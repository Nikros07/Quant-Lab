# Audit lowvol_defensive_longonly (und _etf) — 2026-10-21
Urteil: BESTANDEN MIT HINWEISEN
Geprüfte Module/Tests/Läufe: `strategies/lowvol_defensive_longonly.py`, `strategies/lowvol_defensive_longonly_etf.py`; `tests/test_lowvol_defensive_longonly.py` und `tests/test_lowvol_defensive_longonly_etf.py`, zusammen grün (51 passed). Läufe: `run_all.py --ids lowvol_defensive_longonly --tag audit_lowvol_defensive_longonly --n-boot 200` und `--ids lowvol_defensive_longonly_etf --tag audit_lowvol_defensive_longonly_etf --n-boot 200`, beide ohne Kausalitätsverletzung, ohne `--final`. Gegenlesen: `qlab/engine.py`, `qlab/calendar.py`, `qlab/data.py`, `scripts/run_all.py`, Spec-Eintrag `lowvol_defensive_longonly` in `research/strategie-kandidaten.json`.

Hinweis vorab: Das Urteil bezieht sich auf den Code. Das Abbruchkriterium der Spezifikation (Faktor-Ebene) ist laut meiner Rechnung erreicht, siehe Abschnitt "Abbruchkriterium" unten.

## Befunde
| Nr | Schwere | Datei:Zeile | Befund | Beleg | Korrekturvorschlag |
|---|---|---|---|---|---|
| 1 | mittel | `scripts/run_all.py:150` und `:168` (Deflated Sharpe) | DSR zählt nur die Läufe eines Aufrufs (Hauptmodul 2, ETF 3), nicht alle Versuche des Projekts. Beim Hauptmodul ist die Varianz der Sharpe-Werte der Fallback 1e-4 (weniger als 3 Läufe). DSR 1.000 bzw. 0.986 ist daher keine belastbare Mehrfachtest-Korrektur. | `n_trials = len(runs)`; `var_sr = ... if len(sr_all) > 2 else 1e-4`; Summary: "Streuung ... 1.00e-04" | Versuchszahl über alle Selektionsläufe des Projekts führen und im Bericht ausweisen, oder DSR nur mit Projektzähler ausgeben. |
| 2 | mittel | `strategies/lowvol_defensive_longonly.py:98-100`, `:154-160` (Helfer), Ausgabe SUMMARY | Die Monatsrenditen liegen nur an Monatsenden. MaxDD wird deshalb nur auf Monatsend-NAV gemessen (zu gering, Innermonatsverluste fehlen). Beta und Alpha werden auf Tagesrenditen gerechnet und sind bedeutungslos: Lauf zeigt beta 0.02 und alpha_ann 6.3 %. Der Modul-Docstring warnt zwar, die SUMMARY-Tabelle markiert es nicht. | Summary CSV: `beta 0.0207`, `alpha_ann 0.0628`, `max_dd -0.434`; Docstring: "MaxDD/Vol/Beta auf Tagesbasis sind fuer diese Reihe NICHT belastbar" | Beta/Alpha für diese Reihe aus dem Ergebnis streichen oder monatlich rechnen; MaxDD als Untergrenze kennzeichnen. |
| 3 | niedrig | `strategies/lowvol_defensive_longonly.py:98-100` | Erster Monat: die volle Monatsrendite wird ab der Basis des ersten Handelstags (Kurs 100) gutgeschrieben, der Kauf erfolgt aber erst am Folgetag. Die Rendite zwischen letztem Vormonatsschluss und Kauf (1-2 Handelstage) ist dadurch leicht zu hoch. Nicht quantifizierbar ohne Tageskurse. | `start_day = grid[grid >= first_m.start_time][0]`; Test-Beispiel: Jan-Endkurs 101.0 bei Basis 100 am 03.01.2005 | Ersten Monat erst ab Folgemonat handeln lassen oder Basis auf den letzten Vormonatsschluss legen. Auswirkung nur im Startmonat. |
| 4 | niedrig | `strategies/lowvol_defensive_longonly_etf.py:14` und `:64-69` | Spezifikation verlangt "Kauf zur Eröffnung des ersten Handelstags", Modul kauft zur Eröffnung von t+1 (Engine-Vertrag). Abweichung ist im Docstring dokumentiert. | Docstring: "Die Abweichung ist ein Handelstag" | Im Spec-Eintrag vermerken, dass der Engine-Vertrag gilt. Keine Codeänderung nötig. |
| 5 | niedrig | `qlab/calendar.py:91` (von `weekly_vol` genutzt, `..._etf.py:72-88`) | `week_end_flags` beginnt jede Woche auch am Jahreswechsel neu. Damit gibt es 2001 53 Wochenenden. Das "156-Wochen"-Fenster umfasst daher ca. 2,95 Jahre statt 3. Spec sagt "156 Wochen" ohne Festlegung. Der Test-Referenzwert `ref_weekly_vol` (Test:49-59) repliziert dieselbe Konvention, findet den Effekt also nicht. | Rechnung: 527 Wochenenden 2000-2009; 2001: 53. | Entscheiden, ob ISO-Wochen oder Kalenderwochen gelten, und dokumentieren. Falls ISO gewollt: Jahreswechsel-Split entfernen und Test anpassen. |
| 6 | niedrig | `tests/test_lowvol_defensive_longonly.py:226-234`; `tests/test_lowvol_defensive_longonly_etf.py:341-348` | Tests "alle Varianten laufen durch" prüfen nur `nav` endlich und > 0. Keine Prüfung auf Kennzahlen oder erwartete NAV. Die Sektor-Test-Daten sind synthetisch mit festen Volatilitäten, daher ist die Auswahl dort trivial eindeutig. | Assertion: `np.isfinite(res.nav).all() and (res.nav > 0).all()` | Pro Variante eine Handrechnung-NAV als Assert ergänzen. |
| 7 | niedrig | `results/SUMMARY_audit_lowvol_defensive_longonly_etf.md` (Kopf) | Die Kopfzeile "SPY: CAGR 9.5 %, Sharpe 0.46, MaxDD -55.2 %" ist die Vollperiode ab 1993. Der Vergleich der ETF-Läufe (ab 2011) verwendet SPY im Fenster 2011-2022 mit CAGR 13.0 %, Sharpe 0.76, MaxDD -33.7 %. Ohne Hinweis ist das für den Leser verwirrend. | summary_csv: `spy_cagr 0.1296`, `spy_sharpe 0.7587` (Lauf 0) | Kopfzeile je Fenster ausweisen. |

Keine Befunde der Schwere "hoch". Die Prüfpunkte aus dem Auftrag sind so abgedeckt:
* Look-ahead im Code: keiner gefunden. `weekly_vol` nutzt `pos = np.cumsum(wk) - 1` (kausal, nur bis t). `month_end_flags`/`week_end_flags` kommen aus `qlab.calendar` (nächster Datentag, kein `groupby.last()`). Keine `center=True`, kein `bfill`, keine Vollstichproben-Normierung. Kausalitätstest bestanden (kein Eintrag in den Läufen). Zusätzlich Test "Zukunftsdaten verändern ändert keine Vergangenheitsgewichte" vorhanden und grün.
* Gewichte je Zeile ≤ 1: Hauptmodul 1.0, ETF-USMV/SPLV 1.0, Sektor-Proxy Summe 1.0 (je 1/3). Kein Hebel, kein Short. Keine Gewichte auf NaN-Kurse (Test und Handrechnung).
* Spezifikation: Universum (Lo 20 BETA/VAR, USMV, SPLV, SPY, XLB..XLY ohne XLRE/XLC), Signal am Schluss von t, Handel t+1, Varianten (3 vorab festgelegt: VAR, SPLV, Sektor-Proxy), Hebel (keiner) stimmen mit der Spezifikation überein, außer Befund 4. Kosten: `SPEC` enthält kein `cost_bps`; es gelten die Standardkosten 5 bps/Seite. Faktor-Ebene ist brutto (kein Umschlag innerhalb French-Portfolios).

## Handrechnung (kurz: Eingabe, erwartet, Modul)
* Sektor-Proxy: synthetisches Panel, 9 Sektoren, 2515 Handelstage (2000-01-03 bis 2009-12-31, Seed 42). Unabhängige Neuimplementierung (Wochenschluss je Kalenderjahr/ISO-Woche, letzte 156 Wochenrenditen, Std ddof=1, drei kleinste) an drei Monatsenden:
  * 2005-01-31: erwartet XLF, XLP, XLV; Modul XLF, XLP, XLV; Std-Abweichung max 3e-17; Gewichte je 1/3.
  * 2006-09-29: erwartet XLF, XLP, XLV; Modul gleich; Abweichung 3e-17.
  * 2007-12-31: erwartet XLF, XLP, XLU; Modul gleich; Abweichung 3e-17.
* Hauptmodul: Monatsrenditen Jan-Apr 2005 (+1 %, -2 %, +3 %, +0,5 %). Modul-Monatsende relativ zu Januar: Feb 0,98; Mär 1,0094 (= 0,98 x 1,03); Apr 1,014447 (= x 1,005). Entspricht der Kettenrechnung. Gewicht [1.0] am 03.01.2005 (erster Kurstag).

## Lauf-Kennzahlen (aus SUMMARY_audit_<id>.md / summary CSV, ohne Steuer, 5 bps)
Hauptmodul (1963-07 bis 2022-12, 59,5 Jahre):
| Lauf | CAGR | Vol | Sharpe | MaxDD | Umsatz/J | nach Steuer CAGR / Sharpe |
|---|---|---|---|---|---|---|
| base (Lo 20 BETA) | 10,4 % | 12,6 % | 0,51 | -43,4 % | 0,84 % (nur Einstieg) | 10,1 % / 0,48 |
| var (Lo 20 VAR) | 11,2 % | 12,6 % | 0,56 | -42,3 % | 0,84 % | 10,8 % / 0,53 |
| Vergleich MKT (Ken French, 1963+) | 10,2 % | — | 0,41 | -55,6 % | — | — |

ETF (USMV ab 2011-10-20, SPLV ab 2011-05-05, Sektor-Proxy ab 2001-12-31):
| Lauf | Zeitraum | CAGR | Vol | Sharpe | MaxDD | Vergleich SPY im selben Fenster | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|
| USMV | 11,2 J | 11,8 % | 14,2 % | 0,81 | -33,1 % | CAGR 13,0 %, Sharpe 0,76, MaxDD -33,7 % | 4,5 % (nur Einstieg) | 0,005 % |
| SPLV | 11,7 J | 10,9 % | 15,3 % | 0,71 | -36,3 % | CAGR 11,5 %, Sharpe 0,67, MaxDD -33,7 % | 4,3 % | 0,004 % |
| Sektor-Proxy | 21,0 J | 7,8 % | 15,5 % | 0,49 | -41,6 % | CAGR 7,9 %, Sharpe 0,43, MaxDD -55,2 % | 0,53 | 0,05 % |

Nach Abgeltungsteuer (Summary-Zusatztabelle): USMV 10,4 % vs SPY 11,1 % (Überrendite -0,6 pp); SPLV 9,6 % vs 9,7 %; Sektor-Proxy 6,8 % vs 6,9 %.
Plausibilität: alle Sharpe < 1,0, keine Warnschwelle. USMV-Beta zum Markt 0,76, Alpha 1,6 % p.a. (Summary, daily). Umsatz beim Buy&Hold ist nur der Einstiegskauf. Der Sektor-Proxy liegt bei 0,53 Umschlag/Jahr, das passt zu Monatsrebalancing von 3 aus 9.

## Abbruchkriterium der Spezifikation (nicht Code, aber Ergebnis)
* Faktor-Ebene (`alpha_split_from_french`, French bis 2022-12-31): Alpha nach 2008 t = 1,14 (n = 180, 1,57 % p.a.); vor 2008 t = 2,02; gesamt t = 2,31. Spec: "auf Faktor-Ebene verwerfen, wenn der Alpha-t-Wert nach 2008 < 1,65 ist" → Kriterium erfüllt, Verwerfen nach Spezifikation.
* ETF-Ebene: Sharpe-Differenz zu SPY (2011-) = +0,05 (90 %-KI -0,13 bis 0,27, p = 0,33). Kriterium ist "Sharpe-Diff <= 0 UND MaxDD nicht mindestens 5 pp besser". Die Sharpe-Diff ist > 0, daher nicht verworfen, aber knapp und statistisch nicht von 0 zu unterscheiden. MaxDD-Vorteil nur 0,6 pp.

## Offene Punkte / nicht geprüft
* Sortierung nach Beta/Varianz (Ken French, Tabelle 0 = value-weighted, Rebalancing-Termine, nur Daten bis t): nicht in diesem Code, daher nicht prüfbar. Die Cache-Daten zeigen plausible Werte (Lo 20 BETA mittlere Monatsrendite 0,90 %, Hi 20 1,17 %), die Formationsregel selbst habe ich nicht gegen Ken French verifiziert (kein Netzabruf, nur Cache).
* Survivorship bei French-Portfolios (CRSP-basiert, Delisting-Behandlung): nicht geprüft. ETF-Universum: die 9 SPDR-Sektoren existierten alle ab 1998-12, daher kein Auswahl-Bias durch Ausfall. Der Sektor-Universum-Bias ist damit gering, aber nicht null (Auswahl nach heutigem Stand der Liste).
* Holdout: `load()` in beiden Modulen schneidet nicht ab (Caches reichen bis 2026). Die Abschneidung erfolgt im Harness (`run_all` ohne `--final`). Ich habe `--final` nicht genutzt und keine Daten ab 2023 für Auswahl oder Bewertung verwendet, außer das Faktor-Alpha ist explizit bei 2022-12-31 abgeschnitten.
* Spec-Zahl "USMV 0.90 vs SPY 0.94 seit 2011" (Spec-Text) weicht vom Lauf ab (USMV 0.81 vs SPY 0.76, gleiche Periode bis 2022-12). Nicht erklärt.
* Steuer-Berechnung (Engine) nicht im Detail geprüft; sie ist nicht Teil des Auftrags.
* Keine Netzabfragen über Cache/yfinance hinaus. Der `run_all`-Lauf nutzte vorhandene Caches.

Hilfsskript (Wegwerf, nur lesend): `docs/audits/_tmp/lowvol_audit_check.py`. Die Laufdateien liegen in `results/` (SUMMARY_audit_*.md, summary_audit_*.csv), das gehört zum Projekt-Lauf.
