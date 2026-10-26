"""Turn of the Month (McConnell/Xu 2008) — Handelstage -1 bis +3, sonst Cash. Langzeit-Test auf Ken-French-Gesamtmarkt 1926-2022.

Quellen: McConnell, Xu 2008, "Equity Returns at the Turn of the Month", Financial Analysts Journal 64(2),
https://ideas.repec.org/a/taf/ufajxx/v64y2008i2p49-64.html; Maberly, Waggoner 2000 (Atlanta Fed WP 2000-11).
Regel (festgelegt vor dem Backtest, aus research/strategie-kandidaten.json und research/families/calendar.md, 3.1):

    d(-1) = letzter Handelstag des Monats M, d(-2) = vorletzter, d(+k) = k-ter Handelstag von M+1.
    Long 100 % Aktienmarkt von Close(d(-2)) bis Close(d(+3)); gehalten werden also die Tagesrenditen der
    Tage d(-1), d(+1), d(+2), d(+3) (4 von ca. 21 Handelstagen, ca. 19 % Exposure). Sonst 100 % Cash.

Umsetzung im Engine-Vertrag:
* Der Handelskalender ist im Voraus bekannt, das Signal braucht KEINEN Preis. Eine Signalzeile steht deshalb auf dem
  Handelstag VOR dem Ausfuehrungstag: Kauf bei Close(d(-2)) = Signal auf d(-3), Verkauf bei Close(d(+3)) = Signal auf
  d(+2). Das Panel aus `load()` hat open == close (panel_from_returns): die Engine handelt ein Signal von Tag t zum
  Schlusskurs von t+1 — genau die MOC-Ausfuehrung der Spezifikation. Der Kauf verdient ab d(-1), der Verkauf nach
  dem Ertrag von d(+3).
* Handelstage kommen aus dem Datenindex des Panels (alte French-Daten enthalten bis 1952-05 die Samstage, die
  damals Handelstage waren; Feiertage fehlen einfach). "Letzter Handelstag des Monats" ausschliesslich ueber
  qlab.calendar.month_end_flags, nie ueber groupby/resample auf den Daten. Weil d(-3) schon zwei Handelstage vor dem
  Monatsende erkannt werden muss, wird der Datenindex um 6 kuenftige Handelstage aus dem NYSE-Kalender verlaengert
  (nur Datumsangaben, keine Preise). Dadurch sind abgeschnittene Daten (Live-Betrieb, check_causality) ueber den
  Kalender konsistent mit den vollen Daten. Vor 1952-05-26 nutzt die Verlaengerung Mo-Sa, danach den NYSE-Kalender
  (Feiertage in qlab.calendar erst ab 1990, die Sommer-Samstagsschliessungen 1945-1951 sind nicht modelliert; in den
  alten Daten betrifft das nur das Schwanzende abgeschnittener Daten, nie die Ergebnisse auf den vollen Daten. Die
  Kausalitaets-Schnitte des Harness liegen bei 30-95 % des Index, also nach 1952.)
* Nur Aenderungszeilen: Einstieg = Zeile {asset: 1.0} auf dem Signaltag, Ausstieg = Zeile {asset: 0.0}. Zwischen den
  Zeilen "driftet" die Position (kein Rebalancing, keine Kosten dazwischen). Einstieg nur, wenn der Kurs auf dem
  Signaltag gueltig ist (NaN = nicht handelbar); der Ausstieg wird bei NaN-Kurs auf den naechsten gueltigen Tag
  verschoben, damit keine Position haengen bleibt.
* Cash verzinst die Engine mit dem French-RF (SHY/BIL aus der Spezifikation werden deshalb nicht gebraucht). Kosten
  2 bp je Seite laut Spezifikation ueber SPEC["cost_bps"]; der Kosten-Stresstest 5 bp je Seite laeuft ueber den
  Harness: `--cost-mult 2.5`.

Parameter `entry_day` / `exit_day` (Notation der Spezifikation: -1 = letzter, -2 = vorletzter Handelstag von M,
+k = k-ter Handelstag von M+1): der Handelstag, an dessen AUSFUEHRUNGSKURS gekauft bzw. verkauft wird.
Basis: entry_day=-2, exit_day=+3.

Varianten (vorab festgelegt aus der Spezifikation, Robustheits-Checks, keine Auswahl der besten):
    tag_plus1    nur Tag +1 (ETF-Era-Befund): entry_day=-1, exit_day=+1, Close(d(-1)) bis Close(d(+1))
    konservativ  spaetere Ausfuehrung: entry_day=-1, exit_day=+4. Die Spezifikation meint Open(d(-1)) bis Open(d(+4)); auf den
                 French-Daten gibt es keine Eroeffnungskurse, die Variante ist dort Close(d(-1)) bis Close(d(+4))
                 (ein voller Handelstag spaeter als die Basis). Das ETF-Modul bildet sie mit echten Eroeffnungskursen ab.
(Die dritte Spezifikations-Sensitivitaet "Kosten 5 bp je Seite" ist keine Gewichts-Variante: --cost-mult 2.5.)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pandas.tseries.offsets import CustomBusinessDay

from qlab.calendar import NYSE_BDAY, month_end_flags
from qlab.data import Panel, french, panel_from_returns

ASSET = "MKT"

SPEC = {
    "id": "tom_spy_m2_p3",
    "name": "Turn of the Month (Tage -1 bis +3), Langzeit auf French-Gesamtmarkt",
    "family": "calendar",
    "tickers": [ASSET],              # Spalte des Panels aus load(); kein Yahoo-Ticker
    "start": "1926-07-01",           # French Daily beginnt 1926-07-01
    "sources": [
        "McConnell, Xu 2008, Equity Returns at the Turn of the Month, "
        "https://ideas.repec.org/a/taf/ufajxx/v64y2008i2p49-64.html",
        "Maberly, Waggoner 2000, Turn-of-the-month effect in S&P 500 futures / cash, "
        "https://ideas.repec.org/p/fip/fedawp/2000-11.html",
    ],
    "params": {"asset": ASSET, "entry_day": -2, "exit_day": 3},
    "variants": {
        "tag_plus1": {"entry_day": -1, "exit_day": 1},
        "konservativ": {"entry_day": -1, "exit_day": 4},
    },
    "cost_bps": {ASSET: 2.0},
}

_EXT_DAYS = 6                                         # so viele kuenftige Handelstage werden aus dem Kalender ergaenzt
_SATURDAY_TRADING_END = pd.Timestamp("1952-05-26")    # letzter Datensamstag in den French-Daten: 1952-05-24
_SAT_BDAY = CustomBusinessDay(weekmask="Mon Tue Wed Thu Fri Sat")
_MAX_WINDOW_ROWS = 10                                 # laengstes erlaubtes Haltefenster (Handelstage)


# --------------------------------------------------------------------------------------
# Daten
# --------------------------------------------------------------------------------------

def build_panel(mkt_ret: pd.Series) -> Panel:
    """Panel aus Gesamtmarkt-Tagesrenditen (open == close; Handel zum Folgetag-Schlusskurs)."""
    return panel_from_returns(pd.DataFrame({ASSET: mkt_ret.astype(float)}))


def load() -> Panel:
    """Langzeit-Panel: French-Gesamtmarkt (Mkt-RF + RF, taeglich, ab 1926-07), ungekuerzt (der Harness schneidet ab)."""
    fdf = french("F-F_Research_Data_Factors", daily=True)
    return build_panel(fdf["Mkt-RF"] + fdf["RF"])


# --------------------------------------------------------------------------------------
# Kalender-Logik (Kern, wird vom ETF-Modul importiert)
# --------------------------------------------------------------------------------------

def _rel(day: int) -> int:
    """Spezifikations-Notation -> Zeilenabstand zum letzten Handelstag d(-1) des Monats (d(-1) = 0, d(+1) = 1)."""
    if day == 0 or int(day) != day:
        raise ValueError(f"Handelstag {day!r} ungueltig: -1, -2, ... oder +1, +2, ... erwartet (es gibt keinen Tag 0)")
    day = int(day)
    return day + 1 if day < 0 else day


def _extend_index(idx: pd.DatetimeIndex, n: int = _EXT_DAYS) -> pd.DatetimeIndex:
    """Datenindex plus n kuenftige Handelstage aus dem Kalender (nur Datumsangaben, keine Preise)."""
    if len(idx) == 0:
        return idx
    step = _SAT_BDAY if idx[-1] < _SATURDAY_TRADING_END else NYSE_BDAY
    future = []
    d = idx[-1]
    for _ in range(n):
        d = d + step
        future.append(d)
    return idx.append(pd.DatetimeIndex(future))


def window_weights(close: pd.Series, asset: str, entry_day: int = -2, exit_day: int = 3) -> pd.DataFrame:
    """Aenderungszeilen {asset: 1.0} (Einstiegssignal) und {asset: 0.0} (Ausstiegssignal) fuer das Turn-of-the-Month-Fenster.

    Gekauft wird am Ausfuehrungspreis des Handelstags `entry_day`, verkauft am Ausfuehrungspreis von `exit_day`
    (Notation siehe Modul-Docstring); die Signalzeile steht jeweils auf dem Handelstag davor.
    """
    e_rel, x_rel = _rel(entry_day), _rel(exit_day)
    if not (e_rel < x_rel <= e_rel + _MAX_WINDOW_ROWS):
        raise ValueError(f"exit_day ({exit_day}) muss nach entry_day ({entry_day}) liegen, Fenster hoechstens "
                         f"{_MAX_WINDOW_ROWS} Handelstage")
    idx = pd.DatetimeIndex(close.index)
    n = len(idx)
    px_ok = np.isfinite(close.to_numpy(float))
    ext = _extend_index(idx)
    me_pos = np.flatnonzero(month_end_flags(ext).to_numpy())            # Positionen von d(-1), kausal erkannt

    entries: dict[pd.Timestamp, float] = {}
    exits: dict[pd.Timestamp, float] = {}
    for p in me_pos:
        s_in = int(p) + e_rel - 1                                       # Signaltag = Handelstag vor dem Ausfuehrungstag
        s_out = int(p) + x_rel - 1
        if s_in < 0 or s_in >= n or not px_ok[s_in]:
            continue                                                    # Einstieg nicht in den Daten oder nicht handelbar
        entries[idx[s_in]] = 1.0
        j = s_out
        while j < n and not px_ok[j]:
            j += 1                                                      # Ausstieg bei NaN-Kurs auf den naechsten gueltigen Tag
        if j < n:
            exits[idx[j]] = 0.0
    rows = {**exits, **entries}                                         # bei Kollision gewinnt der neue Einstieg
    out = pd.DataFrame({asset: pd.Series(rows, dtype=float)}).sort_index()
    out.index = pd.DatetimeIndex(out.index)
    return out


# --------------------------------------------------------------------------------------
# Strategie
# --------------------------------------------------------------------------------------

def weights(panel, asset: str = ASSET, entry_day: int = -2, exit_day: int = 3) -> pd.DataFrame:
    """Zielgewichte (0 oder 1) auf `asset` an den Signaltagen des Turn-of-the-Month-Fensters; sonst Cash."""
    return window_weights(panel.close[asset], asset, entry_day=entry_day, exit_day=exit_day)
