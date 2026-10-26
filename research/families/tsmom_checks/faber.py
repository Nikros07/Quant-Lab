# UNGETESTET - nur Plausibilitaetscheck fuer research/families/tsmom.md (2026-10-11). Vor Nutzung im Quant-Lab neu implementieren + Tests (Regel 2).
import yfinance as yf, pandas as pd, numpy as np, warnings
warnings.filterwarnings("ignore")
def dl(t):
    d = yf.download(t, period="max", auto_adjust=True, progress=False, threads=False)
    if isinstance(d.columns, pd.MultiIndex): d.columns=d.columns.get_level_values(0)
    return d["Close"].dropna()
U=["SPY","EFA","IEF","VNQ","DBC"]
P=pd.concat({t:dl(t) for t in U},axis=1).dropna()
irx=dl("^IRX")
rf=(irx.reindex(P.index).ffill().shift(1)/100/252).fillna(0)
R=P.pct_change()
idx=P.index
def month_ends(offset=0):
    g=pd.Series(idx,index=idx).groupby([idx.year,idx.month])
    out=[]
    for _,s in g:
        # offset = number of trading days AFTER the last trading day of previous month ... use position from end: offset 0 = last day
        arr=s.index
        if offset==0: out.append(arr[-1])
        else:
            pos=min(offset-1,len(arr)-1)  # offset-th trading day of month
            out.append(arr[pos])
    return pd.DatetimeIndex(out)
def sim(n_sma=10, offset=0, cost=0.0010, start="2006-12-01", cash="rf"):
    me=month_ends(offset)
    # monthly sampled prices at calendar month-ends (SMA uses last n monthly values sampled on signal dates)
    Pm=P.loc[me]
    sma=Pm.rolling(n_sma).mean()
    sig=(Pm>sma).astype(float).where(sma.notna())
    W={}
    for m in me:
        if m<pd.Timestamp(start) or sig.loc[m].isna().any(): continue
        i=idx.get_indexer([m])[0]
        if i+1>=len(idx): continue
        W[idx[i+1]]=sig.loc[m]*0.2
    W=pd.DataFrame(W).T
    pos=W.reindex(idx).ffill().shift(1)
    first=W.index[0]
    pos=pos.loc[first:]
    cashw=1-pos.sum(axis=1)
    gross=(pos*R.loc[first:,U]).sum(axis=1)+cashw*rf.loc[first:]
    dW=W.diff().abs().sum(axis=1); dW.iloc[0]=W.iloc[0].abs().sum()
    c=pd.Series(0.0,index=idx); c.loc[dW.index]=dW*cost
    net=gross-c.loc[first:]
    return net, gross, dW
def stats(r,label):
    r=r.dropna(); n=len(r); ex=r-rf.reindex(r.index)
    ann=(1+r).prod()**(252/n)-1; vol=r.std()*np.sqrt(252); sh=ex.mean()/ex.std()*np.sqrt(252)
    eq=(1+r).cumprod(); dd=(eq/eq.cummax()-1).min()
    return dict(label=label,cagr=round(ann*100,2),vol=round(vol*100,2),sharpe=round(sh,2),maxdd=round(dd*100,1))
rows=[]
net,gross,dW=sim()
first=net.index[0]
bh=R.loc[first:,U].mean(axis=1)   # daily rebalanced EW
for a,b in [("2006-12-01","2026-12-31"),("2007-01-01","2014-12-31"),("2015-01-01","2026-12-31"),("2020-01-01","2026-12-31")]:
    rows.append(stats(net.loc[a:b],f"GTAA5 SMA10 net10bp {a[:4]}-{b[:4]}"))
    rows.append(stats(bh.loc[a:b],f"EW5 BH {a[:4]}-{b[:4]}"))
print("GTAA5 turnover (sum|dw|)/yr:", round(dW.sum()/(len(net)/252),2), " first", first.date())
# sensitivity: SMA length and rebalance day offset
sens=[]
for n in (6,8,10,12):
    for off in (0,5,10,15):
        nt,_,_=sim(n_sma=n,offset=off)
        s=stats(nt,f"sma{n}_off{off}"); sens.append((n,off,s["cagr"],s["sharpe"],s["maxdd"]))
sdf=pd.DataFrame(sens,columns=["sma","day_offset","cagr","sharpe","maxdd"])
print(pd.DataFrame(rows).to_string())
print(sdf.pivot(index="sma",columns="day_offset",values="cagr"))
print(sdf.pivot(index="sma",columns="day_offset",values="sharpe"))
print("CAGR spread across offsets for SMA10:", sdf[sdf.sma==10].cagr.max()-sdf[sdf.sma==10].cagr.min())
# SPY only 10m SMA, 1993-
spy=dl("SPY"); r=spy.pct_change(); rf2=(irx.reindex(spy.index).ffill().shift(1)/100/252).fillna(0)
me=pd.DatetimeIndex(pd.Series(spy.index,index=spy.index).groupby([spy.index.year,spy.index.month]).last().values)
pm=spy.loc[me]; sig=(pm>pm.rolling(10).mean()).astype(float).where(pm.rolling(10).mean().notna())
W={}
for m in me:
    if pd.isna(sig.loc[m]): continue
    i=spy.index.get_indexer([m])[0]
    if i+1>=len(spy): continue
    W[spy.index[i+1]]=sig.loc[m]
W=pd.Series(W); pos=W.reindex(spy.index).ffill().shift(1)
f=W.index[0]; pos=pos.loc[f:]
g=pos*r.loc[f:]+(1-pos)*rf2.loc[f:]
dw=W.diff().abs().fillna(W.iloc[0]); c=pd.Series(0.0,index=spy.index); c.loc[dw.index]=dw*0.0005
n=g-c.loc[f:]
def st2(x,label):
    x=x.dropna(); ex=x-rf2.reindex(x.index); nn=len(x)
    eq=(1+x).cumprod(); 
    return dict(label=label,cagr=round(((1+x).prod()**(252/nn)-1)*100,2),vol=round(x.std()*np.sqrt(252)*100,2),sharpe=round(ex.mean()/ex.std()*np.sqrt(252),2),maxdd=round((eq/eq.cummax()-1).min()*100,1))
out=[]
for a,b in [("1993-01-01","2026-12-31"),("1993-01-01","2006-12-31"),("2007-01-01","2026-12-31"),("2015-01-01","2026-12-31")]:
    out.append(st2(n.loc[a:b],f"SPY SMA10 net5bp {a[:4]}-{b[:4]}")); out.append(st2(r.loc[f:].loc[a:b],f"SPY BH {a[:4]}-{b[:4]}"))
print(pd.DataFrame(out).to_string())
print("SPY SMA10 trades/yr:", round(len(W[W.diff().abs()>0])/((spy.index[-1]-f).days/365.25),2), " first signal", f.date())
