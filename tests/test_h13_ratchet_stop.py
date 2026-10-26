"""Tests fuer scripts/check_h13_ratchet_stop.py (sleeve3, H13): nur synthetische Daten, kein Netz."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def _load(name: str):
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


h13 = _load("check_h13_ratchet_stop")
h11 = _load("check_trend_vt_basket")
sleeve3 = h13.sleeve3


def _random_close(n=1500, seed=1, mu=0.0003, sig=0.012) -> pd.Series:
    rng = np.random.default_rng(seed)
    r = rng.normal(mu, sig, n)
    return pd.Series(100.0 * np.cumprod(1.0 + r), index=pd.bdate_range("2000-01-03", periods=n))


def _zero_rf(idx) -> pd.Series:
    return pd.Series(0.0, index=idx)


def test_no_stop_reproduces_base1x_of_h11():
    c = _random_close(seed=3)
    rf = _zero_rf(c.index)
    a = sleeve3(c, rf, stop_mode=None)
    b = h11.sleeve(c, rf, vol_scaled=False, cap=1.0, bps=10.0)
    np.testing.assert_allclose(a["ret"].to_numpy(), b["ret"].to_numpy(), atol=1e-12)


def test_chand_reproduces_h11_trail_without_vol_scaling():
    c = _random_close(seed=5, sig=0.015)
    rf = pd.Series(0.00005, index=c.index)
    a = sleeve3(c, rf, stop_mode="chand", m=2.0)
    b = h11.sleeve(c, rf, vol_scaled=False, cap=1.0, trail_m=2.0, bps=10.0)
    np.testing.assert_allclose(a["ret"].to_numpy(), b["ret"].to_numpy(), atol=1e-12)
    np.testing.assert_allclose(a["pos"].to_numpy(), b["pos"].to_numpy(), atol=1e-12)


@pytest.mark.parametrize("mode", ["chand_ratchet", "steps"])
def test_stop_never_decreases_within_a_holding_period(mode):
    c = _random_close(seed=7, mu=0.0006, sig=0.011)
    df = sleeve3(c, _zero_rf(c.index), stop_mode=mode)
    stop = df["stop"].to_numpy()
    pos = df["pos"].to_numpy()
    prev = np.nan
    seen = 0
    for i in range(len(df)):
        if pos[i] == 0.0 or np.isnan(stop[i]):
            prev = np.nan                                   # neue Haltephase: Stop beginnt neu
            continue
        if np.isfinite(prev):
            assert stop[i] >= prev - 1e-9
            seen += 1
        prev = stop[i]
    assert seen > 200


def test_steps_moves_to_breakeven_after_one_R_and_locks_profit():
    n = 700
    idx = pd.bdate_range("2000-01-03", periods=n)
    rng = np.random.default_rng(11)
    r = rng.normal(0.0, 0.004, n)                           # ruhig
    r[300:] += 0.0012                                       # kraeftiger Aufwaertstrend ab Tag 300
    c = pd.Series(100.0 * np.cumprod(1.0 + r), index=idx)
    df = sleeve3(c, _zero_rf(idx), stop_mode="steps")
    held = df[(df["pos"] > 0) & df["stop"].notna()]
    assert not held.empty
    first = held.iloc[0]
    last = held.iloc[-1]
    # Einstiegskurs ~ Anfangsstop-Niveau darueber; spaeter liegt der Stop deutlich ueber dem Anfangsstop (im Gewinn)
    assert last["stop"] > first["stop"]
    entry_idx = df.index.get_loc(held.index[0]) - 1
    assert last["stop"] > c.loc[df.index[0]:].iloc[entry_idx] * 0.99


def test_after_stop_no_reentry_before_next_month_end():
    c = _random_close(seed=13, mu=0.0004, sig=0.02)
    df = sleeve3(c, _zero_rf(c.index), stop_mode="steps")
    pos = df["pos"].to_numpy()
    flags = pd.Series(
        __import__("qlab.calendar", fromlist=["month_end_flags"]).month_end_flags(df.index).to_numpy(), index=df.index)
    # Jeder Wechsel von 0 auf 1 muss genau 2 Handelstage nach einem Monatsende liegen
    for i in range(1, len(df)):
        if pos[i] > 0 and pos[i - 1] == 0:
            assert i >= 2 and bool(flags.iloc[i - 2]) or i < 2


def test_invalid_mode_rejected():
    c = _random_close()
    with pytest.raises(ValueError):
        sleeve3(c, _zero_rf(c.index), stop_mode="foo")


def test_causality_future_does_not_change_past():
    c = _random_close(n=1400, seed=17)
    rf = _zero_rf(c.index)
    full = sleeve3(c, rf, stop_mode="steps")
    cut = 1100
    c2 = c.copy()
    c2.iloc[cut:] = c2.iloc[cut:] * np.linspace(1.0, 0.4, len(c) - cut)
    part = sleeve3(c2, rf, stop_mode="steps")
    common = full.index[full.index < c.index[cut - 5]]
    assert len(common) > 300
    np.testing.assert_allclose(full.loc[common, "ret"].to_numpy(), part.loc[common, "ret"].to_numpy(), atol=1e-12)
