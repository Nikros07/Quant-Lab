from datetime import date

import pytest

from tests.helpers import make_bars
from trendbot.signal import DataError, decide, month_closes


def rising(n=14, start=100.0, step=2.0):
    return [start + step * i for i in range(n)]


def test_uptrend_is_on_and_ma_is_mean_of_last_12_month_ends():
    closes = rising(14)
    bars, (y, m) = make_bars(2025, 1, closes)
    s = decide(bars, date(y, m, 5))
    assert s.on is True
    assert s.ma == pytest.approx(sum(closes[-12:]) / 12)
    assert s.last_close == closes[-1]
    assert s.month == "2026-02"
    assert len(s.closes) == 12


def test_drop_below_average_is_off():
    closes = rising(13) + [90.0]          # letzter Monat bricht deutlich ein
    bars, (y, m) = make_bars(2025, 1, closes)
    s = decide(bars, date(y, m, 5))
    assert s.on is False
    assert s.distance < 0


def test_equal_to_ma_counts_as_on():
    # 12 Monate, letzter = Durchschnitt aller 12 -> P >= MA
    base = [100.0] * 11
    last = (sum(base) + 100.0) / 12
    bars, (y, m) = make_bars(2025, 1, base + [last])
    assert decide(bars, date(y, m, 2)).on is True


def test_current_month_never_counts_even_with_extreme_prices():
    closes = rising(14)
    bars, (y, m) = make_bars(2025, 1, closes, partial_current=[1.0, 1.0, 1.0])
    s_low = decide(bars, date(y, m, 4))
    bars2, _ = make_bars(2025, 1, closes, partial_current=[1e6, 1e6, 1e6])
    s_high = decide(bars2, date(y, m, 4))
    assert s_low.on == s_high.on is True
    assert s_low.ma == s_high.ma and s_low.last_close == s_high.last_close


def test_rule_flips_only_at_month_boundary():
    closes = rising(13) + [90.0]
    bars, (y, m) = make_bars(2025, 1, closes)
    a = decide(bars, date(y, m, 2))
    b = decide(bars, date(y, m, 27))        # später im selben Monat: gleiches Ergebnis
    assert (a.on, a.ma, a.last_close) == (b.on, b.ma, b.last_close)


def test_too_few_months_raises():
    bars, (y, m) = make_bars(2025, 6, rising(8))
    with pytest.raises(DataError):
        decide(bars, date(y, m, 5))


def test_missing_month_raises():
    bars, (y, m) = make_bars(2025, 1, rising(14))
    bars = [b for b in bars if not b[0].startswith("2025-09")]    # September fehlt komplett
    with pytest.raises(DataError):
        decide(bars, date(y, m, 5))


def test_stale_data_last_completed_month_missing_raises():
    bars, (y, m) = make_bars(2025, 1, rising(14))
    with pytest.raises(DataError):
        decide(bars, date(y + (m == 12), (m % 12) + 1, 5))        # heute 1 Monat später, Daten enden früher


def test_month_with_stale_last_bar_raises():
    bars, (y, m) = make_bars(2025, 1, rising(14))
    # im Dezember 2025 gibt es nur Kurse bis zum 10.: 'letzter Kurs' wäre kein Monatsende
    bars = [b for b in bars if not (b[0].startswith("2025-12") and b[0] > "2025-12-15")]
    with pytest.raises(DataError):
        decide(bars, date(y, m, 5))


def test_unsorted_or_duplicate_dates_raise():
    bars, (y, m) = make_bars(2025, 1, rising(14))
    bars2 = bars[:5] + [bars[3]] + bars[5:]
    with pytest.raises(DataError):
        decide(bars2, date(y, m, 5))


def test_invalid_price_raises():
    bars, (y, m) = make_bars(2025, 1, rising(14))
    bars[10] = (bars[10][0], -5.0)
    with pytest.raises(DataError):
        decide(bars, date(y, m, 5))


def test_year_boundary_months_ok():
    bars, (y, m) = make_bars(2024, 11, rising(14))
    s = decide(bars, date(y, m, 3))
    assert s.month == "2025-12"
    assert len(s.closes) == 12


def test_month_closes_excludes_current_month_and_orders():
    bars, (y, m) = make_bars(2025, 1, rising(3), partial_current=[50.0])
    out = month_closes(bars, date(y, m, 2))
    assert [x[0] for x in out] == ["2025-01", "2025-02", "2025-03"]


def test_custom_ma_length():
    closes = rising(14)
    bars, (y, m) = make_bars(2025, 1, closes)
    s = decide(bars, date(y, m, 5), ma_months=10)
    assert s.ma == pytest.approx(sum(closes[-10:]) / 10)
