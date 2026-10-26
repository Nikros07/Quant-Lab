"""Kausal korrekte Kalender-Helfer (Monatsende, Wochenende, Monatsanfang).

Falle: "Letzter Handelstag des Monats" aus den Daten abzuleiten (groupby(...).max()) ist ein
versteckter Blick in die Zukunft — ob ein Tag der letzte war, weiß man erst am Folgetag. Auf
abgeschnittenen Daten (Live-Betrieb, check_causality) wird dann der letzte Datentag fälschlich als
Monatsende erkannt. Diese Helfer entscheiden für jeden Tag außer dem letzten mit dem nächsten
Datentag (das ist Vergangenheit, wenn man später rechnet — aber für Tag t nutzen wir nur, ob der
NÄCHSTE NYSE-Handelstag im anderen Monat liegt), und nutzen dafür einen NYSE-Kalender statt
der Daten.
"""
from __future__ import annotations

import pandas as pd
from pandas.tseries.holiday import (AbstractHolidayCalendar, GoodFriday, Holiday, USLaborDay,
                                    USMartinLutherKingJr, USMemorialDay, USPresidentsDay,
                                    USThanksgivingDay, nearest_workday)
from pandas.tseries.offsets import CustomBusinessDay

# Einmalige Schließungen der NYSE (ohne reguläre Feiertage)
_SPECIAL_CLOSURES = [
    "2001-09-11", "2001-09-12", "2001-09-13", "2001-09-14",   # 9/11
    "2004-06-11",                                              # Reagan
    "2007-01-02",                                              # Ford
    "2012-10-29", "2012-10-30",                                # Hurricane Sandy
    "2018-12-05",                                              # Bush senior
    "2025-01-09",                                              # Carter
]


class NYSECalendar(AbstractHolidayCalendar):
    rules = [
        USMartinLutherKingJr, USPresidentsDay, GoodFriday, USMemorialDay,
        Holiday("Juneteenth", month=6, day=19, start_date="2022-01-01", observance=nearest_workday),
        Holiday("July4", month=7, day=4, observance=nearest_workday),
        USLaborDay, USThanksgivingDay,
        Holiday("Christmas", month=12, day=25, observance=nearest_workday),
    ]


def _new_year_closures() -> list[pd.Timestamp]:
    """1. Januar: Sonntag -> Montag geschlossen; Samstag -> KEIN Ersatztag (NYSE-Regel)."""
    out = []
    for y in range(1990, 2036):
        d = pd.Timestamp(year=y, month=1, day=1)
        if d.weekday() == 6:
            out.append(d + pd.Timedelta(days=1))
        elif d.weekday() < 5:
            out.append(d)
    return out


_HOLIDAYS = (list(NYSECalendar().holidays(start="1990-01-01", end="2035-12-31"))
             + _new_year_closures() + [pd.Timestamp(d) for d in _SPECIAL_CLOSURES])
NYSE_BDAY = CustomBusinessDay(holidays=_HOLIDAYS)


def _next_trading_day(d: pd.Timestamp) -> pd.Timestamp:
    return d + NYSE_BDAY


def month_end_flags(index: pd.DatetimeIndex, calendar_only: bool = False) -> pd.Series:
    """True an Tagen, die der letzte Handelstag ihres Monats sind (kausal).

    Für alle Zeilen außer der letzten entscheidet der nächste *Datentag*; für die letzte Zeile der
    NYSE-Kalender. `calendar_only=True` nutzt für alle Zeilen den Kalender (zum Testen).
    """
    idx = pd.DatetimeIndex(index)
    n = len(idx)
    out = []
    for i, d in enumerate(idx):
        if calendar_only or i == n - 1:
            nxt = _next_trading_day(d)
        else:
            nxt = idx[i + 1]
        out.append(nxt.month != d.month)
    return pd.Series(out, index=idx)


def month_end_dates(index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    f = month_end_flags(index)
    return f.index[f.to_numpy()]


def week_end_flags(index: pd.DatetimeIndex) -> pd.Series:
    """Letzter Handelstag der Kalenderwoche (kausal, gleiche Logik)."""
    idx = pd.DatetimeIndex(index)
    n = len(idx)
    out = []
    for i, d in enumerate(idx):
        nxt = _next_trading_day(d) if i == n - 1 else idx[i + 1]
        out.append(nxt.isocalendar().week != d.isocalendar().week or nxt.year != d.year)
    return pd.Series(out, index=idx)


def first_trading_day_flags(index: pd.DatetimeIndex) -> pd.Series:
    """Erster Handelstag des Monats — kausal, weil nur der Vortag verglichen wird."""
    idx = pd.DatetimeIndex(index)
    prev_month = pd.Series(idx.month, index=idx).shift(1)
    return pd.Series(idx.month != prev_month.to_numpy(), index=idx) & (pd.Series(range(len(idx)), index=idx) > 0)
