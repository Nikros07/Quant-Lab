# Familie: Low-Risk / Betting-Against-Beta / Quality

Stand: 2026-10-11. Analyst: Quant-Research-Subagent. Sprache: Deutsch.
Ziel: implementierbare bzw. ehrlich bewertete Strategien mit **gratis Daten** (Yahoo/yfinance, Ken French, AQR-Datasets).

## 0. Kurzfazit (ehrlich)

1. **Faktor-Ebene (akademische Long/Short-Portfolios) funktioniert in den Papers, Handelbarkeit ist das Problem.**
   - BAB: Sharpe 0,78 (1926 bis 03/2012, FP 2014). Nach Handelskosten bleiben 48 bp/Monat, aber das verallgemeinerte Fama-French-5-Faktor-Alpha ist nur 16 bp/Monat und nicht signifikant (Novy-Marx/Velikov). BAB verdient seinen Nettoertrag über Profitabilitäts- und Investment-Tilts.
   - Gross-Profitability (Novy-Marx 2013) ist dagegen **kostenrobust**: jährliches Rebalancing, Handelskosten 3 bp/Monat, Netto-4-Faktor-Alpha 0,51 %/Monat (t = 3,77). Das ist der robusteste Eintrag der Familie.
   - Idiosyncratic-Volatility-L/S: brutto 0,63 %/Monat, netto 0,11 %/Monat (t = 0,37). Funktioniert nach Kosten nicht.
2. **Handelbare Gratis-Proxys (ETFs) zeigen seit 2011/2013 keinen Vorsprung vor SPY.** Eigener deskriptiver Check (Abschnitt 4): USMV und SPLV haben weniger Volatilität, aber auch weniger Rendite. SPHQ und QUAL liegen auf SPY-Niveau. Im Corona-Crash 2020 schützte keiner der Defensiv-ETFs (USMV minus 33,0 % gegen SPY minus 33,7 %).
3. **Low-Vol / Quality ist daher eher ein Risiko-Reduzierer oder Stil-Tilt als eine Alpha-Quelle** für diesen Aufbau. Das passt zum Erfolgsfall 2 im Quant-Lab (sicheres Portfolio), nicht zu Erfolgsfall 1 (belegter Edge nach Kosten und Steuern).
4. Ich habe **keine Strategie-Backtests** gerechnet (Regel 3 des Projekts: Hypothese vor Test). Die Zahlen in Abschnitt 4 sind nur deskriptive Kennzahlen der ETFs, kein Test der unten vorgeschlagenen Regeln.

## 1. Quellenstatus (was wirklich gesehen wurde)

Gesamt 16 Web-Abrufe (Search und Fetch), dazu lokale Auswertung von PDFs aus dem Session-Cache und ein yfinance-Check.

| Quelle | Tiefe |
|---|---|
| Frazzini/Pedersen 2014 "Betting Against Beta" (JFE 111(1), 1-25) | Volltext gelesen (Entwurf 10.05.2013 und veröffentlichte Fassung; Sharpe 0,78 steht in beiden) |
| Novy-Marx/Velikov "Betting Against Betting Against Beta" (WP Nov 2018; JFE Jan 2022 laut Sekundärquelle) | Volltext des WP gelesen |
| Novy-Marx/Velikov "A Taxonomy of Anomalies and Their Trading Costs" (NBER WP 20721, Dez 2014; 2016 publiziert, Journal aus Gedächtnis: RFS) | Tabellen 2 und 3 und Text gelesen |
| Asness/Frazzini/Pedersen "Quality Minus Junk" (Review of Accounting Studies 24(1), 34-112, 2019) | Konstruktion und Tabelle 4 gelesen (publizierte Fassung) |
| Novy-Marx 2013 "The Other Side of Value" (JFE 108(1), 1-28) | **nur Abstract** über Suchzusammenfassung, Volltext nicht gelesen |
| Blitz/van Vliet 2007 "The Volatility Effect" (JPM 34(1), 102-113) | **nur Abstract** über Suchzusammenfassung (SSRN-Fetch gab 403), Regel über Quantpedia-Seite |
| Baker/Bradley/Wurgler 2011 (FAJ 67(1), 40-54) | **nur Metadaten und Kernargument** über Suchzusammenfassung, Abstract nicht im Wortlaut gesehen |
| AQR-Dataset-Seiten (BAB, QMJ) | Seiten abgerufen, **Excel-Dateien nicht heruntergeladen** (Download braucht Freigabe von Nick) |
| Ken French Data Library (Übersichtsseite) | Seite abgerufen, Dateinamen ja, **Startdaten stehen nicht auf der Seite**, Dateien nicht geladen |
| Quantpedia "Low Volatility Factor Effect in Stocks" | Seite abgerufen |

**Nicht abgerufen (nur als Suchtreffer-Erwähnung, deshalb nicht in der Papierliste und nicht belastbar):** McLean/Pontiff (Verfall nach Publikation), Jensen/Kelly/Pedersen, Perras/Reberger/Wagner 2020 (Low-Vol in US/Europa/Deutschland), Clarke/de Silva/Thorley (Minimum Variance), Ang et al. 2006 (IVOL). Wer das braucht, muss es nachladen.

**Lücke:** Ich habe in den 16 Abrufen **keine Arbeit 2015-2026 gefunden und gelesen**, die den Low-Vol-/Quality-Verfall nach Publikation direkt misst. Die jüngste gelesene Arbeit ist Novy-Marx/Velikov (BABAB, 2018/2022). Der Nachpublikationsbefund stützt sich deshalb auf meinen eigenen ETF-Check (Abschnitt 4).

## 2. Strategien (nach erwarteter Robustheit sortiert)

### S1 `gp_quality_profitability` — Gross-Profitability / Quality-Tilt (jährlich)

**Quelle der Idee:** Novy-Marx 2013 (Gross Profits/Assets sagt die Querschnittsrenditen etwa so gut voraus wie Book-to-Market; Abstract über Suchzusammenfassung). Kostenzahlen aus Novy-Marx/Velikov (Taxonomy, Tabelle 3).

**Originalregel (nicht gratis machbar, Compustat nötig):** Jedes Jahr Ende Juni t: GP/A = (Umsatz minus Warenkosten) / Aktiva mit Geschäftsjahr t-1, Dezile mit NYSE-Breakpoints, wertgewichtet, Long oberstes Dezil, Short unterstes, Halten Juli t bis Juni t+1.

**Gratis-Umsetzung A (Faktor-Ebene, Forschungs-Harness, nicht handelbar):**
- Ken French "Portfolios Formed on Operating Profitability" (`ftp/Portfolios_Formed_on_OP_CSV.zip`) und "Fama/French 5 Factors (2x3)" (`ftp/F-F_Research_Data_5_Factors_2x3_CSV.zip`, enthält RMW, Mkt-RF, SMB, HML, CMA, RF).
- Rendite je Monat m: `r_LS(m) = r(OP oberstes Quintil/Dezil, wertgew.) - r(OP unterstes)`. Long-only-Variante: `r(OP oben) - RF` gegen `Mkt-RF`.
- Keine Look-ahead-Gefahr, weil French die Portfolios nach der Standardkonvention (Bilanzdaten Geschäftsjahr t-1, Bildung Ende Juni t) bildet. Startdatum der OP-Datei steht nicht auf der Seite. Laut Novy-Marx/Velikov (Fußnote 4) sind die FF5-Faktoren RMW/CMA erst **nach Juni 1963** verfügbar, die OP-Datei dürfte ähnlich beginnen. Das ist beim Download zu prüfen.

**Gratis-Umsetzung B (handelbar, ETF):** 100 % SPHQ (Yahoo-Start 2005-12-06), alternativ QUAL (2013-07-18) oder COWZ (2016-12-22, Free-Cash-Flow-Tilt), Benchmark SPY. Kein Signal, keine Rebalancing-Logik, Kauf zum Eröffnungskurs des ersten Handelstags. Auswertung nur als Aktivrendite und Tracking Error gegen SPY.

**Evidenz (gelesen):**
- Taxonomy (Tabelle 3, Wertgewicht, Dezil-L/S, jährlich, 07/1963-12/2012): Gross Profitability brutto 0,40 %/Monat (t = 2,94), 4-Faktor-Alpha 0,52 (t = 3,83), Handelskosten 0,03 %/Monat, **netto 0,37 (t = 2,74), Netto-Alpha 0,51 (t = 3,77)**. Die Spalte "TO" ist 1,96 (einseitig, %/Monat laut Textzusammenhang).
- Kombination "ValProf" (Rangsumme aus Book-to-Market und Gross Profitability, jährlich): brutto 0,82 (t = 5,18), Kosten 0,06, netto 0,77 (t = 4,82), Netto-Alpha 0,49 (t = 3,93). Das ist die stärkste kostenbereinigte Zeile aller niedrig umschlagenden Anomalien in Tabelle 3 und eine sinnvolle Erweiterung (Value plus Quality), liegt aber knapp außerhalb der Familie.
- Novy-Marx/Velikov (BABAB): Der reine Beta-Arbitrage-Ertrag stammt zu einem großen Teil aus Profitabilitäts- und Investment-Tilts (Ladungen von wertgewichtetem BAB: 0,45 auf RMW, 0,50 auf CMA). Profitabilität ist also der Kern, den Low-Beta nur indirekt einsammelt.

**Ehrliche Einschränkungen:**
- ETF-Check seit 2011/2013: SPHQ Sharpe (rf = 0) 0,94 gegen SPY 0,94, CAGR 15,09 % gegen 15,23 % (ab 21.10.2011). QUAL 0,84 gegen 0,87, CAGR 13,74 % gegen 14,19 % (ab 19.07.2013). **Kein messbarer Vorsprung.** SPHQ fiel im Crash 2008/09 (01.09.2008 bis 09.03.2009) um 48,6 % gegen 46,0 % bei SPY, ist also kein Krisenschutz.
- Die ETFs verwenden eigene Indexmethoden (Mischungen aus ROE, Verschuldung, Accruals), nicht Gross Profitability. Faktor-Ebene und ETF-Ebene sind nicht dasselbe.
- Verfall nach Publikation (2013): **nicht gemessen gefunden**. Offen. Empfehlung: Faktor-Ebene aufteilen in Stichprobe bis 2012 und ab 2013.

**Vor-Registrierung (Vorschlag für docs/HYPOTHESEN.md):** Erwartung: ETF-Aktivrendite gegen SPY nicht von null unterscheidbar. Abbruch: Wenn Sharpe-Differenz (Bootstrap, 95 %-Intervall) null einschließt, kein Einsatz als Alpha-Strategie.

---

### S2 `lowvol_defensive_longonly` — Low-Volatility, Long-only (defensiv)

**Quelle:** Blitz/van Vliet 2007. Abstract (Suchzusammenfassung): Globale Low- gegen High-Vol-Dezile haben einen jährlichen Alpha-Spread von etwa 12 % (1986-2006), ebenfalls einzeln in USA, Europa und Japan, nicht durch Value und Size erklärt. Regelbeschreibung laut Quantpedia (Seite abgerufen): historische Volatilität der Wochenrenditen über 3 Jahre, gleichgewichtete Dezile, Long nur Dezil mit niedrigster Vol, monatliches Rebalancing, ohne Transaktionskosten; Quantpedia nennt für das Long-only-Dezil 11,3 % p.a., Vol 10,1 %, Sharpe 0,72 (1986-2006, Risikofreizins 4 % von Quantpedia **geschätzt**). Baker/Bradley/Wurgler 2011: Erklärung über Benchmark-Zwang institutioneller Anleger (Limits to Arbitrage), Low-Vol/Low-Beta Portfolios hatten 1968-2008 hohe Durchschnittsrenditen bei kleinen Drawdowns (Suchzusammenfassung).

**Gratis-Umsetzung A (ETF, handelbar, Buy-and-Hold gegen SPY):** USMV (Start 2011-10-20), SPLV (2011-05-05), EFAV (2011-10-20, Industrieländer ex US), EEMV (2011-10-20, Schwellenländer), XSLV (2013-02-15, Small-Cap Low-Vol). Kein Signal.

**Gratis-Umsetzung B (eigener Sektor-Proxy, 100 % abgeleitet, kein Paper dazu, ungetestet):**
```
UNIVERS = [XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY]    # Yahoo-Start 1998-12-22 (geprüft)
am letzten Handelstag t jedes Monats (Schlusskurs):
    w_i  = Wochenrenditen (letzter Handelstag der Woche, adjustierter Schlusskurs) der letzten 156 Wochen
    vol_i = stdev(w_i)                      # mindestens 156 Wochen nötig, erstes Signal ca. Ende 2001
    wähle die 3 ETFs mit kleinster vol_i
    Zielgewicht: je 1/3, sonst 0
Ausführung: Eröffnungskurs des nächsten Handelstags t+1, Halten bis zum nächsten Monatsultimo
Benchmarks: SPY, Gleichgewicht über dieselben 9 Sektoren, dieselbe Zeit
Kosten-Annahme (zu verifizieren): 5 bp je Seite
```
Hinweis: Sektor-Low-Vol erfasst nur den Sektor-Tilt, nicht die Titelselektion innerhalb der Sektoren. Es ist ein Proxy, kein Replikat von Blitz/van Vliet. XLRE (2015-10-08) und XLC (2018-06-19) bewusst ausgelassen, damit die Universumsgröße konstant bleibt.

**Gratis-Umsetzung C (Faktor-Ebene):** Ken French "Portfolios Formed on Variance" (`Portfolios_Formed_on_VAR_CSV.zip`), "...on Market Beta" (`Portfolios_Formed_on_BETA_CSV.zip`), "...on Residual Variance". Niedrigstes minus höchstes Dezil/Quintil und Long-only-niedrigstes, jeweils wertgewichtet. Stichprobe teilen: bis 2007 (Blitz/van Vliet) und ab 2008. Startdaten stehen nicht auf der Seite (Download prüfen).

**Eigene deskriptive Zahlen (Abschnitt 4):** Seit 21.10.2011: USMV CAGR 11,73 %, Vol 13,35 %, Sharpe (rf = 0) 0,90, MaxDD minus 33,10 %. SPLV 9,93 %, 14,25 %, 0,74, minus 36,26 %. SPY 15,23 %, 16,66 %, 0,94, minus 33,72 %. **Weniger Risiko, aber auch weniger Rendite, Sharpe nicht besser.**

**Nachpublikation und Tail-Risiken:**
- Das Risiko-Versprechen "weniger Verlust im Crash" hielt im Corona-Crash nicht: 19.02. bis 23.03.2020 SPY minus 33,7 %, USMV minus 33,0 %, SPLV minus 35,8 %.
- In Aufwärtsjahren großes Zurückbleiben: 2023 USMV plus 10,3 % und SPLV plus 0,5 % gegen SPY plus 26,2 %. 2025: 7,6 % und 4,1 % gegen 17,7 %. 2026 bis 09.10.: 7,9 % und 2,7 % gegen 15,1 %.
- Ein Vorteil zeigte sich 2022 (USMV minus 9,4 %, SPLV minus 4,9 %, SPY minus 18,2 %).
- Ein Befund aus der Suche (nur Zusammenfassung, nicht gelesen): Low-Vol sei in Bullenmärkten stärker. Das passt nicht zu meinem Datenbild und ist nicht belegt.

**Vor-Registrierung:** Erwartung: Sharpe-Differenz gegen SPY um null, Max-Drawdown nicht klar besser. Der einzige Nutzen wäre geringere Volatilität. Abbruch: kein Einsatz als Alpha-Strategie, nur als Baustein falls Vol-Reduktion bei gleichem Sharpe gewünscht.

---

### S3 `qmj_quality_minus_junk_series` — Quality Minus Junk (Faktor-Ebene via AQR-Reihe)

**Quelle:** Asness/Frazzini/Pedersen (Review of Accounting Studies 24(1), 34-112, 2019).

**Originalregel (gelesen, Anhang-Details nicht vollständig geprüft):**
```
Qualität = z( Profitabilität + Wachstum + Sicherheit )
  Profitabilität = z( z(GPOA)+z(ROE)+z(ROA)+z(CFOA)+z(GMAR)+z(-ACC) )
  Wachstum       = z( 5-Jahres-Veränderung der pro-Aktie-Residualgewinn-Kennzahlen von GPOA,ROE,ROA,CFOA,GMAR, ohne Accruals, geteilt durch den verzögerten Nenner )
  Sicherheit     = z( z(-BAB-Beta)+z(-Leverage)+z(-O-Score)+z(-Z-Score-Risiko)+z(-EVOL) )   # EVOL = ROE-Volatilität
  z(x)           = (Rang(x) - Mittelwert(Rang)) / Std(Rang), querschnittlich je Monat
Fehlt eine Kennzahl, wird der Durchschnitt der übrigen genommen.
Bilanzdaten: Geschäftsjahre, die in Kalenderjahr t-1 enden, gelten ab Juni t (FF-Konvention)
QMJ = 1/2 (Small Quality + Big Quality) - 1/2 (Small Junk + Big Junk)
  Größe: NYSE-Median (USA), 80. Perzentil je Land (Ausland); Long oberste 30 %, Short unterste 30 % der Qualität;
  wertgewichtete Portfolios, monatlich neu gebildet; Ländergewichtung nach Marktkapitalisierung.
```
Die AQR-Seite nennt zusätzlich **Payout** als Qualitätsdimension, die publizierte Fassung hat drei Dimensionen (Payout steht als eigene Variante im Anhang, Fußnote 13). Konstruktion der AQR-Reihe und des Papers sind also nicht garantiert identisch.

**Gratis-Daten:** AQR "Quality Minus Junk: Factors, Monthly" (`https://www.aqr.com/-/media/AQR/Documents/Insights/Data-Sets/Quality-Minus-Junk-Factors-Monthly.xlsx`), USA plus 23 Auslandsmärkte, Seitendatum 31.07.2026. Die Social-Text-Angabe der Seite nennt Beginn 1956 (USA) und 1986 (Global), das Paper nennt Juni 1957 und Juni 1989 für Renditen. **Beginn bitte nach dem Download selbst prüfen.** Aus Yahoo ist die Faktorbildung nicht rekonstruierbar (keine Point-in-Time-Bilanzen).

**Gratis-Umsetzung (Faktor-Ebene):** Monatliche QMJ-USA-Reihe direkt als Renditezeitreihe; Auswertung: Sharpe, Alpha gegen FF5 plus UMD (French-Dateien), Teilstichproben bis 2012 und ab 2013, dazu der Beitrag von RMW. Eine handelbare Version gibt es nicht; als Hilfsproxy kommt S1 (SPHQ, QUAL) infrage.

**Evidenz (gelesen, Tabelle 4):**
- USA 07/1957-12/2016: Excess Return 0,29 %/Monat (t = 3,62), CAPM-Alpha 0,39, 3-Faktor 0,51, 4-Faktor 0,60 (t = 9,95), Sharpe 0,47, Marktbeta minus 0,20.
- Global (Broad Sample): Excess Return 0,38 (t = 3,33), 4-Faktor-Alpha 0,61 (t = 8,07), Sharpe 0,64. Tabellenkopf nennt 7/1998 und die Fußnote 6/1989 (Inkonsistenz im Text).
- Positiv in 23 von 24 Ländern. Die Autoren sehen keine Crash-Risiko-Struktur, sondern eine milde positive Konvexität (Flucht in Qualität).
- **Robustheit zu FF5:** Mit RMW/CMA im Modell sinken die Alphas auf 16 bis 38 bp/Monat, die meisten bleiben signifikant. QMJ lädt stark auf RMW (Gross Profitability ist Teil der Profitabilitäts-Komponente), die Idee überlappt also mit S1.
- Der "Price of Quality" war im Internet-Hoch minimal (Februar 2000) und sagt die künftige QMJ-Rendite negativ voraus.

**Lücken:** Handelskosten und Kapazität von QMJ im Paper: in dem, was ich gelesen habe, **keine Netto-Zahl gefunden**. Nachpublikations-Verfall: nicht gefunden. Eine Masterarbeit, die QMJ auf 44 Länder (2005-2019) erweitert, fand laut Suchzusammenfassung Alphas in 43 von 44 Ländern (nicht abgerufen, nicht peer-reviewed). Eine praxisnahe Studie fand mit anderer Qualitätsdefinition (ROIC, Accruals, Wachstum, Verschuldung) für 2005-2015 deutlich schlechtere QMJ-Renditen: Das Ergebnis hängt stark von der Kennzahlenauswahl ab (ebenfalls nur Suchzusammenfassung).

**Vor-Registrierung:** Erwartung: positive Reihe, aber kleineres Alpha nach FF5 und nach 2013. Abbruch: QMJ-Alpha ab 2013 nicht signifikant → Quality nur als Risiko-Baustein.

---

### S4 `bab_beta_neutral_etf_pair` — Betting Against Beta (beta-neutral)

**Quelle:** Frazzini/Pedersen 2014. Kritik und Kosten: Novy-Marx/Velikov (BABAB).

**Originalregel (gelesen, Entwurf Mai 2013, Sharpe-Aussage in beiden Fassungen gleich):**
```
Beta je Aktie i, Monatsultimo t:
  sigma_i, sigma_m  = 1-Jahres-rollende Std. der 1-Tages-Logrenditen (mind. 120 Handelstage)
  rho               = 5-Jahres-rollende Korrelation der überlappenden 3-Tages-Logrenditen (mind. 750 Handelstage)
  beta_TS = rho * sigma_i / sigma_m
  beta    = 0.6 * beta_TS + 0.4 * 1.0                  # Shrinkage nach Vasicek, w = 0.6
Rang z_i = rank(beta_i), zbar = Mittelwert(z)
  w_H = k * max(z - zbar, 0),  w_L = k * max(zbar - z, 0),  k = 2 / sum|z - zbar|   (je Seite Summe 1)
  beta_L = beta' w_L,  beta_H = beta' w_H
BAB_{t+1} = (1/beta_L) * (r_L - rf) - (1/beta_H) * (r_H - rf)       # monatlich neu gewichtet
Universum: alle US-Stammaktien (CRSP), 1926 bis 03/2012
```

**Gratis-Umsetzung A (Faktor-Ebene):** AQR "Betting Against Beta: Equity Factors, Monthly/Daily" (`.../Betting-Against-Beta-Equity-Factors-Monthly.xlsx`; 23 Auslandsmärkte plus USA, Seitendatum 31.07.2026; zusätzlich "Original Paper Data" vom 27.02.2018). **Achtung:** Novy-Marx/Velikov berichten, dass die Original-Paper-Reihe (Ende 03/2012) und die laufend gepflegte Reihe nur zu 96,2 % korrelieren (nach 1967) und die Original-Reihe eine signifikant höhere Sharpe hat. Beide Reihen getrennt auswerten und Teilstichprobe ab 04/2012 gesondert melden. Startdatum der Reihen nicht auf der Seite.

**Gratis-Umsetzung B (handelbarer ETF-Proxy, abgeleitet, ungetestet):**
```
L = SPLV (Start 2011-05-05),  H = SPHB (Start 2011-05-05),  M = SPY,  cash = ^IRX als Zinsproxy
am Monatsultimo t (Schlusskurs):
   beta_L, beta_H = OLS-Beta der täglichen Überschussrenditen von L bzw. H auf M über 252 Handelstage
   beta_k = 0.6 * beta_k + 0.4 * 1.0                  # FP-Shrinkage
   Gewichte: +1/beta_L in L,  -1/beta_H in H           # beta-neutral, Rest Cash
Ausführung: Eröffnungskurs t+1, Halten bis zum nächsten Monatsultimo
Kosten (ANNAHMEN zu verifizieren): ETF-Spread, Marginzins auf ca. 1,4x Long und 0,7x Short, Leihgebühr SPHB (nicht frei verfügbar, Stresstest 0,5 bis 1,5 % p.a.)
```
Warnung aus meinem Check: ein **naives** 50/50-Paar (Long SPLV, Short SPHB, täglich rebalanciert, ohne Beta-Skalierung) hatte 2011-05-05 bis 2026-10-09 CAGR minus 8,62 %, Vol 21,85 %, MaxDD minus 82,98 %, Beta zu SPY minus 0,75. Das ist ein verkappter Short auf den Markt und **kein Test von BAB**. Eine beta-neutrale Variante wurde absichtlich nicht gerechnet (Hypothese vor Test).

**Evidenz (gelesen):**
- FP: Sharpe 0,78 (US, 1926 bis 03/2012; etwa doppelt so hoch wie Value, 40 % über Momentum), Volatilität 10,7 %, Excess Return 0,70 %/Monat (Tabelle III im Entwurf, Spaltenlayout in der PDF-Extraktion verrutscht, Sharpe 0,78 und Vol 10,7 sind eindeutig). Positiv in jedem der vier 20-Jahres-Abschnitte. In den 19 weiteren MSCI-Industrieländern positive Sharpe in 18.
- Novy-Marx/Velikov (BABAB, Stichprobe 01/1968-12/2017): BAB steckt pro Dollar im Schnitt 1,05 USD in Aktien unterhalb der untersten 1 % der Marktkapitalisierung. Die rangbasierte Gewichtung entspricht faktisch Gleichgewichtung. Wertgewichtetes BAB: Excess Return 56 bp/Monat (t = 3,48), Sharpe 0,49 gegen 1,08 beim Original-BAB, FF5-Alpha nur 24 bp (t = 1,63).
- **Kosten:** Durchschnittlich 60 bp/Monat (26 bp in den letzten 10 Jahren). Netto 48 bp/Monat (t = 3,30), aber verallgemeinertes FF5-Alpha nur 16 bp (t = 1,20). Ohne die untersten Dezile: Kosten 23 bp, netto 47 bp (t = 3,37), Alpha 15 bp (t = 1,23). Kapitalisierungsgewichtete, "implementierbare" Version: Kosten 8 bp, netto 43 bp (t = 2,75), Alpha 19 bp (t = 1,36). **Die Netto-Alphas sind in allen Varianten statistisch nicht von null verschieden.**
- Die Beta-Schätzung ist laut Novy-Marx/Velikov mit der Einzelaktien-Volatilität vermengt und im Zeitverlauf vorhersehbar verzerrt; BAB nimmt zudem bei hoher Marktvolatilität weniger Marktrisiko (implizites Vol-Timing).

**Tail-Risiken:** Hebel (ca. 2x Brutto-Exposure beim ETF-Paar), Korrelationssprünge, Short-Squeeze bei SPHB-Short, Marginanrufe. Der ETF-Proxy hat nur etwa 15 Jahre Historie und ist stark von den Indexregeln abhängig (Methodik nicht geprüft). Steuerliche Behandlung von Short- und Hebelpositionen in Deutschland nicht recherchiert.

**Vor-Registrierung:** Erwartung: Netto-Sharpe des ETF-Paars klar unter dem FP-Wert, Alpha gegen FF5 nicht signifikant. Abbruch: Netto-Sharpe unter 0,3 oder Beta zu SPY (Rolling) außerhalb von plus/minus 0,2.

---

### S5 `ivol_lowvar_ls` — Idiosynkratische Volatilität, Long/Short (funktioniert nach Kosten nicht)

**Quelle:** Zahlen aus Novy-Marx/Velikov (Taxonomy, Tabelle 3, Mid-Turnover): monatlich neu gebildet, wertgewichtete Dezil-L/S, NYSE-Breakpoints, 07/1963-12/2012. IVOL gemessen als Residualvolatilität (Ang et al. 2006 wird in der Tabelle als Referenz genannt, Paper nicht gelesen).

**Regel (für den Faktor-Harness):**
```
Daten: Ken French "Portfolios Formed on Residual Variance" (Portfolios_Formed_on_RESVAR_CSV.zip), wertgewichtet
r_LS(m) = r(niedrigstes Dezil/Quintil) - r(höchstes Dezil/Quintil)
Long-only: niedrigstes minus RF
```
Details der French-Konstruktion (Fenster der Residualvarianz) stehen auf `Data_Library/det_port_form_RESVAR.html`, **nicht abgerufen**.

**Evidenz:** Brutto 0,63 %/Monat (t = 2,13), **netto 0,11 %/Monat (t = 0,37)**. Der Text: IVOL und Ausfallwahrscheinlichkeit sind nach Kosten nur "marginal profitabel". Die Netto-Zeile habe ich aus dem PDF-Layout rekonstruiert und gegen zwei Zeilen mit bekannten Textwerten (ValMomProf 99 bp, ValMom 51 bp) abgeglichen.

**Ehrliches Fazit:** Die Short-Seite (hoch volatile Kleinaktien) ist teuer und kaum handelbar. Der brauchbare Teil des Effekts ist die Long-only-Seite, also S2. Als eigene Strategie nicht empfohlen. Der Eintrag dient als Negativ-Kontrolle für die Kostenannahmen im Harness.

## 3. Daten-Cheatsheet (alles gratis)

| Zweck | Quelle | Anmerkung |
|---|---|---|
| ETF-Preise | yfinance, `auto_adjust=True` | Total-Return-Proxy, Start-Daten in Abschnitt 4 |
| FF5, RMW, Momentum | Ken French: `F-F_Research_Data_5_Factors_2x3_CSV.zip`, `F-F_Momentum_Factor_CSV.zip` | Startdatum nicht auf Seite; FF5 laut Novy-Marx/Velikov ab Juli 1963 |
| Beta/Varianz/Profitabilität | Ken French: `Portfolios_Formed_on_BETA`, `_VAR`, `_RESVAR`, `_OP`, `25_Portfolios_ME_OP_5x5` (jeweils `_CSV.zip` unter `ftp/`) | Basis-URL laut Seite: `http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/` |
| BAB, QMJ | AQR Data Library (Excel) | Download braucht Freigabe von Nick |
| Zinsproxy | `^IRX` (Start 1990-01-02), `^VIX` (1990-01-02) | geprüft |

Nicht gratis und deshalb nicht umsetzbar: Compustat-Bilanzdaten (GP/A, O-Score), CRSP-Einzelaktien, Leihgebühren, Intraday-Spreads.

## 4. Eigener deskriptiver Check (kein Strategie-Backtest)

Skript: `C:\Users\spide\AppData\Local\Temp\claude\C--Users-spide-Desktop\fd8c6e7d-2582-491e-b8b4-e35ec2d76021\scratchpad\lowrisk_etf_check.py`, ausgeführt mit der Quant-Lab-`.venv` am 2026-10-11, letzter Datenpunkt 2026-10-09. Preise `auto_adjust=True`, Tagesrenditen, Sharpe mit rf = 0 (Gesamtrendite, nicht Überschuss), keine Steuern, keine Handelskosten (Fondsgebühren stecken im Kurs).

Yahoo-Startdaten (geprüft): SPY 1993-01-29, SPHQ 2005-12-06, SPLV 2011-05-05, SPHB 2011-05-05, USMV 2011-10-20, EFAV 2011-10-20, EEMV 2011-10-20, XSLV 2013-02-15, VLUE 2013-04-18, QUAL 2013-07-18, DGRO 2014-06-12, COWZ 2016-12-22, JQUA 2017-11-09, SPHD 2012-10-26, XLB/XLE/XLF/XLI/XLK/XLP/XLU/XLV/XLY 1998-12-22, XLRE 2015-10-08, XLC 2018-06-19, IWM 2000-05-26, IEF 2002-07-30.

**Fenster ab 2011-10-21:**

| ETF | CAGR | Vol | Sharpe (rf=0) | MaxDD |
|---|---|---|---|---|
| SPY | 15,23 % | 16,66 % | 0,94 | -33,72 % |
| USMV | 11,73 % | 13,35 % | 0,90 | -33,10 % |
| SPLV | 9,93 % | 14,25 % | 0,74 | -36,26 % |
| SPHB | 16,74 % | 26,70 % | 0,71 | -46,84 % |
| SPHQ | 15,09 % | 16,30 % | 0,94 | -31,59 % |
| EFAV | 7,04 % | 12,90 % | 0,59 | -27,56 % |
| EEMV | 5,47 % | 14,65 % | 0,44 | -31,56 % |

**Fenster ab 2013-07-19:** SPY 14,19 % / 0,87; QUAL 13,74 % / 0,84 / MaxDD -34,06 %; SPHQ 13,96 % / 0,87; COWZ (ab 2016-12) 13,19 % / 0,73 / MaxDD -38,63 %.

**Jahresrenditen (Gesamtrendite, %)**, Auswahl: 2020 SPY 18,3 / USMV 5,6 / SPLV -1,4 / QUAL 17,0 / SPHQ 16,9. 2022 SPY -18,2 / USMV -9,4 / SPLV -4,9 / QUAL -20,5 / SPHQ -15,8. 2023 SPY 26,2 / USMV 10,3 / SPLV 0,5 / QUAL 30,9 / SPHQ 24,8. 2025 SPY 17,7 / USMV 7,6 / SPLV 4,1 / QUAL 12,7 / SPHQ 13,3. 2026 bis 09.10. SPY 15,1 / USMV 7,9 / SPLV 2,7 / QUAL 15,0 / SPHQ 15,3.

**Crashfenster:** 19.02.-23.03.2020: SPY -33,7 %, USMV -33,0 %, SPLV -35,8 %, QUAL -34,1 %, SPHQ -31,4 %, SPHB -46,5 %. 01.09.2008-09.03.2009: SPY -46,0 %, SPHQ -48,6 %.

Lesart: Die Zahlen sind Beschreibung, keine Evidenz für oder gegen die Faktoren. Fenster ist kurz (ein Zyklus), die Indexmethoden der ETFs sind nicht die der Papers.

## 5. Offene Punkte

- Startdaten der French-Dateien (BETA, VAR, RESVAR, OP) und Spaltenstruktur nach dem Download prüfen. Die Seite nennt sie nicht.
- AQR-Excel erst nach Freigabe von Nick herunterladen; vorher Blattnamen und Beginn der Reihen unbekannt.
- Zwei Veröffentlichungsstände von BAB (Original bis 03/2012, laufende Reihe) getrennt behandeln.
- Nachpublikations-Verfall für Gross Profitability, QMJ und Low-Vol nach 2013 beziehungsweise 2007: nicht durch gelesene Quellen belegt. Mit Teilstichproben im Harness selbst messen und Mehrfachtest-Korrektur anwenden (Projektregel 4).
- Falls später mehr Literatur gewünscht: McLean/Pontiff, Jensen/Kelly/Pedersen, Clarke et al. (Minimum Variance), Ang et al. 2006 (IVOL), Perras et al. 2020 nachladen und tatsächlich lesen.

## 6. Quellen-URLs

Gelesen (Volltext oder relevante Abschnitte):
- Frazzini/Pedersen 2014 (veröffentlicht): https://research-api.cbs.dk/ws/portalfiles/portal/60082899/lasse_heje_pedersen_et_al_betting_against_beta_publishersversion.pdf
- Frazzini/Pedersen (Entwurf 10.05.2013): https://www.johnhcochrane.com/s/BettingAgainstBeta.pdf (Weiterleitung auf static1.squarespace.com)
- Novy-Marx/Velikov, Betting Against Betting Against Beta (WP Nov 2018): https://mysimon.rochester.edu/novy-marx/research/BABAB.pdf ; Verlagsnachweis laut Suchtreffer: https://pure.psu.edu/en/publications/betting-against-betting-against-beta/
- Novy-Marx/Velikov, A Taxonomy of Anomalies and Their Trading Costs (NBER WP 20721): http://www.nber.org/papers/w20721 (Titelseite der gelesenen PDF)
- Asness/Frazzini/Pedersen, Quality Minus Junk (veröffentlicht): https://research-api.cbs.dk/ws/portalfiles/portal/60211462/lasse_heje_pedersen_et_al_quality_minus_junk_publishersversion.pdf ; Verlagsnachweis: https://ideas.repec.org/a/spr/reaccs/v24y2019i1d10.1007_s11142-018-9470-2.html
- AQR BAB-Dataset-Seite: https://www.aqr.com/Insights/Datasets/Betting-Against-Beta-Equity-Factors-Monthly
- AQR QMJ-Dataset-Seite: https://www.aqr.com/Insights/Datasets/Quality-Minus-Junk-Factors-Monthly
- Ken French Data Library: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
- Quantpedia Low Volatility: https://quantpedia.com/strategies/low-volatility-factor-effect-in-stocks

Nur Abstract oder Suchzusammenfassung (Volltext nicht gelesen):
- Novy-Marx 2013: https://ideas.repec.org/a/eee/jfinec/v108y2013i1p1-28.html ; Working Paper: https://www.nber.org/system/files/working_papers/w15940/w15940.pdf
- Blitz/van Vliet 2007: https://papers.ssrn.com/abstract=980865 (direkter Abruf: 403) ; Suchtreffer RePEc: https://ideas.repec.org/p/ems/eureri/10460.html
- Baker/Bradley/Wurgler 2011: https://papers.ssrn.com/abstract=1745108 ; https://www.cfainstitute.org/en/research/financial-analysts-journal/2011/benchmarks-as-limits-to-arbitrage-understanding-the-low-volatility-anomaly
- Alpha-Architect-Zusammenfassung zu BAB-Konstruktion (Suchtreffer, nicht gelesen): https://alphaarchitect.com/2019/08/betting-against-beta-bab-construction/
- Quantpedia "Biased Betting Against Beta?" (Suchtreffer, nicht gelesen): https://quantpedia.com/biased-betting-against-beta/
