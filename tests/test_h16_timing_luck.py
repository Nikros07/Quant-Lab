"""Tests fuer scripts/check_h16_timing_luck.py (H16): nur synthetische Daten, kein Netz."""
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


h16 = _load("check_h16_timing_luck")
h12 = _load("check_h12_robust_basket")
sleeve_phase = h16.sleeve_phase


def _rand_r(n, seed, mu=0.0003, sig=0.01):
    return np.random.default_rng(seed).normal(mu, sig, n)


def _month21_index(n_months=40) -> pd.DatetimeIndex:
    """Index mit genau 21 Datentagen je Kalendermonat (die ersten 21 Kalendertage), also Monatsende = Position 20 + 21k."""
    days = []
    for m in pd.period_range("2000-01", periods=n_months, freq="M"):
        start = m.start_time
        days.extend(pd.date_range(start, periods=21, freq="D"))
    return pd.DatetimeIndex(days)


def _close_on(idx, seed=1, mu=0.0003, sig=0.01) -> pd.Series:
    return pd.Series(100.0 * np.cumprod(1.0 + _rand_r(len(idx), seed, mu, sig)), index=idx)


def _zero_rf(idx) -> pd.Series:
    return pd.Series(0.0, index=idx)


def test_phase20_equals_base1x_when_months_have_21_days():
    idx = _month21_index(40)
    c = _close_on(idx, seed=3)
    rf = pd.Series(0.00004, index=idx)
    a = sleeve_phase(c, rf, 20)
    b = h12.sleeve2(c, rf, lengths=(12,), target=None)
    assert a.index.equals(b.index)
    np.testing.assert_allclose(a["ret"].to_numpy(), b["ret"].to_numpy(), atol=1e-12)
    np.testing.assert_allclose(a["pos"].to_numpy(), b["pos"].to_numpy(), atol=1e-12)


def test_other_phase_differs_from_base1x():
    idx = _month21_index(60)
    c = _close_on(idx, seed=4)
    rf = _zero_rf(idx)
    a = sleeve_phase(c, rf, 5).reindex(h12.sleeve2(c, rf).index)
    b = h12.sleeve2(c, rf)
    assert not np.allclose(np.nan_to_num(a["pos"].to_numpy()), b["pos"].to_numpy())


def test_causality_future_change_does_not_alter_past():
    idx = pd.bdate_range("2000-01-03", periods=900)
    c = _close_on(idx, seed=5)
    rf = _zero_rf(idx)
    k = 700
    c2 = c.copy()
    c2.iloc[k + 1:] *= np.linspace(1.0, 0.3, len(c) - k - 1)     # Zukunft nach Tag k veraendern
    for phi in (0, 7, 20):
        a = sleeve_phase(c, rf, phi)
        b = sleeve_phase(c2, rf, phi)
        j = a.index.get_loc(idx[k])
        np.testing.assert_allclose(a["pos"].to_numpy()[: j + 1], b["pos"].to_numpy()[: j + 1], atol=1e-15)
        np.testing.assert_allclose(a["ret"].to_numpy()[: j + 1], b["ret"].to_numpy()[: j + 1], atol=1e-15)


def test_execution_lag_position_changes_only_two_days_after_decision():
    idx = pd.bdate_range("2000-01-03", periods=800)
    c = _close_on(idx, seed=6, mu=0.0005, sig=0.012)
    rf = _zero_rf(idx)
    for phi in (0, 3, 13):
        s = sleeve_phase(c, rf, phi)
        pos = s["pos"].to_numpy()
        pos_i = np.array([idx.get_loc(d) for d in s.index])
        change = np.where(np.abs(np.diff(pos)) > 0)[0] + 1       # Index in s, an dem die Position wechselt
        assert len(change) > 0
        # Wechsel nur an Positionen i+2 mit i = phi (mod 21), i >= 231
        for ch in change:
            i = pos_i[ch] - 2
            assert i % 21 == phi and i >= 231


def test_strict_uptrend_is_always_long_with_single_entry_cost():
    idx = pd.bdate_range("2000-01-03", periods=700)
    c = pd.Series(100.0 * 1.001 ** np.arange(700), index=idx)
    rf = _zero_rf(idx)
    s = sleeve_phase(c, rf, 4, bps=10.0)
    pos = s["pos"].to_numpy()
    assert pos[0] == 0.0 and pos[-1] == 1.0
    first_long = np.argmax(pos > 0)
    assert (pos[first_long:] == 1.0).all()
    r = c.pct_change().reindex(s.index).fillna(0.0).to_numpy()
    expected = pos * r
    expected[first_long] -= 10.0 / 1e4
    np.testing.assert_allclose(s["ret"].to_numpy(), expected, atol=1e-12)


def test_downtrend_is_flat_and_earns_rf_only():
    idx = pd.bdate_range("2000-01-03", periods=600)
    c = pd.Series(100.0 * 0.999 ** np.arange(600), index=idx)
    rf = pd.Series(0.0001, index=idx)
    s = sleeve_phase(c, rf, 9)
    assert (s["pos"] == 0.0).all()
    np.testing.assert_allclose(s["ret"].to_numpy(), 0.0001, atol=1e-15)


def test_signal_matches_manual_ma_at_decision_day():
    idx = pd.bdate_range("2000-01-03", periods=700)
    c = _close_on(idx, seed=8)
    rf = _zero_rf(idx)
    phi = 11
    s = sleeve_phase(c, rf, phi)
    pos = pd.Series(s["pos"].to_numpy(), index=s.index)
    arr = c.to_numpy()
    checked = 0
    for i in range(phi + 21 * 11 + 21 * 3, 690, 21):
        if i < 231:
            continue
        ma = np.mean([arr[i - 21 * j] for j in range(12)])
        want = 1.0 if arr[i] >= ma else 0.0
        assert pos.iloc[pos.index.get_loc(idx[i + 2])] == want
        checked += 1
    assert checked >= 5


def test_tranche_is_mean_of_phases_and_starts_when_all_started():
    idx = pd.bdate_range("2000-01-03", periods=700)
    c = _close_on(idx, seed=9)
    rf = pd.Series(0.00002, index=idx)
    ph = {p: sleeve_phase(c, rf, p)["ret"] for p in h16.PHASES}
    t = h16.tranche_returns(ph)
    assert t.index[0] == ph[20].index[0]                       # spaetester Start = Phase 20
    manual = pd.concat(list(ph.values()), axis=1).loc[t.index].mean(axis=1)
    np.testing.assert_allclose(t.to_numpy(), manual.to_numpy(), atol=1e-15)


def test_invalid_phase_raises():
    idx = pd.bdate_range("2000-01-03", periods=400)
    c = _close_on(idx)
    with pytest.raises(ValueError):
        sleeve_phase(c, _zero_rf(idx), 21)
    with pytest.raises(ValueError):
        sleeve_phase(c, _zero_rf(idx), -1)


def test_evaluate_thresholds():
    names = [f"phi{p:02d}" for p in range(21)]
    K = {n: {"cagr": 0.07, "max_dd": -0.15, "upi": 1.0} for n in names}
    K["tranche21"] = {"cagr": 0.07, "max_dd": -0.14, "upi": 1.05}
    ev = h16.evaluate(K, names)
    assert not ev["luck"] and ev["tranche_ok"]
    K["phi03"] = {"cagr": 0.07, "max_dd": -0.15, "upi": 1.30}   # Spanne 0,30 > 0,25
    assert h16.evaluate(K, names)["luck"]
    K["phi03"] = {"cagr": 0.07, "max_dd": -0.19, "upi": 1.0}    # MaxDD-Spanne 4 Pp > 3 Pp
    assert h16.evaluate(K, names)["luck"]
    K["tranche21"] = {"cagr": 0.07, "max_dd": -0.16, "upi": 1.05}  # MaxDD schlechter als Median
    assert not h16.evaluate(K, names)["tranche_ok"]
