"""Tests für country_value_cape_faber_proxy auf synthetischen Daten (kein Netz, kein Datencache)."""
import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import month_end_flags
from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import country_value_cape_faber_proxy as m

UNI = m.UNIVERSE
ZERO = CostModel(default_bps=0.0, short_fee_annual=0.0, lever_spread_annual=0.0)

VARIANTS = {"base": {}, **m.SPEC["variants"]}


# --------------------------------------------------------------------------------------
# Hilfen: synthetische Panels
# --------------------------------------------------------------------------------------

def random_panel(n=4400, seed=3, ew_listing="1996-03-18", tickers=UNI, start="1993-01-29"):
    """Tägliche Zufallskurse (Open != Close). SPY ab `start`, alle anderen erst ab `ew_listing` (davor NaN)."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range(start, periods=n)
    mm = len(tickers)
    on = rng.normal(0.0002, 0.005, (n, mm))
    intra = rng.normal(0.0002, 0.008, (n, mm))
    close = 100.0 * np.cumprod((1 + on) * (1 + intra), axis=0)
    prev = np.vstack([np.full((1, mm), 100.0), close[:-1]])
    open_ = prev * (1 + on)
    c = pd.DataFrame(close, index=idx, columns=tickers)
    o = pd.DataFrame(open_, index=idx, columns=tickers)
    before = idx < pd.Timestamp(ew_listing)
    for t in tickers:
        if t != "SPY":
            c.loc[before, t] = np.nan
            o.loc[before, t] = np.nan
    return Panel(o, c)


def step_panel(monthly, first_month="1996-03", start="1996-03-18", stub_days=3):
    """Panel aus Monatsendkursen: Kurs = konstant innerhalb des Monats (Open == Close).

    monthly: {Ticker: Liste der Kurse je Monat ab `first_month` (NaN = nicht gelistet/Lücke)}.
    Der letzte Handelstag jedes Monats trägt exakt den Monatskurs; ein kurzer Stub-Monat am Ende sorgt dafür,
    dass auch der letzte echte Monatsultimo aus den Daten (nicht nur dem Kalender) erkannt wird.
    Rückgabe: Panel und die Liste der Monatsend-Handelstage (nur Testhilfe, darf groupby nutzen).
    """
    K = len(next(iter(monthly.values())))
    first = pd.Period(first_month, "M")
    end_month = (first + K - 1).end_time.normalize()
    main = pd.bdate_range(start, end_month)
    stub = pd.bdate_range(end_month + pd.Timedelta(days=1), periods=stub_days)
    idx = main.append(stub)
    k = np.minimum((idx.year - first.year) * 12 + idx.month - first.month, K - 1)
    close = pd.DataFrame({t: np.asarray(v, float)[k] for t, v in monthly.items()}, index=idx)
    ends = pd.Series(main, index=main).groupby(main.to_period("M")).max().to_list()
    return Panel(close.copy(), close), ends


def growth_levels(K, growth):
    return [100.0 * growth ** k for k in range(K)]


def ref_weights(monthly, ends, lookback=120, divisor=3, month=12):
    """Bewusst naive, schleifenbasierte Referenz (unabhängiger Code-Pfad) der Regel."""
    names = [n for n in UNI if n in monthly]
    rows = {}
    for k, d in enumerate(ends):
        if d.month != month or k + 1 < lookback:
            continue
        cand = []
        for n in names:
            win = np.asarray(monthly[n][k - lookback + 1:k + 1], float)
            if np.all(np.isfinite(win)) and np.all(win > 0):
                cand.append((win[-1] / win.mean(), n))
        kk = len(cand) // divisor
        if kk < 1:
            continue
        cand.sort(key=lambda x: (x[0], x[1]))
        w = {n: 0.0 for n in names}
        for _, n in cand[:kk]:
            w[n] = 1.0 / kk
        rows[d] = w
    return pd.DataFrame.from_dict(rows, orient="index")[names]


def random_monthly(K=200, seed=11, first_listed=None, gaps=None):
    """Zufällige Monatsendkurse für alle 14 Ticker; first_listed {Ticker: erster gültiger Monatsindex}."""
    rng = np.random.default_rng(seed)
    monthly = {}
    for t in UNI:
        monthly[t] = 100.0 * np.cumprod(1.0 + rng.normal(0.005, 0.06, K))
    for t, upto in (first_listed or {}).items():
        monthly[t][:upto] = np.nan
    for t, k in (gaps or {}).items():
        monthly[t][k] = np.nan
    return monthly


# --------------------------------------------------------------------------------------
# Spezifikation / Vertrag
# --------------------------------------------------------------------------------------

def test_spec_contract():
    s = m.SPEC
    assert s["id"] == "country_value_cape_faber_proxy" and s["family"] == "valuecarry"
    assert len(s["variants"]) <= 3
    assert len(UNI) == 14 and len(set(UNI)) == 14
    assert s["tickers"] == UNI
    assert not any(t.startswith("^") for t in s["tickers"])        # keine Zinsreihen o. ä. als Handelsobjekt
    assert s["cost_bps"] == {t: 10.0 for t in UNI}                   # 10 bp je Seite laut Spezifikation
    allowed = set(inspect.signature(m.weights).parameters) - {"panel"}
    assert set(s["params"]) <= allowed
    for v in s["variants"].values():
        assert set(v) <= allowed
    # weights() mit Standardwerten == Basisparameter (check_causality ruft ohne Argumente auf)
    defaults = {k: p.default for k, p in inspect.signature(m.weights).parameters.items() if k != "panel"}
    assert defaults == s["params"]
    assert s["params"] == {"lookback_months": 120, "select_divisor": 3, "rebalance_month": 12}


def test_invalid_args():
    p = random_panel(n=300)
    with pytest.raises(ValueError):
        m.weights(p, lookback_months=1)
    with pytest.raises(ValueError):
        m.weights(p, select_divisor=0)
    with pytest.raises(ValueError):
        m.weights(p, rebalance_month=13)
    with pytest.raises(ValueError):
        m.weights(p, rebalance_month=0)


# --------------------------------------------------------------------------------------
# Regel: Referenzvergleich, Auswahl, Gleichstand, erstes Signal
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", list(VARIANTS))
def test_matches_naive_reference(name):
    # Lücken: spät gelistet, einzelne Datenlücken (machen den ETF für 120/60 Monate unbrauchbar)
    monthly = random_monthly(K=200, first_listed={"EWS": 20, "EWH": 45}, gaps={"EWD": 90, "EWA": 140})
    panel, ends = step_panel(monthly)
    kw = VARIANTS[name]
    got = m.weights(panel, **kw)
    exp = ref_weights(monthly, ends, lookback=kw.get("lookback_months", 120), divisor=kw.get("select_divisor", 3),
                      month=kw.get("rebalance_month", 12))
    assert len(got) >= 5
    pd.testing.assert_frame_equal(got, exp, check_freq=False, check_names=False, atol=1e-12, rtol=0)


@pytest.mark.parametrize("name", list(VARIANTS))
def test_matches_naive_reference_no_gaps(name):
    monthly = random_monthly(K=190, seed=5)
    panel, ends = step_panel(monthly)
    kw = VARIANTS[name]
    got = m.weights(panel, **kw)
    exp = ref_weights(monthly, ends, lookback=kw.get("lookback_months", 120), divisor=kw.get("select_divisor", 3),
                      month=kw.get("rebalance_month", 12))
    assert len(got) >= 5
    pd.testing.assert_frame_equal(got, exp, check_freq=False, check_names=False, atol=1e-12, rtol=0)


def test_cheapest_third_exact_and_equal_weight():
    # Konstantes Monatswachstum g_i: RP steigt streng mit g -> die 4 langsamsten sind am billigsten
    K = 135
    order = list(np.random.default_rng(5).permutation(UNI))          # order[0] = niedrigstes Wachstum = billigster
    monthly = {t: growth_levels(K, 1.0 + 0.002 * (i + 1)) for i, t in enumerate(order)}
    panel, ends = step_panel(monthly)
    w = m.weights(panel)
    assert list(w.index) == [e for e in ends if e.month == 12 and ends.index(e) >= 119]
    for _, row in w.iterrows():
        assert set(row[row > 0].index) == set(order[:4])             # floor(14/3) = 4
        assert row[row > 0].tolist() == pytest.approx([0.25] * 4)
        assert row.sum() == pytest.approx(1.0)
        assert (row >= 0).all()
    # Viertel: floor(14/4) = 3 Länder zu je 1/3
    wq = m.weights(panel, **m.SPEC["variants"]["quartile"])
    for _, row in wq.iterrows():
        assert set(row[row > 0].index) == set(order[:3])
        assert row[row > 0].tolist() == pytest.approx([1.0 / 3.0] * 3)
        assert row.sum() == pytest.approx(1.0)


def test_ties_alphabetical():
    K = 135
    monthly = {t: [100.0] * K for t in UNI}                          # alle RP exakt 1
    panel, _ = step_panel(monthly)
    w = m.weights(panel)
    assert len(w) >= 1
    for _, row in w.iterrows():
        assert set(row[row > 0].index) == {"EWA", "EWC", "EWD", "EWG"}
        assert row.sum() == pytest.approx(1.0)


def test_signal_uses_price_at_signal_day_and_window_including_it():
    # Nur der Kurs am Signaltag selbst (Monatsende kdec) verändert sich: der bisher billigste Wert wird teuer
    # und fliegt aus der Auswahl. Ein Schock im Folgemonat ändert das Signal bei kdec dagegen nicht.
    K = 135
    base = {t: growth_levels(K, 1.0 + 0.002 * (i + 1)) for i, t in enumerate(UNI)}
    p0, ends = step_panel(base)
    kdec = next(i for i, e in enumerate(ends) if e.month == 12 and i >= 119)
    w0 = m.weights(p0).loc[ends[kdec]]
    cheapest = UNI[0]
    assert w0[cheapest] > 0
    shocked = {t: list(v) for t, v in base.items()}
    shocked[cheapest][kdec] *= 5.0                                   # am Signaltag plötzlich teuer
    w1 = m.weights(step_panel(shocked)[0]).loc[ends[kdec]]
    assert w1[cheapest] == 0.0 and w1.sum() == pytest.approx(1.0)
    after = {t: list(v) for t, v in base.items()}
    after[cheapest][kdec + 1] *= 0.01                                # Schock NACH dem Signaltag
    after[UNI[-1]][kdec + 1] *= 100.0
    w2 = m.weights(step_panel(after)[0]).loc[ends[kdec]]
    pd.testing.assert_series_equal(w0, w2, check_names=False)


def test_only_month_end_prices_matter():
    # Kurse an Nicht-Monatsendetagen (und Eröffnungskurse) haben keinen Einfluss auf die Gewichte
    panel = random_panel(n=3600, seed=9)
    w0 = m.weights(panel)
    flags = month_end_flags(panel.close.index).to_numpy()
    rng = np.random.default_rng(1)
    c2, o2 = panel.close.copy(), panel.open.copy()
    noise = rng.uniform(0.5, 2.0, c2.shape)
    c2[~flags] = c2[~flags].to_numpy() * noise[~flags]
    o2 = o2 * rng.uniform(0.5, 2.0, o2.shape)
    w1 = m.weights(Panel(o2, c2))
    pd.testing.assert_frame_equal(w0, w1)


def test_history_boundary_119_vs_120_months():
    # Signal im Februar: 1996-03 + 119 Monate = 2006-02 (Monatsindex 119) -> das 120-Monats-Fenster beginnt genau bei Monat 0.
    # Ticker X mit Monat 0 = NaN hat dort nur 119 gültige Werte -> kein Kandidat, auch wenn er der billigste wäre.
    K = 135
    monthly = {t: growth_levels(K, 1.0 + 0.002 * (i + 1)) for i, t in enumerate(UNI)}
    x = UNI[0]                                                       # niedrigstes Wachstum = billigster
    monthly[x] = list(monthly[x])
    monthly[x][0] = np.nan
    panel, ends = step_panel(monthly)
    assert ends[119].month == 2
    w = m.weights(panel, rebalance_month=2)
    assert w.index[0] == ends[119]
    assert w.loc[ends[119], x] == 0.0                                # nur 119 Monate Historie
    assert w.loc[ends[119]].sum() == pytest.approx(1.0)
    assert (w.loc[ends[119]] > 0).sum() == 4                         # floor(13/3) = 4
    assert w.loc[ends[131], x] == pytest.approx(0.25)                # ein Jahr später ist Monat 0 aus dem Fenster
    # genau 120 gültige Werte (Monat 0 vorhanden) -> Kandidat und billigster
    monthly[x][0] = 100.0
    w2 = m.weights(step_panel(monthly)[0], rebalance_month=2)
    assert w2.loc[ends[119], x] == pytest.approx(0.25)


def test_gap_in_window_excludes_ticker_until_it_leaves_window():
    K = 260
    monthly = {t: growth_levels(K, 1.0 + 0.002 * (i + 1)) for i, t in enumerate(UNI)}
    x = UNI[0]                                                       # billigster
    monthly[x] = list(monthly[x])
    monthly[x][150] = np.nan                                         # Lücke bei Monatsindex 150
    panel, ends = step_panel(monthly)
    w = m.weights(panel)
    for d in w.index:
        kk = ends.index(d)
        in_window = kk - 119 <= 150 <= kk
        assert (w.loc[d, x] == 0.0) == in_window


def test_first_signal_dates_with_early_spy_history():
    # SPY ab 1993-01, die 13 Länder-ETFs ab 1996-03 (Monatsindex 38). SPY allein (N=1) ergibt nie ein Signal.
    K = 190
    first_listed = {t: 38 for t in UNI if t != "SPY"}
    monthly = random_monthly(K=K, seed=2, first_listed=first_listed)
    panel, ends = step_panel(monthly, first_month="1993-01", start="1993-01-29")
    base = m.weights(panel)
    assert base.index[0] == pd.Timestamp("2006-12-29")               # erste Entscheidung 12/2006
    assert (base.index.year >= 2006).all()
    assert (base.index.month == 12).all()
    assert (base.loc[pd.Timestamp("2006-12-29")] > 0).sum() == 4
    avg60 = m.weights(panel, lookback_months=60)
    assert avg60.index[0] == pd.Timestamp("2001-12-31")              # 60 Monate nach 1996-03
    june = m.weights(panel, rebalance_month=6)
    assert june.index[0] == pd.Timestamp("2006-06-30")
    assert (june.index.month == 6).all()
    # Abstand der Signale: genau 12 Monate
    for w in (base, avg60, june):
        months = w.index.year * 12 + w.index.month
        assert (np.diff(months) == 12).all()


def test_too_few_candidates_gives_no_signal_not_cash():
    # Nur 2 Ticker mit Daten -> floor(2/3) = 0 -> keine Zeile (keine Cash-Zeile)
    K = 150
    monthly = {t: (growth_levels(K, 1.01) if t in ("SPY", "EWC") else [np.nan] * K) for t in UNI}
    panel, _ = step_panel(monthly)
    w = m.weights(panel)
    assert len(w) == 0
    # exakt 3 Kandidaten -> 1 Land mit Gewicht 1
    monthly["EWU"] = growth_levels(K, 1.02)
    w3 = m.weights(step_panel(monthly)[0])
    assert len(w3) > 0
    for _, row in w3.iterrows():
        assert (row > 0).sum() == 1 and row.sum() == pytest.approx(1.0)
        assert row["SPY"] == pytest.approx(1.0) or row["EWC"] == pytest.approx(1.0)   # langsamste Wachstumsreihe


# --------------------------------------------------------------------------------------
# Form, Wertebereich, NaN-Preise
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", list(VARIANTS))
def test_shape_range_and_nan_prices(name):
    kw = VARIANTS[name]
    panel = random_panel(n=4400, ew_listing="1996-03-18")
    # ein Land spät gelistet -> weniger Kandidaten in frühen Jahren
    late = panel.close.index[panel.close.index >= pd.Timestamp("1999-06-01")][0]
    panel.close.loc[:late - pd.Timedelta(days=1), "EWS"] = np.nan
    panel.open.loc[:late - pd.Timedelta(days=1), "EWS"] = np.nan
    w = m.weights(panel, **kw)
    assert len(w) >= 3
    assert w.index.is_monotonic_increasing and w.index.is_unique
    assert set(w.index) <= set(panel.close.index)
    assert set(w.columns) <= set(panel.close.columns)
    assert np.isfinite(w.to_numpy()).all()
    flags = month_end_flags(panel.close.index)
    assert flags.loc[w.index].all()                                  # nur Monatsendetage
    assert (w.index.month == kw.get("rebalance_month", 12)).all()
    assert (w >= 0).all().all()                                      # long-only
    gross = w.abs().sum(axis=1)
    assert (gross <= 1.0 + 1e-9).all()
    assert gross.to_numpy() == pytest.approx(1.0)                    # voll investiert, kein Cash-Filter
    # Anzahl Positionen = floor(N / Divisor) und Gleichgewicht
    div = kw.get("select_divisor", 3)
    lb = kw.get("lookback_months", 120)
    me = panel.close[flags.to_numpy()]
    cand = (me.notna().astype(float).rolling(lb).sum() == lb) & me.notna()
    for d, row in w.iterrows():
        k = int(cand.loc[d].sum()) // div
        assert (row > 0).sum() == k
        assert row[row > 0].tolist() == pytest.approx([1.0 / k] * k)
    # kein Gewicht auf NaN-Preisen am Signaltag
    px = panel.close.reindex(index=w.index, columns=w.columns)
    assert (w.where(px.isna()).fillna(0.0) == 0.0).all().all()


def test_nan_price_on_signal_day_gets_no_weight():
    K = 135
    monthly = {t: growth_levels(K, 1.0 + 0.002 * (i + 1)) for i, t in enumerate(UNI)}
    panel, ends = step_panel(monthly)
    kdec = next(i for i, e in enumerate(ends) if e.month == 12 and i >= 119)
    d = ends[kdec]
    base = m.weights(panel).loc[d]
    assert set(base[base > 0].index) == set(UNI[:4])
    # billigster Ticker am Signaltag ohne Kurs: nicht handelbar, der nächste rückt nach (N=13 -> floor = 4)
    panel.close.loc[d, UNI[0]] = np.nan
    w = m.weights(panel).loc[d]
    assert w[UNI[0]] == 0.0
    assert set(w[w > 0].index) == set(UNI[1:5])
    assert w.sum() == pytest.approx(1.0)
    # drei Ticker ohne Kurs: N=11 -> floor(11/3) = 3 Länder zu je 1/3
    panel.close.loc[d, UNI[1]] = np.nan
    panel.close.loc[d, UNI[2]] = np.nan
    w3 = m.weights(panel).loc[d]
    assert w3[[UNI[0], UNI[1], UNI[2]]].abs().sum() == 0.0
    assert set(w3[w3 > 0].index) == set(UNI[3:6])
    assert w3[w3 > 0].tolist() == pytest.approx([1.0 / 3.0] * 3)


def test_benchmark_weights_equal_weight_all_candidates():
    monthly = random_monthly(K=200, first_listed={"EWS": 20, "EWH": 45}, gaps={"EWD": 90})
    panel, ends = step_panel(monthly)
    for kw in VARIANTS.values():
        w = m.weights(panel, **kw)
        b = m.benchmark_weights(panel, **kw)
        assert list(b.index) == list(w.index)                        # gleiche Signaltage
        for d in b.index:
            n = int((b.loc[d] > 0).sum())
            assert n >= 3
            assert b.loc[d][b.loc[d] > 0].tolist() == pytest.approx([1.0 / n] * n)
            assert b.loc[d].sum() == pytest.approx(1.0)
            assert set(w.loc[d][w.loc[d] > 0].index) <= set(b.loc[d][b.loc[d] > 0].index)   # Auswahl ⊂ Korb


def test_input_not_mutated_and_deterministic():
    panel = random_panel(n=3600, seed=4)
    snap_c, snap_o = panel.close.copy(), panel.open.copy()
    w1 = m.weights(panel)
    w2 = m.weights(panel)
    pd.testing.assert_frame_equal(w1, w2)
    pd.testing.assert_frame_equal(panel.close, snap_c)
    pd.testing.assert_frame_equal(panel.open, snap_o)


def test_empty_or_short_panel_returns_empty_frame():
    p = random_panel(n=40)
    w = m.weights(p)
    assert len(w) == 0
    assert set(w.columns) <= set(UNI)


# --------------------------------------------------------------------------------------
# Kausalität und Engine-Smoke
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", list(VARIANTS))
def test_causality(name):
    panel = random_panel(n=4400)
    kw = VARIANTS[name]
    assert check_causality(lambda p: m.weights(p, **kw), panel) == []


@pytest.mark.parametrize("name", list(VARIANTS))
def test_causality_cuts_around_signal_days(name):
    # Schnitte direkt auf/vor/nach Signaltagen (Dezember bzw. Juni), wo Fehler bei der Monatsende-Erkennung auftreten
    panel = random_panel(n=4400, seed=8)
    kw = VARIANTS[name]
    w = m.weights(panel, **kw)
    assert len(w) >= 3
    idx = panel.close.index
    cuts = []
    for d in w.index[:4]:
        pos = idx.get_loc(d)
        cuts += [idx[pos - 1], d, idx[pos + 1]]
    assert check_causality(lambda p: m.weights(p, **kw), panel, cuts=cuts) == []


def test_causality_with_nan_gaps():
    panel = random_panel(n=4400, seed=21)
    rng = np.random.default_rng(2)
    for t in ("EWC", "EWJ", "EWD"):
        pool = np.flatnonzero(panel.close[t].notna().to_numpy())
        bad = rng.choice(pool, size=40, replace=False)
        panel.close.iloc[bad, panel.close.columns.get_loc(t)] = np.nan
        panel.open.iloc[bad, panel.open.columns.get_loc(t)] = np.nan
    for kw in VARIANTS.values():
        assert check_causality(lambda p, _kw=kw: m.weights(p, **_kw), panel) == []


@pytest.mark.parametrize("name", list(VARIANTS))
def test_engine_runs_on_weights(name):
    panel = random_panel(n=4400)
    w = m.weights(panel, **VARIANTS[name])
    assert len(w) >= 3
    res = run_backtest(panel, w, cost=ZERO, rf=pd.Series(0.0, index=panel.close.index))
    assert np.isfinite(res.nav.to_numpy()).all() and (res.nav > 0).all()
    assert res.n_trades > 0
    assert res.skipped_orders == 0
    first_trade_day = res.turnover[res.turnover > 0].index[0]
    assert res.gross_exposure.loc[first_trade_day] == pytest.approx(1.0, abs=0.05)
    assert (res.weights.min() >= -1e-12).all()                       # nie short
