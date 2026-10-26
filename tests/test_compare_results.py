"""Tests fuer scripts/compare_results.py. Nur synthetische Daten, kein Netz."""
from __future__ import annotations

import calendar
import importlib.util
import sys
import types
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
_SPEC = importlib.util.spec_from_file_location(
    "compare_results", ROOT / "scripts" / "compare_results.py"
)
cr = importlib.util.module_from_spec(_SPEC)
sys.modules["compare_results"] = cr
_SPEC.loader.exec_module(cr)

# Szenario: 20 Monate steigend (Jan 2020 bis Aug 2021, Kurs 100 bis 138), dann Einbruch auf 50.
MONATSKURSE = [(2020 + i // 12, i % 12 + 1, 100.0 + 2 * i) for i in range(20)]
MONATSKURSE += [(2021, 9, 50.0), (2021, 10, 50.0)]

# Von Hand gerechnet: MA12 steigender Reihe = letzter Kurs - 11. Ab Sep 2021 liegt der Kurs
# unter dem Mittel. Erwartete Signale ab dem 12. Monatsende (Dez 2020):
ERWARTET_SIGNALE = (
    [((2020, 12), "LONG")]
    + [((2021, m), "LONG") for m in range(1, 9)]
    + [((2021, 9), "FLAT"), ((2021, 10), "FLAT")]
)


def _bdays(y: int, m: int) -> pd.DatetimeIndex:
    return pd.bdate_range(
        pd.Timestamp(date(y, m, 1)), pd.Timestamp(date(y, m, calendar.monthrange(y, m)[1]))
    )


def _erster_bday(y: int, m: int) -> date:
    return pd.bdate_range(pd.Timestamp(date(y, m, 1)), periods=1)[0].date()


def _kurse(partial_nov: bool) -> pd.Series:
    rows = []
    for y, m, c in MONATSKURSE:
        rows += [(d.date(), c) for d in _bdays(y, m)]
    if partial_nov:  # laufender Monat: nur 1.-10. November, Kurs 1000
        rows += [(d.date(), 1000.0) for d in pd.bdate_range(pd.Timestamp("2021-11-01"), pd.Timestamp("2021-11-10"))]
    return pd.Series(
        [c for _, c in rows],
        index=pd.DatetimeIndex([pd.Timestamp(d) for d, _ in rows]),
        dtype=float,
    )


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def _write_prices_csv(path: Path, prices: pd.Series) -> Path:
    lines = ["Date,Close"] + [f"{ts.date().isoformat()},{c}" for ts, c in prices.items()]
    return _write(path, "\n".join(lines) + "\n")


@pytest.fixture
def ref_csv(tmp_path: Path) -> Path:
    """Referenz-CSV aus dem Szenario, erzeugt ueber die CLI (csv-Quelle, --to 31.10.2021)."""
    preis = _write_prices_csv(tmp_path / "kurse.csv", _kurse(partial_nov=True))
    out = tmp_path / "referenz.csv"
    rc = cr.main(["reference", "--source", "csv", "--csv", str(preis), "--out", str(out), "--to", "2021-10-31"])
    assert rc == 0
    return out


# ---------------------------------------------------------------- (a) Referenz

def test_referenz_signale_und_wechsel():
    rows, _ = cr.build_reference(_kurse(False), date(2020, 1, 1), None, date(2030, 1, 1))
    assert [(r["month_end"][:7], r["signal"]) for r in rows] == [
        (f"{y}-{m:02d}", s) for (y, m), s in ERWARTET_SIGNALE
    ]
    assert [r["month_end"][:7] for r in rows if r["change"]] == ["2020-12", "2021-09"]
    dec = rows[0]
    assert dec["close"] == 122.0
    assert dec["ma12"] == pytest.approx(111.0)
    assert dec["exec_date"] == "2021-01-01"
    sep = rows[-2]
    assert sep["month_end"][:7] == "2021-09" and sep["exec_date"] == "2021-10-01"


def test_laufender_monat_wird_ignoriert():
    prices = _kurse(True)
    rows, warnungen = cr.build_reference(prices, date(2020, 1, 1), None, today=date(2021, 11, 15))
    assert len(rows) == 11
    assert rows[-1]["month_end"][:7] == "2021-10"
    # Erst nach Monatsende zaehlt November als vollstaendig: Kurs 1000 -> LONG, also Wechsel.
    rows2, warnungen2 = cr.build_reference(prices, date(2020, 1, 1), None, today=date(2021, 12, 1))
    assert rows2[-1]["month_end"][:7] == "2021-11"
    assert rows2[-1]["signal"] == "LONG" and rows2[-1]["change"] is True
    assert any("2021-11" in w for w in warnungen2)  # Daten enden am 10.11., Warnung
    assert warnungen == []  # Oktober endet am 29.10., keine Warnung; November ist gar nicht enthalten


def test_bis_datum_schneidet_monate_ab():
    rows, _ = cr.build_reference(_kurse(True), date(2020, 1, 1), date(2021, 10, 31), today=date(2030, 1, 1))
    assert len(rows) == 11


def test_reference_cli_schreibt_csv(ref_csv):
    df = pd.read_csv(ref_csv, dtype=str, keep_default_na=False)
    assert list(df.columns) == cr.REF_SPALTEN
    assert len(df) == 11
    assert df["month_end"].iloc[0] == "2020-12-31"
    assert df["change"].tolist().count("True") == 2


# ---------------------------------------------------------------- (b) compare-mt5

EA_HEADER = "date;symbol;month_close;ma;signal;action"


def _ea_zeilen(buy: bool = True, close: bool = True, extra: tuple[str, ...] = ()) -> list[str]:
    """Log, das exakt der Referenz entspricht: Zeile am Ausfuehrungstag, Signal = Monatsende des Vormonats."""
    zeilen = []
    for (y, m), sig in ERWARTET_SIGNALE:
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        datum = _erster_bday(ny, nm).strftime("%Y.%m.%d")
        aktion = ""
        if (y, m) == (2020, 12) and buy:
            aktion = "BUY"
        if (y, m) == (2021, 9) and close:
            aktion = "CLOSE"
        zeilen.append(f"{datum};SPY;;;{sig};{aktion}")
    return zeilen + list(extra)


def _log(tmp_path: Path, zeilen: list[str]) -> Path:
    return _write(tmp_path / "ea_log.csv", "\n".join([EA_HEADER] + zeilen) + "\n")


def test_mt5_exakt_referenz_ergibt_100_prozent(ref_csv, tmp_path, capsys):
    log = _log(tmp_path, _ea_zeilen())
    rc = cr.main(["compare-mt5", "--log", str(log), "--reference", str(ref_csv)])
    out = capsys.readouterr().out
    assert rc == 0, out
    assert "ÜBEREINSTIMMUNG: 100.0 %" in out


def test_mt5_fehlender_wechsel_ergibt_unter_100_und_exit_1(ref_csv, tmp_path, capsys):
    log = _log(tmp_path, _ea_zeilen(buy=False))  # BUY zum 2021-01-01 fehlt
    rc = cr.main(["compare-mt5", "--log", str(log), "--reference", str(ref_csv)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "fehlend:  1" in out
    assert "2021-01-01" in out  # fehlender Wechsel mit Datum
    # Basis: (1 gefunden + 11 Signale ok) / (2 Wechsel + 0 zusaetzlich + 11 Signale geprueft)
    assert "ÜBEREINSTIMMUNG: 92.3 %" in out


def test_mt5_zusaetzliche_aktion_ergibt_exit_1(ref_csv, tmp_path, capsys):
    log = _log(tmp_path, _ea_zeilen(extra=("2021.03.15;SPY;;;LONG;CLOSE",)))
    rc = cr.main(["compare-mt5", "--log", str(log), "--reference", str(ref_csv)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "Zusätzliche EA-Aktionen ohne Referenz: 1" in out


def test_mt5_signalabweichung_mit_abstand(ref_csv, tmp_path, capsys):
    # EA meldet am 01.02.2021 FLAT, Referenz (Monatsende Jan 2021) ist LONG.
    zeilen = [z if not z.startswith("2021.02.01") else "2021.02.01;SPY;124,0;113,0;FLAT;" for z in _ea_zeilen()]
    log = _log(tmp_path, zeilen)
    rc = cr.main(["compare-mt5", "--log", str(log), "--reference", str(ref_csv)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "Signal-Abweichungen: 1 " in out
    assert "2021-02-01 Zeile" in out and "EA FLAT, Referenz LONG" in out
    assert "Abstand close/ma" in out and "EA +9.73 %" in out  # 124/113 - 1 aus der Logzeile


# ---------------------------------------------------------------- (c) compare-tv

TV_FORMAT_A = (  # eine Zeile pro Trade, deutsche Namen, Semikolon, Dezimalkomma, mit UTF-8-BOM
    "﻿Nr;Einstiegsdatum;Einstiegspreis;Ausstiegsdatum;Ausstiegspreis\n"
    "1;2021-01-01 00:00;100,0;2021-10-01 00:00;50,0\n"
)
TV_FORMAT_B = (  # zwei Zeilen pro Trade, englische Namen, Komma
    "Trade #,Type,Date and time,Signal,Price USD\n"
    "1,Entry long,01.01.2021 00:00,Long,100.0\n"
    "1,Exit long,01.10.2021 00:00,Exit long,50.0\n"
)


@pytest.mark.parametrize("inhalt, fmt", [(TV_FORMAT_A, "A"), (TV_FORMAT_B, "B")])
def test_tv_beide_formate_ergeben_100_prozent(ref_csv, tmp_path, capsys, inhalt, fmt):
    trades = _write(tmp_path / f"trades_{fmt}.csv", inhalt)
    rc = cr.main(["compare-tv", "--trades", str(trades), "--reference", str(ref_csv)])
    out = capsys.readouterr().out
    assert rc == 0, out
    assert f"Format {fmt}" in out
    assert "ÜBEREINSTIMMUNG: 100.0 %" in out


def test_tv_offener_trade_ohne_ausstieg_ist_abweichung(ref_csv, tmp_path, capsys):
    trades = _write(
        tmp_path / "trades_offen.csv",
        "Trade #,Type,Date and time,Signal,Price USD\n1,Entry long,01.01.2021 00:00,Long,100.0\n",
    )
    rc = cr.main(["compare-tv", "--trades", str(trades), "--reference", str(ref_csv)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "2021-10-01" in out
    assert "ÜBEREINSTIMMUNG: 50.0 %" in out


# ---------------------------------------------------------------- (d) unbekannte Spalten

def test_tv_unbekannte_spalten_geben_klare_fehlermeldung(ref_csv, tmp_path, capsys):
    trades = _write(tmp_path / "trades_kaputt.csv", "Foo;Bar;Baz\n1;2;3\n")
    rc = cr.main(["compare-tv", "--trades", str(trades), "--reference", str(ref_csv)])
    err = capsys.readouterr().err
    assert rc == 2
    assert "nicht erkannt" in err
    assert "Foo, Bar, Baz" in err


# ---------------------------------------------------------------- Yahoo-Pfad ohne Netz

def test_yahoo_pfad_mit_gefaelschtem_yfinance(monkeypatch):
    """Prueft Aufruf und Zeitzonen-Behandlung von load_prices_yahoo, ohne Netz."""

    class FakeTicker:
        def __init__(self, symbol):
            self.symbol = symbol

        def history(self, start, end, auto_adjust):
            assert self.symbol == "SPY"
            assert start == "2020-01-01" and end == "2021-10-02"  # yfinance: Ende exklusiv
            assert auto_adjust is False
            idx = pd.bdate_range("2021-09-29", periods=3, tz="America/New_York")
            return pd.DataFrame({"Close": [1.0, 2.0, 3.0], "Dividends": [0.0, 0.0, 0.0]}, index=idx)

    fake = types.ModuleType("yfinance")
    fake.Ticker = FakeTicker
    monkeypatch.setitem(sys.modules, "yfinance", fake)
    s = cr.load_prices_yahoo("SPY", date(2020, 1, 1), date(2021, 10, 1))
    assert [d.date() for d in s.index] == [date(2021, 9, 29), date(2021, 9, 30), date(2021, 10, 1)]
    assert list(s.values) == [1.0, 2.0, 3.0]


# ---------------------------------------------------------------- Hilfsfunktionen

@pytest.mark.parametrize(
    "text", ["2021-01-01", "2021.01.01", "01.01.2021", "2021-01-01T00:00:00-05:00", "2021.01.01 00:00"]
)
def test_datumsparser_akzeptiert_erlaubte_formate(text):
    assert cr.parse_date(text) == date(2021, 1, 1)


def test_datumsparser_lehnt_anderes_format_ab():
    with pytest.raises(ValueError):
        cr.parse_date("2021/01/01")


def test_toleranzfenster():
    wechsel = [cr.RefChange(date(2020, 12, 31), cr.LONG, date(2021, 1, 1))]
    spaet = [cr.Event(date(2021, 1, 6), cr.LONG, "BUY", 1)]  # 5 Tage nach exec
    assert len(cr.match_events(wechsel, spaet, 5)[0]) == 1
    found, missing, extra = cr.match_events(wechsel, spaet, 4)
    assert len(missing) == 1 and len(extra) == 1
    zwei_vorher = [cr.Event(date(2020, 12, 30), cr.LONG, "BUY", 1)]  # 2 Tage vor exec: erlaubt
    assert len(cr.match_events(wechsel, zwei_vorher, 0)[0]) == 1
    drei_vorher = [cr.Event(date(2020, 12, 29), cr.LONG, "BUY", 1)]  # 3 Tage vor exec: nicht erlaubt
    assert len(cr.match_events(wechsel, drei_vorher, 0)[0]) == 0
