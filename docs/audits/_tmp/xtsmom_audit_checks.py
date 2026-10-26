import sys
sys.path.insert(0, ".")
import numpy as np, pandas as pd
from qlab.calendar import month_end_flags
from qlab.data import CACHE
import strategies.xtsmom_us_switch_longcash as M
import strategies.xtsmom_us_switch_longcash_etf as E

# (1) Monatsende: Daten-basiert (nur letzter Tag kalender) vs. reine Kalender-Variante
def cmp(name, idx):
    a = month_end_flags(idx)
    b = month_end_flags(idx, calendar_only=True)
    diff = a[a != b]
    print(f"{name}: Tage={len(idx)} Monatsende(daten)={int(a.sum())} Monatsende(kalender)={int(b.sum())} Abweichungen={len(diff)}")
    for d in diff.index[:8]:
        print("   Abw.:", d.date(), "daten=", bool(a[d]), "kalender=", bool(b[d]))
    return diff

pe = E.load()
cmp("ETF-Panel", pe.close.index)
# Lange Panels: nur Index des VFINX-Kurses (Kalender des Hauptmoduls)
try:
    pl = M.load()
    cmp("Langpanel", pl.close.index)
except Exception as exc:
    print("Langpanel nicht ladbar:", exc)

# (2) Signaltage vergleichen: Modul-Signale mit Kalender-Monatsenden (calendar_only)
w = E.weights(pe)
print("ETF Signale:", len(w), "erstes:", w.index[0].date(), "letztes:", w.index[-1].date())
