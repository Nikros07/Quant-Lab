"""Antonacci Global Equities Momentum (GEM) als Multi-Lookback-Ensemble (L = 6 ... 12 Monate).

Quellen: Antonacci 2017, Risk Premia Harvesting Through Dual Momentum (SSRN 2042750);
Newfound Research 2019, Fragility Case Study: Dual Momentum GEM (Spezifikationsrisiko je Lookback).
Spezifikation: research/strategie-kandidaten.json (id antonacci_gem_lookback_ensemble), Notizen in
research/families/tactical.md, Abschnitt 3.3.

Basisregel mit Lookback L (am letzten Handelstag t eines Monats, Schlusskurse, angepasst = Total Return):
    r_X = P_X(t) / P_X(t - L Monate) - 1        (Monatsend-Schlusskurse; Cash: kumulierter ^IRX-Zuwachs)
    Falls r_SPY > r_Cash:  100 % in das Asset mit dem höheren r aus {SPY, EFA}   (Gleichstand -> SPY)
    sonst:                 100 % in AGG.
Absolutes Momentum prüft also nur den US-Aktienteil (SPY gegen Cash), wie bei Antonacci.

Ensemble: 7 Sleeves mit L = 6, 7, 8, 9, 10, 11, 12, je 1/7 des Kapitals. Jeden Dezember (am letzten
Handelstag) werden die Sleeve-Anteile auf 1/7 zurückgesetzt, dazwischen driften sie mit ihrer Wertentwicklung.
Die Strategie liefert Zielgewichte; die Engine rebalanciert auf JEDER Signalzeile komplett auf diese Gewichte.
Damit die Sleeves trotzdem driften und nicht jeden Monat auf 1/7 zurückfallen, führt die Strategie den Anteil
jedes Sleeves virtuell mit (nur aus Kursen bis einschließlich t) und gibt an jedem Monatsende das driftende
Sleeve-Gewicht aus (`_drift_targets`). Die Buchhaltung bildet die Engine bei Standard-Ausführung ("open":
Signal am Schluss t, Handel zur Eröffnung t+1) exakt nach: Der Handel setzt alle Sleeves auf ihre Anteile vom
Schluss t, danach läuft der Intraday-Teil von t+1 und ab t+2 jeder volle Tag mit dem neuen Asset. Bei
`--exec close_next`/`close` ist die Drift minimal anders verteilt (Größenordnung eines Tagesgaps).

Cash (Spezifikation): ^IRX (13-Wochen-T-Bill-Rendite in PROZENT, kein handelbarer Preis, bekommt nie Gewicht)
wird zu einem Zuwachsindex verkettet: je Handelstag Faktor 1 + ^IRX(Vortag) / 100 / 252 (Information bis zum
Vortag, kein Blick nach vorn). r_Cash(L) = Zuwachs über dieselben L Monate. BIL wird nicht gebraucht.

Ensemble-Start: erst wenn ALLE Sleeves ein gültiges Signal haben (L = 12 braucht 12 Monate Historie).
Fehlende Preise = nicht handelbar: Hat ein Sleeve am Monatsende keine gültige Historie (SPY, Ex-US, Cash) oder
keinen Kurs auf dem gewählten Asset, gibt es für diesen Monat keine Signalzeile (die Positionen driften weiter).

Kausalität: Monatsenden aus qlab.calendar.month_end_flags; Lookback-Kurse sind Monatsend-Kurse strikt vor t
(Kalendermonat t-L), kurze Kurslücken werden höchstens 5 Tage vorwärts überbrückt, nie rückwärts.

Varianten (vorab festgelegt, laut Spezifikation "sensitivity_variants", keine Auswahl der besten):
    acwx       Ex-US = ACWX (Yahoo ab 2008-04) statt EFA
    single_l12 Einzel-GEM mit L = 12 (Originalregel, Kontrolle; zugleich Konzentrationstest)
    bond_ief   Anleihen-Bein = IEF statt AGG
Kosten (10 bp je Seite, Stress 5/20 über --cost-mult) stehen in SPEC["cost_bps"]; Kosten, Cash-Zins und
Steuer verbucht die Engine.
"""
from __future__ import annotations

import time

import numpy as np
import pandas as pd

from qlab.calendar import month_end_flags
from qlab.data import CACHE, Panel, load_panel

US = "SPY"
RATE = "^IRX"
TRADABLE = ["SPY", "EFA", "AGG", "IEF", "ACWX"]
LOOKBACKS = (6, 7, 8, 9, 10, 11, 12)

RF_DAYS = 252             # ^IRX (Prozent p.a.) -> Zins je Handelstag (wie die anderen Lab-Strategien)
FFILL_LIMIT = 5           # kurze Kurslücken (Tage) überbrücken, nie länger
EFA_LONG_START = "2001-08-01"   # EFA startet 2001-08-14; der geteilte Cache beginnt wegen eines späteren Aufrufs erst 2006-03
_EFA_LONG_CACHE = CACHE / "long_px_EFA_2001.parquet"

SPEC = {
    "id": "antonacci_gem_lookback_ensemble",
    "name": "Antonacci GEM als Multi-Lookback-Ensemble (L=6..12, SPY/EFA/AGG, Cash ^IRX)",
    "family": "tactical",
    # ^IRX ist reine Zinsquelle (Prozent, nie handelbar); BIL entfällt (^IRX-Zuwachs ersetzt ihn).
    "tickers": TRADABLE + [RATE],
    "start": "2003-09-29",       # AGG startet 2003-09-29; erstes Ensemble-Signal 2004-09-30 (12 Monatsenden Vorlauf)
    "sources": [
        "Antonacci 2017, Risk Premia Harvesting Through Dual Momentum, "
        "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2042750",
        "Newfound Research 2019, Fragility Case Study: Dual Momentum GEM, "
        "https://blog.thinknewfound.com/2019/01/fragility-case-study-dual-momentum-gem/",
    ],
    "params": {"lookbacks": LOOKBACKS, "ex_us": "EFA", "bond": "AGG", "reset_month": 12},
    "variants": {
        "acwx": {"ex_us": "ACWX"},
        "single_l12": {"lookbacks": (12,)},
        "bond_ief": {"bond": "IEF"},
    },
    "cost_bps": {t: 10.0 for t in TRADABLE},     # Spezifikation: 10 bp je Seite (Stress 5/20 bp über --cost-mult)
}


# --------------------------------------------------------------------------------------
# Daten
# --------------------------------------------------------------------------------------

def _load_efa_long(max_age_days: float = 30.0) -> pd.DataFrame:
    """EFA (Open/Close, angepasst) ab 2001-08 in eigenem Cache (der geteilte px_EFA-Cache beginnt erst 2006-03)."""
    path = _EFA_LONG_CACHE
    if path.exists() and (time.time() - path.stat().st_mtime) < max_age_days * 86400:
        return pd.read_parquet(path)
    err = None
    try:
        import yfinance as yf

        df = yf.Ticker("EFA").history(start=EFA_LONG_START, auto_adjust=True, actions=False)
        if df is not None and len(df) > 0:
            df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
            df = df[["Open", "Close"]].astype(float)
            df = df[~df.index.duplicated(keep="last")].sort_index()
            df.to_parquet(path)
            return df
        err = RuntimeError("leere Antwort für EFA")
    except Exception as exc:  # Netz, Rate-Limit
        err = exc
    if path.exists():
        print(f"[data] WARNUNG: EFA (lang) nicht aktualisierbar ({err}); alter Cache wird genutzt")
        return pd.read_parquet(path)
    raise RuntimeError(f"EFA (lang) nicht ladbar: {err}")


def load() -> Panel:
    """SPY, AGG, IEF, ACWX, ^IRX aus dem Cache + EFA ab 2001-08, ab SPEC["start"] auf die ETF-Handelstage gelegt.

    Zeilen, an denen kein einziger ETF handelt (reine Zins-Tage), werden entfernt: Sonst würde der Zins-Ticker den
    Handelskalender verlängern und die Engine den Over-Night-Übergang über NaN-Zeilen auf 1 setzen.
    """
    base = load_panel(["SPY", "AGG", "IEF", "ACWX", RATE])           # volle Cache-Historie, keine Kürzung
    efa = _load_efa_long()
    idx = base.close.index.union(efa.index)
    close = base.close.reindex(idx)
    open_ = base.open.reindex(idx)
    close["EFA"] = efa["Close"].reindex(idx)
    open_["EFA"] = efa["Open"].reindex(idx)
    cols = TRADABLE + [RATE]
    close, open_ = close[cols], open_[cols]
    keep = close[TRADABLE].notna().any(axis=1)
    close, open_ = close[keep], open_[keep]
    sl = slice(pd.Timestamp(SPEC["start"]), None)
    return Panel(open_.loc[sl], close.loc[sl])


# --------------------------------------------------------------------------------------
# Bausteine
# --------------------------------------------------------------------------------------

def _cash_factors(irx: pd.Series) -> pd.Series:
    """Tagesfaktor des Cash-Zuwachses aus ^IRX (Prozent). Faktor am Tag i nutzt nur ^IRX bis i-1; NaN = Zins unbekannt."""
    return 1.0 + irx.shift(1) / 100.0 / RF_DAYS


def _empty(assets: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=assets, index=pd.DatetimeIndex([]), dtype=float)


def _check_lookbacks(lookbacks) -> list[int]:
    lb = [int(x) for x in lookbacks]
    if not lb:
        raise ValueError("mindestens ein Lookback nötig")
    if any(x < 1 for x in lb) or len(set(lb)) != len(lb):
        raise ValueError("lookbacks müssen eindeutige ganze Zahlen >= 1 sein")
    return lb


def _drift_targets(choice: np.ndarray, pos: np.ndarray, reset: np.ndarray,
                   on: np.ndarray, intr: np.ndarray) -> np.ndarray:
    """Zielgewichte je Signalzeile aus driftenden Sleeves.

    choice : (K, E) Asset-Index je Sleeve und Signalzeile (gewählt am Schluss des Signaltags)
    pos    : (E,)   Zeilenposition des Signaltags im Tagesindex (aufsteigend)
    reset  : (E,)   True -> Sleeve-Anteile vor dem Gewicht auf 1/K zurücksetzen (Dezember)
    on     : (n, A) Over-Night-Faktor open[i]/close[i-1] je Asset (1 bei fehlendem Kurs)
    intr   : (n, A) Intraday-Faktor close[i]/open[i] je Asset (1 bei fehlendem Kurs)

    Das Signal vom Schluss t wird (Engine, exec "open") zur Eröffnung von t+1 zu den Zielgewichten gehandelt, also
    zu den Sleeve-Anteilen vom Schluss t; der Over-Night-Sprung von t+1 geht dabei nicht mehr in die Anteile ein.
    Danach wächst jedes Sleeve mit seinem neuen Asset: Intraday-Faktor von t+1, ab t+2 volle Tage (on * intr).
    Gibt (E, A) Gewichte mit Zeilensumme 1 zurück.
    """
    K, E = choice.shape
    A = on.shape[1]
    g = on * intr
    out = np.zeros((E, A))
    share = np.full(K, 1.0 / K)
    hold = choice[:, 0]
    for e in range(E):
        if e > 0:
            a, b = int(pos[e - 1]) + 1, int(pos[e]) + 1
            f = intr[a] * np.prod(g[a + 1:b], axis=0)         # Tage a..b-1; leeres Produkt = 1
            share = share * f[hold]
            share = share / share.sum()
        if reset[e]:
            share = np.full(K, 1.0 / K)
        np.add.at(out[e], choice[:, e], share)
        hold = choice[:, e]
    return out


# --------------------------------------------------------------------------------------
# Strategie
# --------------------------------------------------------------------------------------

def weights(panel, lookbacks=LOOKBACKS, ex_us: str = "EFA", bond: str = "AGG",
            reset_month: int | None = 12) -> pd.DataFrame:
    """Zielgewichte (Summe 1, nur Long, kein Hebel) auf [SPY, ex_us, bond] an jedem Monatsende mit gültigem Signal."""
    lb = _check_lookbacks(lookbacks)
    assets = [US, ex_us, bond]
    if len(set(assets)) != 3:
        raise ValueError("SPY, Ex-US-Asset und Anleihe-Asset müssen verschieden sein")
    if reset_month is not None and not 1 <= int(reset_month) <= 12:
        raise ValueError("reset_month muss 1..12 oder None sein")
    missing = [t for t in assets + [RATE] if t not in panel.close.columns]
    if missing:
        raise KeyError(f"Panel braucht {missing}")

    # Nur Tage, an denen mindestens eines der drei Assets einen Kurs hat (der Zins-Ticker verlängert den Kalender nicht).
    px_all = panel.close[assets]
    keep = px_all.notna().any(axis=1).to_numpy()
    px = px_all[keep]
    if len(px) < 3:
        return _empty(assets)
    idx = px.index
    op = panel.open[assets].reindex(idx)
    n, A = len(idx), len(assets)

    flags = month_end_flags(idx).to_numpy()                   # nur kausal erkannte Monatsenden
    me_pos = np.flatnonzero(flags)
    M = len(me_pos)
    if M <= min(lb):
        return _empty(assets)

    cls = px.to_numpy(float)
    opn = op.to_numpy(float)
    pxf = px.ffill(limit=FFILL_LIMIT).to_numpy(float)         # nur Vergangenheit, nur kurze Lücken
    cur = pxf[me_pos]
    cur = np.where(cur > 0, cur, np.nan)                      # nicht-positive Kurse = ungültig
    raw = cls[me_pos]                                         # echter Kurs am Signaltag: NaN = nicht handelbar

    irx = panel.close[RATE].reindex(idx).ffill(limit=FFILL_LIMIT)
    fac = _cash_factors(irx)
    cash = fac.fillna(1.0).cumprod().to_numpy(float)
    unknown = fac.isna().cumsum().to_numpy(float)
    cash_me, unk_me = cash[me_pos], unknown[me_pos]

    months = (idx.year * 12 + idx.month).to_numpy()[me_pos]
    month_index = pd.Index(months)
    rows = np.arange(M)
    choice = np.full((len(lb), M), -1, dtype=int)
    with np.errstate(invalid="ignore", divide="ignore"):
        for k, L in enumerate(lb):
            ref = month_index.get_indexer(months - L)         # Monatsende des Kalendermonats t-L (-1 = fehlt)
            has = ref >= 0
            rf_ = np.where(has, ref, 0)
            r = np.where(has[:, None], cur / cur[rf_] - 1.0, np.nan)
            rc = np.where(has & (unk_me - unk_me[rf_] == 0), cash_me / cash_me[rf_] - 1.0, np.nan)
            ok = np.isfinite(r[:, :2]).all(axis=1) & np.isfinite(rc)   # Entscheidung braucht SPY, Ex-US, Cash
            risk_on = r[:, 0] > rc                            # absolutes Momentum: SPY gegen Cash
            pick = np.where(risk_on, np.where(r[:, 1] > r[:, 0], 1, 0), 2)   # relatives Momentum, Gleichstand -> SPY
            price = raw[rows, pick]
            ok &= np.isfinite(price) & (price > 0)            # gewähltes Asset muss am Signaltag handelbar sein
            choice[k] = np.where(ok, pick, -1)

    row_ok = (choice >= 0).all(axis=0)                        # erst handeln, wenn jedes Sleeve ein Signal hat
    if not row_ok.any():
        return _empty(assets)
    pos = me_pos[row_ok]
    dates = idx[pos]

    on = np.ones((n, A))
    intr = np.ones((n, A))
    with np.errstate(invalid="ignore", divide="ignore"):
        prev = cls[:-1]
        ok_on = np.isfinite(opn[1:]) & np.isfinite(prev) & (prev > 0)
        on[1:] = np.where(ok_on, opn[1:] / prev, 1.0)
        ok_in = np.isfinite(opn) & np.isfinite(cls) & (opn > 0)
        intr = np.where(ok_in, cls / opn, 1.0)

    if reset_month is None:
        reset = np.zeros(len(pos), dtype=bool)
    else:
        reset = np.asarray(dates.month == int(reset_month))
    w = _drift_targets(choice[:, row_ok], pos, reset, on, intr)
    return pd.DataFrame(w, index=dates, columns=assets, dtype=float)
