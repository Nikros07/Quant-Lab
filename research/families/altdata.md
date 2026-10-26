# Familie: Alternative Daten / Prediction Markets / Event-getrieben

Stand der Recherche: 2026-10-12. Budget: 15 Web-Abrufe (WebSearch + WebFetch), Liste in Abschnitt 1. Zusätzlich lokale Prüfungen (Python/curl gegen Yahoo, Ken French, Wurgler-Seite, siehe Abschnitt 1) und ein per WebFetch gespeichertes PDF, das ich lokal mit pdftotext komplett gelesen habe.

Kennzeichnung der Belegstärke:
- **[GELESEN]** = Text der Seite bzw. des PDF wurde abgerufen und gesehen.
- **[SNIPPET]** = nur Zusammenfassung aus einem Suchergebnis gesehen, Quelle selbst NICHT geöffnet. Zahlen daraus sind unverifiziert. Alle Snippet-Quellen sind in der Strukturausgabe entsprechend markiert.
- **[LOKAL GEPRÜFT]** = per Skript gegen die echte Datenquelle getestet (Namen, Datenstart, Spalten).
- **[GEDÄCHTNIS]** = aus meinem Wissen, in dieser Sitzung nicht geprüft. Vor Nutzung prüfen.
Was ich nicht gefunden habe, steht ausdrücklich als "nicht gefunden".

## 0. Kurzfazit (ehrlich)

- Diese Familie liefert **keinen Kandidaten, der sicher nach Kosten und Steuern trägt**. Das ist ein gültiges Ergebnis. Die Familie liefert vor allem (a) eine strukturell begründete Ineffizienz mit winziger Kapazität (Prediction-Market-Favoriten), (b) einen Regime-Filter für Anomalien, der Long-Short braucht und in Echtzeit nicht beziehbar ist (Baker-Wurgler-Sentiment), (c) eine kurzfristige Umkehr-Idee mit kurzer Publikationsstichprobe und fragiler Datenquelle (Google-Suchvolumen), (d) zwei Einträge, die laut Literatur nach Veröffentlichung/Kosten **tot bis sehr schwach** sind (Wetter/SAD, PEAD in Large Caps).
- Das beste Alt-Data-Ergebnis in meinen Quellen ist **negativ**: Der berühmte Google-Trends-"debt"-Backtest (Preis et al. 2013) ist ein Keyword-Mining-Artefakt, und die vorgelegte Replikation mit später geladenen Daten reproduziert die Entscheidungen nur zu 72 % (Wiecki-Notebook, blogartig, SNIPPET).
- **Datenqualität ist selbst das Risiko**: Google Trends ist gesampelt und normalisiert (jede Abfrage kann abweichen), Yahoo-Earnings-Daten sind inoffiziell, der Wurgler-Index wird nur jährlich aktualisiert (Datei sagt "UPDATED: March, 2026", Daten bis 2025-12).
- Praktisch für Deutschland: Prediction Markets sind rechtlich/steuerlich und im Zugang (Kalshi: US-reguliert; Polymarket: geoblocking in mehreren Ländern) für einen Wohnsitz in Deutschland **nicht geprüft**. SPY/QQQ sind für EU-Kleinanleger typischerweise nicht kaufbar (PRIIPs); für Live bräuchte man UCITS-Äquivalente (Ticker, Datenstart, Spread vor Nutzung prüfen). Abgeltungssteuer wird bei jedem Round-Trip fällig; bei den kurzen Haltedauern (FEARS: 2 Tage) ist das ein Dauerbremsklotz.
- Mehrfachtest-Hinweis: Fünf Einträge sind nicht fünf unabhängige Chancen. FEARS, Sunshine und News-Sentiment sind alle "Stimmung -> kurzfristiger Aktienindex". Wenn die Lab-Regeln (Deflated Sharpe) gelten, zählt jede Parametervariante mit.

## 1. Abrufstatus (Transparenz)

| Nr | Typ | Quelle / Zweck | Status |
|---|---|---|---|
| 1 | WebSearch | Polymarket/Kalshi Kalibrierung, Favorite-Longshot | ok, Snippets |
| 2 | WebSearch | PEAD nach Veröffentlichung, Martineau | ok, Snippets |
| 3 | WebFetch | arxiv.org/abs/2602.19520 (Le 2026) | GELESEN (Abstract-Seite) |
| 4 | WebFetch | UCLA Anderson Review "Is PEAD a thing again?" | GELESEN |
| 5 | WebSearch | Google Trends Preis/Challet/Replikation | ok, Snippets |
| 6 | WebFetch | arxiv.org/abs/1403.1715 (Challet, Bel Hadj Ayed) | GELESEN (Abstract-Seite) |
| 7 | WebSearch | Sunshine (Hirshleifer-Shumway), SAD (Kamstra), Replikationen | ok, Snippets |
| 8 | WebFetch | pages.stern.nyu.edu/~jwurgler/ | NUTZLOS (nur Frameset); Daten danach lokal geprüft |
| 9 | WebSearch | Baker-Wurgler Daten, Stambaugh-Yu-Yuan | ok, Snippets |
| 10 | WebSearch | Tetlock 2007, Garcia 2013, News-Strategien nach Kosten | ok, Snippets |
| 11 | WebSearch | Da-Engelberg-Gao (Attention, FEARS) | ok, Snippets |
| 12 | WebFetch | www2.gwu.edu/~forcpgm/2026-001.pdf (Kalshi-Paper) | PDF wurde gespeichert und lokal mit pdftotext GELESEN (85 KB Text) |
| 13 | WebFetch | docs.polymarket.com ... prices-history | GELESEN |
| 14 | WebSearch | PEAD/EAR/Kosten/Quantpedia | ok, Snippets |
| 15 | WebSearch | Snowberg-Wolfers (FLB), Snowberg-Wolfers-Zitzewitz | ok, Snippets |

Zusätzliche lokale Prüfungen (keine WebSearch/WebFetch-Abrufe, aber echte Netzzugriffe, Ergebnisse sind [LOKAL GEPRÜFT]):
- Yahoo via yfinance 1.7.0 (Quant-Lab-venv): Datenstarts der Ticker (Tabelle in Abschnitt 8).
- Ken French: monatliche Datensätze per Loader aus `qlab/data.py` gelesen (Namen und Datenstart, Abschnitt 8).
- Wurgler: Datei `https://pages.stern.nyu.edu/~jwurgler/data/SENTIMENT.xlsx` heruntergeladen (130 KB) in eigenen Ordner, mit Standardbibliothek im isolierten Modus gelesen.
- yfinance `Ticker.get_earnings_dates(limit=100)` für AAPL, KO, JNJ getestet.

## 2. Strategie 1: Prediction-Market-Favoriten (Favorite-Longshot-Ernte), id `pm_favorite_maker`

### Idee und Evidenz
Bei Wettmärkten werden Außenseiter überbezahlt, Favoriten unterbezahlt (Favorite-Longshot-Bias, Jahrzehnte alt im Pferderennen). Neu ist der Nachweis auf Kalshi und Polymarket.

**Bürgi, Deng, Whelan (2026), "Makers and Takers: The Economics of the Kalshi Prediction Market"**, GWU CER Working Paper 2026-001, https://www2.gwu.edu/~forcpgm/2026-001.pdf [GELESEN, lokal]:
- Daten: Transaktionsdaten zu 46.282 Kontrakten aus 12.403 Events, 2021 bis April 2025, über 300.000 Preise (Preise bis zu 10 Tage vor Marktschluss, 24-Stunden-Raster).
- Kontrakte unter 10 Cent: Verlust von über 60 % des Einsatzes (nach Gebühren). Beispiel im Text: Ein 5c-Kontrakt, der nur zu 3 % gewinnt, hat vor Gebühren -40 %.
- Kontrakte ab 50 Cent: kleine positive Renditen, ab 70 Cent statistisch signifikant, aber klein. 95c-Kontrakt, der zu 98 % gewinnt: +3,1 % vor Gebühren.
- Durchschnittliche Rendite aller Kontrakte ca. -20 % (gleichgewichtet über Kontrakte, vor Gebühren). Maker im Schnitt -9,64 %, Taker -31,46 % (nach Gebühren).
- Maker, die Kontrakte ab 50 Cent kaufen: **+2,6 % pro Kontrakt**, Standardabweichung 33 %. Das ist keine Jahresrendite, sondern pro Kontrakt bis Abwicklung.
- Gebühren im Samplezeitraum: Taker zahlen 0,07 * P * (1-P) pro Kontrakt (aufgerundet auf Cent), Maker nichts. **Ab April 2025 zahlen auch Maker Gebühren** (Höhe im Paper nicht genannt, Stichprobe endet deshalb im April 2025). Das gefährdet die +2,6 %.
- Die Autoren sagen selbst: Der Bias scheint über die Zeit abzunehmen. Sie nennen drei Gründe, warum das noch niemand wegarbitriert hat: kleine Volumina (Top-Dezil-Markt im Schnitt 526.245 USD Endvolumen), Risiko (hohe Streuung), mangelnde Kenntnis. Sie erwarten möglichen Verfall nach Veröffentlichung.
- Regressionen nach Jahr (Tabelle 9): Preis-Koeffizient bleibt in allen Jahren 2021 bis 2025 positiv (0,021 bis 0,048, 2025 nur auf 10 %-Niveau signifikant). Bias besteht also bis 2025, ist aber nicht größer geworden.

**Le (2026), "Decomposing Crowd Wisdom: Domain-Specific Calibration Dynamics in Prediction Markets"**, arXiv:2602.19520 (v1 23.02.2026, v2 04.08.2026), https://arxiv.org/abs/2602.19520 [Abstract-Seite GELESEN]:
- 353 Mio. Trades in 429.000 binären Kontrakten auf Kalshi und Polymarket. Robustester Befund: dauerhafte Unterkonfidenz in Politik-Märkten (Preise zu nah an 50 %), repliziert auf Polymarket. Große Kalshi-Politik-Trades zeigen zusätzliche Kompression, auf Polymarket nicht robust. Laut Bayes-Modell ist etwa die Hälfte der rohen Steigungsvariation Schätzrauschen.
- **Warnung:** Ein Suchsnippet zur v1 nannte 292 Mio. Trades / 327.000 Kontrakte und "ein 70-Cent-Kontrakt einen Monat vor Ablauf entspricht ca. 75 %". Die v2-Abstract-Seite nennt andere Stichprobengrößen und diese Zahl nicht. Die 70->75-Zahl ist daher unverifiziert und kann sich zwischen Versionen geändert haben.

**Snowberg, Wolfers (2010), "Explaining the Favorite-Longshot Bias: Is it Risk-Love or Misperceptions?"**, JPE 118(4), NBER WP 15923, https://www.nber.org/papers/w15923 [SNIPPET]: Wahrscheinlichkeitsfehlwahrnehmung (Prospect Theory) erklärt den Bias besser als Risikoliebe. (Pferderennen, nicht Prediction Markets.)

Polymarket-Daten: `GET https://clob.polymarket.com/prices-history` mit `market` (Asset-ID), `startTs`, `endTs`, `interval` (max, all, 1m, 1w, 1d, 6h, 1h), `fidelity` (Minuten, Default 1); keine Authentifizierung nötig; Rate-Limits, maximale Datenmenge und Zeitstempel-Einheit **nicht dokumentiert** (https://docs.polymarket.com/developers/CLOB/timeseries) [GELESEN]. Kalshi: öffentliche Marktdaten-API und Handelshistorie, Auth-/Rate-Limit-Details **nicht geprüft** [GEDÄCHTNIS]. Wiederverwendbar im Lab: `Projekte\Polymarket-Bot\backend\services\polymarket_service.py` (Gamma-Abruf, Normalisierung der Marktfelder) laut CLAUDE.md-Tabelle; ich habe nur die Feldnamen per grep gesehen, nicht die Qualität des Codes geprüft.

Weitere Quellen mit Zahlen, die ich nur als Snippet sah und nicht als Beleg verwende: ein Princeton-Thesis (Polymarket Brier Skill Score 0,398, Bandbreite 0,264 Sport bis 0,565 Politik; https://theses-dissertations.princeton.edu/entities/publication/d5708372-5ea3-4252-b669-7f9cee07387c), Blogposts. Nicht peer-reviewed.

### Regel (unzweideutig)
```
Daten: Polymarket binäre Märkte (resolved, nicht annulliert). Marktliste inkl. Auflösung und
       Enddatum: Gamma-API https://gamma-api.polymarket.com/markets (Felder closed, active, outcomePrices, endDate
       sind im Lab-Projekt Projekte\Polymarket-Bot\backend\services\polymarket_service.py in Gebrauch, Code gelesen;
       die Token-/Asset-ID für prices-history [Feld clobTokenIds] und historische Abfrage mit closed=true sind NICHT geprüft)
       Preishistorie: CLOB prices-history, interval=max, fidelity=1440 (Tagesraster).
Universum: Märkte mit >= 14 Tagen Preishistorie vor Ende und kumuliertem Volumen >= V_MIN
           (vorab festlegen, Vorschlag 20 000 USD). Annullierte Märkte zählen mit PnL 0 (Rückerstattung).
Für jedes Event E mit Auflösungsdatum D (Kalenderdatum des Marktendes):
  Signaltag s = D - 8 Tage; Signalpreis p_yes = letzter Tageskurs (Bar-Close) des Tages s.
  Kandidaten-Seiten: YES mit Preis p = p_yes, NO mit Preis p = 1 - p_yes.
  Kandidat, wenn 0.70 <= p <= 0.95.
  Pro Event höchstens EINE Position: die Seite mit dem höchsten p unter den Kandidaten.
  Kein Kandidat -> kein Trade.
Ausführung: am Folgetag (s+1) zum Tages-Close dieser Seite plus 0.01 (konservativ, 1 Tick Slippage).
            Optimistische Sensitivität: Füllung zu p(s) ohne Aufschlag (Maker-Annahme).
Größe: Einsatz je Event = 0.5 % des aktuellen Kontos, maximal 10 % des Kontos gleichzeitig offen
       (weitere Events in Reihenfolge ihres Enddatums überspringen, wenn Deckel erreicht).
Halten: bis Auflösung. PnL pro Kontrakt: (1 - f) wenn Seite gewinnt, sonst -f (f = Füllpreis).
Gebühren: Kalshi-Taker ceil_cent(0.07 * f * (1-f)) je Kontrakt (Schema vor 04/2025, aus Bürgi et al.).
          Maker-Gebühr ab 04/2025 und Polymarket-Gebühren: NICHT verifiziert; Baseline 0, Sensitivität 2 % vom Einsatz.
Sensitivitäten (alle berichten, keine nachträgliche Auswahl): Horizont D-2, D-4, D-11 statt D-8; Preisband 0.50-0.95.
Bewertung: Ereignis-geclusterter Bootstrap der mittleren Rendite pro Event; Halbjahres-Aufteilung;
           Test, ob das Vorzeichen in Märkten mit Auflösungsdatum nach 2025-04 gleich bleibt.
```

### Ehrliche Risiken
- Backtest auf Tages-Closes kann Maker-Füllung nicht abbilden (Warteschlange, Adverse Selection). Die +2,6 % stammen aus echten Maker-Fills; unser Proxy ist optimistisch oder pessimistisch, je nach Annahme.
- Kapazität winzig. Streuung groß (33 % pro Kontrakt). Korrelation innerhalb Events und über thematisch verwandte Events (Wahlen) wird bei Gleichgewichtung unterschätzt.
- Verfall: Autoren sehen Abnahme, Maker-Gebühren seit April 2025 drücken die Marge. Zugang/Recht/Steuer für Deutschland ungeklärt. **Echtgeld-Freigabe ist Nicks Entscheidung (Lab-Regel 5).**

## 3. Strategie 2: Sentiment-Regime-Filter für Anomalien (Stambaugh-Yu-Yuan), id `sentiment_state_anomaly`

### Evidenz
**Stambaugh, Yu, Yuan (2012), "The Short of It: Investor Sentiment and Anomalies"**, JFE 104(2), 288-302; NBER WP 16898, https://www.nber.org/papers/w16898 [SNIPPET]: Jede von 11 Anomalien ist nach hohem Sentiment profitabler; der Effekt kommt von der Short-Seite; auf der Long-Seite kein Zusammenhang. Eine Praxis-Zusammenfassung nennt 70 % des Hedge-Portfolio-Alphas in Monaten mit überdurchschnittlichem Sentiment (Juli 1965 bis Januar 2008, Drei-Faktor-bereinigt). Folgepapier "The Long of It" (NBER WP 18231) simuliert 200 Mio. Zufalls-Regressoren und findet keinen, der so stark wirkt wie Sentiment (Zufallsargument), https://nber.org/system/files/working_papers/w18231/w18231.pdf [SNIPPET].

**Daten [LOKAL GEPRÜFT]:** `https://pages.stern.nyu.edu/~jwurgler/data/SENTIMENT.xlsx`, Blatt `DATA`, Spalten `yearmo, SENT, SENT_ORTH, pdnd, ripo, nipo, cefd, s, indpro, consdur, consnon, consserv, recess, employ, cpi`. `SENT` 1965-07 bis 2025-12 (726 Monate), `SENT_ORTH` 725 Monate. README-Blatt: "UPDATED: March, 2026", Code und jährliche Updates auf GitHub (BWInvestorSentimentIndex). Das heißt: **Die Datei wird nur jährlich aktualisiert; Live-Signale sind damit nicht möglich**, nur Backtest. Der Index ist per Hauptkomponentenanalyse über die Gesamtstichprobe gebaut (Standard-Verfahren dieser Literatur, [GEDÄCHTNIS]) -> Gewichte "kennen" die Zukunft. Baker-Wurgler (2006) JF 61, 1645-1680 ist laut README die Datenquelle; Paper-PDF auf Wurgler-Seite verlinkt (https://pages.stern.nyu.edu/~jwurgler/papers/wurgler_baker_cross_section.pdf), Inhalt von mir NICHT gelesen.

### Regel
```
Daten (alle gratis, [LOKAL GEPRÜFT] Namen/Start): 
  Sentiment: SENT_ORTH (Hauptvariante), SENT (Sensitivität), monatlich.
  French monatlich, erster Block der CSV (Annahme: wertgewichtet, vor Nutzung gegen Dateikopf prüfen):
   10_Portfolios_Prior_12_2 (1927-01), Portfolios_Formed_on_INV / _OP / _AC / _NI / _VAR / _RESVAR / _BETA (je 1963-07),
   F-F_Research_Data_5_Factors_2x3 (1963-07), F-F_Momentum_Factor (1927-01).
Anomalie-Menge K (vorab fixiert, 7 Stück; Long-/Short-Bein jeweils Dezil):
  MOM: long Hi PRIOR, short Lo PRIOR
  INV: long Lo 10, short Hi 10          OP: long Hi 10, short Lo 10
  AC:  long Lo 10, short Hi 10          NI: long Lo 10, short Hi 10 (Dezilspalten, nicht '< 0'/'ZERO')
  VAR: long Lo 10, short Hi 10          BETA: long Lo 10, short Hi 10
Regime je Monat m: H(m) = 1, wenn SENT_ORTH(m-2) > Median von SENT_ORTH über [1965-07 .. m-2] (expandierend,
  KEIN Vollstichproben-Median). Lag 2 Monate wegen Veröffentlichungs-/Revisionslücke.
Strategie-Rendite (Research-Variante, Long-Short): R(m) = mean_k [ H(m) * ( ret_long_k(m) - ret_short_k(m) ) ] + (1-H(m)) * RF(m)
  Rebalancing monatlich, Gleichgewicht über k, Monatsrenditen aus der French-Datei (kein Handelsschritt modelliert).
Zusatztest (Kern der Hypothese): Mittelwert und t-Wert (Newey-West) von (L-S) in H-Monaten minus in Nicht-H-Monaten;
  zusätzlich nur das Short-Bein: ret_short_k(m) in H vs. Nicht-H.
Holdout (vorab festlegen): In-Sample 1965-07 .. 2008-01 (= Paper-Stichprobe, nur Replikation),
  Out-of-Sample 2008-02 .. 2025-12 (~215 Monate) = das eigentliche Urteil.
Kosten: French-Dezile sind kostenfrei und vollständig investiert; Implementierungs-Haircut ist nicht quantifiziert (keine Quelle gesehen) ->
        bei Positivbefund Turnover separat schätzen.
```

### Ehrliche Risiken
- Short-Bein-Gewinne sind für Kleinanleger kaum handelbar (Leerverkauf, Borrow, kleine/illiquide Aktien in den extremen Dezilen). **Long-only-Variante hat laut dem Paper keinen Effekt** (Long-Beine zeigen keinen Zusammenhang).
- Out-of-Sample nach 2008 habe ich **keine Evidenz gefunden** (nicht recherchiert). Die Anomalien selbst sind nach Veröffentlichung generell geschwächt; ob die Sentiment-Interaktion trägt, ist der offene Test.
- Index nur jährlich aktualisiert; ein echtzeitfähiger Proxy (z. B. Michigan Consumer Sentiment auf FRED, AAII-Umfrage) ist **nicht** durch eine von mir gesehene Quelle gedeckt.

## 4. Strategie 3: Google-Suchvolumen "FEARS" als Kontra-Signal, id `fears_reversal`

### Evidenz
**Da, Engelberg, Gao (2015), "The Sum of All FEARS: Investor Sentiment and Asset Prices"**, RFS 28(1), 1-32, https://www3.nd.edu/~pgao/papers/FEARS_20131007.pdf (Arbeitspapier-Fassung) [SNIPPET]: Index aus Suchanfragen zu Haushaltssorgen ("recession", "unemployment", "bankruptcy" als Beispiele), 2004-2011: sagt kurzfristige Umkehr voraus (heute niedrige Rendite, in den **folgenden zwei Tagen** höhere), temporär höhere Volatilität, Abflüsse aus Aktienfonds in Anleihefonds; stärker bei Aktien, die für Noise-Trader attraktiv und schwer zu arbitragieren sind. Später (Snippet): Studie mit ca. 100.000 deutschen Brokerage-Kunden in einem Journal of Financial Markets-Beitrag 2020: negative Kurzfrist-Beziehung, Umkehr in den folgenden sechs Tagen (Titel/URL nicht sauber gesehen, nicht als Beleg gelistet).
**Da, Engelberg, Gao (2011), "In Search of Attention"**, JF, https://rady.ucsd.edu/faculty/directory/engelberg/pub/portfolios/GOOGLE.pdf [SNIPPET]: Anstieg des Suchvolumens (Russell 3000, 2004-2008) sagt höhere Kurse in den nächsten 2 Wochen und Umkehr innerhalb eines Jahres voraus.
**Gegenbeispiel:** Preis, Moat, Stanley (2013), Scientific Reports, https://pmc.ncbi.nlm.nih.gov/articles/PMC3635219 [SNIPPET]: 98 Suchbegriffe, wöchentliche Dow-Jones-Strategie; "debt" lieferte laut Zusammenfassungen 326 % (andere Quelle 310 %) gegen ca. 50 % Buy&Hold (Jan 2004 bis Feb 2011) -> Best-of-98-Auswahl. **Challet, Bel Hadj Ayed (2014), arXiv:1403.1715**, https://arxiv.org/abs/1403.1715 [Abstract GELESEN]: Keyword-Wahl ist "by far the greatest culprit" unter den Verzerrungen; ihr sauberer Backtest liefert ca. 17 Basispunkte pro Woche und hängt nur schwach davon ab, ob Preisrenditen, Google-Daten oder beides als Prädiktoren dienen. Wiecki-Replikationsnotebook (blogartig, SNIPPET): Mit später geladenen Google-Daten sinkt die Performance stark; nur 72 % der Handelsentscheidungen stimmen mit den Originaldaten überein: https://nbviewer.jupyter.org/github/twiecki/replicate_google_trends/tree/master/goog_repl.ipynb

### Regel
```
Daten: Google Trends über pytrends (inoffiziell, in der Quant-Lab-venv NICHT installiert, nicht getestet) [GEDÄCHTNIS],
       Region US, Tagesraster. Tagesdaten gibt es nur in Fenstern von wenigen Monaten (Fenster ca. 270 Tage [GEDÄCHTNIS]):
       überlappende Fenster abrufen, über die Überlappung verketten (Skalierungsfaktor aus Mittelwertverhältnis).
       Werte sind gesampelt: jede Reihe 5x unabhängig abrufen, Mittel bilden, EINFRIEREN und versionieren (Parquet).
Keyword-Korb B (vorab fixiert, keine Auswahl nach Performance; weicht von der Original-Konstruktion ab):
  recession, unemployment, bankruptcy, depression, inflation, stock market crash, layoffs, foreclosure, default, economic crisis
Preise: SPY (Datenstart 1993-01-29, lokal geprüft) bzw. ^GSPC (1927-12-30); Open und Close.
Täglich t (US-Handelstag; Trends-Tag = UTC-Tag, endet nach dem US-Schluss, deshalb keine Vorschau):
  dS[i,t] = ln(max(SVI[i,t],1)) - ln(max(SVI[i,t-1],1))
  z[i,t]  = (dS[i,t] - Mittel(dS[i,t-250..t-1])) / Std(dS[i,t-250..t-1])
  FEARS[t] = Mittel über i in B von z[i,t]
Signal: FEARS[t] >= 90. Perzentil von FEARS[t-250..t-1]
Ausführung: Kauf SPY zum Open von t+1; Verkauf zum Close von t+2. Überlappende Signale: Union der Haltefenster, nie mehr als 100 % Exposure.
Außerhalb der Fenster: Cash (RF aus French-Tagesdaten, bereits im Lab).
Kosten: 2 bp Round-Trip als Platzhalter (SPY); für UCITS-Ersatz echten Spread messen.
Tests: (a) Replikation 2004-2011, (b) Out-of-Sample 2012 bis heute, (c) Negativkontrolle mit 10 zufällig gezogenen,
       finanzfremden Keywords (gleiches Verfahren; Challet-Argument), (d) Zufallsfenster mit gleichem Exposure.
```

### Ehrliche Risiken
- Publikationsstichprobe 2004-2011 kurz (ca. 8 Jahre), kein Out-of-Sample-Beleg in meinen Quellen außer dem Snippet zur deutschen Brokerage-Studie.
- Abhängig von einer inoffiziellen Schnittstelle; Google kann Normalisierung ändern. Wiecki-Replikation zeigt Datenänderungen über die Zeit.
- Exposure nur wenige Tage im Jahr -> geringe Stichprobe, hoher Steueranteil pro Trade, Sharpe schwer von Zufall zu trennen.

## 5. Strategie 4: Stimmung/Wetter-Saisonalität (SAD), id `sad_winter_rotation`

### Evidenz
**Kamstra, Kramer, Levi (2003), "Winter Blues: A SAD Stock Market Cycle"**, AER 93(1), 324-343, https://papers.ssrn.com/abstract=208622 [SNIPPET]: Renditen hängen im Herbst/Winter mit der Tageslänge zusammen, stärker bei höheren Breiten, Südhalbkugel um sechs Monate verschoben. Ein weiteres Snippet nennt für Staatsanleihen ca. 80 Basispunkte höhere Monatsrenditen im Herbst als im Winter (Zuordnung zum Paper nicht verifiziert).
**Hirshleifer, Shumway (2003), "Good Day Sunshine: Stock Returns and the Weather"**, JF, https://scholarsarchive.byu.edu/facpub/9283 [SNIPPET]; Zahlen laut OSU-Pressemitteilung (https://news.osu.edu/sunny-days-at-the-stock-exchange-give-lift-to-market-study-says/): 26 Länder, 1982-1997, Unterschied bewölkt/sonnig ca. 9 Basispunkte pro Tag (24,8 % annualisiert). **Autoren selbst: Bei häufigem Handeln fressen bescheidene Kosten die Gewinne auf.** -> Daily-Sunshine-Handel ist laut Autoren nach Kosten nicht tragfähig; deshalb keine eigene Strategie.
**Gegenevidenz:** Kelly, Meschke (2010), "Sentiment and Stock Returns: The SAD Anomaly Revisited", J. Banking & Finance [SNIPPET; der von mir angegebene Link https://kuscholarworks.ku.edu/entities/publication/9b3f2e5c-cb73-4cd9-a39e-4c289cc1b997 stammt aus der Trefferliste, seine Zuordnung zu diesem Paper habe ich nicht per Abruf bestätigt]: SAD-Zeitreihenvorhersagen passen nicht zu den saisonalen Depressionsmustern der Bevölkerung; keine Beziehung zwischen SAD-Häufigkeit und Renditen. Weitere Snippets: Jacobsen/Marquering (Daten getrieben), eine Replikation New York, bei der der Sunshine-Effekt über die Zeit schwächer wird, und eine finnische Studie ohne Effekt in Helsinki (alle nur Snippets).

### Regel (Derivat aus qualitativer Beschreibung; Vorzeichen-Details vor Kodierung gegen das Original prüfen)
```
Hinweis: Das Rotationsschema unten ist MEINE Übersetzung der Aussage "Renditen im Herbst niedriger, im Winter höher; Südhalbkugel
6 Monate versetzt" in eine Handelsregel. Exakte Koeffizienten und Vorzeichen von SAD-Variable und Herbst-Dummy stammen aus dem
Gedächtnis und sind NICHT geprüft [GEDÄCHTNIS]. Vor Kodierung das Paper lesen.
Daten: ^GSPC (1927-12-30) bzw. SPY (1993-01-29) als Aktien; IEF (2002-07-30) bzw. ^IRX (1960-01-04) als Defensiv/Cash;
       Südhalbkugel: EWA (1996-03-18), EWZ (2000-07-14), EZA (2003-02-07), ^AORD (1984-08-03)  [alle LOKAL GEPRÜFT].
Nord-Regel (Kalender, kein Preissignal):
  Herbstphase = vom 23.09. bis 20.12. jedes Jahres.
  Signal und Ausführung: am Schlusskurs des letzten Handelstags <= 22.09.: Aktien verkaufen, in IEF (alternativ Cash) wechseln.
                         am Schlusskurs des letzten Handelstags <= 20.12.: zurück in Aktien.
  Sonst 100 % Aktien. Kein Hebel, keine Leerverkäufe.
Süd-Spiegel (Diskriminierungstest): gleiche Regel mit Herbstphase 23.03. bis 20.06. auf EWA/EWZ/EZA gegenüber deren Buy&Hold.
Hypothese: Nord-Regel schlägt Buy&Hold risikoadjustiert; Süd-Spiegel ebenfalls. Wenn nur die Nord-Regel wirkt
(Halloween-ähnlich) und die Süd-Spiegelung nicht, ist der Mechanismus nicht SAD.
Vergleich Pflicht: Halloween-Regel aus der Kalender-Familie (research/families/calendar.md), exposure-gematchte Zufallsfenster.
```

### Ehrliche Risiken
- Überlappt stark mit Halloween/"Sell in May" (Kalender-Familie). Kein neuer Edge, wenn beides dasselbe misst.
- Nach meinen Quellen: Mechanismus von mindestens einer Replikation bestritten (Kelly/Meschke); Sunshine-Effekt (Hirshleifer/Shumway) laut Autoren nach Kosten tot.
- Zwei Wechsel pro Jahr, Steuer pro Wechsel; mit UCITS-Ersatz zusätzlicher Spread.

## 6. Strategie 5: PEAD / Earnings-Announcement-Return in Large Caps, id `pead_ear_yahoo_surprise`

### Evidenz (überwiegend gegen Handelbarkeit)
- **Martineau (2022), "Rest in Peace Post-Earnings Announcement Drift"**, Critical Finance Review 11, 613-646, https://cfr.ivo-welch.info/published/papers/martineau2021rest.pdf [SNIPPET]: Bei Nicht-Microcaps verschwindet die Drift ab 2001 und ist seit 2006 nicht mehr vorhanden; bei Microcaps erst später. Erklärung: Dezimalisierung (2001) und schnelleres elektronisches Arbitrage-Trading (Regulation 2005). Nach Snippet nicht auf "Publikation" zurückgeführt.
- **Gegenposition** (UCLA Anderson Review [GELESEN], https://anderson-review.ucla.edu/is-post-earnings-announcement-drift-a-thing-again/): Zwei Arbeiten 2025 widersprechen Martineau: Dickerson, Julliard, Mueller, "The co-pricing factor zoo" (JFE, in press) und Hirshleifer, Peng, Wang, "News diffusion in social networks and stock market reactions" (RFS 38(3), 2025; t-Wert ca. 14). Ein Working Paper von Subrahmanyam (2025, Vorname und Titel laut Brief nicht angegeben) zeigt dagegen: US-Daten Feb 2001 bis Dez 2024, t-Wert 2,18 mit allen Aktien, **1,43 ohne Microcaps** (untere 20 % der NYSE-Marktkapitalisierung, ca. 3 % des Gesamtwerts). Dickerson et al. messen Drift über Announcement-Tag-Renditen (nicht über Gewinnüberraschung) und schließen Microcaps nicht aus. Renditegrößen, Sharpe, Nettozahlen nannte der Brief **nicht**.
- **Brandt, Kishore, Santa-Clara, Venkatachalam (2008), "Earnings Announcements are Full of Surprises"** (Original NICHT geöffnet); Zahlen über Quantpedia https://quantpedia.com/strategies/post-earnings-announcement-effect/ [SNIPPET]: EAR-Strategie 7,55 % abnormale Rendite pro Jahr, 1,3 Prozentpunkte mehr als SUE; kein Reversal nach 3 Quartalen; Kombination ca. 12,5 % pro Jahr. Quantpedia-Universum: NYSE/AMEX/NASDAQ ohne Finanzwerte und Versorger, Kurs >= 5 USD. Ob brutto oder netto: nicht geprüft.
- **Ng, Rusticus, Verdi (2008), "Implications of transaction costs for the post-earnings announcement drift"**, JAR, https://research.polyu.edu.hk/en/publications/implications-of-transaction-costs-for-the-post-earnings-announcem/ [SNIPPET]: Gewinne der PEAD-Strategie sinken durch Transaktionskosten deutlich; die Aktien mit der höchsten abnormalen Rendite haben die höchsten Kosten. Eine Sekundärquelle nennt für Chordia/Goyal/Sadka/Sadka/Shivakumar (2009), dass Kosten 70 bis 100 % des Bruttogewinns aufzehren: **unverifiziert, Original nicht gesehen**.
- **Chan, Jegadeesh, Lakonishok (1996), "Momentum Strategies"**, JF 51(5), 1681-1713, https://ideas.repec.org/a/bla/jfinan/v51y1996i5p1681-1713.html [SNIPPET]: Kursmomentum und Gewinnmomentum haben jeweils eigenen Vorhersagegehalt.
- Sekundärquelle eventstudytools (https://www.eventstudytools.com/earnings-announcements): Spread zwischen höchstem und niedrigstem SUE von ca. 5 % (1980er/90er) auf <= 3 % (späte 2010er). Nicht geprüft.

### Gratis-Daten-Pfad [LOKAL GEPRÜFT, Stichprobe]
`yfinance.Ticker(t).get_earnings_dates(limit=100)` liefert Zeitstempel (mit Uhrzeit, New-York-Zeit), `EPS Estimate`, `Reported EPS`, `Surprise(%)`. Test: AAPL, KO, JNJ -> je 100 Zeilen, erste gemeldete Zeile 2005-01 (AAPL) bzw. 2002-01 (KO, JNJ). Schätzung bei 87 bzw. 99 Zeilen gefüllt. **Warnung:** AAPL-Altwerte sind auf 0,01 USD gerundet (EPS Estimate 0,01, Reported 0,01, trotzdem "Surprise 42 %") -> Überraschungswerte bei kleinen EPS-Werten sind Rundungsrauschen. Daher EPS-Filter unten. Das ist eine **Analystenschätzungs-Überraschung** (wie I/B/E/S-Stil), nicht die saisonale Random-Walk-SUE der Originalpapiere. Nur 3 Ticker getestet; Abdeckung des gesamten Universums, Vollständigkeit und Stabilität der inoffiziellen Schnittstelle sind unbekannt. Survivorship: Punkt-in-der-Zeit-Indexzugehörigkeit ist nicht gratis; aktuelle S&P-500-Liste ist eine verzerrte Näherung.

### Regel
```
Universum: aktuelle S&P-500-Mitglieder (Survivorship-Verzerrung, ehrlich ausweisen), Kurs >= 5 USD zum Eventtag.
Ereignisse: get_earnings_dates(limit=100) je Ticker; behalte Zeilen mit Reported EPS und EPS Estimate vorhanden, und |EPS Estimate| >= 0.10 USD.
Ereignistag d0: Zeitstempel >= 16:00 ET -> d0 = nächster Handelstag; Zeitstempel < 16:00 ET -> d0 = gleicher Handelstag.
EAR = Summe über Tage d0-1, d0, d0+1 von (Close-zu-Close-Rendite Aktie minus Rendite SPY).
SURP = Surprise(%) in Prozent, winsorisiert bei 1./99. Perzentil des laufenden Pools.
Pool = alle Ereignisse der letzten 250 Handelstage VOR dem Signaltag (keine Zukunftsinformation).
Score = 0.5 * Perzentil(EAR im Pool) + 0.5 * Perzentil(SURP im Pool)
Signaltag s = Close von d0+1. Long, wenn Score >= 0.80; Short, wenn Score <= 0.20 (Long-Short-Forschungsvariante);
Retail-Variante: nur Long-Seite, gegen SPY gemessen (kein Hedge-Handel).
Ausführung: Open von d0+2. Halten 60 Handelstage, Verkauf zum Close des 60. Tages. Gleichgewicht je Position
 (1/N, N = Zahl offener Positionen je Seite, Deckel 100). Überlappende Positionen erlaubt.
Kosten: Basis 10 bp je Richtung (Large Caps, Platzhalter ohne Quelle), Stress 30 bp; Leihgebühr Short 0.5 % pro Jahr (Platzhalter).
Pflicht-Vergleiche: SPY Buy&Hold, Zufalls-Events (gleiche Anzahl, gleiche Haltedauer), Zeit-Split 2006 (vor/nach Martineau-Bruch).
Erwartung (vorab): Mittel der Nettoanomalie im S&P-500-Universum nach 2006 nahe null. Ergebnis ist Negativkontrolle.
```

### Ehrliche Risiken
- In investierbaren Large Caps ist die Drift nach Martineau seit 2006 nicht nachweisbar; die 2025er Gegenbefunde kommen laut Brief maßgeblich aus Microcaps (t 2,18 -> 1,43 ohne sie). Microcaps sind gerade die teuren Werte (Ng et al., SNIPPET).
- Gratis-Datenpfad ist inoffiziell, nur 3 Ticker getestet, mit Survivorship-Bias.

## 7. Geprüft und NICHT als Strategie aufgenommen

1. **Preis/Moat/Stanley "debt"-Wochenstrategie (Google Trends -> Dow)** [Regel nach Gedächtnis: wöchentlich, Δn = aktuelle Wochenabfrage minus Mittel der letzten Δt Wochen (Original Δt = 3), Short bei Anstieg, Long bei Rückgang]. Grund: Best-of-98-Keywords, Challet/Bel Hadj Ayed zeigen Keyword-Auswahl als größte Verzerrung, Replikationsnotebook mit späteren Daten reproduziert nur 72 % der Entscheidungen. Als Negativbefund im Eintrag 3 geführt.
2. **Tetlock (2007) Media-Pessimismus und Garcia (2013) "Sentiment during recessions"** (Papers im Suchergebnis gelistet, Volltexte nicht geöffnet: https://www.columbia.edu/~pt2238/papers/Tetlock_Media_Sentiment_JF.pdf, https://papers.ssrn.com/abstract=685145, https://leeds-faculty.colorado.edu/garcia/media_v33.pdf). Snippets: Tetlock nutzt die WSJ-Spalte "Abreast of the Market", Daten 1984-1999, hoher Pessimismus -> Abwärtsdruck mit Umkehr; Garcia nutzt NYT-Finanzspalten 1905-2005, Vorhersagbarkeit konzentriert in Rezessionen (bei einer Standardabweichung Newsschock ca. 12 bp Tagesrendite im Dow, Entwurfsfassung 2011). Ein praxisnaher Hinweis aus Snippets: nach Transaktionskosten verschwindet der Gewinn bei Aktien/Tagesdaten (Dow-Jones-News-Studie 1980-2004), bei Headline-Trading mit 10 bp Kosten (Masterarbeit), nur Strategien mit gedrosseltem Umschlag bleiben vorn (Commodity-Futures ca. 8,3 % p. a. nach Kosten, Währungen). **Warum nicht aufgenommen:** Die Originaltexte (WSJ, NYT) sind nicht gratis; ein GDELT-Ton-Proxy (gratis, laut [GEDÄCHTNIS] ab 2015 in nutzbarer Form) hat in meinen Quellen **keinen** Beleg. Garcias Rezessionsbedingung ist ex post gelabelt (NBER) und bräuchte eine Echtzeit-Variante.
3. **Sunshine täglich (Hirshleifer/Shumway)**: nach Aussage der Autoren selbst nach Kosten nicht tragfähig; Wetterdaten pro Börsenstadt (NOAA, gratis, aber aufwendig, nicht geprüft) für ein Signal, das die Autoren selbst als kostenfrei-nicht-handelbar einordnen.
4. **Wahl-Events aus Prediction Markets -> Aktien/Anleihen (Snowberg, Wolfers, Zitzewitz 2007, QJE; NBER WP 12073, https://www.nber.org/system/files/working_papers/w12073/w12073.pdf [SNIPPET])**: Intraday-Reaktion auf Wahl-Wahrscheinlichkeitsänderungen (2004: Bush-Präsidentschaft höhere Aktienpreise, Zinsen, Ölpreise, stärkerer Dollar); Langfrist-Aussage Republikaner-Präsident +2 bis 3 % Aktienbewertung. Es ist ein Identifikationsbeweis, keine wiederholbare Handelsregel (vier Beobachtungen pro Dekade).
5. **Prediction-Market-Preise als Makro-Signal für ETFs** (z. B. Rezessions-/Fed-Märkte auf Polymarket als Timing-Filter): Ich habe **keine** begutachtete Evidenz gefunden. Reine Hypothese.

## 8. Daten-Referenz (gratis) mit Prüfstatus

| Daten | Start | Status |
|---|---|---|
| ^GSPC (Yahoo) | 1927-12-30 | LOKAL GEPRÜFT (Daten bis 2026-10-09) |
| SPY | 1993-01-29 | LOKAL GEPRÜFT |
| TLT / IEF | 2002-07-30 | LOKAL GEPRÜFT |
| BIL | 2007-05-30 | LOKAL GEPRÜFT |
| ^IRX | 1960-01-04 | LOKAL GEPRÜFT |
| EWA | 1996-03-18 | LOKAL GEPRÜFT |
| EWZ | 2000-07-14 | LOKAL GEPRÜFT |
| EZA | 2003-02-07 | LOKAL GEPRÜFT |
| ^AORD | 1984-08-03 | LOKAL GEPRÜFT |
| ^VIX | 1990-01-02 | LOKAL GEPRÜFT |
| IWB | 2000-05-19 | LOKAL GEPRÜFT |
| French F-F_Research_Data_5_Factors_2x3 (monatlich) | 1963-07 | LOKAL GEPRÜFT (bis 2026-08) |
| French F-F_Momentum_Factor | 1927-01 | LOKAL GEPRÜFT |
| French Portfolios_Formed_on_INV / OP / AC / NI / VAR / RESVAR / BETA | 1963-07 | LOKAL GEPRÜFT (Namen und Spalten; Dezil-Spaltennamen z. B. "Lo 10", "2-Dec"/"Dec 2", "Hi 10" laut Ausgabe nur teilweise gesehen) |
| French 10_Portfolios_Prior_12_2 | 1927-01 | LOKAL GEPRÜFT (Spalten "Lo PRIOR" bis "Hi PRIOR") |
| Baker-Wurgler SENTIMENT.xlsx | SENT 1965-07, bis 2025-12 | LOKAL GEPRÜFT |
| yfinance get_earnings_dates | AAPL 2005, KO/JNJ 2002 (je 100 Zeilen) | Stichprobe LOKAL GEPRÜFT |
| Polymarket prices-history | Start je Markt | Dokumentation GELESEN, Praxis-Test fehlt |
| Kalshi öffentliche API | seit 2021 | NICHT geprüft |
| pytrends / Google Trends | 2004-01 | NICHT geprüft (Paket nicht installiert) |

## 9. Vorschlag für HYPOTHESEN.md (vor jedem Test eintragen)

- pm_favorite_maker: Erwartung: Netto-Mittelrendite pro Event > 0 im Band 0.70-0.95 bei konservativer Füllung. Abbruch: Mittelrendite <= 0 oder 95-%-Bootstrap-Intervall schließt 0 ein in der Teilstichprobe nach 2025-04. Danach keine weitere Variante auf denselben Daten.
- sentiment_state_anomaly: Erwartung: Spread (L-S in H-Monaten minus Nicht-H-Monaten) > 0 im Holdout 2008-02 bis 2025-12. Abbruch: Spread <= 0 oder |t| < 2 im Holdout.
- fears_reversal: Erwartung: Netto-Rendite der Signalfenster > exposure-gematchte Zufallsfenster im Holdout 2012+. Abbruch: Unterschied nicht signifikant oder Negativkontrolle (Zufalls-Keywords) ähnlich gut.
- sad_winter_rotation: Erwartung: Nord- UND Süd-Spiegel verbessern risikoadjustiert gegen Buy&Hold. Abbruch: Süd-Spiegel wirkungslos oder Nord-Effekt vollständig durch Halloween erklärt.
- pead_ear_yahoo_surprise: Erwartung: Netto-Spread nach 2006 ≈ 0 (Negativkontrolle). Abbruch bereits erfüllt, wenn das so eintritt; kein Live.

## 10. Quellenliste (alle URLs, die ich im Lauf gesehen habe und hier nutze)

Gelesen:
- https://www2.gwu.edu/~forcpgm/2026-001.pdf (Bürgi, Deng, Whelan)
- https://arxiv.org/abs/2602.19520 (Le)
- https://anderson-review.ucla.edu/is-post-earnings-announcement-drift-a-thing-again/
- https://arxiv.org/abs/1403.1715 (Challet, Bel Hadj Ayed)
- https://docs.polymarket.com/developers/CLOB/timeseries
- https://pages.stern.nyu.edu/~jwurgler/data/SENTIMENT.xlsx (lokal)

Nur Snippet / Trefferliste:
- https://www.nber.org/papers/w15923 (Snowberg, Wolfers)
- https://www.nber.org/system/files/working_papers/w12073/w12073.pdf (Snowberg, Wolfers, Zitzewitz)
- https://www.nber.org/papers/w16898 und https://nber.org/system/files/working_papers/w18231/w18231.pdf (Stambaugh, Yu, Yuan)
- https://pages.stern.nyu.edu/~jwurgler/papers/wurgler_baker_cross_section.pdf (Baker, Wurgler 2006; nur als Link gesehen)
- https://www3.nd.edu/~pgao/papers/FEARS_20131007.pdf und https://ideas.repec.org/a/oup/rfinst/v28y2015i1p1-32..html (Da, Engelberg, Gao 2015)
- https://rady.ucsd.edu/faculty/directory/engelberg/pub/portfolios/GOOGLE.pdf (Da, Engelberg, Gao 2011)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC3635219 (Preis, Moat, Stanley)
- https://nbviewer.jupyter.org/github/twiecki/replicate_google_trends/tree/master/goog_repl.ipynb (Wiecki)
- https://papers.ssrn.com/abstract=208622 und https://ideas.repec.org/a/aea/aecrev/v93y2003i1p324-343.html (Kamstra, Kramer, Levi)
- https://scholarsarchive.byu.edu/facpub/9283 und https://news.osu.edu/sunny-days-at-the-stock-exchange-give-lift-to-market-study-says/ (Hirshleifer, Shumway)
- https://kuscholarworks.ku.edu/entities/publication/9b3f2e5c-cb73-4cd9-a39e-4c289cc1b997 (vermutlich Kelly, Meschke; nicht bestätigt)
- https://cfr.ivo-welch.info/published/papers/martineau2021rest.pdf und https://ideas.repec.org/a/now/jnlcfr/104.00000122.html (Martineau)
- https://quantpedia.com/strategies/post-earnings-announcement-effect/ (Brandt et al. über Quantpedia)
- https://research.polyu.edu.hk/en/publications/implications-of-transaction-costs-for-the-post-earnings-announcem/ (Ng, Rusticus, Verdi)
- https://ideas.repec.org/a/bla/jfinan/v51y1996i5p1681-1713.html (Chan, Jegadeesh, Lakonishok)
- https://www.eventstudytools.com/earnings-announcements (Sekundärquelle)
- https://www.columbia.edu/~pt2238/papers/Tetlock_Media_Sentiment_JF.pdf, https://papers.ssrn.com/abstract=685145, https://leeds-faculty.colorado.edu/garcia/media_v33.pdf (Tetlock, Garcia)
- https://theses-dissertations.princeton.edu/entities/publication/d5708372-5ea3-4252-b669-7f9cee07387c (Princeton-Thesis, nur Snippet, nicht als Beleg genutzt)
