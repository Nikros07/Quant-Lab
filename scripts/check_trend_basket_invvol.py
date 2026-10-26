"""H10: Inverse-Volatilitäts-Korb gegen gleichgewichteten Korb (docs/HYPOTHESEN.md, Eintrag H7–H10, Abschnitt H10).

Märkte und Sleeves wie H6 (check_trend_portfolio): 17 Märkte ohne CL=F, je Markt Monats-MA12-Strategie-Sleeve
und Buy&Hold-Sleeve, Auswertung bis 2022-12-31, 10 bp je Wechsel, Ausführung Schluss Folgetag, Cash = US-RF.

Gewichtung: w_i,t proportional zu 1/σ_i,t, σ_i,t = Standardabweichung der täglichen Buy&Hold-Renditen des Markts i
über die letzten 60 Handelstage bis einschließlich Vortag (shift(1), kausal). Gewichte je Tag auf Summe 1
normiert über die an dem Tag gültigen Märkte (Sleeve vorhanden und σ > 0 mit >= 60 Beobachtungen).
Tage mit weniger als 8 gültigen Märkten werden verworfen (wie H6).

Vergleich: iv_filter (inverse Vol, Strategie-Sleeves) gegen ew_filter (H6-Korb, Strategie-Sleeves).
Informativ: iv_bh gegen ew_bh (dieselbe Gewichtung auf Buy&Hold-Sleeves).

Kriterium H10: (a) Sharpe-Diff iv_filter − ew_filter >= 0,10 UND Bootstrap-p (einseitig) <= 0,10;
(b) MaxDD iv_filter nicht um mehr als 2 Prozentpunkte schlechter als MaxDD ew_filter.
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

import check_trend_portfolio as h6
from qlab import metrics
from qlab.data import risk_free_daily
from qlab.stats import bootstrap_sharpe_diff

MARKETS = h6.MARKETS
MIN_MARKETS = h6.MIN_MARKETS          # 8, wie H6
WINDOW = 60                           # Volatilitätsfenster laut H10
N_BOOT = h6.N_BOOT                    # 2000, wie H6
SHARPE_MIN_DIFF = h6.SHARPE_MIN_DIFF  # 0,10
P_MAX = h6.P_MAX                      # 0,10
MAXDD_TOL = 0.02                      # 2 Prozentpunkte
OUT_DIR = ROOT / "results"
OUT_STATS = OUT_DIR / "H10_invvol_basket.csv"
OUT_BASKET = OUT_DIR / "H10_basket_returns.csv"


def weighted_basket(sleeve: pd.DataFrame, bh: pd.DataFrame, window: int = 60,
                    min_markets: int = 8) -> tuple[pd.Series, pd.Series, pd.DataFrame]:
    """Inverse-Volatilitäts-Korb.

    sleeve: Tagesrenditen je Markt (Spalten = Märkte), die gewichtet werden.
    bh: Buy&Hold-Tagesrenditen je Markt, nur daraus wird die Volatilität geschätzt (bis zum vorherigen
    Handelstag des Markts, kausal, window Beobachtungen).
    Gibt (Korbrendite, Anzahl gültiger Märkte, Gewichte) zurück; Gewichte als DataFrame, je Tag Summe 1.
    """
    # Je Markt auf eigenen Handelstagen (dropna): die Sleeves liegen auf einem Vereinigungskalender
    # (BTC handelt am Wochenende, Aktien nicht), ein Fenster über Zeilen würde sonst zu kurz.
    vol = pd.DataFrame({
        c: bh[c].dropna().rolling(window, min_periods=window).std(ddof=1).shift(1).reindex(sleeve.index)
        for c in sleeve.columns
    }, index=sleeve.index, columns=sleeve.columns)
    valid = sleeve.notna() & vol.notna() & (vol > 0)
    inv = (1.0 / vol).where(valid, 0.0)
    total = inv.sum(axis=1)
    n = valid.sum(axis=1)
    keep = (n >= min_markets) & (total > 0)
    w = inv.loc[keep].div(total[keep], axis=0)
    ret = (w * sleeve.loc[keep].fillna(0.0)).sum(axis=1)
    return ret, n[keep].astype(int), w


def _pct(v: float) -> str:
    return "–" if pd.isna(v) else f"{v * 100:.2f} %"


def _num(v: float, fmt: str = "{:.2f}") -> str:
    return "–" if pd.isna(v) else fmt.format(v)


def main() -> None:
    print(f"H10 inverse Volatilität: Korb aus {len(MARKETS)} Märkten (ohne CL=F), σ über {WINDOW} Handelstage "
          f"bis Vortag, mindestens {MIN_MARKETS} Märkte, Auswertung bis {h6.END}, {h6.BPS:.0f} bp je Wechsel, "
          "Ausführung Schluss Folgetag, ohne Steuer, Cash = US-FF-RF\n")

    strat, bh, skipped = {}, {}, []
    for t in MARKETS:
        try:
            strat[t], bh[t] = h6.market_returns(t)
        except Exception as exc:  # Laden fehlgeschlagen oder zu kurz: Markt fehlt im Korb
            print(f"[{t}] keine Daten, übersprungen: {exc}")
            skipped.append(t)
    print(f"\nMärkte im Korb: {len(strat)} von {len(MARKETS)}; übersprungen: {skipped or 'keine'}")

    S = pd.DataFrame(strat)
    B = pd.DataFrame(bh)

    iv_f, n_iv, w_iv = weighted_basket(S, B, WINDOW, MIN_MARKETS)
    iv_b, _, _ = weighted_basket(B, B, WINDOW, MIN_MARKETS)
    ew_f, _ = h6.basket(S, MIN_MARKETS)
    ew_b, _ = h6.basket(B, MIN_MARKETS)

    common = iv_f.index.intersection(iv_b.index).intersection(ew_f.index).intersection(ew_b.index)
    print(f"\nTage inverse-Vol-Filter gültig: {len(iv_f)}; gemeinsamer Index aller vier Körbe: {len(common)} "
          f"({'identisch' if len(common) == len(iv_f) else 'Abweichung: ' + str(len(iv_f) - len(common)) + ' Tage entfallen'})")
    iv_f, iv_b, ew_f, ew_b = iv_f.loc[common], iv_b.loc[common], ew_f.loc[common], ew_b.loc[common]
    n_iv = n_iv.loc[common]
    if len(common) == 0:
        print("Keine gemeinsamen Handelstage, keine Auswertung möglich.")
        return
    print(f"Korbstart (gemeinsam): {common[0].date().isoformat()}")
    print(f"Anzahl gültiger Märkte (inverse Vol) ab Korbstart: Minimum {int(n_iv.min())}, "
          f"Maximum {int(n_iv.max())}, am Ende {int(n_iv.iloc[-1])}")
    print(f"Handelstage: {len(common)} ({common[0].date()} bis {common[-1].date()})")
    wmax = w_iv.loc[common].max(axis=1).mean()
    print(f"Mittleres größtes Einzelgewicht (inverse Vol): {wmax * 100:.1f} % "
          f"(Gleichgewicht wäre {100 / max(int(n_iv.mean()), 1):.1f} % bei {n_iv.mean():.1f} Märkten)\n")

    rf = risk_free_daily(common)

    k_ivf = metrics.summarize(iv_f, rf)
    k_ewf = metrics.summarize(ew_f, rf)
    k_ivb = metrics.summarize(iv_b, rf)
    k_ewb = metrics.summarize(ew_b, rf)
    rows = {"IV-Filter (H10)": k_ivf, "EW-Filter (H6)": k_ewf, "IV-B&H": k_ivb, "EW-B&H": k_ewb}
    table = pd.DataFrame({
        name: {
            "CAGR": _pct(d["cagr"]), "Vol": _pct(d["vol"]), "Sharpe": _num(d["sharpe"]),
            "MaxDD": _pct(d["max_dd"]), "Calmar": _num(d["calmar"]),
            "Schlechtestes Jahr": _pct(d["worst_year"]),
        } for name, d in rows.items()
    })
    print(table.to_string())

    boot = bootstrap_sharpe_diff(iv_f, ew_f, rf=rf, n_boot=N_BOOT)
    boot_bh = bootstrap_sharpe_diff(iv_b, ew_b, rf=rf, n_boot=N_BOOT)

    sharpe_diff = k_ivf["sharpe"] - k_ewf["sharpe"]
    sharpe_diff_bh = k_ivb["sharpe"] - k_ewb["sharpe"]
    print(f"\nSharpe-Differenz IV − EW (Filter, Kennzahlen): {sharpe_diff:+.3f}")
    print(f"Bootstrap Filter (stationär, {N_BOOT} Ziehungen): Differenz {boot['sharpe_diff']:+.3f}, "
          f"90-%-CI [{boot['ci90'][0]:+.3f}, {boot['ci90'][1]:+.3f}], p (einseitig) = {boot['p_value']:.3f}")
    print(f"Informativ B&H: Sharpe-Differenz IV − EW {sharpe_diff_bh:+.3f}, Bootstrap-Differenz "
          f"{boot_bh['sharpe_diff']:+.3f}, p (einseitig) = {boot_bh['p_value']:.3f}")

    years = pd.DataFrame({name: (1 + s).groupby(s.index.year).prod() - 1
                          for name, s in [("IV-Filter", iv_f), ("EW-Filter", ew_f),
                                          ("IV-B&H", iv_b), ("EW-B&H", ew_b)]})
    years.index.name = "Jahr"
    yshow = years.map(lambda v: "–" if pd.isna(v) else f"{v * 100:.1f} %")
    print("\nJahrestabelle (erstes und letztes Jahr unvollständig):")
    print(yshow.to_string())

    crit_a = sharpe_diff >= SHARPE_MIN_DIFF and boot["p_value"] <= P_MAX
    crit_b = k_ivf["max_dd"] >= k_ewf["max_dd"] - MAXDD_TOL
    total = crit_a and crit_b
    lab = lambda ok: "ERFÜLLT" if ok else "NICHT erfüllt"
    print(f"\nKriterium H10 (a) Sharpe-Diff >= {SHARPE_MIN_DIFF:.2f} und p <= {P_MAX:.2f}: {lab(crit_a)} "
          f"(Diff {sharpe_diff:+.3f}, p {boot['p_value']:.3f})")
    print(f"Kriterium H10 (b) MaxDD IV nicht mehr als {MAXDD_TOL * 100:.0f} Pp. schlechter als EW: {lab(crit_b)} "
          f"({_pct(k_ivf['max_dd'])} gegen {_pct(k_ewf['max_dd'])})")
    print(f"Gesamt H10: {lab(total)}")

    stats = pd.DataFrame.from_dict(
        {name: {"Jahre": d["years"], "CAGR": d["cagr"], "Vol": d["vol"], "Sharpe": d["sharpe"],
                "MaxDD": d["max_dd"], "Calmar": d["calmar"], "Schlechtestes_Jahr": d["worst_year"]}
         for name, d in rows.items()}, orient="index")
    stats.index.name = "Serie"
    stats["Sharpe_Diff_Vergleich"] = float("nan")
    stats["Boot_ci90_lo"] = float("nan")
    stats["Boot_ci90_hi"] = float("nan")
    stats["Boot_p"] = float("nan")
    stats.loc["IV-Filter (H10)", ["Sharpe_Diff_Vergleich", "Boot_ci90_lo", "Boot_ci90_hi", "Boot_p"]] = [
        sharpe_diff, boot["ci90"][0], boot["ci90"][1], boot["p_value"]]
    stats.loc["IV-B&H", ["Sharpe_Diff_Vergleich", "Boot_ci90_lo", "Boot_ci90_hi", "Boot_p"]] = [
        sharpe_diff_bh, boot_bh["ci90"][0], boot_bh["ci90"][1], boot_bh["p_value"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stats.to_csv(OUT_STATS, encoding="utf-8", float_format="%.6f")
    basket_df = pd.DataFrame({"iv_filter": iv_f, "ew_filter": ew_f, "iv_bh": iv_b, "ew_bh": ew_b,
                              "n_markets": n_iv})
    basket_df.index.name = "date"
    basket_df.reset_index().assign(date=lambda d: d["date"].dt.date.astype(str)).to_csv(
        OUT_BASKET, index=False, encoding="utf-8", float_format="%.10f")
    print(f"\nCSV gespeichert: {OUT_STATS}")
    print(f"CSV gespeichert: {OUT_BASKET}")


if __name__ == "__main__":
    main()
