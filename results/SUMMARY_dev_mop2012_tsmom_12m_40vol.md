# Backtest-Ergebnis `dev_mop2012_tsmom_12m_40vol` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **3** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 1.18e-05. PBO (gemeinsames Fenster ab 2004-01-01, 3 Läufe): **0.88**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mop2012_tsmom_12m_40vol:lf | tsmom | 2008-02 | 14.8 | 2.4% | 7.4% | 0.28 | -16.8% | -0.23 (-0.64…0.26) | 0.800 | 0% | 0.810 | 1.9 | 0.37% |
| mop2012_tsmom_12m_40vol:portvol10 | tsmom | 2008-02 | 14.8 | 2.6% | 10.4% | 0.24 | -23.7% | -0.27 (-0.92…0.38) | 0.700 | 0% | 0.772 | 3.8 | 0.75% |
| mop2012_tsmom_12m_40vol | tsmom | 2008-02 | 14.8 | 2.0% | 16.6% | 0.17 | -36.7% | -0.34 (-0.95…0.25) | 0.780 | 0% | 0.681 | 4.7 | 0.94% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| mop2012_tsmom_12m_40vol:portvol10 | 2.6% | 2.0% | 0.54% | 0.19 | 7.9% | -5.9% |
| mop2012_tsmom_12m_40vol:lf | 2.4% | 1.8% | 0.54% | 0.20 | 7.9% | -6.1% |
| mop2012_tsmom_12m_40vol | 2.0% | 1.5% | 0.55% | 0.14 | 7.9% | -6.5% |