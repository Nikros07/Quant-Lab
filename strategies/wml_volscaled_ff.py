"""Volatilitaets-skaliertes US-Aktien-Momentum (WML) auf Ken-French-Dezilen — Messlatte auf Faktor-Ebene.

Quellen: Barroso/Santa-Clara 2015 ("Momentum has its moments", JFE); Daniel/Moskowitz 2016
("Momentum Crashes", JFE; dort als "cvol" mit 126 Tagen und Vol-Ziel 19 % nachgebaut);
Cederburg/O'Doherty/Wang/Yan 2020 (kritische Gegenprobe zu vol-gemanagten Portfolios).

Daten (Ken French, Tagesrenditen, wertgewichtet, in `load()` als Panel via panel_from_returns):
    "Hi PRIOR" / "Lo PRIOR" aus 10_Portfolios_Prior_12_2_Daily (Tabelle 0), WML[d] = R_hi[d] - R_lo[d].
Cash-Zins (Fama-French RF) verbucht die Engine selbst.

Regel (Spezifikation, unveraendert uebernommen):
    Signaltag t = letzter Handelstag jedes Monats (qlab.calendar.month_end_flags, kausal):
        sigma = stdev(WML[t-125 .. t], ddof=1) * sqrt(252)        # 126 Beobachtungen inkl. t
        w     = min(0.12 / sigma, 2.0)                             # Deckel 2.0 = Schutzgrenze des Labs
    Ziel: +w auf "Hi PRIOR", -w auf "Lo PRIOR", Rest Cash (RF). Signal am Schluss von t, die Engine
    handelt am Folgetag (Panel aus Renditen: open == close, also zum Schlusskurs von t+1).
    Signale erst ab 1930-01-01 ("Test ab 1930"); die Jahre davor liefern nur Vorlauf fuer die 126 Tage.

Varianten (vorab festgelegt, zaehlen als Versuche): statisch w = 1 (Kontrolle), Vol-Ziel 19 %, Deckel 1.0.
Keine Parameteroptimierung; alle Parameter stammen aus der Quelle bzw. der Spezifikation.

Kosten: Die Spezifikation verlangt 0.65 % pro Monat mal mittleres w (Novy-Marx/Velikov) statt der
Standardkosten. Diese Kosten entstehen im Aktien-Umschlag INNERHALB der French-Dezile und sind im
Handelsvolumen der beiden Dezil-Reihen nicht sichtbar. Naeherung: `cost_bps` (pro Seite, auf beide
Reihen) ist so kalibriert, dass die Engine bei den tatsaechlichen Monats-Rebalancings im Mittel
0.65 % * w pro Monat belastet (siehe `implied_cost_bps` und den Kommentar bei CALIBRATED_COST_BPS). Das ersetzt die
5 bps Standard; zusaetzlich zieht die Engine nur die Leihgebuehr (0.5 % p.a. auf Short-Volumen).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from qlab.calendar import month_end_flags
from qlab.data import french, panel_from_returns

HI = "Hi PRIOR"
LO = "Lo PRIOR"
TRADING_DAYS = 252
FIRST_SIGNAL = "1930-01-01"
MOM_COST_PER_MONTH = 0.0065          # Novy-Marx/Velikov: 0.65 % pro Monat je Einheit w

# Kalibrierung von cost_bps (pro Seite): bps = 1e4 * 0.0065 * Summe(w_t) / Summe(Handelsvolumen_t / NAV_t)
# mit der Engine bei Basisparametern im Auswahlzeitraum 1930-2022 (Holdout nie beruehrt; nur Volumen und
# Gewichte, keine Renditen-Kennzahl). Reproduzierbar mit `implied_cost_bps(panel.truncate("2022-12-31"))`
# = 331.4 bps, auf 5 bps gerundet. Die Varianten liegen bei 319 (Ziel 19 %), 359 (statisch) und 400 (Deckel 1.0)
# bps, d. h. der feste Wert belastet jede Variante mit 0.54-0.67 % statt exakt 0.65 % pro Monat und w.
CALIBRATED_COST_BPS = 330.0

SPEC = {
    "id": "wml_volscaled_ff",
    "name": "Vol-skaliertes US-Aktien-Momentum (WML, Ken French, Barroso/Santa-Clara)",
    "family": "xsmom",
    "tickers": ["French:10_Portfolios_Prior_12_2_Daily", "French:F-F_Research_Data_Factors_daily"],
    "start": FIRST_SIGNAL,           # Testbeginn; Daten ab 1926-11 dienen nur als Vorlauf
    "sources": [
        "Barroso, Santa-Clara 2015, Momentum has its moments, JFE, https://ciencia.ucp.pt/en/publications/momentum-has-its-moments/",
        "Daniel, Moskowitz 2016, Momentum Crashes, JFE, https://www.nber.org/papers/w20439",
        "Cederburg, O'Doherty, Wang, Yan 2020, On the performance of volatility-managed portfolios, https://www.lehigh.edu/~xuy219/research/COWY.pdf",
        "Novy-Marx, Velikov 2016, A Taxonomy of Anomalies and Their Trading Costs (Momentum-Kosten 0.65 %/Monat)",
    ],
    "params": {"vol_target": 0.12, "lookback": 126, "cap": 2.0, "scale": True, "first_signal": FIRST_SIGNAL},
    "variants": {
        "static_w1": {"scale": False},          # Kontrolle (Pflicht): w = 1
        "vol_target_19": {"vol_target": 0.19},  # Daniel/Moskowitz
        "cap_1": {"cap": 1.0},                  # Deckel 1.0 statt 2.0
    },
    "cost_bps": {HI: CALIBRATED_COST_BPS, LO: CALIBRATED_COST_BPS},
}


def load():
    """Panel aus den French-Tagesrenditen (value-weighted, Tabelle 0). Nicht abgeschnitten: das macht der Harness."""
    df = french("10_Portfolios_Prior_12_2_Daily", table=0)
    ret = df[[HI, LO]].astype(float)
    return panel_from_returns(ret)


def weights(panel, vol_target: float = 0.12, lookback: int = 126, cap: float = 2.0, scale: bool = True,
            first_signal: str = FIRST_SIGNAL) -> pd.DataFrame:
    """Zielgewichte (+w Hi PRIOR, -w Lo PRIOR) an jedem Monatsende-Handelstag, nur aus Daten <= t.

    scale=False: statisches w = 1 (Kontrolle), gleiche Signaltage wie die skalierte Variante.
    Keine Zeile, wenn eine der beiden Reihen am Signaltag keinen Kurs hat oder keine 126 gueltigen
    WML-Tagesrenditen im Fenster liegen (NaN = nicht handelbar).
    """
    px = panel.close[[HI, LO]]
    idx = px.index
    prev = px.shift(1)
    ret = px / prev - 1.0                                      # erste Zeile und Luecken -> NaN
    wml = ret[HI] - ret[LO]
    sigma = wml.rolling(lookback, min_periods=lookback).std(ddof=1) * np.sqrt(TRADING_DAYS)

    flags = month_end_flags(idx).to_numpy()                     # kausal, nicht aus den Daten abgeleitet
    sig = sigma.to_numpy(dtype=float)
    priced = px.notna().all(axis=1).to_numpy()
    with np.errstate(invalid="ignore"):
        valid = flags & priced & np.isfinite(sig) & (sig > 0) & (idx >= pd.Timestamp(first_signal))

    if scale:
        with np.errstate(divide="ignore", invalid="ignore"):
            w = np.minimum(vol_target / sig, cap)
    else:
        w = np.ones(len(idx))
    w = w[valid]
    return pd.DataFrame({HI: w, LO: -w}, index=idx[valid])


def implied_cost_bps(panel, **params) -> float:
    """bps pro Seite, bei denen die Engine im Mittel MOM_COST_PER_MONTH * w pro Signalmonat belastet.

    Nur Handelsvolumen und Gewichte gehen ein (keine Renditen-Kennzahl): zero-cost-Lauf der Engine,
    bps = 1e4 * 0.0065 * Summe(w) / Summe(Volumen/NAV).
    """
    from qlab.engine import CostModel, run_backtest

    w = weights(panel, **params)
    zero = CostModel(default_bps=0.0, short_fee_annual=0.0, lever_spread_annual=0.0)
    rf = pd.Series(0.0, index=panel.close.index)
    res = run_backtest(panel, w, cost=zero, rf=rf)
    volume = 2.0 * float(res.turnover.sum())                    # turnover ist einseitig: Volumen/NAV = 2 * turnover
    if volume <= 0:
        return float("nan")
    return 1e4 * MOM_COST_PER_MONTH * float(w[HI].sum()) / volume
