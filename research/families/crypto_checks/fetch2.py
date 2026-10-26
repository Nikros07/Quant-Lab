import yfinance as yf, pandas as pd
for t in ["^IRX","^GSPC"]:
    d = yf.download(t, start="1999-01-01", auto_adjust=True, progress=False)
    if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
    d.to_csv(f"px_{t.replace('^','_')}.csv"); print(t, d.index[0].date(), len(d))
