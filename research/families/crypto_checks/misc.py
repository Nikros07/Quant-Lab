from common import *
import yfinance as yf
pd.set_option("display.width",200)
# ETH trend
for tkr,start in (("ETH-USD","2018-06-01"),):
    d=load(tkr).dropna(); c=d["Close"]; o=d["Open"]; r_oo=o.shift(-1)/o-1
    irx=load("^IRX")["Close"].reindex(d.index).ffill()/100/365
    sigs={"BH":pd.Series(1.0,index=c.index),"SMA50":(c>c.rolling(50).mean()).astype(float),"SMA100":(c>c.rolling(100).mean()).astype(float),"SMA200":(c>c.rolling(200).mean()).astype(float),
          "ENS":sum((c>c.rolling(n).mean()).astype(float) for n in (20,50,100,200))/4}
    rows=[]
    for k,s in sigs.items():
        pos=s.shift(1).fillna(0); ret,turn=run_pos(pos,r_oo,0.0020); ret=ret+(1-pos)*irx
        for pn,(a,b) in {"ALL":(start,"2026-10-11"),"2018-2021":(start,"2021-12-31"),"2022-2026":("2022-01-01","2026-10-11")}.items():
            rows.append(dict(strat=k,period=pn,**metrics(ret.loc[a:b],365,irx)))
    print(pd.DataFrame(rows).to_string())
# BTC+ETH 50/50 ensemble
b=load("BTC-USD").dropna(); e=load("ETH-USD").dropna()
idx=b.index.intersection(e.index)
def ens(df):
    c=df["Close"]; return sum((c>c.rolling(n).mean()).astype(float) for n in (20,50,100,200))/4
rb=(b["Open"].shift(-1)/b["Open"]-1).reindex(idx); re=(e["Open"].shift(-1)/e["Open"]-1).reindex(idx)
pb=ens(b).shift(1).reindex(idx).fillna(0); pe=ens(e).shift(1).reindex(idx).fillna(0)
irx=load("^IRX")["Close"].reindex(idx).ffill()/100/365
ret=0.5*(pb*rb+pe*re)-0.5*(pb.diff().abs().fillna(0)+pe.diff().abs().fillna(0))*0.002+ (1-0.5*(pb+pe))*irx
bh=0.5*(rb+re)
for pn,(a,b_) in {"ALL":("2018-06-01","2026-10-11"),"2022-2026":("2022-01-01","2026-10-11")}.items():
    print("BTC+ETH ENS 50/50",pn,metrics(ret.loc[a:b_],365,irx)); print("BTC+ETH BH 50/50 (daily rebal)",pn,metrics(bh.loc[a:b_],365,irx))
print("latest IRX:", load("^IRX")["Close"].iloc[-1], load("^IRX").index[-1])
# ETP tickers
for t in ["BTCE.DE","VBTC.DE","ZBTC.DE","ABTC.DE","BTC1.SW","ABTC.SW","CETH.DE","VETH.DE","AETH.SW","EBTC.DE"]:
    try:
        d=yf.download(t,start="2015-01-01",auto_adjust=True,progress=False)
        print(t, (d.index[0].date(), len(d)) if len(d) else "EMPTY")
    except Exception as ex: print(t,"ERR")
