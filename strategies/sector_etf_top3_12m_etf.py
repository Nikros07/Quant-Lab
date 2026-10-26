"""Faber-Sektorrotation, handelbare ETF-Fassung: Top 3 von 9 SPDR-Sektor-ETFs nach 12-Monats-Rendite.

Gleiche Regel wie der Langzeit-Check in `sector_etf_top3_12m.py` (Kern `rotation_weights` wird von dort
importiert), aber auf Yahoo-ETFs (auto_adjust, Total Return) ab 1998-12.

Universum fest: XLB XLE XLF XLI XLK XLP XLU XLV XLY. XLRE (ab 2015-10) und XLC (ab 2018-06) werden NICHT
aufgenommen, damit das Universum konstant bleibt. SPY liegt nur im Panel, um die sma10-Variante zu
speisen (SPY unter dem Mittel seiner letzten 10 Monatsenden -> alles Cash); die Basis hält SPY nie.

Erstes Signal: 1999-12-31 (t12 = 1998-12-31, die XL-Daten beginnen 1998-12-22).
Quellen: Faber 2010, Relative Strength Strategies for Investing (SSRN 1585517);
Quantpedia, Sector Momentum - Rotational System.
"""
from __future__ import annotations

import pandas as pd

from strategies.sector_etf_top3_12m import rotation_weights

UNIVERSE = ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]
FILTER = "SPY"

SPEC = {
    "id": "sector_etf_top3_12m_etf",
    "name": "Faber-Sektorrotation ETF (Top 3 von 9 SPDR-Sektoren, 12-Monats-Rendite)",
    "family": "xsmom",
    "tickers": UNIVERSE + [FILTER],
    "start": "1998-12-22",
    "sources": [
        "Faber 2010, Relative Strength Strategies for Investing, SSRN 1585517",
        "Quantpedia, Sector Momentum - Rotational System, https://quantpedia.com/strategies/sector-momentum-rotational-system",
    ],
    "params": {"lookback_months": 12, "top_n": 3, "combo": False, "cash_filter_months": 0, "hold_rank": 0},
    "variants": {
        "combo": {"combo": True},
        "sma10": {"cash_filter_months": 10},
        "hold_buffer": {"hold_rank": 5},
    },
}


def weights(panel, **params) -> pd.DataFrame:
    p = {**SPEC["params"], **params}
    filt = panel.close[FILTER] if p["cash_filter_months"] else None
    return rotation_weights(panel.close, UNIVERSE, filter_close=filt, **p)
