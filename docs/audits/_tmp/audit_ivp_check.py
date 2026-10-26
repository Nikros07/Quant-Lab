"""Wegwerf-Pruefskript Audit ivp_risk_parity_unlevered (nur lesend, schreibt nichts ausser stdout)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\spide\Desktop\Projekte\Quant-Lab")
sys.path.insert(0, str(ROOT))

from qlab.calendar import month_end_flags, NYSE_BDAY  # noqa: E402
from qlab.data import Panel, load_panel, risk_free_daily  # noqa: E402
from qlab.engine import CostModel, run_backtest  # noqa: E402
from qlab import metrics  # noqa: E402
from strategies import ivp_risk_parity_unlevered as M  # noqa: E402

T = M.TICKERS
print("== 1) Realdaten, bis 2022-12-31 ==")
p = load_panel(T, start=M.SPEC["start"]).truncate("2022-12-31")
print("Index:", p.close.index[0].date(), p.close.index[-1].date(), "Zeilen", len(p.close))
print("erste gueltige Kurse je Titel:")
print(p.close.apply(lambda s: s.first_valid_index().date() if s.first_valid_index() is not None else None).to_string())
print("Zeilen mit NaN in mind. einem Titel (ab 2008):", int(p.close.loc["2008":, T].isna().any(axis=1).sum()))

# 1a) Monatsend-Flags: kausal vs. reiner Kalender
f_panel = month_end_flags(p.close.index)
f_cal = month_end_flags(p.close.index, calendar_only=True)
diff = (f_panel.to_numpy() != f_cal.to_numpy())
print("Flag-Abweichung Datenindex vs. NYSE-Kalender:", int(diff.sum()), "Tage", list(p.close.index[diff][:5].date))

# 2) Basis und Varianten durch die Modulfunktion (wie Harness)
w_base = M.weights(p)
print("Signaltage Basis:", len(w_base), "erster:", w_base.index[0].date(), "letzter:", w_base.index[-1].date())
print("max |Zeilensumme - 1|:", float((w_base.sum(axis=1) - 1).abs().max()))
print("min/max Gewicht:", float(w_base.min().min()), float(w_base.max().max()))
me_priced = p.close.index[f_cal.to_numpy() & p.close[T].notna().all(axis=1).to_numpy()]
print("Monatsenden mit Kurs-Vollstaendigkeit ab Gate:", len([d for d in me_priced if d >= w_base.index[0]]),
      "vs Signale", len(w_base))
w_eq = M.weights(p, scheme="equal")
print("Gleiche Signaltage Kontrolle vs Basis:", list(w_eq.index) == list(w_base.index))

# 3) Engine-Lauf Basis und 1/N-Kontrolle (Abbruchkriterium der Spezifikation)
cost = CostModel()
rf = risk_free_daily(p.close.index)
res_b = run_backtest(p, w_base, cost=cost, rf=rf)
res_e = run_backtest(p, w_eq, cost=cost, rf=rf)
print("skipped_orders Basis/1N:", res_b.skipped_orders, res_e.skipped_orders)
print("n_trades Basis/1N:", res_b.n_trades, res_e.n_trades)
for name, r in (("Basis", res_b), ("1/N", res_e)):
    rr = r.ret.loc[w_base.index[0]:]
    s = metrics.summarize(rr, r.rf.loc[w_base.index[0]:])
    dd22 = r.nav.loc["2022"]
    mdd22 = float((dd22 / dd22.cummax() - 1).min())
    print(f"{name}: CAGR {s['cagr']:.4f} Vol {s['vol']:.4f} Sharpe {s['sharpe']:.3f} MaxDD {s['max_dd']:.4f} MaxDD2022 {mdd22:.4f}")
rr_b = res_b.ret.loc[w_base.index[0]:]
rr_e = res_e.ret.loc[w_base.index[0]:]
sb = metrics.sharpe_daily(rr_b, res_b.rf.loc[rr_b.index])
se = metrics.sharpe_daily(rr_e, res_e.rf.loc[rr_e.index])
print(f"Sharpe Basis {sb:.3f} 1/N {se:.3f} Differenz {sb - se:.3f}")
print("Wochenend-/Markt-Gewichte 2022-12-30 Basis:", w_base.loc[w_base.index[w_base.index <= '2022-12-31'][-1]].round(4).to_dict())

# 4) Handrechnung auf synthetischem Panel, unabhaengige Neuimplementierung
rng = np.random.default_rng(2024)
n = 900
idx = pd.date_range("2005-01-03", periods=n, freq=NYSE_BDAY)
vol = np.array([0.010, 0.014, 0.018, 0.005, 0.004, 0.012, 0.003, 0.008, 0.016])
rets = rng.normal(0.0002, 1.0, (n, 9)) * vol + 0.3 * rng.normal(0, 0.008, (n, 1))
close_arr = 100 * np.cumprod(1 + rets, axis=0)
close = pd.DataFrame(close_arr, index=idx, columns=T)
open_ = close.shift(1).fillna(100.0)
pp = Panel(open_, close)
w_mod = M.weights(pp)
# unabhaengig: Monatsende = letzter Tag des Monats im Index (Synthetik, kein Kalenderproblem)
ends = [d for d in idx[:-1] if idx[idx.get_loc(d) + 1].month != d.month] + [idx[-1]]
R = close.pct_change(fill_method=None)
checked = []
for d in ends:
    i = idx.get_loc(d)
    if i < 504:
        continue
    win = R.iloc[max(0, i - 755): i + 1]
    if win.notna().sum().min() < 504:
        continue
    s = np.array([win[c].std(ddof=1) for c in T]) * np.sqrt(252)
    ref = (1 / s) / (1 / s).sum()
    checked.append((d, ref))
print("== 4) Handrechnung synthetisch ==")
print("Monatsenden mit Gate in Handrechnung:", len(checked), "Modul-Signale:", len(w_mod))
for d, ref in checked[:3] + checked[-2:]:
    if d in w_mod.index:
        dev = float(np.max(np.abs(w_mod.loc[d].to_numpy() - ref)))
        print(d.date(), "Modul", np.round(w_mod.loc[d].to_numpy(), 5), "Hand", np.round(ref, 5), "max|Abw|", f"{dev:.2e}")
    else:
        print(d.date(), "fehlt im Modul")
# Pruefung: Modul hat keine Zeile, die die Hand nicht hat
print("Modul-Zeilen ohne Hand-Gegenstueck:", len(set(w_mod.index) - set(d for d, _ in checked)))
print("Hand-Zeilen ohne Modul-Gegenstueck:", len(set(d for d, _ in checked) - set(w_mod.index)))
