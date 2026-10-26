# Strategie: Monatlicher Trendfilter „Index oder Cash" (MA12)

Stand 2026-10-13. Geprüft im Quant-Lab-Prüfstand, unabhängig auditiert (Look-ahead, Quellentreue, Handrechnung: bestanden).
Code: `deploy/mt5/TrendFilter_MA12.mq5` (MetaTrader 5) und `deploy/tradingview/TrendFilter_MA12.pine` (TradingView).

## Die Regel (komplett)

Am **letzten Handelstag jedes Monats**:

1. `P` = Schlusskurs des S&P-500-Preisindex an diesem Tag.
2. `MA` = Durchschnitt der letzten 12 Monatsschlusskurse (inklusive `P`).
3. `P ≥ MA` → **long** (100 % investiert, kein Hebel). `P < MA` → **Cash**.
4. Gehandelt wird zur Eröffnung des nächsten Handelstags. Dazwischen passiert nichts.

Quellen: Faber 2007 (SSRN 962461), Neely/Rapach/Tu/Zhou 2014. Keine optimierten Parameter, nur die 12 aus der Literatur.

## Ergebnisse (alle nach Handelskosten 10 bp je Wechsel)

| Zeitraum | | CAGR | Sharpe | Max. Verlust | Vergleich: Markt |
|---|---|---|---|---|---|
| 1993–2022 (SPY, Auswahlzeitraum) | Strategie | 9,4 % | 0,60 | **−22,5 %** | 9,6 % · 0,47 · −54,6 % |
| 1930–2022 (US-Gesamtmarkt, Langzeittest) | Strategie | 9,6 % | 0,58 | **−37,4 %** | 9,6 % · 0,44 · −80,3 % |
| **2023 bis heute (Holdout, einmal geöffnet)** | Strategie | 15,5 % | 0,88 | −10,0 % | SPY 22,0 % |

Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss): CAGR 8,0 % (1993–2022) gegenüber 8,9 % für Buy&Hold. Die Steuer kostet ca. 1,4 Prozentpunkte pro Jahr, weil jeder Wechsel Gewinne realisiert.

Handelsaktivität: 38 Signalwechsel seit 1993 (≈ 1,1 pro Jahr), 78 % der Zeit investiert.

Krisenjahre (Strategie vs. Markt): 2001 +3,7 % vs −11,8 % · 2002 +2,6 % vs −21,6 % · 2008 +2,0 % vs −36,8 % · 2022 −15,9 % vs −18,2 %.

## Ehrliche Einordnung

**Was belegt ist:** Der Filter halbiert den größten Verlust (−22 % statt −55 % seit 1993, −37 % statt −80 % seit 1930) bei fast gleicher Rendite wie Buy&Hold. Das Muster hält über 93 Jahre, in vier Varianten und im später geöffneten Holdout.

**Was NICHT belegt ist:** Ein Renditevorteil. Der Sharpe-Vorsprung (+0,14 bis +0,13) ist statistisch grenzwertig (90 %-Intervall 0,00…0,29; Deflated Sharpe 0,83–0,92, Schwelle wäre 0,95). In nur 36–43 % der rollierenden 5-Jahres-Fenster schlägt die Strategie den Markt bei der Rendite. Nach Steuer liegt sie 0,9 Prozentpunkte unter Buy&Hold.

**Der Preis:**
- In starken Bullenmärkten hinkt sie hinterher (2023: +6,4 % vs. +26,2 %), weil Fehlsignale kosten (2010, 2015/16, 2018/19, 2023, April 2025).
- Das Holdout (3,7 Jahre, überwiegend Bullenmarkt) ist **kein** Stresstest; es bestätigt nur, dass nichts kaputtgegangen ist.
- Dies ist der Gewinner nach Robustheit, nicht nach Rendite. Höheren Sharpe hatten die VIX-gesteuerte Sektor-Umkehr (0,72) und Keller PAA (0,66), aber nur als Best-of-3-Variante mit 18–37 Umschlägen pro Jahr bzw. nur 14,6 Jahren Daten. Beide sind für MT5/TradingView weder einfach noch robust genug.

## Einsatz: wo es funktioniert und wo nicht

| Weg | Urteil |
|---|---|
| **TradingView-Alarm + ETF beim normalen Broker** (UCITS-S&P-500-ETF, thesaurierend) | **Empfohlen.** Gleicht dem Backtest am meisten. Ein Alarm pro Monat, von Hand ausführen. In der Cash-Phase Tagesgeld/Geldmarkt-ETF. |
| **MetaTrader 5 mit Index-CFD (z. B. US500)** | Funktioniert technisch, aber **prüfe vorher den Long-Swap** deines Brokers. Index-CFDs kosten typisch Leitzins plus 2–3 % pro Jahr nur für das Halten. Bei 4–5 % Zinsen sind das ~7 % p. a. und würden den Vorteil komplett auffressen. Außerdem verzinst MT5 Cash nicht. Nur sinnvoll bei niedrigem Swap oder mit einem Aktien-/ETF-CFD ohne hohen Finanzierungsaufschlag. |

## So testest du es

**TradingView:** Pine-Editor öffnen, `TrendFilter_MA12.pine` einfügen, „Zum Chart hinzufügen" auf dem **Tageschart** von `SP:SPX` oder SPY. Nicht im Pine-Editor kompiliert worden: Falls eine Fehlermeldung kommt, schick sie mir. Alarm: Alarm erstellen → Bedingung = die Strategie → „Alert()-Funktionsaufrufe nur".

**MetaTrader 5:** `TrendFilter_MA12.mq5` nach `MQL5\Experts\` kopieren (kompiliert ohne Fehler und Warnung). Im Demokonto auf den D1-Chart von `US500` (Symbolname bei deinem Broker prüfen), `InpTradingOn = true`. Strategy Tester: Symbol US500, Zeitrahmen D1, „Nur Eröffnungspreise". Zuerst `InpTradingOn = false` laufen lassen und das Journal gegen die Referenz unten prüfen. Im Tester nicht verifiziert, nur kompiliert.

**Referenz zum Gegenprüfen (S&P-500-Preisindex, Python-Prüfstand):**

| Monatsende | Schluss | MA12 | Signal |
|---|---|---|---|
| 2026-03-31 | 6528,52 | 6504,59 | LONG |
| 2026-04-30 | 7209,01 | 6641,25 | LONG |
| 2026-05-29 | 7580,06 | 6780,28 | LONG |
| 2026-06-30 | 7499,36 | 6888,15 | LONG |
| 2026-07-31 | 7489,72 | 6984,01 | LONG |
| 2026-08-31 | 7686,14 | 7086,16 | LONG |
| 2026-09-30 | 7651,54 | 7166,42 | LONG |

Aktuell **LONG**. Nächste Entscheidung: Schluss vom **30.10.2026**, Ausführung am 02.11. MT5 und TradingView dürfen durch abweichende Brokerkurse in Einzelfällen abweichen; maßgeblich ist, dass der Wechseltag und die Richtung übereinstimmen.

Wechsel seit 2018: Okt 2018 flat → Nov long → Dez flat → Feb 2019 long → Mai flat → Jun long → Feb 2020 flat → Mai long → Feb 2022 flat → Mär long → Apr flat → Jan 2023 long → Feb flat → Mär long → Okt 2023 flat → Nov long → Mär 2025 flat → Mai long.

## Vor echtem Geld (Roadmap Phase 6/7)

- [ ] Demo oder Papierhandel mindestens 6 Monatsentscheidungen, Abweichung zum Python-Signal erklären
- [ ] Broker-Kosten prüfen: Swap/Finanzierung (CFD) oder TER und Spread (ETF); Verzinsung der Cash-Phase
- [ ] Steuerfall klären (UCITS-Thesaurierer vs. CFD; Verlustverrechnung bei Termingeschäften beschränkt)
- [ ] Kleiner Einsatz, feste Verlustgrenze, Entscheidung von Nick

Dieser Bericht ist keine Anlageberatung. Vergangene Ergebnisse sagen nichts Sicheres über die Zukunft; die Strategie kann über Jahre hinter dem Markt zurückbleiben.

---

## Verifikation (Stand 2026-10-20)

**TradingView, S&P 500 (`SP500`, Tageschart, Testzeitraum 03/2018 bis 10/2026):** Alle **15 von 15** Ein- und Ausstiege stimmen mit dem Python-Prüfstand überein (gleicher Handelstag, gleiche Richtung). Die TradingView-Historie beginnt 03/2018, deshalb ist das erste Signal Februar 2019. Abgleich per `scripts/compare_results.py compare-tv`, 100 %.

| Kennzahl (TradingView, Preisindex ohne Dividenden, Cash ohne Zins) | Wert |
|---|---|
| Gewinn gesamt | +9.764 USD = +97,6 % aus 10.000 USD |
| Max. Drawdown | 1.741 USD = 12,7 % |
| Abgeschlossene Trades | 7 (3 Gewinner, 4 Verlierer), 1 offener seit 02.06.2025 |
| Ø Gewinn / Ø Verlust | +22,9 % / −4,0 % |
| Profitfaktor | 3,6 |

Einordnung: Der Index stieg im selben Zeitraum von ca. 2.785 (01.03.2019) auf ca. 7.730, also etwa +177 % (Preisindex). Die Strategie liegt mit +98 % deutlich dahinter, hatte dafür nie mehr als 12,7 % Verlust (der Index im Februar/März 2020 etwa −34 %). Das ist die erwartete Abwägung: weniger Risiko, weniger Rendite in einer langen Aufwärtsphase mit V-förmigen Einbrüchen (2020, April 2025). Es ist kein Renditevorteil.

**TradingView, Gold (`XAUUSD`, 1997 bis 2026):** 17 von 19 Einstiegen und 16 von 19 Ausstiegen stimmen mit einer Futures-Referenz (`GC=F`) überein. Die Abweichungen liegen in Grenzmonaten (Spot gegen Futures) oder in einem auf den Screenshots nicht sichtbaren Trade. Gold ist NICHT geprüft: Die Strategie ist nur für den S&P 500 belegt.

## Werkzeug zum Abgleich eigener Ergebnisse

```bash
# Referenz für S&P 500 erzeugen (hier ab 2012)
.venv\Scripts\python.exe scripts\compare_results.py reference --source yahoo --symbol "^GSPC" --from 2012-01-01 --out results\abgleich\ref.csv
# TradingView: "Liste der Trades" als CSV exportieren, dann vergleichen
.venv\Scripts\python.exe scripts\compare_results.py compare-tv --trades Pfad\zum\export.csv --reference results\abgleich\ref.csv
# MetaTrader 5: das vom EA geschriebene Log vergleichen
.venv\Scripts\python.exe scripts\compare_results.py compare-mt5 --log "C:\Users\spide\AppData\Roaming\MetaQuotes\Terminal\Common\Files\TrendFilter_MA12_log.csv" --reference results\abgleich\ref.csv
```

## MetaTrader 5: Strategietester (EA v1.10)

Der EA ist kompiliert (0 Fehler, 0 Warnungen) und in deinen MT5-Datenordner kopiert (`MQL5\Experts\QuantLab\TrendFilter_MA12`). **Im Strategietester ist er noch nicht gelaufen**: Dein Demo-Konto `5046576318` auf MetaQuotes-Demo ist abgelaufen (Log: *authorization failed – Invalid account*), ohne Serververbindung kann der Tester keine Kurshistorie laden.

Vorbereitung: In MT5 *Datei → Konto eröffnen → MetaQuotes-Demo* (oder das Demokonto deines Brokers mit Indexsymbol, z. B. `US500`). Dann:

1. `Strg+R` (Strategietester), Expert `QuantLab\TrendFilter_MA12`, Symbol dein Index-CFD, Zeitrahmen `D1`, Modell *Nur Eröffnungspreise*, Zeitraum ab 2012, Einlage 10.000.
2. Vorher die Datei `...\Terminal\Common\Files\TrendFilter_MA12_log.csv` löschen (das Log wird angehängt).
3. Nach dem Lauf das Log mit `compare-mt5` gegen die Referenz prüfen. Kleine Abweichungen sind bei Grenzmonaten normal, weil CFD-Kurse leicht vom Preisindex abweichen.
4. Preset `deploy\mt5\TrendFilter_MA12.set` und Kommandozeilen-Vorlage `deploy\mt5\tester_example.ini` liegen bereit. Beides stammt von einem Hilfsagenten und ist aus dem Gedächtnis geschrieben, nicht verifiziert. Wird das Preset abgelehnt, im Tester „Einstellungen speichern" neu erzeugen.
5. Im Tester zählt die Rechnung ohne Cash-Zins und ohne CFD-Swap. Den Long-Swap des Symbols gibt der EA beim Start ins Journal aus.

## TradingView: Dateien

- `deploy\tradingview\TrendFilter_MA12.pine` (Strategie, Version 1.1): zusätzlich Referenztabelle der letzten 6 Monatsenden und eine Cash-Zins-Kurve im Datenfenster. Entscheidungs- und Mengenlogik sind unverändert.
- `deploy\tradingview\TrendFilter_MA12_Alerts.pine` (Indikator für Alarme: Wechsel auf LONG / FLAT und Monatsmeldung). Noch nicht in TradingView kompiliert.


## Mehr Trades? Schnellere Takte gemessen (2026-10-20)

Für TradingView gibt es `deploy\tradingview\TrendFilter_MA12_Plus.pine` mit wählbarem Takt (monatlich, wöchentlich, täglich SMA200, SMA50/200-Kreuzung, optional Puffer). Die schnelleren Takte wurden vorab als Hypothesen H1–H4 registriert und im Python-Prüfstand gemessen (S&P 500, 1994–2022, 10 bp Kosten, deutsche Steuer, Holdout ungeöffnet):

| Takt | Einstiege/Jahr | CAGR (nach Steuer) | Sharpe nach Steuer | Max. Verlust |
|---|---|---|---|---|
| **Monatlich MA12 (Basis)** | 0,55 | 9,4 % (8,0 %) | **0,48** | −22,5 % |
| H1 wöchentlich SMA40 | 1,9 | 7,0 % (6,0 %) | 0,36 | −29,6 % |
| H2 täglich SMA200 | 3,6 | 7,4 % (6,3 %) | 0,38 | −23,0 % |
| H3 täglich SMA50/200 | 0,48 | 9,7 % (8,2 %) | 0,48 | −33,7 % |
| H4 täglich SMA200 + 1 % Puffer | 1,5 | 8,0 % (6,8 %) | 0,42 | −25,2 % |
| SPY Buy&Hold | – | 9,5 % (8,8 %) | 0,42 | −55,2 % |

**Ergebnis: widerlegt.** Keine schnellere Variante schlägt die Basis (Δ Sharpe −0,12 bis 0,00, nicht signifikant). Mehr Trades bedeuten mehr Kosten und Steuer, aber keinen Vorteil; die tägliche 200-Tage-Linie kostet etwa 2 Prozentpunkte Rendite pro Jahr. Die Plus-Version eignet sich zum Auswerten und Vergleichen, nicht für echtes Geld. Die monatliche Variante bleibt die geprüfte.

**Mehr Daten ohne schlechtere Strategie:** längere Historie statt schnellerer Signale. Auf `SP:SPX` (Tageschart, TradingView mit Historie ab 1928) liefert dieselbe Monatsregel in 98 Jahren 60 Einstiege (0,61 pro Jahr) statt 9 seit 2018. Alternativ dieselbe Regel auf weiteren Märkten laufen lassen (jeder Markt ist ein eigener Test).

## Mehr Märkte gemessen (H5, 2026-10-21)

Dieselbe Regel, unverändert, auf 18 vorab festgelegten Märkten (Preisreihen bis 2022-12-31, 10 bp Kosten, Ausführung zum Folgeschluss, ohne Steuer, Cash = US-Zins; Rohdaten `results/H5_multi_market.csv`, Skript `scripts/check_trend_multi_market.py`, 7 Tests):

| Markt | ab | Jahre | Einstiege | CAGR Regel / Buy&Hold | Sharpe Regel / B&H | MaxDD Regel / B&H |
|---|---|---|---|---|---|---|
| ^GSPC | 1928-11 | 94.1 | 56 | 6.9 % / 5.5 % | 0.34 / 0.22 | -52 % / -86 % |
| ^IXIC | 1972-01 | 50.9 | 35 | 10.8 % / 9.2 % | 0.49 / 0.33 | -37 % / -78 % |
| ^DJI | 1992-12 | 30.0 | 27 | 5.9 % / 8.0 % | 0.36 / 0.40 | -31 % / -54 % |
| ^N225 | 1965-12 | 57.0 | 46 | 6.5 % / 5.2 % | 0.22 / 0.14 | -36 % / -82 % |
| ^FTSE | 1984-12 | 38.0 | 31 | 3.9 % / 4.9 % | 0.13 / 0.19 | -33 % / -53 % |
| ^GDAXI | 1990-12 | 32.0 | 25 | 5.9 % / 7.4 % | 0.30 / 0.33 | -43 % / -73 % |
| ^FCHI | 1991-02 | 31.8 | 25 | 4.9 % / 4.2 % | 0.25 / 0.19 | -31 % / -65 % |
| ^HSI | 1987-11 | 35.1 | 32 | 5.3 % / 6.5 % | 0.23 / 0.27 | -49 % / -65 % |
| ^AXJO | 1993-10 | 29.2 | 24 | 2.8 % / 4.3 % | 0.11 / 0.21 | -25 % / -54 % |
| ^GSPTSE | 1980-05 | 42.6 | 26 | 7.1 % / 5.5 % | 0.35 / 0.18 | -31 % / -50 % |
| ^KS11 | 1997-11 | 25.1 | 22 | 7.8 % / 6.8 % | 0.43 / 0.32 | -40 % / -56 % |
| ^STOXX50E | 2008-02 | 14.8 | 14 | -0.9 % / 0.0 % | -0.05 / 0.09 | -27 % / -53 % |
| EEM | 2004-03 | 18.8 | 17 | 5.5 % / 5.7 % | 0.32 / 0.29 | -39 % / -66 % |
| EFA | 2002-07 | 20.4 | 16 | 5.2 % / 5.9 % | 0.37 / 0.32 | -28 % / -61 % |
| TLT | 2003-06 | 19.5 | 19 | 2.2 % / 3.7 % | 0.14 / 0.25 | -28 % / -44 % |
| GC=F | 2001-07 | 21.4 | 17 | 7.3 % / 9.4 % | 0.47 / 0.53 | -39 % / -44 % |
| CL=F | 2001-07 | 21.4 | 21 | 5.1 % / -100.0 % | 0.27 / -0.00 | -60 % / -100 % |
| BTC-USD | 2015-08 | 7.3 | 4 | 73.6 % / 79.3 % | 1.16 / 1.15 | -85 % / -83 % |

**Ergebnis (Hypothese H5, vorab registriert): bestanden, aber nur beim Drawdown.**
- Max. Verlust kleiner als Buy&Hold auf 17 von 18 Märkten (Median −36 % gegen −61 %). Einzige Ausnahme: BTC-USD (nur 7 Jahre).
- Sharpe mindestens so hoch wie Buy&Hold auf 10 von 18 Märkten (Zufallsniveau, Vorzeichentest p = 0,41). Median Δ Sharpe +0,02; Median Δ Rendite −0,9 Prozentpunkte pro Jahr.
- Insgesamt 457 Einstiege über alle Märkte; auf dem S&P 500 ab 1928 allein 56.
- Lesart: Der Filter schützt vor tiefen Einbrüchen auf fast jedem Markt, kostet dafür etwa ein Prozent Rendite im Jahr und bringt keinen Sharpe-Vorteil. Das passt zum S&P-500-Befund und zur Literatur.
- Vorbehalte: Cash-Zins ist der US-Satz auch für Japan, Europa und Hongkong (begünstigt die Regel); EEM/EFA/TLT sind dividendenbereinigt, die Indizes nicht; die Märkte sind korreliert, 18 Märkte sind keine 18 unabhängigen Tests; CL=F-Buy&Hold ist durch einen negativen Yahoo-Kurs (−37,63 am 2020-04-20) unbrauchbar (ohne CL=F: 16/17 und 9/17); Yahoo-Altdaten vor 1990 unvalidiert.

## TradingView: viel mehr Handelsdaten über den Monats-Chart (nicht getestet)

Die Regel entscheidet nur an Monatsenden und handelt zur Eröffnung des Folgemonats. Auf einem **Monats-Chart** (Zeitrahmen `1M`) ist das genau ein Signal pro Balken: Schluss des Monatsbalkens entscheidet, Auftrag füllt zur Eröffnung des nächsten Monatsbalkens, also zum ersten Handelstag, wie in der Python-Referenz. Auf `SP:SPX` hat der Monats-Chart ca. 1.170 Balken ab 1928 und liegt damit weit unter dem Balkenlimit, das den Tages-Chart auf ab 2018 begrenzt. Erwartet wird die Referenz `results/abgleich/ref_spx_lang.csv` (119 Wechsel seit 1928, also ca. 60 Einstiege). Das ist aus dem Pine-Code abgeleitet, aber in TradingView noch nicht ausprobiert: bitte `TrendFilter_MA12.pine` auf `SP:SPX` im Zeitrahmen `1M` laden und die Trade-Liste exportieren; Abgleich mit `scripts/compare_results.py compare-tv`. Das Plus-Skript mit Tages- oder Wochentakt ist für den Monats-Chart nicht gedacht (nur die Einstellung "Monatlich").

## Korb aus 17 Märkten (H6, 2026-10-21): die sicherste Variante, aber ohne belegten Sharpe-Vorteil

Gleichgewichteter Korb aus den Monats-MA12-Sleeves von 17 Märkten (die 18 aus H5 ohne CL=F), täglich auf Gleichgewicht, nur Tage mit mindestens 8 offenen Märkten; 1991-02 bis 2022-12, 10 bp Kosten, ohne Steuer, Preisindizes ohne Dividenden, Cash = US-Zins (Rohdaten `results/H6_portfolio.csv`, Skript `scripts/check_trend_portfolio.py`, 7 Tests):

| | Filter-Korb | Buy&Hold-Korb | nur S&P 500 (Filter) |
|---|---|---|---|
| CAGR | 7,3 % | 8,3 % | 8,1 % |
| Volatilität | 8,2 % | 13,5 % | 12,5 % |
| Sharpe | **0,63** | 0,49 | 0,51 |
| Max. Verlust | **−14,8 %** | −47,1 % | −21,7 % |
| Schlechtestes Jahr | −11,2 % | −33,3 % | −16,6 % |

- Ergebnis nach dem vorab festgelegten Kriterium: **nicht bestanden**. Der Sharpe-Vorsprung von +0,14 ist nicht statistisch belegt (90-%-Intervall −0,11 bis +0,39, p = 0,18); der maximale Verlust ist dagegen auf ein Drittel geschrumpft.
- Ein erster Lauf hatte einen Konstruktionsfehler von mir (an Wochenenden stand der Korb zu 100 % in BTC); er ist im Register als Lauf 1 dokumentiert, maßgeblich ist der korrigierte Lauf 2.
- Lesart für Nick: Wer „Geld sicher halten" ernst nimmt, fährt mit dem Korb besser als mit einem einzelnen Markt (halbe Volatilität, ein Drittel des Verlusts, ca. 1 Prozentpunkt weniger Rendite als Buy&Hold). Das ist ein Risikoschutz, kein bewiesener Renditevorteil. Umsetzung: in TradingView läuft das Skript je Markt einzeln; einen echten Korb in einem Skript gibt es (noch) nicht.

## TradingView-Fund 2026-10-21: Einstiege wurden bei Kurslücken abgelehnt (behoben in v1.2)

Nick hat den Monats-Chart von `SP:SPX` (Datenbeginn 1871) mit dem Skript v1.1 laufen lassen: 76 Trades. Der Abgleich der abgelesenen Trades ab 1932 mit der Python-Referenz ergab: **Ausstiege 44 von 44 identisch**, aber nur 33 von 46 Einstiegen. Ursache: Die Stückzahl (100 % des Eigenkapitals) wird am Schlusskurs des Signalmonats berechnet, die Order füllt zur Eröffnung des Folgemonats. Eröffnet der Markt höher, reicht das Kapital nicht, und TradingView lehnt den Einstieg ab. Beleg an den 22 Einstiegen seit 1990, für die Eröffnungskurse vorliegen: Bei Kurslücke nach oben fehlte der Einstieg in 8 von 10 Fällen, bei Lücke nach unten oder null kam er in 10 von 12 Fällen (die beiden Ausreißer sind Monate mit Lücke genau 0 in den Yahoo-Daten). Der Einstieg kam dann Monate später oder gar nicht, ein Teil der Aufwärtsphase fehlte. Die Strategie-Regel selbst ist korrekt (Ausstiege identisch).

- **Fix in v1.2:** explizite Stückzahl mit Puffer (Eingabe „Ordergröße in % des Eigenkapitals", Standard 97 %, deckt Lücken bis ca. 3 %) und optional **feste Ordergröße** statt Zinseszins (Eingabe „Feste Ordergröße", z. B. 10000). Gilt auch für `TrendFilter_MA12_Plus.pine`. In TradingView noch nicht probiert; erwartet: mehr Trades als 76 und alle Python-Einstiege ab 1932 wiederzufinden.
- **76 gegen 60:** TradingView hat Daten ab 1871, 26 der Trades liegen vor 1932 (dort nur Monatsdaten, kein Python-Gegenstück; meine Referenz beginnt 1928). Vor 1932 sind die Daten nicht vergleichbar.
- **„Zu viel Kapital":** Die Größen in der Trade-Liste folgen dem Zinseszins (aus 10.000 werden bis 2025 knapp 11 Millionen). Wer das nicht will, setzt „Feste Ordergröße" auf 10000.
- Alte Fassung zur Sicherheit: `deploy/tradingview/TrendFilter_MA12_v1.1_alt.pine`.

## Verbesserungsideen aus GitHub (H7–H10, 2026-10-21): keine bringt etwas

Recherche in 4 Themen (Rohdaten `research/github/ergebnis_rohdaten.json`); die meisten gefundenen Repos sind klein und kaum geprüft, das einzige große (3.000 Sterne) setzt das schon getestete Faber-Timing um. Vier neue Ideen wurden vorab registriert und gegen die Basis gemessen (SPY, MA12, 1993–2022, Basis: CAGR 9,4 %, Sharpe 0,60, max. Verlust −22,5 %):

| Idee | CAGR | Sharpe | Max. Verlust | ΔSharpe (p) |
|---|---|---|---|---|
| H7 Anleihe (VUSTX, eigener Filter) statt Cash | 9,9 % | 0,59 | −24,9 % | −0,01 (0,54) |
| H7 Anleihe IEF (ab 2003) | 10,0 % | 0,62 | −22,5 % | +0,03 (0,17) |
| H8 Hysterese-Band 1 % | 9,7 % | 0,61 | −20,2 % | +0,02 (0,35) |
| H9 Vol-Skalierung, Ziel 15 % | 8,7 % | 0,59 | −20,3 % | −0,01 (0,58) |
| H9 Vol-Skalierung, Ziel 10 % | 7,5 % | 0,59 | −17,9 % | −0,01 (0,58) |
| H10 Inverse-Vol-Korb statt Gleichgewicht (17 Märkte) | 6,5 % | 0,57 | −16,4 % | −0,04 (0,87) |

**Ergebnis: nicht bestanden, die Basis bleibt.** Die Ideen verändern nur das Risiko-Rendite-Verhältnis (H8/H9 etwas kleinerer Verlust gegen weniger Rendite), keine verbessert den Sharpe belegbar.

## Belegte Strategie für Nicks Vorgaben (H11 und MT5, 2026-10-23)

**Vorgaben:** Marktrendite bei halbem Verlust, höchstens ca. 20 % Verlust, breit über Märkte, CFD/Futures per Alarm oder MetaTrader, Hebel bis 1,5x erwünscht.

**Was belegt ist (Lab, 17-Märkte-Korb, 1991–2022, 10 bp je Seite):**

| Variante | CAGR | Sharpe | MaxDD |
|---|---|---|---|
| Buy&Hold-Korb | 8,3 % | 0,49 | −47,1 % |
| **Monats-MA12 je Markt, gleichgewichtet, ohne Hebel (Empfehlung)** | **7,3 %** | **0,63** | **−14,7 %** |
| + Vol-Skalierung, Hebel bis 1,5x (H11 Hauptlauf) | 6,2 % | 0,54 | −16,3 % |
| + Vol-Skalierung ohne Hebel | 6,0 % | 0,57 | −12,6 % |
| + Trailing-Stop | 5,3 % | 0,44 | −17,3 % |
| + Trailing-Stop und R:R 3:1 | 5,1 % | 0,42 | −17,5 % |

**Ehrlich:** "Marktrendite" wird nicht erreicht (ca. 1 Pp. darunter), "halber Verlust" schon (ein Drittel). Hebel 1,5x und Stops sind nicht belegt und hier schlechter. Ein einzelner Markt (nur S&P 500) hält die 20 % nicht sicher: im MT5-Test auf US500 2012–2026 lag der Equity-Drawdown bei 27 % (Corona-Crash, der Monatsfilter reagiert erst am Monatsende). Die 20 % gelten für den Korb aus vielen Märkten.

**Umsetzung:** TradingView `TrendFilter_MA12_v2.pine` (Strategie, ein Markt, Zusätze schaltbar und AUS) plus `TrendFilter_MA12_Dashboard.pine` (17 Märkte, Zielgewicht je Markt und Investitionsquote, Alarm am Monatsende). MT5: `TrendFilter_MA12_v2.mq5` (Basis identisch zu v1.10, Zusätze schaltbar). Für den Korb in MT5 den EA je Symbol mit `InpExposure = 1 / Anzahl Märkte` auf eigene Charts legen.

**MT5-Strategietester (EA v2, US500 D1, Modell 2, 2012–2026-10-15, Start 10 000 USD):**

| Variante | Netto-Gewinn | Equity-DD | Trades | Anmerkung |
|---|---|---|---|---|
| Basis (alles AUS, identisch zu v1.10) | 8 237,57 | 26,95 % | 12 | Signale 22/22 gleich Python-Referenz |
| Vol-Skalierung bis 1,5x | 6 547,67 | 33,18 % | 53 | Hebel stand vor dem Corona-Crash auf Maximum |
| Trailing-Stop | 9 015,46 | 23,98 % | 16 | |
| Trailing-Stop + R:R 3:1 | 9 225,11 | 23,88 % | 20 | |
| Vol-Skalierung ohne Hebel (Höchstgewicht 1,0) | 6 883,51 | 24,61 % | 27 | gleicher Test, später nachgeholt |
| Vol ohne Hebel + Trailing-Stop | 7 679,92 | 20,66 % | 28 | |
| Vol ohne Hebel + Stop + R:R 3:1 | 7 704,39 | 20,62 % | 31 | |

Die Stop-Varianten sehen auf diesem einen Pfad (ein Markt, 14 Jahre, Stops im Tagesverlauf) besser aus. Das ist **kein** Beleg: Das vorab festgelegte Kriterium (17 Märkte, 30 Jahre) verfehlt der Stop; ein einzelner günstiger Pfad ändert das Ergebnis nicht. Modell 2 enthält keine CFD-Finanzierung (Swap), keine Steuern und keine echten Intraday-Kurse.

## Konstanz-Optimierung (H12, 2026-10-23): keine belegte Verbesserung

Ziel: wenig Verlust und gleichmäßig gute Gewinne. Kennzahl vorab: UPI = CAGR / Ulcer-Index (je höher, desto besser). 17-Märkte-Korb, ohne Hebel, 1991–2022:

| Variante | CAGR | MaxDD | Ulcer | UPI | Zeit unter −10 % | 3J-Fenster > 0 |
|---|---|---|---|---|---|---|
| Buy&Hold | 8,25 % | −47,1 % | 13,98 % | 0,59 | 33,6 % | 87,3 % |
| **MA12 (Basis, belegt)** | **7,30 %** | **−14,8 %** | 6,75 % | 1,08 | 19,6 % | 94,7 % |
| + Vol-Ziel 15 % (kein Hebel) | 5,99 % | −12,6 % | 5,22 % | 1,15 | 5,3 % | 94,1 % |
| + Vol-Ziel 20 % | 6,43 % | −14,1 % | 5,99 % | 1,07 | 8,0 % | 93,6 % |
| + Vol-Ziel 25 % | 6,72 % | −14,4 % | 6,31 % | 1,07 | 9,7 % | 94,2 % |
| Signal-Mischung MA6/9/12 (`ens3`) | 7,28 % | −13,5 % | 6,21 % | 1,17 | 13,1 % | 95,5 % |
| `ens3` + Vol-Ziel 20 % | 6,33 % | −13,0 % | 5,49 % | 1,15 | 5,0 % | 94,1 % |

**Ergebnis:** Nach den vorab festgelegten Kriterien besteht keine Variante. Die Vol-Skalierung senkt den Verlust, kostet aber 0,6–1,3 Pp. Rendite und ist in der zweiten Hälfte (2007–2022) schlechter als die Basis. Die Signal-Mischung `ens3` hält die Rendite und senkt den Verlust etwas, scheitert aber knapp am Kriterium (UPI +8,5 % statt +10 %, in 1991–2006 nicht besser) und hat auf dem S&P allein den größeren Verlust. Sie bleibt Kandidat für eine Bestätigung auf neuen Daten.

**Genaue Analyse der Basis (Korb):** 22 von 32 Jahren positiv (Buy&Hold 24), schlechtestes Jahr −11,2 % (B&H −33,2 %). Schwach sind Aufschwung-Jahre mit Wechseln (2010 −0,1 %, 2012 +1,5 %, 2014 −1,0 %, 2015 −3,1 %, 2019 +4,2 %). Längste Phase unter dem Höchststand 3,6 Jahre (B&H 5,7). Schlechtester 3-Jahres-CAGR −3,7 % (B&H −16,2 %).

## Nachziehender Stop ("Ratsche", H13, 2026-10-23): im Korb schlechter, nur als Schalter

Regel `Stufen`: Anfangs-Stop = Einstieg − 1R (R = 2 x Vol / Wurzel(12) x Einstieg). Erreicht der höchste Schlusskurs Einstieg + k x R, rückt der Stop auf Einstieg + (k − 1) x R: Break-even bei +1R, danach je +1R eine Stufe. Der Stop sinkt nie. Alternative `Chandelier-Ratsche`: höchster Schlusskurs x (1 − 2 x Vol / Wurzel(12)), sinkt nie.

| 17-Märkte-Korb 1991–2022 | CAGR | MaxDD | UPI | Sharpe |
|---|---|---|---|---|
| Basis (kein Stop) | 7,30 % | −14,8 % | 1,08 | 0,63 |
| Stufen-Stop | 6,29 % | −15,8 % | 0,84 | 0,53 |
| Chandelier-Ratsche | 5,62 % | −17,6 % | 0,72 | 0,48 |

Im Korb verschlechtern beide den Verlust und die Rendite (Kriterien nicht erfüllt). Auf dem S&P 500 allein (1928–2022) helfen sie: MaxDD −43,7 % (Stufen) bzw. −39,7 % (Ratsche) statt −52,1 %, UPI 0,56 bzw. 0,61 statt 0,45. Nach Teilperioden hilft der Stop bis 1999 und schadet seit 2000 (explorativ).

MT5-Strategietester (EA v2, US500 D1, 2012–2026, 10 000 USD): Basis 8 237,57 USD bei 26,95 % Equity-DD; Stufen-Stop 7 693,62 USD bei 21,63 % (14 Trades); Chandelier-Ratsche 8 192,83 USD bei 21,97 % (22 Trades); Vol ohne Hebel + Stufen-Stop 6 258,88 USD bei 22,94 % (30 Trades). Ein Markt, ein Pfad: kein Beleg.

## Härtetests P1 (H14–H18, 2026-10-26): Verlustvorteil robust, MaxDD-Erwartung realistischer

| Test | Ergebnis |
|---|---|
| H14 Placebo (1000 zufällige Zustandsfolgen, gleiche Marktzeit) | bestanden: UPI 1,081 gegen p95 0,961; MaxDD −14,75 % besser als alle 1000 Placebos (bestes −23,3 %) |
| H15 Bootstrap (2000 Ziehungen, 60-Tage-Blöcke) | Verlustvorteil belegt (MaxDD +7,8 Pp besser, 5. Perzentil); Rendite −1,0 Pp [−4,1; +2,3], P(schlechter) 70 %, nicht belegt |
| H16 Timing-Luck (21 Entscheidungstage) | Streuung groß: MaxDD −15,9 % bis −24,0 % (Median −20,7 %), hängt am Corona-Crash; `tranche21` 7,15 % / −20,4 % |
| H17 Marktauswahl (Leave-one-out, 300 Teilmengen) | bestanden: MaxDD in 100 %, UPI in 99,4 % besser; Rendite in 97 % unter B&H (Median −0,8 Pp) |
| H18 Kosten | Futures/ETF: Vorsprung hält bis ca. 125 bp je Seite. CFD mit Finanzierung des vollen Nominalwerts: nur 3,15 % CAGR, −22 % MaxDD, UPI unter B&H |

**Was das für Nick heißt:**
- Der Drawdown-Vorteil gegenüber Buy&Hold ist echt und hängt nicht an einzelnen Märkten oder am Zufall.
- **Der historische größte Verlust von −14,7 % ist optimistisch.** Erwartet werden −20 bis −30 % (Bootstrap-Median −20,9 %, schlechtester 5-%-Fall −31,6 %). Das Ziel "höchstens ca. 20 % Verlust" ist damit nicht sicher einzuhalten.
- Ein Renditenachteil von etwa 1 Pp ist möglich, ein Renditevorteil ist nicht belegt.
- Tranchen (Entscheidung auf mehrere Tage verteilen) nehmen den Termin-Zufall heraus; im Test knapp besser als der Median.
- Umsetzung per CFD ist teuer, weil der volle Nominalwert finanziert wird. Futures oder ETFs sind kostenseitig deutlich besser; bei CFDs Finanzierungsaufschlag und Dividendenausgleich des Anbieters prüfen.

