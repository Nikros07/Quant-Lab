"""H17: Marktauswahl - haengt der Vorteil von `base1x` an einzelnen Maerkten? (docs/HYPOTHESEN.md, Eintrag H17)

Vorab registrierte Regel (unveraendert uebernommen):
  (a) Leave-one-out: 17 Koerbe aus je 16 Maerkten.
  (b) 300 Zufallsteilmengen aus je 8 bis 12 der 17 Maerkte (feste Seeds 0..299, mindestens 6 gueltige Maerkte je Tag).
  Je Teilmenge `base1x` gegen den Buy&Hold-Korb derselben Maerkte.
  Kriterium: `base1x` hat in >= 95 % der Teilmengen den kleineren MaxDD UND in >= 80 % der Teilmengen den hoeheren UPI
  als Buy&Hold. Zusaetzlich berichtet: schlechtester Fall und der Markt, dessen Entfernen den UPI am meisten senkt.

Umsetzung (einfachste Lesart):
  * Sleeve je Markt = sleeve2(lengths=(12,), target=None) aus H12 (= `base1x`: Monatsschluss >= Mittel der letzten
    12 Monatsschluesse, Entscheidung am Monatsende, Ausfuehrung Schluss Folgetag, 10 bp je Seite, Cash = US-RF).
  * Buy&Hold je Markt = Tagesrendite ab dem Sleeve-Start desselben Marktes (wie in H12).
  * Korb = gleichgewichteter Mittelwert der gueltigen Sleeves je Tag (basket aus check_trend_portfolio).
    min_markets: Leave-one-out 8 (wie base1x mit 17 Maerkten), Zufallsteilmengen 6 (wie registriert).
  * Je Teilmenge werden Strategie- und B&H-Korb auf ihrem gemeinsamen Index verglichen (Schnittmenge der Tage).
  * Kennzahlen aus konstanz() (H12): MaxDD, UPI = CAGR / Ulcer-Index. "Kleinerer MaxDD" = betragsmaessig kleiner.
  * Zufallsteilmenge: rng = default_rng(seed), Groesse = rng.integers(8, 13) (gleichverteilt 8..12), Auswahl ohne
    Zuruecklegen. Die Anteile werden fuer (a) und (b) getrennt gegen die Schwellen geprueft; bestanden nur, wenn beide
    Teile beide Schwellen erreichen. Zusaetzlich wird der gepoolte Anteil (a)+(b) berichtet.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
import pandas as pd

import check_h12_robust_basket as h12
import check_trend_portfolio as tp
import check_trend_vt_basket as vt
from qlab.data import risk_free_daily

OUT_DIR = ROOT / "results"
OUT_LOO = OUT_DIR / "H17_leave_one_out.csv"
OUT_RAND = OUT_DIR / "H17_random_subsets.csv"
OUT_SUM = OUT_DIR / "H17_summary.csv"

N_RANDOM = 300
SIZE_LO, SIZE_HI = 8, 12          # Teilmengen-Groesse gleichverteilt 8..12 (beide inklusive)
MIN_LOO = 8                       # wie base1x mit 17 Maerkten
MIN_RANDOM = 6                    # registriert
THR_DD = 0.95                     # Anteil Teilmengen mit kleinerem MaxDD
THR_UPI = 0.80                    # Anteil Teilmengen mit hoeherem UPI


def load_sleeves(markets=None, loader=None, rf_fn=risk_free_daily):
    """Sleeve- und B&H-Renditen je Markt. Gibt (SL, BH, skipped) zurueck (DataFrames bzw. Liste)."""
    markets = list(vt.MARKETS if markets is None else markets)
    loader = loader or vt.load_market
    sl, bh, skipped = {}, {}, []
    for t in markets:
        try:
            close = loader(t)
            rf = rf_fn(close.index)
            res = h12.sleeve2(close, rf, lengths=(12,), target=None)
        except Exception as exc:
            print(f"[{t}] uebersprungen: {exc}")
            skipped.append(t)
            continue
        s = res.index[0]
        sl[t] = res["ret"]
        bh[t] = close.astype(float).pct_change(fill_method=None).loc[s:].fillna(0.0)
    return pd.DataFrame(sl), pd.DataFrame(bh), skipped


def evaluate_subset(SL: pd.DataFrame, BH: pd.DataFrame, markets: list, min_markets: int,
                    rf_fn=risk_free_daily) -> dict:
    """base1x- und B&H-Korb der Teilmenge auf gemeinsamem Index; Kennzahlen aus konstanz()."""
    cols = list(markets)
    s_ret, _ = tp.basket(SL[cols], min_markets)
    b_ret, _ = tp.basket(BH[cols], min_markets)
    common = s_ret.index.intersection(b_ret.index)
    s_ret, b_ret = s_ret.reindex(common), b_ret.reindex(common)
    rf = rf_fn(common)
    ks, kb = h12.konstanz(s_ret, rf), h12.konstanz(b_ret, rf)
    return {
        "n_markets": len(cols), "n_days": len(common),
        "start": str(common[0].date()), "end": str(common[-1].date()),
        "cagr_s": ks["cagr"], "cagr_bh": kb["cagr"],
        "maxdd_s": ks["max_dd"], "maxdd_bh": kb["max_dd"],
        "upi_s": ks["upi"], "upi_bh": kb["upi"],
        "sharpe_s": ks["sharpe"], "sharpe_bh": kb["sharpe"],
        "dd_better": bool(ks["max_dd"] > kb["max_dd"]),    # MaxDD negativ: groesser = betragsmaessig kleiner
        "upi_better": bool(ks["upi"] > kb["upi"]),
        "d_maxdd_pp": (ks["max_dd"] - kb["max_dd"]) * 100.0,
        "d_upi": ks["upi"] - kb["upi"],
    }


def leave_one_out(SL, BH, markets, min_markets=MIN_LOO, rf_fn=risk_free_daily) -> pd.DataFrame:
    """Je Markt ein Korb ohne diesen Markt."""
    rows = []
    for m in markets:
        rest = [x for x in markets if x != m]
        rows.append({"removed": m, **evaluate_subset(SL, BH, rest, min_markets, rf_fn)})
    return pd.DataFrame(rows)


def random_subset(markets: list, seed: int, lo: int = SIZE_LO, hi: int = SIZE_HI) -> list:
    """Reproduzierbare Zufallsteilmenge: Groesse gleichverteilt lo..hi, Auswahl ohne Zuruecklegen."""
    rng = np.random.default_rng(seed)
    k = int(rng.integers(lo, hi + 1))
    pick = rng.choice(len(markets), size=k, replace=False)
    return [markets[i] for i in sorted(pick)]


def random_subsets(SL, BH, markets, n=N_RANDOM, min_markets=MIN_RANDOM, rf_fn=risk_free_daily,
                   lo=SIZE_LO, hi=SIZE_HI) -> pd.DataFrame:
    rows = []
    for seed in range(n):
        sub = random_subset(markets, seed, lo, hi)
        rows.append({"seed": seed, "markets": " ".join(sub), **evaluate_subset(SL, BH, sub, min_markets, rf_fn)})
    return pd.DataFrame(rows)


def shares(df: pd.DataFrame) -> tuple[float, float]:
    """(Anteil kleinerer MaxDD, Anteil hoeherer UPI) ueber die Teilmengen."""
    return float(df["dd_better"].mean()), float(df["upi_better"].mean())


def passes(df: pd.DataFrame) -> bool:
    a, b = shares(df)
    return a >= THR_DD and b >= THR_UPI


def _lab(ok: bool) -> str:
    return "ERFUELLT" if ok else "NICHT erfuellt"


def main() -> None:
    print(f"H17 Marktauswahl: {len(vt.MARKETS)} Maerkte, base1x gegen B&H derselben Maerkte, "
          f"{vt.BPS:.0f} bp je Seite, Cash = US-RF, Auswertung bis {vt.END}\n")
    SL, BH, skipped = load_sleeves()
    markets = list(SL.columns)
    print(f"Maerkte mit Daten: {len(markets)} von {len(vt.MARKETS)}; uebersprungen: {skipped or 'keine'}\n")

    full = evaluate_subset(SL, BH, markets, MIN_LOO)
    print(f"Referenz alle {len(markets)} Maerkte (min {MIN_LOO}): {full['start']} bis {full['end']}, "
          f"CAGR {full['cagr_s'] * 100:.2f} % / {full['cagr_bh'] * 100:.2f} %, "
          f"MaxDD {full['maxdd_s'] * 100:.2f} % / {full['maxdd_bh'] * 100:.2f} %, "
          f"UPI {full['upi_s']:.3f} / {full['upi_bh']:.3f} (base1x / B&H)\n")

    loo = leave_one_out(SL, BH, markets)
    rnd = random_subsets(SL, BH, markets)

    # (a) Leave-one-out
    a_dd, a_upi = shares(loo)
    print("(a) Leave-one-out (je Zeile: Markt entfernt):")
    show = loo[["removed", "n_days", "cagr_s", "maxdd_s", "maxdd_bh", "upi_s", "upi_bh", "d_upi"]].copy()
    for c in ("cagr_s", "maxdd_s", "maxdd_bh"):
        show[c] = (show[c] * 100).map("{:.2f}".format)
    for c in ("upi_s", "upi_bh", "d_upi"):
        show[c] = show[c].map("{:.3f}".format)
    print(show.to_string(index=False))
    print(f"  Anteil kleinerer MaxDD: {a_dd:.1%} ({int(loo['dd_better'].sum())} von {len(loo)}); "
          f"Anteil hoeherer UPI: {a_upi:.1%} ({int(loo['upi_better'].sum())} von {len(loo)})")
    drop = loo.loc[loo["upi_s"].idxmin()]
    print(f"  Markt, dessen Entfernen den base1x-UPI am meisten senkt: {drop['removed']} "
          f"(UPI {drop['upi_s']:.3f} statt {full['upi_s']:.3f}, {drop['upi_s'] - full['upi_s']:+.3f})")

    # (b) Zufallsteilmengen
    b_dd, b_upi = shares(rnd)
    print(f"\n(b) {len(rnd)} Zufallsteilmengen (Groesse {rnd['n_markets'].min()} bis {rnd['n_markets'].max()}, "
          f"Mittel {rnd['n_markets'].mean():.1f}):")
    print(f"  Anteil kleinerer MaxDD: {b_dd:.1%} ({int(rnd['dd_better'].sum())} von {len(rnd)}); "
          f"Anteil hoeherer UPI: {b_upi:.1%} ({int(rnd['upi_better'].sum())} von {len(rnd)})")
    print(f"  Delta MaxDD (Pp, base1x minus B&H): Median {rnd['d_maxdd_pp'].median():+.2f}, "
          f"Minimum {rnd['d_maxdd_pp'].min():+.2f}, Maximum {rnd['d_maxdd_pp'].max():+.2f}")
    print(f"  Delta UPI (base1x minus B&H): Median {rnd['d_upi'].median():+.3f}, "
          f"Minimum {rnd['d_upi'].min():+.3f}, Maximum {rnd['d_upi'].max():+.3f}")
    w_dd = rnd.loc[rnd["d_maxdd_pp"].idxmin()]
    w_upi = rnd.loc[rnd["d_upi"].idxmin()]
    print(f"  Schlechtester Fall MaxDD: Seed {int(w_dd['seed'])}, {int(w_dd['n_markets'])} Maerkte, "
          f"MaxDD {w_dd['maxdd_s'] * 100:.2f} % vs {w_dd['maxdd_bh'] * 100:.2f} % ({w_dd['d_maxdd_pp']:+.2f} Pp)")
    print(f"  Schlechtester Fall UPI: Seed {int(w_upi['seed'])}, {int(w_upi['n_markets'])} Maerkte, "
          f"UPI {w_upi['upi_s']:.3f} vs {w_upi['upi_bh']:.3f} ({w_upi['d_upi']:+.3f})")
    w_loo = loo.loc[loo["d_upi"].idxmin()]
    print(f"  Schlechtester Fall Leave-one-out (UPI-Differenz): ohne {w_loo['removed']}: "
          f"UPI {w_loo['upi_s']:.3f} vs {w_loo['upi_bh']:.3f} ({w_loo['d_upi']:+.3f})")
    for lab, d in (("kleinerer MaxDD", "dd_better"), ("hoeherer UPI", "upi_better")):
        bad = rnd[~rnd[d]]
        if len(bad):
            print(f"  Teilmengen ohne {lab}: {len(bad)}; Maerkte-Haeufigkeit dort vs. gesamt (Top 5 Abweichung):")
            freq_bad = pd.Series(" ".join(bad["markets"]).split()).value_counts() / len(bad)
            freq_all = pd.Series(" ".join(rnd["markets"]).split()).value_counts() / len(rnd)
            diff = (freq_bad - freq_all).dropna().sort_values()
            print("    " + ", ".join(f"{k} {v:+.2f}" for k, v in list(diff.head(3).items()) + list(diff.tail(2).items())))

    # gepoolt und Gesamturteil
    pool = pd.concat([loo, rnd], ignore_index=True)
    p_dd, p_upi = shares(pool)
    ok_a, ok_b = passes(loo), passes(rnd)
    total = ok_a and ok_b
    print(f"\n(c) Gepoolt ({len(pool)} Teilmengen): kleinerer MaxDD {p_dd:.1%}, hoeherer UPI {p_upi:.1%}")
    print(f"\nKriterium H17: MaxDD-Anteil >= {THR_DD:.0%} UND UPI-Anteil >= {THR_UPI:.0%}")
    print(f"  (a) Leave-one-out: MaxDD {a_dd:.1%}, UPI {a_upi:.1%} -> {_lab(ok_a)}")
    print(f"  (b) Zufallsteilmengen: MaxDD {b_dd:.1%}, UPI {b_upi:.1%} -> {_lab(ok_b)}")
    print(f"  (gepoolt zur Information: {_lab(p_dd >= THR_DD and p_upi >= THR_UPI)})")
    print(f"  Gesamt H17: {_lab(total)}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    loo.to_csv(OUT_LOO, index=False, encoding="utf-8", float_format="%.6f")
    rnd.to_csv(OUT_RAND, index=False, encoding="utf-8", float_format="%.6f")
    summ = pd.DataFrame([
        {"teil": "alle_17", "n": 1, "anteil_maxdd": float(full["dd_better"]), "anteil_upi": float(full["upi_better"]),
         "median_d_upi": full["d_upi"], "min_d_upi": full["d_upi"], "min_d_maxdd_pp": full["d_maxdd_pp"],
         "kriterium": ""},
        {"teil": "leave_one_out", "n": len(loo), "anteil_maxdd": a_dd, "anteil_upi": a_upi,
         "median_d_upi": loo["d_upi"].median(), "min_d_upi": loo["d_upi"].min(),
         "min_d_maxdd_pp": loo["d_maxdd_pp"].min(), "kriterium": _lab(ok_a)},
        {"teil": "zufall_300", "n": len(rnd), "anteil_maxdd": b_dd, "anteil_upi": b_upi,
         "median_d_upi": rnd["d_upi"].median(), "min_d_upi": rnd["d_upi"].min(),
         "min_d_maxdd_pp": rnd["d_maxdd_pp"].min(), "kriterium": _lab(ok_b)},
        {"teil": "gepoolt", "n": len(pool), "anteil_maxdd": p_dd, "anteil_upi": p_upi,
         "median_d_upi": pool["d_upi"].median(), "min_d_upi": pool["d_upi"].min(),
         "min_d_maxdd_pp": pool["d_maxdd_pp"].min(), "kriterium": _lab(total)},
    ])
    summ.to_csv(OUT_SUM, index=False, encoding="utf-8", float_format="%.6f")
    print(f"\nCSV gespeichert: {OUT_LOO}\nCSV gespeichert: {OUT_RAND}\nCSV gespeichert: {OUT_SUM}")


if __name__ == "__main__":
    main()
