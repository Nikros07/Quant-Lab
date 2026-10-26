from common import *
d=load("BTC-USD").dropna()
c=d["Close"]; o=d["Open"]
r_oo=(o.shift(-1)/o-1)  # earned from open d to open d+1
cost=0.0020  # 20 bp per one-way
irx=load("^IRX")["Close"].reindex(d.index).ffill()/100/365
res={}
def sma_sig(n): return (c>c.rolling(n).mean()).astype(float)
sigs={"BH":pd.Series(1.0,index=c.index)}
for n in (50,100,200): sigs[f"SMA{n}"]=sma_sig(n)
sigs["ENS(20,50,100,200)"]=sum(sma_sig(n) for n in (20,50,100,200))/4
# TSMOM: sign of past 90d return
sigs["TSMOM90"]=((c/c.shift(90)-1)>0).astype(float)
# Donchian ensemble: 20,50,100,200 day breakout, exit at 0.5N low (stateful)
def donch(N):
    hi=c.shift(1).rolling(N).max(); lo=c.shift(1).rolling(N//2).min()
    s=pd.Series(0.0,index=c.index); st=0
    for i,(x,h,l) in enumerate(zip(c.values,hi.values,lo.values)):
        if st==0 and x>h: st=1
        elif st==1 and x<l: st=0
        s.iloc[i]=st
    return s
sigs["DONCH_ENS(20,50,100,200)"]=sum(donch(N) for N in (20,50,100,200))/4
periods={"ALL (2015-12..)":("2015-09-01","2026-10-11"),"2015-2019":("2015-09-01","2019-12-31"),"2020-2022":("2020-01-01","2022-12-31"),"2023-2026":("2023-01-01","2026-10-11")}
rows=[]
for k,s in sigs.items():
    pos=s.shift(1)  # signal at close t-1 -> trade at open t
    pos=pos.where(pos.index>=pd.Timestamp("2015-09-01"))
    for cst,lab in ((0.0,"gross"),(cost,"net20bp")):
        ret,turn=run_pos(pos.fillna(0),r_oo,cst)
        # in cash earn T-bill when not invested
        ret=ret+(1-pos.fillna(0))*irx
        for pn,(a,b) in periods.items():
            m=metrics(ret.loc[a:b],365,irx)
            tpy=turn.loc[a:b].sum()/ (len(turn.loc[a:b])/365)
            rows.append(dict(strat=k,cost=lab,period=pn,**m,turn_per_yr=round(tpy,1)))
df=pd.DataFrame(rows)
pd.set_option("display.width",200); pd.set_option("display.max_rows",500)
print(df[df.cost=="net20bp"].pivot(index="strat",columns="period",values="Sharpe").round(2))
print(df[df.cost=="net20bp"].pivot(index="strat",columns="period",values="CAGR"))
print(df[df.cost=="net20bp"].pivot(index="strat",columns="period",values="MaxDD"))
print(df[(df.period=="ALL (2015-12..)")][["strat","cost","CAGR","Vol","Sharpe","MaxDD","turn_per_yr"]].to_string())
