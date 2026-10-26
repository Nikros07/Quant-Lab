# Backtest-Ergebnis `audit_commodity_gold_trend_dbc_gld` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **4** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 8.35e-06. PBO (gemeinsames Fenster ab 2004-01-01, 0 Läufe): **–**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| commodity_gold_trend_dbc_gld:sma252 | crypto | 2007-02 | 15.9 | 4.7% | 11.1% | 0.40 | -29.4% | -0.06 (-0.56…0.43) | 0.555 | 9% | 0.915 | 3.3 | 0.67% |
| commodity_gold_trend_dbc_gld | crypto | 2006-12 | 16.1 | 4.4% | 11.0% | 0.36 | -28.3% | -0.10 (-0.62…0.30) | 0.625 | 13% | 0.897 | 3.9 | 0.79% |
| commodity_gold_trend_dbc_gld:sma168 | crypto | 2006-10 | 16.2 | 3.8% | 11.1% | 0.31 | -25.7% | -0.17 (-0.74…0.33) | 0.685 | 13% | 0.849 | 4.6 | 0.92% |
| commodity_gold_trend_dbc_gld:gold_only | crypto | 2005-09 | 17.3 | 4.5% | 14.3% | 0.30 | -37.6% | -0.17 (-0.60…0.35) | 0.730 | 20% | 0.852 | 3.9 | 0.78% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| commodity_gold_trend_dbc_gld:sma252 | 4.7% | 3.6% | 1.10% | 0.30 | 7.1% | -3.5% |
| commodity_gold_trend_dbc_gld | 4.4% | 3.4% | 1.01% | 0.27 | 7.3% | -3.9% |
| commodity_gold_trend_dbc_gld:gold_only | 4.5% | 3.2% | 1.27% | 0.21 | 7.7% | -4.4% |
| commodity_gold_trend_dbc_gld:sma168 | 3.8% | 2.9% | 0.85% | 0.23 | 7.6% | -4.6% |