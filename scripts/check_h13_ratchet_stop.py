"""H13: Nachziehender Stop ("Ratsche") im 17-Maerkte-Korb (docs/HYPOTHESEN.md, Eintrag H13).

Je Markt ein Sleeve (sleeve3): Monats-MA12-Zustand wie base1x (Gewicht 1,0 bei LONG, kein Hebel, keine Vol-Skalierung),
Ausfuehrung zum Schluss des Folgetags, 10 bp je Seite, Cash = US-RF. Stop-Arten:
  * "chand":         wie H11 `trail` (HH x (1 - m sigma_t / sqrt(12)), darf zurueckweichen) - nur Referenz
  * "chand_ratchet": Stop = max(bisheriger Stop, HH x (1 - m sigma_t / sqrt(12))), sinkt nie
  * "steps":         R = m sigma_E / sqrt(12) x E; Anfangs-Stop E - R; bei HH >= E + k R (k >= 1) Stop E + (k - 1) R,
                     also Break-even bei +1R, danach je +1R eine Stufe nach oben; sinkt nie
Schliesst der Kurs unter dem Stop am Tag t, Ausstieg zum Schluss von t+1 (pos ab t+2 = 0); Wiedereinstieg nur am
naechsten Monatsende mit Signal LONG. Der Monatsfilter steigt unabhaengig davon aus.
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
from qlab.calendar import month_end_flags
from qlab.data import risk_free_daily

TRADING_DAYS = 252
SQRT12 = float(np.sqrt(12.0))
OUT_DIR = ROOT / "results"
OUT_STATS = OUT_DIR / "H13_ratchet_stop.csv"
OUT_RET = OUT_DIR / "H13_basket_returns.csv"
FIRST_HALF = vt.FIRST_HALF
SECOND_HALF = vt.SECOND_HALF

RUNS = {
    "base1x": dict(stop_mode=None),
    "chand": dict(stop_mode="chand"),
    "chand_ratchet": dict(stop_mode="chand_ratchet"),
    "steps": dict(stop_mode="steps"),
}
NEW_RUNS = ["chand_ratchet", "steps"]


def sleeve3(close: pd.Series, rf: pd.Series, *, stop_mode: str | None = None, m: float = 2.0,
            bps: float = 10.0) -> pd.DataFrame:
    """Ein Markt-Sleeve nach H13 (siehe Modul-Docstring). Gibt ret, pos, stop je Handelstag ab dem Sleeve-Start zurueck."""
    if stop_mode not in (None, "chand", "chand_ratchet", "steps"):
        raise ValueError(f"unbekannte stop_mode: {stop_mode}")
    close = close.astype(float)
    idx = close.index
    r = close.pct_change(fill_method=None)
    sigma = np.sqrt((r ** 2).ewm(halflife=20, adjust=False).mean() * TRADING_DAYS)

    state = vt.monthly_state(close)
    if state.empty:
        raise ValueError("kein gueltiger Monatszustand (zu wenige Monatsenden mit MA12)")
    s_i = idx.get_loc(state.index[0])
    flags = month_end_flags(idx).to_numpy()
    st = state.reindex(idx).fillna(False).to_numpy(bool)
    sig = sigma.to_numpy(float)
    c = close.to_numpy(float)
    r0 = np.nan_to_num(r.to_numpy(float))
    rf_a = rf.reindex(idx).ffill().fillna(0.0).to_numpy(float)

    n = len(idx)
    pos = np.zeros(n)
    stop_arr = np.full(n, np.nan)
    chg: dict[int, tuple[float, float]] = {}
    cur = 0.0
    stopped = False
    HH = E = D = lvl = np.nan
    for i in range(s_i, n):
        if i in chg:
            w_new, sig_dec = chg.pop(i)
            if w_new > 0 and cur == 0.0:               # Einstieg: Ausfuehrung am Schluss von i-1
                E = c[i - 1]
                HH = E
                D = m * sig_dec / SQRT12 * E if np.isfinite(sig_dec) else np.nan
                lvl = E - D if (stop_mode == "steps" and np.isfinite(D) and D > 0) else np.nan
            cur = w_new
        pos[i] = cur

        trig = False
        if cur > 0 and not stopped:
            HH = max(HH, c[i])
            if stop_mode == "chand":
                lvl = HH * (1.0 - m * sig[i] / SQRT12) if np.isfinite(sig[i]) else np.nan
            elif stop_mode == "chand_ratchet":
                cand = HH * (1.0 - m * sig[i] / SQRT12) if np.isfinite(sig[i]) else np.nan
                lvl = np.fmax(lvl, cand)
            elif stop_mode == "steps" and np.isfinite(D) and D > 0:
                k = np.floor((HH - E) / D)
                cand = E + (k - 1.0) * D if k >= 1 else E - D
                lvl = np.fmax(lvl, cand)
            if stop_mode is not None and np.isfinite(lvl):
                stop_arr[i] = lvl
                if c[i] < lvl:
                    trig = True
                    chg[i + 2] = (0.0, np.nan)         # Ausstieg: Schluss t+1, pos ab t+2 = 0
                    stopped = True

        if not trig and flags[i]:
            w = 1.0 if (st[i] and np.isfinite(sig[i]) and sig[i] > 0) else 0.0
            if not stopped:
                chg[i + 2] = (w, sig[i])
            elif w > 0:                                # Wiedereinstieg am naechsten Monatsende mit LONG
                chg[i + 2] = (w, sig[i])
                stopped = False

    p = pos[s_i:]
    prev = np.concatenate([[0.0], p[:-1]])
    ret = p * r0[s_i:] + (1.0 - p) * rf_a[s_i:] - np.abs(p - prev) * bps / 1e4
    return pd.DataFrame({"ret": ret, "pos": p, "stop": stop_arr[s_i:]}, index=idx[s_i:])


def main() -> None:
    print(f"H13 Nachziehender Stop: {len(vt.MARKETS)} Maerkte, ohne Hebel, Auswertung bis {vt.END}, {vt.BPS:.0f} bp je Wechsel, "
          f"Ausfuehrung Schluss Folgetag, Cash = US-RF, ohne Steuer\n")
    names = ["bh"] + list(RUNS)
    RET = {k: {} for k in names}
    skipped = []
    for t in vt.MARKETS:
        try:
            close = vt.load_market(t)
            rf = risk_free_daily(close.index)
            res = {name: sleeve3(close, rf, **kw) for name, kw in RUNS.items()}
        except Exception as exc:
            print(f"[{t}] uebersprungen: {exc}")
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

    K = {name: h12.konstanz(R[name], rf_c) for name in names}
    print("(1) Kennzahlen je Korb (ganzer Zeitraum):")
    print(h12._table(K, names).to_string())
    halves = {}
    for lab, (a, b) in [("1991-2006", FIRST_HALF), ("2007-2022", SECOND_HALF)]:
        halves[lab] = {name: h12.konstanz(R[name].loc[a:b], rf_c.loc[a:b]) for name in names}
        print(f"\n(2) Haelfte {lab}:")
        print(h12._table(halves[lab], names).to_string())
    sp = {}
    if "^GSPC" in RET["bh"]:
        sp_rf = risk_free_daily(RET["bh"]["^GSPC"].index)
        sp = {name: h12.konstanz(RET[name]["^GSPC"], sp_rf) for name in names}
        print(f"\n(3) S&P 500 allein (ab {RET['bh']['^GSPC'].index[0].date()}):")
        print(h12._table(sp, names).to_string())

    B = K["base1x"]
    print("\n(4) Kriterien H13 gegen base1x:")
    verdict = {}
    for name in NEW_RUNS + ["chand"]:
        V = K[name]
        a = V["max_dd"] - B["max_dd"] >= 0.01
        b = V["cagr"] >= B["cagr"] - 0.005
        c_ = V["sharpe"] >= B["sharpe"]
        d = V["upi"] >= B["upi"]
        e = (halves["1991-2006"][name]["upi"] >= halves["1991-2006"]["base1x"]["upi"]
             and halves["2007-2022"][name]["upi"] >= halves["2007-2022"]["base1x"]["upi"])
        f = bool(sp) and sp[name]["upi"] >= sp["base1x"]["upi"]
        verdict[name] = all([a, b, c_, d, e, f])
        print(f"  {name:<14} (a) MaxDD {h12._pct(V['max_dd'])} ({(V['max_dd'] - B['max_dd']) * 100:+.2f} Pp) {h12._lab(a)} | "
              f"(b) CAGR {h12._pct(V['cagr'])} ({(V['cagr'] - B['cagr']) * 100:+.2f} Pp) {h12._lab(b)} | "
              f"(c) Sharpe {h12._num(V['sharpe'], '{:.3f}')} vs {h12._num(B['sharpe'], '{:.3f}')} {h12._lab(c_)} | "
              f"(d) UPI {h12._num(V['upi'], '{:.3f}')} vs {h12._num(B['upi'], '{:.3f}')} {h12._lab(d)} | "
              f"(e) Haelften UPI {h12._lab(e)} | (f) S&P-UPI {h12._lab(f)} -> gesamt {h12._lab(verdict[name])}")

    rows = []
    for scope, KK in [("ganz", K), ("1991-2006", halves["1991-2006"]), ("2007-2022", halves["2007-2022"])] + (
            [("S&P allein", sp)] if sp else []):
        for nme in names:
            rows.append({"Serie": nme, "Abschnitt": scope, **KK[nme]})
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
