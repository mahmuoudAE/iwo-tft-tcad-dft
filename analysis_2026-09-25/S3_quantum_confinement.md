# S3: Quantum confinement in ultrathin IWO TFTs. Is it needed, how large is it, and what separates it from electrostatics?

Specialist S3, 2026-09-25. No ATLAS launches were made. All new numbers come from three Python scripts in `analysis_2026-09-25/scratch/S3/`:
- `s3_e1_magnitude.py`, output in `s3_e1_magnitude_out.txt`;
- `s3_sp1d.py` (1-D Schrodinger-Poisson), output in `s3_sp1d_{notraps,traps,series}_out.txt` and `.json`;
- `s3_necessity_curves.py`, output in `s3_necessity_curves_out.txt`, which uses the real ATLAS `idvg.dat` of runs 0012, 0013, 0016 and 0017 and `data/experimental_clean.csv`.

Run IDs refer to `results/runs/<run>/execution.json`. "Shift" always means a gate-voltage shift in V at fixed electron sheet density n_s or fixed current.

## Summary

1. **Confinement at 2 nm is physically expected, but the transfer data cannot confirm it.**
   - Its expected size is 0.14 to 0.38 V as a subthreshold-equivalent shift, with a central value of 0.26 to 0.30 V for m* = 0.18 m0.
   - On one ID-VG curve per thickness it is exactly degenerate with about 1.7e12 cm^-2 of fixed charge, because q/Cox = 0.179 V per 1e12 cm^-2.
   - With the present data it is **assumed (physically supported), not demonstrated**.
2. **The data do not require confinement.**
   - The pre-registered held-out test A6 (run_0034: no confinement, Qf fitted on 2 nm only) predicts Vth_cc at 6.3 nm to within -0.057 V. The confinement model with a shared Qf (run_0014) misses by -0.294 V.
   - The story without confinement then misses 13.2 nm by +0.25 V. This value is derived from run_0017 using the exact rigid-Qf property; it was not run directly.
   - The extra Vth needed beyond a classical, confinement-free model is +0.30 / +0.36 / +0.05 V at 2 / 6.3 / 13.2 nm. This pattern is non-monotonic, and no confinement term can produce it, since confinement is ≤ 0.05 V at 6.3 nm.
3. **The SS_min "evidence" is an extraction artefact.**
   - Removing confinement changes the curve by a nearly rigid shift. The local SS versus log Id profiles of runs 0012/0016 and 0013/0017 agree within 1 to 2 mV/dec.
   - SS_min changes (73 → 84 and 151 → 139 mV/dec) only because the first 5-point window above the 5×-floor threshold lands at a different place on the 0.05 V grid.
   - Resampling the confinement-on curve onto the no-confinement grid alone gives 76 to 82 mV/dec (2 nm) and 136 to 137 mV/dec (13.2 nm).
4. **ATLAS dEc(2 nm) = 0.353 eV is at the high end of what effective-mass SP gives.**
   - ATLAS realises 0.345 V without traps and 0.315 to 0.326 V with traps.
   - SP gives 0.256 V (finite barriers), about 0.30 V (effective width anchored on the DFT slabs) and 0.384 V (hard wall), all for m* = 0.18 with non-parabolicity.
   - If W raises m* to 0.26 to 0.35, SP gives only 0.14 to 0.20 V.
   - Beyond 2 nm, the t^-1.38 law overestimates confinement by about 2× (6.3 nm: 0.070 vs 0.036 V) and 1.6× (13.2 nm: 0.026 vs 0.016 V).
5. **New finding: classical drift-diffusion is adequate for the trap-free electrostatics at 2 nm, but not for the free/trapped partition.**
   - Trap-free at 2 nm, C_eff agrees within 1 % and the onset shift is rigid.
   - With the V1 tail, the result depends strongly on which energy the localized tail states are referenced to. If the tail follows the confined edge, the shift at 2 nm is 0.26 V. If it stays at the bulk edge, the shift is 0.91 V.
   - At 6.3 and 13.2 nm, gate-field quantization combined with local tail states raises Vg(n_s = 1e12) by 0.15 to 0.19 V relative to classical, while Vg(1e10) moves by ≤ 0.04 V. That is a change in curve shape which the rigid dEc law cannot represent.

---

## 1. Magnitude of the ground subband (Task 1)

Source: `s3_e1_magnitude_out.txt`. E1 is measured from the bulk Ec, for a flat band. NP is the Kane non-parabolicity E(1+αE) = ħ²k²/2m*, with α = C = 0.5 eV^-1 and m*(0) = 0.18 ± 0.02 m0 (Stokey2021 l.196-197, quoting Feneberg).

| t (nm) | infinite well, m* 0.18 / 0.208 / 0.257 / 0.35 (eV) | infinite well + NP, same m* (eV) | finite barriers, BDD, m* 0.18 + NP (eV) | ATLAS dEc (eV) | kT (eV) |
|---|---|---|---|---|---|
| 2.0 | 0.522 / 0.452 / 0.366 / 0.269 | 0.430 / 0.380 / 0.316 / 0.240 | 0.231-0.252 (heavy barrier mass); 0.305 (equal mass) | 0.353 | 0.0259 |
| 6.3 | 0.053 / 0.046 / 0.037 / 0.027 | 0.051 / 0.045 / 0.036 / 0.027 | 0.039-0.040 | 0.072 | |
| 13.2 | 0.012 / 0.010 / 0.008 / 0.006 | 0.012 / 0.010 / 0.008 / 0.006 | 0.010-0.011 | 0.026 | |

**Barriers.** None of these values are measured for this stack.
- Al2O3 conduction-band offset: 2.0 / 3.4 / 4.0 eV, all ASSUMED.
  - 3.4 eV is what ATLAS loads by default (χ_Al2O3 = 0.9 eV; Astra QUANTUM_SENSITIVITY.md l.83-87).
  - Si2021 (l.284-285) states "> 4 eV".
- Vacuum barrier: χ_IWO = 4.3 eV (Fan2021 estimate, model yaml). This is an idealisation, because the channel is exposed to air and may carry adsorbates.
- Barrier masses: 0.4 m0 for Al2O3 and 1.0 m0 for vacuum, both ASSUMED.
- Across Al2O3 offsets of 2 to 4 eV, E1 changes by < 0.02 eV.

**The boundary condition matters more than the barrier height.** Under BenDaniel-Duke matching, heavy barrier masses effectively widen the well by (m_b/m_w)/κ per side. This halves E1 at 2 nm (0.43 → 0.25 eV). With equal masses the wall is effectively about 0.47 nm wider (Q1); with a hard wall it is not widened at all (Q2).

**The three PBE slab points fix the effective width.**
- The three points are Lin2022 0.95 and 1.98 nm, 0.94 and 0.33 eV (l.547-549), and Si2021 1.5 nm, about 0.6 eV (l.297).
- An effective-mass + NP well with m* = 0.17 (the Lin2022 PBE bulk mass, l.331) reproduces all three within 0.06 eV.
- The fit gives α = 0.59 eV^-1 and an effective width of t + 0.26 nm.
- The fitted α is close to the measured C = 0.5 eV^-1, so the PBE slabs behave like a physically sensible effective-mass well.

This "DFT-anchored" curve gives:

| t (nm) | 2 | 3 | 4 | 5 | 6.3 | 13.2 |
|---|---|---|---|---|---|---|
| E1 (eV) | 0.357 | 0.187 | 0.114 | 0.076 | 0.050 | 0.012 |
| ATLAS law (eV) | 0.353 | 0.202 | 0.136 | 0.100 | 0.072 | 0.026 |
| ratio law / EM | 0.99 | 1.08 | 1.19 | 1.30 | 1.45 | 2.15 |

The local exponent of the physical curve is -1.50 at 2 nm, -1.87 at 6.3 nm and -1.95 at 13.2 nm; the V1 power law is fixed at -1.38. The V1 law is therefore **correct at its anchor (2 nm) and unphysical beyond about 3 nm**. This agrees with S2, who reported ×1.59 / ×2.51 against the parabolic infinite well with m* = 0.208.

**E1 is not the quantity a classical model should use.** A 2-D subband carries more states than Nc·t does over the same energy. The "subthreshold-equivalent rigid shift" is dEc_eq = -kT ln[Σ_i g_2D,i kT e^(-E_i/kT) / (Nc t)] (section f of the output). At 2 nm, with m* = 0.18, NP and a finite barrier, dEc_eq = 0.207 to 0.215 eV while E1 = 0.248 eV. The 2-D density of states subtracts about 0.04 V at 2 nm and about 0.01 V at 6.3 nm.

**Gate-field (triangular) confinement.** The interface field is F = q n_s/(ε_IWO ε0).
- n_s = 1e12 cm^-2: F = 1.95e5 V/cm, E1_tri = 0.10 eV and ⟨z⟩ = 3.45 nm (m* = 0.18).
- n_s = 1.3e13 cm^-2 (Vg = 3 V; the bound Cox(3 - Vth_cc)/q is 1.31 / 1.32 / 1.63e13): E1_tri = 0.56 eV and ⟨z⟩ = 1.47 nm.

When the field rather than the film sets the wavefunction (from the SP centroids, §2):
- **2 nm:** never. The centroid stays at 0.94 to 0.98 nm, about t/2, up to 1.3e13 cm^-2.
- **6.3 nm:** set by the film at threshold (2.97 nm at 1e12, t/2 = 3.15 nm) and by the field above about 2-3e12. At 3 V the centroid is 1.89 nm.
- **13.2 nm:** set by the field from about 1e11-3e11 upward. At 3 V the centroid is 2.31 nm.

So at Vg = 3 V every film is strongly quantized, with E1 about 0.5 eV. For the 6.3 and 13.2 nm films this is inversion-layer-like field quantization, which V1 does not represent at all.

**Image (dielectric) confinement.** The air side has ε 1 against ε 9.3 for IWO. This adds about +31 meV at 1 nm from the air surface (single-interface estimate), so roughly +0.02 to 0.03 eV at 2 nm. It is not included in PBE, the SP model or ATLAS. This term is plausible-unverified.

## 2. 1-D Schrödinger-Poisson vs classical 3-D Fermi-Dirac (Task 2)

**Model** (`s3_sp1d.py`):
- Stack: TiN 4.70 eV | HfO2 15 nm (ε 19.57) | Al2O3 2 nm (ε 9.0) | IWO t nm (ε 9.3, χ 4.3) | air, with a Neumann condition at the IWO top.
- Fixed charge Qf = +1.73e12 cm^-2 and Nd_eff(t) from the V1 laws. EF = 0; the channel centre is at Vd = 0.
- Q1: m* 0.18 with NP 0.5, finite barriers (3.4 / 4.3 eV) with equal masses; this is the central case.
- Q2: hard wall (upper bound).
- Q3: BenDaniel-Duke with heavy barrier masses (lower bound).
- Q4: m* 0.257, parabolic. Q5: m* 0.35, parabolic.
- C0: classical, no dEc, Nc(0.208); the analogue of runs 0016 / 0017 / 0034.
- C1: classical with the ATLAS dEc law and Nc(m*(t)); the analogue of runs 0012 / 0014 / 0013.
- Gauss-law error is ≤ 2e-18 C/cm².

**Trap-free results** (shift relative to C0 at n_s = 1e10 cm^-2, in V; the shift at 1e11 agrees within 3 mV):

| t (nm) | C1 (ATLAS law) | Q1 central | Q2 hard wall | Q3 BDD heavy | Q4 m*0.257 | Q5 m*0.35 |
|---|---|---|---|---|---|---|
| 2.0 | 0.345 | 0.256 | 0.384 | 0.202 | 0.205 | 0.139 |
| 3.0 | 0.197 | 0.131 | 0.179 | 0.105 | 0.090 | 0.052 |
| 4.0 | 0.133 | 0.078 | 0.102 | 0.065 | 0.047 | 0.021 |
| 5.0 | 0.097 | 0.052 | 0.065 | 0.045 | 0.028 | 0.007 |
| 6.3 | 0.070 | 0.036 | 0.043 | 0.031 | 0.016 | -0.002 |
| 13.2 | 0.026 | 0.016 | 0.018 | 0.015 | 0.001 | -0.012 |

**Consistency check with ATLAS.** With the V1 tail and Dit included as classical DOS, the 1-D C1 - C0 shift is:
- 0.326 V at 1e10 and 0.300 V at 1e11 for 2 nm. ATLAS 0012 - 0016 gives ΔVth_cc = 0.315 V and ΔVth_lin = 0.299 V.
- 0.023 V for 13.2 nm, equal to ATLAS 0013 - 0017.

The 1-D model therefore reproduces the ATLAS relative shifts to within 11 mV. Absolute onsets are not compared, because Vth_cc is a 2-D current criterion at Vd = 0.7 V.

**Verdict on ATLAS dEc(2 nm).**
- Relative to effective-mass SP with m* = 0.18, ATLAS **overestimates** the realised shift. The overestimate is 0.09 V against Q1 and about 0.05 V against the DFT-anchored width. The DFT-anchored value is E1 = 0.35 eV minus the 2-D DOS term of 0.045 eV observed in Q2, which gives about 0.30 V.
- It overestimates by 0.14 to 0.21 V if W raises m* to 0.26 to 0.35. Januar2026 (l.238-241) reports a flatter CBM with W, but only qualitatively.
- The value still lies inside the SP bracket of 0.14 to 0.38 V and within the stated ±50 %.
- Two errors in ATLAS partly cancel:
  - the gap shift is applied as a rigid Ec shift, which ignores the 2-D DOS gain (+0.04 V too high);
  - the m*(t)-driven increase of Nc works in the opposite direction (-8 mV).

**Dark space and capacitance** (trap-free; C_eff = q Δn_s/ΔVg over 2 to 3 V):

| t (nm) | C_eff/Cox, C0 / C1 / Q1 / Q2 | centroid at 3 V, C0 / Q1 / Q2 (nm) | centroid at 1e12, C0 / Q1 (nm) |
|---|---|---|---|
| 2.0 | 0.874 / 0.885 / 0.884 / 0.880 | 0.82 / 0.94 / 0.98 | 0.94 / 0.99 |
| 6.3 | 0.878 / 0.880 / 0.853 / 0.832 | 1.43 / 1.89 / 2.10 | 2.51 / 2.97 |
| 13.2 | 0.878 / 0.878 / 0.853 / 0.832 | 1.74 / 2.31 / 2.56 | 4.93 / 5.60 |

- The quantum dark space is +0.12 to 0.16 nm at 2 nm and +0.5 to 0.8 nm at 6.3 and 13.2 nm. That corresponds to +0.05 to 0.07 nm and +0.2 to 0.34 nm of EOT, against an EOT of 3.86 nm.
- Even the classical model has C_eff/Cox of only about 0.87, because of its own centroid and degenerate DOS. μ_FE extracted with Cox therefore understates the band mobility by about 13 % before any trapping. ATLAS includes this effect, so the fitted mu_band already absorbs it.
- The extra quantum bias is < 1 % at 2 nm and 3 to 5 % at 6.3 and 13.2 nm. A quantum model would need mu_band about 3 to 5 % higher at those thicknesses, which is negligible against the 4 to 5× mobility step (S2).
- **Coupling to S2.** Januar2026 (l.539-541) argues that "electrostatic confinement forces the carrier wavefunction closer to the dielectric interface". SP shows the opposite for 2 nm: quantization moves charge away from Al2O3 to mid-film, and the wavefunction overlaps both surfaces. The (1-Dsr/t)² roughness factor is therefore a phenomenological term, not a consequence of the physics of confinement.

**With the tail as a fixed classical DOS** (`s3_sp1d_traps_out.txt`; shift relative to C0 at n_s = 1e10 / 1e11 / 1e12, in V):

| t (nm) | C1 (ATLAS) | Q1, tail follows the confined edge | Q1, tail at the bulk Ec | Q2 (confined-edge tail) |
|---|---|---|---|---|
| 2.0 | 0.326 / 0.300 / 0.301 | 0.259 / 0.267 / 0.231 | **0.911 / 0.673 / 0.339** | 0.387 / 0.399 / 0.366 |
| 6.3 | 0.067 / 0.062 / 0.059 | 0.040 / **0.103 / 0.190** | 0.158 / 0.346 / 0.327 | 0.047 / 0.117 / 0.224 |
| 13.2 | 0.023 / 0.023 / 0.022 | 0.014 / **0.071 / 0.175** | 0.053 / 0.179 / 0.233 | 0.015 / 0.081 / 0.207 |

- **Bulk reference at 2 nm.** If localized tail states do not follow the confined edge (localization length shorter than t), the whole 4e12 cm^-2 tail must fill before the subband populates. The onset then moves by +0.91 V, and the 1-D slope from 1e10 to 1e11 falls from 326 to 80 mV/dec. Both results are inconsistent with the measured curve unless everything is refitted.
- **Confined-edge reference at 6.3 and 13.2 nm.** Here the gate field lifts the subband 0.1 to 0.15 eV above the band edge at the interface. This forces EF higher at the interface for the same free n_s, and so fills more of the steep tail (WTA = 40 meV).
  - Vg(1e12) - Vg(1e10) grows by +0.15 V (6.3 nm) and +0.16 V (13.2 nm), and falls by 0.03 V at 2 nm.
  - This is a change in curve shape in the threshold region. It points the same way as the unexplained 6.3 nm Vth_lin-Vth_cc gap (measured 1.176 V; run_0015 gives 0.820 V).
  - The same effect appears at 13.2 nm, where the classical model already fits that gap (0.946 vs 0.961 V). It is therefore a **model-form uncertainty of about 0.15 V in Vth_lin at t ≥ 6.3 nm, not an explanation**.

**Answer to "is classical DD adequate at 2 nm?"**
- **Trap-free electrostatics: yes**, once a correct dEc_eq is inserted. The onset shift is rigid within 11 mV across 1e10 to 1e12, and C_eff agrees within 1 %.
- **Trap-limited device: not determined.** The result hinges on where the localized tail states sit relative to the confined subband. No local data or theory fixes this; the relevant physics is localization length against t. This belongs jointly to S3 and S4.

**Simplifications:**
- 1-D model at Vd = 0; single isotropic valley.
- NP enters only through the subband-bottom masses; in-plane NP is ignored in the degenerate regime.
- No exchange-correlation, image potential or disorder.
- Wavefunction weight in Al2O3 is dropped from Poisson (≤ 2 %).
- Deep Gaussian omitted (< 1 mV).
- φ_M, χ and the barriers are ASSUMED.

**Cross-check with Astra's hard-wall ATLAS SP** (Astra QUANTUM_CHARGE_VERIFICATION.md; 2 nm, m* = 0.34, trap-free, different seed stack): at 3 V the centroid is 0.965 nm (quantum) against 0.745 nm (classical). My values are 0.98 and 0.82 nm, so the two are qualitatively consistent. Their n_s deficits are not comparable to mine, because the stack parameters differ.

## 3. Necessity test (Task 3)

**Extra Vth_cc needed beyond the confinement-free classical model with Qf 1.73e12** (`s3_necessity_curves_out.txt`):

| t (nm) | measured Vth_cc (V) | no-QC model (V) | needed (V) | as negative charge (cm^-2) | ATLAS-QC supplies (V) | residual (V) |
|---|---|---|---|---|---|---|
| 2.0 | 0.662 | 0.361 (run_0016) | +0.301 | 1.68e12 | +0.315 | -0.014 |
| 6.3 | 0.644 | 0.286 (run_0034 rigidly shifted) | +0.358 | 2.00e12 | +0.064 | +0.294 |
| 13.2 | 0.083 | 0.030 (run_0017) | +0.053 | 2.96e11 | +0.023 | +0.030 |

**One-offset stories:**

| story | fit | 2 nm miss (V) | 6.3 nm miss (V) | 13.2 nm miss (V) |
|---|---|---|---|---|
| A: QC + Qf fitted on 2 and 13.2 nm | calibration | -0.014 | -0.294 (run_0014, active RMSE 0.678 dec) | -0.030 |
| B: no QC + Qf 4.76e10 fitted on 2 nm only | 6.3 nm is a held-out prediction | 0 | -0.057 (A6/run_0034, RMSE 0.211 dec) | +0.248 (derived) |

Neither story fits all three thicknesses with one offset.

**Data features:**
- The needed offset is non-monotonic in t. Every confinement estimate is monotonic and ≤ 0.05 V at 6.3 nm.
- The shape of the 6.3 nm curve does not depend on confinement: gm_max is 2.80e-7 A/V/µm in A6 and 2.86e-7 in run_0014. Vth_lin still misses by -0.39 V in A6.

**Verdict: the transfer data *tolerate* confinement and do not *require* it.**
- They mildly *disfavour* a confinement-dominated reading of Vth(t).
- If confinement at 2 nm is real, then about 0.14 to 0.38 V of it must be compensated at 2 nm relative to 6.3 nm. That is 0.8 to 2.1e12 cm^-2 of extra positive charge or equivalent, or the 6.3 nm device has an offset of the same size by coincidence.
- With n = 1 device per thickness, the second option cannot be excluded.

**The exact degeneracy.**
- On one curve, dEc_eff(2 nm) = 0.301 to 0.315 V is equivalent to ΔQ = 1.68 to 1.76e12 cm^-2 of fixed negative charge. Equivalently, Qf 1.73e12 → 4.76e10, which removes 97 % of the fitted Qf.
- The same offset also trades off one-to-one with φ_M (assumed 4.70, with a TiN range of 4.5 to 4.9 eV) and with χ (4.3 ± 0.3 eV). Each of those uncertainties is as large as dEc itself.
- The only same-curve signatures that differ are second-order:
  - The Nc(m*) change makes the shift non-rigid above 1e-10 A/µm (0.345 → 0.302 V at 1e-8) and moves SS_cc from 289 to 304 mV/dec (measured 270).
  - The quantum C_eff differs by < 1 % at 2 nm.
- Both effects are smaller than the leverage of the fitted parameters: WTA +5 meV gives +12 mV/dec, and Dit ×3 gives +9 mV/dec (brief §4).
- **dEc is not identifiable from ID-VG.**

**SS_min.**
- The horizontal shift is constant at 0.345 V from 1e-14 to 1e-11 A/µm, which is exactly dEc - kT ln(Nc ratio) = 0.3451.
- The local SS versus log Id profiles coincide. At log Id of -12.9 / -12.2 / -11.5 the on and off curves give 67/68, 73/74 and 83/84 mV/dec.
- The simulated SS rises steeply with current (about 10 to 25 mV/dec per 0.5 dec). SS_min is therefore just the SS of the first window above 5× the measured floor, and it depends on where that window falls on the grid.
- The resampling test reproduces most of the "improvement" with the same physical curve: 73 → 76 to 82 (2 nm) and 151 → 136 to 137 (13.2 nm).
- **Not evidence.** The same artefact affects the measured SS_min. The fitted WTA and Dit are not implicated, because the shift is rigid in that current range. Report SS_cc, or SS at a fixed current, instead.

## 4. Validity of the DFT proxy (Task 4)

- **Supports it.** The pure-In2O3 PBE slabs (H-passivated/vacuum in Lin2022; corundum on Al2O3, H-terminated in Si2021) behave like an effective-mass well with a sensible spill (0.26 nm total) and a sensible α (0.59 eV^-1). The 2 nm anchor is therefore credible as an **independent theoretical prediction**. It is not fitted to the devices.
- **Against it: the extrapolation.** The 3-point log-log fit has a local slope and should steepen toward -2. Its extrapolation to 6.3 and 13.2 nm overestimates by 1.45× and 2.15×. The Vth impact is ≤ 0.035 V, so this is harmless for the 6.3 nm question.
- **W.** Januar2026 (l.238-241) reports a flatter CBM and heavier m* with W, but only qualitatively. The effect is NOT DETERMINED numerically. m* = 0.257 or 0.35 lowers the 2 nm SP shift to 0.205 or 0.139 V.
- **Disorder.** The slabs are crystalline (bixbyite or corundum). Sputtered 2 nm films are probably amorphous (Si2021 on ALD films of 0.7 to 1.5 nm; S2).
  - Confinement applies to extended states whose localization length exceeds t.
  - Tail states with a localization length below t are not lifted.
  - §2 shows that this distinction changes the 2 nm onset by 0.65 V with the V1 tail. Localization lengths are NOT DETERMINED FROM AVAILABLE DATA.
- **Interface dipoles and termination.** H or OH termination (DFT) differs from an air-exposed surface (device). The Al2O3/IWO and IWO/air dipoles shift χ_eff by amounts not captured by the slab-minus-bulk difference, and at 2 nm the two dipoles may overlap. These effects are unquantified and degenerate with φ_M, χ and Qf.
- **Thickness definition.** Slab thickness is set by atomic planes, while device thickness is nominal (method unknown). ±0.3 nm at 2 nm moves E1 by about ±25 % (S5).
- **PBE gap error.** Only shifts are used. The fitted α (0.59) is close to the measured 0.5, so the PBE non-parabolicity does not appear to distort the shift strongly.

## 5. Distinguishing predictions (Task 5)

| test | confinement-dominated prediction | charge-dominated prediction | source |
|---|---|---|---|
| Optical/SE/REELS gap, Eg(t) - Eg(13.2) | 2 nm: +0.2 to 0.45 eV (electron E1 0.17 to 0.43 eV, central about 0.35, plus hole ≤ 0.05; Si2021 l.290-292 says Ev is almost unchanged); 6.3 nm: +0.02 to 0.05; 3 / 4 / 5 nm: about +0.19 / 0.11 / 0.08 (DFT-anchored) | < 0.02 eV at all t | §1 |
| CBM from IPES, or from UPS/XPS (EF - Ev) plus the optical gap | Ec rises about 0.3 eV at 2 nm relative to 6.3 nm | Ec fixed; EF moves instead | §1 |
| Denser series, ΔVth_cc with all else equal (1-D shift at 1e10) | 2→3 nm: +0.125 to 0.205 V; 3→4: +0.05 to 0.08; 4→5: +0.026 to 0.037; 5→6.3: +0.016 to 0.022 (Q1 to Q2). Onset approximately t^-1.5 to t^-2 below 4 nm | flat for 2 ≤ t ≤ 6.3 nm (step picture) or monotonic in 1/t (interface-charge dilution) | `s3_sp1d_series_out.txt` |
| Temperature, 300 → 358 K | confinement offset changes by -6 mV (2-D DOS term, -1.0e-4 eV/K); dVth/dT independent of thickness within about 0.1 mV/K | a thermally activated trap or donor offset gives a thickness-dependent dVth/dT; magnitude NOT DETERMINED without a specific model | analytic, §1(f) |
| Replicates | resolving ΔVth = 0.13 V (2 vs 3 nm) at 95 %/80 % needs n ≈ 15.7 σ²/Δ²: n = 3 per thickness if σ = 0.05 V, n = 10 if σ = 0.10 V | the same n decides whether the 6.3 nm offset of 0.29 V is device-specific | device spread NOT DETERMINED |
| Split C-V plus Hall n_s(Vg) | free/trapped partition near threshold: the observable most sensitive to the tail reference (§2) | – | |

## 6. Couplings and identifiability

- **S1.** dEc(t) trades off against Qf, φ_M and χ, and against t-dependent fixed or back charge: 1 V ↔ 5.6e12 cm^-2.
  - C-V V_FB per thickness does not separate them, because it measures the same sum.
  - Only a spectroscopic Ec(t) (optical gap, IPES) combined with C-V breaks the degeneracy.
  - My 1-D model reproduces ATLAS relative shifts to within 11 mV, so S1 can use it as a fast surrogate.
- **S2.** C_eff/Cox is 0.86 to 0.88 classically (trap-free). The quantum correction is ≤ 1 % at 2 nm and -3 to -5 % at 6.3 and 13.2 nm. The m*(t) Drude effect (-18 % at 2 nm, S2) is hidden in mu_band. Roughness scattering cannot rest on a "pushed to the interface" argument at 2 nm.
- **S4.**
  - The energy reference of the tail under confinement is the dominant model-form uncertainty: 0.26 vs 0.91 V at 2 nm.
  - Field quantization with local tails changes the free/trapped partition by 0.15 to 0.19 V in Vg(1e12) at t ≥ 6.3 nm.
  - WTA, Nt(t) and dEc trade off on one curve, and SS_cc is the only lever, which is weak.
  - Si2021's picture of a TNL at fixed absolute energy (l.294-300) is the "bulk-reference" limit.
- **S5.** Confinement raises the Pd/IWO barrier by E1 at 2 nm (0.25 to 0.38 eV). This is consistent with S5's verdict of plausible-unverified.
- **S6.**
  - Run ATLAS's own Schrodinger-Poisson or BQP with the DOS enabled at 6.3 and 13.2 nm to test the +0.15 to 0.19 V Vg(1e12) prediction. It was made here before any such run and should be registered as a prediction.
  - Report SS at a fixed current rather than SS_min.
  - Replace the t^-1.38 extrapolation with the DFT-anchored effective-mass + NP curve (0.357 / 0.050 / 0.012 eV), or with dEc_eq from SP.

## Verdicts

| mechanism / claim | verdict | evidence class | key number |
|---|---|---|---|
| Film (geometric) confinement exists at 2 nm | strongly supported | prediction (theory: effective mass + PBE slabs; not measured on IWO) | SP subthreshold-equivalent shift 0.26 to 0.30 V (m* 0.18); bracket 0.14 to 0.38 V |
| Transfer data require confinement | rejected | prediction (A6/run_0034, held-out 6.3 nm) | no-QC miss -0.057 V vs -0.294 V with QC |
| Confinement explains the Vth(t) pattern (2 ≈ 6.3 ≫ 13.2) | rejected | correlation + calibration | needed offset +0.30 / +0.36 / +0.05 V; QC at 6.3 nm ≤ 0.05 V |
| ATLAS dEc = 0.353 eV at 2 nm (realised 0.315 to 0.345 V) | plausible-unverified; high relative to SP | prediction (DFT) vs SP | overestimates Q1 by 0.09 V and the DFT-anchored width by about 0.05 V; by 0.14 to 0.21 V if m* ≥ 0.26 |
| t^-1.38 law beyond 3 nm | rejected (as physics) | none (extrapolation) | ×1.45 at 6.3 nm, ×2.15 at 13.2 nm; SP 0.036 vs 0.070 V at 6.3 nm |
| SS_min change without confinement as evidence | rejected (extraction artefact) | numerical audit of runs 0012/0016/0013/0017 | resampling alone gives 76 to 82 and 136 to 137 mV/dec; local SS agrees within 2 mV/dec |
| Classical DD adequate at 2 nm (trap-free n_s, C_eff) | strongly supported | prediction (1-D SP) | rigid within 11 mV; C_eff within 1 % |
| Tail-state energy reference under confinement | not determined | none | 2 nm onset shift 0.26 (confined edge) vs 0.91 V (bulk edge) |
| Gate-field quantization at 6.3 and 13.2 nm (on-state) | strongly supported (existence); plausible-unverified (device impact) | prediction (SP) | E1_tri about 0.5 eV at 3 V; C_eff -3 to -5 %; with local tails Vg(1e12) +0.15 to 0.19 V |
| Image-charge (dielectric) confinement | plausible-unverified | none (estimate) | about +0.02 to 0.03 eV at 2 nm |
| dEc identifiable from one ID-VG per thickness | rejected | calibration (degeneracy) | 0.301 to 0.315 V ≡ 1.68 to 1.76e12 cm^-2 |

**Wording for the paper.**

> "A confinement shift of about 0.3 eV at 2 nm is expected from effective-mass Schrodinger-Poisson calculations anchored on PBE slab calculations (0.14–0.38 V depending on effective mass and barrier treatment). It is included as an assumed, independently predicted term. The transfer characteristics alone cannot distinguish it from a fixed-charge offset of about 1.7 × 10^12 cm^-2, and it does not explain the similar thresholds of the 2 and 6.3 nm devices."
