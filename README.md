# Quant-Lab

Ehrlich geprüftes Quant-Forschungsprojekt (Start 2026-10-05). Ziel: ein System, das das Geld sicher hält oder einen belegten Vorteil nach Kosten und Steuern hat. Ein ehrliches „kein Vorteil gefunden“ ist ein gültiges Ergebnis. **Keine Anlageberatung. Handel nur im Demokonto, nichts hier ist für echtes Geld freigegeben.**

## Ergebnis in Kürze

Empfehlung (`base1x`): je Markt ein Monatsfilter, am letzten Handelstag des Monats „Schlusskurs ≥ Mittel der letzten 12 Monatsschlüsse → long, sonst Cash“, 17 Märkte gleichgewichtet, ohne Hebel, Ausführung am Folgetag, 10 bp je Seite, Cash zum US-Geldmarktzins, 1991–2022, Holdout ab 2023 geschlossen.

| 17-Märkte-Korb | Rendite p. a. | größter Verlust | Sharpe |
|---|---|---|---|
| Buy & Hold | 8,3 % | −47,1 % | 0,49 |
| Monatsfilter MA12 (`base1x`) | 7,3 % | −14,7 % | 0,63 |

Belegt ist nur der kleinere Verlust (etwa ein Drittel), bei rund 1 Prozentpunkt weniger Rendite. Ein Renditevorteil ist nicht belegt. Hebel bis 1,5x, Volatilitäts-Skalierung, Trailing-Stops (auch Stufen-Stop, Risk-Reward) und Signal-Mischungen haben die vorab festgelegten Tests nicht bestanden (H11–H13) und stehen nur als abschaltbare Optionen im Code. Ein einzelner Markt hält 20 % Verlust nicht (S&P 500 allein: −52 % in 1928–2022, MT5-Test US500 2012–2026: 27 % Equity-Drawdown).

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
| `deploy/mt5/` | MQL5-Expert-Advisor (v1.10, v2) und Tester-Konfigurationen, nur Demokonto |
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
- Der Prüfblock H14–H18 (Placebo, Bootstrap, Timing-Luck, Marktauswahl, Kosten) ist registriert, aber noch nicht gelaufen.
