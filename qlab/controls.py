"""Pflicht-Konkurrenten: jede Strategie muss diese schlagen, sonst ist sie nichts wert."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .data import Panel


from .calendar import month_end_dates  # noqa: E402  (kausal, nicht aus Daten abgeleitet)


def buy_and_hold(panel: Panel, ticker: str) -> pd.DataFrame:
    first = panel.close[ticker].first_valid_index()
    return pd.DataFrame({ticker: [1.0]}, index=[first])


def fixed_mix(panel: Panel, weights: dict[str, float], rebalance: str = "monthly") -> pd.DataFrame:
    """Feste Gewichte, monatlich (oder jährlich) zurückgestellt."""
    dates = month_end_dates(panel.close.index)
    if rebalance == "annual":
        dates = dates[dates.month == 12]
    valid = panel.close[list(weights)].dropna().index
    dates = dates[dates.isin(valid)]
    return pd.DataFrame({t: [w] * len(dates) for t, w in weights.items()}, index=dates)


def random_monthly(panel: Panel, k: int, seed: int, tickers: list[str] | None = None) -> pd.DataFrame:
    """Nullmodell: jeden Monat k zufällige Titel gleichgewichtet. Zeigt das Rauschniveau."""
    rng = np.random.default_rng(seed)
    tickers = tickers or panel.tickers
    dates = month_end_dates(panel.close.index)
    rows = []
    for d in dates:
        avail = [t for t in tickers if np.isfinite(panel.close.at[d, t])]
        if len(avail) < k:
            continue
        pick = rng.choice(avail, size=k, replace=False)
        rows.append(pd.Series({t: 1.0 / k for t in pick}, name=d))
    return pd.DataFrame(rows).fillna(0.0) if rows else pd.DataFrame(columns=tickers)
