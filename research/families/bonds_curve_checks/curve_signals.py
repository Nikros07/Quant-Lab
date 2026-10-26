# UNGETESTET - nur Plausibilitaetscheck fuer research/families/gap_bonds_duration_curve_carry_mom_value.md (2026-10-12).
# Vor Nutzung im Quant-Lab neu implementieren + Tests (Regel 2). Nicht zur Strategiewahl verwenden (Regel 3).
# Daten: Yahoo ^TNX (10J-Par-Rendite, ab 1962), ^IRX (13-Wochen-Bill, ab 1960), French Mkt-RF+RF daily (Cache) als Aktien-Proxy.
# Synthetische 10J-Rendite: R = y(t-1)/252 - Dmod(y(t-1))*(y(t)-y(t-1)), Dmod = (1-(1+y/2)^-20)/y (Par-Bond, halbjaehrlich). Kein Roll-down, keine Konvexitaet.
# Ausfuehrung: Signal am Schlusskurs des letzten Handelstags t eines Monats, Handel zum Schluss t+1, neue Position verdient ab t+2. Kosten 5 bp je Einheit Umschichtung.
# Value-Signal (Realzins) NICHT getestet: braucht Inflationserwartung (FRED EXPINF10YR / CPI), nicht im Cache.
import sys, warnings
import numpy as np, pandas as pd, yfinance as yf
warnings.filterwarnings("ignore")
ROOT = r"C:\Users\spide\Desktop\Projekte\Quant-Lab"
COST = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0005

def dl(t, cache):
    try:
        d = yf.download(t, period="max", auto_adjust=False, progress=False, threads=False)
        if isinstance(d.columns, pd.MultiIndex):
            d.columns = d.columns.get_level_values(0)
        s = d["Close"].dropna()
        if len(s) > 5000:
            return s
    except Exception as e:
        print("yf fail", t, e)
    d = pd.read_parquet(ROOT + r"\data_cache\px_" + cache + ".parquet")
    return d["Close"].dropna()

tnx, irx = dl("^TNX", "_idx_TNX"), dl("^IRX", "_idx_IRX")
tnx.index = pd.to_datetime(tnx.index).tz_localize(None); irx.index = pd.to_datetime(irx.index).tz_localize(None)
print("TNX", tnx.index.min().date(), tnx.index.max().date(), "IRX", irx.index.min().date(), irx.index.max().date())
idx = tnx.index
y = tnx / 100.0
yc = irx.reindex(idx).ffill() / 100.0
ym = y.shift(1)
D = (1 - (1 + ym / 2) ** -20) / ym
R10 = ym / 252 - D * y.diff()
Rc = yc.shift(1) / 252
ex = np.log1p(R10) - np.log1p(Rc)

f = pd.read_parquet(ROOT + r"\data_cache\french_F-F_Research_Data_Factors_daily.parquet"); f.index = pd.to_datetime(f.index)
req = np.log1p((f["Mkt-RF"] + f["RF"]).astype(float)).reindex(idx).fillna(0.0)

s = pd.Series(idx, index=idx)
me = pd.DatetimeIndex(s.groupby([s.index.year, s.index.month]).last().values)

def pct_prior(series, n=2520):
    out = {}
    v = series.values; ix = {d: i for i, d in enumerate(series.index)}
    for m in me:
        i = ix[m]
        if i < n or np.isnan(v[i]): continue
        w = v[i - n:i]
        w = w[~np.isnan(w)]
        if len(w) < n * 0.95: continue
        out[m] = (w < v[i]).mean()
    return pd.Series(out)

spread = (y - yc)
p_car = pct_prior(spread)
e21, e252 = ex.ewm(span=21, adjust=False).mean(), ex.ewm(span=252, adjust=False).mean()
mom_ls = pd.Series(np.where((e21 > 0) & (e252 > 0), 1, np.where((e21 < 0) & (e252 < 0), -1, 0)), index=idx).reindex(me)
mom_ls = mom_ls[(me >= idx[300])]
car_ls = pd.Series(np.where(p_car > 1/3, 1, -1), index=p_car.index)
eq63 = req.ewm(span=63, adjust=False).mean()
p_eq = pct_prior(eq63)
eqh_ls = pd.Series(np.where(p_eq < 0.25, 1, np.where(p_eq > 0.75, -1, 0)), index=p_eq.index)

def lo(x): return (x > 0).astype(float)
sig = {
    "CARRY_LS": car_ls, "MOM_LS": mom_ls, "EQH_LS": eqh_ls,
    "CARRY_LO": lo(car_ls), "MOM_LO": lo(mom_ls), "EQH_LO": lo(eqh_ls),
}
idx_all = car_ls.index.intersection(mom_ls.index).intersection(eqh_ls.index)
sig["COMBO2_LS"] = ((car_ls + mom_ls) / 2).reindex(car_ls.index.intersection(mom_ls.index))
sig["COMBO3_LS"] = ((car_ls + mom_ls + eqh_ls) / 3).reindex(idx_all)
sig["COMBO2_LO"] = ((lo(car_ls) + lo(mom_ls)) / 2).reindex(car_ls.index.intersection(mom_ls.index))
sig["COMBO3_LO"] = ((lo(car_ls) + lo(mom_ls) + lo(eqh_ls)) / 3).reindex(idx_all)
sig["BH10"] = pd.Series(1.0, index=car_ls.index.intersection(mom_ls.index))

def run(sg):
    sg = sg.dropna(); W = {}
    for m, v in sg.items():
        i = idx.get_indexer([m])[0]
        if i + 1 >= len(idx): continue
        W[idx[i + 1]] = v
    W = pd.Series(W)
    pos = W.reindex(idx).ffill().shift(1)
    first = W.index[0]; pos = pos.loc[first:]
    # long-only (alle LO + BH): w*R10+(1-w)*Rc ; LS: Rc + pos*(R10-Rc)  -> identisch formuliert
    gross = Rc.loc[first:] + pos * (R10.loc[first:] - Rc.loc[first:])
    dw = W.diff().abs().fillna(abs(W.iloc[0]))
    c = pd.Series(0.0, index=idx); c.loc[dw.index] = dw * COST
    return gross - c.loc[first:], pos, Rc.loc[first:]

def stats(net, pos, rc, a, b):
    x = net.loc[a:b].dropna()
    if len(x) < 250: return None
    exr = x - rc.loc[x.index]
    eq = (1 + x).cumprod()
    return dict(cagr=round(((1 + x).prod() ** (252 / len(x)) - 1) * 100, 2), vol=round(x.std() * np.sqrt(252) * 100, 1),
                sharpe=round(exr.mean() / exr.std() * np.sqrt(252), 2), maxdd=round((eq / eq.cummax() - 1).min() * 100, 1),
                inv=round(pos.loc[x.index].abs().mean() * 100), start=x.index[0].date())

runs = {k: run(v) for k, v in sig.items()}
periods = [("Voll", "1900-01-01", "2100-01-01"), ("1972-2018 (Newfound-Fenster)", "1972-01-01", "2018-12-31"),
           ("1972-1981 Zinsanstieg", "1972-01-01", "1981-12-31"), ("1982-2007", "1982-01-01", "2007-12-31"),
           ("2008-2021", "2008-01-01", "2021-12-31"), ("1972-2021 (vor 2022)", "1972-01-01", "2021-12-31"),
           ("2022-2026-10", "2022-01-01", "2026-12-31"), ("Post-Publikation 2018-11..heute", "2018-11-01", "2100-01-01"), ("2023-2026-10 (nach dem Schock)", "2023-01-01", "2100-01-01"), ("2022 allein", "2022-01-01", "2022-12-31")]
print("COST", COST)
for lab, a, b in periods:
    print("\n==", lab)
    for k, (net, pos, rc) in runs.items():
        st = stats(net, pos, rc, a, b)
        if st: print(f"{k:10s}", st)
# Kalenderjahre
print("\nKalenderjahr-Rendite % (total, inkl. Cash-Anteil)")
yrs = list(range(2013, 2027))
rows = {}
for k, (net, pos, rc) in runs.items():
    rows[k] = [round(((1 + net[net.index.year == yv]).prod() - 1) * 100, 1) if (net.index.year == yv).any() else None for yv in yrs]
print(pd.DataFrame(rows, index=yrs).T.to_string())
# Positionen Ende 2021/Mitte 2022
for k in ["CARRY_LS", "MOM_LS", "EQH_LS", "COMBO2_LO", "COMBO3_LO"]:
    pos = runs[k][1]
    print(k, "Pos Ende2021", pos.loc[:"2021-12-31"].iloc[-1], "Ende Q1-22", pos.loc[:"2022-03-31"].iloc[-1], "Ende Q2-22", pos.loc[:"2022-06-30"].iloc[-1], "Ende2022", pos.loc[:"2022-12-31"].iloc[-1])
# Umschlag (Einheiten pro Jahr) je Strategie
print("\nUmschlag |dW| pro Jahr (Vollperiode)")
for k, (net, pos, rc) in runs.items():
    dpos = pos.diff().abs().sum() / (len(pos) / 252)
    print(f"{k:10s} {dpos:.2f}")
