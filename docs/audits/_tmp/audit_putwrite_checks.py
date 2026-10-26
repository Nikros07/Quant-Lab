import sys
sys.path.insert(0, "C:/Users/spide/Desktop/Projekte/Quant-Lab")
import numpy as np, pandas as pd
from qlab.engine import CostModel, run_backtest
from qlab.calendar import month_end_flags
from strategies import putwrite_vrp_index as S
D = "C:/Users/spide/Desktop/Projekte/Quant-Lab/data_cache/"
put = pd.read_parquet(D + "px__idx_PUT.parquet")["Close"]
spy = pd.read_parquet(D + "px_SPY.parquet")["Close"]
rf_df = pd.read_parquet(D + "french_F-F_Research_Data_Factors_daily.parquet")
print("rf cols", list(rf_df.columns)[:5], rf_df["RF"].head(2).tolist() if "RF" in rf_df else "")
rf = rf_df["RF"]
rf = rf / 100.0 if rf.abs().median() > 0.1 else rf
ISEND = pd.Timestamp("2022-12-31")
put_is = put[put.index <= ISEND]; spy_is = spy[spy.index <= ISEND]; rf_is = rf[rf.index <= ISEND]
P = S.build_panel(put_is, spy_is, rf_is)

# 1) Anomalie 2020: Sharpe mit und ohne die beiden Tage (2-Tage-Rendite zusammengefasst)
lvl = P.close["PUT_C050"]
r = lvl.pct_change().dropna()
def sh(x): return float(x.mean() / x.std() * np.sqrt(252))
rr = r.copy()
i1, i2 = pd.Timestamp("2020-03-13"), pd.Timestamp("2020-03-16")
print("raw sharpe(no rf) full", round(sh(rr), 4))
# replace two anomalous days by combined return on 2nd day, first day 0
comb = (1 + rr.loc[i1]) * (1 + rr.loc[i2]) - 1
rr2 = rr.drop(i1).copy(); rr2.loc[i2] = comb
print("sharpe with 2020 days merged", round(sh(rr2), 4), "comb ret", round(comb, 4))

# 2) Handrechnung synthetisch (Testpanel, seed 3, N=300)
rng = np.random.default_rng(3)
n = 300
idx = pd.bdate_range("1996-08-02", periods=n)
spy_r = 0.0004 + 0.010 * rng.standard_normal(n)
put_r = 0.0002 + 0.6 * spy_r + 0.003 * rng.standard_normal(n)
pl = pd.Series(100 * np.cumprod(1 + put_r), index=idx)
sl = pd.Series(40 * np.cumprod(1 + spy_r), index=idx)
fr = pd.Series(0.00015, index=pd.bdate_range(idx[0] - pd.Timedelta(days=400), idx[-1] + pd.Timedelta(days=30)))
PP = S.build_panel(pl, sl, fr)
w = S.weights(PP, cost_pp=0.5)
print("HAND weights index0", w.index[0] == idx[0], w.iloc[0, 0])
g = pl.pct_change().iloc[1:] - 0.005 / 252
lv = 100 * (1 + g).cumprod()
lv = pd.concat([pd.Series([100.0], index=[idx[0]]), lv])
print("HAND level day1 expected", round(lv.iloc[1], 6), "module", round(PP.close["PUT_C050"].iloc[1], 6))
res = run_backtest(PP, w, cost=CostModel(default_bps=0.0), rf=pd.Series(0.0, index=idx))
exp_nav = (lv / lv.iloc[1]).iloc[1:].to_numpy()
print("HAND nav max abs dev", float(np.max(np.abs(res.nav.iloc[1:].to_numpy() - exp_nav))))
print("HAND nav[5] expected", round(exp_nav[4], 8), "module", round(res.nav.iloc[5], 8))

# 3) Beta-Mix: eigene Referenz am letzten Monatsende der IS-Periode, mit Kalender-Monatsende
me = P.close.index[month_end_flags(P.close.index).to_numpy()]
bw = S.beta_matched_weights(P)
last = bw.index[-1]
mm = P.close.loc[me[me <= last]]
rr_m = mm.pct_change().dropna()
y = (rr_m["PUT_C050"] - rr_m["RF"]).to_numpy(); x = (rr_m["SPY"] - rr_m["RF"]).to_numpy()
b = np.polyfit(x, y, 1)[0]
print("BETA last", last.date(), "module", round(float(bw["SPY"].iloc[-1]), 6), "own", round(float(np.clip(b, 0, 1)), 6))

# 4) Beta-Mix als Vergleich: Sharpe und Alpha-t (monatlich, Ueberschuss ueber Beta-Mix)
Pm = P.close.loc[me]
rm = Pm.pct_change().dropna()
ex_put = (rm["PUT_C050"] - rm["RF"]).to_numpy()
ex_spy = (rm["SPY"] - rm["RF"]).to_numpy()
X = np.column_stack([np.ones(len(ex_spy)), ex_spy])
coef, *_ = np.linalg.lstsq(X, ex_put, rcond=None)
res_ = ex_put - X @ coef
s2 = res_ @ res_ / (len(ex_put) - 2)
cov = s2 * np.linalg.inv(X.T @ X)
print("ALPHA monthly", round(coef[0], 6), "ann", round(coef[0] * 12, 4), "t", round(coef[0] / np.sqrt(cov[0, 0]), 3), "n", len(ex_put))
print("BETA-OLS (full IS, monthly)", round(coef[1], 4))
