"""Lädt alle (wahrscheinlich) benötigten Kurse in den Cache, einmal und nacheinander.

Aufruf:
    .venv\\Scripts\\python.exe scripts\\prewarm.py                 # Standardliste
    .venv\\Scripts\\python.exe scripts\\prewarm.py --from-json research\\strategie-kandidaten.json
Verhindert, dass parallel arbeitende Agenten gleichzeitig denselben Cache beschreiben.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from qlab.data import french, load_ticker  # noqa: E402

DEFAULT = [
    # Aktien USA / Größe / Stil
    "SPY", "QQQ", "IWM", "DIA", "MDY", "IWD", "IWF", "VTV", "VUG", "IJR", "IJH",
    # Sektoren (SPDR)
    "XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY", "XLC", "XLRE", "XLG",
    # International / Länder
    "EFA", "EEM", "VEA", "VWO", "EWJ", "EWG", "EWU", "EWQ", "EWC", "EWA", "EWH", "EWS", "EWT", "EWY", "EWZ", "EWW",
    "EWP", "EWI", "EWL", "EWN", "EWD", "EIS", "INDA", "FXI", "VGK", "ACWI", "VT",
    # Faktor-ETFs
    "MTUM", "QUAL", "USMV", "VLUE", "SIZE", "SPLV", "SPHB",
    # Anleihen
    "IEF", "TLT", "SHY", "IEI", "TLH", "LQD", "HYG", "AGG", "BND", "TIP", "BIL", "SHV", "MBB", "EMB", "BWX", "VCSH", "VCIT",
    # Rohstoffe / Gold / Immobilien
    "GLD", "IAU", "SLV", "DBC", "GSG", "USO", "UNG", "DBA", "VNQ", "IYR", "RWX", "VNQI", "GC=F", "CL=F",
    # Währungen
    "UUP", "FXE", "FXY", "FXA", "FXB", "FXC", "FXF",
    # Volatilität
    "^VIX", "^VIX3M", "^VXV", "VXX", "SVXY", "UVXY", "VIXY", "^GSPC", "^IRX", "^TNX", "^TYX", "^FVX", "^NDX", "^RUT",
    # Krypto
    "BTC-USD", "ETH-USD",
]

FRENCH = ["F-F_Research_Data_Factors", "F-F_Momentum_Factor", "F-F_Research_Data_5_Factors_2x3",
          "49_Industry_Portfolios", "17_Industry_Portfolios", "10_Portfolios_Prior_12_2", "25_Portfolios_5x5"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-json", default="")
    ap.add_argument("--french", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    tickers = list(DEFAULT)
    if a.from_json:
        for s in json.loads(Path(a.from_json).read_text(encoding="utf-8")).get("selected", []):
            tickers += list(s.get("tickers", []))
    seen, ok, bad = set(), [], []
    for t in tickers:
        if t in seen:
            continue
        seen.add(t)
        try:
            df = load_ticker(t, start="1990-01-01", max_age_days=30 if not a.force else 0, refresh=a.force)
            ok.append((t, str(df.index.min().date()), len(df)))
        except Exception as exc:
            bad.append((t, str(exc)[:80]))
    print(f"{len(ok)} geladen, {len(bad)} fehlgeschlagen")
    for t, st, n in ok:
        print(f"  {t:10s} ab {st}  {n:6d} Tage")
    for t, e in bad:
        print(f"  FEHLT {t}: {e}")
    if a.french:
        for ds in ("F-F_Research_Data_Factors", "F-F_Momentum_Factor"):
            for daily in (True, False):
                try:
                    french(ds, daily=daily)
                    print("French ok:", ds, "daily" if daily else "monthly")
                except Exception as exc:
                    print("French FEHLER:", ds, daily, str(exc)[:80])


if __name__ == "__main__":
    main()
