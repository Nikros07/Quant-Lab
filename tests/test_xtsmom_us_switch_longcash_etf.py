"""Tests für strategies/xtsmom_us_switch_longcash_etf.py — nur synthetische Daten, kein Netz, kein Datencache.

Bekannte Antworten: Monatsstufen-Panels (Preise und ^IRX innerhalb eines Kalendermonats konstant) mit einer
unabhängig geschriebenen Referenz (reine Python-Schleifen); der Kern `switch_weights` selbst wird im Test des
Hauptmoduls geprüft, hier geht es um die ETF-Fassung mit SHY als Cash-Titel.
"""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import NYSE_BDAY, month_end_flags
from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import xtsmom_us_switch_longcash as MAIN
from strategies import xtsmom_us_switch_longcash_etf as E

EQ, BD, CASH, LB, RT = E.EQ, E.BOND, E.CASH, E.LONGBOND, E.RATE
COLS = [EQ, BD, CASH, LB, RT]
VARIANTS = {"base": {}, **E.SPEC["variants"]}
EQ_W, BD_W, CASH_W = 0, 1, 2


# --------------------------------------------------------------------------------------
# Hilfen
# --------------------------------------------------------------------------------------

def nyse_index(n, start="2004-01-02"):
    return pd.date_range(start, periods=n, freq=NYSE_BDAY)


def random_panel(n=3200, seed=5, start="2004-01-02", gaps=True) -> Panel:
    """Tagespreise mit wechselnden Regimen; Open != Close (Overnight-Lücken), ^IRX in Prozent."""
    rng = np.random.default_rng(seed)
    idx = nyse_index(n, start)
    t = np.arange(n)
    eq_r = np.where(np.sin(t / 110.0) > -0.2, 0.0007, -0.0014) + rng.normal(0.0, 0.01, n)
    bd_r = np.where(np.sin(t / 170.0 + 1.0) > -0.3, 0.0004, -0.0009) + rng.normal(0.0, 0.004, n)
    lb_r = 1.5 * bd_r + rng.normal(0.0, 0.003, n)
    sh_r = 0.0001 + rng.normal(0.0, 0.0005, n)
    irx = 2.5 + 1.5 * np.sin(2 * np.pi * t / 900.0)
    close = pd.DataFrame({EQ: 100 * np.exp(np.cumsum(eq_r)), BD: 100 * np.exp(np.cumsum(bd_r)),
                          CASH: 100 * np.exp(np.cumsum(sh_r)), LB: 100 * np.exp(np.cumsum(lb_r)), RT: irx}, index=idx)
    open_ = close.copy()
    if gaps:
        gap = np.exp(rng.normal(0.0, 0.002, (n, 4)))
        open_[[EQ, BD, CASH, LB]] = close[[EQ, BD, CASH, LB]].shift(1).fillna(100.0).to_numpy() * gap
    return Panel(open_, close)


def step_panel(eq, bd, irx, start="2001-01-02"):
    eq = np.asarray(eq, float)
    n = len(eq)
    s = pd.Timestamp(start)
    idx = pd.date_range(s, s + pd.offsets.MonthEnd(n), freq=NYSE_BDAY)
    month_no = np.minimum(((idx.year * 12 + idx.month) - (s.year * 12 + s.month)).to_numpy(), n - 1)
    bd = np.asarray(bd, float)
    irx = np.broadcast_to(np.asarray(irx, float), (n,)).copy()
    sh = 100.0 * (1.0 + 0.001) ** np.arange(n)
    close = pd.DataFrame({EQ: eq[month_no], BD: bd[month_no], CASH: sh[month_no], LB: bd[month_no], RT: irx[month_no]},
                         index=idx)
    me = pd.DatetimeIndex(pd.Series(idx, index=idx).groupby(month_no).last().to_numpy())
    return Panel(close.copy(), close), idx, me


def reference_states(eq, bd, irx, lookback=12, skip=0) -> dict[int, int]:
    out = {}
    for m in range(lookback, len(eq)):
        growth = 1.0
        for j in range(m - lookback + 1, m - skip + 1):
            growth *= 1.0 + irx[j - 1] / 100.0 / 12.0
        rf = growth - 1.0
        rE = eq[m - skip] / eq[m - lookback] - 1.0 - rf
        rB = bd[m - skip] / bd[m - lookback] - 1.0 - rf
        out[m] = EQ_W if (rB > 0 and rE > 0) else (BD_W if rB > 0 else CASH_W)
    return out


def changes_only(states):
    out, last = [], None
    for m in sorted(states):
        if states[m] != last:
            out.append((m, states[m]))
            last = states[m]
    return out


def regime_paths(n_months=132, seed=2):
    rng = np.random.default_rng(seed)
    m = np.arange(n_months)
    eq_r = np.where(np.sin(m / 9.0) > -0.2, 0.012, -0.02) + rng.normal(0, 0.03, n_months)
    bd_r = np.where(np.sin(m / 14.0 + 1.0) > -0.3, 0.005, -0.008) + rng.normal(0, 0.012, n_months)
    irx = 2.5 + 2.0 * np.sin(m / 20.0)
    return 100 * np.exp(np.cumsum(eq_r)), 100 * np.exp(np.cumsum(bd_r)), irx


def first_state(eq, bd, irx, **kw):
    panel, _, me = step_panel(eq, bd, irx)
    w = E.weights(panel, **kw)
    assert len(w) == 1 and w.index[0] == me[12]
    return w.iloc[0].to_numpy().tolist()


# --------------------------------------------------------------------------------------
# Vertrag / Form
# --------------------------------------------------------------------------------------

def test_spec_contract():
    spec = E.SPEC
    assert spec["id"] == "xtsmom_us_switch_longcash_etf"
    assert spec["id"] != MAIN.SPEC["id"]
    assert len(spec["variants"]) <= 3
    sig = inspect.signature(E.weights)
    for name in list(spec["params"]) + [k for v in spec["variants"].values() for k in v]:
        assert name in sig.parameters, name
    assert set(spec["cost_bps"]) == {EQ, BD, CASH, LB} and all(v == 2.0 for v in spec["cost_bps"].values())
    assert spec["params"] == {"equity": "SPY", "bond": "IEF", "cash": "SHY", "rate": "^IRX", "lookback": 12, "skip": 0}
    assert spec["variants"] == {"skip1": {"skip": 1}, "tlt": {"bond": "TLT"}}
    assert RT in spec["tickers"] and hasattr(E, "load")


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_shape_and_range(variant):
    panel = random_panel()
    params = {**E.SPEC["params"], **VARIANTS[variant]}
    w = E.weights(panel, **params)
    assert list(w.columns) == [params["equity"], params["bond"], CASH]
    assert RT not in w.columns
    assert len(w) > 8 and w.notna().all().all()
    assert set(np.unique(w.to_numpy())) <= {0.0, 1.0}
    assert np.allclose(w.sum(axis=1), 1.0)                       # immer 100 % in genau einem ETF (kein Hebel, kein Short)
    flags = month_end_flags(panel.close.index)
    assert w.index.isin(flags.index[flags.to_numpy()]).all()
    assert w.index.is_monotonic_increasing and not w.index.has_duplicates
    assert (w.diff().abs().sum(axis=1).iloc[1:] > 0).all()       # nur Zustandswechsel
    assert {tuple(r) for r in w.to_numpy()} == {(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)}


# --------------------------------------------------------------------------------------
# Regel
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant,kw", [("base", dict(lookback=12, skip=0)), ("skip1", dict(lookback=12, skip=1))])
def test_matches_reference_rule(variant, kw):
    eq, bd, irx = regime_paths()
    panel, _, me = step_panel(eq, bd, irx)
    w = E.weights(panel, **{**E.SPEC["params"], **VARIANTS[variant]})
    ref = reference_states(eq, bd, irx, **kw)
    assert set(ref.values()) == {EQ_W, BD_W, CASH_W}
    exp = changes_only(ref)
    assert list(w.index) == [me[m] for m, _ in exp]
    assert np.allclose(w.to_numpy(), np.array([[1.0 if i == s else 0.0 for i in range(3)] for _, s in exp]))


def test_known_states():
    up, down, flat = np.linspace(100, 120, 13), np.linspace(100, 90, 13), np.full(13, 100.0)
    assert first_state(up, np.linspace(100, 110, 13), 2.0) == [1.0, 0.0, 0.0]        # SPY
    assert first_state(down, np.linspace(100, 110, 13), 2.0) == [0.0, 1.0, 0.0]      # IEF
    assert first_state(up, np.linspace(100, 97, 13), 2.0) == [0.0, 0.0, 1.0]         # SHY (Anleihe verliert)
    assert first_state(up, flat, 2.0) == [0.0, 0.0, 1.0]                              # Anleihe flach < Bills -> SHY
    assert first_state(flat, flat, 0.0) == [0.0, 0.0, 1.0]                            # strikt > 0
    assert first_state(flat, np.linspace(100, 110, 13), 0.0) == [0.0, 1.0, 0.0]


def test_tlt_variant_swaps_bond_leg():
    eq, bd, irx = regime_paths()
    panel, _, me = step_panel(eq, bd, irx)
    close = panel.close.copy()
    close[LB] = 100 * np.exp(np.cumsum(np.random.default_rng(9).normal(0.0, 0.002, len(close))))
    p2 = Panel(close.copy(), close)
    w = E.weights(p2, bond=LB)
    assert list(w.columns) == [EQ, LB, CASH]
    ref = changes_only(reference_states(eq, close[LB].groupby((close.index.year * 12 + close.index.month)).last().to_numpy(), irx))
    assert list(w.index) == [me[m] for m, _ in ref]


def test_same_signal_as_main_module_cash_is_shy():
    """ETF-Fassung = Hauptmodul-Fassung, nur dass die Nullzeile (Cash) hier ein Gewicht 1 auf SHY ist."""
    panel = random_panel()
    w_etf = E.weights(panel)
    w_main = MAIN.weights(panel)
    assert list(w_etf.index) == list(w_main.index)
    expected = w_main.copy()
    expected[CASH] = (w_main.sum(axis=1) == 0).astype(float)
    assert np.array_equal(w_etf.to_numpy(), expected[[EQ, BD, CASH]].to_numpy())


# --------------------------------------------------------------------------------------
# Fehlende Preise (NaN = nicht handelbar)
# --------------------------------------------------------------------------------------

def test_no_weights_on_nan_prices():
    eq, bd, irx = regime_paths(n_months=60)
    panel, idx, me = step_panel(eq, bd, irx)
    ref = changes_only(reference_states(eq, bd, irx))
    cash_month = next(m for m, s in ref if s == CASH_W)
    # SHY am Signaltag ohne Kurs -> in diesem Monat kein Gewicht
    close = panel.close.copy()
    close.loc[me[cash_month], CASH] = np.nan
    w = E.weights(Panel(close.copy(), close))
    assert me[cash_month] not in w.index
    for d, row in w.iterrows():
        for t in (EQ, BD, CASH):
            assert row[t] == 0.0 or np.isfinite(close.loc[d, t])
    # ETFs noch nicht gelistet (Anleihe/Cash starten Mitte Monat 2): erstes Signal erst 12 Monatsenden nach dem ersten Kurs
    close = panel.close.copy()
    cut = idx[idx <= me[2]][-10]
    close.loc[:cut, [BD, CASH, LB]] = np.nan
    w = E.weights(Panel(close.copy(), close))
    assert len(w) > 0 and w.index.min() >= me[2 + 12]
    assert close.loc[w.index[w[CASH] > 0], CASH].notna().all()


# --------------------------------------------------------------------------------------
# Kausalität
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_causality_check(variant):
    panel = random_panel()
    params = {**E.SPEC["params"], **VARIANTS[variant]}
    assert check_causality(lambda p: E.weights(p, **params), panel) == []


def test_future_prices_do_not_change_past_weights():
    panel = random_panel()
    base = E.weights(panel)
    cut = panel.close.index[int(len(panel.close) * 0.6)]
    close = panel.close.copy()
    after = close.index > cut
    close.loc[after, [EQ, BD, LB]] *= 0.01
    close.loc[after, RT] = 25.0
    other = E.weights(Panel(close.copy(), close))
    assert base.loc[:cut].equals(other.loc[:cut])


def test_last_data_day_mid_month_is_not_month_end():
    panel = random_panel(n=1600)
    idx = panel.close.index
    mid = idx[idx >= pd.Timestamp("2008-06-10")][0]
    w = E.weights(panel.truncate(mid))
    assert w.index.max() < pd.Timestamp("2008-06-01")
    assert E.weights(panel).index.max() > mid


# --------------------------------------------------------------------------------------
# Engine-Integration (Ausführung zur Eröffnung t+1, Exposure)
# --------------------------------------------------------------------------------------

def test_engine_integration_open_execution_and_exposure():
    panel = random_panel()
    w = E.weights(panel)
    res = run_backtest(panel, w, cost=CostModel(per_ticker_bps={t: 2.0 for t in (EQ, BD, CASH, LB)}))
    first = w.index[0]
    after = res.gross_exposure.loc[first:].iloc[1:]
    assert (after <= 1.0 + 1e-3).all()
    assert (after > 0.97).all()                                    # nach dem ersten Signal immer (fast) voll in einem ETF
    assert (res.weights[[LB, RT]].abs() <= 1e-12).all().all()      # Basis: kein Gewicht auf TLT, nie auf ^IRX
    # Position erst nach dem Signaltag (Handel zur Eröffnung von t+1)
    s = w.index[0]
    col = w.loc[s].idxmax()
    assert res.weights.loc[s, col] < 1e-9
    nxt = panel.close.index[panel.close.index.get_loc(s) + 1]
    assert res.weights.loc[nxt, col] > 0.95
    # Umsatz nur am Tag nach einem Wechsel
    pos = panel.close.index.get_indexer(w.index) + 1
    exec_days = panel.close.index[pos[pos < len(panel.close.index)]]
    assert (res.turnover.drop(exec_days) <= 1e-9).all()
    assert (res.turnover.loc[exec_days[1:]] > 0.45).all()          # Wechsel zwischen zwei ETFs: Umschichtung des ganzen Portfolios


# --------------------------------------------------------------------------------------
# load() ohne Netz: Datenbeschaffung wird ersetzt
# --------------------------------------------------------------------------------------

def test_load_drops_rate_only_days_and_starts_2002_07(monkeypatch):
    idx = pd.bdate_range("2002-05-01", periods=130)
    close = pd.DataFrame({EQ: np.linspace(80, 90, 130), BD: np.nan, CASH: np.nan, LB: np.nan, RT: 1.7}, index=idx)
    close.loc["2002-07-30":, [BD, CASH, LB]] = 100.0
    only_rate = idx[75]                                              # Tag, an dem kein ETF einen Kurs hat
    close.loc[only_rate, [EQ, BD, CASH, LB]] = np.nan
    fake = Panel(close.copy(), close.copy())
    monkeypatch.setattr(E, "load_panel", lambda tickers: fake)
    p = E.load()
    assert p.close.index.min() >= pd.Timestamp(E.PANEL_START)
    assert only_rate not in p.close.index and only_rate not in p.open.index
    assert list(p.close.columns) == [EQ, BD, CASH, LB, RT]
    assert p.open.index.equals(p.close.index)
