# Backtest-Ergebnis `audited` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **54** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 1.32e-04. PBO (gemeinsames Fenster ab 2004-01-01, 37 Läufe): **0.47**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| nagel_vix_gated_sector_etf_reversal:vix_25 | reversal | 1998-12 | 24.0 | 6.5% | 6.8% | 0.72 | -14.0% | 0.38 (-0.01…0.75) | 0.043 | 41% | 0.941 | 18.5 | 1.11% |
| sector_etf_top3_12m:sma10 | xsmom | 1927-07 | 95.4 | 12.2% | 13.7% | 0.68 | -49.1% | 0.25 (0.11…0.40) | 0.007 | 61% | 0.992 | 2.2 | 0.22% |
| nagel_vix_gated_sector_etf_reversal:vix_20 | reversal | 1998-12 | 24.0 | 6.8% | 7.9% | 0.67 | -14.0% | 0.32 (-0.02…0.66) | 0.063 | 41% | 0.894 | 33.9 | 2.04% |
| keller_paa_g12 | tactical | 2008-05 | 14.6 | 5.9% | 8.4% | 0.66 | -14.3% | 0.16 (-0.35…0.58) | 0.300 | 5% | 0.820 | 3.1 | 0.61% |
| sector_etf_top3_12m | xsmom | 1927-07 | 95.4 | 14.0% | 17.7% | 0.66 | -72.3% | 0.22 (0.15…0.29) | 0.000 | 92% | 0.986 | 2.3 | 0.23% |
| keller_paa_g12:sleeves3 | tactical | 2008-05 | 14.6 | 5.7% | 8.3% | 0.65 | -14.2% | 0.15 (-0.37…0.56) | 0.317 | 5% | 0.808 | 3.2 | 0.65% |
| sector_etf_top3_12m:combo | xsmom | 1927-07 | 95.4 | 13.9% | 17.8% | 0.65 | -75.0% | 0.21 (0.14…0.28) | 0.000 | 87% | 0.982 | 2.9 | 0.29% |
| keller_paa_g12:top4 | tactical | 2008-05 | 14.6 | 5.9% | 9.0% | 0.63 | -14.6% | 0.12 (-0.42…0.58) | 0.363 | 5% | 0.782 | 3.4 | 0.68% |
| keller_paa_g12:breadth4 | tactical | 2008-05 | 14.6 | 5.2% | 7.9% | 0.62 | -13.8% | 0.11 (-0.43…0.58) | 0.380 | 5% | 0.771 | 3.1 | 0.62% |
| sector_etf_top3_12m:hold_buffer | xsmom | 1927-07 | 95.4 | 13.1% | 18.0% | 0.60 | -75.7% | 0.17 (0.09…0.23) | 0.000 | 85% | 0.953 | 1.1 | 0.11% |
| trend_ma12_us_equity_cash_etf:signal_tr | macro | 1993-12 | 29.0 | 9.5% | 13.0% | 0.60 | -22.5% | 0.14 (-0.08…0.35) | 0.127 | 49% | 0.829 | 0.6 | 0.11% |
| trend_ma12_us_equity_cash_etf | macro | 1993-01 | 29.9 | 9.4% | 12.8% | 0.60 | -22.5% | 0.13 (-0.10…0.34) | 0.210 | 43% | 0.829 | 0.5 | 0.11% |
| trend_ma12_us_equity_cash_etf:sma10 | macro | 1993-01 | 29.9 | 9.2% | 12.6% | 0.59 | -23.0% | 0.12 (-0.09…0.33) | 0.180 | 45% | 0.822 | 0.7 | 0.13% |
| trend_ma12_us_equity_cash | macro | 1930-01 | 92.9 | 9.6% | 11.8% | 0.58 | -37.4% | 0.14 (0.00…0.29) | 0.050 | 36% | 0.920 | 0.6 | 0.12% |
| trend_ma12_us_equity_cash:sma10 | macro | 1930-01 | 92.9 | 9.6% | 11.7% | 0.58 | -37.3% | 0.14 (0.00…0.30) | 0.057 | 38% | 0.919 | 0.7 | 0.15% |
| trend_ma12_us_equity_cash_etf:ma2_12 | macro | 1993-01 | 29.9 | 9.5% | 13.7% | 0.57 | -33.7% | 0.10 (-0.11…0.33) | 0.197 | 47% | 0.791 | 0.4 | 0.08% |
| trend_ma12_us_equity_cash:ma2_12 | macro | 1930-01 | 92.9 | 9.6% | 12.0% | 0.57 | -39.3% | 0.13 (0.00…0.27) | 0.067 | 36% | 0.905 | 0.5 | 0.09% |
| eq_voltarget_ewma_harvey:vol_10 | volmgmt | 1928-01 | 95.0 | 8.4% | 10.0% | 0.55 | -46.9% | 0.11 (0.03…0.20) | 0.020 | 20% | 0.869 | 0.5 | 0.02% |
| trend_ma12_us_equity_cash:signal_tr | macro | 1930-01 | 92.9 | 9.3% | 12.1% | 0.54 | -45.7% | 0.11 (-0.02…0.25) | 0.107 | 31% | 0.858 | 0.7 | 0.13% |
| eq_voltarget_ewma_harvey | volmgmt | 1928-01 | 95.0 | 8.9% | 11.2% | 0.54 | -55.4% | 0.11 (0.03…0.18) | 0.010 | 19% | 0.856 | 0.4 | 0.02% |
| eq_voltarget_ewma_harvey_etf | volmgmt | 1994-02 | 28.9 | 7.9% | 11.4% | 0.54 | -31.0% | 0.08 (-0.05…0.18) | 0.113 | 37% | 0.731 | 0.5 | 0.02% |
| eq_voltarget_ewma_harvey_etf:vol_10 | volmgmt | 1994-02 | 28.9 | 7.2% | 10.0% | 0.53 | -24.6% | 0.08 (-0.06…0.18) | 0.143 | 35% | 0.725 | 0.6 | 0.02% |
| eq_voltarget_ewma_harvey:cap_1_5 | volmgmt | 1928-01 | 95.0 | 9.4% | 12.5% | 0.53 | -55.4% | 0.10 (0.01…0.19) | 0.043 | 41% | 0.840 | 1.1 | 0.04% |
| eq_voltarget_ewma_harvey_etf:cap_1_5 | volmgmt | 1994-02 | 28.9 | 8.2% | 12.2% | 0.53 | -31.0% | 0.07 (-0.06…0.19) | 0.167 | 37% | 0.724 | 1.0 | 0.04% |
| eq_voltarget_ewma_harvey:hl_40 | volmgmt | 1928-01 | 95.0 | 8.8% | 11.4% | 0.53 | -53.5% | 0.10 (0.03…0.17) | 0.017 | 18% | 0.830 | 0.2 | 0.01% |
| eq_voltarget_ewma_harvey_etf:hl_40 | volmgmt | 1994-02 | 28.9 | 7.9% | 11.7% | 0.52 | -28.1% | 0.06 (-0.05…0.16) | 0.147 | 39% | 0.706 | 0.2 | 0.01% |
| nagel_vix_gated_sector_etf_reversal | reversal | 1998-12 | 24.0 | 5.2% | 7.3% | 0.50 | -19.9% | 0.16 (-0.16…0.53) | 0.220 | 41% | 0.663 | 36.8 | 2.21% |
| faber_gtaa:sma_12 | tactical | 2007-02 | 15.8 | 4.3% | 7.9% | 0.47 | -12.6% | -0.00 (-0.34…0.34) | 0.503 | 9% | 0.576 | 0.9 | 0.09% |
| antonacci_gem_lookback_ensemble | tactical | 2004-09 | 18.2 | 7.1% | 14.5% | 0.46 | -31.0% | -0.02 (-0.24…0.22) | 0.517 | 30% | 0.574 | 1.8 | 0.36% |
| antonacci_gem_lookback_ensemble:single_l12 | tactical | 2004-09 | 18.2 | 7.5% | 15.7% | 0.46 | -33.7% | -0.02 (-0.26…0.22) | 0.530 | 30% | 0.573 | 1.3 | 0.27% |
| nagel_vix_gated_sector_etf_reversal:vix_30 | reversal | 1998-12 | 24.0 | 4.2% | 5.7% | 0.46 | -14.0% | 0.12 (-0.25…0.44) | 0.287 | 38% | 0.583 | 9.0 | 0.54% |
| sector_etf_top3_12m_etf:sma10 | xsmom | 1999-12 | 23.0 | 7.0% | 13.6% | 0.46 | -24.0% | 0.13 (-0.16…0.41) | 0.213 | 46% | 0.577 | 2.6 | 0.26% |
| antonacci_gem_lookback_ensemble:bond_ief | tactical | 2004-09 | 18.2 | 7.0% | 14.4% | 0.46 | -30.3% | -0.02 (-0.29…0.26) | 0.513 | 30% | 0.566 | 1.8 | 0.36% |
| faber_gtaa:sma_8 | tactical | 2006-10 | 16.2 | 4.3% | 8.1% | 0.45 | -18.5% | -0.01 (-0.34…0.30) | 0.520 | 13% | 0.553 | 1.1 | 0.11% |
| faber_gtaa | tactical | 2006-12 | 16.0 | 4.3% | 8.2% | 0.45 | -14.4% | -0.01 (-0.32…0.27) | 0.517 | 13% | 0.544 | 1.0 | 0.10% |
| antonacci_gem_lookback_ensemble:acwx | tactical | 2009-04 | 13.7 | 5.7% | 14.8% | 0.41 | -31.0% | -0.37 (-0.52…-0.21) | 1.000 | 0% | 0.492 | 2.0 | 0.39% |
| wml_volscaled_ff | xsmom | 1930-01 | 92.9 | 7.8% | 13.8% | 0.39 | -79.9% | -0.04 (-0.31…0.28) | 0.587 | 43% | 0.371 | 1.0 | 6.77% |
| wml_volscaled_ff:cap_1 | xsmom | 1930-01 | 92.9 | 7.5% | 12.7% | 0.39 | -74.3% | -0.05 (-0.32…0.26) | 0.590 | 43% | 0.357 | 0.7 | 4.90% |
| sector_etf_top3_12m_etf:combo | xsmom | 1999-12 | 23.0 | 7.2% | 18.7% | 0.39 | -44.7% | 0.06 (-0.11…0.19) | 0.263 | 46% | 0.442 | 3.4 | 0.34% |
| sector_etf_top3_12m_etf | xsmom | 1999-12 | 23.0 | 7.1% | 18.9% | 0.38 | -45.5% | 0.05 (-0.09…0.16) | 0.283 | 46% | 0.420 | 2.8 | 0.28% |
| sector_etf_top3_12m_etf:hold_buffer | xsmom | 1999-12 | 23.0 | 7.3% | 20.3% | 0.38 | -53.3% | 0.05 (-0.09…0.16) | 0.267 | 51% | 0.416 | 1.1 | 0.11% |
| country_etf_xsmom_12_1:long_top5_sma10 | xsmom | 1997-03 | 25.8 | 6.7% | 15.4% | 0.38 | -39.5% | -0.03 (-0.32…0.21) | 0.617 | 48% | 0.411 | 2.3 | 0.23% |
| wml_volscaled_ff:vol_target_19 | xsmom | 1930-01 | 92.9 | 8.0% | 21.4% | 0.33 | -94.8% | -0.11 (-0.37…0.19) | 0.730 | 47% | 0.164 | 1.6 | 10.58% |
| country_value_cape_faber_proxy:avg60 | valuecarry | 2001-12 | 21.0 | 5.2% | 23.0% | 0.29 | -61.0% | -0.14 (-0.34…0.03) | 0.877 | 30% | 0.269 | 0.4 | 0.08% |
| country_etf_xsmom_12_1:long_top5 | xsmom | 1997-03 | 25.8 | 5.7% | 21.4% | 0.28 | -62.9% | -0.13 (-0.33…0.05) | 0.863 | 38% | 0.240 | 2.6 | 0.26% |
| mop2012_tsmom_12m_40vol:lf | tsmom | 2008-02 | 14.8 | 2.4% | 7.4% | 0.28 | -16.8% | -0.23 (-0.66…0.24) | 0.810 | 0% | 0.290 | 1.9 | 0.37% |
| mop2012_tsmom_12m_40vol:portvol10 | tsmom | 2008-02 | 14.8 | 2.6% | 10.4% | 0.24 | -23.7% | -0.27 (-0.90…0.38) | 0.737 | 0% | 0.244 | 3.8 | 0.75% |
| country_value_cape_faber_proxy:june | valuecarry | 2006-06 | 16.5 | 2.9% | 23.3% | 0.20 | -59.0% | -0.28 (-0.47…-0.07) | 0.977 | 0% | 0.186 | 0.3 | 0.05% |
| country_value_cape_faber_proxy | valuecarry | 2006-12 | 16.0 | 2.8% | 23.1% | 0.20 | -57.6% | -0.26 (-0.47…-0.08) | 0.977 | 0% | 0.188 | 0.3 | 0.06% |
| country_value_cape_faber_proxy:quartile | valuecarry | 2006-12 | 16.0 | 2.4% | 23.7% | 0.18 | -56.9% | -0.28 (-0.47…-0.09) | 0.983 | 0% | 0.172 | 0.3 | 0.07% |
| mop2012_tsmom_12m_40vol | tsmom | 2008-02 | 14.8 | 2.0% | 16.6% | 0.17 | -36.7% | -0.34 (-0.95…0.26) | 0.797 | 0% | 0.167 | 4.7 | 0.94% |
| wml_volscaled_ff:static_w1 | xsmom | 1930-01 | 92.9 | -2.3% | 32.4% | 0.06 | -100.0% | -0.38 (-0.63…-0.08) | 0.997 | 39% | 0.000 | 1.2 | 8.19% |
| country_etf_xsmom_12_1 | xsmom | 1997-03 | 25.8 | -0.0% | 13.5% | -0.07 | -64.1% | -0.48 (-0.97…-0.03) | 0.950 | 24% | 0.006 | 5.3 | 0.53% |
| country_etf_xsmom_12_1:universe_ext | xsmom | 1997-03 | 25.8 | -0.4% | 13.9% | -0.10 | -68.0% | -0.50 (-0.98…-0.08) | 0.963 | 19% | 0.004 | 5.4 | 0.54% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| sector_etf_top3_12m | 14.0% | 11.8% | 2.21% | 0.54 | 9.4% | 2.4% |
| sector_etf_top3_12m:combo | 13.9% | 11.6% | 2.21% | 0.53 | 9.4% | 2.2% |
| sector_etf_top3_12m:hold_buffer | 13.1% | 11.1% | 2.00% | 0.50 | 9.4% | 1.7% |
| sector_etf_top3_12m:sma10 | 12.2% | 10.4% | 1.82% | 0.56 | 9.4% | 1.0% |
| trend_ma12_us_equity_cash | 9.6% | 8.3% | 1.35% | 0.46 | 9.3% | -1.1% |
| trend_ma12_us_equity_cash:ma2_12 | 9.6% | 8.2% | 1.35% | 0.46 | 9.3% | -1.1% |
| trend_ma12_us_equity_cash:sma10 | 9.6% | 8.2% | 1.36% | 0.46 | 9.3% | -1.1% |
| trend_ma12_us_equity_cash_etf:signal_tr | 9.5% | 8.1% | 1.42% | 0.49 | 8.8% | -0.7% |
| trend_ma12_us_equity_cash_etf:ma2_12 | 9.5% | 8.1% | 1.39% | 0.47 | 8.9% | -0.8% |
| trend_ma12_us_equity_cash_etf | 9.4% | 8.0% | 1.39% | 0.49 | 8.9% | -0.9% |
| trend_ma12_us_equity_cash:signal_tr | 9.3% | 8.0% | 1.32% | 0.43 | 9.3% | -1.3% |
| trend_ma12_us_equity_cash_etf:sma10 | 9.2% | 7.9% | 1.38% | 0.48 | 8.9% | -1.0% |
| eq_voltarget_ewma_harvey:cap_1_5 | 9.4% | 7.8% | 1.53% | 0.42 | 9.3% | -1.5% |
| eq_voltarget_ewma_harvey:hl_40 | 8.8% | 7.8% | 1.04% | 0.44 | 9.3% | -1.6% |
| eq_voltarget_ewma_harvey | 8.9% | 7.7% | 1.18% | 0.44 | 9.3% | -1.6% |
| eq_voltarget_ewma_harvey:vol_10 | 8.4% | 7.2% | 1.17% | 0.43 | 9.3% | -2.1% |
| eq_voltarget_ewma_harvey_etf:cap_1_5 | 8.2% | 6.9% | 1.30% | 0.43 | 8.8% | -1.9% |
| eq_voltarget_ewma_harvey_etf:hl_40 | 7.9% | 6.8% | 1.09% | 0.43 | 8.8% | -2.0% |
| eq_voltarget_ewma_harvey_etf | 7.9% | 6.8% | 1.16% | 0.44 | 8.8% | -2.0% |
| wml_volscaled_ff:vol_target_19 | 8.0% | 6.7% | 1.36% | 0.27 | 9.3% | -2.6% |
| wml_volscaled_ff | 7.8% | 6.7% | 1.17% | 0.31 | 9.3% | -2.7% |
| wml_volscaled_ff:cap_1 | 7.5% | 6.5% | 0.96% | 0.32 | 9.3% | -2.8% |
| antonacci_gem_lookback_ensemble:single_l12 | 7.5% | 6.2% | 1.29% | 0.38 | 8.0% | -1.7% |
| eq_voltarget_ewma_harvey_etf:vol_10 | 7.2% | 6.2% | 1.05% | 0.43 | 8.8% | -2.6% |
| sector_etf_top3_12m_etf:hold_buffer | 7.3% | 6.1% | 1.16% | 0.32 | 5.3% | 0.8% |
| sector_etf_top3_12m_etf:combo | 7.2% | 6.0% | 1.21% | 0.33 | 5.3% | 0.7% |
| sector_etf_top3_12m_etf:sma10 | 7.0% | 5.9% | 1.12% | 0.38 | 5.3% | 0.6% |
| sector_etf_top3_12m_etf | 7.1% | 5.9% | 1.17% | 0.32 | 5.3% | 0.6% |
| antonacci_gem_lookback_ensemble | 7.1% | 5.9% | 1.25% | 0.38 | 8.0% | -2.1% |
| antonacci_gem_lookback_ensemble:bond_ief | 7.0% | 5.8% | 1.24% | 0.38 | 8.0% | -2.2% |
| nagel_vix_gated_sector_etf_reversal:vix_20 | 6.8% | 5.7% | 1.08% | 0.53 | 5.9% | -0.2% |
| country_etf_xsmom_12_1:long_top5_sma10 | 6.7% | 5.6% | 1.01% | 0.31 | 7.5% | -1.9% |
| nagel_vix_gated_sector_etf_reversal:vix_25 | 6.5% | 5.6% | 0.96% | 0.58 | 5.9% | -0.3% |
| country_etf_xsmom_12_1:long_top5 | 5.7% | 4.9% | 0.86% | 0.24 | 7.5% | -2.7% |
| keller_paa_g12:top4 | 5.9% | 4.7% | 1.26% | 0.49 | 7.9% | -3.2% |
| keller_paa_g12 | 5.9% | 4.7% | 1.25% | 0.52 | 7.9% | -3.2% |
| antonacci_gem_lookback_ensemble:acwx | 5.7% | 4.6% | 1.09% | 0.34 | 12.0% | -7.4% |
| keller_paa_g12:sleeves3 | 5.7% | 4.5% | 1.23% | 0.51 | 7.9% | -3.4% |
| nagel_vix_gated_sector_etf_reversal | 5.2% | 4.4% | 0.83% | 0.39 | 5.9% | -1.5% |
| country_value_cape_faber_proxy:avg60 | 5.2% | 4.3% | 0.95% | 0.25 | 6.9% | -2.6% |
| keller_paa_g12:breadth4 | 5.2% | 4.1% | 1.14% | 0.47 | 7.9% | -3.8% |
| nagel_vix_gated_sector_etf_reversal:vix_30 | 4.2% | 3.7% | 0.50% | 0.37 | 5.9% | -2.2% |
| faber_gtaa:sma_8 | 4.3% | 3.5% | 0.76% | 0.36 | 7.4% | -3.8% |
| faber_gtaa | 4.3% | 3.5% | 0.74% | 0.36 | 7.2% | -3.7% |
| faber_gtaa:sma_12 | 4.3% | 3.5% | 0.78% | 0.37 | 7.4% | -3.9% |
| country_value_cape_faber_proxy:june | 2.9% | 2.4% | 0.52% | 0.18 | 7.8% | -5.4% |
| country_value_cape_faber_proxy | 2.8% | 2.3% | 0.50% | 0.18 | 7.2% | -4.9% |
| mop2012_tsmom_12m_40vol:portvol10 | 2.6% | 2.0% | 0.54% | 0.19 | 7.9% | -5.9% |
| country_value_cape_faber_proxy:quartile | 2.4% | 1.9% | 0.46% | 0.16 | 7.2% | -5.3% |
| mop2012_tsmom_12m_40vol:lf | 2.4% | 1.8% | 0.54% | 0.20 | 7.9% | -6.1% |
| mop2012_tsmom_12m_40vol | 2.0% | 1.5% | 0.55% | 0.14 | 7.9% | -6.5% |
| country_etf_xsmom_12_1 | -0.0% | -0.2% | 0.20% | -0.09 | 7.5% | -7.8% |
| country_etf_xsmom_12_1:universe_ext | -0.4% | -0.6% | 0.20% | -0.11 | 7.5% | -8.2% |
| wml_volscaled_ff:static_w1 | -2.3% | -2.4% | 0.08% | 0.06 | 9.3% | -11.7% |