# Backtest-Ergebnis `dev_country_value_cape_faber_proxy` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **4** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 8.66e-06. PBO (gemeinsames Fenster ab 2004-01-01, 0 Läufe): **–**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| country_value_cape_faber_proxy:avg60 | valuecarry | 2001-12 | 21.0 | 5.2% | 23.0% | 0.29 | -61.0% | -0.14 (-0.35…0.05) | 0.870 | 30% | 0.860 | 0.4 | 0.08% |
| country_value_cape_faber_proxy:june | valuecarry | 2006-06 | 16.5 | 2.9% | 23.3% | 0.20 | -59.0% | -0.28 (-0.47…-0.07) | 0.980 | 0% | 0.729 | 0.3 | 0.05% |
| country_value_cape_faber_proxy | valuecarry | 2006-12 | 16.0 | 2.8% | 23.1% | 0.20 | -57.6% | -0.26 (-0.46…-0.02) | 0.980 | 0% | 0.723 | 0.3 | 0.06% |
| country_value_cape_faber_proxy:quartile | valuecarry | 2006-12 | 16.0 | 2.4% | 23.7% | 0.18 | -56.9% | -0.28 (-0.47…-0.07) | 0.980 | 0% | 0.703 | 0.3 | 0.07% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| country_value_cape_faber_proxy:avg60 | 5.2% | 4.3% | 0.95% | 0.25 | 6.9% | -2.6% |
| country_value_cape_faber_proxy:june | 2.9% | 2.4% | 0.52% | 0.18 | 7.8% | -5.4% |
| country_value_cape_faber_proxy | 2.8% | 2.3% | 0.50% | 0.18 | 7.2% | -4.9% |
| country_value_cape_faber_proxy:quartile | 2.4% | 1.9% | 0.46% | 0.16 | 7.2% | -5.3% |