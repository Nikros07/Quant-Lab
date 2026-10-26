import sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path("C:/Users/spide/Desktop/Projekte/Quant-Lab")
sys.path.insert(0, str(ROOT))
from qlab.data import Panel, risk_free_daily, CACHE
from qlab.engine import CostModel, run_backtest
from qlab import metrics
from strategies import crypto_trend_ens_btc_eth as s

# 1) BTC Buy&Hold im Auswahlfenster (gleicher Zeitraum wie Lauf, ohne Kosten)
btc = pd.read_parquet(CACHE / "px_BTC-USD.parquet")["Close"]
btc = btc.loc["2015-09-01":"2022-12-31"]
r = btc.pct_change().fillna(0.0)
rf = risk_free_daily(btc.index)
bh = metrics.summarize(r.iloc[1:], rf.iloc[1:])
print("BTC_BH cagr %.4f vol %.4f sharpe %.3f maxdd %.4f years %s" % (bh["cagr"], bh["vol"], bh["sharpe"], bh["max_dd"], bh["years"]))

# 2) RF-Akkrual: Wochenenden erhalten Freitags-RF?
full = risk_free_daily(pd.date_range("2016-01-01", "2016-01-31", freq="D"))
print("RF Jan 2016 (Sa/So = Freitagswert?):", full.loc["2016-01-08":"2016-01-11"].round(7).tolist())
ann_cal = full.sum() / (31 / 365.25)
print("RF-Summe/Jahr auf Kalendertagen (Engine): %.4f" % ann_cal)
bdays = risk_free_daily(pd.bdate_range("2016-01-01", "2016-01-31")).sum() / (21/252)
print("RF-Summe/Jahr auf Börsentagen: %.4f" % bdays)

# 3) Handrechnung auf synthetischem Panel (eigene Schleifenimplementierung)
rng = np.random.default_rng(11)
n = 420
idx = pd.date_range("2014-09-17", periods=n, freq="D")
p_btc = 100*np.exp(np.cumsum(rng.normal(0.001, 0.03, n)))
p_eth = 100*np.exp(np.cumsum(rng.normal(0.0005, 0.04, n)))
p_eth[:200] = np.nan
close = pd.DataFrame({"BTC-USD": p_btc, "ETH-USD": p_eth}, index=idx)
panel = Panel(close.copy(), close)
w = s.weights(panel, first_signal=None)
def my_w(t):
    out = {}
    for a, col in (("BTC-USD", p_btc), ("ETH-USD", p_eth)):
        if a == "ETH-USD" and t < 199: out[a]=0.0; continue
        window = col[t-199:t+1] if t >= 199 else None
        if window is None or np.isnan(window).any(): out[a]=0.0; continue
        hits = sum(col[t] > col[t-n_+1:t+1].mean() for n_ in (20,50,100,200))
        out[a] = 0.5 * hits / 4
    return out
for t in (260, 333, 419):
    mine = my_w(t); mod = w.loc[idx[t]]
    print(idx[t].date(), "mine", {k: round(v,4) for k,v in mine.items()}, "mod", {k: round(float(mod[k]),4) for k in mine})

# 4) Kosten nur bei Signalwechsel vs. tägliches Nachziehen
changes = (w.diff().abs().sum(axis=1) > 1e-12).sum()
print("Tage mit Zielgewichtsänderung:", int(changes), "von", len(w))
