"""Abgleich der MA12-Monatsend-Trendstrategie: Referenz gegen MT5-EA-Log und TradingView-Trades.

Regel der Referenz: Am letzten Handelstag eines vollständigen Kalendermonats LONG, wenn der
Monatsschlusskurs >= Mittel der letzten 12 Monatsschlusskurse (inkl. aktuellem) ist, sonst FLAT.
Ausgeführt wird am nächsten Handelstag (exec_date).

Befehle:
  reference    Referenz-CSV aus Tageskursen erzeugen (Yahoo oder CSV-Datei)
  compare-mt5  EA-Log (Trenner ';') mit der Referenz abgleichen
  compare-tv   TradingView-Export "Liste der Trades" mit der Referenz abgleichen

Exit-Code: 0 = 100 % Uebereinstimmung, 1 = Abweichungen (oder nichts zu vergleichen),
2 = Eingabe- oder Datenfehler.
"""
from __future__ import annotations

import argparse
import bisect
import calendar
import codecs
import csv
import io
import math
import re
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

MA_MONATE = 12
FRUEH_TOLERANZ_TAGE = 2  # eine Aktion darf bis 2 Tage VOR exec_date liegen
DEFAULT_FROM = "2012-01-01"
DEFAULT_TO = "2026-10-01"
LONG = "LONG"
FLAT = "FLAT"
SHORT = "SHORT"  # nur TradingView: Short-Trade, passt zu keiner Referenz
REF_SPALTEN = ["month_end", "close", "ma12", "signal", "exec_date", "change"]


# ---------------------------------------------------------------- Datum und Zahlen

_ISO_RE = re.compile(r"^\s*(\d{4})[-.](\d{1,2})[-.](\d{1,2})(?=$|[T\s])")
_DE_RE = re.compile(r"^\s*(\d{1,2})\.(\d{1,2})\.(\d{4})(?=$|[T\s])")


def parse_date(text: str) -> date:
    """YYYY-MM-DD, YYYY.MM.DD, DD.MM.YYYY. ISO-Zeitstempel: nur der Datumsteil wird genommen."""
    s = str(text).strip()
    m = _ISO_RE.match(s)
    if m:
        y, mo, d = (int(x) for x in m.groups())
    else:
        m = _DE_RE.match(s)
        if not m:
            raise ValueError(
                f"Datum nicht lesbar: {text!r} (erlaubt: YYYY-MM-DD, YYYY.MM.DD, DD.MM.YYYY)"
            )
        d, mo, y = (int(x) for x in m.groups())
    try:
        return date(y, mo, d)
    except ValueError as exc:
        raise ValueError(f"Datum ungültig: {text!r}") from exc


def parse_number(text: str | None) -> float | None:
    """Zahl mit Punkt oder Komma als Dezimaltrenner. Leer ergibt None."""
    if text is None:
        return None
    s = str(text).strip()
    if not s:
        return None
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):  # deutsch: 1.234,5
            s = s.replace(".", "").replace(",", ".")
        else:  # englisch: 1,234.5
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        raise ValueError(f"Zahl nicht lesbar: {text!r}") from None


def _opt_number(text: str | None) -> float | None:
    try:
        return parse_number(text)
    except ValueError:
        return None


def _norm_signal(text: str | None) -> str | None:
    s = str(text or "").strip().upper()
    return s if s in (LONG, FLAT) else None


def _monatsende(ym: tuple[int, int]) -> date:
    return date(ym[0], ym[1], calendar.monthrange(ym[0], ym[1])[1])


def _monate_zwischen(a: tuple[int, int], b: tuple[int, int]) -> list[tuple[int, int]]:
    out = []
    y, m = a
    while (y, m) <= b:
        out.append((y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


# ---------------------------------------------------------------- Dateien einlesen

def read_text(path: Path) -> str:
    roh = path.read_bytes()
    if roh.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        return roh.decode("utf-16")
    try:
        return roh.decode("utf-8-sig")
    except UnicodeDecodeError:
        return roh.decode("cp1252", errors="replace")


def read_table(path: Path) -> tuple[list[str], list[tuple[int, dict[str, str]]]]:
    """Liest eine CSV mit Trenner ',' oder ';' (aus der Kopfzeile erkannt).

    Gibt (Kopfzeilen, [(Zeilennummer, {Spalte: Wert}), ...]) zurueck.
    """
    text = read_text(path)
    kopf = next((line for line in text.splitlines() if line.strip()), "")
    if not kopf:
        raise ValueError(f"Datei ist leer: {path.name}")
    delim = ";" if kopf.count(";") > kopf.count(",") else ","
    reader = csv.reader(io.StringIO(text), delimiter=delim)
    rows: list[tuple[int, list[str]]] = []
    for cells in reader:
        if any(c.strip() for c in cells):
            rows.append((reader.line_num, [c.strip() for c in cells]))
    header = rows[0][1]
    records = []
    for no, cells in rows[1:]:
        cells = cells + [""] * (len(header) - len(cells))
        records.append((no, dict(zip(header, cells))))
    return header, records


def _require_file(p: str | Path) -> Path:
    path = Path(p)
    if not path.is_file():
        raise ValueError(f"Datei nicht gefunden: {p}")
    return path


def _colmap(header: list[str], benoetigt: tuple[str, ...], datei: str) -> dict[str, str]:
    low = {h.lower(): h for h in header}
    fehlt = [n for n in benoetigt if n not in low]
    if fehlt:
        raise ValueError(
            f"{datei}: Spalte(n) {', '.join(fehlt)} fehlen. Gefunden: {', '.join(header)}"
        )
    return {n: low[n] for n in benoetigt}


def _zelle(rec: dict[str, str], col: str | None) -> str:
    return rec.get(col, "") if col else ""


# ---------------------------------------------------------------- Datenklassen

@dataclass(frozen=True)
class RefRow:
    month_end: date
    close: float | None
    ma12: float | None
    signal: str
    exec_date: date | None
    change: bool


@dataclass(frozen=True)
class LogRow:
    zeile: int
    datum: date
    signal: str | None
    aktion: str
    month_close: float | None
    ma: float | None


@dataclass(frozen=True)
class Event:
    """Eine Handelsaktion aus EA-Log (BUY/CLOSE) oder TradingView (Entry/Exit)."""
    datum: date
    kind: str  # LONG = Einstieg, FLAT = Ausstieg, SHORT = passt nie zur Referenz
    text: str
    zeile: int
    preis: float | None = None


@dataclass(frozen=True)
class RefChange:
    month_end: date
    kind: str
    exec_date: date | None


@dataclass
class SignalStats:
    geprueft: int = 0
    ok: int = 0
    ohne_ref: int = 0
    ohne_signal: int = 0
    abweichungen: list = field(default_factory=list)  # Liste aus (LogRow, RefRow)


# ---------------------------------------------------------------- Referenz

def load_prices_csv(path: Path) -> pd.Series:
    header, recs = read_table(path)
    low = {h.lower(): h for h in header}
    dcol = next((low[k] for k in ("date", "datum") if k in low), None)
    if dcol is None:
        dcol = next((h for h in header if "date" in h.lower() or "datum" in h.lower()), None)
    ccol = next((low[k] for k in ("close", "schlusskurs") if k in low), None)
    if ccol is None:
        ccol = next(
            (h for h in header
             if ("close" in h.lower() or "schluss" in h.lower()) and "adj" not in h.lower()),
            None,
        )
    if dcol is None or ccol is None:
        raise ValueError(
            f"Spalten in {path.name} nicht erkannt. Gefunden: {', '.join(header)}. "
            "Erwartet: 'date' und 'close' (z. B. Date,Close)."
        )
    dates, closes = [], []
    for no, rec in recs:
        try:
            c = parse_number(rec[ccol])
            if c is None:
                continue
            dates.append(pd.Timestamp(parse_date(rec[dcol])))
        except ValueError as exc:
            raise ValueError(f"{path.name}, Zeile {no}: {exc}") from None
        closes.append(c)
    if not closes:
        raise ValueError(f"{path.name} enthält keine Kurszeilen.")
    s = pd.Series(closes, index=pd.DatetimeIndex(dates), dtype=float).sort_index()
    if s.index.has_duplicates:
        dup = s.index[s.index.duplicated()][0].date()
        raise ValueError(f"{path.name}: doppeltes Datum {dup}.")
    return s


def load_prices_yahoo(symbol: str, start: date, end: date) -> pd.Series:
    try:
        import yfinance as yf
    except ImportError as exc:
        raise ValueError("yfinance ist nicht installiert.") from exc
    try:
        hist = yf.Ticker(symbol).history(
            start=start.isoformat(),
            end=(end + timedelta(days=1)).isoformat(),  # yfinance: Ende exklusiv
            auto_adjust=False,
        )
    except Exception as exc:  # Netz- oder Yahoo-Fehler
        raise ValueError(f"Yahoo-Abruf für {symbol} fehlgeschlagen: {exc}") from exc
    if hist is None or hist.empty or "Close" not in hist.columns:
        raise ValueError(f"Keine Kursdaten für {symbol} von Yahoo erhalten (Symbol oder Netz prüfen).")
    idx = pd.DatetimeIndex(pd.to_datetime(hist.index))
    if idx.tz is not None:
        idx = idx.tz_localize(None)
    s = pd.Series(hist["Close"].astype(float).to_numpy(), index=idx.normalize()).dropna()
    return s.sort_index()


def build_reference(
    prices: pd.Series, start: date, end: date | None, today: date
) -> tuple[list[dict], list[str]]:
    """Monatsend-Signale ab dem 12. Monatsende.

    prices: Tageskurse, DatetimeIndex, sortiert. Monate zaehlen nur, wenn ihr Kalendermonatsende
    vor `today` und nicht nach `end` liegt (laufender Monat wird ignoriert). exec_date ist der
    erste Handelstag nach dem Monatsende in den vollen Kursdaten.
    """
    warnungen: list[str] = []
    alle = [(ts.date(), float(c)) for ts, c in prices.items()]
    handelstage = [d for d, _ in alle]

    letzter: dict[tuple[int, int], tuple[date, float]] = {}
    for d, c in alle:
        if d < start or (end is not None and d > end):
            continue
        letzter[(d.year, d.month)] = (d, c)  # sortiert: letzter Handelstag gewinnt
    if not letzter:
        raise ValueError("Keine Kurse im gewählten Zeitraum.")

    vollstaendig = []
    for ym in sorted(letzter):
        if _monatsende(ym) >= today or (end is not None and _monatsende(ym) > end):
            continue
        vollstaendig.append(ym)
    if not vollstaendig:
        raise ValueError("Kein vollständiger Kalendermonat im Zeitraum.")

    for ym in _monate_zwischen(vollstaendig[0], vollstaendig[-1]):
        if ym not in letzter:
            raise ValueError(
                f"Datenlücke: kein Handelstag im Monat {ym[0]}-{ym[1]:02d}. "
                "Ohne diesen Monat stimmt der MA12 nicht."
            )

    closes = [letzter[ym][1] for ym in vollstaendig]
    rows: list[dict] = []
    prev: str | None = None
    for i, ym in enumerate(vollstaendig):
        d, c = letzter[ym]
        rest = (_monatsende(ym) - d).days
        if rest > 4:
            warnungen.append(
                f"{ym[0]}-{ym[1]:02d}: letzter Handelstag {d} liegt {rest} Tage vor "
                "Monatsende - Daten evtl. unvollständig."
            )
        if i < MA_MONATE - 1:
            continue
        ma = sum(closes[i - MA_MONATE + 1 : i + 1]) / MA_MONATE
        sig = LONG if c >= ma else FLAT
        change = (sig == LONG) if prev is None else (sig != prev)
        prev = sig
        pos = bisect.bisect_right(handelstage, d)
        ausf = handelstage[pos] if pos < len(handelstage) else None
        rows.append({
            "month_end": d.isoformat(),
            "close": round(c, 6),
            "ma12": round(ma, 6),
            "signal": sig,
            "exec_date": ausf.isoformat() if ausf else "",
            "change": change,
        })
    return rows, warnungen


def load_reference(path: Path) -> list[RefRow]:
    header, recs = read_table(path)
    datei = f"Referenz {path.name}"
    sp = _colmap(header, ("month_end", "signal", "change", "exec_date"), datei)
    low = {h.lower(): h for h in header}
    rows = []
    for no, rec in recs:
        try:
            roh_sig = rec[sp["signal"]]
            sig = _norm_signal(roh_sig)
            if sig is None:
                raise ValueError(f"Signal {roh_sig!r} ist weder LONG noch FLAT")
            roh_exec = rec[sp["exec_date"]].strip()
            rows.append(RefRow(
                month_end=parse_date(rec[sp["month_end"]]),
                close=_opt_number(_zelle(rec, low.get("close"))),
                ma12=_opt_number(_zelle(rec, low.get("ma12"))),
                signal=sig,
                exec_date=parse_date(roh_exec) if roh_exec else None,
                change=rec[sp["change"]].strip().lower() in ("true", "1", "yes", "ja"),
            ))
        except ValueError as exc:
            raise ValueError(f"{datei}, Zeile {no}: {exc}") from None
    if not rows:
        raise ValueError(f"{datei} enthält keine Monatsenden.")
    return sorted(rows, key=lambda r: r.month_end)


# ---------------------------------------------------------------- EA-Log und TradingView

def load_ea_log(path: Path) -> list[LogRow]:
    header, recs = read_table(path)
    datei = f"EA-Log {path.name}"
    sp = _colmap(header, ("date", "signal", "action"), datei)
    low = {h.lower(): h for h in header}
    mc, ma = low.get("month_close"), low.get("ma")
    out = []
    for no, rec in recs:
        try:
            d = parse_date(rec[sp["date"]])
        except ValueError as exc:
            raise ValueError(f"{datei}, Zeile {no}: {exc}") from None
        out.append(LogRow(
            zeile=no,
            datum=d,
            signal=_norm_signal(rec[sp["signal"]]),
            aktion=rec[sp["action"]].strip().upper(),
            month_close=_opt_number(_zelle(rec, mc)),
            ma=_opt_number(_zelle(rec, ma)),
        ))
    if not out:
        raise ValueError(f"{datei} enthält keine Datenzeilen.")
    return out


def _tv_datum(name: str, no: int, raw: str) -> date:
    try:
        return parse_date(raw)
    except ValueError as exc:
        raise ValueError(f"{name}, Zeile {no}: {exc}") from None


def _tv_format_a(name, recs, typ_cols, d_entry, d_exit, p_entry, p_exit) -> list[Event]:
    events = []
    for no, rec in recs:
        raw_e = rec.get(d_entry, "").strip()
        raw_x = rec.get(d_exit, "").strip()
        if not raw_e and not raw_x:
            continue
        short = any("short" in rec.get(t, "").lower() for t in typ_cols)
        if raw_e:
            events.append(Event(
                _tv_datum(name, no, raw_e),
                SHORT if short else LONG,
                "Entry short" if short else "Entry long",
                no,
                _opt_number(_zelle(rec, p_entry)),
            ))
        if raw_x:
            events.append(Event(
                _tv_datum(name, no, raw_x),
                SHORT if short else FLAT,
                "Exit short" if short else "Exit long",
                no,
                _opt_number(_zelle(rec, p_exit)),
            ))
    return events


def _tv_format_b(name, recs, d_col, t_col, p_col) -> list[Event]:
    events = []
    for no, rec in recs:
        typ = rec.get(t_col, "").strip()
        raw = rec.get(d_col, "").strip()
        if not typ and not raw:
            continue
        low = typ.lower()
        is_entry = any(t in low for t in ("entry", "einstieg"))
        is_exit = any(t in low for t in ("exit", "ausstieg"))
        if not (is_entry or is_exit):
            raise ValueError(
                f"{name}, Zeile {no}: Typ {typ!r} nicht erkannt (erwartet z. B. "
                "'Entry long' / 'Exit long' oder 'Einstieg long' / 'Ausstieg long')."
            )
        if not raw:
            raise ValueError(f"{name}, Zeile {no}: Datum fehlt.")
        if "short" in low:
            kind = SHORT
        elif "long" in low:
            kind = LONG if is_entry else FLAT
        else:
            raise ValueError(f"{name}, Zeile {no}: Richtung (long/short) im Typ {typ!r} nicht erkannt.")
        events.append(Event(_tv_datum(name, no, raw), kind, typ, no, _opt_number(_zelle(rec, p_col))))
    return events


def load_tv_events(path: Path) -> tuple[str, list[Event]]:
    """Liest den TradingView-Export "Liste der Trades" in einem von zwei Formaten.

    A: eine Zeile pro Trade, mit Entry- und Exit-Datumsspalte.
    B: zwei Zeilen pro Trade, Typ-Spalte mit 'Entry long'/'Exit long' (bzw. Einstieg/Ausstieg).
    """
    header, recs = read_table(path)
    low = {h: h.lower() for h in header}

    def spalten(*teile: str) -> list[str]:
        return [h for h in header if any(t in low[h] for t in teile)]

    # Spalten mit 'date'/'datum' vor reinen 'zeit'-Spalten (z. B. "Uhrzeit") bevorzugen
    datum = sorted(
        spalten("date", "datum", "zeit"),
        key=lambda h: 0 if any(t in low[h] for t in ("date", "datum")) else 1,
    )
    typ = spalten("type", "typ")
    preis = spalten("price", "preis")
    datum_entry = [h for h in datum if any(t in low[h] for t in ("entry", "einstieg"))]
    datum_exit = [h for h in datum if any(t in low[h] for t in ("exit", "ausstieg"))]
    preis_entry = next((h for h in preis if any(t in low[h] for t in ("entry", "einstieg"))), None)
    preis_exit = next((h for h in preis if any(t in low[h] for t in ("exit", "ausstieg"))), None)

    if datum_entry and datum_exit:
        events = _tv_format_a(path.name, recs, typ, datum_entry[0], datum_exit[0], preis_entry, preis_exit)
        return "A (eine Zeile pro Trade)", events
    if datum and typ:
        events = _tv_format_b(path.name, recs, datum[0], typ[0], preis[0] if preis else None)
        return "B (zwei Zeilen pro Trade)", events
    raise ValueError(
        f"Spalten in {path.name} nicht erkannt. Gefunden: {', '.join(header)}. "
        "Erwartet entweder Format A (Entry- und Exit-Datumsspalte, Namen mit 'entry'/'einstieg' "
        "bzw. 'exit'/'ausstieg') oder Format B (Datum-Spalte mit 'date'/'datum'/'zeit' und "
        "Typ-Spalte mit 'type'/'typ')."
    )


# ---------------------------------------------------------------- Abgleich

def match_events(
    changes: list[RefChange], events: list[Event], tol: int
) -> tuple[list[tuple[RefChange, Event, int]], list[RefChange], list[Event]]:
    """Ordnet jedem Referenz-Wechsel hoechstens eine passende Aktion zu (eins zu eins).

    Passend: gleiche Richtung (LONG <-> BUY/Entry long, FLAT <-> CLOSE/Exit long) und
    Datum der Aktion im Fenster [exec_date - 2 Tage, exec_date + tol Tage].
    """
    used = [False] * len(events)
    found, missing = [], []
    order = sorted(changes, key=lambda c: (c.exec_date is None, c.exec_date or c.month_end))
    for ch in order:
        if ch.exec_date is None:
            missing.append(ch)
            continue
        best_i, best_d = None, None
        for i, ev in enumerate(events):
            if used[i] or ev.kind != ch.kind:
                continue
            d = (ev.datum - ch.exec_date).days
            if -FRUEH_TOLERANZ_TAGE <= d <= tol and (best_d is None or abs(d) < abs(best_d)):
                best_i, best_d = i, d
        if best_i is None:
            missing.append(ch)
        else:
            used[best_i] = True
            found.append((ch, events[best_i], best_d))
    extra = [ev for i, ev in enumerate(events) if not used[i]]
    return found, missing, extra


def check_signals(log_rows: list[LogRow], ref_rows: list[RefRow]) -> SignalStats:
    """Vergleicht das Signal jeder Logzeile mit dem Referenzsignal des Vormonats-Monatsendes."""
    ref_by_month = {(r.month_end.year, r.month_end.month): r for r in ref_rows}
    st = SignalStats()
    for lr in log_rows:
        if lr.signal is None:
            st.ohne_signal += 1
            continue
        y, m = lr.datum.year, lr.datum.month
        vormonat = (y - 1, 12) if m == 1 else (y, m - 1)
        ref = ref_by_month.get(vormonat)
        if ref is None:
            st.ohne_ref += 1
            continue
        st.geprueft += 1
        if ref.signal == lr.signal:
            st.ok += 1
        else:
            st.abweichungen.append((lr, ref))
    return st


def _fmt_pct(ok: int, total: int) -> str:
    if ok == total:
        return "100.0 %"
    return f"{math.floor(ok * 1000 / total) / 10:.1f} %"  # abgerundet, damit nie 100.0 bei Abweichung


def _abstand(close: float | None, ma: float | None) -> str:
    if close is None or not ma:
        return "n/a"
    return f"{(close / ma - 1) * 100:+.2f} %"


def run_comparison(
    *,
    titel: str,
    info: list[str],
    extra_label: str,
    name_long: str,
    name_flat: str,
    ref_rows: list[RefRow],
    events: list[Event],
    tol: int,
    log_rows: list[LogRow] | None = None,
) -> int:
    changes = [RefChange(r.month_end, r.signal, r.exec_date) for r in ref_rows if r.change]
    found, missing, extra = match_events(changes, events, tol)
    sig = check_signals(log_rows, ref_rows) if log_rows is not None else None
    n_sig = sig.geprueft if sig else 0
    n_sig_ok = sig.ok if sig else 0
    total = len(changes) + len(extra) + n_sig
    ok = len(found) + n_sig_ok

    print(f"=== Abgleich {titel} gegen Referenz (Toleranz {tol} Tage) ===")
    for line in info:
        print(line)
    print(f"Referenz-Wechsel: {len(changes)}")
    print(f"  gefunden: {len(found)}")
    print(f"  fehlend:  {len(missing)}")
    for ch in missing:
        ausf = ch.exec_date.isoformat() if ch.exec_date else "unbekannt (Daten reichen nicht bis zum nächsten Handelstag)"
        erwartet = name_long if ch.kind == LONG else name_flat
        print(f"    - {ch.kind}: Ausführung {ausf} (Monatsende {ch.month_end.isoformat()}), erwartet {erwartet}")
    print(f"Zusätzliche {extra_label} ohne Referenz: {len(extra)}")
    for ev in extra:
        preis = f", Preis {ev.preis:g}" if ev.preis is not None else ""
        print(f"    - {ev.datum.isoformat()} Zeile {ev.zeile}: {ev.text}{preis}")
    if sig is None:
        print("Signal-Abweichungen: entfällt (TV-Export enthält keine Signalzeilen)")
    else:
        print(
            f"Signal-Abweichungen: {len(sig.abweichungen)} "
            f"(geprüft: {sig.geprueft}, ohne Referenzwert: {sig.ohne_ref}, "
            f"ohne gültiges Signal: {sig.ohne_signal})"
        )
        for lr, ref in sig.abweichungen:
            print(
                f"    - {lr.datum.isoformat()} Zeile {lr.zeile}: EA {lr.signal}, Referenz {ref.signal} "
                f"(Monatsende {ref.month_end.isoformat()}); Abstand close/ma: "
                f"EA {_abstand(lr.month_close, lr.ma)}, Referenz {_abstand(ref.close, ref.ma12)}"
            )
    teile_ok = [f"gefunden {len(found)}"]
    teile_tot = [f"Wechsel {len(changes)}"]
    if sig is not None:
        teile_ok.append(f"Signale ok {sig.ok}")
        teile_tot.append(f"Signale geprüft {sig.geprueft}")
    teile_tot.append(f"zusätzlich {len(extra)}")
    print(f"Basis: ({' + '.join(teile_ok)}) / ({' + '.join(teile_tot)})")
    if total == 0:
        print("ÜBEREINSTIMMUNG: n/a (nichts zu vergleichen)")
        return 1
    print(f"ÜBEREINSTIMMUNG: {_fmt_pct(ok, total)}")
    return 0 if ok == total else 1


# ---------------------------------------------------------------- Kommandos

def _toleranz(v: int) -> int:
    if v < 0:
        raise ValueError("--tolerance-days darf nicht negativ sein.")
    return v


def cmd_reference(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    if args.symbol and args.csv:
        parser.error("--symbol und --csv nicht zusammen angeben.")
    source = args.source or ("csv" if args.csv else "yahoo" if args.symbol else None)
    if source is None:
        parser.error("Quelle fehlt: --symbol SYMBOL (yahoo) oder --csv PFAD.")
    if source == "yahoo" and not args.symbol:
        parser.error("--source yahoo braucht --symbol.")
    if source == "csv" and not args.csv:
        parser.error("--source csv braucht --csv PFAD.")

    start = parse_date(args.date_from)
    end = parse_date(args.date_to)
    if start > end:
        raise ValueError("--from liegt nach --to.")

    if source == "yahoo":
        prices = load_prices_yahoo(args.symbol, start, end)
    else:
        prices = load_prices_csv(_require_file(args.csv))

    rows, warnungen = build_reference(prices, start, end, date.today())
    if not rows:
        raise ValueError("Zu wenig Daten: mindestens 12 vollständige Monatsenden nötig.")

    df = pd.DataFrame(rows, columns=REF_SPALTEN)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8")

    for w in warnungen:
        print(f"WARNUNG: {w}", file=sys.stderr)
    print(f"Referenz geschrieben: {out}")
    print(
        f"Monatsenden mit Signal: {len(df)} ({df['month_end'].iloc[0]} bis {df['month_end'].iloc[-1]}), "
        f"Wechsel: {int(df['change'].sum())}"
    )
    if df["exec_date"].iloc[-1] == "":
        print("Hinweis: Für das letzte Monatsende fehlt das Ausführungsdatum (Daten reichen nicht bis zum nächsten Handelstag).")
    print("Letzte 12 Zeilen:")
    print(df.tail(12).round({"close": 4, "ma12": 4}).to_string(index=False))
    return 0


def cmd_compare_mt5(args: argparse.Namespace) -> int:
    tol = _toleranz(args.tolerance_days)
    ref = load_reference(_require_file(args.reference))
    log = load_ea_log(_require_file(args.log))
    events = [
        Event(r.datum, LONG if r.aktion == "BUY" else FLAT, r.aktion, r.zeile)
        for r in log
        if r.aktion in ("BUY", "CLOSE")
    ]
    info = [
        f"EA-Log: {len(log)} Zeilen, {len(events)} Aktionen (BUY/CLOSE), "
        f"Zeitraum {min(r.datum for r in log)} bis {max(r.datum for r in log)}",
        f"Referenz: {len(ref)} Monatsenden mit Signal, Zeitraum {ref[0].month_end} bis {ref[-1].month_end}",
    ]
    return run_comparison(
        titel="EA-Log", info=info, extra_label="EA-Aktionen",
        name_long="BUY", name_flat="CLOSE",
        ref_rows=ref, events=events, tol=tol, log_rows=log,
    )


def cmd_compare_tv(args: argparse.Namespace) -> int:
    tol = _toleranz(args.tolerance_days)
    ref = load_reference(_require_file(args.reference))
    fmt, events = load_tv_events(_require_file(args.trades))
    info = [
        f"TV-Export: Format {fmt}, {len(events)} Ereignisse (Einstiege/Ausstiege)",
        f"Referenz: {len(ref)} Monatsenden mit Signal, Zeitraum {ref[0].month_end} bis {ref[-1].month_end}",
    ]
    return run_comparison(
        titel="TradingView-Trades", info=info, extra_label="TV-Ereignisse",
        name_long="Entry long", name_flat="Exit long",
        ref_rows=ref, events=events, tol=tol, log_rows=None,
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Abgleich der MA12-Monatsend-Strategie: Referenz gegen MT5-EA-Log und TradingView-Trades."
    )
    sub = p.add_subparsers(dest="befehl", required=True, metavar="BEFEHL")

    r = sub.add_parser("reference", help="Referenz-Signale aus Tageskursen berechnen")
    r.add_argument("--source", choices=["yahoo", "csv"], help="Quelle (Standard: aus --symbol bzw. --csv abgeleitet)")
    r.add_argument("--symbol", help="Yahoo-Ticker, z. B. SPY")
    r.add_argument("--csv", metavar="PFAD", help="Tageskurs-CSV mit Spalten date,close")
    r.add_argument("--out", required=True, metavar="PFAD.csv", help="Ziel-CSV der Referenz")
    r.add_argument("--from", dest="date_from", default=DEFAULT_FROM, metavar="DATUM")
    r.add_argument("--to", dest="date_to", default=DEFAULT_TO, metavar="DATUM")

    m = sub.add_parser("compare-mt5", help="EA-Log (MT5, Trenner ';') mit Referenz abgleichen")
    m.add_argument("--log", required=True, metavar="PFAD")
    m.add_argument("--reference", required=True, metavar="PFAD.csv")
    m.add_argument("--tolerance-days", type=int, default=5, metavar="N")

    t = sub.add_parser("compare-tv", help="TradingView-Export 'Liste der Trades' mit Referenz abgleichen")
    t.add_argument("--trades", required=True, metavar="PFAD.csv")
    t.add_argument("--reference", required=True, metavar="PFAD.csv")
    t.add_argument("--tolerance-days", type=int, default=5, metavar="N")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.befehl == "reference":
            return cmd_reference(args, parser)
        if args.befehl == "compare-mt5":
            return cmd_compare_mt5(args)
        return cmd_compare_tv(args)
    except (ValueError, OSError) as exc:
        print(f"FEHLER: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    sys.exit(main())
