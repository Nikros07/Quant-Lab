# Audit halloween_nov_apr_equity (inkl. _etf) — 2026-10-21
Urteil: BESTANDEN MIT HINWEISEN
Geprüfte Module/Tests/Läufe: `strategies/halloween_nov_apr_equity.py` (Hauptmodul, inkl. Variante `dax`), `strategies/halloween_nov_apr_equity_etf.py` (Schwester, nur Unterschiede), `tests/test_halloween_nov_apr_equity.py` (42 Tests, alle bestanden; für `_etf` existiert keine Testdatei), `qlab/engine.py`, `qlab/calendar.py`, `qlab/data.py`, `scripts/run_all.py`; Läufe `--ids halloween_nov_apr_equity --tag audit_halloween_nov_apr_equity --n-boot 200` und `--ids halloween_nov_apr_equity_etf --tag audit_halloween_nov_apr_equity_etf --n-boot 200` (beide ohne Fehler, Kausalitätstest bestanden, kein `--final`). Spezifikation: `research/strategie-kandidaten.json`, Eintrag `halloween_nov_apr_equity` (Basis für beide Module).

## Befunde

Keine Befunde mit Schwere „hoch“. Ein Befund „mittel“, sieben „niedrig“.

| Nr | Schwere | Datei:Zeile | Befund | Beleg | Korrekturvorschlag |
|---|---|---|---|---|---|
| 1 | mittel | `strategies/halloween_nov_apr_equity.py:100` (Variante `dax`) | Der DAX wird als Yahoo-Index `^GDAXI` mit `auto_adjust=True` geladen. Ein Kursindex enthält keine Dividenden. Die Variante wird deshalb gegen Total-Return-Benchmarks (SPY, MKT) verglichen und vermutlich zu niedrig ausgewiesen. Die Variante hat außerdem 5 bp statt 2 bp Kosten (Zeile 27–28, Standard-Kosten). Vermutung aus der Datenquelle; im Cache nicht verifiziert. | `dax = load_ticker(DAX, start=DAX_START)["Close"]`; Harness-Lauf: `dax` CAGR 9.3 %, Kosten 0.10 %/J (5 bp), Basis nur 0.04 %/J. | Totalreturn-Reihe verwenden (z. B. DAX-ETF als TR-Proxy) oder Variante als Kursrendite kennzeichnen und nur gegen Kursindex vergleichen; Kosten auf 2 bp angleichen. Basisergebnis (French, Total Return) ist nicht betroffen. |
| 2 | niedrig | `qlab/calendar.py:71-74`, `strategies/halloween_nov_apr_equity.py:134`, `tests/test_halloween_nov_apr_equity.py:119-128` | Monatsende-Flag verwendet für jede Zeile außer der letzten den nächsten Datenindex-Eintrag (`idx[i+1]`), nicht den NYSE-Kalender. Der Docstring von `calendar.py` nennt genau diese Art Ableitung eine Falle und sagt „Kalender im Voraus bekannt“. Es fließen nur Datumsangaben, keine Kurse, in das Signal. Numerisch ab 1990 kein Unterschied (0 Abweichungen Datenindex vs. Kalender). Vor 1990 gibt es 89 abweichende Monatsenden, weil der Kalender Samstagshandel nicht kennt und Feiertage erst ab 1990 enthält. Der Test `test_holiday_gap…` codifiziert das Datenverhalten. | Skriptprüfung: nur Daten 8 / nur Kalender 1 (ab 1990); Monatsende-Abweichungen Daten/Kalender ab 1990 = 0; gesamt 89 (1926–1989). | Docstring und Testname ehrlich formulieren („Monatsende aus Handelsdatum-Index“). Optional Kalender um Samstage vor 1952 und pre-1990-Feiertage ergänzen, damit der Kalender-Pfad stimmt. |
| 3 | niedrig | `strategies/halloween_nov_apr_equity.py:22-25`; `qlab/engine.py` (exec_mode) | Spezifikation sieht MOC (Handel am Schluss von t) vor. Der Standardlauf des Harness (`--exec open`) handelt am Folgetag. Der Auftrag definiert „Handel t+1“ als Zeitpunkt, daher ist der Lauf regelkonform. Der MOC-Lauf der Spezifikation ist nur als Zusatz belegt. | Zusatzrechnung (Scratch): MKT 1926–2022 CAGR 8.32 % (open) vs. 8.46 % (close); SPY 1993–2022 7.64 % vs. 7.74 %. | Im Bericht beide Ausführungen nennen; Basis-Spezifikation präzisieren („Folgetag-Eröffnung“ oder MOC). |
| 4 | niedrig | `scripts/run_all.py:54-68` (Benchmarks) | Pflichtvergleiche der Spezifikation (konstanter 50/50-Mix, Rang des Nov-Apr-Fensters unter 12 Startmonaten, Abbruchkriterium) sind nicht Teil des Standardlaufs; das Abbruchkriterium wird vom Harness nicht ausgewertet. Nachgerechnet im Scratch (nur bis 2022-12-31, siehe Lauf-Kennzahlen): Rang 1 von 12 in beiden Datensätzen. Abbruch nicht ausgelöst, aber der Vorsprung gegen den 50/50-Mix ist klein (MKT 1999–2022: 0.40 vs. 0.36; SPY 1993–2022: 0.453 vs. 0.447). | Skript-Ausgabe: MKT Nov–Apr Rang 1 (Top-3 [11,10,7]), SPY Rang 1 (Top-3 [11,3,7]). | Pflichtvergleiche als Standardausgabe in den Harness aufnehmen; Abbruchkriterium explizit prüfen. |
| 5 | niedrig | `scripts/run_all.py:150-151` | Deflated Sharpe zählt nur die 2 bzw. 3 Harness-Läufe als Versuche. Die 12 Startmonate und der 50/50-Mix (Mining-Check der Spezifikation) fließen nicht ein. Der DSR von 1.000 ist damit überhöht. | `n_trials = len(runs)`; Summary: „Läufe: 2“ (Hauptmodul), „Läufe: 3“ (ETF). | Anzahl Versuche um die Mining-Startmonate erhöhen (mindestens 12) oder den DSR als nur innerhalb der Läufe gültig kennzeichnen. |
| 6 | niedrig | `strategies/halloween_nov_apr_equity_etf.py:22` | Docstring nennt für EFA „Yahoo-Cache ab 2006-03“. Der Lauf zeigt den ersten Entry 2001-10 (`long_px_EFA_2001.parquet` im Cache). Die Angabe ist veraltet. | Summary `halloween_nov_apr_equity_etf:efa` „ab 2001-10“. | Docstring auf 2001 korrigieren. |
| 7 | niedrig | `tests/` (fehlt: `test_halloween_nov_apr_equity_etf.py`) | Das `_etf`-Modul hat keine eigene Testdatei. Seine SPY-spezifischen Teile (Start 1993, Varianten `cash_ief` ab 2002-10 und `efa`) sind nur über den Harness-Lauf geprüft, nicht durch Tests. Die Logik selbst kommt aus dem getesteten Hauptmodul. | `ls tests/`: keine Datei `test_halloween_nov_apr_equity_etf.py`. | Kleine Testdatei: Varianten-Zeilen, NaN-Behandlung bei IEF/EFA, Start 1993. |
| 8 | niedrig | `tests/test_halloween_nov_apr_equity.py:73`, `:265` | Zwei schwache Assertions: `len(w) == 26 or … or len(w) > 20` ist praktisch immer wahr. Bei `test_last_data_day_mid_month…` ist die Bedingung eine Disjunktion, die fast immer erfüllt ist. | Zeile 73: `assert len(w) == 2 * 13 or len(w) == 2 * 13 - 1 or len(w) > 20`; Zeile 265: `assert not (…).any() or …max() < …`. | Exakte Anzahl der Signale aus dem Synthetik-Panel ableiten und prüfen; Disjunktionen aufspalten. |

Geprüft ohne Befund: Signal bei Oktober-/April-Monatsende mit Gewicht 1/0 (Zeile 134–146), keine Gewichte auf NaN-Kursen (`ok`-Maske, Zeile 138–141), kein Hebel und kein Short (one-hot, Zeile 141–146), DAX-Forward-Fill auf 5 Tage begrenzt und kausal (`ffill(limit=5)`, Zeile 92), Varianten höchstens 3 (Haupt: 1 + `dax`; ETF: Basis + `cash_ief` + `efa`), Kausalitätstest bestanden (`check_causality`, Lauf ohne „KAUSALITÄT VERLETZT“), Umsatz und Kosten passen zur Spezifikation.

## Handrechnung (kurz: Eingabe, erwartet, Modul)

- Eingabe: synthetisches Panel, Seed 20261021, Handelstage 2005-01-03 bis 2008-12-31 (1 003 Tage, 25.12. als Feiertagslücke), Eröffnung = Vortagsschluss × Rauschen, Kosten 0, RF 0.
- Signale: unabhängig bestimmt (letzter Datentag je Monat per eigener Gruppierung, nur Oktober/April): 8 Signale. Modul: 8 Signale, identisch in Datum und Wert.
- Tag 2006-10-31: erwartet Gewicht 1 (Entry), Modul 1. Tag 2007-04-30: erwartet 0 (Exit), Modul 0.
- NAV-Kette (Handel am Eröffnungskurs t+1, Kauf/Verkauf zu op[t+1], Haltung bis Eröffnung des Exit-Folgetags): an allen 8 Ereignistagen identisch zur Engine (z. B. 2006-11-01: erwartet 1.0279599001, Engine 1.0279599001; 2007-05-01: 1.1235710991 = 1.1235710991).

## Lauf-Kennzahlen (aus SUMMARY_audit_<id>.md, IS bis 2022-12-31, Kosten 2 bp je Seite, Steuern in Tabelle „nach Steuer“)

| Lauf | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | Umsatz/J | Kosten/J | CAGR nach Steuer |
|---|---|---|---|---|---|---|---|---|---|
| halloween_nov_apr_equity (Basis, French) | 1926-10 | 96.2 | 8.3 % | 11.8 % | 0.48 | −58.8 % | 1.0 | 0.04 % | 7.1 % |
| halloween_nov_apr_equity:dax | 1990-04 | 32.7 | 9.3 % | 15.3 % | 0.50 | −38.8 % | 1.0 | 0.10 % | 7.9 % |
| halloween_nov_apr_equity_etf (Basis, SPY) | 1993-04 | 29.7 | 7.5 % | 13.4 % | 0.45 | −34.6 % | 1.0 | 0.04 % | 6.4 % |
| halloween_nov_apr_equity_etf:cash_ief | 2002-10 | 20.2 | 8.0 % | 14.7 % | 0.52 | −35.6 % | 2.0 | 0.08 % | 6.3 % |
| halloween_nov_apr_equity_etf:efa | 2001-10 | 21.2 | 6.1 % | 14.8 % | 0.39 | −33.9 % | 1.0 | 0.04 % | 5.0 % |

Benchmarks aus dem Summary: SPY Buy&Hold 1993–2022 CAGR 9.5 %, Sharpe 0.46, MaxDD −55.2 %; MKT Buy&Hold 1926–2022 CAGR 9.8 %, Sharpe 0.45, MaxDD −84.1 %.
PBO: Hauptmodul „–“ (nur 2 Läufe), ETF 0.39 (3 Läufe, gemeinsames Fenster ab 2004).

Zusatzrechnung (Scratch, nicht im Summary; annualisierte Sharpe, IS bis 2022-12-31):
- MKT 1926–2022: Nov–Apr Sharpe 0.475 (open) bzw. 0.486 (MOC); 50/50-Mix 0.458; Buy&Hold 0.447.
- MKT 1999–2022: Nov–Apr 0.402 (open) bzw. 0.389 (MOC); 50/50-Mix 0.361.
- SPY 1993–2022: Nov–Apr 0.453 (open) bzw. 0.459 (MOC); 50/50-Mix 0.447; Buy&Hold 0.460.
- Mining-Rang (12 Startmonate, Sharpe nicht annualisiert): Nov–Apr = Rang 1 in allen vier Kombinationen (MKT/SPY × open/close).

Plausibilität: Expositionsmittel 0.49 (6 von 12 Monaten), Umsatz 1.0 einseitig/Jahr (2 Trades à 100 %), Kosten 0.04 %/J. Passt zur Spezifikation. Keine Sharpe über 1.0 (kein Warnsignal). Der Vorsprung ggü. dem 50/50-Mix ist klein (ca. 0.01–0.04 Sharpe) und statistisch nicht belegt (Harness p = 0.39–0.64 für Sharpe-Differenz).

## Offene Punkte / nicht geprüft

- Holdout ab 2023 nicht geöffnet (kein `--final`). Das Abbruchkriterium der Spezifikation (1999–2026) ist deshalb nur bis 2022 geprüft.
- Die Zusatzrechnungen (Mining-Rang, 50/50-Mix, MOC-Varianten) stammen aus Wegwerf-Skripten im Scratchpad; die Harness-Läufe selbst sind unverändert.
- Ob Yahoo `^GDAXI` tatsächlich ein Kursindex ist, ist nicht im Cache verifiziert (Befund 1 beruht auf der Datenquelle, nicht auf einer Messung).
- ffill-Lücken: DAX nur 5 Tage vorwärts gefüllt; ob ein Handel auf einem gefüllten Kurs vorkommt, nicht zählenmäßig geprüft.
- Steuermodell (qlab/tax, Engine) und Survivorship nicht geprüft; French-Reihen als Total Return vertraut.
- Originalquellen (Bouman/Jacobsen 2002, Zhang/Jacobsen 2012) nicht gelesen; Spezifikations-Zitate nicht verifiziert.
- Kausalitätstest nutzt nur 5 Schnittpunkte (30–95 % der Daten); für 1926–1989 mit Samstagshandel nicht gezielt geprüft (siehe Befund 2).
- Keine Dateien in `strategies/`, `qlab/`, `tests/`, `scripts/` verändert. Harness schrieb in `results/` (SUMMARY_audit_*, summary_audit_*, returns_common_audit_*, equity_audit_*). Logs liegen in `docs/audits/_tmp/`.
