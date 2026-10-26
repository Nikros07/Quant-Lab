# Audit index_etf_ibs_rsi2_longonly — 2026-10-21
Urteil: DURCHGEFALLEN (ein hoher Befund offen: Ausführungsreferenz des Standardlaufs weicht von der Spezifikation ab)

Geprüfte Module/Tests/Läufe:
- `strategies/index_etf_ibs_rsi2_longonly.py` (222 Zeilen), `qlab/engine.py` (Vertrag, `run_backtest`, `check_causality`), `qlab/data.py` (`load_ticker`, `Panel`)
- Spec: `research/strategie-kandidaten.json`, Eintrag `selected` mit id `index_etf_ibs_rsi2_longonly`
- Kein `_etf`-Schwestermodul vorhanden.
- `tests/test_index_etf_ibs_rsi2_longonly.py`: 52 Tests, alle bestanden (8,8 s)
- Lauf A (Auftrag): `run_all.py --ids index_etf_ibs_rsi2_longonly --tag audit_index_etf_ibs_rsi2_longonly --n-boot 200`, Standard-Ausführung `open`, Kausalität bestanden (causal_ok = True für alle 3 Läufe)
- Lauf B (zum Vergleich, Spezifikations-Hauptfall): gleicher Befehl mit `--exec close_next`, Tag `audit_index_etf_ibs_rsi2_longonly_closenext`, Kausalität bestanden
- Handrechnung: `docs/audits/_tmp/handcalc_ibs.py` (synthetisches Panel, 320 Tage, fester Seed 42)
- Kein `--final`, kein `--skip-causality`, Netz nur über den vorhandenen Cache (`data_cache/px_*.parquet`). Auswertung endet 2022-12-31 (`IS_END`), Holdout unberührt.

## Befunde

| Nr | Schwere | Datei:Zeile | Befund | Beleg | Korrekturvorschlag |
|---|---|---|---|---|---|
| 1 | hoch | `scripts/run_all.py:79` (Default `--exec open`), Modul `strategies/index_etf_ibs_rsi2_longonly.py:31-33` | Der Standardlauf des Projekts bildet die Spezifikations-Hauptausführung nicht ab. Die Spec verlangt "Kauf zum Schlusskurs t+1" (Hauptfall); der Harness-Default ist Eröffnung t+1, die laut Spec nur eine Sensitivität ist. Der Standardlauf liefert Sharpe 0,64 / CAGR 6,9 %; der spec-konforme Lauf Sharpe 0,45 / CAGR 5,4 %, also kein Vorsprung gegenüber SPY (Sharpe 0,46). Das Modul selbst ist korrekt (Handrechnung: Position 0 am Signaltag, 1 am Tag t+1 nach Schluss bei `close_next`). Verfälscht den Befund wesentlich. | `SUMMARY_audit_..._closenext.md`: "Ausführung: close_next", Rangliste Hauptlauf Sharpe 0,45 vs. `SUMMARY_audit_index_etf_ibs_rsi2_longonly.md`: Sharpe 0,64 | Berichte müssen beide Ausführungen nebeneinander ausweisen, und die Spec-Hauptausführung (`close_next`) gehört als Hauptergebnis. Nicht im Modul korrigieren, sondern bei der Auswertung. |
| 2 | mittel | Abbruchkriterium (Spec `abort_criterion`), `scripts/run_all.py` | Das Abbruchkriterium verlangt Signifikanz gegenüber exposure-gematchten Zufallseinstiegen (p > 0,10 verwirft). Der Harness rechnet dieses Vergleichsset nicht. Ersatzweise (Sharpe-Differenz gegen SPY): p = 0,17 (open) bzw. 0,52 (close_next), jeweils über 0,10. Nach dem Kriterium wäre die Strategie verworfen. | `summary_audit_..._csv`: `sharpe_diff_p` 0.17 / 0.52 | Zufallseinstiege mit gleicher Marktquote (Exposure ~21 %) implementieren und den p-Wert dagegen berechnen. |
| 3 | mittel | `tests/test_index_etf_ibs_rsi2_longonly.py:462-470` | Es gibt keinen Test für `exec_mode="close_next"`, obwohl das die Spec-Hauptausführung ist. Der einzige Ausführungstest prüft nur `open`, und dort mit `atol=1e-3`. Die Abweichung in Befund 1 wäre durch die Tests nicht aufgefallen. | Testcode: nur `run_backtest(p, w, exec_mode="open", ...)` | Test ergänzen: Kauf zu `close[t+1]`, Verkauf zu `close[u+1]`, exakte Gewichte. |
| 4 | niedrig | `qlab/engine.py:191-195` (Zusammenspiel mit Kosten) | Kosten werden nach der Größenbestimmung vom Cash abgezogen. Nach einem vollen Kauf liegt das Gewicht bei `close_next` bei 1,001 (Summe > 1). Ein kleiner, kostenbedingter Hebel ohne Spezifikation. Der Test toleriert 1e-3 (`test_engine_skips_nothing_and_exposure_is_at_most_one`). | Handrechnung Ausgabe: `exec=close_next ... t+1: 1.001` | Auf NAV nach Kosten dimensionieren oder Gewicht auf 1 begrenzen. Engine-Änderung, nicht Teil dieses Audits. |
| 5 | niedrig | Modul `load()` / Spec `tickers` | Spec nennt `^IRX` als Cash, das Modul nutzt die Fama-French-RF der Engine. Die Abweichung ist im Modul dokumentiert (Docstring Zeile 41-43 nennt Kosten, nicht die Cash-Quelle). | Spec-Feld `tickers` enthält `^IRX`; Modul `INSTRUMENTS = ["SPY", "QQQ", "IWM"]` | Im Bericht als Abweichung ausweisen. |

Geprüft ohne Befund:
- Signalregel: IBS = (C-L)/(H-L), strikt `< 0,20` und `> 0,70`, SMA200 strikt `C > SMA`, Haltedauer `i - t0 >= 5`, kein Einstieg am Ausstiegstag. Alles in `_flags` und `_target_states` (Zeilen 157-192) entspricht der Spec. Bei H == L kein Signal (Zeile 133).
- Zeitachse Signal/Ausführung: Signal am Schluss t, Handel `open[t+1]` (Standard) bzw. `close[t+1]` (`close_next`). Beides mit der Engine nachgerechnet, siehe Handrechnung.
- Look-ahead: kein `center=True`, kein `shift(-n)`, kein `bfill`/`ffill` auf Kursen, kein `groupby().last()`. Alle Fenster sind rückwärts (`rolling`, Wilder-RSI als Schleife). `load()` füllt nichts auf (Zeile 122).
- Gewichte nur an Tagen mit Kurs (`dropna` in Zeile 208); Engine meldet 0 übersprungene Orders.
- Cache-Qualität (SPY 1993-, QQQ 1999-, IWM 2000-): keine Zeile mit High < max(Open,Close) oder Low > min(Open,Close), kein H == L, keine NaN.
- Kausalitätstest bestanden für Basis und beide Varianten (Lauf A und B).

## Handrechnung (kurz)
Eingabe: synthetisches Panel, 320 Handelstage ab 2015-01-02, `default_rng(42)`. Eigene Neuimplementierung mit Schleifen, unabhängig vom Modul.
- Zustandsvergleich über alle Tage: 0 Abweichungen Modul vs. Neuimplementierung (Basisregel).
- Einstieg Signaltag t = 2015-10-21: Close 108,2480, IBS 0,105 (< 0,20), SMA200 102,8531 (Close darüber). Modul: Gewicht 1 an t.
- Engine `open`: Gewicht an t = 0,000, an t+1 = 1,000. Kaufpreis = open(t+1) = 108,1859. Erwartet: open(t+1). Stimmt.
- Engine `close_next`: Gewicht an t = 0,000, an t+1 = 1,001. Kaufpreis = close(t+1) = 109,0127. Erwartet: close(t+1). Stimmt, mit Befund 4 zum Gewicht.
- Ausstieg-Timing: nicht separat gerechnet, aber durch `test_engine_executes_entry_after_signal_day_and_exit_after_exit_signal` und die Szenariotests abgedeckt (Ausstieg am Signaltag u, Verkauf u+1).

## Lauf-Kennzahlen (aus SUMMARY_audit_index_etf_ibs_rsi2_longonly.md und ..._closenext.md)

Benchmark SPY (Buy&Hold, bis 2022-12-31): CAGR 9,5 %, Vol 18,9 %, Sharpe 0,46, MaxDD -55,2 %; nach Steuer CAGR 8,8 %, Sharpe 0,42.

| Lauf | Ausführung | CAGR | Vol | Sharpe | MaxDD | Umsatz/J (einseitig) | Kosten/J | ΔSharpe vs SPY (90 %-KI), p | Ø Marktquote | CAGR nach Steuer | Sharpe nach Steuer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Basis (Lauf A) | open | 6,9 % | 7,4 % | 0,64 | -15,6 % | 23,0 | 0,92 % | 0,19 (-0,13…0,48), p 0,17 | 21 % | 5,9 % | 0,52 |
| Basis (Lauf B, Spec) | close_next | 5,4 % | 7,4 % | 0,45 | -11,4 % | 23,0 | 0,92 % | -0,00 (-0,34…0,31), p 0,52 | 21 % | 4,7 % | 0,36 |
| connors_rsi2 (Lauf A) | open | 6,5 % | 6,7 % | 0,65 | -14,9 % | 7,7 | 0,31 % | 0,19, p 0,16 | 10 % | 5,6 % | 0,52 |
| connors_rsi2 (Lauf B) | close_next | 5,7 % | 6,5 % | 0,56 | -15,0 % | 7,7 | 0,31 % | 0,10, p 0,29 | 10 % | 5,1 % | 0,46 |
| no_sma200 (Lauf A) | open | 9,4 % | 12,3 % | 0,61 | -32,8 % | 33,6 | 1,34 % | 0,16, p 0,15 | 30 % | 8,0 % | 0,50 |
| no_sma200 (Lauf B) | close_next | 7,6 % | 12,0 % | 0,49 | -38,0 % | 33,6 | 1,34 % | 0,03, p 0,41 | 30 % | 6,5 % | 0,40 |

PBO (3 Läufe, gemeinsames Fenster ab 2004): 0,93. Deflated Sharpe in der Auswertung: 0,9996 (open), 0,9985 (close_next). Die DSR-Werte passen nicht gut zu einem PBO von 0,93 und sind nicht nachvollzogen. Keine Sharpe > 1,0, daher keine Warnung nach Schritt 8.

Plausibilität: Ø Marktquote 21 % liegt im erwarteten Bereich (20-35 %). Umsatz/J ist einseitig (Engine: `vol/2`), die Kosten (2 bp je Seite) stimmen damit überein (23 x 2 x 2 bp = 0,92 %).

## Offene Punkte / nicht geprüft
- Nicht gerechnet: QQQ und IWM als Einzelläufe (nur SPY, wie der Auftrag und `run_all` es vorsehen). Die Tests prüfen die Einzelinstrumente nur synthetisch.
- Nicht geprüft: Qualität der Yahoo-High/Low-Daten vor ca. 2000 gegen Originalquellen. Der Cache zeigt keine logischen Verletzungen, mehr ist nicht belegt.
- Nicht geprüft: Abbruchkriterium mit exposure-gematchten Zufallseinstiegen (fehlt im Harness, siehe Befund 2).
- Nicht geprüft: Wirkung der Spread-Annahme von 2 bp für SPY im Stress (5 bp, `--cost-mult 2.5`). Nicht gelaufen.
- Nicht geprüft: Ob die DSR-Werte korrekt berechnet sind (Widerspruch zum PBO 0,93, Befund oben).
- Wegwerf-Skripte und Logs liegen in `docs/audits/_tmp/` (handcalc_ibs.py, run_closenext.log). Ergebnisdateien in `results/` (`SUMMARY_audit_index_etf_ibs_rsi2_longonly*.md`, `summary_audit_*.csv`).
