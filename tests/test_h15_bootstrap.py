"""Tests fuer scripts/check_h15_bootstrap.py (H15): nur synthetische Daten, kein Netz."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def _load(name: str):
    import sys
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


h15 = _load("check_h15_bootstrap")
h12 = _load("check_h12_robust_basket")


def _series(n=1500, seed=3, mu=0.0004, sig=0.01) -> pd.Series:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2000-01-03", periods=n)
    return pd.Series(rng.normal(mu, sig, n), index=idx)


def test_indices_laenge_bereich_und_determinismus():
    a = h15.stationary_indices(500, 60, np.random.default_rng([15, 0]))
    b = h15.stationary_indices(500, 60, np.random.default_rng([15, 0]))
    c = h15.stationary_indices(500, 60, np.random.default_rng([15, 1]))
    assert len(a) == 500 and a.min() >= 0 and a.max() < 500
    assert np.array_equal(a, b)          # feste Seeds -> reproduzierbar
    assert not np.array_equal(a, c)


def test_mittlere_blocklaenge_stimmt():
    n = 200_000
    ix = h15.stationary_indices(n, 60, np.random.default_rng(1))
    fortsetzung = (ix[1:] == (ix[:-1] + 1) % n)
    p_neu = 1.0 - fortsetzung.mean()    # Anteil Blockanfaenge ~ 1/60 (minus zufaellige Treffer ~ 1/n)
    assert p_neu == pytest.approx(1 / 60, rel=0.1)


def test_ein_riesiger_block_ist_zyklische_verschiebung():
    ix = h15.stationary_indices(300, 1e12, np.random.default_rng(7))
    assert np.array_equal(np.sort(ix), np.arange(300))                   # Permutation
    assert np.all((ix[1:] - ix[:-1]) % 300 == 1)                         # nur eine Verschiebung


def test_kennzahlen_gleich_h12_konstanz():
    r = _series()
    rf = pd.Series(0.00008, index=r.index)
    ppy = h15.metrics.periods_per_year(r.index)
    k = h15.kennzahlen(r.to_numpy(), rf.to_numpy(), ppy)
    ref = h12.konstanz(r, rf)
    for key in h15.KEYS:
        assert k[key] == pytest.approx(ref[key], rel=1e-9, abs=1e-12), key


def test_identische_reihen_geben_null_differenz():
    r = _series(600)
    rf = np.zeros(len(r))
    d = h15.bootstrap(r.to_numpy(), r.to_numpy(), rf, 252.0, n_draws=30)
    for k in h15.KEYS:
        assert np.allclose(d[f"d_{k}"].to_numpy(), 0.0)        # gepaart: gleicher Indexvektor fuer beide Reihen
    res = h15.auswerten(d)
    assert res["verlustvorteil_belegt"] is False                # 5. Perzentil = 0 ist nicht > 0
    assert res["p_cagr_lower"] == 0.0


def test_cagr_ist_permutationsinvariant_bei_einem_block():
    a = _series(800, seed=4).to_numpy()
    b = _series(800, seed=5, mu=0.0001, sig=0.014).to_numpy()
    rf = np.zeros(800)
    d = h15.bootstrap(a, b, rf, 252.0, n_draws=10, mean_block=1e12)
    pa, pb = h15.kennzahlen(a, rf, 252.0), h15.kennzahlen(b, rf, 252.0)
    assert np.allclose(d["d_cagr"].to_numpy(), pa["cagr"] - pb["cagr"], atol=1e-12)


def test_kriterium_defensiv_gegen_stark_fallenden_korb():
    rng = np.random.default_rng(11)
    n = 2000
    bh = rng.normal(0.0003, 0.015, n)
    bh[600:700] = -0.012                                         # lange, tiefe Verlustphase in der Reihe
    sicher = np.where(bh < -0.005, 0.0, bh * 0.5)                # raus aus fallenden Tagen (nur Test, kein Handel)
    rf = np.zeros(n)
    d = h15.bootstrap(sicher, bh, rf, 252.0, n_draws=200)
    res = h15.auswerten(d)
    assert res["max_dd"]["p05"] > 0
    assert res["verlustvorteil_belegt"] is True


def test_bootstrap_bei_schlechterem_korb_nicht_belegt():
    rng = np.random.default_rng(12)
    n = 1500
    bh = rng.normal(0.0004, 0.008, n)
    riskant = bh * 3.0                                           # mehr Hebel -> tieferer Drawdown
    d = h15.bootstrap(riskant, bh, np.zeros(n), 252.0, n_draws=100)
    assert h15.auswerten(d)["verlustvorteil_belegt"] is False


def test_bootstrap_reproduzierbar_und_seedabhaengig():
    a, b = _series(500, seed=1).to_numpy(), _series(500, seed=2).to_numpy()
    rf = np.zeros(500)
    d1 = h15.bootstrap(a, b, rf, 252.0, n_draws=20, seed=15)
    d2 = h15.bootstrap(a, b, rf, 252.0, n_draws=20, seed=15)
    d3 = h15.bootstrap(a, b, rf, 252.0, n_draws=20, seed=16)
    pd.testing.assert_frame_equal(d1, d2)
    assert not d1["d_cagr"].equals(d3["d_cagr"])


def test_laengen_mismatch_wirft_fehler():
    with pytest.raises(ValueError):
        h15.bootstrap(np.zeros(10), np.zeros(9), np.zeros(10), 252.0, n_draws=2)


def test_base1x_eingang_ist_kausal():
    """Aendern nur der Kurse nach T aendert die base1x-Renditen (Eingang des Bootstraps) bis T nicht."""
    rng = np.random.default_rng(21)
    n = 900
    idx = pd.bdate_range("2005-01-03", periods=n)
    close = pd.Series(100 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, n))), index=idx)
    rf = pd.Series(0.00005, index=idx)
    T = 600
    c2 = close.copy()
    c2.iloc[T + 1:] = c2.iloc[T + 1:] * 1.7
    s1 = h12.sleeve2(close, rf, **h12.RUNS["base1x"])["ret"]
    s2 = h12.sleeve2(c2, rf, **h12.RUNS["base1x"])["ret"]
    assert np.allclose(s1.loc[:idx[T]].to_numpy(), s2.loc[:idx[T]].to_numpy())


def test_laden_csv_liest_gepaarte_spalten(tmp_path):
    p = tmp_path / "x.csv"
    pd.DataFrame({"date": ["2000-01-03", "2000-01-04", "2000-01-05"], "bh": [0.01, np.nan, 0.02],
                  "base1x": [0.0, 0.01, 0.0], "ens3": [1, 2, 3]}).to_csv(p, index=False)
    df = h15.laden_csv(p)
    assert list(df.columns) == ["bh", "base1x"] and len(df) == 2
