"""Tests fuer lowvol_defensive_longonly_etf (USMV/SPLV Buy&Hold, Sektor-Proxy) auf synthetischen Daten.

Kein Netz, kein Datencache. Die Sektoren haben feste, klar getrennte Tagesvolatilitaeten, damit die erwartete
Auswahl (die drei ruhigsten Sektoren) eindeutig ist.
"""
import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import NYSE_BDAY, month_end_flags, week_end_flags
from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import lowvol_defensive_longonly_etf as m

SECTORS = m.SECTORS
ZERO = CostModel(default_bps=0.0, short_fee_annual=0.0, lever_spread_annual=0.0)
VARIANTS = {"base": {}, **m.SPEC["variants"]}
# Tagesvolatilitaet je Sektor; die drei kleinsten: XLP, XLU, XLV (deutlicher Abstand zum vierten)
SIGMA = {"XLP": 0.005, "XLU": 0.006, "XLV": 0.007, "XLE": 0.012, "XLB": 0.0135, "XLI": 0.015,
         "XLF": 0.0165, "XLK": 0.018, "XLY": 0.020}
CALM = {"XLP", "XLU", "XLV"}


def make_panel(seed=0, start="2003-01-02", end="2012-12-31", listing=None, xlk_switch=None):
    """12 Reihen auf dem NYSE-Kalender: 9 Sektoren, USMV, SPLV, SPY. `listing`: {Ticker: erster Kurstag}."""
    idx = pd.date_range(start, end, freq=NYSE_BDAY)
    n = len(idx)
    rng = np.random.default_rng(seed)
    sig = {t: np.full(n, s) for t, s in SIGMA.items()}
    sig.update({"USMV": np.full(n, 0.008), "SPLV": np.full(n, 0.007), "SPY": np.full(n, 0.011)})
    if xlk_switch is not None:
        sig["XLK"] = np.where(idx >= pd.Timestamp(xlk_switch), 0.003, SIGMA["XLK"])
    close = pd.DataFrame({t: 100.0 * np.exp(np.cumsum(rng.normal(0.0003, s))) for t, s in sig.items()}, index=idx)
    open_ = close.shift(1) * (1.0 + rng.normal(0.0, 0.001, close.shape))
    open_.iloc[0] = close.iloc[0]
    for t, d in (listing or {}).items():
        close.loc[close.index < d, t] = np.nan
    open_ = open_.where(close.notna())
    return Panel(open_, close)


@pytest.fixture(scope="module")
def panel():
    return make_panel(seed=7)


def ref_weekly_vol(close: pd.DataFrame, t, lookback=156) -> pd.Series:
    """Unabhaengige Referenz: Wochenschluesse (Kalenderjahr, ISO-Jahr, ISO-Woche) aus den VOLLEN Daten, nur Wochen mit Ende <= t.

    Wie qlab.calendar.week_end_flags beginnt auch an jedem Jahreswechsel eine neue (kurze) Woche."""
    iso = close.index.isocalendar()
    key = pd.MultiIndex.from_arrays([close.index.year, iso["year"].to_numpy(), iso["week"].to_numpy()])
    ends = pd.DatetimeIndex(pd.Series(close.index, index=key).groupby(level=[0, 1, 2]).max().to_numpy()).sort_values()
    ends = ends[ends <= t]
    wc = close.loc[ends]
    wr = (wc / wc.shift(1) - 1.0).iloc[1:]
    return wr.iloc[-lookback:].std(ddof=1)


# --------------------------------------------------------------------------------------
# SPEC
# --------------------------------------------------------------------------------------

def test_spec_contract():
    s = m.SPEC
    assert s["id"] == "lowvol_defensive_longonly_etf" and s["family"] == "lowrisk"
    assert m.SECTORS == ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]
    assert "XLRE" not in s["tickers"] and "XLC" not in s["tickers"]      # Universum konstant
    assert s["tickers"] == ["USMV", "SPLV", "SPY"] + m.SECTORS
    assert s["start"] == "1998-12-22"
    assert 1 <= len(s["variants"]) <= 3 and set(s["variants"]) == {"splv", "sector_proxy"}
    params = set(inspect.signature(m.weights).parameters) - {"panel"}
    assert set(s["params"]) == params
    for vp in s["variants"].values():
        assert set(vp) <= params
    assert s["params"] == {"mode": "hold", "asset": "USMV", "lookback_weeks": 156, "top_n": 3}
    assert s["variants"]["splv"] == {"asset": "SPLV"} and s["variants"]["sector_proxy"] == {"mode": "sector_lowvol"}
    assert s["sources"]


def test_unknown_mode_raises(panel):
    with pytest.raises(ValueError):
        m.weights(panel, mode="nope")


# --------------------------------------------------------------------------------------
# Buy&Hold (Basis und SPLV-Variante)
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("asset,variant", [("USMV", "base"), ("SPLV", "splv")])
def test_hold_is_single_row_at_first_valid_price(asset, variant):
    listing = {"USMV": pd.Timestamp("2006-03-01"), "SPLV": pd.Timestamp("2005-06-01")}
    p = make_panel(seed=3, listing=listing)
    kw = VARIANTS[variant]
    w = m.weights(p, **kw)
    first = p.close[asset].first_valid_index()
    assert first == listing[asset]
    assert list(w.columns) == [asset] and list(w.index) == [first]
    assert w.iloc[0, 0] == 1.0                                           # 100 %, kein Hebel, kein Cash
    assert np.isfinite(p.close.loc[w.index, asset]).all()                # nie auf einen NaN-Kurs
    assert first > p.close.index[0]                                      # erst ab Auflage, nicht ab Panelbeginn


def test_hold_empty_without_prices():
    p = make_panel(seed=3)
    close = p.close.copy()
    close["USMV"] = np.nan
    w = m.weights(Panel(p.open.copy(), close))
    assert len(w) == 0 and list(w.columns) == ["USMV"]


def test_hold_engine_buys_next_open_and_holds_only_the_asset():
    listing = {"USMV": pd.Timestamp("2006-03-01")}
    p = make_panel(seed=3, listing=listing)
    w = m.weights(p)
    res = run_backtest(p, w, cost=ZERO, rf=pd.Series(0.0, index=p.close.index))
    idx = p.close.index
    t0 = w.index[0]
    nxt = idx[idx.get_loc(t0) + 1]
    assert res.weights.loc[:t0].abs().to_numpy().max() == 0.0            # davor / am Signaltag nichts
    assert res.weights.loc[nxt, "USMV"] == pytest.approx(1.0, abs=1e-12)
    assert res.weights.drop(columns=["USMV"]).abs().to_numpy().max() == 0.0
    assert res.skipped_orders == 0 and res.n_trades == 1
    assert np.isfinite(res.nav).all() and (res.nav > 0).all()
    # NAV folgt dem Fonds ab dem Kaufkurs (Eroeffnung t+1)
    expect = p.close.loc[idx[-1], "USMV"] / p.open.loc[nxt, "USMV"]
    assert res.nav.iloc[-1] == pytest.approx(expect, rel=1e-9)


# --------------------------------------------------------------------------------------
# Sektor-Proxy (Variante B): Wochenvolatilitaet
# --------------------------------------------------------------------------------------

def test_weekly_vol_matches_independent_reference(panel):
    close = panel.close[SECTORS]
    vol = m.weekly_vol(close)
    idx = close.index
    flags_w = week_end_flags(idx)
    flags_m = month_end_flags(idx)
    midweek = [d for d in idx[1200:1300] if not flags_w.loc[d]][0]       # Tag mitten in der Woche
    wkend = [d for d in idx[1300:1400] if flags_w.loc[d]][0]
    mend = [d for d in idx[1500:1600] if flags_m.loc[d]][0]
    for t in (midweek, wkend, mend, idx[-1]):
        got = vol.loc[t]
        ref = ref_weekly_vol(close, t)
        assert np.allclose(got.to_numpy(), ref.reindex(SECTORS).to_numpy(), rtol=1e-10), t


def test_weekly_vol_window_is_156_weeks_and_ignores_the_future(panel):
    close = panel.close[SECTORS].copy()
    idx = close.index
    wk = week_end_flags(idx).to_numpy()
    wdates = idx[wk]
    j = 400                                                              # Wochenschluss Nr. j als Bezug
    t = wdates[j]
    base = m.weekly_vol(close).loc[t, "XLP"]

    def vol_with(change_at):
        c = close.copy()
        c.loc[change_at, "XLP"] *= 1.25
        return m.weekly_vol(c).loc[t, "XLP"]

    assert vol_with(wdates[j - 157]) == pytest.approx(base, rel=1e-12)   # 157 Schluesse zurueck: ausserhalb
    assert abs(vol_with(wdates[j - 156]) - base) > 1e-6                  # aeltester Schluss im Fenster
    assert abs(vol_with(wdates[j]) - base) > 1e-6                        # Schluss von t selbst
    c2 = close.copy()
    c2.loc[c2.index > t, :] *= 7.0                                       # alles nach t veraendern
    assert m.weekly_vol(c2).loc[t, "XLP"] == pytest.approx(base, rel=1e-12)


def test_weekly_vol_needs_full_window_and_never_fills_gaps(panel):
    close = panel.close[SECTORS]
    vol = m.weekly_vol(close)
    wk = week_end_flags(close.index).to_numpy()
    wdates = close.index[wk]
    first_ok = vol.dropna(how="any").index[0]
    assert first_ok == wdates[156]                                       # 157 Schluesse = 156 Wochenrenditen
    assert vol.loc[:wdates[155]].isna().all().all()
    gap = close.copy()
    k = 200
    gap.loc[wdates[k], "XLP"] = np.nan                                   # ein fehlender Wochenschluss
    vg = m.weekly_vol(gap)["XLP"]
    assert vg.loc[wdates[k]:wdates[k + 156 - 1]].isna().all()            # 156 Wochen lang kein Wert (kein Auffuellen)
    assert np.isfinite(vg.loc[wdates[k + 157]])


def test_sector_shape_value_range_and_month_ends_only(panel):
    w = m.weights(panel, **m.SPEC["variants"]["sector_proxy"])
    assert list(w.columns) == SECTORS                                    # nur Sektoren, nie SPY/USMV/SPLV
    assert len(w) > 60 and not w.isna().any().any()
    assert np.allclose(w.sum(axis=1), 1.0)                               # voll investiert, kein Hebel
    assert ((w == 0.0) | np.isclose(w, 1.0 / 3.0)).all().all()
    assert ((w > 0).sum(axis=1) == 3).all()
    flags = month_end_flags(panel.close.index)
    assert flags.loc[w.index].all()
    assert not w.index.to_period("M").duplicated().any()                 # hoechstens ein Signal pro Monat
    assert w.index.is_monotonic_increasing and w.index.is_unique


def test_sector_picks_the_three_calmest_sectors(panel):
    w = m.weights(panel, mode="sector_lowvol")
    held = w.gt(0).apply(lambda r: set(r.index[r]), axis=1)
    assert all(h == CALM for h in held)
    w5 = m.weights(panel, mode="sector_lowvol", top_n=5)
    assert np.allclose(w5.sum(axis=1), 1.0) and ((w5 > 0).sum(axis=1) == 5).all()
    assert np.allclose(w5.to_numpy()[w5.to_numpy() > 0], 0.2)
    assert all(CALM <= set(r.index[r > 0]) for _, r in w5.iterrows())


def test_sector_first_signal_is_first_month_end_after_156_weeks(panel):
    w = m.weights(panel, mode="sector_lowvol")
    idx = panel.close.index
    wk = week_end_flags(idx).to_numpy()
    first_vol_day = idx[wk][156]
    flags = month_end_flags(idx)
    expected = flags[flags & (flags.index >= first_vol_day)].index[0]
    assert w.index[0] == expected


def test_sector_selection_follows_a_volatility_regime_change():
    p = make_panel(seed=4, xlk_switch="2007-01-01")                      # XLK wird ab 2007 zum ruhigsten Sektor
    w = m.weights(p, mode="sector_lowvol")
    early = w.loc[:"2006-12-31"]
    late = w.loc["2010-03-01":]                                          # Fenster (3 Jahre) liegt komplett nach dem Wechsel
    assert len(early) > 5 and len(late) > 20
    assert (early["XLK"] == 0.0).all()
    assert (late["XLK"] > 0).all()
    assert np.allclose(late.sum(axis=1), 1.0) and ((late > 0).sum(axis=1) == 3).all()


def test_sector_no_signal_until_all_nine_have_a_full_window_and_no_weight_on_nan():
    listing = {"XLY": pd.Timestamp("2005-03-01")}
    p = make_panel(seed=5, start="2003-01-02", end="2012-12-31", listing=listing)
    w = m.weights(p, mode="sector_lowvol")
    idx = p.close.index
    first_y = p.close["XLY"].first_valid_index()
    wk = week_end_flags(idx)
    own_week_ends = idx[wk.to_numpy() & (idx >= first_y)]
    flags = month_end_flags(idx)
    expected = flags[flags & (flags.index >= own_week_ends[156])].index[0]   # 156 Wochenrenditen ab dem ersten XLY-Kurs
    assert w.index[0] == expected
    assert w.index[0] > first_y + pd.Timedelta(weeks=150)
    assert p.close.loc[w.index, SECTORS].notna().all().all()
    assert not w.isna().any().any()


def test_sector_month_end_without_price_gets_no_signal(panel):
    idx = panel.close.index
    wk, me = week_end_flags(idx), month_end_flags(idx)
    base = m.weights(panel, mode="sector_lowvol")
    cand = [d for d in base.index[10:40] if not wk.loc[d]]               # Monatsende, das kein Wochenschluss ist
    assert cand, "synthetische Daten brauchen ein Monatsende mitten in der Woche"
    d = cand[0]
    close = panel.close.copy()
    close.loc[d, "XLP"] = np.nan                                         # ein Sektor ohne Kurs genau am Signaltag
    open_ = panel.open.where(close.notna())
    w = m.weights(Panel(open_, close), mode="sector_lowvol")
    assert d not in w.index                                              # nichts auf einen nicht handelbaren Kurs
    assert d in base.index
    nb = base.index[base.index.get_loc(d) + 1]
    assert nb in w.index


def test_last_row_is_not_treated_as_month_end_unless_calendar_says_so(panel):
    base = m.weights(panel, mode="sector_lowvol")
    idx = panel.close.index
    flags = month_end_flags(idx)
    mid = [d for d in idx[1500:1600] if not flags.loc[d]][5]             # Tag mitten im Monat
    assert mid not in m.weights(panel.truncate(mid), mode="sector_lowvol").index
    ends = base.index[30]                                                # echtes Monatsende
    assert ends in m.weights(panel.truncate(ends), mode="sector_lowvol").index


# --------------------------------------------------------------------------------------
# Kausalitaet
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", list(VARIANTS))
def test_check_causality_on_synthetic_panel(panel, name):
    kw = VARIANTS[name]
    assert check_causality(lambda pp: m.weights(pp, **kw), panel) == []


@pytest.mark.parametrize("name", list(VARIANTS))
def test_check_causality_with_staggered_listings(name):
    listing = {"USMV": pd.Timestamp("2008-10-20"), "SPLV": pd.Timestamp("2008-05-05"), "XLY": pd.Timestamp("2004-03-01")}
    p = make_panel(seed=11, listing=listing)
    kw = VARIANTS[name]
    assert check_causality(lambda pp: m.weights(pp, **kw), p) == []
    first = p.close["USMV"].first_valid_index()
    cuts = [first - pd.Timedelta(days=30), first, first + pd.Timedelta(days=30)]
    assert check_causality(lambda pp: m.weights(pp, **kw), p, cuts=cuts) == []


def test_causality_check_catches_lookahead_in_the_sector_rule(panel):
    """Tripwire: ein Blick in die Zukunft muss vom selben Test erkannt werden."""
    base = m.weights(panel, mode="sector_lowvol")

    def peeking(pp):
        w = m.weights(pp, mode="sector_lowvol")
        fut = pp.close["XLP"].shift(-5).reindex(w.index)
        return w * (1.0 + fut.notna().astype(float).to_numpy()[:, None])  # nutzt, ob es spaeter noch Daten gibt

    cuts = list(base.index[[10, 20, 30]]) + [base.index[30] + pd.Timedelta(days=2)]
    assert check_causality(peeking, panel, cuts=cuts) != []


def test_perturbing_future_data_does_not_change_past_weights(panel):
    base = m.weights(panel, mode="sector_lowvol")
    cut = base.index[40]
    close = panel.close.copy()
    close.loc[close.index > cut] = close.loc[close.index > cut].to_numpy() * 3.0 + 1.0
    pert = m.weights(Panel(panel.open.where(close.notna()), close), mode="sector_lowvol")
    a, b = base.loc[:cut], pert.loc[:cut]
    assert list(a.index) == list(b.index)
    assert np.allclose(a.to_numpy(), b.to_numpy(), rtol=0, atol=1e-12)


# --------------------------------------------------------------------------------------
# Engine-Integration
# --------------------------------------------------------------------------------------

def test_sector_proxy_runs_through_engine_without_buying_anything_else(panel):
    w = m.weights(panel, mode="sector_lowvol")
    res = run_backtest(panel, w, cost=CostModel(default_bps=5.0), rf=pd.Series(0.0, index=panel.close.index))
    assert np.isfinite(res.nav).all() and (res.nav > 0).all()
    assert res.skipped_orders == 0
    assert res.gross_exposure.max() <= 1.02
    others = [c for c in panel.close.columns if c not in SECTORS]
    assert res.weights[others].abs().to_numpy().max() == 0.0             # SPY, USMV, SPLV nie gehalten
    assert res.n_trades > 0
    t0 = w.index[0]
    idx = panel.close.index
    nxt = idx[idx.get_loc(t0) + 1]
    assert res.weights.loc[t0, SECTORS].abs().max() == 0.0               # am Signaltag selbst noch nichts
    assert (res.weights.loc[nxt, list(CALM)] > 0.30).all()               # Kauf erst ab t+1


def test_all_variants_run_through_engine_with_tax(panel):
    from qlab.engine import TaxModel

    rf = pd.Series(0.0, index=panel.close.index)
    for kw in VARIANTS.values():
        res = run_backtest(panel, m.weights(panel, **kw), cost=CostModel(), rf=rf, tax=TaxModel())
        assert np.isfinite(res.nav).all() and (res.nav > 0).all()
        assert res.gross_exposure.max() <= 1.02
