"""Low-Volatility / Low-Beta, Long-only (defensiv) — Faktor-Ebene auf Ken-French-Portfolios, Langzeit ab 1963-07.

Hauptmodul der Strategie `lowvol_defensive_longonly`. Der ETF-Realitaets-Check (USMV/SPLV Buy&Hold gegen SPY,
Sektor-Proxy als Variante) steht im Zweitmodul `lowvol_defensive_longonly_etf`.

Quellen: Blitz/van Vliet 2007 (The Volatility Effect), Baker/Bradley/Wurgler 2011 (Benchmarks as Limits to
Arbitrage). Die Spezifikation steht in research/strategie-kandidaten.json (Eintrag `lowvol_defensive_longonly`)
und research/families/lowrisk.md (Abschnitt S2).

Regel (Spezifikation, unveraendert uebernommen): KEIN Signal, KEINE Optimierung.
    100 % im wertgewichteten Quintil mit dem niedrigsten Beta ("Lo 20" aus Ken French "Portfolios_Formed_on_BETA",
    Tabelle 0 = Value Weighted Returns, monatlich), Long-only, kein Hebel, kein Cash. Buy&Hold ab dem ersten
    Datenpunkt (Juli 1963). Die Bewertung ist "niedrigstes Quintil minus RF gegen Mkt-RF" (CAPM-Alpha, Sharpe);
    die Stichprobe wird bei 2007/2008 geteilt (`SPLIT_DATE`, Helfer `capm_alpha_split`).
    Die Sortierung nach Beta und die interne Neugewichtung der Portfolios besorgt Ken French; sie ist nicht
    Teil dieses Moduls (Look-ahead-Freiheit der Sortierung liegt bei der Datenquelle und wurde hier nicht geprueft).

Umsetzung im Engine-Vertrag:
* French liefert nur MONATSrenditen (Datum = 1. des Monats). Damit der Harness (Tages-Benchmarks, Tages-
  Annualisierung, Bootstrap-Bloecke) sauber vergleicht, legt `monthly_to_month_end_grid` jede Monatsrendite
  auf den LETZTEN HANDELSTAG ihres Monats im Tagesraster der Fama-French-Tagesfaktoren; an allen anderen Tagen
  ist die Rendite 0. Eine Monatsrendite wird damit erst am Monatsende sichtbar (kein Blick in die Zukunft);
  Innermonats-Verluste sind unsichtbar (MaxDD/Vol/Beta auf Tagesbasis sind fuer diese Reihe NICHT belastbar,
  CAGR, Monats-Sharpe und Jahresrenditen schon).
* `load()` liefert ein Panel ueber `panel_from_returns` (open == close): Signal am Schluss von t, die Engine
  kauft zum Schlusskurs von t+1. Das Panel hat zwei Spalten: BETA_COL (Hauptlauf) und VAR_COL (Variante).
* Gewichte: genau eine Zeile am ersten Tag mit gueltigem Kurs der gewaehlten Spalte (NaN = nicht handelbar).

Kosten: Standard (5 bps je Seite) fuer das einmalige Kaufen. Umschlagkosten INNERHALB der French-Portfolios
sind nicht modelliert (reine Faktor-Ebene, brutto). Steuern verbucht die Engine.

Variante (vorab festgelegt, Robustheits-Check, keine Auswahl der besten):
    var   Portfolios_Formed_on_VAR (Sortierung nach Varianz statt Beta), sonst identische Regel.
Die uebrigen vorregistrierten Varianten (SPLV statt USMV, Sektor-Proxy) stehen im Zweitmodul `..._etf`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from qlab.calendar import month_end_flags
from qlab.data import Panel, french, panel_from_returns

QUINTILE = "Lo 20"                       # niedrigstes Quintil (Spaltenname in den French-Dateien)
BETA_COL = "BETA Lo 20"
VAR_COL = "VAR Lo 20"
SPLIT_DATE = "2008-01-01"                # Stichprobenteilung: Monate < 2008 gegen Monate >= 2008
IS_END = "2022-12-31"                    # Auswahlzeitraum; Daten ab 2023 (Holdout) werden nie geladen

SPEC = {
    "id": "lowvol_defensive_longonly",
    "name": "Low-Vol Long-only (defensiv), Faktor-Ebene: French-Beta-Quintil (Lo 20), Buy&Hold",
    "family": "lowrisk",
    "tickers": [BETA_COL, VAR_COL],      # Spalten des Panels aus load(); keine Yahoo-Ticker
    "start": "1963-07-01",               # French Portfolios_Formed_on_BETA/VAR beginnen 1963-07
    "sources": [
        "Blitz, van Vliet 2007, The Volatility Effect: Lower Risk Without Lower Return, https://papers.ssrn.com/abstract=980865",
        "Baker, Bradley, Wurgler 2011, Benchmarks as Limits to Arbitrage: Understanding the Low-Volatility Anomaly, https://papers.ssrn.com/abstract=1745108",
        "Ken French Data Library, Portfolios Formed on Market Beta / on Variance (value weighted, monthly)",
    ],
    "params": {"column": BETA_COL},
    "variants": {
        "var": {"column": VAR_COL},      # Sortierung nach Varianz statt Beta
    },
}


# --------------------------------------------------------------------------------------
# Daten
# --------------------------------------------------------------------------------------

def monthly_to_month_end_grid(monthly: pd.DataFrame, grid: pd.DatetimeIndex) -> pd.DataFrame:
    """Monatsrenditen (Index = beliebiger Tag im Monat, bei French der 1.) auf ein Handelstag-Raster legen.

    Jede Monatsrendite steht am LETZTEN Raster-Tag ihres Monats, alle anderen Tage zwischen der ersten und der
    letzten gueltigen Monatsrendite einer Spalte haben Rendite 0.0 (Kurs konstant); davor und danach NaN
    (nicht handelbar). Monate ohne Raster-Tage werden verworfen. Ist der letzte Monat des Rasters unvollstaendig
    (letzter Raster-Tag laut NYSE-Kalender kein Monatsende), wird seine Rendite NICHT gebucht.
    """
    grid = pd.DatetimeIndex(grid).sort_values()
    out = pd.DataFrame(np.nan, index=grid, columns=monthly.columns, dtype=float)
    if len(grid) == 0 or len(monthly) == 0:
        return out.iloc[0:0]
    per = grid.to_period("M")
    last_day = pd.Series(grid, index=per)
    last_day = last_day[~last_day.index.duplicated(keep="last")]           # letzter Datentag je Monat
    if not bool(month_end_flags(grid[-40:]).iloc[-1]):                       # Rasterende mitten im Monat
        last_day = last_day.iloc[:-1]
    mm = monthly.copy()
    mm.index = pd.DatetimeIndex(mm.index).to_period("M")
    mm = mm[~mm.index.duplicated(keep="last")]
    mm = mm[mm.index.isin(last_day.index)].sort_index()
    for col in mm.columns:
        s = mm[col]
        first_m, last_m = s.first_valid_index(), s.last_valid_index()
        if first_m is None:
            continue
        start_day = grid[grid >= first_m.start_time][0]                      # erster Handelstag des ersten Monats
        sel = (grid >= start_day) & (grid <= last_day.loc[last_m])
        out.loc[sel, col] = 0.0
        span = s.loc[first_m:last_m]
        out.loc[last_day.loc[span.index].to_numpy(), col] = span.to_numpy(dtype=float)
    return out.dropna(how="all")


def load() -> Panel:
    """Panel aus den French-Monatsrenditen "Lo 20" (BETA und VAR), auf das Tagesraster der French-Faktoren gelegt.

    Nicht abgeschnitten: das macht der Harness (Holdout ab 2023 wird dort entfernt).
    """
    grid = french("F-F_Research_Data_Factors", daily=True).index           # nur Handelstage-Raster
    beta = french("Portfolios_Formed_on_BETA", table=0)[QUINTILE].astype(float)
    var = french("Portfolios_Formed_on_VAR", table=0)[QUINTILE].astype(float)
    monthly = pd.DataFrame({BETA_COL: beta, VAR_COL: var})
    return panel_from_returns(monthly_to_month_end_grid(monthly, grid))


# --------------------------------------------------------------------------------------
# Strategie
# --------------------------------------------------------------------------------------

def weights(panel, column: str = BETA_COL) -> pd.DataFrame:
    """Buy&Hold: 100 % auf `column`, eine einzige Zeile am ersten Tag mit gueltigem Kurs (NaN = nicht handelbar)."""
    first = panel.close[column].first_valid_index()
    if first is None:
        return pd.DataFrame({column: np.array([], dtype=float)}, index=pd.DatetimeIndex([]))
    return pd.DataFrame({column: [1.0]}, index=pd.DatetimeIndex([first]))


# --------------------------------------------------------------------------------------
# Auswertungshelfer (Faktor-Ebene, monatlich; kein Teil der Strategie)
# --------------------------------------------------------------------------------------

def capm_alpha(excess_strategy: pd.Series, excess_market: pd.Series) -> dict:
    """OLS  y = a + b * x + e  mit y = Strategie minus RF, x = Mkt-RF (monatlich). Gibt Alpha, t-Wert, Beta, n zurueck.

    t-Wert klassisch (homoskedastisch, n - 2 Freiheitsgrade). Alpha pro Monat und mal 12 (`alpha_ann`).
    """
    df = pd.concat([excess_strategy.rename("y"), excess_market.rename("x")], axis=1, join="inner").dropna()
    n = len(df)
    if n < 12:
        return {"n": n, "alpha_m": float("nan"), "alpha_ann": float("nan"), "t_alpha": float("nan"), "beta": float("nan")}
    x = np.column_stack([np.ones(n), df["x"].to_numpy(float)])
    y = df["y"].to_numpy(float)
    xtx_inv = np.linalg.inv(x.T @ x)
    coef = xtx_inv @ (x.T @ y)
    resid = y - x @ coef
    s2 = float(resid @ resid) / (n - 2)
    se_alpha = float(np.sqrt(s2 * xtx_inv[0, 0]))
    return {"n": n, "alpha_m": float(coef[0]), "alpha_ann": float(coef[0]) * 12.0,
            "t_alpha": float(coef[0]) / se_alpha if se_alpha > 0 else float("nan"), "beta": float(coef[1])}


def capm_alpha_split(lowvol_total: pd.Series, mkt_rf: pd.Series, rf: pd.Series, split: str = SPLIT_DATE) -> dict:
    """CAPM-Alpha (Lo 20 minus RF gegen Mkt-RF) fuer die ganze Stichprobe sowie vor/ab `split` (Monatsdaten)."""
    ex = lowvol_total - rf.reindex(lowvol_total.index)
    cut = pd.Timestamp(split)
    return {"full": capm_alpha(ex, mkt_rf),
            "pre": capm_alpha(ex[ex.index < cut], mkt_rf),
            "post": capm_alpha(ex[ex.index >= cut], mkt_rf)}


def alpha_split_from_french(dataset: str = "Portfolios_Formed_on_BETA", split: str = SPLIT_DATE,
                            end: str = IS_END) -> dict:
    """Wie `capm_alpha_split`, aber direkt aus den French-Monatsdateien; schneidet bei `end` ab (Holdout bleibt zu)."""
    port = french(dataset, table=0)[QUINTILE].astype(float).loc[:end]
    fac = french("F-F_Research_Data_Factors").loc[:end]
    return capm_alpha_split(port, fac["Mkt-RF"], fac["RF"], split=split)
