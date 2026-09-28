# SYNTHESIS: thickness dependence of ultrathin IWO bottom-gate TFTs (2 / 6.3 / 13.2 nm)

Synthesis author, 2026-09-25. Paths are relative to the package root `IWO_PHYSICS_CONSTRAINED_MODEL_V1`.

**Scope of this stage**
- No ATLAS launch was made. Nothing outside `analysis_2026-09-25/` was modified.
- Inputs: `EVIDENCE_BRIEF.md` (§1-5b); S1-S6; `PREDICTIONS_REGISTER.md`; `REVIEW.md`; campaigns A, B and C; run_0001 to run_0052; `data/experimental_clean.csv`.
- New read-only check: `scratch/SYNTHESIS/syn_checks.py`, output in `syn_checks_out.txt` (cited as [SYN-a/b/c]). It computes:
  - (a) horizontal offsets Vg_meas(I) − Vg_sim(I) at fixed currents for 13 runs;
  - (b) the one-offset threshold fits, re-derived from `execution.json`;
  - (c) SHA-256 of the 44 files hashed in the register. All 44 are unchanged.
- A second read-only check: `scratch/SYNTHESIS/syn_leverage.py`, output in `syn_leverage_out.txt` [SYN-d]. It computes same-metric leverages of one-at-a-time pairs at 2 nm.

**Evidence classes**

| class | meaning |
|---|---|
| DATA | measured curve, unchanged extractor |
| NUM | converged ATLAS result, model-internal |
| CAL | fitted to the same curve |
| OOS | out-of-sample test designed before the outcome |
| POST | test designed or evaluated after the outcome was known |
| PRED | registered, untested |
| SURR | specialist surrogate, not independently re-run |
| THEORY | theory |
| LIT | literature, often a related material |
| CORR | correlation across three devices |

Every data statement is about **one device per thickness (N = 1)**.

---

## 0. Executive summary

In these single devices, the 2 and 6.3 nm TFTs are electrically similar (Vth_cc 0.662 / 0.644 V; mu_FE 12.2 / 11.0 cm²/Vs). The 13.2 nm device differs sharply (0.083 V; 50.2 cm²/Vs). No thickness power law describes this.

**Most defensible explanation (moderate-to-low certainty).** The dominant change is in channel transport and charge between 6.3 and 13.2 nm. It sits on top of trap-limited conduction through a near-Ec exponential tail, which is present in all films.
- The ~4.6-fold rise in apparent mobility cannot be attributed, within the calibrated model, to contacts, roughness, electrostatics or tail filling (strongly supported, model-conditional).
- Its physical origin, for example a structural transition, is not determined.

**Confinement.** A shift of about 0.3 eV at 2 nm is expected theoretically, but the data neither require nor identify it.
- On one ID-VG curve it is exactly equivalent to about 1.7e12 cm⁻² of fixed charge.
- One shared offset fits equally well with or without it (rms 0.136 vs 0.133 V).

**The 6.3 nm discrepancy has two parts:**
- a rigid part (0.29 V with confinement, 0.06 V without), which cannot be assigned with N = 1;
- an on-state shape part: the turn-on delay is 0.31-0.36 V too small and gm is 17-23 % low. No tested V1 change reproduces it without breaking the subthreshold slope, which points to the constant-mobility model form.

**Status.** The model is calibrated, not validated. The ID-VD and 338/358 K predictions are hash-registered in two exact mobility variants and await independent data.

---

## A. Demonstrated conclusions (data and converged simulations)

### A.1 Statements

| # | conclusion and key numbers | class | source |
|---|---|---|---|
| D1 | **Measured pattern: 2 ≈ 6.3 nm ≠ 13.2 nm in every metric.** Vth_cc 0.662 / 0.644 / 0.083 V; mu_FE 12.15 / 10.95 / 50.17 cm²/Vs; SS_cc 269.9 / 295.4 / 160.0 mV/dec; Ion 5.09e-7 / 4.03e-7 / 3.07e-6 A/µm; floor 4.6e-15 / 1.5e-13 / 6.6e-12 A/µm. mu_FE(6.3) < mu_FE(2), so no monotonic law passes through all three | DATA | brief §2 |
| D2 | **WF, χ, Qf and the pure dEc shift are one number per curve.** WF +0.1 eV gives +0.1000 V rigid with SS unchanged (runs 0048, 0049). Qf is rigid within 0.6 mV over 1e-14..3e-7 A/µm (0001→0003, 0002→0004, 0005→0007). dEc(2 nm) = 0.353 eV ≡ 1.97e12 cm⁻². The V1 confinement *package* (dEc plus m*→Nc) is only near-rigid: the shift is 0.345 V at 1e-14, 0.302 V at 1e-8 and 0.311 V at 3e-7 A/µm, and SS_cc is 289.1 vs 303.7 mV/dec (0012 vs 0016). Its non-rigid part (+38.8 mV between 1e-11 and 1e-8 A/µm; SS_cc +14.6 mV/dec) is nearly reproduced by m* ×0.8 (SS_cc +14.6, +37.5 mV) or by Nt ×1.09 (+14.6, +34 mV), from log-linear scaling of runs 0050 and 0023 | NUM | REVIEW V5; S6 §2; [SYN-d] |
| D3 | **The thresholds do not discriminate confinement.** One-offset rms 0.1363 V (with) vs 0.1325 V (without); leave-one-out 0.2045 vs 0.1988 V. The winner flips with the anchor: 2 nm anchor 0.2205 vs 0.1800 V; 13.2 nm anchor 0.1897 vs 0.2782 V. Each reading needs one film-specific charge. With confinement, 6.3 nm needs Qf 0.086e12 against the shared 1.73e12 (1.64e12 cm⁻² less positive, 0.294 V). Without it, 13.2 nm needs 1.434e12 against 0.047e12 fitted on 2 nm (1.39e12 more positive, 0.248 V) | NUM on DATA | [SYN-b]; REVIEW V11 |
| D4 | **The shared-parameter model misses the 6.3 nm threshold by −0.294 V** (run_0014). mu_band 12.4 is the V0 fit of the same curve (`config/iwo_material_model.yaml` l.105), so this is a failed OOS test of the **threshold only** | OOS, failed | REVIEW §1(b) |
| D5 | **No tested V1 variant reproduces the 6.3 nm on-state without breaking the subthreshold.** Eight charge/electrostatic variants (runs 0014, 0015, 0030-0035) give gap 0.72-0.88 V against 1.176 V measured. C1 (run_0052) gives 0.939 V. B0 (run_0037) gives 1.202 V but with SS_cc 410.9 against 295.4 mV/dec. Smaller same-signed misses exist at 2 nm (gap −0.145 V, gm −8.6 %) and 13.2 nm (−0.021 V, −2.6 %) | NUM | S6 §1.6, §3.1 |
| D6 | **The constant-current threshold is mobility-confounded.** Giving the 13.2 nm curve the 2 nm mobility moves Vth_cc by +0.108 to +0.115 V, i.e. 19-20 % of the measured 0.579 V step. The model's confinement term realises 0.292 V (0.3156 − 0.0234), i.e. 50.4 % of that step | DATA / NUM | REVIEW V8, V13 |
| D7 | **SS_min is invalid.** run_0012 and B1 (Ion equal within 0.01 %) give 73.2 vs 83.1 mV/dec, from a 2.5 % current difference at Vg = 0.15 V. The claim "removing confinement moves SS toward the data" is an artefact: SS_min 151.3 / 138.6 (runs 0013 / 0017), but fixed-current SS 90.8 / 92.0 | NUM | S6 §1.4; REVIEW V9 |
| D8 | **Calibrated state at DOS 384/192** (B1, B2 ×1.015074, B3 ×1.020113) | CAL | S6 §1.6 |
| D9 | **300 K transfer numerics converge where checked.** At 2 nm, DOS refinement changes Ion by +1.98 % then +0.48 %: order 2.03, Richardson residual +0.16 %. The offset at equal mu is +2.48 / +0.95 / +0.50 %. Mesh ×0.7 passes at 6.3 nm (run_0036: 0.0625 vs 0.0626 dec, ΔVth_cc −0.3 mV) and at 13.2 nm (run_0028). Id is linear in mu to 6e-6; KCL ≤ 2.5e-16 A. The open items are listed in §F | NUM | S6 §1 |
| D10 | **The T ≠ 300 K runs (0044-0047) used the silicon default tmu = 1.5.** Ion(0045)/Ion(0038) = 0.7742, and × (358.15/300)^1.5 = 1.0098. Both registered variants are exact, because Id is linear in a uniform constant mobility | NUM | brief §5b; REVIEW V7 |
| D11 | **run_0027 is not an overlap test.** x.mesh ends at 24 µm, the drain collapsed to a line, and deckbuild.out reports "Electrode shortened" ×3 | audit | S5 §2 |
| D12 | **The paper's mobilities are the saturation formula applied to these curves.** It gives 5.09 / 27.40 cm²/Vs (paper: 5.1 / 27.4). The peaks sit at Vg 1.75 V (2 nm, 0.09 V above Vth_lin) and 0.95 V (13.2 nm, below Vth_lin), with Vd = 0.7 V. It predicts 3.86 cm²/Vs at 6.3 nm. This is provenance evidence: it fixes L/(W·Cox) × A/µm jointly, not Vd | DATA | REVIEW V3 |

**D8 breakdown** (each pair is measured / simulated; values for 2 / 6.3 / 13.2 nm):
- Vth_cc: 0.662/0.680, 0.644/0.653, 0.083/0.054 V.
- SS 1e-11..1e-10: 121.2/123.5, 124.5/124.5, 91.8/90.9 mV/dec. The 13.2 nm measured value is floor-subtracted; the raw value is 136.1.
- SS 1e-10..1e-9: the model is too soft by +20 / +6 / +25 mV/dec.
- Ion: 0.00 % by construction.
- mu_band: 17.69 / 11.58 / 61.60 cm²/Vs.

### A.2 The 6.3 nm discrepancy: rigid part and on-state shape part

The table gives the horizontal offset Vg_meas(I) − Vg_sim(I) in V [SYN-a]. A positive value means the measured curve reaches that current later.

| run | 1e-11 | 1e-10 | 1e-9 | 1e-8 | 3e-8 | 1e-7 | 2e-7 | 3e-7 A/µm |
|---|---|---|---|---|---|---|---|---|
| 6.3 nm run_0014 (shared) | +0.293 | +0.296 | +0.294 | +0.316 | +0.358 | +0.455 | +0.484 | +0.449 |
| 6.3 nm run_0015 (tuned Qf) | −0.003 | −0.003 | −0.007 | +0.011 | +0.047 | +0.132 | +0.141 | +0.087 |
| 6.3 nm A6 run_0034 (no confinement) | +0.063 | +0.062 | +0.057 | +0.077 | +0.117 | +0.213 | +0.239 | +0.201 |
| 6.3 nm C1 run_0052 | +0.010 | +0.009 | −0.004 | −0.009 | +0.024 | +0.134 | +0.201 | +0.212 |
| 6.3 nm B0 run_0037 | +0.142 | +0.094 | −0.010 | −0.138 | −0.167 | −0.125 | −0.088 | −0.084 |
| 2 nm B1 run_0038 | +0.004 | +0.002 | −0.019 | −0.040 | −0.029 | +0.008 | +0.034 | +0.037 |
| 13.2 nm B3 run_0040 | +0.006 | +0.051 | +0.029 | −0.015 | −0.029 | −0.029 | −0.026 | −0.020 |

- **Rigid part.** 0.294 V ≡ 1.64e12 cm⁻² with the confinement law (constant within 3 mV from 1e-11 to 1e-9 A/µm in run_0014). Without the law (A6) it is 0.057 V ≡ 0.32e12 cm⁻².
- **Shape part** (offset minus the offset at 1e-9), at 1e-7 / 2e-7 A/µm:
  - run_0014: +0.161 / +0.190 V;
  - run_0015: +0.139 / +0.148 V;
  - A6: +0.156 / +0.182 V.

  It is therefore independent of the confinement law and of Qf.
- **Comparison with the other films.** The residual swing is 0.07-0.08 V at 2 and 13.2 nm, against about 0.15 V at 6.3 nm, where it has a "late, then steep" form. B0 overshoots in the middle and misses the subthreshold.

### A.3 Specialist disagreements resolved from primary files

| issue | resolution and the evidence used |
|---|---|
| Do the Vth data favour confinement (FINAL_STATUS), favour no confinement (S1), or "mildly disfavour" it (S3)? | **Neutral** (D3; Vth_cc from `execution.json` plus the exact Qf identity). All three positions are overstated |
| Rigid 6.3 nm part: 0.10-0.16 V (S2) or 0.29 V (S1, S6)? | **0.294 V** (with confinement) in every run that keeps the fixed-current SS within ~15 mV/dec. C1 keeps Qf 8.7e10 and gives Vth_cc 0.648 V. S2's value needs B0's Qf of 9.8e11, i.e. a trap model that fails SS_cc by +116 |
| S2's re-partition "strongly supported" (written before B0) vs FAIL (S6) | **Rejected**: run_0037 gives SS_cc 410.9 against 295.4, and SS 1e-11..1e-10 +48.8 |
| SS_min change: physics (S4) or artefact (S3, S6)? | **Artefact**. Id(0.15 V) is 2.34e-14 / 2.28e-14 / 2.34e-14 A/µm (runs 0012 / 0038 / 0029) against a gate of 2.30e-14 |
| μ_sat peaks: "linear regime" (S2) or "Vov ≈ 1.1 V" (S5)? | **Neither**. Relative to Vth_lin the peaks sit at +0.09 / +0.73 / −0.09 V. The reproduction is provenance evidence |
| Near-Ec agreement: "reproduces all films" (S4) vs "too soft" (S6) | The model agrees in 1e-11..1e-10 only; it is too soft by +20 / +6 / +25 mV/dec in 1e-10..1e-9. S4's ratios hold through a mu-dependent inversion |
| Floors "flat to ±3 %" (S4) | 6.3 nm scatter is **±45 %** (max/min 3.0-3.5), with no trend (−0.011 dec/V). The trend-based rejection of gate leakage stands |
| 13.2 nm no-confinement Qf: ~1.86e12 (brief) vs 1.43e12 | **1.434e12** [SYN-b] |
| 13.2 nm isolation ΔIon: −6.8 / +3.7 % (brief) vs −5.0 / +5.8 % | Relative to B3: **−4.99 / +5.79 %**. The brief used the measurement as reference |
| S1's B0 SS_cc 418 "blind" (S6 P2); A6 "pre-registered" (S3, S6) | Both **POST**. The S1 code was saved at 19:18:00Z, during run_0037 (19:16-19:21Z). Config A was written days after the run_0014 miss was known |
| 31.8 nm "mu_FE 49.2" as support (S1, S2, S4) | **Not a mobility**: gm has maxima at −0.30, 0.85, 1.15 and 1.70 V, and gm(3 V)/gm_max = 0.067. It is reported only as a documented model failure |
| Referee: the confinement package's signature is "below the leverage of the fitted WTA" | The conclusion (not identifiable) holds, but the comparison mixed SS_cc with SS_min. On SS_cc, WTA +5 meV gives +0.8 and Dit ×3 gives +0.5 mV/dec, against +14.6 for the package. The signature is reproduced instead by m* ×0.8 or Nt ×1.09 [SYN-d] |
| "Numerics closed" (S6); "86 % is confinement" (S1) | Closed for 300 K transfer metrics only (§F). The confinement share is 77-86 % depending on the decomposition |

---

## B. Strongly supported physical interpretations

These rest on multiple independent lines of evidence but are not uniquely proven.

**B1. The ~4.6× apparent-mobility increase between 6.3 and 13.2 nm is a change in channel transport.**
- **Contacts:** θ_net < 0 in all films, gm still rising at 3 V at 2 nm, and a thickness-independent Rsd would need ρc ≈ 0.26 Ω·cm² (S5).
- **Electrostatics:** campaign A changes gm by ≤ 2 %.
- **Quantum capacitance:** C_eff/Cox changes by ≤ 1 % at 2 nm and 3-5 % at 6.3/13.2 nm (S3, SURR).
- **Roughness factor:** ×1.05.
- **Tail partition:** P changes 0.791 → 0.826 (S2, SURR).
- 109 % of ln(×4.58) sits in the fitted mu_band.
- *Caveat:* the Rsd bounds are calibration-class (≲5e4 Ω·µm at 2 nm, ≲1-2e4 Ω·µm at 13.2 nm).

**B2. Subthreshold conduction in all films is governed by filling of a near-Ec exponential acceptor tail.**
- One shared WTA (40 meV) reproduces the 1e-11..1e-10 slope within 2.3 mV/dec (13.2 nm after floor subtraction).
- Ideal-contact ATLAS runs reproduce the supralinear α_H (1.59 / 2.14 / 1.29) and the negative θ through trap filling alone (S5).
- An inversion validated on ATLAS curves gives measured/ATLAS DOS ratios of 0.81-1.46 near Ec (S4, mu-conditional).
- *Not supported:* the V1 DOS *form*. Deeper states are ×2.2-2.8 underestimated, and the 1e-10..1e-9 window is too soft.

**B3. Contacts do not create the thickness trend.**
- The required Rsd would drop 83 % of Vd.
- At fixed ρc the contact fraction scales as R_sh^−1/2, so a thickness-independent contact penalises the *thick* film.
- θ_net has the wrong sign in all films.
- Class: CORR + LIT (related material).

**B4. The floors are neither gate leakage (at 6.3 and 13.2 nm) nor thermal generation.**
- The 13.2 nm floor is flat within ×1.06 while V_gd changes from 1.2 to 3.7 V.
- The floor rises ×1432 (∝ t^3.85) on an identical gate stack.
- Thermal generation falls 13-17 decades short.
- Origin NOT DETERMINED.

**B5. The published mobilities are saturation-formula values taken outside the formula's regime (D12).** V1's Nt(t) exponent (the "factor of four") descends from an analysis built on those values (REVIEW 2.4; S4 §1b).

### B.6 Cross-cutting questions

**Q1. Is quantum confinement NECESSARY?**
- **No (demonstrated).** It is not required: D3 shows equal fit quality with and without it.
- **It is not identifiable.** The pure dEc term is exactly rigid. The package's only same-curve signature (+38.8 mV of non-rigidity; +14.6 mV/dec of SS_cc) is nearly reproduced by the assumed m* (×0.8) or by the fitted Nt anchor (×1.09) (D2, [SYN-d]).
- **Correction to the referee's reasoning (same conclusion).** REVIEW §1(f) compared this SS_cc signature with WTA's SS_min leverage (+12.4 mV/dec). On the same metric, WTA +5 meV moves SS_cc by only +0.8 and Dit ×3 by +0.5 mV/dec. The degeneracy is with m* and Nt, not with WTA.
- **It is physically expected (THEORY, not measured on these films).** Effective-mass Schrödinger-Poisson anchored on PBE slabs gives 0.26-0.30 V at 2 nm, bracket 0.14-0.38 V (S3 §2).
- **If it is present,** then 2 nm must carry 0.8-2.1e12 cm⁻² more positive charge than 6.3 nm, or the 6.3 nm device carries a coincident offset of that size.
- **Deciders:** the optical gap (+0.2 to 0.45 eV at 2 nm vs < 0.02 eV) or Vth(T) (the confinement offset changes by only −6 mV over 300→358 K).

**Q2. What is the origin of the 6.3 nm discrepancy?** The decomposition is demonstrated (§A.2); neither part is assigned.
- **Rigid part.** Its size is set by the choice of confinement law. Every tested physical charge fails in magnitude or in its SS signature (§D). Device spread, sweep history (0.003-0.24 V extrapolated from Januar PBS; S4 §6) and thickness error are NOT DETERMINED.
- **Shape part.** It is independent of confinement and reproduced by no tested V1 change. The most plausible cause is the constant, density-independent mobility. This is inferred from the trade-off line of 3.2-8.5 mV of gap per mV/dec of SS_cc (S6 §3.3) and is untested.
  - Alternatives: above-threshold trapping or sweep history; field quantization with local tails (S3: +0.15-0.19 V in Vg(n_s = 1e12), but this should also appear at 13.2 nm, where the model already fits).
  - The smaller same-signed misses at 2 nm (D5) point to a common model-form error that is largest at 6.3 nm.

**Q3. Do the thickness laws have a physical origin?**

| law | origin | evidence |
|---|---|---|
| dEc = 0.9205 t^-1.38 | physical at the 2 nm anchor (PBE slabs behave like an effective-mass well, α 0.59 vs a measured 0.5 eV⁻¹); the exponent is a local 3-point slope | above 2.98 nm it exceeds the infinite-well bound: ×1.59 at 6.3 nm, ×2.51 at 13.2 nm. The physical slope tends to −2. Vth impact ≤ 35 mV |
| m* = 0.208 + 0.131 t^-1.41 | plausibly non-parabolicity | 4 PBE points; enters only Nc; +14.9 mV on the 2→13.2 step (S6 §2) |
| Nt = 2e19 (2/t)^0.75 | **none** | two-point interpolation. The exponent comes from one qualitative ratio; the same paper's PBS devices imply 1.71; a surface + bulk form differs by 8 % at 6.3 nm |
| Nd_eff law | **none** | three constants from one V0 shoulder; effect ≤ 0.070 V |
| power laws in mu_FE, Ion, Vth | **none** | non-monotonic data; LOO miss ×2.63 (mu_FE, exponent 0.7516) |

No functional form in t is identified. The "step between 6.3 and 13.2 nm" describes three points; its leave-one-out "win" is circular (REVIEW V12).

**Q4. Identifiability: which parameters trade off on one ID-VG curve, and what breaks each degeneracy**

| degenerate set | observable | independent experiment |
|---|---|---|
| WF, χ, Qf, pure dEc, filled Dit, Nd·t (rigid) | Vth offset | C-V V_FB(t): a front sheet scales as t⁰, a volume as t and t², a back sheet as t/ε_s. KPFM/UPS for WF and χ |
| dEc(t) vs a t-dependent fixed charge | Vth(t) | spectroscopic Ec(t) (optical gap, IPES) combined with C-V; Vth(T) |
| mu_band vs Nt (Nt ×1.5 ≡ mu ×1.33) | Ion | gap + gm (partial); split C-V n_total(Vg); gated Hall |
| Nt, WTA, Dit, deep states, near-Ec band, back acceptors | SS, gap | T series (the subthreshold Ea gives EF − Ec without mu); multi-frequency C-V; passivation; Ds + g_b·t across more thicknesses |
| Rsd, tail exponent α, θr (r = +1.00) | gm roll-off | TLM or L-series; low-Vd ID-VD |
| mu_band lumping Rsd, C_eff/Cox (~0.87), the m* Drude term (−18 % at 2 nm) and roughness | gm | Hall; TLM; C-V |
| 6.3 nm offset: film property vs device spread vs sweep history | Vth(6.3) | 3-5 replicates (n ≈ 15.7σ²/Δ²); dual sweeps with dwell recorded |
| charge location (front / back / bulk) | second-order SS, gap | V_FB(t); vacuum vs air; passivation |
| tail energy reference under confinement (0.26 vs 0.91 V at 2 nm) | 2 nm onset | split C-V + Hall at 2 nm; T series |
| band vs percolation vs phonon transport | mu_FE(T) | T series (register §6) |

**Q5. Couplings between mechanisms**
1. **Mobility → threshold.** The CC definition converts mobility into threshold: +0.108 to 0.115 V (D6).
2. **Mobility → SS_cc.** The free-carrier capacitance puts ~60 mV/dec of mobility into the thin-film SS_cc (S4, SURR). SS_cc(t) read as a trap trend is biased.
3. **Confinement ↔ tail filling.** The tail energy reference changes the 2 nm onset by 0.65 V (S3, SURR). This is the dominant model-form uncertainty at 2 nm.
4. **Confinement ↔ Nc(m\*) ↔ SS.** m* ×1.3 gives −44 mV and −17.7 mV/dec at 2 nm (run_0050). Confinement also raises the Pd/IWO barrier at 2 nm (S5 M2).
5. **Tail density ↔ mobility ↔ gap ↔ SS.** B0 and C1 lie on one trade-off line.
6. **Donors / EF0 ↔ confinement ↔ floor.** If the floor path is ungated IWO, its ×1432 rise needs EF0 − Ec to move by only ~0.10 eV between 2 and 13.2 nm, against the 0.33 eV extrapolated dEc difference. The floor would then bound confinement and donor compensation *jointly* (S4 §5; conditional).
7. **Rsd ↔ α ↔ θ** (r = +1.00).
8. **Bias stress ↔ Nt and Vth.** PBS doubles Nt at 2 nm (Januar), so sweep history can alter both offset and shape.
9. **Floor ↔ SS extraction.** Both the SS_min window and the 13.2 nm fixed-current SS (raw 136.1 vs subtracted 91.8 mV/dec) depend on the floor.
10. **Numerical coupling.** The DOS quadrature error of Ion scales roughly with Nt(t). It is removed by recalibration, but it shows that numerics can mimic a thickness trend.

---

## C. Plausible but unverified hypotheses

| # | hypothesis | for | against / open | falsified if |
|---|---|---|---|---|
| C1 | **Material transition between 6.3 and 13.2 nm** (crystallinity, grain coalescence, percolation) that raises band mobility and effective positive charge together. *This is the working hypothesis* | Vth, mu_FE, SS_cc and floor changes co-located (CORR). A 39 meV barrier difference suffices (S2). Januar: ultrathin films "lack long-range crystallinity". Parsimony: the no-confinement reading puts the charge and mobility anomalies in the same film | no structural data at 6.3 or 13.2 nm. Kim2024 (another process) shows no step at 10-30 nm. N = 1. Parsimony is not discrimination (D3) | GIXRD/TEM show the same phase and grain size at 6.3 and 13.2 nm; **or** Hall mobility at 6.3 nm is within 30 % of 13.2 nm; **or** replicate mean mu_FE(6.3) is within 30 % of mu_FE(13.2) |
| C2 | Donor or positive-charge step at 13.2 nm (~2.5e17 → ~1e18 cm⁻³) | the no-confinement reading needs +1.39e12 cm⁻² (D3); the floor rises with t | degenerate with confinement on Vth(t) | C-V V_FB(t) flat within 50 mV across the three films |
| C3 | Confinement of 0.26-0.30 V (0.14-0.38) at 2 nm | THEORY (S3 SP + PBE) | not identifiable (D2); W may raise m* | optical-gap shift between 2 and 13.2 nm < 0.1 eV |
| C4 | The 6.3 nm rigid offset is device-specific (spread, sweep history, stress) | the PBS-extrapolated sweep shift (0.003-0.24 V) reaches the order of the 0.29 V offset at its top end | spread and sweep records NOT DETERMINED | replicates give σ(Vth) < 0.1 V with a mean ≥ 0.2 V off the shared law |
| C5 | The on-state shape needs a carrier-density-dependent (percolation-type) mobility | trade-off line (S6 §3.3); D5 at 2 nm | untested; this ATLAS version ignores MOBILITY updates between SOLVEs | a density-dependent mobility calibrated on 2 and 13.2 nm leaves the 6.3 nm gap miss > 0.1 V at SS_cc ≤ 330 mV/dec; or dual sweeps show the feature is hysteretic |
| C6 | Surface + bulk trap DOS (Ds ≈ 8.5e12 cm⁻²eV⁻¹ + g_b ≈ 1e19 cm⁻³eV⁻¹ near Ec − 0.1 eV) | inversion validated on ATLAS (S4) | the energy axis moves by kT·ln(mu ratio); 13.2 nm is valid only near −0.1 eV | multi-frequency C-V per thickness |
| C7 | Near-Ec states (C1) as a partial contributor | run_0052 recovers 33 % of the gap at SS_cc +15.6 | Ion +16 %; DOS resolution of the 20 meV band unchecked | C1 at 768 levels loses the gap gain |
| C8 | The floors are an ungated IWO path ∝ t^3.85 | order of magnitude fits (S4) | instrument floor or unpatterned film possible | IG ≈ ID, or no 1/L scaling on an L-series |
| C9 | Qf is an interfacial ionized-V_O layer | electrostatically possible | Qf is an alignment absorber (±0.2 eV of WF ≡ ±1.12e12 cm⁻²) | no C-V dispersion and no NBS response |
| C10 | MTR temperature behaviour (T-independent band mobility) | registered P-MTR variant | untested | ΔIon(2 nm, 358 K) > +5 % or < −15 % |

---

## D. Rejected explanations, each with the quantitative inconsistency

"Model-conditional" means the rejection holds within the V1 DOS and electrostatics.

| explanation | quantitative reason | class |
|---|---|---|
| **6.3 nm thickness error** (A1, run_0031) | −1 nm (to 5.3 nm) gives **+0.036 V of the required +0.294 V** (12 %). Closing the gap through dEc needs t ≈ 2.1 nm, a 67 % error. The gap stays at −0.297 V and gm at −18 %. With a physical dEc(t) the gain would be even smaller | NUM, model-conditional |
| **Fewer donors** (A2, run_0032) | **+0.030 V** (analytic bound 0.028), ×10 short | NUM |
| **Front Dit** (A4, run_0033) | ×5 gives **+0.051 V** with the gap unchanged (0.857 vs 0.862 V). It would need ×23-24 (≈7e12 cm⁻²eV⁻¹) at 6.3 nm only, on a shared gate stack | NUM |
| **Back-surface charge as the sole cause** (A3, run_0030) | matches Vth_cc (−0.017 V) but **SS_cc is off by −64.1 mV/dec**; the gap closes to 0.724 V; the offset at 1e-7 A/µm worsens to +0.285 V | NUM, model-conditional |
| **Combination** A5 (run_0035) | covers 0.215 of 0.294 V (73 %) with SS_cc −45.9 mV/dec | NUM |
| **S2 re-partition** (B0, run_0037) | on-state met, but **SS_cc 410.9 vs 295.4** and SS 1e-11..1e-10 +48.8 mV/dec | OOS (registered 18:59Z), failed |
| **S4 near-Ec band as the full explanation** (C1, run_0052) | **gap +0.119 V vs +0.28 predicted** (33 % of the 0.356 V miss); Ion +16.0 % vs ±3 %; gm −16.8 % at matched Ion | OOS (registered 19:21Z), partly failed |
| **Any rigid charge as the whole 6.3 nm miss** | the offset varies from −0.007 to +0.141 V between 1e-9 and 2e-7 A/µm (run_0015) | NUM on DATA |
| **Thickness-independent Rsd as the cause of the trend** | needs Rsd·W ≈ 1.15e6 Ω·µm at 2 nm (ρc ≈ 0.26 Ω·cm², L_T ≈ 45 µm): 83 % of Vd and 5700× the Rc of related metal/In2O3 contacts. θ_net is −0.10 / −0.12 / −0.046 V⁻¹, the wrong sign | CORR + LIT |
| **Confinement-raised Pd/IWO barrier as the step** | needs Δφ ≥ 0.20 eV; dEc(6.3) = 0.07 eV cannot give Ion(6.3) = 0.79·Ion(2) | CORR |
| **Roughness factor as the mobility step** | ×1.051 against ×4.58 needed (3 % of ln) | CAL |
| **Thickness-fluctuation scattering (∝ t⁶)** | mu(6.3) = 17 implies mu(2) = 0.017 cm²/Vs, against ~12-19 extracted (×700) | SURR |
| **Back-surface Coulomb scattering** | monotonic in t; ×2700 short at 6.3 nm | SURR |
| **Tail partition as the mobility step** | P changes by +4 %; ×4.6 would need Nt ×6.7e3 | SURR |
| **Uniform donors / neutral layer as the 6.3→13.2 Vth step** | the steepest possible slope ratio is 2.35 vs ~9-20 measured. Nd fitted to 6.3→13.2 (2.2e18 cm⁻³) predicts −0.25 V for 2→6.3 against −0.018 V measured. The floor bounds an ungated sheet at 13.2 nm to ≤ 2e7 cm⁻² | SURR + DATA |
| **Gate leakage as the dominant floor (6.3, 13.2 nm)** | ≤ ×1.06 change (13.2 nm; 6.3 nm ±45 % with no trend) while V_gd rises 1.2 → 3.7 V; ×1432 rise on an identical stack | DATA |
| **Thermal generation as the floor** | 13-17 decades short | calculation |
| **Power laws in t for mu_FE, Ion, Vth** | non-monotonic data; LOO miss ×2.63 (mu_FE), ×3.76 (Ion) | DATA |
| **dEc ∝ t^-1.38 beyond ~3 nm as physics** | exceeds the effective-mass upper bound above 2.98 nm | THEORY |
| **"Removing confinement improves SS"** | window artefact; fixed-current SS unchanged within 1-2 mV/dec | NUM |
| **"The Vth data require / refute confinement"** | one-offset rms 0.136 vs 0.133 V | NUM on DATA |
| **"Contact geometry irrelevant"** | never tested (D11) | audit |

**Not rejected (NOT DETERMINED):** hysteresis, bias stress during the sweep, device spread, measurement ambient, and thickness error beyond the model-conditional bound.

---

## E. Calibration vs validation status of every major model claim

| claim | status | evidence |
|---|---|---|
| 2 and 13.2 nm fits (Vth_cc +19 / −29 mV; Ion 0.00 %) | CAL | B1, B3 |
| 6.3 nm tuned fit | CAL (device-specific Qf and mu) | run_0015 / B2 |
| Shared laws predict the 6.3 nm threshold | **OOS, failed** (−0.294 V; mu from the V0 fit of the same curve) | run_0014 |
| 6.3 nm "reproduced in shape" | subthreshold slope yes; **on-state no** (gap −0.314 V, gm −16.6 %) | S6 §3.1 |
| Confinement accounts for the 2 vs 13.2 nm step; "it was tested" | **not supported**: realises 50.4 %; the data are neutral | D3, D6 |
| No confinement + Qf from 2 nm predicts 6.3 nm | **POST**, threshold only (−0.057 V) | A6 |
| Subthreshold follows Nt(t), WTA, Dit "without tuning" | CAL (Nt2 and WTA fitted) | brief §3 |
| mu_band per film; no mobility law | CAL | — |
| Qf rigid; WF/χ/Qf are one number; Id linear in mu; m* second-order | NUM | D2; S6 §2 |
| 300 K transfer convergence | NUM | D9 |
| V1 2 nm mesh; DOS order at 6.3 and 13.2 nm; T and ID-VD convergence | **not demonstrated** | §F |
| Physical deck ≡ reduced deck; donors and ε irrelevant at 2 nm | NUM | runs 0008/0012, 0009/0013, 0022, 0026 |
| Contact geometry irrelevant | **RETRACT** | D11 |
| A1-A5 rejected as the sole cause | NUM, model-conditional | §D |
| B0 re-partition | **OOS, failed** | SS_cc +115.6 |
| S1's B0 SS_cc 418 | POST | REVIEW 2.15 |
| C1 near-Ec band | OOS: passed on gm and SS, **failed** on gap and Ion | run_0052 |
| Rsd cannot create the trend | CORR + LIT; the bounds are CAL | S5 |
| Paper mu = saturation formula | DATA (provenance, not device validation) | D12 |
| Structural step | CORR | C1 |
| Confinement 0.26-0.30 V at 2 nm | THEORY | S3 |
| MTR surrogate vs ATLAS P-MTR (P7) | numerical cross-check | register §5.4 |
| ID-VD and 338/358 K predictions | **PRED** | register |
| Ideal Ohmic contacts, constant mobility, T-independent tails | assumed | register §6 |

---

## F. Minimum work required before submission, ordered by scientific dependency

### F.0 Originally requested items completed in this study

| item | status | runs |
|---|---|---|
| 6.3 nm hypothesis study | done; no tested mechanism explains the miss | A1-A6: 0030-0035; B0: 0037; C1: 0052 |
| DOS 384/192 recalibration | done | 0038-0040; refinement series 0019, 0029; B2 and B3 rescaled exactly |
| 6.3 nm mesh check | done, PASS | A7: 0036 |
| WF / m* isolation | done | 0048-0051 |
| ID-VD predictions | done, registered | 0041-0043 |
| Temperature predictions | done, registered in two variants (tmu caveat) | 0044-0047 |

The launch budget is exhausted (52/52). **Not done:** explicit TMUN, SP/BQP, a corrected overlap run, the V1 2 nm mesh check, DOS order at 6.3 and 13.2 nm, DOS/mesh checks at T ≠ 300 K and for ID-VD, and C1 DOS resolution. These need about 10-11 new launches.

### F.1 Checklist

Each item names what it needs first and whether it is ANALYSIS, ATLAS or LAB. *Italic* text is the limitation sentence to print if the item cannot be done.

**Tier 0: analysis only; no dependency; do now**

- **0.1 [ANALYSIS] Correct the package documents (§K).**
  - Retract run_0027.
  - Re-tabulate every table with fixed-current metrics (V(1e-9), SS 1e-11..1e-10, SS 1e-10..1e-9, SS_cc, gap, gap7, Ion/gm) in place of SS_min.
  - Give the 13.2 nm SS both raw and floor-subtracted.
  - Mandatory; no limitation sentence is acceptable.
- **0.2 [ANALYSIS] Freeze the prediction register externally (§G.3)** before any comparison data are requested.
  - *"Predictions were registered internally with SHA-256 hashes; no third-party timestamp exists."*
- **0.3 [ANALYSIS] Audit ATLAS defaults.** Use the parameter dumps in one 300 K and one 358 K `deckbuild.out`: tmu 1.5, vsat 9.78e6 cm/s, SRH/Auger, lattice constant.
  - *"Unset ATLAS material parameters took silicon defaults; the constant-mobility temperature exponent (1.5) was active in the elevated-temperature runs and is reported as a separate prediction variant."*
- **0.4 [ANALYSIS] Identifiability.** Build a Jacobian or profile over the fitted metrics from the existing one-at-a-time pairs: at 2 nm, runs 0012, 0020-0026, 0048 and 0050; at 13.2 nm, 0049 and 0051. Report which *combinations* are identified.
  - *"Identifiability was assessed only by one-at-a-time perturbations; the fitted parameter set is one member of a family of equivalent calibrations."*

**Tier 1: records and existing data; everything below depends on these**

- **1.1 [LAB/records]** Vd, current normalisation, sweep direction, rate and dwell, ranges, temperature, ambient, device IDs, IG/IS if logged, and the thickness method.
  - *"Drain bias (0.7 V), current normalisation and geometry were taken from the device schematic; sweep direction, hysteresis, temperature and gate current were not recorded; one device per thickness was measured."*
- **1.2 [LAB/records]** Januar SI: Fig. S12 (2 nm at 338/358 K, with its own 300 K curve), Fig. 5a mu_sat(6.3 nm), the MIM/MISM C-V, ID-VD S7b and the PBS in Fig. 6. Establish device identity. Needs 0.2 and 2.1-2.2 before the comparison is reported.
  - *"No measurement independent of the calibration curves was available; the model is calibrated, not validated, and its registered predictions are untested."*

**Tier 2: ATLAS, needed before a registered prediction is compared (parallel to Tier 1)**

- **2.1** Explicit TMUN: re-run B12 (2 nm, 358.15 K) with the constant-mobility temperature exponent set to 0. Expected: P-MTR within ±0.2 % in current. One launch.
- **2.2** DOS check at 358 K (B12 at a second level). One launch.
- **2.3** ID-VD mesh ×0.7 near the drain (B8), to bound Vd_sat and gd(3 V)/gd0. One launch.
- If not done: *"Elevated-temperature predictions were computed with the ATLAS default constant-mobility exponent (T^-1.5) and, by exact rescaling, for a temperature-independent band mobility; discretization convergence was verified at 300 K for transfer curves only."*

**Tier 3: ATLAS numerical closure of the calibrated state**

- **3.1** V1 2 nm deck, mesh ×0.7. One launch.
- **3.2** DOS 192/96 at 6.3 and 13.2 nm, for the observed order. Two launches.
- **3.3** C1 at 768/384 levels, or document ATLAS level placement. One launch.
- **3.4** Corrected overlap run: x.mesh beyond the electrodes, and reject any log containing "Electrode shortened". One launch. It tests geometry only; contact physics needs ρc (6.1) and a finite contact-resistance boundary (keyword to be checked in the ATLAS 5.28.1.R manual).
- If not done: *"Mesh convergence of the 2 nm deck is inherited from an earlier deck of the same generator; discretization order was established only at 2 nm; contact geometry and resistance were not tested."*

**Tier 4: replicates; needed before ANY film-specific claim**

- **4.1 [LAB]** 3-5 devices at each of 2, 6.3 and 13.2 nm, same process run, dual sweeps with rate and dwell recorded. This decides C4.
  - *"Each thickness is represented by a single device; device-to-device variation was not quantified, so the 6.3 nm threshold offset cannot be distinguished from process variation or sweep history."*

**Tier 5: thickness metrology; needed before any t-law**

- **5.1 [LAB]** XRR or ellipsometry, cross-sectional TEM, and XPS/RBS for W (with "2 % W" defined).
  - *"Channel thicknesses are nominal, without measured uncertainty; '~2 % W' is undefined; all thickness laws are evaluated at nominal t."*

**Tier 6: contacts and parasitic paths; needed before any mobility extraction (needs 1, 5)**

- **6.1 [LAB]** TLM or L-series; low-Vd output (0-0.2 V) and transfer at Vd = 0.05-0.1 V; IG and IS recorded simultaneously; mesa vs unpatterned devices. This tests the registered ID-VD shape and the floor path.
  - *"Contacts were not characterised; extracted mobilities include any source/drain resistance, which is not identifiable from one transfer curve at one channel length; bounds of ≲5e4 Ω·µm (2 nm) and ≲2e4 Ω·µm (13.2 nm) hold only within the calibrated trap model; off-state currents are not attributed to the channel."*

**Tier 7: electrostatics (needs 5, 6)**

- **7.1 [LAB]** Quasi-static, multi-frequency and split C-V per thickness. This gives V_FB(t), n_total(Vg) and a charge-referenced threshold (REVIEW 2.12).
- **7.2 [LAB]** Passivated vs air-exposed or vacuum.
- If not done: *"Flat-band voltage and the free/trapped partition were not measured; work function, electron affinity, fixed charge and any confinement shift enter as one fitted offset per curve, and the charge location is not identified."*

**Tier 8: band edge and confinement (needs 5, 7)**

- **8.1 [ATLAS]** SP/BQP with the V1 DOS at 2, 6.3 and 13.2 nm. It tests S3's P8 (+0.15-0.19 V in Vg(n_s = 1e12)) and the 2 nm tail reference. Register it before 8.2. Two to three launches.
- **8.2 [LAB]** Optical gap vs t; UPS/XPS EF − Ev; IPES.
- If not done: *"The confinement shift is an assumed input taken from PBE calculations on pure In2O3 slabs of 0.95-1.98 nm (0.14-0.38 V at 2 nm in effective-mass Schrödinger-Poisson estimates); it was not measured on IWO and cannot be distinguished from a fixed-charge offset of ~1.7e12 cm⁻² with the present data."*

**Tier 9: transport mechanism (needs 6, 7)**

- **9.1 [LAB]** T series (≥ 3-4 temperatures, 300-360 K) on all three films.
- **9.2 [LAB]** Gated Hall; GIXRD/HRTEM/SEM grain size at 6.3 and 13.2 nm and in between.
- If not done: *"Only room-temperature data were used; band mobility and tail-state density form a calibrated pair; the origin of the mobility increase between 6.3 and 13.2 nm is not determined."*

**Tier 10: functional form in t (needs everything above)**

- **10.1 [LAB]** At least two more thicknesses (3-5 nm and 8-11 nm), predicted blind with the frozen model.
  - *"No functional form in thickness is identified; the thickness laws are interpolations between two anchors."*

### F.2 Submission thresholds

- **Calibration/methods paper (no mechanism claim):** Tier 0; items 1.1 and 1.2 with the S12 comparison; Tiers 2-3. This is about 8 launches.
- **Mechanism paper:** additionally Tiers 4, 5, 7 and 8.2.

---

## G. Predictions to register now

Source: `PREDICTIONS_REGISTER.md` (registered 2026-09-24T23:24:53Z), runs 0038-0047. The primary quantities are **changes on the same device relative to its own 300 K curve**.

### G.1 Key numbers

P-MTR means a T-independent band mobility. P-phonon is the as-simulated case (mu ∝ T^-1.5).

| quantity | 2 nm 338 K | 2 nm 358 K | 6.3 nm 358 K | 13.2 nm 358 K |
|---|---|---|---|---|
| ΔVth_cc P-MTR / P-phonon (mV) | −49.3 / −27.9 | −73.1 / −40.5 | −78.9 / −46.7 | −76.3 / −56.6 |
| ΔVth_lin, both variants (mV) | −17.2 | −26.5 | −34.5 | −30.1 |
| ΔIon P-MTR / P-phonon | +0.63 % / −15.91 % | +0.99 % / −22.58 % | +2.22 % / −21.63 % | +1.52 % / −22.17 % |
| mu_FE ratio P-MTR / P-phonon | ×0.9947 / ×0.8312 | ×0.9919 / ×0.7604 | ×0.9997 / ×0.7664 | ×1.0002 / ×0.7668 |
| ΔSS 1e-10..1e-9 P-MTR / P-phonon (mV/dec) | −8.6 / +1.0 | −12.1 / +2.0 | −12.5 / +2.4 | −10.6 / −3.3 |

**Activation energies (P-MTR),** Ea at Vg 0.5 / 1 / 1.5 / 2 / 3 V, in meV:
- 2 nm: 124 / 57 / 23 / 8 / 1.5;
- 6.3 nm: 128 / 53 / 20 / 9 / 3.5;
- 13.2 nm: 63 / 21 / 8 / 5 / 2.4.

P-phonon is exactly 42.3 meV lower at every Vg. mu_FE(13.2)/mu_FE(2) goes from 4.40 to 4.44 in both variants.

**ID-VD (300 K):**
- Id(0.1)/Id(0.05) is 1.80-1.98 in all films at Vg 1-3 V, with no S-shape.
- Id(0.1)/Id(0.7) at Vg 3 V is 0.172 / 0.171 / 0.164.
- Vd_sat (10 % of gd0) is 0.43-1.80 / 0.44-1.90 / 0.68-2.30 V.
- gd(3 V)/gd0 is 0.01-0.19 % (2 and 6.3 nm) and 0.03-0.68 % (13.2 nm).
- Id(13.2)/Id(2) at Vd 0.1 V is 26.5 / 10.8 / 7.44 / 6.29 / 5.75 at Vg 1-3 V.

### G.2 Decision rules

These rules become prospective once this file is hashed (§G.3). σ_rep is the repeatability of the same device and is NOT DETERMINED; it must be measured before the comparison.

| test | outcome → meaning |
|---|---|
| ΔIon(2 nm, 358 K) | ≥ +5 %: activated band mobility or percolation (both variants and V1's constant mobility falsified). Between −5 and +5 %: P-MTR consistent. ≤ −15 %: phonon-like, P-MTR falsified. In between: report g = −ln(R_meas/R_MTR)/ln(T/300); neither variant confirmed |
| ΔVth_lin at 338 / 358 K (−17.2 / −26.5 mV; the same in both variants; the sharpest test) | pass if \|meas − pred\| ≤ max(15 mV, 2σ_rep). The 15 mV exceeds the −5 to −12 mV grid bias (S6 §1.5). A fail falsifies the equilibrium tail-filling electrostatics |
| ΔVth_cc(358 K) | inside −35 to −85 mV: tail filling is sufficient. Outside: additional T-dependent charge |
| ΔSS 1e-10..1e-9 at 358 K | an increase > 20 mV/dec means a T-dependent tail/Dit or non-equilibrium trapping |
| mu_FE(13.2)/mu_FE(2) vs T | constant within ±5 %: common mechanism. Falling toward ~3.3: supports C1 |
| Low-Vd output | Id(0.1)/Id(0.05) > 2.0 or an S-shape (especially at 2 nm only): non-Ohmic injection |
| Id(0.1)/Id(0.7) at Vg 3 V | lower than predicted by more than σ_rep and growing with Id: Rsd is present; the film ordering of the deficit locates it |
| mu_sat(6.3 nm) in Januar Fig. 5a | 3.86 cm²/Vs within the digitisation error confirms the provenance chain |

**Conceded (REVIEW U7).** The ID-VD items test auxiliary assumptions. Only the mu_FE-ratio-vs-T and Ea(3 V)-ordering tests bear on the thickness mechanism.

### G.3 Preserving prospective status

1. **Hashes checked.** All 44 files in register §10 are unchanged [SYN-c]. The register's own SHA-256 is `836ead1f731745f95e339dedff351c2cc4dae5c6cdd3979d5c992e8e3030a681`.
2. **External timestamp.** Deposit the register, `predictions_canonical.csv`, this file and their hashes with an external timestamp (an e-mail to the supervisor and an OSF/Zenodo or repository commit) **before** the S12 data are requested or opened.
3. **Never edit the register or the CSV.** The prose multiplier error (1.19665 / 1.30426 should read 1.19669 / 1.30441; the code uses the exact values) goes in a separately timestamped addendum.
4. **No refit before comparison.** Do not refit mu_band, Qf, Nt or WTA before the comparison is written. Use the unchanged extractor (SHA-256 `a7d0b236…`). If S12 exists only as figures, digitise it before viewing the predictions and record the digitisation error.
5. **Re-checks sit beside the registered numbers.** Tier-2 re-checks are reported next to the registered numbers and never replace them. A shift beyond the registered numerical uncertainty is reported as a numerical flaw of that prediction.
6. **Device identity.** Record whether the S12 device is the workbook 2 nm device (NOT DETERMINED).

---

## H. Likely reviewer criticisms and the strongest defensible response

### H.1 The eight required questions (REVIEW §1)

| question | response |
|---|---|
| (a) Are the parameters unique? | **Conceded.** WF, χ, Qf and dEc are one number (D2); mu_band trades with Nt, and Rsd with α. We call it a "calibrated, non-unique parameter set"; item 0.4 identifies the combinations; C-V, split C-V/Hall and TLM pin three of them |
| (b) Validated or calibrated? | **Conceded: calibrated.** run_0014 is a failed OOS threshold test; A6 is POST; B0 failed and C1 partly failed; mu_sat is provenance evidence. The first validation is the register against S12 (§G) |
| (c) Could the power law be accidental? | **Conceded.** All laws are two-point laws or extrapolations (Q3). The step form is equally unsupported. No functional form is claimed |
| (d) Is the 6.3 nm miss understood? | **Partly.** The *decomposition* is demonstrated: rigid 0.294 V, plus a shape part of +0.16-0.19 V that is independent of confinement (§A.2). Eight electrostatic variants, B0 and C1 are excluded quantitatively. The *cause* is not assigned |
| (e) Converged? | **Agreed: partially.** Converged for 300 K transfer (D9). Tiers 2-3 list the rest, including the solver-grid Vth_lin bias |
| (f) Is confinement demonstrated? | **Conceded: assumed** and theoretically expected, not identifiable (Q1). The residual signature is degenerate with m* and Nt, not with WTA as REVIEW argued [SYN-d]. "It was tested" is deleted |
| (g) Are contacts and interfaces separated? | **Agreed: partially.** The trend argument stands (B3). Rsd magnitude, charge location and interface vs bulk traps are not separated (Tiers 6-7) |
| (h) Is the preferred mechanism falsifiable? | **Answered.** The working hypothesis C1 has pre-declared falsifiers, and so do the auxiliaries C3, C4, C5 and C10 (§C). The register's ID-VD items are acknowledged to test auxiliary assumptions only |

### H.2 Further objections (REVIEW §2, §4)

| objection | response |
|---|---|
| 2.1 Vd and units come from the schematic | Accepted. mu_sat fixes L/(W·Cox) × A/µm, not Vd. Item 1.1 |
| 2.2 N = 1 | Accepted. No film-specific mechanism is claimed (§J). Item 4.1 |
| 2.3 Sweep history | Accepted. An open confounder of both offset and shape |
| 2.4 Mobility definition | Accepted. The regime claims of S2 and S5 are withdrawn. The paper's 60-70 mV/dec is reachable only next to the floor (the 6.3 nm 2-point minimum is 33.4 mV/dec, i.e. noise) |
| 2.5 31.8 nm | Accepted. It is a documented model failure (Id(−3 V) = 3.0e-7 A/µm), never used as support |
| 2.6 Floors | Accepted. Origin NOT DETERMINED. The 13.2 nm SS is given raw (136.1) and subtracted (91.8; model 91.2), and the subtraction is flagged as an assumption |
| 2.7 tmu | Accepted as a configuration-control failure. Both variants are exact (D10). Items 0.3 and 2.1 |
| 2.8-2.10 | run_0027 retracted, SS_min retired, overclaims corrected (§K) |
| 2.11 RMSE not comparable | Accepted. Active spans are 6.57 / 5.25 / 4.59 decades; robust metrics are given alongside |
| 2.12 CC Vth confounded | Accepted (D6). Report both; the charge-referenced threshold needs item 7.1 |
| 2.13 Extraction at Vd = 0.7 V | Accepted. mu_FE(2 nm) is a lower bound (gm_max at the last point), and Vth_lin(2 nm) depends on where the sweep ends |
| 2.14 T and Cox | Accepted. 300 K is assumed. ε(Al2O3) 7-9 moves the EOT by ~3 %, and every q/Cox charge with it |
| 2.15 Pre-registration hygiene | Accepted. A6, S1's B0 value and the KCL rule change are POST. B0 (S2) and C1 (S4) were genuinely pre-registered, and both failed or partly failed |
| 2.16 Qf read as a charge | Accepted (C9) |
| O1-O9 overstatements | All conceded (§A.3, §K) |
| U1-U7 understatements | All accepted: U1 → D5; U2 → 2.11; U3 → D4; U4 → B5; U5 → item 3.4; U6 → 2.15; U7 → §G.2 |

### H.3 Additional criticisms we expect

| criticism | response |
|---|---|
| "Three curves and ~10 fitted numbers: what is learned?" | The degeneracy map (D2-D3, Q4), the anomaly decomposition (§A.2), the quantitative exclusions (§D) and the registered predictions. Not the parameter values |
| "Is a 2 nm film continuous?" | NOT DETERMINED; Januar's AFM roughness is higher at 2 nm. Stated as a limitation |
| "Is drift-diffusion valid at 2 nm?" | For trap-free electrostatics, SP agrees within 11 mV and C_eff within 1 % (S3, SURR). With traps, the tail energy reference is a stated model-form uncertainty (0.26 vs 0.91 V) |
| "If constant mobility is the problem, why not implement a density-dependent one?" | This ATLAS version ignores MOBILITY updates between SOLVEs, and no IWO-calibrated model exists locally. So C5 stays "plausible" and is deferred (§I) |
| "The temperature data come from another device" | Identity NOT DETERMINED. Only changes relative to that device's own 300 K curve are compared |
| "The air-exposed back channel may drift" | The ambient was not recorded. Item 7.2 |

---

## I. What to leave for a second paper, and why

| topic | why not now |
|---|---|
| QE/DFT for W:In2O3 (W substitution, air/OH surfaces, tail localization length vs t) | no QE installation. Even a correct dEc is not identifiable from these data (D2); it has value only together with an optical gap vs t |
| 31.8 nm and thicker films | needs a different mechanism (Nd ≥ 3e18 cm⁻³ or a back donor sheet); the V0 fit is non-identifiable. Report it here only as a failure |
| SP/BQP with traps | changes the model form. The single check (8.1) belongs here; a trap-coupled quantum model does not |
| Density-dependent / percolation mobility | the leading candidate for the shape miss (C5). It needs T and split C-V/Hall data to be identifiable, and it cannot be emulated within a sweep in this ATLAS version |
| Off-state floor physics | needs IG/IS, an L-series and mesa devices |
| Bias-stress and hysteresis dynamics | needs dual sweeps and PBS/NBS on replicates |
| Denser thickness series and a functional form in t | needs Tiers 4-5; a step and a steep sigmoid cannot be separated with three points |
| Contact physics with measured ρc | needs TLM (6.1) |

---

## J. The strongest claims the present study can support

1. **NUM; demonstrated.**
   > "On a single transfer curve per thickness, the confinement-induced conduction-band shift, the gate work function, the channel electron affinity and a fixed interface charge enter as one rigid threshold offset (reproduced to within 1 mV in drift-diffusion simulations). A confinement shift of ~0.3 eV at 2 nm, expected from effective-mass estimates anchored on first-principles slab calculations, is therefore an assumed input, not a result, and the measured thresholds are described equally well with or without it (single-offset rms 0.136 vs 0.133 V)."

2. **DATA + NUM; demonstrated for these devices.**
   > "The 2 and 6.3 nm devices have similar thresholds and field-effect mobilities, whereas the 13.2 nm device shows a 0.56-0.58 V lower threshold and a 4.1-4.6-fold higher apparent mobility. With the calibrated tail-state and donor laws and a thickness-independent fixed charge, a single offset does not reproduce all three thresholds within 0.1 V, with or without the confinement term (largest residuals 0.19 and 0.18 V); at least one further thickness-dependent quantity is required, which the present data do not identify. About 0.11 V of the threshold difference follows from the constant-current threshold definition combined with the mobility difference."

3. **Strongly supported; model-conditional.**
   > "Within the calibrated trap-limited model, the 4.6-fold increase in apparent mobility between 6.3 and 13.2 nm cannot be attributed to source/drain resistance, interface roughness, electrostatics or tail-state filling; its physical origin, for example a thickness-dependent microstructure, is not determined by the present data."

4. **NUM on DATA; demonstrated negative result.**
   > "The 6.3 nm device departs from the shared calibration in two separable ways: a rigid threshold offset (0.29 V, equivalent to 1.6 × 10¹² cm⁻² of fixed charge) and a gate-voltage-dependent on-state shape (turn-on delay 0.31-0.36 V too small, transconductance 17-23 % too low). No tested change of fixed charge, donor density, interface, tail-state or near-band-edge acceptor density, film thickness or back-surface charge reproduces the shape without degrading the subthreshold slope. With one device per thickness, the offset cannot be distinguished from device-to-device variation, and the shape points to a limitation of the constant-mobility model."

---

## K. Corrections needed to existing package documents

Nothing has been edited. Each row gives the statement and its corrected wording.

### FINAL_STATUS.md

| statement | corrected wording |
|---|---|
| "15 real ATLAS launches" | "52 launches (run_0001-0052, RUN_INDEX.csv); run_0010 aborted, run_0011 was stopped and run_0018 timed out without currents; run_0027 is malformed and retracted." |
| "The final set is four runs" | "The final calibrated set is runs 0038-0040 (DOS 384/192; mu_band 17.69 / 11.58 / 61.60 after exact rescaling); run_0014 is the shared-parameter threshold test; runs 0012-0015 (DOS 96/48) are superseded." |
| Table SS_min column; row 0014 "VALIDATION (shared parameters, nothing tuned)" | Use fixed-current SS, SS_cc, gap and gm (S6 §1.6), and state the 13.2 nm floor subtraction. Row 0014: "shared-parameter out-of-sample threshold test (mu_band 12.4 = V0 fit of the same curve): failed, −0.294 V." |
| "ONE fitted electrostatic value … Everything else is a law or a literature/measured value" | "Fitted: shared Qf; the 6.3 nm Qf; mu_band ×3; the Nt anchor and WTA; the Nd-law constants (V0). Assumed: WF, χ, Dit, deep Gaussian, ε(Al2O3)." |
| "reproduced in SHAPE (SS_min 108 vs 115 …)" | "Subthreshold slope at fixed current reproduced (−2.2 mV/dec); on-state shape not (gap −0.314 V, gm −16.6 %)." |
| "+27 % on-current is the consequence of that overdrive error, not of the mobility" | "About three quarters (log share) of the +26.8 % follows from the threshold miss, one quarter from the mobility choice (12.4 vs 11.69)." |
| "fits to 0.063 dec … as well as the other two"; "one electrostatic number is all it misses" | "One offset removes the threshold miss (+7 mV); Vth_lin still misses by −0.349 V and gm by −23 %. log-RMSE is not comparable across films (spans 6.57 / 5.25 / 4.59 dec)." |
| Conclusion 1 (confinement "accounts for" the 0.58 V; offsets "agreeing to 40 mV") | "With the DFT-proxy confinement law, one shared offset brings 2 and 13.2 nm within 30 mV and misses 6.3 nm by 0.29 V; without it, one offset fitted on 2 nm brings 6.3 nm within 60 mV and misses 13.2 nm by 0.25 V. The thresholds do not discriminate the readings (one-offset rms 0.136 vs 0.133 V). The realised confinement term is 0.29 V (50 % of the measured step). The law-only offsets were +0.333 and +0.287 V (47 mV apart). Confinement is an assumed input, not a result." |
| Conclusion 2 "without tuning" | "with a fitted tail anchor and width; the 1e-11..1e-10 A/µm slope is reproduced within 2.3 mV/dec (13.2 nm floor-subtracted); the 1e-10..1e-9 slope is too soft by +20 / +6 / +25 mV/dec." |
| "Not run: work-function and m*-only cases, any sensitivity at 6.3 nm" | "Run 2026-09-25: 0030-0036 (6.3 nm), 0048-0051 (WF, m*); ID-VD and 338/358 K predictions 0041-0047 (registered; tmu = 1.5 caveat)." |
| "publication-ready as a calibrated, thickness-resolved TCAD parameter extraction" | "A calibrated, explicitly non-unique TCAD description of three single devices; not a parameter extraction; not validated; submission requires SYNTHESIS §F Tiers 0-3." |

### SENSITIVITY_RESULTS.md

| statement | corrected wording |
|---|---|
| overlap_4um (run_0027) "MEASURED IN ATLAS" | "RETRACTED: malformed deck (x.mesh ends at 24 µm; drain collapsed; 'Electrode shortened' ×3)." |
| NOT RUN: WF, m*, 6.3 nm | "Superseded. WF +0.1 eV: +0.100 V rigid, SS unchanged, ΔIon −6.8 % / −5.0 % at 2 / 13.2 nm vs the same-mu baselines (runs 0048/0049). m* ×1.3: −0.044 / −0.029 V, SS_cc −17.7 / −13.2 mV/dec, ΔIon +4.1 / +5.8 % (0050/0051). 6.3 nm: 0030-0036." |
| dSS_min column (e.g. mu_band "−9.89"; no_confinement "+10.7 / −12.7") | Add a note: "SS_min is window-phase sensitive (±10 mV/dec; S6 §1.4); these values are extraction artefacts; fixed-current SS changes are ≤ 2 mV/dec." |

### NUMERICAL_CONVERGENCE.md

| statement | corrected wording |
|---|---|
| V0 checks "apply to the V1 decks" (A, B at 2 nm) | "Carried over by lineage; not re-demonstrated on the V1 2 nm physical deck (open)." |
| C' "FAIL"; C "DOS x4 not run" | "Resolved by recalibration at 384/192 (0038-0040). At 2 nm: order 2.03, residual +0.16 % Ion. Offsets at equal mu +2.48 / +0.95 / +0.50 %; Vth_lin −22 mV at 2 nm. The order is not established at 6.3 and 13.2 nm." |
| L "OPEN" | "PASS (run_0036: 0.0625 vs 0.0626 dec; ΔVth_cc −0.3 mV; Ion −0.03 %)." |
| G' "PASS after documented rule change" | add: "The rule was changed after the original rule failed; both rules and both verdicts are reported." |
| (missing) | Add rows: no DOS/mesh checks for T ≠ 300 K or for ID-VD; C1 band resolution unchecked; the 0.1 V solver grid above 1.5 V biases Vth_lin by −5 to −12 mV; SS_min invalid; the runner does not gate on geometry warnings. |

### LIMITATIONS.md

| item | corrected wording |
|---|---|
| #1 | add: "The t^-1.38 extrapolation exceeds the effective-mass bound beyond ~3 nm (×1.59 at 6.3 nm; Vth impact ≤ 35 mV)." |
| #4 | add: "Gate leakage is rejected as the dominant floor at 6.3 and 13.2 nm on trend grounds; the origin is still NOT DETERMINED." |
| #5 "~12 → ~57" | "11.58 → 61.60 cm²/Vs (DOS 384/192). The constant, density-independent mobility is the most plausible cause of the unreproduced on-state shape." |
| #6 "reproduces the subthreshold shape (SS_min 108 vs 115) … removes the miss" | "Reproduces the fixed-current subthreshold slope but not the on-state (gap −0.314 V, gm −16.6 %); the tuned run removes the threshold miss only." |
| #10 "the only form of partial validation" | "The 6.3 nm test is out-of-sample for the threshold only (mu_band = V0 fit of the same curve) and failed by −0.294 V; the registered predictions are untested." |
| #11 "2 um overlap … insensitive" | "Contact geometry and resistance are untested (run_0027 malformed; ideal Ohmic boundaries cannot represent ρc); Rsd is bounded only within the calibrated trap model." |
| #13 "DOS-level doubling … 1.1 %" | "+2.0 % (192/96) and +2.5 % (384/192) at 2 nm on the V1 deck; resolved by recalibration." |
| #14 | add: "The mu_sat reproduction confirms L/(W·Cox) and A/µm jointly, not Vd." |
| #15 (misnumbered): "differing by 1.6e12"; "4 um overlap change nothing"; "Not run: …" | "1.39e12 cm⁻², while with the law 6.3 nm needs 1.64e12 (symmetric)"; retract the overlap statement; the "not run" items are superseded. |
| (new) | "One device per thickness; elevated-T runs used the ATLAS default tmu = 1.5 (two variants reported); SS_min retired; 31.8 nm is a documented model failure." |

### SUPERVISOR_SUMMARY.md

| statement | corrected wording |
|---|---|
| SS column (SS_min); 6.3 nm row "validation: shape right, threshold 0.29 V off" | Fixed-current SS. "Shared-parameter threshold test failed (−0.29 V); on-state shape also missed (gap −0.31 V, gm −17 %)." Tuned row: add "Vth_lin −0.35 V, gm −23 %." |
| "Free quantities: one shared fixed charge …" | list all fitted quantities (as in FINAL_STATUS) |
| #1 "The confinement story holds … it was tested … 1.6e12 … contact geometry [is] irrelevant" | the FINAL_STATUS Conclusion 1 wording, plus "donors and permittivity change the 2 nm result by < 2 % (runs 0022, 0026); contact geometry was not tested." |
| #2 "a real discrepancy, not a fitting failure … same quality as the other two" | "One number removes the threshold part but not the on-state shape. With one device per thickness the offset cannot be separated from device variation or sweep history, and without the confinement law it would be 13.2 nm that needs its own charge." |
| "all 14 launches" | "52 launches" |
| "What would make it predictive" | add: instrument records, 3-5 replicates per thickness, and comparison of Januar SI Fig. S12 with the frozen register |

### Other documents

None of these may be edited in place; record the corrections separately.
- **EVIDENCE_BRIEF.** §4: 1.434e12, not ~1.86e12. §5b: 13.2 nm ΔIon is −4.99 / +5.79 % relative to B3.
- **S1.** §3.1: A7 PASS. B0's 418 is POST. The conclusion should read "equally described with or without the confinement law".
- **S2.** The re-partition is rejected (B0). Withdraw "linear regime", "confirmed to three significant figures" and "does not need the lab". The 31.8 nm "mu_FE" is not a mobility.
- **S3.** "Mildly disfavour" should read "do not discriminate". A6 is POST.
- **S4.** 6.3 nm floor ±45 %, not ±3 %. The Qf magnitude is not a donor measurement. The SS_min reading is an artefact.
- **S6.** P2 is POST. Numerics are "closed for 300 K transfer metrics". #5 "A6 favours no-QC" should read "neutral".
- **PREDICTIONS_REGISTER.** The multiplier prose fix goes in an addendum only (§G.3).
