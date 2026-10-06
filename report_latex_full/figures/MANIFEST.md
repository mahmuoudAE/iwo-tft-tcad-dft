## stack_schematic
Drawn from config/geometry.yaml and docs/DEVICE_STRUCTURE.md; region numbers as in build_iwo_decks.py (full structure).

## measured_transfer
data/experimental_clean.csv, Vd 0.7 V. Dotted: off-band median (-2..-0.5 V): 2.0 nm floor 4.61e-15 A/um; 6.3 nm floor 1.53e-13 A/um; 13.2 nm floor 6.60e-12 A/um

## measured_metrics
Measured metrics: {"2.0": {"vcc": 0.6618, "vlin": 1.6631, "ss1": 121.2073, "ss2": 269.8986, "mufe": 12.1459, "musat": 5.0867, "ion": 5.08966e-07, "fl": 0.0}, "6.3": {"vcc": 0.644, "vlin": 1.82, "ss1": 124.4921, "ss2": 295.367, "mufe": 10.9467, "musat": 3.8585, "ion": 4.03448e-07, "fl": 0.0}, "13.2": {"vcc": 0.0825, "vlin": 1.0441, "ss1": 136.1494, "ss2": 160.0202, "mufe": 50.1662, "musat": 27.4041, "ion": 3.07069e-06, "fl": 7e-12}}

## numerics_convergence
Runs 0012/0019/0029 (DOS), 0013/0028 and 0015/0036 (mesh), offsets from S6 report section 1 (B1-B3), SS_min artefact threshold 2.30e-14 A/um (S6).

## calibrated_overlays
Active region = measured > 5x off-band median. 2.0 nm: run_0038 x1.000000: Vth_cc 0.680, Vth_lin 1.537, mu_FE 11.10, Ion 5.09e-07; active rms 0.0429 dec | 6.3 nm: run_0039 x1.015073: Vth_cc 0.653, Vth_lin 1.466, mu_FE 8.39, Ion 4.034e-07; active rms 0.0630 dec | 13.2 nm: run_0040 x1.020112: Vth_cc 0.054, Vth_lin 0.995, mu_FE 48.85, Ion 3.071e-06; active rms 0.0813 dec

## calibration_history
Stage runs from results/runs; see ch. 7 table for metrics.

## param_control_2nm
Pairs (label, base, perturbed): Qf 0 -> 1.73e12: 0001->0003; $\mu_{band}$ 16.8 -> 18.13: 0003->0008; $\chi$ -0.1 eV: 0012->0020; $\chi$ +0.1 eV: 0012->0021; $N_d$ x2: 0012->0022; $N_t$ x1.5: 0012->0023; $W_{TA}$ +5 meV: 0012->0024; $D_{it}$ x3: 0012->0025; $\varepsilon_{IWO}$ 10.55: 0012->0026; confinement off: 0012->0016; gate WF +0.1 eV: 0038->0048; $m^*$ x1.3: 0038->0050. Grey circles: measured 2 nm. run_0027 (overlap) excluded: malformed.

## param_control_delta
Changes (dVth_cc V, dSS 1e-10..1e-9 mV/dec, dIon %): Qf 0 -> 1.73e12: -0.309, +0.4, +27.1; $\mu_{band}$ 16.8 -> 18.13: -0.009, -3.8, +7.9; $\chi$ -0.1 eV: +0.100, +0.0, -6.9; $\chi$ +0.1 eV: -0.100, +0.0, +7.0; $N_d$ x2: -0.009, +0.7, +0.7; $N_t$ x1.5: +0.082, +49.0, -25.1; $W_{TA}$ +5 meV: +0.020, +4.6, +0.4; $D_{it}$ x3: +0.025, +0.1, -1.8; $\varepsilon_{IWO}$ 10.55: -0.001, -0.4, +0.7; confinement off: -0.316, +15.3, +21.4; gate WF +0.1 eV: +0.100, -0.0, -6.8; $m^*$ x1.3: -0.044, -18.0, +4.1

## param_control_13nm
Pairs: Qf 0 -> 1.73e12: 0002->0004; $\mu_{band}$ 57.6 -> 61.9: 0004->0009; confinement off: 0013->0017; gate WF +0.1 eV: 0040->0049; $m^*$ x1.3: 0040->0051

## hyp_6p3_overlays
Runs 0014, 0015, 0031, 0032, 0030, 0033, 0035, 0034 vs measured 6.3 nm (DOS 96/48).

## hyp_6p3_metrics
Errors vs measured 6.3 nm (Vth_cc 0.644, SS 295.4, gap 1.176, gm 3.431e-07); green = within 0.05 V / 20 mV/dec / 0.1 V / 8 %: 0014 shared (validation): -0.294 V, -10.4, -0.314 V, -16.6 %; 0015 tuned Qf 8.7e10: +0.007 V, -6.5, -0.356 V, -23.1 %; 0031 A1 t = 5.3 nm: -0.258 V, -4.9, -0.297 V, -18.1 %; 0032 A2 $N_d$ removed: -0.264 V, -14.7, -0.329 V, -17.5 %; 0030 A3 back charge: -0.017 V, -64.1, -0.452 V, -18.4 %; 0033 A4 $D_{it}$ x5: -0.243 V, -9.1, -0.319 V, -16.9 %; 0035 A5 combination: -0.079 V, -45.9, -0.405 V, -19.6 %; 0034 A6 no confinement: -0.057 V, -7.7, -0.337 V, -18.4 %; 0037 B0 re-partition: +0.010 V, +115.6, +0.026 V, -5.0 %; 0052 C1 near-Ec band: +0.004 V, +9.1, -0.237 V, -3.5 %; 0039 B2 tuned DOS384: +0.009 V, -5.7, -0.362 V, -23.3 %

## shape_6p3
Measured 6.3 nm vs run_0039 (x11.581987/11.41), run_0037 (B0), run_0052 (C1). gm = numerical gradient on the 0.05 V grid.

## off_floors
Floors (median -2..-0.5 V): {2.0: 4.60552e-15, 6.3: 1.52759e-13, 13.2: 6.59655e-12}; ratio 13.2/2 = 1432; log-log slope 3.78 (S4 quotes 3.85).

## vth_budget
Gauss terms at Vth_cc from S1 report section 1.1 (1-D surrogate matching ATLAS within 3 mV): runs 0012, 0014, 0013.

## symmetric_calibration
Required Qf from S1 key numbers / SYNTHESIS D3. with confinement: best single Qf 1.153e12, residuals [0.117, -0.19, 0.073] V, rms 0.1358 V | without confinement: best single Qf 0.403e12, residuals [-0.063, -0.12, 0.184] V, rms 0.1320 V

## mobility_partition
V1 decomposition (runs 0012/0015/0013) and S2 partition (1-D surrogate) from S2 report key numbers.

## thickness_laws
Laws from config/iwo_material_model.yaml; DFT points tables/THICKNESS_LAW_EVIDENCE.csv; SP shifts scratch/S3/s3_sp1d_notraps_out.txt (Q1 at n_s=1e10).

## sp_confinement
scratch/S3/s3_sp1d_notraps.json (no traps). Shifts vs C0 at 1e10 cm^-2: C1: 0.345, 0.070, 0.026 | Q1: 0.256, 0.036, 0.016 | Q2: 0.384, 0.043, 0.018 | Q3: 0.202, 0.031, 0.015 | Q4: 0.205, 0.016, 0.001 | Q5: 0.139, -0.001, -0.012

## mufe_extraction
np.gradient on the measured 0.05 V grid; 2.0 nm: max linear 12.15, max sat-formula 5.09; 6.3 nm: max linear 10.95, max sat-formula 3.86; 13.2 nm: max linear 50.17, max sat-formula 27.40 (paper: 5.1 and 27.4).

## powerlaw_loo
Models fitted through 2 and 13.2 nm, predicting 6.3 nm (measured 10.95): {'power law': 28.776822157764073, 'A + B/t': 42.733408859785875, 'exponential': 20.94268262747763, 'step': 12.15}; Ion power exponent 2.75 predicts 3.43e-05 A/um at 31.8 nm (measured 3.59e-6).

## idvd_predictions
output_characteristics.csv of runs 0041-0043 (recalibrated DOS 384/192). 2.0 nm run_0041: Id(3,3) 8.687e-07 A/um; 6.3 nm run_0042: Id(3,3) 7.142e-07 A/um; 13.2 nm run_0043: Id(3,3) 6.388e-06 A/um

## temperature_predictions
Runs 0044-0047 as simulated (ATLAS tmu = 1.5, P-phonon) and x(T/300)^1.5 (P-MTR); 300 K refs 0038, 0039 x1.015074, 0040 x1.020113.

## activation_energy
Least-squares Arrhenius over available T (2 nm: 300/338.15/358.15; others 300/358.15); 2.0 P-MTR Ea(1 V) 57.3 meV; 2.0 P-phonon Ea(1 V) 15.1 meV; 6.3 P-MTR Ea(1 V) 53.4 meV; 6.3 P-phonon Ea(1 V) 11.1 meV; 13.2 P-MTR Ea(1 V) 20.8 meV; 13.2 P-phonon Ea(1 V) -21.5 meV

## band_2p0_eq
Copied from plots\2p0\band_diagram_eq.png

## band_2p0_vth
Copied from plots\2p0\band_diagram_vth.png

## band_2p0_on
Copied from plots\2p0\band_diagram_on.png

## band_13p2_on
Copied from plots\13p2\band_diagram_on.png

## edens_2p0_vs_vg
Copied from plots\2p0\electron_density_vs_vg.png

## edens_13p2_vs_vg
Copied from plots\13p2\electron_density_vs_vg.png

## trap_spectroscopy
Copied from analysis_2026-09-25\scratch\S4\s4_trap_spectroscopy.png

## yfunction
Copied from analysis_2026-09-25\scratch\S5\s5_yfunction_hfunction.png
## stack_schematic
Drawn from config/geometry.yaml and docs/DEVICE_STRUCTURE.md; region numbers as in build_iwo_decks.py (full structure).

## param_control_delta
Changes (dVth_cc V, dSS 1e-10..1e-9 mV/dec, dIon %): Qf 0 -> 1.73e12: -0.309, +0.4, +27.1; $\mu_{band}$ 16.8 -> 18.13: -0.009, -3.8, +7.9; $\chi$ -0.1 eV: +0.100, +0.0, -6.9; $\chi$ +0.1 eV: -0.100, +0.0, +7.0; $N_d$ x2: -0.009, +0.7, +0.7; $N_t$ x1.5: +0.082, +49.0, -25.1; $W_{TA}$ +5 meV: +0.020, +4.6, +0.4; $D_{it}$ x3: +0.025, +0.1, -1.8; $\varepsilon_{IWO}$ 10.55: -0.001, -0.4, +0.7; confinement off: -0.316, +15.3, +21.4; gate WF +0.1 eV: +0.100, -0.0, -6.8; $m^*$ x1.3: -0.044, -18.0, +4.1

## thickness_laws
Laws from config/iwo_material_model.yaml; DFT points tables/THICKNESS_LAW_EVIDENCE.csv; SP shifts scratch/S3/s3_sp1d_notraps_out.txt (Q1 at n_s=1e10).
## numerics_convergence
Runs 0012/0019/0029 (DOS), 0013/0028 and 0015/0036 (mesh), offsets from S6 report section 1 (B1-B3), SS_min artefact threshold 2.30e-14 A/um (S6).

## thickness_laws
Laws from config/iwo_material_model.yaml; DFT points tables/THICKNESS_LAW_EVIDENCE.csv; SP shifts scratch/S3/s3_sp1d_notraps_out.txt (Q1 at n_s=1e10).

## idvd_predictions
output_characteristics.csv of runs 0041-0043 (recalibrated DOS 384/192). 2.0 nm run_0041: Id(3,3) 8.687e-07 A/um; 6.3 nm run_0042: Id(3,3) 7.142e-07 A/um; 13.2 nm run_0043: Id(3,3) 6.388e-06 A/um
## calibrated_overlays
Active region = measured > 5x off-band median. 2.0 nm: run_0038 x1.000000: Vth_cc 0.680, Vth_lin 1.537, mu_FE 11.10, Ion 5.09e-07; active rms 0.0429 dec | 6.3 nm: run_0039 x1.015073: Vth_cc 0.653, Vth_lin 1.466, mu_FE 8.39, Ion 4.034e-07; active rms 0.0630 dec | 13.2 nm: run_0040 x1.020112: Vth_cc 0.054, Vth_lin 0.995, mu_FE 48.85, Ion 3.071e-06; active rms 0.0813 dec

## temperature_predictions
Ratios of runs 0044-0047 (as simulated, ATLAS tmu = 1.5: P-phonon) and x(T/300)^1.5 (P-MTR) to the 300 K references 0038, 0039 x1.015074, 0040 x1.020113; 2.0 nm 338.15 K: ratio at 3 V P-phonon 0.841, P-MTR 1.006; at 0.5 V P-MTR 1.71; 2.0 nm 358.15 K: ratio at 3 V P-phonon 0.774, P-MTR 1.010; at 0.5 V P-MTR 2.18; 6.3 nm 358.15 K: ratio at 3 V P-phonon 0.784, P-MTR 1.022; at 0.5 V P-MTR 2.24; 13.2 nm 358.15 K: ratio at 3 V P-phonon 0.778, P-MTR 1.015; at 0.5 V P-MTR 1.48
## measured_metrics
Measured metrics: {"2.0": {"vcc": 0.6618, "vlin": 1.6631, "ss1": 121.2073, "ss2": 269.8986, "mufe": 12.1459, "musat": 5.0867, "ion": 5.08966e-07, "fl": 0.0}, "6.3": {"vcc": 0.644, "vlin": 1.82, "ss1": 124.4921, "ss2": 295.367, "mufe": 10.9467, "musat": 3.8585, "ion": 4.03448e-07, "fl": 0.0}, "13.2": {"vcc": 0.0825, "vlin": 1.0441, "ss1": 136.1494, "ss2": 160.0202, "mufe": 50.1662, "musat": 27.4041, "ion": 3.07069e-06, "fl": 7e-12}}
## shape_6p3
Measured 6.3 nm vs run_0039 (x11.581987/11.41), run_0037 (B0), run_0052 (C1). gm = numerical gradient on the 0.05 V grid.

## off_floors
Floors (median -2..-0.5 V): {2.0: 4.60552e-15, 6.3: 1.52759e-13, 13.2: 6.59655e-12}; ratio 13.2/2 = 1432; log-log slope 3.78 (S4 quotes 3.85).

## symmetric_calibration
Required Qf from S1 key numbers / SYNTHESIS D3. with confinement: best single Qf 1.153e12, residuals [0.117, -0.19, 0.073] V, rms 0.1358 V | without confinement: best single Qf 0.403e12, residuals [-0.063, -0.12, 0.184] V, rms 0.1320 V

## powerlaw_loo
Models fitted through 2 and 13.2 nm, predicting 6.3 nm (measured 10.95): {'power law': 28.776822157764073, 'A + B/t': 42.733408859785875, 'exponential': 20.94268262747763, 'step': 12.15}; Ion power exponent 2.75 predicts 3.43e-05 A/um at 31.8 nm (measured 3.59e-6).
## thickness_laws
Laws from config/iwo_material_model.yaml; DFT points tables/THICKNESS_LAW_EVIDENCE.csv; SP shifts scratch/S3/s3_sp1d_notraps_out.txt (Q1 at n_s=1e10).
## thickness_laws
Laws from config/iwo_material_model.yaml; DFT points tables/THICKNESS_LAW_EVIDENCE.csv; SP shifts scratch/S3/s3_sp1d_notraps_out.txt (Q1 at n_s=1e10).
## thickness_laws
Laws from config/iwo_material_model.yaml; DFT points tables/THICKNESS_LAW_EVIDENCE.csv; SP shifts scratch/S3/s3_sp1d_notraps_out.txt (Q1 at n_s=1e10).
## thickness_laws
Laws from config/iwo_material_model.yaml; DFT points tables/THICKNESS_LAW_EVIDENCE.csv; SP shifts scratch/S3/s3_sp1d_notraps_out.txt (Q1 at n_s=1e10).
## thickness_laws
Laws from config/iwo_material_model.yaml; DFT points tables/THICKNESS_LAW_EVIDENCE.csv; SP shifts scratch/S3/s3_sp1d_notraps_out.txt (Q1 at n_s=1e10).
## thickness_laws
Laws from config/iwo_material_model.yaml; DFT points tables/THICKNESS_LAW_EVIDENCE.csv; SP shifts scratch/S3/s3_sp1d_notraps_out.txt (Q1 at n_s=1e10).
## thickness_laws
Laws from config/iwo_material_model.yaml; DFT points tables/THICKNESS_LAW_EVIDENCE.csv; SP shifts scratch/S3/s3_sp1d_notraps_out.txt (Q1 at n_s=1e10).
