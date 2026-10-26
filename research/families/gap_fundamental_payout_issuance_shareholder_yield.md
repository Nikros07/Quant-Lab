# Familie (Nachrecherche): Payout- und Emissions-Faktoren (Net Share Issuance, Net Payout Yield, Shareholder Yield)

Stand der Recherche: 2026-10-12. Dies ist eine Nachrecherche zu einer vom Kritiker gefundenen Luecke.
Budget war ca. 15 Web-Abrufe; tatsaechlich genutzt: 17 (7 WebSearch, 10 WebFetch). Davon waren 4 unproduktiv: 2 Abrufe mit von mir falsch geratener NBER-Nummer (w11182, w22287, beides fremde Paper, nichts verwertet), 2 Abrufe mit Redirect (Wharton-PDF: 404-Redirect, Inhalt nie gelesen; Cochrane-PDF: Redirect, der Folgeabruf lief durch). Zwei PDFs (HXZ, FF2008) wurden vom WebFetch lokal gespeichert und danach mit pdftotext selbst gelesen. Das Budget ist leicht ueberschritten.

Fortsetzung nach Nutzungslimit-Reset (2026-10-12): Die Notizdatei war bereits vollstaendig geschrieben; es wurden keine weiteren Web-Abrufe gemacht (Budget war ohnehin ueberschritten), die Datei wurde nur gegengelesen und das strukturierte Ergebnis daraus abgeleitet. Die in Abschnitt 5 genannten offenen Punkte bleiben offen.

Alle Zahlen stammen aus tatsaechlich gelesenen Seiten/PDFs oder sind ausdruecklich als "Suchsnippet", "Sekundaerquelle", "aus Gedaechtnis, nicht verifiziert" oder "nicht gefunden" markiert. Eigene Berechnungen (z. B. FF5-Regression) wurden in diesem Lauf NICHT durchgefuehrt, weil keine Daten-Downloads gemacht wurden; die Spezifikation fuer diesen Test steht unten.

## 0. Kurzfazit (ehrlich)

1. Der Emissions-Effekt (Net Stock Issues, NI/NSI) ist einer der am besten belegten Bilanz-Anomalien im Faktorzoo: Fama/French (2008) finden Hedge-Renditen von -0,54 % bis -0,71 % pro Monat (t > 4,25) in ALLEN drei Groessengruppen (Micro, Small, Big), gleich- und wertgewichtet, 1963-2005 (gelesen, Originaltext). Hou/Xue/Zhang (HXZ) replizieren ihn mit strenger Methodik (NYSE-Breakpoints, wertgewichtet, Dezile) mit -0,66 % pro Monat (t = -4,45), 1967-2014 (gelesen, aber Tabellenzelle aus verunstaltetem pdftotext-Layout zugeordnet, siehe Abschnitt 3).
2. ABER: Der Effekt ist KEIN eigenstaendiger Faktor. Fama/French (RFS 2016) zeigen, dass das Fuenf-Faktor-Modell die NI-Anomalie erklaert (Rueckkaeufer laden positiv auf RMW und CMA, starke Emittenten negativ). HXZ finden: Das q-Faktor-Alpha des NSI-Spreads ist noch -0,29 % (t = -2,19), also unter der Huerde t = 3, und die Investment-Ladung dominiert. Antwort auf die Kernfrage (inkrementeller Nutzen gegen FF5 und gegen die Quality/Value-Eintraege): sehr wahrscheinlich ein Duplikat der Investment-/Profitability-Exposition. Dies ist aus der Literatur geschlossen, NICHT selbst gerechnet.
3. Der Effekt ist zeitlich instabil: Pontiff/Woodgate und Fama/French (2008) berichten, dass vor 1970 bzw. in 1926-1962 kein NI-Effekt zu sehen ist. Der gesamte Beleg stammt aus ca. 1963/1970 bis heute.
4. Der Effekt sitzt in den Extremen: Nach Fama/French (2008) sind die negativen abnormalen Renditen auf das hoechste Emissionsquintil begrenzt (dort im Schnitt 20-26 % der ausstehenden Aktien), die mittleren Quintile haben sogar positive abnormale EW-Renditen. Konsequenz: Als Long-only-Variante taugt eher ein Ausschluss-Screen (die extremen Emittenten meiden) als ein breites Tilting.
5. Net Payout Yield (Boudoukh et al. 2007): in Zeitreihen und Querschnitt informativer als die Dividendenrendite (Abstract gelesen). Unabhaengige strenge Replikation (HXZ): Dividendenrendite (Dp) und Total Payout Yield (Op) sind in wertgewichteten NYSE-Dezilen insignifikant, aber der Net Payout Yield (Nop) ist signifikant (+0,65 %/Monat, t = 3,36, q-Alpha +0,36, t = 2,41; Zuordnung inferiert, ab Juli 1972). Der Gewinn kommt also aus dem Emissionsabzug, nicht aus dem Dividenden-/Rueckkaufteil.
6. Free-Data-Realitaet: Ken French bietet NI- und D/P-Portfolios, aber KEINE Payout-/Total-Payout-Portfolios (Bibliotheksseite geprueft). Echte Net-Payout-Yield-Strategien brauchen Compustat und sind mit Gratis-Daten nicht reproduzierbar. Handelbare Gratis-Proxies sind Fonds (SYLD, PKW, SDY, UCITS-Dividenden-ETFs); die haben nur kurze Historie (ab ca. 2005 bis 2013) und tragen Value-/Size-Tilts, die kein Payout-Alpha beweisen.
7. Kosten: Alle French-Zeitreihen sind brutto, Long-Short und nicht handelbar. Die Short-Seite (Grossemittenten) liegt ueberwiegend in kleinen, teuer zu shortenden Werten; im Long-only-Screen bleibt das Problem aus, aber der Vorteil schrumpft entsprechend.

Ranking-Begruendung ("Robustheit" = Evidenzstaerke x Handelbarkeit mit Gratis-Daten x Ueberleben nach Kosten): Platz 1 ist der Ausschluss-Screen (nutzt die robuste Seite des Effekts, long-only, niedrige Umschlaghaeufigkeit, aber nur als Research-Replikation machbar). Platz 2 ist das Diagnose-Instrument auf Faktor-Ebene mit klarer Entscheidungsregel (starke Evidenz, nicht handelbar, wahrscheinlich redundant). Platz 3 ist der Net-Payout-Proxy (schwacher Proxy, aber der einzige gratis-moegliche Zugang zur Boudoukh-Idee). Platz 4 und 5 sind die einzig direkt handelbaren Varianten und haben vermutlich keinen Edge nach TER.

## 1. Abrufstatus (Transparenz)

| Quelle | URL | Status |
|---|---|---|
| Ken French Data Library (Uebersichtsseite) | https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html | ABGERUFEN. NI-Datei: Portfolios_Formed_on_NI_CSV.zip; D/P: Portfolios_Formed_on_D-P_CSV.zip; ex-Dividenden-Variante Portfolios_Formed_on_D-P_Wout_Div_CSV.zip. Kein Payout-/Total-Payout-Eintrag gefunden. |
| Ken French NI-Detailseite | https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_port_form_NI.html | ABGERUFEN. NYSE-Breakpoints, Formierung Ende Juni, NI = Aenderung des natuerlichen Logarithmus der splitbereinigten Aktienzahl von Geschaeftsjahresende t-2 bis t-1; Portfolios: NI<0, NI=0, Quintile, Dezile; alle NYSE/AMEX/NASDAQ-Aktien mit Marktkapitalisierung im Juni t und Aktienzahlen t-2 und t-1. Monatsrenditen ab Juli 1963 (laut Seite "bis August 2026"), Jahresrenditen ab 1964 (bis 2025). Gewichtung (VW/EW) steht NICHT auf der Seite. |
| Pontiff/Woodgate (2008), JF 63(2), 921-945 | https://ideas.repec.org/a/bla/jfinan/v63y2008i2p921-945.html | NUR Suchergebnis/Abstract-Zusammenfassung (IDEAS in den Suchtreffern). Volltext NICHT gelesen. |
| McLean/Pontiff/Watanabe (2009), JFE 94(1), 1-17 | https://ideas.repec.org/a/eee/jfinec/v94y2009i1p1-17.html | ABGERUFEN (IDEAS-Seite, Abstract). Volltext nicht gelesen. |
| Boudoukh/Michaely/Richardson/Roberts (2007), JF 62(2), 877-915 | https://www.nber.org/papers/w10651 | ABGERUFEN (NBER-Abstract; Working Paper Juli 2004, rev. Feb 2006). Keine Zahlen auf der Seite. Wharton-PDF-Link (Autorenseite) scheiterte (Redirect auf 404). |
| Fama/French (2008), Dissecting Anomalies, JF 63(4), 1653-1678 | https://ideas.repec.org/a/bla/jfinan/v63y2008i4p1653-1678.html (Suchtreffer); Manuskript: https://www.johnhcochrane.com/s/fama_french_dissecting_anomalies_JF.pdf (Redirect auf static1.squarespace.com, dort geladen) | MANUSKRIPT GELESEN (Autorenversion mit JF-Seitenzahlen 1662-1675; relevante Passagen zu NI, Tabellen II-V, Schlussfolgerungen). |
| Fama/French (2016), Dissecting Anomalies with a Five-Factor Model, RFS 29(1), 69-103, DOI 10.1093/rfs/hhv043 | https://academicnewsletter.sufe.edu.cn/info/353707 und CFA-Digest https://rpc.cfainstitute.org/research/cfa-digest/2016/05/dissecting-anomalies-with-a-five-factor-model-digest-summary | NUR Abstract/Digest-Zusammenfassungen aus Suchergebnissen. Volltext NICHT gelesen. Stichprobe laut Suchergebnis: Juli 1963 bis Dezember 2014. |
| Hou/Xue/Zhang (2020), Replicating Anomalies, RFS; NBER w23394 | https://www.nber.org/papers/w23394.pdf | PDF GELADEN und mit pdftotext gelesen (Abschnitte 3.2.2, 3.2.3, Anhang A.2.14-A.2.17, A.3.10, A.3.12, Tabellen 4/5 in verunstaltetem Layout). |
| Quant-Investing Blog (Shareholder-Yield-Backtest 2001-2013) | https://www.quant-investing.com/blog/dividend-investor-this-ratio-beats-dividend-yield/ | NUR SUCHSNIPPET (Zusammenfassung der Suchmaschine), Seite nicht geoeffnet. Sekundaerquelle, Blog. |
| SYLD (Cambria Shareholder Yield ETF) | u. a. https://www.cboe.com/us/equities/listings/listed_products/symbols/SYLD/ , https://www.roic.ai/quote/SYLD | NUR Suchsnippets (Fondsseiten nicht geoeffnet). |
| Calluzzo/Moneta/Topaloglu, "Anomalies are Fleeting" (JFE) | keine direkte URL im Suchtreffer | NUR Suchsnippet-Zusammenfassung (Net Stock Issues unter 14 Anomalien, Post-Publikation-Rendite um 32 % relativ gesunken, gepoolt). NICHT als Paper gefuehrt. |
| "Anomalies across the globe: once public, no longer existent?" | https://portal.fis.tum.de/en/publications/anomalies-across-the-globe-once-public-no-longer-existent/ | NUR Titel/Snippet: 241 Anomalien, 39 Maerkte, nur die USA zeigen einen verlaesslichen Post-Publikations-Rueckgang der Long-Short-Renditen. Autoren im Treffer nicht genannt, NICHT als Paper gefuehrt. |
| Ikenberry/Lakonishok/Vermaelen (1995), JFE | - | NICHT abgerufen. Bewusst nicht als Paper gefuehrt. |

Nicht abgerufen und deshalb NICHT als Paper gefuehrt: Ikenberry/Lakonishok/Vermaelen 1995, Daniel/Titman 2006 (Composite Issuance), Bradshaw/Richardson/Sloan 2006 (Net External Financing; nur ueber HXZ-Text erwaehnt), Hirshleifer/Jiang (Financing-based Misvaluation Factor), Faber (Buch "Shareholder Yield"), McLean/Pontiff 2016 (nur Suchsnippet: ca. -50 % nach Publikation), Chen/Zimmermann (Open Source Asset Pricing; evtl. gratis Signaldaten, nicht geprueft), Jensen/Kelly/Pedersen.

## 2. Verifizierte Literaturbefunde (nur Gelesenes)

### 2.1 Fama/French (2008), Dissecting Anomalies (Manuskript gelesen)
- NI-Definition: Aenderung des natuerlichen Logarithmus der splitbereinigten Aktienzahl von Geschaeftsjahresende t-2 auf t-1 (identisch mit der Ken-French-NI-Definition). Sortierung jeweils Ende Juni; Haltedauer Juli bis Juni; Stichprobe Juli 1963 bis Dezember 2005; Breakpoints fuer alle Groessengruppen aus der Gruppe "All-but-Micro".
- Sortierzellen: Negative NI in 2 Zellen (Median der negativen Werte), Nullen separat, positive NI in 5 Quintilen.
- Hedge-Renditen (extreme Portfolios): "negative average hedge returns ... range from -0.54% to -0.71% per month and are more than 4.25 standard errors from zero for all size groups and for EW and VW returns" (so sinngemaess; Zahlen aus Text).
- Fama-MacBeth-Steigungen auf nichtnull-NI: -1,49 bis -1,94 fuer Micro/Small/Big, alle weiter als 4,4 Standardfehler von null; Unterschiede zwischen Groessengruppen kleiner als 1,15 Standardfehler. Also konsistent in allen Groessengruppen.
- Spektrum: Starke positive abnormale EW-Renditen nach grossen Rueckkaeufen (ueber dem Median: im Schnitt ca. 5 % der ausstehenden Aktien): 0,47 %, 0,26 %, 0,28 % pro Monat fuer Micro, Small, Big. Die ersten drei positiven Quintile (Emissionen im Schnitt 0,1 %, 0,6 %, 1,5 % der Aktien) haben positive abnormale EW-Renditen. Nur das fuenfte Quintil (Emissionen im Schnitt 20-26 % der Aktien) liefert verlaesslich niedrigere Renditen als groessen- und B/M-gematchte Portfolios.
- Zeitliche Instabilitaet: "Pontiff and Woodgate (2008) find that the earlier period produces no evidence that net stock issues ... are associated with unusual returns" (1926 bis ca. 1962/1970, siehe auch Pontiff/Woodgate unten). Fama/French nennen das einen "serioeseren Fleck" auf der NI-Anomalie.
- Big stocks machen laut Text mehr als 90 % der Gesamt-Marktkapitalisierung aus.

### 2.2 Pontiff/Woodgate (2008) (nur Abstract aus Suchergebnis)
- Aktienemissionen sagen Querschnittsrenditen nach 1970 stark vorher; die Vorhersagekraft ist statistisch signifikanter als die von Size, Book-to-Market oder Momentum, bleibt nach Ausschluss der aus Studien zu Rueckkaeufen, Zweitplatzierungen und Fusionen bekannten Daten bestehen; vor 1970 ist die Beziehung in den meisten Haltedauern nicht signifikant (Zusammenfassung der Suchmaschine, nicht der Volltext).

### 2.3 McLean/Pontiff/Watanabe (2009) (IDEAS-Abstract gelesen)
- 41 Laender. Emission sagt Renditen voraus; Signifikanz hoeher als Size oder Momentum, aehnlich wie Book-to-Market. Der Effekt zeigt sich bei kleinen und grossen Firmen. Anders als in den USA wird er im Ausland staerker von schwachen Renditen nach Emissionen getragen als von starken Renditen nach Rueckkaeufen. Staerker in Laendern mit mehr Emissionsaktivitaet, entwickelteren Aktienmaerkten und besserem Investorenschutz. Interpretation der Autoren: der Effekt haengt an der Leichtigkeit, Aktien auszugeben und zurueckzukaufen. Das spricht fuer die Meidung-extremer-Emittenten-Konstruktion (Strategie 1), weil die Emissionsseite international der Treiber ist.

### 2.4 Boudoukh/Michaely/Richardson/Roberts (2007) (NBER-Abstract gelesen)
- Rueckgang der Vorhersagekraft der Dividendenrendite in Zeitreihenregressionen ist stark uebertrieben. Mit Total Payout Yield (Dividenden plus Rueckkaeufe) statt Dividendenrendite signifikante und oekonomisch relevante Vorhersagbarkeit auf kurzen und langen Horizonten. Total Payout Yield traegt im Querschnitt mehr Information ueber erwartete Renditen als die Dividendenrendite; das High-minus-Low-Payout-Yield-Portfolio ist ein bepreister Faktor. Ergebnisse robust gegen verschiedene Messmethoden. Zahlen: auf der NBER-Seite keine. Keine Zahlen gefunden.
- Kritik durch HXZ (Text gelesen): Das Ergebnis zu Op basiert bei Boudoukh auf NYSE-Breakpoints, aber gleichgewichteten Renditen; bei wertgewichteten Dezilen sind Dp und Op insignifikant.

### 2.5 Fama/French (2016), Five-Factor Model (nur Abstract/Digest)
- Abstract-Aussage (Suchergebnis): Negative RMW- und CMA-Steigungen (wie bei unprofitablen Firmen, die aggressiv investieren) erklaeren die niedrigen Durchschnittsrenditen von Hoch-Beta-, Grossemittenten- und Hoch-Volatilitaets-Aktien; Rueckkaeufer haben hohe Renditen, weil ihre Renditen positiv auf RMW und CMA laden. CFA-Digest: Das FF5-Modell erklaert die Beta-, NI- und Volatilitaets-Anomalien, nicht aber Accruals und Momentum. Stichprobe Juli 1963 bis Dezember 2014.

### 2.6 Hou/Xue/Zhang (NBER w23394, gelesen)
- Stichprobe Januar 1967 bis Dezember 2014; Finanzfirmen und Firmen mit negativem Buchwert ausgeschlossen; NYSE-Breakpoints, wertgewichtete Dezile. Gesamtbefund: 286 von 447 Anomalien (64 %) insignifikant bei t-Hurde 1,96; 380 (85 %) bei t = 3 (aus Suchzusammenfassung; im PDF nicht erneut nachgezaehlt).
- Abschnitt 3.2.2: Dividendenrendite (Dp) und Payout Yield (Op) sind in jaehrlichen und allen monatlichen Sorts insignifikant. (Text gelesen.)
- Abschnitt 3.2.3: Net External Finance (Nxf) und Net Equity Finance (Nef) verdienen im Schnitt -0,27 % und -0,17 % pro Monat (t = -1,44 und -0,86), also insignifikant, im Vergleich zu 15,5 % (t = 5,7) bzw. 11,2 % (t = 3,82) pro Jahr bei Bradshaw/Richardson/Sloan (2006) mit NYSE-AMEX-NASDAQ-Breakpoints und gleichgewichteten Renditen. (Text gelesen.)
- Abschnitt 3.3 (q-Faktor): Composite Equity Issuance (Cei): -0,56 %/Monat (t = -3,16), q-Alpha -0,24 % (t = -1,85), Investment-Faktor-Ladung -1,04 (t = -13,74), ROE-Faktor-Ladung -0,12 (t = -1,57). (Text gelesen.) Das heisst: erklaert durch den Investment-Faktor.
- Anhang A.3.10: HXZ-Nsi = ln(Aktien Geschaeftsjahresende t-1 / Aktien Geschaeftsjahresende t-2); Ende Juni Sort in 10 Portfolios: 2 negative, 1 Null, 7 positive; Haltedauer Juli bis Juni. (Text gelesen.)
- Anhang A.2.16: Nop = (Dividenden Compustat DVC plus Rueckkaeufe PRSTKC plus Reduktion Vorzugsaktien PSTKRV minus Emissionen SSTK minus Anstieg PSTKRV) / Marktkapitalisierung Dezember t-1; Firmen mit nichtpositiven Total Payouts (bzw. Null-Netto-Payouts) ausgeschlossen; Sorts Ende Juni, Portfolios ab Juli 1972 (Daten zu Kaeufen/Verkaeufen von Aktien starten 1971). (Text gelesen.)
- Tabelle 4 (Zeilen aus verunstaltetem pdftotext-Layout, Spaltenzuordnung inferiert und gegen Cei gegengeprueft, das mit dem Fliesstext uebereinstimmt): Nsi (Spalte 79): High-minus-Low -0,66 %/Monat (t = -4,45), q-Alpha -0,29 % (t = -2,19), Investment-Ladung -0,67 (t = -7,67). Nop (Spalte 53): +0,65 %/Monat (t = 3,36), q-Alpha +0,36 % (t = 2,41). Diese zwei Zahlenpaare sind inferiert, nicht aus Fliesstext. VOR VERWENDUNG IN EINER ENTSCHEIDUNG im Original-PDF (NBER w23394, Tabelle 4) gegenpruefen.

## 3. Strategien (nach erwarteter Robustheit)

Gemeinsame Annahmen: Die French-Daten sind Monatsrenditen von Portfolios, die jedes Jahr Ende Juni neu sortiert werden (NI nutzt Aktienzahlen aus Geschaeftsjahresenden t-2 und t-1). Weil Fundamentaldaten mit Verzug veroeffentlicht werden, enthaelt die French-Konstruktion einen Informationsabstand; die Haltedauer beginnt im Juli. Ein Live-Nachbau der Sortierung ist mit Gratis-Daten nicht sauber moeglich (Aktienzahlen-Historie ueber yfinance unzuverlaessig); die French-Strategien sind deshalb Research-Replikationen, kein direkt handelbarer Algorithmus.

### Strategie 1: NI-Ausschluss-Screen (Markt ohne oberstes Emissionsquintil), long-only

Idee: Nur die robuste Seite des Effekts nutzen. Fama/French (2008): Nur das oberste Emissionsquintil hat verlaesslich negative abnormale Renditen; McLean et al.: international treibt die Emissionsseite den Effekt.

Regel (Pseudocode):
```
Daten: Ken French "Portfolios_Formed_on_NI" (monatlich, VW-Renditen; falls vorhanden zusaetzlich Anzahl Firmen und
       Durchschnittsgroesse je Zelle), Zeitraum 1963-07 bis letzter Monat.
PRUEFEN beim ersten Einlesen: (a) Spaltennamen; (b) ob die Quintile ueber alle Aktien oder nur ueber positive NI gebildet sind;
       (c) ob Anzahl Firmen und Durchschnittsgroesse enthalten sind. Verwende genau EINE sich ausschliessende Zerlegung
       (z. B. {NI<0, NI=0, 5 Quintile der positiven NI} oder {5 Quintile ueber alle}); Kontrolle: Summe der Gewichte gleich
       Gesamtmarkt (Vergleich zur Summe ueber alle Zellen).
Fuer jeden Monat m:
    fuer jede Zelle k:  w_k(m) = AnzahlFirmen_k(m-1) * Durchschnittsgroesse_k(m-1)     # Vormonats-Gewichte, kein Look-ahead
                        (falls Block fehlt: w_k konstant als Marktanteil der Zelle je Juni-Formierung approximieren; dann als Naeherung kennzeichnen)
    Hi = Zelle mit der hoechsten Emission (oberstes Quintil)
    R_screen(m) = SUM_{k != Hi} w_k(m) * R_VW_k(m) / SUM_{k != Hi} w_k(m)
    R_mkt(m)    = SUM_{alle k} w_k(m) * R_VW_k(m) / SUM_{alle k} w_k(m)
    aktiv(m)    = R_screen(m) - R_mkt(m)
Rebalancing: monatlich innerhalb der Zellen (so liefert French die Daten); echte Sortierung jaehrlich Ende Juni.
Ausfuehrung (Live-Idee): Signal (NI je Aktie) nach Geschaeftsjahres-Berichten bis Ende Juni t kennbar, Handel frueestens am ersten Handelstag nach dem Juni-Schlusskurs (also Juli).
Auswertung: aktiv(m) gegen FF5+UMD regressieren (siehe Strategie 2), Teilperioden 1963-07..2005-12, 2008-07..heute.
```
Erwartung: klein. Aus Fama/French (2008) ist die erwartete Aktivrendite des Ausschlusses nicht ableitbar (keine Marktanteil-Zahl fuer das oberste Quintil gelesen: nicht gefunden). Wenn Hi-Quintil nur ca. 1/5 der Firmen aber kleine Marktanteile hat, ist der Ausschluss mechanisch fast marktneutral; der Nutzen zeigt sich als kleine positive Aktivrendite und kleine Tracking-Error.

### Strategie 2: NI-Long-Short auf Faktor-Ebene mit Spanning-Test gegen FF5+Momentum (Diagnose/Entscheidungs-Gate)

Regel (Pseudocode):
```
Daten (alle gratis):
  Ken French "Portfolios_Formed_on_NI" (monatlich, VW-Renditen)                   ab 1963-07
  Ken French "F-F_Research_Data_5_Factors_2x3" (Mkt-RF, SMB, HML, RMW, CMA, RF)   ab 1963-07   (Dateiname aus Gedaechtnis, nicht geprueft)
  Ken French "F-F_Momentum_Factor" (UMD)                                          ab 1927       (Dateiname aus Gedaechtnis, nicht geprueft)
Long  = Zelle "NI<0" (Netto-Rueckkaeufer), Short = Zelle mit der hoechsten Emission (Hi-Quintil)
LS(m) = R_VW_long(m) - R_VW_short(m)                              # brutto, kein Kostenabzug
Regression: LS(m) = a + b1*MktRF + b2*SMB + b3*HML + b4*RMW + b5*CMA + b6*UMD + e(m)
            t-Werte mit Newey-West-HAC (6 Lags)
Stichproben: voll (1963-07..letzter Monat); 1963-07..2005-12 (Fama/French-Fenster); 2008-07..letzter Monat (nach Pontiff/Woodgate-Publikation, Apr 2008).
Gegenprobe: dieselbe Regression mit LS = R(NI<0) - R(Mkt) (Long-only-Aktivrendite).
Entscheidungsregel: NI wird als eigener Baustein NUR aufgenommen, wenn
   (1) Alpha a (voll) mit t >= 3,0 UND
   (2) Alpha in 2008-07..heute positiv mit t >= 1,65 UND
   (3) Alpha nach 0,50 % p.a. pauschalen Zusatzkosten fuer Long-only-Umsetzung noch > 0.
   Sonst: als CMA/RMW-Exposition verbucht, kein neuer Eintrag (Duplikat zu Quality/Value).
Ausfuehrung: reine Analyse; kein Handel.
Beispielcode (ungetestet; Datenset-Namen via pandas_datareader.famafrench.get_available_datasets() pruefen):
   import pandas_datareader.data as web
   ni  = web.DataReader('Portfolios_Formed_on_NI', 'famafrench', start='1963-07')[0]
   ff5 = web.DataReader('F-F_Research_Data_5_Factors_2x3', 'famafrench', start='1963-07')[0]
   mom = web.DataReader('F-F_Momentum_Factor', 'famafrench', start='1963-07')[0]
   # Spaltennamen von ni inspizieren; Renditen sind in Prozent; Zeitindex PeriodIndex('M')
```
Evidenz: FF2008 Hedge -0,54..-0,71 %/Monat (t > 4,25); HXZ -0,66 %/Monat (t = -4,45) mit q-Alpha -0,29 (t = -2,19); FF2016: durch FF5 erklaert. Erwartung: Alpha gegen FF5 nahe null bzw. nicht signifikant, besonders nach 2008.

### Strategie 3: Net-Payout-Proxy (Komposit aus French-D/P- und NI-Portfolios)

Idee: Der Net Payout Yield = Dividenden + Rueckkaeufe - Emissionen. Echte Nop-Portfolios sind mit Gratis-Daten nicht verfuegbar (nicht auf der French-Seite). Naeherung: Mittelwert aus einem Dividendenrenditen-Spread und einem Emissions-Spread.

Regel (Pseudocode):
```
Daten: Ken French "Portfolios_Formed_on_D-P" (VW, monatlich) und "Portfolios_Formed_on_NI" (VW, monatlich); ab 1963-07.
       (D/P: laut Bibliothek univariate Sorts; auch eine ex-Dividenden-Variante "Portfolios_Formed_on_D-P_Wout_Div" existiert, die statt Gesamtrendite die Rendite ohne Dividenden liefert.)
PRUEFEN: Spaltenstruktur und ob eine "Zero"-Zelle (Nicht-Zahler) vorhanden ist; Nicht-Zahler NICHT in den Long-Leg.
DP_LS(m) = R_VW[hoechstes D/P-Quintil](m) - R_VW[niedrigstes D/P-Quintil ohne Nicht-Zahler](m)
NI_LS(m) = R_VW["NI<0"](m) - R_VW[Hi-Emissions-Quintil](m)
PAYOUT_PROXY(m) = 0.5 * DP_LS(m) + 0.5 * NI_LS(m)
Rebalancing: jaehrlich Ende Juni (French), Monatsrenditen; Ausfuehrung Juli.
Test: wie Strategie 2 (FF5+UMD, Newey-West, Teilstichproben). Zusatz: Regression von PAYOUT_PROXY auf NI_LS allein: bringt der D/P-Teil etwas dazu?
```
Evidenz: HXZ (Op und Dp insignifikant; Nop +0,65 %/Monat, t = 3,36, q-Alpha +0,36 mit t = 2,41, inferiert). Das legt nahe: der Emissionsteil traegt den Effekt, der Dividendenteil fuegt wenig hinzu; der Proxy ist wahrscheinlich nicht besser als NI_LS allein.

### Strategie 4: Shareholder-Yield-/Buyback-ETFs gegen S&P 500 (handelbarer Forschungsproxy)

Regel (Pseudocode):
```
Daten (yfinance, auto_adjust=True, Total Return):
  SYLD  Cambria Shareholder Yield ETF   Auflage laut Gedaechtnis Mai 2013 (nicht verifiziert).
        Laut Suchsnippet: ca. 100 US-Titel, Gleichgewicht, quartalsweises Rebalancing, TER 0,59 %,
        vor 26.03.2018 aktiv gemanagt, bis 01.06.2020 mit Cambria-Shareholder-Yield-Index (Fondsseite nicht geoeffnet).
  PKW   Invesco BuyBack Achievers ETF   Auflage laut Gedaechtnis Dez 2006 (nicht verifiziert).
  SDY   SPDR S&P Dividend ETF           Auflage laut Gedaechtnis Nov 2005 (nicht verifiziert).
  SPY   Benchmark  (ab 1993-01-29, aus Gedaechtnis)
  RSP   Gleichgewichteter S&P 500 (Kontrolle fuer Gleichgewichtungs-Effekt; Auflage 2003, aus Gedaechtnis)
  VYM, IWD Kontrollen (Dividenden-/Value-ETF)
Portfolio P = 1/3 SYLD + 1/3 PKW + 1/3 SDY, monatlich auf Gleichgewicht zurueckgesetzt (letzter Handelstag des Monats, Ausfuehrung Schlusskurs naechster Handelstag).
Aktivrendite A(m) = R_P(m) - R_SPY(m)   (TER ist in den ETF-Renditen enthalten)
Regression: A(m) = a + b1*MktRF + b2*SMB + b3*HML + b4*RMW + b5*CMA + b6*UMD + e(m), HAC(6)
Zweite Regression: P gegen RSP (statt SPY), um Gleichgewichts-/Mid-Cap-Tilt zu neutralisieren.
Entscheidung: Nur adoptieren, wenn a (nach TER) > 0 mit t >= 2 ueber mindestens 10 Jahre gemeinsame Historie UND Max-Drawdown-Abstand zu SPY akzeptabel.
```
Erwartung (ehrlich): Kein signifikantes Alpha nach TER. Gruende: kurze Historie (SYLD ab ca. 2013), Value-/Size-Tilts, TER von 0,35-0,60 %, Fonds sind keine reinen Payout-Portfolios. Hinweis aus Sekundaerquelle (Suchsnippet): Ein Backtest 2001-2013 fand die obersten 20 % nach Shareholder Yield bei 9,94 % p.a., die obersten 20 % nach Dividendenrendite bei 9,95 % p.a. und den Markt bei 5,67 % p.a.; mit Fabers schuldeninklusiver Definition 10,04 %. Schlussfolgerung des Autors: Debt Paydown fuegt wenig hinzu. Einzelne kurze Quelle, nicht belastbar.

### Strategie 5: Dividendenrendite-Tilt ueber UCITS-Dividenden-ETFs (Negativ-Eintrag)

Regel (Pseudocode):
```
Idee: Echtbetrieb in der EU mit UCITS-Dividenden-ETFs statt US-ETFs.
Kandidaten (aus Gedaechtnis, NICHT verifiziert; Yahoo-Abdeckung und Auflagedaten vor Verwendung pruefen):
  VHYL.L  Vanguard FTSE All-World High Dividend Yield UCITS
  ISPA.DE iShares STOXX Global Select Dividend 100 UCITS (DE)
Benchmark: gleichwertiger Welt-ETF (z. B. VWCE.DE/IWDA.AS; Ticker aus Gedaechtnis).
Allokation: 100 % Dividenden-ETF vs 100 % Welt-ETF; Rebalancing keins (Buy&Hold).
Test wie Strategie 4 (aber ohne Ken-French-US-Faktoren; besser Ken French "Developed" bzw. "Global" Faktoren: Datenverfuegbarkeit nicht geprueft).
```
Evidenz: Dividendenrendite allein ist in HXZ wertgewichtet insignifikant. Dividenden-ETFs sind im Kern Value-/Low-Vol-Tilts. Als Payout-Faktor-Exposure ist das KEIN Beleg, sondern ein Negativ-Eintrag: nach Kosten kein erwarteter Payout-Edge.

## 4. Nachpublikations-Verfall, Kosten, Tail-Risiken

- Zeitliche Instabilitaet im Original: Kein NI-Effekt 1926-1962 laut Pontiff/Woodgate/FF2008. Das spricht gegen eine stabile Risikopraemie.
- Nachpublikation: Suchsnippet (nicht verifiziert) zu McLean/Pontiff (2016): ca. -50 % nach Publikation, gepoolt ueber viele Anomalien. Suchsnippet zu Calluzzo/Moneta/Topaloglu: Net Stock Issues gehoert zu 14 untersuchten Anomalien, die Post-Publikations-Rendite sank gepoolt auf durchschnittlich 1,05 %/Monat (32 % relativ), keine NI-spezifische Zahl gefunden. Fuer NI allein habe ich keine Post-Publikations-Schaetzung gelesen (nicht gefunden). Strategie 2 liefert die Spezifikation, um das selbst zu messen.
- Strenge Replikation: HXZ zeigen, dass Dp/Op/Nxf/Nef bei wertgewichteten NYSE-Dezilen insignifikant sind; NSI und Cei bleiben signifikant, werden aber vom Investment-Faktor absorbiert.
- Kosten: French-Renditen sind brutto. Die Short-Seite ist in kleinen Titeln teuer. Die Fonds-Proxies (SYLD TER 0,59 % laut Suchsnippet) haben Kosten in der Groessenordnung der erwarteten Prämie.
- Tail-Risiken: Concentrated Value-/Size-Tilts (Dividenden-/Buyback-Fonds sind zyklisch und finanzlastig); Rueckkaeufe sind prozyklisch und werden in Krisen gestrichen (2008-09, 2020). Das ist eine plausible Hypothese, in diesem Lauf nicht mit Daten geprueft.
- Datenhygiene: Die Namen der Spalten in den French-Dateien und die Aufteilung der Quintile muessen beim ersten Einlesen geprueft werden; die Detailseite nennt nur "NI<0, NI=0, quintiles, deciles" und gibt keine Gewichtung an.

## 5. Offene Punkte / naechste Schritte

1. Strategie 2 ausfuehren (French-NI-Datei laden, FF5+UMD-Regression; ca. 10 Zeilen Code). Das ist die einzige belastbare Antwort auf die Kernfrage; bis dahin gilt "wahrscheinlich Duplikat".
2. HXZ-Tabelle 4 (Nsi, Nop) im Original-PDF gegenpruefen (Zellen-Zuordnung inferiert).
3. Fama/French (2016) Volltext lesen, um die NI-Alphas und RMW/CMA-Ladungen in Zahlen zu haben (nur Abstract gelesen).
4. Pruefen, ob Chen/Zimmermann (Open Source Asset Pricing) fertige Net-Share-Issuance-/Payout-Signale gratis bereitstellen (nicht abgerufen).
5. Yahoo-Startdaten fuer SYLD/PKW/SDY/RSP und UCITS-Ticker mit yfinance verifizieren (Datumsangaben oben stammen aus dem Gedaechtnis).
