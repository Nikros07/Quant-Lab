# UNGETESTET - nur Plausibilitaetscheck fuer research/families/tsmom.md (2026-10-11). Vor Nutzung im Quant-Lab neu implementieren + Tests (Regel 2).
import yfinance as yf, pandas as pd, numpy as np, warnings
warnings.filterwarnings("ignore")
def dl(t):
    d=yf.download(t,period="max",auto_adjust=True,progress=False,threads=False)
    if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
    return d["Close"].dropna()
g=dl("^GSPC"); irx=dl("^IRX")
g=g.loc["1960-01-01":]
r=g.pct_change(); rf=(irx.reindex(g.index).ffill().shift(1)/100/252).fillna(0)
me=pd.DatetimeIndex(pd.Series(g.index,index=g.index).groupby([g.index.year,g.index.month]).last().values)
pm=g.loc[me]; sma=pm.rolling(10).mean(); sig=(pm>sma).astype(float).where(sma.notna())
W={}
for m in me:
    if pd.isna(sig.loc[m]): continue
    i=g.index.get_indexer([m])[0]
    if i+1>=len(g): continue
    W[g.index[i+1]]=sig.loc[m]
W=pd.Series(W); pos=W.reindex(g.index).ffill().shift(1); f=W.index[0]; pos=pos.loc[f:]
gr=pos*r.loc[f:]+(1-pos)*rf.loc[f:]
dw=W.diff().abs().fillna(W.iloc[0]); c=pd.Series(0.0,index=g.index); c.loc[dw.index]=dw*0.0005
net=gr-c.loc[f:]
def st(x,l):
    x=x.dropna(); n=len(x); ex=x-rf.reindex(x.index); eq=(1+x).cumprod()
    return dict(label=l,cagr=round(((1+x).prod()**(252/n)-1)*100,2),vol=round(x.std()*np.sqrt(252)*100,1),sharpe=round(ex.mean()/ex.std()*np.sqrt(252),2),maxdd=round((eq/eq.cummax()-1).min()*100,1))
out=[]
for a,b in [("1961-01-01","2026-12-31"),("1961-01-01","2012-12-31"),("2013-01-01","2026-12-31"),("2000-01-01","2012-12-31")]:
    out.append(st(net.loc[a:b],f"GSPC-price SMA10 {a[:4]}-{b[:4]}")); out.append(st(r.loc[a:b],f"GSPC-price BH {a[:4]}-{b[:4]}"))
print(pd.DataFrame(out).to_string()); print("first signal",f.date(),"switches/yr",round((W.diff().abs()>0).sum()/((g.index[-1]-f).days/365.25),2))
