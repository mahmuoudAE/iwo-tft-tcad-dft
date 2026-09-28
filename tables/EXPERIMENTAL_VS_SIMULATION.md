# Experimental vs simulation (V1 best verified runs)

Same extractor for both curves (scripts/extract_metrics.py): Vth = constant current 1e-9 A/um (log interpolation); SS = steepest 0.2 V window with Id above 5x the MEASURED off floor of that thickness and below 1 % of Ion, applied to both curves so the same current range is evaluated (SS_cc, the average slope between the 1e-10 and 1e-8 A/um crossings, is in the CSV); mu_FE = gm_max L/(W Cox Vd) at Vd = 0.7 V; Ion = Id(+3 V); Ioff = min Id (simulation: min POSITIVE Id, native zeros counted). Currents in A/um. Vth differences are absolute (no % for sign-changing quantities).

| t (nm) | run | Vth_exp (V) | Vth_sim (V) | dVth (V) | SS_exp | SS_sim (mV/dec) | mu_exp | mu_sim (cm^2/Vs) | Ion_exp | Ion_sim | dIon % | Ioff_exp | Ioff_sim (min pos.) | zeros | Ion/Ioff exp | Ion/Ioff sim | active log RMSE | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2.0 | run_0012 | 0.66 | 0.68 | +0.01 | 84 | 73 | 12.1 | 11.3 | 5.09e-07 | 5.09e-07 | +0.0 | 1.1e-16 | 5.4e-21 | 24 | 4.7e+09 | 9.4e+13 (>) | 0.037 | calibrated: shared Qf + fitted mu_band 18.13; physical structure, stepped sweep (rescored under the median-floor KCL rule, see NUMERICAL_CONVERGENCE G') |
| 6.3 | run_0015 | 0.64 | 0.65 | +0.01 | 115 | 111 | 10.9 | 8.4 | 4.03e-07 | 4.03e-07 | -0.0 | 5.9e-15 | 6.7e-22 | 25 | 6.9e+07 | 6.0e+14 (>) | 0.063 | TUNED: device-specific Qf 8.7e10 (+0.29 V vs the shared value; cause NOT DETERMINED) + fitted mu_band 11.69; physical structure, stepped sweep |
| 13.2 | run_0013 | 0.08 | 0.05 | -0.03 | 131 | 151 | 50.2 | 49.0 | 3.07e-06 | 3.07e-06 | -0.0 | 6.4e-12 | 3.0e-20 | 37 | 4.8e+05 | 1.0e+14 (>) | 0.081 | calibrated: shared Qf + fitted mu_band 61.9; physical structure, stepped sweep |
| 6.3 | run_0014 | 0.64 | 0.35 | -0.29 | 115 | 108 | 10.9 | 9.1 | 4.03e-07 | 5.11e-07 | +26.8 | 5.9e-15 | 1.3e-21 | 23 | 6.9e+07 | 4.1e+14 (>) | 0.678 | VALIDATION with the shared parameters only (Qf 1.73e12, mu_band 12.4): shape reproduced, threshold -0.29 V |

Ioff_sim is the minimum positive simulated current; where native zeros exist the simulated Ion/Ioff is a lower bound and no percentage error is reported. The measured off-state floors are not modelled (docs/LIMITATIONS.md).
