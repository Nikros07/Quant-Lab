# Quant-Lab

Ehrlich geprüftes Quant-Forschungsprojekt (Start 2026-10-05). Ziel: ein System, das das Geld sicher hält oder einen belegten Vorteil nach Kosten und Steuern hat. Ein ehrliches „kein Vorteil gefunden“ ist ein gültiges Ergebnis. **Keine Anlageberatung. Handel nur im Demokonto, nichts hier ist für echtes Geld freigegeben.**

## Ergebnis in Kürze

Empfehlung (`base1x`): je Markt ein Monatsfilter, am letzten Handelstag des Monats „Schlusskurs ≥ Mittel der letzten 12 Monatsschlüsse → long, sonst Cash“, 17 Märkte gleichgewichtet, ohne Hebel, Ausführung am Folgetag, 10 bp je Seite, Cash zum US-Geldmarktzins, 1991–2022, Holdout ab 2023 geschlossen.

| 17-Märkte-Korb | Rendite p. a. | größter Verlust | Sharpe |
|---|---|---|---|
| Buy & Hold | 8,3 % | −47,1 % | 0,49 |
| Monatsfilter MA12 (`base1x`) | 7,3 % | −14,7 % | 0,63 |

Belegt ist der kleinere Verlust (gegenüber Buy & Hold robust: Placebo-, Bootstrap- und Marktauswahl-Test bestanden), bei rund 1 Prozentpunkt weniger Rendite. Ein Renditevorteil ist nicht belegt. **Der historische größte Verlust von −14,7 % ist optimistisch:** Bootstrap-Median −20,9 % (5-%-Fall −31,6 %), je nach Entscheidungstag −16 % bis −24 % im Crash 2020. Erwartet werden −20 bis −30 %. Als CFD mit Finanzierung des vollen Nominalwerts bleibt kaum Rendite über dem Geldmarkt (3,2 % p. a.); Futures oder ETFs sind kostenseitig deutlich besser. Hebel bis 1,5x, Volatilitäts-Skalierung, Trailing-Stops (auch Stufen-Stop, Risk-Reward), Signal-Mischungen sowie Struktur-Stops an Swing-Lows (Support/Liquiditätszonen), Fair-Value-Gap-Stops und 4 Tranchen haben die vorab festgelegten Tests nicht bestanden (H11–H13, H19–H21) und stehen nur als abschaltbare Optionen im Code. Ein einzelner Markt hält 20 % Verlust nicht (S&P 500 allein: −52 % in 1928–2022, MT5-Test US500 2012–2026: 27 % Equity-Drawdown).

**Hinweis zu MT5-Stop-Tests:** Der Strategietester im Modell „Nur Eröffnungspreise“ überschätzt Stops (ein FVG-Trail sah dort wie ein Durchbruch aus, im Modell „1-Minuten-OHLC“ ist er schlechter als die Basis). Stop-Ergebnisse nur aus Modell 1 oder Echtticks verwenden; Details in [`docs/STRATEGIE-TRENDFILTER.md`](docs/STRATEGIE-TRENDFILTER.md).

## Arbeitsweise

- **Hypothese vor dem Test:** Jede Idee steht mit Kriterium und Abbruchlogik in [`docs/HYPOTHESEN.md`](docs/HYPOTHESEN.md), bevor gerechnet wird; Ergebnisse werden unverändert berichtet.
- **Der Code rechnet, die KI redet:** Alle Zahlen kommen aus getestetem Python (Kosten, deutsche Steuer, Ausführung am nächsten Kurs, PSR/DSR/PBO, Holdout-Schutz).
- **Nichts erreicht echtes Kapital** ohne ausdrückliche Freigabe (siehe [`docs/ROADMAP.md`](docs/ROADMAP.md)).

## Aufbau

| Ordner | Inhalt |
|---|---|
| `qlab/` | Prüfstand: Daten, Engine, Kennzahlen, Kalender, Kontrollen |
| `strategies/`, `scripts/` | Strategiemodule, Audits, Härtetests H5–H13 |
| `tests/` | über 1 000 Tests |
| `docs/` | Hypothesenregister, Logbuch ([`LOGBUCH.md`](docs/LOGBUCH.md)), Strategiebericht ([`STRATEGIE-TRENDFILTER.md`](docs/STRATEGIE-TRENDFILTER.md)), Audits |
| `research/` | Literatur- und Repo-Recherche (Rohdaten) |
| `results/` | Ergebnisdateien der Läufe |
| `deploy/tradingview/` | Pine Script v6: Strategie (v1.2, v2), Plus, Alarm, 17-Märkte-Dashboard |
| `deploy/mt5/` | MQL5-Expert-Advisor (v1.10, v2, v3 mit Zonen-Zeichnung und schaltbaren Struktur-/FVG-Stops) und Tester-Konfigurationen, nur Demokonto |
| `deploy/alpaca-bot/` | geparkter Papierhandels-Bot (nicht in Betrieb) |

## Starten

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
.venv/Scripts/python -m pytest tests -q
.venv/Scripts/python scripts/check_h12_robust_basket.py
```

Marktdaten kommen aus öffentlichen Quellen (Yahoo, Ken French, Shiller) und werden lokal in `data_cache/` zwischengespeichert, der nicht im Repo liegt.

## Stand und Grenzen

- Preisindizes ohne Dividenden, Überlebensverzerrung der Marktauswahl nicht ausgeschlossen, viele Tests auf denselben Daten (Mehrfachtest-Hinweis in den Hypothesen).
- Die Pine-Dateien sind nicht in TradingView kompiliert; der MT5-EA lief nur im Strategietester und im Demokonto.
- Der Prüfblock H14–H18 sowie H19–H21 (Struktur-Stops, FVG, Tranchen) sind gelaufen (Ergebnisse in `docs/HYPOTHESEN.md`). Offen: Verifikation von Pine/EA durch unabhängige Prüfer, Literaturrecherche zu weiteren Verfahren, Test auf neuen Daten (Holdout ab 2023).
