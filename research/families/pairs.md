# Familie: Pairs Trading / Statistische Arbitrage

Stand der Recherche: 2026-10-11. Budget war ca. 15 Web-Abrufe; tatsaechlich genutzt: 7 Websuchen + 8 Seitenabrufe = 15. Vier Abrufe lieferten nur Binaer-PDF, die ich lokal mit pdftotext gelesen habe (Krauss-Review, Avellaneda-Lee, Fil, Clegg-Krauss), das ist also Volltext-Niveau.
Alle Zahlen stammen aus tatsaechlich gelesenen Seiten/PDFs oder sind als "Suchergebnis", "Zitat laut Krauss" bzw. "aus Gedaechtnis" markiert. Was ich nicht gefunden habe, steht ausdruecklich als "nicht gefunden".

## 0. Kurzfazit (ehrlich)

- Pairs Trading ist eine der best-dokumentierten Anomalien und zugleich eine der am staerksten verfallenen. Alle Quellen, die ich gelesen habe, zeigen: die klassische Distanz-Methode (Gatev/Goetzmann/Rouwenhorst, GGR) verdiente bis 2002 ca. 11 % p.a. Excess Return (Quantpedia-Seite, Krauss), danach faellt sie nach realistischen Kosten auf null oder darunter.
- Die haertesten Belege fuer "tot nach Kosten":
  - Clegg & Krauss (2016, Volltext gelesen), S&P 500 ohne Survivorship-Bias, 1990-2015, Kosten 5 bp pro Halbumschlag und Aktie: GGR, Kointegration (CI1/CI2) und sogar die neue Partial-Cointegration-Methode (PCI) liefern im Teilzeitraum 01/2010-10/2015 NACH Kosten annualisiert ca. -0,2 % (GGR), -1,7 % (CI1), -0,6 % (CI2), -2,8 % (PCI), waehrend der Markt +13,1 % macht (Table 13, siehe Abschnitt 6 zur Tabellenzuordnung).
  - Fil (arXiv 2020, Volltext gelesen), NYSE 1990-2020, Kosten 26-35 bp einseitig plus 0,6 % p.a. Leihgebuehr: Basisregel unter 0,2 % pro Monat gegen 0,47 % Markt.
  - Rad/Low/Faff (Quantitative Finance 2016, nur Abstract-Ebene ueber Suchergebnis): netto 38 bp (Distanz), 33 bp (Kointegration), 5 bp (Copula) pro Monat, 1962-2014; Handelsgelegenheiten von Distanz und Kointegration sanken ab 2009 deutlich.
- Das einzige ueber mehrere unabhaengige Quellen wiederkehrende "Funktioniert"-Muster: Pairs Trading verdient in Krisen/Baerenmaerkten (Liquiditaetsbereitstellung). Do/Faff 2010, Fil 2020 (ca. 2 % pro Monat Excess im Baerenmarkt, ca. 1 % hinter dem Markt im Bullenmarkt), Clegg/Krauss (GFC 09/2008-12/2009: GGR +5,2 % p.a. netto, PCI +49 %). Aber: man weiss nicht vorher, wann der Baerenmarkt beginnt (Fil sagt das selbst: Foresight-Bias). Und Huck (2015), zitiert nach Krauss, fand, dass VIX-Timing die Pairs-Renditen NICHT verbessert.
- Wichtige Datenfalle fuer Quant-Lab: Alle Aktien-Varianten brauchen eine survivorship-freie Konstituentenhistorie. Gratis gibt es nur die HEUTIGE S&P-500-Liste (Wikipedia). Fuer Mean-Reversion-Strategien ist das besonders heikel, weil Verlierer, die weiter fielen oder delisted wurden, fehlen. Jede Aktien-Backtest-Zahl aus Gratisdaten ist deshalb eine OBERE Schranke. Der saubere Gratis-Test ist die ETF-Variante (Strategie 5).
- Fuer Nick praktisch: Leerverkauf einzelner Aktien/ETFs ist bei einem deutschen Retail-Broker nur ueber CFDs/Derivate machbar. Verlustverrechnung bei Termingeschaeften/CFDs ist in Deutschland eingeschraenkt (nach meiner Erinnerung 20.000 EUR pro Jahr, §20 Abs. 6 EStG; NICHT in dieser Sitzung geprueft). Vor jedem echten Einsatz klaeren.
- Empfohlene Test-Reihenfolge im Quant-Lab (anders als die Robustheits-Rangfolge unten): 5 (ETF, datenehrlich) vor 2 und 3 (Aktien, nur mit Bias-Hinweis), 1 nur wenn man Tagesumschlag mit realistischen Kosten testet.

Ranking-Begruendung: "Robustheit" = Breite unabhaengiger Evidenz x Kostenfestigkeit x Post-2002-Verhalten. Keine der fuenf Strategien hat eine belegte positive Nach-Kosten-Rendite nach 2010. Platz 1 (Avellaneda-Lee) hat die beste dokumentierte Nach-Kosten-Zahl (Sharpe 0,9 bis 1,5 in 2003-2007), aber nur von den Autoren selbst und mit Same-Close-Ausfuehrung; Platz 5 hat gar keine direkte Evidenz.

## 1. Abrufstatus (Transparenz)

| Quelle | Status |
|---|---|
| Krauss, Statistical arbitrage pairs trading strategies: Review and outlook (IWQW Discussion Paper 09/2015, https://www.iwf.rw.fau.de/files/2016/03/09-2015.pdf; Journal of Economic Surveys 31(2), 513-545, 2017) | ABGERUFEN (WebFetch lieferte nur Binaer), lokal mit pdftotext GANZ lesbar. Quelle fuer GGR-Regel, Do/Faff, Huck, Chen et al., Caldeira/Moura, Bowen et al. u.a. Hinweis: Das ist die Working-Paper-Fassung, nicht die Journalfassung. |
| Quantpedia "Pairs trading with stocks" https://quantpedia.com/strategies/pairs-trading-with-stocks | ABGERUFEN, Text gelesen. Sekundaerquelle fuer GGR-Zahlen (11,16 %, Vol 5,85 %, Sharpe 1,22, 162 bp Kosten pro Paar, 1962-2002). Die Seite widerspricht sich intern (Max-DD "-17 %" bei Hinweis "not stated"; 11,16 %/5,85 % ergibt nicht Sharpe 1,22). Zahlen daher nur mit Vorbehalt. |
| Avellaneda & Lee 2010 (Quantitative Finance 10(7), 761-782), NYU-Autorenseite, PDF-Fassung vom 11.07.2008: https://math.nyu.edu/~avellane/AvellanedaLeeStatArb071108.pdf | ABGERUFEN (Binaer), lokal ganz lesbar. Regeln und Zahlen unten stammen direkt aus dieser Fassung. |
| Fil 2020, Gold Standard Pairs Trading Rules: Are They Valid? https://arxiv.org/abs/2010.01157 (PDF https://arxiv.org/pdf/2010.01157) | ABGERUFEN (Abstract-Seite + PDF lokal gelesen). Tabelle 2 ist im Text verzerrt, nur Fliesstext-Zahlen verwertet. |
| Clegg & Krauss 2016, Pairs trading with partial cointegration (IWQW 05/2016), https://www.iwf.rw.fau.de/files/2016/05/05-2016.pdf | ABGERUFEN (Binaer), lokal gelesen (Abstract, Methodik, Tabellen 8, 9, 11, 13). Tabellenspalten sind im Text verzerrt, Zuordnung per Plausibilitaetspruefung gegen den Fliesstext (siehe Abschnitt 6). Die spaetere Journalfassung (Quantitative Finance 2018) NICHT gesehen. |
| Huck & Afawubo 2015, Applied Economics 47(6), 599-613, https://ideas.repec.org/a/taf/applec/v47y2015i6p599-613.html | ABGERUFEN, nur Abstract-Ebene. Keine Zahlen, kein Stichprobenzeitraum auf der Seite. Clegg/Krauss konnten die Huck-Ergebnisse NICHT reproduzieren (siehe unten). |
| Han, He & Toh 2023, Pairs trading via unsupervised learning (EJOR 307(2), 929-947), https://ideas.repec.org/a/eee/ejores/v307y2023i2p929-947.html | ABGERUFEN, nur Abstract-Ebene. Regeln NICHT verifiziert, Firmencharakteristika sind nicht gratis. Deshalb keine Strategie. |
| Do & Faff 2010, Does simple pairs trading still work? (FAJ 66(4), 83-95), https://research.bond.edu.au/en/publications/does-simple-pairs-trading-still-work/ | NUR Suchergebnis (Abstract-Ebene aus mehreren Bibliotheksseiten). Zahlen im Detail nur ueber Krauss und Clegg/Krauss. Volltext nicht gelesen. |
| Rad, Low & Faff 2016, Quantitative Finance 16(10), 1541-1558, https://research.bond.edu.au/en/publications/the-profitability-of-pairs-trading-strategies-distance-cointegrat/ | NUR Suchergebnis (Abstract-Ebene). Volltext nicht gelesen. |
| Chen, Chen, Chen & Li 2019, Empirical Investigation of an Equity Pairs Trading Strategy (Management Science 65(1), 370-389), https://ideas.repec.org/a/inm/ormnsc/v65y2019i1p370-389.html | NUR Suchergebnis (Abstract-Ebene). Regeldetails ueber Krauss (WP-Fassung Chen/Chen/Li 2012). |
| Gatev, Goetzmann, Rouwenhorst 2006 (RFS 19(3), 797-827) | NICHT selbst abgerufen. GGR-Regel und Zahlen nur ueber Krauss, Quantpedia, Clegg/Krauss, Fil. |
| Do & Faff 2012 (J. Financial Research 35(2), 261-287), Vidyamurthy 2004 (Buch), Jacobs & Weber 2015, Bowen et al., Mori/Ziobrowski, Caldeira/Moura u.a. | NICHT selbst abgerufen, nur als Zitate innerhalb von Krauss bzw. Clegg/Krauss verwendet und als "laut Krauss" markiert. Nicht als Paper gefuehrt. |

Ungeprueft gefundene Spuren (NICHT gelesen, nur Treffer in der Suche, keine Quelle fuer irgendeine Zahl): Pandini 2026 "Stationary but not profitable: a critical look at pairs trading" (nur Dateiname eines prnewswire-PDFs), Sun 2025 Warsaw Working Paper 19/2025 (Update-Survey 2016-2023, laut Suchergebnis), diverse Masterarbeiten (Aalto, Durham, Utu zu Krypto-Pairs). Diese koennten die Post-2015-Luecke schliessen und sind der erste Ort fuer eine Folgerecherche.

## 2. Gemeinsame Implementierungsregeln (fuer alle Strategien)

- Signal am Schlusskurs t. Handel fruehestens t+1. Hauptvariante: Ausfuehrung zur Eroeffnung t+1 (yfinance auto_adjust=True, dann sind Open/High/Low/Close konsistent dividenden- und splitbereinigt). Sensitivitaet: Schlusskurs t+1. GGR selbst verwendeten schon einen Ein-Tages-Lag zur Entschaerfung von Bid-Ask-Bounce (Fil, Clegg/Krauss). Avellaneda-Lee handelten im Backtest zum Schlusskurs desselben Tages wie das Signal (Original-Text Abschnitt 5) = optimistisch, hier korrigiert.
- Kosten-Raster (Pflicht, Quant-Lab-Regel 4):
  - Basis: 5 bp pro Halbumschlag pro Bein (Avellaneda-Lee und Clegg/Krauss, d.h. 10 bp Round-Trip pro Bein, 20 bp Round-Trip pro Paar mit zwei Beinen).
  - Streng: 26 bp einseitig (Fil 2009-2020) bzw. 30-35 bp (Fil 1990-2007), plus 0,6 % p.a. Leihgebuehr auf Short-Beine (Fil, nach D'Avolio 2002).
  - Historischer Anker: GGR-Schaetzung 162 bp pro Paar Round-Trip fuer Top-20 (Quantpedia-Seite, 1962-2002).
  - ETF-Variante: eigene Annahme 3 bp pro Halbumschlag pro Bein, nicht aus einem Paper.
- Rendite auf COMMITTED capital berichten (Kapital pro Paar wird bei Periodenstart reserviert, egal ob das Paar handelt). Das ist konservativer als "fully invested" und ist die Konvention bei GGR/Clegg-Krauss.
- Survivorship: Aktien-Universum = heutige S&P-500-Liste (Wikipedia "List of S&P 500 companies", Yahoo-Ticker mit '.' ersetzt durch '-'). Das ist verzerrt. Ergebnisse als obere Schranke lesen. Share-Class-Duplikate ausschliessen (GOOG/GOOGL, FOX/FOXA, NWS/NWSA, sowie jedes Paar mit Tagesrenditen-Korrelation > 0,99), sonst gewinnt die Distanzauswahl mit "Paaren", die derselbe Emittent sind.
- Sektor: aktuelle GICS-Zuordnung aus der Wikipedia-Liste. Achtung: GICS wurde 2018 umgebaut (Communication Services); historische Sektorzuordnung ist damit ungenau. Alternative ohne dieses Problem: Fama-French-Industrien nur fuer ETF/Portfolio-Tests.
- Walk-forward: Alle Parameter sind festgelegt (keine Optimierung auf den Daten). Fil zeigt, dass "adaptive" Parameterwahl (alle 2 Jahre neu optimiert) schlechter war als die festen GGR-Parameter. Huck (2013, laut Krauss): GGR-Renditen reagieren sehr empfindlich auf die Formationslaenge (gut bei 6, 18, 24 Monaten, Einbruch bei 12). Mehrfachtest-Korrektur (Deflated Sharpe/PBO) Pflicht, Parameter-Sweeps nur als Sensitivitaet.
- Hypothese vor Test: Abbruchkriterium-Vorschlag fuer alle Pairs-Varianten (zur Eintragung in docs/HYPOTHESEN.md): Verwerfen, wenn netto (Basis-Kosten, 2010-2026, Walk-forward) Sharpe < 0,3 oder Sharpe unter SPY-Buy-and-Hold, oder wenn der Gewinn von einem Einzeljahr (2020, 2022) getragen wird.

## 3. Strategien

Rangfolge nach erwarteter Robustheit, beste zuerst. Ehrlicher Gesamteindruck: Platz 1-2 haben noch eine kleine Chance, Platz 3-5 sind Dokumentation von "wahrscheinlich tot".

### Strategie 1: ae_sector_etf_residual_sscore (Avellaneda-Lee, ETF-Faktor-Version)

Idee: Aktienrendite gegen ihren Sektor-ETF regressieren, das kumulierte Residuum als Ornstein-Uhlenbeck-Prozess behandeln, den "s-score" als Distanz zum Gleichgewicht handeln.

Regel (aus dem Original-PDF, Abschnitte 3-5 und Appendix; Abweichungen markiert):
1. Taeglich, am Schlusskurs t, fuer jede Aktie i mit mindestens 60 Handelstagen Historie und zugeordnetem Sektor-ETF E(i).
2. OLS ueber die letzten 60 Tagesrenditen (Tage t-59..t): R_i,s = a + beta_i * R_E,s + eps_s.
3. Kumulatives Residuum X_k = Summe der eps_s bis k, k=1..60 (X_60 = 0 per Konstruktion mit Intercept).
4. AR(1)-Regression ueber k=1..59: X_{k+1} = a_X + b * X_k + zeta. Aktie ist nur zugelassen, wenn 0 < b < 0.9672 (aequivalent kappa = -ln(b)*252 > 8.4, d.h. Mean-Reversion-Zeit unter ca. 30 Handelstagen).
5. m_i = a_X/(1-b). sigma_eq,i = sqrt( Var(zeta) / (1 - b^2) ).
6. Zentrierung: m_bar = Querschnittsmittel der m_j aller an diesem Tag zugelassenen Aktien. s_i = (-(m_i) + m_bar) / sigma_eq,i. (Das ist Gleichung (22) des Papers, Original-Text: "centered means work better".)
7. Signal bei Flat: Long-Eroeffnung wenn s_i < -1,25. Short-Eroeffnung wenn s_i > +1,25. Schliessen: Long wenn s_i > -0,50. Short wenn s_i < +0,75. (Cutoffs sbo=sso=1,25, sbc=0,75, ssc=0,50, vom Autor empirisch auf 2000-2004 gewaehlt = Data-Mining-Risiko.)
8. Position: Long Aktie = $1 Aktie + Short beta_i Dollar des Sektor-ETF. Short Aktie = umgekehrt. beta_i wird beim Eroeffnen fixiert und bis zum Schliessen gehalten.
9. Groesse: pro neuer Position lambda = 2/100 = 2 % des aktuellen Eigenkapitals (A-L: "2+2"-Hebel bei 100 Long/100 Short), maximal 100 Long- und 100 Short-Positionen gleichzeitig; bei Ueberzahl Prioritaet nach groesstem |s|. Positionen werden nicht nachgesteuert ("bang-bang").
10. Ausfuehrung: Orders aus Schluss t zur Eroeffnung t+1 (Abweichung vom Paper: dort Schlusskurs t). Taegliche Pruefung, keine festen Rebalancing-Tage.
11. Kosten: 5 bp pro Halbumschlag pro Bein, Leihgebuehr 0,6 % p.a. auf Short-Aktie.

Universum gratis: Aktien = heutige S&P-500-Konstituenten (Survivorship-Bias). Sektor-ETFs XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY (Datenstart ca. Dezember 1998, aus Gedaechtnis, vor Nutzung per yfinance pruefen), XLRE ab ca. Oktober 2015 und XLC ab ca. Juni 2018 (aus Gedaechtnis). Zuordnung: Materials->XLB, Energy->XLE, Financials->XLF, Industrials->XLI, Information Technology->XLK, Consumer Staples->XLP, Utilities->XLU, Health Care->XLV, Consumer Discretionary->XLY. Real Estate/Communication Services erst ab ETF-Start handeln, sonst ausschliessen. Das Original nutzte 15 ETFs, die teils nicht mehr existieren, und fuer 1996-2002 synthetische kapitalgewichtete Sektorindizes.

Evidenz im Original: Nach Kosten (10 bp Round-Trip) Sharpe 1,44 fuer PCA-Strategien 1997-2007, aber nur 0,9 in 2003-2007; ETF-Strategien 1,1 (1997-2007) "mit aehnlicher Verschlechterung nach 2002"; mit Volumengewichtung ("trading time") ETF-Strategie Sharpe 1,51 in 2003-2007. Krauss: Ergebnisse "nicht robust gegen Data Mining", weil die Autoren Schwellen ausprobiert haben.

Risiken: August 2007 "Quant Quake" (A-L reproduzieren den Drawdown und stuetzen die Khandani-Lo-Entpackungstheorie). Hohe Umschlagshaeufigkeit macht die Strategie kostenempfindlich: mit 26 bp einseitig (Fil) wuerde jede Round-Trip rund 100 bp pro Bein kosten, das frisst jede plausible Edge. Ob die ETF-Residuum-Reversion nach 2008 noch existiert, steht in keiner gelesenen Quelle (Clegg/Krauss: PCI, das auf Reversal laedt, ist 2010-2015 netto negativ).

### Strategie 2: coint_sector_pairs_sp500 (Kointegrations-Paare, zweistufig, innerhalb GICS-Sektor)

Regel (Auswahl nach Rad/Low/Faff-"Efficient two-step" wie von Fil beschrieben, Handel nach Clegg/Krauss CI1; Eigenzusaetze markiert):
1. Studienperioden: Formationsende t0 alle 126 Handelstage (halbjaehrlich, nicht ueberlappend). Formation F = 252 Handelstage bis t0. Handelsfenster T = die naechsten 126 Handelstage.
2. Zugelassene Aktien: heutige S&P-500-Liste, keine Luecken in F, gleicher GICS-Sektor pro Paar, kein Share-Class-Duplikat (siehe Abschnitt 2).
3. Normierter Preisindex: P_t / P_{t0-251} (Adjusted Close). Fuer alle Same-Sector-Paare SSD = Summe (P_i,t - P_j,t)^2 ueber F. Liste aufsteigend nach SSD sortieren.
4. In dieser Reihenfolge der Reihe nach testen: Engle-Granger (statsmodels.tsa.stattools.coint, trend='c', autolag='aic') auf log-Preisen, y = ln P_j, x = ln P_i, mit i,j in alphabetischer Ticker-Reihenfolge. Paar akzeptieren wenn p < 0,05 UND beide Aktien noch in keinem akzeptierten Paar sind (Eigenzusatz, vermeidet Konzentration) UND Halbwertszeit der Spread-Reihe (AR(1) auf w) zwischen 2 und 60 Tagen (Untergrenze entspricht Clegg/Krauss rho > 0,5, Obergrenze Eigenzusatz). Stopp bei 20 akzeptierten Paaren oder nach 3.000 getesteten Kandidaten.
5. Hedge: OLS ln P_j = alpha + beta * ln P_i + w auf F. Spread w_t = ln P_j,t - alpha - beta * ln P_i,t. sigma_w = Standardabweichung von w ueber F. Alle drei Groessen (alpha, beta, sigma_w) bleiben im Handelsfenster fest. Paar verwerfen, wenn beta ausserhalb [0,2; 5].
6. z_t = w_t / sigma_w am Schlusskurs t.
7. Eroeffnen (wenn Paar flat): z_t > +2 -> Short-Spread (Short j, Long i). z_t < -2 -> Long-Spread (Long j, Short i). Ausfuehrung Open t+1.
8. Schliessen: Short-Spread, wenn z_t <= 0. Long-Spread, wenn z_t >= 0 (c = 0, wie CI1). Ausfuehrung Open t+1. Alle offenen Positionen am letzten Tag des Handelsfensters schliessen (Open des Folgetags = erster Tag der naechsten Periode, dort werden neue Paare gebildet). Wiedereroeffnung nach Schliessen im selben Fenster erlaubt.
9. Position pro Paar: Kapital-Slot = Eigenkapital/20 (committed). Beine: Slot fuer das groessere Bein, kleineres Bein = Slot * min(beta, 1/beta). Keine Nachsteuerung.
10. Stop-Loss: Hauptvariante ohne (CI1, GGR). Vorregistrierte Variante: Schliessen und fuer den Rest des Fensters sperren, wenn der Paar-Verlust 10 % des Slots erreicht (wie CI2 bei Clegg/Krauss).
11. Kosten wie in Abschnitt 2.

Evidenz:
- Rad/Low/Faff (Abstract, Suchergebnis): US-Gesamtmarkt 1962-2014, mittlere Monats-Excess-Rendite VOR Kosten Distanz 91 bp, Kointegration 85 bp, Copula 43 bp; NACH Kosten 38 / 33 / 5 bp. Distanz und Kointegration verlieren ab 2009 deutlich an Handelsgelegenheiten. Kointegration ist in turbulenten Maerkten am besten. Alle Alphas bleiben nach Risikofaktoren positiv und signifikant.
- Huck & Afawubo (Abstract): S&P-500-Konstituenten, nach Risiko- und Kostenkontrolle ist die Distanzmethode statistisch insignifikant, Stationaritaetsauswahl schwach, Kointegration "high, stable, robust". Laut Krauss ist die Spread-Volatilitaet kointegrierter Paare fast doppelt so hoch wie die von Distanzpaaren.
- ABER Clegg/Krauss (Volltext): "We have not been able to reproduce the higher returns of Huck (2015); Huck and Afawubo (2015)" (Daten, Survivorship-Behandlung, laengerer Zeitraum). Eigene Zahlen S&P 500 1990-2015: CI1 0,20 %/Monat brutto, CI2 0,15 %; annualisiert nach Kosten (Table 11) ca. 1,6 % (CI1) und 1,1 % (CI2), Sharpe -0,24 bzw. -0,37; 2010-10/2015 nach Kosten CI1 -1,7 %, CI2 -0,6 % p.a.
- Fil (Volltext): Kointegration hat die hoehere Obergrenze (bis 1,03 % Monatsprofit ueber 1990-2020 mit nachtraeglich optimalen Parametern, gegen 0,64 % Distanz), aber mit statischen Regeln "nur 0,23 % und 0,26 % pro Monat" (Distanz, Kointegration), also unter dem Markt.
- Krauss: Das Multiple-Testing-Problem wird in vielen Kointegrationsstudien nicht kontrolliert (Beispiel: 1.225 Paare bei alpha 5 % -> erwartet 61 Fehlalarme). Hier Teil-Abhilfe durch SSD-Vorauswahl plus Halbwertszeit-Filter, keine formale FWER-Kontrolle (Cummins/Bucca 2012 laut Krauss waere der naechste Schritt).

Risiken: Kointegrationsbruch (Fusion, Gewinnwarnung) ohne Stop = grosse Linksschwanz-Verluste. Look-ahead bei Sektor- und Konstituenten-Listen. Hohe Parameter-Empfindlichkeit.

### Strategie 3: ggr_distance_sector_zerocross (klassische Distanz-Paare mit Do/Faff-artigen Filtern)

Regel (GGR-Kern laut Krauss, Quantpedia, Clegg/Krauss; Filter nach Do/Faff NUR als Idee, Rangsummen-Formel ist Eigenentwurf, weil ich Do/Faff 2012 nicht gelesen habe):
1. Perioden wie Strategie 2 (126-Tage-Rhythmus), Formation 252 Tage, Handel 126 Tage. (GGR-Original: 12 Monate Formation, 6 Monate Handel.)
2. Preisindex: kumulierter Total-Return-Index (Adjusted Close), auf 1 normiert am ersten Formationstag. SSD ueber F fuer alle Same-Sector-Paare.
3. Baseline GGR (Kontrolle, immer mitlaufen lassen): die 20 Paare mit kleinster SSD.
4. Do/Faff-artige Variante: fuer jedes Paar zusaetzlich Nullstellen-Zaehler N = Anzahl der Vorzeichenwechsel des Spreads P_i - P_j in F. Rang_SSD (aufsteigend) + Rang_N (absteigend) = Rangsumme, die 20 Paare mit kleinster Rangsumme. (Do/Faff begruenden die Zero-Crossings als Proxy fuer Mean-Reversion-Staerke, laut Krauss.)
5. Handelsfenster: Preisindex am ersten Handelstag auf 1 neu normieren (Krauss-Beschreibung von GGR; Clegg/Krauss nutzen dagegen die rohen Preise: bei Implementierung als Schalter fuehren und beide Fassungen berichten). sigma = Standardabweichung des Spreads in F (aus der Formation-Normierung).
6. Eroeffnen bei |Spread_t| > 2*sigma am Schluss t; Ausfuehrung Open t+1. Spread > 0: Short i, Long j. Spread < 0: Long i, Short j. Gleiche Dollarbetraege pro Bein.
7. Schliessen: Spread kreuzt 0 (Schluss t, Ausfuehrung Open t+1) oder Ende des Handelsfensters. Wiedereroeffnung im selben Fenster erlaubt.
8. Kapital: Eigenkapital/20 pro Paar (committed).
9. Kosten wie in Abschnitt 2.

Evidenz:
- GGR (laut Quantpedia-Seite und Krauss): 1962-2002 ca. 11,16 % p.a. bei Top-20, Vol 5,85 %, Sharpe 1,22 (Seite, interne Unstimmigkeit), kein Laden auf Standard-Risikofaktoren, 162 bp Kosten pro Paar Round-Trip -> netto 113-225 bp pro 6 Monate. Quantpedia nennt einen Post-Publikations-Test 1999-2002 mit 10,4 % p.a. Excess (Top-20; ob vor oder nach Kosten, steht auf der Seite nicht eindeutig).
- Do/Faff (laut Krauss): CRSP 1962-2009. Profitabilitaet sinkt, vor allem weil mehr Paare nicht konvergieren (32 % der Distanz-Paare konvergieren nicht). Mit Kosten ist die GGR-Basisregel "weitgehend unprofitabel". Mit Industrie-Beschraenkung (48 FF-Industrien) + Zero-Crossings + SSD bleibt es "leicht profitabel" nach vollen Kosten, aber anfaellig fuer Data Snooping (29 getestete Auswahlkombinationen). Abstract (Suchergebnis): sehr stark in anhaltenden Turbulenzphasen inkl. GFC; zusaetzliche Algorithmen/Masse bringen ca. 22 bp/Monat bei Bankaktien.
- Clegg/Krauss S&P 500 1990-2015: GGR brutto 0,15 %/Monat (Do/Faff in ihren Daten: 0,56 % fuer 1989-2002 und 0,33 % fuer 2003-2009, laut Clegg/Krauss), netto annualisiert ca. 1,1 % bei Sharpe -0,55 (Table 11). Sub-Perioden netto (Table 13, mean return): 1990-03/2001 ca. 2,5 %; 04/2001-08/2008 -0,6 %; GFC 09/2008-12/2009 ca. +5,2 %; 01/2010-10/2015 ca. -0,2 %.
- Fil (NYSE 1990-2020): Basisregel (Top 20, 2 sigma, 12/6 Monate) unter 0,2 %/Monat gegen Markt 0,47 %; Baerenmarkt-Excess ca. 2 %/Monat, Bullenmarkt ca. 1 % hinter dem Markt.
- Krauss' Kritik: SSD waehlt Paare mit niedriger Spread-Varianz (wenig Gewinnpotenzial) und ohne Kointegrationstest (hohes Divergenzrisiko).

Risiken: Nicht-konvergierende Paare, Delisting, Formationslaengen-Empfindlichkeit (Huck 2013 laut Krauss).

### Strategie 4: chen_comovement_reversal (Return-Korrelations-"Paare" mit Comover-Portfolio, monatlich)

Regel (Chen et al. laut Krauss' Beschreibung der WP-Fassung 2012; Vorzeichen-Konvention aus der Oekonomie, Original-Formel im Text verzerrt, im Paper pruefen):
1. Monatlich, am letzten Handelstag des Monats t. Universum = heutige S&P-500-Liste mit mindestens 60 Monatsrenditen (Adjusted Close, Monatsende zu Monatsende).
2. Formationsfenster: Monatsrenditen der Monate t-60..t-1 (5 Jahre, ohne Monat t).
3. Paarweise Pearson-Korrelationen der Monatsrenditen. Comover-Portfolio von Aktie i = gleichgewichtetes Portfolio der 50 hoechstkorrelierten Aktien (quasi-multivariat). Die Univariate-Variante mit nur 1 Comover ist die Kontrolle (laut Krauss rund ein Drittel weniger Rendite).
4. beta_i = OLS-Steigung der Monatsrendite von i auf die Comover-Portfoliorendite im Formationsfenster.
5. Divergenz im Monat t: D_i = beta_i * (R_C,t - Rf_t) - (R_i,t - Rf_t). Hoher D = Aktie i hat gegenueber ihren Comovern zurueckgelegen. Rf = monatlicher RF aus Ken French (F-F_Research_Data_Factors).
6. Sortiere alle Aktien nach D in 10 Dezile. Long: Dezil mit groesstem D. Short: Dezil mit kleinstem D. Gleichgewichtet, dollarneutral.
7. Ausfuehrung: Open des ersten Handelstags von Monat t+1; Halteperiode ein Monat; am Open des ersten Handelstags von Monat t+2 komplett neu.
8. Kosten: Basis 5 bp, streng 20 bp pro Halbumschlag und Aktie, Leihgebuehr 0,6 % p.a. (Umschlag ca. 100 % pro Monat, deshalb Kosten kritisch).

Evidenz: Laut Krauss (WP 2012) auf demselben Datensatz wie GGR (CRSP, 1962-2002): durchschnittliche monatliche Rohrendite 1,70 % (gleichgewichtet), fast doppelt so hoch wie GGR; Fussnote bei Krauss: 1,40 % fuer das Comover-Long-Short (Table 1 Panel A), 0,95 % fuer klassische Aktienpaare (Table 5 Panel B). Chen et al. 2019 (Abstract, Suchergebnis): grosse, signifikante Abnormal Returns, aber das Signal besteht aus kurzfristigem Reversal und Pairs-Momentum, und die Gewinne werden grossenteils durch Short-Term-Reversal und eine Ein-Monats-Version von Industrie-Momentum erklaert. Quantpedia-Seite: die Rendite ist ueber die Zeit gesunken und war in der Liquiditaetskrise schwach.
Das ist also im Kern ein Short-Term-Reversal-/Industrie-Momentum-Faktor in Pairs-Verkleidung, mit sehr hohem Umschlag. Kosten und Survivorship-Bias sind die zwei Hauptfeinde. Clegg/Krauss: PCI-Renditen laden ebenfalls signifikant auf dem Short-Term-Reversal-Faktor.

Risiken: Reversal-Crash in Stressphasen, Umschlag, Kosten, Short-Seite bei Retail-Brokern.

### Strategie 5: etf_sector_coint_pairs (Eigenentwurf: Kointegrations-Paare nur unter Sektor-ETFs, datenehrlicher Test)

STATUS: Eigenentwurf, keine direkte Evidenz. Ich habe kein Paper gefunden/gelesen, das Pairs Trading mit genau dieser ETF-Menge testet. Gedacht als survivorship-freier Gratis-Test der Familie. Regel-Vorlage ist Strategie 2.

Regel:
1. Universum: XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY (9 ETFs, 36 Paare). Kein XLRE/XLC (zu kurze Historie).
2. Alle 126 Handelstage: Formation 252 Tage log-Preise (Adjusted Close). Fuer alle 36 Paare Engle-Granger (wie Strategie 2). Akzeptiere Paare mit p < 0,05 und Halbwertszeit 2-60 Tage, hoechstens 5 Paare, sortiert nach kleinstem p (Sensitivitaet: Bonferroni p < 0,05/36 = 0,0014).
3. Hedge, z-Score, Eroeffnen/Schliessen exakt wie Strategie 2 (z = +/-2, Exit z = 0, Ausfuehrung Open t+1, Fensterende zwangsschliessen).
4. Kapital: Eigenkapital/5 pro Slot; unbenutzte Slots bleiben Cash. KEIN Pair im Fenster = NO TRADE (passt zur Quant-Lab-Regel 1).
5. Kosten: Eigene Annahme 3 bp pro Halbumschlag pro Bein, Leihgebuehr 0,3-0,6 % p.a. (nicht aus einem Paper), Sensitivitaet bis 10 bp.

Indirekte Evidenz (alles nur laut Krauss' Review): GGR-Regel auf Rohstoff-Futures 1990-2008 signifikante Excess Returns (Bianchi et al. 2009); REIT-Paare besser als Aktien, aber der Effekt verschwindet nach 2000 (Mori/Ziobrowski 2011); GGR in Finnland (Broussard/Vaihekoski 2012) und UK (Bowen/Hutchinson 2014) bestaetigt, UK teils durch Liquiditaetsbereitstellung erklaerbar. Das sind keine ETF-Belege.

Warum trotzdem aufnehmen: Die Sektor-ETFs sind hochkorreliert (Beta-Strukturen stabil), aber echte Kointegration zwischen Sektoren ist unwahrscheinlich (unterschiedliche Fundamentaldaten). Erwartung: sehr wenige Paare pro Fenster, viele Fenster ohne Handel, Ergebnis nahe null. Genau diese Erwartung ist die Hypothese, die man sauber mit Gratisdaten pruefen kann.

## 4. Nicht als Strategie gefuehrt (mit Grund)

- Partial Cointegration (PCI, Clegg & Krauss): Volltext gelesen, aber die Schaetzung (Zustandsraum, ML per Kalman-Filter) ist nicht ohne Rueckfrage kodierbar, und die Autoren selbst zeigen: 12,3 % p.a. netto und Sharpe 1,1 ueber 1990-10/2015 (S&P 500 ohne Survivorship-Bias, 4-Jahres-Formation, Z-Schwellen 1,0 / -0,5, 10 % Stop-Loss, 5 bp pro Halbumschlag), aber 01/2010-10/2015 netto ca. -2,8 % p.a. (Sharpe ca. -0,57) bei Markt +13,1 %. Sub-Perioden: 1990-03/2001 netto ca. 22 %, Sharpe 2,4; 04/2001-08/2008 5,2 %; GFC 49 %; danach negativ. Autoren: "increasing deployment of such strategies renders the markets more efficient". Ein Eintrag "funktioniert nach Kosten nicht mehr".
- Han/He/Toh 2023 (EJOR): Agglomeratives Clustering mit Firmencharakteristika, US 1980-2020, annualisierter Mittelwert 24,8 %, Sharpe 2,69, "profitabel nach Kosten und ohne Aktien unter dem 20-%-NYSE-Groessenquantil" (Abstract). Kostenannahmen stehen nicht auf der Seite, Regeln nicht verifiziert, Charakteristika (CRSP/Compustat) nicht gratis. Zahl wirkt wie ein Ausreisser relativ zu allem anderen, was ich gelesen habe. Vor jedem Einsatz Volltext lesen und mit Return-only-Clustering replizieren (Eigenentwurf).
- Hochfrequenz-Pairs: Bowen et al. (FTSE 100, 2007, 60-Minuten-Bars): ca. 20 % p.a. Excess, aber 15 bp Kosten plus 60 Minuten Ausfuehrungsverzoegerung eliminieren alles (laut Krauss). Nicht mit Gratis-Tagesdaten testbar.
- VIX-Timing der Pairs-Strategie: Huck (2015, laut Krauss) fand auf S&P 500 und Nikkei 225 keine Verbesserung. Die Idee "nur in Krisen handeln" ist durch Fil/Clegg-Krauss motiviert, aber ohne Vorab-Erkennbarkeit nicht belegt. Wenn man sie testen will: Eintrag in HYPOTHESEN.md mit festem Schwellenwert (z.B. ^VIX-Schluss ueber 25 am Signaltag) VOR dem Test, und damit gegen Huck's Befund.
- Intraday/Hochfrequenz mit Gratisdaten: nicht moeglich (yfinance 1-Minuten-Daten nur wenige Tage).

## 5. Ehrliche Bewertung: Nachpublikations-Verfall, Kosten, Tails

Verfall (Zahlen siehe oben):
| Zeitraum | Quelle | Befund |
|---|---|---|
| 1962-2002 | GGR via Quantpedia/Krauss | ca. 11 % p.a. Excess (Top-20), vor Kosten |
| 1962-2014 | Rad/Low/Faff (Abstract) | Distanz 91 bp -> 38 bp netto pro Monat, Kointegration 85 -> 33 bp, Copula 43 -> 5 bp; ab 2009 deutlich weniger Gelegenheiten |
| 1989-2002 vs 2003-2009 | Do/Faff laut Clegg/Krauss | 0,56 % vs 0,33 % pro Monat (brutto) |
| 1990-2015 S&P 500 | Clegg/Krauss | GGR 0,15 %/Monat brutto, netto Sharpe -0,55; 2010-2015 netto ca. -0,2 % p.a. |
| 1990-2020 NYSE | Fil | < 0,2 %/Monat vs Markt 0,47 %; Bullenmarkt ca. 1 % hinter dem Markt |
| Avellaneda-Lee | PCA Sharpe 1,44 (1997-2007) -> 0,9 (2003-2007) | Verfall nach 2002 im Original selbst |

Kostenempfindlichkeit: Bowen et al. (Hochfrequenz) und Fil (optimale Schwellen steigen mit den Kosten) zeigen, dass die Edge mit den Kosten verschwindet. Ein 6-Monats-Pairs-Portfolio hat weniger Umschlag als Avellaneda-Lee (Tagesumschlag), aber der Gewinn pro Trade ist klein. Regel: Jede Zahl mit den Kostenstufen "Basis" und "streng" berichten.

Tail-Risiken: Nicht-konvergierende Paare (32 % der Distanz-Paare laut Do/Faff via Krauss), Kointegrationsbruch bei Unternehmensereignissen, Quant-Quake August 2007 (A-L), Reversal-Crashs, Short-Squeezes und Leihverbote, Delisting (der GGR-Test mit -100 % fuer delistete Long-Aktien blieb laut Quantpedia positiv). Die Liquiditaetsbereitstellungs-Natur (Andrade et al. 2005 Taiwan, Bowen/Hutchinson UK, laut Krauss) bedeutet: Gewinne kommen in Krisen, aber Praxis-Handelbarkeit in genau diesen Phasen (Leihverbote, Spreadsprung) ist fraglich. Clegg/Krauss: "an execution during that time would have been likely".

## 6. Hinweis zu den Clegg/Krauss-Tabellen (Zuordnung)

Der PDF-Text verteilt die Zeilenbeschriftungen der Tabellen 11 und 13 unsauber. Ich habe die Zeilenreihenfolge (Mean return, Mean excess return, Standard deviation, Sharpe ratio, Maximum drawdown, Calmar ratio) gegen Fliesstextaussagen geprueft: PCI GFC "49 percent, DD 3 percent, Sharpe 2.6" und 1990-03/2001 "22 percent, Sharpe well above 2" stimmen mit meiner Zuordnung exakt ueberein, ebenso 12,3 % / Sharpe 1,1 (Gesamtzeitraum) und 5,2 % (04/2001-08/2008). Die Werte fuer GGR/CI1/CI2/MKT in den Teilperioden folgen derselben Zeilenordnung, sind aber weniger stark gegengeprueft. Vor dem Zitieren in einem Bericht bitte im PDF Table 13 direkt oeffnen.

Gesamtzeitraum 1990-10/2015, nach Kosten (Table 11, annualisiert, fully invested): Mean GGR ca. 1,1 %, CI1 ca. 1,6 %, CI2 ca. 1,1 %, PCI 12,3 %, MKT 9,6 %. Sharpe GGR -0,55, CI1 -0,24, CI2 -0,37, PCI 1,11, MKT 0,43 (Sharpe auf Basis der dort verwendeten Excess-Renditen).
Teilperiode 01/2010-10/2015, nach Kosten (Table 13, annualisiert, mean return): GGR -0,18 %, CI1 -1,67 %, CI2 -0,56 %, PCI -2,76 %, MKT +13,08 %. Sharpe GGR -0,10, CI1 -0,34, CI2 -0,20, PCI -0,57, MKT 0,94.

## 7. Offene Punkte / naechste Schritte

1. Survivorship-freie Gratis-Quelle fuer S&P-500-Historie? Nicht gefunden. Pragmatisch: heutige Liste verwenden, Ergebnisse als obere Schranke deklarieren, zusaetzlich die ETF-Strategie 5 als bias-freie Gegenprobe rechnen.
2. Do/Faff 2012 (J. Financial Research) und Gatev et al. 2006 im Original lesen, um die Zero-Crossing-Auswahl und die GGR-Normalisierung im Handelsfenster (Re-Normierung vs. Formations-Normierung) zu klaeren. Krauss beschreibt Re-Normierung auf den ersten Handelstag, Clegg/Krauss verwenden rohe Preise mit Formations-Sigma. Beide Varianten im Code als Schalter vorsehen.
3. Chen et al. 2019: Online-Appendix (INFORMS) fuer die exakte Divergenz-Definition (Vorzeichen, Comover-Auswahl) pruefen.
4. Rad/Low/Faff und Huck/Afawubo im Volltext lesen (Stichprobenperioden, Kostenmodell). Huck/Afawubo nennt auf der IDEAS-Seite keinen Zeitraum.
5. Folgerecherche Post-2015: die oben genannten ungelesenen Spuren (Sun 2025 Survey, Pandini 2026, Krypto-Pairs-Arbeiten).
6. Ken French Data Library fuer Gratis-Zusatz: Industry-Portfolios (48 Industrien, taegliche Renditen ab 1926-07-01) und F-F_Research_Data_Factors (RF, Mkt-RF, SMB, HML; taeglich/monatlich ab 1926-07) sind survivorship-frei, aber nicht handelbar (keine Kosten). Dateinamen aus Gedaechtnis, vor Nutzung auf mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html bestaetigen. Nutzen: Gegenprobe der Mean-Reversion-Hypothese zwischen Industrien ohne Survivorship-Bias.

## 8. Quellen-URLs (alle tatsaechlich aufgerufen oder in Suchergebnissen gesehen)

- Krauss Review (WP): https://www.iwf.rw.fau.de/files/2016/03/09-2015.pdf (abgerufen)
- Quantpedia GGR-Seite: https://quantpedia.com/strategies/pairs-trading-with-stocks (abgerufen)
- Avellaneda-Lee: https://math.nyu.edu/~avellane/AvellanedaLeeStatArb071108.pdf (abgerufen)
- Fil 2020: https://arxiv.org/abs/2010.01157 und https://arxiv.org/pdf/2010.01157 (abgerufen)
- Clegg-Krauss: https://www.iwf.rw.fau.de/files/2016/05/05-2016.pdf (abgerufen)
- Huck-Afawubo: https://ideas.repec.org/a/taf/applec/v47y2015i6p599-613.html (abgerufen)
- Han-He-Toh: https://ideas.repec.org/a/eee/ejores/v307y2023i2p929-947.html (abgerufen)
- Do-Faff 2010 (Suchtreffer): https://research.bond.edu.au/en/publications/does-simple-pairs-trading-still-work/ , https://rpc.cfainstitute.org/research/financial-analysts-journal/2010/does-simple-pairs-trading-still-work
- Rad-Low-Faff (Suchtreffer): https://research.bond.edu.au/en/publications/the-profitability-of-pairs-trading-strategies-distance-cointegrat/
- Chen et al. 2019 (Suchtreffer): https://ideas.repec.org/a/inm/ormnsc/v65y2019i1p370-389.html , DOI https://doi.org/10.1287/mnsc.2017.2825
- Weitere Suchtreffer ohne Lektuere: https://cxoadvisory.com/technical-trading/best-stock-pairs-trading-method , https://mma.prnewswire.com/media/2965868/2026_00G__StationaryButNotProfitable_ACriticalLookatPairsTrading_DavidePandini.pdf?p=pdf , https://harbourfrontquant.substack.com/p/improving-pairs-trading-profitability
