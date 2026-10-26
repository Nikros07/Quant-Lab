# Backtest-Ergebnis `dev_eq_voltarget_ewma_harvey` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **4** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 2.19e-07. PBO (gemeinsames Fenster ab 2004-01-01, 4 Läufe): **0.24**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| eq_voltarget_ewma_harvey:vol_10 | volmgmt | 1928-01 | 95.0 | 8.4% | 10.0% | 0.55 | -46.9% | 0.11 (0.03…0.21) | 0.020 | 20% | 1.000 | 0.5 | 0.02% |
| eq_voltarget_ewma_harvey | volmgmt | 1928-01 | 95.0 | 8.9% | 11.2% | 0.54 | -55.4% | 0.11 (0.03…0.19) | 0.010 | 19% | 1.000 | 0.4 | 0.02% |
| eq_voltarget_ewma_harvey:cap_1_5 | volmgmt | 1928-01 | 95.0 | 9.4% | 12.5% | 0.53 | -55.4% | 0.10 (0.01…0.20) | 0.050 | 41% | 1.000 | 1.1 | 0.04% |
| eq_voltarget_ewma_harvey:hl_40 | volmgmt | 1928-01 | 95.0 | 8.8% | 11.4% | 0.53 | -53.5% | 0.10 (0.02…0.17) | 0.020 | 18% | 1.000 | 0.2 | 0.01% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| eq_voltarget_ewma_harvey:cap_1_5 | 9.4% | 7.8% | 1.53% | 0.42 | 9.3% | -1.5% |
| eq_voltarget_ewma_harvey:hl_40 | 8.8% | 7.8% | 1.04% | 0.44 | 9.3% | -1.6% |
| eq_voltarget_ewma_harvey | 8.9% | 7.7% | 1.18% | 0.44 | 9.3% | -1.6% |
| eq_voltarget_ewma_harvey:vol_10 | 8.4% | 7.2% | 1.17% | 0.43 | 9.3% | -2.1% |