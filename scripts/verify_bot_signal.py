"""Vergleicht das Signal des Bots (SPY-Preisreihe, wie Alpaca sie liefert) mit dem getesteten
Lab-Signal (S&P-500-Preisindex ^GSPC) an jedem Monatsende seit 1994.

Yahoo: auto_adjust=False -> 'Close' ist nur splitbereinigt (ohne Dividenden), also dieselbe Art Preisreihe
wie Alpacas adjustment=split.
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "deploy" / "alpaca-bot"))

import pandas as pd
import yfinance as yf

from qlab.data import load_panel
from strategies import trend_ma12_us_equity_cash_etf as m
from trendbot.signal import DataError, decide

spy = yf.Ticker("SPY").history(start="1993-01-01", auto_adjust=False, actions=False)
spy.index = pd.to_datetime(spy.index).tz_localize(None).normalize()
bars_all = [(d.date().isoformat(), float(c)) for d, c in spy["Close"].dropna().items()]

panel = load_panel(m.SPEC["tickers"], start=m.SPEC["start"])
lab = m.weights(panel)["SPY"]                      # 1.0 / 0.0 an jedem Monatsende
rows, mism = [], []
for d, v in lab.items():
    if d < pd.Timestamp("1994-02-01"):
        continue
    # "heute" = erster Kalendertag des Folgemonats; Bot sieht nur Kurse bis zu diesem Tag
    today = date(d.year + (d.month == 12), 1 if d.month == 12 else d.month + 1, 1)
    upto = [b for b in bars_all if b[0] <= today.isoformat()]
    try:
        s = decide(upto, today, 12)
    except DataError as exc:
        rows.append((d.date(), "FEHLER", str(exc)[:50]))
        continue
    rows.append((d.date(), s.on, bool(v)))
    if s.on != bool(v):
        mism.append((d.date().isoformat(), "Bot " + ("ON" if s.on else "OFF"), "Lab " + ("ON" if v else "OFF"), f"{s.distance * 100:+.2f}%"))

n = len(rows)
errs = [r for r in rows if r[1] == "FEHLER"]
print(f"Monatsenden verglichen: {n}, Datenfehler: {len(errs)}, Abweichungen: {len(mism)}")
for x in mism:
    print("  ", x)
for x in errs[:5]:
    print("  FEHLER", x)
