# Prediction register: IWO V1 ATLAS model, ID-VD and elevated-temperature transfer predictions

**Registered (UTC): 2026-09-24T23:24:53Z.** Registrant: specialist S6, analysis_2026-09-25 (no ATLAS launch by S6; every number below is read from the real ATLAS runs listed, or derived from them by the exact operations stated). None of the predicted quantities was used in calibration, and no measurement of them was in the project's possession at registration time. Januar et al. 2026 SI Fig. S12 (2 nm transfer curves at 65 and 85 C) exists but is NOT in the package; it is the first intended test.

## 1. Model state that is being registered
- Model V1 (`config/iwo_material_model.yaml`), physical structure, classical electrons-only drift-diffusion with Fermi statistics, acceptor tail NTA/WTA (WTA 0.040 eV), deep and interface Gaussians, fixed front charge Qf, uniform Nd_eff(t), confinement law dEc = 0.9205 t^-1.3815 eV, Nc(m*(t)), constant spatially uniform band mobility, ideal Ohmic Pd contacts, DOS levels 384/192.
- Calibrated (300 K, Vd 0.7 V, one ID-VG per film): mu_band = 17.6897 (2 nm), 11.582 (6.3 nm), 61.6046 cm^2/Vs (13.2 nm); Qf = 1.73e12 cm^-2 (2 and 13.2 nm, shared) and 8.7e10 cm^-2 (6.3 nm, device-specific "tuned" configuration).
- 300 K references: run_0038 (B1) x 17.6897/17.69 = x0.999983, run_0039 (B2) x 11.582/11.41 = x1.015074, run_0040 (B3) x 61.6046/60.39 = x1.020113 (exact: Id is linear in the uniform constant mobility; verified run_0029/run_0038 ratio 1.024879 vs 1.024873 expected over 43 points; ID-VD at Vd 0.7 V equals the rescaled transfer curves to <0.001 % at all 15 (film, Vg) points).
- Temperature assumptions (campaign B plan): Nc, Nv proportional to T^1.5 (ATLAS); Eg T-independent (egalpha = 0); NTA/WTA, Dit, deep states, Qf, Nd_eff T-independent; tail occupancy at the lattice temperature (thermal equilibrium, isothermal, no self-heating).
- Known calibration residuals the predictions inherit (final converged comparison, S6 report section 1): 2 nm gm_max -8.6 %, Vth_lin -0.127 V; 6.3 nm gm_max -23 %, Vth_lin -0.354 V (on-state shape NOT reproduced; the 6.3 nm predictions are lower-confidence); 13.2 nm gm_max -2.6 %.

## 2. Temperature caveat (tmu) and the two registered variants
ATLAS applied its silicon-default constant-mobility temperature exponent (printed "tmu = 1.5" in `run_0045/deckbuild.out`, REGIONAL MOBILITY MODEL SUMMARY, lines ~384-423: "mu = 12.977 @ 358 K, tmu = 1.5"), i.e. mu_band(T) = mu_band(300 K)(T/300)^-1.5, although the plan declared a T-independent band mobility. Because the mobility is uniform and constant, the current is exactly proportional to that factor, so two variants are exact:
- **P-phonon** = as simulated (band mobility falls as T^-1.5).
- **P-MTR** = simulated currents x (T/300)^+1.5 = x1.19665 (338.15 K) and x1.30426 (358.15 K): T-independent band mobility, multiple-trapping-and-release through the equilibrium tail only.
The as-simulated runs must never be quoted as "T-independent mobility". A measured result between the variants is read through an effective exponent: mu_band proportional to T^-g with g = -ln(R_meas/R_MTR)/ln(T/300), where R is the measured and P-MTR-predicted ratio of the same current quantity (Ion or mu_FE) at T vs 300 K.

## 3. Extraction definitions (apply identically to future measured curves)
`scripts/extract_metrics.py` (unchanged) for Vth_cc (Id = 1e-9 A/um, log-linear), Vth_lin (secant gm on the 0.05 V grid, linear extrapolation at gm_max), mu_FE = gm_max L/(W Cox Vd) (L 20 um, Cox 8.955e-7 F/cm^2, Vd 0.7 V), Ion = Id(3 V). Simulated curves are first interpolated (np.interp) from the native grid (0.05 V for -1..1.5 V, 0.1 V above) onto the 0.05 V measurement grid, as in `scripts/run_atlas.py`. Added fixed-current metrics (S6): V(I) = Vg at Id = I (log-linear), SS(I1..I2) = [V(I2)-V(I1)]/log10(I2/I1) for 1e-11..1e-10, 1e-10..1e-9 and 1e-10..1e-8 A/um. SS_min is NOT registered (window-phase artefact, S6 report 1.4). Ea(Vg) = -k_B dln(Id)/d(1/T) at fixed Vg and Vd 0.7 V (least squares over the available temperatures). **The primary registered quantities are the changes (dVth, dSS, ratios, Ea), to be compared with changes measured on the same device relative to its own 300 K curve**; absolute values carry the 300 K calibration residual.

## 4. ID-VD predictions (300 K; runs B8 run_0041, B9 run_0042, B10 run_0043; Vd 0-0.5 V in 0.05 V steps, 0.5-3 V in 0.1 V steps)

### 4.1 Drain current (A/um)
| film | Vg (V) | Id @0.05 | Id @0.1 | Id @0.5 | Id @1 | Id @2 | Id @3 V | Id @0.7 (= calibrated transfer) | model/measured at Vd 0.7 (calibration residual, context) |
|---|---|---|---|---|---|---|---|---|---|
| 2 nm | 1 | 1.854e-09 | 3.34e-09 | 7.693e-09 | 7.872e-09 | 7.882e-09 | 7.888e-09 | 7.86e-09 | 0.813 |
| 2 nm | 1.5 | 8.969e-09 | 1.699e-08 | 5.292e-08 | 6.075e-08 | 6.106e-08 | 6.111e-08 | 5.841e-08 | 0.972 |
| 2 nm | 2 | 1.988e-08 | 3.86e-08 | 1.482e-07 | 2.014e-07 | 2.101e-07 | 2.103e-07 | 1.786e-07 | 1.052 |
| 2 nm | 2.5 | 3.197e-08 | 6.27e-08 | 2.649e-07 | 4.135e-07 | 4.761e-07 | 4.772e-07 | 3.376e-07 | 1.035 |
| 2 nm | 3 | 4.447e-08 | 8.768e-08 | 3.883e-07 | 6.537e-07 | 8.582e-07 | 8.687e-07 | 5.09e-07 | 1.000 |
| 6.3 nm | 1 | 2.116e-09 | 3.836e-09 | 8.985e-09 | 9.233e-09 | 9.247e-09 | 9.254e-09 | 9.214e-09 | 1.021 |
| 6.3 nm | 1.5 | 8.245e-09 | 1.575e-08 | 5.224e-08 | 6.136e-08 | 6.176e-08 | 6.181e-08 | 5.859e-08 | 1.229 |
| 6.3 nm | 2 | 1.644e-08 | 3.202e-08 | 1.266e-07 | 1.791e-07 | 1.891e-07 | 1.893e-07 | 1.553e-07 | 1.249 |
| 6.3 nm | 2.5 | 2.549e-08 | 5.005e-08 | 2.138e-07 | 3.408e-07 | 4.037e-07 | 4.048e-07 | 2.745e-07 | 1.131 |
| 6.3 nm | 3 | 3.498e-08 | 6.9e-08 | 3.069e-07 | 5.211e-07 | 7.027e-07 | 7.142e-07 | 4.034e-07 | 1.000 |
| 13.2 nm | 1 | 4.651e-08 | 8.863e-08 | 2.852e-07 | 3.245e-07 | 3.259e-07 | 3.263e-07 | 3.142e-07 | 0.948 |
| 13.2 nm | 1.5 | 9.441e-08 | 1.838e-07 | 7.241e-07 | 1.011e-06 | 1.055e-06 | 1.056e-06 | 8.85e-07 | 0.996 |
| 13.2 nm | 2 | 1.463e-07 | 2.872e-07 | 1.228e-06 | 1.954e-06 | 2.289e-06 | 2.294e-06 | 1.576e-06 | 1.006 |
| 13.2 nm | 2.5 | 2e-07 | 3.946e-07 | 1.758e-06 | 2.988e-06 | 4.015e-06 | 4.068e-06 | 2.312e-06 | 1.004 |
| 13.2 nm | 3 | 2.55e-07 | 5.044e-07 | 2.302e-06 | 4.063e-06 | 6.035e-06 | 6.388e-06 | 3.071e-06 | 1.000 |

### 4.2 Output-curve shape (the genuine prediction content: normalised to the calibrated Vd = 0.7 V point)
| film | Vg | Vg - Vth_lin(300 K model) (V) | Id(0.1)/Id(0.05) | d2Id/dVd2 at Vd->0 (A/um/V^2) | gd0 (S/um, quadratic fit 0-0.1 V) | Vd_sat: gd = 10 % of gd0 (V) | gd at Vd 3 V (S/um) | gd(3 V)/gd0 | Id(3)/Id(0.7) | Id(0.1)/Id(0.7) |
|---|---|---|---|---|---|---|---|---|---|---|
| 2 nm | 1 | -0.54 | 1.8011 | -1.48e-07 | 4.077e-08 | 0.43 | 4.7e-12 | 0.01 % | 1.0036 | 0.4249 |
| 2 nm | 1.5 | -0.04 | 1.8941 | -3.8e-07 | 1.889e-07 | 0.68 | 4e-11 | 0.02 % | 1.0463 | 0.2909 |
| 2 nm | 2 | +0.46 | 1.9414 | -4.66e-07 | 4.093e-07 | 1.01 | 1.6e-10 | 0.04 % | 1.1773 | 0.2161 |
| 2 nm | 2.5 | +0.96 | 1.9614 | -4.93e-07 | 6.516e-07 | 1.40 | 4.9e-10 | 0.08 % | 1.4136 | 0.1857 |
| 2 nm | 3 | +1.46 | 1.9716 | -5.04e-07 | 9.02e-07 | 1.80 | 1.49e-09 | 0.17 % | 1.7067 | 0.1723 |
| 6.3 nm | 1 | -0.47 | 1.8126 | -1.59e-07 | 4.63e-08 | 0.44 | 6e-12 | 0.01 % | 1.0044 | 0.4163 |
| 6.3 nm | 1.5 | +0.03 | 1.9103 | -2.96e-07 | 1.723e-07 | 0.73 | 4.4e-11 | 0.03 % | 1.0550 | 0.2688 |
| 6.3 nm | 2 | +0.53 | 1.9472 | -3.47e-07 | 3.375e-07 | 1.09 | 1.6e-10 | 0.05 % | 1.2188 | 0.2061 |
| 6.3 nm | 2.5 | +1.03 | 1.9636 | -3.71e-07 | 5.191e-07 | 1.49 | 4.6e-10 | 0.09 % | 1.4746 | 0.1823 |
| 6.3 nm | 3 | +1.53 | 1.9725 | -3.85e-07 | 7.093e-07 | 1.90 | 1.38e-09 | 0.19 % | 1.7702 | 0.1710 |
| 13.2 nm | 1 | +0.01 | 1.9057 | -1.76e-06 | 9.741e-07 | 0.68 | 2.6e-10 | 0.03 % | 1.0384 | 0.2821 |
| 13.2 nm | 1.5 | +0.51 | 1.9468 | -2.01e-06 | 1.938e-06 | 1.05 | 1e-09 | 0.05 % | 1.1934 | 0.2077 |
| 13.2 nm | 2 | +1.01 | 1.9639 | -2.11e-06 | 2.978e-06 | 1.45 | 2.8e-09 | 0.09 % | 1.4558 | 0.1822 |
| 13.2 nm | 2.5 | +1.51 | 1.9728 | -2.17e-06 | 4.055e-06 | 1.87 | 8.1e-09 | 0.20 % | 1.7596 | 0.1707 |
| 13.2 nm | 3 | +2.01 | 1.9783 | -2.21e-06 | 5.155e-06 | 2.30 | 3.5e-08 | 0.68 % | 2.0803 | 0.1643 |

Gradual-channel reference: Id(0.1)/Id(0.05) = 2 x [1 - 0.05/Vov]/[1 - 0.025/Vov] < 2 for an Ohmic contact (Vov = effective overdrive); every registered value is 1.80-1.98 with negative low-Vd curvature (no S-shape). Output conductance at 3 V is 0.01-0.68 % of gd0 (L = 20 um, no channel-length modulation, no parallel path in the model).

### 4.3 Film ratios Id(t)/Id(2 nm) at equal Vg and Vd
| ratio | Vg | Vd 0.05 | 0.1 | 0.5 | 1 | 2 | 3 V |
|---|---|---|---|---|---|---|---|
| 6.3/2 nm | 1 | 1.141 | 1.149 | 1.168 | 1.173 | 1.173 | 1.173 |
| 6.3/2 nm | 1.5 | 0.919 | 0.927 | 0.987 | 1.010 | 1.011 | 1.011 |
| 6.3/2 nm | 2 | 0.827 | 0.829 | 0.854 | 0.889 | 0.900 | 0.900 |
| 6.3/2 nm | 2.5 | 0.797 | 0.798 | 0.807 | 0.824 | 0.848 | 0.848 |
| 6.3/2 nm | 3 | 0.787 | 0.787 | 0.790 | 0.797 | 0.819 | 0.822 |
| 13.2/2 nm | 1 | 25.082 | 26.538 | 37.075 | 41.223 | 41.353 | 41.365 |
| 13.2/2 nm | 1.5 | 10.526 | 10.819 | 13.685 | 16.648 | 17.272 | 17.281 |
| 13.2/2 nm | 2 | 7.357 | 7.442 | 8.285 | 9.701 | 10.894 | 10.909 |
| 13.2/2 nm | 2.5 | 6.258 | 6.294 | 6.636 | 7.225 | 8.432 | 8.524 |
| 13.2/2 nm | 3 | 5.734 | 5.753 | 5.929 | 6.215 | 7.033 | 7.354 |

## 5. Elevated-temperature transfer predictions (Vd 0.7 V; B11 run_0044 338.15 K 2 nm; B12 run_0045, B13 run_0046, B14 run_0047 at 358.15 K)

### 5.1 300 K references (rescaled B1/B2/B3)
| film | Vth_cc (V) | V(1e-11) (V) | V(1e-7) (V) | SS 1e-11..1e-10 | SS 1e-10..1e-9 | SS 1e-10..1e-8 (mV/dec) | Vth_lin (V) | mu_FE (cm^2/Vs) | Ion (A/um) |
|---|---|---|---|---|---|---|---|---|---|
| 2 nm | 0.6804 | 0.3419 | 1.7043 | 123.5 | 215.0 | 290.9 | 1.5365 | 11.096 | 5.09e-07 |
| 6.3 nm | 0.6529 | 0.3128 | 1.7376 | 124.5 | 215.6 | 289.7 | 1.4664 | 8.393 | 4.034e-07 |
| 13.2 nm | 0.0536 | -0.1807 | 0.6832 | 90.9 | 143.4 | 193.0 | 0.9946 | 48.851 | 3.071e-06 |

### 5.2 Changes relative to 300 K
| film | T (K) | variant | Vth_cc (V) | dVth_cc (mV) | dV(1e-11) (mV) | dV(1e-7) (mV) | SS 1e-11..1e-10 (d) | SS 1e-10..1e-9 (d) | SS 1e-10..1e-8 (d) | dVth_lin (mV) | mu_FE (ratio) | Ion (A/um) | dIon (%) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 nm | 338.15 | P-phonon | 0.6526 | -27.9 | -28.9 | +56.4 | 123.5 (+0.0) | 216.0 (+1.0) | 300.2 (+9.3) | -17.2 | 9.223 (x0.8312) | 4.28e-07 | -15.91 |
| 2 nm | 338.15 | P-MTR | 0.6311 | -49.3 | -36.9 | -27.1 | 119.7 (-3.8) | 206.3 (-8.6) | 287.1 (-3.8) | -17.2 | 11.037 (x0.9947) | 5.122e-07 | +0.63 |
| 2 nm | 358.15 | P-phonon | 0.6399 | -40.5 | -44.0 | +85.4 | 125.0 (+1.5) | 216.9 (+2.0) | 304.5 (+13.6) | -26.5 | 8.437 (x0.7604) | 3.94e-07 | -22.58 |
| 2 nm | 358.15 | P-MTR | 0.6074 | -73.1 | -54.6 | -41.6 | 117.3 (-6.3) | 202.8 (-12.1) | 285.3 (-5.6) | -26.5 | 11.006 (x0.9919) | 5.14e-07 | +0.99 |
| 6.3 nm | 358.15 | P-phonon | 0.6062 | -46.7 | -48.3 | +107.8 | 123.7 (-0.7) | 217.9 (+2.4) | 307.3 (+17.6) | -34.5 | 6.433 (x0.7664) | 3.162e-07 | -21.63 |
| 6.3 nm | 358.15 | P-MTR | 0.5739 | -78.9 | -60.2 | -45.4 | 118.2 (-6.3) | 203.1 (-12.5) | 286.9 (-2.8) | -34.5 | 8.391 (x0.9997) | 4.124e-07 | +2.22 |
| 13.2 nm | 358.15 | P-phonon | -0.0030 | -56.6 | -55.4 | +0.9 | 93.0 (+2.1) | 140.1 (-3.3) | 195.2 (+2.2) | -30.1 | 37.459 (x0.7668) | 2.39e-06 | -22.17 |
| 13.2 nm | 358.15 | P-MTR | -0.0226 | -76.3 | -65.2 | -64.2 | 90.4 (-0.5) | 132.9 (-10.6) | 183.1 (-9.9) | -30.1 | 48.862 (x1.0002) | 3.117e-06 | +1.52 |

Thickness ratio mu_FE(13.2)/mu_FE(2): 4.403 (300 K) -> 4.440 (358.15 K) in both variants (+0.8 %); Ion(13.2)/Ion(2): 6.033 -> 6.065. The tmu factor is common to all films, so the ratios are variant-independent.

### 5.3 Apparent activation energy of Id at fixed Vg (meV; Vd 0.7 V; 2 nm fit over 300/338.15/358.15 K with the two pair values in brackets, 6.3 and 13.2 nm over 300/358.15 K)
| film | variant | Vg 0 | 0.5 | 1.0 | 1.5 | 2.0 | 3.0 V |
|---|---|---|---|---|---|---|---|
| 2 nm | P-phonon | n/a (Id < 1e-16) | +81.6 (+81.4, +82.1) | +15.2 (+15.2, +14.9) | -19.5 (-19.1, -20.5) | -34.3 (-33.6, -36.2) | -40.6 (-39.7, -43.2) |
| 2 nm | P-MTR | n/a (Id < 1e-16) | +123.7 (+122.5, +127.1) | +57.3 (+56.4, +59.9) | +22.6 (+22.0, +24.5) | +7.8 (+7.5, +8.8) | +1.5 (+1.4, +1.8) |
| 6.3 nm | P-phonon | +452.0 * | +86.0 | +11.1 | -22.3 | -33.5 | -38.8 |
| 6.3 nm | P-MTR | +494.3 * | +128.3 | +53.4 | +20.0 | +8.8 | +3.5 |
| 13.2 nm | P-phonon | +120.8 | +20.4 | -21.5 | -34.0 | -37.7 | -39.9 |
| 13.2 nm | P-MTR | +163.1 | +62.7 | +20.8 | +8.3 | +4.7 | +2.4 |

\* below 5x the measured 300 K off-floor of that film: not measurable on the existing devices. The P-MTR minus P-phonon difference is the tmu term, +1.5 k_B T_eff = +42.3 meV for 300-358.15 K, at every Vg.

### 5.4 Cross-check against the pre-registered analytic MTR expectation (S2 section 4, 1-D surrogate, 300 -> 350 K, T-independent mu)
| film | quantity at 350 K | S2 surrogate (registered 2026-09-24T18:57Z) | ATLAS P-MTR (interpolated linearly in T) | difference |
|---|---|---|---|---|
| 2 nm | dVth_cc (mV) | -64 | -63.4 | +0.6 |
| 2 nm | mu_FE ratio | 0.993 | 0.9930 | +0.0000 |
| 2 nm | Ion ratio | 1.004 | 1.0084 | +0.0044 |
| 2 nm | dVth_lin (mV) | -15 | -22.7 | -7.7 |
| 13.2 nm | dVth_cc (mV) | -66 | -65.6 | +0.4 |
| 13.2 nm | mu_FE ratio | 0.999 | 1.0002 | +0.0012 |
| 13.2 nm | Ion ratio | 1.011 | 1.0131 | +0.0021 |
| 13.2 nm | dVth_lin (mV) | -24 | -25.9 | -1.9 |
Ea (P-MTR, 300-358 K fit) vs S2 (300-350 K): 2 nm 124/57/23/8/2 vs 120/56/23/7/1 meV at Vg 0.5/1/1.5/2/3 V; 13.2 nm 163/63/21/8/5/2 vs 156/61/20/8/4/2 meV at Vg 0/0.5/1/1.5/2/3 V. This is a model-vs-surrogate consistency test (numerical), not an experimental validation.

## 6. What each outcome would falsify
| registered prediction | model value(s) | measured outcome that falsifies | assumption falsified |
|---|---|---|---|
| Low-Vd linearity, all films and Vg | Id(0.1)/Id(0.05) = 1.80-1.98; d2Id/dVd2 < 0 at Vd -> 0 | ratio > 2.0 or upward (S-shaped) curvature below ~0.2 V, in particular at 2 nm only | ideal Ohmic Pd/IWO injection (S5 M2: confinement-raised barrier); also the mu_band = intrinsic lumping |
| Normalised output Id(0.1)/Id(0.7) at Vg 3 V | 0.172 / 0.171 / 0.164 (2 / 6.3 / 13.2 nm) | measured value lower by more than the repeatability, growing with Id | negligible Rsd (series resistance compresses the low-Vd end); thickness ordering of the deficit identifies which film carries Rc |
| Saturation | Vd_sat(10 %) 0.43-1.80 V (2 nm), 0.44-1.90 (6.3), 0.68-2.30 (13.2) for Vg 1-3 V | quasi-saturation well below these (> ~0.3 V lower) | constant mobility and zero Rsd (field-dependent mobility or Rsd) |
| Output conductance at Vd 3 V | 0.01-0.19 % of gd0 (2, 6.3 nm), 0.03-0.68 % (13.2 nm) | several % of gd0, or rising with t | no parallel/ungated path, long-channel electrostatics (S4 floor path; back-channel conduction) |
| Film ratios at low Vd | Id(13.2)/Id(2) at Vd 0.1 V = 26.5 / 10.8 / 7.44 / 6.29 / 5.75 (Vg 1-3 V) | low-Vd ratio differing from the Vd 0.7 V ratio beyond the predicted Vd dependence | thickness-independent (zero) contact resistance |
| On-current vs T (2 nm, 358 K) | P-MTR +0.99 %, P-phonon -22.6 % (mu_FE x0.992 / x0.760) | dIon > ~+5 % (g < -0.2) | T-independent or phonon-like band mobility: activated band mobility / percolation (S2 4b predicts mu x1.03-1.39) |
| On-current vs T | as above | dIon near -22 % (g ~ +1.5) | T-independent band mobility (band-like phonon-limited transport instead) |
| Thickness ratio mu_FE(13.2)/mu_FE(2) | 4.40 -> 4.44 at 358 K (both variants) | shrinks toward ~3.3 (or 2.7-3.3) | common band-transport mechanism in all films (S2: barrier-limited thin films, phonon-limited 13.2 nm) |
| dVth_cc at 358 K | P-MTR -73 / -79 / -76 mV; P-phonon -41 / -47 / -57 mV (2 / 6.3 / 13.2 nm); dVth_lin -27 / -35 / -30 mV in both | at 358 K, outside the -35 ... -85 mV envelope of the two variants beyond the (NOT DETERMINED, to be measured) repeatability, or a thickness spread >> 20 mV | equilibrium tail filling as the only T-dependent charge (e.g. thermally ionized V_O donors, T-dependent Qf, hysteresis) |
| dVth_cc at 338 K (2 nm) | P-MTR -49 mV; P-phonon -28 mV | as above | as above |
| Subthreshold Ea at fixed Vg | P-MTR 124 / 128 / 63 meV at 0.5 V; 57 / 53 / 21 meV at 1 V (2 / 6.3 / 13.2 nm) | ordering Ea(2) ~ Ea(6.3) > Ea(13.2) violated beyond ~10 meV | tail/EF alignment (Vth) ordering of the model; a different EF-Ec at the 6.3 nm film |
| On-state Ea (Vg 3 V) | P-MTR +1.5 / +3.5 / +2.4 meV; P-phonon -40.6 / -38.8 / -39.9 meV | thin-film Ea(3 V) exceeding the 13.2 nm value by > ~10 meV | thickness-independent transport mechanism (structural/percolation step, S2) |
| SS at fixed current, 358 K | P-MTR: SS 1e-10..1e-9 -12.1 / -12.5 / -10.6 mV/dec; P-phonon +2.0 / +2.4 / -3.3 | increase > ~20 mV/dec | T-independent tail (WTA) and Dit; thermal-equilibrium trapping |

## 7. Numerical uncertainty of the registered numbers
- Id, Ion, mu_FE ratios: DOS residual beyond 384/192 +0.16 % at 2 nm (Richardson, observed order 2.0 from runs 0012/0019/0029), smaller for 6.3/13.2 nm (offsets scale ~Nt); mesh x0.7 <= 0.013 % (runs 0036, 0028); linear rescale exact to 1e-5. DOS convergence was verified at 300 K only (not at 338/358 K).
- Vth_cc, V(I): +/-1 mV (DOS residual < 0.5 mV, mesh 0.3-0.4 mV, log-linear vs PCHIP interpolation <= 1.5 mV). Fixed-current SS: +/-1 mV/dec. Vth_lin: grid-limited, -5 to -12 mV bias of the simulation grid relative to a 0.05 V measurement (0.1 V solver steps above 1.5 V); gm_max: -0.4 to -0.7 %.
- Ea: < 0.5 meV (numerical); ID-VD: Vd_sat +/-0.05 V (0.1 V grid); gd(3 V) at Vg 1 V is set by current differences of ~5e-13 A/um per 0.1 V and carries up to ~5 % numerical uncertainty (KCL residual up to 1e-14 A in runs 0041/0042).
- Physical/model-form uncertainty is NOT included in these numbers (S6 report sections 3-4).

## 8. Run IDs
300 K references: run_0038 (B1, 2 nm), run_0039 (B2, 6.3 nm tuned), run_0040 (B3, 13.2 nm). ID-VD: run_0041 (B8), run_0042 (B9), run_0043 (B10). Elevated T: run_0044 (B11, 2 nm, 338.15 K), run_0045 (B12, 2 nm, 358.15 K), run_0046 (B13, 6.3 nm, 358.15 K), run_0047 (B14, 13.2 nm, 358.15 K). Linearity check: run_0029 vs run_0038. All launches are logged in `results/RUN_INDEX.csv` (finish rows 2026-09-24T19:28:46Z to 21:54:12Z).

## 9. Canonical machine-readable file
`analysis_2026-09-25/predictions_canonical.csv` (1917 rows; columns film, T_K, variant, Vg, Vd, quantity, value, unit, run_id). Variants: as_simulated_300K (ID-VD), reference_300K, P-phonon, P-MTR. It holds every ID-VD point (Vd > 0), the normalised output curves, the derived output metrics, the full predicted transfer curves (Vg >= -1 V, Id > 1e-16 A/um) for every film, temperature and variant, the metric changes and the Ea values.

## 10. Source files and SHA-256 (computed with Python hashlib at registration)
| file (relative to the package root) | SHA-256 |
|---|---|
| `data/experimental_clean.csv` | `e27a53e8c72169d5e19cdf666c9203f82185f3f23613d5210b47d92ad999b73c` |
| `scripts/extract_metrics.py` | `a7d0b236ecfa4f67433fc842a2b9cebeb295e4a5946f38ea72643139678edf63` |
| `config/iwo_material_model.yaml` | `ab063e8d20b7e57bff498096294183b179d6b667790c535c7bf6dffeba5f3025` |
| `config/campaign_B_recal_predictions.json` | `3247b99c427801d417c3e3388e80289d9bdec894d478b5180c02477a0a548df7` |
| `results/campaigns/campaign_B_recal_predictions.json` | `8b9be148cd9b6fb5dd327d35a5c36a6b2041fc815d5535d5c9512e2cfd18691c` |
| `results/runs/run_0038_2p0_recal_dos384_2p0/idvg.dat` | `cefecae05b2e76ee97c36763f099230cce8a278dcf64d3831e8ca1c268bf9875` |
| `results/runs/run_0038_2p0_recal_dos384_2p0/execution.json` | `d6e68576e7471d3e8451a6b0c9eb9bb9b66a993e8840b1ba77cb856d934b3182` |
| `results/runs/run_0038_2p0_recal_dos384_2p0/device.in` | `165bbbb59bd379b6c310f5a3469b4b8f0949dcdcc009cc2825edb827723d0721` |
| `results/runs/run_0039_6p3_recal_dos384_6p3_tuned/idvg.dat` | `bb7d26ec07baf7068ef3a9d92d7eb08c8cc8eef3c08375944c0cf8bcee2299b8` |
| `results/runs/run_0039_6p3_recal_dos384_6p3_tuned/execution.json` | `a03695bc38c7a0443821838c9bca1d6b8e2bbc9621b9775658e19e257bd5d9b0` |
| `results/runs/run_0039_6p3_recal_dos384_6p3_tuned/device.in` | `184189690ce24b31a1a0270d14e0f3ad36e35bc7c55b811debaac61e58242722` |
| `results/runs/run_0040_13p2_recal_dos384_13p2/idvg.dat` | `3c0f81cf430abf0bb923b0b665272786288778b84d0bc68e404c7b73bf9414e1` |
| `results/runs/run_0040_13p2_recal_dos384_13p2/execution.json` | `cdd53139cc9351b16b98b8bcf597599c2362683a9868b489636a8322833cbc57` |
| `results/runs/run_0040_13p2_recal_dos384_13p2/device.in` | `11020ebbbea8aee1a494e753c28e473bc689738e4b6d58c07aad68370ea96bf0` |
| `results/runs/run_0041_2p0_pred_idvd_2p0/output_characteristics.csv` | `444471f22a6d530f23ea1f5138f1b97906a441803a64919826d02b56862c8d1e` |
| `results/runs/run_0041_2p0_pred_idvd_2p0/execution.json` | `8dd4220c82167f041af8f03fc04d7fc3110fdec1d6f0383e340f7f44af75645e` |
| `results/runs/run_0041_2p0_pred_idvd_2p0/device.in` | `80b4962a3e46230bd736e8b4b3d1fa6769292819f9b4a5468a00bcf84b6e5e7a` |
| `results/runs/run_0042_6p3_pred_idvd_6p3_tuned/output_characteristics.csv` | `74b6709ad63aff2995fbc7a5d35bbca1e9c36c8e78a1cbb943975f6424c64878` |
| `results/runs/run_0042_6p3_pred_idvd_6p3_tuned/execution.json` | `585f19f36ed6ac60d5e3151d973f9ca226f22c0943fbfe81f25fa6bdcffa163e` |
| `results/runs/run_0042_6p3_pred_idvd_6p3_tuned/device.in` | `1132e600cd9374ee037f81281e48dc3ed12d2b999ed5321a36a09b63497fe078` |
| `results/runs/run_0043_13p2_pred_idvd_13p2/output_characteristics.csv` | `cca708643e7f0106217e735c4fccd45c9a9447eb822e3a3c36675d24abb9c1f9` |
| `results/runs/run_0043_13p2_pred_idvd_13p2/execution.json` | `6159ada850361d8e1b84d9cd3bf214fdc5e266842d10cd837499f3aa6b085bda` |
| `results/runs/run_0043_13p2_pred_idvd_13p2/device.in` | `b0eac4011200c8bf282a879b40a3ced8138b137097971352a7c09a48ce3757a6` |
| `results/runs/run_0044_2p0_pred_T338K_2p0/idvg.dat` | `0b4cef05172bfd34337b50fcc2f7402140c75597833d54867bf545e94712a906` |
| `results/runs/run_0044_2p0_pred_T338K_2p0/execution.json` | `7124ae3006202185ce312c8d0a3c5364184a5d793875660490f583f0005b10ec` |
| `results/runs/run_0044_2p0_pred_T338K_2p0/device.in` | `26b7083e160859384e5127f3e5becd6326aaa4d3c3abfdaa91bea7ef3205a489` |
| `results/runs/run_0044_2p0_pred_T338K_2p0/deckbuild.out` | `a5f900792998d2b19f94a4ff55b863bf11e21ce787dcb4b9c1aa622179119c8f` |
| `results/runs/run_0045_2p0_pred_T358K_2p0/idvg.dat` | `47fffa91c6dac0b8a0237c015b226a3ad590ebcd45e3d210e5c558c365ea714a` |
| `results/runs/run_0045_2p0_pred_T358K_2p0/execution.json` | `484be4c2b88daea4e08e910142a12b8720b166b17ec798c4ad11d36ec936fb32` |
| `results/runs/run_0045_2p0_pred_T358K_2p0/device.in` | `5f6e39b9c4f1ea9a424b7abcac65b133ed2fda47d46f7b57e18f47d5f47d490e` |
| `results/runs/run_0045_2p0_pred_T358K_2p0/deckbuild.out` | `1706847d78970fe11e9ddd7855dbc7cdb094094f294dec1cbf59fcf44f3b0566` |
| `results/runs/run_0046_6p3_pred_T358K_6p3/idvg.dat` | `ecfe1f99b0e0156c9d7c026d929e5309859476e3596f75d2e9622b9f94c71f75` |
| `results/runs/run_0046_6p3_pred_T358K_6p3/execution.json` | `ac6566a376ea032689654967609565df71304c774c8720eedd43fe4255fc7990` |
| `results/runs/run_0046_6p3_pred_T358K_6p3/device.in` | `2eb29a95c9319b70d82835d274d8f4ceff50b4764547611987eeaac647e1ab0b` |
| `results/runs/run_0046_6p3_pred_T358K_6p3/deckbuild.out` | `72bd89d391696d3f1839d01ac4bd443d6f2cf63410ddaf6f4e15a3a639e4fdc8` |
| `results/runs/run_0047_13p2_pred_T358K_13p2/idvg.dat` | `102890b1657e435fd534bea02475fed096211b1f2f413d5667812694e9fa25db` |
| `results/runs/run_0047_13p2_pred_T358K_13p2/execution.json` | `4cddbb3db0f5169e9967f5334d54b7390ad675e40f7a0e2aba8f538eac69c351` |
| `results/runs/run_0047_13p2_pred_T358K_13p2/device.in` | `df4fedf5850342c77541df502667d29a18bf9f382376c668fe7e0476b31c65fe` |
| `results/runs/run_0047_13p2_pred_T358K_13p2/deckbuild.out` | `f1f5c586bd3f9d48224500c4fafbe58f0c76828370d4abca66e7b3b929b5abb2` |
| `analysis_2026-09-25/scratch/S6/s6_lib.py` | `19af8ef0d57ee2e8d7680e5d50351c61540cce9867055337aa810981e53dd694` |
| `analysis_2026-09-25/scratch/S6/s6_part3_predictions.py` | `c8b13ef7258ff85801ac7de3e56bcf5966093a1ae91c3d6e48e3e47af50f112b` |
| `analysis_2026-09-25/scratch/S6/s6_write_register.py` | `b35fb2a261c423deac9873c1ce85fb6b8fb92b7e958f822c4b4113c4cfe97abe` |
| `analysis_2026-09-25/scratch/S6/s6_part3_out.txt` | `0ecbc5ca2425424f239f4c254c32b96ede6a962d3cf894afb1d35fdeef30b84c` |
| `analysis_2026-09-25/predictions_canonical.csv` | `5c9950be9a3909210364a8d0592725d697578b73d218f995d0725224b3f0dc1c` |

Any later change to these files, to the extraction definitions or to the model state invalidates the prospective status of this register; a revised register must be a new, separately timestamped file.
