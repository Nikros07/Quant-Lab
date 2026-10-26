"""Hilfen für die Tests: synthetische Tageskurse mit vorgegebenen Monatsschlusskursen."""
from datetime import date, timedelta


def last_weekday(y: int, m: int) -> date:
    d = date(y + (m == 12), 1 if m == 12 else m + 1, 1) - timedelta(days=1)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def make_bars(start_year: int, start_month: int, month_closes, mid_price=None, partial_current=None):
    """Je Monat 3 Kurse (3., 15., letzter Handelstag). Der Monatsschluss ist `month_closes[i]`.

    mid_price: Kurs für 3. und 15. (Standard: gleicher wie der Monatsschluss — egal, nur der Schluss zählt).
    partial_current: Liste von Kursen für den ersten Tagen des Folgemonats (laufender Monat).
    """
    bars = []
    y, m = start_year, start_month
    for c in month_closes:
        mid = c * 0.9 if mid_price is None else mid_price
        bars += [(date(y, m, 3).isoformat(), mid), (date(y, m, 15).isoformat(), mid),
                 (last_weekday(y, m).isoformat(), float(c))]
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    if partial_current:
        for i, p in enumerate(partial_current):
            bars.append((date(y, m, 1 + i).isoformat(), float(p)))
    return bars, (y, m)
