# Nachrecherche: Cross-Asset-Signale (Anleihen <-> Aktien) und Lead-Lag (Laender, Branchen)

Stand: 2026-10-12. Autor: Quant-Research-Analyst (Subagent). Nachrecherche zu einer vom Kritiker gefundenen Luecke.
Status aller Regeln unten: **Eigenentwurf nach Literatur, UNGETESTET.** Vor Nutzung im Quant-Lab: Hypothese in `docs/HYPOTHESEN.md` eintragen (Regel 3), dann neu implementieren + Tests (Regel 2). Der Plausibilitaets-Check `research/families/crossasset_checks/starts.py` ist laut eigener Kopfzeile ungetestet; ich habe ihn nur fuer Datenstarts genutzt.

## 0. Quellenstatus (ehrlich)

Aufwand: ca. 15 Web-Aufrufe (WebSearch + WebFetch, davon 3 WebFetch mit HTTP 403). **Kein Volltext eines Hauptpapers gelesen.** Alle Paper-Aussagen stammen aus Abstracts, Suchzusammenfassungen oder Sekundaerseiten. Wo eine Zahl fehlt, steht "nicht gefunden".

| Quelle | Status |
|---|---|
| Pitkaejaervi/Suominen/Vaittinen 2020 (JFE 136(1):63-85, DOI 10.1016/j.jfineco.2019.02.011) | Abstract-Aussagen ueber Tinbergen-Seite und Suchtreffer (gesehen); ScienceDirect und Alpha Architect lieferten **HTTP 403**, nicht abgerufen. Regeldetails von CXO Advisory (abgerufen). |
| CXO Advisory Review zum Paper | Abgerufen, Regeln und Einschraenkungen daraus uebernommen. |
| Pitkaejaervi Masterarbeit 2016 (Aalto) | Abgerufen (Abstract). |
| Quantpedia-Update 11.04.2017 (Strategie #342) | Nur ueber Suchzusammenfassung gesehen (Host `vvv.quantpedia.com`, ungewoehnlich), Seite selbst nicht abgerufen. |
| Rapach/Strauss/Zhou 2013 JF 68(4):1633-1662 | Nur Abstract-Aussagen aus Suchtreffer, Volltext nicht gelesen. OOS-Kennzahlen **nicht gefunden**. |
| Aye/Balcilar/Gupta (Empirica 2017) und Siliverstovs (2015) | Nur aus Suchzusammenfassung. Siliverstovs: Original/URL nicht gesehen, daher nicht als Paper gelistet. |
| Hong/Torous/Valkanov 2007 JFE | Abstract-Aussagen aus Suchtreffer; Tse 2015 (J. Empirical Finance) gesehen als Suchtreffer (IDEAS). |
| Menzly/Ozbas 2010 JF 65(4):1555-1580 | Nur Abstract (IDEAS-Suchtreffer). Daten (Input-Output-Tabellen) nicht geprueft, keine Strategie daraus abgeleitet. |
| Huang/Li/Wang/Zhou 2020 JFE 135(3):774-794 | Abstract aus Suchtreffern (WUSTL-Profil, IDEAS). |
| Connolly/Stivers/Sun 2005 JFQA 40(1):161-194 | Abstract-Aussagen aus Suchtreffer (IDEAS/Cambridge). |
| Fernandez-Perez et al. 2022 (Oel-Volatilitaet, XTSMOM) | Nur Suchtreffer-Snippet (ScienceDirect/AUT-PDF), nicht abgerufen. |
| D. E. Shaw Juni 2021 "Revisiting Stock-Bond Correlation" | Abgerufen. |
| **Nicht abgerufen, deshalb NICHT als Beleg verwendet:** Gulko 2002 ("Decoupling", J. Portfolio Mgmt), Baele/Bekaert/Inghelbrecht 2010, Hou 2007 (Industry information diffusion), Cohen/Frazzini. | Nur Startliteratur laut Auftrag. |

## 1. Kernbefund

1. **Das einzige Paper, das genau diese Familie (Cross-Asset-TSMOM) behandelt, ist Pitkaejaervi et al. (2020).** Aussage laut Abstract: 20 entwickelte Laender, Anleihe- und Aktienindizes ab Januar 1980 bis Dezember 2016 (CXO nennt Januar 1980 bis Dezember 2015 fuer die dort besprochene Fassung; Quantpedia 1980-2015). Vergangene Anleiherenditen sind positive Praediktoren kuenftiger Aktienrenditen, vergangene Aktienrenditen negative Praediktoren kuenftiger Anleiherenditen. Der diversifizierte Cross-Asset-Portfolio-Sharpe liegt laut Autoren **45 %** ueber einem normalen TSMOM-Portfolio (Quantpedia-Abstract: "ueber 40 %"). Erklaerung der Autoren: langsam fliessendes Kapital ("slow-moving capital") in Anleihe- und Aktienmaerkten.
2. **Exakte Regel (CXO-Beschreibung):** Aktien eines Landes long, wenn vergangene Rendite von Aktienindex UND Staatsanleihenindex positiv; short, wenn beide negativ; sonst keine Position. Anleihen eines Landes long, wenn Anleihe-Rendite positiv UND Aktien-Rendite negativ; short, wenn Anleihe negativ UND Aktien positiv; sonst keine Position. Anleihenindex mit konstanter 5-Jahres-Laufzeit. Hauptspezifikation 12 Monate Lookback / 1 Monat Haltedauer (getestet wurden 1, 3, 6, 9, 12, 24, 36, 48). Renditen als Ueberrendite ueber den 1-Monats-US-T-Bill. Positionen ueber Laender gemittelt.
3. **Wichtige Folgerung fuer die Umsetzung (eigene logische Ableitung):** Aktien- und Anleihe-Bein schliessen sich pro Land gegenseitig aus. Haben rE und rB gleiches Vorzeichen, wird die Aktie gehandelt (+1/-1); haben sie verschiedene Vorzeichen, die Anleihe (+1/-1). Es ist also immer genau ein Instrument aktiv (pro Land). Das macht die US-Version zu einem einfachen Umschalter SPY / IEF / Cash (bzw. Short).
4. **Ehrliche Einschraenkungen laut CXO:** Leistung brutto, nicht netto; Indizes statt handelbarer Fonds; Lag-Analysen nutzen dieselben Daten wie die Strategie-Tests (teils In-Sample); gesamte Stichprobe ist ein starker Anleihen-Bullenmarkt; Sharpe-Verbesserung fuer USA, UK, Kanada nur gering und fuer Japan nicht vorhanden; Gewinne koennten aus Aenderungen der Aktien-Anleihen-Korrelation statt aus Renditeverbesserung stammen. Zusaetzlich: Ueberlegenheit in 18 von 20 Laendern auf Brutto-Sharpe-Basis (CXO).
5. **Keine unabhaengige Nach-2020-Replikation der Cross-Asset-Regel gefunden** (zwei Suchlaeufe, auch Extended-Modus). Das ist selbst ein Befund: Verfall ist unbekannt, nicht widerlegt.
6. **Kritik am Oberthema TSMOM:** Huang/Li/Wang/Zhou (2020): Asset-fuer-Asset-Regressionen zeigen kaum Evidenz fuer TSMOM, in- und out-of-sample; der gepoolte t-Wert ueberzeugt unter Bootstrap nicht; eine TSM-Handelsstrategie verdient zwar, ist aber ungefaehr so gut wie eine Strategie auf dem historischen Stichprobenmittel (ohne Vorhersagbarkeit). Das trifft Long/Cash-Varianten besonders: Ein Teil der Rendite ist Aufwaertsdrift, nicht Vorhersage.
7. **Stock-Bond-Korrelation ist das Kernrisiko:** Laut Suchzusammenfassung drehte die Korrelation um das Jahr 2000 fuer die meisten G7-Laender von positiv auf negativ; D. E. Shaw (Juni 2021): Das Vorzeichen haengt vom Schocktyp ab (Wachstums-/Risikoappetit-Schocks -> negativ, Inflationserwartungs-/Fed-Reaktionsschocks -> positiv). Die Strategie lebt davon, dass Anleihen bei fallenden Aktien steigen (Flucht in Qualitaet). 2022 (beide fielen) ist der Testfall; ich habe keine veroeffentlichte Zahl dazu.
8. **Connolly/Stivers/Sun (2005):** Hoehere Aktienmarkt-Unsicherheit (implizite Vola, Umschlag) geht mit tieferer kuenftiger Aktien-Anleihen-Korrelation einher; an Tagen mit Vola-Sprung schlagen Anleihen Aktien (Flucht in Sicherheit). Das ist ein Korrelations-, kein Renditeprognose-Befund; als Handelssignal nur als Filter-Idee (siehe Abschnitt 5).

## 2. Datenlage (gepruefte Starts, yfinance `history(period="max", auto_adjust=True)`, Lauf 2026-10-12)

| Ticker | Start | Hinweis |
|---|---|---|
| SPY | 1993-01-29 | |
| IEF, TLT, SHY | 2002-07-30 | |
| VFINX | 1980-01-02 | Fonds, angepasst = Gesamtrendite |
| VUSTX | 1986-05-19 | Langlaufer-Treasury-Fonds |
| VFITX | 1991-10-28 | Intermediate-Treasury-Fonds |
| BIL | 2007-05-30 | |
| ^IRX (13W-Bill-Rendite) | 1960-01-04 | Tagesdaten, nur Rendite (kein Preis) |
| ^FVX (5J-US-Rendite) | 1962-01-02 | passt zur 5-Jahres-Laufzeit des Papers (nur USA) |
| ^TNX (10J), ^TYX (30J) | 1962-01-02 / 1977-02-15 | |
| EWJ, EWG, EWU, EWQ, EWC, EWA, EWH, EWS, EWP, EWI, EWN, EWD, EWL, EWK, EWO, EWM, EWW | 1996-03-18 | |
| EWT / EWY / EWZ | 2000-06-23 / 2000-05-12 / 2000-07-14 | |
| EZU / EFA | 2000-07-31 / 2001-08-27 | |
| XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY | 1998-12-22 | XLRE erst 2015-10-08 |
| BWX / IGOV (Welt-Staatsanleihen ex-US) | 2007-10-11 / 2009-01-30 | zu kurz fuer Laender-Replikation |
| SH (Short-S&P) / TBT | 2006-06-21 / 2008-05-22 | |
| ^GSPC | 1927-12-30 | nur Kursindex |
| ^GSPTSE | 1979-06-29 | |
| ^N225 | 1965-01-05 | |
| ^FTSE | 1984-01-03 | |
| ^GDAXI | 1987-12-30 | |
| ^FCHI | 1990-03-01 | |
| ^HSI | 1986-12-31 | |
| ^AXJO | 1992-11-23 | |
| ^SSMI | 1990-11-09 | |
| ^AEX | 1992-10-12 | |
| ^IBEX | 1993-07-12 | |
| ^BVSP, ^KS11, ^TWII, ^STI, ^OMX | 1993-04-27 / 1996-12-11 / 1997-07-02 / 1987-12-28 / 2008-11-20 | |

**FRED (Anleiherenditen fuer Laender ohne ETF):** Der Abruf von `fred.stlouisfed.org` scheiterte in dieser Umgebung (auch per curl). **Datenstarts, Aktualitaet und Frequenz der Serien IRLTLT01DEM156N, ...JPM..., ...GBM..., ...CAM..., ...AUM..., ...FRM..., ...ITM..., ...CHM..., ...SEM..., ...NLM..., ...ESM..., ...KRM156N (und US: GS10, GS5) sind NICHT verifiziert.** Vermutung (ungeprueft, vor Nutzung pruefen): Die OECD-Serien sind Monatsmittel statt Monatsendwerte und kommen mit Veroeffentlichungsverzoegerung. Beides erzeugt Look-ahead im Backtest bzw. Verzug live. Ken French (49 Industry Portfolios, Mkt-RF/RF, monatlich) wurde in diesem Lauf nicht abgerufen; Start 1926-07 ist mein Wissensstand, **nicht geprueft**; Veroeffentlichung erfolgt mit mehreren Wochen Verzug, daher live nur mit Sektor-ETFs ersetzbar.

## 3. Strategien (nach erwarteter Robustheit sortiert)

Gemeinsame Konventionen fuer alle Regeln:
- Signal am Schlusskurs des letzten Handelstags des Monats T; Handel zur **Eroeffnung des naechsten Handelstags T+1** (angepasste Open-Kurse); Halten bis zur naechsten Monatsend-Entscheidung.
- "r12" = Gesamtrendite (angepasster Schlusskurs) von T-12 Monate (letzter Handelstag dieses Monats) bis T, minus Bill-Rendite derselben 12 Monate: `rf12 = Produkt(1 + ^IRX[Monatsende]/100/12 ueber die 12 Monate) - 1`. "> 0" strikt, Gleichheit zaehlt als nicht positiv.
- Kostenannahme fuer Backtest (Platzhalter, anhand Spread festlegen): SPY/IEF/SHY 2-3 bp je Seite, Laender-ETFs 5-15 bp je Seite. Steuer: deutsche Abgeltungssteuer 26,375 % auf realisierte Gewinne; jeder Wechsel realisiert Gewinne und kostet Steuerstundung gegenueber Buy&Hold (Regel 4 im CLAUDE.md).

### 3.1 `xtsmom_us_switch_longcash` (Komplexitaet 2)

Long/Cash-Umsetzung der Pitkaejaervi-Regel nur fuer die USA mit ETFs. Ohne Short-Bein.

```
Universum: SPY (Aktien), IEF (7-10J Treasuries), SHY (Cash-Proxy; vor 2002-07 ^IRX/12 pro Monat)
Lange Historie (Backtest): VFINX statt SPY (ab 1980-01), VFITX statt IEF (ab 1991-10),
  davor Bond-Proxy aus ^FVX: r_B(m) = y(m-1)/12 - D*(y(m)-y(m-1)), y in Dezimal,
  D = (1 - (1+y/2)^-10)/y   # modifizierte Duration eines 5J-Par-Bonds; Zeitraum 1962+ (Sensitivitaetstest, nicht Hauptergebnis)
Jeden Monat an T (Schluss):
  rE = r12(SPY);  rB = r12(IEF)
  wenn rE > 0 und rB > 0:      Ziel = 100 % SPY
  sonst wenn rE <= 0 und rB > 0: Ziel = 100 % IEF      # "Flucht in Qualitaet"-Zustand
  sonst (rB <= 0):             Ziel = 100 % SHY
Ausfuehrung: Wechsel zur Eroeffnung T+1, nur wenn Ziel != aktuelle Position.
```

Erwartung (vor dem Test): Der Schutz liegt hauptsaechlich im Drawdown (Aktien raus, wenn Anleihen nicht bestaetigen), nicht in Mehrrendite gegenueber SPY Buy&Hold; Abbruchkriterium: nach Kosten und Steuer kein besserer Sharpe/Calmar als 12M-Trend auf SPY allein (long/cash), und kein besserer Wert als die Zufallsbenchmark mit gleicher Investitionsquote. Prueft die Hypothese "Anleihebestaetigung bringt etwas ueber reinen Aktientrend hinaus".

### 3.2 `xtsmom_country_basket_longcash` (Komplexitaet 4)

Der diversifizierte Korb des Papers (nur Aktien-Bein, long/cash), Handel ueber Laender-ETFs; Anleihesignal synthetisch aus FRED-Renditen.

```
Laender (ETF / lokaler Aktienindex fuer das Signal / FRED-Rendite): 
  US  SPY  / ^GSPC   / GS10 oder IRLTLT01USM156N
  JP  EWJ  / ^N225   / IRLTLT01JPM156N
  DE  EWG  / ^GDAXI  / IRLTLT01DEM156N
  GB  EWU  / ^FTSE   / IRLTLT01GBM156N
  FR  EWQ  / ^FCHI   / IRLTLT01FRM156N
  CA  EWC  / ^GSPTSE / IRLTLT01CAM156N
  AU  EWA  / ^AXJO   / IRLTLT01AUM156N
  CH  EWL  / ^SSMI   / IRLTLT01CHM156N
  NL  EWN  / ^AEX    / IRLTLT01NLM156N
  ES  EWP  / ^IBEX   / IRLTLT01ESM156N
  IT  EWI  / (kein Gratis-Index geprueft, EWI selbst als Signal) / IRLTLT01ITM156N
  SE  EWD  / (EWD selbst)  / IRLTLT01SEM156N
Synthetische Anleihe-Monatsrendite (je Land):
  y = FRED-Rendite/100;  r_B(m) = y(m-1)/12 - D(y(m-1)) * (y(m) - y(m-1))
  D(y) = (1 - (1+y/2)^-20)/y   # 10J-Par-Bond (Papier: konstante 5J-Laufzeit, hier nur 10J-Rendite verfuegbar; nur Vorzeichen zaehlt)
  Konservativ: Bond-Signal mit 1 Monat Verzug (Monate m-12 ... m-1), wegen Monatsmittel/Publikationsverzug.
Je Land c an T:
  sE = Vorzeichen( r12_Aktie_lokal(c) - rf12 )          # Preisindex ohne Dividende (Bias beachten)
  sB = Vorzeichen( 12M-Summe der r_B(c) - rf12 )        # mit 1 Monat Verzug
  Gewicht des Landes-Slices = 1 / N (N = Laender mit vollstaendigen Daten in diesem Monat)
  Slice in ETF(c), wenn sE > 0 und sB > 0; sonst Slice in SHY (vor 2002: ^IRX)
Backtest-Start handelbar: 1997-03 (EWx ab 1996-03 plus 12M Lookback). Frueher nur Signal-Studie.
```

Erwartung: Der Nutzen liegt in Diversifikation des Anleihesignals; weil Aktien-Laender stark korreliert sind, rechne ich mit einem Ergebnis nahe dem US-Umschalter. Abbruch: nach Kosten kein besserer Sharpe als Gleichgewichts-Laenderkorb mit reinem 12M-Aktientrend.

### 3.3 `xtsmom_us_ls_replica_volscaled` (Komplexitaet 3)

Moeglichst genaue US-Replik der Paper-Regel inklusive Short, als **Obergrenze** der Strategie (Short-ETF/Futures-Kosten, Borrow, Margin).

```
Instrumente: SPY, IEF (Variante: TLT; fuer Short-Test auch SH/TBT NICHT verwenden -> Zerfall durch Leverage-Pfad), Cash zu ^IRX
An T:  rE, rB wie 3.1
  Fall A: rE > 0 und rB > 0  -> pos = +1 in SPY
  Fall B: rE < 0 und rB < 0  -> pos = -1 in SPY
  Fall C: rB > 0 und rE < 0  -> pos = +1 in IEF
  Fall D: rB < 0 und rE > 0  -> pos = -1 in IEF
  (sonst 0 -> alles in Cash)
Vola-Skalierung (Eigenentwurf; das Paper-Chart skaliert nach CXO nur zur Darstellung auf 10 % Vola):
  sigma = Stdabw der taeglichen Renditen des aktiven Instruments, letzte 60 Handelstage, * sqrt(252)
  Hebel = min(2, 0.10 / sigma);  Gewicht = pos * Hebel
Cash-Rest verzinst zu ^IRX; Short-Erloes verzinst zu ^IRX minus 0.5 % p.a. Borrow-Fee (Annahme, parametrisieren)
```

Erwartung: Das Short-Bein von SPY (Fall B) hilft in Baerenmaerkten, kostet aber in V-foermigen Erholungen; Short-IEF (Fall D) zahlt in Zinsanstiegsphasen. Abbruch: Alpha ueber 3.1 nach Borrow und Kosten nicht signifikant (Deflated Sharpe) oder Ergebnis nur aus 1-2 Phasen.

### 3.4 `rsz_us_leads_country_etfs_longcash` (Komplexitaet 3)

Rapach/Strauss/Zhou (2013): vergangene US-Renditen sagen Renditen vieler Nicht-US-Laender voraus (nicht umgekehrt). Vereinfachtes Einfaktor-Modell, **nicht** das volle Modell des Papers (mir ist das volle Modell nicht bekannt, nur der Abstract).

```
Praediktor: SPY-Monatsrendite;  Universum: EWJ, EWG, EWU, EWQ, EWC, EWA, EWL, EWN, EWP, EWI, EWD, EWH, EWS; Cash = SHY/^IRX
Monatsrenditen aus angepassten Schlusskursen am letzten Handelstag des Monats; x_s = r_SPY(s) - rf(s); y_s = r_i(s+1) - rf(s+1)
An T (Ende Monat t), je Land i:
  Fenster: die letzten 120 Paare (x_s, y_s) mit s+1 <= t   (rollierend, kein Blick nach vorn)
  OLS: y = a + b*x;  Prognose f_i = a + b * x_t
  Schwelle: investiere nur, wenn f_i > Fenstermittel von y   (aequivalent: b*(x_t - Mittel(x)) > 0)
  Gewicht pro Land = 1/N; Slice in ETF(i) wenn Bedingung, sonst SHY
Handel T+1 Open. Vergleich Pflicht: gleiche Strategie mit Praediktor = eigene Vormonatsrendite des ETF (reines Momentum) und Zufalls-Timing gleicher Investitionsquote.
```

Warnung: Der Test misst Zeitzonen-/Handelszeitartefakte nicht: US-gelistete Laender-ETFs handeln zu US-Zeiten, ein Teil des in lokalen Indizes gemessenen Vorlaufs fehlt daher. Der Effekt bei den ETFs ist nur der monatliche Rest.

### 3.5 `htv_industry_leads_market_combo` (Komplexitaet 3)

Hong/Torous/Valkanov (2007): Branchenrenditen sagen die Marktrendite voraus (bis zu 2 Monate), Mechanismus: graduelle Informationsdiffusion. Zeitreihen-Ableitung, Eigenentwurf (das Paper testet Branchen-Praediktoren einzeln, die Kombinationsregel ist von mir); hohes Data-Snooping-Risiko (viele Branchen, wenig Signal).

```
Daten: Ken French "49_Industry_Portfolios" (monatlich, value-weighted), "F-F_Research_Data_Factors" (Mkt-RF, RF)  [Start 1926-07, ungeprueft]
Live-Ersatz (ETF): XLB XLE XLF XLI XLK XLP XLU XLV XLY (ab 1998-12-22), Markt = SPY
An Monatsende t, je Branche j (expandierendes Fenster, mind. 240 Monate):
  Regression: (Mkt_s+1 - RF_s+1) = a_j + b_j * (R_j,s - RF_s)   fuer alle s mit s+1 <= t
  f_j = a_j + b_j * (R_j,t - RF_t)
  F = Mittelwert aller f_j       # gleichgewichtete Kombination
  Mu = expandierender Mittelwert von Mkt-RF bis t
  Position naechster Monat: 100 % Markt (SPY/VFINX), wenn F > Mu; sonst 100 % Cash (SHY/^IRX)
Backtest-OOS erst ab Monat 241 der Daten; Kosten wie 3.1.
```

Erwartung: nahe null nach Kosten. Tse (2015, J. Empirical Finance): Mit 48 Branchen, 1946-2013, haben nur 1 bis 7 Branchen signifikante Vorhersagekraft; Gesamtbild mit Markteffizienz vereinbar. Menzly/Ozbas (2010) Lieferketten-Cross-Predictability sind hier **nicht** umgesetzt (benoetigt Input-Output-Tabellen, Komplexitaet 5, Zahlen nicht abgerufen).

## 4. Nach-Publikations-Verfall, Kosten, Tail-Risiken (zusammengefasst)

- **Cross-Asset-TSMOM (3.1-3.3):** Keine unabhaengige Replikation nach 2020 gefunden. Stichprobe 1980-2016 ist ein Anleihen-Bullenmarkt (CXO). Wenn der Vorteil mit der Aktien-Anleihen-Korrelation zusammenhaengt, ist der Regimewechsel 2021/22 (positive Korrelation) der Hauptverfallskanal. Konsequenz in der Regel 3.1: In 2022 waeren beide Vorzeichen negativ, also Cash (gut). Ein Zustand "Aktien +, Anleihen -" (z. B. 2021) schaltet die Aktie ab und kostet Rendite.
- **Lag der 12M-Regel:** Nach V-Erholungen (Maerz 2009, Maerz 2020) bleibt die 12M-Aktienrendite lange negativ, die Regel haelt IEF bzw. Cash und verpasst die Erholung (Momentum-Crash-Muster, mein Erwartungswert, nicht belegt).
- **Kosten:** Monatliche Entscheidung; die tatsaechliche Wechselzahl bei 3.1 ist unbekannt und muss der Backtest zaehlen. Bei 3.2 und 3.4 kommen breitere Laender-ETF-Spreads und mehr Steuerreibung hinzu. Paper-Ergebnisse sind brutto.
- **Long/Cash verwirft das Short-Bein:** Ein Teil des Paper-Alphas kann aus Shorts stammen; 3.1/3.2 sind dann keine Replikation, sondern eine konservative Ableitung. 3.3 prueft das.
- **Huang et al. 2020:** Ein Teil der "Vorhersage" ist moeglicherweise Drift; Pflichtvergleich: Strategie auf historischem Mittel/Buy&Hold gleicher Investitionsquote.
- **Lead-Lag Laender (3.4):** In-Sample stark, OOS fragil. Laut Suchzusammenfassung findet Siliverstovs (2015) positive Evidenz vor allem in US-Rezessionen und nennt die Ergebnisse fragil bzgl. Prognosezeitraum; Aye/Balcilar/Gupta (2017) finden einen zeitvariablen US-Effekt (OLS stark, Adaptive-Elastic-Net schwach). Erwartung: nach Kosten kein Vorteil.
- **Lead-Lag Branchen (3.5):** Tse (2015) schwaechte die US-Ergebnisse stark ab; nicht-US-Studien (Australien) finden anderen Mechanismus; Ergebnisse stuetzen eher "kein robuster Edge".
- **Tail-Risiken:** Beide Instrumente (Aktien/Anleihen) fallen gleichzeitig (Inflationsschock): Strategie kann zwar auf Cash gehen, aber nur mit 1 Monat Verzug + Gap-Risiko; Shorts in 3.3 haben unbegrenztes Verlustrisiko bei Squeeze; Zinssprung bei negativer Rendite-Konvexitaet.

## 5. Verwandte Idee (nicht als eigene Strategie gefuehrt)

Filter: Bond-Bein nur nutzen, wenn die 12M-Korrelation zwischen taeglichen SPY- und IEF-Renditen negativ ist. Motivation: CXO nennt Korrelationsaenderungen als Alternativerklaerung der Gewinne, Connolly et al. verknuepfen Unsicherheit mit der Korrelation. **Das ist mein Eigenentwurf ohne Paper-Beleg.** Nur testen, wenn 3.1 zuerst eine Basisrendite zeigt (Regel 3: nicht auf denselben Daten waehlen und bestaetigen).

## 6. Offene Punkte / Luecken

- Volltexte der Hauptpapers nicht gelesen; keine Sharpe-/Alpha-Tabellen. Falls Nick Zugriff auf JFE/SSRN hat, Tabellen zu 12/1 pro Land und Subsamples (vor/nach 2000) nachtragen.
- FRED-Serien: Start, Frequenz (Monatsmittel?), Aktualitaet pruefen.
- Gulko (2002), Baele et al. (2010), Hou (2007), Cohen/Frazzini (2008) nicht abgerufen.
- Keine Nach-2020-OOS-Evidenz fuer XTSMOM selbst gefunden. Fernandez-Perez et al. (2022) berichten laut Snippet ein Cross-Asset-TSMOM mit Oelvolatilitaet als Signal (andere Variante).

## 7. Quellen (URLs)

- Pitkaejaervi/Suominen/Vaittinen (2020), Tinbergen-Eintrag: https://tinbergen.nl/publication/168343/cross-asset-signals-and-time-series-momentum
- Pitkaejaervi et al. (2020), ScienceDirect (nur Treffer, 403): https://www.sciencedirect.com/science/article/abs/pii/S0304405X19302156
- CXO Advisory Review: https://www.cxoadvisory.com/equity-premium/cross-asset-class-intrinsic-momentum
- Alpha Architect Zusammenfassung (403, nicht abgerufen): https://alphaarchitect.com/cross-asset-signals-and-time-series-momentum/
- Quantpedia-Update 11.04.2017 (Suchtreffer): https://vvv.quantpedia.com/?p=739
- Aalto-Masterarbeit Pitkaejaervi 2016: https://epub.lib.aalto.fi/en/ethesis/id/14577
- Aalto-Mitteilung zur Annahme im JFE: https://aalto.fi/en/news/finance-paper-accepted-to-be-published-in-the-journal-of-financial-economics
- Rapach/Strauss/Zhou (2013), Abstract-Eintrag: https://academicnewsletter.sufe.edu.cn/info/360253
- Aye/Balcilar/Gupta (Empirica 2017), Repositorium: https://repository.up.ac.za/handle/2263/59374
- Hong/Torous/Valkanov (2007), Abstract-Eintrag: https://academicnewsletter.sufe.edu.cn/info/357378
- CXO zu Hong/Torous/Valkanov: https://www.cxoadvisory.com/economic-indicators/market-leading-industries
- Tse (2015), J. Empirical Finance 34:195-203: https://ideas.repec.org/a/eee/empfin/v34y2015icp195-203.html
- Menzly/Ozbas (2010), IDEAS: https://ideas.repec.org/a/bla/jfinan/v65y2010i4p1555-1580.html
- Huang/Li/Wang/Zhou (2020), IDEAS: https://ideas.repec.org/a/eee/jfinec/v135y2020i3p774-794.html
- Huang et al. (2020), WUSTL-Profil: https://profiles.wustl.edu/en/publications/time-series-momentum-is-it-there/
- Connolly/Stivers/Sun (2005), IDEAS: https://ideas.repec.org/a/cup/jfinqa/v40y2005i01p161-194_00.html
- Fernandez-Perez et al. (2022), ScienceDirect: https://www.sciencedirect.com/science/article/abs/pii/S0378426622002849
- D. E. Shaw (Juni 2021), Stock-Bond-Korrelation: https://www.deshaw.com/library/market-insight-revisiting-stock-bond-correlation
