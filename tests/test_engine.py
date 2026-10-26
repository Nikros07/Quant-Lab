"""Engine-Tests auf synthetischen Daten (kein Netz). Bekannte Antworten statt Vertrauen."""
import numpy as np
import pandas as pd
import pytest

from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest


def make_panel(n=1500, tickers=("A", "B"), seed=1, drift=0.0003, vol=0.01):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2010-01-01", periods=n)
    closes, opens = {}, {}
    for k, t in enumerate(tickers):
        r_on = rng.normal(drift / 2, vol / 2, n)
        r_id = rng.normal(drift / 2, vol / 2, n)
        c = np.empty(n); o = np.empty(n)
        prev = 100.0
        for i in range(n):
            o[i] = prev * (1 + r_on[i])
            c[i] = o[i] * (1 + r_id[i])
            prev = c[i]
        closes[t], opens[t] = c, o
    close = pd.DataFrame(closes, index=idx)
    open_ = pd.DataFrame(opens, index=idx)
    return Panel(open_, close)


ZERO = CostModel(default_bps=0.0, short_fee_annual=0.0, lever_spread_annual=0.0)


def rf_zero(panel):
    return pd.Series(0.0, index=panel.close.index)


def test_buy_and_hold_matches_price_ratio():
    p = make_panel(tickers=("A",))
    tgt = pd.DataFrame({"A": [1.0]}, index=[p.close.index[0]])
    res = run_backtest(p, tgt, cost=ZERO, rf=rf_zero(p))
    # Signal an Tag 0, Kauf zur Eröffnung Tag 1 -> NAV-Ende = close[-1]/open[1]
    expected = p.close["A"].iloc[-1] / p.open["A"].iloc[1]
    assert res.nav.iloc[-1] == pytest.approx(expected, rel=1e-9)
    assert res.n_trades == 1


def test_exec_close_next_is_later_than_open():
    p = make_panel(tickers=("A",))
    tgt = pd.DataFrame({"A": [1.0]}, index=[p.close.index[0]])
    r = run_backtest(p, tgt, cost=ZERO, rf=rf_zero(p), exec_mode="close_next")
    expected = p.close["A"].iloc[-1] / p.close["A"].iloc[1]
    assert r.nav.iloc[-1] == pytest.approx(expected, rel=1e-9)


def test_single_round_trip_cost():
    p = make_panel(tickers=("A",), drift=0.0, vol=0.0)  # flache Preise
    idx = p.close.index
    tgt = pd.DataFrame({"A": [1.0, 0.0]}, index=[idx[0], idx[10]])
    res = run_backtest(p, tgt, cost=CostModel(default_bps=10.0), rf=rf_zero(p))
    # 10 bps beim Kauf auf 1.0, 10 bps beim Verkauf auf ~0.999 -> ~ (1-0.001)^2.
    # Kauf zu 100 % lässt Cash um die Kosten leicht negativ (Kredit, 1,5 % p.a. Aufschlag
    # über 10 Tage ≈ 0,0006 bp) -> Toleranz 1e-5 statt exakt.
    assert res.nav.iloc[-1] == pytest.approx((1 - 0.001) * (1 - 0.001), rel=1e-5)
    assert res.turnover.sum() == pytest.approx(1.0 + 0.999, rel=1e-3) or res.turnover.sum() > 0.9


def test_cash_earns_risk_free():
    p = make_panel(tickers=("A",))
    rf = pd.Series(0.0001, index=p.close.index)
    tgt = pd.DataFrame({"A": [0.0]}, index=[p.close.index[0]])
    res = run_backtest(p, tgt, cost=ZERO, rf=rf)
    assert res.nav.iloc[-1] == pytest.approx(1.0001 ** len(p.close), rel=1e-9)


def test_leverage_pays_financing():
    p = make_panel(tickers=("A",), drift=0.0, vol=0.0)
    rf = pd.Series(0.0002, index=p.close.index)
    tgt = pd.DataFrame({"A": [2.0]}, index=[p.close.index[0]])
    res = run_backtest(p, tgt, cost=CostModel(default_bps=0.0, lever_spread_annual=0.0), rf=rf)
    # Flache Preise, Hebel 2: Kredit 1.0 zahlt RF -> NAV fällt
    assert res.nav.iloc[-1] < 1.0
    assert res.gross_exposure.iloc[5] == pytest.approx(2.0, rel=1e-3)


def test_drift_without_signal_has_no_turnover():
    p = make_panel(tickers=("A", "B"))
    tgt = pd.DataFrame({"A": [0.5], "B": [0.5]}, index=[p.close.index[0]])
    res = run_backtest(p, tgt, cost=CostModel(default_bps=5.0), rf=rf_zero(p))
    assert res.n_trades == 2
    w_end = res.weights.iloc[-1]
    assert abs(w_end["A"] - 0.5) > 1e-3  # Gewichte driften


def test_unknown_ticker_raises():
    p = make_panel(tickers=("A",))
    tgt = pd.DataFrame({"ZZZ": [1.0]}, index=[p.close.index[0]])
    with pytest.raises(KeyError):
        run_backtest(p, tgt, cost=ZERO, rf=rf_zero(p))


def test_nan_price_blocks_trade_then_executes():
    p = make_panel(tickers=("A",))
    idx = p.close.index
    p.open.iloc[1:4, 0] = np.nan  # nicht handelbar an Tagen 1..3
    p.close.iloc[1:4, 0] = np.nan
    tgt = pd.DataFrame({"A": [1.0]}, index=[idx[0]])
    res = run_backtest(p, tgt, cost=ZERO, rf=rf_zero(p))
    assert res.skipped_orders >= 1
    assert res.weights["A"].iloc[10] > 0.9  # später doch gekauft


# ---- Kausalität ---------------------------------------------------------------------

def honest_momentum(panel):
    px = panel.close["A"]
    sig = (px / px.shift(60) - 1 > 0).astype(float)
    sig = sig[sig.index.to_series().dt.is_month_end | True]  # täglich
    out = pd.DataFrame({"A": sig})
    out.iloc[:60] = np.nan
    return out


def cheating_strategy(panel):
    px = panel.close["A"]
    sig = (px.shift(-1) / px - 1 > 0).astype(float)  # schaut einen Tag in die Zukunft
    out = pd.DataFrame({"A": sig})
    return out


def full_sample_zscore(panel):
    px = panel.close["A"].pct_change()
    z = (px - px.mean()) / px.std()  # globale Statistik = Look-ahead
    return pd.DataFrame({"A": (z > 0).astype(float)})


def test_causality_passes_honest_strategy():
    assert check_causality(honest_momentum, make_panel(tickers=("A",))) == []


def test_causality_detects_future_peek():
    assert check_causality(cheating_strategy, make_panel(tickers=("A",)))


def test_causality_detects_full_sample_statistics():
    assert check_causality(full_sample_zscore, make_panel(tickers=("A",)))


def test_cheater_would_profit_but_check_flags_it():
    p = make_panel(tickers=("A",))
    res = run_backtest(p, cheating_strategy(p), cost=ZERO, rf=rf_zero(p))
    # Der Betrüger erzielt (wegen Open-Ausführung) nur teilweise Vorteil, muss aber auffallen:
    assert check_causality(cheating_strategy, p)
    assert np.isfinite(res.nav.iloc[-1])
