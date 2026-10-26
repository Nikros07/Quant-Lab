"""Steuermodell gegen Handrechnung (deterministische Preise, keine Kosten, kein Zins)."""
import numpy as np
import pandas as pd
import pytest

from qlab.data import Panel
from qlab.engine import CostModel, TaxModel, run_backtest

ZERO = CostModel(default_bps=0.0, short_fee_annual=0.0, lever_spread_annual=0.0)


def panel_from_path(prices, start="2020-06-01", name="A"):
    idx = pd.bdate_range(start, periods=len(prices))
    px = pd.DataFrame({name: np.asarray(prices, float)}, index=idx)
    return Panel(px.copy(), px)       # open == close: Gewinn fällt über Nacht, Handel zum Folgetag-Kurs


def rf0(p):
    return pd.Series(0.0, index=p.close.index)


def path(n_flat1, price1, n_up, price2, n_end):
    return [price1] * n_flat1 + [price2] * n_up + [price2] * n_end


def test_round_trip_gain_taxed_at_year_end_no_tf():
    # Kauf bei 100, Verkauf bei 200 im selben Jahr, Jahresende danach
    prices = [100] * 5 + [200] * 400
    p = panel_from_path(prices)
    idx = p.close.index
    tgt = pd.DataFrame({"A": [1.0, 0.0]}, index=[idx[0], idx[40]])
    tax = TaxModel(tf_map={"A": 0.0})
    r = run_backtest(p, tgt, cost=ZERO, rf=rf0(p), tax=tax)
    # Gewinn 1.0 -> Steuer 0.26375 -> End-NAV 2 - 0.26375
    assert r.nav.iloc[-1] == pytest.approx(2.0 - 0.26375, rel=1e-9)
    assert r.taxes_paid.sum() == pytest.approx(0.26375, rel=1e-9)


def test_teilfreistellung_reduces_tax():
    prices = [100] * 5 + [200] * 400
    p = panel_from_path(prices)
    idx = p.close.index
    tgt = pd.DataFrame({"A": [1.0, 0.0]}, index=[idx[0], idx[40]])
    r = run_backtest(p, tgt, cost=ZERO, rf=rf0(p), tax=TaxModel(tf_map={"A": 0.30}))
    assert r.taxes_paid.sum() == pytest.approx(0.26375 * 0.7 * 1.0, rel=1e-9)


def test_buy_and_hold_defers_tax_but_liquidation_figure_matches():
    prices = [100] * 5 + [200] * 400
    p = panel_from_path(prices)
    tgt = pd.DataFrame({"A": [1.0]}, index=[p.close.index[0]])
    r = run_backtest(p, tgt, cost=ZERO, rf=rf0(p), tax=TaxModel(tf_map={"A": 0.0}))
    assert r.taxes_paid.sum() == 0.0
    assert r.nav.iloc[-1] == pytest.approx(2.0, rel=1e-9)
    assert r.tax_if_liquidated == pytest.approx(0.26375, rel=1e-9)
    after = (1 + r.ret_after_liquidation_tax()).prod()
    assert after == pytest.approx(2.0 - 0.26375, rel=1e-9)


def test_loss_carryforward_offsets_next_year_gain():
    # Jahr 1: Kauf 100 -> Verkauf 50 (Verlust 0.5), Jahr 2: Kauf 50 -> Verkauf 100 (Gewinn ~ NAV-abhängig)
    n = 700
    idx = pd.bdate_range("2020-06-01", periods=n)
    px = np.full(n, 100.0)
    px[10:] = 50.0                 # Absturz im ersten Jahr
    px[400:] = 100.0               # Erholung im zweiten Jahr
    p = Panel(pd.DataFrame({"A": px}, index=idx).copy(), pd.DataFrame({"A": px}, index=idx))
    tgt = pd.DataFrame({"A": [1.0, 0.0, 1.0, 0.0]}, index=[idx[0], idx[20], idx[200], idx[500]])
    # Tag 20: Verkauf bei 50 (nach Kauf bei 100) -> Verlust 0.5 (NAV 1 -> 0.5)
    # Tag 200: Kauf bei 50 mit 0.5 NAV; Tag 500: Verkauf bei 100 -> Gewinn 0.5
    # Erstes Jahr endet vor Tag 200 (2020-12-31), Verlust 0.5 wird vorgetragen
    # Zweites Jahr: Gewinn 0.5 - Vortrag 0.5 = 0 -> keine Steuer
    r = run_backtest(p, tgt, cost=ZERO, rf=rf0(p), tax=TaxModel(tf_map={"A": 0.0}))
    assert r.taxes_paid.sum() == pytest.approx(0.0, abs=1e-9)
    assert r.nav.iloc[-1] == pytest.approx(1.0, rel=1e-9)


def test_short_gain_is_taxable():
    # Short bei 100 -> Eindeckung bei 50: Gewinn 0.5 des NAV (Short mit Gewicht -1)
    prices = [100] * 5 + [50] * 400
    p = panel_from_path(prices)
    idx = p.close.index
    tgt = pd.DataFrame({"A": [-1.0, 0.0]}, index=[idx[0], idx[40]])
    r = run_backtest(p, tgt, cost=ZERO, rf=rf0(p), tax=TaxModel(tf_map={"A": 0.0}))
    assert r.taxes_paid.sum() == pytest.approx(0.26375 * 0.5, rel=1e-6)


def test_tax_none_is_identical_to_before():
    prices = [100] * 5 + [200] * 400
    p = panel_from_path(prices)
    tgt = pd.DataFrame({"A": [1.0]}, index=[p.close.index[0]])
    a = run_backtest(p, tgt, cost=ZERO, rf=rf0(p))
    b = run_backtest(p, tgt, cost=ZERO, rf=rf0(p), tax=None)
    pd.testing.assert_series_equal(a.nav, b.nav)
    assert a.taxes_paid is None
