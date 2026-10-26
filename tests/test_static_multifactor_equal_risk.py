"""Tests fuer static_multifactor_equal_risk auf synthetischen Daten (kein Netz, kein Datencache)."""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import NYSE_BDAY, month_end_flags
from qlab.data import Panel, panel_from_returns
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import static_multifactor_equal_risk as m

FAC = m.FACTORS
ZERO = CostModel(default_bps=0.0, short_fee_annual=0.0, lever_spread_annual=0.0)
VARIANTS = {"base": {}, **m.SPEC["variants"]}


# --------------------------------------------------------------------------------------
# Hilfen: synthetische Panels (NYSE-Handelstage, damit Monatsenden wie in echten Daten erkannt werden)
# --------------------------------------------------------------------------------------

def make_daily(n=3000, seed=7, start="2003-01-02", scale=1.0):
    """Tages-Ueberrenditen der 4 Faktoren (leicht korreliert, Vol-Regimewechsel alle 500 Tage) und RF."""
    idx = pd.date_range(start, periods=n, freq=NYSE_BDAY)
    rng = np.random.default_rng(seed)
    vols = np.array([0.0045, 0.0030, 0.0025, 0.0065]) * scale
    z = 0.8 * rng.normal(0, 1, (n, 4)) + 0.3 * rng.normal(0, 1, (n, 1))
    regime = np.where((np.arange(n) // 500) % 2 == 0, 1.0, 2.0)[:, None]
    mu = np.array([0.0002, 0.0002, 0.00015, 0.0003])
    f = pd.DataFrame(mu + z * vols * regime, index=idx, columns=FAC)
    rf = pd.Series(rng.uniform(0.00005, 0.0002, n), index=idx, name="RF")
    return f, rf


def to_panel(f: pd.DataFrame, rf: pd.Series) -> Panel:
    """Total-Return-Panel wie in load(): Faktor-Spalten = f + RF, plus RF-Spalte."""
    ret = f.add(rf, axis=0)
    ret["RF"] = rf
    return panel_from_returns(ret)


def make_panel(**kw) -> Panel:
    return to_panel(*make_daily(**kw))


def nan_panel(panel: Panel, col: str, rows: slice) -> Panel:
    close, open_ = panel.close.copy(), panel.open.copy()
    close.iloc[rows, close.columns.get_loc(col)] = np.nan
    open_.iloc[rows, open_.columns.get_loc(col)] = np.nan
    return Panel(open_, close)


def oracle_signals(close: pd.DataFrame, inverse_vol=True, target=0.10, cap=2.0, window=36, min_obs=24):
    """Unabhaengige, bewusst plumpe Referenz der Spezifikation (Pandas-Schleifen, Position = Kalendermonat).

    Rueckgabe: {Signaltag: (w, lev)}. Monatsrenditen = Produkt der Tages-Ueberrenditen; Monate mit fehlendem
    Tagespreis sind ungueltig; Fenster = Kalendermonate key-35..key; nur vollstaendige Monate zaehlen.
    """
    r = close / close.shift(1) - 1.0
    f = r[FAC].sub(r["RF"], axis=0)
    idx = f.index
    ym = pd.Series(idx.year * 12 + idx.month, index=idx)
    monthly = {}
    for key, g in f.groupby(ym):
        monthly[key] = np.full(4, np.nan) if g.isna().any().any() else ((1.0 + g).prod() - 1.0).to_numpy()
    ends = month_end_flags(idx, calendar_only=True)
    out = {}
    for t in idx[ends.to_numpy()]:
        if close.loc[t].isna().any():
            continue
        key = t.year * 12 + t.month
        if np.isnan(monthly[key]).any():
            continue
        win = pd.DataFrame([monthly[kk] for kk in range(key - window + 1, key + 1) if kk in monthly], columns=FAC).dropna()
        if len(win) < min_obs:
            continue
        vol = win.std(ddof=1) * np.sqrt(12)
        w = (1 / vol) / (1 / vol).sum() if inverse_vol else pd.Series(0.25, index=FAC)
        pv = float(np.sqrt(w.to_numpy() @ win.cov().to_numpy() @ w.to_numpy()) * np.sqrt(12))
        out[t] = (w.to_numpy(), min(cap, target / pv))
    return out


def assert_matches_oracle(panel: Panel, **kw):
    mk = {k: v for k, v in kw.items() if k in ("target_vol", "cap", "inverse_vol")}
    w = m.weights(panel, **kw)
    ok = {"target_vol": "target", "cap": "cap", "inverse_vol": "inverse_vol"}
    exp = oracle_signals(panel.close, **{ok[k]: v for k, v in mk.items()})
    assert list(w.index) == sorted(exp)
    for t in w.index:
        wt, lev = exp[t]
        assert np.allclose(w.loc[t].to_numpy(), lev * wt, rtol=1e-9, atol=1e-12)
    return w


# --------------------------------------------------------------------------------------
# Form, Wertebereich, Signaltage
# --------------------------------------------------------------------------------------

def test_shape_and_value_range():
    p = make_panel()
    w = m.weights(p)
    cap = m.SPEC["params"]["cap"]
    assert list(w.columns) == FAC                                     # kein Gewicht auf RF
    assert len(w) > 50
    assert w.notna().all().all()
    assert (w > 0).all().all()                                        # nur Long auf den Faktor-Reihen
    assert (w.sum(axis=1) <= cap + 1e-12).all()                       # Brutto-Exposure <= Deckel
    assert w.index.is_monotonic_increasing and w.index.is_unique
    assert set(w.index) <= set(p.close.index)


def test_signal_days_are_month_ends_only():
    p = make_panel()
    w = m.weights(p)
    flags = month_end_flags(p.close.index)
    assert flags.loc[w.index].all()
    assert not w.index.to_period("M").duplicated().any()              # hoechstens ein Signal pro Monat
    first = w.index[0]
    all_ends = flags[flags].index
    assert list(w.index) == list(all_ends[all_ends >= first])         # nach dem Vorlauf jedes Monatsende


def test_first_signal_after_24_complete_months():
    p = make_panel()
    idx = p.close.index
    w = m.weights(p)
    # Monat der ersten Datenzeile ist wegen fehlender Vortagsrendite ungueltig -> erste volle Historie nach 24 weiteren
    first_month = idx[0].year * 12 + idx[0].month
    sig_month = w.index[0].year * 12 + w.index[0].month
    assert sig_month - first_month == 24
    assert w.index[0] == idx[(idx.year * 12 + idx.month == sig_month)][-1]       # Monatsende dieses Monats


def test_first_signal_date_filter():
    p = make_panel()
    cut = p.close.index[1500]
    w = m.weights(p, first_signal=str(cut.date()))
    assert w.index.min() >= cut
    assert w.index.min() < cut + pd.Timedelta(days=40)                # nur der Anfang faellt weg
    full = m.weights(p, first_signal=None)
    assert list(w.index) == list(full.index[full.index >= cut])


def test_default_first_signal_is_1966_06():
    assert m.FIRST_SIGNAL == "1966-06-01" and m.SPEC["params"]["first_signal"] == "1966-06-01"
    f, rf = make_daily(n=800, start="1963-07-01")                      # 1963-07-01 = Montag (kein Feiertag)
    p = to_panel(f, rf)
    w = m.weights(p, first_signal="1963-07-01")
    assert w.index[0] == pd.Timestamp("1965-07-30")                    # 24 volle Monate 1963-08..1965-07, dessen Monatsende
    w2 = m.weights(p)                                                  # Default: erstes Signal 1966-06-30 (Daten bis ca. 1966-07)
    assert len(w2) >= 1 and w2.index[0] == pd.Timestamp("1966-06-30")


# --------------------------------------------------------------------------------------
# Formel, Fenster, Gewichte
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", list(VARIANTS))
def test_weights_match_independent_oracle(name):
    p = make_panel()
    kw = VARIANTS[name]
    assert_matches_oracle(p, **kw)
    assert_matches_oracle(make_panel(seed=3, scale=2.0), **kw)


def test_inverse_vol_gives_equal_risk_weights():
    p = make_panel()
    w = m.weights(p)
    t = w.index[30]
    r = p.close / p.close.shift(1) - 1.0
    f = r[FAC].sub(r["RF"], axis=0)
    ym = f.index.year * 12 + f.index.month
    monthly = (1.0 + f).groupby(ym).prod() - 1.0
    key = t.year * 12 + t.month
    win = monthly.loc[key - 35:key]
    vol = win.std(ddof=1) * np.sqrt(12)
    share = w.loc[t] / w.loc[t].sum()
    assert np.allclose((share * vol).to_numpy(), (share * vol).iloc[0])  # w_i * vol_i konstant
    assert share.idxmax() == vol.idxmin() and share.idxmin() == vol.idxmax()
    assert share.sum() == pytest.approx(1.0)


def test_leverage_caps_and_vol_target():
    # sehr ruhige Faktoren -> Deckel bindet; Deckel 1 -> Brutto 1
    calm = make_panel(scale=0.1)
    w = m.weights(calm)
    assert np.allclose(w.sum(axis=1), 2.0)
    assert np.allclose(m.weights(calm, cap=1.0).sum(axis=1), 1.0)
    # sehr unruhige Faktoren -> Ziel-Vol bindet (lev < 1) und trifft 10 % Portfolio-Vol
    wild = make_panel(scale=4.0)
    ww = m.weights(wild)
    assert (ww.sum(axis=1) < 1.0).all()
    t = ww.index[35]
    r = wild.close / wild.close.shift(1) - 1.0
    f = r[FAC].sub(r["RF"], axis=0)
    ym = f.index.year * 12 + f.index.month
    monthly = (1.0 + f).groupby(ym).prod() - 1.0
    key = t.year * 12 + t.month
    win = monthly.loc[key - 35:key]
    port_vol = float(np.sqrt(ww.loc[t].to_numpy() @ win.cov().to_numpy() @ ww.loc[t].to_numpy()) * np.sqrt(12))
    assert port_vol == pytest.approx(0.10, rel=1e-9)
    assert ww.sum(axis=1).std() > 0.02                                 # Hebel variiert mit dem Vol-Regime


def test_equal_weight_variant_uses_quarter_weights_and_same_signal_days():
    p = make_panel()
    base = m.weights(p)
    ew = m.weights(p, **m.SPEC["variants"]["equal_weight"])
    assert list(ew.index) == list(base.index)
    share = ew.div(ew.sum(axis=1), axis=0)
    assert np.allclose(share.to_numpy(), 0.25)
    assert not np.allclose(base.to_numpy(), ew.to_numpy())             # Inverse-Vol wirkt tatsaechlich anders


def test_window_is_36_months_inclusive_of_t_and_excludes_future():
    f, rf = make_daily()
    p = to_panel(f, rf)
    base = m.weights(p)
    t = base.index[40]
    idx = f.index
    key = t.year * 12 + t.month
    ym = idx.year * 12 + idx.month

    def w_at(day_key=None, after=False):
        f2 = f.copy()
        if after:
            f2.loc[f2.index > t, "HML"] += 0.03
        else:
            day = idx[ym == day_key][5]
            f2.loc[day, "HML"] += 0.05
        return m.weights(to_panel(f2, rf)).loc[t]

    assert np.allclose(w_at(key - 36), base.loc[t], rtol=0, atol=1e-10)    # t-36: ausserhalb des Fensters
    assert np.allclose(w_at(after=True), base.loc[t], rtol=0, atol=1e-10)   # alles nach t
    assert np.abs(w_at(key - 35) - base.loc[t]).max() > 1e-4                # aeltester Monat im Fenster
    assert np.abs(w_at(key) - base.loc[t]).max() > 1e-4                     # Monat von t selbst


def test_monthly_factor_returns_compounding_and_missing_days():
    idx = pd.date_range("2010-01-04", periods=130, freq=NYSE_BDAY)
    ret = pd.DataFrame({"HML": 0.001, "RMW": 0.002, "CMA": -0.001, "Mom": 0.0, "RF": 0.0001}, index=idx)
    # Faktor-Total-Return = f + RF -> Ueberrendite f = konstant
    ret[FAC] = ret[FAC].add(ret["RF"], axis=0)
    close = panel_from_returns(ret).close
    mon = m.monthly_factor_returns(close)
    assert isinstance(mon.index, pd.PeriodIndex) and list(mon.columns) == FAC
    assert mon.iloc[0].isna().all()                                    # erster Monat: erste Zeile ohne Vortagsrendite
    days = pd.Series(1, index=idx).groupby(idx.to_period("M")).sum()
    full = mon.iloc[1:-1]                                              # vollstaendige Monate
    for col, c in (("HML", 0.001), ("RMW", 0.002), ("CMA", -0.001), ("Mom", 0.0)):
        exp = (1 + c) ** days.iloc[1:-1] - 1
        assert np.allclose(full[col].to_numpy(), exp.to_numpy(), atol=1e-12)
    # fehlender Tageskurs macht den Monat der betroffenen Spalte ungueltig (NaN), die anderen Faktoren bleiben gueltig
    c2 = close.copy()
    c2.iloc[40, c2.columns.get_loc("RMW")] = np.nan
    mon2 = m.monthly_factor_returns(c2)
    bad = [idx[40].to_period("M"), idx[41].to_period("M")]
    assert mon2.loc[bad[0], "RMW"] != mon2.loc[bad[0], "RMW"]          # NaN
    assert mon2.loc[bad[0], ["HML", "CMA", "Mom"]].notna().all()


# --------------------------------------------------------------------------------------
# NaN-Preise, Randfaelle
# --------------------------------------------------------------------------------------

def test_no_weights_on_nan_prices_and_incomplete_history():
    p = make_panel()
    idx = p.close.index
    pn = nan_panel(p, "Mom", slice(0, 600))                            # Momentum noch nicht verfuegbar
    pn = nan_panel(pn, "RMW", slice(1500, 1560))                       # Luecke mitten in der Reihe
    w = assert_matches_oracle(pn)
    assert pn.close.loc[w.index].notna().all().all()                   # an Signaltagen sind alle Kurse da
    # kein Signal vor 24 vollstaendigen Mom-Monaten
    mom_first_ret = idx[601]
    assert (w.index[0].year * 12 + w.index[0].month) - (mom_first_ret.year * 12 + mom_first_ret.month) >= 23
    # keine Signale in den Monaten der Luecke
    gap_months = {(d.year, d.month) for d in idx[1500:1561]}
    assert not any((d.year, d.month) in gap_months for d in w.index)
    # danach wieder Signale, obwohl die Luecke noch im Fenster liegt (>= 24 vollstaendige Monate genuegen)
    assert (w.index > idx[1561] + pd.Timedelta(days=200)).any()
    assert w.notna().all().all()


def test_nan_price_at_signal_day_blocks_that_day():
    p = make_panel()
    w = m.weights(p)
    t = w.index[10]
    pos = p.close.index.get_loc(t)
    pn = nan_panel(p, "CMA", slice(pos, pos + 1))
    w2 = m.weights(pn)
    assert t not in w2.index
    assert pn.close.loc[w2.index].notna().all().all()


def test_empty_when_history_too_short():
    p = make_panel(n=300)                                              # ca. 14 Monate
    w = m.weights(p)
    assert len(w) == 0
    assert list(w.columns) == FAC
    assert len(m.weights(make_panel(n=2))) == 0


def test_last_row_is_not_treated_as_month_end_unless_calendar_says_so():
    p = make_panel()
    w_full = m.weights(p)
    idx = p.close.index
    flags = month_end_flags(idx)
    mid = [d for d in idx[1500:1600] if not flags.loc[d]][5]
    assert mid not in m.weights(p.truncate(mid)).index                  # kein falsches Monatsende am Datenrand
    ends = w_full.index[10]
    assert ends in m.weights(p.truncate(ends)).index                    # ... aber ein echtes wird erkannt


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
        fut = pp.close["HML"].shift(-3) / pp.close["HML"] - 1.0
        return w * (1.0 + (fut.reindex(w.index) > 0).astype(float).to_numpy()[:, None])

    cuts = list(base.index[[10, 20, 30]])
    assert check_causality(peeking, p, cuts=cuts) != []


def test_perturbing_future_data_does_not_change_past_weights():
    f, rf = make_daily()
    base = m.weights(to_panel(f, rf))
    cut = base.index[40]
    f2 = f.copy()
    f2.loc[f2.index > cut] = f2.loc[f2.index > cut].to_numpy() * -3.0 + 0.01
    pert = m.weights(to_panel(f2, rf))
    a, b = base.loc[:cut], pert.loc[:cut]
    assert list(a.index) == list(b.index)
    assert np.allclose(a.to_numpy(), b.to_numpy(), rtol=0, atol=1e-9)


# --------------------------------------------------------------------------------------
# Engine-Integration
# --------------------------------------------------------------------------------------

def test_engine_executes_next_day_at_target_weights():
    p = make_panel(n=1200)
    w = m.weights(p)
    rf = pd.Series(0.0, index=p.close.index)
    res = run_backtest(p, w, cost=ZERO, rf=rf)
    idx = p.close.index
    t0 = w.index[0]
    nxt = idx[idx.get_loc(t0) + 1]
    assert res.weights.loc[t0, FAC].abs().max() == 0.0                  # am Signaltag selbst noch nichts
    assert np.allclose(res.weights.loc[nxt, FAC].to_numpy(), w.loc[t0].to_numpy(), atol=1e-9)
    assert res.weights.loc[nxt, "RF"] == 0.0                            # nie ein Gewicht auf RF
    assert np.isfinite(res.nav).all() and (res.nav > 0).all()
    assert res.skipped_orders == 0


def test_engine_excess_return_equals_weighted_factor_return():
    """Total-Return-Aufbau: Engine-Rendite - RF == sum(Gewicht_Vortag * Faktor-Ueberrendite), auch bei lev > 1."""
    f, rf = make_daily(n=1800, scale=2.0)
    p = to_panel(f, rf)
    w = m.weights(p)
    assert (w.sum(axis=1) > 1.0).any() and (w.sum(axis=1) < 1.0).any()  # beide Faelle kommen vor
    res = run_backtest(p, w, cost=ZERO, rf=rf)                          # Hebel-Aufschlag 0 in ZERO
    prev_w = res.weights[FAC].shift(1)
    expected = (prev_w * f).sum(axis=1)
    got = res.ret - rf
    assert np.allclose(got.iloc[2:].to_numpy(), expected.iloc[2:].to_numpy(), rtol=0, atol=1e-10)


def test_engine_charges_lever_spread_only_on_borrowed_part():
    f, rf = make_daily(n=1800, scale=2.0)
    p = to_panel(f, rf)
    w = m.weights(p)
    assert (w.sum(axis=1) > 1.0).any()
    cost = CostModel(default_bps=0.0, short_fee_annual=0.0, lever_spread_annual=0.015)
    res = run_backtest(p, w, cost=cost, rf=rf)
    prev_w = res.weights[FAC].shift(1)
    borrowed = (prev_w.sum(axis=1) - 1.0).clip(lower=0.0)
    expected = (prev_w * f).sum(axis=1) - borrowed * 0.015 / 252
    assert np.allclose((res.ret - rf).iloc[2:].to_numpy(), expected.iloc[2:].to_numpy(), rtol=0, atol=1e-10)
    assert (res.gross_exposure <= 2.0 * 1.25).all()                     # Drift zwischen den Rebalancings bleibt klein


def test_engine_runs_all_variants_without_ruin():
    p = make_panel(n=1800)
    rf = pd.Series(0.0, index=p.close.index)
    for kw in VARIANTS.values():
        res = run_backtest(p, m.weights(p, **kw), cost=ZERO, rf=rf)
        assert (res.nav > 0).all()
        assert res.skipped_orders == 0


# --------------------------------------------------------------------------------------
# Referenz auf Monatsdaten, Kosten-Kalibrierung
# --------------------------------------------------------------------------------------

def _monthly_inputs(scale=2.0):
    f, rf = make_daily(scale=scale)
    p = to_panel(f, rf)
    mon = m.monthly_factor_returns(p.close)
    ym = rf.index.to_period("M")
    rfm = (1.0 + rf).groupby(ym).prod() - 1.0
    return p, mon, rfm


def test_reference_net_return_formula():
    p, mon, rfm = _monthly_inputs()
    ref = m.reference_monthly_returns(mon, rfm)
    assert (ref["lev"] > 1.0).any() and (ref["lev"] <= 1.0).any()
    for hc in (0.0, 0.02, 0.04):
        r = m.reference_monthly_returns(mon, rfm, haircut=hc)
        for pos in (0, len(r) // 2, len(r) - 2):
            month = r.index[pos]
            lev, gross = r.iloc[pos]["lev"], r.iloc[pos]["gross"]
            fin = (lev - 1.0) * (rfm.loc[month] + 0.005 / 12) if lev > 1.0 else 0.0
            assert r.iloc[pos]["net"] == pytest.approx(gross - hc / 12 - fin, abs=1e-14)
    # eine Zeile komplett von Hand: Gewichte aus den 36 Monaten bis zum Vormonat
    month = ref.index[len(ref) // 2]
    k = list(mon.index).index(month) - 1
    win = mon.iloc[k - 35:k + 1].dropna()
    vol = win.std(ddof=1) * np.sqrt(12)
    w = (1 / vol) / (1 / vol).sum()
    lev = min(2.0, 0.10 / float(np.sqrt(w.to_numpy() @ win.cov().to_numpy() @ w.to_numpy()) * np.sqrt(12)))
    gross = lev * float((w * mon.loc[month]).sum())
    assert ref.loc[month, "lev"] == pytest.approx(lev, rel=1e-12)
    assert ref.loc[month, "gross"] == pytest.approx(gross, rel=1e-12)


def test_reference_leverage_matches_weights_signals():
    p, mon, rfm = _monthly_inputs()
    ref = m.reference_monthly_returns(mon, rfm)
    for name, kw in VARIANTS.items():
        w = m.weights(p, **kw)
        r = m.reference_monthly_returns(mon, rfm, **kw)
        for t in w.index[:-1]:
            nxt = t.to_period("M") + 1
            assert r.loc[nxt, "lev"] == pytest.approx(float(w.loc[t].sum()), rel=1e-10)
    assert len(ref) > 50


def test_implied_cost_bps_reproduces_haircut_on_synthetic_panel():
    p = make_panel()
    bps = m.implied_cost_bps(p)
    assert np.isfinite(bps) and bps > 0
    w = m.weights(p)
    cost = CostModel(per_ticker_bps={f: bps for f in FAC}, default_bps=bps, short_fee_annual=0.0, lever_spread_annual=0.0)
    res = run_backtest(p, w, cost=cost, rf=pd.Series(0.0, index=p.close.index))
    years = (p.close.index[-1] - w.index[0]).days / 365.25
    assert float(res.cost.sum()) == pytest.approx(0.02 * years, rel=0.12)
    assert np.isnan(m.implied_cost_bps(make_panel(n=300)))


# --------------------------------------------------------------------------------------
# SPEC, load()
# --------------------------------------------------------------------------------------

def test_spec_contract():
    s = m.SPEC
    assert s["id"] == "static_multifactor_equal_risk" and s["family"] == "factors"
    assert 1 <= len(s["variants"]) <= 3
    params = set(inspect.signature(m.weights).parameters) - {"panel"}
    assert set(s["params"]) == params
    for vp in s["variants"].values():
        assert set(vp) <= params
    p = s["params"]
    assert (p["window"], p["min_obs"], p["target_vol"], p["cap"], p["inverse_vol"]) == (36, 24, 0.10, 2.0, True)
    assert s["variants"]["equal_weight"] == {"inverse_vol": False}
    cb = s["cost_bps"]
    assert set(cb) == set(FAC) and len(set(cb.values())) == 1 and cb["HML"] == m.CALIBRATED_COST_BPS > 5.0
    assert s["sources"] and s["start"] == "1966-06-01"
    assert callable(m.load)


def test_load_builds_total_return_panel_from_french_daily(monkeypatch):
    rng = np.random.default_rng(0)
    idx = pd.date_range("1963-07-01", periods=60, freq="B")
    d5 = pd.DataFrame(rng.normal(0.0003, 0.005, (60, 6)), index=idx, columns=["Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF"])
    d5["RF"] = 0.0001
    idx_mom = pd.date_range("1963-01-01", periods=300, freq="B")             # Mom beginnt frueher -> innerer Join
    mom = pd.DataFrame({"Mom": rng.normal(0.0004, 0.007, 300)}, index=idx_mom)
    calls = []

    def fake_french(name, daily=None, table=0, **kw):
        calls.append((name, daily))
        return d5 if "5_Factors" in name else mom

    monkeypatch.setattr(m, "french", fake_french)
    p = m.load()
    assert calls == [("F-F_Research_Data_5_Factors_2x3", True), ("F-F_Momentum_Factor", True)]
    assert p.tickers == FAC + ["RF"]
    assert p.open.equals(p.close)                                          # panel_from_returns: open == close
    assert p.close.index.min() == idx.min() and p.close.index.max() == idx.max()
    got = (p.close / p.close.shift(1) - 1.0).iloc[1:]
    both = idx.intersection(idx_mom)
    exp_hml = d5.loc[both, "HML"] + d5.loc[both, "RF"]
    assert np.allclose(got["HML"].to_numpy(), exp_hml.iloc[1:].to_numpy(), atol=1e-12)
    exp_mom = mom.loc[both, "Mom"] + d5.loc[both, "RF"]
    assert np.allclose(got["Mom"].to_numpy(), exp_mom.iloc[1:].to_numpy(), atol=1e-12)
    assert np.allclose(got["RF"].to_numpy(), 0.0001, atol=1e-12)
