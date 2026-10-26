# Familie Krypto und Alternative Assets (Momentum/Trend/Carry in Krypto, Rohstoffen, Gold) - Literaturrecherche und Strategie-Kandidaten

Stand: 2026-10-12. Quant-Research-Analyst-Lauf (Workflow "research:crypto"). Sprache: Deutsch (ASCII-Schreibweise wie die Geschwister-Notizen).
Alle Literaturzahlen stammen aus Seiten/PDFs, die in dieser Session wirklich abgerufen wurden (jeweils mit Abrufart markiert),
oder aus eigenen Rechnungen (klar als "EIGENER CHECK" markiert). Was nicht gefunden wurde, steht als "nicht gefunden".
Skripte der eigenen Checks: `research/families/crypto_checks/` (laden Daten selbst per yfinance bzw. Binance-Public-API).

## 0. Kurzfazit (ehrlich)

1. Krypto-TREND (Zeitreihen-Momentum, Long/Flat auf BTC/ETH) ist der einzige Kandidat mit (a) akademischer Unterstuetzung, (b) Gratis-Daten,
   (c) einem Ergebnis, das in meinem eigenen Check nach 20 bp Kosten und Ausfuehrung zum naechsten Open besteht - ABER der Vorteil liegt
   fast nur im DRAWDOWN (BTC MaxDD -83 % -> ca. -54 %), nicht in der Rendite (BTC-Buy&Hold CAGR 69.9 % vs. Trend 62-79 %). In 2023-2026
   ist der Sharpe der Trendregeln ungefaehr gleich Buy&Hold (0.9-1.3 vs 1.06). Es ist ein Zyklus (2015-2026, im Kern 3 Boom/Bust-Zyklen):
   statistisch duenn (Standardfehler eines Sharpe ueber 11 Jahre ca. 0.3-0.4).
2. Kreuzschnitt-Momentum in Krypto (Liu-Tsyvinski-Wu) ist in der Arbeit riesig (ca. 2.5-4.1 % pro WOCHE, Long-Short), aber: Stichprobe
   2014-2018 mit 109 -> 1.583 Mikro-Coins, ohne Handelskosten/Leerverkaufsrestriktionen. Han/Kang/Ryu (nur Abstract/Suchtreffer gesehen)
   sagen: unter realistischen Annahmen ist TS-Momentum robust, CS-Momentum schwach; Verlierer-Coins springen zurueck. Mein EIGENER CHECK
   auf 10 grossen Yahoo-Coins (2018-2026, mit Survivorship-Bias) findet KEINEN Vorteil gegenueber Equal-Weight/BTC; Long/Short ist Null.
3. Krypto-Carry (Basis/Funding): die Prämie war real (Funding BTC-Perp 2020: 17 %, 2021: 31 % p.a.), ist aber zerfallen:
   2025 ca. 5.1 %, 2026 bisher ca. 2.9 % p.a. (annualisiert) vs. 3-Monats-T-Bill 4.06 % (^IRX, 2026-10-09). Nach Gebuehren/Margin/Gegenparteirisiko
   aktuell kein Vorteil gegenueber Cash. Eintrag lautet: "funktioniert aktuell nach Kosten nicht".
4. Rohstoffe: die starke akademische Evidenz (Erb-Harvey, Gorton-Rouwenhorst, Miffre-Rallis, Fuertes-Miffre-Rallis) gilt fuer ein
   Long/Short-Futures-Universum (22-37 Kontrakte, 1979-2007), mit Term-Structure-Daten (Datastream/Bloomberg), die NICHT gratis sind, und mit
   sehr optimistischen Kosten (0.033 % Round-Trip). Gratis-Proxy (9 Rohstoff-ETFs, monatlich 12-1-Momentum, long top 3): Sharpe 0.18, CAGR 3.0 %,
   MaxDD -52 % - kein brauchbarer Edge. Was bleibt: Trendfilter auf DBC+GLD (Sharpe 0.47 vs 0.38 Buy&Hold, MaxDD -28 % vs -51 %), aber der Vorteil
   stammt aus 2006-2015 (Rohstoff-Baerenmarkt, 2008); 2016-2026 schlaegt Buy&Hold (Sharpe 0.76 vs 0.62).
5. Gold-Trend: im Gratis-Test (GLD 2005-2026, GC=F 2000-2026) KEIN Edge. SMA210/TSMOM252 liefern weniger Rendite UND niedrigeren Sharpe als Buy&Hold
   (0.43-0.48 vs 0.55), nur etwas flacheren Drawdown (-36 % vs -45 %). Gold war 2005-2026 ein Dauer-Bullenmarkt.
6. Nichts hier ersetzt den Stand der anderen Familien (SPY/60-40 Benchmark). Rohstoff/Gold: Sharpe 0.4-0.5 vs SPY ca. 0.57 (siehe tsmom.md).
   Krypto: hoechstens als kleine, risikobegrenzte Beimischung (Positionsgroesse!) interessant, nicht als Kernstrategie.

## 1. Methodik, Quellenlage, was NICHT gesehen wurde

Genau 17 Web-Abrufe (WebSearch + WebFetch, inkl. 4 Fehlschlaege/Binaerdateien); danach nur lokale Rechnungen. Abrufart je Quelle:

| Quelle | Abruf | Gelesen |
|---|---|---|
| Liu/Tsyvinski/Wu, Common Risk Factors in Cryptocurrency (WP-Version 15.04.2019) | Cowles-PDF, lokal per pdftotext | Einleitung, Abschnitt 3.1/3.2 (Momentum), Faktorbau, Hedging; Tabellen 4 und 8 nur teilweise |
| Fuertes/Miffre/Rallis, JBF 2010 (Accepted Manuscript) | City-Repository-PDF, lokal per pdftotext | Abstract, Daten, Momentum- und TS-Definition, Double-Sort, Kostenabschnitt; Tabellen nur teilweise |
| Begusic/Kostanjcar, Momentum and liquidity in cryptocurrencies | arXiv 1904.00890 PDF, lokal | komplett (kurz) |
| Zarattini/Pagani/Barbon, Catching Crypto Trends | abarbon.com Seite (nur Abstract) | nur Abstract; Regeln/Lookbacks/Perioden/Kosten im PDF NICHT gesehen |
| Schmeling/Schrimpf/Todorov, Crypto carry (BIS WP 1087) | bis.org Zusammenfassung | nur Abstract |
| Gorton/Rouwenhorst NBER w10595, Bhardwaj/Gorton/Rouwenhorst NBER w21243 | nber.org Abstractseiten | nur Abstract |
| Quantpedia "Term structure effect in commodities" | Seite abgerufen | Zusammenfassung; Herkunft der Kennzahlen unklar |
| Han/Kang/Ryu (TS- und CS-Momentum in Krypto, realistische Annahmen) | NUR WebSearch-Zusammenfassung (PDF auf acfr.aut.ac.nz gab 403) | Abstract-Niveau, keine Parameter |
| Miffre/Rallis JBF 2007 | NUR WebSearch-Zusammenfassung (Arbeitspapier 2006) | "13 profitable Momentum-Strategien, 9.38 % p.a." - Suchtreffer-Zahl, ungeprueft |
| Fieberg et al. CTREND (JFQA 2025), Fieberg et al. Crypto Factor Momentum (QF 2023) | NUR Suchtreffer-Snippets (JFQA-PDF 404) | NICHT als Paper gefuehrt, keine Zahlen verwendet |
| arXiv 2602.11708 "AdaptiveTrend" (Sharpe 2.41 OOS 2022-2024) | NUR Suchtreffer | NICHT verwendet (36 Monate, Eigenwerbung, nicht repliziert) |

NICHT abgerufen, deshalb nicht als Paper gefuehrt: Liu/Tsyvinski RFS 2021 "Risks and Returns of Cryptocurrency" (NBER w24877), Erb/Harvey 2006 (SSRN, nur ueber die Beschreibung in
Fuertes et al. bekannt), Gold-spezifische Arbeiten, Alpha Architect/AQR/Hoffstein-Seiten (kein Budget). Fuer Gold liegt KEIN Paper vor, nur der eigene Check.
Die SSRN-Abstractseite von LTW und die Journal-of-Finance-Version (JF 77, 2022, laut Suchtreffer 10 statt 9 Strategien) wurden nicht gelesen; die Zahlen unten sind die der WP-Version vom April 2019.

Verwendete Gratis-Daten, geprueft per yfinance am 2026-10-12 (erster Kurs):
BTC-USD 2014-09-17, ETH-USD 2017-11-09, XRP/DOGE/BCH/ADA/XLM/BNB/LINK-USD 2017-11-09, LTC-USD 2014-09-17, GC=F 2000-08-30, GLD 2004-11-18, IAU 2005-01-28,
SLV 2006-04-28, DBC 2006-02-06, GSG 2006-07-21, USO 2006-04-10, UNG 2007-04-18, DBA/DBB 2007-01-05, PPLT/PALL 2010-01-08, CPER 2011-11-15, COMT 2014-10-16,
PDBC 2014-11-07, GBTC 2015-05-11, BITO 2021-10-20, IBIT/FBTC 2024-01-11, BTC=F (CME) 2017-12-18, ETH=F 2021-02-05, ^IRX 1999-01-04 (Cash-Satz, % p.a.).
Boersen-ETPs fuer deutsche Anleger (Yahoo vorhanden, nur Ticker/Start geprueft, nichts getestet): BTCE.DE 2020-06-08, VBTC.DE 2020-11-19, VETH.DE 2021-03-26, ABTC.SW 2019-02-26, AETH.SW 2019-03-05.
Binance Public API (kostenlos, ohne Key, per curl/requests): `https://fapi.binance.com/fapi/v1/fundingRate` - BTCUSDT-Perp ab 2019-09-10, ETHUSDT ab 2019-11-27 (aus Deutschland erreichbar).
Yahoo-Warnung: `GC=F`, `BTC=F` sind unbereinigte Front-Month-Ketten (Roll-Luecken); fuer Signale ETF-Proxys (GLD, DBC) oder Spot (BTC-USD) nutzen.
Yahoo-Kryptoserien: 24/7, Tagesschluss = 00:00 UTC; "Open" = naechster UTC-Mitternacht-Preis -> Ausfuehrung "zum Open des Folgetags" ist praktisch der Preis um 00:00 UTC.

### Eigene Test-Methodik (alle EIGENER CHECK unten)
- Signal am Close t (Close eingeschlossen), Handel zum Open t+1, gehalten bis Open t+2 (Open-zu-Open-Renditen). Kein Look-ahead.
- Kosten pro Einheit Umschlag (one-way): BTC/ETH/Krypto 20 bp, Gold-ETF 5 bp, Rohstoff-ETFs 10 bp. Cash-Anteil verzinst mit ^IRX.
- Regeln wurden VOR dem Test aus der Literatur bzw. als runde Standardwerte gesetzt, nicht optimiert. Mehrfachtest-Hinweis: im BTC-Test 6 Regeln, Gold 3 pro Instrument,
  DBC+GLD 4 Fensterlaengen, Krypto-CS 5 Lookbacks + 2 L/S - nichts davon ist deflated-Sharpe-korrigiert. Es sind Plausibilitaetschecks, keine Validierung.
- Subperioden werden gezeigt, damit Nachpublikations-Verfall sichtbar wird (Krypto-Veroeffentlichungen 2019-2021, Rohstoff-Papiere 2006-2010).
- Nicht modelliert: Steuern, Spread-Schwankungen, Boersenausfaelle, Marktimpact. Deutsche Steuer (aus dem Gedaechtnis, NICHT geprueft): Krypto-Verkauf nach mehr als einem Jahr Haltedauer ist fuer
  Privatanleger steuerfrei (§23 EStG), Trendregeln mit Umschlag zerstoeren diese Haltefrist -> Gewinne unterliegen dem persoenlichen Steuersatz (Freigrenze beachten). Das kann den Trend-Vorteil gegenueber Buy&Hold voellig auffressen. Vor einer Umsetzung ist das ZUERST zu klaeren.

## 2. Literatur im Detail

### 2.1 Liu/Tsyvinski/Wu: Common Risk Factors in Cryptocurrency (WP 15.04.2019; spaeter Journal of Finance 77(2), 2022)
URL (gelesen): https://cowles.yale.edu/sites/default/files/2022-10/LiuTsyvinskiWu2019%20COMMON%20RISK%20FACTORS.pdf ; NBER: https://www.nber.org/papers/w25882 (nicht lesbar, 504); SSRN: https://papers.ssrn.com/abstract=3379131 (nur im Suchtreffer).
- Stichprobe: alle Coins mit Marktkap. > 1 Mio. USD, Anfang 2014 bis Ende 2018; 109 Coins 2014 -> 1.583 Coins 2018. Marktindex: 1.707 Coins, marktkap.-gewichtet.
- Methode: woechentlich Sortierung in Quintile nach Faktor, naechste Woche wertgewichtete Quintil-Renditen, Long Q5 / Short Q1.
- Ergebnis Momentum (Long-Short-Quintil, Wochenrendite): 1-Wochen 2.7 %, 2-Wochen 3.3 %, 3-Wochen 4.1 % (1-%-Niveau), 4-Wochen 2.5 % (5-%-Niveau). 8-, 16-, 50-, 100-Wochen-Momentum: NICHT signifikant.
  Size (klein minus gross): 3.4 % (Marktkap.), 3.9 % (Preis), 4.1 % (Max-Preis) pro Woche.
- Die Autoren schreiben selbst: die Strategie beruecksichtigt weder Handelskosten noch die Machbarkeit von Leerverkaeufen; sie testen "Long kleinste Coins / Short Bitcoin" als Ersatz.
- CMOM (Faktor): 3-Wochen-Momentum, Top 30 % minus Bottom 30 %, wertgewichtet; CSMB analog fuer Size (Bottom 30 % minus Top 30 %). Drei-Faktor-Modell CMKT+CSMB+CMOM erklaert alle 9 Strategien. Momentum-Strategien laden nicht signifikant auf CMKT.
- Hedging unbezahlter Risiken: fuer Size grosser Sharpe-Gewinn, fuer Momentum keiner (Ladungen sind "transienter").
- Ehrliche Einordnung: 3-4 % pro Woche (>150 % p.a.) in einer Mikro-Coin-Stichprobe, die das 2017er-Blasenjahr enthaelt, sind ohne Spreads/Leerverkauf nicht handelbar. Die Existenz von Momentum in grossen liquiden Coins ist eine andere, schwaechere Aussage (siehe 2.3).

### 2.2 Han/Kang/Ryu: Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market: A Comprehensive Analysis under Realistic Assumptions
URL (Treffer in WebSearch, PDF 403): https://acfr.aut.ac.nz/__data/assets/pdf_file/0009/918729/Time_Series_and_Cross_Sectional_Momentum_in_the_Cryptocurrency_Market_with_IA.pdf
Nur die Suchtreffer-Zusammenfassung gesehen (Autoren Chulwoo Han, Byeongguk Kang, Jehyeon Ryu; Jahr in der Zusammenfassung nicht genannt):
- Fruehere Studien ignorierten Reibungen; mit Handelskosten, taeglichen Preisschwankungen und Liquidationsrisiko werden viele Momentum-Portfolios unprofitabel, einige "signifikante" verdienen nichts.
- TS-Momentum robust, CS-Momentum schwach; Effekt konzentriert in den groessten frueheren Gewinnern; Verlierer erholen sich haeufig stark und verursachen grosse Verluste.
- Kostenparameter, Regeln, Kennzahlen: NICHT gefunden. Das ist die wichtigste Gegenstimme zu 2.1 und deckt sich mit meinem eigenen Check (Abschnitt 4.5).

### 2.3 Begusic/Kostanjcar: Momentum and liquidity in cryptocurrencies (arXiv 1904.00890, April 2019)
URL: https://arxiv.org/pdf/1904.00890 (komplett gelesen)
- Daten: coinmarketcap, Jan 2015 - Jan 2019, 711 Coins, Stablecoins entfernt; Kriterien: >= 26 Wochen Historie, Marktkap. nie unter 1 Mio. USD. Momentum = 14-Tage-Rendite, 3 Gruppen (30/40/30), Amihud-Illiquiditaet 14 Tage, gleichgewichtet, 14-Tage-Rebalancing.
- Momentum (Gewinner minus Verlierer) nur bei den LIQUIDESTEN Coins signifikant (UMD 0.26 % Tagesrendite, *); bei illiquiden Coins Mean Reversion (illiquide Verlierer 1.07 %/Tag vs. illiquide Gewinner 0.53 %).
- Long-only "liquid winners": Tagesrendite 0.71 %, IR 1.59 bei 0 bp; 1.43 bei 50 bp; 1.27 bei 100 bp pro Rebalancing.
- Warnung der Autoren (bestaetigt meine Skepsis): "illiquid losers" (1.07 %/Tag, IR 2.49) leiden praktisch an hohen Spreads; 1.07 % pro TAG entspricht einer absurden Annualisierung - das ist Blasen-/Mikro-Coin-Artefakt, kein Edge.
  Die Stichprobe endet im Januar 2019: das 2018er-Crash-Jahr ist nur am Rand drin, keine Out-of-sample-Pruefung.

### 2.4 Zarattini/Pagani/Barbon: Catching Crypto Trends - A Tactical Approach for Bitcoin and Altcoins (SFI Research Paper / SSRN, 2025)
URL (nur Abstract gelesen): https://abarbon.com/papers/catching-crypto-trends ; auch https://ideas.repec.org/p/chf/rpseri/rp2580.html ; https://concretumgroup.com/catching-crypto-trends-a-tactical-approach-for-bitcoin-and-altcoins/
- Ensemble von Donchian-Channel-Trendmodellen mit verschiedenen Lookbacks, volatilitaetsbasierte Positionsgroesse, rotierendes Portfolio der 20 liquidesten Coins (survivorship-bias-freier Datensatz aller Coins seit 2015).
- Laut Abstract: Sharpe > 1.5 nach Gebuehren, annualisierte Alpha 10.8 % gegen Bitcoin. Laut Suchtreffer (CXO-Zusammenfassung): Universum = Coins >= 1 Jahr gelistet, Median-Tagesvolumen >= 2 Mio. USD (30 Tage); BTC-Test Long-only.
- Lookbacks, Volatilitaetsziel, Perioden, Max-Drawdown, Kosten: NICHT gefunden (nur Abstract). Backtest eines Arbeitspapiers, keine Replikation gesehen. Ich fuehre die Zahl daher nur als "behauptet".

### 2.5 Schmeling/Schrimpf/Todorov: Crypto carry (BIS Working Paper 1087, April 2023)
URL: https://www.bis.org/publ/work1087.htm (nur Zusammenfassung)
- Carry = Futures-Spot-Basis; kann bis ca. 60 % p.a. erreichen, im Mittel > 10 % p.a. (hoeher als in Aktien, Anleihen, FX, Rohstoffen laut Abstract). Treiber: volatiler Convenience Yield, gehebelte Trendjagd kleiner Anleger, knappes Arbitragekapital. Hoher Carry sagt kuenftige Crashs voraus.
- Cash-and-Carry (long Spot, short Future) ist riskant wegen Margin-Spitzen und Liquidationen in Drawdowns. Sharpe, Stichprobe, Kosten: NICHT gefunden.

### 2.6 Rohstoffe: Gorton/Rouwenhorst (2006), Bhardwaj/Gorton/Rouwenhorst, Erb/Harvey, Miffre/Rallis, Fuertes/Miffre/Rallis
- Gorton/Rouwenhorst, "Facts and Fantasies about Commodity Futures", NBER w10595 (Juni 2004, rev. Maerz 2006): https://www.nber.org/papers/w10595 - gleichgewichtiger Rohstoff-Futures-Index, Juli 1959-Maerz 2004: gleiche Rendite/Sharpe wie Aktien, negativ korreliert mit Aktien und Anleihen, positiv mit Inflation. Zahlen: nicht gefunden (nur Abstract).
- Bhardwaj/Gorton/Rouwenhorst (NBER w21243, zehn Jahre danach): https://www.nber.org/papers/w21243 - laut Abstract bestaetigen Out-of-sample-Daten die Kernbefunde im Wesentlichen; Rohstoff-Korrelationen stiegen in der Finanzkrise zeitweise. Keine Zahlen im Abstract; zu Momentum/Carry nichts abgerufen.
- Erb/Harvey (2006), nur ueber die Beschreibung in Fuertes et al.: kaufe die 6 am staerksten backwardierten, verkaufe die 6 am staerksten contangierten von 12 Rohstoffen (monatlich).
- Miffre/Rallis JBF 2007 (nur Suchtreffer, Arbeitspapier 2006): 13 profitable Momentum-Strategien (von 56 getesteten), Durchschnitt 9.38 % p.a. vs. -2.64 % Long-only-EW, Jan 1979-Sep 2004; beste (12-1) 14.6 % bei 25.6 % Vol. Zahlen aus Suchtreffer, ungeprueft.
- Fuertes/Miffre/Rallis, JBF 34(10), 2530-2548 (2010): http://openaccess.city.ac.uk/id/eprint/6416 (PDF gelesen). Daten Datastream/Bloomberg, 1.1.1979-31.1.2007, 37 Rohstoffe (22 -> 35 Kontrakte), nearby/second/distant Preise, Roll am Monatsende oder am 15. des Verfallsmonats.
  Momentum: Quintile nach R-Monats-Rendite, Halten H Monate, 13 Kombinationen aus Miffre/Rallis; TS1: Long Top-20 % / Short Bottom-20 % nach Roll-Rendite R = (ln P_nahe - ln P_naechste) * 365 / (Tage_fern - Tage_nah), gleichgewichtet, 1 Monat halten.
  Double-Sort: Terzile nach Roll-Rendite; im High-Terzil Split nach Vor-R-Monats-Rendite (Winner/Loser), im Low-Terzil ebenso; Long High-Winner, Short Low-Loser, 1 Monat. Annualisierte Alphas: Momentum 10.14 %, TS 12.66 %, Double-Sort 21.02 %; netto 20.41 % (0.033 % Round-Trip nach Locke/Venkatesh 1997, Umschlag ca. 9-10.7 pro Jahr). Mittlere Korrelation Momentum/TS: 31.26 %.
  Die Autoren behaupten Robustheit gegen Liquiditaet, Data Mining und Kosten; robust auch gegen hohe Vol seit 2007. Gleichzeitig: Leerverkauf von Futures wird als "so einfach wie Long" behandelt, Preisimpact/Kommissionen ignoriert, Stichprobenende Jan 2007 (vor Finanzialisierung, 2008, 2014-2016-Oelcrash).
- Quantpedia Term-Structure-Seite (https://quantpedia.com/strategies/term-structure-effect-in-commodities): Long Top-20 % / Short Bottom-20 % nach Roll-Rendite, monatlich; angegeben 11.73 % p.a., Vol 23.84 %, MaxDD -78.06 %, Sharpe 0.49, Stichprobe 1979-2004 - die Seite sagt selbst nicht klar, ob das fuer die einfache Regel gilt. MaxDD -78 % ist der eigentlich wichtige Wert.

## 3. Strategien (nach erwarteter Robustheit sortiert)

Reihenfolge nach erwarteter Robustheit der UMSETZBAREN Variante mit Gratis-Daten: 1 > 2 > 3 > 4 > 5. (3) hat die staerkste akademische Evidenz, ist aber mit Gratis-Daten nicht testbar - deshalb Platz 3.

### 3.1 crypto_trend_ens_btc_eth - BTC/ETH Trend-Ensemble, Long/Flat
Regel (genau wie in 4.1/4.2 getestet): taeglich nach dem UTC-Tagesschluss t: je Coin X in {BTC-USD, ETH-USD} s_X = Mittel ueber n in {20,50,100,200} von 1[Close_X(t) > SMA_n(t)] (SMA inkl. Close t). Zielgewicht w_X = 0.5 * s_X, Rest Cash (^IRX / Tagesgeld / BIL).
Handel zum Open t+1 (= 00:00 UTC). ETH-Bein erst nach 200 Close-Werten. Kein Hebel, kein Short. Kosten im Test 20 bp pro Einheit Gewichtsaenderung.
Test-Einschraenkung (ehrlich): im Test wird auf die Zielgewichte taeglich "zurueckgesetzt", Kosten fallen aber nur bei Signalwechseln an (nicht fuer Drift-Rebalancing zwischen BTC/ETH/Cash). Praxis: Rebalancing nur bei Signalwechsel oder bei Gewichtsabweichung > 25 % relativ, dann ist der Test naeherungsweise exakt.
Erwartung: Drawdown ca. -45 bis -55 % statt -76 bis -86 %, Sharpe ca. 0.6-1.1 (BTC+ETH) mit grosser Unsicherheit. Abbruchkriterium (Vorschlag): Walk-forward-Sharpe <= Buy&Hold-Sharpe UND MaxDD nicht kleiner als 70 % des B&H-DD ueber 24 Monate frische Daten.

### 3.2 commodity_gold_trend_dbc_gld - Rohstoff- und Gold-Trendfilter
Regel (wie in 4.4 getestet): taeglich nach Close t je Instrument X in {DBC, GLD}: on_X = Close_X(t) > SMA_210(Close_X)(t). w_X = 0.5 wenn on_X, sonst 0; Rest Cash. Handel zum Open t+1. 10 bp one-way im Test. Umschlag ca. 7.5/Jahr (Summe).
UCITS-Pendants fuer Deutschland (nicht getestet): Gold z.B. SGLD.L (Yahoo ab 2009-06-26, laut tsmom.md); breiter Rohstoffindex-ETC: nicht geprueft.
Erwartung: Sharpe ca. 0.4-0.5, MaxDD ca. -25 bis -30 %, Rendite nahe Buy&Hold - also Risikominderung, kein Edge. Abbruch: 24 Monate frische Daten mit Sharpe unter 50/50-Buy&Hold UND MaxDD nicht besser.

### 3.3 commodity_ts_momentum_double_sort_futures - Fuertes/Miffre/Rallis Double-Sort (Rohstoff-Futures, Long/Short)
Regel laut Paper: monatlich am Monatsletzten. Fuer jeden der 22-37 Rohstoff-Futures R = (ln P_nahe - ln P_naechste) * 365 / (Tage_naechste - Tage_nahe) (Roll-Rendite, TS1); Terzile nach R; im High-Terzil Halbierung nach der R_m-Monats-Rendite (R_m in {1,3,12}) -> High-Winner; im Low-Terzil Halbierung -> Low-Loser. Long High-Winner, Short Low-Loser, gleichgewichtet, Halten 1 Monat, voll besichert (Long/Short je Bein Einheit-Nominal). Netto 20.41 % Alpha (1979-2007).
Gratis nicht testbar: Term-Structure (nahe/naechste/ferne Kontrakte) und Short-Futures nicht aus Yahoo. Nur der Momentum-Teil laesst sich mit ETFs annaehern - Check 4.4: Sharpe 0.18, CAGR 3.0 %, MaxDD -52 %. Nicht empfehlenswert ohne Datenzukauf.

### 3.4 crypto_funding_carry_delta_neutral - Perp-Funding-Carry
Regel (wie in 4.6 geprueft): BTC Spot long + BTCUSDT-Perp short, gleiche Nominale N. A(t) = 3*365*Mittel der letzten 90 Funding-Raten (30 Tage, 8h-Takt, nur Informationen VOR dem Stempel). Wenn A > ^IRX/100 + 0.02: Position halten (kassiere Funding je 8h), sonst flat in T-Bills. 30 bp Round-Trip. Basis- und Margin-P&L nicht modelliert.
Status: Prämie seit 2025 ca. T-Bill-Niveau; kein belegter Vorteil mehr. Tail-Risiko: Boersenausfall (Kontrahent), Auto-Deleveraging, Margin-Spitzen (laut Schmeling et al.). Fuer deutsche Privatanleger: Derivatezugang/MiCA/Steuer ungeklaert.

### 3.5 crypto_cs_momentum_ltw - Kreuzschnitt-Momentum Kryptowaehrungen
Regel laut LTW (WP 2019): woechentlich am Wochenende, alle Coins mit Marktkap. > 1 Mio. USD; r_3 = P_t/P_(t-3 Wochen) - 1; Quintile (Faktor CMOM: Top 30 % minus Bottom 30 %); Long Q5 / Short Q1 wertgewichtet; Halten 1 Woche. Nicht handelbar mit Gratis-Daten (Universum 1.707 Coins, Leerverkauf, Spreads).
Praxis-Variante (getestet in 4.5): Sonntags-Close-Signal, Montag-Open-Handel, long die 3 Coins mit der besten w-Wochen-Rendite (w in 1,3,4,8,16) aus 10 grossen Yahoo-Coins, gleichgewichtet. Ergebnis: kein Vorteil gegenueber EW/BTC.

## 4. Eigene Checks (EIGENER CHECK, Skripte in crypto_checks/)

### 4.1 BTC-USD Trendregeln (btc.py), 2015-09-01 bis 2026-10-11, 20 bp one-way, Cash zu ^IRX
| Regel | CAGR | Vol | Sharpe | MaxDD | Umschlag/Jahr (one-way) |
|---|---|---|---|---|---|
| Buy&Hold | 69.9 % | 65.6 % | 1.10 | -83.4 % | 0.1 |
| SMA50 | 78.6 % | 48.0 % | 1.40 | -59.1 % | 18.3 |
| SMA100 | 73.2 % | 50.5 % | 1.30 | -61.9 % | 12.5 |
| SMA200 | 66.6 % | 52.5 % | 1.19 | -69.9 % | 6.6 |
| Ensemble SMA(20,50,100,200), Gewicht = Anteil "ueber SMA" | 72.3 % | 45.3 % | 1.38 | -54.3 % | 18.9 |
| TSMOM 90 Tage (Rendite > 0) | 63.7 % | 53.3 % | 1.15 | -65.0 % | 12.7 |
| Donchian-Ensemble (20,50,100,200; Exit bei Tief N/2) | 62.0 % | 41.0 % | 1.33 | -53.2 % | 6.2 |
Brutto vs. netto (20 bp): Differenz im Sharpe 0.03-0.08 -> Kosten stoeren bei 6-19 Umschlag/Jahr kaum; bei Spreads von 50+ bp (kleine Coins, Retail-Gebuehren, Slippage in Crashs) schon.
Sharpe nach Subperiode (netto): 2015-2019 / 2020-2022 / 2023-2026: BH 1.42 / 0.74 / 1.06; Ensemble SMA 1.78 / 1.06 / 1.06; Donchian-Ens 1.73 / 1.01 / 1.00; SMA50 1.58 / 1.30 / 1.30; SMA200 1.58 / 0.77 / 0.97; TSMOM90 1.70 / 0.50 / 0.91.
MaxDD je Periode: BH -83.4 / -76.6 / -53.1 %; Ensemble SMA -54.3 / -52.5 / -29.3 %; Donchian-Ens -53.2 / -43.8 / -20.1 %.
Lesart: Verbesserung real aber klein bei Rendite/Sharpe, deutlich beim Drawdown; im letzten Teil (2023-2026) kein Sharpe-Vorsprung mehr. Zahlreiche Whipsaws (2020-2022). Alle Zahlen stammen aus EINEM Handelspfad mit sehr hohen Renditen (BTC 70 % p.a.) - kein Zeichen, dass das fuer die Zukunft gilt.

### 4.2 ETH-USD und BTC+ETH (misc.py), ETH ab 2018-06, 20 bp
ETH Buy&Hold: CAGR 19.3 %, Vol 81 %, Sharpe 0.60, MaxDD -86.4 % (2022-2026: CAGR -7.5 %, Sharpe 0.17, MaxDD -74.1 %).
ETH Ensemble SMA(20,50,100,200): CAGR 47.2 %, Vol 51.2 %, Sharpe 0.96, MaxDD -54.1 % (2022-2026: CAGR 15.9 %, Sharpe 0.47, MaxDD -37.4 %). SMA50: 48.2 % / 0.94 / -57.1 %.
BTC+ETH 50/50, Ensemble je Coin (Gewicht 0.5*Signal): 2018-06 bis 2026-10 CAGR 47.6 %, Vol 41.3 %, Sharpe 1.08, MaxDD -46.4 %; 2022-2026 CAGR 19.5 %, Vol 31.2 %, Sharpe 0.60, MaxDD -30.2 %.
Buy&Hold 50/50 (taeglich rebalanciert): 29.5 % / 67.9 % / 0.69 / -76.3 % (2022-2026: 4.1 % / 57.3 % / 0.29 / -68.4 %). Hier ist der Trendvorteil gegenueber B&H groesser, weil ETH 2022-2026 im Baerenmarkt/Seitwaertsphase war.

### 4.3 Gold (gold.py), 5 bp, Cash zu ^IRX
| Instrument/Regel | CAGR | Sharpe | MaxDD | Umschlag/J |
|---|---|---|---|---|
| GLD 2005-2026 Buy&Hold | 10.6 % | 0.55 | -45.3 % | 0 |
| GLD SMA210 | 8.0 % | 0.48 | -36.3 % | 6.8 |
| GLD TSMOM252 | 7.5 % | 0.43 | -39.5 % | 5.4 |
| GLD Ensemble SMA(100,150,210) | 7.1 % | 0.43 | -37.2 % | 9.2 |
| GC=F 2000-10 bis 2026 Buy&Hold | 11.1 % | 0.57 | -44.8 % | |
| GC=F SMA210 | 8.1 % | 0.47 | -39.5 % | 7.6 |
2016-2026 (GLD): BH 13.0 % / 0.70 / -28.5 %; SMA210 9.4 % / 0.54 / -25.1 %. Gold-Trend bringt in den Gratis-Daten KEINEN Vorteil, nur leicht weniger Drawdown. (GC=F-Kette hat Roll-Luecken; Ergebnis qualitativ gleich wie GLD.)

### 4.4 Rohstoff-ETFs (gold.py, combo.py, cscom.py)
- DBC (ab 2006-04): Buy&Hold CAGR 2.7 %, Sharpe 0.15, MaxDD -76.3 %; SMA210: 5.7 %, 0.35, -32.1 % (2016-2026: BH 10.4 % / 0.51; SMA210 8.1 % / 0.46). GSG: BH -1.3 % p.a., MaxDD -89.8 %; SMA210 2.9 %, Sharpe 0.16.
- DBC + GLD je 50 % mit eigenem SMA210-Filter (10 bp), 2006-06 bis 2026-10: CAGR 6.6 %, Vol 11.3 %, Sharpe 0.47, MaxDD -28.3 % vs. Buy&Hold 50/50: 6.5 %, 15.4 %, 0.38, -51.4 %. Vorteil kommt aus 2006-2015 (Trend 4.2 % / 0.32 / -28.0 % vs BH 0.3 % / 0.05 / -49.4 %); 2016-2026 verliert Trend (8.8 % / 0.62 / -16.0 % vs BH 12.4 % / 0.76 / -21.0 %). Umschlag ca. 7.5/Jahr. Fensterlaenge (Sharpe): 126 -> 0.25, 168 -> 0.43, 210 -> 0.47, 252 -> 0.48 (kein Fall ohne Wirkung; kurze Fenster schlechter).
- Cross-Sectional-Momentum auf 9 Rohstoff-ETFs (GLD, SLV, DBA, DBB, USO, UNG, CPER, PPLT, PALL), monatlich, 12-1-Momentum, 10 bp, 2008-06 bis 2026-10: Equal-Weight (monatlich) CAGR 0.1 %, Sharpe 0.02, MaxDD -64.3 %; long top 3: 3.0 %, Sharpe 0.18, MaxDD -52.1 %; top 2: 1.4 %/0.14; top 4: 1.5 %/0.11; top 3 + SMA210-Filter: 4.6 %/0.26/-46.3 %; Long-Short top3/bot3 (fuer Privatanleger kaum machbar): 5.8 %/0.29/-55.8 % (2008-2015: 7.9 %/0.45; 2016-2026: 4.3 %/0.22). USO/UNG verlieren massiv durch Contango.
  -> Gratis-ETF-Proxy fuer FMR/Miffre-Rallis ist NICHT brauchbar: kein Roll-Return-Signal, Contango-Dauerverlust der Einzel-ETFs, kleines Universum.

### 4.5 Krypto-Kreuzschnitt-Momentum auf 10 Yahoo-Coins (cscrypto.py), 2018-02 bis 2026-10, woechentlich, 20 bp
Universum: BTC, ETH, XRP, LTC, DOGE, BCH, ADA, XLM, BNB, LINK (alle heute gross = Survivorship-Bias). Signal: Rendite der letzten w Wochen am Sonntags-Close (UTC), Handel Montag-Open, long Top 3 gleichgewichtet, Rest Cash.
| Strategie | CAGR | Sharpe | MaxDD | Sharpe 2018-21 / 2022-26 |
|---|---|---|---|---|
| Equal-Weight 10, woechentlich | 31.9 % | 0.71 | -80.7 % | 1.07 / 0.30 |
| BTC Buy&Hold | 27.3 % | 0.66 | -76.6 % | 0.88 / 0.42 |
| long Top 3, 1-Wochen | 19.3 % | 0.60 | -91.5 % | 0.80 / 0.38 |
| long Top 3, 3-Wochen | 16.5 % | 0.57 | -89.7 % | 0.99 / 0.10 |
| long Top 3, 4-Wochen | 14.1 % | 0.55 | -89.2 % | 1.04 / -0.04 |
| long Top 3, 8-Wochen | 24.7 % | 0.62 | -91.0 % | 1.04 / 0.03 |
| long Top 3, 16-Wochen | 35.5 % | 0.75 | -86.7 % | 1.14 / 0.33 |
| Long-Short Top3/Bot3, 3-Wochen (Leerverkauf ohne Kosten) | n/a | -0.07 | (ueber -100 %, Modell ohne Liquidation) | -0.01 / -0.20 |
| Long-Short Top3/Bot3, 16-Wochen | -0.6 % | 0.21 | -87.9 % | 0.59 / -0.20 |
Lesart: Der LTW-Effekt (1-4-Wochen-Momentum) zeigt sich in einem Universum grosser, liquider Coins NICHT; in der zweiten Haelfte (2022-2026) ist 3-4-Wochen-Momentum sogar schlechter als Equal-Weight. Das ist konsistent mit Han/Kang/Ryu ("CS schwach") und Begusic/Kostanjcar (Effekt nur bei Liquiden, klein). Einschraenkungen: nur 10 Coins, Survivorship-Bias (hier eher zugunsten aller Strategien), kein 1.583-Coin-Universum. Aussagekraft = niedrig, aber keinerlei Hinweis auf einen handelbaren Vorteil.

### 4.6 Krypto-Funding-Carry (funding.py, carry.py), Binance USDT-M Perp, Summe der 8-Stunden-Funding-Raten je Kalenderjahr
BTC: 2019 (ab 10.9.) 2.31 %, 2020 17.24 %, 2021 30.61 %, 2022 4.16 %, 2023 7.87 %, 2024 11.96 %, 2025 5.13 %, 2026 (bis 12.10., ca. 2.9 % annualisiert) 2.26 %.
ETH: 2019 (ab 27.11.) 0.85 %, 2020 27.49 %, 2021 37.54 %, 2022 0.79 %, 2023 8.26 %, 2024 13.00 %, 2025 4.93 %, 2026 YTD 1.51 %.
Zum Vergleich T-Bill (Summe ueber ^IRX): 2022 ca. 2.0 %, 2023 5.0 %, 2024 5.0 %, 2025 4.05 %, 2026 YTD 2.86 %. Aktueller ^IRX: 4.06 %.
Regel "an, wenn trailing 30-Tage-Funding annualisiert > T-Bill + 2 %, sonst Cash; 30 bp pro Round-Trip (Einstieg+Ausstieg), pro Nominal": Jahresergebnisse 2023 6.25 %, 2024 11.58 %, 2025 3.95 %, 2026 YTD 2.57 % (T-Bill 5.04 / 4.97 / 4.05 / 2.86 %). Also Ueberschuss ueber Cash: 2023 ca. +1.2, 2024 ca. +6.6 Prozentpunkte, 2025 ca. -0.1, 2026 YTD ca. -0.3 Prozentpunkte (Funding "immer an" 2025: 5.13 % vs. 4.05 % T-Bill, also knapp +1) - auf Nominal-Basis, VOR Basisrisiko, Margin-Kapitalbindung (nur ca. 50-90 % des Kapitals arbeiten), Boersen-Gegenparteirisiko, MiCA-/Verfuegbarkeit fuer deutsche Privatanleger. Das Funding-Signal ist nur das halbe Bild: die Basis Perp-Spot und die Futures-Basis (CME) sind in dieser Prüfung NICHT enthalten.

## 5. Offene Punkte / was ich NICHT geklaert habe
- Liu/Tsyvinski RFS 2021 (TS-Momentum, Investor Attention) nicht gelesen. Han/Kang/Ryu und Zarattini et al. nur auf Abstract-Niveau. Die belastbare Aussage "TS-Momentum in Krypto funktioniert nach Kosten" haengt an Abstracts + eigenem Check, nicht an Volltexten.
- Gold: keine Gold-spezifische Quelle gelesen; eigener Check zeigt keinen Trend-Vorteil.
- Rohstoff-Term-Structure mit Gratis-Daten: nicht umsetzbar (Yahoo hat nur Front-Month-Ketten; Einzelkontrakt-Historien verfallen). Falls Quant-Lab spaeter bezahlte/halbfreie Quellen zulaesst (CME-Settlements, Stooq?), Prüfen - NICHT geprueft.
- Fuer deutsche Privatanleger vermutlich einzig praktikabel: ETC/ETP-Wrapper (BTCE.DE, VBTC.DE, ABTC.SW; SGLD.L fuer Gold - letzteres aus tsmom.md uebernommen), aber Spread/TER/Steuer nicht modelliert.
- Hypothese-vor-Test-Regel des Quant-Labs: die Regeln in Abschnitt 3 stehen jetzt fest; falls sie weiterverfolgt werden, gehoeren sie mit Erwartung/Abbruchkriterium in `docs/HYPOTHESEN.md`, bevor weiter getestet wird. Die Daten der eigenen Checks sind damit "verbraucht" fuer Bestaetigung, neue Bestaetigung nur mit frischen Daten (Walk-forward ab jetzt).
