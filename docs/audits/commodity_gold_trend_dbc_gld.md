# Audit commodity_gold_trend_dbc_gld — 2026-10-21
Urteil: BESTANDEN MIT HINWEISEN

Geprüfte Module/Tests/Läufe: `strategies/commodity_gold_trend_dbc_gld.py` (kein `_etf`-Schwestermodul vorhanden); `tests/test_commodity_gold_trend_dbc_gld.py` (37 passed); Lauf `scripts/run_all.py --ids commodity_gold_trend_dbc_gld --tag audit_commodity_gold_trend_dbc_gld --n-boot 200` (ohne `--final`, ohne `--skip-causality`, Kausalitätstest bestanden, 0 übersprungene Orders). Spec: `research/strategie-kandidaten.json`, Eintrag `commodity_gold_trend_dbc_gld` (in `selected`). Gegengelesen: `qlab/engine.py` (Vertrag, `check_causality`), `scripts/run_all.py`. Wegwerf-Skripte: `docs/audits/_tmp/commodity_gold_handcalc.py`, `docs/audits/_tmp/commodity_gold_bh.py`, Log `docs/audits/_tmp/run_commodity_gold.log`.

Kurzurteil: Kein Look-ahead, kein Hebel, Engine-Vertrag eingehalten, Handrechnung stimmt exakt. Die Abweichungen zur Spezifikation sind klein oder dokumentiert. Die Stichprobe (16 Jahre, Basislauf) trägt keine Edge-Aussage: Die Sharpe-Differenz zum SPY ist negativ und das 90-%-KI reicht von -0,62 bis +0,30. Das Ergebnis ist als Risikominderungs-Kandidat zu lesen, nicht als belegter Vorteil.

## Befunde
| Nr | Schwere | Datei:Zeile | Befund | Beleg | Korrekturvorschlag |
|---|---|---|---|---|---|
| 1 | mittel | `scripts/run_all.py:150-151`, `:168` (Deflated Sharpe) | Die Mehrfachtest-Korrektur zählt nur die 4 Läufe dieses Aufrufs (`n_trials = len(runs)`). Die Streuung der Sharpe-Werte über diese 4 Läufe ist winzig (8,35e-06), dadurch ist die erwartete Maximum-Sharpe-Schwelle sr0 nur 0,048 p.a. Der DSR von 0,897 (Basislauf) ist damit praktisch der PSR und keine echte Korrektur. PBO wird nicht berechnet ("–", 0 Läufe im gemeinsamen Fenster ab 2004, weil DBC erst 2006 Kurse hat). | Summary: "Läufe: **4** ... Streuung ... 8.35e-06 ... PBO ... **–**"; CSV `sr0_annual` = 0,048 | Versuchszahl über alle Selektionsläufe des Projekts führen; PBO auf gemeinsamem Fenster ab 2006-12 ausweisen. |
| 2 | mittel | Spec-Eintrag `research/strategie-kandidaten.json` (Feld `abort_criterion`, `expected_sharpe_after_decay`); Lauf `results/summary_audit_commodity_gold_trend_dbc_gld.csv` | Aussagekraft: Basislauf 16,1 Jahre (2006-12 bis 2022-12). Sharpe-Differenz zu SPY -0,10, 90-%-KI -0,62 bis +0,30, p = 0,63; 5-Jahres-Fenster über SPY nur 13 %. Dekade 2006-2015: Sharpe +0,24 gegenüber 50/50-Buy&Hold; Dekade 2016-2022: -0,18. Das reicht nicht für eine Edge-Aussage. Der Holdout ab 2023 bleibt unangetastet, eine Prüfung der Spec-Dekade 2016-2026 ist deshalb nicht möglich. | Lauf-CSV `sharpe_diff_vs_spy` -0,10, `sharpe_diff_ci_lo` -0,62, `sharpe_diff_ci_hi` +0,30, `share_5y_beating_spy` 0,13; Handrechnung `commodity_gold_bh.py`-Ausgabe | Keine Edge-Behauptung; Ergebnis als Risikominderungs-Kandidat führen. Dekaden-Befund im Logbuch festhalten. |
| 3 | niedrig | `strategies/commodity_gold_trend_dbc_gld.py:27` | Spec-Abweichung Cash: Spec verlangt Cash-Zins über ^IRX, die Engine verzinst Cash mit Fama-French-RF. Die Abweichung ist im Modul-Docstring dokumentiert, im Spec-Eintrag aber nicht vermerkt. Auswirkung nicht quantifiziert (beides T-Bill-nahe Sätze). | Docstring: "die Engine verzinst Cash mit dem Fama-French-RF (nicht mit ^IRX)"; Spec: "Rest Cash (^IRX)" | Spec-Eintrag auf FF-RF angleichen oder ^IRX als Cash-Reihe in die Engine geben und Differenz rechnen. |
| 4 | niedrig | `strategies/commodity_gold_trend_dbc_gld.py:86-88` (Zeilen nur bei Zielwechsel), Docstring Zeile 19 | Rebalancing-Interpretation: Spec sagt "täglich prüfen", das Modul schreibt Zielzeilen nur bei Zielwechsel. Zwischen Signalen driften die Beine (keine Rückführung auf 0,5/0,5). Die Interpretation passt zur Spec-Angabe ca. 7,5 Einheiten Umschlag/Jahr (gemessen: 7,8 beidseitig), ist aber als Spec-Mehrdeutigkeit zu behandeln. | Modul: `changed = (w != w.shift(1)).any(axis=1)`; Messung `docs/audits/_tmp/commodity_gold_handcalc.py`: 249 Signalwechsel in 16 J, Summe abs(dw) 7,81/J | Im Spec-Eintrag klarstellen: Rebalancing nur bei Signalwechsel (Drift zwischen Signalen zulässig). |
| 5 | niedrig | `strategies/commodity_gold_trend_dbc_gld.py:47` (Kommentar) und Spec-Feld `data_start` ("2006-06") | Datenangaben widersprechen sich: Kommentar "DBC startet im Cache am 2006-03-01", Spec-Feld `spec` "DBC ab 2006-02-06". Gemessen: erster DBC-Kurs 2006-02-06 (17 Kurse vor 2006-03-01). Spec-`data_start` 2006-06 ist mit SMA-210-Anlauf nicht konsistent: erstes Signal im Lauf ist 2006-12-04. | `load_panel` in der Handrechnung: `DBC erster Kurs 2006-02-06`; Lauf: erster Signaltag 2006-12-04 | Kommentar und Spec-Feld auf 2006-02-06 / 2006-12 korrigieren. Keine Codewirkung. |
| 6 | niedrig | `tests/test_commodity_gold_trend_dbc_gld.py:102` | Der Test `test_spec_contract` prüft `"^IRX" not in s["tickers"]` und schreibt damit die Cash-Abweichung (Befund 3) als erwartetes Verhalten fest. Die Konvention ist damit getestet, aber nicht gegen die Spec. | `assert s["tickers"] == ["DBC", "GLD"] and "^IRX" not in s["tickers"]` | Test nach Entscheidung zu Befund 3 anpassen; bei Angleichung der Spec Test beibehalten. |
| 7 | niedrig | `tests/test_commodity_gold_trend_dbc_gld.py:336-342` | `test_engine_runs_without_skipped_orders_and_never_levered` prüft die NAV nur auf endlich und > 0, keine Kennzahl und keine Handrechnung. Die Referenz-Tests nutzen dieselbe `dropna`-Konvention wie das Modul (keine unabhängige NaN-Prüfung). | `assert np.isfinite(res.nav).all() and (res.nav > 0).all()` | Pro Variante eine Handrechnung-NAV an einem synthetischen Panel als Assert ergänzen. |
| 8 | niedrig | Lauf-Kopf `results/SUMMARY_audit_commodity_gold_trend_dbc_gld.md` | Der Kopf "Kosten sind enthalten (5 bps pro Seite Standard)" trifft für DBC/GLD nicht zu: die Module laufen mit 10 bp je Seite (`per_ticker_bps`). Nur die Benchmarks (SPY, 60/40, MKT) nutzen 5 bp. Die Zahlen sind damit korrekt, der Text irreführend. | `CostModel(per_ticker_bps={"DBC": 10.0, "GLD": 10.0})` im Harness; Kopfzeile "5 bps" | Kopfzeile je Instrument ausweisen. |

Keine Befunde der Schwere "hoch". Geprüfte Punkte ohne Befund:
* Look-ahead: keines gefunden. Keine `center=True`, kein `shift` in falscher Richtung, kein `bfill`, kein `ffill`, kein `iloc[-1]` über die Reihe, keine Vollstichproben-Normierung, kein `groupby(...).last()`. Die SMA läuft rollierend über die eigenen Beobachtungen inkl. t (`strategies/...py:76`). Kausalitätstest bestanden (`causal_ok = True`), Test "Zukunftspreise ändern keine Vergangenheitsgewichte" grün.
* Signal-Ausführung: Signal am Schluss von t, Handel zur Eröffnung t+1 (`qlab/engine.py`: `exec_mode="open"`, `pending`-Logik). Test `test_engine_trades_next_open_after_first_signal` vorhanden und grün.
* Gewichte: je Zeile Summe ≤ 1,0 (Maximum 0,5 je Bein im Basislauf, 1,0 bei gold_only), kein Short, keine Gewichte auf NaN-Kurse (`skipped_orders = 0`).
* Varianten: sma168, sma252, gold_only, drei Stück, alle vorab in `sensitivity_variants` der Spec festgelegt, kein Hebel, Kosten 10 bp je Seite wie Spec.
* Trendregel: strikt größer (`s > sma`), SMA 210 inkl. t, Signal bei Gleichstand = AUS (Test `test_both_up_is_fully_invested_in_two_halves_and_flat_is_off`).
* Abbruchkriterium der Spec (geprüft): (a) Sharpe-Vorteil zu 50/50-B&H unter 0,05 in beiden Dekaden: NICHT erfüllt, 2006-2015 liegt bei +0,24. (b) Netto-Sharpe unter SPY UND MaxDD-Vorteil < 15 pp: NICHT erfüllt, MaxDD-Vorteil 26,9 pp (-28,3 % vs -55,2 %). Die Spec-Referenz "SPY ca. 0,57" wird im Lauf nicht reproduziert (SPY 0,46 vor Steuer, gleiches Fenster); am Urteil ändert das nichts, weil (b) an der MaxDD-Bedingung scheitert.

## Handrechnung (kurz: Eingabe, erwartet, Modul)
* Synthetisches Panel: 400 Börsentage ab 2010-01-04, `np.random.default_rng(12345)`, Kurse Drift 0,03 %/Tag, Volatilität 1 %, ab Tag 250 Drift -0,12 %/Tag. Unabhängige Neuimplementierung (Mittel der letzten 210 Kurse inkl. t, strikt größer). Erwartete Zeilen: 8 (2010-10-22, 2010-11-01, 2010-11-03, 2010-11-05, 2011-04-11, 2011-04-20, 2011-04-26, 2011-07-15). Modul liefert exakt dieselben Zeilen und Gewichte (`Übereinstimmung: True`).
  * 2010-11-01: erwartet DBC 0,5 / GLD 0,0; Modul 0,5 / 0,0.
  * 2011-04-20: erwartet DBC 0,5 / GLD 0,0; Modul 0,5 / 0,0.
  * 2011-04-26: erwartet 0,0 / 0,0; Modul 0,0 / 0,0.
* Engine-Timing: Signal t = 2010-11-01, erster Handel zur Eröffnung 2010-11-02 (Test grün).

## Lauf-Kennzahlen (aus `results/SUMMARY_audit_commodity_gold_trend_dbc_gld.md` und CSV, bis 2022-12-31, nicht Holdout)
Basislauf: erster Signaltag 2006-12-04, 16,1 Jahre, Kosten 10 bp je Seite (DBC/GLD).

| Lauf | CAGR | Vol | Sharpe | MaxDD | Umsatz/J (einseitig) | Kosten/J | Sharpe nach Steuer | CAGR nach Steuer |
|---|---|---|---|---|---|---|---|---|
| base (DBC+GLD, SMA 210) | 4,4 % | 11,0 % | 0,36 | -28,3 % | 3,9 | 0,79 % | 0,27 | 3,4 % |
| sma168 | 3,8 % | 11,1 % | 0,31 | -25,7 % | 4,6 | 0,92 % | 0,23 | 2,9 % |
| sma252 | 4,7 % | 11,1 % | 0,40 | -29,4 % | 3,3 | 0,67 % | 0,30 | 3,6 % |
| gold_only (GLD) | 4,5 % | 14,3 % | 0,30 | -37,6 % | 3,9 | 0,78 % | 0,21 | 3,2 % |
| SPY Buy&Hold (Vergleich, gleiches Fenster) | 8,6 % | — | 0,46 | -55,2 % | — | — | 0,40 | 7,3 % |
| 50/50 DBC/GLD Buy&Hold (eigene Rechnung, gleiches Start) | — | — | 0,27 | — | — | — | — | — |

* Umsatz: 3,9 einseitig, 7,8 beidseitig pro Jahr (249 Signalwechsel in 16 J). Entspricht der Spec-Angabe "ca. 7,5 Einheiten" bei beidseitiger Zählung.
* Mittlere Bruttoexposition Basislauf 58 %: der niedrigere MaxDD kommt aus dem Cash-Anteil, nicht aus besserem Timing allein.
* Plausibilität: keine Sharpe über 1,0, kein Warnsignal. Erwartung der Spec 0,25-0,45 nach Decay: Basislauf 0,36 liegt darin.
* Kausalität: bestanden. Übersprungene Orders: 0.

## Offene Punkte / nicht geprüft
* Holdout ab 2023 nicht geöffnet (kein `--final`). Spec-Dekade 2016-2026 nur bis 2022 geprüft.
* Stresstest Kosten 25 bp (Spec) nicht gelaufen (`--cost-mult 2.5` nicht ausgeführt).
* Steuer: Engine-Vereinfachung (Durchschnittskosten, keine Vorabpauschale) nicht im Detail gegengeprüft. Haltefrist-Vorteil bei physischem Gold-ETC nicht bewertet (Spec-Hinweis, keine Modulwirkung).
* Datenqualität DBC/GLD aus Cache (yfinance, auto_adjust) nicht gegen Primärquelle geprüft; kein Netzabruf.
* Die Anzahl Versuche im DSR (Befund 1) spiegelt nicht die Gesamtzahl der Projektläufe; eine Zahl dafür habe ich nicht erhoben.
* Ken-French/Gorton-Rouwenhorst-Mechanismus (Quellen in SPEC) nicht inhaltlich verifiziert.
