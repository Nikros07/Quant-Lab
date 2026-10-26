"""Backtest-Engine (tagesbasiert, ereignisgetrieben über Zielgewichte).

Vertrag mit den Strategien
--------------------------
Eine Strategie liefert `target`: DataFrame (Index = Handelstage, Spalten = Ticker) mit
Zielgewichten, **berechnet nur aus Daten bis einschließlich des Schlusskurses dieses Tages**.
* Eine Zeile mit mindestens einem Wert = Rebalancing-Signal (NaN innerhalb der Zeile = 0).
* Eine komplett leere Zeile (alles NaN) / fehlende Zeile = nichts tun, Positionen driften.

Ausführung (exec_mode)
----------------------
* "open"       (Standard): Signal am Schluss von t, Handel zur Eröffnung von t+1.
* "close_next" : Handel zum Schluss von t+1 (konservativ).
* "close"      : Handel zum Schluss von t selbst (optimistisch; nur für Vergleiche).

Kosten: `bps` pro Seite auf das gehandelte Volumen (Spread+Gebühr+Slippage), Cash wird mit
dem Fama-French-RF verzinst, Kredit kostet RF + Spread, Leerverkäufe eine Leihgebühr.
Steuern sind hier NICHT enthalten (siehe qlab/tax.py).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .data import Panel, risk_free_daily

TRADING_DAYS = 252


@dataclass
class CostModel:
    default_bps: float = 5.0                 # pro Seite, Standard-ETF
    per_ticker_bps: dict = field(default_factory=dict)
    short_fee_annual: float = 0.005          # Leihgebühr auf Short-Volumen
    lever_spread_annual: float = 0.015       # Aufschlag auf RF bei negativem Cash

    def bps(self, ticker: str) -> float:
        return self.per_ticker_bps.get(ticker, self.default_bps)


# Teilfreistellung (InvStG) für UCITS-Äquivalente: Aktienfonds 30 %, Immobilien 60 %, sonst 0 %.
EQUITY_TF = 0.30
_BOND_GOLD_CRYPTO = {"IEF", "TLT", "SHY", "LQD", "HYG", "AGG", "BIL", "BND", "TIP", "GLD", "IAU", "DBC", "GSG",
                     "SLV", "USO", "UNG", "GC=F", "CL=F", "BTC-USD", "ETH-USD", "VXX", "SVXY", "UVXY", "^VIX"}


def default_teilfreistellung(ticker: str) -> float:
    if ticker in _BOND_GOLD_CRYPTO:
        return 0.0
    if ticker in ("VNQ", "VNQI", "IYR", "RWX"):
        return 0.60
    return EQUITY_TF


@dataclass
class TaxModel:
    """Vereinfachte deutsche Abgeltungsteuer auf realisierte Gewinne (thesaurierende ETFs).

    * 26,375 % (25 % + Soli), auf den um die Teilfreistellung gekürzten Gewinn.
    * Einstandspreis nach Durchschnittskosten (statt FIFO), Verlustverrechnung im selben Topf
      mit Vortrag, Zahlung zum Jahreswechsel aus Cash.
    * Ohne Sparer-Pauschbetrag und Vorabpauschale (konservativ bzw. vernachlässigbar bei kleinen Beträgen).
    * Unrealisierte Gewinne am Ende bleiben unversteuert; `BacktestResult.tax_if_liquidated`
      gibt die Steuer bei Verkauf zum Schluss an.
    """
    rate: float = 0.26375
    tf_map: dict = field(default_factory=dict)

    def tf(self, ticker: str) -> float:
        return self.tf_map.get(ticker, default_teilfreistellung(ticker))


@dataclass
class BacktestResult:
    nav: pd.Series
    ret: pd.Series
    weights: pd.DataFrame        # Gewichte am Tagesende (Positionswert / NAV)
    turnover: pd.Series          # einseitig, Anteil am NAV pro Tag
    cost: pd.Series              # Kosten als Anteil am NAV pro Tag
    rf: pd.Series
    n_trades: int
    skipped_orders: int
    taxes_paid: pd.Series | None = None      # gezahlte Steuer als Geld, am Zahltag
    tax_if_liquidated: float = 0.0           # Steuer auf unrealisierte Gewinne bei Verkauf zum Schluss (Anteil am End-NAV)

    @property
    def gross_exposure(self) -> pd.Series:
        return self.weights.abs().sum(axis=1)

    def ret_after_liquidation_tax(self) -> pd.Series:
        """Renditen, bei denen am letzten Tag die Steuer auf alle unrealisierten Gewinne abgezogen wird
        (fairer Vergleich zwischen Buy&Hold, das Steuern aufschiebt, und aktiven Strategien)."""
        r = self.ret.copy()
        if self.tax_if_liquidated > 0 and len(self.nav) > 1:
            last, prev = self.nav.iloc[-1], self.nav.iloc[-2]
            if prev > 0:
                r.iloc[-1] = (last - self.tax_if_liquidated) / prev - 1.0
        return r


def _normalise_target(target: pd.DataFrame, tickers: list[str], index: pd.DatetimeIndex) -> pd.DataFrame:
    if target is None or len(target) == 0:
        return pd.DataFrame(columns=tickers, dtype=float)
    unknown = [c for c in target.columns if c not in tickers]
    if unknown:
        raise KeyError(f"Strategie nutzt Ticker ohne Daten: {unknown}")
    t = target.reindex(columns=tickers)
    t = t[t.index.isin(index)]
    t = t.dropna(how="all")
    return t.fillna(0.0)


def _book_trades(pos, basis, trade, fees, tf) -> float:
    """Aktualisiert Einstandswerte (in place); gibt das steuerpflichtige realisierte Ergebnis zurück.

    Durchschnittskostenmethode, vorzeichenrichtig für Long und Short:
    realisiert wird der geschlossene Anteil f der alten Position: f * (Wert - Einstand) - Gebühr,
    gekürzt um die Teilfreistellung. Ein Drehen der Position baut den Rest mit neuem Einstand auf.
    """
    taxable = 0.0
    for j in np.flatnonzero(np.abs(trade) > 1e-15):
        p0, t, fee = pos[j], trade[j], fees[j]
        if abs(p0) < 1e-15 or p0 * t > 0:                      # Aufbau / Aufstockung
            basis[j] += t + np.sign(t) * fee
        else:                                                   # Verkleinern, Schließen, Drehen
            f = min(1.0, abs(t) / abs(p0))
            taxable += (f * (p0 - basis[j]) - fee) * (1.0 - tf[j])
            basis[j] *= (1.0 - f)
            rest = t + f * p0                                   # in Gegenrichtung neu aufgebauter Teil
            if abs(rest) > 1e-15 and f >= 1.0 - 1e-12:
                basis[j] += rest
    return taxable


def run_backtest(panel: Panel, target: pd.DataFrame, cost: CostModel | None = None,
                 exec_mode: str = "open", rf: pd.Series | None = None,
                 start: str | None = None, end: str | None = None,
                 tax: TaxModel | None = None) -> BacktestResult:
    if exec_mode not in ("open", "close_next", "close"):
        raise ValueError(exec_mode)
    cost = cost or CostModel()
    if start or end:
        panel = panel.slice(start, end)
    idx = panel.close.index
    tickers = panel.tickers
    n, m = len(idx), len(tickers)
    if n < 3:
        raise ValueError("zu wenige Handelstage")

    op = panel.open.to_numpy(float)
    cl = panel.close.to_numpy(float)
    if rf is None:
        rf = risk_free_daily(idx)
    rf = rf.reindex(idx).ffill().fillna(0.0).to_numpy(float)
    bps = np.array([cost.bps(t) for t in tickers]) / 1e4

    tgt = _normalise_target(target, tickers, idx)
    tgt_arr = {d: row.to_numpy(float) for d, row in tgt.iterrows()}
    day_pos = {d: i for i, d in enumerate(idx)}

    pos = np.zeros(m)           # Positionswerte in Geldeinheiten
    cash = 1.0
    pending: np.ndarray | None = None
    nav_hist = np.empty(n)
    w_hist = np.zeros((n, m))
    turn_hist = np.zeros(n)
    cost_hist = np.zeros(n)
    n_trades = 0
    skipped = 0
    basis = np.zeros(m)         # Einstandswert je Titel (Durchschnittskosten), nur wenn tax aktiv
    tf = np.array([tax.tf(t) for t in tickers]) if tax else np.zeros(m)
    realized_ytd = 0.0          # Summe steuerpflichtiger (nach TF) realisierter Ergebnisse im Jahr
    loss_carry = 0.0
    tax_paid = np.zeros(n)
    short_fee_d = cost.short_fee_annual / TRADING_DAYS
    lever_d = cost.lever_spread_annual / TRADING_DAYS

    def rebalance(price: np.ndarray, desired: np.ndarray, i: int) -> bool:
        """Auf Zielgewichte handeln, nur Titel mit gültigem Kurs. True, wenn alles ausgeführt."""
        nonlocal cash, n_trades, skipped, realized_ytd
        nav = cash + pos.sum()
        ok = np.isfinite(price)
        want = desired * nav
        trade = np.where(ok, want - pos, 0.0)
        blocked = (~ok) & (np.abs(desired) > 0) & (np.abs(want - pos) > 1e-12)
        if blocked.any():
            skipped += int(blocked.sum())
        vol = np.abs(trade)
        c = float((vol * bps).sum())
        if tax is not None:
            realized_ytd += _book_trades(pos, basis, trade, vol * bps, tf)
        pos[:] = pos + trade
        cash = cash - trade.sum() - c
        n_trades += int((vol > 1e-12).sum())
        turn_hist[i] += vol.sum() / 2.0 / max(nav, 1e-12)
        cost_hist[i] += c / max(nav, 1e-12)
        return not blocked.any()

    for i in range(n):
        # 1) Über Nacht: close[i-1] -> open[i]; Cash-Zins/Finanzierung einmal pro Tag
        if i > 0:
            f = np.where(np.isfinite(op[i]) & np.isfinite(cl[i - 1]) & (cl[i - 1] > 0), op[i] / cl[i - 1], 1.0)
            pos *= f
        gross_short = float(np.abs(np.minimum(pos, 0.0)).sum())
        if cash >= 0:
            cash *= 1.0 + rf[i]
        else:
            cash *= 1.0 + rf[i] + lever_d
        cash -= gross_short * short_fee_d

        # 2) Handel zur Eröffnung (Signal von gestern)
        if exec_mode == "open" and pending is not None:
            if rebalance(op[i], pending, i):
                pending = None

        # 3) Tagsüber: open[i] -> close[i]
        f = np.where(np.isfinite(op[i]) & np.isfinite(cl[i]) & (op[i] > 0), cl[i] / op[i], 1.0)
        pos *= f

        # 4) Handel zum Schluss
        if exec_mode == "close_next" and pending is not None:
            if rebalance(cl[i], pending, i):
                pending = None
        d = idx[i]
        if d in tgt_arr:
            if exec_mode == "close":
                rebalance(cl[i], tgt_arr[d], i)
            else:
                pending = tgt_arr[d]   # neues Signal überschreibt ein noch offenes

        if tax is not None and i < n - 1 and idx[i + 1].year != idx[i].year:
            total = realized_ytd + loss_carry
            if total > 0:
                due = tax.rate * total
                cash -= due
                tax_paid[i] = due
                loss_carry = 0.0
            else:
                loss_carry = total
            realized_ytd = 0.0

        nav = cash + pos.sum()
        nav_hist[i] = nav
        if nav > 0:
            w_hist[i] = pos / nav
        else:
            nav_hist[i:] = max(nav, 0.0)
            break

    nav_s = pd.Series(nav_hist, index=idx, name="nav")
    ret = nav_s.pct_change().fillna(nav_s.iloc[0] - 1.0)
    tax_liq = 0.0
    if tax is not None:
        unreal = float(((pos - basis) * (1.0 - tf)).sum())
        tax_liq = tax.rate * max(realized_ytd + loss_carry + unreal, 0.0)
    return BacktestResult(
        nav=nav_s, ret=ret,
        weights=pd.DataFrame(w_hist, index=idx, columns=tickers),
        turnover=pd.Series(turn_hist, index=idx), cost=pd.Series(cost_hist, index=idx),
        rf=pd.Series(rf, index=idx), n_trades=n_trades, skipped_orders=skipped,
        taxes_paid=pd.Series(tax_paid, index=idx) if tax is not None else None, tax_if_liquidated=tax_liq,
    )


# --------------------------------------------------------------------------------------
# Kausalitätstest: Gewichte bis Tag t dürfen nicht von Daten nach t abhängen.
# --------------------------------------------------------------------------------------

def check_causality(weights_fn, panel: Panel, cuts: list | None = None, n_cuts: int = 5,
                    tol: float = 1e-9) -> list[str]:
    """Gibt eine Liste von Verstößen zurück (leer = bestanden).

    Vergleicht die Strategie auf den vollen Daten mit der Strategie auf bei `cut` abgeschnittenen
    Daten. Für alle Tage <= cut müssen die Zielgewichte identisch sein (inkl. welche Zeilen
    überhaupt ein Signal enthalten).
    """
    full = weights_fn(panel)
    idx = panel.close.index
    if cuts is None:
        lo, hi = int(len(idx) * 0.3), int(len(idx) * 0.95)
        cuts = [idx[int(x)] for x in np.linspace(lo, hi, n_cuts)]
    problems: list[str] = []
    full_n = full.dropna(how="all")
    for cut in cuts:
        part = weights_fn(panel.truncate(cut)).dropna(how="all")
        a = full_n.loc[:cut]
        b = part.loc[:cut]
        if list(a.index) != list(b.index):
            only_a = a.index.difference(b.index)
            only_b = b.index.difference(a.index)
            problems.append(f"{pd.Timestamp(cut).date()}: Signaltage verschieden (nur voll: {len(only_a)}, nur abgeschnitten: {len(only_b)})")
            continue
        cols = sorted(set(a.columns) | set(b.columns))
        diff = (a.reindex(columns=cols).fillna(0.0) - b.reindex(columns=cols).fillna(0.0)).abs()
        if len(diff) and float(diff.to_numpy().max()) > tol:
            when = diff.max(axis=1).idxmax()
            problems.append(f"{pd.Timestamp(cut).date()}: Gewichte bei {pd.Timestamp(when).date()} hängen von späteren Daten ab (max Abw. {float(diff.to_numpy().max()):.3g})")
    return problems
