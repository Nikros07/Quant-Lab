# Familie METHODIK - Overfitting, Replikations-Verfall, Backtest-Statistik

Stand: 2026-10-12. Quant-Research-Analyst-Lauf (Workflow "research:method"). Sprache: Deutsch (ASCII-Umschrift wie die anderen Familien-Dateien).
Alle Zahlen stammen aus Seiten/PDFs, die in dieser Session wirklich abgerufen und (soweit PDF) lokal per pdftotext gelesen wurden,
oder aus eigenen Rechnungen (klar als "EIGENER CHECK" markiert). Was nicht gefunden wurde, steht als "nicht gefunden".

WICHTIG: Diese Familie enthaelt KEINE Handelsstrategie. Die "Strategien" unten sind Pruefstand-Module (Gates), die jeder Kandidat
aus den anderen Familien durchlaufen muss, bevor er Kapital sieht. Sortierung = erwartete Robustheit des Moduls (bestes zuerst).

## 0. Kurzfazit (ehrlich)

1. Die Literatur ist sich einig, dass ein roher In-Sample-Backtest nichts beweist. Uneinig ist sie ueber das AUSMASS:
   - Pessimisten: Harvey/Liu/Zhu (RFS 2016): neue Faktoren brauchen t > 3.0 (Bonferroni-Schwelle 3.78 bei 316 Faktoren, BHY 3.18-3.39).
     Hou/Xue/Zhang (RFS 2020): von 447 Anomalien sind bei strenger Konstruktion (NYSE-Breakpoints, wertgewichtet) 64 % bei 5 % unbedeutend, 85 % mit t >= 3.
   - Optimisten: Jensen/Kelly/Pedersen (JF 2023): die meisten Faktoren replizieren. Chen/Zimmermann (arXiv 2022): Publikationsbias nur 10-15 % des In-Sample-Mittels, FDR < 10 %.
   - Versoehnung: "replizierbar im Papier-Portfolio" ist nicht "investierbar nach Kosten". Chen/Velikov (JFQA 2023, nur Suchtreffer-Zusammenfassung gesehen):
     durchschnittliche Anomalie netto nach Spread, Post-Publikation und Moderne nur ca. 4 bp/Monat (204 Anomalien); Working-Paper-Fassung 8 bp/Monat (120 Anomalien).
2. McLean/Pontiff (JF 2016, Volltext gelesen): 97 Praediktoren, Rendite -26 % out-of-sample (Obergrenze fuer Data-Mining-Effekt), -58 % nach Publikation,
   also ca. -32 Prozentpunkte "Publikationseffekt". Regel fuer das Lab: publizierte Idee = In-Sample-Rendite mal 0.42 als Erwartung VOR Kosten.
3. Fuer das Lab ist die wichtigste Zahl eine EIGENE Rechnung: mit ca. 18 Jahren ETF-Daten (2008-2026) und N = 40 unabhaengigen Versuchen braucht ein Kandidat
   eine annualisierte Sharpe von ca. 0.90 (bei Normalrenditen), damit der Deflated Sharpe >= 0.95 wird; bei N = 200 ca. 1.04. SPY hat dort ca. 0.57 (Wert aus tsmom.md).
   Heisst: im 18-Jahres-ETF-Fenster kann fast nichts "bewiesen" werden. Statistische Macht kommt nur aus langen Reihen (Ken French ab 1926, ^GSPC ab 1927)
   oder aus sehr grossen Effekten. NO TRADE bleibt der erwartbare Ausgang - das ist laut CLAUDE.md ein gueltiges Ergebnis.
4. Die Bausteine PSR, Deflated Sharpe, stationaerer Bootstrap und PBO existieren schon in `qlab/stats.py` und stimmen mit den Papier-Formeln ueberein (siehe Abschnitt 6).
   FEHLEND: Haircut-Sharpe (Bonferroni/Holm/BHY), Min-Backtest-Length-Vorfilter, familienweiter Test (Reality Check / SPA / Romano-Wolf StepM),
   ein persistentes Trial-Register (Matrix aller je getesteten Varianten) - ohne das ist jedes N geraten.

## 1. Methodik und Datenlage dieser Session

Wirklich abgerufen, Volltext lokal extrahiert und gelesen:
- Bailey/Lopez de Prado, The Deflated Sharpe Ratio (JPM 2014, Fassung 31.07.2014): https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf
  Griechische Symbole gingen in der Textextraktion verloren (Eq. 2 unleserlich); Eq. (1)/(6) und der Python-Code in Snippet 1 sind aber lesbar,
  und das Zahlenbeispiel (0.9505 bei N=46, 90 % bei N=100, N=88 bei Normalrenditen) habe ich mit der rekonstruierten Formel EXAKT reproduziert (siehe Abschnitt 7).
- Bailey/Borwein/Lopez de Prado/Zhu, The Probability of Backtest Overfitting (Fassung Feb 2015): https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf
- Bailey/Borwein/Lopez de Prado/Zhu, Pseudo-Mathematics and Financial Charlatanism (Notices AMS 2014, Fassung 01.04.2014): https://carmamaths.org/jon/backtest.pdf
- Harvey/Liu/Zhu, ... and the Cross-Section of Expected Returns (RFS 29(1), 2016): https://people.duke.edu/~charvey/Research/Published_Papers/P118_and_the_cross.PDF
- Harvey/Liu, Backtesting (JPM 41(1), Herbst 2015): https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF
- McLean/Pontiff, Does Academic Research Destroy Stock Return Predictability? (JF, Feb 2016; gelesen wurde die "Forthcoming"-Fassung): https://counterpointfunds.com/wp-content/uploads/2017/07/PredictabilityMcleanPontiff.pdf
Abstract/Seitenzusammenfassung gesehen (kein Volltext):
- Hou/Xue/Zhang, Replicating Anomalies (NBER w23394, 2017; RFS 2020): https://www.nber.org/papers/w23394
- Jensen/Kelly/Pedersen, Is There a Replication Crisis in Finance? (NBER w28432, 2021; JF 78(5) 2023): https://www.nber.org/papers/w28432
- Chen/Zimmermann, Publication Bias in Asset Pricing Research (arXiv 2209.13623): https://arxiv.org/abs/2209.13623
Nur Suchtreffer-Zusammenfassung (Zahlen mit Vorsicht, Volltext NICHT gesehen):
- Chen/Velikov, Zeroing In on the Expected Returns of Anomalies (JFQA 58(3), 2023; FEDS 2020-039): https://www.federalreserve.gov/econres/feds/zeroing-in-on-the-expected-returns-of-anomalies.htm
- White (2000), A Reality Check for Data Snooping, Econometrica 68(5), 1097-1126: https://www.econometricsociety.org/publications/econometrica/2000/09/01/reality-check-data-snooping
- Hansen (2005), A Test for Superior Predictive Ability, JBES 23, 365-380 (Working-Paper-Titel "An Unbiased and Powerful Test for Superior Predictive Ability": https://ideas.repec.org/p/bro/econwp/2001-06.html)
- Romano/Wolf (2005), Stepwise Multiple Testing as Formalized Data Snooping, Econometrica 73(4), 1237-1282: https://www.econometricsociety.org/publications/econometrica/2005/07/01/stepwise-multiple-testing-formalized-data-snooping (Working Paper: https://econ-papers.upf.edu/papers/712.pdf)
- Politis/Romano (1994), The Stationary Bootstrap, JASA 89(428), 1303-1313 (Katalogeintrag): https://gnosis.library.ucy.ac.cy/handle/7/57533
- Software-Referenz: arch-Dokumentation (SPA, StepM, RealityCheck, MCS, StationaryBootstrap; Seite nennt nur Autor/Jahr, keine Formeln): https://arch.readthedocs.io/en/latest/multiple-comparison/multiple-comparison-reference.html
Nicht abrufbar / nicht versucht: AQR-Seiten, Alpha Architect, Quantpedia, Hoffstein/Newfound, Allocate Smartly (Budget von ca. 15 Abrufen verbraucht, davon einer 403:
https://www.ams.org/notices/201405/rnoti-p458.pdf). Daher KEINE Zahlen von dort. Nicht abgerufen, nur als Suchtreffer-Titel gesehen: arXiv 2607.06502 "What Useful Alphas?" (Juli 2026) - keine Aussage daraus.
Nicht verfuegbar: Politis/White (2004) und Patton/Politis/White (2009) zur optimalen Blocklaenge, Ledoit/Wolf (2008) Sharpe-Differenz-Test - nur aus eigenem Wissen, hier NICHT geprueft.

Hinweis zu Formeln: Alles, was unten mit "VERIFIZIERT" steht, wurde im abgerufenen Text gesehen. "ABGELEITET" = von mir aus verifizierten Bausteinen umgestellt.
"AUS GEDAECHTNIS" = Standardverfahren, nicht gegen Volltext geprueft - vor Implementierung gegen die Quelle/arch-Quellcode pruefen.

## 2. Exakte Formeln

### 2.1 Probabilistic Sharpe Ratio (PSR) und Deflated Sharpe Ratio (DSR) - Bailey/Lopez de Prado 2014
Alle Sharpe-Werte PRO PERIODE (nicht annualisiert); T = Anzahl Renditebeobachtungen; g3 = Schiefe; g4 = Kurtosis (NICHT Excess, Normal = 3).

    PSR(SR*) = Phi( (SR_hat - SR*) * sqrt(T-1) / sqrt(1 - g3*SR_hat + (g4-1)/4 * SR_hat^2) )          # Phi = Standardnormal-CDF

    E[max_N] (in SR-Einheiten, Nullhypothese wahrer SR = 0) :
      SR0 = sqrt(V[SR_n]) * ( (1-gamma) * Phi^-1(1 - 1/N)  +  gamma * Phi^-1(1 - 1/(N*e)) )           # gamma = 0.5772156649 (Euler-Mascheroni)
      V[SR_n] = Varianz der SR-Schaetzer ueber die N Versuche, N = Zahl UNABHAENGIGER Versuche

    DSR = PSR(SR0)

Status: SR0-Formel und Python-Code VERIFIZIERT (Eq. 1/6, Snippet 1 im PDF: maxZ=(1-emc)*norm.ppf(1-1/N)+emc*norm.ppf(1-1/(N*e)); Ergebnis = mu + sigma*maxZ).
PSR/DSR-Bruch: Struktur im Text beschrieben (PSR mit Schiefe/Kurtosis, DSR = PSR mit Schwelle SR0); Symbole im PDF-Text verloren, aber durch exakte
Reproduktion des Papier-Beispiels bestaetigt (Abschnitt 7). Papier-Beispiel: Erwartung E[max] fuer N=10 und sigma=1 ist 1.57 (im Pseudo-Mathematics-Paper genannt, von mir reproduziert: 1.5746).

Beispiel im DSR-Paper (Treasury-Auktionen): annualisierte SR 2.5, 5 Jahre Tagesdaten (T=1250), V[SR] = 0.5 (annualisiert), Schiefe -3, Kurtosis 10, N=100 -> DSR ca. 0.90 (Investor lehnt ab);
bei N=46 waere DSR = 0.9505; mit Normalrenditen (Schiefe 0, Kurtosis 3) reicht N=88 fuer 0.95. (Im PDF-Text sind die Eingabewerte teils unleserlich; ich habe sie aus der Konsistenz rekonstruiert.)

Anzahl unabhaengiger Versuche aus M korrelierten (Appendix A.3): Mittlere Korrelation rho_bar; die Aussagen im Text: rho_bar -> 1 gibt N -> 1, rho_bar -> 0 gibt N -> M, dazwischen wird interpoliert
(Eq. 9; Symbole verloren). Lineare Interpolation N_eff = rho_bar + (1 - rho_bar)*M ist damit konsistent - ABGELEITET, vor Nutzung gegen das Papier pruefen.
Bailey/LdP warnen selbst: mit M > T ist die Korrelationsmatrix schlecht konditioniert, rho_bar ist dann selbst ueberangepasst; Alternative: Dimensionsreduktion/Clustering oder Entropie-Verfahren.
Stoppregel im Papier: 1/e-Regel (ca. 37 % der theoretisch begruendbaren Konfigurationen zufaellig testen, dann bis zum ersten besseren weitermachen).

### 2.2 Minimum Track Record Length (MinTRL) - ABGELEITET
PSR >= 1 - alpha nach n umgestellt (gleicher Nenner wie PSR):

    n* = 1 + [ 1 - g3*SR_hat + (g4-1)/4 * SR_hat^2 ] * ( Z_(1-alpha) / (SR_hat - SR*) )^2

EIGENER CHECK (Normalrenditen, SR* = 0, alpha = 5 %, monatlich): annualisierte SR 0.3 -> 363 Monate (30.3 Jahre); 0.5 -> 132 Monate (11.0 Jahre); 0.8 -> 53 Monate (4.4 Jahre); 1.0 -> 35 Monate (2.9 Jahre).
Das ist die Mindestlaenge fuer EINEN Test ohne Mehrfachtest.

### 2.3 Minimum Backtest Length (MinBTL) - Bailey/Borwein/LdP/Zhu 2014 (Theorem 3.1, VERIFIZIERT)

    MinBTL (Jahre) = ( ( (1-gamma)*Phi^-1(1-1/N) + gamma*Phi^-1(1-1/(N*e)) ) / E[max_N] )^2  <  2*ln(N) / E[max_N]^2

E[max_N] = annualisierte In-Sample-Sharpe, die durch reines Rauschen unter N unabhaengigen Versuchen zu erwarten ist. Papier: bei E[max]=1 reichen 5 Jahre nur fuer N <= 45
(und "nach nur 7 Versuchen" 2 Jahre). EIGENER CHECK: N=45 -> 4.998 Jahre, N=7 -> 1.92 Jahre, N=100 -> 6.40 Jahre, N=1000 -> 10.6 Jahre (die einfache Schranke 2 ln N ist deutlich laxer: 7.6 Jahre bei N=45).
Papier betont: MinBTL ist notwendig, nicht hinreichend. Unabhaengigkeit der Versuche macht die Schaetzung konservativ.
Ebenfalls im Papier: Overfitting erzeugt NEGATIVE Out-of-Sample-Leistung, sobald die Strategie "Gedaechtnis" hat (serielle Abhaengigkeit, z.B. AR(1) mit Halbwertszeit) - ohne Gedaechtnis ist die OOS-Erwartung nur null.

### 2.4 Haircut-Sharpe - Harvey/Liu 2015 (Backtesting, VERIFIZIERT)
Sharpe -> t: Sharpe pro Periode = t / sqrt(T). Monatsdaten: SR_m = SR_ann/sqrt(12); t = SR_m * sqrt(T_monate).

    p_S    = Pr( |t_{T-1}| > t )                       (zweiseitig, Student-t mit T-1 Freiheitsgraden)
    p_M    = 1 - (1 - p_S)^N       (N unabhaengige Tests; allgemeiner Fall: Bonferroni/Holm/BHY, siehe 2.5)
    HSR    = Sharpe, die p_M als EINZELtest-p-Wert haette:  Pr(|t_{T-1}| > t_adj) = p_M  ->  HSR_ann = t_adj/sqrt(T) * sqrt(12)
    Haircut = (SR - HSR)/SR

Papier-Beispiel: 20 Jahre Monatsrenditen (T=240), annualisierte SR 0.75: p_S = 0.0008; N=200 -> p_M = 0.15, HSR = 0.32, Haircut ca. 60 %.
EIGENER CHECK mit Student-t: p_S = 0.00093, p_M(N=200) = 0.169, HSR = 0.308, Haircut 58.9 % (kleine Abweichung, Papier rundet/benutzt evtl. leicht andere t-Berechnung).
Weitere Papier-Aussagen: Haircut ist NICHTLINEAR: bei annualisierter SR < 0.4 fast immer > 50 % (teils viel mehr), bei SR > 1.0 hoechstens 25 %. Die Faustregel "50 % abziehen" nennen die Autoren einen schweren Fehler.
HL korrigieren die Sharpe der Beispiele fuer Autokorrelation (Matlab-Funktion Haircut_SR, Eingaben u.a. Frequenz, annualisiert ja/nein, Autokorrelation-korrigiert ja/nein, Anzahl Tests).
Hinweis der Autoren: Sharpe ist nur bei normalen Renditen ein gutes Mass; negative Schiefe (Short-Vol) macht hohe SR verdaechtig.

### 2.5 Mehrfachtest-Korrekturen - Harvey/Liu/Zhu 2016 (VERIFIZIERT, Sektion 3.4)
M = Zahl der Tests, p_(1) <= ... <= p_(M) geordnete Roh-p-Werte.

    Bonferroni (FWER):  p_i^Bonf = min( M * p_i , 1 )
    Holm (FWER, schrittweise abwaerts): p_(j)^Holm = min( max_{i<=j} (M - i + 1) * p_(i) , 1 )
    BHY (FDR, schrittweise aufwaerts): p_(M)^BHY = p_(M);  p_(i)^BHY = min( p_(i+1)^BHY , M * c(M) / i * p_(i) )  fuer i <= M-1
                                       c(M) = sum_{j=1..M} 1/j   (Benjamini-Yekutieli, gueltig bei beliebiger Abhaengigkeit); c(M)=1 ist die laxe Benjamini-Hochberg-Variante
    Entscheidung: Hypothese i verwerfen (Faktor "entdeckt"), wenn p^adj <= Niveau (HLZ: 5 % bei Bonferroni/Holm, FDR 1 % oder 5 % bei BHY).

Schwellen (HLZ, 316 Faktoren): Bonferroni-t startet bei 1.96 und erreicht 3.78 im Jahr 2012 (4.00 im Jahr 2032, Extrapolation); BHY stabilisiert bei 3.39 (FDR 1 %), 2.78 (FDR 5 %, 2012);
bei ergaenzten fehlenden Tests (M > R) BHY 3.68 (1 %) / 3.18 (5 %) -> "Mindestschwelle 3.18"; mit c(M)=1: 3.05 (5 %) / 3.17 (1 %). Modell mit Korrelationen: ca. 3.9 (FWER 5 %) bzw. 3.0 (FDR 1 %).
Fazit der Autoren: neuer Faktor braucht t > 3.0; auch theoriegetriebene Faktoren nicht mehr mit t = 2.0.
EIGENER CHECK Bonferroni (zweiseitig 5 %, Normal): M=20 -> 3.02; M=100 -> 3.48; M=316 -> 3.78 (stimmt mit HLZ); M=1000 -> 4.06.

### 2.6 Probability of Backtest Overfitting (PBO), CSCV - Bailey/Borwein/LdP/Zhu (VERIFIZIERT, Alg. 2.3)
1. Matrix M (T x N): Gewinn/Verlust-Reihen von N Konfigurationen, synchron.
2. In S (gerade) gleich lange Zeilenbloecke M_s teilen (Papier-Beispiel S=16).
3. Alle C(S, S/2) Kombinationen J bilden: Training = Bloecke in J in Originalordnung, Test = Komplement.
4. Pro Kombination: n* = Konfiguration mit bester In-Sample-Kennzahl; relative OOS-Rang w = rang(n*) / (N+1) in (0,1); Logit lambda = ln( w / (1 - w) ).
5. PBO = Anteil der Kombinationen mit lambda <= 0 (Integral der Logit-Dichte von -inf bis 0). Lambda > 0 heisst: IS-Sieger liegt OOS ueber dem Median.
Zusatzgroessen im Papier: Performance Degradation (Regression OOS-Kennzahl auf IS-Kennzahl), OOS-Verlustwahrscheinlichkeit, stochastische Dominanz (1./2. Ordnung).
Entscheidungsvorschlag im Papier: "Neyman-Pearson-ueblich" Modelle mit PBO > 0.05 verwerfen. Beispiele im Papier: PBO 74 % (ueberangepasstes Beispiel), 0.04 % (reale Strategie).
Hinweis: Der PDF-Text nennt fuer S=16 "12,780" Kombinationen; richtig ist C(16,8) = 12,870 (EIGENER CHECK; qlab/stats.py nutzt combinations() und ist damit korrekt).
PBO bewertet den AUSWAHLPROZESS aus N Varianten, nicht die Existenz eines Edge: eine einzelne Strategie ohne Varianten hat kein PBO.

### 2.7 Reality Check / SPA / StepM / Stationaerer Bootstrap (AUS GEDAECHTNIS, nur Bibliografie verifiziert)
Gesehen: arch-Seite beschreibt SPA (Hansen 2005) als Test mit H0: max_i E[L_i] >= E[L_bm] gegen H1: min_i E[L_i] < E[L_bm], Eingabe sind VERLUSTE (kleiner = besser), ein Benchmark gegen eine Modellmenge;
StepM (Romano/Wolf 2005) liefert eine MENGE besserer Modelle statt eines p-Werts; RealityCheck (White 2000) ist die Vorlaeufer-Version; MCS (Hansen/Lunde/Nason 2011) ohne Benchmark.
Suchtreffer-Zusammenfassungen: White: Nullhypothese "bestes Modell hat keine Vorhersageueberlegenheit gegenueber dem Benchmark"; Hansen: Verfeinerung, weniger empfindlich gegen schlechte/irrelevante Alternativen;
Romano/Wolf: stufenweises Verfahren mit Kontrolle der familienweisen Fehlerrate (FWER), mehr Macht als Single-Step, Studentisierung empfohlen.
Politis/Romano: Bloecke mit geometrisch verteilter Laenge, Mittel 1/p (der arch-Doku-Treffer sagt "exponentiell verteilt, Blockgroesse als Mittelwert"); neue Blocklaenge mit Wahrscheinlichkeit p, sonst naechster Index (zirkulaer).

Skizze (AUS GEDAECHTNIS):
    d[k,t] = r_k,t - r_bm,t     (Netto-Differenzrendite Variante k minus Benchmark; arch erwartet Verluste: loss = -return)
    dbar_k = mean_t d[k,t];  omega_k = bootstrap-Standardfehler von sqrt(T)*dbar_k
    T_SPA  = max( max_k sqrt(T)*dbar_k/omega_k , 0 )
    Bootstrap b=1..B: Indexfolge I_t stationaer (p = 1/b_bar), d*_k,b = mean_t d[k, I_t]; zentrieren: Z*_k,b = sqrt(T)*(d*_k,b - g(dbar_k))/omega_k
      g_upper(x) = x (=White-RC-Zentrierung), g_lower(x) = max(x,0), g_consistent(x) = x * 1{x >= -A_k}, A_k = 1/4 * T^(-1/4) * sqrt(var(sqrt(T)*dbar_k)) (Hansen; Konstante AUS GEDAECHTNIS, vor Nutzung gegen Paper/arch pruefen)
    p_x = mean_b( max(max_k Z*_k,b, 0) > T_SPA )  fuer x in {lower, consistent, upper}   (lower <= consistent <= upper)
    StepM: Statistiken t_k = sqrt(T)*dbar_k/omega_k absteigend; wiederhole: c = (1-alpha)-Quantil von max_{k in verbleibend} Z*_k,b; verwerfe alle k mit t_k > c; entferne sie; bis keine mehr.
Empfehlung: NICHT selbst nachbauen, sondern `arch.bootstrap` nutzen (SPA, StepM, RealityCheck, StationaryBootstrap, MCS) und die Konventionen (Verluste, studentize, block_size, reps) im Test gegen ein Simulationsbeispiel pruefen.

## 3. Erwartungs-Abschlaege fuer publizierte Strategien - Zahlen mit Quelle

| Quelle | Gegenstand | Zahl | Anmerkung |
|---|---|---|---|
| McLean/Pontiff 2016 (Volltext) | 97 Praediktoren aus 80 Studien, Stichprobenende 2013 | Ø In-Sample 58.2 bp/Monat; OOS vor Publikation -15.0 bp (-26 %); nach Publikation -33.7 bp (-58 %); Ø Rohmittel: 0.582 / 0.402 / 0.264 %/Monat | Publikationseffekt ca. 32 Pp.; 26 % = Obergrenze fuer Data-Mining/statistische Verzerrung; Portfolios meist gleichgewichtet |
| McLean/Pontiff 2016 | Zeitverlauf | ab 13. Monat nach Stichprobenende >20 bp unter In-Sample; Jahr 3 nach Publikation -40.8 bp, Jahr 4 -43.3 bp, Jahr 5 -20.5 bp, danach im Mittel -33.9 bp ggue. In-Sample | Bezug laut Text "gegenueber In-Sample"; hoeher In-Sample-Rendite -> staerkerer Verfall |
| McLean/Pontiff 2016 | Struktur | 85 von 97 (88 %) hatten In-Sample-t > 1.5; mittlere Korrelation der Praediktor-Portfolios 0.033; nach Publikation steigt die Korrelation mit anderen publizierten Portfolios | Ohne die 12 schwachen: -18.0 bp OOS, -38.7 bp nach Publikation bei Ø 65.2 bp In-Sample |
| Harvey/Liu/Zhu 2016 (Volltext) | 316 Faktoren, 313 Artikel (250 publiziert) | Bonferroni-t 3.78 (2012), BHY 3.39 (1 %), min. 3.18; von 296 signifikanten Faktoren gelten 158 (Bonferroni), 142 (Holm), 132 (BHY 1 %), 80 (BHY 5 %) als falsch entdeckt | Modell: M ca. 1,300-1,800 getestet; wahre Faktoren Ø 0.55 %/Monat (6.6 %/Jahr), annualisierte SR ca. 0.44 bei 15 % Vol |
| Harvey/Liu 2015 (Volltext) | Haircut-Sharpe | SR 0.75, 20 Jahre, N=200 -> HSR 0.32 (ca. -60 %); SR < 0.4 meist > 50 % Haircut; SR > 1.0 hoechstens 25 % | gilt fuer Mehrfachtest-Korrektur, NICHT inkl. Post-Publication-Verfall und Kosten |
| Hou/Xue/Zhang 2020 (Abstract) | 447 Anomalien, NYSE-Breakpoints, wertgewichtet | 286 (64 %) unbedeutend bei 5 %; mit t >= 3: 380 (85 %); von 161 signifikanten werden 115 (150 mit t >= 3) im q-Faktor-Modell unbedeutend | Mikrocaps treiben viele Scheinresultate; liquiditaetsnahe Variablen: 95 von 102 fallen durch |
| Chen/Velikov 2023 (nur Suchtreffer) | 204 Anomalien, halber effektiver Spread, Post-Publikation, Zeit ab ca. 2000 | Ø Anomalie netto ca. 4 bp/Monat; beste hoechstens ca. 10 bp; kombinierte Strategien ca. 20 bp (Working Paper: 120 Anomalien, 8 bp) | Autoren: halber Spread = Untergrenze der Kosten (ohne Leihgebuehren/Price Impact); In-Sample-Referenzwert in der Zusammenfassung nicht angegeben |
| Chen/Zimmermann (Abstract) | Meta-Studien | Publikationsbias per Empirical Bayes nur 10-15 % des In-Sample-Mittels; FDR < 10 %; "andere Portfoliotests" 30-50 % schwaecher | Gegenposition zu HLZ/HXZ |
| Jensen/Kelly/Pedersen 2023 (Abstract) | Bayes-Modell, 13 Themen, 93 Laender | Mehrheit der Faktoren repliziert und funktioniert out-of-sample; Zahlen im Abstract nicht angegeben | Gegenposition zu HLZ |
| Bailey/LdP 2014 | Mehrfachtest-Selektion | E[max SR] bei N=10: 1.57 (sigma=1); 5 Jahre erlauben nur ca. 45 unabhaengige Versuche fuer In-Sample-SR 1 | siehe 2.1-2.3 |

Aggregiertes Vorgehen fuer das Lab (EIGENE Konvention, aus obigen Zahlen abgeleitet, KEINE Papier-Aussage):
    publizierte Idee, US-Aktien-Querschnitt:  Erwartung_vor_Kosten = In-Sample-Mittel * (1 - 0.58)        (McLean/Pontiff, Publikationsfall)
    eigene, unpublizierte Entdeckung:         Erwartung_vor_Kosten = In-Sample-Mittel * (1 - 0.26)        (nur statistische Verzerrung, Obergrenze) und zusaetzlich DSR/Haircut
    danach Kosten und Steuer abziehen; Chen/Velikov (ca. 4 bp/Monat netto im Mittel) ist der Warnhinweis, dass das Ergebnis oft ~0 ist.
Grenzen: Alle Zahlen gelten fuer US-Aktien-Long-Short-Anomalien (Jahrzehnte bis 2013 bzw. 2020er). Fuer ETF-Timing/Asset-Allokation gibt es in dieser Recherche KEINE gleichwertigen Verfallszahlen - dort nur die Mehrfachtest-Statistik anwenden.

## 4. Die Pruefstand-Module ("Strategien") im Detail
Reihenfolge nach erwarteter Robustheit. Gemeinsame Eingabe: Netto-Renditereihe des Kandidaten NACH Kosten und Steuer-Modell, Signal am Schlusskurs t, Ausfuehrung zur Eroeffnung t+1 (so ist die Reihe im Lab schon gebaut),
und das Trial-Register: Matrix R aller JE getesteten Varianten (auch verworfene) auf denselben Daten, mit Datum, Familie, Parametern.

### M1 dsr_gate_honest_n - Deflated-Sharpe-Tor mit ehrlichem N
    1. SR_hat = mean(r)/std(r, ddof=1) pro Tag (oder pro Monat bei monatlichem Handel); T = Anzahl Beobachtungen; g3 = skew(r); g4 = kurtosis(r) + 3 (pandas .kurt() ist Excess).
       Bei merklicher Autokorrelation (|AC1| > 0.1) mit nicht ueberlappenden Monatsrenditen rechnen (EIGENE Konvention; HL korrigieren ebenfalls auf Autokorrelation).
    2. M = Spaltenzahl von R; rho_bar = mittlere Off-Diagonal-Korrelation; N_eff = ceil( rho_bar + (1-rho_bar)*M ), mindestens 1. Wenn unsicher: N_eff = M (konservativ).
    3. V = var(SR_m ueber Spalten, ddof=1) in derselben Periodeneinheit wie SR_hat; bei M < 10: V = 1/T (Stichprobenvarianz unter H0; EIGENE Konvention).
    4. SR0 = sqrt(V) * ((1-g)*Phi^-1(1-1/N_eff) + g*Phi^-1(1-1/(N_eff*e))), g = 0.5772156649; (N_eff = 1 -> SR0 = 0).
    5. DSR = Phi( (SR_hat - SR0)*sqrt(T-1) / sqrt(1 - g3*SR_hat + (g4-1)/4*SR_hat^2) ).
    6. Vorfilter MinBTL: Jahre >= ( ((1-g)*Phi^-1(1-1/N_eff) + g*Phi^-1(1-1/(N_eff*e))) / SR_ann_hat )^2.
    ENTSCHEIDUNG: Kandidat besteht nur wenn DSR >= 0.95 UND MinBTL-Vorfilter erfuellt. Sonst NO TRADE / "nicht bewiesen".
    Trial-Zaehlung: JEDE Variante zaehlt (Parameter, Universum, Rebalance-Takt, Filter), auch in anderen Familien, solange gleiche Daten; vorab in HYPOTHESEN.md registrierte Kandidaten zaehlen als N.
EIGENER CHECK - Mindest-Sharpe (annualisiert, Normalrenditen, V[SR]=1/Jahre, DSR >= 0.95): 10 Jahre: N=1: 0.52, N=10: 1.02, N=40: 1.21, N=200: 1.40; 18 Jahre: 0.39 / 0.76 / 0.90 / 1.04; 25 Jahre: 0.33 / 0.64 / 0.77 / 0.88.
SR0 (annualisiert, V=1/Jahre) fuer 18 Jahre: N=10: 0.37, 40: 0.52, 100: 0.60, 200: 0.65, 1000: 0.77; fuer 40 Jahre: N=10: 0.25, 40: 0.35, 200: 0.44, 1000: 0.51.

### M2 t3_haircut_sharpe_gate - t >= 3-Huerde und Haircut-Sharpe (Bonferroni/Holm/BHY)
    1. Monatliche Netto-Excess-Renditen, T >= 60 Monate. SR_m = mean/std(ddof=1); t = SR_m*sqrt(T); SR_ann = SR_m*sqrt(12).
    2. Harte Huerde: t >= 3.0. Darunter ausscheiden.
    3. p_S = 2*(1 - F_t(t; df=T-1)). M = Zahl der bisher im Lab getesteten Strategie-Ideen (mindestens; ehrlich zaehlen).
       Mit Vektor aller p-Werte der M Tests: Bonferroni, Holm, BHY (Formeln 2.5), p_adj fuer den Kandidaten.
       Ohne Vektor: nur Bonferroni p = min(M*p_S, 1).
    4. t_adj = F_t^-1(1 - p_adj/2; T-1); HSR_ann = t_adj/sqrt(T)*sqrt(12); Haircut = 1 - HSR_ann/SR_ann.
    ENTSCHEIDUNG: bestanden, wenn t >= 3.0 UND Holm-p_adj <= 0.05 (alternativ BHY-p_adj <= 0.05 als lockere FDR-Variante, ausdruecklich als solche melden). Bericht immer mit HSR und Haircut.
    Faustwerte (EIGENER CHECK): Mindest-SR fuer t = 3 bei 5 / 10 / 20 / 40 / 60 Jahren: 1.34 / 0.95 / 0.67 / 0.47 / 0.39 annualisiert; fuer t = 2: 0.89 / 0.63 / 0.45 / 0.32 / 0.26.
    Bonferroni-t bei M = 20 / 50 / 100 / 316: 3.02 / 3.29 / 3.48 / 3.78.

### M3 publication_decay_discount - Erwartungs-Abschlag fuer publizierte Ideen
    Eingabe: mu_IS = In-Sample-Mittelrendite der Quelle (brutto, pro Monat), Publikationsjahr Y, Turnover und Kostenmodell des Labs.
    1. Falls Idee publiziert (vor Testbeginn bekannt): mu_pub = mu_IS * (1 - 0.58). Falls eigene Entdeckung: mu_pub = mu_IS * (1 - 0.26).
       Sensitivitaet: optimistisch (1 - 0.15) [Chen/Zimmermann Bias 10-15 %], pessimistisch Chen/Velikov (Mittel der Anomalien ca. 4 bp/Monat netto).
    2. mu_net = mu_pub - Kosten_pro_Monat (Turnover * (halber Spread + Gebuehr + Slippage)) - Steuer (Abgeltungssteuer-Modul des Labs).
    3. Naeherung Erwartungs-Sharpe: SR_exp = SR_IS * (1 - 0.58) (Vola unveraendert angenommen - EIGENE Naeherung).
    ENTSCHEIDUNG: Kandidat darf nur weiter, wenn mu_net > 0 UND SR_exp bei Buy&Hold-Konkurrenz (SPY) im Konfidenzband liegt, sonst Aussage "Edge nach Verfall und Kosten nicht erwartbar".
    Zusatzregel: je hoeher mu_IS relativ zum Mittel (58.2 bp/Monat bei McLean/Pontiff), desto staerkerer Verfall - nie linear extrapolieren, sondern vorsichtig runden.

### M4 pbo_cscv_selection_gate - Probability of Backtest Overfitting
    1. R = Netto-Tagesrenditen aller N >= 10 Varianten EINER Idee (gleiche Daten, synchron); T >= 160; S = 16 gleich lange Bloecke (Rest am Anfang verwerfen).
    2. Fuer jede der C(16,8) = 12,870 Teilmengen J mit 8 Bloecken: IS = J, OOS = Komplement; SR pro Variante; n* = argmax SR_IS; w = rang_OOS(n*)/(N+1); lambda = ln(w/(1-w)).
    3. PBO = Anteil lambda <= 0. Zusatz: Verlustwahrscheinlichkeit OOS = Anteil SR_OOS(n*) < 0; Degradation = Steigung der Regression SR_OOS(n*) auf SR_IS(n*).
    ENTSCHEIDUNG: PBO <= 0.05 bestanden (Papier-Konvention). Praktischer Lab-Zusatz (EIGENE Konvention): PBO > 0.2 = Auswahl wackelig, PBO >= 0.5 = Auswahl ist Muenzwurf. Bei Durchfallen: die gesamte Variantenfamilie verwerfen, nicht die zweitbeste nehmen.

### M5 spa_stepm_family_test - familienweiter Bootstrap-Test gegen Benchmark
    1. Benchmark = Buy&Hold-Konkurrent (SPY bzw. Equal-Weight-Korb); D[t,k] = Netto-Tagesrendite Variante k - Benchmark; ALLE getesteten Varianten (auch verworfene).
    2. Stationaerer Bootstrap (Politis/Romano), mittlere Blocklaenge b_bar; B = 10,000; gleiche Zeitindizes fuer alle Varianten (Abhaengigkeit bleibt erhalten).
       b_bar: Fallback round(T^(1/3)) (EIGENE Naeherung); besser automatisch (Politis/White 2004, nicht gesehen).
    3. SPA (studentisiert) mit "consistent"-p-Wert; bei p_consistent < 0.05: Nullhypothese "keine Variante schlaegt den Benchmark" verworfen. Zusaetzlich StepM (alpha = 0.05) fuer die Liste der Gewinner.
       Umsetzung: arch.bootstrap.SPA / StepM mit Verlusten = -Rendite (Signatur-Details vor Nutzung pruefen).
    ENTSCHEIDUNG: Kandidat besteht nur, wenn er in der StepM-Gewinnerliste steht und p_SPA_consistent < 0.05. Ergebnisse (alle drei SPA-p-Werte) ins Logbuch.

## 5. Praktische Konsequenzen fuer das Quant-Lab (EIGENE Folgerungen)
- Trial-Register anlegen (CSV/Parquet im Repo oder data_cache): pro Test eine Spalte mit Netto-Tagesrendite, Datum, Familie, Parameter. Ohne Register ist weder N (DSR/Haircut) noch PBO/SPA moeglich.
- Pflicht vor jedem Kandidatenbericht: DSR, PSR vs. SPY, Haircut-Sharpe, PBO (falls Varianten), SPA/StepM (falls Familie). Ergebnis kann sein: "Rauschen".
- Lange Reihen nutzen, wo moeglich: Ken French Faktoren (Monatsdaten ab 1926-07, aus Gedaechtnis, hier NICHT geprueft), ^GSPC ab 1927-12-30, ^IRX ab 1960-01-04 (beides laut tsmom.md per yfinance am 2026-10-11 geprueft).
  18 Jahre ETF-Daten (SPY ab 1993-01-29, viele ETFs erst 2002-2007) haben zu wenig Macht (Standardfehler einer Jahres-Sharpe ca. 1/sqrt(18) = 0.24).
- Out-of-sample-Tests mit nur ein paar Jahren Holdout sind schwach: Harvey/Liu betonen, dass kurze OOS-Fenster viele echte Entdeckungen verpassen und dass Forscher die Daten ohnehin schon "gesehen" haben.
- Alle publizierten Anomalie-Verfallszahlen stammen aus US-Aktien-Querschnitten; fuer ETF-Tests nicht direkt uebertragbar.

## 6. Pruefung von `qlab/stats.py` gegen die Papiere (Stand 2026-10-12)
- `psr`: entspricht der PSR-Formel (Nenner 1 - g3*SR + (g4-1)/4*SR^2, kurt NICHT-excess, sqrt(n-1)). OK.
- `expected_max_sr`: entspricht Eq. 1/6 des DSR-Papiers inkl. Snippet 1; gibt 0 bei n_trials <= 1. OK. Vorsicht: `var_sr` muss in derselben Einheit wie `sr` stehen (pro Tag).
- `deflated_sharpe`: `r.kurt() + 3.0` ist korrekt (pandas .kurt() = Excess). Schiefe/Kurtosis aus `r`, SR aus Excess-Rendite `ex` - Abweichung vernachlaessigbar. Der Aufrufer muss `n_trials` ehrlich zaehlen (siehe M1).
- `pbo_cscv`: entspricht Algorithmus 2.3 (S=16, 12,870 Kombinationen, relativer Rang rank/(N+1), Logit, PBO = Anteil <= 0). Abweichung: Bloecke koennen durch linspace leicht ungleich lang sein (Papier verlangt gleich lang) - unkritisch. Fehlend: Performance-Degradation und OOS-Verlustwahrscheinlichkeit.
- `_stationary_idx`/`bootstrap_sharpe_diff`: stationaerer Bootstrap mit Wiederbeginn-Wahrscheinlichkeit 1/mean_block, zirkulaer - entspricht dem Politis/Romano-Schema; fester mean_block = 21. Es ist ein TEST EINER Hypothese (Kandidat vs. Benchmark). Wird er auf den Gewinner vieler Varianten angewendet, ist er ohne Mehrfachtest-Korrektur verzerrt -> Modul M5 noetig.
- Fehlend: Haircut-Sharpe (M2), MinBTL (M1), SPA/StepM (M5), Trial-Register, Autokorrelations-Korrektur der Sharpe.
Known-Answer-Tests, die man in `tests/test_stats.py` ergaenzen kann (EIGENE Rechnungen, mit Papier abgeglichen):
- expected_max_sr(10, var_sr=1.0) = 1.5746 (Papier: 1.57).
- DSR-Beispiel: sr = 2.5/sqrt(250), T = 1250, skew = -3, kurt = 10, var_sr = 0.5/250: N=100 -> 0.9004; N=46 -> 0.9505; mit skew 0, kurt 3: N=88 -> 0.9505, N=100 -> 0.9428.
- MinBTL(E[max]=1): N=45 -> 4.998 Jahre; N=7 -> 1.923 Jahre.
- Haircut-Sharpe: T=240, SR_ann 0.75, unabhaengig N=200 -> p_M = 0.169, HSR = 0.308 (Papier 0.15 / 0.32, Toleranz einplanen).
- Bonferroni zweiseitig 5 % mit M=316 -> z = 3.778 (HLZ 3.78).
- C(16,8) = 12870.

## 7. Kontroverse und Grenzen (ehrlich)
- Die Schaetzung der "Wahrscheinlichkeit, dass ein publizierter Faktor falsch ist", haengt stark von Annahmen ab: HLZ (Haertepunkte 3.0-3.9, M ca. 1,300-1,800 getestet) und HXZ (64-85 % durchfallend) gegen JKP/CZ (die meisten replizieren, FDR < 10 %).
  Beide Lager stimmen darin ueberein, dass der alte t = 2-Massstab nicht reicht und dass Verfall nach Publikation existiert (MP: 58 %; CZ: Meta-Studien).
- DSR und Haircut ersetzen KEINE ehrliche Zaehlung: wer verworfene Varianten nicht protokolliert, bekommt zu kleine N und zu lasche Schwellen. Das ist die groesste praktische Schwachstelle (Bailey/LdP: "ein Backtest ohne Angabe der Versuchszahl ist wertlos").
- PSR/DSR nehmen iid-Renditen mit Momentenkorrektur an; Autokorrelation (Tagesdaten von Rebalance-Strategien) und Volatilitaets-Cluster verletzen das. Bootstrap (M5) oder nicht ueberlappende Monatsrenditen sind robuster.
- MinBTL/DSR sind notwendig, nicht hinreichend (Papier). Ein bestandenes Tor ist kein Beweis, nur das Fehlen eines Gegenbeweises.
- Regime/Strukturbruch (z.B. Kurth et al. 2026 in tsmom.md: schnelle Trendsignale seit ca. 2009 praktisch tot) werden von keinem dieser Tests erfasst - Out-of-sample-Zeitfenster bleiben noetig.

## 8. Quellen-URLs (alle in dieser Session abgerufen oder als Suchtreffer gesehen, Status siehe Abschnitt 1)
- https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf (SSRN-Abstract im PDF: http://ssrn.com/abstract=2460551)
- https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf
- https://carmamaths.org/jon/backtest.pdf (Pseudo-Mathematics and Financial Charlatanism, Fassung 01.04.2014; ein Verweis auf SSRN abstract=2345489 steht im Literaturteil des PDFs)
- https://people.duke.edu/~charvey/Research/Published_Papers/P118_and_the_cross.PDF
- https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF (CME-Kopie als Suchtreffer: https://www.cmegroup.com/content/dam/cmegroup/education/files/backtesting.pdf)
- https://counterpointfunds.com/wp-content/uploads/2017/07/PredictabilityMcleanPontiff.pdf
- https://www.nber.org/papers/w23394
- https://www.nber.org/papers/w28432
- https://arxiv.org/abs/2209.13623
- https://www.federalreserve.gov/econres/feds/zeroing-in-on-the-expected-returns-of-anomalies.htm (Suchtreffer; Journal-Seite: https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/zeroing-in-on-the-expected-returns-of-anomalies/945133D5A3ECEEAF466AEE91551FD225)
- https://www.econometricsociety.org/publications/econometrica/2000/09/01/reality-check-data-snooping
- https://ideas.repec.org/p/bro/econwp/2001-06.html
- https://www.econometricsociety.org/publications/econometrica/2005/07/01/stepwise-multiple-testing-formalized-data-snooping
- https://econ-papers.upf.edu/papers/712.pdf
- https://gnosis.library.ucy.ac.cy/handle/7/57533
- https://arch.readthedocs.io/en/latest/multiple-comparison/multiple-comparison-reference.html
- https://arch.readthedocs.io/en/latest/bootstrap/generated/arch.bootstrap.StationaryBootstrap.html (Suchtreffer)
