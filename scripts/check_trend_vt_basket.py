"""H11: Trend-Korb mit Volatilitaets-Skalierung und Hebel bis 1,5x (docs/HYPOTHESEN.md, Eintrag H11 und H11-Ergaenzung).

Je Markt ein "Sleeve" (Funktion sleeve): Monats-MA12-Zustand (monthly_state aus check_trend_multi_market),
Gewicht min(cap, target / sigma) bei LONG, Ausfuehrung zum Schluss des Folgetags, Kosten und
Finanzierungsaufschlag wie in H11. Optional Volatilitaets-Stop (trail_m) und Gewinnziel (rr).
Der Korb ist der gleichgewichtete Mittelwert der Sleeves (basket aus check_trend_portfolio).

Alle Regeln siehe Docstring von sleeve() und die H11-Ergaenzung in docs/HYPOTHESEN.md.
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

import check_trend_multi_market as h5
import check_trend_portfolio as tp
from qlab import metrics
from qlab.calendar import month_end_flags
from qlab.data import Panel, load_panel, risk_free_daily

END = h5.END
LOAD_START = h5.LOAD_START
MIN_YEARS = h5.MIN_YEARS
BPS = h5.BPS
MARKETS = tp.MARKETS                 # 17 Maerkte: H5-Liste ohne CL=F
MIN_MARKETS = tp.MIN_MARKETS         # 8
basket = tp.basket
monthly_state = h5.monthly_state
TRADING_DAYS = 252
SQRT12 = float(np.sqrt(12.0))
OUT_DIR = ROOT / "results"
OUT_STATS = OUT_DIR / "H11_vt_basket.csv"
OUT_RET = OUT_DIR / "H11_basket_returns.csv"

FIRST_HALF = ("1991-01-01", "2006-12-31")
SECOND_HALF = ("2007-01-01", "2022-12-31")

RUNS = {
    "base1x": dict(vol_scaled=False, cap=1.0),                                   # (B) H6-aehnlicher Vergleich
    "vt15_cap15": dict(target=0.15, cap=1.5),                                    # (C) HAUPTLAUF
    "vt15_cap10": dict(target=0.15, cap=1.0),                                    # (D)
    "trail": dict(target=0.15, cap=1.5, trail_m=2.0),                            # (E)
    "trail_rr": dict(target=0.15, cap=1.5, trail_m=2.0, rr=3.0),                 # (F)
    "stress": dict(target=0.15, cap=1.5, fin_markup=0.04),                       # (G) nur informativ
}
LABELS = {
    "bh": "B&H-Korb (A)",
    "base1x": "base1x (B, ohne Skalierung)",
    "vt15_cap15": "vt15_cap15 (C, Hauptlauf)",
    "vt15_cap10": "vt15_cap10 (D)",
    "trail": "trail (E)",
    "trail_rr": "trail_rr (F)",
    "stress": "Stress vt15_cap15, Aufschlag 4 % (G)",
}


def sleeve(close: pd.Series, rf: pd.Series, *, target: float = 0.15, cap: float = 1.5, vol_scaled: bool = True,
           trail_m: float | None = None, rr: float | None = None, bps: float = 10.0,
           fin_markup: float = 0.025) -> pd.DataFrame:
    """Ein Markt-Sleeve nach H11. Gibt ret, pos, state, sigma je Handelstag ab dem Sleeve-Start zurueck.

    * sigma_t = sqrt(252 * EWMA(r^2, Halbwertszeit 20)), nur Daten bis t.
    * Entscheidung am Monatsende m: Gewicht min(cap, target / sigma_m) bei LONG (sigma_m > 0), sonst 0.
      Ohne vol_scaled: 1.0 bei LONG. Ausfuehrung zum Schluss von m+1, wirksam fuer die Rendite von m+2.
    * Stop (trail_m): HH = hoechster Schlusskurs seit Einstieg; Stop_t = HH_t * (1 - trail_m * sigma_t / sqrt(12)).
      close_t < Stop_t -> Ausstieg, pos ab t+2 = 0. Gewinnziel (rr): E + rr * D mit D = trail_m * sigma_dec / sqrt(12) * E.
      close_t >= Ziel -> Ausstieg wie oben. Nach Stop-Ausstieg nur Wiedereinstieg am naechsten Monatsende mit LONG.
    * ret_d = pos_d r_d + (1 - pos_d) rf_d - max(pos_d - 1, 0) * fin_markup / 252 - |pos_d - pos_{d-1}| * bps / 1e4.
    """
    if rr is not None and trail_m is None:
        raise ValueError("rr braucht trail_m (der Risikoabstand kommt aus dem Stop)")
    close = close.astype(float)
    idx = close.index
    r = close.pct_change(fill_method=None)
    var = (r ** 2).ewm(halflife=20, adjust=False).mean()
    sigma = np.sqrt(var * TRADING_DAYS)

    state = monthly_state(close)                       # Zustand, nur an Monatsenden entschieden
    if state.empty:
        raise ValueError("kein gueltiger Monatszustand (zu wenige Monatsenden mit MA12)")
    s_i = idx.get_loc(state.index[0])                  # Sleeve-Start = erstes Monatsende mit Zustand
    flags = month_end_flags(idx).to_numpy()
    st = state.reindex(idx).fillna(False).to_numpy(bool)
    sig = sigma.to_numpy(float)
    c = close.to_numpy(float)
    r0 = np.nan_to_num(r.to_numpy(float))
    rf_a = rf.reindex(idx).ffill().fillna(0.0).to_numpy(float)

    n = len(idx)
    pos = np.zeros(n)
    chg: dict[int, tuple[float, float]] = {}           # Tag -> (neues Gewicht, sigma der Entscheidung)
    cur = 0.0
    stopped = False
    HH = E = D = np.nan
    for i in range(s_i, n):
        if i in chg:
            w_new, sig_dec = chg.pop(i)
            if w_new > 0 and cur == 0.0:               # Einstieg: Ausfuehrung am Schluss von i-1
                E = c[i - 1]
                HH = E
                if trail_m is not None:
                    D = trail_m * sig_dec / SQRT12 * E
            cur = w_new
        pos[i] = cur

        trig = False
        if cur > 0 and not stopped:
            HH = max(HH, c[i])
            if trail_m is not None and c[i] < HH * (1.0 - trail_m * sig[i] / SQRT12):
                trig = True
            if rr is not None and c[i] >= E + rr * D:
                trig = True
            if trig:
                chg[i + 2] = (0.0, np.nan)             # Ausstieg: Schluss t+1, pos ab t+2 = 0
                stopped = True

        if not trig and flags[i]:
            if st[i] and np.isfinite(sig[i]) and sig[i] > 0:
                w = min(cap, target / sig[i]) if vol_scaled else 1.0
            else:
                w = 0.0
            if not stopped:
                chg[i + 2] = (w, sig[i])
            elif w > 0:                                # Wiedereinstieg am naechsten Monatsende mit LONG
                chg[i + 2] = (w, sig[i])
                stopped = False

    p = pos[s_i:]
    prev = np.concatenate([[0.0], p[:-1]])
    ret = (p * r0[s_i:] + (1.0 - p) * rf_a[s_i:]
           - np.maximum(p - 1.0, 0.0) * fin_markup / TRADING_DAYS
           - np.abs(p - prev) * bps / 1e4)
    return pd.DataFrame({
        "ret": ret,
        "pos": p,
        "state": np.where(st[s_i:], "LONG", "Cash"),
        "sigma": sig[s_i:],
    }, index=idx[s_i:])


def load_market(t: str) -> pd.Series:
    """Schlusskurse eines Marktes ab erstem gueltigen Kurs, bis END, ffill(limit=5) fuer das Signal.

    Gleiche Ladelogik wie market_returns in check_trend_portfolio (inkl. ^GSPC-Langreihe).
    Wirft eine Exception, wenn der Markt nicht geladen werden kann oder zu kurz ist.
    """
    if t == "^GSPC":
        from strategies.trend_ma12_us_equity_cash import _load_gspc_long
        c = _load_gspc_long().to_frame(t)
        panel = Panel(c.copy(), c).truncate(END)
    else:
        panel = load_panel([t], start=LOAD_START).truncate(END)
    raw = panel.close[t].dropna()
    if raw.empty:
        raise ValueError("keine Kurse")
    years_data = (raw.index[-1] - raw.index[0]).days / 365.25
    if years_data < MIN_YEARS:
        raise ValueError(f"nur {years_data:.1f} Jahre Daten")
    n_bad = int((raw <= 0).sum())
    if n_bad:
        print(f"[{t}] WARNUNG: {n_bad} Schlusskurse <= 0 in den Rohdaten")
    return panel.close[t].loc[raw.index[0]:].ffill(limit=5)


def _pct(v: float) -> str:
    return "–" if pd.isna(v) else f"{v * 100:.2f} %"


def _num(v: float, fmt: str = "{:.2f}") -> str:
    return "–" if pd.isna(v) else fmt.format(v)


def _lab(ok: bool) -> str:
    return "ERFÜLLT" if ok else "NICHT erfüllt"


def _row(name: str, section: str, ret: pd.Series, rf: pd.Series, weight: float = np.nan,
         share_gt1: float = np.nan) -> dict:
    d = metrics.summarize(ret, rf)
    g = lambda k: d.get(k, np.nan)
    return {"Serie": name, "Abschnitt": section, "Tage": len(ret),
            "Start": ret.index[0].date().isoformat() if len(ret) else "",
            "Ende": ret.index[-1].date().isoformat() if len(ret) else "",
            "CAGR": g("cagr"), "Vol": g("vol"), "Sharpe": g("sharpe"), "MaxDD": g("max_dd"),
            "Calmar": g("calmar"), "Schlechtestes_Jahr": g("worst_year"),
            "Mittleres_Gewicht": weight, "Anteil_Tage_pos_gt1": share_gt1}


def main() -> None:
    print(f"H11 Trend-Korb mit Volatilitaetsskalierung: {len(MARKETS)} Maerkte (ohne CL=F), Monats-MA12, "
          f"Auswertung bis {END}, {BPS:.0f} bp je Wechsel, Ausfuehrung Schluss Folgetag, Cash = US-RF, ohne Steuer\n")

    names = ["bh"] + list(RUNS)
    RET = {k: {} for k in names}
    POS = {k: {} for k in names}
    skipped = []
    for t in MARKETS:
        try:
            close = load_market(t)
        except Exception as exc:
            print(f"[{t}] keine Daten, uebersprungen: {exc}")
            skipped.append(t)
            continue
        rf = risk_free_daily(close.index)
        try:
            res = {name: sleeve(close, rf, **kw) for name, kw in RUNS.items()}
        except Exception as exc:
            print(f"[{t}] Sleeve nicht berechenbar, uebersprungen: {exc}")
            skipped.append(t)
            continue
        s = res["vt15_cap15"].index[0]
        r_bh = close.pct_change(fill_method=None).loc[s:].fillna(0.0)
        RET["bh"][t] = r_bh
        POS["bh"][t] = pd.Series(1.0, index=r_bh.index)
        for name in RUNS:
            RET[name][t] = res[name]["ret"]
            POS[name][t] = res[name]["pos"]

    n_ok = len(RET["bh"])
    print(f"Maerkte mit Daten: {n_ok} von {len(MARKETS)}; uebersprungen: {skipped or 'keine'}\n")

    baskets = {}
    for name in names:
        baskets[name] = basket(pd.DataFrame(RET[name]), MIN_MARKETS)
    common = None
    for name in names:
        ix = baskets[name][0].index
        common = ix if common is None else common.intersection(ix)
    R = pd.DataFrame({name: baskets[name][0].reindex(common) for name in names})
    rf_c = risk_free_daily(common)
    ncnt = baskets["vt15_cap15"][1].reindex(common)
    print(f"Gemeinsamer Index (alle Koerbe gueltig): {common[0].date()} bis {common[-1].date()}, "
          f"{len(common)} Handelstage; Maerkte je Tag Minimum {int(ncnt.min())}, Maximum {int(ncnt.max())}\n")

    def pos_stats(name: str) -> tuple[float, float]:
        P = pd.DataFrame(POS[name]).reindex(common)
        return float(P.mean(axis=1).mean()), float((P > 1).sum().sum() / P.notna().sum().sum())

    K = {name: metrics.summarize(R[name], rf_c) for name in names}
    rows = []
    for name in names:
        w, g1 = pos_stats(name)
        rows.append(_row(LABELS[name], "Korb gemeinsamer Index", R[name], rf_c, w, g1))
    tab = pd.DataFrame({
        LABELS[name]: {
            "CAGR": _pct(K[name]["cagr"]), "Vol": _pct(K[name]["vol"]), "Sharpe": _num(K[name]["sharpe"]),
            "MaxDD": _pct(K[name]["max_dd"]), "Calmar": _num(K[name]["calmar"]),
            "Schlechtestes Jahr": _pct(K[name]["worst_year"]),
            "Mittleres Gewicht": _num(pos_stats(name)[0]),
            "Anteil Markt-Tage pos > 1": _pct(pos_stats(name)[1]),
        } for name in names
    })
    print("(1) Kennzahlen je Korb:")
    print(tab.to_string())

    halves = {}
    print("\n(2) Zwei Haelften (MaxDD / CAGR):")
    for name in ["bh", "base1x", "vt15_cap15"]:
        for lab, (a, b) in [("1991-2006", FIRST_HALF), ("2007-2022", SECOND_HALF)]:
            seg = R[name].loc[a:b]
            d = metrics.summarize(seg, rf_c.loc[a:b])
            halves[(name, lab)] = d
            rows.append(_row(f"{LABELS[name]} [{lab}]", f"Haelfte {lab}", seg, rf_c.loc[a:b]))
            print(f"  {LABELS[name]:<32} {lab}: MaxDD {_pct(d.get('max_dd', np.nan))}, "
                  f"CAGR {_pct(d.get('cagr', np.nan))}")

    base, bh = K["vt15_cap15"], K["bh"]
    b1 = K["base1x"]
    crit_a = base["cagr"] >= bh["cagr"] - 0.005
    crit_b = base["max_dd"] >= -0.20
    crit_c = base["sharpe"] >= b1["sharpe"] - 0.05
    crit_d = (halves[("vt15_cap15", "1991-2006")].get("max_dd", np.nan) >= -0.25
              and halves[("vt15_cap15", "2007-2022")].get("max_dd", np.nan) >= -0.25)
    total = crit_a and crit_b and crit_c and crit_d
    print("\n(3) Kriterien H11 (Hauptlauf vt15_cap15):")
    print(f"  (a) CAGR {_pct(base['cagr'])} >= CAGR B&H {_pct(bh['cagr'])} - 0,5 Pp: {_lab(crit_a)}")
    print(f"  (b) MaxDD {_pct(base['max_dd'])} >= -20 %: {_lab(crit_b)}")
    print(f"  (c) Sharpe {_num(base['sharpe'], '{:.3f}')} >= Sharpe base1x {_num(b1['sharpe'], '{:.3f}')} - 0,05: {_lab(crit_c)}")
    print(f"  (d) MaxDD beider Haelften >= -25 %: {_lab(crit_d)}")
    print(f"  Gesamt H11: {_lab(total)}")

    print("\n(4) Stop-Kriterium (e) gegen vt15_cap15:")
    stop_ok = {}
    for name in ["trail", "trail_rr"]:
        v = K[name]
        dd_ok = v["max_dd"] - base["max_dd"] >= 0.02
        cg_ok = v["cagr"] >= base["cagr"] - 0.005
        sh_ok = v["sharpe"] >= base["sharpe"]
        stop_ok[name] = dd_ok and cg_ok and sh_ok
        print(f"  {LABELS[name]:<24} MaxDD {_pct(v['max_dd'])} (Diff {(v['max_dd'] - base['max_dd']) * 100:+.2f} Pp, "
              f"{_lab(dd_ok)}); CAGR {_pct(v['cagr'])} (Diff {(v['cagr'] - base['cagr']) * 100:+.2f} Pp, {_lab(cg_ok)}); "
              f"Sharpe {_num(v['sharpe'], '{:.3f}')} (Diff {v['sharpe'] - base['sharpe']:+.3f}, {_lab(sh_ok)}) "
              f"-> gesamt {_lab(stop_ok[name])}")

    print("\n(5) S&P 500 allein (^GSPC-Sleeve, eigenes Fenster ab Sleeve-Start):")
    if "^GSPC" in RET["bh"]:
        for name in ["bh", "base1x", "vt15_cap15", "trail", "trail_rr"]:
            ret_sp = RET[name]["^GSPC"]
            rf_sp = risk_free_daily(ret_sp.index)
            w = float(POS[name]["^GSPC"].mean())
            g1 = float((POS[name]["^GSPC"] > 1).mean())
            rows.append(_row(f"S&P 500: {LABELS[name]}", "S&P 500 allein", ret_sp, rf_sp, w, g1))
            d = metrics.summarize(ret_sp, rf_sp)
            print(f"  {LABELS[name]:<28} {ret_sp.index[0].date()} bis {ret_sp.index[-1].date()}: "
                  f"CAGR {_pct(d['cagr'])}, Vol {_pct(d['vol'])}, Sharpe {_num(d['sharpe'])}, "
                  f"MaxDD {_pct(d['max_dd'])}, Calmar {_num(d['calmar'])}")
    else:
        print("  ^GSPC-Sleeve fehlt, entfaellt")

    print("\n(informativ) Stresslauf G, vt15_cap15 mit 4 % Finanzierungsaufschlag: "
          f"CAGR {_pct(K['stress']['cagr'])}, Sharpe {_num(K['stress']['sharpe'])}, MaxDD {_pct(K['stress']['max_dd'])}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stats = pd.DataFrame(rows)
    stats.to_csv(OUT_STATS, index=False, encoding="utf-8", float_format="%.6f")
    rb = R.copy()
    rb.index.name = "date"
    rb.reset_index().assign(date=lambda d: d["date"].dt.date.astype(str)).to_csv(
        OUT_RET, index=False, encoding="utf-8", float_format="%.10f")
    print(f"\nCSV gespeichert: {OUT_STATS}")
    print(f"CSV gespeichert: {OUT_RET}")


if __name__ == "__main__":
    main()
