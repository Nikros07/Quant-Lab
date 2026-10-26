# Audit-Auftrag (gilt für jede Strategie-Familie)

Du prüfst fremden Code **nur lesend**. Verändere NIE Dateien in `strategies/`, `qlab/`, `tests/`, `scripts/`.
Du darfst nur schreiben: `docs/audits/<id>.md` (dein Bericht) und Wegwerf-Skripte im Scratchpad bzw. unter `docs/audits/_tmp/`.
Python nur über `.venv\Scripts\python.exe` im Projektordner `C:\Users\spide\Desktop\Projekte\Quant-Lab`. Antworte auf Deutsch, knapp.
Verboten: `--final` (Holdout ab 2023 bleibt zu), Netzwerk-Daten außer dem vorhandenen Cache/yfinance wie das Projekt es selbst nutzt, Zahlen erfinden.

## Schritte je Modul (`strategies/<id>.py`; gibt es ein `_etf`-Schwestermodul, prüfe beide, das zweite nur auf Unterschiede)

1. **Spezifikation laden.** In `research/strategie-kandidaten.json` Schlüssel `selected` den Eintrag mit `id == <id>` suchen (für `_etf`-Module den Basis-Eintrag). Felder `spec`, `sensitivity_variants`, `tickers`, `abort_criterion` lesen. Das ist die Soll-Vorgabe.
2. **Spezifikationstreue.** Punkt für Punkt gegen den Code (mit Zeilennummern) vergleichen: Instrumente/Universum, Signalregel, Schwellen, Zeitpunkt (Signal am Schluss t, Handel t+1 laut Engine-Vertrag), Haltedauer/Ausstieg, Cash-Behandlung, Hebel (nur falls Spezifikation es erlaubt), Kosten in `SPEC["cost_bps"]`, Varianten (höchstens 3, wie in `sensitivity_variants`, vorab festgelegt). Jede Abweichung = Befund.
3. **Look-ahead-Suche** im Code: Fenster, die in die Zukunft reichen (`center=True`, falsche `shift`-Richtung, `.iloc[-1]` über die ganze Reihe), Monats-/Wochenenden aus den Daten per `groupby(...).last()` statt `qlab.calendar.month_end_flags`/`week_end_flags` (verboten, weil Blick in die Zukunft), Normierung mit Vollstichprobe-Statistik, `ffill`/`bfill` über Lücken, Rückwärts-Auffüllen (`bfill`), Gewichte auf NaN-Kursen.
4. **Engine-Vertrag** prüfen (lies `qlab/engine.py`: Docstring von `run_backtest` und `check_causality`): Index von `weights()` = Signaltage, Summe der Gewichte je Zeile ≤ 1 (kein ungewollter Hebel/Short), keine Gewichte auf Titel ohne Kurs.
5. **Handrechnung.** Baue ein kleines synthetisches Panel (≥ 300 Tage, feste Zufallszahlen, `qlab.data.Panel(open, close)` wie in den vorhandenen Tests) und rechne die erwarteten Gewichte an 2–3 Entscheidungstagen unabhängig und von Hand/mit eigener kurzer Neuimplementierung nach. Vergleiche mit der Modul-Ausgabe. Abweichung = Befund.
6. **Tests.** `.venv\Scripts\python.exe -m pytest tests/test_<id>.py -q` ausführen. Lies die Tests: Prüfen sie echtes Verhalten oder sind sie tautologisch/zu lasch (z. B. nur `isinstance`, nur `>= 0`)? Schwache Tests als Befund (Schweregrad niedrig/mittel) melden.
7. **Lauf mit Kausalitätstest.** `.venv\Scripts\python.exe scripts\run_all.py --ids <id> --tag audit_<id> --n-boot 200` (nicht `--skip-causality`, nicht `--final`). Kausalitätstest muss bestehen. Notiere CAGR, Vol, Sharpe, MaxDD, Umsatz/Jahr aus der erzeugten `results/SUMMARY_audit_<id>.md`. Läuft der Befehl nicht (Fehler/Zeitüberschreitung), schreibe das ehrlich in den Bericht.
8. **Plausibilität.** Passen Rendite/Umsatz zur Spezifikation (z. B. erwartete Marktquote)? Auffällig hohe Sharpe (> 1,0) ist ein Warnsignal und muss erklärt werden.

## Bericht `docs/audits/<id>.md`

```
# Audit <id> — <Datum>
Urteil: BESTANDEN | BESTANDEN MIT HINWEISEN | DURCHGEFALLEN
Geprüfte Module/Tests/Läufe: ...
## Befunde
| Nr | Schwere (hoch/mittel/niedrig) | Datei:Zeile | Befund | Beleg (Zitat ≤ 2 Zeilen / Rechnung) | Korrekturvorschlag |
## Handrechnung (kurz: Eingabe, erwartet, Modul)
## Lauf-Kennzahlen (aus SUMMARY_audit_<id>.md)
## Offene Punkte / nicht geprüft
```

Schwere „hoch“ = verfälscht Rendite/Risiko wesentlich (Look-ahead, falsche Regel, Hebel ohne Spezifikation). Urteil DURCHGEFALLEN, sobald ein hoher Befund offen ist.
Behaupte nichts, was du nicht mit Zeile oder Rechnung belegt hast; „nicht geprüft“ ist erlaubt und besser als geraten.

## Rückmeldung an den Auftraggeber (letzte Nachricht)
Nur: Urteil, Anzahl Befunde je Schwere, die zwei wichtigsten Befunde in je einem Satz, Kennzahlen, Pfad zum Bericht.
