"""Länder-Value nach Faber (CAPE-Idee) mit Gratis-Proxy: Kurs / 10-Jahres-Durchschnitt, billigstes Drittel.

Quellen: Faber 2012 "Global Value: Building Trading Models with the 10 Year CAPE" (Quantpedia-Zusammenfassung),
Asness 2012 "An Old Friend: The Stock Market's Shiller P/E". Länder-CAPEs sind gratis nicht verfügbar; der
Proxy ersetzt "realer Index / 10J-Durchschnitt realer Gewinne" durch "Kurs / 10J-Durchschnitt des Kurses".

Regel (Spezifikation research/strategie-kandidaten.json, Eintrag country_value_cape_faber_proxy):
  Universum: 14 ETFs (SPY + 13 iShares-MSCI-Länder), Kurs P = angepasster Schlusskurs (USD, Total Return).
  Signaltag t = letzter NYSE-Handelstag im Dezember (qlab.calendar.month_end_flags, nur Daten <= t).
  Kandidaten = ETFs mit gültigen Monatsendkursen für alle der letzten 120 Monatsenden bis t (>= 120 Monate
  Historie, keine Lücke) UND gültigem Kurs am Signaltag selbst (sonst nicht handelbar).
  RP_i = P_i(t) / Mittel(P_i über die letzten 120 Monatsendwerte bis einschließlich t).
  Auswahl: die floor(N/3) Kandidaten mit dem kleinsten RP_i (Gleichstand alphabetisch nach Ticker),
  gleichgewichtet (Summe 1), long-only, kein Cash-Filter. Ist floor(N/3) = 0 (zu wenige Kandidaten), gibt es
  KEIN Signal an diesem Tag (keine Cash-Zeile). Das gilt historisch bis 2005, weil bis dahin nur SPY
  (ab 1993) 120 Monate Historie hat; die erste Entscheidung ist damit 2006-12-29 (N = 14, 4 Länder).
  Die Engine handelt zur Eröffnung von t+1 und hält 12 Monate (zwischen den Signalen keine Zeilen, Drift).
  Kosten 10 bp je Seite stehen in SPEC["cost_bps"]; Cash-Zins und Steuer verbucht die Engine.

Vorab festgelegte Varianten (Robustheits-Checks der Spezifikation, keine Optimierung):
  quartile : billigstes Viertel statt Drittel (select_divisor = 4, bei N = 14 also 3 Länder)
  avg60    : 60- statt 120-Monats-Durchschnitt (AMP-Reversal-Proxy); die Historienpflicht der Kandidaten
             folgt dem Fenster (60 Monate), die erste Entscheidung rückt dadurch auf 2001-12
  june     : Rebalancing im Juni statt Dezember (Timing-Luck-Test), erste Entscheidung 2006-06

Hilfsfunktion benchmark_weights(): Benchmark der Spezifikation (gleichgewichteter Korb aller Kandidaten,
jährlich rebalanciert, gleiche Signaltage). Der Harness vergleicht nur gegen SPY/US-Markt; die Bewertung als
Excess gegen diesen Korb muss separat laufen (der Korb ist keine registrierte Strategie).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from qlab.calendar import month_end_flags

UNIVERSE = ["SPY", "EWC", "EWU", "EWG", "EWQ", "EWI", "EWP", "EWN", "EWL", "EWD", "EWJ", "EWA", "EWH", "EWS"]

SPEC = {
    "id": "country_value_cape_faber_proxy",
    "name": "Länder-Value: billigstes Drittel nach Kurs/10J-Durchschnitt (Faber-CAPE-Proxy, 14 ETFs)",
    "family": "valuecarry",
    "tickers": UNIVERSE,
    # SPY startet 1993-01-29, die 13 Länder-ETFs 1996-03-18; die erste Entscheidung liegt erst im 12/2006.
    # Start 1993 (statt 1996), damit ein Cache-Refresh den von den Benchmarks geteilten SPY-Cache nicht kürzt.
    "start": "1993-01-01",
    "sources": [
        "Faber 2012, Global Value: Building Trading Models with the 10 Year CAPE, "
        "https://quantpedia.com/strategies/value-factor-effect-within-countries",
        "Asness 2012, An Old Friend: The Stock Market's Shiller P/E, "
        "https://www.aqr.com/library/aqr-publications/an-old-friend-the-stock-markets-shiller-pe",
    ],
    "params": {
        "lookback_months": 120,     # Durchschnitt über die letzten 120 Monatsenden (inkl. t)
        "select_divisor": 3,        # billigstes Drittel: floor(N / 3)
        "rebalance_month": 12,      # Signaltag = letzter Handelstag dieses Monats
    },
    "variants": {
        "quartile": {"select_divisor": 4},
        "avg60": {"lookback_months": 60},
        "june": {"rebalance_month": 6},
    },
    "cost_bps": {t: 10.0 for t in UNIVERSE},       # 10 bp je Seite laut Spezifikation
}


def _signals(panel, lookback_months: int, select_divisor: int, rebalance_month: int, pick_all: bool) -> pd.DataFrame:
    """Gemeinsamer Kern von weights() und benchmark_weights()."""
    if lookback_months < 2:
        raise ValueError("lookback_months muss >= 2 sein")
    if select_divisor < 1:
        raise ValueError("select_divisor muss >= 1 sein")
    if not 1 <= rebalance_month <= 12:
        raise ValueError("rebalance_month muss 1..12 sein")
    cols = [t for t in UNIVERSE if t in panel.close.columns]
    px = panel.close[cols]

    flags = month_end_flags(px.index)
    me = px[flags.to_numpy()]                                  # nur kausal erkannte Monatsenden
    me = me.where(me > 0)                                      # nicht-positive Kurse = ungültig
    avg = me.rolling(lookback_months).mean()                   # inkl. aktuellem Monatsende; jede Lücke -> NaN
    rp = (me / avg).to_numpy(float)                            # NaN = kein Kandidat (zu kurze Historie, Lücke, kein Kurs heute)

    name_arr = np.array(cols)
    out = np.zeros(rp.shape)
    keep = np.zeros(len(me), dtype=bool)
    for r in np.flatnonzero(me.index.month == rebalance_month):
        ok = np.isfinite(rp[r])
        n = int(ok.sum())
        k = n // select_divisor                                # floor(N / Divisor)
        if k < 1:
            continue                                           # zu wenige Kandidaten: kein Signal
        idx = np.flatnonzero(ok)
        order = idx[np.lexsort((name_arr[idx], rp[r, idx]))]   # aufsteigend nach RP, Gleichstand alphabetisch
        pick = order if pick_all else order[:k]
        out[r, pick] = 1.0 / len(pick)
        keep[r] = True
    return pd.DataFrame(out[keep], index=me.index[keep], columns=cols)


def weights(panel, lookback_months: int = 120, select_divisor: int = 3, rebalance_month: int = 12) -> pd.DataFrame:
    """Zielgewichte (Summe 1, long-only) an den Signaltagen; zwischen den Signalen keine Zeilen."""
    return _signals(panel, lookback_months, select_divisor, rebalance_month, pick_all=False)


def benchmark_weights(panel, lookback_months: int = 120, select_divisor: int = 3, rebalance_month: int = 12) -> pd.DataFrame:
    """Gleichgewichteter Korb aller Kandidaten an denselben Signaltagen wie weights() (Benchmark der Spezifikation)."""
    return _signals(panel, lookback_months, select_divisor, rebalance_month, pick_all=True)
