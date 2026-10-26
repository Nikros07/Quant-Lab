# Familie TSMOM / Trendfolge - Literaturrecherche und Strategie-Kandidaten

Stand: 2026-10-11. Quant-Research-Analyst-Lauf (Workflow "research:tsmom"). Sprache: Deutsch.
Alle Zahlen stammen aus Seiten/PDFs, die in dieser Session wirklich abgerufen und gelesen wurden, oder aus eigenen
Plausibilitaetsrechnungen (klar als "EIGENER CHECK" markiert). Was nicht gefunden wurde, steht als "nicht gefunden".

## 0. Kurzfazit (ehrlich)

1. Der wissenschaftliche Kern ist stark: Trendfolge/TSMOM ist ueber sehr lange Zeitraeume und Assetklassen signifikant
   (Hurst/Ooi/Pedersen 1880-2016, Lemperiere et al. t-Stat ca. 10 seit 1800). Aber: die Evidenz gilt fuer ein breites
   Futures-Universum (58-100+ Maerkte, Long/Short, Hebel, institutionelle Kosten).
2. Seit ca. 2009 ist der Vorteil fuer SCHNELLE Signale praktisch verschwunden (Kurth/Eisler/Rej/Bouchaud 2026:
   EWM-5-20 Sharpe 0.84 -> 0.12; langsame EWM-50-200 0.70 -> 0.40). Lemperiere 2014 sah schon "seit 2011 flach".
   Langsame Trends halten besser.
3. Kritik an der Statistik: Huang/Li/Wang/Zhou (JFE 2020) finden je Asset kaum Vorhersagbarkeit; die TSMOM-Strategie
   performt ungefaehr wie eine Strategie auf dem historischen Mittelwert. Kim/Tse/Wald (2016): MOP-Ergebnis stark vom
   Volatility-Scaling getrieben, Vorteil 2009-2013 weg.
4. EIGENER CHECK auf Gratis-ETFs (12 Assets, 2008-2026): Multi-Asset-TSMOM nach 10 bp Kosten hat Sharpe 0.15-0.39 und
   schlaegt weder SPY (0.57) noch 60/40 (0.65); gegenueber Equal-Weight-Buy&Hold der gleichen 12 ETFs (0.31) ist der Vorteil
   ca. null bis +0.1 (nicht signifikant bei 18 Jahren Daten, Standardfehler eines Sharpe ca. 0.24).
   Schnelle Signale (1-Monat-Anteil bei HOP) fressen die Kosten (Umschlag 19x/Jahr) -> "funktioniert nach Kosten nicht mehr".
5. Was robust bleibt: Trendfilter als DRAWDOWN-KONTROLLE (Faber-SMA10): MaxDD ca. -16 % statt -46 % (EW5), aber keine
   Renditeverbesserung, und in Bullenmaerkten (2013-2026) deutlicher Rueckstand. Fuer das Quant-Lab-Ziel "Geld sicher halten"
   ist das der plausibelste Kandidat; fuer "Edge nach Kosten" gibt es hier KEINEN belegten Kandidaten im Gratis-ETF-Raum.

## 1. Methodik und Datenlage

- Papers per WebFetch/PDF gelesen (Volltext lokal extrahiert): MOP 2012, Hurst-Ooi-Pedersen 2017, Levine-Pedersen 2016,
  Lemperiere et al. 2014 (arXiv), Kurth et al. 2026 (arXiv), Georgopoulou-Wang 2017 (Autorenmanuskript), Faber (SSRN 962461,
  Update Feb 2013), Harvey et al. 2018 (Vol-Targeting).
- Nur Abstract/Seitenzusammenfassung gesehen (kein Volltext): Huang et al. 2020 (ideas.repec), Kim/Tse/Wald (Quantpedia-Seite),
  Baltas/Kosowski "Demystifying" (Imperial-Repository-Abstract; SSRN-Seite lieferte 403, CME-Mirror Timeout, Imperial-Download 405).
- Nicht abrufbar (403): Alpha Architect (zwei Seiten), SSRN-Abstractseiten. Deshalb KEINE Alpha-Architect-Zahlen im Dokument.
- Nur als Suchtreffer-Snippet (nicht abgerufen, keine Zahlen verwendet): Newfound "The Luck of the Rebalance Timing" (2013) und
  Hoffstein/Faber/Braun "The Dumb (Timing) Luck of Smart Beta" (2019) - nur als Hinweis auf Rebalance-Timing-Luck.
- Bulletproof-Hinweis: Hurst-Ooi-Pedersen enthaelt die Kennzahlen-Tabellen (Exhibit 1-10) nur als Grafiken; Portfolio-Sharpe
  1880-2016 nicht extrahierbar. Im Text steht nur: durchschnittlicher Sharpe je Markt (brutto) ca. 0.4, 8 von 10 der groessten
  60/40-Drawdowns mit positivem TSMOM-Ertrag, groesste TSMOM-Drawdowns bis ca. -25 %. Eine Sekundaerquelle (CXO via Suchtreffer)
  nennt 0.76 Sharpe nach Kosten und 2/20 - NICHT bestaetigt, deshalb nicht verwendet.

### Gratis-Daten, geprueft per yfinance am 2026-10-11 (erster Kurs / Datenpunkte bis 2026-10-09)
Aktien: SPY 1993-01-29, EFA 2001-08-27, EEM 2003-04-14, IWM 2000-05-26, QQQ 1999-03-10, VWO 2005-03-10.
Anleihen: IEF 2002-07-30, TLT 2002-07-30, SHY 2002-07-30, AGG 2003-09-29, BIL 2007-05-30, LQD 2002-07-30, HYG 2007-04-11, TIP 2003-12-05, BND 2007-04-10.
Real Assets: VNQ 2004-09-29, GLD 2004-11-18, DBC 2006-02-06, USO 2006-04-10.
FX-ETFs: FXE 2005-12-12, FXY 2007-02-13, FXB 2006-06-26, FXA 2006-06-26, UUP 2007-03-01.
Managed-Futures-ETFs (Benchmark/Proxy): DBMF 2019-05-08, KMLM 2020-12-02, CTA 2022-03-08.
Indizes: ^GSPC 1927-12-30 (nur Preisindex, ohne Dividenden), ^IRX 1960-01-04 (13-Wochen-T-Bill-Rendite, % p.a.), ^TNX 1962-01-02, ^VIX 1990-01-02, DX-Y.NYB 1971-01-04, ^GDAXI 1987-12-30, ^STOXX50E 2007-03-30, BTC-USD 2014-09-17.
Futures-Kontinuierlich (Yahoo): ES=F/NQ=F 2000-09-18, ZN=F/ZB=F 2000-09-21, GC=F/SI=F/HG=F 2000-08-30, CL=F 2000-08-23, ZC=F/ZW=F 2000-07-17, 6E=F 2000-09-12, 6J=F 2000-09-13, 6B=F 2000-10-05, 6A=F 2000-11-08, 6C=F 2000-05-23.
UCITS (fuer deutsche Privatanleger handelbar): IWDA.AS 2009-09-25, EUNL.DE 2009-09-25, SXR8.DE 2010-05-19, CSPX.L 2010-09-15, XEON.DE 2008-01-02 (EUR-Overnight-Cash), IBTM.L 2008-01-02, IEAC.L 2009-03-06, SGLD.L 2009-06-26, XDWD.DE 2014-08-15, VWCE.DE 2019-07-29.
Ken French Data Library (Mkt-RF, RF monatlich ab 1926-07) fuer lange Aktien-Trendfilter-Tests: aus dem Gedaechtnis, in dieser Session NICHT geprueft/geladen.

Warnung Yahoo-Futures: ein kurzer Test zeigte CL=F mit NEGATIVEM Schlusskurs (-37.63 am 2020-04-20) und 90 Tagen mit |Rendite|>8 %;
GC=F min 255.1 (2001-02-15), was dem damaligen Spot-Niveau entspricht, also keine Rueckwaerts-Anpassung. Die "=F"-Serien sind
unbereinigte Front-Month-Verkettungen (Roll-Luecken, kein sauberer Carry). Fuer Signalberechnung auf Renditen ungeeignet ->
ETF-Proxys (Roll/Carry stecken im ETF-Preis) nutzen.

Deutsche Praxis (Hinweise, nicht modelliert): US-ETFs (SPY, EFA, ...) sind bei deutschen Brokern fuer Privatanleger wegen
PRIIPs/KID meist gesperrt -> UCITS-Gegenstuecke (kurze Historie, s. oben). Jeder Ausstieg realisiert Gewinne (Abgeltungsteuer);
Steuern, Teilfreistellung, Vorabpauschale sind in KEINER Rechnung unten enthalten. Short-Positionen/Hebel ueber Privatbroker nur eingeschraenkt
(CFDs, Futures); deshalb gibt es jeweils eine Long/Flat-Variante.

## 2. Strategien (sortiert nach erwarteter Robustheit)

Gemeinsame Konventionen fuer alle Regeln:
- Preise: taegliche Adjusted Closes (yfinance auto_adjust=True, Total-Return-Naeherung).
- Monatsende t = letzter Handelstag des Kalendermonats. Signal NUR aus Daten bis Schlusskurs t. Handel frueestens am naechsten Handelstag
  (t+1), Ausfuehrung im Backtest zum Schlusskurs t+1 (Variante: Eroeffnung t+1). Positionen gelten fuer Renditen ab t+2.
- Cash/rf: taeglicher Satz rf_d = ^IRX[Vortag]/100/252 (oder BIL/SHY/XEON.DE als handelbarer Cash-Proxy).
- Kosten: ETF 5-10 bp je Seite auf |Delta Gewicht| plus TER; Futures nicht vorgesehen.

### S1 faber_gtaa5_sma10 (Rang 1) - Faber 2007/2013 "GTAA 5"
Regel:
```
UNIVERSE = [SPY, EFA, IEF, VNQ, DBC]   # Faber-Original: S&P500, MSCI EAFE, US 10y Govt, NAREIT, GSCI (Total Return)
am Monatsende t (letzter Handelstag):
  fuer i in UNIVERSE:
     pm_i = Liste der letzten 10 Monatsend-Adjusted-Closes inkl. t
     sma_i = mean(pm_i)
     sig_i = 1 wenn adjclose_i(t) > sma_i sonst 0          # strikt groesser, Gleichstand -> 0
  w_i = 0.20 * sig_i ; w_cash = 1 - sum(w_i)                # Cash = 13W T-Bill (^IRX-Accrual) bzw. BIL/SHY
  handle auf Zielgewichte zum Schlusskurs t+1; halten bis zum naechsten Monatsend-Signal
kein Hebel, keine Shorts; frueester Start 2006-12 (DBC hat erst ab 2006-02 zehn Monatsenden)
```
Evidenz (Faber, SSRN 962461, Update Feb 2013, Volltext gelesen): S&P 500 1901-2012: Timing 10.18 % vs 9.32 % p.a. (compound),
MaxDD 42.24 % vs 83.66 %, ca. 70 % der Zeit investiert, unter 1 Round-Trip pro Jahr; GTAA 1973-2012: Drawdown von 46 % auf unter 10 %;
2006-2012 (als Out-of-sample deklariert, Autor ist Fondsmanager mit Eigeninteresse) schlug Timing Buy&Hold um ueber 2 Prozentpunkte p.a.
Faber nennt selbst: ca. 30 % Cash im Schnitt, Umschlag ca. 70 %/Jahr, 3-4 Round-Trips pro Jahr fuer das Portfolio; Kosten/Steuern im Backtest ausgeschlossen.
Unabhaengiger Out-of-sample-Check (Concretum Group Substack, 200-Tage-SMA-Variante, 2006-01 bis 2025-03, 10 bp Kosten angenommen):
CAGR 6.05 %, Sharpe 0.68, MaxDD 11.7 % (In-sample 1972-2005 laut Artikel: CAGR 11.7 %, Sharpe 0.81, MaxDD 9.5 %). Er nennt selbst Rendite unter In-sample,
Schwaeche in "choppy" Maerkten und lange Cash-Phasen. Rebalance-Tag-Streuung (Timing Luck): CAGR-Spanne ca. 220 bp ueber Monatsend-Tage; Tranching in 4 Teilportfolios senkt die Spanne stark.
EIGENER CHECK (SMA10, Dez 2006 - Okt 2026, 10 bp, Ausfuehrung t+1-Close, Cash ^IRX): CAGR 4.77 %, Vol 8.1 %, Sharpe 0.43, MaxDD -15.8 %
vs. Equal-Weight-5-Buy&Hold: 6.40 % / 14.6 % / 0.39 / -45.7 %. 2007-2014: Sharpe 0.40 vs 0.31; 2015-2026: Sharpe 0.46 vs 0.51, CAGR 5.1 % vs 7.5 %.
Umschlag ca. 1.9 (Summe |Delta w|)/Jahr. Sensitivitaet: SMA 6/8/10/12 x Signaltag-Offset 0/5/10/15: CAGR 4.1-5.4 %, Sharpe 0.35-0.50; fuer SMA10 Spanne 0.76 pp.
Nachpublikation: Rendite-Vorteil nicht bestaetigt, Risiko-Vorteil (Drawdown, Vol) bestaetigt. Tail-Risiken: Crash innerhalb eines Monats (z. B. 1987-Typ) wird nicht abgefangen
(Faber/HOP raeumen das ein); V-foermige Erholungen und Seitwaertsmaerkte erzeugen Whipsaw; lange Cash-Phasen kosten in Bullenmaerkten (2013-2026 deutlich).
Datenstart: SPY 1993, EFA 2001-08, IEF 2002-07, VNQ 2004-09, DBC 2006-02 -> Gesamtsystem ab Ende 2006. Lange Historie nur ueber Indizes (^GSPC 1927 als Preisindex) oder Ken French.
UCITS-Variante (z. B. IWDA.AS statt SPY/EFA, IBTM.L/IEAC.L fuer Anleihen, SGLD.L fuer Gold): Historie erst ab 2009-2010.

### S2 faber_spx_sma10_cash (Rang 2) - Ein-Asset-Marktfilter (Faber Abschnitt S&P 500)
Regel:
```
ASSET = SPY (Total Return, ab 1993-01-29)   # lange Historie: ^GSPC Preisindex ab 1927 (ohne Dividenden); UCITS: IWDA.AS/EUNL.DE ab 2009-09-25
CASH  = ^IRX-Accrual bzw. XEON.DE (ab 2008-01-02) bzw. BIL
am Monatsende t:  sig = 1 wenn adjclose(t) > mean(letzte 10 Monatsend-Closes inkl. t) sonst 0
Gewicht ASSET = sig, Cash = 1 - sig; Ausfuehrung Schlusskurs t+1; Kosten 5 bp je Seite
```
Evidenz: Faber-Zahlen wie oben (1901-2012). EIGENER CHECK SPY (5 bp): 1993-2026: CAGR 9.69 % / Vol 12.9 % / Sharpe 0.59 / MaxDD -26.3 % vs Buy&Hold 10.87 % / 18.7 % / 0.51 / -55.2 %;
1993-2006: Sharpe 0.65 vs 0.45; 2007-2026: 0.55 vs 0.55; 2015-2026: CAGR 7.26 % vs 13.87 %, Sharpe 0.45 vs 0.71, MaxDD -26.3 % vs -33.7 % (der Filter war im Bullenmarkt nicht schuetzend genug und kostete Rendite).
Etwa 1.4 Wechsel/Jahr. ^GSPC-Preisindex 1961-2026 (ohne Dividenden, beide Seiten): 8.18 % vs 7.75 % CAGR, MaxDD -33.2 % vs -56.8 %; 1961-2012: 8.19 % vs 6.36 %; 2000-2012: 5.44 % vs -0.23 %;
2013-2026 (nach Fabers Update): 8.13 % vs 13.17 %, Sharpe 0.55 vs 0.71. -> Schutz in langen Baeren (2000-2012), teure Verzoegerung in V-Erholungen/Bullenmaerkten.
Nachpublikation: Ertrag nicht besser als Buy&Hold, Risikoreduktion ja. Tail-Risiko: Gap-Down ueber Monatsende, mehrere Fehlsignale in Folge (2015-2026 MaxDD -26 % im Filter selbst).
Gleiches Signal wie S1, daher stark korreliert mit S1 (keine echte Diversifikation der Idee).

### S3 slow_ewma_crossover_riskparity (Rang 3) - langsame Trendfolge nach Lemperiere/Kurth + Levine-Pedersen
Regel (Papier-Variante daily; Quant-Lab-Anpassung monatlich):
```
UNIVERSE_ETF12 = [SPY,EFA,EEM,IEF,TLT,VNQ,GLD,DBC,FXE,FXY,FXB,FXA]  # gemeinsamer Start 2007-02-13 (FXY)
fuer jeden Handelstag t und Asset i:
   f_t = EWMA(P, alpha=1-exp(-1/50)),  s_t = EWMA(P, alpha=1-exp(-1/200))    # tau=50 und 4*tau=200 Tage, auf Adjusted Close
   raw_t = f_{t-1} - s_{t-1}                                                  # nur Daten bis Vortag
   z_t = clip( raw_t / EWMSTD(raw, alpha=1-exp(-1/800))_t , -2, 2 )           # 16*tau=800 Tage Streuung
am Monatsende t:
   sigma_i = sqrt(261 * EWMA(excess_ret^2, COM=60 Tage))                      # MOP-Vol-Schaetzer
   w_i_raw = z_i / sigma_i / N          # N = Anzahl Assets mit Daten
   MODE=LS (Papier): w = w_raw ; MODE=LF (Privatanleger): w = max(w_raw,0) und sum(w) <= 1 (kein Hebel), Rest Cash
   Skaliere w so, dass ex-ante Portfolio-Vol = 10 % (Kovarianz der letzten 756 Handelstage, min. 252), Bruttohebel <= 3 (nur MODE=LS)
   Ausfuehrung Schlusskurs t+1
```
Evidenz: Lemperiere/Deremble/Seager/Potters/Bouchaud (arXiv 1404.3274, Volltext gelesen): t-Stat ca. 5 seit 1960 (Futures), ca. 10 seit 1800 (Spot Rohstoffe/Indizes),
Sharpe brutto (ohne Kosten) 0.80/0.83/0.78/0.80/0.76/0.65/0.57 fuer Zeitskalen n = 2/3/5/7/10/15/20 Monate seit 1960; Signal saettigt bei starken Trends;
"lange Trends ohne statistische Verschlechterung, kurze Trends deutlich schwaecher"; Fig. 6: "seit 2011 praktisch flach"; typische Drawdown-Dauer 1/S^2 Jahre (Sharpe 0.7 -> ca. 2 Jahre, 4 Jahre nicht ungewoehnlich).
Kurth/Eisler/Rej/Bouchaud (arXiv 2607.01550, 2026, Volltext gelesen): ca. 100 liquide Futures, 1995-2025, EWM-tau-4tau mit Clip +-2; Sharpe 1995-2009 vs 2009-2025:
tau=5: 0.84 -> 0.12; 10: 0.83 -> 0.22; 20: 0.79 -> 0.27; 50: 0.70 -> 0.40 (Unsicherheit ca. +-0.25); SG-CTA-Index laut Paper seit 2008/09 praktisch flach (ausser 2014 und Covid);
Bruch haengt an "volatilitaetsnormierter Tickgroesse": Small-Tick-Kontrakte kollabieren, Large-Tick-Kontrakte bleiben (Sharpe 1.0-1.2 bei langen Signalen). Zahlen sind Papier-Simulationen ohne Handelskosten-Abzug (kein "net" im Text gefunden).
Levine-Pedersen (FAJ 2016, Volltext gelesen): TSMOM und gleitende-Durchschnitt-Crossover sind in allgemeinster Form aequivalent; empirisch 58 Instrumente 1985-04/2015, taeglich rebalanciert, brutto:
Sharpe TSMOM(22/66/260 Tage) = 0.97/1.20/1.45, MACROSS(3,12)/(8,32)/(32,128) = 1.01/1.06/1.33 -> Wahl des Filters ist weniger wichtig als Horizont, Portfoliokonstruktion und Risikomanagement.
EIGENER CHECK (ETF12, 10 bp, ab ca. 2008-03): MODE=LS: CAGR 5.17 %, Vol 11.1 %, Sharpe 0.38, MaxDD -24.0 % (brutto Sharpe 0.42); 2008-2014: 0.46, 2015-2026: 0.35. MODE=LF: 4.32 %, Vol 8.0 %, Sharpe 0.39, MaxDD -21.8 %.
Umschlag nur 3.8 (LS) bzw. 1.8 (LF) pro Jahr. Benchmarks gleiche Periode: EW12-B&H Sharpe 0.31, SPY 0.57, 60/40 0.65. -> Vorteil gegenueber EW12 ca. +0.07, nicht signifikant.
Nachpublikation: zeitliche Verschlechterung moderat, langsamer Horizont am robustesten; Kosten gering wegen niedrigem Umschlag. Tail: lange Flachphasen (2009-2013 im Papier), Korrelationssprung (alle Maerkte gleichzeitig), Trendumkehr-Schocks (2009-Q1/2020-Q1-Typ).

### S4 hop_multihorizon_tsmom_10vol (Rang 4) - Hurst/Ooi/Pedersen 2017
Regel (Papier-konform, ETF-Proxy statt 67 Maerkte):
```
UNIVERSE = ETF12 (s. S3); Maerkte nur mit verfuegbarer Historie
am Monatsende t, fuer jedes Asset i:
   ER_k = (P_i(t)/P_i(t-k Monate) - 1) - (kumulierter rf ueber dieselben k Monate),   k in {1,3,12}
   sign_k = +1 wenn ER_k > 0 sonst -1      # Long/Short (Papier); Variante LF: sign_k in {1,0}
   s_i = (sign_1 + sign_3 + sign_12) / 3                        # gleichgewichtete Mischung
   sigma_i = sqrt(261 * EWMA(excess_ret^2, COM=60 Tage))
   w_i_raw = s_i / sigma_i / N
   skaliere auf ex-ante Portfolio-Vol 10 % (Kovarianz der letzten 756 Handelstage, min. 252), Bruttohebel <= 3 (LS)
   LF: sum(w) <= 1, Rest Cash
   Ausfuehrung Schlusskurs t+1, Rebalancing monatlich
```
(HOP selbst: monatliche Daten, 3-Jahres-Kovarianz auf Monatsrenditen, immer Long oder Short in jedem Markt.)
Evidenz (Volltext gelesen): 67 Maerkte (29 Rohstoffe, 11 Aktienindizes, 15 Anleihen, 12 Waehrungen), Jan 1880 - Dez 2016, Futures wo verfuegbar, davor Cash-Index plus lokaler Zins;
TSMOM in jedem Jahrzehnt positiv (auch jede Einzelhorizont-Variante); durchschnittlicher Sharpe je Markt brutto ca. 0.4; positiver Ertrag in 8 von 10 groessten 60/40-Drawdowns (Baerenmaerkte langsam, im Schnitt ca. 15 Monate;
schnelle Crashs wie 1987 schlecht); groesste Drawdowns der Strategie bis ca. -25 %; Signal um 1 Monat verzoegert: deutlich schlechter, v. a. kurze Horizonte;
Kosten: AQR-eigene 2012-Schaetzungen (2x teurer 1993-2002, 6x vor 1993), Roll-Kosten NICHT enthalten, Gebuehren 2/20 simuliert. Beste Performance bei niedrigen Korrelationen zwischen Maerkten; Korrelationen stiegen 2008-2014.
Nachpublikation / Verfall: Baltas-Kosowski (nur Abstract): schwaches Post-2008 durch steigende Paar-Korrelationen, Korrelations-adjustierter Hebel verbessert; Georgopoulou-Wang (Manuskript): QE der Notenbanken verzerrte Korrelationen;
Kurth 2026: schnelle Signale (inkl. 1-Monats-Anteil) seit 2009 ohne Vorteil. EIGENER CHECK (ETF12, 10 bp): MODE=LS: CAGR 2.49 %, Vol 10.7 %, Sharpe 0.15, MaxDD -28.3 % (brutto 0.33; Bruttohebel im Schnitt 1.7; Umschlag 19x/Jahr);
2008-2014 Sharpe 0.36, 2015-2026 Sharpe 0.03. MODE=LF: Sharpe 0.24 (0.51 -> 0.08), Umschlag 6.6x. -> in ETF-Form nach Kosten kein Vorteil ggue. EW12-B&H (0.31).
Tail: Momentum-Crash/Trendumkehr gleichzeitig ueber viele Maerkte; mit Hebel (bis 3x) und Shorts echte Verlustgefahr; Finanzierungs-/Leihekosten fuer Shorts und Hebel im Check nur zu rf angesetzt (zu optimistisch).

### S5 mop2012_tsmom_12m_40vol (Rang 5) - Moskowitz/Ooi/Pedersen 2012 (Referenz-Replikation)
Regel:
```
UNIVERSE = ETF12 (Original: 58 Futures: 9 Aktienindizes, 13 Staatsanleihen, 12 Waehrungspaare, 24 Rohstoffe, ab 1985-01)
am Monatsende t, Asset i:
   ER12 = 12-Monats-Exzessrendite (Total Return minus rf)      # Lookback k=12 Monate, Haltedauer h=1 Monat
   pos_i = sign(ER12) * 0.40 / sigma_i                          # sigma_i = sqrt(261 * EWMA(excess_ret^2, delta=60/61)), Schwerpunkt der Gewichte 60 Tage
   Portfolio = Durchschnitt ueber alle verfuegbaren Assets: w_i = pos_i / N_t
   Ausfuehrung Schlusskurs t+1
```
Evidenz (Volltext gelesen): 58 liquide Futures; bei 1985-2009 jedes einzelne Instrument mit positivem TSMOM-Ertrag, 52 statistisch signifikant (5 %); diversifiziertes TSMOM: Sharpe > 1; Alpha ggue. MSCI World/FF-Faktoren 1.58 %/Monat (t=7.99);
1966-1985 (out-of-sample, wenige Instrumente) Sharpe 1.1; Portfolio-Vol ca. 12 % p.a. bei 40 %-Einzelziel (diversifizierte Futures-Welt). Kosten im Hauptergebnis nicht abgezogen (Tabelle 3 "gross").
Kritik/Verfall: Kim/Tse/Wald (Quantpedia-Zusammenfassung): Alpha 1.27 %/Monat mit Vol-Scaling vs 0.41 % ohne (1985-2009); Vorteil nach 2001 / 2009-2013 verschwunden; skalierter Buy&Hold aehnlich.
Huang/Li/Wang/Zhou (JFE 135(3), 2020, nur Abstract): je Asset kaum In-/Out-of-sample-Evidenz, gepoolter t-Wert nicht robust (Bootstrap), TSM-Strategie ~ Strategie auf historischem Mittelwert.
EIGENER CHECK (ETF12, 10 bp): MODE=LS: CAGR 4.93 %, Vol 18.5 %, Sharpe 0.28, MaxDD -39.2 % (brutto 0.35; Bruttohebel ca. 3.5x); 2008-2014 0.29, 2015-2026 0.27; MODE=LF: Sharpe 0.24, MaxDD -34.0 %.
-> in dieser Form kein Vorteil; dient als Replikations-Benchmark, nicht als Kandidat fuer Echtgeld.

## 3. Eigene Plausibilitaetsrechnung - Details und Grenzen

Skripte: `research/families/tsmom_checks/` (sim.py, faber.py, gspc.py, starts.py; sim_results.csv). UNGETESTET - nur Plausibilitaet.
- Universum ETF12 vorab festgelegt (nicht nach Ergebnis gewaehlt), gemeinsamer Start 2007-02-13, erste Handelsentscheidungen ca. 2008-03;
  Benchmarks starten 2008-01-01 (kleine Periodenabweichung).
- Handelskosten pauschal 10 bp je Seite (ETF) bzw. 5 bp (SPY-Check); Steuern, TER, Spread-Spitzen, Dividenden-Quellensteuer nicht modelliert.
- Long/Short und Hebel zu rf finanziert (zu optimistisch fuer Privatanleger); Short-Rebate = rf angenommen.
- Umschlag in Tabellen = Summe |Delta Gewicht| pro Jahr (Kostenpunkt = 10 bp x Umschlag).
- Dies sind KEINE Walk-forward-Validierungen und enthalten keine Mehrfachtest-Korrektur. Das 16er-Gitter (SMA x Tag-Offset) ist nur
  eine Robustheitsanzeige. Eine formale Pruefung muss nach Regel 3 vorregistriert werden (Hypothese + Abbruchkriterium) und auf frischen Daten laufen.

Tabelle (Periode ca. 2008-03 bis 2026-10, netto 10 bp, ETF12):
| Variante | CAGR % | Vol % | Sharpe | MaxDD % | Sharpe 08-14 | Sharpe 15-26 | Umschlag/J |
|---|---|---|---|---|---|---|---|
| S4 HOP LS 10vol | 2.49 | 10.7 | 0.15 | -28.3 | 0.36 | 0.03 | 19.2 |
| S4 HOP LF | 2.87 | 7.3 | 0.24 | -18.8 | 0.51 | 0.08 | 6.6 |
| S5 MOP12 LS 40vol | 4.93 | 18.5 | 0.28 | -39.2 | 0.29 | 0.27 | 12.9 |
| S5 MOP12 LF | 3.91 | 14.8 | 0.24 | -34.0 | 0.26 | 0.23 | 6.6 |
| S3 EWM50-200 LS 10vol | 5.17 | 11.1 | 0.38 | -24.0 | 0.46 | 0.35 | 3.8 |
| S3 EWM50-200 LF | 4.32 | 8.0 | 0.39 | -21.8 | 0.50 | 0.34 | 1.8 |
| SPY Buy&Hold | 11.35 | 19.7 | 0.57 | -51.9 | 0.41 | 0.71 | - |
| 60/40 (SPY/IEF) | 8.45 | 11.4 | 0.65 | -30.8 | 0.62 | 0.67 | - |
| EW12 Buy&Hold | 4.07 | 10.0 | 0.31 | -30.8 | 0.31 | 0.32 | - |

Tabelle S1/S2 (siehe oben bei den Strategien).
Beobachtung: Die ETF12-Periode ist ein langer Aktien-/Anleihen-Bullenmarkt mit Nullzins; Long/Short-Trendfolge profitiert davon nicht.
Das ist die gleiche Epoche, in der laut Kurth/Lemperiere auch die CTA-Industrie schwach war - der Check bestaetigt also das Verfall-Bild, nicht die Papier-Sharpes.

## 4. Vorschlaege fuer das Quant-Lab (nach Regeln in CLAUDE.md)

- Hypothese vor Test eintragen. Vorschlag H1: "Faber-SMA10 (S1/S2) senkt MaxDD um mind. 40 % ggue. Buy&Hold bei Sharpe >= B&H - 0.1 nach 10 bp und mit
  Ausfuehrung t+1; Abbruch, wenn auf frischen Daten (nach 2026-10) Sharpe < B&H - 0.2 UND MaxDD-Reduktion < 25 %."
  H2: "Langsame EWM-Trendfolge (S3, LF) hat Sharpe > EW12-B&H + 0.15 netto; Abbruch, falls < +0.05 im Walk-forward."
  H3 (Negativ-Erwartung, nur zur Dokumentation): S4/S5 erreichen netto in ETF-Form keinen Sharpe > 0.3.
- Einordnung zu schon Bekanntem (CLAUDE.md): ETF v4 (`adaptive_momentum_v4.py`) verliert laut Lab gegen S&P-500-Buy&Hold und gewinnt nur beim Drawdown -
  das deckt sich mit dem Befund hier fuer S1/S2 (Risiko-, nicht Renditevorteil). S1/S2 muessen daher gegen v4 als Referenz-Baseline antreten,
  nicht nur gegen Buy&Hold. Der Lab-Standard "Ausfuehrung zur Eroeffnung t+1" ist strenger als der Schlusskurs-t+1 der Checks hier -
  vor Nutzung die Open-Variante rechnen (Yahoo liefert Open; Kosten dann ggf. etwas hoeher).
- Pflicht-Konkurrenten: Buy&Hold gleiches Universum, 60/40, Zufallssignal mit gleichem Umschlag, Vol-skalierte Long-only-Variante (Kim/Tse/Wald-Test: ist es nur Vol-Scaling?).
- Rebalance-Timing-Luck testen: Signaltag-Offset variieren oder in 4 Tranchen splitten (Concretum: Spanne ca. 220 bp ueber Monatsend-Tage fuer 200-Tage-SMA).
- Benchmarks Managed Futures (Gratis-Daten): DBMF (ab 2019-05-08), KMLM (ab 2020-12-02), CTA (ab 2022-03-08) - zu kurz fuer Validierung, aber als Realitaets-Check der CTA-Industrie nutzbar.
- Falls Futures-Daten noetig: keine Yahoo "=F"-Serien fuer Renditesignale; saubere, rueckwaerts-bereinigte Reihen ggf. kostenpflichtig (nicht verwenden ohne Rueckfrage, Budgetregel).
- Fuer den echten Betrieb als UCITS: IWDA.AS/EUNL.DE (2009-09), XEON.DE (2008-01), IBTM.L (2008-01), IEAC.L (2009-03), SGLD.L (2009-06): Backtest-Fenster nur ca. 2010-2026 - weniger als zwei Zyklen.

## 5. Quellenliste (alle URLs wurden in dieser Session angefragt; Status in Klammern)

- Moskowitz/Ooi/Pedersen, "Time series momentum", JFE 104 (2012) 228-250, DOI 10.1016/j.jfineco.2011.11.003
  - https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum (Seite gelesen, Abstract)
  - https://fairmodel.econ.yale.edu/ec439/jpde.pdf (Volltext-PDF, lokal extrahiert und gelesen)
- Hurst/Ooi/Pedersen, "A Century of Evidence on Trend-Following Investing", JPM 44(1), Fall 2017
  - https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing (Seite gelesen)
  - https://fairmodel.econ.yale.edu/ec439/hurst.pdf (Volltext, gelesen)
- Levine/Pedersen, "Which Trend Is Your Friend?", FAJ 72(3) 2016, 51-66, DOI 10.2469/faj.v72.n3.3
  - https://research-api.cbs.dk/ws/files/60084063/lasse_heje_pedersen_et_al_which_trend_is_your_friend_publishersversion.pdf (Volltext gelesen)
- Lemperiere/Deremble/Seager/Potters/Bouchaud, "Two centuries of trend following", arXiv:1404.3274 (2014)
  - https://arxiv.org/abs/1404.3274 und https://arxiv.org/pdf/1404.3274 (gelesen)
- Kurth/Eisler/Rej/Bouchaud, "Is Trend Still Your Friend? A Microstructural Account of the Demise of Short-Term Trend-Following", arXiv:2607.01550 (2. Juli 2026)
  - https://arxiv.org/abs/2607.01550 und https://arxiv.org/pdf/2607.01550 (gelesen)
- Huang/Li/Wang/Zhou, "Time series momentum: Is it there?", JFE 135(3) (2020) 774-794, DOI 10.1016/j.jfineco.2019.08.004
  - https://ideas.repec.org/a/eee/jfinec/v135y2020i3p774-794.html (Abstract gelesen); https://profiles.wustl.edu/en/publications/time-series-momentum-is-it-there/ (Suchtreffer)
- Kim/Tse/Wald, "Time series momentum and volatility scaling", Journal of Financial Markets 30 (2016) 103-124
  - https://quantpedia.com/deconstructing-the-time-series-momentum-strategy/ (Zusammenfassung gelesen); https://ideas.repec.org/a/eee/finmar/v30y2016icp103-124.html (Suchtreffer)
- Baltas/Kosowski, "Demystifying Time-Series Momentum Strategies: Volatility Estimators, Trading Rules and Pairwise Correlations" (SSRN 2140091)
  - https://spiral.imperial.ac.uk/handle/10044/1/41472 (Abstract gelesen); https://papers.ssrn.com/abstract=2140091 (403, nicht gelesen); PDF-Downloads (CME, Imperial) scheiterten.
- Georgopoulou/Wang, "The Trend Is Your Friend: Time-Series Momentum Strategies across Equity and Commodity Markets", Review of Finance 21(4) (2017) 1557-1592, DOI 10.1093/rof/rfw048
  - https://pure.manchester.ac.uk/ws/portalfiles/portal/39718724/The_Trend_is_Your_Friend_Time_Series_Momentum_Strategies_Across_Equity_and_Commodity_Markets.pdf (Autorenmanuskript, gelesen)
- Faber, "A Quantitative Approach to Tactical Asset Allocation", Journal of Wealth Management (Spring 2007); SSRN 962461, Update Feb 2013
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461 (Suchtreffer); Volltext-Kopie gelesen: https://mebfaber.com/wp-content/uploads/2016/05/SSRN-id962461.pdf
- Harvey/Hoyle/Korgaonkar/Rattray/Sargaison/Van Hemert, "The Impact of Volatility Targeting", JPM 45(1) (2018) 14-33, DOI 10.3905/jpm.2018.45.1.014
  - Ergebnis: Vol-Scaling hebt Sharpe fuer Risikoassets (Aktien, Kredit), fuer Anleihen/Waehrungen/Rohstoffe vernachlaessigbarer Effekt; Tail-Risiko sinkt. (Volltext lokal gelesen)
- Concretum Group, "Global Tactical Asset Allocation, Automated With Python and IBKR" (Substack; Daten bis 2025-03)
  - https://concretumgroup.substack.com/p/global-tactical-asset-allocation (gelesen)
- Hinweis Rebalance-Timing-Luck (nur Suchtreffer-Snippet): https://blog.thinknewfound.com/2013/08/the-luck-of-the-rebalance-timing/
- Nicht abrufbar (403): https://alphaarchitect.com/trend-following-is-everywhere/ und weitere Alpha-Architect-Seiten; SSRN-Abstractseiten.

## 6. Offene Luecken (ehrlich)

- Baltas-Kosowski-Details (Yang-Zhang-Fensterlaenge, Korrelations-Hebelformel, Kostenmodell, Sharpe) nicht gelesen -> keine eigene Strategie daraus.
- HOP-Portfolio-Sharpe 1880-2016 und Kostenwerte nicht extrahierbar (Grafiken).
- "Trends Everywhere" (Babu et al., AQR/JIM 2020) und Man-AHL-Papiere nicht abgerufen.
- Ken French/AQR-Datasets (z. B. "Time Series Momentum Factors" von AQR) nicht geladen - waere die naechste Gratis-Datenquelle fuer eine Faktor-Replikation (Download braucht Freigabe).
- Steuerliche Wirkung (Abgeltungsteuer) und UCITS-Handelskosten nicht gerechnet.
