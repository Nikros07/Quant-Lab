from common import *
pd.set_option("display.width",200)
irx_s=load("^IRX")["Close"]
def daily_test(tkr, start, label, cost=0.0005, smaN=(210,), tsm=(252,)):
    d=load(tkr).dropna(); c=d["Close"]; o=d["Open"]
    r_oo=(o.shift(-1)/o-1)
    rf=irx_s.reindex(d.index).ffill()/100/252
    out=[]
    sigs={"BH":pd.Series(1.0,index=c.index)}
    for n in smaN: sigs[f"SMA{n}"]=(c>c.rolling(n).mean()).astype(float)
    for n in tsm: sigs[f"TSMOM{n}"]=((c/c.shift(n)-1)>0).astype(float)
    sigs["ENS(100,150,210)"]=sum((c>c.rolling(n).mean()).astype(float) for n in (100,150,210))/3
    for k,s in sigs.items():
        pos=s.shift(1).fillna(0)
        ret,turn=run_pos(pos,r_oo,cost); ret=ret+(1-pos)*rf
        for pn,(a,b) in {"ALL":(start,"2026-10-08"),"first half":(start,"2015-12-31"),"2016-2026":("2016-01-01","2026-10-08")}.items():
            m=metrics(ret.loc[a:b],252,rf)
            out.append(dict(tkr=label,strat=k,period=pn,**m,turn=round(turn.loc[a:b].sum()/(len(turn.loc[a:b])/252),1)))
    return pd.DataFrame(out)
res=pd.concat([daily_test("GLD","2005-01-01","GLD"),daily_test("GC=F","2000-10-01","GC=F"),daily_test("DBC","2006-04-01","DBC"),daily_test("GSG","2006-09-01","GSG")])
print(res.to_string())
