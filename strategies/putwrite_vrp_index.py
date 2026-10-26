"""Cash-gedeckter ATM-Put-Verkauf auf den S&P 500 (Cboe PutWrite Index ^PUT) — Index-Ebene, kein Signal.

Quellen: Bondarenko 2019, "Historical Performance of Put-Writing Strategies" (Cboe White Paper; nur die
Cboe-Zusammenfassungsseite gelesen); Carr, Wu 2009, "Variance Risk Premia", Review of Financial Studies 22(3).
Regeln aus research/families/volpremium.md, Abschnitt 5.1.

Mechanismus: Varianzrisikoprämie (implizite Vol > realisierte Vol). Der Index verkauft einmal im Monat einen
1-Monats-ATM-Put auf den S&P 500, hält die Sicherheit zu 100 % in T-Bills und hält bis Verfall. Ein Teil der
Rendite ist Aktienbeta (laut Cboe-Seite 0.56), nur ein Rest ist VRP-Alpha.

Regel (festgelegt vor dem Backtest, Parameter aus der Spezifikation, keine Optimierung):
    w_PUT = 100 % ^PUT, dauerhaft, kein Rebalancing, kein Timing-Filter. Rendite = ^PUT-Tagesrendite.
    Kostenabzug c Prozentpunkte p.a. (Lab-Annahme, der Index ist brutto): Basis c = 0.50.
    Die Strategie liefert deshalb genau EINE Zeile: Gewicht 1.0 am ersten Tag mit gültigem Kurs.
    Danach bleibt die Zeile weg (Engine: nichts tun); bei einem einzigen Titel gibt es keine Drift.

Umsetzung im Engine-Vertrag:
* Das Panel (`load()`) enthält ausschließlich Index-/Hilfsreihen, keine handelbaren Ticker:
    PUT_C025 / PUT_C050 / PUT_C100  ^PUT als Total-Return-Reihe, je Tag um c/252 gekürzt (c = 0.25 / 0.50 /
                                    1.00 Prozentpunkte p.a.). Die Kostenvarianten sind damit drei Spalten; welche
                                    Spalte ein Lauf handelt, bestimmt der Parameter `cost_pp`.
    SPY                             Schlusskurs (angepasst), nur für den Pflichtvergleich (Beta-Mix), nie ein
                                    Gewicht der Hauptstrategie.
    RF                              Cash-Index aus dem Fama-French-RF (täglich), nur für den Beta-Mix.
  open == close für alle Spalten: ein Signal am Schluss von Tag t wird zum Schlusskurs von t+1 umgesetzt und
  verdient ab t+2 (konservativ, einheitlich mit den anderen Index-Strategien).
* Der Kalender des Panels ist der Kalender von ^PUT (nicht die Vereinigung mit SPY). Der Cboe-Index fehlt an
  7 SPY-Handelstagen (1997-01-31, 1997-02-03, 1997-11-18, 2001-01-12, 2004-03-16, 2007-05-11, 2009-03-23).
  Mit der Vereinigung würde die Engine die Rendite über eine NaN-Lücke verschlucken (NaN = Kurs unverändert,
  der Folgetag hat keinen Vortageskurs); auf dem ^PUT-Kalender wird jede Rendite über die Lücke korrekt
  verbucht (Rendite zweier Tage, Kostenabzug trotzdem nur einmal c/252: Wirkung < 0.003 pp p.a.).
* Die Engine verbucht zusätzlich 5 bp Standardkosten auf den einmaligen Einstieg und verzinst Cash mit RF;
  Steuern verbucht sie ebenfalls (die Steuerrechnung des Harness behandelt die Spalte als Aktienfonds mit 30 %
  Teilfreistellung — für Stillhalterprämien/Termingeschäfte nur eine grobe Näherung).
* Fehlende Kurse (NaN) = nicht handelbar: das Gewicht wird erst am ersten Tag mit gültigem Kurs vergeben.

Daten-Eigenheit (nicht korrigiert, nur dokumentiert): Der Yahoo-Verlauf von ^PUT enthält am 2020-03-13 (+35.3 %)
und 2020-03-16 (-28.4 %) zwei Tageswerte, die gegen SPY (+8.5 % / -10.9 %) unplausibel hoch ausschlagen
(Index-Bewertung im Verfall/Rollen während der Limit-Tage). Über beide Tage zusammen ist die Rendite plausibel
(2020-03-12 -> 2020-03-16: -3.1 % bei SPY -2.6 %). Das verzerrt tagesbasierte Vol-/Sharpe-Kennzahlen leicht,
nicht die Gesamtrendite. Es wird nichts geglättet oder entfernt.

Pflichtvergleich (b): `beta_matched_weights` liefert den beta-gematchten SPY/Cash-Mix auf demselben Panel
(Gewicht auf SPY = expandierende OLS-Steigung der monatlichen Exzessrenditen ^PUT auf SPY, mindestens 36
Monate; Rest Cash). Er ist KEINE registrierte Strategie, der Harness läuft ihn nicht; er steht für die
spätere Auswertung (Abbruchkriterium: Alpha-t-Wert < 1.65 nach 0.50 pp Kosten) bereit.

Varianten (vorab festgelegt, Robustheits-Checks, keine Auswahl der besten):
    cost_025   Kosten 0.25 pp p.a.
    cost_100   Kosten 1.00 pp p.a.
    from_2008  Teilstichprobe: Einstieg erst am ersten Handelstag ab 2008-01-01 (Entscheidungsrelevanz)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from qlab.calendar import month_end_flags
from qlab.data import Panel, french, load_ticker

TRADING_DAYS = 252
COST_GRID_PP = (0.25, 0.50, 1.00)        # Kostenabzug in Prozentpunkten p.a. (Basis: 0.50)
SPY = "SPY"
CASH = "RF"
FIRST_DATE = "1996-08-02"                # ^PUT startet bei Yahoo am 1996-08-02

SPEC = {
    "id": "putwrite_vrp_index",
    "name": "Cash-gedeckter ATM-Put-Verkauf auf den S&P 500 (Cboe PutWrite Index ^PUT), Index-Ebene",
    "family": "volpremium",
    "tickers": ["PUT_C025", "PUT_C050", "PUT_C100", SPY, CASH],   # Spalten des Panels aus load(); keine Yahoo-Ticker
    "start": FIRST_DATE,
    "sources": [
        "Bondarenko 2019, Historical Performance of Put-Writing Strategies (Cboe), "
        "https://www.cboe.com/insights/posts/white-paper-shows-volatility-risk-premium-facilitated-higher-risk-adjusted-returns-for-put-index/",
        "Carr, Wu 2009, Variance Risk Premia, https://ideas.repec.org/a/oup/rfinst/v22y2009i3p1311-1341..html",
    ],
    "params": {"cost_pp": 0.50, "first_signal": None},
    "variants": {
        "cost_025": {"cost_pp": 0.25},
        "cost_100": {"cost_pp": 1.00},
        "from_2008": {"first_signal": "2008-01-01"},
    },
}


# --------------------------------------------------------------------------------------
# Daten
# --------------------------------------------------------------------------------------

def cost_column(cost_pp: float) -> str:
    """Spaltenname der ^PUT-Reihe mit `cost_pp` Prozentpunkten Kostenabzug p.a. (0.5 -> 'PUT_C050')."""
    return f"PUT_C{int(round(float(cost_pp) * 100)):03d}"


def build_panel(put_close: pd.Series, spy_close: pd.Series, rf_daily: pd.Series,
                cost_grid_pp=COST_GRID_PP) -> Panel:
    """Panel aus ^PUT-Schlusskursen (bestimmen den Kalender), SPY-Schlusskursen und täglichem RF (Dezimalrendite).

    Keine Netzwerk-/Cache-Zugriffe (wird von `load()` und den Tests genutzt). open == close.
    Die ^PUT-Rendite zwischen zwei aufeinanderfolgenden gültigen Kursen wird um c/252 gekürzt; Tage ohne
    gültigen ^PUT-Kurs bleiben NaN (nicht handelbar), die Rendite über die Lücke geht nicht verloren.
    """
    put = pd.Series(put_close, dtype=float).sort_index()
    put = put[~put.index.duplicated(keep="last")]
    idx = put.index
    valid = put.dropna()
    r_gross = valid / valid.shift(1) - 1.0                      # NaN beim ersten gültigen Kurs
    cols: dict[str, pd.Series] = {}
    for c in cost_grid_pp:
        r_net = (r_gross - c / 100.0 / TRADING_DAYS).fillna(0.0)
        lvl = 100.0 * (1.0 + r_net).cumprod()
        cols[cost_column(c)] = lvl.reindex(idx)
    close = pd.DataFrame(cols, index=idx)
    close[SPY] = pd.Series(spy_close, dtype=float).reindex(idx)
    rf = pd.Series(rf_daily, dtype=float).sort_index().fillna(0.0)
    rf_lvl = 100.0 * (1.0 + rf).cumprod()                       # Cash-Index auf dem vollen French-Kalender
    close[CASH] = rf_lvl.reindex(rf_lvl.index.union(idx)).ffill().reindex(idx)
    return Panel(close.copy(), close)


def load() -> Panel:
    """Panel aus ^PUT (Yahoo, ab 1996-08-02), SPY und French-RF, ungekürzt (der Harness schneidet ab)."""
    put = load_ticker("^PUT")["Close"]
    spy = load_ticker(SPY)["Close"]
    rf = french("F-F_Research_Data_Factors", daily=True)["RF"]
    return build_panel(put, spy, rf)


# --------------------------------------------------------------------------------------
# Strategie
# --------------------------------------------------------------------------------------

def weights(panel, cost_pp: float = 0.50, first_signal: str | None = None) -> pd.DataFrame:
    """Gewicht 1.0 auf der ^PUT-Spalte mit `cost_pp` Kostenabzug, EINE Zeile am ersten Tag mit gültigem Kurs.

    `first_signal`: frühestes Signaldatum (Teilstichprobe); der Einstieg ist der erste Handelstag ab diesem Datum
    mit gültigem Kurs. Ohne gültigen Kurs (oder Daten erst nach `first_signal`) bleibt das Ergebnis leer.
    """
    col = cost_column(cost_pp)
    if col not in panel.close.columns:
        raise KeyError(f"Panel ohne Spalte {col} (Kostenabzug {cost_pp} pp nicht vorgesehen; Raster {COST_GRID_PP})")
    px = panel.close[col]
    ok = px.notna().to_numpy()
    if first_signal is not None:
        ok = ok & (px.index >= pd.Timestamp(first_signal))
    pos = np.flatnonzero(ok)
    if len(pos) == 0:
        return pd.DataFrame({col: np.asarray([], dtype=float)}, index=pd.DatetimeIndex([]))
    return pd.DataFrame({col: [1.0]}, index=pd.DatetimeIndex([px.index[pos[0]]]))


# --------------------------------------------------------------------------------------
# Pflichtvergleich (b): beta-gematchter SPY/Cash-Mix (keine registrierte Strategie)
# --------------------------------------------------------------------------------------

def beta_matched_weights(panel, cost_pp: float = 0.50, min_months: int = 36, spy: str = SPY,
                         cash: str = CASH, first_signal: str | None = None) -> pd.DataFrame:
    """Monatsende-Gewicht auf SPY = expandierende OLS-Steigung der monatlichen Exzessrenditen ^PUT auf SPY.

    Beta (mit Achsenabschnitt) aus allen Monatsrenditen bis einschließlich dieses Monatsendes, mindestens
    `min_months` Beobachtungen; Exzess = Rendite minus RF-Rendite desselben Zeitraums. Rest ist Cash (die Engine
    verzinst ihn). Lab-Ergänzung: Begrenzung auf [0, 1] (kein Hebel, kein Short; das Beta liegt erwartungsgemäß
    bei ~0.5). Die Kostenspalte ändert die Steigung praktisch nicht. Monatsenden nur über month_end_flags;
    nur Monatsenden mit gültigem SPY-Kurs bekommen ein Gewicht.
    """
    px = panel.close
    put_col = cost_column(cost_pp)
    flags = month_end_flags(px.index).to_numpy()
    me = px.loc[flags, [put_col, spy, cash]]
    ret = me / me.shift(1) - 1.0                                # Rendite zwischen aufeinanderfolgenden Monatsenden
    y = (ret[put_col] - ret[cash]).to_numpy(float)
    x = (ret[spy] - ret[cash]).to_numpy(float)
    m = np.isfinite(x) & np.isfinite(y)
    xv, yv = np.where(m, x, 0.0), np.where(m, y, 0.0)
    n = np.cumsum(m)
    sx, sy = np.cumsum(xv), np.cumsum(yv)
    sxx, sxy = np.cumsum(xv * xv), np.cumsum(xv * yv)
    with np.errstate(divide="ignore", invalid="ignore"):
        cov = sxy - sx * sy / n
        var = sxx - sx * sx / n
        beta = np.where((n >= min_months) & (var > 1e-18), cov / var, np.nan)
    keep = np.isfinite(beta) & me[spy].notna().to_numpy()
    out = pd.DataFrame({spy: np.clip(beta[keep], 0.0, 1.0)}, index=me.index[keep])
    if first_signal is not None:
        out = out.loc[pd.Timestamp(first_signal):]
    return out
