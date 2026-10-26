# Backtest-Ergebnis `dev_sector_etf_top3_12m` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **4** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 4.46e-06. PBO (gemeinsames Fenster ab 2004-01-01, 4 Läufe): **0.41**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sector_etf_top3_12m:sma10 | xsmom | 1927-07 | 95.4 | 12.2% | 13.7% | 0.68 | -49.1% | 0.25 (0.12…0.39) | 0.000 | 61% | 1.000 | 2.2 | 0.22% |
| sector_etf_top3_12m | xsmom | 1927-07 | 95.4 | 14.0% | 17.7% | 0.66 | -72.3% | 0.22 (0.15…0.29) | 0.000 | 92% | 1.000 | 2.3 | 0.23% |
| sector_etf_top3_12m:combo | xsmom | 1927-07 | 95.4 | 13.9% | 17.8% | 0.65 | -75.0% | 0.21 (0.13…0.28) | 0.000 | 87% | 1.000 | 2.9 | 0.29% |
| sector_etf_top3_12m:hold_buffer | xsmom | 1927-07 | 95.4 | 13.1% | 18.0% | 0.60 | -75.7% | 0.17 (0.09…0.23) | 0.000 | 85% | 1.000 | 1.1 | 0.11% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| sector_etf_top3_12m | 14.0% | 11.8% | 2.21% | 0.54 | 9.4% | 2.4% |
| sector_etf_top3_12m:combo | 13.9% | 11.6% | 2.21% | 0.53 | 9.4% | 2.2% |
| sector_etf_top3_12m:hold_buffer | 13.1% | 11.1% | 2.00% | 0.50 | 9.4% | 1.7% |
| sector_etf_top3_12m:sma10 | 12.2% | 10.4% | 1.82% | 0.56 | 9.4% | 1.0% |