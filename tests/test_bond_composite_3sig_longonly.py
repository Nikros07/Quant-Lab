"""Tests für strategies/bond_composite_3sig_longonly.py — nur synthetische Daten, kein Netz, kein Datencache."""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import month_end_flags
from qlab.data import Panel
from qlab.engine import CostModel, check_causality, default_teilfreistellung, run_backtest
from strategies import bond_composite_3sig_longonly as strat

A, TNX, IRX, PIE = strat.ASSET, strat.TNX, strat.IRX, strat.PIE
VARIANTS = {"base": {}, **strat.SPEC["variants"]}
FULL_PARAMS = strat.SPEC["params"]


# --------------------------------------------------------------------------------------
# Synthetische Daten
# --------------------------------------------------------------------------------------

def _signal_frame(n_years: float = 16, seed: int = 5, start: str = "1990-01-02") -> pd.DataFrame:
    """Prozentwerte: 10J-Rendite (mean-reverting mit langsamem Zyklus), 3M-Satz mit schwankendem Spread, erwartete Inflation."""
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


def _price_from_signals(sig: pd.DataFrame) -> pd.Series:
    r10, _ = strat.synthetic_returns(sig[TNX], sig[IRX])
    return 100.0 * (1.0 + r10.fillna(0.0)).cumprod()


def _panel(n_years: float = 16, seed: int = 5, start: str = "1990-01-02") -> Panel:
    sig = _signal_frame(n_years, seed, start)
    close = sig.copy()
    close.insert(0, A, _price_from_signals(sig))
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
    assert spec["id"] == "bond_composite_3sig_longonly"
    assert len(spec["variants"]) <= 3
    sig = inspect.signature(strat.weights)
    for name in list(spec["params"]) + [k for v in spec["variants"].values() for k in v]:
        assert name in sig.parameters, name
    assert hasattr(strat, "load")
    assert set(spec["tickers"]) == {A, TNX, IRX, PIE}
    # Parameter exakt aus der Spezifikation
    p = spec["params"]
    assert p["carry_window"] == 2520 and p["carry_threshold"] == pytest.approx(1 / 3)
    assert (p["ewma_fast"], p["ewma_slow"], p["anchor_halflife"]) == (21, 252, 36)
    assert set(p["signals"]) == {"carry", "trend", "value"}
    assert set(spec["variants"]) == {"only_carry", "only_trend", "only_value"}


def test_proxy_name_gets_no_teilfreistellung():
    """Die synthetische Anleihe muss im Steuermodell als Rentenpapier (0 %) laufen, nicht als Aktienfonds (30 %)."""
    assert default_teilfreistellung(A) == 0.0


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_shape_and_range(variant):
    panel = _panel()
    w = strat.weights(panel, **{**FULL_PARAMS, **VARIANTS[variant]})
    assert list(w.columns) == [A]
    assert len(w) > 40
    assert w.notna().all().all()
    allowed = {0.0, 1.0} if variant != "base" else {0.0, 1 / 3, 2 / 3, 1.0}
    assert set(np.round(np.unique(w.to_numpy()), 12)) <= {round(a, 12) for a in allowed}
    assert (w.sum(axis=1) <= 1.0 + 1e-12).all() and (w >= 0).all().all()       # kein Hebel, kein Short
    assert w.index.isin(_month_end_index(panel)).all()                           # nur an Monatsenden
    assert w.index.is_monotonic_increasing and not w.index.has_duplicates


def test_weights_never_use_signal_columns():
    w = strat.weights(_panel())
    assert TNX not in w.columns and IRX not in w.columns and PIE not in w.columns


def test_invalid_signal_selection_raises():
    with pytest.raises(ValueError):
        strat.weights(_panel(), signals=())
    with pytest.raises(ValueError):
        strat.weights(_panel(), signals=("carry", "momentum"))


# --------------------------------------------------------------------------------------
# Synthetische Anleihe
# --------------------------------------------------------------------------------------

def test_par_duration_formula():
    y = pd.Series([0.04, 0.0, -0.01, 0.10])
    d = strat.par_duration(y)
    assert d.iloc[0] == pytest.approx((1 - 1.02 ** -20) / 0.04)
    assert 8.0 < d.iloc[0] < 8.3                      # 10J-Par-Anleihe bei 4 %: Duration ca. 8,2
    assert np.isnan(d.iloc[1]) and np.isnan(d.iloc[2])
    assert d.iloc[3] == pytest.approx((1 - 1.05 ** -20) / 0.10)


def test_synthetic_returns_known_answers():
    tnx = pd.Series([4.0, 4.0, 4.5, 4.0], index=pd.bdate_range("2000-01-03", periods=4))
    irx = pd.Series([3.0, 3.0, 3.0, 2.52], index=tnx.index)
    r10, rc = strat.synthetic_returns(tnx, irx)
    assert np.isnan(r10.iloc[0]) and np.isnan(rc.iloc[0])
    d4 = (1 - 1.02 ** -20) / 0.04
    d45 = (1 - 1.0225 ** -20) / 0.045
    assert r10.iloc[1] == pytest.approx(0.04 / 252)                                      # Rendite unverändert -> Carry
    assert r10.iloc[2] == pytest.approx(0.04 / 252 - d4 * 0.005)                         # Zins steigt -> Verlust
    assert r10.iloc[3] == pytest.approx(0.045 / 252 - d45 * (-0.005))                    # Zins fällt -> Gewinn
    assert rc.iloc[1] == pytest.approx(0.03 / 252)
    assert rc.iloc[3] == pytest.approx(0.03 / 252)                                       # Rc nutzt den Vortageswert
    # gestern bekannt: r10 an Tag t hängt nicht von zukünftigen Renditen ab
    r10b, _ = strat.synthetic_returns(tnx.iloc[:3], irx.iloc[:3])
    assert r10b.iloc[:3].equals(r10.iloc[:3])


# --------------------------------------------------------------------------------------
# Inflationserwartung / CPI-Verzögerung
# --------------------------------------------------------------------------------------

def _cpi(n_months=120, growth=0.02, start="2000-01-31", noise=0.0, seed=0):
    idx = pd.date_range(start, periods=n_months, freq="ME")
    rng = np.random.default_rng(seed)
    return pd.Series(100.0 * (1 + growth) ** (np.arange(n_months) / 12.0) * (1 + rng.normal(0, noise, n_months)), index=idx)


def test_expected_inflation_constant_growth():
    pie = strat.expected_inflation_monthly(_cpi(120, 0.02))
    assert isinstance(pie.index, pd.PeriodIndex)
    first = pie.first_valid_index()
    assert first == pd.Period("2000-01", "M") + 47        # 12 Monate für infl, dann 36 Werte
    assert pie.dropna().to_numpy() == pytest.approx(0.02)


def test_expected_inflation_matches_manual_mean():
    cpi = _cpi(100, 0.03, noise=0.004, seed=3)
    pie = strat.expected_inflation_monthly(cpi)
    c = cpi.to_numpy()
    k = 70
    infl = [c[j] / c[j - 12] - 1 for j in range(k - 35, k + 1)]
    assert pie.iloc[k] == pytest.approx(np.mean(infl))
    assert len(infl) == 36


def test_expected_inflation_gap_is_not_bridged():
    cpi = _cpi(140, 0.03)
    gap = cpi.drop(cpi.index[60])
    pie = strat.expected_inflation_monthly(gap)
    assert len(pie) == 140                                   # Monatsraster bleibt vollständig, die Lücke wird NaN
    # Die Lücke macht infl in Monat 60 und 72 ungültig und damit jedes 36er-Fenster, das einen davon enthält (60..107).
    assert pie.iloc[60:108].isna().all()
    assert pie.iloc[59] == pytest.approx(0.03) and pie.iloc[108] == pytest.approx(0.03)


def test_cpi_step_column_lag_units_and_expiry():
    months = pd.period_range("2020-01", "2020-12", freq="M")
    pie = pd.Series(np.arange(1, 13) / 100.0, index=months)             # 1 % ... 12 %
    idx = pd.bdate_range("2019-12-02", "2021-04-30")
    col = strat.cpi_step_column(pie, idx, lag_months=2)
    assert col.loc["2020-02-28"] != col.loc["2020-02-28"]              # Januar gilt erst ab 1. März
    assert col.loc["2020-03-02"] == pytest.approx(1.0)                  # Prozent, nicht Dezimal
    assert col.loc["2020-03-31"] == pytest.approx(1.0)                  # am Märzende ist erst der Januar bekannt (m-2)
    assert col.loc["2020-04-30"] == pytest.approx(2.0)
    assert col.loc["2021-02-26"] == pytest.approx(12.0)                 # Dezember gilt ab 1. Februar 2021
    assert col.loc["2021-03-01"] != col.loc["2021-03-01"]              # danach kein stilles Weiterschreiben
    assert col.loc["2021-04-30"] != col.loc["2021-04-30"]


def test_cpi_step_column_is_causal():
    months = pd.period_range("2010-01", periods=60, freq="M")
    pie = pd.Series(np.random.default_rng(1).normal(0.02, 0.01, 60), index=months)
    idx = pd.bdate_range("2010-01-04", "2015-06-30")
    base = strat.cpi_step_column(pie, idx)
    changed = pie.copy()
    changed.iloc[40:] += 0.05                                           # ab Monat 40 andere Zukunft
    other = strat.cpi_step_column(changed, idx)
    cut = (months[40] + 2).to_timestamp(how="start")                    # Verfügbarkeit des geänderten Werts
    before = idx[idx < cut]
    assert len(before) > 100
    assert np.allclose(base.loc[before], other.loc[before], equal_nan=True)
    assert not np.allclose(base.loc[idx[idx >= cut]], other.loc[idx[idx >= cut]], equal_nan=True)


def test_cpi_gap_gives_nan_not_stale_value():
    months = pd.period_range("2010-01", periods=24, freq="M")
    pie = pd.Series(0.02, index=months)
    pie.iloc[10] = np.nan
    idx = pd.bdate_range("2010-01-04", "2012-03-30")
    col = strat.cpi_step_column(pie, idx)
    gap_day = idx[idx >= (months[10] + 2).to_timestamp(how="start")][0]
    assert np.isnan(col.loc[gap_day])


# --------------------------------------------------------------------------------------
# Panel-Aufbau (ohne Netz)
# --------------------------------------------------------------------------------------

def test_build_panel_structure():
    sig = _signal_frame(3, seed=2, start="1990-01-02")
    pie_m = pd.Series(0.03, index=pd.period_range("1980-01", "1992-12", freq="M"))
    irx = sig[IRX].copy()
    irx.iloc[100:103] = np.nan                                           # kurze Lücke -> wird gefüllt
    p = strat.build_panel(sig[TNX], irx.dropna(), pie_m)
    assert p.tickers == [A, TNX, IRX, PIE]
    assert p.close.index.equals(sig.index)
    assert p.open.equals(p.close)                                        # open == close (Handel zum Folgetag-Schluss)
    r10, _ = strat.synthetic_returns(p.close[TNX], p.close[IRX])
    assert np.isnan(p.close[A].iloc[0])                                  # erster Tag hat keine Rendite
    assert p.close[A].iloc[1] == pytest.approx(100.0 * (1 + r10.iloc[1]))
    assert np.allclose(p.close[A].dropna().to_numpy(), (100.0 * (1 + r10.fillna(0.0)).cumprod()).iloc[1:].to_numpy())
    assert p.close[IRX].iloc[100:103].notna().all()                      # Lücke vorwärts gefüllt (<= 5 Tage)
    assert p.close[PIE].dropna().iloc[0] == pytest.approx(3.0)           # Prozent


def test_build_panel_long_irx_gap_stays_nan():
    sig = _signal_frame(2, seed=2, start="1990-01-02")
    irx = sig[IRX].copy()
    irx.iloc[100:120] = np.nan
    pie_m = pd.Series(0.03, index=pd.period_range("1980-01", "1992-12", freq="M"))
    p = strat.build_panel(sig[TNX], irx.dropna(), pie_m)
    assert p.close[IRX].iloc[100:105].notna().all()
    assert p.close[IRX].iloc[106:120].isna().all()


def test_check_yield_units_rejects_scaled_data():
    ok = pd.Series(np.linspace(1.0, 8.0, 500))
    strat._check_yield_units(ok, "x")
    with pytest.raises(ValueError):
        strat._check_yield_units(ok * 10.0, "x")                          # Faktor-10-Einheit


# --------------------------------------------------------------------------------------
# Stimmen: Referenzimplementierungen (naiv, getrennt vom Modulcode)
# --------------------------------------------------------------------------------------

def _carry_ref(spread: np.ndarray, flags: np.ndarray, window=2520, thr=1 / 3) -> dict[int, float]:
    out = {}
    for i in np.flatnonzero(flags):
        if i < window or np.isnan(spread[i]):
            continue
        past = [x for x in spread[i - window:i] if not np.isnan(x)]
        if len(past) < 0.95 * window:
            continue
        below = sum(1 for x in past if x < spread[i])
        out[i] = 1.0 if below / len(past) > thr else 0.0
    return out


def _ewma_ref(x: np.ndarray, alpha: float, min_obs: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    y, n = None, 0
    for i, v in enumerate(x):
        if np.isnan(v):
            continue
        y = v if y is None else (1 - alpha) * y + alpha * v
        n += 1
        if n >= min_obs:
            out[i] = y
    return out


def test_carry_vote_matches_reference():
    sig = _signal_frame(16, seed=9)
    flags = month_end_flags(sig.index).to_numpy()
    spread = ((sig[TNX] - sig[IRX]) / 100.0)
    got = strat.carry_vote(spread, flags)
    ref = _carry_ref(spread.to_numpy(), flags)
    pos = {d: i for i, d in enumerate(sig.index)}
    got_valid = got.dropna()
    assert {pos[d] for d in got_valid.index} == set(ref)
    assert all(got_valid.loc[sig.index[i]] == v for i, v in ref.items())
    assert 0 < got_valid.mean() < 1                                     # beide Zustände kommen vor


def test_carry_vote_threshold_is_strictly_greater_than_one_third():
    n = 2520
    for below, expect in ((839, 0.0), (840, 0.0), (841, 1.0)):          # genau 1/3 zählt NICHT
        past = np.r_[np.full(below, -1.0), np.full(n - below, 1.0)]
        v = np.r_[past, 0.0]
        s = pd.Series(v, index=pd.bdate_range("2000-01-03", periods=n + 1))
        flags = np.zeros(n + 1, bool)
        flags[-1] = True
        got = strat.carry_vote(s, flags)
        assert got.iloc[-1] == expect, below


def test_carry_vote_excludes_current_day_and_needs_full_history():
    n = 2520
    s = pd.Series(np.arange(n + 3, dtype=float), index=pd.bdate_range("2000-01-03", periods=n + 3))
    flags = np.zeros(n + 3, bool)
    flags[[n - 1, n, n + 2]] = True
    got = strat.carry_vote(s, flags)
    assert np.isnan(got.iloc[0])                                         # nur 2519 Vortage -> noch kein Signal
    assert got.iloc[1] == 1.0                                            # 2520 Vortage, alle kleiner -> Anteil 1
    # Der heutige Wert zählt nicht zum Vergleichsfenster: heutiger Wert ist der kleinste -> Anteil 0
    s2 = s.copy()
    s2.iloc[n + 2] = -5.0
    assert strat.carry_vote(s2, flags).iloc[2] == 0.0
    # Zu viele Lücken im Fenster (< 95 % gültig) -> kein Signal
    s3 = s.copy()
    s3.iloc[100:100 + 200] = np.nan
    assert np.isnan(strat.carry_vote(s3, flags).iloc[1])
    # heutiger Wert fehlt -> kein Signal
    s4 = s.copy()
    s4.iloc[n] = np.nan
    assert np.isnan(strat.carry_vote(s4, flags).iloc[1])


def test_trend_vote_matches_reference():
    sig = _signal_frame(10, seed=4)
    flags = month_end_flags(sig.index).to_numpy()
    got = strat.trend_vote(sig[TNX], sig[IRX], flags)
    r10, rc = strat.synthetic_returns(sig[TNX], sig[IRX])
    ex = (np.log1p(r10) - np.log1p(rc)).to_numpy()
    ef = _ewma_ref(ex, 2 / 22, 21)
    es = _ewma_ref(ex, 2 / 253, 252)
    ref = np.where(np.isnan(ef) | np.isnan(es), np.nan, ((ef > 0) & (es > 0)).astype(float))
    exp = pd.Series(ref, index=sig.index)[flags]
    assert got.index.equals(exp.index)
    assert np.allclose(got.to_numpy(), exp.to_numpy(), equal_nan=True)
    assert 0 < got.dropna().mean() < 1


def test_trend_vote_direction_and_warmup():
    idx = pd.bdate_range("2000-01-03", periods=800)
    flags = month_end_flags(idx).to_numpy()
    irx = pd.Series(1.0, index=idx)
    fall = pd.Series(np.linspace(8.0, 4.0, 800), index=idx)             # Zinsen fallen -> Anleihen steigen
    rise = pd.Series(np.linspace(4.0, 8.0, 800), index=idx)
    up = strat.trend_vote(fall, irx, flags).dropna()
    dn = strat.trend_vote(rise, irx, flags).dropna()
    assert (up == 1.0).all() and len(up) > 20
    assert (dn == 0.0).all() and len(dn) > 20
    first_valid = strat.trend_vote(fall, irx, flags).first_valid_index()
    assert idx.get_loc(first_valid) >= 252                              # Span-252-EWMA braucht 252 Beobachtungen


def _ewmas(y: np.ndarray, idx):
    r10, rc = strat.synthetic_returns(pd.Series(y, index=idx), pd.Series(0.5, index=idx))
    ex = np.log1p(r10) - np.log1p(rc)
    return ex.ewm(span=21, adjust=False, min_periods=21).mean(), ex.ewm(span=252, adjust=False, min_periods=252).mean()


def test_trend_vote_requires_both_ewmas_positive():
    idx = pd.bdate_range("2000-01-03", periods=700)
    flags = np.zeros(700, bool)
    flags[[630, 699]] = True
    # (a) Lange Hausse, dann kurzer Zinsanstieg: schnelle EWMA negativ, langsame (noch) positiv oder negativ -> Stimme 0
    y = np.r_[np.linspace(8.0, 3.0, 640), np.linspace(3.0, 3.9, 60)]
    ef, es = _ewmas(y, idx)
    assert ef.iloc[630] > 0 and es.iloc[630] > 0 and ef.iloc[699] < 0
    got = strat.trend_vote(pd.Series(y, index=idx), pd.Series(0.5, index=idx), flags)
    assert got.iloc[0] == 1.0 and got.iloc[1] == 0.0
    # (b) Lange Baisse, dann kurze Erholung: schnelle EWMA positiv, langsame negativ -> Stimme 0
    y = np.r_[np.linspace(3.0, 8.0, 670), np.linspace(8.0, 7.8, 30)]
    ef, es = _ewmas(y, idx)
    assert ef.iloc[699] > 0 and es.iloc[699] < 0
    got = strat.trend_vote(pd.Series(y, index=idx), pd.Series(0.5, index=idx), flags)
    assert got.iloc[1] == 0.0


def test_value_vote_matches_reference_and_direction():
    sig = _signal_frame(16, seed=6)
    flags = month_end_flags(sig.index).to_numpy()
    got = strat.value_vote(sig[TNX], sig[PIE], flags, 36)
    real = (sig[TNX] - sig[PIE]).to_numpy()[flags]
    alpha = 1 - 0.5 ** (1 / 36)
    anchor = _ewma_ref(real, alpha, 36)
    ref = np.where(np.isnan(anchor), np.nan, (real > anchor).astype(float))
    assert np.allclose(got.to_numpy(), ref, equal_nan=True)
    assert 0 < got.dropna().mean() < 1
    # Richtung: steigender Realzins liegt über dem Anker, fallender darunter
    idx = pd.bdate_range("2000-01-03", periods=2000)
    fl = month_end_flags(idx).to_numpy()
    pie = pd.Series(2.0, index=idx)
    assert (strat.value_vote(pd.Series(np.linspace(3, 9, 2000), index=idx), pie, fl).dropna() == 1.0).all()
    assert (strat.value_vote(pd.Series(np.linspace(9, 3, 2000), index=idx), pie, fl).dropna() == 0.0).all()
    # Warm-up: erst nach 36 Monatsenden
    v = strat.value_vote(pd.Series(np.linspace(3, 9, 2000), index=idx), pie, fl)
    assert v.notna().sum() == fl.sum() - 35


def test_value_vote_nan_pie_gives_no_vote():
    idx = pd.bdate_range("2000-01-03", periods=1500)
    fl = month_end_flags(idx).to_numpy()
    tnx = pd.Series(np.linspace(3, 9, 1500), index=idx)
    pie = pd.Series(2.0, index=idx)
    pie.iloc[1200:] = np.nan                                             # CPI-Reihe abgelaufen
    v = strat.value_vote(tnx, pie, fl)
    me = idx[fl]
    assert v[me[me >= idx[1200]]].isna().all()
    assert v[me[me < idx[1200]]].dropna().size > 0


# --------------------------------------------------------------------------------------
# Zusammensetzung der Gewichte
# --------------------------------------------------------------------------------------

def test_weight_is_mean_of_votes_and_variants_share_start():
    panel = _panel()
    v = strat.votes(panel)
    w = strat.weights(panel)
    ok = v.notna().all(axis=1)
    assert w.index.equals(v.index[ok.to_numpy() & panel.close[A][month_end_flags(panel.close.index).to_numpy()].notna().to_numpy()])
    assert np.allclose(w[A].to_numpy(), v.loc[w.index].sum(axis=1).to_numpy() / 3.0)
    for name, col in (("only_carry", "carry"), ("only_trend", "trend"), ("only_value", "value")):
        wv = strat.weights(panel, **{**FULL_PARAMS, **strat.SPEC["variants"][name]})
        assert wv.index.equals(w.index)                                  # gemeinsames Startdatum für alle Läufe
        assert np.array_equal(wv[A].to_numpy(), v.loc[wv.index, col].to_numpy())
    # alle drei Zustände des Komposits kommen im Testpfad vor, sonst taugt der Test nichts
    assert w[A].nunique() >= 3


def test_first_signal_needs_carry_history():
    panel = _panel()
    w = strat.weights(panel)
    first_pos = panel.close.index.get_loc(w.index[0])
    assert first_pos >= 2520                                             # 2520 Vortage Carry-Historie
    # das erste Monatsende mit >= 2520 Vortagen ist das erste Signal (Trend und Value sind früher bereit)
    me = _month_end_index(panel)
    expected = me[[panel.close.index.get_loc(d) >= 2520 for d in me]][0]
    assert w.index[0] == expected


def test_signals_ignore_asset_column():
    panel = _panel()
    close = panel.close.copy()
    close[A] = 50.0 + np.arange(len(close))                              # Handelstitel völlig anders
    other = strat.weights(Panel(close.copy(), close))
    assert strat.weights(panel).equals(other)


# --------------------------------------------------------------------------------------
# Fehlende Kurse (NaN = nicht handelbar)
# --------------------------------------------------------------------------------------

def test_no_weights_on_nan_asset_prices():
    panel = _panel()
    base = strat.weights(panel)
    close = panel.close.copy()
    cut = base.index[10]
    close.loc[:cut, A] = np.nan                                          # Titel noch nicht gelistet
    w = strat.weights(Panel(close.copy(), close))
    assert w.index.min() > cut
    assert not close.loc[w.index, A].isna().any()
    # einzelner NaN-Kurs am Monatsende: dort kein Gewicht
    hole = base.index[20]
    close2 = panel.close.copy()
    close2.loc[hole, A] = np.nan
    w2 = strat.weights(Panel(close2.copy(), close2))
    assert hole not in w2.index and base.index[21] in w2.index


def test_expired_cpi_series_stops_weights():
    panel = _panel()
    base = strat.weights(panel)
    stop = base.index[30]
    close = panel.close.copy()
    close.loc[close.index > stop, PIE] = np.nan                          # keine aktuelle CPI mehr
    w = strat.weights(Panel(close.copy(), close))
    assert w.index.max() <= stop
    assert w.equals(base.loc[:stop])


def test_missing_signal_value_at_month_end_gives_no_row():
    panel = _panel()
    base = strat.weights(panel)
    d = base.index[25]
    close = panel.close.copy()
    close.loc[d, TNX] = np.nan
    w = strat.weights(Panel(close.copy(), close))
    assert d not in w.index


# --------------------------------------------------------------------------------------
# Kausalität
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_causality_check(variant):
    panel = _panel()
    params = {**FULL_PARAMS, **VARIANTS[variant]}
    assert check_causality(lambda p: strat.weights(p, **params), panel) == []
    # Schnitte mitten in der Signalphase (nicht nur im Vorlauf)
    me = _month_end_index(panel)
    cuts = [me[-60], me[-40], me[-22], me[-5]]
    assert check_causality(lambda p: strat.weights(p, **params), panel, cuts=cuts) == []


def test_future_data_does_not_change_past_weights():
    panel = _panel()
    base = strat.weights(panel)
    cut = base.index[len(base) // 2]
    close = panel.close.copy()
    after = close.index > cut
    close.loc[after, TNX] = close.loc[after, TNX] * 0.1 + 0.5            # drastisch andere Zinszukunft
    close.loc[after, IRX] = 9.0
    close.loc[after, PIE] = 12.0
    close.loc[after, A] = close.loc[after, A] * 0.01
    other = strat.weights(Panel(close.copy(), close))
    assert base.loc[:cut].equals(other.loc[:cut])
    assert not base.loc[cut:].equals(other.loc[cut:])                    # die Zukunft selbst darf sich ändern


def test_last_data_day_mid_month_is_not_month_end():
    panel = _panel()
    idx = panel.close.index
    mid = idx[idx >= pd.Timestamp("2003-06-10")][0]
    w = strat.weights(panel.truncate(mid))
    assert (w.index.max() if len(w) else pd.Timestamp("1900-01-01")) < pd.Timestamp("2003-06-01")
    v = strat.votes(panel.truncate(mid))
    assert v.index.max() < pd.Timestamp("2003-06-01")
    assert strat.votes(panel).index.max() > mid                        # mit späteren Daten ist der Juni 2003 abgeschlossen


# --------------------------------------------------------------------------------------
# Engine-Integration (Ausführungstiming, Exposure)
# --------------------------------------------------------------------------------------

def test_engine_integration_timing_and_exposure():
    panel = _panel()
    w = strat.weights(panel)
    res = run_backtest(panel, w, rf=_rf(panel))
    assert (res.gross_exposure <= 1.0 + 1e-3).all()                          # ungehebelt; Kosten kommen aus dem Cash
    assert (res.weights[A] >= -1e-9).all()
    assert (res.weights[[TNX, IRX, PIE]].abs().to_numpy() < 1e-12).all()   # nie ein Gewicht auf Signalspalten
    assert res.skipped_orders == 0
    idx = panel.close.index
    # Signal am Tag t -> Position erst am Tag t+1 (open == close: Handel zum Schluss von t+1), nicht schon an t
    changes = w.index[(w[A].diff().abs() > 1e-9).to_numpy()]
    s = changes[3]
    nxt = idx[idx.get_loc(s) + 1]
    before = res.weights.loc[s, A]
    assert before == pytest.approx(w[A].shift(1).loc[s], abs=0.08)          # noch das alte Gewicht (plus Drift)
    assert res.weights.loc[nxt, A] == pytest.approx(w.loc[s, A], abs=2e-3)   # neues Zielgewicht, nur Kosten als Abweichung
    # gehandelt wird nur am Tag nach einem Signal
    pos = idx.get_indexer(w.index) + 1
    exec_days = idx[pos[pos < len(idx)]]
    assert (res.turnover.drop(exec_days) <= 1e-12).all()


def test_engine_position_earns_return_from_t_plus_2():
    """Neue Position verdient erst die Rendite ab t_m+2 (nicht die des Ausführungstages t_m+1)."""
    idx = pd.bdate_range("2000-01-03", periods=40)
    price = pd.Series(100.0, index=idx)
    price.iloc[11:] = 110.0                                              # Sprung an Tag 11 (= t+1)
    price.iloc[13:] = 121.0                                              # Sprung an Tag 13 (= t+3)
    close = pd.DataFrame({A: price, TNX: 4.0, IRX: 3.0, PIE: 2.0})
    panel = Panel(close.copy(), close)
    w = pd.DataFrame({A: [1.0]}, index=[idx[10]])                        # Signal an Tag 10
    res = run_backtest(panel, w, cost=CostModel(default_bps=0.0), rf=_rf(panel))
    # Handel zum Schluss von Tag 11 (110), danach nur der Sprung auf 121
    assert res.nav.iloc[11] == pytest.approx(1.0)
    assert res.nav.iloc[13] == pytest.approx(121.0 / 110.0)
