"""P2 (Messfehler-Check nach V5): Korb mit eingefalteten Tagen und ohne Bitcoin.

Registrierung: docs/HYPOTHESEN.md, Abschnitt "Pruefblock P2". Messvarianten, keine Auswahl:
  A  wie bisher (tp.basket verwirft Tage mit < MIN_MARKETS Maerkten)
  B  gefaltet: verworfene Tage werden je Markt aufgezinst und zum naechsten behaltenen Tag gerechnet
  C  ohne BTC-USD, Verwerfen wie A
  D  ohne BTC-USD und gefaltet
Je Variante base1x und Buy&Hold-Korb; Markt-Sleeves und Kosten wie H12 (sleeve2, lengths=(12,), target=None).
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
import check_trend_portfolio as tp
import check_trend_vt_basket as vt
from qlab.data import risk_free_daily

OUT_DIR = ROOT / "results"
OUT_STATS = OUT_DIR / "P2_btc.csv"
OUT_RET = OUT_DIR / "P2_basket_returns.csv"
BTC = "BTC-USD"
H12_REF = {"cagr": 0.073013, "max_dd": -0.147462}


def fold_groups(returns: pd.DataFrame, min_markets: int) -> tuple[pd.DataFrame, pd.Series]:
    """Schneidet ab dem Korbstart und ordnet jedem Tag eine Gruppe zu.

    Verworfene Tage (weniger als min_markets gueltige Maerkte) gehoeren zum NAECHSTEN behaltenen Tag.
    Verworfene Tage nach dem letzten behaltenen Tag erhalten die Gruppe 0 und fallen spaeter weg.
    """
    n = returns.notna().sum(axis=1)
    ok = n >= min_markets
    if not ok.any():
        raise ValueError(f"an keinem Tag {min_markets} gueltige Maerkte")
    start = ok.idxmax()
    r = returns.loc[start:]
    keep = n.loc[start:] >= min_markets
    gid = keep.iloc[::-1].cumsum().iloc[::-1]
    return r, gid


def fold_apply(df: pd.DataFrame, gid: pd.Series) -> pd.DataFrame:
    """Zinst je Spalte die Renditen jeder Gruppe auf; Gruppe ohne Beobachtung bleibt NaN."""
    g = gid.values
    growth = (1.0 + df.fillna(0.0)).groupby(g).prod() - 1.0
    cnt = df.notna().groupby(g).sum()
    growth = growth.where(cnt > 0)
    last_date = pd.Series(df.index, index=df.index).groupby(g).last()
    growth.index = pd.DatetimeIndex(last_date.reindex(growth.index).values)
    return growth.sort_index()


def fold_thin_days(returns: pd.DataFrame, min_markets: int = 8) -> pd.DataFrame:
    """Gefalteter Renditeblock: je Markt ueber verworfene Tage aufgezinst, nur behaltene Tage im Index."""
    r, gid = fold_groups(returns, min_markets)
    keep_groups = gid != 0
    return fold_apply(r.loc[keep_groups], gid.loc[keep_groups])


def basket_folded(returns: pd.DataFrame, min_markets: int = 8) -> tuple[pd.Series, pd.Series]:
    """Gleichgewichteter Korb auf dem gefalteten Block: (Korbrendite, Zahl gueltiger Maerkte)."""
    f = fold_thin_days(returns, min_markets)
    return f.mean(axis=1, skipna=True), f.notna().sum(axis=1)


def folded_rf(index: pd.DatetimeIndex, returns: pd.DataFrame, min_markets: int = 8) -> pd.Series:
    """Cash-Rendite (Tagesrendite) ueber dieselben Gruppen aufgezinst wie der Renditeblock."""
    r, gid = fold_groups(returns, min_markets)
    keep_groups = gid != 0
    rf = risk_free_daily(r.index).to_frame("rf")
    return fold_apply(rf.loc[keep_groups], gid.loc[keep_groups])["rf"]


def variant_series(strat: pd.DataFrame, bh: pd.DataFrame, min_markets: int) -> dict:
    """A bis D: je (Strategie-Korbrendite, B&H-Korbrendite, rf) auf dem eigenen Index."""
    out = {}
    s_a, _ = tp.basket(strat, min_markets)
    b_a, _ = tp.basket(bh, min_markets)
    out["A mit BTC, verwerfen"] = (s_a, b_a, risk_free_daily(s_a.index))
    s_b, _ = basket_folded(strat, min_markets)
    b_b, _ = basket_folded(bh, min_markets)
    out["B mit BTC, gefaltet"] = (s_b, b_b, folded_rf(strat.index, strat, min_markets))
    strat_c = strat.drop(columns=[BTC], errors="ignore")
    bh_c = bh.drop(columns=[BTC], errors="ignore")
    s_c, _ = tp.basket(strat_c, min_markets)
    b_c, _ = tp.basket(bh_c, min_markets)
    out["C ohne BTC, verwerfen"] = (s_c, b_c, risk_free_daily(s_c.index))
    s_d, _ = basket_folded(strat_c, min_markets)
    b_d, _ = basket_folded(bh_c, min_markets)
    out["D ohne BTC, gefaltet"] = (s_d, b_d, folded_rf(strat_c.index, strat_c, min_markets))
    return out


def main() -> None:
    print(f"P2 Messcheck: {len(vt.MARKETS)} Maerkte, ohne Hebel, Auswertung bis {vt.END}, {vt.BPS:.0f} bp je Wechsel\n")
    strat, bh, skipped = {}, {}, []
    for t in vt.MARKETS:
        try:
            close = vt.load_market(t)
            rf = risk_free_daily(close.index)
            res = h12.sleeve2(close, rf, **h12.RUNS["base1x"])
        except Exception as exc:
            print(f"[{t}] uebersprungen: {exc}")
            skipped.append(t)
            continue
        s = res["ret"].index[0]
        bh[t] = close.pct_change(fill_method=None).loc[s:].fillna(0.0)
        strat[t] = res["ret"]
    print(f"Maerkte mit Daten: {len(strat)} von {len(vt.MARKETS)}; uebersprungen: {skipped or 'keine'}\n")
    S, B = pd.DataFrame(strat), pd.DataFrame(bh)
    V = variant_series(S, B, vt.MIN_MARKETS)

    rows = []
    for name, (sr, br, rfv) in V.items():
        for label, ser in (("base1x", sr), ("Buy&Hold-Korb", br)):
            k = h12.konstanz(ser, rfv.reindex(ser.dropna().index).fillna(0.0))
            rows.append({"Variante": name, "Serie": label, "Tage": int(ser.dropna().shape[0]),
                         "von": str(ser.index[0].date()), "bis": str(ser.index[-1].date()), **k})
    T = pd.DataFrame(rows)
    show = T[["Variante", "Serie", "Tage", "cagr", "vol", "sharpe", "max_dd", "ulcer", "upi"]].copy()
    for c in ("cagr", "vol", "ulcer", "max_dd"):
        show[c] = (show[c] * 100).map("{:.2f} %".format)
    for c in ("sharpe", "upi"):
        show[c] = show[c].map("{:.3f}".format)
    print(show.to_string(index=False))

    a = T[(T.Variante.str.startswith("A")) & (T.Serie == "base1x")].iloc[0]
    print(f"\nPruefung A gegen H12 base1x: CAGR {a.cagr:.6f} (Soll {H12_REF['cagr']:.6f}), MaxDD {a.max_dd:.6f} "
          f"(Soll {H12_REF['max_dd']:.6f}) -> "
          f"{'reproduziert' if abs(a.cagr - H12_REF['cagr']) < 5e-6 and abs(a.max_dd - H12_REF['max_dd']) < 5e-6 else 'ABWEICHUNG'}")

    def g(v, s, c):
        return float(T[(T.Variante.str.startswith(v)) & (T.Serie == s)].iloc[0][c])

    d_mdd = (g("B", "base1x", "max_dd") - g("A", "base1x", "max_dd")) * 100
    d_cagr_c = (g("C", "base1x", "cagr") - g("A", "base1x", "cagr")) * 100
    print("\nBerichts-Kriterien P2:")
    print(f"  (1) MaxDD B minus A = {d_mdd:+.2f} Pp -> {'Kopfzahlen umstellen' if abs(d_mdd) > 0.75 else 'keine Umstellung'}")
    print(f"  (2) CAGR C minus A = {d_cagr_c:+.2f} Pp -> {'Spanne mit/ohne BTC nennen' if d_cagr_c < -0.5 else 'keine Spanne noetig'}")
    for v in "BCD":
        better = g(v, "base1x", "max_dd") > g(v, "Buy&Hold-Korb", "max_dd")
        print(f"  (3) Variante {v}: MaxDD base1x {g(v, 'base1x', 'max_dd') * 100:.2f} % gegen B&H "
              f"{g(v, 'Buy&Hold-Korb', 'max_dd') * 100:.2f} % -> {'Vorteil bleibt' if better else 'Vorteil weg'}")
    OUT_DIR.mkdir(exist_ok=True)
    T.to_csv(OUT_STATS, index=False)
    cols = {}
    for name, (sr, br, _) in V.items():
        cols[f"{name[0]}_base1x"] = sr
        cols[f"{name[0]}_bh"] = br
    pd.DataFrame(cols).to_csv(OUT_RET, index_label="date")
    print(f"\nCSV gespeichert: {OUT_STATS} und {OUT_RET}")


if __name__ == "__main__":
    main()
