import sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path("C:/Users/spide/Desktop/Projekte/Quant-Lab")
sys.path.insert(0, str(ROOT))
from qlab.data import load_panel, risk_free_daily
from qlab.engine import CostModel, run_backtest
from qlab import metrics
from strategies import crypto_trend_ens_btc_eth as s
panel = load_panel(["BTC-USD", "ETH-USD"], start="2014-09-17").truncate("2022-12-31")
w = s.weights(panel)
rf = risk_free_daily(panel.close.index)
print("erster ETH-Gewichtstag:", w.index[w["ETH-USD"] > 0][0].date(), "| ETH-Listing:", panel.close["ETH-USD"].first_valid_index().date())
print("max Summe Gewichte:", float(w.sum(axis=1).max()), "| min:", float(w.sum(axis=1).min()))
print("ETH-Gewicht an NaN-Kurs:", int(((w["ETH-USD"]>0) & panel.close["ETH-USD"].isna().reindex(w.index)).sum()))
for mult in (1.0, 2.0, 2.5):
    cost = CostModel(per_ticker_bps={k: v*mult for k, v in s.SPEC["cost_bps"].items()}, default_bps=5*mult)
    r = run_backtest(panel, w, cost=cost, rf=rf)
    ret = r.ret.loc["2015-09-01":]
    m = metrics.summarize(ret, rf.reindex(ret.index), turnover=r.turnover, cost=r.cost)
    print("mult %.1f  CAGR %.4f Sharpe %.3f MaxDD %.4f Umsatz/J %.2f Kosten/J %.4f" % (mult, m["cagr"], m["sharpe"], m["max_dd"], m["turnover_per_year"], m["cost_drag_per_year"]))
    if mult == 1.0:
        print("  avg gross %.3f" % r.gross_exposure.loc["2015-09-01":].mean())
