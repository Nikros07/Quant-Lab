# Audit tom_spy_m2_p3 (und tom_spy_m2_p3_etf) — 2026-10-21
Urteil: BESTANDEN MIT HINWEISEN

Geprüfte Module/Tests/Läufe:
- Module: `strategies/tom_spy_m2_p3.py` (Hauptmodul, French-Gesamtmarkt 1926–2022), `strategies/tom_spy_m2_p3_etf.py` (Schwester, SPY 1993–2022)
- Spec: `research/strategie-kandidaten.json`, Eintrag `tom_spy_m2_p3` (Schwester nutzt denselben Basis-Eintrag)
- Tests: `tests/test_tom_spy_m2_p3.py` und `tests/test_tom_spy_m2_p3_etf.py`; zusammen 73 Tests bestanden
- Läufe: `scripts/run_all.py --ids tom_spy_m2_p3 --tag audit_tom_spy_m2_p3 --n-boot 200` und `--ids tom_spy_m2_p3_etf --tag audit_tom_spy_m2_p3_etf --n-boot 200`, beide Exit 0, Kausalitätstest in beiden Läufen bestanden (5 Schnitte). Kein `--final`, kein `--skip-causality`.
- Eigene Zusatzprüfungen (Skripte in `docs/audits/_tmp/`): Kalender-Orakel gegen Signaldaten, Handrechnung, dichte Kausalitätsschnitte, Teilperioden.

Hinweis zum Monatsende (Auftrag): Die Monatsende-Logik ist nicht vollständig kalenderbasiert. Der Endpunkt der Daten wird korrekt über den Kalender verlängert, aber innerhalb der Daten wird das Monatsende aus der nächsten Datenzeile abgeleitet (Befund 2) und vor 1990 fehlen Feiertage im Kalender (Befund 1). Beides verändert die Vollstichprobe nicht, verletzt aber die Vorgabe „nicht aus den Daten abgeleitet“ bzw. den Kausalitätstest.

## Befunde

| Nr | Schwere | Datei:Zeile | Befund | Beleg | Korrekturvorschlag |
|---|---|---|---|---|---|
| 1 | mittel | `qlab/calendar.py:52`; `strategies/tom_spy_m2_p3.py:113`, `:136` | Feiertage des NYSE-Kalenders gibt es erst ab 1990. Die Verlängerung des Datenindex (`_extend_index`) nutzt vor 1990 denselben Kalender und erzeugt so Scheinhandelstage (z. B. Memorial Day 30.05.1955, Karfreitag 1956 am 30.03.). Die Kausalität bricht dann bei abgeschnittenen Daten. | `check_causality` über Schnitte an den letzten 4 Tagen je Monat 1955–57: 11 von 144 Schnitten verletzt, z. B. 1955-05-26, 1956-03-27, 1957-11-26 (Signal nur im Vollauf vorhanden). | Feiertagsliste ab 1926 bzw. NYSE-Schließungen 1926–1989 ergänzen; Kausalitätstest mit dichten Schnitten 1955–60 ergänzen. Vollstichprobe nicht betroffen (Kalender-Vergleich siehe unten). |
| 2 | mittel | `qlab/calendar.py:74`; `strategies/tom_spy_m2_p3.py:141` | Monatsende wird für alle Datenzeilen außer der letzten über die nächste Datenzeile bestimmt (`nxt = idx[i + 1]`). Die Haltefenster sind Positionsoffsets im Datenindex (`s_in = int(p) + e_rel - 1`). Fehlt ein echter Handelstag in den Daten, verschiebt sich das Fenster; das Signal hängt dann von der Existenz einer Folgezeile ab. Der Test `test_last_trading_day_is_data_based_after_a_dropped_day` (`tests/test_tom_spy_m2_p3.py:173`) schreibt genau dieses Verhalten fest. | SPY und French fehlen beide am 1994-04-27 (NYSE-Handelstag). Signal landet am 1994-04-26 statt am 04-27. Dichtscan ETF 1993–2022 (1420 Schnitte): 1 Verstoß (1994-04-26, „nur voll: 1“). Ausführung bleibt am richtigen Tag (Close 28.04.). | Handelstage aus dem NYSE-Kalender erzeugen und fehlende Kurse als NaN behandeln statt die Zeilen des Datenindex zu zählen; den Test an der Kalenderbasis neu ausrichten. |
| 3 | mittel (Hinweis, kein Codefehler) | Lauf, `results/SUMMARY_audit_tom_spy_m2_p3.md` | Sharpe Vollstichprobe 0,80 liegt über der Spec-Erwartung nach Zerfall (0,30–0,60). Die Teilperioden zeigen, dass der Effekt fast vollständig vor 1993 liegt: 1926–92 Sharpe 1,03, 1993–2022 Sharpe 0,37, 2004–2022 Sharpe 0,25. Sharpe über 1,0 ist ein Warnsignal; hier erklärt durch die Stichprobe vor 1993 (Originalpaper: 1,04 für 1926–2005) und den Zerfall nach 1993. PBO = 0,77 für die drei Läufe. | Eigene Rechnung mit denselben Parametern und Kosten 2 bp je Seite (`run_backtest`, Teilperioden). | Keine Code-Änderung. Im Befund Vollstichprobe nicht als Beleg für eine heutige Rendite werten; maßgeblich ist der Zeitraum 1993+ (Sharpe ca. 0,3–0,4 nach Kosten, vor Steuern). |
| 4 | niedrig | `scripts/run_all.py:158` | Benchmark-Wahl: Der ETF-Lauf startet am 1993-02-24, also vor 1993-03-01, und wird deshalb gegen MKT (French-Gesamtmarkt) statt SPY verglichen. Die Spalten `spy_*` und „ΔSharpe vs SPY“ im ETF-Summary sind damit falsch benannt (MKT 1993–22: CAGR 9,7 %, Sharpe 0,47). | `results/summary_audit_tom_spy_m2_p3_etf.csv`, Spalte `bench` = MKT. | Schwelle an den tatsächlichen Modulstart koppeln bzw. ETF-Module mit SPY-Benchmark laufen lassen. `scripts/` nicht verändert. |
| 5 | niedrig | `strategies/tom_spy_m2_p3.py` (SPEC, Docstring) | Dokumentierte Abweichungen von der Spec: Cash wird mit French-RF verzinst statt SHY/BIL; die Spec-Ticker `^GSPC`, `SHY`, `BIL` werden nicht genutzt; die Variante „konservativ“ im Hauptmodul handelt Close statt Open (echte Open-Variante nur im ETF-Modul). | Docstring und `SPEC["tickers"] == ["MKT"]`. | Keine Änderung nötig; im Bericht ausgewiesen. |
| 6 | niedrig | `tests/test_tom_spy_m2_p3.py:301-338`; `tests/test_tom_spy_m2_p3_etf.py:170-183` | Die Kausalitätstests decken nur 2001–07, 2005–06, 1932–34 und 1952–53 ab. Die Schwächen aus Befund 1 (1955–60) und Befund 2 (1994-04) sind dadurch nicht abgedeckt. ETF-Test: nur 5 Schnitte, zwei Varianten. | Testdateien. | Dichte Schnitte an Monatsenden 1955–60 und 1994-04 als Tests aufnehmen. |

Geprüft ohne Befund:
- Spezifikationstreue (Hauptmodul und ETF): Instrument (Gesamtmarkt bzw. SPY), Signal d(-3) bzw. d(+2), Kauf Close d(-2), Verkauf Close d(+3), Haltefenster 4 Handelstage (ca. 19 % Exposure, gemessen 0,18–0,19), Kosten 2 bp je Seite (`SPEC["cost_bps"]`), kein Hebel, kein Short, Varianten 2 (plus Kosten-Stress über den Harness), vorab festgelegt.
- Ausführung: Engine-Vertrag eingehalten. Index der Gewichte = Signaltage; Summe der Gewichte je Zeile ≤ 1; keine Gewichte auf NaN-Kurse; `skipped_orders = 0`.
- Look-ahead im engeren Sinn: keine Fenster mit `center=True`, kein `bfill`, keine Normierung über die Vollstichprobe, kein `groupby(...).last()` auf den Daten. Die Signale hängen nicht von den Kursen ab (Test `test_signal_ignores_prices_entirely`). Der Datenendfall (Verlängerung um 6 Kalendertage) ist im Kern korrekt; Befund 1 betrifft nur die Vorkriegs-Verlängerung.
- Abgleich gegen unabhängiges Kalender-Orakel (Datenindex plus bekannter Lücke 1994-04-27) über alle Monate: Hauptmodul 1202 Einstiege und 1201 Ausstiege, 1 Abweichung (letzte Zeile 2026-08-27, offenes Fenster ohne Oracle-Ende); ETF 404 Einstiege, 2 Abweichungen (nur 1994-04, Befund 2), 0 bei den Ausstiegen.

## Handrechnung (kurz: Eingabe, erwartet, Modul)

Eingabe: synthetisches Panel, NYSE-Kalender 02.01.2001–30.06.2003 (630 Tage), `np.random.default_rng(42)`, `build_panel`. Erwartung von Hand (p = Position des letzten Handelstags d(-1)):

| d(-1) | Einstieg: Signal d(-3) = p-2, Ausführung Close d(-2) | Ausstieg: Signal d(+2) = p+2, Ausführung Close d(+3) | Modul |
|---|---|---|---|
| 31.08.2001 (Fr) | 29.08.2001 (1), Ausf. 30.08. | 05.09.2001 (0), Ausf. 06.09. (d(+1)=04.09., da 03.09. Labor Day) | identisch |
| 28.02.2002 (Do) | 26.02.2002 (1), Ausf. 27.02. | 04.03.2002 (0), Ausf. 05.03. | identisch |
| 30.05.2003 (Fr) | 28.05.2003 (1), Ausf. 29.05. | 03.06.2003 (0), Ausf. 04.06. | identisch |

Engine-Renditen im Fenster Feb 2002 (ohne Kosten, Zins 0) gleich der Marktrendite an den Fenstertagen, sonst 0 (absolute Abweichung ≤ 1e-12). Die Handrechnung hat die Haltetage d(-1), d(+1), d(+2), d(+3) bestätigt.

## Lauf-Kennzahlen (aus SUMMARY_audit_*.md, Zeitraum bis 2022-12-31, Kosten 2 bp je Seite, vor Steuer außer „nach Steuer“)

| Lauf | CAGR | Vol | Sharpe | MaxDD | Umsatz/Jahr | Kosten/Jahr | CAGR nach Steuer / Sharpe nach Steuer | Kausal |
|---|---|---|---|---|---|---|---|---|
| main base (1926–2022) | 8,9 % | 7,2 % | 0,80 | -23,2 % | 12,0 | 0,48 % | 7,8 % / 0,64 | ja |
| main konservativ | 8,1 % | 7,6 % | 0,67 | -28,8 % | 12,0 | 0,48 % | 7,1 % / 0,53 | ja |
| main tag_plus1 | 4,0 % | 3,7 % | 0,25 | -14,4 % | 12,0 | 0,48 % | 3,8 % / 0,20 | ja |
| etf base (1993–2022) | 4,8 % | 8,0 % | 0,35 | -17,7 % | 12,0 | 0,48 % | 4,2 % / 0,28 | ja |
| etf konservativ | 4,6 % | 8,2 % | 0,33 | -21,4 % | 12,0 | 0,48 % | 4,1 % / 0,27 | ja |
| etf tag_plus1 | 4,5 % | 4,5 % | 0,52 | -11,6 % | 12,0 | 0,48 % | 4,1 % / 0,42 | ja |

Vergleich (Harness): MKT-Buy&Hold 1926–2022 CAGR 9,8 %, Sharpe 0,45, MaxDD -84,1 %. SPY-Buy&Hold 1993–2022 CAGR 9,5 %, Sharpe 0,46, MaxDD -55,2 %. Deflated Sharpe: main base 1,00, ETF base 0,92, main tag_plus1 0,55. PBO: main 0,77, ETF 0,41.

Plausibilität: Exposure 18–19 % passt zur Spec (4 von ca. 21 Handelstagen). 12 Round-Trips pro Jahr (24 Trades) × 2 bp = 0,48 % Kosten pro Jahr, passt. Tagesrendite an Haltetagen im ETF (SPY, 1993–2022) ca. 21,5 % p.a. gegenüber ca. 8,4 % an den übrigen Tagen (arithmetisch, eigene Rechnung) — kein Anzeichen für Look-ahead; der Effekt ist nach Zerfall klein.

## Offene Punkte / nicht geprüft
- Lücken 1960–1989: Dichtscan nur stichprobenartig (Befund 1 über 1955–57 mit 11 Verstößen); der Harness-Test (5 Schnitte) hat keine Vorkriegs-Monatsenden getroffen.
- Dichte Kausalprüfung French 1990–2022 (die letzten 2 Handelstage jedes Monats, 782 Schnitte): 0 Verstöße. Vor 1990 ist sie nur stichprobenartig geprüft (Befund 1 über 1955–57).
- Varianten `--exec close_next`, `--cost-mult 0.5/2.5` (Kostenstress 1/5 bp) nicht gelaufen; Spec verlangt sie als Sensitivität, nicht als Audit-Pflicht.
- Steuer: Angaben aus der Harness-Berechnung (Verkauf zum Schluss angenommen), nicht separat nachgerechnet.
- Holdout (ab 2023) nicht geöffnet; keine Variante nach den Ergebnissen gewählt.
- Netzdaten: Harness hat den vorhandenen Cache bzw. yfinance genutzt wie das Projekt selbst; keine neuen Quellen.
- Scratch-Skripte und Logs liegen in `docs/audits/_tmp/` (`tom_*.py`, `*.log`); `docs/audits/_tmp/handcalc_ibs.py` gehört nicht zu diesem Audit.
