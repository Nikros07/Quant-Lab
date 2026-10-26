"""Binärer Trendfilter US-Aktien / Cash MA(1,12) mit Hysterese-Band 1 % — Live-Test auf SPY (H8).

Hypothese H8 (docs/HYPOTHESEN.md, Eintrag H7–H10): Basis ist `trend_ma12_us_equity_cash_etf`
(SPY, Signal ^GSPC, Monats-MA12, 10 bp je Wechsel, Ausführung Eröffnung t+1, Cash = US-RF).
Neu ist nur eine Hysterese um den Monats-MA12:

    P_m   = Schlusskurs des S&P-500-PREISINDEX (^GSPC) am letzten Handelstag jedes Monats m.
    MA12  = Mittel der letzten 12 Monatsend-Schlusskurse inkl. t.
    Zustand LONG/FLAT, geändert nur an kausal erkannten Monatsenden mit gültigem MA12:
      * erster Zustand: LONG, wenn P_t >= MA12_t, sonst FLAT (wie Basis);
      * aus FLAT nur LONG, wenn P_t >= MA12_t * (1 + band);
      * aus LONG nur FLAT, wenn P_t <  MA12_t * (1 - band);
      * sonst Zustand halten.
    Zeilengewicht = 1.0 auf SPY (LONG) bzw. 0.0 (FLAT); Rest Cash. Kein Hebel, kein Short.

Umsetzung im Engine-Vertrag:
* Signal am Schluss des letzten Handelstags t eines Monats (month_end_flags, kausal); die Engine handelt
  zur Eröffnung von t+1. Die Zustandsmaschine läuft nur über Monate mit gültigem MA12 (Warmup-Monate
  ohne Zustand); Zeilen werden nur ausgegeben, wenn der SPY-Kurs an dem Monatsende gültig ist.
* Das Signal ist der Preisindex ^GSPC, das Handelsinstrument der SPY. Panel ab 1990, damit 12
  Monatsenden Signal-Historie vor dem SPY-Start (1993-01-29) vorliegen.
* Kosten 10 bp je Wechsel über SPEC["cost_bps"]; Cash verzinst die Engine mit dem French-RF.

Parameter (genau ein Wert, keine Varianten): band = 0.01. Bei band = 0.0 entspricht das Modul exakt
der Basis `trend_ma12_us_equity_cash_etf` (Zielgewichte identisch).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from qlab.calendar import month_end_flags

ASSET = "SPY"
SIGNAL = "^GSPC"

SPEC = {
    "id": "trend_ma12_band_etf",
    "name": "Trendfilter US-Aktien/Cash MA(1,12) mit 1-%-Hysterese-Band, Test auf SPY",
    "family": "macro",
    "tickers": [ASSET, SIGNAL],
    "start": "1990-01-01",           # ^GSPC-Vorlauf für 12 Monatsenden; SPY selbst startet 1993-01-29
    "sources": [
        "Faber 2007, A Quantitative Approach to Tactical Asset Allocation, SSRN 962461",
        "Neely, Rapach, Tu, Zhou 2014, Forecasting the Equity Risk Premium: The Role of Technical Indicators, "
        "https://files.stlouisfed.org/files/htdocs/wp/2010/2010-008.pdf",
    ],
    "params": {"signal": SIGNAL, "asset": ASSET, "ma_long": 12, "band": 0.01},
    "variants": {},                  # H8: genau ein Band (1 %), keine Varianten
    "cost_bps": {ASSET: 10.0},
}


def weights(panel, signal: str = SIGNAL, asset: str = ASSET, ma_long: int = 12,
            band: float = 0.01) -> pd.DataFrame:
    """Zielgewichte (0 oder 1) auf `asset` an jedem Monatsende mit gültigem MA12; Rest ist Cash.

    Zustandsmaschine mit Hysterese `band` (Anteil, z. B. 0.01 = 1 %) um den Monats-MA12.
    """
    if not 0.0 <= band < 1.0:
        raise ValueError(f"band muss in [0, 1) liegen, ist {band}")
    idx = panel.close.index
    flags = month_end_flags(idx).to_numpy()
    # begrenztes Vorwärtsfüllen (kausal): Monatsende ohne eigenen Kurs nimmt den letzten Schluss der Vorwoche
    sig_px = panel.close[signal].ffill(limit=5)
    me = sig_px[flags]                                       # nur kausal erkannte Monatsenden
    slow = me.rolling(ma_long).mean()                        # inkl. aktuellem Monatsende
    upper = 1.0 + band
    lower = 1.0 - band

    states = np.full(len(me), np.nan)
    state = None                                             # None = noch kein gültiger MA12
    for i, (px, ma) in enumerate(zip(me.to_numpy(float), slow.to_numpy(float))):
        if not np.isfinite(ma):                              # Warmup: noch kein gültiger MA12
            continue
        if state is None:
            state = 1.0 if px >= ma else 0.0                 # erster Zustand wie Basis (>=)
        elif state == 0.0 and px >= ma * upper:              # aus FLAT: Einstieg erst oberhalb Band
            state = 1.0
        elif state == 1.0 and px < ma * lower:               # aus LONG: Ausstieg erst unterhalb Band
            state = 0.0
        states[i] = state

    on = pd.Series(states, index=me.index)
    valid = on.notna() & panel.close[asset][flags].notna()
    return pd.DataFrame({asset: on.astype(float)}, index=me.index)[valid]
