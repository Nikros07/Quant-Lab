# Backtest-Ergebnis `is` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **3** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 4.44e-07. PBO (gemeinsames Fenster ab 2004-01-01, 0 Läufe): **–**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.4%, Vol 17.2%, Sharpe 0.44, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| faber_gtaa:sma_12 | tactical | 2007-02 | 15.8 | 4.3% | 7.9% | 0.47 | -12.6% | -0.00 (-0.36…0.32) | 0.520 | 9% | 0.965 | 0.9 | 0.09% |
| faber_gtaa:sma_8 | tactical | 2006-10 | 16.1 | 4.3% | 8.1% | 0.45 | -18.5% | -0.01 (-0.35…0.34) | 0.550 | 13% | 0.962 | 1.1 | 0.11% |
| faber_gtaa | tactical | 2006-12 | 16.0 | 4.3% | 8.2% | 0.45 | -14.4% | -0.01 (-0.31…0.27) | 0.510 | 14% | 0.959 | 1.0 | 0.10% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| faber_gtaa:sma_8 | 4.3% | 3.5% | 0.77% | 0.36 | 7.4% | -3.8% |
| faber_gtaa | 4.3% | 3.5% | 0.74% | 0.36 | 7.2% | -3.7% |
| faber_gtaa:sma_12 | 4.3% | 3.5% | 0.78% | 0.37 | 7.4% | -3.9% |