# Backtest-Ergebnis `dev_commodity_gold_trend_dbc_gld` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **4** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 1.01e-05. PBO (gemeinsames Fenster ab 2004-01-01, 0 Läufe): **–**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| commodity_gold_trend_dbc_gld:sma252 | crypto | 2007-03 | 15.8 | 4.7% | 11.0% | 0.40 | -29.4% | -0.07 (-0.58…0.31) | 0.620 | 9% | 0.915 | 3.3 | 0.66% |
| commodity_gold_trend_dbc_gld | crypto | 2006-12 | 16.0 | 4.5% | 11.0% | 0.38 | -28.3% | -0.08 (-0.57…0.45) | 0.630 | 13% | 0.904 | 4.0 | 0.79% |
| commodity_gold_trend_dbc_gld:sma168 | crypto | 2006-10 | 16.2 | 3.7% | 11.1% | 0.31 | -25.7% | -0.16 (-0.66…0.33) | 0.710 | 13% | 0.845 | 4.6 | 0.93% |
| commodity_gold_trend_dbc_gld:gold_only | crypto | 2005-09 | 17.3 | 4.5% | 14.3% | 0.30 | -37.6% | -0.17 (-0.57…0.33) | 0.740 | 20% | 0.848 | 3.9 | 0.78% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| commodity_gold_trend_dbc_gld:sma252 | 4.7% | 3.6% | 1.10% | 0.30 | 7.3% | -3.7% |
| commodity_gold_trend_dbc_gld | 4.5% | 3.5% | 1.05% | 0.29 | 7.2% | -3.7% |
| commodity_gold_trend_dbc_gld:gold_only | 4.5% | 3.2% | 1.27% | 0.21 | 7.7% | -4.4% |
| commodity_gold_trend_dbc_gld:sma168 | 3.7% | 2.9% | 0.85% | 0.23 | 7.3% | -4.4% |