# Backtest-Ergebnis `audit_index_etf_ibs_rsi2_longonly_closenext` (bis 2022-12-31, Ausführung: close_next, Kosten ×1.0)

Läufe: **3** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 1.20e-05. PBO (gemeinsames Fenster ab 2004-01-01, 3 Läufe): **0.77**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.65, MaxDD -32.2%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| index_etf_ibs_rsi2_longonly:connors_rsi2 | reversal | 1993-11 | 29.1 | 5.7% | 6.5% | 0.56 | -15.0% | 0.10 (-0.23…0.40) | 0.290 | 39% | 0.997 | 7.7 | 0.31% |
| index_etf_ibs_rsi2_longonly:no_sma200 | reversal | 1993-11 | 29.1 | 7.6% | 12.0% | 0.49 | -38.0% | 0.03 (-0.18…0.29) | 0.410 | 39% | 0.991 | 33.6 | 1.34% |
| index_etf_ibs_rsi2_longonly | reversal | 1993-11 | 29.1 | 5.4% | 7.4% | 0.45 | -11.4% | -0.00 (-0.34…0.31) | 0.520 | 33% | 0.985 | 23.0 | 0.92% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| index_etf_ibs_rsi2_longonly:no_sma200 | 7.6% | 6.5% | 1.08% | 0.40 | 8.8% | -2.3% |
| index_etf_ibs_rsi2_longonly:connors_rsi2 | 5.7% | 5.1% | 0.68% | 0.46 | 8.8% | -3.7% |
| index_etf_ibs_rsi2_longonly | 5.4% | 4.7% | 0.67% | 0.36 | 8.8% | -4.1% |