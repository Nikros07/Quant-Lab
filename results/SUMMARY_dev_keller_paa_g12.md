# Backtest-Ergebnis `dev_keller_paa_g12` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **4** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 1.82e-06. PBO (gemeinsames Fenster ab 2004-01-01, 4 Läufe): **0.84**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| keller_paa_g12 | tactical | 2008-05 | 14.6 | 5.9% | 8.4% | 0.66 | -14.3% | 0.16 (-0.28…0.55) | 0.270 | 5% | 0.992 | 3.1 | 0.61% |
| keller_paa_g12:sleeves3 | tactical | 2008-05 | 14.6 | 5.7% | 8.3% | 0.65 | -14.2% | 0.15 (-0.33…0.53) | 0.290 | 5% | 0.991 | 3.2 | 0.65% |
| keller_paa_g12:top4 | tactical | 2008-05 | 14.6 | 5.9% | 9.0% | 0.63 | -14.6% | 0.12 (-0.32…0.45) | 0.300 | 5% | 0.989 | 3.4 | 0.68% |
| keller_paa_g12:breadth4 | tactical | 2008-05 | 14.6 | 5.2% | 7.9% | 0.62 | -13.8% | 0.11 (-0.40…0.55) | 0.340 | 5% | 0.988 | 3.1 | 0.62% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| keller_paa_g12:top4 | 5.9% | 4.7% | 1.26% | 0.49 | 7.9% | -3.2% |
| keller_paa_g12 | 5.9% | 4.7% | 1.25% | 0.52 | 7.9% | -3.2% |
| keller_paa_g12:sleeves3 | 5.7% | 4.5% | 1.23% | 0.51 | 7.9% | -3.4% |
| keller_paa_g12:breadth4 | 5.2% | 4.1% | 1.14% | 0.47 | 7.9% | -3.8% |