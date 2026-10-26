import sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path("C:/Users/spide/Desktop/Projekte/Quant-Lab")
sys.path.insert(0, str(ROOT))
from qlab.data import load_panel, risk_free_daily
from qlab.engine import CostModel, run_backtest
from strategies import crypto_trend_ens_btc_eth as s
panel = load_panel(["BTC-USD", "ETH-USD"], start="2014-09-17").truncate("2022-12-31")
w = s.weights(panel)
rf = risk_free_daily(panel.close.index)
win = (panel.close.index >= "2015-09-01") & (panel.close.index <= "2022-12-31")
yrs = (panel.close.index[-1] - pd.Timestamp("2015-09-01")).days / 365.25
rf_cal = rf.loc["2015-09-01":].sum() / yrs
bd = risk_free_daily(pd.bdate_range("2015-09-01", "2022-12-31"))
rf_bd = bd.sum() / yrs
cash = (1 - w.sum(axis=1)).loc["2015-09-01":]
print("mittlere Cash-Quote im Lauf: %.3f" % cash.mean())
print("RF p.a. kalendertags-Index: %.5f ; nur Börsentage (Ken French): %.5f" % (rf_cal, rf_bd))
print("Überverzinsung Cash p.a. (Näherung): %.5f" % (cash.mean() * (rf_cal - rf_bd)))
# Kosten nur bei Signalwechsel (Spezifikations-Eigencheck) vs. tägliches Nachziehen (Modul)
w2 = w.loc["2015-09-01":]
chg = w2.diff().abs().sum(axis=1).fillna(0) > 1e-12
w_sig = w2.where(chg).ffill().fillna(0.0)
for lbl, ww in (("taeglich (Modul)", w2), ("nur Signalwechsel", w_sig)):
    r = run_backtest(panel, ww, cost=CostModel(per_ticker_bps=s.SPEC["cost_bps"]), rf=rf)
    nav = r.nav.loc["2015-09-01":]
    cg = (nav.iloc[-1]/nav.iloc[0]) ** (1/yrs) - 1
    print(lbl, "CAGR %.4f cost_p.a. %.4f" % (cg, r.cost.loc["2015-09-01":].sum()/yrs))
print("Signaltage mit Wechsel (Auswahlfenster): %d" % chg.sum())
# korrigiert: Zeilen ohne Wechsel ganz weglassen (leere Zeile = nichts tun)
ww = w2[chg]
r = run_backtest(panel, ww, cost=CostModel(per_ticker_bps=s.SPEC["cost_bps"]), rf=rf)
nav = r.nav.loc["2015-09-01":]
print("nur Wechsel-Zeilen (korrigiert) CAGR %.4f cost_p.a. %.4f" % ((nav.iloc[-1]/nav.iloc[0])**(1/yrs)-1, r.cost.loc["2015-09-01":].sum()/yrs))
