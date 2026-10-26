import sys
sys.path.insert(0, ".")
import numpy as np, pandas as pd
import strategies.xtsmom_us_switch_longcash_etf as E
from qlab.calendar import month_end_flags

p = E.load()
w = E.weights(p)
c = p.close
# unabhaengig: Monatsendtage aus Daten (letzter Datentag je Monat), nur fuer Pruefung
me = c.index.to_series().groupby([c.index.year, c.index.month]).last()
def px_at(col, d): return c[col].loc[:d].ffill().iloc[-1]
for T in ["2008-10-31", "2020-03-31", "2012-06-29"]:
    T = pd.Timestamp(T)
    if T not in w.index and T not in me.values:
        print(T.date(), "kein Monatsende"); continue
    months = [pd.Timestamp(d) for d in me.values]
    j = months.index(T)
    T12 = months[j-12]
    rf = 1.0
    for k in range(1, 13):                      # Monat T-k+1 verzinst mit ^IRX am Ende T-k
        rf *= 1 + px_at("^IRX", months[j-k]) / 100 / 12
    rf -= 1
    rE = px_at("SPY", T) / px_at("SPY", T12) - 1 - rf
    rB = px_at("IEF", T) / px_at("IEF", T12) - 1 - rf
    exp = "SPY" if (rB > 0 and rE > 0) else ("IEF" if rB > 0 else "SHY")
    got = w.loc[T].idxmax() if T in w.index else "kein Wechsel (Zustand unveraendert)"
    print(f"{T.date()}: rf12={rf:.4%} rE={rE:+.4%} rB={rB:+.4%} -> Hand={exp} | Modul={got}")
