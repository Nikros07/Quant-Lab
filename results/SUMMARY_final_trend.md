# Backtest-Ergebnis `final_trend` (bis heute, Ausführung: open, Kosten ×1.0)

Läufe: **8** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 4.72e-06. PBO (gemeinsames Fenster ab 2004-01-01, 4 Läufe): **0.86**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 10.9%, Vol 18.5%, Sharpe 0.52, MaxDD -55.2%
- **60/40**: CAGR 8.6%, Vol 10.5%, Sharpe 0.68, MaxDD -32.5%
- **MKT**: CAGR 10.3%, Vol 17.5%, Sharpe 0.47, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| trend_ma12_us_equity_cash_etf:signal_tr | macro | 1993-12 | 32.8 | 10.5% | 12.9% | 0.65 | -22.5% | 0.13 (-0.06…0.34) | 0.125 | 43% | 1.000 | 0.6 | 0.11% |
| trend_ma12_us_equity_cash_etf | macro | 1993-01 | 33.7 | 10.0% | 12.7% | 0.62 | -22.5% | 0.10 (-0.13…0.30) | 0.225 | 38% | 1.000 | 0.6 | 0.12% |
| trend_ma12_us_equity_cash_etf:ma2_12 | macro | 1993-01 | 33.7 | 10.4% | 13.8% | 0.61 | -33.7% | 0.09 (-0.12…0.29) | 0.230 | 41% | 0.999 | 0.4 | 0.08% |
| trend_ma12_us_equity_cash_etf:sma10 | macro | 1993-01 | 33.7 | 9.7% | 12.6% | 0.61 | -25.1% | 0.08 (-0.14…0.28) | 0.270 | 40% | 0.999 | 0.7 | 0.14% |
| trend_ma12_us_equity_cash | macro | 1930-01 | 96.6 | 9.8% | 11.8% | 0.59 | -37.4% | 0.13 (-0.04…0.26) | 0.065 | 35% | 1.000 | 0.6 | 0.12% |
| trend_ma12_us_equity_cash:ma2_12 | macro | 1930-01 | 96.6 | 9.9% | 12.1% | 0.58 | -39.3% | 0.13 (-0.02…0.26) | 0.070 | 35% | 1.000 | 0.5 | 0.09% |
| trend_ma12_us_equity_cash:sma10 | macro | 1930-01 | 96.6 | 9.7% | 11.7% | 0.58 | -37.3% | 0.12 (-0.04…0.26) | 0.075 | 36% | 1.000 | 0.8 | 0.15% |
| trend_ma12_us_equity_cash:signal_tr | macro | 1930-01 | 96.6 | 9.5% | 12.1% | 0.55 | -45.7% | 0.10 (-0.07…0.24) | 0.105 | 31% | 1.000 | 0.7 | 0.13% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| trend_ma12_us_equity_cash_etf:signal_tr | 10.5% | 8.9% | 1.58% | 0.53 | 10.2% | -1.3% |
| trend_ma12_us_equity_cash_etf:ma2_12 | 10.4% | 8.9% | 1.55% | 0.50 | 10.3% | -1.4% |
| trend_ma12_us_equity_cash_etf | 10.0% | 8.5% | 1.50% | 0.51 | 10.3% | -1.7% |
| trend_ma12_us_equity_cash:ma2_12 | 9.9% | 8.5% | 1.40% | 0.47 | 9.8% | -1.3% |
| trend_ma12_us_equity_cash | 9.8% | 8.4% | 1.39% | 0.47 | 9.8% | -1.4% |
| trend_ma12_us_equity_cash:sma10 | 9.7% | 8.3% | 1.39% | 0.46 | 9.8% | -1.5% |
| trend_ma12_us_equity_cash_etf:sma10 | 9.7% | 8.2% | 1.47% | 0.49 | 10.3% | -2.0% |
| trend_ma12_us_equity_cash:signal_tr | 9.5% | 8.2% | 1.37% | 0.44 | 9.8% | -1.6% |