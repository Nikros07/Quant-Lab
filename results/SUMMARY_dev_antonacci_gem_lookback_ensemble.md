# Backtest-Ergebnis `dev_antonacci_gem_lookback_ensemble` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **4** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 2.25e-06. PBO (gemeinsames Fenster ab 2004-01-01, 3 Läufe): **0.99**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| antonacci_gem_lookback_ensemble | tactical | 2004-09 | 18.2 | 7.1% | 14.5% | 0.46 | -31.0% | -0.02 (-0.28…0.21) | 0.490 | 30% | 0.968 | 1.8 | 0.36% |
| antonacci_gem_lookback_ensemble:single_l12 | tactical | 2004-09 | 18.2 | 7.5% | 15.7% | 0.46 | -33.7% | -0.02 (-0.29…0.21) | 0.580 | 30% | 0.968 | 1.3 | 0.27% |
| antonacci_gem_lookback_ensemble:bond_ief | tactical | 2004-09 | 18.2 | 7.0% | 14.4% | 0.46 | -30.3% | -0.02 (-0.32…0.24) | 0.520 | 30% | 0.967 | 1.8 | 0.36% |
| antonacci_gem_lookback_ensemble:acwx | tactical | 2009-04 | 13.7 | 5.7% | 14.8% | 0.41 | -31.0% | -0.37 (-0.54…-0.22) | 1.000 | 0% | 0.923 | 2.0 | 0.39% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| antonacci_gem_lookback_ensemble:single_l12 | 7.5% | 6.2% | 1.29% | 0.38 | 8.0% | -1.7% |
| antonacci_gem_lookback_ensemble | 7.1% | 5.9% | 1.25% | 0.38 | 8.0% | -2.1% |
| antonacci_gem_lookback_ensemble:bond_ief | 7.0% | 5.8% | 1.24% | 0.38 | 8.0% | -2.2% |
| antonacci_gem_lookback_ensemble:acwx | 5.7% | 4.6% | 1.09% | 0.34 | 12.0% | -7.4% |