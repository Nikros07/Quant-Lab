# Familie: Dual Momentum / Tactical Asset Allocation (TAA)

Stand der Recherche: 2026-10-11. Budget: ca. 15 Web-Abrufe, davon mehrere an 403/404 gescheitert (siehe "Abrufstatus").
Alle Zahlen unten stammen aus tatsaechlich abgerufenen Seiten/PDFs oder sind als "Suchsnippet" bzw. "aus Gedaechtnis" markiert.
Was ich nicht gefunden habe, steht ausdruecklich als "nicht gefunden".

## 0. Kurzfazit (ehrlich)

- Die gesamte Familie ist im Kern EINE Wette: Trendfolge (absolute Momentum) auf wenige liquide ETF-Klassen plus etwas relative Momentum. Die Strategien sind untereinander hoch korreliert. Fuenf Varianten testen heisst nicht fuenf unabhaengige Edges.
- Robusteste Kandidaten sind die einfachen, langsamen, breit diversifizierten Varianten (Faber 10-Monats-SMA auf 5 Klassen, PAA-G12). Die "aggressiven" Keller-Varianten (BAA-G4/T1, DAA mit 2-Asset-Canary) sind sehr stark in-sample selektiert (Keller sagt das im BAA-Paper selbst: Parameter "in-sample optimal auf K/IS") und haben mit Top1/Top2 hohe Konzentration und damit hohes Rebalance-Timing-Luck.
- Die publizierten Langfrist-Zahlen (1970-2022) beruhen auf Kellers eigenen ETF-Proxys vor ETF-Start. Diese Proxys sind NICHT gratis verfuegbar. Frei testbar ist nur die ETF-Aera (je nach Universum ab ca. 2008). Das ist ~18 Jahre inkl. nur einer grossen Krise (2008), plus 2020 und 2022.
- Unabhaengige Post-Publikations-Evidenz (OOS nach Veroeffentlichung, nach Kosten, nicht vom Autor) habe ich fuer die Keller-Strategien NICHT gefunden. Fuer GEM gibt es das Newfound-Fragilitaetsargument (Spezifikationsrisiko). Ein "funktioniert nach Kosten nicht mehr" konnte ich weder belegen noch widerlegen; das muss der eigene Backtest zeigen.
- Rebalance-Timing-Luck (Hoffstein/Faber/Braun) ist fuer jede dieser Strategien ein reales Problem: Ein einzelnes Monatsend-Rebalancing ist nur EINE Stichprobe des Ausfuehrungstags. Empfehlung: immer mit gestaffelten Tranchen (Sleeves) testen.

## 1. Abrufstatus (Transparenz)

| Quelle | Status |
|---|---|
| Keller, Bold Asset Allocation (SSRN 4166845), PDF ueber Mirror thechartist.com.au | ABGERUFEN und lokal mit pdftotext komplett gelesen (14 Seiten) |
| CXO Advisory Zusammenfassung zu DAA | ABGERUFEN (Sekundaerquelle ueber Keller/Keuning 2018) |
| Quantpedia "Asset Class Trend Following" (Faber) | ABGERUFEN (Sekundaerquelle ueber Faber SSRN 962461) |
| Newfound Blog "The Dumb Timing Luck of Smart Beta" (2019) | ABGERUFEN |
| Newfound Tag-Seite GEM mit Excerpt zu "Fragility Case Study: Dual Momentum GEM" (2019-01-14) | Tag-Seite ABGERUFEN, der Einzelpost selbst NICHT |
| SSRN-Abstractseite DAA/VAA (papers.ssrn.com) | 403, nicht abrufbar |
| Allocate Smartly DAA-Seite | 404 |
| Alpha Architect Antonacci-Seite | 403 |
| Advisor Perspectives "Global Equity Momentum: A Craftsman's Perspective" (2019) | 403 (zwei URLs), nicht gelesen |
| Antonacci "Risk Premia Harvesting Through Dual Momentum" | NUR Suchsnippets (Repository-Eintrag, Alpha Architect-Snippet); SSRN-ID 2042750 stammt aus der Literaturliste des BAA-Papers |
| Keller/Butler EAA (SSRN 2543979) | NUR Suchsnippets (CXO, R-Bloggers); nicht abgerufen |
| Hoffstein et al. "Rebalance Timing Luck" (Journal of Index Investing) | Paper selbst NICHT gesehen; nur Newfound-Blogpost-Zusammenfassung des Papers |

Konsequenz: Fuer DAA, GEM, EAA ist die Regel nur ueber Sekundaerquellen/Gedaechtnis rekonstruiert. Wo ein Parameter nicht verifiziert ist, steht das unten. Vor dem Kodieren sollten die Originalpapers (SSRN-PDFs) im Browser geoeffnet und mit der Regel hier abgeglichen werden.

## 2. Gemeinsame Implementierungsregeln (gelten fuer alle Strategien)

- Datenquelle: yfinance mit auto_adjust=True (Total-Return-nahe Adjusted Close). Monatsend-Preis = Adjusted Close des letzten Handelstags des Kalendermonats.
- Signal am Schlusskurs des letzten Handelstags t des Monats. Handel FRUEHESTENS am naechsten Handelstag (t+1). Hauptvariante: Ausfuehrung zum Schlusskurs t+1; Sensitivitaet: Open t+1 und t+2. (Keller selbst handelt "am Monatsende", also am Signalschluss; das ist nicht umsetzbar und leicht optimistisch.)
- Kosten: Keller nimmt 0,1 % pro Handel einseitig (TC=0,1 %). Daraus abgeleitet (eigene Rechnung, Umschlag einseitig p.a. mal 0,1 %): PAA-G12 ca. 0,28 %/Jahr (284 % Umschlag), BAA-G12 ca. 0,47 %/Jahr (472 %), BAA-G4 ca. 0,52 %/Jahr (523 %). Testen mit 5, 10, 20 bps einseitig plus Spread-Aufschlag fuer DBC, HYG, EWJ, VNQ.
- Gemeinsamer Startpunkt fuer Vergleich: erster Monat, in dem ALLE Assets des Universums 13 Monatsend-Preise haben (siehe Datenstarts). Nicht mit Proxys vermischen, ausser explizit markiert.
- Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF, Keller nutzt das als Referenz), gleichgewichtetes Buy&Hold desselben Universums (wichtig: sonst misst man nur Diversifikation), Cash.
- Timing-Luck-Pflicht: Jede Strategie zusaetzlich mit 3 gestaffelten Sleeves (Signal-Stichtag 0, 7, 14 Handelstage vor Monatsende; je ein Drittel Kapital) und zusaetzlich mit allen 21 einzelnen Ausfuehrungstagen als Verteilung testen. Die Streuung der Endwerte ueber Rebalance-Tag ist ein Robustheitsmass.

Datenstarts (Yahoo), aus dem Gedaechtnis, vor Nutzung mit yfinance pruefen (erster gueltiger Index zaehlt): SPY 1993-01, QQQ 1999-03, IWM 2000-05, EFA 2001-08, IEF/SHY/TLT/LQD 2002-07, AGG 2003-09, TIP 2003-12, VNQ 2004-09, GLD 2004-11, VWO 2005-03, VGK 2005-03, DBC 2006-02, GSG 2006-07, VEA 2007-07, BND 2007-04, HYG 2007-04, BIL 2007-05, ACWX 2008-03, EWJ 1996-03. Der spaeteste Starter in G12 plus Canary (VEA, BIL) ist Mitte 2007. Mit 12 Monaten Lookback sind BAA/DAA/PAA mit allen Assets also erst ab ca. Mitte/Ende 2008 live-aequivalent testbar.
Gratis-Langfrist-Proxys (nur fuer Teile): Ken French Data Library (US-Markt ab 1926, RF ab 1926), Shiller-Daten (S&P-Zeitreihe, 10J-Zinsen), Vanguard-Fonds in yfinance (VFINX, VBMFX ab 1986, VGSIX/VGTSX ab 1996-ish; Daten pruefen). Rohstoffe: GC=F (Gold-Futures, ab ca. 2000 bei Yahoo). Kellers 1970er-Proxys sind nicht gratis.

## 3. Strategien (nach erwarteter Robustheit sortiert)

### 3.1 faber_gtaa5_sma10_tranched (Faber GTAA, 5 Klassen, 10-Monats-SMA, gestaffelt)

Regel:
- Universum (Quantpedia-Fassung): SPY (US-Aktien), EFA (Ausland), BND (Anleihen), VNQ (REITs), GSG (Rohstoffe). Original-Paper nutzt Indizes (S&P 500, MSCI EAFE, 10J-Treasuries, NAREIT, GSCI) - aus dem Gedaechtnis, Quantpedia nennt nur die Klassen; naeher am Paper waere IEF statt BND.
- Jeder Slot 20 %. Am Monatsende t: P_t > SMA10 (Mittel der letzten 10 Monatsend-Adjusted-Closes inkl. t)? Ja: Slot im Asset. Nein: Slot in Cash (BIL oder SHY). Monatliches Rebalancing, Ausfuehrung t+1.
- Verbesserung (Hoffstein): 3 Sleeves mit Stichtagen 0/7/14 Handelstage vor Monatsende, je 1/3 Kapital; jede Sleeve nutzt ihre eigene verschobene "Monatsend"-Preisreihe (jede 21. Handelstagsstichprobe).

Belege:
- Quantpedia-Seite (abgerufen): Faber-Paper Exhibit 19, 1973-2008: 11,27 % p.a., Volatilitaet 6,87 %, Max Drawdown -29,43 %, Sharpe 1,06. Robustheitscheck laut Seite: 10J-Staatsanleihen statt T-Bills als Cash: 13,41 % vs 12,04 % p.a. (1973-2012, Updatedaten). Ohne Steuern, Kommissionen, Slippage.
- Paper: Faber, "A Quantitative Approach to Tactical Asset Allocation", SSRN 962461 (2013-Update der 2007-JoWM-Fassung). Paper selbst nicht gelesen; Zahlen ueber Quantpedia.
- Zakamulin (laut Quantpedia-Seite zitiert): Timing-Performance enthaelt oft Data-Mining-Bias und ignoriert Reibung; reale Performance nur marginal besser als passiv. Zakamulin-Papers selbst nicht abgerufen.

Verfall/Risiken:
- Trendfilter auf 5 Klassen liefert vor allem Drawdown-Reduktion, kaum Mehrrendite gegenueber Buy&Hold in langen Seitwaertsphasen. Whipsaw-Kosten bei V-foermigen Erholungen (2020, Q4 2018). Reine Cash-Quote in 2022 war ein Plus (Aktien UND Anleihen unter SMA), aber das ist eine einzelne Beobachtung.
- Keine Replikationsfehlschlaege gefunden, aber auch keine unabhaengige Post-2013-Auswertung abgerufen. Ehrlich: unbekannt.
- Kosten: sehr gering (5 ETFs, monatlich, niedriger Umschlag). Zahl aus den Quellen nicht verfuegbar; selbst messen.
- Data-Start: GSG ab 2006-07 und BND ab 2007-04 begrenzen den freien Test auf ca. 2008-2026. DBC statt GSG als Alternative (2006-02).

### 3.2 keller_paa_g12 (Protective Asset Allocation, G12, in BAA-Paper-Notation)

Regel (voll spezifiziert in Kellers BAA-Paper, Fig 1, abgerufen):
- Offensive = Canary-Universum (NO=NP=12): SPY, QQQ, IWM, VGK, EWJ, VWO, VNQ, DBC, GLD, TLT, HYG, LQD. Defensive (ND=2): BIL, IEF.
- Momentum m_i(t) = P_t / SMA13_t - 1 mit SMA13 = Mittel der 13 Monatsend-Preise P_t..P_{t-12} (Keller: "SMA(12)"). Gilt fuer alle drei Universen.
- b = Anzahl Assets im Canary-Universum mit m_i < 0. Defensivanteil CF = min(1, b/6) (Breadth B=6).
- Offensivteil (1-CF) gleichgewichtet auf die Top 6 nach m_i (reine Relative-Momentum-Auswahl, unabhaengig vom Vorzeichen). Defensivteil CF komplett in das eine bessere (hoechstes m) von BIL, IEF (TD=1).
- Beispiel aus dem Paper: 3 schlechte Canary-Assets: 50 % bestes Defensiv-Asset + 6 x 8,33 % Offensive.
- Monatliches Rebalancing, gleichgewichtet je Universum. Ausfuehrung: Keller am Monatsendkurs; hier t+1.
- Hinweis: Notation wurde von Keller gegenueber dem Originalpapier (PAA 2016, SSRN 2759734) leicht angepasst; ein Abgleich mit dem Original ist offen.

Belege (BAA-Paper, Dec 1970-Jun 2022, Kellers ETF-Proxys, TC 0,1 % einseitig):
- Full Sample: CAGR 12,1 %, Max monatl. Drawdown 11,2 %, Vola 7,4 %, Sharpe 1,02, UPI 3,03, Defensive Fraction 50,7 %, Umschlag 284 %/Jahr. 60/40 (SPY/IEF) im Vergleich: 9,5 % CAGR, 29,5 % Max-DD.
- Recent Sample Jun 2002-Jun 2022: CAGR 8,9 %, Max-DD 7,0 %, Vola 7,5 %, Sharpe 1,03. In-Sample-Zehnjahresfenster Jun 2012-Jun 2022: 5,8 % CAGR, Sharpe 0,92 (60/40: 8,8 % im selben Fenster, laut Tabelle R6040-Spalte; Spaltenzuordnung der Extraktion ist unsicher).
- PAA-Paper selbst (SSRN 2759734) nur ueber Literaturliste des BAA-Papers bekannt, nicht gelesen.

Verfall/Risiken:
- Das letzte Zehnjahresfenster ist die schwaechste Phase (5,8 % CAGR), also gerade ausserhalb der Entwicklungsperiode klar schwaecher. Das ist aus Kellers eigener Tabelle ablesbar und passt zu Verfall nach Entwicklung der Regel.
- Hoher Umschlag (284 %), Top6 aus 12 mit monatlichen Wechseln; Timing-Luck relevant.
- Hohe Korrelation der 12 Assets in Krisen (2008, 2020, 2022); der Canary-Breadth-Schwellwert B=6 ist eine Parameterwahl, die Keller aus der Optimierung kennt.
- Autor ist Entwickler und Evaluator derselben Strategie; kein unabhaengiger Out-of-Sample-Test abgerufen.

### 3.3 antonacci_gem_lookback_ensemble (Dual Momentum GEM, Multi-Lookback-Ensemble)

Basisregel (Antonacci; aus Gedaechtnis/Buchwissen, im Abruf nur allgemein bestaetigt):
- Assets: US-Aktien (SPY; Gratis-Langfrist: Ken French Mkt-RF+RF), Ex-US-Aktien (ACWX oder VEU; Alternativ EFA), Anleihen (AGG), Cash/T-Bill (BIL; Langfrist: French RF).
- Am Monatsende t mit Lookback L Monate (Original: 12): r_X = P_t / P_{t-L} - 1 (Total Return).
- Absolute Momentum: Falls r_SPY > r_BIL: 100 % in das Asset mit hoeherem r aus {SPY, ACWX}; sonst 100 % AGG. Monatlicher Check, Ausfuehrung t+1.
- Ensemble-Variante (Empfehlung auf Basis Newfound): 7 Sleeves mit L = 6, 7, 8, 9, 10, 11, 12, je 1/7 Kapital, Sleeve-Gewichte jaehrlich zurueckgesetzt. Die Zahl sieben und die Lookback-Spanne 6-12 folgen der Newfound-Aussage "seven GEM variants, 6 to 12 months"; die genaue Konstruktion (Sleeve-Rebalancing, ob Trend- und Momentum-Lookback gekoppelt sind) ist meine Interpretation.

Belege:
- Antonacci, "Risk Premia Harvesting Through Dual Momentum" (SSRN 2042750; Journal of Management & Entrepreneurship 11(1), 2017, S. 27-55 laut Repository-Snippet). Abstract-Aussage laut Snippet: Absolute und relative Momentum erhoehen die Rendite jeweils unabhaengig; absolute Momentum senkt Volatilitaet und Drawdown staerker; die Kombination ist besser.
- Quantpedia #846 laut Suchsnippet: Backtest 1974-2011, indikative Performance 14,9 %, geschaetzte Volatilitaet 13,93 %. In-Sample, aus Snippet, Quelle nicht abgerufen.
- Newfound "Fragility Case Study: Dual Momentum GEM" (2019-01-14), laut Tag-Seiten-Excerpt: GEM mit Lookbacks 6-12 Monate; 9-Monats-Variante 43,1 % Gesamtrendite vs 146,1 % fuer die 10-Monats-Variante (Zeitraum aus dem Excerpt nicht ersichtlich); 2010: +12,2 % (10 Monate) vs -9,31 % (9 Monate); Jahresabstaende zwischen Implementierungen "hunderte bis tausende Basispunkte". Empfehlung: ueber Implementierungen diversifizieren; 7 GEM-Varianten gleichgewichtet, jaehrlich rebalanciert: naeher am Median, hoehere Sharpe, geringerer Max-DD.
- Suchsnippet (nicht abgerufen): ReSolve replizierte Antonacci mit Proxys sehr nah, fand aber bei 324 Lookback-Varianten (1-18 Monate) ein 5 %-Risiko, dass eine Spezifikation eine andere ueber 5 Jahre um bis zu 64 Prozentpunkte unterperformt. Alpha Architect (2015): RAA habe vergleichbare Performance wie Dual Momentum. Beide nur Snippet-Ebene.

Verfall/Risiken:
- 100 % in EIN Asset pro Monat: hoechste Konzentration der Familie, maximales Timing-Luck und Spezifikationsrisiko (Newfound).
- Nach 2012 (Publikation) ist die OOS-Evidenz mager; ich habe keine verlaessliche Post-2018-Auswertung gefunden. Anleihen-Bein (AGG) lief 2022 (Zins-Schock) schlecht: Stock/Bond-Doppelverlust ist ein dokumentierter Tail fuer jede Bond-als-Safe-Haven-Regel.
- Kosten gering (ein Wechsel pro Monat zwischen 3 ETFs), Steuer/Wechselhaeufigkeit aber real.
- Das Ensemble ist die ehrlichere Variante; der Einzel-Lookback-12-Backtest ueberschaetzt wahrscheinlich die Zuverlaessigkeit.

### 3.4 keller_daa_g12 (Defensive Asset Allocation, G12, Canary VWO+BND)

Regel (CXO-Zusammenfassung, abgerufen; einzelne Parameter nicht verifiziert):
- Momentum "13612W": m = 12*r1 + 4*r3 + 2*r6 + 1*r12 (r_k = Total Return ueber k Monate; Skalierung egal fuer Vorzeichen und Ranking; CXO beschreibt es als Mittel der annualisierten 1/3/6/12-Monats-Returns, aequivalent).
- Canary-Universum C = {VWO, BND}. b = Anzahl c in C mit m_c < 0. Breadth B=2. CF (Cash-Anteil) = min(1, b/B); Rundung auf Vielfache von 1/T (bei B=2 und T=6 ohne Wirkung).
- Cash-Asset = das mit dem hoechsten m aus {SHY, IEF, LQD}.
- Risikoteil (1-CF), gleichgewichtet auf die Top T nach m aus dem G12-Universum, unabhaengig vom Vorzeichen von m. G12 = {SPY, QQQ, IWM, VGK, EWJ, VWO, VNQ, DBC, GLD, TLT, HYG, LQD} (Liste aus Kellers BAA-Paper; ob DAA hier DBC oder GSG nutzt, ist NICHT verifiziert). T=6 ist der Keller-Standard fuer G12, im Abruf NICHT bestaetigt: Sensitivitaet T=2..6 mit testen.
- Monatlich, Ausfuehrung t+1.

Belege:
- Keller/Keuning (2018), "Breadth Momentum and the Canary Universe: Defensive Asset Allocation (DAA)", SSRN 3212862 (ID aus Literaturliste im BAA-Paper; SSRN-Seite 403). Laut CXO-Zusammenfassung (Testperiode Maerz 2008 bis Maerz 2018): DAA schlug VAA bei CAGR in 3 von 4 Universen, hatte aber in allen 4 hoehere Drawdowns; durchschnittliche Cash-Quote oft unter der Haelfte von VAA; geringerer Umschlag und besseres Tracking-Error-Profil. Konkrete CAGR/DD/Sharpe-Zahlen stehen nur in einem Bild und fehlen im Abruf.
- Quantpedia-Suchsnippet: Backtest 1970-2018, indikative Performance 16 %. Nicht abgerufen.
- CXO-Kritik: Das Canary-Universum wurde mit Daten 1926-1970 experimentell gewaehlt und in-sample ueber 1971-1993 optimiert; der Out-of-Sample-Test 1994-Maerz 2018 ist der relevante. Vorperiode ETF-Proxys. Die ETF-Periode 2008-2018 sei zu kurz fuer verlaessliche Inferenz.

Verfall/Risiken:
- Canary mit nur 2 Assets (VWO, BND): Ein falsches Signal im Canary schaltet die ganze Allokation um. Hohe Schwellwert-Empfindlichkeit (B).
- Hoeherer Drawdown als VAA ist der Preis fuer weniger Cash; Tail-Risiken liegen in schnellen V-Erholungen (2020) und in Stock/Bond-Doppelverlusten, wo Cash-Asset IEF/LQD nicht schuetzt (2022).
- Unabhaengige Replikation: nur Hobbyisten-Code (R-Bloggers "KDA", Suchsnippet), keine formale. Eine QuantConnect-Forennachricht (Suchsnippet) berichtet, dass das verwandte Hybrid AA (HAA) die publizierten Ergebnisse nicht reproduzierte und schiebt es teils auf das Ausfuehrungstiming. Das ist anekdotisch, passt aber zur Erwartung, dass Same-Close-Ausfuehrung Ergebnisse aufbläht.

### 3.5 keller_baa_g12_balanced (Bold Asset Allocation, G12/T6; Variante G4/T1 aggressiv)

Regel (voll spezifiziert, BAA-Paper Abschnitt 6, abgerufen):
- Am Monatsende t:
  1. Relative Momentum fuer Offensive und Defensive: m_i = P_t / SMA13_t - 1 (SMA ueber 13 Monatsend-Preise P_t..P_{t-12}).
  2. Canary P = {SPY, VWO, VEA, BND}. Absolute Momentum der Canary-Assets mit 13612W = 12*r1 + 4*r3 + 2*r6 + 1*r12; "bad" wenn < 0. Falls MINDESTENS EIN Canary-Asset bad (B=1): Defensiv-Modus. Sonst Offensiv-Modus.
  3. Offensiv-Modus: Universe O (G12) = {SPY, QQQ, IWM, VGK, EWJ, VWO, VNQ, DBC, GLD, TLT, HYG, LQD}; Top 6 nach m_i gleichgewichtet (je 1/6), kein Absolut-Filter. Defensiv-Modus: Universe D = {TIP, DBC, BIL, IEF, TLT, LQD, BND}; Top 3 nach m_i je 1/3; jedes der Top 3 mit m_i kleiner als m_BIL wird durch BIL ersetzt.
  4. Gesamtes Portfolio jeden Monat neu gewichten, auch ohne Positionswechsel.
- Aggressive Variante BAA-G4/T1: Offensiv-Universum = {QQQ, VWO, VEA, BND}, Top 1 (TO=1); alles andere gleich. Dort wurde QQQ statt SPY "in-sample optimal" gewaehlt (Keller Fussnote).
- Kosten: Keller TC=0,1 % einseitig. Ausfuehrung t+1 statt Monatsendkurs.

Belege (BAA-Paper, Dec 1970-Jun 2022, Kellers Proxys, nach 0,1 % TC):
- BAA-G12/T6: CAGR 14,6 %, Max monatl. DD 8,7 %, Vola 8,5 %, Sharpe 1,19, UPI 4,81, Defensive Fraction 57,2 %, Umschlag 472 %/Jahr, 8,2 Handelsmonate/Jahr. Recent Sample (Jun 2002-Jun 2022): 12,2 % CAGR, 8,7 % DD, Sharpe 1,27. Letzte 10 Jahre (Jun 2012-Jun 2022): 7,8 % CAGR.
- BAA-G4/T1: CAGR 21,0 %, Max DD 14,6 %, Vola 13,6 %, Sharpe 1,21, Umschlag 523 %. Recent Sample 16,7 % CAGR, DD 9,5 %, Sharpe 1,32.
- BAA-G12/T3: 16,4 % CAGR, DD 11,4 %. BAA-G4/T2: 17,7 % CAGR, DD 12,7 %. 60/40: 9,5 % CAGR, 29,5 % DD.
- Keller-eigener YTD 2022 (bis Jun): +6,4 % (in den ersten sechs Monaten 2022 waren alle BAA-Varianten komplett defensiv: 33 % DBC, 67 % BIL), gegenueber -16 % fuer 60/40.
- BAA-Paper selbst: SSRN 4166845 (v0.981, Juli 2022). Nur Arbeitspapier, kein Peer-Review.

Selbstkritik des Papers und meine Einordnung:
- Mehrere Bausteine wurden "in-sample optimal auf K/IS" gewaehlt (DBC im Defensiv-Universum, QQQ statt SPY, Filterkombination SMA(12)/13612W; K/IS-Fenster: Dec 1970-Dec 1980 und Jun 2012-Jun 2022). Das ist Mehrfachtesten auf demselben Pfad. Keller verweist selbst auf Harvey/Liu (Backtesting).
- Robustheitstabellen im Paper: In BAA-G4 bricht K auf 0,0 % (Max-DD > 25 %), wenn der Canary-Filter langsamer als 13612W/SMA(3) ist (SMA(6), SMA(9), SMA(12), RET(12) im Canary: durchgehend 0,0 %). Die Strategie lebt also vom schnellen Canary-Signal. Das ist eine harte Abhaengigkeit, keine "flache" Robustheit.
- Mit Canary B=1 und 4 Assets ist die Quote im Defensivmodus ca. 57 %; Wechselhaeufigkeit (8,2 Handelsmonate pro Jahr in G12) und Defensiv-Universe mit DBC/TLT/LQD (Zins-Schock-Risiko) sind reale Reibung.
- Kein unabhaengiger OOS-Nachweis nach Veroeffentlichung (Juli 2022) gefunden.
- Die 21 % CAGR bei nur 14,6 % Max-DD (G4/T1) ueber 52 Jahre sind in meinen Augen ein Overfit-Alarm, kein Beleg. Ich wuerde nur G12/T6 als ernsthaften Kandidaten fuehren und G4/T1 nur als Stresstest.

## 4. Meta-Ebene: Rebalance-Timing-Luck (Hoffstein, Faber, Braun)

- Quelle (abgerufen): Newfound-Blog, 2019, Zusammenfassung des Papers "Rebalance Timing Luck: The (Dumb) Luck of Smart Beta" (Journal of Index Investing laut Newfound; Paper selbst nicht gesehen; Suchsnippet datiert es auf Februar 2020).
- Zahlen laut Blog (Aktien-Smart-Beta, NICHT TAA): jaehrlich 100-400 bp Timing-Luck fuer 100-Aktien-Portfolios, halbjaehrlich rebalanciert: Value 2,5 %, Momentum 4,4 %, Low Vol 1,1 %, Quality 2,0 %. Zwei identische Momentum-Portfolios (100 Aktien, halbjaehrlich): 95 %-Intervall der Streuung +/-12,4 %. Steigt mit Umschlag, Konzentration und Signalgeschwindigkeit; faellt bei haeufigerem Rebalancing.
- Ausdrueckliche Luecke: Der Blogpost nennt KEINE Zahlen fuer TAA/Trendstrategien (erwaehnt nur fruehere Arbeiten). Fuer Faber/PAA/GEM ist die Groessenordnung unbekannt und muss mit den Tranchen-Backtests (Abschnitt 2) selbst gemessen werden. Erwartung: Top1-Strategien (GEM, BAA-G4) am empfindlichsten.
- Abhilfe laut Paper: Tranchen mit gestaffelten Rebalance-Terminen (z. B. quartalsweise in drei Sleeves JAN-APR-JUL-OCT, FEB-MAI-AUG-NOV, MAR-JUN-SEP-DEZ). Kosten der Staffelung im Blog nicht quantifiziert.
- Aeltere Newfound-Notiz: https://blog.thinknewfound.com/2013/08/the-luck-of-the-rebalance-timing/ (nur Suchsnippet).

## 5. Nicht aufgenommen / nicht ausreichend verifiziert

- Elastic Asset Allocation (Keller/Butler, SSRN 2543979, Dez 2014): Nur Snippets. Gewichtung ueber Elastizitaeten (geometrisch gewichtete Mittel von Rendite, Volatilitaet und Korrelation zum gleichgewichteten Index; Rendite aus 1/3/6/12-Monats-Excess-Returns, Vola und Korrelation aus 12 Monaten). CXO-Snippet: Golden-EAA-Varianten OOS (Apr 1964-Aug 2014) Sharpe 0,60-0,97 vs 0,32-0,48 fuer S&P 500 und Gleichgewicht. Die Parameter (Elastizitaeten wR, wV, wC, Exponent) habe ich nicht gesehen, daher keine Regel angegeben (waere sonst geraten).
- Flexible Asset Allocation (Keller/van Putten, SSRN 2193735), VAA (SSRN 3002624), Hybrid AA (HAA): nicht abgerufen. VAA-G4-Canary (SPY, VWO, VEA, BND) ist nur indirekt ueber BAA bekannt.
- Allocate Smartly: Seiten waren 404; keine unabhaengigen Live-/Replikationszahlen gewonnen.
- Neuere akademische Replikationen (2015-2026) zu Keller-Strategien: nicht gefunden. Das ist selbst ein Befund: Die Familie wird von Praktikern/Blogs getragen, nicht von begutachteter Literatur.
- Zakamulin-Papers (Moving-Average-Timing, Data-Mining-Bias): nur ueber Zitat bei Quantpedia/BAA-Literaturliste bekannt.

## 6. Empfohlene naechste Schritte im Quant-Lab

1. Gemeinsames Universum-Panel (yfinance, auto_adjust) bauen, Datenstarts pruefen, Look-ahead-Test (Signal t, Trade t+1) per Unit-Test.
2. Strategien 3.1 bis 3.5 mit Standardkosten (10 bps) und Kostenleiter (5/10/20 bps) auf der gemeinsamen Periode ab ca. 2008-08 backtesten; zusaetzlich Teilzeitraeume (2008-2013, 2013-2019, 2019-2026), um den "Verfall in Kellers letztem Zehnjahresfenster" zu pruefen.
3. Timing-Luck-Verteilung (21 Ausfuehrungstage, 3er-Sleeves) pro Strategie.
4. Benchmark-Zwang: schlagen sie gleichgewichtetes Buy&Hold desselben Universums und 60/40 nach Kosten risikobereinigt (Sharpe, Ulcer, Calmar)? Wenn nicht: "funktioniert nach Kosten nicht" als gueltiger Eintrag festhalten.
5. Korrelationsmatrix der fuenf Strategie-Renditen; wahrscheinlich eher ein Cluster als fuenf Edges.
6. Originalpapers (SSRN-PDFs DAA 3212862, VAA 3002624, PAA 2759734, Antonacci 2042750) manuell oeffnen und Parameter (T, Universum, GEM-Details) abgleichen.

## 7. Quellen (alle URLs, wie gesehen)

Abgerufen:
- Keller (2022), Bold Asset Allocation (BAA): https://ssrn.com/abstract=4166845 (PDF-Mirror, gelesen: https://thechartist.com.au/wp-content/uploads/2024/12/5369/SSRN-id4166845.pdf)
- CXO Advisory, Zusammenfassung DAA: https://www.cxoadvisory.com/strategic-allocation/multi-class-momentum-portfolio-with-canary-crash-protection/
- Quantpedia, Asset Class Trend Following (Faber): https://quantpedia.com/strategies/asset-class-trend-following/ ; Faber-Paper laut Seite: http://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461
- Newfound, "The dumb timing luck of smart beta": https://blog.thinknewfound.com/2019/11/the-dumb-timing-luck-of-smart-beta/
- Newfound GEM-Tag-Seite: https://blog.thinknewfound.com/tag/gem/ (Einzelpost laut Seite: https://blog.thinknewfound.com/2019/01/fragility-case-study-dual-momentum-gem/ - nicht abgerufen)

Nur als Suchtreffer gesehen (Inhalt nur als Snippet):
- Antonacci, Risk Premia Harvesting Through Dual Momentum, Repository-Eintrag: https://gnanaganga.inflibnet.ac.in:8443/jspui/handle/123456789/14295 ; Alpha Architect (403): https://alphaarchitect.com/risk-premia-harvesting-through-momentum/ ; SSRN-ID 2042750 laut BAA-Literaturliste
- Newfound 2013, Luck of the Rebalance Timing: https://blog.thinknewfound.com/2013/08/the-luck-of-the-rebalance-timing/
- Keller/Butler EAA: CXO https://www.cxoadvisory.com/momentum-investing/long-run-test-of-a-tactical-tractable-mpt ; R-Bloggers https://www.r-bloggers.com/2015/01/for-a-new-year-a-new-asset-allocation-system-just-published-in-ssrn/
- Alpha Architect, RAA vs Dual Momentum (2015): https://alphaarchitect.com/2015/02/asset-allocation-horserace-robust-asset-allocation-raa-vs-dual-momentum/
- QuantConnect-Forum zu HAA: https://www.quantconnect.com/forum/discussion/14842/hybrid-asset-allocation/
- R-Bloggers KDA (DAA-Code): https://www.r-bloggers.com/2019/01/right-now-its-kdaasset-allocation/
- Quantpedia Premium Update (DAA-Snippet 1970-2018, 16 %): https://vvv.quantpedia.com/?p=25576
