"""Halloween-Indikator / "Sell in May": US-Aktien von November bis April, sonst Cash — Langzeit-Test auf Ken-French-Gesamtmarkt.

Quellen: Bouman, Jacobsen 2002, "The Halloween Indicator, 'Sell in May and Go Away': Another Puzzle" (AER);
Zhang, Jacobsen 2012, "The Halloween Indicator: Everywhere and All the Time". Regel aus
research/strategie-kandidaten.json (Eintrag halloween_nov_apr_equity) und research/families/calendar.md, 3.2.

Regel (festgelegt vor dem Backtest, Parameter aus der Quelle, keine Optimierung):
    Jedes Jahr Y: Entry am Schluss des letzten Handelstags im Oktober  -> 100 % Aktienmarkt.
                  Exit  am Schluss des letzten Handelstags im April (Y+1) -> 100 % Cash, bis zum nächsten Oktober.
    Kein Hebel, kein Short. Zwei Wechsel pro Jahr.

Umsetzung im Engine-Vertrag:
* Das Panel (`load()`) enthält zwei Spalten: "MKT" = US-Gesamtmarkt als Total-Return-Reihe aus Ken French
  (Mkt-RF + RF, täglich; open == close) und "^GDAXI" = DAX-Index (nur für die Variante `dax`; ab 1990, auf die
  French-Handelstage gelegt, Lücken höchstens 5 Tage vorwärts gefüllt, damit an US-Handelstagen ohne DAX-Handel
  keine Tagesrendite verloren geht). Cash verzinst die Engine mit dem French-RF.
* Monatsenden NUR über qlab.calendar.month_end_flags (kausal; der Kalender ist im Voraus bekannt). Es gibt nur
  an den Monatsenden Oktober (Entry, Gewicht 1) und April (Exit, Gewicht 0) eine Zeile; an allen anderen Tagen
  bleibt die Zeile weg (Engine: nichts tun). Zeile nur, wenn der Kurs am Signaltag gültig ist (NaN = nicht handelbar).
* Die Reihe beginnt mit dem ersten Oktober- bzw. April-Monatsende der Daten (French: 1926-10-30). Kein Signal vor
  dem ersten Kalenderereignis; wer vor dem ersten Oktober im Cash steht, ist ohnehin im Sommerzustand.
* Ausführung: Die Spezifikation sieht MOC am Signaltag t vor. Der Engine-Vertrag handelt ein Signal von t erst
  zur Eröffnung von t+1; weil open == close, bedeutet das hier den Schlusskurs von t+1 (verdient ab t+2). Das ist
  eine Spur konservativer als die Spezifikation und entspricht zugleich der Sensitivität "Ausführung am Folgetag".
  Die MOC-Ausführung der Spezifikation läuft über `scripts/run_all.py --exec close` (Handel zum Schluss von t).

Kosten: 2 bp je Seite (Spezifikation) für den Gesamtmarkt über SPEC["cost_bps"]; Stresstest 1/5 bp über
`--cost-mult 0.5` bzw. `2.5` im Harness. Der DAX läuft mit dem Engine-Standard (5 bp), weil er nur ein Index ist.
Steuern und Cash-Zins verbucht die Engine.

Pflichtvergleiche der Spezifikation (nicht Teil dieses Moduls, sondern der Auswertung): Buy&Hold (Harness-Benchmarks
MKT/SPY), konstanter 50/50-Mix (`qlab.controls.fixed_mix(panel, {ASSET: 0.5})`) und der Rang des Nov-Apr-Fensters unter
allen 12 möglichen 6-Monats-Startmonaten (Mining-Check): dafür `weights(panel, start_month=m)` für m = 1..12 aufrufen
(Parameter `start_month`/`n_months`, Standard 11/6 laut Quelle; die 12 Läufe sind ein Rang-Check, keine Auswahl).

Variante (vorab festgelegt, Robustheits-Check, keine Auswahl der besten):
    dax   Internationale Replikation: dieselbe Regel auf den DAX (^GDAXI, ab 1990) statt auf den US-Markt; Cash bleibt
          der US-RF (kein EUR-Geldmarktzins verfügbar) — Näherung.
Die weiteren Sensitivitäten der Spezifikation stehen im ETF-Modul `halloween_nov_apr_equity_etf` (Cash = IEF, EFA)
bzw. in der Ausführungsart des Harness (siehe oben).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from qlab.calendar import month_end_flags
from qlab.data import Panel, french, load_ticker, panel_from_returns

ASSET = "MKT"
DAX = "^GDAXI"
DAX_START = "1990-01-01"             # gemeinsamer Cache-Start (Yahoo-Index ab 1987-12, im Cache ab 1990)
FFILL_LIMIT = 5                      # DAX-Feiertage an US-Handelstagen: höchstens 5 Tage Vorwärtsfüllen

SPEC = {
    "id": "halloween_nov_apr_equity",
    "name": "Halloween-Indikator: US-Aktien Nov-Apr, Cash Mai-Okt, Langzeit auf French-Gesamtmarkt",
    "family": "calendar",
    "tickers": [ASSET, DAX],         # Spalten des Panels aus load(); keine Yahoo-Ticker außer dem DAX-Index
    "start": "1926-07-01",           # French-Datenstart; erstes Signal Ende Oktober 1926
    "sources": [
        "Bouman, Jacobsen 2002, The Halloween Indicator, Sell in May and Go Away: Another Puzzle, "
        "https://pure.eur.nl/en/publications/the-halloween-indicator-sell-in-may-and-go-away-another-puzzle/",
        "Zhang, Jacobsen 2012, The Halloween Indicator: Everywhere and All the Time, "
        "https://research.nottingham.edu.cn/en/publications/the-halloween-indicator-sell-in-may-and-go-away-everywhere-and-al/fingerprints/",
    ],
    "params": {"asset": ASSET, "start_month": 11, "n_months": 6, "cash_asset": None},
    "variants": {
        "dax": {"asset": DAX},
    },
    "cost_bps": {ASSET: 2.0},
}


# --------------------------------------------------------------------------------------
# Daten
# --------------------------------------------------------------------------------------

def build_panel(mkt_ret: pd.Series, dax_close: pd.Series | None = None, ffill_limit: int = FFILL_LIMIT) -> Panel:
    """Panel aus Gesamtmarkt-Renditen (French) plus optional DAX-Schlusskursen auf den French-Handelstagen.

    Der DAX wird auf den French-Kalender gelegt; Tage, an denen nur der DAX (nicht die USA) handelt, entfallen
    (Kurs-NIVEAUS gehen nicht verloren), und US-Handelstage ohne DAX-Handel werden höchstens `ffill_limit` Tage
    mit dem letzten Schluss gefüllt. Ohne Füllung würde die Engine die Rendite über die Lücke verlieren
    (sie rechnet pro Tag open[i] / close[i-1]). Vor dem ersten DAX-Kurs bleibt alles NaN (nicht handelbar).
    open == close für beide Spalten (Handel zum Folgetag-Schluss, wie bei allen French-Reihen).
    """
    base = panel_from_returns(pd.DataFrame({ASSET: mkt_ret}))
    if dax_close is None:
        return base
    close = base.close.copy()
    close[DAX] = dax_close.astype(float).reindex(close.index).ffill(limit=ffill_limit)
    return Panel(close.copy(), close)


def load() -> Panel:
    """Langzeit-Panel (French-Gesamtmarkt ab 1926-07 + DAX ab 1990), ungekürzt (der Harness schneidet ab)."""
    fdf = french("F-F_Research_Data_Factors", daily=True)
    mret = (fdf["Mkt-RF"] + fdf["RF"]).astype(float)
    dax = load_ticker(DAX, start=DAX_START)["Close"]
    return build_panel(mret, dax)


# --------------------------------------------------------------------------------------
# Strategie
# --------------------------------------------------------------------------------------

def window_months(start_month: int = 11, n_months: int = 6) -> tuple[int, int]:
    """(Entry-Monat, Exit-Monat): Entry am Ende des Monats VOR `start_month`, Exit am Ende des letzten Fenstermonats.

    Standard 11/6: Entry Ende Oktober (10), Exit Ende April (4). `n_months` höchstens 11 (sonst fielen Entry und Exit
    auf denselben Monat).
    """
    if not (1 <= int(start_month) <= 12):
        raise ValueError(f"start_month muss 1..12 sein, nicht {start_month}")
    if not (1 <= int(n_months) <= 11):
        raise ValueError(f"n_months muss 1..11 sein, nicht {n_months}")
    entry = (int(start_month) - 2) % 12 + 1
    exit_ = (int(start_month) + int(n_months) - 2) % 12 + 1
    return entry, exit_


def halloween_weights(close: pd.DataFrame, asset: str, start_month: int = 11, n_months: int = 6,
                      cash_asset: str | None = None) -> pd.DataFrame:
    """Zielgewichte an den Monatsenden Entry/Exit; Index = Signaltage (Schluss t), Spalten = asset (+ cash_asset).

    Entry-Zeile: asset 1, cash_asset 0. Exit-Zeile: asset 0, cash_asset 1 (ohne cash_asset bleibt der Rest Cash,
    den die Engine verzinst). Eine Zeile gibt es nur, wenn die Kurse aller beteiligten Titel am Signaltag gültig sind.
    """
    if cash_asset is not None and cash_asset == asset:
        raise ValueError("cash_asset darf nicht der Aktien-Titel sein")
    entry_m, exit_m = window_months(start_month, n_months)
    idx = close.index
    flags = month_end_flags(idx).to_numpy()                 # nur kausal erkannte Monatsenden
    months = np.asarray(idx.month)
    is_entry = flags & (months == entry_m)
    is_exit = flags & (months == exit_m)
    ok = close[asset].notna().to_numpy()
    if cash_asset is not None:
        ok = ok & close[cash_asset].notna().to_numpy()      # NaN = nicht handelbar (z. B. noch nicht gelistet)
    sel = (is_entry | is_exit) & ok
    on = is_entry[sel].astype(float)
    cols = {asset: on}
    if cash_asset is not None:
        cols[cash_asset] = 1.0 - on
    return pd.DataFrame(cols, index=idx[sel])


def weights(panel, asset: str = ASSET, start_month: int = 11, n_months: int = 6,
            cash_asset: str | None = None) -> pd.DataFrame:
    """Zielgewichte (0 oder 1) auf `asset` am letzten Handelstag von Oktober (1) bzw. April (0); Rest ist Cash."""
    return halloween_weights(panel.close, asset, start_month=start_month, n_months=n_months, cash_asset=cash_asset)
