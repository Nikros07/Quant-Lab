"""Laender-ETF-Querschnitts-Momentum (12-1) auf 17 iShares-MSCI-Laender-ETFs.

Quellen: Asness/Moskowitz/Pedersen 2013 "Value and Momentum Everywhere" (Momentum-Praemie auch in
Laender-Aktienindizes), Daniel/Moskowitz 2016 "Momentum Crashes". Die Gewichtung (Rang minus
Durchschnittsrang) ist eine feste Implementierungsentscheidung im AMP-Stil, kein Paper-Wert.

Regel (Spezifikation research/strategie-kandidaten.json, Eintrag country_etf_xsmom_12_1):
  Signaltag t = letzter NYSE-Handelstag von Monat m (qlab.calendar.month_end_flags, nur Daten <= t).
  score_i = AdjClose_i[Ende m-1] / AdjClose_i[Ende m-12] - 1       (11-Monats-Rendite, juengster Monat uebersprungen)
  rank_i  = 1..N aufsteigend nach Score (Gleichstand alphabetisch nach Ticker), z_i = rank_i - (N+1)/2
  Hauptlauf Long-Short dollar-neutral: w_i = z_i / sum(z_j > 0)   (bei N=17: z/36, Long +1, Short -1, Brutto 2)
  Engine handelt zur Eroeffnung t+1, monatliches Rebalancing, Halten bis zum naechsten Signaltag.
  Erstes Signal 1997-03-31 (Ende m-12 = 1996-03-29).

Vorab festgelegte Varianten (Robustheits-Checks, keine Optimierung):
  long_top5       : 1/5 auf die 5 besten, long-only
  long_top5_sma10 : wie long_top5, ein ausgewaehlter ETF aber nur, wenn AdjClose[t] > Mittel seiner letzten
                    10 Monatsendkurse (inkl. t, wie Faber), sonst Cash
  universe_ext    : Hauptlauf (Long-Short) mit Universum + EWZ, EWY, EWT, EZA ab Verfuegbarkeit

Nicht in der Strategie: Kosten (5 bp je Seite), Cash-Zins, Leihegebuehr, Steuer - das verbucht die Engine.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from qlab.calendar import month_end_flags

UNIVERSE = ["EWA", "EWC", "EWG", "EWH", "EWI", "EWJ", "EWM", "EWN", "EWP", "EWQ", "EWS", "EWU", "EWW",
            "EWL", "EWD", "EWK", "EWO"]
EXTENSION = ["EWZ", "EWY", "EWT", "EZA"]       # nur fuer die Variante universe_ext (Daten ab 2000-05 bis 2003-02)

SPEC = {
    "id": "country_etf_xsmom_12_1",
    "name": "Laender-ETF-Momentum (17 iShares-MSCI-Laender, 12-1, Rang-Gewichte)",
    "family": "xsmom",
    # Erweiterungs-Ticker nur geladen, damit die Variante universe_ext Daten hat; der Hauptlauf
    # (und die beiden Long-only-Varianten) rangiert ausschliesslich die 17 Basis-ETFs.
    # EFA (Vergleichs-Buy&Hold) und ^IRX (Zinsquelle) sind keine Handelsobjekte der Regel: Cash-Zins
    # verbucht die Engine selbst (Fama-French RF), die Benchmarks liefert der Harness.
    "tickers": UNIVERSE + EXTENSION,
    "start": "1996-03-18",
    "sources": [
        "Asness, Moskowitz, Pedersen 2013, Value and Momentum Everywhere, "
        "https://www.aqr.com/library/journal-articles/value-and-momentum-everywhere",
        "Daniel, Moskowitz 2016, Momentum Crashes, "
        "https://business.columbia.edu/sites/default/files-efs/pubfiles/4607/mom11.pdf",
    ],
    "params": {
        "mode": "long_short",       # "long_short" (Hauptlauf) oder "long_top"
        "lookback_months": 12,      # Ende m-12 ...
        "skip_months": 1,           # ... bis Ende m-1
        "top_n": 5,                 # nur mode="long_top"
        "sma_filter": False,        # nur mode="long_top": ETF nur ueber seinem 10-Monats-Mittel
        "sma_months": 10,
        "extended": False,          # True: Universum + EWZ, EWY, EWT, EZA ab Verfuegbarkeit
        "min_assets": 10,           # Datenschutz: weniger gueltige Titel -> kein Signal (greift historisch nie)
    },
    "variants": {
        "long_top5": {"mode": "long_top"},
        "long_top5_sma10": {"mode": "long_top", "sma_filter": True},
        "universe_ext": {"extended": True},
    },
}


def weights(panel, mode: str = "long_short", lookback_months: int = 12, skip_months: int = 1,
            top_n: int = 5, sma_filter: bool = False, sma_months: int = 10, extended: bool = False,
            min_assets: int = 10) -> pd.DataFrame:
    if mode not in ("long_short", "long_top"):
        raise ValueError(mode)
    if min_assets < 2:
        raise ValueError("min_assets muss >= 2 sein")
    names = UNIVERSE + (EXTENSION if extended else [])
    cols = [t for t in names if t in panel.close.columns]
    px = panel.close[cols]

    flags = month_end_flags(px.index)
    me = px[flags.to_numpy()]                                  # nur kausal erkannte Monatsenden
    me = me.where(me > 0)                                      # nicht-positive Kurse = ungueltig
    score = me.shift(skip_months) / me.shift(lookback_months) - 1.0   # 12-1: Ende m-1 / Ende m-12 - 1
    sma = me.rolling(sma_months).mean()                        # inkl. aktuellem Monatsende; NaN bei Luecke

    sc, cur, av = score.to_numpy(float), me.to_numpy(float), sma.to_numpy(float)
    name_arr = np.array(cols)
    out = np.zeros_like(sc)
    keep = np.zeros(len(me), dtype=bool)
    for r in range(len(me)):
        ok = np.isfinite(sc[r]) & np.isfinite(cur[r])          # Score da UND heute handelbarer Kurs
        n = int(ok.sum())
        if n < min_assets:
            continue
        keep[r] = True
        idx = np.flatnonzero(ok)
        order = idx[np.lexsort((name_arr[idx], sc[r, idx]))]   # aufsteigend nach Score, Gleichstand alphabetisch
        if mode == "long_short":
            z = np.arange(1, n + 1) - (n + 1) / 2.0            # N=17: -8 ... +8
            out[r, order] = z / z[z > 0].sum()                 # N=17: z/36 -> Long +1, Short -1
        else:
            top = order[-top_n:]                               # die top_n hoechsten Raenge
            if sma_filter:
                top = top[cur[r, top] > av[r, top]]            # NaN-SMA -> False -> Cash
            out[r, top] = 1.0 / top_n
    return pd.DataFrame(out[keep], index=me.index[keep], columns=cols)
