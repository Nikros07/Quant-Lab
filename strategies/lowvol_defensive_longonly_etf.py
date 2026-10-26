"""Low-Volatility Long-only (defensiv), ETF-Realitaets-Check: USMV (und SPLV) Buy&Hold, Sektor-Proxy als Variante.

Zweitmodul zu `lowvol_defensive_longonly` (Faktor-Ebene auf Ken-French-Portfolios, Langzeit ab 1963): gleiche
Idee (Low-Risk-Anomalie, Blitz/van Vliet 2007; Baker/Bradley/Wurgler 2011), aber auf handelbaren, in den USA
gelisteten ETFs. Spezifikation: research/strategie-kandidaten.json (`lowvol_defensive_longonly`) und
research/families/lowrisk.md (S2, Umsetzungen A und B).

Basis (Spezifikation, unveraendert uebernommen): KEIN Signal, KEINE Optimierung.
    100 % USMV (iShares MSCI USA Min Vol), Buy&Hold ab Auflage (Yahoo-Start 2011-10-20), Vergleich mit SPY und
    Steuer nach Abgeltungsteuer macht der Harness. Kein Hebel, kein Cash.

Umsetzung im Engine-Vertrag:
* Die Engine handelt immer erst nach dem Signal: Signal am Schluss des ersten Handelstags mit Kurs, Kauf zur
  Eroeffnung des NAECHSTEN Tages. "Kauf zur Eroeffnung des ersten Handelstags" ist damit nicht abbildbar
  (der Tag davor hat keinen Kurs, ein Gewicht davor waere ein Blick in die Zukunft); die Abweichung ist ein
  Handelstag.
* Gewichte: genau eine Zeile am ersten Tag mit gueltigem Schlusskurs des Fonds (NaN = nicht handelbar).
* SPY liegt nur im Panel als Vergleichsreihe und bekommt nie ein Gewicht.

Varianten (vorab festgelegt, Robustheits-Checks, keine Auswahl der besten):
    splv          SPLV (Invesco S&P 500 Low Volatility, Yahoo-Start 2011-05-05) statt USMV, sonst identisch.
    sector_proxy  Variante B der Spezifikation (eigener Sektor-Proxy, KEIN Paper-Replikat, nur Sektor-Tilt):
                  Universum fest: XLB XLE XLF XLI XLK XLP XLU XLV XLY (XLRE und XLC bewusst ausgelassen, damit
                  die Universumsgroesse konstant bleibt). Am letzten Handelstag t jedes Monats (qlab.calendar.
                  month_end_flags) die Standardabweichung der Wochenrenditen der letzten 156 Wochen je Sektor
                  (Wochenschluss-zu-Wochenschluss, letzter Handelstag der Woche ueber week_end_flags, Stand =
                  letzter abgeschlossener Wochenschluss <= t); die 3 Sektoren mit der kleinsten Std bekommen je
                  1/3 (Gleichstand: Spaltenreihenfolge), Rest 0. Die Engine handelt zur Eroeffnung von t+1.
                  Ein Signal gibt es nur, wenn alle 9 Sektoren 156 gueltige Wochenrenditen und einen Kurs an t
                  haben (erstes Signal ca. Ende 2001). Kosten Standard (5 bps je Seite, wie in der Spezifikation).
Die dritte vorregistrierte Variante (Faktor-Ebene mit Portfolios_Formed_on_VAR statt BETA) steht im Hauptmodul.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from qlab.calendar import month_end_flags, week_end_flags

SECTORS = ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]

SPEC = {
    "id": "lowvol_defensive_longonly_etf",
    "name": "Low-Vol Long-only (defensiv), ETF-Check: USMV Buy&Hold; Varianten SPLV, Sektor-Proxy",
    "family": "lowrisk",
    "tickers": ["USMV", "SPLV", "SPY"] + SECTORS,
    "start": "1998-12-22",               # SPDR-Sektoren starten 1998-12-22; USMV 2011-10-20, SPLV 2011-05-05
    "sources": [
        "Blitz, van Vliet 2007, The Volatility Effect: Lower Risk Without Lower Return, https://papers.ssrn.com/abstract=980865",
        "Baker, Bradley, Wurgler 2011, Benchmarks as Limits to Arbitrage: Understanding the Low-Volatility Anomaly, https://papers.ssrn.com/abstract=1745108",
    ],
    "params": {"mode": "hold", "asset": "USMV", "lookback_weeks": 156, "top_n": 3},
    "variants": {
        "splv": {"asset": "SPLV"},
        "sector_proxy": {"mode": "sector_lowvol"},
    },
}


# --------------------------------------------------------------------------------------
# Bausteine
# --------------------------------------------------------------------------------------

def hold_weights(panel, asset: str) -> pd.DataFrame:
    """Buy&Hold: 100 % auf `asset`, eine einzige Zeile am ersten Tag mit gueltigem Schlusskurs."""
    first = panel.close[asset].first_valid_index()
    if first is None:
        return pd.DataFrame({asset: np.array([], dtype=float)}, index=pd.DatetimeIndex([]))
    return pd.DataFrame({asset: [1.0]}, index=pd.DatetimeIndex([first]))


def weekly_vol(close: pd.DataFrame, lookback_weeks: int = 156) -> pd.DataFrame:
    """Std (ddof=1) der Wochenrenditen der letzten `lookback_weeks` Wochen, auf jeden Handelstag t gelegt.

    Wochenschluesse nur ueber qlab.calendar.week_end_flags (kausal). Der Wert an Tag t ist der des letzten
    abgeschlossenen Wochenschlusses <= t; NaN, solange keine `lookback_weeks` gueltigen Wochenrenditen im Fenster
    liegen (fehlende Kurse bleiben NaN, es wird nichts aufgefuellt).
    """
    idx = close.index
    wk = week_end_flags(idx).to_numpy()
    wclose = close[wk]
    wret = wclose / wclose.shift(1) - 1.0
    vol = wret.rolling(lookback_weeks, min_periods=lookback_weeks).std(ddof=1)
    pos = np.cumsum(wk) - 1                                    # Position des letzten Wochenschlusses <= t (-1: keiner)
    out = np.full(close.shape, np.nan)
    ok = pos >= 0
    out[ok] = vol.to_numpy(dtype=float)[pos[ok]]
    return pd.DataFrame(out, index=idx, columns=close.columns)


def sector_lowvol_weights(panel, lookback_weeks: int = 156, top_n: int = 3) -> pd.DataFrame:
    """Monatsende-Signal: die `top_n` Sektoren mit der kleinsten Wochenrenditen-Std, je 1/top_n."""
    close = panel.close[SECTORS]
    idx = close.index
    vol = weekly_vol(close, lookback_weeks).to_numpy()
    flags = month_end_flags(idx).to_numpy()                    # kausal, nicht aus den Daten abgeleitet
    px_ok = close.notna().to_numpy()
    use = flags & np.isfinite(vol).all(axis=1) & px_ok.all(axis=1)
    v = vol[use]
    order = np.argsort(v, axis=1, kind="stable")[:, :top_n]    # kleinste Std zuerst; Gleichstand: Spaltenreihenfolge
    w = np.zeros_like(v)
    np.put_along_axis(w, order, 1.0 / top_n, axis=1)
    return pd.DataFrame(w, index=idx[use], columns=SECTORS)


def weights(panel, mode: str = "hold", asset: str = "USMV", lookback_weeks: int = 156, top_n: int = 3) -> pd.DataFrame:
    """Zielgewichte. mode="hold": 100 % `asset` Buy&Hold; mode="sector_lowvol": Sektor-Proxy (Variante B)."""
    if mode == "hold":
        return hold_weights(panel, asset)
    if mode == "sector_lowvol":
        return sector_lowvol_weights(panel, lookback_weeks=lookback_weeks, top_n=top_n)
    raise ValueError(f"unbekannter mode {mode!r}")
