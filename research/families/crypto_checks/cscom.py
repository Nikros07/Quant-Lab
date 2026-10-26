from common import *
pd.set_option("display.width",200)
U=["GLD","SLV","DBA","DBB","USO","UNG","CPER","PPLT","PALL"]
C=pd.concat({t:load(t)["Close"] for t in U},axis=1).sort_index()
O=pd.concat({t:load(t)["Open"] for t in U},axis=1).sort_index()
C=C.loc["2007-06-01":]; O=O.loc["2007-06-01":]
r_oo=O.shift(-1)/O-1
irx=load("^IRX")["Close"].reindex(C.index).ffill()/100/252
mom=C.shift(21)/C.shift(252)-1
me=C.index.to_series().groupby([C.index.year,C.index.month]).last().values
me=pd.DatetimeIndex(me)
def backtest(k, longshort=False, cost=0.0010, long_only_pos=True, sma_filter=False):
    pos=pd.DataFrame(0.0,index=C.index,columns=U)
    cur=pd.Series(0.0,index=U)
    sma=C.rolling(210).mean()
    for i,d in enumerate(C.index):
        # pos used for return of day d was decided at previous close
        pos.loc[d]=cur
        if d in me:
            m=mom.loc[d].dropna()
            if len(m)>=k+1:
                w=pd.Series(0.0,index=U)
                top=m.sort_values(ascending=False).index[:k]
                w[top]=1.0/k
                if sma_filter:
                    for t in top:
                        if not (C.loc[d,t]>sma.loc[d,t]): w[t]=0.0
                if longshort:
                    bot=m.sort_values().index[:k]; w[bot]=-1.0/k
                cur=w
    # pos at d is held from open d to open d+1 -> but decided at close of previous day: pos.loc[d] was set before updating cur at d, so lag of one day OK
    ret=(pos*r_oo).sum(axis=1)
    turn=pos.diff().abs().sum(axis=1)
    ret=ret-turn*cost
    cash=(1-pos.abs().sum(axis=1).clip(upper=1))*irx if not longshort else irx
    return (ret+cash), turn
start="2008-06-02"; end="2026-10-08"
# EW benchmark monthly rebalanced of available
ew=pd.Series(0.0,index=C.index); cur=pd.Series(0.0,index=U); posb=pd.DataFrame(0.0,index=C.index,columns=U)
for d in C.index:
    posb.loc[d]=cur
    if d in me:
        av=C.loc[d].dropna().index; cur=pd.Series(0.0,index=U); cur[av]=1.0/len(av)
retb=(posb*r_oo).sum(axis=1)-posb.diff().abs().sum(axis=1)*0.0010
rows=[]
res={"EW9 monthly":retb}
for k in (2,3,4):
    res[f"CS-MOM12-1 long top{k}"]=backtest(k)[0]
res["CS-MOM top3 + SMA210 filter"]=backtest(3,sma_filter=True)[0]
res["CS-MOM L/S top3-bot3 (not retail-feasible)"]=backtest(3,longshort=True)[0]
for k,r in res.items():
    for pn,(a,b) in {"ALL":(start,end),"2008-2015":(start,"2015-12-31"),"2016-2026":("2016-01-01",end)}.items():
        rows.append(dict(strat=k,period=pn,**metrics(r.loc[a:b],252,irx)))
print(pd.DataFrame(rows).to_string())
print("turnover long top3 / yr:", round(backtest(3)[1].loc[start:end].sum()/((len(C.loc[start:end]))/252),1))
