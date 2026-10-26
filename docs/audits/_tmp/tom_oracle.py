import sys; sys.path.insert(0, ".")
import pandas as pd, numpy as np
from qlab.calendar import NYSE_BDAY
from qlab.data import french, load_ticker
from strategies import tom_spy_m2_p3 as main, tom_spy_m2_p3_etf as etf
fdf = french("F-F_Research_Data_Factors", daily=True)
fi = fdf.index
spy = load_ticker("SPY", start="1993-01-01", max_age_days=1e9)
def oracle(truth_idx, e=-2, x=3):
    # Wahrheit: Handelstage = Datenindex (+ bekannte fehlende 1994-04-27); Monatsende = letzter Handelstag des Monats
    s = pd.Series(np.arange(len(truth_idx)), index=truth_idx)
    last = s.groupby([truth_idx.year, truth_idx.month]).max().astype(int).tolist()
    ent, ext = [], []
    rel = {-2:-1, -1:0, 1:1, 2:2, 3:3, 4:4}
    for p in last:
        if p-3>=0 and p+5<len(truth_idx):
            ent.append(truth_idx[p+ (rel[e]-1) -1 +1 -1]) if False else ent.append(truth_idx[p-2 if e==-2 else p-1])
            ext.append(truth_idx[p+2 if x==3 else p])
    return ent, ext
truth_spy = spy.index.union(pd.DatetimeIndex(["1994-04-27"]))
for name, mod, panel_idx, truth, build in [
    ("ETF SPY", etf, spy.index, truth_spy, lambda: etf.build_panel(spy)),
    ("French", main, fi, fi, lambda: main.load())]:
    w = mod.weights(build())
    col = w.columns[0]
    ent_m = list(w.index[w[col]==1.0]); ext_m = list(w.index[w[col]==0.0])
    e_o, x_o = oracle(truth)
    e_o_set, x_o_set = set(e_o), set(x_o)
    # nur Monate mit vollständigem Oracle-Fenster ab Start
    start = ent_m[0] if ent_m else None
    e_o2 = [d for d in e_o if start is not None and d>=start]; x_o2=[d for d in x_o if start is not None and d>=start]
    mis_e = sorted(set(e_o2)^set(ent_m)); mis_x = sorted(set(x_o2)^set(ext_m))
    print(name, "Einstiege Modul", len(ent_m), "Oracle", len(e_o2), "Abweichungen", len(mis_e))
    print(name, "Ausstiege Modul", len(ext_m), "Oracle", len(x_o2), "Abweichungen", len(mis_x))
    print("  Beispiele Einstieg:", [str(d.date()) for d in mis_e[:12]])
    print("  Beispiele Ausstieg:", [str(d.date()) for d in mis_x[:12]])
