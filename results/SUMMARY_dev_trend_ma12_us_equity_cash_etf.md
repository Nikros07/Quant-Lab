# Backtest-Ergebnis `dev_trend_ma12_us_equity_cash_etf` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **4** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 6.63e-07. PBO (gemeinsames Fenster ab 2004-01-01, 4 Läufe): **0.90**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| trend_ma12_us_equity_cash_etf:signal_tr | macro | 1993-12 | 29.0 | 9.5% | 13.0% | 0.60 | -22.5% | 0.14 (-0.07…0.35) | 0.160 | 49% | 0.999 | 0.6 | 0.11% |
| trend_ma12_us_equity_cash_etf | macro | 1993-01 | 29.9 | 9.4% | 12.8% | 0.60 | -22.5% | 0.13 (-0.08…0.31) | 0.170 | 43% | 0.999 | 0.5 | 0.11% |
| trend_ma12_us_equity_cash_etf:sma10 | macro | 1993-01 | 29.9 | 9.2% | 12.6% | 0.59 | -23.0% | 0.12 (-0.06…0.29) | 0.150 | 45% | 0.999 | 0.7 | 0.13% |
| trend_ma12_us_equity_cash_etf:ma2_12 | macro | 1993-01 | 29.9 | 9.5% | 13.7% | 0.57 | -33.7% | 0.10 (-0.07…0.28) | 0.140 | 47% | 0.999 | 0.4 | 0.08% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| trend_ma12_us_equity_cash_etf:signal_tr | 9.5% | 8.1% | 1.42% | 0.49 | 8.8% | -0.7% |
| trend_ma12_us_equity_cash_etf:ma2_12 | 9.5% | 8.1% | 1.39% | 0.47 | 8.9% | -0.8% |
| trend_ma12_us_equity_cash_etf | 9.4% | 8.0% | 1.39% | 0.49 | 8.9% | -0.9% |
| trend_ma12_us_equity_cash_etf:sma10 | 9.2% | 7.9% | 1.38% | 0.48 | 8.9% | -1.0% |