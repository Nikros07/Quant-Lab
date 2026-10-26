# Backtest-Ergebnis `dev_bond_composite_3sig_longonly_etf` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **4** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 6.84e-05. PBO (gemeinsames Fenster ab 2004-01-01, 4 Läufe): **0.06**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bond_composite_3sig_longonly_etf:only_value | gap_bonds_duration_curve_carry_mom_value | 2002-07 | 20.4 | 2.6% | 2.7% | 0.52 | -6.6% | 0.02 (-0.51…0.53) | 0.500 | 28% | 0.960 | 0.6 | 0.06% |
| bond_composite_3sig_longonly_etf:only_carry | gap_bonds_duration_curve_carry_mom_value | 2002-07 | 20.4 | 3.9% | 5.7% | 0.50 | -15.8% | -0.00 (-0.56…0.54) | 0.500 | 28% | 0.948 | 0.9 | 0.09% |
| bond_composite_3sig_longonly_etf | gap_bonds_duration_curve_carry_mom_value | 2002-07 | 20.4 | 3.0% | 3.8% | 0.49 | -8.7% | -0.01 (-0.51…0.46) | 0.520 | 28% | 0.944 | 1.3 | 0.13% |
| bond_composite_3sig_longonly_etf:only_trend | gap_bonds_duration_curve_carry_mom_value | 2002-07 | 20.4 | 2.2% | 4.7% | 0.24 | -10.0% | -0.26 (-0.81…0.20) | 0.810 | 28% | 0.683 | 4.2 | 0.42% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| bond_composite_3sig_longonly_etf:only_carry | 3.9% | 2.8% | 1.09% | 0.30 | 8.4% | -5.6% |
| bond_composite_3sig_longonly_etf | 3.0% | 2.2% | 0.82% | 0.27 | 8.4% | -6.2% |
| bond_composite_3sig_longonly_etf:only_value | 2.6% | 1.9% | 0.63% | 0.26 | 8.4% | -6.4% |
| bond_composite_3sig_longonly_etf:only_trend | 2.2% | 1.6% | 0.65% | 0.11 | 8.4% | -6.8% |