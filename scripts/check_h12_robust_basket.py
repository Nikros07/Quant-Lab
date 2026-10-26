"""H12: Konstanz-Optimierung des ungehebelten Korbs (docs/HYPOTHESEN.md, Eintrag H12).

Je Markt ein "Sleeve" (sleeve2): Gewicht = Mittel der binaeren Monats-Signale ueber `lengths` (Monatsschluss >= Mittel der
letzten L Monatsschluesse) mal Vol-Skalierung min(cap, target / sigma) (ohne Hebel: cap = 1). Entscheidung am Monatsende m,
Ausfuehrung zum Schluss von m+1, wirksam fuer die Rendite ab m+2 (wie H11). Kosten 10 bp je Seite auf |Delta Gewicht|,
Cash zum US-RF. Mit lengths=(12,) und target=None bzw. 0,15 entspricht sleeve2 exakt `base1x` bzw. `vt15_cap10` aus H11.
Der Korb ist der gleichgewichtete Mittelwert der Sleeves (basket aus check_trend_portfolio).

Auswahl und Kriterien: siehe H12 in docs/HYPOTHESEN.md (Auswahl nur auf der ersten Haelfte 1991-2006).
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

import check_trend_portfolio as tp
import check_trend_vt_basket as vt
from qlab import metrics
from qlab.calendar import month_end_flags
from qlab.data import risk_free_daily

TRADING_DAYS = 252
OUT_DIR = ROOT / "results"
OUT_STATS = OUT_DIR / "H12_robust_basket.csv"
OUT_RET = OUT_DIR / "H12_basket_returns.csv"

FIRST_HALF = vt.FIRST_HALF
SECOND_HALF = vt.SECOND_HALF

RUNS = {
    "base1x": dict(lengths=(12,), target=None),
    "vt15_cap10": dict(lengths=(12,), target=0.15),
    "vt20_cap10": dict(lengths=(12,), target=0.20),
    "vt25_cap10": dict(lengths=(12,), target=0.25),
    "ens3": dict(lengths=(6, 9, 12), target=None),
    "ens3_vt20": dict(lengths=(6, 9, 12), target=0.20),
}
CANDIDATES = ["vt15_cap10", "vt20_cap10", "vt25_cap10", "ens3", "ens3_vt20"]
NEW_RUNS = ["vt20_cap10", "vt25_cap10", "ens3", "ens3_vt20"]


def sleeve2(close: pd.Series, rf: pd.Series, *, lengths: tuple = (12,), target: float | None = None,
            cap: float = 1.0, bps: float = 10.0) -> pd.DataFrame:
    """Ein Markt-Sleeve nach H12. Gibt ret, pos, sigma je Handelstag ab dem Sleeve-Start zurueck.

    * Signal je Laenge L am Monatsende: Monatsschluss >= Mittel der letzten L Monatsschluesse (1.0 / 0.0); Gewicht der
      Signale = Mittel ueber `lengths`. Der Sleeve startet am ersten Monatsende, an dem alle Laengen gueltig sind.
    * Vol-Skalierung (target): scale = min(cap, target / sigma_m), sigma = sqrt(252 * EWMA(r^2, Halbwertszeit 20)),
      nur Daten bis zum Monatsende m. Ohne target: scale = 1. Ist sigma_m nicht endlich oder <= 0: scale = 0 (wie H11).
    * Gewichtswechsel: Entscheidung am Monatsende m, Ausfuehrung zum Schluss von m+1, wirksam ab dem Tag m+2.
    * ret_d = pos_d r_d + (1 - pos_d) rf_d - |pos_d - pos_{d-1}| * bps / 1e4 (ohne Hebel keine Finanzierungskosten).
    """
    if not lengths:
        raise ValueError("lengths darf nicht leer sein")
    if cap > 1.0:
        raise ValueError("H12 rechnet ohne Hebel: cap <= 1,0")
    close = close.astype(float)
    idx = close.index
    r = close.pct_change(fill_method=None)
    sigma = np.sqrt((r ** 2).ewm(halflife=20, adjust=False).mean() * TRADING_DAYS)

    flags = month_end_flags(idx).to_numpy()
    me = close[flags]
    parts = []
    for L in lengths:
        ma = me.rolling(L).mean()
        parts.append((me >= ma).astype(float).where(ma.notna()))
    st_me = pd.concat(parts, axis=1).mean(axis=1, skipna=False).dropna()
    if st_me.empty:
        raise ValueError("kein gueltiger Monatszustand (zu wenige Monatsenden)")
    s_i = idx.get_loc(st_me.index[0])

    n = len(idx)
    sig = sigma.to_numpy(float)
    dec = np.full(n, np.nan)
    for d, st in st_me.items():
        i = idx.get_loc(d)
        if i + 2 >= n:
            continue
        scale = 0.0
        if np.isfinite(sig[i]) and sig[i] > 0:
            scale = 1.0 if target is None else min(cap, target / sig[i])
        dec[i + 2] = st * scale
    pos = pd.Series(dec).ffill().fillna(0.0).to_numpy()

    r0 = np.nan_to_num(r.to_numpy(float))
    rf_a = rf.reindex(idx).ffill().fillna(0.0).to_numpy(float)
    p = pos[s_i:]
    prev = np.concatenate([[0.0], p[:-1]])
    ret = p * r0[s_i:] + (1.0 - p) * rf_a[s_i:] - np.abs(p - prev) * bps / 1e4
    return pd.DataFrame({"ret": ret, "pos": p, "sigma": sig[s_i:]}, index=idx[s_i:])


def ulcer_index(ret: pd.Series) -> float:
    nav = (1.0 + ret.dropna()).cumprod()
    dd = nav / nav.cummax() - 1.0
    return float(np.sqrt((dd ** 2).mean()))


def konstanz(ret: pd.Series, rf: pd.Series) -> dict:
    """Kennzahlen der Konstanz (siehe H12): UPI, Ulcer, Zeit unter -10 %, positive 36-Monats-Fenster, schlechtester 3J-CAGR."""
    ret = ret.dropna()
    d = metrics.summarize(ret, rf)
    nav = (1.0 + ret).cumprod()
    dd = nav / nav.cummax() - 1.0
    u = ulcer_index(ret)
    roll = ((nav / nav.shift(756)) ** (252.0 / 756.0) - 1.0).dropna()
    return {
        "cagr": d.get("cagr", np.nan), "vol": d.get("vol", np.nan), "sharpe": d.get("sharpe", np.nan),
        "max_dd": d.get("max_dd", np.nan), "calmar": d.get("calmar", np.nan),
        "ulcer": u, "upi": d.get("cagr", np.nan) / u if u > 0 else np.nan,
        "dd10": float((dd < -0.10).mean()),
        "pos36": float((roll > 0).mean()) if len(roll) else np.nan,
        "worst3y": float(roll.min()) if len(roll) else np.nan,
        "pos_years": d.get("pos_years", np.nan), "worst_year": d.get("worst_year", np.nan),
    }


def _pct(v: float) -> str:
    return "–" if pd.isna(v) else f"{v * 100:.2f} %"


def _num(v: float, fmt: str = "{:.2f}") -> str:
    return "–" if pd.isna(v) else fmt.format(v)


def _lab(ok: bool) -> str:
    return "ERFÜLLT" if ok else "NICHT erfüllt"


def _table(K: dict, names: list) -> pd.DataFrame:
    return pd.DataFrame({
        n: {"CAGR": _pct(K[n]["cagr"]), "Vol": _pct(K[n]["vol"]), "Sharpe": _num(K[n]["sharpe"]),
            "MaxDD": _pct(K[n]["max_dd"]), "Ulcer": _pct(K[n]["ulcer"]), "UPI": _num(K[n]["upi"]),
            "Zeit DD<-10%": _pct(K[n]["dd10"]), "36M>0": _pct(K[n]["pos36"]),
            "schl. 3J-CAGR": _pct(K[n]["worst3y"]), "pos. Jahre": _pct(K[n]["pos_years"]),
            "schl. Jahr": _pct(K[n]["worst_year"])} for n in names})


def main() -> None:
    print(f"H12 Konstanz-Optimierung: {len(vt.MARKETS)} Maerkte, ohne Hebel, Auswertung bis {vt.END}, "
          f"{vt.BPS:.0f} bp je Wechsel, Ausfuehrung Schluss Folgetag, Cash = US-RF, ohne Steuer\n")
    names = ["bh"] + list(RUNS)
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
            res = {name: sleeve2(close, rf, **kw) for name, kw in RUNS.items()}
        except Exception as exc:
            print(f"[{t}] Sleeve nicht berechenbar, uebersprungen: {exc}")
            skipped.append(t)
            continue
        s = res["base1x"].index[0]
        RET["bh"][t] = close.pct_change(fill_method=None).loc[s:].fillna(0.0)
        for name in RUNS:
            RET[name][t] = res[name]["ret"]
    print(f"Maerkte mit Daten: {len(RET['bh'])} von {len(vt.MARKETS)}; uebersprungen: {skipped or 'keine'}\n")

    baskets = {name: tp.basket(pd.DataFrame(RET[name]), vt.MIN_MARKETS) for name in names}
    common = None
    for name in names:
        ix = baskets[name][0].index
        common = ix if common is None else common.intersection(ix)
    R = pd.DataFrame({name: baskets[name][0].reindex(common) for name in names})
    rf_c = risk_free_daily(common)
    print(f"Gemeinsamer Index: {common[0].date()} bis {common[-1].date()}, {len(common)} Handelstage\n")

    K = {name: konstanz(R[name], rf_c) for name in names}
    print("(1) Kennzahlen je Korb (ganzer Zeitraum):")
    print(_table(K, names).to_string())

    halves = {}
    for lab, (a, b) in [("1991-2006", FIRST_HALF), ("2007-2022", SECOND_HALF)]:
        halves[lab] = {name: konstanz(R[name].loc[a:b], rf_c.loc[a:b]) for name in names}
        print(f"\n(2) Haelfte {lab}:")
        print(_table(halves[lab], names).to_string())

    # Auswahl nur auf der ersten Haelfte
    first, second = halves["1991-2006"], halves["2007-2022"]
    winner = max(CANDIDATES, key=lambda n: first[n]["upi"])
    print("\n(3) Auswahl nach UPI der ersten Haelfte (1991-2006):")
    for n in CANDIDATES:
        print(f"  {n:<12} UPI {_num(first[n]['upi'])}" + ("   <- Gewinner" if n == winner else ""))
    print(f"  Rang des Gewinners in der zweiten Haelfte (UPI): "
          f"{sorted(CANDIDATES, key=lambda n: -second[n]['upi']).index(winner) + 1} von {len(CANDIDATES)}")

    # S&P 500 allein (lange Reihe)
    sp = {}
    if "^GSPC" in RET["bh"]:
        sp_rf = risk_free_daily(RET["bh"]["^GSPC"].index)
        for name in names:
            sp[name] = konstanz(RET[name]["^GSPC"], sp_rf)
        print(f"\n(4) S&P 500 allein (ab {RET['bh']['^GSPC'].index[0].date()}):")
        print(_table(sp, names).to_string())

    W, B = K[winner], K["base1x"]
    crit_a = (W["upi"] >= 1.10 * B["upi"] and first[winner]["upi"] >= first["base1x"]["upi"]
              and second[winner]["upi"] >= second["base1x"]["upi"])
    crit_b = W["cagr"] >= B["cagr"] - 0.007
    crit_c = W["max_dd"] >= B["max_dd"] - 0.005
    crit_d = W["pos36"] >= B["pos36"] - 0.01
    crit_e = bool(sp) and sp[winner]["upi"] >= sp["base1x"]["upi"]
    total = crit_a and crit_b and crit_c and crit_d and crit_e
    print(f"\n(5) Kriterien H12 (Gewinner {winner} gegen base1x):")
    print(f"  (a) UPI {_num(W['upi'], '{:.3f}')} >= 1,10 x {_num(B['upi'], '{:.3f}')} und in beiden Haelften >= base1x "
          f"({_num(first[winner]['upi'])} / {_num(first['base1x']['upi'])}; {_num(second[winner]['upi'])} / "
          f"{_num(second['base1x']['upi'])}): {_lab(crit_a)}")
    print(f"  (b) CAGR {_pct(W['cagr'])} >= {_pct(B['cagr'])} - 0,7 Pp: {_lab(crit_b)}")
    print(f"  (c) MaxDD {_pct(W['max_dd'])} >= {_pct(B['max_dd'])} - 0,5 Pp: {_lab(crit_c)}")
    print(f"  (d) 36M>0 {_pct(W['pos36'])} >= {_pct(B['pos36'])} - 1 Pp: {_lab(crit_d)}")
    if sp:
        print(f"  (e) S&P allein UPI {_num(sp[winner]['upi'], '{:.3f}')} >= {_num(sp['base1x']['upi'], '{:.3f}')}: {_lab(crit_e)}")
    else:
        print("  (e) ^GSPC fehlt: NICHT erfuellbar")
    print(f"  Gesamt H12: {_lab(total)}")
    print("\n(6) Alle Kandidaten gegen base1x (informativ, keine Auswahl):")
    for n in CANDIDATES:
        print(f"  {n:<12} UPI {_num(K[n]['upi'])} ({K[n]['upi'] / B['upi'] - 1:+.1%}), CAGR {(K[n]['cagr'] - B['cagr']) * 100:+.2f} Pp, "
              f"MaxDD {(K[n]['max_dd'] - B['max_dd']) * 100:+.2f} Pp, Ulcer {_pct(K[n]['ulcer'])}")

    rows = []
    for scope, KK in [("ganz", K), ("1991-2006", first), ("2007-2022", second)] + ([("S&P allein", sp)] if sp else []):
        for n in names:
            rows.append({"Serie": n, "Abschnitt": scope, **KK[n]})
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT_STATS, index=False, encoding="utf-8", float_format="%.6f")
    rb = R.copy()
    rb.index.name = "date"
    rb.reset_index().assign(date=lambda d: d["date"].dt.date.astype(str)).to_csv(
        OUT_RET, index=False, encoding="utf-8", float_format="%.10f")
    print(f"\nCSV gespeichert: {OUT_STATS}")
    print(f"CSV gespeichert: {OUT_RET}")


if __name__ == "__main__":
    main()
