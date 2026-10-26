"""Wegwerf-Audit (nur lesend): Strategie vs 50/50-Buy&Hold DBC/GLD je Dekade, bis 2022-12-31 (kein Holdout)."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT = Path("C:/Users/spide/Desktop/Projekte/Quant-Lab")
sys.path.insert(0, str(ROOT))
from qlab import metrics
from qlab.data import load_panel, risk_free_daily
from qlab.engine import CostModel, run_backtest
from qlab.controls import buy_and_hold, fixed_mix
from strategies import commodity_gold_trend_dbc_gld as S

p = load_panel(["DBC", "GLD"], start="2004-01-01").truncate("2022-12-31")
rf = risk_free_daily(p.close.index)
cost = CostModel(per_ticker_bps={"DBC": 10.0, "GLD": 10.0})
w = S.weights(p)
first = w.index.min()
strat = run_backtest(p, w, cost=cost, rf=rf)
# 50/50 B&H ab gleichem Startdatum: Startgewichte am ersten Signaltag, dann Drift (kein Rebalancing)
bh_w = pd.DataFrame(0.0, index=[first], columns=["DBC", "GLD"]); bh_w.loc[first] = [0.5, 0.5]
bh = run_backtest(p, bh_w, cost=cost, rf=rf)
def sr(res, a, b):
    return metrics.sharpe_daily(res.ret.loc[a:b], res.rf.loc[a:b]) * np.sqrt(252)
print("erster Signaltag", first.date())
for name, a, b in [("gesamt", first, "2022-12-31"), ("2006-2015", first, "2015-12-31"), ("2016-2022", "2016-01-01", "2022-12-31")]:
    s1, s2 = sr(strat, a, b), sr(bh, a, b)
    print(f"{name}: Strategie {s1:.2f} | 50/50 B&H {s2:.2f} | Diff {s1-s2:+.2f}")
