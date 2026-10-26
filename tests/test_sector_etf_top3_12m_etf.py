"""Tests der ETF-Fassung der Faber-Sektorrotation (9 SPDR-Sektoren). Synthetische Panels, kein Netz."""
import numpy as np
import pandas as pd
import pytest

from qlab.calendar import NYSE_BDAY
from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import sector_etf_top3_12m_etf as etf
from strategies.sector_etf_top3_12m import rotation_weights
from strategies.sector_etf_top3_12m_etf import FILTER, SPEC, UNIVERSE, weights

VARIANTS = ["base"] + sorted(SPEC["variants"])


def params_for(variant: str) -> dict:
    return dict(SPEC["params"]) if variant == "base" else {**SPEC["params"], **SPEC["variants"][variant]}


def make_panel(seed=0, start="2004-01-01", end="2008-12-31", xl_start=None, vol=0.012):
    """9 Sektor-ETFs + SPY auf dem NYSE-Kalender; optional: XL-Reihen erst ab `xl_start` (wie in echt)."""
    idx = pd.date_range(start, end, freq=NYSE_BDAY)
    rng = np.random.default_rng(seed)
    names = UNIVERSE + [FILTER]
    close = pd.DataFrame({t: 100.0 * np.exp(np.cumsum(rng.normal(rng.normal(0.0003, 0.0005), vol, len(idx))))
                          for t in names}, index=idx)
    # SPY: Auf- und Abschwung, damit der sma10-Filter beide Zustände sieht
    n = len(idx)
    mu = np.where(np.arange(n) < 500, 0.0010, np.where(np.arange(n) < 900, -0.0020, 0.0015))
    close[FILTER] = 100.0 * np.exp(np.cumsum(mu + rng.normal(0, 0.004, n)))
    open_ = close.shift(1).fillna(close.iloc[0]) * (1.0 + rng.normal(0.0, 0.002, close.shape))
    if xl_start is not None:
        close.loc[close.index < xl_start, UNIVERSE] = np.nan
        open_.loc[open_.index < xl_start, UNIVERSE] = np.nan
    return Panel(open_, close)


@pytest.fixture(scope="module")
def panel():
    return make_panel(seed=7)


def test_spec_is_fixed_nine_sector_universe():
    assert UNIVERSE == ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]
    assert "XLRE" not in SPEC["tickers"] and "XLC" not in SPEC["tickers"]
    assert SPEC["tickers"] == UNIVERSE + ["SPY"]
    assert SPEC["id"] == "sector_etf_top3_12m_etf"
    assert SPEC["family"] == "xsmom"
    assert SPEC["start"] == "1998-12-22"
    assert len(SPEC["variants"]) <= 3 and set(SPEC["variants"]) == {"combo", "sma10", "hold_buffer"}
    for v in SPEC["variants"].values():
        assert set(v) <= set(SPEC["params"])
    assert SPEC["params"]["lookback_months"] == 12 and SPEC["params"]["top_n"] == 3


@pytest.mark.parametrize("variant", VARIANTS)
def test_shape_value_range_and_spy_never_held(panel, variant):
    w = weights(panel, **params_for(variant))
    assert list(w.columns) == UNIVERSE                    # SPY ist nur Signalquelle
    assert len(w) > 20 and not w.isna().any().any()
    assert ((w == 0.0) | np.isclose(w, 1.0 / 3.0)).all().all()
    s = w.sum(axis=1)
    assert (s <= 1.0 + 1e-12).all()                       # kein Hebel
    n_pos = (w > 0).sum(axis=1)
    assert set(n_pos.unique()) <= ({0, 3} if variant == "sma10" else {3})


@pytest.mark.parametrize("variant", VARIANTS)
def test_same_rule_as_shared_core(panel, variant):
    p = params_for(variant)
    ref = rotation_weights(panel.close, UNIVERSE, filter_close=panel.close[FILTER], **p)
    pd.testing.assert_frame_equal(weights(panel, **p), ref, check_freq=False)


def test_first_signal_is_twelve_months_after_first_month_end(panel):
    w = weights(panel)
    idx = panel.close.index
    me = pd.DatetimeIndex(pd.Series(idx, index=idx).groupby([idx.year, idx.month]).max().to_numpy())
    assert w.index[0] == me[12]


def test_unlisted_etfs_get_no_weight_and_all_variants_start_together():
    """SPY existiert früher als die XL-Reihen (wie in echt): kein Signal und kein Cash-Signal vor dem
    ersten bewertbaren Monatsende, in keiner Variante."""
    p = make_panel(seed=9, start="2002-01-01", end="2008-12-31", xl_start=pd.Timestamp("2003-06-02"))
    base = weights(p)
    first = base.index[0]
    assert first >= pd.Timestamp("2004-06-01")            # frühestens 12 Monate nach erstem XL-Kurs
    assert not w_has_signal_before(base, first)
    for variant in VARIANTS:
        w = weights(p, **params_for(variant))
        assert w.index[0] == first, variant               # auch sma10 beginnt nicht schon im SPY-Vorlauf
        assert not w.isna().any().any()


def w_has_signal_before(w, d):
    return bool((w.index < d).any())


@pytest.mark.parametrize("variant", VARIANTS)
def test_check_causality_on_synthetic_panel(panel, variant):
    p = params_for(variant)
    assert check_causality(lambda pp: weights(pp, **p), panel) == []


def test_causality_with_staggered_listing():
    p = make_panel(seed=13, start="2002-01-01", end="2008-12-31", xl_start=pd.Timestamp("2003-06-02"))
    assert check_causality(lambda pp: weights(pp), p) == []
    assert check_causality(lambda pp: weights(pp, **params_for("sma10")), p) == []


def test_runs_through_engine_and_never_buys_spy(panel):
    w = weights(panel)
    res = run_backtest(panel, w, cost=CostModel(default_bps=5.0), rf=pd.Series(0.0, index=panel.close.index))
    assert np.isfinite(res.nav).all() and (res.nav > 0).all()
    assert res.skipped_orders == 0
    assert res.gross_exposure.max() <= 1.02
    assert (res.weights[FILTER].abs() < 1e-12).all()
    assert res.n_trades > 0


def test_sma10_needs_spy_in_panel(panel):
    nospy = Panel(panel.open.drop(columns=[FILTER]), panel.close.drop(columns=[FILTER]))
    assert len(weights(nospy)) > 0
    with pytest.raises(KeyError):
        weights(nospy, **params_for("sma10"))
    assert etf.FILTER == "SPY"
