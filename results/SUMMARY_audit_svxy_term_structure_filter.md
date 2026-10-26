# Backtest-Ergebnis `audit_svxy_term_structure_filter` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **3** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 4.75e-05. PBO (gemeinsames Fenster ab 2004-01-01, 0 Läufe): **–**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| svxy_term_structure_filter | volpremium | 2011-10 | 11.2 | 31.5% | 47.8% | 0.80 | -56.9% | 0.00 (-0.45…0.34) | 0.480 | 92% | 0.990 | 6.5 | 2.62% |
| svxy_term_structure_filter:w025 | volpremium | 2011-10 | 11.2 | 10.1% | 15.0% | 0.68 | -19.9% | -0.13 (-0.61…0.24) | 0.655 | 8% | 0.972 | 1.7 | 0.67% |
| svxy_term_structure_filter:spy_secondary | volpremium | 2006-07 | 16.4 | 8.6% | 14.2% | 0.59 | -33.8% | 0.10 (-0.17…0.34) | 0.275 | 38% | 0.976 | 8.1 | 0.32% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| svxy_term_structure_filter | 31.5% | 24.2% | 7.30% | 0.68 | 12.0% | 12.2% |
| svxy_term_structure_filter:w025 | 10.1% | 7.7% | 2.42% | 0.52 | 12.0% | -4.3% |
| svxy_term_structure_filter:spy_secondary | 8.6% | 6.9% | 1.72% | 0.47 | 8.0% | -1.1% |