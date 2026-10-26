# Familie: Volatilitaetsgesteuerte Portfolios / Vol-Targeting

Stand der Recherche: 2026-10-11. Budget war ca. 15 Web-Abrufe; tatsaechlich genutzt: 9 Websuchen + 11 Seitenabrufe = 20 (davon 5 Abrufe an 403 gescheitert, siehe Abrufstatus). Ich habe das Budget also ueberschritten, weil die ersten PDF-Abrufe nur Binaerdaten lieferten und ich sie lokal mit pdftotext lesen musste.
Alle Zahlen stammen aus tatsaechlich gelesenen Seiten/PDFs oder sind als "Suchsnippet" bzw. "aus Gedaechtnis" markiert. Was ich nicht gefunden habe, steht ausdruecklich als "nicht gefunden".

## 0. Kurzfazit (ehrlich)

- Die Familie besteht aus EINER Idee: Exposure umgekehrt proportional zur zuletzt gemessenen Volatilitaet. Die Effekte unterscheiden sich stark je nach Anlageklasse:
  - Tail-Risiko-Effekt (weniger Vol-of-Vol, kleinerer Mean Shortfall, kleinere Drawdowns): breit belegt (Harvey et al. 2018, 60+ Assets, Man AHL). Das ist der robusteste Teil, aber ein "Sicherheits"-Effekt, kein Renditeversprechen.
  - Sharpe-Verbesserung: bei Aktienmarkt moderat und NICHT signifikant (Cederburg et al.: MKT 0.42 -> 0.51, p = 0.30), bei Anleihen/Waehrungen/Rohstoffen praktisch null oder negativ (Harvey), bei Momentum gross und signifikant (MOM 0.48 -> 0.99, p = 0.00).
- Die Moreira-Muir-"Alphas" (Spanning-Regressionen) sind in Echtzeit nicht handelbar, weil sie ex-post-optimale Mischgewichte brauchen. Cederburg et al. zeigen: reale Out-of-Sample-Kombinationen schlagen die ungemanagte Variante in 72 von 103 Faellen NICHT (CER). Das ist der wichtigste Daempfer der Familie.
- Nach Kosten: Barroso-Detzel (nur Suchsnippet/Abstract-Ebene) sagen, dass ausser dem Marktfaktor kein Faktor die Kosten uebersteht; Marktfaktor nur bei hoher Stimmung. Eine Studie 2024 (nur Suchsnippet) sagt: nur Markt und Momentum teilweise robust nach Kosten.
- Interner Befund im Projekt: Laut Quant-Lab/CLAUDE.md brachte ein "Vol-Overlay" im Fly-of-Wallstreet-Projekt nichts. Das ist ein eigener, nicht dokumentierter Test; ich konnte ihn nicht pruefen, er passt aber zum unsicheren Sharpe-Effekt beim Aktienmarkt.
- Wichtigste Backtest-Falle: Die publizierten Vergleiche skalieren die Zielvola EX POST (Konstante k bzw. c, so dass die Vollstichproben-Vol gleich ist). In Echtzeit gibt es dieses c nicht. Alle Regeln unten verwenden deshalb eine feste Ziel-Vol oder ein expandierendes c. Und: Kontrolle muss eine Konstant-Mix-Strategie mit GLEICHER mittlerer Exposure/Vol sein, nicht nur Buy&Hold, sonst misst man Hebel statt Timing.
- Sample-Ende der Primaerliteratur: Harvey 2017, Cederburg/Wang-Yan 2016/2020, DeMiguel 2020. Die Jahre 2018-2026 (inkl. COVID-Gap 2020, Aktien-Anleihen-Gleichlauf 2022) sind fuer diese Familie praktisch ungetestet. Genau dort liegt der echte Out-of-Sample-Test im Quant-Lab.

Ranking-Begruendung: "Robustheit" = Evidenzstaerke x Handelbarkeit mit Gratis-Daten. Risk-managed Momentum hat die statistisch staerkste Evidenz, ist aber ein Long-Short-Faktor mit Short-/Umschlagskosten, die in der French-Reihe NICHT enthalten sind. Deshalb steht der einfache Markt-Vol-Target auf Platz 1, Momentum auf Platz 2.

## 1. Abrufstatus (Transparenz)

| Quelle | Status |
|---|---|
| Harvey et al. 2018, Duke-PDF (people.duke.edu/~charvey/Research/Published_Papers/P135_The_impact_of.pdf) | ABGERUFEN (WebFetch lieferte nur Binaer), lokal mit pdftotext GANZ gelesen. Die Zahlen-Tabellen (Exhibits 5, 8, 11, 13, 15, 16) sind durch Schriftkodierung unlesbar; nur Fliesstext-Zahlen sind verwertet. |
| Cederburg et al. 2020, Lehigh-PDF (lehigh.edu/~xuy219/research/COWY.pdf) | ABGERUFEN, lokal gelesen (Einleitung, Table 1, Teile von Sec. 3-4). Table 1 war lesbar. |
| Wang & Yan 2021, Lehigh-PDF (lehigh.edu/~xuy219/research/Downside.pdf) | ABGERUFEN, lokal gelesen (Einleitung, Definition, Teile Tabelle 3/4). Table 4 (Kosten) ist durch Layout verwuerfelt; nur Fliesstext verwertet. |
| NBER w22208 (Moreira-Muir) | ABGERUFEN, nur Abstract-Seite. |
| SSRN Barroso/Santa-Clara (abstract_id=2041429) | 403 |
| Saias 2017 MSc-These (repositorio.ucp.pt) | ABGERUFEN, lokal gelesen. Sekundaerquelle: repliziert die BSC-Methode (126 Tage, 12 % Ziel). NICHT das Original-Paper. |
| Alpha Architect "Conditional Volatility Targeting" | 403 |
| repub.eur.nl/pub/130215 (Bongaerts/Kang/van Dijk) | ABGERUFEN, nur Abstract; die exakte Regel steht dort NICHT. |
| ScienceDirect "The disappearing profitability of volatility-managed equity factors" | 403; nur Suchtreffer-Titel, NICHT gelesen, daher nicht als Paper gefuehrt |
| Wiley DeMiguel/Martin-Utrera/Uppal JF 2024 | 403 |
| Lancaster FoFI-2022 PDF (Arbeitspapierfassung DeMiguel et al., 10.05.2022) | ABGERUFEN, lokal gelesen: Abstract + Einleitung + Gliederung |
| Barroso & Detzel JFE 2021, Barroso & Santa-Clara JFE 2015 (Original) | NUR Suchsnippets (Abstract-Ebene), Volltext nicht gelesen. Barroso-Detzel-Aussagen werden zusaetzlich in der DeMiguel-Einleitung (gelesen) wiedergegeben. |

Konsequenz: Fuer BSC (Momentum) und Bongaerts et al. ist die Regel nur ueber Sekundaerquellen bzw. gar nicht verifiziert. Vor dem Kodieren sollten die Originale im Browser geoeffnet werden.

## 2. Gemeinsame Implementierungsregeln

- Signal am Schlusskurs t. Handel fruehestens t+1. Hauptvariante: Ausfuehrung zum Schlusskurs t+1 (MOC). Sensitivitaet: Open t+2. Das entspricht Harvey et al.: der Vol-Schaetzer fuer den Tag s nutzt Renditen nur bis s-2, also "24 Stunden im Voraus bekannt".
- Vol-Schaetzer: Harvey nutzt die Standardabweichung der Tagesrenditen mit exponentiell abfallenden Gewichten und ausdruecklich NULL-Mittelwert (also aus quadrierten Renditen), Aufwaermphase 270 Handelstage. Moreira-Muir/Cederburg/Wang-Yan nutzen die realisierte Varianz bzw. Vol des Vormonats aus Tagesdaten (Monatsrebalancing).
- Kosten: Harvey nimmt 1.0 bp Aktien, 0.5 bp Anleihen/Kredit, 1.0 bp Gold, 2.0 bp Oel, 3.5 bp Kupfer (Futures, Post-2008-Schaetzung, Autoren sagen selbst: fuer frueher nicht repraesentativ). Fuer ETFs im Quant-Lab: 2 bp einseitig als Basis, Sensitivitaet 5 und 10 bps. Wang-Yan testen 1, 10, 14, 25, 50 bps auf monatliche Gewichtsaenderungen von Faktoren.
- Hebel: Alle Sharpe-Gewinne der Literatur beruhen auf Hebel in ruhigen Phasen (Harvey: mittlere Exposure ist mit Vol-Scaling hoeher). Ohne Hebel (Cap 1.0) bleibt nur der De-Risking-Teil. Beide Varianten testen; Finanzierung des Hebels mit RF + 0.5 %/Jahr ansetzen (eigene Annahme, nicht aus Paper).
- Steuer (Deutschland, Abgeltungssteuer): Haeufiges Umschichten realisiert Gewinne. Wurde in den Papers nicht untersucht; im Quant-Lab separat ausweisen (Projektregel 4).
- Pflichtvergleiche: (a) Buy&Hold, (b) Konstant-Mix mit GLEICHER mittlerer Exposure, (c) Konstant-Mix mit gleicher Vollstichproben-Vol, (d) Teilperioden 1993-2007, 2008-2019, 2020-2026, (e) Stresstage (2020-02/03, 2022).
- Mehrfachtest: Pro Strategie nur 1 vorab festgelegte Hauptparametrierung (HL, Target, Cap); Variationen nur als Sensitivitaet, nicht zur Auswahl (Projektregel 3).

## 3. Strategien (nach erwarteter Robustheit)

### 3.1 eq_voltarget_ewma_harvey - Vol-Targeting auf den US-Aktienmarkt (EWMA, Harvey et al.)

Regel (Pseudocode):

    PARAMETER
      TARGET = 0.12      # annualisierte Ziel-Vol (Harvey: 10 %; 12 % naeher an SPY-Langfristvol; Sens. 0.10, 0.15)
      HL     = 20        # Halbwertszeit Handelstage (Harvey-Hauptfall; Sens. 10, 40)
      CAP    = 1.0       # Variante A: kein Hebel. Variante B: CAP = 1.5 (Hebel finanziert zu RF + 0.5 %/Jahr)
      BAND   = 0.05      # No-Trade-Band auf die Exposure (EIGENE Ergaenzung, nicht im Paper; Harvey rebalanciert taeglich)
      COST   = 2 bp einseitig auf |Delta pos|
      WARMUP = 270 Handelstage
    DATEN
      r[s]  = Tages-Totalrendite (SPY Adj Close pct_change; Langfrist: French Mkt-RF + RF)
      rf[s] = Tages-Geldmarktrendite (French RF; ab 1993 alternativ ^IRX/252)
    SCHAETZER (am Schluss von t, nur Daten <= t)
      lam   = 0.5 ** (1/HL)
      v[WARMUP-1] = mean(r[0:WARMUP]**2)
      v[t]  = lam*v[t-1] + (1-lam)*r[t]**2          # Null-Mittelwert (Harvey Fn. 8)
      sig[t]= sqrt(252 * v[t])
    ZIELGEWICHT UND POSITION
      pos[s] = Exposure, gehalten vom Schluss s-1 bis Schluss s (verdient r[s])
      target[s] = min(CAP, TARGET / sig[s-2])        # Signal Schluss s-2, Order Schluss s-1
      pos[s] = target[s] if abs(target[s] - pos[s-1]) >= BAND else pos[s-1]
    RENDITE
      R[s] = pos[s]*(r[s]-rf[s]) + rf[s] - COST*abs(pos[s]-pos[s-1]) - 0.005*max(pos[s]-1,0)/252

Evidenz:
- Harvey et al. (JPM 45(1), Fall 2018, S. 14-33, DOI 10.3905/jpm.2018.45.1.014; gelesen): "Equities All U.S." 1927-2017, Tagesdaten von Ken French. Sharpe unskaliert 0.40, skaliert je nach Halbwertszeit 0.48-0.51; brutto = netto auf zwei Nachkommastellen (10-Tage-HL: 0.4831 brutto, 0.4766 netto, Kosten 0.066 %/Jahr bei 10 % Vol). Regression der skalierten (20-Tage-HL) auf unskalierte Tagesrenditen: Alpha 0.64 bp/Tag, t = 3.05 (Newey-West, 30 Lags), R2 = 0.73. Vol-of-Vol 4.6 % (unskaliert) vs 1.8 % (skaliert). Umschlag: ca. 5 Round-Trips/Jahr bei reaktivstem, unter 1/Jahr bei traegstem Schaetzer. Kurtosis deutlich geringer, Max Drawdown geringer; Skewness mehrdeutig, weil auch der rechte Tail gekappt wird. Sharpe verbessert sich in allen 30-Jahres-Teilperioden AUSSER 1957-1987.
- Gleiches Paper, andere Assets: Anleihen 1963-2017 Sharpe sinkt durch Skalierung (Ursache ausschliesslich die Zeit vor 1980); 1988-2017 aehnlich, nur Vol-of-Vol niedriger. Bei den 50 Futures/Forwards und Kredit: Sharpe leicht besser bei Aktienindizes und Kredit, sonst aehnlich; Vol-of-Vol und Mean Shortfall fast durchgehend besser. Intraday-Vol (5-Minuten-Bars, S&P-500-Futures ab 1988) bringt leichte Verbesserung gegenueber Tagesdaten (nicht gratis).
- Cederburg et al. (JFE 138(1), 2020, S. 95-117; gelesen), Table 1, Aug 1926-Dez 2016, Monatsrebalancing, Varianz des Vormonats, c ex post: MKT Sharpe 0.42 -> 0.51, Differenz 0.09, p = 0.30 (nicht signifikant). Alpha-Zerlegung des MKT-Spanning-Alphas (4.63 %/Jahr): Return-Timing-Teil -0.24 %, Vol-Timing-Teil 4.87 %. Es wirkt also nur das Volatilitaets-Clustering, nicht eine Rendite-Vorhersage.
- Bongaerts/Kang/van Dijk (FAJ 2020; nur Abstract gelesen): "Konventionelles Vol-Targeting verbessert die Performance in globalen Aktienmaerkten nicht konsistent und kann zu deutlich groesseren Drawdowns fuehren." Das ist direkte Gegenevidenz zu dieser Strategie.

Ehrliche Bewertung:
- Nach-Publikations-Verfall: Harvey endet 2017, keine unabhaengige Replikation nach 2018 gefunden. Barroso-Detzel (Suchsnippet): Der Marktfaktor ist die einzige Ausnahme, die Kosten uebersteht, aber nur bei hoher Stimmung.
- Kosten: bei 10-bp-Annahmen und taeglichem Rebalancing kein Problem fuer SPY; das Risiko ist Hebel-Finanzierung und Steuer, nicht die Handelskosten.
- Tail-Risiken: Gap-Tage (19.10.1987 ist in Harvey sichtbar) kann kein Vol-Schaetzer verhindern. Mechanisch plausibel (NICHT gemessen von mir): Abwaertsspirale mit Re-Risking nach V-foermigen Erholungen. Ohne Hebel (CAP 1.0) bleibt vermutlich wenig Sharpe-Gewinn, nur Drawdown-Reduktion; das ist zu testen.
- Interessenkonflikt: Harvey-Koautoren sind bei Man AHL (Praktiker, Vol-Targeting ist Teil ihres Geschaefts).

### 3.2 riskmanaged_momentum_bsc - Risk-managed Momentum (Barroso & Santa-Clara)

Regel:

    DATEN: wml[d] = Tagesrendite des French-Momentumfaktors "Mom" (F-F_Momentum_Factor_daily, ab 1926-11-03), in Prozent / 100
    Fuer jeden Kalendermonat k mit letztem Handelstag m_k (Signal am Schluss m_k):
      rv      = sum(wml[d]**2 for die letzten 126 Handelstage bis inkl. m_k) / 126
      sig_mon = sqrt(21 * rv)                       # Monatsvol-Prognose, Null-Mittelwert
      w_k     = (0.12 / sqrt(12)) / sig_mon          # Ziel 12 % p.a., Gewicht fest fuer den ganzen Folgemonat
      (Hauptvariante OHNE Cap; Sens. Cap 2.0; Verteilung der w_k immer mit ausgeben)
    Anwendung: strat[d] = w_k * wml[d] fuer die Handelstage des Monats k+1 ab dem ZWEITEN Handelstag
               (der erste Handelstag laeuft noch mit w_{k-1}; Order am Schluss des ersten Handelstags)
    Kosten: 2 * COST * |w_k - w_{k-1}| (zwei Beine) PLUS Eigenkosten des Faktors (Umschlag, Leihe) - in der French-Reihe NICHT enthalten, separat ansetzen.

Quelle der Parameter: 126 Handelstage und 12 % Ziel stammen aus der Sekundaerquelle (Saias 2017, Gl. 7-8, "wie in Barroso und Santa-Clara"), die Originalformeln habe ich nicht gesehen (SSRN 403).

Evidenz:
- Barroso & Santa-Clara (JFE 116(1), 2015, S. 111-120, DOI 10.1016/j.jfineco.2014.11.010; NUR Abstract aus Suchsnippet): Momentum-Risiko ist stark zeitvariabel und vorhersagbar; Skalierung "eliminiert praktisch Crashes und verdoppelt fast die Sharpe-Ratio". Stichprobe laut Snippet 1927-2011.
- Cederburg et al. Table 1 (MOM, Jan 1927-Dez 2016, Monats-Rebalancing mit Vormonatsvarianz, c ex post): Sharpe 0.48 -> 0.99, Differenz 0.50, p = 0.00; Mittelwert 7.94 % -> 16.17 % bei gleicher Vol 16.39 %. Im Text: Die meisten signifikanten Sharpe-Gewinne in den 103 Strategien stammen aus den neun Momentum-Strategien; Vol-Management hilft bei jeder davon. Auch die Out-of-Sample-Kombination fuer MOM, ROE, BAB liefert grosse Nutzengewinne (Autorenaussage).
- Saias 2017 (MSc, eigene CRSP-Daten, Nov 1930-Dez 2015): Total Momentum Sharpe 0.49, skaliert 1.00. Nur als Plausibilitaetscheck, kein unabhaengiges Peer-Review.
- Wang & Yan (Einleitung, gelesen) nennen "Barroso/Santa-Clara und Daniel/Moskowitz: Momentum-Crashes praktisch eliminiert, Sharpe fast verdoppelt".

Ehrliche Bewertung:
- Staerkste statistische Evidenz der Familie, aber: (1) ein Long-Short-Faktor mit Leerverkaeufen; die French-Reihe ist reibungslos. (2) Barroso-Detzel (Suchsnippet): ausser Markt kein Faktor ueberlebt Kosten, Momentum eingeschlossen; eine internationale Studie 2024 (Suchsnippet) sagt "nur Markt und Momentum teilweise robust". (3) Der Faktor selbst hat nach der Veroeffentlichung der Momentum-Anomalie moeglicherweise Prämie verloren; nicht von mir geprueft.
- Frei handelbare Proxys sind schwach: MTUM (iShares MSCI USA Momentum, seit ca. 2013) minus SPY als Long-Short-Naeherung, oder Sektor-Momentum mit SPDR-Sektor-ETFs (XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY seit ca. Dezember 1998): Long Top 3 / Short Bottom 3 nach 12-1-Monats-Rendite, dann dieselbe Skalierung. Letzteres ist MEIN Design-Vorschlag, nicht aus einem Paper.
- Crash-Risiko bleibt: Die Skalierung reagiert mit Verzoegerung (126-Tage-Fenster); der Wechsel von hoher zu niedriger Vol nach einem Crash laesst die Strategie die Erholung zum Teil verpassen (mechanisch plausibel; Zahl nicht gefunden).

### 3.3 balanced_6040_twolevel_voltarget - Vol-Targeting auf 60/40 (Asset-Ebene + Portfolio-Ebene, Harvey et al.)

Regel:

    ASSETS: E = SPY (Aktien), B = IEF (US-Treasuries 7-10J; Langfrist: synthetisch aus FRED DGS10 nach Harvey Fn. 6)
    TARGET_ASSET = 0.10, TARGET_PORT = 0.10, HL = 20, WARMUP = 270, GROSS_CAP = 2.0 (EIGENE Annahme; Hebel finanziert zu RF + 0.5 %)
    Je Asset i in {E,B}: sig_i[t] aus Null-Mittelwert-EWMA wie in 3.1 (Excess-Renditen)
      x_i[s] = TARGET_ASSET / sig_i[s-2]                      # Asset-Ebene
      z_i[s] = x_i[s] * exz_i[s]                              # skalierte Excess-Rendite
    P[s] = 0.6*z_E[s] + 0.4*z_B[s]                            # 60/40 in RISIKO-Termen (beide Sleeves haben 10 % Vol)
    sig_P[t] = sqrt(252 * EWMA_HL20(P[t]**2))
    y[s] = TARGET_PORT / sig_P[s-2]                           # Portfolio-Ebene
    Gewichte: wE[s] = y[s]*0.6*x_E[s], wB[s] = y[s]*0.4*x_B[s]; falls wE+wB > GROSS_CAP: beide proportional auf GROSS_CAP skalieren
    Rendite: R[s] = wE[s]*exz_E[s] + wB[s]*exz_B[s] + rf[s] - Kosten(|Delta wE| + |Delta wB|) - Finanzierung(max(wE+wB-1,0))
    Handel: Signale mit 2 Tagen Verzoegerung wie in 3.1 (Signal Schluss s-2, Order Schluss s-1), tagliche Neuberechnung, No-Trade-Band 0.05 je Asset.
    Vergleich: (a) 60/40 mit Risikogewichten ohne Scaling, (b) nur Asset-Ebene, (c) beide Ebenen, (d) 60/40 nach Kapitalgewichten.

Evidenz:
- Harvey et al. (gelesen), Sektion "Portfolios": Drei Varianten (ungescaled; nur Asset-Ebene; Asset- plus Portfolio-Ebene) fuer ein 60/40-Aktien-Anleihen-Portfolio (S&P-500- und 10J-T-Note-Futures, 1988-2017). Text: Sharpe, Vol-of-Vol und Mean Shortfall verbessern sich durch Asset-Skalierung und weiter durch die zweite Skalierung auf Portfolioebene; die Verbesserung im linken Tail ist groesser als die Reduktion im rechten Tail. Zahlenwerte der Exhibit 16 sind im PDF-Text nicht lesbar: NICHT gefunden. Risk-Parity-Portfolio (Aktien/Anleihen/Kredit/Rohstoffe) wird nur im Online-Supplement behandelt (nicht gesehen).
- Warnung im selben Paper: Anleihen-Vol-Targeting senkt den Sharpe 1963-2017 (nur wegen 1960-1980 mit niedriger Vol und negativer Rendite), nach 1988 ueber eine einzige Zinsrueckgangsphase gemessen.

Ehrliche Bewertung:
- Stichprobe 1988-2017 ist eine lange Anleihen-Hausse mit negativer Aktien-Anleihen-Korrelation. 2022 (gleichzeitiger Absturz von Aktien und Anleihen) wurde in der Literatur, die ich gesehen habe, nicht untersucht: NICHT gefunden. Der Portfolio-Level-Schritt soll genau den Korrelationsanstieg abfangen (Harvey), das ist ein Testpunkt.
- Hebel auf Anleihen (IEF-Vol ca. 6-7 %, also Hebel > 1.4 fuer 10 % Ziel; Zahl aus Gedaechtnis) macht die Finanzierung entscheidend.
- Weniger Staerke als 3.1, weil die Zusatzevidenz fuer die Portfolio-Ebene nur ein einziges Paper (praktiker-gesponsert) ist.

### 3.4 downside_vol_fixedweight_market - Downside-Vol-Skalierung mit festem 50/50-Mix (Wang & Yan)

Regel:

    DATEN: f[d] = French Mkt-RF (Tag), RF[d]; ab 1926-07-01. Alternative ab 1993: SPY minus RF.
    Fuer Monat k (Tage j in k, Signal am Schluss des letzten Handelstags von k):
      neg = [f[j] for j in k if f[j] < 0]
      if len(neg) < 3: neg = negative Tagesrenditen aus Monat k UND Monat k-1 zusammen   # Regel aus Wang-Yan
      sd_k    = sqrt(sum(x**2 for x in neg))             # Wang-Yan Gl. (3), Summe, nicht Mittel
      inv_k   = 1 / sd_k
      c_k     = 1 / mean(inv_s for s = 1..k)             # expandierend (Echtzeit-Variante; Paper waehlt c ex post): mittleres Managed-Gewicht = 1
      w_dn_k  = min(3.0, c_k * inv_k)                    # Cap 3.0 ist EIGENE Annahme
      W_k     = 0.5 * 1.0 + 0.5 * w_dn_k                 # fester 50/50-Mix aus ungemanagt und managed (Wang-Yan: "z.B. 50 % / 50 %")
    Position im Monat k+1: Exposure W_k in Mkt (Rest bzw. Hebel zu RF), Wechsel am Schluss des ersten Handelstags von k+1.
    Rebalancing: einmal pro Monat. Kosten 2 bp einseitig auf |Delta W|.
    Kontrolle: Gleiches mit Gesamtvol statt Downside-Vol (Wang-Yan: Zielvergleich), und ungemanagtes Buy&Hold.

Evidenz (Wang & Yan, J. Banking & Finance 131 (2021) 106198, gelesen; Stichprobe wie Moreira-Muir, bis Dez 2016 hier nicht explizit verifiziert):
- MKT Spanning-Alpha: total-vol-managed 3.34 %/Jahr (t = 3.39), downside-vol-managed 4.83 %/Jahr (t = 4.10).
- Anomalien (94): positives Alpha bei total-vol 62/94, bei downside-vol 89/94.
- Echtzeit-Kombination (expandierende Gewichte) schlaegt die ungemanagte Variante bei total-vol in nur 50 von 103, bei downside-vol in 70 von 103. Feste Gewichte: total-vol 64-68, downside-vol 80-81 von 103.
- Kosten (Fliesstext, Tabelle 4 verwuerfelt): total-vol-Alphas im Mittel positiv bis 14 bp, downside-vol bis 25 bp; bei 50 bp meist negativ. Downside-vol hat hoeheren Umschlag.
- Mechanismus laut Autoren: Downside-Vol sagt zusaetzlich zukuenftige RENDITEN voraus (Return Timing), nicht nur zukuenftige Vol.
- Zahl fuer MKT Out-of-Sample Sharpe in Wang-Yan: nicht gefunden.

Ehrliche Bewertung:
- Dieselben Autoren (Wang, Yan) haben Cederburg et al. geschrieben und sind hier die einzige Quelle; keine unabhaengige Replikation gefunden. Die Downside-Formulierung ist eine von vielen moeglichen Varianten: Data-Mining-Risiko.
- Die Spanning-Alphas sind In-Sample; die belastbare Aussage ist nur die Anzahl der Echtzeit-Faelle (70 bzw. 80-81 von 103), nicht eine Marktrendite-Prognose.
- Fuer den reinen Marktfaktor ist der Edge gegenueber 3.1 unklar; Test lohnt, weil Monatsrebalancing billiger ist.

### 3.5 conditional_voltarget_extremes - Konditionales Vol-Targeting nur in Extremzonen (Bongaerts/Kang/van Dijk) - REGEL NICHT VERIFIZIERT

WARNUNG: Das Paper-Abstract nennt nur das Prinzip ("Exposure nur in extremen Hoch- und Niedrigvol-Zustaenden anpassen"); die genaue Regel (Schwellen, Fenster, Cap) habe ich NICHT gefunden. Die Parameter unten sind ein DESIGN-VORSCHLAG von mir zum Testen der Idee, nicht die Paper-Regel. Das ist als Hypothese zu behandeln, nicht als Replikation.

Regel (Design-Vorschlag):

    DATEN: Tagesrenditen des Index (SPY oder ^GSPC); Warm-up 756 Handelstage
    Am letzten Handelstag t des Monats (Schluss):
      sig[t] = sqrt(252 * mean(r[t-20..t]**2))             # 21-Tage-Realized-Vol
      p[t]   = Perzentil von sig[t] in der EXPANDIERENDEN Historie sig[s <= t]
      sig_med[t] = expandierender Median von sig
      if p[t] >= 0.80: w = max(0.25, sig_med[t] / sig[t])   # Hochvol-Zone: reduzieren
      elif p[t] <= 0.20: w = min(1.25, sig_med[t] / sig[t]) # Niedrigvol-Zone: leicht hebeln
      else: w = 1.0                                         # sonst nichts tun (niedriger Umschlag)
    Handel am Schluss des naechsten Handelstags; Rest in RF; Kosten 2 bp einseitig.
    Schwellen 0.20/0.80 und Caps 0.25/1.25 sind NICHT aus dem Paper.

Evidenz:
- Bongaerts/Kang/van Dijk, FAJ 76(4), 2020, S. 54-71, DOI 10.1080/0015198X.2020.1790853 (nur Abstract gelesen, repub.eur.nl): Konventionelles Vol-Targeting verbessert Aktienmaerkte nicht konsistent und kann Drawdowns deutlich vergroessern; das konditionale Verfahren verbessert laut Autoren konsistent Sharpe, Drawdown und Tail-Risiko bei niedrigem Umschlag und Hebel. Daten laut Suchsnippet: 10 groesste Aktienmaerkte, Januar 1972-Maerz 2019 (Snippet, nicht verifiziert). Konkrete Sharpe-/Drawdown-/Umschlagszahlen: nicht gefunden.

Ehrliche Bewertung:
- Autoren-eigene Evidenz, keine Replikation gefunden. Fuer Echtzeit-Tests sind die Schwellen leicht zu overfitten; deshalb nur als Hypothese mit fest vorab gewaehlten Parametern (Projektregel 3) testen.
- Free-Data-Hinweis: Das Paper nutzt 10 Laender. Gratis-Proxys: Indexpreisreihen ohne Dividenden (^GSPC ab 1927-12-30, ^N225, ^FTSE, ^GDAXI, ^FCHI, ^HSI, ^GSPTSE; Startdaten je Index ca., nicht verifiziert) oder iShares-Laender-ETFs (EWJ, EWG, EWU, EWC, EWA, EWQ, EWL, ab ca. 1996). Preisindizes unterschaetzen die Rendite, sind aber fuer relative Tests brauchbar.

## 4. Weitere gesehene Arbeiten (nicht als eigene Strategie gefuehrt)

- Moreira & Muir (J. Finance 72(4), 2017, S. 1611-1644; NBER w22208, April 2016, rev. Juni 2016; NBER-Abstract gelesen): Managed Portfolios mit weniger Risiko bei hoher Vol erzeugen grosse Alphas und heben Sharpe-Ratios; erklaerter Mechanismus: Aenderungen der Vol sind nicht proportional zu Aenderungen der erwarteten Rendite. Zahlen im NBER-Abstract nicht enthalten; ein Suchsnippet nennt zur frueheren Arbeitspapierfassung "Alpha 4.9 %, Appraisal Ratio 0.33, +25 % Sharpe fuer den Markt" (Suchsnippet, nicht verifiziert). Ihre Regel (Varianz-Skalierung, Vormonat, c ex post) ist die Grundlage von Cederburg Gl. (1) und wurde hier durch die Vol-Skalierung (weniger Umschlag, Wang-Yan Fn. 7) ersetzt.
- DeMiguel, Martin-Utrera, Uppal, "A Multifactor Perspective on Volatility-Managed Portfolios" (Arbeitspapier 10.05.2022 gelesen: Abstract und Einleitung; JF 2024 laut Suchsnippet, Wiley 403): Konditionales Multi-Faktor-Portfolio, dessen Faktorgewichte sich mit der Marktvolatilitaet aendern, optimiert unter Transaktionskosten, mit Netting-Effekt ("Trading Diversification"). Out-of-Sample (Jan 1977-Dez 2020, Daten ab Jan 1967) und netto: Sharpe ca. 16 % ueber dem unkonditionalen Multi-Faktor-Portfolio und ca. 10 % ueber dem konditionalen Fixed-Weight-Portfolio von Moreira-Muir. Ohne Netting haben vier der neun gemanagten Faktoren negative Netto-Rendite. Nicht als Strategie gefuehrt, weil: Mean-Variance-Optimierung mit Kostenterm und expandierendem Fenster ist keine unzweideutige Kurzregel, die ich ohne den Volltext sauber kodieren koennte. Als Phase-2-Kandidat im Quant-Lab sinnvoll (Faktoren aus French-Bibliothek: Mkt-RF, SMB, HML, RMW, CMA, Mom, taeglich ab 1963/1926).
- Barroso & Detzel (JFE 140(3), 2021, S. 744-767, DOI 10.1016/j.jfineco.2021.02.009; Suchsnippet/Abstract-Ebene und DeMiguel-Einleitung): Nach Kosten bringt Vol-Management bei allen Faktoren ausser dem Markt null abnormale Rendite und senkt die Sharpe-Ratio signifikant, auch mit sechs Kostenminderungsstrategien. Die gemanagte Marktposition behaelt ihre Rendite, konzentriert in leicht arbitrierbaren Aktien, und nur bei hoher Stimmung.

## 5. Offene Punkte / Vorschlaege fuer docs/HYPOTHESEN.md

- H1 (3.1): Vol-Target-SPY (TARGET 0.12, HL 20, CAP 1.0, 2 bp) hat im Zeitraum 1993-2026 einen mindestens 25 % kleineren Max-Drawdown als SPY Buy&Hold und eine Sharpe-Ratio mindestens gleich einer Konstant-Mix-Kontrolle mit gleicher mittlerer Exposure. Abbruch, wenn die Sharpe-Differenz in 2 von 3 Teilperioden (1993-2007, 2008-2019, 2020-2026) negativ ist. (Die 25 % sind ein Vorschlag, nicht aus der Literatur.)
- H2 (3.2): Risk-managed Mom (French-Reihe) behaelt nach Abzug von 2*COST*|Delta w| und einer Platzhalter-Kostenannahme fuer die Faktor-Eigenkosten (Vorschlag: 30-60 bp/Jahr, KEIN Literaturwert) noch positive Sharpe-Differenz. Abbruch bei Differenz <= 0 in 2012-2026.
- H3 (3.3): Ob die 2-Ebenen-Skalierung 2022 den Drawdown des 60/40 senkt (Literatur sagt dazu nichts).
- Daten-Checkliste vor dem Kodieren: Startdaten laut Gedaechtnis (SPY ab ca. 1993-01, IEF/TLT ab ca. 2002-07, MTUM ab ca. 2013-04, SPDR-Sektor-ETFs ab ca. 1998-12, ^IRX ab 1960, ^VIX ab 1990, FRED DGS10 ab 1962, French daily Faktoren ab 1926-07 bzw. Mom ab 1926-11) beim ersten Download verifizieren.

## 6. Quellen-URLs (alle tatsaechlich aufgerufen)

- Harvey et al. 2018: https://people.duke.edu/~charvey/Research/Published_Papers/P135_The_impact_of.pdf
- Cederburg et al. 2020: https://www.lehigh.edu/~xuy219/research/COWY.pdf
- Wang & Yan 2021: https://www.lehigh.edu/~xuy219/research/Downside.pdf
- Moreira & Muir (NBER): https://www.nber.org/papers/w22208
- Saias 2017 (Replikation BSC, MSc-These): https://repositorio.ucp.pt/bitstreams/be7fa383-f5c7-406b-b753-4ea8e49d5d23/download
- Bongaerts/Kang/van Dijk (Abstract): https://repub.eur.nl/pub/130215
- DeMiguel/Martin-Utrera/Uppal (Arbeitspapier): http://wp.lancs.ac.uk/fofi2022/files/2022/08/FoFI-2022-076-Alberto-Martin-Utrera.pdf
- Nur ueber Suchtreffer gesehen (nicht abgerufen oder 403):
  - Barroso & Santa-Clara: https://ciencia.ucp.pt/en/publications/momentum-has-its-moments/ und SSRN 2041429
  - Barroso & Detzel: https://www.sciencedirect.com/science/article/pii/S0304405X21000775
  - Wiley JF 2024 (DeMiguel et al.): https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13395
  - "Disappearing profitability of volatility-managed equity factors" (Titel im Suchtreffer, nicht gelesen): https://www.sciencedirect.com/science/article/abs/pii/S1386418123000551
  - "On the performance of volatility-managed equity factors - International and further evidence" (2024, Suchsnippet): https://www.sciencedirect.com/science/article/pii/S092753982400094X
  - Alpha Architect (403): https://alphaarchitect.com/conditional-volatility-targeting/
- Datenquellen: Ken French Data Library https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html (Datei-Namen aus Gedaechtnis: F-F_Research_Data_Factors_daily, F-F_Momentum_Factor_daily); FRED https://fred.stlouisfed.org (DGS10, laut Harvey Fn. 5 als Quelle der 10J-Renditen); Yahoo Finance via yfinance.
