"""Wegwerf-Audit (nur lesend): Handrechnung + Umschlag-/Datencheck fuer commodity_gold_trend_dbc_gld."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path("C:/Users/spide/Desktop/Projekte/Quant-Lab")
sys.path.insert(0, str(ROOT))
from qlab.data import Panel, load_panel
from strategies import commodity_gold_trend_dbc_gld as S

# 1) Synthetisches Panel, fester Seed, 400 Tage
rng = np.random.default_rng(12345)
n = 400
idx = pd.bdate_range("2010-01-04", periods=n)
T = ["DBC", "GLD"]
ret = rng.normal(0.0003, 0.01, (n, 2)) + np.where(np.arange(n)[:, None] < 250, 0.0, -0.0012)
close = pd.DataFrame(100 * np.exp(np.cumsum(ret, axis=0)), index=idx, columns=T)
open_ = close.shift(1).fillna(100.0)
p = Panel(open_, close)

w = S.weights(p)
print("Modul-Zeilen (Datum, DBC, GLD):")
print(w.to_string())

# unabhaengige Neuimplementierung
exp_rows = []
prev = None
for k in range(209, n):
    on = {t: float(close[t].iloc[k] > close[t].iloc[k - 209:k + 1].mean()) for t in T}
    tgt = (0.5 * on["DBC"], 0.5 * on["GLD"])
    if prev is None or tgt != prev:
        exp_rows.append((idx[k], tgt))
    prev = tgt
print("\nErwartet (Handrechnung):")
for d, tg in exp_rows:
    print(d.date(), tg)
ok = len(exp_rows) == len(w) and all(
    d == w.index[i] and np.allclose(w.iloc[i].to_numpy(), tg) for i, (d, tg) in enumerate(exp_rows))
print("\nUebereinstimmung Modul vs Handrechnung:", ok)

# 2) Echte Daten: Umschlag pro Jahr (Signalwechsel) und Startdatum
real = load_panel(["DBC", "GLD"], start="2004-01-01").truncate("2022-12-31")
wr = S.weights(real)
print("\nReal: erster Signaltag", wr.index.min().date(), "Zeilen", len(wr))
chg = wr.diff().abs().sum(axis=1).iloc[1:]
years = (wr.index[-1] - wr.index[0]).days / 365.25
print("Signalwechsel gesamt", len(wr) - 1, "pro Jahr", round((len(wr) - 1) / years, 2))
print("Summe |dw| (beide Seiten) pro Jahr", round(float(chg.sum()) / years, 2))
print("Einseitiger Umschlag pro Jahr (|dw|/2)", round(float(chg.sum()) / 2 / years, 2))
print("DBC erster Kurs", real.close["DBC"].first_valid_index().date(), "GLD erster Kurs", real.close["GLD"].first_valid_index().date())
print("DBC-Kurse vor 2006-03-01:", int(real.close["DBC"].loc[:"2006-03-01"].notna().sum()))
print("Letzter Lauf-Tag", real.close.index[-1].date())
