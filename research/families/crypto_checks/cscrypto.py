from common import *
pd.set_option("display.width",200)
U=["BTC-USD","ETH-USD","XRP-USD","LTC-USD","DOGE-USD","BCH-USD","ADA-USD","XLM-USD","BNB-USD","LINK-USD"]
C=pd.concat({t:load(t)["Close"] for t in U},axis=1).sort_index()
O=pd.concat({t:load(t)["Open"] for t in U},axis=1).sort_index()
C=C.loc["2017-11-09":]; O=O.loc["2017-11-09":]
print(C.isna().sum().to_dict())
r_oo=O.shift(-1)/O-1
irx=load("^IRX")["Close"].reindex(C.index).ffill()/100/365
def mom(w): return C/C.shift(7*w)-1
rebal=[d for d in C.index if d.weekday()==6]   # Sunday close (UTC) -> trade Monday open
rebal=set(rebal)
def bt(w,k,ls=False,cost=0.0020,hold_mkt=False):
    m=mom(w); cur=pd.Series(0.0,index=U); pos=pd.DataFrame(0.0,index=C.index,columns=U)
    for d in C.index:
        pos.loc[d]=cur
        if d in rebal:
            x=m.loc[d].dropna()
            if len(x)>=2*k:
                cur=pd.Series(0.0,index=U); cur[x.sort_values(ascending=False).index[:k]]=1.0/k
                if ls: cur[x.sort_values().index[:k]]=-1.0/k
    ret=(pos*r_oo).sum(axis=1)-pos.diff().abs().sum(axis=1)*cost
    ret=ret+(1-pos.sum(axis=1).clip(upper=1))*irx if not ls else ret
    return ret
# EW benchmark weekly rebalanced
cur=pd.Series(0.0,index=U); posb=pd.DataFrame(0.0,index=C.index,columns=U)
for d in C.index:
    posb.loc[d]=cur
    if d in rebal:
        av=C.loc[d].dropna().index; cur=pd.Series(0.0,index=U); cur[av]=1/len(av)
ewr=(posb*r_oo).sum(axis=1)-posb.diff().abs().sum(axis=1)*0.0020
res={"EW10 weekly":ewr,"BTC B&H":r_oo["BTC-USD"]}
for w in (1,3,4,8,16):
    res[f"CS long top3 mom{w}w"]=bt(w,3)
res["L/S top3-bot3 mom3w (gross shortable, no borrow cost)"]=bt(3,3,ls=True)
res["L/S top3-bot3 mom16w"]=bt(16,3,ls=True)
rows=[]
for k,r in res.items():
    for pn,(a,b) in {"ALL":("2018-02-01","2026-10-11"),"2018-2021":("2018-02-01","2021-12-31"),"2022-2026":("2022-01-01","2026-10-11")}.items():
        rows.append(dict(strat=k,period=pn,**metrics(r.loc[a:b],365,irx)))
print(pd.DataFrame(rows).to_string())
