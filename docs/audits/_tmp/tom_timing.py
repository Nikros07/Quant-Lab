import sys, time; sys.path.insert(0, ".")
import pandas as pd
from qlab.data import load_ticker
from strategies import tom_spy_m2_p3_etf as etf
t=time.time()
spy = load_ticker("SPY", start="1993-01-01", max_age_days=1e9).loc[:"2022-12-31"]
print("load", round(time.time()-t,2), len(spy), flush=True)
ep = etf.build_panel(spy)
t=time.time(); w = etf.weights(ep); print("weights full", round(time.time()-t,3), flush=True)
t=time.time(); w = etf.weights(ep.truncate("2000-03-15")); print("weights trunc", round(time.time()-t,3), flush=True)
