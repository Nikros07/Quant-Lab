# UNGETESTET - nur Plausibilitaetscheck fuer research/families/macro.md (2026-10-12). Vor Nutzung im Quant-Lab neu implementieren + Tests (Regel 2).
# Grober Nachbau der Sum-of-the-parts-Prognose (Ferreira/Santa-Clara, NBER WP 14571, Dez 2008): E(r) = log(1+D/P) + 20-Jahres-Mittel des
# Gewinnwachstums, Multiple-Wachstum = 0 (Variante "nur Dividendenrendite + Gewinnwachstum"). Keine Shrinkage-/Regressionsteile.
# Daten: Shiller ie_data.xls (Yale, Stand Sep 2023, Datei vorher in einen eigenen Ordner geladen), Zielrenditen aus French (Mkt-RF + RF, Gesamtmarkt).
# Abweichungen zum Paper: Zielrendite Gesamtmarkt statt S&P 500; D und E um 3 Monate verzoegert (Shiller interpoliert/veroeffentlicht spaet).
# Aufruf: PYLIB=<ordner mit xlrd> python sop_shiller.py <pfad zu ie_data.xls>
import sys, os
sys.path.insert(0, os.environ["PYLIB"])
import numpy as np, pandas as pd, xlrd
ROOT = r"C:\Users\spide\Desktop\Projekte\Quant-Lab"
sh = xlrd.open_workbook(sys.argv[1]).sheet_by_name("Data")
rows = []
for i in range(8, sh.nrows):
    v = sh.row_values(i, 0, 5)
    if not isinstance(v[0], float):
        continue
    y = int(v[0]); m = int(round((v[0] - y) * 100))
    num = lambda x: float(x) if isinstance(x, (int, float)) else np.nan
    rows.append((pd.Period(f"{y}-{m:02d}", "M"), num(v[1]), num(v[2]), num(v[3])))
sd = pd.DataFrame(rows, columns=["per", "P", "D", "E"]).set_index("per")
print("Shiller:", sd.index[0], sd.index[-1], "| letzter Monat mit E:", sd["E"].last_valid_index(), "| mit D:", sd["D"].last_valid_index())

f = pd.read_parquet(ROOT + r"\data_cache\french_F-F_Research_Data_Factors_daily.parquet")
f.index = pd.to_datetime(f.index)
r = (f["Mkt-RF"] + f["RF"]).astype(float); rf = f["RF"].astype(float)
ym = r.index.to_period("M")
ret_m = (1 + r).groupby(ym).prod() - 1
rf_m = (1 + rf).groupby(ym).prod() - 1
ex_m = ret_m - rf_m
last = min(sd["E"].last_valid_index(), sd["D"].last_valid_index())
idx = ex_m.index[ex_m.index <= last]
ex_m = ex_m.loc[idx]; rf_m = rf_m.loc[idx]
sd = sd.reindex(idx)

LAG = 3
dp = np.log(1 + sd["D"].shift(LAG) / sd["P"])
ge20 = np.log(sd["E"].shift(LAG) / sd["E"].shift(LAG + 240)) / 20.0
exp_ann = dp + ge20
fc_sop = (exp_ann / 12.0 - rf_m).shift(1)  # Prognose am Ende von t fuer Monat t+1 (rf_m(t) als Naeherung fuer rf(t+1))
fc_dp = (dp / 12.0 - rf_m).shift(1)        # nur Dividendenrendite (Gegenprobe)
start = pd.Period("1927-01", "M")
ha = ex_m.expanding().mean().shift(1)
var_t = ex_m.expanding().var(ddof=1).shift(1)

def evaluate(fc, label, a, b, gamma, cost):
    sel = (idx >= pd.Period(a, "M")) & (idx <= pd.Period(b, "M"))
    y = ex_m[sel]
    ok = fc[sel].notna() & ha[sel].notna()
    e_m = y[ok] - fc[sel][ok]; e_h = y[ok] - ha[sel][ok]
    r2 = 1 - (e_m ** 2).sum() / (e_h ** 2).sum()
    out = {}
    for nm, fx in (("model", fc), ("HA", ha)):
        w = (fx / (gamma * var_t)).clip(0, 1.5)[sel][ok]
        rp = w * y[ok] + rf_m[sel][ok]
        to = w.diff().abs().fillna(0)
        rpn = rp - cost * to
        cer = rpn.mean() - gamma / 2 * rpn.var(ddof=1)
        shp = (rpn - rf_m[sel][ok]).mean() / (rpn - rf_m[sel][ok]).std(ddof=1) * np.sqrt(12)
        out[nm] = (cer, shp, w.mean(), to.mean(), rpn)
    eq = (1 + out["model"][4]).cumprod(); cagr = eq.iloc[-1] ** (12 / len(eq)) - 1; mdd = (eq / eq.cummax() - 1).min()
    return dict(label=label, per=f"{a[:4]}-{b[:4]}", gamma=gamma, R2OS_pct=round(r2 * 100, 2),
                CERgain_pct_pa=round((out["model"][0] - out["HA"][0]) * 1200, 2),
                shAnn_mod=round(out["model"][1], 2), shAnn_HA=round(out["HA"][1], 2), shAnn_BH=round(y[ok].mean() / y[ok].std(ddof=1) * np.sqrt(12), 2),
                meanW=round(out["model"][2], 2), meanW_HA=round(out["HA"][2], 2), cagr=round(cagr * 100, 2), mdd=round(mdd * 100, 1), nobs=int(ok.sum()))

end = str(last)
rows = []
for lab, fc in (("SOP(dp+ge20)", fc_sop), ("nur dp", fc_dp)):
    for (a, b) in (("1947-01", "2007-12"), ("2008-01", end), ("1947-01", end), ("1980-01", end)):
        for g in (2.0, 5.0):
            rows.append(evaluate(fc, lab, a, b, g, 0.001))
df = pd.DataFrame(rows)
pd.set_option("display.width", 250)
print(df.to_string(index=False))
