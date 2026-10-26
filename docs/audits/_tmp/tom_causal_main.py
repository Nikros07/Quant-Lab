import sys, time; sys.path.insert(0, ".")
import pandas as pd
from qlab.data import french
from qlab.engine import check_causality
from strategies import tom_spy_m2_p3 as main
def tail_cuts(idx, a, b, k=2):
    sub = idx[(idx>=a)&(idx<=b)]
    out=[]
    for _, g in sub.to_series().groupby([sub.year, sub.month]):
        out += list(g.index[-k:])
    return out
ff = french("F-F_Research_Data_Factors", daily=True)
fp = main.build_panel(ff["Mkt-RF"] + ff["RF"]).truncate("2022-12-31")
for name,a,b,step in [("main 1990-2022",'1990-06-01','2022-12-31',1),("main 1955-1960 (letzte 4 Tage)", '1955-01-01','1960-12-31',0),("main 1960-1989 jedes 3. Jahr",'1960-01-01','1989-12-31',3)]:
    cuts = tail_cuts(fp.close.index, a, b, k=4 if step==0 else 2)
    if step==3: cuts=[c for c in cuts if c.year%3==0]
    t=time.time(); bad = check_causality(lambda p: main.weights(p), fp, cuts=cuts)
    print(f"{name}: Schnitte {len(cuts)}, Verstoesse {len(bad)}, {time.time()-t:.0f}s", flush=True)
    for x in bad[:6]: print("   ", x, flush=True)
