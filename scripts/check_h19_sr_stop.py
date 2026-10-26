"""H19: Struktur-Stop an Swing-Lows (Support-/Liquiditaetszonen) und Swing-Low-Trail (docs/HYPOTHESEN.md, Eintrag H19).

Je Markt ein Sleeve (sleeve4), Entscheidung und Ausfuehrung wie sleeve3 aus H13 (Monats-MA12-Zustand, Ausfuehrung
Schluss Folgetag, 10 bp je Seite, Cash = US-RF). Neu sind nur die Stops:
  * Pivot-Tief am Tag p: Schlusskurs c[p] <= alle Schlusskurse in p-k..p+k (k = 10). Bestaetigung erst am Tag p+k.
  * Zone L = Pivot-Tief-Niveau, Stop-Niveau = L - buf x ATR (buf = 0,5; ATR = Mittel von |Delta Schlusskurs| ueber 14 Tage).
  * "sr_stop":  Beim Einstieg (E = Schluss des Tages vor der Ausfuehrung) wird das juengste bestaetigte Pivot-Tief mit
                L < E und Pivot-Tag >= f - 120 gesucht (f = Entscheidungstag). Anfangs-Stop S0 = L - buf x ATR_f.
                Abstand d = E - S0, begrenzt auf [1R, 4R], R = m x sigma_f / Wurzel(12) x E (m = 2, wie H13).
                Ohne Pivot-Tief gilt d = 1R. Der Stop bleibt dann fest.
  * "sr_trail": wie sr_stop, zusaetzlich wird am Tag t ein neues Pivot-Tief bestaetigt (Pivot-Tag t-k), ist der
                Kandidat L - buf x ATR_t; Stop = max(Stop, Kandidat). Der Stop sinkt nie.
Schliesst der Kurs am Tag t unter dem Stop, Ausstieg zum Schluss von t+1 (pos ab t+2 = 0); Wiedereinstieg nur am
naechsten Monatsende mit Signal LONG. Der Monatsfilter steigt unabhaengig davon aus.
Kriterium (a) bis (f) wie H13, gegen base1x.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
import pandas as pd

import check_h12_robust_basket as h12
import check_h13_ratchet_stop as h13
import check_trend_portfolio as tp
import check_trend_vt_basket as vt
from qlab.calendar import month_end_flags
from qlab.data import risk_free_daily

TRADING_DAYS = 252
SQRT12 = float(np.sqrt(12.0))
OUT_DIR = ROOT / "results"
OUT_STATS = OUT_DIR / "H19_sr_stop.csv"
OUT_RET = OUT_DIR / "H19_basket_returns.csv"
FIRST_HALF = vt.FIRST_HALF
SECOND_HALF = vt.SECOND_HALF

NEW_RUNS = ["sr_stop", "sr_trail"]


def pivot_lows(close: pd.Series, k: int = 10):
    """Pivot-Tiefs nach H19. Gibt (level, conf) zurueck.

    level[i] = Schlusskurs am Tag i, wenn c[i] <= alle c[j] fuer j in [i-k, i+k], sonst NaN.
    conf[i] = i + k: der Tag, ab dem das Pivot bei i als bekannt gilt (Bestaetigung). Vor conf[i] darf level[i]
    nicht benutzt werden; das stellt der Aufrufer (sleeve4) sicher.
    """
    s = pd.Series(np.asarray(close, dtype=float))
    win_min = s.rolling(2 * k + 1, center=True, min_periods=2 * k + 1).min().to_numpy()
    c = s.to_numpy()
    level = np.where(c <= win_min, c, np.nan)     # NaN-Vergleiche ergeben False -> NaN
    conf = np.arange(len(c)) + k
    return level, conf


def atr_proxy(close: pd.Series, n: int = 14) -> pd.Series:
    """Mittel von |Delta Schlusskurs| ueber die letzten n Tage (nur Daten bis zum jeweiligen Tag)."""
    return close.astype(float).diff().abs().rolling(n).mean()


def sleeve4(close: pd.Series, rf: pd.Series, *, stop_mode: str | None = None, m: float = 2.0, k: int = 10,
            buf: float = 0.5, lookback: int = 120, clamp: tuple = (1.0, 4.0), bps: float = 10.0) -> pd.DataFrame:
    """Ein Markt-Sleeve nach H19 (siehe Modul-Docstring). Gibt ret, pos, stop je Handelstag ab dem Sleeve-Start zurueck.

    stop_mode=None ist exakt sleeve3(stop_mode=None) aus H13.
    """
    if stop_mode not in (None, "sr_stop", "sr_trail"):
        raise ValueError(f"unbekannte stop_mode: {stop_mode}")
    close = close.astype(float)
    idx = close.index
    r = close.pct_change(fill_method=None)
    sigma = np.sqrt((r ** 2).ewm(halflife=20, adjust=False).mean() * TRADING_DAYS)

    state = vt.monthly_state(close)
    if state.empty:
        raise ValueError("kein gueltiger Monatszustand (zu wenige Monatsenden mit MA12)")
    s_i = idx.get_loc(state.index[0])
    flags = month_end_flags(idx).to_numpy()
    st = state.reindex(idx).fillna(False).to_numpy(bool)
    sig = sigma.to_numpy(float)
    c = close.to_numpy(float)
    r0 = np.nan_to_num(r.to_numpy(float))
    rf_a = rf.reindex(idx).ffill().fillna(0.0).to_numpy(float)
    atr = atr_proxy(close).to_numpy(float)
    piv, _ = pivot_lows(close, k)

    def find_pivot(f: int, E: float):
        """Juengstes bestaetigtes Pivot-Tief (Bestaetigung <= f, Pivot-Tag >= f - lookback) mit L < E, sonst None."""
        lo = max(f - lookback, 0)
        for p in range(f - k, lo - 1, -1):
            if np.isfinite(piv[p]) and piv[p] < E:
                return float(piv[p])
        return None

    n = len(idx)
    pos = np.zeros(n)
    stop_arr = np.full(n, np.nan)
    chg: dict[int, tuple[float, float, int]] = {}      # Tag -> (Gewicht, sigma_f, f)
    cur = 0.0
    stopped = False
    E = R = stop = np.nan
    for i in range(s_i, n):
        if i in chg:
            w_new, sig_dec, f = chg.pop(i)
            if w_new > 0 and cur == 0.0:               # Einstieg: Ausfuehrung am Schluss von i-1
                E = c[i - 1]
                R = m * sig_dec / SQRT12 * E if np.isfinite(sig_dec) else np.nan
                if stop_mode is not None and np.isfinite(R) and R > 0:
                    L = find_pivot(f, E) if np.isfinite(atr[f]) else None
                    if L is None:
                        dist = R
                    else:
                        S0 = L - buf * atr[f]
                        dist = min(max(E - S0, clamp[0] * R), clamp[1] * R)
                    stop = E - dist
                else:
                    stop = np.nan
            cur = w_new
        pos[i] = cur

        trig = False
        if cur > 0 and not stopped and stop_mode is not None and np.isfinite(stop):
            if stop_mode == "sr_trail" and i - k >= 0 and np.isfinite(piv[i - k]) and np.isfinite(atr[i]):
                cand = piv[i - k] - buf * atr[i]        # Pivot-Tag i-k, am Tag i bestaetigt
                stop = max(stop, cand)
            stop_arr[i] = stop
            if c[i] < stop:
                trig = True
                chg[i + 2] = (0.0, np.nan, i)           # Ausstieg: Schluss t+1, pos ab t+2 = 0
                stopped = True

        if not trig and flags[i]:
            w = 1.0 if (st[i] and np.isfinite(sig[i]) and sig[i] > 0) else 0.0
            if not stopped:
                chg[i + 2] = (w, sig[i], i)
            elif w > 0:                                 # Wiedereinstieg am naechsten Monatsende mit LONG
                chg[i + 2] = (w, sig[i], i)
                stopped = False

    p = pos[s_i:]
    prev = np.concatenate([[0.0], p[:-1]])
    ret = p * r0[s_i:] + (1.0 - p) * rf_a[s_i:] - np.abs(p - prev) * bps / 1e4
    return pd.DataFrame({"ret": ret, "pos": p, "stop": stop_arr[s_i:]}, index=idx[s_i:])


RUNS = {
    "base1x": (h13.sleeve3, dict(stop_mode=None)),
    "steps": (h13.sleeve3, dict(stop_mode="steps")),          # H13-Referenz
    "sr_stop": (sleeve4, dict(stop_mode="sr_stop")),
    "sr_trail": (sleeve4, dict(stop_mode="sr_trail")),
}


def main() -> None:
    print(f"H19 Struktur-Stop (Swing-Lows): {len(vt.MARKETS)} Maerkte, ohne Hebel, Auswertung bis {vt.END}, "
          f"{vt.BPS:.0f} bp je Wechsel, Ausfuehrung Schluss Folgetag, Cash = US-RF, ohne Steuer\n")
    names = ["bh"] + list(RUNS)
    RET = {k: {} for k in names}
    skipped = []
    for t in vt.MARKETS:
        try:
            close = vt.load_market(t)
            rf = risk_free_daily(close.index)
            res = {name: fn(close, rf, **kw) for name, (fn, kw) in RUNS.items()}
        except Exception as exc:
            print(f"[{t}] uebersprungen: {exc}")
            skipped.append(t)
            continue
        s = res["base1x"].index[0]
        RET["bh"][t] = close.pct_change(fill_method=None).loc[s:].fillna(0.0)
        for name in RUNS:
            RET[name][t] = res[name]["ret"]
    print(f"Maerkte mit Daten: {len(RET['bh'])} von {len(vt.MARKETS)}; uebersprungen: {skipped or 'keine'}\n")

    baskets = {name: tp.basket(pd.DataFrame(RET[name]), vt.MIN_MARKETS) for name in names}
    common = None
    for name in names:
        ix = baskets[name][0].index
        common = ix if common is None else common.intersection(ix)
    R = pd.DataFrame({name: baskets[name][0].reindex(common) for name in names})
    rf_c = risk_free_daily(common)
    print(f"Gemeinsamer Index: {common[0].date()} bis {common[-1].date()}, {len(common)} Handelstage\n")

    K = {name: h12.konstanz(R[name], rf_c) for name in names}
    print("(1) Kennzahlen je Korb (ganzer Zeitraum):")
    print(h12._table(K, names).to_string())
    halves = {}
    for lab, (a, b) in [("1991-2006", FIRST_HALF), ("2007-2022", SECOND_HALF)]:
        halves[lab] = {name: h12.konstanz(R[name].loc[a:b], rf_c.loc[a:b]) for name in names}
        print(f"\n(2) Haelfte {lab}:")
        print(h12._table(halves[lab], names).to_string())
    sp = {}
    if "^GSPC" in RET["bh"]:
        sp_rf = risk_free_daily(RET["bh"]["^GSPC"].index)
        sp = {name: h12.konstanz(RET[name]["^GSPC"], sp_rf) for name in names}
        print(f"\n(3) S&P 500 allein (ab {RET['bh']['^GSPC'].index[0].date()}):")
        print(h12._table(sp, names).to_string())

    B = K["base1x"]
    print("\n(4) Kriterien H19 gegen base1x:")
    verdict = {}
    for name in NEW_RUNS:
        V = K[name]
        a = V["max_dd"] - B["max_dd"] >= 0.01
        b = V["cagr"] >= B["cagr"] - 0.005
        c_ = V["sharpe"] >= B["sharpe"]
        d = V["upi"] >= B["upi"]
        e = (halves["1991-2006"][name]["upi"] >= halves["1991-2006"]["base1x"]["upi"]
             and halves["2007-2022"][name]["upi"] >= halves["2007-2022"]["base1x"]["upi"])
        f = bool(sp) and sp[name]["upi"] >= sp["base1x"]["upi"]
        verdict[name] = all([a, b, c_, d, e, f])
        print(f"  {name:<14} (a) MaxDD {h12._pct(V['max_dd'])} ({(V['max_dd'] - B['max_dd']) * 100:+.2f} Pp) {h12._lab(a)} | "
              f"(b) CAGR {h12._pct(V['cagr'])} ({(V['cagr'] - B['cagr']) * 100:+.2f} Pp) {h12._lab(b)} | "
              f"(c) Sharpe {h12._num(V['sharpe'], '{:.3f}')} vs {h12._num(B['sharpe'], '{:.3f}')} {h12._lab(c_)} | "
              f"(d) UPI {h12._num(V['upi'], '{:.3f}')} vs {h12._num(B['upi'], '{:.3f}')} {h12._lab(d)} | "
              f"(e) Haelften UPI {h12._lab(e)} | (f) S&P-UPI {h12._lab(f)} -> gesamt {h12._lab(verdict[name])}")

    rows = []
    for scope, KK in [("ganz", K), ("1991-2006", halves["1991-2006"]), ("2007-2022", halves["2007-2022"])] + (
            [("S&P allein", sp)] if sp else []):
        for nme in names:
            rows.append({"Serie": nme, "Abschnitt": scope, **KK[nme]})
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT_STATS, index=False, encoding="utf-8", float_format="%.6f")
    rb = R.copy()
    rb.index.name = "date"
    rb.reset_index().assign(date=lambda d: d["date"].dt.date.astype(str)).to_csv(
        OUT_RET, index=False, encoding="utf-8", float_format="%.10f")
    print(f"\nCSV gespeichert: {OUT_STATS}")
    print(f"CSV gespeichert: {OUT_RET}")


if __name__ == "__main__":
    main()
