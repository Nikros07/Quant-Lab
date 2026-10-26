# Familie: Anleihen-Duration-Timing (Carry, Momentum, Value auf Staatsanleihen)

Nachrecherche zu einer vom Kritiker gefundenen Luecke. Stand: 2026-10-12. Recherche-Budget: 15 WebSearch/WebFetch-Abrufe + 2 curl-Pruefungen + lokale Textextraktion zweier PDFs.
Rolle in der Liste: Diversifikator zu den Aktien-/Multi-Asset-Familien. Anleihen kamen bisher nur als Beimischung (tactical/riskparity) vor.

## 1. Kurzfazit (ehrlich)

1. Die Literatur stuetzt Duration-Timing auf US-Staatsanleihen nur schwach. Die beste praktische Quelle (Newfound 2017) schreibt selbst: Kein Timing-Modell war ueber die durchschnittliche Positionierung hinaus statistisch signifikant. Ein grosser Teil des "Erfolgs" ist die Durchschnitts-Long-Position im 40-jaehrigen Anleihen-Bullenmarkt.
2. Der robuste Nutzen ist Drawdown-Reduktion und Ersatz von Buy&Hold-Duration in Zinsanstiegsphasen, nicht Alpha. Bei Newfound sinkt der Max-Drawdown von 36,2 % (10J-Excess) auf ca. 10 % (Equal-Weight-Kombination), bei fast gleicher Rendite. Das passt zu Erfolgsfall 2 des Quant-Lab (sicher halten), nicht zu Erfolgsfall 1 (belegter Edge).
3. Die staerksten publizierten Sharpe-Werte (Brooks & Moskowitz: Multi-Style 1,01 live, 1995-2016) stammen aus laenderuebergreifenden, durationsneutralen Long/Short-Portfolios. Das ist mit Gratis-Tagesdaten nicht handelbar. Die US-only-Variante (das, was das Quant-Lab bauen kann) ist der schwaechere Teil der Evidenz.
4. Alle gefundenen Backtests sind brutto (ohne Kosten), In-Sample und enden vor 2019. Echte Out-of-Sample-Nachpublikationsdaten liefert nur der ungetestete Plausibilitaetscheck im Repo (siehe Abschnitt 5): Carry und Kombination waren nach 2018 schwach, 2022 (Zinsschock) hat nur das Trend-Signal geschuetzt.
5. Value (Realzins) ist das datenhungrigste und am wenigsten reproduzierbare Signal (Inflationserwartung). Auf Gratisdaten nur mit Proxys.

## 2. Was wirklich gelesen wurde (Quellen-Status)

| Quelle | URL | Status |
|---|---|---|
| Brooks & Moskowitz, "Yield Curve Premia", NBER-Konferenzentwurf Jul 2017 (67 S.) | https://conference.nber.org/conf_papers/f96333/f96333.pdf | Volltext gelesen (PDF lokal gespeichert, mit pdftotext extrahiert; Definitionen, Tabelle IX, Fussnoten). Journal-Publikation nicht gefunden. |
| Newfound, "Duration Timing with Style Premia" | https://blog.thinknewfound.com/2017/06/duration-timing-style-premia/ | Gelesen. Datum laut Blog-Tag-Seite: 26.06.2017 (Startliste nannte 2019, das ist vermutlich ein Irrtum). |
| Newfound, "Timing Bonds with Value, Momentum, and Carry" | https://blog.thinknewfound.com/2018/01/timing-bonds-value-momentum-carry/ | Gelesen (29.01.2018). Die Quelle hat interne Zahlen-Inkonsistenzen (siehe Abschnitt 8). |
| Newfound, "A Carry-Trend-Hedge Approach to Duration Timing" | https://blog.thinknewfound.com/2018/10/a-carry-trend-hedge-approach-to-duration-timing/ | Gelesen (15.10.2018). Das ist die Vorlage fuer den Plausibilitaetscheck. |
| Sihvonen, "Yield Curve Momentum" (BoF DP 15/2021; Review of Finance 2024, Bd. 28 Nr. 3) | https://publications.bof.fi/items/6697dabe-9863-4b90-9ba2-961f01b12d27 | Nur Abstract-Ebene (BoF-Seite + Suchzusammenfassungen). PDF-Link: https://publications.bof.fi/bitstreams/59ad826f-ae8d-4e0a-b95e-9b82438d7ba1/download (nicht gelesen). Abruf von revfin.org scheiterte (HTTP 425). Handelsregel, Sharpe-Werte, Kosten: NICHT gefunden. |
| Thornton & Valente (2012, RFS 25(10)), "Out-of-Sample Predictions of Bond Excess Returns and Forward Rates: An Asset Allocation Perspective" | https://ideas.repec.org/a/oup/rfinst/v25y2012i10p3141-3168.html ; WP: https://files.stlouisfed.org/files/htdocs/wp/2010/2010-034.pdf | Nur Abstract/Suchzusammenfassung. |
| Hurst, Ooi, Stamelos (AQR, Mai 2015), "Trend Following and Rising Rates" | https://www.aqr.com/-/media/AQR/Documents/Insights/White-Papers/Trend-Following-and-Rising-Rates2023.pdf | Text gelesen (Dateiname sagt 2023, Dokument ist von Mai 2015, Daten bis April 2013). |
| FRED EXPINF10YR (Cleveland Fed, 10-Year Expected Inflation) | https://fred.stlouisfed.org/series/EXPINF10YR | Seite gelesen: monatlich, Prozent, modellbasiert (Zinsen, Inflation, Swaps, Umfragen), letzter Wert Sep 2026 = 2,57 %. Startdatum stand nicht auf der Seite. |

NICHT abgerufen und deshalb NICHT als Paper gefuehrt: Asness/Moskowitz/Pedersen (2013), Moskowitz/Ooi/Pedersen (2012), Baz et al. (2015), Cochrane/Piazzesi (2005), Fama/Bliss (1987), Koijen et al. (2018), Hurst/Ooi/Pedersen "A Century of Evidence on Trend-Following Investing". Zu den letzten beiden gab es nur Suchtreffer-Zusammenfassungen (siehe 4.3).
Nicht gezielt gefunden (Budget): Replikationen/Kritik 2019-2026 speziell zu US-Duration-Timing. Das ist eine offene Luecke dieser Nachrecherche.

Datenzugriff in dieser Sitzung: Die Fed-GSW-Seiten (federalreserve.gov/data/...) lieferten 404, FRED-Direktabrufe per curl scheiterten (Timeout/Reset). Alle FRED-Serien-IDs und Startdaten unten sind daher, ausser wo vermerkt, NICHT in dieser Sitzung verifiziert. Vor der Implementierung ein Download-Smoketest.

## 3. Gemeinsame Konstruktion (fuer alle US-Varianten)

Daten (gratis):
- ^TNX (Yahoo, 10J-Par-Rendite in Prozent): Start 1962-01-02 (aus dem Check-Lauf verifiziert). ^IRX (13-Wochen-Bill, Diskontbasis): Start 1960-01-04 (verifiziert). Der lokale Cache `data_cache/px__idx_TNX.parquet` beginnt erst 1990, fuer 1962+ muss live von Yahoo geladen und die Rohserie lokal abgelegt werden.
- Einheiten-Plausibilitaet: ^TNX hatte historisch Einheitenwechsel (Faktor 10). Beim Laden pruefen: 0 < TNX/100 < 0,20 und Gegenpruefung gegen FRED DGS10 (laut Erinnerung ab 1962-01-02, unverifiziert).
- ETFs (Startdaten aus dem lokalen Cache verifiziert): IEF 2002-07-30, TLT 2002-07-30, SHY 2002-07-30, IEI 2007-01-11, TLH 2007-01-11, SHV 2007-01-11, BIL 2007-05-30, TIP 2003-12-05, AGG 2003-09-29, BWX 2007-10-11.
- Hinweis zur Umsetzbarkeit (nicht verifiziert): US-domizilierte ETFs wie IEF/TLT/SHY sind fuer deutsche Privatanleger bei vielen Brokern wegen fehlendem KID gesperrt. Backtest mit IEF/SHY als Proxy, Realumsetzung ueber UCITS-Aequivalente (7-10J US-Treasury, 1-3J). Deren Historie ist auf Yahoo kuerzer.

Synthetische 10J-Rendite (identisch zum Plausibilitaetscheck, `bonds_curve_checks/curve_signals.py`):
`y_t = TNX_t/100; D(y) = (1-(1+y/2)^-20)/y; R10_t = y_{t-1}/252 - D(y_{t-1})*(y_t - y_{t-1}); Rc_t = IRX_{t-1}/100/252`.
Ohne Roll-down und ohne Konvexitaet; Diskontbasis statt Bond-Equivalent bei IRX. Diese Naeherungen sind klein gegenueber Zinsschocks, aber nicht null. Die Newfound-Indexrenditen (CMT-Index) enthalten Roll. Groessenordnung nicht quantifiziert.

Timing: Signal am Schluss des letzten Handelstags `t_m` des Monats, Handel zum Schluss von `t_m+1`, Position verdient ab Tag `t_m+2` (synthetische Serie hat nur Schlusskurse). ETF-Variante: Eroeffnung `t_m+1` (adjustiert).
Kosten: 5 bp je Einheit Umschichtung `|dw|` (Basis), 20 bp als Stresstest. Newfound/Brooks-Moskowitz rechnen BRUTTO.
Steuer: Abgeltungssteuer auf realisierte Gewinne je Umschichtung mitrechnen (Quant-Lab-Regel 4). Teilfreistellung bei reinen Rentenfonds laut Erinnerung nicht vorhanden, Rechtsstand pruefen.

Methodische Pflicht (aus Newfound 2017 gelernt): Jedes Timing-Signal muss gegen eine STATISCHE Benchmark mit gleicher durchschnittlicher Investitionsquote getestet werden (Newfound nennt das "strategic"). Sonst misst man die Investitionsquote im Bullenmarkt, nicht Timing-Faehigkeit. Dazu Block-Bootstrap des Sharpe-Unterschieds.

## 4. Strategien (nach erwarteter Robustheit sortiert)

### 4.1 `bond_composite_3sig_longonly` — Carry + Trend + Value, long-only, Gewicht 0/1/3..1

Regel: siehe rule_exact im strukturierten Ergebnis. Kern: je Monatsende drei Stimmen (Carry: Terminspread-Perzentil, Trend: 21d- und 252d-EWMA der 10J-Ueberschussrendite, Value: Realzins ueber 3J-EWMA-Anker), `w = Summe der Stimmen / 3`, `w` in 10J (bzw. IEF), `1-w` in Cash (^IRX bzw. BIL/SHY).

Evidenz:
- Newfound Jan 2018 (6/1974-1/2018, brutto, Long/Short ggue. Cash): 10J-Excess 2,0 % p.a., Vol 7,3 %, IR 0,27, MaxDD 36,2 %. Value L/S 2,0 % / 5,0 % / 0,41 / 19,8 %. Momentum L/S 1,9 % / 6,9 % / 0,27 / 20,9 %. Carry L/S 2,5 % / 6,6 % / 0,38 / 20,1 %. Equal Weight 2,3 % / 4,0 % / 0,57 / 10,2 %. ERC-Gewichtung (Schnitt 43 % Value, 27 % Momentum, 30 % Carry): IR 0,59 -> 0,64, MaxDD 10,2 % -> 8,7 %.
- Newfound Jun 2017: Composite-Timing CAGR 4,03 %, Vol 5,26 %, Sharpe 0,77, MaxDD 9,15 % vs. "Composite Strategic" (feste Durchschnittsgewichte) 3,78 % / 4,63 % / 0,82 / 9,71 %. Also: Timing schlaegt die statische Benchmark im Sharpe NICHT.
- Newfound Okt 2018 (1972-2018): Combined L/S (Carry, Momentum, Equity-Momentum-Hedge, Equal Weight) 2,5 % / 4,3 % / Sharpe 0,58; Integrated (Mehrheitsvotum) 3,5 % / 7,1 % / 0,49.
- Kosten: nirgends modelliert. Out-of-Sample: nirgends.

Nachpublikation/Verfall: Siehe Abschnitt 5. Kombination mit Equity-Hedge statt Value (Check, 5 bp): Sharpe 0,40 vs. 0,19 Buy&Hold ueber die Gesamtperiode, MaxDD -10,3 % vs. -28,3 %; ab 2018-11: Sharpe -0,03 vs. -0,26, CAGR 2,6 % vs. 0,4 %; Kalenderjahr 2022: -4,2 % vs. -17,0 %. In Bullenphasen (1982-2007: CAGR 8,2 % vs. 9,6 %; 2008-2021: 2,4 % vs. 3,5 %) hinkt die Kombi bei der Rendite hinterher. Value-Variante: ungetestet.
Charakter: Drawdown-Diversifikator, kein Alpha-Beleg.

### 4.2 `bond_carry_termspread_gate` — Terminspread-Perzentil, long/Cash

Evidenz:
- Newfound Okt 2018: Carry = Spread 10J minus 1J (Perzentil gg. die vorherigen 10 Jahre taeglicher Spreads, oberes 2/3 long, unteres 1/3 short, Handel am ersten Handelstag des Monats). 1972-2018: L/S 2,6 % Rendite, 7,7 % Vol, Sharpe 0,33; Long-Only-Benchmark 2,1 % / 7,6 % / 0,27. Regeldetails zu exakten Cutoffs: "nicht gefunden".
- Newfound Jun 2017: Carry = 5J minus 2J Spread. Timing CAGR 5,47 %, Vol 6,97 %, Sharpe 0,79, MaxDD 12,03 % vs. strategisch 4,71 % / 5,80 % / 0,81 / 12,11 %. Carry-Variante gegen 10J-Langfrist-Durchschnitt: Rendite etwa 200 bp niedriger bei mehr Trades.
- Brooks & Moskowitz: Carry = Rendite minus lokaler 3M-Satz (Terminspread); Rolldown in Fussnote 8 als vernachlaessigbar approximiert. Cross-Section Level: Carry-Koeffizient 0,25 (t = 2,11), multivariat 0,30 (t = 2,64). Live-Sample (JPM GBI, 3/1995-4/2016): Carry-Sharpe "aehnlich dem Value-Sharpe" (Value 0,65), Slope-Carry Sharpe 0,69. Brutto.

Nachpublikation (Check, 5 bp, Long-Only): Sharpe 0,35 vs. 0,19 BH (Gesamt), 0,44 vs. 0,28 (1972-2018), 0,48 vs. 0,42 (2008-2021), aber ab 2018-11 Sharpe -0,41 vs. -0,26 (CAGR 1,0 % vs. 0,4 %). Zinsschock 2022: -7,2 % vs. -17,0 % BH, aber das Signal war Ende 2021 und bis Mitte 2022 noch long (steile Kurve zu Beginn des Zinszyklus). Carry schuetzt NICHT vor Zinserhoehungszyklen.

### 4.3 `bond_trend_dualewma_longflat` — 21d/252d-Trend der 10J-Ueberschussrendite, long/Cash

Evidenz:
- Newfound Okt 2018: Momentum L/S 1,7 % / 6,3 % / Sharpe 0,28 (1963-2018); Long-Only-Benchmark 1,5 % / 7,2 % / 0,21. Einzelvarianten: MOM21 0,19, MOM63 0,25, MOM126 (Quelle: "128") 0,18, MOM252 0,26. MOM63 "in Drawdown seit den fruehen 2000ern".
- Newfound Jan 2018: Momentum (12-1 Monate, 10J vs. 1J) L/S 1,9 % / 6,9 % / 0,27. "Largely flat since early 1990s". Newfound Jun 2017: Timing CAGR 3,62 %, Sharpe 0,50 (strategisch 0,82).
- Brooks & Moskowitz: Momentum (12M-Rendite) in der Cross-Section Level NICHT signifikant; live-Sample Level-Momentum 2,1 % p.a., t = 1,6; Alpha gg. Hauptkomponenten 5,02 % (t = 2,46). Als "Hedge zum Level-Faktor" interpretiert (negativ mit Value korreliert).
- Sihvonen (Review of Finance 2024; Aug 1971-Dez 2019): Monatsrenditen von Treasuries sagen die Rendite des Folgemonats voraus, am staerksten bei kurzen Laufzeiten, kurzlebig (kein Effekt nach dem Folgemonat), handelbar via Futures, Gewinne ueberleben "vernuenftige" Kosten fuer Profis (laut Abstract-Zusammenfassung). Handelsregel/Sharpe/Kosten: nicht gefunden. Konsequenz: ein 1-Monats-Signal auf kurzen Laufzeiten (IEI/SHY) ist eine eigene, ungetestete Hypothese; die Regel dafuer ist eine EIGENE Ableitung, nicht aus dem Paper.
- AQR (Hurst/Ooi/Stamelos 2015): Multi-Asset-TSMOM (Gleichgewicht aus 1-, 3-, 12-Monats-Signal, 67 Maerkte, 10 % Vol-Ziel, netto geschaetzter Transaktionskosten) war in Phasen steigender UND fallender 10J-Renditen positiv (Nov 1945-Apr 2013); Fixed-Income-Trend war im Zinsanstieg 1975-1981 positiv, war in der Fallphase ca. 72 % der Zeit long und im Anstiegszeitraum ca. 50 % der Zeit short. Hypothetische Simulation eines Anbieters mit Eigeninteresse; vor 1980er ohne Futures (Cash-Indizes).
- Aus Suchtreffern (nicht gelesen): Hurst/Ooi/Pedersen "A Century of Evidence" (67 Maerkte, 1880-2016, laut Sekundaerzusammenfassung in jedem Jahrzehnt positiv, ca. 0,4 Sharpe nach 2/20 ueber alle Assets); Berichte ueber stark gesunkene Trend-Sharpes nach 2010 (alle Assets, nicht bondspezifisch). Nicht als Paper gefuehrt.

Nachpublikation (Check, 5 bp, Long/Flat): Sharpe 0,22 vs. 0,19 BH (Gesamt), 0,23 vs. 0,28 (1972-2018), 0,41 vs. 0,56 (1982-2007), 0,21 vs. 0,42 (2008-2021), 0,24 vs. -0,26 (ab 2018-11). Kalenderjahr 2022: +2,0 % (Position Ende 2021 = Cash) vs. -17,0 % BH. Investiert nur ca. 39 % der Zeit. Das Signal ist ein Krisenfilter, kein Renditebringer.

### 4.4 `bond_value_realyield_longflat` — Realzins ueber 3J-Anker, long/Cash

Evidenz:
- Brooks & Moskowitz: Value = Rendite minus maturity-gematchte Konsens-Inflationsprognose (Consensus Economics; nicht gratis). Cross-Section Level: Koeffizient 0,53 (t = 3,56), multivariat 0,50 (t = 3,72); live (1995-2016) Value-Premium 3,8 % p.a., Vol 5,9 %, Sharpe 0,65, t = 3,0, Alpha gg. Long-only-Benchmark 3,0 % (t = 2,3). Value "subsumiert" den Level-Faktor (PC1) und den Cochrane-Piazzesi-Faktor.
- Newfound Jan 2018: Value = 10J-Rendite minus 10J-SPF-Inflationsprognose (Philadelphia Fed; Fallbacks 1J-SPF, dann BIP-Deflator), Abweichung vom 3J-EW-Mittel, zweifach de-trendet, in 12-Monats-Erwartungsrendite umgerechnet, Haltedauer 1 Jahr (52 ueberlappende Portfolios). L/S 2,0 % / 5,0 % / IR 0,41 / MaxDD 19,8 %.
- Newfound Jun 2017: Value-Timing CAGR 5,75 %, Sharpe 0,84 vs. strategisch 4,37 % / 0,81. In Deutschland (10J vs. 2J) scheiterte Value, wenn demeaned. US 1960er-1980er: Value-Drawdown groesser als -25 % von den 1960ern bis Juni 1970. Newfound warnt: Realzins-Signal war meist long, "may lack timing ability". Keine Signifikanz ueber den Durchschnitt hinaus.

Nachpublikation: nicht getestet (Check hatte keine Inflationserwartung im Cache). Die Hauptschwaeche ist der Datenvorlauf: Echtzeit-Inflationserwartungen gratis nur ab EXPINF10YR/SPF/TIPS-Breakeven, davor Proxy.

### 4.5 `bond_xcountry_style_ls_research` — Brooks-Moskowitz-Stil, laenderuebergreifend, duration-neutral (nur Forschungsproxy)

Kurzbeschreibung: Je Monat pro Land Value/Momentum/Carry-Rang, Long/Short ueber Laender ohne Netto-Duration, Komposit mit konstanter Vol-Gewichtung.
Evidenz: Zero-Coupon-Daten 1971-2016 (US: Gurkaynak/Sack/Wright ab 1971-12-31; weitere Laender per Svensson-Kurven, z. B. Japan ab 1985-03-29). Live-JPM-GBI-Sample 3/1995-4/2016: Level-Value Sharpe 0,65; Level-Momentum 2,1 % (t = 1,6); Multi-Style Level Sharpe 1,01, Praemie 3,1 % (t = 4,6), Alpha gg. PCs 6,58 % (t = 4,56). Slope: Value 0,43, Momentum 0,26, Carry 0,69, Multi 0,73. Butterfly Multi-Style: 7,6 % Alpha gg. den PC-Faktoren (t = 3,98). Alles BRUTTO; die Autoren warnen selbst, dass Butterfly wegen Hebel hoehere Kosten verursacht.
Nachpublikation/Verfall: Daten enden 2016; nichts nach 2016 gesehen. Nicht handelbar mit Gratisdaten, nur als Forschungsproxy ueber OECD-Monatsdaten.

## 5. Eigene Befunde aus dem Repo: ungetesteter Plausibilitaetscheck

Quelle: `research/families/bonds_curve_checks/curve_signals.py`, Ausgaben `out_5bp.txt`, `out_20bp.txt`. Selbst als UNGETESTET markiert (nur Plausibilitaet, nicht zur Strategiewahl). Synthetische 10J-Serie (^TNX), Sharpe auf Ueberschuss zu ^IRX, Kosten 5 bp je Umschichtungseinheit. Er setzt die Newfound-Okt-2018-Regeln um und ersetzt Value durch den Equity-Hedge (EQH), weil keine Inflationserwartung im Cache war. Value ist NICHT getestet.

| Serie (5 bp) | Gesamt 1972-2026-10: CAGR / Sharpe / MaxDD | Sharpe 1972-2018 | Sharpe 2008-2021 | Sharpe ab 2018-11 | Kalenderjahr 2022 |
|---|---|---|---|---|---|
| BH10 (10J durchgehend) | 5,69 % / 0,19 / -28,3 % | 0,28 | 0,42 | -0,26 | -17,0 % |
| CARRY_LO | 6,50 % / 0,35 / -16,9 % | 0,44 | 0,48 | -0,41 | -7,2 % |
| MOM_LO | 5,48 % / 0,22 / -14,0 % | 0,23 | 0,21 | 0,24 | +2,0 % |
| EQH_LO | 5,94 % / 0,35 / -13,1 % | 0,44 | 0,30 | 0,06 | -7,4 % |
| COMBO3_LO (Carry+Trend+EQH) | 6,08 % / 0,40 / -10,3 % | 0,47 | 0,42 | -0,03 | -4,2 % |
| COMBO3_LS | 6,68 % / 0,53 / -12,0 % | 0,58 | 0,31 | 0,17 | +2,6 % |
| CARRY_LS | 7,06 % / 0,35 / -25,0 % | 0,43 | 0,37 | -0,16 | +3,2 % |
| MOM_LS | 5,92 % / 0,25 / -18,5 % | 0,26 | 0,11 | 0,18 | +8,5 % |

Lesart:
- Der Check reproduziert die Newfound-Groessenordnung (Carry-L/S Sharpe 0,43 vs. publiziert 0,33; Combined 0,58 vs. publiziert 0,58 im Fenster 1972-2018), aber das ist nur der In-Sample-Teil.
- Die Long-Only-Varianten sind nur ca. 24-59 % der Zeit investiert. Ein Teil des Sharpe-Vorteils ist also reine Investitionsquote und kein Timing. Dieser Punkt ist offen und der wichtigste Test.
- 1972-1981 (Zinsanstieg): Long-Only-Varianten haben Sharpe unter bzw. um null, nur die Long/Short-Varianten (die short Duration gehen) gewinnen. Long-Only kann den Anstieg nur umgehen, nicht ausnutzen.
- Verfall: Ab 2018-11 haben Carry (Sharpe -0,41 LO) und Kombination (-0,03 LO) den Buy&Hold nur durch weniger Verlust geschlagen, nicht durch Gewinn.

## 6. Bewusst nicht aufgenommen

- Cochrane-Piazzesi-/Fama-Bliss-Vorwaertsraten-Faktor als Handelssignal: Thornton & Valente (2012) fanden, dass Forward-Rate-Information einem Mean-Variance-Investor keinen systematischen Mehrwert (kein hoeherer Out-of-Sample-Sharpe ggue. Erwartungshypothese) bringt und die relative Performance im Zeitverlauf nachlaesst (nur Abstract-Ebene gesehen). Eine Brandeis-Arbeit widerspricht (Drei-Faktor-Modell mit Makrofaktor), nicht gelesen. Daten (Fama-Bliss unsmoothed, CRSP) nicht gratis; Fed-GSW-Seite lieferte 404.
- BRP-Variante (10J-Rendite minus erwartete durchschnittliche 1J-Rate ueber das Jahrzehnt, SPF): Newfound Jun 2017 Timing CAGR 3,89 %, Sharpe 0,71 vs. strategisch 0,82. Redundant zu Value.
- 1-Monats-Treasury-Momentum nach Sihvonen als eigener Eintrag: Regel nicht gesehen, daher nur als Variante in 4.3.

## 7. Vorschlag fuer `docs/HYPOTHESEN.md` (vor jedem Test eintragen)

- H-Bond-1 (Composite long-only): Erwartung: MaxDD <= 60 % des 10J-Buy&Hold, Sharpe(Ueberschuss zu Cash) nach 5 bp mindestens gleich Buy&Hold und mindestens gleich der statischen Benchmark mit gleicher Durchschnittsquote. Abbruch: Wenn der Sharpe-Vorsprung gegen die statische Benchmark im Block-Bootstrap nicht signifikant ist (p > 0,10) oder in einem der Fenster 1972-81 / 1982-2007 / 2008-2021 / 2022+ der MaxDD schlechter als Buy&Hold ist -> als reiner Drawdown-Filter klassifizieren, kein Edge.
- H-Bond-2 (Carry): Erwartung: schwach positiv. Abbruch: ab 2018-11 weiter schlechter als Buy&Hold und 2022-Verlust > 50 % des Buy&Hold-Verlusts.
- H-Bond-3 (Trend): Erwartung: Krisenfilter, Sharpe ~ Buy&Hold, Vorteil im Zinsanstieg. Abbruch: Verlust im Zinsanstieg 1972-81 > Buy&Hold oder Umschlag > 6 Einheiten/Jahr bei 20 bp Kosten.
- H-Bond-4 (Value): Erwartung: unsicher. Zuerst nur mit CPI-Proxy 1965+ testen, EXPINF10YR-Variante (ab Verfuegbarkeit) nur zur Robustheit.
- Varianten (EQH statt Value, L/S-Version, Perzentil-Schwellen) nur als eigene, vorab registrierte Hypothesen und NICHT auf denselben Daten auswaehlen UND bestaetigen.
- Mehrfachtest: 4-5 Familienvarianten zaehlen mit Deflated Sharpe / PBO.

## 8. Offene Punkte / Unsicherheiten

- Replikation/Kritik 2019-2026 nicht gezielt gefunden.
- Sihvonen: konkrete Handelsregel und Kosten nicht gelesen.
- FRED-IDs/Startdaten unverifiziert (DGS10, DTB3, GS10, GS1, TB3MS, T10Y3M, T10YIE, DFII10, CPIAUCNS, OECD-Laenderreihen IRLTLT01{CC}M156N / IR3TIB01{CC}M156N); EXPINF10YR existiert (Seite gelesen), Start unverifiziert.
- Philly-Fed SPF 10J-CPI-Erwartung (Newfound-Quelle): Startdatum nicht verifiziert (Erinnerung: 1991).
- Newfound-Zahlen enthalten Quell-Inkonsistenzen (Buy&Hold-MaxDD 36,2 % vs. 45,7 %; Momentum-Rendite 1,9 % vs. 1,7 %; Equal-Weight-Vol 4,0 % vs. 4,2 %). Sie sind als grobe Groessenordnung zu lesen.
