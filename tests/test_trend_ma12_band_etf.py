"""Tests für strategies/trend_ma12_band_etf.py (H8) — nur synthetische Daten, kein Netz, kein Datencache.

Monatsreihe für die Handrechnungen (Index = Monat, Wert = Monatsende-Schluss):
    m0..m10 = 100 | m11 = 90 | m12 = 99 | m13..m22 = 100 | m23 = 101 (bzw. 100,99 im Grenzfall)
MA12 an Monat k = Mittel(m_{k-11} .. m_k).  Band 1 %: Einstieg ab MA12 * 1.01, Ausstieg unter MA12 * 0.99.
"""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import month_end_flags
from qlab.data import Panel
from qlab.engine import check_causality, run_backtest
from strategies import trend_ma12_band_etf as strat
from strategies import trend_ma12_us_equity_cash_etf as base

ASSET, SIG = strat.ASSET, strat.SIGNAL

SEQ = np.array([100.0] * 11 + [90.0, 99.0] + [100.0] * 10 + [101.0, 101.0, 101.0])   # 26 Monate (Puffer nach m23)
# Handrechnung (Monat: MA12, Schwelle, Ergebnis):
#   m11: MA = (11*100+90)/12 = 99.17 ; 90 < MA                        -> FLAT (erster Zustand)
#   m12: MA = (10*100+90+99)/12 = 99.08 ; 99 < MA                     -> FLAT
#   m13..m22: MA = (90+99+10*100)/12 = 99.08 ; Einstieg erst >= 100.07 -> 100 < 100.07 -> FLAT
#             (Basis wäre ab m13 LONG, weil 100 >= 99.08)
#   m23: MA = (99+10*100+101)/12 = 100.00 ; Einstieg bei >= 101.00 -> 101 >= 101.00 -> LONG


def _panel(asset_px: pd.Series, sig_px: pd.Series) -> Panel:
    close = pd.DataFrame({ASSET: asset_px, SIG: sig_px})
    open_ = close * 0.999                                   # Open leicht abweichend vom Close
    return Panel(open_, close)


def _month_panel(monthly, start="2001-01-01"):
    """Tagesdaten: jeder Handelstag trägt den Monatswert seines Monats; Monatsende = letzter Handelstag."""
    monthly = np.asarray(monthly, float)
    first = pd.Timestamp(start).to_period("M")
    last = first + (len(monthly) - 1)
    idx = pd.bdate_range(first.start_time, last.end_time)
    k = np.array([(d.year - first.year) * 12 + (d.month - first.month) for d in idx])
    px = pd.Series(monthly[k], index=idx)
    me_dates = pd.DatetimeIndex(pd.Series(idx, index=idx).groupby(k).last().to_numpy())   # Orakel im Test
    return _panel(px, px.copy()), me_dates


def _random_panel(n_years=12, seed=11, start="2001-01-02") -> Panel:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range(start, periods=int(252 * n_years))
    regime = np.where(np.sin(np.arange(len(idx)) / 160.0) > -0.3, 0.0006, -0.0012)
    r = regime + rng.normal(0.0, 0.01, len(idx))
    px = pd.Series(100 * np.exp(np.cumsum(r)), index=idx)
    return _panel(px, px * (1 + rng.normal(0, 0.0005, len(idx))))


def _seq_panel(last_value: float = 101.0):
    seq = SEQ.copy()
    seq[23] = last_value
    return _month_panel(seq)


def test_spec_contract():
    spec = strat.SPEC
    assert spec["id"] == "trend_ma12_band_etf"
    assert spec["variants"] == {}                           # H8: keine Varianten
    assert spec["params"]["band"] == 0.01
    sig = inspect.signature(strat.weights)
    for name in spec["params"]:
        assert name in sig.parameters, name
    assert set(spec["tickers"]) == {ASSET, SIG}
    assert spec["cost_bps"][ASSET] == 10.0


def test_band_out_of_range_is_rejected():
    panel, _ = _seq_panel()
    with pytest.raises(ValueError):
        strat.weights(panel, band=-0.01)
    with pytest.raises(ValueError):
        strat.weights(panel, band=1.0)


def test_shape_range_and_both_states_occur():
    panel = _random_panel()
    w = strat.weights(panel)
    assert list(w.columns) == [ASSET]
    assert len(w) > 60
    assert w.notna().all().all()
    assert set(np.unique(w.to_numpy())) <= {0.0, 1.0}
    assert (w.sum(axis=1) <= 1.0 + 1e-12).all() and (w >= 0).all().all()
    assert w[ASSET].nunique() == 2                          # Test ist nicht trivial: LONG und FLAT kommen vor
    flags = month_end_flags(panel.close.index)
    assert w.index.isin(flags.index[flags.to_numpy()]).all()
    assert panel.close.loc[w.index, ASSET].notna().all()    # keine Gewichte auf Titel ohne Kurs


def test_hand_calculated_decision_days():
    """(a) Exakte Gewichte an den Entscheidungsmonaten, Handrechnung siehe Modulkopf."""
    panel, me = _seq_panel(101.0)
    w = strat.weights(panel)[ASSET]
    assert w.loc[me[11]] == 0.0      # erster Zustand: 90 < MA12 -> FLAT
    assert w.loc[me[12]] == 0.0      # 99 < MA12 -> FLAT
    assert w.loc[me[13]] == 0.0      # 100 >= MA12, aber unter Einstiegsschwelle 100.07 -> FLAT
    assert w.loc[me[22]] == 0.0      # weiterhin im Band -> FLAT
    assert w.loc[me[23]] == 1.0      # 101 >= 100 * 1.01 -> LONG
    assert list(w.index) == list(me[11:])


def test_entry_exactly_at_upper_band_triggers_and_just_below_does_not():
    """(1) Schluss genau auf MA12 * 1.01 löst den Einstieg aus (>=), knapp darunter nicht."""
    panel, me = _seq_panel(101.0)                           # MA12 = 100.00 exakt -> Schwelle 101.00
    assert strat.weights(panel)[ASSET].loc[me[23]] == 1.0
    panel, me = _seq_panel(100.99)                          # MA12 = 99.9992 -> Schwelle 100.9992 > 100.99
    w = strat.weights(panel)[ASSET]
    assert w.loc[me[23]] == 0.0
    assert (w.loc[me[11]:me[23]] == 0.0).all()


def test_band_keeps_flat_state_above_ma12():
    """(2) Im Band bleibt FLAT, obwohl der Schluss über dem MA12 liegt; die Basis wäre LONG."""
    panel, me = _seq_panel(101.0)
    w = strat.weights(panel)[ASSET]
    b = base.weights(panel)[ASSET]
    in_band = me[13:23]                                     # m13..m22: 100 >= MA12 (99.08), < 100.07
    assert (w.loc[in_band] == 0.0).all()
    assert (b.loc[in_band] == 1.0).all()


def test_band_keeps_long_state_below_ma12():
    """(2) Im Band bleibt LONG, obwohl der Schluss unter dem MA12 liegt; Ausstieg erst unter MA12 * 0.99."""
    monthly = np.array([100.0] * 12 + [99.0, 98.0])
    panel, me = _month_panel(monthly)
    # m11: MA12 = 100.00, 100 >= 100 -> LONG (erster Zustand)
    # m12: MA12 = (11*100+99)/12 = 99.92, Ausstiegsschwelle 98.92; 99 >= 98.92 -> LONG gehalten
    # m13: MA12 = (10*100+99+98)/12 = 99.75, Ausstiegsschwelle 98.75; 98 < 98.75 -> FLAT
    w = strat.weights(panel)[ASSET]
    b = base.weights(panel)[ASSET]
    assert w.loc[me[11]] == 1.0
    assert w.loc[me[12]] == 1.0
    assert b.loc[me[12]] == 0.0                             # Basis stiege schon hier aus
    assert w.loc[me[13]] == 0.0


def test_first_state_and_warmup():
    """(e) Erster Zustand nur mit 12 Monatsenden; Gleichheit zählt als LONG."""
    panel, me = _month_panel(np.full(24, 100.0))
    w = strat.weights(panel)[ASSET]
    assert w.index[0] == me[11]
    assert (w == 1.0).all()


def test_band_zero_equals_base_on_sequence():
    """(4) band=0 ist exakt die Basis (gleiche Zeilen, gleiche Werte)."""
    panel, _ = _seq_panel(101.0)
    a = strat.weights(panel, band=0.0)
    b = base.weights(panel)
    assert list(a.index) == list(b.index)
    assert np.array_equal(a[ASSET].to_numpy(), b[ASSET].to_numpy())


def test_band_zero_equals_base_on_random_panel():
    """(4) Gleiche Reihen wie die Basis auf demselben synthetischen Panel, mit Wechseln."""
    panel = _random_panel(n_years=12)
    a = strat.weights(panel, band=0.0)
    b = base.weights(panel)
    assert list(a.index) == list(b.index)
    assert np.array_equal(a[ASSET].to_numpy(), b[ASSET].to_numpy())
    assert a[ASSET].nunique() == 2


def test_band_changes_result_on_random_panel():
    """Gegenprobe: mit dem Band 1 % ändert sich die Reihe tatsächlich (sonst wäre (4) leer)."""
    panel = _random_panel(n_years=12)
    a = strat.weights(panel, band=0.0)[ASSET]
    b = strat.weights(panel, band=0.01)[ASSET]
    assert list(a.index) == list(b.index)
    assert (a != b).any()


def test_signal_column_drives_decision():
    up = np.linspace(100, 200, 30)
    panel_a, _ = _month_panel(up)
    falling = pd.Series(np.linspace(200, 100, len(panel_a.close)), index=panel_a.close.index)
    panel_b = _panel(panel_a.close[ASSET], falling)
    assert (strat.weights(panel_b)[ASSET] == 0.0).all()                 # ^GSPC fällt -> FLAT trotz steigendem SPY
    assert (strat.weights(panel_b, signal=ASSET)[ASSET] == 1.0).all()   # Signal aus SPY selbst


def test_no_weights_before_etf_listing():
    panel = _random_panel(n_years=6)
    close = panel.close.copy()
    listing = close.index[400]
    close.loc[:close.index[399], ASSET] = np.nan
    p2 = Panel((close * 0.999).copy(), close)
    w = strat.weights(p2)
    assert len(w) > 0
    assert w.index.min() >= listing
    assert not p2.close.loc[w.index, ASSET].isna().any()


def test_signal_gaps_forward_filled_only_briefly():
    panel, me = _month_panel(np.linspace(100, 140, 30))
    close = panel.close.copy()
    d = me[20]
    close.loc[d, SIG] = np.nan
    assert d in strat.weights(Panel(close * 0.999, close)).index          # kurze Lücke: Vortag genutzt
    close = panel.close.copy()
    pos = close.index.get_loc(d)
    close.iloc[pos - 8:pos + 1, close.columns.get_loc(SIG)] = np.nan
    assert d not in strat.weights(Panel(close * 0.999, close)).index       # lange Lücke: kein Signal


def test_causality_check():
    """(3) Kausalität mit dem Harness-Check."""
    panel = _random_panel(n_years=12)
    assert check_causality(lambda p: strat.weights(p), panel) == []


def test_causality_check_on_band_sequence():
    panel, _ = _seq_panel(101.0)
    assert check_causality(lambda p: strat.weights(p), panel, n_cuts=8) == []


def test_future_prices_do_not_change_past_weights():
    """(3) Kurse nach dem Schnitt verändern keine Gewichte davor."""
    panel = _random_panel(n_years=10)
    base_w = strat.weights(panel)
    cut = panel.close.index[int(len(panel.close) * 0.6)]
    close = panel.close.copy()
    close.loc[close.index > cut] *= 0.01
    other = strat.weights(Panel((close * 0.999).copy(), close))
    assert base_w.loc[:cut].equals(other.loc[:cut])


def test_last_data_day_mid_month_is_not_month_end():
    panel = _random_panel(n_years=4)
    idx = panel.close.index
    mid = idx[idx >= pd.Timestamp("2003-06-10")][0]
    w = strat.weights(panel.truncate(mid))
    assert w.index.max() < pd.Timestamp("2003-06-01")


def test_engine_integration_timing_and_exposure():
    panel, _ = _seq_panel(101.0)
    rng = np.random.default_rng(2)
    noise = pd.Series(1 + rng.normal(0, 0.002, len(panel.close)), index=panel.close.index)
    close = panel.close.mul(noise, axis=0)
    p2 = Panel((close * 0.999).copy(), close)
    w = strat.weights(p2)
    res = run_backtest(p2, w)
    assert (res.gross_exposure <= 1.0 + 1e-3).all()
    assert (res.weights[ASSET] >= -1e-9).all()
    s = w.index[w[ASSET] == 1.0][0]
    assert res.weights.loc[s, ASSET] == 0.0                                  # Signaltag: noch keine Position
    nxt = p2.close.index[p2.close.index.get_loc(s) + 1]
    assert res.weights.loc[nxt, ASSET] > 0.95                                # Handel am Folgetag (Eröffnung)
    pos = p2.close.index.get_indexer(w.index) + 1
    exec_days = p2.close.index[pos[pos < len(p2.close.index)]]
    assert (res.turnover.drop(exec_days) <= 1e-12).all()                     # sonst kein Umsatz


def test_run_backtest_finite_on_random_panel():
    """(d) Keine Varianten vorhanden; Standardlauf liefert endliche Kennzahlen."""
    panel = _random_panel(n_years=12)
    w = strat.weights(panel, **strat.SPEC["params"])
    res = run_backtest(panel, w)
    assert np.isfinite(res.nav.to_numpy()).all()
    assert (res.nav > 0).all()
    assert (res.gross_exposure <= 1.0 + 1e-3).all()          # Kursdrift zwischen Rebalancings, wie im Basis-Test
