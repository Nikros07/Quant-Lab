# Backtest-Ergebnis `dev_country_etf_xsmom_12_1` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **4** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 2.30e-04. PBO (gemeinsames Fenster ab 2004-01-01, 4 Läufe): **0.07**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| country_etf_xsmom_12_1:long_top5_sma10 | xsmom | 1997-03 | 25.8 | 6.7% | 15.4% | 0.38 | -39.5% | -0.03 (-0.32…0.21) | 0.620 | 48% | 0.731 | 2.3 | 0.23% |
| country_etf_xsmom_12_1:long_top5 | xsmom | 1997-03 | 25.8 | 5.7% | 21.4% | 0.28 | -62.9% | -0.13 (-0.35…0.03) | 0.870 | 38% | 0.554 | 2.6 | 0.26% |
| country_etf_xsmom_12_1 | xsmom | 1997-03 | 25.8 | -0.0% | 13.5% | -0.07 | -64.1% | -0.48 (-1.03…-0.08) | 0.940 | 24% | 0.049 | 5.3 | 0.53% |
| country_etf_xsmom_12_1:universe_ext | xsmom | 1997-03 | 25.8 | -0.4% | 13.9% | -0.10 | -68.0% | -0.50 (-1.03…-0.12) | 0.970 | 19% | 0.038 | 5.4 | 0.54% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| country_etf_xsmom_12_1:long_top5_sma10 | 6.7% | 5.6% | 1.01% | 0.31 | 7.5% | -1.9% |
| country_etf_xsmom_12_1:long_top5 | 5.7% | 4.9% | 0.86% | 0.24 | 7.5% | -2.7% |
| country_etf_xsmom_12_1 | -0.0% | -0.2% | 0.20% | -0.09 | 7.5% | -7.8% |
| country_etf_xsmom_12_1:universe_ext | -0.4% | -0.6% | 0.20% | -0.11 | 7.5% | -8.2% |