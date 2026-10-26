"""Tests fuer scripts/check_h19_sr_stop.py (sleeve4, pivot_lows, H19): nur synthetische Daten, kein Netz."""
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


h19 = _load("check_h19_sr_stop")
h13 = _load("check_h13_ratchet_stop")
sleeve4 = h19.sleeve4
pivot_lows = h19.pivot_lows
sleeve3 = h13.sleeve3
SQRT12 = float(np.sqrt(12.0))


def _random_close(n=1500, seed=1, mu=0.0003, sig=0.012) -> pd.Series:
    rng = np.random.default_rng(seed)
    r = rng.normal(mu, sig, n)
    return pd.Series(100.0 * np.cumprod(1.0 + r), index=pd.bdate_range("2000-01-03", periods=n))


def _zero_rf(idx) -> pd.Series:
    return pd.Series(0.0, index=idx)


def test_pivot_confirmed_only_k_days_later():
    # V-foermige Delle mit Tief am Tag p = 60 (eindeutiges Minimum)
    n = 200
    p, k = 60, 10
    c = np.full(n, 100.0)
    c[:] += np.linspace(0.0, 5.0, n)                     # leicht steigend
    c[p] = 80.0                                          # klares Tief
    s = pd.Series(c, index=pd.bdate_range("2000-01-03", periods=n))
    level, conf = pivot_lows(s, k)
    assert np.isfinite(level[p])
    assert level[p] == 80.0
    assert conf[p] == p + k                              # Bestaetigung erst an Tag p+k
    # Nur mit Daten bis p+k-1 ist das Pivot noch nicht bestimmbar (Fenster unvollstaendig)
    level_ok, _ = pivot_lows(s.iloc[: p + k + 1], k)     # Daten bis Tag p+k (Index 0..p+k)
    assert np.isfinite(level_ok[p])
    level_early, _ = pivot_lows(s.iloc[: p + k], k)      # Daten nur bis p+k-1: Fenster unvollstaendig
    assert not np.isfinite(level_early[p])


def test_future_change_does_not_change_past_returns_sr_trail():
    c = _random_close(n=1400, seed=17, mu=0.0005, sig=0.014)
    rf = _zero_rf(c.index)
    full = sleeve4(c, rf, stop_mode="sr_trail")
    cut = 1100
    c2 = c.copy()
    c2.iloc[cut:] = c2.iloc[cut:] * np.linspace(1.0, 0.4, len(c) - cut)
    part = sleeve4(c2, rf, stop_mode="sr_trail")
    common = full.index[full.index < c.index[cut - 5]]
    assert len(common) > 300
    np.testing.assert_allclose(full.loc[common, "ret"].to_numpy(), part.loc[common, "ret"].to_numpy(), atol=1e-12)
    np.testing.assert_allclose(full.loc[common, "stop"].to_numpy(), part.loc[common, "stop"].to_numpy(),
                               atol=1e-12, equal_nan=True)


@pytest.mark.parametrize("seed", [3, 5])
def test_none_reproduces_sleeve3_none(seed):
    c = _random_close(seed=seed, sig=0.015)
    rf = pd.Series(0.00005, index=c.index)
    a = sleeve4(c, rf, stop_mode=None)
    b = sleeve3(c, rf, stop_mode=None)
    np.testing.assert_allclose(a["ret"].to_numpy(), b["ret"].to_numpy(), atol=1e-12)
    np.testing.assert_allclose(a["pos"].to_numpy(), b["pos"].to_numpy(), atol=1e-12)


def test_sr_trail_stop_never_decreases_within_a_holding_period():
    c = _random_close(seed=7, mu=0.0006, sig=0.011)
    df = sleeve4(c, _zero_rf(c.index), stop_mode="sr_trail")
    stop = df["stop"].to_numpy()
    pos = df["pos"].to_numpy()
    prev = np.nan
    seen = 0
    for i in range(len(df)):
        if pos[i] == 0.0 or np.isnan(stop[i]):
            prev = np.nan                                    # neue Haltephase: Stop beginnt neu
            continue
        if np.isfinite(prev):
            assert stop[i] >= prev - 1e-9
            seen += 1
        prev = stop[i]
    assert seen > 200


def test_initial_stop_distance_between_1R_and_4R():
    c = _random_close(n=2000, seed=21, mu=0.0004, sig=0.013)
    rf = _zero_rf(c.index)
    df = sleeve4(c, rf, stop_mode="sr_stop")
    r = c.pct_change(fill_method=None)
    sigma = np.sqrt((r ** 2).ewm(halflife=20, adjust=False).mean() * 252).to_numpy()
    pos = df["pos"].to_numpy()
    stop = df["stop"].to_numpy()
    cv = c.loc[df.index].to_numpy()
    checked = 0
    for i in range(1, len(df)):
        if pos[i] > 0 and pos[i - 1] == 0 and np.isfinite(stop[i]):
            gi = df.index.get_loc(df.index[i])
            E = cv[i - 1]
            f_glob = c.index.get_loc(df.index[i]) - 2
            R = 2.0 * sigma[f_glob] / SQRT12 * E
            ratio = (E - stop[i]) / R
            assert 1.0 - 1e-9 <= ratio <= 4.0 + 1e-9
            checked += 1
    assert checked >= 3


def test_without_pivot_distance_is_1R():
    # strikt steigender Kurs: kein Pivot-Tief (c[p] <= c[p-k] nie erfuellt) -> Abstand 1R
    n = 900
    idx = pd.bdate_range("2000-01-03", periods=n)
    c = pd.Series(100.0 * np.exp(0.001 * np.arange(n)), index=idx)
    df = sleeve4(c, _zero_rf(idx), stop_mode="sr_stop")
    r = c.pct_change(fill_method=None)
    sigma = np.sqrt((r ** 2).ewm(halflife=20, adjust=False).mean() * 252).to_numpy()
    pos = df["pos"].to_numpy()
    stop = df["stop"].to_numpy()
    checked = 0
    for i in range(1, len(df)):
        if pos[i] > 0 and pos[i - 1] == 0:
            gi = idx.get_loc(df.index[i])
            E = c.iloc[gi - 1]
            R = 2.0 * sigma[gi - 2] / SQRT12 * E
            assert stop[i] == pytest.approx(E - R, rel=1e-9)
            checked += 1
    assert checked >= 1


def test_reentry_only_two_days_after_month_end():
    from qlab.calendar import month_end_flags

    c = _random_close(seed=13, mu=0.0004, sig=0.02)
    df = sleeve4(c, _zero_rf(c.index), stop_mode="sr_stop")
    pos = df["pos"].to_numpy()
    flags = month_end_flags(df.index).to_numpy()
    entries = 0
    # Jeder Wechsel von 0 auf 1 (Einstieg oder Wiedereinstieg) liegt genau 2 Handelstage nach einem Monatsende
    for i in range(1, len(df)):
        if pos[i] > 0 and pos[i - 1] == 0:
            entries += 1
            assert i >= 2 and bool(flags[i - 2])
    assert entries >= 2


def test_invalid_mode_rejected():
    c = _random_close()
    with pytest.raises(ValueError):
        sleeve4(c, _zero_rf(c.index), stop_mode="foo")
