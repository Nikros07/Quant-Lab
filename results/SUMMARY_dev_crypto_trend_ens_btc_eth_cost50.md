# Backtest-Ergebnis `dev_crypto_trend_ens_btc_eth_cost50` (bis 2022-12-31, Ausführung: open, Kosten ×2.5)

Läufe: **3** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 8.29e-06. PBO (gemeinsames Fenster ab 2004-01-01, 3 Läufe): **0.92**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| crypto_trend_ens_btc_eth:sma50_btc | crypto | 2015-09 | 7.3 | 84.1% | 54.0% | 1.37 | -61.6% | 0.78 (0.07…1.71) | 0.070 | 100% | 1.000 | 8.3 | 8.34% |
| crypto_trend_ens_btc_eth | crypto | 2015-09 | 7.3 | 59.2% | 41.4% | 1.30 | -51.1% | 0.70 (-0.06…1.58) | 0.070 | 100% | 1.000 | 7.7 | 7.66% |
| crypto_trend_ens_btc_eth:sma200_btc | crypto | 2015-09 | 7.3 | 79.7% | 58.8% | 1.27 | -70.6% | 0.67 (-0.19…1.56) | 0.090 | 100% | 1.000 | 2.7 | 2.73% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| crypto_trend_ens_btc_eth:sma50_btc | 84.1% | 67.4% | 16.69% | 1.19 | 8.6% | 58.8% |
| crypto_trend_ens_btc_eth:sma200_btc | 79.7% | 67.4% | 12.31% | 1.14 | 8.6% | 58.8% |
| crypto_trend_ens_btc_eth | 59.2% | 46.4% | 12.86% | 1.08 | 8.6% | 37.7% |