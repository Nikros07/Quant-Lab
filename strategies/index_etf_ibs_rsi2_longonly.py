"""Index-ETF-Kurzfrist-Umkehr, long-only: IBS-Kern, Connors-RSI(2) als Variante.

Praktiker-Idee ohne Peer-Review-Beleg (Mechanismus: Liquiditaetsbereitstellung nach Nagel 2012, dort aber
nicht fuer Index-ETFs getestet). Deshalb strikt vorregistriert: alle Parameter stehen hier fest, es wird nichts
optimiert. Quelle der Regeln: research/strategie-kandidaten.json (id index_etf_ibs_rsi2_longonly) und
research/families/reversal.md Abschnitt 3.3.

Regel (Basis, Signale am Schlusskurs von Tag t, nur Daten bis t):

* Instrument je einzeln (NICHT poolen): SPY (ab 1993), QQQ (ab 1999), IWM (ab 2000), auto_adjust-OHLC.
  Der Harness testet SPY (Parameter `ticker`, Standard "SPY"); QQQ und IWM liegen im selben Panel und werden
  mit `ticker="QQQ"` bzw. `"IWM"` einzeln gerechnet, nie zusammen.
* IBS_t = (Close_t - Low_t) / (High_t - Low_t); bei High == Low kein Signal (IBS undefiniert).
* Einstieg, wenn keine Position UND Close_t > SMA200(Close)_t UND IBS_t < 0,20.
  SMA200 schliesst den heutigen Schlusskurs ein (wie ueblich bei Trendfiltern); beide Vergleiche strikt.
* Ausstieg am ersten Tag u > t mit IBS_u > 0,70 ODER u - t >= 5 Handelstage (Haltedauer 5 Tage).
* Nur long, 100 % Eigenkapital je Trade, sonst Cash, kein Hebel, kein Stop.

Zeitachse (Signaltag t, Einstiegssignal; Engine-Konvention "Signal am Schluss von t, Handel danach"):
Die Position besteht von der Ausfuehrung am Tag t+1 bis zur Ausfuehrung am Tag u+1. Der Ausstiegstag u wird
wie die Spezifikation es sagt ab dem Tag NACH dem Einstiegssignal geprueft (u > t), die Mindesthaltedauer
sind also 1 Handelstag. Am Ausstiegssignaltag u gilt die Position noch als gehalten (sie wird erst am Tag
u+1 verkauft), es gibt an diesem Tag also kein neues Einstiegssignal; ein neues Signal ist fruehestens am
Tag u+1 moeglich (Kauf dann am Tag u+2).

Variante "connors_rsi2": Einstieg Close > SMA200 UND Wilder-RSI(2) < 10; Ausstieg am ersten Tag u > t mit
Close_u > SMA5(Close)_u (SMA5 inkl. heute). Wie in der Spezifikation OHNE Zeitstopp (max_hold None).
Variante "no_sma200": wie Basis, aber ohne SMA200-Filter. Der Startzeitpunkt der Strategie bleibt gleich
(erste Zeile erst, wenn 200 Schlusskurse vorliegen), damit alle Laeufe denselben Zeitraum bewerten.

Ausfuehrung: Der Harness handelt standardmaessig zur Eroeffnung t+1 (exec "open"). Die in der Spezifikation
genannte Hauptausfuehrung "Schlusskurs t+1" entspricht `run_all.py --exec close_next`; die Sensitivitaet
"Eroeffnung t+1" ist der Harness-Standard. Beide Ausfuehrungen laufen ueber das Harness-Flag, nicht ueber
`variants` (die Engine kennt die Ausfuehrung nicht pro Variante).

Ausgabeformat: Zielgewicht 0/1 nur fuer das gewaehlte Instrument, als Zeile am ersten gueltigen Tag und an
jedem Tag, an dem sich der Zielzustand aendert (Einstiegs- bzw. Ausstiegssignal). Zwischen den Zeilen driftet
die Position (die Engine rebalanciert nicht jeden Tag, keine Scheinumsaetze). Es gibt nie ein Gewicht auf
einen Tag ohne Kurs; Tage ohne Schlusskurs des Instruments werden uebersprungen.

Kosten: 2 bp je Seite (Spezifikation) ueber SPEC["cost_bps"]; der Stress 5 bp entspricht `--cost-mult 2.5`.
Die Engine verbucht Kosten, Cash-Zins (Fama-French RF statt ^IRX) und Steuer selbst.

Datenhinweis: Das Standard-Panel kennt nur Open/Close. Fuer das IBS braucht die Strategie High/Low; `load()`
liefert deshalb ein OHLCPanel (Unterklasse von Panel mit .high/.low, bleibt bei truncate/slice erhalten).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from qlab.data import Panel, load_ticker

INSTRUMENTS = ["SPY", "QQQ", "IWM"]

SPEC = {
    "id": "index_etf_ibs_rsi2_longonly",
    "name": "Index-ETF-Kurzfrist-Umkehr long-only (IBS-Kern, Connors-RSI(2) als Variante)",
    "family": "reversal",
    "tickers": INSTRUMENTS,
    "start": "1993-01-29",       # SPY-Start; QQQ 1999-03, IWM 2000-05
    "sources": [
        "Nagel 2012, Evaporating Liquidity, https://www.nber.org/papers/w17653",
        "Quantified Strategies, The classical mean reversion strategy (Praktiker-Blog, kein Peer Review), "
        "https://quantifiedstrategies.substack.com/p/the-classical-mean-reversion-strategy",
    ],
    "params": {
        "ticker": "SPY",
        "signal": "ibs",            # "ibs" oder "rsi2"
        "use_sma_filter": True,
        "sma_window": 200,
        "ibs_entry": 0.20,
        "ibs_exit": 0.70,
        "max_hold": 5,              # Handelstage; None = kein Zeitstopp
        "rsi_len": 2,
        "rsi_entry": 10.0,
        "exit_sma": 5,              # nur signal="rsi2": Ausstieg, wenn Close > SMA(exit_sma)
    },
    "variants": {
        "connors_rsi2": {"signal": "rsi2", "max_hold": None},
        "no_sma200": {"use_sma_filter": False},
    },
    "cost_bps": {t: 2.0 for t in INSTRUMENTS},
}


# --------------------------------------------------------------------------------------
# Daten: Panel mit High/Low
# --------------------------------------------------------------------------------------

class OHLCPanel(Panel):
    """Panel mit zusaetzlichen High/Low-Matrizen (gleicher Index und Spalten wie close)."""

    def __init__(self, open_: pd.DataFrame, close: pd.DataFrame, high: pd.DataFrame, low: pd.DataFrame,
                 volume: pd.DataFrame | None = None):
        super().__init__(open_, close, volume)
        self.high = high
        self.low = low

    def truncate(self, end) -> "OHLCPanel":
        end = pd.Timestamp(end)
        return OHLCPanel(self.open.loc[:end], self.close.loc[:end], self.high.loc[:end], self.low.loc[:end],
                         self.volume.loc[:end])

    def slice(self, start=None, end=None) -> "OHLCPanel":
        sl = slice(pd.Timestamp(start) if start else None, pd.Timestamp(end) if end else None)
        return OHLCPanel(self.open.loc[sl], self.close.loc[sl], self.high.loc[sl], self.low.loc[sl],
                         self.volume.loc[sl])


def load() -> OHLCPanel:
    """SPY, QQQ, IWM (auto_adjust-OHLC aus dem Cache) auf der Vereinigung ihrer Handelstage.

    Fehlende Kurse (Titel noch nicht gelistet) bleiben NaN = nicht handelbar; es wird nichts aufgefuellt.
    """
    opens, highs, lows, closes, vols = {}, {}, {}, {}, {}
    for t in INSTRUMENTS:
        df = load_ticker(t, start=SPEC["start"])
        opens[t], highs[t], lows[t], closes[t], vols[t] = df["Open"], df["High"], df["Low"], df["Close"], df["Volume"]
    close = pd.DataFrame(closes).sort_index()
    idx = close.index
    return OHLCPanel(pd.DataFrame(opens).reindex(idx), close, pd.DataFrame(highs).reindex(idx),
                     pd.DataFrame(lows).reindex(idx), pd.DataFrame(vols).reindex(idx))


# --------------------------------------------------------------------------------------
# Indikatoren (alle rein rueckwaertsgerichtet)
# --------------------------------------------------------------------------------------

def _ibs(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """Internal Bar Strength; NaN bei High <= Low (Spanne null) oder fehlenden Daten."""
    rng = high - low
    return ((close - low) / rng.where(rng > 0)).astype(float)


def _wilder_rsi(close: pd.Series, n: int) -> pd.Series:
    """Wilder-RSI(n): Startwert = einfacher Mittelwert der ersten n Aenderungen, danach (avg*(n-1)+x)/n.

    RSI = 100 * avg_gain / (avg_gain + avg_loss); NaN, wenn beide Mittel null sind (keine Bewegung).
    """
    c = close.to_numpy(float)
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return pd.Series(out, index=close.index)
    d = np.diff(c)
    gain, loss = np.maximum(d, 0.0), np.maximum(-d, 0.0)
    ag, al = gain[:n].mean(), loss[:n].mean()
    for k in range(n, len(c)):                 # Aenderung k-1 -> k ist d[k-1]; RSI an Position k
        if k > n:
            ag = (ag * (n - 1) + gain[k - 1]) / n
            al = (al * (n - 1) + loss[k - 1]) / n
        tot = ag + al
        out[k] = 100.0 * ag / tot if tot > 0 else np.nan
    return pd.Series(out, index=close.index)


def _flags(c: pd.Series, h: pd.Series, l: pd.Series, p: dict) -> tuple[np.ndarray, np.ndarray]:
    """Einstiegs- und Ausstiegsbedingung je Tag (bool-Arrays; NaN-Vergleiche zaehlen als False)."""
    if p["use_sma_filter"]:
        trend_ok = (c > c.rolling(p["sma_window"]).mean()).to_numpy(bool)
    else:
        trend_ok = np.ones(len(c), dtype=bool)
    if p["signal"] == "ibs":
        ibs = _ibs(h, l, c)
        entry = trend_ok & (ibs < p["ibs_entry"]).to_numpy(bool)
        exit_ = (ibs > p["ibs_exit"]).to_numpy(bool)
    elif p["signal"] == "rsi2":
        rsi = _wilder_rsi(c, int(p["rsi_len"]))
        entry = trend_ok & (rsi < p["rsi_entry"]).to_numpy(bool)
        exit_ = (c > c.rolling(int(p["exit_sma"])).mean()).to_numpy(bool)
    else:
        raise ValueError(f"unbekanntes signal {p['signal']!r} (erlaubt: 'ibs', 'rsi2')")
    return entry, exit_


def _target_states(entry: np.ndarray, exit_: np.ndarray, start: int, max_hold: int | None) -> np.ndarray:
    """Zielzustand (0/1) am Schluss jedes Tages ab `start`; davor NaN.

    Zustand "long" bedeutet: gehalten bis zur Ausfuehrung des Ausstiegs. Ausstieg am Tag i (> Einstiegssignaltag t0)
    bei Ausstiegsbedingung oder i - t0 >= max_hold; am Ausstiegstag selbst kein neuer Einstieg.
    """
    n = len(entry)
    target = np.full(n, np.nan)
    long_, t0 = False, -1
    for i in range(max(start, 0), n):
        if long_:
            if exit_[i] or (max_hold is not None and i - t0 >= max_hold):
                long_ = False
        elif entry[i]:
            long_, t0 = True, i
        target[i] = 1.0 if long_ else 0.0
    return target


def weights(panel, ticker: str = "SPY", signal: str = "ibs", use_sma_filter: bool = True, sma_window: int = 200,
            ibs_entry: float = 0.20, ibs_exit: float = 0.70, max_hold: int | None = 5, rsi_len: int = 2,
            rsi_entry: float = 10.0, exit_sma: int = 5) -> pd.DataFrame:
    """Zielgewichte (0/1) fuer `ticker`; nur Zeilen am ersten gueltigen Tag und an Zustandswechseln."""
    for attr in ("high", "low"):
        if getattr(panel, attr, None) is None:
            raise ValueError("Panel ohne High/Low: index_etf_ibs_rsi2_longonly braucht ein OHLCPanel (load())")
    if ticker not in panel.close.columns:
        raise KeyError(f"{ticker} nicht im Panel (vorhanden: {list(panel.close.columns)})")
    p = dict(ticker=ticker, signal=signal, use_sma_filter=use_sma_filter, sma_window=int(sma_window),
             ibs_entry=ibs_entry, ibs_exit=ibs_exit, max_hold=max_hold, rsi_len=rsi_len, rsi_entry=rsi_entry,
             exit_sma=exit_sma)

    c = panel.close[ticker].dropna()                    # nur Tage mit Kurs des Instruments
    h = panel.high[ticker].reindex(c.index)
    l = panel.low[ticker].reindex(c.index)
    empty = pd.DataFrame(columns=[ticker], dtype=float)
    if len(c) < p["sma_window"]:
        return empty

    entry, exit_ = _flags(c, h, l, p)
    target = _target_states(entry, exit_, start=p["sma_window"] - 1, max_hold=max_hold)
    valid = ~np.isnan(target)
    if not valid.any():
        return empty
    prev = np.r_[np.nan, target[:-1]]
    rows = valid & ((np.isnan(prev)) | (target != prev))      # erster gueltiger Tag + Zustandswechsel
    return pd.DataFrame({ticker: target[rows]}, index=c.index[rows])
