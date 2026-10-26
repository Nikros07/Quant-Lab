"""Tests für scripts/check_trend_basket_invvol.py (weighted_basket): nur synthetische Daten, kein Netz."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_trend_basket_invvol.py"
_spec = importlib.util.spec_from_file_location("check_trend_basket_invvol", SCRIPT)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)
weighted_basket = mod.weighted_basket


def _idx(n: int) -> pd.DatetimeIndex:
    return pd.bdate_range("2001-01-01", periods=n)


def _rand(n: int, seed: int, scale: float) -> pd.Series:
    rng = np.random.default_rng(seed)
    return pd.Series(rng.normal(0.0, scale, n), index=_idx(n))


def test_gewichte_summieren_sich_je_tag_auf_eins():
    n = 200
    bh = pd.DataFrame({"a": _rand(n, 1, 0.01), "b": _rand(n, 2, 0.02), "c": _rand(n, 3, 0.005)})
    sleeve = pd.DataFrame({"a": _rand(n, 4, 0.01), "b": _rand(n, 5, 0.01), "c": _rand(n, 6, 0.01)})
    ret, cnt, w = weighted_basket(sleeve, bh, window=20, min_markets=2)
    assert len(ret) > 0
    np.testing.assert_allclose(w.sum(axis=1).to_numpy(), 1.0, rtol=0, atol=1e-12)
    assert (cnt == 3).all()


def test_hoehere_volatilitaet_kleineres_gewicht_handrechnung():
    # Fenster 2: Std von [x, -x] (ddof=1) = x*sqrt(2). Vol a = 0,02*sqrt(2), Vol b = 0,01*sqrt(2), Verhältnis 2.
    # Erster Tag mit Vol: Index 2 (rolling ab Index 1, dann shift(1)). Dort inverse Vol: a = 1, b = 2 -> w_a = 1/3, w_b = 2/3.
    idx = _idx(5)
    bh = pd.DataFrame({
        "a": [0.02, -0.02, 0.02, -0.02, 0.02],
        "b": [0.01, -0.01, 0.01, -0.01, 0.01],
    }, index=idx)
    sleeve = pd.DataFrame({"a": 0.001, "b": 0.003}, index=idx)
    ret, cnt, w = weighted_basket(sleeve, bh, window=2, min_markets=2)
    assert list(ret.index) == list(idx[2:])
    assert w.loc[idx[2], "a"] == pytest.approx(1 / 3, rel=1e-9)
    assert w.loc[idx[2], "b"] == pytest.approx(2 / 3, rel=1e-9)
    assert ret.loc[idx[2]] == pytest.approx(1 / 3 * 0.001 + 2 / 3 * 0.003, rel=1e-9)
    assert w.loc[idx[2], "b"] > w.loc[idx[2], "a"]


def test_gleiche_volatilitaet_ergibt_gleichgewichtsmittel():
    n = 60
    base = _rand(n, 7, 0.01)
    bh = pd.DataFrame({"a": base, "b": base, "c": base})
    sleeve = pd.DataFrame({"a": _rand(n, 8, 0.01), "b": _rand(n, 9, 0.02), "c": _rand(n, 10, 0.015)})
    ret, cnt, w = weighted_basket(sleeve, bh, window=10, min_markets=2)
    np.testing.assert_allclose(w.to_numpy(), 1 / 3, rtol=0, atol=1e-12)
    np.testing.assert_allclose(ret.to_numpy(), sleeve.loc[ret.index].mean(axis=1).to_numpy(), rtol=0, atol=1e-12)


def test_kausalitaet_aenderung_am_tag_t_veraendert_gewichte_an_t_nicht():
    n, t = 80, 50
    bh = pd.DataFrame({"a": _rand(n, 11, 0.01), "b": _rand(n, 12, 0.02), "c": _rand(n, 13, 0.005)})
    sleeve = pd.DataFrame({"a": _rand(n, 14, 0.01), "b": _rand(n, 15, 0.01), "c": _rand(n, 16, 0.01)})
    idx = bh.index
    _, _, w = weighted_basket(sleeve, bh, window=10, min_markets=2)

    bh2 = bh.copy()
    bh2.iloc[t, :] += 0.05          # Buy&Hold-Renditen am Tag t geändert
    sleeve2 = sleeve.copy()
    sleeve2.iloc[t, 0] += 0.01      # Strategie-Rendite am Tag t geändert
    _, _, w2 = weighted_basket(sleeve2, bh2, window=10, min_markets=2)

    assert idx[t] in w.index and idx[t] in w2.index
    pd.testing.assert_frame_equal(w2.loc[:idx[t]], w.loc[:idx[t]])
    # Gegenprobe: am Folgetag wirkt die Änderung über die Volatilität
    assert not np.allclose(w2.loc[idx[t + 1]].to_numpy(), w.loc[idx[t + 1]].to_numpy())


def test_tage_mit_zu_wenig_gueltigen_maerkten_fallen_heraus():
    n, k = 40, 10
    bh = pd.DataFrame({"a": _rand(n, 17, 0.01), "b": _rand(n, 18, 0.02), "c": _rand(n, 19, 0.01)})
    sleeve = pd.DataFrame({"a": _rand(n, 20, 0.01), "b": _rand(n, 21, 0.01), "c": _rand(n, 22, 0.01)})
    sleeve.iloc[k, 0] = np.nan      # nur 2 gültige Märkte an Tag k
    ret, cnt, w = weighted_basket(sleeve, bh, window=5, min_markets=3)
    assert bh.index[k] not in ret.index
    assert bh.index[k + 1] in ret.index
    assert (cnt == 3).all()
    assert len(w) == len(ret)


def test_markt_ohne_ausreichende_historie_bekommt_kein_gewicht():
    n, window = 50, 10
    bh = pd.DataFrame({"a": _rand(n, 23, 0.01), "b": _rand(n, 24, 0.02)})
    # c: nur 9 Beobachtungen (< window), sonst NaN -> nie eine gültige Volatilität
    c = pd.Series(np.nan, index=_idx(n))
    c.iloc[41:] = np.random.default_rng(25).normal(0.0, 0.01, 9)
    bh["c"] = c
    sleeve = pd.DataFrame({"a": _rand(n, 26, 0.01), "b": _rand(n, 27, 0.01), "c": _rand(n, 28, 0.01)})
    ret, cnt, w = weighted_basket(sleeve, bh, window=window, min_markets=2)
    assert (w["c"] == 0).all()
    assert (cnt == 2).all()
    np.testing.assert_allclose(w[["a", "b"]].sum(axis=1).to_numpy(), 1.0, rtol=0, atol=1e-12)
