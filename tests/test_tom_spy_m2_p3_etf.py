"""Tests für strategies/tom_spy_m2_p3_etf.py — nur synthetische Daten, kein Netz, kein Datencache."""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import NYSE_BDAY
from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import tom_spy_m2_p3 as main
from strategies import tom_spy_m2_p3_etf as strat

ASSET, ASSET_OPEN = strat.ASSET, strat.ASSET_OPEN
VARIANTS = {"base": {}, **strat.SPEC["variants"]}
START, END = "2003-01-02", "2007-12-14"

# Wie im Hauptmodul-Test: Lage relativ zur Position p des letzten Handelstags d(-1) eines Monats
SIGNALS = {"base": (-2, 2), "tag_plus1": (-1, 0), "konservativ": (-1, 3)}


def _params(variant: str) -> dict:
    return {**strat.SPEC["params"], **VARIANTS[variant]}


def _ohlc(start=START, end=END, seed=4) -> pd.DataFrame:
    """Synthetischer SPY mit echtem NYSE-Kalender; die Eröffnung weicht deutlich vom Vortagsschluss ab (Über-Nacht-Lücke)."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start, end, freq=NYSE_BDAY)
    close = 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, len(idx))))
    prev = np.r_[close[0], close[:-1]]
    open_ = prev * (1 + rng.normal(0.0, 0.004, len(idx)))
    return pd.DataFrame({"Open": open_, "Close": close}, index=idx)


def _complete_month_ends(idx: pd.DatetimeIndex) -> list[int]:
    s = pd.Series(np.arange(len(idx)), index=idx)
    last = [int(p) for p in s.groupby([idx.year, idx.month]).max()]
    return [p for p in last if p - 3 >= 0 and p + 5 < len(idx)]


def _engine(panel, w, bps: float = 0.0, **kw):
    rf = pd.Series(0.0, index=panel.close.index)
    return run_backtest(panel, w, cost=CostModel(default_bps=bps), rf=rf, **kw)


def _expected_returns(ohlc: pd.DataFrame, variant: str) -> pd.Series:
    """Erwartete Tagesrendite bei Nullkosten und Nullzins, aus den Kursen von Hand gerechnet."""
    o, c = ohlc["Open"].to_numpy(), ohlc["Close"].to_numpy()
    cc = np.r_[0.0, c[1:] / c[:-1] - 1.0]                      # Schluss -> Schluss
    out = np.zeros(len(c))
    for p in _complete_month_ends(ohlc.index):
        if variant == "base":                                  # Kauf Close(d(-2)), Verkauf Close(d(+3))
            out[p:p + 4] = cc[p:p + 4]
        elif variant == "tag_plus1":                           # Kauf Close(d(-1)), Verkauf Close(d(+1))
            out[p + 1] = cc[p + 1]
        else:                                                  # Kauf Open(d(-1)), Verkauf Open(d(+4))
            out[p] = c[p] / o[p] - 1.0
            out[p + 1:p + 4] = cc[p + 1:p + 4]
            out[p + 4] = o[p + 4] / c[p + 3] - 1.0
    return pd.Series(out, index=ohlc.index)


# --------------------------------------------------------------------------------------
# Vertrag / Panel
# --------------------------------------------------------------------------------------

def test_spec_contract():
    spec = strat.SPEC
    assert spec["id"] == "tom_spy_m2_p3_etf"
    assert spec["family"] == "calendar" and spec["sources"] and spec["start"] == "1993-01-01"
    assert 1 <= len(spec["variants"]) <= 3
    sig = inspect.signature(strat.weights)
    for name in list(spec["params"]) + [k for v in spec["variants"].values() for k in v]:
        assert name in sig.parameters, name
    assert spec["params"] == {"asset": ASSET, "entry_day": -2, "exit_day": 3}
    assert spec["variants"]["konservativ"]["asset"] == ASSET_OPEN
    assert spec["cost_bps"] == {ASSET: 2.0, ASSET_OPEN: 2.0}
    assert spec["tickers"] == ["SPY"] and hasattr(strat, "load")
    assert spec["sources"] == main.SPEC["sources"]


def test_build_panel_has_a_moc_column_and_a_real_open_column():
    ohlc = _ohlc()
    p = strat.build_panel(ohlc)
    assert p.tickers == [ASSET, ASSET_OPEN]
    assert p.open[ASSET].equals(ohlc["Close"]) and p.close[ASSET].equals(ohlc["Close"])       # SPY: Handel zum Schluss
    assert p.open[ASSET_OPEN].equals(ohlc["Open"]) and p.close[ASSET_OPEN].equals(ohlc["Close"])   # echte Eröffnung
    assert not p.open[ASSET_OPEN].equals(p.close[ASSET_OPEN])
    assert p.close.index.equals(ohlc.index)


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_shape_and_range(variant):
    panel = strat.build_panel(_ohlc())
    p = _params(variant)
    w = strat.weights(panel, **p)
    assert list(w.columns) == [p["asset"]]
    assert len(w) > 80
    assert w.notna().all().all()
    assert set(np.unique(w.to_numpy())) <= {0.0, 1.0}
    assert (w.sum(axis=1) <= 1.0 + 1e-12).all() and (w >= 0).all().all()
    assert w.index.isin(panel.close.index).all() and w.index.is_monotonic_increasing and not w.index.has_duplicates
    vals = w[p["asset"]].to_numpy()
    assert vals[0] == 1.0 and (np.abs(np.diff(vals)) == 1.0).all()


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_signal_rows_match_the_calendar_oracle(variant):
    ohlc = _ohlc()
    panel = strat.build_panel(ohlc)
    idx = ohlc.index
    p = _params(variant)
    w = strat.weights(panel, **p)[p["asset"]]
    e, x = SIGNALS[variant]
    ps = _complete_month_ends(idx)
    assert list(w.index[w == 1.0]) == [idx[q + e] for q in ps]
    assert list(w.index[w == 0.0]) == [idx[q + x] for q in ps]


def test_same_rule_as_the_french_main_module():
    """Auf identischem Kalender liefern Haupt- und ETF-Modul dieselben Signalzeilen (nur Spaltenname verschieden)."""
    ohlc = _ohlc()
    r = ohlc["Close"].pct_change().fillna(0.0)
    wm = main.weights(main.build_panel(r))
    we = strat.weights(strat.build_panel(ohlc))
    assert wm.index.equals(we.index) and np.allclose(wm["MKT"].to_numpy(), we[ASSET].to_numpy())
    for v in ("tag_plus1",):
        a = main.weights(main.build_panel(r), **main.SPEC["variants"][v])
        b = strat.weights(strat.build_panel(ohlc), **strat.SPEC["variants"][v])
        assert a.index.equals(b.index)


def test_first_signal_with_spy_like_start_is_the_first_complete_window():
    """SPY startet am letzten Handelstag des Januars 1993: das Januar-Fenster fehlt, Februar ist das erste."""
    ohlc = _ohlc("1993-01-29", "1993-12-31")
    w = strat.weights(strat.build_panel(ohlc))[ASSET]
    assert w.index[0] == pd.Timestamp("1993-02-24") and w.iloc[0] == 1.0       # d(-1) = Fr 26.02.
    assert w.index[1] == pd.Timestamp("1993-03-02") and w.iloc[1] == 0.0       # Ausstiegssignal d(+2): Mo 01.03. = d(+1)


# --------------------------------------------------------------------------------------
# Fehlende Kurse
# --------------------------------------------------------------------------------------

def test_no_weights_on_nan_prices_before_listing():
    ohlc = _ohlc()
    panel = strat.build_panel(ohlc)
    cut = pd.Timestamp("2004-06-30")
    close, open_ = panel.close.copy(), panel.open.copy()
    close.loc[:cut] = np.nan
    open_.loc[:cut] = np.nan
    p2 = Panel(open_, close)
    for variant in VARIANTS:
        p = _params(variant)
        w = strat.weights(p2, **p)
        assert len(w) > 0 and w.index.min() > cut and w.notna().all().all()
        assert not p2.close.loc[w.index, p["asset"]].isna().any()
    w = strat.weights(p2)
    assert w.index[0] == pd.Timestamp("2004-07-28") and w.iloc[0, 0] == 1.0       # Juni-Fenster ohne Preis fällt ganz aus


# --------------------------------------------------------------------------------------
# Kausalität
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_causality_check(variant):
    panel = strat.build_panel(_ohlc())
    p = _params(variant)
    assert check_causality(lambda pn: strat.weights(pn, **p), panel) == []


def test_causality_on_every_single_day_of_a_stretch():
    panel = strat.build_panel(_ohlc("2004-12-01", "2006-07-31"))
    idx = panel.close.index
    cuts = list(idx[(idx >= "2005-10-15") & (idx <= "2006-03-15")])
    for variant in ("base", "konservativ"):
        p = _params(variant)
        assert check_causality(lambda pn: strat.weights(pn, **p), panel, cuts=cuts) == [], variant


def test_future_prices_do_not_change_past_weights():
    panel = strat.build_panel(_ohlc())
    base = strat.weights(panel)
    cut = panel.close.index[int(len(panel.close) * 0.6)]
    close, open_ = panel.close.copy(), panel.open.copy()
    close.loc[close.index > cut] *= 0.01
    open_.loc[open_.index > cut] *= 0.01
    assert base.loc[:cut].equals(strat.weights(Panel(open_, close)).loc[:cut])


# --------------------------------------------------------------------------------------
# Engine-Integration: MOC-Semantik der Basis, echte Eröffnung der Variante "konservativ"
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_engine_returns_match_hand_computed_prices(variant):
    """Basis und tag_plus1 verdienen Schluss-zu-Schluss-Renditen (MOC); konservativ Open(d(-1)) bis Open(d(+4))."""
    ohlc = _ohlc()
    panel = strat.build_panel(ohlc)
    p = _params(variant)
    res = _engine(panel, strat.weights(panel, **p))
    np.testing.assert_allclose(res.ret.to_numpy(), _expected_returns(ohlc, variant).to_numpy(), atol=1e-10)
    assert res.skipped_orders == 0
    other = ASSET_OPEN if p["asset"] == ASSET else ASSET
    assert (res.weights[other].abs() < 1e-12).all()                              # die andere Spalte wird nie gehandelt


def test_base_ignores_the_overnight_gap_between_open_and_close():
    """Die Basis darf nicht von den Eröffnungskursen abhängen (SPY-Spalte hat open == close)."""
    ohlc = _ohlc()
    ohlc2 = ohlc.copy()
    ohlc2["Open"] = ohlc2["Open"] * 1.05                                         # völlig andere Eröffnungen
    r1 = _engine(strat.build_panel(ohlc), strat.weights(strat.build_panel(ohlc))).ret
    r2 = _engine(strat.build_panel(ohlc2), strat.weights(strat.build_panel(ohlc2))).ret
    np.testing.assert_allclose(r1.to_numpy(), r2.to_numpy(), atol=1e-12)


def test_engine_base_timing_exposure_and_costs():
    ohlc = _ohlc()
    panel = strat.build_panel(ohlc)
    idx = ohlc.index
    w = strat.weights(panel)
    res = _engine(panel, w, bps=2.0)
    ps = _complete_month_ends(idx)
    exec_days = set(idx[[q + o for q in ps for o in (-1, 3)]])                   # Kauf d(-2), Verkauf d(+3)
    assert set(res.turnover.index[res.turnover > 1e-12]) == exec_days
    assert res.n_trades == 2 * len(ps)
    assert float(res.cost.sum()) == pytest.approx(2 * len(ps) * 2e-4, rel=0.02)
    assert (res.gross_exposure <= 1.0 + 1e-3).all()
    assert 0.16 < (res.weights[ASSET].loc["2004-01-01":"2007-06-30"] > 0.5).mean() < 0.22


def test_konservativ_trades_at_the_open_of_the_following_day():
    ohlc = _ohlc()
    panel = strat.build_panel(ohlc)
    idx = ohlc.index
    p = _params("konservativ")
    w = strat.weights(panel, **p)
    res = _engine(panel, w)
    q = _complete_month_ends(idx)[10]
    wd = res.weights[ASSET_OPEN]
    assert wd.loc[idx[q - 1]] == 0.0                                             # Signaltag d(-2): noch nicht investiert
    assert wd.loc[idx[q]] > 0.9                                                  # Kauf zur Eröffnung von d(-1)
    assert wd.loc[idx[q + 3]] > 0.9                                              # am Ausstiegssignal-Tag noch investiert
    assert wd.loc[idx[q + 4]] == pytest.approx(0.0, abs=1e-9)                    # Verkauf zur Eröffnung von d(+4)
