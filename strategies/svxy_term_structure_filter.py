"""SVXY nur bei VIX-Contango (VIX / VIX3M < 1), sonst Cash — mit SPY-Sekundaertest.

Quellen (Familie volpremium, Abschnitt 5.2):
* CXO Advisory 2020, "Exploiting VIX Futures Roll Return with ETNs" (Sekundaerquelle).
* Cheng 2019, "The VIX Premium", Review of Financial Studies 32(1).

WICHTIG: Das CXO-Signal ist die Rendite der VIX-Futures-Roll (naechster vs. uebernaechster Kontrakt).
Das Verhaeltnis ^VIX / ^VIX3M ist ein Gratis-Proxy dafuer; die Gleichwertigkeit ist NICHT belegt.
Die CXO-Zahlen (CAGR 38 % usw.) sind deshalb keine Erwartung fuer diese Umsetzung.

Regel (alle Parameter fest aus der Spezifikation, nichts optimieren):

* ratio_t = ^VIX_t / ^VIX3M_t (Schlusswerte), ON_t = ratio_t < THR mit THR = 1.00 (strikt: genau 1.00 = AUS).
* Fehlt ratio_t (Daten fehlen laenger als `_FFILL_LIMIT` Zeilen), ist ON_t = AUS (Cash). Fehlende Einzeltage in
  ^VIX/^VIX3M werden hoechstens `_FFILL_LIMIT` Zeilen mit dem letzten bekannten Wert ueberbrueckt (nur Vergangenheit).
* ON -> Zielgewicht W im Handelstitel (Hauptlauf SVXY, W = 1.00), AUS -> Cash. Kein Hebel, Gewicht nie ueber 1.
* Das Signal entsteht am Schlusskurs t, die Engine handelt zur Eroeffnung t+1 (Harness-Standard "open"):
    ON_t und ON_t-1          : halten, Tagesrendite Close/Close
    ON_t und nicht ON_t-1    : Einstieg zum Open t+1, Rendite Close_t+1 / Open_t+1 - 1
    nicht ON_t und ON_t-1    : Ausstieg zum Open t+1, Rendite Open_t+1 / Close_t - 1
    sonst                    : Cash (Zins verbucht die Engine mit dem Fama-French-RF)
* "Kein Drift-Rebalancing": Es gibt NUR bei einem Zustandswechsel (und am ersten Tag mit gueltigem Signal) eine
  Zielgewichtszeile. An allen anderen Tagen liefert die Strategie bewusst keine Zeile, die Engine laesst die Position
  laufen. (Eine Zeile pro Tag wuerde bei W < 1 jeden Tag zurueck auf W handeln und Kosten erzeugen.)
* Zeilen gibt es nur an Tagen, an denen der Handelstitel einen Schlusskurs hat. Titel ohne Kurs (SVXY vor 2011-10-04,
  Datenluecken) bekommen nie ein Gewicht, und eine Datenluecke erzeugt keinen Schein-Wechsel.

Ausfuehrungs-Sensitivitaet "Fill zum Schlusskurs t+1": laeuft ueber den Harness, nicht ueber `weights`
(`scripts/run_all.py --exec close_next`), weil Gewichte nur das Signal, nicht den Fill-Zeitpunkt festlegen.
Kosten-Stress (0.10 % / 0.40 % je Wechsel): `--cost-mult 0.5` bzw. `--cost-mult 2` (Basis 20 bps je Seite).

Regimebruch: SVXY war bis einschliesslich 2018-02-27 ein -1x-Produkt, ab 2018-02-28 -0.5x. Statistiken sind
getrennt auszuweisen (`split_by_regime`). ^IRX steht bewusst nicht in SPEC["tickers"]: Der Cash-Zins kommt aus der
Engine (Fama-French-RF), ^IRX waere nur ein Prozentwert ohne handelbaren Preis.

Ruin-Hinweis (Spezifikation): Tagesverlust des -1x-Produkts am 2018-02-06 war -83 %; Echtgeld nie ueber 12 %
Portfolioanteil bei -1x bzw. 25 % bei -0.5x. `weights` lehnt W > 1 und W <= 0 ab.
"""
from __future__ import annotations

import pandas as pd

SVXY = "SVXY"
SPY = "SPY"
VIX = "^VIX"
VIX3M = "^VIX3M"
ASSETS = (SVXY, SPY)
_FFILL_LIMIT = 5                        # fehlende Einzeltage in den Vol-Indizes: hoechstens 5 Zeilen ueberbruecken
MAX_WEIGHT = 1.0                        # harte Obergrenze (kein Hebel)
REGIME_BREAK = pd.Timestamp("2018-02-28")   # ab hier ist SVXY ein -0.5x-Produkt

SPEC = {
    "id": "svxy_term_structure_filter",
    "name": "SVXY nur bei VIX-Contango (VIX/VIX3M < 1), sonst Cash (mit SPY-Sekundaertest)",
    "family": "volpremium",
    "tickers": [SVXY, SPY, VIX, VIX3M],          # ^IRX nicht noetig: Cash-Zins verbucht die Engine (French-RF)
    "start": "2006-07-17",                        # ^VIX3M ab 2006-07-17, SVXY ab 2011-10-04
    "sources": [
        "CXO Advisory 2020, Exploiting VIX Futures Roll Return with ETNs, "
        "https://www.cxoadvisory.com/volatility-effects/exploiting-vix-futures-roll-return-with-etns/",
        "Cheng 2019, The VIX Premium, Review of Financial Studies 32(1), "
        "https://ideas.repec.org/a/oup/rfinst/v32y2019i1p180-227..html",
    ],
    # w = Gewicht in ON-Phasen, threshold = Schwelle fuer VIX/VIX3M (fest 1.00), asset = Handelstitel
    "params": {"w": 1.0, "threshold": 1.0, "asset": SVXY},
    "variants": {
        "w025": {"w": 0.25},                      # Portfolio-Baustein, Rest Cash
        "spy_secondary": {"asset": SPY},          # Sekundaertest: dasselbe Signal steuert SPY (ab 2006-07)
    },
    # 0.20 % je Wechsel (CXO-Annahme) in SVXY; SPY 2 bp einseitig (Familie volpremium/volmgmt)
    "cost_bps": {SVXY: 20.0, SPY: 2.0},
}


def split_by_regime(ret: pd.Series) -> dict[str, pd.Series]:
    """Teilt eine SVXY-Renditereihe am Regimebruch (-1x bis 2018-02-27, -0.5x ab 2018-02-28)."""
    return {
        "svxy_minus_1x": ret.loc[ret.index < REGIME_BREAK],
        "svxy_minus_0_5x": ret.loc[ret.index >= REGIME_BREAK],
    }


def term_ratio(vix: pd.Series, vix3m: pd.Series) -> pd.Series:
    """VIX_t / VIX3M_t; NaN, wenn eine Seite fehlt (nach Ueberbrueckung) oder VIX3M <= 0.

    Fehlende Einzeltage werden hoechstens `_FFILL_LIMIT` Zeilen mit dem letzten bekannten Wert
    ueberbrueckt (rein vergangenheitsbezogen).
    """
    v = vix.ffill(limit=_FFILL_LIMIT)
    v3 = vix3m.ffill(limit=_FFILL_LIMIT)
    return v / v3.where(v3 > 0)


def contango_on(vix: pd.Series, vix3m: pd.Series, threshold: float = 1.0) -> pd.Series:
    """ON_t = (VIX_t / VIX3M_t < threshold) als bool-Serie; fehlendes Verhaeltnis -> False (Cash)."""
    ratio = term_ratio(vix, vix3m)
    return (ratio < float(threshold)) & ratio.notna()


def weights(panel, w: float = 1.0, threshold: float = 1.0, asset: str = SVXY) -> pd.DataFrame:
    if asset not in ASSETS:
        raise ValueError(f"asset muss eines von {ASSETS} sein, nicht {asset!r}")
    if not (0.0 < float(w) <= MAX_WEIGHT):
        raise ValueError(f"w muss in (0, {MAX_WEIGHT}] liegen, nicht {w!r}")

    close = panel.close
    px = close[asset]
    ratio = term_ratio(close[VIX], close[VIX3M])

    # Nur Tage, an denen der Handelstitel einen Kurs hat (kausal: ob heute ein Kurs da ist, weiss man heute).
    days = px.notna().to_numpy()
    ratio = ratio[days]
    on = (ratio < float(threshold)).astype(float)         # NaN-Verhaeltnis -> 0.0 (Cash)
    known = ratio.notna().cummax()                       # ab dem ersten Tag mit gueltigem Signal (nur Vergangenheit)
    if len(on) == 0 or not bool(known.any()):
        return pd.DataFrame(columns=[asset], dtype=float)

    first = known & ~known.shift(1, fill_value=False)    # erster Tag mit gueltigem Signal
    changed = on != on.shift(1)                          # Zustandswechsel gegenueber dem Vortag mit Kurs
    emit = known & (changed | first)

    target = pd.DataFrame({asset: float(w) * on[emit]})
    return target + 0.0                                  # kein -0.0
