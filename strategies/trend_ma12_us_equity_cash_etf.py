"""Binärer Trendfilter US-Aktien / Cash MA(1,12) — Live-Test auf dem investierbaren ETF SPY (ab 1993-01-29).

Zweites Modul zu `trend_ma12_us_equity_cash` (Langzeit-Test auf French-Gesamtmarkt): gleiche Regel,
aber gehandelt wird der SPY (Yahoo, angepasst = Total Return) statt der French-Reihe.

Regel (festgelegt vor dem Backtest, aus research/families/macro.md, Abschnitt 3.1):
    P_m  = Schlusskurs des S&P-500-PREISINDEX (^GSPC) am letzten Handelstag jedes Monats m.
    MA12 = Mittel der letzten 12 Monatsend-Schlusskurse inkl. t.
    S_t  = 1, wenn P_t >= MA12_t (Neely MA(1,12)), sonst 0.
    Position = S_t * 100 % SPY + (1 - S_t) * 100 % Cash. Kein Hebel, kein Short.

Umsetzung im Engine-Vertrag:
* Signal am Schluss des letzten Handelstags t eines Monats (month_end_flags, kausal); die Engine handelt
  zur Eröffnung von t+1 (Standard-Ausführung). Das ist eine Spur konservativer/anders als "Schluss t+1"
  der Spezifikation, aber derselbe Vertrag wie bei allen ETF-Strategien im Lab.
* Das Signal bleibt auch hier der Preisindex ^GSPC (nicht der SPY), so wie im Paper; der SPY ist nur das
  Handelsinstrument. Das Panel beginnt 1990, damit 12 Monatsenden Signal-Historie vor dem SPY-Start
  (1993-01-29) vorliegen. Vor der SPY-Notierung wird kein Gewicht vergeben.
* Cash verzinst die Engine mit dem French-RF. Kosten 10 bp je Wechsel (Spec) über SPEC["cost_bps"].

Varianten (vorab festgelegt, Robustheits-Checks, keine Auswahl der besten):
    sma10      P_t > Mittel der letzten 10 Monatsenden (Fabers S&P-Teil, strikt größer)
    ma2_12     Mittel(P_t, P_t-1) >= MA12  (Neely MA(2,12))
    signal_tr  gleiche Regel, aber das Signal kommt aus dem Total-Return-Verlauf des SPY (angepasster
               Kurs) statt aus dem Preisindex; erstes Signal daher erst nach 12 SPY-Monatsenden (Ende 1993)
"""
from __future__ import annotations

import pandas as pd

from qlab.calendar import month_end_flags

ASSET = "SPY"
SIGNAL = "^GSPC"

SPEC = {
    "id": "trend_ma12_us_equity_cash_etf",
    "name": "Trendfilter US-Aktien/Cash MA(1,12), Live-Test auf SPY",
    "family": "macro",
    "tickers": [ASSET, SIGNAL],
    "start": "1990-01-01",           # ^GSPC-Vorlauf für 12 Monatsenden; SPY selbst startet 1993-01-29
    "sources": [
        "Neely, Rapach, Tu, Zhou 2014, Forecasting the Equity Risk Premium: The Role of Technical Indicators, "
        "https://files.stlouisfed.org/files/htdocs/wp/2010/2010-008.pdf",
        "Faber 2007, A Quantitative Approach to Tactical Asset Allocation, SSRN 962461",
        "Goyal, Welch, Zafirov 2023, Equity Premium Prediction",
    ],
    "params": {"signal": SIGNAL, "asset": ASSET, "ma_short": 1, "ma_long": 12, "strict": False},
    "variants": {
        "sma10": {"ma_long": 10, "strict": True},
        "ma2_12": {"ma_short": 2},
        "signal_tr": {"signal": ASSET},
    },
    "cost_bps": {ASSET: 10.0},
}


def weights(panel, signal: str = SIGNAL, asset: str = ASSET, ma_short: int = 1, ma_long: int = 12,
            strict: bool = False) -> pd.DataFrame:
    """Zielgewichte (0 oder 1) auf `asset` an jedem Monatsende mit gültigem Signal; Rest ist Cash."""
    idx = panel.close.index
    flags = month_end_flags(idx).to_numpy()
    # begrenztes Vorwärtsfüllen (kausal): Monatsende ohne eigenen Kurs nimmt den letzten Schluss der Vorwoche
    sig_px = panel.close[signal].ffill(limit=5)
    me = sig_px[flags]                                       # nur kausal erkannte Monatsenden
    fast = me.rolling(ma_short).mean()                       # inkl. aktuellem Monatsende
    slow = me.rolling(ma_long).mean()
    on = (fast > slow) if strict else (fast >= slow)
    valid = fast.notna() & slow.notna() & panel.close[asset][flags].notna()
    return pd.DataFrame({asset: on.astype(float)}, index=me.index)[valid]
