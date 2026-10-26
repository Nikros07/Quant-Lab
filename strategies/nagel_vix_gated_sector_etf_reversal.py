"""VIX-getorte Tages-Umkehr auf den 9 SPDR-Sektor-ETFs (Industrie-Variante von Nagel 2012).

Uebertragung der Industrie-Reversal-Idee aus Nagel (2012) auf handelbare, survivorship-freie
Sektor-ETFs. Das ist EINE UEBERTRAGUNG, kein Paper-Ergebnis (Nagel testet CRSP-Aktien und 48
Fama-French-Industrieportfolios, 1998-2010, brutto, Handel zum Signal-Schluss).

Regel (Spezifikation research/strategie-kandidaten.json, Familie reversal.md Abschnitt 3.5):

* Universum XLB XLE XLF XLI XLK XLP XLU XLV XLY (auto_adjust-Schlusskurse).
* Tag d: r_i,d = Tagesrendite, m_d = Mittel der r_i,d, x_i,d = r_i,d - m_d,
  w_i(d) = -x_i,d / (0.5 * sum_k |x_k,d|)           (dollar-neutral: Long-Leg +1, Short-Leg -1).
* Overlay aus 5 Teilstrategien (Nagel): Zielgewicht fuer die Haltephase Close(t+1) -> Close(t+2)
  = (1/5) * sum_{j=0..4} w_i(t-j)                   (nutzt nur Renditen der Tage t, t-1, ..., t-4).
* Gate g_t = 1, wenn ^VIX-Schluss(t) > Median(^VIX-Schluss(t-251..t)), sonst 0. Gewicht_i = g_t * Overlay_i.
  Sensitivitaeten (vorab festgelegt, ALLE berichten, keine Auswahl): feste Schwellen 20 / 25 / 30.
* Taegliches Rebalancing; ist das Gate zu, liefert die Strategie ausdruecklich eine Zeile mit lauter
  Nullen (= flach gehen), keine leere Zeile (die Engine wuerde die Positionen sonst driften lassen).

Timing: Das Signal entsteht am Schlusskurs von t (Renditen bis t, VIX-Schluss t). Die Engine handelt es
im Harness-Standard (exec "open") zur Eroeffnung t+1; die in der Spezifikation genannte Hauptausfuehrung
"Schlusskurs t+1" entspricht `run_all.py --exec close_next`.

Kosten: 3 bp je Seite (Spezifikation) ueber SPEC["cost_bps"]; der Stresstest 1/5 bp laeuft ueber --cost-mult.
Die Engine verbucht Kosten, Steuer, Cash-Zins und Leihgebuehr selbst, nichts davon steckt hier drin.

^VIX liegt nur als Signalquelle im Panel (Indexstand, kein handelbarer Preis) und bekommt nie ein Gewicht.
SPEC["start"] liegt vor dem ETF-Start 1998-12-22, damit die 252-Tage-Gate-Historie des VIX am ersten ETF-Tag
schon vorliegt, egal ob die Kurse aus dem Cache oder frisch geladen werden (erstes Signal sonst abhaengig
vom Cache-Zustand).
"""
from __future__ import annotations

import pandas as pd

ETFS = ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]
VIX = "^VIX"
_FFILL_LIMIT = 5      # fehlende Einzeltage: hoechstens 5 Zeilen mit dem letzten bekannten Wert ueberbruecken

SPEC = {
    "id": "nagel_vix_gated_sector_etf_reversal",
    "name": "VIX-getorte Tages-Umkehr auf Sektor-ETFs (Nagel, Industrie-Variante)",
    "family": "reversal",
    "tickers": ETFS + [VIX],
    "start": "1997-06-01",       # ETFs ab 1998-12-22; VIX-Vorlauf (252 Tage) liegt davor
    "sources": ["Nagel 2012, Evaporating Liquidity, https://www.nber.org/papers/w17653"],
    # vix_threshold None = Median-Gate (Basis); Zahl = feste VIX-Schwelle (Sensitivitaet)
    "params": {"vix_threshold": None, "vix_window": 252, "n_lags": 5},
    "variants": {
        "vix_20": {"vix_threshold": 20.0},
        "vix_25": {"vix_threshold": 25.0},
        "vix_30": {"vix_threshold": 30.0},
    },
    "cost_bps": {t: 3.0 for t in ETFS},
}


def _daily_returns(px: pd.DataFrame) -> pd.DataFrame:
    """Rendite = Schluss / letzter bekannter Schluss davor - 1 (NaN, wenn heute oder davor kein Kurs)."""
    return px / px.ffill(limit=_FFILL_LIMIT).shift(1) - 1.0


def _daily_reversal_weights(r: pd.DataFrame) -> pd.DataFrame:
    """w_i(d) je ETF-Handelstag aus den Tagesrenditen r (Zeilen = Tage, Spalten = ETFs).

    ETFs ohne Rendite an einem Tag bekommen Gewicht 0 und zaehlen nicht in Mittel und Normierung.
    Ist die Summe der |x| null (alle Renditen gleich) oder fehlen alle Renditen, sind alle Gewichte 0.
    """
    x = r.sub(r.mean(axis=1), axis=0)                                  # mean ueberspringt NaN
    denom = 0.5 * x.abs().sum(axis=1, min_count=1)
    w = -x.div(denom.where(denom > 0), axis=0)
    return w.fillna(0.0)


def _gate(vix: pd.Series, index: pd.DatetimeIndex, threshold: float | None, window: int) -> pd.Series:
    """Gate 0/1 auf den ETF-Handelstagen `index`; NaN, solange die VIX-Historie fuer das Fenster fehlt.

    Median-Gate: VIX-Schluss(t) > Median der letzten `window` VIX-Schluesse inkl. t (nur Vergangenheit).
    Feste Schwelle: VIX-Schluss(t) > threshold; der Vorlauf von `window` Beobachtungen wird trotzdem
    verlangt, damit alle Gate-Arten ueber denselben Zeitraum laufen.
    """
    v = vix.dropna()
    have_history = v.rolling(window).count() >= window
    if threshold is None:
        ref = v.rolling(window).median()
        on = (v > ref).astype(float)
    else:
        on = (v > float(threshold)).astype(float)
    on = on.where(have_history)
    # ETF-Tage ohne VIX-Wert: letzter bekannter Gate-Wert (nur Vergangenheit), kurz begrenzt
    return on.reindex(index, method="ffill", limit=_FFILL_LIMIT)


def weights(panel, vix_threshold: float | None = None, vix_window: int = 252, n_lags: int = 5) -> pd.DataFrame:
    close = panel.close
    px_all = close[ETFS]
    px = px_all[px_all.notna().any(axis=1)]                            # nur echte ETF-Handelstage
    if len(px) == 0:
        return pd.DataFrame(columns=ETFS, dtype=float)

    r = _daily_returns(px)
    w_day = _daily_reversal_weights(r)
    has_ret = r.notna().any(axis=1)                                    # mindestens eine Rendite an diesem Tag
    full_history = has_ret.astype(float).rolling(n_lags).sum() >= n_lags
    overlay = w_day.rolling(n_lags).mean()                             # (1/n) * Summe der letzten n Tagesgewichte

    gate = _gate(close[VIX], px.index, vix_threshold, vix_window)
    target = overlay.mul(gate, axis=0)
    target = target.where(px.notna(), 0.0) + 0.0                       # kein Gewicht auf Titel ohne Kurs (+0.0: kein -0.0)
    valid = full_history & gate.notna()
    return target[valid.to_numpy()]
