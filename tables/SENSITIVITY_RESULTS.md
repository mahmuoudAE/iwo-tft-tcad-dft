# Sensitivity results (V1)

Rows marked MEASURED IN ATLAS come from pairs of executed runs that differ in exactly one input; rows marked NOT RUN are the planned one-at-a-time cases that were not launched (user directive). No sensitivity below is estimated analytically.

| t (nm) | parameter | from | to | runs | dVth_cc (V) | dSS_min (mV/dec) | dmu_FE (%) | dIon (%) | active RMSE ref -> pert | status / note |
|---|---|---|---|---|---|---|---|---|---|---|
| 2.0 | Qf (fixed interface charge, cm^-2) | 0 | 1.73e12 | run_0001 -> run_0003 | -0.309 | +2.25 | +2.64 | +27.1 | 3.928 -> 0.056 | MEASURED IN ATLAS (stage pair); dVth = -0.309 V for dQf = 1.73e12 cm^-2: -q dQf/Cox = -0.3095 V (Cox 8.955e-7 F/cm^2) -> the solver reproduces the flat-band relation exactly |
| 13.2 | Qf (fixed interface charge, cm^-2) | 0 | 1.73e12 | run_0002 -> run_0004 | -0.31 | +5.09 | +1.39 | +18.2 | 1.030 -> 0.086 | MEASURED IN ATLAS (stage pair) |
| 2.0 | mu_band (cm^2/Vs) | 16.8 | 18.13 | run_0003 -> run_0008 | -0.00923 | -9.89 | +7.92 | +7.92 | 0.056 -> 0.037 | MEASURED IN ATLAS (stage pair); Ion scales ~linearly with mu_band at fixed electrostatics (+7.9 % mu -> +7.9 % Ion) |
| 13.2 | mu_band (cm^2/Vs) | 57.6 | 61.9 | run_0004 -> run_0009 | -0.00618 | +5.68e-05 | +7.47 | +7.47 | 0.086 -> 0.081 | MEASURED IN ATLAS (stage pair) |
| 6.3 | Qf (fixed interface charge, cm^-2) | 1.73e12 | 8.7e10 | run_0005 -> run_0007 | +0.294 | +2.58 | -2.09 | -16.3 | 0.678 -> 0.082 | MEASURED IN ATLAS (stage pair) |
| 2.0 | structure + sweep form (reduced/pointwise -> physical/stepped) | reduced, 121 pts | physical, 76 pts | run_0008 -> run_0012 | -6.57e-05 | +0.00609 | -0.17 | -0.00236 | 0.037 -> 0.037 | MEASURED IN ATLAS (stage pair) |
| 13.2 | structure + sweep form (reduced/pointwise -> physical/stepped) | reduced, 121 pts | physical, 76 pts | run_0009 -> run_0013 | -9.27e-05 | +0.021 | -0.104 | +0.000326 | 0.081 -> 0.081 | MEASURED IN ATLAS (stage pair) |
| 2.0 | OAT no_confinement: thickness_laws.dEg_QC_eV.a=0 thickness_laws.mstar_m0.b=0 | final | no_confinement | run_0012 -> run_0016 | -0.316 | +10.7 | +0.549 | +21.4 | 0.037 -> 0.846 | MEASURED IN ATLAS (one-at-a-time, vs the final run) |
| 13.2 | OAT no_confinement: thickness_laws.dEg_QC_eV.a=0 thickness_laws.mstar_m0.b=0 | final | no_confinement | run_0013 -> run_0017 | -0.0234 | -12.7 | -0.0782 | +0.93 | 0.081 -> 0.114 | MEASURED IN ATLAS (one-at-a-time, vs the final run) |
| 2.0 | OAT chi_m0p1: bulk_reference.chi_bulk_eV.value=4.20 | final | chi_m0p1 | run_0012 -> run_0020 | +0.1 | -0.000747 | -0.719 | -6.94 | 0.037 -> 0.463 | MEASURED IN ATLAS (one-at-a-time, vs the final run) |
| 2.0 | OAT chi_p0p1: bulk_reference.chi_bulk_eV.value=4.40 | final | chi_p0p1 | run_0012 -> run_0021 | -0.1 | -0.00149 | +0.617 | +6.98 | 0.037 -> 0.361 | MEASURED IN ATLAS (one-at-a-time, vs the final run) |
| 2.0 | OAT nd_x2: thickness_laws.Nd_eff_cm3.Nd0=5e17 | final | nd_x2 | run_0012 -> run_0022 | -0.00948 | +1.56 | +0.105 | +0.688 | 0.037 -> 0.054 | MEASURED IN ATLAS (one-at-a-time, vs the final run) |
| 2.0 | OAT nt_x1p5: thickness_laws.Nt_cm3.Nt2=3e19 | final | nt_x1p5 | run_0012 -> run_0023 | +0.082 | +3.15 | -6.78 | -25.1 | 0.037 -> 0.263 | MEASURED IN ATLAS (one-at-a-time, vs the final run) |
| 2.0 | OAT wta_p5meV: thickness_laws.WTA_eV.value=0.045 | final | wta_p5meV | run_0012 -> run_0024 | +0.0197 | +12.4 | +0.32 | +0.434 | 0.037 -> 0.063 | MEASURED IN ATLAS (one-at-a-time, vs the final run) |
| 2.0 | OAT dit_x3: traps.interface_acceptor_sheet.peak_cm2_eV=9e11 | final | dit_x3 | run_0012 -> run_0025 | +0.025 | +9.37 | -0.176 | -1.8 | 0.037 -> 0.098 | MEASURED IN ATLAS (one-at-a-time, vs the final run) |
| 2.0 | OAT eps_10p55: bulk_reference.eps_r.value=10.55 | final | eps_10p55 | run_0012 -> run_0026 | -0.000882 | -0.0709 | +0.629 | +0.685 | 0.037 -> 0.037 | MEASURED IN ATLAS (one-at-a-time, vs the final run) |
| 2.0 | OAT overlap_4um: geometry.contact_overlap_um.value=4.0 | final | overlap_4um | run_0012 -> run_0027 | -0.000956 | +0.0218 | -1.76 | -2.17 | 0.037 -> 0.038 | MEASURED IN ATLAS (one-at-a-time, vs the final run) |
|  | gate work function +0.1 eV (same action as Qf: -q dQf/Cox) |  |  |  ->  | - | - | - | - | - -> - | NOT RUN (see docs/NUMERICAL_CONVERGENCE.md for the refinement checks; other cases not launched) |
|  | m* = bulk only |  |  |  ->  | - | - | - | - | - -> - | NOT RUN (see docs/NUMERICAL_CONVERGENCE.md for the refinement checks; other cases not launched) |
|  | any case at 6.3 nm |  |  |  ->  | - | - | - | - | - -> - | NOT RUN (see docs/NUMERICAL_CONVERGENCE.md for the refinement checks; other cases not launched) |
