# Audit-Übersicht der 11 bisher ungeprüften Strategie-Familien (2026-10-21)

Vorgehen: Sonnet hat den Auftrag (`AUDIT-AUFTRAG.md`) geschrieben und die Ergebnisse gegengelesen, je Familie ein Haiku-Agent hat nur lesend geprüft (Spezifikation gegen Code, Look-ahead-Suche, Engine-Vertrag, Handrechnung auf synthetischen Daten, Tests, Lauf mit Kausalitätstest bis 2022-12-31). Der Holdout ab 2023 blieb zu. Die Kennzahlen der Berichte habe ich gegen die erzeugten `results/summary_audit_*.csv` stichprobenartig abgeglichen (tom_etf, crypto, svxy, putwrite, ivp, xtsmom, commodity: stimmen). Handrechnungen und Befunde im Einzelnen habe ich nicht nachgerechnet, nur Stichproben im Code gelesen (Kalender, IBS-Ausführung).

Alle Zahlen: bis 2022-12-31, nach Kosten, vor Steuer, Ausführung Eröffnung Folgetag, wenn nicht anders vermerkt.

| Familie | Urteil (Haiku) | Befunde hoch/mittel/niedrig | CAGR | Sharpe | MaxDD | Einordnung |
|---|---|---|---|---|---|---|
| index_etf_ibs_rsi2_longonly | DURCHGEFALLEN* | 1/2/2 | 6,9 % (open) / 5,4 % (Folgeschluss laut Spec) | 0,64 / 0,45 | −15,6 % / −11,4 % | Code korrekt. Der "hohe" Befund betrifft nur die Auswertung: Harness-Standard ist Eröffnung, Spec verlangt Folgeschluss. Spec-konform Sharpe = SPY (0,46). Kein Vorteil, kleiner Drawdown. |
| tom_spy_m2_p3 (+_etf) | bestanden mit Hinweisen | 0/3/3 | 8,9 % / ETF 4,8 % | 0,80 / ETF 0,35 | −23,2 % / −17,7 % | Der Effekt liegt vor 1993 (Sharpe 1,03), danach 0,37, ab 2004 0,25. Kein heutiger Vorteil. |
| halloween_nov_apr_equity (+_etf) | bestanden mit Hinweisen | 0/1/7 | 8,3 % / SPY 7,5 % | 0,48 / 0,45 | −58,8 % / −34,6 % | SPY-Buy&Hold hat Sharpe 0,46: kein Vorteil. DAX-Variante nur als Kursindex. |
| lowvol_defensive_longonly (+_etf) | bestanden mit Hinweisen | 0/2/5 | 10,4 % | 0,51 | −43,4 % | Abbruchkriterium auf Faktor-Ebene erreicht (Alpha-t 1,14 < 1,65). USMV 2011–22: Sharpe 0,81 gegen SPY 0,76, nach Steuer unter SPY. |
| xtsmom_us_switch_longcash (+_etf) | bestanden mit Hinweisen | 0/1/5 | 10,3 % / ETF 6,4 % | 0,59 / ETF 0,46 | −33,8 % / −33,7 % | ETF-Version: Δ Sharpe gegen SPY −0,04. Kein Vorteil. |
| bond_composite_3sig_longonly (+_etf) | bestanden mit Hinweisen | 0/1/4 | 5,9 % / ETF 3,0 % | 0,39 / ETF 0,49 | −9,7 % / −8,7 % | Synthetische Anleiherendite weicht vom IEF ab (Korrelation 0,95, Mittel 2,7 % statt 3,6 %). Defensiv, nach Steuer Sharpe 0,18. |
| commodity_gold_trend_dbc_gld | bestanden mit Hinweisen | 0/2/6 | 4,4 % | 0,36 | −28,3 % | 16 Jahre, Sharpe-Differenz zu SPY −0,10 (90-%-KI −0,62…+0,30): keine Aussage möglich, kein Vorteil sichtbar. |
| crypto_trend_ens_btc_eth | bestanden mit Hinweisen | 0/4/4 | 66,7 % | 1,41 | −46,6 % | Nur 7,3 Jahre, in-sample. BTC Buy&Hold: 79,4 % CAGR, Sharpe 1,15, MaxDD −83,4 %. Bei 2,5-fachen Kosten Sharpe 1,30. Nutzen vor allem Drawdown. |
| ivp_risk_parity_unlevered | bestanden mit Hinweisen | 0/2/5 | 3,7 % | 0,45 | −19,8 % | SPY im Fenster: 9,3 %, Sharpe 0,51. 1/N-Kontrolle fehlt im Harness; Sharpe-Vorsprung gegen 1/N 0,09. |
| putwrite_vrp_index | bestanden mit Hinweisen | 0/5/3 | 7,3 % | 0,40 | −37,4 % | SPY im Fenster 0,42. Alpha gegen beta-gematchten Mix t = 0,97 (Schwelle 1,65): nur Aktien-Beta mit Tail-Risiko. |
| svxy_term_structure_filter | bestanden mit Hinweisen | 0/3/5 | 31,5 % | 0,80 | −56,9 % | Rendite stammt aus dem alten −1x-Regime (50,2 % gegen 10,3 % im −0,5x-Regime). Δ Sharpe gegen SPY 0,00 (p = 0,48). 2018-Crash lag zufällig in Cash. |

*Urteil des Agenten wörtlich; meine Lesart: Strategie-Code in Ordnung, Auswertungsreferenz muss beide Ausführungsarten zeigen.

## Gesamtbefund
- **Kein Look-ahead im Code, kein Kausalitätsfehler, keine falsche Regel, kein verstecktes Hebeln** in den 11 Familien (alle Handrechnungen stimmen mit den Modulen überein, 0 hohe Befunde im Strategiecode).
- **Kein belegter Rendite- oder Sharpe-Vorteil gegenüber Buy&Hold.** Die hohen Sharpe-Werte (TOM 0,80, SVXY 0,80, Krypto 1,41) entstehen aus einem Regime, das nicht mehr gilt (vor 1993, −1x-Hebel vor 2018) oder aus 7 Jahren Stichprobe. Wo der Filter nützt, ist es der Drawdown.
- Die Auswahl der Strategie bleibt damit beim Trendfilter MA12 (halber Drawdown, Rendite ≈ Markt).

## Schwächen des Prüfstands (aus den Audits, noch nicht behoben)
1. **(teilweise behoben durch den Gesamtlauf `audited_all`, 107 Läufe)** **Deflated Sharpe zählt nur die Läufe eines Aufrufs** (2–4 statt aller Projektversuche): bei Einzel-`--ids`-Läufen unbrauchbar hoch (1,000). Nur der Sammellauf `audited` mit allen 54 Läufen ist belastbar.
2. **Abbruchkriterien der Spezifikationen werden vom Harness nicht berechnet** (exposure-gematchte Zufalls-Einstiege, 1/N-Kontrolle, beta-gematchter Mix, Alpha-t). Einige wurden in den Audits ad hoc nachgerechnet (siehe Berichte).
3. **Ausführungsart:** Harness-Standard `open`; Spezifikationen verlangen teils Folgeschluss. Beide Läufe ausweisen.
4. **Kalender vor 1990:** Feiertage sind erst ab 1990 hinterlegt, Samstagshandel vor 1952 ist nicht modelliert. Die Monatsend-Flags innerhalb der Daten kommen aus dem Datenindex (nur Datumsinformation, kein Kurs); der Kausalitätstest ist für Daten vor 1990 nicht aussagekräftig (11 von 144 dichten Schnitten 1955–57 schlugen fehl, Vollstichprobe unberührt; 0 Verstöße bei 782 dichten Schnitten 1990–2022).
5. **Engine:** nach einem vollen Kauf mit `close_next` liegt das Gewicht kostenbedingt bei 1,001 (kleiner, ungewollter Hebel).
6. **Berichts-Kopfzeilen** zeigen die SPY-Kennzahlen der Vollperiode, auch wenn das Strategiefenster kürzer ist.
7. **Schwache Tests** (Disjunktionen, die immer wahr sind) in `test_halloween_nov_apr_equity.py` und einigen anderen; `halloween_nov_apr_equity_etf` hat keine eigene Testdatei.

Einzelberichte: `docs/audits/<id>.md`. Wegwerf-Skripte und Logs: `docs/audits/_tmp/`.
