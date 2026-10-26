import sys, time; sys.path.insert(0, ".")
import pandas as pd
from qlab.data import french
from qlab.engine import check_causality
from strategies import tom_spy_m2_p3 as main
ff = french("F-F_Research_Data_Factors", daily=True)
fp = main.build_panel(ff["Mkt-RF"] + ff["RF"]).truncate("2000-12-31")
idx = fp.close.index
sub = idx[(idx>="1990-06-01")&(idx<="2000-12-31")]
cuts=[]
for _, g in sub.to_series().groupby([sub.year, sub.month]):
    cuts += [g.index[-1]]
t=time.time(); bad = check_causality(lambda p: main.weights(p), fp, cuts=cuts)
print(f"main 1990-2000 letzter Tag je Monat: Schnitte {len(cuts)}, Verstoesse {len(bad)}, {time.time()-t:.0f}s", flush=True)
for x in bad[:5]: print("  ", x)
