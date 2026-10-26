"""Tests für strategies/ivp_risk_parity_unlevered.py auf synthetischen Panels (kein Netz, kein Datencache).

Bekannte Antworten
* Renditen +-s_i im Wechsel (Mittel ~0): die Stichproben-Std ist s_i * c mit demselben Faktor c für alle Assets,
  also ist die Inverse-Vol-Gewichtung exakt (1/s_i) / sum(1/s_j).
* Diagonale Kovarianz: ERC = Inverse Vol, HRP = Inverse Varianz. Konstante Korrelation: ERC = Inverse Vol.
* Unabhängige Referenz für Inverse Vol: pandas rolling(756, min_periods=504).std() auf pct_change.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import NYSE_BDAY, month_end_flags
from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import ivp_risk_parity_unlevered as M

T = M.TICKERS
N9 = len(T)
BASE = M.SPEC["params"]
VARIANTS = M.SPEC["variants"]
ALL_RUNS = {"base": dict(BASE), **{k: {**BASE, **v} for k, v in VARIANTS.items()},
            "equal": {**BASE, **M.SPEC["controls"]["equal_weight_u9"]}}
ZERO = CostModel(default_bps=0.0, short_fee_annual=0.0, lever_spread_annual=0.0)


# --------------------------------------------------------------------------------------
# Hilfen
# --------------------------------------------------------------------------------------

def nyse_index(n, start="2008-01-02"):
    return pd.date_range(start, periods=n, freq=NYSE_BDAY)


def panel_from_ret(ret: np.ndarray, start="2008-01-02", seed=11) -> Panel:
    n = ret.shape[0]
    idx = nyse_index(n, start)
    close = pd.DataFrame(100.0 * np.cumprod(1.0 + ret, axis=0), index=idx, columns=T)
    gap = np.random.default_rng(seed).normal(0.0, 0.002, (n, N9))
    open_ = close.shift(1).fillna(close.iloc[0]) * np.exp(gap)
    return Panel(open_, close)


def random_panel(n=1250, seed=7, start="2008-01-02") -> Panel:
    rng = np.random.default_rng(seed)
    vols = np.linspace(0.004, 0.018, N9)                         # verschiedene Volatilitäten je Asset
    common = rng.normal(0.0, 0.004, (n, 1))                      # gemeinsamer Faktor -> Korrelationen
    ret = rng.normal(0.0003, 1.0, (n, N9)) * vols + 0.5 * common
    return panel_from_ret(ret, start, seed)


def alt_panel(sig, n=1250, start="2008-01-02", change_at=None, sig_late=None) -> Panel:
    """Renditen +-s_i im Wechsel; optional ab Zeile `change_at` mit anderen s_i."""
    sign = np.where(np.arange(n) % 2 == 0, 1.0, -1.0)[:, None]
    s = np.tile(np.asarray(sig, float), (n, 1))
    if change_at is not None:
        s[change_at:] = np.asarray(sig_late, float)
    return panel_from_ret(sign * s, start)


def with_nan(p: Panel, ticker, rows) -> Panel:
    close, open_ = p.close.copy(), p.open.copy()
    close.loc[rows, ticker] = np.nan
    open_.loc[rows, ticker] = np.nan
    return Panel(open_, close)


def month_ends(idx):
    return idx[month_end_flags(idx).to_numpy()]


def assert_no_weight_on_nan(w, panel):
    px = panel.close.reindex(index=w.index, columns=w.columns)
    assert not ((w > 0) & px.isna()).any().any()


def ref_ivp(panel, window=756, min_obs=504):
    """Unabhängige Referenz: Inverse Vol aus pandas rolling-Std, an allen Tagen."""
    r = panel.close[T].pct_change(fill_method=None)
    sig = r.rolling(window, min_periods=min_obs).std() * np.sqrt(252)
    inv = 1.0 / sig
    return inv.div(inv.sum(axis=1), axis=0)


# --------------------------------------------------------------------------------------
# SPEC
# --------------------------------------------------------------------------------------

def test_spec_contract():
    s = M.SPEC
    assert s["id"] == "ivp_risk_parity_unlevered"
    assert s["tickers"] == ["VTI", "EFA", "EEM", "VNQ", "IEF", "TLT", "TIP", "GLD", "DBC"]
    assert len(set(s["tickers"])) == N9
    assert s["family"] == "riskparity" and s["sources"]
    assert 1 <= len(s["variants"]) <= 3
    for v in s["variants"].values():
        assert set(v) <= set(s["params"])
    assert s["params"] == {"scheme": "ivp", "window": 756, "min_obs": 504}
    assert set(s["variants"]) == {"erc_lw", "hrp_252", "window_252"}
    assert "equal" not in [v.get("scheme") for v in s["variants"].values()]       # 1/N ist Kontrolle, keine Variante
    assert s["controls"]["equal_weight_u9"] == {"scheme": "equal"}
    assert "cost_bps" not in s or all(v >= 0 for v in s["cost_bps"].values())


# --------------------------------------------------------------------------------------
# Bausteine: Ledoit-Wolf, ERC, HRP
# --------------------------------------------------------------------------------------

def test_ledoit_wolf_matches_loop_reference_and_properties():
    rng = np.random.default_rng(3)
    for n in (40, 120, 600):
        rows = rng.normal(0, 1, (n, 5)) @ rng.normal(0, 1, (5, 5)) * np.array([1, 2, 3, 4, 5.0]) + 0.1
        corr, delta = M.ledoit_wolf_corr(rows)
        # Schleifen-Referenz der Formel (Ledoit/Wolf 2004, Ziel = Einheitsmatrix)
        z = (rows - rows.mean(0)) / rows.std(0)
        p = z.shape[1]
        s = z.T @ z / n
        m = np.trace(s) / p
        d2 = np.sum((s - m * np.eye(p)) ** 2) / p
        acc = 0.0
        for k in range(n):
            acc += np.sum((np.outer(z[k], z[k]) - s) ** 2)
        b2 = min(acc / (n ** 2 * p), d2)
        ref_delta = b2 / d2
        assert delta == pytest.approx(ref_delta, abs=1e-12)
        assert 0.0 <= delta <= 1.0
        assert corr == pytest.approx(ref_delta * m * np.eye(p) + (1 - ref_delta) * s, abs=1e-12)
        assert np.allclose(np.diag(corr), 1.0) and np.allclose(corr, corr.T)
        assert np.linalg.eigvalsh(corr).min() > 0
    # Daten mit echter Korrelationsstruktur (gemeinsamer Faktor): weniger Beobachtungen -> mehr Schrumpfung
    def factor_rows(n):
        return 0.8 * rng.normal(0, 1, (n, 1)) + rng.normal(0, 1, (n, 6))
    d_small = M.ledoit_wolf_corr(factor_rows(30))[1]
    d_large = M.ledoit_wolf_corr(factor_rows(3000))[1]
    assert 0.0 < d_large < d_small <= 1.0
    # unkorrelierte Daten: das Ziel (Einheitsmatrix) ist die Wahrheit -> volle Schrumpfung, Korrelation = Einheitsmatrix
    corr, delta = M.ledoit_wolf_corr(rng.normal(0, 1, (3000, 6)))
    assert delta == pytest.approx(1.0, abs=1e-12) and corr == pytest.approx(np.eye(6), abs=1e-12)


def test_ledoit_wolf_constant_series_returns_none():
    rows = np.random.default_rng(1).normal(0, 1, (100, 4))
    rows[:, 2] = 0.01
    assert M.ledoit_wolf_corr(rows) == (None, None)


def test_erc_known_answers_and_equal_risk_contributions():
    sd = np.array([0.1, 0.2, 0.3, 0.05, 0.4])
    inv = (1 / sd) / (1 / sd).sum()
    assert M.erc_weights(np.diag(sd ** 2)) == pytest.approx(inv, abs=1e-10)         # diagonal: ERC = Inverse Vol
    cc = 0.4 * np.ones((5, 5)) + 0.6 * np.eye(5)
    assert M.erc_weights(np.outer(sd, sd) * cc) == pytest.approx(inv, abs=1e-9)     # konstante Korrelation: ERC = Inverse Vol
    rng = np.random.default_rng(5)
    for _ in range(25):
        a = rng.normal(0, 1, (9, 9))
        cov = a @ a.T / 9 + 0.05 * np.eye(9)
        w = M.erc_weights(cov)
        assert w.sum() == pytest.approx(1.0) and (w > 0).all()
        rc = w * (cov @ w) / float(w @ cov @ w)
        assert np.abs(rc - 1 / 9).max() < 1e-6


def test_hrp_known_answers():
    assert M.hrp_weights(np.array([[2.0]])) == pytest.approx([1.0])
    cov2 = np.array([[0.04, 0.01], [0.01, 0.01]])
    iv = 1 / np.diag(cov2)
    assert M.hrp_weights(cov2) == pytest.approx(iv / iv.sum())                      # 2 Assets: Inverse Varianz
    sd = np.array([0.1, 0.2, 0.3, 0.05, 0.4, 0.15])
    iv = 1 / sd ** 2
    assert M.hrp_weights(np.diag(sd ** 2)) == pytest.approx(iv / iv.sum(), abs=1e-12)   # diagonal: Inverse Varianz
    w = M.hrp_weights(np.eye(8))
    assert w == pytest.approx(np.full(8, 1 / 8))
    rng = np.random.default_rng(9)
    for _ in range(20):
        a = rng.normal(0, 1, (9, 9))
        cov = a @ a.T / 9 + 0.05 * np.eye(9)
        w = M.hrp_weights(cov)
        assert w.sum() == pytest.approx(1.0) and (w > 0).all() and (w < 1).all()


def test_hrp_is_invariant_to_asset_order():
    rng = np.random.default_rng(13)
    a = rng.normal(0, 1, (9, 9))
    cov = a @ a.T / 9 + 0.05 * np.eye(9)
    perm = rng.permutation(9)
    w = M.hrp_weights(cov)
    wp = M.hrp_weights(cov[np.ix_(perm, perm)])
    assert wp == pytest.approx(w[perm], abs=1e-10)


# --------------------------------------------------------------------------------------
# Bekannte Antworten der Strategie
# --------------------------------------------------------------------------------------

def test_ivp_weights_inverse_to_volatility_exact():
    sig = np.array([0.004, 0.006, 0.010, 0.012, 0.002, 0.003, 0.0025, 0.008, 0.015])
    p = alt_panel(sig)
    w = M.weights(p)
    assert len(w) > 5
    exp = (1 / sig) / (1 / sig).sum()
    for _, row in w.iterrows():
        assert row.to_numpy() == pytest.approx(exp, abs=1e-9)


def test_ivp_matches_independent_pandas_reference_on_random_data():
    p = random_panel()
    w = M.weights(p)
    ref = ref_ivp(p).loc[w.index]
    assert len(w) > 20
    assert (w - ref).abs().to_numpy().max() < 1e-12


def test_ivp_window_252_matches_pandas_reference():
    p = random_panel()
    w = M.weights(p, **ALL_RUNS["window_252"])
    ref = ref_ivp(p, 252, 168).loc[w.index]
    assert (w - ref).abs().to_numpy().max() < 1e-12


def test_equal_vol_gives_equal_weights_for_every_scheme():
    p = alt_panel(np.full(N9, 0.01))
    for name, params in ALL_RUNS.items():
        if name == "hrp_252":
            continue                                               # HRP hängt von der Clusterung ab, siehe unten
        w = M.weights(p, **params)
        assert len(w) > 5
        assert w.to_numpy() == pytest.approx(np.full(w.shape, 1 / N9), abs=1e-6), name


def test_window_252_uses_only_last_252_rows():
    early = np.array([0.004, 0.006, 0.010, 0.012, 0.002, 0.003, 0.0025, 0.008, 0.015])
    late = np.array([0.012, 0.004, 0.003, 0.002, 0.010, 0.006, 0.005, 0.008, 0.004])
    p = alt_panel(early, change_at=600, sig_late=late)
    w252 = M.weights(p, **ALL_RUNS["window_252"])
    w756 = M.weights(p)
    exp_late = (1 / late) / (1 / late).sum()
    full_late = w252[w252.index >= p.close.index[600 + 252]]
    assert len(full_late) > 3
    for _, row in full_late.iterrows():
        assert row.to_numpy() == pytest.approx(exp_late, abs=1e-6)             # Fenster sieht nur noch die späte Phase
    assert not np.allclose(w756.iloc[-1].to_numpy(), exp_late, atol=1e-3)      # das 756er-Fenster mischt beide Phasen


def test_equal_scheme_is_one_over_nine_on_same_dates_as_base():
    p = random_panel()
    w_eq = M.weights(p, **ALL_RUNS["equal"])
    w_b = M.weights(p)
    assert list(w_eq.index) == list(w_b.index) and len(w_eq) > 20
    assert w_eq.to_numpy() == pytest.approx(np.full(w_eq.shape, 1 / N9), abs=1e-14)


def test_higher_vol_asset_gets_lower_weight_in_every_scheme():
    p = random_panel()
    for name, params in ALL_RUNS.items():
        if name == "equal":
            continue
        w = M.weights(p, **params)
        assert len(w) > 5
        # Vol steigt über die Spalten (linspace); gleichgewichtete Risikoaufteilung -> mittlere Gewichte fallen
        mean_w = w.mean()
        assert mean_w.iloc[0] > mean_w.iloc[-1], name


def test_erc_equals_ivp_when_assets_are_uncorrelated_with_known_vols():
    rng = np.random.default_rng(21)
    n = 1250
    sig = np.linspace(0.004, 0.014, N9)
    ret = rng.normal(0, 1, (n, N9)) * sig
    p = panel_from_ret(ret)
    w_i, w_e = M.weights(p), M.weights(p, **ALL_RUNS["erc_lw"])
    assert list(w_i.index) == list(w_e.index)
    assert (w_i - w_e).abs().to_numpy().max() < 0.03                          # fast gleich (Rest = Schätzrauschen der Korrelation)


# --------------------------------------------------------------------------------------
# Form, Wertebereich, Kalender
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", list(ALL_RUNS))
def test_shape_range_and_no_leverage(name):
    p = random_panel()
    w = M.weights(p, **ALL_RUNS[name])
    assert len(w) > 20
    assert list(w.columns) == T
    assert w.index.is_monotonic_increasing and w.index.is_unique
    assert set(w.index) <= set(p.close.index)
    assert not w.isna().any().any()
    assert (w > 0).all().all() and (w <= 1.0).all().all()                      # long-only, jedes Asset im Portfolio
    s = w.sum(axis=1)
    assert (s - 1.0).abs().max() < 1e-9                                        # voll investiert, kein Hebel, kein Cash


def test_rows_are_exactly_causal_month_ends_from_gate_on():
    p = random_panel()
    idx = p.close.index
    me = month_ends(idx)
    first_ok = [d for d in me if idx.get_loc(d) >= M.GATE_MIN_OBS][0]          # ab Zeile 504 hat jedes Asset 504 Renditen
    expected = [d for d in me if d >= first_ok]
    for name, params in ALL_RUNS.items():
        w = M.weights(p, **params)
        assert list(w.index) == expected, name                                 # alle Läufe starten am selben Tag (Gate)


def test_first_signal_is_the_first_month_end_after_504_returns():
    p = random_panel(n=800)
    idx = p.close.index
    w = M.weights(p)
    assert idx.get_loc(w.index[0]) >= 504                                      # Zeile 0 hat keine Rendite -> i Renditen an Zeile i
    earlier = [d for d in month_ends(idx) if d < w.index[0]]
    assert earlier and all(idx.get_loc(d) < 504 for d in earlier)              # kein früheres Monatsende erfüllt das Gate


def test_short_history_gives_empty_frame():
    p = random_panel(n=400)
    for name, params in ALL_RUNS.items():
        w = M.weights(p, **params)
        assert len(w) == 0 and list(w.columns) == T, name
    tiny = random_panel(n=2)
    assert len(M.weights(tiny)) == 0


def test_parameter_validation():
    p = random_panel(n=300)
    with pytest.raises(ValueError):
        M.weights(p, scheme="min_var")
    with pytest.raises(ValueError):
        M.weights(p, window=100, min_obs=200)
    with pytest.raises(ValueError):
        M.weights(p, window=1, min_obs=1)
    with pytest.raises(ValueError):
        M.weights(p, min_obs=1)


# --------------------------------------------------------------------------------------
# Fehlende Preise = nicht handelbar
# --------------------------------------------------------------------------------------

def test_late_listed_asset_blocks_all_signals_until_504_returns():
    p = random_panel(n=1500)
    q = with_nan(p, "DBC", p.close.index[:400])
    idx = q.close.index
    first_valid = idx.get_loc(q.close["DBC"].first_valid_index())              # = 400
    me = month_ends(idx)
    # DBC hat an Zeile i genau i - first_valid Renditen (die erste Zeile nach der Lücke hat noch keine)
    expected_first = [d for d in me if idx.get_loc(d) - first_valid >= 504][0]
    for name, params in ALL_RUNS.items():
        w = M.weights(q, **params)
        assert w.index.min() == expected_first, name
        assert w.index.min() > p.close.index[first_valid + 500 - 1]
        assert_no_weight_on_nan(w, q)
        assert not w.isna().any().any()


def test_missing_price_on_signal_day_skips_only_that_signal():
    p = random_panel()
    idx = p.close.index
    me = month_ends(idx)
    t_star = me[40]
    q = with_nan(p, "TLT", [t_star])
    for name, params in ALL_RUNS.items():
        w = M.weights(q, **params)
        assert t_star not in w.index, name                                     # TLT nicht handelbar -> kein Signal
        for d in (me[39], me[41], me[42]):                                     # 1-Tages-Lücke blockiert die Historie nicht
            assert d in w.index, name
        assert_no_weight_on_nan(w, q)
        assert not w.isna().any().any()


def test_missing_price_gives_nan_returns_never_filled():
    # Ein NaN-Kurs macht die Rendite am NaN-Tag UND am Folgetag ungültig; es wird nichts gefüllt oder überbrückt.
    p = random_panel()
    idx = p.close.index
    me = month_ends(idx)
    t_star = me[40]
    q = with_nan(p, "TLT", [idx[idx.get_loc(t_star) - 3]])                     # Lücke kurz vor dem Signaltag
    w = M.weights(q)
    assert t_star in w.index
    r = q.close[T].pct_change(fill_method=None)
    win = r.iloc[idx.get_loc(t_star) - 755: idx.get_loc(t_star) + 1]
    assert win["TLT"].isna().sum() == 2 and win.drop(columns="TLT").isna().sum().sum() == 0
    sig = win.std(ddof=1) * np.sqrt(252)                                       # pandas überspringt NaN
    ref = (1 / sig) / (1 / sig).sum()
    assert w.loc[t_star].to_numpy() == pytest.approx(ref.to_numpy(), abs=1e-12)


def test_delisted_asset_stops_signals_and_never_gets_weight():
    p = random_panel()
    cut = 1000
    q = with_nan(p, "EEM", p.close.index[cut:])
    for name, params in ALL_RUNS.items():
        w = M.weights(q, **params)
        assert len(w) > 0 and w.index.max() < q.close.index[cut], name
        assert_no_weight_on_nan(w, q)


def test_long_gap_in_history_gives_no_weight_on_nan_and_no_crash():
    p = random_panel(n=1500)
    rows = p.close.index[900:1000]                                             # 100 Tage Lücke in einem Asset
    q = with_nan(p, "VNQ", rows)
    for name, params in ALL_RUNS.items():
        w = M.weights(q, **params)
        assert len(w) > 0, name
        assert not w.isna().any().any()
        assert (w.sum(axis=1) - 1).abs().max() < 1e-9
        assert_no_weight_on_nan(w, q)


def test_hrp_252_needs_168_complete_rows_in_window():
    p = random_panel(n=1500)
    idx = p.close.index
    q = with_nan(p, "VNQ", idx[900:1000])                                      # 100 Tage Lücke, Renditen: 101 ungültig
    w_i = M.weights(q)                                                         # ivp 756/504: Lücke unkritisch
    w_h = M.weights(q, **ALL_RUNS["hrp_252"])
    assert set(w_h.index) <= set(w_i.index)
    r = q.close[T].pct_change(fill_method=None)
    complete = r.notna().all(axis=1)
    n_complete = {d: int(complete.iloc[idx.get_loc(d) - 251: idx.get_loc(d) + 1].sum()) for d in w_i.index}
    for d in w_i.index:
        if n_complete[d] >= 168:
            assert d in w_h.index
        else:
            assert d not in w_h.index
    assert any(c < 168 for c in n_complete.values()) and any(c >= 168 for c in n_complete.values())


def test_non_positive_price_is_treated_as_missing():
    p = random_panel()
    idx = p.close.index
    me = month_ends(idx)
    close, open_ = p.close.copy(), p.open.copy()
    close.loc[me[40], "GLD"] = 0.0
    q = Panel(open_, close)
    w = M.weights(q)
    assert me[40] not in w.index
    assert not w.isna().any().any()


# --------------------------------------------------------------------------------------
# Kausalität
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", list(ALL_RUNS))
def test_check_causality_passes(name):
    p = random_panel(n=1150)
    params = ALL_RUNS[name]
    assert check_causality(lambda pp, _pa=params: M.weights(pp, **_pa), p, n_cuts=7) == []


def test_check_causality_with_nan_history():
    p = random_panel(n=1500)
    q = with_nan(p, "DBC", p.close.index[:300])
    assert check_causality(lambda pp: M.weights(pp, **BASE), q, n_cuts=6) == []
    assert check_causality(lambda pp: M.weights(pp, **ALL_RUNS["hrp_252"]), q, n_cuts=4) == []


@pytest.mark.parametrize("name", ["base", "erc_lw", "hrp_252", "window_252"])
def test_future_prices_do_not_change_past_weights(name):
    p = random_panel()
    idx = p.close.index
    cut = idx[1000]
    close, open_ = p.close.copy(), p.open.copy()
    close.loc[close.index > cut] *= 7.0
    open_.loc[open_.index > cut] *= 7.0
    q = Panel(open_, close)
    a = M.weights(p, **ALL_RUNS[name]).loc[:cut]
    b = M.weights(q, **ALL_RUNS[name]).loc[:cut]
    assert list(a.index) == list(b.index) and len(a) > 0
    assert (a - b).abs().to_numpy().max() < 1e-12


def test_weights_use_data_through_signal_day_including_that_close():
    p = random_panel()
    idx = p.close.index
    w = M.weights(p)
    t = w.index[10]
    close, open_ = p.close.copy(), p.open.copy()
    close.loc[t, "VTI"] *= 1.15                                                # Schlusskurs von t selbst ändern
    q = Panel(open_, close)
    w2 = M.weights(q)
    assert (w.loc[t] - w2.loc[t]).abs().max() > 1e-4                           # Signal an t sieht den Schlusskurs von t
    before = w.index[w.index < t]
    assert (w.loc[before] - w2.loc[before]).abs().to_numpy().max() < 1e-14     # frühere Signale bleiben unberührt


def test_open_prices_do_not_influence_weights():
    p = random_panel()
    q = Panel(p.open * 3.0, p.close)
    for name in ("base", "hrp_252"):
        a, b = M.weights(p, **ALL_RUNS[name]), M.weights(q, **ALL_RUNS[name])
        assert (a - b).abs().to_numpy().max() < 1e-14


# --------------------------------------------------------------------------------------
# Zusammenspiel mit der Engine
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", ["base", "erc_lw", "hrp_252", "window_252", "equal"])
def test_engine_runs_fully_invested_without_skipped_orders(name):
    p = random_panel()
    w = M.weights(p, **ALL_RUNS[name])
    res = run_backtest(p, w, cost=ZERO, rf=pd.Series(0.0, index=p.close.index))
    assert res.skipped_orders == 0
    assert np.isfinite(res.nav).all() and (res.nav > 0).all()
    assert res.gross_exposure.max() <= 1.0 + 1e-6                              # nie gehebelt
    first_trade_day = p.close.index[p.close.index.get_loc(w.index[0]) + 1]     # Signal t, Handel zur Eröffnung t+1
    assert res.gross_exposure.loc[first_trade_day:].min() > 0.99
    assert res.gross_exposure.loc[:w.index[0]].max() == 0.0
    costed = run_backtest(p, w, cost=CostModel(), rf=pd.Series(0.0, index=p.close.index))
    assert costed.cost.sum() > 0 and costed.n_trades > 0


def test_equal_weight_control_trades_only_the_monthly_drift_back():
    # Engine-Konsistenz: die 1/N-Kontrolle handelt jeden Monat nur die Drift zurück (kleiner, aber positiver Umschlag)
    p = random_panel()
    w = M.weights(p, **ALL_RUNS["equal"])
    res = run_backtest(p, w, cost=ZERO, rf=pd.Series(0.0, index=p.close.index))
    to = res.turnover.loc[res.turnover > 1e-9]
    assert len(to) >= len(w) - 1
    assert to.iloc[1:].max() < 0.2
