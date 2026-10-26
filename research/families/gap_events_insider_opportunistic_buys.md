# Familie (Nachrecherche): Insider-Käufe, Opportunistic vs. Routine, SEC Form 4

Stand der Recherche: 2026-10-12. Budget: 15 Web-Abrufe (7 WebSearch + 8 WebFetch), Liste in Abschnitt 1. Dazu lokale Prüfungen (Yahoo-Datenstarts, Yahoo-Lücken bei delisteten Titeln) und zwei per WebFetch gespeicherte PDFs plus das NBER-PDF, die ich lokal mit pdftotext komplett lesen konnte.

Kennzeichnung der Belegstärke:
- **[GELESEN]** = Text der Seite bzw. des PDF wurde abgerufen und gesehen (PDFs: lokal mit pdftotext).
- **[SNIPPET]** = nur Zusammenfassung aus einem Suchergebnis gesehen, Quelle selbst NICHT geöffnet. Zahlen daraus sind unverifiziert.
- **[LOKAL GEPRÜFT]** = per Skript gegen die echte Datenquelle getestet.
- **[GEDÄCHTNIS]** = aus meinem Wissen, in dieser Sitzung nicht geprüft.
- **[ANNAHME]** = Designentscheidung von mir (Parameter, die in keiner Quelle stehen). Jede davon zählt beim Mehrfachtest mit.
Was ich nicht gefunden habe, steht ausdrücklich als "nicht gefunden".

## 0. Kurzfazit (ehrlich)

1. **Die Datenlücke aus der Kritik ist kleiner als befürchtet.** Die SEC-Seite nennt als Abdeckung "January 2006 - September 2026" [GELESEN], die Readme sagt "XML data submitted from January 2006 through current period" [GELESEN]. Die data.gov-Liste mit 2019Q2 als Start war offenbar unvollständig oder veraltet. ZIPs selbst habe ich NICHT heruntergeladen (Download braucht Freigabe von Nick), die Existenz der 2006er-Dateien ist also nur aus der Seitenliste belegt. Mit 2006er Start ist die Routine-Klassifikation (3 Jahre Historie) ab **Januar 2009** möglich, die Testperiode **2009 bis 2026 (ca. 17,7 Jahre, ca. 213 Monate) liegt komplett nach der Veröffentlichung** (NBER-WP 2010, JF 2012) und komplett nach der 2-Tage-Meldepflicht (seit 2002). Das ist ein echter Out-of-Sample-Test.
2. **Die Rohsignale sind real, aber kurzlebig und in kleinen Titeln.** Neuere Daten (Blog-Studie 2022 bis Juni 2026, N=7.405 Signale) zeigen nach Filing +0,53 % am ersten Handelstag (Open bis Close) und +1,0 % über 5 Tage (jeweils gegen SPY, vor Kosten), aber 21 und 63 Tage sind statistisch nicht von null zu unterscheiden. Eine arXiv-Studie zu Microcaps (2018 bis 2024) sagt: Reaktion dauert 2 bis 3 Handelstage, kein signifikantes Alpha, wenn man den ersten Tag auslässt. Das heißt: Wer erst zum nächsten Open nach dem Filing einsteigt und länger hält, sieht vermutlich nur einen Bruchteil des publizierten Effekts.
3. **Die Routine/Opportunistic-Trennung bringt long-only weniger, als die Schlagzeile (82 Bp) suggeriert.** Die 82 Bp sind ein Long-Short-Wert (Opportunistic Buys minus Opportunistic Sells, wertgewichtet). Die Hälfte der Verbesserung kommt laut den Autoren von den Verkäufen (Short-Seite, für Nick nicht umsetzbar). Long-only Opportunistic Buys: 5-Faktor-Alpha **+72 Bp/Monat wertgewichtet (t=2,27)** und **+158 Bp/Monat gleichgewichtet (t=7,03)**. Aber auch Routine Buys haben gleichgewichtet **+87 Bp (t=5,00)**; nur wertgewichtet sind sie null (+9 Bp, t=0,34). Der Effekt "Insider-Käufe schlagen den Markt" steckt gleichgewichtet also schon in den Routine-Käufen; die Klassifikation addiert dort ca. 70 Bp.
4. **Ali & Hirshleifer (JFE 2017) behaupten, ihr Maß schlägt das Cohen-Malloy-Pomorski-Maß.** Nach Kontrolle ihres Maßes sagt das Nicht-Routine-Maß keine Renditen mehr voraus (Autorenangabe, Stichprobe 1986 bis 2014). Ihr Maß braucht aber Quartalszahlen-Termine (QEA-Daten), die es nicht sauber gratis gibt.
5. **Echter Showstopper im Gratis-Setup ist Survivorship plus Ticker-Wiederverwendung bei Yahoo** [LOKAL GEPRÜFT]: SIVB, FRC, JCP, LEH, WAMUQ, RAD, GTXI, ZNGA liefern leer. BBBY und SHLD liefern Daten, aber erst ab 2026-07-17 bzw. 2023-09-14, also eine andere Firma unter dem alten Kürzel. Insider-Käufe konzentrieren sich auf Problemfirmen (Einbruch, Kauf, Insolvenz). Die Verlierer fehlen, der Backtest ist nach oben verzerrt, und zwar genau dort, wo der Effekt sitzt.
6. **Erwartung:** Ein sauberer Gratis-Test kann (a) den Effekt nach Kosten bestätigen, (b) ihn als "nach Kosten nicht belastbar" einstufen oder (c) als "im Gratis-Setup nicht belastbar prüfbar" abbrechen, wenn der Anteil fehlender Kurse zu hoch ist. Alle drei Ausgänge sind laut Lab-Regeln gültig. Meine Prior: (b) oder (c) wahrscheinlicher als (a).

## 1. Abrufstatus (Transparenz)

| Nr | Typ | Quelle / Zweck | Status |
|---|---|---|---|
| 1 | WebSearch | Cohen/Malloy/Pomorski Überblick | ok, Snippets (Seiten HBS, Harvard, NBER, SSRN gelistet) |
| 2 | WebSearch | Replikation / Post-Publication-Decay Opportunistic/Routine | ok, Snippets; **keine direkte Replikation gefunden** |
| 3 | WebFetch | https://www.nber.org/papers/w16454.pdf | GELESEN (PDF gespeichert, lokal pdftotext, 1798 Zeilen) |
| 4 | WebFetch | https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets | GELESEN (Abdeckung 2006 bis 2026) |
| 5 | WebSearch | Ali & Hirshleifer "Opportunism as a firm and managerial trait" | ok, Snippets |
| 6 | WebFetch | https://www.sec.gov/files/insider_transactions_readme.pdf | GELESEN (PDF lokal pdftotext, 779 Zeilen) |
| 7 | WebFetch | alphaarchitect.com/following-opportunistic-insiders-earns-1-alpha/ | **FEHLGESCHLAGEN (HTTP 403)**, nicht gelesen |
| 8 | WebSearch | Insider-Kauf-Renditen nach SOX / Verfall | ok, Snippets (Brochet via Harvard-Forum, Hossain, QuantInsti) |
| 9 | WebFetch | https://blog.quantinsti.com/sec-form-4-insider-trading-python-event-study/ | GELESEN (Blog, kein Peer-Review) |
| 10 | WebFetch | AQR-PDF Ali & Hirshleifer (Opportunism.pdf) | GELESEN (PDF lokal pdftotext, 2444 Zeilen) |
| 11 | WebSearch | Lakonishok & Lee 2001, Jeng/Metrick/Zeckhauser | ok, Snippets (Abstracts über IDEAS/NBER/Wharton) |
| 12 | WebSearch | Cluster-Käufe, Alldredge & Blank | ok, Snippets; nennt arXiv 2602.06198 |
| 13 | WebFetch | https://arxiv.org/abs/2602.06198 (Zhao 2026) | GELESEN (Abstract-Seite, Version v2 vom 2026-09-24) |
| 14 | WebFetch | https://cxoadvisory.com/investing-expertise/evolving-informativeness-of-insider-trading | GELESEN (Zusammenfassung von Hossain 2010) |
| 15 | WebSearch (extended) | Post-2008-Anwendungen der CMP-Klassifikation | ok, Snippets; keine Replikation der Renditen gefunden |

Lokale Prüfungen (keine WebSearch/WebFetch, aber echte Netzzugriffe, [LOKAL GEPRÜFT]):
- Yahoo via yfinance 1.3.0 (Python311, isolierter Modus): Datenstarts der Benchmark-Ticker (Abschnitt 6).
- Yahoo-Abfrage für 14 bekannte delistete bzw. wiederverwendete Kürzel (Abschnitt 5).

## 2. Primärliteratur im Detail

### 2.1 Cohen, Malloy, Pomorski (2012), "Decoding Inside Information", Journal of Finance 67(3); NBER w16454 [GELESEN, Working-Paper-PDF]
- URLs: https://www.nber.org/papers/w16454.pdf , https://papers.ssrn.com/abstract=1692517 , https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.2012.01740.x
- **Daten:** Thomson-Reuters-Insider-Filings, Form 4, Januar 1986 bis Dezember 2007, nur offene Marktkäufe und -verkäufe (Optionsausübungen und private Transaktionen ausgeschlossen). Portfolios 1989 bis 2007. Verknüpft mit CRSP/Compustat.
- **Klassifikation (wörtlich nach Papier, Abschnitt II):** Insider braucht in jedem der drei vorangegangenen Jahre mindestens einen Trade, sonst wird er gar nicht klassifiziert. **Routine** = Trade im selben Kalendermonat in mindestens drei aufeinanderfolgenden Jahren. **Opportunistic** = alle anderen klassifizierten Insider. Klassifikation zu Beginn jedes Kalenderjahres, danach gilt sie für alle Trades des Jahres. Fußnote 9: Rückfenster von 1 bis 5 Jahren getestet, ähnliche Ergebnisse, 3 Jahre als Mitte ausgewiesen. Fußnote 10: strengere Definition (Monat plus gleiche Handelsgröße) liefert ähnliche Resultate.
- **Anteile:** 64 % der Käufe und 52 % der Verkäufe routine; 55 % aller Trades routine, 45 % opportunistic. Die klassifizierbare Stichprobe ist ca. ein Drittel aller Insider-Transaktionen, tendenziell größere Aktien, weniger Micro-Caps als in CRSP (Tabelle I, Abbildung 2).
- **Portfolio:** Firma kommt in Monat t+1 ins Opportunistic-Buy-Portfolio, wenn ein Insider in Monat t einen Opportunistic Buy platziert hat. Haltedauer ein Monat, monatliches Rebalancing. Gleich- und wertgewichtet. Konservativer Test (Anhang A4): Renditen vom 11. Tag t+1 bis 10. Tag t+2, Ergebnisse "virtually identical".
- **Ergebnisse Tabelle IV (5-Faktor-Alpha inkl. Liquiditätsfaktor, 1989 bis 2007).** Hinweis: Das pdftotext-Layout der Tabelle ist zerlegt; die Zuordnung der Spalten habe ich über die im Abstract genannten Zahlen (82 Bp, 180 Bp, 43 Bp) gegengeprüft.
  - Opportunistic Buys gleichgewichtet: **+158 Bp/Monat (t=7,03)**; wertgewichtet: **+72 Bp/Monat (t=2,27)**. Durchschnittliche Rohrendite des Portfolios: 2,33 % (EW) bzw. 1,79 % (VW) pro Monat, Monats-Std 4,95 % bzw. 5,96 %.
  - Routine Buys gleichgewichtet: +87 Bp (t=5,00); wertgewichtet: +9 Bp (t=0,34).
  - Opportunistic (Buys minus Sells): wertgewichtet **82 Bp/Monat (t=2,15; 9,8 % p.a.)**, gleichgewichtet 180 Bp (t=6,07; 21,6 % p.a.). Routine (Buys minus Sells): EW +43 Bp (t=1,73), VW -20 Bp laut Einleitung (t=-0,57).
  - Opportunistic Sells EW: -23 Bp (t=-1,30), nicht signifikant. Signifikant ist die Sell-Seite erst in der Differenz zu den Routine-Sells.
- **Aussage des Papers zur Struktur:** "Über die Hälfte" der Verbesserung durch die Klassifikation kommt von den Verkäufen. Rückgabe steigt rund 6 Monate nach dem Trade und bleibt dann (kein Umkehrmuster).
- **Robustheit laut Autoren:** gilt für große und kleine, hoch- und niedrigumsatzstarke Aktien; vor 2000 ähnlich (Fußnote 6); Anzahl opportunistischer Käufe trägt zusätzliche Information (1 Std-Abw. in Log-Anzahl = +35 Bp/Monat, t=4,56).
- **Meldeverzug im Sample:** Median 3 Tage zwischen Trade und Meldung; 10-Tages-Frist bis 2002, danach 2 Tage (Fußnote 7).
- **Nicht im Papier gefunden:** ob der Insider auf (Person) oder (Person, Firma) Ebene klassifiziert wird. Ich habe (Person, Firma) gewählt [ANNAHME].

### 2.2 Ali & Hirshleifer (2017), "Opportunism as a firm and managerial trait: Predicting insider trading profits and misconduct", JFE 126(3), 490-515 [GELESEN, AQR-PDF]
- URLs: https://www.aqr.com/-/media/AQR/Documents/AQR-Insight-Award/2018/Opportunism.pdf?sc_lang=en , https://ideas.repec.org/a/eee/jfinec/v126y2017i3p490-515.html
- **Idee:** Opportunistisch ist, wer in der Vergangenheit **vor Quartalszahlen (QEA)** profitabel gehandelt hat. Pre-QEA-Trade = Trade in den 21 Handelstagen vor der QEA, die letzten 2 Tage ausgenommen. Profit je Trade = Durchschnitt der marktbereinigten Tagesrenditen im 5-Tage-Fenster um den QEA-Termin. Durchschnittsprofit des Insiders = (Summe Profit der Käufe minus Summe Profit der Verkäufe) / (Anzahl Käufe + Verkäufe). Aggregation mehrerer Trades derselben Periode, Aggregate unter 5.000 USD ausgeschlossen. Quintil-Ranking zu Jahresbeginn, Q5 = opportunistisch. Erstes Ranking 1989 (3 Jahre Daten).
- **Portfolios:** Firma ist im Long-Portfolio, wenn ein Insider der Gruppe im Vormonat gekauft hat; Haltedauer 1 Monat; Aktienpreis unter 5 USD ausgeschlossen; nur Stammaktien. Stichprobe 1986 bis 2014 (Portfolios Jan 1989 bis Juni 2014).
- **Ergebnisse (4-Faktor-Alpha):** Q5 Long-Short wertgewichtet **1,12 %/Monat (p<0,01)**, gleichgewichtet 1,59 %. Nur-Long Q5: EW **1,24 %/Monat**, VW **0,59 %/Monat**. Alle Insider zusammen Long-Short nur 0,37 bis 0,50 % (VW). Konservative Bildung (Portfolio zum Schluss des 10. Tages des Monats t+1): EW 1,44 %, VW 1,11 % (Long-Short). Das Q5-Long-Portfolio hat im Schnitt nur **29 Aktien pro Monat**, das Short-Portfolio 85.
- **Der Median-Insider hat nur 1 Pre-QEA-Trade, 59 % haben nur einen** (Fußnote 4); 33 % der Insider haben mindestens einen.
- **Vergleich mit CMP:** "our opportunistic trading measure dominates the nonroutineness measure"; nach Kontrolle ihres Maßes sagt das CMP-Maß keine Renditen voraus. Das ist eine Autorenaussage in ihrem Papier, nicht unabhängig bestätigt.
- **Hilfreich für Nick:** Effekt gilt laut Autoren auch in größeren Firmen (wertgewichtet); Differenz Top-minus-Bottom wertgewichtet 0,94 %/Monat.
- **Implementierungsproblem:** QEA-Termine kommen aus Compustat. Gratis-Proxy siehe Strategie 3.

### 2.3 Weitere Quellen
- **Lakonishok & Lee (2001), "Are Insider Trades Informative?", RFS 14(1)** [SNIPPET]: https://ideas.repec.org/a/oup/rfinst/v14y2001i1p79-111.html . Stichprobe 1975 bis 1995; Informationsgehalt kommt von Käufen, nicht Verkäufen; Vorhersagekraft "driven by insider's ability to predict returns in smaller firms". Zahlen nicht gesehen.
- **Jeng, Metrick, Zeckhauser (2003), REStat 85(2)** [SNIPPET]: https://www.nber.org/papers/w6913 , https://rodneywhitecenter.wharton.upenn.edu/wp-content/uploads/2014/04/9919.pdf . Rendite, die Insider selbst verdienen (Performance-Evaluation-Sicht, nicht die Rendite eines Außenstehenden nach dem Filing). Zwei Fassungen widersprechen sich in der Zahl: Wharton-WP 1999 "mehr als 6 % pro Jahr" für Käufe, NBER-Fassung ca. 40 Bp/Monat (ca. 4,8 % p.a.); welche Fassung gedruckt wurde, habe ich nicht geprüft. Nach Suchergebnis kein signifikanter Unterschied Klein vs. Groß in der NBER-Fassung.
- **Seyhun (1998), Investment Intelligence from Insider Trading, MIT Press:** nicht abgerufen, nur als Startliteratur genannt. Keine Zahlen von mir.
- **Hossain (2010), "Has the Informativeness of Insider Filing Changed Post Sox?"**, gelesen über die Zusammenfassung von CXO Advisory [GELESEN, Zweitquelle]: https://cxoadvisory.com/investing-expertise/evolving-informativeness-of-insider-trading . 42.794 Form-4-Filings, Jan 1996 bis Mai 2009. Zwei-Tage-CAR ab Filing-Datum, Käufe: vor SOX 0,32 %, nach SOX **1,13 %**; Verkäufe -0,19 % bzw. -0,54 %; nach Kreditkrise Käufe 1,84 %. Rang des Insiders ist die wichtigste erklärende Variable; Größeneffekt "somewhat more pronounced for small firms", aber nicht signifikant. CXO weist selbst darauf hin: Bruttorenditen, Messung beginnt am Filing-Tag, daher nur teils handelbar. Das Paper selbst habe ich nicht geöffnet.
- **Brochet (2010), SOX und Insider-Trades** [SNIPPET]: https://corpgov.law.harvard.edu/2009/10/30/sox-and-insider-trades/ . 3-Tage-CAR nach Kauf-Filings vor SOX ca. 0,59 %, nach SOX ca. 1,89 % (nur Snippet).
- **Alldredge & Blank (2019), "Do Insiders Cluster Trades With Colleagues? Evidence From Daily Insider Trading", Journal of Financial Research 42(2), 331-360** [SNIPPET]: https://ideas.repec.org/a/bla/jfnres/v42y2019i2p331-360.html . Geclusterte Käufe: Überrendite von über 2 % im Folgemonat (Snippet); WP-Fassung: 22 % der Käufe am selben Tag wie ein anderer Insider-Kauf, profitabler, wenn sie CEO/CFO folgen. Stichprobe, Gewichtung und Benchmark habe ich nicht gesehen.
- **Zhao (2026), "Insider Purchases Far Below the 52-Week High: Decomposing the Disclosure Reaction in Microcap Equities"**, arXiv 2602.06198 v2 [GELESEN, Abstract-Seite]: https://arxiv.org/abs/2602.06198 . Stichprobe 2018 bis 2024, Marktkapitalisierung 30 bis 500 Mio USD, 13.534 Kauf-Zeilen, 1.192 Emittenten, Code P. Erster-Tag-Überrendite 4,13 % (am weitesten unter 52-Wochen-Hoch) gegenüber 0,86 % (nahe Hoch); "The reaction lasts two to three sessions"; **29-Tage-Drift t=1,70 (unpräzise), Kalenderzeit-Portfolio, das den ersten Tag auslässt, "earns no significant alpha"**. v2 zieht frühere Behauptungen (Run-up, Klassifikator-Überlegenheit, Priorität) zurück. Einzelautor-Preprint, nicht begutachtet. Kosten, Survivorship und Datenquelle stehen NICHT auf der Abstract-Seite.
- **QuantInsti-Blog (2026), "SEC Form 4 Insider Purchases in Python: A Filing-Date Event Study with Free EDGAR Data"** [GELESEN, Blog, kein Peer-Review]: https://blog.quantinsti.com/sec-form-4-insider-trading-python-event-study/ . Form 4 vom 2022-01-01 bis 2026-06-30, Code P, nur Originale (kein 4/A), nur Stammaktien, nur Officer in Kernrollen, mindestens 10.000 USD, Fill-Preis im Band 0,5x bis 2,0x des nominellen Schlusses, 7.406 Emittent-Tag-Signale. Einstieg: erste SPY-Handelssitzung nach Filing-Datum, Next-Open. Ergebnis (bereinigt gegen SPY, zweiseitig geclustert): CAR 1 Sitzung **+0,534 % (t=6,46)**; 5 Sitzungen **+1,009 % (t=5,05)**; 21 Sitzungen +0,980 % (t=1,68, KI -0,19 % bis +2,15 %); 63 Sitzungen CAR +1,103 % (t=1,19), BHAR +0,104 % (t=0,11), Median-BHAR 63 Tage -3,605 %. Der Autor sagt selbst: kein survivorship-freies Universum, 1.888 Komponenten ohne Preis (nicht zufällig fehlend), keine Kosten- oder Kapazitätsmodellierung, keine Mehrfachtest-Korrektur.

### 2.4 Post-2008-Anwendungen der CMP-Klassifikation (nur Snippets, nicht geöffnet)
Ergebnis der Suche: **keine unabhängige Replikation der Renditen nach 2007 gefunden.** Gefunden (nur Titel/Snippet, [SNIPPET]):
- BIS Working Paper 697, "Are Banks Opaque? Evidence from Insider Trading": https://www.bis.org/publ/work697.pdf (Trades Januar 1990 bis Dezember 2015, nutzt den Algorithmus).
- Das (2025), "Opportunistic Insider Trading During the COVID-19 Pandemic", FMII: https://onlinelibrary.wiley.com/doi/10.1111/fmii.12213
- Gangopadhyay & Yook (2022), "Profits to Opportunistic Insider Trading Before and After the Dodd-Frank Act of 2010", J. Financial Regulation and Compliance: nur im Literaturverzeichnis gesehen, keine URL, Inhalt ungeprüft.
- Görgen/Renneboog/Zhao, "Insider Trading and Networked Directors" (ECGI WP): https://www.ecgi.global/sites/default/files/working_papers/documents/finalgoergenrenneboogzhao1.pdf . Snippet: Anteil routine Trades stieg seit 2008 deutlich bis auf 15 % und bis 2012. Mehrdeutig, ungeprüft.
- Weitere Titel ohne Inhalt: "Insider trading patterns" (https://www.sciencedirect.com/science/article/abs/pii/S0929119920300985), "Mimicking insider trades" (https://pure-oai.bham.ac.uk/ws/portalfiles/portal/148211989/Mimicking_Insider_Trades.pdf), CRA Literature Watch Q2 2025 (https://www.crai.com/insights-events/publications/insider-trading-market-manipulation-literature-watch-q2-2025/).
- Allgemeiner Verfall: Quantpedia fasst Arbeiten zusammen, wonach in den USA ein verlässlicher Rückgang nach Publikation besteht und die Sharpe-Ratio neu publizierter Faktoren pro Jahr um ca. 5 % sinkt [SNIPPET, https://quantpedia.com/in-sample-vs-out-of-sample-analysis-of-trading-strategies/]. McLean & Pontiff (2016) ist die Standardreferenz [GEDÄCHTNIS, Zahlen nicht geprüft].
- Nicht gefunden: eine Arbeit, die CMP-Long-Only-Renditen mit EDGAR-Daten 2009 bis 2025 nachrechnet. Das ist genau der Test, den das Lab machen würde.

## 3. Datenlage Gratis-Setup

### 3.1 SEC DERA Insider Transactions Data Sets [GELESEN]
- Seite: https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets ; Readme: https://www.sec.gov/files/insider_transactions_readme.pdf
- **Abdeckung: "January 2006 - September 2026"**, vierteljährlich aktualisiert. Datenquelle: XML-Teil der Formulare 3, 4, 5, "as filed", inklusive Amendments, ohne Bereinigung. Die SEC garantiert keine Richtigkeit.
- Tabellen (tab-getrennt, UTF-8): SUBMISSION (Schlüssel ACCESSION_NUMBER; u. a. FILING_DATE, PERIOD_OF_REPORT, DOCUMENT_TYPE, ISSUERCIK, ISSUERNAME, ISSUERTRADINGSYMBOL, REMARKS), REPORTINGOWNER (RPTOWNERCIK, RPTOWNERNAME, RPTOWNER_RELATIONSHIP mit OFFICER/DIRECTOR/TENPERCENTOWNER/OTHER, RPTOWNER_TITLE), NONDERIV_TRANS (TRANS_DATE, TRANS_CODE, TRANS_SHARES, TRANS_PRICEPERSHARE, TRANS_ACQUIRED_DISP_CD, SHRS_OWND_FOLWNG_TRANS, TRANS_TIMELINESS E/L/leer, SECURITY_TITLE), NONDERIV_HOLDING, DERIV_TRANS, DERIV_HOLDING, FOOTNOTES, OWNER_SIGNATURE.
- **TRANS_CODE P = "Open market or private purchase of non-derivative or derivative security"** (Readme-Anhang 6.2). Wichtig: "private purchase" ist eingeschlossen, also können Käufe direkt vom Emittenten (Privatplatzierungen) im Code P stecken. Gegenmaßnahme in den Regeln: Preisband gegen Yahoo-Schlusskurs [ANNAHME, wie im QuantInsti-Blog].
- **FILING_DATE ist ein reines Datum (DD-MON-YYYY), ohne Uhrzeit.** Der Blog bestätigt: keine SEC-Acceptance-Timestamps. Konsequenz: frühester sicher handelbarer Zeitpunkt = Open des ersten Handelstages **nach** FILING_DATE. Das ist konservativ (verschenkt ggf. einen Intraday-Teil) und vermeidet Look-ahead.
- ISSUERTRADINGSYMBOL ist das Kürzel zum Filing-Zeitpunkt (Freitext, kann leer oder verändert sein), keine Garantie für Gleichheit mit dem heutigen Yahoo-Kürzel.
- Nicht in der Readme gesehen: Hinweis, ob mehrere Eigentümer in einer Einreichung (Gemeinschaftsfilings) mehrere REPORTINGOWNER-Zeilen erzeugen. Aus dem Schlüssel (ACCESSION_NUMBER, RPTOWNERCIK) folgt es; Deduplizierung nötig.
- Form 4/A (Korrekturen): ein eigener DOCUMENT_TYPE. In den Regeln werden Originale genutzt und 4/A ignoriert [ANNAHME]; das verliert einige Trades und kann Verzögerungen verbergen.
- Nicht geprüft: tatsächliche ZIP-Größen, Download-URL-Muster, Spalten-Namen im echten ZIP (Readme ja, ZIP nein).

### 3.2 Kurse: Yahoo via yfinance [LOKAL GEPRÜFT, 2026-10-12]
| Ticker | Zweck | Datenstart | Hinweis |
|---|---|---|---|
| SPY | Marktbenchmark | 1993-01-29 | |
| IWM | Russell 2000 Benchmark | 2000-05-26 | |
| IJR | S&P SmallCap 600 | 2000-05-26 | |
| IWC | iShares Micro-Cap | 2005-08-16 | |
| VB | Vanguard Small-Cap | 2004-01-30 | |
| IWN / IWO | Russell 2000 Value / Growth | 2000-07-28 | |
| XSMO, XSVM | Invesco S&P SmallCap Momentum / Value | 2005-03-03 | |
| ^RUT | Russell 2000 Index (ohne Dividenden) | 1987-09-10 | Preisindex |
| ^GSPC | S&P 500 Index | 1927-12-30 | Preisindex |
| ^IRX | 13-Wochen-T-Bill-Zins | 1960-01-04 | |
| SLY | | leer | delistet/umbenannt |
Für EU-Kleinanleger sind SPY/IWM wegen PRIIPs oft nicht direkt kaufbar; für Live-Betrieb UCITS-Äquivalente prüfen (nicht geprüft). Als **Benchmark im Test** reichen die US-Ticker.

### 3.3 Ken French (Faktor-Regressionen) [Namen aus Lab-Dateien übernommen, dort LOKAL GEPRÜFT]
`F-F_Research_Data_5_Factors_2x3` (monatlich ab 1963-07, Spalten Mkt-RF, SMB, HML, RMW, CMA, RF), `F-F_Momentum_Factor` (monatlich ab 1927-01), jeweils auch als `_daily`. Das Papier nutzt Carhart plus Liquiditätsfaktor; einen Liquiditätsfaktor (Pastor-Stambaugh) gibt es nicht auf der Gratis-Liste, daher Alpha gegen FF5 + Mom als Ersatz [ANNAHME].

## 4. Strategien (nach erwarteter Robustheit sortiert)

Gemeinsame Daten- und Ausführungsregeln (gelten für alle):
- **Quellen:** DERA ZIPs 2006Q1 bis 2026Q3; Join NONDERIV_TRANS, SUBMISSION, REPORTINGOWNER über ACCESSION_NUMBER.
- **Filter Transaktion:** DOCUMENT_TYPE == "4" (Original), TRANS_CODE == "P" bzw. "S" (S nur für Historie), SECURITY_TITLE enthält "common" (case-insensitive), TRANS_SHARES > 0, TRANS_PRICEPERSHARE > 0, Wert = Shares x Preis, kein Gemeinschaftsfiling (mehr als ein RPTOWNERCIK pro ACCESSION_NUMBER: Zeilen einzeln zählen, aber Trade nur einmal) [ANNAHME].
- **Zeitpunkt:** Information wird am Close von FILING_DATE als bekannt unterstellt (konservativ, weil ohne Uhrzeit). Handel frühestens zum **Open des ersten Handelstages nach FILING_DATE**. Signal wird am Schlusskurs bestimmt, Trade nächster Handelstag.
- **Kurse:** yfinance `auto_adjust=True`, Open und Close. Ticker-Identitätsprüfung: Kurshistorie muss vor Signaldatum mindestens 252 Handelstage zurückreichen und darf im Fenster [Signal-30, Signal+Haltedauer] keine Lücke über 10 Handelstage haben (fängt Wiederverwendung wie BBBY/SHLD ab) [ANNAHME].
- **Preisband:** TRANS_PRICEPERSHARE muss zwischen 0,5x und 2,0x des Yahoo-Schlusskurses am TRANS_DATE liegen (Privatplatzierungen/Fehler raus) [ANNAHME, wie QuantInsti].
- **Liquiditätsfilter am Signaltag:** Close >= 5 USD (wie Ali/Hirshleifer) und 60-Tage-Durchschnitt von Close x Volumen >= 1 Mio USD [ANNAHME].
- **Kosten (pro Seite, vor Steuern) [ANNAHME, nicht aus Quelle]:** 40 Bp bei ADV 1 bis 5 Mio USD, 20 Bp bei ADV über 5 Mio USD. Zusätzliche Stresstest-Variante: doppelte Kosten.
- **Fehlende Kurse:** Anteil der Signale ohne verwendbare Yahoo-Zeitreihe je Jahr berichten. Wenn über 25 % der Signale eines Jahres fehlen: Jahr als "nicht belastbar" markieren. Stresstest: fehlende Signale bekommen die 5. Perzentil-Rendite der vorhandenen Signale desselben Monats [ANNAHME].
- **Benchmarks und Pflichtvergleiche:** IWM und IWC (Total Return aus Adj Close), gleichgewichtetes Zufallsportfolio aus denselben Liquiditätsfiltern ohne Insider-Signal (1.000 Ziehungen mit gleicher Anzahl Titel pro Monat), außerdem der "alle Insider-Käufe"-Korb und der "Routine-Käufe"-Korb mit denselben Filtern.
- **Steuer:** Abgeltungssteuer 26,375 % auf realisierte Gewinne, Verlustverrechnung innerhalb der Aktien (nicht mit Termingeschäften); bei monatlichem Umschlag fällt Steuer jährlich auf Netto an.

### Strategie 1: `cmp_opp_buys_monthly_liquid`
Cohen/Malloy/Pomorski-Long-only, monatlich, gleichgewichtet, mit Liquiditätsfilter.

```
# Klassifikation (jährlich)
trades = alle Zeilen mit TRANS_CODE in {P, S}, DOCUMENT_TYPE == "4", Stammaktie
key    = (RPTOWNERCIK, ISSUERCIK)
für Jahr Y in 2009..aktuell:
    for key:
        M[y] = Menge der Kalendermonate (1..12), in denen key mindestens einen Trade
               (Datum = TRANS_DATE) im Jahr y hatte, für y in {Y-3, Y-2, Y-1}
        eligible = M[Y-3], M[Y-2], M[Y-1] sind alle nicht leer
        routine  = eligible UND (M[Y-3] ∩ M[Y-2] ∩ M[Y-1]) nicht leer
        opport   = eligible UND NICHT routine
        # nicht eligible -> kein Signal
    Klassifikation gilt für alle Trades mit FILING_DATE im Jahr Y

# Monatssignal
D_t = letzter Handelstag von Monat t
S_t = { Emittent f : es existiert Kauf (TRANS_CODE == "P", TRANS_ACQUIRED_DISP_CD == "A",
        Wert >= 5.000 USD) von Insider key mit opport == True,
        FILING_DATE in (D_{t-1}, D_t] }
S_t = S_t gefiltert nach: Ticker-Identitätsprüfung, Preisband, Close(D_t) >= 5, ADV60$ >= 1 Mio

# Gewichtung und Ausführung
N = |S_t|
wenn N >= 10:  w_f = 1 / N
sonst:         w_f = 1 / 10 je Titel, Rest in BIL (oder Cash)
Kauf zum Open des ersten Handelstages nach D_t; Verkauf bzw. Rebalancing zum Open des
ersten Handelstages nach D_{t+1}; Monatsrendite je Titel = Open_ende / Open_start - 1
(adjustiert), Kosten pro Seite auf den gehandelten Anteil.

# Pflichtvergleiche, gleiche Regeln mit
#  (a) routine == True  (b) alle klassifizierten Käufe  (c) alle Käufe ohne Klassifikation (ab 2006)
```
- **Testperiode:** 2009-01 bis aktuell, in zwei Hälften berichten (2009 bis 2017, 2018 bis 2026). Hypothese vorab: Alpha (vs. FF5 + Mom, monatlich) > 0 UND Opportunistic-Korb schlägt Routine-Korb. Abbruchkriterium: Netto-Alpha nicht signifikant (t < 2) oder Differenz Opportunistic minus Routine nicht signifikant oder > 25 % Signale ohne Kurse.
- **Power-Überschlag [ANNAHME, Residual-Std 4,5 %/Monat]:** 213 Monate geben einen Standardfehler des Alphas von ca. 0,31 %/Monat; ein Alpha von 72 Bp hätte t≈2,3, ein auf die Hälfte geschrumpftes (36 Bp) nur t≈1,2. Das Lab kann einen Verfall um die Hälfte also statistisch kaum von null trennen.
- **Mit Insider-Eligibility ab 3 Jahren Historie** verliert man neue Insider, die oft informativ sind (Neuzugänge); das ist Design des Papers, kein Fehler.

### Strategie 2: `insider_cluster_officer_buys_21d`
Event-Strategie auf geclusterte Käufe mehrerer Insider (Officer beteiligt).

```
# Cluster-Definition (nur Informationen bis zum Signaltag)
Käufe = TRANS_CODE == "P", TRANS_ACQUIRED_DISP_CD == "A", Wert >= 5.000 USD, Stammaktie, Original-Form-4
Für Emittent f und Handelstag d (= FILING_DATE-Handelstag):
    bekannte Käufe K = alle Käufe mit FILING_DATE <= d
    Cluster, wenn es mindestens 2 verschiedene RPTOWNERCIK in K gibt, deren TRANS_DATE auf
    denselben oder aufeinanderfolgenden Handelstagen liegen, und mindestens einer davon
    RPTOWNER_RELATIONSHIP enthält "OFFICER"
    (reine TENPERCENTOWNER-Cluster zählen nicht)
Event-Tag e = erster Handelstag d, an dem die Cluster-Bedingung mit bekannten Filings erfüllt ist
Pro Emittent höchstens ein Event pro 63 Handelstage.

# Filter am Event-Tag: Ticker-Identität, Preisband, Close >= 5, ADV60$ >= 1 Mio

# Ausführung
Einstieg: Open des ersten Handelstages nach e
Ausstieg: Open des 22. Handelstages nach e (also 21 Handelstage Haltedauer)
Position: 1/20 des Gesamtkapitals je offenes Event (Cap 5 %), überschüssiges Kapital in BIL;
bei mehr als 20 offenen Events: 1/N gleichgewichtet
Kosten pro Seite wie oben. Tägliche Bewertung, Rebalancing nur bei Ein- und Ausstieg.
```
- **Hypothese vorab:** Netto-Alpha gegen IWM/FF5+Mom positiv und mittlere 21-Tage-Rendite der Events größer als die der Zufallsportfolios; Abbruch: Mittelwert der 21-Tage-Überrendite (Next-Open-Einstieg) < 2 x Kostenbetrag oder t < 2 (geclustert nach Emittent und Monat).
- **Mehrfachtest-Hinweis:** "5 Tage Fenster", "2 Insider", "Officer-Pflicht" sind meine Entscheidungen. Nur diese eine Variante testen und Variationen nur als Robustheitsbericht, nicht als Auswahl.
- **Die Quelle für die 2 %/Monat habe ich nur als Snippet gesehen.** Sie sagt nichts über Einstiegsverzug aus.

### Strategie 3: `ah_pre_qea_opportunist_buys`
Ali/Hirshleifer-Opportunismus, Long-only. **Daten nur mit Proxy.**

```
# QEA-Datum je Emittent und Quartal: (Gratis-Proxy, ungeprüft [GEDÄCHTNIS])
E = Filing-Datum des 8-K mit Item 2.02 ("Results of Operations") von EDGAR
    (submissions-Daten je CIK; Items-Feld je Filing). Alternative: yfinance Earnings-Dates
    (nur wenige Jahre, laut Lab-Notiz altdata.md unzuverlässig).

# Ranking (jährlich, 1. Januar Y, ab Y = 2012 für Evaluation)
Für jeden Trade (P oder S, TRANS_DATE, Wert) von key=(RPTOWNERCIK, ISSUERCIK) vor 1. Jan Y:
    Pre-QEA-Trade, wenn TRANS_DATE in [E-21, E-3] Handelstage; mehrere Trades derselben
    Periode zu einem Netto-Trade aggregieren (Käufer, wenn Shares gekauft > verkauft);
    Aggregate mit Wert < 5.000 USD verwerfen
    Profit_k = Mittel_{j=-2..+2} ( R_f,E+j - R_Markt,E+j )     # SPY als Marktproxy
AvgProfit(key) = ( Σ Profit_k über Käufe - Σ Profit_k über Verkäufe ) / (B + S)
Quintile über alle key mit mindestens einem Pre-QEA-Trade; Q5 = opportunistisch

# Signal und Ausführung identisch zu Strategie 1, nur Käufe von key in Q5
```
- **Warum nur ab 2012 evaluieren:** Ranking nutzt die gesamte Historie bis Jahresbeginn. Mit DERA ab 2006 hat das Ranking 2009 nur 3 Jahre Daten; das Papier hat im Schnitt nur 29 Aktien im Q5-Long-Portfolio bei vollen Daten. Ich erwarte 2009 bis 2011 eine sehr dünne Besetzung. Wenn monatlich weniger als 10 Titel im Signal sind, wird der Rest in Cash/BIL gehalten.
- **Ehrlich:** Das ist die Strategie mit den größten publizierten Zahlen (VW-Alpha Q5-Long 0,59 %/Monat, EW 1,24 %), aber auch die mit dem unsichersten Gratis-Datenpfad. Die Proxy-Qualität (8-K-Datum gleich Ergebnisdatum) ist nicht geprüft.
- **free_data_ok = false**, bis ein Test gezeigt hat, dass EDGAR-Proxy-Termine plausibel sind.

### Strategie 4: `insider_officer_buy_event_5d_shorthold`
Kurzhaltedauer-Event-Strategie. **Erwarteter Ausgang: funktioniert nach Kosten wahrscheinlich nicht.** Eintrag als Negativ-Test und Gegenprobe zum "Effekt sitzt in den ersten Tagen".

```
Event: Kauf (TRANS_CODE == "P", A), Stammaktie, Original-Form-4, RPTOWNER_RELATIONSHIP enthält "OFFICER",
       Wert >= 10.000 USD (an QuantInsti angelehnt), einmal pro Emittent und 10 Handelstage
Filter: Ticker-Identität, Preisband, Close >= 5, ADV60$ >= 1 Mio
Einstieg: Open des ersten Handelstages nach FILING_DATE
Ausstieg: Close des 5. Handelstages nach Einstiegstag (also 5 Sitzungen Haltedauer)
Position: 2 % des Kapitals je Event, maximal 25 gleichzeitige Positionen, Rest in BIL
Kosten pro Seite wie oben (20 bzw. 40 Bp)
```
- **Break-even-Rechnung (aus gelesenen Zahlen):** Brutto +1,009 % über 5 Sitzungen (Blog-Stichprobe, gegen SPY, vor Kosten). Bei 40 Bp pro Seite sind 80 Bp Round-Trip, übrig bleiben ca. 0,2 %; bei 60 Bp pro Seite (also 1,2 % Round-Trip) ist der Edge null. Die Kostenschätzung selbst ist [ANNAHME].
- **Fester Hinweis:** Zhao (2026) findet bei Microcaps ohne den ersten Tag kein signifikantes Alpha; der Blog findet am ersten Tag nach Filing (Open bis Close) noch +0,53 %. Beide Befunde kennen keine Kosten und keine delisteten Titel.
- **Zweck im Lab:** Prüfen, ob die Next-Open-Regel den Edge schon vor Kosten auffrisst. Ein klares "nach Kosten tot" ist ein verwertbares Ergebnis.

## 5. Realismus-Probleme im Detail

### 5.1 Survivorship und Ticker-Wiederverwendung bei Yahoo [LOKAL GEPRÜFT 2026-10-12]
Abfrage `Ticker(t).history(period="max")`:
- **Leer:** SIVB, FRC, JCP, LEH, WAMUQ, RAD, GTXI, ZNGA.
- **Falsche Firma unter altem Kürzel:** BBBY Datenstart 2026-07-17 (60 Handelstage), SHLD Datenstart 2023-09-14.
- **Lückenlos aber ohnehin überlebt:** LUMN (ab 1980), AMRN (ab 1993), PETS (ab 1999), CTRM (ab 2019).
Konsequenz: Ein Backtest auf Yahoo-Kursen verliert systematisch genau die Käufe vor einer Insolvenz oder Übernahme zu niedrigem Kurs (letzteres wäre Gewinn, ersteres Verlust). Die Richtung der Verzerrung ist nach oben (Verlierer fehlen), aber die Größe unbekannt. Gegenmaßnahme: Anteil fehlender Signale offenlegen und stressen (Abschnitt 4).

### 5.2 Veröffentlichung und Ausführung
- **Frist:** 2 Geschäftstage seit 2002 (CMP Fußnote 7); Median-Verzug im CMP-Sample 3 Tage, davor bis 10 Tage nach Monatsende.
- **Kein Zeitstempel in DERA:** Filing-Tag gilt als Ende des Tages; Einstieg frühestens am nächsten Open.
- **Erster-Tag-Reaktion fehlt dem Next-Open-Käufer teilweise:** Hossain (Zwei-Tage-CAR 1,13 %) misst ab Filing-Tag; Brochet (Snippet) 3-Tage-CAR 1,89 %. Davon ist ein Teil Tag 0 (Filing-Tag) und für Nick nicht erreichbar.
- **CMP-Kalendermonats-Portfolio** hält Titel durchschnittlich ca. 15 Tage nach Filing bis zum Einstieg (Signal Monatsende, Einstieg nächster Monatsanfang). Das ist konservativ, mindert die Edge aber stärker, wenn der Effekt kurzlebig ist.

### 5.3 Kosten und Steuern [ANNAHME, nirgends gemessen]
Spreads in Aktien mit 1 bis 5 Mio USD Tagesumsatz sind selten unter 30 bis 50 Bp (Daumenwert aus dem Gedächtnis, [GEDÄCHTNIS]); der Insider-Effekt sitzt laut Lakonishok/Lee in kleinen Firmen. In den Regeln habe ich Micro-Cap per ADV-Filter ausgeschlossen, damit kann der Effekt deutlich schrumpfen. Genau das ist eine Messung wert: Alpha je ADV-Terzil (nur berichten, nicht auswählen).

### 5.4 Tail-Risiken
Long-only in Small-/Micro-Caps hat Marktbeta ca. 1 (Benchmark IWM/IWC, nicht SPY, vergleichen), Einzelwert-Crashs von -50 % und mehr über einen Monat sind in dieser Gruppe häufig (Insider kaufen Einbrüche, Zhao). Marz 2020 und 2008/09 sind Härtetests (2009 ist Teil der Stichprobe nur, weil die Klassifikation erst dann startet; der Tiefpunkt März 2009 fällt in den Aufbau).

## 6. Offene Punkte / nächste Schritte (für Nick, nicht automatisch)

1. **Freigabe für Download nötig:** DERA-ZIPs (2006Q1 bis 2026Q3) laden, Struktur lokal prüfen (Spaltennamen, Zeilenzahl P-Käufe pro Jahr). Das ist ein Bruchteil von 1 GB; Größe nicht geprüft.
2. Prüfen, ob Anteil Signale ohne Yahoo-Kurse unter 25 % bleibt. Wenn nein: Ausgang (c) "im Gratis-Setup nicht belastbar prüfbar" dokumentieren und beenden.
3. Hypothesen in `docs/HYPOTHESEN.md` eintragen (vor Backtest), vor allem: H1 Strategie 1, H2 Strategie 2, Abbruchkriterien wie oben.
4. Mehrfachtest: 4 Strategien, mehrere Parameter, 3 Gewichtungen = deutlich über 10 Versuche. Deflated Sharpe nutzen.
5. Alpha Architect (Seite 403) und Autoren-Papiere (Lakonishok/Lee, Jeng et al., Alldredge/Blank, Brochet, Hossain) nur über Snippets bzw. Zweitquellen gesehen. Wenn eine dieser Zahlen in eine Entscheidung eingeht, Originale öffnen.
6. EU-Zugang: Handelbarkeit kleiner US-Titel über deutsche Broker nicht geprüft.
