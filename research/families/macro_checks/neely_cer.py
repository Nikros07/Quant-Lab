# UNGETESTET - nur Plausibilitaetscheck fuer research/families/macro.md (2026-10-11). Vor Nutzung im Quant-Lab neu implementieren + Tests (Regel 2).
# Nachbau der Neely/Rapach/Tu/Zhou-Konstruktion (nur Preis-Indikatoren, ohne Volumen) mit French-Marktrenditen statt S&P 500.
# Spezifikation aus dem abgerufenen St.-Louis-Fed-WP 2010-008: rekursive OLS-Regression r_{t+1} = a + b*S_t, Schaetzstart 1951-01,
# OOS ab 1966-01, Varianz = 60-Monats-Fenster, gamma = 5, w in [0, 1.5], Kosten 50 bp pro Umschichtung (Paper) und 10 bp (Variante).
import numpy as np, pandas as pd
ROOT = r"C:\Users\spide\Desktop\Projekte\Quant-Lab"
f = pd.read_parquet(ROOT + r"\data_cache\french_F-F_Research_Data_Factors_daily.parquet")
f.index = pd.to_datetime(f.index)
r = (f["Mkt-RF"] + f["RF"]).astype(float); rf = f["RF"].astype(float)
ym = r.index.to_period("M")
ret_m = (1 + r).groupby(ym).prod() - 1
rf_m = (1 + rf).groupby(ym).prod() - 1
ex_m = ret_m - rf_m
P = (1 + ret_m).cumprod()  # Monatsend-Index (Total Return)

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
start_est = pd.Period("1951-01", "M"); oos_start = pd.Period("1966-01", "M")
# Forecast fuer Monat t+1 wird am Ende von Monat t gebildet; Regression nutzt Paare (S_k, ex_{k+1}) mit k+1 <= t
fc = {c: pd.Series(np.nan, index=idx) for c in S.columns}; ha = pd.Series(np.nan, index=idx)
for i in range(len(idx) - 1):
    t = idx[i]
    if t < pd.Period("1965-12", "M"):
        continue
    tn = idx[i + 1]  # Zielmonat
    # Paare k = start..t-1: S_k -> ex_{k+1}
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
var60 = ex_m.rolling(60).var(ddof=1).shift(0)  # Info bis t, gilt fuer Zielmonat t+1 -> unten per shift(1) auf Zielmonat gelegt
var_t = var60.shift(1)

def evaluate(fcst, label, a, b, cost):
    sel = (idx >= pd.Period(a, "M")) & (idx <= pd.Period(b, "M"))
    y = ex_m[sel]
    e_m = (y - fcst[sel]); e_h = (y - ha[sel])
    ok = e_m.notna() & e_h.notna()
    r2 = 1 - (e_m[ok] ** 2).sum() / (e_h[ok] ** 2).sum()
    def port(fc_):
        w = (fc_ / (GAMMA * var_t)).clip(0, WMAX)
        return w
    w = port(fcst)[sel][ok]; wh = port(ha)[sel][ok]
    out = {}
    for nm, ww in (("model", w), ("HA", wh)):
        rp = ww * y[ok] + rf_m[sel][ok]
        to = ww.diff().abs().fillna(0)
        rp_net = rp - cost * to
        cer = rp_net.mean() - GAMMA / 2 * rp_net.var(ddof=1)
        sh = (rp_net - rf_m[sel][ok]).mean() / (rp_net - rf_m[sel][ok]).std(ddof=1)
        out[nm] = (cer, sh, to.mean(), ww.mean(), rp_net)
    gain = (out["model"][0] - out["HA"][0]) * 1200
    bh = y[ok] + rf_m[sel][ok]
    bh_sh = y[ok].mean() / y[ok].std(ddof=1)
    # annualisierte Rendite/Vol des Modellportfolios
    rp = out["model"][4]; eq = (1 + rp).cumprod()
    cagr = eq.iloc[-1] ** (12 / len(rp)) - 1; mdd = (eq / eq.cummax() - 1).min()
    return dict(label=label, per=f"{a[:4]}-{b[:4]}", cost_bp=int(cost * 1e4), R2OS_pct=round(r2 * 100, 2), CERgain_pct_pa=round(gain, 2),
                shMonthly=round(out["model"][1], 3), shHA=round(out["HA"][1], 3), shBH=round(bh_sh, 3), meanW=round(out["model"][3], 2),
                relTO=round(out["model"][2] / out["HA"][2], 2) if out["HA"][2] > 0 else np.nan, cagr=round(cagr * 100, 2), mdd=round(mdd * 100, 1), nobs=int(ok.sum()))

rows = []
for c in ["MA(1,12)", "MA(2,12)", "MOM(12)", "MA(1,9)", "COMB8"]:
    for (a, b) in (("1966-01", "2011-12"), ("2012-01", "2026-08"), ("1966-01", "2026-08")):
        for cost in (0.005, 0.001):
            rows.append(evaluate(fc[c], c, a, b, cost))
df = pd.DataFrame(rows)
pd.set_option("display.width", 220)
print(df.to_string(index=False))
