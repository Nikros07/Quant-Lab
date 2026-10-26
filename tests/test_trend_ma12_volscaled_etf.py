"""Tests für strategies/trend_ma12_volscaled_etf.py (H9) — nur synthetische Daten, kein Netz, kein Datencache."""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import month_end_dates, month_end_flags
from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import trend_ma12_volscaled_etf as strat

ASSET, SIG = strat.ASSET, strat.SIGNAL
BASE = dict(strat.SPEC["params"])
TARGET10 = {**strat.SPEC["params"], **strat.SPEC["variants"]["target10"]}

# Handrechnung: 21 Renditen aus 10x +a, 10x -a und einer 0 haben Mittel 0, Summe der Quadrate 20 a^2,
# Stichprobenvarianz (ddof=1) = 20 a^2 / 20 = a^2, also sigma_taeglich = a, annualisiert a * sqrt(252).
# Eine zyklische Reihe mit Periode 21 hat in JEDEM 21er-Fenster genau dieses Muster (Permutation).
PAT = np.array([1.0, -1.0] * 10 + [0.0])
A_HIGH = 0.30 / np.sqrt(252)     # sigma_ann = 0,30  ->  Gewicht = 0,15 / 0,30 = 0,5
A_CALM = 0.05 / np.sqrt(252)     # sigma_ann = 0,05  ->  Gewicht = min(1; 0,15 / 0,05 = 3) = 1,0
N, T_SW = 800, 500               # ruhig bis Index 499, danach hohe Vola


def _panel(r_asset, sig_px, start="2001-01-01") -> Panel:
    r_asset = np.asarray(r_asset, float)
    idx = pd.bdate_range(start, periods=len(r_asset))
    px = pd.Series(100.0 * np.cumprod(1.0 + r_asset), index=idx)
    close = pd.DataFrame({ASSET: px, SIG: pd.Series(np.asarray(sig_px, float), index=idx)})
    return Panel(close * 0.999, close)


def _periodic_returns(n=N, switch=T_SW, a_before=A_CALM, a_after=A_HIGH) -> np.ndarray:
    t = np.arange(n)
    a = np.where(t < switch, a_before, a_after)
    return a * PAT[t % 21]


def _rising(n=N):
    return 100.0 * 1.001 ** np.arange(n)


def _falling(n=N):
    return 100.0 * 0.999 ** np.arange(n)


def _flat(n=N):
    return np.full(n, 100.0)


def _decision_days(idx):
    """d_calm: Monatsende im ruhigen Regime mit vollem Fenster; d_high: Monatsende im hohen Regime."""
    me = month_end_dates(idx)
    d_calm = me[me >= idx[280]][0]
    d_high = me[me >= idx[T_SW + 25]][0]
    return d_calm, d_high


def _random_panel(n_years=12, seed=11, start="2001-01-02") -> Panel:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range(start, periods=int(252 * n_years))
    regime = np.where(np.sin(np.arange(len(idx)) / 160.0) > -0.3, 0.0006, -0.0012)
    r = regime + rng.normal(0.0, 0.01, len(idx))
    px = pd.Series(100 * np.exp(np.cumsum(r)), index=idx)
    return Panel(px * 0.999, pd.DataFrame({ASSET: px, SIG: px * (1 + rng.normal(0, 0.0005, len(idx)))}, index=idx))


def test_spec_contract():
    spec = strat.SPEC
    assert spec["id"] == "trend_ma12_volscaled_etf"
    assert spec["family"] == "volmgmt"
    assert set(spec["tickers"]) == {ASSET, SIG}
    assert spec["cost_bps"][ASSET] == 10.0
    assert len(spec["variants"]) <= 3
    assert spec["variants"] == {"target10": {"target": 0.10}}
    assert spec["params"]["target"] == 0.15 and spec["params"]["vol_window"] == 21
    sig = inspect.signature(strat.weights)
    for name in list(spec["params"]) + [k for v in spec["variants"].values() for k in v]:
        assert name in sig.parameters, name


def test_handcalc_weights_high_and_calm_vol():
    panel = _panel(_periodic_returns(), _rising())
    d_calm, d_high = _decision_days(panel.close.index)
    w = strat.weights(panel)[ASSET]
    assert w.loc[d_calm] == 1.0                              # ruhig: 0,15/0,05 = 3 -> Cap 1,0 exakt
    assert w.loc[d_high] == pytest.approx(0.5, abs=1e-12)    # hohe Vola: 0,15/0,30 = 0,5
    assert w.loc[d_high] < 1.0


def test_sigma_uses_exactly_last_21_returns():
    n = 400
    idx = pd.bdate_range("2001-01-01", periods=n)
    d = month_end_dates(idx)[month_end_dates(idx) >= idx[300]][0]
    k = idx.get_loc(d)
    r = np.zeros(n)
    r[k - 20:k + 1] = A_HIGH * PAT                 # genau 21 Renditen bis einschliesslich t
    r[k - 21] = 0.5                                # 22. letzte Rendite: darf NICHT eingehen
    panel = _panel(r, _rising(n))
    assert strat.weights(panel)[ASSET].loc[d] == pytest.approx(0.5, abs=1e-12)
    # Gegenprobe 1: mit vol_window=22 fliesst die 0,5 ein, Gewicht aendert sich
    assert strat.weights(panel, vol_window=22)[ASSET].loc[d] != pytest.approx(0.5)
    # Gegenprobe 2: eine Rendite INNERHALB des Fensters aendert das Gewicht
    r2 = r.copy()
    r2[k - 3] += 0.01
    assert strat.weights(_panel(r2, _rising(n)))[ASSET].loc[d] != pytest.approx(0.5)


def test_flat_signal_gives_zero_and_rising_signal_gives_weight():
    r = _periodic_returns()
    w_fall = strat.weights(_panel(r, _falling()))[ASSET]
    assert len(w_fall) > 0
    assert (w_fall == 0.0).all()                              # FLAT -> 0, egal wie hoch die Vola
    d_calm, d_high = _decision_days(pd.bdate_range("2001-01-01", periods=N))
    w_rise = strat.weights(_panel(r, _rising()))[ASSET]
    assert w_rise.loc[d_high] == pytest.approx(0.5)           # Gegenprobe: gleiche Vola, LONG -> 0,5


def test_tie_counts_as_long_warmup_and_strictly_below_is_flat():
    panel = _panel(_periodic_returns(), _flat())
    idx = panel.close.index
    me = month_end_dates(idx)
    w = strat.weights(panel)[ASSET]
    assert w.index[0] == me[11]                               # erst mit 12 Monatsenden inkl. t
    d_calm, d_high = _decision_days(idx)
    assert w.loc[d_calm] == 1.0                               # Gleichheit P_t = MA12 -> LONG
    assert w.loc[d_high] == pytest.approx(0.5)
    # knapp unter MA12 -> FLAT
    sig = _flat()
    sig[idx.get_loc(d_high)] = 99.999
    w_below = strat.weights(_panel(_periodic_returns(), sig))[ASSET]
    assert w_below.loc[d_high] == 0.0
    assert w_below.loc[d_calm] == 1.0


def test_zero_or_nan_sigma_gives_zero_weight_without_error():
    w0 = strat.weights(_panel(np.zeros(N), _rising()))[ASSET]   # sigma = 0 (konstanter Kurs)
    assert len(w0) > 0 and (w0 == 0.0).all()
    panel = _panel(_periodic_returns(), _rising())
    d_calm, d_high = _decision_days(panel.close.index)
    close = panel.close.copy()
    kpos = panel.close.index.get_loc(d_high)
    close.iloc[kpos - 5, close.columns.get_loc(ASSET)] = np.nan   # Lücke im Fenster -> sigma NaN
    w = strat.weights(Panel(close * 0.999, close))[ASSET]
    assert np.isfinite(w.to_numpy()).all()
    assert w.loc[d_high] == 0.0
    assert w.loc[d_calm] == 1.0                               # ungestoert


def test_weight_never_above_one_even_with_huge_target():
    panel = _random_panel(n_years=6)
    w = strat.weights(panel, target=10.0)[ASSET]
    assert (w <= 1.0).all() and (w >= 0.0).all()
    d_calm, d_high = _decision_days(panel.close.index)
    assert (strat.weights(_panel(_periodic_returns(), _rising()), target=10.0)[ASSET]
            .loc[[d_calm, d_high]] == 1.0).all()              # Cap 1,0 auch bei hoher Vola


@pytest.mark.parametrize("params", [BASE, TARGET10], ids=["base", "target10"])
def test_shape_range_and_monthend_only(params):
    panel = _random_panel(n_years=12)
    w = strat.weights(panel, **params)
    assert list(w.columns) == [ASSET]
    assert len(w) > 60
    assert np.isfinite(w.to_numpy()).all()
    assert ((w >= 0.0) & (w <= 1.0)).all().all()
    flags = month_end_flags(panel.close.index)
    assert w.index.isin(flags.index[flags.to_numpy()]).all()
    assert (w[ASSET] > 0).any() and (w[ASSET] < 1).any()     # Test ist nicht trivial


def test_target10_is_never_above_base_and_handcalc():
    panel = _panel(_periodic_returns(), _rising())
    d_calm, d_high = _decision_days(panel.close.index)
    wb = strat.weights(panel)[ASSET]
    w10 = strat.weights(panel, **TARGET10)[ASSET]
    assert w10.index.equals(wb.index)
    assert w10.loc[d_high] == pytest.approx(1.0 / 3.0)        # 0,10 / 0,30
    assert w10.loc[d_calm] == 1.0                             # 0,10 / 0,05 = 2 -> Cap
    assert (w10 <= wb + 1e-12).all()


@pytest.mark.parametrize("params", [BASE, TARGET10], ids=["base", "target10"])
def test_causality_check(params):
    fn = lambda p: strat.weights(p, **params)
    assert check_causality(fn, _random_panel(n_years=12)) == []
    assert check_causality(fn, _panel(_periodic_returns(), _rising())) == []


def test_future_returns_do_not_change_decision_weight():
    panel = _panel(_periodic_returns(), _rising())
    _, d_high = _decision_days(panel.close.index)
    k = panel.close.index.get_loc(d_high)
    col = panel.close.columns.get_loc(ASSET)
    base = strat.weights(panel)[ASSET]
    close = panel.close.copy()
    close.iloc[k + 1:, col] *= 1.5                            # Renditeaenderung NACH dem Entscheidungstag
    after = strat.weights(Panel(close * 0.999, close))[ASSET]
    assert after.loc[:d_high].equals(base.loc[:d_high])
    close2 = panel.close.copy()
    close2.iloc[k, col] *= 1.5                                # Gegenprobe: Tag t selbst liegt im Fenster
    inside = strat.weights(Panel(close2 * 0.999, close2))[ASSET]
    assert inside.loc[d_high] != base.loc[d_high]


def test_no_weights_before_etf_listing():
    panel = _random_panel(n_years=6)
    close = panel.close.copy()
    listing = close.index[400]
    close.loc[:close.index[399], ASSET] = np.nan
    p2 = Panel(close * 0.999, close)
    w = strat.weights(p2)
    assert len(w) > 0 and w.index.min() >= listing
    assert not p2.close.loc[w.index, ASSET].isna().any()


@pytest.mark.parametrize("params", [BASE, TARGET10], ids=["base", "target10"])
def test_engine_integration_timing_and_exposure(params):
    panel = _panel(_periodic_returns(), _rising())
    idx = panel.close.index
    rf = pd.Series(0.0, index=idx)                            # kein Netz: RF explizit null
    cost = CostModel(per_ticker_bps={ASSET: 10.0})
    w = strat.weights(panel, **params)
    res = run_backtest(panel, w, cost=cost, rf=rf)
    assert np.isfinite(res.nav.to_numpy()).all() and (res.nav > 0).all()
    assert np.isfinite(res.ret.to_numpy()).all()
    # Ziel-Gewicht <= 1; Ist-Exposure kann durch 10-bp-Kosten bei Cash < 0 um ~0,1 % darüber liegen
    assert (res.gross_exposure <= 1.0 + 2e-3).all()
    assert (res.weights[ASSET] >= -1e-9).all()
    assert (w[ASSET] <= 1.0).all()
    s = w.index[w[ASSET] > 0][0]
    assert res.weights.loc[s, ASSET] == 0.0                   # am Signaltag noch keine Position
    nxt = idx[idx.get_loc(s) + 1]
    assert res.weights.loc[nxt, ASSET] == pytest.approx(w.loc[s, ASSET], abs=0.03)
    d_calm, d_high = _decision_days(idx)
    for d in (d_calm, d_high):                                # Handel zur Eroeffnung des Folgetags
        nd = idx[idx.get_loc(d) + 1]
        assert res.weights.loc[nd, ASSET] == pytest.approx(w.loc[d, ASSET], abs=0.03)
