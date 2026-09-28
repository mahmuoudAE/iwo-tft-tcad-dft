# S1: device, back-channel and dimensional electrostatics, and the 6.3 nm discrepancy

Specialist S1, 2026-09-25. No ATLAS launches. Sources used:
- ATLAS outputs: `results/runs/run_00xx/execution.json`, `comparison.csv` and the depth profiles `cb_/qfn_/n_{vth,on}.dat`.
- Campaign A metrics: `results/campaigns/campaign_A_6p3_hypotheses.json`.
- Scratch outputs in `analysis_2026-09-25/scratch/S1/`: `s1_atlas_tables.out.txt`, `s1_poisson1d.out.txt`, `s1_shape_test.out.txt` and `s1_analytic.out.txt`, with the scripts of the same names.

## 0. Tools, and why the decomposition can be trusted

**The 1-D surrogate.** `s1_poisson1d.py` is a 1-D Poisson plus gradual-channel (Pao-Sah) surrogate of the V1 physics. It uses:
- the same DOS (Fermi-Dirac electrons, NTA/WTA tail, deep and interface Gaussians), Nd, Qf, optional back sheet and zero field in air;
- parameters read from each run's `metadata.json`, with no tuning.

It reproduces all 12 ATLAS runs it was checked on (0012–0017, 0030–0035) within these tolerances:

| metric | agreement with ATLAS |
|---|---|
| Vth_cc | ≤ 3 mV |
| Vth_lin | ≤ 25 mV |
| SS_cc | ≤ 10 mV/dec |
| gm_max and Ion | ≤ 2.5 % |

Examples:

| run | Vth_cc 1-D / ATLAS (V) | SS_cc 1-D / ATLAS (mV/dec) |
|---|---|---|
| run_0015 | 0.652 / 0.651 | 293.7 / 288.8 |
| run_0030 | 0.629 / 0.627 | 235.4 / 231.3 |
| run_0013 | 0.052 / 0.053 | — |

Two consequences follow:
1. The V1 ATLAS results are essentially 1-D electrostatics. The 2-D top-contact access adds nothing measurable to these metrics.
2. The surrogate can compute the exact Gauss decomposition at threshold, which ATLAS does not export.

**The Gauss identity.** It is evaluated at the source end, at Vg = Vth_cc:

Vth = (WF − χ_bulk) + dEc + (E_Fn − E_c)_front + q(n_t + n_it + n_GA + n_s − Nd·t − Qf − Qb_eff)/Cox

Its closure is exact to 1e-6 V.

**Evidence class.** Surrogate numbers are *model predictions* checked against ATLAS. They are not measurements.

## 1. Threshold-voltage charge budget (task 1)

### 1.1 Gauss terms at threshold

Values in V, from `s1_poisson1d.out.txt` (B1). The model Vth_cc agrees with ATLAS in every column.

| term | 2.0 nm (run_0012) | 6.3 nm validation (0014) | 6.3 nm tuned (0015) | 13.2 nm (0013) | status |
|---|---|---|---|---|---|
| WF − χ_bulk | +0.400 | +0.400 | +0.400 | +0.400 | assumed, degenerate with Qf |
| confinement dEc | +0.353 | +0.072 | +0.072 | +0.026 | DFT proxy, extrapolated |
| (E_Fn − E_c) front (sets n_s; includes kT·ln Nc, dilution over t, CC definition) | −0.038 | −0.039 | −0.037 | −0.111 | model |
| front Qf | −0.310 | −0.310 | −0.016 | −0.310 | fitted |
| q·Nd·t/Cox | −0.009 | −0.028 | −0.028 | −0.070 | fitted law |
| tail charge filled (n_t, cm⁻²) | +0.256 (1.43e12) | +0.226 (1.27e12) | +0.231 (1.29e12) | +0.098 (5.5e11) | fitted Nt, WTA |
| interface traps | +0.012 | +0.012 | +0.012 | +0.012 | assumed Dit |
| free electrons (n_s at source) | +0.014 (7.6e10) | +0.016 (9.1e10) | +0.017 | +0.005 (2.6e10) | model |
| deep Gaussian | 0.000 | +0.001 | +0.001 | +0.003 | assumed |
| **Vth_cc (1-D / ATLAS / measured)** | 0.679 / 0.676 / 0.662 | 0.351 / 0.350 / 0.644 | 0.652 / 0.651 / 0.644 | 0.052 / 0.053 / 0.083 | |

### 1.2 One-at-a-time removals

Values in V (1-D, B2).

| term removed | 2.0 nm | 6.3 nm tuned | 13.2 nm |
|---|---|---|---|
| confinement (dEc and m*) | 0.315 | 0.064 | 0.023 |
| tail | 0.221 | 0.215 | 0.112 |
| m* through Nc only | −0.039 | −0.008 | −0.002 |
| Nd | −0.009 | −0.031 | −0.094 |
| Dit | 0.012 | 0.012 | 0.011 |

These match the terms ATLAS isolates:

| term | ATLAS runs | ATLAS value |
|---|---|---|
| confinement | 0012 − 0016 | 0.315 V |
| confinement | 0013 − 0017 | 0.023 V |
| confinement | 0034 − 0014 minus the exact Qf shift | 0.237 − 0.301 = −0.064, i.e. +0.064 V at 6.3 nm |
| Nd | A2 (removing donors) | +0.030 V |
| Nd | run_0022 (Nd × 2) | −0.009 V |
| Dit | run_0025 (× 3) | +0.025 V, i.e. about 0.012 per 1× |
| Dit | A4 (× 5) | +0.051 V, i.e. about 0.013 per 1× |

**Constant-current (CC) definition effect.** This is measured directly on the experimental curves (`s1_atlas_tables.out.txt`): Vg at 1e-9 × (mu_t/mu_2) minus Vg at 1e-9.

| film | mobility basis | Vth_cc shift if the film had the 2 nm mobility |
|---|---|---|
| 13.2 nm | mu_FE (ratio 4.13) | +0.108 V |
| 13.2 nm | mu0 (ratio 4.45) | +0.115 V |
| 6.3 nm | — | −0.012 to −0.026 V |

In the 1-D model the same effect is +0.144 V at 13.2 nm and +0.026 V at 6.3 nm. The naive estimate SS_cc × log10(ratio) gives 0.10 V at SS 160.

About 0.11–0.14 V of the measured 2→13.2 nm Vth_cc step (−0.579 V) is therefore a consequence of the Vth definition, not a charge.

### 1.3 Decomposing the thickness differences (V1 model)

| step | model ΔVth_cc | confinement | tail | E_Fn − E_c (CC + dilution) | Nd | measured |
|---|---|---|---|---|---|---|
| 2 → 13.2 nm | −0.627 V | −0.327 (52 %) | −0.158 (25 %) | −0.073 (12 %) | −0.061 (10 %) | −0.579 V |
| 2 → 6.3 nm | −0.328 V | −0.281 (86 %) | −0.030 | −0.001 | −0.019 | −0.018 V |

- **2 → 13.2 nm.** The remaining terms are free electrons −0.009 V and deep Gaussian +0.003 V.
- **2 → 6.3 nm.** The V1 6.3 nm miss is essentially the confinement difference. The analytic kT·ln Nc term alone is only 8 mV (2 nm).

**Which terms are fitted.** Of the analytic terms, only q·Nd·t/Cox (0.009 / 0.028 / 0.070 V) and dEc (0.353 / 0.072 / 0.026 eV) are fixed by laws. The tail term is set by the fitted Nt law and is the largest non-confinement term.

## 2. Dimensional electrostatics (task 2)

Numbers are from `s1_analytic.out.txt` and 1-D B3/B5.

### 2.1 Screening lengths and depletion

- **Debye length.** L_D = 7.3 / 6.7 / 3.7 / 2.1 nm at n = 2.5e17 / 3e17 / 1e18 / 3e18 cm⁻³.
- **Trap-screening length.** L_t = √(ε·WTA/q·n_t) is 1.7 / 3.2 / 7 nm at the threshold trapped densities of 2 / 6.3 / 13.2 nm (7.2e18 / 2.0e18 / 4.2e17 cm⁻³).
- **Band bending across the film at threshold.** It is only 0.026 / 0.057 / 0.020 eV (1-D), and 0.022 / 0.045 / 0.016 eV in the ATLAS profiles (run_0012 / run_0015 / run_0013).
- **Carrier location.** Subthreshold conduction is volumetric (electron centroid 0.8 / 2.1 / 5.7 nm from the front). In the on-state at 3 V all films carry a ~0.7–1.1 nm front accumulation layer (ATLAS profiles), which couples to S3.
- **Depletion width W = Qs/Nd.** At the V1 Nd (2.5–3e17), a surface charge of 1e12 cm⁻² depletes 40 nm. Every film ≤ 31.8 nm is therefore fully depleted.
- **Condition for a neutral layer between 6.3 and 13.2 nm.** With Qs ≈ 1e12, it would need 7.6e17 < Nd < 1.6e18.

### 2.2 Lever arm of a back-surface sheet charge

Values in V per 1e12 cm⁻².

| t (nm) | front, analytic 1/Cox | back, analytic (1/Cox + t/ε_s) | back, 1-D full DOS, on Vth_cc | back, 1-D without tail, on Vth_cc | back, 1-D, on Vth_lin | back, 1-D, ΔSS_cc (mV/dec) |
|---|---|---|---|---|---|---|
| 2.0 | 0.179 | 0.218 | 0.185 | 0.195 | 0.168 | −11 |
| 6.3 | 0.179 | 0.301 | 0.172 | 0.220 | 0.077 | −38 |
| 13.2 | 0.179 | 0.436 | 0.215 | 0.261 | 0.064 | −47 |

**ATLAS cross-check.** A3 (run_0030): −1.64e12 at the back gives +0.278 V, against +0.293 V for the same charge at the front, a ratio of 0.95.

**Why the analytic back lever does not apply.**
- The threshold current is carried at the front, not the back.
- The negative back charge empties the tail states in the back half of the film (self-compensation).

**The back-charge signature.** A back charge has almost front-equivalent leverage on Vth_cc, weak leverage on Vth_lin, and a strong SS_cc reduction. This is its distinguishing, model-conditional signature.

### 2.3 Neutral layer versus a step (uniform-Nd scan, 1-D B5, Qf 1.73e12, confinement on)

**Vth_cc versus uniform Nd.** Uniform donors give Vth = V0 − q·Nd·t/Cox − q·Nd·t²/(2ε) − …, which is smooth in t.

| t (nm) | Nd = 2.5e17 | Nd = 1e18 | Nd = 2e18 | Nd = 3e18 |
|---|---|---|---|---|
| 13.2 | +0.069 V | −0.211 V | −0.619 V | −1.03 V |
| 31.8 | −0.22 V | −1.39 V | −2.95 V | always on, Id(−3 V) 2.5e-7 A/um |

- **31.8 nm with the V1 law** (Nd 1.85e18): Vth −2.71 V and Id(−3 V) 1.2e-12 A/um, so not always on. This is consistent with V0 needing a back donor sheet plus series R.
- **The slope ratio test.** The steepest interval-slope ratio this form can give is (6.3+13.2)/(2+6.3) = 2.35 (pure t² term). The measured ratio is:
  - −0.004 vs −0.081 V/nm, about 20×;
  - about 9× after the CC-mobility correction.

  With confinement the model ratio is < 1: the model drops 0.33 V from 2 to 6.3 nm and 0.30 V from 6.3 to 13.2 nm.
- **No ungated neutral layer in 13.2 nm.** Its off-band current of 6.6e-12 A/um bounds any ungated free sheet to ≤ 2e7 cm⁻² (n_s = I·L/(q·mu·Vd), mu 59). A neutral sheet of only 1e10 cm⁻² would carry 3.3e-9 A/um.
- **What 31.8 nm needs.** Its always-on state needs at least 5.6e11 to 9.2e11 cm⁻² ungated, i.e. uniform Nd ≥ 3e18 (1-D). That value would put 13.2 nm at −1.0 V. The 13.2 → 31.8 transition therefore requires a ≥ 10× change in effective donor density (or a surface donor layer), which is a material step rather than dimensional electrostatics.

**The Ion step.** From 6.3 to 13.2 nm, Ion rises 7.6×. Of that:
- ×1.66 is electrostatic: Cox·(3 − Vth_lin) ratio, about 25 % in log terms;
- ×4.58 is mu_FE, about 75 %.

**Verdict.** A neutral bulk layer does not explain the 6.3→13.2 step in Vth or Ion. A single-material law, whether a power law or t/t², cannot produce it either. A step requires a change of material between 6.3 and 13.2 nm, in charge (about +1.4e12 cm⁻² in the no-confinement reading) and in mobility. This couples to S2's two-regime reading.

## 3. The 6.3 nm discrepancy: campaign A (task 3)

### 3.1 Results

Deltas are relative to run_0014 (Vth_cc 0.350, Vth_lin 1.212, SS_min 108.2, SS_cc 284.9, gm 2.860e-7, Ion 5.11e-7, RMSE 0.678 dec) and to the measurement (0.644 / 1.820 / 114.7 / 295.4 / 3.431e-7 / 4.03e-7).

| run | hypothesis | ΔVcc | ΔSSmin | ΔSScc | ΔVlin | Δgm | ΔIon | vs meas: Vcc | vs meas: SScc | vs meas: Vlin | vs meas: gm | vs meas: Ion | RMSE (dec) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0015 | tuned front Qf 8.7e10, mu 11.69 (calibration) | +0.301 | +2.6 | +3.9 | +0.259 | −7.7 % | −21 % | +0.007 | −6.5 | **−0.349** | **−23 %** | 0 % | 0.063 |
| 0030 | A3 back −1.64e12 | +0.278 | −10.5 | −53.6 | +0.140 | −2.1 % | −9.8 % | −0.017 | **−64.1** | −0.468 | −18 % | +14 % | 0.237 |
| 0031 | A1 t = 5.3 nm | +0.036 | +9.1 | +5.5 | +0.053 | −1.8 % | −4.7 % | −0.258 | −4.9 | −0.555 | −18 % | +21 % | 0.613 |
| 0032 | A2 Nd0 1e16 | +0.030 | +6.5 | −4.2 | +0.015 | −1.0 % | −1.8 % | −0.264 | −14.7 | −0.593 | −18 % | +24 % | 0.634 |
| 0033 | A4 Dit × 5 | +0.051 | +8.3 | +1.3 | +0.046 | −0.3 % | −2.9 % | −0.243 | −9.1 | −0.562 | −17 % | +23 % | 0.595 |
| 0034 | A6 no confinement, Qf from 2 nm (held-out) | +0.237 | +9.4 | +2.8 | +0.214 | −2.2 % | −14 % | **−0.057** | −7.7 | −0.394 | −18 % | +9 % | **0.211** |
| 0035 | A5 5.8 nm + Nd 1e16 + back −1e12 | +0.215 | −11.0 | −35.5 | +0.124 | −3.5 % | −10 % | −0.079 | −45.9 | −0.484 | −20 % | +14 % | 0.246 |

A7 (run_0036, mesh × 0.7) has no `execution.json` (STARTED only in RUN_INDEX): NOT DETERMINED.

### 3.2 Required values and physical plausibility

- **A1 (thickness error): rejected.**
  - A −1 nm error (−16 %) gives only 12 % of the miss.
  - Closing 0.29 V through the confinement law needs dEc ≈ 0.33 eV, i.e. t ≈ 2.1 nm, a 67 % thickness error.
  - The thickness method and uncertainty are NOT DETERMINED, but a 4 nm error is not credible for a thickness series.
- **A2 (donors): rejected.** It is bounded at +0.030 V (analytic 0.028), i.e. ×10 short.
- **A4 (front Dit): rejected at plausible density.**
  - At ≈ 0.013 V per 1× (3e11 cm⁻²/eV), closing the miss needs a peak of ≈ 7e12 cm⁻² eV⁻¹. That is 23× the assumed value and about 12× the HfO2/In2O3 proxy of 6e11 (yaml, Wang2022).
  - It would also have to be present at 6.3 nm only, on a gate stack shared by all thicknesses.
  - Placed at Ec − 0.3 eV it is filled at threshold, so it acts as a disguised fixed charge.
- **A3 (back-surface negative charge): reproduces Vth_cc (−0.017 V) but is rejected as the sole cause (model-conditional).**
  - It moves SS_cc 64 mV/dec and SS_min 17 mV/dec away from the measurement.
  - It worsens the on-state lag (Vth_lin −0.47 V).
  - The −1.64e12 magnitude has no local source ("adsorbate scale" is an assumption).
  - All films were air-exposed. The same charge at 2 nm or 13.2 nm would shift them by 0.30 or 0.35 V (lever 0.185 / 0.215 per 1e12), so it cannot be specific to 6.3 nm without a sample-specific cause.
- **A5 (combination): rejected.**
  - Individually "plausible" values deliver 0.215 of the 0.294 V (73 %).
  - The back-charge SS signature is again wrong (SS_cc −46).
- **Tuned front charge (0015): fits by construction (calibration).** It is a charge 1.64e12 cm⁻² less positive than at 2 and 13.2 nm, with no independent observable.
- **A6 (no confinement): the best held-out result.**
  - Vth_cc −0.057 V and SS_cc −8, with the same on-state shape error as 0015.
  - Its 6.3 nm Qf would be −2.7e11, i.e. 3.2e11 cm⁻² (0.057 V) from the 2 nm value. That is a difference that N = 1 device-to-device spread could produce (spread NOT DETERMINED).

### 3.3 The on-state shape is not an offset

Every hypothesis leaves gm within −0.3 to −3.5 % of run_0014 and the gap Vth_lin − Vth_cc at 0.72–0.88 V. The measured gap is 1.176 V, against 1.001 V (2 nm) and 0.962 V (13.2 nm).

The horizontal offset Vg_meas(I) − Vg_sim(I) for the tuned run_0015 is:

| I (A/um) | 1e-10 | 1e-9 | 1e-8 | 3e-8 | 1e-7 | 2e-7 | 3e-7 |
|---|---|---|---|---|---|---|---|
| offset (V) | −0.003 | −0.007 | +0.011 | +0.047 | +0.132 | +0.141 | +0.087 |

For the 2 and 13.2 nm fits the offset stays within ±0.035 V at all levels.

The measured 6.3 nm curve therefore turns on late (about +0.14 V, ≈ 8e11 cm⁻² equivalent near 1–2e-7 A/um) and then rises more steeply. This is a gate-voltage-dependent quantity. A rigid charge at any location cannot produce it: a back charge makes it worse, because it shifts Vth_lin only 0.4× as much as Vth_cc.

**Test of electrostatic alternatives** (1-D, `s1_shape_test.out.txt`, calibration). An acceptor band of 1.5–3e12 cm⁻² at Ec − 0 to 0.15 eV (W 0.05) was added, and Qf and mu were refit to Vth_cc and Ion.

| case | best gap (V) | SS_cc (mV/dec) |
|---|---|---|
| best acceptor band | 0.97 | 344 (measured 295) |
| no band | 0.83 | — |

S2's pre-registered B0 partition (Nt 2.66e19, mu_band 19.6, Qf 9.8e11) gives in 1-D:
- Vth_cc 0.656, Vth_lin 1.889, gap 1.233;
- gm 3.31e-7 (mu_FE ≈ 10.6), Ion −8.8 %;
- **but SS_cc 418 mV/dec** (+123 mV/dec against the measurement).

This is registered here as an S1 prediction for the ATLAS B0 run. It is expected to be within about 10 mV/dec of that value, given the surrogate's bias.

**Implication.** Gap states that repair the shape destroy the subthreshold slope. The shape needs charge or conduction that switches on only when E_F approaches or crosses Ec. The candidates are:
- a carrier-density-dependent (percolation-type) mobility (S2);
- states above Ec;
- trapping that grows only above threshold during the forward sweep (PBS-like). Januar reports ΔVth 0.72 V (10 nm IWO) and ~1.2 V (2 nm IWO) after 6 V / 1200 s (Januar2026 lines 612–616), so the scale is plausible, but sweep rate, dwell and hysteresis are NOT DETERMINED.

Contact resistance (S5) is excluded as the cause: it would lower gm at high Vg, whereas the measured gm is 23–29 % higher.

### 3.4 Identifiability and conclusion

**Degenerate rigid-shift parameters.** On one ID-VG curve, these all enter Vth_cc as rigid shifts at first order, and only their weighted sum is identified (≈ 1.64e12 cm⁻² ≡ 0.29 V at 6.3 nm):
- WF, χ, dEc, Qf;
- Qb (lever 0.96× front);
- Nd·t (+ t² term);
- filled Dit.

**Location** (front / back / bulk) is separable only through second-order SS_cc and gap signatures. These depend on the fitted Nt and WTA, so the separation is model-conditional. With the V1 DOS the measured SS_cc (295) prefers a front or bulk charge (289) over a back charge (231).

**Degeneracy breakers:**

| to identify | measurement |
|---|---|
| back-surface charge | vacuum/air or passivated/unpassivated comparison; top gate or KPFM |
| front charge and Dit | C-V flat-band per thickness and frequency dispersion |
| confinement vs traps | Vth(T): dEc is T-independent, trap filling is not |
| dEc directly | band edge by UPS/optical absorption |

**Non-simulatable candidates**, all NOT DETERMINED from the available data:
- hysteresis or sweep direction;
- bias stress during the sweep;
- sample-to-sample variation (N = 1 per thickness);
- thickness error;
- ambient or day of measurement.

**Conclusion.** The 6.3 nm "discrepancy" is best explained as an artefact of the confinement law rather than a property of the 6.3 nm film:
- 86 % of the model's 2→6.3 drop is dEc(2) − dEc(6.3);
- removing confinement and calibrating on 2 nm alone predicts 6.3 nm to −0.057 V (held-out).

No single physical charge hypothesis at plausible magnitude closes the miss (A1/A2/A4 give 10–17 %; A3/A5 give the wrong SS). The on-state shape miss (gap +0.35 V, gm −23 %) is separate, common to all runs, and Vg-dependent.

**Certainty: moderate to low.** There is N = 1 per thickness and one held-out point, and the symmetric reading (§4) cannot be excluded by the Vth values alone.

## 4. The symmetric calibration (task 4)

Single-charge misses (model − measured Vth_cc) and the Qf that each film would need:

| film | with confinement: miss | with confinement: Qf needed | without confinement: miss | without confinement: Qf needed |
|---|---|---|---|---|
| 2 nm | +0.014 | 1.81e12 | +0.003 (fit) | 4.8e10 |
| 6.3 nm | −0.294 | 0.09e12 | −0.057 (A6) | −2.7e11 |
| 13.2 nm | −0.030 | 1.56e12 | +0.247 | 1.43e12 |

Sources: with confinement, the calibration Qf of 1.73e12 (runs 0012/0014/0013). Without confinement, Qf = 4.76e10 (1-D B4: 0.665 / 0.588 / 0.330; the rigid shift of run_0017 gives 0.331).

The brief quotes ~1.86e12 for the 13.2 nm no-confinement Qf. My rigid-shift value from run_0017 is 1.43e12. This does not change the conclusion.

**Both readings need one film-specific charge of about 1.4–1.6e12 cm⁻².** The no-confinement assignment, with (2, 6.3) clustered and 13.2 as the outlier, is more natural:
1. 13.2 nm differs independently in every other metric: mu_FE ×4.6, SS_cc 160 vs 270–295, off-floor ×44, and it is on the path to the always-on 31.8 nm. The 6.3 nm film matches 2 nm in mu_FE, Ion and SS_cc.
2. The needed extra positive charge rises monotonically with thickness. This is consistent with Kim2024 (a different IWO process, 10–30 nm), where V_on shifts negative with T_ch.
3. A single uniform extra Nd (8.3e17 cm⁻³, i.e. total ≈ 1.1e18) plus one offset fits all three films to within +0.056 / −0.077 / +0.020 V (linearised LSQ, 1 d.o.f.). With confinement, no non-negative Nd can lift 6.3 nm: A2 caps it at +0.03 V, so the 6.3 nm residual stays ≥ 0.2 V.
4. The confinement law is a pure-In2O3 DFT fit at ≤ 1.98 nm, extrapolated (S3).

**The data cannot decide by Vth alone:** it is 3 points, N = 1, with 2 parameters per reading. The decisive measurements are:
- Vth(T);
- a band edge versus t;
- C-V;
- several devices at 2, 4–5, 6.3, 8–10 and 13.2 nm.

## 5. Couplings

- **S2.** mu_FE sets Vth_cc through the CC definition: 0.11–0.14 V of the 2→13.2 step. The on-state shape is a trap/mobility partition problem. B0 1-D predicts SS_cc 418 (risk), which favours a density-dependent mobility.
- **S3.** dEc carries 0.281 V of the model's 2→6.3 difference, and Vth responds to dEc at ≈ 1 V/eV. The on-state front-accumulation centroid is about 1 nm, where quantum dark space lowers the effective Cox.
- **S4.** The tail term is 0.10–0.26 V, 25 % of the 2→13.2 step. Nt, WTA and Qf trade off, and the location signatures depend on the DOS.
- **S5.** R_c cannot give the higher measured gm.
- **S6.** Register B0 (SS_cc 418) and a 13.2 nm no-confinement run with Qf 4.76e10 (predicted Vth_cc 0.33).

## Verdicts

| mechanism | verdict | evidence class | key number |
|---|---|---|---|
| V1 6.3 nm miss = confinement difference dEc(2) − dEc(6.3) | demonstrated (within model) | prediction (1-D checked vs 12 ATLAS runs) | 0.281 of 0.328 V (86 %) |
| No confinement, one Qf (2 nm) predicts 6.3 nm | plausible-unverified (favoured) | prediction (A6 held-out) | Vth_cc −0.057 V, RMSE 0.21 vs 0.68 dec |
| Tuned 6.3 nm-specific front charge | plausible-unverified | calibration | 1.64e12 cm⁻² (0.294 V) |
| Back-surface negative charge (sole cause) | rejected (model-conditional) | prediction (A3) | SS_cc −64 mV/dec, Vth_lin −0.47 V |
| Thickness error | rejected | prediction (A1) + analytic | −1 nm → +0.036 V; needs t ≈ 2.1 nm |
| Reduced donors | rejected | prediction (A2) | ≤ +0.030 V |
| Front Dit | rejected at plausible Dit | prediction (A4) | needs ≈ 7e12 cm⁻²eV⁻¹ (23×) |
| Plausible combination A5 | rejected | prediction | 73 % of miss, SS_cc −46 |
| 6.3 nm on-state shape is a rigid offset | rejected | prediction (all campaign-A runs) | gap 0.72–0.88 vs 1.18 V |
| Gap-state trap band / B0 fixes shape at constant SS | rejected (1-D) | calibration | best SS_cc 344; B0 418 vs 295 |
| Sweep-induced trapping / sample variation | not determined | none | Januar PBS 0.7–1.2 V (6 V, 1200 s) |
| Back-referenced lever arm (Q·t/ε_s) at threshold | rejected | prediction (1-D + A3) | 0.96–1.2× front, not 1.7–2.4× |
| Neutral bulk layer / homogeneous t, t² law as the 6.3→13.2 step | rejected | prediction (1-D) + data bound | slope ratio ≤ 2.35 vs ~9–20; ungated n_s(13.2) ≤ 2e7 cm⁻² |
| 31.8 nm always-on from a neutral layer | plausible-unverified | prediction (1-D) | needs Nd ≥ 3e18 (≥ 10× the 13.2 nm-compatible value) |
| CC-definition (mobility) share of the Vth_cc step | strongly supported | prediction (analytic on data) | +0.11–0.14 V of −0.58 V |
| q·Nd·t/Cox | demonstrated small (≤ 6.3 nm) | prediction (A2, run_0022) | 0.009 / 0.028 / 0.070 V |
| Tail charge at threshold | plausible-unverified | calibration | 0.256 / 0.226 / 0.098 V |
| Interface-trap charge | demonstrated small | prediction (run_0025, A4) | 0.012 V, thickness-independent |
