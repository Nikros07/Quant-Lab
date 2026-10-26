import sys
sys.path.insert(0, r"C:\Users\spide\Desktop\Projekte\Quant-Lab")
import numpy as np, pandas as pd
from qlab.calendar import month_end_flags
from qlab.data import Panel
from strategies import bond_composite_3sig_longonly as m

rng = np.random.default_rng(42)
idx = pd.bdate_range("1990-01-02", periods=1000)
n = len(idx); t = np.arange(n)
tnx = np.clip(5 + 2*np.sin(t/150) + np.cumsum(rng.normal(0, 0.03, n))*0.1, 0.6, 14)
irx = np.clip(tnx - (1.2 + np.sin(t/90)), 0.05, None)
pie = 2.5 + np.sin(t/300)
sig = pd.DataFrame({m.TNX: tnx, m.IRX: irx, m.PIE: pie}, index=idx)
r10, _ = m.synthetic_returns(sig[m.TNX], sig[m.IRX])
px = 100*(1+r10.fillna(0)).cumprod()
close = sig.copy(); close.insert(0, m.ASSET, px)
panel = Panel(close.copy(), close)
W = 100; FAST, SLOW, HL = 21, 252, 36   # kleineres Carry-Fenster nur fuer Handrechnung (Parameter, kein Spec-Bruch im Modul)
w_mod = m.weights(panel, carry_window=W, anchor_halflife=HL)

# unabhaengige Neuimplementierung (Schleifen, keine Modulfunktionen)
y = tnx.copy(); yi = irx.copy()
s = (np.asarray(tnx) - np.asarray(irx))/100
ex = []
r10_l = [np.nan]; rc_l = [np.nan]
for i in range(1, n):
    yp = y[i-1]/100; yc = y[i]/100
    dur = (1-(1+yp/2)**-20)/yp
    r10_l.append(yp/252 - dur*(yc-yp)); rc_l.append(yi[i-1]/100/252)
r10_l = np.array(r10_l); rc_l = np.array(rc_l)
exr = np.log1p(r10_l) - np.log1p(rc_l)
def ewm_manual(x, span=None, hl=None):
    a = 2/(span+1) if span else 1-0.5**(1/hl)
    out = np.full(len(x), np.nan); v=None; k=0
    for i, xi_ in enumerate(x):
        if np.isnan(xi_): continue
        v = xi_ if v is None else (1-a)*v + a*xi_
        k += 1
        out[i] = v
    return out
ef = ewm_manual(exr, span=FAST); es = ewm_manual(exr, span=SLOW)
me_flags = month_end_flags(idx).to_numpy()
rows = {}
ana_hist = []  # Anker ueber Monatsend-Samples
for i in range(n):
    if not me_flags[i]: continue
    real = float(tnx[i] - pie[i])   # Realzins am Monatsende (Prozent)
    ana_hist.append(real)
    if i < W + 1 or np.isnan(ef[i]) or np.isnan(es[i]) or len(ana_hist) < HL: continue
    past = s[i-W:i]
    car = 1.0 if (past < s[i]).mean() > 1/3 else 0.0
    trd = 1.0 if (ef[i] > 0 and es[i] > 0) else 0.0
    # Anker: EWMA ueber Monatsend-Realzinsen inkl. aktuellem Monat, halflife in Monaten
    a = 1-0.5**(1/HL); anc = ana_hist[0]
    for q in ana_hist[1:]: anc = (1-a)*anc + a*q
    val = 1.0 if real > anc else 0.0
    rows[idx[i]] = (car+trd+val)/3

# Vergleich an 3 Entscheidungstagen (erste, mittlere, letzte gemeinsame Zeile)
common = [d for d in w_mod.index if d in rows]
print("Modul-Zeilen", len(w_mod), "Handrechnung-Zeilen", len(rows), "gemeinsam", len(common))
picks = [common[0], common[len(common)//2], common[-1]]
for d in picks:
    print(d.date(), "Modul", round(float(w_mod.loc[d, m.ASSET]),6), "Hand", round(rows[d],6))
mx = max(abs(float(w_mod.loc[d, m.ASSET]) - rows[d]) for d in common)
print("max abs Abweichung ueber alle gemeinsamen Tage:", mx)
print("Modul-Tage ohne Hand-Gegenstueck:", len(set(w_mod.index)-set(rows)), " Hand ohne Modul:", len(set(rows)-set(w_mod.index)))
