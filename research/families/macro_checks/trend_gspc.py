# UNGETESTET - nur Plausibilitaetscheck fuer research/families/macro.md (2026-10-12). Vor Nutzung im Quant-Lab neu implementieren + Tests (Regel 2).
# Binaere Trendregel auf US-Aktien/Cash. Signal aus S&P-500-PREISINDEX ^GSPC (Monatsende-Schluss), Renditen aus French (Mkt-RF + RF, Gesamtmarkt, taeglich).
# Ausfuehrung: Signal am Schluss des letzten Handelstags t eines Monats, Handel zum Schluss t+1, neue Position verdient ab t+2. Kosten 10 bp pro vollstaendigem Wechsel.
import numpy as np, pandas as pd, yfinance as yf, warnings
warnings.filterwarnings("ignore")
ROOT = r"C:\Users\spide\Desktop\Projekte\Quant-Lab"
COST = 0.0010
f = pd.read_parquet(ROOT + r"\data_cache\french_F-F_Research_Data_Factors_daily.parquet")
f.index = pd.to_datetime(f.index)
r = (f["Mkt-RF"] + f["RF"]).astype(float); rf = f["RF"].astype(float)
d = yf.download("^GSPC", period="max", auto_adjust=False, progress=False, threads=False)
if isinstance(d.columns, pd.MultiIndex):
    d.columns = d.columns.get_level_values(0)
g = d["Close"].dropna()
g = g.reindex(r.index).ffill()
s = pd.Series(r.index, index=r.index)
me = pd.DatetimeIndex(s.groupby([s.index.year, s.index.month]).last().values)
pm = g.loc[me]
sig = {}
sig["SMA10"] = (pm > pm.rolling(10).mean()).astype(float).where(pm.rolling(10).mean().notna())
sig["MA(1,12)"] = (pm > pm.rolling(12).mean()).astype(float).where(pm.rolling(12).mean().notna())
sig["MA(2,12)"] = (pm.rolling(2).mean() >= pm.rolling(12).mean()).astype(float).where(pm.rolling(12).mean().notna())
sig["MOM12"] = (pm > pm.shift(12)).astype(float).where(pm.shift(12).notna())

def run(sg):
    sg = sg.dropna(); W = {}
    for m, v in sg.items():
        i = r.index.get_indexer([m])[0]
        if i + 1 >= len(r): continue
        W[r.index[i + 1]] = v
    W = pd.Series(W)
    pos = W.reindex(r.index).ffill().shift(1)
    first = W.index[0]; pos = pos.loc[first:]
    gross = pos * r.loc[first:] + (1 - pos) * rf.loc[first:]
    dw = W.diff().abs().fillna(0.0)
    c = pd.Series(0.0, index=r.index); c.loc[dw.index] = dw * COST
    return gross - c.loc[first:], pos, W

def stats(x, label, pos=None):
    x = x.dropna(); n = len(x); ex = x - rf.reindex(x.index); eq = (1 + x).cumprod()
    d_ = dict(label=label, cagr=round(((1 + x).prod() ** (252 / n) - 1) * 100, 2), vol=round(x.std() * np.sqrt(252) * 100, 1),
              sharpe=round(ex.mean() / ex.std() * np.sqrt(252), 2), maxdd=round((eq / eq.cummax() - 1).min() * 100, 1))
    if pos is not None: d_["inmkt%"] = round(pos.loc[x.index].mean() * 100, 0)
    return d_

runs = {k: run(v) for k, v in sig.items()}
start = max(v[0].index[0] for v in runs.values()); print("gemeinsamer Start", start.date())
rows = []
for a, b in [("1930-01-01", "2026-12-31"), ("1930-01-01", "1969-12-31"), ("1970-01-01", "1999-12-31"), ("2000-01-01", "2026-12-31"), ("2013-01-01", "2026-12-31")]:
    a = max(pd.Timestamp(a), start)
    rows.append(stats(r.loc[a:b], f"BH {a.year}-{b[:4]}"))
    for k, (net, pos, W) in runs.items():
        rows.append(stats(net.loc[a:b], f"{k} {a.year}-{b[:4]}", pos))
pd.set_option("display.width", 200)
print(pd.DataFrame(rows).to_string(index=False))
for k, (net, pos, W) in runs.items():
    yrs = (r.index[-1] - W.index[0]).days / 365.25
    print(k, "Wechsel/Jahr", round((W.diff().abs() > 0).sum() / yrs, 2))
