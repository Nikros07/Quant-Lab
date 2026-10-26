# Backtest-Ergebnis `dev_static_multifactor_equal_risk` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **2** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 1.00e-04. PBO (gemeinsames Fenster ab 2004-01-01, 0 Läufe): **–**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| static_multifactor_equal_risk:equal_weight | factors | 1966-06 | 56.5 | 9.6% | 7.6% | 0.68 | -59.9% | 0.27 (-0.18…0.71) | 0.160 | 50% | 1.000 | 0.3 | 1.60% |
| static_multifactor_equal_risk | factors | 1966-06 | 56.5 | 8.8% | 7.2% | 0.61 | -49.5% | 0.20 (-0.17…0.59) | 0.160 | 48% | 1.000 | 0.3 | 1.96% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| static_multifactor_equal_risk:equal_weight | 9.6% | 8.0% | 1.56% | 0.47 | 9.8% | -1.7% |
| static_multifactor_equal_risk | 8.8% | 7.0% | 1.72% | 0.37 | 9.8% | -2.7% |