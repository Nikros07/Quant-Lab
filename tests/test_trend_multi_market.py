"""Tests für scripts/check_trend_multi_market.py (monthly_state): nur synthetische Daten, kein Netz."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import month_end_flags

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_trend_multi_market.py"
_spec = importlib.util.spec_from_file_location("check_trend_multi_market", SCRIPT)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)
monthly_state = mod.monthly_state


def test_steigende_reihe_nach_warmup_immer_long():
    idx = pd.bdate_range("2000-01-03", "2010-12-31")
    close = pd.Series(np.linspace(100.0, 500.0, len(idx)), index=idx)
    s = monthly_state(close)
    assert len(s) > 0
    assert s.all()


def test_fallende_reihe_nie_long():
    idx = pd.bdate_range("2000-01-03", "2010-12-31")
    close = pd.Series(np.linspace(500.0, 100.0, len(idx)), index=idx)
    s = monthly_state(close)
    assert len(s) > 0
    assert not s.any()


def test_erster_zustand_am_zwoelften_monatsende():
    idx = pd.bdate_range("2000-01-03", "2005-12-30")
    close = pd.Series(np.linspace(100.0, 500.0, len(idx)), index=idx)
    s = monthly_state(close)
    month_ends = idx[month_end_flags(idx).to_numpy()]
    assert s.index[0] == month_ends[11]


@pytest.mark.parametrize("cut", ["2003-06-17", "2003-06-30", "2004-11-30"])
def test_kausal_spaetere_kurse_aendern_frueheren_zustand_nicht(cut):
    rng = np.random.default_rng(1)
    idx = pd.bdate_range("2000-01-03", "2008-12-31")
    close = pd.Series(100 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, len(idx)))), index=idx)
    alt = close.copy()
    after = alt.index > pd.Timestamp(cut)
    alt[after] = rng.uniform(10.0, 1000.0, int(after.sum()))
    d = pd.Timestamp(cut)
    s1, s2 = monthly_state(close), monthly_state(alt)
    assert len(s1.loc[:d]) > 0
    pd.testing.assert_series_equal(s1.loc[:d], s2.loc[:d])


def test_zustand_aendert_sich_nur_an_monatsenden():
    rng = np.random.default_rng(2)
    idx = pd.bdate_range("2000-01-03", "2012-12-31")
    close = pd.Series(100 * np.exp(np.cumsum(rng.normal(0.0, 0.02, len(idx)))), index=idx)
    s = monthly_state(close)
    flags = month_end_flags(idx).reindex(s.index).to_numpy()
    changed = s.astype(int).diff().fillna(0).ne(0).to_numpy()
    assert changed.any()                      # sonst wäre der Test leer
    assert not (changed & ~flags).any()
