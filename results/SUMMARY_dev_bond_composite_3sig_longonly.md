# Backtest-Ergebnis `dev_bond_composite_3sig_longonly` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **4** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 3.59e-05. PBO (gemeinsames Fenster ab 2004-01-01, 4 Läufe): **0.15**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bond_composite_3sig_longonly:only_carry | gap_bonds_duration_curve_carry_mom_value | 1972-03 | 50.8 | 6.7% | 6.1% | 0.41 | -16.9% | 0.02 (-0.36…0.31) | 0.430 | 29% | 0.986 | 0.5 | 0.05% |
| bond_composite_3sig_longonly | gap_bonds_duration_curve_carry_mom_value | 1972-03 | 50.8 | 5.9% | 4.2% | 0.39 | -9.7% | 0.01 (-0.36…0.28) | 0.470 | 25% | 0.982 | 0.7 | 0.07% |
| bond_composite_3sig_longonly:only_trend | gap_bonds_duration_curve_carry_mom_value | 1972-03 | 50.8 | 5.5% | 4.9% | 0.26 | -14.1% | -0.13 (-0.57…0.22) | 0.750 | 22% | 0.874 | 2.0 | 0.20% |
| bond_composite_3sig_longonly:only_value | gap_bonds_duration_curve_carry_mom_value | 1972-03 | 50.8 | 5.3% | 5.1% | 0.22 | -20.8% | -0.17 (-0.49…0.15) | 0.790 | 27% | 0.800 | 0.4 | 0.04% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| bond_composite_3sig_longonly:only_carry | 6.7% | 5.6% | 1.09% | 0.22 | 9.3% | -3.7% |
| bond_composite_3sig_longonly | 5.9% | 5.0% | 0.93% | 0.18 | 9.3% | -4.4% |
| bond_composite_3sig_longonly:only_trend | 5.5% | 4.8% | 0.73% | 0.12 | 9.3% | -4.6% |
| bond_composite_3sig_longonly:only_value | 5.3% | 4.5% | 0.85% | 0.06 | 9.3% | -4.9% |