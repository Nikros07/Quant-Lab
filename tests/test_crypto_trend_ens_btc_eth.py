"""Tests für strategies/crypto_trend_ens_btc_eth.py — nur synthetische Daten, kein Netz, kein Datencache."""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import crypto_trend_ens_btc_eth as strat

BTC, ETH = strat.BTC, strat.ETH
VARIANTS = {"base": {}, **strat.SPEC["variants"]}
ETH_LISTING_OFFSET = 1148            # Tage zwischen BTC-Start (2014-09-17) und ETH-Start (2017-11-09)


def _make_panel(n_days=2600, seed=3, start="2014-09-17", eth_offset=ETH_LISTING_OFFSET) -> Panel:
    """7-Tage-Kalender wie bei Krypto; ETH beginnt später (davor NaN)."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start, periods=n_days, freq="D")
    t = np.arange(n_days)
    regime = np.where(np.sin(t / 140.0) > -0.25, 0.0015, -0.0030)           # Boom/Bust-Wechsel
    btc = 100 * np.exp(np.cumsum(regime + rng.normal(0, 0.03, n_days)))
    eth = 100 * np.exp(np.cumsum(regime + rng.normal(0, 0.04, n_days)))
    close = pd.DataFrame({BTC: btc, ETH: eth}, index=idx)
    close.iloc[:eth_offset, 1] = np.nan
    prev = close.shift(1).fillna(close)
    open_ = prev * (1 + rng.normal(0, 0.0005, (n_days, 2)))                 # Open t ~ Close t-1 (00:00 UTC)
    open_ = open_.where(close.notna())
    return Panel(open_, close)


def _const_panel(value=100.0, n_days=400, start="2014-09-17") -> Panel:
    idx = pd.date_range(start, periods=n_days, freq="D")
    close = pd.DataFrame({BTC: value, ETH: value}, index=idx)
    return Panel(close.copy(), close)


def _ref_share(prices: np.ndarray, lookbacks, t: int) -> float | None:
    """Referenzimplementierung (Schleife): Anteil der SMA-Regeln mit Close(t) > SMA_n(t); None ohne volle Historie."""
    if t + 1 < max(lookbacks) or np.isnan(prices[max(0, t + 1 - max(lookbacks)):t + 1]).any():
        return None
    hits = [prices[t] > prices[t + 1 - n:t + 1].mean() for n in lookbacks]
    return float(np.mean(hits))


def test_spec_contract():
    spec = strat.SPEC
    assert spec["id"] == "crypto_trend_ens_btc_eth"
    assert spec["family"] == "crypto"
    assert len(spec["variants"]) <= 3
    sig = inspect.signature(strat.weights)
    for name in list(spec["params"]) + [k for v in spec["variants"].values() for k in v]:
        assert name in sig.parameters, name
    assert spec["tickers"] == [BTC, ETH]
    assert spec["cost_bps"] == {BTC: 20.0, ETH: 20.0}
    assert spec["start"] == "2014-09-17"
    assert not any(t.startswith("^") for t in spec["tickers"])      # ^IRX ist kein handelbarer Preis


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_shape_and_range(variant):
    panel = _make_panel()
    params = {**strat.SPEC["params"], **VARIANTS[variant]}
    w = strat.weights(panel, **params)
    assert list(w.columns) == [BTC, ETH]
    assert len(w) > 1000
    assert w.notna().all().all()
    assert (w >= 0).all().all()                                   # kein Short
    per_asset_cap = 1.0 / len(params["assets"])
    assert (w.max() <= per_asset_cap + 1e-12).all()
    assert (w.sum(axis=1) <= 1.0 + 1e-12).all()                   # kein Hebel
    if variant == "base":
        # Vielfache von 0,5 * 1/4 = 0,125
        assert np.allclose(w.to_numpy() / 0.125, np.round(w.to_numpy() / 0.125))
        assert (w.sum(axis=1) > 0).any() and (w.sum(axis=1) < 1.0).any()
    else:
        assert set(np.unique(w[BTC])) <= {0.0, 1.0}
        assert (w[ETH] == 0.0).all()


def test_matches_reference_rule_base():
    panel = _make_panel()
    w = strat.weights(panel)
    lookbacks = (20, 50, 100, 200)
    px = {BTC: panel.close[BTC].to_numpy(), ETH: panel.close[ETH].to_numpy()}
    checked = 0
    for d in w.index[::7]:
        t = panel.close.index.get_loc(d)
        for a in (BTC, ETH):
            share = _ref_share(px[a], lookbacks, t)
            expected = 0.0 if share is None else 0.5 * share
            assert w.loc[d, a] == pytest.approx(expected, abs=1e-12), (d, a)
            checked += 1
    assert checked > 500


@pytest.mark.parametrize("variant,n", [("sma50_btc", 50), ("sma200_btc", 200)])
def test_matches_reference_rule_single_sma(variant, n):
    panel = _make_panel(seed=8)
    w = strat.weights(panel, **{**strat.SPEC["params"], **VARIANTS[variant]})
    p = panel.close[BTC].to_numpy()
    for d in w.index[::5]:
        t = panel.close.index.get_loc(d)
        expected = float(p[t] > p[t + 1 - n:t + 1].mean())
        assert w.loc[d, BTC] == expected
        assert w.loc[d, ETH] == 0.0


def test_strict_inequality_flat_prices_give_cash():
    w = strat.weights(_const_panel(), first_signal=None)
    assert len(w) > 0
    assert (w == 0.0).all().all()                                 # Close == SMA zählt nicht als "über"


def test_trend_response_up_down():
    n = 700
    idx = pd.date_range("2014-09-17", periods=n, freq="D")
    up = np.linspace(100, 400, n)
    close = pd.DataFrame({BTC: up, ETH: up}, index=idx)
    p_up = Panel(close.copy(), close)
    w = strat.weights(p_up, first_signal=None)
    assert (w.loc[idx[250]:] == 0.5).all().all()                  # alle vier Regeln melden "über" -> je 50 %
    close_dn = pd.DataFrame({BTC: up[::-1], ETH: up[::-1]}, index=idx)
    w2 = strat.weights(Panel(close_dn.copy(), close_dn), first_signal=None)
    assert (w2 == 0.0).all().all()                                # stetig fallend -> alles Cash


def test_partial_ensemble_share():
    """Kurzfristiger Einbruch nach langem Aufwärtstrend: nur SMA20 (und ggf. SMA50) kippen -> Teilgewicht."""
    n = 600
    idx = pd.date_range("2014-09-17", periods=n, freq="D")
    p = np.linspace(100, 300, n)
    p[-5:] = p[-6] * 0.93                                          # -7 % gegen Ende
    close = pd.DataFrame({BTC: p, ETH: p}, index=idx)
    w = strat.weights(Panel(close.copy(), close), first_signal=None)
    last = w.iloc[-1]
    share = _ref_share(p, (20, 50, 100, 200), n - 1)
    assert 0.0 < share < 1.0
    assert last[BTC] == pytest.approx(0.5 * share)
    assert last[ETH] == pytest.approx(0.5 * share)


def test_eth_zero_until_200_closes_and_never_on_nan_price():
    panel = _make_panel()
    w = strat.weights(panel)
    px = panel.close
    listing = px.index[ETH_LISTING_OFFSET]
    first_ready = px.index[ETH_LISTING_OFFSET + 199]               # 200. Close
    assert (w.loc[:first_ready - pd.Timedelta(days=1), ETH] == 0.0).all()
    assert (w.loc[first_ready:, ETH] > 0).any()
    assert w.loc[w.index < listing, ETH].eq(0.0).all()
    # nie ein Gewicht auf einem NaN-Preis
    for a in (BTC, ETH):
        nan_days = px.index[px[a].isna()].intersection(w.index)
        assert (w.loc[nan_days, a] == 0.0).all()
    assert w.notna().all().all()


def test_gap_in_prices_gives_zero_weight():
    panel = _make_panel()
    close = panel.close.copy()
    d = close.index[1800]
    close.loc[d, BTC] = np.nan
    p2 = Panel(panel.open.copy(), close)
    w = strat.weights(p2)
    assert w.loc[d, BTC] == 0.0
    # innerhalb der folgenden 199 Tage fehlt dem Fenster ein Wert -> weiter 0 (keine erfundene Historie)
    assert (w.loc[d:d + pd.Timedelta(days=198), BTC] == 0.0).all()
    assert w.notna().all().all()


def test_first_signal_start_date():
    panel = _make_panel()
    w = strat.weights(panel)
    assert w.index.min() == pd.Timestamp("2015-09-01")
    w_all = strat.weights(panel, first_signal=None)
    assert w_all.index.min() == panel.close.index.min()
    # Vorlauf wirkt: Gewichte ab Startdatum sind identisch zur Version ohne Startbeschränkung
    assert w.equals(w_all.loc["2015-09-01":])
    # der Index ist lückenlos (täglich, 7 Tage)
    assert (np.diff(w.index.values) == np.timedelta64(1, "D")).all()


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_causality_check(variant):
    panel = _make_panel(n_days=2600)
    params = {**strat.SPEC["params"], **VARIANTS[variant]}
    assert check_causality(lambda p: strat.weights(p, **params), panel) == []


def test_future_prices_do_not_change_past_weights():
    panel = _make_panel()
    base = strat.weights(panel)
    cut = panel.close.index[int(len(panel.close) * 0.6)]
    close = panel.close.copy()
    close.loc[close.index > cut] *= 0.01
    other = strat.weights(Panel((panel.open * 1.0).copy(), close))
    assert base.loc[:cut].equals(other.loc[:cut])


def test_only_close_prices_are_used():
    """Open-Kurse (auch die von t+1) dürfen das Signal nicht beeinflussen."""
    panel = _make_panel()
    w1 = strat.weights(panel)
    w2 = strat.weights(Panel(panel.open * 3.0, panel.close.copy()))
    assert w1.equals(w2)


def test_engine_integration_timing_exposure_costs():
    panel = _make_panel(n_days=2000)
    w = strat.weights(panel)
    rf = pd.Series(0.00005, index=panel.close.index)              # kein Netz: RF vorgeben
    cost = CostModel(per_ticker_bps=strat.SPEC["cost_bps"])
    res = run_backtest(panel, w, cost=cost, rf=rf)
    assert res.skipped_orders == 0
    assert (res.gross_exposure <= 1.0 + 1e-6).all()
    assert (res.weights >= -1e-9).all().all()
    assert np.isfinite(res.nav).all() and (res.nav > 0).all()
    # Signaltag: noch keine Position; Handel erst zur Eröffnung des Folgetags
    first = w.index[0]
    assert (res.weights.loc[:first] == 0.0).all().all()
    sig_days = w.index[w.sum(axis=1) > 0]
    s = sig_days[0]
    nxt = panel.close.index[panel.close.index.get_loc(s) + 1]
    assert res.weights.loc[s].abs().sum() == 0.0
    assert res.weights.loc[nxt].abs().sum() > 0.0
    # ETH vor der Notierung: nie Position
    assert (res.weights.loc[:panel.close.index[ETH_LISTING_OFFSET - 1], ETH] == 0.0).all()
    # Kosten fallen an, sind aber nicht absurd
    assert res.cost.sum() > 0
    assert res.cost.sum() < 0.5


def test_engine_stress_costs_are_higher():
    panel = _make_panel(n_days=1800)
    w = strat.weights(panel)
    rf = pd.Series(0.0, index=panel.close.index)
    c20 = run_backtest(panel, w, cost=CostModel(per_ticker_bps=strat.SPEC["cost_bps"]), rf=rf).cost.sum()
    c50 = run_backtest(panel, w, cost=CostModel(per_ticker_bps={k: v * 2.5 for k, v in strat.SPEC["cost_bps"].items()}),
                       rf=rf).cost.sum()
    assert c50 > 2.0 * c20 * 0.9
