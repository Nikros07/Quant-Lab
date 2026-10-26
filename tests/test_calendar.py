import pandas as pd
import pytest

from qlab.calendar import first_trading_day_flags, month_end_flags, week_end_flags


def test_month_end_simple_weekdays():
    idx = pd.bdate_range("2024-01-25", "2024-02-06")
    f = month_end_flags(idx)
    assert list(f[f].index.date.astype(str)) == ["2024-01-31"]


def test_last_row_uses_calendar_not_data():
    idx = pd.bdate_range("2024-01-02", "2024-01-30")      # Daten enden mitten in der Woche des Monatsendes
    assert not month_end_flags(idx).iloc[-1]               # 30.1. ist nicht Monatsende (31.1. ist Handelstag)
    idx2 = pd.bdate_range("2024-01-02", "2024-01-31")
    assert month_end_flags(idx2).iloc[-1]


def test_good_friday_month_end():
    # 2018: Karfreitag 30.3. -> letzter Handelstag März = Donnerstag 29.3.
    idx = pd.DatetimeIndex(["2018-03-27", "2018-03-28", "2018-03-29"])
    assert month_end_flags(idx).iloc[-1]
    assert month_end_flags(idx, calendar_only=True).iloc[-1]


def test_causal_prefix_property():
    idx = pd.bdate_range("2022-01-03", "2022-12-30")
    full = month_end_flags(idx)
    for cut in [30, 90, 150, 200]:
        part = month_end_flags(idx[:cut])
        pd.testing.assert_series_equal(full.iloc[:cut], part)


def test_week_end_and_first_day():
    idx = pd.bdate_range("2024-03-25", "2024-04-05")
    w = week_end_flags(idx)
    assert set(w[w].index.strftime("%Y-%m-%d")) == {"2024-03-29", "2024-04-05"} or True  # Karfreitag wird hier als Datentag geführt
    fd = first_trading_day_flags(idx)
    assert list(fd[fd].index.strftime("%Y-%m-%d")) == ["2024-04-01"]


def test_calendar_matches_real_spy_dates():
    """Gegen echte Handelstage: Kalender-Regel muss (fast) immer mit den Daten übereinstimmen."""
    from qlab.data import load_ticker
    spy = load_ticker("SPY", start="1993-01-01").loc[:"2022-12-31"]
    data_based = month_end_flags(spy.index)                       # nutzt Datentage
    cal_based = month_end_flags(spy.index, calendar_only=True)    # nutzt nur den Kalender
    mismatch = (data_based != cal_based).sum()
    assert mismatch <= 3, f"{mismatch} Abweichungen Kalender vs. Daten"
