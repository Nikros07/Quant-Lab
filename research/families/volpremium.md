# Familie: Volatilitaetspraemie / VIX-Termstruktur (VRP, Short-Vol, Put-Writing)

Stand der Recherche: 2026-10-11, Nachlauf ("Erneut versuchen") 2026-10-12. Budget war ca. 15 Web-Abrufe je Lauf. Lauf 1: 6 Websuchen + 9 Seitenabrufe = 15 (davon 2 Abrufe an Zertifikatsfehler gescheitert). Lauf 2 (Nachlauf): 5 Websuchen + 7 Seitenabrufe = 12 (davon 2 gescheitert: EFMA-PDF Zertifikatsfehler, SSRN HTTP 403). Der Nachlauf hat vor allem Luecken aus Lauf 1 geschlossen: Cboe-Seite zu Bondarenko, SFI-Seite zu Zarattini et al., CXO-Zusammenfassung zu Simon-Campasano, Cheng (RFS 2019), Dew-Becker et al. (JFE 2017), Alexander-Korovilas, Eraker-Wu (Abstract). Dazu kamen im Lauf 1 lokale Datenchecks (yfinance auf Yahoo, einige curl-Pruefungen auf dem Cboe-CDN), die keine Recherche, sondern reine Verfuegbarkeitstests sind.
Alle Zahlen stammen aus tatsaechlich gelesenen Seiten/PDFs oder sind als "Suchzusammenfassung", "Sekundaerquelle" bzw. "eigene Messung (deskriptiv)" markiert. Was ich nicht gefunden habe, steht ausdruecklich als "nicht gefunden". Es wurde KEIN Strategie-Backtest gerechnet (Projektregel 3: Hypothese vor Test); gerechnet wurden nur deskriptive Datenfakten (Tickerstart, Tagesverluste, Signalverlauf an Stresstagen).

## 0. Kurzfazit (ehrlich)

- Die Praemie selbst ist gut belegt: Carr-Wu (Arbeitspapier 2004, gelesen) finden fuer S&P 500 und Dow stark negative Varianzrisikopraemien, d.h. wer Varianz verkauft, verdient im Mittel; CAPM und Fama-French erklaeren nur einen kleinen Teil (die Autoren schliessen: entweder ineffizient oder ein eigener, hoch bepreister Risikofaktor). Bollerslev-Tauchen-Zhou (RFS 2009, gelesen) finden, dass IV minus RV Aktienrenditen vorhersagt (Quartalshorizont am staerksten).
- Aber: Die Praemie ist die Entschaedigung fuer Crash- und Vol-of-Vol-Risiko. Das Problem der Familie ist NICHT, ob es eine Praemie gibt, sondern ob man den Tail ueberlebt UND den Rest nach Kosten behaelt. Datenlage Tail (eigene Messung, Yahoo SVXY): Tagesverlust 2018-02-06 -82.96 %, 2018-02-05 -31.99 %; Buy&Hold SVXY vom Hoch 2018-01 (Close 257.74) bis zum Tief 2020-03 (Close 13.14) ca. -95 %. CXO (gelesen) nennt -93 % MaxDD fuer SVXY-B&H 2011-10 bis 2019-12.
- Staerke der Evidenz ist sehr ungleich: Die Praemie (Carr-Wu, BTZ, Eraker-Wu auf Abstract-Ebene) ist akademisch solide; die konkreten ETP-Timing-Regeln (CXO, Zarattini et al. 2025, QuantConnect-Replikation) beruhen auf kurzen Stichproben (2011-2019 bzw. 2008-2025), teils nicht peer-reviewed, teils nur ueber Sekundaerquellen gelesen, und das Produkt hat 2018 sein Exposure gewechselt (-1x auf -0.5x). Simon-Campasano (Basis-Strategie) ist im Original nicht lesbar gewesen und laut Quantpedia out-of-sample leicht negativ.
- Gegenposition / Kritik (Nachlauf, nur Abstract-Ebene gelesen): Dew-Becker/Giglio/Le/Rodriguez (JFE 2017): Investoren in Varianz-Swaps waren ueber einen weiten Bereich von Horizonten (Abstract: 1 Quartal bis 14 Jahre, 1996-2014; Seminarankuendigung nennt 1 Monat) im Wesentlichen indifferent gegenueber Nachrichten ueber kuenftige Varianz; bepreist ist nur der unerwartete, transitorische realisierte Varianzanteil. Das stellt viele strukturelle Erklaerungen der VRP in Frage. Cheng (RFS 2019): die ex-ante VIX-Praemie faellt oder bleibt flach, wenn das Risiko steigt (Hedging-Nachfrage sinkt), und fallende Praemien sagen hoeheres Marktrisiko voraus; das kehrt die naive Logik "mehr Risiko = mehr Praemie" um und stuetzt Ausstiegs-/Umkehrsignale (siehe S2/S3). Alexander/Korovilas (CXO-Zusammenfassung, Stichprobe 2004-2011): Volatilitaets-Diversifikation mit VIX-Futures/ETNs schlug reine Aktienportfolios nur in der Krisen-Teilperiode; kumuliert seit April 2009 etwa -92 % (VXX) und -46 % (VXZ).
- Robustheits-Reihenfolge, die ich vertrete: (1) Put-Writing-Index (kein Produkt-Risiko, kein Hebel, aber Aktien-Beta und Cboe-gesponserte Evidenz), (2) einfacher Termstruktur-Filter auf SVXY (viel NO-TRADE, aber Mini-Stichprobe und Proxy-Abweichung), (3) Dual-Signal nach Zarattini/Aziz/Mele (mehr Parameter, nur Replikation gelesen), (4) VRP als Aktien-Timing-Signal nach BTZ (praktisch kein Tail-Risiko, aber In-Sample-Evidenz und mit Gratis-Daten schwaecher), (5) VIX-Futures-Basis (Simon-Campasano; mit Gratis-Daten nur ab 2013 pruefbar, vermutlich verfallen).
- Interner Zusammenhang mit Quant-Lab: Projektregel 1 (kein erzwungener Trade) passt zu S2/S3, weil dort Cash-Zustaende eingebaut sind. Fly-of-Wallstreet-Befund ("Vol-Overlay brachte nichts") ist ein anderes Thema (Vol-Targeting), ersetzt aber keinen Test dieser Familie.
- Wichtigste Backtest-Fallen: (a) Survivorship: XIV (Credit Suisse, Feb 2018 beendet) fehlt auf Yahoo, SVXY ueberlebte nur durch Leverage-Cut; ein Backtest nur auf SVXY unterschaetzt Ruin-Risiko. (b) Regimebruch SVXY -1x/-0.5x am 2018-02-27/28. (c) Yahoo-VXX startet erst 2018-01-25 (Altserie fehlt). (d) Signal- und Handelszeit: VIX/VIX3M gibt es als Schlusswert, gehandelt wird fruehestens am naechsten Tag; an den Stresstagen entscheidet das ueber -32 % bzw. -83 % (siehe 4.2).
- Die EU-Retail-Handelbarkeit der US-ETPs (KID/PRIIPs-Beschraenkung) und die steuerliche Behandlung von Stillhalterpraemien wurden NICHT recherchiert (Annahme aus Gedaechtnis, nicht geprueft). Vor jeder Umsetzung klaeren (Projektregel 5, Nick entscheidet).

## 1. Abrufstatus (Transparenz)

| Quelle | Status |
|---|---|
| Quantpedia "Exploiting Term Structure of VIX Futures" (quantpedia.com/strategies/exploiting-term-structure-of-vix-futures) | ABGERUFEN, gelesen (Regel, Kostenannahmen, OOS-Hinweis) |
| Simon & Campasano EFMA-2013-PDF (efmaefm.org, alle drei URL-Varianten) | 3x FEHLGESCHLAGEN (Zertifikatsfehler). Das Original-PDF wurde NICHT gelesen. NACHLAUF: CXO-Zusammenfassung (Fassung Juni 2012) https://www.cxoadvisory.com/volatility-effects/timing-and-hedging-the-roll-return-for-vix-futures/ ABGERUFEN und gelesen: Regel, Kosten, Kennzahlen, Vorbehalte (siehe 5.5). Weiterhin Sekundaerquelle. |
| CXO "Timing and Hedging the Roll Return for VIX Futures" (Nachlauf) | ABGERUFEN, gelesen (Sekundaerquelle zu Simon-Campasano) |
| Cboe-Seite zu Bondarenko-White-Paper (Nachlauf) | ABGERUFEN, gelesen (Kennzahlen siehe 5.1); Original-White-Paper NICHT gelesen |
| SFI-Seite zu Zarattini/Aziz/Mele N°25-91 (Nachlauf) | ABGERUFEN, nur Abstract-Seite, keine Regeln; SSRN-Abstract (abstract_id=5316487) HTTP 403, PDF nicht erreicht |
| CXO-Zusammenfassung Alexander & Korovilas 2012 (Nachlauf) | ABGERUFEN, gelesen (Sekundaerquelle, Original-Paper nicht gelesen) |
| arXiv 2103.02016 Avellaneda et al. (Nachlauf) | Abstract-Seite ABGERUFEN; nur qualitative Aussage ("reasonable" OOS-Performance), keine Zahlen, nicht als Strategie uebernommen (Deep-Learning, nicht regelbasiert) |
| IDEAS-Seite Cheng "The VIX Premium", RFS 2019 (Nachlauf) | ABGERUFEN, nur Abstract |
| Suchzusammenfassungen Nachlauf: Dew-Becker et al. JFE 2017; Eraker-Wu JFE 2017 (ideas.repec.org/a/eee/jfinec/v125y2017i1p72-98.html) | NUR Abstract-Ebene aus Suchergebnis, Papers nicht gelesen |
| CXO Advisory "Exploiting VIX Futures Roll Return with ETNs" (Zusammenfassung von "Identifying VXX/SVXY Tendencies", 2020-01-31) | ABGERUFEN, gelesen. Sekundaerquelle (Blog-Zusammenfassung), Original-Studie nicht gelesen; Formulierung der Regel dort selbst widerspruechlich (siehe S2). |
| Concretum-Seite zu Zarattini/Aziz/Mele "The Volatility Edge" | ABGERUFEN: nur Zusammenfassungsseite, Regeln und Details NICHT enthalten. SFI-Working-Paper N°25-91 / RePEc nur als Suchtreffer-Zusammenfassung gesehen, Paper selbst NICHT gelesen. |
| QuantConnect Research Post 21143 (Replikation, nicht peer-reviewed) | ABGERUFEN, gelesen (hier stehen die konkreten Regeln her) |
| Bollerslev/Tauchen/Zhou RFS 2009 (Duke-PDF rfs_09.pdf) | ABGERUFEN (WebFetch lieferte nur Binaer), lokal mit pdftotext gelesen: Abstract, Einleitung, Abschnitt 3.1 (Table 2/4-Text). Tabellen-Zahlenwerte teils nur im Fliesstext verwertet. |
| Carr & Wu (NYU-PDF, Dateiname "...ReviewofFinStudiesMarch2009-a.pdf") | ABGERUFEN, lokal gelesen. ACHTUNG: Der Inhalt ist die Arbeitspapier-Fassung "This version: May 27, 2004", nicht der gedruckte RFS-Text. Zahlen koennen vom Druck abweichen. |
| Eraker & Wu JFE 2017 | NUR Suchzusammenfassung (Abstract-Ebene ueber Spiegelseite), Paper nicht gelesen |
| Bondarenko "Historical Performance of Put-Writing Strategies" (2019) / Cboe-Zusammenfassung | Lauf 1: nur Suchzusammenfassung. Nachlauf: Cboe-Seite abgerufen (siehe 5.1), Original-White-Paper nicht gelesen. Cboe ist Indexsponsor und Auftraggeber: Interessenkonflikt. |
| Israelov & Nielsen "Covered Calls Uncovered" FAJ 2015 | NUR Suchzusammenfassung, Paper nicht gelesen |
| Augustin/Cheng/Van den Bergen FAJ 2021 (CFA-Institute-Seite) | ABGERUFEN, nur die Kurzfassung der Seite gelesen, nicht das Paper |
| Suche zu XIV/SVXY Februar 2018 (Credit Suisse, ProShares) | Suchzusammenfassung; die Zahlen dort variieren je Quelle (siehe 4.2), ich nutze die eigenen Yahoo-Messwerte |
| Dew-Becker et al. "The price of variance risk" u.a. kritische Literatur | NICHT recherchiert (Budget). Das ist eine Luecke bei der Kritik-Seite der Praemie. |

Konsequenz: Fuer S3 (Dual-Signal) ist nur die Replikation, nicht das Paper gelesen; fuer S5 nur Sekundaerquellen. Vor dem Kodieren sollten SFI-PDF (S3) und der Journal-of-Derivatives-Artikel (S5) im Browser geoeffnet werden.

## 2. Gemeinsame Implementierungsregeln

- Signal am Schlusskurs t (VIX, VIX3M, SPY, VX-Settle). Handel fruehestens t+1. Hauptvariante: Fill zum Eroeffnungskurs t+1 (Projektregel 4), Sensitivitaet: Schlusskurs t+1. Die QuantConnect-Replikation handelt dagegen noch am Tag t (Order 16 Minuten vor Schluss) und ist damit optimistischer als das Quant-Lab-Raster.
- Kosten: Eigene Annahme 0.20 % je Positionswechsel in SVXY (entspricht der CXO-Annahme), Sensitivitaet 0.10 % und 0.40 %. Fuer SPY 2 bp einseitig (wie in der Familie volmgmt). Fuer Short-VIXY/Leihegebuehr: im QC-Post keine Annahme (nicht gefunden); fuer Quant-Lab separat ausweisen.
- Pflichtvergleiche (Projektregel 4): (a) Buy&Hold SPY, (b) Buy&Hold der Ziel-Position (z.B. SVXY B&H, ^PUT B&H), (c) Konstant-Mix mit GLEICHER mittlerer Exposure (z.B. W x SVXY + Rest Cash ohne Signal), um Timing-Wert von Hebel/Exposure zu trennen, (d) Teilperioden: SVXY nur 2011-10..2018-02-26 (-1x) und 2018-02-28..heute (-0.5x) getrennt, (e) Stresstage 2018-02-02..08, 2020-02-21..03-18, 2024-08-05, 2016-06-24.
- Ruin-Pflicht: Fuer jede Short-Vol-Variante den maximalen Eintagesverlust der HALTEPOSITION ausweisen und die Gewichtsobergrenze so waehlen, dass ein Tag wie 2018-02-06 (-83 % im -1x-Produkt) das Gesamtkapital um hoechstens ca. 10 % trifft (eigene Faustregel: Gewicht <= 12 % in -1x-Produkten bzw. <= 25 % in -0.5x-Produkten bei Gap-Annahme -50 %/-83 %). Die Ruin-Rechnung gehoert in montecarlo.py (Nick\nemi\nemi\backtest\montecarlo.py), nicht in ein Pandas-Skript.
- Mehrfachtest: Pro Strategie nur 1 vorab festgelegte Hauptparametrierung (Schwellen fest wie unten), Varianten nur als Sensitivitaet, nicht zur Auswahl. Alle Stichproben sind klein (VIX-Regime: nur wenige Krisen); Deflated Sharpe / PBO ist hier wichtig, aber bei <= 4 echten Vol-Schocks (2008, 2018, 2020, 2022/2024) kaum aussagekraeftig. Ehrlich ausweisen: Anzahl unabhaengiger Krisenepisoden in jeder Stichprobe.
- Steuer: Nicht recherchiert. Stillhalterpraemien/Optionen und US-ETPs fuer deutsche Privatanleger separat pruefen (Verlustverrechnungstoepfe).

## 3. Gratis-Daten (eigene Pruefung 2026-10-11, yfinance, Yahoo)

| Zweck | Ticker | Start (erste Zeile) | Bemerkung |
|---|---|---|---|
| Spot-Vol 30 Tage | ^VIX | 1990-01-02 | ok |
| Vol 3 Monate | ^VIX3M | 2006-07-17 | ok, 5091 Beobachtungen bis 2026-10-09 |
| Vol 9 Tage | ^VIX9D | 2011-01-03 | ok |
| Vol 6 Monate | ^VIX6M | 2008-01-02 | ok |
| Vol-of-Vol | ^VVIX | 2007-01-03 | ok |
| Skew | ^SKEW | 1990-01-02 | ok |
| Long-Vol ETP | VIXY | 2011-01-04 | ok |
| Long-Vol ETP | UVXY | 2011-10-04 | 1.5x, Zerfall extrem |
| Long-Vol ETP | VXX | 2018-01-25 | Yahoo hat NUR die neue Serie ab 2018-01-25; die Altserie (ETN 2009-2018) fehlt |
| Short-Vol ETP | SVXY | 2011-10-04 | -1x bis 2018-02-27, danach -0.5x. Close = Adj Close (keine Dividenden) |
| Short-Vol ETP | SVIX | 2022-03-30 | -1x, kurze Historie |
| Short-Vol ETP | XIV | LEER | Credit-Suisse-ETN beendet Feb 2018: Survivorship-Luecke |
| Long-Vol 2x | UVIX | 2022-03-30 | kurz |
| Put-Writing-Index | ^PUT | 1996-08-02 | 7588 Zeilen. Cboe-Quelle nennt Historie ab 1986-06-30 (nicht auf Yahoo). Teile der Pre-2007-Historie sind laut Suchzusammenfassung rueckgerechnet |
| Covered-Call/BuyWrite | ^BXM, ^BXMD, ^WPUT | nur 1 Zeile | im Test unbrauchbar |
| Put-Write-ETF | PUTW | LEER | vermutlich eingestellt (nicht geprueft) |
| Vol-Premium-ETF | SVOL | 2021-05-13 | kurz |
| Aktienmarkt | SPY / ^GSPC | 1993-01-29 / 1985-01-02 | ok |
| Cash | ^IRX oder Ken-French-RF | ^IRX ab 1960er, French-RF taeglich ab 1926 | RF fuer BTZ-Test nutzen |
| VX-Futures (Settle je Verfall) | cdn.cboe.com/data/us/futures/market_statistics/historical_data/VX/VX_YYYY-MM-DD.csv | Verfall 2013-02-13 und spaeter geprueft (HTTP 200: 2013-02-13, 2014-02-19, 2015-02-18, 2018-02-14, 2020-03-18, 2024-01-17); Verfaelle 2008-02-20, 2009-02-18, 2010-02-17, 2011-02-16, 2012-02-22 lieferten HTTP 403 | Spalten: Trade Date, Futures, Open, High, Low, Close, Settle, Change, Total Volume, EFP, Open Interest. Im Verfall 2013-02 steht Settle teils auf 0 (dann Close nehmen). Nutzungsbedingungen von Cboe NICHT geprueft. |

Folge: Die Stichprobe von Simon-Campasano (2006/2007-2011) ist mit Gratis-Daten NICHT reproduzierbar; nur der Zeitraum ab 2013 ist testbar, also genau die Zeit NACH der Publikation.

## 4. Deskriptive Tail-Fakten (eigene Messung, Yahoo, kein Strategie-Backtest)

### 4.1 SVXY (Close-zu-Close)
- Schlechteste Tagesrenditen: 2018-02-06 -82.96 %, 2018-02-05 -31.99 %, 2016-06-24 -26.45 %, 2018-02-08 -22.30 %, 2024-08-05 -21.43 %, 2020-03-16 -19.53 %.
- Buy&Hold-Max-Drawdown der gesamten Reihe 2011-10-04 bis 2026-10-09: ca. -95.2 % (Tief 2020-03-18). Von 257.74 (Hoch im Fenster 2018-01-25..03-15) auf 19.16 (Tief im selben Fenster); 2020-02-14..04-01: Hoch 33.92, Tief 13.14.
- Im -0.5x-Regime (ab 2018-02-28) betrugen die schlechtesten Tage 2024-08-05 -21 % und 2020-03-16 -20 %. Das ist deutlich milder als -83 %, aber fuer ein "Sicherheits"-Portfolio immer noch gross.

### 4.2 VIX / VIX3M (Verhaeltnis der Schlusswerte)
- 2006-07-17 bis 2026-10-09 (5091 Beobachtungen): Anteil Tage mit Verhaeltnis > 1 (Backwardation) = 10.9 %. Maximum 1.43 am 2008-10-24. Groesste Luecke zwischen Beobachtungen 5 Kalendertage.
- Februar 2018: 2018-02-02 Verhaeltnis 1.016 (VIX 17.31, schon > 1), 2018-02-05 1.327 (VIX 37.32), 2018-02-06 1.262, 2018-02-07 1.204, 2018-02-08 1.224. Ein Schluss-Signal "Verhaeltnis >= 1 => Cash" vom 2018-02-02 haette bei Fill am Open 2018-02-05 den Grossteil des -83 %-Tages 2018-02-06 vermieden, NICHT aber vollstaendig den -32 %-Tag 2018-02-05 (genau wie viel am Open vs. Close verloren ging, nicht gemessen). Bei Fill am Close 2018-02-05 waere der volle -32 % getroffen worden. EIN Fall, kein Beleg.
- Maerz 2020: 2020-02-21 Verhaeltnis 0.97, 2020-02-24 1.142 (Signal wechselt, Fill am Open 2020-02-25), danach bis 2020-03-16 durchgehend ueber 1 (1.16 bis 1.34).

## 5. Strategien (nach erwarteter Robustheit)

### 5.1 putwrite_vrp_index - Cash-gedeckter ATM-Put-Verkauf auf S&P 500 (Cboe PutWrite Index)

Regel (Pseudocode):

    DATEN   ^PUT (Yahoo, ab 1996-08-02), SPY, Cash = Ken-French-RF taeglich
    INDEX-LOGIK (Beschreibung laut Suchzusammenfassung der Bondarenko-Arbeit): einmal pro Monat wird ein
      1-Monats-ATM-Put auf den S&P 500 verkauft, die Sicherheit liegt zu 100 % in T-Bills, Halten bis Verfall.
      Handelstag, Uhrzeit und Strike-Wahl des Index: NICHT aus gelesenen Quellen, bei Cboe nachlesen.
    BACKTEST (Index-Ebene, keine Signale)
      w_PUT = 1.0 durchgehend, kein Rebalancing, Rendite = Index-Tagesrendite
      Kostenabzug: c Prozentpunkte p.a., c in {0.25, 0.50, 1.00} (EIGENE Annahme, nicht aus Quelle; Index ist brutto)
    PFLICHTVERGLEICHE
      (a) SPY B&H
      (b) Beta-gematchter Mix: monatlich w_SPY(m) = beta(m-1), beta = expandierende OLS-Steigung der monatlichen
          Excess-Renditen von ^PUT auf SPY (mind. 36 Monate), Rest Cash. Zweck: VRP-Alpha vom Aktien-Beta trennen.
      (c) Teilperioden 1996-2007, 2008-2019, 2020-2026
    REALE UMSETZUNG (nur wenn Freigabe-Tor erreicht): Selbst-Roll mit SPX-/XSP-Put-Optionen, Fill zum
      naechsten realen Kurs, Spread/Slippage ausweisen. Ohne Optionspreis-Daten ist das mit Gratis-Daten NICHT
      backtestbar; der Index-Backtest ist nur die obere Schranke.

- Universum gratis: ^PUT (ab 1996-08-02), SPY (ab 1993-01-29), Ken-French-RF.
- Papers: Bondarenko (2019, nur Cboe-Zusammenfassungsseite gelesen, nicht das Original); Israelov/Nielsen (2015, nur Suchzusammenfassung); Carr/Wu (Praemien-Beleg, gelesen); Eraker/Wu (nur Abstract).
- Behaupteter Effekt (Cboe-Seite zum Bondarenko-White-Paper, im Nachlauf abgerufen): Stichprobe 1986-06-30 bis 2018-12-31; PUT-Index kumuliert +1835 % (PPUT, Put-Kauf-Index: +708 %); annualisierte Volatilitaet PUT 9.95 % vs. S&P 500 14.93 %; Beta 0.56; Schiefe -2.09 (S&P 500: -0.81); monatliches Alpha 0.2 %; hoehere Sharpe-, Sortino- und Stutzer-Masse als die anderen fuenf Vergleichsindizes. NICHT auf der Seite gefunden: annualisierte Rendite, numerische Sharpe-Werte, Max-Drawdown. (Eine Zahl aus Lauf 1, "VIX 19.3 % vs. realisiert 15.1 % im Zeitraum 1990-2018", stammte aus einer Suchzusammenfassung und wurde auf der abgerufenen Seitenfassung nicht bestaetigt; nicht verwenden.) Die Schiefe von -2.09 zeigt, dass die geringere Volatilitaet keine geringere Tail-Gefahr bedeutet. Israelov/Nielsen (Suchzusammenfassung): die Short-Vol-Komponente eines Covered Calls hatte Sharpe nahe 1.0 bei nur ca. 10 % des Risikos; die Aktien-Umkehrkomponente trug ca. 25 % des Risikos fast ohne Rendite.
- Nachpublikation / Kritik: Keine unabhaengige Replikation gefunden (Suchbudget). Die Evidenz ist Cboe-gesponsert; PUT-Historie vor 2007 ist rueckgerechnet; alle Zahlen sind brutto. Die Strategie hat deutliches Aktien-Beta (Groesse in gelesenen Quellen nicht gefunden) und verliert in Crashs; Drawdown-Zahlen fuer ^PUT in 2008 und 2020 nicht gefunden, selbst aus ^PUT messen. Es gibt keinen Timing-Filter, daher keine NO-TRADE-Phasen.
- Tail: kein Produkt-Gap wie bei SVXY, aber voller Aktien-Crash-Verlust abzueglich Praemie; Risiko ist ueberschaubar, weil keine Hebelung.

### 5.2 svxy_term_structure_filter - SVXY nur bei VIX-Contango (VIX < VIX3M), sonst Cash

Regel (Pseudocode):

    PARAMETER THR = 1.00 (fest, nicht optimieren)
              W   = 1.00 (Variante A, wie CXO: 100 % SVXY oder Cash) oder W = 0.25 (Variante B, Portfolio-Baustein; Rest Cash)
              COST = 0.20 % je Wechsel (Annahme aus CXO; Sens. 0.10 %, 0.40 %)
    Am Schlusskurs t:
      ratio_t = VIX_t / VIX3M_t           (^VIX, ^VIX3M; Daten ab 2006-07-17, SVXY ab 2011-10-04)
      ON_t    = (ratio_t < THR)
    Ausfuehrung (Hauptfall): Order nach Schluss t, Fill zum Open t+1.
      Sensitivitaet: Fill zum Close t+1.
    Position fuer Handel an Tag t+1:
      ON_t   und ON_{t-1}      : SVXY halten, Tagesrendite = Close_{t+1}/Close_t - 1
      ON_t   und nicht ON_{t-1}: Einstieg zum Open t+1, Tagesrendite = Close_{t+1}/Open_{t+1} - 1
      nicht ON_t und ON_{t-1}  : Ausstieg zum Open t+1, Tagesrendite = Open_{t+1}/Close_t - 1
      sonst                    : Cash (Rendite 0 oder RF)
      Gewicht in ON-Phasen = W, kein Drift-Rebalancing
    Regime-Bruch: SVXY bis einschliesslich 2018-02-27 -1x, ab 2018-02-28 -0.5x -> Statistiken getrennt ausweisen.
    SEKUNDAER-TEST (EIGENE Ergaenzung, keine Quelle gelesen): dasselbe Signal ON_t steuert SPY statt SVXY
      (SPY wenn ON, sonst Cash), damit Pre-2011-Daten (ab 2006-07-17) nutzbar sind und das Signal ohne ETP-Eigenheiten
      gemessen wird.

- Universum gratis: ^VIX (ab 1990-01-02), ^VIX3M (ab 2006-07-17), SVXY (ab 2011-10-04), SPY.
- Papers: CXO Advisory 2020 (Zusammenfassung von "Identifying VXX/SVXY Tendencies"); Quantpedia-Seite (Termstruktur-Grundidee); Zarattini/Aziz/Mele 2025 (Termstruktur als Teil des Dual-Signals, nur Zusammenfassung gelesen).
- Behaupteter Effekt (CXO, Sekundaerquelle, 2011-10 bis 2019-12): SVXY-Cash netto CAGR 38.0 % vs. SVXY-B&H 14.7 %, MaxDD -58 % vs. -93 %, Tages-Std 3.00 % vs. 4.12 %, 123 Wechsel, Kosten 0.2 % je Wechsel, Cash ohne Zins. Sharpe nicht angegeben. WICHTIG: Das CXO-Signal ist die Rendite der VIX-Futures-Roll (naechster vs. uebernaechster Kontrakt), NICHT VIX/VIX3M. Mein Signal ist ein Gratis-Proxy; die Gleichwertigkeit ist nicht belegt.
- Nachpublikation / Kritik: CXO selbst nennt: wenige VIX-Regime in der Stichprobe, Exposure-Wechsel 2018 verzerrt, wachsendes Handelsvolumen in VIX-ETPs koennte die Timing-Edge zerstoeren, ETPs sind Derivate-Konstrukte mit Emittentenrisiko. Die Variante SVXY-VXX (Long-Vol bei Backwardation) war "nicht verlaesslich attraktiv" (CAGR 13.7 %, MaxDD -83 %). Fuer 2020-2026 habe ich keine Out-of-Sample-Auswertung gefunden.
- Tail: Fill-Verzoegerung entscheidet (siehe 4.2). Gap-Risiko bleibt, wenn das Signal erst NACH dem Schock kippt (z.B. 2024-08-05 war ein Eintagesschock von -21 % im -0.5x-Produkt).

### 5.3 vrp_dual_signal_zarattini - Short-Vol (VRP positiv und Contango) plus SPY-Rest, Long-Vol bei Umkehr

Regel (Pseudocode, nach der QuantConnect-Replikation; die Original-Regeln aus dem SFI-Paper wurden NICHT gelesen):

    DATEN    ^VIX, ^VIX3M, SPY (Close), VIXY (ab 2011-01-04), optional SVXY (ab 2011-10-04)
    Am Schlusskurs t:
      RV_t   = 100 * sqrt(252) * stdev_ddof1( SPY einfache Tagesrenditen der letzten 10 Handelstage inkl. t )
      eVRP_t = VIX_t - RV_t
      CONT_t = (VIX_t < VIX3M_t)
      w_t    = VIX_t / 100
    Zustand:
      eVRP > 0 und CONT        : Vol-Position = -w     (short), SPY-Gewicht = 1 - w
      eVRP < 0 und CONT        : Vol-Position = -0.5*w (short), SPY-Gewicht = 1 - 0.5*w
      eVRP < 0 und nicht CONT  : Vol-Position = +w     (long),  SPY = 0, Rest Cash
      sonst (eVRP > 0 und nicht CONT, oder eVRP = 0): flat, SPY = 0, Rest Cash
    Rebalancing: nur bei Vorzeichenwechsel der Vol-Position oder |Aenderung des Zielgewichts| > 0.02
    Ausfuehrung: Fill zum Open t+1 (Hauptfall; die Replikation handelt MOC am Tag t, optimistischer).
    VARIANTE A (replikationsnah): Vol-Position ueber VIXY, Short-VIXY braucht Leihe (Gebuehr: im Post nicht angegeben).
    VARIANTE B (ohne Leerverkauf, EIGENE Anpassung): s = min(2*w, 0.5), SVXY-Gewicht = s nur in den beiden
      Short-Zustaenden (SVXY ist -0.5x, daher Faktor 2 zur ungefaehren Delta-Aequivalenz zu -w VIXY), SPY = 1 - s,
      Long-Vol-Zustand wird durch Cash ersetzt (CXO: Long-Vol nicht verlaesslich attraktiv).

- Universum gratis: ^VIX, ^VIX3M, SPY, VIXY, SVXY (Starts siehe Abschnitt 3).
- Papers: Zarattini/Aziz/Mele (SFI Research Paper N°25-91, 2025-10-29, SSRN abstract_id=5316487; nur die SFI-Abstract-Seite und die Concretum-Zusammenfassung gelesen, Regeln der vier Stufen NICHT gelesen; SFI-Seite: vier Regelsets von konstantem Short-Vol bis dynamisch skaliert nach Optionsmarkt-Praemie und VIX-Termstrukturneigung, nur VIX-ETNs, Stichprobe 2008-2025); QuantConnect-Replikation (gelesen, nicht peer-reviewed).
- Behaupteter Effekt: Paper (Concretum-Seite/RePEc-Suchzusammenfassung): 2008-2025, finale Version CAGR 16.3 %, Sharpe ca. 1, Korrelation zum Aktienmarkt ca. 15 %, nach "realistischen" Kosten (Zahlen nicht genannt), MaxDD nicht gefunden; kleiner Anteil zum SPY-Portfolio erhoehe die kombinierte Sharpe um ca. 20 %. Replikation: Sharpe 0.729 vs. SPY 0.582 (2016-01 bis 2026-07); Parametergitter 25 Kombinationen (Fenster 6-14 Tage, Schwelle 1-5 %): Sharpe 0.713-0.773, Maximum am Gitterrand; CAGR/MaxDD nicht gefunden; Kosten nicht gefunden.
- Nachpublikation / Kritik (nur aus den gelesenen Seiten): Der Replikations-Autor nennt den RV-Schaetzer als grob. Ein Forumskommentar (nicht vom Autor) sagt, der SPY-Overlay stehe nicht im Paper (dort Cash) und erkläre einen grossen Teil der Rendite; ein statischer Short in VIXY sei nicht gleich einem -1x-Produkt (Exposure schrumpft bei Gewinnen); Realvol der Replikation ca. 12 % vs. 16.4 % im Paper. Das Paper ist von Oktober 2025 (SFI) bzw. Juni 2025 (CXO-Datum): echte Out-of-Sample-Zeit seit Veroeffentlichung gibt es praktisch nicht.
- Tail: Short-Position wird bei steigender VIX groesser (w = VIX/100); das bedeutet in schnellen Schocks mehr Exposure, wenn die Signale zu spaet kippen. Deshalb Variante B mit Deckel.

### 5.4 vrp_equity_timing_btz - Aktien nur bei hoher Varianzpraemie, sonst Cash (BTZ-Signal)

Regel (Pseudocode):

    DATEN   ^VIX (ab 1990-01-02), ^GSPC-Tagesrenditen fuer RV, Handelsobjekt SPY bzw. fuer lange Historie
            Ken-French "Mkt" = Mkt-RF + RF taeglich (Dataset F-F_Research_Data_Factors_daily), Cash = RF
    Am letzten Handelstag t jedes Monats (Schlusskurs):
      IV_t  = VIX_t^2 / 12                                      (monatliche Varianz, Einheit %-Punkte^2)
      RV_t  = Summe ueber die letzten 21 Handelstage von (100*ln(P_i / P_{i-1}))^2   (^GSPC)
      VRP_t = IV_t - RV_t
      ON_t  = VRP_t > Median( VRP_s fuer alle Monatsenden s <= t ), mind. 60 Monate Vorlauf (erstes Signal 1995-01)
    Naechster Monat: ON -> 100 % Aktienmarkt (SPY bzw. French-Mkt), OFF -> 100 % Cash (RF)
    Ausfuehrung: Order nach Schluss t, Fill zum Open des ersten Handelstags nach t (Sens. Close).
    Kosten: 2 bp einseitig auf Gewichtsaenderung.
    Auswertung: 1995-2007 (Paper-Zeitraum, In-Sample-nah) und 2008-2026 (echtes Out-of-Sample) GETRENNT.

- Universum gratis: ^VIX, ^GSPC/SPY, Ken-French-Daily-Faktoren (Aktienmarkt und RF, ab 1926).
- Papers: Bollerslev/Tauchen/Zhou (2009, gelesen); Carr/Wu (Fassung 2004, gelesen, als Praemien-Beleg).
- Behaupteter Effekt (BTZ, gelesen): Stichprobe 1990-01 bis 2007-12, monatlich. Regression der Aktienrenditen auf IV minus RV: Monatshorizont R2 knapp ueber 1 %; Quartalshorizont R2 6.82 % bei t = 2.86 (modellfreie IV, hochfrequente RV), Maximum bei ca. einem Quartal, danach abnehmend. Entscheidend fuer den Gratis-Proxy: Die Autoren schreiben, die Ergebnisse haengen "crucially" an modellfreier IV und hochfrequenter RV. Mit modellfreier IV (entspricht dem neuen VIX) und taeglicher RV: R2 4.45 % (t = 2.34, Quartal); mit Black-Scholes-IV und taeglicher RV: R2 2.16 % (t = 1.72); mit BS-IV und hochfrequenter RV: R2 3.30 % (t = 1.85). Mein Proxy (VIX + RV aus Tagesdaten) entspricht der Variante mit 4.45 %.
- Nachpublikation / Kritik: Diese R2-Werte sind In-Sample, ueberlappende Quartalsrenditen, kleine Stichprobe (die Autoren warnen selbst, dass Inferenz mit ueberlappenden Daten und wenigen Jahren vorsichtig zu lesen ist). Out-of-Sample-Studien habe ich NICHT gefunden. Ich erwarte, dass das Signal als reine Timing-Regel schwach ist (R2 von 4-7 % ist als Handelsregel mit Cash-Zustaenden nicht zwingend gewinnbringend). Der Wert dieser Strategie ist vor allem ein ehrlicher Out-of-Sample-Test der bekanntesten VRP-Behauptung.
- Tail: praktisch das Aktienmarkt-Risiko in ON-Phasen; keine Produktrisiken, keine Hebel.

### 5.5 vix_basis_simon_campasano - hedged VIX-Futures-Basis (Contango short / Backwardation long)

Regel (Pseudocode; Regel aus Quantpedia, Original nicht lesbar gewesen):

    DATEN   VX-Settle je Verfall (Cboe-CDN, ab Verfall 2013-02-13 geprueft), ^VIX Spot, SPY als Hedge-Proxy (Paper: E-mini S&P 500)
    Am Schlusskurs t (taeglich):
      F1_t  = Settle (wenn Settle = 0: Close) des naechsten VX-Kontrakts mit mind. 10 Handelstagen bis Verfall
      n_t   = Anzahl Handelstage bis Verfall von F1_t
      roll_t = (F1_t - VIX_t) / n_t            (taegliche Roll in Indexpunkten)
      roll_t >  +0.10 : SHORT 1 Einheit F1_t
      roll_t <  -0.10 : LONG  1 Einheit F1_t
      sonst           : keine neue Position
      Jede Einheit wird 5 Handelstage gehalten und dann glattgestellt. Jede Tag-Tranche = 1/5 des Risikokapitals
      (EIGENE Annahme zur Behandlung ueberlappender Positionen; in den gelesenen Quellen nicht beschrieben).
    Hedge: SPY-Gegenposition so, dass das S&P-Beta der VX-Position null ist: h = OLS-Steigung von (Aenderung F1)
      auf SPY-Tagesrendite ueber die letzten 60 Handelstage, am Einstiegstag bestimmt und waehrend der 5 Haltetage
      FIXIERT (CXO: Verhaeltnis aus historischen Regressionen, je Trade fix, im Schnitt ca. 1 E-mini je VIX-Kontrakt,
      Spanne ca. 0.5 bis 2; die Fensterlaenge von 60 Tagen ist EIGENE Annahme, in der Quelle nicht gefunden).
      Keine Stop-Loss/Take-Gain-Regeln (CXO: verschlechterten das Ergebnis).
    Ausfuehrung: Quant-Lab-Hauptfall Fill zu Settle t+1 (VX hat keinen verlaesslichen Open); Paper-nah: Settle t (optimistisch).
    Kosten (Paper laut Quantpedia): volle quotierte VX-Bid-Ask-Spreads, halber Tick je E-mini-Seite, 3 USD Round-Turn
      Brokerage je Kontrakt, durchschnittlich ca. 140 USD je Round-Turn-Trade (Quantpedia). Die CXO-Zusammenfassung nennt
      3 USD je VX-Kontrakt, 12.50 USD je E-mini und "grob 60 USD je kompletten Trade" -> die beiden Sekundaerquellen
      widersprechen sich; im Quant-Lab konservativ die hoehere Zahl (140 USD) plus Sensitivitaet nehmen.

- Universum gratis: VX-Dateien Cboe-CDN (ab ca. 2013), ^VIX, SPY. Original-Zeitraum (2006/07-2011) mit Gratis-Daten NICHT pruefbar.
- Papers: Simon & Campasano, "The VIX Futures Basis: Evidence and Trading Strategies", Journal of Derivatives 21(3), 2014 (Original nicht gelesen); Eraker & Wu JFE 2017 (nur Abstract); Augustin/Cheng/Van den Bergen FAJ 2021 (Tail-Kontext).
- Behaupteter Effekt (CXO-Zusammenfassung der Fassung Juni 2012, im Nachlauf gelesen; Original nicht gelesen): Stichprobe 2006-2011; abgesichert (E-mini-Hedge) im Mittel Netto-Gewinn je Kontrakt Short-Trades 539 USD (Sortino 0.75), Long-Trades 908 USD (Sortino 0.53); kumulierter Endgewinn ca. 82000 USD ohne schwere Drawdowns. Die Jahresrendite haengt voellig an der Margin-Annahme: 53 % p.a. bei Margin 6900 USD je VIX-Kontrakt und 4375 USD je E-mini; nur 20 % p.a. bei Eigenkapital = 5x Mindestmargin. Sharpe und Max-Drawdown stehen nicht auf der Seite. Die frueher genannte Quantpedia-Zahl 19.67 % ist eine indikative Quantpedia-Ableitung und wird nicht uebernommen. Abstract-Aussage: Basis sagt VIX-Futures-Preisaenderungen voraus, nicht den Spot (2006-2011).
- Vorbehalte laut CXO-Zusammenfassung (gelesen): 5 Jahre sind kurz; ca. die Haelfte des Gewinns fiel in die Finanzkrise 2008; "seit Mitte 2010 kaum oder kein Gewinn". Stop-Loss- und Take-Gain-Regeln verschlechterten das Ergebnis; dynamischer Ausstieg half nur der Long-Seite.
- Nachpublikation / Kritik: Quantpedia vermerkt, der Out-of-Sample-Backtest sei leicht negativ (Alpha vermutlich verfallen), Vertrauen "Moderate". Nur die Long-VIX-Haelfte kann Aktien-Crashs teilweise absichern; die Short-Haelfte ist keine Absicherung. Eraker-Wu (Abstract): konstante 1-Monats-VIX-Futures-Position verlor 2006-2013 ca. 30 % p.a., das zeigt die Groesse der Praemie in genau der Phase, in der die Strategie getestet wurde, die Stichprobe war aber auch Krisen-/Hochvol-lastig und ist nicht repraesentativ fuer spaetere Jahre.
- Komplexitaet hoch (Kontrakt-Roll, Hedge, Margin). Fuer Quant-Lab: erst nach S1-S4 und nur als Test "funktioniert nach Publikation noch?" auf 2013-2026.

## 6. Papers-Uebersicht (nur Quellen, die ich tatsaechlich aufgerufen habe)

- Bollerslev, Tauchen, Zhou (2009), Expected Stock Returns and Variance Risk Premia, Review of Financial Studies 22(11). https://public.econ.duke.edu/~boller/Published_Papers/rfs_09.pdf (gelesen)
- Carr, Wu (2009; gelesene Fassung Arbeitspapier Mai 2004), Variance Risk Premia, Review of Financial Studies. https://engineering.nyu.edu/sites/default/files/2019-01/CarrReviewofFinStudiesMarch2009-a.pdf (gelesen; Fassung 2004)
- Simon, Campasano (2014), The VIX Futures Basis: Evidence and Trading Strategies, Journal of Derivatives 21(3). Gelesen nur ueber https://quantpedia.com/strategies/exploiting-term-structure-of-vix-futures ; Original-PDF https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2013-Reading/papers/EFMA2013_0164_fullpaper.pdf nicht abrufbar (Zertifikatsfehler)
- CXO Advisory (2020-01-31, LeCompte), Zusammenfassung von "Identifying VXX/SVXY Tendencies". https://www.cxoadvisory.com/volatility-effects/exploiting-vix-futures-roll-return-with-etns/ (gelesen)
- Zarattini, Aziz, Mele (2025), The Volatility Edge: A Dual Approach for VIX ETNs Trading, SFI Research Paper N°25-91. https://www.sfi.ch/en/publications/n-25-91-the-volatility-edge-a-dual-approach-for-vix-etns-trading ; Zusammenfassung gelesen auf https://concretumgroup.com/the-volatility-edge-a-dual-approach-for-vix-etns-trading/ ; Paper selbst nicht gelesen
- QuantConnect Research 21143, Harvesting the Volatility Risk Premium with a Dual VIX Signal (Replikation, nicht peer-reviewed). https://www.quantconnect.com/research/21143/harvesting-the-volatility-risk-premium-with-a-dual-vix-signal/ (gelesen)
- Eraker, Wu (2017), Explaining the negative returns to volatility claims: An equilibrium approach, Journal of Financial Economics 125(1), 72-98. https://ideas.repec.org/a/eee/jfinec/v125y2017i1p72-98.html ; https://academicnewsletter.sufe.edu.cn/info/356257 (nur Abstract-Ebene ueber Suchzusammenfassung)
- Cheng (2019), The VIX Premium, Review of Financial Studies 32(1), 180-227. https://ideas.repec.org/a/oup/rfinst/v32y2019i1p180-227..html (Abstract gelesen, Paper nicht)
- Dew-Becker, Giglio, Le, Rodriguez (2017), The price of variance risk, Journal of Financial Economics 123(2), 225-250 (NBER WP 21182). https://ideas.repec.org:443/a/eee/jfinec/v123y2017i2p225-250.html ; https://www.nber.org/papers/21182 (nur Abstract-Ebene aus Suchergebnis)
- Alexander, Korovilas (2012), Diversification of Equity with VIX Futures: Personal Views and Skewness Preference; gelesen nur die CXO-Zusammenfassung https://www.cxoadvisory.com/volatility-effects/diversification-with-vix-futures-and-related-etns
- CXO Advisory (2012), Zusammenfassung von Simon & Campasano. https://www.cxoadvisory.com/volatility-effects/timing-and-hedging-the-roll-return-for-vix-futures/ (gelesen)
- Avellaneda, Li, Papanicolaou, Wang (2021), Trading Signals In VIX Futures, arXiv:2103.02016 (nur Abstract-Seite gelesen, Deep-Learning-Ansatz, nicht als Strategie uebernommen)
- Bondarenko (2019), Historical Performance of Put-Writing Strategies; Cboe-Zusammenfassung: https://www.cboe.com/insights/posts/white-paper-shows-volatility-risk-premium-facilitated-higher-risk-adjusted-returns-for-put-index/ (nur Suchzusammenfassung)
- Israelov, Nielsen (2015), Covered Calls Uncovered, Financial Analysts Journal 71(6), 44-57. https://ideas.repec.org/a/taf/ufajxx/v71y2015i6p44-57.html ; https://quantpedia.com/covered-calls-uncovered/ (nur Suchzusammenfassung)
- Augustin, Cheng, Van den Bergen (2021), Volmageddon and the Failure of Short Volatility Products, Financial Analysts Journal. https://rpc.cfainstitute.org/research/financial-analysts-journal/2021/volmageddon-failure-short-volatility-products (CFA-Seite gelesen). Befund: Am 2018-02-05 verloren Short-Vol-ETPs ueber 90 %; Mechanismus laut Autoren: Rebalancing-Zukaeufe von VIX-Futures verstaerkten den Anstieg (Rueckkopplung).

Weitere Suchtreffer, die ich NICHT als Paper fuehre (nur Hinweise): Vaasa- und Aalto-Abschlussarbeiten zur VIX-Termstruktur (osuva.uwasa.fi, aaltodoc.aalto.fi; Aussage in Suchzusammenfassung: Short-VIX-Carry in ruhigen Phasen am besten, Instabilitaet der Termstruktur macht den Carry-Trade riskant), Substack-Beitraege (tradingvolatility, harbourfrontquant), Option-Strategist-Artikel zur Credit-Suisse-Beendigung von XIV, Alpha Architect "covered-calls". Whaley und Bondarenko 2014 ("Why Are Put Options So Expensive?") wurden NICHT abgerufen. Alexander/Korovilas (nur CXO-Zusammenfassung), Dew-Becker et al. und Cheng (nur Abstract-Ebene) wurden im Nachlauf angesehen, siehe oben.

## 7. Offene Punkte / vor dem Kodieren

1. Hypothesen in docs/HYPOTHESEN.md eintragen (Erwartung + Abbruchkriterium) BEVOR irgendein Backtest laeuft. Vorschlag Abbruchkriterium S2: Sharpe nach Kosten unter SPY-B&H im Zeitraum 2018-02-28..heute, ODER MaxDD der Strategie > -35 % bei W = 0.25.
2. SFI-Paper N°25-91 im Browser oeffnen (Regeln der vier Stufen, Instrumente, Kostenannahmen; SSRN lieferte 403, SFI-Seite verlinkt kein PDF), Simon-Campasano-Original besorgen (EFMA-PDF Zertifikatsfehler, DOI 10.3905/jod.2014.21.3.054); beides konnte ich auch im Nachlauf nicht im Original lesen.
2b. Cheng (RFS 2019) im Volltext lesen: moegliche Hypothese "fallende ex-ante VIX-Praemie => raus aus Short-Vol" als eigene Regel; im Nachlauf nur Abstract, daher keine Regel daraus formuliert (Regel 3: Hypothese vor Test, und eine Regel ohne gelesene Definition der Praemie waere erfunden).
3. Cboe-Nutzungsbedingungen fuer VX-Daten und PUT-Index-Methodik pruefen.
4. Handelbarkeit/Steuer fuer Nick (EU-Retail, US-ETPs, Optionen) klaeren, bevor Aufwand in S3 Variante A (Short-Leihe) oder echtes Put-Writing fliesst.
5. Kritische Literatur im Volltext nachziehen (Dew-Becker et al. und Cheng nur auf Abstract-Ebene gesehen; Whaley nicht gesehen), um die Gegenposition zur Praemie zu pruefen.
