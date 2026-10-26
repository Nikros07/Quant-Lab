# UNGETESTET - nur Plausibilitaetscheck fuer research/families/macro.md (2026-10-12). Vor Nutzung im Quant-Lab neu implementieren + Tests (Regel 2).
# Variante von neely_cer.py: Signale wie im Paper aus dem S&P-500-PREISINDEX (^GSPC, ohne Dividenden), Zielrenditen aus French (Mkt-RF + RF, Gesamtmarkt).
# Spezifikation (Neely/Rapach/Tu/Zhou, St.-Louis-Fed-WP 2010-008H): S=1 wenn MA(s) >= MA(l) auf Monatsschluessen; rekursive OLS r_{t+1}=a+b*S_t;
# Schaetzstart 1951-01, OOS ab 1966-01; Varianz = 60-Monats-Fenster; gamma=5; w in [0,1.5]; Kosten 50 bp (Paper) bzw. 10 bp pro Umschichtung.
import numpy as np, pandas as pd, yfinance as yf, warnings
warnings.filterwarnings("ignore")
ROOT = r"C:\Users\spide\Desktop\Projekte\Quant-Lab"
f = pd.read_parquet(ROOT + r"\data_cache\french_F-F_Research_Data_Factors_daily.parquet")
f.index = pd.to_datetime(f.index)
r = (f["Mkt-RF"] + f["RF"]).astype(float); rf = f["RF"].astype(float)
ym = r.index.to_period("M")
ret_m = (1 + r).groupby(ym).prod() - 1
rf_m = (1 + rf).groupby(ym).prod() - 1
ex_m = ret_m - rf_m
print("French Monate:", ex_m.index[0], ex_m.index[-1])

g = yf.download("^GSPC", period="max", auto_adjust=False, progress=False, threads=False)
if isinstance(g.columns, pd.MultiIndex):
    g.columns = g.columns.get_level_values(0)
gc = g["Close"].dropna()
print("GSPC Start/Ende:", gc.index[0].date(), gc.index[-1].date())
P = gc.groupby(gc.index.to_period("M")).last()
P = P.reindex(ex_m.index)

def ma(x, n): return x.rolling(n).mean()
S = {}
for s in (1, 2, 3):
    for l in (9, 12):
        S[f"MA({s},{l})"] = (ma(P, s) >= ma(P, l)).astype(float).where(ma(P, l).notna())
for m in (9, 12):
    S[f"MOM({m})"] = (P >= P.shift(m)).astype(float).where(P.shift(m).notna())
S = pd.DataFrame(S)

GAMMA, WMAX = 5.0, 1.5
idx = ex_m.index
start_est = pd.Period("1951-01", "M")
fc = {c: pd.Series(np.nan, index=idx) for c in S.columns}; ha = pd.Series(np.nan, index=idx)
for i in range(len(idx) - 1):
    t = idx[i]
    if t < pd.Period("1965-12", "M"):
        continue
    tn = idx[i + 1]
    ks = [k for k in idx if start_est <= k < t]
    y = ex_m.shift(-1).loc[ks]
    ha.loc[tn] = ex_m.loc[start_est:t].mean()
    for c in S.columns:
        x = S[c].loc[ks]
        ok = x.notna() & y.notna()
        if ok.sum() < 60 or x[ok].nunique() < 2:
            continue
        b = np.cov(x[ok], y[ok], ddof=1)[0, 1] / np.var(x[ok], ddof=1)
        a = y[ok].mean() - b * x[ok].mean()
        fc[c].loc[tn] = a + b * S[c].loc[t]
fc = pd.DataFrame(fc); fc["COMB8"] = fc.mean(axis=1, skipna=False)
var_t = ex_m.rolling(60).var(ddof=1).shift(1)

def evaluate(fcst, label, a, b, cost):
    sel = (idx >= pd.Period(a, "M")) & (idx <= pd.Period(b, "M"))
    y = ex_m[sel]
    e_m = (y - fcst[sel]); e_h = (y - ha[sel])
    ok = e_m.notna() & e_h.notna()
    r2 = 1 - (e_m[ok] ** 2).sum() / (e_h[ok] ** 2).sum()
    out = {}
    for nm, fcx in (("model", fcst), ("HA", ha)):
        w = (fcx / (GAMMA * var_t)).clip(0, WMAX)[sel][ok]
        rp = w * y[ok] + rf_m[sel][ok]
        to = w.diff().abs().fillna(0)
        rp_net = rp - cost * to
        cer = rp_net.mean() - GAMMA / 2 * rp_net.var(ddof=1)
        shp = (rp_net - rf_m[sel][ok]).mean() / (rp_net - rf_m[sel][ok]).std(ddof=1)
        out[nm] = (cer, shp, to.mean(), w.mean(), rp_net)
    gain = (out["model"][0] - out["HA"][0]) * 1200
    bh_sh = y[ok].mean() / y[ok].std(ddof=1)
    eq = (1 + out["model"][4]).cumprod(); cagr = eq.iloc[-1] ** (12 / len(eq)) - 1; mdd = (eq / eq.cummax() - 1).min()
    eqb = (1 + y[ok] + rf_m[sel][ok]).cumprod(); cagr_b = eqb.iloc[-1] ** (12 / len(eqb)) - 1; mdd_b = (eqb / eqb.cummax() - 1).min()
    return dict(label=label, per=f"{a[:4]}-{b[:4]}", cost_bp=int(cost * 1e4), R2OS_pct=round(r2 * 100, 2), CERgain_pct_pa=round(gain, 2),
                shMod=round(out["model"][1], 3), shHA=round(out["HA"][1], 3), shBH=round(bh_sh, 3), meanW=round(out["model"][3], 2),
                relTO=round(out["model"][2] / out["HA"][2], 2), cagr=round(cagr * 100, 2), mdd=round(mdd * 100, 1),
                cagrBH=round(cagr_b * 100, 2), mddBH=round(mdd_b * 100, 1), nobs=int(ok.sum()))

rows = []
for c in ["MA(1,12)", "MA(2,12)", "MOM(12)", "MA(1,9)", "COMB8"]:
    for (a, b) in (("1966-01", "2011-12"), ("2012-01", "2026-12"), ("1966-01", "2026-12")):
        for cost in (0.005, 0.001):
            rows.append(evaluate(fc[c], c, a, b, cost))
df = pd.DataFrame(rows)
pd.set_option("display.width", 250)
print(df.to_string(index=False))
