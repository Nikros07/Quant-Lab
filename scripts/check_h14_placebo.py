"""H14: Placebo-Timing des ungehebelten Korbs base1x (docs/HYPOTHESEN.md, Pruefblock P1, Eintrag H14).

Frage: Schlaegt das Monats-MA12-Timing zufaelliges Timing mit gleicher Marktzeit?

Regel (wie vorab registriert):
* Je Markt wird der echte Monatszustand (an = Monatsschluss >= Mittel der letzten 12 Monatsschluesse, sonst aus) durch
  eine zufaellige Markov-Kette ersetzt. Die Uebergangswahrscheinlichkeiten (an->aus, aus->an) werden je Markt aus dem
  echten Zustandsverlauf desselben Marktes geschaetzt (Haeufigkeit der Uebergaenge), also gleiche Marktzeit und gleiche
  Wechselhaeufigkeit im Mittel.
* Ausfuehrung und Kosten wie sleeve2/base1x: Entscheidung am Monatsende m, wirksam ab m+2, 10 bp auf |Delta pos|,
  Cash = US-RF, Start am ersten gueltigen Monatsende, gleichgewichteter Korb (basket) auf gemeinsamem Index.
* 1000 Ziehungen mit festen Seeds 0..999, je Ziehung alle 17 Maerkte. Korbkennzahlen: CAGR, MaxDD, UPI, Sharpe.
* Kriterium: Timing-Beitrag BELEGT, wenn UPI(base1x) >= 95. Perzentil der Placebo-UPI UND MaxDD(base1x) besser als
  das 75. Perzentil der Placebo-MaxDD (MaxDD mit Vorzeichen, negativ; "besser" = weniger negativ, also hoeher).
  Sonst: "Der Vorteil laesst sich nicht vom reinen Weniger-im-Markt-Sein unterscheiden".

Einfachste Lesarten (siehe auch Rueckgabe/Bericht): Anfangszustand der Kette = Ziehung aus der stationaeren
Verteilung der geschaetzten Kette (gleiche Marktzeit im Mittel); Perzentile linear interpoliert (numpy);
Vol-Skalierung entfaellt (ohne Hebel, scale = 1, nur 0 bei nicht endlicher Vol wie in sleeve2).
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
import check_trend_portfolio as tp
import check_trend_vt_basket as vt
from qlab import metrics
from qlab.calendar import month_end_flags
from qlab.data import risk_free_daily

TRADING_DAYS = 252
N_DRAWS = 1000
CHUNK = 125                      # Ziehungen je Block (Speicher begrenzen)
LENGTH = 12
BPS = 10.0
UPI_PCT = 95.0                   # Kriterium: UPI(base1x) >= 95. Perzentil der Placebos
DD_PCT = 75.0                    # Kriterium: MaxDD(base1x) besser als 75. Perzentil der Placebo-MaxDD
OUT_DIR = ROOT / "results"
OUT_SUMMARY = OUT_DIR / "H14_placebo_summary.csv"
OUT_DRAWS = OUT_DIR / "H14_placebo_draws.csv"
OUT_TRANS = OUT_DIR / "H14_placebo_markets.csv"


# ---------------------------------------------------------------------------------------------------------------
# Echter Monatszustand und Handelsplan je Markt
# ---------------------------------------------------------------------------------------------------------------
def monthly_state(close: pd.Series, length: int = LENGTH) -> pd.Series:
    """Echter Monatszustand (1.0 / 0.0) an den Monatsenden ab dem ersten gueltigen (wie sleeve2, lengths=(12,))."""
    close = close.astype(float)
    flags = month_end_flags(close.index).to_numpy()
    me = close[flags]
    ma = me.rolling(length).mean()
    st = (me >= ma).astype(float).where(ma.notna()).dropna()
    if st.empty:
        raise ValueError("kein gueltiger Monatszustand (zu wenige Monatsenden)")
    return st


def make_plan(close: pd.Series, rf: pd.Series, state: pd.Series) -> dict:
    """Alles, was nicht vom Zustand abhaengt: Tagesrenditen, Cash-Rendite, Entscheidungstage, Skalierung (wie sleeve2)."""
    close = close.astype(float)
    idx = close.index
    n = len(idx)
    r = close.pct_change(fill_method=None)
    sigma = np.sqrt((r ** 2).ewm(halflife=20, adjust=False).mean() * TRADING_DAYS).to_numpy(float)
    s_i = idx.get_loc(state.index[0])
    loc = np.array([idx.get_loc(d) for d in state.index])
    kept = loc + 2 < n                                   # wie sleeve2: Entscheidungen ohne Folgetag entfallen
    scale = np.where(np.isfinite(sigma[loc]) & (sigma[loc] > 0), 1.0, 0.0)
    return {
        "index": idx[s_i:],
        "r": np.nan_to_num(r.to_numpy(float))[s_i:],
        "rf": rf.reindex(idx).ffill().fillna(0.0).to_numpy(float)[s_i:],
        "dec_day": (loc[kept] + 2) - s_i,                # Entscheidungstage relativ zum Sleeve-Start
        "kept": kept,
        "scale": scale,
        "n_states": len(state),
    }


def sleeve_from_states(plan: dict, states: np.ndarray, bps: float = BPS) -> tuple[np.ndarray, np.ndarray]:
    """Sleeve-Renditen (K, T) und Positionen (K, T) fuer K vorgegebene Zustandsvektoren (K, M) an den Monatsenden.

    Gleiche Ausfuehrung wie sleeve2: Gewicht ab dem Tag m+2, davor 0; ret = p r + (1-p) rf - |dp| bps / 1e4.
    """
    S = np.atleast_2d(np.asarray(states, float))
    if S.shape[1] != plan["n_states"]:
        raise ValueError(f"Zustandsvektor hat {S.shape[1]} Monate, erwartet {plan['n_states']}")
    W = (S * plan["scale"][None, :])[:, plan["kept"]]
    T = len(plan["index"])
    days = np.arange(T)
    seg = np.searchsorted(plan["dec_day"], days, side="right") - 1
    if W.shape[1]:
        P = np.where(seg[None, :] >= 0, W[:, np.clip(seg, 0, None)], 0.0)
    else:
        P = np.zeros((S.shape[0], T))
    prev = np.concatenate([np.zeros((P.shape[0], 1)), P[:, :-1]], axis=1)
    ret = P * plan["r"][None, :] + (1.0 - P) * plan["rf"][None, :] - np.abs(P - prev) * bps / 1e4
    return ret, P


# ---------------------------------------------------------------------------------------------------------------
# Markov-Kette
# ---------------------------------------------------------------------------------------------------------------
def estimate_transitions(state: np.ndarray) -> tuple[float, float]:
    """(p_on_off, p_off_on) als relative Haeufigkeit der Uebergaenge im echten Zustandsverlauf.

    Gibt 0.0 zurueck, wenn der Ausgangszustand nie vorkam (0/0): die Kette bleibt dann im anderen Zustand.
    """
    s = np.asarray(state, float)
    a, b = s[:-1], s[1:]
    n_on, n_off = float((a == 1).sum()), float((a == 0).sum())
    p_on_off = float(((a == 1) & (b == 0)).sum()) / n_on if n_on > 0 else 0.0
    p_off_on = float(((a == 0) & (b == 1)).sum()) / n_off if n_off > 0 else 0.0
    return p_on_off, p_off_on


def simulate_chain(U: np.ndarray, p_on_off: float, p_off_on: float, first_state: float) -> np.ndarray:
    """Markov-Ketten (K, M) aus Gleichverteilungen U (K, M).

    Anfangszustand: stationaere Verteilung pi_on = p_off_on / (p_on_off + p_off_on) (U[:, 0] < pi_on);
    ist die Kette degeneriert (beide p = 0), gilt der echte Anfangszustand `first_state`.
    Uebergang: an bleibt an, wenn U >= p_on_off; aus wird an, wenn U < p_off_on.
    """
    K, M = U.shape
    S = np.empty((K, M))
    tot = p_on_off + p_off_on
    S[:, 0] = (U[:, 0] < p_off_on / tot).astype(float) if tot > 0 else first_state
    for t in range(1, M):
        prev = S[:, t - 1]
        S[:, t] = np.where(prev == 1.0, (U[:, t] >= p_on_off), (U[:, t] < p_off_on)).astype(float)
    return S


def draw_uniforms(seeds: np.ndarray, market_no: int, m: int) -> np.ndarray:
    """Gleichverteilungen (K, m): je Seed und Markt ein eigener Strom (feste Seeds, unabhaengig von uebersprungenen Maerkten)."""
    return np.stack([np.random.default_rng([int(s), market_no]).random(m) for s in seeds])


# ---------------------------------------------------------------------------------------------------------------
# Korb und Kennzahlen
# ---------------------------------------------------------------------------------------------------------------
def basket_from_sleeves(rets: list[tuple[pd.DatetimeIndex, np.ndarray]], min_markets: int = vt.MIN_MARKETS
                        ) -> tuple[pd.DatetimeIndex, np.ndarray]:
    """Gleichgewichteter Korb (K, Tb) aus Sleeve-Renditen (Index, (K, T)); Regeln wie tp.basket (min. Maerkte, Start,
    verworfene duenne Tage). Der Index haengt nur von den Maerkten ab, nicht von den Zustaenden."""
    union = rets[0][0]
    for ix, _ in rets[1:]:
        union = union.union(ix)
    K = rets[0][1].shape[0]
    total = np.zeros((K, len(union)))
    cnt = np.zeros(len(union))
    for ix, R in rets:
        pos = union.get_indexer(ix)
        total[:, pos] += R
        cnt[pos] += 1
    ok = cnt >= min_markets
    if not ok.any():
        raise ValueError(f"an keinem Tag {min_markets} gueltige Maerkte")
    keep = ok & (np.arange(len(union)) >= int(np.argmax(ok)))
    return union[keep], total[:, keep] / cnt[keep][None, :]


def fast_metrics(ret: np.ndarray, rf: np.ndarray, index: pd.DatetimeIndex) -> dict:
    """Vektorisierte Kennzahlen je Zeile von ret (K, T); gleiche Definitionen wie metrics.summarize / konstanz."""
    ppy = metrics.periods_per_year(index)
    years = ret.shape[1] / ppy
    nav = np.cumprod(1.0 + ret, axis=1)
    dd = nav / np.maximum.accumulate(nav, axis=1) - 1.0
    last = nav[:, -1]
    cagr = np.where(last > 0, np.abs(last) ** (1.0 / years) - 1.0, -1.0)
    ulcer = np.sqrt((dd ** 2).mean(axis=1))
    ex = ret - rf[None, :]
    sd = ex.std(axis=1, ddof=1)
    sharpe = np.where(sd > 0, ex.mean(axis=1) / np.where(sd > 0, sd, 1.0) * np.sqrt(ppy), np.nan)
    return {"cagr": cagr, "max_dd": dd.min(axis=1), "ulcer": ulcer,
            "upi": np.where(ulcer > 0, cagr / np.where(ulcer > 0, ulcer, 1.0), np.nan), "sharpe": sharpe}


def load_markets() -> tuple[list[dict], list[str]]:
    """Laedt alle Maerkte wie H12 und baut je Markt den echten Zustand und den Plan. Gibt (Liste, uebersprungen) zurueck."""
    out, skipped = [], []
    for k, t in enumerate(vt.MARKETS):
        try:
            close = vt.load_market(t)
            rf = risk_free_daily(close.index)
            state = monthly_state(close)
            plan = make_plan(close, rf, state)
        except Exception as exc:
            print(f"[{t}] keine Daten/kein Sleeve, uebersprungen: {exc}")
            skipped.append(t)
            continue
        out.append({"t": t, "no": k, "close": close, "rf": rf, "state": state.to_numpy(float), "plan": plan})
    return out, skipped


def run_placebo(markets: list[dict], seeds: np.ndarray, *, chunk: int = CHUNK) -> tuple[pd.DatetimeIndex, dict, dict]:
    """Placebo-Koerbe fuer alle Seeds. Gibt (Korbindex, Kennzahlen je Seed, Marktzeit je Markt) zurueck."""
    trans = {m["t"]: estimate_transitions(m["state"]) for m in markets}
    parts, time_on = [], {m["t"]: [] for m in markets}
    index = None
    for a in range(0, len(seeds), chunk):
        sd = seeds[a:a + chunk]
        rets = []
        for m in markets:
            p_oo, p_no = trans[m["t"]]
            U = draw_uniforms(sd, m["no"], m["plan"]["n_states"])
            S = simulate_chain(U, p_oo, p_no, m["state"][0])
            R, P = sleeve_from_states(m["plan"], S)
            rets.append((m["plan"]["index"], R))
            time_on[m["t"]].append(P.mean(axis=1))
        index, B = basket_from_sleeves(rets)
        parts.append(fast_metrics(B, risk_free_daily(index).to_numpy(float), index))
    res = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
    return index, res, {t: np.concatenate(v) for t, v in time_on.items()}


def percentile_rank(x: np.ndarray, v: float) -> float:
    """Anteil der Placebos mit Wert < v in Prozent (Perzentilrang von v unter den Placebos)."""
    return float((np.asarray(x) < v).mean() * 100.0)


def verdict(base_upi: float, base_dd: float, placebo_upi: np.ndarray, placebo_dd: np.ndarray) -> dict:
    """Registriertes Kriterium: UPI(base) >= 95. Perzentil der Placebo-UPI UND MaxDD(base) > 75. Perzentil der Placebo-MaxDD."""
    q_upi = float(np.percentile(placebo_upi, UPI_PCT))
    q_dd = float(np.percentile(placebo_dd, DD_PCT))
    ok_upi = bool(base_upi >= q_upi)
    ok_dd = bool(base_dd > q_dd)
    return {"q_upi": q_upi, "q_dd": q_dd, "ok_upi": ok_upi, "ok_dd": ok_dd, "bestanden": ok_upi and ok_dd}


def _pct(v: float) -> str:
    return "–" if pd.isna(v) else f"{v * 100:.2f} %"


def main() -> None:
    print(f"H14 Placebo-Timing: {len(vt.MARKETS)} Maerkte, {N_DRAWS} Ziehungen (Seeds 0..{N_DRAWS - 1}), ohne Hebel, "
          f"{BPS:.0f} bp je Wechsel, Ausfuehrung Schluss Folgetag, Cash = US-RF, Auswertung bis {vt.END}\n")
    markets, skipped = load_markets()
    print(f"Maerkte mit Daten: {len(markets)} von {len(vt.MARKETS)}; uebersprungen: {skipped or 'keine'}\n")

    # (1) Echtes base1x ueber die bestehende Pipeline (sleeve2 + basket) und mit der schnellen Funktion
    ret_ref, ret_fast = {}, []
    for m in markets:
        ref = h12.sleeve2(m["close"], m["rf"], lengths=(LENGTH,), target=None)
        ret_ref[m["t"]] = ref["ret"]
        R, _ = sleeve_from_states(m["plan"], m["state"][None, :])
        ret_fast.append((m["plan"]["index"], R))
        diff = float(np.max(np.abs(R[0] - ref["ret"].to_numpy())))
        assert diff < 1e-12, f"[{m['t']}] sleeve_from_states weicht von sleeve2 ab: {diff:.3e}"
    b_ref, _ = tp.basket(pd.DataFrame(ret_ref), vt.MIN_MARKETS)
    ix_fast, B_fast = basket_from_sleeves(ret_fast)
    assert ix_fast.equals(b_ref.index), "Korbindex weicht von tp.basket ab"
    assert float(np.max(np.abs(B_fast[0] - b_ref.to_numpy()))) < 1e-12, "Korb weicht von tp.basket ab"
    common = b_ref.index
    rf_c = risk_free_daily(common)
    base = h12.konstanz(b_ref, rf_c)
    print(f"Gemeinsamer Index: {common[0].date()} bis {common[-1].date()}, {len(common)} Handelstage")
    print("Gleichheit schnelle Funktion = sleeve2 / tp.basket fuer den echten Zustand: ja (max. Abweichung < 1e-12)\n")
    print(f"base1x: CAGR {_pct(base['cagr'])}, MaxDD {_pct(base['max_dd'])}, Ulcer {_pct(base['ulcer'])}, "
          f"UPI {base['upi']:.3f}, Sharpe {base['sharpe']:.3f}\n")

    # (2) Placebos
    seeds = np.arange(N_DRAWS)
    index, res, time_on = run_placebo(markets, seeds)
    assert index.equals(common), "Placebo-Korbindex weicht vom base1x-Index ab"

    tab_rows = []
    for k, name in [("cagr", "CAGR"), ("max_dd", "MaxDD"), ("upi", "UPI"), ("sharpe", "Sharpe"), ("ulcer", "Ulcer")]:
        x = res[k]
        b = base[k]
        row = {"Kennzahl": name, "base1x": b, "placebo_mean": float(np.nanmean(x)),
               "p5": float(np.nanpercentile(x, 5)), "p25": float(np.nanpercentile(x, 25)),
               "p50": float(np.nanpercentile(x, 50)), "p75": float(np.nanpercentile(x, 75)),
               "p95": float(np.nanpercentile(x, 95)), "min": float(np.nanmin(x)), "max": float(np.nanmax(x)),
               "rang_base1x_pct": percentile_rank(x, b)}
        tab_rows.append(row)
    summ = pd.DataFrame(tab_rows)
    print("(2) Placebo-Verteilung (1000 Ziehungen) gegen base1x; rang = Anteil der Placebos unter base1x:")
    show = summ.copy()
    for c in summ.columns[1:-1]:
        show[c] = [f"{v * 100:.2f} %" if n in ("CAGR", "MaxDD", "Ulcer") else f"{v:.3f}"
                   for n, v in zip(summ["Kennzahl"], summ[c])]
    show["rang_base1x_pct"] = [f"{v:.1f}" for v in summ["rang_base1x_pct"]]
    print(show.to_string(index=False))

    v = verdict(base["upi"], base["max_dd"], res["upi"], res["max_dd"])
    print(f"\n(3) Kriterium H14:")
    print(f"  UPI(base1x) {base['upi']:.3f} >= 95. Perzentil der Placebo-UPI {v['q_upi']:.3f}: "
          f"{'ERFUELLT' if v['ok_upi'] else 'NICHT erfuellt'} (Rang {percentile_rank(res['upi'], base['upi']):.1f})")
    print(f"  MaxDD(base1x) {_pct(base['max_dd'])} besser als 75. Perzentil der Placebo-MaxDD {_pct(v['q_dd'])}: "
          f"{'ERFUELLT' if v['ok_dd'] else 'NICHT erfuellt'} (Rang {percentile_rank(res['max_dd'], base['max_dd']):.1f})")
    if v["bestanden"]:
        print("  Gesamt H14: BESTANDEN (Timing-Beitrag belegt)")
    else:
        print("  Gesamt H14: NICHT BESTANDEN - Der Vorteil laesst sich nicht vom reinen Weniger-im-Markt-Sein unterscheiden")
    # Nur informativ: Gegenlesart (MaxDD-Betrag), nicht das registrierte Kriterium
    q_mild = float(np.percentile(res["max_dd"], 100 - DD_PCT))
    print(f"  (informativ, Gegenlesart: 75. Perzentil des MaxDD-Betrags = {_pct(q_mild)}; base1x besser: {base['max_dd'] > q_mild})")

    # (4) Markt-Check: gleiche Marktzeit?
    mk_rows = []
    for m in markets:
        p_oo, p_no = estimate_transitions(m["state"])
        _, P_real = sleeve_from_states(m["plan"], m["state"][None, :])
        mk_rows.append({"markt": m["t"], "monate": m["plan"]["n_states"], "p_an_aus": p_oo, "p_aus_an": p_no,
                        "wechsel_echt": int((np.diff(m["state"]) != 0).sum()),
                        "marktzeit_echt": float(P_real.mean()), "marktzeit_placebo_mittel": float(time_on[m["t"]].mean())})
    mk = pd.DataFrame(mk_rows)
    print("\n(4) Marktzeit echt gegen Placebo-Mittel je Markt:")
    print(mk.assign(p_an_aus=mk["p_an_aus"].map("{:.3f}".format), p_aus_an=mk["p_aus_an"].map("{:.3f}".format),
                    marktzeit_echt=mk["marktzeit_echt"].map("{:.1%}".format),
                    marktzeit_placebo_mittel=mk["marktzeit_placebo_mittel"].map("{:.1%}".format)).to_string(index=False))
    print(f"  Mittel ueber Maerkte: echt {mk['marktzeit_echt'].mean():.1%}, Placebo {mk['marktzeit_placebo_mittel'].mean():.1%}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summ.to_csv(OUT_SUMMARY, index=False, encoding="utf-8", float_format="%.6f")
    draws = pd.DataFrame({"seed": seeds, **{k: res[k] for k in ["cagr", "max_dd", "ulcer", "upi", "sharpe"]}})
    draws.to_csv(OUT_DRAWS, index=False, encoding="utf-8", float_format="%.8f")
    mk.to_csv(OUT_TRANS, index=False, encoding="utf-8", float_format="%.6f")
    print(f"\nCSV gespeichert: {OUT_SUMMARY}\nCSV gespeichert: {OUT_DRAWS}\nCSV gespeichert: {OUT_TRANS}")


if __name__ == "__main__":
    main()
