import pandas as pd, numpy as np
def load(t):
    d=pd.read_csv(f"px_{t.replace('=','_').replace('^','_')}.csv",index_col=0,parse_dates=True)
    return d
def irx_daily(index):
    d=load("^IRX")["Close"].reindex(index).ffill()/100/365.0   # calendar-day approx per row; refine below
    return d
def metrics(r, ppy=365, rf=None):
    r=r.dropna()
    if len(r)<30: return {}
    eq=(1+r).cumprod()
    yrs=len(r)/ppy
    cagr=eq.iloc[-1]**(1/yrs)-1
    vol=r.std()*np.sqrt(ppy)
    ex=r-(rf.reindex(r.index).fillna(0) if rf is not None else 0)
    sh=ex.mean()/r.std()*np.sqrt(ppy) if r.std()>0 else np.nan
    dd=(eq/eq.cummax()-1).min()
    return dict(CAGR=round(cagr*100,1),Vol=round(vol*100,1),Sharpe=round(sh,2),MaxDD=round(dd*100,1),N=len(r))
def run_pos(pos, ret_oo, cost):
    """pos known at close t-1 (already shifted), earns ret_oo; cost per unit one-way turnover"""
    turn=pos.diff().abs().fillna(pos.abs())
    return pos*ret_oo - turn*cost, turn
