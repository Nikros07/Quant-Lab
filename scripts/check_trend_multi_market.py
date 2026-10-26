"""H5: Monats-MA12-Trendregel auf 18 Märkten, je Markt gegen Buy&Hold (docs/HYPOTHESEN.md, Eintrag H5).

Regel (identisch zur Basis in check_trend_modes.py): am Monatsende long, wenn der Monatsschluss >= Mittel
der letzten 12 Monatsschlüsse ist, sonst Cash. Gewicht 1.0 oder 0.0 auf dem Markt selbst, ohne Hebel.
Signal: Schlusskurs (ffill limit=5). Ausführung zum Schluss des Folgetags (exec_mode="close_next") statt
zur Eröffnung, weil Eröffnungskurse alter Indexdaten unzuverlässig sind. Kosten 10 bp je Wechsel, ohne Steuer.
Cash = US-Fama-French-RF, auch für ausländische Märkte (Vereinfachung laut H5).
Buy&Hold: Gewicht 1.0 ab dem ersten gültigen Kurs, Auswertung ab demselben Start wie die Strategie.
Einstiege = Wechsel Cash -> long im Auswertungsfenster (beginnt die Strategie long, zählt der Start).

Holdout: ausgewertet wird nur bis 2022-12-31 (Panel.truncate). load_panel lädt die Historie bis heute
in den Cache, ausgewertet wird davon aber nichts ab 2023.
Abweichung zu H5: load_ticker nutzt auto_adjust=True. EEM, EFA und TLT sind damit dividendenbereinigt,
H5 nennt Preisreihen ohne Dividenden. Die Auswertung bleibt so, wie sie gemessen wurde.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import pandas as pd

from qlab import metrics
from qlab.calendar import month_end_flags
from qlab.data import Panel, load_panel, risk_free_daily
from qlab.engine import CostModel, run_backtest

END = "2022-12-31"
LOAD_START = "1960-01-01"
MIN_YEARS = 5.0
BPS = 10.0
MARKETS = ["^GSPC", "^IXIC", "^DJI", "^N225", "^FTSE", "^GDAXI", "^FCHI", "^HSI", "^AXJO",
           "^GSPTSE", "^KS11", "^STOXX50E", "EEM", "EFA", "TLT", "GC=F", "CL=F", "BTC-USD"]
OUT_CSV = Path(__file__).resolve().parent.parent / "results" / "H5_multi_market.csv"
COLS = ["Status", "Start", "Jahre", "Einstiege", "Einstiege/Jahr", "CAGR_Strat", "CAGR_BH", "Sharpe_Strat",
        "Sharpe_BH", "MaxDD_Strat", "MaxDD_BH", "ΔSharpe", "DD_besser", "Sharpe_ok", "Datenqualität"]


def monthly_state(close: pd.Series) -> pd.Series:
    """Zustand je Handelstag (True = long, False = Cash), nur an Monatsenden entschieden.

    Monatsschluss >= Mittel der letzten 12 Monatsschlüsse -> long, sonst Cash. Zwischen den Monatsenden
    gilt der letzte Zustand. Die Reihe beginnt am ersten Monatsende mit gültigem MA12.
    month_end_flags entscheidet kausal, ohne Blick auf den nächsten Kurs.
    """
    close = close.astype(float)
    f = month_end_flags(close.index).to_numpy()
    me = close[f]
    ma = me.rolling(12).mean()
    ok = me.notna() & ma.notna()
    dec = (me >= ma)[ok]
    state = dec.reindex(close.index).ffill().dropna()
    return state.astype(bool)


def run_market(t: str) -> dict:
    """Eine Zeile der Tabelle. Wirft eine Exception, wenn der Markt nicht geladen werden kann oder zu kurz ist."""
    if t == "^GSPC":
        # Der gemeinsame Cache startet erst 1990; die lange Reihe (ab 1927-12-30, nur Schluss) liegt
        # in einer eigenen Datei. Eröffnung = Schluss (wird bei close_next nicht benutzt).
        from strategies.trend_ma12_us_equity_cash import _load_gspc_long
        c = _load_gspc_long().to_frame(t)
        panel = Panel(c.copy(), c).truncate(END)
    else:
        panel = load_panel([t], start=LOAD_START).truncate(END)
    raw = panel.close[t].dropna()
    if raw.empty:
        raise ValueError("keine Kurse")
    years_data = (raw.index[-1] - raw.index[0]).days / 365.25
    if years_data < MIN_YEARS:
        raise ValueError(f"nur {years_data:.1f} Jahre Daten")
    n_bad = int((raw <= 0).sum())
    if n_bad:
        print(f"[{t}] WARNUNG: {n_bad} Schlusskurse <= 0 in den Rohdaten")

    close = panel.close[t].ffill(limit=5)
    st = monthly_state(close)
    first = st.index.min()
    rf = risk_free_daily(panel.close.index)
    cost = CostModel(per_ticker_bps={t: BPS})

    w = pd.DataFrame({t: st.astype(float)})
    w = w[w[t].diff().fillna(1.0) != 0]                       # nur Zustandswechsel als Signal
    res = run_backtest(panel, w, cost=cost, exec_mode="close_next", rf=rf)
    bh_w = pd.DataFrame({t: [1.0]}, index=[raw.index[0]])     # Buy&Hold ab erstem gültigen Kurs
    bh = run_backtest(panel, bh_w, cost=cost, exec_mode="close_next", rf=rf)

    r, b = res.ret.loc[first:], bh.ret.loc[first:]
    s, sb = metrics.summarize(r, rf), metrics.summarize(b, rf)
    prev = st.shift(1, fill_value=False)
    entries = int((st & ~prev).sum())

    win = panel.close.index[panel.close.index >= first]
    op, cl = panel.open[t].reindex(win), panel.close[t].reindex(win)
    dq = float((op.isna() | (op == 0) | (op == cl)).mean())

    return {
        "Status": "ok",
        "Start": first.date().isoformat(),
        "Jahre": s["years"],
        "Einstiege": entries,
        "Einstiege/Jahr": entries / s["years"],
        "CAGR_Strat": s["cagr"],
        "CAGR_BH": sb["cagr"],
        "Sharpe_Strat": s["sharpe"],
        "Sharpe_BH": sb["sharpe"],
        "MaxDD_Strat": s["max_dd"],
        "MaxDD_BH": sb["max_dd"],
        "ΔSharpe": s["sharpe"] - sb["sharpe"],
        "DD_besser": bool(s["max_dd"] > sb["max_dd"]),        # beide negativ: kleinerer Betrag = besser
        "Sharpe_ok": bool(s["sharpe"] >= sb["sharpe"]),
        "Datenqualität": dq,
    }


def _col(series: pd.Series, fn) -> pd.Series:
    return series.map(lambda v: fn(v) if pd.notna(v) else "–")


def main() -> None:
    print(f"H5 Multi-Markt: Monats-MA12, Auswertung bis {END}, {BPS:.0f} bp je Wechsel, Signal Schlusskurs, "
          "Ausführung Schluss Folgetag, ohne Steuer, Cash = US-FF-RF\n")
    rows = {}
    for t in MARKETS:
        try:
            rows[t] = run_market(t)
        except Exception as exc:  # Laden fehlgeschlagen oder zu kurz: Markt bleibt in der Tabelle
            print(f"[{t}] keine Daten: {exc}")
            rows[t] = {"Status": "keine Daten"}

    df = pd.DataFrame.from_dict(rows, orient="index").reindex(columns=COLS)
    df.index.name = "Markt"

    show = pd.DataFrame(index=df.index)
    show["Status"] = df["Status"]
    show["Start"] = df["Start"].fillna("–")
    show["Jahre"] = _col(df["Jahre"], lambda v: f"{v:.1f}")
    show["Einstiege"] = _col(df["Einstiege"], lambda v: f"{int(v)}")
    show["Einstiege/Jahr"] = _col(df["Einstiege/Jahr"], lambda v: f"{v:.2f}")
    for c in ["CAGR_Strat", "CAGR_BH"]:
        show[c] = _col(df[c], lambda v: f"{v * 100:.2f} %")
    for c in ["Sharpe_Strat", "Sharpe_BH"]:
        show[c] = _col(df[c], lambda v: f"{v:.2f}")
    for c in ["MaxDD_Strat", "MaxDD_BH"]:
        show[c] = _col(df[c], lambda v: f"{v * 100:.1f} %")
    show["ΔSharpe"] = _col(df["ΔSharpe"], lambda v: f"{v:+.2f}")
    show["DD_besser"] = _col(df["DD_besser"], lambda v: "ja" if v else "nein")
    show["Sharpe_ok"] = _col(df["Sharpe_ok"], lambda v: "ja" if v else "nein")
    show["Datenqualität"] = _col(df["Datenqualität"], lambda v: f"{v * 100:.1f} %")
    print()
    print(show.to_string())

    ok = df[df["Status"] == "ok"]
    n = len(ok)
    print(f"\nMärkte mit Daten: {n} von {len(MARKETS)}")
    if n == 0:
        print("Keine Auswertung möglich.")
        return
    dd = ok["DD_besser"].astype(bool)
    sh = ok["Sharpe_ok"].astype(bool)
    share_dd, share_sh = float(dd.mean()), float(sh.mean())
    print(f"Anteil DD_besser: {int(dd.sum())} von {n} = {share_dd * 100:.1f} %")
    print(f"Anteil Sharpe_ok: {int(sh.sum())} von {n} = {share_sh * 100:.1f} %")
    print(f"Median ΔSharpe: {ok['ΔSharpe'].astype(float).median():+.2f}")
    print(f"Einstiege gesamt: {int(ok['Einstiege'].astype(int).sum())}")

    success = share_dd >= 0.70 and share_sh >= 0.50
    abort_a = share_dd < 0.60
    abort_b = share_dd < 0.40
    print(f"\nErfolgskriterium H5 erfüllt? {'JA' if success else 'NEIN'}  "
          "(Anteil DD_besser >= 70 % UND Anteil Sharpe_ok >= 50 %)")
    print(f"Abbruchkriterium: (a) DD_besser < 60 %: {'ausgelöst' if abort_a else 'nicht ausgelöst'}; "
          f"(b) DD_besser < 40 %: {'ausgelöst' if abort_b else 'nicht ausgelöst'}")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.reset_index().to_csv(OUT_CSV, index=False, encoding="utf-8", float_format="%.6f")
    print(f"\nCSV gespeichert: {OUT_CSV}")


if __name__ == "__main__":
    main()
