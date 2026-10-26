"""Audit-Wegwerfskript (nur lesend): Handrechnung Sektor-Proxy, Wochenfenster, Faktor-Alpha."""
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, "C:/Users/spide/Desktop/Projekte/Quant-Lab")
from qlab.calendar import NYSE_BDAY
from qlab.data import Panel
from strategies import lowvol_defensive_longonly_etf as E
from strategies import lowvol_defensive_longonly as M

SECT = E.SECTORS
rng = np.random.default_rng(42)
idx = pd.date_range("2000-01-03", "2009-12-31", freq=NYSE_BDAY)
sig = dict(zip(SECT, [0.0100, 0.0140, 0.0068, 0.0120, 0.0175, 0.0055, 0.0075, 0.0080, 0.0160]))
close = pd.DataFrame({s: 50 * np.exp(np.cumsum(rng.normal(0.0002, sig[s], len(idx)))) for s in SECT}, index=idx)
panel = Panel(close.copy(), close.copy())
print("Tage:", len(idx), "erster/letzter:", idx[0].date(), idx[-1].date())

# --- Unabhaengige Referenz: Wochenschluss = letzter Handelstag je (Kalenderjahr, ISO-Jahr, ISO-Woche)
iso = idx.isocalendar()
wkey = list(zip(idx.year, iso["year"].to_numpy(), iso["week"].to_numpy()))
wk_last = pd.Series(idx, index=range(len(idx))).groupby(pd.Series(wkey, index=range(len(idx))).astype(str).to_numpy()).last()
week_ends = pd.DatetimeIndex(wk_last.to_numpy()).sort_values()
print("Wochenschluesse gesamt:", len(week_ends), " je Kalenderjahr 2001:", int(((week_ends.year == 2001)).sum()),
      " (ISO-Wochen waeren ~52)")
# Monatsende = letzter Handelstag je Kalendermonat (nur Referenz, volle Daten)
me = pd.Series(idx, index=idx).groupby([idx.year, idx.month]).last().to_numpy()
me = pd.DatetimeIndex(me)

mod_w = E.weights(panel, mode="sector_lowvol")
mod_vol = E.weekly_vol(close)
print("Modul-Signale:", len(mod_w), "erstes:", mod_w.index[0].date())

checks = []
for t in [me[60], me[80], me[95]]:
    ends = week_ends[week_ends <= t]
    wc = close.loc[ends]
    wr = (wc / wc.shift(1) - 1.0).iloc[1:]
    last156 = wr.iloc[-156:]
    ref_vol = last156.std(ddof=1)
    ref_pick = ref_vol.sort_values(kind="stable").index[:3].tolist()
    modrow_vol = mod_vol.loc[t, SECT]
    maxdiff = float(np.abs(modrow_vol.to_numpy() - ref_vol.reindex(SECT).to_numpy()).max())
    modrow = mod_w.loc[t]
    mod_pick = sorted(modrow[modrow > 0].index.tolist())
    print(f"\nEntscheidungstag {t.date()}: Wochenenden<=t={len(ends)}, Fenster={len(last156)} Renditen von {last156.index[0].date()} bis {last156.index[-1].date()}")
    print("  Ref-Std je Sektor:", {k: round(v, 5) for k, v in ref_vol.sort_values().items()})
    print("  Ref-Auswahl:", sorted(ref_pick), " Modul-Auswahl:", mod_pick, " Modul-Gewichte:", modrow[modrow > 0].round(4).to_dict())
    print("  max |Std-Abweichung Modul vs Ref|:", maxdiff, " Summe Gewichte:", float(modrow.sum()))
    checks.append(sorted(ref_pick) == mod_pick and maxdiff < 1e-12 and abs(modrow.sum() - 1) < 1e-12)
print("\nHandrechnung Sektor-Proxy OK an allen Tagen:", all(checks))

# --- Hauptmodul: Monatsrenditen -> Tagesraster, Kette = Produkt, Gewicht = 1 an erstem Kurstag
mon = pd.DataFrame({M.BETA_COL: [0.01, -0.02, 0.03, 0.005], M.VAR_COL: [0.0, 0.0, 0.0, 0.0]},
                   index=pd.date_range("2005-01-01", periods=4, freq="MS"))
grid = pd.date_range("2005-01-03", "2005-05-31", freq=NYSE_BDAY)
p = M.load.__globals__["panel_from_returns"](M.monthly_to_month_end_grid(mon, grid))
px = p.close[M.BETA_COL].dropna()
print("\nHauptmodul Kette: Modul-Kurs Monatsende Feb..May:",
      [round(float(px[px.index.is_month_end | (px.index == px.index[px.index.to_period('M').duplicated(keep=False)][0])].iloc[0]), 4)] if False else "")
ends_model = px.groupby(px.index.to_period("M")).last()
print("  Monatsend-Kurse:", ends_model.round(4).to_dict())
print("  erwartet Kette Jan..Apr relativ:", np.round(np.cumprod([1, 1.01, 1.01 * 0.98, 1.01 * 0.98 * 1.03]), 6).tolist())
print("  Modul relativ (Monatsende):", np.round(ends_model.to_numpy() / ends_model.to_numpy()[0], 6).tolist())
w_main = M.weights(p)
print("  Hauptmodul Gewichte:", w_main.to_dict("list"), " erster Kurstag:", px.index[0].date())

# --- Faktor-Alpha (Abbruchkriterium Stichprobe nach 2008), aus French-Cache/Projektdatenzugriff
out = M.alpha_split_from_french()
for k in ("full", "pre", "post"):
    print(f"Alpha {k}: {out[k]}")
