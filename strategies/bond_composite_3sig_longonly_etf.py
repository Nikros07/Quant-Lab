"""Dreier-Komposit Duration-Timing (Carry + Trend + Value) — Live-Test auf den ETFs IEF und SHY (ab 2002-07-30).

Zweites Modul zu `bond_composite_3sig_longonly` (Langzeit-Test 1972-2022 auf der synthetischen 10J-Anleihe):
gleiche Regel, gleiche Signale (die Stimmen werden aus dem Hauptmodul importiert und sind dort getestet),
aber gehandelt werden echte ETFs.

Regel (festgelegt vor dem Backtest, aus research/strategie-kandidaten.json):
    Drei Stimmen am Monatsende t_m (Carry: Terminspread-Perzentil über 2520 Vortage > 1/3; Trend: EWMA 21
    und 252 der synthetischen 10J-Überschussrendite beide > 0; Value: Realzins y10 - pi_e über seinem
    EWMA-Anker mit Halbwertszeit 36 Monate; Details im Hauptmodul).
    w = (v_car + v_trd + v_val) / 3 in IEF (10J-Treasury-ETF), 1-w in SHY (1-3J-Treasury-ETF als Cash-Ersatz,
    laut Spec "ETF-Test IEF/SHY"). Ungehebelt, nie short.

Umsetzung im Engine-Vertrag:
* Die Signale bleiben die SYNTHETISCHEN aus ^TNX/^IRX/CPI (wie im Hauptmodul, ab 1962 gerechnet), nicht die
  ETF-Kurse; die ETFs sind nur die Handelsinstrumente. Das Panel (`load()`) reicht daher bis 1962 zurück und
  enthält IEF/SHY erst ab ihrer Notierung (2002-07-30); davor sind die Kurse NaN = nicht handelbar, und es
  entstehen keine Gewichte. Damit sind die Signale an jedem gemeinsamen Tag identisch zum Hauptmodul.
* Signal am Schluss des letzten Handelstags t_m (month_end_flags, kausal); die Engine handelt zur Eröffnung
  von t_m+1 (Standard-Ausführung aller ETF-Strategien im Lab). Das ist etwas anders als "Schluss t_m+1"
  der Spec (dort wird die synthetische Reihe zum Schluss gehandelt).
* Spalten "^TNX", "^IRX", "PI_E" sind reine Signalquellen in PROZENT, nie ein Gewicht darauf.
* Cash: `cash_asset="SHY"` legt 1-w in SHY an (so die Spec). `cash_asset=None` lässt 1-w als echtes Cash,
  das die Engine mit dem French-RF verzinst. SHY trägt anders als ein Geldmarktfonds etwas Zinsrisiko
  (Duration ca. 2); BIL (Geldmarkt) startet erst 2007-05 und liegt deshalb nicht im Basislauf.
* Der Wechsel von w bewegt sowohl IEF als auch SHY (gehandeltes Volumen 2 * |dw|); Kosten 5 bp je Seite
  (Spec), Stresstest 20 bp über `--cost-mult 4` im Harness.

Varianten (vorab festgelegt, Robustheits-Checks, keine Auswahl der besten):
    only_carry  nur die Carry-Stimme (w = 0 oder 1)
    only_trend  nur die Trend-Stimme (w = 0 oder 1)
    only_value  nur die Value-Stimme (w = 0 oder 1)
"""
from __future__ import annotations

import pandas as pd

from qlab.calendar import month_end_flags
from qlab.data import Panel, load_panel
from strategies.bond_composite_3sig_longonly import (IRX, PIE, SIGNAL_NAMES, TNX, composite, load_signal_inputs,
                                                     signal_columns, votes)

BOND = "IEF"
CASH = "SHY"

SPEC = {
    "id": "bond_composite_3sig_longonly_etf",
    "name": "Dreier-Komposit Duration-Timing (Carry+Trend+Value), Live-Test auf IEF/SHY",
    "family": "gap_bonds_duration_curve_carry_mom_value",
    "tickers": [BOND, CASH, TNX, IRX, PIE],     # Spalten des Panels aus load(); IEF/SHY aus Yahoo, Rest Signalquellen
    "start": "2002-07-30",                       # IEF/SHY-Start; die Signalhistorie reicht im Panel bis 1962
    "sources": [
        "Newfound Research 2018, Timing Bonds with Value, Momentum, and Carry, "
        "https://blog.thinknewfound.com/2018/01/timing-bonds-value-momentum-carry/",
        "Newfound Research 2017, Duration Timing with Style Premia, "
        "https://blog.thinknewfound.com/2017/06/duration-timing-style-premia/",
    ],
    "params": {
        "signals": SIGNAL_NAMES,
        "carry_window": 2520,
        "carry_threshold": 1 / 3,
        "ewma_fast": 21,
        "ewma_slow": 252,
        "anchor_halflife": 36,
        "bond_asset": BOND,
        "cash_asset": CASH,
    },
    "variants": {
        "only_carry": {"signals": ("carry",)},
        "only_trend": {"signals": ("trend",)},
        "only_value": {"signals": ("value",)},
    },
}


def build_panel(etf: Panel, tnx: pd.Series, irx: pd.Series, pie_monthly: pd.Series) -> Panel:
    """ETF-Panel (open/close) auf der Vereinigung aus ETF- und ^TNX-Handelstagen plus die Signalspalten.

    Die Vereinigung verhindert, dass ein Tag mit ETF-Kurs, aber ohne ^TNX-Wert (oder umgekehrt) wegfällt; ETF-Kurse
    vor der Notierung bleiben NaN (nicht handelbar).
    """
    idx = etf.close.index.union(tnx.dropna().index)
    sig = signal_columns(tnx, irx, pie_monthly, idx)
    close = etf.close.reindex(idx).copy()
    open_ = etf.open.reindex(idx).copy()
    for c in (TNX, IRX, PIE):
        close[c] = sig[c]
        open_[c] = sig[c]
    vol = etf.volume.reindex(idx) if len(etf.volume.columns) else None
    return Panel(open_, close, vol)


def load() -> Panel:
    """Panel: IEF/SHY (Yahoo, angepasst) plus Signalspalten ab 1962, ungekürzt (der Harness schneidet bei 2022-12-31 ab)."""
    etf = load_panel([BOND, CASH], start="2002-01-01")
    return build_panel(etf, *load_signal_inputs())


def weights(panel, signals=SIGNAL_NAMES, carry_window: int = 2520, carry_threshold: float = 1 / 3,
            ewma_fast: int = 21, ewma_slow: int = 252, anchor_halflife: int = 36,
            bond_asset: str = BOND, cash_asset: str | None = CASH) -> pd.DataFrame:
    """Zielgewichte: w in `bond_asset`, 1-w in `cash_asset` (oder echtes Cash, wenn None) an jedem Monatsende.

    Eine Zeile entsteht nur, wenn alle drei Stimmen berechenbar sind und alle genutzten ETF-Kurse am Monatsende
    gültig sind (NaN = nicht gelistet = nicht handelbar).
    """
    v = votes(panel, carry_window, carry_threshold, ewma_fast, ewma_slow, anchor_halflife)
    w = composite(v, signals)
    flags = month_end_flags(panel.close.index).to_numpy()
    assets = [bond_asset] + ([cash_asset] if cash_asset else [])
    valid = v.notna().all(axis=1) & panel.close[assets][flags].notna().all(axis=1)
    out = pd.DataFrame({bond_asset: w}, index=v.index)
    if cash_asset:
        out[cash_asset] = 1.0 - w
    return out[valid]
