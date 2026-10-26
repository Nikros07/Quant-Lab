# Backtest-Ergebnis `audit_tom_spy_m2_p3_etf` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **3** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 4.30e-05. PBO (gemeinsames Fenster ab 2004-01-01, 3 Läufe): **0.41**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tom_spy_m2_p3_etf:tag_plus1 | calendar | 1993-02 | 29.8 | 4.5% | 4.5% | 0.52 | -11.6% | 0.05 (-0.37…0.42) | 0.450 | 33% | 0.986 | 12.0 | 0.48% |
| tom_spy_m2_p3_etf | calendar | 1993-02 | 29.9 | 4.8% | 8.0% | 0.35 | -17.7% | -0.12 (-0.41…0.16) | 0.705 | 31% | 0.923 | 12.0 | 0.48% |
| tom_spy_m2_p3_etf:konservativ | calendar | 1993-02 | 29.8 | 4.6% | 8.2% | 0.33 | -21.4% | -0.14 (-0.42…0.15) | 0.805 | 24% | 0.903 | 12.0 | 0.48% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| tom_spy_m2_p3_etf | 4.8% | 4.2% | 0.56% | 0.28 | 9.0% | -4.8% |
| tom_spy_m2_p3_etf:konservativ | 4.6% | 4.1% | 0.52% | 0.27 | 8.9% | -4.8% |
| tom_spy_m2_p3_etf:tag_plus1 | 4.5% | 4.1% | 0.44% | 0.42 | 8.9% | -4.8% |