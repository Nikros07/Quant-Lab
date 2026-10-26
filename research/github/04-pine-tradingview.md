# GitHub-Recherche: Pine-Script-Strategien (TradingView, v5/v6)

Stand: 2026-10-21. Rein lesend (GitHub-API, raw.githubusercontent, WebSearch). Kein Code ausgefuehrt, nichts geklont.

## Vorab: Limits und Abdeckung

- GitHub-Suchendpunkt lieferte beim zweiten Versuch HTTP 403 (Suchlimit ohne Token). Danach WebSearch genutzt.
- Core-API (Repo-Metadaten) funktionierte.
- Gelesen: 4 Repos (README bzw. Strategie-Datei). Nur Suchtreffer gesehen: 3 weitere.
- Keine Repos gefunden, die Dual Momentum, Faber-Timing oder Vol-Targeting in Pine sauber umsetzen. Das ist ein Befund, kein Fehler der Suche.

## Repos

### 1. jayadevrana/free-pine-script-indicators

| Feld | Wert |
|---|---|
| URL | https://github.com/jayadevrana/free-pine-script-indicators |
| Sterne | 1 |
| Lizenz | MPL-2.0 (laut API) |
| Letzter Push | 2026-10-12 (Repo erst am 2026-09-19 angelegt) |

Regel (EMA Trend Strategy, `scripts/ema-trend-strategy.pine.txt`): Long, wenn EMA(9) die EMA(21) von unten kreuzt und Close > EMA(200). Short spiegelbildlich. Exit ueber ATR(14): Stop 2 ATR, Take-Profit 3 ATR, vom Einstandspreis aus.

Messqualitaet:
- Kosten: 0,05 % Kommission und 2 Ticks Slippage im Code gesetzt. Gut.
- Look-ahead: Signale auf Schlusskursen, Ausfuehrung ueber Pine-Standard (Market-Order aus Bar-Schluss wird zum naechsten Open gefuellt). Kein offensichtlicher Look-ahead im Code.
- Sizing: `default_qty_type = strategy.percent_of_equity`, 10 % des aktuellen Eigenkapitals. Das ist Zinseszins-Sizing und genau die Ursache fuer aufgeblasene Ergebnisse, wenn das Kapital mit Gewinnen wachsen darf.
- Out-of-sample: keine. Die README behauptet "honest backtests", zeigt aber in dem, was ich gelesen habe, keine Kennzahlen.
- Bewertung: sauberer Code, schwache Messung. Nur als Vorlage fuer Einstellungen nutzen, nicht fuer Ergebnisse.

Uebertragbare Idee: siehe Liste unten (Sizing und Kostenparameter).

### 2. casoon/pine-scripts

| Feld | Wert |
|---|---|
| URL | https://github.com/casoon/pine-scripts |
| Sterne | 9 |
| Lizenz | MIT (freie Scripte), Premium separat |
| Letzter Push | 2026-10-14 |

Regel: README listet 7 Strategien (u. a. Chandelier Flip Radar, WaveTrend v4, Smooth Trend Radar), jeweils mit Exit-Typ (Trailing, Fixed TP, Pivot ATR) und Status ("Promising" / "Not ready"). Die Regeln selbst stehen in Assessment-Dateien, die ich nicht gelesen habe.

Messqualitaet: unbekannt. Die README nennt keine Sizing-, Kosten- oder Ausfuehrungsparameter. Keine Trendfilter-Strategie auf Monatsbasis erkennbar. Eignet sich nicht fuer unseren Monatsfilter.

### 3. 11Muhil/FibTrend-Pro-Strategy_Pinescript

| Feld | Wert |
|---|---|
| URL | https://github.com/11Muhil/FibTrend-Pro-Strategy_Pinescript |
| Sterne | 3 |
| Lizenz | nicht geprueft (Feld im API-Ausschnitt abgeschnitten) |
| Letzter Push | 2025-02-11 |

Regel (laut Beschreibung, nicht Code gelesen): Long bei Kurs ueber Fib 0,618, Volumenspitze und Kurs ueber 200-SMA. Exit unter Fib 0,5 oder Take-Profit 1 % bzw. ATR-basiert.

Messqualitaet: nicht geprueft. Repo ist klein (8 KB), keine Out-of-sample-Doku erkennbar. Kein Kandidat fuer uns.

### 4. LouisLetcher/quant-pine

| Feld | Wert |
|---|---|
| URL | https://github.com/LouisLetcher/quant-pine |
| Sterne | 23 |
| Lizenz | API: "Other" (NOASSERTION). README: freie Scripte MIT, Premium proprietaer |
| Letzter Push | 2026-07-25 |

Regel: README beschreibt nur die Struktur und das Premium-Modell. Keine Strategieregeln gelesen.

Messqualitaet: unbekannt. Wegen der gemischten Lizenz nur als Ideenquelle markieren, keinen Code uebernehmen.

### Nur Suchtreffer, nicht gelesen

- hasnocool/tradingview-pine-scripts (Simulation und Visualisierung von Strategien, Lizenz unbekannt)
- handiko/RSI-2-Stock-Trading-Strategy-Pinescript (EMA-200-Trendfilter plus RSI-2, Lizenz unbekannt; Regel laut Suchbeschreibung, nicht geprueft)

## Antworten auf die Leitfragen

- Positionsgroesse: Die Repos nutzen ueberwiegend `strategy.percent_of_equity` (Zinseszins). Feste Ordergroesse ist per `default_qty_type = strategy.fixed` oder ueber `qty` moeglich. Ich habe kein Repo gefunden, das feste Groesse ausdruecklich begruendet.
- Cash-Verzinsung: In keinem gelesenen Repo modelliert. Pine-Strategien verzinsen Cash nicht. Das muss extern gerechnet werden.
- Ausfuehrung am naechsten Open: Pine-Standard fuer Market-Orders aus Bar-Schluss. Parameter `process_orders_on_close` ist per Default aus. Die Repos setzen das nicht explizit. Nicht gegen die offizielle Pine-Doku verifiziert.
- Mehrmarkt-Auswertung: In den gelesenen Repos nicht vorhanden (Einzelinstrument-Strategien).
- Alarme: JSON-Alert-Messages (`alert_message`) im EMA-Repo. Ausreichend fuer Webhooks, aber ohne Monatslogik.
- Vol-Targeting, Dual Momentum, Faber in Pine: nicht gefunden.

## Testbare Ideen

1. Feste Ordergroesse statt Zinseszins: Position = 100 % des Startkapitals (`default_qty_type = strategy.fixed`, `qty = initial_capital / close`), Vergleich gegen `percent_of_equity` = 100 % mit identischem Monatsfilter. Erwartung: gleicher Signalverlauf, aber Ergebnis nicht durch Gewinn-Reinvestition aufgeblaehen.
2. Monatsfilter mit Pine-Ausfuehrung: Signal am letzten Handelstag des Monats auf Schlusskurs (Monatsschluss >= Mittel der letzten 12 Monatsschluesse), Ausfuehrung am naechsten Open, Kosten 0,05 % plus 2 Ticks Slippage (Parameter aus dem EMA-Repo).
3. Cash-Verzinsung extern: Cash-Tage mit Tagesgeldsatz verzinsen, Ergebnis vor und nach Verzinsung ausweisen. Diese Idee ist in den gelesenen Repos nicht vorhanden und daher neu.

Neu gegenueber unseren Tests? Idee 1 und 2 betreffen die Umsetzung in Pine und nicht die Signalregel. Ob das Ergebnis aendert, ist nicht getestet. Idee 3 ist neu. Dual Momentum, PAA, Faber, Vol-Targeting bleiben unbelegt.

## Quellen

- https://github.com/jayadevrana/free-pine-script-indicators (README und scripts/ema-trend-strategy.pine.txt, scripts/first-strategy.pine.txt)
- https://github.com/casoon/pine-scripts (README)
- https://github.com/LouisLetcher/quant-pine (README)
- https://github.com/11Muhil/FibTrend-Pro-Strategy_Pinescript (API-Metadaten, Beschreibung)
- GitHub-API: /search/repositories (einmal erfolgreich, dann 403), /repos/{owner}/{repo}
