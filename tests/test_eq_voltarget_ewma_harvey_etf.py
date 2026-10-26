"""Tests für strategies/eq_voltarget_ewma_harvey_etf.py — nur synthetische Daten, kein Netz, kein Datencache."""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import eq_voltarget_ewma_harvey as long_mod
from strategies import eq_voltarget_ewma_harvey_etf as strat

ASSET = strat.ASSET
VARIANTS = {"base": {}, **strat.SPEC["variants"]}


def _params(variant: str, **over) -> dict:
    return {**strat.SPEC["params"], **VARIANTS[variant], **over}


def _panel(n=1800, seed=21, name=ASSET) -> Panel:
    """SPY-ähnlich: Eröffnung weicht vom Vortagsschluss ab (Über-Nacht-Rendite), drei Vol-Regime."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("1999-01-04", periods=n)
    vol = np.repeat([0.006, 0.018, 0.01], n // 3 + 1)[:n]
    r = 0.0004 + vol * rng.standard_normal(n)
    close = pd.Series(100.0 * np.cumprod(1.0 + r), index=idx)
    op = close.shift(1).fillna(close.iloc[0]) * (1 + rng.normal(0, 0.003, n))
    return Panel(pd.DataFrame({name: op}), pd.DataFrame({name: close}))


def test_spec_contract():
    spec = strat.SPEC
    assert spec["id"] == "eq_voltarget_ewma_harvey_etf"
    assert spec["tickers"] == ["SPY"]
    assert len(spec["variants"]) <= 3
    sig = inspect.signature(strat.weights)
    for name in list(spec["params"]) + [k for v in spec["variants"].values() for k in v]:
        assert name in sig.parameters, name
    assert spec["cost_bps"][ASSET] == 2.0
    assert spec["variants"] == long_mod.SPEC["variants"]
    assert not hasattr(strat, "load")                  # Yahoo-Ticker, Standard-Laden im Harness


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_shape_and_range(variant):
    panel = _panel()
    p = _params(variant)
    w = strat.weights(panel, **p)
    assert list(w.columns) == [ASSET]
    assert len(w) > 5 and w.notna().all().all()
    assert w.index.isin(panel.close.index).all()
    assert (w.sum(axis=1) <= p["cap"] + 1e-12).all() and (w > 0).all().all()
    assert w.index[0] == panel.close.index[p["warmup"]]


def test_same_rule_as_long_module():
    panel = _panel()
    w_etf = strat.weights(panel)
    w_long = long_mod.weights(panel, asset=ASSET, first_signal=None)
    pd.testing.assert_frame_equal(w_etf, w_long)


def test_no_weights_on_nan_prices_late_listing():
    panel = _panel()
    close, op = panel.close.copy(), panel.open.copy()
    close.iloc[:300, 0] = np.nan                       # ETF noch nicht gelistet
    op.iloc[:300, 0] = np.nan
    close.iloc[1000:1010, 0] = np.nan
    op.iloc[1000:1010, 0] = np.nan
    pn = Panel(op, close)
    w = strat.weights(pn, band=0.0)
    idx = pn.close.index
    assert pn.close.loc[w.index, ASSET].notna().all()
    assert w.index[0] == idx[300 + 270]
    assert not w.index.isin(idx[1000:1011]).any()
    assert check_causality(lambda p: strat.weights(p), pn) == []


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_causality(variant):
    panel = _panel()
    p = _params(variant)
    assert check_causality(lambda pn, _p=p: strat.weights(pn, **_p), panel) == []


@pytest.mark.parametrize("variant", list(VARIANTS))
@pytest.mark.parametrize("exec_mode", ["open", "close_next"])
def test_engine_run_exposure_within_cap(variant, exec_mode):
    panel = _panel()
    p = _params(variant)
    w = strat.weights(panel, **p)
    res = run_backtest(panel, w, cost=CostModel(per_ticker_bps={ASSET: 2.0}), exec_mode=exec_mode)
    assert res.nav.notna().all() and (res.nav > 0).all()
    assert res.skipped_orders == 0 and res.n_trades > 0
    assert float(res.gross_exposure.max()) <= p["cap"] * 1.05 + 0.01
