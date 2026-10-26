# Familie: Value und Carry (Cross-Asset) - Literatur- und Strategienotizen

Stand der Recherche: 2026-10-11. Analyst: Claude (Quant-Research-Subagent). Aufwand: ca. 17 Web-Abrufe (inkl. 2 Redirects und 2 Fehlversuchen), danach abgeschlossen.

**Wichtig vorab (Ehrlichkeitsvermerk):**
- Zahlen in diesem Dokument stammen nur aus (a) den von mir tatsaechlich abgerufenen und per `pdftotext` gelesenen Volltexten von Asness-Moskowitz-Pedersen 2013 und der Preprint-Fassung (Juli 2012) von Koijen-Moskowitz-Pedersen-Vrugt, (b) abgerufenen Webseiten (Quantpedia, NBER, Ken French, Shiller, AQR) oder (c) Such-Snippets. Quelle (c) ist als "nur Snippet" markiert; dort wurde der Volltext NICHT gelesen.
- Nicht abgerufen/nicht gesehen und deshalb NICHT als Beleg verwendet: Fama-French 1992 und 2015, Lustig-Roussanov-Verdelhan 2011 (nur Abstract-Snippet), Menkhoff et al. 2012, Jensen-Kelly-Pedersen, McLean-Pontiff, Asness "Siren Song of Factor Timing", Welch-Goyal, Campbell-Shiller. Wo ich sie aus Allgemeinwissen kenne, steht es nicht als Fakt hier.
- Eigene Entwurfsparameter (Schwellen, Fenster, Kostenannahmen) sind jeweils als **[Annahme]** markiert; sie stehen NICHT in den Papers.

---

## 1. Quellenstatus

| Quelle | URL | Status |
|---|---|---|
| Asness, Moskowitz, Pedersen (2013), Value and Momentum Everywhere, J. of Finance 68(3), DOI 10.1111/jofi.12021 | https://w4.stern.nyu.edu/facdir/lpederse/papers/ValMomEverywhere.pdf | Volltext abgerufen, gelesen |
| Koijen, Moskowitz, Pedersen, Vrugt, Carry - Preprint "Current Version: July 2012, Preliminary and Incomplete" | https://w4.stern.nyu.edu/facdir/lpederse/papers/Carry.pdf | Volltext abgerufen, gelesen. ACHTUNG: das ist NICHT die finale JFE-Fassung (JFE 127(2), 2018, S. 197-225); Zahlen koennen in der Endfassung abweichen |
| KKMPV/Carry NBER-Seite (WP 19325) | https://www.nber.org/papers/19325 | nur als Suchtreffer gesehen |
| Daniel, Hodrick, Lu, The Carry Trade: Risks and Drawdowns, NBER WP 20433 (Aug 2014); Critical Finance Review 6(2), 2017, S. 211-262 | https://www.nber.org/papers/w20433 | Abstract-Seite abgerufen |
| Lustig, Roussanov, Verdelhan, Common Risk Factors in Currency Markets, Rev. Financial Studies 24(11), 2011, S. 3731-3777 | https://repository.upenn.edu/fnce_papers/335 (auch NBER WP 14082: https://www.nber.org/papers/w14082.pdf) | nur Abstract per Such-Snippet; Seite selbst nicht abgerufen. Die Bezeichnung "HML_FX" konnte ich NICHT bestaetigen. (Mein erster Versuch, NBER w14083 abzurufen, war falsch: das ist eine Subprime-Arbeit. Korrekte Nummer laut Suchtreffer: w14082.) |
| Faber, Global Value: Building Trading Models with the 10 Year CAPE (SSRN 2129474; Buch "Global Value" 2014) | http://papers.ssrn.com/sol3/papers.cfm?abstract_id=2129474 | SSRN-Seite NICHT abgerufen (nicht erreichbar). Inhalt ueber Quantpedia (abgerufen) und CXO-Advisory-Snippets |
| Quantpedia, "Value Factor - CAPE Effect within Countries" | https://quantpedia.com/strategies/value-factor-effect-within-countries | abgerufen |
| CXO Advisory zu Faber | https://www.cxoadvisory.com/fundamental-valuation/a-few-notes-on-global-value und https://cxoadvisory.com/?p=21856 | nur Suchtreffer-Snippet |
| Arnott, Harvey, Kalesnik, Linnainmaa (2021), Reports of Value's Death May Be Greatly Exaggerated, Financial Analysts Journal 77(1), S. 44-67, DOI 10.1080/0015198X.2020.1842704 | https://ideas.repec.org/a/taf/ufajxx/v77y2021i1p44-67.html | nur Abstract per Snippet (Volltext paywalled) |
| "Currency carry trade: The decline in performance after the 2008 Global Financial Crisis", J. of Intl. Financial Markets, Institutions & Money, Bd. 76 (2022) (Journal laut RePEc-URL-Kuerzel "intfin"; Autoren nicht ermittelt) | https://ideas.repec.org/a/eee/intfin/v76y2022ics1042443121001670.html | nur Suchtreffer-Snippet |
| Jurek (Titel/Venue nicht verifiziert), options-basierte Studie "crash-neutral" Carry | https://www.johnhcochrane.com/s/jurek_currency.pdf | nur Snippet; nicht als Beleg in der strukturierten Ausgabe verwendet |
| Asness (Nov 2012) "An Old Friend: The Stock Market's Shiller P/E" (AQR) | Kommentar-Seite: https://rpc.cfainstitute.org/blogs/enterprising-investor/2012/asness-shiller-pe-is-signaling-risk-of-another-lost-decade-for-u-s-stocks/ | nur Snippet/Sekundaerbericht |
| Cambria Global Value ETF (GVAL), nur verwandtes Live-Produkt | https://www.cambriafunds.com/assets/docs/GVAL_Investment_Case.pdf | nur Suchtreffer |

### Datenquellen (geprueft)
- **Ken French Data Library**: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html - abgerufen. Enthaelt u.a. Fama/French 3 und 5 Faktoren (US), Developed / Developed ex US / Europe / Japan / Asia Pacific ex Japan 3- und 5-Faktoren (monatlich und taeglich), 25 bzw. 6 Portfolios nach Size/BM (US und regional) sowie "International Country and Index Portfolios formed on B/M, E/P, CE/P, and D/P" (Rohdaten MSCI 1975-2006, Bloomberg 2007-heute). Startdaten stehen auf der abgerufenen Seite nicht. Die Seite zeigt Renditen bis August 2026. Die Struktur der "International Country and Index Portfolios" habe ich NICHT geprueft - potenziell gratis Quelle fuer echten Laender-Value-Wert (Pruefen!).
- **Shiller-Daten** (ie_data.xls: US-Kurse, Dividenden, Gewinne, Zinsen, CPI, CAPE, monatlich ab Januar 1871): https://shillerdata.com/ (abgerufen). Der alte Host econ.yale.edu/~shiller war nicht erreichbar (ECONNREFUSED). Direktlink laut Seite: https://img1.wsimg.com/blobby/go/e5e77e0b-59d1-44d9-ab25-4763ac982e53/downloads/1449043e-a1ed-4e2e-8e9c-7b9a2a064493/ie_data.xls . Nur USA - keine Laender-CAPEs.
- **AQR Datasets**: https://www.aqr.com/Insights/Datasets - abgerufen. Relevant: "Value and Momentum Everywhere: Factors, Monthly" und "...: Portfolios, Monthly" (Datum auf Seite: 31.07.2026), "The Devil in HML's Details: Factors, Monthly/Daily" (31.07.2026), QMJ, BAB, AQR Momentum Indices. Ein eigener "Carry"-Datensatz steht auf der Seite NICHT. Damit lassen sich die AMP-Faktoren out-of-sample (2013-2026) gegenpruefen (ohne Handelbarkeit). Download = Nutzerfreigabe noetig, hier nicht durchgefuehrt.
- Yahoo-Ticker und FRED-Serien-IDs unten: die Ticker-Muster stammen aus meinem Wissen, ihre aktuelle Verfuegbarkeit/Startdaten habe ich in dieser Recherche NICHT live verifiziert. Vor Nutzung per `yfinance`/FRED pruefen. Die OECD-Serien auf FRED (Zinsen/CPI) sind ein Risiko: manche wurden bei FRED eingestellt oder nicht mehr aktualisiert.

---

## 2. Kernbefunde aus den abgerufenen Volltexten

### 2.1 Asness-Moskowitz-Pedersen 2013 (Journal-Fassung)
- Acht Maerkte/Assetklassen: Einzelaktien US, UK, Kontinentaleuropa, Japan (sehr grosse/liquide Titel, typischerweise obere Quintil, Value-Gewichtung), Laenderindex-Futures, Staatsanleihen, Waehrungen, Rohstoff-Futures.
- Stichproben (Text): Aktien ab 1972 (Europa/Japan ab 1974), Laenderindizes ab 01/1978, Waehrungen ab 01/1979, Anleihen ab 01/1982 (10 Laender), Rohstoffe ab 01/1972, alle bis 07/2011.
- **Value-Masse** (woertlich im Text definiert):
  - Einzelaktien: BE/ME.
  - Laenderindizes: BE/ME des MSCI-Index des Vormonats.
  - Rohstoffe: log(Durchschnitts-Spotpreis von 4,5 bis 5,5 Jahren zurueck / aktueller Spotpreis) = im Kern die negative 5-Jahres-Spotrendite.
  - Waehrungen: log(Durchschnitts-Spotkurs 4,5-5,5 Jahre zurueck / aktueller Spotkurs) MINUS Log-Differenz der CPI-Aenderung (Ausland relativ zu US) ueber denselben Zeitraum = 5-Jahres-Aenderung der Kaufkraftparitaet.
  - Anleihen: 5-Jahres-Aenderung der Rendite 10-jaehriger Anleihen. Alternativmasse (Panel C): Realrendite (10J-Rendite minus 5J-Inflationsprognose) und Term Spread (10J-Rendite minus Kurzfristzins).
- **Momentum**: Rendite der letzten 12 Monate ohne den letzten Monat (MOM 2-12), fuer alle Assetklassen einheitlich.
- **Portfoliokonstruktion**: Rangbasierte Gewichte w_i = c*(rank(S_i) - Mittelwert(rank)), skaliert auf 1 USD long und 1 USD short (Gl. 1); Nicht-Aktien-Assetklassen gleichgewichtet; monatliches Rebalancing ("naively rebalanced exactly monthly"); ueber Assetklassen hinweg Gewichtung mit dem Kehrwert der (Ex-post-Stichproben-)Volatilitaet, "each asset class contributes roughly an equal amount".
- **Ergebnisse (Sharpe, brutto, Stichprobe bis 07/2011)** - Tabelle I ist im Text-Extrakt teilweise verschoben; hier nur Werte, die ich eindeutig zuordnen konnte:
  - Value+Momentum 50/50 ueber alle Assetklassen inkl. Aktien: **Sharpe 1,45** (Fliesstext). Tabellenwerte fuer Kombination ca. 1,4-1,6.
  - Value ueber alle Assetklassen ("Global all asset classes"): Sharpe 0,73 (P3-P1) / 0,72 (Faktor); Value in Nicht-Aktien-Klassen: 0,50 / 0,55.
  - Laenderindizes Value (BE/ME): Sharpe 0,61 (P3-P1) / 0,60 (Faktor), 50/50-Kombination ca. 1,16 / 1,00.
  - Waehrungen Value (PPP-5J): Sharpe 0,34 / 0,44; Kombination 0,63 / 0,69.
  - Rohstoffe Value: Sharpe 0,26 / 0,31.
  - Anleihen Value (5J-Renditeaenderung): Sharpe 0,18 / 0,07, nicht signifikant; mit Realrendite 0,73, Term Spread 0,55, Komposit 0,91 / 1,10 (Text).
  - US-Large-Cap-Value (HML-aehnlich) 01/1972-07/2011: P3-P1 Mittelwert 3,7% p.a. (t = 1,83), Sharpe 0,29; global Aktien Value P3-P1 6,2% (t = 3,60), Sharpe 0,57.
  - Korrelation Value/Momentum innerhalb der Assetklassen im Schnitt ca. -0,49 (Text); in Aktienmaerkten ca. -0,60.
- **Verfall (Autoren selbst, Tabelle VII)**: Sharpe von Value und Momentum sind von 1972-91 auf 1992-2011 "slightly" gesunken; Korrelationen zwischen Value-Strategien verschiedener Maerkte stiegen von 0,31 auf 0,71 (Momentum 0,46 auf 0,77); nach August 1998 hoeher. Kombination Value/Momentum blieb stabil, weil die Value/Momentum-Korrelation von -0,44 auf -0,63 sank. Value schneidet nach 1998 bei sich verschlechternder Funding-Liquiditaet besser ab (Sharpe 0,85 vs. 0,28 bei besserer Liquiditaet); Momentum umgekehrt (0,19 vs. 0,99); die 50/50-Kombination ist "immune" gegen Liquiditaetsrisiko.
- **Kosten**: Das Paper rechnet ohne explizite Transaktionskosten. Aussage der Autoren: Futures-Maerkte haben tiefere Kosten als Aktien; Netto-Renditen "likely much closer". Keine Zahl.

### 2.2 Koijen-Moskowitz-Pedersen-Vrugt, Carry (Preprint Juli 2012)
- Definition: Carry = erwartete Rendite, wenn sich der Preis nicht aendert. Rendite = Carry + E(Preisaenderung) + Schock.
- **Carry je Assetklasse (Text)**:
  - Waehrungen: Zinsdifferenz Ausland minus Inland (skaliert mit 1/(1+r)); abgeleitet aus 1-Monats-Forwards.
  - Aktien(-index-Futures): erwartete Dividendenrendite minus lokaler risikofreier Zins (Gl. 8).
  - Anleihen: Rendite minus Kurzfristzins (Term Spread, Gl. 14), bzw. mit Roll-down: y10 - r - Dmod*(y10 - y(9J11M)) (Gl. 15/17). Synthetische Futures aus Zero-Kupon-Renditen (Korrelation >0,95 zu echten Futures, wo vorhanden).
  - Rohstoffe: Steigung der Futures-Kurve (Kontrakte zweier Laufzeiten), pro Monat normiert.
- **Portfolio**: Rang-Gewichte w_i = z*(rank(C_i) - (N+1)/2), long/short je 1 (Gl. 19) - gleiche Konstruktion wie AMP; Alternative Top/Bottom 20-30%. Monatsende-Rebalancing. "Current carry" und "carry1-12" (gleitender 12-Monats-Mittelwert der Carry-Werte, wegen Saisonalitaet in Dividenden und Rohstoffen). Assetklassen vola-gewichtet kombiniert.
- **Stichprobe**: Aktien 03/1988-02/2011 (13 Index-Futures), Anleihen 11/1991-02/2011 (10 Laender), Rohstoffe 02/1980-02/2011 (24 Futures), Waehrungen 11/1983-02/2011 (20 Forwards).
- **Ergebnisse (brutto, Preprint)**: Einzel-Carry-Trades Sharpe 0,6 bis 0,9 (Einleitung); "current carry" Sharpe von 0,62 (Rohstoffe) bis 0,93 (Aktien); carry1-12 von 0,48 (Anleihen) bis 0,67 (Rohstoffe); Mittelrenditen current carry 5,1% (Anleihen) bis 11,7% (Rohstoffe). **Diversifiziert: Sharpe 1,49 (current) bzw. 0,95 (carry1-12)** vs. passiv-diversifiziert 0,75. Korrelationen der Carry-Trades zwischen Assetklassen nahe null (nur Waehrungen/Anleihen 0,23). Waehrungs-Carry zeigt starke negative Schiefe; diversifiziertes Carry-Portfolio nicht staerker negativ schief als passives. "Carry downturns" fallen mit globalen Rezessionen und Liquiditaetskrisen zusammen.
- Endfassung JFE 2018 (laut Snippet): Carry sagt Renditen quer und zeitlich in vielen Assetklassen voraus, ist durch bekannte Praediktoren nicht erklaert, subsumiert viele. Zweiter Preis Fama-DFA 2018. Zahlen der Endfassung nicht gesehen.

### 2.3 Daniel-Hodrick-Lu (NBER 20433 / CFR 2017) - Abstract-Seite
G10-Carry: Performance haengt von der Basiswaehrung ab. Dollar-neutrale Carry-Trades haben insignifikante abnormale Renditen; die Dollar-Exposure-Komponente verdient signifikante abnormale Renditen mit wenig Schiefe. Dynamische Spread-Gewichtung und Risiko-Rebalancing verbessern die Ergebnisse. Hedging mit Optionen reduziert, eliminiert aber die abnormalen Renditen nicht. Drawdowns: zeitvariable Autokorrelation hilft die negative Schiefe bei laengeren Horizonten zu erklaeren. Keine Sharpe-Zahlen auf der abgerufenen Seite.

### 2.4 Weitere (nur Snippet-Ebene)
- Lustig-Roussanov-Verdelhan 2011: Hoeherverzinsliche Waehrungen laden staerker auf einem "slope"-Faktor; dieser erklaert den Grossteil der Querschnittsunterschiede der Durchschnitts-Excess-Returns zwischen hoch- und niedrigverzinslichen Waehrungen; Faktor haengt mit Aenderungen der globalen Aktienvolatilitaet zusammen.
- Post-2008-Rueckgang des G10-Carry (Snippet auf RePEc-Titel "...the decline in performance after the 2008 Global Financial Crisis"): Rueckgang wird mit der weltweiten Zinskompression seit 2008 und sinkenden Wachstums-/Inflationserwartungen verknuepft; Referenz auf Zuercher Masterarbeit (2023), nach der erweiterter Waehrungskorb, Carry-Momentum und vola-adjustierter Carry den Abschwung vermeiden koennen (Qualitaet dieser Quelle unbekannt).
- Arnott et al. 2021 (Abstract): HML (Fama-French) hat Growth seit 2007 unterperformt; Drawdown 55% bis Mitte 2020; die relative Bewertung der Value-Seite fiel vom obersten Quartil (Anfang 2007) auf das unterste Perzentil (Juni 2020); Aenderung des Bewertungsspreads erklaere den ganzen Drawdown; kapitalisierte Intangibles verbessern das Value-Mass deutlich. Korrektur zu Fig. 1B/Endnote 32 existiert.
- Faber (Snippets/Quantpedia): siehe Strategie 4.
- Asness 2012 via Sekundaerquellen: Start-Shiller-P/E ist ein brauchbarer Proxy fuer 10-Jahres-Realrenditen (Dezil-Sortierung rollierender Dekaden seit 1926); als kurzfristiges Timing schwach; R2 laut Kommentar ca. 40% (nicht verifiziert); lange Phasen hoher Bewertungen testen das Signal.

---

## 3. Gemeinsame Konventionen fuer alle Regeln

- t = letzter Handelstag eines Monats. Alle Signale nutzen nur Daten bis zum Schlusskurs von t. Handel zum **Schlusskurs des naechsten Handelstags (t+1d)** (bei ETFs/Futures projektkonform alternativ zum Eroeffnungskurs t+1d, siehe Quant-Lab-CLAUDE.md; FX-Tagesreihen von FRED haben nur einen Tageswert); Position gehalten bis zum Schlusskurs des Tages nach dem naechsten Monatsultimo. (Strategie 4: jaehrlich.)
- **rankweights(S)**: Ränge aufsteigend (hoechstes Signal = hoechster Rang = long), Ties = Durchschnittsrang; w_i = c*(rank_i - (N+1)/2) mit c so, dass Summe positiver Gewichte +1 und Summe negativer Gewichte -1 ist (AMP Gl. 1, KMPV Gl. 19).
- Renditen aus Total-Return-Reihen (Yahoo `auto_adjust=True` bzw. Adj Close), USD.
- **[Annahme] Kosten** zum Stresstest (nicht aus den Papers): ETF ein-Weg 10 bps, Futures-Proxy 5 bps, G10-FX 3 bps, plus Short-Leihe/Finanzierung bei ETF-Shorts 50 bps p.a. Eigene Sensitivitaet 0 / 1x / 2x rechnen.
- Warm-up: Value-Signal braucht 66 Monate Historie. Erste handelbare Signale: Laender-ETFs ca. 09/2001; Rohstoff-Futures (Yahoo ab ca. 2000) ca. 2006.

---

## 4. Strategien (nach erwarteter Robustheit sortiert)

### S1: `xasset_value_mom_5050` - AMP Value+Momentum 50/50 ueber Laender-ETFs, FX, Rohstoffe (Proxy-Version)
**Warum Platz 1:** Die einzige Kombination, fuer die die Autoren selbst eine stabile Eigenschaft ueber die Zeit zeigen (Value/Momentum-Korrelation sinkt, wenn die Value-Value-Korrelation steigt), diversifiziert ueber Assetklassen, robustes Design (Ranks, Vola-Gewichte). Die Value-Haelfte ist mit Gratisdaten nur ein grober Proxy (Long-Term-Reversal statt BE/ME), die Momentum-Haelfte traegt die Performance.

Regel (Pseudocode):
```
PARAMS: VAL_WIN = Monate t-66 .. t-54; MOM = Rendite t-12m .. t-1m; MIN_N = 6; VOL_WIN = 36 Monate
SLEEVES: EQ, FX, CMD
am Monatsende t:
  fuer jeden Sleeve k:
     A = Assets mit >= 66 Monaten Historie und gueltigem Kurs bei t
     wenn |A| < MIN_N: Sleeve k bekommt Gewicht 0
     fuer i in A:
        TRI_i = Total-Return-Index (EQ: Adj Close; FX: siehe unten; CMD: siehe unten)
        MOM_i = log( TRI_i(t-1m) / TRI_i(t-12m) )
        EQ, CMD:  VAL_i = log( mean(P_i ueber Monatsenden t-66..t-54) / P_i(t) )       # P = TRI
        FX:       VAL_i = log( mean(S_i ueber t-66..t-54) / S_i(t) ) - ( dlogCPI_i - dlogCPI_US )  # S = USD je Fremdwaehrung, dlogCPI ueber 60 Monate;
                  falls keine CPI-Reihe: dlogCPI-Term = 0 (reine 5J-Spot-Reversal), als Schalter USE_CPI
     wV = rankweights(VAL);  wM = rankweights(MOM)
     w_k = 0.5*wV + 0.5*wM
     sigma_k = annualisierte Stdabw. der Monatsrenditen eines gleichgewichteten Long-Only-Korbs der Assets von Sleeve k, trailing 36 Monate
  lambda_k = (1/sigma_k) / Summe_j (1/sigma_j)    # ueber aktive Sleeves
  Zielgewicht Asset i in Sleeve k:  W_i = lambda_k * w_k,i
  optional: Gesamtskalierung auf 10% Vola (trailing 36M Strategie-Vola, ex ante)
Ausfuehrung: Orders zu Schlusskurs t+1d; Halten bis naechster Monatsultimo +1d.
```
FX-Renditeindex (Total-Return vs. USD, inklusive Carry-Anteil): Monatsrendite_i = S_i(m)/S_i(m-1) - 1 + (r_i - r_USD)/12 mit r = 3M-Zins (annualisiert, Vormonatswert).

**Universum und Gratisdaten:**
- EQ (USD-ETFs, iShares MSCI, Start ca. 03/1996, SPY ab 01/1993): SPY, EWC, EWU, EWG, EWQ, EWI, EWP, EWN, EWL, EWD, EWJ, EWA, EWH, EWS (+ optional EWK, EWO, EWW). Taiwan/Korea/Brasilien (EWT, EWY, EWZ) ab 2000 optional.
- FX: Spot USD je Fremdwaehrung fuer EUR, GBP, JPY, CHF, CAD, AUD, NZD, NOK, SEK. Quelle A: FRED H.10 (DEXUSEU ab 1999, DEXJPUS, DEXUSUK, DEXSZUS, DEXCAUS, DEXUSAL, DEXUSNZ, DEXNOUS, DEXSDUS; teils ab 1971) - IDs aus meinem Wissen, nicht verifiziert. Quelle B: Yahoo `EURUSD=X, GBPUSD=X, JPY=X, CHF=X, CAD=X, AUDUSD=X, NZDUSD=X, NOK=X, SEK=X` (Startdaten je Ticker ca. 1996-2003, nicht verifiziert; Yahoo-FX-Daten sind taeglich und dateneigen).
- 3M-Zinsen: FRED `IR3TIB01xxM156N` (OECD, Monatsmittel; xx = US, DE/EZ, GB, JP, CH, CA, AU, NZ, NO, SE). Existenz/Aktualitaet nicht geprueft. CPI: FRED `CPALTT01xxM661N` (OECD) - nicht geprueft.
- CMD: (a) Yahoo-Dauer-Futures `CL=F, HO=F, RB=F, NG=F, GC=F, SI=F, HG=F, PL=F, PA=F, ZC=F, ZW=F, ZS=F, KC=F, SB=F, CT=F, CC=F, LE=F, HE=F` (Start ca. 2000). **Problem:** Yahoos `=F`-Reihen sind nicht roll-bereinigt, Rollspruenge verfaelschen Renditen (enthalten Contango/Backwardation als Luecke), taugen eher als Spot-Naeherung fuer VAL und grob fuer MOM. (b) Rohstoff-ETFs (DBC, GSG, DBA, DBB, DBE, GLD, SLV, USO u.a., Start 2004-2007) mit Total Return, aber kurze Historie und keine 66-Monats-Lookbacks vor ca. 2012. Entscheidung dem Backtester ueberlassen; Empfehlung: (a) fuer Signale, (b) fuer Renditen, wenn Zeitreihen sich decken.
- Anleihen bewusst nicht aufgenommen (AMP: Value in Anleihen mit Standardmass insignifikant, Sharpe 0,18/0,07). Option: Real-Rendite/Term-Spread-Value wie AMP Panel C (FRED OECD `IRLTLT01xxM156N`), aber Inflationsprognosen (Consensus Economics) sind nicht gratis.
- Alternative echte Value-Quelle fuer Laender (BE/ME statt Proxy): Ken French "International Country and Index Portfolios formed on B/M ..." pruefen.

**Belegte Performance:** AMP: 50/50 global alle Assetklassen Sharpe 1,45 (brutto, 1972-2011, Originaluniversum mit Einzelaktien und Futures). Mit dem Gratis-Proxy erwarte ich deutlich weniger (Value-Proxy bei Laendern/Rohstoffen/FX ist Langfrist-Reversal; Rohstoff-Daten roll-verzerrt) - das ist eine Erwartung, kein Messwert.

**Verfall / Replikation:** Autoren zeigen leicht sinkende Einzel-Sharpes 1992-2011 vs. 1972-91 und steigende Korrelation der Value-Strategien ueber Maerkte. Value (HML) hatte 2007-2020 einen Drawdown von 55% (Arnott et al., Snippet). Wie sich die AMP-Faktoren 2013-2026 entwickelt haben, habe ich NICHT geprueft; AQR-Datensatz "Value and Momentum Everywhere: Factors, Monthly" (bis 07/2026) ist der Test dafuer.

**Fehlerfaelle:** (1) Momentum-Crashes bei Marktwenden (Value teilweise Gegengewicht). (2) Vola-Gewichtung mit 36M trailing-Vola kann in Krisen hinterherhinken. (3) Die ETF-Laender-Sleeve mischt FX in USD-Renditen (unhedged) - doppelte FX-Exposure mit dem FX-Sleeve. (4) Kurzer Gratis-Zeitraum (ca. 2001/2006-2026) -> wenige unabhaengige Value-Zyklen (5J-Signal!). (5) Short-Seite bei ETFs praktisch kostenpflichtig/begrenzt; im Backtest synthetisch.

---

### S2: `kmpv_carry_fx_eq_bond_proxy` - Diversifizierter Carry (FX, Aktienindex-Dividendenrendite, Anleihe-Term-Spread) nach Koijen et al.
Regel (Pseudocode):
```
SLEEVES:  FX (9 Waehrungen vs USD, plus USD selbst mit Rendite 0), EQ (14 Laender-ETFs wie S1), BOND (synthetisch, 8-10 Laender)
am Monatsende t:
  FX:   C_i = r3m_i(t) - r3m_USD(t)                      # annualisierte Zinsdifferenz, Monatsmittel Monat t
        Ranking ueber N=10 Laender inkl. USD (KMPV behandelt USD als Land mit FX-Rendite 0)
  EQ:   C_i = (Summe der Barausschuettungen je ETF-Anteil in den 12 Monaten bis t) / P_i(t)    # carry_1-12-Analogon; yfinance Ticker.dividends
  BOND: C_j = y10_j(t) - r3m_j(t)                          # Term Spread (Gl. 14); Roll-down-Term weggelassen (keine 9J11M-Rendite gratis)
  w_k = rankweights(C) je Sleeve
  Sleeve-Gewicht lambda_k = (1/sigma_k)/Summe(1/sigma_j), sigma_k = trailing 36M Vola der Sleeve-Carry-Rendite (ex ante; Burn-in: gleichgewichtet)
  W = lambda_k * w_k
Renditen:
  FX:   S_i(m)/S_i(m-1) - 1 + (r_i - r_USD)/12 - Basis: FRED-Spot/Yahoo-FX
  EQ:   Adj-Close-Rendite der ETFs (USD, ungehedgt)
  BOND: R_j = y10_j(t)/12 - Dmod_j(t)*(y10_j(t+1) - y10_j(t)) - r3m_j(t)/12, Dmod = (1 - (1+y/2)^-20)/y fuer 10J-Par-Anleihe (Gleichung der Annaeherung, [Annahme]); waehrungsgehedgt, Hedgekosten ignoriert
Ausfuehrung: Signal Monatsende t (nur Daten <= t), Handel Schlusskurs t+1d. FRED-Monatsmittel von Monat t sind erst nach Monatsende bekannt -> kein Lookahead im Backtest, aber fuer Live braucht man taegliche Zinsquellen (nicht fuer alle Laender gratis).
```
Daten: siehe S1 (FX, EQ). Anleihen: FRED `IRLTLT01xxM156N` (10J-Renditen, OECD Monatsmittel) und `IR3TIB01xxM156N`. Laender: US, CA, GB, DE, JP, AU, CH, SE, NO (+DK/NZ falls Daten). Nicht verifiziert.
**Fehlend gegenueber dem Paper:** Rohstoff-Carry (Futures-Kurvensteigung) - mit yfinance nicht moeglich, da nur Front-Month-Dauerreihen; keine gratis Kurve mit zweitem Kontrakt von mir geprueft. Rohstoffe waren im Paper die Assetklasse mit der hoechsten Carry-Rendite (11,7% p.a.), ohne sie gehen Diversifikationsgewinn und ein Teil des Edge verloren. Auch Aktien-Carry via ETF-Ausschuettungen ist nur eine Naeherung (Paper: erwartete Dividendenrendite aus Futures minus lokaler Zins).
**Belegt (Preprint, brutto, 1980/83/88/91-02/2011):** diversifiziert Sharpe 1,49 (current carry) / 0,95 (carry1-12); Einzelklassen 0,48-0,93. Korrelationen zwischen Carry-Klassen ca. 0 (FX/Bond 0,23).
**Verfall/Kritik:** FX-Carry ist seit 2008 schwaecher (Snippet). Die 1,49 stammen aus einer "preliminary" Fassung mit In-Sample-Konstruktionswahlen; die JFE-Zahlen habe ich nicht gesehen. Gratis-Version: Aktien-/Bond-Carry teils mit Tagesdaten-Luecken.
**Fehlerfaelle:** Carry-Downturns (Rezessionen/Liquiditaetskrisen, Paper). Equity-Carry ist faktisch ein Dividendenrenditen-Value-Tilt (Sektor/Laender-Konzentration, z.B. hohe Rendite in Krisenlaendern). Bond-Carry: Duration-Risiko bei Zinsanstieg, Roll-down fehlt.

---

### S3: `fx_carry_g10_rank` - G10-Waehrungs-Carry (Rang-Gewichte), optional VIX-Filter
Regel (Pseudocode):
```
UNIVERSE: USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD, NOK, SEK  (N = 10)
am Monatsende t:
  C_i = r3m_i(t) - r3m_USD(t)    # r3m annualisierte 3M-Interbankzinsen (FRED OECD, Monatsmittel Monat t)
  w_i = rankweights(C)           # alle 10 Laender inkl. USD (USD hat FX-Rendite 0)
  Basisvariante A: Zielgewichte W = w
  Variante B (VIX-Filter, [Annahme], nicht aus Papers): m_t = 0.5 falls ^VIX(t) > 80. Perzentil seiner trailing 60 Monate, sonst 1; W = m_t * w
  Variante C (Dollar-Carry, Interpretation des DHL-Abstracts, [Annahme]): falls mean_i(C_i, i != USD) > 0 -> long gleichgewichtet alle 9 Fremdwaehrungen / short USD (je 1 USD), sonst umgekehrt
Rendite Monat t+1d..t'+1d:  R = Summe_i W_i * ( S_i(t'+1d)/S_i(t+1d) - 1 + (r_i(t) - r_USD(t))/12 )    # S = USD je Fremdwaehrung
Ausfuehrung: Schlusskurs t+1d; Rebalancing monatlich.
```
Daten: siehe S1 (Spot, 3M-Zinsen); VIX Yahoo `^VIX` (ab 1990). Die Zinsdifferenz-Approximation ersetzt Forward-Punkte (gratis nicht verfuegbar); sie ignoriert die Cross-Currency-Basis seit 2008 (Abweichung von Covered Interest Parity).
**Evidenz:** KMPV: Waehrungs-Carry mit Rang-Gewichten 11/1983-02/2011 signifikant, aber stark negative Schiefe (Preprint). DHL: dollar-neutraler G10-Carry mit insignifikanten abnormalen Renditen, Dollar-Exposure-Komponente signifikant (Abstract). LRV: Carry-Praemie laesst sich ueber einen Slope-Faktor erklaeren, der mit globaler Aktienvolatilitaet zusammenhaengt (Abstract-Snippet). Snippets (Volltext nicht gelesen): G10-Carry seit 2008 schwaecher; Jurek: crash-neutral Carry statistisch von null nicht unterscheidbar; eine Langfristquelle nennt einen Brutto-Sharpe von ca. 0,47 fuer 2 long/2 short 1975-2015 (nicht verifiziert).
**Verfall:** Ja, sehr wahrscheinlich: Der Rueckgang nach 2008 ist im Snippet beschrieben, Ursache angeblich Zinskompression. Ob die Zinsdifferenzen 2022-2026 (hohe Zinsen in USD/AUD/NZD, niedrig JPY/CHF) die Performance wieder angehoben haben, habe ich nicht geprueft.
**Kosten:** Spot-Spreads in G10 klein; reale Kosten stecken in Swap-/Forward-Punkten und der Basis, die der Zinsdifferenz-Proxy nicht abbildet. Rank-Gewichtung ueber 10 Waehrungen heisst monatlich moderate Umschichtung.
**Tail-Risiko:** Hoechstes der Familie: Crash-Muster (Paper nennt Carry-Downturns bei globalen Rezessionen und Liquiditaetskrisen; konkrete Einzelereignisse habe ich nicht aus den abgerufenen Quellen belegt). Gewinne entstehen langsam, Verluste in Spruengen (negative Schiefe laut KMPV-Preprint).

---

### S4: `country_value_cape_faber_proxy` - Laender-Value (billigstes Drittel) nach Faber/CAPE, mit Gratis-Proxy statt Laender-CAPE
Original (Quantpedia/Faber): Universum 32 Laender; am Jahresende CAPE je Land (realer Index / 10J-Durchschnitt realer Gewinne); billigste 33% waehlen; nur investieren, wenn CAPE < 15 (Rest 0% Cash, kein Zins); gleichgewichtet; jaehrliches Rebalancing. Quantpedia nennt fuer 1980-2011: 14,7% real p.a., Vola 26,1%, Max-Drawdown -27,17%, Sharpe 0,56 (Figure 9 der Quelle). Die Drawdown-Zahl wirkt klein im Verhaeltnis zur Vola (vermutlich auf Jahresbasis berechnet). Sekundaer (Snippet): billigstes Drittel 13,5% p.a. vs. 9,4% Equal-Weight (1980-2011, 32 Laender, Lokalwaehrung, brutto); Buchfassung 2014: 44 Laender, 1980-2013, billigste 25%; CAPE-Filter 18 (statt 15) laut Snippet. Keine Transaktionskosten. Faber selbst raeumt In-Sample-Verzerrungen ein.

Gratis-Proxy-Regel (Pseudocode) - **KEIN Laender-CAPE**, da Laender-CAPEs nicht gratis verfuegbar sind (Faber-Daten: Global Financial Data/Morningstar laut Snippet):
```
UNIVERSE: 14 Laender-ETFs wie S1 (EQ-Sleeve)
am letzten Handelstag im Dezember (t):
  RP_i = P_i(t) / mean( P_i ueber die letzten 120 Monatsenden bis t )         # P = Total-Return-Index (Adj Close, USD)
         (optional inflationsbereinigt mit US-CPI; fuer Rangfolge irrelevant)
  Kandidaten: ETFs mit >= 120 Monaten Historie
  Auswahl: die floor(N/3) Laender mit dem kleinsten RP_i
  Gewichte: gleich, Summe 1 (long only); kein Cash-Filter (CAPE-Schwelle nicht uebertragbar)
Ausfuehrung: Kauf zum Schlusskurs t+1d, Halten 12 Monate, dann Neuauswahl.
Benchmark: gleichgewichteter Korb aller Kandidaten (Rebalancing jaehrlich).
```
Gratis-Datenstart: Signale ab 12/2006 (ETFs ab 03/1996 + 120 Monate) -> nur ca. 19 Jahresentscheidungen. Statistisch praktisch nicht belastbar.
**Bessere Daten pruefen:** Ken French "International Country and Index Portfolios formed on B/M, E/P, CE/P, D/P" (siehe Datenquellen); US-CAPE: Shiller-Datei ab 1871.
**Evidenz-Staerke:** niedrig-mittel. Nur In-Sample-Backtests; Autor und Quantpedia warnen vor langem Horizont (5-10 Jahre), fehlender Absicherung (long-only), Hindsight. Kein publizierter Out-of-sample-Test der exakten Regel gefunden. Verwandtes Live-Produkt Cambria GVAL (Laenderwahl nach langfristigem Discount + Aktienauswahl) hinkt dem MSCI ACWI laut Snippet hinterher (Annualisiert seit Start bis Apr 2018 3,28% vs. 8,18%; 10J-Sharpe bis 03/2026 0,48 vs. 0,69) - nicht dieselbe Regel, nur Indiz.
**Fehlerfaelle:** Value-Fallen/Krisenlaender (Billig bleibt billig, 5-10J), Waehrungseffekte (USD-ETFs), Kosten/ETF-Spreads, Konzentration in wenigen Laendern (5 von 14), Selektionsbias durch ETF-Survivorship (Laender-ETFs, die es heute gibt).

---

### S5: `us_value_hml_etf_pair` - Large-Cap-Value minus Growth (HML-artig) als ETF-Paar - **"funktioniert nach Kosten nicht belastbar"** (Negativ-/Gegenprobe)
Regel (Pseudocode):
```
am Monatsende t:
  Position: long IWD (iShares Russell 1000 Value), short IWF (iShares Russell 1000 Growth), je gleicher USD-Betrag (dollar-neutral), Kapitaleinheit 1
  Rendite = R(IWD) - R(IWF)  (Adj-Close-Renditen), monatlich rebalanciert auf 50/50-Gewichte
Ausfuehrung: Schlusskurs t+1d.
Forschungs-Benchmarks (gratis): Ken French HML (Fama/French 3 Faktoren US, Developed, Europe, Japan, Asia Pacific ex Japan) und AQR "The Devil in HML's Details: Factors, Monthly"
Optionale Long-only-Variante: IWD statt SPY, Excess-Return gegen SPY auswerten.
```
IWD/IWF: Start ca. 05/2000 [Wissen, Datenstart nicht geprueft].
**Evidenz:** AMP: Value in US-Large-Caps 1972-2011: P3-P1 3,7% p.a. (t = 1,83, nicht signifikant auf 5%), Sharpe 0,29; global besser (6,2%, t = 3,60). Arnott et al.: HML seit 2007 mit 55% Drawdown (Mitte 2020); Erklaerung ueber Bewertungsspread-Kompression und fehlende Intangibles im Buchwert. Daraus folgt: reine ETF-Paar-Variante hat nach Kosten keine belastbare Erwartung; Rebound-Argument hat Gegenspieler (Intangibles verschlechtern HML als Value-Mass). Fama-French-Primaerliteratur (1992/2015) habe ich nicht abgerufen und kann daher keine Aussage ueber die Rolle von HML im 5-Faktor-Modell belegen.
**Kosten:** Zwei ETFs, TER je ca. 0,19% [Wissen, nicht verifiziert], Short-Kosten; Brutto-Edge klein -> Kostenempfindlichkeit hoch.
**Verwendung:** als Kontrollstrategie/Negativbeispiel und zur Gegenpruefung der Pipeline (falls die Pipeline hier "Edge" findet, ist sie vermutlich zu optimistisch).

---

## 5. Was ich NICHT gratis nachbauen kann (ehrlich)
- Rohstoff-Carry (Kurvensteigung): Yahoo liefert nur Front-Month-Dauerreihen (`=F`), keine zweiten Kontrakte. Proxy waeren Roll-Yield-Differenzen zwischen Rohstoff-ETFs - ungeprueft, unscharf. Kein Strategieeintrag.
- Laender-CAPE: nicht gratis. Nur Shiller-US-CAPE (ab 1871). Option: Ken-French-Laenderportfolios nach D/P, E/P (Struktur ungeprueft).
- Aktien-Einzeltitel-Value (BE/ME): nicht aus Yahoo ableitbar (Fundamentals unzuverlaessig); gratis nur ueber Ken-French-Faktoren, nicht handelbar.
- Anleihen-Value mit Realrendite: Inflationsprognosen (Consensus Economics) nicht gratis.

## 6. Hinweise fuer die Pipeline
1. Out-of-sample-Pruefung der AMP-Idee 2013-2026 mit AQR-Datensatz "Value and Momentum Everywhere: Factors, Monthly" (Stand 07/2026) und "Devil in HML" vor dem Bau der ETF-Proxy-Versionen.
2. Walk-forward, keine Parameteroptimierung ausser den dokumentierten (66-54 Monate Value-Fenster, 12-1 Momentum, 36M Vola). VIX-Filter in S3B und Dollar-Carry-Variante sind eigene Entwuerfe - separat markieren und Deflated-Sharpe beachten.
3. Alle Kosten-Annahmen oben sind Platzhalter und nicht aus den Papers; Ergebnis stets mit 0x / 1x / 2x Kosten berichten.
4. Wenn die Pipeline Strategien ueber den ex-post-Schwellenwert "Sharpe > x" auswaehlt, ist S4 wegen ~19 Jahresentscheidungen nicht statistisch pruefbar; als Informationsstrategie behandeln.
5. Rohstoff-Futures mit Rollspruengen nicht ohne Roll-Bereinigung fuer Renditen verwenden.

## 7. US-CAPE-Timing (nicht als eigene Strategie aufgenommen, nur Gedanke)
Eine US-Aktien/Anleihe-Allokation nach CAPE-Perzentil (Shiller-Daten ab 1871, SPY/IEF ab 2002 bzw. Shiller-Totalrenditereihe) ist technisch trivial und hat 150 Jahre Daten, aber nur sehr wenige unabhaengige Bewertungszyklen. Die einzige Quelle in meinem Material (Asness 2012 via Sekundaerbericht, Snippet) spricht fuer einen 10-Jahres-Horizont, nicht fuer taktisches Timing; mehrjaehrige Hoch-CAPE-Phasen (insb. seit 2010) laufen gegen eine Timing-Regel. Deshalb habe ich keine eigene Regel mit Parametern erfunden. Wenn gewuenscht: Perzentil des CAPE im erweiterten Fenster -> Aktiengewicht linear in [0.2, 1.0] - waere reine Eigenentwicklung ohne Paper-Beleg.
