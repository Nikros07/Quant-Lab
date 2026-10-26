import yfinance as yf, pandas as pd, sys
tick = ["BTC-USD","ETH-USD","GC=F","GLD","SLV","DBC","DBA","DBB","USO","UNG","CPER","PPLT","PALL","IAU","BIL","SHY","XRP-USD","LTC-USD","DOGE-USD","BCH-USD","ADA-USD","XLM-USD","BNB-USD","LINK-USD","SPY","BITO","IBIT","FBTC","GBTC","BTC=F","ETH=F","COMT","PDBC","GSG"]
out = {}
for t in tick:
    try:
        d = yf.download(t, start="2000-01-01", auto_adjust=True, progress=False)
        if isinstance(d.columns, pd.MultiIndex):
            d.columns = d.columns.get_level_values(0)
        if len(d):
            d.to_csv(f"px_{t.replace('=','_')}.csv")
            print(t, d.index[0].date(), d.index[-1].date(), len(d))
        else:
            print(t, "EMPTY")
    except Exception as e:
        print(t, "ERR", e)
