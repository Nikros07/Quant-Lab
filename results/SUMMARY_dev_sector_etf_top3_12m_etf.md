# Backtest-Ergebnis `dev_sector_etf_top3_12m_etf` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **4** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 6.47e-06. PBO (gemeinsames Fenster ab 2004-01-01, 4 Läufe): **0.80**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sector_etf_top3_12m_etf:sma10 | xsmom | 1999-12 | 23.0 | 7.0% | 13.6% | 0.46 | -24.0% | 0.13 (-0.12…0.49) | 0.230 | 46% | 0.976 | 2.6 | 0.26% |
| sector_etf_top3_12m_etf:combo | xsmom | 1999-12 | 23.0 | 7.2% | 18.7% | 0.39 | -44.7% | 0.06 (-0.08…0.21) | 0.290 | 46% | 0.951 | 3.4 | 0.34% |
| sector_etf_top3_12m_etf | xsmom | 1999-12 | 23.0 | 7.1% | 18.9% | 0.38 | -45.5% | 0.05 (-0.08…0.20) | 0.240 | 46% | 0.945 | 2.8 | 0.28% |
| sector_etf_top3_12m_etf:hold_buffer | xsmom | 1999-12 | 23.0 | 7.3% | 20.3% | 0.38 | -53.3% | 0.05 (-0.08…0.17) | 0.210 | 51% | 0.944 | 1.1 | 0.11% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| sector_etf_top3_12m_etf:hold_buffer | 7.3% | 6.1% | 1.16% | 0.32 | 5.3% | 0.8% |
| sector_etf_top3_12m_etf:combo | 7.2% | 6.0% | 1.21% | 0.33 | 5.3% | 0.7% |
| sector_etf_top3_12m_etf:sma10 | 7.0% | 5.9% | 1.12% | 0.38 | 5.3% | 0.6% |
| sector_etf_top3_12m_etf | 7.1% | 5.9% | 1.17% | 0.32 | 5.3% | 0.6% |