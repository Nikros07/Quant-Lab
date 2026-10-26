"""Anleihe als Cash-Ersatz mit eigenem Filter auf Basis von trend_ma12_us_equity_cash_etf (H7).

Regel (vorab festgelegt, docs/HYPOTHESEN.md, Eintrag H7–H10; kein Parameter-Tuning):
    S_t  = Monats-Signal wie in der Basis: P_t (^GSPC-Preisindex am Monatsende) >= Mittel der letzten
           12 Monatsend-Schlusskurse inkl. t (MA(1,12)).
    S_t = LONG -> 100 % SPY, 0 % Anleihe.
    S_t = FLAT -> 100 % Anleihe B, wenn B_t (angepasster Monatsschluss von B) >= Mittel der letzten
                  12 Monatsend-Schlusskurse von B inkl. t; sonst alles 0 (Cash).
    Ist der Anleihe-Kurs am Entscheidungstag NaN oder hat B keine 12 Monatsenden Vorgeschichte
    (lückenlose Monatsenden), gilt Cash (Gewicht 0). Kein ffill auf dem Anleihe-Kurs.
    Zeilen nur, wenn Signal und SPY-Kurs gültig sind (wie in der Basis).

Umsetzung im Engine-Vertrag:
* Signal am Schluss des letzten Handelstags t eines Monats (month_end_flags, kausal); Handel zur
  Eröffnung von t+1. Cash verzinst die Engine mit dem French-RF. Kosten 10 bp je Wechsel.
* Das Panel beginnt 1990, damit Signal- und Anleihen-Historie (12 Monatsenden) vor dem Start der
  Handelsinstrumente liegt. Vor der Notierung eines Titels wird kein Gewicht vergeben.

Varianten (vorab festgelegt, zählen als Versuche, keine Auswahl der besten):
    ief      B = IEF (statt VUSTX), Fenster ab 2002/2003 durch die Datenlage
    uncond   bond_filter=False: B = VUSTX immer, wenn FLAT (nur mit gültigem Kurs), ohne eigenen Filter

Quellen: Faber 2007 (SSRN 962461); Antonacci 2014, Dual Momentum Investing (Anleihen als sicheres Bein);
Neely, Rapach, Tu, Zhou 2014 (MA-Regel, Basis-Signal).
"""
from __future__ import annotations

import pandas as pd

from qlab.calendar import month_end_flags

ASSET = "SPY"
SIGNAL = "^GSPC"
BOND = "VUSTX"
BOND_MA_LONG = 12          # Anleihen-Filter: Mittel der letzten 12 Monatsenden inkl. t

SPEC = {
    "id": "trend_ma12_bond_substitute_etf",
    "name": "Trendfilter US-Aktien/Anleihe-Cash-Ersatz MA(1,12), Live-Test auf SPY",
    "family": "macro",
    "tickers": [ASSET, SIGNAL, "VUSTX", "IEF"],
    "start": "1990-01-01",           # ^GSPC- und Anleihen-Vorlauf für 12 Monatsenden
    "sources": [
        "Faber 2007, A Quantitative Approach to Tactical Asset Allocation, SSRN 962461",
        "Antonacci 2014, Dual Momentum Investing (Anleihen als sicheres Bein)",
        "Neely, Rapach, Tu, Zhou 2014, Forecasting the Equity Risk Premium: The Role of Technical Indicators, "
        "https://files.stlouisfed.org/files/htdocs/wp/2010/2010-008.pdf",
    ],
    "params": {"signal": SIGNAL, "asset": ASSET, "bond": BOND, "bond_filter": True,
               "ma_short": 1, "ma_long": 12, "strict": False},
    "variants": {
        "ief": {"bond": "IEF"},
        "uncond": {"bond_filter": False},
    },
    "cost_bps": {ASSET: 10.0, "VUSTX": 10.0, "IEF": 10.0},
}


def weights(panel, signal: str = SIGNAL, asset: str = ASSET, bond: str = BOND, bond_filter: bool = True,
            ma_short: int = 1, ma_long: int = 12, strict: bool = False) -> pd.DataFrame:
    """Zielgewichte je Monatsende mit gültigem Signal: Spalten [asset, bond], Rest ist Cash."""
    idx = panel.close.index
    flags = month_end_flags(idx).to_numpy()
    # Aktienfilter: wie in der Basis (begrenztes ffill, kausal)
    sig_px = panel.close[signal].ffill(limit=5)
    me = sig_px[flags]
    fast = me.rolling(ma_short).mean()
    slow = me.rolling(ma_long).mean()
    on = (fast > slow) if strict else (fast >= slow)
    valid = fast.notna() & slow.notna() & panel.close[asset][flags].notna()

    # Anleihen-Bein: ohne ffill; fehlender Kurs oder zu kurze Historie = nicht investierbar (Cash)
    b_me = panel.close[bond][flags]
    if bond_filter:
        b_slow = b_me.rolling(BOND_MA_LONG).mean()          # NaN, wenn ein Monatsende in den 12 fehlt
        bond_ok = (b_me >= b_slow) & b_slow.notna() & b_me.notna()
    else:
        bond_ok = b_me.notna()

    out = pd.DataFrame({asset: on.astype(float),
                        bond: ((~on) & bond_ok).astype(float)}, index=me.index)
    return out[valid]
