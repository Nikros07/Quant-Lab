# UNGETESTET - nur Plausibilitaetscheck fuer research/families/macro.md (2026-10-11). Vor Nutzung im Quant-Lab neu implementieren + Tests (Regel 2).
# Daten: French F-F_Research_Data_Factors_daily (Cache), Yahoo ^TNX, ^IRX. Markt = Mkt-RF + RF (Total Return, US-Gesamtmarkt).
# Ausfuehrung: Signal am Schlusskurs des letzten Handelstags t eines Monats, Handel zum Schluss t+1, neue Position verdient ab t+2.
import sys, warnings
import numpy as np, pandas as pd, yfinance as yf
warnings.filterwarnings("ignore")
ROOT = r"C:\Users\spide\Desktop\Projekte\Quant-Lab"
COST = 0.0010  # 10 bps pro vollstaendigem Wechsel (einseitig)

f = pd.read_parquet(ROOT + r"\data_cache\french_F-F_Research_Data_Factors_daily.parquet")
f.index = pd.to_datetime(f.index)
r = (f["Mkt-RF"] + f["RF"]).astype(float)
rf = f["RF"].astype(float)
lvl = (1 + r).cumprod()

def dl(t):
    d = yf.download(t, period="max", auto_adjust=False, progress=False, threads=False)
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    return d["Close"].dropna()

tnx, irx = dl("^TNX"), dl("^IRX")
print("TNX", tnx.index.min().date(), "IRX", irx.index.min().date())
spr = (tnx.reindex(lvl.index).ffill() - irx.reindex(lvl.index).ffill())
spr = spr.where(lvl.index >= max(tnx.index.min(), irx.index.min()))

# Monatsende-Tage (letzter Handelstag je Kalendermonat)
s = pd.Series(lvl.index, index=lvl.index)
me = pd.DatetimeIndex(s.groupby([s.index.year, s.index.month]).last().values)
pm = lvl.loc[me]
sig = {}
sig["SMA10"] = (pm > pm.rolling(10).mean()).astype(float).where(pm.rolling(10).mean().notna())
sig["MA(1,12)"] = (pm > pm.rolling(12).mean()).astype(float).where(pm.rolling(12).mean().notna())
sig["MOM12"] = (pm > pm.shift(12)).astype(float).where(pm.shift(12).notna())
yc = spr.reindex(me)
sig["YC>0"] = (yc > 0).astype(float).where(yc.notna())
sig["SMA10&YC"] = (sig["SMA10"] * sig["YC>0"])
sig["SMA10|YC"] = ((sig["SMA10"] + sig["YC>0"]) > 0).astype(float).where(sig["SMA10"].notna() & sig["YC>0"].notna())
sig["VOTE3"] = (sig["SMA10"] + sig["MOM12"] + sig["YC>0"]) / 3.0

def run(sg):
    sg = sg.dropna()
    W = {}
    for m, v in sg.items():
        i = lvl.index.get_indexer([m])[0]
        if i + 1 >= len(lvl):
            continue
        W[lvl.index[i + 1]] = v
    W = pd.Series(W)
    pos = W.reindex(lvl.index).ffill().shift(1)
    first = W.index[0]
    pos = pos.loc[first:]
    gross = pos * r.loc[first:] + (1 - pos) * rf.loc[first:]
    dw = W.diff().abs().fillna(0.0)
    c = pd.Series(0.0, index=lvl.index)
    c.loc[dw.index] = dw * COST
    net = gross - c.loc[first:]
    return net, pos, W

def stats(x, label, pos=None):
    x = x.dropna()
    n = len(x)
    ex = x - rf.reindex(x.index)
    eq = (1 + x).cumprod()
    d = dict(label=label,
             cagr=round(((1 + x).prod() ** (252 / n) - 1) * 100, 2),
             vol=round(x.std() * np.sqrt(252) * 100, 1),
             sharpe=round(ex.mean() / ex.std() * np.sqrt(252), 2),
             maxdd=round((eq / eq.cummax() - 1).min() * 100, 1))
    if pos is not None:
        d["inmkt%"] = round(pos.loc[x.index].mean() * 100, 0)
    return d

periods = [("1962-01-01", "2026-12-31"), ("1962-01-01", "1999-12-31"), ("2000-01-01", "2026-12-31"),
           ("2007-01-01", "2026-12-31"), ("2013-01-01", "2026-12-31")]
runs = {k: run(v) for k, v in sig.items()}
start = max(v[0].index[0] for v in runs.values())
print("gemeinsamer Start", start.date())
rows = []
for a, b in periods:
    a = max(pd.Timestamp(a), start)
    rows.append(stats(r.loc[a:b], f"BH {a.year}-{b[:4]}"))
    for k, (net, pos, W) in runs.items():
        rows.append(stats(net.loc[a:b], f"{k} {a.year}-{b[:4]}", pos))
df = pd.DataFrame(rows)
pd.set_option("display.width", 200)
print(df.to_string(index=False))
for k, (net, pos, W) in runs.items():
    yrs = (lvl.index[-1] - W.index[0]).days / 365.25
    print(k, "Wechsel/Jahr", round((W.diff().abs() > 0).sum() / yrs, 2))
# Zusatz: Yield-Curve-Inversionsphasen
print("Anteil Monate YC<=0:", round((yc.dropna() <= 0).mean() * 100, 1), "%")
print("YC-Signal Monate 2022-2026 (Anteil 0):", round((yc.loc["2022-01-01":].dropna() <= 0).mean() * 100, 1), "%")
