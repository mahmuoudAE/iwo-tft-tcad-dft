# Experimental vs simulation: staged calibration ledger and result

All numbers below are read from real ATLAS launches (`results/RUN_INDEX.csv`, one directory per launch with the deck, the raw DeckBuild log, transfer.log and the exported currents). The metric tables generated from the final runs are `tables/EXPERIMENTAL_VS_SIMULATION.{csv,md}` (identical extractor for both curves, `scripts/extract_metrics.py`). The measured curves are the raw workbook values converted once to A/um (`data/experimental_clean.csv`).

Scoring: "active" = measured points above 5x the measured off-band median (Vg in [-2, -0.5] V) - the region where the measurement carries device information; log RMSE in decades. Native ATLAS zeros (currents below the strict-acceptance floor ~1e-17 A/um) are counted and excluded, never floored. Vth = constant current 1e-9 A/um; SS = steepest 0.2 V window above 5x the measured floor of the same device (same range for both curves); mu_FE = gm,max L/(W Cox Vd).

## Stage ledger (what was free at each stage, and what each launch showed)

| stage | free parameters | run(s) | result |
|---|---|---|---|
| 1-2. Laws only (dEg_QC, m*, Nc, Nt, WTA, Nd laws, Dit 3e11, Qf = 0, WF 4.70, mu_band from V0) | none tuned | run_0001 (2 nm), run_0002 (13.2 nm) | Both curves have the measured SHAPE (SS_min sim/meas: 81/84 at 2 nm, 146/131 at 13.2 nm) but sit +0.33 V (2 nm) and +0.29 V (13.2 nm) too positive in Vth_cc; Ion -27 % / -21 % (mostly the lost overdrive). Active log RMSE 3.93 / 1.03 dec. |
| 3. One shared flat-band offset: Qf = +1.73e12 cm^-2 (dVfb = -q Qf/Cox = -0.31 V), everything else unchanged | 1 shared | run_0003 (2 nm), run_0004 (13.2 nm) | 2 nm: active RMSE 0.056 dec, dVth +0.02 V, Ion -7.3 %. 13.2 nm: 0.086 dec, dVth -0.02 V, Ion -7.0 %. One number fixes both devices because their baseline offsets agree to 40 mV, i.e. the 0.35 eV confinement difference dEc(2 nm) - dEc(13.2 nm) predicted by the DFT-proxy law is consistent with the measured 0.58 V threshold difference once Nd(t), Nt(t) and Nc(t) are included (tested in ATLAS, not assumed). |
| 5. Cross-thickness test: 6.3 nm with the stage-3 parameters untouched | 0 | run_0005 (6.3 nm) | FAILS on threshold: Vth_cc sim 0.35 V vs measured 0.64 V (-0.29 V); the SHAPE is reproduced (SS_min 108 vs 115 mV/dec; SS_cc 285 vs 295). Active RMSE 0.68 dec, Ion +27 % (overdrive). The measured 6.3 nm threshold equals the 2 nm one (0.64 vs 0.66 V) although every law places it ~0.3 V lower; both earlier lineages needed a device-specific parameter for this film as well. Cause NOT DETERMINED FROM AVAILABLE DATA (candidates: a different fixed charge/aging state of that sample, a thickness or process deviation, or a non-monotonic confinement/donor behaviour between 2 and 6 nm). |
| 5b. 6.3 nm device-specific flat-band offset: Qf(6.3) = +8.7e10 cm^-2 (i.e. -0.29 V relative to the shared value); nothing else changed | 1 device-specific | run_0007 | see final table |
| 5. 31.8 nm with the stage-3 parameters (Nd law 1.85e18, series R 9.2e4 ohm.um hypothesis from V0, no back-surface sheet) | 0 (+1 inherited Rs) | run_0006 | see final table |
| 6. Band mobility refit to Ion at fixed electrostatics (mu_band is declared FITTED per thickness): 2 nm 16.8 -> 18.13, 13.2 nm 57.6 -> 61.9 cm^2/Vs | 1 per thickness (already counted as fitted) | run_0008 (2 nm), run_0009 (13.2 nm) | 2 nm: active RMSE 0.037 dec, Ion +0.01 %, Vth_cc 0.68 vs 0.66 V, SS_min 73 vs 84 mV/dec, mu_FE 11.3 vs 12.1. 13.2 nm: 0.081 dec, Ion -0.02 %, Vth_cc 0.05 vs 0.08 V, SS_min 151 vs 131, mu_FE 49.0 vs 50.2. |
| 5b result | | run_0007 (6.3 nm) | active RMSE 0.082 dec, Vth_cc 0.64 vs 0.64 V, SS_min 111 vs 115, mu_FE 8.9 vs 10.9, Ion +6.1 %. |
| aborted | 31.8 nm back-surface hypothesis (run_0010: ATLAS stopped during SOLVE INIT after 18 s with no error text; not investigated) and 6.3 nm mobility stage (run_0011: launched, then the whole chain was stopped by the user). Neither produced currents. | | User directive (2026-09-21): stop at three runs, exclude 31.8 nm. |
| 7. Final form requested by the user: physical structure (Air / Pd S/D volumes / Al2O3 / HfO2 / Conductor gate = TiN) and stepped SOLVE VSTEP/VFINAL sweep (0.2 V in deep depletion, 0.05 V from -1 to 1.5 V, 0.1 V above); same parameters as stage 6 | 0 new | run_0012 (2 nm), run_0013 (13.2 nm), run_0014 (6.3 nm with the SHARED parameters only = validation) | see final table; run_0012 vs run_0008 is also the structure/sweep equivalence check (docs/NUMERICAL_CONVERGENCE.md) |
| 8. 6.3 nm tuned (user request after the validation miss): the device-specific offset of stage 5b (Qf 8.7e10) plus the mobility stage (mu_band 12.4 -> 11.69, removing the +6.1 % Ion of run_0007) | 1 device-specific + 1 fitted mobility | run_0015 | active RMSE 0.063 dec, Ion -0.01 %, Vth 0.65 vs 0.64 V, SS_min 111 vs 115, mu_FE 8.4 vs 10.9; residual within +/-0.1 dec over the active region (+0.2 dec at the single point where the measured curve leaves its floor) |

Parameter count (four devices): shared laws with no tuning (dEg_QC, m*, Nc, WTA, Dit, Nt law, Nd law), 1 shared fitted electrostatic value (Qf), 4 fitted band mobilities, 1 device-specific offset (6.3 nm), 1 hypothesis (31.8 nm series resistance) [and any 31.8 nm adjustment recorded below]. Astra: per-device Nd, Nt, WTA, mu and a shared WF/Qf pair (3 devices); Claude V0: per-device Nd, NTA, WTA, mu, Qf, Dit (4 devices).

## Final comparison (runs 0012-0014; generated table: tables/EXPERIMENTAL_VS_SIMULATION.md)

| t (nm) | run | role | Vth_cc exp / sim (V) | SS_min exp / sim | SS_cc(1e-10..1e-8) exp / sim | mu_FE exp / sim | Ion exp / sim (A/um) | active log RMSE | zeros |
|---|---|---|---|---|---|---|---|---|---|
| 2.0 | run_0012 | calibrated | 0.66 / 0.68 | 84 / 73 | 270 / 294 | 12.1 / 11.3 | 5.09e-7 / 5.09e-7 (+0.0 %) | 0.037 dec | 24 |
| 13.2 | run_0013 | calibrated | 0.08 / 0.05 | 131 / 151 | 160 / 195 | 50.2 / 49.0 | 3.07e-6 / 3.07e-6 (-0.0 %) | 0.081 dec | 37 |
| 6.3 | run_0014 | VALIDATION, shared parameters | 0.64 / 0.35 | 115 / 108 | 295 / 285 | 10.9 / 9.1 | 4.03e-7 / 5.11e-7 (+26.8 %) | 0.678 dec | 23 |
| 6.3 | run_0015 | TUNED: Qf 8.7e10 (device-specific, +0.29 V), mu_band 11.69 | 0.64 / 0.65 | 115 / 111 | 295 / 289 | 10.9 / 8.4 | 4.03e-7 / 4.03e-7 (-0.0 %) | 0.063 dec | 25 |

Reading: the two calibrated films are reproduced to < 0.1 dec over the active region with one shared electrostatic value and one band mobility each; the residual structure (13.2 nm: +0.45 dec at the point where the measured curve leaves its 6.6e-12 A/um floor, -0.1 dec around 0.5 V; 2 nm: -0.08 dec around 1 V) is documented in plots/<t>/residual.png. The 6.3 nm validation fails on the threshold (-0.29 V) and, as a consequence of the overdrive, on Ion (+27 %); its shape metrics agree within 7 %. The identical run with one device-specific flat-band offset (run_0007, reduced deck) reaches 0.082 dec and +6 % Ion, which bounds what the shared model misses: one electrostatic number for that film.

Calibration vs validation: 2 nm and 13.2 nm are calibrated (Qf fitted on both, mu_band on each); 6.3 nm is a genuine out-of-sample test of the shared laws and it is reported as a miss. Nothing is validated against a second bias, temperature or device.

Interpretation and the readiness statement are in `docs/SUPERVISOR_SUMMARY.md` and `FINAL_STATUS.md`.

## What the off-state comparison means

The simulated minimum currents are numerical zeros/1e-19-1e-21 A/um; the measured floors (5e-15, 1.5e-13, 6.6e-12 A/um for 2, 6.3, 13.2 nm; 2.7e-7 A/um always-on for 31.8 nm) are not modelled and no mechanism is inserted to reproduce them. Ion/Ioff for the simulation is therefore a lower bound and is not compared in per cent. This is stated in every table.
