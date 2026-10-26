"""Tests fuer scripts/check_trend_vt_basket.py (sleeve, H11): nur synthetische Daten, kein Netz."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from qlab.calendar import month_end_flags

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_trend_vt_basket.py"
_spec = importlib.util.spec_from_file_location("check_trend_vt_basket", SCRIPT)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)
sleeve = mod.sleeve
monthly_state = mod.monthly_state


def _ts(n: int) -> pd.DatetimeIndex:
    return pd.bdate_range("2000-01-03", periods=n)


def _from_returns(r: np.ndarray) -> pd.Series:
    return pd.Series(100.0 * np.cumprod(1.0 + r), index=_ts(len(r)))


def _random_close(n=900, seed=1, mu=0.0003, sig=0.01) -> pd.Series:
    rng = np.random.default_rng(seed)
    return _from_returns(rng.normal(mu, sig, n))


def _zero_rf(idx) -> pd.Series:
    return pd.Series(0.0, index=idx)


def _sigma_ref(close: pd.Series) -> np.ndarray:
    """Eigene EWMA-Rekursion (Halbwertszeit 20, adjust=False), annualisiert mit 252."""
    r = close.pct_change(fill_method=None).to_numpy()
    alpha = 1.0 - np.exp(-np.log(2.0) / 20.0)
    out = np.full(len(r), np.nan)
    var = None
    for i, x in enumerate(r):
        if np.isnan(x):
            continue
        var = x * x if var is None else alpha * x * x + (1 - alpha) * var
        out[i] = np.sqrt(var * 252.0)
    return out


def _month_end_positions(idx: pd.DatetimeIndex) -> np.ndarray:
    return np.flatnonzero(month_end_flags(idx).to_numpy())


def test_gewicht_min_cap_und_handrechnung():
    close = _random_close(n=900, seed=2, mu=0.002, sig=0.01)
    st = monthly_state(close)
    assert bool(st.iloc[0]), "Annahme des Tests: erster Zustand ist LONG"
    s_i = close.index.get_loc(st.index[0])
    sig = _sigma_ref(close)
    rf = _zero_rf(close.index)

    out = sleeve(close, rf, target=0.15, cap=1.5)
    # Zielgewicht ohne Cap-Bindung: 0,15 / sigma
    w_expect = min(1.5, 0.15 / sig[s_i])
    assert out["pos"].iloc[0] == 0.0
    assert out["pos"].iloc[2] == pytest.approx(w_expect, abs=1e-12)

    # Cap bindet: target sehr gross
    out_cap = sleeve(close, rf, target=5.0, cap=1.5)
    assert out_cap["pos"].iloc[2] == pytest.approx(1.5, abs=1e-12)
    assert out_cap["pos"].max() == pytest.approx(1.5, abs=1e-12)


def test_gewicht_mit_sigma_null_oder_flat_ist_null():
    close = _from_returns(np.zeros(900))            # sigma = 0 -> kein Gewicht
    out = sleeve(close, _zero_rf(close.index), target=0.15, cap=1.5)
    assert (out["pos"] == 0.0).all()


def test_ausfuehrungsverzoegerung_zwei_tage():
    close = _random_close(n=900, seed=2, mu=0.002, sig=0.01)
    st = monthly_state(close)
    s_i = close.index.get_loc(st.index[0])
    m_all = _month_end_positions(close.index)
    m2_i = m_all[m_all > s_i][0]                     # naechstes Monatsende nach dem Sleeve-Start
    sig = _sigma_ref(close)
    out = sleeve(close, _zero_rf(close.index), target=0.15, cap=1.5)
    pos = out["pos"].to_numpy()
    s_out = s_i - 0                                  # Sleeve-Ausgabe beginnt am Start
    assert pos[0] == 0.0 and pos[1] == 0.0           # Entscheidung m wirkt noch nicht auf m+1
    w1 = min(1.5, 0.15 / sig[s_i])
    w2 = min(1.5, 0.15 / sig[m2_i])
    assert pos[2] == pytest.approx(w1, abs=1e-12)    # wirkt erst ab m+2
    assert pos[m2_i - s_i + 1] == pytest.approx(w1, abs=1e-12)   # alte Gewichte bis m2+1
    assert pos[m2_i - s_i + 2] == pytest.approx(w2, abs=1e-12)   # neues Gewicht ab m2+2
    assert s_out == s_i


def test_kosten_und_finanzierungsaufschlag_handrechnung():
    close = _random_close(n=900, seed=2, mu=0.002, sig=0.01)
    rf_const = 0.0001
    rf = pd.Series(rf_const, index=close.index)
    bps, markup = 10.0, 0.025
    out = sleeve(close, rf, target=10.0, cap=1.5, bps=bps, fin_markup=markup)   # Gewicht = Cap 1,5
    r = close.pct_change(fill_method=None)
    pos = out["pos"]
    assert pos.iloc[2] == pytest.approx(1.5)
    # Einstiegstag: Gewicht 1,5 aus 0 -> Kosten 1,5 * 10 bp, Markup auf 0,5 Hebel
    d = out.index[2]
    expect = 1.5 * r[d] + (1 - 1.5) * rf[d] - 0.5 * markup / 252 - 1.5 * bps / 1e4
    assert out["ret"].loc[d] == pytest.approx(expect, abs=1e-12)
    # Halteliegen ohne Wechsel: nur Markup und Finanzierung
    d2 = out.index[10]
    expect2 = 1.5 * r[d2] + (1 - 1.5) * rf[d2] - 0.5 * markup / 252
    assert out["ret"].loc[d2] == pytest.approx(expect2, abs=1e-12)


def test_kausalitaet_spaetere_kurse_aendern_frueheres_nicht():
    close1 = _random_close(n=900, seed=3, mu=0.001, sig=0.012)
    d = 500
    close2 = close1.copy()
    close2.iloc[d + 1:] = close2.iloc[d + 1:] * np.linspace(0.6, 1.4, len(close2) - d - 1)
    rf = _zero_rf(close1.index)
    kw = dict(target=0.15, cap=1.5, trail_m=2.0, rr=3.0)
    o1 = sleeve(close1, rf, **kw)
    o2 = sleeve(close2, rf, **kw)
    cut = close1.index[d]
    a, b = o1.loc[:cut], o2.loc[:cut]
    np.testing.assert_array_equal(a["pos"].to_numpy(), b["pos"].to_numpy())
    np.testing.assert_array_equal(a["ret"].to_numpy(), b["ret"].to_numpy())
    np.testing.assert_array_equal(a["sigma"].to_numpy(), b["sigma"].to_numpy())
    assert (a["state"].to_numpy() == b["state"].to_numpy()).all()
    # Gegenprobe: nach d aendert sich tatsaechlich etwas
    assert not np.allclose(o1.loc[cut:, "ret"].to_numpy(), o2.loc[cut:, "ret"].to_numpy())


def _uptrend_then_drop(n_up=260, n_drop=8, n_after=300):
    rng_pattern = np.array([1.0 if k % 2 == 0 else -1.0 for k in range(n_up)])
    r_up = 0.0014 + 0.0002 * rng_pattern
    r_drop = np.full(n_drop, -0.02)
    r_after = 0.0014 + 0.0002 * np.array([1.0 if k % 2 == 0 else -1.0 for k in range(n_after)])
    return _from_returns(np.concatenate([r_up, r_drop, r_after]))


def test_trailing_stop_ausstieg_und_sperre_bis_naechstes_monatsende():
    close = _uptrend_then_drop()
    rf = _zero_rf(close.index)
    out = sleeve(close, rf, target=0.15, cap=1.5, trail_m=2.0)
    s_i = close.index.get_loc(out.index[0])
    pos = out["pos"].reindex(close.index).fillna(0.0).to_numpy()   # volle Kalenderlaenge
    sig = _sigma_ref(close)
    c = close.to_numpy()

    entry = int(np.flatnonzero(pos > 0)[0])          # erster Tag mit Position
    hh = c[entry - 1]
    t = None
    for i in range(entry, len(c)):
        hh = max(hh, c[i])
        if c[i] < hh * (1 - 2.0 * sig[i] / np.sqrt(12)):
            t = i
            break
    assert t is not None, "Testszenario: Stop muss ausloesen"
    # Handrechnung: vor t kein Ausloesen (oben gesucht); Ausstieg zum Schluss t+1, pos ab t+2 gleich 0
    assert pos[t] > 0 and pos[t + 1] > 0
    assert pos[t + 2] == 0.0
    # Kein Wiedereinstieg vor dem naechsten Monatsende mit LONG
    m_all = _month_end_positions(close.index)
    m_next = m_all[m_all > t][0]
    assert (pos[t + 2:m_next + 2] == 0.0).all()
    assert out["state"].iloc[m_next - s_i] == "LONG"
    assert pos[m_next + 2] > 0.0


def test_ohne_trailing_stop_bleibt_long_im_rueckgang():
    close = _uptrend_then_drop()
    out = sleeve(close, _zero_rf(close.index), target=0.15, cap=1.5)
    pos = out["pos"].to_numpy()
    entry = int(np.flatnonzero(pos > 0)[0])
    assert (pos[entry:] > 0).all()


def test_gewinnziel_loest_bei_erreichen_aus():
    close = _random_close(n=900, seed=7, mu=0.0015, sig=0.0005)   # fast monoton steigend
    rf = _zero_rf(close.index)
    out = sleeve(close, rf, target=0.15, cap=1.5, trail_m=2.0, rr=3.0)
    sig = _sigma_ref(close)
    c = close.to_numpy()
    pos = out["pos"].reindex(close.index).fillna(0.0).to_numpy()
    entry = int(np.flatnonzero(pos > 0)[0])
    E = c[entry - 1]
    st_sig = sig[entry - 2]                          # sigma am Entscheidungstag (Monatsende m = entry-2)
    D = 2.0 * st_sig / np.sqrt(12) * E
    target = E + 3.0 * D
    hits = np.flatnonzero(c[entry:] >= target)
    assert len(hits) > 0, "Testszenario: Ziel muss erreicht werden"
    t = entry + int(hits[0])
    assert pos[t] > 0 and pos[t + 1] > 0
    assert pos[t + 2] == 0.0

    # Gegenprobe: ohne Ziel bleibt die Position in diesem Anstieg gehalten
    o_no_rr = sleeve(close, rf, target=0.15, cap=1.5, trail_m=2.0)
    pos_no = o_no_rr["pos"].reindex(close.index).fillna(0.0).to_numpy()
    assert (pos_no[entry:t + 3] > 0).all()


def test_rr_ohne_trail_wirft_fehler():
    close = _random_close(n=900, seed=7)
    with pytest.raises(ValueError):
        sleeve(close, _zero_rf(close.index), rr=3.0)


def test_ohne_stops_und_ohne_skalierung_entspricht_zustand_mit_verzoegerung():
    close = _random_close(n=900, seed=5, mu=0.0005, sig=0.01)
    rf = pd.Series(0.0001, index=close.index)
    out = sleeve(close, rf, vol_scaled=False, cap=1.0)
    s_i = close.index.get_loc(out.index[0])
    st_daily = monthly_state(close).reindex(close.index).fillna(False).to_numpy(bool)
    flags = month_end_flags(close.index).to_numpy()
    dec_days = [i for i in range(s_i, len(close)) if flags[i]]

    expect = np.zeros(len(close))
    for j in range(s_i, len(close)):
        cand = [m for m in dec_days if m + 2 <= j]
        if cand:
            expect[j] = 1.0 if st_daily[cand[-1]] else 0.0
    got = out["pos"].to_numpy()
    np.testing.assert_array_equal(got, expect[s_i:])
    assert set(np.unique(got)) <= {0.0, 1.0}

    # Rendite exakt: pos r + (1-pos) rf - |Delta pos| bps
    r = close.pct_change(fill_method=None).to_numpy()[s_i:]
    rfa = rf.to_numpy()[s_i:]
    prev = np.concatenate([[0.0], got[:-1]])
    ret_expect = got * r + (1 - got) * rfa - np.abs(got - prev) * 10.0 / 1e4
    np.testing.assert_allclose(out["ret"].to_numpy(), ret_expect, rtol=0, atol=1e-14)


def test_flat_ergibt_null_position_und_rf_rendite():
    close = _from_returns(np.full(900, -0.001))      # monoton fallend: Monatsschluss stets unter MA12
    rf = pd.Series(np.linspace(0.00005, 0.00015, len(close)), index=close.index)
    out = sleeve(close, rf, target=0.15, cap=1.5, trail_m=2.0, rr=3.0)
    assert (out["state"] == "Cash").all()
    assert (out["pos"] == 0.0).all()
    np.testing.assert_allclose(out["ret"].to_numpy(), rf.reindex(out.index).to_numpy(), rtol=0, atol=1e-15)
