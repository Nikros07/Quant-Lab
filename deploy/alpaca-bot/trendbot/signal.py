"""Signal des monatlichen Trendfilters (reines Python, keine Zusatzpakete).

Regel (identisch zum getesteten Quant-Lab-Backtest `trend_ma12_us_equity_cash`):
    P  = Schlusskurs des letzten ABGESCHLOSSENEN Monats
    MA = Mittel der letzten `ma_months` abgeschlossenen Monatsschlusskurse (inkl. P)
    P >= MA -> investiert (on=True), sonst Cash (on=False)

Zustandsbasiert: Das Ergebnis ändert sich nur an Monatsgrenzen. Der laufende, noch nicht abgeschlossene
Monat wird NIE verwendet (kein Blick in die Zukunft, kein Rauschen durch Tageskurse).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


class DataError(Exception):
    """Kursdaten unvollständig oder unplausibel — dann wird NICHT gehandelt."""


@dataclass(frozen=True)
class Signal:
    on: bool
    month: str            # 'YYYY-MM' des letzten abgeschlossenen Monats
    last_close: float
    ma: float
    distance: float       # last_close / ma - 1
    ma_months: int
    closes: tuple         # ((monat, schluss), ...) die in den Durchschnitt eingingen

    def describe(self) -> str:
        return (f"Monatsschluss {self.month}: {self.last_close:.2f} "
                f"{'>=' if self.on else '<'} MA{self.ma_months} {self.ma:.2f} "
                f"({self.distance * 100:+.2f} %) -> {'INVESTIERT' if self.on else 'CASH'}")


def _parse(d) -> date:
    if isinstance(d, date):
        return d
    return date.fromisoformat(str(d)[:10])


def month_closes(bars, today) -> list[tuple[str, float, date]]:
    """Letzter Schlusskurs je Kalendermonat, ohne den Monat von `today`.

    bars: Iterable aus (Datum, Schlusskurs), aufsteigend sortiert.
    Rückgabe: [(YYYY-MM, close, datum_des_letzten_kurses), ...].
    """
    today = _parse(today)
    cur = (today.year, today.month)
    last: dict[tuple[int, int], tuple[float, date]] = {}
    prev = None
    for d, c in bars:
        d = _parse(d)
        c = float(c)
        if prev is not None and d <= prev:
            raise DataError(f"Kursdaten nicht streng aufsteigend sortiert bei {d}")
        prev = d
        if c <= 0 or c != c:
            raise DataError(f"Unplausibler Kurs {c} am {d}")
        key = (d.year, d.month)
        if key >= cur:
            continue                      # laufender (oder zukünftiger) Monat zählt nicht
        last[key] = (c, d)
    return [(f"{y:04d}-{m:02d}", c, d) for (y, m), (c, d) in sorted(last.items())]


def _next_month(y: int, m: int) -> tuple[int, int]:
    return (y + 1, 1) if m == 12 else (y, m + 1)


def decide(bars, today, ma_months: int = 12) -> Signal:
    """Berechnet das Signal. Wirft DataError, wenn die Daten nicht ausreichen oder Lücken haben."""
    if ma_months < 2:
        raise ValueError("ma_months muss >= 2 sein")
    mc = month_closes(bars, today)
    if len(mc) < ma_months:
        raise DataError(f"Nur {len(mc)} abgeschlossene Monate, {ma_months} nötig")
    window = mc[-ma_months:]
    # lückenlos aufeinanderfolgende Monate
    y, m = int(window[0][0][:4]), int(window[0][0][5:7])
    for label, _, _ in window:
        if label != f"{y:04d}-{m:02d}":
            raise DataError(f"Monat fehlt in den Kursdaten: erwartet {y:04d}-{m:02d}, gefunden {label}")
        y, m = _next_month(y, m)
    # der letzte abgeschlossene Monat muss direkt vor dem aktuellen liegen
    t = _parse(today)
    if (y, m) != (t.year, t.month):
        raise DataError(f"Neuester abgeschlossener Monat ist {window[-1][0]}, erwartet vor {t.year:04d}-{t.month:02d}")
    # jeder Monatsschluss muss wirklich vom Monatsende stammen (kein veralteter Datenstand)
    for label, _, d in window:
        if d.day < 24:
            raise DataError(f"Monat {label}: letzter Kurs erst am {d} — Daten unvollständig")
    closes = tuple((label, c) for label, c, _ in window)
    last_close = closes[-1][1]
    ma = sum(c for _, c in closes) / ma_months
    return Signal(on=last_close >= ma, month=closes[-1][0], last_close=last_close, ma=ma,
                  distance=last_close / ma - 1.0, ma_months=ma_months, closes=closes)
