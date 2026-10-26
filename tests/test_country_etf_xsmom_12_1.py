"""Tests fuer country_etf_xsmom_12_1 auf synthetischen Daten (kein Netz, kein Datencache)."""
import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import month_end_flags
from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import country_etf_xsmom_12_1 as m

UNI = m.UNIVERSE
EXT = m.EXTENSION
ALL = UNI + EXT
ZERO = CostModel(default_bps=0.0, short_fee_annual=0.0, lever_spread_annual=0.0)
START = "1996-03-18"

VARIANTS = {"base": {}, **m.SPEC["variants"]}


# --------------------------------------------------------------------------------------
# Hilfen: synthetische Panels
# --------------------------------------------------------------------------------------

def random_panel(n=1700, seed=3, listing=None, tickers=ALL):
    """Taegliche Zufallskurse (Open != Close); `listing` = {Ticker: erster Handelstag-Index} -> davor NaN."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range(START, periods=n)
    mm = len(tickers)
    on = rng.normal(0.0002, 0.005, (n, mm))
    intra = rng.normal(0.0002, 0.008, (n, mm))
    close = 100.0 * np.cumprod((1 + on) * (1 + intra), axis=0)
    prev = np.vstack([np.full((1, mm), 100.0), close[:-1]])
    open_ = prev * (1 + on)
    c = pd.DataFrame(close, index=idx, columns=tickers)
    o = pd.DataFrame(open_, index=idx, columns=tickers)
    for t, first in (listing or {}).items():
        c.loc[c.index[:first], t] = np.nan
        o.loc[o.index[:first], t] = np.nan
    return Panel(o, c)


LISTING = {"EWZ": 600, "EWY": 700, "EWT": 800, "EZA": 1100}


def step_panel(monthly, stub_days=3):
    """Panel aus Monatsendkursen: Kurs = konstant innerhalb des Monats (Open == Close).

    monthly: {Ticker: Liste der Kurse je Monat ab 1996-03 (NaN = nicht gelistet/Luecke)}.
    Der letzte Monatsend-Handelstag jedes Monats traegt exakt den Monatskurs; danach folgt ein kurzer
    Stub-Monat, damit auch der letzte echte Monatsultimo aus den Daten (nicht dem Kalender) erkannt wird.
    """
    K = len(next(iter(monthly.values())))
    first = pd.Period("1996-03", "M")
    end_month = (first + K - 1).end_time.normalize()
    main = pd.bdate_range(START, end_month)
    stub = pd.bdate_range(end_month + pd.Timedelta(days=1), periods=stub_days)
    idx = main.append(stub)
    k = np.minimum((idx.year - 1996) * 12 + idx.month - 3, K - 1)
    close = pd.DataFrame({t: np.asarray(v, float)[k] for t, v in monthly.items()}, index=idx)
    ends = pd.Series(main, index=main).groupby(main.to_period("M")).max().to_list()
    return Panel(close.copy(), close), ends


def trend_levels(K, growth):
    return [100.0 * growth ** k for k in range(K)]


def ref_weights(monthly, ends, mode="long_short", sma=False, extended=False, top_n=5, min_assets=10):
    """Bewusst naive, schleifenbasierte Referenz (unabhaengiger Code-Pfad) der Regel."""
    names = [n for n in (UNI + (EXT if extended else [])) if n in monthly]
    K = len(ends)
    rows = {}
    for k in range(12, K):
        valid = []
        for n in names:
            a, b, c = monthly[n][k - 1], monthly[n][k - 12], monthly[n][k]
            if np.isfinite(a) and np.isfinite(b) and np.isfinite(c):
                valid.append((a / b - 1.0, n))
        if len(valid) < min_assets:
            continue
        valid.sort(key=lambda x: (x[0], x[1]))
        N = len(valid)
        w = {n: 0.0 for n in names}
        if mode == "long_short":
            z = [i + 1 - (N + 1) / 2.0 for i in range(N)]
            denom = sum(x for x in z if x > 0)
            for (_, n), zi in zip(valid, z):
                w[n] = zi / denom
        else:
            for _, n in valid[-top_n:]:
                if sma:
                    last10 = monthly[n][k - 9:k + 1]
                    if not np.all(np.isfinite(last10)) or not monthly[n][k] > np.mean(last10):
                        continue
                w[n] = 1.0 / top_n
        rows[ends[k]] = w
    return pd.DataFrame.from_dict(rows, orient="index")[names]


def random_monthly(K=48, seed=11, with_gaps=True):
    rng = np.random.default_rng(seed)
    monthly = {}
    for t in ALL:
        lv = 100.0 * np.cumprod(1.0 + rng.normal(0.005, 0.06, K))
        monthly[t] = lv.copy()
    if with_gaps:
        for t, upto in (("EWZ", 4), ("EWY", 3), ("EWT", 6), ("EZA", 18)):   # spaeter gelistet
            monthly[t][:upto] = np.nan
        monthly["EWK"][20] = np.nan                                           # einzelne Datenluecke
        monthly["EWD"][30] = np.nan
        for t in UNI[:8]:                                                     # zu wenige gueltige Titel (< 10)
            monthly[t][38:40] = np.nan
    return monthly


# --------------------------------------------------------------------------------------
# Spezifikation / Vertrag
# --------------------------------------------------------------------------------------

def test_spec_contract():
    s = m.SPEC
    assert s["id"] == "country_etf_xsmom_12_1" and s["family"] == "xsmom"
    assert len(s["variants"]) <= 3
    assert len(UNI) == 17 and len(set(UNI)) == 17
    assert set(UNI) <= set(s["tickers"])
    assert "^IRX" not in s["tickers"]                    # Zinsreihe ist kein handelbarer Preis
    allowed = set(inspect.signature(m.weights).parameters) - {"panel"}
    assert set(s["params"]) <= allowed
    for v in s["variants"].values():
        assert set(v) <= allowed
    # weights() mit Standardwerten == Basisparameter (check_causality ruft ohne Argumente auf)
    defaults = {k: p.default for k, p in inspect.signature(m.weights).parameters.items() if k != "panel"}
    assert defaults == s["params"]


def test_invalid_args():
    p = random_panel(n=300)
    with pytest.raises(ValueError):
        m.weights(p, mode="foo")
    with pytest.raises(ValueError):
        m.weights(p, min_assets=1)


# --------------------------------------------------------------------------------------
# Regel: Referenzvergleich, Ranggewichte, erstes Signal
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", list(VARIANTS))
def test_matches_naive_reference(name):
    monthly = random_monthly()
    panel, ends = step_panel(monthly)
    kw = VARIANTS[name]
    got = m.weights(panel, **kw)
    exp = ref_weights(monthly, ends, mode=kw.get("mode", "long_short"), sma=kw.get("sma_filter", False),
                      extended=kw.get("extended", False))
    assert len(got) > 20
    pd.testing.assert_frame_equal(got, exp, check_freq=False, check_names=False, atol=1e-12, rtol=0)


def test_long_short_rank_weights_exact():
    # Ticker i hat konstantes Monatswachstum, Rang = Position in der Wachstumsreihenfolge
    K = 30
    order = list(np.random.default_rng(5).permutation(UNI))      # order[0] = schwaechster, order[-1] = staerkster
    monthly = {t: trend_levels(K, 1.0 + 0.003 * (i + 1)) for i, t in enumerate(order)}
    panel, ends = step_panel(monthly)
    w = m.weights(panel)
    assert w.index[0] == ends[12]
    for _, row in w.iterrows():
        for i, t in enumerate(order):
            assert row[t] == pytest.approx((i + 1 - 9) / 36.0)
        assert row.sum() == pytest.approx(0.0, abs=1e-12)
        assert row[row > 0].sum() == pytest.approx(1.0)
        assert row[row < 0].sum() == pytest.approx(-1.0)
        assert row.abs().sum() == pytest.approx(2.0)


def test_first_signal_date_1997_03_31():
    K = 40
    monthly = {t: trend_levels(K, 1.0 + 0.001 * (i + 1)) for i, t in enumerate(UNI)}
    panel, _ = step_panel(monthly)
    w = m.weights(panel)
    assert w.index[0] == pd.Timestamp("1997-03-31")
    # davor kein Signal (Ende m-12 muss existieren)
    assert panel.close.index[0] == pd.Timestamp(START)


def test_ties_alphabetical():
    K = 20
    monthly = {t: [100.0] * K for t in UNI}                       # alle Scores exakt 0
    panel, _ = step_panel(monthly)
    w = m.weights(panel)
    names = sorted(UNI)
    for _, row in w.iterrows():
        for i, t in enumerate(names):
            assert row[t] == pytest.approx((i + 1 - 9) / 36.0)    # EWA = -8/36 ... EWW = +8/36


def test_skips_most_recent_month():
    # Score am Signalmonat k nutzt Ende k-1 und Ende k-12; der Kurs am Signaltag selbst (Ende k) ist irrelevant
    K = 30
    base = {t: trend_levels(K, 1.0 + 0.002 * (i + 1)) for i, t in enumerate(UNI)}
    p0, ends = step_panel(base)
    w0 = m.weights(p0)
    k = 20
    shocked = {t: list(v) for t, v in base.items()}
    for t in UNI:
        shocked[t][k] *= 0.3 if t == UNI[-1] else 3.0              # extremer Schock NUR am Signalmonat
    p1, _ = step_panel(shocked)
    w1 = m.weights(p1)
    pd.testing.assert_series_equal(w0.loc[ends[k]], w1.loc[ends[k]], check_names=False)
    # Gegenprobe: Schock am Ende k-1 (Zaehler) VERAENDERT das Signal bei k
    shocked2 = {t: list(v) for t, v in base.items()}
    shocked2[UNI[-1]][k - 1] *= 0.2
    shocked2[UNI[0]][k - 1] *= 5.0
    p2, _ = step_panel(shocked2)
    w2 = m.weights(p2)
    assert not np.allclose(w0.loc[ends[k]].to_numpy(), w2.loc[ends[k]].to_numpy())
    # ... und Schock am Ende k-12 (Nenner) ebenfalls
    shocked3 = {t: list(v) for t, v in base.items()}
    shocked3[UNI[3]][k - 12] *= 0.1
    p3, _ = step_panel(shocked3)
    w3 = m.weights(p3)
    assert not np.allclose(w0.loc[ends[k]].to_numpy(), w3.loc[ends[k]].to_numpy())


# --------------------------------------------------------------------------------------
# Long-only-Varianten
# --------------------------------------------------------------------------------------

def test_long_top5_picks_best_five_equal_weight():
    K = 30
    order = list(np.random.default_rng(8).permutation(UNI))
    monthly = {t: trend_levels(K, 1.0 + 0.003 * (i + 1)) for i, t in enumerate(order)}
    panel, _ = step_panel(monthly)
    w = m.weights(panel, **m.SPEC["variants"]["long_top5"])
    for _, row in w.iterrows():
        assert (row >= 0).all()
        assert set(row[row > 0].index) == set(order[-5:])
        assert row[row > 0].tolist() == pytest.approx([0.2] * 5)
        assert row.sum() == pytest.approx(1.0)


def test_sma10_filter_goes_to_cash_for_broken_trend():
    K = 40
    monthly = {t: trend_levels(K, 1.0 + 0.002 * (i + 1)) for i, t in enumerate(UNI)}
    top5 = UNI[-5:]
    broken = top5[2]
    k = 25
    monthly[broken][k] *= 0.4                                      # Kurs am Signaltag bricht unter den 10M-Schnitt ein
    panel, ends = step_panel(monthly)
    w_top = m.weights(panel, **m.SPEC["variants"]["long_top5"])
    w_sma = m.weights(panel, **m.SPEC["variants"]["long_top5_sma10"])
    # Score (12-1) unveraendert -> long_top5 haelt den Wert weiter ...
    assert w_top.loc[ends[k], broken] == pytest.approx(0.2)
    # ... das SMA-Filter-Gewicht ist 0 -> Cash (kein Ersatz durch Rang 6)
    assert w_sma.loc[ends[k], broken] == 0.0
    assert w_sma.loc[ends[k]].sum() == pytest.approx(0.8)
    others = [t for t in top5 if t != broken]
    assert w_sma.loc[ends[k], others].tolist() == pytest.approx([0.2] * 4)
    # Davor/Danach (intakter Trend): identisch zu long_top5
    assert w_sma.loc[ends[k - 1]].sum() == pytest.approx(1.0)
    # kein SMA-Wert (weniger als 10 Monatsenden Historie) kann nie vorkommen, wenn Score existiert (12 > 10)
    assert (w_sma.sum(axis=1) <= w_top.sum(axis=1) + 1e-12).all()


# --------------------------------------------------------------------------------------
# Form, Wertebereich, NaN-Preise, erweitertes Universum
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", list(VARIANTS))
def test_shape_range_and_nan_prices(name):
    panel = random_panel(listing=LISTING)
    kw = VARIANTS[name]
    w = m.weights(panel, **kw)
    assert len(w) > 20
    assert w.index.is_monotonic_increasing and w.index.is_unique
    assert set(w.index) <= set(panel.close.index)
    assert set(w.columns) <= set(panel.close.columns)
    assert np.isfinite(w.to_numpy()).all()
    flags = pd.Series(w.index.isin(month_end_flags(panel.close.index)[lambda s: s].index), index=w.index)
    assert flags.all()                                               # nur Monatsendetage
    gross = w.abs().sum(axis=1)
    net = w.sum(axis=1)
    if kw.get("mode", "long_short") == "long_short":
        assert (gross <= 2.0 + 1e-9).all()
        assert net.abs().max() < 1e-9
    else:
        assert (w >= 0).all().all()
        assert (gross <= 1.0 + 1e-9).all()
    # kein Gewicht auf NaN-Preisen am Signaltag
    px = panel.close.reindex(index=w.index, columns=w.columns)
    assert (w.where(px.isna()).fillna(0.0) == 0.0).all().all()


def test_nan_price_on_signal_day_gets_no_weight():
    monthly = random_monthly(with_gaps=False)
    panel, ends = step_panel(monthly)
    k = 22
    panel.close.loc[ends[k], "EWK"] = np.nan                       # EWK am Signaltag nicht handelbar
    w = m.weights(panel)
    assert w.loc[ends[k], "EWK"] == 0.0
    assert w.loc[ends[k]].abs().sum() == pytest.approx(2.0)        # restliche 16 Titel tragen volle Brutto-Exposure
    assert w.loc[ends[k]].sum() == pytest.approx(0.0, abs=1e-12)


def test_late_listed_tickers_only_in_extended_universe():
    monthly = random_monthly(with_gaps=True)
    panel, ends = step_panel(monthly)
    base = m.weights(panel)
    ext = m.weights(panel, extended=True)
    assert set(base.columns) == set(UNI)                            # Hauptlauf rangiert nur die 17
    assert set(ext.columns) == set(ALL)
    # EZA (erst ab Monat 18 gelistet) braucht 12 Monate Vorlauf: erstes Gewicht fruehestens Monat 30
    ez = ext["EZA"]
    assert (ez.loc[:ends[29]] == 0.0).all()
    assert (ez.loc[ends[30]:] != 0.0).any()
    assert (ext.abs().sum(axis=1) <= 2.0 + 1e-9).all()
    # Erweiterung wird nur dort genutzt, wo Scores existieren: Brutto bleibt bei 2 (Long +1, Short -1)
    assert ext.sum(axis=1).abs().max() < 1e-9
    # Anzahl der Positionen waechst mit dem Universum (16 -> 18 -> 20 -> ...)
    nz = (ext != 0).sum(axis=1)
    assert nz.iloc[0] <= nz.iloc[-1]


def test_too_few_valid_assets_gives_no_signal():
    monthly = random_monthly(with_gaps=True)
    panel, ends = step_panel(monthly)
    w = m.weights(panel)
    # 8 Titel haben in Monat 38 und 39 keinen Kurs: ungueltig bei k=38, 39 (Kurs heute) und k=40 (Zaehler Ende k-1)
    for k in (38, 39, 40):
        assert ends[k] not in w.index                             # nur 9 gueltige Titel (< min_assets)
    assert ends[37] in w.index and ends[41] in w.index


def test_input_not_mutated_and_deterministic():
    panel = random_panel(n=800, listing=LISTING)
    snap_c, snap_o = panel.close.copy(), panel.open.copy()
    w1 = m.weights(panel, extended=True)
    w2 = m.weights(panel, extended=True)
    pd.testing.assert_frame_equal(w1, w2)
    pd.testing.assert_frame_equal(panel.close, snap_c)
    pd.testing.assert_frame_equal(panel.open, snap_o)


# --------------------------------------------------------------------------------------
# Kausalitaet und Engine-Smoke
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", list(VARIANTS))
def test_causality(name):
    panel = random_panel(listing=LISTING)
    kw = VARIANTS[name]
    assert check_causality(lambda p: m.weights(p, **kw), panel) == []


def test_causality_with_nan_gaps():
    panel = random_panel(listing=LISTING, seed=21)
    # Einzelne Luecken in Kursen (nicht handelbar an diesen Tagen)
    rng = np.random.default_rng(2)
    for t in ("EWK", "EWO", "EWD"):
        bad = rng.choice(len(panel.close), size=40, replace=False)
        panel.close.iloc[bad, panel.close.columns.get_loc(t)] = np.nan
        panel.open.iloc[bad, panel.open.columns.get_loc(t)] = np.nan
    for kw in VARIANTS.values():
        assert check_causality(lambda p, _kw=kw: m.weights(p, **_kw), panel) == []


@pytest.mark.parametrize("name", list(VARIANTS))
def test_engine_runs_on_weights(name):
    panel = random_panel(n=900, listing=LISTING)
    w = m.weights(panel, **VARIANTS[name])
    res = run_backtest(panel, w, cost=ZERO, rf=pd.Series(0.0, index=panel.close.index))
    assert np.isfinite(res.nav.to_numpy()).all() and (res.nav > 0).all()
    assert res.n_trades > 0
    assert res.skipped_orders == 0
    if VARIANTS[name].get("mode", "long_short") == "long_short":
        first_trade_day = res.turnover[res.turnover > 0].index[0]
        assert res.gross_exposure.loc[first_trade_day] == pytest.approx(2.0, abs=0.05)
