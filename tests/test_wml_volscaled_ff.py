"""Tests fuer wml_volscaled_ff auf synthetischen Daten (kein Netz, kein Datencache)."""
import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import NYSE_BDAY, month_end_flags
from qlab.data import Panel, panel_from_returns
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import wml_volscaled_ff as m

HI, LO = m.HI, m.LO
ZERO = CostModel(default_bps=0.0, short_fee_annual=0.0, lever_spread_annual=0.0)
VARIANTS = {"base": {}, **m.SPEC["variants"]}


# --------------------------------------------------------------------------------------
# Hilfen: synthetische Panels (NYSE-Handelstage, damit Monatsenden wie in echten Daten erkannt werden)
# --------------------------------------------------------------------------------------

def make_returns(n=2600, seed=7, start="2005-01-03", noise=1.0):
    """Tagesrenditen fuer Hi/Lo mit wechselnden Vol-Regimen (damit w variiert)."""
    idx = pd.date_range(start, periods=n, freq=NYSE_BDAY)
    rng = np.random.default_rng(seed)
    regime = np.where((np.arange(n) // 400) % 2 == 0, 1.0, 2.5)
    common = rng.normal(0.0, 0.008, n)
    hi = common + rng.normal(0.0005, 0.004, n) * regime * noise
    lo = common + rng.normal(0.0001, 0.007, n) * regime * noise
    return pd.DataFrame({HI: hi, LO: lo}, index=idx)


def make_panel(**kw):
    return panel_from_returns(make_returns(**kw))


def window_sigma(returns: pd.DataFrame, pos: int, lookback: int = 126) -> float:
    """sigma am Positionsindex `pos` direkt aus den Renditen (Referenz fuer die Formel)."""
    wml = (returns[HI] - returns[LO]).to_numpy()
    win = wml[pos - lookback + 1: pos + 1]
    return float(np.std(win, ddof=1) * np.sqrt(252))


# --------------------------------------------------------------------------------------
# Form, Wertebereich, Signaltage
# --------------------------------------------------------------------------------------

def test_shape_and_value_range():
    p = make_panel()
    w = m.weights(p)
    cap = m.SPEC["params"]["cap"]
    assert list(w.columns) == [HI, LO]
    assert len(w) > 100
    assert w.notna().all().all()
    assert (w[HI] > 0).all() and (w[LO] < 0).all()
    assert np.allclose(w[HI].to_numpy(), -w[LO].to_numpy())          # +w / -w, dollar-neutral
    assert (w[HI] <= cap + 1e-12).all()
    assert (w.abs().sum(axis=1) <= 2 * cap + 1e-12).all()             # Brutto-Exposure <= 2 * Deckel
    assert w.index.is_monotonic_increasing and w.index.is_unique


def test_weights_vary_with_volatility():
    w = m.weights(make_panel())
    assert w[HI].std() > 0.05                                        # Skalierung wirkt (Regimewechsel)


def test_signal_days_are_month_ends_only():
    p = make_panel()
    w = m.weights(p)
    flags = month_end_flags(p.close.index)
    assert flags.loc[w.index].all()
    assert not w.index.to_period("M").duplicated().any()              # hoechstens ein Signal pro Monat
    # nach dem Vorlauf ist JEDES Monatsende ein Signaltag
    first = w.index[0]
    all_ends = flags[flags].index
    assert list(w.index) == list(all_ends[all_ends >= first])


def test_first_signal_after_warmup():
    p = make_panel()
    idx = p.close.index
    w = m.weights(p)
    # Renditen gibt es ab Zeile 1 -> 126 Beobachtungen fruehestens in Zeile 126
    assert idx.get_loc(w.index[0]) >= 126
    earlier_month_ends = [d for d in idx[:126][month_end_flags(idx[:126]).to_numpy()]]
    assert all(d not in w.index for d in earlier_month_ends)


def test_first_signal_date_filter():
    p = make_panel()
    cut = p.close.index[1000]
    w = m.weights(p, first_signal=str(cut.date()))
    assert w.index.min() >= cut
    assert w.index.min() < cut + pd.Timedelta(days=40)                # kein Signal faellt weg, nur der Anfang


# --------------------------------------------------------------------------------------
# Formel und Fenster
# --------------------------------------------------------------------------------------

def test_weight_matches_manual_formula():
    r = make_returns()
    p = panel_from_returns(r)
    w = m.weights(p)
    idx = p.close.index
    for t in [w.index[0], w.index[7], w.index[-1]]:
        pos = idx.get_loc(t)
        sigma = window_sigma(r, pos)
        expected = min(0.12 / sigma, 2.0)
        assert w.loc[t, HI] == pytest.approx(expected, rel=1e-8)
        assert w.loc[t, LO] == pytest.approx(-expected, rel=1e-8)


def test_window_is_126_days_inclusive_of_t_and_excludes_future():
    r = make_returns()
    idx = r.index
    base = m.weights(panel_from_returns(r))
    t = base.index[20]
    pos = idx.get_loc(t)

    def w_at(r2):
        return m.weights(panel_from_returns(r2)).loc[t, HI]

    r_out = r.copy(); r_out.iloc[pos - 126, 0] += 0.2               # t-126: ausserhalb des Fensters
    r_in = r.copy(); r_in.iloc[pos - 125, 0] += 0.2                  # t-125: aeltester Tag im Fenster
    r_t = r.copy(); r_t.iloc[pos, 0] += 0.2                          # t selbst: im Fenster
    r_fut = r.copy(); r_fut.iloc[pos + 1:, :] += 0.05                # alles nach t
    assert w_at(r_out) == pytest.approx(base.loc[t, HI], rel=1e-9)
    assert w_at(r_fut) == pytest.approx(base.loc[t, HI], rel=1e-9)
    assert abs(w_at(r_in) - base.loc[t, HI]) > 1e-4
    assert abs(w_at(r_t) - base.loc[t, HI]) > 1e-4


def test_cap_binds_at_low_volatility():
    r = make_returns(noise=0.02)                                     # fast kein Idiosynkratik-Rauschen
    r[LO] = r[HI] + np.random.default_rng(1).normal(0, 0.0005, len(r))   # WML-Vol ~ 0.0005 * sqrt(252) ~ 0.8 %
    w = m.weights(panel_from_returns(r))
    assert (w[HI] == 2.0).all()
    w1 = m.weights(panel_from_returns(r), cap=1.0)
    assert (w1[HI] == 1.0).all()


# --------------------------------------------------------------------------------------
# Varianten
# --------------------------------------------------------------------------------------

def test_static_variant_is_w_one_on_same_signal_days():
    p = make_panel()
    base = m.weights(p)
    stat = m.weights(p, **m.SPEC["variants"]["static_w1"])
    assert list(stat.index) == list(base.index)
    assert (stat[HI] == 1.0).all() and (stat[LO] == -1.0).all()


def test_vol_target_19_scales_uncapped_weights():
    p = make_panel()
    raw12 = m.weights(p, cap=1e9)
    raw19 = m.weights(p, **{**m.SPEC["variants"]["vol_target_19"], "cap": 1e9})
    assert np.allclose(raw19[HI].to_numpy(), raw12[HI].to_numpy() * 0.19 / 0.12)
    capped = m.weights(p, **m.SPEC["variants"]["vol_target_19"])
    assert np.allclose(capped[HI].to_numpy(), np.minimum(raw19[HI].to_numpy(), 2.0))


def test_cap_one_variant_is_min_of_uncapped_and_one():
    p = make_panel()
    raw = m.weights(p, vol_target=0.30, cap=1e9)
    capped = m.weights(p, vol_target=0.30, **m.SPEC["variants"]["cap_1"])
    assert (raw[HI] > 1.0).any()                                     # Deckel greift wirklich
    assert np.allclose(capped[HI].to_numpy(), np.minimum(raw[HI].to_numpy(), 1.0))
    assert (capped[HI] <= 1.0).all()


# --------------------------------------------------------------------------------------
# NaN-Preise, Randfaelle
# --------------------------------------------------------------------------------------

def test_no_weights_on_nan_prices_or_incomplete_window():
    p = make_panel()
    close = p.close.copy()
    open_ = p.open.copy()
    close.iloc[:500, 1] = np.nan                                     # Lo PRIOR noch nicht verfuegbar
    close.iloc[1500:1520, 0] = np.nan                                # Luecke bei Hi PRIOR
    open_.iloc[:500, 1] = np.nan
    open_.iloc[1500:1520, 0] = np.nan
    pn = Panel(open_, close)
    w = m.weights(pn)
    idx = pn.close.index
    # an Signaltagen sind beide Kurse da
    assert pn.close.loc[w.index].notna().all().all()
    # kein Signal, bevor 126 gueltige WML-Renditen vorliegen
    assert idx.get_loc(w.index[0]) >= 500 + 126
    # kein Signal, solange die Luecke im 126-Tage-Fenster liegt
    bad = idx[1500:1520 + 126]
    assert not any(d in w.index for d in bad)
    # nach der Luecke wieder Signale
    assert (w.index > idx[1520 + 126]).any()
    # alle Zeilen komplett gefuellt (keine halben Signale)
    assert w.notna().all().all()


def test_empty_when_history_too_short():
    p = make_panel(n=100)
    w = m.weights(p)
    assert len(w) == 0
    assert list(w.columns) == [HI, LO]


def test_last_row_is_not_treated_as_month_end_unless_calendar_says_so():
    p = make_panel()
    w_full = m.weights(p)
    idx = p.close.index
    flags = month_end_flags(idx)
    mid = [d for d in idx[1000:1100] if not flags.loc[d]][5]         # Tag mitten im Monat
    wt = m.weights(p.truncate(mid))
    assert mid not in wt.index                                        # kein falsches Monatsende am Datenrand
    ends = w_full.index[10]                                           # echtes Monatsende
    assert ends in m.weights(p.truncate(ends)).index                  # ... aber ein echtes wird erkannt


# --------------------------------------------------------------------------------------
# Kausalitaet
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", list(VARIANTS))
def test_causality(name):
    p = make_panel()
    kw = VARIANTS[name]
    assert check_causality(lambda pp: m.weights(pp, **kw), p) == []


def test_causality_check_catches_lookahead_in_this_setup():
    """Tripwire: ein Blick in die Zukunft muss vom selben Test erkannt werden."""
    p = make_panel()
    base = m.weights(p)

    def peeking(pp):
        w = m.weights(pp)
        fut = pp.close[HI].shift(-3) / pp.close[HI] - 1.0
        return w * (1.0 + (fut.reindex(w.index) > 0).astype(float).to_numpy()[:, None])

    cuts = list(base.index[[10, 20, 30]])
    assert check_causality(peeking, p, cuts=cuts) != []


def test_perturbing_future_data_does_not_change_past_weights():
    r = make_returns()
    base = m.weights(panel_from_returns(r))
    cut = base.index[40]
    r2 = r.copy()
    r2.loc[r2.index > cut] = r2.loc[r2.index > cut].to_numpy() * -3.0 + 0.01
    pert = m.weights(panel_from_returns(r2))
    a, b = base.loc[:cut], pert.loc[:cut]
    assert list(a.index) == list(b.index)
    assert np.allclose(a.to_numpy(), b.to_numpy(), rtol=0, atol=1e-9)


# --------------------------------------------------------------------------------------
# Engine-Integration
# --------------------------------------------------------------------------------------

def test_engine_executes_next_day_at_target_weights():
    p = make_panel(n=900)
    w = m.weights(p)
    rf = pd.Series(0.0, index=p.close.index)
    res = run_backtest(p, w, cost=ZERO, rf=rf)
    idx = p.close.index
    t0 = w.index[0]
    nxt = idx[idx.get_loc(t0) + 1]
    assert res.weights.loc[t0, [HI, LO]].abs().max() == 0.0           # am Signaltag selbst noch nichts
    assert res.weights.loc[nxt, HI] == pytest.approx(w.loc[t0, HI], abs=1e-9)
    assert res.weights.loc[nxt, LO] == pytest.approx(w.loc[t0, LO], abs=1e-9)
    assert np.isfinite(res.nav).all() and (res.nav > 0).all()
    assert res.skipped_orders == 0
    assert (res.gross_exposure.loc[nxt] <= 2 * 2.0 + 1e-9)


def test_engine_runs_all_variants_without_ruin():
    p = make_panel(n=1500)
    rf = pd.Series(0.0, index=p.close.index)
    for kw in VARIANTS.values():
        res = run_backtest(p, m.weights(p, **kw), cost=ZERO, rf=rf)
        assert (res.nav > 0).all()
        assert res.skipped_orders == 0


# --------------------------------------------------------------------------------------
# Kosten-Kalibrierung, SPEC, load()
# --------------------------------------------------------------------------------------

def test_implied_cost_bps_reproduces_target_cost_on_synthetic_panel():
    p = make_panel()
    bps = m.implied_cost_bps(p)
    assert np.isfinite(bps) and bps > 0
    w = m.weights(p)
    cost = CostModel(per_ticker_bps={HI: bps, LO: bps}, default_bps=bps, short_fee_annual=0.0, lever_spread_annual=0.0)
    res = run_backtest(p, w, cost=cost, rf=pd.Series(0.0, index=p.close.index))
    target_total = m.MOM_COST_PER_MONTH * float(w[HI].sum())
    assert float(res.cost.sum()) == pytest.approx(target_total, rel=0.10)


def test_spec_contract():
    s = m.SPEC
    assert s["id"] == "wml_volscaled_ff" and s["family"] == "xsmom"
    assert 1 <= len(s["variants"]) <= 3
    assert "static_w1" in s["variants"]                              # Pflicht-Kontrolle
    params = set(inspect.signature(m.weights).parameters) - {"panel"}
    assert set(s["params"]) == params
    for vp in s["variants"].values():
        assert set(vp) <= params
    assert s["params"]["vol_target"] == 0.12 and s["params"]["lookback"] == 126 and s["params"]["cap"] == 2.0
    assert s["variants"]["vol_target_19"] == {"vol_target": 0.19}
    assert s["variants"]["cap_1"] == {"cap": 1.0}
    cb = s["cost_bps"]
    assert set(cb) == {HI, LO} and cb[HI] == cb[LO] > 5.0            # ersetzt die 5 bps Standard
    assert s["sources"] and s["start"]
    assert callable(m.load)


def test_load_builds_panel_from_french_value_weighted_table(monkeypatch):
    rng = np.random.default_rng(0)
    idx = pd.date_range("1930-01-01", periods=50, freq="B")
    cols = ["Lo PRIOR"] + [f"PRIOR {i}" for i in range(2, 10)] + ["Hi PRIOR"]
    fake = pd.DataFrame(rng.normal(0.0005, 0.01, (50, 10)), index=idx, columns=cols)
    calls = []

    def fake_french(name, daily=None, table=0, **kw):
        calls.append((name, table))
        return fake

    monkeypatch.setattr(m, "french", fake_french)
    p = m.load()
    assert calls == [("10_Portfolios_Prior_12_2_Daily", 0)]           # value-weighted = Tabelle 0
    assert p.tickers == [HI, LO]
    assert p.open.equals(p.close)                                     # panel_from_returns: open == close
    got = p.close[HI].pct_change().iloc[1:].to_numpy()
    assert np.allclose(got, fake[HI].iloc[1:].to_numpy(), atol=1e-12)
