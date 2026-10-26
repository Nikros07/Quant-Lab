# Backtest-Ergebnis `audit_lowvol_defensive_longonly_etf` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **3** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 1.10e-04. PBO (gemeinsames Fenster ab 2004-01-01, 0 Läufe): **–**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lowvol_defensive_longonly_etf | lowrisk | 2011-10 | 11.2 | 11.8% | 14.2% | 0.81 | -33.1% | 0.05 (-0.13…0.27) | 0.325 | 38% | 0.986 | 0.0 | 0.00% |
| lowvol_defensive_longonly_etf:splv | lowrisk | 2011-05 | 11.7 | 10.9% | 15.3% | 0.71 | -36.3% | 0.05 (-0.19…0.28) | 0.340 | 21% | 0.972 | 0.0 | 0.00% |
| lowvol_defensive_longonly_etf:sector_proxy | lowrisk | 2001-12 | 21.0 | 7.8% | 15.5% | 0.49 | -41.6% | 0.06 (-0.08…0.22) | 0.265 | 45% | 0.943 | 0.5 | 0.05% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| lowvol_defensive_longonly_etf | 11.8% | 10.4% | 1.40% | 0.70 | 11.1% | -0.6% |
| lowvol_defensive_longonly_etf:splv | 10.9% | 9.6% | 1.31% | 0.62 | 9.7% | -0.1% |
| lowvol_defensive_longonly_etf:sector_proxy | 7.8% | 6.8% | 1.07% | 0.42 | 6.9% | -0.2% |