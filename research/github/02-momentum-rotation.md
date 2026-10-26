# GitHub-Recherche: Momentum-Rotation und Dual Momentum

Stand: 2026-10-21. Nur lesend recherchiert (GitHub-Suche per API, READMEs per raw.githubusercontent). Kein Repo geklont oder ausgeführt. Code wurde nicht übernommen, nur Regeln und Messmethodik bewertet. GitHub-API-Anfragen: 3 Suchen (ohne Token), READMEs ohne API-Limit.

Suchbegriffe: "dual momentum backtest", "time series momentum backtest", "etf rotation momentum". Die Suche nach "momentum turning points" und "zipline momentum" wurde wegen des Anfragenlimits nicht mehr gemacht.

## Ueberblick der Suchtreffer (Auswahl)

| Repo | Sterne | Lizenz (API) | letzter Push | Thema |
|---|---|---|---|---|
| earaya/GEM | 1 | NOASSERTION (keine erkennbare Lizenz) | 2026-10-07 | GEM (Antonacci), Monatsrecommendation |
| mehul532/time-series-momentum-backtester | 1 | MIT | 2026-10-01 | TSMOM SPY, Parameter- und Kostensweep |
| Alesarabandi/Quantitative-Momentum-Strategy-Backtesting | 1 | MIT | 2025-11-04 | Skewness + Dual Momentum, S&P 500 und STOXX 600 |
| JaaasperLiu/robo-advisor | 9 | MIT | 2026-03-20 | TSMOM und Risk Parity, Monatsrebalancing, 8 ETFs |
| ericxuzhesheng/Trading-Crowding-Momentum-Strategy | 1 | MIT | 2026-10-20 | Momentum minus Handelsaktivitaets-Crowding, Konvexoptimierung, 30 Fonds |
| Alpharotationlab/US-ETF-Rotation-Model | 1 | NOASSERTION (keine erkennbare Lizenz) | 2026-05-17 | Top-3-ETF-Rotation, 20-Tage-Momentum, 200-Tage-MA-Filter |

Nicht ausgewertet, nur am Rand gesehen: TheEvidenceDesk/Dual-Momentum-Bot (2 Sterne, keine Lizenz, Marketing-lastige Beschreibung), 627378329/dual-etf-momentum-rotation (1 Stern, MIT, CSI 300 + Gold), dtmx2007-cloud/treasury-rotation-research (1 Stern, keine Lizenz, aber vorregistrierter Test, Wochen-Momentum bei SHY/IEF/TLT, nachpruefen falls Zeit).

---

## 1. earaya/GEM

https://github.com/earaya/GEM

| Eckdaten | Wert |
|---|---|
| Sterne / Lizenz / Push | 1 / keine erkennbare Lizenz (NOASSERTION) / 2026-10-07 |
| Universum | SPY, ACWX (Aktien), BIL (Hurdle), AGG (Defensive) |

**Regel:** Am letzten Handelstag eines Monats werden die 12-Monats-Total-Returns von SPY und ACWX verglichen und der staerkere gewaehlt. Ist dessen Return groesser als BIL, wird er zu 100 % gehalten, sonst AGG zu 100 %. Bei Gleichstand gewinnt SPY, bei Gleichstand mit BIL gewinnt AGG. Das Repo ist ein CLI-Tool, das nur eine Empfehlung ausgibt und nicht handelt. Dividenden werden am Ex-Tag reinvestiert.

**Messqualitaet:** Keine Backtest-Statistik im README (das Tool erzeugt nur Empfehlungen, keine Performance-Simulation). Positiv: Signal nur aus abgeschlossenen Monatsenden, Daten fail-closed, keine Ersatzwerte bei fehlender Historie. Keine Kosten-, Steuer- oder Out-of-Sample-Auswertung. Ausfuehrung am ersten Handelstag nach dem Signal (kein Look-ahead im Signal).

**Uebertragbare Idee:** Keine neue. Das ist Dual Momentum nach Antonacci, bei dem wir schon getestet haben.

**Neu gegenueber unseren Tests?** Nein. Die relative Wahl SPY/ACWX und der Bond-Fallback sind Dual Momentum in der bereits getesteten Form. Nur die Kombination mit einem Monatsend-Trendfilter fuer den Bond-Fallback waere eine Abweichung (siehe Idee A).

---

## 2. mehul532/time-series-momentum-backtester

https://github.com/mehul532/time-series-momentum-backtester

| Eckdaten | Wert |
|---|---|
| Sterne / Lizenz / Push | 1 / MIT / 2026-10-01 |
| Universum | SPY (Basis), spaeter 10 ETFs: SPY, QQQ, IWM, TLT, IEF, GLD, DBC, EFA, EEM, VNQ |

**Regel:** Pro Asset wird die Rendite ueber ein Lookback-Fenster berechnet (Basis 252 Handelstage). Ist sie positiv, wird das Asset gehalten, sonst ist die Position Cash. Im erweiterten Modus kann Cash durch einen Defensiv-Proxy ersetzt werden. Das Signal wird um einen Tag verschoben, bevor es auf die Renditen angewendet wird. Bei Positionswechseln werden Kosten in Basispunkten abgezogen. Im Multi-Asset-Teil wird jedes ETF unabhaengig gefiltert, aktive ETFs erhalten gleiche Gewichte, ohne aktive ETFs ist die Position Cash.

**Messqualitaet:** Positiv: explizite Ein-Tages-Verzoegerung (das Signal des Schlusses darf nicht im selben Schluss verdient werden), Kosten 0/5/10/25 bp, Parameter-Sweep ueber Lookbacks 21/63/126/189/252, Walk-Forward im Code vorgesehen. Schwach: Im README stehen keine Kennzahlen (nur Platzhalter-Grafiken), keine Out-of-Sample-Ergebnisse, Stichprobe 2000-2026 ohne Vorab-Festlegung dokumentiert. Die Ueberanpassungsgefahr im Sweep wird nicht quantifiziert.

**Uebertragbare Idee:** Wenn der Monatsend-Trendfilter fuer SPY auf Cash steht, halte stattdessen IEF (7-10 J. Treasuries), aber nur wenn IEF selbst ueber seinem eigenen 12-Monats-Mittel der Monatsschluesse liegt, sonst Cash. Parameter: Monatsschluss >= Mittel der letzten 12 Monatsschluesse, Kosten 5 bp pro Positionswechsel, Start 2003 (IEF-Historie), Vergleich gegen Cash-Variante und Buy-and-Hold, Auswertung 2003-2012 vs. 2013-2026 getrennt.

**Neu gegenueber unseren Tests?** Teilweise. Der Monatsend-Trendfilter ist getestet. Anleihen als Cash-Ersatz wurden im Dual-Momentum-Kontext getestet, ohne eigenen Trendfilter am Bond-Leg. Die Kombination "Filter am Ersatz-Asset" ist unseres Wissens nicht getestet. Das ist eine Abweichung, kein grosser Sprung.

---

## 3. Alesarabandi/Quantitative-Momentum-Strategy-Backtesting

https://github.com/Alesarabandi/Quantitative-Momentum-Strategy-Backtesting

| Eckdaten | Wert |
|---|---|
| Sterne / Lizenz / Push | 1 / MIT / 2025-11-04 |
| Universum | Aktien: S&P 500 und STOXX 600 (Einzelaktien) |

**Regel:** Zwei Varianten. (a) Skewness-Filter: zuerst nur Aktien mit positiver Renditeschiefe, dann die Top-Momentum-Titel daraus. (b) Dual Momentum: zuerst Zeitreihen-Momentum (Aktie ueber eigenem Ausgangswert bzw. ueber risikofreiem Satz), dann Querschnitts-Momentum nur innerhalb der Gewinner. Die Ergebnisse sind als Notebooks abgelegt, jeweils fuer S&P 500 und STOXX 600.

**Messqualitaet:** Schwach. Keine Angaben zu Transaktionskosten, keine Out-of-Sample-Aufteilung, Rebalancing-Frequenz und Universumszusammensetzung (Survivorship) nicht erklaert. Max. Drawdown -49 % bis -64 % wird im README selbst als Problem genannt. Kennzahlen (Sharpe 0.55 bis 0.95) sind In-Sample-Werte. Positiv: die Hypothese ist klar formuliert.

**Uebertragbare Idee:** Keine direkt verwertbare Regel, da Aktien-Universum und fehlende Kosten. Die Skewness-Vorfilterung waere als Filter auf einem Index-Korb testbar, aber nicht belegt.

**Neu gegenueber unseren Tests?** Nein. Die Dual-Momentum-Variante (TSM dann CSM) ist im Kern unser getestetes Dual Momentum. Der Skewness-Filter ist neu, aber nur auf Einzelaktien getestet und mit hohem Drawdown.

---

## 4. JaaasperLiu/robo-advisor

https://github.com/JaaasperLiu/robo-advisor

| Eckdaten | Wert |
|---|---|
| Sterne / Lizenz / Push | 9 / MIT / 2026-03-20 |
| Universum | 8 ETFs (Asset-Klassen), Monatsdaten 2003-03 bis 2021-11 |

**Regel:** Zeitreihen-Momentum pro ETF mit monatlichem Rebalancing und dynamischer Allokation (Long bzw. Cash je Asset, Gewichte ueber Volatilitaet bzw. Momentum). Vergleich zu Risk Parity (inverse Volatilitaet). Gewichtsobergrenze per Parameter (max_weight 0.25 im Beispiel). Transaktionskosten in Basispunkten (tc_bps).

**Messqualitaet:** Mittel bis gut. Positiv: deterministische Ausfuehrung mit Hash-Protokoll, Walk-Forward mit expandierenden Fenstern, Tests, Disclaimer. Schwach: Die Tabelle zeigt TSMOM mit 8.1 % CAGR, Sharpe 0.86, MaxDD -15.2 %, aber Monats-Turnover 2.03 (= sehr hoch), Kosten muessen separat betrachtet werden; ob die Tabelle netto oder brutto ist, steht nicht eindeutig. Stichprobe 2003-2021 enthaelt die Finanzkrise und die Erholung, aber nur ein Universum.

**Uebertragbare Idee:** Gewichtsdeckel (max_weight) auf dem Korb statt gleicher Gewichte, mit Volatilitaetsgewichtung nur fuer die aktiven Assets. Testbare Regel: Monatsend-Signal je Asset, aktive Assets gewichtet nach 1/Vola(60 Tage), Einzelgewicht max. 25 %, Rest in Cash, Kosten 5 bp pro Umschlag, Auswertung 2003-2012 und 2013-2026 getrennt. Turnover im Blick behalten.

**Neu gegenueber unseren Tests?** Teilweise. Vol-Targeting und Korb-Ansaetze wurden getestet. Die Kombination aus Trend-Signal und Volatilitaetsgewichtung nur fuer aktive Assets mit Gewichtsdeckel ist aus unseren Notizen nicht ersichtlich, duerfte aber eng an den bisherigen Tests liegen.

---

## 5. ericxuzhesheng/Trading-Crowding-Momentum-Strategy

https://github.com/ericxuzhesheng/Trading-Crowding-Momentum-Strategy

| Eckdaten | Wert |
|---|---|
| Sterne / Lizenz / Push | 1 / MIT / 2026-10-20 |
| Universum | 30 Boersengehandelte Fonds (29 ETF, 1 LOF), China-Fokus plus Anleihen, Gold, Rohstoffe, Daten 2018-2026 |

**Regel:** Score je Fonds aus Ranks: +1.0 * Rank(Return 5 Tage) + 1.0 * Rank(Return 20 Tage) - 0.65 * Rank(Crowding) - 0.1 * Rank(Volatilitaet 20 Tage). Crowding = 0.4 * Rank(Turnover-Anomalie 60 Tage) + 0.3 * Rank(Umsatz-Anomalie) + 0.3 * Rank(20-Tage-Return). Signale um einen Tag verzoegert. Portfolio woechentlich ueber konvexe Optimierung: maximiere Alpha minus Risiko (Kovarianz) minus L1-Turnover-Strafe, Gewichte 0 bis 15 %, Summe = Zielexposure. Kein Stop-Loss.

**Messqualitaet:** Gut dokumentiert, mit Einschraenkungen. Positiv: Signal-Lag, Kosten-Sweep 0-10 bp, Zeit-Split (2023-01-01), Konsistenz-Checks fuer Datensprung-Fehler (Fondsanteilsaenderungen), Ablation ohne Crowding-Term. Die eigene Ablation zeigt: Der Crowding-Term hat nur IC 0.013 gegenueber 0.021 ohne Crowding, und die Sharpe-Verbesserung (1.155 vs 1.015) ist nicht als kausal gemeint. Es ist keine echte Out-of-Sample-Pruefung (Zeit-Split im selben Datensatz), keine Parameter-Robustheit-Analyse, und der Optimierer hat mehrere Parameter (750 bp L1, 15 % Cap, 0.65 Crowding-Gewicht), die nicht ausgewiesen gesucht wurden. Sharpe 1.15 ist daher mit Vorsicht zu lesen.

**Uebertragbare Idee:** Handelsaktivitaets-Filter auf Trendsignal. Monatsende: Long nur wenn SPY ueber dem 12-Monats-Mittel (wie bisher) UND die 60-Tage-Anomalie des SPY-Umsatzes (Z-Score gegen 252-Tage-Mittel) kleiner als +1.0 ist, sonst Cash. Test: S&P 500 seit 2000, 5 bp Kosten, Vergleich mit dem reinen Trendfilter, getrennte Auswertung vor und nach 2013. Erwartung: eher Verlust-Reduktion durch Vermeidung ueberhitzter Phasen als Renditegewinn.

**Neu gegenueber unseren Tests?** Ja. Handelsaktivitaet (Umsatz, Turnover) als Filter ist in unseren Tests nicht vorgekommen. Die Ranking-Gewichte und der Optimierer sind aber nicht uebernehmbar, weil die Gewichte im Repo nicht begruendet sind. Nur der Einzelfilter ist testbar.

---

## 6. Alpharotationlab/US-ETF-Rotation-Model

https://github.com/Alpharotationlab/US-ETF-Rotation-Model

| Eckdaten | Wert |
|---|---|
| Sterne / Lizenz / Push | 1 / keine erkennbare Lizenz (NOASSERTION) / 2026-05-17 |
| Universum | Liquide US-ETFs: SPY, QQQ, IWM, GLD, TLT und weitere (Sektoren, Anleihen) |

**Regel:** Alle 5 Handelstage: Ranking der ETFs nach 20-Tage-Momentum. Nur ETFs, deren Kurs ueber dem 200-Tage-MA liegt, kommen in Frage. Top 3 davon werden gehalten, Rest Cash. Kosten 0.10 % je Seite. Kurse ueber yfinance.

**Messqualitaet:** Schwach bis mittel. Positiv: Kosten erwaehnt, Verlustrisiken offen beschrieben (Momentum-Crashes, Ueberanpassung). Schwach: Backtest 2019-2026 nur In-Sample, keine Out-of-Sample-Stufe, kein Parameter-Sweep, Survivorship-Bias vom Autor selbst eingeraeumt. Kennzahlen: Strategie CAGR 16.8 % vs SPY 17.6 %, MaxDD -23.6 % vs -33.7 %, Sharpe 0.94 vs 0.82. Das Jahr 2024 zeigt -20 % Excess-Return gegenueber SPY, also eine stark von Technologie-Rallyes abhaengige Abweichung.

**Uebertragbare Idee:** Trendfilter je Asset statt nur fuer den Markt. Im Korb der 17 Maerkte wird jedes Asset nur gehalten, wenn sein Monatsschluss ueber dem eigenen 10-Monats-Mittel liegt, und die aktiven Assets werden auf hoechstens 3 begrenzt, Auswahl nach 12-Monats-Momentum. Gleichgewichtung der Top 3, Rest Cash. Kosten 10 bp je Umschlag, Auswertung 2000-2026 mit Zeit-Split.

**Neu gegenueber unseren Tests?** Teilweise. Korb-Filter wurden getestet (17 Maerkte, Verlust gedrittelt, ca. 1 Prozentpunkt weniger Rendite). Die Top-3-Auswahl nach Momentum mit Asset-eigenem Filter ist eine andere Selektion und ist unseres Wissens nicht getestet.

---

## Gesamtbewertung

- Keines der Repos liefert eine belegte Verbesserung ueber den Monatsend-Trendfilter. Mehrere sind In-Sample-Demonstrationen.
- Die sauberste Messung (Signal-Lag, Kosten-Sweep, Zeit-Split) hat das Crowding-Repo, dessen eigene Ablation aber nur einen kleinen Effekt zeigt.
- Die Lizenzlage: GEM und Alpharotation haben keine erkennbare Lizenz (nur Ideen-Nennung, kein Code uebernommen).

## Die 3 besten testbaren Ideen

1. **Handelsaktivitaets-Filter (neu):** Long nur wenn SPY-Monatsschluss >= 12-Monats-Mittel UND 60-Tage-Z-Score des SPY-Umsatzes < +1.0 (sonst Cash). Parameter: 5 bp Kosten, S&P 500 seit 2000, Vergleich mit dem reinen Trendfilter, Auswertung getrennt vor/nach 2013. Quelle: ericxuzhesheng/Trading-Crowding-Momentum-Strategy (MIT).
2. **Filter am Cash-Ersatz (teilweise neu):** Wenn SPY-Filter auf Cash steht, halte IEF nur bei eigenem Monatsend-Trend (>= 12-Monats-Mittel), sonst Cash. Parameter: 5 bp Kosten, Start 2003, Vergleich mit Cash-Variante. Quelle: mehul532/time-series-momentum-backtester (MIT), GEM-Fallback-Logik.
3. **Asset-eigener Trendfilter mit Top-3-Auswahl (teilweise neu):** Im 17-Maerkte-Korb nur Assets ueber eigenem 10-Monats-Mittel, davon die 3 mit dem staerksten 12-Monats-Momentum, gleichgewichtet, Rest Cash, 10 bp Kosten, Zeit-Split 2000-2026. Quelle: Alpharotationlab/US-ETF-Rotation-Model (keine Lizenz, nur Idee).

Hinweis: Alle drei sind Ideen aus fremden READMEs, nicht getestet. Vor einer Uebernahme muessen sie mit eigenem Code und unseren Daten neu gemessen werden, inklusive Kosten und Zeit-Split.
