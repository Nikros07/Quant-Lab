# Pine-Lint: TrendFilter-Skripte (Pine v6)

Stand: 2026-10-21. Nur Lesezugriff, keine Dateien im Projekt geändert.
Geprüft: `deploy/tradingview/TrendFilter_MA12.pine` (v1.1, nur quergelesen), `TrendFilter_MA12_Alerts.pine`, `TrendFilter_MA12_Plus.pine`.

Hinweis zur Methode: Kein Compiler verfügbar. Die Befunde beruhen auf der Prüfung gegen Pine-v6-Regeln nach bestem Wissen. Alles, was nur in TradingView verifizierbar ist, steht als MÖGLICH mit Prüfschritt.

Sicherheitsstufen:
- SICHER: eindeutiger Verstoß gegen eine bekannte Pine-v6-Regel.
- MÖGLICH: unsicher oder Logikbefund; Prüfschritt angegeben.
- KEIN FEHLER: geprüft, in Ordnung (siehe Abschnitt unten).

Zusätzlich maschinell geprüft: keine Tabs, keine CR-Zeichen, keine NBSP. Alle Modus-Strings in der Plus-Datei sind byte-identisch (NFC, ü/ö/ä als Einzelzeichen). Alle Fortsetzungszeilen mit Einrückung ungleich 4 liegen innerhalb von Klammern.

## Zusammenfassung

| Datei | SICHER | MÖGLICH |
|---|---|---|
| TrendFilter_MA12.pine (v1.1) | 0 | 1 |
| TrendFilter_MA12_Alerts.pine | 0 | 3 |
| TrendFilter_MA12_Plus.pine | 0 | 2 |

Wichtigste Funde:
- **Kein SICHER-Fund.** Keine bekannte Pine-v6-Compiler-Regel verletzt.
- **Plus, Zeile 44/56:** Bei Täglich-Modi auf einem Intraday-Chart wird jede Kerze entschieden. Das kann Trades und Alarme pro Kerze auslösen.
- **Plus, Zeile 58–64 vs. Main, Zeile 39:** Bei na-Werten verhält sich Plus anders als die Basis (Plus behält den Zustand, Basis geht auf FLAT). Die Basis-Gleichheit ist damit nur bei gültigen Daten gegeben.
- **Alerts, Zeile 54:** `{{plot_0}}` ist nicht belegt, ob der data_window-Plot als plot_0 zählt. Im Alarmtext prüfen.

## Befunde

| Datei | Zeile | Zitat | Befund | Sicherheit | Korrekturvorschlag (nur Text, keine Dateiänderung) |
|---|---|---|---|---|---|
| TrendFilter_MA12.pine | 66–67 | `if not na(time[1]) and strategy.position_size == 0` / `cashFactor := cashFactor * math.pow(...)` | Die Cash-Zins-Anzeige (adjEquity) prüft die Position am Balkenschluss. Wegen `process_orders_on_close = false` füllt eine Order erst zur Eröffnung des Folgebalkens. Der Zins am Ein- bzw. Ausstiegstag wird dadurch um einen Balken verschoben. Nur Anzeige, keine Auswirkung auf Orders oder Tester-Equity. | MÖGLICH | Kein Pflichtfix. Optional im Kommentar vermerken, dass die Anzeige am Ein-/Ausstieg um einen Tag abweicht. |
| TrendFilter_MA12_Alerts.pine | 40, 54 | `plot(signalOn ? 1.0 : 0.0, "Monatssignal (1 = LONG, 0 = FLAT)", display = display.data_window)` / `message = "... {{plot_0}}"` | Der Alarmtext nutzt `{{plot_0}}`. Ob ein Plot mit `display.data_window` als plot_0 zählt und im Alarmtext den Wert liefert, ist nicht sicher. Falls nicht, steht im Alarm der Platzhalter wörtlich oder leer. | MÖGLICH | In TradingView den Alarm anlegen und die Vorschau prüfen: Der Text muss "1" oder "0" zeigen. Falls nicht: Signalwert direkt in den Text schreiben (z. B. per `str.tostring` in einer Variable, die `alertcondition` nicht unterstützt) oder den Platzhalter entfernen. Alternativ zwei getrennte Alarmbedingungen für LONG und FLAT (bereits vorhanden). |
| TrendFilter_MA12_Alerts.pine | 49–53 | `alertcondition(wentLong, ...)`, `alertcondition(wentFlat, ...)`, `alertcondition(isMonthEnd, ...)` | Die Auslösefrequenz ("Einmal pro Balkenschluss") wird nicht im Code festgelegt, sondern im Alarm-Dialog von TradingView. Ohne diese Einstellung kann ein Alarm pro Tick feuern. Die Logik selbst (nur bei Wechsel, nur bei Balkenschluss) ist im Code korrekt. | MÖGLICH | Kein Code-Fix. Im Alarm-Dialog "Einmal pro Balkenschluss" wählen und bei der Einrichtung dokumentieren. |
| TrendFilter_MA12_Alerts.pine | 32–37 | `wentLong = isMonthEnd and hasPrev and signalOn and not prevOn` / `if isMonthEnd` / `prevOn := signalOn` | Vergleich gegen den Vormonat ist korrekt (Berechnung vor dem Update). Bei einer Datenlücke am letzten Handelstag wird kein Monatsende erkannt, und der Vormonatszustand bleibt alt. Dann ist der nächste Wechsel-Alarm um einen Monat verschoben. | MÖGLICH | Nur bei Datenlücken relevant. Im Alarm-Dialog und in der Chart-Historie prüfen, ob alle Monatsenden vorhanden sind. Keine Code-Änderung zwingend. |
| TrendFilter_MA12_Plus.pine | 44, 56 | `decisionBar = mode == "Monatlich MA12 (geprüft)" ? isMonthEnd : mode == "Wöchentlich SMA40" ? isWeekEnd : true` / `bool decided = decisionBar and not na(sClose) and not na(sMa)` | Für die beiden Täglich-Modi ist `decisionBar` immer `true`, unabhängig vom Chart-Takt. Auf einem Intraday-Chart wird dann jede Kerze entschieden. Die Tagesdaten aus `request.security("D")` können dort noch unfertig sein. Das kann Zustandswechsel, Alarme und Trades pro Kerze auslösen. Die Kopfkommentare sprechen von "Tages-Takten jeder Balken", also ist die Absicht der Tageschart. | MÖGLICH | Für Täglich-Modi `decisionBar` an `timeframe.isdaily` koppeln (z. B. `: mode == "Täglich ..." ? timeframe.isdaily`) oder die Nutzung auf Tageschart im Kopfkommentar und in der Infotabelle verbindlich machen und bei Intraday eine Warnung ausgeben. |
| TrendFilter_MA12_Plus.pine | 58–64 vs. TrendFilter_MA12.pine 39, 41–45 | Plus: `if decided` (keine Aktualisierung bei na) / Basis: `signalOn = not na(mClose) and not na(mMa) and mClose >= mMa` (na zählt als FLAT) | Abweichung der Entscheidungslogik bei fehlenden Werten. In der Basis schließt ein Monatsende mit na-Wert die Position (FLAT). In Plus bleibt der Zustand. Die Gleichheit "Band 0 = Basis" gilt daher nur bei vollständigen Daten. Praktisch nur bei Datenlücken mitten in der Historie. | MÖGLICH | Für Gleichheit: in Plus bei decisionBar mit na-Werten `stateOn := false` setzen (wie Basis), oder in der Basis na als "Zustand halten" definieren. Entscheidung bewusst treffen und im Kopfkommentar festhalten. |

Ausdrücklich nicht gefunden: Keine SICHER-Befunde. Keine Verletzung von `when=`, `alertcondition` in strategy(), `plot`/`bgcolor` in lokalen Blöcken, `strategy.close` ohne Ordner-ID, Zahl-zu-bool-Konvertierung oder Table-Index-Überlauf.

## Geprüfte Punkte ohne Befund (KEIN FEHLER)

Checkliste je Skript (Nummern wie in der Aufgabe):

1. `//@version=6` in Zeile 1: alle drei Dateien. Parameter von `strategy()` (default_qty_type, default_qty_value, commission_type, commission_value, pyramiding, calc_on_every_tick, process_orders_on_close, initial_capital, overlay) gültig. `indicator()` mit overlay und max_labels_count gültig.
2. v6-Änderungen: kein `when=` in strategy-Aufrufen (grep leer). `strategy.close("Long", comment = ...)` mit String-ID. Alle `if`-Bedingungen sind bool (`isMonthEnd`, `showTable and barstate.islast`, `decided`, `hasPrev and stateOn != prevOn`, `wentLong`). Keine Ganzzahl-Division mit erwarteter Ganzzahl (Plus Z. 97 nutzt float korrekt).
3. `request.security`: Signatur (Symbol, Zeitrahmen, Tupel-Ausdruck, `lookahead = barmerge.lookahead_off`) korrekt in allen Aufrufen. Alle auf Skriptebene. Symbolparameter ist `sigSym` (string aus `input.symbol` bzw. `syminfo.tickerid`). Tupel-Rückgabe `[a, b] = ...` korrekt, auch mit `ta.sma`-Ausdrücken. Plus: 4 Aufrufe (unter dem Limit von 40).
4. `alertcondition` nur in `indicator()`-Datei (Alerts), in den beiden `strategy()`-Dateien kein `alertcondition` (grep). `alert(..., alert.freq_once_per_bar_close)` in Main und Plus korrekt. Alerts-Argumente (condition bool, title, message) gültig.
5. `plot`, `bgcolor`, `plot` in Plus und Alerts auf Skriptebene, nicht in if/for-Blöcken. `table.new` nur in `if ... barstate.islast` mit `var`. Zell-Indizes geprüft:
   - Main Infotabelle `table.new(..., 2, 4)`: alle `table.cell` mit Spalte 0–1, Zeile 0–3. In Ordnung.
   - Main Prüftabelle `table.new(..., 4, 7)`: Zeile 0 Kopf, Schleife r = 1..6, Spalten 0–3. In Ordnung.
   - Plus `table.new(..., 2, 7)`: Zeilen 0–6, Spalten 0–1, alle Zellen im Bereich. In Ordnung.
   - `table.cell`-Reihenfolge (Tabelle, Spalte, Zeile, Text) korrekt.
6. Deklarationen: `var array<float> = array.new<float>()`, `var array<string> = array.new<string>()`, `var float cashFactor = 1.0`, `var int firstTime = time`. Zuweisungen mit `:=` nach `var`-Deklaration (`cashFactor`, `prevOn`, `hasPrev`, `stateOn`). Kein Shadowing eingebauter Namen (close, high, low, open, time). Alle Variablen verwendet.
7. Eingaben: `input.int(12, "...", minval = 2, maxval = 60)`, `input.bool`, `input.symbol("SP:SPX", ...)`, `input.float(..., step = 0.5)` gültig. `input.string` in Plus: Standardwert "Monatlich MA12 (geprüft)" ist identisch mit dem ersten Eintrag in `options` (Bytevergleich). Alle Modus-Vergleiche (`mode == "..."`) sind byte-identisch mit den Optionen.
8. Zeit und Strings: `time_close("M")` / `time_close("W")` gültig. `str.format_time(time, "yyyy-MM")` gültig. `str.tostring(x, "#.##")`, `str.tostring(x, "#.#")` gültig. `math.pow`, `math.round` mit gültigen Typen. Keine `ta.*`-Aufrufe in bedingten Blöcken (alle `ta.sma` stehen im Tupel auf Skriptebene).
9. Einrückung: `if`/`for`-Blöcke mit 4 Leerzeichen. Fortsetzungszeilen (Zeilen 20–22, 48–49 in Main; 23–25, 28 in Plus; 50, 52, 54 in Alerts) liegen in offenen Klammern, daher unkritisch.
10. Logik der Plus-Datei:
    - Zustandsmaschine `stateOn` wird nur in `if decided` aktualisiert. Kein Order-Aufruf außerhalb des Entscheidungsblocks.
    - Die vier Modi holen ihre Werte korrekt: Monatlich (mClose/mMa aus "M", SMA12), Wöchentlich (wClose/wMa aus "W", SMA40), Täglich SMA200 (dClose/dMa aus "D"), Kreuzung (dFast/dSlow aus "D", SMA50/SMA200).
    - Hysterese: `>=` für obere Schwelle, `<` für untere Schwelle, Zustand bleibt dazwischen. Korrekt.
    - Einstieg und Ausstieg nur bei Zustandswechsel (`strategy.position_size`-Abfrage). Korrekt.
    - Base-Modus mit Puffer 0 ergibt denselben Vergleich (`>=`) und dieselbe Monatsende-Bedingung wie die Basisdatei. Abweichung nur bei na-Werten (siehe Befund oben).
11. Logik der Alerts-Datei: Alarme nur bei Zustandswechsel (`wentLong`, `wentFlat`), einmal pro Monatsende. Der Monatssignal-Alarm feuert nur auf `isMonthEnd`, nicht in jeder Kerze. Der erste Monat im Chart erzeugt keinen Wechsel-Alarm (hasPrev). Korrekt.

Weitere geprüfte Punkte:
- Main: `isMonthEnd = time_close == time_close("M")` ist das übliche Muster; in v1.1 in TradingView geprüft.
- Main: `adjEquity = strategy.equity * cashFactor` ist mathematisch korrekt (Produkt der Zinsfaktoren über die Cash-Phasen). Nur der Zeitpunkt der Zinszählung ist betroffen (siehe Befund oben).
- Main: Infotabelle und Prüftabelle: Zellen mit `na` werden abgefangen (`na(fClose) ? "-" : ...`).
- Plus: `elapsedYears` und `strategy.closedtrades / elapsedYears` mit Guard `> 0`.
- Plus: `alert()` nur bei Zustandswechsel (`hasPrev and stateOn != prevOn`), wie im Kopfkommentar beschrieben.

## Prüfschritte in TradingView (kein Compiler hier)

1. Alle drei Dateien neu kompilieren (Pine Editor, "Zu Chart hinzufügen"). Achtung: Plus und Alerts sind bisher nie kompiliert worden. Erster Compile-Lauf ist die eigentliche Probe.
2. Alerts: Alarm-Vorschau prüfen (Text bei `{{plot_0}}`, Frequenz "Einmal pro Balkenschluss").
3. Plus: auf einem Intraday-Chart (z. B. 1h) einen Täglich-Modus laden und prüfen, ob Trades oder Zustandswechsel pro Kerze auftreten. Falls ja, Fix nach Befund anwenden.
4. Plus: Basis-Modus (Monatlich) mit Puffer 0 gegen TrendFilter_MA12.pine auf SP:SPX vergleichen; Trades und Monatsende-Werte müssen übereinstimmen.
