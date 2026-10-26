"""Wegwerf-Handrechnung fuer den Audit index_etf_ibs_rsi2_longonly (nur lesend auf Projektcode)."""
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, r"C:\Users\spide\Desktop\Projekte\Quant-Lab")
from qlab.calendar import NYSE_BDAY
from qlab.engine import run_backtest
from qlab.data import Panel
from strategies.index_etf_ibs_rsi2_longonly import OHLCPanel, weights

rng = np.random.default_rng(42)
n = 320
idx = pd.date_range("2015-01-02", periods=n, freq=NYSE_BDAY)
close = 100 * np.exp(np.cumsum(rng.normal(0.0006, 0.01, n)))
open_ = np.r_[close[0], close[:-1]] * (1 + rng.normal(0, 0.003, n))
hi = np.maximum(open_, close) + np.abs(rng.normal(0, 0.006, n)) * close
lo = np.minimum(open_, close) - np.abs(rng.normal(0, 0.006, n)) * close
f = lambda a: pd.DataFrame({"SPY": a}, index=idx)
P = OHLCPanel(f(open_), f(close), f(hi), f(lo))

# Unabhaengige Neuimplementierung: reine Schleifen, Basisregel
c = close; h = hi; l = lo
sma = np.array([np.mean(c[i - 199:i + 1]) if i >= 199 else np.nan for i in range(n)])
ibs = np.array([(c[i] - l[i]) / (h[i] - l[i]) if h[i] > l[i] else np.nan for i in range(n)])
state = np.full(n, np.nan)
held, t0 = False, -1
for i in range(199, n):
    if held:
        if ibs[i] > 0.70 or i - t0 >= 5:          # Ausstiegssignal am Tag i
            held = False
    elif c[i] > sma[i] and ibs[i] < 0.20:          # Einstiegssignal am Tag i
        held, t0 = True, i
    state[i] = 1.0 if held else 0.0

w = weights(P, ticker="SPY")
mod_state = w["SPY"].reindex(idx).ffill()
ref = pd.Series(state, index=idx)
mism = int(((mod_state.fillna(-1) != ref.fillna(-1))).sum())
print("Tage mit Abweichung Modul vs. Neuimplementierung (Basis):", mism)

# Entscheidungstage: erster Einstieg, erster Ausstieg, Zeitstopp
changes = [i for i in range(1, n) if state[i] == 1 and state[i - 1] == 0]
for i in changes[:3]:
    print(f"Signaltag t={idx[i].date()} state={state[i]:.0f} close={c[i]:.4f} ibs={ibs[i]:.3f} sma200={sma[i]:.4f}")
    print("   Modul-Zeile:", w.loc[idx[i]].to_dict() if idx[i] in w.index else "keine Zeile")

# Ausfuehrungszeitpunkt in der Engine: Gewicht wirkt auf Position am Tagesende
for mode in ["open", "close_next"]:
    res = run_backtest(P, w, exec_mode=mode, rf=pd.Series(0.0, index=idx))
    first_change = changes[0]
    print(f"exec={mode}: Signal t={idx[first_change].date()}, Position am Schluss t: {res.weights['SPY'].iloc[first_change]:.3f}, "
          f"t+1: {res.weights['SPY'].iloc[first_change + 1]:.3f}")
    # Ausfuehrungspreis: Kauf zu open[t+1] bzw. close[t+1]
    px = open_[first_change + 1] if mode == "open" else close[first_change + 1]
    print(f"   Erwarteter Kaufpreis = {'Eroeffnung' if mode=='open' else 'Schluss'} t+1 = {px:.4f}")
    print(f"   Engine Kosten/Trade-Summe: {res.cost.sum():.6f}, Anzahl Trades: {res.n_trades}")
