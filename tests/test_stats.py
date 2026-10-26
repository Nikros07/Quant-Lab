import numpy as np
import pandas as pd
import pytest

from qlab import stats
from qlab.metrics import drawdown, summarize


def test_psr_monotone_and_half_at_reference():
    assert stats.psr(0.05, 0.05, 1000, 0.0, 3.0) == pytest.approx(0.5)
    assert stats.psr(0.08, 0.0, 1000, 0.0, 3.0) > stats.psr(0.03, 0.0, 1000, 0.0, 3.0)


def test_expected_max_sr_grows_with_trials():
    a = stats.expected_max_sr(10, 0.0001)
    b = stats.expected_max_sr(1000, 0.0001)
    assert 0 < a < b
    assert stats.expected_max_sr(1, 0.0001) == 0.0


def test_deflated_sharpe_penalises_many_trials():
    rng = np.random.default_rng(0)
    r = pd.Series(rng.normal(0.0006, 0.01, 2500), index=pd.bdate_range("2010", periods=2500))
    one = stats.deflated_sharpe(r, 1, 1e-4)
    many = stats.deflated_sharpe(r, 500, 1e-4)
    assert one["dsr"] == pytest.approx(one["psr_vs_zero"])
    assert many["dsr"] < one["dsr"]


def test_bootstrap_identical_series_is_not_significant():
    rng = np.random.default_rng(1)
    r = pd.Series(rng.normal(0.0003, 0.01, 2000), index=pd.bdate_range("2012", periods=2000))
    out = stats.bootstrap_sharpe_diff(r, r, n_boot=300)
    assert abs(out["sharpe_diff"]) < 1e-9
    assert out["p_value"] > 0.2


def test_bootstrap_detects_real_difference():
    rng = np.random.default_rng(2)
    idx = pd.bdate_range("2005", periods=3000)
    bench = pd.Series(rng.normal(0.0002, 0.01, 3000), index=idx)
    strat = bench + 0.0008 + rng.normal(0, 0.001, 3000)  # klar besser
    out = stats.bootstrap_sharpe_diff(strat, bench, n_boot=300)
    assert out["sharpe_diff"] > 0.5 and out["p_value"] < 0.05


def test_pbo_noise_is_near_half_and_skill_is_low():
    rng = np.random.default_rng(3)
    idx = pd.bdate_range("2000", periods=4000)
    noise = pd.DataFrame(rng.normal(0, 0.01, (4000, 30)), index=idx)
    p_noise = stats.pbo_cscv(noise)["pbo"]
    assert 0.25 < p_noise < 0.75
    skill = noise.copy()
    skill[0] = skill[0] + 0.001  # eine Variante hat dauerhaft Vorsprung
    assert stats.pbo_cscv(skill)["pbo"] < 0.1


def test_summarize_constant_growth():
    idx = pd.bdate_range("2015", periods=504)
    r = pd.Series(0.0004, index=idx)
    s = summarize(r)
    years = (idx[-1] - idx[0]).days / 365.25            # Annualisierung nach Kalenderjahren, nicht n/252
    assert s["cagr"] == pytest.approx((1.0004 ** len(idx)) ** (1 / years) - 1, rel=1e-6)
    assert s["max_dd"] == 0.0
    assert drawdown((1 + r).cumprod()).min() == 0.0


def test_summarize_annualisation_with_six_day_weeks():
    """Regression: alte French-Tagesdaten enthalten Samstage (~263 Zeilen/Jahr). CAGR darf nicht
    von der Zeilenzahl/252 abhängen, sondern von Kalenderjahren."""
    idx = pd.date_range("1930-01-01", periods=263 * 10, freq="D")
    idx = idx[idx.dayofweek < 6][: 313 * 3]            # Mo-Sa
    n = len(idx)
    years = (idx[-1] - idx[0]).days / 365.25
    daily = 1.10 ** (years / n) - 1                     # genau 10 % pro Kalenderjahr
    s = summarize(pd.Series(daily, index=idx))
    assert s["cagr"] == pytest.approx(0.10, abs=2e-3)
