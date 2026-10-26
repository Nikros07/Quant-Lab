"""Faber (2007) Tactical Asset Allocation — 10-Monats-Trendfilter auf 5 Assetklassen.

Referenz-Implementierung und Vorlage für alle anderen Strategien.
Quelle: Mebane T. Faber, "A Quantitative Approach to Tactical Asset Allocation",
Journal of Wealth Management 2007 (SSRN 962461).

Regel (Paper): Am Monatsende je Assetklasse: Schlusskurs > 10-Monats-Durchschnitt der
Monatsschlusskurse -> 20 % Gewicht, sonst Cash. Gleichgewichtet über 5 Klassen.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from qlab.calendar import month_end_flags

SPEC = {
    "id": "faber_gtaa",
    "name": "Faber GTAA (10-Monats-SMA, 5 Assetklassen)",
    "family": "tactical",
    "tickers": ["SPY", "EFA", "IEF", "DBC", "VNQ"],
    "start": "2006-03-01",       # DBC startet 2006-02
    "sources": ["Faber 2007, A Quantitative Approach to Tactical Asset Allocation, SSRN 962461"],
    "params": {"lookback_months": 10},
    "variants": {"sma_8": {"lookback_months": 8}, "sma_12": {"lookback_months": 12}},
}


def weights(panel, lookback_months: int = 10) -> pd.DataFrame:
    px = panel.close[SPEC["tickers"]]
    flags = month_end_flags(px.index)
    me = px[flags.to_numpy()]                              # nur kausal erkannte Monatsenden
    sma = me.rolling(lookback_months).mean()               # inkl. aktuellem Monatsende (wie im Paper)
    on = (me > sma) & me.notna() & sma.notna()
    w = on.astype(float) / len(SPEC["tickers"])            # 20 % pro Klasse, Rest Cash
    # Zeilen ohne jede gültige Historie nicht als Signal werten
    valid = sma.notna().all(axis=1)
    return w[valid]
