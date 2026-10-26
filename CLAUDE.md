# Quant-Lab — Arbeitsanweisung für Claude

Arbeitsname (umbenennbar). Gestartet 2026-10-05. Geplante Laufzeit: 1–2 Monate, Schritt für Schritt.
Sprache mit Nick: Deutsch, locker, kurz. Nick schreibt per Spracheingabe — Tippfehler großzügig lesen.

## Ziel
Ein Quant-Research-Projekt, das am Ende **im echten Markt läuft** und **gründlich getestet** ist.
Zwei akzeptierte Erfolgsfälle:
1. Eine Strategie mit belegtem Vorteil (Edge) nach Kosten und Steuern.
2. Mindestens ein System, das das Geld sicher hält (kleiner Drawdown, ungefähr Marktrendite oder besser nach Risiko).
Ein ehrliches „kein Edge gefunden, hier ist das sichere Portfolio" ist ein **gültiges Ergebnis**.
Nick will etwas Kreatives, kein weiteres Standard-Rezept — aber nur, wenn es den Prüfstand besteht.

## Harte Regeln (nicht verhandeln)
1. **Kein erzwungener Trade.** NO TRADE ist Standard (Lehre aus Apex/NEMI).
2. **Der Code rechnet, KI redet.** Jede Zahl, die Kapital berührt, kommt aus deterministischem, getestetem Python. LLMs nur für Recherche/Erklärung.
3. **Hypothese vor Test.** Jede Idee wird in `docs/HYPOTHESEN.md` mit Erwartung und Abbruchkriterium *vor* dem Backtest eingetragen. Keine nachträglichen Varianten auf denselben Daten auswählen UND bestätigen.
4. **Ehrlich messen:** Kosten (Spread, Gebühren, Slippage) zuerst, deutsche Abgeltungssteuer mitrechnen, Ausführung zum nächsten realen Kurs (Eröffnung), kein Blick in die Zukunft, Walk-forward auf frischen Daten, Mehrfachtest-Korrektur (Deflated Sharpe / PBO), Zufalls- und Buy&Hold-Konkurrenten als Pflichtvergleich.
5. **Nichts erreicht echtes Kapital ohne Freigabe-Tor** (siehe `docs/ROADMAP.md`, Phase 7). Nick entscheidet über echtes Geld, nie Claude. Keine Broker-Keys von Claude anfassen.
6. **Jeder Schritt wird fertig gemacht:** Code + Tests + kurzer Bericht in `docs/LOGBUCH.md`, bevor der nächste beginnt.
7. **Budget:** Endbetrieb max. ~10 €/Monat inkl. Hosting, lieber unter 5 €. Bevorzugt: GitHub Actions (kostenlos), Cron statt Dauerbetrieb, kostenlose Datenquellen, nur Gratis-KI (OpenRouter `:free`). Keine bezahlten APIs ohne Rückfrage.

## Was schon existiert (wiederverwenden statt neu bauen)
Pfade ab `C:\Users\spide\Desktop`.

| Baustein | Pfad | Nutzen |
|---|---|---|
| Walk-forward, Parameter-Sweep | `Nick\nemi\nemi\backtest\validation.py` | Prüfung auf frischen Daten |
| Monte-Carlo, Ruin-Risiko | `Nick\nemi\nemi\backtest\montecarlo.py` | Risiko-Streuung |
| Backtest-Engine, Kennzahlen | `Nick\nemi\nemi\backtest\engine.py`, `metrics.py` | Mit Drawdown-Bugfix + Tests |
| Daten (Yahoo, Speicher, Prüfung) | `Nick\nemi\nemi\data\` | 161 Symbole, Tagesdaten ab 2019 |
| Marktphasen, Sizing, Stops | `Nick\nemi\nemi\engine\regime.py`, `nemi\risk\` | Regime-Erkennung |
| Auswertung NEMI | `Nick\nemi\docs\RESULTS.md`, `AUDIT.md` | Was schon widerlegt ist |
| Zucht/Evolution, Alpaca-Broker, GitHub-Actions-Betrieb | `Projekte\Fly-of-Wallstreet\fly\`, `.github\workflows\daily.yml` | Gratis-Betrieb, Papierhandel |
| Event→Markt-Graph, Look-ahead-Schutz, NASA/Open-Meteo | GitHub `Nikros07/Eye-of-Horus` (**nicht lokal** — klonen) | Kreative Datenquelle |
| Polymarket-Marktdaten (Gamma-API), Kelly, Edge nach Gebühr | `Projekte\Polymarket-Bot\backend\services\polymarket_service.py`, `core\scoring.py` | Prediction-Market-Daten |
| ETF-Momentum v4, Kurs-Cache | `Nick\1. Projects\MT5-Master-Strategy\adaptive_momentum_v4.py`, `.cache_prices_v4.csv` | **Referenz-Baseline** |
| Lessons Learned | `Desktop\projects\README.md` (Abschnitt „Was ich gelernt habe") | Prinzipien |

## Bereits widerlegt — NICHT erneut vorschlagen
- NEMI-Setups (6 Stück, `trend_breakout_long` bestes): out-of-sample 0 von 3 Fenstern; Gewinn nur aus 2020.
- Quartals- statt Monats-Rebalancing (kostet Rendite). Abgeltungssteuer killt den DAX-Vorsprung nicht (kostet ~3,9 Pp.).
- Fly-of-Wallstreet: mehr Sinne, Mehrmarkt, Schädel-Bauweise, Vol-Overlay brachten nichts; Kolonie Sharpe 0,44 vs Kontrolle 0,41 vs SPY 0,48.
- MT5 EA v6 EURUSD H1: Profit Factor 0,88, vor Spread bei null. (v7 noch ungetestet.)
- ETF v4: schlägt DAX um 1,3 Pp. nach Steuer, verliert gegen S&P-500-Buy&Hold (10,02 % vs 10,56 %); Vorteil vor allem Drawdown (−19,3 % vs −24,6 %).

## Werkzeug-Hinweise (Windows)
- Python mit pandas/numpy/yfinance: `C:\Users\spide\AppData\Local\Programs\Python\Python311\python.exe`. Das `python` im PATH ist ein Hermes-Venv ohne pip. Besser eigenes `.venv` in diesem Projekt.
- `gh` ist nicht installiert, kein `GITHUB_TOKEN`: neue GitHub-Repos legt Nick selbst an. Git pusht normal.
- GitHub-MCP-Connector aktuell defekt (Auth-Header). Öffentliche Repos per `curl api.github.com` / raw.githubusercontent.com lesbar.
- Edit-Tool für Dateien nutzen, Heredocs mit `\n` in Python-Strings brechen Zeilen.
- Vor jedem Write den echten Pfad prüfen (Desktop wurde schon umsortiert; Write in fehlenden Pfad erzeugt Geisterordner).

## Stand
Siehe `docs/LOGBUCH.md` (chronologisch) und `docs/ROADMAP.md` (Phasen, Häkchen). Vor jeder Sitzung beide lesen.
Offene Entscheidungen für Nick: `docs/ROADMAP.md`, Abschnitt „Entscheidungen".
