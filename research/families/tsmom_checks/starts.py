# UNGETESTET - nur Plausibilitaetscheck fuer research/families/tsmom.md (2026-10-11). Vor Nutzung im Quant-Lab neu implementieren + Tests (Regel 2).
import yfinance as yf, pandas as pd, warnings
warnings.filterwarnings("ignore")
tick = ["SPY","EFA","EEM","IWM","QQQ","IEF","TLT","SHY","BIL","AGG","VNQ","GLD","DBC","USO","UUP","FXE","FXY","FXB","FXA","DBMF","KMLM","CTA","^GSPC","^TNX","^IRX","^VIX","ES=F","NQ=F","ZN=F","ZB=F","GC=F","CL=F","SI=F","HG=F","ZC=F","ZW=F","6E=F","6J=F","6B=F","6A=F","6C=F","DX-Y.NYB","BTC-USD","VWO","IYR","BND","LQD","HYG","TIP","SCHP","SPLV"]
rows=[]
for t in tick:
    try:
        d = yf.download(t, period="max", auto_adjust=True, progress=False, threads=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns=d.columns.get_level_values(0)
        s = d["Close"].dropna()
        rows.append((t, s.index[0].date() if len(s) else None, s.index[-1].date() if len(s) else None, len(s)))
    except Exception as e:
        rows.append((t, "ERR", str(e)[:50], 0))
for r in rows: print(r)
