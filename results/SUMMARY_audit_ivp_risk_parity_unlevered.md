# Backtest-Ergebnis `audit_ivp_risk_parity_unlevered` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **4** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 6.63e-06. PBO (gemeinsames Fenster ab 2004-01-01, 4 Läufe): **0.72**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ivp_risk_parity_unlevered:erc_lw | riskparity | 2008-02 | 14.8 | 3.6% | 7.0% | 0.46 | -18.7% | -0.05 (-0.39…0.36) | 0.580 | 5% | 0.944 | 0.2 | 0.02% |
| ivp_risk_parity_unlevered | riskparity | 2008-02 | 14.8 | 3.7% | 7.3% | 0.45 | -19.8% | -0.05 (-0.36…0.32) | 0.595 | 5% | 0.943 | 0.2 | 0.02% |
| ivp_risk_parity_unlevered:window_252 | riskparity | 2008-02 | 14.8 | 3.4% | 7.5% | 0.41 | -20.0% | -0.10 (-0.38…0.26) | 0.685 | 5% | 0.919 | 0.2 | 0.02% |
| ivp_risk_parity_unlevered:hrp_252 | riskparity | 2008-02 | 14.8 | 2.7% | 6.3% | 0.37 | -17.8% | -0.13 (-0.60…0.30) | 0.695 | 5% | 0.897 | 0.5 | 0.05% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| ivp_risk_parity_unlevered | 3.7% | 3.0% | 0.70% | 0.36 | 7.9% | -4.9% |
| ivp_risk_parity_unlevered:erc_lw | 3.6% | 2.9% | 0.69% | 0.36 | 7.9% | -5.0% |
| ivp_risk_parity_unlevered:window_252 | 3.4% | 2.7% | 0.66% | 0.32 | 7.9% | -5.2% |
| ivp_risk_parity_unlevered:hrp_252 | 2.7% | 2.1% | 0.66% | 0.27 | 7.9% | -5.9% |