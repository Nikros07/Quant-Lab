"""Dreier-Komposit Duration-Timing (Carry + Trend + Value), long-only 10J-Treasury gegen Cash.

Langzeit-Test 1972-2022 auf einer SYNTHETISCHEN 10J-Par-Anleihe aus ^TNX/^IRX (Yahoo). Der
Live-Test auf den ETFs IEF/SHY steht im Schwestermodul `bond_composite_3sig_longonly_etf`.

Quellen: Newfound Research 2017, "Duration Timing with Style Premia" und 2018, "Timing Bonds with
Value, Momentum, and Carry" (siehe SPEC["sources"]). Evidenz laut research/families/
gap_bonds_duration_curve_carry_mom_value.md, Abschnitt 4.1: Die Quelle selbst findet KEIN Timing-
Signal, das statistisch über die durchschnittliche Positionierung hinaus trägt. Erwartung: Drawdown-
Filter, kein Alpha-Beleg.

Regel (festgelegt vor dem Backtest, aus research/strategie-kandidaten.json):
    y10 = ^TNX/100, y3m = ^IRX/100, D(y) = (1-(1+y/2)^-20)/y   (Par-Anleihe, halbjährlich)
    R10_t = y10_{t-1}/252 - D(y10_{t-1}) * (y10_t - y10_{t-1})   (synthetische 10J-Tagesrendite)
    Rc_t  = y3m_{t-1}/252                                       (Cash-Tagesrendite, nur fürs Signal)
Drei Stimmen am letzten Handelstag t_m jedes Monats (month_end_flags, kausal):
    (1) Carry: s = y10 - y3m. v_car = 1, wenn der Anteil der 2520 VORTAGSwerte von s, die unter s_{t_m}
        liegen, größer als 1/3 ist (Perzentil über die vorherigen 10 Jahre; nur Vergangenheit).
    (2) Trend: ex = ln(1+R10) - ln(1+Rc). v_trd = 1, wenn EWMA(span 21) UND EWMA(span 252) von ex > 0.
    (3) Value: infl = 12-Monats-Veränderung des CPI; pi_e = Mittel der 36 Monatswerte infl bis Monat m-2;
        real = y10 - pi_e; v_val = 1, wenn real über seinem EWMA-Anker (Halbwertszeit 36 Monate) liegt.
    w = (v_car + v_trd + v_val) / 3 in der 10J-Anleihe, 1-w Cash. Ungehebelt, nie short.
Das Signal vom Schluss t_m wird zum Schluss t_m+1 umgesetzt, die Position verdient ab t_m+2: Das Panel
hat open == close (panel_from_returns), die Engine handelt "zur Eröffnung" von t_m+1 = Schlusskurs.

Umsetzung im Engine-Vertrag:
* `load()` liefert ein Panel mit vier Spalten (alle open == close):
    "IEF"   handelbar: synthetische 10J-Par-Anleihe als Total-Return-Reihe (aus R10). Der Spaltenname ist
            ein reiner PROXY-NAME: Die Engine setzt für "IEF" keine Teilfreistellung an (Rentenfonds 0 %);
            ein neutraler Name wie "BOND10" würde im Steuermodell als Aktienfonds (30 %) behandelt.
    "^TNX", "^IRX"  reine Signalquellen in PROZENT (Yahoo-Einheit), nie ein Gewicht darauf.
    "PI_E"  reine Signalquelle in PROZENT: erwartete Inflation (Mittel der 36 Monatswerte der CPI-
            12-Monatsveränderung) mit 2 Monaten Veröffentlichungsverzögerung; ab dem Tag, an dem sie
            bekannt ist (siehe `cpi_step_column`). Nach dem letzten CPI-Wert wird sie NaN (kein stilles
            Weiterschreiben veralteter Daten) -> dann entstehen keine Gewichte.
* Cash verzinst die Engine mit dem French-RF (nicht mit ^IRX/252); ^IRX geht nur ins Signal ein.
* CPI: FRED (CPIAUCNS) ist nicht erreichbar, stattdessen der CPI aus Shillers ie_data (CPI-U, nicht
  saisonbereinigt, endet 2024-09). Für den Auswahlzeitraum bis 2022-12 reicht das; im Live-Betrieb
  muss eine aktuelle CPI-Quelle her.
* Das erste Signal entsteht, sobald ALLE drei Stimmen berechenbar sind (Carry braucht 2520 Vortage,
  daher ca. 1972). Auch die Einzelsignal-Varianten starten an diesem gemeinsamen Datum, damit die vier
  Läufe über denselben Zeitraum vergleichbar sind.

Kosten: Standard 5 bp je Seite (Spec); der Stresstest mit 20 bp läuft über `--cost-mult 4` im Harness.
Steuern verbucht die Engine.

Varianten (vorab festgelegt, Robustheits-Checks, keine Auswahl der besten):
    only_carry  nur die Carry-Stimme (w = 0 oder 1)
    only_trend  nur die Trend-Stimme (w = 0 oder 1)
    only_value  nur die Value-Stimme (w = 0 oder 1)
"""
from __future__ import annotations

import os
import time

import numpy as np
import pandas as pd

from qlab.calendar import month_end_flags
from qlab.data import CACHE, Panel, panel_from_returns, shiller

TRADING_DAYS = 252
ASSET = "IEF"                      # Proxy-Name der synthetischen 10J-Anleihe (Steuer: keine Teilfreistellung)
TNX, IRX, PIE = "^TNX", "^IRX", "PI_E"
SIGNAL_NAMES = ("carry", "trend", "value")
CARRY_MIN_SHARE = 0.95             # Mindestanteil gültiger Werte im 2520-Tage-Fenster (Datenlücken)
FFILL_LIMIT = 5                    # begrenztes (kausales) Vorwärtsfüllen von Signalreihen über Lücken
CPI_LAG_MONTHS = 2                 # CPI des Monats k gilt ab dem 1. Tag des Monats k+2 als bekannt (Spec: "bis m-2")
CPI_MAX_AGE_DAYS = 3650.0          # Shiller-Datei ist statisch; Auswahlzeitraum soll nicht vom Netz abhängen

_TNX_CACHE = CACHE / "bond3sig_idx_TNX_1962.parquet"   # eigener Cache: data_cache/px__idx_TNX beginnt erst 1990
_IRX_CACHE = CACHE / "bond3sig_idx_IRX_1960.parquet"

SPEC = {
    "id": "bond_composite_3sig_longonly",
    "name": "Dreier-Komposit Duration-Timing (Carry+Trend+Value), long-only 10J-Treasury vs. Cash, Langzeit",
    "family": "gap_bonds_duration_curve_carry_mom_value",
    "tickers": [ASSET, TNX, IRX, PIE],      # Spalten des Panels aus load(); keine Yahoo-Ticker
    "start": "1962-01-02",                  # ^TNX-Start; erstes Signal ca. 1972 (2520 Tage Carry-Historie)
    "sources": [
        "Newfound Research 2018, Timing Bonds with Value, Momentum, and Carry, "
        "https://blog.thinknewfound.com/2018/01/timing-bonds-value-momentum-carry/",
        "Newfound Research 2017, Duration Timing with Style Premia, "
        "https://blog.thinknewfound.com/2017/06/duration-timing-style-premia/",
    ],
    "params": {
        "signals": SIGNAL_NAMES,        # welche Stimmen in w eingehen (Komposit = alle drei)
        "carry_window": 2520,           # Vortage fürs Terminspread-Perzentil
        "carry_threshold": 1 / 3,       # Carry-Stimme = 1, wenn Perzentil > 1/3
        "ewma_fast": 21,                # Trend: EWMA-Span (Tage)
        "ewma_slow": 252,
        "anchor_halflife": 36,          # Value: Halbwertszeit des Realzins-Ankers (Monate)
        "asset": ASSET,
    },
    "variants": {
        "only_carry": {"signals": ("carry",)},
        "only_trend": {"signals": ("trend",)},
        "only_value": {"signals": ("value",)},
    },
}


# --------------------------------------------------------------------------------------
# Synthetische Anleihe
# --------------------------------------------------------------------------------------

def par_duration(y: pd.Series) -> pd.Series:
    """Modifizierte Duration einer 10J-Par-Anleihe mit halbjährlichem Kupon: (1-(1+y/2)^-20)/y. NaN für y <= 0."""
    d = (1.0 - (1.0 + y / 2.0) ** -20) / y
    return d.where(y > 0)


def synthetic_returns(tnx_pct: pd.Series, irx_pct: pd.Series) -> tuple[pd.Series, pd.Series]:
    """(R10, Rc): synthetische 10J-Tagesrendite und Cash-Tagesrendite aus ^TNX/^IRX (Prozentwerte).

    Beide nutzen nur die Rendite des Vortags als Ausgangspunkt und die Änderung bis heute.
    Kein Roll-down, keine Konvexität (siehe Familiennotiz).
    """
    y = tnx_pct / 100.0
    ym = y.shift(1)
    r10 = ym / TRADING_DAYS - par_duration(ym) * (y - ym)
    rc = irx_pct.shift(1) / 100.0 / TRADING_DAYS
    return r10, rc


# --------------------------------------------------------------------------------------
# Inflationserwartung (Value-Signal) aus dem monatlichen CPI
# --------------------------------------------------------------------------------------

def expected_inflation_monthly(cpi: pd.Series) -> pd.Series:
    """pi_e_k = Mittel der 36 Monatswerte infl_{k-35..k} (inkl. k), infl = CPI-Veränderung zum Vorjahresmonat.

    Ergebnis in Dezimalform (0.03 = 3 %), Index = PeriodIndex (Monat k). Lücken im Monatsraster bleiben
    NaN (und machen jedes 36er-Fenster, das sie enthält, ungültig).
    """
    c = cpi.dropna().astype(float).copy()
    c.index = pd.PeriodIndex(c.index, freq="M")
    full = pd.period_range(c.index.min(), c.index.max(), freq="M")
    c = c.reindex(full)
    infl = c / c.shift(12) - 1.0
    return infl.rolling(36).mean()


def cpi_step_column(pie_monthly: pd.Series, index: pd.DatetimeIndex, lag_months: int = CPI_LAG_MONTHS) -> pd.Series:
    """Tagesreihe der Inflationserwartung in PROZENT: der Wert des Monats k gilt ab dem 1. Tag von Monat k+lag.

    Am Monatsende m sieht eine Strategie damit pi_e bis Monat m-2 (Spec: "Mittel bis m-2"). Jeder Wert gilt
    bis zum Eintreffen des nächsten; nach dem LETZTEN Wert (und bei Lücken) wird die Reihe NaN statt veralteten
    Daten weiterzuschreiben. Vor dem ersten Wert ist sie NaN.
    """
    p = pie_monthly.copy()
    avail = (p.index + lag_months).to_timestamp(how="start")
    s = pd.Series(p.to_numpy(float) * 100.0, index=avail)
    expire = (p.index[-1] + lag_months + 1).to_timestamp(how="start")
    s = pd.concat([s, pd.Series([np.nan], index=pd.DatetimeIndex([expire]))])
    s = s[~s.index.duplicated(keep="first")].sort_index()
    return s.reindex(pd.DatetimeIndex(index), method="ffill")


# --------------------------------------------------------------------------------------
# Daten / Panel
# --------------------------------------------------------------------------------------

def _check_yield_units(s: pd.Series, name: str) -> None:
    """Yahoo hatte bei ^TNX historisch Einheitenwechsel (Faktor 10): Prozentwerte müssen plausibel sein."""
    if not (s.max() < 25.0 and s.min() > -2.0 and 0.5 < s.median() < 12.0):
        raise ValueError(f"{name}: Werte außerhalb des plausiblen Prozentbereichs "
                         f"(min {s.min():.3g}, median {s.median():.3g}, max {s.max():.3g}) — Einheit prüfen")


def _load_long_close(ticker: str, path, max_age_days: float = 30.0) -> pd.Series:
    """Schlusskurse (Prozent) eines Zins-Index in voller Yahoo-Historie, mit eigenem Cache (atomar geschrieben)."""
    if path.exists() and (time.time() - path.stat().st_mtime) < max_age_days * 86400:
        return pd.read_parquet(path)["Close"]
    err = None
    try:
        import yfinance as yf

        df = yf.Ticker(ticker).history(period="max", auto_adjust=False, actions=False)
        if df is not None and len(df) > 0:
            df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
            df = df[["Close"]].astype(float)
            df = df[~df.index.duplicated(keep="last")].sort_index()
            tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
            df.to_parquet(tmp)
            os.replace(tmp, path)
            return df["Close"]
        err = RuntimeError(f"leere Antwort für {ticker}")
    except Exception as exc:  # Netz, Rate-Limit
        err = exc
    if path.exists():
        print(f"[data] WARNUNG: {ticker} (lang) nicht aktualisierbar ({err}); alter Cache wird genutzt")
        return pd.read_parquet(path)["Close"]
    raise RuntimeError(f"{ticker} (lang) nicht ladbar: {err}")


def load_signal_inputs() -> tuple[pd.Series, pd.Series, pd.Series]:
    """(^TNX in %, ^IRX in %, monatliche erwartete Inflation als Dezimalzahl, PeriodIndex)."""
    tnx = _load_long_close(TNX, _TNX_CACHE).dropna()
    irx = _load_long_close(IRX, _IRX_CACHE).dropna()
    _check_yield_units(tnx, TNX)
    _check_yield_units(irx, IRX)
    pie = expected_inflation_monthly(shiller(max_age_days=CPI_MAX_AGE_DAYS)["cpi"])
    return tnx, irx, pie


def signal_columns(tnx: pd.Series, irx: pd.Series, pie_monthly: pd.Series, index: pd.DatetimeIndex) -> pd.DataFrame:
    """^TNX, ^IRX (Prozent) und PI_E (Prozent) auf `index`. Lücken werden höchstens FFILL_LIMIT Tage kausal gefüllt."""
    idx = pd.DatetimeIndex(index)

    def on(s: pd.Series) -> pd.Series:
        u = s.reindex(s.index.union(idx)).ffill(limit=FFILL_LIMIT)
        return u.reindex(idx)

    return pd.DataFrame({TNX: on(tnx), IRX: on(irx), PIE: cpi_step_column(pie_monthly, idx)}, index=idx)


def build_panel(tnx: pd.Series, irx: pd.Series, pie_monthly: pd.Series) -> Panel:
    """Panel (open == close): handelbare synthetische 10J-Anleihe plus die Signalspalten. Index = ^TNX-Handelstage."""
    idx = tnx.dropna().index
    sig = signal_columns(tnx, irx, pie_monthly, idx)
    r10, _ = synthetic_returns(sig[TNX], sig[IRX])
    base = panel_from_returns(pd.DataFrame({ASSET: r10}))
    close = base.close.copy()
    for c in (TNX, IRX, PIE):
        close[c] = sig[c]
    return Panel(close.copy(), close)


def load() -> Panel:
    """Langzeit-Panel ab 1962-01-02, ungekürzt (der Harness schneidet bei 2022-12-31 ab)."""
    return build_panel(*load_signal_inputs())


# --------------------------------------------------------------------------------------
# Stimmen (alle nur aus Daten bis einschließlich t_m)
# --------------------------------------------------------------------------------------

def carry_vote(spread: pd.Series, flags: np.ndarray, window: int = 2520, threshold: float = 1 / 3) -> pd.Series:
    """1.0, wenn der Anteil der `window` Vortagswerte unter s_t größer als `threshold` ist, sonst 0.0 (Monatsenden)."""
    v = spread.to_numpy(float)
    out = np.full(len(v), np.nan)
    min_n = int(np.ceil(CARRY_MIN_SHARE * window))
    for i in np.flatnonzero(flags):
        if i < window or not np.isfinite(v[i]):
            continue
        past = v[i - window:i]                            # nur Vortage, ohne den heutigen Wert
        past = past[np.isfinite(past)]
        if len(past) < min_n:
            continue
        out[i] = float((past < v[i]).mean() > threshold)
    return pd.Series(out, index=spread.index)[flags]


def trend_vote(tnx_pct: pd.Series, irx_pct: pd.Series, flags: np.ndarray, fast: int = 21, slow: int = 252) -> pd.Series:
    """1.0, wenn beide EWMAs (Span fast/slow) der 10J-Überschussrendite ln(1+R10)-ln(1+Rc) > 0 sind (Monatsenden)."""
    r10, rc = synthetic_returns(tnx_pct, irx_pct)
    ex = np.log1p(r10) - np.log1p(rc)
    ef = ex.ewm(span=fast, adjust=False, min_periods=fast).mean()
    es = ex.ewm(span=slow, adjust=False, min_periods=slow).mean()
    ok = ef.notna() & es.notna()
    vote = ((ef > 0) & (es > 0)).astype(float).where(ok)
    return vote[flags]


def value_vote(tnx_pct: pd.Series, pie_pct: pd.Series, flags: np.ndarray, halflife: int = 36) -> pd.Series:
    """1.0, wenn der Realzins y10 - pi_e über seinem EWMA-Anker (Halbwertszeit in Monaten) liegt (Monatsenden).

    Der Anker läuft über die Monatsend-Stichproben; sein Wert inkl. aktuellem Monat bewertet exakt wie der
    Vormonatsanker (real > ewma_t  <=>  real > ewma_{t-1}). Gültig erst nach `halflife` Monaten Historie.
    """
    real = (tnx_pct - pie_pct)[flags]
    anchor = real.ewm(halflife=halflife, adjust=False, min_periods=halflife).mean()
    ok = real.notna() & anchor.notna()
    return (real > anchor).astype(float).where(ok)


def votes(panel, carry_window: int = 2520, carry_threshold: float = 1 / 3, ewma_fast: int = 21,
          ewma_slow: int = 252, anchor_halflife: int = 36) -> pd.DataFrame:
    """Die drei Stimmen (carry, trend, value) an den kausal erkannten Monatsenden; NaN = noch nicht berechenbar."""
    idx = panel.close.index
    flags = month_end_flags(idx).to_numpy()
    tnx, irx, pie = panel.close[TNX], panel.close[IRX], panel.close[PIE]
    return pd.DataFrame({
        "carry": carry_vote((tnx - irx) / 100.0, flags, carry_window, carry_threshold),
        "trend": trend_vote(tnx, irx, flags, ewma_fast, ewma_slow),
        "value": value_vote(tnx, pie, flags, anchor_halflife),
    })


# --------------------------------------------------------------------------------------
# Strategie
# --------------------------------------------------------------------------------------

def composite(v: pd.DataFrame, signals=SIGNAL_NAMES) -> pd.Series:
    """Anleihegewicht = Mittel der gewählten Stimmen (alle drei: Summe/3; eine Stimme: 0 oder 1)."""
    signals = tuple(signals)
    if not signals or any(s not in SIGNAL_NAMES for s in signals):
        raise ValueError(f"signals muss eine nichtleere Teilmenge von {SIGNAL_NAMES} sein, nicht {signals}")
    return v[list(signals)].mean(axis=1)


def weights(panel, signals=SIGNAL_NAMES, carry_window: int = 2520, carry_threshold: float = 1 / 3,
            ewma_fast: int = 21, ewma_slow: int = 252, anchor_halflife: int = 36, asset: str = ASSET) -> pd.DataFrame:
    """Zielgewicht auf `asset` (0, 1/3, 2/3 oder 1; bei nur einer Stimme 0 oder 1) an jedem Monatsende, Rest ist Cash.

    Eine Zeile entsteht nur, wenn alle drei Stimmen berechenbar sind (gemeinsamer Start für alle Varianten)
    und der Kurs von `asset` gültig ist.
    """
    v = votes(panel, carry_window, carry_threshold, ewma_fast, ewma_slow, anchor_halflife)
    w = composite(v, signals)
    flags = month_end_flags(panel.close.index).to_numpy()
    valid = v.notna().all(axis=1) & panel.close[asset][flags].notna()
    return pd.DataFrame({asset: w}, index=v.index)[valid]
