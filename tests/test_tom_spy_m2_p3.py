"""Tests für strategies/tom_spy_m2_p3.py — nur synthetische Daten, kein Netz, kein Datencache.

Alle Panels entstehen aus Zufallsrenditen über echten Handelskalendern: NYSE-Kalender mit Feiertagen (Index aus
qlab.calendar.NYSE_BDAY), Mo-Sa-Kalender der alten French-Daten (Samstage waren Handelstage) und der Übergang 1952.
"Orakel" (Positionen aus groupby über den kompletten Index) gibt es nur hier im Test, nie im Modul.
"""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest
from pandas.tseries.offsets import CustomBusinessDay

from qlab.calendar import NYSE_BDAY
from qlab.data import Panel
from qlab.engine import CostModel, check_causality, run_backtest
from strategies import tom_spy_m2_p3 as strat

ASSET = strat.ASSET
VARIANTS = {"base": {}, **strat.SPEC["variants"]}
START, END = "2001-01-02", "2007-12-14"          # endet mitten im Monat: das letzte Fenster ist vollständig geschlossen
SAT_BDAY = CustomBusinessDay(weekmask="Mon Tue Wed Thu Fri Sat")

# Lage der Zeilen relativ zur Position p des letzten Handelstags d(-1) eines Monats (d(+k) = p + k):
SIGNALS = {"base": (-2, 2), "tag_plus1": (-1, 0), "konservativ": (-1, 3)}       # (Einstiegssignal, Ausstiegssignal)
EARNING = {"base": (0, 1, 2, 3), "tag_plus1": (1,), "konservativ": (1, 2, 3, 4)}  # Tage, deren Rendite verdient wird


def _params(variant: str, **over) -> dict:
    return {**strat.SPEC["params"], **VARIANTS[variant], **over}


def _returns(idx: pd.DatetimeIndex, seed: int = 3) -> pd.Series:
    rng = np.random.default_rng(seed)
    return pd.Series(rng.normal(0.0004, 0.01, len(idx)), index=idx)


def _panel(start=START, end=END, seed=3, freq=NYSE_BDAY) -> tuple[Panel, pd.Series]:
    idx = pd.date_range(start, end, freq=freq)
    r = _returns(idx, seed)
    return strat.build_panel(r), r


def _mixed_index() -> pd.DatetimeIndex:
    """Mo-Sa bis zum letzten Datensamstag (1952-05-24), danach Mo-Fr."""
    a = pd.date_range("1951-09-03", "1952-05-24", freq=SAT_BDAY)
    b = pd.date_range("1952-05-26", "1953-03-13", freq=NYSE_BDAY)
    return a.append(b)


# ---- Orakel (nur im Test) -------------------------------------------------------------

def _complete_month_ends(idx: pd.DatetimeIndex) -> list[int]:
    """Positionen p der letzten Datentage aller Monate, deren Fenster (d(-3) ... d(+4)) komplett in den Daten liegt."""
    s = pd.Series(np.arange(len(idx)), index=idx)
    last = [int(p) for p in s.groupby([idx.year, idx.month]).max()]
    return [p for p in last if p - 3 >= 0 and p + 5 < len(idx)]


def _expected_signals(idx: pd.DatetimeIndex, variant: str) -> tuple[list, list]:
    e, x = SIGNALS[variant]
    ps = _complete_month_ends(idx)
    return [idx[p + e] for p in ps], [idx[p + x] for p in ps]


def _earning_mask(idx: pd.DatetimeIndex, variant: str) -> np.ndarray:
    mask = np.zeros(len(idx), bool)
    for p in _complete_month_ends(idx):
        for o in EARNING[variant]:
            mask[p + o] = True
    return mask


def _engine(panel, w, bps: float = 0.0, **kw):
    rf = pd.Series(0.0, index=panel.close.index)
    return run_backtest(panel, w, cost=CostModel(default_bps=bps), rf=rf, **kw)


# --------------------------------------------------------------------------------------
# Vertrag / Form
# --------------------------------------------------------------------------------------

def test_spec_contract():
    spec = strat.SPEC
    assert spec["id"] == "tom_spy_m2_p3"
    assert spec["family"] == "calendar" and spec["sources"] and spec["start"] == "1926-07-01"
    assert 1 <= len(spec["variants"]) <= 3
    sig = inspect.signature(strat.weights)
    for name in list(spec["params"]) + [k for v in spec["variants"].values() for k in v]:
        assert name in sig.parameters, name
    assert spec["params"] == {"asset": ASSET, "entry_day": -2, "exit_day": 3}
    assert set(spec["variants"]) == {"tag_plus1", "konservativ"}
    assert spec["cost_bps"] == {ASSET: 2.0}
    assert spec["tickers"] == [ASSET] and hasattr(strat, "load")


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_shape_and_range(variant):
    panel, _ = _panel()
    p = _params(variant)
    w = strat.weights(panel, **p)
    assert list(w.columns) == [ASSET]
    assert len(w) > 100                                                    # zwei Zeilen pro Monat, 6,5 Jahre
    assert w.notna().all().all()
    assert set(np.unique(w.to_numpy())) <= {0.0, 1.0}
    assert (w.sum(axis=1) <= 1.0 + 1e-12).all() and (w >= 0).all().all()   # kein Hebel, kein Short
    assert w.index.isin(panel.close.index).all()
    assert w.index.is_monotonic_increasing and not w.index.has_duplicates
    vals = w[ASSET].to_numpy()
    assert vals[0] == 1.0 and (np.abs(np.diff(vals)) == 1.0).all()          # Einstieg und Ausstieg wechseln sich ab
    assert isinstance(w.index, pd.DatetimeIndex)


def test_build_panel_is_a_plain_return_panel():
    ret = pd.Series([0.01, -0.02, 0.005, 0.0], index=pd.date_range("2005-03-28", periods=4, freq=NYSE_BDAY))
    p = strat.build_panel(ret)
    assert p.tickers == [ASSET]
    assert p.open.equals(p.close)                                          # open == close: Handel zum Folgetag-Schluss
    assert p.close[ASSET].iloc[0] == pytest.approx(101.0)
    assert p.close[ASSET].iloc[2] == pytest.approx(100 * 1.01 * 0.98 * 1.005)


# --------------------------------------------------------------------------------------
# Regel: welche Tage gehalten werden
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_signal_rows_match_the_calendar_oracle(variant):
    panel, _ = _panel()
    idx = panel.close.index
    w = strat.weights(panel, **_params(variant))[ASSET]
    entries, exits = _expected_signals(idx, variant)
    assert len(entries) == 6 * 12 + 11                                      # Jan 2001 .. Nov 2007; im Dezember 2007 enden die Daten
    assert list(w.index[w == 1.0]) == entries
    assert list(w.index[w == 0.0]) == exits


def test_signal_rows_match_the_oracle_for_the_first_month_of_the_data():
    panel, _ = _panel()
    idx = panel.close.index
    w = strat.weights(panel)[ASSET]
    assert w.index[0] == idx[_complete_month_ends(idx)[0] - 2]              # d(-3) des ersten Monats (Januar 2001)
    assert w.index[0] < pd.Timestamp("2001-02-01")


# Konkrete Kalenderfälle (von Hand aus dem NYSE-Kalender): (d(-1), Einstiegssignal d(-3), Ausstiegssignal d(+2))
CASES = [
    ("2005-04-29", "2005-04-27", "2005-05-03"),     # Sa 30.04.: Freitag ist der letzte Handelstag
    ("2005-03-31", "2005-03-29", "2005-04-04"),     # Karfreitag 25.03. liegt davor, 01.04. ist d(+1), Wochenende dazwischen
    ("2005-11-30", "2005-11-28", "2005-12-02"),     # Thanksgiving 24.11. liegt davor
    ("2005-12-30", "2005-12-28", "2006-01-04"),     # 02.01.2006 Feiertag: d(+1) = 03.01.
    ("2006-12-29", "2006-12-27", "2007-01-04"),     # 01.01. Feiertag, 02.01.2007 Trauertag: d(+1) = 03.01.
    ("2001-08-31", "2001-08-29", "2001-09-05"),     # Labor Day 03.09.: d(+1) = 04.09.
    ("2001-09-28", "2001-09-26", "2001-10-02"),     # Monatsende nach den Schließungen vom 11.-14.09.
    ("2007-11-30", "2007-11-28", "2007-12-04"),
]


@pytest.mark.parametrize("last,entry,exit_", CASES)
def test_concrete_windows_around_holidays(last, entry, exit_):
    panel, _ = _panel()
    idx = panel.close.index
    assert pd.Timestamp(last) in idx and pd.Timestamp(entry) in idx          # der Testkalender kennt diese Tage
    w = strat.weights(panel)[ASSET]
    assert w.loc[entry] == 1.0 and w.loc[exit_] == 0.0
    assert list(w.loc[entry:exit_].index) == [pd.Timestamp(entry), pd.Timestamp(exit_)]   # sonst nichts dazwischen
    p = idx.get_loc(pd.Timestamp(last))
    assert idx[p - 2] == pd.Timestamp(entry) and idx[p + 2] == pd.Timestamp(exit_)


def test_last_trading_day_is_data_based_after_a_dropped_day():
    """Fehlt der letzte Handelstag eines Monats in den Daten, wandert d(-1) auf den davor liegenden Tag."""
    panel, r = _panel()
    drop = pd.Timestamp("2004-10-29")                                       # Freitag, letzter Handelstag im Oktober 2004
    keep = panel.close.index[panel.close.index != drop]
    p2 = strat.build_panel(r.loc[keep])
    w = strat.weights(p2)[ASSET]
    entries, exits = _expected_signals(p2.close.index, "base")
    assert list(w.index[w == 1.0]) == entries and list(w.index[w == 0.0]) == exits
    assert pd.Timestamp("2004-10-26") in w.index and w.loc["2004-10-26"] == 1.0   # d(-1) = Do 28.10., d(-3) = Di 26.10.
    assert pd.Timestamp("2004-10-27") not in w.index                              # (mit Freitag 29.10. wäre es der 27.10.)


def test_default_is_minus2_to_plus3_and_equals_explicit_call():
    panel, _ = _panel()
    assert strat.weights(panel).equals(strat.weights(panel, entry_day=-2, exit_day=3))
    assert strat.weights(panel).equals(strat.weights(panel, **strat.SPEC["params"]))


def test_rel_converts_specification_days():
    assert [strat._rel(d) for d in (-3, -2, -1, 1, 2, 3, 4)] == [-2, -1, 0, 1, 2, 3, 4]
    for bad in (0, 1.5, -0.5):
        with pytest.raises(ValueError):
            strat._rel(bad)


@pytest.mark.parametrize("kw", [dict(entry_day=0), dict(exit_day=0), dict(entry_day=3, exit_day=3), dict(entry_day=2, exit_day=-1),
                                dict(entry_day=-2, exit_day=1.5), dict(entry_day=-2, exit_day=20), dict(entry_day=-12, exit_day=1)])
def test_invalid_window_params(kw):
    panel, _ = _panel()
    with pytest.raises(ValueError):
        strat.weights(panel, **kw)


def test_signal_ignores_prices_entirely():
    """Reine Kalenderregel: andere Kurse (andere Zufallspfade) ändern die Gewichte nicht."""
    a, _ = _panel(seed=1)
    b, _ = _panel(seed=99)
    assert strat.weights(a).equals(strat.weights(b))


def test_asset_parameter_selects_the_column():
    panel, r = _panel()
    two = Panel(pd.concat([panel.open, panel.open.rename(columns={ASSET: "B"})], axis=1),
                pd.concat([panel.close, panel.close.rename(columns={ASSET: "B"})], axis=1))
    wb = strat.weights(two, asset="B")
    assert list(wb.columns) == ["B"]
    assert np.allclose(wb["B"].to_numpy(), strat.weights(panel)[ASSET].to_numpy()) and wb.index.equals(strat.weights(panel).index)


def test_short_or_empty_panels_give_empty_weights():
    r = pd.Series(0.001, index=pd.date_range("2005-03-01", periods=5, freq=NYSE_BDAY))
    w = strat.weights(strat.build_panel(r))
    assert w.empty and list(w.columns) == [ASSET]
    w0 = strat.weights(strat.build_panel(r.iloc[:0]))
    assert w0.empty and list(w0.columns) == [ASSET]


# --------------------------------------------------------------------------------------
# Fehlende Kurse (NaN = nicht handelbar)
# --------------------------------------------------------------------------------------

def _panel_with_nans(until=None, holes=()):
    panel, r = _panel()
    close = panel.close.copy()
    if until is not None:
        close.loc[:until, ASSET] = np.nan                                   # noch nicht gelistet
    for h in holes:
        close.loc[h, ASSET] = np.nan
    return Panel(close.copy(), close), panel


def test_no_weights_on_nan_prices_before_listing():
    until = pd.Timestamp("2003-06-30")
    p2, panel = _panel_with_nans(until=until)
    w = strat.weights(p2)
    assert len(w) > 0 and w.index.min() > until
    assert w.notna().all().all()
    assert not p2.close.loc[w.index, ASSET].isna().any()
    # Juni-Fenster (Einstieg 26.06. liegt vor dem Listing) fällt komplett aus, auch sein Ausstieg am 02.07.
    assert w.index[0] == pd.Timestamp("2003-07-29") and w.iloc[0, 0] == 1.0
    assert w.equals(strat.weights(panel).loc[w.index[0]:])


def test_nan_price_on_entry_signal_day_skips_exactly_that_window():
    panel, _ = _panel()
    base = strat.weights(panel)
    entry = base.index[40]
    exit_ = base.index[41]
    assert base.loc[entry, ASSET] == 1.0 and base.loc[exit_, ASSET] == 0.0
    p2, _ = _panel_with_nans(holes=[entry])
    w = strat.weights(p2)
    assert entry not in w.index and exit_ not in w.index
    assert w.equals(base.drop([entry, exit_]))
    assert not p2.close.loc[w.index, ASSET].isna().any()


def test_nan_price_on_exit_signal_day_moves_the_exit_to_the_next_valid_day():
    panel, _ = _panel()
    idx = panel.close.index
    base = strat.weights(panel)
    exit_ = base.index[41]
    nxt = idx[idx.get_loc(exit_) + 1]
    p2, _ = _panel_with_nans(holes=[exit_])
    w = strat.weights(p2)
    assert exit_ not in w.index and w.loc[nxt, ASSET] == 0.0
    moved = pd.concat([base.drop(exit_), pd.DataFrame({ASSET: [0.0]}, index=pd.DatetimeIndex([nxt]))]).sort_index()
    assert w.equals(moved)
    assert not p2.close.loc[w.index, ASSET].isna().any()
    res = _engine(p2, w)                                                     # keine Position bleibt hängen
    assert res.weights[ASSET].iloc[-1] == pytest.approx(0.0, abs=1e-9) and res.skipped_orders == 0


def test_nan_price_on_an_unrelated_day_changes_nothing():
    panel, _ = _panel()
    base = strat.weights(panel)
    quiet = base.index[40] + pd.Timedelta(days=9)                            # mitten im Monat, weit weg von Signalen
    quiet = panel.close.index[panel.close.index >= quiet][0]
    assert quiet not in base.index
    p2, _ = _panel_with_nans(holes=[quiet])
    assert strat.weights(p2).equals(base)


# --------------------------------------------------------------------------------------
# Kausalität
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_causality_check(variant):
    panel, _ = _panel()
    p = _params(variant)
    assert check_causality(lambda pn: strat.weights(pn, **p), panel) == []


@pytest.mark.parametrize("variant", list(VARIANTS))
def test_causality_on_every_single_day_of_a_long_stretch(variant):
    """Schnitt an JEDEM Tag (auch genau am Signaltag, am Tag davor und danach, vor Feiertagen)."""
    panel, _ = _panel("2004-12-01", "2006-07-31")                           # kurzes Panel: jeder Schnitt kostet zwei Läufe
    idx = panel.close.index
    cuts = list(idx[(idx >= "2005-10-15") & (idx <= "2006-03-15")])         # Thanksgiving, Weihnachten, Neujahr, MLK, Presidents Day
    assert len(cuts) > 90
    p = _params(variant)
    assert check_causality(lambda pn: strat.weights(pn, **p), panel, cuts=cuts) == []


def test_causality_in_the_saturday_era():
    """Alte French-Daten: Samstage sind Handelstage; die Kalenderverlängerung nutzt dort Mo-Sa."""
    panel, _ = _panel("1932-06-01", "1934-06-15", freq=SAT_BDAY)
    idx = panel.close.index
    assert (idx.dayofweek == 5).any()
    w = strat.weights(panel)[ASSET]
    entries, exits = _expected_signals(idx, "base")
    assert list(w.index[w == 1.0]) == entries and list(w.index[w == 0.0]) == exits
    cuts = list(idx[(idx >= "1933-11-15") & (idx <= "1934-02-28")])
    assert check_causality(lambda pn: strat.weights(pn), panel, cuts=cuts) == []


def test_causality_across_the_end_of_saturday_trading_1952():
    idx = _mixed_index()
    panel = strat.build_panel(_returns(idx))
    assert (idx[idx > "1952-05-24"].dayofweek < 5).all() and (idx[idx <= "1952-05-24"].dayofweek == 5).any()
    w = strat.weights(panel)[ASSET]
    entries, exits = _expected_signals(idx, "base")
    assert list(w.index[w == 1.0]) == entries and list(w.index[w == 0.0]) == exits
    cuts = list(idx[(idx >= "1952-04-01") & (idx <= "1952-07-15")])
    assert check_causality(lambda pn: strat.weights(pn), panel, cuts=cuts) == []


def test_future_prices_do_not_change_past_weights():
    panel, _ = _panel()
    base = strat.weights(panel)
    cut = panel.close.index[int(len(panel.close) * 0.6)]
    close = panel.close.copy()
    close.loc[close.index > cut] *= 0.01                                    # drastisch andere Zukunft
    other = strat.weights(Panel(close.copy(), close))
    assert base.loc[:cut].equals(other.loc[:cut])


def test_data_ending_exactly_at_a_month_end_leaves_the_window_open():
    """Letzter Datentag ist der letzte Handelstag des Monats (Kalender: nächster Handelstag im Folgemonat)."""
    panel, _ = _panel(end="2007-11-30")
    w = strat.weights(panel)[ASSET]
    assert w.index[-1] == pd.Timestamp("2007-11-28") and w.iloc[-1] == 1.0   # Einstieg, Ausstieg liegt in der Zukunft
    res = _engine(panel, strat.weights(panel))
    assert res.weights[ASSET].iloc[-1] > 0.95                                # Position bleibt offen, nichts wird erfunden
    # Der Kalender ist im Voraus bekannt: schon am vorletzten Handelstag steht das Einstiegssignal (Vorlauf 2 Tage) ...
    w2 = strat.weights(panel.truncate("2007-11-29"))[ASSET]
    assert w2.index[-1] == pd.Timestamp("2007-11-28") and w2.iloc[-1] == 1.0
    # ... aber nicht früher: am 27.11. liegt der letzte Handelstag des Monats noch 3 Tage in der Zukunft
    w3 = strat.weights(panel.truncate("2007-11-27"))[ASSET]
    assert w3.index[-1] == pd.Timestamp("2007-11-02") and w3.iloc[-1] == 0.0      # Ausstieg des Oktober-Fensters


# --------------------------------------------------------------------------------------
# Engine-Integration (Ausführungstiming, Exposure, Kosten)
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("variant", list(VARIANTS))
def test_engine_earns_exactly_the_window_days(variant):
    """Ohne Kosten und Zins entspricht die Engine-Rendite genau der Marktrendite an den Fenstertagen, sonst null."""
    panel, r = _panel()
    idx = panel.close.index
    w = strat.weights(panel, **_params(variant))
    res = _engine(panel, w)
    expected = r.where(_earning_mask(idx, variant), 0.0)
    np.testing.assert_allclose(res.ret.to_numpy(), expected.to_numpy(), atol=1e-10)
    assert res.skipped_orders == 0


def test_engine_base_timing_and_exposure():
    panel, _ = _panel()
    idx = panel.close.index
    w = strat.weights(panel)
    res = _engine(panel, w)
    ps = _complete_month_ends(idx)
    p = ps[10]
    wd = res.weights[ASSET]
    assert wd.loc[idx[p - 2]] == 0.0                                        # Signaltag d(-3): noch nicht investiert
    assert wd.loc[idx[p - 1]] > 0.95                                        # Kauf zum Schluss von d(-2)
    for o in (0, 1, 2):
        assert wd.loc[idx[p + o]] > 0.95
    assert wd.loc[idx[p + 3]] == pytest.approx(0.0, abs=1e-9)               # Verkauf zum Schluss von d(+3)
    assert wd.loc[idx[p + 2]] > 0.95                                        # am Ausstiegssignal-Tag noch investiert
    assert (res.gross_exposure <= 1.0 + 1e-3).all() and (wd >= -1e-9).all()
    # gehandelt wird nur an den Ausführungstagen d(-2) und d(+3)
    exec_days = set(idx[[q + o for q in ps for o in (-1, 3)]])
    traded = set(res.turnover.index[res.turnover > 1e-12])
    assert traded == exec_days
    assert res.n_trades == 2 * len(ps)
    inner = wd.loc["2002-01-01":"2007-06-30"]
    assert 0.16 < (inner > 0.5).mean() < 0.22                               # ca. 4 von 21 Handelstagen


def test_engine_costs_two_bp_per_side():
    panel, _ = _panel()
    w = strat.weights(panel)
    res = _engine(panel, w, bps=2.0)
    n_trades = 2 * len(_complete_month_ends(panel.close.index))
    assert res.n_trades == n_trades
    assert float(res.cost.sum()) == pytest.approx(n_trades * 2e-4, rel=0.02)


def test_engine_exec_close_is_one_day_early():
    """Dokumentierte Eigenschaft: --exec close handelt am Signaltag selbst (eine Ausführung früher als vorgesehen)."""
    panel, _ = _panel()
    idx = panel.close.index
    w = strat.weights(panel)
    res = _engine(panel, w, exec_mode="close")
    p = _complete_month_ends(idx)[10]
    assert res.weights[ASSET].loc[idx[p - 2]] > 0.95


def test_always_invested_nav_follows_prices_without_costs():
    """Kontrolle des Panel-Aufbaus: bei Gewicht 1 vom ersten Tag an folgt das NAV dem Kurs ab t+1."""
    panel, _ = _panel()
    close = panel.close[ASSET]
    res = run_backtest(panel, pd.DataFrame({ASSET: [1.0]}, index=[close.index[0]]), cost=CostModel(default_bps=0.0),
                       rf=pd.Series(0.0, index=close.index))
    assert res.nav.iloc[-1] == pytest.approx(close.iloc[-1] / close.iloc[1], rel=1e-9)
