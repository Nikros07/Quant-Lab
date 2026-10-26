import sys; sys.path.insert(0, ".")
import pandas as pd, numpy as np
from qlab.calendar import NYSE_BDAY
from qlab.data import Panel, french, load_ticker
from qlab.engine import check_causality
from strategies import tom_spy_m2_p3 as main, tom_spy_m2_p3_etf as etf

# (a) Handrechnung: synthetisches Panel, NYSE-Kalender 2001-2003 (>=300 Tage)
idx = pd.date_range("2001-01-02", "2003-06-30", freq=NYSE_BDAY)
rng = np.random.default_rng(42)
r = pd.Series(rng.normal(0.0003, 0.01, len(idx)), index=idx)
P = main.build_panel(r)
w = main.weights(P)["MKT"]
# unabhaengig von Hand: Monatsende = letzter Tag im Monat der Liste, d(-2), d(+3)
L = list(idx)
def pos(d): return L.index(pd.Timestamp(d))
decisions = ["2001-08-31", "2002-02-28", "2003-05-30"]  # d(-1)
for dm1 in decisions:
    p = pos(dm1)
    sig_in = L[p-3]; sig_out = L[p+2]
    print(f"d(-1)={dm1}: Hand Einstiegs-Signal={sig_in.date()} (Ausf. Close {L[p-2].date()}), Ausstiegs-Signal={sig_out.date()} (Ausf. Close {L[p+3].date()})")
    print("   Modul: ", w.get(sig_in, np.nan), w.get(sig_out, np.nan), " | Zeilen in Fenster:", [str(d.date()) for d in w.loc[sig_in:sig_out].index])
# Engine-Rendite Handrechnung: 4 Tage Renditen d(-1),d(+1),d(+2),d(+3) fuer 2002-02
res = main.weights(P)
from qlab.engine import run_backtest, CostModel
rr = run_backtest(P, res, cost=CostModel(default_bps=0.0), rf=pd.Series(0.0, index=idx)).ret
p = pos("2002-02-28")
exp = r.copy()*0; exp.iloc[p:p+4] = r.iloc[p:p+4]
print("Handrechnung Renditen 2002-02 Fenster gleich Modul:", np.allclose(rr.iloc[p-3:p+6].to_numpy(), exp.iloc[p-3:p+6].to_numpy(), atol=1e-12))

# (b) Plausibilitaet: Tagesrendite in Fenstertagen vs. uebrige Tage (SPY 1993-2022, Ausfuehrung Close)
spy = load_ticker("SPY", start="1993-01-01", max_age_days=1e9).loc[:"2022-12-31"]
cc = spy["Close"].pct_change().dropna()
wv = etf.weights(etf.build_panel(spy))["SPY"]
win = pd.Series(0.0, index=cc.index)
ex = pd.Series(np.nan, index=wv.index)
# Fenstertage = Tage mit Haltepositions (Einstieg+1 .. Ausstieg)
held = (wv.reindex(cc.index).ffill().fillna(0) > 0.5).shift(1, fill_value=False)
print("Anteil Tage im Markt (ETF base):", round(float(held.mean()),3))
print("Ann. Rendite Fenstertage:", round(float(cc[held].mean()*252),4), " uebrige:", round(float(cc[~held].mean()*252),4))

# (c) Kausalitaet dicht: Schnitt an letzten 4 Tagen jedes Monats 1955-1960 (Kalender-Verlaengerung vor 1990)
ff = french("F-F_Research_Data_Factors", daily=True)
fi = ff.index
fp = main.build_panel(ff["Mkt-RF"] + ff["RF"])
s = pd.Series(np.arange(len(fi)), index=fi)
cuts = []
for (y,m), g in fi[(fi>="1955-01-01")&(fi<="1960-12-31")].to_series().groupby([fi[(fi>="1955-01-01")&(fi<="1960-12-31")].year, fi[(fi>="1955-01-01")&(fi<="1960-12-31")].month]):
    cuts += list(g.index[-4:])
print("Schnitte:", len(cuts))
print("Kausalitaet dicht 1955-60 (main):", check_causality(lambda pn: main.weights(pn), fp, cuts=cuts)[:3])
