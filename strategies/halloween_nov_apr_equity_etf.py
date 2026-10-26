"""Halloween-Indikator / "Sell in May" — Live-Test auf dem investierbaren ETF SPY (ab 1993-01-29).

Zweites Modul zu `halloween_nov_apr_equity` (Langzeit-Test auf French-Gesamtmarkt): gleiche Regel (Kern
`halloween_weights` wird von dort importiert), aber gehandelt wird der SPY (Yahoo, angepasst = Total Return)
statt der French-Reihe. Regel und Quellen siehe das Hauptmodul bzw. research/families/calendar.md, 3.2.

    Entry am Schluss des letzten Handelstags im Oktober -> 100 % SPY; Exit am Schluss des letzten Handelstags
    im April -> 100 % Cash (die Engine verzinst mit dem French-RF); kein Hebel, kein Short.

Umsetzung im Engine-Vertrag:
* Signal am Schluss des letzten Handelstags t von Oktober bzw. April (month_end_flags, kausal), Handel zur Eröffnung
  von t+1 (Standard-Ausführung des Labs). Das ist die Sensitivität "Eröffnung des Folgetags" der Spezifikation und
  verliert die Über-Nacht-Lücke von t nach t+1; die MOC-Ausführung der Spezifikation (Handel zum Schluss von t) läuft
  über `scripts/run_all.py --exec close`.
* Die Reihe beginnt mit dem ersten Oktober-/April-Monatsende nach dem SPY-Start (1993-04-30, Exit; erster Entry
  1993-10-29). Es werden keine Gewichte auf NaN-Kurse vergeben.
* Kosten 2 bp je Seite (Spezifikation) für alle drei Titel über SPEC["cost_bps"]; Stresstest 1/5 bp über
  `--cost-mult 0.5` bzw. `2.5`. Steuern und Cash-Zins verbucht die Engine.

Varianten (vorab festgelegt, Robustheits-Checks, keine Auswahl der besten):
    cash_ief  Cash-Phase (Mai-Okt) in IEF (7-10J-Staatsanleihen) statt Geldmarkt; Zeilen erst, wenn SPY und IEF
              Kurse haben (IEF ab 2002-07-30, also erster Entry 2002-10-31)
    efa       Internationale Replikation: dieselbe Regel auf EFA (Industrieländer ex USA, Yahoo-Cache ab 2006-03);
              Cash bleibt der US-RF
Die DAX-Replikation (^GDAXI) und die Ausführungsart stehen im Hauptmodul bzw. im Harness (siehe dort).
"""
from __future__ import annotations

import pandas as pd

from strategies.halloween_nov_apr_equity import halloween_weights

ASSET = "SPY"
CASH = "IEF"
INTL = "EFA"

SPEC = {
    "id": "halloween_nov_apr_equity_etf",
    "name": "Halloween-Indikator: SPY Nov-Apr, Cash Mai-Okt, Live-Test auf SPY",
    "family": "calendar",
    "tickers": [ASSET, CASH, INTL],  # alle US-gelistet, gleicher Handelskalender (IEF/EFA nur für die Varianten)
    "start": "1993-01-01",           # SPY startet 1993-01-29
    "sources": [
        "Bouman, Jacobsen 2002, The Halloween Indicator, Sell in May and Go Away: Another Puzzle, "
        "https://pure.eur.nl/en/publications/the-halloween-indicator-sell-in-may-and-go-away-another-puzzle/",
        "Zhang, Jacobsen 2012, The Halloween Indicator: Everywhere and All the Time, "
        "https://research.nottingham.edu.cn/en/publications/the-halloween-indicator-sell-in-may-and-go-away-everywhere-and-al/fingerprints/",
    ],
    "params": {"asset": ASSET, "start_month": 11, "n_months": 6, "cash_asset": None},
    "variants": {
        "cash_ief": {"cash_asset": CASH},
        "efa": {"asset": INTL},
    },
    "cost_bps": {ASSET: 2.0, CASH: 2.0, INTL: 2.0},
}


def weights(panel, asset: str = ASSET, start_month: int = 11, n_months: int = 6,
            cash_asset: str | None = None) -> pd.DataFrame:
    """Zielgewichte (0 oder 1) auf `asset` am letzten Handelstag von Oktober (1) bzw. April (0); Rest ist Cash."""
    return halloween_weights(panel.close, asset, start_month=start_month, n_months=n_months, cash_asset=cash_asset)
