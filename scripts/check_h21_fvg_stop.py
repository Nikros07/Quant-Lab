"""H21: Fair-Value-Gap-Stop (FVG) als Struktur-Stop (docs/HYPOTHESEN.md, Eintrag H21).

Je Markt ein Sleeve (sleeve5). Entscheidung und Ausfuehrung wie sleeve3 aus H13 (Monats-MA12-Zustand, Ausfuehrung
Schluss Folgetag, 10 bp je Seite, Cash = US-RF). Neu sind nur die Stops aus Tages-OHLC:
  * Bullische FVG am Tag t (bekannt zum Schluss von t): Low[t] > High[t-2]. Zone = [unten High[t-2], oben Low[t]].
    Groesse = oben - unten; zaehlt nur, wenn Groesse >= 0,25 x ATR_t (ATR14 = Mittel der True Range).
  * Mitigiert ab dem ersten Tag u > t, an dem der Schlusskurs unter dem unteren Rand liegt.
  * "fvg_stop": Beim Einstieg (E = Schluss des Tages vor der Ausfuehrung) wird unter den am Entscheidungstag f aktiven
    (in den letzten 120 Tagen entstanden, bis f nicht mitigiert) bullischen FVGs mit oberem Rand < E diejenige mit dem
    hoechsten unteren Rand gewaehlt. S0 = unten - 0,5 x ATR_f. Abstand d = E - S0, begrenzt auf [1R, 4R],
    R = 2 x sigma_f / Wurzel(12) x E. Ohne FVG gilt d = 1R. Der Stop bleibt fest.
  * "fvg_trail": wie fvg_stop; zusaetzlich entsteht am Tag t in der Position eine neue zaehlende bullische FVG,
    ist der Kandidat unten - 0,5 x ATR_t; Stop = max(Stop, Kandidat). Der Stop sinkt nie.
Schliesst der Kurs am Tag t unter dem Stop, Ausstieg zum Schluss von t+1 (pos ab t+2 = 0); Wiedereinstieg nur am
naechsten Monatsende mit Signal LONG. Der Monatsfilter steigt unabhaengig davon aus.

Daten: load_ohlc(t) liefert den Schlusskurs-Verlauf von vt.load_market(t) plus High/Low auf demselben Index.
Fuer ^GSPC gibt es OHLC nur ab dem Cache-Start; dort wird der Zeitraum auf den OHLC-Start gekuerzt (informativ).
Kriterium (a) bis (f) wie H13 und H19, gegen base1x.
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
from qlab.data import load_ticker, risk_free_daily

TRADING_DAYS = 252
SQRT12 = float(np.sqrt(12.0))
OUT_DIR = ROOT / "results"
OUT_STATS = OUT_DIR / "H21_fvg_stop.csv"
OUT_RET = OUT_DIR / "H21_basket_returns.csv"
FIRST_HALF = vt.FIRST_HALF
SECOND_HALF = vt.SECOND_HALF

ATR_N = 14
MIN_ATR = 0.25
BUF = 0.5
LOOKBACK = 120
NEW_RUNS = ["fvg_stop", "fvg_trail"]
RUN_MODES = {"base1x": None, "fvg_stop": "fvg_stop", "fvg_trail": "fvg_trail"}


def load_ohlc(t: str) -> pd.DataFrame:
    """Schlusskurs-Reihe wie vt.load_market(t), dazu High und Low auf demselben Index.

    * Close: exakt vt.load_market(t).
    * High/Low: auf den Close-Index gelegt, ffill(limit=5) (wie der Schluss), fehlende Werte mit Close aufgefuellt.
    * ^GSPC: Close-Langreihe ab 1927, OHLC nur ab Cache-Start. Der Close wird auf den OHLC-Start gekuerzt.
    """
    close = vt.load_market(t)
    raw = load_ticker(t, start=vt.LOAD_START)
    if t == "^GSPC":
        close = close.loc[raw.index[0]:]
    h = raw["High"].reindex(close.index).ffill(limit=5).fillna(close)
    lo = raw["Low"].reindex(close.index).ffill(limit=5).fillna(close)
    return pd.DataFrame({"Close": close, "High": h, "Low": lo}, index=close.index)


def atr_ohlc(high: pd.Series, low: pd.Series, close: pd.Series, n: int = ATR_N) -> pd.Series:
    """Mittel der True Range max(H-L, |H-C_vor|, |L-C_vor|) ueber n Tage (nur Daten bis zum jeweiligen Tag)."""
    prev = close.shift(1)
    tr = pd.concat([high - low, (high - prev).abs(), (low - prev).abs()], axis=1).max(axis=1, skipna=True)
    return tr.rolling(n).mean()


def fvg_events(high: pd.Series, low: pd.Series, close: pd.Series, atr_n: int = ATR_N,
               min_atr: float = MIN_ATR) -> pd.DataFrame:
    """Bullische Fair-Value-Gaps je Tag t (siehe Modul-Docstring).

    Spalten: lower (= High[t-2]), upper (= Low[t]), size, atr (ATR_t), bullish (Low[t] > High[t-2]),
    valid (bullisch und size >= min_atr x ATR_t, das ist die zaehlende FVG), mit (Position des ersten Tages u > t mit
    Schluss unter lower, NaN = nicht mitigiert).
    Causal: valid und lower/upper/atr an Tag t haengen nur von Daten bis t ab. Die Spalte mit nutzt der Aufrufer nur
    als Vergleich 'mit > f' fuer den Entscheidungstag f.
    """
    high = high.astype(float)
    low = low.astype(float)
    close = close.astype(float)
    lower = high.shift(2)
    upper = low
    size = upper - lower
    bullish = upper > lower
    atr = atr_ohlc(high, low, close, atr_n)
    valid = bullish & (size >= min_atr * atr)
    c = close.to_numpy(float)
    lo_a = lower.to_numpy(float)
    mit = np.full(len(c), np.nan)
    for t in np.flatnonzero(valid.to_numpy(bool)):
        if t + 1 >= len(c):
            continue
        hit = np.flatnonzero(c[t + 1:] < lo_a[t])
        if hit.size:
            mit[t] = t + 1 + hit[0]
    return pd.DataFrame({"lower": lower, "upper": upper, "size": size, "atr": atr, "bullish": bullish,
                         "valid": valid, "mit": mit}, index=high.index)


def sleeve5(close: pd.Series, high: pd.Series, low: pd.Series, rf: pd.Series, *, stop_mode: str | None = None,
            m: float = 2.0, buf: float = BUF, lookback: int = LOOKBACK, clamp: tuple = (1.0, 4.0),
            bps: float = 10.0, info: dict | None = None) -> pd.DataFrame:
    """Ein Markt-Sleeve nach H21 (siehe Modul-Docstring). Gibt ret, pos, stop je Handelstag ab dem Sleeve-Start zurueck.

    stop_mode=None ist exakt sleeve3(stop_mode=None) aus H13 auf demselben Schlusskurs.
    info (optional, dict): wird mit 'entries' (Einstiege mit Stop-Logik) und 'no_fvg' (davon ohne FVG) gefuellt.
    """
    if stop_mode not in (None, "fvg_stop", "fvg_trail"):
        raise ValueError(f"unbekannte stop_mode: {stop_mode}")
    close = close.astype(float)
    idx = close.index
    high = high.astype(float).reindex(idx)
    low = low.astype(float).reindex(idx)
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

    fv = fvg_events(high, low, close)
    fv_ok = fv["valid"].to_numpy(bool)
    fv_lo = fv["lower"].to_numpy(float)
    fv_up = fv["upper"].to_numpy(float)
    fv_atr = fv["atr"].to_numpy(float)
    fv_mit = fv["mit"].to_numpy(float)

    def find_fvg(f: int, E: float):
        """Unteres Rand der aktiven, unmitigierten bullischen FVG mit oberem Rand < E (hoechster unterer Rand), sonst None."""
        lo = max(f - lookback, 0)
        best = None
        for t in range(f, lo - 1, -1):
            if not fv_ok[t]:
                continue
            if not (np.isnan(fv_mit[t]) or fv_mit[t] > f):      # bis f mitigiert
                continue
            if fv_up[t] < E and (best is None or fv_lo[t] > best):
                best = fv_lo[t]
        return best

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
                if stop_mode is not None:
                    if info is not None:
                        info["entries"] = info.get("entries", 0) + 1
                    if np.isfinite(R) and R > 0:
                        lo_f = find_fvg(f, E) if np.isfinite(fv_atr[f]) else None
                        if lo_f is None:
                            dist = R
                            if info is not None:
                                info["no_fvg"] = info.get("no_fvg", 0) + 1
                        else:
                            S0 = lo_f - buf * fv_atr[f]
                            dist = min(max(E - S0, clamp[0] * R), clamp[1] * R)
                        stop = E - dist
                    else:
                        stop = np.nan
                else:
                    stop = np.nan
            cur = w_new
        pos[i] = cur

        trig = False
        if cur > 0 and not stopped and stop_mode is not None and np.isfinite(stop):
            if stop_mode == "fvg_trail" and fv_ok[i]:
                stop = max(stop, fv_lo[i] - buf * fv_atr[i])   # neue zaehlende FVG am Tag i
            stop_arr[i] = stop
            if c[i] < stop:
                trig = True
                chg[i + 2] = (0.0, np.nan, i)                  # Ausstieg: Schluss t+1, pos ab t+2 = 0
                stopped = True

        if not trig and flags[i]:
            w = 1.0 if (st[i] and np.isfinite(sig[i]) and sig[i] > 0) else 0.0
            if not stopped:
                chg[i + 2] = (w, sig[i], i)
            elif w > 0:                                # Wiedereinstieg am naechsten Monatsende mit LONG
                chg[i + 2] = (w, sig[i], i)
                stopped = False

    p = pos[s_i:]
    prev = np.concatenate([[0.0], p[:-1]])
    ret = p * r0[s_i:] + (1.0 - p) * rf_a[s_i:] - np.abs(p - prev) * bps / 1e4
    return pd.DataFrame({"ret": ret, "pos": p, "stop": stop_arr[s_i:]}, index=idx[s_i:])


def main() -> None:
    print(f"H21 Fair-Value-Gap-Stop: {len(vt.MARKETS)} Maerkte, ohne Hebel, Auswertung bis {vt.END}, "
          f"{vt.BPS:.0f} bp je Wechsel, Ausfuehrung Schluss Folgetag, Cash = US-RF, ohne Steuer\n")
    names = ["bh"] + list(RUN_MODES)
    RET = {k: {} for k in names}
    skipped = []
    devs = []
    fvg_rows = []
    for t in vt.MARKETS:
        try:
            ohlc = load_ohlc(t)
            close, high, low = ohlc["Close"], ohlc["High"], ohlc["Low"]
            rf = risk_free_daily(close.index)
            res, infos = {}, {}
            for name, mode in RUN_MODES.items():
                infos[name] = {}
                res[name] = sleeve5(close, high, low, rf, stop_mode=mode, info=infos[name])
            ref_close = vt.load_market(t)
            ref = h13.sleeve3(ref_close, risk_free_daily(ref_close.index), stop_mode=None)
        except Exception as exc:
            print(f"[{t}] uebersprungen: {exc}")
            skipped.append(t)
            continue
        s = res["base1x"].index[0]
        common_idx = res["base1x"].index.intersection(ref.index)
        d = float(np.abs(res["base1x"].loc[common_idx, "ret"].to_numpy()
                         - ref.loc[common_idx, "ret"].to_numpy()).max()) if len(common_idx) else np.nan
        devs.append((t, len(common_idx), d))
        RET["bh"][t] = close.pct_change(fill_method=None).loc[s:].fillna(0.0)
        for name in RUN_MODES:
            RET[name][t] = res[name]["ret"]
        fv = fvg_events(high, low, close).loc[s:]
        fvg_rows.append({"Markt": t, "FVG bullisch (roh)": int(fv["bullish"].sum()),
                         "FVG zaehlend (>= 0,25 ATR)": int(fv["valid"].sum()),
                         "Einstiege fvg_stop": infos["fvg_stop"]["entries"],
                         "davon ohne FVG fvg_stop": infos["fvg_stop"].get("no_fvg", 0),
                         "Einstiege fvg_trail": infos["fvg_trail"]["entries"],
                         "davon ohne FVG fvg_trail": infos["fvg_trail"].get("no_fvg", 0)})
    print(f"Maerkte mit Daten: {len(RET['bh'])} von {len(vt.MARKETS)}; uebersprungen: {skipped or 'keine'}\n")

    print("(0) Pruefung sleeve5(None) gegen sleeve3(None) auf vt.load_market(t), je Markt (Renditen am gemeinsamen Tag):")
    for t, nd, dv in devs:
        print(f"  {t:<10} {nd:>6} Tage   max |Differenz| = {dv:.3e}")
    dev_all = max([dv for _, _, dv in devs if np.isfinite(dv)] or [np.nan])
    print(f"  gesamt: max |Differenz| = {dev_all:.3e}  "
          f"({'identisch innerhalb 1e-12' if dev_all < 1e-12 else 'ABWEICHUNG, siehe Bericht'})\n")

    fvg_df = pd.DataFrame(fvg_rows)
    print("(0b) FVGs und Einstiege ohne FVG je Markt (ab Sleeve-Start; Einstiege = Einstiege mit Stop-Logik):")
    print(fvg_df.to_string(index=False))
    tot = fvg_df.drop(columns=["Markt"]).sum()
    share_s = tot["davon ohne FVG fvg_stop"] / max(tot["Einstiege fvg_stop"], 1)
    share_t = tot["davon ohne FVG fvg_trail"] / max(tot["Einstiege fvg_trail"], 1)
    print(f"  Gesamt: Anteil Einstiege ohne FVG fvg_stop {share_s * 100:.1f} % "
          f"({int(tot['davon ohne FVG fvg_stop'])} von {int(tot['Einstiege fvg_stop'])}), "
          f"fvg_trail {share_t * 100:.1f} % ({int(tot['davon ohne FVG fvg_trail'])} von {int(tot['Einstiege fvg_trail'])})\n")

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
        print(f"\n(3) S&P 500 allein (nur OHLC-Zeitraum ab {RET['bh']['^GSPC'].index[0].date()}, informativ):")
        print(h12._table(sp, names).to_string())

    B = K["base1x"]
    print("\n(4) Kriterien H21 gegen base1x:")
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
