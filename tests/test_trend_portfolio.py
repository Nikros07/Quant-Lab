"""Tests für scripts/check_trend_portfolio.py (basket): nur synthetische Daten, kein Netz."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_trend_portfolio.py"
_spec = importlib.util.spec_from_file_location("check_trend_portfolio", SCRIPT)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)
basket = mod.basket


def _idx(n: int) -> pd.DatetimeIndex:
    return pd.bdate_range("2001-01-01", periods=n)


def test_zwei_identische_reihen_ergeben_die_reihe():
    idx = _idx(10)
    x = pd.Series(np.linspace(-0.02, 0.03, 10), index=idx)
    df = pd.DataFrame({"a": x, "b": x})
    ret, n = basket(df, min_markets=2)
    pd.testing.assert_series_equal(ret, x, check_names=False)
    assert (n == 2).all()


def test_unterschiedlicher_start_keine_werte_vor_korbstart():
    idx = _idx(8)
    a = pd.Series([0.01] * 8, index=idx)
    b = pd.Series([0.03] * 8, index=idx)
    b.iloc[:2] = np.nan                                  # b startet an Tag 2
    c = pd.Series([0.05] * 8, index=idx)
    c.iloc[:4] = np.nan                                  # c startet an Tag 4
    df = pd.DataFrame({"a": a, "b": b, "c": c})
    ret, n = basket(df, min_markets=2)
    # Erster Tag mit >= 2 gültigen Märkten ist Tag 2 (a und b)
    assert ret.index[0] == idx[2]
    assert idx[1] not in ret.index
    assert ret.loc[idx[2]] == np.mean([0.01, 0.03])
    # Ab Tag 4 zählt c mit, Mittelwert nur über gültige Märkte
    assert ret.loc[idx[4]] == np.mean([0.01, 0.03, 0.05])


def test_gleiche_gewichte_von_hand():
    idx = _idx(3)
    df = pd.DataFrame({
        "a": [0.010, -0.020, 0.030],
        "b": [0.020, 0.040, -0.010],
        "c": [0.030, 0.000, 0.020],
    }, index=idx)
    ret, _ = basket(df, min_markets=3)
    expected =[(0.010 + 0.020 + 0.030) / 3, (-0.020 + 0.040 + 0.000) / 3, (0.030 - 0.010 + 0.020) / 3]
    np.testing.assert_allclose(ret.to_numpy(), expected, rtol=0, atol=1e-12)


def test_nan_eines_marktes_aendert_nur_den_nenner_dieses_tages():
    idx = _idx(5)
    a = pd.Series([0.01, 0.02, np.nan, 0.04, 0.05], index=idx)
    b = pd.Series([0.03, 0.03, 0.03, 0.03, 0.03], index=idx)
    c = pd.Series([0.06, 0.06, 0.06, 0.06, 0.06], index=idx)
    ret, n = basket(pd.DataFrame({"a": a, "b": b, "c": c}), min_markets=2)
    assert ret.loc[idx[2]] == np.mean([0.03, 0.06])      # nur b und c, Nenner 2
    assert ret.loc[idx[0]] == np.mean([0.01, 0.03, 0.06])
    assert ret.loc[idx[3]] == np.mean([0.04, 0.03, 0.06])
    assert ret.loc[idx[4]] == np.mean([0.05, 0.03, 0.06])


def test_n_markets_stimmt():
    idx = _idx(6)
    a = pd.Series([0.0] * 6, index=idx)
    b = pd.Series([0.0] * 6, index=idx)
    c = pd.Series([0.0] * 6, index=idx)
    a.iloc[0] = np.nan
    b.iloc[:2] = np.nan
    c.iloc[4:] = np.nan
    _, n = basket(pd.DataFrame({"a": a, "b": b, "c": c}), min_markets=1)
    # Tag 0: nur c; Tag 1: a,c; Tag 2..3: a,b,c; Tag 4..5: a,b
    assert n.tolist() == [1, 2, 3, 3, 2, 2]
    assert n.index[0] == idx[0]


def test_korbstart_erst_bei_min_markets():
    idx = _idx(4)
    df = pd.DataFrame({
        "a": [0.01, 0.01, 0.01, 0.01],
        "b": [np.nan, 0.02, 0.02, 0.02],
        "c": [np.nan, np.nan, 0.03, 0.03],
    }, index=idx)
    ret, n = basket(df, min_markets=3)
    assert ret.index[0] == idx[2]
    assert n.iloc[0] == 3


def test_duenne_tage_werden_standardmaessig_verworfen():
    """H6-Korrektur: ein Tag mit nur 1 gültigem Markt (Wochenende nur BTC) darf nicht im Korb stehen."""
    idx = _idx(6)
    a = pd.Series([0.01] * 6, index=idx)
    b = pd.Series([0.02] * 6, index=idx)
    c = pd.Series([0.03, 0.03, 0.03, 0.03, 0.03, 0.03], index=idx)
    df = pd.DataFrame({"a": a, "b": b, "c": c})
    df.iloc[3, [0, 1]] = np.nan                       # Tag 3: nur Markt c gültig
    ret, n = basket(df, min_markets=3)                # Standard: dünne Tage verwerfen
    assert idx[3] not in ret.index and idx[3] not in n.index
    assert len(ret) == 5 and (n == 3).all()
    ret2, n2 = basket(df, min_markets=3, drop_thin_days=False)
    assert idx[3] in ret2.index and n2.loc[idx[3]] == 1
    assert ret2.loc[idx[3]] == 0.03                   # Alt-Verhalten: 100 % auf den einen Markt
