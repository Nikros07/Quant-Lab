"""Tests für strategies/trend_ma12_bond_substitute_etf.py (H7) — nur synthetische Daten, kein Netz, kein Datencache.

risk-free wird in run_backtest-Aufrufen explizit auf 0 gesetzt, damit kein French-Download nötig ist.
"""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import month_end_flags
from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import trend_ma12_bond_substitute_etf as strat

ASSET, SIG, BOND, IEF = strat.ASSET, strat.SIGNAL, strat.BOND, "IEF"
VARIANTS = {"base": {}, **strat.SPEC["variants"]}


def _panel(close: pd.DataFrame) -> Panel:
    # Open leicht abweichend vom Close, wie bei echten ETFs
    return Panel(close * 0.999, close)


def _monthly(sig_m, bond_m, ief_m=None, spy_m=None, start="2001-01-01"):
    """Monatskonstante Kurse: jeder Handelstag des Monats k hat den Wert m[k]; Monatsende = m[k].
    Liefert (Panel, Liste der Monatsenden je Monat k)."""
    n = len(sig_m)
    idx = pd.bdate_range(start, pd.Timestamp(start) + pd.offsets.MonthEnd(n))
    key = pd.Series(idx.year * 12 + idx.month, index=idx)
    month_no = np.minimum((key - key.iloc[0]).to_numpy(), n - 1)

    def px(vals):
        return pd.Series(np.asarray(vals, float)[month_no], index=idx)

    ief_m = 100.0 + np.arange(n) if ief_m is None else ief_m
    spy_m = 100.0 + np.arange(n) if spy_m is None else spy_m
    close = pd.DataFrame({ASSET: px(spy_m), SIG: px(sig_m), BOND: px(bond_m), IEF: px(ief_m)})
    flags = month_end_flags(idx)
    me = idx[flags.to_numpy()]
    assert len(me) == n
    return _panel(close), me


def _random_panel(n_years=12, seed=11, start="2001-01-02") -> Panel:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range(start, periods=int(252 * n_years))
    t = np.arange(len(idx))
    # Aktien: Regimewechsel, damit der Signalfilter FLAT und LONG erreicht
    r_eq = np.where(np.sin(t / 160.0) > -0.3, 0.0006, -0.0012) + rng.normal(0.0, 0.01, len(idx))
    spx = pd.Series(100 * np.exp(np.cumsum(r_eq)), index=idx)
    # Anleihen: eigene Regimephase, damit der Anleihen-Filter ON und OFF erreicht
    r_b = np.where(np.sin(t / 110.0 + 1.0) > 0.0, 0.0003, -0.0004) + rng.normal(0.0, 0.004, len(idx))
    vust = pd.Series(100 * np.exp(np.cumsum(r_b)), index=idx)
    r_i = np.where(np.sin(t / 90.0) > 0.2, 0.0002, -0.0003) + rng.normal(0.0, 0.003, len(idx))
    ief = pd.Series(100 * np.exp(np.cumsum(r_i)), index=idx)
    close = pd.DataFrame({ASSET: spx * (1 + rng.normal(0, 0.0005, len(idx))), SIG: spx,
                          BOND: vust, IEF: ief})
    return _panel(close)


def test_spec_contract():
    spec = strat.SPEC
    assert spec["id"] == "trend_ma12_bond_substitute_etf"
    assert spec["family"] == "macro"
    assert spec["start"] == "1990-01-01"
    assert set(spec["tickers"]) == {ASSET, SIG, "VUSTX", IEF}
    assert set(spec["variants"]) == {"ief", "uncond"}
    assert spec["variants"]["ief"] == {"bond": "IEF"}
    assert spec["variants"]["uncond"] == {"bond_filter": False}
    assert spec["params"]["bond"] == "VUSTX" and spec["params"]["bond_filter"] is True
    assert spec["cost_bps"] == {ASSET: 10.0, "VUSTX": 10.0, "IEF": 10.0}
    sig = inspect.signature(strat.weights)
    for name in list(spec["params"]) + [k for v in spec["variants"].values() for k in v]:
        assert name in sig.parameters, name


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_shape_range_and_columns(variant):
    panel = _random_panel()
    params = {**strat.SPEC["params"], **VARIANTS[variant]}
    w = strat.weights(panel, **params)
    assert list(w.columns) == [ASSET, params["bond"]]
    assert len(w) > 60
    assert w.notna().all().all()
    assert set(np.unique(w.to_numpy())) <= {0.0, 1.0}
    assert (w.sum(axis=1) <= 1.0 + 1e-12).all() and (w >= 0).all().all()
    flags = month_end_flags(panel.close.index)
    assert w.index.isin(flags.index[flags.to_numpy()]).all()


def test_random_panel_reaches_all_states():
    """Nicht-triviale Daten: alle drei Zustände (Aktien, Anleihe, Cash) kommen vor."""
    w = strat.weights(_random_panel())
    assert (w[ASSET] == 1.0).any() and (w[ASSET] == 0.0).any()
    assert (w[BOND] == 1.0).any()
    assert ((w[ASSET] == 0.0) & (w[BOND] == 0.0)).any()


def test_hand_calc_flat_stocks_bond_uptrend():
    """Aktien-Signal FLAT ab Monat 12, Anleihe im Aufwärtstrend -> 100 % Anleihe.
    sig_m = 100 (Monate 0-11), 50 (Monate 12-15). MA12 ab Monat 11 = 100.
      k=11: MA12 = 100, Signal 100 >= 100 -> LONG (Gleichheit zählt).
      k=12: MA12 = (11*100 + 50)/12 = 95,83; 50 < 95,83 -> FLAT.
    bond_m = 100 + k. Anleihe k=12 = 112; Mittel k=1..12 = (101+...+112)/12 = 106,5; 112 >= 106,5 -> ON.
    Anleihe k=15 = 115; Mittel k=4..15 = (104+...+115)/12 = 109,5 -> ON.
    """
    sig = [100.0] * 12 + [50.0] * 4
    bond = [100.0 + k for k in range(16)]
    panel, me = _monthly(sig, bond)
    w = strat.weights(panel)
    assert list(w.index) == list(me[11:16])                       # Zeilen erst ab Monat 11
    assert w.loc[me[11], ASSET] == 1.0 and w.loc[me[11], BOND] == 0.0   # LONG: nie Anleihe
    assert w.loc[me[12], ASSET] == 0.0 and w.loc[me[12], BOND] == 1.0   # FLAT + Anleihe-Aufwärtstrend
    assert w.loc[me[15], ASSET] == 0.0 and w.loc[me[15], BOND] == 1.0


def test_hand_calc_flat_stocks_bond_downtrend_is_cash():
    """Aktien FLAT, Anleihe im Abwärtstrend -> alles Cash.
    bond_m = 100 - k. k=12: Anleihe 88; Mittel k=1..12 = (99+...+88)/12 = 93,5; 88 < 93,5 -> Cash.
    Ohne Anleihen-Filter (uncond) wäre k=12 dagegen 100 % Anleihe; das prüft der zweite Teil.
    """
    sig = [100.0] * 12 + [50.0] * 4
    bond = [100.0 - k for k in range(16)]
    panel, me = _monthly(sig, bond)
    w = strat.weights(panel)
    assert w.loc[me[12], ASSET] == 0.0 and w.loc[me[12], BOND] == 0.0
    assert w.loc[me[15], ASSET] == 0.0 and w.loc[me[15], BOND] == 0.0
    wu = strat.weights(panel, bond_filter=False)
    assert wu.loc[me[12], BOND] == 1.0                            # uncond: Anleihe trotz Abwärtstrend
    assert wu.loc[me[11], BOND] == 0.0                            # LONG bleibt LONG


def test_bond_filter_ge_boundary():
    """Anleihen-Filter ist >= (Gleichheit zählt als ON), bei 1 Einheit darunter Cash.
    Anleihe 100 in k=0..11 und k=12 = 100: Mittel k=1..12 = 1200/12 = 100 -> ON.
    Anleihe k=12 = 99: Mittel = 1199/12 = 99,92 -> 99 < 99,92 -> Cash.
    """
    sig = [100.0] * 12 + [50.0] * 4
    panel_eq, me = _monthly(sig, [100.0] * 16)
    assert strat.weights(panel_eq).loc[me[12], BOND] == 1.0
    panel_lt, me = _monthly(sig, [100.0] * 12 + [99.0] * 4)
    assert strat.weights(panel_lt).loc[me[12], BOND] == 0.0


def test_bond_warmup_requires_twelve_month_ends():
    """Anleihe ohne Kurs in Monat 0-2: das 12-Monats-Mittel von Monat 12 enthält NaN -> Cash,
    auch wenn der aktuelle Kurs hoch ist. Ab Monat 14 (Fenster 3-14 vollständig) gilt der Filter."""
    sig = [100.0] * 12 + [50.0] * 4
    bond = [np.nan] * 3 + [100.0 + k for k in range(3, 16)]
    panel, me = _monthly(sig, bond)
    w = strat.weights(panel)
    assert w.loc[me[12], BOND] == 0.0                            # Vorgeschichte unvollständig
    assert w.loc[me[14], BOND] == 1.0                            # Fenster 3..14 vollständig, Trend auf


def test_bond_nan_on_decision_day_is_cash():
    sig = [100.0] * 12 + [50.0] * 4
    bond = [100.0 + k for k in range(16)]
    bond[12] = np.nan                                            # Anleihe fehlt am Entscheidungstag
    panel, me = _monthly(sig, bond)
    w = strat.weights(panel)
    assert w.loc[me[12], ASSET] == 0.0 and w.loc[me[12], BOND] == 0.0
    # Die Lücke (Monat 12) bleibt 12 Monatsenden lang im Mittelfenster: Monat 13 und 14 sind ebenfalls Cash,
    # obwohl die Anleihe dort steigt (Fenster enthält NaN -> kein gültiger Mittelwert).
    assert w.loc[me[13], BOND] == 0.0
    assert w.loc[me[14], BOND] == 0.0


def test_ief_variant_uses_ief_column():
    """IEF im Aufwärtstrend, VUSTX im Abwärtstrend: Basis -> Cash, Variante ief -> IEF 100 %."""
    sig = [100.0] * 12 + [50.0] * 4
    panel, me = _monthly(sig, [100.0 - k for k in range(16)], ief_m=[100.0 + k for k in range(16)])
    base = strat.weights(panel)
    assert list(base.columns) == [ASSET, "VUSTX"]
    assert base.loc[me[12], "VUSTX"] == 0.0
    ief = strat.weights(panel, bond="IEF")
    assert list(ief.columns) == [ASSET, "IEF"]
    assert ief.loc[me[12], "IEF"] == 1.0 and ief.loc[me[12], ASSET] == 0.0


def test_no_weights_before_etf_listing():
    """SPY startet später als ^GSPC: davor kein Gewicht (Zeile nur, wenn SPY-Kurs gültig)."""
    panel = _random_panel(n_years=6)
    close = panel.close.copy()
    listing = close.index[400]
    close.loc[:close.index[399], ASSET] = np.nan
    w = strat.weights(_panel(close))
    assert len(w) > 0
    assert w.index.min() >= listing
    assert not _panel(close).close.loc[w.index, ASSET].isna().any()


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_weights_only_on_priced_titles(variant):
    """Kein Gewicht auf einem Titel ohne Kurs; Gewichte nie negativ, Summe <= 1."""
    panel = _random_panel(n_years=12, seed=3)
    close = panel.close.copy()
    close.iloc[:600, close.columns.get_loc(IEF)] = np.nan       # IEF erst spät notiert
    close.iloc[700:1000, close.columns.get_loc(BOND)] = np.nan  # VUSTX-Lücke
    p2 = _panel(close)
    params = {**strat.SPEC["params"], **VARIANTS[variant]}
    w = strat.weights(p2, **params)
    for col in (ASSET, params["bond"]):
        held = w[col] > 0
        assert p2.close.loc[w.index[held], col].notna().all()
    assert (w.sum(axis=1) <= 1.0 + 1e-12).all()
    assert w.notna().all().all()


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_causality_check(variant):
    panel = _random_panel(n_years=12)
    params = {**strat.SPEC["params"], **VARIANTS[variant]}
    assert check_causality(lambda p: strat.weights(p, **params), panel) == []


def test_future_prices_do_not_change_past_weights():
    panel = _random_panel(n_years=10)
    base = strat.weights(panel)
    cut = panel.close.index[int(len(panel.close) * 0.6)]
    close = panel.close.copy()
    close.loc[close.index > cut, [ASSET, SIG, BOND, IEF]] *= 0.01
    other = strat.weights(_panel(close))
    assert base.loc[:cut].equals(other.loc[:cut])


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_variants_run_in_engine(variant):
    panel = _random_panel(n_years=12)
    params = {**strat.SPEC["params"], **VARIANTS[variant]}
    w = strat.weights(panel, **params)
    cost = CostModel(default_bps=5.0, per_ticker_bps=strat.SPEC["cost_bps"])
    rf = pd.Series(0.0, index=panel.close.index)
    res = run_backtest(panel, w, cost=cost, rf=rf)
    assert np.isfinite(res.nav.to_numpy()).all() and (res.nav > 0).all()
    assert np.isfinite(res.ret.to_numpy()).all()
    # Zielgewichte sind <= 1 (siehe oben). Die Engine zieht Kosten vom Cash ab; nach einem Umschichtungs-
    # Handel (Verkauf + Kauf, je 10 bp) liegt die Brutto-Quote dadurch knapp darüber (gemessen ~1,002).
    assert (res.gross_exposure <= 1.0 + 5e-3).all()
    assert res.weights[params["bond"]].abs().max() > 0.0          # Anleihenbein wird tatsächlich gehalten


def test_engine_timing_bond_bought_next_day():
    """Signal am Monatsende (Anleihe-Filter ON, Aktien FLAT) -> Handel zur Eröffnung des Folgetags."""
    sig = [100.0] * 12 + [50.0] * 4
    panel, me = _monthly(sig, [100.0 + k for k in range(16)])
    rf = pd.Series(0.0, index=panel.close.index)
    w = strat.weights(panel)
    res = run_backtest(panel, w, rf=rf)
    assert res.weights.loc[me[12], BOND] == 0.0                   # Signaltag: noch keine Position
    nxt = panel.close.index[panel.close.index.get_loc(me[12]) + 1]
    assert res.weights.loc[nxt, BOND] > 0.95                      # Handel zur Eröffnung am Folgetag
