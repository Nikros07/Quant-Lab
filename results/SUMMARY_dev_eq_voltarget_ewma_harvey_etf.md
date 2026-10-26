# Backtest-Ergebnis `dev_eq_voltarget_ewma_harvey_etf` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **4** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 1.44e-07. PBO (gemeinsames Fenster ab 2004-01-01, 4 Läufe): **0.24**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| eq_voltarget_ewma_harvey_etf | volmgmt | 1994-02 | 28.9 | 7.9% | 11.4% | 0.54 | -31.0% | 0.08 (-0.04…0.18) | 0.130 | 37% | 0.998 | 0.5 | 0.02% |
| eq_voltarget_ewma_harvey_etf:vol_10 | volmgmt | 1994-02 | 28.9 | 7.2% | 10.0% | 0.53 | -24.6% | 0.08 (-0.06…0.18) | 0.170 | 35% | 0.997 | 0.6 | 0.02% |
| eq_voltarget_ewma_harvey_etf:cap_1_5 | volmgmt | 1994-02 | 28.9 | 8.2% | 12.2% | 0.53 | -31.0% | 0.07 (-0.07…0.17) | 0.210 | 37% | 0.997 | 1.0 | 0.04% |
| eq_voltarget_ewma_harvey_etf:hl_40 | volmgmt | 1994-02 | 28.9 | 7.9% | 11.7% | 0.52 | -28.1% | 0.06 (-0.04…0.15) | 0.180 | 39% | 0.997 | 0.2 | 0.01% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| eq_voltarget_ewma_harvey_etf:cap_1_5 | 8.2% | 6.9% | 1.30% | 0.43 | 8.8% | -1.9% |
| eq_voltarget_ewma_harvey_etf:hl_40 | 7.9% | 6.8% | 1.09% | 0.43 | 8.8% | -2.0% |
| eq_voltarget_ewma_harvey_etf | 7.9% | 6.8% | 1.16% | 0.44 | 8.8% | -2.0% |
| eq_voltarget_ewma_harvey_etf:vol_10 | 7.2% | 6.2% | 1.05% | 0.43 | 8.8% | -2.6% |