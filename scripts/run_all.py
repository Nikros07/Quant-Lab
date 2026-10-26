"""Backtest-Harness: lässt ALLE registrierten Strategien durch denselben Prüfstand laufen.

Aufruf (aus Projektwurzel):
    .venv\\Scripts\\python.exe scripts\\run_all.py                 # nur Auswahlzeitraum bis 2022-12-31
    .venv\\Scripts\\python.exe scripts\\run_all.py --ids tsmom_12m  # einzelne
    .venv\\Scripts\\python.exe scripts\\run_all.py --final          # Holdout (ab 2023) EINMAL öffnen

Der Holdout wird ohne --final nie geladen (Daten werden vor dem Backtest abgeschnitten).
Jede Öffnung des Holdouts wird in results/holdout_log.json protokolliert.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from qlab import controls, metrics, stats  # noqa: E402
from qlab.data import Panel, french, load_panel, panel_from_returns, risk_free_daily  # noqa: E402
from qlab.engine import CostModel, TaxModel, check_causality, run_backtest  # noqa: E402
from strategies._registry import discover  # noqa: E402

IS_END = "2022-12-31"
HOLDOUT_START = "2023-01-01"
COMMON_START = "2004-01-01"      # gemeinsames Fenster für Vergleich/PBO
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)


def fmt_pct(x, d=1):
    return "–" if x is None or not np.isfinite(x) else f"{100 * x:.{d}f}%"


def fmt_num(x, d=2):
    return "–" if x is None or not np.isfinite(x) else f"{x:.{d}f}"


def build_benchmarks(end: str | None, exec_mode: str):
    bp = load_panel(["SPY", "IEF"], start="1993-01-01")
    if end:
        bp = bp.truncate(end)
    rf = risk_free_daily(bp.close.index)
    cost = CostModel()
    bq = bp.slice("2003-01-01")
    out, out_t = {}, {}
    for name, panel_, tgt in (("SPY", bp, controls.buy_and_hold(bp, "SPY")),
                              ("60/40", bq, controls.fixed_mix(bq, {"SPY": 0.6, "IEF": 0.4}))):
        out[name] = run_backtest(panel_, tgt, cost=cost, exec_mode=exec_mode, rf=rf)
        out_t[name] = run_backtest(panel_, tgt, cost=cost, exec_mode=exec_mode, rf=rf, tax=TaxModel())
    # Langhistorie-Benchmark: US-Gesamtmarkt aus Ken French (ab 1926), für Strategien vor 1993
    fdf = french("F-F_Research_Data_Factors", daily=True)
    mret = (fdf["Mkt-RF"] + fdf["RF"])
    if end:
        mret = mret.loc[:end]
    mp = panel_from_returns(pd.DataFrame({"MKT": mret}))
    mrf = fdf["RF"].reindex(mp.close.index).fillna(0.0)
    out["MKT"] = run_backtest(mp, controls.buy_and_hold(mp, "MKT"), cost=cost, exec_mode=exec_mode, rf=mrf)
    out_t["MKT"] = run_backtest(mp, controls.buy_and_hold(mp, "MKT"), cost=cost, exec_mode=exec_mode, rf=mrf,
                                tax=TaxModel(tf_map={"MKT": 0.30}))
    return out, out_t, rf


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default="")
    ap.add_argument("--final", action="store_true", help="Holdout ab 2023 öffnen (einmalig, wird protokolliert)")
    ap.add_argument("--exec", default="open", choices=["open", "close_next", "close"])
    ap.add_argument("--cost-mult", type=float, default=1.0, help="Kosten-Multiplikator (Stresstest)")
    ap.add_argument("--tag", default="")
    ap.add_argument("--skip-causality", action="store_true")
    ap.add_argument("--n-boot", type=int, default=1000)
    args = ap.parse_args()

    tag = args.tag or ("final" if args.final else "is")
    end = None if args.final else IS_END
    if args.final:
        log = RESULTS / "holdout_log.json"
        entries = json.loads(log.read_text()) if log.exists() else []
        entries.append({"opened_at": time.strftime("%Y-%m-%d %H:%M:%S"), "ids": args.ids or "ALL", "exec": args.exec})
        log.write_text(json.dumps(entries, indent=2))
        print(f"[holdout] Öffnung #{len(entries)} protokolliert")

    mods = discover()
    ids = [i for i in args.ids.split(",") if i] or sorted(mods)
    print(f"{len(ids)} Strategien, Zeitraum bis {end or 'heute'}, exec={args.exec}")

    benches, benches_t, rf_all = build_benchmarks(end, args.exec)
    bench_ret = {k: v.ret for k, v in benches.items()}
    bench_ret_t = {k: v.ret_after_liquidation_tax() for k, v in benches_t.items()}

    runs: list[dict] = []
    errors: list[str] = []
    ret_store: dict[str, pd.Series] = {}

    for sid in ids:
        mod = mods[sid]
        spec = mod.SPEC
        variants = {"base": spec.get("params", {})}
        for vn, vp in (spec.get("variants") or {}).items():
            variants[vn] = {**spec.get("params", {}), **vp}
        try:
            panel = mod.load() if hasattr(mod, "load") else load_panel(spec["tickers"], start=spec.get("start", "1993-01-01"))
            if end:
                panel = panel.truncate(end)
            cost = CostModel(per_ticker_bps={k: v * args.cost_mult for k, v in (spec.get("cost_bps") or {}).items()},
                             default_bps=5.0 * args.cost_mult)
            rf = risk_free_daily(panel.close.index)
            causal_ok, causal_msg = None, ""
            if not args.skip_causality:
                problems = check_causality(lambda p, _m=mod, _pp=variants["base"]: _m.weights(p, **_pp), panel)
                causal_ok, causal_msg = (not problems), "; ".join(problems[:2])
                if problems:
                    print(f"  !! {sid}: KAUSALITÄT VERLETZT -> {causal_msg}")
            for vn, vp in variants.items():
                w = mod.weights(panel, **vp)
                res = run_backtest(panel, w, cost=cost, exec_mode=args.exec, rf=rf)
                res_t = run_backtest(panel, w, cost=cost, exec_mode=args.exec, rf=rf, tax=TaxModel())
                first = w.dropna(how="all").index.min()
                ret = res.ret.loc[first:]
                key = sid if vn == "base" else f"{sid}:{vn}"
                ret_store[key] = ret
                runs.append({"key": key, "id": sid, "variant": vn, "family": spec.get("family", ""),
                             "name": spec["name"], "res": res, "res_t": res_t, "first": first, "causal_ok": causal_ok,
                             "causal_msg": causal_msg, "skipped": res.skipped_orders})
            print(f"  ok  {sid} ({len(variants)} Läufe)")
        except Exception as exc:  # nicht verschlucken: im Bericht ausweisen
            errors.append(f"{sid}: {exc}")
            print(f"  FEHLER {sid}: {exc}")
            traceback.print_exc()

    if not runs:
        print("Keine Läufe.")
        return

    # Mehrfachtest-Maß: alle Läufe (inkl. Varianten) zählen als Versuche
    sr_all = np.array([metrics.sharpe_daily(r["res"].ret.loc[r["first"]:], r["res"].rf.loc[r["first"]:]) for r in runs])
    sr_all = sr_all[np.isfinite(sr_all)]
    n_trials = len(runs)
    var_sr = float(np.var(sr_all, ddof=1)) if len(sr_all) > 2 else 1e-4

    rows = []
    for r in runs:
        res, first = r["res"], r["first"]
        ret = res.ret.loc[first:]
        rf = res.rf.loc[first:]
        bn = "SPY" if first >= pd.Timestamp("1993-03-01") else "MKT"   # Benchmark je nach Zeitraum
        spy_r = bench_ret[bn].reindex(ret.index).fillna(0.0)
        s = metrics.summarize(ret, rf, res.turnover, res.cost, bench=spy_r, exposure=res.gross_exposure)
        if "cagr" not in s:
            continue
        spy_s = metrics.summarize(spy_r, rf)
        ret_t = r["res_t"].ret_after_liquidation_tax().loc[first:]
        spy_t = bench_ret_t[bn].reindex(ret_t.index).fillna(0.0)
        st = metrics.summarize(ret_t, rf, bench=spy_t)
        spy_st = metrics.summarize(spy_t, rf)
        dsr = stats.deflated_sharpe(ret, n_trials, var_sr, rf=rf)
        boot = stats.bootstrap_sharpe_diff(ret, spy_r, rf=rf, n_boot=args.n_boot)
        roll = metrics.rolling_window_table(ret, spy_r)
        row = {
            "key": r["key"], "family": r["family"], "variant": r["variant"], "start": str(first.date()), "bench": bn,
            "years": s["years"], "cagr": s["cagr"], "vol": s["vol"], "sharpe": s["sharpe"], "max_dd": s["max_dd"],
            "calmar": s["calmar"], "worst_year": s["worst_year"], "turnover_py": s.get("turnover_per_year"),
            "cost_drag_py": s.get("cost_drag_per_year"), "avg_gross": s.get("avg_gross"),
            "beta": s.get("beta"), "alpha_ann": s.get("alpha_ann"),
            "spy_cagr": spy_s["cagr"], "spy_sharpe": spy_s["sharpe"], "spy_maxdd": spy_s["max_dd"],
            "sharpe_diff_vs_spy": boot["sharpe_diff"], "sharpe_diff_p": boot["p_value"],
            "sharpe_diff_ci_lo": boot["ci90"][0], "sharpe_diff_ci_hi": boot["ci90"][1],
            "share_5y_beating_spy": roll.get("share_beating"), "windows": roll.get("windows"),
            "dsr": dsr["dsr"], "psr0": dsr["psr_vs_zero"], "sr0_annual": dsr["sr0_annual"],
            "cagr_at": st["cagr"], "sharpe_at": st["sharpe"], "maxdd_at": st["max_dd"],
            "spy_cagr_at": spy_st["cagr"], "spy_sharpe_at": spy_st["sharpe"],
            "tax_drag_py": s["cagr"] - st["cagr"],
            "causal_ok": r["causal_ok"], "skipped_orders": r["skipped"],
        }
        if args.final:
            h = ret.loc[HOLDOUT_START:]
            hs = metrics.summarize(h, rf.reindex(h.index), bench=spy_r.reindex(h.index))
            row.update({"hold_cagr": hs.get("cagr"), "hold_sharpe": hs.get("sharpe"), "hold_maxdd": hs.get("max_dd"),
                        "hold_spy_cagr": metrics.summarize(spy_r.loc[HOLDOUT_START:], rf.reindex(spy_r.loc[HOLDOUT_START:].index)).get("cagr")})
        rows.append(row)

    df = pd.DataFrame(rows).sort_values("sharpe", ascending=False)
    df.to_csv(RESULTS / f"summary_{tag}.csv", index=False)

    # Gemeinsames Fenster + PBO nur über Basisläufe und Varianten mit Daten ab COMMON_START
    mat = pd.DataFrame({k: v for k, v in ret_store.items()})
    mat = mat.loc[COMMON_START:]
    # Reihen mit Wochenendtagen (Krypto, 7 Tage/Woche) blähen die Zeilen-Union auf und machen alle Börsentag-Reihen
    # an Wochenenden zu NaN (dann bliebe keine Reihe übrig): sie nehmen am PBO-Fenster nicht teil.
    weekend_cols = [c for c in mat.columns if (mat[c].dropna().index.dayofweek >= 5).any()]
    mat = mat.drop(columns=weekend_cols).dropna(how="all")
    mat = mat.dropna(axis=1, how="any")
    pbo = stats.pbo_cscv(mat) if mat.shape[1] >= 3 else {"pbo": float("nan"), "note": "zu wenige Strategien im gemeinsamen Fenster"}
    mat.to_parquet(RESULTS / f"returns_common_{tag}.parquet")

    # Berichte
    md = []
    md.append(f"# Backtest-Ergebnis `{tag}` (bis {end or 'heute'}, Ausführung: {args.exec}, Kosten ×{args.cost_mult})\n")
    md.append(f"Läufe: **{n_trials}** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). "
              f"Streuung der Tages-Sharpe über alle Läufe: {var_sr:.2e}. "
              f"PBO (gemeinsames Fenster ab {COMMON_START}, {pbo.get('n_strategies', 0)} Läufe): **{fmt_num(pbo.get('pbo'))}**.\n")
    md.append("Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).\n")
    for k, b in benches.items():
        bs = metrics.summarize(b.ret.loc[b.ret.ne(0).idxmax():], b.rf)
        md.append(f"- **{k}**: CAGR {fmt_pct(bs['cagr'])}, Vol {fmt_pct(bs['vol'])}, Sharpe {fmt_num(bs['sharpe'])}, MaxDD {fmt_pct(bs['max_dd'])}")
    md.append("\n## Rangliste nach Sharpe\n")
    md.append("| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for _, x in df.iterrows():
        md.append("| {key} | {fam} | {st} | {yr} | {cagr} | {vol} | {sh} | {dd} | {ds} ({lo}…{hi}) | {p} | {win} | {dsr} | {to} | {cd} |".format(
            key=x["key"], fam=x["family"], st=x["start"][:7], yr=fmt_num(x["years"], 1), cagr=fmt_pct(x["cagr"]), vol=fmt_pct(x["vol"]),
            sh=fmt_num(x["sharpe"]), dd=fmt_pct(x["max_dd"]), ds=fmt_num(x["sharpe_diff_vs_spy"]), lo=fmt_num(x["sharpe_diff_ci_lo"]),
            hi=fmt_num(x["sharpe_diff_ci_hi"]), p=fmt_num(x["sharpe_diff_p"], 3), win=fmt_pct(x["share_5y_beating_spy"], 0),
            dsr=fmt_num(x["dsr"], 3), to=fmt_num(x["turnover_py"], 1), cd=fmt_pct(x["cost_drag_py"], 2)))
    md.append("")
    md.append("## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)")
    md.append("")
    md.append("| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |")
    md.append("|---|---|---|---|---|---|---|")
    for _, x in df.sort_values("cagr_at", ascending=False).iterrows():
        md.append("| {k} | {a} | {b} | {c} | {d} | {e} | {f} |".format(
            k=x["key"], a=fmt_pct(x["cagr"]), b=fmt_pct(x["cagr_at"]), c=fmt_pct(x["tax_drag_py"], 2), d=fmt_num(x["sharpe_at"]),
            e=fmt_pct(x["spy_cagr_at"]), f=fmt_pct(x["cagr_at"] - x["spy_cagr_at"])))
    bad = df[df["causal_ok"] == False]  # noqa: E712
    if len(bad):
        md.append("\n## ⚠ Kausalitätstest verletzt (Ergebnisse unbrauchbar bis behoben)\n")
        for _, x in bad.iterrows():
            md.append(f"- {x['key']}")
    if errors:
        md.append("\n## Fehler\n" + "\n".join(f"- {e}" for e in errors))
    (RESULTS / f"SUMMARY_{tag}.md").write_text("\n".join(md), encoding="utf-8")

    # Kurven
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        top = [k for k in df["key"].head(8)]
        fig, ax = plt.subplots(figsize=(11, 6))
        for k in top:
            s = ret_store[k].loc[COMMON_START:]
            ax.plot((1 + s).cumprod(), lw=1, label=k)
        for k, b in benches.items():
            ax.plot((1 + b.ret.loc[COMMON_START:]).cumprod(), lw=2, ls="--", label=k)
        ax.set_yscale("log"); ax.legend(fontsize=7, ncol=2); ax.set_title(f"Top-8 nach Sharpe ab {COMMON_START} (log)")
        fig.tight_layout(); fig.savefig(RESULTS / f"equity_{tag}.png", dpi=110)
    except Exception as exc:
        print("Plot übersprungen:", exc)

    print("\n" + "\n".join(md[:12]))
    print(f"\nGeschrieben: results/SUMMARY_{tag}.md, summary_{tag}.csv")


if __name__ == "__main__":
    main()
