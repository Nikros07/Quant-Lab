"""Tests fuer scripts/check_h14_placebo.py (H14, Placebo-Timing): nur synthetische Daten, kein Netz."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def _load(name: str):
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


h14 = _load("check_h14_placebo")
h12 = _load("check_h12_robust_basket")


def _random_close(n=1800, seed=1, mu=0.0003, sig=0.012) -> pd.Series:
    rng = np.random.default_rng(seed)
    r = rng.normal(mu, sig, n)
    return pd.Series(100.0 * np.cumprod(1.0 + r), index=pd.bdate_range("2000-01-03", periods=n))


def _market(seed=1, rf_level=0.00005):
    c = _random_close(seed=seed)
    rf = pd.Series(rf_level, index=c.index)
    st = h14.monthly_state(c)
    return c, rf, st, h14.make_plan(c, rf, st)


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_real_state_reproduces_sleeve2(seed):
    """Gleichheit mit base1x (sleeve2, MA12) fuer den echten Zustand: Rendite und Position."""
    c, rf, st, plan = _market(seed)
    R, P = h14.sleeve_from_states(plan, st.to_numpy()[None, :])
    ref = h12.sleeve2(c, rf, lengths=(12,), target=None)
    assert plan["index"].equals(ref.index)
    np.testing.assert_allclose(R[0], ref["ret"].to_numpy(), atol=1e-12)
    np.testing.assert_allclose(P[0], ref["pos"].to_numpy(), atol=1e-12)


def test_causality_future_prices_do_not_change_past_returns():
    """Kausalitaet: Kuerzt man die Kurse am Ende, aendern sich die frueheren Renditen bei gleichem Zustand nicht."""
    c, rf, st, plan = _market(4)
    R_full, _ = h14.sleeve_from_states(plan, st.to_numpy()[None, :])
    cut = len(c) - 150
    c2, rf2 = c.iloc[:cut], rf.iloc[:cut]
    st2 = h14.monthly_state(c2)
    plan2 = h14.make_plan(c2, rf2, st2)
    R_cut, _ = h14.sleeve_from_states(plan2, st2.to_numpy()[None, :])
    # Zustaende der gekuerzten Reihe sind ein Praefix der vollen (MA12 nutzt nur Vergangenheit)
    np.testing.assert_allclose(st.to_numpy()[:len(st2) - 1], st2.to_numpy()[:-1])
    # Rendite bis kurz vor der letzten Entscheidung der gekuerzten Reihe identisch
    n = len(R_cut[0]) - 25
    np.testing.assert_allclose(R_full[0][:n], R_cut[0][:n], atol=1e-12)


def test_all_on_and_all_off_states():
    """Immer an = Buy&Hold ab Tag m+2 minus einmalige Eintrittskosten; immer aus = nur Cash (keine Kosten)."""
    c, rf, st, plan = _market(5)
    M = plan["n_states"]
    R_on, P_on = h14.sleeve_from_states(plan, np.ones((1, M)))
    R_off, P_off = h14.sleeve_from_states(plan, np.zeros((1, M)))
    np.testing.assert_allclose(R_off[0], plan["rf"], atol=1e-15)
    assert P_off.max() == 0.0
    first = int(plan["dec_day"][0])
    assert P_on[0, :first].max() == 0.0 and P_on[0, first:].min() == 1.0
    exp = plan["r"].copy()
    exp[first] -= 10.0 / 1e4
    np.testing.assert_allclose(R_on[0, first:], exp[first:], atol=1e-15)


def test_cost_is_10bp_per_switch():
    """Ein einzelner Wechsel aus->an->aus kostet je Seite 10 bp (Delta pos = 1)."""
    c, rf, st, plan = _market(6)
    M = plan["n_states"]
    s = np.zeros((1, M))
    s[0, 10:12] = 1.0                                   # zwei Monate an
    R, P = h14.sleeve_from_states(plan, s)
    no_cost = P * plan["r"][None, :] + (1 - P) * plan["rf"][None, :]
    total_cost = float((no_cost - R).sum())
    assert total_cost == pytest.approx(2 * 10.0 / 1e4, abs=1e-12)


def test_transition_estimation_counts():
    """Uebergaenge werden als relative Haeufigkeiten aus dem Zustandsverlauf geschaetzt."""
    s = np.array([1, 1, 0, 0, 0, 1, 0, 1, 1, 1], float)
    # Paare: 11 11->? (1->1,1->0,0->0,0->0,0->1,1->0,0->1,1->1,1->1)
    p_oo, p_no = h14.estimate_transitions(s)
    assert p_oo == pytest.approx(2 / 5)                 # aus 5 Paaren mit Start 1: zwei 1->0
    assert p_no == pytest.approx(2 / 4)                 # aus 4 Paaren mit Start 0: zwei 0->1
    assert h14.estimate_transitions(np.ones(6)) == (0.0, 0.0)


def test_chain_matches_market_time_and_switch_rate_on_average():
    """Die Placebo-Kette trifft im Mittel Marktzeit (stationaer) und Wechselhaeufigkeit des echten Zustands."""
    p_oo, p_no = 0.2, 0.3
    K, M = 4000, 300
    U = np.random.default_rng(0).random((K, M))
    S = h14.simulate_chain(U, p_oo, p_no, 1.0)
    assert S.mean() == pytest.approx(p_no / (p_oo + p_no), abs=0.01)
    sw = (np.diff(S, axis=1) != 0).mean()
    pi_on = p_no / (p_oo + p_no)
    assert sw == pytest.approx(pi_on * p_oo + (1 - pi_on) * p_no, abs=0.01)


def test_chain_degenerate_keeps_state():
    """Ohne beobachtete Wechsel bleibt die Kette im echten Anfangszustand."""
    U = np.random.default_rng(1).random((5, 40))
    assert h14.simulate_chain(U, 0.0, 0.0, 1.0).min() == 1.0
    assert h14.simulate_chain(U, 0.0, 0.0, 0.0).max() == 0.0


def test_seeds_are_reproducible_and_distinct():
    a = h14.draw_uniforms(np.array([0, 1]), 3, 20)
    b = h14.draw_uniforms(np.array([0, 1]), 3, 20)
    c = h14.draw_uniforms(np.array([0, 1]), 4, 20)
    np.testing.assert_array_equal(a, b)
    assert not np.allclose(a, c) and not np.allclose(a[0], a[1])


def test_fast_metrics_equal_konstanz():
    """Vektorisierte Kennzahlen = h12.konstanz (CAGR, MaxDD, Ulcer, UPI, Sharpe)."""
    c, rf, st, plan = _market(7)
    R, _ = h14.sleeve_from_states(plan, st.to_numpy()[None, :])
    ser = pd.Series(R[0], index=plan["index"])
    rfs = pd.Series(plan["rf"], index=plan["index"])
    ref = h12.konstanz(ser, rfs)
    f = h14.fast_metrics(R, plan["rf"], plan["index"])
    for k in ("cagr", "max_dd", "ulcer", "upi", "sharpe"):
        assert f[k][0] == pytest.approx(ref[k], rel=1e-9, abs=1e-12)


def test_basket_equals_tp_basket_and_placebo_runs():
    """Korb aus der schnellen Funktion = tp.basket; Mini-Placebo laeuft und liefert endliche Kennzahlen."""
    import check_trend_portfolio as tp
    mk = []
    for k, seed in enumerate([11, 12, 13]):
        c, rf, st, plan = _market(seed)
        mk.append({"t": f"S{k}", "no": k, "close": c, "rf": rf, "state": st.to_numpy(float), "plan": plan})
    rets = [(m["plan"]["index"], h14.sleeve_from_states(m["plan"], m["state"][None, :])[0]) for m in mk]
    ix, B = h14.basket_from_sleeves(rets, min_markets=2)
    ref = tp.basket(pd.DataFrame({m["t"]: h12.sleeve2(m["close"], m["rf"])["ret"] for m in mk}), 2)[0]
    assert ix.equals(ref.index)
    np.testing.assert_allclose(B[0], ref.to_numpy(), atol=1e-12)


def test_verdict_logic():
    pu = np.linspace(0.0, 1.0, 1001)
    pd_ = np.linspace(-0.5, -0.1, 1001)
    ok = h14.verdict(0.96, -0.15, pu, pd_)
    assert ok["bestanden"] and ok["ok_upi"] and ok["ok_dd"]
    assert not h14.verdict(0.90, -0.15, pu, pd_)["bestanden"]       # UPI zu niedrig
    assert not h14.verdict(0.96, -0.35, pu, pd_)["bestanden"]       # MaxDD zu tief (75. Perz. = -0.20)
    q = float(np.percentile(pu, 95))
    assert h14.verdict(q, -0.15, pu, pd_)["ok_upi"]                 # Grenze: >= zaehlt
