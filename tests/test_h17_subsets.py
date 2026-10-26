"""Tests fuer scripts/check_h17_subsets.py (H17 Marktauswahl): nur synthetische Daten, kein Netz."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def _load(name: str):
    import sys
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


h17 = _load("check_h17_subsets")
h12 = _load("check_h12_robust_basket")
tp = _load("check_trend_portfolio")

N_MARKETS = 14


def _zero_rf(idx) -> pd.Series:
    return pd.Series(0.0, index=pd.DatetimeIndex(idx))


def _close(seed: int, n: int = 1500, start: str = "2000-01-03") -> pd.Series:
    rng = np.random.default_rng(seed)
    r = rng.normal(0.0003, 0.012, n)
    return pd.Series(100.0 * np.cumprod(1.0 + r), index=pd.bdate_range(start, periods=n))


def _closes() -> dict:
    # unterschiedliche Startzeitpunkte, damit die Gueltigkeit je Tag variiert
    return {f"M{i:02d}": _close(100 + i, n=1500 - 40 * (i % 4), start="2000-01-03") for i in range(N_MARKETS)}


def _data():
    closes = _closes()
    SL, BH, skipped = h17.load_sleeves(list(closes), loader=lambda t: closes[t], rf_fn=_zero_rf)
    assert not skipped
    return closes, SL, BH


def test_random_subset_reproducible_and_size_range():
    mk = [f"M{i:02d}" for i in range(17)]
    for seed in range(60):
        a = h17.random_subset(mk, seed)
        assert a == h17.random_subset(mk, seed)
        assert 8 <= len(a) <= 12
        assert len(set(a)) == len(a) and set(a) <= set(mk)
    sizes = {len(h17.random_subset(mk, s)) for s in range(300)}
    assert sizes == {8, 9, 10, 11, 12}                      # alle Groessen kommen vor
    assert h17.random_subset(mk, 0) != h17.random_subset(mk, 1)


def test_full_set_equals_h12_base1x_pipeline():
    """Teilmenge = alle Maerkte entspricht dem base1x-Korb der H12-Pipeline (gleiche Funktionen, gleicher Index)."""
    closes, SL, BH = _data()
    ev = h17.evaluate_subset(SL, BH, list(SL.columns), 8, rf_fn=_zero_rf)
    # unabhaengiger Nachbau nach H12-Muster
    ret = {t: h12.sleeve2(c, _zero_rf(c.index), lengths=(12,), target=None)["ret"] for t, c in closes.items()}
    base, _ = tp.basket(pd.DataFrame(ret), 8)
    bh = {t: closes[t].pct_change(fill_method=None).loc[ret[t].index[0]:].fillna(0.0) for t in closes}
    bhk, _ = tp.basket(pd.DataFrame(bh), 8)
    common = base.index.intersection(bhk.index)
    k = h12.konstanz(base.reindex(common), _zero_rf(common))
    assert ev["n_days"] == len(common)
    assert np.isclose(ev["cagr_s"], k["cagr"]) and np.isclose(ev["upi_s"], k["upi"])
    assert np.isclose(ev["maxdd_s"], k["max_dd"])


def test_leave_one_out_has_one_row_per_market_with_n_minus_one():
    _, SL, BH = _data()
    mk = list(SL.columns)
    loo = h17.leave_one_out(SL, BH, mk, min_markets=8, rf_fn=_zero_rf)
    assert len(loo) == len(mk) and set(loo["removed"]) == set(mk)
    assert (loo["n_markets"] == len(mk) - 1).all()


def test_markets_not_in_subset_have_no_influence():
    """Ergebnis haengt nur von den Maerkten der Teilmenge ab (Spalten ausserhalb werden ignoriert)."""
    _, SL, BH = _data()
    sub = list(SL.columns[:10])
    a = h17.evaluate_subset(SL, BH, sub, 6, rf_fn=_zero_rf)
    b = h17.evaluate_subset(SL[sub], BH[sub], sub, 6, rf_fn=_zero_rf)
    assert a == b


def test_causality_sleeve_prefix_unchanged_when_future_removed():
    """Kausalitaet: Abschneiden der Zukunft aendert die Sleeve-Renditen davor nicht."""
    c = _close(7, n=1400)
    full = h12.sleeve2(c, _zero_rf(c.index), lengths=(12,), target=None)["ret"]
    cut = c.iloc[:1000]
    part = h12.sleeve2(cut, _zero_rf(cut.index), lengths=(12,), target=None)["ret"]
    common = part.index[:-5]            # die letzten Tage vor dem Schnitt sind vom Randverhalten betroffen
    np.testing.assert_allclose(full.reindex(common).to_numpy(), part.reindex(common).to_numpy(), atol=1e-12)


def test_shares_and_passes_logic():
    df = pd.DataFrame({"dd_better": [True] * 19 + [False], "upi_better": [True] * 16 + [False] * 4})
    assert h17.shares(df) == (0.95, 0.80)
    assert h17.passes(df)
    df2 = pd.DataFrame({"dd_better": [True] * 18 + [False] * 2, "upi_better": [True] * 20})
    assert not h17.passes(df2)                               # 90 % < 95 %
    df3 = pd.DataFrame({"dd_better": [True] * 20, "upi_better": [True] * 15 + [False] * 5})
    assert not h17.passes(df3)                               # 75 % < 80 %


def test_random_subsets_run_and_flags_consistent():
    _, SL, BH = _data()
    rnd = h17.random_subsets(SL, BH, list(SL.columns), n=12, min_markets=6, rf_fn=_zero_rf)
    assert len(rnd) == 12 and rnd["n_markets"].between(8, 12).all()
    assert (rnd["dd_better"] == (rnd["maxdd_s"] > rnd["maxdd_bh"])).all()
    assert (rnd["upi_better"] == (rnd["upi_s"] > rnd["upi_bh"])).all()
    assert (rnd["maxdd_s"] <= 0).all() and (rnd["maxdd_bh"] <= 0).all()


def test_always_cash_market_cannot_beat_flat_basket_flags():
    """Plausibilitaet: aufsteigender Markt (immer long) -> base1x ~ B&H abzueglich Kosten, kein Absturz/NaN."""
    n = 1200
    idx = pd.bdate_range("2001-01-01", periods=n)
    closes = {f"U{i}": pd.Series(100.0 * np.cumprod(np.full(n, 1.0005 + 0.00001 * i)), index=idx) for i in range(10)}
    SL, BH, _ = h17.load_sleeves(list(closes), loader=lambda t: closes[t], rf_fn=_zero_rf)
    ev = h17.evaluate_subset(SL, BH, list(SL.columns), 6, rf_fn=_zero_rf)
    assert np.isfinite(ev["cagr_s"]) and np.isfinite(ev["maxdd_s"])
    assert ev["cagr_s"] <= ev["cagr_bh"] + 1e-9              # nie besser als B&H bei reinem Aufwaertstrend (Kosten)
