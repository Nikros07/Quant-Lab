"""H18: Kosten und Umsetzung von base1x (docs/HYPOTHESEN.md, Pruefblock P1, Eintrag H18).

Regel (wie vorab registriert, reine Messung, KEIN Bestehen-Kriterium):
  * base1x = Monats-MA12 je Markt (Monatsschluss >= Mittel der letzten 12 Monatsschluesse -> long, sonst Cash),
    17 Maerkte gleichgewichtet, ohne Hebel, Ausfuehrung zum Schluss des Folgetags, 1991-02 bis 2022-12.
    Die Positionen sind IDENTISCH zu sleeve2(lengths=(12,), target=None); nur Kosten/Finanzierung/Cash werden variiert.
  * Kostenstufen 5, 10, 25 und 50 bp je Seite.
  * Szenario A = Lab (Cash zum US-RF, keine Finanzierung).
    Szenario B = CFD (Finanzierung zu US-RF + 2,5 % p. a. auf den Nominalwert, solange der Markt long ist; Cash im
    Konto mit 0 % verzinst; Dividendenausgleich NICHT modelliert).
    Szenario C = Futures/ETF (10 bp, Cash zum US-RF) -- rechnerisch identisch zu A bei 10 bp.
  * Ergebnis je Szenario: CAGR, MaxDD, UPI (zusaetzlich Sharpe, Vol). Referenzen: B&H-Korb (kostenfrei, wie in H12),
    reiner US-RF-Cash.
  * Break-even (Bisektion): wie viele bp je Seite bzw. wie viel Prozent Finanzierungsaufschlag p. a. den CAGR-Vorsprung
    gegenueber reinem US-RF-Cash aufzehren; ab wann base1x den UPI des B&H-Korbs verliert.
  * Kriterium: keines; berichtet wird, ab welcher Kostenstufe base1x den UPI von Buy&Hold verliert.

Finanzierung im Sleeve: ret_d = pos_d r_d + (1 - pos_d) cash_d - |pos_d - pos_{d-1}| bps / 1e4
                                 - pos_d (rf_d + aufschlag / 252)   [nur wenn long_financing gesetzt und pos_d > 0],
mit cash_d = rf_d (cash_rate_mode "rf") oder 0 ("0").
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
OUT_DIR = ROOT / "results"
OUT_SCEN = OUT_DIR / "H18_scenarios.csv"
OUT_BE = OUT_DIR / "H18_breakeven.csv"

COST_LEVELS = (5.0, 10.0, 25.0, 50.0)
STD_BPS = 10.0
CFD_MARKUP = 0.025
CASH_MODES = ("rf", "0")


# ----------------------------------------------------------------------------------------------------------------
# Sleeve
# ----------------------------------------------------------------------------------------------------------------

def prepare_market(close: pd.Series, rf: pd.Series) -> dict:
    """Positionen und Rohrenditen eines Marktes (Kopie der Logik von sleeve2 mit lengths=(12,), target=None).

    Die Position haengt NICHT von Kosten, Finanzierung oder Cash ab. Entscheidung am Monatsende m, Ausfuehrung zum
    Schluss von m+1, wirksam ab Tag m+2.
    """
    close = close.astype(float)
    idx = close.index
    r = close.pct_change(fill_method=None)
    flags = month_end_flags(idx).to_numpy()
    me = close[flags]
    ma = me.rolling(12).mean()
    st_me = (me >= ma).astype(float).where(ma.notna()).dropna()
    if st_me.empty:
        raise ValueError("kein gueltiger Monatszustand (zu wenige Monatsenden)")
    s_i = idx.get_loc(st_me.index[0])
    n = len(idx)
    dec = np.full(n, np.nan)
    for d, st in st_me.items():
        i = idx.get_loc(d)
        if i + 2 >= n:
            continue
        dec[i + 2] = st
    pos = pd.Series(dec).ffill().fillna(0.0).to_numpy()
    r0 = np.nan_to_num(r.to_numpy(float))
    rf_a = rf.reindex(idx).ffill().fillna(0.0).to_numpy(float)
    return {"index": idx[s_i:], "pos": pos[s_i:], "r0": r0[s_i:], "rf": rf_a[s_i:]}


def returns_from_prep(prep: dict, *, cost_bps: float = STD_BPS, long_financing: float | None = None,
                      cash_rate_mode: str = "rf") -> pd.DataFrame:
    """Tagesrenditen eines vorbereiteten Marktes mit Kosten, Finanzierung und Cash-Verzinsung (siehe Modul-Docstring)."""
    if cash_rate_mode not in CASH_MODES:
        raise ValueError(f"cash_rate_mode muss 'rf' oder '0' sein, nicht {cash_rate_mode!r}")
    if cost_bps < 0:
        raise ValueError("cost_bps darf nicht negativ sein")
    p, r0, rf = prep["pos"], prep["r0"], prep["rf"]
    prev = np.concatenate([[0.0], p[:-1]])
    cash = rf if cash_rate_mode == "rf" else np.zeros_like(rf)
    ret = p * r0 + (1.0 - p) * cash - np.abs(p - prev) * cost_bps / 1e4
    if long_financing is not None:
        ret = ret - np.where(p > 0, p * (rf + long_financing / TRADING_DAYS), 0.0)
    return pd.DataFrame({"ret": ret, "pos": p}, index=prep["index"])


def sleeve_h18(close: pd.Series, rf: pd.Series, *, cost_bps: float = STD_BPS, long_financing: float | None = None,
               cash_rate_mode: str = "rf") -> pd.DataFrame:
    """Markt-Sleeve nach H18: base1x-Positionen mit frei waehlbaren Kosten, Finanzierung und Cash-Zins.

    * cost_bps: Kosten je Seite in bp auf |Delta Gewicht|.
    * long_financing: Aufschlag p. a. (z. B. 0.025); None = keine Finanzierung. Sonst wird auf den Nominalwert solange
      pos > 0 der Satz (US-RF + Aufschlag) belastet.
    * cash_rate_mode: "rf" = Cash zum US-RF, "0" = Cash unverzinst.
    Mit Standardwerten (10 bp, keine Finanzierung, Cash rf) identisch zu sleeve2(lengths=(12,), target=None).
    """
    return returns_from_prep(prepare_market(close, rf), cost_bps=cost_bps, long_financing=long_financing,
                             cash_rate_mode=cash_rate_mode)


# ----------------------------------------------------------------------------------------------------------------
# Korb, Kennzahlen, Bisektion
# ----------------------------------------------------------------------------------------------------------------

def basket_returns(preps: dict, min_markets: int, **kw) -> pd.Series:
    """Gleichgewichteter Korb der Sleeves (basket aus check_trend_portfolio)."""
    df = pd.DataFrame({t: returns_from_prep(p, **kw)["ret"] for t, p in preps.items()})
    return tp.basket(df, min_markets)[0]


def bh_returns(preps: dict, min_markets: int, long_financing: float | None = None) -> pd.Series:
    """Buy&Hold-Korb ab Sleeve-Start je Markt. Ohne long_financing kostenfrei (wie in H12); mit Finanzierung wird
    (US-RF + Aufschlag/252) taeglich abgezogen (nur informativ)."""
    cols = {}
    for t, p in preps.items():
        r = p["r0"].copy()
        if long_financing is not None:
            r = r - (p["rf"] + long_financing / TRADING_DAYS)
        cols[t] = pd.Series(r, index=p["index"])
    return tp.basket(pd.DataFrame(cols), min_markets)[0]


def stats(ret: pd.Series, rf: pd.Series) -> dict:
    """CAGR, Vol, Sharpe, MaxDD, Ulcer, UPI (konstanz aus H12)."""
    return h12.konstanz(ret, rf)


def bisect_root(f, lo: float, hi: float, *, tol: float = 1e-4, maxit: int = 80) -> tuple[str, float]:
    """Nullstelle einer monoton FALLENDEN Funktion f auf [lo, hi] per Bisektion.

    Gibt (Status, Wert): "ok" (Nullstelle gefunden), "unter_lo" (f(lo) <= 0: schon am unteren Rand erfuellt, Wert = lo),
    "ueber_hi" (f(hi) > 0: auch am oberen Rand nicht aufgezehrt, Wert = hi).
    """
    flo, fhi = f(lo), f(hi)
    if not np.isfinite(flo) or not np.isfinite(fhi):
        return "nan", float("nan")
    if flo <= 0:
        return "unter_lo", lo
    if fhi > 0:
        return "ueber_hi", hi
    a, b = lo, hi
    for _ in range(maxit):
        m = 0.5 * (a + b)
        if f(m) > 0:
            a = m
        else:
            b = m
        if b - a < tol:
            break
    return "ok", 0.5 * (a + b)


def _pct(v: float) -> str:
    return "–" if pd.isna(v) else f"{v * 100:.2f} %"


def _num(v: float, fmt: str = "{:.2f}") -> str:
    return "–" if pd.isna(v) else fmt.format(v)


# ----------------------------------------------------------------------------------------------------------------
# Hauptlauf
# ----------------------------------------------------------------------------------------------------------------

def load_preps() -> dict:
    preps, skipped = {}, []
    for t in vt.MARKETS:
        try:
            close = vt.load_market(t)
        except Exception as exc:
            print(f"[{t}] keine Daten, uebersprungen: {exc}")
            skipped.append(t)
            continue
        rf = risk_free_daily(close.index)
        try:
            preps[t] = prepare_market(close, rf)
        except Exception as exc:
            print(f"[{t}] Sleeve nicht berechenbar, uebersprungen: {exc}")
            skipped.append(t)
    print(f"Maerkte mit Daten: {len(preps)} von {len(vt.MARKETS)}; uebersprungen: {skipped or 'keine'}\n")
    return preps


def main() -> None:
    print(f"H18 Kosten und Umsetzung: {len(vt.MARKETS)} Maerkte, base1x (Monats-MA12, ohne Hebel), Auswertung bis {vt.END}, "
          "Ausfuehrung Schluss Folgetag, ohne Steuer\n")
    preps = load_preps()
    mm = vt.MIN_MARKETS

    # gemeinsamer Index: B&H und Referenz-base1x (Positionen sind in allen Szenarien gleich, der Index auch)
    ref = basket_returns(preps, mm, cost_bps=STD_BPS)
    bh = bh_returns(preps, mm)
    common = ref.index.intersection(bh.index)
    rf_c = risk_free_daily(common)
    print(f"Gemeinsamer Index: {common[0].date()} bis {common[-1].date()}, {len(common)} Handelstage\n")

    def run(**kw) -> dict:
        return stats(basket_returns(preps, mm, **kw).reindex(common), rf_c)

    K_bh = stats(bh.reindex(common), rf_c)
    K_bh_cfd = stats(bh_returns(preps, mm, CFD_MARKUP).reindex(common), rf_c)
    K_rf = stats(rf_c, rf_c)
    cagr_rf = K_rf["cagr"]

    rows = []

    def add(szen: str, bps: float | None, fin: float | None, cash: str, K: dict) -> None:
        rows.append({
            "Szenario": szen, "Kosten_bp_je_Seite": bps, "Finanzierungsaufschlag_pa": fin, "Cash": cash,
            "CAGR": K["cagr"], "MaxDD": K["max_dd"], "UPI": K["upi"], "Sharpe": K["sharpe"], "Vol": K["vol"],
            "Ulcer": K["ulcer"], "UPI_minus_UPI_BH": K["upi"] - K_bh["upi"],
            "UPI_besser_als_BH": bool(K["upi"] > K_bh["upi"]) if szen not in ("BH", "BH_CFD", "RF_Cash") else "",
            "CAGR_minus_RFCash": K["cagr"] - cagr_rf,
        })

    add("BH", None, None, "-", K_bh)
    add("BH_CFD_info", None, CFD_MARKUP, "-", K_bh_cfd)
    add("RF_Cash", None, None, "rf", K_rf)

    results = {}
    for bps in COST_LEVELS:
        results[("A", bps)] = run(cost_bps=bps, cash_rate_mode="rf")
        results[("B", bps)] = run(cost_bps=bps, long_financing=CFD_MARKUP, cash_rate_mode="0")
    results[("C", STD_BPS)] = run(cost_bps=STD_BPS, cash_rate_mode="rf")
    for (s, bps), K in results.items():
        add(s, bps, CFD_MARKUP if s == "B" else None, "0" if s == "B" else "rf", K)

    names = {"A": "A Lab (Cash rf)", "B": "B CFD (rf+2,5 %, Cash 0)", "C": "C Futures/ETF (10 bp, Cash rf)"}
    print(f"(1) Referenzen: B&H-Korb (kostenfrei): CAGR {_pct(K_bh['cagr'])}, MaxDD {_pct(K_bh['max_dd'])}, "
          f"UPI {_num(K_bh['upi'], '{:.3f}')}, Sharpe {_num(K_bh['sharpe'])}")
    print(f"    B&H-Korb mit CFD-Finanzierung (informativ): CAGR {_pct(K_bh_cfd['cagr'])}, MaxDD {_pct(K_bh_cfd['max_dd'])}, "
          f"UPI {_num(K_bh_cfd['upi'], '{:.3f}')}")
    print(f"    reiner US-RF-Cash: CAGR {_pct(cagr_rf)}\n")
    print("(2) base1x je Szenario und Kostenstufe:")
    for (s, bps), K in results.items():
        flag = "UPI > B&H" if K["upi"] > K_bh["upi"] else "UPI <= B&H"
        print(f"  {names[s]:<30} {bps:>4.0f} bp: CAGR {_pct(K['cagr'])}, MaxDD {_pct(K['max_dd'])}, "
              f"UPI {_num(K['upi'], '{:.3f}')}, Sharpe {_num(K['sharpe'])}  ({flag}; CAGR gg. RF-Cash {(K['cagr'] - cagr_rf) * 100:+.2f} Pp)")

    # Referenz-Check gegen die registrierte Empfehlung
    KA = results[("A", STD_BPS)]
    print(f"\n(3) Kontrolle A@10 bp = base1x: CAGR {_pct(KA['cagr'])}, MaxDD {_pct(KA['max_dd'])}, Sharpe {_num(KA['sharpe'], '{:.3f}')} "
          "(Erwartung laut Stand: 7,30 % / -14,75 % / 0,63)")

    # Break-even
    be = []

    def add_be(szen: str, groesse: str, kriterium: str, status: str, val: float, einheit: str, anm: str) -> None:
        be.append({"Szenario": szen, "Variiert": groesse, "Kriterium": kriterium, "Status": status,
                   "Wert": val, "Einheit": einheit, "Anmerkung": anm})
        txt = {"ok": f"{val:.2f} {einheit}", "unter_lo": f"schon bei {val:.2f} {einheit} nicht mehr erfuellt",
               "ueber_hi": f"auch bei {val:.2f} {einheit} noch erfuellt (Obergrenze)", "nan": "nicht berechenbar"}[status]
        print(f"  {szen:<24} {groesse:<24} {kriterium:<18}: {txt}  {anm}")

    kw_b = dict(long_financing=CFD_MARKUP, cash_rate_mode="0")

    def cagr_gap(mk):            # > 0 solange der CAGR-Vorsprung ggue. RF-Cash besteht; mk: x -> Sleeve-Parameter
        return lambda x: stats(basket_returns(preps, mm, **mk(x)).reindex(common), rf_c)["cagr"] - cagr_rf

    def upi_gap(mk):             # > 0 solange UPI(base1x) > UPI(B&H)
        return lambda x: stats(basket_returns(preps, mm, **mk(x)).reindex(common), rf_c)["upi"] - K_bh["upi"]

    print("\n(4) Break-even (Bisektion):")
    BPS_HI, MK_HI = 1000.0, 0.30
    # bp je Seite
    cases = [
        ("A Lab", "Kosten bp je Seite", lambda x: dict(cost_bps=x, cash_rate_mode="rf"), 0.0, BPS_HI, "bp je Seite", STD_BPS),
        ("B CFD (2,5 %, Cash 0)", "Kosten bp je Seite", lambda x: dict(cost_bps=x, **kw_b), 0.0, BPS_HI, "bp je Seite", STD_BPS),
    ]
    for szen, var, mk, lo, hi, unit, base in cases:
        for krit, fn in [("CAGR = RF-Cash", cagr_gap), ("UPI = UPI B&H", upi_gap)]:
            st, v = bisect_root(fn(mk), lo, hi, tol=0.01)
            extra = f"(Zusatz ggue. {base:.0f} bp: {v - base:+.2f} bp)" if st == "ok" else ""
            add_be(szen, var, krit, st, v, unit, extra)
    # Finanzierungsaufschlag p. a. (in %), bei 10 bp
    fin_cases = [
        ("B CFD (Cash 0, 10 bp)", lambda x: dict(cost_bps=STD_BPS, long_financing=x, cash_rate_mode="0")),
        ("B2 info (Cash rf, 10 bp)", lambda x: dict(cost_bps=STD_BPS, long_financing=x, cash_rate_mode="rf")),
    ]
    for szen, mk in fin_cases:
        for krit, fn in [("CAGR = RF-Cash", cagr_gap), ("UPI = UPI B&H", upi_gap)]:
            f = (lambda x, mk=mk, fn=fn: fn(mk)(x / 100.0))
            st, v = bisect_root(f, 0.0, MK_HI * 100.0, tol=0.001)
            add_be(szen, "Finanzierungsaufschlag % p. a.", krit, st, v, "% p. a.",
                   "(Aufschlag zusaetzlich zu US-RF auf den Nominalwert)")

    # Kostenstufe, ab der UPI von B&H verloren geht (Raster)
    print("\n(5) Ab welcher Kostenstufe (Raster 5/10/25/50 bp) verliert base1x den UPI von B&H?")
    verdict = {}
    for s in ("A", "B"):
        lost = [b for b in COST_LEVELS if results[(s, b)]["upi"] <= K_bh["upi"]]
        verdict[s] = lost[0] if lost else None
        print(f"  {names[s]}: " + (f"ab {lost[0]:.0f} bp" if lost else "in keiner getesteten Stufe (UPI bleibt hoeher als B&H, "
                                    f"UPI B&H {_num(K_bh['upi'], '{:.3f}')})"))
    print("  Hinweis: Szenario C = A bei 10 bp (rechnerisch identisch).")
    print("  Einschraenkung: Dividendenausgleich im CFD nicht modelliert; B&H-Referenz kostenfrei; keine Steuer; "
          "Kosten nur proportional zum Umsatz (kein Mindestspread/Kommission); Cash im CFD-Konto 0 %.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT_SCEN, index=False, encoding="utf-8", float_format="%.6f")
    pd.DataFrame(be).to_csv(OUT_BE, index=False, encoding="utf-8", float_format="%.6f")
    print(f"\nCSV gespeichert: {OUT_SCEN}")
    print(f"CSV gespeichert: {OUT_BE}")


if __name__ == "__main__":
    main()
