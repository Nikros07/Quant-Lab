"""Tests für strategies/commodity_gold_trend_dbc_gld.py — nur synthetische Panels, kein Netz, kein Datencache.

Bekannte Antworten: konstante Tageswachstumsraten (g > 0 liegt streng über dem eigenen SMA, g < 0 darunter,
g = 0 ist gleich dem SMA und damit AUS wegen "strikt größer") sowie ein unabhängig in numpy gerechnetes
Referenzsignal (Mittel der letzten `window` Schlusskurse inkl. t).
"""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import NYSE_BDAY
from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import commodity_gold_trend_dbc_gld as S

T = S.TICKERS
BASE = S.SPEC["params"]
VARIANTS = {"base": dict(BASE), **{k: {**BASE, **v} for k, v in S.SPEC["variants"].items()}}


# --------------------------------------------------------------------------------------
# Hilfen
# --------------------------------------------------------------------------------------

def nyse_index(n, start="2008-01-02"):
    return pd.date_range(start, periods=n, freq=NYSE_BDAY)


def random_panel(n=1400, seed=5, start="2008-01-02"):
    rng = np.random.default_rng(seed)
    idx = nyse_index(n, start)
    regime = np.where(np.sin(np.arange(n) / 120.0)[:, None] > -0.2, 0.0006, -0.0012)     # Trend- und Baerenphasen
    ret = regime + rng.normal(0.0, 0.01, (n, len(T)))
    close = pd.DataFrame(100.0 * np.exp(np.cumsum(ret, axis=0)), index=idx, columns=T)
    gap = rng.normal(0.0, 0.003, (n, len(T)))
    open_ = close.shift(1).fillna(close.iloc[0]) * np.exp(gap)
    return Panel(open_, close)


def trend_panel(growth: dict, n=500):
    idx = nyse_index(n)
    k = np.arange(n)[:, None]
    g = np.array([growth.get(t, 0.0) for t in T])[None, :]
    close = pd.DataFrame(100.0 * np.exp(g * k), index=idx, columns=T)
    return Panel(close.copy(), close)


def with_nan(panel, ticker, rows):
    close, open_ = panel.close.copy(), panel.open.copy()
    close.loc[rows, ticker] = np.nan
    open_.loc[rows, ticker] = np.nan
    return Panel(open_, close)


def reference_signal(close: pd.Series, window: int) -> pd.Series:
    """Unabhängige Referenz: je Tag Mittel der letzten `window` Beobachtungen (inkl. t); NaN ohne volle Historie."""
    c = close.dropna().to_numpy(float)
    out = np.full(len(c), np.nan)
    for i in range(window - 1, len(c)):
        out[i] = float(c[i] > c[i - window + 1:i + 1].mean())
    return pd.Series(out, index=close.dropna().index).reindex(close.index)


def expected_targets(panel, params) -> pd.DataFrame:
    """Erwarteter Zielvektor je Signaltag aus der unabhängigen Referenz (Tage mit Kurs und voller Historie aller Beine)."""
    uni = list(params["universe"])
    ref = pd.DataFrame({t: reference_signal(panel.close[t], params["window"]) for t in uni})
    ref = ref[ref.notna().all(axis=1)]
    exp = pd.DataFrame(0.0, index=ref.index, columns=T)
    exp[uni] = ref / len(uni)
    return exp


def assert_matches_reference(w, panel, params):
    exp = expected_targets(panel, params)
    assert len(w) > 0 and w.index[0] == exp.index[0]
    assert np.allclose(expand_rows(w, exp.index).to_numpy(), exp.to_numpy(), atol=1e-12)
    assert w.index.isin(exp.index).all()                                 # Zeilen nur an gültigen Signaltagen


def assert_no_weight_on_nan(w, panel):
    px = panel.close.reindex(index=w.index, columns=w.columns)
    assert not ((w > 0) & px.isna()).any().any()


def expand_rows(w: pd.DataFrame, index: pd.DatetimeIndex) -> pd.DataFrame:
    """Zeilen nur bei Wechsel -> Zielvektor je Tag (letzte bekannte Zeile gilt), für Vergleiche mit der Referenz."""
    return w.reindex(index, method="ffill")


# --------------------------------------------------------------------------------------
# SPEC
# --------------------------------------------------------------------------------------

def test_spec_contract():
    s = S.SPEC
    assert s["id"] == "commodity_gold_trend_dbc_gld"
    assert s["tickers"] == ["DBC", "GLD"] and "^IRX" not in s["tickers"]
    assert 1 <= len(s["variants"]) <= 3 and s["sources"]
    sig = inspect.signature(S.weights)
    for name in list(s["params"]) + [k for v in s["variants"].values() for k in v]:
        assert name in sig.parameters, name
    assert s["params"]["window"] == 210 and tuple(s["params"]["universe"]) == ("DBC", "GLD")
    assert {k: v["window"] for k, v in s["variants"].items() if "window" in v} == {"sma168": 168, "sma252": 252}
    assert s["variants"]["gold_only"]["universe"] == ("GLD",)
    assert s["cost_bps"] == {"DBC": 10.0, "GLD": 10.0}


# --------------------------------------------------------------------------------------
# Bekannte Antworten
# --------------------------------------------------------------------------------------

def test_uptrend_on_downtrend_off_with_half_weights():
    p = trend_panel({"DBC": 0.001, "GLD": -0.001})
    w = S.weights(p)
    assert len(w) == 1                                                  # nie ein Wechsel: nur das Startsignal
    assert w.index[0] == p.close.index[BASE["window"] - 1]              # 210. Kurs = erster Tag mit voller Historie
    assert w.iloc[0]["DBC"] == pytest.approx(0.5) and w.iloc[0]["GLD"] == 0.0


def test_both_up_is_fully_invested_in_two_halves_and_flat_is_off():
    w_up = S.weights(trend_panel({"DBC": 0.0005, "GLD": 0.0003}))
    assert w_up.iloc[-1].to_numpy() == pytest.approx([0.5, 0.5])
    w_flat = S.weights(trend_panel({}))                                 # Kurs == SMA -> nicht strikt größer -> AUS
    assert (w_flat.to_numpy() == 0.0).all() and len(w_flat) == 1


def test_signal_uses_close_of_day_t_and_strict_inequality():
    """Flach, dann Sprung an Tag `jump`: genau am Sprungtag schaltet das Bein ein (SMA inkl. t), davor AUS."""
    jump = 300
    p = trend_panel({}, n=400)
    close = p.close.copy()
    close.loc[close.index[jump:], "GLD"] = 101.0
    q = Panel(close.copy(), close)
    w = S.weights(q)
    assert list(w.index) == [q.close.index[BASE["window"] - 1], q.close.index[jump]]
    assert w.iloc[0]["GLD"] == 0.0 and w.iloc[1]["GLD"] == pytest.approx(0.5)
    assert w["DBC"].eq(0.0).all()                                       # DBC bleibt flach = AUS (nicht strikt größer)


def test_crossing_down_switches_off_on_first_day_below_sma():
    n = 600
    k = np.arange(n)
    g = np.where(k < 350, 0.002, -0.004)                                # erst steigend, dann stark fallend
    close = pd.DataFrame({"DBC": 100.0 * np.exp(np.cumsum(g)), "GLD": 100.0 * np.exp(np.cumsum(g))},
                         index=nyse_index(n))
    q = Panel(close.copy(), close)
    w = S.weights(q)
    ref = reference_signal(close["DBC"], BASE["window"])
    first_off = ref[(ref == 0.0) & (ref.index > close.index[350])].index[0]
    assert w.index[-1] == first_off
    assert (w.iloc[-1] == 0.0).all() and (w.iloc[-2] == 0.5).all()


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_matches_independent_reference_on_random_panel(variant):
    p = random_panel()
    params = VARIANTS[variant]
    assert_matches_reference(S.weights(p, **params), p, params)


def test_rows_only_at_target_changes():
    p = random_panel()
    w = S.weights(p)
    assert len(w) > 10
    d = w.diff().abs().sum(axis=1).iloc[1:]
    assert (d > 0).all()                                                # jede Zeile nach der ersten ändert den Zielvektor
    ref = pd.DataFrame({t: reference_signal(p.close[t], 210) for t in T})
    ref = ref[ref.notna().all(axis=1)]
    n_changes = int((ref != ref.shift(1)).any(axis=1).iloc[1:].sum())
    assert len(w) == 1 + n_changes


# --------------------------------------------------------------------------------------
# Varianten
# --------------------------------------------------------------------------------------

def test_variant_windows_set_first_signal_day():
    p = random_panel()
    idx = p.close.index
    for name, win in (("sma168", 168), ("sma252", 252)):
        w = S.weights(p, **VARIANTS[name])
        assert w.index[0] == idx[win - 1], name


def test_gold_only_has_full_weight_on_gld_and_none_on_dbc():
    p = trend_panel({"DBC": 0.001, "GLD": 0.001})
    w = S.weights(p, **VARIANTS["gold_only"])
    assert (w["DBC"] == 0.0).all()
    assert w.iloc[-1]["GLD"] == pytest.approx(1.0)
    w_down = S.weights(trend_panel({"DBC": 0.001, "GLD": -0.001}), **VARIANTS["gold_only"])
    assert (w_down.to_numpy() == 0.0).all()


def test_gold_only_starts_when_gld_has_history_even_if_dbc_is_not_listed():
    p0 = trend_panel({"DBC": 0.001, "GLD": 0.001}, n=700)
    q = with_nan(p0, "DBC", p0.close.index[:400])
    w = S.weights(q, **VARIANTS["gold_only"])
    assert w.index[0] == q.close.index[BASE["window"] - 1]
    w_base = S.weights(q)
    assert w_base.index[0] == q.close.index[400 + BASE["window"] - 1]   # Basis wartet auf die DBC-Historie


# --------------------------------------------------------------------------------------
# Form, Wertebereich
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_shape_range_and_exposure(variant):
    p = random_panel()
    params = VARIANTS[variant]
    w = S.weights(p, **params)
    n = len(params["universe"])
    assert len(w) > 5
    assert list(w.columns) == T
    assert w.index.is_monotonic_increasing and w.index.is_unique
    assert set(w.index) <= set(p.close.index)
    assert not w.isna().any().any()
    assert set(np.unique(w.to_numpy().round(12))) <= {0.0, round(1.0 / n, 12)}
    assert (w >= 0).all().all() and (w <= 1.0 / n + 1e-12).all().all()
    assert (w.sum(axis=1) <= 1.0 + 1e-12).all()                          # kein Hebel, Rest ist Cash
    for t in set(T) - set(params["universe"]):
        assert (w[t] == 0.0).all()
    assert_no_weight_on_nan(w, p)


def test_short_history_gives_empty_frame_with_columns():
    p = random_panel(n=150)
    w = S.weights(p)
    assert len(w) == 0 and list(w.columns) == T


def test_parameter_validation():
    p = random_panel(n=300)
    with pytest.raises(ValueError):
        S.weights(p, window=1)
    with pytest.raises(ValueError):
        S.weights(p, window=10.5)
    with pytest.raises(ValueError):
        S.weights(p, universe=())
    with pytest.raises(ValueError):
        S.weights(p, universe=("DBC", "SPY"))
    with pytest.raises(ValueError):
        S.weights(p, universe=("GLD", "GLD"))


# --------------------------------------------------------------------------------------
# Fehlende Preise = nicht handelbar
# --------------------------------------------------------------------------------------

def test_late_listed_dbc_blocks_base_signals_until_full_history():
    p0 = random_panel()
    q = with_nan(p0, "DBC", p0.close.index[:321])                       # DBC startet erst später (wie in echt)
    w = S.weights(q)
    first_dbc = q.close["DBC"].first_valid_index()
    pos = q.close.index.get_loc(first_dbc)
    assert w.index.min() == q.close.index[pos + BASE["window"] - 1]
    assert w.index.min() > first_dbc
    assert_no_weight_on_nan(w, q)


def test_missing_price_on_signal_day_gives_no_row_that_day_but_bridges_history():
    p0 = random_panel()
    t_star = S.weights(p0).index[5]                                     # ein Tag, an dem sich das Ziel ändert
    q = with_nan(p0, "GLD", [t_star])
    w = S.weights(q)
    assert t_star not in w.index                                        # Kurs fehlt -> kein Signal an diesem Tag
    assert len(w.loc[w.index > t_star]) > 5                             # Lücke von einem Tag blockiert die Historie nicht
    assert_no_weight_on_nan(w, q)
    assert_matches_reference(w, q, BASE)                                # SMA über die eigenen Beobachtungen


def test_delisted_asset_stops_signals_and_never_gets_weight():
    p0 = random_panel()
    cut = 900
    q = with_nan(p0, "DBC", p0.close.index[cut:])
    w = S.weights(q)
    assert w.index.max() < q.close.index[cut]
    assert_no_weight_on_nan(w, q)
    w_gold = S.weights(q, **VARIANTS["gold_only"])                      # Gold-Variante läuft unabhängig weiter
    assert w_gold.index.max() > q.close.index[cut]
    assert_no_weight_on_nan(w_gold, q)


def test_long_gap_gives_no_weight_on_nan_and_no_crash():
    p0 = random_panel()
    q = with_nan(p0, "GLD", p0.close.index[600:625])
    for params in VARIANTS.values():
        w = S.weights(q, **params)
        assert len(w) > 0 and not w.isna().any().any()
        assert_no_weight_on_nan(w, q)
        assert_matches_reference(w, q, params)


# --------------------------------------------------------------------------------------
# Kausalität
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_check_causality_passes(variant):
    p = random_panel()
    params = VARIANTS[variant]
    assert check_causality(lambda pp, _pa=params: S.weights(pp, **_pa), p, n_cuts=9) == []


def test_check_causality_with_nan_history_and_gap():
    p0 = random_panel()
    q = with_nan(p0, "DBC", p0.close.index[:300])
    q = with_nan(q, "GLD", p0.close.index[700:712])
    assert check_causality(lambda pp: S.weights(pp, **BASE), q, n_cuts=11) == []


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_future_prices_do_not_change_past_weights(variant):
    p = random_panel()
    cut = p.close.index[1000]
    close, open_ = p.close.copy(), p.open.copy()
    close.loc[close.index > cut] *= 7.0
    open_.loc[open_.index > cut] *= 7.0
    q = Panel(open_, close)
    a = S.weights(p, **VARIANTS[variant]).loc[:cut]
    b = S.weights(q, **VARIANTS[variant]).loc[:cut]
    assert list(a.index) == list(b.index) and len(a) > 0
    assert (a - b).abs().to_numpy().max() < 1e-12


# --------------------------------------------------------------------------------------
# Zusammenspiel mit der Engine
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_engine_runs_without_skipped_orders_and_never_levered(variant):
    p = random_panel()
    w = S.weights(p, **VARIANTS[variant])
    zero = CostModel(default_bps=0.0, short_fee_annual=0.0, lever_spread_annual=0.0)
    res = run_backtest(p, w, cost=zero, rf=pd.Series(0.0, index=p.close.index))
    assert res.skipped_orders == 0
    assert np.isfinite(res.nav).all() and (res.nav > 0).all()
    assert res.gross_exposure.max() <= 1.0 + 1e-6                       # nie gehebelt
    assert res.gross_exposure.loc[:w.index[0]].max() == 0.0             # vor dem Startsignal kein Kapital im Markt
    assert (res.weights >= -1e-12).all().all()                          # nie Short
    costed = run_backtest(p, w, cost=CostModel(per_ticker_bps=S.SPEC["cost_bps"]),
                          rf=pd.Series(0.0, index=p.close.index))
    assert costed.cost.sum() > 0 and costed.n_trades > 0


def test_engine_trades_next_open_after_first_signal():
    p = trend_panel({"DBC": 0.001, "GLD": 0.001})
    w = S.weights(p)
    zero = CostModel(default_bps=0.0, short_fee_annual=0.0, lever_spread_annual=0.0)
    res = run_backtest(p, w, cost=zero, rf=pd.Series(0.0, index=p.close.index))
    first_trade_day = p.close.index[p.close.index.get_loc(w.index[0]) + 1]   # Signal t, Handel zur Eröffnung t+1
    assert res.turnover.loc[:w.index[0]].sum() == 0.0
    assert res.turnover.loc[first_trade_day] == pytest.approx(0.5, abs=1e-9)   # einseitig: 100 % des NAV gekauft
    assert res.gross_exposure.loc[first_trade_day] == pytest.approx(1.0, abs=1e-9)
