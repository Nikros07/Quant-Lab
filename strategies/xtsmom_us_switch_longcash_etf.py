"""Cross-Asset-TSMOM USA: Long/Cash-Umschalter SPY / IEF / SHY — Live-Test auf den ETFs (ab 2002-07-30).

Zweites Modul zu `xtsmom_us_switch_longcash` (Langtest ab 1981 mit VFINX/VFITX-Proxys): gleiche Regel (der Kern
`switch_weights` wird von dort importiert), aber gehandelt werden die investierbaren ETFs. Quellen, Regel und
Begruendung siehe das Hauptmodul bzw. research/families/gap_crossasset_bond_equity_leadlag_signals.md, Abschnitt 3.1.

    rf12   = Produkt ueber 12 Monate von (1 + ^IRX[Vormonatsende] / 100 / 12) - 1
    r12(X) = AdjClose(T) / AdjClose(Monatsende T-12M) - 1 - rf12            (kein Skip-Monat)
    rE = r12(SPY), rB = r12(IEF):  rE > 0 und rB > 0 -> 100 % SPY;  rE <= 0 und rB > 0 -> 100 % IEF;  rB <= 0 -> 100 % SHY

Umsetzung im Engine-Vertrag:
* Cash-Zustand = SHY (Geldmarkt-/Kurzläufer-ETF, ab 2002-07-30), wie in der Spezifikation. Der Cash-Zins der Engine
  (Fama-French RF) wirkt nur auf Restbestände; im Normalfall ist das Portfolio zu 100 % in genau einem ETF.
* Signal am Schluss des letzten Handelstags T eines Monats (month_end_flags, kausal); die Engine handelt zur
  Eroeffnung von T+1 (Standard-Ausfuehrung "open"). Die Spezifikation sieht genau das vor; die Variante der
  Spezifikation "Ausfuehrung Schluss t+1" ist der Harness-Schalter `--exec close_next`.
* Zielgewichte nur bei Zustandswechsel (Ziel != zuletzt ausgegebene Position); das erste gueltige Signal immer.
* Das Panel beginnt am 2002-07-01 (IEF/SHY/TLT starten 2002-07-30, SPY 1993-01-29). Erstes Signal: Monatsende
  2003-07-31 (12 Monatsenden Vorlauf ab 2002-07-31). Ohne gueltige Historie oder ohne Kurs am Signaltag kein Gewicht.
* ^IRX ist eine Rendite in PROZENT (kein Preis) und bekommt nie ein Gewicht. Kosten 2 bp je Seite ueber SPEC["cost_bps"].

Varianten (vorab festgelegt, Robustheits-Checks, keine Auswahl der besten):
    skip1   12-1: Rendite und Zins von Monatsende T-12 bis Monatsende T-1 (letzter Monat zaehlt nicht)
    tlt     TLT statt IEF als Anleihe-Bein (ab 2002-07-30)
Die dritte Variante der Spezifikation (Ausfuehrung Schluss t+1 statt Eroeffnung) laeuft ueber `--exec close_next`.
"""
from __future__ import annotations

import pandas as pd

from qlab.data import Panel, load_panel
from strategies.xtsmom_us_switch_longcash import switch_weights

EQ = "SPY"
BOND = "IEF"
CASH = "SHY"
LONGBOND = "TLT"
RATE = "^IRX"
TRADABLE = [EQ, BOND, CASH, LONGBOND]
PANEL_START = "2002-07-01"

SPEC = {
    "id": "xtsmom_us_switch_longcash_etf",
    "name": "Cross-Asset-TSMOM USA: Long/Cash-Umschalter SPY/IEF/SHY, Live-Test auf ETFs",
    "family": "gap_crossasset_bond_equity_leadlag_signals",
    "tickers": TRADABLE + [RATE],
    "start": PANEL_START,
    "sources": [
        "Pitkaejaervi, Suominen, Vaittinen 2020, Cross-asset signals and time series momentum, "
        "https://doi.org/10.1016/j.jfineco.2019.02.011",
        "CXO Advisory 2017, Cross-asset Class Intrinsic Momentum, "
        "https://www.cxoadvisory.com/equity-premium/cross-asset-class-intrinsic-momentum",
    ],
    "params": {"equity": EQ, "bond": BOND, "cash": CASH, "rate": RATE, "lookback": 12, "skip": 0},
    "variants": {
        "skip1": {"skip": 1},
        "tlt": {"bond": LONGBOND},
    },
    "cost_bps": {t: 2.0 for t in TRADABLE},
}


def load() -> Panel:
    """SPY, IEF, SHY, TLT, ^IRX aus dem Cache, ab 2002-07-01; Zeilen ohne jeden ETF-Kurs (reine Zins-Tage) entfallen."""
    base = load_panel(TRADABLE + [RATE])                      # volle Cache-Historie, keine Kuerzung der Cache-Dateien
    keep = base.close[TRADABLE].notna().any(axis=1)
    sl = slice(pd.Timestamp(PANEL_START), None)
    close, open_ = base.close[keep].loc[sl], base.open[keep].loc[sl]
    return Panel(open_, close)


def weights(panel, equity: str = EQ, bond: str = BOND, cash: str = CASH, rate: str = RATE,
            lookback: int = 12, skip: int = 0) -> pd.DataFrame:
    """Zielgewichte (0/1, Summe 1 in jeder Zeile) auf [equity, bond, cash] bei Zustandswechsel am Monatsende."""
    return switch_weights(panel, equity, bond, rate, cash=cash, lookback=lookback, skip=skip)
