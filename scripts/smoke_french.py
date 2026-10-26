import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from qlab.data import french, shiller, risk_free_daily
import pandas as pd

for name, kw in [("F-F_Research_Data_Factors", dict(daily=True)), ("F-F_Research_Data_Factors", {}),
                 ("F-F_Research_Data_5_Factors_2x3", {}), ("F-F_Research_Data_5_Factors_2x3", dict(daily=True)),
                 ("F-F_Momentum_Factor", dict(daily=True)), ("10_Portfolios_Prior_12_2_Daily", {}),
                 ("10_Portfolios_Prior_12_2_Daily", dict(table=1)), ("Portfolios_Formed_on_BETA", {}),
                 ("49_Industry_Portfolios", dict(daily=True)), ("17_Industry_Portfolios", {})]:
    try:
        df = french(name, **kw)
        print(f"OK  {name} {kw}: {df.shape} {df.index.min().date()}..{df.index.max().date()} cols={list(df.columns)[:6]}")
    except Exception as e:
        print(f"ERR {name} {kw}: {str(e)[:100]}")
try:
    s = shiller()
    print("Shiller:", s.shape, s.index.min().date(), s.index.max().date(), list(s.columns))
    print(s.tail(2).to_string())
except Exception as e:
    print("Shiller ERR:", str(e)[:150])
