# Backtest-Ergebnis `audit_lowvol_defensive_longonly` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **2** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 1.00e-04. PBO (gemeinsames Fenster ab 2004-01-01, 0 Läufe): **–**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lowvol_defensive_longonly:var | lowrisk | 1963-07 | 59.5 | 11.2% | 12.6% | 0.56 | -42.3% | 0.15 (-0.07…0.33) | 0.125 | 65% | 1.000 | 0.0 | 0.00% |
| lowvol_defensive_longonly | lowrisk | 1963-07 | 59.5 | 10.4% | 12.6% | 0.51 | -43.4% | 0.10 (-0.11…0.28) | 0.250 | 50% | 1.000 | 0.0 | 0.00% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| lowvol_defensive_longonly:var | 11.2% | 10.8% | 0.38% | 0.53 | 9.8% | 1.0% |
| lowvol_defensive_longonly | 10.4% | 10.1% | 0.38% | 0.48 | 9.8% | 0.3% |