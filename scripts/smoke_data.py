import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from qlab import controls, metrics
from qlab.data import french, load_panel, risk_free_daily
from qlab.engine import run_backtest

p = load_panel(["SPY", "IEF"], start="1993-01-01").truncate("2022-12-31")
print("SPY ab", p.close["SPY"].first_valid_index().date(), "IEF ab", p.close["IEF"].first_valid_index().date(), "Tage", len(p.close))
rf = risk_free_daily(p.close.index)
print("RF Tagesmittel ann.: %.2f%%" % (rf.mean() * 252 * 100))
r = run_backtest(p, controls.buy_and_hold(p, "SPY"), rf=rf)
s = metrics.summarize(r.ret.loc[r.ret.ne(0).idxmax():], rf)
print("SPY B&H 1993-2022: CAGR %.2f%%  Vol %.1f%%  Sharpe %.2f  MaxDD %.1f%%" % (100*s["cagr"], 100*s["vol"], s["sharpe"], 100*s["max_dd"]))
q = p.slice("2003-01-01")
r2 = run_backtest(q, controls.fixed_mix(q, {"SPY": .6, "IEF": .4}), rf=rf)
s2 = metrics.summarize(r2.ret.loc[r2.ret.ne(0).idxmax():], rf)
print("60/40 2003-2022:   CAGR %.2f%%  Vol %.1f%%  Sharpe %.2f  MaxDD %.1f%%  Umsatz/J %.2f" % (100*s2["cagr"], 100*s2["vol"], s2["sharpe"], 100*s2["max_dd"], r2.turnover.sum()/20))
f = french("F-F_Research_Data_Factors", daily=True)
print("French daily:", f.index.min().date(), f.index.max().date(), list(f.columns))
