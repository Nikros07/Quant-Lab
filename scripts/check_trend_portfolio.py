"""H6: Gleichgewichteter Korb der H5-Monats-MA12-Sleeves gegen gleichgewichteten Buy&Hold-Korb (docs/HYPOTHESEN.md, Eintrag H6).

Märkte: h5.MARKETS ohne CL=F (a priori ausgeschlossen, Yahoo-Schlusskurs −37,63 am 2020-04-20). Je Markt
die H5-Konstruktion unverändert: Monats-MA12-Zustand, Signal Schlusskurs (ffill limit=5), Ausführung
Schluss Folgetag, 10 bp je Wechsel, Cash = US-RF, Buy&Hold ab erstem gültigen Kurs. Beide Sleeves starten
je Markt am selben Tag (erster gültiger Zustand, wie in H5). Ausgewertet wird nur bis 2022-12-31 (Holdout zu).

Korb-Tagesrendite = einfacher Mittelwert der an dem Tag gültigen Sleeve-Renditen (gleiche Gewichte, täglich
neu gewichtet). Korbstart = erster Tag mit mindestens 8 gültigen Märkten.
Kriterium (a): Sharpe(Strategie-Korb) − Sharpe(B&H-Korb) >= 0,10 UND Bootstrap-p <= 0,10.
Kriterium (b): MaxDD des Strategie-Korbs > MaxDD des B&H-Korbs (beide negativ).
S&P-500-Sleeve (Strategie) allein im selben Zeitraum: informativ, kein Kriterium.
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

import pandas as pd

import check_trend_multi_market as h5
from qlab import metrics
from qlab.data import Panel, load_panel, risk_free_daily
from qlab.engine import CostModel, run_backtest
from qlab.stats import bootstrap_sharpe_diff

END = h5.END
LOAD_START = h5.LOAD_START
BPS = h5.BPS
EXCLUDE = {"CL=F"}
MARKETS = [t for t in h5.MARKETS if t not in EXCLUDE]
MIN_MARKETS = 8
N_BOOT = 2000
SHARPE_MIN_DIFF = 0.10
P_MAX = 0.10
OUT_DIR = ROOT / "results"
OUT_STATS = OUT_DIR / "H6_portfolio.csv"
OUT_BASKET = OUT_DIR / "H6_basket_returns.csv"


def market_returns(t: str) -> tuple[pd.Series, pd.Series]:
    """Tagesrenditen (Strategie, Buy&Hold) eines Marktes ab erstem gültigen Zustand (wie run_market in H5).

    Wirft eine Exception, wenn der Markt nicht geladen werden kann oder zu kurz ist.
    """
    if t == "^GSPC":
        # Lange Reihe ab 1927-12-30 (nur Schluss), wie in check_trend_multi_market.run_market.
        from strategies.trend_ma12_us_equity_cash import _load_gspc_long
        c = _load_gspc_long().to_frame(t)
        panel = Panel(c.copy(), c).truncate(END)
    else:
        panel = load_panel([t], start=LOAD_START).truncate(END)
    raw = panel.close[t].dropna()
    if raw.empty:
        raise ValueError("keine Kurse")
    years_data = (raw.index[-1] - raw.index[0]).days / 365.25
    if years_data < h5.MIN_YEARS:
        raise ValueError(f"nur {years_data:.1f} Jahre Daten")
    n_bad = int((raw <= 0).sum())
    if n_bad:
        print(f"[{t}] WARNUNG: {n_bad} Schlusskurse <= 0 in den Rohdaten")

    close = panel.close[t].ffill(limit=5)
    st = h5.monthly_state(close)
    first = st.index.min()
    rf = risk_free_daily(panel.close.index)
    cost = CostModel(per_ticker_bps={t: BPS})

    w = pd.DataFrame({t: st.astype(float)})
    w = w[w[t].diff().fillna(1.0) != 0]
    res = run_backtest(panel, w, cost=cost, exec_mode="close_next", rf=rf)
    bh_w = pd.DataFrame({t: [1.0]}, index=[raw.index[0]])
    bh = run_backtest(panel, bh_w, cost=cost, exec_mode="close_next", rf=rf)

    return res.ret.loc[first:], bh.ret.loc[first:]


def basket(returns: pd.DataFrame, min_markets: int = 8, drop_thin_days: bool = True) -> tuple[pd.Series, pd.Series]:
    """Gleichgewichteter Korb: Tagesrendite = Mittel der an dem Tag gültigen Sleeves.

    Gibt (Korbrendite, Anzahl gültiger Märkte) ab dem Korbstart zurück (erster Tag mit >= min_markets gültigen).
    Vor dem Korbstart gibt es keine Werte.
    """
    n = returns.notna().sum(axis=1)
    ret = returns.mean(axis=1, skipna=True)
    ok = n >= min_markets
    if not ok.any():
        raise ValueError(f"an keinem Tag {min_markets} gültige Märkte")
    start = ok.idxmax()
    ret, n = ret.loc[start:], n.loc[start:]
    if drop_thin_days:   # H6-Korrektur: Wochenenden/Feiertage mit < min_markets Märkten (sonst nur BTC) verwerfen
        keep = n >= min_markets
        ret, n = ret[keep], n[keep]
    return ret, n


def _pct(v: float) -> str:
    return "–" if pd.isna(v) else f"{v * 100:.2f} %"


def _num(v: float, fmt: str = "{:.2f}") -> str:
    return "–" if pd.isna(v) else fmt.format(v)


def main() -> None:
    print(f"H6 Portfolio: gleichgewichteter Korb aus {len(MARKETS)} Märkten (ohne CL=F), Monats-MA12, "
          f"Auswertung bis {END}, {BPS:.0f} bp je Wechsel, Ausführung Schluss Folgetag, ohne Steuer, "
          "Cash = US-FF-RF\n")

    strat, bh, skipped = {}, {}, []
    for t in MARKETS:
        try:
            strat[t], bh[t] = market_returns(t)
        except Exception as exc:  # Laden fehlgeschlagen oder zu kurz: Markt fehlt im Korb
            print(f"[{t}] keine Daten, übersprungen: {exc}")
            skipped.append(t)
    print(f"\nMärkte im Korb: {len(strat)} von {len(MARKETS)}; übersprungen: {skipped or 'keine'}")

    S = pd.DataFrame(strat)
    B = pd.DataFrame(bh)
    rs, ns = basket(S, MIN_MARKETS)
    rb, nb = basket(B, MIN_MARKETS)
    rb = rb.reindex(rs.index)
    ns = ns.reindex(rs.index)
    start = rs.index[0]
    rf = risk_free_daily(rs.index)

    sp = strat["^GSPC"].loc[start:] if "^GSPC" in strat else None
    if sp is None:
        print("WARNUNG: ^GSPC-Sleeve fehlt, S&P-Vergleich entfällt")

    ks = metrics.summarize(rs, rf)
    kb = metrics.summarize(rb, rf)
    ksp = metrics.summarize(sp, rf) if sp is not None else {}
    boot = bootstrap_sharpe_diff(rs, rb, rf=rf, n_boot=N_BOOT)

    print(f"Korbstart (erster Tag mit >= {MIN_MARKETS} Märkten): {start.date().isoformat()}")
    print(f"Anzahl gültiger Märkte ab Korbstart: Minimum {int(ns.min())}, Maximum {int(ns.max())}, "
          f"am Ende {int(ns.iloc[-1])}")
    print(f"Handelstage: {len(rs)} ({rs.index[0].date()} bis {rs.index[-1].date()})\n")

    rows = {"Strategie-Korb": ks, "B&H-Korb": kb}
    if sp is not None:
        rows["S&P500-Sleeve (Strategie)"] = ksp
    table = pd.DataFrame({
        name: {
            "CAGR": _pct(d["cagr"]), "Vol": _pct(d["vol"]), "Sharpe": _num(d["sharpe"]),
            "MaxDD": _pct(d["max_dd"]), "Calmar": _num(d["calmar"]),
            "Schlechtestes Jahr": _pct(d["worst_year"]),
        } for name, d in rows.items()
    })
    print(table.to_string())

    sharpe_diff = ks["sharpe"] - kb["sharpe"]
    print(f"\nSharpe-Differenz Strategie − B&H (Kennzahlen): {sharpe_diff:+.3f}")
    print(f"Bootstrap (stationär, {N_BOOT} Ziehungen): Differenz {boot['sharpe_diff']:+.3f}, "
          f"90-%-CI [{boot['ci90'][0]:+.3f}, {boot['ci90'][1]:+.3f}], p (einseitig) = {boot['p_value']:.3f}")

    years = pd.DataFrame({
        "Strategie-Korb": (1 + rs).groupby(rs.index.year).prod() - 1,
        "B&H-Korb": (1 + rb).groupby(rb.index.year).prod() - 1,
    })
    if sp is not None:
        years["S&P500-Sleeve"] = (1 + sp).groupby(sp.index.year).prod() - 1
    years.index.name = "Jahr"
    yshow = years.map(lambda v: "–" if pd.isna(v) else f"{v * 100:.1f} %")
    print("\nJahrestabelle (erstes und letztes Jahr unvollständig):")
    print(yshow.to_string())

    crit_a = sharpe_diff >= SHARPE_MIN_DIFF and boot["p_value"] <= P_MAX
    crit_b = ks["max_dd"] > kb["max_dd"]
    total = crit_a and crit_b
    lab = lambda ok: "ERFÜLLT" if ok else "NICHT erfüllt"
    print(f"\nKriterium H6 (a) Sharpe-Diff >= {SHARPE_MIN_DIFF:.2f} und p <= {P_MAX:.2f}: {lab(crit_a)} "
          f"(Diff {sharpe_diff:+.3f}, p {boot['p_value']:.3f})")
    print(f"Kriterium H6 (b) MaxDD Strategie > MaxDD B&H: {lab(crit_b)} "
          f"({_pct(ks['max_dd'])} gegen {_pct(kb['max_dd'])})")
    print(f"Gesamt H6: {lab(total)}")

    stats = pd.DataFrame.from_dict(
        {name: {"Jahre": d["years"], "CAGR": d["cagr"], "Vol": d["vol"], "Sharpe": d["sharpe"],
                "MaxDD": d["max_dd"], "Calmar": d["calmar"], "Schlechtestes_Jahr": d["worst_year"]}
         for name, d in rows.items()}, orient="index")
    stats.index.name = "Serie"
    stats["Sharpe_Diff_zu_BH"] = float("nan")
    stats["Boot_ci90_lo"] = float("nan")
    stats["Boot_ci90_hi"] = float("nan")
    stats["Boot_p"] = float("nan")
    stats.loc["Strategie-Korb", ["Sharpe_Diff_zu_BH", "Boot_ci90_lo", "Boot_ci90_hi", "Boot_p"]] = [
        sharpe_diff, boot["ci90"][0], boot["ci90"][1], boot["p_value"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stats.to_csv(OUT_STATS, encoding="utf-8", float_format="%.6f")
    basket_df = pd.DataFrame({"strat_basket": rs, "bh_basket": rb, "n_markets": ns})
    basket_df.index.name = "date"
    basket_df.reset_index().assign(date=lambda d: d["date"].dt.date.astype(str)).to_csv(
        OUT_BASKET, index=False, encoding="utf-8", float_format="%.10f")
    print(f"\nCSV gespeichert: {OUT_STATS}")
    print(f"CSV gespeichert: {OUT_BASKET}")


if __name__ == "__main__":
    main()
