# Backtest-Ergebnis `audit_crypto_trend_ens_btc_eth` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **3** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 2.11e-05. PBO (gemeinsames Fenster ab 2004-01-01, 3 Läufe): **0.89**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| crypto_trend_ens_btc_eth:sma50_btc | crypto | 2015-09 | 7.3 | 93.6% | 53.9% | 1.47 | -58.5% | 0.87 (0.05…1.69) | 0.040 | 100% | 1.000 | 8.3 | 3.33% |
| crypto_trend_ens_btc_eth | crypto | 2015-09 | 7.3 | 66.7% | 41.4% | 1.41 | -46.6% | 0.81 (-0.01…1.57) | 0.045 | 100% | 1.000 | 7.7 | 3.06% |
| crypto_trend_ens_btc_eth:sma200_btc | crypto | 2015-09 | 7.3 | 82.7% | 58.8% | 1.30 | -69.9% | 0.70 (-0.16…1.57) | 0.100 | 100% | 1.000 | 2.7 | 1.09% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| crypto_trend_ens_btc_eth:sma50_btc | 93.6% | 75.4% | 18.23% | 1.27 | 8.6% | 66.8% |
| crypto_trend_ens_btc_eth:sma200_btc | 82.7% | 69.9% | 12.82% | 1.16 | 8.6% | 61.3% |
| crypto_trend_ens_btc_eth | 66.7% | 52.5% | 14.26% | 1.17 | 8.6% | 43.8% |