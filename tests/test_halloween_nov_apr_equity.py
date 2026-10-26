"""Tests für strategies/halloween_nov_apr_equity.py — nur synthetische Daten, kein Netz, kein Datencache."""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import month_end_flags
from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import halloween_nov_apr_equity as strat

ASSET, DAX = strat.ASSET, strat.DAX
VARIANTS = {"base": {}, **strat.SPEC["variants"]}
START, END = "2001-01-02", "2014-06-13"        # endet mitten im Jahr, nicht an einem Oktober-/April-Monatsende


def _params(variant: str, **over) -> dict:
    return {**strat.SPEC["params"], **VARIANTS[variant], **over}


def _panel(seed=5, start=START, end=END, cols=(ASSET, DAX)) -> Panel:
    """Synthetischer Kalender (Mo-Fr) mit Zufallspfaden; Eröffnung weicht vom Vortagsschluss leicht ab."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range(start, end)
    close = pd.DataFrame({c: 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, len(idx)))) for c in cols}, index=idx)
    op = close.shift(1).fillna(close.iloc[0]) * (1 + rng.normal(0, 0.002, close.shape))
    return Panel(op, close)


def _oracle_month_ends(idx: pd.DatetimeIndex, month: int) -> pd.DatetimeIndex:
    """Letzter Datentag jedes vollständigen Kalendermonats `month` (Orakel nur im Test; Monat muss vor dem Datenende enden)."""
    s = pd.Series(idx, index=idx)
    out = [g.index[-1] for (_, m), g in s.groupby([idx.year, idx.month]) if m == month and g.index[-1] < idx[-1]]
    return pd.DatetimeIndex(out)


def _states_by_month(w: pd.DataFrame, asset: str, months: pd.PeriodIndex) -> dict:
    """Zustand (1 = investiert) am ERSTEN Tag jedes Monats gemäß dem letzten Signal davor (Signal gilt ab dem Folgetag)."""
    out = {}
    for p in months:
        prev = w[asset].loc[:p.start_time - pd.Timedelta(days=1)]
        out[p] = np.nan if prev.empty else float(prev.iloc[-1])
    return out


# --------------------------------------------------------------------------------------
# Vertrag / Form
# --------------------------------------------------------------------------------------

def test_spec_contract():
    spec = strat.SPEC
    assert spec["id"] == "halloween_nov_apr_equity"
    assert spec["family"] == "calendar" and spec["sources"] and spec["start"] == "1926-07-01"
    assert len(spec["variants"]) <= 3
    sig = inspect.signature(strat.weights)
    for name in list(spec["params"]) + [k for v in spec["variants"].values() for k in v]:
        assert name in sig.parameters, name
    assert spec["params"] == {"asset": ASSET, "start_month": 11, "n_months": 6, "cash_asset": None}
    assert spec["cost_bps"][ASSET] == 2.0
    assert hasattr(strat, "load")
    assert set(spec["tickers"]) == {ASSET, DAX}


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_shape_and_range(variant):
    panel = _panel()
    p = _params(variant)
    w = strat.weights(panel, **p)
    assert list(w.columns) == [p["asset"]]
    assert len(w) == 2 * 13 or len(w) == 2 * 13 - 1 or len(w) > 20       # ca. zwei Zeilen pro Jahr
    assert w.notna().all().all()
    assert set(np.unique(w.to_numpy())) <= {0.0, 1.0}
    assert (w.sum(axis=1) <= 1.0 + 1e-12).all() and (w >= 0).all().all()  # kein Hebel, kein Short
    flags = month_end_flags(panel.close.index)
    assert w.index.isin(flags.index[flags.to_numpy()]).all()               # nur an Monatsenden
    assert w.index.isin(panel.close.index).all()
    assert w.index.is_monotonic_increasing and not w.index.has_duplicates
    assert set(w.index.month) <= {4, 10}


# --------------------------------------------------------------------------------------
# Regel
# --------------------------------------------------------------------------------------

def test_entry_last_trading_day_of_october_exit_last_trading_day_of_april():
    panel = _panel()
    idx = panel.close.index
    w = strat.weights(panel)[ASSET]
    octs, aprs = _oracle_month_ends(idx, 10), _oracle_month_ends(idx, 4)
    assert list(w.index[w == 1.0]) == list(octs)                # Entry exakt am letzten Datentag im Oktober
    assert list(w.index[w == 0.0]) == list(aprs)                # Exit exakt am letzten Datentag im April
    assert len(octs) == 13 and len(aprs) == 14                  # Daten enden 2014-06: Oktober 2001..2013, April 2001..2014
    # Entry und Exit wechseln sich strikt ab
    vals = w.to_numpy()
    assert (np.abs(np.diff(vals)) == 1.0).all()
    assert vals[0] == 0.0                                       # erstes Ereignis ab Januar 2001 ist der April-Exit


def test_first_event_is_the_first_october_when_data_starts_in_summer():
    panel = _panel(start="2001-07-02")
    idx = panel.close.index
    w = strat.weights(panel)[ASSET]
    assert w.index[0] == _oracle_month_ends(idx, 10)[0]
    assert w.iloc[0] == 1.0


def test_last_trading_day_is_data_based_not_calendar_date():
    """Fällt der 31.10. auf ein Wochenende, ist der Freitag davor der letzte Handelstag (2004-10-31 war ein Sonntag)."""
    panel = _panel()
    w = strat.weights(panel)[ASSET]
    assert pd.Timestamp("2004-10-29") in w.index and w.loc["2004-10-29"] == 1.0
    assert pd.Timestamp("2004-10-28") not in w.index
    assert pd.Timestamp("2005-04-29") in w.index and w.loc["2005-04-29"] == 0.0     # 30.04.2005 war ein Samstag


def test_holiday_gap_in_data_moves_the_signal_day():
    """Fehlt der Monatsendetag in den Daten (Feiertag), wandert das Signal auf den letzten vorhandenen Tag."""
    panel = _panel()
    idx = panel.close.index
    drop = pd.Timestamp("2004-10-29")
    keep = idx[idx != drop]
    p2 = Panel(panel.open.loc[keep], panel.close.loc[keep])
    w = strat.weights(p2)[ASSET]
    assert drop not in w.index
    assert pd.Timestamp("2004-10-28") in w.index and w.loc["2004-10-28"] == 1.0


@pytest.mark.parametrize("start_month", range(1, 13))
def test_start_month_windows_cover_six_consecutive_months(start_month):
    """Mining-Check der Spezifikation: jeder der 12 Startmonate ergibt ein 6-Monats-Fenster ab seinem Monatsersten."""
    panel = _panel()
    w = strat.weights(panel, start_month=start_month)
    months = pd.period_range("2002-01", "2013-12", freq="M")
    st = _states_by_month(w, ASSET, months)
    window = {(start_month - 1 + k) % 12 + 1 for k in range(6)}
    for p, s in st.items():
        assert s == (1.0 if p.month in window else 0.0), (start_month, p)
    assert sum(1 for p in months if st[p] == 1.0) == 6 * 12        # 12 Jahre x 6 Monate investiert


def test_default_is_november_start():
    panel = _panel()
    assert strat.weights(panel).equals(strat.weights(panel, start_month=11, n_months=6))
    assert strat.window_months() == (10, 4)
    assert strat.window_months(1, 6) == (12, 6)
    assert strat.window_months(5, 6) == (4, 10)                     # Mai-Okt: Entry Ende April, Exit Ende Oktober
    assert strat.window_months(7, 3) == (6, 9)


def test_n_months_changes_exit_month():
    panel = _panel()
    w = strat.weights(panel, start_month=11, n_months=3)           # Nov-Jan: Entry Ende Oktober, Exit Ende Januar
    assert set(w.index.month) == {10, 1}
    st = _states_by_month(w, ASSET, pd.period_range("2003-01", "2012-12", freq="M"))
    assert all(s == (1.0 if p.month in (11, 12, 1) else 0.0) for p, s in st.items())


@pytest.mark.parametrize("kw", [dict(start_month=0), dict(start_month=13), dict(n_months=0), dict(n_months=12)])
def test_invalid_window_params(kw):
    with pytest.raises(ValueError):
        strat.weights(_panel(), **kw)
    with pytest.raises(ValueError):
        strat.weights(_panel(), asset=ASSET, cash_asset=ASSET)


def test_signal_ignores_prices_entirely():
    """Reine Kalenderregel: andere Kurse (auch andere Vorzeichen) ändern die Gewichte nicht."""
    a, b = _panel(seed=1), _panel(seed=99)
    assert strat.weights(a).equals(strat.weights(b))
    assert strat.weights(a, asset=DAX).equals(strat.weights(b, asset=DAX).rename(columns={DAX: DAX}))


def test_variant_dax_uses_dax_column_only():
    panel = _panel()
    w_dax = strat.weights(panel, **_params("dax"))
    w_mkt = strat.weights(panel)
    assert list(w_dax.columns) == [DAX] and list(w_mkt.columns) == [ASSET]
    assert np.allclose(w_dax[DAX].to_numpy(), w_mkt[ASSET].to_numpy())
    assert w_dax.index.equals(w_mkt.index)


# --------------------------------------------------------------------------------------
# Fehlende Kurse (NaN = nicht handelbar) und Cash-Titel
# --------------------------------------------------------------------------------------

def test_no_weights_on_nan_asset_prices():
    panel = _panel()
    close = panel.close.copy()
    cut = pd.Timestamp("2005-02-15")
    close.loc[:cut, DAX] = np.nan                                  # DAX noch nicht verfügbar
    p2 = Panel(close.copy(), close)
    w = strat.weights(p2, asset=DAX)
    assert len(w) > 0 and w.index.min() > cut
    assert w.notna().all().all()
    assert not p2.close.loc[w.index, DAX].isna().any()
    assert w.index[0] == pd.Timestamp("2005-04-29") and w.iloc[0, 0] == 0.0
    # Einzelner NaN-Kurs am Oktober-Monatsende: dort kein Gewicht (Entry fällt aus), April-Exit bleibt
    hole = pd.Timestamp("2008-10-31")
    close2 = panel.close.copy()
    close2.loc[hole, ASSET] = np.nan
    w2 = strat.weights(Panel(close2.copy(), close2))
    assert hole not in w2.index
    assert pd.Timestamp("2009-04-30") in w2.index
    assert not close2.loc[w2.index, ASSET].isna().any()
    # der Rest bleibt identisch
    assert w2.equals(strat.weights(panel).drop(hole))


def test_cash_asset_gets_the_remainder():
    panel = _panel(cols=(ASSET, DAX, "BND"))
    close = panel.close.copy()
    close.loc[:"2003-06-30", "BND"] = np.nan                       # Cash-Titel noch nicht gelistet
    p2 = Panel(close.copy(), close)
    w = strat.weights(p2, cash_asset="BND")
    assert list(w.columns) == [ASSET, "BND"]
    assert (w.sum(axis=1) == 1.0).all() and (w >= 0).all().all()   # voll investiert: Aktie oder Cash-Titel
    assert w.index.min() > pd.Timestamp("2003-06-30")              # nichts, bevor der Cash-Titel einen Kurs hat
    assert (w.loc[w[ASSET] == 1.0, "BND"] == 0.0).all() and (w.loc[w[ASSET] == 0.0, "BND"] == 1.0).all()
    assert not p2.close.loc[w.index, "BND"].isna().any()
    base = strat.weights(p2)
    assert list(w.index) == list(base.loc[w.index[0]:].index)       # gleiche Termine wie die Basis, nur später beginnend


# --------------------------------------------------------------------------------------
# Kausalität
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_causality_check(variant):
    panel = _panel()
    p = _params(variant)
    assert check_causality(lambda pn: strat.weights(pn, **p), panel) == []


def test_causality_exactly_at_and_around_the_signal_days():
    panel = _panel()
    idx = panel.close.index
    cuts = []
    for month in (10, 4):
        for d in _oracle_month_ends(idx, month)[2:9]:
            i = idx.get_loc(d)
            cuts += [idx[i - 1], d, idx[i + 1]]                    # Vortag, Signaltag, Folgetag
    assert check_causality(lambda pn: strat.weights(pn), panel, cuts=cuts) == []
    assert check_causality(lambda pn: strat.weights(pn, asset=DAX, start_month=5), panel, cuts=cuts) == []


def test_future_prices_do_not_change_past_weights():
    panel = _panel()
    base = strat.weights(panel)
    cut = panel.close.index[int(len(panel.close) * 0.6)]
    close = panel.close.copy()
    close.loc[close.index > cut] *= 0.01                           # drastisch andere Zukunft
    other = strat.weights(Panel(close.copy(), close))
    assert base.loc[:cut].equals(other.loc[:cut])


def test_last_data_day_mid_month_is_not_a_signal_but_calendar_month_end_is():
    panel = _panel()
    idx = panel.close.index
    mid = idx[idx >= pd.Timestamp("2006-10-20")][0]
    w = strat.weights(panel.truncate(mid))[ASSET]
    assert not (w.index.year == 2006).any() or w.index[w.index.year == 2006].max() < pd.Timestamp("2006-10-01")
    # Letzter Datentag ist der letzte Handelstag im Oktober: der Kalender sagt "nächster Handelstag im November"
    eo = _oracle_month_ends(idx, 10)
    d = eo[eo.year == 2006][0]
    w2 = strat.weights(panel.truncate(d))[ASSET]
    assert w2.index.max() == d and w2.iloc[-1] == 1.0
    # einen Tag früher: noch kein Signal (der Kalender kennt einen späteren Handelstag im Oktober)
    w3 = strat.weights(panel.truncate(idx[idx.get_loc(d) - 1]))[ASSET]
    assert w3.index.max() < d


# --------------------------------------------------------------------------------------
# Engine-Integration (Ausführungstiming, Exposure)
# --------------------------------------------------------------------------------------

def _engine_run(panel, w, **kw):
    rf = pd.Series(0.0, index=panel.close.index)
    return run_backtest(panel, w, cost=CostModel(default_bps=2.0), rf=rf, **kw)


def test_engine_integration_timing_and_exposure():
    panel = _panel(cols=(ASSET,))
    idx = panel.close.index
    w = strat.weights(panel)
    res = _engine_run(panel, w)
    assert (res.gross_exposure <= 1.0 + 1e-3).all()
    assert (res.weights[ASSET] >= -1e-9).all()
    # Signal am Tag t (Entry) -> Position erst ab t+1 (Handel zur Eröffnung), nicht schon am Signaltag
    entries = w.index[w[ASSET] == 1.0]
    s = entries[0]
    assert res.weights.loc[s, ASSET] == 0.0
    nxt = idx[idx.get_loc(s) + 1]
    assert res.weights.loc[nxt, ASSET] > 0.95
    exits = w.index[w[ASSET] == 0.0]
    e = exits[exits > s][0]
    assert res.weights.loc[e, ASSET] > 0.9                              # am Signaltag noch investiert
    assert res.weights.loc[idx[idx.get_loc(e) + 1], ASSET] < 1e-9       # ab t+1 Cash
    # gehandelt wird nur am Tag nach einem Signal; zwei Wechsel pro Jahr
    pos = idx.get_indexer(w.index) + 1
    exec_days = idx[pos[pos < len(idx)]]
    assert (res.turnover.drop(exec_days) <= 1e-12).all()
    assert (res.turnover.loc[idx[idx.get_indexer(entries) + 1]] > 0.45).all()   # einseitiger Umsatz ~ 0,5 bei 100 % Umschichtung
    n_years = 13
    assert res.n_trades in (2 * n_years - 1, 2 * n_years)               # Entry+Exit je Jahr; der erste Exit trifft auf Cash


def test_engine_exposure_is_about_half_the_time_and_cash_in_summer():
    panel = _panel(cols=(ASSET,))
    idx = panel.close.index
    res = _engine_run(panel, strat.weights(panel))
    wd = res.weights[ASSET]
    inner = wd.loc["2002-01-01":"2013-12-31"]
    winter = inner[inner.index.month.isin([12, 1, 2, 3])]               # weit weg von den Wechseltagen
    summer = inner[inner.index.month.isin([6, 7, 8, 9])]
    assert (winter > 0.95).all()
    assert (summer.abs() < 1e-9).all()
    assert 0.45 < (inner > 0.5).mean() < 0.55


def test_engine_exec_close_trades_on_the_signal_day():
    """--exec close = MOC der Spezifikation: Handel zum Schluss des Signaltags."""
    panel = _panel(cols=(ASSET,))
    w = strat.weights(panel)
    res = _engine_run(panel, w, exec_mode="close")
    s = w.index[w[ASSET] == 1.0][0]
    assert res.weights.loc[s, ASSET] > 0.95


def test_always_invested_nav_matches_prices_without_costs():
    """Kontrolle: bei Gewicht 1 vom ersten Tag an folgt das NAV exakt dem Kurs (keine verlorene Tagesrendite)."""
    panel = _panel(cols=(ASSET,))
    close = panel.close[ASSET]
    p2 = Panel(panel.close.copy(), panel.close.copy())                   # open == close wie bei French
    first = close.index[0]
    res = run_backtest(p2, pd.DataFrame({ASSET: [1.0]}, index=[first]), cost=CostModel(default_bps=0.0),
                       rf=pd.Series(0.0, index=close.index))
    assert res.nav.iloc[-1] == pytest.approx(close.iloc[-1] / close.iloc[1], rel=1e-9)   # Handel zum Schluss von t+1


# --------------------------------------------------------------------------------------
# Panel-Aufbau (ohne Netz)
# --------------------------------------------------------------------------------------

def _french_like(n=40, start="2001-03-01"):
    idx = pd.bdate_range(start, periods=n)
    return pd.Series(np.full(n, 0.001), index=idx)


def test_build_panel_without_dax_is_plain_french_panel():
    p = strat.build_panel(_french_like())
    assert p.tickers == [ASSET]
    assert p.open.equals(p.close)                                       # open == close (Handel zum Folgetag-Schluss)
    assert p.close[ASSET].is_monotonic_increasing


def test_build_panel_aligns_dax_with_limited_forward_fill():
    ret = _french_like(n=60)
    idx = ret.index
    dax_idx = idx[10:]                                                   # DAX beginnt erst später
    dax = pd.Series(np.linspace(1000, 1100, len(dax_idx)), index=dax_idx)
    hole = idx[20:22]                                                    # DAX-Feiertag: 2 US-Handelstage ohne DAX
    dax = dax.drop(hole)
    extra = pd.DatetimeIndex(["2001-04-14"])                             # DAX-Handelstag am Samstag: kein US-Tag
    dax = pd.concat([dax, pd.Series([1050.0], index=extra)]).sort_index()
    p = strat.build_panel(ret, dax)
    assert p.tickers == [ASSET, DAX]
    assert p.close.index.equals(idx) and p.open.equals(p.close)
    assert p.close[DAX].iloc[:10].isna().all()                           # vor dem ersten DAX-Kurs: nicht handelbar
    assert p.close[DAX].iloc[10:].notna().all()
    assert p.close[DAX].iloc[20] == p.close[DAX].iloc[19] and p.close[DAX].iloc[21] == p.close[DAX].iloc[19]
    assert pd.Timestamp("2001-04-14") not in p.close.index
    # Füllgrenze: mehr als 5 fehlende Tage am Stück bleiben NaN
    dax_long_gap = dax.drop(idx[30:38])
    p2 = strat.build_panel(ret, dax_long_gap)
    assert p2.close[DAX].iloc[30:35].notna().all() and p2.close[DAX].iloc[35:38].isna().all()
    assert p2.close[DAX].iloc[38:].notna().all()


def test_dax_holiday_does_not_lose_returns_in_the_engine():
    """Ohne Vorwärtsfüllung ginge die Rendite über DAX-Feiertage verloren (Engine rechnet open[i]/close[i-1])."""
    ret = _french_like(n=60)
    idx = ret.index
    dax = pd.Series(1000 * np.cumprod(1 + np.full(len(idx), 0.002)), index=idx)
    dax_h = dax.drop(idx[20:22])
    p = strat.build_panel(ret, dax_h)
    first = idx[3]
    res = run_backtest(p, pd.DataFrame({DAX: [1.0]}, index=[first]), cost=CostModel(default_bps=0.0),
                       rf=pd.Series(0.0, index=idx))
    # Handel zum Schluss von first+1, dann bis zum letzten Tag: NAV = Kursverhältnis (inkl. der Tage nach den Lücken)
    assert res.nav.iloc[-1] == pytest.approx(dax.iloc[-1] / dax.iloc[4], rel=1e-9)
    # Gegenprobe: ohne Füllung wäre die Rendite des ersten Tages nach der Lücke verloren
    raw_close = p.close.copy()
    raw_close[DAX] = dax_h.reindex(idx)
    p_raw = Panel(raw_close.copy(), raw_close)
    res_raw = run_backtest(p_raw, pd.DataFrame({DAX: [1.0]}, index=[first]), cost=CostModel(default_bps=0.0),
                           rf=pd.Series(0.0, index=idx))
    assert res_raw.nav.iloc[-1] < res.nav.iloc[-1] * (1 - 0.0015)


def test_weights_never_use_dax_in_base_and_mkt_in_dax_variant():
    p = strat.build_panel(_french_like(n=40), pd.Series(np.linspace(100, 120, 40), index=_french_like(n=40).index))
    assert list(strat.weights(p).columns) == [ASSET]
    assert list(strat.weights(p, asset=DAX).columns) == [DAX]
