"""Tests für strategies/xtsmom_us_switch_longcash.py — nur synthetische Daten, kein Netz, kein Datencache.

Bekannte Antworten: Monatsstufen-Panels (Preise und ^IRX innerhalb eines Kalendermonats konstant), bei denen das
Monatsend-Signal exakt von Hand bzw. von einer unabhängig geschriebenen Referenz (reine Python-Schleifen) bekannt ist.
"""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import NYSE_BDAY, month_end_flags
from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import xtsmom_us_switch_longcash as S

EQ, BD, LB, RT = S.EQ, S.BOND, S.LONGBOND, S.RATE
COLS = [EQ, BD, LB, RT]
VARIANTS = {"base": {}, **S.SPEC["variants"]}
EQ_W, BD_W, CASH_W = 0, 1, 2              # Zustands-Codes der Referenz


# --------------------------------------------------------------------------------------
# Hilfen
# --------------------------------------------------------------------------------------

def nyse_index(n, start="2004-01-02"):
    return pd.date_range(start, periods=n, freq=NYSE_BDAY)


def random_panel(n=3200, seed=5, start="2004-01-02") -> Panel:
    """Tagespreise mit wechselnden Regimen für Aktien und Anleihe (alle drei Zustände kommen vor), ^IRX in Prozent."""
    rng = np.random.default_rng(seed)
    idx = nyse_index(n, start)
    t = np.arange(n)
    eq_r = np.where(np.sin(t / 110.0) > -0.2, 0.0007, -0.0014) + rng.normal(0.0, 0.01, n)
    bd_r = np.where(np.sin(t / 170.0 + 1.0) > -0.3, 0.0004, -0.0009) + rng.normal(0.0, 0.004, n)
    lb_r = 1.5 * bd_r + rng.normal(0.0, 0.003, n)
    irx = 2.5 + 1.5 * np.sin(2 * np.pi * t / 900.0)
    close = pd.DataFrame({EQ: 100 * np.exp(np.cumsum(eq_r)), BD: 100 * np.exp(np.cumsum(bd_r)),
                          LB: 100 * np.exp(np.cumsum(lb_r)), RT: irx}, index=idx)
    return Panel(close.copy(), close)


def step_panel(eq, bd, irx, lb=None, start="2001-01-02") -> tuple[Panel, pd.DatetimeIndex, pd.DatetimeIndex]:
    """Panel mit NYSE-Handelstagen, Preise/^IRX innerhalb jedes Kalendermonats konstant (= Monatswert).

    Gibt (Panel, Index, Monatsend-Daten) zurück; die Monatsenden kommen aus einem Test-Orakel (volle Monate).
    """
    eq = np.asarray(eq, float)
    n = len(eq)
    s = pd.Timestamp(start)
    idx = pd.date_range(s, s + pd.offsets.MonthEnd(n), freq=NYSE_BDAY)
    month_no = ((idx.year * 12 + idx.month) - (s.year * 12 + s.month)).to_numpy()
    month_no = np.minimum(month_no, n - 1)
    bd = np.asarray(bd, float)
    irx = np.broadcast_to(np.asarray(irx, float), (n,)).copy()
    lb = np.asarray(lb if lb is not None else bd, float)
    close = pd.DataFrame({EQ: eq[month_no], BD: bd[month_no], LB: lb[month_no], RT: irx[month_no]}, index=idx)
    me = pd.DatetimeIndex(pd.Series(idx, index=idx).groupby(month_no).last().to_numpy())
    return Panel(close.copy(), close), idx, me


def reference_states(eq, bd, irx, lookback=12, skip=0) -> dict[int, int]:
    """Unabhängige Referenz (Schleifen): Zustand je Monat m >= lookback."""
    out = {}
    for m in range(lookback, len(eq)):
        growth = 1.0
        for j in range(m - lookback + 1, m - skip + 1):       # Monat j verzinst mit ^IRX am Ende von Monat j-1
            growth *= 1.0 + irx[j - 1] / 100.0 / 12.0
        rf = growth - 1.0
        rE = eq[m - skip] / eq[m - lookback] - 1.0 - rf
        rB = bd[m - skip] / bd[m - lookback] - 1.0 - rf
        out[m] = EQ_W if (rB > 0 and rE > 0) else (BD_W if rB > 0 else CASH_W)
    return out


def changes_only(states: dict[int, int]) -> list[tuple[int, int]]:
    out, last = [], None
    for m in sorted(states):
        if states[m] != last:
            out.append((m, states[m]))
            last = states[m]
    return out


def onehot(state: int, cols: list[str]) -> list[float]:
    return [1.0 if i == state else 0.0 for i in range(len(cols))]


def regime_paths(n_months=132, seed=2):
    """Monatliche Aktien-/Anleihe-/Zinspfade mit Regimewechseln (alle drei Zustände kommen vor)."""
    rng = np.random.default_rng(seed)
    m = np.arange(n_months)
    eq_r = np.where(np.sin(m / 9.0) > -0.2, 0.012, -0.02) + rng.normal(0, 0.03, n_months)
    bd_r = np.where(np.sin(m / 14.0 + 1.0) > -0.3, 0.005, -0.008) + rng.normal(0, 0.012, n_months)
    irx = 2.5 + 2.0 * np.sin(m / 20.0)
    return 100 * np.exp(np.cumsum(eq_r)), 100 * np.exp(np.cumsum(bd_r)), irx


def first_state(eq, bd, irx, **kw):
    """Gewichtszeile des ersten Signals (13 Monate Pfad -> genau ein Signal am 13. Monatsende)."""
    panel, _, me = step_panel(eq, bd, irx)
    w = S.weights(panel, **kw)
    assert len(w) == 1 and w.index[0] == me[12]
    return w.iloc[0].to_numpy()


# --------------------------------------------------------------------------------------
# Vertrag / Form
# --------------------------------------------------------------------------------------

def test_spec_contract():
    spec = S.SPEC
    assert spec["id"] == "xtsmom_us_switch_longcash"
    assert len(spec["variants"]) <= 3
    sig = inspect.signature(S.weights)
    for name in list(spec["params"]) + [k for v in spec["variants"].values() for k in v]:
        assert name in sig.parameters, name
    assert all(v == 2.0 for v in spec["cost_bps"].values())
    assert hasattr(S, "load")
    assert spec["params"]["lookback"] == 12 and spec["params"]["skip"] == 0
    assert spec["variants"]["skip1"] == {"skip": 1} and spec["variants"]["tlt"] == {"bond": LB}


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_shape_and_range(variant):
    panel = random_panel()
    params = {**S.SPEC["params"], **VARIANTS[variant]}
    w = S.weights(panel, **params)
    assert list(w.columns) == [params["equity"], params["bond"]]
    assert RT not in w.columns                                   # Zinsquelle bekommt nie ein Gewicht
    assert len(w) > 8
    assert w.notna().all().all()
    assert set(np.unique(w.to_numpy())) <= {0.0, 1.0}
    assert (w.sum(axis=1) <= 1.0 + 1e-12).all() and (w >= 0).all().all()   # kein Hebel, kein Short
    flags = month_end_flags(panel.close.index)
    assert w.index.isin(flags.index[flags.to_numpy()]).all()     # nur an Monatsenden
    assert w.index.is_monotonic_increasing and not w.index.has_duplicates
    kinds = {tuple(r) for r in w.to_numpy()}
    assert kinds == {(1.0, 0.0), (0.0, 1.0), (0.0, 0.0)}         # Aktie, Anleihe und Cash kommen vor


def test_only_state_changes_are_emitted():
    panel = random_panel()
    w = S.weights(panel)
    assert (w.diff().abs().sum(axis=1).iloc[1:] > 0).all()       # jede Folgezeile ist ein Wechsel
    # ein Wechsel pro Zeile: Aktie <-> Anleihe <-> Cash, nie zwei Titel zugleich
    assert (w.sum(axis=1) <= 1.0).all()


def test_invalid_arguments():
    panel = random_panel(n=800)
    with pytest.raises(ValueError):
        S.weights(panel, skip=12)
    with pytest.raises(ValueError):
        S.weights(panel, lookback=0)
    with pytest.raises(ValueError):
        S.weights(panel, equity=EQ, bond=EQ)
    with pytest.raises(KeyError):
        S.weights(panel, bond="XXX")
    assert S.weights(random_panel(n=200)).empty                  # weniger als 13 Monatsenden -> kein Signal


# --------------------------------------------------------------------------------------
# Regel
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant,kw", [
    ("base", dict(lookback=12, skip=0)),
    ("skip1", dict(lookback=12, skip=1)),
])
def test_matches_reference_rule(variant, kw):
    eq, bd, irx = regime_paths()
    panel, _, me = step_panel(eq, bd, irx)
    params = {**S.SPEC["params"], **VARIANTS[variant]}
    w = S.weights(panel, **params)
    ref = reference_states(eq, bd, irx, **kw)
    assert {s for s in ref.values()} == {EQ_W, BD_W, CASH_W}      # Testpfad enthält alle drei Zustände
    exp = changes_only(ref)
    assert list(w.index) == [me[m] for m, _ in exp]
    assert np.allclose(w.to_numpy(), np.array([onehot(s, [EQ, BD]) for _, s in exp]))


def test_tlt_variant_uses_long_bond_column():
    eq, bd, irx = regime_paths()
    lb = 100 * np.exp(np.cumsum(np.random.default_rng(9).normal(0.0, 0.03, len(eq))))
    panel, _, me = step_panel(eq, bd, irx, lb=lb)
    w = S.weights(panel, bond=LB)
    assert list(w.columns) == [EQ, LB]
    exp = changes_only(reference_states(eq, lb, irx))
    assert list(w.index) == [me[m] for m, _ in exp]
    assert np.allclose(w.to_numpy(), np.array([onehot(s, [EQ, LB]) for _, s in exp]))


def test_known_states():
    up, flat = np.linspace(100, 120, 13), np.full(13, 100.0)
    # Aktien +20 %, Anleihe +10 %, Zins 2 %: beide positiv -> Aktien
    assert first_state(up, np.linspace(100, 110, 13), 2.0).tolist() == [1.0, 0.0]
    # Aktien -10 %, Anleihe +10 % -> Flucht in Qualität: Anleihe
    assert first_state(np.linspace(100, 90, 13), np.linspace(100, 110, 13), 2.0).tolist() == [0.0, 1.0]
    # Anleihe -3 % -> Cash (Nullzeile), egal wie stark die Aktien laufen
    assert first_state(up, np.linspace(100, 97, 13), 2.0).tolist() == [0.0, 0.0]
    assert first_state(np.linspace(100, 90, 13), np.linspace(100, 97, 13), 2.0).tolist() == [0.0, 0.0]
    # Aktien-Überrendite, aber Anleihe flach -> rB < 0 (Zins abgezogen) -> Cash
    assert first_state(up, flat, 2.0).tolist() == [0.0, 0.0]


def test_excess_return_over_bills_decides():
    eq, bd = np.linspace(100, 130, 13), np.linspace(100, 103, 13)      # Anleihe +3 %
    assert first_state(eq, bd, 5.0).tolist() == [0.0, 0.0]            # Bills ~5,1 % -> rB < 0 -> Cash
    assert first_state(eq, bd, 1.0).tolist() == [1.0, 0.0]            # Bills ~1,0 % -> rB > 0, rE > 0 -> Aktien
    # Aktie +4 %: bei Zins 5 % negativ, bei 1 % positiv (Anleihe jeweils +20 %)
    eq2, bd2 = np.linspace(100, 104, 13), np.linspace(100, 120, 13)
    assert first_state(eq2, bd2, 5.0).tolist() == [0.0, 1.0]
    assert first_state(eq2, bd2, 1.0).tolist() == [1.0, 0.0]


def test_zero_is_not_positive():
    """Strikt > 0: Gleichheit zählt als nicht positiv (Spezifikation)."""
    flat = np.full(13, 100.0)
    assert first_state(flat, flat, 0.0).tolist() == [0.0, 0.0]                      # rB = 0 -> Cash
    assert first_state(flat, np.linspace(100, 110, 13), 0.0).tolist() == [0.0, 1.0]  # rE = 0 -> Anleihe, nicht Aktie


def test_rf12_compounds_monthly_irx_of_previous_month_end():
    """rf12 = Produkt (1 + IRX[Vormonatsende]/1200) - 1: Ein IRX-Sprung nur im LETZTEN Monat (T) zählt nicht."""
    eq, bd = np.linspace(100, 130, 13), np.linspace(100, 106, 13)      # Anleihe +6 %
    irx = np.full(13, 2.0)
    assert first_state(eq, bd, irx).tolist() == [1.0, 0.0]            # rf12 ~ 2,0 %
    irx_last = irx.copy()
    irx_last[12] = 40.0                                               # IRX[T] geht in rf12(T) nicht ein
    assert first_state(eq, bd, irx_last).tolist() == [1.0, 0.0]
    irx_first = irx.copy()
    irx_first[0] = 100.0                                              # IRX[T-12] ist der erste Monat von rf12 (100 % / 12)
    assert first_state(eq, bd, irx_first).tolist() == [0.0, 0.0]


def test_skip_variant_ignores_last_month():
    eq = np.concatenate([np.linspace(100, 130, 12), [100.0]])         # Aktien-Absturz nur im letzten Monat
    bd = np.linspace(100, 110, 13)
    assert first_state(eq, bd, 1.0).tolist() == [0.0, 1.0]            # Basis: rE = 0 - rf < 0 -> Anleihe
    assert first_state(eq, bd, 1.0, skip=1).tolist() == [1.0, 0.0]   # 12-1: Monate T-12..T-1 -> Aktien


def test_first_signal_needs_twelve_months_of_lookback():
    eq, bd, irx = regime_paths(n_months=40)
    panel, _, me = step_panel(eq, bd, irx)
    for kw in ({}, {"skip": 1}):
        w = S.weights(panel, **kw)
        assert w.index[0] == me[12]                                   # 13. Monatsende (Basis: Monatsende T-12 existiert)
    assert S.weights(step_panel(eq[:12], bd[:12], irx[:12])[0]).empty


def test_signal_columns_do_not_leak_into_weights():
    """Aktien-/Anleihe-Gewicht hängt nur von der jeweiligen Rolle ab: andere Spalten ändern nichts."""
    eq, bd, irx = regime_paths()
    panel, _, _ = step_panel(eq, bd, irx, lb=bd)
    w1 = S.weights(panel)
    close = panel.close.copy()
    close[LB] = close[LB].to_numpy()[::-1]                            # Langläufer komplett umdrehen
    w2 = S.weights(Panel(close.copy(), close))
    assert w1.equals(w2)


# --------------------------------------------------------------------------------------
# Fehlende Preise / Lücken (NaN = nicht handelbar)
# --------------------------------------------------------------------------------------

def _flip_path():
    """Aktien steigen 18 Monate, fallen dann; Anleihe steigt durchgehend -> Wechsel Aktien -> Anleihe."""
    n = 40
    eq = np.concatenate([np.linspace(100, 160, 18), np.linspace(155, 70, n - 18)])
    bd = np.linspace(100, 150, n)
    return eq, bd, np.full(n, 1.0)


def test_no_weights_on_nan_asset_prices():
    eq, bd, irx = _flip_path()
    panel, idx, me = step_panel(eq, bd, irx)
    ref = changes_only(reference_states(eq, bd, irx))
    assert [s for _, s in ref][:2] == [EQ_W, BD_W]
    flip = ref[1][0]                                                  # Monat des Wechsels Aktien -> Anleihe
    # (a) Anleihe am Signaltag des Wechsels ohne Kurs: kein Gewicht dort; das Signal kommt einen Monat später
    close = panel.close.copy()
    close.loc[me[flip], BD] = np.nan
    w = S.weights(Panel(close.copy(), close))
    assert me[flip] not in w.index
    assert me[flip + 1] in w.index and w.loc[me[flip + 1]].tolist() == [0.0, 1.0]
    # jedes ausgegebene Gewicht liegt auf einem Titel mit gültigem Kurs
    for d, row in w.iterrows():
        for t in (EQ, BD):
            assert row[t] == 0.0 or np.isfinite(close.loc[d, t])
    # (b) Aktie noch nicht gelistet: erstes Signal erst 12 Monatsenden nach dem ersten Kurs
    close = panel.close.copy()
    cut = me[2]
    close.loc[:cut, EQ] = np.nan
    w = S.weights(Panel(close.copy(), close))
    assert len(w) > 0 and w.index.min() >= me[3 + 12]
    assert close.loc[w.index[w[EQ] > 0], EQ].notna().all()


def test_signal_gaps_are_bridged_only_briefly():
    eq, bd, irx = regime_paths(n_months=60)
    panel, idx, me = step_panel(eq, bd, irx)
    base = S.weights(panel)
    # (a) bis 5 Handelstage ohne ^IRX am Monatsende: Vortageswert wird genutzt -> identisches Ergebnis
    close = panel.close.copy()
    close.loc[idx[idx <= me[5]][-5:], RT] = np.nan
    assert S.weights(Panel(close.copy(), close)).equals(base)
    # (b) 6 Handelstage ohne ^IRX am Monatsende von Monat 5: kein Signal in den Monaten, deren rf12-Fenster ihn enthält (6..17)
    close = panel.close.copy()
    close.loc[idx[idx <= me[5]][-6:], RT] = np.nan
    w = S.weights(Panel(close.copy(), close))
    ref_first = base.index[0]
    assert ref_first == me[12]
    assert w.index.min() >= me[18]
    # (c) fehlender ganzer Monat im Fenster (Monat 7 komplett weg): Signale der Monate 8..19 entfallen
    keep = ~((idx > me[6]) & (idx <= me[7]))
    p_gap = Panel(panel.open[keep], panel.close[keep])
    wg = S.weights(p_gap)
    assert wg.index.min() >= me[20]


# --------------------------------------------------------------------------------------
# Kausalität
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_causality_check(variant):
    panel = random_panel()
    params = {**S.SPEC["params"], **VARIANTS[variant]}
    assert check_causality(lambda p: S.weights(p, **params), panel) == []


def test_future_prices_do_not_change_past_weights():
    panel = random_panel()
    base = S.weights(panel)
    cut = panel.close.index[int(len(panel.close) * 0.6)]
    close = panel.close.copy()
    after = close.index > cut
    close.loc[after, [EQ, BD]] *= 0.01                                # drastisch andere Zukunft
    close.loc[after, RT] = 25.0                                        # und anderer Zins
    other = S.weights(Panel(close.copy(), close))
    assert base.loc[:cut].equals(other.loc[:cut])


def test_last_data_day_mid_month_is_not_month_end():
    panel = random_panel(n=1600)
    idx = panel.close.index
    mid = idx[idx >= pd.Timestamp("2008-06-10")][0]
    w = S.weights(panel.truncate(mid))
    assert w.index.max() < pd.Timestamp("2008-06-01")                  # Juni 2008 hat noch kein Monatsende
    assert S.weights(panel).index.max() > mid


# --------------------------------------------------------------------------------------
# Engine-Integration (Ausführungstiming, Exposure)
# --------------------------------------------------------------------------------------

def test_engine_integration_timing_and_exposure():
    eq, bd, irx = regime_paths(n_months=132, seed=2)
    panel, idx, _ = step_panel(eq, bd, irx)
    rng = np.random.default_rng(1)
    noise = pd.Series(1 + rng.normal(0, 0.002, len(idx)), index=idx)
    close = panel.close.copy()
    close[[EQ, BD, LB]] = close[[EQ, BD, LB]].mul(noise, axis=0)       # Tagesbewegung; Monatsendwerte bleiben maßgeblich
    p2 = Panel(close.copy(), close)
    w = S.weights(p2)
    res = run_backtest(p2, w, cost=CostModel(per_ticker_bps={t: 2.0 for t in (EQ, BD, LB)}))
    assert (res.gross_exposure <= 1.0 + 1e-3).all()
    assert (res.weights[[EQ, BD]] >= -1e-9).all().all()
    assert (res.weights[[LB, RT]].abs() <= 1e-12).all().all()          # nie ein Gewicht auf Langläufer (Basis) oder ^IRX
    # Cash-Zustand = Nullzeile -> keine Position
    zero_rows = w.index[(w.sum(axis=1) == 0).to_numpy()]
    assert len(zero_rows) > 0
    for d in zero_rows:
        if d == p2.close.index[-1]:
            continue
        nxt = p2.close.index[p2.close.index.get_loc(d) + 1]
        assert res.gross_exposure.loc[nxt] < 1e-6
    # Signal am Tag t -> Position erst ab t+1 (Handel zum NAV von t+1), nicht schon am Signaltag
    held = w.index[(w.sum(axis=1) > 0).to_numpy()]
    s = held[0]
    col = w.loc[s].idxmax()
    assert res.weights.loc[s, col] < 1e-9
    nxt = p2.close.index[p2.close.index.get_loc(s) + 1]
    assert res.weights.loc[nxt, col] > 0.95
    # Gehandelt wird nur am Tag nach einem Zustandswechsel, sonst kein Umsatz
    pos = p2.close.index.get_indexer(w.index) + 1
    exec_days = p2.close.index[pos[pos < len(p2.close.index)]]
    assert (res.turnover.drop(exec_days) <= 1e-12).all()


# --------------------------------------------------------------------------------------
# Daten-Bausteine (ohne Netz)
# --------------------------------------------------------------------------------------

def test_par_bond_duration_known_values():
    assert S.par_bond_duration(0.05, 5.0) == pytest.approx((1 - 1.025 ** -10) / 0.05)     # ~4,376
    assert S.par_bond_duration(0.04, 30.0) == pytest.approx((1 - 1.02 ** -60) / 0.04)
    assert S.par_bond_duration(1e-9, 5.0) == pytest.approx(5.0, rel=1e-3)                  # y -> 0: Duration -> Laufzeit
    d = S.par_bond_duration(np.array([0.02, 0.05, 0.10]), 5.0)
    assert d[0] > d[1] > d[2]                                                              # höhere Rendite -> kürzere Duration


def test_synthetic_bond_index_carry_and_duration():
    idx = pd.bdate_range("2000-01-03", periods=60)
    y = pd.Series(5.0, index=idx)
    s = S.synthetic_bond_index(y, 5.0)
    assert s.iloc[0] == 100.0 and len(s) == len(y)
    assert np.allclose(s.pct_change().dropna(), 0.05 / 252)                  # konstante Rendite -> reiner Carry
    y2 = y.copy()
    y2.iloc[10:] = 5.5                                                       # Renditesprung +50 bp am Tag 10
    s2 = S.synthetic_bond_index(y2, 5.0)
    r10 = s2.iloc[10] / s2.iloc[9] - 1
    assert r10 == pytest.approx(0.05 / 252 - S.par_bond_duration(0.05, 5.0) * 0.005)
    assert r10 < 0                                                           # Renditeanstieg -> Kursverlust
    r11 = s2.iloc[11] / s2.iloc[10] - 1
    assert r11 == pytest.approx(0.055 / 252)                                 # danach wieder Carry auf neuem Niveau
    # Lücke in der Rendite: Änderung gegen den letzten gültigen Wert, kein NaN im Ergebnis
    y3 = y.copy()
    y3.iloc[10:12] = np.nan
    y3.iloc[12:] = 5.5
    s3 = S.synthetic_bond_index(y3, 5.0)
    assert s3.notna().all() and len(s3) == len(y) - 2


def test_splice_bond_continuity_and_exact_real_prices():
    idx = pd.bdate_range("2000-01-03", periods=400)
    synth = pd.Series(100 * np.exp(np.cumsum(np.random.default_rng(3).normal(0, 0.003, 400))), index=idx)
    t0 = idx[250]
    real = pd.Series(3.0 * np.exp(np.cumsum(np.random.default_rng(4).normal(0, 0.002, 150))), index=idx[250:])
    out = S.splice_bond(real, synth)
    assert out.index.is_monotonic_increasing and not out.index.has_duplicates
    assert out.loc[t0:].equals(real)                                         # ab Fondsstart exakt die echten Kurse
    prev, nxt = idx[249], idx[251]
    assert out.loc[t0] / out.loc[prev] == pytest.approx(synth.loc[t0] / synth.loc[prev])     # Niveau-Splice ohne Sprung
    assert out.loc[:prev].pct_change().dropna().to_numpy() == pytest.approx(synth.loc[:prev].pct_change().dropna().to_numpy())
    assert len(out) == len(idx) and out.loc[nxt] == real.loc[nxt]


def test_build_panel_alignment_and_bridging():
    eq_idx = pd.bdate_range("1990-01-02", periods=60)
    eq = pd.Series(np.linspace(10, 12, 60), index=eq_idx)
    bond_idx = eq_idx.delete([20, 30, 31, 32, 33, 34, 35, 36])             # Lücken: 1 Tag (20) und 7 Tage (30..36)
    # FFILL_LIMIT = 5: Tage 30..34 werden überbrückt, 35 und 36 bleiben NaN
    bond = pd.Series(np.linspace(50, 52, 60), index=eq_idx).loc[bond_idx]
    irx = pd.Series(3.0, index=eq_idx)
    p = S.build_panel(eq, bond, bond * 2, irx)
    assert p.tickers == [EQ, BD, LB, RT]
    assert p.close.index.equals(eq_idx) and p.open.equals(p.close)           # open == close (Fonds-NAV)
    assert p.close.loc[eq_idx[20], BD] == bond.loc[eq_idx[19]]               # 1 Tag Lücke: Vortageswert
    assert S.FFILL_LIMIT == 5
    assert p.close.loc[eq_idx[34], BD] == bond.loc[eq_idx[29]]               # 5. Lückentag: letzter überbrückter
    assert np.isnan(p.close.loc[eq_idx[35], BD]) and np.isnan(p.close.loc[eq_idx[36], BD])   # danach nicht handelbar
    assert p.close[RT].eq(3.0).all() and p.close[EQ].equals(eq)
    # Der Aktienfonds bestimmt den Handelskalender; Zeilen ohne Aktienkurs entfallen
    eq_gap = eq.drop(eq_idx[5])
    assert eq_idx[5] not in S.build_panel(eq_gap, bond, bond, irx).close.index


def test_panel_without_rate_column_is_rejected():
    panel = random_panel(n=800)
    with pytest.raises(KeyError):
        S.weights(Panel(panel.open.drop(columns=[RT]), panel.close.drop(columns=[RT])))
