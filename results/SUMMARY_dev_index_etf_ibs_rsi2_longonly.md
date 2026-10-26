# Backtest-Ergebnis `dev_index_etf_ibs_rsi2_longonly` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **3** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 1.43e-06. PBO (gemeinsames Fenster ab 2004-01-01, 3 Läufe): **0.93**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| index_etf_ibs_rsi2_longonly:connors_rsi2 | reversal | 1993-11 | 29.1 | 6.5% | 6.7% | 0.65 | -14.9% | 0.19 (-0.10…0.51) | 0.190 | 41% | 1.000 | 7.7 | 0.31% |
| index_etf_ibs_rsi2_longonly | reversal | 1993-11 | 29.1 | 6.9% | 7.4% | 0.64 | -15.6% | 0.19 (-0.07…0.43) | 0.160 | 37% | 1.000 | 23.1 | 0.92% |
| index_etf_ibs_rsi2_longonly:no_sma200 | reversal | 1993-11 | 29.1 | 9.3% | 12.3% | 0.61 | -32.8% | 0.15 (-0.06…0.40) | 0.140 | 43% | 0.999 | 33.7 | 1.35% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| index_etf_ibs_rsi2_longonly:no_sma200 | 9.3% | 7.9% | 1.41% | 0.50 | 8.8% | -0.9% |
| index_etf_ibs_rsi2_longonly | 6.9% | 5.9% | 0.94% | 0.52 | 8.8% | -2.8% |
| index_etf_ibs_rsi2_longonly:connors_rsi2 | 6.5% | 5.6% | 0.82% | 0.52 | 8.8% | -3.2% |