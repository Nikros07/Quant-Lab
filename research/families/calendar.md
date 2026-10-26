# Familie: Saisonalität / Kalendereffekte / Event-Drift

Stand der Recherche: 2026-10-11. Budget: 15 Web-Abrufe (WebSearch + WebFetch), davon 2 gescheitert (404, 403). Zusätzlich wurde ein per WebFetch gespeichertes NBER-PDF lokal mit pdftotext gelesen (kein weiterer Web-Abruf).
Kennzeichnung der Belegstärke in diesem Dokument:
- **[GELESEN]** = Seite/PDF wurde abgerufen und der Text gesehen.
- **[SNIPPET]** = nur Zusammenfassung aus einem Suchergebnis gesehen, Quelle selbst NICHT abgerufen. Zahlen daraus sind unverifiziert.
- **[GEDÄCHTNIS]** = aus meinem Wissen, in dieser Sitzung nicht geprüft (betrifft vor allem Ticker-Datenstarts und Dateinamen). Vor Nutzung prüfen.
Was ich nicht gefunden habe, steht ausdrücklich als "nicht gefunden".

## 0. Kurzfazit (ehrlich)

- Die Familie liefert **keinen soliden Stand-alone-Edge**. Sie liefert (a) zwei billige, gut dokumentierte Expositions-Überlagerungen mit offener Frage nach Alpha vs. reiner Risikoreduktion (Turn-of-the-Month, Halloween), (b) eine Querschnitts-Saisonalität (Heston-Sadka/Keloharju et al.), die auf Papier stark ist, aber Long-Short braucht und in der jüngsten Teilperiode schwächer wird, und (c) zwei Einträge, die nach Veröffentlichung/Kosten **nicht mehr funktionieren bzw. nicht nachweisbar sind** (Pre-FOMC-Drift, Overnight-Drift). Zusätzlich: Wochenend-/Wochentagseffekt ist nach dem Stand der Literatur tot (siehe Abschnitt 5).
- Alle Kalender-Signale sind **im Voraus bekannt** (Kalender statt Preis). Das macht Look-ahead-Fehler leicht vermeidbar, schafft aber ein anderes Risiko: Das Fenster wird nach dem Backtest gewählt (Fenster-Mining). Deshalb im Test immer: Exposure-gematchte Zufallsfenster als Nullverteilung, nicht nur Buy&Hold.
- Alle Einträge sind **Long-Aktien-Beta zu bestimmten Tagen**. Sie sind untereinander und mit Buy&Hold stark korreliert, wenn sie investiert sind. Fünf Strategien testen heißt nicht fünf unabhängige Edges.
- Die Stichprobengröße ist bei Ereignisstrategien winzig (FOMC: 8 Termine/Jahr, Halloween: 1 Wechsel/Jahr). Statistische Evidenz braucht Jahrzehnte. Das ist das eigentliche Problem dieser Familie, nicht die Rechenarbeit.
- Praktisch für Deutschland: SPY/QQQ sind für Kleinanleger in der EU typischerweise nicht kaufbar (PRIIPs/KID). Für den Live-Betrieb bräuchte man ein UCITS-Äquivalent (Ticker, Datenstart, Spread vor Nutzung prüfen). Backtests laufen mit SPY/French-Daten. Abgeltungssteuer (25 % + 5,5 % Soli) wird bei jedem Wechsel sofort fällig (keine Steuerstundung wie bei Buy&Hold) – das trifft TOM (12 Zyklen/Jahr) am stärksten, Halloween (1 Zyklus/Jahr) kaum.

## 1. Abrufstatus (Transparenz)

| Quelle | Status |
|---|---|
| NY Fed Staff Report 512, Lucca-Moench "The pre-FOMC announcement drift" (fedinprint.org/item/fednsr/12655) | ABGERUFEN, nur Abstract |
| R-Bloggers / Return and Risk "Update on The Pre-FOMC Announcement Drift" (2015) | ABGERUFEN, Zahlen im Text |
| Quantpedia "Turn of the Month in Equity Indexes" | ABGERUFEN (Sekundärquelle über McConnell-Xu) |
| CXO Advisory "The Turn-of-the-Month Effect" (2006) | ABGERUFEN (Sekundärquelle über McConnell-Xu-Draft) |
| NBER WP 20815 Keloharju-Linnainmaa-Nyberg "Common Factors in Return Seasonalities" (Dez. 2014) | PDF abgerufen und lokal komplett per pdftotext gelesen; Tabellen teils verschoben |
| Kurov-Wolfe-Gilbert, Skidmore-PDF | 404, NICHT abrufbar; nur Suchsnippet |
| Alpha Architect "Trading costs wipe out the overnight return anomaly" | 403, NICHT abrufbar; nur Suchsnippet |
| Halloween (Bouman-Jacobsen, Zhang-Jacobsen), Maberly-Waggoner, JFP-2011-TOM, Robins-Smith, Schwert, Cieslak et al., Hendershott et al., Lou-Polk-Skouras, Cliff-Cooper-Gulen | NUR Suchsnippets (siehe jeweilige Abschnitte) |
| Nicht konsultiert (Budget): AQR, Hoffstein/Newfound, Allocate Smartly, Ken-French-Seite selbst, Shiller-Seite | nicht abgerufen |

Konsequenz: Vor dem Kodieren sollten die Originalpapers (SSRN/NBER) für TOM, Halloween, FOMC und die Overnight-Papiere im Browser geöffnet und die Fensterdefinitionen gegen die Regeln unten abgeglichen werden. Die Regeln hier sind so präzise wie möglich, aber teils aus Sekundärquellen rekonstruiert (siehe pro Strategie).

## 2. Gemeinsame Implementierungsregeln

- Kalender-Signale (TOM, Halloween, FOMC-Termine, Industrie-Saisonalität aus Jahre-alten Daten) sind bei Handelsentscheidung bereits bekannt. Deshalb ist eine Order "Market-on-Close am Tag X" ohne Look-ahead zulässig, auch wenn die Regel "Signal am Schlusskurs t, Handel am nächsten Handelstag" formal enger ist. Zur Sicherheit gilt in jedem Test zusätzlich die **konservative Variante: Ausführung zum Open des Folgetags** (verliert die Overnight-Lücke, was bei Kalendereffekten teils den Kern der Rendite ausmacht – das ist selbst ein Befund).
- Kosten testen mit 1, 2, 5 bps einseitig (SPY) plus Aufschlag für MOC/MOO-Abweichung. Steuer separat im Steuermodul.
- Benchmarks (Pflicht): Buy&Hold desselben Instruments; **exposure-gematchtes Zufalls-Fenster** (gleiche Zahl Tage, 10 000 zufällig platzierte Fenster, Quantil der Strategie in dieser Verteilung); **konstanter Mischanteil** (z. B. 19 % Aktien / 81 % Cash für TOM) als Vergleich mit gleicher Marktexposure; Cash (RF).
- Mehrfachtest: Pro Strategie ist die Hauptvariante vorab festgelegt (unten). Alle Varianten (konservative Ausführung, andere Kostenannahmen, Teilperioden) werden als Sensitivität berichtet, NICHT zur Auswahl benutzt. Die Zahl der probierten Varianten geht in Deflated Sharpe / PBO ein.
- Echte Out-of-Sample-Aufteilung: Jede Strategie hat ein "Publikationsende" (letztes Jahr der Original-Stichprobe). Alles danach ist die einzig ehrliche OOS-Prüfung. Die Papers enden: TOM 2005, Lucca-Moench 03/2011, Keloharju et al. 2011, Bouman-Jacobsen 1998.

### Gratis-Daten (Datenstarts [GEDÄCHTNIS], vor Nutzung mit yfinance/pandas_datareader prüfen)

- **Ken French Data Library** (Dartmouth): `F-F_Research_Data_Factors_daily` (Mkt-RF, SMB, HML, RF, täglich ab 1926-07-01), `F-F_Research_Data_Factors` (monatlich ab 1926-07), `17_Industry_Portfolios` und `49_Industry_Portfolios` (monatlich, value- und equal-weighted, ab 1926-07), jeweils auch `_daily`. Abruf z. B. mit `pandas_datareader.data.DataReader(name, 'famafrench')`. Dateinamen aus dem Gedächtnis. Hinweis: French-Daten kommen mit Verzögerung von Wochen; für Industrie-Saisonalität spielt das keine Rolle, weil die Signale nur Daten von t-12 Monaten und älter nutzen.
- **Yahoo**: ^GSPC (ab 1927-12-30, nur Kursindex, Open vor den 1980ern unzuverlässig), ^SP500TR (Total Return, ab ca. 1988-01-04), SPY (ab 1993-01-29, mit `auto_adjust=True`), ^DJI (ab 1992 bei Yahoo; ältere Reihe nicht gesichert), ^GDAXI (ab 1987-12-30), ^FTSE (ab 1984-04-02), SHY (ab 2002-07), BIL (ab 2007-05), ^IRX (13-Wochen-Zins, ab 1960). Länder-ETFs iShares (EWA, EWC, EWG, EWH, EWI, EWJ, EWK, EWL, EWN, EWO, EWP, EWQ, EWS, EWU u. a.): ab 1996-03.
- **Shiller** (Yale): Monatsreihe S&P Composite ab 1871 (Preise sind Monatsdurchschnitte der Tagesschlusskurse [GEDÄCHTNIS] – glättet und verzerrt Fenstergrenzen; für Halloween nur grob nutzbar).
- **Fed**: Termine der FOMC-Sitzungen (federalreserve.gov, historische Kalender) – gratis, aber nicht in yfinance; müssen einmal in eine CSV übernommen und geprüft werden (geplant vs. außerplanmäßig).

## 3. Strategien (nach erwarteter Robustheit sortiert)

### 3.1 tom_spy_m2_p3 – Turn of the Month (McConnell-Xu), Handelstage -1 bis +3

**Regel (Hauptvariante):**
```
Handelstage-Kalender aus den Marktdaten (NYSE-Tage, die in den Daten vorkommen).
Für jeden Monat M:
  d(-1)  = letzter Handelstag von M
  d(-2)  = vorletzter Handelstag von M
  d(+3)  = dritter Handelstag von M+1
Position:
  Long 100 % Index/ETF vom Close(d(-2)) bis Close(d(+3))   -> erfasst die Tagesrenditen der Tage -1,+1,+2,+3
  sonst 100 % Cash (RF / SHY / BIL)
Order: MOC an d(-2) (Kalender im Voraus bekannt), Exit MOC an d(+3).
Sensitivitäten (nicht zur Auswahl): Entry Open(d(-1)); Exit Open(d(+4)); Fenster nur Tag +1 (siehe Verfall);
  Kosten 1/2/5 bps einseitig.
```
Die Definition "letzter Handelstag bis dritter Handelstag des Folgemonats, vier Tage" stammt aus CXO [GELESEN] und Quantpedia [GELESEN]. Quantpedia formuliert den Einstieg als "einen Handelstag vor Monatsende" und nennt Varianten mit vier Tagen; die Zuordnung zu "Close(d(-2))" ist meine Operationalisierung (die Rendite von Tag -1 beginnt am Close von Tag -2). Vor dem Kodieren am Original (McConnell-Xu, FAJ 64(2), 2008) bestätigen.

**Daten:** Primär Ken French `F-F_Research_Data_Factors_daily` (Mkt = Mkt-RF + RF, 1926-07-01 bis heute, breiter US-Markt, kostenfrei), sekundär SPY (1993-01-29) bzw. ^SP500TR (ca. 1988) für die ETF-Ära. Publikationsende = 2005; OOS = 2006 bis heute.

**Belege:**
- McConnell-Xu [GELESEN, Sekundärquellen]: US-Tagesdaten 1926-2005, Fokus 1987-2005 (CXO). Wertgewichtet 0,14 % pro TOM-Tag vs. -0,01 % an den übrigen 16 Tagen; gleichgewichtet 0,24 % vs. 0,04 %. Effekt in 30 von 34 weiteren Ländern (CXO) bzw. 31 von 35 Ländern (Quantpedia/Abstract). Keine Erklärung durch Zahltag, Risiko, Volumen oder Fondszuflüsse (CXO). Quantpedia: Strategie (-1,+3), 1926-2005, indikativ 7,2 % p.a., Vol ca. 6,9 %, Sharpe 1,04, Max-DD -20,79 %, Tagesmittel 0,15 % vs. 0,01 %, t = 7,81; Kosten "not reported". Die Umrechnung von Tagesmittel auf 7,2 % p.a. ist auf der Quantpedia-Seite nicht erklärt; Zahlen daher nur als Orientierung.
- Quantpedia nennt Carchano-Tornero: TOM sei der einzige Kalendereffekt in S&P-500-Futures (1991-2008), der signifikant und persistent war [Sekundärangabe, Paper nicht gesehen].

**Verfall / Gegenevidenz:**
- Maberly-Waggoner (Atlanta Fed WP 2000-11) [SNIPPET]: TOM-Effekt in S&P-500-Futures verschwinde nach 1990, gelte auch für den Kassamarkt; Erklärung: Verlagerung von Direktbesitz zu Fonds.
- Journal of Financial Planning 2011 "The Turn-of-the-Month Anomaly in the Age of ETFs" [SNIPPET]: in der ETF-Ära konzentriere sich der Effekt im S&P 500 auf den ERSTEN Handelstag des Monats; Kunkel/Compton/Beyer (2003) fänden nur am Tag 1 (08/1988-07/2000) eine signifikant positive Rendite. Das widerspricht McConnell-Xu (positive Renditen an allen vier Tagen).
- Direkter Out-of-Sample-Test von McConnell-Xu nach 2005 mit CRSP: NICHT gefunden.
- Eine Konferenzfolie 2022 (Choi/Hong/Lou/Mukherjee, 401(k)-Daten 2000-2012) [SNIPPET, abgeschnitten] deutet an, dass der Effekt in 401(k)-Zuflüssen noch sichtbar ist – Details nicht lesbar.

**Kosten / Praxis:** 12 Round-Trips pro Jahr. SPY-Spread ca. 1 bp, realistisch 2-4 bps pro Round-Trip inkl. MOC-Slippage, also ca. 0,3-0,5 % p.a. Bei nur ca. 19 % Marktexposure (4 von ca. 21 Tagen) ist die absolute Rendite klein; ein höheres Sharpe-Verhältnis als Buy&Hold entsteht teils nur durch die geringe Exposure. Test gegen konstanten 19/81-Mix und gegen exposure-gematchte Zufallsfenster ist Pflicht. Steuer: 12 Realisierungen/Jahr ohne Steuerstundung.

**Tail-Risiko:** Long-only Aktienrisiko für 4 Tage, kein Crash-Schutz. Gap-Risiko (Overnight) steckt voll im Fenster. Positiv: Cash für 17 Tage reduziert Gesamtdrawdown. Negativ: Cash verpasst auch die positive Drift der übrigen Tage.

**Vorab-Hypothese (Vorschlag für HYPOTHESEN.md):** Erwartung: positive Tagesrendite-Differenz auch nach 2005, aber deutlich kleiner als 0,15 %/Tag; Abbruch, wenn nach 2006 der Tagesmittel-Unterschied (TOM minus Rest) in Newey-West-t < 1,5 liegt UND der Fenster-Rang gegen Zufallsfenster unter dem 90. Perzentil.

### 3.2 halloween_nov_apr_equity – Halloween / Sell in May (Bouman-Jacobsen)

**Regel (Hauptvariante):**
```
Jedes Jahr Y:
  Entry: Close des letzten Handelstags im Oktober (Y) -> 100 % Aktienindex/ETF
  Exit : Close des letzten Handelstags im April (Y+1) -> 100 % Cash (RF / SHY / BIL), bis zum Entry im Oktober
Jahre 1 Wechsel hin, 1 Wechsel zurück. Order MOC (Kalender im Voraus bekannt).
Sensitivität: Open des Folgetags; Cash statt T-Bill = IEF (Bond-Variante); Kosten 1/2/5 bps.
```
Fenster = Nov bis Apr ("Winter"), Mai bis Okt ("Sommer"). Die exakte Fenstergrenze ist über Suchsnippets bestätigt ("Winter = November bis April"); Grenze am Monatsendschluss ist meine Operationalisierung.

**Daten:** French `F-F_Research_Data_Factors` monatlich (Mkt-RF + RF, 1926-07 bis heute; Monatsdaten reichen, da das Signal monatsgenau ist), tägliche Variante `_daily`. ETF-Ära: SPY (1993), Cash: BIL/SHY. International (Replikationsidee): ^GDAXI (1987-12), ^FTSE (1984-04), ^N225, Länder-ETFs ab 1996. Pre-Sample-Check (vor 1926): Shiller-Monatsreihe, Einschränkung Monatsdurchschnitte. Publikationsende = 1998 (Bouman-Jacobsen-Stichprobe 1973-1998 laut Snippet); OOS = 11/1998 bis heute.

**Belege (alle über Suchsnippets, Paper-Volltexte NICHT gelesen):**
- Bouman-Jacobsen, "The Halloween indicator, 'Sell in May and Go Away': Another puzzle" (AER 2002): Stichprobe 1973-1998 laut Snippet.
- Zhang-Jacobsen "...Everywhere and all the time" (Arbeitspapier ca. 2012, Journal-Angabe nicht verifiziert) [SNIPPET über CFA-Institute-Blog 2012]: 55 425 Monatsbeobachtungen, 108 Märkte, inklusive über 300 Jahren UK-Daten; Winterrendite (Nov-Apr) 4,52 % höher als Sommerrendite (t = 9,69; Einheit im Snippet nicht ausgewiesen, vermutlich Differenz der 6-Monats-Renditen); höhere Winterrenditen in 81 von 108 Ländern, signifikant in 35 Ländern vs. 2 Länder mit signifikant höherem Sommer. Post-Publikation (10/1998 bis 04/2011): Strategie schlägt Buy&Hold brutto in 31 von 37 Ländern, risikoadjustiert in 36 von 37 (Angabe laut CFA-Blog; brutto = ohne Kosten und Dividenden).
- Gegenstimme: Blogpost mathinvestor.org (2013) [SNIPPET]: Dow Jones 1915-2012, Sharpe der Strategie 0,275 vs. 0,279 für Buy&Hold, also praktisch gleich. Der Vorteil ist im US-Datensatz damit womöglich nur Risikoreduktion, kein Alpha.
- Frühe UK-Daten haben laut Snippet nur wenige Aktien im Index (drei Aktien in den ersten 110 Jahren) – dünne Evidenz im 17./18. Jahrhundert.

**Verfall / Kritik:** Keine gescheiterte Replikation in den Snippets gefunden außer der Sharpe-Gleichheit im Dow-Test. Kritisch bleibt: Nur 1 Wechsel/Jahr, ca. 25 unabhängige Winter-Sommer-Paare in 25 Jahren OOS. Die Evidenz aus 108 Ländern ist nicht unabhängig (globale Korrelation der Märkte). "Winter ab November" ist eine von 12 möglichen Fensterstartmonaten: Test, wie der Nov-Apr-Fenster-Rang unter allen 12 6-Monats-Fenstern liegt (Mining-Check).

**Kosten / Praxis:** 2 Trades/Jahr, vernachlässigbar (unter 0,1 % p.a.). Steuerlich günstig. Wirtschaftlich: In Sommermonaten Cash/Anleihen halten bedeutet bewusst verpasste Aktienprämie (ca. 50 % Zeit in Cash).

**Tail-Risiko:** Crashs im Sommerhalbjahr (Mai-Okt, z. B. Oktober 1987 und Herbst 2008) werden vermieden, Crashs im Winterhalbjahr (Nov-Apr, z. B. März 2020) voll mitgenommen. Ob das mehr als Zufall der Termine ist, lässt sich in 25 OOS-Jahren nicht entscheiden (Daten der Crashs aus dem Gedächtnis).

**Vorab-Hypothese:** Erwartung: Winter-minus-Sommer-Differenz bleibt positiv, aber Strategie-Sharpe ca. gleich Buy&Hold (Risikoreduktion statt Alpha). Abbruch, wenn die Strategie im OOS (11/1998 bis heute) weder Sharpe noch Max-DD gegenüber dem konstanten 50/50-Mix verbessert.

### 3.3 same_month_seasonality_industry – Heston-Sadka / Keloharju-Linnainmaa-Nyberg, Industrie-Saisonalität

**Regel (Forschungsvariante, Long-Short, nach Keloharju et al. Tabelle 1 [GELESEN]):**
```
Universum: 17 Fama-French-Industrien (French "17_Industry_Portfolios", value-weighted, monatlich).
Für Zielmonat t (Kalendermonat m):
  S_i(t) = Mittelwert über k = 1..20 von R_i(t - 12k)       # Renditen derselben Kalendermonate m in den letzten 20 Jahren
  (Paper: "average return in the same calendar month over the prior 20 years")
  Rang aller 17 nach S_i(t).
Portfolio für Monat t:
  Long gleichgewichtet die 2 Industrien mit höchstem S_i, Short gleichgewichtet die 2 mit niedrigstem S_i.
Rebalancing: monatlich; Halteperiode = Kalendermonat t (Close letzter Handelstag t-1 bis Close letzter Handelstag t).
Erster möglicher Monat: 1946-07 (20 volle Jahre nach 1926-07).
Zusatzvarianten (separat, Sensitivität): Long-only (nur die 2 Longs) gegen gleichgewichtetes Portfolio aller 17 und gegen die Placebo-Regel "Rang nach Other-Month-Mittel" (Paper-Kontrolle, soll ~ 0 oder negativ sein).
```
**Signal im Voraus bekannt:** Das Signal für Monat t benutzt nur Monate t-12, t-24, ... Daher sind MOC-Order am Close des letzten Handelstags von t-1 ohne Look-ahead möglich. Konservative Variante: Open des ersten Handelstags von t.

**Daten:** French 17 (oder 49) Industries, monatlich, 1926-07 bis heute. Echte Industrie-ETFs als Ausführung sind nur teilweise möglich (SPDR-Sektor-ETFs XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY ab 1998-12 [GEDÄCHTNIS], dazu spätere XLRE/XLC); die 20-Jahres-Historie erlaubt mit ETFs erst Signale ab ca. 2019, daher: Signal aus French, Ausführung über ETF-Mapping als offene Aufgabe. Länder-Variante: 15 MSCI-Länder im Paper (1970-2011, mindestens 5 Jahre Historie, Long/Short je 3 Länder); gratis Proxy iShares-Länder-ETFs ab 1996-03, erste Signale ab ca. 2001 – kurze Reihe, geringe Power.

**Belege [GELESEN, NBER WP 20815, Dez. 2014; Journal of Finance 71(4), 2016, 1557-1590 laut Suchtreffer]:**
- Einzelaktien, Dezil-Long-Short, 20 Jahre Same-Month: 1,19 %/Monat (t = 6,27), 1963-2011; Other-Month-Strategie -0,96 % (t = -4,12).
- Industrien (17 FF, Top2/Bottom2): 0,70 %/Monat (t = 3,79). Größen-Portfolios: 1,35 %/Monat (t = 6,64). Dividendenrendite: 0,48 % (t = 3,12). Composite (58 Portfolios, Top6/Bottom6): FF3-Alpha 1,3 %/Monat (t = 8,65), ohne Januar 0,90 % (t = 6,95).
- Länderindizes (15 MSCI, Long/Short je 3, Signale ab 12/1974, Daten bis 01/2011): Same-Month 0,48 %/Monat (t = 2,20), Other-Month -0,36 % (t = -1,66), Differenz t = 2,76. Rohstoffe (24 Futures): 0,93 % (t = 1,93), Differenz 1,15 % (t = 1,97).
- Tagesfrequenz: Same-Weekday-Strategie 0,11 %/Tag (t = 13,30) – laut Autoren wegen hoher Handelskosten nicht investierbar.
- Autoren: Saisonalität sei "nicht eine eigene Anomalieklasse", sondern hänge an gemeinsamen Faktoren (Größe, Dividendenrendite, Industrie); mindestens zwei Drittel der Saisonalität in Aktienrenditen stamme aus gemeinsamen Faktoren; die Strategie habe fast 100 % monatlichen Umschlag (analog Short-Term-Reversal) – Kapazität dennoch größer als bei Reversal (Verweis auf Frazzini-Israel-Moskowitz).
- Heston-Sadka (2008/2010) werden im Paper zitiert (Original nicht gesehen): Saisonalität in Einzelaktien-Querschnitt, unabhängig von Industrie/Größe kontrolliert; Saisonalitäten in 14 internationalen Märkten.
- Folgepapier "Seasonal Reversals in Expected Stock Returns" (Keloharju/Linnainmaa/Nyberg) [SNIPPET]: Saisonalität werde durch Reversal in den anderen Monaten ausgeglichen, Autoren schließen auf temporäre Fehlbewertung.

**Verfall:** [GELESEN] Keloharju et al. Abschnitt 5.4.2: Die meisten Saisonalitätsstrategien sind in allen Teilperioden außer der jüngsten (2003-2011) signifikant positiv; das Composite hat in 2003-2011 nur t = 1,75 (alle Teilperioden davor t > 3,5). Die Teilperioden-Tabelle für die reine Industrie-Strategie ist im PDF-Text verschoben, deshalb nicht zitiert. Unabhängige Replikation nach 2011 mit Industrie-Daten: NICHT gefunden. Die einzige ehrliche OOS-Prüfung ist 2012 bis heute auf French-Daten.

**Kosten / Praxis:** Fast 100 % Monatsumschlag im Long-Short. Industrie-Portfolios sind liquide, aber echte Umsetzung braucht Short-Beine (für Privatanleger über Sektor-ETFs mit Leerverkauf/CFD nur teuer und mit Finanzierungskosten). Long-only-Variante trägt überwiegend Markt-Beta; der Edge liegt im Spread zur Gleichgewichtung. Hohe Kosten- und Steuerempfindlichkeit durch Monatsumschlag (Abgeltungssteuer ohne Stundung).

**Tail-Risiko:** Long-Short ist marktneutral nur ungefähr; Saisonalität ist mit Größen-/Werteffekten verwoben, Faktor-Crashs (2009, 2020) können beide Beine gegen einen laufen lassen. Mit nur 17 Industrien und 2/2 Positionen ist die Konzentration hoch.

**Vorab-Hypothese:** Erwartung: Long-Short Same-Month ist OOS 2012+ positiv, aber t < 2; Long-only schlägt Gleichgewicht nach Kosten nicht. Abbruch, wenn die Differenz Same-Month minus Other-Month OOS 2012+ nicht signifikant größer als 0 ist oder der Net-Sharpe Long-Only gegen Gleichgewicht < 0 liegt.

### 3.4 pre_fomc_drift_daily_proxy – Pre-FOMC Announcement Drift (Lucca-Moench), Tagesdaten-Proxy

**Regel (Proxy, die exakte Original-Regel ist mit Gratis-Daten NICHT testbar):**
```
Original (Lucca-Moench): Long S&P 500 ab 14:00 Uhr (ET) am Tag vor der geplanten FOMC-Ankündigung bis 14:00 am Ankündigungstag (24 Stunden vor der Veröffentlichung); sonst Cash.
Proxy mit Tagesdaten:
  D = Ankündigungstag eines GEPLANTEN FOMC-Termins (bei zweitägigen Sitzungen der zweite Tag; ohne außerplanmäßige/Notfall-Sitzungen).
  Long 100 % SPY vom Close(D-1) bis Close(D); sonst Cash.   # enthält ca. 22 der 24 Stunden vor 14:00 (Close D-1 -> 14:00 D) PLUS 2 Stunden nach der Ankündigung (14:00 -> Close D)
Order: MOC an D-1 (Termin im Voraus bekannt), Exit MOC an D.
Sensitivität (nicht zur Auswahl): Close(D-2)->Close(D-1) ("T-1"); Close(D-1)->Open(D) (nur Overnight); Kosten 1/2/5 bps.
```
Warum Proxy-Ungenauigkeit wichtig ist: Die Nachankündigungsreaktion (14:00-16:00) hat hohe Varianz und kann positive oder negative Drift verwischen. Gratis-Intraday-Daten (yfinance 1h/5m) reichen nur wenige Monate bzw. ca. 730 Tage zurück (GEDÄCHTNIS), also nicht für eine Mehrjahresprüfung.

**Daten:** SPY ab 1993-01-29 (Lucca-Moench-Stichprobe beginnt 1994, erste FOMC-Termine mit Ankündigung ab Feb. 1994), FOMC-Kalender von federalreserve.gov (manuell zu CSV, gratis). Publikationsende = 03/2011 (Paper-Stichprobe 09/1994-03/2011 laut Snippet); OOS = 04/2011 bis heute.

**Belege:**
- Lucca-Moench, NY Fed Staff Report 512 [GELESEN, nur Abstract] / Journal of Finance 70(1), Feb. 2015 [SNIPPET]: Überrenditen im 24-Stunden-Fenster vor geplanten Terminen seit 1994; Ankündigungstagrenditen "mehr als 30-mal größer" als an anderen Tagen; das Vorfenster erkläre "mehr als 80 %" der Aktienprämie im Sample; ähnliche Muster in globalen Indizes, nicht in Anleihen/anderen Nachrichten; keine Risikoerklärung greift. Magnitude ca. 49 bps im Schnitt laut Suchsnippet (unverifiziert). Das Abstract enthält keine bp-Zahlen.
- R-Bloggers/Return and Risk Replikation mit SPY-Tagesdaten (Close D-1 -> Close D) [GELESEN]: In-Sample 01/1994-03/2011, 138 Termine: FOMC-Tag Überrendite 0,33 % (SD 1,17 %) vs. Nicht-FOMC 0,02 %; Differenz +0,31 %, 95-%-Bootstrap-KI 0,11 % bis 0,50 % (also signifikant). Out-of-Sample 04/2011-01/2015, 31 Termine: FOMC-Tag 0,26 % (SD 1,37 %), Nicht-FOMC 0,05 %; Differenz-KI -0,25 % bis +0,69 % (nicht signifikant). Autor-Schätzung: ca. 120 Termine (ca. 15 Jahre) nötig, um den Effekt bei Fortbestand nachzuweisen.

**Verfall (stark):**
- Kurov-Wolfe-Gilbert, "The Disappearing Pre-FOMC Announcement Drift", Finance Research Letters (2021) [SNIPPET; PDF 404]: Stichprobe bis 12/2019; Drift sei nach 2015 praktisch verschwunden, mit und ohne Pressekonferenz.
- Boguth-Grégoire-Martineau (2019) [SNIPPET]: Drift nur bei Terminen mit Pressekonferenz.
- NY Fed Liberty Street, Nov. 2018 [SNIPPET]: weiterhin große Überrenditen, aber nur bei Sitzungen mit Pressekonferenz des Vorsitzenden – kürzerer Zeitraum, günstiger als Kurov et al.
- Meine Rechnung aus den R-Bloggers-OOS-Zahlen: 8 Termine/Jahr, Mittel 0,26 %, SD 1,37 % pro Termin -> ca. 2,1 % p.a. Mittel bei ca. 3,9 % p.a. SD, also t ca. 0,5 pro Jahr. Selbst wenn der Effekt echt wäre, ist er in überschaubarer Zeit statistisch nicht nachweisbar.

**Kosten / Praxis:** 8 Round-Trips/Jahr, ca. 0,2-0,3 % p.a. Kosten gegen eine Brutto-Erwartung von höchstens ca. 1-2 % p.a.; Rest ist Noise der Ankündigungsreaktion. Steuer: 8 Realisierungen/Jahr.

**Tail-Risiko:** Ein Tag Long-Aktienrisiko mit Event-Risiko (überraschende Zinsentscheidung); Verlust an einem einzelnen Termin kann das Jahresplus eines Jahres ausradieren (SD pro Termin 1,2-1,4 %).

**Empfehlung:** Nur als Negativ-/Kontrollstrategie testen ("Ist der Effekt nach 2015 weg?"). Standalone nicht handelbar. NO TRADE ist Standard.

**Vorab-Hypothese:** Erwartung: OOS (2011+) FOMC-Tag-Überrendite nicht signifikant größer als an Normaltagen; Abbruchkriterium schon vor dem Test: Net Edge pro Termin unter 5 bps.

### 3.5 overnight_spy_close_to_open – Overnight-Drift (Cooper-Cliff-Gulen / Lou-Polk-Skouras)

**Regel:**
```
Täglich für jeden Handelstag t:
  Long 100 % SPY von Close(t) bis Open(t+1); während des Handelstags 100 % Cash.
Order: MOC an t, MOO an t+1.  Rendite_t = Open(t+1) / Close(t) - 1  (auto_adjust=True).
Kosten: 2 Trades pro Tag (252 Round-Trips/Jahr). Zu testen: 0,5 / 1 / 2 / 5 bps pro Trade plus MOC/MOO-Abweichung vom offiziellen Eröffnungs-/Schlusskurs.
```
Gegen-Test (Pflicht): Intraday (Open->Close) und Buy&Hold als Zerlegung der Gesamtrendite.

**Daten:** SPY ab 1993-01-29 (Yahoo Open/High/Low/Close, `auto_adjust=True`), ^GSPC-Open ist vor den 1980ern unzuverlässig [GEDÄCHTNIS]. Original-Papers nutzen CRSP-Aktien (Cooper-Cliff-Gulen: US-Aktien 1993-2006 laut Snippet). Publikationsende ca. 2006-2007.

**Belege (Suchsnippets, Papers NICHT gelesen):**
- Alpha Architect (Gast-Post vom 16.06.2020, Titel laut Suchtreffer "Trading costs wipe out the overnight return anomaly"; Abruf 403, Inhalt nur über Snippet): SPY 01/1993-01/2020, kumulative PREIS-Rendite Overnight 717 %, Buy&Hold 627 %, Intraday 12 % – ohne Kosten. Ein weiteres Snippet derselben Suche (Quelle nicht eindeutig zuordenbar) nennt: bei 1 bp pro Trade falle die Overnight-Rendite eines ETF auf 7,3 % p.a., weniger als der ETF selbst. Ein anderer Snippet-Satz sagt widersprüchlich, der Overnight-Vorteil bestehe brutto und netto fort, sei aber "more of a random walk than a repeatable trading strategy" – die Snippets sind also nicht eindeutig; die Kostenwirkung muss der eigene Backtest zeigen. Eigene Umrechnung: 717 % Gesamtrendite = Faktor 8,17 über 27 Jahre -> ca. 8,1 % p.a. brutto; bei 2 bps pro Tag × 252 Tage = ca. 5,0 % p.a. Kosten -> ca. 3 % p.a. netto gegen ca. 7,6 % p.a. Buy&Hold-Preisrendite (alles Preisrenditen, Dividenden fehlen auf beiden Seiten).
- QuantConnect "Overnight anomaly" [SNIPPET]: Renditen werden nach Transaktionskosten aufgehoben, geschätzte Gebühren über 20 Jahre fast 25 % des Startkapitals (Interactive-Brokers-Gebührenmodell).
- Cliff-Cooper-Gulen (2007) [SNIPPET]: 1993-2006, Overnight-Renditen stark positiv, auch vom Freitagsschluss zum Montags-Open.
- Lou-Polk-Skouras, "A tug of war: Overnight versus intraday expected returns", JFE 2019 [SNIPPET, LSE-Repository]: Momentum-Gewinne fallen im Overnight an, andere Anomalien intraday, mit entgegengesetzten Vorzeichen; Querschnitts-Aussage mit Einzelaktien (CRSP), nicht mit ETFs kostenlos reproduzierbar.
- Hendershott-Livdan-Rösch, JFE 138(3), 2020, "Asset pricing: A tale of night and day": nur bibliographische Angabe gesehen, Inhalt NICHT gelesen.
- Eine ETF-Studie (2016) [SNIPPET, Quelle unklar] berichte "deutliche Abnahme und Verschwinden" des Night-and-Day-Effekts ab 2006. Nicht verifiziert.

**Verdikt:** Funktioniert **nach Kosten nicht**. Die Brutto-Prämie existiert in SPY-Daten (Overnight ~ gesamter Preisgewinn), wird aber von 252 Round-Trips pro Jahr aufgezehrt. Für deutsche Privatanleger kommen Abgeltungssteuer auf jede einzelne Tageshandlung und fehlende MOC/MOO-Qualität bei vielen Brokern hinzu. Einzig als Zerlegungswerkzeug (wie viel Rendite fällt overnight an?) bleibt es nützlich, z. B. als Diagnose für andere Strategien (Slippage-Realismus beim Eröffnungskurs).

**Tail-Risiko:** Overnight-Gaps (Schlusskurs bis Eröffnung) tragen die größten Einzeltagsverluste; kein Stop möglich. Bei Mehrtagesereignissen (Wochenenden, Feiertage) unveränderlich.

**Vorab-Hypothese:** Erwartung: brutto positiv, netto bei 1 bp pro Trade unter Buy&Hold. Abbruch ist hier die Erwartung selbst – Test nur zur Kostendokumentation.

## 4. Nicht übernommene oder nur im Anhang geführte Kandidaten

### 4.1 FOMC-Zyklus, gerade Wochen (Cieslak-Morse-Vissing-Jorgensen) – eigener Test empfohlen, hier nur Notiz

Paper: "Stock Returns over the FOMC Cycle", Journal of Finance 2019 [SNIPPET über Suchtreffer; SSRN 2687614; NYU-PDF]. Kernbefund: Die Aktienprämie seit 1994 fällt in den Wochen 0, 2, 4, 6 des FOMC-Zyklus an (Woche 0 beginnt am Tag vor einer geplanten Ankündigung). CFA-Digest-Snippet: durchschnittliche Überrenditen in geraden Wochen 0,33 % bis 0,60 %, in ungeraden -0,09 % bis -0,18 % (Einheit: vermutlich pro Woche, im Snippet nicht eindeutig); die Autoren sehen die Differenz als signifikant auf dem 1-%-Niveau. Der 2018er Arbeitspapier-Entwurf nennt die Stichprobe 2014-2016 als Bestätigung nach dem ersten Entwurf. Erklärung der Autoren: Risikoprämie für Fed-Nachrichten, nicht Makrodaten-Kalender. Verfall nach 2016: NICHT gefunden (weder Bestätigung noch Widerlegung).

Mögliche Regel (meine Operationalisierung, am Original nicht geprüft):
```
S_j = Handelstag vor dem Ankündigungstag D_j eines geplanten FOMC-Termins j.
Für jeden Handelstag u mit S_j <= u < S_{j+1}: Zyklus-Tag n = (Anzahl Handelstage seit S_j), Zyklus-Woche w = floor(n / 5).
Long SPY, wenn w in {0, 2, 4, 6}; sonst Cash.  Signal bekannt, MOC am Vortag; Konservativ: Open.
```
Grund für Nicht-Aufnahme: Ungeprüfte Fensterdefinition (5-Tage-Blöcke), Überlappung mit Pre-FOMC (Woche 0 enthält den Pre-FOMC-Tag), starke Datamining-Gefahr (warum gerade Wochen?), kein Post-2016-Test gefunden, und Exposure ca. 55-60 % mit etwa 16 Wechseln/Jahr. Wäre als 6. Kandidat der nächste in der Reihe.

### 4.2 Wochenend-/Wochentagseffekt – tot

- Robins-Smith, "No More Weekend Effect", Critical Finance Review 2016 [SNIPPET]: Vor 1975 war die mittlere Wochenendrendite der Gleich-/Wertgewichteten Marktportfolios signifikant -18 bps/-19 bps, nach 1975 nicht signifikant (-5 bps/-1 bp). CRSP 1926-2014, Strukturbruchtest mit unbekanntem Bruchdatum.
- Schwert, "Anomalies and Market Efficiency" (NBER WP 9277, 2003) [SNIPPET]: Wochenendeffekt (neben Größe, Value, Dividendenrendite) habe sich nach der Publikation abgeschwächt oder sei verschwunden; Praktiker-Handel könne Anomalien beseitigen.
- Gegenmeinung: Olson-Mossman-Chou (2015) [SNIPPET]: Effekt sei nach Entdeckung (1973) erst gefallen, dann zeitweise wieder aufgetaucht bzw. umgekehrt; Montags-Differenz sei nach 1975 stationär.
- Studie 23 entwickelter Märkte (2003) [SNIPPET]: Wochentagseffekt in den 1980ern verbreitet, in den 1990ern verblasst.
- Fazit: Als Handelsstrategie nicht aufgenommen. Test nur zur Dokumentation (French daily, 1926-): "Long außer Fr-Close -> Mo-Close". Erwartung: ab 1975 kein Edge.

### 4.3 Nicht untersucht (Budget oder keine Gratis-Daten)

- Earnings-Announcement-Premium (Savor-Wilson; Barber et al.) und Post-Earnings-Announcement-Drift: Brauchen firmenspezifische Ergebniskalender und Preise für viele Einzeltitel; keine zuverlässigen Gratis-Daten. Verweis: Keloharju et al. erwähnt Frazzini-Lamont (2007) und Barber/De George/Lehavy/Trueman (2013) zu positiven Abnormalrenditen um geplante Ergebnisse [GELESEN, nur als Zitat].
- Jahreswechsel-Effekte (Januar, Santa Claus, Pre-Holiday), Optionsverfall, Zahltags-Effekte: nicht recherchiert.
- AQR-/Hoffstein-/Allocate-Smartly-Seiten zu Kalenderstrategien: nicht abgerufen.

## 5. Empfehlung für Quant-Lab

1. **Reihenfolge der Tests** (nach Robustheit): TOM (3.1), Halloween (3.2), Industrie-Saisonalität (3.3). Pre-FOMC (3.4) und Overnight (3.5) nur als Dokumentation des Verfalls bzw. der Kostenwirkung. Wochentag nur als Kontrolle.
2. **Gemeinsame Pflichtkontrollen:** (a) Exposure-gematchte Zufallsfenster, (b) konstante Mischquote, (c) OOS strikt ab Publikationsende, (d) Kosten-Raster, (e) Steuer ohne Stundung (nur bei häufigen Wechseln relevant).
3. **Realistische Erwartung:** TOM und Halloween liefern bestenfalls Risikoreduktion mit kleinem oder keinem Alpha nach Kosten; ein absolut schlagkräftiger Edge ist nicht in Sicht. Das passt zu den "geltenden" Erfolgsfällen der Quant-Lab-Regeln (sicheres Portfolio ist ein gültiges Ergebnis). Kombinationen aus mehreren Kalenderfenstern erhöhen nur das Mehrfachtest-Problem.
4. **Datenarbeit vor Backtest:** FOMC-Kalender als CSV (nur geplante Termine, Ankündigungstag), NYSE-Handelstage-Kalender aus den Daten ableiten, French-Datasets per `pandas_datareader` und lokal cachen.

## 6. Quellen-URLs

Abgerufen [GELESEN]:
- https://fedinprint.org/item/fednsr/12655 (Lucca-Moench, NY Fed SR 512, Abstract)
- https://www.r-bloggers.com/2015/03/update-on-the-pre-fomc-announcement-drift/ (Replikation SPY)
- https://quantpedia.com/strategies/turn-of-the-month-in-equity-indexes
- https://www.cxoadvisory.com/calendar-effects/the-turn-of-the-month-effect/
- https://www.nber.org/papers/w20815.pdf (Keloharju-Linnainmaa-Nyberg)

Nur Suchtreffer/Snippet [SNIPPET]:
- https://ideas.repec.org/a/taf/ufajxx/v64y2008i2p49-64.html (McConnell-Xu, FAJ 2008)
- https://www.atlantafed.org/research/publications/wp/2000/11.aspx (Maberly-Waggoner)
- https://www.financialplanningassociation.org/article/journal/APR11-turn-month-anomaly-age-etfs-reexamination-return-enhancement-strategies (TOM im ETF-Zeitalter, 2011)
- https://academicnewsletter.sufe.edu.cn/info/352600 (Bouman-Jacobsen, Another puzzle)
- https://research.nottingham.edu.cn/en/publications/the-halloween-indicator-sell-in-may-and-go-away-everywhere-and-al/fingerprints/ (Zhang-Jacobsen)
- https://rpc.cfainstitute.org/blogs/enterprising-investor/2012/the-halloween-indicator-a-stock-market-anomaly-that-is-stronger-than-ever (CFA-Blog zu Halloween)
- https://mathinvestor.org/2013/11/the-myth-of-the-halloween-indicator/ (Blog, Dow-Test)
- https://www.skidmore.edu/economics/documents/KurovWolfeGilbert-TheDisappearingPre-FOMC-Announce-Drift-200914.pdf (Kurov-Wolfe-Gilbert, bei Abruf 404)
- https://papers.ssrn.com/abstract=2687614 (Cieslak-Morse-Vissing-Jorgensen)
- https://stern.nyu.edu/sites/default/files/assets/documents/cycle_paper_cieslak_morse_vissingjorgensen.pdf
- https://researchonline.lse.ac.uk/id/eprint/119010 (Lou-Polk-Skouras)
- https://ideas.repec.org/a/eee/jfinec/v138y2020i3p635-662.html (Hendershott-Livdan-Rösch, nur Bibliographie)
- https://alphaarchitect.com/trading-costs-wipe-out-the-overnight-return-anomaly/ (bei Abruf 403)
- https://www.quantconnect.com/research/15296/overnight-anomaly/p1
- https://nowpublishers.com/article/Details/CFR-0038 (Robins-Smith, No More Weekend Effect)
- https://www.nber.org/papers/w9277 (Schwert, Anomalies and Market Efficiency)
