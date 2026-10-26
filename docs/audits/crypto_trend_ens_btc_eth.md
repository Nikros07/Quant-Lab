# Audit crypto_trend_ens_btc_eth — 2026-10-21
Urteil: BESTANDEN MIT HINWEISEN
Geprüfte Module/Tests/Läufe: `strategies/crypto_trend_ens_btc_eth.py`, `tests/test_crypto_trend_ens_btc_eth.py` (20 passed). Läufe: `scripts/run_all.py --ids crypto_trend_ens_btc_eth --tag audit_crypto_trend_ens_btc_eth --n-boot 200` und `--cost-mult 2 --tag audit_crypto_trend_ens_btc_eth_cost2 --n-boot 200`, beide Exit 0, keine Kausalitätsverletzung, ohne `--final`. Gegengelesen: `qlab/engine.py`, `qlab/calendar.py` (nicht vom Modul genutzt), `qlab/data.py`, `qlab/metrics.py`, `qlab/stats.py`, `scripts/run_all.py`, Spec-Eintrag `crypto_trend_ens_btc_eth` in `research/strategie-kandidaten.json`. Zusätzliche Wegwerf-Rechnungen in `docs/audits/_tmp/crypto_audit_check*.py`.

Hinweis vorab: Keine Befunde der Schwere „hoch“. Look-ahead, Regeltreue und Engine-Vertrag sind sauber. Die Kennzahlen sind aber nur Auswahlfenster 2015-09 bis 2022-12 (7,3 Jahre, ca. drei Zyklen). Sharpe 1,41 ist damit nicht belastbar, siehe Befund 3.

## Befunde
| Nr | Schwere | Datei:Zeile | Befund | Beleg | Korrekturvorschlag |
|---|---|---|---|---|---|
| 1 | mittel | `scripts/run_all.py:158` (Benchmarkwahl, `build_benchmarks` ab `:46`) | Der Harness vergleicht nur mit SPY, 60/40 und MKT. Das Abbruchkriterium der Spezifikation misst MaxDD und Sharpe aber gegen BTC Buy&Hold. In keinem Lauf steht BTC B&H. Nachgerechnet (Auswahlfenster, ohne Kosten): BTC B&H CAGR 79,4 %, Sharpe 1,15, MaxDD −83,4 %. Modul: CAGR 66,7 %, Sharpe 1,41, MaxDD −46,6 %. | `bn = "SPY" if first >= ... else "MKT"`; Summary zeigt nur SPY/60-40/MKT. Rechnung: `docs/audits/_tmp/crypto_audit_check.py` | BTC B&H als Benchmark für Krypto-Familie in `run_all` aufnehmen, Kriterium im Bericht ausweisen. |
| 2 | mittel | `strategies/crypto_trend_ens_btc_eth.py:74` (`return out[keep]`, Ausgabe jeden Tag) | Das Modul gibt jeden Tag ein Zielgewicht aus. Die Engine rebalanciert damit täglich auf 0,5·s_X (Drift wird jeden Tag zurückgeführt). Die Spezifikation rechnet Kosten nur bei Signalwechseln (Eigencheck 4.1/4.2, laut Docstring). Modul-Docstring nennt das „konservativer“. Der Effekt auf die Rendite ist aber größer als die Kosten: Mit Zeilen nur an Wechseltagen (643 von ca. 2650 Tagen) steigt der CAGR von 66,7 % auf 71,3 %, die Kosten sinken nur von 3,06 % auf 2,80 % p.a. Die Abweichung vom Spec-Vergleichsfall ist also eine Rendite-Frage, keine reine Kostenfrage. | Lauf-Summary: Kosten/J 3,06 %; Rechnung mit Wechsel-Zeilen: CAGR 0,7132, Kosten 0,0280 (`crypto_audit_check2.py`) | Entweder die Umsetzung der Spezifikation (nur Wechsel-Zeilen) übernehmen oder Drift-Rebalancing als eigene Variante ausweisen. Im Bericht beide CAGR nennen. |
| 3 | mittel | `scripts/run_all.py:150` (`n_trials`), `qlab/stats.py:38` (`deflated_sharpe`), Summary „DSR“/„PBO“ | Mehrfachtest-Maße sind nicht belastbar. (a) `n_trials` zählt nur die 3 Läufe dieses Aufrufs, nicht alle Selektionen des Projekts. (b) Die Varianz der Sharpe-Werte über 3 Läufe ist ein Fallback-Wert (2,1e-5), DSR 1,000 ist damit ohne Aussage. (c) PBO 0,89 ist bei 3 fast identischen Ein-Asset-Varianten (gleiche SMA-Regel, anderer Asset-Mix) kaum interpretierbar, hat aber als Warnung Gewicht. | Summary: „Läufe: 3 … Streuung … 2.11e-05 … PBO … 0.89“; DSR 1.000 in allen Zeilen | Versuchszahl projektweit führen; PBO nur mit ausreichend unabhängigen Varianten angeben. Bis dahin Mehrfachtest-Korrektur als „nicht ausgeführt“ melden. |
| 4 | mittel | `strategies/crypto_trend_ens_btc_eth.py:24` (Docstring), `tests/test_crypto_trend_ens_btc_eth.py:244`, Lauf `_cost2` | Stress-Lauf entspricht nicht dem Spezifikations-Stress. Die Spezifikation fordert 50 bp je Einheit (Abbruchkriterium „bei 50 bp Sharpe unter BTC B&H“). Der Auftrag fordert `--cost-mult 2`, das ergibt 40 bp. Der Docstring des Moduls nennt dagegen `--cost-mult 2.5` als Stress. Zwei Quellen widersprechen sich. Zusatzrechnung mit 2,5 (nicht Teil des Laufs): CAGR 59,2 %, Sharpe 1,30, MaxDD −51,1 %. Vergleich BTC B&H (ohne Kosten) Sharpe 1,15: Kriterium im Auswahlfenster erfüllt. | `_cost2`-Lauf: Kosten ×2, Sharpe 1,34; Rechnung mit ×2,5: Sharpe 1,298 | Stressläufe 50 bp (×2,5) offiziell nachholen, Docstring und Spec angleichen. |
| 5 | niedrig | `qlab/engine.py:156` und `:208`, `qlab/data.py:185` | Cash-Verzinsung auf 7-Tage-Index. `risk_free_daily` (French, nur Börsentage) wird mit `ffill` auf Kalendertage gelegt. Sa/So erhalten den Freitagswert, es werden also 7 statt 5 Tagessätze je Woche verzinst. Rechnung: mittlere Cash-Quote 0,557, RF p.a. auf Kalendertagen 1,37 % gegen 0,98 % auf Börsentagen → Überverzinsung ca. 0,22 Pp. p.a. | `rf.reindex(idx).ffill().fillna(0.0)`; Rechnung `crypto_audit_check2.py` | Für 24/7-Märkte RF über Kalendertage umrechnen (Tagessatz = Jahressatz/365) oder Krypto-Cash auf Börsentage beschränken. Effekt klein, aber systematisch. |
| 6 | niedrig | `qlab/stats.py:45` | `sr_annual` und `sr0_annual` werden mit √252 annualisiert, die Serie hat aber ca. 365 Beobachtungen p.a. (Krypto). Die Kennzahl-Spalten in `summary_audit_crypto_trend_ens_btc_eth.csv` sind damit um ca. 20 % falsch skaliert. Die Sharpe-Werte in `metrics.summarize` sind korrekt (`periods_per_year`). | `"sr_annual": sr * np.sqrt(252)` | Annualisierung mit `periods_per_year(idx)` (wie in `metrics.py`). |
| 7 | niedrig | `strategies/crypto_trend_ens_btc_eth.py:22` | Cash-Instrument weicht von Spezifikation ab. Spec nennt ^IRX, das Modul nutzt Fama-French RF (dokumentiert im Docstring). Effekt: ca. 1 % p.a. Zinsniveau im Fenster, ähnlich wie Befund 5. | Docstring: „^IRX … ist nicht im Panel“ | Im Spec-Eintrag vermerken; ^IRX-Cache (`px__idx_IRX.parquet`) wäre vorhanden. |
| 8 | niedrig | `tests/test_crypto_trend_ens_btc_eth.py:237-244` | `test_engine_stress_costs_are_higher` prüft nur `c50 > 2.0 * c20 * 0.9`, also eine lockere Schranke, und nutzt 2,5× statt der Spec-Stress-Stufe. Die übrigen Tests (Handrechnung, Kausalität, Future-Price-Invarianz, Open-Invarianz) sind echt und bestehen. | Assertion Zeile 244 | Exakte Erwartung ableiten (Kosten = 2,5 × Basis-Kosten bei gleicher Turnover). |

## Sachprüfung ohne Befund (was sauber ist)
* Regel und Zeitpunkt: `c > c.rolling(n).mean()` (SMA inkl. Close t, strikt größer), `keep` beschränkt auf `index >= 2015-09-01`. Signal am Schlusskurs t, Engine-Handel zum Open t+1 (`exec_mode="open"`). Stimmt mit Spec.
* Look-ahead-Suche: kein `center=True`, kein `shift(-k)`, kein `groupby(...).last()`, kein `bfill`, keine Vollstichproben-Normierung, kein `qlab.calendar` im Modul (also keine falsche NYSE-Logik auf 24/7-Daten). Keine Gewichte auf NaN-Kursen (Rechnung: 0 Tage mit ETH-Gewicht und NaN-Kurs). Lücken führen zu 0 für 199 Tage (konservativ, Test vorhanden).
* Gewichtssumme: 0 bis 1,0, kein Short, kein Hebel (Rechnung auf echtem Panel: Max Summe 1,0).
* ETH-Start: ETH-Listing 2017-11-09 (Cache), erster ETH-Gewichtstag 2018-06-08. Das ist kein Fehler: Vor dem Gewicht braucht es 200 Closes und dann mindestens eine SMA-Stimme. Ein Gewicht vor dem 200. Close wäre ein Fehler, dafür gibt es einen Test.
* Handrechnung: Synthetisches Panel, 420 Tage, Seed 11, eigene Schleifen-Implementierung an drei Tagen (2015-06-04, 2015-08-16, 2015-11-10). Erwartet BTC 0,5 / ETH 0 bzw. 0,375; Modul identisch (Abweichung 0).
* Tests: 20 bestanden. Referenzimplementierung, Kausalität, Vergangenheit-unabhängig von Zukunftspreisen, Open-Invarianz, Vorlaufwirkung. Schwach nur Befund 8.
* Kausalitätstest im Lauf: bestanden (kein Verletzungs-Eintrag in beiden Läufen).
* Annualisierung der Sharpe-Werte in `metrics.summarize`: `periods_per_year` aus dem Index (ca. 365), also korrekt.
* Turnover 7,7 Einheiten p.a. liegt in der Spec-Spanne „ca. 6–19“.

## Sharpe > 1 (Warnsignal, Einordnung)
* Sharpe 1,41 (Basis, 2015-09 bis 2022-12, 7,3 Jahre) liegt über dem Spec-Erwartungswert nach Decay von 0,6–1,0. Spec-Eigencheck war 1,38 vs B&H 1,10. Unsere Zahl ist also in der Nähe des Eigenchecks, nicht darüber.
* Der Vorteil ist vor allem Drawdown-Kontrolle: MaxDD −46,6 % vs −83,4 % (BTC B&H, eigene Rechnung), bei weniger CAGR (66,7 % vs 79,4 %).
* Bootstrap-Unsicherheit: ΔSharpe gegen SPY 90 %-KI −0,01 bis 1,57, also knapp an der Null. Gegen BTC B&H nicht im Lauf gerechnet (Befund 1).
* Die Zahl ist in-sample (Auswahl 2015–2022), der Holdout 2023–2026 ist nicht geöffnet. Die Spec sagt selbst: Aussagekraft durch ca. drei Zyklen begrenzt.

## Handrechnung (kurz: Eingabe, erwartet, Modul)
* Eingabe: synthetisches Panel, 420 Tage ab 2014-09-17, BTC und ETH (ETH ab Tag 200), Seed 11, `weights(panel, first_signal=None)`.
* 2015-06-04: erwartet BTC 0,5 / ETH 0,0; Modul 0,5 / 0,0.
* 2015-08-16: erwartet BTC 0,5 / ETH 0,0; Modul 0,5 / 0,0.
* 2015-11-10: erwartet BTC 0,5 / ETH 0,375; Modul 0,5 / 0,375.

## Lauf-Kennzahlen (aus `results/SUMMARY_audit_crypto_trend_ens_btc_eth.md`, Auswahlfenster bis 2022-12-31, ohne Steuer)
| Lauf | CAGR | Vol | Sharpe | MaxDD | Umsatz/J | Kosten/J | Hinweis |
|---|---|---|---|---|---|---|---|
| base (Kosten 20 bp) | 66,7 % | 41,4 % | 1,41 | −46,6 % | 7,7 | 3,06 % | Modul-Basislauf |
| Varianten SMA50-BTC | 93,6 % | 53,9 % | 1,47 | −58,5 % | 8,3 | 3,33 % | Variante, Sharpe 1,47 |
| Varianten SMA200-BTC | 82,7 % | 58,8 % | 1,30 | −69,9 % | 2,7 | 1,09 % | Variante, Sharpe 1,30 |
| base, Kosten ×2 (40 bp) | 61,7 % | 41,4 % | 1,34 | −49,3 % | 7,7 | 6,12 % | `_cost2`-Lauf, nicht 50 bp |
| base, Kosten ×2,5 (50 bp) | 59,2 % | — | 1,30 | −51,1 % | 7,7 | 7,66 % | nur Zusatzrechnung |
| BTC Buy&Hold (ohne Kosten) | 79,4 % | 73,7 % | 1,15 | −83,4 % | — | — | Zusatzrechnung |

Nach dem Lauf-Output: Benchmarks SPY 9,5 % / Sharpe 0,46 / MaxDD −55,2 %; 60/40 7,7 % / 0,64 / −32,5 %. Basis-Lauf ΔSharpe vs SPY 0,81 (90 %-KI −0,01 bis 1,57, p = 0,045). 5-Jahres-Fenster schlagen SPY zu 100 %.

## Offene Punkte / nicht geprüft
* Holdout 2023–2026 nicht geöffnet (kein `--final`). Das zweite Teil-Kriterium des Abbruchs („MaxDD-Vorteil gegen BTC B&H ab 2023 unter 20 Pp.“ bzw. Sharpe unter B&H bei 50 bp) ist damit offen.
* 50-bp-Stresslauf offiziell nicht gefahren (nur Zusatzrechnung mit ×2,5, Befund 4).
* Keine Steuerrechnung für Krypto-Direktbesitz (1-Jahres-Haltefrist durch Trendumschlag, Spec-Hinweis). Nicht Teil des Auftrags, nicht geprüft.
* Datenquelle: yfinance-Cache BTC/ETH (`auto_adjust`), keine Prüfung gegen Börsendaten. Netzabfrage nur über den Harness-Cache (max_age 3 Tage), keine eigenen Netzzugriffe.
* Spread und Gebühren der ETN/ETC (BTCE.DE, VBTC.DE) nicht gemessen (Spec sagt „ungemessen“), 20 bp ist Annahme.
* Zarattini/Han-Quellen nicht gegengelesen.
