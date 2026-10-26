import sys, time; sys.path.insert(0, ".")
import pandas as pd, numpy as np
from qlab.data import french, load_ticker
from qlab.engine import check_causality
from strategies import tom_spy_m2_p3 as main, tom_spy_m2_p3_etf as etf
def month_tail_cuts(idx, a, b, k=4):
    sub = idx[(idx>=a)&(idx<=b)]
    out=[]
    for _, g in sub.to_series().groupby([sub.year, sub.month]):
        out += list(g.index[-k:])
    return out
def run(name, fn, panel, cuts):
    t=time.time(); bad = check_causality(fn, panel, cuts=cuts)
    print(f"{name}: Schnitte {len(cuts)}, Verstoesse {len(bad)}, {time.time()-t:.0f}s", flush=True)
    for b in bad[:4]: print("   ", b, flush=True)
spy = load_ticker("SPY", start="1993-01-01", max_age_days=1e9).loc[:"2022-12-31"]
ep = etf.build_panel(spy)
run("ETF base 1993-2022", lambda p: etf.weights(p), ep, month_tail_cuts(ep.close.index, "1993-06-01", "2022-12-31"))
ff = french("F-F_Research_Data_Factors", daily=True)
fp = main.build_panel(ff["Mkt-RF"] + ff["RF"]).truncate("2022-12-31")
run("main base 1990-2022", lambda p: main.weights(p), fp, month_tail_cuts(fp.close.index, "1990-06-01", "2022-12-31"))
run("main base 1960-1989 (jedes 2. Jahr)", lambda p: main.weights(p), fp,
    [c for c in month_tail_cuts(fp.close.index, "1960-01-01", "1989-12-31") if c.year % 2 == 0])
