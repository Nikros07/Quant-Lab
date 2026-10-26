"""Tests für strategies/svxy_term_structure_filter.py — nur synthetische Daten, kein Netz, kein Datencache."""
from __future__ import annotations

import inspect
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import svxy_term_structure_filter as strat

SVXY, SPY, VIX, VIX3M = strat.SVXY, strat.SPY, strat.VIX, strat.VIX3M
VARIANTS = {"base": {}, **strat.SPEC["variants"]}
EPS = 1e-12


def _params(variant: str) -> dict:
    return {**strat.SPEC["params"], **VARIANTS[variant]}


def _panel(n: int = 900, seed: int = 3, start: str = "2012-01-02", svxy_nan_days: int = 0,
           vix3m_nan_days: int = 0, ratio=None) -> Panel:
    """Synthetisches Panel: SVXY/SPY-Zufallspfade mit eigener Open-Reihe, VIX3M ~ 20, VIX = ratio * VIX3M."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range(start, periods=n)
    i = np.arange(n)
    if ratio is None:
        ratio = 1.0 + 0.08 * np.sin(i / 37.0) + 0.03 * rng.normal(size=n)       # kreuzt 1.0 oft
    ratio = np.asarray(ratio, float)
    vix3m = 20.0 + 2.0 * np.sin(i / 70.0)
    close = pd.DataFrame(index=idx)
    open_ = pd.DataFrame(index=idx)
    for name, mu, sd in ((SVXY, -0.0005, 0.03), (SPY, 0.0004, 0.01)):
        c = 50.0 * np.exp(np.cumsum(rng.normal(mu, sd, n)))
        o = np.concatenate([[c[0] * 0.999], c[:-1]]) * np.exp(rng.normal(0.0, 0.004, n))
        close[name], open_[name] = c, o
    for name, vals in ((VIX, ratio * vix3m), (VIX3M, vix3m)):
        close[name] = vals
        open_[name] = vals
    if svxy_nan_days:
        close.iloc[:svxy_nan_days, close.columns.get_loc(SVXY)] = np.nan
        open_.iloc[:svxy_nan_days, open_.columns.get_loc(SVXY)] = np.nan
    if vix3m_nan_days:
        close.iloc[:vix3m_nan_days, close.columns.get_loc(VIX3M)] = np.nan
        open_.iloc[:vix3m_nan_days, open_.columns.get_loc(VIX3M)] = np.nan
    return Panel(open_, close)


def _step_ratio(n: int = 520) -> np.ndarray:
    """Fester Verhältnispfad: AUS 0-99, EIN 100-199, AUS 200-259, EIN 260-399, exakt 1.0 (AUS) ab 400."""
    r = np.full(n, 1.1)
    r[100:200] = 0.9
    r[260:400] = 0.95
    r[400:] = 1.0
    return r


def _reference_rows(close: pd.DataFrame, asset: str, threshold: float, w: float) -> pd.Series:
    """Unabhängige Schleife über Tage mit Kurs (ohne fehlende Vol-Daten): Zeilen nur bei Zustandswechsel."""
    out, prev = {}, None
    for d in close.index:
        if not np.isfinite(close.at[d, asset]):
            continue
        ratio = close.at[d, VIX] / close.at[d, VIX3M]
        on = bool(ratio < threshold)
        if prev is None or on != prev:
            out[d] = w if on else 0.0
        prev = on
    return pd.Series(out, dtype=float)


# --------------------------------------------------------------------------------------
# Vertrag / Spezifikation
# --------------------------------------------------------------------------------------

def test_spec_contract():
    spec = strat.SPEC
    assert spec["id"] == "svxy_term_structure_filter"
    assert Path(strat.__file__).stem == spec["id"]
    assert spec["family"] == "volpremium"
    assert spec["sources"] and spec["start"] == "2006-07-17"
    assert len(spec["variants"]) <= 3
    sig = inspect.signature(strat.weights)
    for name in list(spec["params"]) + [k for v in spec["variants"].values() for k in v]:
        assert name in sig.parameters, name
    assert spec["params"] == {"w": 1.0, "threshold": 1.0, "asset": "SVXY"}
    assert spec["variants"] == {"w025": {"w": 0.25}, "spy_secondary": {"asset": "SPY"}}
    assert spec["tickers"] == [SVXY, SPY, VIX, VIX3M]
    assert "^IRX" not in spec["tickers"]
    assert spec["cost_bps"] == {"SVXY": 20.0, "SPY": 2.0}
    assert VIX not in spec["cost_bps"] and VIX3M not in spec["cost_bps"]


def test_registry_discovers_module():
    from strategies._registry import discover

    assert discover()[strat.SPEC["id"]] is strat


@pytest.mark.parametrize("bad", [0.0, -0.5, 1.01, 2.0])
def test_weight_cap_is_enforced(bad):
    with pytest.raises(ValueError):
        strat.weights(_panel(n=100), w=bad)


def test_unknown_asset_rejected():
    with pytest.raises(ValueError):
        strat.weights(_panel(n=100), asset="^VIX")
    with pytest.raises(ValueError):
        strat.weights(_panel(n=100), asset="XIV")


# --------------------------------------------------------------------------------------
# Form und Wertebereich
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_shape_and_range(variant):
    params = _params(variant)
    panel = _panel()
    w = strat.weights(panel, **params)
    assert list(w.columns) == [params["asset"]]                       # ^VIX/^VIX3M/ungenutzter Titel nie im Ziel
    assert len(w) > 10
    assert w.notna().all().all() and np.isfinite(w.to_numpy()).all()
    assert w.index.isin(panel.close.index).all() and w.index.is_monotonic_increasing
    assert not w.index.has_duplicates
    vals = set(np.unique(w.to_numpy()))
    assert vals <= {0.0, params["w"]}
    assert vals == {0.0, params["w"]}                                  # EIN und AUS kommen vor (Test nicht leer)
    assert (w.sum(axis=1) <= params["w"] + EPS).all()
    assert (w.sum(axis=1) <= strat.MAX_WEIGHT + EPS).all()            # nie Hebel
    assert (w.to_numpy() >= 0.0).all()                                 # nie Short
    assert not (np.signbit(w.to_numpy()) & (w.to_numpy() == 0.0)).any()   # kein -0.0


def test_w025_is_scaled_base_signal():
    panel = _panel(seed=11)
    base = strat.weights(panel)
    small = strat.weights(panel, **_params("w025"))
    assert list(base.index) == list(small.index)
    assert np.allclose(small[SVXY].to_numpy(), 0.25 * base[SVXY].to_numpy(), atol=EPS)


# --------------------------------------------------------------------------------------
# Regel
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("asset", [SVXY, SPY])
@pytest.mark.parametrize("threshold", [1.0, 1.05])
def test_matches_reference_rule(asset, threshold):
    panel = _panel(n=1000, seed=9)
    got = strat.weights(panel, threshold=threshold, asset=asset)[asset]
    ref = _reference_rows(panel.close, asset, threshold, 1.0)
    assert list(got.index) == list(ref.index)
    assert np.allclose(got.to_numpy(), ref.to_numpy(), atol=EPS)
    assert (ref == 1.0).any() and (ref == 0.0).any()


def test_rows_only_at_state_changes():
    w = strat.weights(_panel(n=1000, seed=5))[SVXY]
    assert (w.diff().dropna().abs() > 0).all()                         # nie zwei gleiche Zeilen hintereinander
    assert 6 < len(w) < 400


def test_threshold_is_strict():
    n = 520
    panel = _panel(n=n, ratio=_step_ratio(n))
    w = strat.weights(panel)[SVXY]
    idx = panel.close.index
    assert w.loc[idx[100]] == 1.0                                      # 0.9 < 1 -> EIN
    assert w.loc[idx[200]] == 0.0
    assert w.loc[idx[260]] == 1.0
    assert w.loc[idx[400]] == 0.0                                      # exakt 1.0 -> AUS
    assert idx[401] not in w.index and idx[519] not in w.index         # keine weiteren Wechsel
    assert list(w.index) == [idx[0], idx[100], idx[200], idx[260], idx[400]]
    assert list(w.to_numpy()) == [0.0, 1.0, 0.0, 1.0, 0.0]


def test_threshold_parameter_is_used():
    n = 520
    panel = _panel(n=n, ratio=_step_ratio(n))
    w = strat.weights(panel, threshold=1.05)[SVXY]                    # 1.0 < 1.05 -> ab 400 weiter EIN
    assert w.iloc[-1] == 1.0 and w.index[-1] == panel.close.index[260]


def test_first_row_even_if_off():
    n = 300
    panel = _panel(n=n, ratio=np.full(n, 1.2))                         # dauerhaft Backwardation
    w = strat.weights(panel)
    assert len(w) == 1 and w.index[0] == panel.close.index[0]
    assert w.iloc[0, 0] == 0.0


def test_asset_start_and_signal_start():
    panel = _panel(n=700, seed=6, svxy_nan_days=300)
    idx = panel.close.index
    base = strat.weights(panel)
    spy = strat.weights(panel, asset=SPY)
    assert base.index[0] == idx[300]                                   # SVXY erst ab Tag 300
    assert spy.index[0] == idx[0]
    assert (base.index >= idx[300]).all()


def test_missing_vix3m_history_delays_first_signal():
    panel = _panel(n=700, seed=7, vix3m_nan_days=250)
    idx = panel.close.index
    w = strat.weights(panel)
    assert w.index[0] == idx[250]                                      # VIX3M startet später


def test_spy_variant_has_same_states_as_base_on_common_days():
    panel = _panel(n=900, seed=8)
    a = strat.weights(panel)[SVXY]
    b = strat.weights(panel, asset=SPY)[SPY]
    assert list(a.index) == list(b.index)
    assert np.allclose(a.to_numpy(), b.to_numpy(), atol=EPS)


# --------------------------------------------------------------------------------------
# Fehlende Daten
# --------------------------------------------------------------------------------------

def test_no_weights_on_nan_prices_and_no_phantom_switch():
    panel = _panel(n=800, seed=12)
    close, open_ = panel.close.copy(), panel.open.copy()
    gap = list(range(350, 353)) + [500]
    close.iloc[gap, close.columns.get_loc(SVXY)] = np.nan
    open_.iloc[gap, open_.columns.get_loc(SVXY)] = np.nan
    p2 = Panel(open_, close)
    w = strat.weights(p2)
    assert w.notna().all().all()
    assert close.loc[w.index, SVXY].notna().all()                      # nie eine Zeile an einem Tag ohne Kurs
    ref = strat.weights(_panel(n=800, seed=12))[SVXY]
    for d in close.index[gap]:
        assert d not in w.index
    # eine Kurslücke allein erzeugt keinen Schein-Wechsel: die Zeilen stimmen mit der Referenz ohne Lücke überein,
    # soweit der Zustand nicht gerade an einem Lückentag gewechselt hätte
    common = w.index.intersection(ref.index)
    assert len(common) > 5
    assert np.allclose(w.loc[common, SVXY].to_numpy(), ref.loc[common].to_numpy())


def test_short_vol_gap_is_bridged_long_gap_means_cash():
    n = 400
    panel = _panel(n=n, ratio=np.full(n, 0.9))                         # dauerhaft EIN
    idx = panel.close.index
    close, open_ = panel.close.copy(), panel.open.copy()
    close.iloc[100:105, close.columns.get_loc(VIX3M)] = np.nan         # 5 Zeilen: ueberbrueckt
    close.iloc[200:206, close.columns.get_loc(VIX3M)] = np.nan         # 6 Zeilen: ab der 6. fehlt das Signal
    w = strat.weights(Panel(open_, close))[SVXY]
    assert list(w.index) == [idx[0], idx[205], idx[206]]
    assert list(w.to_numpy()) == [1.0, 0.0, 1.0]


def test_empty_when_no_signal_or_no_asset():
    n = 120
    p = _panel(n=n)
    close, open_ = p.close.copy(), p.open.copy()
    close[VIX3M] = np.nan
    w = strat.weights(Panel(open_, close))
    assert len(w) == 0 and list(w.columns) == [SVXY]
    close2 = p.close.copy()
    close2[SVXY] = np.nan
    w2 = strat.weights(Panel(p.open.copy(), close2))
    assert len(w2) == 0 and list(w2.columns) == [SVXY]
    assert len(strat.weights(Panel(p.open.copy(), close2), asset=SPY)) > 0


def test_nonpositive_vix3m_is_treated_as_missing():
    n = 200
    p = _panel(n=n, ratio=np.full(n, 0.9))
    close = p.close.copy()
    close.iloc[50:, close.columns.get_loc(VIX3M)] = 0.0                # kaputte Daten
    w = strat.weights(Panel(p.open.copy(), close))[SVXY]
    assert np.isfinite(w.to_numpy()).all()
    assert w.iloc[-1] == 0.0                                           # ohne gültiges Verhältnis -> Cash


def test_term_ratio_and_contango_on():
    idx = pd.bdate_range("2020-01-02", periods=4)
    v = pd.Series([15.0, 20.0, 25.0, np.nan], index=idx)
    v3 = pd.Series([20.0, 20.0, 20.0, 20.0], index=idx)
    on = strat.contango_on(v, v3)
    assert list(on) == [True, False, False, False]                     # 0.75 EIN, 1.0 AUS (strikt), 1.25 AUS, ffill 25/20 AUS
    r = strat.term_ratio(v, v3)
    assert r.iloc[0] == pytest.approx(0.75) and r.iloc[3] == pytest.approx(1.25)


def test_split_by_regime():
    idx = pd.bdate_range("2018-02-20", "2018-03-09")
    ret = pd.Series(0.01, index=idx)
    parts = strat.split_by_regime(ret)
    assert parts["svxy_minus_1x"].index.max() == pd.Timestamp("2018-02-27")
    assert parts["svxy_minus_0_5x"].index.min() == pd.Timestamp("2018-02-28")
    assert len(parts["svxy_minus_1x"]) + len(parts["svxy_minus_0_5x"]) == len(ret)


# --------------------------------------------------------------------------------------
# Kausalität
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_causality_check(variant):
    params = _params(variant)
    panel = _panel(n=1000, seed=13)
    assert check_causality(lambda p: strat.weights(p, **params), panel) == []


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_causality_check_with_gaps_and_late_start(variant):
    params = _params(variant)
    panel = _panel(n=1000, seed=14, svxy_nan_days=300, vix3m_nan_days=40)
    close, open_ = panel.close.copy(), panel.open.copy()
    close.iloc[600:603, close.columns.get_loc(SVXY)] = np.nan
    close.iloc[700:708, close.columns.get_loc(VIX)] = np.nan
    close.iloc[800, close.columns.get_loc(VIX3M)] = np.nan
    p2 = Panel(open_, close)
    assert check_causality(lambda p: strat.weights(p, **params), p2) == []
    assert check_causality(lambda p: strat.weights(p, **params), p2, n_cuts=12) == []


def test_future_data_do_not_change_past_weights():
    panel = _panel(n=900, seed=17)
    base = strat.weights(panel)
    cut = panel.close.index[int(len(panel.close) * 0.6)]
    close = panel.close.copy()
    close.loc[close.index > cut, VIX] *= 3.0                           # Stress nach dem Schnitt
    close.loc[close.index > cut, SVXY] *= 0.5
    other = strat.weights(Panel(panel.open.copy(), close))
    assert base.loc[:cut].equals(other.loc[:cut])
    assert not base.loc[cut:].equals(other.loc[cut:])                  # Test ist nicht trivial


# --------------------------------------------------------------------------------------
# Engine-Integration
# --------------------------------------------------------------------------------------

def _expected_daily_returns(panel: Panel, w: pd.DataFrame, asset: str) -> pd.Series:
    """Tagesrenditen nach der Spezifikation (W = 1, Kosten 0, Cash-Zins 0), aus dem Zustand ON_t / ON_t-1."""
    idx = panel.close.index
    close, open_ = panel.close[asset], panel.open[asset]
    state = w[asset].reindex(idx).ffill().fillna(0.0)                 # Zustand nach dem Signal von Tag t
    out = pd.Series(0.0, index=idx)
    for k in range(1, len(idx)):                  # Renditetag k = t+1, Signaltag t = k-1
        on_t = state.iloc[k - 1] > 0
        on_tm1 = state.iloc[k - 2] > 0 if k >= 2 else False
        if on_t and on_tm1:
            out.iloc[k] = close.iloc[k] / close.iloc[k - 1] - 1.0
        elif on_t and not on_tm1:
            out.iloc[k] = close.iloc[k] / open_.iloc[k] - 1.0
        elif (not on_t) and on_tm1:
            out.iloc[k] = open_.iloc[k] / close.iloc[k - 1] - 1.0
    return out


def test_engine_matches_spec_daily_returns_and_timing():
    n = 520
    panel = _panel(n=n, seed=2, ratio=_step_ratio(n))
    idx = panel.close.index
    w = strat.weights(panel)
    res = run_backtest(panel, w, cost=CostModel(default_bps=0.0), rf=pd.Series(0.0, index=idx))
    # Timing: Signal EIN am Schluss von Tag 100 -> Position erst nach der Eröffnung von Tag 101
    assert res.weights.loc[idx[100], SVXY] == pytest.approx(0.0, abs=1e-12)
    assert res.weights.loc[idx[101], SVXY] == pytest.approx(1.0, abs=1e-9)
    assert res.weights.loc[idx[199], SVXY] == pytest.approx(1.0, abs=1e-9)
    # Signal AUS am Schluss von Tag 200 -> am Tag 200 noch voll investiert, am Tag 201 flach
    assert res.weights.loc[idx[200], SVXY] == pytest.approx(1.0, abs=1e-9)
    assert res.weights.loc[idx[201], SVXY] == pytest.approx(0.0, abs=1e-12)
    # Tagesrenditen gemäß Spezifikation (Einstieg Close/Open, Ausstieg Open/Close_vortag, sonst Close/Close)
    expected = _expected_daily_returns(panel, w, SVXY)
    assert np.allclose(res.ret.iloc[1:].to_numpy(), expected.iloc[1:].to_numpy(), atol=1e-9)
    entry = idx[101]
    assert res.ret.loc[entry] == pytest.approx(panel.close.at[entry, SVXY] / panel.open.at[entry, SVXY] - 1.0, abs=1e-9)
    exit_ = idx[201]
    assert res.ret.loc[exit_] == pytest.approx(panel.open.at[exit_, SVXY] / panel.close.at[idx[200], SVXY] - 1.0, abs=1e-9)
    hold = idx[150]
    assert res.ret.loc[hold] == pytest.approx(panel.close.at[hold, SVXY] / panel.close.at[idx[149], SVXY] - 1.0, abs=1e-9)
    # nie ein Gewicht auf Vol-Indizes oder SPY im Hauptlauf; keine geblockten Orders
    for t in (VIX, VIX3M, SPY):
        assert res.weights[t].abs().max() == 0.0
    assert res.skipped_orders == 0
    assert res.gross_exposure.max() <= 1.02                            # Ziel <= 1, minimaler Kostendrift


def test_engine_costs_per_switch():
    n = 520
    panel = _panel(n=n, seed=2, ratio=_step_ratio(n))
    idx = panel.close.index
    w = strat.weights(panel)
    rf = pd.Series(0.0, index=idx)
    free = run_backtest(panel, w, cost=CostModel(default_bps=0.0), rf=rf)
    paid = run_backtest(panel, w, cost=CostModel(per_ticker_bps=strat.SPEC["cost_bps"]), rf=rf)
    assert paid.n_trades == 4                                          # Einstieg, Ausstieg, Einstieg, Ausstieg
    # 4 Wechsel x 0.20 % vom jeweils gehandelten Wert (~ NAV)
    assert float(paid.cost.sum()) == pytest.approx(4 * 0.002, rel=0.25)
    assert paid.nav.iloc[-1] < free.nav.iloc[-1]


def test_engine_w025_enters_with_quarter_weight_and_does_not_rebalance():
    n = 520
    panel = _panel(n=n, seed=4, ratio=_step_ratio(n))
    idx = panel.close.index
    w = strat.weights(panel, w=0.25)
    res = run_backtest(panel, w, cost=CostModel(default_bps=0.0), rf=pd.Series(0.0, index=idx))
    assert res.weights.loc[idx[101], SVXY] == pytest.approx(0.25, abs=0.005)
    assert res.gross_exposure.max() < 0.25 * 1.6                       # nur Drift, nie in die Nähe von 1.0
    assert res.n_trades == 4                                           # kein tägliches Zurück-Handeln auf 25 %


def test_engine_spy_variant_trades_spy_only():
    n = 520
    panel = _panel(n=n, seed=5, ratio=_step_ratio(n))
    w = strat.weights(panel, asset=SPY)
    res = run_backtest(panel, w, cost=CostModel(per_ticker_bps=strat.SPEC["cost_bps"]),
                       rf=pd.Series(0.0, index=panel.close.index))
    assert res.weights[SPY].abs().max() > 0.9
    for t in (SVXY, VIX, VIX3M):
        assert res.weights[t].abs().max() == 0.0


def test_engine_random_panel_runs_clean():
    panel = _panel(n=1200, seed=21, svxy_nan_days=200)
    for variant in VARIANTS:
        params = _params(variant)
        w = strat.weights(panel, **params)
        res = run_backtest(panel, w, cost=CostModel(per_ticker_bps=strat.SPEC["cost_bps"]),
                           rf=pd.Series(0.0, index=panel.close.index))
        assert np.isfinite(res.nav.to_numpy()).all() and (res.nav > 0).all()
        assert res.skipped_orders == 0
        # Zielgewichte <= W; das tatsächliche Gewicht driftet nur minimal darüber (Wechselkosten werden aus Cash
        # bezahlt, das bei W = 1 dadurch leicht negativ wird) bzw. bei W = 0.25 mit dem Kurs
        cap = 1.02 if variant != "w025" else 0.45
        assert res.gross_exposure.max() <= cap
        assert res.weights[[VIX, VIX3M]].abs().to_numpy().max() == 0.0
