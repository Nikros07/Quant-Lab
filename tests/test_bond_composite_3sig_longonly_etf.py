"""Tests für strategies/bond_composite_3sig_longonly_etf.py — nur synthetische Daten, kein Netz, kein Datencache."""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import month_end_flags
from qlab.data import Panel
from qlab.engine import check_causality, default_teilfreistellung, run_backtest
from strategies import bond_composite_3sig_longonly as main
from strategies import bond_composite_3sig_longonly_etf as strat

B, C = strat.BOND, strat.CASH
TNX, IRX, PIE = strat.TNX, strat.IRX, strat.PIE
VARIANTS = {"base": {}, **strat.SPEC["variants"]}
FULL_PARAMS = strat.SPEC["params"]
LISTING_POS = 2800                      # Notierungsbeginn der ETFs (Zeilenposition), nach 2520 Tagen Signalhistorie


# --------------------------------------------------------------------------------------
# Synthetische Daten
# --------------------------------------------------------------------------------------

def _signal_frame(n_years: float = 16, seed: int = 5, start: str = "1990-01-02") -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range(start, periods=int(252 * n_years))
    n = len(idx)
    t = np.arange(n)
    target = 5.0 + 2.5 * np.sin(t / 700.0)
    x = np.empty(n)
    x[0] = target[0]
    for i in range(1, n):
        x[i] = x[i - 1] + 0.004 * (target[i] - x[i - 1]) + rng.normal(0.0, 0.04)
    tnx = np.clip(x, 0.6, 14.0)
    spread = 1.3 + 1.4 * np.sin(t / 180.0 + 0.7) + np.cumsum(rng.normal(0, 0.004, n)) * 0.2
    irx = np.clip(tnx - spread, 0.02, None)
    pie = 2.6 + 1.2 * np.sin(t / 900.0 + 1.0)
    return pd.DataFrame({TNX: tnx, IRX: irx, PIE: pie}, index=idx)


def _etf_prices(idx: pd.DatetimeIndex, seed: int = 8, listing_pos: int = LISTING_POS) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(open, close) für IEF/SHY mit echtem Unterschied zwischen Eröffnung und Schluss; vor der Notierung NaN."""
    rng = np.random.default_rng(seed)
    n = len(idx)
    close, open_ = {}, {}
    for k, (name, vol) in enumerate(((B, 0.004), (C, 0.0012))):
        r_on = rng.normal(0.0001, vol / 2, n)
        r_id = rng.normal(0.0001, vol / 2, n)
        c = np.empty(n)
        o = np.empty(n)
        prev = 100.0 + 10 * k
        for i in range(n):
            o[i] = prev * (1 + r_on[i])
            c[i] = o[i] * (1 + r_id[i])
            prev = c[i]
        c[:listing_pos] = np.nan
        o[:listing_pos] = np.nan
        close[name], open_[name] = c, o
    return pd.DataFrame(open_, index=idx), pd.DataFrame(close, index=idx)


def _panel(n_years: float = 16, seed: int = 5, listing_pos: int = LISTING_POS) -> Panel:
    sig = _signal_frame(n_years, seed)
    o, c = _etf_prices(sig.index, listing_pos=listing_pos)
    return Panel(pd.concat([o, sig], axis=1), pd.concat([c, sig], axis=1))


def _main_panel_from(panel: Panel) -> Panel:
    """Panel für das Hauptmodul auf denselben Signalspalten (Handelstitel = beliebige gültige Reihe)."""
    close = panel.close[[TNX, IRX, PIE]].copy()
    close.insert(0, main.ASSET, 100.0)
    return Panel(close.copy(), close)


def _rf(panel: Panel) -> pd.Series:
    return pd.Series(0.0, index=panel.close.index)


def _month_end_index(panel: Panel) -> pd.DatetimeIndex:
    f = month_end_flags(panel.close.index)
    return f.index[f.to_numpy()]


# --------------------------------------------------------------------------------------
# Vertrag / Form
# --------------------------------------------------------------------------------------

def test_spec_contract():
    spec = strat.SPEC
    assert spec["id"] == "bond_composite_3sig_longonly_etf"
    assert len(spec["variants"]) <= 3
    sig = inspect.signature(strat.weights)
    for name in list(spec["params"]) + [k for v in spec["variants"].values() for k in v]:
        assert name in sig.parameters, name
    assert hasattr(strat, "load")
    assert spec["params"]["bond_asset"] == "IEF" and spec["params"]["cash_asset"] == "SHY"
    assert {B, C, TNX, IRX, PIE} == set(spec["tickers"])
    # Signalparameter identisch zum Hauptmodul (gleiche Regel, nur anderes Handelsinstrument)
    for k in ("signals", "carry_window", "carry_threshold", "ewma_fast", "ewma_slow", "anchor_halflife"):
        assert spec["params"][k] == main.SPEC["params"][k], k
    assert spec["variants"] == main.SPEC["variants"]


def test_etf_tickers_have_no_teilfreistellung():
    assert default_teilfreistellung(B) == 0.0 and default_teilfreistellung(C) == 0.0


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_shape_and_range(variant):
    panel = _panel()
    w = strat.weights(panel, **{**FULL_PARAMS, **VARIANTS[variant]})
    assert list(w.columns) == [B, C]
    assert len(w) > 30
    assert w.notna().all().all()
    assert (w >= -1e-12).all().all() and (w <= 1.0 + 1e-12).all().all()          # kein Hebel, kein Short
    assert np.allclose(w.sum(axis=1).to_numpy(), 1.0)                            # voll investiert: IEF + SHY
    allowed = {0.0, 1.0} if variant != "base" else {0.0, 1 / 3, 2 / 3, 1.0}
    assert set(np.round(np.unique(w[B].to_numpy()), 12)) <= {round(a, 12) for a in allowed}
    assert w.index.isin(_month_end_index(panel)).all()                           # nur an Monatsenden
    assert w.index.is_monotonic_increasing and not w.index.has_duplicates


def test_cash_asset_none_leaves_real_cash():
    panel = _panel()
    w = strat.weights(panel, cash_asset=None)
    assert list(w.columns) == [B]
    assert (w.sum(axis=1) <= 1.0 + 1e-12).all()
    assert np.allclose(w[B].to_numpy(), strat.weights(panel)[B].to_numpy())


def test_weights_never_use_signal_columns():
    w = strat.weights(_panel())
    assert not ({TNX, IRX, PIE} & set(w.columns))


def test_invalid_signal_selection_raises():
    with pytest.raises(ValueError):
        strat.weights(_panel(), signals=())


# --------------------------------------------------------------------------------------
# Gleiche Signale wie im Hauptmodul
# --------------------------------------------------------------------------------------

def test_signals_identical_to_main_module():
    panel = _panel()
    w_etf = strat.weights(panel)
    w_main = main.weights(_main_panel_from(panel))
    common = w_etf.index.intersection(w_main.index)
    assert len(common) == len(w_etf) > 30                      # ETF-Gewichte sind eine Teilmenge der Hauptmodul-Zeilen
    assert np.array_equal(w_etf.loc[common, B].to_numpy(), w_main.loc[common, main.ASSET].to_numpy())
    # Auch für die Einzelsignale
    for name, kw in strat.SPEC["variants"].items():
        a = strat.weights(panel, **{**FULL_PARAMS, **kw})
        b = main.weights(_main_panel_from(panel), **{**main.SPEC["params"], **kw})
        assert np.array_equal(a[B].to_numpy(), b.loc[a.index, main.ASSET].to_numpy()), name


# --------------------------------------------------------------------------------------
# Fehlende Kurse (NaN = nicht handelbar)
# --------------------------------------------------------------------------------------

def test_no_weights_before_etf_listing():
    panel = _panel()
    w = strat.weights(panel)
    listing = panel.close.index[LISTING_POS]
    assert w.index.min() >= listing
    assert not panel.close.loc[w.index, [B, C]].isna().any().any()
    # Vor der Notierung existieren die Signale schon (Hauptmodul-Gewichte beginnen früher) -> das NaN ist der Grund
    assert main.weights(_main_panel_from(panel)).index.min() < listing
    # Erste Zeile = erstes Monatsende ab Notierung (Signale sind dort bereit)
    me = _month_end_index(panel)
    assert w.index[0] == me[me >= listing][0]


def test_single_missing_etf_price_at_month_end():
    panel = _panel()
    base = strat.weights(panel)
    hole = base.index[10]
    for col, kw, expect_row in ((C, {}, False), (C, {"cash_asset": None}, True), (B, {}, False), (B, {"cash_asset": None}, False)):
        close = panel.close.copy()
        close.loc[hole, col] = np.nan
        w = strat.weights(Panel(panel.open.copy(), close), **kw)
        assert (hole in w.index) is expect_row, (col, kw)
        assert base.index[11] in w.index


def test_expired_cpi_series_stops_weights():
    panel = _panel()
    base = strat.weights(panel)
    stop = base.index[20]
    close = panel.close.copy()
    close.loc[close.index > stop, PIE] = np.nan
    w = strat.weights(Panel(panel.open.copy(), close))
    assert w.index.max() <= stop
    assert w.equals(base.loc[:stop])


# --------------------------------------------------------------------------------------
# Kausalität
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_causality_check(variant):
    panel = _panel()
    params = {**FULL_PARAMS, **VARIANTS[variant]}
    assert check_causality(lambda p: strat.weights(p, **params), panel) == []
    me = _month_end_index(panel)
    cuts = [me[-50], me[-30], me[-12], me[-3]]                                   # mitten in der Handelsphase
    assert check_causality(lambda p: strat.weights(p, **params), panel, cuts=cuts) == []


def test_future_data_does_not_change_past_weights():
    panel = _panel()
    base = strat.weights(panel)
    cut = base.index[len(base) // 2]
    close = panel.close.copy()
    after = close.index > cut
    close.loc[after, TNX] = close.loc[after, TNX] * 0.1 + 0.5
    close.loc[after, IRX] = 9.0
    close.loc[after, PIE] = 12.0
    close.loc[after, B] = close.loc[after, B] * 0.01
    other = strat.weights(Panel(panel.open.copy(), close))
    assert base.loc[:cut].equals(other.loc[:cut])
    assert not base.loc[cut:].equals(other.loc[cut:])


def test_last_data_day_mid_month_is_not_month_end():
    panel = _panel()
    idx = panel.close.index
    mid = idx[idx >= pd.Timestamp("2004-06-10")][0]
    w = strat.weights(panel.truncate(mid))
    assert w.index.max() < pd.Timestamp("2004-06-01")
    assert strat.weights(panel).index.max() > mid


# --------------------------------------------------------------------------------------
# Panel-Aufbau (ohne Netz)
# --------------------------------------------------------------------------------------

def test_build_panel_union_index_and_nan_before_listing():
    sig = _signal_frame(3, seed=2, start="2001-01-02")
    pie_m = pd.Series(0.03, index=pd.period_range("1995-01", "2005-12", freq="M"))
    tnx = sig[TNX].drop(sig.index[200])                                  # Tag ohne ^TNX, aber mit ETF-Kurs
    etf_idx = sig.index.drop(sig.index[300]).union(pd.DatetimeIndex(["2001-02-03"]))   # Tag ohne ETF; ein Zusatztag nur im ETF
    o, c = _etf_prices(etf_idx, listing_pos=100)
    etf = Panel(o, c)
    p = strat.build_panel(etf, tnx, sig[IRX], pie_m)
    assert p.close.index.equals(etf.close.index.union(tnx.index))
    assert p.tickers == [B, C, TNX, IRX, PIE]
    assert sig.index[200] in p.close.index                               # ETF-Tag ohne ^TNX bleibt erhalten
    assert sig.index[300] in p.close.index                               # ^TNX-Tag ohne ETF bleibt erhalten
    assert np.isnan(p.close.loc[sig.index[300], B])
    listing = etf_idx[100]
    before = p.close.index < listing
    assert p.close.loc[before, [B, C]].isna().all().all()                # vor der Notierung NaN = nicht handelbar
    later = p.close.loc[~before, [B, C]]
    assert later.drop(sig.index[300]).notna().all().all()                # danach gültig (außer am Tag ohne ETF)
    # Signalspalten: open == close, 1-Tages-Lücke ^TNX vorwärts gefüllt, Prozent
    assert p.open[[TNX, IRX, PIE]].equals(p.close[[TNX, IRX, PIE]])
    assert p.close.loc[sig.index[200], TNX] == pytest.approx(sig[TNX].iloc[199])
    assert p.close[PIE].dropna().iloc[0] == pytest.approx(3.0)
    # ETF-Eröffnung und -Schluss bleiben getrennt erhalten
    assert not p.open[B].dropna().equals(p.close[B].dropna())


# --------------------------------------------------------------------------------------
# Engine-Integration (Ausführungstiming, Exposure)
# --------------------------------------------------------------------------------------

def test_engine_integration_timing_and_exposure():
    panel = _panel()
    w = strat.weights(panel)
    res = run_backtest(panel, w, rf=_rf(panel))
    assert res.skipped_orders == 0
    assert (res.gross_exposure <= 1.0 + 1e-3).all()                          # voll investiert; Kosten kommen aus dem Cash (~3e-4)
    assert (res.weights[[B, C]] >= -1e-9).all().all()
    assert (res.weights[[TNX, IRX, PIE]].abs().to_numpy() < 1e-12).all()      # nie ein Gewicht auf Signalspalten
    idx = panel.close.index
    # Vor der Notierung keine Position (alles NaN-Kurs), nach der ersten Ausführung voll investiert
    assert res.gross_exposure.loc[:idx[LISTING_POS]].max() < 1e-12
    first = w.index[0]
    nxt = idx[idx.get_loc(first) + 1]
    assert res.gross_exposure.loc[first] < 1e-12                            # Signaltag t: noch nichts gehandelt
    assert res.gross_exposure.loc[nxt] == pytest.approx(1.0, abs=2e-3)      # t+1 (Eröffnung): voll investiert in IEF+SHY
    assert res.weights.loc[nxt, B] == pytest.approx(w.loc[first, B], abs=5e-3)   # Tagesdrift Eröffnung -> Schluss
    # gehandelt wird nur am Tag nach einem Signal
    pos = idx.get_indexer(w.index) + 1
    exec_days = idx[pos[pos < len(idx)]]
    assert (res.turnover.drop(exec_days) <= 1e-12).all()
    # Ein Wechsel von w bewegt IEF und SHY gegenläufig: einseitiger Umsatz = |dw| (nicht 2*|dw|)
    changes = w.index[(w[B].diff().abs() > 1e-9).to_numpy()]
    s = changes[2]
    day = idx[idx.get_loc(s) + 1]
    dw = abs(w.loc[s, B] - w[B].shift(1).loc[s])
    assert res.turnover.loc[day] == pytest.approx(dw, abs=0.08)             # Drift zwischen den Signalen verschiebt etwas
    assert res.turnover.loc[day] > 0.5 * dw
