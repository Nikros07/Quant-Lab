"""H15: Bootstrap-Konfidenz der Unterschiede base1x gegen Buy&Hold-Korb (docs/HYPOTHESEN.md, Pruefblock P1, Eintrag H15).

Registrierte Regel (unveraendert uebernommen):
  * Gepaarte Tagesrenditen des Korbs `base1x` und des Buy&Hold-Korbs (gleiche Tage, gleicher gemeinsamer Index wie in H12).
  * Stationaerer Block-Bootstrap (Politis und Romano): geometrische Blocklaenge, Mittel 60 Handelstage, 2000 Ziehungen,
    feste Seeds. Beide Reihen (und der risikolose Zins fuer den Sharpe) werden mit DEMSELBEN Indexvektor gezogen (gepaart).
  * Kennzahlen je Ziehung wie `konstanz` (H12): CAGR, MaxDD, UPI (= CAGR / Ulcer), Sharpe; Differenz = base1x minus B&H.
  * 90-%-Intervalle = 5. und 95. Perzentil der Differenzen.
  * Kriterium: "Verlustvorteil belegt", wenn die 5. Perzentil-Grenze der MaxDD-Differenz (base1x minus B&H, in Prozentpunkten,
    positiv = besser, d. h. MaxDD ist negativ gespeichert und die Differenz base1x - B&H > 0 heisst flacherer Drawdown) > 0 ist.
  * "Renditenachteil": P(CAGR(base1x) < CAGR(B&H)) wird berichtet, kein Bestehen/Durchfallen.

Umsetzung: Index der Ziehung t = Start des laufenden Blocks plus Offset (zyklisch ueber den Rand der Reihe); an jedem Tag beginnt
mit Wahrscheinlichkeit 1/60 ein neuer Block an einer gleichverteilten Zufallsstelle. Jede Ziehung hat dieselbe Laenge wie die Reihe.
Annualisierung wie qlab.metrics.summarize (Beobachtungen je Jahr aus der Originalreihe).
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

from qlab import metrics

OUT_DIR = ROOT / "results"
IN_RET = OUT_DIR / "H12_basket_returns.csv"
OUT_STATS = OUT_DIR / "H15_bootstrap_stats.csv"
OUT_DRAWS = OUT_DIR / "H15_bootstrap_draws.csv"
OUT_SEEDS = OUT_DIR / "H15_bootstrap_seeds.csv"

MEAN_BLOCK = 60          # registriert: mittlere Blocklaenge in Handelstagen
N_DRAWS = 2000           # registriert: Anzahl Ziehungen
MASTER_SEED = 15         # Haupt-Seed (feste Seeds); je Ziehung rng = default_rng([seed, b])
CHECK_SEEDS = (16, 17)   # nur Empfindlichkeit gegen den Seed, nicht fuer das Kriterium
KEYS = ("cagr", "max_dd", "upi", "sharpe")


def stationary_indices(n: int, mean_block: float, rng: np.random.Generator) -> np.ndarray:
    """Indexvektor (Laenge n) eines stationaeren Bootstraps mit geometrischer Blocklaenge (Mittel mean_block), zyklisch."""
    if n < 1:
        raise ValueError("n muss >= 1 sein")
    if mean_block < 1:
        raise ValueError("mean_block muss >= 1 sein")
    p = 1.0 / mean_block
    pos = np.arange(n)
    neu = rng.random(n) < p
    neu[0] = True
    starts = rng.integers(0, n, n)
    block_pos = np.maximum.accumulate(np.where(neu, pos, 0))   # Position, an der der laufende Block begann
    return (starts[block_pos] + (pos - block_pos)) % n


def kennzahlen(ret: np.ndarray, rf: np.ndarray, ppy: float) -> dict:
    """CAGR, MaxDD, UPI, Sharpe wie qlab.metrics.summarize / konstanz (H12), auf numpy-Basis fuer die vielen Ziehungen.

    nav startet mit der ersten Rendite (kein Anfangswert 1 im Maximum), ppy = Beobachtungen je Jahr der Originalreihe.
    """
    ret = np.asarray(ret, float)
    n = len(ret)
    nav = np.cumprod(1.0 + ret)
    years = n / ppy
    cagr = nav[-1] ** (1.0 / years) - 1.0 if nav[-1] > 0 else -1.0
    dd = nav / np.maximum.accumulate(nav) - 1.0
    ulcer = float(np.sqrt(np.mean(dd ** 2)))
    ex = ret - np.asarray(rf, float)
    sd = ex.std(ddof=1)
    sharpe = float(ex.mean() / sd * np.sqrt(ppy)) if sd > 0 else float("nan")
    return {"cagr": float(cagr), "max_dd": float(dd.min()), "upi": float(cagr / ulcer) if ulcer > 0 else float("nan"),
            "sharpe": sharpe}


def bootstrap(r_a: np.ndarray, r_b: np.ndarray, rf: np.ndarray, ppy: float, *, n_draws: int = N_DRAWS,
              mean_block: float = MEAN_BLOCK, seed: int = MASTER_SEED) -> pd.DataFrame:
    """Gepaarter stationaerer Bootstrap. a = base1x, b = B&H. Gibt je Ziehung Kennzahlen a_*, b_* und Differenzen d_* (a minus b)."""
    r_a, r_b, rf = (np.asarray(x, float) for x in (r_a, r_b, rf))
    if not (len(r_a) == len(r_b) == len(rf)):
        raise ValueError("Reihen muessen gleich lang sein")
    n = len(r_a)
    rows = []
    for b in range(n_draws):
        rng = np.random.default_rng([seed, b])
        ix = stationary_indices(n, mean_block, rng)
        ka = kennzahlen(r_a[ix], rf[ix], ppy)
        kb = kennzahlen(r_b[ix], rf[ix], ppy)
        row = {"draw": b}
        for k in KEYS:
            row[f"a_{k}"] = ka[k]
            row[f"b_{k}"] = kb[k]
            row[f"d_{k}"] = ka[k] - kb[k]
        rows.append(row)
    return pd.DataFrame(rows)


def auswerten(draws: pd.DataFrame) -> dict:
    """Intervalle (5./95. Perzentil), Median, Anteil Differenz > 0, P(CAGR a < CAGR b) und das registrierte Kriterium."""
    out = {}
    for k in KEYS:
        d = draws[f"d_{k}"].dropna().to_numpy()
        out[k] = {"p05": float(np.percentile(d, 5)), "median": float(np.median(d)), "p95": float(np.percentile(d, 95)),
                  "mean": float(d.mean()), "share_pos": float((d > 0).mean()), "n": int(len(d))}
    out["p_cagr_lower"] = float((draws["d_cagr"] < 0).mean())
    out["verlustvorteil_belegt"] = bool(out["max_dd"]["p05"] > 0)
    return out


def laden_csv(path: Path = IN_RET) -> pd.DataFrame:
    """Gepaarte Tagesrenditen (Spalten bh, base1x) aus der H12-CSV."""
    df = pd.read_csv(path, usecols=["date", "bh", "base1x"], parse_dates=["date"]).set_index("date")
    return df.dropna()


def neu_berechnen() -> pd.DataFrame:
    """Pipeline wie H12 (nur bh und base1x): load_market, sleeve2, basket, gemeinsamer Index."""
    import check_h12_robust_basket as h12
    import check_trend_portfolio as tp
    import check_trend_vt_basket as vt
    from qlab.data import risk_free_daily
    RET = {"bh": {}, "base1x": {}}
    for t in vt.MARKETS:
        try:
            close = vt.load_market(t)
            rf = risk_free_daily(close.index)
            res = h12.sleeve2(close, rf, **h12.RUNS["base1x"])
        except Exception as exc:
            print(f"[{t}] uebersprungen: {exc}")
            continue
        s = res.index[0]
        RET["bh"][t] = close.pct_change(fill_method=None).loc[s:].fillna(0.0)
        RET["base1x"][t] = res["ret"]
    baskets = {k: tp.basket(pd.DataFrame(v), vt.MIN_MARKETS)[0] for k, v in RET.items()}
    common = baskets["bh"].index.intersection(baskets["base1x"].index)
    return pd.DataFrame({k: v.reindex(common) for k, v in baskets.items()})


def _pp(v: float) -> str:
    return f"{v * 100:+.2f} Pp"


def main() -> None:
    from qlab.data import risk_free_daily
    import check_h12_robust_basket as h12

    df = laden_csv()
    print(f"H15 Bootstrap-Konfidenz: {len(df)} gepaarte Tage {df.index[0].date()} bis {df.index[-1].date()} "
          f"(Quelle {IN_RET.name}), {N_DRAWS} Ziehungen, mittlere Blocklaenge {MEAN_BLOCK}, Seed {MASTER_SEED}\n")

    # Abgleich: neu berechnen und gegen die CSV vergleichen
    try:
        neu = neu_berechnen()
        gem = df.index.intersection(neu.index)
        diff = float((df.loc[gem] - neu.loc[gem]).abs().max().max())
        print(f"Abgleich Neuberechnung gegen CSV: {len(gem)} gemeinsame Tage (CSV {len(df)}, neu {len(neu)}), "
              f"max. Abweichung {diff:.2e}\n")
        abgleich = {"tage_csv": len(df), "tage_neu": len(neu), "max_abw": diff}
    except Exception as exc:
        print(f"Abgleich nicht moeglich: {exc}\n")
        abgleich = {"tage_csv": len(df), "tage_neu": np.nan, "max_abw": np.nan}

    rf = risk_free_daily(df.index).reindex(df.index).fillna(0.0).to_numpy(float)
    ppy = metrics.periods_per_year(df.index)
    r_a, r_b = df["base1x"].to_numpy(float), df["bh"].to_numpy(float)

    # Punktschaetzer und Kontrolle gegen konstanz (H12)
    pt = {"base1x": kennzahlen(r_a, rf, ppy), "bh": kennzahlen(r_b, rf, ppy)}
    rf_s = pd.Series(rf, index=df.index)
    ref = {"base1x": h12.konstanz(df["base1x"], rf_s), "bh": h12.konstanz(df["bh"], rf_s)}
    print("Punktschaetzer (ganzer Zeitraum; Kontrollwert aus konstanz in Klammern):")
    for n_ in ("base1x", "bh"):
        print(f"  {n_:<7} CAGR {pt[n_]['cagr'] * 100:6.2f} % ({ref[n_]['cagr'] * 100:.2f}), MaxDD {pt[n_]['max_dd'] * 100:7.2f} % "
              f"({ref[n_]['max_dd'] * 100:.2f}), UPI {pt[n_]['upi']:.3f} ({ref[n_]['upi']:.3f}), "
              f"Sharpe {pt[n_]['sharpe']:.3f} ({ref[n_]['sharpe']:.3f})")
    print()

    draws = bootstrap(r_a, r_b, rf, ppy)
    res = auswerten(draws)
    labels = {"cagr": "CAGR-Differenz", "max_dd": "MaxDD-Differenz", "upi": "UPI-Differenz", "sharpe": "Sharpe-Differenz"}
    print("Differenzen base1x minus B&H (Bootstrap, 90-%-Intervall = 5.-95. Perzentil):")
    for k in KEYS:
        s = res[k]
        if k in ("cagr", "max_dd"):
            txt = f"Median {_pp(s['median'])}, [{_pp(s['p05'])}; {_pp(s['p95'])}]"
        else:
            txt = f"Median {s['median']:+.3f}, [{s['p05']:+.3f}; {s['p95']:+.3f}]"
        print(f"  {labels[k]:<17} {txt}; Anteil Ziehungen > 0: {s['share_pos']:.1%}")
    print(f"\n  P(CAGR(base1x) < CAGR(B&H)) = {res['p_cagr_lower']:.1%}  (nur berichtet, kein Kriterium)")
    ok = res["verlustvorteil_belegt"]
    print(f"\nKriterium H15: 5. Perzentil der MaxDD-Differenz = {_pp(res['max_dd']['p05'])} > 0 -> "
          f"{'Verlustvorteil BELEGT (bestanden)' if ok else 'Verlustvorteil NICHT belegt (nicht bestanden)'}")

    # Empfindlichkeit gegen den Seed (informativ)
    seed_rows = [{"seed": MASTER_SEED, "p05_maxdd": res["max_dd"]["p05"], "p95_maxdd": res["max_dd"]["p95"],
                  "p_cagr_lower": res["p_cagr_lower"], "verlustvorteil_belegt": ok}]
    for sd in CHECK_SEEDS:
        rr = auswerten(bootstrap(r_a, r_b, rf, ppy, seed=sd))
        seed_rows.append({"seed": sd, "p05_maxdd": rr["max_dd"]["p05"], "p95_maxdd": rr["max_dd"]["p95"],
                          "p_cagr_lower": rr["p_cagr_lower"], "verlustvorteil_belegt": rr["verlustvorteil_belegt"]})
    print("\nSeed-Empfindlichkeit (informativ):")
    for r in seed_rows:
        print(f"  Seed {r['seed']}: p05 MaxDD-Diff {_pp(r['p05_maxdd'])}, P(CAGR niedriger) {r['p_cagr_lower']:.1%}, "
              f"Kriterium {'erfuellt' if r['verlustvorteil_belegt'] else 'nicht erfuellt'}")

    rows = []
    for k in KEYS:
        s = res[k]
        rows.append({"kennzahl": k, "punkt_base1x": pt["base1x"][k], "punkt_bh": pt["bh"][k],
                     "punkt_diff": pt["base1x"][k] - pt["bh"][k], "p05": s["p05"], "median": s["median"],
                     "p95": s["p95"], "anteil_diff_pos": s["share_pos"], "n_ziehungen": s["n"]})
    rows.append({"kennzahl": "P(CAGR base1x < CAGR B&H)", "median": res["p_cagr_lower"]})
    rows.append({"kennzahl": "kriterium_verlustvorteil_belegt", "median": float(ok)})
    rows.append({"kennzahl": "abgleich_max_abw_csv_vs_neu", "median": abgleich["max_abw"]})
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT_STATS, index=False, encoding="utf-8", float_format="%.6f")
    draws.to_csv(OUT_DRAWS, index=False, encoding="utf-8", float_format="%.8f")
    pd.DataFrame(seed_rows).to_csv(OUT_SEEDS, index=False, encoding="utf-8", float_format="%.6f")
    print(f"\nCSV gespeichert: {OUT_STATS}\nCSV gespeichert: {OUT_DRAWS}\nCSV gespeichert: {OUT_SEEDS}")


if __name__ == "__main__":
    main()
