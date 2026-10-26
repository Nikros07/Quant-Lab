"""Vol-Targeting auf den US-Aktienmarkt (EWMA, Harvey et al. 2018) — Live-Test auf dem investierbaren ETF SPY (ab 1993-01-29).

Zweites Modul zu `eq_voltarget_ewma_harvey` (Langzeit-Test auf French-Gesamtmarkt): gleiche Regel
(Kern `vol_target_weights` wird von dort importiert), aber gehandelt wird der SPY (Yahoo, angepasst = Total
Return) statt der French-Reihe. Regeln und Quellen siehe das Hauptmodul bzw. research/families/volmgmt.md, 3.1.

    r[t] = SPY-Tagesrendite (Adj Close pct_change); EWMA-Varianz mit HL 20, Null-Mittelwert, WARMUP 270 Tage;
    target = min(1.0, 12 % / sig[t]); Handel nur bei >= 5 pp Abweichung der nominellen Position.

Umsetzung im Engine-Vertrag:
* Signal am Schluss von t, Handel zur Eröffnung von t+1 (Standard-Ausführung des Labs). Die Spezifikation
  sieht "Signal Schluss s-2, Order Schluss s-1" vor; mit Eröffnungskurs-Ausführung wird die Order etwas
  früher (über Nacht statt einen vollen Handelstag später) umgesetzt. Derselbe Vertrag wie bei allen
  ETF-Modulen im Lab; mit `--exec close_next` im Harness lässt sich die Spezifikation enger nachstellen.
* Das erste Signal kommt nach 270 gültigen SPY-Renditen (ca. Februar 1994). Es werden keine Gewichte auf
  NaN-Kurse vergeben.
* Cash verzinst die Engine mit dem French-RF (^IRX aus der Spezifikation wird deshalb nicht gebraucht).
  Kosten 2 bp je Seite laut Spezifikation über SPEC["cost_bps"].

Varianten (vorab festgelegt, Robustheits-Checks, keine Auswahl der besten):
    cap_1_5  CAP 1.5 (Hebel; die Engine finanziert mit RF + 1.5 % statt der RF + 0.5 % der Spezifikation)
    hl_40    Halbwertszeit 40 Tage statt 20
    vol_10   Vol-Ziel 10 % statt 12 %
"""
from __future__ import annotations

import pandas as pd

from strategies.eq_voltarget_ewma_harvey import vol_target_weights

ASSET = "SPY"

SPEC = {
    "id": "eq_voltarget_ewma_harvey_etf",
    "name": "Vol-Targeting US-Aktienmarkt (EWMA HL 20, Ziel 12 %, ohne Hebel), Live-Test auf SPY",
    "family": "volmgmt",
    "tickers": [ASSET],
    "start": "1993-01-01",           # SPY startet 1993-01-29
    "sources": [
        "Harvey, Hoyle, Korgaonkar, Rattray, Sargaison, Van Hemert 2018, The Impact of Volatility Targeting, "
        "https://people.duke.edu/~charvey/Research/Published_Papers/P135_The_impact_of.pdf",
        "Cederburg, O'Doherty, Wang, Yan 2020, On the performance of volatility-managed portfolios, "
        "https://www.lehigh.edu/~xuy219/research/COWY.pdf",
    ],
    "params": {"asset": ASSET, "target_vol": 0.12, "halflife": 20, "cap": 1.0, "band": 0.05, "warmup": 270},
    "variants": {
        "cap_1_5": {"cap": 1.5},
        "hl_40": {"halflife": 40},
        "vol_10": {"target_vol": 0.10},
    },
    "cost_bps": {ASSET: 2.0},
}


def weights(panel, asset: str = ASSET, target_vol: float = 0.12, halflife: float = 20, cap: float = 1.0,
            band: float = 0.05, warmup: int = 270) -> pd.DataFrame:
    """Zielgewichte (0 < w <= cap) auf `asset` an Tagen, an denen das No-Trade-Band verletzt wird; Rest ist Cash."""
    return vol_target_weights(panel.close[asset], asset, target_vol=target_vol, halflife=halflife, cap=cap,
                              band=band, warmup=warmup, first_signal=None)
