"""Tests fuer scripts/check_h20_tranche4.py (H20): nur synthetische Daten, kein Netz."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def _load(name: str):
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


h20 = _load("check_h20_tranche4")
h16 = _load("check_h16_timing_luck")
h12 = _load("check_h12_robust_basket")


def _close(n: int, seed: int, mu: float = 0.0004, sig: float = 0.012) -> pd.Series:
    idx = pd.bdate_range("2000-01-03", periods=n)
    r = np.random.default_rng(seed).normal(mu, sig, n)
    return pd.Series(100.0 * np.cumprod(1.0 + r), index=idx)


def _rf(idx) -> pd.Series:
    return pd.Series(0.00002, index=idx)


def test_tranche4_is_equal_weight_mean_of_four_phases():
    c = _close(700, seed=11)
    rf = _rf(c.index)
    ph = {p: h16.sleeve_phase(c, rf, p)["ret"] for p in h16.PHASES}
    t4 = h20.tranche4_returns(ph)
    manual = pd.concat([ph[p] for p in (0, 5, 10, 15)], axis=1).loc[t4.index].mean(axis=1)
    np.testing.assert_allclose(t4.to_numpy(), manual.to_numpy(), atol=1e-15)
    # Start erst, wenn alle vier Phasen gestartet sind (Phase 15 ist die spaetste der vier)
    assert t4.index[0] == max(ph[p].index[0] for p in (0, 5, 10, 15))
    assert t4.index.is_monotonic_increasing and not t4.isna().any()


def test_phase_list_is_exactly_0_5_10_15():
    assert tuple(h20.PHASES4) == (0, 5, 10, 15)
    assert len(h20.PHASE_NAMES) == 21 and h20.PHASE_NAMES[0] == "phi00" and h20.PHASE_NAMES[-1] == "phi20"


def test_tranche4_weights_are_quarters_and_at_most_one():
    c = _close(700, seed=12)
    rf = _rf(c.index)
    pos = {p: h16.sleeve_phase(c, rf, p)["pos"] for p in (0, 5, 10, 15)}
    idx = pd.concat([pd.Series(v, index=h16.sleeve_phase(c, rf, p).index) for p, v in pos.items()], axis=1).dropna().index
    w = pd.concat([pd.Series(pos[p], index=h16.sleeve_phase(c, rf, p).index) for p in pos], axis=1).loc[idx].mean(axis=1)
    x = w.to_numpy() * 4.0
    np.testing.assert_allclose(x, np.round(x), atol=1e-12)     # Vielfaches von 1/4
    assert (w.to_numpy() <= 1.0 + 1e-12).all() and (w.to_numpy() >= -1e-12).all()


def test_criterion_pass_and_fail_with_constructed_numbers():
    names = h20.PHASE_NAMES
    K = {n: {"cagr": 0.07, "max_dd": -0.15, "upi": 1.0} for n in names}
    K["base1x"] = {"cagr": 0.075, "max_dd": -0.20, "upi": 1.1}
    K["tranche4"] = {"cagr": 0.069, "max_dd": -0.14, "upi": 1.05}     # a) -0,14 > -0,15 ok; b) 1,05 >= 1,0 ok; c) 0,6 Pp Abstand ok
    c = h20.criterion(K)
    assert c["a"] and c["b"] and c["c"] and c["ok"]
    assert abs(c["gap_cagr"] + 0.006) < 1e-12

    K["tranche4"] = {"cagr": 0.0681, "max_dd": -0.14, "upi": 1.05}   # c) 0,69 Pp Abstand: knapp innerhalb
    assert h20.criterion(K)["c"] and h20.criterion(K)["ok"]
    K["tranche4"] = {"cagr": 0.0679, "max_dd": -0.14, "upi": 1.05}   # c) 0,71 Pp Abstand: knapp ausserhalb
    assert not h20.criterion(K)["c"] and not h20.criterion(K)["ok"]

    K["tranche4"] = {"cagr": 0.07, "max_dd": -0.16, "upi": 1.05}      # a) schlechter als Median -> nicht erfuellt
    c = h20.criterion(K)
    assert not c["a"] and c["b"] and c["c"] and not c["ok"]

    K["tranche4"] = {"cagr": 0.07, "max_dd": -0.14, "upi": 0.99}      # b) UPI unter Median -> nicht erfuellt
    c = h20.criterion(K)
    assert c["a"] and not c["b"] and not c["ok"]

    K["tranche4"] = {"cagr": 0.07, "max_dd": -0.15, "upi": 1.0}       # a) gleich dem Median ist NICHT besser
    assert not h20.criterion(K)["a"]


def test_criterion_median_uses_the_21_phases_only():
    names = h20.PHASE_NAMES
    K = {n: {"cagr": 0.07, "max_dd": -0.15, "upi": 1.0} for n in names}
    K["base1x"] = {"cagr": 0.07, "max_dd": -0.30, "upi": 5.0}         # darf den Median nicht beeinflussen
    K["tranche4"] = {"cagr": 0.07, "max_dd": -0.14, "upi": 1.0}
    c = h20.criterion(K)
    assert abs(c["median_dd"] + 0.15) < 1e-12 and abs(c["median_upi"] - 1.0) < 1e-12


def test_causality_future_change_does_not_alter_past_tranche4():
    idx = pd.bdate_range("2000-01-03", periods=900)
    c = pd.Series(100.0 * np.cumprod(1.0 + np.random.default_rng(5).normal(0.0004, 0.012, len(idx))), index=idx)
    rf = pd.Series(0.0, index=idx)
    k = 700
    c2 = c.copy()
    c2.iloc[k + 1:] *= np.linspace(1.0, 0.3, len(c) - k - 1)           # Zukunft nach Tag k veraendern
    a = h20.tranche4_returns({p: h16.sleeve_phase(c, rf, p)["ret"] for p in h16.PHASES})
    b = h20.tranche4_returns({p: h16.sleeve_phase(c2, rf, p)["ret"] for p in h16.PHASES})
    past = a.index[a.index <= idx[k]]
    assert len(past) > 100
    np.testing.assert_allclose(a.loc[past].to_numpy(), b.loc[past].to_numpy(), atol=1e-15)


def test_base1x_equals_h12_sleeve2_monthend_12m():
    c = _close(900, seed=13)
    rf = _rf(c.index)
    ours = h20.base1x_returns(c, rf)
    ref = h12.sleeve2(c, rf, lengths=(12,), target=None)["ret"]
    assert ours.index.equals(ref.index)
    np.testing.assert_allclose(ours.to_numpy(), ref.to_numpy(), atol=1e-15)
