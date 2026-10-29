"""P3 (beschreibend): Strategie-Reihen gegen Buy&Hold auf S&P 500 und MSCI World.

Registrierung: docs/HYPOTHESEN.md, Abschnitt P3 (kein Kriterium, keine Auswahl).
Alle Reihen werden ueber ihren NAV auf die gemeinsamen Handelstage gelegt (mehrtaegige Luecken werden
aufgezinst) und nur bis END (2022-12-30) ausgewertet; der Holdout bleibt fuer den Korb zu.
Sharpe: Tagesrendite des risikolosen Zinses wird auf die gemeinsamen Tage gelegt, Luecken werden nicht aufgezinst
(Naeherung, nur fuer die Sharpe-Spalte).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np
import pandas as pd

import check_h12_robust_basket as h12
from qlab.data import load_ticker, risk_free_daily

END = pd.Timestamp("2022-12-30")
MSCI_TICKER = "^990100-USD-STRD"
RES = ROOT / "results"
OUT_STATS = RES / "P3_benchmarks.csv"
OUT_YEARLY = RES / "P3_yearly.csv"

SERIES = [
    ("base1x (A, wie bisher)", "H12_basket_returns.csv", "base1x"),
    ("base1x (B, gefaltet)", "P2_basket_returns.csv", "B_base1x"),
    ("vt15_cap10 (H12)", "H12_basket_returns.csv", "vt15_cap10"),
    ("ens3 (H12)", "H12_basket_returns.csv", "ens3"),
    ("Stufen-Stop (H13)", "H19_basket_returns.csv", "steps"),
    ("Swing-Low-Stop (H19)", "H19_basket_returns.csv", "sr_stop"),
    ("Swing-Low-Trail (H19)", "H19_basket_returns.csv", "sr_trail"),
    ("FVG-Stop (H21)", "H21_basket_returns.csv", "fvg_stop"),
    ("FVG-Trail (H21)", "H21_basket_returns.csv", "fvg_trail"),
    ("4 Tranchen (H20)", "H20_basket_returns.csv", "tranche4"),
    ("Buy&Hold-Korb 17 (A)", "H12_basket_returns.csv", "bh"),
]
BENCH = ["S&P 500 (B&H)", "MSCI World (B&H)"]
HALVES = [("1991-2006", "1991-01-01", "2006-12-31"), ("2007-2022", "2007-01-01", "2022-12-31")]


def read_returns(file: str, col: str) -> pd.Series:
    """Tagesrenditen einer Spalte aus einer Ergebnisdatei (Index = Datum), nur bis END."""
    df = pd.read_csv(RES / file, index_col="date", parse_dates=True)
    return clip_end(df[col].dropna())


def clip_end(s: pd.Series) -> pd.Series:
    """Schneidet alles nach END ab (Holdout bleibt zu)."""
    return s.loc[:END]


def returns_on(level: pd.Series, common: pd.DatetimeIndex) -> pd.Series:
    """Renditen einer Niveau-Reihe (NAV oder Kurs) auf den gemeinsamen Tagen; Luecken werden aufgezinst."""
    s = level.reindex(common)
    if s.isna().any():
        raise ValueError("Niveau-Reihe hat auf gemeinsamen Tagen Luecken")
    return s.pct_change().dropna()


def nav(ret: pd.Series) -> pd.Series:
    return (1.0 + ret).cumprod()


def calendar_returns(ret: pd.Series) -> pd.Series:
    """Kalenderjahresrenditen (verkettet); das erste Jahr kann Teiljahr sein."""
    return (1.0 + ret).groupby(ret.index.year).prod() - 1.0


def full_year_returns(ret: pd.Series) -> pd.Series:
    """Nur vollstaendige Kalenderjahre: erstes Jahr (Teiljahr) und ein vor dem 20.12. endendes Schlussjahr entfallen."""
    cal = calendar_returns(ret)
    if len(cal) == 0:
        return cal
    first_year, last_year = ret.index[0].year, ret.index[-1].year
    drop = []
    if ret.index[0] > pd.Timestamp(year=first_year, month=1, day=10):
        drop.append(first_year)
    if ret.index[-1] < pd.Timestamp(year=last_year, month=12, day=20):
        drop.append(last_year)
    return cal.drop(index=[y for y in drop if y in cal.index])


def years_ahead(strat: pd.Series, bench: pd.Series) -> tuple[int, int]:
    """(Jahre, in denen die Strategie vor dem Benchmark liegt, Zahl der gemeinsamen Jahre)."""
    j = strat.index.intersection(bench.index)
    return int((strat.loc[j] > bench.loc[j]).sum()), int(len(j))


def stats(ret: pd.Series, rf: pd.Series) -> dict:
    """h12.konstanz plus Endwert von 100 und Zahl der Jahre im Minus (vollstaendige Jahre)."""
    k = h12.konstanz(ret, rf.reindex(ret.index).fillna(0.0))
    fy = full_year_returns(ret)
    k["end100"] = float(100.0 * (1.0 + ret).prod())
    k["years_neg"] = int((fy < 0).sum())
    k["years_n"] = int(len(fy))
    return k


def load_benchmarks() -> dict[str, pd.Series]:
    from strategies.trend_ma12_us_equity_cash import _load_gspc_long
    spx = clip_end(_load_gspc_long().astype(float).dropna())
    msci = clip_end(load_ticker(MSCI_TICKER, start="1969-01-01")["Close"].astype(float).dropna())
    return {BENCH[0]: spx, BENCH[1]: msci}


def _p(v: float) -> str:
    return f"{v * 100:.2f} %"


def main() -> None:
    strat = {name: read_returns(f, c) for name, f, c in SERIES}
    levels = {name: nav(r) for name, r in strat.items()}
    bench = load_benchmarks()
    for k, v in bench.items():
        levels[k] = v
        print(f"{k}: {v.index[0].date()} bis {v.index[-1].date()}, {len(v)} Tage")
    common = None
    for lv in levels.values():
        common = lv.index if common is None else common.intersection(lv.index)
    print(f"\nGemeinsamer Zeitraum: {common[0].date()} bis {common[-1].date()}, {len(common)} Handelstage\n")
    R = {name: returns_on(lv, common) for name, lv in levels.items()}
    rf = risk_free_daily(common)

    ST = {name: stats(r, rf) for name, r in R.items()}
    FY = {name: full_year_returns(r) for name, r in R.items()}
    order = [n for n, _, _ in SERIES] + BENCH
    rows = []
    for name in order:
        k = ST[name]
        row = {"Serie": name, "CAGR": k["cagr"], "MaxDD": k["max_dd"], "UPI": k["upi"], "Sharpe": k["sharpe"],
               "Endwert_100": k["end100"], "Jahre_im_Minus": f"{k['years_neg']} von {k['years_n']}",
               "schlechtestes_Jahr": k["worst_year"]}
        for b in BENCH:
            row[f"dCAGR_vs_{b.split()[0]}"] = k["cagr"] - ST[b]["cagr"]
            row[f"dMaxDD_vs_{b.split()[0]}"] = k["max_dd"] - ST[b]["max_dd"]
            a, n = years_ahead(FY[name], FY[b])
            row[f"Jahre_vorn_vs_{b.split()[0]}"] = f"{a} von {n}"
        rows.append(row)
    T = pd.DataFrame(rows)
    show = T.copy()
    for c in ("CAGR", "MaxDD", "schlechtestes_Jahr") + tuple(c for c in T.columns if c.startswith("dCAGR") or c.startswith("dMaxDD")):
        show[c] = (show[c] * 100).map("{:+.2f}".format) if c.startswith("d") else (show[c] * 100).map("{:.2f} %".format)
    for c in ("UPI", "Sharpe"):
        show[c] = show[c].map("{:.3f}".format)
    show["Endwert_100"] = show["Endwert_100"].map("{:.0f}".format)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    print("(1) Ganzer gemeinsamer Zeitraum (d... = Strategie minus Benchmark in Prozentpunkten; MaxDD-Differenz positiv = kleinerer Verlust):")
    print(show.to_string(index=False))

    print("\n(2) Hälften (CAGR / MaxDD / UPI):")
    sel = ["base1x (A, wie bisher)", "base1x (B, gefaltet)", "Buy&Hold-Korb 17 (A)"] + BENCH
    for lab, a, b in HALVES:
        print(f"  {lab}:")
        for name in sel:
            r = R[name].loc[a:b]
            k = stats(r, rf)
            print(f"    {name:<24} {_p(k['cagr']):>9}  {_p(k['max_dd']):>9}  UPI {k['upi']:.2f}")

    print("\n(3) Kalenderjahre (vollständig), Rendite in %: base1x A / base1x B / S&P 500 / MSCI World")
    yearly = pd.DataFrame({n: FY[n] for n in ["base1x (A, wie bisher)", "base1x (B, gefaltet)"] + BENCH}) * 100
    print(yearly.round(1).to_string())
    OUT_STATS.parent.mkdir(exist_ok=True)
    T.to_csv(OUT_STATS, index=False)
    (pd.DataFrame({n: FY[n] for n in order}) * 100).round(3).to_csv(OUT_YEARLY, index_label="jahr")
    print(f"\nCSV gespeichert: {OUT_STATS} und {OUT_YEARLY}")


if __name__ == "__main__":
    main()
