"""Tests fuer P2 (Falten verworfener Tage, Korb ohne BTC), synthetische Daten, kein Netz."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import check_p2_btc as p2
import check_trend_portfolio as tp


def _block(days=14, seed=0):
    """3 'Boersen'-Maerkte nur Mo-Fr, 1 'BTC'-Markt jeden Tag; Start Montag."""
    idx = pd.date_range("2024-01-01", periods=days, freq="D")
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(rng.normal(0.0, 0.01, size=(days, 4)), index=idx, columns=["a", "b", "c", "btc"])
    weekend = idx.dayofweek >= 5
    df.loc[weekend, ["a", "b", "c"]] = np.nan
    return df


def test_fold_conserves_growth_per_market():
    df = _block(14)
    f = p2.fold_thin_days(df, min_markets=2)
    # Die letzten behaltenen Tage enden am Freitag (Tag 11); der Rest (Sa/So danach) faellt weg
    for col in ["a", "b", "c", "btc"]:
        full = (1.0 + df.loc[:f.index[-1], col].fillna(0.0)).prod()
        folded = (1.0 + f[col].fillna(0.0)).prod()
        assert folded == pytest.approx(full, rel=1e-12)


def test_fold_moves_weekend_btc_into_monday():
    df = _block(14)
    f = p2.fold_thin_days(df, min_markets=2)
    monday = pd.Timestamp("2024-01-08")
    expected = (1.0 + df.loc["2024-01-06":"2024-01-08", "btc"]).prod() - 1.0   # Sa, So, Mo
    assert f.loc[monday, "btc"] == pytest.approx(expected, rel=1e-12)
    assert pd.Timestamp("2024-01-06") not in f.index and pd.Timestamp("2024-01-07") not in f.index


def test_fold_keeps_other_markets_unchanged_on_kept_days():
    df = _block(14)
    f = p2.fold_thin_days(df, min_markets=2)
    for col in ["a", "b", "c"]:
        pd.testing.assert_series_equal(f[col], df.loc[f.index, col], check_names=False)


def test_trailing_thin_days_dropped():
    df = _block(14)          # Index endet Sonntag 2024-01-14
    f = p2.fold_thin_days(df, min_markets=2)
    assert f.index[-1] == pd.Timestamp("2024-01-12")


def test_no_thin_days_equals_plain_basket():
    idx = pd.bdate_range("2024-01-01", periods=30)
    rng = np.random.default_rng(3)
    df = pd.DataFrame(rng.normal(0.0, 0.01, size=(30, 3)), index=idx, columns=["x", "y", "z"])
    r_old, n_old = tp.basket(df, 2)
    r_new, n_new = p2.basket_folded(df, 2)
    pd.testing.assert_series_equal(r_old, r_new, check_names=False, check_freq=False)
    pd.testing.assert_series_equal(n_old.astype(int), n_new.astype(int), check_names=False, check_freq=False)


def test_group_without_observation_stays_nan():
    idx = pd.date_range("2024-01-01", periods=6, freq="D")
    df = pd.DataFrame({"a": [0.01, 0.01, 0.01, 0.01, 0.01, 0.01],
                       "b": [0.01, 0.01, 0.01, 0.01, 0.01, 0.01],
                       "late": [np.nan, np.nan, np.nan, np.nan, 0.02, 0.02]}, index=idx)
    f = p2.fold_thin_days(df, min_markets=2)
    assert f["late"].iloc[:4].isna().all()
    assert f["late"].iloc[4] == pytest.approx(0.02)


def test_basket_folded_n_counts_valid_markets():
    df = _block(14)
    _, n = p2.basket_folded(df, min_markets=2)
    assert n.loc[pd.Timestamp("2024-01-08")] == 4      # Montag: alle vier Maerkte gueltig (BTC gefaltet)
    assert n.min() >= 2


def test_raises_when_never_enough_markets():
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    df = pd.DataFrame({"a": [0.01] * 5}, index=idx)
    with pytest.raises(ValueError):
        p2.fold_thin_days(df, min_markets=2)
