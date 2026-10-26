"""Tests für strategies/trend_ma12_us_equity_cash_etf.py — nur synthetische Daten, kein Netz, kein Datencache."""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import month_end_flags
from qlab.data import Panel
from qlab.engine import check_causality, run_backtest
from strategies import trend_ma12_us_equity_cash_etf as strat

ASSET, SIG = strat.ASSET, strat.SIGNAL
VARIANTS = {"base": {}, **strat.SPEC["variants"]}


def _panel(asset_px: pd.Series, sig_px: pd.Series) -> Panel:
    close = pd.DataFrame({ASSET: asset_px, SIG: sig_px})
    # Open leicht abweichend vom Close, wie bei echten ETFs
    open_ = close * 0.999
    return Panel(open_, close)


def _monthly_step_panel(monthly: np.ndarray, start="2001-01-01") -> tuple[Panel, pd.DatetimeIndex]:
    n_months = len(monthly)
    idx = pd.bdate_range(start, pd.Timestamp(start) + pd.offsets.MonthEnd(n_months))
    s = pd.Series(idx, index=idx)
    key = s.dt.year * 12 + s.dt.month
    month_no = np.minimum((key - key.iloc[0]).to_numpy(), n_months - 1)
    px = pd.Series(np.asarray(monthly, float)[month_no], index=idx)
    me_dates = pd.DatetimeIndex(s.groupby(month_no).last().to_numpy())      # Orakel nur im Test (volle Monate)
    return _panel(px.copy(), px.copy()), me_dates


def _random_panel(n_years=12, seed=11, start="2001-01-02") -> Panel:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range(start, periods=int(252 * n_years))
    regime = np.where(np.sin(np.arange(len(idx)) / 160.0) > -0.3, 0.0006, -0.0012)
    r = regime + rng.normal(0.0, 0.01, len(idx))
    px = pd.Series(100 * np.exp(np.cumsum(r)), index=idx)
    return _panel(px, px * (1 + rng.normal(0, 0.0005, len(idx))))


def _reference(monthly: np.ndarray, ma_short=1, ma_long=12, strict=False):
    out = []
    for m in range(len(monthly)):
        if m < max(ma_short, ma_long) - 1:
            out.append(None)
            continue
        fast = float(np.mean(monthly[m - ma_short + 1:m + 1]))
        slow = float(np.mean(monthly[m - ma_long + 1:m + 1]))
        out.append(float(fast > slow) if strict else float(fast >= slow))
    return out


def test_spec_contract():
    spec = strat.SPEC
    assert spec["id"] == "trend_ma12_us_equity_cash_etf"
    assert len(spec["variants"]) <= 3
    sig = inspect.signature(strat.weights)
    for name in list(spec["params"]) + [k for v in spec["variants"].values() for k in v]:
        assert name in sig.parameters, name
    assert set(spec["tickers"]) == {ASSET, SIG}
    assert spec["cost_bps"][ASSET] == 10.0


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_shape_and_range(variant):
    panel = _random_panel()
    w = strat.weights(panel, **{**strat.SPEC["params"], **VARIANTS[variant]})
    assert list(w.columns) == [ASSET]
    assert len(w) > 60
    assert w.notna().all().all()
    assert set(np.unique(w.to_numpy())) <= {0.0, 1.0}
    assert (w.sum(axis=1) <= 1.0 + 1e-12).all() and (w >= 0).all().all()
    flags = month_end_flags(panel.close.index)
    assert w.index.isin(flags.index[flags.to_numpy()]).all()


@pytest.mark.parametrize("variant,kw", [
    ("base", dict(ma_short=1, ma_long=12, strict=False)),
    ("sma10", dict(ma_short=1, ma_long=10, strict=True)),
    ("ma2_12", dict(ma_short=2, ma_long=12, strict=False)),
])
def test_matches_reference_rule(variant, kw):
    rng = np.random.default_rng(5)
    monthly = 100 * np.exp(np.cumsum(rng.normal(0.004, 0.05, 72)))
    panel, me_dates = _monthly_step_panel(monthly)
    w = strat.weights(panel, **{**strat.SPEC["params"], **VARIANTS[variant]})
    ref = _reference(monthly, **kw)
    exp = pd.Series({d: v for d, v in zip(me_dates, ref) if v is not None})
    assert list(w.index) == list(exp.index)
    assert np.allclose(w[ASSET].to_numpy(), exp.to_numpy())
    assert exp.nunique() == 2


def test_ties_and_first_signal():
    panel, me_dates = _monthly_step_panel(np.full(24, 100.0))
    base = strat.weights(panel)
    assert base.index[0] == me_dates[11]                      # erst nach 12 Monatsenden inkl. t
    assert (base[ASSET] == 1.0).all()                         # Gleichheit zählt als Long
    sma = strat.weights(panel, ma_long=10, strict=True)
    assert sma.index[0] == me_dates[9]
    assert (sma[ASSET] == 0.0).all()                          # SMA10-Variante strikt größer


def test_trend_response_exit_and_reentry():
    monthly = np.concatenate([np.linspace(100, 160, 18), np.linspace(150, 90, 8), np.linspace(95, 200, 18)])
    panel, me_dates = _monthly_step_panel(monthly)
    w = strat.weights(panel)[ASSET]
    assert w.loc[me_dates[15]] == 1.0
    assert w.loc[me_dates[25]] == 0.0
    assert w.loc[me_dates[-1]] == 1.0


def test_signal_column_drives_decision():
    up = np.linspace(100, 200, 30)
    panel_a, _ = _monthly_step_panel(up)
    falling = pd.Series(np.linspace(200, 100, len(panel_a.close)), index=panel_a.close.index)
    panel_b = _panel(panel_a.close[ASSET], falling)
    assert (strat.weights(panel_b)[ASSET] == 0.0).all()               # ^GSPC fällt -> Cash, obwohl SPY steigt
    assert (strat.weights(panel_b, signal=ASSET)[ASSET] == 1.0).all()  # Variante signal_tr nutzt SPY selbst


def test_no_weights_before_etf_listing():
    """SPY startet später als ^GSPC: davor NaN = nicht handelbar, kein Gewicht."""
    panel = _random_panel(n_years=6)
    close = panel.close.copy()
    listing = close.index[400]
    close.loc[:close.index[399], ASSET] = np.nan
    p2 = Panel((close * 0.999).copy(), close)
    w = strat.weights(p2)
    assert len(w) > 0
    assert w.index.min() >= listing
    assert not p2.close.loc[w.index, ASSET].isna().any()
    # Variante signal_tr: Signal aus dem ETF braucht 12 ETF-Monatsenden
    w_tr = strat.weights(p2, signal=ASSET)
    assert w_tr.index.min() >= w.index.min()
    me = month_end_flags(p2.close.index)
    me_dates = me.index[me.to_numpy()]
    first_etf_me = me_dates[me_dates >= listing][0]
    assert w_tr.index.min() >= me_dates[me_dates >= first_etf_me][11]


def test_signal_gaps_forward_filled_only_briefly():
    panel, me_dates = _monthly_step_panel(np.linspace(100, 140, 30))
    close = panel.close.copy()
    d = me_dates[20]
    close.loc[d, SIG] = np.nan
    assert d in strat.weights(Panel(close * 0.999, close)).index          # kurze Lücke: Vortag genutzt
    close = panel.close.copy()
    pos = close.index.get_loc(d)
    close.iloc[pos - 8:pos + 1, close.columns.get_loc(SIG)] = np.nan
    assert d not in strat.weights(Panel(close * 0.999, close)).index       # lange Lücke: kein Signal


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
    close.loc[close.index > cut] *= 0.01
    other = strat.weights(Panel((close * 0.999).copy(), close))
    assert base.loc[:cut].equals(other.loc[:cut])


def test_last_data_day_mid_month_is_not_month_end():
    panel = _random_panel(n_years=4)
    idx = panel.close.index
    mid = idx[idx >= pd.Timestamp("2003-06-10")][0]
    w = strat.weights(panel.truncate(mid))
    assert w.index.max() < pd.Timestamp("2003-06-01")


def test_engine_integration_timing_and_exposure():
    monthly = np.concatenate([np.linspace(100, 160, 18), np.linspace(150, 90, 8), np.linspace(95, 200, 18)])
    panel, _ = _monthly_step_panel(monthly)
    rng = np.random.default_rng(2)
    noise = pd.Series(1 + rng.normal(0, 0.002, len(panel.close)), index=panel.close.index)
    close = panel.close.mul(noise, axis=0)
    p2 = Panel((close * 0.999).copy(), close)
    w = strat.weights(p2)
    res = run_backtest(p2, w)
    assert (res.gross_exposure <= 1.0 + 1e-3).all()
    assert (res.weights[ASSET] >= -1e-9).all()
    s = w.index[w[ASSET] == 1.0][0]
    assert res.weights.loc[s, ASSET] == 0.0                                  # Signaltag: noch keine Position
    nxt = p2.close.index[p2.close.index.get_loc(s) + 1]
    assert res.weights.loc[nxt, ASSET] > 0.95                                # Handel am Folgetag (Eröffnung)
    pos = p2.close.index.get_indexer(w.index) + 1
    exec_days = p2.close.index[pos[pos < len(p2.close.index)]]
    assert (res.turnover.drop(exec_days) <= 1e-12).all()                     # sonst kein Umsatz
