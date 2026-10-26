import sys
sys.path.insert(0, r"C:\Users\spide\Desktop\Projekte\Quant-Lab")
import pandas as pd
from qlab.calendar import month_end_flags
from strategies import bond_composite_3sig_longonly as m
tnx, irx, pie = m.load_signal_inputs()
ief = pd.read_parquet(r"C:\Users\spide\Desktop\Projekte\Quant-Lab\data_cache\px_IEF.parquet")
c = ief["Close"]
idx = c.index.union(tnx.dropna().index)
idx = idx[(idx >= "2002-07-30") & (idx <= "2022-12-31")]
f = month_end_flags(idx)
me = idx[f.to_numpy()]
miss = [d for d in me if pd.isna(c.reindex(idx).loc[d])]
print("union days", len(idx), "month ends", len(me), "month ends without IEF close", len(miss))
print("examples", [str(d.date()) for d in miss[:10]])
tnx_only = idx.difference(c.index)
print("days only in ^TNX union:", len(tnx_only))
