# Familie: Cross-sectional Momentum / Sektor- und Industrie-Rotation

Stand: 2026-10-11. Recherche-Notizen, keine Backtests (Regel 3 im Projekt: erst Hypothese in `docs/HYPOTHESEN.md`, dann testen).
Alle Zahlen unten stammen aus Dokumenten, die in dieser Session wirklich abgerufen wurden. Wo nur eine Suchtreffer-Zusammenfassung vorlag, steht das dabei. Was ich nicht gefunden habe, steht als "nicht gefunden".

## 0. Kurzfazit (ehrlich)

1. Die Momentum-Prämie auf Aktienebene ist über sehr lange Zeit und viele Märkte dokumentiert (Daniel/Moskowitz: 1927-2013 US, dazu Europa, Japan, UK, Index-Futures, Rohstoffe, Währungen). Sie ist aber crash-anfällig (monatliche Schiefe -4,70 für den Long-Short, 1927-2013) und kostenempfindlich.
2. Der Teil der Evidenz, der mit Gratis-Daten wirklich **handelbar** nachprüfbar ist, ist klein: Aktien-Dezile gibt es gratis nur als Ken-French-Renditereihen (nicht handelbar, ohne Kosten, ohne Leerverkaufskosten). Handelbar mit Gratis-Daten sind nur ETF-Rotationen (US-Sektoren ab 1998-12, Länder-ETFs ab 1996-03). Die haben wenig Historie und wenige, stark korrelierte Titel.
3. Die einzige Verbesserung, die über Märkte und Zeiträume hinweg konsistent auftaucht, ist **Volatilitäts-Skalierung** des Momentum (Barroso/Santa-Clara; Daniel/Moskowitz). Sie ist ex ante umsetzbar (nur vergangene 126 Handelstage).
4. Industrie-Momentum (Moskowitz/Grinblatt) auf Aktienebene ist nach Kosten tot: Novy-Marx/Velikov rechnen brutto +0,93 %/Monat, Kosten 1,22 %/Monat, netto -0,29 %/Monat (t = -1,20). Auf ETF-Ebene sind die Kosten viel kleiner, aber das ist nicht belegt.
5. Das Daniel/Moskowitz-"dynamische" Verfahren ist in der Stichprobe gefittet (GARCH und Regression über die Vollstichprobe). Der Zugewinn gegenüber der einfachen Vol-Skalierung ist daher der am wenigsten robuste Teil.
6. Meine Einschätzung (nicht belegt): Für Nicks Ziel "Vorteil nach Kosten und Steuern" ist die Erwartung für Strategie 2 und 3 niedrig. Sie sind long-only fast Markt-Beta, und Nicks eigene ETF-v4-Messung (verliert gegen S&P-500-Buy&Hold) zeigt in dieselbe Richtung.

## 1. Rangliste (beste Erwartung zuerst)

| # | id | Kurzbeschreibung | Handelbar gratis? | Komplexität | Erwartete Robustheit |
|---|----|------------------|-------------------|-------------|----------------------|
| 1 | `wml_volscaled_ff` | US-Aktien-Momentum (Long-Short-Dezile), Positionsgröße = 12 % / realisierte 126-Tage-Vol | Nur als Messlatte (French-Renditen), kein Handel | 2 | Evidenz hoch, Handelbarkeit null |
| 2 | `sector_etf_top3_12m` | Faber: 3 beste von 9 SPDR-Sektor-ETFs nach 12-Monats-Rendite, gleichgewichtet, monatlich | Ja (ETFs, 1998-12) | 1 | mittel bis niedrig |
| 3 | `country_etf_xsmom_12_1` | Länder-ETF-Momentum, 17 iShares-Länder-ETFs, Rang-Gewichte | Ja (ETFs, 1996-03) | 2 | niedrig |
| 4 | `wml_dynamic_dm_expanding` | Daniel/Moskowitz dynamisch, aber mit wachsendem Fenster statt Vollstichprobe | Nur Messlatte | 5 | niedrig (In-Sample-Verdacht) |
| 5 | `industry_mom_ff17_ls` | Moskowitz/Grinblatt Industrie-Momentum Long-Short auf French-17-Industrien | Nur Messlatte | 2 | sehr niedrig (Kosten) |

Hinweis zur Reihenfolge: Platz 1 hat die stärkste Evidenz, ist aber kein Handelssystem. Wenn nur handelbare Kandidaten zählen, ist Platz 2 der erste.

## 2. Prüfstatus der Quellen (was ich wirklich gesehen habe)

| Quelle | Status |
|--------|--------|
| Daniel/Moskowitz, Momentum Crashes (PDF Columbia) | Volltext abgerufen und lokal mit pdftotext gelesen. Zahlen sind belastbar. Spaltenzuordnung der Tabelle 10 aus dem Textlayout rekonstruiert (siehe 3.3). |
| Novy-Marx/Velikov, Taxonomy of Anomalies (NBER-PDF) | Volltext abgerufen und lokal gelesen. Tabellenspalten teils vertauscht im Textlayout, ich habe Brutto minus Kosten gleich Netto nachgerechnet (stimmt für alle gelesenen Zeilen). |
| Faber, Relative Strength Strategies (PDF) | Volltext (Text) gelesen. Die Kennzahlen-Tabellen sind Bilder und waren nicht lesbar. Kennzahlen über die Quantpedia-Seite. |
| Quantpedia, Sector Momentum Rotational System | Seite abgerufen (Regeln, Kennzahlen aus Faber Exhibit 4.5). |
| Barroso/Santa-Clara, Momentum has its moments | Nur Abstract (Uni-Portugal-Repository) abgerufen. Keine Zahlen im Abstract. Weitere Angaben aus einer Suchtreffer-Zusammenfassung (sekundär). |
| Moskowitz/Grinblatt 1999 | Nur Abstract über IDEAS/RePEc-Suchtreffer. Volltext nicht gesehen. |
| Asness/Moskowitz/Pedersen 2013 | Nur Abstract über Suchtreffer. Volltext nicht abgerufen. |
| Geczy/Samonov 2016 | Nur Abstract über Suchtreffer (Volltext hinter Paywall). |
| Arnott/Clements/Kalesnik/Linnainmaa 2018 | Nur Abstract-Zusammenfassung über Suchtreffer. Veröffentlichte Fassung nicht gefunden. |
| Jegadeesh/Titman 2023 (30 Jahre danach) | Nur Existenz und Abstract-Thema über Suchtreffer. Keine Zahlen gefunden. |
| McLean/Pontiff, Chen/Zimmermann | Nur sekundäre Suchtreffer-Zusammenfassungen. Nicht im Original geprüft. |
| Ken French Data Library | Seite abgerufen (Datensatznamen und CSV-Dateinamen). Startdaten stehen dort nicht. |
| Alpha-Architect-Seite "30 years of out of sample data" | Abruf scheiterte (HTTP 403). Nichts daraus verwendet. |

Nicht bearbeitet (Budget): Residual-Momentum (Blitz et al.), 52-Wochen-Hoch-Momentum, Momentum nach Aktienuniversum-Qualität, Jegadeesh/Titman 1993 im Original, Rouwenhorst Länder-/Schwellenländer-Momentum, Allocate-Smartly-Backtests. Jegadeesh/Titman 2001 und Israel/Moskowitz 2013 sind nur über Daniel/Moskowitz zitiert (Aussage dort: Momentum bestand 1990-1998 und 1927-1965 sowie 1990-2012).

Aufwand: 17 Web-Abrufe (Suchen und Seiten), einer davon fehlgeschlagen. Zusätzlich lokale Kontrolle der Yahoo-Datenstarts mit dem Projekt-`.venv` (nur Metadaten, keine Performance).

## 3. Strategien im Detail

### 3.1 `wml_volscaled_ff` — Volatilitäts-skaliertes US-Aktien-Momentum (Messlatte)

**Quelle**: Barroso/Santa-Clara (JFE 2015, "Momentum has its moments"); Daniel/Moskowitz (JFE 2016) bauen dasselbe als "cvol" nach (126 Tage Tagesrenditen, Vol-Ziel 19 % statt 12 %; bei reiner Skalierung ändert das Ziel die Sharpe-Ratio nicht).

**Regel (unzweideutig)**
```
DATEN (Ken French, täglich, VW-Block der Datei):
  R_hi[d] = Tagesrendite Portfolio "Hi PRIOR"  (10_Portfolios_Prior_12_2_Daily)
  R_lo[d] = Tagesrendite Portfolio "Lo PRIOR"
  WML[d]  = R_hi[d] - R_lo[d]                  # in Dezimal, nicht Prozent
  RF[d]   = Tages-Risikofreier aus F-F_Research_Data_Factors_daily

SIGNALTAG t = letzter NYSE-Handelstag jedes Monats (qlab.calendar), nur Daten <= t:
  sigma = stdev(WML[t-125 .. t], ddof=1) * sqrt(252)      # 126 Handelstage
  w     = min(0.12 / sigma, 2.0)                           # Ziel 12 % p.a.; Deckel 2.0 ist MEINE Schutzgrenze, nicht aus dem Paper

POSITION: ab Handelstag t+1 bis einschließlich nächstem Signaltag:
  +w auf "Hi PRIOR", -w auf "Lo PRIOR", Rest zu RF. Gewichte innerhalb des Monats konstant.
  Tagesrendite der Strategie = w * WML[d] + RF[d]   (Einsatz-neutral, Überschussrendite w*WML)

KONTROLLEN (Pflicht): (a) statisch w = 1;  (b) Ziel 19 % (Daniel/Moskowitz-Variante);
  (c) Zufalls-Skalierung: w aus permutierten Monaten, gleiche Verteilung.
```
Die French-Dezile bilden 12-2 (Rang nach Rendite von t-12 bis t-2, ein Monat Lücke, monatlich neu gebildet, NYSE-Breakpoints laut Beschreibung bei Novy-Marx/Velikov; bei Daniel/Moskowitz eigene CRSP-Konstruktion mit gleicher Rangbildung).

**Daten gratis**: `10_Portfolios_Prior_12_2_Daily_CSV.zip`, `10_Portfolios_Prior_12_2_CSV.zip`, Kontrolle `F-F_Momentum_Factor_daily_CSV.zip`, `F-F_Research_Data_Factors_daily_CSV.zip` (Dateinamen von der French-Seite). Startdatum in dieser Session **nicht geprüft** (Daniel/Moskowitz-Stichprobe beginnt 1927:01, French-Reihen vermutlich ähnlich). Spaltennamen "Lo PRIOR" und "Hi PRIOR" sind aus Erinnerung, beim Laden prüfen. Nicht handelbar: Renditereihen, keine Kosten, keine Leerverkaufskosten.

**Evidenz**
- Daniel/Moskowitz Tabelle 1 (1927:01-2013:03, monatliche VW-Dezile): Long-Short WML Überschussrendite 17,9 %/Jahr, Vol 30,0 %, Sharpe 0,60 (Tabellenzeile; im Fließtext steht 0,71, Widerspruch im Paper), CAPM-Beta -0,58, Schiefe monatlich -4,70, täglich -1,18. Gewinner-Dezil 15,3 %, Verlierer-Dezil -2,5 % pro Jahr.
- Daniel/Moskowitz Tabelle 10, Sharpe statisch -> cvol (Tagesrenditen, 126 Tage), jeweils bis 05/2013: US ab 07/72: 0,283 -> 0,519; UK ab 06/90: 0,465 -> 0,751; Europa ab 06/90: 0,462 -> 0,886; Japan ab 06/90: 0,067 -> 0,160. Anleihen (kein Effekt): 0,004 -> 0,020.
- Barroso/Santa-Clara (Abstract): Risikomanagement "verdoppelt fast" die Sharpe-Ratio und beseitigt die Crashes praktisch. Stichprobe laut Suchtreffer 1927-2011. Weitere Zahlen (16,5 % vs 14,5 % Rendite, Ziel 12 %) stammen nur aus einem Sekundärkommentar, nicht geprüft.
- Geczy/Samonov (Abstract): Momentum-Gewinne vor 1927 (Daten ab 1801) sind positiv und signifikant. Ein dynamisch abgesichertes Momentum schlägt das nicht abgesicherte.

**Nachpublikations-Verfall, Kosten, Tail-Risiko**
- Die Vol-Skalierung ist ex ante (nur vergangene Vol), aber das Vol-Ziel und der 126-Tage-Horizont sind Wahl der Autoren. Dass die Verbesserung in allen Märkten mit dem gleichen Fenster auftritt, spricht für Robustheit. Eine unabhängige Nachprüfung mit neueren Daten habe ich nicht gefunden (nur ein Blog-Test laut Suchtreffer, nicht geprüft).
- Die US-Spalte ab 1972 (Sharpe 0,28) ist niedriger als die Vollstichprobe 1927-2013 (0,60). Die Konstruktionen sind nicht identisch (AMP-Daten vs. CRSP-Dezile), der Vergleich ist nur ein Hinweis, dass die Prämie in der jüngeren Zeit kleiner ist.
- Kosten (Novy-Marx/Velikov, VW-Dezile, NYSE-Breakpoints, 1963-2013, effektive Spreads nach Hasbrouck-Gibbs-Schätzer, ohne Preiswirkung): Momentum brutto 1,33 %/Monat (t = 4,80), Turnover-Spalte 34,52, Kosten 0,65 %/Monat, netto 0,68 %/Monat (t = 2,45). Das ist Mittel über 1963-2013; heutige Spreads sind kleiner, die Kosten der kleinen Verlierer-Aktien (und deren Leihegebühr, hier nicht enthalten) bleiben der kritische Punkt. Die Engine-Voreinstellung von 5 bps pro Seite unterschätzt diese Strategie um ein Vielfaches. Praktische Näherung: 0,65 %/Monat mal mittleres w.
- Tail: Momentum-Crashes sind "Verlierer crashen nach oben". Beispiel Juli/August 1932: Markt +82 %, Gewinner-Dezil +32 %, Verlierer-Dezil +232 %. März bis Mai 2009: Markt +26 %, Verlierer-Dezil +163 %. 14 der 15 schlechtesten Momentum-Monate fallen in Phasen mit negativer 2-Jahres-Marktrendite, alle in Monaten mit steigendem Markt. Vol-Skalierung reagiert mit Verzögerung (126 Tage), sie dämpft, verhindert aber nicht jeden Sprung.

**Prüfplan (Vorschlag)**: Erwartung: Sharpe der Skalierung größer als statisch in mindestens 3 von 4 Teilperioden (1927-49, 50-74, 75-99, 2000-2022); Abbruch, wenn die Verbesserung in 2000-2022 verschwindet oder die Strategie nach 0,65 %/Monat mal w Kosten Sharpe unter 0,3 liegt. Varianten: höchstens 2 (Ziel 12 %, Ziel 19 % nur Kontrolle).

### 3.2 `sector_etf_top3_12m` — Faber-Sektor-Rotation (handelbar)

**Quelle**: Faber, "Relative Strength Strategies for Investing" (SSRN 1585517, April 2010, erste Fassung). Verwandt: Moskowitz/Grinblatt 1999.

**Regel (unzweideutig)**
```
UNIVERSUM (fest, 9): XLB XLE XLF XLI XLK XLP XLU XLV XLY    # Yahoo auto_adjust (Total Return)
  (XLRE ab 2015-10, XLC ab 2018-06 NICHT aufnehmen, damit das Universum konstant bleibt)

SIGNALTAG t = letzter NYSE-Handelstag des Monats (qlab.calendar), nur Daten <= t:
  score_i = AdjClose_i[t] / AdjClose_i[t12] - 1
            mit t12 = letzter Handelstag des Monats, der 12 Monate vor dem Monat von t liegt
  Rang absteigend nach score, Gleichstand: alphabetisch nach Ticker
  erstes gültiges Signal: 1999-12-31 (t12 = 1998-12-31, XL-Daten ab 1998-12-22)

ZIEL: Top 3 je 1/3, übrige 0. Vollinvestiert, kein Hebel, keine Leerverkäufe, kein Cash-Filter in der Basis.
AUSFÜHRUNG: Order zur Eröffnung des Handelstags t+1, Halten bis zum nächsten Signaltag. Rebalancing monatlich.
KOSTEN: qlab-Standard 5 bps pro Seite; Stresstest 25 bps. (Faber: 1 % Round-trip wäre noch profitabel, nur Behauptung.)

VORAB FESTGELEGTE VARIANTEN (max. 3, zählen als Versuche):
  combo       : score = Mittel der Renditen über 1, 3, 6, 9, 12 Monate (Fabers "Kombination")
  sma10       : Basis-Signal, aber alles in Cash (RF), wenn SPY[t] < Mittel der letzten 10 Monatsend-Schlusskurse von SPY (inkl. t)
  hold_buffer : Basis, aber ein gehaltener ETF bleibt, solange sein Rang <= 5; auffüllen bis 3 mit den bestplatzierten

PFLICHT-VERGLEICHE: SPY Buy&Hold; Gleichgewicht über die 9 ETFs, monatlich rebalanciert; Zufalls-Top-3 (Permutationstest).
LANGZEIT-CHECK (nur Signalprüfung, nicht handelbar): French 10 oder 17 Industry Portfolios, monatlich, VW, ab 1926-07
  (Faber-Anhang für die 10er-Version), gleiche Regel, Gewichte aus Monatsende t wirken auf die Rendite von Monat t+1.
```

**Daten gratis (Yahoo-Start in dieser Session per yfinance geprüft)**: XLB XLE XLF XLI XLK XLP XLU XLV XLY alle ab 1998-12-22; XLRE 2015-10-08; XLC 2018-06-19; SPY 1993-01-29; Quervergleich Vanguard-Sektoren VGT VHT VFH VCR VDC VAW VPU ab 2004-01-30, VDE VIS VOX VNQ ab 2004-09-29; BIL ab 2007-05-30. Besser als BIL für Cash: French-RF.

**Evidenz**
- Faber (10 French-Industrien, VW, Monatsdaten 1928-2009, Rangbildung auf Gesamtrendite inkl. Dividenden, alles zum Schlusskurs des Signaltags, ohne Steuern, Gebühren, Slippage): Die Relative-Stärke-Portfolios schlagen Buy&Hold in rund 70 % der Jahre; Faber schätzt 300-600 Basispunkte Mehrrendite pro Jahr. Quantpedia nennt für Exhibit 4.5 (12-Monats-Rang, Top 3): CAGR 13,94 %, Vol 18,38 %, maximaler Drawdown -46,29 %, Sharpe 0,54. Buy&Hold-Vergleichszahlen: nicht gefunden (Tabellen im PDF sind Bilder).
- Faber: Long-only und voll investiert, daher Aktienrisiko voll da; Drawdowns 70-80 % ohne Filter; mit 10-Monats-SMA-Filter auf den S&P 500 (Cash bei Unterschreitung) etwa 40-50 % Drawdown, Rendite weitgehend erhalten (Top 1 verliert etwa 150 bp). Mit Sell-Filter (kaufe Top 3, verkaufe erst bei Rang unter 5) bleibt der Umschlag unter 100 %. Fabers Steuerhinweis: Anstieg des Umschlags von 5-20 % auf 70-100 % kostet etwa 50-150 bp Steuer.
- Faber nennt selbst eine Schwäche: Telecom und Health hatten bis in die 1950er weniger als 20 Firmen.

**Nachpublikations-Verfall und Kosten**
- Das Paper endet 2009. Neuere Out-of-Sample-Zahlen für 9 SPDR-ETFs habe ich nicht gefunden. Die ETF-Historie (1998-12 bis 2022) ist ein knapper Datensatz: 9 Titel, hohe Korrelation, wenige unabhängige Sektor-Zyklen (Technologie 1999/2000, Energie 2005-08, Technologie ab 2010).
- Arnott et al. (Abstract-Ebene): Industrie-Momentum stamme aus Faktor-Momentum, weil Industrien unterschiedlich auf Faktoren laden. Heißt: Sektor-Rotation ist ein verrauschter Stellvertreter für Faktor-Wetten und Markt-Beta, kein eigener Effekt.
- Novy-Marx/Velikov: Industrie-Momentum auf Einzelaktien-Ebene ist nach Kosten negativ (siehe 3.5). Das gilt für den 1-Monats-Aufbau auf Aktien mit Spreads von 1963-2013. Für den 12-Monats-Aufbau auf ETFs mit sehr kleinen Spreads ist es nicht gemessen. Ob die Kostenfalle dort besteht, ist offen.
- Steuern/Zugang (mein Hintergrundwissen, nicht in dieser Session belegt): US-domizilierte ETFs sind für deutsche Privatanleger bei vielen Brokern nicht handelbar (KID/PRIIPs). UCITS-Sektor-ETFs (z. B. iShares S&P 500 Sektor-UCITS) haben eine kürzere Historie. Vor Live-Betrieb prüfen.
- Strukturbruch (Hintergrundwissen, nicht belegt): Die GICS-Reform im Herbst 2018 hat Sektorinhalte verschoben (neuer Sektor Kommunikation). XLK und XLY sind danach nicht mehr dieselben Portfolios wie vorher.
- Kontext aus Nicks Projekt: ETF-v4-Momentum schlägt S&P-500-Buy&Hold nicht (10,02 % vs 10,56 %), nur der Drawdown ist besser. Das ist ein Warnsignal für diese long-only Rotation.

**Prüfplan (Vorschlag)**: Erwartung: Top-3-Rotation schlägt den gleichgewichteten Sektor-Korb (nicht nur SPY) nach 5 bps Sharpe-seitig; Abbruch, wenn im Walk-forward weniger als 60 % der Fenster den Korb schlagen oder der Permutationstest p > 0,10 ergibt. Datenhoheit: Daten ab 2023-01-01 bleiben im Holdout.

### 3.3 `country_etf_xsmom_12_1` — Länder-ETF-Momentum

**Quelle**: Asness/Moskowitz/Pedersen (JF 2013, "Value and Momentum Everywhere", Abstract-Ebene: Momentum-Prämien in acht Märkten und Anlageklassen, darunter Länder-Aktienindex-Futures); Daten und Sharpe-Zahlen für Länder-Futures aus Daniel/Moskowitz Tabelle 10. Die Gewichtung (Rang minus Durchschnittsrang) ist **meine Implementierungsentscheidung** in AMP-Stil und nicht in dieser Session am Paper geprüft.

**Regel (unzweideutig)**
```
UNIVERSUM (fest, 17 iShares-MSCI-Länder-ETFs, Yahoo ab 1996-03-18):
  EWA EWC EWG EWH EWI EWJ EWM EWN EWP EWQ EWS EWU EWW EWL EWD EWK EWO

SIGNALTAG t = letzter NYSE-Handelstag von Monat m, nur Daten <= t:
  score_i = AdjClose_i[Ende Monat m-1] / AdjClose_i[Ende Monat m-12] - 1     # 11 Monate, jüngster Monat übersprungen
  rank_i  = 1..17 aufsteigend nach score (Gleichstand alphabetisch);  z_i = rank_i - 9
  Basis (Long-Short, Dollar-neutral):  w_i = z_i / 36       # positive Gewichte summieren zu +1, negative zu -1, Brutto 2
  erstes gültiges Signal: 1997-03-31 (Ende Monat m-12 = 1996-03-29)

AUSFÜHRUNG: Order zur Eröffnung t+1, monatlich neu, Halten bis zum nächsten Signaltag. Cash/Sicherheit zu RF, Leihekosten laut qlab.

VORAB FESTGELEGTE VARIANTEN:
  long_top5      : 1/5 auf die 5 besten, sonst 0 (long-only, praxistauglich für Privatanleger)
  long_top5_sma10: wie long_top5, aber ein ausgewählter ETF nur, wenn AdjClose[t] > Mittel seiner letzten 10 Monatsendkurse, sonst Cash
PFLICHT-VERGLEICHE: Gleichgewicht über die 17 ETFs; ACWI (ab 2008-03-28) oder EFA (ab 2001-08-27) Buy&Hold; Permutationstest.
```

**Daten gratis (Yahoo-Start geprüft)**: die 17 oben ab 1996-03-18. Erweiterung später möglich: EWZ ab 2000-07-14, EWY 2000-05-12, EWT 2000-06-23, EZA 2003-02-07. Nicht in das Basisuniversum, um das Universum konstant zu halten.

**Evidenz**
- AMP (Abstract): Momentum- und Value-Prämien in acht Märkten, starke gemeinsame Faktorstruktur; Momentum und Value negativ korreliert.
- Daniel/Moskowitz Tabelle 10 (Länder-Aktienindex-Futures, 18 entwickelte Märkte, Daten ab Januar 1978, Tabellenspalte "EQ" ab 02/79 bis 05/2013): Sharpe statisch 0,705, cvol 0,800, dynamisch 0,843. Die Zuordnung der Spalte ist aus den Startdaten im Textlayout rekonstruiert (Startdaten stimmen mit dem Datenabschnitt überein); trotzdem als "nicht doppelt geprüft" behandeln. Futures-Renditen sind lokale Überschussrenditen ohne Währungseffekt, USD-ETFs enthalten den Währungseffekt.
- Daniel/Moskowitz: Option-artiges Crash-Muster auch bei Index-Futures-Momentum.

**Nachpublikations-Verfall, Kosten, Tail-Risiko**
- Zur Out-of-Sample-Performance von Länder-ETF-Rotationen habe ich nichts Belastbares gefunden. Die ETF-Historie umfasst etwa 26 Jahre und 17 stark korrelierte Märkte (ein gemeinsamer globaler Faktor), die statistische Aussagekraft ist gering.
- Spreads kleiner Länder-ETFs (EWK, EWO, EWD) sind größer als bei SPDR-Sektoren (nicht gemessen). ETFs handeln zu US-Zeiten, die Auslandsmärkte sind teils geschlossen: Kurse am Open des nächsten Tages enthalten Informationssprünge aus dem Ausland. Das ist keine Verzerrung zugunsten der Strategie, aber ein Rauschfaktor.
- Long-Short mit ETFs erfordert Leerverkäufe (Leihe), für Privatanleger oft nicht machbar. Dann bleibt die Long-only-Variante, die wieder fast Markt-Beta ist.
- Meine Einschätzung (nicht belegt): netto nach Kosten und Steuern kein belastbarer Vorteil zu erwarten.

**Prüfplan (Vorschlag)**: Abbruch, wenn der Long-Short-Teil (Basis) nach 10 bps pro Seite einen Sharpe unter 0,3 hat oder weniger als 60 % der Walk-forward-Fenster positiv sind.

### 3.4 `wml_dynamic_dm_expanding` — Daniel/Moskowitz dynamisches Momentum, ex ante gerechnet

**Quelle**: Daniel/Moskowitz (JFE 2016), Abschnitt 4, Gleichung (5) bis (7), Tabelle 5, Anhang C und D.

Im Paper werden die GJR-GARCH-Parameter und die Regression **über die gesamte Stichprobe** (1927-2013) geschätzt. Der Sharpe-Zugewinn ist deshalb in der Stichprobe. Die folgende Regel schätzt alles mit wachsendem Fenster. Die Ergebnisse sind damit nicht mit den Paper-Zahlen vergleichbar, absichtlich.

**Regel (unzweideutig)**
```
DATEN: WML[d] wie in 3.1; MKT[d] = (Mkt-RF)[d] + RF[d] aus F-F_Research_Data_Factors_daily; WMLm[k] = Monatsrendite von WML (kumuliert aus Tagen).

SIGNALTAG t = letzter NYSE-Handelstag von Monat m, nur Daten <= t, Mindestlänge 120 Monate Vorlauf:
  I_B  = 1 wenn die kumulierte MKT-Rendite der letzten 24 Monate bis t < 0, sonst 0     # Bärenmarkt-Indikator
  s2m  = Varianz der täglichen Marktüberschussrenditen der letzten 126 Handelstage bis t, mal 252
  Mittelwert-Prognose mu_hat:
     OLS über alle Monate k mit realisierter Folgerendite bis t:   WMLm[k+1] = g0 + gB*I_B[k] + gs*s2m[k] + gi*I_B[k]*s2m[k] + e
     mu_hat = g0 + gB*I_B[m] + gs*s2m[m] + gi*I_B[m]*s2m[m]          # Prognose für Monat m+1 (Spalte 5 der Paper-Tabelle 5)
  Vol-Prognose sigma_22 (täglich):
     sigma_126 = stdev(WML der letzten 126 Tage bis t)
     sigma_GJR = Durchschnitt der GJR-GARCH(1,1)-Tagesvol-Prognose über die nächsten 22 Tage; Parameter per Max-Likelihood auf WML[Tage <= t],
                 neu geschätzt einmal jährlich im Januar, Prognose monatlich mit festen Parametern aktualisiert
     sigma_22  = a + b*sigma_GJR + c*sigma_126, mit (a,b,c) aus OLS (wachsendes Fenster) von realisierter Folgemonats-Tagesvol auf (1, sigma_GJR, sigma_126)
     (Paper-Vollstichprobenwerte nur zum Vergleich: a = 0,0010, b = 0,6114, c = 0,2640)
  sigma_month = sigma_22 * sqrt(21)
  w_raw = mu_hat / sigma_month^2
  Skalierung c_t: so, dass die annualisierte Vol der Reihe {w_raw[k]*WMLm[k+1]} über alle k < m bei 19 % liegt (nur Vergangenheit)
  w = clip(c_t * w_raw, -2.0, +2.0)                              # Deckel 2.0 ist meine Schutzgrenze

POSITION: ab Handelstag t+1, Rest zu RF; w kann negativ werden (Paper erlaubt das, wenn mu_hat < 0).
KONTROLLEN: statisch, 3.1 (cvol), dyn mit Vollstichprobe (nur zur Quantifizierung des In-Sample-Bias).
```

**Evidenz** (aus dem Paper, in der Stichprobe): dynamisch ist ungefähr doppelt so gut wie statisch und "etwas besser" als cvol. Tabelle 10 (bis 05/2013), Sharpe dyn: US ab 07/72 0,646 (statisch 0,283, cvol 0,519); Europa 1,130; UK 0,891; Japan 0,416 (statisch 0,067). Über alle Märkte und Anlageklassen kombiniert: Sharpe 1,18 laut Text (Tabellenwert GAll 1,139, mit vollständig dynamischer Aggregation GAll* 1,223). Anleihen: kein signifikanter Gewinn (0,066).
Paper-Spalte 5 von Tabelle 5 (Monatsrendite in Prozent): g0 = 2,129, gB = 0,023, Marktvarianz -0,088, Interaktion -0,323 (t = -2,2). Einheiten der Varianz-Variable sind aus dem Text nicht eindeutig, daher eigene OLS statt Paper-Koeffizienten.

**Nachpublikations-Verfall, Kosten, Tail-Risiko**
- Hauptrisiko: Overfitting über Vollstichprobe-Schätzung. Der Zugewinn gegenüber cvol ist klein (Vollstichprobe), und ex ante vermutlich kleiner.
- Wegen negativer Prognosen kann die Strategie Momentum shorten, genau dann, wenn Märkte fallen und die Vol hoch ist. Das hat in den 1930er Jahren und 2009 geholfen, es ist ein Wettlauf gegen eine kleine Zahl von Ereignissen (wenige unabhängige Crash-Episoden).
- Gleiche Kostenaussage wie 3.1 (Aktien-Dezile, Leerverkauf).
- Komplexität: GARCH-Fit, zwei Regressionen, wachsendes Fenster. Viele Freiheitsgrade: Jede Änderung zählt als Test für die Mehrfachtest-Korrektur.

**Prüfplan (Vorschlag)**: Nur nach 3.1 ausführen. Abbruch, wenn die ex ante Variante den cvol-Sharpe in 2000-2022 nicht um mindestens 0,1 übertrifft.

### 3.5 `industry_mom_ff17_ls` — Industrie-Momentum (Moskowitz/Grinblatt), ehrlich: nach Kosten tot

**Quelle**: Moskowitz/Grinblatt (JF 1999, Abstract): starker Industrie-Momentum-Effekt, erklärt einen großen Teil des Aktien-Momentum und bleibt nach Kontrolle von Größe, Buchwert/Marktwert, Aktien-Momentum, Querschnitts-Streuung und Mikrostruktur-Effekten profitabel. Arnott et al. nennen den 1-Monats-Horizont als den stärksten. Novy-Marx/Velikov definieren Industrie-Momentum als "Rendite der Industrie im letzten Monat".

**Regel (unzweideutig)**
```
DATEN: French 17_Industry_Portfolios_daily_CSV (VW), plus RF.
SIGNALTAG t = letzter NYSE-Handelstag von Monat m, nur Daten <= t:
  Basis (L=1):   score_j = kumulierte Rendite von Industrie j über die Handelstage von Monat m
  Variante L=6:  kumuliert über die letzten 6 Kalendermonate bis t
  Variante 12-1: kumuliert über Monat m-11 bis m-1 (Monat m ausgelassen)
  Rang absteigend, Gleichstand alphabetisch nach Industrie-Name.
ZIEL: +1/3 auf die 3 besten, -1/3 auf die 3 schlechtesten (Dollar-neutral, Brutto 2). Rest zu RF.
AUSFÜHRUNG: Gewichte ab Handelstag t+1, monatlich neu.
KOSTEN-STRESS: 5, 25, 50 bps pro Seite (die Industrie-Körbe selbst sind nicht handelbar; die Zahlen stehen für den Aufwand, einen Industriekorb aus Einzelaktien nachzubauen).
```
**Daten gratis**: French 17 Industry Portfolios (Datei oben; auch 10/12/30/38/48/49 vorhanden). Startdatum: nicht geprüft; laut Faber-Anhang (Stand 2010) für die 10er-Version monatlich ab 1926-07, täglich ab 1963-07-01. Heutige Dateien können länger zurückreichen.

**Evidenz und Verfall (das ist der eigentliche Wert dieses Eintrags)**
- Novy-Marx/Velikov Tabelle 3 (VW-Dezile auf Einzelaktien, NYSE-Breakpoints, 1963-2013, monatlich, Signal "Industrie-Rendite des letzten Monats"): brutto 0,93 %/Monat (t = 3,97), Kosten 1,22 %/Monat, netto **-0,29 %/Monat (t = -1,20)**.
- Mit Kostenminderung bleibt es negativ: gestaffeltes Rebalancing (Tabelle 7): brutto 0,50, Kosten 0,75, netto -0,26 (t = -2,26). Kauf/Halten-Band 10 %/50 % (Tabelle 8): brutto 0,73, Kosten 0,75, netto -0,02 (t = -0,09).
- Arnott et al. (Abstract): Industrie-Momentum entsteht aus Faktor-Momentum und wird von Faktor-Momentum in industrie-neutralisierten Faktoren abgedeckt. Es ist also kein eigener Effekt.
- Moskowitz/Grinblatt 1999: Replikation außerhalb der USA gemischt (kanadische Studie: Industrie-Faktoren erklären Momentum in Kanada nicht; laut Suchtreffer, nicht geprüft).
- Auf Sektor-ETF-Ebene (9 bis 11 Titel) sind die Kosten viel kleiner, aber dann ist auch die Querschnittsstreuung klein. Eine belegte Netto-Zahl dafür habe ich nicht.

**Zweck im Lab**: Negativ-Kontrolle. Wenn sogar die Long-Short-Version auf den French-Industrien mit 5 bps keinen Sharpe über 0,3 zeigt, dann ist Strategie 2 reines Markt-Beta mit Sektor-Tilt.

**Prüfplan (Vorschlag)**: Erwartung: Brutto-Sharpe der Basis (L=1) positiv, nach 25 bps pro Seite nicht mehr signifikant. Abbruch ab dem ersten Test nach 25 bps mit Sharpe unter 0,3.

## 4. Quer-Evidenz zu Verfall und Replikation

- McLean/Pontiff (Journal of Finance 2016), nur Suchtreffer-Zusammenfassung: 97 Prädiktoren, Rendite nach Veröffentlichung etwa 58 % niedriger als in der Stichprobe (0,26 %/Monat Long-Short), größter Rückgang 3-4 Jahre nach Veröffentlichung. Nicht momentum-spezifisch, brutto.
- Chen/Zimmermann (Critical Finance Review 2022), nur Suchtreffer-Zusammenfassung: 319 Charakteristika, Replikation gelingt für fast alle (98 % der klar signifikanten haben t über 1,96). Zeigt Replizierbarkeit in der Stichprobe, nicht Verfall.
- Daniel/Moskowitz-Zitate: Momentum bestand 1990-1998 (Jegadeesh/Titman 2001) und 1927-1965 sowie 1990-2012 (Israel/Moskowitz 2013). Nicht selbst geprüft.
- Jegadeesh/Titman 2023 ("Momentum: Evidence and Insights 30 Years Later", Pacific-Basin Finance Journal 82): analysiert die Zeit nach 2000 in Pazifik-Märkten und entwickelten Westmärkten. Ergebnisse (Zahlen) nicht gefunden, Volltext hinter Paywall.
- AQR-Momentum-Indizes werden quartalsweise statt monatlich neu gewichtet, um Kosten zu sparen (Novy-Marx/Velikov, Fußnote 5). Das zeigt, dass die Kosten für Profis ein Designthema sind.

## 5. Offene Punkte und Datenlücken

1. Startdaten der French-Dateien (Momentum-Dezile, 17 Industrien, täglich) nicht geprüft. Beim Laden per `qlab.data.french()` direkt prüfen.
2. Spaltennamen der French-Momentum-Datei aus Erinnerung. `_read_french_csv` im Projekt liest laut Code vermutlich nur den ersten Block (VW). Prüfen.
3. Fabers Kennzahlentabellen (Buy&Hold, Top 1 bis 3, alle Lookbacks) sind Bilder im PDF. Zum Nachlesen Seite 8-9 des PDF öffnen.
4. Barroso/Santa-Clara: Vollständige Zahlen (Sharpe roh vs. verwaltet, Fenster, Ziel-Vol) nur aus Sekundärquellen. Original über die JFE-Seite (DOI 10.1016/j.jfineco.2014.11.010 laut Suchtreffer) oder SSRN prüfen, bevor die Parameter fixiert werden.
5. Asness/Moskowitz/Pedersen: Gewichtungsschema und genaue Formationsregeln im Volltext nachlesen, bevor `country_etf_xsmom_12_1` endgültig festgelegt wird. AQR stellt die zugehörigen Datensätze bereit (Seite nicht abgerufen).
6. Faktor-Momentum (Arnott et al., Ehsani/Linnainmaa) wäre mit French-Faktoren gratis testbar, ist aber im Volltext nicht gelesen. Nicht als Strategie aufgenommen.

## 6. Quellen-URLs

Abgerufen und gelesen:
- Daniel/Moskowitz, Momentum Crashes (PDF): https://business.columbia.edu/sites/default/files-efs/pubfiles/4607/mom11.pdf
- Daniel/Moskowitz, NBER w20439 (Suchtreffer, Journal laut Suchtreffer: JFE 122(2), 221-247, 2016): https://www.nber.org/papers/w20439
- Novy-Marx/Velikov, A Taxonomy of Anomalies and Their Trading Costs (NBER w20721, RFS 29(1) 104-147, 2016): https://www.nber.org/papers/w20721.pdf und https://www.nber.org/papers/w20721
- Faber, Relative Strength Strategies for Investing (SSRN 1585517): https://ssrn.com/abstract=1585517 ; PDF-Kopie: https://c.mql5.com/forextsd/forum/213/Relative%20Strength%20Strategies%20for%20Investing.pdf
- Quantpedia, Sector Momentum Rotational System: https://quantpedia.com/strategies/sector-momentum-rotational-system
- Barroso/Santa-Clara, Momentum has its moments (Abstract-Seite): https://ciencia.ucp.pt/en/publications/momentum-has-its-moments/
- Ken French Data Library: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html

Nur als Suchtreffer (Abstract-Ebene) gesehen:
- Moskowitz/Grinblatt, Do Industries Explain Momentum? (JF 54(4), 1249-1290, 1999): https://ideas.repec.org/a/bla/jfinan/v54y1999i4p1249-1290.html
- Asness/Moskowitz/Pedersen, Value and Momentum Everywhere (JF 68(3), 929-985, 2013): https://www.aqr.com/library/journal-articles/value-and-momentum-everywhere und https://pages.stern.nyu.edu/~lpederse/papers/ValMomEverywhere.pdf
- Geczy/Samonov, Two Centuries of Price-Return Momentum (FAJ 72(5), 32-56, 2016): https://papers.ssrn.com/abstract=2292544 und https://ideas.repec.org/a/taf/ufajxx/v72y2016i5p32-56.html
- Arnott/Clements/Kalesnik/Linnainmaa, Factor Momentum (Arbeitspapier Januar 2018): https://rodneywhitecenter.wharton.upenn.edu/wp-content/uploads/2018/03/Juhani.pdf ; Zusammenfassung: https://alphaarchitect.com/the-explanatory-power-of-factor-momentum/
- Jegadeesh/Titman, Momentum: what do we know 30 years after... (Pacific-Basin Finance Journal 82, 2023): https://ideas.repec.org/a/eee/pacfin/v82y2023ics0927538x23002731.html
- Jegadeesh/Titman, Profitability of Momentum Strategies: An Evaluation of Alternative Explanations (2001): https://www.nber.org/papers/w7159
- Chen/Zimmermann, Open Source Cross-Sectional Asset Pricing: https://papers.ssrn.com/abstract=3604626
- McLean/Pontiff: nur über Sekundärtreffer, keine Original-URL abgerufen.

## 7. Datenstarts (Yahoo, per yfinance am 2026-10-11 geprüft)

| Ticker | Erster Datenpunkt |
|--------|-------------------|
| XLB XLE XLF XLI XLK XLP XLU XLV XLY | 1998-12-22 |
| XLRE | 2015-10-08 |
| XLC | 2018-06-19 |
| SPY | 1993-01-29 |
| MTUM | 2013-04-18 |
| IWM | 2000-05-26 |
| VGT VHT VFH VCR VDC VAW VPU | 2004-01-30 |
| VDE VIS VOX VNQ | 2004-09-29 |
| EWA EWC EWG EWH EWI EWJ EWM EWN EWP EWQ EWS EWU EWW EWL EWD EWK EWO | 1996-03-18 |
| EWZ / EWY / EWT / EZA / EPOL | 2000-07-14 / 2000-05-12 / 2000-06-23 / 2003-02-07 / 2010-05-26 |
| EFA / EEM / ACWI | 2001-08-27 / 2003-04-14 / 2008-03-28 |
| ^GSPC / ^IRX / ^VIX | 1927-12-30 / 1960-01-04 / 1990-01-02 |
| BIL / SHY | 2007-05-30 / 2002-07-30 |
| GC=F | 2000-08-30 |
