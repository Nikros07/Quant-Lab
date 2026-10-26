# Backtest-Ergebnis `audited_all` (bis 2022-12-31, Ausführung: open, Kosten ×1.0)

Läufe: **107** (inkl. Varianten, alle zählen als Versuche für den Deflated Sharpe). Streuung der Tages-Sharpe über alle Läufe: 1.57e-04. PBO (gemeinsames Fenster ab 2004-01-01, 62 Läufe): **0.47**.

Kosten sind enthalten (5 bps pro Seite Standard), Steuern NICHT. Benchmarks: SPY Buy&Hold, 60/40 (SPY/IEF).

- **SPY**: CAGR 9.5%, Vol 18.9%, Sharpe 0.46, MaxDD -55.2%
- **60/40**: CAGR 7.7%, Vol 10.6%, Sharpe 0.64, MaxDD -32.5%
- **MKT**: CAGR 9.8%, Vol 17.5%, Sharpe 0.45, MaxDD -84.1%

## Rangliste nach Sharpe

| Lauf | Fam. | ab | Jahre | CAGR | Vol | Sharpe | MaxDD | ΔSharpe vs SPY (90%-KI) | p | 5J-Fenster>SPY | DSR | Umsatz/J | Kosten/J |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| crypto_trend_ens_btc_eth:sma50_btc | crypto | 2015-09 | 7.3 | 93.6% | 53.9% | 1.47 | -58.5% | 0.87 (0.03…1.69) | 0.042 | 100% | 0.990 | 8.3 | 3.33% |
| crypto_trend_ens_btc_eth | crypto | 2015-09 | 7.3 | 66.7% | 41.4% | 1.41 | -46.6% | 0.81 (0.01…1.54) | 0.039 | 100% | 0.984 | 7.7 | 3.06% |
| crypto_trend_ens_btc_eth:sma200_btc | crypto | 2015-09 | 7.3 | 82.7% | 58.8% | 1.30 | -69.9% | 0.70 (-0.18…1.54) | 0.092 | 100% | 0.969 | 2.7 | 1.09% |
| lowvol_defensive_longonly_etf | lowrisk | 2011-10 | 11.2 | 11.8% | 14.2% | 0.81 | -33.1% | 0.05 (-0.13…0.27) | 0.315 | 38% | 0.841 | 0.0 | 0.00% |
| svxy_term_structure_filter | volpremium | 2011-10 | 11.2 | 31.5% | 47.8% | 0.80 | -56.9% | 0.00 (-0.45…0.42) | 0.496 | 92% | 0.833 | 6.5 | 2.62% |
| tom_spy_m2_p3 | calendar | 1926-07 | 96.4 | 8.9% | 7.2% | 0.80 | -23.2% | 0.35 (0.18…0.53) | 0.000 | 45% | 0.996 | 12.0 | 0.48% |
| lowvol_defensive_longonly_etf:splv | lowrisk | 2011-05 | 11.7 | 10.9% | 15.3% | 0.71 | -36.3% | 0.05 (-0.19…0.33) | 0.372 | 21% | 0.755 | 0.0 | 0.00% |
| sector_etf_top3_12m:sma10 | xsmom | 1927-07 | 95.4 | 12.2% | 13.7% | 0.68 | -49.1% | 0.25 (0.10…0.40) | 0.005 | 61% | 0.943 | 2.2 | 0.22% |
| nagel_vix_gated_sector_etf_reversal:vix_25 | reversal | 2007-07 | 15.5 | 5.5% | 7.2% | 0.68 | -14.0% | 0.24 (-0.18…0.66) | 0.190 | 9% | 0.763 | 18.4 | 1.10% |
| svxy_term_structure_filter:w025 | volpremium | 2011-10 | 11.2 | 10.1% | 15.0% | 0.68 | -19.9% | -0.13 (-0.60…0.30) | 0.674 | 8% | 0.711 | 1.7 | 0.67% |
| static_multifactor_equal_risk:equal_weight | factors | 1966-06 | 56.5 | 9.6% | 7.6% | 0.68 | -59.9% | 0.27 (-0.18…0.68) | 0.156 | 50% | 0.892 | 0.3 | 1.60% |
| tom_spy_m2_p3:konservativ | calendar | 1926-07 | 96.4 | 8.1% | 7.6% | 0.67 | -28.8% | 0.22 (0.04…0.39) | 0.019 | 35% | 0.926 | 12.0 | 0.48% |
| keller_paa_g12 | tactical | 2008-05 | 14.6 | 5.9% | 8.4% | 0.66 | -14.3% | 0.16 (-0.33…0.61) | 0.281 | 5% | 0.720 | 3.1 | 0.61% |
| sector_etf_top3_12m | xsmom | 1927-07 | 95.4 | 14.0% | 17.7% | 0.66 | -72.3% | 0.22 (0.15…0.29) | 0.000 | 92% | 0.908 | 2.3 | 0.23% |
| keller_paa_g12:sleeves3 | tactical | 2008-05 | 14.6 | 5.7% | 8.3% | 0.65 | -14.2% | 0.15 (-0.31…0.58) | 0.296 | 5% | 0.705 | 3.2 | 0.65% |
| index_etf_ibs_rsi2_longonly:connors_rsi2 | reversal | 1993-11 | 29.1 | 6.5% | 6.7% | 0.65 | -14.9% | 0.19 (-0.15…0.49) | 0.148 | 41% | 0.773 | 7.7 | 0.31% |
| sector_etf_top3_12m:combo | xsmom | 1927-07 | 95.4 | 13.9% | 17.8% | 0.65 | -75.0% | 0.21 (0.14…0.28) | 0.000 | 87% | 0.889 | 2.9 | 0.29% |
| index_etf_ibs_rsi2_longonly | reversal | 1993-11 | 29.1 | 6.9% | 7.4% | 0.64 | -15.6% | 0.19 (-0.13…0.51) | 0.163 | 37% | 0.764 | 23.0 | 0.92% |
| keller_paa_g12:top4 | tactical | 2008-05 | 14.6 | 5.9% | 9.0% | 0.63 | -14.6% | 0.12 (-0.37…0.59) | 0.351 | 5% | 0.673 | 3.4 | 0.68% |
| keller_paa_g12:breadth4 | tactical | 2008-05 | 14.6 | 5.2% | 7.9% | 0.62 | -13.8% | 0.11 (-0.40…0.59) | 0.370 | 5% | 0.659 | 3.1 | 0.62% |
| index_etf_ibs_rsi2_longonly:no_sma200 | reversal | 1993-11 | 29.1 | 9.4% | 12.3% | 0.61 | -32.8% | 0.16 (-0.07…0.39) | 0.131 | 43% | 0.716 | 33.6 | 1.34% |
| static_multifactor_equal_risk | factors | 1966-06 | 56.5 | 8.8% | 7.2% | 0.61 | -49.5% | 0.20 (-0.24…0.59) | 0.212 | 48% | 0.767 | 0.3 | 1.96% |
| sector_etf_top3_12m:hold_buffer | xsmom | 1927-07 | 95.4 | 13.1% | 18.0% | 0.60 | -75.7% | 0.17 (0.10…0.24) | 0.000 | 85% | 0.790 | 1.1 | 0.11% |
| trend_ma12_us_equity_cash_etf:signal_tr | macro | 1993-12 | 29.0 | 9.5% | 13.0% | 0.60 | -22.5% | 0.14 (-0.09…0.36) | 0.131 | 49% | 0.686 | 0.6 | 0.11% |
| trend_ma12_us_equity_cash_etf | macro | 1993-01 | 29.9 | 9.4% | 12.8% | 0.60 | -22.5% | 0.13 (-0.11…0.34) | 0.190 | 43% | 0.682 | 0.5 | 0.11% |
| trend_ma12_us_equity_cash_etf:sma10 | macro | 1993-01 | 29.9 | 9.2% | 12.6% | 0.59 | -23.0% | 0.12 (-0.11…0.34) | 0.188 | 45% | 0.673 | 0.7 | 0.13% |
| svxy_term_structure_filter:spy_secondary | volpremium | 2006-07 | 16.4 | 8.6% | 14.2% | 0.59 | -33.8% | 0.10 (-0.21…0.36) | 0.299 | 38% | 0.624 | 8.1 | 0.32% |
| xtsmom_us_switch_longcash | gap_crossasset_bond_equity_leadlag_signals | 1981-01 | 41.9 | 10.3% | 11.7% | 0.59 | -33.8% | 0.11 (-0.11…0.36) | 0.224 | 41% | 0.689 | 0.9 | 0.04% |
| trend_ma12_us_equity_cash | macro | 1930-01 | 92.9 | 9.6% | 11.8% | 0.58 | -37.4% | 0.14 (-0.01…0.29) | 0.066 | 36% | 0.713 | 0.6 | 0.12% |
| trend_ma12_us_equity_cash:sma10 | macro | 1930-01 | 92.9 | 9.6% | 11.7% | 0.58 | -37.3% | 0.14 (-0.01…0.29) | 0.064 | 38% | 0.711 | 0.7 | 0.15% |
| trend_ma12_us_equity_cash_etf:ma2_12 | macro | 1993-01 | 29.9 | 9.5% | 13.7% | 0.57 | -33.7% | 0.10 (-0.11…0.33) | 0.218 | 47% | 0.631 | 0.4 | 0.08% |
| trend_ma12_us_equity_cash:ma2_12 | macro | 1930-01 | 92.9 | 9.6% | 12.0% | 0.57 | -39.3% | 0.13 (-0.02…0.28) | 0.069 | 36% | 0.680 | 0.5 | 0.09% |
| lowvol_defensive_longonly:var | lowrisk | 1963-07 | 59.5 | 11.2% | 12.6% | 0.56 | -42.3% | 0.15 (-0.07…0.33) | 0.109 | 65% | 0.674 | 0.0 | 0.00% |
| xtsmom_us_switch_longcash:tlt | gap_crossasset_bond_equity_leadlag_signals | 1981-01 | 41.9 | 10.3% | 12.3% | 0.56 | -33.8% | 0.09 (-0.15…0.33) | 0.282 | 42% | 0.631 | 0.9 | 0.04% |
| xtsmom_us_switch_longcash:skip1 | gap_crossasset_bond_equity_leadlag_signals | 1981-01 | 41.9 | 10.0% | 11.8% | 0.56 | -33.8% | 0.08 (-0.14…0.33) | 0.279 | 35% | 0.624 | 1.0 | 0.04% |
| nagel_vix_gated_sector_etf_reversal:vix_20 | reversal | 2007-07 | 15.5 | 4.9% | 8.0% | 0.55 | -14.0% | 0.10 (-0.35…0.53) | 0.366 | 9% | 0.561 | 32.4 | 1.95% |
| eq_voltarget_ewma_harvey:vol_10 | volmgmt | 1928-01 | 95.0 | 8.4% | 10.0% | 0.55 | -46.9% | 0.11 (0.03…0.20) | 0.023 | 20% | 0.602 | 0.5 | 0.02% |
| trend_ma12_us_equity_cash:signal_tr | macro | 1930-01 | 92.9 | 9.3% | 12.1% | 0.54 | -45.7% | 0.11 (-0.04…0.25) | 0.121 | 31% | 0.588 | 0.7 | 0.13% |
| eq_voltarget_ewma_harvey | volmgmt | 1928-01 | 95.0 | 8.9% | 11.2% | 0.54 | -55.4% | 0.11 (0.03…0.19) | 0.015 | 19% | 0.579 | 0.4 | 0.02% |
| eq_voltarget_ewma_harvey_etf | volmgmt | 1994-02 | 28.9 | 7.9% | 11.4% | 0.54 | -31.0% | 0.08 (-0.04…0.18) | 0.126 | 37% | 0.559 | 0.5 | 0.02% |
| eq_voltarget_ewma_harvey_etf:vol_10 | volmgmt | 1994-02 | 28.9 | 7.2% | 10.0% | 0.53 | -24.6% | 0.08 (-0.05…0.18) | 0.149 | 35% | 0.552 | 0.6 | 0.02% |
| eq_voltarget_ewma_harvey:cap_1_5 | volmgmt | 1928-01 | 95.0 | 9.4% | 12.5% | 0.53 | -55.4% | 0.10 (0.01…0.20) | 0.048 | 41% | 0.552 | 1.1 | 0.04% |
| eq_voltarget_ewma_harvey_etf:cap_1_5 | volmgmt | 1994-02 | 28.9 | 8.2% | 12.2% | 0.53 | -31.0% | 0.07 (-0.06…0.19) | 0.164 | 37% | 0.550 | 1.0 | 0.04% |
| eq_voltarget_ewma_harvey:hl_40 | volmgmt | 1928-01 | 95.0 | 8.8% | 11.4% | 0.53 | -53.5% | 0.10 (0.02…0.18) | 0.025 | 18% | 0.538 | 0.2 | 0.01% |
| bond_composite_3sig_longonly_etf:only_value | gap_bonds_duration_curve_carry_mom_value | 2002-07 | 20.4 | 2.6% | 2.7% | 0.52 | -6.6% | 0.02 (-0.56…0.53) | 0.479 | 28% | 0.529 | 0.6 | 0.06% |
| halloween_nov_apr_equity_etf:cash_ief | calendar | 2002-10 | 20.2 | 8.0% | 14.7% | 0.52 | -35.6% | 0.01 (-0.25…0.30) | 0.482 | 45% | 0.528 | 2.0 | 0.08% |
| eq_voltarget_ewma_harvey_etf:hl_40 | volmgmt | 1994-02 | 28.9 | 7.9% | 11.7% | 0.52 | -28.1% | 0.06 (-0.04…0.16) | 0.146 | 39% | 0.529 | 0.2 | 0.01% |
| tom_spy_m2_p3_etf:tag_plus1 | calendar | 1993-02 | 29.8 | 4.5% | 4.5% | 0.52 | -11.6% | 0.05 (-0.34…0.43) | 0.409 | 33% | 0.526 | 12.0 | 0.48% |
| lowvol_defensive_longonly | lowrisk | 1963-07 | 59.5 | 10.4% | 12.6% | 0.51 | -43.4% | 0.10 (-0.11…0.29) | 0.231 | 50% | 0.508 | 0.0 | 0.00% |
| halloween_nov_apr_equity:dax | calendar | 1990-04 | 32.7 | 9.3% | 15.3% | 0.50 | -38.8% | 0.02 (-0.26…0.28) | 0.460 | 43% | 0.487 | 1.0 | 0.10% |
| bond_composite_3sig_longonly_etf:only_carry | gap_bonds_duration_curve_carry_mom_value | 2002-07 | 20.4 | 3.9% | 5.7% | 0.50 | -15.8% | -0.00 (-0.55…0.50) | 0.500 | 28% | 0.484 | 0.9 | 0.09% |
| bond_composite_3sig_longonly_etf | gap_bonds_duration_curve_carry_mom_value | 2002-07 | 20.4 | 3.0% | 3.8% | 0.49 | -8.7% | -0.01 (-0.59…0.50) | 0.513 | 28% | 0.470 | 1.3 | 0.13% |
| lowvol_defensive_longonly_etf:sector_proxy | lowrisk | 2001-12 | 21.0 | 7.8% | 15.5% | 0.49 | -41.6% | 0.06 (-0.08…0.22) | 0.252 | 45% | 0.465 | 0.5 | 0.05% |
| nagel_vix_gated_sector_etf_reversal:vix_30 | reversal | 2007-07 | 15.5 | 3.6% | 6.4% | 0.48 | -14.0% | 0.03 (-0.38…0.44) | 0.471 | 9% | 0.448 | 9.6 | 0.58% |
| halloween_nov_apr_equity | calendar | 1926-10 | 96.2 | 8.3% | 11.8% | 0.48 | -58.8% | 0.03 (-0.12…0.18) | 0.370 | 39% | 0.335 | 1.0 | 0.04% |
| faber_gtaa:sma_8 | tactical | 2006-09 | 16.2 | 4.5% | 8.1% | 0.47 | -18.5% | 0.00 (-0.37…0.29) | 0.486 | 13% | 0.447 | 1.0 | 0.10% |
| antonacci_gem_lookback_ensemble | tactical | 2004-09 | 18.2 | 7.1% | 14.5% | 0.46 | -31.0% | -0.02 (-0.28…0.23) | 0.524 | 30% | 0.427 | 1.8 | 0.36% |
| antonacci_gem_lookback_ensemble:single_l12 | tactical | 2004-09 | 18.2 | 7.5% | 15.7% | 0.46 | -33.7% | -0.02 (-0.27…0.24) | 0.528 | 30% | 0.425 | 1.3 | 0.27% |
| sector_etf_top3_12m_etf:sma10 | xsmom | 1999-12 | 23.0 | 7.0% | 13.6% | 0.46 | -24.0% | 0.13 (-0.15…0.42) | 0.225 | 46% | 0.411 | 2.6 | 0.26% |
| xtsmom_us_switch_longcash_etf:skip1 | gap_crossasset_bond_equity_leadlag_signals | 2003-07 | 19.4 | 6.5% | 13.0% | 0.46 | -33.7% | -0.04 (-0.30…0.29) | 0.571 | 33% | 0.418 | 2.1 | 0.09% |
| antonacci_gem_lookback_ensemble:bond_ief | tactical | 2004-09 | 18.2 | 7.0% | 14.4% | 0.46 | -30.3% | -0.02 (-0.32…0.26) | 0.526 | 30% | 0.418 | 1.8 | 0.36% |
| xtsmom_us_switch_longcash_etf | gap_crossasset_bond_equity_leadlag_signals | 2003-07 | 19.4 | 6.4% | 12.9% | 0.46 | -33.7% | -0.04 (-0.35…0.32) | 0.558 | 37% | 0.415 | 1.6 | 0.06% |
| ivp_risk_parity_unlevered:erc_lw | riskparity | 2008-02 | 14.8 | 3.6% | 7.0% | 0.46 | -18.7% | -0.05 (-0.45…0.33) | 0.593 | 5% | 0.422 | 0.2 | 0.02% |
| ivp_risk_parity_unlevered | riskparity | 2008-02 | 14.8 | 3.7% | 7.3% | 0.45 | -19.8% | -0.05 (-0.40…0.29) | 0.612 | 5% | 0.418 | 0.2 | 0.02% |
| faber_gtaa:sma_12 | tactical | 2007-01 | 15.9 | 4.1% | 7.9% | 0.45 | -12.6% | -0.01 (-0.37…0.35) | 0.518 | 14% | 0.411 | 0.9 | 0.09% |
| halloween_nov_apr_equity_etf | calendar | 1993-04 | 29.7 | 7.5% | 13.4% | 0.45 | -34.6% | -0.01 (-0.23…0.19) | 0.546 | 44% | 0.375 | 1.0 | 0.04% |
| faber_gtaa | tactical | 2006-11 | 16.1 | 4.2% | 8.2% | 0.44 | -14.4% | -0.02 (-0.34…0.29) | 0.535 | 13% | 0.398 | 1.0 | 0.10% |
| xtsmom_us_switch_longcash_etf:tlt | gap_crossasset_bond_equity_leadlag_signals | 2003-07 | 19.4 | 6.2% | 13.8% | 0.42 | -33.7% | -0.08 (-0.41…0.32) | 0.635 | 37% | 0.359 | 1.9 | 0.08% |
| putwrite_vrp_index:cost_025 | volpremium | 1996-08 | 26.4 | 7.6% | 15.8% | 0.42 | -37.2% | 0.00 (-0.13…0.18) | 0.482 | 50% | 0.321 | 0.0 | 0.00% |
| antonacci_gem_lookback_ensemble:acwx | tactical | 2009-04 | 13.7 | 5.7% | 14.8% | 0.41 | -31.0% | -0.37 (-0.53…-0.21) | 1.000 | 0% | 0.367 | 2.0 | 0.39% |
| ivp_risk_parity_unlevered:window_252 | riskparity | 2008-02 | 14.8 | 3.4% | 7.5% | 0.41 | -20.0% | -0.10 (-0.42…0.22) | 0.697 | 5% | 0.349 | 0.2 | 0.02% |
| bond_composite_3sig_longonly:only_carry | gap_bonds_duration_curve_carry_mom_value | 1972-03 | 50.8 | 6.7% | 6.1% | 0.41 | -16.9% | 0.02 (-0.34…0.34) | 0.464 | 29% | 0.237 | 0.5 | 0.05% |
| putwrite_vrp_index | volpremium | 1996-08 | 26.4 | 7.3% | 15.8% | 0.40 | -37.4% | -0.01 (-0.14…0.16) | 0.551 | 50% | 0.293 | 0.0 | 0.00% |
| commodity_gold_trend_dbc_gld:sma252 | crypto | 2007-02 | 15.9 | 4.7% | 11.1% | 0.40 | -29.4% | -0.06 (-0.59…0.43) | 0.573 | 9% | 0.328 | 3.3 | 0.67% |
| bond_composite_3sig_longonly | gap_bonds_duration_curve_carry_mom_value | 1972-03 | 50.8 | 5.9% | 4.2% | 0.39 | -9.7% | 0.01 (-0.35…0.33) | 0.498 | 25% | 0.212 | 0.7 | 0.07% |
| wml_volscaled_ff | xsmom | 1930-01 | 92.9 | 7.8% | 13.8% | 0.39 | -79.9% | -0.04 (-0.34…0.26) | 0.593 | 43% | 0.118 | 1.0 | 6.77% |
| nagel_vix_gated_sector_etf_reversal | reversal | 2007-07 | 15.5 | 3.5% | 7.7% | 0.39 | -19.9% | -0.06 (-0.53…0.36) | 0.582 | 9% | 0.322 | 39.3 | 2.36% |
| halloween_nov_apr_equity_etf:efa | calendar | 2001-10 | 21.2 | 6.1% | 14.8% | 0.39 | -33.9% | -0.05 (-0.32…0.24) | 0.619 | 39% | 0.297 | 1.0 | 0.04% |
| wml_volscaled_ff:cap_1 | xsmom | 1930-01 | 92.9 | 7.5% | 12.7% | 0.39 | -74.3% | -0.05 (-0.35…0.27) | 0.594 | 43% | 0.111 | 0.7 | 4.90% |
| sector_etf_top3_12m_etf:combo | xsmom | 1999-12 | 23.0 | 7.2% | 18.7% | 0.39 | -44.7% | 0.06 (-0.09…0.21) | 0.255 | 46% | 0.285 | 3.4 | 0.34% |
| sector_etf_top3_12m_etf | xsmom | 1999-12 | 23.0 | 7.1% | 18.9% | 0.38 | -45.5% | 0.05 (-0.09…0.20) | 0.270 | 46% | 0.267 | 2.8 | 0.28% |
| sector_etf_top3_12m_etf:hold_buffer | xsmom | 1999-12 | 23.0 | 7.3% | 20.3% | 0.38 | -53.3% | 0.05 (-0.08…0.18) | 0.257 | 51% | 0.263 | 1.1 | 0.11% |
| country_etf_xsmom_12_1:long_top5_sma10 | xsmom | 1997-03 | 25.8 | 6.7% | 15.4% | 0.38 | -39.5% | -0.03 (-0.30…0.22) | 0.581 | 48% | 0.252 | 2.3 | 0.23% |
| ivp_risk_parity_unlevered:hrp_252 | riskparity | 2008-02 | 14.8 | 2.7% | 6.3% | 0.37 | -17.8% | -0.13 (-0.63…0.33) | 0.677 | 5% | 0.300 | 0.5 | 0.05% |
| putwrite_vrp_index:cost_100 | volpremium | 1996-08 | 26.4 | 6.8% | 15.8% | 0.37 | -37.6% | -0.05 (-0.17…0.12) | 0.673 | 50% | 0.239 | 0.0 | 0.00% |
| commodity_gold_trend_dbc_gld | crypto | 2006-12 | 16.1 | 4.4% | 11.0% | 0.36 | -28.3% | -0.10 (-0.59…0.39) | 0.626 | 13% | 0.285 | 3.9 | 0.79% |
| tom_spy_m2_p3_etf | calendar | 1993-02 | 29.9 | 4.8% | 8.0% | 0.35 | -17.7% | -0.12 (-0.42…0.17) | 0.736 | 31% | 0.202 | 12.0 | 0.48% |
| tom_spy_m2_p3_etf:konservativ | calendar | 1993-02 | 29.8 | 4.6% | 8.2% | 0.33 | -21.4% | -0.14 (-0.43…0.14) | 0.798 | 24% | 0.168 | 12.0 | 0.48% |
| putwrite_vrp_index:from_2008 | volpremium | 2008-01 | 15.0 | 5.1% | 18.7% | 0.33 | -37.4% | -0.13 (-0.29…0.09) | 0.867 | 5% | 0.237 | 0.0 | 0.00% |
| wml_volscaled_ff:vol_target_19 | xsmom | 1930-01 | 92.9 | 8.0% | 21.4% | 0.33 | -94.8% | -0.11 (-0.41…0.20) | 0.728 | 47% | 0.033 | 1.6 | 10.58% |
| commodity_gold_trend_dbc_gld:sma168 | crypto | 2006-10 | 16.2 | 3.8% | 11.1% | 0.31 | -25.7% | -0.17 (-0.70…0.33) | 0.691 | 13% | 0.209 | 4.6 | 0.92% |
| commodity_gold_trend_dbc_gld:gold_only | crypto | 2005-09 | 17.3 | 4.5% | 14.3% | 0.30 | -37.6% | -0.17 (-0.69…0.32) | 0.722 | 20% | 0.197 | 3.9 | 0.78% |
| country_value_cape_faber_proxy:avg60 | valuecarry | 2001-12 | 21.0 | 5.2% | 23.0% | 0.29 | -61.0% | -0.14 (-0.33…0.05) | 0.880 | 30% | 0.155 | 0.4 | 0.08% |
| country_etf_xsmom_12_1:long_top5 | xsmom | 1997-03 | 25.8 | 5.7% | 21.4% | 0.28 | -62.9% | -0.13 (-0.31…0.04) | 0.881 | 38% | 0.125 | 2.6 | 0.26% |
| mop2012_tsmom_12m_40vol:lf | tsmom | 2008-02 | 14.8 | 2.4% | 7.4% | 0.28 | -16.8% | -0.23 (-0.72…0.21) | 0.816 | 0% | 0.186 | 1.9 | 0.37% |
| bond_composite_3sig_longonly:only_trend | gap_bonds_duration_curve_carry_mom_value | 1972-03 | 50.8 | 5.5% | 4.9% | 0.26 | -14.1% | -0.13 (-0.48…0.19) | 0.732 | 22% | 0.040 | 2.0 | 0.20% |
| tom_spy_m2_p3:tag_plus1 | calendar | 1926-07 | 96.4 | 4.0% | 3.7% | 0.25 | -14.4% | -0.19 (-0.41…0.04) | 0.921 | 24% | 0.006 | 12.0 | 0.48% |
| bond_composite_3sig_longonly_etf:only_trend | gap_bonds_duration_curve_carry_mom_value | 2002-07 | 20.4 | 2.2% | 4.7% | 0.24 | -10.0% | -0.26 (-0.80…0.24) | 0.791 | 28% | 0.117 | 4.2 | 0.42% |
| mop2012_tsmom_12m_40vol:portvol10 | tsmom | 2008-02 | 14.8 | 2.6% | 10.4% | 0.24 | -23.7% | -0.27 (-0.93…0.38) | 0.748 | 0% | 0.151 | 3.8 | 0.75% |
| bond_composite_3sig_longonly:only_value | gap_bonds_duration_curve_carry_mom_value | 1972-03 | 50.8 | 5.3% | 5.1% | 0.22 | -20.8% | -0.17 (-0.52…0.15) | 0.812 | 27% | 0.019 | 0.4 | 0.04% |
| country_value_cape_faber_proxy:june | valuecarry | 2006-06 | 16.5 | 2.9% | 23.3% | 0.20 | -59.0% | -0.28 (-0.48…-0.09) | 0.986 | 0% | 0.106 | 0.3 | 0.05% |
| country_value_cape_faber_proxy | valuecarry | 2006-12 | 16.0 | 2.8% | 23.1% | 0.20 | -57.6% | -0.26 (-0.47…-0.07) | 0.979 | 0% | 0.108 | 0.3 | 0.06% |
| country_value_cape_faber_proxy:quartile | valuecarry | 2006-12 | 16.0 | 2.4% | 23.7% | 0.18 | -56.9% | -0.28 (-0.48…-0.09) | 0.984 | 0% | 0.097 | 0.3 | 0.07% |
| mop2012_tsmom_12m_40vol | tsmom | 2008-02 | 14.8 | 2.0% | 16.6% | 0.17 | -36.7% | -0.34 (-0.98…0.26) | 0.818 | 0% | 0.096 | 4.7 | 0.94% |
| wml_volscaled_ff:static_w1 | xsmom | 1930-01 | 92.9 | -2.3% | 32.4% | 0.06 | -100.0% | -0.38 (-0.65…-0.08) | 0.981 | 39% | 0.000 | 1.2 | 8.19% |
| country_etf_xsmom_12_1 | xsmom | 1997-03 | 25.8 | -0.0% | 13.5% | -0.07 | -64.1% | -0.48 (-0.99…-0.02) | 0.949 | 24% | 0.002 | 5.3 | 0.53% |
| country_etf_xsmom_12_1:universe_ext | xsmom | 1997-03 | 25.8 | -0.4% | 13.9% | -0.10 | -68.0% | -0.50 (-0.98…-0.04) | 0.961 | 19% | 0.001 | 5.4 | 0.54% |

## Nach deutscher Steuer (Abgeltungsteuer, Teilfreistellung, Verkauf zum Schluss angenommen)

| Lauf | CAGR vor Steuer | CAGR nach Steuer | Steuerlast p.a. | Sharpe nach Steuer | SPY CAGR nach Steuer | Überrendite nach Steuer |
|---|---|---|---|---|---|---|
| crypto_trend_ens_btc_eth:sma50_btc | 93.6% | 75.4% | 18.23% | 1.27 | 8.6% | 66.8% |
| crypto_trend_ens_btc_eth:sma200_btc | 82.7% | 69.9% | 12.82% | 1.16 | 8.6% | 61.3% |
| crypto_trend_ens_btc_eth | 66.7% | 52.5% | 14.26% | 1.17 | 8.6% | 43.8% |
| svxy_term_structure_filter | 31.5% | 24.2% | 7.30% | 0.68 | 12.0% | 12.2% |
| sector_etf_top3_12m | 14.0% | 11.8% | 2.21% | 0.54 | 9.4% | 2.4% |
| sector_etf_top3_12m:combo | 13.9% | 11.6% | 2.21% | 0.53 | 9.4% | 2.2% |
| sector_etf_top3_12m:hold_buffer | 13.1% | 11.1% | 2.00% | 0.50 | 9.4% | 1.7% |
| lowvol_defensive_longonly:var | 11.2% | 10.8% | 0.38% | 0.53 | 9.8% | 1.0% |
| lowvol_defensive_longonly_etf | 11.8% | 10.4% | 1.40% | 0.70 | 11.1% | -0.6% |
| sector_etf_top3_12m:sma10 | 12.2% | 10.4% | 1.82% | 0.56 | 9.4% | 1.0% |
| lowvol_defensive_longonly | 10.4% | 10.1% | 0.38% | 0.48 | 9.8% | 0.3% |
| lowvol_defensive_longonly_etf:splv | 10.9% | 9.6% | 1.31% | 0.62 | 9.7% | -0.1% |
| xtsmom_us_switch_longcash | 10.3% | 8.8% | 1.54% | 0.46 | 10.5% | -1.7% |
| xtsmom_us_switch_longcash:tlt | 10.3% | 8.8% | 1.53% | 0.44 | 10.5% | -1.8% |
| xtsmom_us_switch_longcash:skip1 | 10.0% | 8.5% | 1.52% | 0.43 | 10.5% | -2.0% |
| trend_ma12_us_equity_cash | 9.6% | 8.3% | 1.35% | 0.46 | 9.3% | -1.1% |
| trend_ma12_us_equity_cash:ma2_12 | 9.6% | 8.2% | 1.35% | 0.46 | 9.3% | -1.1% |
| trend_ma12_us_equity_cash:sma10 | 9.6% | 8.2% | 1.36% | 0.46 | 9.3% | -1.1% |
| trend_ma12_us_equity_cash_etf:signal_tr | 9.5% | 8.1% | 1.42% | 0.49 | 8.8% | -0.7% |
| trend_ma12_us_equity_cash_etf:ma2_12 | 9.5% | 8.1% | 1.39% | 0.47 | 8.9% | -0.8% |
| static_multifactor_equal_risk:equal_weight | 9.6% | 8.0% | 1.56% | 0.47 | 9.8% | -1.7% |
| trend_ma12_us_equity_cash_etf | 9.4% | 8.0% | 1.39% | 0.49 | 8.9% | -0.9% |
| trend_ma12_us_equity_cash:signal_tr | 9.3% | 8.0% | 1.32% | 0.43 | 9.3% | -1.3% |
| index_etf_ibs_rsi2_longonly:no_sma200 | 9.4% | 8.0% | 1.42% | 0.50 | 8.8% | -0.8% |
| halloween_nov_apr_equity:dax | 9.3% | 7.9% | 1.40% | 0.41 | 9.5% | -1.5% |
| trend_ma12_us_equity_cash_etf:sma10 | 9.2% | 7.9% | 1.38% | 0.48 | 8.9% | -1.0% |
| eq_voltarget_ewma_harvey:cap_1_5 | 9.4% | 7.8% | 1.53% | 0.42 | 9.3% | -1.5% |
| tom_spy_m2_p3 | 8.9% | 7.8% | 1.15% | 0.64 | 9.6% | -1.8% |
| eq_voltarget_ewma_harvey:hl_40 | 8.8% | 7.8% | 1.04% | 0.44 | 9.3% | -1.6% |
| svxy_term_structure_filter:w025 | 10.1% | 7.7% | 2.42% | 0.52 | 12.0% | -4.3% |
| eq_voltarget_ewma_harvey | 8.9% | 7.7% | 1.18% | 0.44 | 9.3% | -1.6% |
| eq_voltarget_ewma_harvey:vol_10 | 8.4% | 7.2% | 1.17% | 0.43 | 9.3% | -2.1% |
| halloween_nov_apr_equity | 8.3% | 7.1% | 1.18% | 0.38 | 9.6% | -2.5% |
| tom_spy_m2_p3:konservativ | 8.1% | 7.1% | 1.01% | 0.53 | 9.6% | -2.4% |
| static_multifactor_equal_risk | 8.8% | 7.0% | 1.72% | 0.37 | 9.8% | -2.7% |
| eq_voltarget_ewma_harvey_etf:cap_1_5 | 8.2% | 6.9% | 1.30% | 0.43 | 8.8% | -1.9% |
| svxy_term_structure_filter:spy_secondary | 8.6% | 6.9% | 1.72% | 0.47 | 8.0% | -1.1% |
| putwrite_vrp_index:cost_025 | 7.6% | 6.9% | 0.70% | 0.37 | 7.8% | -0.9% |
| eq_voltarget_ewma_harvey_etf:hl_40 | 7.9% | 6.8% | 1.09% | 0.43 | 8.8% | -2.0% |
| eq_voltarget_ewma_harvey_etf | 7.9% | 6.8% | 1.16% | 0.44 | 8.8% | -2.0% |
| lowvol_defensive_longonly_etf:sector_proxy | 7.8% | 6.8% | 1.07% | 0.42 | 6.9% | -0.2% |
| wml_volscaled_ff:vol_target_19 | 8.0% | 6.7% | 1.36% | 0.27 | 9.3% | -2.6% |
| wml_volscaled_ff | 7.8% | 6.7% | 1.17% | 0.31 | 9.3% | -2.7% |
| putwrite_vrp_index | 7.3% | 6.6% | 0.69% | 0.36 | 7.8% | -1.2% |
| wml_volscaled_ff:cap_1 | 7.5% | 6.5% | 0.96% | 0.32 | 9.3% | -2.8% |
| halloween_nov_apr_equity_etf | 7.5% | 6.4% | 1.18% | 0.36 | 8.9% | -2.5% |
| halloween_nov_apr_equity_etf:cash_ief | 8.0% | 6.3% | 1.76% | 0.41 | 8.5% | -2.3% |
| antonacci_gem_lookback_ensemble:single_l12 | 7.5% | 6.2% | 1.29% | 0.38 | 8.0% | -1.7% |
| eq_voltarget_ewma_harvey_etf:vol_10 | 7.2% | 6.2% | 1.05% | 0.43 | 8.8% | -2.6% |
| sector_etf_top3_12m_etf:hold_buffer | 7.3% | 6.1% | 1.16% | 0.32 | 5.3% | 0.8% |
| putwrite_vrp_index:cost_100 | 6.8% | 6.1% | 0.66% | 0.33 | 7.8% | -1.7% |
| sector_etf_top3_12m_etf:combo | 7.2% | 6.0% | 1.21% | 0.33 | 5.3% | 0.7% |
| index_etf_ibs_rsi2_longonly | 6.9% | 5.9% | 0.94% | 0.52 | 8.8% | -2.9% |
| sector_etf_top3_12m_etf:sma10 | 7.0% | 5.9% | 1.12% | 0.38 | 5.3% | 0.6% |
| sector_etf_top3_12m_etf | 7.1% | 5.9% | 1.17% | 0.32 | 5.3% | 0.6% |
| antonacci_gem_lookback_ensemble | 7.1% | 5.9% | 1.25% | 0.38 | 8.0% | -2.1% |
| antonacci_gem_lookback_ensemble:bond_ief | 7.0% | 5.8% | 1.24% | 0.38 | 8.0% | -2.2% |
| country_etf_xsmom_12_1:long_top5_sma10 | 6.7% | 5.6% | 1.01% | 0.31 | 7.5% | -1.9% |
| index_etf_ibs_rsi2_longonly:connors_rsi2 | 6.5% | 5.6% | 0.82% | 0.52 | 8.8% | -3.2% |
| bond_composite_3sig_longonly:only_carry | 6.7% | 5.6% | 1.09% | 0.22 | 9.3% | -3.7% |
| xtsmom_us_switch_longcash_etf | 6.4% | 5.2% | 1.24% | 0.36 | 8.2% | -3.0% |
| xtsmom_us_switch_longcash_etf:skip1 | 6.5% | 5.1% | 1.37% | 0.36 | 8.2% | -3.1% |
| xtsmom_us_switch_longcash_etf:tlt | 6.2% | 5.0% | 1.19% | 0.34 | 8.2% | -3.2% |
| halloween_nov_apr_equity_etf:efa | 6.1% | 5.0% | 1.02% | 0.32 | 7.3% | -2.3% |
| bond_composite_3sig_longonly | 5.9% | 5.0% | 0.93% | 0.18 | 9.3% | -4.4% |
| country_etf_xsmom_12_1:long_top5 | 5.7% | 4.9% | 0.86% | 0.24 | 7.5% | -2.7% |
| bond_composite_3sig_longonly:only_trend | 5.5% | 4.8% | 0.73% | 0.12 | 9.3% | -4.6% |
| keller_paa_g12:top4 | 5.9% | 4.7% | 1.26% | 0.49 | 7.9% | -3.2% |
| keller_paa_g12 | 5.9% | 4.7% | 1.25% | 0.52 | 7.9% | -3.2% |
| antonacci_gem_lookback_ensemble:acwx | 5.7% | 4.6% | 1.09% | 0.34 | 12.0% | -7.4% |
| nagel_vix_gated_sector_etf_reversal:vix_25 | 5.5% | 4.5% | 0.95% | 0.54 | 6.8% | -2.3% |
| keller_paa_g12:sleeves3 | 5.7% | 4.5% | 1.23% | 0.51 | 7.9% | -3.4% |
| bond_composite_3sig_longonly:only_value | 5.3% | 4.5% | 0.85% | 0.06 | 9.3% | -4.9% |
| putwrite_vrp_index:from_2008 | 5.1% | 4.3% | 0.71% | 0.29 | 6.9% | -2.5% |
| country_value_cape_faber_proxy:avg60 | 5.2% | 4.3% | 0.95% | 0.25 | 6.9% | -2.6% |
| tom_spy_m2_p3_etf | 4.8% | 4.2% | 0.56% | 0.28 | 9.0% | -4.8% |
| tom_spy_m2_p3_etf:konservativ | 4.6% | 4.1% | 0.52% | 0.27 | 8.9% | -4.8% |
| tom_spy_m2_p3_etf:tag_plus1 | 4.5% | 4.1% | 0.44% | 0.42 | 8.9% | -4.8% |
| keller_paa_g12:breadth4 | 5.2% | 4.1% | 1.14% | 0.47 | 7.9% | -3.8% |
| nagel_vix_gated_sector_etf_reversal:vix_20 | 4.9% | 3.9% | 0.91% | 0.43 | 6.8% | -2.9% |
| tom_spy_m2_p3:tag_plus1 | 4.0% | 3.8% | 0.20% | 0.20 | 9.6% | -5.8% |
| faber_gtaa:sma_8 | 4.5% | 3.7% | 0.80% | 0.38 | 7.5% | -3.8% |
| commodity_gold_trend_dbc_gld:sma252 | 4.7% | 3.6% | 1.10% | 0.30 | 7.1% | -3.5% |
| faber_gtaa | 4.2% | 3.5% | 0.73% | 0.35 | 7.3% | -3.8% |
| faber_gtaa:sma_12 | 4.1% | 3.4% | 0.76% | 0.35 | 7.2% | -3.8% |
| commodity_gold_trend_dbc_gld | 4.4% | 3.4% | 1.01% | 0.27 | 7.3% | -3.9% |
| commodity_gold_trend_dbc_gld:gold_only | 4.5% | 3.2% | 1.27% | 0.21 | 7.7% | -4.4% |
| nagel_vix_gated_sector_etf_reversal:vix_30 | 3.6% | 3.0% | 0.57% | 0.38 | 6.8% | -3.8% |
| ivp_risk_parity_unlevered | 3.7% | 3.0% | 0.70% | 0.36 | 7.9% | -4.9% |
| commodity_gold_trend_dbc_gld:sma168 | 3.8% | 2.9% | 0.85% | 0.23 | 7.6% | -4.6% |
| ivp_risk_parity_unlevered:erc_lw | 3.6% | 2.9% | 0.69% | 0.36 | 7.9% | -5.0% |
| bond_composite_3sig_longonly_etf:only_carry | 3.9% | 2.8% | 1.09% | 0.30 | 8.4% | -5.6% |
| nagel_vix_gated_sector_etf_reversal | 3.5% | 2.8% | 0.72% | 0.30 | 6.8% | -4.1% |
| ivp_risk_parity_unlevered:window_252 | 3.4% | 2.7% | 0.66% | 0.32 | 7.9% | -5.2% |
| country_value_cape_faber_proxy:june | 2.9% | 2.4% | 0.52% | 0.18 | 7.8% | -5.4% |
| country_value_cape_faber_proxy | 2.8% | 2.3% | 0.50% | 0.18 | 7.2% | -4.9% |
| bond_composite_3sig_longonly_etf | 3.0% | 2.2% | 0.82% | 0.27 | 8.4% | -6.2% |
| ivp_risk_parity_unlevered:hrp_252 | 2.7% | 2.1% | 0.66% | 0.27 | 7.9% | -5.9% |
| mop2012_tsmom_12m_40vol:portvol10 | 2.6% | 2.0% | 0.54% | 0.19 | 7.9% | -5.9% |
| bond_composite_3sig_longonly_etf:only_value | 2.6% | 1.9% | 0.63% | 0.26 | 8.4% | -6.4% |
| country_value_cape_faber_proxy:quartile | 2.4% | 1.9% | 0.46% | 0.16 | 7.2% | -5.3% |
| mop2012_tsmom_12m_40vol:lf | 2.4% | 1.8% | 0.54% | 0.20 | 7.9% | -6.1% |
| bond_composite_3sig_longonly_etf:only_trend | 2.2% | 1.6% | 0.65% | 0.11 | 8.4% | -6.8% |
| mop2012_tsmom_12m_40vol | 2.0% | 1.5% | 0.55% | 0.14 | 7.9% | -6.5% |
| country_etf_xsmom_12_1 | -0.0% | -0.2% | 0.20% | -0.09 | 7.5% | -7.8% |
| country_etf_xsmom_12_1:universe_ext | -0.4% | -0.6% | 0.20% | -0.11 | 7.5% | -8.2% |
| wml_volscaled_ff:static_w1 | -2.3% | -2.4% | 0.08% | 0.06 | 9.3% | -11.7% |