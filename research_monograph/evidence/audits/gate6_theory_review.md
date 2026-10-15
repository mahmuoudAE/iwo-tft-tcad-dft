# Gate 6 review 1: referee report on the theory chapters (M04, M04b, M05, M06; M07 mobility check)

Reviewer: independent subagent, read-only, 2026-10-14. Report reproduced verbatim below; the disposition of each
finding (verified by the main session before any edit) is at the end. Line numbers refer to the draft before the
Gate 6 corrections (commit ab428e8).

---

Referee report on M04, M04b, M05, M06 (plus the M07 mobility check). Read-only, no files changed. I opened no blinded paths; aIWO_ names appear only as text inside M06. Numbers below are my own recomputations (Python, scratchpad).

## Findings, most severe first

**1. ERROR — M04b:98–104 and keyresult 193–194.** Quote: "The production force noise, about 10^-3 Ry/bohr, is of the same size as the relaxation threshold itself."
- QE's "Total SCF correction" is a norm over all atoms. RESULTS_LOG 2026-10-11 10:41Z says so explicitly: "norm over all atoms". M04b:115 applies exactly this norm-to-component conversion to the total force.
- Per component, 1.3e-3/√414 = 6.4e-5 Ry/bohr. That is about 15 times below the per-component threshold of 1e-3. The log itself says "RMS ΔF of 6.7e-5 is at that noise level."
- The C036 restart mismatch (max |ΔF| 4.99e-3 per component) is larger than the whole norm, so SCF tolerance cannot be its explanation. FACT-073 says "cause open".
- "Confirmed by the logged checks" rests on two different cells, with different smearing and β. The same geometry gives 1.3e-3 with MV and 5.6e-4 with Gaussian at equal conv_thr, so the prefactor depends on the system. The 1e-14 values were recomputed, not printed (both print 0.000000).
- A same-cell pair exists and should be used: aIO_1p0_s1 gives 1.3e-3 at 1e-7 (log 13:36Z).
- Fix: "The SCF correction (a norm over all 3N components) is 1.3e-3 Ry/bohr at 1e-7, i.e. ~6e-5 Ry/bohr per component, about 15 times below the threshold. Same-cell ratio 1e-7→1e-14 ≈ 3700 vs √1e7 = 3200 is consistent with δF ∝ √conv_thr. The C036 restart discrepancy exceeds this noise; its cause is open."
- Also M04:218: add that the 2.4e-4 smearing screen is at the SCF-noise resolution (RMS 6.7e-5).

**2. ERROR (logic) — M05:166–169 and keyresult 233–235.** Quote: "The difference, about 40 meV at 2 nm, is of the same size as the spread between alignment routes: at 2 nm … −0.054 and −0.049 eV".
- The 2 nm route spread is 5 meV, and the plateau is flat within 8 meV (13_dft_rev:1720). A 40 meV deviation is 5–8 times larger, so it is resolved against the stated route uncertainties.
- The 29 meV spread exists only at 1 nm, and it uses a two-step value that M04b:162 declares invalid there ("no such interior").
- The single-band EMA estimate is also inconsistent with the chapter's own non-parabolic CB. The hole confinement energy should be ε1·m_e/m_h, with ε1 = ΔEc(1+αΔEc), not ΔEc·m_e/m_h.
  - At 1 nm this gives ΔEv = −0.061 eV and a CB share of 0.93. Computed: −0.052 and 0.94, so EMA agrees.
  - At 2 nm it gives −0.016 eV and 0.95, against computed −0.054 and 0.84.
- Fix: "At 1 nm Kane-consistent EMA (−0.061 eV, share 0.93) agrees with the computation. At 2 nm the computed ΔEv exceeds EMA by ≈38 meV, 5–8× the route spread and plateau flatness. This deviation is unexplained; only a systematic common to both routes (bulk reference, termination dipole) could remove it."

**3. ERROR — M05:38–41.** Quote: "A finite barrier does not rescue it … decay length … ≈0.1 nm, is far too small to explain the factor 2.3."
- With the F′/m continuity condition the chapter itself states (line 26), the even-state condition is tan(kt/2) = (m_b/m_vac)(κ/k).
- The effective penetration per side is therefore ≈(m_vac/m_b)/κ = 6.5 × 0.098 = 0.63 nm, not 0.1 nm.
- Solved exactly (parabolic, m_b = 0.1541, m_vac = m0, V = 4 eV): E1 = 0.251 eV at 1.962 nm (computed 0.281; infinite well 0.634), so t_eff/t = 1.59. At 0.930 nm, E1 = 0.625 eV.
- So the magnitude of the factor 2.3 is within reach of a finite-barrier envelope model. The real conclusion is that the boundary condition at an OH/vacuum surface is undetermined.
- Fix: "The result depends on the boundary condition: with F′/m continuity and m0 outside, a 4 eV barrier lowers E1(1.96 nm) to 0.25 eV. The envelope model is therefore not predictive, not refuted."
- Note: the Kane box widths in the table give t_eff − t = 0.77 nm (2 nm) and 0.46 nm (1 nm), so a constant penetration does not fit all thicknesses either.

**4. OVERCLAIM — M05:138–143, 228–231.** Quote: "The mass increase is a bulk band-structure effect … not a surface or termination effect."
- Of the "within 2% at three thicknesses", two are flagged non-model films:
  - 0.461 nm has ΔEc = 1.585 eV, 3.5 times beyond the 0.45 eV Kane fit window.
  - At 0.695 nm the ±0.17 eV on ΔEc moves m_pred by ±2·m_b·α·0.17 = ±0.030 m0 (±9%).
- Of the two in-model films, one agrees (0.7%) and one is off by 10%.
- Lines 148–149 contradict the mass test. "The computed band flattens more than the bulk Kane band at large k_z" would make m∥ = ħ²k/(dE/dk) heavier than Kane. The computed 1 nm mass is lighter (0.279 vs 0.306), i.e. less non-parabolic.
- Fix: "consistent with the bulk non-parabolicity at 2 nm; 10% off at 1 nm; the other two films do not test it." Replace the band-flattening sentence by a direct comparison with the computed bulk [001] band beyond 0.45 eV (bands_path is available), or by "box width or band shape; the data cannot separate them".

**5. MISSING-CAVEAT (borders on ERROR) — M06:39–43 and keyresult 191–193.** Quote: "For a film between Al2O3 (ε≈9) and air this mean is 5 … upper bound of about 0.45 eV … several times the bulk value."
- The device has only 2 nm of Al2O3 on 15 nm of HfO2 (ε = 19.57), with air above (03_device_data_rev:65–70).
- 2 nm is comparable to r0 (2.1 nm) and the 2-D donor radius (1.3 nm). Beyond it the substrate side is effectively HfO2: (19.57+1)/2 = 10.3 ≈ ε_s = 10.55, giving E_2D = 0.107 eV, i.e. essentially no dielectric enhancement.
- At 0.1–0.45 eV binding exceeds ħω_LO, so static ε_s is no longer the right screening. Non-parabolicity raises the mass. Both effects increase the binding, so "upper bound" is not strictly correct.
- Fix: state the real stack. The dielectric term is small for the HfO2-backed side; quantum confinement alone gives at most 4× (≈2× at t ≈ 0.75 a_B). Call 0.45 eV "an estimate for an Al2O3/air environment, not this device".

**6. OVERCLAIM — M06:60–62.** Quote: "the cells sit at the doping limit, where the resonance is being filled."
- The baseline is more careful (13_dft_rev:1287–1288): "whether band filling pins it there would need a density series".
- 0.1 eV is below the MV width (0.136 eV).
- A partially occupied narrow level necessarily lies at E_F, so this coincidence is not independent evidence.
- "Doping limit" is a thermodynamic (compensation) concept, while the filling here is forced by cell composition.
- Fix: "at the cells' forced filling (1.4–3e21 cm^-3) E_F has reached the resonance; whether it pins E_F at lower density is not computed."

**7. ERROR / OVERCLAIM — M06:179–183.** Quote: "complete activation would give of the order of 6×10^20 … The difference … must come from compensation … or from donors that are not activated".
- The baseline says ~1e21 (13_dft_rev:1280).
- W⁶⁺ on an In site (3 e/W, as M04b and M06:29 state) at 2% of cations gives 3 × 5.85e20 = 1.75e21. The 6e20 figure assumes 1 e/W, which is a property of the amorphous cells.
- "2% W" has no defined basis (03_device_data_rev:287).
- C016 itself says N_D,eff is "not identifiable from I_D–V_G". A fitted TCAD parameter also absorbs interface charge, trap DOS and work-function errors, so it cannot carry "must".
- Fix: "Full activation of 2% (cation basis, basis undefined) W⁶⁺ gives up to ~1.8e21 cm^-3. The fitted N_D,eff is lower by 3–4 orders, but it is not identifiable, so the gap is compatible with compensation, incomplete activation, or model compensation by other fitted quantities."

**8. ERROR (attribution and method) — M04b:118–119 and 39–41.**
- Quote: "Variable-cell relaxations (Wentzcovitch dynamics, Wentzcovitch1991) relax the bulk lattice". The inputs use cell_dynamics='bfgs' (cern_htcondor/results/slab2_relax_c2/vcrelax.in) and the vc-relax default bfgs (bulk_In2O3_protocol/vcrelax_ecut71_k3.in). Wentzcovitch dynamics (damp-w) was not used.
- "Variable-cell relaxations use a modified kinetic functional or a higher cutoff" implies the project did. The bulk vc-relax used neither: 71 Ry, no qcutz. The Pulay stress is bounded only by the 1 kbar pressure-convergence criterion. Say so.
- M04b:114 gives forc_conv_thr 1e-3 / etot 1e-4, but the bulk vc-relax used 1e-4 / 1e-5.

**9. MISSING-CAVEAT / OVERCLAIM — M05:55–65.**
- The VBM at Γ is dipole-forbidden (M04:127). The two-band Kane gap is therefore the gap to the dipole-allowed valence states, not the fundamental gap. This changes E_P (≈14 eV for an optical gap ~3.6 eV instead of 10.7) and can reverse "remote bands reduce the non-parabolicity".
- The measured 0.208 m0 may include polaron renormalisation: Fröhlich α ≈ (1/ε∞ − 1/ε_s)√(Ry·m/ħω_LO) ≈ 1.0 for ε∞ ≈ 4, ħω_LO ≈ 70 meV, giving m_pol/m ≈ 1+α/6 ≈ 1.17. That could account for much of the "26% below".
- E_P is not functional-invariant: PBE gives 4.9 eV, while HSE gives ~10 eV with the HSE masses.
- Fix: "Masses cannot be scaled from gaps at fixed E_P." Drop "not controlled by the gap in the two-band way". Add both caveats.

**10. OVERCLAIM — M04:79 and keyresult M04b:188–195.**
- M04:79 says "every approximation … apart from numerical ones, is an approximation of [E_xc]". That is false: frozen core and pseudopotentials (NC vs PAW gap differ by 32 meV, FACT-032), static nuclei, scalar relativity without SOC, and the spin-unpolarised restriction are physical approximations.
- The keyresult's "five approximations whose size can be stated" omits:
  - spin polarisation: A20(i) UNASSESSED; FACT-046 gives moments of 0.62/0.74 μB;
  - SOC for W 5d levels;
  - W concentration and supercell size;
  - static-lattice gap and mass renormalisation, which matter for every comparison with experiment.
- "Adiabatic separation negligible" is unquantified, and the W cells are metals, not "closed-shell" (M04:41).
- Plane-wave counts agreeing within 0.15% checks a geometric formula, not basis convergence.
- The amorphous geometries were relaxed at 60 Ry, below the cutoff that met the criteria; their geometric error is not estimated.

**11. OVERCLAIM — M05:150–152.** Quote: "within 10% the first follows from the second".
- That holds for the total mass m, not for Δm. Kane Δm from the ΔEc law is 0.152 vs the law's 0.126 at 0.93 nm (+21%).
- The exponents differ (1.478 vs 1.2755), giving 18% divergence at 6.3 nm.
- Fix: "m within 10% (Δm within 21%)".

**12. MISSING-CAVEAT — M05:220–226.**
- The spacings at 6.3 and 13.2 nm extrapolate a 2-point law 3–7 times beyond its data. The law has p = 1.48, while a Kane band tends to p → 2.
- Using the 1.39·t Kane box instead gives 0.088 eV (3.4 kT) at 6.3 nm, not 0.14 eV (5.3 kT). FACT-025 already gives a ΔEc(6.3) range of 0.050–0.075 eV.
- The criterion E2−E1 ≫ kT ignores degenerate filling (E_F − E1).
- Line 223 says "10–18%". At 1 nm I get 1.367 vs 1.50 eV, i.e. 8.9%, so write "9–18%".

**13. MINOR — M04:200–202 (MV smearing).** The y > 1/√2 condition is sufficient but loose. Exact values:
- f̃ changes sign at x = (ε−μ)/σ ≈ 0.92;
- its minimum is −0.083 at x = √2;
- f̃(0) = 0.60.
State these values.

**14. MINOR — M04b:140–145.**
- The 0.095 eV drop is the unscreened vacuum field times t. Inside the film the field is screened (ε∞ ≈ 4 gives ~0.02–0.03 eV), so it is an upper bound.
- Δφ = slope × c assumes an unscreened field through the slab. With (c − t)·slope the step is ≈0.35–0.37 V instead of 0.44 V.

**15. MINOR (references).**
- M06:88: Lany2007 (PRL 98, 045501) is GGA+U with corrections, not a hybrid-functional study. Reword to "first-principles studies".
- M06:57: Swallow2020 is Mo-specific. Cite a W source or say "by analogy for W".
- M06:109: please confirm that Varley2012 reports a stable self-trapped hole specifically in In2O3, and give its self-trapping energy (low-confidence check).
- M04:56: the constrained search needs Levy 1979 / Lieb 1983.
- M06:39: r0 needs Rytova/Keldysh 1979.

**16. MINOR — M06:31.** "Two to three orders" is right for the amorphous cells (6e20/9.1e17 ≈ 660). The crystalline cells are 1.5–3.3×10³ times above (3.2–3.5 orders).

**17. MINOR — M05:184–190.**
- α_HSE mixes the PAW-PBE gap (0.889) with the NC-HSE gap. The consistent NC pair gives 0.253.
- The model ratio is E1^HSE/E1^PBE, while the computed r is a ΔEg ratio. Say so.

**18. MINOR — M05:211.** The deck Δm of 0.046 does not follow from the chapter's law (0.0473 at t = 2.0; 0.0485 at t_HH = 1.962). Name the deck law and basis; the 4-point vs 10-point basis differs per FACT-006.

**19. MINOR (small fixes).**
- M04:33–37: the second sum includes the diagonal (k = k′) adiabatic correction. "Non-adiabatic couplings" covers only k′ ≠ k.
- M04:170: the density lacks the spin factor 2 (f ≤ 1 per spin, as N_ex = N_el − 2N_VB implies).
- M04b:23: 8^{3/2} = 22.6 is relative to the wave-function basis; relative to the 4Ecut default it is 2^{3/2} = 2.8.
- M04b:87: conv_thr 1e-8 is a loosening (other runs used 1e-9), not a remedy for sloshing.
- M05:142: "6–19%" should read 7–19% (JSON: −6.9 to −18.8%).
- M04b:184: the exact-exchange cost scales with N_q·N_occ, not N_q·N_b.
- M06:173–174: "the scale on which a W-centred trap would act" applies only to deep d-like traps; shallow traps (nm scale) are invisible.

## VERIFIED
- **M04:**
  - κ: 0.0765 (O), 0.0468 (In).
  - Coupled BO equation.
  - HK inequality.
  - KS double-counting energy.
  - E_g = E_g^KS + Δxc.
  - PBE: κ = 0.804, μ = 0.21951, s definition.
  - HSE erfc/erf split; QE defaults 0.25 and 0.106 bohr⁻¹ (input nqx = 1 confirmed).
  - Gaussian E0 = (E+F)/2 (a = g(μ)σ²/4).
  - MV occupation formula (integration checked).
  - Smearing widths in meV.
  - HSE/NC-PBE factor 2.29.
  - Lattice +1.87%.
- **M04b:**
  - N_pw = ΩE^{3/2}/6π²; all four table rows (37315, 74631, 253981, 327622).
  - Band counts for all four cells and the In56O96H24 slab.
  - Two-step formula.
  - 1 nm EA/IP route (0.8477/−0.0521, closure to 0.8998).
  - Δφ = 0.442 V, 0.262 eÅ, 1.26 D, 0.0945 eV.
  - Cost factors 2.67 and 5.5; 3.56 GB.
  - 6.1e-3/√288 = 3.6e-4.
  - Ratio 3700 vs 3162.
- **M05:**
  - 0.37603 eV nm²; 0.634 eV; 0.098 nm decay length.
  - Kane α (0.81), E_P = 4.88, 0.302 m0, 10.7 eV.
  - p(E) exponents; m∥ = m_b(1+2αE); α∥ = α/(1+2αE), which is exact.
  - Every table entry against the JSON; t_eff = 2.731 nm; exponents 1.478/1.619/1.323.
  - HSE r range 0.988–1.165.
  - N_c prefactor 2.5094e19; 15/4 factor (1.0562).
  - N_2D = 1.0799e13 (m/m0) cm^-2; 1.373e19 and 3.218e18 (for m = 0.2543); kT ln 4.27 = 37.5 meV.
  - Spacings 0.588 / 0.136 / 0.049 eV.
- **M06:**
  - E_D 25.4 meV; a_B 2.68 nm; n_c 9.09e17; E_2D 0.102 eV; ε = 5 bound 0.453 eV; r0 2.11 nm.
  - Formation-energy and transition-level formulas.
  - PR_n table; N_eff = 3.43.
  - FACT-082 capacities 2.04/0.73 e.
- **M07:**
  - μ_sat = μV_D/(2V_ov − V_D) derivation and its validity condition V_ov ≤ V_D.
  - Predicted ratios 0.474 / 0.225 / 0.676. The text's "0.23" rounds 0.2249 up; 0.22 would be exact.

---

## Disposition (main session, 2026-10-14)

Each finding was checked against the cited source or recomputed before any edit. Correction IDs refer to appendix MG,
section "Corrections made in the monograph's own review (Gate 6)".

| # | Disposition | What was done |
|---|---|---|
| 1 | Accepted (verified: RESULTS_LOG "norm over all atoms") | M04b rewritten with the same-cell pair and per-component noise; C036 cause left open; M04 smearing screen notes the SCF-noise resolution. V1 |
| 2 | Accepted (recomputed: −0.061 / −0.016 eV) | M05 partition rewritten; confinement_analysis.py adds the Kane-consistent EMA; FACT-029, M002, MS-02 updated. V3 |
| 3 | Accepted (recomputed: 0.251 / 0.625 eV) | M05 validity paragraph rewritten: envelope model not predictive, not refuted. V4 |
| 4 | Accepted | M05 test items, key result; M004, MS-04, M01, M09, M15 and the manuscript reworded (1 % at 2 nm, 10 % at 1 nm). V5 |
| 5 | Accepted (device stack verified) | M06 dielectric paragraph and key result; M006 reworded. V6 |
| 6 | Accepted | M06 resonant-donor paragraph. V7 |
| 7 | Accepted | M06, M11 and the manuscript give 6e20 to 1.8e21 cm^-3 (one to three electrons per W) and treat the comparison as an argument of scale (C016 not identifiable). V8 |
| 8 | Accepted (input files checked; bulk pressure criterion is 0.2 kbar, not 1 kbar) | M04b: BFGS cell dynamics, bulk thresholds, Pulay-stress statement. V2 |
| 9 | Accepted | M05: dipole-forbidden VBM caveat, polaron caveat (stated as about half of the 26 %), E_P not invariant. |
| 10 | Accepted | M04 approximation sentence and M04b key result rewritten (unsized approximations listed; 60 Ry amorphous relaxations noted). |
| 11 | Accepted | M05 consequence item (Δm within about 20 %). |
| 12 | Accepted (recomputed 0.088 eV, 0.021 eV) | M05 subband paragraph and key result; "9–18 %". V10 |
| 13 | Accepted at the time; SUPERSEDED by V12 (2026-10-15) | The reviewer's numbers were correct for the monograph's printed formula, but that formula was the mirror image of the Quantum ESPRESSO weight. Correct values: 0.40 at μ, never negative, maximum 1.083 at x = −√2 (V12). |
| 14 | Accepted | M04b dipole paragraph (0.35–0.37 V; 0.095 eV as upper bound). |
| 15 | Accepted in part | Lany2007 reworded; Swallow2020 "by analogy" for W; Varley2012 kept after checking its abstract (In2O3 is among the oxides with self-trapped holes favoured; self-trapping energy not given in the abstract); Levy1979 and Lieb1983 added (DOI-verified); r0 cited to Cudazzo2011 (DOI-verified) instead of Rytova/Keldysh, which could not be DOI-verified. |
| 16 | Accepted | M06 and M10: "about three orders of magnitude (660; 1500–3300 times)". |
| 17 | Accepted | confinement_analysis.py uses the NC-PBE gap (α_HSE 0.253; r 0.98–1.16); FACT-029a regenerated; M05 notes E1 ratio vs ΔEg ratio. |
| 18 | Accepted | M05 names the deck law (0.1114 t^-1.2611, deck basis); M09 deck-basis value at 2.0 nm corrected to 0.046. |
| 19 | Accepted (all seven) | M04 Born–Oppenheimer sum, spin factor; M04b 8^{3/2} reference, conv_thr wording, N_q N_occ; M05 "7–19 %"; M06 deep vs shallow traps. |
| Verified list, M07 | Accepted | M07 predicted ratio 0.23 → 0.22. |
