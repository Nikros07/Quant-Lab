"""Tests für strategies/antonacci_gem_lookback_ensemble.py auf synthetischen Panels (kein Netz, kein Datencache).

Bekannte Antworten: Preise mit konstanter Tageswachstumsrate g und ein konstantes ^IRX-Niveau. Dann stehen alle
Sleeves auf demselben Asset, und die Entscheidung hängt nur von g gegen den Cash-Zuwachs ab (der Zeilenfaktor
1 + irx/100/252 kürzt sich gegen exp(g) pro Zeile). Für gemischte Sleeves und die Drift dient eine
unabhängig geschriebene Referenz-Implementierung (reine Python-Schleifen) als Gegenprobe.
"""
import numpy as np
import pandas as pd
import pytest

from qlab.calendar import NYSE_BDAY, month_end_flags
from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import antonacci_gem_lookback_ensemble as G

COLS = ["SPY", "EFA", "AGG", "IEF", "ACWX", "^IRX"]
TRADE = ["SPY", "EFA", "AGG", "IEF", "ACWX"]
BASE = G.SPEC["params"]
LB = list(BASE["lookbacks"])


# --------------------------------------------------------------------------------------
# Hilfen
# --------------------------------------------------------------------------------------

def nyse_index(n, start="2008-01-02"):
    return pd.date_range(start, periods=n, freq=NYSE_BDAY)


def random_panel(n=1500, seed=11, start="2008-01-02"):
    rng = np.random.default_rng(seed)
    idx = nyse_index(n, start)
    ret = rng.normal(0.0003, 0.01, (n, len(TRADE)))
    close_t = 100.0 * np.exp(np.cumsum(ret, axis=0))
    gap = rng.normal(0.0, 0.003, (n, len(TRADE)))
    open_t = np.vstack([close_t[:1], close_t[:-1]]) * np.exp(gap)
    irx = 2.5 + 1.5 * np.sin(2 * np.pi * np.arange(n) / 500.0)         # Prozent
    close = pd.DataFrame(np.column_stack([close_t, irx]), index=idx, columns=COLS)
    open_ = pd.DataFrame(np.column_stack([open_t, irx]), index=idx, columns=COLS)
    return Panel(open_, close)


def trend_panel(growth: dict, irx=2.0, n=800, start="2010-01-04"):
    """Konstante log-Tageswachstumsrate je Ticker (Rest 0); open == close; ^IRX konstant (Prozent)."""
    idx = nyse_index(n, start)
    k = np.arange(n)[:, None]
    g = np.array([growth.get(t, 0.0) for t in TRADE])[None, :]
    close = pd.DataFrame(100.0 * np.exp(g * k), index=idx, columns=TRADE)
    close[G.RATE] = irx
    return Panel(close.copy(), close)


def cash_g(irx):
    """log-Wachstum je Zeile, bei dem ein Asset exakt den Cash-Zuwachs bei konstantem ^IRX (Prozent) erzielt."""
    return float(np.log(1.0 + irx / 100.0 / G.RF_DAYS))


def me_dates(idx):
    return idx[month_end_flags(idx).to_numpy()]


def reference(panel, lookbacks=LB, ex_us="EFA", bond="AGG", reset_month=12):
    """Unabhängige Referenz (Schleifen) für lückenfreie Panels: Entscheidungen + driftende Sleeves."""
    assets = [G.US, ex_us, bond]
    idx = panel.close.index
    cl = panel.close[assets].to_numpy(float)
    op = panel.open[assets].to_numpy(float)
    irx = panel.close[G.RATE].to_numpy(float)
    flags = month_end_flags(idx).to_numpy()
    me = [i for i in range(len(idx)) if flags[i]]
    ymap = {idx[i].year * 12 + idx[i].month: i for i in me}
    cash = np.ones(len(idx))
    for i in range(1, len(idx)):
        cash[i] = cash[i - 1] * (1.0 + irx[i - 1] / 100.0 / 252.0)
    K = len(lookbacks)
    rows = []
    for i in me:
        ym = idx[i].year * 12 + idx[i].month
        ch = []
        for L in lookbacks:
            j = ymap.get(ym - L)
            if j is None:
                break
            r = cl[i] / cl[j] - 1.0
            rc = cash[i] / cash[j] - 1.0
            if r[0] > rc:
                ch.append(1 if r[1] > r[0] else 0)
            else:
                ch.append(2)
        else:
            rows.append((i, ch))
    nav = [1.0 / K] * K
    prev_ch, last = None, None
    out, chs, dates = [], [], []
    for i, ch in rows:
        if last is not None:
            for d in range(last + 1, i + 1):
                for k in range(K):
                    h = prev_ch[k]
                    if d > last + 1:
                        nav[k] *= op[d, h] / cl[d - 1, h]                    # über Nacht (ab t+2)
                    nav[k] *= cl[d, h] / op[d, h]                            # tagsüber (ab Eröffnung t+1)
            s = sum(nav)
            nav = [x / s for x in nav]
        if reset_month is not None and idx[i].month == reset_month:
            nav = [1.0 / K] * K
        s = sum(nav)
        row = np.zeros(3)
        for k in range(K):
            row[ch[k]] += nav[k] / s
        out.append(row)
        chs.append(ch)
        dates.append(idx[i])
        prev_ch, last = list(ch), i
    w = pd.DataFrame(np.array(out).reshape(len(out), 3), index=pd.DatetimeIndex(dates), columns=assets)
    return w, np.array(chs).T.reshape(K, len(chs))


def one(series):
    """Alle Werte gleich 1 (Summe von Siebteln ist nur bis auf Rundung 1)."""
    return bool(((series - 1.0).abs() < 1e-12).all())


def last_row(w):
    return w.iloc[-1]


def assert_no_weight_on_nan(w, panel):
    px = panel.close.reindex(index=w.index, columns=w.columns)
    assert not ((w > 0) & px.isna()).any().any()


# --------------------------------------------------------------------------------------
# SPEC
# --------------------------------------------------------------------------------------

def test_spec_contract():
    s = G.SPEC
    assert s["id"] == "antonacci_gem_lookback_ensemble"
    assert s["family"] == "tactical" and s["sources"]
    assert set(TRADE) <= set(s["tickers"]) and G.RATE in s["tickers"]
    assert len(set(s["tickers"])) == len(s["tickers"])
    assert tuple(s["params"]["lookbacks"]) == (6, 7, 8, 9, 10, 11, 12)
    assert (s["params"]["ex_us"], s["params"]["bond"], s["params"]["reset_month"]) == ("EFA", "AGG", 12)
    assert 1 <= len(s["variants"]) <= 3
    for v in s["variants"].values():
        assert set(v) <= set(s["params"])
    assert all(s["cost_bps"][t] == 10.0 for t in TRADE)
    assert G.RATE not in s["cost_bps"]                                       # ^IRX wird nie gehandelt


# --------------------------------------------------------------------------------------
# Bekannte Antworten (alle Sleeves einig)
# --------------------------------------------------------------------------------------

def test_all_sleeves_pick_spy_and_first_signal_is_13th_month_end():
    p = trend_panel({"SPY": 0.0006, "EFA": 0.0003, "AGG": 0.0001})
    w = G.weights(p)
    me = me_dates(p.close.index)
    assert w.index[0] == me[12]                                              # L=12 braucht 12 Monatsenden Vorlauf
    assert list(w.index) == list(me[12:])
    assert list(w.columns) == ["SPY", "EFA", "AGG"]
    for _, row in w.iterrows():
        assert row.to_numpy() == pytest.approx([1.0, 0.0, 0.0], abs=1e-12)


def test_relative_momentum_picks_higher_exus_and_acwx_variant():
    p = trend_panel({"SPY": 0.0003, "EFA": 0.0006, "ACWX": 0.0009, "AGG": 0.0001})
    w = G.weights(p)
    assert one(w["EFA"]) and w[["SPY", "AGG"]].abs().to_numpy().max() == 0.0
    wa = G.weights(p, **{**BASE, **G.SPEC["variants"]["acwx"]})
    assert list(wa.columns) == ["SPY", "ACWX", "AGG"]
    assert one(wa["ACWX"])
    q = trend_panel({"SPY": 0.0009, "EFA": 0.0003, "ACWX": 0.0001})
    assert one(G.weights(q, ex_us="ACWX")["SPY"])


def test_tie_between_spy_and_exus_goes_to_spy():
    p = trend_panel({"SPY": 0.0006, "EFA": 0.0006})
    w = G.weights(p)
    assert one(w["SPY"])


def test_absolute_momentum_tests_spy_against_cash_not_exus():
    g = {"SPY": 0.00005, "EFA": 0.0008, "AGG": 0.0001, "IEF": 0.0002}       # SPY schwach, EFA stark
    p5 = trend_panel(g, irx=5.0)
    w = G.weights(p5)
    assert one(w["AGG"]) and w[["SPY", "EFA"]].abs().to_numpy().max() == 0.0
    p0 = trend_panel(g, irx=0.0)                                             # gleicher Kursverlauf, Cash 0 -> risk-on
    w0 = G.weights(p0)
    assert one(w0["EFA"])
    wi = G.weights(p5, **{**BASE, **G.SPEC["variants"]["bond_ief"]})
    assert list(wi.columns) == ["SPY", "EFA", "IEF"]
    assert one(wi["IEF"])


def test_negative_spy_with_zero_cash_goes_to_bond():
    p = trend_panel({"SPY": -0.0002, "EFA": 0.0008}, irx=0.0)
    w = G.weights(p)
    assert one(w["AGG"])


@pytest.mark.parametrize("irx", [0.5, 2.0, 4.5])
def test_cash_boundary_is_exactly_the_accrual(irx):
    c = cash_g(irx)
    above = trend_panel({"SPY": c + 1e-6, "EFA": c - 5e-4}, irx=irx)
    below = trend_panel({"SPY": c - 1e-6, "EFA": c + 5e-4}, irx=irx)
    assert one(G.weights(above)["SPY"])                            # knapp über Cash, strikt >
    assert one(G.weights(below)["AGG"])                            # knapp darunter -> Anleihen


def test_single_l12_variant_and_other_lookbacks_start_dates():
    p = trend_panel({"SPY": 0.0006})
    me = me_dates(p.close.index)
    w12 = G.weights(p, **{**BASE, **G.SPEC["variants"]["single_l12"]})
    assert w12.index[0] == me[12] and list(w12.index) == list(me[12:])
    w6 = G.weights(p, lookbacks=(6,))
    assert w6.index[0] == me[6]
    w69 = G.weights(p, lookbacks=(6, 9))
    assert w69.index[0] == me[9]                                             # erst, wenn jedes Sleeve ein Signal hat


# --------------------------------------------------------------------------------------
# Gemischte Sleeves, Drift, Dezember-Reset (Gegenprobe gegen die Referenz)
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("params", [
    {},
    {"reset_month": None},
    {"reset_month": 6},
    {"lookbacks": (12,)},
    {"lookbacks": (3, 5)},
    {"ex_us": "ACWX", "bond": "IEF"},
])
def test_weights_match_independent_reference(params):
    p = random_panel()
    w = G.weights(p, **{**BASE, **params})
    kw = {k: v for k, v in params.items() if k in ("ex_us", "bond", "reset_month")}
    if "lookbacks" in params:
        kw["lookbacks"] = list(params["lookbacks"])
    ref, _ = reference(p, **kw)
    assert len(w) > 20 and list(w.index) == list(ref.index)
    assert list(w.columns) == list(ref.columns)
    assert (w - ref).abs().to_numpy().max() < 1e-10


def test_mixed_sleeves_drift_and_december_reset():
    p = random_panel()
    w = G.weights(p)
    frac = ((w > 1e-9) & (w < 1 - 1e-9)).any(axis=1)
    assert frac.sum() >= 10                                                  # das Szenario enthält echte Sleeve-Splits
    sevenths = (w * 7.0 - (w * 7.0).round()).abs().max(axis=1) < 1e-9        # Vielfache von 1/7
    dec = w.index.month == 12
    assert dec.sum() >= 3
    assert sevenths[dec].all()                                               # im Dezember: Anteile exakt 1/7
    assert (~sevenths[~dec & frac.to_numpy()]).any()                         # sonst driften sie (keine glatten Siebtel)
    nodec = G.weights(p, **{**BASE, "reset_month": None})
    assert (nodec - w).abs().to_numpy().max() > 1e-6                         # ohne Reset anderes Ergebnis
    assert w.index.equals(nodec.index)


def test_drift_targets_hand_calculation():
    K, A = 2, 3
    on = np.ones((7, A))
    intr = np.ones((7, A))
    intr[1] = [1.10, 0.90, 1.0]
    on[2] = [1.20, 1.00, 1.0]
    on[3] = [1.00, 1.05, 1.0]            # Over-Night direkt nach dem Handelstag: geht NICHT in die Anteile ein
    intr[3] = [1.00, 1.02, 0.95]
    choice = np.array([[0, 1, 0], [1, 2, 2]])
    pos = np.array([0, 2, 5])
    out = G._drift_targets(choice, pos, np.array([False, False, False]), on, intr)
    assert out[0] == pytest.approx([0.5, 0.5, 0.0])
    # Tage 1-2 (Signal an Position 0): Sleeve 0 hält SPY (intraday 1.10, dann 1.20 * 1.0), Sleeve 1 hält EXUS (0.90)
    n0, n1 = 0.5 * 1.10 * 1.20, 0.5 * 0.90
    s0, s1 = n0 / (n0 + n1), n1 / (n0 + n1)
    assert out[1] == pytest.approx([0.0, s0, s1])                           # Sleeve 0 -> EXUS, Sleeve 1 -> Bond
    # Tage 3-5 (Signal an Position 2): Sleeve 0 hält EXUS (intraday 1.02), Sleeve 1 hält Bond (intraday 0.95)
    m0, m1 = s0 * 1.02, s1 * 0.95
    t0, t1 = m0 / (m0 + m1), m1 / (m0 + m1)
    assert out[2] == pytest.approx([t0, 0.0, t1])                           # Sleeve 0 -> SPY, Sleeve 1 -> Bond
    assert out[2].sum() == pytest.approx(1.0)
    out_r = G._drift_targets(choice, pos, np.array([False, False, True]), on, intr)
    assert out_r[2] == pytest.approx([0.5, 0.0, 0.5])                       # Reset: 1/K je Sleeve
    assert out_r[1] == pytest.approx(out[1])                                # vorher unverändert


def test_cash_factors_use_only_previous_day_and_flag_unknown():
    irx = pd.Series([2.52, 2.52, np.nan, 5.04], index=nyse_index(4))
    f = G._cash_factors(irx)
    assert np.isnan(f.iloc[0])
    assert f.iloc[1] == pytest.approx(1.0001)
    assert f.iloc[2] == pytest.approx(1.0001)
    assert np.isnan(f.iloc[3])                                               # Zins von gestern unbekannt
    a = pd.Series([2.52, 2.52, 2.52, 5.04], index=nyse_index(4))
    b = a.copy()
    b.iloc[3] = 99.0                                                         # heutiger Zins ändert nur spätere Faktoren
    assert G._cash_factors(a).equals(G._cash_factors(b))


# --------------------------------------------------------------------------------------
# Form, Wertebereich
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", ["base", "acwx", "single_l12", "bond_ief"])
def test_shape_range_and_exposure(variant):
    p = random_panel()
    params = dict(BASE) if variant == "base" else {**BASE, **G.SPEC["variants"][variant]}
    w = G.weights(p, **params)
    assert len(w) > 40
    assert list(w.columns) == ["SPY", params["ex_us"], params["bond"]]
    assert G.RATE not in w.columns
    assert w.index.is_monotonic_increasing and w.index.is_unique
    assert set(w.index) <= set(p.close.index)
    assert not w.isna().any().any()
    assert (w >= 0).all().all() and (w <= 1.0 + 1e-12).all().all()
    s = w.sum(axis=1)
    assert (s - 1.0).abs().max() < 1e-12                                     # voll investiert, kein Hebel, kein Cash
    me = me_dates(p.close.index)
    assert set(w.index) <= set(me)                                           # nur kausale Monatsenden
    if variant == "single_l12":
        assert set(np.round(w.to_numpy().ravel(), 12)) <= {0.0, 1.0}         # Konzentrationstest: 100 % in einem Asset


def test_short_history_gives_empty_frame():
    p = random_panel(n=200)                                                  # < 13 Monatsenden
    w = G.weights(p)
    assert len(w) == 0 and list(w.columns) == ["SPY", "EFA", "AGG"]
    w6 = G.weights(random_panel(n=1), lookbacks=(6,))
    assert len(w6) == 0


def test_parameter_validation():
    p = random_panel(n=300)
    with pytest.raises(ValueError):
        G.weights(p, lookbacks=())
    with pytest.raises(ValueError):
        G.weights(p, lookbacks=(6, 6))
    with pytest.raises(ValueError):
        G.weights(p, lookbacks=(0, 6))
    with pytest.raises(ValueError):
        G.weights(p, ex_us="SPY")
    with pytest.raises(ValueError):
        G.weights(p, bond="EFA")
    with pytest.raises(ValueError):
        G.weights(p, reset_month=13)
    with pytest.raises(KeyError):
        G.weights(Panel(p.open.drop(columns=["^IRX"]), p.close.drop(columns=["^IRX"])))
    with pytest.raises(KeyError):
        G.weights(p, ex_us="VEU")


def test_rate_ticker_never_gets_weight_and_other_tickers_stay_zero():
    p = random_panel()
    w = G.weights(p)
    assert set(w.columns) == {"SPY", "EFA", "AGG"}                           # IEF/ACWX/^IRX kommen im Hauptlauf nicht vor
    full = w.reindex(columns=COLS).fillna(0.0)
    assert full[["IEF", "ACWX", "^IRX"]].to_numpy().max() == 0.0


# --------------------------------------------------------------------------------------
# Fehlende Preise = nicht handelbar
# --------------------------------------------------------------------------------------

def test_late_listed_exus_blocks_signals_until_full_history():
    p = random_panel()
    close, open_ = p.close.copy(), p.open.copy()
    close.loc[close.index[:400], "EFA"] = np.nan
    open_.loc[open_.index[:400], "EFA"] = np.nan
    q = Panel(open_, close)
    w = G.weights(q)
    idx = q.close.index
    me = me_dates(idx)
    valid_from = q.close["EFA"].first_valid_index()
    me_valid = me[me >= valid_from]
    assert w.index.min() == me_valid[12]                                     # L=12 braucht 12 Monate EFA-Historie
    assert w.index.min() > idx[400]
    assert_no_weight_on_nan(w, q)


def test_acwx_variant_starts_after_acwx_history():
    p = random_panel()
    close, open_ = p.close.copy(), p.open.copy()
    close.loc[close.index[:300], "ACWX"] = np.nan
    open_.loc[open_.index[:300], "ACWX"] = np.nan
    q = Panel(open_, close)
    w = G.weights(q, **{**BASE, **G.SPEC["variants"]["acwx"]})
    me = me_dates(q.close.index)
    me_valid = me[me >= q.close["ACWX"].first_valid_index()]
    assert w.index.min() == me_valid[12]
    assert_no_weight_on_nan(w, q)


def test_missing_price_of_chosen_asset_on_signal_day_skips_that_signal():
    p = trend_panel({"SPY": 0.0006, "EFA": 0.0003}, n=900)
    idx = p.close.index
    me = me_dates(idx)
    t_star = me[20]
    close, open_ = p.close.copy(), p.open.copy()
    close.loc[t_star, "SPY"] = np.nan
    open_.loc[t_star, "SPY"] = np.nan
    q = Panel(open_, close)
    w = G.weights(q)
    assert t_star not in w.index                                             # SPY gewählt, aber nicht handelbar
    for d in me[21:34]:                                                      # 1-Tage-Lücke blockiert die Historie nicht
        assert d in w.index
    assert_no_weight_on_nan(w, q)


def test_missing_price_of_unchosen_asset_does_not_block_and_gets_no_weight():
    p = trend_panel({"SPY": 0.0006, "EFA": 0.0003}, n=900)
    idx = p.close.index
    me = me_dates(idx)
    t_star = me[20]
    close, open_ = p.close.copy(), p.open.copy()
    close.loc[t_star, "AGG"] = np.nan
    open_.loc[t_star, "AGG"] = np.nan
    q = Panel(open_, close)
    w = G.weights(q)
    assert t_star in w.index and w.loc[t_star, "AGG"] == 0.0
    assert_no_weight_on_nan(w, q)


def test_delisted_asset_stops_signals_and_never_gets_weight():
    p = random_panel()
    close, open_ = p.close.copy(), p.open.copy()
    cut = 900
    close.loc[close.index[cut:], "EFA"] = np.nan
    open_.loc[open_.index[cut:], "EFA"] = np.nan
    q = Panel(open_, close)
    w = G.weights(q)
    assert len(w) > 0
    assert_no_weight_on_nan(w, q)
    # nach der Einstellung kein gültiges Rendite-Fenster mehr (Ex-US-Rendite fehlt) -> keine Zeilen später als ~5 Tage
    assert w.index.max() <= q.close.index[cut + G.FFILL_LIMIT]


def test_long_gap_in_history_gives_no_weight_on_nan_and_no_crash():
    p = random_panel()
    close, open_ = p.close.copy(), p.open.copy()
    rows = close.index[600:625]                                              # 25 Tage Lücke, länger als FFILL_LIMIT
    close.loc[rows, "SPY"] = np.nan
    open_.loc[rows, "SPY"] = np.nan
    q = Panel(open_, close)
    w = G.weights(q)
    ref_len = len(G.weights(p))
    assert 0 < len(w) < ref_len                                              # betroffene Fenster fallen aus
    assert not w.isna().any().any()
    assert_no_weight_on_nan(w, q)
    assert (w.sum(axis=1) - 1.0).abs().max() < 1e-12


def test_irx_gap_invalidates_only_windows_that_contain_it():
    p = random_panel()
    close, open_ = p.close.copy(), p.open.copy()
    gap = close.index[500:540]                                               # 40 Tage ^IRX unbekannt
    close.loc[gap, "^IRX"] = np.nan
    open_.loc[gap, "^IRX"] = np.nan
    q = Panel(open_, close)
    w = G.weights(q)
    idx = q.close.index
    irx_f = q.close["^IRX"].ffill(limit=G.FFILL_LIMIT)
    bad = irx_f.shift(1).isna().to_numpy()                                   # Tage ohne bekannten Vortageszins
    me = me_dates(idx)
    pos = {d: i for i, d in enumerate(idx)}
    expect = []
    for j in range(12, len(me)):
        a, b = pos[me[j - 12]], pos[me[j]]
        if not bad[a + 1:b + 1].any():                                       # L=12-Fenster enthält alle kürzeren
            expect.append(me[j])
    assert list(w.index) == expect
    assert len(expect) < len(me) - 12
    assert_no_weight_on_nan(w, q)


# --------------------------------------------------------------------------------------
# Kausalität
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", ["base", "acwx", "single_l12", "bond_ief"])
def test_check_causality_passes(variant):
    p = random_panel()
    params = dict(BASE) if variant == "base" else {**BASE, **G.SPEC["variants"][variant]}
    assert check_causality(lambda pp, _pa=params: G.weights(pp, **_pa), p, n_cuts=9) == []


def test_check_causality_with_nan_history_and_irx_gap():
    p = random_panel()
    close, open_ = p.close.copy(), p.open.copy()
    close.loc[close.index[:300], "EFA"] = np.nan
    open_.loc[open_.index[:300], "EFA"] = np.nan
    close.loc[close.index[700:720], "^IRX"] = np.nan
    q = Panel(open_, close)
    assert check_causality(lambda pp: G.weights(pp, **BASE), q, n_cuts=9) == []


def test_future_prices_do_not_change_past_weights():
    p = random_panel()
    cut = p.close.index[1000]
    close, open_ = p.close.copy(), p.open.copy()
    after = close.index > cut
    close.loc[after, TRADE] *= 7.0
    open_.loc[after, TRADE] *= 7.0
    close.loc[after, "^IRX"] += 3.0
    q = Panel(open_, close)
    a = G.weights(p, **BASE).loc[:cut]
    b = G.weights(q, **BASE).loc[:cut]
    assert list(a.index) == list(b.index) and len(a) > 0
    assert (a - b).abs().to_numpy().max() < 1e-12


# --------------------------------------------------------------------------------------
# Zusammenspiel mit der Engine
# --------------------------------------------------------------------------------------

def test_engine_runs_fully_invested_without_skipped_orders():
    p = random_panel()
    w = G.weights(p, **BASE)
    zero = CostModel(default_bps=0.0, short_fee_annual=0.0, lever_spread_annual=0.0)
    res = run_backtest(p, w, cost=zero, rf=pd.Series(0.0, index=p.close.index))
    assert res.skipped_orders == 0
    assert np.isfinite(res.nav).all() and (res.nav > 0).all()
    assert res.gross_exposure.max() <= 1.0 + 1e-6                            # nie gehebelt
    start = int(p.close.index.get_loc(w.index[0])) + 1                       # Handel zur Eröffnung des Folgetags
    assert res.gross_exposure.iloc[start:].min() > 0.9                       # danach voll investiert
    assert res.weights[G.RATE].abs().max() == 0.0                            # nie Gewicht auf ^IRX
    costed = run_backtest(p, w, cost=CostModel(per_ticker_bps=G.SPEC["cost_bps"]),
                          rf=pd.Series(0.0, index=p.close.index))
    assert costed.cost.sum() > 0 and costed.n_trades > 0


def test_sim_matches_engine_drift_on_every_row():
    """Die vom Modul mitgeführten Sleeve-Anteile müssen zur Engine passen: Behielte jedes Sleeve zwischen zwei
    Signalen sein Asset, wäre die (nur durch Kurse gedriftete) Engine-Position gleich dem neuen Zielgewicht.
    Das hypothetische 'kein Wechsel'-Ziel wird je Zeile aus der Referenz-Entscheidung gebildet und gegen die
    tatsächliche Engine-Position am Signaltag geprüft (Dezember-Reset in der Zeile selbst ausgenommen)."""
    p = random_panel()
    w = G.weights(p, **BASE)
    _, choice = reference(p)
    idx = p.close.index
    cols = ["SPY", "EFA", "AGG"]
    cl, op = p.close[cols].to_numpy(float), p.open[cols].to_numpy(float)
    on = np.ones_like(cl)
    on[1:] = op[1:] / cl[:-1]
    intr = cl / op
    pos = np.array([idx.get_loc(t) for t in w.index])
    reset = np.asarray(w.index.month == 12)
    zero = CostModel(default_bps=0.0, short_fee_annual=0.0, lever_spread_annual=0.0)
    res = run_backtest(p, w, cost=zero, rf=pd.Series(0.0, index=idx))
    switched = 0
    for e in range(1, len(w)):
        cm = choice[:, :e + 1].copy()
        cm[:, e] = cm[:, e - 1]                                              # hypothetisch: kein Sleeve wechselt
        rs = reset[:e + 1].copy()
        rs[e] = False                                                        # die Engine setzt am Signaltag nichts zurück
        hyp = G._drift_targets(cm, pos[:e + 1], rs, on, intr)[e]
        real = res.weights.loc[w.index[e], cols].to_numpy(float)
        assert real == pytest.approx(hyp, abs=1e-9)
        if not (choice[:, e] == choice[:, e - 1]).all():
            switched += 1
    assert switched >= 5                                                     # das Szenario enthält echte Wechsel
