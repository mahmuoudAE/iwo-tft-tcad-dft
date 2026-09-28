# Referee report: IWO thickness-series TCAD analysis (V1 model and the 2026-09-25 specialist reports)

Reviewer: an adversarial referee working to the IEEE TED / EDL / Nature Electronics standard. Date: 2026-09-25.

**What I did and did not do**
- No ATLAS launch. No package script or config was modified.
- Every recomputed number comes from `analysis_2026-09-25/scratch/REVIEW/review_verify.py`, whose output is `review_verify_out.txt`.
  - It imports `scripts/extract_metrics.py` unchanged.
  - It reads `data/experimental_clean.csv`, and `comparison.csv`, `idvg.dat`, `execution.json` and `metadata.json` in `results/runs/*/`.
  - It also reads the deckbuild logs of run_0045 and run_0027 and file timestamps.
- Where I rely on a specialist surrogate that I did not re-run, I say so in section 3.

**Documents reviewed**
- The claims currently made: `FINAL_STATUS.md` and `docs/SUPERVISOR_SUMMARY.md`.
- The analysis behind them: `EVIDENCE_BRIEF.md`, S1-S6, `PREDICTIONS_REGISTER.md`, and the campaign JSONs A, B and C.

---

## 0. Recommendation and the three findings that decide it

**Recommendation: reject in current form.** I would reconsider as a major revision if two conditions are met:
- the paper is reframed as a calibrated, explicitly non-unique TCAD description with no mechanism claim;
- at least one independent comparison from section 6 is added.

**1. The threshold data cannot tell "confinement" from "no confinement".**

Each reading is fitted with one rigid offset (a Qf change is exactly rigid; see V5). I then compare the RMS Vth_cc miss.

| test | V1 with confinement (V) | V1 without confinement (V) |
|---|---|---|
| least-squares offset on all 3 films | 0.136 | 0.133 |
| leave-one-out | 0.205 | 0.199 |
| offset fitted on 2 nm only (held-out 6.3 and 13.2) | 0.221 | **0.180** |
| offset fitted on 13.2 nm only | **0.190** | 0.278 |
| offset fitted on 6.3 nm only | 0.288 | 0.220 |

The "winner" is decided by which film is held out.

- **FINAL_STATUS #1 and SUPERVISOR #1** say confinement "accounts for the 0.58 V threshold difference" and "was tested". Not supported.
- **S1** says the 6.3 nm discrepancy is "best explained as an artefact of the confinement law". Not supported either.
- **S3** says the data "mildly disfavour" confinement. Also not supported.

The two readings simply move the one film-specific charge between films:
- with confinement, 6.3 nm needs about 1.64e12 cm^-2 of its own;
- without it, 13.2 nm needs about 1.39e12 cm^-2 of its own.

**2. Nothing has been validated.** Every reproduced quantity was fitted on the same curve.
- The "validation" run_0014 is not parameter-free. Its mu_band of 12.4 is the V0 per-film fit of this same 6.3 nm curve (`config/iwo_material_model.yaml` mu_band_fitted 6.3: 12.4; `docs/MATERIAL_PARAMETER_EXTRACTION.md`), and it still misses Vth_cc by -0.294 V.
- The only held-out success, A6, was designed after the miss was known.
- Both pre-registered mechanism tests failed or only partly passed:
  - B0: SS_cc +116 mV/dec against the measurement;
  - C1: gap +0.12 V against +0.28 V predicted, and Ion +16 % against ±3 %.
- The one reproduction of independent published numbers (the paper's 5.1 and 27.4 cm^2/Vs) validates data provenance, not device physics.

**3. The evidence base is one device per thickness.**
- The drain bias and the units come from a schematic.
- There is no sweep direction, IG/IS, temperature, C-V or ID-VD.
- Every statement about "the 6.3 nm film" is therefore also a statement about one unrepeated device.

---

## 1. Answers to the eight questions

### (a) Are the parameters uniquely determined? — NOT SATISFIED

**Exact or near-exact degeneracies**, recomputed on the ATLAS curves:
- **Qf is an exact rigid shift at every thickness.** Across 1e-14 to 3e-7 A/um the shift is:

  | runs | film | shift (V) |
  |---|---|---|
  | 0001 → 0003 | 2 nm | -0.3092 to -0.3098 |
  | 0002 → 0004 | 13.2 nm | -0.3094 to -0.3098 |
  | 0005 → 0007 | 6.3 nm | +0.2936 to +0.2942 |

  The analytic values are 0.3095 and 0.2939 V.
- **Gate WF +0.1 eV** (runs 0048/0049) gives exactly +0.1000 V at both films, with SS_cc changed by 0.0 mV/dec.
- **One number.** WF, χ, Qf and the pure dEc term are therefore one number per curve.
- **mu_band trades against Nt on Ion.** Nt ×1.5 is equivalent to mu ×1.33 (run_0023; S2 Jacobian).
- **Rsd trades against the tail exponent.** The α-θ correlation is +1.00 (S5; not re-run by me).
- **Nt, WTA, Dit and near-Ec states trade off** on SS and on the gap (S2, S4, S6).

**Fitted parameters.** Against three curves (brief §3) the fit uses:
- Qf: one shared value and one device-specific value;
- mu_band ×3;
- the Nt anchor and WTA;
- three Nd-law constants from V0;
- a V0-fitted mobility (12.4) in the "validation" run.

**Assumed values.** WF 4.70 eV, χ 4.3 eV, Dit 3e11, the deep Gaussian and ε(Al2O3) = 9.0 all sit inside the degenerate sets. So Qf = 1.73e12 cm^-2 is an alignment absorber, not a charge: ±0.2 eV of TiN work function is equivalent to ±1.12e12 cm^-2.

**What would satisfy me:**
- An identifiability analysis on the metric set actually fitted: profile likelihood, or Fisher/Jacobian rank. It should list which *combinations* are identified.
- Independent pins for at least three of them: V_FB(t) from C-V, n_free/n_total from split C-V or gated Hall, and Rc from TLM.
- Retire the phrase "parameter extraction" (FINAL_STATUS) in favour of "calibrated, non-unique parameter set".

### (b) Is the model validated or merely calibrated? — NOT SATISFIED (calibrated)

**The fits:**
- At 2 and 13.2 nm, Ion and Vth_cc are fitted: Ion errors +0.00 % and -0.02 %; Vth_cc within +19 and -27 mV (B1 and B3 as run).
- The tuned 6.3 nm run has two device-specific parameters.
- The "validation" run_0014 uses a V0 mobility fitted to the same curve and misses Vth_cc by -0.2941 V (recomputed).

**The prospective tests:**

| test | recomputed result | what it tests |
|---|---|---|
| A6 | Vth_cc -0.0573 V | threshold only, and designed post hoc |
| B0 | SS_cc 410.95 vs 295.37 mV/dec | fails |
| C1 | gap +0.119 V vs +0.28 predicted; Ion +16.0 % vs ±3 % | partly fails |
| P7 | S2 surrogate vs ATLAS P-MTR | a numerical cross-check, not an experiment |
| 5.09 / 27.40 | reproduction of the paper's numbers | data provenance and extraction, not the device model |

**Registered predictions.** The ID-VD and temperature predictions are not yet tested.

**What would satisfy me:**
- At least one comparison of registered predictions with measurements not used in calibration, with the quantity, tolerance and pass/fail stated before the data are opened. Candidates:
  - Januar SI Fig. S12 (2 nm at 338/358 K), taken as changes relative to that device's own 300 K curve. ΔVth_lin = -17 / -27 mV is the same in both registered variants, so it is the sharpest test.
  - ID-VD of the same devices.
  - A fourth thickness predicted blind.

### (c) Could the power law be accidental over this thickness range? — NOT SATISFIED

**Every thickness law in V1 is a two-point law or an extrapolation.**
- **Nt ∝ t^-0.75.** The exponent is ln 4 / ln 6.6 = 0.7346 (recomputed). It comes from the phrase "roughly a factor of four" (Januar l.515-516).
  - The same paper's PBS devices imply an exponent of 1.71 (S2, S4).
  - The "factor of four" comes from the paper's Fig. 5a μmax-Nt analysis, which is built on saturation-formula mobilities used outside their regime (V3).
  - A surface + bulk form through the same anchors differs by only 8 % at 6.3 nm (S4).
- **dEc = 0.9205 t^-1.3815.** This is a 3-point PBE fit over 0.95-1.98 nm, extrapolated by a factor of 3.2 and 6.7 in t.
  - It crosses the infinite-well effective-mass upper bound at t = 2.98 nm (recomputed).
  - At 6.3 nm it gives 72 meV against 46 meV for m* = 0.208, i.e. ×1.59.
- **Nd law.** It has three constants fitted to one V0 shoulder.

**With three thicknesses, any two-parameter law passes exactly through two of them.** The one out-of-sample point fails:
- the 6.3 nm Vth misses by -0.294 V;
- a mu_FE power law through 2 and 13.2 nm (exponent 0.7516) predicts 28.8 against 10.95 cm^2/Vs, i.e. ×2.63.

**S2's replacement, a "step between 6.3 and 13.2 nm", is no better supported.**
- Its leave-one-out "win" (×1.11) is circular: t_c was placed in (6.3, 13.2) after the 6.3 nm point was seen.
- With t_c in (2, 6.3), the same form misses by ×4.58.
- It has three parameters for three points.

**What would satisfy me:**
- At least 5-6 thicknesses, including 3-5 nm and 8-11 nm, with at least 3-5 devices each.
- Functional forms compared by held-out prediction, with t_c or the exponent fixed in advance (or AIC/BIC with parameter counts stated).
- Until then the paper must say: "no functional form in t is identified; the laws are interpolations between two anchors."

### (d) Is the 6.3 nm discrepancy actually understood? — NOT SATISFIED

**The offset (0.29 V) is not assigned.** As shown in §0, a film-specific charge at 6.3 nm (with confinement) and one at 13.2 nm (without confinement) fit equally well. None of the non-simulatable causes is excluded:
- hysteresis;
- bias stress during the sweep (S4 estimates 0.003-0.24 V);
- thickness error;
- device-to-device spread.

All are NOT DETERMINED.

**The shape is not explained.** Recomputed for the tuned run_0015:
- gap (Vth_lin - Vth_cc) 0.820 V against 1.176 V measured;
- gm_max -23.1 %;
- Vth_lin -0.349 V.

The tested variants do not fix it:
- the seven electrostatic variants give gaps of 0.72-0.88 V;
- B0 opens the gap (1.202 V) only by adding +122 mV/dec of SS_cc relative to run_0015;
- C1 recovers 33-35 % of the gap.

**S6's "constant, density-independent mobility" is not a tested mechanism.** It is inferred from a trade-off line.
- It also implies a same-signed miss at 2 nm, which exists but is not reported in FINAL_STATUS: gap -0.145 V, gm -8.6 % (recomputed on B1).

**What would satisfy me:**
- Replicates at 6.3 nm, to measure the Vth spread.
- Dual sweeps with the dwell recorded.
- Transfer curves at Vd = 0.05-0.1 V.
- One mechanism, with shared parameters, that reproduces Vth_cc, the gap, gm and SS_cc of all three films together, and is then tested on a held-out observable.

### (e) Are the numerical results converged? — PARTIALLY

**Satisfied for the 300 K transfer metrics:**
- **Mesh ×0.7 at 6.3 nm** (A7): RMSE 0.06247 vs 0.06261 dec, ΔVth_cc -0.32 mV, Ion -0.027 % (recomputed).
- **Mesh ×0.7 at 13.2 nm** (run_0028).
- **DOS refinement at 2 nm** (96 → 192 → 384 levels): Ion +1.983 % then +0.484 %, observed order p = 2.03, Richardson residual +0.156 % (recomputed).
- **Linearity in mu:** the run_0029/run_0038 ratio is 1.024879 against 1.024873.
- **KCL** is satisfied.

**Not demonstrated:**
- **2 nm mesh on the V1 deck.** There is no check on the V1 2 nm physical-structure deck. Check A is inherited from V0 "lineage" (`docs/NUMERICAL_CONVERGENCE.md`), for the thinnest film with 8 + 4 vertical intervals.
- **DOS order at 6.3 and 13.2 nm.** Only two DOS levels were run, so no order estimate exists.
- **Temperature runs.** No DOS or mesh check at 338/358 K (the register admits this).
- **ID-VD at high Vd.** No mesh check near pinch-off, although Vd_sat and gd(3 V)/gd0 = 0.01-0.68 % are registered and are mesh-sensitive.
- **C1's narrow band.** There is no DOS-resolution check for its 20 meV Gaussian. If the 384 levels are spaced uniformly over the ~3.1 eV gap, about 4 levels fall within its ~33 meV FWHM. The level placement is NOT DETERMINED, so C1's partial-fail verdict may be affected by discretization.
- **Coarse solver grid.** The 0.1 V solver grid above 1.5 V biases Vth_lin by up to -12 mV (S6).
- **SS_min is not a converged metric.** A 2.5 % current rescale flips it by 10 mV/dec (V9).

**What would satisfy me:**
- V1 2 nm mesh ×0.7 (vertical and lateral);
- DOS 192/96 at 6.3 and 13.2 nm, to get the order;
- one DOS check at 358 K;
- one ID-VD mesh check near the drain;
- C1 at 768 levels, or the ATLAS level placement documented.

(The launch budget is exhausted, so these are paper requirements, not package requirements.)

### (f) Is quantum confinement demonstrated or merely assumed? — NOT SATISFIED (assumed)

**It enters as an imposed band-edge shift.**
- dEc is a rigid band-edge shift from pure-In2O3 PBE slabs; no DFT was run for IWO.
- On one ID-VG curve it is equivalent to fixed charge: dEc(2 nm) = 0.353 eV ≡ 1.97e12 cm^-2, and the realised 0.3156 V ≡ 1.76e12 cm^-2.
- The Vth data neither require nor reject it (§0).

**The only same-curve signature is small.** The m*(t) → Nc part makes the V1 confinement package non-rigid:
- the horizontal shift between runs 0012 and 0016 is 0.3446 V at 1e-14 A/um, 0.3017 V at 1e-8 and 0.3109 V at 3e-7;
- SS_cc is 289.1 vs 303.7 mV/dec.

That is 43 mV and 14.6 mV/dec, below the leverage of the fitted WTA (+12.4 mV/dec per 5 meV) and Dit.

**S3's Schrödinger-Poisson result is theory, not a measurement on these films.** A 0.26-0.30 V shift at 2 nm is physically plausible, but the bracket is 0.14-0.38 V, set by m*.

**What would satisfy me:**
- A spectroscopic band edge versus t on these films: optical gap, IPES, or UPS/XPS plus the optical gap. S3's discriminator is +0.2 to 0.45 eV at 2 nm (confinement) against < 0.02 eV (charge).
- Alternatively, Vth(T) together with C-V V_FB(t).
- Delete "it was tested" (SUPERVISOR #1).

### (g) Are contact/interface effects sufficiently separated from bulk semiconductor effects? — PARTIALLY

**Accepted.** S5's order-of-magnitude case that a thickness-independent Rsd cannot *create* the thickness trend. It would need:
- ρc ≈ 0.26 Ω·cm²;
- 83 % of Vd dropped at the contacts;
- and θ_net is negative in every film, the wrong sign for Rsd.

**Not separated:**
- **Rsd magnitude.** The α-θ correlation is +1.00, there is one channel length and no TLM, and the bounds (≲ 5e4 Ω·µm at 2 nm, ≲ 1-2e4 Ω·µm at 13.2 nm) hold only inside the calibrated trap model.
- **Front vs back vs bulk charge.** These are separable only through model-conditional SS signatures (S1).
- **Interface vs bulk traps.** S4's Ds + g_b·t rests on an inversion that needs mu:
  - its energy axis shifts by kT·ln(mu ratio);
  - at 13.2 nm it was validated only near Ec - 0.1 eV (×0.52-3.4 elsewhere).
- **Contact barrier.** An ideal Ohmic boundary cannot represent a contact barrier (S5 M2).
- **run_0027 is malformed** (verified):
  - `x.mesh` ends at 24 µm while the electrodes run to 28 µm;
  - deckbuild.out reports "Electrode shortened in X-direction" 3 times.

**What would satisfy me:**
- TLM or an L-series, which gives Rc and also tests whether the floor scales as 1/L;
- low-Vd ID-VD;
- C-V V_FB(t): a front sheet scales as t^0, a back sheet as t/ε_s;
- passivated vs air-exposed splits.

### (h) What experimental result could falsify the preferred mechanism, and is the preferred mechanism stated falsifiably? — NOT SATISFIED

**There is no single preferred mechanism.** The documents prefer different stories:

| document | preferred mechanism |
|---|---|
| FINAL_STATUS | confinement + Nt law + a 6.3 nm device-specific offset |
| S1 | no confinement; 13.2 nm is the outlier |
| S2 | structural step with a density-dependent mobility |
| S4 | donor step + near-Ec states |
| S6 | a constant-mobility model-form error |

**FINAL_STATUS's form is unfalsifiable on ID-VG.** Any Vth pattern can be absorbed into one "device-specific flat-band offset".

**The registered falsifiers mostly test auxiliary assumptions** (Ohmic contacts, T-independent mobility), not the thickness mechanism:
- Id(0.1)/Id(0.05) = 1.80-1.98 is what any long-channel Ohmic TFT gives.
- The ΔVth_cc envelope at 358 K (-35 to -85 mV) is wide.
- The mobility exponent g is to be fitted from the measurement, which turns Ion(T) into calibration.
- Only two registered items bear on thickness: the "mu_FE ratio shrinks toward 3.3" item and the Ea(3 V) ordering.

**What would satisfy me:** one stated mechanism, with a pre-declared observable, tolerance and failure condition. Examples:

| mechanism | falsified if |
|---|---|
| "structural step" | GIXRD/TEM shows the same phase and grain size at 6.3 and 13.2 nm, or Hall mobility at 6.3 nm is within 30 % of 13.2 nm |
| "confinement" | the optical-gap shift between 2 and 13.2 nm is below 0.1 eV |
| "6.3 nm is device variation" | replicates give σ(Vth) < 0.1 V with a mean still 0.29 V off the shared law |
| "MTR-limited transport" | μ_FE(3 V) at 2 nm rises by more than 5 % between 300 and 358 K |

---

## 2. Further objections

**2.1 Drain bias and units from a schematic (major).**
- Vd = 0.7 V and A/µm come only from the schematic/PPTX (`data/data_summary.json`, `_units_note`).
- The saturation-formula reproduction shows only that the workbook, L/(W·Cox) and the *paper's own* constants are mutually consistent:
  - μ_sat does not contain Vd;
  - a constant shared with the paper, even a wrong one (e.g. the assumed ε(Al2O3) = 9.0), would reproduce just as well.
- S2's "Cox, W/L and A/µm confirmed to three significant figures" is therefore overstated.
- Every ATLAS run and every linear μ_FE assumes Vd = 0.7 V.
- *Satisfy:* the instrument setup file or the lab notebook.

**2.2 N = 1 per thickness (fatal for mechanism claims).**
- The 6.3 nm "anomaly" is 0.29 V. S3's own power estimate needs n ≈ 3 (σ = 0.05 V) to 10 (σ = 0.10 V) devices per thickness to resolve 0.13 V.
- No claim about a film-specific property is admissible without replicates.

**2.3 Sweep direction, dwell, hysteresis and bias history unknown (major).**
- Januar PBS gives 0.72-1.2 V shifts after 6 V / 1200 s. S4 scales this to 0.003-0.24 V for one sweep, which is comparable to the 0.29 V offset.
- The 6.3 nm shape feature (late turn-on, then a steep rise) is the kind of signature a sweep-history effect produces.
- *Satisfy:* dual sweeps with the rate and dwell recorded.

**2.4 Paper-vs-workbook mobility definition (resolved for provenance; major for the paper's physics).**
- Recomputed μ_sat = 2L/(W·Cox)·(d√Id/dVg)²:

  | film | μ_sat (cm^2/Vs) | peak at Vg |
  |---|---|---|
  | 2 nm | 5.09 | 1.75 V |
  | 13.2 nm | 27.40 | 0.95 V |
  | 6.3 nm | 3.86 | 2.55 V |

  The values are the same for central, forward and backward differences (13.2 nm: 27.40-27.49). Savitzky-Golay smoothing gives 4.99-5.08 and 25.7-26.4, so the match requires unsmoothed point differences.
- **The regime claims are wrong.**
  - The 13.2 nm peak lies *below* Vth_lin (0.95 < 1.044 V).
  - The 2 nm peak is only 0.09 V above Vth_lin, i.e. in saturation at Vd = 0.7 V. It is not "in the linear regime" (S2).
- **S2's ratio explanation does not reproduce quantitatively.** Vd/(2Vov - Vd), with Vov taken from Vth_cc, predicts μ_sat/μ_FE = 0.474 (2 nm) and 0.676 (13.2 nm). The actual values are 0.419 and 0.546 (and 0.352 at 6.3 nm). The comparison is only indicative, because the two peaks sit at different Vg.
- **Consequence 1: the Nt law's provenance.** The paper's μmax-Nt correlation (Fig. 5a), and so the Nt(t) exponent imported into V1, rest on a formula applied outside its regime.
- **Consequence 2: the paper's SS claim.** The paper's "near-thermal-limit SS (60-70 mV/dec)" (l.209-210) can be obtained from these curves only next to the noise floor:
  - the 5-point SS without the floor gate is 70.6 mV/dec at 0.20 V (2 nm);
  - the 2-point minimum is 58.6 mV/dec (2 nm) and **33.4 mV/dec (6.3 nm, sub-thermal, i.e. noise)**;
  - the floor-gated SS_min is 84.5 / 114.7 / 130.8 mV/dec.

**2.5 Excluding 31.8 nm while citing it (major).**
- The one film the model cannot reproduce (always-on; Id(-3 V) = 3.0e-7 A/µm) was excluded after the model failed on it.
- S2 nonetheless cites its "apparent mu_FE 49.2 ≈ 50.2" as a mobility plateau. That number is gm_max at Vg = -0.30 V of an always-on film:
  - gm has local maxima at -0.30, 0.85, 1.15 and 1.70 V;
  - gm(3 V)/gm_max = 0.067 (recomputed).

  It is not a mobility.
- S1 and S4 also use 31.8 nm for their donor-step readings.
- *Satisfy:* report 31.8 nm as a documented model failure, with its data, and do not use it selectively.

**2.6 Off-state floors (major for the paper; minor for the model).**
- The floors are not modelled, so Ion/Ioff cannot be compared.
- Recomputed floors (median over -2 to -0.5 V):

  | film | median (A/µm) | point scatter | trend |
  |---|---|---|---|
  | 2 nm | 4.606e-15 | — | not flat below -2 V: +1.21 dec/V over -3 to -2 V |
  | 6.3 nm | 1.528e-13 | max/min 3.0-3.5; p10/p90 of I/median 0.55/1.25 | slope -0.011 dec/V; half-window medians agree to 2 % |
  | 13.2 nm | 6.597e-12 | max/min 1.06; p10/p90 0.976/1.025 | flat |

  - The 13.2/2 ratio is 1432.3, i.e. t^3.851.
  - The 6.3 nm scatter is ±45 %, not the "±3 %" S4 states.
- S4's rejection of gate leakage is sound on the *trend*.
- S4's "gate-independent parallel IWO path, conductance ∝ t^3.85" is one of several readings. It cannot be separated from an instrument range or offset floor, or from a path through unpatterned film (patterning NOT DETERMINED), without IG/IS, an L-series and the instrument settings.
- **The 13.2 nm SS match depends on floor subtraction.** S6's fixed-current SS match at 1e-11..1e-10 A/µm for 13.2 nm exists only after subtracting the floor:
  - raw 136.1 mV/dec;
  - floor-subtracted 91.8 mV/dec;
  - model 91.2 mV/dec.

  Subtracting the floor presupposes that it is an additive parallel current, which is unverified.

**2.7 Silicon-default tmu = 1.5 (major process issue).**
- **What happened.** The campaign plan declared a T-independent band mobility, but ATLAS applied mu(T) = mu(300 K)·(T/300)^-1.5.
- **The log line is not direct proof.** `run_0045/deckbuild.out` l.391-393 prints "@ Temperature = 358 Kelvin, mu = 12.977, tmu = 1.5". Here 12.977 is the *300 K* parameter (17.6897 × 0.73359), not the effective mobility.
- **The inference that tmu acted is sound.** It rests on the current ratio:
  - run_0045 / run_0038 gives Ion ratio 0.7742;
  - × (358.15/300)^1.5 = 1.0098;
  - that agrees with S2's independent MTR surrogate.
- **The two-variant construction is exact** for a uniform constant mobility.
- **It is still a configuration-control failure.** The IWO user material carries other silicon defaults in the parameter dump (vsat 9.78e6 cm/s, SRH and Auger coefficients, Alattice 5.43 Å). They are inactive or irrelevant here, but the paper needs a full audit of default versus set parameters.
- **Minor text error in the register.** The register prose quotes ×1.19665 and ×1.30426; the exact values are 1.19669 and 1.30441. The code (`s6_part3_predictions.py` l.64) uses the exact expression, so only the prose is wrong, by 0.012 %.

**2.8 Malformed run_0027 still cited (major until retracted).**
- "Electrode shortened" appears only in run_0027. The other 50 deckbuild logs carry at most the benign "Projection cannot be done" warning.
- It is still cited in three places:
  - `tables/SENSITIVITY_RESULTS.md` l.23 lists it as "MEASURED IN ATLAS";
  - `docs/SUPERVISOR_SUMMARY.md` l.20 says contact geometry is "irrelevant";
  - `docs/LIMITATIONS.md` #11 says "insensitive".
- The runner scored it REAL_ATLAS_SCORED, so ATLAS warnings do not gate acceptance.

**2.9 SS_min is not robust (major, because it is the headline SS in FINAL_STATUS and SUPERVISOR).**
- Recomputed at Vg = 0.15 V:

  | run | Id(0.15 V) (A/µm) | vs 5 × floor gate (2.3028e-14) | SS_min (mV/dec) |
  |---|---|---|---|
  | run_0012 | 2.3383e-14 | above | 73.2 |
  | B1 | 2.2813e-14 | below | 83.1 |
  | run_0029 (same DOS as B1, mu 18.13) | 2.3386e-14 | above | 73.2 |

  A 2.5 % mobility rescale moves "SS" by 10 mV/dec.
- Two headline statements rest on this metric:
  - "6.3 nm reproduced in SHAPE (SS_min 108 vs 115)";
  - "removing confinement moves SS toward the data" (runs 0013/0017: 151.3 → 138.6).

**2.10 Overclaims in FINAL_STATUS and SUPERVISOR (major).** Recomputed:

| claim | finding |
|---|---|
| "Confinement ... accounts for the measured 0.58 V threshold difference" | Realised confinement is 0.3156 - 0.0234 = 0.292 V, i.e. **50.4 %** of the measured 0.579 V. About 0.11 V of the step is the mobility bias of the constant-current definition (+0.108 V). The model step (0.623 V) overshoots by 44 mV. |
| "It was tested" | The 2/13.2 nm agreement is the design point. The out-of-sample 6.3 nm test failed (-0.294 V). |
| "Without the law the two films would need fixed charges differing by 1.6e12" | Recomputed 1.39e12 cm^-2 (0.248 V). With the law, 6.3 nm needs 1.64e12, so the argument is symmetric. |
| "6.3 nm is reproduced in SHAPE" | SS_min is invalid. The on-state shape fails: run_0014 gap -0.314 V, gm -16.6 %. |
| "The tuned run shows that one electrostatic number is all it misses" | run_0015 also changed mu (12.4 → 11.69) and still misses Vth_lin by -0.349 V and gm by -23.1 %. |
| "+27 % on-current is the consequence of that overdrive error, not of the mobility" | The mobility choice is 24.9 % of the log error (+6.06 % of the +26.8 %). |
| "Subthreshold shapes ... without tuning" | Nt2 and WTA are FITTED (brief §3). |
| "Validation ... nothing tuned" | mu 12.4 is the V0 fit of this curve. |
| "Offsets agreeing to 40 mV" (runs 0001/0002) | +0.3331 vs +0.2866 V, i.e. 46.5 mV. |
| "15 launches" / "all 14 launches" | 52. |
| "Not run: WF, m*, 6.3 nm sensitivities" | Superseded (runs 0030-0036, 0048-0051). |
| "Publication-ready as a ... parameter extraction" | The parameter set is not unique (see (a)). |

**2.11 The fit-quality metric is not comparable across films (major).**
- The active log-RMSE spans differ: 6.57 / 5.25 / 4.59 decades for 2 / 6.3 / 13.2 nm (runs 0012 / 0015 / 0013). So 0.037 / 0.063 / 0.081 dec are not comparable.
- Log-RMSE is also insensitive to on-state errors: run_0015 misses gm by -23 % at 0.063 dec.
- *Satisfy:* report the gap, gm, Ion/gm and fixed-current SS next to the RMSE (S6 §1.6 is the right table).

**2.12 Constant-current Vth is mobility-confounded (major for the Vth(t) narrative).**
- On the measured 13.2 nm curve, giving it the 2 nm mobility moves Vth_cc by +0.1084 V (μ_FE ratio 4.13) to +0.1154 V (ratio 4.45).
- So the "threshold" trend is partly a mobility trend.
- *Satisfy:* use a charge-referenced threshold (e.g. V at fixed n_s from C-V), or report both.

**2.13 Extraction at Vd = 0.7 V (minor).**
- Vth_lin is extrapolated at gm_max although Vd is not ≪ Vov.
- At 2 nm, gm_max falls on the last point (3.00 V, a one-sided difference). So μ_FE(2 nm) = 12.15 is a lower bound, and Vth_lin(2 nm) depends on where the sweep ends.
- The gap metric inherits both effects.

**2.14 Measurement temperature and Cox inputs (minor).**
- The measurement temperature is assumed to be 300 K; it was not recorded.
- ε(Al2O3) = 9.0 is assumed. Varying it over 7-9 moves the EOT by about 3 %, and every q/Cox-derived charge moves with it.
- The HfO2 permittivity 19.57 is labelled "measured", but the method and device are not stated.

**2.15 Pre-registration hygiene (major for how the prediction record is presented).**
- **S1's B0 "prediction" was not pre-registered.** It predicted SS_cc 418, but:
  - `s1_poisson1d.py` was saved at 19:18:00Z, after run_0037 started (19:16:21Z);
  - its output was saved at 19:24:15Z, after the run ended (19:21:30Z).
- **A6 was designed after the 6.3 nm miss was known.** The needed Qf (~-3e11) was pre-computed in the brief, and seven hypotheses were tried. It is "held out" in parameters, not in model selection.
- **The KCL acceptance rule was changed after a failure** (NUMERICAL_CONVERGENCE, check G').
- All three must be presented as post hoc.

**2.16 Qf read as a physical charge (major; S4 §3d).**
- S4 reads Qf's magnitude as donors or an ionized-V_O layer (≈1.7e19 cm^-3 over 1 nm).
- Qf is exactly degenerate with WF and χ (0.100 V rigid; max |Δlog Id| ≤ 1.6e-5), so its magnitude is not a charge measurement.

---

## 3. Adversarial verification of load-bearing claims

Everything was recomputed from raw files; see `scratch/REVIEW/review_verify_out.txt`. For all 30 runs checked (0001-0005, 0007, 0012-0017, 0019, 0029-0040, 0048-0052), the metrics recomputed from `comparison.csv` through the unchanged extractor matched `execution.json` exactly.

| # | claim (source) | my recomputed value | verdict |
|---|---|---|---|
| V1 | A6 misses 6.3 nm Vth_cc by -0.057 V; run_0014 by -0.294 V (S1, S3, S6) | -0.0573 / -0.2941 V | **agree** on the numbers; **disagree** with "A6 favours no-QC" (V11) |
| V2 | B0: SS_cc 410.9, SS_min 141.6, Vth_cc 0.654, Vth_lin 1.856, mu_FE 10.40, Ion -7.6 % (brief §5b, S6) | 410.95 / 141.60 / 0.6543 / 1.8563 / 10.396 / -7.63 %. SS_cc is +115.6 vs measured and +122.1 vs run_0015 | **agree** |
| V3 | Paper's 5.1 / 27.4 = saturation formula on the workbook curves: 5.09 / 27.40; 6.3 nm gives 3.86 (S2, S5) | 5.09 at 1.75 V, 27.40 at 0.95 V, 3.86 at 2.55 V. Robust to unsmoothed finite differences; SG smoothing gives 4.99-5.08 / 25.7-26.4. Ratio 5.387 vs 5.373 | **agree** on the reproduction; **disagree** with S2's "linear regime" and "0.45-0.55 of the true value" (actual 0.419 / 0.352 / 0.546; 13.2 nm peak below Vth_lin) |
| V4 | Floors are flat to ±3 % (6.3, 13.2 nm) and rise ×1432 ∝ t^3.85 (S4) | 4.606e-15 / 1.528e-13 / 6.597e-12; ratio 1432.3 (t^3.851; segments 3.05 / 5.09). 13.2 nm max/min 1.06. 6.3 nm max/min 3.0-3.5 (p10/p90 0.55/1.25) with no trend | **agree** on the ratio and on 13.2 nm; **disagree** on "±3 %" at 6.3 nm |
| V5 | q/Cox = 0.179 V per 1e12; Qf is an exact rigid shift; dEc(2 nm) is exactly degenerate with ~1.7e12 cm^-2 (brief, S3, S6) | 0.17891 V per 1e12. Qf shifts -0.3092…-0.3098 and +0.2936…+0.2942 V across 1e-14..3e-7 A/µm. The confinement package is **not** rigid: 0.3446 → 0.3017 → 0.3109 V; SS_cc 289.1 vs 303.7 | **agree** (Qf); **partially** (dEc + m* is near-, not exactly, degenerate; only pure dEc is exact) |
| V6 | DOS 96/48 → 384/192 gives +2.5 / +1.0 / +0.5 % Ion; p = 2.0; residual +0.16 %; recalibrated mu 17.69 / 11.58 / 61.60 (brief §5b, S6) | +2.476 / +0.947 / +0.496 %; p = 2.03; residual +0.156 %; mu 17.6897 / 11.5820 / 61.6046 | **agree** ("∝ Nt(t)" is only approximate: 1 : 0.38 : 0.20 vs 1 : 0.42 : 0.24) |
| V7 | tmu factor 0.7667 at 358.15 K; P-MTR multipliers ×1.30426 / ×1.19665 (brief §5b, register §2) | (358.15/300)^-1.5 = 0.76663. Exact multipliers 1.30441 / 1.19669. Simulated Ion ratio 0.7742 → P-MTR +0.98 % (6.3: +2.23 %; 13.2: +1.52 %) | **agree** on the factor and physics; **disagree** with the register prose factors (0.012 %); the deckbuild line alone is not proof |
| V8 | 86 % of the model's 2→6.3 nm drop is dEc(2) - dEc(6.3) (S1) | 0.2809 eV / 0.3265 V = 86.0 %. The counterfactual realised difference is 0.2514 V = 77.0 %. Confinement is 50.4 % of the *measured* 2→13.2 step | **agree** arithmetically; the share depends on the decomposition (77-86 %) |
| V9 | SS_min flips 73.2 ↔ 83.1 from a 2.6 % current difference at 0.15 V (S6, brief §5b) | 2.3383e-14 / gate 2.3028e-14 / 2.2813e-14 A/µm; 73.21 vs 83.14; run_0029 gives 73.23 | **agree** |
| V10 | Fixed-current SS 1e-11..1e-10 within 2.3 mV/dec in all films (S6) | measured vs simulated: 2 nm 121.2 vs 123.5; 6.3 nm 124.5 vs 124.8; 13.2 nm **136.1 raw** / 91.8 floor-subtracted vs 91.2 | **agree only with floor subtraction** at 13.2 nm |
| V11 | A6 favours no-QC; the data mildly disfavour confinement (S1, S3) | one-offset rms 0.136 vs 0.133 V; LOO 0.205 vs 0.199; anchor 2 nm 0.221 vs 0.180; anchor 13.2 nm 0.190 vs 0.278 | **disagree**: indistinguishable |
| V12 | Step form wins LOO (×1.11) vs power law (×2.63) (S2) | power law ×2.63 (exponent 0.7516); step ×1.110 with t_c ∈ (6.3, 13.2), ×4.58 with t_c ∈ (2, 6.3) | **agree** on the numbers; **disagree** on their weight (circular) |
| V13 | The CC definition contributes +0.108 / +0.115 V to the 13.2 nm Vth_cc (S1) | +0.1084 / +0.1154 V | **agree** |
| V14 | 13.2 nm isolation ΔIon is -5.0 % (WF) and +5.8 % (m*) vs B3; the brief's -6.8 / +3.7 % are relative to the measurement (S6) | -4.99 / +5.79 % vs run_0040; -6.86 / +3.71 % vs measured | **agree** (S6 is right, the brief is wrong) |
| V15 | A7 mesh check passes: 0.0625 vs 0.0626 dec (brief, S6) | 0.06247 vs 0.06261; ΔVth_cc -0.32 mV; Ion -0.027 % | **agree** |
| V16 | 31.8 nm apparent mu_FE 49.2 ≈ the 13.2 nm plateau (S2) | 49.18 at Vg -0.30 V; four gm maxima; gm(3 V)/gm_max 0.067 | **agree** on the number; **disagree** that it is a mobility |
| V17 | The laws alone offset 2 and 13.2 nm by the same +0.3 V "to 40 mV" (FINAL_STATUS, runs 0001/0002) | +0.3331 / +0.2866 V (46.5 mV) at Qf = 0, mu 16.8 / 57.6, reduced deck | **agree** approximately |
| V18 | run_0014's +27 % Ion is overdrive, "not the mobility" (FINAL_STATUS) | the mobility is 24.9 % of the log error | **partially** |
| V19 | S1's B0 SS_cc of 418 was a prediction (S1; S6 P2 "passed, blind") | code saved 19:18:00Z, output 19:24:15Z; run_0037 ran 19:16:21-19:21:30Z | **disagree**: not pre-registered |

**Not reproduced.** These claims rest on specialist surrogates that I did not re-run. They must be marked as unverified if they reach a paper:
- **S1:** the Gauss-term table and the "≤ 3 mV vs 12 ATLAS runs" surrogate agreement.
- **S2:** the 1-D partition (Nt 2.38 / 2.66 / 0.476e19; mu 19.3 / 19.6 / 62.7).
- **S3:** the Schrödinger-Poisson subband energies and C_eff/Cox.
- **S4:**
  - the trap-DOS inversion ratios (0.81-1.17; ×2.2-2.8);
  - the Ds + g_b decomposition;
  - the 0-D surrogate behind C1.
- **S5:** the Y-function θ and α_H values, and the Rsd bounds.

---

## 4. Over- and under-statements, and contradictions between reports

### 4.1 Contradictions

- **K1. What confinement does.**
  - FINAL_STATUS #1 / SUPERVISOR #1: confinement explains the step and "was tested".
  - S1: the 6.3 nm miss is "an artefact of the confinement law".
  - S3: the data "tolerate, do not require, mildly disfavour" confinement.
  - S6 #5: "physically ASM".

  V11 shows the Vth data are neutral, so neither direction is supported.
- **K2. S1 and S3 cannot both be adopted.**
  - S1 favours the no-confinement reading.
  - S3 rates film confinement at 2 nm "strongly supported" (0.26-0.30 V).

  If S3 is right, S1's reading needs an unexplained, 2 nm-specific ~+1.5-1.7e12 cm^-2 (S3 §3 says so itself). That is again one device-specific parameter, now at 2 nm.
- **K3. S2 still rates as "strongly supported" two claims that B0 undercut:**
  - that the non-monotonic mu_band is an Nt-law artefact;
  - "flat 19.3 / 19.6 then ×3.2".

  B0 reproduced the on-state but broke SS_cc (+116 mV/dec), and S6 marks S2's re-partition FAIL. S2 was written at 19:04Z, before B0, and has not been updated.
- **K4. SS_min: physics or artefact?** S4 §2 treats the SS_min change on removing confinement as physics ("another way of shifting the tail-to-deep-state balance") and uses it to explain run_0012's 73 vs 84.5. S3 and S6 show it is a window artefact, and I confirmed this (V9).
- **K5. Where the μ_sat peaks sit.**
  - S2 says the 2 nm peak is in the linear regime.
  - S5 says the 2 and 13.2 nm peaks sit at "trap-filling onset", and the 6.3 nm peak at "Vov ≈ 1.1 V".
  - Recomputed, the 6.3 nm Vov is 1.91 V relative to Vth_cc and 0.73 V relative to Vth_lin. Neither is 1.1 V.
  - S2 calls the reproduction "validation-class"; S6 calls it a "retrodiction". It is provenance evidence.
- **K6. Near-Ec agreement.**
  - S4 says "near Ec, the V1 tail reproduces all three films".
  - S6 §1.6 finds the model too soft in the 1e-10..1e-9 window by +20 / +6 / +25 mV/dec.
  - S4 itself finds ×2.2-2.8 missing deep states.
- **K7. Stale S1 text.**
  - S1 §3.1 says A7 is "NOT DETERMINED", but run_0036 finished at 19:16:11Z, before S1 was saved at 19:33:37Z.
  - S1 also registers as a "prediction" a number it computed after the run (V19).
- **K8. The brief's 13.2 nm numbers are wrong.**
  - EVIDENCE_BRIEF §4 gives the 13.2 nm no-confinement Qf as ~1.86e12 and §5b gives the isolation ΔIon values. Both are wrong.
  - S1, S4 and S6 are right: 1.434e12 recomputed, and -4.99 / +5.79 %.
- **K9. "Numerics are closed".** S6's bottom line 1 conflicts with S6's own caveats:
  - DOS convergence at 300 K only;
  - no ID-VD mesh check;
  - no DOS-resolution check for the C1 band;
  - a V0-only mesh check at 2 nm.
- **K10. Selective use of 31.8 nm.** FINAL_STATUS excludes 31.8 nm, while S1, S2 and S4 use it as supporting evidence.

### 4.2 Overstated

- **O1. S2 §5.** Two phrases go too far:
  - "does not need to be resolved with the lab";
  - "constants ... confirmed to three significant figures".

  Vd is not confirmed. The paper's SS (60-70 mV/dec) and Nt ratio (×4 vs PBS ×15.6) are not reproducible from the same devices.
- **O2. S3's "exact" degeneracy.** It is near-degenerate: the Nc part gives 43 mV and 14.6 mV/dec (V5).
- **O3. S1's "demonstrated, 86 %".** This depends on the decomposition; the counterfactual gives 77 %.
- **O4. S4's "flat to ±3 %".** Not true at 6.3 nm.
- **O5. S4 §3d.** "Its magnitude does [represent donors]" (see 2.16).
- **O6. S6 P2 "passed (blind)", and "pre-registered held-out test A6" (S3/S6).** Both are post hoc (2.15).
- **O7. S6 "within 2.3 mV/dec for all three films".** This holds only with floor subtraction at 13.2 nm.
- **O8. S2 "the step form wins every leave-one-out test".** The test is circular (V12).
- **O9. S2's structural-transition support.** It leans on the 31.8 nm "mu_FE" (V16).

### 4.3 Understated

- **U1. The on-state shape also misses at 2 nm** (gap -0.145 V, gm -8.6 %). It is hidden by the 0.037 dec RMSE.
- **U2. RMSE spans differ between films** by up to 2 decades.
- **U3. The "validation" mobility 12.4 is a fit to the same curve.** S6 calls its origin "undocumented"; it is in fact documented as the V0 fit.
- **U4. The Nt(t) exponent inherits the paper's misapplied saturation-formula mobilities.**
- **U5. The runner does not gate on ATLAS geometry warnings** (run_0027 was accepted).
- **U6. The KCL rule was changed after a failure.**
- **U7. The registered ID-VD predictions cannot discriminate the thickness mechanisms.** They test contact ideality only (Id(0.1)/Id(0.05) of 1.80-1.98 is generic for a long-channel Ohmic device).

---

## 5. Wording I would require in the author documents

- **FINAL_STATUS #1.** Replace it with:

  > "With the DFT-proxy confinement law, one shared offset brings 2 and 13.2 nm within 30 mV and misses 6.3 nm by 0.29 V; without it, one offset fitted on 2 nm brings 6.3 nm within 60 mV and misses 13.2 nm by 0.25 V. The three thresholds do not discriminate the two readings (one-offset rms 0.136 vs 0.133 V). Confinement is an assumed input, not a result."

- **The 6.3 nm "validation".** Describe it as:

  > "an out-of-sample test of the threshold (mobility from an earlier fit of the same curve), which failed by -0.29 V; the on-state shape (gap -0.31 V, gm -17 %) is also not reproduced."

- **SS.** Replace SS_min everywhere by V(1e-9), SS over 1e-11..1e-10 and over 1e-10..1e-9, SS_cc, the gap and Ion/gm. State the floor-subtraction choice.
- **Contacts.** Retract the run_0027 row and "contact geometry irrelevant".
- **Temperature.** Always give both variants, and state that tmu = 1.5 was an unplanned silicon default.
- **Data.** State:

  > "one device per thickness; drain bias and current normalisation from the device schematic; sweep direction, hysteresis, temperature and gate current not recorded; 31.8 nm not reproduced by the model."

---

## 6. What would change my recommendation

In order of cost:

1. **Retrieve Januar SI data that already exist.**
   - Fig. S12 (2 nm at 338/358 K): test ΔVth_lin (-17 / -27 mV, the same in both variants), ΔVth_cc and ΔIon against the hash-locked register.
   - The Fig. 5a 6.3 nm μ_sat, registered as 3.86.
2. **Measurement records:** Vd, sweep direction and rate, dwell, IG/IS, instrument ranges.
3. **3-5 replicate devices** at 2, 6.3 and 13.2 nm.
4. **Output and contact data:** ID-VD, low-Vd transfer curves (0.05-0.1 V), and TLM or an L-series.
5. **Per-thickness characterisation:** C-V (quasi-static and multi-frequency), optical gap and XRR thickness for each film.
6. **At least 2 more thicknesses** in 3-5 nm and 8-11 nm, predicted before they are measured.

Items 1-2 alone would support a calibration paper with no mechanism claim. A mechanism claim needs at least items 3 and 5.

---

## Appendix: reproduction

- **Script:** `analysis_2026-09-25/scratch/REVIEW/review_verify.py`. Run it with `..\IWO_ATLAS_Model_claude\.venv\Scripts\python.exe` from the package root. It reads only, and it imports `scripts/extract_metrics.py` unchanged.
- **Output:** `analysis_2026-09-25/scratch/REVIEW/review_verify_out.txt`. Its sections map to the table in section 3:

  | output section | content |
  |---|---|
  | V1-V2 | run metrics |
  | V3 | μ_sat reproduction |
  | V4 | off-state floors |
  | V5 | rigid shifts |
  | V6 | DOS convergence |
  | V7 | tmu |
  | V8 | decomposition |
  | V9 | SS_min |
  | V10 | fixed-current SS |
  | V11 | one-offset stories |
  | V12 | leave-one-out |
  | V13 | CC-definition effect |
  | V14 | 31.8 nm |
  | V15 | isolation runs |
  | V16 | A7 mesh and RMSE spans |
  | V17 | paper SS claim |
  | V18 | Ion-error share |
  | V19 | analytic checks |

- **Checked by hand, not by the script:**
  - the file timestamps in 2.15 (`LastWriteTimeUtc`);
  - the run_0027 `device.in` / `deckbuild.out` inspection (x.mesh ends at 24 µm; 3 × "Electrode shortened");
  - the warning survey over all 51 deckbuild.out files;
  - `run_0045/deckbuild.out` l.384-423.
