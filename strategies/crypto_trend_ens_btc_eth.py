"""BTC/ETH Trend-Ensemble (SMA 20/50/100/200), Long/Flat mit Cash.

Quellen / Mechanismus: Trendfolge in einem aufmerksamkeitsgetriebenen, von Privatanlegern dominierten Markt
(Zarattini/Pagani/Barbon 2025 "Catching Crypto Trends", Han/Kang/Ryu 2023 "Time-Series and Cross-Sectional
Momentum in the Cryptocurrency Market"). Die konkrete Regel stammt aus research/families/crypto.md,
Abschnitt 3.1 (identisch mit den Eigenchecks 4.1/4.2), festgelegt vor diesem Backtest.

Regel (täglich, nach dem UTC-Tagesschluss t; Krypto handelt an 7 Tagen pro Woche):
    s_X  = 1/4 * Summe_{n in {20,50,100,200}} 1[Close_X(t) > SMA_n(Close_X)(t)]     (SMA inkl. Close t, strikt >)
    X in {BTC-USD, ETH-USD}; ein Coin gilt erst, wenn die längste SMA-Historie (200 Closes) vorliegt,
    sonst s_X = 0 (ETH startet 2017-11-09, also erstes ETH-Gewicht nach 200 Closes).
    w_X  = 0.5 * s_X,   w_Cash = 1 - w_BTC - w_ETH.   Kein Hebel, kein Short.

Umsetzung im Engine-Vertrag:
* Signal am Schlusskurs t (Yahoo-Tagesende = 23:59:59 UTC), die Engine handelt zur Eröffnung t+1
  (= 00:00 UTC, praktisch derselbe Kurs). Es wird jeden Tag eine Zielgewichtszeile ausgegeben
  ("täglich prüfen"); die Engine bucht damit auch die Kosten für das Zurückführen der gedrifteten Gewichte
  auf 0,5 * s_X. Das ist konservativer als der Eigencheck der Spezifikation, der Kosten nur bei Signalwechseln
  ansetzte.
* Erstes Gewicht am 2015-09-01 (Spezifikation: "Start 2015-09"); die SMA-Historie davor (BTC ab 2014-09-17)
  dient nur als Vorlauf. Parameter `first_signal`.
* Cash verzinst die Engine selbst mit dem Fama-French-RF; ^IRX (Prozentwert, nicht handelbar) ist nicht im Panel.
* Kosten 20 bp je Seite und Coin (Spezifikation) über SPEC["cost_bps"]; der 50-bp-Stress läuft über den
  Harness-Schalter `--cost-mult 2.5`.

Varianten (vorab festgelegt, Robustheits-Checks, keine Auswahl der besten):
    sma50_btc    Einzelregel Close > SMA50 -> 100 % BTC (ETH nicht gehandelt)
    sma200_btc   Einzelregel Close > SMA200 -> 100 % BTC (ETH nicht gehandelt)
    (dritte Variante der Spezifikation, "Kosten 50 bp", ist keine Gewichtsregel: --cost-mult 2.5)
"""
from __future__ import annotations

import pandas as pd

BTC = "BTC-USD"
ETH = "ETH-USD"

SPEC = {
    "id": "crypto_trend_ens_btc_eth",
    "name": "BTC/ETH Trend-Ensemble (SMA 20/50/100/200), Long/Flat mit Cash",
    "family": "crypto",
    "tickers": [BTC, ETH],
    "start": "2014-09-17",           # BTC-USD startet 2014-09-17 (SMA-Vorlauf); ETH-USD ab 2017-11-09
    "sources": [
        "Zarattini, Pagani, Barbon 2025, Catching Crypto Trends, https://abarbon.com/papers/catching-crypto-trends",
        "Han, Kang, Ryu 2023, Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market, "
        "https://acfr.aut.ac.nz/__data/assets/pdf_file/0009/918729/Time_Series_and_Cross_Sectional_Momentum_in_the_Cryptocurrency_Market_with_IA.pdf",
    ],
    "params": {"lookbacks": (20, 50, 100, 200), "assets": (BTC, ETH), "first_signal": "2015-09-01"},
    "variants": {
        "sma50_btc": {"lookbacks": (50,), "assets": (BTC,)},
        "sma200_btc": {"lookbacks": (200,), "assets": (BTC,)},
    },
    "cost_bps": {BTC: 20.0, ETH: 20.0},
}


def weights(panel, lookbacks=(20, 50, 100, 200), assets=(BTC, ETH), first_signal: str | None = "2015-09-01") -> pd.DataFrame:
    """Tägliche Zielgewichte: je Coin (1/len(assets)) * Anteil der SMA-Regeln, die "Close > SMA" melden; Rest Cash."""
    lookbacks = tuple(int(n) for n in lookbacks)
    assets = tuple(assets)
    px = panel.close
    out = pd.DataFrame(0.0, index=px.index, columns=SPEC["tickers"])
    for a in assets:
        c = px[a]
        votes = sum((c > c.rolling(n).mean()).astype(float) for n in lookbacks) / len(lookbacks)
        # Coin zählt erst mit vollständiger Historie der längsten SMA (und gültigem aktuellen Kurs), sonst Gewicht 0
        ready = c.rolling(max(lookbacks)).mean().notna()
        out[a] = votes.where(ready, 0.0) / len(assets)
    has_price = px[list(assets)].notna().any(axis=1)
    keep = has_price.to_numpy()
    if first_signal is not None:
        keep = keep & (px.index >= pd.Timestamp(first_signal))
    return out[keep]
