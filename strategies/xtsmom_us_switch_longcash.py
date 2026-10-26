"""Cross-Asset-TSMOM USA: Long/Cash-Umschalter Aktien / Anleihen / Cash — Langzeit-Test ab 1981 (Fonds- und Zins-Proxys).

Quellen: Pitkaejaervi, Suominen, Vaittinen 2020, "Cross-asset signals and time series momentum", JFE 136(1),
https://doi.org/10.1016/j.jfineco.2019.02.011; CXO Advisory 2017, "Cross-asset Class Intrinsic Momentum".
Spezifikation: research/strategie-kandidaten.json (id xtsmom_us_switch_longcash), Notizen in
research/families/gap_crossasset_bond_equity_leadlag_signals.md, Abschnitt 3.1.

Regel (festgelegt vor dem Backtest, Parameter aus der Quelle, keine Optimierung), am letzten Handelstag T jedes Monats:
    r12(X) = AdjClose_X(T) / AdjClose_X(Monatsende T-12M) - 1 - rf12            (kein Skip-Monat)
    rf12   = Produkt ueber die 12 Monate k = T-11 ... T von (1 + ^IRX[Monatsende k-1] / 100 / 12) - 1
    rE = r12(Aktien), rB = r12(Anleihe)
    rE > 0 und rB > 0     -> 100 % Aktien
    rE <= 0 und rB > 0    -> 100 % Anleihe    (Flucht in Qualitaet)
    rB <= 0               -> 100 % Cash
"> 0" ist strikt (Gleichheit zaehlt als nicht positiv). Kein Hebel, kein Short. Das Signal haengt nur von Daten bis
einschliesslich T ab; die Engine handelt zur Eroeffnung des Folgetags.

Zwei Module (Spezifikation: Langtest UND Live-Test)
---------------------------------------------------
* DIESES Modul `xtsmom_us_switch_longcash` = Langtest ab 1981 mit den Proxys der Spezifikation:
      Aktien  : VFINX (Vanguard 500, ab 1980-01-02; angepasst = Gesamtrendite) statt SPY
      Anleihe : VFITX (Vanguard Intermediate-Term Treasury, ab 1991-10-28), davor eine synthetische Reihe aus ^FVX
      Cash    : Engine-Cash (Fama-French RF, Tagesrendite des 1-Monats-Bills) statt SHY / ^IRX/1200
  Das erste Signal gibt es am 1981-01-30 (12 Monate Vorlauf ab dem ersten VFINX-Monatsende 1980-01-31).
* `xtsmom_us_switch_longcash_etf` = Live-Test auf den ETFs SPY / IEF / SHY (ab 2002-07-30, erstes Signal 2003-07-31).

Umsetzung im Engine-Vertrag
---------------------------
* Panel-Spalten tragen die ROLLEN-Namen "SPY" (= VFINX), "IEF" (= VFITX + ^FVX-Synthese), "TLT" (= VUSTX + ^TYX-Synthese,
  nur fuer die Variante `tlt`) und "^IRX" (Zinsquelle in PROZENT, nie ein Gewicht). Die Rollen-Namen sind Absicht: Die
  Engine leitet die Teilfreistellung (InvStG) aus dem Ticker ab (Aktien 30 %, IEF/TLT/SHY 0 %). Mit den Fonds-Namen
  VFITX/VUSTX bekaeme die Anleihe-Seite faelschlich 30 % Teilfreistellung und die Nach-Steuer-Zahlen waeren zu gut.
  Modelliert wird ohnehin der UCITS-Aktien- bzw. Staatsanleihen-ETF, die Fonds sind nur die Kurshistorie dafuer.
* Fonds handeln zum Tages-NAV: open == close fuer alle Handelsspalten (wie bei `panel_from_returns`). Ein Signal am
  Schluss von T wird damit zum NAV von T+1 umgesetzt und verdient ab T+2. Das entspricht der Spezifikation
  ("Wechsel zur Eroeffnung T+1") bis auf den Unterschied Eroeffnung/Schluss, den ein Fonds nicht kennt.
* Zielgewichte nur bei Zustandswechsel: Eine Signalzeile (ein Gewicht 1.0 oder eine Nullzeile = Cash) erscheint nur,
  wenn der Zielzustand vom zuletzt AUSGEGEBENEN abweicht ("Wechsel nur, wenn Ziel != aktuelle Position"). Das vermeidet
  Mini-Umschichtungen (und damit Mini-Steuerereignisse) an jedem Monatsende. Das erste gueltige Signal wird immer
  ausgegeben, auch als Nullzeile (Cash), damit die Auswertung am ersten Signaltag beginnt.
* Monatsenden NUR ueber qlab.calendar.month_end_flags (kausal). Das Lookback-Monatsende ist der letzte Datentag des
  Kalendermonats T-12; fehlt dieser Monat oder ein Zins im Fenster, gibt es kein Signal. Kurze Kurs-/Zinsluecken
  (bis 5 Handelstage) werden nur mit dem letzten bekannten Wert nach vorn ueberbrueckt, nie rueckwaerts.
* Gehandelt wird nur ein Titel mit gueltigem Kurs am Signaltag (NaN = nicht handelbar -> kein Signal an diesem Tag).

Synthetische Anleihe-Reihe vor dem Fonds-Start (Spezifikation, "Sensitivitaetstest" der langen Historie)
---------------------------------------------------------------------------------------------------------
    y = Rendite in Dezimal (^FVX bzw. ^TYX / 100),   D(y) = (1 - (1 + y/2)^-(2 N)) / y   (modifizierte Duration einer
    N-jaehrigen Par-Anleihe mit Halbjahreskupon; N = 5 fuer ^FVX, N = 30 fuer ^TYX)
    Tagesrendite r(d) = y(d-1) / 252 - D(y(d-1)) * (y(d) - y(d-1))                 (Carry minus Duration * Renditeaenderung)
Die Spezifikation gibt die Formel monatlich an; hier die Tagesfassung derselben Formel (Konvexitaet ignoriert).
Die Reihe wird zum Kursniveau verkettet und am Fonds-Starttag auf den echten Fondskurs skaliert (Niveau-Splice).

Kosten: 2 bp je Seite laut Spezifikation (statt 5 bp Engine-Standard) ueber SPEC["cost_bps"]; Stresstest 5/10 bp ueber
`--cost-mult 2.5 / 5` im Harness. Steuern und Cash-Zins verbucht die Engine.

Varianten (vorab festgelegt, Robustheits-Checks, keine Auswahl der besten):
    skip1   12-1: Skip-Monat im Lookback. Rendite und Zins laufen von Monatsende T-12 bis Monatsende T-1 (11 Monate;
            Kursverhaeltnis P(T-1)/P(T-12), Zins fuer dieselben 11 Monate), der letzte Monat zaehlt nicht.
    tlt     Langlaeufer-Anleihe (Spalte "TLT": VUSTX ab 1986-05-19, davor ^TYX-Synthese) statt der 7-10J-Anleihe.
Die dritte Variante der Spezifikation ("Ausfuehrung Schluss t+1 statt Eroeffnung") ist ein Harness-Schalter
(`--exec close_next`), kein Strategie-Parameter. Fuer die Fonds-Spalten (open == close) ist sie ohnehin die Basis.
"""
from __future__ import annotations

import time

import numpy as np
import pandas as pd

from qlab.calendar import month_end_flags
from qlab.data import CACHE, Panel, load_ticker

EQ = "SPY"            # Rolle Aktien (Langtest: VFINX)
BOND = "IEF"          # Rolle Anleihe 7-10J (Langtest: VFITX + ^FVX-Synthese)
LONGBOND = "TLT"      # Rolle Langlaeufer (Variante tlt; Langtest: VUSTX + ^TYX-Synthese)
RATE = "^IRX"         # 13-Wochen-Bill-Rendite in PROZENT, nie handelbar
LOOKBACK = 12
FFILL_LIMIT = 5       # kurze Luecken (Handelstage) mit dem letzten Wert nach vorn ueberbruecken, nie laenger
RF_DAYS = 252         # Carry je Handelstag der synthetischen Anleihe
SPLICE_FIVE_YEAR = 5.0    # ^FVX: 5-jaehrige Par-Anleihe
SPLICE_THIRTY_YEAR = 30.0  # ^TYX: 30-jaehrige Par-Anleihe

SPEC = {
    "id": "xtsmom_us_switch_longcash",
    "name": "Cross-Asset-TSMOM USA: Long/Cash-Umschalter Aktien/Anleihe/Cash, Langtest ab 1981 (VFINX/VFITX)",
    "family": "gap_crossasset_bond_equity_leadlag_signals",
    "tickers": [EQ, BOND, LONGBOND, RATE],     # Spalten des Panels aus load(); Proxys siehe Moduldoku
    "start": "1981-01-01",
    "sources": [
        "Pitkaejaervi, Suominen, Vaittinen 2020, Cross-asset signals and time series momentum, "
        "https://doi.org/10.1016/j.jfineco.2019.02.011",
        "CXO Advisory 2017, Cross-asset Class Intrinsic Momentum, "
        "https://www.cxoadvisory.com/equity-premium/cross-asset-class-intrinsic-momentum",
    ],
    "params": {"equity": EQ, "bond": BOND, "rate": RATE, "lookback": LOOKBACK, "skip": 0},
    "variants": {
        "skip1": {"skip": 1},
        "tlt": {"bond": LONGBOND},
    },
    "cost_bps": {EQ: 2.0, BOND: 2.0, LONGBOND: 2.0},
}


# --------------------------------------------------------------------------------------
# Daten
# --------------------------------------------------------------------------------------

def _safe(ticker: str) -> str:
    return ticker.replace("^", "_idx_").replace("=", "_eq_").replace("/", "_")


def _load_long(ticker: str, start: str, max_age_days: float = 30.0) -> pd.Series:
    """Schlusskurse (angepasst) ab `start` in eigenem Cache (der gemeinsame Cache beginnt erst 1990-01-02)."""
    path = CACHE / f"long_px_{_safe(ticker)}_{start[:4]}.parquet"
    if path.exists() and (time.time() - path.stat().st_mtime) < max_age_days * 86400:
        return pd.read_parquet(path)["Close"]
    err = None
    try:
        import yfinance as yf

        df = yf.Ticker(ticker).history(start=start, auto_adjust=True, actions=False)
        if df is not None and len(df) > 0:
            df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
            df = df[["Close"]].astype(float)
            df = df[~df.index.duplicated(keep="last")].sort_index()
            df.to_parquet(path)
            return df["Close"]
        err = RuntimeError(f"leere Antwort fuer {ticker}")
    except Exception as exc:  # Netz, Rate-Limit
        err = exc
    if path.exists():
        print(f"[data] WARNUNG: {ticker} (lang) nicht aktualisierbar ({err}); alter Cache wird genutzt")
        return pd.read_parquet(path)["Close"]
    raise RuntimeError(f"{ticker} (lang) nicht ladbar: {err}")


def par_bond_duration(y, years: float):
    """Modifizierte Duration einer `years`-jaehrigen Par-Anleihe mit Halbjahreskupon bei Rendite y (Dezimal)."""
    y = np.maximum(np.asarray(y, float), 1e-4)            # Schutz gegen y -> 0
    return (1.0 - (1.0 + y / 2.0) ** (-2.0 * years)) / y


def synthetic_bond_index(yield_pct: pd.Series, years: float) -> pd.Series:
    """Kursniveau (Start 100) einer synthetischen Par-Anleihe aus einer Renditereihe in PROZENT.

    Tagesrendite r(d) = y(d-1)/252 - D(y(d-1)) * (y(d) - y(d-1)), y in Dezimal; nur Vortageswerte im Carry/Duration-Teil,
    die Renditeaenderung nutzt y(d). Luecken in der Rendite werden uebersprungen (Aenderung gegen den letzten gueltigen Wert).
    """
    y = (pd.Series(yield_pct, dtype=float).dropna() / 100.0)
    y = y[np.isfinite(y.to_numpy())]
    prev = y.shift(1)
    r = prev / RF_DAYS - par_bond_duration(prev.fillna(0.05).to_numpy(), years) * (y - prev)
    r = r.iloc[1:]
    level = 100.0 * (1.0 + r).cumprod()
    first = pd.Series([100.0], index=[y.index[0]])
    return pd.concat([first, level])


def splice_bond(real_close: pd.Series, synthetic: pd.Series) -> pd.Series:
    """Echte Fondskurse ab dem ersten Fondstag; davor die auf das Fondsniveau skalierte Synthese (Niveau-Splice)."""
    real = real_close.dropna()
    real = real[real > 0]
    if real.empty:
        raise ValueError("keine echten Anleihe-Kurse")
    t0 = real.index[0]
    before = synthetic[synthetic.index < t0]
    at = synthetic[synthetic.index <= t0]
    if at.empty:
        return real.sort_index()
    k = float(real.iloc[0]) / float(at.iloc[-1])
    return pd.concat([before * k, real]).sort_index()


def _bridge(series: pd.Series, idx: pd.DatetimeIndex) -> pd.Series:
    """Reihe auf `idx` legen; Luecken (nur auf diesen Tagen) mit dem letzten bekannten Wert fuellen, hoechstens FFILL_LIMIT Tage."""
    union = series.index.union(idx)
    return series.reindex(union).ffill(limit=FFILL_LIMIT).reindex(idx)


def build_panel(equity: pd.Series, bond: pd.Series, longbond: pd.Series, irx: pd.Series) -> Panel:
    """Panel (open == close) auf den Handelstagen des Aktienfonds; Spalten [SPY, IEF, TLT, ^IRX] (Rollen-Namen)."""
    eq = equity.dropna()
    idx = pd.DatetimeIndex(eq.index)
    close = pd.DataFrame({
        EQ: eq,
        BOND: _bridge(bond.dropna(), idx),
        LONGBOND: _bridge(longbond.dropna(), idx),
        RATE: _bridge(irx.dropna(), idx),
    }, index=idx)
    return Panel(close.copy(), close)


def load() -> Panel:
    """Langzeit-Panel ab 1980-01-02 (VFINX), ungekuerzt (der Harness schneidet bei 2022-12-31 ab)."""
    vfinx = _load_long("VFINX", "1980-01-01")
    irx = _load_long("^IRX", "1960-01-01")
    fvx = _load_long("^FVX", "1962-01-01")
    tyx = _load_long("^TYX", "1977-01-01")
    vustx = _load_long("VUSTX", "1986-01-01")
    vfitx = load_ticker("VFITX")["Close"]
    bond = splice_bond(vfitx, synthetic_bond_index(fvx, SPLICE_FIVE_YEAR))
    longbond = splice_bond(vustx, synthetic_bond_index(tyx, SPLICE_THIRTY_YEAR))
    return build_panel(vfinx, bond, longbond, irx)


# --------------------------------------------------------------------------------------
# Kern (wird vom ETF-Modul wiederverwendet)
# --------------------------------------------------------------------------------------

def _take(arr: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """arr[ref] mit NaN dort, wo ref < 0 (Monat fehlt)."""
    return np.where(ref >= 0, arr[np.where(ref >= 0, ref, 0)], np.nan)


def switch_weights(panel, equity: str, bond: str, rate: str, cash: str | None = None,
                   lookback: int = LOOKBACK, skip: int = 0) -> pd.DataFrame:
    """Zielgewichte (0/1, Summe <= 1) auf [equity, bond] (+ [cash]) an Monatsenden mit Zustandswechsel.

    Ohne `cash`-Titel ist der Cash-Zustand eine Nullzeile (die Engine haelt dann Cash und verzinst es).
    """
    lookback, skip = int(lookback), int(skip)
    if lookback < 1 or not 0 <= skip < lookback:
        raise ValueError("lookback muss >= 1 sein und 0 <= skip < lookback")
    assets = [equity, bond] + ([cash] if cash else [])
    if len(set(assets)) != len(assets):
        raise ValueError("Aktien-, Anleihe- und Cash-Titel muessen verschieden sein")
    missing = [t for t in assets + [rate] if t not in panel.close.columns]
    if missing:
        raise KeyError(f"Panel braucht {missing}")
    empty = pd.DataFrame(columns=assets, index=pd.DatetimeIndex([]), dtype=float)

    idx = panel.close.index
    if len(idx) < 3:
        return empty
    flags = month_end_flags(idx).to_numpy()                   # nur kausal erkannte Monatsenden
    me_pos = np.flatnonzero(flags)
    M = len(me_pos)
    if M <= lookback:
        return empty

    px = panel.close[assets]
    raw = px.to_numpy(float)[me_pos]                          # echter Kurs am Signaltag: NaN = nicht handelbar
    pxf = px.ffill(limit=FFILL_LIMIT).to_numpy(float)[me_pos]  # nur Vergangenheit, nur kurze Luecken
    irx = panel.close[rate].ffill(limit=FFILL_LIMIT).to_numpy(float)[me_pos]
    months = (idx.year * 12 + idx.month).to_numpy()[me_pos]

    def ref_of(k: int) -> np.ndarray:
        """Position (im Monatsend-Array) des Kalendermonats T-k; -1, wenn dieser Monat fehlt."""
        target = months - k
        j = np.searchsorted(months, target)
        jj = np.minimum(j, M - 1)
        return np.where((j < M) & (months[jj] == target), jj, -1)

    num_ref, den_ref = ref_of(skip), ref_of(lookback)
    with np.errstate(invalid="ignore", divide="ignore"):
        def r12(a: int) -> np.ndarray:
            num, den = _take(pxf[:, a], num_ref), _take(pxf[:, a], den_ref)
            good = (num_ref >= 0) & (den_ref >= 0) & (num > 0) & (den > 0)
            return np.where(good, num / den - 1.0, np.nan)

        growth = np.ones(M)
        good_rf = np.ones(M, dtype=bool)
        for k in range(skip + 1, lookback + 1):               # Monat j = T-k+1 verzinst mit ^IRX[Monatsende j-1] = T-k
            y = _take(irx, ref_of(k))
            good_rf &= np.isfinite(y)
            growth *= 1.0 + np.nan_to_num(y) / 100.0 / 12.0
        rf = np.where(good_rf, growth - 1.0, np.nan)

        rE, rB = r12(0) - rf, r12(1) - rf
    ok = np.isfinite(rE) & np.isfinite(rB)
    state = np.where(rB > 0, np.where(rE > 0, 0, 1), 2)       # 0 = Aktien, 1 = Anleihe, 2 = Cash
    for s in range(len(assets)):                              # gehandelter Titel braucht einen gueltigen Kurs am Signaltag
        ok &= (state != s) | (np.isfinite(raw[:, s]) & (raw[:, s] > 0))

    dates, rows, last = [], [], None
    for e in np.flatnonzero(ok):
        s = int(state[e])
        if s == last:                                         # Ziel == aktuelle Position -> nichts zu tun
            continue
        last = s
        w = np.zeros(len(assets))
        if s < len(assets):                                   # Cash ohne Cash-Titel = Nullzeile
            w[s] = 1.0
        dates.append(idx[me_pos[e]])
        rows.append(w)
    if not rows:
        return empty
    return pd.DataFrame(np.vstack(rows), index=pd.DatetimeIndex(dates), columns=assets, dtype=float)


# --------------------------------------------------------------------------------------
# Strategie
# --------------------------------------------------------------------------------------

def weights(panel, equity: str = EQ, bond: str = BOND, rate: str = RATE, lookback: int = LOOKBACK,
            skip: int = 0) -> pd.DataFrame:
    """Zielgewichte (0/1) auf [equity, bond]; die Nullzeile bedeutet 100 % Cash (Engine-Cash, Fama-French RF)."""
    return switch_weights(panel, equity, bond, rate, cash=None, lookback=lookback, skip=skip)
