# S2: Carrier transport, mobility and thickness laws (IWO 2 to 13.2 nm)

Scope: band mobility vs field-effect mobility, trap-limited conduction, percolation and crystallinity, roughness and Coulomb scattering, whether the thickness laws have a physical origin, and what to expect from temperature measurements. No ATLAS runs were launched for this report. The Python scripts and their outputs are in `analysis_2026-09-25/scratch/S2/`:
- `s2_part1_curves.py`: curve features, mobility decomposition, Jacobian, law-form tests;
- `s2_part2_mtr_temperature.py`: a 1-D Poisson surrogate, 350 K expectations, Coulomb and roughness estimates;
- `s2_part3_repartition.py`: a trap/mobility partition consistent with the curve shape;
- `s2_part4_musat_location.py`: the paper's mobility definition.

Each script writes a matching `*_out.txt` file.

Terms used throughout:
- **gap** = Vth_lin minus Vth_cc (turn-on delay). A Qf change shifts the whole curve rigidly, and mu_band only rescales the current, so neither changes the gap. It is set by trapping.
- **Partition factor P** = mu_FE / mun, where mun = mu_band x (1 - Dsr/t)^2 is the mobility actually entered in the ATLAS deck.
- **LOO** = leave-one-out.

**1-D surrogate (my tool, not a physics claim).** This is a 1-D Poisson model of a floating film:
- Fermi-Dirac electrons, the V1 acceptor tail, Nd_eff, Qf, TiN work function 4.70 eV and chi(t);
- the gradual-channel approximation at Vd = 0.7 V, which is exact in 1-D for a floating body because n(Vg, V) = n(Vg - V, 0).

With the V1 parameters it reproduces ATLAS as follows (part 2):

| run | mu_FE, 1-D vs ATLAS | Vth, 1-D vs ATLAS |
|---|---|---|
| 0012 | 11.56 vs 11.27 | 10 to 15 mV difference |
| 0015 | 8.48 vs 8.42 | 10 to 15 mV difference |
| 0013 | 49.44 vs 48.95 | 10 to 15 mV difference |
| 0023 (Nt x1.5) | 11.00 vs 10.50 | Vth_lin +41 mV |

It is not valid for SS, because the interface and deep Gaussians are omitted: SS_min is 64 vs 73 mV/dec at 2 nm and 67 vs 111 at 6.3 nm.

---
## 0. Bottom line

1. **The ×4.6 mobility step from 6.3 to 13.2 nm is not explained by the model. It is parametrised.**
   - In the calibrated runs, mu_FE = mu_band × R(t) × P.
   - 109 % of ln(50.17/10.95) is carried by the fitted mu_band. The roughness factor contributes 3 %, the free/trapped partition 3 %, and the model residual −16 %.
   - The Nt(t) law changes the partition factor P at gm_max by only 0.79 to 0.85 across all films.
2. **Three thickness-dependent mechanisms are rejected by order-of-magnitude arguments as the origin of the step:**
   - Trap partition: it would need Nt ×6.7e3.
   - Roughness (1 − Dsr/t)^2: it gives ×1.05.
   - Thickness-fluctuation roughness (mu ∝ t^6) and back-surface Coulomb scattering are both steeply monotonic in t. They cannot give mu(2 nm) ≈ mu(6.3 nm) and a step after 6.3 nm; each misses by a factor of 700 to 2700.
3. **The non-monotonic mu_band (6.3 < 2 nm) is most likely an artifact of the imposed Nt law.**
   - The tuned 6.3 nm run misses the gap by −0.36 V and gm_max by −23 %.
   - Five electrostatic hypotheses (campaign A, runs 0030 to 0034) leave gm_max unchanged within ±2 %.
   - A partition consistent with the curve shape gives mu_band = 19.3 / 19.6 / 62.7 and Nt = 2.4e19 / 2.7e19 / 4.8e18 cm^-3. Ion, which was not fitted, lands within −2.6 / −7.9 / +0.1 %.
   - The simplest reading is two material regimes: films of 6.3 nm or less behave alike, and 13.2 nm is different.
4. **A structural transition between 6.3 and 13.2 nm is the most defensible explanation, but it is unverified.**
   - The candidates are the onset of (poly)crystallinity, grain coalescence, or the end of percolation.
   - It is favoured by leave-one-out tests (a step form misses the held-out 6.3 nm point by only 1.03 to 1.26×, while smooth forms miss by 1.9 to 6.4×).
   - It is also favoured by the co-located Vth step and by the 31.8 nm apparent mu_FE of 49.2, which is equal to 50.2 at 13.2 nm.
   - No structural data at 6.3 or 13.2 nm are available locally.
5. **No metric power law survives.**
   - The dEc ∝ t^-1.38 extrapolation exceeds the infinite-well effective-mass upper bound for t > 3.0 nm.
   - Nt ∝ t^-0.75 cannot be distinguished from a surface + bulk form with 2 points. Moreover, the source paper itself implies exponents of 0.73 and 1.71.
6. **The paper's 5.1 and 27.4 are reproduced exactly (5.09 and 27.40).** They come from the saturation formula, 2L/(W·Cox)·(∂√Id/∂Vg)², applied to these same Vd = 0.7 V workbook curves. The discrepancy is therefore explained; it does not need to be resolved with the lab.

---
## 1. Decomposition of mu_FE (Task 1)

### 1.1 Numbers
Sources: `s2_part1_out.txt` §B; runs 0012, 0015 and 0013 (execution.json and comparison.csv); the decks give mun = 13.30, 10.65 and 59.24.

| t (nm) | mu_FE measured | mu_band (fit) | R=(1-0.287/t)^2 | P = mu_FE,sim/mun | mu_FE,sim | measured/sim |
|---|---|---|---|---|---|---|
| 2.0 | 12.15 | 18.13 | 0.734 | 0.847 | 11.27 | 1.078 |
| 6.3 | 10.95 | 11.69 | 0.911 | 0.791 | 8.42 | 1.300 |
| 13.2 | 50.17 | 61.9 | 0.957 | 0.826 | 48.95 | 1.025 |

Split of ln(ratio), in the order band / roughness / partition / residual:

| step | total | band | roughness | partition | residual |
|---|---|---|---|---|---|
| 6.3→13.2 nm | ×4.58 | +109 % | +3 % | +3 % | −16 % |
| 2→13.2 nm | ×4.13 | +87 % | +19 % | −2 % | −4 % |

The free fraction at Vg = 3 V is 0.68 / 0.67 / 0.76 in the 1-D surrogate, with n_trap ≈ 4.0 / 4.2 / 3.4e12 cm^-2 (part 2 §1). Because the trapped sheet charge is nearly the same in every film, the partition cannot carry a thickness step.

Additional observations:
- The measured gm peaks at the end of the sweep for 2 nm (Vg = 3.00 V). The 2 nm "peak" mu_FE of 12.15 is therefore a lower bound.
- The gm roll-off gm(3 V)/gm_max is 1.000 / 0.981 / 0.978. That is at most 2.2 % from series resistance or theta_r degradation.

### 1.2 The mu_band vs Nt degeneracy
The Jacobian at 2 nm (run_0012 → run_0023, per unit ln Nt; part 1 §C) is:
- dVth_cc = +0.202 V
- dgap = +0.495 V
- dln gm_max = −0.173
- dln Ion = −0.711

Ion is dominated by the threshold. It responds four times more strongly to Nt than gm does, and mu enters Ion linearly. So on Ion alone, Nt ×1.5 is exactly compensated by mu ×1.33; this is the degeneracy seen in run_0023.

Which features break the degeneracy:
- **The gap** depends on Nt only. It is blind to both Qf and mu.
- **gm_max** tracks mu (and depends weakly on Nt).
- **Vth_cc** fixes Qf once Nt is known.

Three features against three parameters (Qf, Nt, mu) is identifiable in principle. However, the gap is also produced by:
- WTA (the tail width),
- the interface-acceptor Dit,
- deep states,
- energy-distributed back-surface acceptors.

These trade off against Nt (see §6).

### 1.3 Is a non-monotonic band mobility credible?
It is not credible as physics, and there is evidence that it is a fitting artifact.

The tuned run_0015 matches Vth_cc and Ion but has:
- a gap of 0.820 V vs 1.176 V measured;
- gm_max −23 % (Ion/gm_max = 1.53 V vs 1.18 V).

The measured 6.3 nm curve turns on later and more steeply than the model. That signature means more trapped charge between Vth_cc and Vth_lin, together with a higher band mobility.

Campaign A tested five electrostatic mechanisms at mu_band 12.4, one at a time relative to run_0014 (gm 2.860e-7, gap 0.862):

| hypothesis | run | gm (A/V/um) | gap (V) |
|---|---|---|---|
| back charge −1.64e12 | 0030 | 2.799e-7 | 0.724 |
| t = 5.3 nm | 0031 | 2.810e-7 | 0.879 |
| Nd0 1e16 | 0032 | 2.831e-7 | 0.847 |
| Dit ×5 | 0033 | 2.850e-7 | 0.857 |
| no confinement | 0034 | 2.798e-7 | 0.839 |

None moves gm by more than 2 %, and none opens the gap toward 1.176 V. A fixed back charge actually *closes* the gap. The on-state shape is therefore a transport and trapping feature, not an electrostatic one.

I then fitted a partition that is consistent with the curve shape, using the surrogate (part 3). For each film I set Nt from the measured gap, mu_band from gm_max and Qf from Vth_cc; Ion was not fitted and serves as a check:

| t | Nt factor vs V1 law | Nt (cm^-3) | mu_band | Qf (cm^-2) | Vth_lin sim/meas | Ion (not fitted) |
|---|---|---|---|---|---|---|
| 2.0 | 1.19 | 2.38e19 | 19.3 | 1.89e12 | 1.665/1.663 | −2.6 % |
| 6.3 | 3.15 | 2.66e19 | 19.6 | 9.8e11 | 1.881/1.820 | −7.9 % |
| 13.2 | 0.98 | 4.76e18 | 62.7 | 1.46e12 | 1.041/1.044 | +0.1 % |

With this partition, mu_band is flat from 2 to 6.3 nm (19.3 → 19.6) and then steps ×3.2. Nt(6.3) ≈ Nt(2), so the t^-0.75 law is off by ×3 at 6.3 nm.

**Prediction registered for S6 (made before any ATLAS test).** Run 6.3 nm with:
- NTA = 6.66e20 cm^-3 eV^-1 (Nt 2.66e19), WTA 0.040;
- mu_band 19.6 (mun 17.9);
- Qf 9.8e11.

It should give Vth_cc 0.64 ± 0.03 V, Vth_lin 1.82 to 1.90 V, mu_FE 10.5 to 11.0 and Ion −5 to −10 %. SS_min should rise a few to about 15 mV/dec above the value in run_0015; this is a risk to the hypothesis if the measured 114.7 is exceeded by a large margin.

If the prediction holds, the device-specific 6.3 nm Qf offset shrinks from 0.29 V to about 0.10 to 0.16 V (this couples to S1).

Evidence class: calibration (same curve), with one internal check (Ion).

---
## 2. Mechanisms for the ×4.6 step between 6.3 and 13.2 nm (Task 2)

Requirement: at 300 K, ln 4.6 = 1.52. With Matthiessen's rule and a 13.2 nm mobility of about 62, an extra scattering channel present only in the thinner films would need mu_x(6.3) ≈ 17 cm²/Vs, while leaving mu(2) ≈ mu(6.3).

| mechanism | expected t-dependence | magnitude for 6.3→13.2 | result |
|---|---|---|---|
| Trap-limited partition (Januar Eq. 5) | through Nt(t) and EF pinning | P changes 0.791→0.826 (+4 %). Linearised, ×4.6 needs Nt ×6.7e3 | **rejected** as primary; falls short by ×30 in ln |
| Roughness factor (1−Dsr/t)^2, Dsr 0.287 nm | about 1 − 2Dsr/t | ×1.051 (13.2/6.3); ×1.305 (13.2/2) | **rejected**; 3 % of the needed ln |
| Thickness-fluctuation roughness (Sakaki/Uchida, mu_SR ∝ t^6) | dE1 = 2E1·Δ/t: 105 / 3.96 / 0.44 meV | if mu_SR(6.3) = 17 then mu_SR(2) = 0.017 cm²/Vs, vs about 12 to 19 extracted | **rejected**; contradicted ×700 at 2 nm |
| Coulomb, front fixed charge Qf 1.73e12 at d = 0 (screened 2DEG, zero-thickness upper bound on scattering) | none; same interface for every film | mu_C = 283 (n_s 3e12) to 515 (1e13) cm²/Vs | **rejected** as the step. At most a 10 to 20 % contribution at 13.2 nm, equal in all films |
| Coulomb, back-surface sheet 1.64e12 (A3 value), eps_bar 5.15 | ∝ (2k_F·d)^3 | mu_C = 1.4e3 / 4.7e4 / 4.5e5 at 2 / 6.3 / 13.2 nm | **rejected**; ×2700 short at 6.3 nm and monotonic |
| Coulomb from trapped tail electrons (about 4e12 cm^-2 in the channel) | same n_trap in all films (§1.1) | about 120 cm²/Vs (scales as 1/N from the Qf case) | not a step |
| Remote HfO2 phonons through 2 nm Al2O3 | carriers sit at the same interface in accumulation in every film | first order independent of t | **rejected** as the step; magnitude NOT DETERMINED (no local data) |
| Series R / contacts (S5) | would cut gm more in the high-current 13.2 nm film | measured roll-off ≤ 2.2 % | cannot create ×4.6; if present, it *understates* mu(13.2) |
| Fringing current from an unpatterned channel | grows with film conductance | W/L = 14.5 gives about a 10 % order effect | cannot give ×4.6; channel patterning NOT DETERMINED |
| Structural transition: amorphous or nanocrystalline to polycrystalline, grain-boundary (Seto) barriers, or percolation (Kamiya/Nomura) | step at a critical thickness t_c, then a plateau | a barrier difference of kT·ln 4.6 = 39 meV is enough | **plausible, unverified** |

Supporting evidence for the structural transition:
- **Januar2026 p.2 to 3.** HRTEM shows the ultrathin channels "lack long-range crystallinity"; plan-view SEM shows nanoscale grains whose size depends on thickness (SI Fig. S4b, not bundled); AFM RMS roughness is higher at 2 nm than at 10 nm. The paper also states that annealing above 150 °C increases mobility and carrier concentration through crystallinity (SI Figs. S7 and S8).
- **Si2021.** The degree of crystallinity decreases as film thickness drops to 2 to 3 nm in certain oxides, and ALD In2O3 at 0.7 to 1.5 nm is amorphous.
- **Lin2022.** Annealed ALD In2O3 is polycrystalline, and DFT indicates polycrystalline mobility is comparable to single-crystal mobility.
- **Correlation within this data set:**
  - the step form wins every leave-one-out test (§3);
  - Vth drops by 0.58 V and the off-state floor rises ×44 at the same thickness interval, consistent with Januar's link between crystallinity and higher carrier concentration (couples to S1 and S4);
  - the always-on 31.8 nm film has apparent mu_FE 49.2 (gm_max at Vg = −0.3 V; part 1 §A), a plateau rather than a continued rise.

Contradicting or weakening evidence:
- There are no structural data at 6.3 or 13.2 nm.
- Kim2024 is a different IWO process (SiO2 gate). Its mu_FE of 8.1 / 11.8 / 10 at 10 / 20 / 30 nm shows no step, and its RMS roughness *increases* with thickness (0.134 / 0.199 / 0.258 nm).
- There is one device per thickness, so device-to-device spread is unknown.
- Discriminating predictions are in §4 (temperature) and §7.

---
## 3. Power laws (Task 3)

Fits are on the three thin films. Two-parameter forms leave one degree of freedom; the step form has two levels plus t_c somewhere in 6.3 to 13.2 nm. The LOO column fits the form on 2 and 13.2 nm and predicts 6.3 nm. Source: `s2_part1_out.txt` §D.

| metric | power law: rms rel. residual / LOO | A+B/t | a·exp(bt) | linear | step: rms / LOO |
|---|---|---|---|---|---|
| mu_FE | 0.56 / ×2.63 | 1.03 / ×3.90 | 0.34 / ×1.91 | 0.63 / ×2.44 | 0.043 / ×1.11 |
| Ion | 0.85 / ×3.76 | 1.87 / ×6.37 | 0.53 / ×2.52 | 1.14 / ×3.70 | 0.096 / ×1.26 |
| Vth_cc | 0.54 / ×0.29 | 1.52 / ×0.30 | 0.34 / ×0.46 | 0.39 / ×0.68 | 0.011 / ×1.03 |
| Vth_lin | 0.17 / ×0.69 | 0.21 / ×0.64 | 0.12 / ×0.76 | 0.11 / ×0.78 | 0.037 / ×0.91 |
| mu_band (V1 fit) | 0.73 / ×3.27 | 1.24 / ×4.56 | 0.52 / ×2.49 | 0.81 / ×2.99 | 0.19 / ×1.55 (×1.02 after the §1.3 partition) |

A held-out check with the 31.8 nm film (context only): an Ion power law through 6.3 and 13.2 nm (exponent 2.74) predicts 3.4e-5 A/um at 31.8 nm. The measured value is 3.59e-6 (×9.6 lower), and the prediction also exceeds the series-resistance ceiling of 0.7 V / 9e4 Ω·um = 7.8e-6.

Mu_FE and Ion are non-monotonic, so no monotonic two-parameter law can fit them. **No metric follows a power law in t.** With three points, "step at t_c" is favoured but not proven. Distinguishing a step from a steep sigmoid needs at least 3 thicknesses between 6.3 and 13.2 nm and at least 5 devices each; at present the spread is unknown.

The V1 model's own laws:

**dEc = 0.9205 t^-1.3815**
- This is a local slope over 0.95 to 1.98 nm PBE slabs.
- The infinite-barrier parabolic effective-mass estimate, E1 = 0.376/(m*·t²) eV·nm², is an upper bound for a parabolic band; finite barriers and non-parabolicity only lower it.
- The law exceeds that bound for t > 2.98 nm: 72 vs 45 meV at 6.3 nm (×1.59) and 26 vs 10 meV at 13.2 nm (×2.51). Its exponent should tend to −2.
- The extrapolation to 6.3 to 13.2 nm is non-physical. The effect on Vth is small (27 and 16 mV), so this is S3's lane.
- Confinement barely touches transport: run_0016 vs 0012 changes gm by +0.6 % and the gap by +17 mV.

**m* − 0.208 ∝ t^-1.41**
- This exponent matches the dEc exponent, as expected from conduction-band non-parabolicity, where m* rises with electron energy. Stokey2021 (§I) reports m* from 0.18 at low density to about 0.44 at 1e21 cm^-3 (Feneberg, cited there).
- So there is a physical origin, but only four PBE points support it, and the law enters only Nc.
- V1 does not carry m*(t) into mobility (Drude mu = eτ/m*). At fixed τ this would be −18 % at 2 nm, and that effect is hidden inside the fitted mu_band.

**Nt ∝ t^-0.75**
- A surface + bulk form through the same two anchors, Nt = 2.15e18 cm^-3 + 3.57e12 cm^-2/t, gives 7.8e18 at 6.3 nm vs 8.5e18 from the power law. The data cannot tell them apart.
- The source is internally inconsistent: Januar Sec. 2.8 ("×4, 13.2 → 2 nm") implies an exponent of 0.73, while its PBS devices (5.3e19 at 2 nm, 3.39e18 at 10 nm; p.9) imply 1.71.
- The §1.3 partition finds Nt(6.3) ≈ Nt(2), which breaks any monotonic law.
- Verdict: this is empirical interpolation.

---
## 4. Temperature (Task 4): analytic expectations for 300 → 350 K
Constant used below: 1/kT(300 K) − 1/kT(350 K) = 5.525 eV^-1.

**(a) Trap-limited conduction (MTR)**

Assumptions: V1 tail (WTA 40 meV, Tt = 464 K), T-independent mu_band, Nc ∝ T^1.5, Eg independent of T. These are the same assumptions as campaign B.

Computed in the 1-D surrogate (part 2 §3):

| quantity at 350 K | 2 nm | 13.2 nm |
|---|---|---|
| mu_FE | ×0.993 | ×0.999 |
| Ion | ×1.004 | ×1.011 |
| ΔVth_cc | −64 mV | −66 mV |
| ΔVth_lin | −15 mV | −24 mV |

Apparent activation energy of Id at fixed Vg:

| Vg | 2 nm | 13.2 nm |
|---|---|---|
| 0 V | 504 meV | 156 meV |
| 0.5 V | 120 meV | 61 meV |
| 1.0 V | 56 meV | 20 meV |
| 1.5 V | 23 meV | 8 meV |
| 2.0 V | 7 meV | 4 meV |
| 3.0 V | 1 meV | 2 meV |

Ea follows (Ec − EF) at the surface in subthreshold and falls to about 0 once EF enters the band. At equal Vg the 2 nm film shows the larger activation. At equal overdrive the two films are similar (about 20 meV at Vth_lin).

The MTR signature is a threshold shift with an on-state mobility that is flat in T.

**(b) Percolation or potential barriers (Kamiya type)**

mu ∝ exp[−(φ_m − σ²/2kT)/kT]. Over φ_m = 20 to 60 meV and σ = 0 to 20 meV, mu(350)/mu(300) = 1.03 to 1.39 (Ea 6 to 60 meV). The activation persists above threshold and decreases slowly with n. An Arrhenius plot is curved (ln mu is linear in 1/T²).

If the ×4.6 step is a 39 meV grain-boundary barrier difference, the disordered films gain ×1.24 more than 13.2 nm. The ratio mu_FE(13.2)/mu_FE(2) would then fall from 4.13 to about 3.3.

**(c) Phonon-limited transport**

mu ∝ T^-1 to T^-2 gives ×0.857 to ×0.735, scaled by the phonon fraction of 1/mu. The phonon-limited mobility of In2O3 or IWO is NOT DETERMINED locally.

If 13.2 nm is band-like and partly phonon-limited while 2 nm is barrier-limited, the ratio falls to about 2.7 to 3.3.

**The discriminating measurement**

Measure mu_FE at Vg = 3 V at 350 K:
- about 0 % change → MTR only (V1 and campaign B);
- +3 to +40 % → percolation or barriers;
- negative → phonons.

Then compare the mu_FE(13.2)/mu_FE(2) ratio: constant under MTR, shrinking under a structural or percolation step.

The 13.2 nm film decides the sign of dmu/dT (band vs barrier). The 2 nm film decides MTR vs percolation, because it has the larger activation at fixed Vg under both.

Januar SI Fig. S12 already contains 2 nm transfer curves at 65 °C and 85 °C (338 and 358 K; paper p.8 and SI caption). These existing lab data can test (a) against (b) immediately.

---
## 5. Paper 5.1 / 27.4 vs workbook 12.1 / 50.2 (Task 5)

The main text of Januar does not state the extraction (no Vd, W/L or formula). The SI is not bundled.

Applying the saturation formula mu_sat = 2L/(W·Cox)·(∂√Id/∂Vg)² to the workbook Vd = 0.7 V curves, with the same Cox (8.955e-7), L/W and units, gives (part 1 §A, part 4):

| film | mu_sat peak | peak at Vg | paper |
|---|---|---|---|
| 2 nm | 5.09 | 1.75 V | 5.1 |
| 13.2 nm | 27.40 | 0.95 V | 27.4 |
| 6.3 nm | 3.86 | — | not quoted |

The ratio 13.2/2 is 5.39, vs 5.37 in the paper. Two other definitions do not reproduce the paper:
- a thickness-dependent series capacitance moves mu the wrong way (14.8 / 122);
- Id/(Cox·Vov·Vd) gives 16.1 / 73.1.

Conclusions:
1. The paper's devices and the workbook devices are the same. The constants Cox, W/L = 290/20 and A/um are confirmed to three significant figures. This is **validation-class** evidence, because it reproduces independent published numbers.
2. The paper's values are a saturation formula applied where Vg − Vth (about 1.1 V at the 2 nm peak) is larger than Vd = 0.7 V. The device is in the linear regime there, so the formula gives about Vd/(2Vov − Vd) × mu, roughly 0.45 to 0.55 of the true value. This explains the thickness-dependent ratio of 2.4× vs 1.8×.
3. The linear-regime mu_FE of 12.1 / 11.0 / 50.2 is the appropriate apparent mobility. It is still an apparent value, because Vd/Vov is not small and the 2 nm peak is not reached.
4. Januar's μmax–Nt correlation (Fig. 5a) is built on saturation-formula values.

---
## 6. Couplings and identifiability

| parameters that trade off on one ID-VG curve | curve feature | experiment that breaks it |
|---|---|---|
| mu_band ↔ Nt | Ion | gap + gm_max (partial, with WTA and Dit fixed); split C-V or gated Hall giving n_total(Vg) and n_free(Vg) (full) |
| Nt ↔ WTA ↔ interface Dit ↔ deep states ↔ energy-distributed back-surface acceptors (S4, S1) | gap, SS | T-dependence (Tt enters as T/Tt); C-V frequency dispersion; passivated vs bare back-surface splits |
| Qf ↔ gate work function ↔ chi ↔ dEc (S1, S3) | Vth_cc | C-V flat-band; IPE/UPS |
| mu_band ↔ R(t) ↔ Rc ↔ W_eff (S5) | gm_max | TLM (Rc); channel-isolation check; Hall mobility |
| band vs barrier-limited mu | not separable at one T | T sweep (§4) |

Couplings to the other specialists:
- **S1.** The 6.3 nm anomaly has two components:
  - a rigid part (Qf about 1e12 vs 1.5 to 1.9e12, roughly 0.10 to 0.16 V) that stays S1's;
  - a shape part (gap +0.36 V, gm −23 %) that is a trap/mobility partition issue. It is not electrostatic, since campaign A leaves gm unchanged.
- **S3.** Confinement is not a transport mechanism in V1: gm changes < 1 % in runs 0016 and 0017. The dEc extrapolation above 3 nm is non-physical.
- **S4.** The §1.3 partition needs Nt(6.3) ≈ Nt(2) ≈ 2.5e19 with WTA fixed. A wider tail at 6.3 nm is the competing reading, and SS must decide between them (the surrogate is not valid for SS).
- **S5.** The measured roll-off limits Rc effects to a few %. If Rc is present, mu_band(13.2) is underestimated and the step is larger.
- **S6.** Two items to register:
  - the §1.3 run;
  - campaign B at 350 K, which should reproduce §4(a): ΔVth_cc ≈ −65 mV and |Δmu_FE| < 1 %. A mismatch would indicate a surrogate or ATLAS numerical issue, not physics.

---
## 7. Measurements needed

1. **Temperature series.** Transfer curves at ≥ 4 temperatures from 300 to 360 K for 2, 6.3 and 13.2 nm, plus the existing 2 nm 338/358 K data (Januar Fig. S12). This decides MTR vs barrier vs phonon transport, and whether the thickness ratio shrinks with T.
2. **Structure.** GIXRD, HRTEM/SAED and SEM grain size at 6.3, about 8, about 10, about 11.5 and 13.2 nm. This locates t_c and tests the crystallinity step.
3. **Hall effect (van der Pauw, ideally gated) on each film.** This gives mu_Hall and n_Hall vs mu_FE, which separates band mobility from the trap partition. Lin2022 did this on 2.5 nm In2O3, getting 48.2 cm²/Vs.
4. **Split C-V (or C-V with frequency).** n_total(Vg) closes the mu–Nt degeneracy.
5. **More thicknesses and replicates.** At least 3 thicknesses between 6.3 and 13.2 nm, with at least 5 devices per thickness. This separates step vs sigmoid vs power law and quantifies spread.
6. **Low-Vd curves and ID-VD, plus TLM.** Transfer curves at Vd = 0.05 to 0.1 V give a proper linear mu_FE, and ID-VD with TLM gives Rc (S5).

---
## 8. Verdicts

| mechanism / claim | verdict | evidence class | key number |
|---|---|---|---|
| Paper 5.1/27.4 = saturation formula on the same curves | demonstrated | validation | 5.09 / 27.40 reproduced |
| mu_FE thickness dependence carried by the fitted mu_band | demonstrated (model-internal) | calibration | 109 % of ln(×4.58), 6.3→13.2 |
| Trap partition (Januar Eq. 5) as primary cause of the step | rejected | calibration | needs Nt ×6.7e3; P changes by 4 % |
| Roughness factor (1−Dsr/t)^2 | rejected (as the step) | calibration | ×1.05 (6.3→13.2) |
| Thickness-fluctuation roughness (∝ t^6) | rejected | correlation | ×700 contradiction at 2 nm |
| Coulomb (front Qf, back surface, trapped charge) | rejected (as the step) | calibration | mu_C 283 to 515 (front), 4.7e4 (back, 6.3 nm) |
| Remote phonons | rejected (as the step) | none | independent of t to first order |
| Non-monotonic mu_band is an Nt-law partition artifact | strongly supported | calibration | 6.3 nm gap −0.36 V, gm −23 %; campaign A gm ±2 % |
| Flat mu_band ≤ 6.3 nm then ×3.2 step (19.3/19.6/62.7) | plausible, unverified (ATLAS prediction registered) | calibration | Ion check −2.6/−7.9/+0.1 % |
| Structural transition (crystallinity / grain boundaries / percolation) between 6.3 and 13.2 nm | plausible, unverified | correlation | 39 meV barrier suffices; mu_FE(31.8) 49 ≈ 50 |
| Metric power laws (mu_FE, Ion, Vth) | rejected | correlation | LOO misses ×2.6 to ×3.8; Ion(31.8) over by ×9.6 |
| dEc ∝ t^-1.38 beyond 3 nm | rejected (as physics) | none | 1.59× / 2.51× above the effective-mass bound |
| Nt ∝ t^-0.75 | not determined (empirical interpolation) | calibration | source exponents 0.73 vs 1.71 |
| m* ∝ t^-1.41 (non-parabolicity) | plausible, unverified | calibration | exponent matches dEc (−1.41 vs −1.38) |
| MTR temperature signature (V1) | not determined (prediction registered) | prediction | Δmu_FE < 1 %, ΔVth_cc −65 mV at 350 K |
| Phonon-limited 13.2 nm transport | not determined | none | expect −14 to −27 % × phonon fraction |
