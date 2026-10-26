import sys; sys.path.insert(0, ".")
import pandas as pd, numpy as np
from qlab.calendar import NYSE_BDAY
from qlab.data import french, risk_free_daily
from qlab.data import load_ticker
fdf = french("F-F_Research_Data_Factors", daily=True)
idx = fdf.index
print("French n", len(idx), idx[0].date(), idx[-1].date())
# Mo-Fr Tage ohne Datenzeile nach 1990 (Kalender-Lücken)
mf = pd.bdate_range("1990-01-01", idx[-1])
miss = mf.difference(idx)
print("French Mo-Fr-Lücken ab 1990:", len(miss), [str(d.date()) for d in miss[:15]])
extra = idx[idx >= "1990-01-01"].difference(NYSE_BDAY.__class__ and pd.date_range("1990-01-01", idx[-1], freq=NYSE_BDAY))
print("French Daten an Nicht-Handelstagen (NYSE-Kalender, ab 1990):", len(extra), [str(d.date()) for d in extra[:15]])
pre = idx[idx < "1952-05-26"]
print("French Samstage vor 1952-05-26:", int((pre.dayofweek == 5).sum()), "letzter Samstag:", str(pre[pre.dayofweek==5][-1].date()) if (pre.dayofweek==5).any() else None)
spy = load_ticker("SPY", start="1993-01-01", max_age_days=1e9)
si = spy.index
cal = pd.date_range(si[0], si[-1], freq=NYSE_BDAY)
print("SPY n", len(si), si[0].date(), si[-1].date(), "fehlende NYSE-Tage:", len(cal.difference(si)), [str(d.date()) for d in cal.difference(si)[:15]])
print("SPY Daten an Nicht-Handelstagen:", [str(d.date()) for d in si.difference(cal)[:15]])
# Monatsende-Vergleich: Datenbasiert vs Kalender (nur Daten-Index)
def me_data(i):
    return set(i[:-1][np.array([i[k+1].month!=i[k].month for k in range(len(i)-1)])])
def me_cal(i):
    s=set()
    for d in i:
        if (d+NYSE_BDAY).month!=d.month: s.add(d)
    return s
a=me_data(si); b=me_cal(si[:-1])
print("SPY Monatsende data vs cal: nur data", len(a-b), "nur cal", len(b-a), sorted(d.date() for d in (a^b))[:10])
