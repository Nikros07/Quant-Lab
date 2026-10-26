"""Tests der Faber-Sektorrotation (Langzeit-Check auf French-Industrien + gemeinsamer Kern).

Alles auf synthetischen Panels: kein Netz, kein Datencache. Bekannte Antworten statt Vertrauen:
eine unabhängig geschriebene Referenz (reines Python/Pandas, Monatsenden über groupby auf den
vollständigen Testdaten) muss dieselben Gewichte liefern wie die Strategie.
"""
import numpy as np
import pandas as pd
import pytest

from qlab.calendar import NYSE_BDAY
from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import sector_etf_top3_12m as mod
from strategies.sector_etf_top3_12m import INDUSTRIES, MARKET, SPEC, _select, rotation_weights, weights

VARIANTS = ["base"] + sorted(SPEC["variants"])


def params_for(variant: str) -> dict:
    return dict(SPEC["params"]) if variant == "base" else {**SPEC["params"], **SPEC["variants"][variant]}


def make_panel(names, start="2004-01-01", end="2008-12-31", seed=0, drifts=None, vol=0.012):
    """Zufallspfade auf dem NYSE-Kalender; Ende = Monatsende, damit der letzte Tag ein echtes Monatsende ist."""
    idx = pd.date_range(start, end, freq=NYSE_BDAY)
    rng = np.random.default_rng(seed)
    closes = {}
    for k, t in enumerate(names):
        mu = drifts[k] if drifts is not None else rng.normal(0.0003, 0.0005)
        closes[t] = 100.0 * np.exp(np.cumsum(rng.normal(mu, vol, len(idx))))
    close = pd.DataFrame(closes, index=idx)
    open_ = close.shift(1).fillna(close.iloc[0]) * (1.0 + rng.normal(0.0, 0.002, close.shape))
    return Panel(open_, close)


def true_month_ends(idx: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Unabhängige Monatsenden (nur gültig, wenn die Daten selbst mit einem vollständigen Monat enden)."""
    s = pd.Series(idx, index=idx)
    return pd.DatetimeIndex(s.groupby([idx.year, idx.month]).max().to_numpy())


def regime_market(idx, seed=5):
    """Steigt, fällt dann deutlich, steigt wieder: erzeugt Risk-on- und Risk-off-Phasen."""
    rng = np.random.default_rng(seed)
    n = len(idx)
    mu = np.where(np.arange(n) < 500, 0.0010, np.where(np.arange(n) < 900, -0.0020, 0.0015))
    return pd.Series(100.0 * np.exp(np.cumsum(mu + rng.normal(0, 0.004, n))), index=idx)


def reference_weights(close, names, lookback=12, top_n=3, hold_rank=0, combo=False, market=None, sma_n=0):
    """Absichtlich anders gebaut als die Strategie: Namen statt Indizes, Schleife über Monatsenden."""
    names = sorted(names)
    me = close.loc[true_month_ends(close.index), names]
    mkt_me = market.loc[me.index] if market is not None else None
    ks = mod.COMBO_MONTHS if combo else (lookback,)
    rows, held = {}, []
    for i in range(len(me)):
        if i < max(ks):
            continue
        score = {n: float(np.mean([me[n].iloc[i] / me[n].iloc[i - k] - 1.0 for k in ks])) for n in names}
        score = {n: s for n, s in score.items() if np.isfinite(s)}
        if len(score) < top_n:
            continue
        if sma_n:
            if i < sma_n - 1:
                continue
            sma = mkt_me.iloc[i - sma_n + 1:i + 1].mean()
            if mkt_me.iloc[i] < sma:
                rows[me.index[i]] = {n: 0.0 for n in names}
                held = []
                continue
        ranked = sorted(score, key=lambda n: (-score[n], n))
        chosen = []
        if hold_rank:
            chosen = [n for n in ranked if n in held and ranked.index(n) + 1 <= hold_rank][:top_n]
        for n in ranked:
            if len(chosen) < top_n and n not in chosen:
                chosen.append(n)
        rows[me.index[i]] = {n: (1.0 / top_n if n in chosen else 0.0) for n in names}
        held = chosen
    return pd.DataFrame.from_dict(rows, orient="index", columns=names)


@pytest.fixture(scope="module")
def panel():
    names = INDUSTRIES + [MARKET]
    p = make_panel(names, seed=11)
    p.close[MARKET] = regime_market(p.close.index)
    p.open[MARKET] = p.close[MARKET]
    return p


# ------------------------------------------------------------------ Form und Wertebereich

@pytest.mark.parametrize("variant", VARIANTS)
def test_shape_and_value_range(panel, variant):
    w = weights(panel, **params_for(variant))
    assert list(w.columns) == sorted(INDUSTRIES)          # Markt-Spalte wird nie gehandelt
    assert MARKET not in w.columns
    assert len(w) > 20
    assert not w.isna().any().any()
    assert w.index.is_monotonic_increasing and w.index.is_unique
    assert set(w.index) <= set(true_month_ends(panel.close.index))     # nur echte Monatsenden
    assert ((w == 0.0) | np.isclose(w, 1.0 / 3.0)).all().all()
    s = w.sum(axis=1)
    assert (s <= 1.0 + 1e-12).all()                       # kein Hebel
    n_pos = (w > 0).sum(axis=1)
    if variant == "sma10":
        assert set(n_pos.unique()) <= {0, 3}
        assert np.allclose(s[n_pos == 0], 0.0)
    else:
        assert (n_pos == 3).all() and np.allclose(s, 1.0)


def test_first_signal_needs_twelve_months_of_history(panel):
    w = weights(panel)
    me = true_month_ends(panel.close.index)
    assert w.index[0] == me[12]                           # kein Skip-Monat, kein früheres Signal


@pytest.mark.parametrize("variant", VARIANTS)
def test_matches_independent_reference(panel, variant):
    p = params_for(variant)
    got = weights(panel, **p)
    ref = reference_weights(panel.close[INDUSTRIES], INDUSTRIES, lookback=p["lookback_months"], top_n=p["top_n"],
                            hold_rank=p["hold_rank"], combo=p["combo"], market=panel.close[MARKET],
                            sma_n=p["cash_filter_months"])
    assert len(ref) > 20
    pd.testing.assert_frame_equal(got, ref, check_freq=False, check_dtype=False)


def test_known_ranking_with_deterministic_growth():
    """Titel wachsen mit festen, verschiedenen Raten: die drei schnellsten sind bekannt."""
    idx = pd.bdate_range("2004-01-01", "2006-12-29")
    names = sorted(INDUSTRIES)
    rates = {n: 0.0001 * (k + 1) for k, n in enumerate(reversed(names))}      # letzter Name = langsamster
    close = pd.DataFrame({n: 100.0 * (1.0 + rates[n]) ** np.arange(len(idx)) for n in names}, index=idx)
    p = Panel(close.copy(), close)
    w = weights(p)
    fastest = sorted(names, key=lambda n: -rates[n])[:3]
    assert len(w) > 10
    for _, row in w.iterrows():
        assert sorted(row[row > 0].index) == sorted(fastest)


# ------------------------------------------------------------------ Gleichstand, fehlende Preise

def test_ties_are_broken_alphabetically():
    idx = pd.bdate_range("2004-01-01", "2005-12-30")
    names = sorted(INDUSTRIES)
    flat = pd.DataFrame(100.0, index=idx, columns=names)
    w = weights(Panel(flat.copy(), flat))
    assert len(w) > 0
    for _, row in w.iterrows():
        assert list(row[row > 0].index) == names[:3]


def test_partial_tie_picks_alphabetically_first():
    """Zwei Titel mit identischem Score auf Rang 3/4: der alphabetisch frühere kommt in die Top 3."""
    names = ["Aa", "Bb", "Cc", "Dd", "Ee"]
    score = np.array([0.5, 0.4, 0.3, 0.3, 0.1])                         # Cc und Dd gleichauf
    assert _select(score, top_n=3, hold_rank=0, held=[]) == [0, 1, 2]
    assert names[2] == "Cc"


def test_unlisted_ticker_gets_no_weight_and_short_universe_gives_no_signal():
    names = INDUSTRIES + [MARKET]
    p = make_panel(names, seed=3)
    late = "Utils"
    p.close.loc[p.close.index[:400], late] = np.nan                     # erst ab Tag 400 gelistet
    p.open.loc[p.open.index[:400], late] = np.nan
    w = weights(p)
    first_valid = p.close.index[400]
    month_ends = true_month_ends(p.close.index)
    # Score braucht Kurs bei t UND t-12 Monate: frühestens 12 Monate nach dem ersten gültigen Monatsende
    first_me = [d for d in month_ends if d >= first_valid][0]
    earliest = first_me.to_period("M") + 12
    assert (w.loc[w.index.to_period("M") < earliest, late] == 0.0).all()    # bei zu wenig bewertbaren Titeln (< 3) entsteht gar kein Signal
    q = make_panel(names, seed=4)
    for t in INDUSTRIES[:8]:
        q.close[t] = np.nan
        q.open[t] = np.nan
    assert len(weights(q)) == 0


def test_nan_price_on_signal_day_is_never_selected():
    names = INDUSTRIES + [MARKET]
    # "Durbl" ist mit Abstand der Gewinner, hat aber am Signaltag keinen Kurs
    drifts = [0.0002] * len(names)
    drifts[names.index("Durbl")] = 0.004
    p = make_panel(names, seed=8, drifts=drifts, vol=0.004)
    me = true_month_ends(p.close.index)
    target = me[20]
    p.close.loc[target, "Durbl"] = np.nan
    w = weights(p)
    assert w.loc[target, "Durbl"] == 0.0
    assert w.loc[me[19], "Durbl"] > 0.0 and w.loc[me[21], "Durbl"] > 0.0
    assert w.loc[me[32], "Durbl"] == 0.0                                 # 12 Monate später fehlt t-12
    assert not w.isna().any().any()


# ------------------------------------------------------------------ Varianten

def test_combo_score_is_mean_of_five_horizons(panel):
    me = panel.close.loc[true_month_ends(panel.close.index), sorted(INDUSTRIES)]
    got = mod._scores(me, 12, combo=True)
    i = 30
    expect = np.mean([me.iloc[i] / me.iloc[i - k] - 1.0 for k in (1, 3, 6, 9, 12)], axis=0)
    assert np.allclose(got.iloc[i].to_numpy(), expect)
    assert got.iloc[:12].isna().all().all()                              # 12 Monate Vorlauf nötig
    single = mod._scores(me, 12, combo=False)
    assert np.allclose(single.iloc[i].to_numpy(), (me.iloc[i] / me.iloc[i - 12] - 1.0).to_numpy())


def test_sma10_goes_to_cash_exactly_when_market_below_average(panel):
    w = weights(panel, **params_for("sma10"))
    me = true_month_ends(panel.close.index)
    mkt = panel.close[MARKET].loc[me]
    sma = mkt.rolling(10).mean()
    off = w.sum(axis=1) == 0.0
    assert off.any() and (~off).any()                                    # Szenario enthält beide Phasen
    expected_off = (mkt < sma).loc[w.index]
    assert (off == expected_off).all()
    assert not w.isna().any().any()                                      # Cash = ausdrückliche Nullzeile, nicht NaN


def test_hold_buffer_select_logic():
    score = np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3])               # Rang = Index + 1
    # gehalten: Rang 4 und Rang 2 bleiben (<= 5), Rang 6 fliegt raus; Auffüllen mit bestplatzierten
    assert sorted(_select(score, 3, 5, held=[3, 1, 5])) == [0, 1, 3]
    # kein Puffer: reine Top 3
    assert sorted(_select(score, 3, 0, held=[3, 1, 5])) == [0, 1, 2]
    # gehaltener Titel ohne Score (NaN) wird nicht behalten
    s2 = score.copy()
    s2[3] = np.nan
    assert sorted(_select(s2, 3, 5, held=[3, 1])) == [0, 1, 2]
    # alle drei gehalten und noch in den Top 5: nichts ändert sich, auch wenn sie nicht die Top 3 sind
    assert sorted(_select(score, 3, 5, held=[2, 3, 4])) == [2, 3, 4]


def test_hold_buffer_keeps_held_names_while_rank_at_most_five(panel):
    me = panel.close.loc[true_month_ends(panel.close.index), sorted(INDUSTRIES)]
    rank = mod._scores(me, 12, combo=False).rank(axis=1, ascending=False, method="first")   # Spalten alphabetisch
    w = weights(panel, **params_for("hold_buffer"))
    n_kept = 0
    for prev, cur in zip(w.index[:-1], w.index[1:]):
        held = w.columns[w.loc[prev] > 0]
        keep = [n for n in held if rank.loc[cur, n] <= 5]
        n_kept += len(keep)
        assert (w.loc[cur, keep] > 0).all()
    assert n_kept > 0


# ------------------------------------------------------------------ Kausalität

@pytest.mark.parametrize("variant", VARIANTS)
def test_check_causality_on_synthetic_panel(panel, variant):
    p = params_for(variant)
    assert check_causality(lambda pp: weights(pp, **p), panel) == []


def test_causality_with_missing_data():
    names = INDUSTRIES + [MARKET]
    p = make_panel(names, seed=21)
    p.close.loc[p.close.index[:300], "Hlth"] = np.nan
    p.close.loc[p.close.index[700:705], "Shops"] = np.nan
    assert check_causality(lambda pp: weights(pp), p) == []


def test_no_signal_for_incomplete_last_month(panel):
    """Mitten im Monat abgeschnittene Daten: der angefangene Monat darf kein Signal erzeugen."""
    me = true_month_ends(panel.close.index)
    cut = me[30] + pd.Timedelta(days=9)
    part = panel.truncate(cut)
    w = weights(part)
    assert w.index.max() == me[30]
    assert w.index.max() <= part.close.index[-1]


def test_weights_do_not_depend_on_future_prices(panel):
    """Preise nach dem Schnitt verändern: Gewichte bis zum Schnitt bleiben identisch."""
    me = true_month_ends(panel.close.index)
    cut = me[35]
    base = weights(panel)
    q = Panel(panel.open.copy(), panel.close.copy())
    q.close.loc[q.close.index > cut, :] *= np.random.default_rng(0).uniform(0.3, 3.0, (int((q.close.index > cut).sum()), q.close.shape[1]))
    alt = weights(q)
    pd.testing.assert_frame_equal(base.loc[:cut], alt.loc[:cut], check_freq=False)


# ------------------------------------------------------------------ Engine-Integration, SPEC, Laden

def test_runs_through_engine_without_leverage(panel):
    w = weights(panel)
    res = run_backtest(panel, w, cost=CostModel(default_bps=5.0), rf=pd.Series(0.0, index=panel.close.index))
    assert np.isfinite(res.nav).all() and (res.nav > 0).all()
    assert res.skipped_orders == 0
    assert res.gross_exposure.max() <= 1.02                              # voll investiert, höchstens Kosten-Schlupf
    assert (res.weights[MARKET].abs() < 1e-12).all()                     # Markt-Spalte nie gehandelt


def test_spec_contract_and_variants_run(panel):
    assert SPEC["id"] == "sector_etf_top3_12m"
    assert SPEC["family"] == "xsmom"
    assert len(SPEC["variants"]) <= 3
    assert set(SPEC["variants"]) == {"combo", "sma10", "hold_buffer"}
    for v in SPEC["variants"].values():
        assert set(v) <= set(SPEC["params"])
    assert SPEC["params"]["lookback_months"] == 12 and SPEC["params"]["top_n"] == 3
    assert len(INDUSTRIES) == 10 and len(set(INDUSTRIES)) == 10
    for variant in VARIANTS:
        assert len(weights(panel, **params_for(variant))) > 20


def test_missing_universe_or_market_raises(panel):
    with pytest.raises(KeyError):
        weights(Panel(panel.open.drop(columns=["Hlth"]), panel.close.drop(columns=["Hlth"])))
    nomkt = Panel(panel.open.drop(columns=[MARKET]), panel.close.drop(columns=[MARKET]))
    assert len(weights(nomkt)) > 0                                       # Basis braucht den Markt nicht
    with pytest.raises(KeyError):
        weights(nomkt, cash_filter_months=10)


def test_build_panel_from_returns_is_untruncated_and_open_equals_close():
    idx = pd.bdate_range("2000-01-03", periods=300)
    rng = np.random.default_rng(2)
    ind = pd.DataFrame(rng.normal(0.0003, 0.01, (300, 10)), index=idx, columns=INDUSTRIES)
    mkt = pd.Series(rng.normal(0.0003, 0.01, 300), index=idx)
    p = mod.build_panel(ind, mkt)
    assert list(p.close.columns) == INDUSTRIES + [MARKET]
    assert p.close.index.equals(idx)
    assert p.open.equals(p.close)
    assert np.isclose(p.close[MARKET].iloc[1] / p.close[MARKET].iloc[0], 1.0 + mkt.iloc[1])


def test_rotation_weights_rejects_bad_params():
    p = make_panel(["A", "B", "C", "D"], seed=1)
    with pytest.raises(ValueError):
        rotation_weights(p.close, ["A", "B", "C", "D"], top_n=0)
    with pytest.raises(ValueError):
        rotation_weights(p.close, ["A", "B", "C", "D"], top_n=3, hold_rank=2)
