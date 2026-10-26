# Backtest-Ergebnis `audit_xtsmom_us_switch_longcash` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **3** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 9.30e-07. PBO (gemeinsames Fenster ab 2004-01-01, 3 Läufe): **0.95**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| xtsmom_us_switch_longcash | gap_crossasset_bond_equity_leadlag_signals | 1981-01 | 41.9 | 10.3% | 11.7% | 0.59 | -33.8% | 0.11 (-0.15…0.38) | 0.220 | 41% | 1.000 | 0.9 | 0.04% |
| xtsmom_us_switch_longcash:tlt | gap_crossasset_bond_equity_leadlag_signals | 1981-01 | 41.9 | 10.3% | 12.3% | 0.56 | -33.8% | 0.09 (-0.17…0.35) | 0.315 | 42% | 1.000 | 0.9 | 0.04% |
| xtsmom_us_switch_longcash:skip1 | gap_crossasset_bond_equity_leadlag_signals | 1981-01 | 41.9 | 10.0% | 11.8% | 0.56 | -33.8% | 0.08 (-0.17…0.32) | 0.285 | 35% | 1.000 | 1.0 | 0.04% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| xtsmom_us_switch_longcash | 10.3% | 8.8% | 1.54% | 0.46 | 10.5% | -1.7% |
| xtsmom_us_switch_longcash:tlt | 10.3% | 8.8% | 1.53% | 0.44 | 10.5% | -1.8% |
| xtsmom_us_switch_longcash:skip1 | 10.0% | 8.5% | 1.52% | 0.43 | 10.5% | -2.0% |