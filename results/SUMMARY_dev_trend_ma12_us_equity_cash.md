# Backtest-Ergebnis `dev_trend_ma12_us_equity_cash` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **4** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 1.09e-06. PBO (gemeinsames Fenster ab 2004-01-01, 4 Läufe): **0.72**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| trend_ma12_us_equity_cash | macro | 1930-01 | 92.9 | 9.6% | 11.8% | 0.58 | -37.4% | 0.14 (0.03…0.30) | 0.060 | 36% | 1.000 | 0.6 | 0.12% |
| trend_ma12_us_equity_cash:sma10 | macro | 1930-01 | 92.9 | 9.6% | 11.7% | 0.58 | -37.3% | 0.14 (0.03…0.32) | 0.060 | 38% | 1.000 | 0.7 | 0.15% |
| trend_ma12_us_equity_cash:ma2_12 | macro | 1930-01 | 92.9 | 9.6% | 12.0% | 0.57 | -39.3% | 0.13 (0.02…0.28) | 0.060 | 36% | 1.000 | 0.5 | 0.09% |
| trend_ma12_us_equity_cash:signal_tr | macro | 1930-01 | 92.9 | 9.3% | 12.1% | 0.54 | -45.7% | 0.11 (-0.02…0.27) | 0.110 | 31% | 1.000 | 0.7 | 0.13% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| trend_ma12_us_equity_cash | 9.6% | 8.3% | 1.35% | 0.46 | 9.3% | -1.1% |
| trend_ma12_us_equity_cash:ma2_12 | 9.6% | 8.2% | 1.35% | 0.46 | 9.3% | -1.1% |
| trend_ma12_us_equity_cash:sma10 | 9.6% | 8.2% | 1.36% | 0.46 | 9.3% | -1.1% |
| trend_ma12_us_equity_cash:signal_tr | 9.3% | 8.0% | 1.32% | 0.43 | 9.3% | -1.3% |