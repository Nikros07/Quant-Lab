# Backtest-Ergebnis `dev_wml_volscaled_ff` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **4** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 9.59e-05. PBO (gemeinsames Fenster ab 2004-01-01, 4 Läufe): **0.03**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| wml_volscaled_ff | xsmom | 1930-01 | 92.9 | 7.8% | 13.8% | 0.39 | -79.9% | -0.04 (-0.31…0.30) | 0.570 | 43% | 0.985 | 1.0 | 6.77% |
| wml_volscaled_ff:cap_1 | xsmom | 1930-01 | 92.9 | 7.5% | 12.7% | 0.39 | -74.3% | -0.05 (-0.32…0.30) | 0.560 | 43% | 0.983 | 0.7 | 4.90% |
| wml_volscaled_ff:vol_target_19 | xsmom | 1930-01 | 92.9 | 8.0% | 21.4% | 0.33 | -94.8% | -0.11 (-0.37…0.23) | 0.770 | 47% | 0.935 | 1.6 | 10.58% |
| wml_volscaled_ff:static_w1 | xsmom | 1930-01 | 92.9 | -2.3% | 32.4% | 0.06 | -100.0% | -0.38 (-0.65…-0.08) | 0.990 | 39% | 0.150 | 1.2 | 8.19% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| wml_volscaled_ff:vol_target_19 | 8.0% | 6.7% | 1.36% | 0.27 | 9.3% | -2.6% |
| wml_volscaled_ff | 7.8% | 6.7% | 1.17% | 0.31 | 9.3% | -2.7% |
| wml_volscaled_ff:cap_1 | 7.5% | 6.5% | 0.96% | 0.32 | 9.3% | -2.8% |
| wml_volscaled_ff:static_w1 | -2.3% | -2.4% | 0.08% | 0.06 | 9.3% | -11.7% |