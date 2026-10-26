"""Turn of the Month (McConnell/Xu 2008) — Live-Test auf dem investierbaren ETF SPY (ab 1993-01-29).

Zweites Modul zu `tom_spy_m2_p3` (Langzeit-Test auf dem French-Gesamtmarkt): gleiche Regel und gleicher Kern
(`window_weights` wird von dort importiert), aber gehandelt wird der SPY (Yahoo, angepasst = Total Return) statt der
French-Reihe. Regel, Quellen und Notation der Handelstage siehe das Hauptmodul bzw. research/families/calendar.md, 3.1.

    d(-1) = letzter Handelstag des Monats M, d(-2) = vorletzter, d(+k) = k-ter Handelstag von M+1.
    Long 100 % SPY von Close(d(-2)) bis Close(d(+3)) (Tagesrenditen der Tage -1, +1, +2, +3), sonst 100 % Cash.

Ausfuehrung (wichtig, weicht vom Lab-Standard "Eroeffnung t+1" bewusst ab):
Die Spezifikation fordert MOC-Orders zum Schlusskurs (der Kalender ist im Voraus bekannt, das Signal braucht keinen
Preis). Der Harness handelt aber standardmaessig zur Eroeffnung von t+1. Damit die Basis trotzdem genau
Close(d(-2)) -> Close(d(+3)) abbildet, liefert `load()` zwei Spalten:

    SPY       Handelsspalte der Basis und von `tag_plus1`: open == close (angepasster Schlusskurs). Die Engine
              handelt ein Signal von Tag t dann zum Schlusskurs von t+1 — Kauf bei Close(d(-2)) (Signal auf d(-3)),
              Verkauf bei Close(d(+3)) (Signal auf d(+2)). Dasselbe Verfahren wie bei den French-Panels.
    SPY_OPEN  echte Eroeffnungskurse (Open) und Schlusskurse des SPY. Nur fuer die Variante `konservativ`
              (Spezifikation: Entry Open(d(-1)), Exit Open(d(+4))): Signal auf d(-2) bzw. d(+3), die Engine handelt
              zur Eroeffnung des Folgetags.

Beide Spalten sind derselbe ETF mit denselben Schlusskursen; es wird je Lauf nur eine davon gehandelt. Der Harness muss
mit der Standard-Ausfuehrung (`--exec open`) laufen; `--exec close`/`close_next` verschiebt die Ausfuehrung um einen Tag.

Umsetzung im Engine-Vertrag:
* Handelstage kommen aus dem Datenindex (SPY-Handelstage, NYSE). "Letzter Handelstag des Monats" ausschliesslich ueber
  qlab.calendar.month_end_flags; weil d(-3) schon zwei Handelstage vor dem Monatsende erkannt werden muss, verlaengert
  `window_weights` den Index um 6 kuenftige NYSE-Handelstage (nur Datumsangaben, keine Preise).
* Die Reihe beginnt mit dem ersten Monatsende, dessen d(-3) in den SPY-Daten liegt (Februar 1993). Es werden keine
  Gewichte auf NaN-Kurse vergeben.
* Cash verzinst die Engine mit dem French-RF (SHY/BIL der Spezifikation werden nicht gebraucht). Kosten 2 bp je Seite
  (Spezifikation) fuer beide Spalten ueber SPEC["cost_bps"]; der Kosten-Stresstest 1/5 bp laeuft ueber den Harness
  (`--cost-mult 0.5` bzw. `2.5`). Steuern verbucht die Engine.

Varianten (vorab festgelegt aus der Spezifikation, Robustheits-Checks, keine Auswahl der besten):
    tag_plus1    nur Tag +1 (ETF-Era-Befund): Close(d(-1)) bis Close(d(+1))
    konservativ  Entry Open(d(-1)), Exit Open(d(+4)) mit echten Eroeffnungskursen (Spalte SPY_OPEN)
(Die dritte Spezifikations-Sensitivitaet "Kosten 5 bp je Seite" ist keine Gewichts-Variante: --cost-mult 2.5.)
"""
from __future__ import annotations

import pandas as pd

from qlab.data import Panel, load_ticker
from strategies.tom_spy_m2_p3 import window_weights

ASSET = "SPY"
ASSET_OPEN = "SPY_OPEN"

SPEC = {
    "id": "tom_spy_m2_p3_etf",
    "name": "Turn of the Month (Tage -1 bis +3), Live-Test auf SPY",
    "family": "calendar",
    "tickers": [ASSET],              # Yahoo-Ticker; das Panel aus load() hat zusaetzlich die Pseudo-Spalte SPY_OPEN
    "start": "1993-01-01",           # SPY startet 1993-01-29
    "sources": [
        "McConnell, Xu 2008, Equity Returns at the Turn of the Month, "
        "https://ideas.repec.org/a/taf/ufajxx/v64y2008i2p49-64.html",
        "Maberly, Waggoner 2000, Turn-of-the-month effect in S&P 500 futures / cash, "
        "https://ideas.repec.org/p/fip/fedawp/2000-11.html",
    ],
    "params": {"asset": ASSET, "entry_day": -2, "exit_day": 3},
    "variants": {
        "tag_plus1": {"entry_day": -1, "exit_day": 1},
        "konservativ": {"asset": ASSET_OPEN, "entry_day": -1, "exit_day": 4},
    },
    "cost_bps": {ASSET: 2.0, ASSET_OPEN: 2.0},
}


# --------------------------------------------------------------------------------------
# Daten
# --------------------------------------------------------------------------------------

def build_panel(ohlc: pd.DataFrame) -> Panel:
    """Panel mit den Spalten SPY (open := close, Handel zum Schlusskurs) und SPY_OPEN (echte Open/Close).

    `ohlc`: DataFrame mit den Spalten "Open" und "Close" (angepasst), Index = Handelstage.
    """
    close = ohlc["Close"].astype(float)
    open_ = ohlc["Open"].astype(float)
    cl = pd.DataFrame({ASSET: close, ASSET_OPEN: close})
    op = pd.DataFrame({ASSET: close, ASSET_OPEN: open_})
    return Panel(op, cl)


def load() -> Panel:
    """SPY (auto_adjust-OHLC aus dem Cache) ab 1993-01-29, ungekuerzt (der Harness schneidet ab)."""
    return build_panel(load_ticker(ASSET, start=SPEC["start"]))


# --------------------------------------------------------------------------------------
# Strategie
# --------------------------------------------------------------------------------------

def weights(panel, asset: str = ASSET, entry_day: int = -2, exit_day: int = 3) -> pd.DataFrame:
    """Zielgewichte (0 oder 1) auf `asset` an den Signaltagen des Turn-of-the-Month-Fensters; sonst Cash."""
    return window_weights(panel.close[asset], asset, entry_day=entry_day, exit_day=exit_day)
