from common import *
pd.set_option("display.width",200)
irx_s=load("^IRX")["Close"]
def leg(tkr, n=210, cost=0.0010):
    d=load(tkr).dropna(); c=d["Close"]; o=d["Open"]; r_oo=o.shift(-1)/o-1
    return c,o,r_oo
tk=["DBC","GLD"]
D={t:leg(t) for t in tk}
idx=D["DBC"][0].index.intersection(D["GLD"][0].index)
rf=irx_s.reindex(idx).ffill()/100/252
tot=0; totbh=0; turns=0
for t in tk:
    c,o,r=D[t]; c=c.reindex(idx); r=r.reindex(idx)
    sig=(c>c.rolling(210).mean()).astype(float)
    pos=sig.shift(1).fillna(0)
    ret,turn=run_pos(pos,r,0.0010); ret=ret+(1-pos)*rf
    tot=tot+0.5*ret; totbh=totbh+0.5*r; turns=turns+0.5*turn
# BH monthly rebal approx = daily rebal 50/50
for pn,(a,b) in {"ALL":("2006-06-01","2026-10-08"),"2006-2015":("2006-06-01","2015-12-31"),"2016-2026":("2016-01-01","2026-10-08"),"2022-2026":("2022-01-01","2026-10-08")}.items():
    print("DBC+GLD trend",pn,metrics(tot.loc[a:b],252,rf)," BH",metrics(totbh.loc[a:b],252,rf))
print("turnover/yr (portfolio, one-way sum):", round(turns.loc["2006-06-01":].sum()/(len(turns.loc["2006-06-01":])/252),1))
# Sensitivity SMA window 150/210/252 for DBC+GLD to show non-cherry-picking
for n in (126,168,210,252):
    tot=0
    for t in tk:
        c,o,r=D[t]; c=c.reindex(idx); r=r.reindex(idx)
        pos=(c>c.rolling(n).mean()).astype(float).shift(1).fillna(0)
        ret,turn=run_pos(pos,r,0.0010); ret=ret+(1-pos)*rf; tot=tot+0.5*ret
    print("SMA",n,metrics(tot.loc["2006-06-01":"2026-10-08"],252,rf))
