import sys; sys.path.insert(0, ".")
import pandas as pd
from qlab.data import french, risk_free_daily
from qlab.engine import CostModel, run_backtest
from qlab import metrics
from strategies import tom_spy_m2_p3 as main
ff = french("F-F_Research_Data_Factors", daily=True)
fp = main.build_panel(ff["Mkt-RF"] + ff["RF"]).truncate("2022-12-31")
w = main.weights(fp)
res = run_backtest(fp, w, cost=CostModel(per_ticker_bps={"MKT": 2.0}), rf=ff["RF"].reindex(fp.close.index).fillna(0.0))
for a,b in [("1926-07-01","1992-12-31"),("1993-01-01","2022-12-31"),("2004-01-01","2022-12-31")]:
    r = res.ret.loc[a:b]; rf = res.rf.loc[a:b]
    s = metrics.summarize(r, rf)
    print(a,b, "CAGR", round(s["cagr"],4), "Sharpe", round(s["sharpe"],2), "avg_gross", round(float(res.gross_exposure.loc[a:b].mean()),3))
