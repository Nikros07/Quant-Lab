"""H16: Timing-Luck und Tranchen (docs/HYPOTHESEN.md, Pruefblock P1, Eintrag H16).

Regel (wie vorab registriert):
* Statt am Monatsende wird alle 21 Handelstage entschieden, mit Phasenverschiebung phi = 0..20 (21 Laeufe).
  Entscheidungstage sind die Positionen phi, phi + 21, phi + 42, ... der Handelstage-Reihe des Marktes.
* Signal an = Schlusskurs am Entscheidungstag t >= Mittel der 12 Schlusskurse bei t, t-21, ..., t-231
  (der Entscheidungstag und die 11 davor liegenden im Abstand von 21 Handelstagen). Das Signal gilt bis zur
  naechsten Entscheidung.
* Ausfuehrung zum Schluss von t+1, wirksam fuer die Rendite ab t+2. Rest wie `base1x`/sleeve2 (H12): Gewicht 1,0 bei
  LONG sonst 0, 10 bp je Seite auf |Delta Gewicht|, Cash zum US-RF, ohne Hebel, ohne Steuer.
* `tranche21` = Mittel der 21 Phasen-Renditen je Markt (je 1/21), danach gleichgewichteter Korb.
* 17 Maerkte, gleichgewichteter Korb (basket aus check_trend_portfolio), 1991-02 bis 2022-12, Holdout zu.
* Alle 21 Phasen-Koerbe, `tranche21` und `base1x` (Monatsende-Entscheidung, nicht Teil der 21 Phasen) werden auf dem
  gemeinsamen Index verglichen.

Kriterium (Streuung): berichtet wird die Spannweite (max - min) der 21 Phasen-Laeufe in CAGR, MaxDD, UPI.
"Timing-Luck gross", wenn Spannweite UPI > 0,25 ODER Spannweite MaxDD > 3 Pp.
Kriterium Tranche: `tranche21` besser als der Median der 21 Phasen-Laeufe in UPI UND in MaxDD.
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

TRADING_DAYS = 252
STEP = 21                     # Abstand der Entscheidungen in Handelstagen
N_MA = 12                     # Anzahl Schlusskurse im Mittel (t, t-21, ..., t-231)
PHASES = tuple(range(STEP))   # phi = 0..20
OUT_DIR = ROOT / "results"
OUT_STATS = OUT_DIR / "H16_phasen_kennzahlen.csv"
OUT_RANGE = OUT_DIR / "H16_spannweite_kriterien.csv"
OUT_RET = OUT_DIR / "H16_basket_returns.csv"

LUCK_UPI = 0.25               # Spannweite UPI, ab der "Timing-Luck gross"
LUCK_DD = 0.03                # Spannweite MaxDD (3 Pp), ab der "Timing-Luck gross"


def sleeve_phase(close: pd.Series, rf: pd.Series, phi: int, *, step: int = STEP, n_ma: int = N_MA,
                 bps: float = 10.0) -> pd.DataFrame:
    """Ein Markt-Sleeve mit 21-Tage-Entscheidungsraster und Phase phi. Gibt ret, pos je Handelstag ab dem Start zurueck.

    * Entscheidungstage: Positionen i = phi, phi + step, ... der Reihe; gueltig ab i >= (n_ma - 1) * step.
    * Signal: close[i] >= Mittel(close[i - j*step], j = 0..n_ma-1); ist das Mittel nicht endlich, wird die Entscheidung
      uebersprungen (alte Position bleibt, wie sleeve2). Wie sleeve2 ist das Gewicht 0, wenn sigma (EWMA, HWZ 20) nicht
      endlich oder <= 0 ist; sonst 1,0 bei LONG.
    * Wirksam ab i+2 (Ausfuehrung Schluss i+1); Entscheidungen mit i+2 >= n entfallen. Start = erster gueltiger Entscheidungstag.
    * ret_d = pos_d r_d + (1 - pos_d) rf_d - |pos_d - pos_{d-1}| * bps / 1e4.
    """
    if not (0 <= phi < step):
        raise ValueError(f"phi muss in 0..{step - 1} liegen")
    close = close.astype(float)
    idx = close.index
    n = len(idx)
    c = close.to_numpy(float)
    r = close.pct_change(fill_method=None)
    sigma = np.sqrt((r ** 2).ewm(halflife=20, adjust=False).mean() * TRADING_DAYS).to_numpy(float)

    first = (n_ma - 1) * step
    ma = np.full(n, np.nan)
    if n > first:
        acc = np.zeros(n - first)
        for j in range(n_ma):
            acc += c[first - j * step: n - j * step]       # Kurse bei i - j*step fuer i = first..n-1
        ma[first:] = acc / n_ma                              # NaN pflanzt sich fort (wie rolling().mean())
    pos_i = np.arange(phi, n, step)
    pos_i = pos_i[pos_i >= first]
    valid = pos_i[np.isfinite(ma[pos_i])]
    if len(valid) == 0:
        raise ValueError("kein gueltiger Entscheidungstag (zu wenige Daten)")
    s_i = int(valid[0])

    dec = np.full(n, np.nan)
    for i in valid:
        if i + 2 >= n:
            continue
        st = 1.0 if c[i] >= ma[i] else 0.0
        scale = 1.0 if (np.isfinite(sigma[i]) and sigma[i] > 0) else 0.0
        dec[i + 2] = st * scale
    pos = pd.Series(dec).ffill().fillna(0.0).to_numpy()

    r0 = np.nan_to_num(r.to_numpy(float))
    rf_a = rf.reindex(idx).ffill().fillna(0.0).to_numpy(float)
    p = pos[s_i:]
    prev = np.concatenate([[0.0], p[:-1]])
    ret = p * r0[s_i:] + (1.0 - p) * rf_a[s_i:] - np.abs(p - prev) * bps / 1e4
    return pd.DataFrame({"ret": ret, "pos": p}, index=idx[s_i:])


def tranche_returns(phase_rets: dict) -> pd.Series:
    """Mittel der Phasen-Renditen eines Marktes (je 1/Anzahl). Erst ab dem Tag, an dem alle Phasen gestartet sind."""
    df = pd.concat(list(phase_rets.values()), axis=1)
    return df.mean(axis=1, skipna=False).dropna()


def spread(vals: pd.Series) -> float:
    """Spannweite max - min."""
    v = vals.dropna()
    return float(v.max() - v.min())


def evaluate(K: dict, phase_names: list) -> dict:
    """Kriterien aus den Kennzahlen K[name] (Dicts mit cagr, max_dd, upi). Gibt die Kennwerte und die Urteile zurueck."""
    cagr = pd.Series({n: K[n]["cagr"] for n in phase_names})
    dd = pd.Series({n: K[n]["max_dd"] for n in phase_names})
    upi = pd.Series({n: K[n]["upi"] for n in phase_names})
    rng = {"cagr": spread(cagr), "max_dd": spread(dd), "upi": spread(upi)}
    luck = bool(rng["upi"] > LUCK_UPI or rng["max_dd"] > LUCK_DD)
    med_upi, med_dd = float(upi.median()), float(dd.median())
    t = K["tranche21"]
    tr_upi = bool(t["upi"] > med_upi)
    tr_dd = bool(t["max_dd"] > med_dd)      # MaxDD ist negativ; "besser" = weniger negativ
    return {"range": rng, "luck": luck, "median_upi": med_upi, "median_dd": med_dd,
            "tranche_upi_ok": tr_upi, "tranche_dd_ok": tr_dd, "tranche_ok": tr_upi and tr_dd}


def _pct(v: float) -> str:
    return "–" if pd.isna(v) else f"{v * 100:.2f} %"


def _num(v: float, fmt: str = "{:.2f}") -> str:
    return "–" if pd.isna(v) else fmt.format(v)


def _lab(ok: bool) -> str:
    return "ERFÜLLT" if ok else "NICHT erfüllt"


def main() -> None:
    print(f"H16 Timing-Luck: {len(vt.MARKETS)} Maerkte, Entscheidung alle {STEP} Handelstage (Phasen 0..{STEP - 1}), "
          f"MA ueber {N_MA} Kurse, ohne Hebel, Auswertung bis {vt.END}, {vt.BPS:.0f} bp je Wechsel, "
          f"Ausfuehrung Schluss Folgetag, Cash = US-RF, ohne Steuer\n")
    phase_names = [f"phi{p:02d}" for p in PHASES]
    names = ["base1x"] + phase_names + ["tranche21"]
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
            base = h12.sleeve2(close, rf, lengths=(12,), target=None)
            ph = {p: sleeve_phase(close, rf, p)["ret"] for p in PHASES}
        except Exception as exc:
            print(f"[{t}] Sleeve nicht berechenbar, uebersprungen: {exc}")
            skipped.append(t)
            continue
        RET["base1x"][t] = base["ret"]
        for p in PHASES:
            RET[f"phi{p:02d}"][t] = ph[p]
        RET["tranche21"][t] = tranche_returns(ph)
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
    print("(1) Kennzahlen je Korb (gemeinsamer Index):")
    print(h12._table(K, names).to_string())

    ev = evaluate(K, phase_names)
    rg = ev["range"]
    print("\n(2) Spannweite der 21 Phasen-Laeufe (max - min):")
    print(f"  CAGR   {rg['cagr'] * 100:.2f} Pp   (min {_pct(min(K[n]['cagr'] for n in phase_names))}, "
          f"max {_pct(max(K[n]['cagr'] for n in phase_names))})")
    print(f"  MaxDD  {rg['max_dd'] * 100:.2f} Pp   (schlechtester {_pct(min(K[n]['max_dd'] for n in phase_names))}, "
          f"bester {_pct(max(K[n]['max_dd'] for n in phase_names))})")
    print(f"  UPI    {rg['upi']:.3f}      (min {_num(min(K[n]['upi'] for n in phase_names))}, "
          f"max {_num(max(K[n]['upi'] for n in phase_names))})")
    print(f"  Timing-Luck gross (UPI-Spanne > {LUCK_UPI} oder MaxDD-Spanne > {LUCK_DD * 100:.0f} Pp): {'JA' if ev['luck'] else 'NEIN'}")

    B, T = K["base1x"], K["tranche21"]
    print("\n(3) Tranche gegen Median der 21 Phasen:")
    print(f"  UPI    tranche21 {_num(T['upi'], '{:.3f}')} > Median {ev['median_upi']:.3f}: {_lab(ev['tranche_upi_ok'])}")
    print(f"  MaxDD  tranche21 {_pct(T['max_dd'])} besser als Median {_pct(ev['median_dd'])}: {_lab(ev['tranche_dd_ok'])}")
    print(f"  Tranchen-Kriterium gesamt: {_lab(ev['tranche_ok'])}")
    print(f"\n(4) Referenz base1x (Monatsende, nicht in den 21 Phasen): CAGR {_pct(B['cagr'])}, MaxDD {_pct(B['max_dd'])}, "
          f"UPI {_num(B['upi'], '{:.3f}')}; Rang in UPI unter 22 (21 Phasen + base1x): "
          f"{1 + sum(K[n]['upi'] > B['upi'] for n in phase_names)}")

    rows = [{"Serie": n, **K[n]} for n in names]
    rng_rows = [
        {"Groesse": "Spannweite CAGR (Pp)", "Wert": rg["cagr"] * 100},
        {"Groesse": "Spannweite MaxDD (Pp)", "Wert": rg["max_dd"] * 100},
        {"Groesse": "Spannweite UPI", "Wert": rg["upi"]},
        {"Groesse": "Median UPI Phasen", "Wert": ev["median_upi"]},
        {"Groesse": "Median MaxDD Phasen", "Wert": ev["median_dd"]},
        {"Groesse": "tranche21 UPI", "Wert": T["upi"]},
        {"Groesse": "tranche21 MaxDD", "Wert": T["max_dd"]},
        {"Groesse": "Timing-Luck gross (1=ja)", "Wert": float(ev["luck"])},
        {"Groesse": "Tranche UPI besser (1=ja)", "Wert": float(ev["tranche_upi_ok"])},
        {"Groesse": "Tranche MaxDD besser (1=ja)", "Wert": float(ev["tranche_dd_ok"])},
        {"Groesse": "Tranchen-Kriterium erfuellt (1=ja)", "Wert": float(ev["tranche_ok"])},
    ]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT_STATS, index=False, encoding="utf-8", float_format="%.6f")
    pd.DataFrame(rng_rows).to_csv(OUT_RANGE, index=False, encoding="utf-8", float_format="%.6f")
    rb = R.copy()
    rb.index.name = "date"
    rb.reset_index().assign(date=lambda d: d["date"].dt.date.astype(str)).to_csv(
        OUT_RET, index=False, encoding="utf-8", float_format="%.10f")
    print(f"\nCSV gespeichert: {OUT_STATS}")
    print(f"CSV gespeichert: {OUT_RANGE}")
    print(f"CSV gespeichert: {OUT_RET}")


if __name__ == "__main__":
    main()
