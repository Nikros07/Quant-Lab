# Backtest-Ergebnis `dev_tom_spy_m2_p3` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **3** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 3.04e-04. PBO (gemeinsames Fenster ab 2004-01-01, 3 Läufe): **0.77**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tom_spy_m2_p3 | calendar | 1926-07 | 96.4 | 8.9% | 7.2% | 0.80 | -23.2% | 0.35 (0.19…0.57) | 0.000 | 45% | 1.000 | 12.0 | 0.48% |
| tom_spy_m2_p3:konservativ | calendar | 1926-07 | 96.4 | 8.1% | 7.6% | 0.67 | -28.8% | 0.22 (0.03…0.39) | 0.010 | 35% | 1.000 | 12.0 | 0.48% |
| tom_spy_m2_p3:tag_plus1 | calendar | 1926-07 | 96.4 | 4.0% | 3.7% | 0.25 | -14.4% | -0.19 (-0.38…0.07) | 0.920 | 24% | 0.547 | 12.0 | 0.48% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| tom_spy_m2_p3 | 8.9% | 7.8% | 1.15% | 0.64 | 9.6% | -1.8% |
| tom_spy_m2_p3:konservativ | 8.1% | 7.1% | 1.01% | 0.53 | 9.6% | -2.4% |
| tom_spy_m2_p3:tag_plus1 | 4.0% | 3.8% | 0.20% | 0.20 | 9.6% | -5.8% |