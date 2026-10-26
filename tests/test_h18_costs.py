"""Tests fuer scripts/check_h18_costs.py (H18, Kosten und Umsetzung): nur synthetische Daten, kein Netz."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def _load(name: str):
    import sys
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


h18 = _load("check_h18_costs")
h12 = _load("check_h12_robust_basket")


def _random_close(n=1500, seed=1, mu=0.0003, sig=0.01) -> pd.Series:
    rng = np.random.default_rng(seed)
    r = rng.normal(mu, sig, n)
    return pd.Series(100.0 * np.cumprod(1.0 + r), index=pd.bdate_range("2000-01-03", periods=n))


def _rf(idx, v=0.0) -> pd.Series:
    return pd.Series(v, index=idx)


def _preps(n_markets=4, rfv=0.00008):
    out = {}
    for k in range(n_markets):
        c = _random_close(seed=10 + k, mu=0.0004)
        out[f"M{k}"] = h18.prepare_market(c, _rf(c.index, rfv))
    return out


def test_scenario_a_reproduces_base1x_exactly():
    c = _random_close(seed=3)
    rf = _rf(c.index, 0.00009)
    a = h18.sleeve_h18(c, rf, cost_bps=10.0, long_financing=None, cash_rate_mode="rf")
    b = h12.sleeve2(c, rf, lengths=(12,), target=None)
    assert a.index.equals(b.index)
    np.testing.assert_allclose(a["ret"].to_numpy(), b["ret"].to_numpy(), atol=1e-14)
    np.testing.assert_allclose(a["pos"].to_numpy(), b["pos"].to_numpy(), atol=1e-14)


def test_positions_independent_of_costs_financing_cash():
    c = _random_close(seed=5)
    rf = _rf(c.index, 0.0001)
    a = h18.sleeve_h18(c, rf)
    b = h18.sleeve_h18(c, rf, cost_bps=50.0, long_financing=0.025, cash_rate_mode="0")
    np.testing.assert_array_equal(a["pos"].to_numpy(), b["pos"].to_numpy())


def test_cost_difference_is_exact_turnover_times_bps():
    c = _random_close(seed=7)
    rf = _rf(c.index, 0.0)
    a = h18.sleeve_h18(c, rf, cost_bps=5.0)
    b = h18.sleeve_h18(c, rf, cost_bps=25.0)
    p = a["pos"].to_numpy()
    turn = np.abs(p - np.concatenate([[0.0], p[:-1]]))
    np.testing.assert_allclose((a["ret"] - b["ret"]).to_numpy(), turn * 20.0 / 1e4, atol=1e-14)
    assert turn.sum() > 2          # es gibt Wechsel
    assert (b["ret"] + 1).prod() < (a["ret"] + 1).prod()


def test_financing_charges_rf_plus_markup_only_when_long():
    c = _random_close(seed=9)
    rf = _rf(c.index, 0.0001)
    a = h18.sleeve_h18(c, rf, cost_bps=10.0, cash_rate_mode="0")
    b = h18.sleeve_h18(c, rf, cost_bps=10.0, long_financing=0.025, cash_rate_mode="0")
    p = a["pos"].to_numpy()
    expected = np.where(p > 0, p * (0.0001 + 0.025 / 252), 0.0)
    np.testing.assert_allclose((a["ret"] - b["ret"]).to_numpy(), expected, atol=1e-14)
    assert (p == 0).any() and (p > 0).any()
    # long_financing = 0 belastet nur den US-RF
    z = h18.sleeve_h18(c, rf, cost_bps=10.0, long_financing=0.0, cash_rate_mode="0")
    np.testing.assert_allclose((a["ret"] - z["ret"]).to_numpy(), np.where(p > 0, p * 0.0001, 0.0), atol=1e-14)


def test_cash_mode_zero_gives_no_interest_in_cash_days():
    idx = pd.bdate_range("2000-01-03", periods=1000)
    c = pd.Series(100.0 * np.exp(-0.001 * np.arange(1000)), index=idx)   # Dauer-Abwaertstrend: nie long
    rf = _rf(idx, 0.0002)
    z = h18.sleeve_h18(c, rf, cash_rate_mode="0")
    r = h18.sleeve_h18(c, rf, cash_rate_mode="rf")
    assert (z["pos"] == 0).all()
    np.testing.assert_allclose(z["ret"].to_numpy(), 0.0, atol=1e-15)
    np.testing.assert_allclose(r["ret"].to_numpy(), 0.0002, atol=1e-15)


def test_invalid_arguments_raise():
    c = _random_close()
    with pytest.raises(ValueError):
        h18.sleeve_h18(c, _rf(c.index), cash_rate_mode="xyz")
    with pytest.raises(ValueError):
        h18.sleeve_h18(c, _rf(c.index), cost_bps=-1.0)
    with pytest.raises(ValueError):
        h18.prepare_market(c.iloc[:200], _rf(c.index[:200]))     # zu wenige Monatsenden fuer MA12


def test_causality_future_does_not_change_past():
    c = _random_close(n=1600, seed=17)
    rf = _rf(c.index, 0.00005)
    full = h18.sleeve_h18(c, rf, long_financing=0.025, cash_rate_mode="0")
    cut = 1200
    c2 = c.copy()
    c2.iloc[cut:] = c2.iloc[cut:] * np.linspace(1.0, 3.0, len(c) - cut)
    part = h18.sleeve_h18(c2, rf, long_financing=0.025, cash_rate_mode="0")
    common = full.index[full.index < c.index[cut - 5]]
    assert len(common) > 300
    np.testing.assert_allclose(full.loc[common, "ret"].to_numpy(), part.loc[common, "ret"].to_numpy(), atol=1e-14)


def test_basket_scenario_a_equals_equal_weight_of_sleeve2():
    preps = _preps(4)
    got = h18.basket_returns(preps, 3, cost_bps=10.0, cash_rate_mode="rf")
    cols = {}
    for k in range(4):
        c = _random_close(seed=10 + k, mu=0.0004)
        cols[f"M{k}"] = h12.sleeve2(c, _rf(c.index, 0.00008), lengths=(12,), target=None)["ret"]
    exp = h18.tp.basket(pd.DataFrame(cols), 3)[0]
    assert got.index.equals(exp.index)
    np.testing.assert_allclose(got.to_numpy(), exp.to_numpy(), atol=1e-14)


def test_bisect_root_known_function_and_edges():
    st, v = h18.bisect_root(lambda x: 5.0 - x, 0.0, 100.0, tol=1e-6)
    assert st == "ok" and v == pytest.approx(5.0, abs=1e-5)
    assert h18.bisect_root(lambda x: -1.0 - x, 0.0, 10.0)[0] == "unter_lo"
    assert h18.bisect_root(lambda x: 100.0 - x, 0.0, 10.0)[0] == "ueber_hi"


def test_breakeven_bps_on_synthetic_markets_is_consistent():
    preps = _preps(4)
    base = h18.basket_returns(preps, 3, cost_bps=0.0)
    rf_c = _rf(base.index, 0.00008)
    cagr_rf = h12.konstanz(rf_c, rf_c)["cagr"]

    def gap(x):
        r = h18.basket_returns(preps, 3, cost_bps=x).reindex(base.index)
        return h12.konstanz(r, rf_c)["cagr"] - cagr_rf

    # CAGR faellt monoton mit den Kosten
    assert gap(0.0) > gap(50.0) > gap(500.0)
    st, v = h18.bisect_root(gap, 0.0, 5000.0, tol=0.01)
    if st == "ok":
        assert abs(gap(v)) < 5e-4
