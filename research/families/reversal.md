# Familie: Short-term Reversal / Mean Reversion

Stand der Recherche: 2026-10-11. Budget: ca. 15 Web-Abrufe (WebSearch + WebFetch), real 16 plus ein Header-/Seitenabruf der French-Library per curl und lokales Auslesen zweier per WebFetch gespeicherter PDFs (pdftotext).
Alle Zahlen unten stammen aus tatsaechlich abgerufenen Seiten/PDFs oder sind als "Suchsnippet" bzw. "aus Gedaechtnis" markiert. Was ich nicht gefunden habe, steht ausdruecklich als "nicht gefunden".

## 0. Kurzfazit (ehrlich)

- Der Kern der Familie (Kurzfrist-Umkehr von Aktien) ist real, aber seine Nachpublikations-Geschichte ist schlecht: Er war in den 1990ern und bei Liquiditaetsstress riesig, ist in ruhigen Phasen nach 2000 stark geschrumpft und lebt vor allem in kleinen, illiquiden Aktien, in denen Kosten ihn auffressen. Die besten Belege fuer "funktioniert nach Kosten" betreffen Grosskapitalisierungen und bereinigte (Residual-/Industrie-relative) Signale, nicht die rohe Umkehr.
- Die Gratis-Datenlage ist fuer genau die guten Varianten schwach: CRSP-Punkt-in-Zeit-Universum ist nicht gratis. Mit yfinance kann man nur HEUTIGE Index-Mitglieder laden. Das ist bei Umkehrstrategien besonders verzerrend (man kauft Verlierer, und gerade die Verlierer, die nie zurueckkamen, fehlen im Datensatz). Jede Aktien-Strategie hier (3.1 S1, 3.2 S2, 3.4 S4) liefert deshalb nur eine OBERGRENZE, keinen Beleg.
- Frei und ohne Survivorship-Problem testbar sind nur ETF-/Index-Varianten (3.3 S3, 3.5 S5) und die Ken-French-Faktoren/-Portfolios (als Plausibilitaetscheck, nicht handelbar).
- Fuer einen deutschen Privatanleger (Abgeltungssteuer, kein einfaches Leerverkaufen, US-ETFs wie SPY/XLx bei vielen EU-Brokern wegen PRIIPs/KID nicht handelbar, aus Gedaechtnis, nicht in diesem Lauf geprueft) sind Long-Short-Varianten praktisch kaum umsetzbar. Realistisch bleibt Long-only (S3, IBS) oder nur Research.
- Die gefundenen Original-Zahlen sind fast alle BRUTTO bzw. mit Same-Close-Ausfuehrung (Handel zum selben Schlusskurs, der das Signal erzeugt). Unsere Pflichtregel (Signal Close t, Handel fruehestens t+1) ist bei Tagesumkehr deutlich haerter als die Papers. Fuer taegliche Strategien (S4 Avellaneda/Lee, S5 Nagel-ETF; auch S3 IBS) ist daher gut moeglich, dass fast nichts uebrig bleibt. Das ist ein gueltiges Ergebnis.
- "Dai-Zhong-Zhu (Reversal in ETFs)" aus der Aufgabenstellung konnte ich NICHT finden. Die Suche lieferte stattdessen Dai/Medhat/Novy-Marx/Rizova (2024), das sich auf Einzelaktien bezieht. Ich gebe "Dai-Zhong-Zhu" deshalb nicht als Quelle an. Die ETF-Evidenz in dieser Notiz ist entsprechend duenn.
- Jegadeesh 1990 und Lehmann 1990 habe ich nicht abgerufen (nur ueber Nagel/Quantpedia zitiert gesehen), deshalb nicht als Quelle gefuehrt.

## 1. Abrufstatus (Transparenz)

| Quelle | Status |
|---|---|
| Avellaneda/Lee, Statistical Arbitrage in the U.S. Equities Market (NYU-PDF, math.nyu.edu/faculty/avellane/AvellanedaLeeStatArb20090616.pdf) | ABGERUFEN. WebFetch konnte das PDF nicht lesen, wurde aber lokal gespeichert und mit pdftotext komplett ausgelesen (Regeln, Appendix, Abstract, Tabellenunterschriften; Tabellenwerte selbst stehen als Bilder und wurden nicht gelesen) |
| Nagel, Evaporating Liquidity, NBER w17653 (Abstractseite und PDF) | ABGERUFEN. PDF lokal mit pdftotext gelesen (Strategie-Definition, Tabelle 1, Tabelle 2/3 Text) |
| Quantpedia "Short-term reversal in stocks" (quantpedia.com/strategies/short-term-reversal-in-stocks) | ABGERUFEN (Sekundaerquelle zu Groot/Huij/Zhou, Frazzini/Israel/Moskowitz, Nagel, Blitz et al.). Seite enthaelt eigene Widersprueche (siehe S2) |
| Blitz/Huij/Lansdorp/Verbeek 2013, Repository-Seite repub.eur.nl/pub/40707 | ABGERUFEN, aber nur Abstract + Metadaten. Regeldetails und Zahlen aus dem Paper NICHT gesehen |
| Robeco-Seite zu Blitz/van der Grient/Honarvar 2023 | ABGERUFEN, nur Zusammenfassung. Keine Zahlen, keine Regeldetails (Sample, Lookback, Gewichtung, Kosten alle "nicht auf der Seite") |
| Quantified Strategies "The classical mean reversion strategy" (Substack) | ABGERUFEN, aber nach der Einleitung hinter Paywall. Nur: SPY, ab Januar 2000, 100 % Eigenkapital je Trade. Keine Regeln, keine Ergebnisse |
| Ken French Data Library (data_library.html) | Seite per curl abgerufen (Dateinamen verifiziert), Header der Daily-ST_Rev-Zip per curl HEAD (HTTP 200, 86 KB, zuletzt geaendert 2026-09-25). Keine Datei heruntergeladen, Zeitraeume der Dateien NICHT verifiziert |
| Nagel NBER-Seite, Suchtreffer zu Nagel, Avellaneda/Lee | Suchsnippets, Inhalte durch die Volltexte oben bestaetigt |
| Dai/Medhat/Novy-Marx/Rizova, "Reversals and the Returns to Liquidity Provision" (FAJ 2024, NBER w30917) | NUR Suchsnippet (rpc.cfainstitute.org, causalclaims.trfetzer.com). Seite NICHT abgerufen, deshalb nicht in der Quellenliste der Strategien |
| Baltussen/Da/Soebhag, End-of-day reversal (Arbeitspapier 2025) | NUR Suchsnippets (alphaarchitect.com/end-of-trading, www3.nd.edu/~zda/EOD.pdf, eur.nl-Pressemeldung). Nicht abgerufen. Nicht aufgenommen: braucht Minutendaten (nicht gratis) |
| Hou/Xue/Zhang, Replicating Anomalies (NBER w23394) | NUR Suchsnippet. Reversal-Zahlen daraus NICHT gesehen |
| Nadler/Schmidt 2018 (Momentum/Reversal in ETF-Portfolios), Micaletti 2023 (Short-Term Mean-Reversion Indicators for Global Equities), Concretum 2026 (Sektor-ETF-Reversal) | NUR Suchsnippets (cxoadvisory.com Seiten, concretumgroup.substack.com). Nicht abgerufen, Ergebnisse unbekannt/unverifiziert |
| R-Bloggers 2013 "IBS reversion edge with QuantShare" | NUR Suchsnippet |
| Connors/Alvarez "Short Term Trading Strategies That Work" (RSI(2)) | NICHT gesehen. Regel unten aus Gedaechtnis |

Konsequenz: Fuer S1 (Blitz et al.) und S3 (IBS/RSI(2)) sind die konkreten Parameter nicht aus abgerufenen Primaerquellen verifiziert. Sie sind unten ausdruecklich als "Entwurf" gekennzeichnet. Vor dem Kodieren die Papers (SSRN/Journal) im Browser oeffnen und abgleichen.

## 2. Gemeinsame Implementierungsregeln (gelten fuer alle Strategien)

- Datenquelle: yfinance, auto_adjust=True. Bei Aktienstrategien Tagesdaten, bei ETFs auch High/Low (IBS).
- Ausfuehrung: Signal am Schlusskurs t. HAUPTVARIANTE Handel zum Schlusskurs t+1. Sensitivitaeten: Open t+1 und Close t+2. Die Papers handeln durchweg am Signal-Schluss (Avellaneda/Lee schreiben "all trades at the closing price of that day"; Nagel rechnet Close-to-Close mit Gewichten aus Vortagesrenditen). Ihre Ergebnisse sind damit fuer uns nicht direkt uebertragbar, sondern optimistisch.
- Kosten: pro Strategie getrennt testen. Als Referenzpunkte aus den gelesenen Quellen: Avellaneda/Lee 5 bp pro Trade (10 bp Round-Trip), Groot et al. (laut Quantpedia) Nomura-Modell plus Kommission 5 bp (1990er) / 3 bp (2000er). Eigene Annahmen fuer heute (NICHT belegt): Grosskapitalisierungs-Aktien 5-10 bp je Seite, Sektor-SPDRs 1-3 bp je Seite, Leihkosten Short 0,3-1 % p.a.
- Survivorship: yfinance liefert nur heute existierende Ticker. Aktienuniversen (S1, S2, S4) sind daher verzerrt, in Umkehrstrategien nach oben. Als Gegentest: Ken-French-Faktor F-F_ST_Reversal_Factor (monatlich und daily) auf Post-2000-Verfall pruefen.
- Steuer/Praxis (Projektregel CLAUDE.md): Abgeltungssteuer mitrechnen. Hohe Umschlaege realisieren staendig Gewinne. Leerverkauf und Hedge-ETF-Leg sind fuer einen deutschen Privatanleger nur ueber CFDs/Derivate machbar, mit anderer Verlustverrechnung (aus Gedaechtnis, nicht geprueft). US-domizilierte ETFs (SPY, XLx) sind bei vielen EU-Brokern nicht handelbar (aus Gedaechtnis). UCITS-Proxys haben andere Historie (S&P-500-UCITS ab ca. 2010).
- Pflichtvergleiche: Buy&Hold desselben Instruments, Zufalls-Einstieg mit gleicher Haltedauer und gleichem Time-in-Market, Kosten-Sweep, Aufteilung vor/nach 2010.

Datenstarts (Yahoo, AUS DEM GEDAECHTNIS, vor Nutzung mit yfinance pruefen): ^GSPC ab 1927-12 (High/Low vor ca. 1962 vermutlich degeneriert, vor IBS-Nutzung pruefen), SPY ab 1993-01, QQQ ab 1999-03, IWM ab 2000-05, ^VIX ab 1990-01, Select-Sector-SPDRs XLB/XLE/XLF/XLI/XLK/XLP/XLU/XLV/XLY ab 1998-12, XLRE ab 2015-10, XLC ab 2018-06.
Verifiziert (Dateinamen in der French-Library, per curl auf der Library-Seite gefunden): F-F_Research_Data_Factors_CSV.zip (monatlich), F-F_Research_Data_Factors_daily_CSV.zip, F-F_ST_Reversal_Factor_CSV.zip, F-F_ST_Reversal_Factor_daily_CSV.zip, 10_Portfolios_Prior_1_0_CSV.zip und 10_Portfolios_Prior_1_0_Daily_CSV.zip (Anzeigename "10 Portfolios Formed on Short-Term Reversal"), 49_Industry_Portfolios_CSV.zip und 49_Industry_Portfolios_daily_CSV.zip. Zeitraeume der Dateien: aus Gedaechtnis ab 1926/1927, nicht verifiziert.

## 3. Strategien (nach erwarteter Robustheit sortiert, beste zuerst)

### 3.1 residual_reversal_largecap_monthly (Residual- bzw. Industrie-bereinigte 1-Monats-Umkehr, Grosskapitalisierungen, monatlich)

Grundidee: Umkehr nicht auf Rohrenditen, sondern auf der Rendite, die ein Faktor- bzw. Branchenmodell NICHT erklaert. Das entfernt die zeitvariablen Faktorbetas (und Industrie-Momentum), die die rohe Umkehr verwaessern.

Regel (ENTWURF, Parameter nicht aus dem Paper verifiziert; die Idee "Residual statt Roh" und die Behauptung ueber Wirkung sind aus dem Abstract):
```
Universum U_t: heutige S&P-500-Mitglieder (Wikipedia-Liste), nur Aktien mit >= 37 Monatsrenditen (survivorship-verzerrt, siehe oben)
Zeitpunkt t: letzter Handelstag jedes Kalendermonats
Fuer jede Aktie i:
   r_i,s = Monats-Gesamtrendite (Adj Close), s = t-36 ... t
   OLS ueber s = t-36 ... t-1 (36 Beobachtungen):  (r_i,s - RF_s) = a + b1*MKT_s + b2*SMB_s + b3*HML_s + e_i,s
   resid_i,t = (r_i,t - RF_t) - (b1*MKT_t + b2*SMB_t + b3*HML_t)      # ohne Alpha a
   sig_i = Standardabweichung der e_i,s im Fenster (36 Werte)
   z_i,t = resid_i,t / sig_i
Rangfolge nach z. LONG: unterstes Dezil (staerkste negative z). SHORT: oberstes Dezil.
Gewichte: gleichgewichtet, +100 % Long / -100 % Short (Dollar-neutral).  Long-only-Variante: nur Long-Leg, Benchmark = Gleichgewicht aller U_t.
Ausfuehrung: Kauf/Verkauf zum Schlusskurs t+1. Halten bis zum Schlusskurs des ersten Handelstags des Folgemonats (also Rebalancing alle ~21 Handelstage). Positionen, die im Leg bleiben, werden nicht gehandelt.
Variante B (Branchen-relativ, leichter kodierbar): x_i,t = (Rendite der letzten 21 Handelstage von i) - (Gleichgewichts-Mittel der Rendite der letzten 21 Handelstage aller S&P-500-Aktien im selben GICS-Sektor). Rest wie oben. (Idee laut Suchsnippet zu Dai et al. 2024; Details dort NICHT verifiziert.)
Faktoren: Ken French F-F_Research_Data_Factors_CSV (monatlich). ACHTUNG: Die Monatsdatei erscheint mit Verzug. Fuer Live-Betrieb Proxy-Faktoren aus ETFs (z. B. SPY, IWM, IWD/IWF) oder die Daily-Datei aufsummieren.
```
Kosten: Umschlag nicht gefunden, muss gemessen werden (vermutlich hoch, da jeden Monat die Verlierer wechseln). Test 5/10/20 bp je Seite plus Leihkosten.

Belege (gesehen):
- Blitz, Huij, Lansdorp, Verbeek (2013), "Short-term residual reversal", Journal of Financial Markets 16(3), 477-504. Abstract (repub.eur.nl/pub/40707): konventionelle Kurzfrist-Umkehr hat dynamische Fama-French-Faktorexposures; die Residual-Variante vermeidet sie und verdient ungefaehr das Doppelte an risikoadjustierter Rendite; Profite bleiben signifikant nach Handelskosten, auch bei Beschraenkung auf Large Caps nach 1990; Erklaerung durch Handelsfriktionen oder asynchronen Handel wird zurueckgewiesen. Zahlen aus dem Paper selbst: NICHT gesehen.
- Blitz, van der Grient, Honarvar (2023), "Reversing the trend of short-term reversal" (SSRN-ID 4575689 laut Robeco-Seite). Robeco-Zusammenfassung (robeco.com/en-au/insights/2023/10/reversing-the-trend-of-short-term-reversal): verbesserte Umkehr, die Branchen- und Faktor-Momentum neutralisiert, bietet doppelte risikoadjustierte Rendite und bleibt ueber die Zeit wirksam. Zahlen/Regeldetails NICHT auf der Seite. Interessenkonflikt beachten: Robeco setzt die Erkenntnis in einem eigenen Produkt ein.
- Quantpedia (abgerufen) zitiert den Abstract desselben Teams: die klassische Umkehr habe im Zeitverlauf stetig nachgelassen, in den meisten Regionen sei sie inzwischen verschwunden. Das stuetzt die Sicht "roh tot, bereinigt lebendig", ist aber eine Selbstaussage der Autoren.

Verfall/Risiken:
- Selbst-Aussagen der Autoren, keine unabhaengige Replikation gefunden. Hou/Xue/Zhang (nur Suchsnippet) zeigen allgemein, dass viele Liquiditaets-/Reversal-Anomalien bei NYSE-Breakpoints und Value-Weighting insignifikant werden. Das konkrete Reversal-Ergebnis daraus habe ich NICHT gesehen.
- Survivorship in yfinance (siehe oben) verzerrt die Verlierer-Seite nach oben.
- Tail-Risiko: Verlierer-Kauf in Krisen (2008, 2020): Liquidationsdruck, Short-Squeezes im Short-Leg. Quantpedia warnt vor Drawdowns in genau diesen Phasen (aber siehe S2 fuer die dort genannten Zahlen).
- Parameter (36 Monate, Dezil, Standardisierung) sind Entwurf, nicht Paper-Wert.

### 3.2 top100_weekly_reversal (woechentliche Umkehr, 100 groesste US-Aktien, 10 Long / 10 Short)

Regel (Parameter nach Quantpedia-Zusammenfassung von Groot/Huij/Zhou, an Widerspruechen der Seite bereinigt):
```
Universum: 100 groesste US-Aktien nach Marktkap. Gratis-Proxy: S&P-100-Mitglieder heute (survivorship-verzerrt)
Signaltag t: letzter Handelstag jeder Woche (normalerweise Freitag)
R5_i = AdjClose_i(t) / AdjClose_i(t-5 Handelstage) - 1        # Quantpedia nennt Robustheitsergebnisse fuer eine 5-Tage-Variante; die Seite widerspricht sich bei "Woche" vs "Monat" im Short-Leg, ich nehme in beiden Legs R5
LONG: 10 Aktien mit kleinstem R5.  SHORT: 10 Aktien mit groesstem R5.
Gewichte: 10 % des Eigenkapitals je Aktie je Seite (+100 % / -100 %)  [Gewichtung ist auf der Quantpedia-Seite "nicht angegeben", also Entwurf]
Ausfuehrung: Schlusskurs t+1; Haltedauer 5 Handelstage; woechentlich neu. Bleibt eine Aktie im Leg, wird nicht gehandelt.
Kosten-Sweep: 3, 5, 10, 20 bp je Seite; Zusatz Leihkosten.
Long-only-Variante: nur Long-Leg, Vergleich mit Gleichgewicht aller 100.
```
Belege (Quantpedia-Seite abgerufen, Zahlen daraus, Paper selbst NICHT gesehen): Universum 100 groesste Aktien, woechentliches Rebalancing, Nomura-Kostenmodell (Spread plus permanenter und temporaerer Impact) plus Kommission 5 bp (1990er) / 3 bp (letztes Jahrzehnt), Trades bis 1 Mio USD je Aktie. Stichprobe 1990-2009: Netto-Long-Short 29,0 bp pro Woche, entspricht laut Quantpedia 16,25 % p.a., Vol 14,94 % (aus t-Wert geschaetzt), Sharpe 1,09. Max. Drawdown -52,94 % (die Seite nennt in ihrem Feld "nicht angegeben", also widerspruechlich). Robustheit: 5-Tage-Rebalancing, Nomura-Kosten, netto je Woche: 1.500 Aktien -31,4 bp, 500 Aktien +10,6 bp, 100 Aktien +29,0 bp. Die Seite sagt, der Befund halte fuer 100 und 500 Aktien, aber nicht fuer 1.500.

Verfall/Risiken:
- Nach 2009 keine Zahlen gefunden. Allgemeine Evidenz auf derselben Seite: Blitz et al. sehen die klassische Umkehr als stark abgeschwaecht bis verschwunden. Nagel (siehe 3.5) zeigt: Reversal-Profite fielen bis 2007 auf unter 0,2 % pro Tag (Tages-Strategie, brutto) und explodierten in der Finanzkrise 2007-09. Es ist also ein Short-Vol-/Liquiditaets-Risiko-Ertrag mit Krisen-Gewinnen, aber Krisen-Drawdowns auf Einzelaktien-Ebene sind real (Quantpedia: -52,94 %, unsicher).
- Hohe Konzentration (20 Positionen), Idiosynkratik. Kleine Netto-Marge: 29 bp bei 100 Aktien, 10,6 bp bei 500. Wenn die echten Kosten nur um 10-20 bp hoeher liegen, ist sie weg.
- Survivorship und fehlendes Punkt-in-Zeit-Universum in den Gratisdaten.
- Deutscher Privatanleger: Short-Leg kaum umsetzbar.

### 3.3 index_etf_ibs_rsi2_longonly (Index-ETF-Kurzfrist-Umkehr, Long-only: IBS-Kern, RSI(2) als Variante)

Regel (Parameter sind ENTWURF/Prior-Werte, ungetunt, nicht aus einem Paper):
```
Instrumente (je einzeln testen, NICHT poolen und das beste waehlen): SPY (ab 1993), QQQ (ab 1999), IWM (ab 2000); optional ^GSPC ab 1962, falls High/Low brauchbar
Daten: auto_adjust=True, OHLC
IBS_t = (Close_t - Low_t) / (High_t - Low_t); falls High == Low: kein Signal
Einstieg (Variante A, IBS): Close_t > SMA200(Close)_t UND IBS_t < 0.20  UND keine Position  =>  KAUF zum Schlusskurs t+1   (Sensitivitaet: Open t+1)
Ausstieg: erster Tag u > Einstieg mit IBS_u > 0.70 ODER Haltedauer >= 5 Handelstage  =>  VERKAUF zum Schlusskurs u+1
Variante B (Connors RSI(2), AUS DEM GEDAECHTNIS, Buch nicht gesehen): RSI = Wilder-RSI mit Laenge 2 auf Close. Einstieg: Close_t > SMA200 UND RSI(2)_t < 10 => Kauf Schlusskurs t+1. Ausstieg: Close_u > SMA5(Close)_u => Verkauf Schlusskurs u+1
Kein Short, keine Hebel, 100 % Eigenkapital je Trade, sonst Cash (Zins 0 oder BIL)
Kosten: 1-3 bp je Seite + Spread; Steuer extra
```
Belege: KEIN Peer-Review-Paper gefunden. Eine Suche nach einer Quantpedia-Seite zu IBS ergab keinen Treffer. Gesehen nur Praktiker-Material: Quantified Strategies (Substack, abgerufen aber hinter Paywall: SPY, ab Januar 2000, 100 % Eigenkapital je Trade, keine Regeln und Zahlen sichtbar). Der Suchtreffer einer anderen Seite derselben Serie fasst zusammen: Kauf am Schluss, wenn IBS < 0,25 und RSI(21) < 45, Ausstieg, sobald Schluss ueber dem Vortagesschluss. Zahlen dazu im Snippet: nicht enthalten. Ein QuantConnect-Beispiel (nur Snippet) rangiert Index-ETFs nach IBS. Theoretisch passt Nagel (2012): Kurzfrist-Umkehr bezahlt Liquiditaetsbereitstellung und ist zustandsabhaengig (VIX), aber Nagel testet KEINE Index-IBS-Regel.
Gegenindiz: Nadler/Schmidt 2018 (nur Suchsnippet via cxoadvisory) finden Momentum und Umkehr bei US-Aktien-ETFs weitgehend unwirksam (kurze Stichprobe 2011-2017, nicht abgerufen).

Verfall/Risiken: Hohes Data-Mining-Risiko (viele Praktiker-Varianten, jeder hat Parameter an derselben SPY-Historie optimiert). Typisches Tail-Risiko: Kauf in laufendem Crash (2008, 2020), Trendfilter SMA200 reagiert langsam. Kein Stop. Kleine Stichprobe an Signalen in Bullenphasen. Effekt konzentriert sich vermutlich auf bestimmte Vol-Regime (Hypothese, nicht belegt).

### 3.4 avellaneda_lee_sector_etf_statarb (Residual-Stat-Arb gegen Sektor-ETF, taeglich, s-Score)

Das ist die am genauesten spezifizierte Regel der Familie. Ich habe sie aus dem Paper-PDF (Abschnitte 3-5, Appendix) abgeschrieben.

Regel (Paper), mit unserer Ausfuehrungsregel:
```
Universum: Aktien mit Marktkap > 1 Mrd USD zum Handelstag. Gratis-Proxy: heutige S&P-500-Mitglieder (survivorship-verzerrt)
Sektor-ETF je Aktie: Select-Sector-SPDR passend zum GICS-Sektor (XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY). Aktien aus Immobilien/Kommunikation weglassen (XLRE/XLC erst seit 2015/2018). Das Paper selbst nutzt 15 ETFs, nicht diese 9.
Taeglich nach Schluss t, fuer jede Aktie:
  1) R_n^S = b0 + b * R_n^ETF + eps_n,  n = 1..60   (die letzten 60 Tagesrenditen bis inkl. t, OLS)
  2) X_k = Summe_{j<=k} eps_j, k = 1..60            (X_60 = 0 per Konstruktion)
  3) AR(1): X_{n+1} = a + c * X_n + zeta,  n = 1..59 ("c" im Paper "b")
  4) kappa = -ln(c) * 252;  m = a / (1-c);  sigma_eq = sqrt( Var(zeta) / (1 - c^2) )
  5) Modell nur gueltig bei kappa > 252/30 = 8.4, d. h. 0 < c < 0.9672; sonst: kein neuer Trade und offene Position schliessen
  6) s_i = (X_60 - m_adj) / sigma_eq = -m_adj / sigma_eq,  m_adj_i = m_i - Mittelwert ueber alle Aktien (Mittelwert der m_j; "centered means")
Handelsregel (Paper): KAUF-zu-oeffnen wenn s < -1.25: kaufe 1 USD Aktie, verkaufe b USD Sektor-ETF.  VERKAUF-zu-oeffnen wenn s > +1.25: leerverkaufe 1 USD Aktie, kaufe b USD ETF.
   LONG schliessen wenn s > -0.50.  SHORT schliessen wenn s < +0.75.
Positionsgroesse: Paper "2+2"-Leverage, ca. 2 % des Eigenkapitals je Aktie (2/100 bei erwarteten 100 Long und 100 Short), nur bei neuen Positionen angepasst. All-or-nothing ("bang-bang").
Volumen-Variante ("trading time"): ersetze R_t durch R_t * (Vbar / V_t) mit Vbar = mittleres Tagesvolumen der letzten 10 Handelstage, V_t = Volumen des Tages. Hilft laut Paper nur bei ETF-Faktoren.
AUSFUEHRUNG UNSER: Signale aus Daten bis Schluss t, Trades zum Schlusskurs t+1 (Paper: gleicher Schlusskurs t).
Kosten Paper: 5 bp pro Trade, 10 bp Round-Trip. Eigene Annahme Hedge-ETF zusaetzlich 1-3 bp je Seite.
```
Belege (Paper gelesen):
- Avellaneda & Lee (2010), Quantitative Finance 10(7), 761-782. Abstract/Text: PCA-Strategien durchschnittlicher jaehrlicher Sharpe 1,44 fuer 1997-2007 nach Kosten, aber nur 0,9 fuer 2003-2007. ETF-Strategien Sharpe 1,1 fuer 1997-2007 ("similar degradation after 2002"). Mit Volumen-Information (trading time) ETF-Strategie Sharpe 1,51 fuer 2003-2007. Tabellenunterschrift Tabelle 5 (echte 15 ETFs, 2002-2007): "average Sharpe ratio from 2003 to 2007 was 0.6" (Kalenderzeit ohne Volumen).
- August 2007: Alle Mean-Reversion-Strategien erlitten einen grossen Drawdown mit Erholung in etwa 10 Tagen; PCA etwa 5 %, ETF-basiert etwa 10 % (bei 2+2-Leverage).
- Leverage 2+2 so gewaehlt, dass ca. 10 % Vol; Backtest ohne Short-Leihkosten-Aussage gefunden (nicht explizit).

Verfall/Risiken:
- Im Paper selbst: deutlicher Rueckgang ab 2002/2003. Nach 2007 enthaelt das Paper keine Daten ("more studies, particularly after 2007, may be required"). Unabhaengige Post-2007-Zahlen habe ich NICHT gefunden.
- Der Paper-Backtest handelt am Signal-Schluss; unser t+1 ist fuer eine Tagesumkehr eine harte Einschraenkung. Erwartung (nicht belegt): ein grosser Teil des Ertrags geht weg.
- Hohes Crowding-/Quant-Quake-Risiko (August 2007), hohe Umschlaege, Kosten 10 bp Round-Trip sind fuer Privatanleger optimistisch.
- 9 Sektor-SPDRs sind ein gegenueber dem Paper (15 ETFs) groeberes Faktormodell; Residuen sind groesser.
- Survivorship in yfinance. Taeglich ~500 Regressionen sind rechnerisch ok.
- Deutscher Privatanleger: nicht umsetzbar (Short plus Hedge plus Tagesumschlag).

### 3.5 nagel_vix_gated_sector_etf_reversal (VIX-getorte Tages-Umkehr auf Sektor-ETFs, Industrie-Variante von Nagel)

Eigener Entwurf, inspiriert von Nagel (2012). Nagel testet Aktien (CRSP, 1998-2010) und 48 Fama-French-Industrieportfolios. Ich habe die Industrie-Idee auf handelbare Sektor-ETFs uebertragen. Das ist eine UEBERTRAGUNG, kein Paper-Ergebnis.

Regel (Entwurf):
```
Universum: XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY (9 Sektor-SPDRs, ab 1998-12)
Tag d: r_i,d = AdjClose-Rendite; m_d = Mittel_i r_i,d;  x_i,d = r_i,d - m_d;   w_i(d) = - x_i,d / ( 0.5 * Summe_k |x_k,d| )    # Long-Leg +1, Short-Leg -1 (Dollar-neutral)
Nagel-Overlay aus 5 Teilstrategien (Lag 1..5): Zielgewicht fuer die Haltephase (Close t+1 -> Close t+2) = (1/5) * Summe_{j=0..4} w_i(t-j)    # nutzt Renditen der Tage t, t-1, ..., t-4
Gate: g_t = 1, wenn VIX_close(t) > Median(VIX_close(t-251..t)), sonst 0.  Gewicht_i = g_t * Zielgewicht_i.  (Sensitivitaet: feste Schwellen 20/25/30; ALLE berichten, keine beste waehlen.)
Ausfuehrung: Schluss t+1 (eine Tagesverzoegerung mehr als bei Nagel, siehe unten). taegliches Rebalancing.
Kosten: 1, 3, 5 bp je Seite
Optional: Beta-Hedge mit SPY (Nagel hedgt bedingte Marktexposure)
```
Belege (PDF gelesen):
- Nagel (2012), "Evaporating Liquidity", Review of Financial Studies 25(7), 2005-2039; NBER w17653 (2011). Reversal-Strategie: Gewichte proportional zum negativen marktbereinigten Return, $1 Long/$1 Short, ueberlagert aus 5 Teilstrategien mit Lags 1-5 Tage; Daten CRSP-Schlusskurse bzw. Quote-Midpoints, NYSE/AMEX/Nasdaq, Stichprobe Januar 1998 bis Dezember 2010. Tabelle 1: Einzelaktien-Reversal Mittelwert 0,30 % pro Tag (Transaktionspreise) bzw. 0,18 % (Quote-Mitten), annualisierte Sharpe 8,44 bzw. 4,50 (bedingt marktbereinigt 9,58 bzw. 4,91); Industrie-Portfolio-Reversal 0,02 % pro Tag, Sharpe 0,56 (bedingt 0,44). Alle diese Werte sind BRUTTO ohne Handelskosten, und fast die Haelfte des Aktienertrags (Transaktionspreise vs. Quote-Mitten) ist Bid-Ask-Bounce.
- VIX-Vorhersage (Tabelle 2): +1 Prozentpunkt im normalisierten VIX (entspricht +ca. 16 Prozentpunkten im annualisierten VIX, wie der Text die Skalierung angibt) erhoeht die Tagesrendite der Aktien-Umkehr um 0,22 Prozentpunkte, adj. R2 = 0,07. Tabelle 3 (bedingte Sharpe): +1 Prozentpunkt VIX erhoeht den bedingten annualisierten Sharpe um 0,13. Industrie-Koeffizienten kleiner, aber positiv.
- Fig. 1 (Text): Reversal-Renditen waren nahe 1 % pro Tag waehrend LTCM (1998) und Nasdaq-Rueckgang 2000/01, sanken bis 2007 auf unter 0,2 % pro Tag, "explodierten" danach in der Finanzkrise.
- Hinweis aus dem Text: Industrie-Portfolios zeigen auf Tagesbasis "some return continuations" (Fortsetzung), deshalb sind die Ergebnisse dort nicht robust gegen die Lag-Wahl.

Verfall/Risiken:
- Unbedingt nur schwache Industrie-Evidenz (Sharpe 0,56 brutto, 1998-2010). Der Effekt haengt am Gate. Gate-Schwelle ist ein freier Parameter (Overfitting-Gefahr).
- Die Aktien-Zahlen von Nagel sind nicht auf ETFs uebertragbar (ETF-Sektoren haben praktisch keinen Bid-Ask-Bounce-Anteil, und der Aktien-Ertrag war in der Mikrostruktur verankert).
- Handel zum Schlusskurs t+1 statt t: Tagesumkehr verliert dadurch vermutlich den Grossteil (nicht belegt, nur theoretisch aus dem Halbwertszeit-Argument: Hendershott/Menkveld laut Nagel 0,5 bis 2 Tage).
- Post-2010 Evidenz zur VIX-Beziehung: nicht gefunden. Forschungs-Test ohne Handelsanspruch: F-F_ST_Reversal_Factor (daily/monatlich) gegen lagged ^VIX regressieren, getrennt fuer 1990-2010 und 2011-2026. Das testet Nagels Behauptung out-of-sample gratis.
- Short-Leg ETF-Sektoren fuer deutschen Privatanleger: nur ueber CFDs/Derivate.

## 4. Nicht aufgenommen, aber relevant (Leads)

- Baltussen/Da/Soebhag, "End-of-day reversal": fruehere Intraday-Rendite sagt (Querschnitt) die Rendite der letzten halben Stunde negativ voraus. Zweiter Platz beim Quantpedia Award 2025 laut eur.nl. Braucht Intraday-Daten (nicht gratis), und der Effekt ist 30-Minuten-Fenster. Nicht abgerufen.
- Dai/Medhat/Novy-Marx/Rizova (FAJ 2024): Kurzfrist-Umkehr haengt von Aktien-Liquiditaet ab (hohe Volatilitaet: staerkere, schnellere Umkehr; niedriger Umsatz: dauerhaftere, am Ende staerkere Umkehr); Kandidaten sind Quintile der Industrie-relativen Renditen ueber 1/5/21 Tage, 3 Tage um Earnings ausgeschlossen. Nur Suchsnippet. Wert als Folge-Lektuere fuer S1 Variante B.
- Hou/Xue/Zhang "Replicating Anomalies": 64 % aller Anomalien insignifikant bei NYSE-Breakpoints/Value-Weighting. Das STREV-Ergebnis nicht gesehen.
- Micaletti (2023, 17 Mean-Reversion-Indikatoren auf Sektor- und Laender-ETFs) und Concretum (2026, Sektor-ETF-Reversal mit Signifikanzfilter): nur Snippets, Ergebnisse nicht einsehbar.
- Kein Paper zu woechentlicher Umkehr in Laender-Index-ETFs gefunden (nur der Hinweis, dass die Literatur zu Laenderindizes existieren duerfte, aus Gedaechtnis, nicht verifiziert).

## 5. Vorschlag fuer die Quant-Lab-Hypothesen (Hypothese vor Test)

- H-REV-1 (S3/IBS): "SPY-IBS < 0.2 mit SMA200-Filter schlaegt nach Kosten und Steuer Buy&Hold-Zufallseinstieg gleicher Time-in-Market". Abbruch: Sharpe nach Kosten unter Zufallsbenchmark im Median, oder Edge nur in 2008/2020.
- H-REV-2 (Forschungs-Check, gratis, ohne Survivorship): ST_Rev-Faktor (French) hat nach 2000 keinen Mittelwert mehr signifikant ungleich null, ausser bei hohem VIX. Wenn bestaetigt: S1 und S2 nur noch als Krisen-Strategie sinnvoll.
- H-REV-3 (S4 und S5): Tagesumkehr mit Ausfuehrung t+1 hat nach Kosten keinen Edge. Erwartung: Edge verschwindet. Test trotzdem billig fuer S5 (9 ETFs).
- Aktien-Strategien S1/S2/S4 nur starten, wenn ein Punkt-in-Zeit-Universum organisiert wird (z. B. kostenlose historische Index-Mitglieder-Listen), sonst nur als Obergrenze lesen.

## 6. Quellen (gesehen) mit URLs

- Avellaneda & Lee 2010: https://www.math.nyu.edu/faculty/avellane/AvellanedaLeeStatArb20090616.pdf (Bibliografie laut Suchtreffer: Quantitative Finance 10(7), 761-782, https://ideas.repec.org/a/taf/quantf/v10y2010i7p761-782.html)
- Nagel 2012: https://www.nber.org/papers/w17653 und https://www.nber.org/papers/w17653.pdf
- Blitz/Huij/Lansdorp/Verbeek 2013: https://repub.eur.nl/pub/40707
- Blitz/van der Grient/Honarvar 2023 (Robeco-Zusammenfassung): https://www.robeco.com/en-au/insights/2023/10/reversing-the-trend-of-short-term-reversal
- Quantpedia Short-term reversal in stocks: https://quantpedia.com/strategies/short-term-reversal-in-stocks
- Quantified Strategies (nur Einleitung): https://quantifiedstrategies.substack.com/p/the-classical-mean-reversion-strategy
- Ken French Data Library: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html (Dateien unter .../ken.french/ftp/<Dateiname>, z. B. F-F_ST_Reversal_Factor_daily_CSV.zip)
- Nur Suchsnippets (nicht abgerufen): https://rpc.cfainstitute.org/research/financial-analysts-journal/2024/reversals-and-the-returns-to-liquidity-provision, https://causalclaims.trfetzer.com/paper/w30917.html, https://alphaarchitect.com/end-of-trading/, https://www3.nd.edu/~zda/EOD.pdf, https://www.nber.org/papers/w23394.pdf, https://www.cxoadvisory.com/technical-trading/best-short-term-equity-etf-reversal-indicator/, https://concretumgroup.substack.com/p/a-mean-reversion-model-for-us-sectors, https://www.r-bloggers.com/2013/01/ibs-reversion-edge-with-quantshare/
