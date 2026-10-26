"""Tests fuer scripts/check_h12_robust_basket.py (sleeve2, H12): nur synthetische Daten, kein Netz."""
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


h12 = _load("check_h12_robust_basket")
h11 = _load("check_trend_vt_basket")
sleeve2 = h12.sleeve2


def _random_close(n=1200, seed=1, mu=0.0003, sig=0.01) -> pd.Series:
    rng = np.random.default_rng(seed)
    r = rng.normal(mu, sig, n)
    return pd.Series(100.0 * np.cumprod(1.0 + r), index=pd.bdate_range("2000-01-03", periods=n))


def _zero_rf(idx) -> pd.Series:
    return pd.Series(0.0, index=idx)


def test_base1x_reproduces_h11_sleeve():
    c = _random_close(seed=3)
    rf = _zero_rf(c.index)
    a = sleeve2(c, rf, lengths=(12,), target=None)
    b = h11.sleeve(c, rf, vol_scaled=False, cap=1.0, bps=10.0)
    assert a.index.equals(b.index)
    np.testing.assert_allclose(a["ret"].to_numpy(), b["ret"].to_numpy(), atol=1e-12)
    np.testing.assert_allclose(a["pos"].to_numpy(), b["pos"].to_numpy(), atol=1e-12)


def test_vt15_cap10_reproduces_h11_sleeve():
    c = _random_close(seed=5, sig=0.015)
    rf = pd.Series(0.00005, index=c.index)
    a = sleeve2(c, rf, lengths=(12,), target=0.15, cap=1.0)
    b = h11.sleeve(c, rf, target=0.15, cap=1.0, bps=10.0)
    np.testing.assert_allclose(a["ret"].to_numpy(), b["ret"].to_numpy(), atol=1e-12)
    assert (a["pos"] <= 1.0 + 1e-12).all()


def test_identical_lengths_equal_single_length():
    c = _random_close(seed=7)
    rf = _zero_rf(c.index)
    a = sleeve2(c, rf, lengths=(12, 12, 12))
    b = sleeve2(c, rf, lengths=(12,))
    np.testing.assert_allclose(a["ret"].to_numpy(), b["ret"].to_numpy(), atol=1e-12)


def test_ensemble_weights_are_thirds_without_vol():
    c = _random_close(seed=11)
    p = sleeve2(c, _zero_rf(c.index), lengths=(6, 9, 12))["pos"]
    allowed = np.array([0.0, 1 / 3, 2 / 3, 1.0])
    assert np.min(np.abs(p.to_numpy()[:, None] - allowed[None, :]), axis=1).max() < 1e-12


def test_start_is_first_month_end_with_longest_window():
    c = _random_close(seed=13)
    a = sleeve2(c, _zero_rf(c.index), lengths=(6, 9, 12))
    b = sleeve2(c, _zero_rf(c.index), lengths=(12,))
    assert a.index[0] == b.index[0]


def test_no_leverage_allowed():
    c = _random_close()
    with pytest.raises(ValueError):
        sleeve2(c, _zero_rf(c.index), target=0.15, cap=1.5)
    with pytest.raises(ValueError):
        sleeve2(c, _zero_rf(c.index), lengths=())


def test_causality_future_does_not_change_past():
    c = _random_close(n=1300, seed=17)
    rf = _zero_rf(c.index)
    full = sleeve2(c, rf, lengths=(6, 9, 12), target=0.20)
    cut = 1000
    c2 = c.copy()
    c2.iloc[cut:] = c2.iloc[cut:] * np.linspace(1.0, 3.0, len(c) - cut)   # Zukunft veraendern
    part = sleeve2(c2, rf, lengths=(6, 9, 12), target=0.20)
    common = full.index[full.index < c.index[cut - 5]]
    assert len(common) > 300
    np.testing.assert_allclose(full.loc[common, "ret"].to_numpy(), part.loc[common, "ret"].to_numpy(), atol=1e-12)


def test_vol_target_reduces_weight_in_wild_market():
    c = _random_close(seed=19, sig=0.03, mu=0.001)
    p = sleeve2(c, _zero_rf(c.index), lengths=(12,), target=0.15)["pos"]
    assert p.max() <= 1.0 + 1e-12
    assert p[p > 0].mean() < 1.0


def test_ulcer_index_basic():
    flat = pd.Series(0.001, index=pd.bdate_range("2020-01-01", periods=300))
    assert h12.ulcer_index(flat) == pytest.approx(0.0)
    r = pd.Series([0.01] * 100 + [-0.2] + [0.0] * 100, index=pd.bdate_range("2020-01-01", periods=201))
    assert h12.ulcer_index(r) > 0.05


def test_konstanz_keys_and_upi():
    c = _random_close(n=2000, seed=23)
    ret = c.pct_change().dropna()
    k = h12.konstanz(ret, _zero_rf(ret.index))
    for key in ("cagr", "ulcer", "upi", "dd10", "pos36", "worst3y", "max_dd"):
        assert key in k
    assert k["upi"] == pytest.approx(k["cagr"] / k["ulcer"])
    assert 0.0 <= k["pos36"] <= 1.0
