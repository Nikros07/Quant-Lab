# Backtest-Ergebnis `dev_nagel_vix_gated_sector_etf_reversal` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **4** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 6.33e-05. PBO (gemeinsames Fenster ab 2004-01-01, 4 Läufe): **0.20**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| nagel_vix_gated_sector_etf_reversal:vix_25 | reversal | 1998-12 | 24.0 | 6.5% | 6.8% | 0.72 | -14.0% | 0.38 (0.02…0.75) | 0.040 | 41% | 0.999 | 18.5 | 1.11% |
| nagel_vix_gated_sector_etf_reversal:vix_20 | reversal | 1998-12 | 24.0 | 6.8% | 7.9% | 0.67 | -14.0% | 0.32 (0.01…0.66) | 0.070 | 41% | 0.996 | 33.9 | 2.04% |
| nagel_vix_gated_sector_etf_reversal | reversal | 1998-12 | 24.0 | 5.2% | 7.3% | 0.50 | -19.9% | 0.16 (-0.12…0.52) | 0.220 | 41% | 0.969 | 36.8 | 2.21% |
| nagel_vix_gated_sector_etf_reversal:vix_30 | reversal | 1998-12 | 24.0 | 4.2% | 5.7% | 0.46 | -14.0% | 0.12 (-0.19…0.45) | 0.310 | 38% | 0.952 | 9.0 | 0.54% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| nagel_vix_gated_sector_etf_reversal:vix_20 | 6.8% | 5.7% | 1.08% | 0.53 | 5.9% | -0.2% |
| nagel_vix_gated_sector_etf_reversal:vix_25 | 6.5% | 5.6% | 0.96% | 0.58 | 5.9% | -0.3% |
| nagel_vix_gated_sector_etf_reversal | 5.2% | 4.4% | 0.83% | 0.39 | 5.9% | -1.5% |
| nagel_vix_gated_sector_etf_reversal:vix_30 | 4.2% | 3.7% | 0.50% | 0.37 | 5.9% | -2.2% |