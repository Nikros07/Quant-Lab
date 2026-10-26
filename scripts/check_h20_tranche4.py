"""H20: Tranchen auf 4 Tage verteilt (docs/HYPOTHESEN.md, Eintrag H20).

Regel (wie vorab registriert):
* Wie H16: Entscheidung alle 21 Handelstage, Phasen phi = 0..20 je Markt (h16.sleeve_phase).
* `tranche4` = Mittel der vier Phasen phi in {0, 5, 10, 15}, je Gewicht 1/4 (gleiche Methode wie
  h16.tranche_returns). Erst ab dem Tag, an dem alle vier Phasen gestartet sind.
* Vergleich: `base1x` (Monatsende, h12.sleeve2), die 21 Einzelphasen (Median), `tranche21` (aus H16-Logik).
* Gemeinsamer Korb (tp.basket, MIN_MARKETS) fuer alle Serien, gemeinsamer Index, Kennzahlen mit h12.konstanz.

Kriterium (exakt wie registriert): `tranche4` besteht, wenn
  (a) MaxDD besser (weniger negativ) als der Median der 21 Einzelphasen-MaxDD UND
  (b) UPI nicht niedriger als der Median der 21 Einzelphasen-UPI UND
  (c) CAGR nicht mehr als 0,7 Pp unter base1x-CAGR.
Zusaetzlich informativ: tranche21, base1x, Spannweite der 21 Phasen, Halbzeiten (vt.FIRST_HALF / vt.SECOND_HALF).
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
import check_h16_timing_luck as h16
import check_trend_portfolio as tp
import check_trend_vt_basket as vt
from qlab.data import risk_free_daily

PHASES4 = (0, 5, 10, 15)                              # Phasen der Tranche (je 1/4)
PHASE_NAMES = [f"phi{p:02d}" for p in h16.PHASES]     # 21 Einzelphasen
SERIES = ["base1x", "tranche4", "tranche21"]
OUT_DIR = ROOT / "results"
OUT_STATS = OUT_DIR / "H20_tranche4.csv"
OUT_RET = OUT_DIR / "H20_basket_returns.csv"
CAGR_GAP = 0.007                                      # (c): hoechstens 0,7 Pp unter base1x


def base1x_returns(close: pd.Series, rf: pd.Series) -> pd.Series:
    """Monatsende-Entscheidung 12-Monats-MA (H12-Sleeve ohne Vol-Skalierung)."""
    return h12.sleeve2(close, rf, lengths=(12,), target=None)["ret"]


def tranche4_returns(phase_rets: dict) -> pd.Series:
    """Gleich gewichtetes Mittel der Phasen 0, 5, 10, 15 (je 1/4). Erst ab dem Tag, an dem alle 4 gestartet sind."""
    return h16.tranche_returns({p: phase_rets[p] for p in PHASES4})


def criterion(K: dict, phase_names: list = PHASE_NAMES) -> dict:
    """H20-Kriterium aus den Kennzahlen K[name] (Dicts mit cagr, max_dd, upi). NaN gilt als nicht erfuellt."""
    dd_med = float(pd.Series({n: K[n]["max_dd"] for n in phase_names}).median())
    upi_med = float(pd.Series({n: K[n]["upi"] for n in phase_names}).median())
    t, b = K["tranche4"], K["base1x"]
    a = bool(t["max_dd"] > dd_med)                    # (a) weniger negativ als Median
    bb = bool(t["upi"] >= upi_med)                    # (b) nicht niedriger als Median
    c = bool(t["cagr"] >= b["cagr"] - CAGR_GAP)       # (c) hoechstens 0,7 Pp unter base1x
    return {"median_dd": dd_med, "median_upi": upi_med, "a": a, "b": bb, "c": c,
            "gap_cagr": float(t["cagr"] - b["cagr"]), "ok": bool(a and bb and c)}


def _lab(ok: bool) -> str:
    return "ERFÜLLT" if ok else "NICHT erfüllt"


def _pct(v: float) -> str:
    return "–" if pd.isna(v) else f"{v * 100:.2f} %"


def _num(v: float, fmt: str = "{:.3f}") -> str:
    return "–" if pd.isna(v) else fmt.format(v)


def main() -> None:
    print(f"H20 Tranche4: {len(vt.MARKETS)} Maerkte, Phasen {PHASES4} je 1/4 (Entscheidung alle {h16.STEP} Handelstage), "
          f"Auswertung bis {vt.END}, {vt.BPS:.0f} bp je Wechsel, Ausfuehrung Schluss Folgetag, Cash = US-RF, ohne Steuer\n")
    names = ["base1x"] + PHASE_NAMES + ["tranche21", "tranche4"]
    RET = {k: {} for k in names}
    skipped = []
    for t in vt.MARKETS:
        try:
            close = vt.load_market(t)
        except Exception as exc:
            print(f"[{t}] keine Daten, uebersprungen: {exc}")
            skipped.append(t)
            continue
        rf = risk_free_daily(close.index)
        try:
            base = base1x_returns(close, rf)
            ph = {p: h16.sleeve_phase(close, rf, p)["ret"] for p in h16.PHASES}
        except Exception as exc:
            print(f"[{t}] Sleeve nicht berechenbar, uebersprungen: {exc}")
            skipped.append(t)
            continue
        RET["base1x"][t] = base
        for p in h16.PHASES:
            RET[f"phi{p:02d}"][t] = ph[p]
        RET["tranche21"][t] = h16.tranche_returns(ph)
        RET["tranche4"][t] = tranche4_returns(ph)
    print(f"Maerkte mit Daten: {len(RET['base1x'])} von {len(vt.MARKETS)}; uebersprungen: {skipped or 'keine'}\n")

    baskets = {name: tp.basket(pd.DataFrame(RET[name]), vt.MIN_MARKETS) for name in names}
    common = None
    for name in names:
        ix = baskets[name][0].index
        common = ix if common is None else common.intersection(ix)
    R = pd.DataFrame({name: baskets[name][0].reindex(common) for name in names})
    rf_c = risk_free_daily(common)
    print(f"Gemeinsamer Index: {common[0].date()} bis {common[-1].date()}, {len(common)} Handelstage\n")

    K = {name: h12.konstanz(R[name], rf_c) for name in names}
    crit = criterion(K)
    rg = {k: h16.spread(pd.Series({n: K[n][k] for n in PHASE_NAMES})) for k in ("cagr", "max_dd", "upi")}

    print("(1) Kennzahlen (gemeinsamer Index):")
    print(h12._table(K, SERIES).to_string())
    print(f"\n(2) Median der 21 Einzelphasen: MaxDD {_pct(crit['median_dd'])}, UPI {_num(crit['median_upi'])}")
    print(f"    Spannweite der 21 Phasen (max - min): CAGR {rg['cagr'] * 100:.2f} Pp, "
          f"MaxDD {rg['max_dd'] * 100:.2f} Pp, UPI {rg['upi']:.3f}")
    print(f"    tranche4 MaxDD {_pct(K['tranche4']['max_dd'])}, UPI {_num(K['tranche4']['upi'])}, "
          f"CAGR {_pct(K['tranche4']['cagr'])}; base1x CAGR {_pct(K['base1x']['cagr'])}")

    print("\n(3) Kriterium H20:")
    print(f"  (a) MaxDD tranche4 {_pct(K['tranche4']['max_dd'])} besser als Median {_pct(crit['median_dd'])}: {_lab(crit['a'])}")
    print(f"  (b) UPI tranche4 {_num(K['tranche4']['upi'])} nicht niedriger als Median {_num(crit['median_upi'])}: {_lab(crit['b'])}")
    print(f"  (c) CAGR tranche4 {_pct(K['tranche4']['cagr'])} vs base1x {_pct(K['base1x']['cagr'])} "
          f"(Abstand {crit['gap_cagr'] * 100:+.2f} Pp, Grenze -0,70 Pp): {_lab(crit['c'])}")
    print(f"  Gesamturteil H20: {_lab(crit['ok'])}")

    # Halbzeiten (informativ)
    rows = []
    for name in names:
        rows.append({"Serie": name, "Abschnitt": "gesamt", **K[name]})
    print("\n(4) Halbzeiten (informativ):")
    for label, (a, b) in (("1991-2006", vt.FIRST_HALF), ("2007-2022", vt.SECOND_HALF)):
        sub = R.loc[a:b]
        rf_s = rf_c.loc[sub.index]
        Kh = {name: h12.konstanz(sub[name].dropna(), rf_s) for name in SERIES}
        for name in SERIES:
            rows.append({"Serie": name, "Abschnitt": label, **Kh[name]})
            print(f"  {label} {name:<10} CAGR {_pct(Kh[name]['cagr'])}, MaxDD {_pct(Kh[name]['max_dd'])}, "
                  f"UPI {_num(Kh[name]['upi'])}")

    rows.append({"Serie": "Median 21 Phasen", "Abschnitt": "gesamt",
                 **{k: float(np.median([K[n][k] for n in PHASE_NAMES])) for k in ("cagr", "max_dd", "upi")}})
    rows.append({"Serie": "Spannweite 21 Phasen", "Abschnitt": "gesamt", **rg})

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT_STATS, index=False, encoding="utf-8", float_format="%.6f")
    rb = R[SERIES].copy()
    rb.index.name = "date"
    rb.reset_index().assign(date=lambda d: d["date"].dt.date.astype(str)).to_csv(
        OUT_RET, index=False, encoding="utf-8", float_format="%.10f")
    print(f"\nCSV gespeichert: {OUT_STATS}")
    print(f"CSV gespeichert: {OUT_RET}")


if __name__ == "__main__":
    main()
