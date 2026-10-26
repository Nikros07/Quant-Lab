"""Kennzahlen aus Tagesrenditen."""
from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


def sharpe_daily(ret: pd.Series | np.ndarray, rf: pd.Series | np.ndarray | float = 0.0) -> float:
    """Nicht annualisierte Sharpe (pro Tag), Überrendite zum risikolosen Zins."""
    r = np.asarray(ret, float) - (np.asarray(rf, float) if not np.isscalar(rf) else rf)
    r = r[np.isfinite(r)]
    if len(r) < 3:
        return float("nan")
    sd = r.std(ddof=1)
    return float(r.mean() / sd) if sd > 0 else float("nan")


def periods_per_year(idx: pd.DatetimeIndex) -> float:
    """Beobachtungen pro Kalenderjahr (252 bei normalen Börsentagen, ~263 bei alten French-Daten
    mit Samstagen). Annualisierung muss damit rechnen, nicht mit festen 252."""
    years = (idx[-1] - idx[0]).days / 365.25
    return len(idx) / years if years > 0 else float(TRADING_DAYS)


def drawdown(nav: pd.Series) -> pd.Series:
    return nav / nav.cummax() - 1.0


def underwater_days(nav: pd.Series) -> int:
    dd = drawdown(nav)
    longest = cur = 0
    for v in (dd.to_numpy() < -1e-12):
        cur = cur + 1 if v else 0
        longest = max(longest, cur)
    return longest


def summarize(ret: pd.Series, rf: pd.Series | None = None, turnover: pd.Series | None = None,
              cost: pd.Series | None = None, bench: pd.Series | None = None,
              exposure: pd.Series | None = None) -> dict:
    ret = ret.dropna()
    if len(ret) < 30:
        return {"n_days": int(len(ret))}
    rf_ = rf.reindex(ret.index).fillna(0.0) if rf is not None else pd.Series(0.0, index=ret.index)
    nav = (1 + ret).cumprod()
    ppy = periods_per_year(ret.index)
    years = len(ret) / ppy
    cagr = float(nav.iloc[-1] ** (1 / years) - 1) if nav.iloc[-1] > 0 else -1.0
    vol = float(ret.std(ddof=1) * np.sqrt(ppy))
    ex = ret - rf_
    sr = float(ex.mean() / ex.std(ddof=1) * np.sqrt(ppy)) if ex.std(ddof=1) > 0 else float("nan")
    down = ex[ex < 0]
    sortino = float(ex.mean() / np.sqrt((down ** 2).sum() / max(len(ex) - 1, 1)) * np.sqrt(ppy)) if len(down) > 2 else float("nan")
    dd = drawdown(nav)
    maxdd = float(dd.min())
    yearly = (1 + ret).groupby(ret.index.year).prod() - 1
    out = {
        "n_days": int(len(ret)), "years": round(years, 2),
        "cagr": cagr, "vol": vol, "sharpe": sr, "sortino": sortino,
        "max_dd": maxdd, "calmar": float(cagr / abs(maxdd)) if maxdd < 0 else float("nan"),
        "worst_year": float(yearly.min()), "best_year": float(yearly.max()),
        "pos_years": float((yearly > 0).mean()),
        "underwater_days": underwater_days(nav),
        "skew": float(ret.skew()), "kurt": float(ret.kurt() + 3.0),  # nicht-excess
        "total_return": float(nav.iloc[-1] - 1),
    }
    if turnover is not None:
        t = turnover.reindex(ret.index).fillna(0.0)
        out["turnover_per_year"] = float(t.sum() / years)
    if cost is not None:
        c = cost.reindex(ret.index).fillna(0.0)
        out["cost_drag_per_year"] = float(c.sum() / years)
    if exposure is not None:
        out["avg_gross"] = float(exposure.reindex(ret.index).mean())
    if bench is not None:
        b = bench.reindex(ret.index).dropna()
        r = ret.reindex(b.index)
        if len(b) > 60 and b.std() > 0:
            beta = float(np.cov(r, b, ddof=1)[0, 1] / b.var(ddof=1))
            out["beta"] = beta
            out["corr"] = float(np.corrcoef(r, b)[0, 1])
            alpha_d = float((r - rf_.reindex(b.index)).mean() - beta * (b - rf_.reindex(b.index)).mean())
            out["alpha_ann"] = alpha_d * ppy
    return out


def rolling_window_table(ret: pd.Series, bench: pd.Series, window_years: int = 5,
                         step_months: int = 6) -> dict:
    """Anteil der rollierenden Fenster, in denen die Strategie die Benchmark nach CAGR schlägt."""
    ret = ret.dropna()
    bench = bench.reindex(ret.index).fillna(0.0)
    ppy = periods_per_year(ret.index)
    w = int(window_years * ppy)
    if len(ret) < w + 10:
        return {"windows": 0}
    step = int(step_months * ppy / 12)
    wins, diffs = 0, []
    for s in range(0, len(ret) - w, step):
        a = (1 + ret.iloc[s:s + w]).prod() ** (1 / window_years) - 1
        b = (1 + bench.iloc[s:s + w]).prod() ** (1 / window_years) - 1
        diffs.append(a - b)
        wins += a > b
    return {"windows": len(diffs), "share_beating": wins / len(diffs), "median_excess_cagr": float(np.median(diffs))}
