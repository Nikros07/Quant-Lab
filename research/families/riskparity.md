# Familie: Risk Parity / Minimum-Varianz / HRP / Diversifikation

Stand: 2026-10-11. Analyst: Quant-Research-Subagent. Sprache: Deutsch.
Ziel: implementierbare bzw. ehrlich bewertete Strategien mit **gratis Daten** (Yahoo/yfinance, Ken French, AQR-Datasets). Portfoliokonstruktion ohne Renditeprognose.

## 0. Kurzfazit (ehrlich)

1. **Diese Familie liefert keinen "Alpha"-Edge im Sinne von Erfolgsfall 1, sondern Risiko-Reduktion und Robustheit (Erfolgsfall 2).** Die Papers behaupten höhere Sharpe-Ratios (Risk Parity) bzw. niedrigere Out-of-Sample-Varianz (HRP, Min-Var). Eine Rendite-Überlegenheit über SPY-Buy&Hold ist **nicht** belegt und nach den Quant-Lab-Regeln (Kosten, Steuer, Realzeit-Ausführung) nicht zu erwarten.
2. **Die stärkste Evidenz ist die für die Nicht-Optimierung:** DeMiguel/Garlappi/Uppal (RFS 2009) finden, dass keines von 14 Optimierungsmodellen über 7 Datensätze die naive 1/N-Regel konsistent schlägt (Sharpe, Sicherheitsäquivalent, Turnover). Das ist der robusteste Anker der Familie und zugleich die Pflicht-Benchmark für jede andere Regel hier.
3. **Risk Parity: Ergebnis hängt an Zeitraum, Leverage und Kosten.** Asness/Frazzini/Pedersen (AFP 2012): US 1926-2010, unlevered RP Sharpe 0,52, levered RP 0,53, 60/40 0,40, marktgewichtet 0,25 (Tabelle 2, selbst gelesen). Dagegen steht Anderson/Bianchi/Goldberg (FAJ 2012): Start-/Endzeitpunkt verschiebt das Ergebnis materiell, Transaktionskosten können das Ranking umdrehen, "besonders bei Leverage". Autoren beider Seiten sind nicht neutral (AFP/AQR sind selbst Risk-Parity-Anbieter, Bruder/Roncalli sind bei Lyxor).
4. **2022 hat die Kernannahme (negative Aktien-Anleihen-Korrelation) gebrochen.** Eigener deskriptiver Check (Abschnitt 5): 2022 verloren IEF -15,2 %, TLT -31,2 %, TIP -12,3 %, SPY -18,2 %, nur DBC machte +19,3 %. Die tägliche Korrelation SPY-TLT war 2007-2020 durchgehend negativ (-0,14 bis -0,71 pro Kalenderjahr) und ist seit 2022 positiv (2026 bis 09.10.: +0,35). Jede Variante mit hohem Anleihenanteil oder gar Leverage ist davon direkt betroffen.
5. **HRP ist die am schwächsten belegte Methode der Familie.** Das Originalpapier (López de Prado 2016) enthält in der gelesenen Fassung **nur Monte-Carlo-Simulation mit gaußschen Zufallsdaten, keinen Realdaten-Backtest**. Unabhängige Replikationen (nur über Suchzusammenfassungen und Quantpedia gesehen) sind gemischt: HRP schlägt meist Inverse-Varianz, gegen Min-Var und 1/N uneinheitlich.
6. Ich habe **keine Strategie-Backtests** gerechnet (Quant-Lab-Regel 3: Hypothese vor Test). Abschnitt 5 enthält nur deskriptive Asset-Kennzahlen (Jahresrenditen, Korrelationen) als Kontext, kein Test der Regeln unten.

## 1. Quellenstatus (was wirklich gesehen wurde)

Gesamt 22 Web-Abrufe (9 WebSearch, 13 WebFetch), davon 5 Fehlversuche (403, 404, DNS-Fehler, 2 Redirects ohne Inhalt). Bei mehreren PDFs lieferte WebFetch nur Binärdaten; die Texte habe ich dann lokal per pdftotext aus der gespeicherten Datei gelesen. Das Budget von ca. 15 wurde damit überschritten, weil Fehlversuche und die PDF-Umwege mitzählen. Dazu: lokales pdftotext auf gespeicherten PDFs, ein yfinance-Check der Startdaten, ein yfinance-Check der Asset-Kennzahlen, ein HEAD-Request auf Ken French (nichts heruntergeladen).

| Quelle | Tiefe |
|---|---|
| Asness/Frazzini/Pedersen 2012, "Leverage Aversion and Risk Parity", FAJ 68(1), 47-59 | **Volltext gelesen** (AQR-PDF per pdftotext), Tabelle 2 und Konstruktionsregel exakt |
| López de Prado 2016, "Building Diversified Portfolios that Outperform Out-of-Sample", JPM 42(4), 59-69 | **Volltext der SSRN-Fassung gelesen** (31 Seiten, Fassung vom Dez. 2015, Guggenheim-Affiliation); Algorithmus und Monte-Carlo-Zahlen exakt. Journalfassung nicht gesehen. |
| Bruder/Roncalli 2012, "Managing Risk Exposures using the Risk Budgeting Approach" (MPRA 37246) | **Teilweise gelesen** (Abstract, Risk-Parity-Beispiel, ERC-Index-Abschnitt). Mathematische Teile nicht im Detail geprüft. |
| AQR, "Risk Parity Is Even Better Than We Thought" (Asness, 1.6.2015) | **Volltext gelesen**; Interessenkonflikt (AQR verkauft Risk Parity) |
| Li/Kose 2015, "Black Ice: Low-Volatility Investing in Theory and Practice" (Research Affiliates) | **Volltext gelesen**, Tabellen 1 und 2 |
| Anderson/Bianchi/Goldberg 2012, "Will My Risk Parity Strategy Outperform?", FAJ 68(6), 75-93 | **Nur Abstract** (CFA-Institute-Seite abgerufen, IDEAS und Suchzusammenfassung). Berkeley-PDF nicht erreichbar (DNS-Fehler). Zahlen aus dem Volltext fehlen. |
| DeMiguel/Garlappi/Uppal 2009, "Optimal versus Naive Diversification", RFS 22(5), 1915-1953 | **Nur Abstract-Ebene** (Suchzusammenfassung; LBS-Seite lieferte nur Metadaten). Volltext nicht gelesen. |
| Maillard/Roncalli/Teiletche 2010, "The Properties of Equally Weighted Risk Contribution Portfolios", JPM 36(4), 60-70 | **Nur Sekundärquellen** (Suchzusammenfassung). SSRN-Abruf gab 403. Das Ergebnis "ERC-Vol zwischen Min-Var und 1/N" steht aber auch im Abstract von Bruder/Roncalli 2012 (gelesen). |
| Clarke/de Silva/Thorley 2006, "Minimum-Variance Portfolios in the U.S. Equity Market", JPM 33(1), 10-24 | **Nur Zitat** in Suchtreffer. Inhalt nicht gesehen. Nicht in der Papierliste. |
| Chow/Kose/Li 2016, "The Impact of Constraints on Minimum-Variance Portfolios", FAJ | Nur Abstract-Ebene (Suchzusammenfassung, CFA-Institute-Link) |
| Lohre/Rother/Schäfer 2020, HRP mit Tail Dependence (SSRN 3513399) | **Nur über die Quantpedia-Seite** (abgerufen) gesehen, nicht das Paper selbst |
| Quantpedia "Hierarchical Risk Parity" | Seite abgerufen |
| Replikationen HRP (Reis et al. RBFin; CBS-Masterarbeit; Eko/Husodo; iranische Studien; QuantConnect-Forum) | **Nur Suchzusammenfassungen**, niedrige Qualität, nur als Stimmungsbild |
| Kritik 2022 (CAIA, Substack-/Blog-Artikel zu Bridgewater All Weather, RPAR) | **Nur Suchzusammenfassungen**. CAIA-Seite gab beim Abruf 404. Zahlen dort (z. B. All Weather ca. -22 %, RPAR ca. -32 % Drawdown, Korrelation +0,65) sind **nicht verifiziert**. |

**Lücken, ehrlich:**
- Ich habe **kein spezifisches 2022er Paper** zur Risk-Parity-Kritik gefunden und gelesen. Die 2022-Evidenz stammt aus meinem eigenen yfinance-Check und unverifizierten Sekundärtexten.
- Ich habe **keine begutachtete Realdaten-Replikation von HRP** im Volltext gelesen.
- Von den Papers 2015-2026 habe ich nur Li/Kose 2015 (Volltext), Chow/Kose/Li 2016 (Abstract), Lohre et al. 2020 (über Quantpedia) gesehen. Raffinots HERC (SSRN 3237540, im Suchtreffer genannt) habe ich nicht geöffnet.
- Anderson/Bianchi/Goldberg, DeMiguel et al., Maillard et al. und Clarke et al. sind nur auf Abstract- bzw. Zitat-Ebene belegt.

## 2. Gemeinsame Konventionen für alle Regeln unten

- **Daten:** `yfinance`, Tagesdaten, `auto_adjust=True` (Total-Return-Näherung). Cash-Satz: `^IRX` (13-Wochen-T-Bill, in Prozent p. a.), Daten ab 1960-01-04.
- **Signalzeitpunkt:** Schlusskurs des **letzten Handelstags t jedes Kalendermonats**; es dürfen nur Daten bis einschließlich t in die Berechnung eingehen.
- **Ausführung:** Eröffnungskurs des **nächsten Handelstags t+1** (yfinance `Open` bei `auto_adjust=True`). Gewichte driften danach frei bis zum nächsten Signal (kein tägliches Rebalancing).
- **Kosten (Annahme von mir, nicht aus den Papers):** 5 bp pro Seite auf das gehandelte Volumen für große US-ETFs, Stresstest 15 bp. Steuerreibung durch monatliches Umschichten (Quant-Lab-Regel 4) ist in keinem der Papers modelliert.
- **Praktischer Hinweis (Allgemeinwissen, nicht recherchiert):** US-gelistete ETFs (VTI, TLT usw.) sind für EU-Privatanleger bei vielen Brokern wegen der KID-Pflicht nicht kaufbar. Für Live braucht es UCITS-Äquivalente mit kürzerer Yahoo-Historie. Die US-Ticker sind hier das Forschungs-Proxy.
- **Universum U9 (gemeinsam für S1, S2, S3, S5):** `VTI, EFA, EEM, VNQ, IEF, TLT, TIP, GLD, DBC`. Gemeinsamer Datenstart durch **DBC am 2006-02-06** (yfinance-Check 2026-10-11). Die Aufteilung ist 4 Aktien/REIT, 3 Anleihen, 2 Rohstoffe/Gold.
- **Datenstarts laut yfinance (Check vom 2026-10-11):** SPY 1993-01-29, VTI 2001-06-15, IWM 2000-05-26, EFA 2001-08-27, EEM 2003-04-14, TLT/IEF/SHY/LQD 2002-07-30, TIP 2003-12-05, AGG 2003-09-29, VNQ 2004-09-29, GLD 2004-11-18, DBC 2006-02-06, GSG 2006-07-21, HYG 2007-04-11, BND 2007-04-10, BIL 2007-05-30, IEI 2007-01-11, EMB 2007-12-19, SPLV 2011-05-05, USMV 2011-10-20, PDBC 2014-11-07, SCHP 2010-08-05, XLK/XLU 1998-12-22, `GC=F` 2000-08-30, `^GSPC` 1927-12-30. Mutual Funds mit langer Historie: VFINX 1980-01-02, VUSTX 1986-05-19, VBMFX 1986-12-11, VFITX 1991-10-28, VWEHX 1980-01-02.
- **Kurze Stichprobe:** U9 gibt nur ca. 20,7 Jahre (2006-02 bis 2026-10), inklusive 2008, 2013, 2020 und 2022. Faustformel (nicht aus den gelesenen Papers): Der Standardfehler einer Jahres-Sharpe liegt bei ca. 0,25. Sharpe-Differenzen unter ca. 0,15 zwischen zwei Regeln sind in so einer Stichprobe praktisch nicht unterscheidbar. Das ist genau das Problem, das DeMiguel et al. für die Optimierung betonen.
- **Lange Stichprobe als Zusatz (S2):** 2-Asset-Stichprobe `VFINX` plus `VBMFX` ab 1986-12-11 (Aktien und Anleihen wie AFP Long Sample, aber nur 40 Jahre). Weiter zurück bräuchte man Shiller-Daten (S&P-Reihe und 10-jährige Zinsen, Anleihenrenditen synthetisch aus Zinsen): von mir **nicht geprüft**.

## 3. Strategien (nach erwarteter Robustheit sortiert, beste zuerst)

### S1 `ew_multiasset_1n` — 1/N über Anlageklassen (Benchmark und Basisfall)

**Quelle der Idee:** DeMiguel/Garlappi/Uppal 2009 (Abstract-Ebene): 14 Optimierungsmodelle über 7 Datensätze, keines konsistent besser als 1/N bei Sharpe, Sicherheitsäquivalent oder Turnover. Notwendige Schätzfenster, damit Mean-Variance-Optimierung 1/N schlägt: ca. 3000 Monate bei 25 Assets, ca. 6000 Monate bei 50 Assets (so im Abstract laut Suchzusammenfassung).

**Regel:**
```
U = U9 (9 ETFs, siehe Konventionen)
Signal t = letzter Handelstag jedes Monats, ab dem alle 9 ETFs notieren (frühestens 2006-02-28)
Zielgewichte w_i = 1/9
Ausführung: Open(t+1): auf Zielgewichte handeln
Halten bis zum nächsten Monatsultimo; keine Leverage; Rest 0 (voll investiert)
```
Keine geschätzten Parameter. Nur der Rebalancing-Takt (Monat) ist eine Wahl. Quartalsvariante nur als vorab festgelegte Alternative, nicht aus den Daten auswählen.

**Evidenz und Grenzen:** Der DeMiguel-Befund gilt für Aktienportfolios (Industrie-, Größen-Portfolios) und "Mean-Variance plus Erweiterungen". Er sagt nichts über absolute Rendite. 1/N hat keine Risikokontrolle. In U9 liegt das Risiko überwiegend bei Aktien/REIT/Rohstoffen (4 Aktienpositionen, DBC mit Vol ca. 19 %, VNQ ca. 29 %). Kritik am Paper (über einen Blog-Text und Suchzusammenfassung gesehen): kurze Monatsdaten, keine Signifikanztests der Sharpe-Unterschiede, und Kritzman/Page/Turkington (2010) halten mit längeren Daten dagegen für Optimierung. Das habe ich **nicht** im Original gelesen.

**Vorschlag Hypothese:** S1 ist Pflicht-Benchmark für S2, S3, S5. Abbruch einer Alternative, wenn Nettosharpe nicht mindestens ca. 0,15 über 1/N liegt oder Max-Drawdown nicht klar kleiner ist.

### S2 `ivp_risk_parity_unlevered` — Inverse-Volatilitäts-Risk-Parity (AFP-Konstruktion), optional levered

**Quelle der Idee:** Asness/Frazzini/Pedersen 2012. Originalregel (aus dem Volltext): Ende jeden Monats Gewicht je Anlageklasse gleich dem Kehrwert der Volatilität, geschätzt aus **drei Jahren Monatsrenditen (Überrenditen) bis Monat t-1**; Rest-Kovarianzen werden nicht genutzt. Unlevered-Version: Gewichte auf Summe 1 normiert. Levered-Version: Gewichte mit einer Konstanten k multipliziert, damit die **Ex-post-Volatilität** der marktgewichteten Benchmark getroffen wird (das ist eine Look-ahead-Eigenschaft des Papers).

**Regel (angepasst, ohne Look-ahead):**
```
U = U9 (Anlageklassen-ETFs). Alternativ Lang-Test: U = {VFINX, VBMFX} ab 1986-12-11.
Signal t = letzter Handelstag des Monats
sigma_i = Std(tägliche Renditen des Assets i über die letzten 756 Handelstage bis inkl. t) * sqrt(252)
          Mindestens 504 Beobachtungen nötig (Anlaufphase), erstes Signal ca. Feb 2008
w_i = (1/sigma_i) / sum_j (1/sigma_j)         # unlevered, Summe = 1
Ausführung: Open(t+1)
Variante L (levered, nur wenn vorab beschlossen):
   Sigma = Stichprobenkovarianz der letzten 756 Tage (annualisiert);  sigma_p = sqrt(w' Sigma w)
   k = min(2.0, 0.10 / sigma_p);  Gewicht k*w_i; Kredit-Anteil (k-1) kostet (IRX/100 + 0.01) p.a.
```
Die 756 Tage sind eine pragmatische Übertragung der 36 Monate des Papers auf Tagesdaten (Abweichung von mir). Der Zinsaufschlag 1 % und die Kappung bei 2,0 sind **meine Annahmen**, nicht aus dem Paper.

**Zahlen aus dem Paper (Tabelle 2, selbst gelesen):**
- Long Sample (US-Aktien und -Anleihen, 1926-2010): Aktien Sharpe 0,35; Anleihen 0,47; marktgewichtet 0,25; 60/40 0,40; RP unlevered Überrendite 2,20 %, Vol 4,25 %, Sharpe 0,52; RP levered (auf 15,08 % Vol skaliert) Überrendite 7,99 %, Sharpe 0,53, Alpha 5,50 % (t = 4,30). Durchschnittsgewichte unlevered ca. 15 % Aktien, 85 % Anleihen.
- Broad Sample (globale Aktien, US-Anleihen, Kredit, Rohstoffe, 1973-2010): RP unlevered Sharpe 0,62; RP levered Sharpe 0,61 bei Vol 10,10 %; marktgewichtet Sharpe 0,43.
- Zusätzlich 10 weitere Länder, Aktien und Anleihen 1986-2010, Tabelle 3 (Zahlen nicht notiert).
- Mit Futures-Leverage nehmen die Autoren keine Finanzierungskosten an (Überrenditen). Für einen ETF-Anleger gilt das nicht.

**Evidenz und Grenzen:** siehe Abschnitt 4 (ABG-Kritik, AQR-Antwort, 2022). Kernpunkt: Der Vorsprung stammt zu großen Teilen aus dem Anleihenanteil in einer Phase fallender Zinsen und negativer Aktien-Anleihen-Korrelation. Der AFP-Text selbst argumentiert dagegen, dass 1926-2010 ein "near-perfect round trip" der Anleihenrenditen enthält und die Aktien bewertungsmäßig fast verdoppelt wurden, also eher Aktien begünstigt waren. Beides stützt sich auf Daten bis 2010.

### S3 `erc_shrunk_cov` — Equal Risk Contribution mit geschrumpfter Kovarianz

**Quelle der Idee:** Maillard/Roncalli/Teiletche 2010 (nur sekundär gesehen) und Bruder/Roncalli 2012 (Abstract gelesen): Die Volatilität des Risk-Budgeting-Portfolios liegt zwischen der des Minimum-Varianz-Portfolios und des Gewicht-Budgeting-Portfolios (bei gleichem Budget: 1/N); Existenz und Eindeutigkeit werden diskutiert. ERC nutzt Korrelationen, im Gegensatz zu S2.

**Regel:**
```
U = U9; Signal t = letzter Handelstag des Monats; Lookback 756 Handelstage (min. 504)
r = tägliche Renditen; D = diag(Std je Asset);  z = r / Std (standardisiert)
R_hat = LedoitWolf-Kovarianz von z (sklearn.covariance.LedoitWolf), auf Korrelationsform bringen (Diagonale = 1)
Sigma_hat = D * R_hat * D * 252
Löse:  min_y  0.5 * y' Sigma_hat y  -  (1/N) * sum_i ln(y_i),   y_i > 0    (konvex)
w = y / sum(y)
Kontrolle: max_i | w_i (Sigma w)_i / (w' Sigma w) - 1/N | < 1e-6, sonst Fehler
Ausführung: Open(t+1); kein Leverage in der Basisversion (Leverage-Variante wie bei S2)
```
Die Zielfunktion folgt aus der Stationaritätsbedingung y_i (Sigma y)_i = 1/N, also gleiche Risikobeiträge. Das Schrumpfen der Korrelationsmatrix Richtung Identität ist **meine Design-Entscheidung** (nicht aus den Papers). Es zieht ERC in Richtung S2.

**Evidenz:** Bruder/Roncalli 2012 (Lyxor, Interessenkonflikt): ERC-Eurozone-Index (gleiches Universum wie Euro Stoxx 50 NR, monatlich ERC-gewichtet), Jan 1993 bis Dez 2011: Vol 21,2 % gegen 22,9 %, Drawdown 55,1 % gegen 66,6 %, Jahresrendite 10,7 % gegen 7,1 % (Indizes SGIXERC und SX5T). Das ist ein einzelner Index in einem Zeitraum mit Pre-Publikation-Überlappung. Ein Beispiel-Risk-Parity-Fonds mit Aktien und Anleihen (WGBI und MSCI World) brachte gegenüber konstanten Durchschnittsgewichten ca. +40 bp Rendite und ca. 35 bp weniger Vol, also klein.

**Grenzen:** Wenn die geschätzten Korrelationen annähernd gleich sind, ist ERC fast gleich S2. In Stressphasen steigen Korrelationen und die Schätzung hinkt hinterher. Der Vorteil gegenüber S2 ist in der Praxis klein (Turnover von ERC-Risk-Parity laut Quantpedia ca. 5 % im Lohre-Fall, Einheit nicht angegeben).

### S4 `minvar_industries_constrained` — Long-only Minimum-Varianz mit Gewichtskappen (Aktien)

**Quelle der Idee:** Clarke/de Silva/Thorley 2006 (nur Zitat gesehen, Inhalt **nicht** gelesen). Gelesen: Li/Kose 2015 (Research Affiliates) und Abstract-Ebene Chow/Kose/Li 2016.

**Forschungsregel (Ken French, gratis, nicht direkt handelbar):**
```
Daten: Ken French "49 Industry Portfolios", daily, wertgewichtet. Dateiname: 49_Industry_Portfolios_daily_CSV.zip
       URL (HTTP 200 per HEAD geprüft, nicht heruntergeladen):
       https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/49_Industry_Portfolios_daily_CSV.zip
       Startdatum: 1926-07 laut Erinnerung (NICHT verifiziert, Datei nicht geladen). Fehlwerte -99.99 / -999 als NaN behandeln.
Signal t = letzter Handelstag des Monats; Lookback 756 Handelstage; nur Industrien ohne NaN im Fenster
Sigma_hat wie in S3 (Ledoit-Wolf auf standardisierten Renditen, zurückskaliert)
w = argmin w' Sigma_hat w   s.t. sum(w) = 1,  0 <= w_i <= 0.05
Anwendung: Gewichte w_t gelten für die Tagesrenditen ab t+1 (kein Look-ahead)
```
Das Cap von 5 % ist **meine** Festlegung (vorab, nicht aus den Daten zu optimieren). Li/Kose nennen Min-/Max-Gewichte als Constraint-Art, die konkreten Werte habe ich nicht gesehen.

**Handelbare Umsetzung (gratis):** (a) ETF `USMV` (Start 2011-10-20) bzw. `SPLV` (heuristisch, Start 2011-05-05). (b) Die 9 Original-Sektor-SPDRs (XLK und XLU nachgewiesen ab 1998-12-22; die anderen Ticker nicht einzeln geprüft) mit derselben Optimierung und Cap 25 %. Hinweis: Das überlappt mit `lowrisk.md`, wo ein eigener ETF-Check für USMV und SPLV steht (weniger Vol, aber auch weniger Rendite als SPY seit 2011, kein Schutz im Corona-Crash).

**Zahlen aus Li/Kose 2015 (selbst gelesen), simulierte US-Min-Var-Portfolios aus den 1000 größten Aktien, Januar 1967 bis September 2014 (Tabelle 2):**
- Baseline Min-Var: Rendite 12,0 %, Vol 12,1 %, Sharpe 0,57.
- Mit allen Constraints (Kapazität, Sektor, Turnover): Rendite 11,6 %, Vol 13,0 %, Sharpe 0,50.
- Kapitalgewichtet: Rendite 10,3 %, Vol 15,4 %, Sharpe 0,34.
- Turnover laut Tabelle 1: 49,5 % Baseline, 20,0 % mit Turnover-Constraint (Einheit vermutlich einseitig pro Jahr; im Text nicht ausdrücklich gelesen).
- Aussage der Autoren: Constraints machen Min-Var investierbar, bewegen es aber Richtung Benchmark, das Risiko steigt, die Sharpe schwächelt, "mixed effects" bei der risikoadjustierten Performance. Die Baseline zeigt starke Sektorkonzentration (z. B. Versorger), niedrigere Bewertungskennzahlen als Benchmark in den USA (KGV 15,1 gegen 16,3).
- Quellenbias: Li/Kose sind bei Research Affiliates, die selbst heuristische Low-Vol-Produkte vertreten. Sie argumentieren, dass die heuristische Methode bei Kosten und Bewertung besser sei.

**Grenzen:** Min-Var ist ein Low-Beta-/Low-Vol-Faktor-Bet (Aktien), kein Diversifikationstrick. Seine Wirkung ist zinssensitiv und stark in Aktienkrisen, aber nicht konstant (2020: kein Schutz laut lowrisk.md).

### S5 `hrp_lopez_de_prado` — Hierarchical Risk Parity

**Quelle:** López de Prado 2016 (JPM 42(4), 59-69; gelesen wurde die SSRN-Fassung). Algorithmus, direkt aus dem Volltext:

**Regel:**
```
U = U9; Signal t = letzter Handelstag des Monats
r = tägliche Renditen der letzten 252 Handelstage bis inkl. t  (Paper-MC: 260; ich nehme 252)
C = Korrelationsmatrix(r);  V = Kovarianzmatrix(r)
Stufe 1 (Tree Clustering):
   d_ij = sqrt( (1 - C_ij) / 2 )                     # korrelations-basierte Distanz, Metrik
   D_ij = sqrt( sum_k (d_ki - d_kj)^2 )              # euklidische Distanz der Distanz-Spalten
   Linkage: scipy.cluster.hierarchy.linkage(squareform(D), method='single')   # wie im Paper-Code
Stufe 2 (Quasi-Diagonalisierung): Reihenfolge = Blätter des Dendrogramms (getQuasiDiag im Paper-Anhang)
Stufe 3 (Rekursive Bisektion):
   w_i = 1 für alle; Liste L = [alle Assets in Dendrogramm-Reihenfolge]
   solange ein Cluster in L Länge > 1 hat:
       teile jeden solchen Cluster in zwei Hälften  L1 = erste int(len/2), L2 = Rest  (Reihenfolge bleibt)
       für Hälfte j = 1,2:  V_j = w_j' * V_j * w_j  mit  w_j = IVP-Gewichte in der Hälfte  (IVP_k = (1/V_kk)/sum(1/V_ll))
       alpha = 1 - V_1/(V_1 + V_2)
       w in L1 *= alpha;  w in L2 *= (1 - alpha)
Ausführung: Open(t+1); keine Leverage
```
Referenzimplementierung im Paper-Anhang (Python, `scipy`), also deterministisch und gratis nachbaubar. `skfolio` und `HierPortfolios` (R) haben ähnliche Klassen (in Suchtreffern gesehen, nicht geprüft; Varianten wie HERC unterscheiden sich).

**Zahlen aus dem Paper (selbst gelesen):** Monte Carlo mit 10 Zufallsreihen (gaußsch, 520 Beobachtungen, Vol 10 %, plus zufällige Schocks und Korrelationsstruktur), Lookback 260 Tage, Rebalancing alle 22 Beobachtungen, 10.000 Wiederholungen. Out-of-Sample-Varianz: CLA 0,1157, IVP 0,0928, HRP 0,0671, also CLA 72,47 % und IVP 38,24 % höher als HRP. Mittlere Renditen ca. 0. Der Autor nennt "ca. 31,3 % bessere OOS-Sharpe" von HRP gegenüber CLA. Die Aussage, HRPs Vorteil werde bei größerem Universum, mehr Schocks oder Kosten **größer**, wird **ohne Daten** behauptet.

**Unabhängige Evidenz (nur sekundär gesehen):**
- Lohre/Rother/Schäfer (über Quantpedia): Multi-Asset-Multi-Faktor, Jan 2012 bis Dez 2017 (6 Jahre), Net-Sharpe: Original-HRP 0,94, ERC F 1,26, H IVP C 0,50, H ERC C 0,55. Turnover Original-HRP ca. 18 %, ERC-Risk-Parity ca. 5 %. Das heißt, in dieser einen kurzen Stichprobe liegt der einfache ERC-Risk-Parity-Ansatz vor Original-HRP.
- CBS-Masterarbeit (30 Industrie-Portfolios, Walk-forward): in einer Version HRP mit höchstem Sharpe, knapp vor IV; in einer anderen Version besser als IV/EW/ERC bei Risikokennzahlen, aber schlechter als Min-Var. Reis et al. (Brasilien): HRP nicht überall am besten. Suchzusammenfassungen, Qualität gering.

**Ehrliche Einordnung:** Das Originalpapier belegt mit Simulation, dass HRP die OOS-Varianz gegenüber CLA/IVP senkt, wenn die Kovarianz instabil geschätzt wird. Mit nur 9 Assets und 252 Tagen ist der Instabilitätsvorteil gering, weil die Kovarianzmatrix gut konditioniert ist. Der Algorithmus hat einen diskreten Teil (Dendrogramm-Reihenfolge, Single-Linkage-Chaining), Rangwechsel bei fast gleichen Korrelationen können zu Gewichtssprüngen führen (Plausibilitätsargument von mir, nicht belegt).

## 4. Nachpublikations-Verfall, Kosten, Tail-Risiken

| Thema | Befund |
|---|---|
| **1/N (S1)** | Der Vorteil ist relativ (Schätzfehler der Optimierer), er "verfällt" nicht durch Crowding. Er hängt von N, Stichprobenlänge und Universum ab. Kritik an Datenlänge und Signifikanz (Blog, Kritzman et al. 2010, nicht im Original gelesen). |
| **Risk Parity (S2, S3)** | AFP-Sample endet 2010, mitten in der Anleihenhausse. ABG (Abstract): Start-/Enddatum ändert die Ergebnisse materiell, Kosten können das Ranking drehen, besonders mit Leverage, und ein signifikanter Renditevorsprung garantiert keine Outperformance über realistische Horizonte. AQR-Antwort 2015 (Interessenkonflikt): 1947-2015 Brutto-Sharpe 60/40 = 0,52, einfaches RP = 0,75, beide ca. 10 % Vol, also ca. 2,5 % p. a. Renditevorsprung; Regression r_RP = 4,0 % + 0,70 * r_60/40; erst ab 4,0 % p. a. Kosten/Abschlag sei ein Teilanteil nicht mehr sinnvoll. Dieses "Beimischungs"-Argument ist theoretisch ok, ändert aber nichts daran, dass die **Brutto**-Sharpe 0,75 gegen reale Kosten (Futures-Roll, Finanzierung, Gebühren) steht. |
| **2022** | Nur Sekundärquellen: Risk-Parity-Fonds verloren stark (Bridgewater All Weather laut Blogs ca. -22 %), Aktien und Anleihen fielen gemeinsam. Eigener Check: siehe Abschnitt 5. Leverage auf Anleihen verstärkt das. |
| **Min-Var (S4)** | Constraints senken Rendite und Sharpe gegenüber der unrestringierten Baseline (Li/Kose). Mehr Turnover ohne Constraints (49,5 % Baseline). Eigener Check in lowrisk.md: seit 2011 kein Vorsprung vor SPY bei USMV/SPLV. |
| **HRP (S5)** | Originalpaper nur Simulation. Replikationen gemischt. Korrelationsbasierte Variante hat höheren Turnover (ca. 18 % im Lohre-Fall, laut Quantpedia, Einheit unklar). |
| **Kosten** | Alle Regeln hier sind monatlich mit 9 liquiden ETFs: bei 5 bp pro Seite sind die Kosten bei ERC/IVP klein, bei HRP und Min-Var mit höherem Turnover größer. Die Konstruktion mit Leverage braucht Finanzierung zu T-Bill plus Aufschlag. Das Ergebnis kippt laut ABG schnell. |
| **Steuer** | In den Papers nicht modelliert. Monatliches Umschichten realisiert Gewinne laufend (Quant-Lab-Regel 4: Abgeltungssteuer mitrechnen). |

**Tail-Risiken (gemeinsam):** (1) Regimewechsel der Aktien-Anleihen-Korrelation. (2) Zinsanstieg bei hohem Duration-Anteil (TLT: 2022 -31,2 %). (3) Volatilitäts-Schätzung hinkt hinterher: nach einem Vol-Schock ist das Gewicht der gerade volatilen Assets noch zu hoch (Mechanik, nicht aus Quelle). (4) Korrelations-Spitzen in Krisen (alle Aktienpositionen fallen gleichzeitig, 2008 und 2020 in U9: EFA -41,0 %, EEM -48,9 %, VNQ -37,0 %, DBC -31,8 % im Kalenderjahr 2008).

## 5. Eigener deskriptiver Check (yfinance, Stand 2026-10-09, `auto_adjust=True`, U9 plus SPY)

Kein Strategietest, nur Asset-Kennzahlen aus dem Zeitraum 2006-02-06 bis 2026-10-09 (5202 Handelstage, nur Tage, an denen alle Ticker Daten haben).

Kalenderjahresrenditen in Prozent:

| Jahr | DBC | EEM | EFA | GLD | IEF | SPY | TIP | TLT | VNQ | VTI |
|---|---|---|---|---|---|---|---|---|---|---|
| 2008 | -31,8 | -48,9 | -41,0 | 4,9 | 17,9 | -36,8 | 0,1 | 34,0 | -37,0 | -37,0 |
| 2013 | -7,6 | -3,6 | 21,4 | -28,3 | -6,1 | 32,3 | -8,5 | -13,4 | 2,3 | 33,4 |
| 2018 | -11,6 | -15,3 | -13,8 | -1,9 | 1,0 | -4,6 | -1,4 | -1,6 | -6,0 | -5,2 |
| 2020 | -7,8 | 17,0 | 7,6 | 24,8 | 10,0 | 18,3 | 10,8 | 18,2 | -4,6 | 21,1 |
| 2022 | 19,3 | -20,6 | -14,4 | -0,8 | -15,2 | -18,2 | -12,3 | -31,2 | -26,3 | -19,5 |
| 2023 | -6,2 | 8,9 | 18,4 | 12,7 | 3,6 | 26,2 | 3,8 | 2,8 | 11,9 | 26,0 |

Tägliche Korrelation SPY mit TLT (bzw. IEF) je Kalenderjahr: 2007 -0,39 (-0,51), 2008 -0,48 (-0,47), 2010 -0,55 (-0,52), 2011 -0,71 (-0,68), 2013 -0,21 (-0,12), 2019 -0,46 (-0,49), 2020 -0,48 (-0,51), 2021 -0,14 (-0,09), **2022 +0,08 (+0,19)**, 2023 +0,13 (+0,04), 2024 +0,06 (+0,07), 2025 +0,10 (-0,09), 2026 bis 09.10. +0,35 (+0,41).
Annualisierte Vol gesamt in %: IEF 6,8; TIP 6,2; TLT 14,8; GLD 18,5; SPY 19,2; DBC 19,3; EFA 21,3; EEM 28,0; VNQ 28,9. In 2022: IEF 10,2; TLT 20,3; SPY 24,2.
Max-Drawdown gesamt in %: IEF -23,9; TIP -14,5; TLT -48,4; GLD -45,6; SPY -55,2; DBC -76,4; VNQ -73,1. Max-Drawdown innerhalb 2022: IEF -18,2; TIP -14,3; TLT -36,6; SPY -24,5; DBC -23,2.

**Lesehilfe:** Die Blog-Zahl "Aktien-Anleihen-Korrelation 2022 ca. +0,65" (aus den Suchtreffern zu 2022) ist mit meiner einfachen Jahrestagesrechnung **nicht reproduziert** (dort +0,08 bis +0,19), vermutlich andere Fenster/Frequenz (24 Monate rollierend). Das Vorzeichen-Kippen gegenüber 2007-2020 ist dagegen in meinen Daten klar. Dass die positive Korrelation 2023-2026 anhielt, ist für jede Anleihen-lastige Regel relevant.

## 6. Nicht aufgenommene Kandidaten

- **Maximum-Diversification (Choueifaty/Coignard)**: nur als Referenzeintrag in Bruder/Roncalli gesehen, nicht gelesen.
- **Levered Risk Parity als eigener Eintrag**: als Variante L in S2 enthalten. Begründung: Der Mehrwert wird in der Kritik (ABG) und in 2022 am stärksten bestritten, und Leverage lässt sich im Quant-Lab (Budget, Privatanleger-Setup) nur mit Annahmen abbilden.
- **Sharpe Parity (Alpha Architect, Jan 2015)** und **HERC (Raffinot)**: nur als Suchtreffer-Titel gesehen, nicht geöffnet.

## 7. Empfohlenes Vorgehen im Quant-Lab (Vorschlag)

1. S1 bis S3 und S5 auf **identischem Universum U9 und identischen Daten** rechnen und gegen SPY-Buy&Hold, 60/40 (SPY/IEF) und S1 vergleichen. Wegen der kurzen Stichprobe (ca. 18,6 Jahre ab Feb 2008) vor allem Drawdown, Vol, Worst-Year und Turnover vergleichen, nicht nur Sharpe.
2. S2 zusätzlich auf der langen 2-Asset-Stichprobe (VFINX/VBMFX ab 1986-12-11) testen, um die Abhängigkeit von der Anleihenhausse sichtbar zu machen (Aufteilung: 1987-2020 gegen 2021-2026).
3. S4 nur als Forschungs-Harness (Ken French, ab 1926 laut Erinnerung) und mit USMV/SPLV als Reality-Check, weil lowrisk.md dort schon einen Check hat.
4. Vor Tests je eine Zeile in `docs/HYPOTHESEN.md` (Erwartung plus Abbruchkriterium). Vorschläge: S2: Net-Sharpe >= S1 und Max-DD kleiner als S1, sonst verwerfen. S3: nur behalten, wenn besser als S2 um >= 0,1 Sharpe oder deutlich kleinerer Drawdown. S5: nur behalten, wenn besser als S3 bei gleichem Turnover. Mehrfachtest-Korrektur (Deflated Sharpe) anwenden, da vier Konstruktionen auf denselben Daten verglichen werden.

## 8. Quellen-URLs (alle tatsächlich abgerufen oder in Suchtreffern gesehen; Tiefe siehe Abschnitt 1)

Gelesen (Volltext oder wesentliche Teile):
- AFP 2012: https://www.Aqr.Com/-/media/AQR/Documents/Insights/Journal-Article/Leverage-Aversion-and-Risk-Parity.pdf
- López de Prado, SSRN-Abstract: https://papers.ssrn.com/abstract=2708678 (Suchtreffer) und gelesene Kopie: https://www.smallake.kr/wp-content/uploads/2020/04/SSRN-id2708678.pdf
- Bruder/Roncalli 2012: https://mpra.ub.uni-muenchen.de/37246/1/MPRA_paper_37246.pdf
- AQR 2015: https://www.aqr.com/Insights/Perspectives/Risk-Parity-Is-Even-Better-Than-We-Thought?aqrPDF=1
- Li/Kose 2015: https://www.rafi.com/research/publications/articles/378-black-ice-low-volatility-investing-in-theory-and-practice
- Quantpedia HRP: https://quantpedia.com/hierarchical-risk-parity/
- Ken French (HEAD 200, nicht geladen): https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/49_Industry_Portfolios_daily_CSV.zip

Nur Abstract-/Metadaten-Ebene:
- ABG 2012: https://rpc.cfainstitute.org/research/financial-analysts-journal/2012/will-my-risk-parity-strategy-outperform ; IDEAS: https://ideas.repec.org/a/taf/ufajxx/v68y2012i6p75-93.html ; Kommentar (Suchtreffer): https://research.cbs.dk/en/publications/will-my-risk-parity-strategy-outperform-a-comment/ ; Autorenantwort (Suchtreffer): https://rpc.cfainstitute.org/research/financial-analysts-journal/2013/will-my-risk-parity-strategy-outperform-author-response
- DeMiguel et al. 2009: https://lbsresearch.london.edu/id/eprint/407 ; IDEAS: https://ideas.repec.org/a/oup/rfinst/v22y2009i5p1915-1953.html ; Kritik-Blog: https://www.r-bloggers.com/2013/06/the-fallacy-of-1n-and-static-weight-allocation/
- AFP IDEAS: https://ideas.repec.org/a/taf/ufajxx/v68y2012i1p47-59.html
- Chow/Kose/Li 2016: https://rpc.cfainstitute.org/en/research/financial-analysts-journal/2016/the-impact-of-constraints-on-minimum-variance-portfolios

Nur Suchtreffer (nicht belastbar):
- CAIA zu 2022: https://caia.org/node/7312 (Abruf 404)
- Alpha Architect: https://alphaarchitect.com/strategies-to-mitigate-tail-risk/ und https://alphaarchitect.com/does-sharpe-parity-work-better-than-risk-parity/
- HRP-Replikationen: https://periodicos.fgv.br/rbfin/article/download/89848/84802/201368 ; https://research-api.cbs.dk/ws/portalfiles/portal/76452070/1332322_Master_Thesis_Hierarchical_Risk_Parity.pdf
