# Familie: Makro-/Regime-/Vorhersage-Signale (Aktienpraemie-Prognose, Regime-Filter, Trend + Makro)

Stand: 2026-10-12 (zweiter Versuch; ein frueherer Lauf hatte nur zwei Hilfsskripte in `macro_checks/` hinterlassen, aber keine Notizen).
Autor: Recherche-Agent. Sprache: Deutsch. Alle Zahlen stammen entweder aus einer Quelle, die ich wirklich abgerufen habe (Quelle steht dabei), oder aus eigenen, UNGETESTETEN Plausibilitaetsrechnungen (gekennzeichnet "eigener Check"). Wo ich etwas nicht gefunden habe, steht "nicht gefunden".

## 0. Kurzfazit (ehrlich)

1. **Die klassischen Makro-Praediktoren (Dividendenrendite, Zinsstruktur, Kreditspreads, Inflation, ...) schlagen den historischen Mittelwert out-of-sample nicht verlaesslich.** Neely et al. (Tabelle 4) zeigen: nur 3 von 14 Makrovariablen haben ein positives R2_OS, und die liegen bei 0,05 % bis 0,29 % monatlich. Goyal-Welch-Zafirov (Folien 2023) fassen ihre Neuuntersuchung von rund 45 Variablen so zusammen: "Think 10 %" funktioniert, weitere 10-20 % mit Plus und Minus, "70-80 % poof".
2. **Die robusteste Komponente dieser Familie ist nicht Makro, sondern Trend** (Neely: technische Indikatoren schlagen Makro). Als reine Binaerregel (Aktien oder Cash) bleibt der Drawdown-Schutz in meinem eigenen Check ueber 1929-2026 und auch seit 2000 erhalten, die Renditeueberlegenheit gegenueber Buy&Hold aber nicht (seit 2013 klar darunter).
3. **Alles, was Makro-Vorhersage in Gewichte mit Hebel bis 1,5 uebersetzt (Neely-Mean-Variance, Sum-of-the-parts), zeigt in meinen Nachbauten nach Publikation negative Werte** (R2_OS in beiden Faellen etwa -1,2 %, CER-Gewinn negativ). Das Paper-Ergebnis laesst sich fuer die Zeit davor teilweise reproduzieren (Neely schwaecher, SOP fast exakt), aber es ist kein Edge, auf den man Kapital setzen sollte.
4. **Regime-Modelle (HMM / Jump-Modell) sind im Kern ein Volatilitaets-/Downside-Filter.** Das aktuellste Paper (Shu/Yu/Mulvey 2024) zeigt Sharpe 0,68 vs. 0,48 (S&P 500, 1990-2023, 10 bp Kosten, 1 Tag Verzoegerung), aber: ein Autorenteam, Hyperparameter-Tuning, keine unabhaengige Replikation gefunden. Eher "wahrscheinlich Drawdown-Schutz, Sharpe-Vorteil unsicher".
5. **Zinsstruktur als Rezessionsfilter (10J minus 3M) funktionierte bis 1999 (Sharpe 0,63 vs. 0,49), seit 2000 nicht mehr (0,39 vs. 0,42) und gab 2022-2026 in 46 % der Monate Fehlalarm** (eigener Check). Als Zusatz zum Trendfilter bringt es nichts.
6. **Gu-Kelly-Xiu / ML-Asset-Pricing ist mit Gratisdaten nicht reproduzierbar** (Aktien-Querschnitt mit Dutzenden Merkmalen) und gehoert nicht in das Quant-Lab-Budget. Kein Strategieeintrag.

Empfehlung fuer das Quant-Lab: (a) die binaere Trendregel als "Sicherheits-Baustein" weiter pruefen (Hypothese + Walk-forward + Steuern), (b) Jump-Modell nur als optionales, sauber getestetes Experiment, (c) Neely-MV, SOP und Zinsstruktur-Filter nur als dokumentierte Negativ-Ergebnisse fuehren.

## 1. Abrufstatus (Transparenz)

Aufwand: 15 Web-Abrufe (WebSearch + WebFetch). PDFs kamen als Binaerdaten zurueck und wurden lokal mit `pypdf` in Text umgewandelt (kein weiterer Web-Abruf). Zusaetzlich liefen eigene Python-Checks mit Yahoo/French/Shiller-Daten und FRED-Datenstartpruefung (Daten-Downloads, keine Literaturabrufe).

| Quelle | Status |
|---|---|
| Neely/Rapach/Tu/Zhou, St.-Louis-Fed WP 2010-008H (Aug 2013) | Voll abgerufen (PDF, 48 Seiten lokal extrahiert). Tabellen 4 und 5 gelesen. |
| Ferreira/Santa-Clara, NBER WP 14571 (Dez 2008) | Voll abgerufen (PDF, 34 Seiten). Das ist die **Working-Paper-Fassung**; die JFE-Zahlen (2011) kenne ich nur aus einer Suchergebnis-Zusammenfassung. |
| Shu/Yu/Mulvey, arXiv 2402.05272 (v3 Sep 2024) | Abstract-Seite und Voll-PDF (22 Seiten) abgerufen. |
| Goyal/Welch/Zafirov, Folien Maerz 2023 (Welch-Homepage) | Voll abgerufen (41 Folien), aber fast ohne Zahlen. Veroeffentlichte Fassung RFS 37(11), 3490-3557 (2024) nur aus Suchergebnis bekannt, nicht geoeffnet. |
| Gu/Kelly/Xiu, NBER w25398 | Nur Abstract-Seite. |
| Nystrup/Hansen/Madsen/Lindstroem (Regime-based vs. static) | Nur DTU-Seite zur Masterarbeit (Behauptung ohne Zahlen) + Suche. Das Journal-Paper selbst NICHT gesehen. |
| Welch/Goyal RFS 2008, Campbell/Thompson RFS 2008 (OUP-Seiten) | Seiten kamen abgeschnitten (nur Titel/Heft). **Nicht als Beleg verwendet.** Was ich ueber Campbell-Thompson schreibe, steht in Neely et al. bzw. im SOP-Paper. |
| Kelly/Malamud/Zhou (JF 2024), Nagel (NBER w34104, 2025) | Nur Suchergebnis-Zusammenfassungen. **Nicht abgerufen**, deshalb nur als Hinweis (Abschnitt 6), nicht als Beleg. |
| Hamilton 1989, Kritzman/Page/Turkington 2012, Rapach/Strauss/Zhou 2010, Estrella/Mishkin | Nicht abgerufen. Rapach/Strauss/Zhou nur ueber Neely et al. zitiert. |

## 2. Gemeinsame Implementierungsregeln (gelten fuer alle Strategien unten)

- Signal am Schlusskurs des letzten Handelstags t eines Monats (oder Tages bei taeglichen Modellen), Handel fruehestens zum Schluss von t+1 (naechster Handelstag), neue Position verdient ab t+2. Das ist exakt die Konvention, die auch das Jump-Modell-Paper nutzt (Regime von Tag t wird am Ende von t+1 gehandelt).
- Kosten: Standard-Annahme 10 bp pro vollstaendigem Wechsel (einseitig). Neely nutzt 50 bp pro Transaktion als Sensitivitaet. Immer beide rechnen.
- Steuern (Deutschland, Abgeltungssteuer): Jeder Wechsel Aktie -> Cash realisiert Gewinne; Steuerstundung des Buy&Hold geht verloren. Bei 1-1,5 Wechseln pro Jahr nicht vernachlaessigbar. In keiner der unten genannten Zahlen enthalten.
- Benchmark-Pflicht: Buy&Hold desselben Index, Cash-Rendite (French RF bzw. BIL/SHV), und der Mehrfachtest-Hinweis (siehe Abschnitt 5).
- Daten-Wahl-Falle: Die Neely-Signale reagieren auf Preisindex vs. Total-Return-Index (siehe 3.3). Signal immer aus dem **Preisindex** (^GSPC) bilden, so wie im Paper.

## 3. Strategien (nach erwarteter Robustheit sortiert, beste zuerst)

### 3.1 trend_ma12_us_equity_cash - Binaerer Trendfilter (Neely-Signal MA(1,12) als reine Timing-Regel)

**Quelle der Signaldefinition:** Neely/Rapach/Tu/Zhou (Gl. 4-6): `S=1` wenn `MA(s) >= MA(l)` bzw. `P_t >= P_{t-m}`; monatliche Regeln mit s in {1,2,3}, l in {9,12}, m in {9,12}. Das Paper nutzt die Signale als Regressoren, nicht als Handelsregel. Die Binaerregel ist **meine** Uebertragung (Eigenentwurf); der Drawdown-Schutz ist vor allem durch eigene Checks belegt, nicht durch das Paper.

**Regel (Pseudocode):**
```
Signalreihe:  P_m = Schlusskurs ^GSPC am letzten Handelstag jedes Kalendermonats m (Preisindex, ohne Dividenden)
Am Monatsende t:
   MA12_t = Mittel(P_m ueber die letzten 12 Monatsenden inkl. t)
   S_t = 1 wenn P_t >= MA12_t, sonst 0                         # Neely MA(1,12)
   (Varianten: MA(2,12): Mittel(P_t, P_{t-1}) >= MA12_t ; SMA10: P_t > Mittel der letzten 10 Monatsenden ; MOM12: P_t >= P_{t-12})
Ausfuehrung: Order zum Schlusskurs des naechsten Handelstags t+1; Position = S_t * 100 % Aktien-ETF + (1-S_t) * 100 % Cash
Haltedauer:  bis zum naechsten Monatsend-Signal. Keine Hebelung, keine Shorts. Kosten 10 bp je Wechsel.
```

**Daten (gratis):** Signal: `^GSPC` Close (Yahoo, ab 1927-12-30, Preisindex). Renditen: Ken French `F-F_Research_Data_Factors_daily` (Mkt-RF + RF; ab 1926-07-01, Gesamtmarkt als Total-Return-Proxy) oder investierbar `SPY` (Yahoo adjusted, ab 1993-01-29) bzw. `VTSMX` (ab 1992-04-27). Cash: French RF (taeglich) oder `BIL` (ab 2007-05-30) / `SHV` (ab 2007-01-11).

**Eigener Check (UNGETESTET, `macro_checks/trend_gspc.py`; Signal aus ^GSPC-Preisindex, Renditen French-Gesamtmarkt, 10 bp, Ausfuehrung t+1):**

| Zeitraum | Strategie | CAGR | Vol | Sharpe | MaxDD | im Markt |
|---|---|---|---|---|---|---|
| 1930-2026 | Buy&Hold | 9,68 % | 17,0 % | 0,45 | -80,2 % | 100 % |
| 1930-2026 | MA(1,12) | 9,42 % | 11,6 % | 0,57 | -37,4 % | 68 % |
| 1930-2026 | SMA10 | 9,30 % | 11,5 % | 0,57 | -37,3 % | 67 % |
| 2000-2026 | Buy&Hold | 8,59 % | 19,5 % | 0,42 | -54,6 % | 100 % |
| 2000-2026 | MA(1,12) | 8,41 % | 12,7 % | 0,55 | -21,9 % | 74 % |
| 2013-2026 | Buy&Hold | 15,08 % | 17,3 % | 0,80 | -34,2 % | 100 % |
| 2013-2026 | MA(1,12) | 10,51 % | 12,7 % | 0,71 | -21,9 % | 84 % |

Wechsel pro Jahr: MA(1,12) 1,21, SMA10 1,49, MA(2,12) 0,92, MOM12 0,98. Variante mit Signal aus dem French-Total-Return-Index (`trend_yc.py`, 1962-2026): MA(1,12) Sharpe 0,53 vs. 0,44, MaxDD -32,3 % vs. -54,6 %.

**Ehrliche Einordnung:** Etwa gleiche Rendite wie Buy&Hold ueber das Jahrhundert (9,4 % vs. 9,7 %), aber Drawdown etwa halbiert. In der langen Bullenphase 2013-2026 verliert die Regel rund 4,6 Pp. CAGR gegen Buy&Hold. Der "Edge" ist Risikoreduktion, kein Mehr-Rendite. Das passt zum Quant-Lab-Erfolgsfall 2 (Geld sicher halten).

**Ausfallmodi / Tail-Risiken:** Verspaetete Wiedereinstiege nach V-foermigen Erholungen (2009, 2020); Saegezahn-Seitwaertsphasen (viele kleine Verluste); Ein-Tages-Crash zwischen zwei Monatsend-Signalen (Oktober 1987) wird nicht abgefangen; Stichtags-Zufall (Monatsende-Termin "timing luck"); deutsche Steuer auf realisierte Gewinne; Signal haengt an Index-Wahl (Preis- vs. Total-Return-Index).

### 3.2 jump_model_regime_01_equity - Statistisches Jump-Modell, 0/1-Regimefilter (Shu/Yu/Mulvey 2024), HMM als Vergleich

**Quelle:** Shu, Yu, Mulvey (2024), arXiv 2402.05272, "Downside Risk Reduction Using Regime-Switching Signals: A Statistical Jump Model Approach". Hamilton-artige HMMs sind darin die Vergleichsbasis (2-Zustands-Gauss-HMM, rollierend, 3000 Tage Trainingsfenster, Bulla et al. 2011).

**Regel (Pseudocode, nach dem Paper; Teile in eckigen Klammern sind meine Luecken-Fuellung):**
```
Daten:   taegliche Gesamtrendite R_t des Aktienindex, taegliche Cash-Rendite RF_t; x_t = R_t - RF_t (Tagesueberrendite)
Features (alle exponentiell gewichtet, pandas ewm(halflife=h)):
   f1_t = Abwaertsabweichung DD_t(h=10)  = sqrt( EWM_h( min(x,0)^2 ) )
   f2_t = Sortino_t(h=20) = EWM_20(x) / DD_t(20)
   f3_t = Sortino_t(h=60) = EWM_60(x) / DD_t(60)
   [Features auf dem Trainingsfenster standardisieren]
Modell:  K=2 Zustaende, Statistisches Jump-Modell:
   min ueber (Zentroide theta_0, theta_1; Zustandsfolge s) :   SUM_t 0.5*||f_t - theta_{s_t}||^2  +  lambda * SUM_t 1[s_t != s_{t-1}]
   Loesung per Koordinatenabstieg (Zentroide <-> Zustandsfolge per Dynamischer Programmierung), 10 Neustarts (k-means++), bester Zielwert zaehlt
   Trainingsfenster: 3000 Handelstage (~12 Jahre); Zentroide werden alle 6 Monate neu geschaetzt
   Bull-Zustand (s=0) = der Zustand mit der hoeheren kumulierten Ueberrendite im Trainingsfenster; Bear (s=1) = der andere
Online-Inferenz am Tag t (kein Blick nach vorn):
   mit den aktuellen Zentroiden DP ueber die letzten l=3000 Tage bis t laufen lassen, letzten Zustand s_hat_t nehmen
lambda:  jeden Monat neu waehlen aus einem Kandidatengitter [Eigenvorschlag {5,10,20,50,100}; Paper nennt lambda=50 als typischen Wert, Gitter nicht gefunden]:
   fuer jedes lambda die Online-Zustandsfolge der letzten 8 Jahre bilden, 0/1-Strategie mit 1 Tag Verzoegerung simulieren, lambda mit hoechstem Sharpe nehmen; gilt ab dem uebernaechsten Tag
Handel:  w = 1 (100 % Aktien) wenn s_hat_t = Bull, sonst 0 (100 % Cash). Zustand von Tag t wird am Schluss von t+1 gehandelt (Position verdient ab t+2). Kosten 10 bp einseitig.
```
HMM-Vergleich im Paper: rollierender 2-Zustands-Gauss-HMM auf taeglichen Log-Renditen (Python `hmmlearn`), Zustand mit hoher Vol = Bear, Median-Filter ueber k Tage (k per Kreuzvalidierung), sonst gleiche 0/1-Regel.

**Daten (gratis):** Rendite: French `Mkt-RF + RF` taeglich (ab 1926-07-01; 3000 Tage Training + 8 Jahre Validierung brauchen ca. 20 Jahre Vorlauf, OOS also ab ca. 1946, inklusive der Weltwirtschaftskrise-Daten nur im Training) oder `SPY` adjusted (ab 1993-01-29; dann OOS erst ab ca. 2013, zu kurz). Cash: French RF. Andere Maerkte: `^GDAXI` (ab 1987-12-30), `^N225` (ab 1965-01-05, Preisindex, nicht Total Return). Das Paper nutzt Bloomberg-Total-Return-Reihen ab 1970 und 3M-Bill-Renditen (GFD), OOS 1990-2023.

**Paper-Zahlen (Tabelle 4, S&P 500, 1990-2023, 10 bp einseitig, 1 Tag Verzoegerung):**

| | Buy&Hold | HMM 0/1 | Jump-Modell 0/1 |
|---|---|---|---|
| Rendite (CAGR) | 10,2 % | 8,5 % | 11,2 % |
| Volatilitaet | 18,2 % | 11,3 % | 13,1 % |
| Sharpe | 0,48 | 0,54 | 0,68 |
| MaxDD | -55,2 % | -28,9 % | -26,6 % |
| Umschlag p.a. | 0 % | 141 % | 44 % |
| mittlere Investitionsquote | 100 % | 72 % | 80 % |

DAX: Sharpe 0,30 / 0,35 / 0,44, MaxDD -72,7 % / -40,5 % / -39,4 %. Nikkei 225: Sharpe 0,12 / 0,19 / 0,31, MaxDD -79,1 % / -48,6 % / -45,3 %. Robustheit gegen Verzoegerung (Tabelle 5, S&P 500 Sharpe): JM 0,68 / 0,71 / 0,70 bei 1 / 5 / 10 Tagen; HMM 0,54 / 0,55 / 0,51.

**Ehrliche Einordnung:** Die Drawdown-Reduktion (-55 % -> -27 %) ist plausibel und wirtschaftlich nachvollziehbar (Volatilitaets-Clustering). Der Sharpe-Vorteil ist die Aussage des Autorenteams mit selbst getunten Hyperparametern auf genau der Historie, auf der getestet wird; eine unabhaengige Replikation habe ich nicht gefunden. Die Autoren sagen selbst, die Modelle seien "interpretativ, nicht praediktiv" und erkennen Regimewechsel mit Verzoegerung.

**Ausfallmodi / Tail-Risiken:** Latenz am Anfang und Ende von Crashs (V-Erholungen werden verpasst); Fehlalarme in langanhaltend turbulenten Seitwaertsphasen; Modell-/Hyperparameter-Risiko (lambda, Features); Implementierungsaufwand (eigene DP/Koordinatenabstiegs-Implementierung noetig; Paper verweist auf eine GitHub-Seite des Erstautors `Yizhan-Oliver-Shu/jump-models`, von mir nicht geprueft); `hmmlearn` ist im Quant-Lab-venv nicht installiert; taegliches Re-Signal heisst taegliche Pruefung; Steuer bei 44 % Umschlag p.a. (Paper) nicht enthalten.

### 3.3 neely_techind_mv_timing - Technische Indikatoren -> Aktienpraemien-Prognose -> Mean-Variance-Gewicht (Neely/Rapach/Tu/Zhou)

**Quelle:** Neely, Rapach, Tu, Zhou, "Forecasting the Equity Risk Premium: The Role of Technical Indicators", St. Louis Fed WP 2010-008H (Aug 2013); veroeffentlicht in Management Science 2014 (Venue laut Goyal/Welch/Zafirov-Folien).

**Regel (Pseudocode, aus Abschnitt 3-4 des Papers):**
```
Daten:  monatliche Schlusskurse P_m (^GSPC, Preisindex) und monatliche Aktien-Ueberrendite ex_m = R_m - rf_m (French Mkt-RF aufgezinst; rf_m = French RF aufgezinst)
Indikatoren je Monatsende t (8 preisbasierte; die Paper-Volumen-Indikatoren VOL(s,l) lasse ich weg):
   S_MA(s,l),t = 1[ Mittel(P_t..P_{t-s+1}) >= Mittel(P_t..P_{t-l+1}) ] , s in {1,2,3}, l in {9,12}
   S_MOM(m),t  = 1[ P_t >= P_{t-m} ] , m in {9,12}
Prognose (expandierende OLS, nur realisierte Paare):
   fuer jeden Indikator i:  ex_{s+1} = a_i + b_i * S_{i,s}   fuer s = 1951-01 .. t-1       # Schaetzbeginn 1951-01 (Paper: 1950:12)
   rhat_{t+1,i} = a_i + b_i * S_{i,t}
   rhat_{t+1}   = Mittel der 8 rhat_{t+1,i}                                                   # einfache Kombination (Paper: PC-TECH ~ Mittel der Einzelprognosen)
Gewicht:
   sigma2_t = Stichprobenvarianz (ddof=1) der letzten 60 monatlichen Ueberrenditen bis t
   w_t = clip( rhat_{t+1} / (gamma * sigma2_t) , 0 , 1.5 ),   gamma = 5
Portfolio: w_t * Aktien + (1-w_t) * Cash (w>1: Cash-Kredit zu RF [Annahme]; Variante B fuer Kleinanleger: clip auf [0,1])
Takt:    monatlich. Signal am Schlusskurs des letzten Handelstags t, Handel zum Schluss von t+1. Kosten 10 bp (Paper-Sensitivitaet 50 bp) auf |w_t - w_{t-1}|.
OOS-Beginn: 1966-01 (Paper). Vergleichsportfolio "HA": gleiche Regel mit rhat = Mittel aller bisherigen ex_m.
```

**Paper-Zahlen (Abschnitte 3-4, OOS 1966:01-2011:12, 552 Monate; Tabellen 4/5):**
- R2_OS einzelner technischer Indikatoren alle positiv: MA(1,9) 0,24 %, MA(1,12) 0,63 %, MA(2,12) 0,78 %, MOM(12) 0,15 %, VOL(1,12) 0,80 %; PC-TECH 0,65 %; Kombination aus 14 Makro-Einzelprognosen 1,16 %; Sum-of-the-parts 1,32 %; PC-ECON -0,86 %; **PC-ALL (Makro + Technik) 1,79 %**, aber nur in Rezessionen (11,24 %), in Expansionen -2,80 %.
- Makro einzeln: nur DY (0,05 %), RVOL (0,19 %), LTR (0,29 %) positiv; TMS -0,99 %, DFY -0,64 %, INFL -0,45 %.
- Nutzen (gamma 5, Gewichte 0-1,5, 60-Monats-Varianz): CER des Historischer-Mittelwert-Portfolios 3,54 % p.a.; CER-Gewinn MA(1,12) 2,91 % (netto 50 bp: 2,51 %), MA(2,12) 3,17 % (netto 2,82 %); PC-ALL 4,94 % (netto 4,12 %), Sharpe(monatlich) 0,16 vs. 0,05 fuer HA. Umschlag der Indikator-Portfolios 2- bis 5-mal so hoch wie HA (HA: 2,09 % pro Monat). CER-Gewinne konzentrieren sich auf Rezessionen (MA(1,12): 18,91 % in Rezessionen, -0,27 % in Expansionen).
- Data-Mining-Test (Clark-McCracken maxMSFE-F): p = 0,03.

**Eigener Nachbau (UNGETESTET, `macro_checks/neely_gspc.py`, Signale ^GSPC-Preisindex, Ziel = French-Gesamtmarkt, Kosten 50 bp / 10 bp):**

| Variante | Zeitraum | R2_OS | CER-Gewinn p.a. (50 bp) | Sharpe monatl. Modell / HA / BH |
|---|---|---|---|---|
| MA(1,12) | 1966-2011 | 0,40 % (Paper 0,63 %) | 2,06 % (Paper netto 2,51 %) | 0,092 / 0,051 / 0,09 |
| MA(1,12) | **2012-2026** | **-1,21 %** | **-1,44 %** (10 bp: -0,90 %) | 0,183 / 0,219 / 0,27 |
| MA(1,12) | 1966-2026 | 0,06 % | 1,22 % | 0,113 / 0,089 / 0,13 |
| MA(2,12) | 2012-2026 | -1,07 % | -1,40 % | 0,184 / 0,219 / 0,27 |
| Kombination der 8 | 2012-2026 | -0,79 % | -1,01 % | 0,194 / 0,219 / 0,27 |
| MA(1,12) mit Signal aus Total-Return-Index (French) | 1966-2011 | -0,02 % | 1,17 % | 0,069 / 0,051 / 0,09 |

CAGR MA(1,12) 2012-2026: 8,45 % vs. Buy&Hold 15,13 % (MaxDD -27,2 % vs. -24,9 %). Fazit des Checks: Richtung des Papers fuer 1966-2011 reproduzierbar, Groesse etwa 60-80 % des Papers (R2_OS 0,40 vs. 0,63; CER netto 2,06 vs. 2,51); nach 2011 negativ. Das Ergebnis haengt am Index (Preis vs. Total Return) - ein Warnzeichen fuer Fragilitaet.

**Post-Publikation / Kritik:** Goyal/Welch/Zafirov (Folien 2023) fuehren die 14 technischen Indikatoren (Stichprobe 1951:02-2021:12) unter ihren "Favoriten" (rund 10 % der ca. 45 Variablen), Zahlen dazu stehen nicht auf den Folien. Mein Nachbau sieht seit 2012 keinen Nutzen. Beide Aussagen stehen nebeneinander: die Folien spiegeln Vollstichprobenwerte bis 2021, mein Check trennt 2012-2026 ab.

**Ausfallmodi / Tail-Risiken:** Hebel bis 1,5 und Umschlag um Faktor ~4 gegenueber HA (Paper) -> Kostensensitiv; Gewinn konzentriert in wenigen Rezessionen (1973-75, 2008) - sehr wenige unabhaengige Ereignisse; in Expansionen ist der Nutzen null bis negativ (Paper: PC-TECH -0,29 % in Expansionen); Parameter-Instabilitaet der rekursiven OLS-Koeffizienten.

### 3.4 sop_valuation_timing - Sum-of-the-parts-Prognose (Ferreira/Santa-Clara) mit Mean-Variance-Gewichten

**Quelle:** Ferreira, Santa-Clara, "Forecasting Stock Market Returns: The Sum of the Parts is More than the Whole", NBER WP 14571 (Dez 2008), veroeffentlicht Journal of Financial Economics 100(3), 514-537 (2011) (Venue laut Suchergebnis).

**Regel (Pseudocode, vereinfachte Variante "nur Dividendenrendite + Gewinnwachstum", Multiple-Wachstum = 0):**
```
Daten:  Shiller ie_data.xls monatlich ab 1871-01: P (S&P Comp. Preis), D (Dividende, annualisiert), E (Gewinn, annualisiert); Marktrendite: French Mkt-RF + RF, rf: French RF
Am Monatsende t (Informationsverzoegerung: D und E um 3 Monate verzoegern, weil Shiller interpoliert):
   dp_t   = ln( 1 + D_{t-3} / P_t )
   ge20_t = ln( E_{t-3} / E_{t-243} ) / 20            # 20-Jahres-Durchschnitt des jaehrlichen Gewinnwachstums (Paper: gleitender 20-Jahres-Durchschnitt des Gewinnwachstums)
   erwartete Jahresrendite   rhat_ann_t = dp_t + ge20_t   # Paper: E(gm)=0 in dieser Variante
   erwartete Monats-Ueberrendite muhat_{t+1} = rhat_ann_t / 12 - rf_t
Gewicht:  w_t = clip( muhat_{t+1} / (gamma * sigma2_t) , 0 , 1.5 ), gamma = 2 (Paper) [Variante gamma = 5], sigma2_t = Varianz ALLER bisherigen Monatsueberrenditen (expandierend, Paper)
Takt:     monatlich, Signal am Schlusskurs t, Handel zum Schluss t+1, Kosten 10 bp auf |dw|
Benchmark: gleiche Regel mit muhat = Mittel aller bisherigen Monatsueberrenditen (historischer Mittelwert)
OOS-Beginn: 20 Jahre nach Stichprobenstart (Paper: Jan 1948 bei Start Dez 1927).
```
Die Vollvariante des Papers addiert zusaetzlich eine Prognose des Multiple-Wachstums (Regression auf Zins/Spread-Variablen mit Shrinkage bzw. "Multiple Reversion"); die habe ich nicht nachgebaut.

**Paper-Zahlen (WP-Fassung Dez 2008; Stichprobe Dez 1927-Dez 2007; Prognosen ab Jan 1948):** nur Dividendenrendite + Gewinnwachstum: R2_OS monatlich 1,32 %, CER-Gewinn 1,79 % p.a., Sharpe-Gewinn 67 %; hoechste Variante: CER-Gewinn bis 2,33 % p.a., Sharpe +73 %; Historischer Mittelwert: CER 7,4 % p.a., Sharpe 0,45. Teilperiode 1977-2007 (zweite Haelfte): R2_OS fuer Dividende + Gewinnwachstum 0,98 % (erste Haelfte 1,80 %), "es gibt einen Rueckgang ueber die Zeit". Zum Vergleich in derselben Stichprobe: Campbell-Thompson-Ansatz CER-Gewinn 1,5 %, Sharpe-Gewinn 27 %; traditionelle Prognoseregressionen meist negativ (R2_OS -1,78 % bis -0,05 % bei Ausnahme NTIS 0,69 %). Journal-Fassung laut Suchergebnis (nicht selbst gelesen): R2_OS >1,3 % monatlich, Sharpe-Gewinn 0,3.

**Eigener Nachbau (UNGETESTET, `macro_checks/sop_shiller.py`; Shiller-Datei Stand Sep 2023, E/D bis 2023-06; 10 bp):**

| Zeitraum | gamma | R2_OS | CER-Gewinn p.a. | Sharpe (ann.) Modell / HA / BH | mittleres Gewicht Modell / HA |
|---|---|---|---|---|---|
| 1947-2007 | 2 | 1,30 % (WP 1,32 %) | 0,47 % (WP 1,79 %) | 0,79 / 0,47 / 0,52 | 0,51 / 0,96 |
| 2008-2023 | 2 | **-1,17 %** | **-1,79 %** | 0,51 / 0,59 / 0,60 | 0,98 / 1,11 |
| 2008-2023 | 5 | -1,17 % | -0,84 % | 0,49 / 0,59 / 0,60 | 0,40 / 0,44 |
| 1980-2023 | 2 | -0,21 % | -1,00 % | 0,56 / 0,52 / 0,54 | 0,64 / 1,06 |
| 1947-2023 | 2 | 0,68 % | 0,01 % | 0,64 / 0,50 / 0,53 | 0,61 / 0,99 |

Der Nachbau trifft das WP fuer 1947-2007 bei R2_OS (1,30 % vs. 1,32 %) und Sharpe (+68 % vs. WP +67 %) fast exakt; der CER-Gewinn ist kleiner. Nach 2008 kippt alles ins Negative.

**Ausfallmodi / Tail-Risiken:** Bewertung kann jahrzehntelang "teuer" bleiben (2010er: Modell unterinvestiert); Shiller-Gewinne werden rueckwirkend interpoliert/revidiert (Look-ahead-Gefahr, deshalb 3 Monate Verzoegerung - die Wahl ist willkuerlich); die Gewinnreihe ist langsam und wird rueckwirkend interpoliert; nur ein Aktienmarkt, eine Zeitreihe, ueberlappende Bewertungszyklen -> wenige unabhaengige Beobachtungen; das Paper selbst zeigt abnehmende Prognosegueete ueber die Zeit (Teilperioden).

### 3.5 term_spread_recession_filter - Zinsstruktur-Rezessionsfilter (10J minus 3M), allein und mit Trend

**Quelle (Evidenz):** Neely et al.: TMS (Term Spread) hat zwar R2_OS -0,99 %, aber signifikant kleineren MSFE nach Clark-West (2,08, 5 %-Niveau); CER-Gewinn 1,88 % p.a. (netto 50 bp 1,44 %), Sharpe(monatl.) 0,12 (bester Makro-Wert), Rezessions-CER-Gewinn 8,95 %, Expansionen 0,42 %. Die Binaerregel selbst stammt nicht aus dem Paper; sie ist ein Eigenentwurf, die Evidenz dafuer ist mein eigener Check.

**Regel (Pseudocode):**
```
Daten:  ^TNX (10J-Rendite in %, Yahoo, ab 1962-01-02) und ^IRX (13-Wochen-Bill in %, Yahoo, ab 1960-01-04); alternativ FRED T10Y3M (ab 1982-01-04, gratis CSV https://fred.stlouisfed.org/graph/fredgraph.csv?id=T10Y3M)
Am letzten Handelstag t jedes Monats:  spread_t = ^TNX_t - ^IRX_t    (Prozentpunkte)
   S_t = 1 wenn spread_t > 0, sonst 0
Ausfuehrung:  Handel zum Schluss von t+1; Position = S_t * 100 % Aktien-ETF + (1-S_t) * Cash; Kosten 10 bp je Wechsel
Variante "Trend UND Kurve":  Aktien nur wenn  (P_t > SMA10_t)  UND  (spread_t > 0), sonst Cash
```

**Eigener Check (UNGETESTET, `macro_checks/trend_yc.py`, French-Gesamtmarkt, 10 bp):**

| Zeitraum | Strategie | CAGR | Vol | Sharpe | MaxDD | im Markt |
|---|---|---|---|---|---|---|
| 1962-2026 | Buy&Hold | 10,70 % | 16,2 % | 0,44 | -54,6 % | 100 % |
| 1962-2026 | Kurve>0 | 11,20 % | 14,9 % | 0,50 | -54,8 % | 87 % |
| 1962-2026 | SMA10 | 9,77 % | 11,5 % | 0,50 | -32,3 % | 74 % |
| 1962-2026 | SMA10 UND Kurve | 9,93 % | 10,8 % | 0,54 | -32,3 % | 66 % |
| 1962-1999 | Buy&Hold / Kurve>0 | 12,20 % / 13,78 % | 13,3 % / 12,4 % | 0,49 / **0,63** | -48,2 % / -33,1 % | |
| 2000-2026 | Buy&Hold / Kurve>0 | 8,59 % / 7,63 % | 19,5 % / 17,9 % | 0,42 / **0,39** | -54,6 % / -54,8 % | |
| 2000-2026 | SMA10 / SMA10 UND Kurve | 7,89 % / 7,02 % | 12,7 % / 11,7 % | 0,51 / 0,47 | -24,9 % / -21,8 % | |

Anteil Monate mit Kurve <= 0: 13,0 % insgesamt, **46,4 % der Monate seit 2022**, waehrend der Markt stark stieg (Fehlalarm). Wechsel pro Jahr: Kurve>0 0,56; SMA10 UND Kurve 1,46.

**Fazit:** Bis 1999 deutlich nuetzlich, danach kein Nutzen mehr (Sharpe unter Buy&Hold; Max-Drawdown -54,8 % entspricht dem von Buy&Hold, die Krise 2007-09 wurde also nicht vermieden; vermutlich war die Kurve vor dem Crash wieder positiv, im Detail nicht geprueft). Als Zusatz zum Trendfilter verschlechtert es seit 2000 den Sharpe (0,47 vs. 0,51). **Empfehlung: nicht verwenden**, nur als Negativ-Eintrag fuehren.

**Ausfallmodi / Tail-Risiken:** Variable Vorlaufzeit (Monate bis Jahre); Strukturbruch durch Notenbank-Politik (QE, Zinsen am Nullpunkt); Fehlalarm 2022-2026; ^IRX ist ein Diskontsatz (kein exakter Zinssatz); wenige Rezessionen = sehr wenige Beobachtungen.

## 4. Nicht als Strategie aufgenommen (und warum)

- **Gu/Kelly/Xiu (2020, RFS 33(5), 2223-2273):** Abstract (NBER w25398): ML-Methoden, am besten Baeume und neuronale Netze, "doubling the performance of leading regression-based strategies"; dominante Signale Momentum, Liquiditaet, Volatilitaet. R2_OS- und Sharpe-Zahlen: auf der abgerufenen Seite **nicht gefunden**. Das Verfahren nutzt Aktien-Querschnitte mit sehr vielen Merkmalen; solche Daten (CRSP/Compustat) sind nicht gratis. Das ist meine Einschaetzung, nicht Inhalt der abgerufenen Seite. Kein Quant-Lab-Kandidat.
- **Makro-Praediktoren allein (Dividendenrendite, TBL, LTY, DFY, INFL, ...):** Neely Tabelle 4: R2_OS meist negativ. Goyal/Welch/Zafirov-Folien: 17 Originalvariablen von Goyal/Welch (2008) "no variable really held up out of sample", unverhaeltnismaessiger Einfluss des Bearmarkts 1974-75. Keine eigene Strategie.
- **Kombinierte Makro-Prognosen (Rapach/Strauss/Zhou 2010):** Laut Neely (Fussnote 29) R2_OS 1,16 % fuer das Mittel der 14 Makro-Einzelprognosen (1966-2011). Ich habe das Original nicht abgerufen und kein Gratis-Datenset (Goyal-Daten) in diesem Lauf nachgebaut.
- **Kritik/Replikation Virtue-of-Complexity:** Suchergebnis (nicht abgerufen) nennt Nagel, NBER w34104 (2025), "Seemingly Virtuous Complexity in Return Prediction" mit der Aussage, der scheinbare Marktzeit-Erfolg komplexer Modelle (Random Fourier Features) sei im Kern eine volatilitaets-gewichtete Momentum-Strategie, bei Kunstdaten schneide sie schlecht ab. Als Hinweis behandeln, nicht als geprueften Beleg.

## 5. Offene Punkte / Hypothesen-Vorschlaege fuer docs/HYPOTHESEN.md

1. **H-Makro-1 (Trendfilter):** "Binaerer MA(1,12)-Filter auf US-Aktien (Signal ^GSPC) halbiert den Max-Drawdown gegenueber Buy&Hold bei Sharpe >= Buy&Hold, auch nach 10 bp Kosten und deutscher Steuer." Abbruch: MaxDD-Verbesserung < 25 % oder Sharpe < Buy&Hold - 0,05 im Walk-forward ab 2000. Test: mehrere Maerkte (^GDAXI, ^N225, EFA ab 2001-08-27), nicht nur USA.
2. **H-Makro-2 (Jump-Modell):** "Das 0/1-Jump-Modell schlaegt den einfachen MA(1,12)-Filter im Sharpe nach Kosten." Abbruch: kein Vorteil auf French-Gesamtmarkt OOS ca. 1946-2026 im Walk-forward. Erst nach H-Makro-1.
3. **H-Makro-3 (Negativ-Hypothesen):** Neely-MV, SOP und Zinsstruktur-Filter haben nach Publikation keinen Nutzen. Wuerden nur dann aufgegriffen, wenn ein Test auf einem **anderen Markt** (nicht USA) ein positives R2_OS zeigt.
4. **Mehrfachtest-Warnung:** Meine Checks hier haben mehrere Varianten (MA(1,12), MA(2,12), SMA10, MOM12, Kombinationen) auf denselben Daten verglichen, ohne Korrektur. Fuer das Quant-Lab gilt: **Variante vorab festlegen**, dann Deflated Sharpe/PBO rechnen. Meine Zahlen sind Hinweise, keine Bestaetigung.
5. **Code-Pflicht (Regel 2):** Die fuenf Skripte in `macro_checks/` sind Plausibilitaetschecks (Dateikopf: UNGETESTET). Vor jeder Nutzung im Quant-Lab neu implementieren, Tests schreiben, Look-ahead-Test (Signal darf nur Daten bis t sehen).

## 6. Eigene Rechnungen (UNGETESTET) - Dateien

Pfad `C:\Users\spide\Desktop\Projekte\Quant-Lab\research\families\macro_checks\`:
- `neely_cer.py` (frueher Lauf; Signale aus French-Total-Return-Index)
- `trend_yc.py` (frueher Lauf; Trend + Zinsstruktur auf French-Gesamtmarkt; in diesem Lauf ausgefuehrt)
- `neely_gspc.py` (neu; Signale aus ^GSPC-Preisindex wie im Paper)
- `trend_gspc.py` (neu; Binaerregel mit ^GSPC-Signal)
- `sop_shiller.py` (neu; benoetigt `xlrd` und die Shiller-Datei; Aufruf mit Umgebungsvariable `PYLIB`)

Eingesetzte Daten: French `F-F_Research_Data_Factors_daily` (Cache `data_cache`, ab 1926-07-01), Yahoo `^GSPC` (ab 1927-12-30), `^TNX` (ab 1962-01-02), `^IRX` (ab 1960-01-04), Shiller `ie_data.xls` (Yale, Stand Sep 2023; das ist ein aelterer Stand - neuere Daten liegen auf Shillers aktueller Seite, nicht geprueft). Weitere geprueften Datenstarts (Yahoo): SPY 1993-01-29, VTSMX 1992-04-27, VTI 2001-06-15, ^VIX 1990-01-02, BIL 2007-05-30, SHV 2007-01-11, SHY/IEF/TLT/LQD 2002-07-30, HYG 2007-04-11, EFA 2001-08-27, EWJ 1996-03-18, ^GDAXI 1987-12-30, ^N225 1965-01-05, ^DJI 1992-01-02, ^W5000 1989-01-03. FRED (gratis CSV, ohne Schluessel): T10Y3M ab 1982-01-04, T10Y2Y ab 1976-06-01, BAA10Y ab 1986-01-02, NFCI ab 1971-01-08, USREC ab 1854-12-01, BAMLH0A0HYM2 nur ab 2023-10-10 (gratis nur 3 Jahre -> als Kreditspread-Quelle untauglich, stattdessen BAA10Y).

Hinweis zu Kreditspreads: In diesem Lauf wurde **keine** Kreditspread-Strategie getestet (DFY in Neely Tabelle 4: R2_OS -0,64 %, CER-Gewinn -0,82 % p.a.). Wer sie pruefen will: BAA10Y von FRED, aber ohne Evidenz aus diesem Lauf.

## 7. Quellen (alle tatsaechlich aufgerufen oder in Suchergebnissen gesehen)

Abgerufen und gelesen:
- Neely, Rapach, Tu, Zhou (2010/2013): https://files.stlouisfed.org/files/htdocs/wp/2010/2010-008.pdf
- Ferreira, Santa-Clara (2008 WP): https://www.nber.org/papers/w14571.pdf (Abstract-Seite: https://nber.org/papers/w14571)
- Shu, Yu, Mulvey (2024): https://arxiv.org/abs/2402.05272 und https://arxiv.org/pdf/2402.05272
- Goyal, Welch, Zafirov, Folien Maerz 2023: https://www.ivo-welch.org/research/presentations/99-stanford-prediction.pdf (urspruengliche Adresse ivo-welch.info leitete weiter)
- Gu, Kelly, Xiu (nur Abstract): https://www.nber.org/papers/w25398
- Nystrup (DTU, nur Beschreibung der Masterarbeit): https://www2.imm.dtu.dk/pubdb/pubs/6808-full.html
- Daten: http://www.econ.yale.edu/~shiller/data/ie_data.xls ; https://fred.stlouisfed.org/graph/fredgraph.csv?id=T10Y3M (und weitere IDs wie oben)

Nur in Suchergebnissen gesehen (nicht geoeffnet):
- Goyal, Welch, Zafirov (RFS 37(11), 2024): https://www.sfi.ch/en/publications/a-comprehensive-2022-look-at-the-empirical-performance-of-equity-premium-prediction ; SSRN: https://ssrn.com/abstract=3929119
- Welch, Goyal Original (SSRN): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=517667
- Rapach, Strauss, Zhou (2010): https://academic.oup.com/rfs/article-abstract/23/2/821/1604687
- Nagel (2025): https://www.nber.org/papers/w34104 ; Kelly, Malamud, Zhou: https://nber.org/papers/w30217
- Regime-Literatur: https://mpra.ub.uni-muenchen.de/121552 (Literaturliste, die Nystrup et al. zitiert)
- OUP-Seiten Welch/Goyal und Campbell/Thompson (abgeschnitten, nichts verwertbar): https://academic.oup.com/rfs/article/21/4/1455/1565737 , https://academic.oup.com/rfs/article/21/4/1509/1567813
