# Audit ivp_risk_parity_unlevered — 2026-10-21
Urteil: BESTANDEN MIT HINWEISEN
Geprüfte Module/Tests/Läufe: `strategies/ivp_risk_parity_unlevered.py` (285 Zeilen, vollständig gelesen; kein `_etf`-Schwestermodul vorhanden). Test `tests/test_ivp_risk_parity_unlevered.py`: 48 bestanden (`.venv\Scripts\python.exe -m pytest tests/test_ivp_risk_parity_unlevered.py -q`). Lauf `scripts/run_all.py --ids ivp_risk_parity_unlevered --tag audit_ivp_risk_parity_unlevered --n-boot 200` (ohne `--final`, ohne `--skip-causality`), Exit 0, Kausalitätstest bestanden (`causal_ok` = True in allen 4 Läufen), 0 übersprungene Orders. Spezifikation: `research/strategie-kandidaten.json`, Eintrag `selected`, plus `research/families/riskparity.md` Abschnitt S2. Wegwerf-Prüfskript: `docs/audits/_tmp/audit_ivp_check.py`.

## Befunde
| Nr | Schwere (hoch/mittel/niedrig) | Datei:Zeile | Befund | Beleg (Zitat ≤ 2 Zeilen / Rechnung) | Korrekturvorschlag |
|---|---|---|---|---|---|
| 1 | mittel | `scripts/run_all.py` (liest `controls` nicht); `strategies/ivp_risk_parity_unlevered.py:89-92` | Die Spezifikation verlangt die 1/N-Kontrolle als mitlaufende Kontrolle. Der Harness führt sie nicht aus. Die SUMMARY enthält nur die 4 Läufe Basis + 3 Varianten. Damit ist das Abbruchkriterium aus dem offiziellen Lauf nicht auswertbar. | Modul-Kommentar: "Der Harness liest diesen Schlüssel nicht". Rechnung im Prüfskript: 1/N Sharpe 0,365, Basis 0,454 (siehe Handrechnung/Kennzahlen). | Die 1/N-Kontrolle als eigenen Lauf (eigener Tag) ausführen und die Zeile in den Bericht übernehmen, oder den Harness um `controls` erweitern. |
| 2 | mittel | Ergebnis, kein Code-Fehler: Abbruchkriterium, Spezifikation `abort_criterion` | Der Sharpe-Vorsprung gegen 1/N liegt bei 0,089 und damit unter der Schwelle 0,10. Das Verwerfen greift nur, wenn beide Bedingungen gelten. Die zweite Bedingung (MaxDD 2022 nicht besser als 1/N) ist falsch: Basis −17,4 % gegen 1/N −19,1 %. Also wird nicht verworfen, aber der Sharpe-Kriterium ist nicht erfüllt. | Prüfskript: Basis MaxDD 2022 −0,1740, 1/N −0,1906; Sharpe (summarize, ab 2008-02-29) Basis 0,454, 1/N 0,365; Differenz 0,089. | Im Bericht als Grenzfall ausweisen. Vor Freigabe entscheiden, ob die Schwelle 0,10 gilt. Keine Änderung am Code. |
| 3 | niedrig | `strategies/ivp_risk_parity_unlevered.py:67-93` (SPEC ohne `cost_bps`); `tests/test_ivp_risk_parity_unlevered.py:104` | Die Spezifikation nennt "Kosten 5 bp je Seite". Das steht nicht in `SPEC`. Der Wert kommt aus dem Harness-Default `default_bps=5.0` (`scripts/run_all.py`, CostModel-Aufbau). Der Test prüft das nicht: `assert "cost_bps" not in s or all(...)` ist immer wahr, weil der Schlüssel fehlt. | Zitat Test: `assert "cost_bps" not in s or all(v >= 0 for v in s["cost_bps"].values())`. | `cost_bps` mit 5 bp explizit in `SPEC` eintragen und den Test auf den Wert 5 setzen. |
| 4 | niedrig | `scripts/run_all.py` (`--cost-mult`) | Der Stresstest mit 15 bp (Spezifikation: "Stress 15 bp", `--cost-mult 3`) ist nicht gelaufen. | Kein Lauf mit `--cost-mult 3` vorhanden. | Stresslauf mit `--cost-mult 3 --tag audit_ivp_risk_parity_unlevered_cost3` nachholen. |
| 5 | niedrig | `qlab/engine.py:214-216` und `223-225` (Engine, nicht Modul) | Ein blockierter Handel (Kurs an t+1 fehlt) bleibt als `pending` stehen und wird an einem späteren Tag mit dem alten Ziel ausgeführt. Das widerspricht der Spezifikation "Ausführung zur Eröffnung t+1" im Fall einer Lücke. Auf den echten Daten ist es nicht ausgelöst: `skipped_orders` = 0. | Zitat engine.py:215: `if rebalance(op[i], pending, i): pending = None`. | Im Engine-Vertrag dokumentieren oder Ausführungen nach einer Lücke verwerfen. Nicht modulseitig. |
| 6 | niedrig | `tests/test_ivp_risk_parity_unlevered.py:274` | Der Test ERC gegen Inverse-Vol auf unkorrelierten Daten nutzt Toleranz 0,03. Das ist locker. Er prüft die Richtung, aber kaum die Genauigkeit des ERC-Lösers. Der Löser selbst ist über 25 Zufallsmatrizen mit Toleranz 1e-6 getestet (Zeilen 149-162). | Zitat: `assert (w_i - w_e).abs().to_numpy().max() < 0.03`. | Mit größerem Panel oder kleinerer Toleranz schärfen. Niedrig, weil der Löser separat exakt geprüft ist. |
| 7 | niedrig | `qlab/calendar.py:67-75` (Abhängigkeit des Moduls über `month_end_flags`) | Die Monatsende-Erkennung hängt am Panel-Index (Vereinigung aller Titel). Fehlt im Index der echte letzte Handelstag eines Monats, wird der Vortag als Monatsende erkannt. Auf den echten Daten gibt es 0 Abweichungen gegen den NYSE-Kalender (siehe Prüfung unten). | Prüfskript: "Flag-Abweichung Datenindex vs. NYSE-Kalender: 0 Tage". | Beibehalten. Bei neuen Daten Flags gegen den Kalender prüfen. |

Keine Befunde der Schwere „hoch“. Keine Look-ahead-Befunde (Details unten).

## Spezifikationstreue (Modul, Zeilen)
- Universum U9: `TICKERS` Z. 61, identisch mit `selected`-Eintrag (VTI, EFA, EEM, VNQ, IEF, TLT, TIP, GLD, DBC). Stimmt.
- Signal am Monatsende t: Z. 267 `month_end_flags(idx)` (kausal), Z. 268 `priced` (alle 9 Kurse an t vorhanden). Stimmt.
- Fenster: Z. 278 `ret[max(0, i-window+1):i+1]`, Renditen bis einschließlich t. Schätzung nur aus Daten bis t. Stimmt.
- Mindestbeobachtungen je Asset: Z. 215 (`ok.sum(axis=0) < min_obs`) und Gate Z. 272-273 (756 Zeilen, 504 Renditen). Stimmt.
- Volatilität: Z. 217 `std(ddof=1) * sqrt(252)`. Gewichte: Z. 220-221 `(1/sigma)/sum(1/sigma)`. Summe = 1, kein Hebel, kein Short. Stimmt.
- Varianten (Z. 84-88): `erc_lw` (756), `hrp_252` (252, min 168), `window_252` (252, min 168). Entsprechen den drei `sensitivity_variants`. Die Mindestzahl 168 ist eine dokumentierte Festlegung (Z. 49-50), keine Optimierung.
- Zeitpunkt: Signal Schluss t, Handel Eröffnung t+1 (Engine-Default `exec_mode="open"`, Harness-Default). Stimmt mit Spezifikation und riskparity.md.
- Haltedauer: bis zum nächsten Monatsende, Gewichte driften (Engine). Stimmt.
- Kosten: 5 bp je Seite über Harness-Default (siehe Befund 3). Stimmt inhaltlich.
- Steuern: über `TaxModel()` im Harness, nicht im Modul.
- Hinweis zu Spezifikation: `riskparity.md` S2 nennt eine optionale Levered-Variante L. Diese ist im Modul nicht enthalten. Die Spezifikation im JSON sagt "Kein Hebel". Kein Befund.

## Look-ahead-Suche
- Durchsicht der gesamten Datei: kein `center=True`, kein `shift(-`, kein `bfill`, kein `.iloc[-1]` über die ganze Reihe, kein `groupby().last()` für Monatsenden, keine Vollstichproben-Normierung.
- Lücken: `load_panel` füllt nicht (`qlab/data.py:97-111`, Kommentar "Lücken NICHT stillschweigend füllen"). Das Modul füllt ebenfalls nichts (Z. 19-22, 263-266).
- Gewichte auf NaN-Kurse: Zeile nur bei vollständigen Kursen (Z. 268). Auf echten Daten: 0 Zeilen mit NaN in mind. einem Titel ab 2008.
- Prüfskript: Zeitversatz-Test der Modul-Funktion (abgeschnittene Daten) durch den Harness-Kausalitätstest bestanden; zusätzlich Test `test_future_prices_do_not_change_past_weights` grün.

## Engine-Vertrag
- Index von `weights()` = Signaltage (179 Zeilen von 2008-02-29 bis 2022-12-30). Stimmt mit Monatsenden mit vollständigen Kursen überein (179 von 179).
- Summe je Zeile: max |Summe − 1| = 3,3e-16. Gewichte Bereich 0,036 bis 0,271, alle positiv, kein Short.
- Gewichte auf Titel ohne Kurs: keine. `skipped_orders` = 0.

## Handrechnung (kurz: Eingabe, erwartet, Modul)
- Eingabe synthetisch: 900 Handelstage, `default_rng(2024)`, Vol-Vektor [0,010 … 0,016], gemeinsamer Faktor, Renditen über `pct_change`. Eigene Neuimplementierung mit pandas-`std(ddof=1)` über 756 Zeilen, Gate 504.
- Ergebnis: 18 gemeinsame Signaltage. Auf den Vergleichstagen 2007-01-31, 2007-02-28, 2007-03-30, 2008-06-30 max |Abweichung| 1,4e-17 bis 0,0. Stimmt.
- Eine Zeile (2008-07-30) war nur in der Handrechnung enthalten. Ursache: es ist die letzte Zeile der Synthetik-Reihe, und dort entscheidet der Kalender (nächster NYSE-Tag 2008-07-31 = gleicher Monat), also kein Monatsende. Die Modulausgabe ist richtig, mein Handrechnungs-Skript hatte den letzten Index-Tag als Monatsende gesetzt.
- Schwäche: nur 2 unabhängige Entscheidungstage plus Stichproben, keine Zustände mit NaN in der Synthetik.

## Lauf-Kennzahlen (aus SUMMARY_audit_ivp_risk_parity_unlevered.md und summary CSV)
Zeitraum 2008-02-29 bis 2022-12-31 (14,8 J). Kosten 5 bp je Seite, Ausführung open, Steuern nicht enthalten.

| Lauf | CAGR | Vol | Sharpe | MaxDD | Umsatz/J | Kosten/J | Sharpe-Diff vs SPY (90%-KI) | DSR |
|---|---|---|---|---|---|---|---|---|
| Basis | 3,7 % | 7,3 % | 0,45 | −19,8 % | 0,18 | 0,02 % | −0,05 (−0,36…0,32), p 0,595 | 0,943 |
| erc_lw | 3,6 % | 7,0 % | 0,46 | −18,7 % | 0,18 | 0,02 % | −0,05 (−0,39…0,36), p 0,580 | 0,944 |
| window_252 | 3,4 % | 7,5 % | 0,41 | −20,0 % | 0,23 | 0,02 % | −0,10 (−0,38…0,26), p 0,685 | 0,919 |
| hrp_252 | 2,7 % | 6,3 % | 0,37 | −17,8 % | 0,51 | 0,05 % | −0,13 (−0,60…0,30), p 0,695 | 0,897 |

- SPY im selben Fenster (CSV `spy_cagr`/`spy_sharpe`/`spy_maxdd`): CAGR 9,3 %, Sharpe 0,51, MaxDD −51,5 %. Die Kopfzeile der SUMMARY nennt SPY 9,5 %, MaxDD −55,2 %; das ist die Vollhistorie ab 1993, nicht das Strategiefenster.
- Nach deutscher Steuer (Harness-Modell): Basis CAGR 3,0 %, Sharpe 0,36; SPY 7,9 %.
- 1/N-Kontrolle (Prüfskript, gleiche Engine und Kosten, gleiche Signaltage): CAGR 4,2 %, Vol 11,6 %, Sharpe 0,365, MaxDD −34,7 %, MaxDD 2022 −19,1 %.
- Sharpe über 1,0: nein (Warnsignal nicht ausgelöst). Erwartung laut Spezifikation 0,30–0,50: Basis 0,45 liegt darin.
- Plausibilität: Umsatz 0,18/J und Kosten 0,02 %/J passen zu monatlichem Rebalancing mit Anleihen-Anteil (Gewichte 2022: IEF 0,23, TIP 0,22). Mittlere Bruttoexponierung 0,9997, also voll investiert ohne Hebel. Die geringe Rendite ist mit der Anleihenlastigkeit der Konstruktion konsistent. Der Vorsprung gegen SPY liegt nicht vor, auch im Fenster ist die Differenz nicht signifikant.

## Offene Punkte / nicht geprüft
- Stresslauf 15 bp (`--cost-mult 3`) nicht gelaufen (Befund 4).
- Die 1/N-Kontrolle ist nur im Prüfskript gerechnet, nicht im offiziellen Harness-Lauf (Befund 1).
- Das Abbruchkriterium "Sharpe ≥ 0,10 über 1/N" ist nicht erfüllt (Befund 2). Die Schwelle und deren Anwendung sind eine Entscheidung für den Auftraggeber.
- Die lange Stichprobe (VFINX/VBMFX ab 1986) aus der Spezifikation ist nicht geprüft, ebenso die Levered-Variante L (nicht im Modul).
- Die Steuerrechnung im Harness (Teilfreistellung 30 %/60 %) ist nicht im Detail nachgerechnet.
- Der Vergleich mit der Vollhistorie-SPY-Zeile (9,5 %) ist ein Darstellungspunkt, kein Fehler.
- Keine Prüfung des Holdouts (ab 2023): bewusst nicht, `--final` ausgeschlossen.
