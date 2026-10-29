"""Tests fuer P3 (Vergleich mit Benchmarks), synthetische Daten, kein Netz."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import check_p3_benchmarks as p3


def test_calendar_returns_chain_within_year():
    idx = pd.to_datetime(["2020-03-02", "2020-03-03", "2020-03-04", "2021-01-04"])
    r = pd.Series([0.10, 0.10, 0.0, -0.05], index=idx)
    cal = p3.calendar_returns(r)
    assert cal.loc[2020] == pytest.approx(0.21)
    assert cal.loc[2021] == pytest.approx(-0.05)


def test_returns_on_compounds_gaps():
    idx = pd.bdate_range("2024-01-01", periods=6)
    r = pd.Series([0.01, 0.02, -0.01, 0.03, 0.0, 0.02], index=idx)
    level = p3.nav(r)
    common = idx[[0, 2, 5]]                      # Tage 1 und 3 fehlen
    out = p3.returns_on(level, common)
    assert out.iloc[0] == pytest.approx((1.02) * (0.99) - 1.0)         # Tage 1 und 2
    assert out.iloc[1] == pytest.approx((1.03) * (1.0) * (1.02) - 1.0)  # Tage 3 bis 5


def test_returns_on_raises_on_missing_day():
    idx = pd.bdate_range("2024-01-01", periods=5)
    level = pd.Series([1.0, 1.1, 1.2, 1.3, 1.4], index=idx)
    with pytest.raises(ValueError):
        p3.returns_on(level, idx.append(pd.DatetimeIndex(["2024-02-05"])))


def test_years_ahead_counts_only_common_years():
    a = pd.Series([0.10, -0.05, 0.02], index=[2019, 2020, 2021])
    b = pd.Series([0.05, 0.00, 0.04, 0.50], index=[2019, 2020, 2021, 2022])
    assert p3.years_ahead(a, b) == (1, 3)


def test_full_year_returns_drops_partial_first_year():
    idx = pd.bdate_range("2019-03-01", "2021-12-31")
    r = pd.Series(0.0001, index=idx)
    fy = p3.full_year_returns(r)
    assert list(fy.index) == [2020, 2021]


def test_stats_end100_and_negative_years():
    idx = pd.bdate_range("2019-01-02", "2021-12-31")
    n = len(idx)
    r = pd.Series(0.0, index=idx)
    r.loc["2020-06-01"] = -0.10          # 2020 im Minus
    r.loc["2021-06-01"] = 0.10           # 2021 im Plus
    rf = pd.Series(0.0, index=idx)
    k = p3.stats(r, rf)
    assert k["end100"] == pytest.approx(100.0 * 0.9 * 1.1)
    assert k["years_neg"] == 1
    assert k["years_n"] == 3


def test_clip_end_removes_holdout():
    idx = pd.to_datetime(["2022-12-29", "2022-12-30", "2023-01-03"])
    s = pd.Series([1.0, 2.0, 3.0], index=idx)
    assert p3.clip_end(s).index[-1] == pd.Timestamp("2022-12-30")
