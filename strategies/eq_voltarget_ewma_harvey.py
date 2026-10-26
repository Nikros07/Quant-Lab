"""Vol-Targeting auf den US-Aktienmarkt (EWMA-Volatilität, Harvey et al. 2018) — Langzeit-Test auf Ken-French-Gesamtmarkt.

Quellen: Harvey, Hoyle, Korgaonkar, Rattray, Sargaison, Van Hemert 2018, "The Impact of Volatility Targeting",
Journal of Portfolio Management 45(1) (Duke-PDF P135); Cederburg, O'Doherty, Wang, Yan 2020, "On the performance
of volatility-managed portfolios", JFE 138(1). Regeln aus research/families/volmgmt.md, Abschnitt 3.1.

Regel (festgelegt vor dem Backtest, Parameter aus der Quelle, keine Optimierung):
    r[t]   = Tages-Totalrendite des US-Gesamtmarkts (French: Mkt-RF + RF).
    lam    = 0.5 ** (1 / HL)                           HL = 20 Handelstage (Harvey-Hauptfall)
    v[WARMUP-1] = mean(r[0:WARMUP]**2)                 WARMUP = 270 Handelstage, Null-Mittelwert (Harvey Fn. 8)
    v[t]   = lam * v[t-1] + (1 - lam) * r[t]**2
    sig[t] = sqrt(252 * v[t])                          annualisierte Vol-Prognose, nur Daten <= t
    target = min(CAP, TARGET / sig[t])                 TARGET = 12 % p.a., CAP = 1.0 (kein Hebel)
    pos    = target, falls |target - pos_alt| >= BAND  (BAND = 5 Prozentpunkte, Lab-Ergänzung), sonst pos_alt
Der Rest des Portfolios ist Cash (verzinst die Engine mit dem French-RF).

Umsetzung im Engine-Vertrag:
* Das Panel (`load()`) enthält eine Spalte "MKT" = US-Gesamtmarkt als Total-Return-Reihe aus Ken French
  (Mkt-RF + RF, täglich) über `panel_from_returns` (open == close). Ein Signal am Schluss von Tag t wird
  damit zum Schlusskurs von t+1 gehandelt und verdient ab t+2 — exakt die Spezifikation (Signal Schluss s-2,
  Order Schluss s-1, Position s verdient r[s]).
* Die Tagesrendite wird aus der Kursreihe zurückgerechnet (close / close.shift(1) - 1). Das erste Datum
  (1926-07-01) hat dadurch keine Rendite und fällt aus dem Warmup — Wirkung vernachlässigbar.
* Zeilen werden nur an Tagen ausgegeben, an denen das 5-pp-Band verletzt wird (= Handelssignal); an allen
  anderen Tagen bleibt die Zeile weg (Engine: nichts tun). Das Band wird auf die nominelle Position
  verglichen. Zwischen zwei Signalen driftet die Engine-Position mit den Kursen; die Spezifikation rechnet
  dagegen mit konstantem Anteil (pos * (r - rf) + rf). Das ist eine bekannte, bewusst akzeptierte Näherung.
* Fehlende Kurse (NaN) = nicht handelbar: an solchen Tagen wird kein Signal ausgegeben, eine fehlende Rendite
  geht nicht in die Varianz ein (der Schätzer wird einfach nicht fortgeschrieben).
* Erstes Signal: ab 1928-01-01 (Spezifikation: "Test ab 1928"); die Varianz läuft schon vorher aus der
  Warmup-Phase (270 Handelstage ab 1926-07-01, also vor 1928).

Kosten: 2 bp je Seite laut Spezifikation (statt 5 bp Engine-Standard) über SPEC["cost_bps"]. Stresstest über
`--cost-mult` im Harness. Steuern und Cash-Zins verbucht die Engine.

Varianten (vorab festgelegt, Robustheits-Checks, keine Auswahl der besten):
    cap_1_5  CAP 1.5 (Hebel; die Engine finanziert mit RF + 1.5 % statt der RF + 0.5 % der Spezifikation)
    hl_40    Halbwertszeit 40 Tage statt 20
    vol_10   Vol-Ziel 10 % statt 12 %
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from qlab.data import Panel, french, panel_from_returns

ASSET = "MKT"
FIRST_SIGNAL = "1928-01-01"          # Spezifikation: "Test ab 1928" (French-Daten ab 1926-07, Warmup davor)
TRADING_DAYS = 252

SPEC = {
    "id": "eq_voltarget_ewma_harvey",
    "name": "Vol-Targeting US-Aktienmarkt (EWMA HL 20, Ziel 12 %, ohne Hebel), Langzeit auf French-Gesamtmarkt",
    "family": "volmgmt",
    "tickers": [ASSET],              # Spalte des Panels aus load(); keine Yahoo-Ticker
    "start": FIRST_SIGNAL,
    "sources": [
        "Harvey, Hoyle, Korgaonkar, Rattray, Sargaison, Van Hemert 2018, The Impact of Volatility Targeting, "
        "https://people.duke.edu/~charvey/Research/Published_Papers/P135_The_impact_of.pdf",
        "Cederburg, O'Doherty, Wang, Yan 2020, On the performance of volatility-managed portfolios, "
        "https://www.lehigh.edu/~xuy219/research/COWY.pdf",
    ],
    "params": {"asset": ASSET, "target_vol": 0.12, "halflife": 20, "cap": 1.0, "band": 0.05, "warmup": 270,
               "first_signal": FIRST_SIGNAL},
    "variants": {
        "cap_1_5": {"cap": 1.5},
        "hl_40": {"halflife": 40},
        "vol_10": {"target_vol": 0.10},
    },
    "cost_bps": {ASSET: 2.0},
}


# --------------------------------------------------------------------------------------
# Daten
# --------------------------------------------------------------------------------------

def load() -> Panel:
    """Langzeit-Panel: French-Gesamtmarkt (Mkt-RF + RF) ab 1926-07 als Total-Return-Kurs, ungekürzt (der Harness schneidet ab)."""
    fdf = french("F-F_Research_Data_Factors", daily=True)
    mret = (fdf["Mkt-RF"] + fdf["RF"]).astype(float)
    return panel_from_returns(pd.DataFrame({ASSET: mret}))


# --------------------------------------------------------------------------------------
# Kern (wird vom ETF-Modul wiederverwendet)
# --------------------------------------------------------------------------------------

def ewma_sigma(r: np.ndarray, halflife: float, warmup: int) -> np.ndarray:
    """Annualisierte EWMA-Vol (Null-Mittelwert) je Tag; NaN, solange weniger als `warmup` gültige Renditen vorliegen.

    Rein vorwärts gerechnet: sig[t] hängt nur von gültigen Renditen bis einschließlich t ab. Tage mit NaN-Rendite
    bekommen NaN und schreiben den Schätzer nicht fort.
    """
    lam = 0.5 ** (1.0 / halflife)
    out = np.full(len(r), np.nan)
    ok = np.flatnonzero(np.isfinite(r))
    if len(ok) < warmup:
        return out
    sq = r[ok] ** 2
    v = float(sq[:warmup].mean())                       # v[WARMUP-1] = mean(r[0:WARMUP]**2)
    out[ok[warmup - 1]] = np.sqrt(TRADING_DAYS * v)
    for k in range(warmup, len(ok)):
        v = lam * v + (1.0 - lam) * sq[k]
        out[ok[k]] = np.sqrt(TRADING_DAYS * v)
    return out


def vol_target_weights(close: pd.Series, asset: str, target_vol: float = 0.12, halflife: float = 20,
                       cap: float = 1.0, band: float = 0.05, warmup: int = 270,
                       first_signal: str | None = None) -> pd.DataFrame:
    """Zielgewichte auf `asset` (Rest Cash), nur an Tagen mit Band-Verletzung; Index = Signaltage (Schluss t)."""
    idx = close.index
    px = close.to_numpy(float)
    r = np.full(len(px), np.nan)
    if len(px) > 1:
        prev = px[:-1]
        with np.errstate(divide="ignore", invalid="ignore"):
            r[1:] = np.where(np.isfinite(px[1:]) & np.isfinite(prev) & (prev > 0), px[1:] / prev - 1.0, np.nan)
    sig = ewma_sigma(r, halflife, warmup)

    start_i = 0 if first_signal is None else int(idx.searchsorted(pd.Timestamp(first_signal)))
    pos = 0.0                                           # nominelle Position (Start: Cash)
    dates, vals = [], []
    for i in range(start_i, len(px)):
        s = sig[i]
        if not (np.isfinite(s) and np.isfinite(px[i])):
            continue                                    # kein Signal ohne Vol-Schätzung oder ohne handelbaren Kurs
        tgt = cap if s <= 1e-12 else min(cap, target_vol / s)
        if abs(tgt - pos) >= band:
            pos = tgt
            dates.append(idx[i])
            vals.append(tgt)
    return pd.DataFrame({asset: np.asarray(vals, dtype=float)}, index=pd.DatetimeIndex(dates))


# --------------------------------------------------------------------------------------
# Strategie
# --------------------------------------------------------------------------------------

def weights(panel, asset: str = ASSET, target_vol: float = 0.12, halflife: float = 20, cap: float = 1.0,
            band: float = 0.05, warmup: int = 270, first_signal: str | None = FIRST_SIGNAL) -> pd.DataFrame:
    """Zielgewichte (0 < w <= cap) auf `asset` an Tagen, an denen das No-Trade-Band verletzt wird; Rest ist Cash."""
    return vol_target_weights(panel.close[asset], asset, target_vol=target_vol, halflife=halflife, cap=cap,
                              band=band, warmup=warmup, first_signal=first_signal)
