import sys
sys.path.insert(0, r"C:\Users\spide\Desktop\Projekte\Quant-Lab")
import pandas as pd, numpy as np
from strategies import bond_composite_3sig_longonly as m
tnx, irx, pie = m.load_signal_inputs()
idx = tnx.dropna().index
sig = m.signal_columns(tnx, irx, pie, idx)
r10, rc = m.synthetic_returns(sig[m.TNX], sig[m.IRX])
ief = pd.read_parquet(r"C:\Users\spide\Desktop\Projekte\Quant-Lab\data_cache\px_IEF.parquet")
print(ief.columns.tolist()[:6], ief.index.min(), ief.index.max(), len(ief))
c = ief["Close"] if "Close" in ief.columns else ief.iloc[:, 0]
ri = c.pct_change()
j = pd.concat([r10.rename("syn"), ri.rename("ief")], axis=1).loc["2003":"2022"].dropna()
print("n", len(j), "corr", round(j.corr().iloc[0,1],3))
for y, g in j.groupby(j.index.year):
    print(y, round((1+g.syn).prod()-1,4), round((1+g.ief).prod()-1,4))
print("ann mean syn", round(j.syn.mean()*252,4), "ief", round(j.ief.mean()*252,4))
print("ann vol syn", round(j.syn.std()*np.sqrt(252),4), "ief", round(j.ief.std()*np.sqrt(252),4))
print("nan gaps in ^TNX within 1962-2022:", int(tnx.loc[:"2022-12-31"].index.to_series().diff().dt.days.gt(10).sum()))
