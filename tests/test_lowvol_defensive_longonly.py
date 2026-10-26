"""Tests fuer lowvol_defensive_longonly (Faktor-Ebene, French-Beta-Quintil) auf synthetischen Daten.

Kein Netz, kein Datencache: Monatsrenditen und Handelstag-Raster sind erfunden bzw. per monkeypatch ersetzt.
"""
import inspect

import numpy as np
import pandas as pd
import pytest
from scipy import stats as sps

from qlab.calendar import NYSE_BDAY
from qlab.data import Panel, panel_from_returns
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import lowvol_defensive_longonly as m

BETA, VAR = m.BETA_COL, m.VAR_COL
ZERO = CostModel(default_bps=0.0, short_fee_annual=0.0, lever_spread_annual=0.0)
VARIANTS = {"base": {}, **m.SPEC["variants"]}


# --------------------------------------------------------------------------------------
# Hilfen
# --------------------------------------------------------------------------------------

def make_grid(start="2000-01-03", end="2010-12-31"):
    return pd.date_range(start, end, freq=NYSE_BDAY)


def make_monthly(start="2000-01-01", end="2010-12-01", seed=3):
    """Monatsrenditen wie bei French: Datum = 1. des Monats, zwei Spalten (BETA/VAR Lo 20)."""
    idx = pd.date_range(start, end, freq="MS")
    rng = np.random.default_rng(seed)
    return pd.DataFrame({BETA: rng.normal(0.007, 0.04, len(idx)), VAR: rng.normal(0.006, 0.035, len(idx))}, index=idx)


def make_panel(monthly=None, grid=None):
    monthly = make_monthly() if monthly is None else monthly
    grid = make_grid() if grid is None else grid
    return panel_from_returns(m.monthly_to_month_end_grid(monthly, grid))


def last_trading_days(grid):
    s = pd.Series(grid, index=grid)
    return pd.DatetimeIndex(s.groupby([grid.year, grid.month]).max().to_numpy())


# --------------------------------------------------------------------------------------
# Monatsrenditen -> Tagesraster
# --------------------------------------------------------------------------------------

def test_grid_puts_monthly_return_on_last_trading_day_and_zero_elsewhere():
    monthly, grid = make_monthly(), make_grid()
    out = m.monthly_to_month_end_grid(monthly, grid)
    ends = last_trading_days(grid)
    assert len(ends) == len(monthly)
    assert np.allclose(out.loc[ends, BETA].to_numpy(), monthly[BETA].to_numpy(), atol=1e-15)
    assert np.allclose(out.loc[ends, VAR].to_numpy(), monthly[VAR].to_numpy(), atol=1e-15)
    others = out.drop(index=ends)
    assert (others == 0.0).all().all()
    assert out.index.equals(grid)                                    # Raster vollstaendig, nichts verschoben


def test_monthly_compounding_survives_the_embedding():
    monthly, grid = make_monthly(), make_grid()
    p = make_panel(monthly, grid)
    px = p.close[BETA]
    me = px[px.index.isin(last_trading_days(grid))]
    got = (me / me.shift(1) - 1.0).iloc[1:].to_numpy()
    assert np.allclose(got, monthly[BETA].iloc[1:].to_numpy(), atol=1e-12)
    assert px.iloc[-1] / px.iloc[0] == pytest.approx(np.prod(1.0 + monthly[BETA].to_numpy()), rel=1e-12)


def test_return_is_not_visible_before_month_end():
    """Innerhalb eines Monats bewegt sich der Kurs nicht (sonst saehe man die Monatsrendite vorab)."""
    monthly, grid = make_monthly(), make_grid()
    px = make_panel(monthly, grid).close[BETA]
    ends = set(last_trading_days(grid))
    moved = px.index[px.diff().abs() > 0]
    assert len(moved) > 100
    assert all(d in ends for d in moved)


def test_grid_span_follows_data_and_per_column_start():
    grid = make_grid("1999-01-04", "2012-12-31")
    monthly = make_monthly("2003-01-01", "2006-12-01")
    monthly.loc[monthly.index < "2004-01-01", VAR] = np.nan          # VAR beginnt ein Jahr spaeter
    out = m.monthly_to_month_end_grid(monthly, grid)
    assert out.index.min() == grid[grid >= "2003-01-01"][0]
    assert out.index.max() == last_trading_days(grid[grid <= "2006-12-31"])[-1]
    assert out[BETA].notna().all()
    first_var = grid[grid >= "2004-01-01"][0]
    assert out.loc[out.index < first_var, VAR].isna().all()
    assert (out.loc[first_var:, VAR].notna()).all()
    p = panel_from_returns(out)
    assert p.close[VAR].first_valid_index() == first_var            # nicht handelbar, bevor die Reihe existiert


def test_partial_last_month_of_grid_is_not_booked():
    monthly = make_monthly("2005-01-01", "2005-06-01")
    full = m.monthly_to_month_end_grid(monthly, make_grid("2005-01-03", "2005-06-30"))
    part = m.monthly_to_month_end_grid(monthly, make_grid("2005-01-03", "2005-06-15"))   # Juni nur halb im Raster
    assert full[BETA].iloc[-1] == pytest.approx(monthly[BETA].iloc[-1])
    assert part.index.max() == pd.Timestamp("2005-05-31")
    assert part[BETA].iloc[-1] == pytest.approx(monthly[BETA].iloc[-2])
    assert not (part.index > "2005-05-31").any()


def test_months_without_grid_days_are_dropped_and_empty_inputs():
    monthly = make_monthly("2005-01-01", "2005-12-01")
    out = m.monthly_to_month_end_grid(monthly, make_grid("2005-03-01", "2005-06-30"))
    assert out.index.min() == pd.Timestamp("2005-03-01")
    assert out[BETA].iloc[-1] == pytest.approx(monthly[BETA].loc["2005-06-01"])
    assert len(m.monthly_to_month_end_grid(monthly.iloc[0:0], make_grid())) == 0


# --------------------------------------------------------------------------------------
# Gewichte
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", list(VARIANTS))
def test_shape_and_value_range(name):
    p = make_panel()
    kw = VARIANTS[name]
    w = m.weights(p, **kw)
    col = kw.get("column", BETA)
    assert list(w.columns) == [col]
    assert len(w) == 1
    assert w.iloc[0, 0] == 1.0                                       # 100 %, kein Hebel, kein Cash
    assert (w.sum(axis=1) <= 1.0 + 1e-12).all() and (w.abs().sum(axis=1) <= 1.0 + 1e-12).all()
    assert w.index[0] == p.close.index[0]                            # erster Tag mit Kurs
    assert w.notna().all().all()


def test_no_weight_on_nan_prices_and_no_other_column():
    monthly = make_monthly()
    monthly.loc[monthly.index < "2003-01-01", VAR] = np.nan
    p = make_panel(monthly)
    first_var = p.close[VAR].first_valid_index()
    assert first_var > p.close.index[0]
    wv = m.weights(p, column=VAR)
    assert list(wv.index) == [first_var]                             # nicht vor dem ersten Kurs
    assert np.isfinite(p.close.loc[wv.index, VAR]).all()
    wb = m.weights(p)
    assert list(wb.columns) == [BETA] and wb.index[0] == p.close.index[0]


def test_empty_when_column_has_no_price():
    p = make_panel()
    close = p.close.copy()
    close[VAR] = np.nan
    w = m.weights(Panel(p.open.copy(), close), column=VAR)
    assert len(w) == 0 and list(w.columns) == [VAR]


def test_unknown_column_raises():
    with pytest.raises(KeyError):
        m.weights(make_panel(), column="nicht_da")


# --------------------------------------------------------------------------------------
# Kausalitaet
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", list(VARIANTS))
def test_causality(name):
    p = make_panel()
    kw = VARIANTS[name]
    assert check_causality(lambda pp: m.weights(pp, **kw), p) == []


def test_causality_with_late_starting_column():
    monthly = make_monthly()
    monthly.loc[monthly.index < "2003-01-01", VAR] = np.nan
    p = make_panel(monthly)
    assert check_causality(lambda pp: m.weights(pp, column=VAR), p) == []
    first_var = p.close[VAR].first_valid_index()
    cuts = [first_var - pd.Timedelta(days=40), first_var, first_var + pd.Timedelta(days=40)]
    assert check_causality(lambda pp: m.weights(pp, column=VAR), p, cuts=cuts) == []


def test_causality_check_catches_lookahead_in_this_setup():
    """Tripwire: ein Blick in die Zukunft muss vom selben Test erkannt werden."""
    p = make_panel()

    def peeking(pp):
        w = m.weights(pp)
        fut = pp.close[BETA].shift(-30).reindex(w.index)             # Kurs 30 Handelstage spaeter
        return w * (1.0 + fut.notna().astype(float).to_numpy()[:, None])

    cuts = [p.close.index[0] + pd.Timedelta(days=d) for d in (2, 50, 400)]
    assert check_causality(peeking, p, cuts=cuts) != []              # Gewicht am 1. Tag haengt von der Zukunft ab


def test_perturbing_future_data_does_not_change_weights():
    monthly = make_monthly()
    grid = make_grid()
    base = m.weights(make_panel(monthly, grid))
    m2 = monthly.copy()
    m2.loc[m2.index > "2004-01-01"] = m2.loc[m2.index > "2004-01-01"].to_numpy() * -3.0 + 0.2
    pert = m.weights(make_panel(m2, grid))
    pd.testing.assert_frame_equal(base, pert)


# --------------------------------------------------------------------------------------
# Engine-Integration
# --------------------------------------------------------------------------------------

def test_engine_buys_next_day_close_and_nav_equals_compounded_monthly_returns():
    monthly, grid = make_monthly(), make_grid()
    p = make_panel(monthly, grid)
    w = m.weights(p)
    res = run_backtest(p, w, cost=ZERO, rf=pd.Series(0.0, index=p.close.index))
    idx = p.close.index
    t0 = w.index[0]
    nxt = idx[idx.get_loc(t0) + 1]
    assert res.weights.loc[t0, BETA] == 0.0                          # am Signaltag selbst noch nichts
    assert res.weights.loc[nxt, BETA] == pytest.approx(1.0, abs=1e-12)
    assert res.weights[VAR].abs().max() == 0.0                       # andere Spalte nie gehalten
    assert res.skipped_orders == 0 and res.n_trades == 1
    # alle Monatsrenditen liegen nach dem Kauf (Kauf am 2. Tag, erstes Monatsende spaeter) -> NAV = Produkt
    assert res.nav.iloc[-1] == pytest.approx(np.prod(1.0 + monthly[BETA].to_numpy()), rel=1e-10)
    assert (res.gross_exposure <= 1.0 + 1e-12).all()


def test_engine_runs_all_variants_with_default_costs_and_tax():
    from qlab.engine import TaxModel

    p = make_panel()
    rf = pd.Series(0.0, index=p.close.index)
    for kw in VARIANTS.values():
        res = run_backtest(p, m.weights(p, **kw), cost=CostModel(), rf=rf, tax=TaxModel())
        assert np.isfinite(res.nav).all() and (res.nav > 0).all()
        assert res.skipped_orders == 0
        assert res.gross_exposure.max() <= 1.01                       # Kosten ziehen das Cash minimal ins Minus


# --------------------------------------------------------------------------------------
# SPEC und load()
# --------------------------------------------------------------------------------------

def test_spec_contract():
    s = m.SPEC
    assert s["id"] == "lowvol_defensive_longonly" and s["family"] == "lowrisk"
    assert 1 <= len(s["variants"]) <= 3 and set(s["variants"]) == {"var"}
    params = set(inspect.signature(m.weights).parameters) - {"panel"}
    assert set(s["params"]) == params
    for vp in s["variants"].values():
        assert set(vp) <= params
    assert s["params"] == {"column": BETA} and s["variants"]["var"] == {"column": VAR}
    assert s["tickers"] == [BETA, VAR]
    assert s["start"] == "1963-07-01" and s["sources"]
    assert callable(m.load)
    assert m.SPLIT_DATE == "2008-01-01" and m.IS_END == "2022-12-31"


def _fake_french_factory(monthly_beta, monthly_var, grid, calls):
    def fake_french(name, daily=None, table=0, **kw):
        calls.append((name, daily, table))
        if name == "F-F_Research_Data_Factors" and daily:
            return pd.DataFrame({"Mkt-RF": 0.0, "SMB": 0.0, "HML": 0.0, "RF": 0.0}, index=grid)
        if name == "Portfolios_Formed_on_BETA":
            return monthly_beta
        if name == "Portfolios_Formed_on_VAR":
            return monthly_var
        raise AssertionError(name)
    return fake_french


def test_load_builds_panel_from_value_weighted_quintile_columns(monkeypatch):
    mon, grid = make_monthly(), make_grid()
    rng = np.random.default_rng(5)
    other = pd.DataFrame(rng.normal(0, 0.05, (len(mon), 2)), index=mon.index, columns=["Qnt 2", "Hi 20"])
    beta_df = pd.concat([mon[[BETA]].rename(columns={BETA: "Lo 20"}), other], axis=1)
    var_df = pd.concat([mon[[VAR]].rename(columns={VAR: "Lo 20"}), other], axis=1)
    calls = []
    monkeypatch.setattr(m, "french", _fake_french_factory(beta_df, var_df, grid, calls))
    p = m.load()
    assert ("Portfolios_Formed_on_BETA", None, 0) in calls and ("Portfolios_Formed_on_VAR", None, 0) in calls
    assert ("F-F_Research_Data_Factors", True, 0) in calls            # Tagesraster
    assert p.tickers == [BETA, VAR]
    assert p.open.equals(p.close)                                    # panel_from_returns: open == close
    px = p.close[BETA]
    me = px[px.index.isin(last_trading_days(grid))]
    assert np.allclose((me / me.shift(1) - 1.0).iloc[1:].to_numpy(), mon[BETA].iloc[1:].to_numpy(), atol=1e-12)
    assert set(p.close.columns) == {BETA, VAR}                       # keine fremden Quintile im Panel


# --------------------------------------------------------------------------------------
# Auswertungshelfer (Alpha gegen Mkt-RF, Stichprobenteilung)
# --------------------------------------------------------------------------------------

def make_factor_data(n=400, seed=1, alpha=0.002, beta=0.7, start="1975-01-01"):
    idx = pd.date_range(start, periods=n, freq="MS")
    rng = np.random.default_rng(seed)
    mkt = pd.Series(rng.normal(0.006, 0.045, n), index=idx)
    rf = pd.Series(0.003, index=idx)
    y_excess = alpha + beta * mkt + rng.normal(0, 0.012, n)
    return (y_excess + rf), mkt, rf


def test_capm_alpha_matches_scipy_linregress():
    total, mkt, rf = make_factor_data()
    res = m.capm_alpha(total - rf, mkt)
    ref = sps.linregress(mkt.to_numpy(), (total - rf).to_numpy())
    assert res["n"] == len(mkt)
    assert res["alpha_m"] == pytest.approx(ref.intercept, rel=1e-9)
    assert res["beta"] == pytest.approx(ref.slope, rel=1e-9)
    assert res["t_alpha"] == pytest.approx(ref.intercept / ref.intercept_stderr, rel=1e-8)
    assert res["alpha_ann"] == pytest.approx(12.0 * ref.intercept, rel=1e-9)


def test_capm_alpha_recovers_known_parameters():
    total, mkt, rf = make_factor_data(n=3000, seed=2, alpha=0.002, beta=0.7)
    res = m.capm_alpha(total - rf, mkt)
    assert res["beta"] == pytest.approx(0.7, abs=0.03)
    assert res["alpha_m"] == pytest.approx(0.002, abs=0.001)
    assert res["t_alpha"] > 2.0


def test_capm_alpha_needs_enough_observations():
    total, mkt, rf = make_factor_data(n=8)
    res = m.capm_alpha(total - rf, mkt)
    assert res["n"] == 8 and np.isnan(res["alpha_m"]) and np.isnan(res["t_alpha"])


def test_capm_alpha_split_partitions_the_sample():
    total, mkt, rf = make_factor_data(n=480, start="1975-01-01")   # 1975-01 .. 2014-12
    out = m.capm_alpha_split(total, mkt, rf)                          # Standard: Teilung bei 2008-01
    n_pre = int((total.index < "2008-01-01").sum())
    assert out["pre"]["n"] == n_pre
    assert out["post"]["n"] == len(total) - n_pre
    assert out["full"]["n"] == len(total)
    ex = total - rf
    ref_post = m.capm_alpha(ex[ex.index >= "2008-01-01"], mkt)
    assert out["post"] == ref_post
    out2 = m.capm_alpha_split(total, mkt, rf, split="2000-01-01")
    assert out2["pre"]["n"] == int((total.index < "2000-01-01").sum())


def test_alpha_split_from_french_never_reads_the_holdout(monkeypatch):
    idx = pd.date_range("1990-01-01", "2025-12-01", freq="MS")
    rng = np.random.default_rng(9)
    port = pd.DataFrame({"Lo 20": rng.normal(0.008, 0.04, len(idx)), "Hi 20": 0.0}, index=idx)
    fac = pd.DataFrame({"Mkt-RF": rng.normal(0.006, 0.045, len(idx)), "RF": 0.002}, index=idx)
    seen = []

    def fake_french(name, daily=None, table=0, **kw):
        seen.append(name)
        return port if name.startswith("Portfolios_Formed") else fac

    monkeypatch.setattr(m, "french", fake_french)
    out = m.alpha_split_from_french()
    assert out["full"]["n"] == int((idx <= "2022-12-31").sum())      # nichts ab 2023
    assert out["pre"]["n"] + out["post"]["n"] == out["full"]["n"]
    assert seen == ["Portfolios_Formed_on_BETA", "F-F_Research_Data_Factors"]
    out_var = m.alpha_split_from_french("Portfolios_Formed_on_VAR")
    assert seen[-2] == "Portfolios_Formed_on_VAR" and out_var["full"]["n"] == out["full"]["n"]
