"""Tests für strategies/eq_voltarget_ewma_harvey.py — nur synthetische Daten, kein Netz, kein Datencache."""
from __future__ import annotations

import inspect
import math

import numpy as np
import pandas as pd
import pytest

from qlab.data import Panel, panel_from_returns
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import eq_voltarget_ewma_harvey as strat

ASSET = strat.ASSET
BASE = {**strat.SPEC["params"], "first_signal": None}          # first_signal (1928) soll in den Tests nicht binden
VARIANTS = {"base": {}, **strat.SPEC["variants"]}


def _params(variant: str, **over) -> dict:
    return {**BASE, **VARIANTS[variant], **over}


def _returns(seed=11, n=1800, vols=(0.005, 0.02, 0.01)) -> np.ndarray:
    """Tagesrenditen mit drei Vol-Regimen (ruhig -> turbulent -> mittel), je ein Drittel."""
    rng = np.random.default_rng(seed)
    sig = np.repeat(np.asarray(vols, float), math.ceil(n / len(vols)))[:n]
    return 0.0004 + sig * rng.standard_normal(n)


def _idx(n=1800, start="1999-01-04") -> pd.DatetimeIndex:
    return pd.bdate_range(start, periods=n)


def _panel_from_ret(r: np.ndarray, start="1999-01-04", open_noise=0.0, seed=5) -> Panel:
    """Close = 100 * Produkt(1 + r); Eröffnung = Schluss des Vortags * (1 + Rauschen) (open == close bei Rauschen 0)."""
    idx = _idx(len(r), start)
    close = pd.Series(100.0 * np.cumprod(1.0 + r), index=idx)
    if open_noise > 0:
        rng = np.random.default_rng(seed)
        op = close.shift(1).fillna(close.iloc[0]) * (1 + rng.normal(0, open_noise, len(r)))
    else:
        op = close.copy()
    return Panel(pd.DataFrame({ASSET: op}), pd.DataFrame({ASSET: close}))


def _panel(**kw) -> Panel:
    return _panel_from_ret(_returns(), **kw)


def _reference_sigma(close: np.ndarray, halflife: float, warmup: int) -> np.ndarray:
    """Unabhängige, bewusst plumpe Referenz der Spezifikation (reine Python-Schleifen, Position = Tagesindex)."""
    lam = 0.5 ** (1.0 / halflife)
    r = [float("nan")] + [close[i] / close[i - 1] - 1.0 for i in range(1, len(close))]
    out = [float("nan")] * len(close)
    first = 1                                              # r[0] existiert nicht (keine Vorgängerkurs)
    v = sum(x * x for x in r[first:first + warmup]) / warmup
    out[first + warmup - 1] = math.sqrt(252 * v)
    for t in range(first + warmup, len(close)):
        v = lam * v + (1 - lam) * r[t] ** 2
        out[t] = math.sqrt(252 * v)
    return np.asarray(out)


def _reference_weights(close: np.ndarray, target_vol, halflife, cap, band, warmup) -> dict[int, float]:
    sig = _reference_sigma(close, halflife, warmup)
    pos, out = 0.0, {}
    for t in range(len(close)):
        if math.isnan(sig[t]):
            continue
        tgt = min(cap, target_vol / sig[t])
        if abs(tgt - pos) >= band:
            pos = tgt
            out[t] = tgt
    return out


# --------------------------------------------------------------------------------------
# Vertrag / Form
# --------------------------------------------------------------------------------------

def test_spec_contract():
    spec = strat.SPEC
    assert spec["id"] == "eq_voltarget_ewma_harvey"
    assert spec["family"] == "volmgmt"
    assert len(spec["variants"]) <= 3
    sig = inspect.signature(strat.weights)
    for name in list(spec["params"]) + [k for v in spec["variants"].values() for k in v]:
        assert name in sig.parameters, name
    assert spec["cost_bps"][ASSET] == 2.0
    assert spec["params"]["target_vol"] == 0.12 and spec["params"]["halflife"] == 20
    assert spec["params"]["cap"] == 1.0 and spec["params"]["band"] == 0.05 and spec["params"]["warmup"] == 270
    assert spec["variants"] == {"cap_1_5": {"cap": 1.5}, "hl_40": {"halflife": 40}, "vol_10": {"target_vol": 0.10}}
    assert hasattr(strat, "load")


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_shape_and_range(variant):
    panel = _panel()
    p = _params(variant)
    w = strat.weights(panel, **p)
    assert list(w.columns) == [ASSET]
    assert len(w) > 5
    assert w.notna().all().all()
    assert w.index.isin(panel.close.index).all()
    assert w.index.is_monotonic_increasing and not w.index.has_duplicates
    # Summe der Gewichte <= erlaubte Brutto-Exposure (CAP), kein Short, kein Nullgewicht
    assert (w.sum(axis=1) <= p["cap"] + 1e-12).all()
    assert (w > 0).all().all()
    assert w.index[0] >= panel.close.index[p["warmup"]]


def test_empty_when_history_too_short():
    panel = _panel_from_ret(_returns(n=200))
    w = strat.weights(panel, **BASE)
    assert len(w) == 0 and list(w.columns) == [ASSET]


def test_first_signal_after_warmup_and_first_signal_date():
    panel = _panel()
    idx = panel.close.index
    w = strat.weights(panel, **BASE)
    assert w.index[0] == idx[270]                       # 270 gültige Renditen -> erstes Signal am 270. Rendite-Tag
    w2 = strat.weights(panel, **{**BASE, "first_signal": "2003-01-01"})
    assert w2.index[0] >= pd.Timestamp("2003-01-01")
    assert len(w2) > 0


# --------------------------------------------------------------------------------------
# Regel
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_matches_reference_every_day(variant):
    """Ohne Band muss jeder Tag ab Warmup exakt min(CAP, Ziel / sig) tragen (unabhängige Referenzrechnung)."""
    panel = _panel()
    p = _params(variant, band=0.0)
    w = strat.weights(panel, **p)
    ref = _reference_weights(panel.close[ASSET].to_numpy(), p["target_vol"], p["halflife"], p["cap"], 0.0, p["warmup"])
    assert list(w.index) == [panel.close.index[t] for t in ref]
    assert np.allclose(w[ASSET].to_numpy(), list(ref.values()), rtol=1e-10, atol=1e-12)


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_matches_reference_with_band(variant):
    panel = _panel()
    p = _params(variant)
    w = strat.weights(panel, **p)
    ref = _reference_weights(panel.close[ASSET].to_numpy(), p["target_vol"], p["halflife"], p["cap"], p["band"], p["warmup"])
    assert list(w.index) == [panel.close.index[t] for t in ref]
    assert np.allclose(w[ASSET].to_numpy(), list(ref.values()), rtol=1e-10, atol=1e-12)
    # Band: aufeinanderfolgende Signale unterscheiden sich um mindestens 5 pp, erstes Signal von Cash aus
    vals = np.concatenate([[0.0], w[ASSET].to_numpy()])
    assert (np.abs(np.diff(vals)) >= p["band"] - 1e-12).all()


def test_band_reduces_number_of_trades():
    panel = _panel()
    n_band = len(strat.weights(panel, **BASE))
    n_daily = len(strat.weights(panel, **{**BASE, "band": 0.0}))
    assert 0 < n_band < n_daily / 5


def test_weight_falls_when_vol_rises():
    """Ruhiges Regime (Vol 8 %) -> Gewicht am Cap; turbulentes Regime (Vol 32 %) -> deutlich darunter (~12/32)."""
    panel = _panel_from_ret(_returns(vols=(0.005, 0.02, 0.01)))
    w = strat.weights(panel, **BASE)[ASSET]
    idx = panel.close.index
    calm = w.loc[:idx[590]]
    assert calm.iloc[-1] == pytest.approx(1.0)                               # Cap 1.0 (12 % / 8 % > 1)
    turbulent = w.loc[idx[1100]:idx[1190]]                                   # ~500 Tage nach Regimewechsel
    assert turbulent.iloc[-1] < 0.55
    # Mit Hebel-Cap ist das ruhige Gewicht höher als 1 (12 % / 8 % = 1.5), das turbulente unverändert
    w15 = strat.weights(panel, **_params("cap_1_5"))[ASSET]
    assert w15.loc[:idx[590]].iloc[-1] > 1.2
    assert w15.max() <= 1.5 + 1e-12


def test_vol_estimator_uses_only_past_returns():
    """Ein Crash nach dem Schnitt darf keine früheren Gewichte ändern (explizite Version des Kausalitätstests)."""
    r = _returns()
    cut = 1200
    base = strat.weights(_panel_from_ret(r), **BASE)
    r2 = r.copy()
    r2[cut + 1:] = -0.08                                                      # Dauer-Crash nach dem Schnitt
    shocked = strat.weights(_panel_from_ret(r2), **BASE)
    idx = _idx(len(r))
    a, b = base.loc[:idx[cut]], shocked.loc[:idx[cut]]
    assert list(a.index) == list(b.index)
    assert np.allclose(a.to_numpy(), b.to_numpy(), rtol=0, atol=1e-12)
    assert len(shocked.loc[idx[cut + 1]:]) > 0                                # nach dem Schnitt reagiert die Strategie


# --------------------------------------------------------------------------------------
# NaN-Preise = nicht handelbar
# --------------------------------------------------------------------------------------

def _nan_panel() -> Panel:
    panel = _panel_from_ret(_returns())
    close = panel.close.copy()
    op = panel.open.copy()
    close.iloc[:400, 0] = np.nan                         # Ticker noch nicht gelistet
    op.iloc[:400, 0] = np.nan
    close.iloc[900:915, 0] = np.nan                      # Datenlücke mitten in der Reihe
    op.iloc[900:915, 0] = np.nan
    return Panel(op, close)


def test_no_weights_on_nan_prices():
    panel = _nan_panel()
    idx = panel.close.index
    w = strat.weights(panel, **{**BASE, "band": 0.0})                         # ohne Band: jeder handelbare Tag ein Signal
    assert w.notna().all().all()
    assert panel.close.loc[w.index, ASSET].notna().all()                      # nie ein Gewicht auf einem NaN-Kurs
    assert w.index[0] == idx[400 + 270]                                       # 270 gültige Renditen nach Listing
    # Tag 915 hat keine gültige Rendite (Vortag NaN) -> kein Signal; Tage 900-914 sowieso nicht
    assert not w.index.isin(idx[900:916]).any()
    assert w.index.isin(idx[916:]).sum() == len(idx[916:])
    # Panel ohne ein einziges gültiges Kursdatum liefert nichts, ohne abzustürzen
    empty = Panel(panel.open * np.nan, panel.close * np.nan)
    assert len(strat.weights(empty, **BASE)) == 0


# --------------------------------------------------------------------------------------
# Kausalität
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_causality(variant):
    panel = _panel()
    p = _params(variant)
    assert check_causality(lambda pn, _p=p: strat.weights(pn, **_p), panel) == []


def test_causality_edge_cuts_and_nan_panel():
    panel = _panel()
    idx = panel.close.index
    cuts = [idx[100], idx[269], idx[270], idx[271], idx[600], idx[1500]]      # u. a. direkt um das Warmup-Ende
    assert check_causality(lambda pn: strat.weights(pn, **BASE), panel, cuts=cuts) == []
    assert check_causality(lambda pn: strat.weights(pn, **BASE), _nan_panel()) == []
    assert check_causality(lambda pn: strat.weights(pn, **{**BASE, "band": 0.0}), _nan_panel(),
                           cuts=[idx[500], idx[899], idx[905], idx[915], idx[1000]]) == []


def test_causality_check_detects_lookahead_in_this_setup():
    """Negativkontrolle: eine Ganzstichproben-Skalierung (Look-ahead) wird vom Test tatsächlich erkannt."""
    panel = _panel()

    def cheating(pn):
        w = strat.weights(pn, **{**BASE, "band": 0.0})
        return w * float(pn.close[ASSET].pct_change().std() * 100.0)

    assert check_causality(cheating, panel) != []


# --------------------------------------------------------------------------------------
# Engine-Integration (Ausführungs-Timing)
# --------------------------------------------------------------------------------------

def test_french_style_panel_timing_matches_spec():
    """Panel wie aus load() (panel_from_returns, open == close): Signal t -> Handel Schluss t+1 -> verdient r[t+2].

    Ohne Kosten, ohne Zins und ohne Band ist die Engine-Rendite exakt R[s] = w[s-2] * r[s] (Spezifikation).
    """
    r = pd.Series(_returns(), index=_idx())
    panel = panel_from_returns(pd.DataFrame({ASSET: r}))
    idx = panel.close.index
    w = strat.weights(panel, **{**BASE, "band": 0.0})
    res = run_backtest(panel, w, cost=CostModel(default_bps=0.0), rf=pd.Series(0.0, index=idx))
    ret = panel.close[ASSET].pct_change().fillna(0.0)
    pos = w[ASSET].reindex(idx).shift(2).fillna(0.0)
    nav_ref = (1.0 + pos * ret).cumprod()
    assert np.allclose(res.nav.to_numpy(), nav_ref.to_numpy(), rtol=1e-10, atol=1e-12)


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_engine_run_exposure_within_cap(variant):
    panel = _panel_from_ret(_returns(), open_noise=0.0)
    p = _params(variant)
    w = strat.weights(panel, **p)
    res = run_backtest(panel, w, cost=CostModel(per_ticker_bps={ASSET: 2.0}))
    assert res.nav.notna().all() and (res.nav > 0).all()
    assert res.skipped_orders == 0
    assert res.n_trades > 0
    # Brutto-Exposure ≈ höchstens CAP (kleine Überschreitung durch Kosten/negativen Cash und Kursdrift)
    assert float(res.gross_exposure.max()) <= p["cap"] * 1.05 + 0.01
    # vor dem ersten Signal liegt alles in Cash
    assert (res.gross_exposure.loc[:w.index[0]] == 0).all()
