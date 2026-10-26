# Audit svxy_term_structure_filter — 2026-10-21
Urteil: BESTANDEN MIT HINWEISEN
Geprüfte Module/Tests/Läufe: `strategies/svxy_term_structure_filter.py` (123 Zeilen, kein `_etf`-Schwestermodul), `tests/test_svxy_term_structure_filter.py` (40 Tests, alle bestanden), Lauf `scripts/run_all.py --ids svxy_term_structure_filter --tag audit_svxy_term_structure_filter --n-boot 200` (Kausalitätstest bestanden, kein `--final`, kein `--skip-causality`), Spezifikation `research/strategie-kandidaten.json` Eintrag Nr. 21 (`selected`), Handrechnung `docs/audits/_tmp/handcalc_svxy.py`, Detailprüfung `docs/audits/_tmp/svxy_detail.py`.

## Befunde
| Nr | Schwere (hoch/mittel/niedrig) | Datei:Zeile | Befund | Beleg (Zitat ≤ 2 Zeilen / Rechnung) | Korrekturvorschlag |
|---|---|---|---|---|---|
| 1 | mittel | `scripts/run_all.py` (keine Verwendung von `split_by_regime`); `strategies/svxy_term_structure_filter.py:75-80` | Die Spezifikation verlangt, die Statistik von -1x (bis 2018-02-27) und -0.5x (ab 2018-02-28) getrennt auszuweisen. Der Lauf liefert nur eine gemeinsame Kennzahl über beide Regime. `split_by_regime` wird vom Lauf nicht aufgerufen. | `grep split_by_regime scripts/run_all.py` ohne Treffer. Nachrechnung (Detailskript): -1x: CAGR 50,2 %, Vol 56,5 %; -0,5x: CAGR 10,3 %, Vol 33,0 %. Die Gesamt-CAGR 31,5 % wird vom -1x-Regime getragen. | Lauf um Regime-Split erweitern und beide Teile im Bericht ausweisen. |
| 2 | mittel | `strategies/svxy_term_structure_filter.py:33-34, 56` | Abweichung von der Spezifikation: Die Spezifikation nennt ^IRX als Cash-Zins und in den Tickern. Der Code nutzt bewusst den Fama-French-RF der Engine. Das steht nur im Docstring. | Spec: `"tickers": [SVXY, ^VIX, ^VIX3M, SPY, ^IRX]`. Code Z. 56: `"tickers": [SVXY, SPY, VIX, VIX3M]`. | Entweder Spezifikation an die Umsetzung anpassen (dokumentiert) oder ^IRX als Cash-Zins einbauen. Die Abweichung sollte im Logbuch stehen. |
| 3 | mittel | Lauf / `strategies/svxy_term_structure_filter.py:91-97` | Das Stressereignis 2018-02-05/06 (in der Spezifikation Abbruchkriterium) liegt im Lauf in Cash. Das Signal war am 2018-02-02 schon AUS (Verhältnis 1,016), die Position wurde am Open 02-05 verkauft. Der Lauf testet damit das Ruin-Szenario nicht. Das Abbruchkriterium „Einzeltagesverlust > 40 %“ bleibt ungeprüft. | Detailskript: VIX/VIX3M 2018-02-01 0,915; 02-02 1,016; 02-05 1,327; 02-06 1,262. Gewichte: 2018-02-02 = 0,0. Größter Tagesverlust im Lauf: -19,2 % (2011-11-09). | Im Bericht festhalten, dass das Stressereignis nicht durchschlägt. Zusätzlich einen Stresstest mit Haltepflicht (Zwangs-Long an den Stresstagen) als reine Szenario-Rechnung, nicht als Strategie-Variante. |
| 4 | mittel | Bewertung des Ergebnisses (nicht Code) | Kein belegter Vorteil gegenüber SPY im Risiko-adjustierten Sinn. Die Sharpe-Differenz zu SPY ist 0,00 mit 90-%-KI -0,45 … 0,34 und p = 0,48. Die CAGR-Differenz kommt mit Vol 47,8 % und MaxDD -56,9 %. Die „92 % der 5-J-Fenster über SPY“ beruhen auf 13 überlappenden Fenstern. | Summary-Tabelle: ΔSharpe vs SPY 0,00 (-0,45…0,34), p 0,480, 5J-Fenster 92 % (n = 13). | Im Hinweis an den Auftraggeber nicht als „Edge“ formulieren. Erst mit Regime-Split (Befund 1) und Kosten-/Fill-Stress beurteilen. |
| 5 | niedrig | `strategies/svxy_term_structure_filter.py:66-69` | Spezifikation nennt drei Varianten (W = 0,25; Fill Schluss t+1; SPY-Sekundärtest). Die SPEC enthält nur zwei. Die Fill-Variante läuft nur über CLI `--exec close_next`. Sie wurde in diesem Lauf nicht ausgeführt. | Spec `sensitivity_variants` mit drei Punkten. Summary: 3 Läufe (base, w025, spy_secondary). | `close_next`-Lauf und Kosten-Stress (`--cost-mult 0.5` / `2`) separat ausführen und protokollieren. |
| 6 | niedrig | `tests/test_svxy_term_structure_filter.py` (gesamt) | Tests prüfen Regel, Timing, Kausalität und Kosten gut. Sie laufen aber nur auf synthetischen Panels. Kein Test deckt den Regimebruch 2018 oder die Stressereignisse ab. `test_matches_reference_rule` reimplementiert dieselbe Regel. | Alle Tests nutzen `_panel(...)` mit Zufallspfaden, keine Daten aus dem Cache. | Einen Test mit echtem Cache-Ausschnitt ergänzen (nur lokal, deterministisch), der den 2018-Übergang prüft. |
| 7 | niedrig | `results/SUMMARY_audit_svxy_term_structure_filter.md` (Kopfzeile vs. Tabelle) | Die Kopfzeile nennt SPY mit CAGR 9,5 % und Sharpe 0,46 (ab 1993). Die Vergleichstabelle nutzt SPY ab 2011-10 mit CAGR 13,9 % und Sharpe 0,80. Beides ist korrekt, aber die Fenster sind nicht ausgewiesen. | CSV `spy_cagr 0,1388`, `spy_sharpe 0,804`; Kopfzeile „SPY: CAGR 9.5%, Sharpe 0.46“. | Benchmark-Fenster in jeder Tabelle mit angeben. |
| 8 | niedrig | `strategies/svxy_term_structure_filter.py:89-91, 113` (Timing) | Der VIX-Schlusswert wird nach dem NYSE-Schluss berechnet. Das Signal am Schluss t kann dadurch einen Zeitvorsprung von einigen Minuten gegenüber SPY/SVXY-Schlusskursen haben. Der Fill am Open t+1 entschärft das weitgehend. | Nur Hinweis, keine Zahl belegt. | Im Bericht als nicht quantifiziert vermerken. |

Keine Befunde zu Look-ahead oder Engine-Vertrag gefunden:
- `ffill(limit=5)` ist rein vergangenheitsbezogen (Z. 89-90), `v3.where(v3 > 0)` verhindert Division durch 0 (Z. 91).
- `known = ratio.notna().cummax()` (Z. 114) und `shift(1)` (Z. 118-119) sind kausal.
- Gewichte nur an Tagen mit Kurs (Z. 111). Die Summe je Zeile ist maximal 1,0 (Z. 103-104 erzwingen `0 < w <= 1`).
- Kein `center=True`, kein `bfill`, kein `groupby(...).last()`.
- `check_causality` im Lauf bestanden (CSV `causal_ok = True` für alle 3 Läufe, keine Meldung im Log).
- Holdout geschützt: `IS_END = "2022-12-31"` (run_all.py:31), Summary „bis 2022-12-31“. `--final` nicht verwendet.

Warnsignale nach Auftrag (3):
- Sharpe 0,80 (base) liegt unter 1,0. Kein Warnsignal.
- MaxDD -56,9 %. Kein „sehr kleiner Drawdown“. Aber nahe am Abbruchkriterium -60 %.
- CAGR 31,5 % für ein Short-Vol-Produkt: erklärbar. Der Großteil stammt aus dem -1x-Regime 2011-2018 (CAGR 50 %), das durch den Produktbruch nicht wiederholbar ist (Befund 1).

## Handrechnung (kurz: Eingabe, erwartet, Modul)
- Eingabe: synthetisches Panel, 400 Handelstage ab 2014-01-02, `ratio` = 1,1 / 0,9 (60-119) / 1,0 (150) / 0,8 (200-259) / 1,2 (260-), feste Seeds.
- Erwartet (eigene Schleife, Zeile nur bei Zustandswechsel oder erstem Tag): 5 Zeilen, Gewichte 0, 1, 0, 1, 0 an 2014-03-26 (nach dem ersten Tag), 2014-03-27, 2014-10-09, 2014-12-31, 2015-01-01 mit den Zeilen aus dem Lauf.
- Modul: identische Zeilen und Werte (`Index identisch: True`, `Werte identisch: True`). Schwellwert-Grenzfall 1,0 wird als AUS gewertet (Tag 150 wird nicht als ON-Zeile ausgegeben).
- Tagesrenditen der Engine wurden über den Test `test_engine_matches_spec_daily_returns_and_timing` geprüft (bestanden), nicht zusätzlich von Hand an echten Daten.

## Lauf-Kennzahlen (aus SUMMARY_audit_svxy_term_structure_filter.md)
Zeitraum: bis 2022-12-31 (Holdout unberührt). Kosten 20 bps je Wechsel SVXY, 2 bps SPY. Steuern nur in der zweiten Tabelle.

| Lauf | Ab | Jahre | CAGR | Vol | Sharpe | MaxDD | Umsatz/J | Kosten/J | Kausal | ΔSharpe vs SPY (90-%-KI), p | DSR |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base (W = 1) | 2011-10 | 11,2 | 31,5 % | 47,8 % | 0,80 | -56,9 % | 6,5 | 2,62 % | ja | 0,00 (-0,45…0,34), p 0,48 | 0,99 |
| w025 (W = 0,25) | 2011-10 | 11,2 | 10,1 % | 15,0 % | 0,68 | -19,9 % | 1,7 | 0,67 % | ja | -0,13 (-0,61…0,24), p 0,66 | 0,97 |
| spy_secondary | 2006-07 | 16,4 | 8,6 % | 14,2 % | 0,59 | -33,8 % | 8,1 | 0,32 % | ja | 0,10 (-0,17…0,34), p 0,28 | 0,98 |

Nach Steuer (base): CAGR 24,2 %, Sharpe 0,68, Steuerlast 7,3 % p. a. SPY nach Steuer (gleiches Fenster) 12,0 %.
Regime-Split (Detailskript, nicht aus dem Lauf): -1x 2011-10 bis 2018-02-27 CAGR 50,2 %, Vol 56,5 %; -0,5x ab 2018-02-28 bis 2022-12-31 CAGR 10,3 %, Vol 33,0 %.
Anzahl Zeilen: 148 (147 Wechsel in 11,2 Jahren, ca. 13 pro Jahr). Anteil Tage mit Gewicht 1: ca. 35 %.
Umsatz-Hinweis: Die Summary-Angabe 6,5 / Jahr ist die Engine-Kennzahl (einseitig, halbiert). Mein Detailskript nutzt einen anderen Nenner und wird nicht als Gegenbeleg verwendet.

## Offene Punkte / nicht geprüft
- Fill-Sensitivität `close_next` und Kosten-Stress (0,5x / 2x) nicht gelaufen (Befund 5).
- Regime-Split nicht im offiziellen Lauf, nur ad hoc (Befund 1).
- Handrechnung nur auf synthetischen Daten. Engine-Renditen an echten Daten nicht von Hand nachgerechnet.
- Die Abbruchkriterien (MaxDD -60 %, Einzeltagesverlust -40 %) sind im Lauf nicht vollständig geprüft, weil das Stressereignis in Cash lag (Befund 3).
- Steuermodell vereinfacht (Durchschnittskosten, keine Vorabpauschale) laut `qlab/engine.py`. Nicht erneut geprüft.
- Datenqualität yfinance (auto_adjust, Splits, -1x/-0,5x-Umstellung im Kursverlauf) nicht gegen eine zweite Quelle geprüft.
- Die CXO-Angaben (CAGR 38 %) sind nach Spezifikation keine Erwartung und nicht Gegenstand dieses Audits.
- `results/SUMMARY_dev_svxy_term_structure_filter.md` und die dev-Dateien nicht ausgewertet.
- Keine Änderungen an `strategies/`, `qlab/`, `tests/`, `scripts/`, `research/` vorgenommen.
