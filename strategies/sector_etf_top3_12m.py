"""Faber-Sektorrotation (Relative Strength): Top 3 von 10 US-Branchen nach 12-Monats-Rendite.

LANGZEIT-CHECK (nicht handelbar) auf Ken-French-Daten ab 1926-07. Die handelbare ETF-Fassung
(9 SPDR-Sektor-ETFs ab 1998-12) steht in `sector_etf_top3_12m_etf.py` und nutzt dieselbe Regel
(`rotation_weights` aus diesem Modul).

Quellen: Faber 2010, "Relative Strength Strategies for Investing" (SSRN 1585517);
Quantpedia, "Sector Momentum - Rotational System"; verwandt: Moskowitz/Grinblatt 1999.

Regel (aus der Spezifikation, nichts davon ist optimiert):
  Signaltag t = letzter Handelstag des Monats (qlab.calendar.month_end_flags, kausal).
  score_i = Kurs_i[t] / Kurs_i[t12] - 1, t12 = Monatsende 12 Monate vorher (kein Skip-Monat).
  Rang absteigend nach score, Gleichstand alphabetisch nach Name.
  Ziel: Top 3 je 1/3, Rest 0. Voll investiert, kein Hebel, keine Leerverkäufe, kein Cash-Filter in der Basis.
  Die Engine handelt zur Eröffnung von t+1 (hier: Folgetag-Schlusskurs, weil open == close) und hält bis
  zum nächsten Signaltag. Kosten und Steuern bucht die Engine.

Vorab festgelegte Varianten (max. 3, zählen als Versuche):
  combo       : score = Mittel der Renditen über 1, 3, 6, 9, 12 Monate (Fabers "Kombination").
  sma10       : Basis-Signal, aber alles Cash, wenn der Markt am Signaltag unter dem Mittel seiner letzten
                10 Monatsend-Schlusskurse (inkl. t) liegt. Hier ist der Markt der US-Gesamtmarkt (French,
                Mkt-RF + RF); in der ETF-Fassung SPY.
  hold_buffer : Basis, aber ein gehaltener Titel bleibt, solange sein Rang <= 5; auffüllen bis 3 mit den
                bestplatzierten.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from qlab.calendar import month_end_flags
from qlab.data import french, panel_from_returns

# French "10 Industry Portfolios" (Faber-Anhang), value-weighted, tägliche Total-Return-Reihen.
INDUSTRIES = ["NoDur", "Durbl", "Manuf", "Enrgy", "HiTec", "Telcm", "Shops", "Hlth", "Utils", "Other"]
MARKET = "MKT"                     # US-Gesamtmarkt (Mkt-RF + RF), nur Signalquelle für die sma10-Variante
COMBO_MONTHS = (1, 3, 6, 9, 12)    # Fabers "Kombination"

SPEC = {
    "id": "sector_etf_top3_12m",
    "name": "Faber-Sektorrotation Langzeit-Check (Top 3 von 10 French-Industrien, 12-Monats-Rendite)",
    "family": "xsmom",
    "tickers": INDUSTRIES + [MARKET],
    "start": "1926-07-01",
    "sources": [
        "Faber 2010, Relative Strength Strategies for Investing, SSRN 1585517",
        "Quantpedia, Sector Momentum - Rotational System, https://quantpedia.com/strategies/sector-momentum-rotational-system",
        "Ken French Data Library, 10_Industry_Portfolios_daily (value-weighted)",
    ],
    "params": {"lookback_months": 12, "top_n": 3, "combo": False, "cash_filter_months": 0, "hold_rank": 0},
    "variants": {
        "combo": {"combo": True},
        "sma10": {"cash_filter_months": 10},
        "hold_buffer": {"hold_rank": 5},
    },
}


# --------------------------------------------------------------------------------------
# Kern (wird von der ETF-Fassung wiederverwendet)
# --------------------------------------------------------------------------------------

def _prior_month_end(me: pd.DataFrame, k: int) -> pd.DataFrame:
    """Kurs am Monatsende k Monate zuvor, über den Monat zugeordnet (robust gegen Datenlücken -> NaN)."""
    per = me.index.to_period("M")
    tmp = me.copy()
    tmp.index = per
    prior = tmp.reindex(per - k)
    prior.index = me.index
    return prior


def _scores(me: pd.DataFrame, lookback_months: int, combo: bool) -> pd.DataFrame:
    """Momentum-Score je Monatsende; NaN, wenn irgendein benötigter Kurs fehlt."""
    ks = COMBO_MONTHS if combo else (lookback_months,)
    parts = [me / _prior_month_end(me, k) - 1.0 for k in ks]
    sc = sum(parts) / len(parts)
    return sc.replace([np.inf, -np.inf], np.nan)


def _select(score_row: np.ndarray, top_n: int, hold_rank: int, held: list[int]) -> list[int]:
    """Indizes der gewählten Titel. Spalten sind alphabetisch sortiert, ein stabiles Sortieren nach
    -score löst Gleichstände daher alphabetisch auf."""
    ok = np.flatnonzero(np.isfinite(score_row))
    order = ok[np.argsort(-score_row[ok], kind="stable")]
    rank = {int(j): r + 1 for r, j in enumerate(order)}
    chosen: list[int] = []
    if hold_rank:
        keep = [j for j in held if j in rank and rank[j] <= hold_rank]
        keep.sort(key=lambda j: rank[j])
        chosen = keep[:top_n]
    for j in order:
        if len(chosen) >= top_n:
            break
        if int(j) not in chosen:
            chosen.append(int(j))
    return chosen


def rotation_weights(close: pd.DataFrame, universe: list[str], filter_close: pd.Series | None = None,
                     lookback_months: int = 12, top_n: int = 3, combo: bool = False,
                     cash_filter_months: int = 0, hold_rank: int = 0) -> pd.DataFrame:
    """Zielgewichte der Sektorrotation. Nutzt nur Kurse bis einschließlich des Signaltags (Monatsende).

    Zeilen = Signaltage (Monatsenden). Titel ohne gültigen Kurs (noch nicht gelistet / Lücke) haben keinen
    Score und werden nicht gewählt; gibt es weniger als `top_n` bewertbare Titel, entsteht kein Signal.
    Eine Zeile aus lauter Nullen (sma10-Variante, Markt unter Durchschnitt) bedeutet: alles in Cash.
    """
    if top_n < 1 or lookback_months < 1 or hold_rank < 0 or cash_filter_months < 0:
        raise ValueError("ungültige Parameter")
    if hold_rank and hold_rank < top_n:
        raise ValueError("hold_rank muss >= top_n sein")
    names = sorted(universe)
    missing = [t for t in names if t not in close.columns]
    if missing:
        raise KeyError(f"Universum unvollständig im Panel: {missing}")
    if cash_filter_months and filter_close is None:
        raise KeyError("cash_filter_months > 0 braucht die Marktreihe (filter_close)")

    px = close[names]
    flags = month_end_flags(px.index).to_numpy()
    me = px[flags]                                          # nur kausal erkannte Monatsenden
    if len(me) == 0:
        return pd.DataFrame(columns=names, dtype=float)
    sc = _scores(me, lookback_months, combo).to_numpy(float)
    dates = me.index

    if cash_filter_months:
        fme = filter_close.reindex(px.index)[flags]
        f_arr = fme.to_numpy(float)
        sma_arr = fme.rolling(cash_filter_months).mean().to_numpy(float)     # inkl. aktuellem Monatsende

    m = len(names)
    rows, out_dates = [], []
    held: list[int] = []
    for k in range(len(dates)):
        if int(np.isfinite(sc[k]).sum()) < top_n:
            continue                                        # zu wenig bewertbare Titel: nichts tun
        if cash_filter_months:
            if not (np.isfinite(f_arr[k]) and np.isfinite(sma_arr[k])):
                continue                                    # Marktfilter noch ohne Historie: kein Signal
            if f_arr[k] < sma_arr[k]:
                rows.append(np.zeros(m))
                out_dates.append(dates[k])
                held = []
                continue
        chosen = _select(sc[k], top_n, hold_rank, held)
        w = np.zeros(m)
        w[chosen] = 1.0 / top_n
        rows.append(w)
        out_dates.append(dates[k])
        held = chosen
    if not rows:
        return pd.DataFrame(columns=names, dtype=float)
    return pd.DataFrame(np.vstack(rows), index=pd.DatetimeIndex(out_dates), columns=names)


# --------------------------------------------------------------------------------------
# Strategie-Schnittstelle (Langzeit-Check auf French-Daten)
# --------------------------------------------------------------------------------------

def weights(panel, **params) -> pd.DataFrame:
    p = {**SPEC["params"], **params}
    filt = panel.close[MARKET] if p["cash_filter_months"] else None
    return rotation_weights(panel.close, INDUSTRIES, filter_close=filt, **p)


def build_panel(industries: pd.DataFrame, market: pd.Series):
    """Panel aus täglichen Renditen der Industrien plus Markt (rein, ohne Netz; testbar)."""
    ret = industries[INDUSTRIES].join(market.rename(MARKET), how="outer")
    return panel_from_returns(ret)


def load():
    """French-Daten laden (Cache/Netz). Nicht abgeschnitten: der Harness schneidet bei 2022-12-31 ab."""
    ind = french("10_Industry_Portfolios_daily", table=0)
    f = french("F-F_Research_Data_Factors", daily=True)
    return build_panel(ind, f["Mkt-RF"] + f["RF"])
