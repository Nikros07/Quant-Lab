# UNGETESTET - nur Plausibilitaetscheck fuer research/families/gap_crossasset_bond_equity_leadlag_signals.md (2026-10-12). Vor Nutzung im Quant-Lab neu implementieren + Tests (Regel 2).
import io, warnings, requests, pandas as pd
import yfinance as yf
warnings.filterwarnings("ignore")
tick = ["SPY","IEF","TLT","SHY","EWJ","EWG","EWU","EWQ","EWC","EWA","EWH","EWS","EWP","EWI","EWN","EWD","EWL","EWK","EWO","EWM","EWT","EWY","EWZ","EWW",
        "BWX","IGOV","VFINX","VUSTX","VFITX","^GSPC","^N225","^FTSE","^GDAXI","^FCHI","^HSI","^AXJO","^GSPTSE","^SSMI","^AEX","^IBEX","^BVSP","^KS11","^TWII","^STI","^OMX"]
for t in tick:
    try:
        d = yf.Ticker(t).history(period="max", auto_adjust=True, actions=False)
        s = d["Close"].dropna()
        print(t, s.index[0].date() if len(s) else None, s.index[-1].date() if len(s) else None, len(s), flush=True)
    except Exception as e:
        print(t, "ERR", str(e)[:60], flush=True)
ids = ["GS10","GS5","IRLTLT01DEM156N","IRLTLT01JPM156N","IRLTLT01GBM156N","IRLTLT01CAM156N","IRLTLT01AUM156N","IRLTLT01FRM156N","IRLTLT01ITM156N",
       "IRLTLT01CHM156N","IRLTLT01SEM156N","IRLTLT01NLM156N","IRLTLT01ESM156N","IRLTLT01KRM156N","IRLTLT01USM156N","USREC"]
for i in ids:
    try:
        r = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={i}", timeout=30, headers={"User-Agent":"Mozilla/5.0"})
        df = pd.read_csv(io.StringIO(r.text)); df.columns=["date","v"]; df = df[pd.to_numeric(df.v, errors="coerce").notna()]
        print("FRED", i, df.date.iloc[0], df.date.iloc[-1], len(df), flush=True)
    except Exception as e:
        print("FRED", i, "ERR", str(e)[:60], flush=True)
