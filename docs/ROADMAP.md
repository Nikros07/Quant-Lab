# Roadmap — ca. 8–10 Wochen

Prinzip: jede Phase endet mit einem Tor. Ohne bestandenes Tor kein nächster Schritt.
Aufwand ist grob; lieber langsam und sauber.

## Phase 0 — Fundament (Woche 1)
- [ ] Projekt-Repo + `.venv` + Git (Nick legt Remote auf github.com an)
- [ ] Bausteine aus NEMI **kopieren/portieren** (nicht verlinken): Backtest, Validation, Monte-Carlo, Daten
- [ ] Eye-of-Horus klonen, Quant-Engine und Look-ahead-Schutz anschauen
- [ ] Eine gemeinsame Datenbasis: Tageskurse ab ~2000 (SPY, QQQ, EFA, EWG, GLD, IEF, BIL, VIX …), dazu Dividenden. Cache als Datei im Repo/Branch
- [ ] Testbasis: bekannte Strategie (Buy&Hold SPY) muss exakt reproduzierbare Zahlen liefern
- **Tor:** Backtester reproduziert SPY-B&H und ETF-v4-Zahlen aus der Vault-Doku (±0,1 Pp.)

## Phase 1 — Prüfstand zuerst (Woche 1–2)
Der Prüfstand ist das eigentliche Produkt. Er muss streng sein, bevor wir Ideen testen.
- [ ] Kostenmodell (Spread je Instrument, Gebühren, Slippage) + deutsche Steuer (Abgeltung, Teilfreistellung ETF, Verlusttöpfe)
- [ ] Pflicht-Konkurrenten: SPY-B&H, 60/40, Zufalls-Strategie mit gleicher Handelsfrequenz
- [ ] Deflated Sharpe, PBO (Überanpassungs-Wahrscheinlichkeit), Bootstrap-Konfidenz
- [ ] Walk-forward + „Holdout, der nie angefasst wird" (z. B. letzte 2 Jahre, Zugriff nur einmal)
- [ ] Look-ahead-Test: absichtlich verseuchte Strategie muss auffallen
- **Tor:** Prüfstand erkennt eine bewusst eingebaute Schein-Strategie als Schein.

## Phase 2 — Fundament-Portfolio („Geld halten") (Woche 2–3)
Das sicherheitsorientierte Standbein, falls Phase 3–5 nichts bringen.
- [ ] ETF-Momentum v4 sauber neu aufsetzen, UCITS-Ticker (in Deutschland real handelbar)
- [ ] Varianten nur mit vorab festgelegtem Satz (max. ~10), Mehrfachtest-Korrektur
- [ ] Risiko-Ziel: Max-Drawdown deutlich kleiner als Markt, Rendite ≥ ~60/40
- **Tor:** nach Kosten+Steuer besser als 60/40 in Risiko-Rendite auf frischen Daten, oder ehrlich: „B&H-ETF ist die Antwort".

## Phase 3 — Hypothesen sammeln (Woche 3–4)
- [ ] Web-Research je Kandidat (Quellen in `research/`)
- [ ] Kandidaten (nur Ideen, noch nichts bestätigt):
  1. **Prediction-Market-Signale**: Polymarket-Wahrscheinlichkeiten (Rezession, Fed, Wahlen) als Regime-/Risk-On-Off-Signal für ETFs. Datenhistorie prüfen!
  2. **Ereignis-getriebenes Signal** (Eye of Horus): Wetter/Katastrophen → Rohstoffe/Versicherer. Wahrscheinlich schwaches Signal, aber kreativ und noch ungetestet auf echten Daten.
  3. **Regime-Erkennung** (Lücke aus NEMI): Wann funktioniert Trend, wann nicht? Vorab erkennbar machen.
  4. **Vorhersagefehler-Lernen / evolutionäre Auswahl** (Fly-Ideen, mit Deflated Sharpe) — nur falls billig.
  5. **Volatilitäts-Risikoprämie / Carry** (konservativ, gut dokumentiert).
  6. **Prediction-Market-Kalibrierung**: Wo liegt der Markt systematisch falsch (z. B. Favoriten-Longshot-Bias)? Hier ist Edge in kleinen Märkten plausibler als an liquiden Börsen.
- [ ] Je Hypothese Eintrag in `HYPOTHESEN.md` (Erwartung, Datenquelle, Kosten, Abbruchkriterium)
- **Tor:** Nick wählt 2–3 Hypothesen aus.

## Phase 4 — Hypothesen testen (Woche 4–6)
- [ ] Je Hypothese: Daten bauen, Test durch Prüfstand, Ergebnis in `LOGBUCH.md` (auch Negatives)
- [ ] Holdout bleibt unberührt bis zum Schluss
- **Tor:** Mindestens ein Kandidat besteht (Kosten, Walk-forward, Deflated Sharpe) — oder wir erklären „kein Edge" und gehen mit Phase 2 weiter.

## Phase 5 — Portfolio-Bau (Woche 6–7)
- [ ] Kombination aus Fundament + bestandener Strategie, Risikobudget, Positionsgröße, Drawdown-Bremse (rollierendes Fenster, **nicht** Allzeithoch — bekannter Bug)
- [ ] Monte-Carlo, Ruin-Risiko, Stress-Tests (2008, 2020, 2022)
- **Tor:** Holdout einmal geöffnet, Ergebnis ehrlich dokumentiert.

## Phase 6 — Ausführung + Papierhandel (Woche 7–10, läuft danach weiter)
- [ ] Täglicher Lauf über GitHub Actions (Muster von Fly-of-Wallstreet), Zustand auf eigenem Branch
- [ ] Alpaca-Papierkonto (kostenlos) **oder** eigenes Papier-Journal, falls Alpaca für UCITS nicht passt
- [ ] Monitoring: Abweichung Backtest ↔ Papier, Alarm bei Fehler/Datenlücke
- [ ] Betriebskosten dokumentieren (Ziel < 5 €/Monat)
- **Tor:** mindestens 4–8 Wochen Papier ohne Betriebsfehler, Abweichung zum Backtest erklärbar.

## Phase 7 — Freigabe für echtes Geld (Nick entscheidet)
- [ ] Checkliste aus `Nick\1. Projects\MT5-Master-Strategy\04-Validierung-Vor-Live-Schaltung.md` anpassen und abhaken
- [ ] Broker für Deutschland klären (Zugang, Kosten, UCITS, Steuerreporting)
- [ ] Start mit sehr kleinem Betrag, feste Verlustgrenze, Not-Aus-Regel
- **Tor:** Nick sagt ausdrücklich Ja.

## Entscheidungen (offen, brauchen Nick)
1. **Startkapital und Einzahlungsplan**: bestimmt, welche Strategien überhaupt handelbar sind (bei NEMI war 1.000 € zu klein).
2. **Märkte**: nur ETFs/Aktien, oder auch Prediction Markets (Polymarket-Zugang aus Deutschland rechtlich/steuerlich prüfen!).
3. **Name** und GitHub-Repo für das Projekt.
4. **Risiko-Toleranz**: maximaler Verlust, den Nick akzeptiert (z. B. −15 % / −25 %).
5. **Zeit pro Woche**, damit Phasen realistisch bleiben.
