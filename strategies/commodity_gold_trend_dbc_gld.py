"""Rohstoff- und Gold-Trendfilter (DBC + GLD je 50 %, SMA 210), Long/Cash.

Quellen (Mechanismus, kein Parameterfund): Gorton/Rouwenhorst 2006 (NBER w10595) und
Bhardwaj/Gorton/Rouwenhorst 2015 (NBER w21243). Die Regel selbst ist eine einfache, vorab festgelegte
Trendfilter-Regel aus research/families/crypto.md, Abschnitt 3.2 (Familie dort unter "crypto" einsortiert;
inhaltlich Rohstoff-/Gold-Trend). Erwartung laut Recherche: Risikominderung, kein belegter Edge.

Regel (feste Parameter, KEINE Optimierung):
    Je Instrument X in {DBC, GLD}, täglich nach Handelsschluss t:
        on_X(t) = AdjClose_X(t) > SMA_210(AdjClose_X)(t)         (SMA inkl. Tag t, strikt größer)
        w_X(t)  = 0.5, wenn on_X(t), sonst 0                      (Rest Cash; kein Hebel, kein Short)
    Die Engine handelt zur Eröffnung von t+1; Kosten (10 bp je Seite über SPEC["cost_bps"]), Cash-Zins
    und Steuer verbucht die Engine.

Umsetzung im Engine-Vertrag:
* Signal-Historie: Der SMA wird auf den eigenen Beobachtungen jedes Instruments gerechnet (nur Vergangenheit,
  rollierend, inkl. t). Ein Signal gibt es erst, wenn ALLE Instrumente des gewählten Universums 210 Kurse
  Historie haben (Zeilen ohne vollständige Historie sind kein Signal). Fehlt an einem Tag der Kurs eines
  Instruments (NaN = nicht handelbar), gibt es an diesem Tag keine Zeile: Positionen driften, es wird nie ein
  Gewicht auf einen NaN-Kurs vergeben.
* Handelsfrequenz: Die Regel wird täglich geprüft, die Zeile (= Rebalancing-Signal) wird aber nur am ersten
  Signaltag und an Tagen geschrieben, an denen sich der Zielvektor gegenüber dem vorigen Signaltag ändert.
  Das entspricht der in der Spezifikation genannten Umschlagsrechnung (nur Signalwechsel, ca. 7,5 Einheiten
  pro Jahr) und vermeidet tägliches Drift-Rebalancing (Kosten und Steuer-Realisierung ohne Signal).
  Bei einem Signalwechsel stellt die Engine beide Beine auf das Zielgewicht (das nicht gewechselte Bein
  wird dabei mit zurückgesetzt).
* Cash-Zins: die Engine verzinst Cash mit dem Fama-French-RF (nicht mit ^IRX); ^IRX, GSG und IAU der
  Spezifikation werden nicht gebraucht (GSG/IAU nur als Ersatz, falls DBC/GLD fehlen würden).

Varianten (vorab festgelegt, Robustheits-Checks, keine Auswahl der besten):
    sma168     Fenster 168 Handelstage statt 210
    sma252     Fenster 252 Handelstage statt 210
    gold_only  nur GLD (Gewicht 1,0 statt 0,5, wenn on), DBC bleibt ohne Gewicht; das Signal beginnt dann
               schon, sobald GLD 210 Kurse hat (GLD ist früher gelistet als DBC)
"""
from __future__ import annotations

import pandas as pd

TICKERS = ["DBC", "GLD"]

SPEC = {
    "id": "commodity_gold_trend_dbc_gld",
    "name": "Rohstoff- und Gold-Trendfilter (DBC + GLD je 50 %, SMA 210), Long/Cash",
    "family": "crypto",                   # Einordnung der Recherche (families/crypto.md); inhaltlich Rohstoff/Gold-Trend
    "tickers": list(TICKERS),
    "start": "2004-11-18",                # GLD-Start; DBC startet im Cache am 2006-03-01
    "sources": [
        "Gorton, Rouwenhorst 2006, Facts and Fantasies about Commodity Futures, https://www.nber.org/papers/w10595",
        "Bhardwaj, Gorton, Rouwenhorst 2015, Facts and Fantasies about Commodity Futures Ten Years Later, "
        "https://www.nber.org/papers/w21243",
    ],
    "params": {"window": 210, "universe": ("DBC", "GLD")},
    "variants": {
        "sma168": {"window": 168},
        "sma252": {"window": 252},
        "gold_only": {"universe": ("GLD",)},
    },
    "cost_bps": {"DBC": 10.0, "GLD": 10.0},
}


def weights(panel, window: int = 210, universe: tuple = ("DBC", "GLD")) -> pd.DataFrame:
    """Zielgewichte (Spalten = TICKERS) an Signaltagen mit Zielwechsel; Gewicht je Instrument = 1/len(universe) bei on."""
    uni = list(universe)
    if not uni or any(t not in TICKERS for t in uni) or len(set(uni)) != len(uni):
        raise ValueError(f"universe muss eine nichtleere Teilmenge von {TICKERS} ohne Duplikate sein: {uni}")
    if int(window) != window or window < 2:
        raise ValueError(f"window muss eine ganze Zahl >= 2 sein: {window}")
    window = int(window)

    idx = panel.close.index
    legs = {}
    for t in uni:
        s = panel.close[t].dropna()                       # eigene Beobachtungen (NaN = nicht gelistet / Datenloch)
        sma = s.rolling(window).mean()                    # inkl. Tag t, nur Vergangenheit
        sig = (s > sma).astype(float).where(sma.notna())  # NaN, solange keine volle Historie
        legs[t] = sig.reindex(idx)                        # NaN an Tagen ohne eigenen Kurs
    sig = pd.DataFrame(legs, index=idx)
    sig = sig[sig.notna().all(axis=1)]                    # nur Tage mit Kurs UND Historie für alle Beine

    w = pd.DataFrame(0.0, index=sig.index, columns=TICKERS)
    w[uni] = sig / len(uni)
    if len(w) == 0:
        return w
    changed = (w != w.shift(1)).any(axis=1)
    changed.iloc[0] = True                                # erste Zeile = Startsignal (auch bei komplett Cash)
    return w[changed.to_numpy()]
