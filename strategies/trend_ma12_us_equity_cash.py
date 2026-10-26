"""Binärer Trendfilter US-Aktien / Cash, Neely-Signal MA(1,12) — Langzeit-Test 1930-2022 auf Ken-French-Gesamtmarkt.

Quellen der Signaldefinition: Neely, Rapach, Tu, Zhou 2014, "Forecasting the Equity Risk Premium:
The Role of Technical Indicators" (Gl. 4-6, monatliche MA-Signale); Faber 2007 (S&P-500-Abschnitt).
Die Binärregel "Signal = Position" ist eine Eigenübertragung (Neely nutzt die Signale als Regressoren).

Regel (festgelegt vor dem Backtest, aus research/families/macro.md, Abschnitt 3.1):
    P_m  = Schlusskurs des S&P-500-PREISINDEX (^GSPC) am letzten Handelstag jedes Monats m.
    MA12 = Mittel der letzten 12 Monatsend-Schlusskurse inkl. t.
    S_t  = 1, wenn P_t >= MA12_t (Neely MA(1,12)), sonst 0.
    Position = S_t * 100 % Aktienmarkt + (1 - S_t) * 100 % Cash. Kein Hebel, kein Short.

Umsetzung im Engine-Vertrag:
* Das Panel (`load()`) enthält zwei Spalten: "MKT" = US-Gesamtmarkt als Total-Return-Reihe aus
  Ken French (Mkt-RF + RF, täglich; open == close) und "^GSPC" = Preisindex nur als Signalquelle
  (nie ein Gewicht darauf). Cash verzinst die Engine selbst mit dem French-RF.
* Weil open == close, wird das Signal von Tag t zum Schlusskurs von t+1 umgesetzt; die neue Position
  verdient ab t+2 (genau wie in der Spezifikation).
* Monatsenden NUR über qlab.calendar.month_end_flags (kausal). Rolling-Fenster laufen nur über
  vergangene Monatsenden. Die Gewichte beginnen mit dem ersten Monatsende ab 1930-01-01 (Spec: "Start 1930").
* Gewichte nur ausgeben, wenn Signal und Aktienkurs gültig sind (NaN = nicht handelbar).

Kosten: 10 bp je Wechsel (Spec) statt der 5 bp Engine-Standard, über SPEC["cost_bps"]. Stresstest 50 bp
über `--cost-mult 5` im Harness. Steuern verbucht die Engine.

Varianten (vorab festgelegt, Robustheits-Checks, keine Auswahl der besten):
    sma10      P_t > Mittel der letzten 10 Monatsenden (Fabers S&P-Teil, strikt größer)
    ma2_12     Mittel(P_t, P_t-1) >= MA12  (Neely MA(2,12))
    signal_tr  gleiche Regel, aber das Signal kommt aus der Total-Return-Reihe (French-Gesamtmarkt)
               statt aus dem Preisindex ^GSPC
"""
from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from qlab.calendar import month_end_flags
from qlab.data import CACHE, Panel, french, panel_from_returns

ASSET = "MKT"
SIGNAL = "^GSPC"
FIRST_SIGNAL = "1930-01-01"          # Spezifikation: "Start: 1930"
GSPC_START = "1927-01-01"            # Yahoo liefert ^GSPC ab 1927-12-30
_GSPC_LONG_CACHE = CACHE / "long_idx_GSPC_1927.parquet"   # eigene Datei: der gemeinsame Cache startet erst 1990

SPEC = {
    "id": "trend_ma12_us_equity_cash",
    "name": "Trendfilter US-Aktien/Cash MA(1,12), Langzeit auf French-Gesamtmarkt",
    "family": "macro",
    "tickers": [ASSET, SIGNAL],      # Spalten des Panels aus load(); keine Yahoo-Ticker
    "start": FIRST_SIGNAL,
    "sources": [
        "Neely, Rapach, Tu, Zhou 2014, Forecasting the Equity Risk Premium: The Role of Technical Indicators, "
        "https://files.stlouisfed.org/files/htdocs/wp/2010/2010-008.pdf",
        "Faber 2007, A Quantitative Approach to Tactical Asset Allocation, SSRN 962461",
        "Goyal, Welch, Zafirov 2023, Equity Premium Prediction",
    ],
    "params": {"signal": SIGNAL, "asset": ASSET, "ma_short": 1, "ma_long": 12, "strict": False,
               "first_signal": FIRST_SIGNAL},
    "variants": {
        "sma10": {"ma_long": 10, "strict": True},
        "ma2_12": {"ma_short": 2},
        "signal_tr": {"signal": ASSET},
    },
    "cost_bps": {ASSET: 10.0},
}


# --------------------------------------------------------------------------------------
# Daten
# --------------------------------------------------------------------------------------

def _load_gspc_long(max_age_days: float = 30.0) -> pd.Series:
    """Schlusskurse des ^GSPC-Preisindex ab 1927-12-30 (eigener Cache, da data_cache/px__idx_GSPC erst 1990 beginnt)."""
    path = _GSPC_LONG_CACHE
    if path.exists() and (time.time() - path.stat().st_mtime) < max_age_days * 86400:
        return pd.read_parquet(path)["Close"]
    err = None
    try:
        import yfinance as yf

        df = yf.Ticker(SIGNAL).history(start=GSPC_START, auto_adjust=True, actions=False)
        if df is not None and len(df) > 0:
            df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
            df = df[["Close"]].astype(float)
            df = df[~df.index.duplicated(keep="last")].sort_index()
            df.to_parquet(path)
            return df["Close"]
        err = RuntimeError("leere Antwort für ^GSPC")
    except Exception as exc:  # Netz, Rate-Limit
        err = exc
    if path.exists():
        print(f"[data] WARNUNG: ^GSPC (lang) nicht aktualisierbar ({err}); alter Cache wird genutzt")
        return pd.read_parquet(path)["Close"]
    raise RuntimeError(f"^GSPC (lang) nicht ladbar: {err}")


def build_panel(mkt_ret: pd.Series, gspc_close: pd.Series) -> Panel:
    """Panel aus Gesamtmarkt-Renditen (French) plus Preisindex-Spalte als reiner Signalquelle.

    Der Preisindex wird auf die French-Handelstage gelegt, OHNE Lücken zu füllen (die Signalberechnung
    füllt selbst begrenzt nach vorn). open == close für beide Spalten.
    """
    base = panel_from_returns(pd.DataFrame({ASSET: mkt_ret}))
    g = gspc_close.reindex(base.close.index)
    close = base.close.copy()
    close[SIGNAL] = g
    open_ = base.open.copy()
    open_[SIGNAL] = g
    return Panel(open_, close)


def load() -> Panel:
    """Langzeit-Panel (French-Gesamtmarkt ab 1926-07 + ^GSPC ab 1927-12), ungekürzt (der Harness schneidet ab)."""
    fdf = french("F-F_Research_Data_Factors", daily=True)
    mret = (fdf["Mkt-RF"] + fdf["RF"]).astype(float)
    return build_panel(mret, _load_gspc_long())


# --------------------------------------------------------------------------------------
# Strategie
# --------------------------------------------------------------------------------------

def weights(panel, signal: str = SIGNAL, asset: str = ASSET, ma_short: int = 1, ma_long: int = 12,
            strict: bool = False, first_signal: str | None = FIRST_SIGNAL) -> pd.DataFrame:
    """Zielgewichte (0 oder 1) auf `asset` an jedem Monatsende mit gültigem Signal; Rest ist Cash."""
    idx = panel.close.index
    flags = month_end_flags(idx).to_numpy()
    # begrenztes Vorwärtsfüllen (kausal): Monatsende ohne eigenen Kurs nimmt den letzten Schluss der Vorwoche
    sig_px = panel.close[signal].ffill(limit=5)
    me = sig_px[flags]                                       # nur kausal erkannte Monatsenden
    fast = me.rolling(ma_short).mean()                       # inkl. aktuellem Monatsende
    slow = me.rolling(ma_long).mean()
    on = (fast > slow) if strict else (fast >= slow)
    valid = fast.notna() & slow.notna() & panel.close[asset][flags].notna()
    w = pd.DataFrame({asset: on.astype(float)}, index=me.index)[valid]
    if first_signal is not None:
        w = w.loc[pd.Timestamp(first_signal):]
    return w
