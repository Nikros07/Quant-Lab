"""Tests fuer scripts/check_h21_fvg_stop.py (sleeve5, fvg_events, H21): nur synthetische Daten, kein Netz."""
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


h21 = _load("check_h21_fvg_stop")
h13 = _load("check_h13_ratchet_stop")
sleeve5 = h21.sleeve5
fvg_events = h21.fvg_events
sleeve3 = h13.sleeve3
SQRT12 = float(np.sqrt(12.0))


def _ohlc(n=1500, seed=1, mu=0.0003, sig=0.012):
    """Synthetische Tages-OHLC mit Schluss als Random Walk; High/Low um Eroeffnung und Schluss."""
    rng = np.random.default_rng(seed)
    r = rng.normal(mu, sig, n)
    c = 100.0 * np.cumprod(1.0 + r)
    op = c * (1.0 + rng.normal(0.0, sig * 0.5, n))
    span = np.abs(rng.normal(0.0, sig * 0.8, n)) * c + 0.01
    h = np.maximum(op, c) + 0.5 * span
    lo = np.minimum(op, c) - 0.5 * span
    idx = pd.bdate_range("2000-01-03", periods=n)
    return pd.Series(c, idx), pd.Series(h, idx), pd.Series(lo, idx)


def _zero_rf(idx) -> pd.Series:
    return pd.Series(0.0, index=idx)


def test_fvg_handbeispiel_und_mindestgroesse():
    # Tage 0..5. Bullisch (Low[t] > High[t-2]): t=2 (11.5 > 10), t=3 (12.5 > 11), t=5 (13.5 > 13); t=4 nein (12.0 = 12.0)
    high = pd.Series([10.0, 11.0, 12.0, 13.0, 13.0, 14.0])
    low = pd.Series([9.0, 10.5, 11.5, 12.5, 12.0, 13.5])
    close = pd.Series([9.5, 11.0, 12.0, 12.8, 12.5, 13.8])
    fv = fvg_events(high, low, close, atr_n=2, min_atr=0.0)
    assert fv["bullish"].tolist() == [False, False, True, True, False, True]
    assert fv.loc[2, "lower"] == 10.0 and fv.loc[2, "upper"] == 11.5
    assert fv.loc[2, "size"] == pytest.approx(1.5)
    # Mindestgroesse: mit unerreichbarer Schwelle bleibt bullisch, zaehlt aber nicht
    fv_big = fvg_events(high, low, close, atr_n=2, min_atr=1000.0)
    assert fv_big["bullish"].tolist() == fv["bullish"].tolist()
    assert not fv_big["valid"].any()


def test_fvg_wird_erst_zum_schluss_von_t_bekannt():
    c, h, lo = _ohlc(n=400, seed=2)
    cut = 250
    h2, lo2, c2 = h.copy(), lo.copy(), c.copy()
    h2.iloc[cut:] = h2.iloc[cut:] * 0.5                  # drastische Zukunftsaenderung
    lo2.iloc[cut:] = lo2.iloc[cut:] * 0.5
    c2.iloc[cut:] = c2.iloc[cut:] * 0.5
    a = fvg_events(h, lo, c)
    b = fvg_events(h2, lo2, c2)
    for col in ["bullish", "valid", "lower", "upper", "atr"]:
        np.testing.assert_array_equal(a[col].iloc[:cut].to_numpy(), b[col].iloc[:cut].to_numpy())
    assert a["valid"].iloc[:cut].sum() > 5


def test_mitigation_ungueltig_bei_schluss_unter_unterem_rand():
    high = pd.Series([10.0, 11.0, 12.0, 12.5, 12.6, 12.7])
    low = pd.Series([9.0, 10.5, 11.5, 11.8, 12.2, 12.3])
    # FVG an t=2 mit unterem Rand 10 und oberem Rand 11,5
    close_mit = pd.Series([9.5, 11.0, 12.0, 9.5, 12.5, 12.6])     # Tag 3 schliesst unter 10
    close_ohne = pd.Series([9.5, 11.0, 12.0, 11.5, 12.5, 12.6])   # nie unter 10
    fv1 = fvg_events(high, low, close_mit, atr_n=2, min_atr=0.0)
    fv2 = fvg_events(high, low, close_ohne, atr_n=2, min_atr=0.0)
    assert fv1.loc[2, "valid"] and fv1.loc[2, "mit"] == 3
    assert fv2.loc[2, "valid"] and np.isnan(fv2.loc[2, "mit"])


@pytest.mark.parametrize("seed", [3, 5])
def test_none_reproduces_sleeve3_none(seed):
    c, h, lo = _ohlc(seed=seed, sig=0.015)
    rf = pd.Series(0.00005, index=c.index)
    a = sleeve5(c, h, lo, rf, stop_mode=None)
    b = sleeve3(c, rf, stop_mode=None)
    np.testing.assert_allclose(a["ret"].to_numpy(), b["ret"].to_numpy(), atol=1e-12)
    np.testing.assert_allclose(a["pos"].to_numpy(), b["pos"].to_numpy(), atol=1e-12)


def test_future_change_does_not_change_past_returns_fvg_trail():
    c, h, lo = _ohlc(n=1400, seed=17, mu=0.0005, sig=0.014)
    rf = _zero_rf(c.index)
    full = sleeve5(c, h, lo, rf, stop_mode="fvg_trail")
    cut = 1100
    c2, h2, lo2 = c.copy(), h.copy(), lo.copy()
    fac = np.linspace(1.0, 0.4, len(c) - cut)
    c2.iloc[cut:] = c2.iloc[cut:] * fac
    h2.iloc[cut:] = h2.iloc[cut:] * fac
    lo2.iloc[cut:] = lo2.iloc[cut:] * fac
    part = sleeve5(c2, h2, lo2, rf, stop_mode="fvg_trail")
    common = full.index[full.index < c.index[cut - 5]]
    assert len(common) > 300
    np.testing.assert_allclose(full.loc[common, "ret"].to_numpy(), part.loc[common, "ret"].to_numpy(), atol=1e-12)
    np.testing.assert_allclose(full.loc[common, "stop"].to_numpy(), part.loc[common, "stop"].to_numpy(),
                               atol=1e-12, equal_nan=True)


def test_fvg_trail_stop_never_decreases_within_holding():
    c, h, lo = _ohlc(seed=7, mu=0.0006, sig=0.011)
    df = sleeve5(c, h, lo, _zero_rf(c.index), stop_mode="fvg_trail")
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
    assert seen > 100


def test_initial_stop_distance_between_1R_and_4R():
    c, h, lo = _ohlc(n=2000, seed=21, mu=0.0004, sig=0.013)
    df = sleeve5(c, h, lo, _zero_rf(c.index), stop_mode="fvg_stop")
    r = c.pct_change(fill_method=None)
    sigma = np.sqrt((r ** 2).ewm(halflife=20, adjust=False).mean() * 252).to_numpy()
    pos = df["pos"].to_numpy()
    stop = df["stop"].to_numpy()
    cv = c.loc[df.index].to_numpy()
    checked = 0
    for i in range(1, len(df)):
        if pos[i] > 0 and pos[i - 1] == 0 and np.isfinite(stop[i]):
            E = cv[i - 1]
            f_glob = c.index.get_loc(df.index[i]) - 2
            R = 2.0 * sigma[f_glob] / SQRT12 * E
            ratio = (E - stop[i]) / R
            assert 1.0 - 1e-9 <= ratio <= 4.0 + 1e-9
            checked += 1
    assert checked >= 3


def test_ohne_fvg_genau_1R():
    # Ueberlappende Balken: Low[t] = C - 1 liegt stets unter High[t-2] = C' + 1, also keine bullische FVG
    n = 900
    idx = pd.bdate_range("2000-01-03", periods=n)
    c = pd.Series(100.0 * np.exp(0.001 * np.arange(n)), index=idx)
    h = c + 1.0
    lo = c - 1.0
    fv = fvg_events(h, lo, c)
    assert not fv["bullish"].any()
    info = {}
    df = sleeve5(c, h, lo, _zero_rf(idx), stop_mode="fvg_stop", info=info)
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
    assert info["no_fvg"] == info["entries"] == checked


def test_reentry_only_two_days_after_month_end():
    from qlab.calendar import month_end_flags

    c, h, lo = _ohlc(seed=13, mu=0.0004, sig=0.02)
    df = sleeve5(c, h, lo, _zero_rf(c.index), stop_mode="fvg_stop")
    pos = df["pos"].to_numpy()
    flags = month_end_flags(df.index).to_numpy()
    entries = 0
    for i in range(1, len(df)):
        if pos[i] > 0 and pos[i - 1] == 0:
            entries += 1
            assert i >= 2 and bool(flags[i - 2])
    assert entries >= 2


def test_invalid_mode_rejected():
    c, h, lo = _ohlc()
    with pytest.raises(ValueError):
        sleeve5(c, h, lo, _zero_rf(c.index), stop_mode="foo")
