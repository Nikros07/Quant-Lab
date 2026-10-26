"""Tests für strategies/keller_paa_g12.py auf synthetischen Panels (kein Netz, kein Datencache).

Bekannte Antworten: Preise mit konstanter Tageswachstumsrate g. Dann ist m_i = 1/mean(exp(-g*D_j)) - 1
streng steigend in g, m_i < 0 genau für g < 0, und das Ranking nach m entspricht dem Ranking nach g.
"""
import numpy as np
import pandas as pd
import pytest

from qlab.calendar import NYSE_BDAY, month_end_flags
from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import keller_paa_g12 as K

ALL, OFF, DEF = K.ALL, K.OFFENSIVE, K.DEFENSIVE
BASE = K.SPEC["params"]


# --------------------------------------------------------------------------------------
# Hilfen
# --------------------------------------------------------------------------------------

def nyse_index(n, start="2010-01-04"):
    return pd.date_range(start, periods=n, freq=NYSE_BDAY)


def random_panel(n=1400, seed=7, start="2008-01-02"):
    rng = np.random.default_rng(seed)
    idx = nyse_index(n, start)
    ret = rng.normal(0.0003, 0.01, (n, len(ALL)))
    close = pd.DataFrame(100.0 * np.exp(np.cumsum(ret, axis=0)), index=idx, columns=ALL)
    gap = rng.normal(0.0, 0.003, (n, len(ALL)))
    open_ = close.shift(1).fillna(close.iloc[0]) * np.exp(gap)
    return Panel(open_, close)


def trend_panel(growth: dict, n=800):
    """Konstante Tageswachstumsrate je Ticker (Rest 0)."""
    idx = nyse_index(n)
    k = np.arange(n)[:, None]
    g = np.array([growth.get(t, 0.0) for t in ALL])[None, :]
    close = pd.DataFrame(100.0 * np.exp(g * k), index=idx, columns=ALL)
    return Panel(close.copy(), close)


def growth_scenario(off, bil, ief):
    g = {t: v for t, v in zip(OFF, off)}
    g["BIL"], g["IEF"] = bil, ief
    return g


def last_row(w):
    return w.iloc[-1]


def first_signal_date(idx):
    """13. Monatsende (12 Vor-Monatsenden + das aktuelle), Referenz aus dem Kalender-Helfer."""
    me = idx[month_end_flags(idx).to_numpy()]
    return me[12]


# --------------------------------------------------------------------------------------
# SPEC
# --------------------------------------------------------------------------------------

def test_spec_contract():
    s = K.SPEC
    assert s["id"] == "keller_paa_g12"
    assert len(s["tickers"]) == 14 and len(set(s["tickers"])) == 14
    assert set(OFF) | set(DEF) == set(s["tickers"])
    assert len(OFF) == 12 and DEF == ["BIL", "IEF"]
    assert 1 <= len(s["variants"]) <= 3
    for v in s["variants"].values():
        assert set(v) <= set(s["params"])
    assert s["family"] == "tactical" and s["sources"]
    assert all(s["cost_bps"][t] == 10.0 for t in s["tickers"])


# --------------------------------------------------------------------------------------
# Bekannte Antworten
# --------------------------------------------------------------------------------------

def test_no_breadth_alarm_fully_offensive_top6():
    off = [0.0002 * (i + 1) for i in range(12)]                    # alle m > 0, m steigt mit dem Index
    p = trend_panel(growth_scenario(off, bil=0.0001, ief=0.00005))
    w = K.weights(p)
    assert len(w) > 5
    assert w.index[0] == first_signal_date(p.close.index)
    exp = pd.Series(0.0, index=ALL)
    exp[OFF[6:]] = 1.0 / 6.0
    for _, row in w.iterrows():
        assert row.to_numpy() == pytest.approx(exp.to_numpy(), abs=1e-12)


def test_three_bad_assets_half_defensive_into_better_defensive():
    off = [-0.0003, -0.0002, -0.0001] + [0.0001 * (i + 1) for i in range(9)]       # b = 3
    p = trend_panel(growth_scenario(off, bil=0.0001, ief=0.0003))                  # IEF hat höheres m
    w = last_row(K.weights(p))
    assert w["IEF"] == pytest.approx(0.5)
    assert w["BIL"] == 0.0
    for t in OFF[6:]:                                                              # höchste g -> höchstes m
        assert w[t] == pytest.approx(0.5 / 6.0)
    for t in OFF[:6]:
        assert w[t] == 0.0
    assert w.sum() == pytest.approx(1.0)


def test_defensive_choice_follows_higher_momentum_bil_wins():
    off = [-0.0002] * 12                                                           # b = 12 -> CF = 1
    p = trend_panel(growth_scenario(off, bil=0.00005, ief=-0.0001))
    w = last_row(K.weights(p))
    assert w["BIL"] == pytest.approx(1.0)
    assert w.drop("BIL").abs().sum() == 0.0


def test_full_protection_at_b_equal_threshold_and_partial_below():
    off6 = [-0.0002] * 6 + [0.0002 * (i + 1) for i in range(6)]                    # b = 6 -> CF = 1
    w = last_row(K.weights(trend_panel(growth_scenario(off6, bil=0.0, ief=0.0002))))
    assert w["IEF"] == pytest.approx(1.0)
    assert w[OFF].abs().sum() == 0.0
    off5 = [-0.0002] * 5 + [0.0002 * (i + 1) for i in range(7)]                    # b = 5 -> CF = 5/6
    w5 = last_row(K.weights(trend_panel(growth_scenario(off5, bil=0.0, ief=0.0002))))
    assert w5["IEF"] == pytest.approx(5.0 / 6.0)
    assert w5[OFF].sum() == pytest.approx(1.0 / 6.0)
    assert (w5[OFF] > 0).sum() == 6


def test_defensive_tie_goes_to_bil():
    off = [-0.0002] * 12
    w = last_row(K.weights(trend_panel(growth_scenario(off, bil=0.0001, ief=0.0001))))
    assert w["BIL"] == pytest.approx(1.0)


def test_variants_top4_and_breadth4():
    off = [-0.0003, -0.0002, -0.0001] + [0.0001 * (i + 1) for i in range(9)]       # b = 3
    p = trend_panel(growth_scenario(off, bil=0.0001, ief=0.0003))
    w_top4 = last_row(K.weights(p, **{**BASE, **K.SPEC["variants"]["top4"]}))
    assert (w_top4[OFF] > 0).sum() == 4
    for t in OFF[8:]:
        assert w_top4[t] == pytest.approx(0.5 / 4.0)
    assert w_top4["IEF"] == pytest.approx(0.5)
    w_b4 = last_row(K.weights(p, **{**BASE, **K.SPEC["variants"]["breadth4"]}))
    assert w_b4["IEF"] == pytest.approx(0.75)                                      # CF = min(1, 3/4)
    for t in OFF[6:]:
        assert w_b4[t] == pytest.approx(0.25 / 6.0)


# --------------------------------------------------------------------------------------
# Form, Wertebereich, Kalender
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", ["base", "top4", "breadth4", "sleeves3"])
def test_shape_range_and_exposure(variant):
    p = random_panel()
    params = dict(BASE) if variant == "base" else {**BASE, **K.SPEC["variants"][variant]}
    w = K.weights(p, **params)
    assert len(w) > 20
    assert list(w.columns) == ALL
    assert w.index.is_monotonic_increasing and w.index.is_unique
    assert set(w.index) <= set(p.close.index)
    assert not w.isna().any().any()
    assert (w >= 0).all().all() and (w <= 1.0 + 1e-12).all().all()
    s = w.sum(axis=1)
    assert (s <= 1.0 + 1e-9).all() and (s >= 1.0 - 1e-9).all()                    # voll investiert, kein Hebel
    n_off = (w[OFF] > 1e-12).sum(axis=1)
    assert (n_off <= params["top_n"] * (3 if variant == "sleeves3" else 1)).all()


def test_base_rows_are_exactly_causal_month_ends():
    p = random_panel()
    idx = p.close.index
    w = K.weights(p)
    me = idx[month_end_flags(idx).to_numpy()]
    assert list(w.index) == list(me[12:])                                          # ab dem 13. Monatsende


def test_sleeves3_dates_are_0_7_14_trading_days_before_month_end():
    p = random_panel()
    idx = p.close.index
    w = K.weights(p, **{**BASE, **K.SPEC["variants"]["sleeves3"]})
    ext = nyse_index(len(idx) + 60, start=str(idx[0].date()))                      # Referenz über das Datenende hinaus
    pos = pd.Series(np.arange(len(ext)), index=ext)
    last_pos = pos.groupby([ext.year, ext.month]).transform("max")                 # nur Testreferenz
    dist = (last_pos - pos).loc[w.index]
    assert set(dist.unique()) == {0, 7, 14}
    assert w.index[0] >= first_signal_date(idx) - 14 * NYSE_BDAY


def test_sleeves3_equals_mean_of_single_sleeves():
    p = random_panel()
    singles = {o: K.weights(p, **{**BASE, "sleeve_offsets": (o,)}) for o in (14, 7, 0)}
    comb = K.weights(p, **{**BASE, "sleeve_offsets": (14, 7, 0)})
    assert comb.index[0] == max(s.index[0] for s in singles.values())
    for t, row in comb.iterrows():
        parts = [s.loc[:t].iloc[-1] for s in singles.values()]
        exp = sum(parts) / 3.0
        assert row.to_numpy() == pytest.approx(exp.to_numpy(), abs=1e-12)
    # an jedem Stichtag eines Sleeves liegt dessen Signal auch im kombinierten Ziel
    assert set().union(*[set(s.index) for s in singles.values()]) >= set(comb.index)


def test_short_history_gives_empty_frame():
    p = random_panel(n=200)                                                        # < 13 Monatsenden
    w = K.weights(p)
    assert len(w) == 0 and list(w.columns) == ALL
    w3 = K.weights(p, **{**BASE, "sleeve_offsets": (14, 7, 0)})
    assert len(w3) == 0


def test_parameter_validation():
    p = random_panel(n=300)
    with pytest.raises(ValueError):
        K.weights(p, top_n=0)
    with pytest.raises(ValueError):
        K.weights(p, top_n=13)
    with pytest.raises(ValueError):
        K.weights(p, breadth=0)
    with pytest.raises(ValueError):
        K.weights(p, sleeve_offsets=())
    with pytest.raises(ValueError):
        K.weights(p, sleeve_offsets=(-1,))


# --------------------------------------------------------------------------------------
# Fehlende Preise = nicht handelbar
# --------------------------------------------------------------------------------------

def assert_no_weight_on_nan(w, panel):
    px = panel.close.reindex(index=w.index, columns=w.columns)
    assert not ((w > 0) & px.isna()).any().any()


def test_late_listed_asset_blocks_signals_until_full_history():
    p = random_panel()
    close = p.close.copy()
    open_ = p.open.copy()
    close.loc[close.index[:400], "HYG"] = np.nan
    open_.loc[open_.index[:400], "HYG"] = np.nan
    q = Panel(open_, close)
    w = K.weights(q)
    idx = q.close.index
    me = idx[month_end_flags(idx).to_numpy()]
    valid_from = q.close["HYG"].first_valid_index()
    me_valid = me[me >= valid_from]
    assert w.index.min() == me_valid[12]
    assert w.index.min() > p.close.index[400]
    assert_no_weight_on_nan(w, q)


def test_missing_price_on_signal_day_skips_that_signal_but_bridges_history():
    p = random_panel()
    idx = p.close.index
    me = idx[month_end_flags(idx).to_numpy()]
    t_star = me[30]
    close = p.close.copy()
    open_ = p.open.copy()
    close.loc[t_star, "QQQ"] = np.nan
    open_.loc[t_star, "QQQ"] = np.nan
    q = Panel(open_, close)
    w = K.weights(q)
    assert t_star not in w.index                                                   # QQQ nicht handelbar -> kein Signal
    for d in me[31:43]:                                                            # Lücke von 1 Tag blockiert die Historie nicht
        assert d in w.index
    assert_no_weight_on_nan(w, q)


def test_delisted_asset_stops_signals_and_never_gets_weight():
    p = random_panel()
    close = p.close.copy()
    open_ = p.open.copy()
    cut = 900
    close.loc[close.index[cut:], "QQQ"] = np.nan
    open_.loc[open_.index[cut:], "QQQ"] = np.nan
    q = Panel(open_, close)
    w = K.weights(q)
    assert w.index.max() < q.close.index[cut]
    assert_no_weight_on_nan(w, q)


def test_long_gap_in_history_gives_no_weight_on_nan_and_no_crash():
    p = random_panel()
    close = p.close.copy()
    open_ = p.open.copy()
    rows = close.index[600:625]                                                    # 25 Tage Lücke, länger als FFILL_LIMIT
    close.loc[rows, "EWJ"] = np.nan
    open_.loc[rows, "EWJ"] = np.nan
    q = Panel(open_, close)
    for params in (BASE, {**BASE, "sleeve_offsets": (14, 7, 0)}):
        w = K.weights(q, **params)
        assert len(w) > 0
        assert not w.isna().any().any()
        assert_no_weight_on_nan(w, q)


# --------------------------------------------------------------------------------------
# Kausalität
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", ["base", "top4", "breadth4", "sleeves3"])
def test_check_causality_passes(variant):
    p = random_panel()
    params = dict(BASE) if variant == "base" else {**BASE, **K.SPEC["variants"][variant]}
    assert check_causality(lambda pp, _pa=params: K.weights(pp, **_pa), p, n_cuts=9) == []


def test_check_causality_with_nan_history():
    p = random_panel()
    close, open_ = p.close.copy(), p.open.copy()
    close.loc[close.index[:300], "HYG"] = np.nan
    open_.loc[open_.index[:300], "HYG"] = np.nan
    q = Panel(open_, close)
    assert check_causality(lambda pp: K.weights(pp, **BASE), q, n_cuts=7) == []


@pytest.mark.parametrize("offsets", [(0,), (14, 7, 0)])
def test_future_prices_do_not_change_past_weights(offsets):
    p = random_panel()
    idx = p.close.index
    cut = idx[1000]
    close = p.close.copy()
    open_ = p.open.copy()
    close.loc[close.index > cut] *= 7.0
    open_.loc[open_.index > cut] *= 7.0
    q = Panel(open_, close)
    a = K.weights(p, **{**BASE, "sleeve_offsets": offsets}).loc[:cut]
    b = K.weights(q, **{**BASE, "sleeve_offsets": offsets}).loc[:cut]
    assert list(a.index) == list(b.index) and len(a) > 0
    assert (a - b).abs().to_numpy().max() < 1e-12


# --------------------------------------------------------------------------------------
# Zusammenspiel mit der Engine
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("offsets", [(0,), (14, 7, 0)])
def test_engine_runs_fully_invested_without_skipped_orders(offsets):
    p = random_panel()
    w = K.weights(p, **{**BASE, "sleeve_offsets": offsets})
    zero = CostModel(default_bps=0.0, short_fee_annual=0.0, lever_spread_annual=0.0)
    res = run_backtest(p, w, cost=zero, rf=pd.Series(0.0, index=p.close.index))
    assert res.skipped_orders == 0
    assert np.isfinite(res.nav).all() and (res.nav > 0).all()
    assert res.gross_exposure.max() <= 1.0 + 1e-6                                  # nie gehebelt
    first_trade_day = p.close.index[p.close.index.get_loc(w.index[0]) + 1]         # Signal t, Handel zur Eröffnung t+1
    assert res.gross_exposure.loc[first_trade_day:].min() > 0.99                   # nach dem Start voll investiert
    assert res.gross_exposure.loc[:w.index[0]].max() == 0.0                        # vorher kein Kapital im Markt
    costed = run_backtest(p, w, cost=CostModel(per_ticker_bps=K.SPEC["cost_bps"]),
                          rf=pd.Series(0.0, index=p.close.index))
    assert costed.cost.sum() > 0 and costed.n_trades > 0
