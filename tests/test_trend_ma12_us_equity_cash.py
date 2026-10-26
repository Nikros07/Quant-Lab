"""Tests für strategies/trend_ma12_us_equity_cash.py — nur synthetische Daten, kein Netz, kein Datencache."""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import month_end_flags
from qlab.data import Panel
from qlab.engine import check_causality, run_backtest
from strategies import trend_ma12_us_equity_cash as strat

ASSET, SIG = strat.ASSET, strat.SIGNAL
# Für die Tests in der Zukunft beginnen, damit first_signal (1930) nie bindet, außer wo gewollt.
VARIANTS = {"base": {}, **strat.SPEC["variants"]}


def _panel(asset_px: pd.Series, sig_px: pd.Series) -> Panel:
    close = pd.DataFrame({ASSET: asset_px, SIG: sig_px})
    return Panel(close.copy(), close)


def _monthly_step_panel(monthly: np.ndarray, start="2001-01-01") -> tuple[Panel, pd.DatetimeIndex]:
    """Tagespreise, die innerhalb jedes Kalendermonats konstant = Monatswert sind (Monatsende-Preis exakt bekannt)."""
    n_months = len(monthly)
    idx = pd.bdate_range(start, pd.Timestamp(start) + pd.offsets.MonthEnd(n_months) - pd.Timedelta(days=0))
    # nur volle Monate: letzter Handelstag des letzten Monats ist das Ende
    s = pd.Series(idx, index=idx)
    key = s.dt.year * 12 + s.dt.month
    month_no = (key - key.iloc[0]).to_numpy()
    month_no = np.minimum(month_no, n_months - 1)
    px = pd.Series(np.asarray(monthly, float)[month_no], index=idx)
    me_dates = pd.DatetimeIndex(s.groupby(month_no).last().to_numpy())      # Orakel nur im Test (volle Monate)
    return _panel(px.copy(), px.copy()), me_dates


def _random_panel(n_years=12, seed=7, start="2001-01-02") -> Panel:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range(start, periods=int(252 * n_years))
    regime = np.where(np.sin(np.arange(len(idx)) / 180.0) > -0.3, 0.0006, -0.0012)   # Auf- und Abschwünge
    r = regime + rng.normal(0.0, 0.01, len(idx))
    px = pd.Series(100 * np.exp(np.cumsum(r)), index=idx)
    return _panel(px, px * (1 + rng.normal(0, 0.0005, len(idx))))


def _reference(monthly: np.ndarray, ma_short=1, ma_long=12, strict=False) -> list[float | None]:
    out: list[float | None] = []
    for m in range(len(monthly)):
        if m < max(ma_short, ma_long) - 1:
            out.append(None)
            continue
        fast = float(np.mean(monthly[m - ma_short + 1:m + 1]))
        slow = float(np.mean(monthly[m - ma_long + 1:m + 1]))
        out.append(float(fast > slow) if strict else float(fast >= slow))
    return out


# --------------------------------------------------------------------------------------
# Vertrag / Form
# --------------------------------------------------------------------------------------

def test_spec_contract():
    spec = strat.SPEC
    assert spec["id"] == "trend_ma12_us_equity_cash"
    assert len(spec["variants"]) <= 3
    sig = inspect.signature(strat.weights)
    for name in list(spec["params"]) + [k for v in spec["variants"].values() for k in v]:
        assert name in sig.parameters, name
    assert spec["cost_bps"][ASSET] == 10.0
    assert hasattr(strat, "load")


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_shape_and_range(variant):
    panel = _random_panel()
    w = strat.weights(panel, **{**strat.SPEC["params"], **VARIANTS[variant], "first_signal": None})
    assert list(w.columns) == [ASSET]
    assert len(w) > 60
    assert w.notna().all().all()
    assert set(np.unique(w.to_numpy())) <= {0.0, 1.0}
    assert (w.sum(axis=1) <= 1.0 + 1e-12).all() and (w >= 0).all().all()       # kein Hebel, kein Short
    flags = month_end_flags(panel.close.index)
    assert w.index.isin(flags.index[flags.to_numpy()]).all()                     # nur an Monatsenden
    assert w.index.is_monotonic_increasing and not w.index.has_duplicates


# --------------------------------------------------------------------------------------
# Regel
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant,kw", [
    ("base", dict(ma_short=1, ma_long=12, strict=False)),
    ("sma10", dict(ma_short=1, ma_long=10, strict=True)),
    ("ma2_12", dict(ma_short=2, ma_long=12, strict=False)),
])
def test_matches_reference_rule(variant, kw):
    rng = np.random.default_rng(3)
    monthly = 100 * np.exp(np.cumsum(rng.normal(0.004, 0.05, 72)))
    panel, me_dates = _monthly_step_panel(monthly)
    params = {**strat.SPEC["params"], **VARIANTS[variant], "first_signal": None}
    w = strat.weights(panel, **params)
    ref = _reference(monthly, **kw)
    exp = pd.Series({d: v for d, v in zip(me_dates, ref) if v is not None})
    assert list(w.index) == list(exp.index)
    assert np.allclose(w[ASSET].to_numpy(), exp.to_numpy())
    assert exp.nunique() == 2                      # Testpfad enthält Ein- und Ausstiege


def test_first_signal_needs_twelve_month_ends():
    monthly = np.linspace(100, 130, 30)
    panel, me_dates = _monthly_step_panel(monthly)
    w = strat.weights(panel, first_signal=None)
    assert w.index[0] == me_dates[11]              # 12. Monatsende inkl. t
    w10 = strat.weights(panel, first_signal=None, ma_long=10, strict=True)
    assert w10.index[0] == me_dates[9]


def test_ties_constant_prices():
    monthly = np.full(24, 100.0)
    panel, _ = _monthly_step_panel(monthly)
    base = strat.weights(panel, first_signal=None)
    assert (base[ASSET] == 1.0).all()                                   # P_t >= MA12 (Gleichheit zählt)
    sma = strat.weights(panel, first_signal=None, ma_long=10, strict=True)
    assert (sma[ASSET] == 0.0).all()                                    # SMA10-Variante strikt größer


def test_trend_response_exit_and_reentry():
    # 18 Monate steigend, dann Absturz, dann Erholung
    monthly = np.concatenate([np.linspace(100, 160, 18), np.linspace(150, 90, 8), np.linspace(95, 200, 18)])
    panel, me_dates = _monthly_step_panel(monthly)
    w = strat.weights(panel, first_signal=None)[ASSET]
    assert w.loc[me_dates[15]] == 1.0                       # im Aufschwung investiert
    assert w.loc[me_dates[25]] == 0.0                       # nach dem Absturz Cash
    assert w.loc[me_dates[-1]] == 1.0                       # nach der Erholung wieder investiert
    assert w.diff().abs().sum() >= 2                        # mindestens ein Ausstieg und ein Wiedereinstieg


def test_signal_uses_signal_column_not_asset():
    """Signal kommt aus ^GSPC; der Handelstitel darf das Signal nicht bestimmen."""
    up = np.linspace(100, 200, 30)
    panel_a, _ = _monthly_step_panel(up)
    panel_b = _panel(panel_a.close[ASSET], pd.Series(np.interp(np.arange(len(panel_a.close)),
                                                                [0, len(panel_a.close) - 1], [200, 100]),
                                                      index=panel_a.close.index))
    w_up = strat.weights(panel_a, first_signal=None)
    w_dn = strat.weights(panel_b, first_signal=None)
    assert (w_up[ASSET] == 1.0).all()
    assert (w_dn[ASSET] == 0.0).all()                       # Asset steigt, ^GSPC fällt -> Cash
    w_tr = strat.weights(panel_b, first_signal=None, signal=ASSET)
    assert (w_tr[ASSET] == 1.0).all()                       # Variante signal_tr nutzt das Asset selbst


def test_first_signal_cutoff():
    panel = _random_panel(n_years=8, start="2001-01-02")
    w_all = strat.weights(panel, first_signal=None)
    w_cut = strat.weights(panel, first_signal="2004-01-01")
    assert w_cut.index.min() >= pd.Timestamp("2004-01-01")
    assert w_cut.equals(w_all.loc["2004-01-01":])


# --------------------------------------------------------------------------------------
# Fehlende Kurse (NaN = nicht handelbar)
# --------------------------------------------------------------------------------------

def test_no_weights_on_nan_asset_prices():
    panel = _random_panel(n_years=6)
    close = panel.close.copy()
    cut = close.index[400]
    close.loc[:cut, ASSET] = np.nan                         # Titel noch nicht gelistet
    p2 = Panel(close.copy(), close)
    w = strat.weights(p2, first_signal=None)
    assert len(w) > 0
    assert w.index.min() > cut
    assert w.notna().all().all()
    flags = month_end_flags(p2.close.index)
    assert not p2.close.loc[w.index, ASSET].isna().any()
    # Einzelner NaN-Kurs am Monatsende: dort kein Gewicht
    me = flags.index[flags.to_numpy()]
    hole = me[40]
    close2 = panel.close.copy()
    close2.loc[hole, ASSET] = np.nan
    w2 = strat.weights(Panel(close2.copy(), close2), first_signal=None)
    assert hole not in w2.index
    assert me[41] in w2.index


def test_signal_gaps_forward_filled_only_briefly():
    monthly = np.linspace(100, 140, 30)
    panel, me_dates = _monthly_step_panel(monthly)
    # (a) Monatsende ohne ^GSPC-Kurs (z. B. Samstag): Vortageskurs wird genutzt -> Zeile vorhanden
    close = panel.close.copy()
    d = me_dates[20]
    close.loc[d, SIG] = np.nan
    w = strat.weights(Panel(close.copy(), close), first_signal=None)
    assert d in w.index
    # (b) lange Lücke (> 5 Handelstage) -> kein Signal an diesem Monatsende
    close = panel.close.copy()
    d = me_dates[20]
    pos = close.index.get_loc(d)
    close.iloc[pos - 8:pos + 1, close.columns.get_loc(SIG)] = np.nan
    w = strat.weights(Panel(close.copy(), close), first_signal=None)
    assert d not in w.index


# --------------------------------------------------------------------------------------
# Kausalität
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_causality_check(variant):
    panel = _random_panel(n_years=12)
    params = {**strat.SPEC["params"], **VARIANTS[variant]}
    problems = check_causality(lambda p: strat.weights(p, **params), panel)
    assert problems == []
    problems = check_causality(lambda p: strat.weights(p, **{**params, "first_signal": None}), panel)
    assert problems == []


def test_future_prices_do_not_change_past_weights():
    panel = _random_panel(n_years=10)
    base = strat.weights(panel, first_signal=None)
    cut = panel.close.index[int(len(panel.close) * 0.6)]
    close = panel.close.copy()
    close.loc[close.index > cut] *= 0.01                    # drastisch andere Zukunft
    other = strat.weights(Panel(close.copy(), close), first_signal=None)
    a, b = base.loc[:cut], other.loc[:cut]
    assert a.equals(b)


def test_last_data_day_mid_month_is_not_month_end():
    panel = _random_panel(n_years=4)
    idx = panel.close.index
    mid = idx[idx >= pd.Timestamp("2003-06-10")][0]
    w = strat.weights(panel.truncate(mid), first_signal=None)
    assert w.index.max() < pd.Timestamp("2003-06-01")       # Juni-2003 hat noch kein Monatsende
    w_full = strat.weights(panel, first_signal=None)
    assert w_full.index.max() > mid


# --------------------------------------------------------------------------------------
# Engine-Integration (Ausführungstiming, Exposure)
# --------------------------------------------------------------------------------------

def test_engine_integration_timing_and_exposure():
    monthly = np.concatenate([np.linspace(100, 160, 18), np.linspace(150, 90, 8), np.linspace(95, 200, 18)])
    panel, _ = _monthly_step_panel(monthly)
    # etwas Tagesbewegung, damit Kosten/Drift sichtbar sind; Monatsendwerte bleiben maßgeblich
    rng = np.random.default_rng(1)
    noise = pd.Series(1 + rng.normal(0, 0.002, len(panel.close)), index=panel.close.index)
    close = panel.close.mul(noise, axis=0)
    p2 = Panel(close.copy(), close)
    w = strat.weights(p2, first_signal=None)
    res = run_backtest(p2, w)
    assert (res.gross_exposure <= 1.0 + 1e-3).all()
    assert (res.weights[ASSET] >= -1e-9).all()
    # Signal an Tag t (erste 1.0) -> Position erst ab t+1 (Handel zur Eröffnung), nicht schon am Signaltag
    on_dates = w.index[w[ASSET] == 1.0]
    s = on_dates[0]
    assert res.weights.loc[s, ASSET] == 0.0
    nxt = p2.close.index[p2.close.index.get_loc(s) + 1]
    assert res.weights.loc[nxt, ASSET] > 0.95
    # Gehandelt wird nur am Tag nach einem Signal (Monatsende t -> t+1), sonst kein Umsatz
    pos = p2.close.index.get_indexer(w.index) + 1
    exec_days = p2.close.index[pos[pos < len(p2.close.index)]]
    assert (res.turnover.drop(exec_days) <= 1e-12).all()
    # Wechsel (Ein-/Ausstieg) bewegen praktisch das ganze Portfolio (Umsatz ist einseitig: 100 % Umschichtung = 0,5)
    flips = w.index[(w[ASSET].diff().abs() > 0).to_numpy()]
    nxt_days = p2.close.index[p2.close.index.get_indexer(flips) + 1]
    assert (res.turnover.loc[nxt_days] > 0.45).all()


# --------------------------------------------------------------------------------------
# Panel-Aufbau (ohne Netz)
# --------------------------------------------------------------------------------------

def test_build_panel_aligns_signal_without_filling():
    idx = pd.bdate_range("1930-01-01", periods=30)
    sat = pd.DatetimeIndex(["1930-02-15"])            # Samstag-Zeile wie in den alten French-Daten
    idx = idx.union(sat)
    ret = pd.Series(0.001, index=idx)
    g = pd.Series(np.linspace(20, 21, 30), index=pd.bdate_range("1930-01-01", periods=30))
    p = strat.build_panel(ret, g)
    assert p.tickers == [ASSET, SIG]
    assert p.close.index.equals(idx)
    assert p.open.equals(p.close)                     # open == close (Handel zum Folgetag-Schluss)
    assert np.isnan(p.close.loc["1930-02-15", SIG])   # Lücke bleibt Lücke
    assert np.allclose(p.close[SIG].dropna().to_numpy(), g.reindex(idx).dropna().to_numpy())
    assert p.close[ASSET].is_monotonic_increasing
    # Das Signal-Ticker-Gewicht wird nie vergeben
    w = strat.weights(p, first_signal=None, ma_long=2)
    assert list(w.columns) == [ASSET]
