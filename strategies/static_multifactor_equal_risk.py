"""Statische Multi-Faktor-Kombination (HML, RMW, CMA, Mom) mit Inverse-Vol-Gewichten auf Ken-French-Faktoren.

Quellen: Jensen, Kelly, Pedersen 2023 ("Is There a Replication Crisis in Finance?", JoF); Hou, Xue, Zhang 2020
("Replicating Anomalies", RFS). Regeln aus research/strategie-kandidaten.json (Eintrag
static_multifactor_equal_risk) und research/families/factors.md, Abschnitt 3.1.

Regel (Spezifikation, unveraendert uebernommen; Parameter aus der Quelle, keine Optimierung):
    Monatsrenditen f_i der Long-Short-Faktoren i in {HML, RMW, CMA, Mom} (Ueberrenditen, zero-cost).
    Am letzten Handelstag t jedes Monats (qlab.calendar.month_end_flags, kausal), nur Daten bis t:
        vol_i = std(f_i, Monate t-35..t, ddof=1) * sqrt(12)              # mind. 24 Beobachtungen
        w_i   = (1 / vol_i) / sum_k (1 / vol_k)                           # Summe w = 1
        port_vol = sqrt(w' Cov36M w) * sqrt(12)                           # Cov aus denselben 36 Monaten
        lev   = min(2.0, 0.10 / port_vol)                                 # Ziel-Vol 10 % p.a., Deckel 2.0
        Ziel  = lev * w_i auf Faktor i (nur Long, Brutto-Exposure = lev <= 2)
    Spezifikations-Rendite des Folgemonats (Referenz, siehe `reference_monthly_returns`):
        R = lev * sum_i w_i f_i,t+1 - 2 % / 12 - (lev > 1 ? (lev - 1) * (RF + 0.005 / 12) : 0)
    Erster Test-Monat 1966-07 (36 Monate Historie ab 1963-07): erstes Signal am 1966-06-30.

Umsetzung im Engine-Vertrag (Abweichungen von der Spezifikation: siehe unten und deviations_from_spec):
* Daten: Ken-French-TAGESdaten (F-F_Research_Data_5_Factors_2x3_daily + F-F_Momentum_Factor_daily, beide ab
  1963-07-01). Der Harness rechnet mit Tagesrenditen und 252 Tagen/Jahr, eine Monatsreihe waere dort nicht
  handhabbar. Die Monatsrenditen der Spezifikation werden in `weights` KAUSAL aus den Tagesrenditen
  zusammengesetzt: f_Monat = Produkt(1 + f_Tag) ueber alle Handelstage des Kalendermonats. Der Monat des
  Signaltags t ist vollstaendig, weil t der (kausal erkannte) letzte Handelstag ist. Ein Monat mit auch nur
  einem fehlenden Tageswert gilt als fehlend (NaN). Gegenprobe gegen die French-Monatsdateien (1963-08 bis
  2026-08): Korrelation 0.996-0.997 (HML/RMW/CMA), 0.971 (Mom; die Tages- und Monatsreihe von French
  unterscheiden sich beim Momentum nennenswert).
* Panel (`load()`): 4 Faktor-Spalten als TOTAL-RETURN-Reihen (f_i + RF_Tag, ueber `panel_from_returns`,
  open == close) plus eine Spalte "RF" (nur Lieferant des Tages-RF fuer die Signalberechnung; nie ein Gewicht).
  Begruendung: Die French-Faktoren sind selbstfinanzierende Ueberrenditen. Die Engine verbucht Cash (1 - lev)
  zum RF; haelt man Faktor + RF-Total-Return mit Gewicht lev, ist die Engine-Rendite lev * sum(w f) + RF und die
  Ueberrendite zum RF (Sharpe im Harness) genau lev * sum(w f) wie in der Spezifikation. Aus den Panel-Preisen
  rekonstruiert `weights` den Faktor als f_i = Rendite_i - Rendite_RF (exakt, additiv).
* Ein Signal am Schluss von t wird zum Schlusskurs von t+1 gehandelt (open == close) und verdient ab t+2. Die
  Spezifikation verdient ab t+1 mit konstanten Gewichten ueber den Monat; hier driften die Positionen zwischen
  den Rebalancings (Engine: Buy&Hold bis zum naechsten Signal). Bekannte, bewusst akzeptierte Naeherung.
* Finanzierung: Hebel (lev > 1) finanziert die Engine mit RF + 1.5 % auf den Kredit (lev - 1). Netto verbleibt
  also (lev - 1) * 1.5 % Abzug auf die Ueberrendite. Die Spezifikation zieht dagegen (lev - 1) * (RF + 0.5 %)
  von der Ueberrendite ab (der RF-Anteil ist dort eine zusaetzliche, konservative Zaehlung). Die Engine ist
  damit in Zeiten hoher Zinsen MILDER als die Spezifikation. Die spezifikationsgetreue Monatsrechnung liefert
  `reference_monthly_returns` (reine Monatsdaten, ohne Engine) fuer die Abbruchkriterien.
* Haircut 2 % p.a. (Kosten-/Verfallspauschale, pauschal, nicht hebelabhaengig): Er laesst sich in der Engine nur
  ueber Handelskosten abbilden. `cost_bps` (pro Seite, auf alle vier Faktoren) ist so kalibriert, dass die
  Engine bei den tatsaechlichen Monats-Rebalancings im Auswahlzeitraum bis 2022-12-31 im Mittel 2 % p.a. belastet
  (siehe `implied_cost_bps`, nur Handelsvolumen und Gewichte, keine Renditen). Die Haircut-Sensitivitaeten der
  Spezifikation (0 % und 4 %) sind keine Gewichtsvarianten, sondern Kosten-Laeufe: `run_all.py --cost-mult 0`
  bzw. `--cost-mult 2` (Standardkosten der Engine entfallen dort, weil alle vier Spalten ueberschrieben sind).
  Dort fallen die Engine-Finanzierungskosten unveraendert an.

Varianten (vorab festgelegt, zaehlen als Versuche; Robustheits-Check, keine Auswahl der besten):
    equal_weight  1/N-Gewichte (w_i = 1/4) statt Inverse-Vol; Hebel-Formel (Ziel-Vol 10 %, Deckel 2.0)
                  unveraendert auf Basis der 1/N-Portfolio-Vol. Pflichtvergleich (a) der Spezifikation.
Steuern verbucht die Engine (TaxModel). Nicht direkt handelbar (Long-Short-Faktoren): Forschungs-Bewertung.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from qlab.calendar import month_end_flags
from qlab.data import Panel, french, panel_from_returns

FACTORS = ["HML", "RMW", "CMA", "Mom"]
RF_COL = "RF"
FIRST_SIGNAL = "1966-06-01"           # Spezifikation: "Start 1966-07 (36 Monate)"; erstes Signal 1966-06-30
HAIRCUT = 0.02                        # Spezifikation: 2 % p.a. Kosten-/Verfallspauschale
LEVER_SPREAD = 0.005                  # Spezifikation: Hebel kostet RF + 0.5 % p.a. (nur in der Referenzrechnung)

# Kalibrierung von cost_bps (pro Seite): bps = 1e4 * HAIRCUT * Jahre / Summe(Handelsvolumen_t / NAV_t) mit der
# Engine bei Basisparametern im Auswahlzeitraum 1966-06 bis 2022-12-31 (Null-Kosten-Lauf, Cash-Zins 0; nur
# Volumen und Gewichte, keine Renditen-Kennzahl; Holdout nie beruehrt). Reproduzierbar mit
# `implied_cost_bps(load().truncate("2022-12-31"))` = 292.5 bps, auf 292 gerundet. Mit dem festen Wert belastet die
# Engine die Basisvariante im Mittel mit 1.98 % p.a., die Variante equal_weight (weniger Umschlag) mit 1.64 % p.a.
# statt 2 %. Der Umschlag ist niedrig (ca. 0.34 pro Jahr einseitig), der Einstiegskauf (Volumen ca. 2 x NAV) kostet
# einmalig 5.8 % des Start-NAV.
CALIBRATED_COST_BPS = 292.0

SPEC = {
    "id": "static_multifactor_equal_risk",
    "name": "Statische Multi-Faktor-Kombination (HML, RMW, CMA, Mom), Inverse-Vol + Ziel-Vol 10 %, Ken French",
    "family": "factors",
    "tickers": ["French:HML", "French:RMW", "French:CMA", "French:Mom", "French:RF"],   # Spalten des Panels aus load()
    "start": FIRST_SIGNAL,            # Testbeginn; Daten ab 1963-07 dienen nur als Vorlauf (36 Monate)
    "sources": [
        "Jensen, Kelly, Pedersen 2023, Is There a Replication Crisis in Finance?, https://www.nber.org/papers/w28432",
        "Hou, Xue, Zhang 2020, Replicating Anomalies, https://www.nber.org/papers/w23394",
    ],
    "params": {"window": 36, "min_obs": 24, "target_vol": 0.10, "cap": 2.0, "inverse_vol": True,
               "first_signal": FIRST_SIGNAL},
    "variants": {
        "equal_weight": {"inverse_vol": False},     # 1/N statt Inverse-Vol (Pflichtvergleich der Spezifikation)
    },
    "cost_bps": {f: CALIBRATED_COST_BPS for f in FACTORS},
}


# --------------------------------------------------------------------------------------
# Daten
# --------------------------------------------------------------------------------------

def load() -> Panel:
    """Panel aus den French-Tagesdaten: HML/RMW/CMA/Mom als Total-Return-Reihen (f + RF) plus RF-Spalte.

    Nicht abgeschnitten: das macht der Harness. Beide Tagesdateien beginnen am 1963-07-01 (innerer Join).
    """
    d5 = french("F-F_Research_Data_5_Factors_2x3", daily=True)
    mom = french("F-F_Momentum_Factor", daily=True)
    df = pd.concat([d5[["HML", "RMW", "CMA", "RF"]], mom[["Mom"]]], axis=1, join="inner").astype(float)
    rf = df["RF"]
    ret = pd.DataFrame({f: df[f] + rf for f in FACTORS})
    ret[RF_COL] = rf
    return panel_from_returns(ret[FACTORS + [RF_COL]])


# --------------------------------------------------------------------------------------
# Kern
# --------------------------------------------------------------------------------------

def monthly_factor_returns(close: pd.DataFrame) -> pd.DataFrame:
    """Kalendermonats-Renditen der Ueberrenditen f_i aus Total-Return-Kursen (Faktor-Spalten + RF-Spalte).

    Index = lueckenlose Monats-PeriodIndex von der ersten bis zur letzten Datenzeile. Ein Monat ist NaN, wenn
    an einem seiner Handelstage eine Rendite fehlt (inkl. erste Datenzeile: keine Vortagsrendite). Der letzte
    Monat der Daten kann unvollstaendig sein; er wird von `weights` nur an einem kausal erkannten Monatsende
    verwendet, an dem er vollstaendig ist.
    """
    ret = close / close.shift(1) - 1.0                                   # NaN bei fehlendem Kurs oder erster Zeile
    f = ret[FACTORS].sub(ret[RF_COL], axis=0)
    per = f.index.to_period("M")
    comp = (1.0 + f.fillna(0.0)).groupby(per).prod() - 1.0
    bad = f.isna().groupby(per).sum() > 0
    out = comp.mask(bad)
    return out.reindex(pd.period_range(out.index.min(), out.index.max(), freq="M"))


def _signal(win: np.ndarray, target_vol: float, cap: float, inverse_vol: bool, min_obs: int):
    """(w, lev) aus einem Monatsfenster (Zeilen = Monate, Spalten = Faktoren); None bei zu wenig/degenerierten Daten.

    Es zaehlen nur Monate, in denen ALLE Faktoren vorliegen (Cov und Vol aus denselben Beobachtungen).
    """
    rows = win[~np.isnan(win).any(axis=1)]
    if len(rows) < min_obs:
        return None
    cov = np.atleast_2d(np.cov(rows, rowvar=False, ddof=1))
    vol = np.sqrt(np.diag(cov)) * np.sqrt(12.0)
    if not (np.all(np.isfinite(vol)) and np.all(vol > 0)):
        return None
    if inverse_vol:
        inv = 1.0 / vol
        w = inv / inv.sum()
    else:
        w = np.full(len(vol), 1.0 / len(vol))
    port_vol = float(np.sqrt(w @ cov @ w) * np.sqrt(12.0))
    if not (np.isfinite(port_vol) and port_vol > 0):
        return None
    return w, min(cap, target_vol / port_vol)


def weights(panel, window: int = 36, min_obs: int = 24, target_vol: float = 0.10, cap: float = 2.0,
            inverse_vol: bool = True, first_signal: str = FIRST_SIGNAL) -> pd.DataFrame:
    """Zielgewichte lev * w_i auf HML/RMW/CMA/Mom an jedem Monatsende-Handelstag, nur aus Daten <= t.

    Keine Zeile, wenn an t ein Kurs fehlt, der laufende Monat unvollstaendig ist oder im 36-Monats-Fenster
    weniger als `min_obs` vollstaendige Monate liegen (NaN = nicht handelbar). Das Fenster umfasst die Monate
    t-35..t (inkl. des Monats von t); frueheste Zeile nach 24 vollstaendigen Monaten bzw. `first_signal`.
    """
    px = panel.close[FACTORS + [RF_COL]]
    idx = px.index
    cols = list(FACTORS)
    if len(idx) < 3:
        return pd.DataFrame(columns=cols, index=pd.DatetimeIndex([]), dtype=float)

    monthly = monthly_factor_returns(px)
    mvals = monthly.to_numpy(dtype=float)
    m0 = monthly.index[0].year * 12 + monthly.index[0].month
    flags = month_end_flags(idx).to_numpy()                              # kausal, nicht aus den Daten abgeleitet
    priced = px.notna().all(axis=1).to_numpy()
    first_ts = pd.Timestamp(first_signal) if first_signal is not None else None
    mpos = idx.year.to_numpy() * 12 + idx.month.to_numpy() - m0

    dates, rows = [], []
    for i in np.flatnonzero(flags & priced):
        if first_ts is not None and idx[i] < first_ts:
            continue
        k = int(mpos[i])
        if np.isnan(mvals[k]).any():                                     # laufender Monat unvollstaendig
            continue
        win = mvals[max(0, k - window + 1):k + 1]
        sig = _signal(win, target_vol, cap, inverse_vol, min_obs)
        if sig is None:
            continue
        w, lev = sig
        dates.append(idx[i])
        rows.append(lev * w)
    if not rows:
        return pd.DataFrame(columns=cols, index=pd.DatetimeIndex([]), dtype=float)
    return pd.DataFrame(np.vstack(rows), index=pd.DatetimeIndex(dates), columns=cols)


# --------------------------------------------------------------------------------------
# Referenz (Spezifikation auf reinen Monatsdaten, ohne Engine) und Kosten-Kalibrierung
# --------------------------------------------------------------------------------------

def reference_monthly_returns(factors: pd.DataFrame, rf: pd.Series, window: int = 36, min_obs: int = 24,
                              target_vol: float = 0.10, cap: float = 2.0, inverse_vol: bool = True,
                              haircut: float = HAIRCUT, first_month=None) -> pd.DataFrame:
    """Netto-Monatsrenditen der Spezifikation, woertlich: R = lev * sum(w f_t+1) - haircut/12 - Hebelkosten.

    factors: Monatsrenditen (Spalten HML, RMW, CMA, Mom), rf: Monats-RF (Dezimal), gleicher Index (Monate in
    Reihenfolge). Gewichte aus den Monaten t-window+1..t, Rendite im Monat t+1 (Index der Ergebnisse = Monat t+1).
    Spalten: lev, gross (lev * sum w f), net (nach Haircut und Hebelkosten (lev-1)*(RF + 0.005/12) bei lev > 1).
    Reine Rechenhilfe fuer die Abbruchkriterien (Netto-Sharpe, t-Statistik); der Harness nutzt sie nicht.
    """
    f = factors[FACTORS]
    out_idx, out = [], []
    for k in range(len(f) - 1):
        if first_month is not None and f.index[k] < pd.Period(first_month, freq="M"):
            continue
        sig = _signal(f.iloc[max(0, k - window + 1):k + 1].to_numpy(dtype=float), target_vol, cap, inverse_vol, min_obs)
        if sig is None:
            continue
        w, lev = sig
        nxt = f.iloc[k + 1].to_numpy(dtype=float)
        if np.isnan(nxt).any() or not np.isfinite(rf.iloc[k + 1]):
            continue
        gross = lev * float(w @ nxt)
        cost = haircut / 12.0 + ((lev - 1.0) * (float(rf.iloc[k + 1]) + LEVER_SPREAD / 12.0) if lev > 1.0 else 0.0)
        out_idx.append(f.index[k + 1])
        out.append((lev, gross, gross - cost))
    return pd.DataFrame(out, index=pd.Index(out_idx), columns=["lev", "gross", "net"])


def implied_cost_bps(panel, haircut: float = HAIRCUT, **params) -> float:
    """bps pro Seite, bei denen die Engine im Mittel `haircut` pro Jahr belastet (Handelsvolumen-basiert).

    Nur Handelsvolumen und Gewichte gehen ein (keine Renditen-Kennzahl): Null-Kosten-Lauf der Engine,
    bps = 1e4 * haircut * Jahre / Summe(Volumen/NAV) mit Jahre = (letzter Handelstag - erstes Signal) / 365.25.
    """
    from qlab.engine import CostModel, run_backtest

    w = weights(panel, **params)
    if len(w) == 0:
        return float("nan")
    zero = CostModel(default_bps=0.0, short_fee_annual=0.0, lever_spread_annual=0.0)
    res = run_backtest(panel, w, cost=zero, rf=pd.Series(0.0, index=panel.close.index))
    volume = 2.0 * float(res.turnover.sum())                             # turnover ist einseitig
    years = (panel.close.index[-1] - w.index[0]).days / 365.25
    if volume <= 0 or years <= 0:
        return float("nan")
    return 1e4 * haircut * years / volume
