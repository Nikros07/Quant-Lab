import sys, time; sys.path.insert(0, ".")
import pandas as pd
from qlab.data import french
from qlab.engine import check_causality
from strategies import tom_spy_m2_p3 as main
ff = french("F-F_Research_Data_Factors", daily=True)
fp = main.build_panel(ff["Mkt-RF"] + ff["RF"]).truncate("1960-12-31")
idx = fp.close.index
sub = idx[(idx>="1955-01-01")&(idx<="1957-12-31")]
cuts=[]
for _, g in sub.to_series().groupby([sub.year, sub.month]):
    cuts += list(g.index[-4:])
t=time.time(); bad = check_causality(lambda p: main.weights(p), fp, cuts=cuts)
print(f"main 1955-57 letzte 4 Tage je Monat: Schnitte {len(cuts)}, Verstoesse {len(bad)}, {time.time()-t:.0f}s", flush=True)
for x in bad: print("  ", x)
