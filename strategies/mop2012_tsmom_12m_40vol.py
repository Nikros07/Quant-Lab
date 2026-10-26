"""Moskowitz-Ooi-Pedersen (2012) Time-Series Momentum — 12-Monats-Vorzeichen, 40 % Einzel-Vol-Ziel.

Referenz-Replikation (ETF12-Proxy statt 58 Futures). Dient als Benchmark fuer alle Trendfolger,
nicht als Echtgeld-Kandidat (Long/Short mit Hebel ist fuer Privatanleger nicht umsetzbar).
Quellen: Moskowitz, Ooi, Pedersen 2012, Time series momentum, JFE 104(2);
         Hurst, Ooi, Pedersen 2017, A Century of Evidence on Trend-Following Investing.

Regel (am Monatsende t, je Asset i des Universums ETF12):
    ER12_i = 12-Monats-Exzessrendite = (P_t / P_{t-12M} - 1) - kumulierter ^IRX-Zins ueber dieselben 12 Monate
    sigma_i = sqrt(261 * EWMA(exzess_ret^2))        # com = 60 Tage, Tagesrenditen abzueglich Tageszins
    MODE = LS (Hauptlauf, Papier):  pos_i = sign(ER12_i) * 0.40 / sigma_i
    MODE = LF (Long/Flat, Zweitlauf): pos_i = 1[ER12_i > 0] * 0.40 / sigma_i, Summe der Gewichte auf <= 1 gekappt
    w_i = pos_i / N_t   (N_t = Zahl der Assets mit gueltigem Signal), Bruttohebel (LS) auf <= 3 gekappt
    Nicht auf Portfolio-Vol skaliert (ausser in der Variante `portvol10`).

Kausalitaet: Alles nur aus Daten bis einschliesslich Tag t (Rolling/EWMA/shift nach hinten); Monatsenden
ueber qlab.calendar.month_end_flags. Das Signal entsteht am Schlusskurs t, die Engine handelt zur
Eroeffnung t+1 (Spezifikation: Schluss t+1 -> `run_all.py --exec close_next`).

^IRX (3-Monats-Zins, PROZENT) ist kein handelbarer Preis: er dient nur als Zinsquelle und bekommt nie Gewicht.
Kosten (10 bp je Seite laut Spezifikation) stehen in SPEC["cost_bps"]; die Engine verbucht sie.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from qlab.calendar import month_end_flags
from qlab.data import Panel, load_panel

UNIVERSE = ["SPY", "EFA", "EEM", "IEF", "TLT", "VNQ", "GLD", "DBC", "FXE", "FXY", "FXB", "FXA"]
RATE_TICKER = "^IRX"

RF_DAYS = 252            # ^IRX (Prozent p.a.) -> Zins je Handelstag
VOL_ANN = 261            # Annualisierungsfaktor der Vol (MOP 2012)
VOL_MIN_PERIODS = 120    # EWMA-Vol braucht mindestens ~ein halbes Jahr Tageswerte
MIN_SIGMA = 1e-8         # Schutz gegen Division durch ~0 (Asset ohne Kursbewegung = nicht handelbar)
LF_CAP = 1.0             # LF: Summe der Gewichte <= 1 (proportional gekappt)
COV_WINDOW = 756         # Variante portvol10: Kovarianz der letzten 756 Handelstage (Hurst-Ooi-Pedersen)
COV_MIN_OBS = 200        # paarweise Mindestanzahl gemeinsamer Tage fuer die Kovarianz

SPEC = {
    "id": "mop2012_tsmom_12m_40vol",
    "name": "Moskowitz-Ooi-Pedersen TSMOM: 12-Monats-Vorzeichen, vol-skaliert (40 %), ETF12-Proxy",
    "family": "tsmom",
    "tickers": UNIVERSE + [RATE_TICKER],
    "start": "2007-02-13",       # gemeinsamer Start (FXY startet 2007-02-13)
    "sources": [
        "Moskowitz, Ooi, Pedersen 2012, Time series momentum, JFE 104(2), "
        "https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum",
        "Hurst, Ooi, Pedersen 2017, A Century of Evidence on Trend-Following Investing, "
        "https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing",
        "Kim, Tse, Wald 2016, Time Series Momentum and Volatility Scaling, "
        "https://quantpedia.com/deconstructing-the-time-series-momentum-strategy/",
    ],
    "params": {
        "mode": "LS",              # Hauptlauf laut Papier: Long/Short
        "lookback_months": 12,
        "asset_vol": 0.40,         # Einzel-Vol-Ziel
        "vol_com": 60,             # EWMA-Schwerpunkt der Gewichte in Tagen
        "max_gross": 3.0,          # Bruttohebel-Kappe (nur LS)
        "portfolio_vol": None,     # None = nicht auf Portfolio-Vol skaliert
    },
    # Vorab festgelegte Robustheits-Checks aus der Spezifikation (zaehlen als Versuche).
    # Der dritte Check der Spezifikation (Ausfuehrung Eroeffnung t+1) ist eine Engine-Einstellung
    # und kein Parameter: Harness-Standard ist exec=open.
    "variants": {
        "lf": {"mode": "LF"},                     # Long/Flat, Gesamtgewicht <= 1
        "portvol10": {"portfolio_vol": 0.10},     # LS auf 10 % Portfolio-Vol (Cov 756 Tage, Faktor 261)
    },
    "cost_bps": {t: 10.0 for t in UNIVERSE},      # Spezifikation: 10 bp je Seite
}


def load() -> Panel:
    """ETF12 + ^IRX ab dem gemeinsamen Start (der Cache liefert sonst die volle Historie)."""
    return load_panel(SPEC["tickers"], start=SPEC["start"]).slice(SPEC["start"])


def _empty(assets: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=assets, index=pd.DatetimeIndex([]), dtype=float)


def weights(panel, mode: str = "LS", lookback_months: int = 12, asset_vol: float = 0.40,
            vol_com: float = 60, max_gross: float = 3.0, portfolio_vol: float | None = None) -> pd.DataFrame:
    mode = str(mode).upper()
    if mode not in ("LS", "LF"):
        raise ValueError(f"mode muss 'LS' oder 'LF' sein, nicht {mode!r}")
    assets = [t for t in UNIVERSE if t in panel.close.columns]
    if not assets:
        raise KeyError("Panel enthaelt keinen ETF12-Ticker")
    if RATE_TICKER not in panel.close.columns:
        raise KeyError(f"Panel braucht {RATE_TICKER} als Zinsquelle")

    # Nur Tage, an denen mindestens ein handelbares Asset einen Kurs hat (der Zins-Ticker darf den
    # Kalender nicht verlaengern). NaN = noch nicht gelistet / nicht handelbar.
    px_all = panel.close[assets]
    px = px_all[px_all.notna().any(axis=1).to_numpy()]
    if len(px) < 3:
        return _empty(assets)

    # Tageszins (Information bis zum Vortag): ffill ist kausal, kein bfill
    irx = panel.close[RATE_TICKER].reindex(px.index).ffill()
    rf = irx.shift(1) / 100.0 / RF_DAYS
    cum_rf = (1.0 + rf.fillna(0.0)).cumprod()

    ret = px / px.shift(1) - 1.0                         # NaN, wenn gestern oder heute kein Kurs
    exc = ret.sub(rf, axis=0)                            # NaN, wenn Zins unbekannt
    sigma = np.sqrt(VOL_ANN * (exc ** 2).ewm(com=vol_com, min_periods=VOL_MIN_PERIODS).mean())

    # Kausale Monatsenden (nicht aus den Daten abgeleitet)
    me = px.index[month_end_flags(px.index).to_numpy()]
    k = int(lookback_months)
    if len(me) <= k:
        return _empty(assets)

    pm, cm = px.loc[me], cum_rf.loc[me]
    er = (pm / pm.shift(k) - 1.0).sub(cm / cm.shift(k) - 1.0, axis=0)   # Exzessrendite ueber k Monate
    # Fenster nur gueltig, wenn im ganzen Fenster der Zins bekannt war
    unknown = rf.isna().astype(int).cumsum().loc[me]
    rf_ok = ((unknown - unknown.shift(k)) == 0).to_numpy()
    er.loc[~rf_ok, :] = np.nan

    sig_me = sigma.loc[me]
    valid = er.notna() & (sig_me > MIN_SIGMA)
    rows = valid.index[valid.any(axis=1).to_numpy()]
    if len(rows) == 0:
        return _empty(assets)

    sgn = np.sign(er) if mode == "LS" else (er > 0).astype(float)
    sgn = sgn.where(valid, 0.0)
    inv_sig = (1.0 / sig_me).where(valid, 0.0)
    raw = (sgn * inv_sig).loc[rows]                       # sign / sigma, 0 ohne gueltiges Signal
    n_t = valid.sum(axis=1).loc[rows]

    if portfolio_vol is None:
        w = raw.mul(asset_vol / n_t, axis=0)
    else:
        # Hurst-Ooi-Pedersen: auf Portfolio-Vol skalieren (ex-ante Kovarianz der letzten 756 Tage bis t)
        w = pd.DataFrame(0.0, index=rows, columns=assets)
        keep = []
        for m in rows:
            cols = list(valid.columns[valid.loc[m].to_numpy()])
            w0 = raw.loc[m, cols].to_numpy(dtype=float) / float(n_t.loc[m])
            if not np.any(w0):                            # alle Signale 0 -> komplett Cash
                keep.append(m)
                continue
            win = exc.loc[:m, cols].iloc[-COV_WINDOW:]
            cov = win.cov(min_periods=COV_MIN_OBS).to_numpy(dtype=float) * VOL_ANN
            var = float(w0 @ cov @ w0)
            if not np.isfinite(var) or var <= 1e-14:
                continue                                  # Kovarianz nicht schaetzbar -> kein Signal
            w.loc[m, cols] = w0 * (float(portfolio_vol) / np.sqrt(var))
            keep.append(m)
        w = w.loc[keep]

    if mode == "LS":                                      # Bruttohebel <= max_gross
        g = w.abs().sum(axis=1)
        scale = (max_gross / g).where(g > max_gross, 1.0)
    else:                                                 # LF: Summe <= 1, Rest Cash
        s = w.sum(axis=1)
        scale = (LF_CAP / s).where(s > LF_CAP, 1.0)
    return w.mul(scale, axis=0).astype(float)
