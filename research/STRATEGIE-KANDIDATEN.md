# Strategie-Kandidaten fuer das Quant-Lab

Stand: 2026-10-12. Ausgewaehlt: 26 Strategien, abgelehnt: 64 Eintraege.

Rahmen: Privatanleger Deutschland, Gratis-Daten (yfinance, Ken French, AQR), gemeinsamer Backtester mit Signal am Schlusskurs t und Ausfuehrung fruehestens t+1, Kosten und Steuer zentral. Kontrollen (SPY Buy&Hold, 60/40, Zufall) laufen separat und sind hier nicht aufgefuehrt.

> Alle Parameter sind aus den Papers/Notizen uebernommen und vorab fixiert. Jede Variante zaehlt als Versuch fuer die Mehrfachtest-Korrektur (M <= 26 x 4 = 104). Die erwarteten Sharpe-Werte sind begruendete Groessenordnungen, keine Messwerte; wo ein eigener Plausibilitaetscheck aus den Familiennotizen vorliegt, ist er genannt (ungetestet im Sinne von nicht im Lab-Backtester reproduziert).

## Ehrliche Vorab-Einordnung

- Fast alle Kandidaten liefern nach Nachpublikations-Verfall eher Risikoreduktion (Drawdown, Volatilitaet) als Mehrrendite. Erwartete Sharpe-Werte liegen meist bei 0.2 bis 0.6, also im Bereich von SPY (ca. 0.5 bis 0.6 seit 2007).
- Bei ca. 18 Jahren Daten ist der Standardfehler eines Sharpe ca. 0.24. Differenzen unter ca. 0.15 sind nicht unterscheidbar. Mit M bis ca. 104 Versuchen braucht ein Deflated-Sharpe-Bestehen ca. 0.9 bis 0.95 Sharpe.
- Mehrere Eintraege sind bewusst Negativ- oder Kosten-Kontrollen (z. B. GGR-Paare, Nagel-Umkehr, Dividenden-/Value-Naeherungen). Ein Nullergebnis dort ist ein Befund, kein Fehler.

## Uebersicht der ausgewaehlten Strategien

| # | ID | Familie | Takt | Erwartete Sharpe nach Verfall |
|---|----|---------|------|-------------------------------|
| 1 | `faber_gtaa5_sma10` | tsmom | monatlich (Summe /Delta w/ ca. 1.9 pro J | 0.30-0.45 (eigener Check 0.43 netto, 2006-2026; liegt schon im Nach-Publikations-Zeitraum, daher kein weite... |
| 2 | `trend_ma12_us_equity_cash` | macro | monatlich (ca. 1.2 Wechsel pro Jahr) | 0.40-0.55 (eigener Check 0.55 vs 0.42 B&H seit 2000, 0.71 vs 0.80 seit 2013); der Nutzen ist Drawdown, nich... |
| 3 | `mop2012_tsmom_12m_40vol` | tsmom | monatlich (Umschlag 12.9 LS bzw. 6.6 LF  | 0.15-0.30 (eigener Check LS 0.28, LF 0.24 netto; Paper brutto >1 mit 58 Futures; Verfall nach 2008 belegt) |
| 4 | `sector_etf_top3_12m` | xsmom | monatlich | 0.35-0.55 (nahe SPY; Faber 0.54 brutto bis 2009 auf French-Industrien, Mehrwert gegenueber Gleichgewicht er... |
| 5 | `country_etf_xsmom_12_1` | xsmom | monatlich | LS 0.15-0.30 (Paper: 0.705 mit Index-Futures brutto 1979-2013; ETF in USD mit Waehrungsrauschen, 17 korreli... |
| 6 | `wml_volscaled_ff` | xsmom | monatlich (Gewichte), taegliche Basisdat | brutto 0.35-0.55 (statisch 1927-2013: 0.60, vol-skaliert grob doppelt in der Stichprobe, Momentum-Praemie s... |
| 7 | `keller_paa_g12` | tactical | monatlich (Umschlag ca. 284 % pro Jahr l | 0.40-0.60 (Keller 1.02 mit eigenen Proxys 1970-2022, letztes Jahrzehnt nur 5.8 % CAGR vs 12.1 % Gesamt; nac... |
| 8 | `antonacci_gem_lookback_ensemble` | tactical | monatlich (Signale), Sleeve-Reset jaehrl | 0.35-0.55 (Antonacci 1974-2011 in-sample ca. 14.9 % p.a.; ReSolve/Newfound: grosse Streuung je Lookback; na... |
| 9 | `eq_voltarget_ewma_harvey` | volmgmt | taeglich berechnet, Handel nur bei Ueber | 0.45-0.60 (Harvey 0.40 -> 0.48-0.51 mit ex-post-Skalierung; Cederburg 0.42 -> 0.51 mit p = 0.30; ohne Hebel... |
| 10 | `static_multifactor_equal_risk` | factors | monatlich | 0.20-0.45 (brutto 1963-2026 ca. 0.4-0.7 zu erwarten; McLean-Pontiff -58 % nach Publikation, RMW/CMA nur ein... |
| 11 | `lowvol_defensive_longonly` | lowrisk | Buy&Hold (ETF); French-Dateien monatlich | 0.45-0.70 (Quantpedia long-only-Dezil 0.72 1986-2006 brutto; eigener ETF-Check: USMV 0.90 vs SPY 0.94 seit ... |
| 12 | `fx_carry_g10_rank` | valuecarry | monatlich | 0.10-0.35 (2L/2S-Langfristwert 1975-2015 ca. 0.47 brutto; Rueckgang nach 2008 durch Zinskompression) |
| 13 | `country_value_cape_faber_proxy` | valuecarry | jaehrlich (Dezember) | 0.30-0.50 (Sharpe ca. wie Benchmark; Faber 0.56 In-Sample 1980-2011; GVAL-Produkt hinkte hinterher; Excess ... |
| 14 | `nagel_vix_gated_sector_etf_reversal` | reversal | taeglich | 0.0-0.30 (Nagel Industrien 0.56 brutto 1998-2010; mit Tagesverzoegerung, Kosten und Verfall nach 2010 wahrs... |
| 15 | `index_etf_ibs_rsi2_longonly` | reversal | taeglich (Signale), Haltedauer 1-5 Tage | 0.30-0.60 bei nur ca. 20-35 % Marktquote (Rendite unbekannt, keine Peer-Review-Evidenz; Ausfuehrung t+1 sta... |
| 16 | `ggr_distance_sector_zerocross` | pairs | Paarbildung halbjaehrlich, Signal taegli | -0.3 bis +0.2 (Clegg/Krauss survivorship-frei: netto Sharpe -0.55 fuer 1990-2015; GGR-Original 1.22 brutto ... |
| 17 | `tom_spy_m2_p3` | calendar | monatlich (12 Round-Trips pro Jahr) | 0.30-0.60 (Paper 1.04 bei 19 % Exposure 1926-2005; ETF-Aera-Befunde: Effekt nur noch am Tag +1; absolute Re... |
| 18 | `halloween_nov_apr_equity` | calendar | jaehrlich (2 Wechsel pro Jahr) | 0.35-0.55 (ca. Buy&Hold-Niveau bei halber Exposure; Dow 1915-2012: Sharpe 0.275 vs 0.279 laut Blog) |
| 19 | `ivp_risk_parity_unlevered` | riskparity | monatlich | 0.30-0.50 (AFP: 0.52 US 1926-2010 in Anleihen-Hausse; 2022 wirkt Aktien-Anleihen-Korrelationswechsel negati... |
| 20 | `putwrite_vrp_index` | volpremium | kein Signal (Index rollt monatlich) | 0.40-0.65 (Cboe/Bondarenko: bessere Sharpe als S&P 500, gesponsert, brutto, Schiefe -2.09; beta-bereinigtes... |
| 21 | `svxy_term_structure_filter` | volpremium | taeglich pruefen (CXO: 123 Wechsel 2011- | 0.30-0.70 mit extremer Unsicherheit (CXO 38 % CAGR vs 14.7 % B&H 2011-2019 in-sample; nur vier unabhaengige... |
| 22 | `bond_composite_3sig_longonly` | gap_bonds_duration_curve_carry_mom_value | monatlich | 0.25-0.45 (eigener Check mit Equity-Hedge statt Value 0.40 vs 0.19 B&H 1972-2026; ab 2018-11 -0.03 vs -0.26... |
| 23 | `commodity_gold_trend_dbc_gld` | crypto | taeglich pruefen (ca. 7.5 Einheiten Umsc | 0.25-0.45 (eigener Check 0.47 vs 0.38 B&H, 2016-2026 verliert der Filter gegen B&H; Standardfehler 0.22 bei... |
| 24 | `crypto_trend_ens_btc_eth` | crypto | taeglich pruefen, Umschlag ca. 6-19 Einh | 0.6-1.0 (Eigencheck 1.38 vs 1.10 B&H, in-sample-lastig; Standardfehler eines Sharpe ueber 11 Jahre 0.3-0.4;... |
| 25 | `pm_favorite_maker` | altdata | eventgetrieben, Haltedauer ca. 8 Tage bi | nicht bestimmbar (kein Zeitreihen-Sharpe); Erwartung pro Event nach Taker-Slippage etwa 0 bis +1 %, Maker-E... |
| 26 | `xtsmom_us_switch_longcash` | gap_crossasset_bond_equity_leadlag_signals | monatlich | 0.30-0.50 (Quantpedia-Indikation 6.5 % p.a. bei 10 % Vola brutto 1980-2015 fuer die Long-Short-Fassung; Lon... |

## Verteilung nach Renditequelle (Familie)

- **tsmom** (2): `faber_gtaa5_sma10`, `mop2012_tsmom_12m_40vol`
- **macro** (1): `trend_ma12_us_equity_cash`
- **xsmom** (3): `sector_etf_top3_12m`, `country_etf_xsmom_12_1`, `wml_volscaled_ff`
- **tactical** (2): `keller_paa_g12`, `antonacci_gem_lookback_ensemble`
- **volmgmt** (1): `eq_voltarget_ewma_harvey`
- **factors** (1): `static_multifactor_equal_risk`
- **lowrisk** (1): `lowvol_defensive_longonly`
- **valuecarry** (2): `fx_carry_g10_rank`, `country_value_cape_faber_proxy`
- **reversal** (2): `nagel_vix_gated_sector_etf_reversal`, `index_etf_ibs_rsi2_longonly`
- **pairs** (1): `ggr_distance_sector_zerocross`
- **calendar** (2): `tom_spy_m2_p3`, `halloween_nov_apr_equity`
- **riskparity** (1): `ivp_risk_parity_unlevered`
- **volpremium** (2): `putwrite_vrp_index`, `svxy_term_structure_filter`
- **gap_bonds_duration_curve_carry_mom_value** (1): `bond_composite_3sig_longonly`
- **crypto** (2): `commodity_gold_trend_dbc_gld`, `crypto_trend_ens_btc_eth`
- **altdata** (1): `pm_favorite_maker`
- **gap_crossasset_bond_equity_leadlag_signals** (1): `xtsmom_us_switch_longcash`

## Details je Strategie

### 1. Faber GTAA-5: 10-Monats-SMA-Trendfilter auf 5 Assetklassen (long/Cash)

- **ID:** `faber_gtaa5_sma10` | **Familie:** tsmom
- **Mechanismus:** Zeitreihen-Momentum/Trendfolge ueber Anlageklassen: Preise reagieren verzoegert auf Information und Risikoaversion wechselt in Wellen. Der 10-Monats-Durchschnitt zieht Kapital vor langen Baerenmaerkten ab. Belegt ist vor allem eine Risikoreduktion (Drawdown, Vol), kaum Mehrrendite.
- **Spezifikation (feste Parameter):** Universum SPY, EFA, IEF, VNQ, DBC (yfinance auto_adjust). Cash = taeglicher Zuwachs ^IRX[Vortag]/100/252. Am letzten Handelstag t jedes Monats: sig_i = 1 wenn AdjClose_i(t) > Mittel der letzten 10 Monatsend-AdjCloses inkl. t (strikt, Gleichstand = 0), sonst 0. Zielgewicht w_i = 0.20*sig_i, Rest Cash. Handel zum Schlusskurs t+1, Position verdient ab t+2, halten bis zum naechsten Monatsende. Kein Hebel, kein Short. Kosten 10 bp je Seite auf |Delta w| (Stress 20 bp). Erstes Signal 2006-12 (DBC ab 2006-02-06, 10 Monatsenden).
- **Ticker:** SPY, EFA, IEF, VNQ, DBC, ^IRX
- **Datenstart:** 2006-12 (US-ETFs; Langtest nur auf Indizes/French-Daten)
- **Rebalancing:** monatlich (Summe |Delta w| ca. 1.9 pro Jahr)
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - SMA 12 Monate statt 10
  - 3 gestaffelte Tranchen (Stichtage 0/7/14 Handelstage vor Monatsende, je 1/3) gegen Timing-Luck
  - Ausfuehrung Eroeffnung t+1 statt Schluss t+1
- **Abbruchkriterium:** Verwerfen, wenn netto (10 bp) der MaxDD nicht mindestens 10 Prozentpunkte unter dem Equal-Weight-5-Buy&Hold liegt ODER der Netto-Sharpe unter dem EW5 liegt, jeweils im Gesamtzeitraum und in beiden Haelften (2007-2016, 2017-2026).
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.30-0.45 (eigener Check 0.43 netto, 2006-2026; liegt schon im Nach-Publikations-Zeitraum, daher kein weiterer Abschlag; Vorteil gegenueber EW5 nur Drawdown)
- **Hinweis deutsche Privatanleger:** US-ETFs sind bei deutschen Brokern meist gesperrt (PRIIPs/KID). UCITS-Ersatz: IWDA/EUNL (ab 2009), IBTM.L (2008), Immobilien- und Rohstoff-UCITS mit kuerzerer Historie; Cash ueber Geldmarkt-ETF (XEON). Abgeltungsteuer bei jedem Ausstieg, Teilfreistellung fuer Aktienfonds; Steuer wird zentral modelliert.
- **Quellen:**
  - Faber 2007, A Quantitative Approach to Tactical Asset Allocation, https://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461
  - Concretum Group 2025, Global Tactical Asset Allocation (unabhaengiger Check), https://concretumgroup.substack.com/p/global-tactical-asset-allocation

### 2. Binaerer Trendfilter US-Aktien/Cash (MA(1,12)), Langzeit-Test auf French-Gesamtmarkt

- **ID:** `trend_ma12_us_equity_cash` | **Familie:** macro
- **Mechanismus:** Trendfilter auf dem Gesamtmarkt als Baer-Markt-Schutz: Wenn der Index unter seinem 12-Monats-Mittel liegt, steigen Volatilitaet und Ausfallwahrscheinlichkeit; Aktienpraemie ist dann im Mittel niedrig. Ersetzt faber_spx_sma10_cash (gleiche Idee) und liefert den einzigen Test ueber fast 100 Jahre.
- **Spezifikation (feste Parameter):** Signal: ^GSPC Preisindex, Schlusskurs am letzten Handelstag jedes Monats t. S_t = 1 wenn P_t >= Mittel der letzten 12 Monatsend-Schlusskurse inkl. t (Neely MA(1,12)), sonst 0. Position = S_t*100 % Aktienmarkt + (1-S_t)*100 % Cash; Handel zum Schlusskurs t+1, Rendite ab t+2. Renditeserie Backtest: Ken French Mkt = Mkt-RF + RF (taeglich), Cash = French RF. Live-Proxy SPY (ab 1993-01-29). Kein Hebel, kein Short. Kosten 10 bp je Wechsel (Stress 50 bp). Start: 1930.
- **Ticker:** ^GSPC, SPY, ^IRX, French:Mkt-RF, French:RF
- **Datenstart:** 1930 (Signal ab 1928-12 moeglich); Live-ETF ab 1993
- **Rebalancing:** monatlich (ca. 1.2 Wechsel pro Jahr)
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - SMA10-Regel (P_t > Mittel der letzten 10 Monatsenden), entspricht Fabers S&P-Teil
  - MA(2,12): Mittel(P_t,P_t-1) >= MA12
  - Signal auf Total-Return-Serie statt Preisindex
- **Abbruchkriterium:** Verwerfen, wenn 2000-2026 netto der Sharpe nicht ueber Buy&Hold liegt UND der MaxDD nicht mindestens 15 Prozentpunkte kleiner ist. (Als Risikoreduktion zaehlt der Filter nur, wenn Drawdown-Schutz in 2008 und 2020 sichtbar bleibt.)
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.40-0.55 (eigener Check 0.55 vs 0.42 B&H seit 2000, 0.71 vs 0.80 seit 2013); der Nutzen ist Drawdown, nicht Rendite
- **Hinweis deutsche Privatanleger:** Sehr gut umsetzbar: ein UCITS-S&P-500- oder MSCI-World-ETF (thesaurierend) plus Geldmarkt-ETF. Steuer: Gewinnrealisierung bei jedem Ausstieg, Verlust der Stundung; ca. 1 Wechsel pro Jahr bleibt ueberschaubar.
- **Quellen:**
  - Neely, Rapach, Tu, Zhou 2014, Forecasting the Equity Risk Premium: The Role of Technical Indicators, https://files.stlouisfed.org/files/htdocs/wp/2010/2010-008.pdf
  - Goyal, Welch, Zafirov 2023, Equity Premium Prediction (Folien), https://www.ivo-welch.org/research/presentations/99-stanford-prediction.pdf
  - Faber 2007 (S&P-500-Abschnitt 1901-2012), https://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461

### 3. Moskowitz-Ooi-Pedersen TSMOM: 12-Monats-Vorzeichen, vol-skaliert, ETF12-Proxy (Replikations-Benchmark)

- **ID:** `mop2012_tsmom_12m_40vol` | **Familie:** tsmom
- **Mechanismus:** Zeitreihen-Momentum ueber viele Maerkte: Unterreaktion auf Information und Herding erzeugen Autokorrelation in Renditen; Hedger zahlen Risikopraemien an Trendfolger. Ersetzt hop_multihorizon und slow_ewma als Vertreter der vol-skalierten Mehrmarkt-Trendfolge.
- **Spezifikation (feste Parameter):** Universum ETF12 = SPY, EFA, EEM, IEF, TLT, VNQ, GLD, DBC, FXE, FXY, FXB, FXA (gemeinsamer Start 2007-02-13; nur Assets mit Daten). Am Monatsende t: ER12 = 12-Monats-Exzessrendite (AdjClose-Rendite minus kumulierter ^IRX-Zins). sigma_i = sqrt(261*EWMA(excess_ret^2)) mit com=60 Tage. Hauptlauf MODE=LS (Papier): pos_i = sign(ER12_i)*0.40/sigma_i, w_i = pos_i/N_t, Bruttohebel <= 3, Finanzierung rf+0.5 % (Annahme). Zweitlauf MODE=LF: sign in {1,0}, Summe w auf <= 1.0 gekappt (proportional), Rest Cash. Ausfuehrung Schluss t+1, monatliches Rebalancing, Kosten 10 bp je Seite. Nicht auf Portfolio-Vol skaliert.
- **Ticker:** SPY, EFA, EEM, IEF, TLT, VNQ, GLD, DBC, FXE, FXY, FXB, FXA, ^IRX
- **Datenstart:** 2007-02-13
- **Rebalancing:** monatlich (Umschlag 12.9 LS bzw. 6.6 LF pro Jahr)
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - LF mit Gesamtgewicht <= 1 (Hauptlauf-Zweitlauf, siehe spec)
  - Portfolio-Vol-Ziel 10 % nach Hurst-Ooi-Pedersen (Kovarianz 756 Tage, Faktor 261, Hebel <= 3 nur LS)
  - Ausfuehrung Eroeffnung t+1
- **Abbruchkriterium:** Verwerfen als Echtgeld-Kandidat, wenn der Netto-Sharpe (LS und LF) unter dem EW12-Buy&Hold liegt (eigener Check 0.31) in beiden Halbzeiten. Bleibt als Replikations-Benchmark im Lab.
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.15-0.30 (eigener Check LS 0.28, LF 0.24 netto; Paper brutto >1 mit 58 Futures; Verfall nach 2008 belegt)
- **Hinweis deutsche Privatanleger:** LS (Shorts, Hebel bis 3x) ist fuer Privatanleger nicht umsetzbar; nur LF mit UCITS-ETFs und Waehrungsersatz (Waehrungs-ETFs fehlen in UCITS). Der Test dient als Benchmark fuer alle Trendfolger, nicht als Handelsidee.
- **Quellen:**
  - Moskowitz, Ooi, Pedersen 2012, Time series momentum, https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum
  - Hurst, Ooi, Pedersen 2017, A Century of Evidence on Trend-Following Investing, https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing
  - Kim, Tse, Wald 2016, Time Series Momentum and Volatility Scaling, https://quantpedia.com/deconstructing-the-time-series-momentum-strategy/

### 4. Faber-Sektorrotation: Top 3 von 9 SPDR-Sektor-ETFs nach 12-Monats-Rendite

- **ID:** `sector_etf_top3_12m` | **Familie:** xsmom
- **Mechanismus:** Querschnitts-Momentum auf Branchen-Ebene: Branchen-Informationen diffundieren langsam (Moskowitz/Grinblatt), Gewinner-Branchen bleiben kurzfristig Gewinner. Nach Arnott et al. teils Faktor-Momentum in anderer Verpackung.
- **Spezifikation (feste Parameter):** Universum fest: XLB XLE XLF XLI XLK XLP XLU XLV XLY (auto_adjust). XLRE/XLC nicht aufnehmen. Am letzten NYSE-Handelstag t: score_i = AdjClose_i[t]/AdjClose_i[t12]-1 (t12 = Monatsende 12 Monate vorher, kein Skip-Monat). Rang absteigend, Gleichstand alphabetisch. Top 3 je 1/3, Rest 0, voll investiert, kein Hebel, kein Cash-Filter. Order zur Eroeffnung t+1, halten bis zum naechsten Signaltag. Kosten 5 bp je Seite (Stress 25 bp). Erstes Signal 1999-12-31. Langzeit-Check (nicht handelbar): French 10/17 Industry Portfolios ab 1926, gleiche Regel.
- **Ticker:** XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY, SPY
- **Datenstart:** 1998-12-22 (erstes Signal 1999-12-31); Langzeit French ab 1926-07
- **Rebalancing:** monatlich
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - Combo-Score: Mittel der Renditen ueber 1/3/6/9/12 Monate
  - SMA10-Cash-Filter: alles Cash (RF), wenn SPY unter dem Mittel seiner letzten 10 Monatsenden
  - Hold-Buffer: gehaltener ETF bleibt, solange Rang <= 5
- **Abbruchkriterium:** Verwerfen, wenn der Netto-Sharpe nicht ueber dem monatlich rebalancierten Gleichgewichts-Korb der 9 ETFs liegt ODER der Permutationstest (Zufalls-Top-3) p > 0.10 ergibt.
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.35-0.55 (nahe SPY; Faber 0.54 brutto bis 2009 auf French-Industrien, Mehrwert gegenueber Gleichgewicht erwartet nahe 0)
- **Hinweis deutsche Privatanleger:** SPDR-Sektoren sind in Deutschland meist nicht kaufbar; UCITS-Sektor-ETFs (MSCI World/STOXX 600 Sektoren) haben kuerzere Historie. Hoher Umschlag (Faber 70-100 %) bedeutet Abgeltungsteuer-Drag.
- **Quellen:**
  - Faber 2010, Relative Strength Strategies for Investing, https://c.mql5.com/forextsd/forum/213/Relative%20Strength%20Strategies%20for%20Investing.pdf
  - Quantpedia, Sector Momentum - Rotational System, https://quantpedia.com/strategies/sector-momentum-rotational-system

### 5. Laender-ETF-Momentum (17 iShares-MSCI-Laender, 12-1, Rang-Gewichte)

- **ID:** `country_etf_xsmom_12_1` | **Familie:** xsmom
- **Mechanismus:** Internationales Querschnitts-Momentum (Asness/Moskowitz/Pedersen): Laendermaerkte zeigen Trend, getrieben von langsamer Informationsdiffusion und Kapitalflussverhalten; unabhaengige Renditequelle von US-Aktien-Momentum.
- **Spezifikation (feste Parameter):** Universum fest (17): EWA EWC EWG EWH EWI EWJ EWM EWN EWP EWQ EWS EWU EWW EWL EWD EWK EWO. Am letzten NYSE-Handelstag t von Monat m: score_i = AdjClose_i[Ende m-1]/AdjClose_i[Ende m-12]-1. rank_i aufsteigend (Gleichstand alphabetisch), z_i = rank_i - 9. Hauptlauf Long-Short dollar-neutral w_i = z_i/36 (Summe long +1, short -1). Order zur Eroeffnung t+1, Rebalancing monatlich. Sicherheiten zu ^IRX, Leihekosten 0.5 % p.a. (Annahme). Kosten 5 bp je Seite (Stress 10, 25). Erstes Signal 1997-03-31.
- **Ticker:** EWA, EWC, EWG, EWH, EWI, EWJ, EWM, EWN, EWP, EWQ, EWS, EWU, EWW, EWL, EWD, EWK, EWO, EFA, ^IRX
- **Datenstart:** 1996-03-18 (erstes Signal 1997-03-31)
- **Rebalancing:** monatlich
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - long_top5: 1/5 auf die 5 besten, long-only
  - long_top5_sma10: wie long_top5, aber ETF nur wenn AdjClose[t] > Mittel seiner letzten 10 Monatsenden, sonst Cash
  - Universum + EWZ, EWY, EWT, EZA ab Verfuegbarkeit
- **Abbruchkriterium:** Verwerfen, wenn der Netto-Sharpe der LS-Version < 0.20 oder der Permutationstest (zufaellige Raenge) p > 0.10 ist; die Long-only-Variante muss zusaetzlich den Gleichgewichts-Korb der 17 ETFs im Sharpe schlagen.
- **Erwartete Sharpe nach Nachpublikations-Verfall:** LS 0.15-0.30 (Paper: 0.705 mit Index-Futures brutto 1979-2013; ETF in USD mit Waehrungsrauschen, 17 korrelierte Maerkte); Long-only Top 5 ca. Markt-Sharpe 0.3-0.5
- **Hinweis deutsche Privatanleger:** Long-Short ist ueber ETFs nicht machbar. Realistisch ist nur die Top-5-Long-Variante mit UCITS-Laender-ETFs (iShares MSCI Japan, Germany, UK usw.); kleine Laender (EWK, EWO, EWD) haben UCITS-Aequivalente nur teilweise.
- **Quellen:**
  - Asness, Moskowitz, Pedersen 2013, Value and Momentum Everywhere, https://www.aqr.com/library/journal-articles/value-and-momentum-everywhere
  - Daniel, Moskowitz 2016, Momentum Crashes, https://business.columbia.edu/sites/default/files-efs/pubfiles/4607/mom11.pdf

### 6. Volatilitaets-skaliertes US-Aktien-Momentum (WML, Barroso/Santa-Clara; Messlatte auf Faktor-Ebene)

- **ID:** `wml_volscaled_ff` | **Familie:** xsmom
- **Mechanismus:** Momentum-Crashes sind vorhersagbar (hohe Vol nach Baerenmaerkten); Skalierung auf konstante Vol nimmt Crash-Risiko heraus und hebt die Sharpe. Steht fuer Risikomanagement des bekanntesten Aktien-Faktors; liefert dieselbe Information wie riskmanaged_momentum_bsc und vol_managed_momentum_bsc, die verworfen wurden.
- **Spezifikation (feste Parameter):** Daten Ken French: 10_Portfolios_Prior_12_2_Daily (Hi PRIOR, Lo PRIOR, wertgewichtet), F-F_Research_Data_Factors_daily (RF). WML[d] = R_hi - R_lo. Signaltag t = letzter NYSE-Handelstag jedes Monats: sigma = stdev(WML[t-125..t], ddof=1)*sqrt(252); w = min(0.12/sigma, 2.0) (Deckel 2.0 ist Schutzgrenze des Labs). Position ab t+1 bis zum naechsten Signaltag: +w auf Hi, -w auf Lo, Rest RF; Gewichte im Monat konstant. Kosten: 0.65 % pro Monat mal mittleres w (Novy-Marx/Velikov-Momentum-Kosten), plus die Standardkosten nicht doppelt zaehlen.
- **Ticker:** French:10_Portfolios_Prior_12_2_Daily, French:F-F_Research_Data_Factors_daily
- **Datenstart:** Ken French Daily: ca. 1927 (nicht verifiziert), Test ab 1930
- **Rebalancing:** monatlich (Gewichte), taegliche Basisdaten
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - statisch w = 1 (Kontrolle, Pflicht)
  - Vol-Ziel 19 % (Daniel/Moskowitz-Variante)
  - Deckel 1.0 statt 2.0
- **Abbruchkriterium:** Verwerfen, wenn der vol-skalierte WML 2008-2026 brutto den Sharpe des statischen WML nicht um mindestens 0.15 uebertrifft (Kernbehauptung), ODER wenn nach Kosten der Sharpe <= 0 ist.
- **Erwartete Sharpe nach Nachpublikations-Verfall:** brutto 0.35-0.55 (statisch 1927-2013: 0.60, vol-skaliert grob doppelt in der Stichprobe, Momentum-Praemie seit 1972 schwaecher); nach Momentum-Kosten (0.65 %/Monat) 0.0-0.25
- **Hinweis deutsche Privatanleger:** Nicht handelbar (Dezil-Shorts, Leihegebuehr). Forschungs-Messlatte: zeigt, ob Vol-Management eine Praemie rettet; MTUM-artige UCITS-Momentum-ETFs (iShares MSCI World Momentum) sind long-only und ein anderes, nicht belegtes Design.
- **Quellen:**
  - Barroso, Santa-Clara 2015, Momentum has its moments, https://ciencia.ucp.pt/en/publications/momentum-has-its-moments/
  - Daniel, Moskowitz 2016, Momentum Crashes, https://www.nber.org/papers/w20439
  - Cederburg, O'Doherty, Wang, Yan 2020, On the performance of volatility-managed portfolios, https://www.lehigh.edu/~xuy219/research/COWY.pdf

### 7. Keller Protective Asset Allocation G12 (Breadth, SMA12)

- **ID:** `keller_paa_g12` | **Familie:** tactical
- **Mechanismus:** Kombination aus relativem Momentum (Top 6 von 12) und Breadth-basiertem Crash-Schutz: Wenn viele Anlageklassen unter ihrem 12-Monats-Mittel liegen, wird dynamisch in Cash/Anleihen umgeschichtet. Diversifikation ueber Assetklassen plus Schutzmechanismus.
- **Spezifikation (feste Parameter):** Offensiv O = SPY, QQQ, IWM, VGK, EWJ, VWO, VNQ, DBC, GLD, TLT, HYG, LQD; Defensiv D = BIL, IEF. Am Schlusskurs des letzten Handelstags t: m_i = P_i(t)/mean(P_i(t),P_i(t-1M),...,P_i(t-12M)) - 1 (13 Monatsend-AdjCloses). b = Anzahl i in O mit m_i < 0; CF = min(1, b/6). Offensivanteil (1-CF) gleichgewichtet auf die 6 Assets mit hoechstem m_i; Defensivanteil CF komplett in das Asset aus {BIL, IEF} mit hoeherem m. Gesamtportfolio monatlich neu gewichten. Ausfuehrung Schluss t+1. Kosten 10 bp je Seite (Stress 5/20 bp). Start 2008-06 (BIL/HYG plus 13 Monate).
- **Ticker:** SPY, QQQ, IWM, VGK, EWJ, VWO, VNQ, DBC, GLD, TLT, HYG, LQD, BIL, IEF
- **Datenstart:** 2008-06
- **Rebalancing:** monatlich (Umschlag ca. 284 % pro Jahr laut Keller)
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - Top 4 statt Top 6
  - Breadth-Schwelle B=4 (CF = min(1, b/4))
  - 3 gestaffelte Sleeves (Stichtage -14/-7/0 Handelstage vor Monatsende)
- **Abbruchkriterium:** Verwerfen, wenn der Netto-Sharpe (10 bp) nicht ueber dem 60/40-Buy&Hold-Kontrolle und dem Gleichgewichts-Korb O liegt, oder wenn die Variantenfamilie (Top 4/6, B=4/6) einen PBO > 0.5 hat.
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.40-0.60 (Keller 1.02 mit eigenen Proxys 1970-2022, letztes Jahrzehnt nur 5.8 % CAGR vs 12.1 % Gesamt; nach Abschlag und Umschlagskosten)
- **Hinweis deutsche Privatanleger:** 12 ETFs, hoher Umschlag und Abgeltungsteuer bei jeder Umschichtung; UCITS-Aequivalente existieren fuer fast alle Bausteine (HYG, LQD, VGK, EWJ), aber mit kuerzerer Historie. Realistisch nur mit sehr niedrigen Handelskosten und Steuerwirkung im Backtest.
- **Quellen:**
  - Keller, Keuning 2016, Protective Asset Allocation (PAA), https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2759734

### 8. Antonacci Global Equities Momentum (GEM) als Multi-Lookback-Ensemble (6-12 Monate)

- **ID:** `antonacci_gem_lookback_ensemble` | **Familie:** tactical
- **Mechanismus:** Duales Momentum: relativ (US vs. Ex-US-Aktien) plus absolut (Aktien vs. T-Bill, sonst Anleihen). Das Ensemble ueber sieben Lookbacks reduziert das von Newfound gezeigte Spezifikationsrisiko; gleichzeitig ein Konzentrationstest (100 % in einem Asset).
- **Spezifikation (feste Parameter):** Assets: SPY, EFA (Ex-US; Hauptlauf EFA wegen Historie ab 2001-08), AGG, Cash ^IRX-Zuwachs (statt BIL, Start vorgezogen). Basisregel mit Lookback L: r_X = P_X(t)/P_X(t-L Monate)-1 (Total Return). Falls r_SPY > r_cash: 100 % in das Asset mit hoeherem r aus {SPY, EFA}; sonst 100 % AGG. Ensemble: 7 Sleeves L = 6,7,8,9,10,11,12, je 1/7 Kapital, jaehrlich im Dezember auf 1/7 zurueckgesetzt, dazwischen driftend. Ausfuehrung Schluss t+1, Kosten 10 bp je Seite (Stress 5/20). Start 2004-09 (AGG 2003-09 + 12 Monate).
- **Ticker:** SPY, EFA, AGG, ^IRX, ACWX, BIL
- **Datenstart:** 2004-09
- **Rebalancing:** monatlich (Signale), Sleeve-Reset jaehrlich
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - Ex-US = ACWX (ab 2008-03) statt EFA
  - Einzel-GEM mit L=12 (Originalregel, Kontrolle)
  - Anleihe-Bein = IEF statt AGG
- **Abbruchkriterium:** Verwerfen, wenn der MaxDD nicht mindestens 15 Prozentpunkte unter SPY liegt UND der Netto-Sharpe unter dem 60/40-Buy&Hold bleibt, oder wenn der Sharpe-Unterschied zwischen den Einzel-Lookbacks > 0.4 ausmacht (Spezifikationsrisiko dominiert).
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.35-0.55 (Antonacci 1974-2011 in-sample ca. 14.9 % p.a.; ReSolve/Newfound: grosse Streuung je Lookback; nach Kosten und Verfall)
- **Hinweis deutsche Privatanleger:** Sehr gut umsetzbar: nur 3-4 UCITS-ETFs (MSCI World, MSCI ACWI ex US/EM, Euro-Staatsanleihen/Global Aggregate hedged, Geldmarkt). Maximal ein Wechsel pro Monat, Steuer ueberschaubar.
- **Quellen:**
  - Antonacci 2017, Risk Premia Harvesting Through Dual Momentum, https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2042750
  - Newfound Research 2019, Fragility Case Study: Dual Momentum GEM, https://blog.thinknewfound.com/2019/01/fragility-case-study-dual-momentum-gem/

### 9. Vol-Targeting auf den US-Aktienmarkt (EWMA, Harvey et al.)

- **ID:** `eq_voltarget_ewma_harvey` | **Familie:** volmgmt
- **Mechanismus:** Volatilitaet ist persistent, Rendite pro Risikoeinheit schwankt weniger: Exposure invers zur erwarteten Vol zu setzen glaettet das Risiko (Vol-of-Vol, Tail-Risiko), ohne die erwartete Rendite proportional zu opfern. Die Sharpe-Verbesserung am Aktienmarkt selbst ist klein; robust ist der Tail-Effekt.
- **Spezifikation (feste Parameter):** r = Tages-Totalrendite (Backtest: French Mkt-RF + RF; Live SPY AdjClose), rf aus French RF. WARMUP = 270 Tage. lam = 0.5^(1/20); v[WARMUP-1] = mean(r[0:270]^2); v[t] = lam*v[t-1] + (1-lam)*r[t]^2 (Null-Mittelwert); sig[t] = sqrt(252*v[t]). target[s] = min(1.0, 0.12/sig[s-2]) (Signal Schluss s-2, Order Schluss s-1, Position s verdient r[s]); pos[s] = target[s] falls |target[s]-pos[s-1]| >= 0.05, sonst pos[s-1] (No-Trade-Band 5 pp, Lab-Ergaenzung). R[s] = pos*(r-rf) + rf - 2 bp*|dpos|. Kein Hebel (CAP 1.0).
- **Ticker:** SPY, ^IRX, French:Mkt-RF, French:RF
- **Datenstart:** French Daily ab 1926-07 (Test ab 1928); SPY ab 1993-01-29
- **Rebalancing:** taeglich berechnet, Handel nur bei Ueberschreiten des 5-pp-Bandes (ca. 1-5 Round-Trips pro Jahr)
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - CAP 1.5 (Hebel, Finanzierung rf+0.5 % Annahme)
  - Halbwertszeit 40 Tage statt 20
  - Vol-Ziel 0.10 statt 0.12
- **Abbruchkriterium:** Verwerfen, wenn die MaxDD-Reduktion gegenueber Buy&Hold (1930-2026) unter 10 Prozentpunkte liegt ODER der Sharpe unter dem Konstant-Mix mit gleicher mittlerer Exposure liegt (dann misst die Strategie nur die Investitionsquote).
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.45-0.60 (Harvey 0.40 -> 0.48-0.51 mit ex-post-Skalierung; Cederburg 0.42 -> 0.51 mit p = 0.30; ohne Hebel erwartet Sharpe ca. gleich B&H, Vorteil Drawdown)
- **Hinweis deutsche Privatanleger:** Gut umsetzbar ohne Hebel: UCITS-S&P-500/MSCI-World-ETF plus Geldmarkt-ETF, Anpassungen nur bei 5-pp-Abweichung. Steuerlich viele kleine Verkaeufe; Vorabpauschale und Teilfreistellung im zentralen Steuermodul.
- **Quellen:**
  - Harvey, Hoyle, Korgaonkar, Rattray, Sargaison, Van Hemert 2018, The Impact of Volatility Targeting, https://people.duke.edu/~charvey/Research/Published_Papers/P135_The_impact_of.pdf
  - Cederburg, O'Doherty, Wang, Yan 2020, On the performance of volatility-managed portfolios, https://www.lehigh.edu/~xuy219/research/COWY.pdf

### 10. Statische Multi-Faktor-Kombination (HML, RMW, CMA, Mom) mit Inverse-Vol-Gewichten auf French-Faktoren

- **ID:** `static_multifactor_equal_risk` | **Familie:** factors
- **Mechanismus:** Mehrere schwach korrelierte Aktien-Praemien (Value, Profitabilitaet, Investition, Momentum) diversifizieren sich; Inverse-Vol verhindert, dass der volatilste Faktor dominiert. Deckt Value-, Quality- und Investitions-Quellen ab, die einzeln als verworfene Kandidaten (gp_quality, qmj, us_value) auftauchten.
- **Spezifikation (feste Parameter):** Monatsdaten Ken French: F-F_Research_Data_5_Factors_2x3 (HML, RMW, CMA; ab 1963-07) und F-F_Momentum_Factor (Mom). Am Monatsende t: vol_i = std(f_i, Monate t-35..t)*sqrt(12), min. 24 Beobachtungen; w_i = (1/vol_i)/sum(1/vol_k); port_vol = sqrt(w'Cov36M w)*sqrt(12); lev = min(2.0, 0.10/port_vol). Rendite Monat t+1: R = lev*sum(w_i*f_i,t+1) - 2 %/12 Haircut (Kosten-/Verfallspauschale) - (lev>1 ? (lev-1)*(RF + 0.005/12) : 0). Gewichte gelten den Folgemonat, Signal nur aus Daten bis t. Start 1966-07 (36 Monate).
- **Ticker:** French:HML, French:RMW, French:CMA, French:Mom, French:RF
- **Datenstart:** 1963-07 (Test ab 1966-07)
- **Rebalancing:** monatlich
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - Haircut 0 % (brutto)
  - Haircut 4 %
  - 1/N-Gewichte ohne Vol-Gewichtung
- **Abbruchkriterium:** Verwerfen, wenn der Netto-Sharpe (2 % Haircut) 2008-2026 < 0.20 oder die t-Statistik der Mittelrendite < 1.65 ist; ausserdem Vergleich mit 1/N der Faktoren und Mkt-RF bei gleicher Ziel-Vol.
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.20-0.45 (brutto 1963-2026 ca. 0.4-0.7 zu erwarten; McLean-Pontiff -58 % nach Publikation, RMW/CMA nur eine Stichprobe ab 1963)
- **Hinweis deutsche Privatanleger:** Nicht direkt handelbar (Long-Short-Faktoren). Umsetzung nur indirekt mit long-only Faktor-ETFs (UCITS: iShares Edge MSCI World Value/Quality/Momentum/Min-Vol), die den Faktor kaum rein abbilden; hier Forschungs-Bewertung der Praemien.
- **Quellen:**
  - Jensen, Kelly, Pedersen 2023, Is There a Replication Crisis in Finance?, https://www.nber.org/papers/w28432
  - Hou, Xue, Zhang 2020, Replicating Anomalies, https://www.nber.org/papers/w23394

### 11. Low-Volatility Long-only (defensiv): French-Beta-Quintil, USMV/SPLV, Sektor-Proxy

- **ID:** `lowvol_defensive_longonly` | **Familie:** lowrisk
- **Mechanismus:** Low-Risk-Anomalie: Anleger mit Hebelrestriktionen und Lotterie-Praeferenz ueberzahlen risikoreiche Aktien; Aktien mit niedrigem Beta/Vol liefern vergleichbare Rendite bei weniger Risiko (Blitz/van Vliet, Baker/Bradley/Wurgler).
- **Spezifikation (feste Parameter):** Hauptlauf (Faktor-Ebene, lange Historie): Ken French Portfolios_Formed_on_BETA (wertgewichtet), Long-only niedrigstes Quintil minus RF gegen Mkt-RF; Stichprobe geteilt bei 2007/2008. Realitaets-Check ETF: 100 % USMV (und SPLV) Buy&Hold gegen SPY ab Auflage (kaufen zur Eroeffnung des ersten Handelstags), nach Abgeltungsteuer. Kein Signal, keine Optimierung. Sektor-Proxy (siehe Variante B) wird nur als vorregistrierte Variante gerechnet.
- **Ticker:** USMV, SPLV, SPY, French:Portfolios_Formed_on_BETA, XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY
- **Datenstart:** French ab 1963-07; ETFs ab 2011-05-05/2011-10-20; Sektor-Proxy Signale ab ca. 2001
- **Rebalancing:** Buy&Hold (ETF); French-Dateien monatlich; Sektor-Proxy monatlich
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - B: Sektor-Proxy: 3 SPDR-Sektoren mit kleinster Std der woechentlichen Renditen (156 Wochen), monatlich, Eroeffnung t+1
  - Faktor-Ebene mit Portfolios_Formed_on_VAR statt BETA
  - SPLV statt USMV
- **Abbruchkriterium:** Verwerfen, wenn die Sharpe-Differenz zu SPY ab 2011 (ETFs) <= 0 ist UND der MaxDD nicht mindestens 5 Prozentpunkte besser ausfaellt; auf Faktor-Ebene verwerfen, wenn der Alpha-t-Wert nach 2008 < 1.65 ist.
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.45-0.70 (Quantpedia long-only-Dezil 0.72 1986-2006 brutto; eigener ETF-Check: USMV 0.90 vs SPY 0.94 seit 2011 - Sharpe ca. gleich SPY)
- **Hinweis deutsche Privatanleger:** UCITS-Min-Vol-ETFs existieren (iShares Edge MSCI World/USA Min Vol), ab ca. 2012-2014; sehr gut handelbar. Erwartung: weniger Vol, aber auch weniger Rendite als der Gesamtmarkt in Bullenphasen.
- **Quellen:**
  - Blitz, van Vliet 2007, The Volatility Effect: Lower Risk Without Lower Return, https://papers.ssrn.com/abstract=980865
  - Baker, Bradley, Wurgler 2011, Benchmarks as Limits to Arbitrage: Understanding the Low-Volatility Anomaly, https://papers.ssrn.com/abstract=1745108

### 12. G10-Waehrungs-Carry mit Rang-Gewichten

- **ID:** `fx_carry_g10_rank` | **Familie:** valuecarry
- **Mechanismus:** Carry-Praemie: Hochzins-Waehrungen werten im Mittel nicht in dem Masse ab, wie die Zinsdifferenz es nach ungedeckter Zinsparitaet verlangt (Forward-Premium-Puzzle); die Praemie kompensiert Crash-Risiko in Liquiditaetskrisen (Daniel/Hodrick/Lu, Lustig/Roussanov/Verdelhan). Unabhaengige Quelle von Aktien/Trend.
- **Spezifikation (feste Parameter):** Universum USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD, NOK, SEK (N = 10). Am Monatsende t: C_i = r3m_i(t) - r3m_USD(t) (3M-Interbankzinsen, FRED OECD IR3TIB01xxM156N, Monatsmittel). Variante A (Hauptlauf): w = rankweights(C) ueber alle 10 inkl. USD: w_i = z*(rank_i - 5.5), Summe long +1, short -1; USD-FX-Rendite 0. Rendite t+1d bis t'+1d: R = sum W_i*(S_i(t'+1d)/S_i(t+1d) - 1 + (r_i(t) - r_USD(t))/12) mit S = USD je Fremdwaehrung (FRED H.10 oder Yahoo). Handel zum Schlusskurs t+1d, monatlich. Kosten 3 bp je Wechsel (Stress 10 bp). Zinsdifferenz ersetzt Forward-Punkte, Basis ignoriert.
- **Ticker:** EURUSD=X, GBPUSD=X, JPY=X, CHF=X, CAD=X, AUDUSD=X, NZDUSD=X, NOK=X, SEK=X, FRED:IR3TIB01xxM156N, FRED:DEXxxxx
- **Datenstart:** ca. 1999 (EUR) bzw. 1996-2003 (Yahoo); FRED teils ab 1971
- **Rebalancing:** monatlich
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - VIX-Filter: Gewicht 0.5, wenn ^VIX > 80. Perzentil seiner letzten 60 Monatsendwerte
  - Dollar-Carry: long alle 9 Fremdwaehrungen/short USD, wenn Durchschnitts-Carry > 0, sonst umgekehrt
  - CurrencyShares-ETFs (FXE, FXY, FXB, FXA, FXC, FXF) statt Spot+Zins
- **Abbruchkriterium:** Verwerfen, wenn der Netto-Sharpe 2009-2026 < 0.20 ist oder die FRED-Zinsreihen nicht bis 2026 aktuell abrufbar sind (Datenabbruch gilt als Abbruch).
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.10-0.35 (2L/2S-Langfristwert 1975-2015 ca. 0.47 brutto; Rueckgang nach 2008 durch Zinskompression)
- **Hinweis deutsche Privatanleger:** Retail-Umsetzung nur ueber Devisen-CFDs/Forex mit Swaps oder Futures; keine UCITS-ETFs fuer Carry. Verlustverrechnungsbeschraenkungen fuer Termingeschaefte pruefen. Primaer Forschungsbaustein fuer die Renditequelle Carry.
- **Quellen:**
  - Daniel, Hodrick, Lu 2017, The Carry Trade: Risks and Drawdowns, https://www.nber.org/papers/w20433
  - Lustig, Roussanov, Verdelhan 2011, Common Risk Factors in Currency Markets, https://papers.ssrn.com/abstract=1159046

### 13. Laender-Value: billigstes Drittel nach Preis zu 10-Jahres-Durchschnitt (Faber-CAPE-Proxy)

- **ID:** `country_value_cape_faber_proxy` | **Familie:** valuecarry
- **Mechanismus:** Value auf Laenderebene: langfristig fallende Preise bedeuten niedrigere Bewertung und hoehere erwartete Rendite (Mean Reversion, Asness/Moskowitz/Pedersen). Einzige Value-Quelle auf Querschnittsebene mit Gratis-Daten.
- **Spezifikation (feste Parameter):** Universum 14 ETFs: SPY, EWC, EWU, EWG, EWQ, EWI, EWP, EWN, EWL, EWD, EWJ, EWA, EWH, EWS. Am letzten Handelstag im Dezember t: Kandidaten = ETFs mit >= 120 Monaten Historie; RP_i = P_i(t)/mean(P_i ueber die letzten 120 Monatsendwerte bis t) mit P = AdjClose (USD). Waehle die floor(N/3) Laender mit kleinstem RP_i, gleichgewichtet, long-only, kein Cash-Filter. Kauf zum Schlusskurs t+1d, halten 12 Monate. Benchmark: gleichgewichteter Korb aller Kandidaten, jaehrlich rebalanciert; Bewertung nur als Excess gegen diesen Benchmark. Kosten 10 bp je Seite. Erste Entscheidung 12/2006.
- **Ticker:** SPY, EWC, EWU, EWG, EWQ, EWI, EWP, EWN, EWL, EWD, EWJ, EWA, EWH, EWS
- **Datenstart:** 1996-03 (erste Entscheidung 2006-12)
- **Rebalancing:** jaehrlich (Dezember)
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - Billigstes Viertel statt Drittel
  - 60-Monats-Durchschnitt statt 120 (AMP-Reversal-Proxy)
  - Rebalancing im Juni statt Dezember (Timing-Luck-Test)
- **Abbruchkriterium:** Verwerfen, wenn der Excess gegenueber dem Gleichgewichts-Korb nach Kosten < +1 % p.a. ist oder |t| < 1. Statistische Aussagekraft ist mit ca. 19 Jahresentscheidungen ohnehin schwach und wird im Bericht so ausgewiesen.
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.30-0.50 (Sharpe ca. wie Benchmark; Faber 0.56 In-Sample 1980-2011; GVAL-Produkt hinkte hinterher; Excess erwartet 0 bis +2 % p.a.)
- **Hinweis deutsche Privatanleger:** Jaehrliches Rebalancing ist steuerlich guenstig; UCITS-Laender-ETFs (iShares MSCI Japan, UK, Germany ...) existieren. Gut umsetzbar, aber Aussagekraft des Tests ist gering.
- **Quellen:**
  - Faber 2012, Global Value: Building Trading Models with the 10 Year CAPE (Quantpedia-Zusammenfassung), https://quantpedia.com/strategies/value-factor-effect-within-countries
  - Asness 2012, An Old Friend: The Stock Market's Shiller P/E, https://www.aqr.com/library/aqr-publications/an-old-friend-the-stock-markets-shiller-pe

### 14. VIX-getorte Tages-Umkehr auf Sektor-ETFs (Nagel, Industrie-Variante)

- **ID:** `nagel_vix_gated_sector_etf_reversal` | **Familie:** reversal
- **Mechanismus:** Liquiditaetsbereitstellung: Umkehrrenditen entschaedigen Marktteilnehmer, die in Phasen hoher Vol Liquiditaet liefern (Nagel 2012). Der VIX ist ein Proxy fuer die Knappheit von Marktliquiditaet. Test der Idee auf survivorship-freien ETFs.
- **Spezifikation (feste Parameter):** Universum XLB XLE XLF XLI XLK XLP XLU XLV XLY (auto_adjust, ab 1998-12). Tag d: r_i,d = Tagesrendite, m_d = Mittel der r, x_i,d = r_i,d - m_d, w_i(d) = -x_i,d/(0.5*sum|x_k,d|) (dollar-neutral, Long +1, Short -1). Overlay aus 5 Teilstrategien: Zielgewicht fuer Close(t+1)->Close(t+2) = (1/5)*sum_{j=0..4} w_i(t-j). Gate g_t = 1 wenn ^VIX-Schluss(t) > Median(^VIX-Schluss(t-251..t)), sonst 0. Ausfuehrung Schlusskurs t+1 (eine Tagesverzoegerung mehr als Nagel). Taegliches Rebalancing. Kosten 3 bp je Seite (Stress 1/5 bp).
- **Ticker:** XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY, ^VIX
- **Datenstart:** 1998-12-22
- **Rebalancing:** taeglich
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - feste VIX-Schwelle 20
  - feste VIX-Schwelle 25 (und 30 getrennt berichten, keine Auswahl)
  - Beta-Hedge mit SPY
- **Abbruchkriterium:** Verwerfen, wenn der Netto-Sharpe (3 bp) bei allen drei festen Schwellen 20/25/30 UND beim Median-Gate <= 0.20 ist; gilt zugleich als Beleg, dass der Tagesumkehr-Effekt mit t+1-Ausfuehrung verschwunden ist.
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.0-0.30 (Nagel Industrien 0.56 brutto 1998-2010; mit Tagesverzoegerung, Kosten und Verfall nach 2010 wahrscheinlich nahe 0)
- **Hinweis deutsche Privatanleger:** Nicht umsetzbar (taegliche Long-Short-Positionen, Shorts nur ueber CFDs). Forschungsbaustein und Null-Hypothese fuer kurzfristige Umkehr.
- **Quellen:**
  - Nagel 2012, Evaporating Liquidity, https://www.nber.org/papers/w17653

### 15. Index-ETF-Kurzfrist-Umkehr long-only (IBS-Kern, Connors-RSI(2) als Variante)

- **ID:** `index_etf_ibs_rsi2_longonly` | **Familie:** reversal
- **Mechanismus:** Kurzfristige Ueberreaktion: Ein Schluss nahe dem Tagestief in einem Aufwaertstrend wird im Mittel kurzfristig korrigiert (Liquiditaetsbereitstellung nach Nagel, nicht belegt fuer Index-ETFs). Praktiker-Idee, deshalb strikt vorregistriert.
- **Spezifikation (feste Parameter):** Instrumente einzeln getestet (nicht poolen): SPY (ab 1993), QQQ (1999), IWM (2000), auto_adjust OHLC. IBS_t = (Close_t - Low_t)/(High_t - Low_t); bei High==Low kein Signal. Einstieg, wenn keine Position UND Close_t > SMA200(Close)_t UND IBS_t < 0.20: Kauf zum Schlusskurs t+1. Ausstieg am ersten Tag u > Einstieg mit IBS_u > 0.70 ODER Haltedauer >= 5 Handelstage: Verkauf zum Schlusskurs u+1. Nur long, 100 % Eigenkapital je Trade, sonst Cash (^IRX), kein Hebel, kein Stop. Kosten 2 bp je Seite (Stress 5 bp) plus Steuermodul. Hypothese und Abbruchkriterium vor dem Backtest registrieren.
- **Ticker:** SPY, QQQ, IWM, ^IRX
- **Datenstart:** SPY 1993-01-29; QQQ 1999-03; IWM 2000-05
- **Rebalancing:** taeglich (Signale), Haltedauer 1-5 Tage
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - Connors RSI(2): Einstieg Close > SMA200 und Wilder-RSI(2) < 10, Ausstieg Close > SMA5
  - Ausfuehrung Eroeffnung t+1
  - ohne SMA200-Filter
- **Abbruchkriterium:** Verwerfen, wenn die Rendite pro Exposure-Tag 2010-2026 nicht signifikant (p > 0.10) ueber exposure-gematchten Zufalleinstiegen liegt oder der Netto-Sharpe nach Steuer unter Buy&Hold bleibt.
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.30-0.60 bei nur ca. 20-35 % Marktquote (Rendite unbekannt, keine Peer-Review-Evidenz; Ausfuehrung t+1 statt Signal-Schluss verkleinert den Edge)
- **Hinweis deutsche Privatanleger:** UCITS-S&P-500-ETF (z.B. CSPX/SXR8) mit High/Low-Daten verfuegbar; viele kurze Trades bedeuten Spread und Abgeltungsteuer ohne Stundung; Handel nur bei sehr niedrigen Kosten.
- **Quellen:**
  - Nagel 2012, Evaporating Liquidity, https://www.nber.org/papers/w17653
  - Quantified Strategies, The classical mean reversion strategy (Praktiker-Blog, kein Peer Review), https://quantifiedstrategies.substack.com/p/the-classical-mean-reversion-strategy

### 16. GGR-Distanz-Paare (12/6 Monate) mit Sektor- und Zero-Crossing-Filter (Null-/Negativkontrolle)

- **ID:** `ggr_distance_sector_zerocross` | **Familie:** pairs
- **Mechanismus:** Relative-Value: Aktien mit gemeinsamen Fundamentaldaten laufen auseinander und konvergieren wieder (temporaere Liquiditaets-Preisdruecke). Dokumentierter Verfall seit 2002 - Rolle im Lab: Kontrolle, dass unsere Pipeline keinen Schein-Edge produziert.
- **Spezifikation (feste Parameter):** Zyklus: Formation 252 Handelstage, Handel 126 Tage, Neuauswahl alle 126 Tage. Total-Return-Index (AdjClose), am ersten Formationstag auf 1 normiert; nur Paare im selben GICS-Sektor, Share-Class-Duplikate raus. SSD = sum (P_i - P_j)^2 ueber Formation. Baseline GGR: die 20 Paare mit kleinster SSD (laeuft immer mit). Filter-Variante: N = Zahl der Vorzeichenwechsel des Spreads in der Formation; Rangsumme = Rang_SSD (aufsteigend) + Rang_N (absteigend); die 20 Paare mit kleinster Rangsumme. Im Handelsfenster Preisindex am ersten Tag auf 1 renormiert; sigma = Std des Spreads in der Formation. Eroeffnen bei |Spread| > 2*sigma am Schluss t (gleiche Dollarbetraege), Ausfuehrung Eroeffnung t+1; schliessen bei Nulldurchgang oder Fensterende. Kapital = Eigenkapital/20 je Paar. Kosten 5 bp (Basis) bzw. 26-35 bp (streng) je Halbumschlag und Bein, Leihgebuehr 0.6 % p.a.
- **Ticker:** S&P-500-Konstituenten heute (Wikipedia-Liste, yfinance Tagesdaten)
- **Datenstart:** ca. 1990 (je Aktie)
- **Rebalancing:** Paarbildung halbjaehrlich, Signal taeglich
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - Zero-Crossing-Filter (Rangsumme) statt reiner SSD
  - Kosten streng 26-35 bp
  - rohe Preise statt renormiertem Index im Handelsfenster (Clegg/Krauss-Variante)
- **Abbruchkriterium:** Verwerfen, wenn der Netto-Sharpe mit strengen Kosten 2010-2026 <= 0 ist (erwartet); gilt dann als bestaetigter Verfall, die Strategie wird nicht weiterverfolgt.
- **Erwartete Sharpe nach Nachpublikations-Verfall:** -0.3 bis +0.2 (Clegg/Krauss survivorship-frei: netto Sharpe -0.55 fuer 1990-2015; GGR-Original 1.22 brutto 1962-2002; Survivorship-Bias der Gratisliste macht unser Ergebnis zur Obergrenze)
- **Hinweis deutsche Privatanleger:** Nicht umsetzbar (Short-Beine nur ueber CFDs, hoher Umschlag). Rein als Null-Kontrolle fuer das Lab.
- **Quellen:**
  - Do, Faff 2010, Does simple pairs trading still work?, https://research.bond.edu.au/en/publications/does-simple-pairs-trading-still-work/
  - Quantpedia, Pairs Trading with Stocks (Zusammenfassung Gatev/Goetzmann/Rouwenhorst), https://quantpedia.com/strategies/pairs-trading-with-stocks

### 17. Turn of the Month: Aktienmarkt Handelstage -1 bis +3, sonst Cash

- **ID:** `tom_spy_m2_p3` | **Familie:** calendar
- **Mechanismus:** Institutionelle Kapitalfluesse (Gehaltszahlungen, Pensionsfonds) zum Monatswechsel schaffen temporaeren Nachfragedruck; Befund ueber fast 100 Jahre (McConnell/Xu). Nutzt nur ca. 19 % der Handelstage.
- **Spezifikation (feste Parameter):** Kalender: NYSE-Handelstage. Fuer jeden Monat M: d(-2) = vorletzter, d(-1) = letzter Handelstag von M, d(+3) = dritter Handelstag von M+1. Position: Long 100 % Aktienmarkt von Close(d(-2)) bis Close(d(+3)) (Tagesrenditen der Tage -1, +1, +2, +3), sonst 100 % Cash (RF/SHY). Kalender im Voraus bekannt, daher keine Look-ahead-Gefahr (MOC-Order). Rendite Backtest: French Mkt = Mkt-RF + RF (taeglich, ab 1926), Live-Proxy SPY. Kosten 2 bp je Seite (Stress 1/5 bp). Fenster-Zuordnung vor dem Codieren am McConnell/Xu-Original abgleichen.
- **Ticker:** SPY, ^GSPC, French:Mkt-RF, French:RF, SHY, BIL
- **Datenstart:** French 1926-07; SPY 1993-01-29; OOS ab 2006
- **Rebalancing:** monatlich (12 Round-Trips pro Jahr)
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - nur Tag +1 (ETF-Era-Befund)
  - konservative Ausfuehrung: Entry Open(d(-1)), Exit Open(d(+4))
  - Kosten 5 bp je Seite
- **Abbruchkriterium:** Verwerfen, wenn die Rendite pro Exposure-Tag 2006-2026 nach Kosten nicht signifikant (t < 2 bzw. p > 0.10 gegen 10000 exposure-gematchte Zufalls-4-Tage-Fenster) ist.
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.30-0.60 (Paper 1.04 bei 19 % Exposure 1926-2005; ETF-Aera-Befunde: Effekt nur noch am Tag +1; absolute Rendite klein)
- **Hinweis deutsche Privatanleger:** Umsetzbar mit UCITS-S&P-500-ETF und Geldmarkt-ETF, aber 12 Realisierungen pro Jahr ohne Steuerstundung; Spread ca. 0.3-0.5 % p.a. (Schaetzung). Eher Risikoreduktion als Alpha.
- **Quellen:**
  - McConnell, Xu 2008, Equity Returns at the Turn of the Month, https://ideas.repec.org/a/taf/ufajxx/v64y2008i2p49-64.html
  - Maberly, Waggoner 2000, Turn-of-the-month effect in S&P 500 futures / cash, https://ideas.repec.org/p/fip/fedawp/2000-11.html

### 18. Halloween-Indikator / Sell in May: Aktien Nov-Apr, Cash Mai-Okt

- **ID:** `halloween_nov_apr_equity` | **Familie:** calendar
- **Mechanismus:** Saisonale Risikopraemie bzw. Urlaubs-/Liquiditaetseffekt: In den Sommermonaten waere die Praemie im Mittel niedriger. Mechanismus umstritten; wird im Lab auch gegen die SAD-Idee (Stimmung/Tageslaenge) und exposure-gematchte Zufalls-6-Monats-Fenster getestet.
- **Spezifikation (feste Parameter):** Jedes Jahr Y: Entry am Close des letzten Handelstags im Oktober -> 100 % Aktienmarkt; Exit am Close des letzten Handelstags im April (Y+1) -> 100 % Cash (RF/^IRX) bis zum naechsten Oktober. Rendite: French Mkt (ab 1926) bzw. SPY (ab 1993), Cash French RF. Order MOC (Kalender im Voraus bekannt). Kosten 2 bp je Seite (Stress 1/5 bp). Pflichtvergleiche: Buy&Hold, konstanter 50/50-Mix, Rang des Nov-Apr-Fensters unter allen 12 moeglichen 6-Monats-Startmonaten (Mining-Check). Ehrliches OOS = 11/1998 bis heute.
- **Ticker:** SPY, ^GSPC, French:Mkt-RF, French:RF, ^GDAXI, EFA, ^IRX
- **Datenstart:** French 1926-07; SPY 1993-01-29
- **Rebalancing:** jaehrlich (2 Wechsel pro Jahr)
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - Cash durch IEF ersetzt
  - Ausfuehrung Eroeffnung des Folgetags
  - Internationale Replikation (^GDAXI, EFA)
- **Abbruchkriterium:** Verwerfen, wenn 1999-2026 netto der Sharpe nicht ueber dem 50/50-Mix gleicher mittlerer Exposure liegt ODER das Nov-Apr-Fenster nicht unter den besten 3 der 12 Startmonate rangiert.
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.35-0.55 (ca. Buy&Hold-Niveau bei halber Exposure; Dow 1915-2012: Sharpe 0.275 vs 0.279 laut Blog)
- **Hinweis deutsche Privatanleger:** Sehr gut umsetzbar (UCITS-ETF plus Geldmarkt), nur zwei Wechsel pro Jahr, steuerlich ueberschaubar.
- **Quellen:**
  - Bouman, Jacobsen 2002, The Halloween Indicator, Sell in May and Go Away: Another Puzzle, https://pure.eur.nl/en/publications/the-halloween-indicator-sell-in-may-and-go-away-another-puzzle/
  - Zhang, Jacobsen 2012, The Halloween Indicator: Everywhere and All the Time, https://research.nottingham.edu.cn/en/publications/the-halloween-indicator-sell-in-may-and-go-away-everywhere-and-al/fingerprints/

### 19. Inverse-Volatilitaets-Risk-Parity, ungehebelt (U9-Multi-Asset-ETFs)

- **ID:** `ivp_risk_parity_unlevered` | **Familie:** riskparity
- **Mechanismus:** Risikoparitaet: Wenn Anleger Hebel meiden, sind risikoarme Anlagen (Anleihen) relativ zu teuer; Gleichgewichtung des Risikos statt des Kapitals diversifiziert besser (Asness/Frazzini/Pedersen). Ersetzt ERC/HRP/MinVar als Familienvertreter; diese werden als Varianten gerechnet.
- **Spezifikation (feste Parameter):** Universum U9 = VTI, EFA, EEM, VNQ, IEF, TLT, TIP, GLD, DBC (auto_adjust). Am letzten Handelstag t jedes Monats: sigma_i = Std der Tagesrenditen der letzten 756 Handelstage bis t * sqrt(252), mindestens 504 Beobachtungen. w_i = (1/sigma_i)/sum_j(1/sigma_j). Ausfuehrung zur Eroeffnung t+1, Halten bis zum naechsten Monatsultimo, Gewichte driften. Kein Hebel. Kosten 5 bp je Seite (Stress 15 bp). Erstes Signal ca. 2008-02. Die 1/N-Variante von U9 laeuft als zusaetzliche Kontrolle mit.
- **Ticker:** VTI, EFA, EEM, VNQ, IEF, TLT, TIP, GLD, DBC
- **Datenstart:** U9 ab 2006-02-06, erstes Signal ca. 2008-02
- **Rebalancing:** monatlich
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - ERC mit Ledoit-Wolf-geschrumpfter Korrelation (Bruder/Roncalli)
  - Hierarchical Risk Parity (Lopez de Prado), 252-Tage-Fenster
  - Schaetzfenster 252 Tage statt 756
- **Abbruchkriterium:** Verwerfen, wenn der Netto-Sharpe nicht um mindestens 0.10 ueber dem 1/N-Korb U9 liegt UND der MaxDD in 2022 nicht besser ist als bei 1/N.
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.30-0.50 (AFP: 0.52 US 1926-2010 in Anleihen-Hausse; 2022 wirkt Aktien-Anleihen-Korrelationswechsel negativ: IEF -15 %, TLT -31 %)
- **Hinweis deutsche Privatanleger:** Gut umsetzbar mit UCITS-ETFs (MSCI World/EM, Staatsanleihen, Gold-ETC, Rohstoff, Immobilien); monatliches Rebalancing, niedriger Umschlag. Anleihenlastig: Zinsrisiko, keine Hebelung.
- **Quellen:**
  - Asness, Frazzini, Pedersen 2012, Leverage Aversion and Risk Parity, https://www.aqr.com/Insights/Research/Journal-Article/Leverage-Aversion-and-Risk-Parity
  - Anderson, Bianchi, Goldberg 2012, Will My Risk Parity Strategy Outperform?, https://rpc.cfainstitute.org/research/financial-analysts-journal/2012/will-my-risk-parity-strategy-outperform
  - Bruder, Roncalli 2012, Managing Risk Exposures using the Risk Budgeting Approach, https://mpra.ub.uni-muenchen.de/37246/

### 20. Cash-gedeckter ATM-Put-Verkauf auf den S&P 500 (Cboe PutWrite Index ^PUT)

- **ID:** `putwrite_vrp_index` | **Familie:** volpremium
- **Mechanismus:** Varianzrisikopraemie: Optionskaeufer zahlen eine Praemie fuer Absicherung (implizite Vol > realisierte Vol); der Stillhalter erhaelt sie und traegt Crash-Risiko. Ein Teil der Rendite ist Aktienbeta (0.56), nur ein Rest ist VRP-Alpha.
- **Spezifikation (feste Parameter):** Index-Ebene, kein Signal: 100 % ^PUT (Yahoo, ab 1996-08-02), Rendite = ^PUT-Tagesrendite, Cash French RF. Kostenabzug 0.50 Prozentpunkte p.a. (Lab-Annahme, Index ist brutto). Pflichtvergleiche: SPY Buy&Hold; beta-gematchter Mix aus SPY und Cash (Beta aus expandierender OLS der Monats-Exzessrenditen ^PUT auf SPY, mind. 36 Monate) - trennt VRP-Alpha von Aktienbeta; Teilperioden 1996-2007, 2008-2019, 2020-2026. Real nur ueber Selbst-Roll von SPX/XSP-Puts, mit Gratis-Daten nicht backtestbar -> Index ist die Obergrenze.
- **Ticker:** ^PUT, SPY, French:RF
- **Datenstart:** ^PUT ab 1996-08-02
- **Rebalancing:** kein Signal (Index rollt monatlich)
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - Kosten 0.25 pp p.a.
  - Kosten 1.00 pp p.a.
  - Teilstichprobe ab 2008 getrennt ausgewertet (Entscheidungsrelevanz)
- **Abbruchkriterium:** Verwerfen als Alpha-Quelle, wenn das Alpha gegen den beta-gematchten SPY/Cash-Mix nach 0.50 pp Kosten einen t-Wert < 1.65 hat; dann nur als Aktien-Beta mit Tail-Risiko eingestuft.
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.40-0.65 (Cboe/Bondarenko: bessere Sharpe als S&P 500, gesponsert, brutto, Schiefe -2.09; beta-bereinigtes Alpha klein)
- **Hinweis deutsche Privatanleger:** ^PUT ist nicht kaufbar. Selbst-Roll von SPX/XSP-Puts bei deutschen Brokern moeglich (Optionshandel, Margin); steuerlich Stillhalter-Praemien und Verlustverrechnung (Termingeschaefte) pruefen. UCITS-PutWrite-ETFs nicht geprueft.
- **Quellen:**
  - Bondarenko 2019, Historical Performance of Put-Writing Strategies (Cboe), https://www.cboe.com/insights/posts/white-paper-shows-volatility-risk-premium-facilitated-higher-risk-adjusted-returns-for-put-index/
  - Carr, Wu 2009, Variance Risk Premia, https://ideas.repec.org/a/oup/rfinst/v22y2009i3p1311-1341..html

### 21. SVXY nur bei VIX-Contango (VIX/VIX3M < 1), sonst Cash (mit SPY-Sekundaertest)

- **ID:** `svxy_term_structure_filter` | **Familie:** volpremium
- **Mechanismus:** VIX-Futures-Roll-Rendite: In Contango gewinnt eine Short-Vol-Position durch Roll-Down; in Backwardation (Stress) wechselt das Signal nach Cash. Kreative Hochrisiko-Idee mit Ruin-Risiko, deshalb mit harter Gewichtsgrenze.
- **Spezifikation (feste Parameter):** ratio_t = ^VIX_t/^VIX3M_t; ON_t = ratio_t < 1.00 (nicht optimieren). Order nach Schluss t, Fill Eroeffnung t+1. Tagesrendite t+1: ON_t und ON_t-1: SVXY Close/Close; ON_t und nicht ON_t-1: Einstieg Open t+1, Rendite Close_t+1/Open_t+1 - 1; nicht ON_t und ON_t-1: Ausstieg Open t+1; sonst Cash (^IRX). Hauptlauf W = 1.00 (wie CXO); Kosten 0.20 % je Wechsel (Stress 0.10/0.40 %). SVXY -1x bis 2018-02-27, ab 2018-02-28 -0.5x: Statistiken getrennt ausweisen. Sekundaertest: ON_t steuert SPY statt SVXY (Daten ab 2006-07-17).
- **Ticker:** SVXY, ^VIX, ^VIX3M, SPY, ^IRX
- **Datenstart:** SVXY 2011-10-04; ^VIX3M 2006-07-17
- **Rebalancing:** taeglich pruefen (CXO: 123 Wechsel 2011-10 bis 2019-12)
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - W = 0.25 (Portfolio-Baustein, Rest Cash)
  - Fill zum Schlusskurs t+1 statt Eroeffnung t+1
  - SPY-Sekundaertest (ON: SPY, sonst Cash) ab 2006-07
- **Abbruchkriterium:** Verwerfen, wenn bei W=1 und t+1-Fill der MaxDD schlechter als -60 % ist oder ein Einzeltagesverlust > 40 % auftritt (Stresstage 2018-02-05/06, 2020-03, 2024-08-05); Echtgeld nie ueber 12 % Portfolioanteil bei -1x bzw. 25 % bei -0.5x.
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.30-0.70 mit extremer Unsicherheit (CXO 38 % CAGR vs 14.7 % B&H 2011-2019 in-sample; nur vier unabhaengige Vol-Regime; Fill-Verzoegerung drueckt)
- **Hinweis deutsche Privatanleger:** SVXY (US-ETP) ist bei EU-Brokern wegen PRIIPs/KID oft nicht handelbar. Gap-Risiko (-83 % am 2018-02-06): Totalverlust-Szenario; nur als Forschungsbaustein bzw. mit Kleinstanteil.
- **Quellen:**
  - CXO Advisory 2020, Exploiting VIX Futures Roll Return with ETNs, https://www.cxoadvisory.com/volatility-effects/exploiting-vix-futures-roll-return-with-etns/
  - Cheng 2019, The VIX Premium, https://ideas.repec.org/a/oup/rfinst/v32y2019i1p180-227..html

### 22. Dreier-Komposit Duration-Timing (Carry + Trend + Value), long-only 10J-Treasury gegen Cash

- **ID:** `bond_composite_3sig_longonly` | **Familie:** gap_bonds_duration_curve_carry_mom_value
- **Mechanismus:** Stil-Praemien in der Duration: Terminspread (Carry), Trend der Ueberschussrendite (Momentum) und Realzins gegen Anker (Value) sagen Anleiherenditen im Mittel vorher. Einziger Bond-Baustein der Liste; liefert Verlustbegrenzung bei Zinsanstieg (2022: -4.2 % statt -17.0 % im Check).
- **Spezifikation (feste Parameter):** Synthetische 10J-Par-Anleihe aus ^TNX/^IRX: y10 = ^TNX/100, y3m = ^IRX/100; D(y) = (1-(1+y/2)^-20)/y; R10_t = y10_{t-1}/252 - D(y10_{t-1})*(y10_t - y10_{t-1}); Rc_t = y3m_{t-1}/252. Signale am Monatsende t_m: (1) Carry: s = y10 - y3m; v_car = 1 wenn Anteil der 2520 Vortagswerte unter s_{t_m} > 1/3. (2) Trend: v_trd = 1 wenn EWMA(span 21) und EWMA(span 252) der Ueberschussrendite ln(1+R10)-ln(1+Rc) beide > 0. (3) Value: infl = CPIAUCNS 12-Monats-Veraenderung, pi_e = Mittel der 36 Monatswerte bis m-2; real = y10 - pi_e; v_val = 1 wenn real > EWMA-Anker (Halbwertszeit 36 Monate). w = (v_car+v_trd+v_val)/3, Rest Cash. Signal Schluss t_m, Handel Schluss t_m+1, ungehebelt, nie short. Kosten 5 bp (Stress 20 bp). Start ca. 1972; ETF-Test IEF/SHY ab 2002-07.
- **Ticker:** ^TNX, ^IRX, FRED:CPIAUCNS, IEF, SHY, BIL, TLT
- **Datenstart:** ^TNX 1962-01-02, ^IRX 1960-01-04; ETFs 2002-07
- **Rebalancing:** monatlich
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - nur Carry-Gate (Terminspread im oberen Zwei-Drittel-Perzentil)
  - nur Trend (Dual-EWMA 21/252)
  - nur Value (Realzins ueber Anker)
- **Abbruchkriterium:** Verwerfen des Timing-Anspruchs, wenn der Sharpe des Komposits nicht ueber dem statischen Portfolio mit konstantem Gewicht = mittlere Quote liegt (Block-Bootstrap p > 0.20); dann bleibt nur Investitionsquote-Effekt.
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.25-0.45 (eigener Check mit Equity-Hedge statt Value 0.40 vs 0.19 B&H 1972-2026; ab 2018-11 -0.03 vs -0.26; Teil ist Investitionsquote)
- **Hinweis deutsche Privatanleger:** Gut umsetzbar: UCITS-US-Treasury-7-10Y (IBTM.L) oder Bund-ETF plus Geldmarkt-ETF (XEON); monatlich, niedriger Umschlag. Ergebnis gilt fuer US-Duration, bei Euro-Anleihen anderes Zinsregime.
- **Quellen:**
  - Newfound Research 2018, Timing Bonds with Value, Momentum, and Carry, https://blog.thinknewfound.com/2018/01/timing-bonds-value-momentum-carry/
  - Newfound Research 2017, Duration Timing with Style Premia, https://blog.thinknewfound.com/2017/06/duration-timing-style-premia/

### 23. Rohstoff- und Gold-Trendfilter (DBC + GLD je 50 %, SMA 210), Long/Cash

- **ID:** `commodity_gold_trend_dbc_gld` | **Familie:** crypto
- **Mechanismus:** Rohstoff-Futures zeigen Trend ueber Monate (Lagerhaltung, Angebotsanpassung); ein Trendfilter vermeidet lange Baermaerkte und den Contango-Verlust in Abwaertstrends. Rohstoffe als eigene Anlageklasse neben Aktien und Anleihen.
- **Spezifikation (feste Parameter):** Universum DBC (ab 2006-02-06) und GLD (ab 2004-11-18). Taeglich nach Handelsschluss t: on_X = AdjClose_X(t) > SMA210(AdjClose_X)(t); w_X = 0.5 wenn on_X, sonst 0; Rest Cash (^IRX). Anpassung zur Eroeffnung t+1. Kein Hebel, kein Short. Kosten 10 bp je Seite (Stress 25 bp). Start 2006-06.
- **Ticker:** DBC, GLD, ^IRX, GSG, IAU
- **Datenstart:** 2006-06
- **Rebalancing:** taeglich pruefen (ca. 7.5 Einheiten Umschlag pro Jahr)
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - Fenster 168 Tage
  - Fenster 252 Tage
  - Gold allein (GLD) statt DBC+GLD
- **Abbruchkriterium:** Verwerfen, wenn der Sharpe-Vorteil gegenueber 50/50-Buy&Hold in beiden Dekaden (2006-2015, 2016-2026) unter 0.05 liegt oder der Netto-Sharpe unter SPY (ca. 0.57) bleibt und der MaxDD-Vorteil < 15 Prozentpunkte ist.
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.25-0.45 (eigener Check 0.47 vs 0.38 B&H, 2016-2026 verliert der Filter gegen B&H; Standardfehler 0.22 bei 20 Jahren)
- **Hinweis deutsche Privatanleger:** Rohstoffe: UCITS-Rohstoff-ETF (swap-basiert) oder Gold-ETC; Gold-ETCs haben teils das Haltefrist-Privileg (steuerfrei nach 1 Jahr bei physischer Lieferbarkeit), das durch Trendumschlag verloren geht. Steuerliche Einordnung des konkreten Produkts pruefen.
- **Quellen:**
  - Gorton, Rouwenhorst 2006, Facts and Fantasies about Commodity Futures, https://www.nber.org/papers/w10595
  - Bhardwaj, Gorton, Rouwenhorst 2015, Facts and Fantasies about Commodity Futures Ten Years Later, https://www.nber.org/papers/w21243

### 24. BTC/ETH Trend-Ensemble (SMA 20/50/100/200), Long/Flat mit Cash

- **ID:** `crypto_trend_ens_btc_eth` | **Familie:** crypto
- **Mechanismus:** Trendfolge in einem aufmerksamkeitsgetriebenen, von Privatanlegern dominierten Markt: Momentum durch Zufluss- und Herdeneffekte. Der Nutzen laut Eigencheck ist vor allem Drawdown-Kontrolle (-54 % statt -83 %).
- **Spezifikation (feste Parameter):** Universum BTC-USD (ab 2014-09-17), ETH-USD (ab 2017-11-09), Cash ^IRX. Taeglich nach dem UTC-Tagesschluss t, fuer X in {BTC, ETH}: s_X = (1/4)*sum_{n in {20,50,100,200}} 1[Close_X(t) > SMA_n(Close_X)(t)] (ETH erst nach 200 Closes, sonst s_ETH = 0). w_X = 0.5*s_X, w_cash = 1 - w_BTC - w_ETH. Anpassung zur Eroeffnung t+1 (00:00 UTC). Kosten 20 bp je Einheit |Delta w| (Stress 50 bp). Kein Hebel, kein Short. Start 2015-09.
- **Ticker:** BTC-USD, ETH-USD, ^IRX
- **Datenstart:** BTC 2014-09-17 (Test ab 2015-09), ETH 2017-11-09
- **Rebalancing:** taeglich pruefen, Umschlag ca. 6-19 Einheiten pro Jahr
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - Einzelregel Close > SMA50 -> 100 % BTC
  - Einzelregel Close > SMA200 -> 100 % BTC
  - Kosten 50 bp je Einheit (Spread-Stress)
- **Abbruchkriterium:** Verwerfen, wenn 2023-2026 der MaxDD-Vorteil gegenueber BTC Buy&Hold < 20 Prozentpunkte betraegt ODER bei 50 bp Kosten der Sharpe unter BTC Buy&Hold faellt. Aussagekraft ist durch ca. drei Boom/Bust-Zyklen begrenzt und wird so ausgewiesen (kein 2008).
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.6-1.0 (Eigencheck 1.38 vs 1.10 B&H, in-sample-lastig; Standardfehler eines Sharpe ueber 11 Jahre 0.3-0.4; Rendite-Erwartung aus 70 % CAGR ist unrealistisch)
- **Hinweis deutsche Privatanleger:** Handel ueber Krypto-ETN/ETC (BTCE.DE, VBTC.DE ab 2020) oder Boerse. Steuer: Direktbesitz hat Haltefrist von 1 Jahr, die durch Trendumschlag verloren geht; ETN/ETC steuerlich anders (Abgeltungsteuer) - Einordnung vor Echtgeld pruefen. Spread/TER ungemessen.
- **Quellen:**
  - Zarattini, Pagani, Barbon 2025, Catching Crypto Trends, https://abarbon.com/papers/catching-crypto-trends
  - Han, Kang, Ryu 2023, Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market, https://acfr.aut.ac.nz/__data/assets/pdf_file/0009/918729/Time_Series_and_Cross_Sectional_Momentum_in_the_Cryptocurrency_Market_with_IA.pdf

### 25. Prediction-Market-Favoriten halten (Favorite-Longshot-Ernte, Polymarket/Kalshi)

- **ID:** `pm_favorite_maker` | **Familie:** altdata
- **Mechanismus:** Favorite-Longshot-Bias: Wetter ueberzahlen Aussenseiter-Kontrakte (Lottery-Praeferenz), daher sind Favoriten (70-95 %) im Mittel leicht unterbewertet; Maker verdienen am Bias, Taker zahlen (Buergi/Deng/Whelan, Kalshi). Eigenstaendige Quelle ohne Bezug zu Boersenkursen.
- **Spezifikation (feste Parameter):** Daten eingefroren aus Polymarket: Marktliste/Aufloesung via Gamma-API, Tagespreise via CLOB prices-history (interval=max, fidelity=1440). Universum: binaere, aufgeloeste Maerkte mit >= 14 Tagen Preishistorie und kumuliertem Volumen >= 20000 USD; annullierte Maerkte zaehlen mit PnL 0. Fuer jedes Event mit Aufloesungsdatum D: Signaltag s = D - 8 Tage; p_yes = Tages-Close am Tag s; Kandidaten-Seiten YES mit p = p_yes, NO mit p = 1 - p_yes; Kandidat wenn 0.70 <= p <= 0.95. Hoechstens EINE Position pro Event (Seite mit hoechstem p). Ausfuehrung am Folgetag s+1 zum Tages-Close der gewaehlten Seite plus 0.01 (1 Tick Slippage); Sensitivitaet Fuellung zu p(s). Einsatz je Event 0.5 % des Kontos, max. 10 % gleichzeitig offen. Halten bis Aufloesung; PnL = (1-f) bei Gewinn, sonst -f. Gebuehren Baseline 0, Sensitivitaet 2 % vom Einsatz.
- **Ticker:** Polymarket Gamma-API (gamma-api.polymarket.com/markets), Polymarket CLOB prices-history
- **Datenstart:** ca. 2020 (Polymarket-Historie, nicht geprueft)
- **Rebalancing:** eventgetrieben, Haltedauer ca. 8 Tage bis Aufloesung
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - Horizont D-4 Tage
  - Horizont D-11 Tage
  - Band 0.50-0.95 statt 0.70-0.95
- **Abbruchkriterium:** Verwerfen, wenn das 95-%-Konfidenzintervall (ereignisgeclusterter Bootstrap) der mittleren Rendite pro Event nach 1 Tick Slippage und 2 % Gebuehr die Null enthaelt, bei mindestens 300 Events und gleichem Vorzeichen in beiden Halbjahres-Splits.
- **Erwartete Sharpe nach Nachpublikations-Verfall:** nicht bestimmbar (kein Zeitreihen-Sharpe); Erwartung pro Event nach Taker-Slippage etwa 0 bis +1 %, Maker-Edge laut Buergi et al. +2.6 % pro Kontrakt vor Verfall der Bias
- **Hinweis deutsche Privatanleger:** Zugang, Recht und Steuer fuer Wohnsitz Deutschland nicht geprueft. Daten sind frei abrufbar; Echtgeld nur nach Freigabe-Tor durch Nick. Historie erst ab ca. 2020 (kuerzer als 15 Jahre; kreative Ausnahme).
- **Quellen:**
  - Buergi, Deng, Whelan 2026, Makers and Takers: The Economics of the Kalshi Prediction Market, https://www.karlwhelan.com/Papers/Kalshi.pdf
  - Le 2026, Decomposing Crowd Wisdom: Domain-Specific Calibration Dynamics in Prediction Markets, https://arxiv.org/abs/2602.19520

### 26. Cross-Asset-TSMOM USA: Long/Cash-Umschalter SPY / IEF / SHY

- **ID:** `xtsmom_us_switch_longcash` | **Familie:** gap_crossasset_bond_equity_leadlag_signals
- **Mechanismus:** Cross-Asset-Signale (Pitkaejaervi/Suominen/Vaittinen): Der Zustand des Anleihenmarkts (12M-Rendite) informiert ueber das Aktienmarkt-Regime. Aktien und Anleihen steigend -> Aktien; Aktien fallend und Anleihen steigend (Flucht in Qualitaet) -> Anleihen; Anleihen fallend -> Cash.
- **Spezifikation (feste Parameter):** Universum SPY, IEF, SHY (Cash; vor 2002-07 ^IRX/1200 pro Monat). Langtest: VFINX (ab 1980-01-02) statt SPY, VFITX (ab 1991-10-28) statt IEF; davor Bond-Proxy aus ^FVX. r12(X) = AdjClose(T)/AdjClose(Monatsende T-12M) - 1 - rf12, rf12 = Produkt ueber 12 Monate von (1 + ^IRX[Vormonatsende]/100/12) - 1, kein Skip-Monat. Am Monatsende T: rE = r12(SPY), rB = r12(IEF). rE > 0 und rB > 0: 100 % SPY; rE <= 0 und rB > 0: 100 % IEF; rB <= 0: 100 % SHY. Wechsel zur Eroeffnung T+1, halten bis zum naechsten Monatsende. Kosten 2 bp je Seite (Stress 5/10 bp), Abgeltungsteuer im Steuermodul.
- **Ticker:** SPY, IEF, SHY, VFINX, VFITX, ^IRX, ^FVX
- **Datenstart:** Langtest ab 1981 (VFINX/VFITX), ETFs ab 2002-07-30
- **Rebalancing:** monatlich
- **Vorab festgelegte Sensitivitaetsvarianten (zaehlen als Versuche):**
  - 12-1: Skip-Monat im Lookback
  - TLT statt IEF als Anleihe-Bein
  - Ausfuehrung Schluss t+1 statt Eroeffnung
- **Abbruchkriterium:** Verwerfen, wenn der Netto-Sharpe nicht ueber dem reinen 12M-Trendfilter auf SPY (long/cash) liegt oder die Strategie in 2008-2026 nicht mindestens 15 Prozentpunkte weniger MaxDD als SPY hat (dann bringt der Bond-Filter nichts).
- **Erwartete Sharpe nach Nachpublikations-Verfall:** 0.30-0.50 (Quantpedia-Indikation 6.5 % p.a. bei 10 % Vola brutto 1980-2015 fuer die Long-Short-Fassung; Long/Cash ohne Short erwartet schwaecher)
- **Hinweis deutsche Privatanleger:** Gut umsetzbar mit drei UCITS-ETFs (Aktien, Staatsanleihen 7-10J, Geldmarkt); Zustand 2 ist nur ein Wechsel zwischen Anleihe und Aktie. Steuer bei jedem Wechsel; Regimewechsel positive Aktien-Anleihen-Korrelation (2022) ist das Hauptrisiko.
- **Quellen:**
  - Pitkaejaervi, Suominen, Vaittinen 2020, Cross-asset signals and time series momentum, https://doi.org/10.1016/j.jfineco.2019.02.011
  - CXO Advisory 2017, Cross-asset Class Intrinsic Momentum, https://www.cxoadvisory.com/equity-premium/cross-asset-class-intrinsic-momentum

## Abgelehnte Kandidaten

| ID | Begruendung |
|----|-------------|
| `faber_spx_sma10_cash` | Gleiche Idee wie trend_ma12_us_equity_cash (Index-Trendfilter); SMA10 ist dort vorregistrierte Variante. Zwei Eintraege waeren eine Doppelzaehlung derselben Renditequelle. |
| `slow_ewma_crossover_riskparity` | Gleiche Renditequelle wie mop2012 (Mehrmarkt-Trendfolge mit Vol-Normierung); eigener Check Sharpe 0.38 nur +0.07 vor EW12 und nicht signifikant; cx 3, viele Parameter (50/200, Clip, 800 Tage). |
| `hop_multihorizon_tsmom_10vol` | Gleiche Quelle wie mop2012; eigener Check LS Sharpe 0.15, 19 Einheiten Umschlag pro Jahr; das 10-%-Portfolio-Vol-Ziel laeuft als Variante von mop2012. |
| `wml_dynamic_dm_expanding` | cx 5: GJR-GARCH, mehrere OLS mit wachsendem Fenster, viele Freiheitsgrade und In-Sample-Konstruktion im Paper; Zugewinn gegenueber cvol klein; ueberschreitet 150 Zeilen; keine unabhaengige Replikation. |
| `industry_mom_ff17_ls` | Reine Negativ-Kontrolle auf nicht handelbaren Industriekoerben; Novy-Marx/Velikov zeigen netto -0.29 %/Monat. sector_etf_top3_12m und der Nagel-Test decken die Branchen-Frage mit handelbaren ETFs ab. |
| `faber_gtaa5_sma10_tranched` | Gleiche Regel wie faber_gtaa5_sma10; die Staffelung gegen Timing-Luck ist dort als vorregistrierte Variante enthalten. |
| `keller_daa_g12` | Gleiche Familie und gleiches Universum wie PAA; Parameter T=6, B=2, DBC/GSG im Abruf nicht verifiziert, nur Sekundaerquellen; 2-Asset-Canary ist ein optimierter Parameter. |
| `keller_baa_g12_balanced` | cx 4: Selektion auf dem Entwicklungsfenster ohne Mehrfachtest-Korrektur (21 % CAGR bei 14.6 % MaxDD fuer G4/T1 ist Overfit-Alarm), Umschlag ca. 470-520 %; Beitrag zur Diversifikation gegenueber PAA gering. |
| `riskmanaged_momentum_bsc` | Doppelt mit wml_volscaled_ff (gleiche Barroso/Santa-Clara-Methode auf French-Mom); Sektor-ETF-Proxy ist ein eigener Design-Vorschlag ohne Beleg. |
| `balanced_6040_twolevel_voltarget` | Hebel auf der Anleihenseite mit Finanzierungskosten, Gross-Cap, Band und mehrere Eigenannahmen; nur ein praktikergesponsertes Paper, Stichprobe 1988-2017 mit negativer Aktien-Anleihen-Korrelation; deckt sich in der Idee mit eq_voltarget. |
| `downside_vol_fixedweight_market` | Variante des Vol-Targeting (eq_voltarget); expandierendes c_k, Cap 3.0 und 50/50-Mix sind Lab-Annahmen; keine unabhaengige Replikation, Autoren sind Koautoren der kritischen Studie. |
| `conditional_voltarget_extremes` | Die Regel des Papers wurde nicht gefunden; der Eintrag ist ein Design-Vorschlag mit nicht aus dem Paper stammenden Schwellen und waere damit Data-Snooping, keine Replikation. |
| `gp_quality_profitability` | Auf Faktor-Ebene ueberlappt Gross Profitability stark mit RMW (in static_multifactor enthalten); ETF-Proxys SPHQ/QUAL zeigen seit 2011/2013 keinen Vorsprung vor SPY (eigener Check). |
| `qmj_quality_minus_junk_series` | Reihe nur ueber AQR-Excel (Download braucht Freigabe von Nick), nicht rekonstruierbar, starke Ueberlappung mit RMW/Gross Profitability; kann nach Freigabe als Zusatz in static_multifactor eingehen. |
| `bab_beta_neutral_etf_pair` | cx 4: AQR-Download noetig, FF5-Alpha nach Kosten nicht signifikant (Novy-Marx/Velikov), Mikro-Cap-Konzentration; ETF-Paar SPLV/SPHB nur 15 Jahre, ungetestet und mit Shorts/Hebel; naives Paar ist Markt-Short. |
| `ivol_lowvar_ls` | Reine Negativ-Kontrolle: Rendite stammt aus der teuren Short-Seite (netto 0.11 %/Monat, t 0.37); die handelbare Long-Seite ist in lowvol_defensive_longonly enthalten. |
| `xasset_value_mom_5050` | cx 4: Rohstoff-Dauerfutures unbereinigt (Rollspruenge), FX-Zins/CPI-Reihen aus FRED-OECD (teils eingestellt), Reversal-Proxy statt B/M; Laender-Value und Momentum sind einzeln bereits in country_value und country_etf_xsmom abgedeckt. |
| `kmpv_carry_fx_eq_bond_proxy` | cx 4: Rohstoff-Carry (groesste Praemie im Paper) nicht gratis, Aktien-Carry als ETF-Ausschuettung und Bond-Carry ohne Roll-down sind ungetestete Naeherungen; FX-Carry laeuft einzeln in fx_carry_g10_rank. |
| `us_value_hml_etf_pair` | Negativ-Kontrolle: IWD-minus-IWF Long-Short mit Short-Seite und kleinem Brutto-Edge (HML-Drawdown 55 % 2007-2020); HML steckt bereits in static_multifactor. |
| `residual_reversal_largecap_monthly` | cx 4: Survivorship-verzerrtes S&P-500-Universum, Dezil-Long-Short mit Shorts, 36-Monats-Regressionen pro Aktie; Parameter nur aus dem Abstract; Vorteil der residualen Umkehr nur als Selbstaussage des Robeco-Teams. |
| `top100_weekly_reversal` | Netto-Marge winzig (bei 500 Aktien nur +10.6 bp pro Woche), Zahlen nur aus Sekundaerquelle, Survivorship, 20 Positionen mit Shorts; fuer Privatanleger nicht umsetzbar. |
| `avellaneda_lee_sector_etf_statarb` | cx 5: Sharpe 1.1 nur bis 2002, Paper dokumentiert den Verfall selbst; 10 bp Round-Trip und t+1-Ausfuehrung zerstoeren den Edge sehr wahrscheinlich; Shorts, Survivorship, Tagesumschlag. |
| `ae_sector_etf_residual_sscore` | Doppelt mit avellaneda_lee_sector_etf_statarb (gleiche Regel); gleiche Gruende. |
| `coint_sector_pairs_sp500` | Clegg/Krauss (survivorship-frei): 2010-2015 netto negativ; Rad/Low/Faff: deutlich weniger Gelegenheiten ab 2009; Survivorship der Gratisliste; ggr_distance_sector_zerocross deckt die Pairs-Nullhypothese bereits ab. |
| `chen_comovement_reversal` | Gewinn laut Autoren selbst groesstenteils Short-Term-Reversal plus Industrie-Momentum; ca. 100 % Monatsumschlag; Vorzeichenkonvention der Divergenz im Paper noch zu pruefen; ca. 50 Aktien je Dezil im S&P 500. |
| `etf_sector_coint_pairs` | Eigenentwurf ohne Paper-Evidenz (Kriterium 1 nicht erfuellt); Sektor-ETFs sind hochkorreliert, aber nicht kointegriert - erwartetes Ergebnis Dauer-NO-TRADE. |
| `same_month_seasonality_industry` | Long-Short Top2/Bottom2 auf 17 Industrien mit nahezu 100 % Monatsumschlag; Composite 2003-2011 schon nicht mehr signifikant (t 1.75); ETF-Umsetzung erst ab ca. 2019 validierbar. Kann spaeter nachgeholt werden. |
| `overnight_spy_close_to_open` | Kostenfalle (252 Round-Trips pro Jahr, ca. 5 % p.a. Kosten bei 1 bp pro Trade); Brutto-Praemie ist bekannt, netto negativ; allenfalls Diagnose-Zerlegung im Backtester, keine eigene Strategie. |
| `ew_multiasset_1n` | Ist eine Kontrolle, keine Strategie: 1/N ueber U9 wird zentral als Benchmark mitgerechnet (siehe ivp_risk_parity_unlevered). |
| `erc_shrunk_cov` | Bei geschrumpften Korrelationen faktisch Inverse-Vol; laeuft als Variante von ivp_risk_parity_unlevered. |
| `minvar_industries_constrained` | Faktorwette Low-Vol wie lowvol_defensive_longonly; Constraint-Parameter (Cap 5 %) sind Lab-Entscheidung; USMV/SPLV zeigen seit 2011 keinen Vorsprung; Beitrag zur Diversifikation klein. |
| `hrp_lopez_de_prado` | Originalpaper nur mit Simulationsdaten, keine Realdaten-Evidenz; mit 9 gut konditionierten Assets kaum Vorteil gegen Inverse-Vol; laeuft als Variante von ivp_risk_parity_unlevered. |
| `vrp_dual_signal_zarattini` | Paper erst Oktober 2025, keine echte Out-of-Sample-Zeit; Replikation nur als Forumspost mit nicht im Paper stehendem SPY-Overlay; Variante A braucht Short-VIXY mit Leihe; Parameter-Snooping am Gitterrand. svxy_term_structure_filter deckt die Short-Vol-Idee ab. |
| `vrp_equity_timing_btz` | Das Paper ist eine Renditeprognose-Regression (R2 4-7 % in-sample), die Median-Schwelle ist Lab-Uebersetzung; Cash-Phasen kosten Rendite, Beitrag laeuft redundant zu den Trend-/Vol-Timing-Regeln. |
| `vix_basis_simon_campasano` | cx 5: Cboe-Settle-Daten vor 2013 nicht abrufbar (HTTP 403), Original-Zeitraum 2006-2011 nicht reproduzierbar, seit 2010 kaum Gewinn laut CXO, Margin-Annahmen willkuerlich, Nutzungsbedingungen ungeprueft. |
| `jump_model_regime_01_equity` | cx 4: eigene DP-/Koordinatenabstieg-Implementierung mit 10 Neustarts, monatlicher lambda-Wahl und halbjaehrlicher Neuschaetzung sprengt 150 Zeilen; im Kern Downside-Vol-Filter; Parameter und Gitter nicht aus dem Paper verifiziert. |
| `neely_techind_mv_timing` | Eigener Nachbau 2012-2026: R2_OS -1.2 %, CER-Gewinn negativ, Sharpe 0.18 vs Buy&Hold 0.27; Hebel 1.5, hoher Umschlag; das binaere Signal laeuft in trend_ma12_us_equity_cash. |
| `sop_valuation_timing` | Nachbau reproduziert das Paper bis 2007, versagt aber danach (2008-2023 R2_OS -1.2 %, CER-Gewinn -1.8 %): Kriterium 1 (nicht komplett widerlegt) praktisch nicht erfuellt; Shiller-Daten mit Interpolations-/Revisionsproblemen. |
| `term_spread_recession_filter` | Eigener Check: bis 1999 nuetzlich, seit 2000 nicht mehr (Sharpe 0.39 vs 0.42), Krise 2007-09 nicht vermieden; als Zusatz zum Trendfilter schaedlich. Nur dokumentierter Negativ-Eintrag; Carry-Anteil steckt in bond_composite. |
| `sentiment_state_anomaly` | Index nur jaehrlich aktualisiert und mit Gesamtstichproben-Hauptkomponenten gebaut (Look-ahead, kein Live-Signal); Gewinne aus Short-Beinen kleiner illiquider Aktien; kein handelbares Ergebnis. |
| `fears_reversal` | Datenquelle pytrends inoffiziell, gesampelt, nicht reproduzierbar (Replikation trifft nur 72 % der Entscheidungen); Keyword-Selektion; sehr wenige Handelstage. |
| `sad_winter_rotation` | Mechanismus von Replikationen bestritten (Kelly/Meschke), ueberlappt vollstaendig mit Halloween (kein neuer Edge); Datumsgrenzen sind Mining-Gefahr. |
| `pead_ear_yahoo_surprise` | cx 4: Drift in investierbaren Large Caps seit 2006 nicht nachweisbar (Martineau); Yahoo-Earnings-Daten inoffiziell mit Rundungsrauschen, Survivorship; Short-Seite. Wuerde als Ereignis-Idee gern aufgenommen, doch Gratis-Daten tragen den Test nicht. |
| `vol_managed_momentum_bsc` | Doppelt mit wml_volscaled_ff (gleiche Methode, gleiche French-Mom-Reihe). |
| `tsfm_factor_momentum` | Mit nur 7 Faktoren statt 65 fehlt die Diversifikation; QMJ/BAB benoetigen AQR-Download mit Freigabe; Annualisierung der Signalgleichung unverifiziert; ETF-Proxy nur 13 Jahre. |
| `factor_etf_blend_long_only` | Nur 13 Jahre gemeinsame Historie bei kleinem Tracking Error: kein statistisch belastbarer Alpha-Test moeglich; Projekterfahrung zeigt keinen Vorsprung; Min-Vol/Quality-Teil durch lowvol_defensive_longonly abgedeckt. |
| `crypto_funding_carry_delta_neutral` | Praemie verfallen (2025/2026 unter T-Bills im eigenen Check), Boersen-Gegenpartei- und Margin-Risiko, Derivate-Zugang fuer deutsche Privatanleger ungeklaert, Basis-P&L nicht modelliert. |
| `dsr_gate_honest_n` | Keine Handelsstrategie, sondern Pruefstand-Gate; geht in die Methodik (Deflated Sharpe Ratio) und die Abnahmekriterien ein. |
| `t3_haircut_sharpe_gate` | Keine Strategie, sondern Gate (t >= 3, Holm/BHY, Haircut-Sharpe); fliesst in die Methodik-Notizen. |
| `publication_decay_discount` | Keine Strategie, sondern Rechenregel fuer Erwartungsabschlaege (McLean/Pontiff); in expected_sharpe_after_decay verwendet. |
| `pbo_cscv_selection_gate` | Keine Strategie, sondern Gate fuer Variantenfamilien (PBO via CSCV); bei den Familien mit mehr als zehn Varianten einzusetzen. |
| `spa_stepm_family_test` | Keine Strategie, sondern familienweiter Bootstrap-Test; Formeln aus Gedaechtnis, vor Nutzung per Simulation pruefen (arch-Paket). |
| `bond_carry_termspread_gate` | Einzelsignal des Komposits bond_composite_3sig_longonly und dort als Variante vorregistriert; eigener Check ab 2018-11 Sharpe -0.41, Position Ende 2021 noch voll long. |
| `bond_trend_dualewma_longflat` | Einzelsignal des Komposits (Variante); eigener Check 1972-2018 Sharpe 0.23 gegen Buy&Hold 0.28; die Sihvonen-Variante (c) ist Eigenableitung ohne gelesene Handelsregel. |
| `bond_value_realyield_longflat` | Einzelsignal des Komposits (Variante); gratis Inflationserwartungen nur teilweise und mit Vintage-Problem, im eigenen Check nicht getestet. |
| `xtsmom_country_basket_longcash` | cx 4: 12 Laender mit FRED-OECD-Renditen (Monatsmittel, Verzug, teils eingestellt) und synthetischen Anleiherenditen; Laendermaerkte stark korreliert, wenig Zusatznutzen ueber den US-Umschalter; Datenabruf von FRED in der Recherche gescheitert. |
| `xtsmom_us_ls_replica_volscaled` | Long/Short mit Hebel bis 2x und Borrow-Annahmen; fuer Privatanleger nicht umsetzbar, nur Obergrenze; Verbesserung gegenueber TSMOM fuer USA laut CXO gering. |
| `rsz_us_leads_country_etfs_longcash` | Laut Siliverstovs und Aye/Balcilar/Gupta fragil und zeitvariabel; US-gelistete Laender-ETFs handeln zu US-Zeiten, ein Teil des Vorlaufs fehlt; Regel investiert fast immer (misst eventuell nur Markt-Beta-Timing). |
| `htv_industry_leads_market_combo` | Tse (2015): nur 1 bis 7 von 48 Branchen signifikant, vereinbar mit Markteffizienz; Kombinationsregel ist Eigenentwurf; French-Daten live nicht zeitnah nutzbar. |
| `ni_exclusion_screen_french` | Vermutlich Duplikat der Investment-/Profitabilitaets-Exposition (FF5: RMW/CMA); mit Gratis-Daten nur Research-Replikation ohne Live-Nachbau; Alpha nach 2008 nicht gemessen. |
| `ni_longshort_ff5_spanning_gate` | Diagnose-Test, keine Handelsstrategie; erwartetes Ergebnis: von FF5 erklaert (Fama/French 2016). Kann als Zusatz-Regression auf static_multifactor laufen. |
| `net_payout_proxy_french_dp_ni` | Proxy ist kein Net Payout (Rueckkaeufe fehlen); D/P-Teil bringt nichts hinzu (HXZ), redundant zu NI und CMA/RMW; Long-Short brutto, nicht handelbar. |
| `shareholder_yield_etf_basket_vs_spy` | Nur ca. 13 Jahre gemeinsame Historie, SYLD aenderte 2018/2020 die Konstruktion; TER in der Groessenordnung der Praemie; kein statistisch belastbarer Test, Quelle fuer Zahlen nur Blog. |
| `ucits_dividend_etf_negative_entry` | Behauptet ausdruecklich keinen Edge; Ticker, Startdaten und Faktorreihen (Developed/Global) nicht verifiziert; Dividendenrendite allein ist bei strenger Replikation insignifikant. |

## Methodik-Zusammenfassung (Mehrfachtest, Haircut, verfall)

1. Deflated Sharpe Ratio (Bailey/Lopez de Prado 2014): DSR = Phi( (SR_hat - SR0)*sqrt(T-1) / sqrt(1 - g3*SR_hat + (g4-1)/4*SR_hat^2) ), SR_hat pro Periode, g3 Schiefe, g4 Kurtosis (nicht Excess).
2. Schwelle SR0 = sqrt(V)*((1-gam)*Phi^-1(1-1/N) + gam*Phi^-1(1-1/(N*e))), gam = 0.5772, V = Varianz der Sharpe-Werte ueber die N Versuche; fehlt V, V = 1/T. N ist die effektive Zahl unabhaengiger Versuche (bei M Varianten N_eff = ceil(rho_bar + (1-rho_bar)*M)).
3. MinBTL-Vorfilter: Jahre >= (((1-gam)*Phi^-1(1-1/N) + gam*Phi^-1(1-1/(N*e))) / SR_ann)^2; notwendig, nicht hinreichend.
4. Eigener Check des Mindest-Sharpe fuer DSR >= 0.95 (Normalrenditen, V = 1/Jahre): 18 Jahre N=1: 0.39, N=10: 0.76, N=40: 0.90, N=200: 1.04; 10 Jahre 0.52/1.02/1.21/1.40; 25 Jahre 0.33/0.64/0.77/0.88. Unsere Liste hat M <= 26 x 4 = 104 Versuche (Strategie plus je 3 Varianten); N_eff geschaetzt 40-70, also bei 18 Jahren Sharpe ca. 0.9-0.95 noetig. Fast keine ETF-Strategie wird das erreichen - das ist der Befund, kein Fehler.
5. Harvey/Liu/Zhu 2016: Hurde t >= 3.0 statt 2.0; Holm- oder BHY-angepasste p-Werte, Haircut-Sharpe HSR = t_adj/sqrt(T)*sqrt(12), Haircut = 1 - HSR/SR; Mindest-SR fuer t = 3 bei 5/10/20/40/60 Jahren: 1.34/0.95/0.67/0.47/0.39; Bonferroni-t bei M = 20/50/100/316: 3.02/3.29/3.48/3.78. HLZ: nach Korrektur 132-158 von 296 publizierten Faktoren nicht mehr signifikant; Haircut 60 % bei SR 0.75 und N = 200.
6. Nachpublikations-Verfall (McLean/Pontiff 2016): Rendite von US-Aktien-Anomalien statistisch -26 % ausserhalb der Stichprobe und -58 % nach Publikation; Chen/Zimmermann (arXiv 2209.13623): Publikationsbias nur 10-15 % (optimistische Gegenposition, nur Abstract); Chen/Velikov: mittlere Anomalie netto ca. 4 bp/Monat. Gilt fuer Aktien-Querschnitte, auf ETF-Timing/Allokation nicht belegt uebertragbar.
7. Anwendung im Lab: Erwartungs-Sharpe = SR_IS*(1-0.35 bis 0.58) bei Aktien-Anomalien; bei Trend/Allokation mit eigenem Check wird dieser statt eines Abschlags genannt (liegt meist schon im Nach-Publikations-Zeitraum).
8. Probability of Backtest Overfitting (Bailey et al. 2015, CSCV): S = 16 Bloecke, 12870 Kombinationen; PBO <= 0.05 bestanden; Lab-Zusatzregel PBO > 0.2 wackelig, >= 0.5 Muenzwurf; Familie bei Durchfall komplett verwerfen. Einsetzbar nur bei N >= 10 Varianten und T >= 160 Perioden.
9. White Reality Check / Hansen SPA / Romano-Wolf StepM (stationaerer Bootstrap, B = 10000, Blocklaenge ca. T^(1/3)): familienweiter Test gegen den Benchmark; Formeln aus Gedaechtnis (nur Bibliografie verifiziert), vor Nutzung per Simulation pruefen (arch-Paket).
10. Trial-Register: Jede Variante und jede verworfene Idee zaehlt als Versuch; mit den 26 Strategien (hoechstens 3 vorab festgelegte Varianten, keine nachtraegliche Auswahl) sind das M <= 104 plus Sonderlaeufe; wer N zu klein ansetzt, macht das Gate zu lasch.
11. Fuer jede Strategie vorab: Hypothese, feste Parameter, Abbruchkriterium und Mindest-Sharpe in HYPOTHESEN.md festhalten, bevor der Backtest laeuft; Parameter werden nicht auf denselben Daten gewaehlt.
12. Pflicht-Kontrollen gegen Selbsttaeuschung: SPY Buy&Hold, 60/40, konstanter Mix mit gleicher mittlerer Exposure, exposure-gematchte Zufallseinstiege (Permutationstest), Teilperioden vor/nach 2008, Block-Bootstrap der Sharpe-Differenz.
13. Ausfuehrung: Signal aus Daten bis Schluss t, Handel fruehestens am naechsten Handelstag; Kosten zentral (5-10 bp ETFs, Stress 20-50 bp), Abgeltungsteuer 26.375 % separat; Standardfehler eines Sharpe bei 18 Jahren ca. 0.24, daher Sharpe-Differenzen unter 0.15 nicht unterscheidbar.
14. Erwartung ehrlich setzen: Die meisten Kandidaten (Trend, Tactical, Vol-Management) liefern Risikoreduktion, keine Mehrrendite; Gates sollen deshalb zwischen echter Rendite-Praemie und Investitionsquote/Drawdown-Schutz trennen.
15. Gates nicht als Strategien zaehlen, aber zwingend vor jeder Freigabe: DSR >= 0.95 UND t >= 3 (Holm) ODER explizit als Risikoreduktions-Strategie mit Drawdown-Beleg gegen Konstant-Mix klassifizieren.
