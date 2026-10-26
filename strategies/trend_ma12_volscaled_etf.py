"""Trendfilter US-Aktien MA(1,12) mit Volatilitäts-Skalierung im LONG-Zustand — H9 (Live-Test auf SPY).

Regel (festgelegt vor dem Backtest, docs/HYPOTHESEN.md, H9):
    Signal wie Basis `trend_ma12_us_equity_cash_etf`: P_m = Schlusskurs ^GSPC (Preisindex) am Monatsende,
    MA12 = Mittel der letzten 12 Monatsend-Schlusskurse inkl. t, LONG, wenn P_t >= MA12_t.
    Am Monatsende LONG:  Gewicht SPY = min(1.0; Ziel / sigma)
        sigma = Standardabweichung (ddof=1) der täglichen einfachen SPY-Renditen der letzten
                vol_window = 21 Handelstage bis einschließlich Monatsende, mal sqrt(252).
        Ziel = 15 % (Hauptlauf), Variante `target10` = 10 %.
    Am Monatsende FLAT: Gewicht 0 (Cash). Ist sigma NaN oder 0: Gewicht 0.
    Gewichte nur an Monatsenden, kein Hebel (Cap 1.0), kein Short.

Umsetzung im Engine-Vertrag:
* Signal und sigma nutzen nur Daten bis einschließlich t (kausal); die Engine handelt zur Eröffnung von t+1.
* Das Signal bleibt der Preisindex ^GSPC; SPY ist das Handelsinstrument. Vor der SPY-Notierung wird kein
  Gewicht vergeben (kein Kurs = keine Zeile).
* Kosten 10 bp je Wechsel (SPEC["cost_bps"]). Cash wird über den French-RF verzinst (Engine).

Quellen:
    Faber 2007, A Quantitative Approach to Tactical Asset Allocation, SSRN 962461
    Moreira, Muir 2017, Volatility-Managed Portfolios, Journal of Finance 72(4) (Volatilitäts-Skalierung)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from qlab.calendar import month_end_flags

ASSET = "SPY"
SIGNAL = "^GSPC"

SPEC = {
    "id": "trend_ma12_volscaled_etf",
    "name": "Trendfilter US-Aktien MA(1,12) mit Vol-Skalierung (Ziel 15 %), SPY",
    "family": "volmgmt",
    "tickers": [ASSET, SIGNAL],
    "start": "1990-01-01",           # ^GSPC-Vorlauf für 12 Monatsenden; SPY selbst startet 1993-01-29
    "sources": [
        "Faber 2007, A Quantitative Approach to Tactical Asset Allocation, SSRN 962461",
        "Moreira, Muir 2017, Volatility-Managed Portfolios, Journal of Finance 72(4)",
    ],
    "params": {"signal": SIGNAL, "asset": ASSET, "ma_short": 1, "ma_long": 12, "strict": False,
               "target": 0.15, "vol_window": 21},
    "variants": {
        "target10": {"target": 0.10},
    },
    "cost_bps": {ASSET: 10.0},
}


def weights(panel, signal: str = SIGNAL, asset: str = ASSET, ma_short: int = 1, ma_long: int = 12,
            strict: bool = False, target: float = 0.15, vol_window: int = 21) -> pd.DataFrame:
    """Zielgewichte auf `asset` an jedem Monatsende mit gültigem Signal.

    LONG (Signal >= MA): min(1, target / sigma_annual) mit sigma aus den letzten `vol_window` Tagesrenditen.
    FLAT oder sigma NaN/0: 0.
    """
    idx = panel.close.index
    flags = month_end_flags(idx).to_numpy()

    # Trendsignal wie Basis (begrenztes Vorwärtsfüllen, kausal)
    sig_px = panel.close[signal].ffill(limit=5)
    me = sig_px[flags]
    fast = me.rolling(ma_short).mean()
    slow = me.rolling(ma_long).mean()
    on = (fast > slow) if strict else (fast >= slow)
    px = panel.close[asset]
    valid = fast.notna() & slow.notna() & px[flags].notna()

    # Realisierte Vola: letzte vol_window tägliche einfache Renditen bis einschließlich t
    ret = px / px.shift(1) - 1.0
    sigma_ann = ret.rolling(vol_window, min_periods=vol_window).std(ddof=1) * np.sqrt(252)
    s = sigma_ann[flags].to_numpy(float)

    with np.errstate(divide="ignore", invalid="ignore"):
        raw = np.where(np.isfinite(s) & (s > 0), target / s, 0.0)
    scale = np.minimum(1.0, raw)                       # kein Hebel
    w = on.astype(float).to_numpy() * scale
    return pd.DataFrame({asset: w}, index=me.index)[valid]
