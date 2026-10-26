# Familie: Aktienfaktoren / Faktor-Timing / Faktor-Kombination

Stand der Recherche: 2026-10-12. Budget war ca. 15 Web-Abrufe; tatsächlich genutzt: 17 (davon 1 gescheitert mit HTTP 504), dazu 1 PDF lokal mit pdftotext gelesen. Das Budget ist also leicht überschritten.
Alle Zahlen stammen aus tatsächlich gelesenen Seiten/PDFs oder sind ausdrücklich als "Suchsnippet", "Sekundärquelle" oder "aus Gedächtnis, nicht verifiziert" markiert. Was ich nicht gefunden habe, steht als "nicht gefunden".

## 0. Kurzfazit (ehrlich)

- Der Faktor-Zoo ist real, aber deutlich kleiner als publiziert. Jensen/Kelly/Pedersen (JF 2023) finden, dass die Mehrheit von 153 Faktoren replizierbar ist (13 Themen, 93 Länder). Hou/Xue/Zhang (RFS 2020) finden das Gegenteil bei strenger Behandlung von Mikro-Caps: 286 von 447 Anomalien (64 %) sind insignifikant, bei Hürde t >= 3 sind es 380 (85 %). Beide Befunde sind kein Widerspruch: Die Antwort hängt von Gewichtung (Value-Weight, NYSE-Breakpoints) und Test ab. Konsequenz für uns: nur große, einfache, breit belegte Faktoren (Value, Profitability/Quality, Investment, Momentum, Low-Beta) und nur Value-Weight-Konstruktionen anfassen.
- Nachpublikations-Verfall ist belegt (McLean/Pontiff: ca. -26 % außerhalb der Stichprobe, ca. -58 % nach Publikation, 97 Prädiktoren). Linnainmaa/Roberts: Profitability- und Investment-Prämien sind 1926-1963 nahe null; die Mehrheit der buchhalterischen Anomalien ist vermutlich Data-Snooping.
- Die Faktor-Zeitreihen der Ken French Library sind Long-Short, brutto und NICHT handelbar. Für einen Kleinanleger mit Gratis-Daten gibt es nur zwei handelbare Wege: (a) Long-only Faktor-ETFs (MTUM/QUAL/VLUE/USMV) mit kurzer Historie ab 2011-2013, (b) Paare aus ETFs als schwache Proxies. Beides hat kaum statistische Aussagekraft (13 Jahre, hohe Korrelation zu SPY). Das passt zur Projekterfahrung (CLAUDE.md: ETF-v4 verliert gegen S&P-500-Buy&Hold, Vol-Overlay brachte nichts).
- Faktor-Timing: Zeitreihen-Faktor-Momentum hat die stärkste Evidenz (Gupta/Kelly: 59 von 65 Faktoren mit positivem AR(1), TSFM-Sharpe 0,84 bei 1-Monats-Fenster, netto 0,63 bei 12-Monats-Fenster). Kontrarisches Wertspread-Timing hat KEINE robuste Evidenz (Asness et al. 2017). Daraus folgt die Rangfolge unten.
- Nicht abgerufen und deshalb NICHT als Paper geführt: Harvey/Liu/Zhu 2016, Fama/French 2015 (Five-Factor), Arnott/Clements/Kalesnik/Linnainmaa (Factor Momentum), Daniel/Moskowitz (Momentum Crashes), Blitz-Arbeiten, Frazzini/Israel/Moskowitz 2015 (Handelskosten), Chen/Zimmermann (Open Source Asset Pricing, evtl. gratis Signaldaten, nicht geprüft). Sie werden nur dort erwähnt, wo ein gelesenes Paper sie zitiert.

Ranking-Begründung: "Robustheit" = Evidenzstärke x Handelbarkeit mit Gratis-Daten x Überleben nach Kosten. Platz 1 ist die langweiligste Strategie (statisch, diversifiziert), Platz 2 und 3 sind Timing-Overlays mit guter Evidenz, aber Long-Short-Charakter. Platz 4 ist die einzige direkt handelbare Version und hat vermutlich keinen Edge. Platz 5 ist ein dokumentiertes Negativ-Ergebnis.

## 1. Abrufstatus (Transparenz)

| Quelle | Status |
|---|---|
| NBER w23394 Hou/Xue/Zhang "Replicating Anomalies" | ABGERUFEN (Abstract-Seite, WebFetch) |
| NBER w28432 Jensen/Kelly/Pedersen | WebFetch 504 Gateway Timeout; Inhalt nur über Websuche (Snippet-Zusammenfassung). Volltext NICHT gelesen. |
| Gupta/Kelly "Factor Momentum Everywhere" (AQR-PDF) | ABGERUFEN, lokal mit pdftotext gelesen: Einleitung, Faktorkonstruktion, TSFM-Gleichungen, Kostenabschnitt. Abbildungen/Tabellen durch Schriftkodierung unlesbar; nur Fließtext-Zahlen verwertet. |
| Ken French Data Library (Startseite + 5-Factor-Detailseite) | ABGERUFEN |
| AQR Datasets-Seite | ABGERUFEN |
| Ehsani/Linnainmaa NBER w25551 | nur Websuche (Snippet-Ebene), Volltext nicht gelesen |
| Novy-Marx/Velikov NBER w20721 | nur Websuche (Snippet-Ebene) |
| Barroso/Santa-Clara JFE 2015 | nur Websuche und Sekundärquellen (CXO Advisory, Blog-Replikation); Original nicht gelesen |
| Cederburg et al. JFE 2020 | nur Websuche. Die Zahlen "MOM Sharpe 0,48 -> 0,99" stammen aus der Schwesternotiz `volmgmt.md`, dort wurde die Lehigh-PDF gelesen; ich habe sie hier nicht selbst geprüft. |
| Asness/Chandra/Ilmanen/Israel 2017 | nur Websuche (Snippet-Ebene) |
| McLean/Pontiff JF 2016 | nur Websuche (Snippet-Ebene) |
| Fitzgibbons et al. "Long-Only Style Investing" | nur Websuche (Snippet-Ebene); Zahlen stammen aus Alpha-Architect-Zusammenfassung |
| Linnainmaa/Roberts RFS 2018 | nur Websuche (Snippet-Ebene) |
| ETF-Auflagedaten (MTUM, QUAL, VLUE, USMV) | nur Websuche, Sekundärquellen (Robinhood, TrackInsight, TradingView), keine Emittenten-Seite |
| r-bloggers Replikation Barroso/Santa-Clara | ABGERUFEN, aber es repliziert eine ETF-Rotation (nicht das Original); nur für "126 Tage" nützlich |

Vor dem Kodieren sollten die Originale (BSC, Ehsani/Linnainmaa, Asness et al.) im Browser geöffnet werden, um Formeldetails zu prüfen.

## 2. Gemeinsame Daten- und Implementierungsregeln

### 2.1 Gratis-Daten (konkret)

Ken French Data Library, Basis `https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/` (Dateinamen auf der Seite gelesen; Pfad `ftp/<Name>_CSV.zip` bzw. `_TXT.zip`):

| Datensatz | Datei | Start / Stand |
|---|---|---|
| FF 5 Faktoren (2x3) monatlich | `ftp/F-F_Research_Data_5_Factors_2x3_CSV.zip` | Monatswerte Juli 1963 bis August 2026 (auf Seite gelesen). Spalten: Mkt-RF, SMB, HML, RMW, CMA, RF. |
| FF 5 Faktoren (2x3) täglich | `ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip` | Start laut Seite nicht genannt; vermutlich 1963-07-01 (Annahme) |
| FF 3 Faktoren monatlich/täglich/wöchentlich | `ftp/F-F_Research_Data_Factors_CSV.zip`, `..._daily_CSV.zip`, `..._weekly_CSV.zip` | Start auf Seite nicht genannt; aus Gedächtnis Juli 1926, nicht verifiziert |
| Momentum (Mom) monatlich/täglich | `ftp/F-F_Momentum_Factor_CSV.zip`, `ftp/F-F_Momentum_Factor_daily_CSV.zip` | Start auf Seite nicht genannt; aus Gedächtnis Jan 1927 (monatlich) bzw. Nov 1926 (täglich), nicht verifiziert |
| ST_Reversal, LT_Reversal monatlich/täglich | `ftp/F-F_ST_Reversal_Factor_CSV.zip`, `ftp/F-F_LT_Reversal_Factor_CSV.zip` (+ `_daily`) | Start nicht genannt |
| Developed/Europe/Japan/Asia-Pacific/North America 3 und 5 Faktoren + Mom | `ftp/Developed_5_Factors_CSV.zip`, `ftp/Developed_Mom_Factor_CSV.zip` usw. (+ Daily) | Start nicht genannt; aus Gedächtnis ca. 1990 (nicht verifiziert) |
| 25 Portfolios Size x B/M | `ftp/25_Portfolios_5x5_CSV.zip` (+ Daily, Wout_Div) | |

Konstruktion RMW/CMA/HML/SMB laut French-Seite: 6 Value-Weight-Portfolios aus Size x (B/M | OP | INV), jährlich im Juni neu gebildet (Marktkapitalisierung Dezember t-1 und Juni t), gehalten Juli t bis Juni t+1. Universum NYSE, AMEX, NASDAQ. Das heißt: HML/RMW/CMA haben niedrigen Umschlag, aber die Faktoren wechseln nur einmal im Jahr die Zusammensetzung.
Hinweis zum Einlesen: Die CSV-Dateien haben Kopfzeilen und mehrere Blöcke (Monatlich, danach Jährlich). Werte sind in Prozent. `pandas_datareader` (`famafrench`) funktioniert je nach pandas-Version nicht; direkter ZIP-Download ist robuster.

AQR Datasets (`https://www.aqr.com/Insights/Datasets`, Seite gelesen; Stand der Dateien Juli bis Sept 2026):
- Quality Minus Junk: Factors, Monthly und Daily; US-Sample ab 1956, Global ab 1986.
- Betting Against Beta: Equity Factors, Monthly und Daily; USA + 23 Länder; Start auf der Seite nicht genannt.
- The Devil in HML's Details: Factors, Monthly und Daily; USA + 23 Länder; Start nicht genannt.
- Value and Momentum Everywhere: Factors, Monthly; 8 Märkte/Anlageklassen; Start nicht genannt.
- AQR Momentum Indices, Monthly.
- Dateiformat (xlsx/csv) auf der Seite nicht genannt.
- "Century of Factor Premia" und "Time Series Momentum" standen NICHT auf der Seite (entgegen meiner Erinnerung).

ETFs (yfinance, `auto_adjust=True`), Auflagedaten nur aus Sekundärquellen:
- MTUM (iShares MSCI USA Momentum Factor): 2013-04-16
- VLUE (iShares MSCI USA Value Factor): 2013-04-16
- QUAL (iShares MSCI USA Quality Factor): 2013-07-16 (einzelne Quellen: 07-18)
- USMV (iShares MSCI USA Min Vol Factor): 2011-10-18
- SPY ab 1993-01-29, IWM ab Mai 2000, IWD/IWF ab Mai 2000: aus Gedächtnis, NICHT verifiziert.
- Cash-Proxy: BIL/SHV oder ^IRX (Auflagedaten nicht geprüft).
- Gemeinsame Historie der vier Faktor-ETFs: ab 2013-07-16, also ca. 13 Jahre (inkl. Q4 2026 ca. 13,2 Jahre). Das reicht NICHT für statistisch belastbare Alpha-Tests bei Tracking Errors von wenigen Prozent.
- Für deutsche Privatanleger sind die US-ETFs wegen der KID/PRIIPs-Regeln meist nicht kaufbar; UCITS-Äquivalente (iShares MSCI World Momentum/Value/Quality Factor) existieren nach meinem Wissen, Ticker und Historie habe ich NICHT geprüft.

### 2.2 Ausführungsregel
Signal aus Daten bis einschließlich Schlusskurs bzw. Monatsende t, Anwendung erst auf Renditen ab t+1. Für ETF-Versionen: Ausführung zum Eröffnungskurs des nächsten Handelstags (Quant-Lab-Regel 4), Sensitivität: Schlusskurs t+1.

### 2.3 Kosten
- Gupta/Kelly rechnen 10 bps pro Einheit Umschlag (zitiert Frazzini/Israel/Moskowitz 2015, nicht gelesen). Die Faktoren der French-Library enthalten KEINE Handels-, Leih- und Finanzierungskosten.
- Novy-Marx/Velikov (Snippet-Ebene): Umschlag unter 50 % pro Monat ist die Trennlinie; die meisten Anomalien darunter haben nach Kosten noch signifikante Netto-Spreads, wenige darüber; Size, Value und Profitability haben die höchste Kapazität; ein Buy/Hold-Spread ist die wirksamste Kostenbremse. Das lässt sich ohne CRSP/Compustat nicht nachbauen.
- Für die Backtests hier: Kosten als Sensitivitätsgitter (0 / 1 / 2 / 4 % p.a. Haircut auf den Faktor-Teil; Mom mit höherem Umschlag eher am oberen Ende). Das Gitter ist eine EIGENE Annahme, nicht aus einem Paper.
- Deutsche Abgeltungssteuer separat ausweisen (Projektregel 4).

## 3. Strategien (nach erwarteter Robustheit sortiert)

### 3.1 static_multifactor_equal_risk — Statische Multi-Faktor-Kombination (Equal-Risk)

Idee: Kein Timing, nur Diversifikation über wenige breit belegte Faktoren, risikogewichtet. Das ist die Basislinie, gegen die jedes Timing antreten muss.

Regel (Pseudocode):
```
Daten monatlich (Prozent / 100):
  HML, RMW, CMA aus F-F_Research_Data_5_Factors_2x3 (ab 1963-07)
  Mom aus F-F_Momentum_Factor
  K = {HML, RMW, CMA, Mom}; SMB bewusst NICHT im Kern (nur Variante).
  Variante A: HML -> AQR HML_Devil (US), RMW -> AQR QMJ (US).
Am Monatsende t (nur Daten bis t):
  vol_i,t = std(f_i, Monate t-35..t) * sqrt(12)      # min. 24 Beobachtungen
  w_i,t   = (1/vol_i,t) / sum_k (1/vol_k,t)           # sum w = 1
  port_vol_t = sqrt(w' * Cov36M * w) * sqrt(12)
  lev_t = min(2.0, 0.10 / port_vol_t)                 # Ziel-Vol 10 % p.a.; Cap 2 = eigene Annahme
Rendite Monat t+1:
  R_{t+1} = lev_t * sum_i w_i,t * f_i,t+1 - Haircut/12 - (lev_t>1 ? (lev_t-1)*(RF_{t+1} + 0.005/12) : 0)
Rebalancing monatlich; Gewichte gelten für den ganzen Folgemonat.
Pflichtvergleiche: (a) 1/N ohne Vol-Gewichtung, (b) Mkt-RF mit gleicher Ziel-Vol, (c) Teilperioden 1963-1989, 1990-2007, 2008-2026.
```
Handelbare Annäherung: siehe 3.4 (Long-only-ETF-Mix); echte Long-Short-Umsetzung braucht Aktien-Shorts und ist mit Gratis-Daten nicht überprüfbar.

Evidenz:
- Jensen/Kelly/Pedersen: Mehrheit von 153 Faktoren repliziert, 13 Themen, die meisten sind Teil des Tangentialportfolios, funktionieren in 93 Ländern (Snippet-Ebene).
- Gupta/Kelly (gelesen): Der gleichgewichtete Durchschnitt der 65 Roh-Faktoren hat eine annualisierte Sharpe-Ratio von 1,07 (brutto, Stichprobe ab 1960er bis ca. 2017, Long-Short-Charakteristikfaktoren). Beste Netto-Sharpe unter den Fama-French-Faktoren: RMW 0,45 (nach 10 bps/Umschlag). 3 von 65 Faktoren haben negative Durchschnittsrendite, 25 sind nicht von null unterscheidbar, die stärksten sind die "üblichen Verdächtigen" (BAB, Momentum, Industrie-Momentum, Bewertungsraten).
- Hou/Xue/Zhang: 64 % der Anomalien insignifikant (Value-Weight, NYSE-Breakpoints), 85 % bei t >= 3; Gegenmodell: q-Faktoren erklären 115 der 161 signifikanten Anomalien (Alpha insignifikant).

Verfall / Kritik:
- McLean/Pontiff (97 Variablen, finale Fassung): ca. -26 % außerhalb der Stichprobe (Obergrenze für Data-Mining), ca. -58 % nach Publikation; stärkere Rückgänge bei höherer In-Sample-Rendite; Korrelationen publizierter Prädiktoren steigen nach Publikation. Ältere Arbeitspapierfassung nannte 82 Merkmale und ca. 35 %: nicht verwechseln.
- Linnainmaa/Roberts: Profitability- und Investment-Prämien sind 1926-1963 nahe null; Verschiebung des Startdatums senkt Durchschnittsrenditen/Alphas um 50 bis 75 %. Das gilt direkt für RMW und CMA, deren Daten erst 1963 beginnen: Wir haben praktisch nur eine Stichprobe, in der sie funktionierten.
- Das Ende der Stichprobe der Primärliteratur liegt bei ca. 2017-2021; die Jahre 2018-2026 sind der eigentliche Test.

Kosten: Hohe Kapazität bei Size/Value/Profitability (Novy-Marx/Velikov, Snippet). Mom ist der Kostentreiber. Retail-Zugang zu den Long-Short-Portfolios fehlt; Leihgebühren für Short-Seite sind in den Daten nicht enthalten.

Tail-Risiken: Value-Faktor-Drawdowns über mehrere Jahre (Datenbezug aus dieser Session: nicht berechnet, nur Hinweis); Momentum-Crashes bei Marktrebounds (siehe 3.2); Hebel (Cap 2) verstärkt beides. Equal-Risk-Gewichtung überwichtet den ruhigsten Faktor (meist CMA/RMW) und kann dort Konzentrationsrisiko erzeugen.

### 3.2 vol_managed_momentum_bsc — Risiko-gesteuertes Momentum (Barroso/Santa-Clara)

Regel (Pseudocode):
```
Daten: F-F_Momentum_Factor_daily (Mom, Prozent/100), RF aus F-F_Research_Data_Factors_daily.
Am letzten Handelstag s jedes Monats t:
  r = Mom-Tagesrenditen der letzten 126 Handelstage bis einschließlich s
  sigma_hat = sqrt(252) * std(r)                       # BSC-Original: Realisierte Varianz aus 126 Tagen; ob Mittelwert abgezogen wird, nicht verifiziert (Unterschied klein)
  w_t = min(Cap, 0.12 / sigma_hat),  Cap = 2.0 (Sensitivität Cap = unbegrenzt und Cap = 1.0)
Im Folgemonat, jeden Handelstag d:
  R_d = w_t * Mom_d + (1 - w_t) * 0     # Mom ist selbstfinanzierend (excess); Hebel > 1 kostet RF + 0.5 %/Jahr (eigene Annahme)
Gewicht konstant im Monat (keine Zwischen-Rebalancierung); Ausführung ab erstem Handelstag nach s.
Pflichtvergleiche: (a) ungemanagtes Mom, (b) Mom mit konstantem Hebel gleicher mittlerer Exposure (sonst misst man Hebel statt Timing),
(c) Teilperioden: 1927-1993, 1994-2007, 2008-2026; Stresstage (2009-03/04 Rebound, 2020-11, 2022).
```

Evidenz:
- Barroso/Santa-Clara (JFE 2015, Abstract per Suchsnippet): Das Risiko von Momentum ist stark zeitvariabel und vorhersagbar; Risikosteuerung "eliminiert Crashes praktisch und verdoppelt nahezu die Sharpe-Ratio". Sekundärquelle (CXO Advisory): Durchschnittsrendite 16,5 % gegenüber 14,5 % p.a., Ziel-Vol 12 %, 126 Tage, Stichprobe 1927-2011. Das ist NICHT aus dem Original gelesen.
- Cederburg et al. (JFE 2020, Snippet): Vol-Management schlägt über 103 Strategien hinweg NICHT systematisch das ungemanagte Portfolio, Momentum ist (neben Profitability und BAB) die Ausnahme. Aus `volmgmt.md` (dort gelesen): MOM-Sharpe 0,48 -> 0,99 (p = 0,00).

Verfall / Kritik: Aus `volmgmt.md` (Snippet-Ebene, nicht von mir geprüft): Barroso/Detzel sagen, dass nach Kosten außer dem Marktfaktor kaum ein Faktor übrig bleibt; eine Studie von 2024 sieht nur Markt und Momentum teilweise robust. Die Jahre 2018-2026 sind in der Primärliteratur kaum getestet.
Kosten: Mom wird monatlich umgeschichtet, plus Gewichtswechsel. In den French-Daten sind keine Kosten, kein Short-Borrow und keine Krisen-Illiquidität enthalten. Das ist hier der entscheidende Vorbehalt: die Sharpe-Verbesserung (brutto) kann die Kosten des Hebels in ruhigen Phasen nicht tragen.
Handelbarkeit: Es gibt keinen guten Gratis-ETF-Proxy für Long-Short-Momentum. Eine Annäherung wäre `MTUM - beta*SPY` (rollierende 252-Tage-Beta), aber der Tracking Error von MTUM gegen SPY ist klein, so dass der skalierte Hebel unrealistisch hoch würde. Deshalb: reine Forschungsstrategie auf French-Mom, nicht direkt handelbar.
Tail-Risiken: Volatilitätsschätzung hinkt: Das Gewicht ist nach einem Crash niedrig, genau wenn Momentum im Rebound wieder stark läuft ("Verpassen des Erholungsteils"); Gap-Risiken innerhalb des Monats werden nicht gemanagt.

### 3.3 tsfm_factor_momentum — Zeitreihen-Faktor-Momentum (Gupta/Kelly; Ehsani/Linnainmaa)

Idee: Jeder Faktor wird nach seiner EIGENEN jüngsten Rendite gewichtet (long bei positiver Historie, short bei negativer). Gupta/Kelly zeigen, dass das zeitreihenbasierte Verfahren dem Querschnittsverfahren überlegen ist.

Regel (Pseudocode; Gleichung (1) des Gupta/Kelly-Papiers nachgebaut, Formel im PDF teilweise durch Kodierung beschädigt, Details siehe Abschnitt "Unsicherheit"):
```
Universum U (monatlich, Excess-Returns, Vorzeichen so orientiert, dass die publizierte Prämie positiv ist):
  SMB, HML, RMW, CMA, Mom   (Ken French; ab 1963-07)
  QMJ_US, BAB_US            (AQR; Startdatum QMJ US 1956 laut AQR-Seite, BAB nicht genannt)
  => N = 7; gemeinsamer Start 1963-07; wegen Vol-Fenster erste Handelsmonate ab ca. 1973-07.
Am Monatsende t, Formationsfenster j in {12 (Haupt), 1 (Robustheitscheck)}:
  mean_j,i = 12 * mean(f_i, Monate t-j+1..t)                         # annualisierte Durchschnittsrendite im Fenster
  sigma_i  = sqrt(12) * std(f_i, letzte 36 Monate) falls j < 12, letzte 120 Monate falls j >= 12   # Gupta/Kelly: 3 bzw. 10 Jahre
  z_i      = mean_j,i / sigma_i
  s_i,t    = clip(z_i, -2, +2)
Haupt-Gewichte (vereinfachte, für kleines N robuste Variante; EIGENE Entscheidung):
  w_i,t = s_i,t / N
  R_{t+1} = sum_i w_i,t * f_i,t+1
Variante B (formale Gupta/Kelly-Definition: Long-Short mit Einheitshebel je Seite):
  L = {i: s_i > 0}, S = {i: s_i <= 0}
  R_{t+1} = sum_{i in L} (s_i / sum_L s) * f_i,t+1  -  sum_{i in S} (s_i / sum_S s) * f_i,t+1
  (bei S: s_i und Summe beide negativ => Gewichte positiv und auf 1 normiert; die Short-Seite wird subtrahiert.
   Bei kleinem N konzentriert sich die Short-Seite oft auf einen einzigen Faktor; deshalb nur als Variante testen.)
Rebalancing monatlich, Gewichte gelten für den Folgemonat t+1; kein Look-ahead.
Pflichtvergleiche: (a) 1/N der untimed Faktoren (gleiche mittlere Vorzeichen-Exposure beachten), (b) Mom allein, (c) Varianten j = 1, 6, 12, (d) Kostenhaircut-Gitter, (e) ohne Mom im Universum.
Handelbarer Proxy (nur 2013-2026, ohne statistische Aussagekraft): Long-only-Rotation je ETF F in {MTUM, QUAL, VLUE, USMV}:
  halte F statt SPY, falls (Rendite F - Rendite SPY) über 12 Monate > 0, sonst SPY. Monatssignal, Ausführung Open t+1.
```

Evidenz (Gupta/Kelly, gelesen):
- 65 Charakteristik-Faktoren; AR(1) im Monat durchschnittlich 0,11, positiv bei 59 von 65, signifikant bei 49 (zum Vergleich: Marktrendite 0,07).
- Einzelfaktor-Timing (Skalierung nach eigener 1-Monats-Rendite): Alpha positiv bei 61 von 65, signifikant bei 47; Informationsrate im Schnitt 0,33.
- Kombiniertes TSFM: Sharpe 0,84 (1-Monats-Fenster), 0,70 (12 Monate), 0,72 (5 Jahre). Alpha gegenüber dem gleichgewichteten Roh-Faktor-Portfolio 10,3 % p.a. (t = 4,6); durchschnittliche TSFM-Rendite 12,0 % p.a. (1-Monats-Fenster). Zum Vergleich: UMD Sharpe 0,56, gleichgewichtete Roh-Faktoren 1,07 (jeweils brutto).
- Nach Kosten (10 bps/Umschlag): TSFM(1-12) Sharpe 0,63 gegenüber 0,70 brutto; UMD netto 0,51; bester Fama-French-Faktor netto: RMW 0,45. Kurzfristige Reversal-Überrendite wird komplett von Kosten aufgefressen.
- International (Gupta/Kelly) ähnlich stark. Querschnitts-Variante CSFM hat Korrelation > 0,90 mit TSFM, aber negatives Alpha gegenüber TSFM.
- Ehsani/Linnainmaa (JF 2022, Snippet): Aktien-Momentum stammt aus Faktor-Momentum; Monatsrendite eines Faktors nach einem Gewinnjahr 51 bps (JF-Fassung; NBER 53 bps) gegenüber 6 bps (JF; NBER 1 bp) nach einem Verlustjahr. Momentum-Strategien crashen, wenn die Faktor-Autokorrelationen zusammenbrechen.

Verfall / Kritik:
- Gupta/Kelly (JPM 2019) endet ca. 2017; ich habe KEINE Post-Publikations-Replikation gefunden (nicht gesucht außerhalb der gelesenen Quellen). Nach McLean/Pontiff ist mit Verfall zu rechnen; nach Publikation steigt die Crowding-Gefahr.
- Der Befund beruht auf 65 breiten Stock-Level-Faktoren. Mit N = 5 bis 7 (French/AQR) fehlt die Diversifikation über viele schwache Faktoren; die Ergebnisse dürften schwächer und volatiler ausfallen. Das ist eine Erwartung, kein gemessener Befund.
- Hohe Überlappung mit Mom im Universum; Gupta/Kelly sagen selbst, dass UMD das 12-Monats-TSFM teilweise erklärt (2-12-Fenster).
Kosten: Umschlag vergleichbar mit Aktien-Momentum, "etwas niedriger" (Gupta/Kelly). In den French-Daten nicht modelliert. Die Short-Seite je Faktor ist wieder ein Aktien-Short-Portfolio.
Tail-Risiken: Gleichgerichtete Faktorwenden (z. B. harte Marktwenden), Short-Positionen in Faktoren, die plötzlich stark drehen; Konzentration auf wenige Faktoren bei Variante B.

Unsicherheit der Regel: Im extrahierten PDF-Text ist die Gleichung für s_i,j,t beschädigt. Gelesen wurde: z-Wert = durchschnittliche Rendite im Formationsfenster geteilt durch annualisierte Vol der vorherigen 3 Jahre (j < 12) bzw. 10 Jahre (j >= 12), Cap bei +-2 ("min(max(...,-2),2)"). Ob die Durchschnittsrendite annualisiert oder monatlich in den Zähler geht, ist aus dem Text nicht zweifelsfrei; da z nur durch Cap begrenzt ist, bestimmt das die Skalierung. Meine Annahme: beides auf Jahresbasis. Vor dem Kodieren im Original-PDF nachsehen.

### 3.4 factor_etf_blend_long_only — Long-only Faktor-ETF-Mix gegen SPY (handelbarer Proxy, vermutlich kein Edge)

Regel (Pseudocode):
```
Universum: MTUM, QUAL, VLUE, USMV; Benchmark: SPY. Datenstart gemeinsam ab 2013-07-16; Backtest ab 2013-08-01.
Am letzten Handelstag jedes Monats t (Schlusskurs): Zielgewichte 25 % je ETF (statisch). Drift-Korrektur nur, wenn |Ist - Ziel| > 5 %-Punkte (Kostenbremse; Sensitivität: immer monatlich, quartalsweise).
Ausführung: Eröffnungskurs des nächsten Handelstags.
Kosten: 2 bps einseitig Spread/Slippage als Basis, Sensitivität 5 und 10 bps; Fondsgebühren stecken im Adjusted Close.
Auswertung:
  (1) Überrendite gegen SPY, Tracking Error, Informationsrate.
  (2) Regression der täglichen Überrendite auf F-F 5 Faktoren + Mom (Daily) mit Newey-West (HAC) Standardfehlern.
  (3) Teilperioden 2013-2019, 2020-2026.
Erwartung (EIGENE Schätzung, vor dem Test festzuhalten): Überrendite nach Kosten innerhalb +-1 % p.a., nicht signifikant.
Abbruchkriterium: Informationsrate < 0,3 oder Alpha-t-Wert < 2 nach FF5+Mom-Regression => verwerfen und SPY halten.
```
Warum dieser Eintrag: Er ist die einzige direkt handelbare und mit Gratis-Daten vollständig testbare Faktor-Umsetzung, und er prüft die Kernaussage "Faktorprämien sind nach Kosten für einen Retail-Anleger realisierbar".

Evidenz: Fitzgibbons et al. (AQR, Snippet): Der "Mix" einzelner Stil-Portfolios (genau das hier) ist dem "Integrate" (Gesamtscore je Aktie) unterlegen: Alpha-Architect-Zusammenfassung 1,4 % (Mix) gegenüber 3,2 % (Integration) gegenüber MSCI World, bei Tracking-Error-Restriktion; autorennahe Quelle, nicht geprüft. Fraser-Jenkins et al. 2016 widersprechen laut einem Kritiker (nur über Snippet bekannt). Echte Live-Performance-Zahlen der Faktor-ETFs gegen SPY habe ich NICHT gefunden.
Verfall / Kritik: McLean/Pontiff (siehe 3.1). Nach Projekterfahrung (CLAUDE.md) schlug auch eine ETF-Momentum-Rotation den S&P-500-Buy&Hold nicht. Die ETFs sind Long-only: sie tragen den Marktfaktor und nur eine kleine Faktor-Neigung; die Faktorprämie ist schwach identifizierbar.
Kosten: Fondsgebühren der iShares-Faktor-ETFs habe ich NICHT geprüft. Handel mit ETFs ist günstig, aber die Prämie, die ein Long-only-Tilt erwischt, ist klein.
Tail-Risiken: Faktor-Dürre über mehrere Jahre bei gleichzeitigem Marktbeta; Sektor-Konzentration (z. B. Momentum-ETF stark in einem Sektor) ist eine versteckte Wette und kein Faktor; Index-Rebalancing der ETFs ist semi-annual (aus Gedächtnis, nicht verifiziert).
Steuern/Zugang: US-ETFs für Deutsche meist nicht handelbar (PRIIPs), UCITS-Äquivalente nicht geprüft.

### 3.5 contrarian_value_spread_timing — Kontrarisches Faktor-Timing über Bewertungsspread (Negativ-Eintrag)

Regel (Pseudocode; eigene Standardisierung der Idee, nicht die exakte Spezifikation eines gelesenen Papers):
```
Pro Faktor i in {HML, RMW, CMA, Mom, SMB}:
  VS_i,t = ln( BM_long-leg,t / BM_short-leg,t )     # BM = Summe Buchwert / Summe Marktwert je Leg, Monatsende t, Buchwerte mit mind. 6 Monaten Lag
  z_i,t  = (VS_i,t - mean(VS_i, 240 Monate)) / std(VS_i, 240 Monate), min. 120 Monate
  g_i,t  = clip(1 + 0.5 * z_i,t, 0, 2)
  w_i,t  = g_i,t / sum_k g_k,t           # normalisiert auf Summe = 1 (neutral 1/N)
  R_{t+1} = sum_i w_i,t * f_i,t+1
Monatlich, Ausführung t+1.
```
Gratis-Daten: NICHT möglich. Die Legs-B/M der Faktoren stehen nicht in den abgerufenen French-Dateien (nur Renditen); sie bräuchten CRSP/Compustat. Ein sauberer Gratis-Proxy ist mir nicht bekannt. Deshalb `free_data_ok = false`, und die Strategie ist als "nicht umsetzen" markiert.

Evidenz gegen die Strategie: Asness/Chandra/Ilmanen/Israel (JPM 2017, Snippet-Ebene): Faktoren sind nie auf Extremen; KEINE robuste Evidenz, dass Value-basiertes Faktor-Timing sinnvoll outperformt; Timing korreliert hoch mit dem Value-Faktor selbst und bringt wenig, wenn Value ohnehin im Portfolio ist. Antwort auf Arnott et al. (Research Affiliates 2016; Titel nur aus Suchtreffer bekannt, nicht abgerufen).
Verfall / Kritik: Die Debatte ist offen; ich habe kein Paper gefunden, das robustes kontrarisches Timing nach Kosten belegt. Vorsichtiger Grund: Spreads sind sehr persistent, Mean-Reversion tritt über Jahre auf, nicht über Monate; die effektive Anzahl unabhängiger Beobachtungen ist winzig.
Kosten: Der Overlay selbst erzeugt moderaten Umschlag, aber der Hauptmangel ist die Datenlage.
Tail-Risiken: Kontrarisches Timing erhöht das Gewicht genau dann, wenn ein Faktor leidet (Wertfalle, strukturelle Brüche).

## 4. Hypothesen-Vorschläge für `docs/HYPOTHESEN.md` (Projektregel 3, EIGENE Erwartungen)

| ID | Hypothese | Erwartung | Abbruchkriterium |
|---|---|---|---|
| H-F1 | Statische Equal-Risk-Kombination HML/RMW/CMA/Mom hat in 1990-2026 eine Sharpe-Ratio > Mkt-RF | brutto knapp darüber, nach 2 % Haircut ungefähr gleich | Netto-Sharpe nicht größer als Mkt-RF in beiden Teilperioden |
| H-F2 | Vol-Management erhöht die Mom-Sharpe in jeder Teilperiode | ja, brutto; nach 25 bps/Umschlag unklar | Sharpe-Gewinn verschwindet in 2008-2026 |
| H-F3 | TSFM (j = 12) auf 7 Faktoren schlägt 1/N der untimed Faktoren | Sharpe-Gewinn kleiner als bei Gupta/Kelly | Alpha gegenüber 1/N nicht signifikant (t < 2) |
| H-F4 | Faktor-ETF-Mix schlägt SPY nach Kosten | nein | IR < 0,3 oder FF5+Mom-Alpha t < 2 |
| H-F5 | Value-Spread-Timing | nicht testen (Daten fehlen) | |

Mehrfachtest-Hinweis: Jede Variante (j, Cap, Haircut) zählt für Deflated Sharpe / PBO.

## 5. Offene Lücken

- Kein Post-2018-Test von Faktor-Momentum gefunden. Genau dort liegt der echte Out-of-Sample-Test.
- Handelskosten-Quelle (Frazzini/Israel/Moskowitz 2015) nicht gelesen.
- ETF-Gebühren und Live-Performance der Faktor-ETFs nicht gefunden.
- Chen/Zimmermann "Open Source Cross-Sectional Asset Pricing" könnte Gratis-Signaldaten für stock-level Faktoren liefern (nicht in dieser Sitzung abgerufen; Idee nur aus Gedächtnis).
- Blitz, Hanauer und weitere Faktorkombinations-Literatur wurde im Abrufbudget nicht erreicht.

## 6. Quellen-URLs

Abgerufen (Volltext oder Abstract-Seite gelesen):
- Hou/Xue/Zhang, Replicating Anomalies (NBER w23394, RFS 33(5) 2020): https://www.nber.org/papers/w23394
- Gupta/Kelly, Factor Momentum Everywhere (JPM Quantitative Special Issue 2019): https://www.Aqr.Com/-/media/AQR/Documents/Insights/Journal-Article/Factor-Momentum-Everywhere-JPM-Quant-19.pdf?sc_lang=en und Landingpage https://www.aqr.com/Insights/Research/Working-Paper/Factor-Momentum-Everywhere
- Ken French Data Library: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
- French 5-Factor-Details: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_5_factors_2x3.html
- AQR Datasets: https://www.aqr.com/Insights/Datasets

Nur über Websuche (Snippet-/Sekundärebene):
- Jensen/Kelly/Pedersen, Is There a Replication Crisis in Finance? (JF 78(5) 2023): https://nber.org/system/files/working_papers/w28432/w28432.pdf ; Zusammenfassung https://alphaarchitect.com/is-there-a-replication-crisis-in-finance/
- Ehsani/Linnainmaa, Factor Momentum and the Momentum Factor (JF 77(3) 2022): https://www.nber.org/papers/w25551
- Novy-Marx/Velikov, A Taxonomy of Anomalies and Their Trading Costs (RFS 29(1) 2016): https://www.nber.org/papers/w20721 ; https://mysimon.rochester.edu/novy-marx/research/ToAatTC.pdf
- Barroso/Santa-Clara, Momentum Has Its Moments (JFE 2015): https://ciencia.ucp.pt/en/publications/momentum-has-its-moments/ ; Sekundärzusammenfassung https://www.cxoadvisory.com/momentum-investing/avoiding-momentum-strategy-crashes/
- Cederburg/O'Doherty/Wang/Yan, On the Performance of Volatility-Managed Portfolios (JFE 2020): https://www.lehigh.edu/~xuy219/research/COWY.pdf ; https://www.cxoadvisory.com/volatility-effects/does-volatility-management-work-for-equity-factor-portfolios/
- Asness/Chandra/Ilmanen/Israel, Contrarian Factor Timing Is Deceptively Difficult (JPM 2017): https://www.Aqr.Com/Insights/Research/Journal-Article/Contrarian-Factor-Timing-is-Deceptively-Difficult-Supplement ; https://www.cxoadvisory.com/value-premium/valuation-based-factor-timing/
- McLean/Pontiff, Does Academic Research Destroy Stock Return Predictability? (JF 2016): https://www.gwern.net/doc/economics/2016-mclean.pdf ; https://counterpointfunds.com/wp-content/uploads/2017/07/PredictabilityMcleanPontiff.pdf
- Fitzgibbons/Friedman/Pomorski/Serban, Long-Only Style Investing: Don't Just Mix, Integrate (2017): https://www.aqr.com/Insights/Research/White-Papers/Long-Only-Style-Investing ; https://alphaarchitect.com/should-investors-combine-or-separate-their-factor-exposures/
- Linnainmaa/Roberts, The History of the Cross-Section of Stock Returns (RFS 31(7) 2018): https://www.nber.org/papers/w22894 ; https://finance.wharton.upenn.edu/~mrrobert/resources/Publications/anomaliesRFS2017.pdf
- ETF-Auflagedaten (Sekundärquellen): https://www.trackinsight.com/en/fund/BATS:MTUM , https://www.trackinsight.com/en/fund/QUAL , https://robinhood.com/us/en/stocks/USMV/ , https://robinhood.com/us/en/stocks/VLUE/
- Blog-Replikation (nur Windowlänge 126 Tage): https://www.r-bloggers.com/2015/09/hypothesis-driven-development-part-iv-testing-the-barrososanta-clara-rule/

Verwandte Notizen im Projekt: `volmgmt.md` (Vol-Management, überlappt mit 3.2), `xsmom.md` (Querschnitts-Momentum), `lowrisk.md` (Low-Vol/BAB), `valuecarry.md` (Value-Timing über Anlageklassen).
