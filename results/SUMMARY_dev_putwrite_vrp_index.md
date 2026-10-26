# Backtest-Ergebnis `dev_putwrite_vrp_index` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **4** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 6.57e-06. PBO (gemeinsames Fenster ab 2004-01-01, 3 Läufe): **0.00**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| putwrite_vrp_index:cost_025 | volpremium | 1996-08 | 26.4 | 7.6% | 15.8% | 0.42 | -37.2% | 0.00 (-0.15…0.17) | 0.450 | 50% | 0.974 | 0.0 | 0.00% |
| putwrite_vrp_index | volpremium | 1996-08 | 26.4 | 7.3% | 15.8% | 0.40 | -37.4% | -0.01 (-0.16…0.15) | 0.540 | 50% | 0.968 | 0.0 | 0.00% |
| putwrite_vrp_index:cost_100 | volpremium | 1996-08 | 26.4 | 6.8% | 15.8% | 0.37 | -37.6% | -0.05 (-0.19…0.12) | 0.680 | 50% | 0.955 | 0.0 | 0.00% |
| putwrite_vrp_index:from_2008 | volpremium | 2008-01 | 15.0 | 5.1% | 18.7% | 0.33 | -37.4% | -0.13 (-0.32…0.07) | 0.840 | 5% | 0.867 | 0.0 | 0.00% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| putwrite_vrp_index:cost_025 | 7.6% | 6.9% | 0.70% | 0.37 | 7.8% | -0.9% |
| putwrite_vrp_index | 7.3% | 6.6% | 0.69% | 0.36 | 7.8% | -1.2% |
| putwrite_vrp_index:cost_100 | 6.8% | 6.1% | 0.66% | 0.33 | 7.8% | -1.7% |
| putwrite_vrp_index:from_2008 | 5.1% | 4.3% | 0.71% | 0.29 | 6.9% | -2.5% |