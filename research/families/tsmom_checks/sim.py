# UNGETESTET - nur Plausibilitaetscheck fuer research/families/tsmom.md (2026-10-11). Vor Nutzung im Quant-Lab neu implementieren + Tests (Regel 2).
import yfinance as yf, pandas as pd, numpy as np, warnings, sys
warnings.filterwarnings("ignore")
def dl(t):
    d = yf.download(t, period="max", auto_adjust=True, progress=False, threads=False)
    if isinstance(d.columns, pd.MultiIndex): d.columns=d.columns.get_level_values(0)
    return d["Close"].dropna()
U = ["SPY","EFA","EEM","IEF","TLT","VNQ","GLD","DBC","FXE","FXY","FXB","FXA"]
P = pd.concat({t:dl(t) for t in U+["SHY"]},axis=1)
irx = dl("^IRX")
P = P.dropna(subset=["SPY"])
rf = (irx.reindex(P.index).ffill().shift(1)/100/252).fillna(0)   # known at t-1
R = P.pct_change()
start = P[U].dropna().index[0]
print("common start", start.date(), "end", P.index[-1].date())
P=P.loc[start:]; R=R.loc[start:]; rf=rf.loc[start:]
ER = R[U].sub(rf,axis=0)
me = P.groupby([P.index.year,P.index.month]).apply(lambda x:x.index[-1]).values
me = pd.DatetimeIndex(me)
# drop last (incomplete) month if last date isn't last of month - keep, harmless
Pm = P[U].loc[me]
cumrf = (1+rf).cumprod()
cm = cumrf.loc[me]
def er_k(k):
    return Pm/Pm.shift(k)-1 - (cm/cm.shift(k)-1).values.reshape(-1,1)
def ewvol():
    return np.sqrt((ER**2).ewm(com=60, min_periods=120).mean()*261).loc[me]
VOL = ewvol()
idx = P.index
def exec_date(m):
    i = idx.get_indexer([m])[0]
    return idx[i+1] if i+1 < len(idx) else None
def build(kind, longshort=True, tvol=0.10, cap=3.0):
    W = {}
    prevN=None
    for j,m in enumerate(me):
        if m < start + pd.Timedelta(days=380): continue
        sig = pd.Series(0.0,index=U)
        if kind=="hop":
            ss=[]
            for k in (1,3,12):
                e = er_k(k).loc[m]
                s = np.sign(e) if longshort else (e>0).astype(float)
                ss.append(s)
            sig = sum(ss)/3
        elif kind=="mop":
            e = er_k(12).loc[m]; sig = np.sign(e) if longshort else (e>0).astype(float)
        elif kind=="ewm":
            sig = EWMSIG.loc[m]
            if not longshort: sig=sig.clip(lower=0)
        v = VOL.loc[m]
        ok = v.notna() & P[U].loc[m].notna()
        sig = sig[ok]; v=v[ok]; N=len(sig)
        if N==0: continue
        if kind=="mop":
            w = sig*0.40/v/N
        else:
            w = sig/v/N
            # scale to target vol using cov of last 756d excess returns
            win = ER.loc[:m, sig.index].iloc[-756:]
            if len(win)>=252:
                C = win.cov().values*261
                pv = float(np.sqrt(max(w.values@C@w.values,1e-12)))
                w = w*(tvol/pv)
            if not longshort and w.sum()>1.0: w = w/w.sum()   # unlevered long/flat
            g = w.abs().sum()
            if g>cap: w = w*cap/g
        ed = exec_date(m)
        if ed is None: continue
        W[ed] = w.reindex(U).fillna(0.0)
    W = pd.DataFrame(W).T
    return W
def ewm_signal(tau):
    ema_f = P[U].ewm(alpha=1-np.exp(-1/tau),min_periods=tau).mean()
    ema_s = P[U].ewm(alpha=1-np.exp(-1/(4*tau)),min_periods=4*tau).mean()
    st = (ema_f-ema_s).shift(1)
    # normalise by slow EW std of st (decay 16 tau)
    sd = st.ewm(alpha=1-np.exp(-1/(16*tau)),min_periods=2*tau).std()
    s = (st/sd).clip(-2,2)
    return s
def run(W, cost=0.0010, cash_other=None):
    pos = W.reindex(idx).ffill().shift(1).fillna(0.0)   # held from close of exec day -> returns next day
    gross = rf + (pos*ER).sum(axis=1)
    # turnover cost at exec dates
    dW = W.diff().abs().sum(axis=1); dW.iloc[0]=W.iloc[0].abs().sum()
    c = pd.Series(0.0,index=idx); c.loc[dW.index]=dW*cost
    net = gross - c
    first = W.index[0]
    return gross.loc[first:], net.loc[first:], dW, pos
def stats(r, rfs, label):
    r=r.dropna(); n=len(r)
    ex = r-rfs.reindex(r.index)
    ann = (1+r).prod()**(252/n)-1
    vol = r.std()*np.sqrt(252)
    sh = ex.mean()/ex.std()*np.sqrt(252)
    eq=(1+r).cumprod(); dd=(eq/eq.cummax()-1).min()
    return dict(label=label, cagr=round(ann*100,2), vol=round(vol*100,2), sharpe=round(sh,2), maxdd=round(dd*100,1))
def subp(r, rfs, name, ranges):
    out=[]
    for a,b in ranges:
        x=r.loc[a:b]
        if len(x)>200: out.append(stats(x,rfs,f"{name} {a[:4]}-{b[:4]}"))
    return out
res=[]
ranges=[("2008-01-01","2026-12-31"),("2008-01-01","2014-12-31"),("2015-01-01","2026-12-31"),("2020-01-01","2026-12-31")]
EWMSIG = ewm_signal(50)
for name,kind,ls,kw in [("HOP_LS_10vol","hop",True,{}),("HOP_LongFlat","hop",False,{}),("MOP12_LS_40vol","mop",True,{}),("MOP12_LongFlat","mop",False,{}),("EWM50-200_LS_10vol","ewm",True,{}),("EWM50-200_LongFlat","ewm",False,{})]:
    W = build(kind, longshort=ls, **kw)
    g,n,dW,pos = run(W)
    to = dW.sum()/ (len(g)/252)
    for r_ in subp(n, rf, name+" net10bp", ranges): res.append(r_)
    res.append(stats(g, rf, name+" gross full"))
    print(name, "avg gross lev", round(pos.abs().sum(axis=1).loc[g.index].mean(),2), "turnover/yr (sum|dw|)", round(to,2), flush=True)
# benchmarks
spy = R["SPY"].loc[start:]
sixty = 0.6*R["SPY"]+0.4*R["IEF"]
ew = R[U].mean(axis=1)
for nm,x in [("SPY BH",spy),("60/40 daily-rebal",sixty.loc[start:]),("EW12 BH daily-rebal",ew.loc[start:])]:
    for a,b in ranges:
        y=x.loc[a:b]; res.append(stats(y,rf,f"{nm} {a[:4]}-{b[:4]}"))
df=pd.DataFrame(res); pd.set_option("display.width",200); pd.set_option("display.max_rows",200)
print(df.to_string())
df.to_csv(sys.argv[1]+"/sim_results.csv",index=False)
