# Backtest-Ergebnis `dev_halloween_nov_apr_equity_etf` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **3** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 5.16e-05. PBO (gemeinsames Fenster ab 2004-01-01, 0 Läufe): **–**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| halloween_nov_apr_equity_etf:cash_ief | calendar | 2002-10 | 20.2 | 8.0% | 14.7% | 0.52 | -35.6% | 0.01 (-0.32…0.34) | 0.470 | 45% | 0.971 | 2.0 | 0.08% |
| halloween_nov_apr_equity_etf | calendar | 1993-04 | 29.7 | 7.5% | 13.4% | 0.45 | -34.6% | -0.01 (-0.21…0.18) | 0.540 | 44% | 0.971 | 1.0 | 0.04% |
| halloween_nov_apr_equity_etf:efa | calendar | 2006-04 | 16.7 | 4.6% | 15.6% | 0.30 | -33.9% | -0.17 (-0.45…0.10) | 0.810 | 21% | 0.794 | 1.0 | 0.04% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| halloween_nov_apr_equity_etf | 7.5% | 6.4% | 1.18% | 0.36 | 8.9% | -2.5% |
| halloween_nov_apr_equity_etf:cash_ief | 8.0% | 6.3% | 1.76% | 0.41 | 8.5% | -2.3% |
| halloween_nov_apr_equity_etf:efa | 4.6% | 3.7% | 0.81% | 0.25 | 7.5% | -3.8% |