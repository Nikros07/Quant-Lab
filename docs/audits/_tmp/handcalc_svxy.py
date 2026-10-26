"""Wegwerf-Handrechnung fuer svxy_term_structure_filter (synthetisches Panel, feste Seeds)."""
import sys
sys.path.insert(0, r"C:\Users\spide\Desktop\Projekte\Quant-Lab")
import numpy as np
import pandas as pd
from qlab.data import Panel
from strategies import svxy_term_structure_filter as strat

rng = np.random.default_rng(42)
n = 400
idx = pd.bdate_range("2014-01-02", periods=n)
ratio = np.full(n, 1.1)
ratio[60:120] = 0.9          # EIN ab 60
ratio[150:151] = 1.0         # exakt 1.0 -> AUS, Wechsel am 150
ratio[200:260] = 0.8         # EIN ab 200
ratio[260:] = 1.2            # AUS ab 260
vix3m = pd.Series(20.0, index=idx)
vix = pd.Series(ratio * 20.0, index=idx)
svxy = pd.Series(50 * np.exp(np.cumsum(rng.normal(0, 0.02, n))), index=idx)
spy = pd.Series(300 * np.exp(np.cumsum(rng.normal(0, 0.01, n))), index=idx)
close = pd.DataFrame({"SVXY": svxy, "SPY": spy, "^VIX": vix, "^VIX3M": vix3m})
open_ = close.copy()
panel = Panel(open_, close)

w = strat.weights(panel)["SVXY"]
# Eigene Referenz: Zustandswechsel gegenueber Vortag, Zeile nur bei Wechsel oder erstem Tag
expected = {}
prev = None
for k, d in enumerate(idx):
    on = bool(vix.iloc[k] / vix3m.iloc[k] < 1.0)
    if prev is None or on != prev:
        expected[d] = 1.0 if on else 0.0
    prev = on
exp = pd.Series(expected, dtype=float)

print("Modul-Zeilen:", len(w), "| Referenz-Zeilen:", len(exp))
print("Index identisch:", list(w.index) == list(exp.index))
print("Werte identisch:", np.allclose(w.to_numpy(), exp.to_numpy()))
for d in [idx[59], idx[60], idx[149], idx[150], idx[199], idx[200], idx[259], idx[260]]:
    print(d.date(), "ratio", round(float(vix[d] / vix3m[d]), 3),
          "modul", float(w.get(d, np.nan)), "ref", float(exp.get(d, np.nan)))
print("Summe Gewichte je Zeile max:", float(strat.weights(panel).sum(axis=1).max()))
