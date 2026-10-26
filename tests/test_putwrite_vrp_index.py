"""Tests für strategies/putwrite_vrp_index.py — nur synthetische Daten, kein Netz, kein Datencache."""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import month_end_flags
from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import putwrite_vrp_index as strat

BASE = dict(strat.SPEC["params"])
VARIANTS = {"base": {}, **strat.SPEC["variants"]}
N = 3300                                  # ~13 Jahre Handelstage ab 1996-08-02 (reicht bis 2009)
START = "1996-08-02"


def _idx(n: int = N, start: str = START) -> pd.DatetimeIndex:
    return pd.bdate_range(start, periods=n)


def _returns(seed: int = 3, n: int = N, beta: float = 0.6):
    """SPY-Tagesrenditen und ^PUT-Tagesrenditen (beta * SPY + eigenes Rauschen + Prämie)."""
    rng = np.random.default_rng(seed)
    spy = 0.0004 + 0.010 * rng.standard_normal(n)
    put = 0.0002 + beta * spy + 0.003 * rng.standard_normal(n)
    return spy, put


def _levels(r: np.ndarray, idx: pd.DatetimeIndex, base: float = 100.0) -> pd.Series:
    return pd.Series(base * np.cumprod(1.0 + r), index=idx)


def _rf(idx: pd.DatetimeIndex) -> pd.Series:
    """RF-Tagesrendite auf einem längeren Kalender als dem des Panels (wie French ab 1926)."""
    full = pd.bdate_range(idx[0] - pd.Timedelta(days=400), idx[-1] + pd.Timedelta(days=30))
    return pd.Series(0.00015, index=full)


def _inputs(seed: int = 3, n: int = N, beta: float = 0.6):
    idx = _idx(n)
    spy_r, put_r = _returns(seed, n, beta)
    return _levels(put_r, idx), _levels(spy_r, idx, 40.0), _rf(idx)


def _panel(**kw) -> Panel:
    put, spy, rf = _inputs(**kw)
    return strat.build_panel(put, spy, rf)


# --------------------------------------------------------------------------------------
# Vertrag / Form
# --------------------------------------------------------------------------------------

def test_spec_contract():
    spec = strat.SPEC
    assert spec["id"] == "putwrite_vrp_index"
    assert spec["family"] == "volpremium"
    assert len(spec["variants"]) <= 3
    sig = inspect.signature(strat.weights)
    for name in list(spec["params"]) + [k for v in spec["variants"].values() for k in v]:
        assert name in sig.parameters, name
    assert spec["params"] == {"cost_pp": 0.50, "first_signal": None}
    assert spec["variants"] == {"cost_025": {"cost_pp": 0.25}, "cost_100": {"cost_pp": 1.00},
                                "from_2008": {"first_signal": "2008-01-01"}}
    assert strat.COST_GRID_PP == (0.25, 0.50, 1.00)
    assert hasattr(strat, "load")
    assert spec["sources"] and spec["start"] == "1996-08-02"


def test_cost_column_names():
    assert strat.cost_column(0.25) == "PUT_C025"
    assert strat.cost_column(0.50) == "PUT_C050"
    assert strat.cost_column(1.00) == "PUT_C100"


def test_registry_discovers_module():
    from strategies._registry import discover

    mods = discover()
    assert "putwrite_vrp_index" in mods and mods["putwrite_vrp_index"] is strat


# --------------------------------------------------------------------------------------
# Panel (Kostenabzug, Kalender, Hilfsreihen)
# --------------------------------------------------------------------------------------

def test_panel_columns_calendar_and_open_equals_close():
    put, spy, rf = _inputs()
    panel = strat.build_panel(put, spy, rf)
    assert list(panel.close.columns) == ["PUT_C025", "PUT_C050", "PUT_C100", "SPY", "RF"]
    assert panel.close.index.equals(put.index)                    # Kalender = ^PUT-Kalender
    assert panel.open.equals(panel.close) and panel.open is not panel.close
    assert panel.close.notna().all().all()
    assert np.allclose(panel.close["SPY"].to_numpy(), spy.to_numpy())
    rf_ret = panel.close["RF"].pct_change().dropna()
    assert np.allclose(rf_ret.to_numpy(), 0.00015)                # Cash-Index wächst mit dem RF


@pytest.mark.parametrize("c", strat.COST_GRID_PP)
def test_cost_drag_is_c_over_252_per_day(c):
    put, spy, rf = _inputs()
    panel = strat.build_panel(put, spy, rf)
    net = panel.close[strat.cost_column(c)].pct_change().iloc[1:]
    gross = put.pct_change().iloc[1:]
    assert np.allclose(net.to_numpy(), gross.to_numpy() - c / 100.0 / 252.0, rtol=0, atol=1e-12)


def test_cost_drag_over_one_year_is_about_c():
    idx = _idx(253)
    flat = pd.Series(100.0, index=idx)                            # ^PUT bewegt sich nicht
    panel = strat.build_panel(flat, flat.copy(), _rf(idx))
    for c in strat.COST_GRID_PP:
        lvl = panel.close[strat.cost_column(c)]
        growth = lvl.iloc[-1] / lvl.iloc[0]                       # 252 Renditen
        assert growth == pytest.approx((1.0 - c / 100.0 / 252.0) ** 252, rel=1e-12)
        assert growth == pytest.approx(1.0 - c / 100.0, abs=1e-4)   # ~ c Prozentpunkte p.a. (Zinseszins 2. Ordnung)


def test_panel_nan_gap_keeps_return_across_gap_and_cost_once():
    put, spy, rf = _inputs(n=400)
    put_gap = put.copy()
    put_gap.iloc[100:105] = np.nan                                # 5 fehlende ^PUT-Tage
    panel = strat.build_panel(put_gap, spy, rf)
    col = panel.close["PUT_C050"]
    assert col.iloc[100:105].isna().all() and col.iloc[:100].notna().all() and col.iloc[105:].notna().all()
    two_gap = col.iloc[105] / col.iloc[99] - 1.0                  # Rendite über die Lücke
    assert two_gap == pytest.approx((put.iloc[105] / put.iloc[99] - 1.0) - 0.005 / 252, abs=1e-12)
    # ohne Lücke bleibt alles vor der Lücke identisch
    full = strat.build_panel(put, spy, rf)
    assert np.allclose(full.close["PUT_C050"].iloc[:100].to_numpy(), col.iloc[:100].to_numpy())


def test_panel_spy_with_gaps_and_extra_days_is_aligned_to_put_calendar():
    put, spy, rf = _inputs(n=300)
    spy2 = spy.drop(spy.index[[10, 11]])                          # SPY-Lücke -> NaN im Panel
    extra = pd.Series([1.0], index=[pd.Timestamp("1990-01-02")])  # Tag, den ^PUT nicht hat -> verschwindet
    panel = strat.build_panel(put, pd.concat([extra, spy2]), rf)
    assert panel.close.index.equals(put.index)
    assert panel.close["SPY"].iloc[[10, 11]].isna().all()
    assert panel.close["SPY"].drop(panel.close.index[[10, 11]]).notna().all()


# --------------------------------------------------------------------------------------
# Form und Wertebereich der Gewichte
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_shape_and_range(variant):
    panel = _panel()
    p = {**BASE, **VARIANTS[variant]}
    w = strat.weights(panel, **p)
    col = strat.cost_column(p["cost_pp"])
    assert list(w.columns) == [col]
    assert len(w) == 1
    assert w.notna().all().all()
    assert w.index.isin(panel.close.index).all()
    assert w.index.is_monotonic_increasing and not w.index.has_duplicates
    assert (w.sum(axis=1) <= 1.0 + 1e-12).all()                   # keine Hebelung
    assert (w > 0).all().all()                                    # kein Short, kein Nullgewicht


def test_first_row_is_first_day_and_variant_columns():
    panel = _panel()
    idx = panel.close.index
    assert strat.weights(panel, **BASE).index[0] == idx[0]
    assert list(strat.weights(panel, cost_pp=0.25).columns) == ["PUT_C025"]
    assert list(strat.weights(panel, cost_pp=1.00).columns) == ["PUT_C100"]
    w08 = strat.weights(panel, **strat.SPEC["variants"]["from_2008"])
    assert w08.index[0] == pd.Timestamp("2008-01-01")             # erster Handelstag der Synthetik ab dem Stichtag
    assert pd.Timestamp("2008-01-01") in idx


def test_first_signal_lands_on_next_available_day():
    panel = _panel()
    w = strat.weights(panel, first_signal="2008-01-05")           # Samstag -> nächster Handelstag ist Montag der 7.
    assert w.index[0] == pd.Timestamp("2008-01-07")
    assert len(strat.weights(panel, first_signal="2100-01-01")) == 0       # nach Datenende: nichts


def test_only_put_column_is_weighted():
    panel = _panel()
    for v in VARIANTS.values():
        w = strat.weights(panel, **{**BASE, **v})
        assert set(w.columns) <= {"PUT_C025", "PUT_C050", "PUT_C100"}
        assert "SPY" not in w.columns and "RF" not in w.columns


def test_missing_cost_column_raises():
    panel = _panel()
    with pytest.raises(KeyError):
        strat.weights(panel, cost_pp=0.75)


# --------------------------------------------------------------------------------------
# NaN-Preise = nicht handelbar
# --------------------------------------------------------------------------------------

def _nan_panel() -> Panel:
    panel = _panel()
    close, op = panel.close.copy(), panel.open.copy()
    for c in ("PUT_C025", "PUT_C050", "PUT_C100"):
        close.iloc[:400, close.columns.get_loc(c)] = np.nan       # ^PUT noch nicht veröffentlicht
        op.iloc[:400, op.columns.get_loc(c)] = np.nan
        close.iloc[900:915, close.columns.get_loc(c)] = np.nan    # Datenlücke mitten in der Reihe
        op.iloc[900:915, op.columns.get_loc(c)] = np.nan
    return Panel(op, close)


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_no_weights_on_nan_prices(variant):
    panel = _nan_panel()
    p = {**BASE, **VARIANTS[variant]}
    w = strat.weights(panel, **p)
    col = strat.cost_column(p["cost_pp"])
    assert w.notna().all().all()
    assert panel.close.loc[w.index, col].notna().all()            # nie ein Gewicht auf einem NaN-Kurs
    if variant != "from_2008":
        assert w.index[0] == panel.close.index[400]               # erster Tag mit gültigem Kurs
    # Stichtag mitten in der NaN-Lücke -> Einstieg am ersten gültigen Tag danach
    gap = strat.weights(panel, first_signal=str(panel.close.index[905].date()))
    assert gap.index[0] == panel.close.index[915]


def test_empty_when_no_valid_price():
    panel = _panel()
    empty = Panel(panel.open * np.nan, panel.close * np.nan)
    w = strat.weights(empty, **BASE)
    assert len(w) == 0 and list(w.columns) == ["PUT_C050"]
    assert isinstance(w.index, pd.DatetimeIndex)


# --------------------------------------------------------------------------------------
# Kausalität
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_causality(variant):
    panel = _panel()
    p = {**BASE, **VARIANTS[variant]}
    assert check_causality(lambda pn, _p=p: strat.weights(pn, **_p), panel) == []


def test_causality_edge_cuts_and_nan_panel():
    panel = _panel()
    idx = panel.close.index
    cuts = [idx[0], idx[1], idx[2], idx[300], idx[2900]]
    assert check_causality(lambda pn: strat.weights(pn, **BASE), panel, cuts=cuts) == []
    nan_panel = _nan_panel()
    cuts_nan = [idx[100], idx[399], idx[400], idx[401], idx[905], idx[1500]]    # u. a. direkt um den ersten gültigen Kurs
    assert check_causality(lambda pn: strat.weights(pn, **BASE), nan_panel, cuts=cuts_nan) == []
    f08 = strat.SPEC["variants"]["from_2008"]
    cuts_08 = [idx[idx.get_loc(pd.Timestamp("2008-01-01")) + k] for k in (-2, -1, 0, 1, 5)]
    assert check_causality(lambda pn: strat.weights(pn, **f08), panel, cuts=cuts_08) == []


def test_causality_check_detects_lookahead_in_this_setup():
    """Negativkontrolle: eine Ganzstichproben-Skalierung (Look-ahead) wird vom Test tatsächlich erkannt."""
    panel = _panel()

    def cheating(pn):
        w = strat.weights(pn, **BASE)
        return w * (1.0 + float(pn.close["PUT_C050"].pct_change().std()) * 50.0)

    assert check_causality(cheating, panel) != []


def test_weights_do_not_depend_on_future_crash():
    put, spy, rf = _inputs()
    base = strat.weights(strat.build_panel(put, spy, rf), **BASE)
    put2 = put.copy()
    put2.iloc[2000:] = put2.iloc[2000:] * 0.1                     # Crash nach dem Einstieg
    shocked = strat.weights(strat.build_panel(put2, spy, rf), **BASE)
    assert base.equals(shocked)


# --------------------------------------------------------------------------------------
# Engine-Integration (Ausführungs-Timing, Exposure, Kosten)
# --------------------------------------------------------------------------------------

def test_engine_timing_buy_and_hold_after_entry():
    """Signal t=0 -> Handel zum Schluss von t=1 -> NAV folgt ab t=1 exakt der Kostenspalte (ohne Kosten/Zins)."""
    panel = _panel()
    idx = panel.close.index
    w = strat.weights(panel, **BASE)
    res = run_backtest(panel, w, cost=CostModel(default_bps=0.0), rf=pd.Series(0.0, index=idx))
    lvl = panel.close["PUT_C050"]
    assert (res.nav.iloc[:2] == 1.0).all()                        # Tag 0 und 1: Cash bzw. Einstieg zum Schlusskurs
    ref = lvl / lvl.iloc[1]
    assert np.allclose(res.nav.iloc[1:].to_numpy(), ref.iloc[1:].to_numpy(), rtol=1e-10, atol=1e-12)
    assert res.n_trades == 1 and res.skipped_orders == 0


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_engine_run_exposure_and_trades(variant):
    panel = _panel()
    p = {**BASE, **VARIANTS[variant]}
    w = strat.weights(panel, **p)
    res = run_backtest(panel, w, cost=CostModel(), rf=pd.Series(0.00015, index=panel.close.index))
    assert res.nav.notna().all() and (res.nav > 0).all()
    assert res.n_trades == 1 and res.skipped_orders == 0
    assert float(res.gross_exposure.max()) <= 1.0 + 0.01          # 5 bp Einstiegskosten, keine Hebelung
    assert (res.gross_exposure.loc[:w.index[0]] == 0).all()        # vor dem Signal ist alles Cash
    col = strat.cost_column(p["cost_pp"])
    assert (res.weights.drop(columns=[col]).abs().to_numpy() == 0).all()      # nie Position in SPY/RF/anderen Spalten


def test_engine_entry_deferred_when_price_missing_next_day():
    panel = _panel()
    close, op = panel.close.copy(), panel.open.copy()
    close.iloc[1, close.columns.get_loc("PUT_C050")] = np.nan     # Ausführungstag hat keinen Kurs
    op.iloc[1, op.columns.get_loc("PUT_C050")] = np.nan
    p2 = Panel(op, close)
    w = strat.weights(p2, **BASE)
    assert w.index[0] == close.index[0]
    res = run_backtest(p2, w, cost=CostModel(default_bps=0.0), rf=pd.Series(0.0, index=close.index))
    assert res.skipped_orders >= 1
    assert res.n_trades == 1
    assert res.gross_exposure.iloc[-1] == pytest.approx(1.0, abs=1e-6)
    assert float(res.gross_exposure.iloc[1]) == 0.0               # am NaN-Tag nicht investiert
    assert float(res.gross_exposure.iloc[2]) == pytest.approx(1.0, abs=1e-6)


def test_higher_cost_means_lower_terminal_nav():
    panel = _panel()
    idx = panel.close.index
    navs = {}
    for c in strat.COST_GRID_PP:
        w = strat.weights(panel, cost_pp=c)
        navs[c] = run_backtest(panel, w, cost=CostModel(default_bps=0.0), rf=pd.Series(0.0, index=idx)).nav.iloc[-1]
    assert navs[0.25] > navs[0.50] > navs[1.00]
    years = (N - 2) / 252.0                                       # Position von Tag 1 bis Ende
    assert navs[0.25] / navs[0.50] == pytest.approx(np.exp(0.0025 * years), rel=2e-3)
    assert navs[0.50] / navs[1.00] == pytest.approx(np.exp(0.0050 * years), rel=3e-3)


# --------------------------------------------------------------------------------------
# Pflichtvergleich (b): beta-gematchter SPY/Cash-Mix
# --------------------------------------------------------------------------------------

def _oracle_month_ends(idx: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Nur im Test: letzter Datentag jedes vollständigen Monats (letzter, evtl. unvollständiger Monat entfällt)."""
    s = pd.Series(idx, index=idx)
    key = s.dt.year * 12 + s.dt.month
    last = pd.DatetimeIndex(s.groupby(key.to_numpy()).last().to_numpy())
    return last[:-1]


def _reference_beta(panel: Panel, me_dates: pd.DatetimeIndex, col: str, min_months: int) -> dict:
    """Plumpe Referenz: OLS-Steigung per np.polyfit auf allen Monats-Exzessrenditen bis zum Monatsende."""
    c = panel.close.loc[me_dates]
    r = c.iloc[1:].to_numpy() / c.iloc[:-1].to_numpy() - 1.0                   # Spalten: [col, SPY, RF]-Reihenfolge s. u.
    cols = list(c.columns)
    y = r[:, cols.index(col)] - r[:, cols.index("RF")]
    x = r[:, cols.index("SPY")] - r[:, cols.index("RF")]
    out = {}
    for k in range(min_months, len(y) + 1):                                    # k Monatsrenditen, die k-te gehört zu me_dates[k]
        slope = np.polyfit(x[:k], y[:k], 1)[0]
        out[me_dates[k]] = float(np.clip(slope, 0.0, 1.0))
    return out


def test_beta_matched_matches_reference():
    panel = _panel()
    me = _oracle_month_ends(panel.close.index)
    w = strat.beta_matched_weights(panel)
    ref = _reference_beta(panel, me, "PUT_C050", 36)
    assert list(w.columns) == ["SPY"]
    got = w["SPY"].loc[list(ref)]
    assert np.allclose(got.to_numpy(), list(ref.values()), rtol=0, atol=1e-9)
    assert w.index[0] == me[36]                                   # 36 Monatsrenditen -> erstes Gewicht am 37. Monatsende
    assert abs(float(w["SPY"].iloc[-1]) - 0.6) < 0.08             # simuliertes Beta 0.6 wird wiedergefunden


def test_beta_matched_range_and_clipping():
    panel = _panel()
    w = strat.beta_matched_weights(panel)
    assert (w["SPY"] >= 0).all() and (w["SPY"] <= 1.0).all()
    assert (w.sum(axis=1) <= 1.0 + 1e-12).all()
    # Beta weit über 1 -> auf 1 begrenzt; negatives Beta -> 0
    hi = strat.beta_matched_weights(_panel(beta=3.0))
    lo = strat.beta_matched_weights(_panel(beta=-1.0))
    assert np.allclose(hi["SPY"].to_numpy(), 1.0)
    assert np.allclose(lo["SPY"].to_numpy(), 0.0)


def test_beta_matched_independent_of_cost_column():
    panel = _panel()
    a = strat.beta_matched_weights(panel, cost_pp=0.25)["SPY"]
    b = strat.beta_matched_weights(panel, cost_pp=1.00)["SPY"]
    assert float((a - b).abs().max()) < 2e-3


def test_beta_matched_needs_min_months():
    idx = _idx(36 * 21)                                           # knapp unter 36 Monaten Renditen
    spy_r, put_r = _returns(n=len(idx))
    panel = strat.build_panel(_levels(put_r, idx), _levels(spy_r, idx, 40.0), _rf(idx))
    assert len(strat.beta_matched_weights(panel)) == 0
    assert len(strat.beta_matched_weights(panel, min_months=12)) > 0


def test_beta_matched_no_weight_on_nan_spy_month_end():
    panel = _panel()
    me = _oracle_month_ends(panel.close.index)
    bad = me[60]
    close = panel.close.copy()
    close.loc[bad, "SPY"] = np.nan
    w = strat.beta_matched_weights(Panel(close.copy(), close))
    assert bad not in w.index and me[59] in w.index and me[61] in w.index
    assert w["SPY"].notna().all()


def test_beta_matched_causality():
    panel = _panel()
    assert check_causality(lambda pn: strat.beta_matched_weights(pn), panel) == []
    cuts = [panel.close.index[i] for i in (900, 1100, 1101, 1500, 3000)]
    assert check_causality(lambda pn: strat.beta_matched_weights(pn), panel, cuts=cuts) == []
    f = lambda pn: strat.beta_matched_weights(pn, first_signal="2002-01-01")  # noqa: E731
    assert check_causality(f, panel) == []


def test_beta_matched_month_ends_use_calendar_flags():
    panel = _panel()
    w = strat.beta_matched_weights(panel)
    flags = month_end_flags(panel.close.index)
    assert flags.loc[w.index].all()                               # nur kausal erkannte Monatsenden
    # abgeschnittenes Panel: der letzte Datentag ist kein Monatsende, solange der NYSE-Kalender das verneint
    cut = panel.close.index[1800]
    if not month_end_flags(panel.close.index[: 1801]).iloc[-1]:
        assert cut not in strat.beta_matched_weights(panel.truncate(cut)).index


def test_beta_matched_engine_run():
    panel = _panel()
    w = strat.beta_matched_weights(panel)
    res = run_backtest(panel, w, cost=CostModel(), rf=pd.Series(0.00015, index=panel.close.index))
    assert (res.nav > 0).all() and res.skipped_orders == 0
    assert float(res.gross_exposure.max()) <= 1.0 + 0.02
    assert (res.weights.drop(columns=["SPY"]).abs().to_numpy() == 0).all()
