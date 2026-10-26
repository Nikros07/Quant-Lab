"""Misst die vorab registrierten Ideen H7-H9 gegen die Basis `trend_ma12_us_equity_cash_etf` (docs/HYPOTHESEN.md, Eintrag H7-H10).

Kriterium (vorab festgelegt): dSharpe (neu - Basis) >= +0,10 mit stationärem Bootstrap p (einseitig) <= 0,10
UND MaxDD des Neuen nicht um mehr als 2 Prozentpunkte schlechter als die Basis.
Auswahlzeitraum bis 2022-12-31, Holdout ab 2023 wird nicht geladen. Ausführung Eröffnung Folgetag (Lab-Standard),
Kosten aus SPEC["cost_bps"], Cash = US-RF. Vergleich jeweils ab dem späteren der beiden ersten Gewichtstage.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import pandas as pd

from qlab import metrics, stats
from qlab.data import load_panel, risk_free_daily
from qlab.engine import CostModel, TaxModel, run_backtest
from strategies._registry import discover

END = "2022-12-31"
BASE_ID = "trend_ma12_us_equity_cash_etf"
RUNS = [  # (Modul-ID, Variante, Hypothese)
    ("trend_ma12_bond_substitute_etf", "base", "H7"),
    ("trend_ma12_bond_substitute_etf", "ief", "H7"),
    ("trend_ma12_bond_substitute_etf", "uncond", "H7"),
    ("trend_ma12_band_etf", "base", "H8"),
    ("trend_ma12_volscaled_etf", "base", "H9"),
    ("trend_ma12_volscaled_etf", "target10", "H9"),
]
TAX_TF = {"VUSTX": 0.0}          # Anleihenfonds: keine Teilfreistellung (Default der Engine wäre Aktienfonds 30 %)
MAXDD_TOL = 0.02


def run(mod, variant: str):
    spec = mod.SPEC
    params = dict(spec.get("params", {}))
    if variant != "base":
        params.update(spec["variants"][variant])
    panel = (mod.load() if hasattr(mod, "load") else load_panel(spec["tickers"], start=spec.get("start", "1993-01-01"))).truncate(END)
    cost = CostModel(per_ticker_bps=spec.get("cost_bps") or {}, default_bps=5.0)
    rf = risk_free_daily(panel.close.index)
    w = mod.weights(panel, **params)
    res = run_backtest(panel, w, cost=cost, exec_mode="open", rf=rf)
    res_t = run_backtest(panel, w, cost=cost, exec_mode="open", rf=rf, tax=TaxModel(tf_map=TAX_TF))
    first = w.dropna(how="all").index.min()
    return res, res_t, rf, first, w


mods = discover()
base_res, base_res_t, base_rf, base_first, _ = run(mods[BASE_ID], "base")

rows = []
for mid, var, hyp in RUNS:
    if mid not in mods:
        print(f"[{hyp}] Modul {mid} fehlt")
        continue
    res, res_t, rf, first, w = run(mods[mid], var)
    start = max(first, base_first)
    r, b = res.ret.loc[start:], base_res.ret.loc[start:]
    rt, bt = res_t.ret_after_liquidation_tax().loc[start:], base_res_t.ret_after_liquidation_tax().loc[start:]
    s, sb = metrics.summarize(r, rf), metrics.summarize(b, base_rf)
    st, sbt = metrics.summarize(rt, rf), metrics.summarize(bt, base_rf)
    bs = stats.bootstrap_sharpe_diff(r, b, rf=rf, n_boot=2000)
    d_sh = s["sharpe"] - sb["sharpe"]
    ok_sh = d_sh >= 0.10 and bs["p_value"] <= 0.10
    ok_dd = s["max_dd"] >= sb["max_dd"] - MAXDD_TOL
    rows.append({
        "H": hyp, "Lauf": mid.replace("trend_ma12_", "").replace("_etf", "") + ("" if var == "base" else f":{var}"),
        "ab": str(start.date()), "Jahre": s["years"],
        "CAGR": s["cagr"], "CAGR_Basis": sb["cagr"], "Vol": s["vol"], "Vol_Basis": sb["vol"],
        "Sharpe": s["sharpe"], "Sharpe_Basis": sb["sharpe"], "dSharpe": d_sh,
        "ci90_lo": bs["ci90"][0], "ci90_hi": bs["ci90"][1], "p": bs["p_value"],
        "MaxDD": s["max_dd"], "MaxDD_Basis": sb["max_dd"],
        "Sharpe_nSt": st["sharpe"], "Sharpe_Basis_nSt": sbt["sharpe"],
        "Umsatz/J": s.get("turnover_per_year"), "Kriterium_Sharpe": ok_sh, "Kriterium_DD": ok_dd, "Kriterium": ok_sh and ok_dd,
    })

df = pd.DataFrame(rows)
df.to_csv(ROOT / "results" / "H7_H9_vergleich.csv", index=False)
show = df.copy()
for c in ["CAGR", "CAGR_Basis", "Vol", "Vol_Basis", "MaxDD", "MaxDD_Basis"]:
    show[c] = (show[c] * 100).round(1).astype(str) + " %"
for c in ["Sharpe", "Sharpe_Basis", "dSharpe", "ci90_lo", "ci90_hi", "Sharpe_nSt", "Sharpe_Basis_nSt"]:
    show[c] = show[c].round(2)
show["p"] = show["p"].round(3)
show["Jahre"] = show["Jahre"].round(1)
show["Umsatz/J"] = show["Umsatz/J"].astype(float).round(2)
print(f"Basis: {BASE_ID}; Auswahlzeitraum bis {END}; Ausführung Eröffnung Folgetag; Vergleich auf gemeinsamem Fenster\n")
print(show.to_string(index=False))
print("\nKriterium je Lauf (dSharpe >= 0,10 UND p <= 0,10 UND MaxDD nicht > 2 Pp schlechter):")
for _, x in df.iterrows():
    print(f"  {x['H']} {x['Lauf']:22s} {'ERFÜLLT' if x['Kriterium'] else 'nicht erfüllt'}  "
          f"(dSharpe {x['dSharpe']:+.2f}, p {x['p']:.3f}, MaxDD {x['MaxDD'] * 100:.1f} % gegen {x['MaxDD_Basis'] * 100:.1f} %)")
