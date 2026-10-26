# Backtest-Ergebnis `audit_xtsmom_us_switch_longcash_etf` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **3** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 1.55e-06. PBO (gemeinsames Fenster ab 2004-01-01, 3 Läufe): **0.84**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| xtsmom_us_switch_longcash_etf:skip1 | gap_crossasset_bond_equity_leadlag_signals | 2003-07 | 19.4 | 6.5% | 13.0% | 0.46 | -33.7% | -0.04 (-0.31…0.26) | 0.590 | 33% | 0.973 | 2.1 | 0.09% |
| xtsmom_us_switch_longcash_etf | gap_crossasset_bond_equity_leadlag_signals | 2003-07 | 19.4 | 6.4% | 12.9% | 0.46 | -33.7% | -0.04 (-0.38…0.29) | 0.565 | 37% | 0.972 | 1.6 | 0.06% |
| xtsmom_us_switch_longcash_etf:tlt | gap_crossasset_bond_equity_leadlag_signals | 2003-07 | 19.4 | 6.2% | 13.8% | 0.42 | -33.7% | -0.08 (-0.44…0.30) | 0.665 | 37% | 0.962 | 1.9 | 0.08% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| xtsmom_us_switch_longcash_etf | 6.4% | 5.2% | 1.24% | 0.36 | 8.2% | -3.0% |
| xtsmom_us_switch_longcash_etf:skip1 | 6.5% | 5.1% | 1.37% | 0.36 | 8.2% | -3.1% |
| xtsmom_us_switch_longcash_etf:tlt | 6.2% | 5.0% | 1.19% | 0.34 | 8.2% | -3.2% |