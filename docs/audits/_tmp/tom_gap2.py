import sys; sys.path.insert(0, ".")
import pandas as pd, numpy as np
from qlab.calendar import NYSE_BDAY
from qlab.data import french, load_ticker
from strategies import tom_spy_m2_p3 as main, tom_spy_m2_p3_etf as etf
fdf = french("F-F_Research_Data_Factors", daily=True)
idx = fdf.index
cal = pd.date_range("1990-01-01", idx[-1], freq=NYSE_BDAY)
print("French: NYSE-Tage ohne Datenzeile ab 1990:", len(cal.difference(idx)), [str(d.date()) for d in cal.difference(idx)[:20]])
spy = load_ticker("SPY", start="1993-01-01", max_age_days=1e9)
si = spy.index
w = etf.weights(etf.build_panel(spy))
print("ETF Signale um 1994-04:")
print(w.loc["1994-04-01":"1994-05-10"])
print("Datenzeilen 1994-04-20..05-05:", [str(d.date()) for d in si[(si>="1994-04-20")&(si<="1994-05-05")]])
