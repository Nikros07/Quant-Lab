from common import *
pd.set_option("display.width",200)
f=pd.read_csv("fund_BTCUSDT.csv",index_col=0,parse_dates=True).iloc[:,0]
f=f.groupby(f.index.floor("h")).sum()   # one entry per funding time
irx=load("^IRX")["Close"].reindex(f.index.floor("D")).ffill().values/100
rf8=pd.Series(irx/365*(1/3),index=f.index)  # per 8h
W=90   # 30 days of 8h
trail=f.rolling(W).mean()*3*365   # annualised trailing funding
def run(thr, cost_toggle=0.0030):
    on=(trail.shift(1)>(pd.Series(irx,index=f.index)+thr)).astype(float)   # decided on info before the funding stamp
    ret=on*f+(1-on)*rf8 - on.diff().abs().fillna(0)*cost_toggle/2   # cost_toggle = round trip charged half at entry, half at exit
    return ret,on
rows=[]
for name,(ret,on) in {"always on":(f.copy(),pd.Series(1.0,index=f.index)),"thr +0%":run(0.0),"thr +2%":run(0.02),"thr +5%":run(0.05)}.items():
    if name=="always on":
        ret=f-on.diff().abs().fillna(0)*0.0015
    y=ret.groupby(ret.index.year).sum()
    rows.append(pd.Series(y.round(4),name=name))
rows.append(pd.Series((pd.Series(irx/365/3,index=f.index)).groupby(f.index.year).sum().round(4),name="T-bill"))
print(pd.DataFrame(rows).T.to_string())
