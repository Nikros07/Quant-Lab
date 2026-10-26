import sys
sys.path.insert(0, r"C:\Users\spide\Desktop\Projekte\Quant-Lab")
import numpy as np, pandas as pd
from qlab.data import load_panel, risk_free_daily
from qlab.engine import CostModel, run_backtest
from strategies import svxy_term_structure_filter as s
p = load_panel(s.SPEC["tickers"], start=s.SPEC["start"]).truncate("2022-12-31")
print("Panel Start je Ticker:", {t: str(p.close[t].first_valid_index().date()) for t in p.close.columns})
print("NaN-Tage SVXY nach Start:", int(p.close["SVXY"].loc[p.close["SVXY"].first_valid_index():].isna().sum()))
print("NaN-Tage VIX/VIX3M:", int(p.close["^VIX"].isna().sum()), int(p.close["^VIX3M"].isna().sum()))
w = s.weights(p)["SVXY"]
print("Zeilen:", len(w), "erste:", w.index[0].date(), "Wechsel:", int((w.diff().abs()>0).sum()))
cost = CostModel(per_ticker_bps=s.SPEC["cost_bps"])
rf = risk_free_daily(p.close.index)
res = run_backtest(p, s.weights(p), cost=cost, rf=rf)
r = res.ret
print("min daily ret:", float(r.min()), r.idxmin().date(), "| 2nd:", float(r.nsmallest(3).iloc[1]), r.nsmallest(3).index[1].date())
print("returns < -40%:", [(d.date(), round(float(v),3)) for d, v in r[r < -0.40].items()])
print("ratio 2018-02-01..02-09:")
rr = s.term_ratio(p.close["^VIX"], p.close["^VIX3M"])
print(rr.loc["2018-02-01":"2018-02-09"].round(3).to_string())
print("w 2018-02:", w.loc["2018-01-25":"2018-02-28"].to_string())
nav = res.nav
dd = nav/nav.cummax()-1
print("MaxDD:", float(dd.min()), dd.idxmin().date())
print("Anteil Tage ON (Gewicht>0):", float((res.weights["SVXY"]>0).mean()))
print("Umsatz/J:", float(res.turnover.sum()/ (len(p.close)/252)))
for name, part in s.split_by_regime(r.loc[w.index[0]:]).items():
    if len(part): print(name, "n", len(part), "CAGR", float((1+part).prod()**(252/len(part))-1), "Vol", float(part.std()*np.sqrt(252)))
