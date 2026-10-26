# Audit bond_composite_3sig_longonly — 2026-10-21
Urteil: BESTANDEN MIT HINWEISEN
Geprüfte Module/Tests/Läufe: `strategies/bond_composite_3sig_longonly.py` (Hauptmodul, vollständig) und `strategies/bond_composite_3sig_longonly_etf.py` (Schwester, nur Unterschiede). Tests `tests/test_bond_composite_3sig_longonly.py` und `tests/test_bond_composite_3sig_longonly_etf.py`: 62 bestanden. Läufe `--ids bond_composite_3sig_longonly --tag audit_bond_composite_3sig_longonly --n-boot 200` und `--ids bond_composite_3sig_longonly_etf --tag audit_bond_composite_3sig_longonly_etf --n-boot 200`, beide ohne `--final`, Kausalitätstest bestanden (`causal_ok` = True, 0 übersprungene Orders). Spezifikation: `research/strategie-kandidaten.json`, Eintrag `selected`.

## Befunde
| Nr | Schwere (hoch/mittel/niedrig) | Datei:Zeile | Befund | Beleg (Zitat ≤ 2 Zeilen / Rechnung) | Korrekturvorschlag |
|---|---|---|---|---|---|
| 1 | mittel | `strategies/bond_composite_3sig_longonly.py:114-124` (`synthetic_returns`), Docstring Z. 1-10 | Die synthetische 10J-Total-Return-Reihe (Carry y/252 plus Duration-Preiseffekt) ist nicht gegen eine echte Anleihe-Reihe belegt. Die Spezifikation schließt Konvexität und Roll-down bewusst aus, das ist spec-konform. Der Abgleich zeigt aber eine systematische Lücke, die im Bericht nicht erklärt ist. | Eigene Rechnung 2003–2022 gegen `data_cache/px_IEF.parquet` (`docs/audits/_tmp/plaus_ief.py`): Korrelation der Tagesrenditen 0,946. Mittelwert 2,7 %/J synthetisch gegen 3,6 %/J IEF. Volatilität 7,7 % gegen 6,7 %. Überschlag Konvexitätseffekt ca. 0,5 pp/J (eigene Schätzung, nicht gemessen). Der Rest der Lücke ist nicht attribuiert (IEF hat kürzere Duration, Expense Ratio, Abweichung ^TNX gegen Anleihe). Die Duration-Formel `(1-(1+y/2)^-20)/y` ist für die Par-Anleihe korrekt (Test `test_par_duration_formula`). | Konvexitätsterm `0.5*C*Δy²` ergänzen oder den Effekt im Bericht quantifizieren. IEF-Abgleich (Korrelation, Mittel, Vol je Jahr) in den Bericht übernehmen, damit die Rekonstruktion belegt ist. |
| 2 | niedrig | `strategies/bond_composite_3sig_longonly.py:204` (`expected_inflation_monthly(shiller(...)["cpi"])`), Docstring Z. 36-39 | Die CPI-Quelle weicht von der Spezifikation ab (Spec: FRED CPIAUCNS, Code: Shiller ie_data, CPI-U nicht saisonbereinigt, endet 2024-09). Die Datumszuordnung auf Monatsende steht in `qlab/data.py:214`. Die zwei Monate Verzögerung sind konservativ gewählt. | Zitat Docstring: "CPI: FRED (CPIAUCNS) ist nicht erreichbar, stattdessen ... Shiller". | Quelle im Bericht als Abweichung ausweisen. Vor Live-Einsatz eine aktuelle CPI-Quelle anbinden, wie der Docstring selbst fordert. |
| 3 | niedrig | `strategies/bond_composite_3sig_longonly_etf.py:19-21` | Die Spezifikation verlangt Handel zum Schluss t_m+1. Die ETF-Variante handelt zur Eröffnung t_m+1 (Engine-Default `exec_mode="open"`). Der Docstring nennt das ausdrücklich. Kein Blick in die Zukunft, das Signal stammt weiterhin aus dem Schluss t_m. | Docstring Z. 19-21: "Das ist etwas anders als 'Schluss t_m+1' der Spec". Lauf mit `exec_mode="open"` (Standard). | Abweichung im Bericht ausweisen oder für den Vergleich `--exec close_next` zusätzlich laufen lassen. |
| 4 | niedrig | `strategies/bond_composite_3sig_longonly.py:75-101`, `strategies/bond_composite_3sig_longonly_etf.py:46-73` | `SPEC` enthält keinen Schlüssel `cost_bps`. Der Harness nutzt daher `default_bps=5.0` (`scripts/run_all.py:117-118`). Das entspricht der Spec (5 bp je Seite). Der Stresstest mit 20 bp (`--cost-mult 4`) ist nicht gelaufen. | Harness-Code: `default_bps=5.0 * args.cost_mult`, `spec.get("cost_bps") or {}` ist leer. | `cost_bps` explizit in SPEC eintragen. Stresslauf mit `--cost-mult 4` nachholen. |
| 5 | niedrig | `tests/test_bond_composite_3sig_longonly.py:562-563`, `tests/test_bond_composite_3sig_longonly_etf.py:299-300` | Die Integrationstests zu Ausführungstiming prüfen mit `abs=0.08` bzw. `> 0.5*dw`. Das fängt einen Zeitversatz um einen Monatsschritt (Gewichtssprung 1/3 oder mehr) ab, lässt aber Abweichungen bis 0,08 Gewicht durch. Der Test ist zu locker für den Nachweis des exakten Timings. | Zitat: `assert before == pytest.approx(w[A].shift(1).loc[s], abs=0.08)`. | Toleranz über Driftmodell exakt machen oder Drift über Einzeltag-Rechnung herausrechnen. |

## Spezifikationstreue (Hauptmodul, Zeilen)
- Instrumente: synthetische 10J-Par-Anleihe aus ^TNX/^IRX, Cash über French-RF (Engine). Stimmt mit Spec überein.
- Carry (Z. 240-253): Vergleichsfenster `v[i-window:i]` (Vortage, ohne heutigen Wert), Schwelle `> 1/3` strikt. Test `test_carry_vote_threshold_is_strictly_greater_than_one_third` bestätigt das.
- Trend (Z. 256-264): EWMA-Spannen 21 und 252 auf `ln(1+R10) - ln(1+Rc)`, beide > 0. Stimmt mit Spec.
- Value (Z. 267-276): Anker halbwertszeit 36 Monate über Monatsend-Samples. Die Umformung "real > ewma_t <=> real > ewma_{t-1}" ist korrekt (adjust=False).
- Zeitpunkt: Signal am Monatsende t_m, Engine handelt am Folgetag, Hauptmodul mit open == close, also Schluss t_m+1. Entspricht Spec.
- Gewichtsbereich: w in {0, 1/3, 2/3, 1}, Rest Cash. Kein Hebel, kein Short.
- Kosten: 5 bp je Seite (siehe Befund 4). Steuern über `TaxModel()` im Harness, Teilfreistellung für IEF/SHY 0 %.

## Look-ahead-Suche
- Grep auf `center=True`, `bfill`, `.last()`, `.iloc[-1]`, `shift(-` in beiden Modulen: keine Treffer.
- Monatsenden über `qlab.calendar.month_end_flags` (nicht `groupby().last()`).
- Auffüllung: nur `ffill(limit=5)` (kausal) für ^IRX und Signal-Spalten, `reindex(..., method="ffill")` für CPI. Keine Rückwärts-Füllung. ^TNX-Lücken werden nicht gefüllt (`idx = tnx.dropna().index`).
- Vollstichproben-Normierung: keine gefunden. Alle Statistiken sind expandierend oder Fenster-basiert.
- Kausalitätstest im Lauf: bestanden (main und ETF).

## Engine-Vertrag
- Index von `weights()` = Monatsende-Signaltage (`month_end_flags`), monoton, ohne Duplikate (Test bestätigt).
- Summe der Gewichte je Zeile = 1 bei ETF (IEF+SHY), ≤ 1 beim Hauptmodul. Kein Hebel.
- Gewichte nur bei gültigem Kurs (`valid`-Maske). Vor der ETF-Notierung 2002-07 keine Gewichte.
- ETF-Modul: Union der Handelstage von ETF und ^TNX geprüft. In den Cache-Daten 2002–2022 gibt es keinen Monatsletzten ohne IEF-Kurs (`docs/audits/_tmp/union_flags.py`: 246 Monatsenden, 0 ohne Kurs). Der Fehlerfall tritt hier nicht auf, bleibt aber bei künftigen Daten möglich.

## Handrechnung (kurz: Eingabe, erwartet, Modul)
- Eingabe: synthetisches Panel, 1000 Handelstage (`bdate_range` ab 1990-01-02, feste Zufallszahlen `default_rng(42)`), Carry-Fenster auf 100 verkürzt (Parameter, nur für die Rechnung), Trend 21/252, Value-Halbwertszeit 36 Monate.
- Unabhängige Neuimplementierung in Schleifen (`docs/audits/_tmp/handcalc_bond3sig.py`), ohne Modulfunktionen.
- Ergebnis: 11 gemeinsame Monatsenden, keine Abweichung (max. |Δ| = 0). Stichproben: 1992-12-31 Modul 0,0 = Hand 0,0; 1993-05-31 Modul 0,0 = Hand 0,0; 1993-10-29 Modul 0,333333 = Hand 0,333333.
- Schwäche der Rechnung: nur 11 Zeilen, die Stichproben sind überwiegend 0. Die Rechnung bestätigt Logik und Zeitpunkt, aber die Abdeckung der Zustände "2/3" und "1" ist schwach.

## Lauf-Kennzahlen (aus SUMMARY_audit_<id>.md)
Hauptmodul, Basislauf (Carry+Trend+Value), 1972-03 bis 2022-12, Kosten 5 bp, Ausführung open:
- CAGR 5,9 %, Vol 4,2 %, Sharpe 0,39, MaxDD −9,7 %, Umsatz 0,7/J, Kosten 0,07 %/J.
- Nach deutscher Steuer: CAGR 5,0 %, Sharpe 0,18.
- SPY im selben Zeitraum: CAGR 9,5 %, Sharpe 0,46, MaxDD −55,2 %. 60/40: CAGR 7,7 %, Sharpe 0,64.
- PBO 0,15, DSR 0,982. Sharpe-Differenz gegen SPY 0,01 (90%-KI −0,36 … 0,28, p = 0,495).
- Einzelsignale: only_carry Sharpe 0,41, only_trend 0,26, only_value 0,22.

ETF-Modul, Basislauf (IEF/SHY), 2002-07 bis 2022-12 (20,4 J), Kosten 5 bp:
- CAGR 3,0 %, Vol 3,8 %, Sharpe 0,49, MaxDD −8,7 %, Umsatz 1,3/J, Kosten 0,13 %/J.
- Nach Steuer: CAGR 2,2 %, Sharpe 0,27.
- SPY im selben Fenster: CAGR 9,4 %, Sharpe 0,50. Sharpe-Differenz gegen SPY −0,01 (KI −0,50 … 0,52).
- PBO 0,06, DSR 0,944.

Plausibilität: Umsatz und Kosten passen zu monatlichem Rebalancing. Kein Sharpe über 1,0, keine Warnung nötig. Die Rendite liegt deutlich unter SPY und ist in der Größenordnung eines Anleihe-Timings. Die Varianten zeigen keinen Vorteil über das Basismodell.

## Offene Punkte / nicht geprüft
- Abbruchkriterium der Spec (Sharpe des Komposits gegen statisches Portfolio mit mittlerer Quote, Block-Bootstrap p > 0,20) ist nicht gerechnet. Der Harness liefert diesen Vergleich nicht. Das ist der wichtigste offene Punkt zur Frage, ob der Timing-Anspruch überhaupt gilt.
- Stresslauf 20 bp (`--cost-mult 4`) nicht gelaufen (Befund 4).
- Euro-Anleihen und die Gültigkeit des US-Zinsregimes sind nicht geprüft (laut Spec-Notiz eigenes Thema).
- ^IRX (Yahoo) ist eine Diskontrate, keine Anleihenrendite. Der Effekt auf die Cash-Rendite des Signals ist nicht quantifiziert.
- Die Konvexitätsschätzung in Befund 1 ist eine Überschlagsrechnung, nicht gemessen.
- Gemeinsame Logdatei `docs/audits/_tmp/run_etf.log` wurde während des Laufs von einem anderen Prozess überschrieben (Inhalt enthielt einen xtsmom-Eintrag). Die Ergebnisse stammen aus den SUMMARY-Dateien mit den richtigen Tags (`results/SUMMARY_audit_bond_composite_3sig_longonly.md`, `results/SUMMARY_audit_bond_composite_3sig_longonly_etf.md`, je mit `causal_ok` = True). Die Kausalitätsprüfung ist dort über die CSV-Spalte belegt, nicht über das Log.
