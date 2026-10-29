"""P4: H16 (Timing-Luck) und H20 (4 Tranchen) ohne BTC-USD, Raster-Check nach V5.

Registrierung: docs/HYPOTHESEN.md, Abschnitt P4. Die Skripte H16/H20 laufen unveraendert, nur die Marktliste
wird um BTC-USD gekuerzt und die Ausgabedateien werden umgeleitet (results/P4_*). Die Konsolenausgaben der beiden
Laeufe werden in results/P4_H16.log und results/P4_H20.log gespeichert; hier erscheinen nur die letzten Zeilen.
"""
import contextlib
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import check_h16_timing_luck as h16
import check_h20_tranche4 as h20
import check_trend_vt_basket as vt

RES = ROOT / "results"
EXCLUDE = "BTC-USD"


def run(mod, log_name: str) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        mod.main()
    text = buf.getvalue()
    (RES / log_name).write_text(text, encoding="utf-8")
    return text


def main() -> None:
    vt.MARKETS = [t for t in vt.MARKETS if t != EXCLUDE]
    print(f"Maerkte ohne {EXCLUDE}: {len(vt.MARKETS)}")
    h16.OUT_STATS = RES / "P4_H16_phasen_kennzahlen.csv"
    h16.OUT_RANGE = RES / "P4_H16_spannweite_kriterien.csv"
    h16.OUT_RET = RES / "P4_H16_basket_returns.csv"
    h20.OUT_STATS = RES / "P4_H20_tranche4.csv"
    h20.OUT_RET = RES / "P4_H20_basket_returns.csv"
    t16 = run(h16, "P4_H16.log")
    t20 = run(h20, "P4_H20.log")
    for name, text in (("H16", t16), ("H20", t20)):
        print(f"\n=== {name} ohne BTC (letzte 28 Zeilen der Ausgabe) ===")
        print("\n".join(text.strip().splitlines()[-28:]))


if __name__ == "__main__":
    main()
