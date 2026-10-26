"""Keller/Keuning (2016) Protective Asset Allocation (PAA), Universum G12, Breadth-Schutz.

Quelle: Wouter J. Keller, Jan Willem Keuning, "Protective Asset Allocation (PAA): A Simple Momentum-Based
Alternative for Term Deposits", SSRN 2759734 (2016); Notation und G12-Universum wie im BAA-Papier
(Keller 2022, SSRN 4166845, Fig. 1), siehe research/families/tactical.md, Abschnitt 3.2.

Regel (Spezifikation research/strategie-kandidaten.json, id keller_paa_g12):
* Offensiv O = SPY, QQQ, IWM, VGK, EWJ, VWO, VNQ, DBC, GLD, TLT, HYG, LQD (12). Defensiv D = BIL, IEF.
* Am Schlusskurs des letzten Handelstags t des Monats, je Asset i aus O und D:
      m_i = P_i(t) / mean(P_i(t), P_i(t-1M), ..., P_i(t-12M)) - 1      (13 angepasste Monatsend-Schlusskurse)
* b  = Anzahl Assets in O mit m_i < 0.   CF = min(1, b / B)   mit B = 6.
* Offensivanteil (1 - CF) gleichgewichtet auf die 6 Assets aus O mit dem höchsten m_i (rein relatives
  Momentum, unabhängig vom Vorzeichen). Defensivanteil CF komplett in das Asset aus {BIL, IEF} mit dem höheren m.
* Monatlich komplett neu gewichten. Summe der Zielgewichte = 1 (kein Hebel, kein Short).

Ausführung, Kosten und Steuern verbucht die Engine (Signal am Schluss t, Handel t+1). Die Strategie liefert
nur Zielgewichte.

Varianten (vorab festgelegt, laut Spezifikation "sensitivity_variants"):
* top4      : Top 4 statt Top 6.
* breadth4  : Breadth-Schwelle B = 4 (CF = min(1, b/4)).
* sleeves3  : drei gestaffelte Sleeves mit Stichtagen 14 / 7 / 0 Handelstage vor dem Monatsende, je 1/3 des
              Kapitals. Das Zielgewicht an einem Stichtag ist der Mittelwert der zuletzt berechneten
              Sleeve-Zielgewichte (das neu berechnete Sleeve plus die beiden anderen auf ihrem Stand).
              Der Handel startet erst, wenn alle drei Sleeves ihr erstes Signal haben.

Kausalität: Alle Größen am Tag t nutzen nur Kurse bis einschließlich t. Monatsenden kommen aus
qlab.calendar.month_end_flags. Die Sleeve-Stichtage 14 und 7 Handelstage vor Monatsende werden aus dem
NYSE-Kalender (nicht aus den Kursdaten) bestimmt; ob ein Tag im Index liegt, entscheidet nur, ob er
ein Signal bekommt. Die 12 Vor-Monatsend-Kurse sind immer strikt vor t.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from qlab.calendar import NYSE_BDAY, month_end_flags

OFFENSIVE = ["SPY", "QQQ", "IWM", "VGK", "EWJ", "VWO", "VNQ", "DBC", "GLD", "TLT", "HYG", "LQD"]
DEFENSIVE = ["BIL", "IEF"]
ALL = OFFENSIVE + DEFENSIVE

HISTORY_MONTHS = 12       # P(t-1M) ... P(t-12M), zusammen mit P(t) = 13 Kurse
FFILL_LIMIT = 5           # kurze Datenlücken (Tage) im Monatsend-Kurs überbrücken, nie länger

SPEC = {
    "id": "keller_paa_g12",
    "name": "Keller PAA G12 (Breadth-Schutz, SMA12, Top 6 von 12)",
    "family": "tactical",
    "tickers": ALL,
    "start": "2007-05-01",    # BIL startet 2007-05-30; erstes Signal frühestens 2008-05-30 (13 Monatsenden)
    "sources": [
        "Keller & Keuning 2016, Protective Asset Allocation (PAA), SSRN 2759734, "
        "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2759734",
        "Keller 2022, Bold Asset Allocation (BAA), SSRN 4166845 (Notation G12, SMA13, Fig. 1)",
    ],
    "params": {"top_n": 6, "breadth": 6, "sleeve_offsets": (0,)},
    "variants": {
        "top4": {"top_n": 4},
        "breadth4": {"breadth": 4},
        "sleeves3": {"sleeve_offsets": (14, 7, 0)},
    },
    # Spezifikation: 10 bp je Seite (Stress 5/20 bp über --cost-mult)
    "cost_bps": {t: 10.0 for t in ALL},
}


def _calendar_month_ends(first: pd.Timestamp, last: pd.Timestamp) -> list[pd.Timestamp]:
    """Letzter NYSE-Handelstag jedes Monats zwischen first und last, rein aus dem Kalender."""
    months = pd.period_range(first, last, freq="M")
    return [NYSE_BDAY.rollback(p.end_time.normalize()) for p in months]


def _signal_dates(idx: pd.DatetimeIndex, offset: int) -> pd.DatetimeIndex:
    """Stichtage im Index: `offset` NYSE-Handelstage vor dem Monatsende (0 = letzter Handelstag)."""
    if offset == 0:
        return idx[month_end_flags(idx).to_numpy()]
    if offset < 0:
        raise ValueError("sleeve_offsets müssen >= 0 sein")
    targets = [d - offset * NYSE_BDAY for d in _calendar_month_ends(idx[0], idx[-1])]
    return idx[idx.isin(pd.DatetimeIndex(targets))]


def _sleeve_targets(px: pd.DataFrame, pxf: pd.DataFrame, me: pd.DataFrame, dates: pd.DatetimeIndex,
                    top_n: int, breadth: float) -> pd.DataFrame:
    """Zielgewichte des Sleeves an den Stichtagen `dates` (nur Tage mit kompletter, gültiger Historie)."""
    n_off = len(OFFENSIVE)
    me_arr = me.to_numpy(float)
    n_prev = me.index.searchsorted(dates, side="left")          # Monatsenden strikt vor dem Stichtag
    cur_all = pxf.loc[dates].to_numpy(float)                     # Kurs t (kurze Lücken überbrückt)
    raw_all = px.loc[dates].to_numpy(float)                      # echter Kurs an t: nicht handelbar, wenn NaN
    rows, out_dates = [], []
    for j, t in enumerate(dates):
        k = int(n_prev[j])
        if k < HISTORY_MONTHS:
            continue
        hist = me_arr[k - HISTORY_MONTHS:k]
        cur, raw = cur_all[j], raw_all[j]
        if not (np.isfinite(hist).all() and np.isfinite(cur).all() and np.isfinite(raw).all()):
            continue                                             # fehlender Kurs = nicht handelbar: kein Signal
        sma = (hist.sum(axis=0) + cur) / (HISTORY_MONTHS + 1)
        if not (sma > 0).all():
            continue
        m = cur / sma - 1.0
        m_off, m_def = m[:n_off], m[n_off:]
        b = int((m_off < 0).sum())
        cf = min(1.0, b / float(breadth))
        w = np.zeros(len(ALL))
        best = np.argsort(-m_off, kind="stable")[:top_n]         # Ranking nur innerhalb des Tages (Querschnitt)
        w[best] = (1.0 - cf) / top_n
        w[n_off + int(np.argmax(m_def))] += cf                   # Gleichstand -> BIL (erstes Element)
        rows.append(w)
        out_dates.append(t)
    return pd.DataFrame(np.array(rows).reshape(len(rows), len(ALL)), index=pd.DatetimeIndex(out_dates),
                        columns=ALL, dtype=float)


def weights(panel, top_n: int = 6, breadth: float = 6, sleeve_offsets: tuple = (0,)) -> pd.DataFrame:
    if top_n < 1 or top_n > len(OFFENSIVE):
        raise ValueError("top_n muss zwischen 1 und 12 liegen")
    if breadth <= 0:
        raise ValueError("breadth muss > 0 sein")
    offsets = tuple(sorted(set(int(o) for o in sleeve_offsets), reverse=True))
    if not offsets:
        raise ValueError("mindestens ein Sleeve nötig")

    px = panel.close[ALL]
    idx = px.index
    pxf = px.ffill(limit=FFILL_LIMIT)                            # nur Vergangenheit, nur kurze Lücken
    me = pxf.loc[idx[month_end_flags(idx).to_numpy()]]           # Monatsend-Schlusskurse (kausal erkannt)

    sleeves = [_sleeve_targets(px, pxf, me, _signal_dates(idx, o), int(top_n), float(breadth)) for o in offsets]
    if any(len(s) == 0 for s in sleeves):
        return pd.DataFrame(columns=ALL, dtype=float)
    if len(sleeves) == 1:
        return sleeves[0]

    all_dates = sleeves[0].index
    for s in sleeves[1:]:
        all_dates = all_dates.union(s.index)
    start = max(s.index[0] for s in sleeves)                     # erst handeln, wenn jedes Sleeve ein Signal hat
    all_dates = all_dates[all_dates >= start]
    acc = None
    for s in sleeves:
        cur = s.reindex(s.index.union(all_dates)).ffill().reindex(all_dates)
        acc = cur if acc is None else acc + cur
    return acc / len(sleeves)
