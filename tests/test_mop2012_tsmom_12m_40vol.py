"""Tests fuer mop2012_tsmom_12m_40vol auf synthetischen Daten (kein Netz, kein Datencache)."""
import numpy as np
import pandas as pd
import pytest

from qlab.calendar import NYSE_BDAY, month_end_flags
from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import mop2012_tsmom_12m_40vol as mod
from strategies.mop2012_tsmom_12m_40vol import RATE_TICKER, SPEC, UNIVERSE, weights

ZERO = CostModel(default_bps=0.0, short_fee_annual=0.0, lever_spread_annual=0.0)


def make_panel(n=1800, assets=None, seed=3, drift=0.0003, vol=0.01, irx=None, late=None, start="2012-01-03"):
    """Zufallskurse (geometrische Irrfahrt) fuer ETF12 + ^IRX auf NYSE-Handelstagen.

    late: {Ticker: Anzahl Handelstage, die der Kurs am Anfang noch fehlt (NaN)}.
    """
    assets = list(UNIVERSE) if assets is None else list(assets)
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start, periods=n, freq=NYSE_BDAY)
    close = {}
    for k, t in enumerate(assets):
        r = rng.normal(drift, vol * (0.6 + 0.1 * (k % 5)), n)
        close[t] = 100.0 * np.cumprod(1.0 + r)
    close = pd.DataFrame(close, index=idx)
    for t, m in (late or {}).items():
        close.loc[idx[:m], t] = np.nan
    # ^IRX in Prozent; Standard = langsam schwankend (0.5 ... 3.5), damit Blicke in die Zukunft beim Zins auffallen
    close[RATE_TICKER] = 2.0 + 1.5 * np.sin(np.arange(n) / 200.0) if irx is None else irx
    noise = 1.0 + rng.normal(0, 0.001, close.shape)
    open_ = close * noise
    return Panel(open_, close)


def const_panel(rets, n=700, irx=2.0, start="2012-01-03"):
    """Deterministische Kurse mit konstanter Tagesrendite je Asset (bekannte Antwort)."""
    idx = pd.date_range(start, periods=n, freq=NYSE_BDAY)
    close = pd.DataFrame({t: 100.0 * (1.0 + r) ** np.arange(n) for t, r in rets.items()}, index=idx)
    close[RATE_TICKER] = irx
    return Panel(close.copy(), close)


# ---- Form, Wertebereich ----------------------------------------------------------------

def test_shape_columns_and_monthly_signal_dates():
    p = make_panel()
    w = weights(p)
    assert list(w.columns) == UNIVERSE                      # ^IRX bekommt nie ein Gewicht
    assert RATE_TICKER not in w.columns
    assert w.index.is_monotonic_increasing and w.index.is_unique
    assert w.index.isin(p.close.index).all()
    flags = month_end_flags(p.close.index, calendar_only=True)
    assert flags.loc[w.index].all()                         # nur Monatsenden
    # erstes Signal fruehestens 12 Monatsenden nach dem ersten Monatsende der Daten
    first_me = p.close.index[flags.to_numpy()][0]
    assert w.index[0] >= first_me + pd.DateOffset(months=12) - pd.Timedelta(days=3)
    assert np.isfinite(w.to_numpy()).all()


def test_ls_gross_exposure_capped_at_three():
    # sehr ruhige Assets -> 0.40/sigma gross sehr gross -> Kappe muss greifen
    w = weights(make_panel(vol=0.002))
    gross = w.abs().sum(axis=1)
    assert gross.max() <= 3.0 + 1e-9
    assert gross.max() == pytest.approx(3.0, abs=1e-9)      # Kappe greift tatsaechlich
    # normale Vol: ohne Kappe 0.40/sigma/N * N ~ 0.4/(0.01*sqrt(261)) ~ 2.5 -> bleibt unter 3 oder bei 3
    assert weights(make_panel()).abs().sum(axis=1).max() <= 3.0 + 1e-9


def test_ls_cap_scales_proportionally():
    p = make_panel(vol=0.002)
    capped = weights(p, max_gross=3.0)
    uncapped = weights(p, max_gross=1e9)
    assert uncapped.abs().sum(axis=1).max() > 3.0
    g = uncapped.abs().sum(axis=1)
    ratio = (capped / uncapped.where(uncapped.abs() > 1e-12)).stack()
    expected = (3.0 / g).clip(upper=1.0)
    for d, sub in ratio.groupby(level=0):
        assert np.allclose(sub.to_numpy(), expected.loc[d], rtol=1e-9)


def test_lf_weights_nonnegative_and_sum_capped_at_one():
    w = weights(make_panel(vol=0.002), mode="LF")
    assert (w >= 0).all().all()
    s = w.sum(axis=1)
    assert s.max() <= 1.0 + 1e-9
    assert s.max() == pytest.approx(1.0, abs=1e-9)          # Kappe greift
    w2 = weights(make_panel(), mode="LF")
    assert (w2 >= 0).all().all() and w2.sum(axis=1).max() <= 1.0 + 1e-9


def test_lf_all_negative_signals_gives_zero_row_not_missing_row():
    p = make_panel(drift=-0.002, vol=0.002)                 # alle Assets im Abwaertstrend
    w = weights(p, mode="LF")
    assert len(w) > 0
    assert (w.abs().sum(axis=1) == 0).any()
    assert not w.isna().any().any()                         # Nullzeile = Cash-Signal, keine NaN-Zeile


# ---- Bekannte Antwort ----------------------------------------------------------------

def test_known_answer_vol_scaling_and_sign():
    up, dn = 0.0004, -0.0003
    p = const_panel({"SPY": up, "TLT": dn}, irx=2.0)
    rf_d = 2.0 / 100.0 / 252
    w = weights(p, max_gross=1e9)
    assert list(w.columns) == ["SPY", "TLT"]
    last = w.iloc[-1]
    s_up = np.sqrt(261) * abs(up - rf_d)                    # EWMA konstanter Reihe = Konstante
    s_dn = np.sqrt(261) * abs(dn - rf_d)
    assert last["SPY"] == pytest.approx(+0.40 / s_up / 2, rel=1e-6)
    assert last["TLT"] == pytest.approx(-0.40 / s_dn / 2, rel=1e-6)
    lf = weights(p, mode="LF", max_gross=1e9).iloc[-1]      # LF kappt auf Summe <= 1
    assert lf["TLT"] == 0.0
    assert lf["SPY"] == pytest.approx(1.0, abs=1e-12)


def test_excess_return_uses_irx_rate():
    # Asset steigt ~2.5 % p.a. (< 5 % Zins) -> Exzessrendite negativ -> LF flat, LS short
    p = const_panel({"SPY": 0.0001}, irx=5.0)
    assert weights(p, mode="LF").iloc[-1]["SPY"] == 0.0
    assert weights(p).iloc[-1]["SPY"] < 0
    # gleiches Asset bei 0 % Zins -> Exzessrendite positiv
    p0 = const_panel({"SPY": 0.0001}, irx=0.0)
    assert weights(p0, mode="LF").iloc[-1]["SPY"] > 0
    assert weights(p0).iloc[-1]["SPY"] > 0


def test_equal_split_over_available_assets_only():
    # SPY (immer da) und EFA (erst spaeter gelistet): N_t waechst von 1 auf 2
    p = make_panel(assets=["SPY", "EFA"], n=900, late={"EFA": 300}, vol=0.01)
    solo = make_panel(assets=["SPY"], n=900, vol=0.01)         # gleiche SPY-Reihe (gleicher Seed), N_t = 1
    assert p.close["SPY"].equals(solo.close["SPY"])
    w = weights(p, max_gross=1e9)
    w_solo = weights(solo, max_gross=1e9)["SPY"]
    only_spy = w[w["EFA"] == 0]
    both = w[w["EFA"] != 0]
    assert len(only_spy) > 0 and len(both) > 0
    assert only_spy.index.max() < both.index.min()
    # N_t = 1: volles Gewicht 0.40/sigma; N_t = 2: genau halb so gross (gleiche SPY-Signale und -Vol)
    assert np.allclose(only_spy["SPY"].to_numpy(), w_solo.loc[only_spy.index].to_numpy(), rtol=1e-12)
    assert np.allclose(both["SPY"].to_numpy(), w_solo.loc[both.index].to_numpy() / 2.0, rtol=1e-12)


# ---- Fehlende Preise -------------------------------------------------------------------

def test_no_weight_on_nan_prices_or_missing_history():
    p = make_panel(late={"FXY": 500, "DBC": 250})
    w = weights(p)
    px = p.close
    for t in UNIVERSE:
        held = w.index[w[t] != 0]
        assert px.loc[held, t].notna().all()                # Gewicht nur auf vorhandenem Kurs
    # FXY braucht nach Listing noch 12 Monate Historie: davor kein Gewicht
    first_px = px["FXY"].first_valid_index()
    assert (w.loc[:first_px + pd.DateOffset(months=12) - pd.Timedelta(days=7), "FXY"] == 0).all()
    assert (w["FXY"] != 0).any()                            # spaeter aber doch dabei


def test_nan_price_on_month_end_day_blocks_only_that_asset():
    p = make_panel()
    w_ref = weights(p)
    d = w_ref.index[20]
    p2 = make_panel()
    p2.close.loc[d, "GLD"] = np.nan
    w = weights(p2)
    assert w.loc[d, "GLD"] == 0.0
    assert (w.loc[d].drop("GLD") != 0).any()


def test_missing_assets_are_skipped_and_missing_rate_raises():
    p = make_panel(assets=["SPY", "IEF", "GLD"])
    w = weights(p)
    assert list(w.columns) == ["SPY", "IEF", "GLD"]
    with pytest.raises(KeyError):
        weights(Panel(p.open.drop(columns=[RATE_TICKER]), p.close.drop(columns=[RATE_TICKER])))
    with pytest.raises(ValueError):
        weights(p, mode="XX")


def test_short_history_returns_empty_frame():
    p = make_panel(n=200)
    w = weights(p)
    assert len(w) == 0
    assert list(w.columns) == UNIVERSE


def test_rate_rows_do_not_extend_the_trading_calendar():
    # ^IRX hat zusaetzliche Tage ohne ETF-Kurse (Panel-Index = Vereinigung): kein Signal darauf
    p = make_panel()
    extra = pd.DatetimeIndex(p.close.index[100:140:7] + pd.Timedelta(days=1)).difference(p.close.index)
    open2 = p.open.reindex(p.close.index.union(extra))
    close2 = p.close.reindex(p.close.index.union(extra))
    close2.loc[extra, RATE_TICKER] = 2.0
    w_ref = weights(p)
    w = weights(Panel(open2, close2))
    pd.testing.assert_frame_equal(w_ref, w)


# ---- Portfolio-Vol-Variante ----------------------------------------------------------------

def test_portfolio_vol_variant_hits_target_when_cap_not_binding():
    p = make_panel(seed=11, vol=0.01)
    w = weights(p, portfolio_vol=0.10)
    assert len(w) > 0
    assert w.abs().sum(axis=1).max() <= 3.0 + 1e-9
    # unabhaengige Nachrechnung am letzten Signaltag
    d = w.index[-1]
    g = w.loc[d].abs().sum()
    assert g < 3.0 - 1e-6, "Test braucht ungekappten Fall"
    px = p.close[UNIVERSE]
    rf = p.close[RATE_TICKER].shift(1) / 100 / 252
    exc = (px / px.shift(1) - 1).sub(rf, axis=0)
    cov = exc.loc[:d].iloc[-756:].cov() * 261
    vec = w.loc[d].to_numpy()
    assert float(np.sqrt(vec @ cov.to_numpy() @ vec)) == pytest.approx(0.10, rel=1e-9)


def test_portfolio_vol_variant_lf_respects_sum_cap():
    w = weights(make_panel(vol=0.002), mode="LF", portfolio_vol=0.10)
    assert (w >= 0).all().all() and w.sum(axis=1).max() <= 1.0 + 1e-9


# ---- Kausalitaet -------------------------------------------------------------------------

@pytest.mark.parametrize("kw", [{}, {"mode": "LF"}, {"portfolio_vol": 0.10}], ids=["LS", "LF", "portvol10"])
def test_causality_on_synthetic_panel(kw):
    p = make_panel(seed=5)
    assert check_causality(lambda q: weights(q, **kw), p) == []


@pytest.mark.parametrize("kw", [{}, {"mode": "LF"}, {"portfolio_vol": 0.10}], ids=["LS", "LF", "portvol10"])
def test_causality_cut_exactly_at_and_before_signal_days(kw):
    # Schnitte genau auf Signaltage und den Handelstag davor: faengt Blicke von nur wenigen Tagen in die
    # Zukunft, die ein gleichmaessig verteiltes Schnittraster leicht verfehlt.
    p = make_panel(seed=6)
    idx = p.close.index
    sig = weights(p).index
    cuts = []
    for d in sig[::10]:
        cuts += [d, idx[idx.get_loc(d) - 1], idx[idx.get_loc(d) - 3]]
    assert check_causality(lambda q: weights(q, **kw), p, cuts=cuts) == []


def test_causality_with_late_listings_and_gaps():
    p = make_panel(seed=8, late={"FXY": 400})
    p.close.iloc[700:703, 2] = np.nan
    assert check_causality(lambda q: weights(q), p) == []
    assert check_causality(lambda q: weights(q, mode="LF"), p) == []


def test_data_end_mid_month_is_not_a_month_end():
    p = make_panel()
    idx = p.close.index
    # ein Tag mitten im Monat (nicht Monatsende) als letzter Datentag
    mid = [d for d in idx[600:700] if d.day in (13, 14, 15)][0]
    w = weights(p.truncate(mid))
    assert mid not in w.index
    full = weights(p)
    # Signale vor dem Schnitt sind identisch
    pd.testing.assert_frame_equal(full.loc[:mid], w.loc[:mid])


def test_future_shock_does_not_change_past_weights():
    p = make_panel()
    w0 = weights(p)
    cut = w0.index[60]
    p2 = make_panel()
    p2.close.loc[p2.close.index > cut, UNIVERSE] *= 5.0     # drastischer Kursschock NACH dem Schnitt
    w1 = weights(p2)
    pd.testing.assert_frame_equal(w0.loc[:cut], w1.loc[:cut])


# ---- SPEC / Engine-Vertrag --------------------------------------------------------------------

def test_spec_contract():
    assert SPEC["id"] == "mop2012_tsmom_12m_40vol"
    assert len(SPEC["variants"]) <= 3
    assert RATE_TICKER in SPEC["tickers"] and set(UNIVERSE) <= set(SPEC["tickers"])
    assert set(SPEC["cost_bps"]) == set(UNIVERSE)           # ^IRX wird nie gehandelt
    assert RATE_TICKER not in SPEC["cost_bps"]
    p = make_panel(n=900)
    for vp in [SPEC["params"], *({**SPEC["params"], **v} for v in SPEC["variants"].values())]:
        w = weights(p, **vp)
        assert len(w) > 0


def test_weights_run_in_engine():
    p = make_panel(n=900)
    rf0 = pd.Series(0.0, index=p.close.index)
    for kw in ({}, {"mode": "LF"}):
        w = weights(p, **kw)
        res = run_backtest(p, w, cost=ZERO, rf=rf0)         # KeyError, falls Gewichte auf Nicht-Tickern
        assert np.isfinite(res.nav.iloc[-1]) and res.nav.iloc[-1] > 0
        assert res.skipped_orders == 0
        assert (res.weights[RATE_TICKER].abs() < 1e-12).all()
