"""Misst die vorab registrierten Takt-Varianten H1-H4 gegen die Basis (monatlich MA12) auf dem S&P 500.

Hypothesen: docs/HYPOTHESEN.md (eingetragen vor dem Test). NUR Auswahlzeitraum bis 2022-12-31,
der Holdout ab 2023 wird nicht geladen.
Signal: ^GSPC (Preisindex), gehandelt: SPY, Ausführung zur Eröffnung des Folgetags, 10 bp je Wechsel.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
import pandas as pd

from qlab import metrics, stats
from qlab.calendar import month_end_flags, week_end_flags
from qlab.data import load_panel, risk_free_daily
from qlab.engine import CostModel, TaxModel, run_backtest

END = "2022-12-31"
START = "1994-01-01"          # gemeinsamer Start (SMA200 und MA12 sind dann sicher warmgelaufen)

panel = load_panel(["SPY", "^GSPC"], start="1990-01-01").truncate(END)
px = panel.close["^GSPC"].ffill(limit=5)
idx = px.index


def hysteresis(sig_close: pd.Series, sig_ma: pd.Series, decision: pd.Series, band: float) -> pd.Series:
    """Zustandsmaschine wie im Pine-Skript: nur an Entscheidungstagen aktualisieren."""
    state, out = False, []
    for d in idx:
        if decision.at[d] and np.isfinite(sig_close.at[d]) and np.isfinite(sig_ma.at[d]):
            if sig_close.at[d] >= sig_ma.at[d] * (1 + band):
                state = True
            elif sig_close.at[d] < sig_ma.at[d] * (1 - band):
                state = False
        out.append(state)
    s = pd.Series(out, index=idx)
    first = sig_ma.first_valid_index()
    return s[s.index >= first]


def monthly(band=0.0):
    f = month_end_flags(idx)
    me = px[f.to_numpy()]
    ma = me.rolling(12).mean()
    c = me.reindex(idx).ffill(); m = ma.reindex(idx).ffill()
    return hysteresis(c.where(f), m.where(f), f, band)


def weekly(band=0.0):
    f = week_end_flags(idx)
    we = px[f.to_numpy()]
    ma = we.rolling(40).mean()
    return hysteresis(we.reindex(idx).where(f), ma.reindex(idx).where(f), f, band)


def daily200(band=0.0):
    ma = px.rolling(200).mean()
    return hysteresis(px, ma, pd.Series(True, index=idx), band)


def cross(band=0.0):
    fast, slow = px.rolling(50).mean(), px.rolling(200).mean()
    return hysteresis(fast, slow, pd.Series(True, index=idx), band)


VARIANTS = {
    "Basis monatlich MA12": monthly,
    "H1 wöchentlich SMA40": weekly,
    "H2 täglich SMA200": daily200,
    "H3 täglich SMA50/200": cross,
    "H4 täglich SMA200 + 1% Puffer": lambda: daily200(0.01),
}

rf = risk_free_daily(idx)
cost = CostModel(per_ticker_bps={"SPY": 10.0})
rows, rets = [], {}
for name, fn in VARIANTS.items():
    on = fn()
    on = on[on.index >= pd.Timestamp(START)]
    w = pd.DataFrame({"SPY": on.astype(float)})
    w = w[w["SPY"].diff().fillna(1.0) != 0]                      # nur Zustandswechsel als Signal
    res = run_backtest(panel, w, cost=cost, rf=rf)
    res_t = run_backtest(panel, w, cost=cost, rf=rf, tax=TaxModel())
    first = w.index.min()
    r, rt = res.ret.loc[first:], res_t.ret_after_liquidation_tax().loc[first:]
    rets[name] = (r, rt)
    s, st = metrics.summarize(r, rf), metrics.summarize(rt, rf)
    entries = int((w["SPY"].diff().fillna(1.0) > 0).sum())
    rows.append({"Variante": name, "Einstiege": entries, "pro Jahr": entries / s["years"], "CAGR": s["cagr"], "Vol": s["vol"],
                 "Sharpe": s["sharpe"], "MaxDD": s["max_dd"], "CAGR nach Steuer": st["cagr"], "Sharpe nach Steuer": st["sharpe"],
                 "Kosten/J": float(res.cost.loc[first:].sum() / s["years"]), "investiert": float((on.reindex(r.index).fillna(False)).mean())})

spy = run_backtest(panel, pd.DataFrame({"SPY": [1.0]}, index=[panel.close["SPY"].first_valid_index()]), cost=CostModel(), rf=rf)
spy_t = run_backtest(panel, pd.DataFrame({"SPY": [1.0]}, index=[panel.close["SPY"].first_valid_index()]), cost=CostModel(), rf=rf, tax=TaxModel())
first = pd.Timestamp(START)
bs, bst = metrics.summarize(spy.ret.loc[first:], rf), metrics.summarize(spy_t.ret_after_liquidation_tax().loc[first:], rf)
rows.append({"Variante": "SPY Buy&Hold", "Einstiege": 1, "pro Jahr": 0.0, "CAGR": bs["cagr"], "Vol": bs["vol"], "Sharpe": bs["sharpe"],
             "MaxDD": bs["max_dd"], "CAGR nach Steuer": bst["cagr"], "Sharpe nach Steuer": bst["sharpe"], "Kosten/J": 0.0, "investiert": 1.0})

df = pd.DataFrame(rows).set_index("Variante")
base_rt = rets["Basis monatlich MA12"][1]
pvals = {}
for name, (r, rt) in rets.items():
    if name.startswith("Basis"):
        continue
    b = stats.bootstrap_sharpe_diff(rt, base_rt, rf=rf, n_boot=1000)
    pvals[name] = (b["sharpe_diff"], b["ci90"][0], b["ci90"][1], b["p_value"])

fmt = df.copy()
for c in ["CAGR", "Vol", "MaxDD", "CAGR nach Steuer", "Kosten/J", "investiert"]:
    fmt[c] = (fmt[c] * 100).round(2).astype(str) + " %"
for c in ["Sharpe", "Sharpe nach Steuer", "pro Jahr"]:
    fmt[c] = fmt[c].round(2)
print(f"Zeitraum {START} bis {END}, Kosten 10 bp je Wechsel, Signal ^GSPC, gehandelt SPY, Ausführung Eröffnung Folgetag\n")
print(fmt.to_string())
print("\nΔ Sharpe nach Steuer gegenüber der Basis (Stationärer Bootstrap, 90%-Intervall, p einseitig):")
for k, (d, lo, hi, p) in pvals.items():
    print(f"  {k:32s} Δ={d:+.2f}  [{lo:+.2f} … {hi:+.2f}]  p={p:.3f}")
print("\nAbbruchkriterium (HYPOTHESEN.md): Verbesserung nur wenn Nach-Steuer-Sharpe ≥ Basis + 0,05 UND MaxDD ≥ −30 %")
base = df.loc["Basis monatlich MA12", "Sharpe nach Steuer"]
for k in VARIANTS:
    if k.startswith("Basis"):
        continue
    ok = (df.loc[k, "Sharpe nach Steuer"] >= base + 0.05) and (df.loc[k, "MaxDD"] >= -0.30)
    print(f"  {k:32s} {'ERFÜLLT' if ok else 'nicht erfüllt'}  (Sharpe nach Steuer {df.loc[k, 'Sharpe nach Steuer']:.2f} vs Basis {base:.2f}, MaxDD {df.loc[k, 'MaxDD'] * 100:.1f} %)")
