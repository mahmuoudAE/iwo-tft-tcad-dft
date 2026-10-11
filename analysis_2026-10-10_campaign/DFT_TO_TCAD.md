# From our DFT to TCAD inputs (campaign 2026-10-10)

**Purpose.** List every TCAD-relevant quantity in the DFT we already have, and turn each into an ATLAS input. For each one, say whether V2 already uses it.

**Scope.** No new DFT and no ATLAS run were made. Every number was re-read from the Quantum ESPRESSO output files by `dft_to_tcad_extract.py`, which is in this folder. Codex checked the numbers independently (§2).

**Labels** (charter §3):
- COMPUTED: from our DFT output files.
- MEASURED: measured on the target devices.
- LITERATURE: from a cited publication.
- FITTED: fitted to named data.
- ASSUMED: chosen without data.
- CALCULATED: a closed-form formula applied to labelled inputs.
- MODEL: a simple physical model whose parameters were fitted to COMPUTED points.

A law fitted only to DFT points is labelled "FITTED to COMPUTED DFT points". It contains no device data, and nothing here is validation against the devices.

## 1. Bottom line

1. **Conduction-band shift.** The confinement shift of the conduction band, ΔE_c(t), is the main DFT input to the TCAD. V2 already uses it at 1 and 2 nm.
   - New point at 0.695 nm: ΔE_c = +1.059 eV.
   - The 2 nm value was re-computed: +0.281 eV.
   - The HSE06 check raises ΔE_c by a factor of 1.06–1.11, i.e. +17 to +31 meV at 2 nm. This assumes the ratio measured at 1 nm transfers to other thicknesses.
2. **Thick films are extrapolated.** No slab is thicker than 2 nm, so the values at 6.3 and 13.2 nm come from fitted laws. Depending on the law, ΔE_c is 0.046–0.062 eV at 6.3 nm and 0.013–0.024 eV at 13.2 nm (PBE).
3. **New candidate: a quasi-2D density of states.**
   - DFT puts the second subband 0.72 eV above the first at 2 nm (1.50 eV at 1 nm), far above kT. So at 2 nm and below, the film carries a single subband.
   - The matching effective density of states is N2D/t = 1.38e19 cm⁻³ at 2 nm. That is 4.3 times the 3-D value V2 uses (3.24e18 cm⁻³).
   - This equals a band shift of −37.5 meV, or about −55 mV in V_G at the 2 nm subthreshold slope. This is an estimate, not an ATLAS result.
   - At 6.3 nm the effect is ×1.5 (MODEL), and at 13.2 nm it is about ×0.9.
4. **The DFT band inputs cannot explain the 6.3 nm failure.** Their combined uncertainty at 6.3 nm is about 0.03 eV:
   - ΔE_c spread: 16 meV;
   - HSE scaling: about 7 meV;
   - change in the density of states: about 10 meV.

   The 6.3 nm threshold misses by 0.29 V (rigid part, V1) and by 0.23–0.37 V (V2 T3) [INFERRED].
5. **The mass cannot explain the mobility trend.** DFT gives m*(2 nm)/m*(13.2 nm) = 1.20. At constant scattering time this lowers the 2 nm mobility to 0.83 of the 13.2 nm value. The fitted μ_band ratio is 0.28 [INFERRED].
6. **W is a fully ionized, resonant donor.** In all four W cells (PBE), the W-5d-rich level lies 1.2–1.8 eV *above* the host conduction-band bottom.
   - In the 2 nm W slab (1.8 % of the cations are W, the composition closest to the devices), 97 % of the three donated electrons are in the host conduction band. Only 3 % project onto W 5d orbitals.
   - So W adds no gap state and no electron trap. The effective donor density must stay FITTED, because compensation was not computed.
7. **Surface states.**
   - The conduction-band edge is an interior state at every thickness from 0.695 nm up.
   - The valence-band edge becomes an OH surface state at 1 nm and below, and in the 2 nm slab once W is added.
   - In an electron-only TCAD this does not matter. DFT gives no support for acceptor-like surface states near E_c on an OH-terminated surface. The interface trap sheet and Q_f stay ASSUMED/FITTED.

## 2. Sources, method and cross-check

### Output folders
Under `qe_workflow/cern_htcondor/results/`.

| Film | Folders |
|---|---|
| 0.5 nm | `slabL1_relax_v2` |
| 0.75 nm | `slabL2_relax_v2` |
| 1 nm | `slab1r_final_cpu`; W slab `iwo_slab1_final_cpu` |
| 2 nm | `slab2_relax_c2`, `slab2r_pdos_cpu`; W slab `iwo_slab2_final_cpu` |
| W in bulk | `iwo_W24d`, `iwo_W8b` |
| HSE check | `nc_pbe_*`, `nc_hse_*` |
| Bulk | `qe_workflow/bulk_In2O3_protocol/bands_path.out`, `bands_gamma.out` |

### Method
All numbers are PAW-PBE unless marked HSE.

- **Gap.** From the last HOMO/LUMO line of `scf.out`. ΔE_g = gap − 0.8887 eV (bulk fundamental gap).
- **EA and IP.** From the vacuum plateau of `*_avg.dat` (as in `analyze_slabs.py`). The vacuum-referenced CBM is −EA.
- **ΔE_c at 2 nm.** Two-step alignment, a/2 window. The slab side was re-computed here and gives +0.2813 eV (log: +0.281). The bulk constants E_v − ⟨V⟩ = 3.9098 eV and E_c − ⟨V⟩ = 4.7985 eV are taken from `RESULTS_LOG.md`, because `bulk_v11.cube` was deleted on 2026-10-06.
- **ΔE_c below 2 nm.** ΔE_c(t) = ΔE_c(2 nm) + EA(2 nm) − EA(t), the same-termination EA route used by V2 at 1 nm. Then ΔE_v = ΔE_c − ΔE_g.
- **Mass.** Parabolic fit, |k| ≤ 0.05 Å⁻¹, along in-plane [100] (`collect_results.slab_mass`).
- **Non-parabolicity.** Kane fit E(1 + αE) = ħ²k²/2m* over the 10 points nearest Γ.
- **W cells.**
  - Band characters come from `projwfc.x`. The VB top is band n_pure − 1, because of the In 4d / W 5s5p band-count pitfall; this was confirmed for every cell.
  - Occupations come from the eigenvalues with the Marzari–Vanderbilt smearing of `scf.in` (0.01 Ry). They reproduce the electron counts to 2e-4.
- **Surface-state measure.** Same as `surface_state_check.py`: the share of projected weight on H atoms plus O atoms within 1.15 Å of an H.

### Cross-check by Codex
Codex re-derived the main numbers with its own scripts, read-only and without seeing ours. Its answer is in `codex_xcheck_2026-10-10.md` (prompt: `codex_xcheck_prompt_2026-10-10.md`).
- The gaps, EA, IP, thicknesses, E2 − E1, surface shares and all 2 nm W-slab numbers agree to the printed digits.
- The masses agree within 0.001 m0.

## 3. Results per thickness (pure In2O3 slabs)

All rows are COMPUTED except those marked CALCULATED or LITERATURE.

| Quantity | bulk | 2 nm | 1 nm | 0.75 nm | 0.51 nm |
|---|---|---|---|---|---|
| H-to-H thickness, relaxed (nm) | — | 1.962 | 0.930 | 0.695 | 0.461 |
| In-plane cell (Å) | 10.306 | 10.318 × 10.309 | 10.336 × 10.335 | 10.428 × 10.293 | 10.696 × 10.019 |
| PBE gap (eV) | 0.8887 | 1.2239 | 1.7885 | 2.1986 | 3.1401 |
| ΔE_g, PBE (eV) | 0 | +0.335 | +0.900 | +1.310 | +2.251 |
| ΔE_g, HSE-corrected (eV) [CALCULATED, ratio 1.060–1.107] | 0 | 0.355–0.371 | 0.954–0.996 | 1.388–1.450 | 2.386–2.492 |
| ΔE_c, PBE (eV) | 0 | **+0.281** (two-step; double average +0.287) | **+0.848** (EA route; two-step +0.819, no interior) | **+1.059** (EA route) | +1.585 (EA route) |
| ΔE_v, PBE (eV) | 0 | −0.054 | −0.052 | −0.251 | −0.667 |
| CB share ΔE_c/ΔE_g | — | 0.84 | 0.94 | 0.81 | 0.70 |
| ΔE_c, HSE-scaled (eV) [CALCULATED; same CB share ASSUMED] | 0 | 0.298–0.311 | 0.899–0.939 | 1.122–1.172 | 1.680–1.754 |
| EA (eV); vacuum-referenced CBM = −EA | 4.776 (bulk-equivalent) | 4.495 | 3.9285 | 3.718 | 3.192 |
| IP (eV) | 5.665 (bulk-equivalent) | 5.719 | 5.717 | 5.916 | 6.332 |
| Vacuum asymmetry, left − right (meV) | — | 0.0 | 0.0 | −27 | 0.0 |
| m*, in-plane, PBE (m0) | 0.159 | 0.2064 | 0.2811 | 0.3348 | 0.4282 |
| Δm* (m0) | 0 | +0.047 | +0.122 | +0.176 | +0.269 |
| E2 − E1 at Γ (eV) | — | 0.719 | 1.499 | 1.815 | 1.887 |
| Kane α, PBE (1/eV) | 0.63 | 0.50 | 0.38 | 0.33 | 0.25 |
| m* for TCAD, V2 convention 0.208 + Δm* [CALCULATED] | 0.208 (LITERATURE, Stokey 2021) | 0.255 | 0.330 | 0.384 | 0.477 |
| NC300, 3-D, V2 form (cm⁻³) [CALCULATED] | 2.38e18 | 3.24e18 | 4.76e18 | 5.97e18 | 8.27e18 |
| NC300, quasi-2D N2D/t (cm⁻³) [CALCULATED] | — | 1.38e19 | 3.56e19 | 5.53e19 | 1.01e20 |
| Ratio quasi-2D / 3-D (equivalent E_c shift) | — | 4.26 (−37.5 meV) | 7.49 (−52 meV) | 9.26 (−58 meV) | 12.2 (−65 meV) |
| VBM weight on OH (OH share of atoms) | — | 0.2 % (27 %): interior | 73 % (50 %): surface, proxy | 76 % (63 %): surface, one side | 98 % (86 %): all OH |
| CBM weight on OH | — | 1.4 %: interior | 23 %: interior, proxy | 36 %: interior-weighted | 56 % |
| Validity | reference | bulk-like interior | no bulk-like interior | VB edge is a surface state | **outside the recipe**: relaxes into an In(OH)₃-like layer; excluded from all laws |

### Notes on the table

**Bulk-equivalent EA and IP.**
- They are the 2 nm EA plus ΔE_c(2 nm), and the 2 nm IP plus ΔE_v(2 nm).
- They hold only for the H/OH-terminated (001) surface, in PBE.
- They are reported but not proposed for AFFINITY:
  - the termination dipole is not that of the device surfaces;
  - an HSE correction of the absolute edges does not exist;
  - χ is degenerate with the gate work function and Q_f (`analysis_2026-09-25/SYNTHESIS.md`).

**The 1 nm surface check is a proxy.** The pure 1 nm slab has no projwfc run, so its W twin was used (`iwo_slab1_final_cpu`, VB top = band 311).
- In the pure 2 nm slab, the valence states with the most OH weight (20–27 %) lie 50–70 meV below the VBM.
- In the 2 nm W slab, four OH-surface bands (71–75 % OH weight) form the VB top. They sit 67 meV above the highest interior-like valence state.

**Quasi-2D NC300.** It is defined as N2D/t, with N2D = m* kT/(πħ²), the label thickness t and the V2-convention mass. The second subband is included with its Boltzmann weight, which is at most 8e-13.
- It is the Boltzmann-equivalent density of states, valid in subthreshold.
- In the degenerate on-state, the 3-D Fermi–Dirac form in ATLAS overstates n at a given Fermi level: by a factor of 1.7 at E_F − E_1 = 4.7 kT, the level that n_s ≈ 1.3e13 cm⁻² at V_G = 3 V implies. Here F_1/2 = 8.10 against ln(1 + e^η) = 4.70.

**Kane α.** It is overestimated, because the PBE gap is too small. It is reported, not mapped: ATLAS drift-diffusion uses a parabolic NC300 for a user material.

## 4. Tungsten (PBE, crystalline cells, one W per cell)

| Quantity | bulk, W on 24d | bulk, W on 8b | 1 nm slab | 2 nm slab |
|---|---|---|---|---|
| W share of the cations | 3.1 % | 3.1 % | 4.2 % | 1.8 % |
| Donated electrons (3 per W), cm⁻³ [CALCULATED] | 2.7e21 | 2.7e21 | 3.0e21 (2.8e14 cm⁻²) | 1.4e21 (2.8e14 cm⁻²) |
| VB top band; host CB bottom band (projwfc) | 351; 352 | 351; 352 | 311; 312 | 663; 664 |
| E_F − host CB bottom at Γ (eV) | 1.763 | 1.713 | 1.228 | 1.238 |
| W-5d-rich level − host CB bottom at Γ (eV), W 5d weight | **+1.764** (0.54) | **+1.803** (0.50) | **+1.223** (0.56) | **+1.341** (0.52) |
| Electrons in the host CB bottom band (of 3) | 1.79 | 1.93 | 2.00 | 2.04 (+0.86 in the 2nd host subband) |
| W-5d-projected electrons (of 3) | 0.29 (10 %) | 0.36 (12 %) | 0.43 (14 %) | **0.09 (3 %)** |
| Gap, VB top to host CB at Γ (eV); change vs pure | 0.862; −0.031 | 0.894; +0.001 | 1.719; −0.069 | 1.076; −0.148 (VB top is an OH surface state; interior ≈ −0.08) |
| EA; IP; work function (eV) | — | — | 4.069; 5.789; 2.84 | 4.746; 5.823; 3.51 |
| Change vs the pure twin: EA, IP (eV) | — | — | +0.141, +0.072 | +0.251, +0.104 |

### Other W results [COMPUTED, `results/summary.json`, `RESULTS_LOG.md`]
- **Site.** W prefers 24d by 0.258 eV.
- **Charge state.** The mean W–O bond is 1.98 Å, which matches W⁶⁺ (Shannon 1976 [LITERATURE]: W⁶⁺ 1.98 Å, W⁴⁺ 2.04 Å).
- **Magnetism.** Weak moments of 0.6–0.7 μB per cell appear at 3×3×3 k-points. This is preliminary.

### How to read the W table [INFERRED]
- Each cell holds 1.4–5.5e21 cm⁻³ donated electrons, so E_F lies 1.2–1.8 eV inside the conduction band. The W-5d-rich level holds some electrons only because the band is filled up to it.
- The thinner and more W-rich 1 nm cell puts more of the charge on W (14 %). The 2 nm cell is the closest to the devices, at 1.8 % W, and puts only 3 % there.
- At device densities (below 1e19 cm⁻³, E_F below E_c) the level is empty.
- **For ATLAS:**
  - W is a fully ionized donor with a negative ionization energy, i.e. no DEFECTS or trap entry for W.
  - A fully active "~2 % W" would give about 1e21 cm⁻³, which is incompatible with films that switch off. Most of the W donors must therefore be compensated or inactive, and the DFT cannot say by what.
  - The changes in gap and EA with W are dominated by this extreme filling. They do not transfer to device densities.
- **Limitation.** This is PBE only. A hybrid functional can lower localized d levels, and no HSE calculation of a W cell exists.

## 5. Mapping to ATLAS parameters

| ATLAS parameter | Law | DFT input (label) | Other inputs (label) | V2 | New here |
|---|---|---|---|---|---|
| **EG300** | E_g,bulk + ΔE_g(t) | ΔE_g points COMPUTED. Law ΔE_g = 0.8143·t^−1.3152 (t = H–H, nm) is FITTED to the 0.695/0.930/1.962 nm DFT points; residuals ≤ 0.4 %. Optional HSE factor ×1.06–1.11 (ASSUMED transfer). | E_g,bulk = 3.05 eV, LITERATURE (Fan 2021) | Used: 2-point PBE law 0.83997·t^−1.34569 (Lin labels) | 0.695 nm point; 3-point law; HSE option. EG300 enters only n_i (holes are not solved), so its effect on I_D is negligible [INFERRED]. |
| **AFFINITY** | χ_bulk − ΔE_c(t) | ΔE_c COMPUTED: two-step at 2 nm, EA route below. Laws, all FITTED to DFT points, at 2.0 / 6.3 / 13.2 nm: (a) V2 0.78504·t^−1.504: 0.277 / 0.049 / 0.016; (b) 3-point H–H 0.7015·t^−1.3167 (residuals +7/−9/+3 %): 0.282 / 0.062 / 0.024; (c) 1–2 nm H–H 0.7616·t^−1.4778: 0.273 / 0.050 / 0.017; (d) MODEL box E1 = E21/3: 0.234 / 0.046 / 0.013. Optional HSE factor ×1.06–1.11. | χ_bulk = 4.3 eV, LITERATURE (Fan 2021). The DFT bulk-equivalent EA of 4.78 eV (PBE, H-(001)) is not proposed. | Used: 0.281 @ 1.98 nm, 0.848 @ 0.95 nm | 0.695 nm point (1.059 eV); extrapolation spread at 6.3/13.2 nm; HSE option (+17 to +31 meV at 2 nm, +3 to +7 meV at 6.3 nm). For T4, tabulated points `{"0.695": dEc 1.0586, dEg 1.3099, dm 0.1758}` (`dft_inputs.json`, same format as `t4_prepare.py`; T4 is on hold, D-07). |
| **NC300** | V2: 2(2πm*kT/h²)^1.5 with m* = 0.208 + Δm*(t). Candidate at t ≤ 2 nm: N2D/t. | Δm* COMPUTED. Law Δm* = 0.1112·t^−1.2639 (FITTED to DFT points; V2 had 0.11416·t^−1.29453). E2 − E1 COMPUTED. Crossover box (δ = 1.40 nm, m_z = 0.139 m0) is a MODEL from the 1 and 2 nm E21. | m*_bulk = 0.208, LITERATURE (Stokey 2021) | Used: 3-D form | Quasi-2D: 1.38e19 at 2 nm (×4.3, −37.5 meV). MODEL: ×1.47 (−10 meV) at 6.3 nm, ×0.88 (+3 meV) at 13.2 nm. Needs one ATLAS test before any use. If adopted, Q_f must be refitted. |
| **Quantum-confinement model** (if one is ever switched on) | the solver computes the confinement itself | in-plane m* COMPUTED; m_z only from the MODEL (0.139) | — | not used | **Then the ΔE_c/ΔE_g laws must be switched off** (double counting). Check the mass keywords in the installed manual first. |
| **ARICHN** (Schottky S/D only) | 120.17 A cm⁻² K⁻² × m*(t) | m*(t) as above | — | not used (ideal ohmic S/D) | Relevant only if the Pd contacts are made Schottky. The Mott–Schottky barrier would then be WF_Pd − AFFINITY(t), which ΔE_c raises by 0.28 eV at 2 nm. WF_Pd is a LITERATURE input that must be cited. Pinning is not computed. |
| **ME.TUNNEL** (gate tunnelling) | oxide tunnelling mass | none: this DFT has no HfO2/Al2O3 | LITERATURE needed | — | Not derivable here. |
| **DOPING / N_d,eff(t)** | unchanged: FITTED 2.5e17·[1 + (t/20)^4] | W is a resonant, fully ionized donor with 3 e per W; 3 % W-5d-projected at 2 nm (COMPUTED) | — | Qualitative only | Supports keeping N_d,eff FITTED. DFT cannot give the compensated (active) fraction. |
| **DEFECTS / INTDEFECTS / INTERFACE QF** | unchanged: tail FITTED; deep Gaussian ASSUMED; D_it sheet ASSUMED; Q_f FITTED | No W gap state. The CB edge is interior at every t ≥ 0.695 nm. OH states appear only at the VB edge, are donor-like near E_v and stay neutral in n-type operation. | — | Not DFT-based | No DFT basis for acceptor-like surface states near E_c of an OH surface. The real Al2O3/IWO interface and the air surface are not computed. |
| **MUN** (μ_band) | unchanged: FITTED | m*(2)/m*(13.2) = 1.20 (COMPUTED + LITERATURE bulk) | — | not used | At constant scattering time the mass gives a mobility ratio of 0.83; the fitted ratio is 0.28. Most of the mobility drop is not band-structural [INFERRED]. |
| **PERMITTIVITY** | unchanged: 9.3, MEASURED (Januar 2026 SI) | none (no DFPT) | — | — | — |

### ATLAS constraints that apply when these are implemented
These are from `01_CURRENT_STATE.md` §K.
- NC300, EG300 and AFFINITY are MATERIAL parameters, set once per deck. Thickness laws therefore enter through the deck generator, as in V2.
- Nothing here needs more than the existing traps (MAXTRAPS ≤ 10).
- A change of NC300 at 2 nm must be followed by a Q_f refit. Q_f is shared and acts as one number with χ and ΔE_c (SYNTHESIS).

## 6. What V2 already used and what is new

### Already in V2 (`config/iwo_material_model_v2.yaml`, `analysis_2026-10-06_V2/make_v2_model.py`)
- ΔE_g at 0.95 and 1.98 nm: 0.900 and 0.335 eV.
- ΔE_c at 0.95 and 1.98 nm: 0.848 and 0.281 eV.
- Δm* at 0.95 and 1.98 nm: 0.122 and 0.047 m0, added to the 0.208 m0 literature bulk mass.
- NC300 from the 3-D formula.
- HSE: only as a check (ratio 1.06). It was not applied.
- W: only qualitatively (N_d,eff stays fitted).
- 2 nm band edges bulk-like: only qualitatively.
- The `points` slots for thin films are empty: `t4_prepare.py` was never run, and `thin_dft.json` does not exist.

### New in this extraction
- **Thin films.** Full read-out of the 0.695 and 0.461 nm films: gap, ΔE_c, Δm*, EA/IP, E21, surface character and validity flag.
- **2 nm alignment.** The two-step ΔE_c(2 nm) was re-computed on the slab side and gives +0.2813 eV.
- **Laws.** 3-point laws, and the spread of the extrapolation at 6.3 and 13.2 nm.
- **HSE option.** HSE-scaled ΔE_g and ΔE_c.
- **Subbands and density of states.** Subband spacings, and the quasi-2D NC300 candidate with its MODEL crossover.
- **Non-parabolicity.** Kane α (PBE).
- **Surface character.** At 0.695, 0.461 and 1 nm (proxy), and in the 2 nm W slab.
- **2 nm W slab analysis.** This was pending in `01_CURRENT_STATE.md` §F. It gives the filling, the W level and the W effect.
- **All W cells.** One consistent electron-filling and W-5d-projection analysis of all four cells.
- **Absolute alignment.** Bulk-equivalent EA/IP (PBE, H-(001)).

## 7. Gaps: what this DFT cannot give

1. **Absolute E_g and χ of amorphous IWO.**
   - PBE gives 0.89 eV and HSE06 2.07–2.11 eV, both at the PBE lattice and both below the literature bulk value.
   - The EA depends on the termination.
   - The bulk anchors of EG300 and AFFINITY therefore stay LITERATURE.
2. **HSE band-edge partition.** No HSE planar average exists, and the HSE ratio exists only at 1 nm. Keeping the PBE CB share is ASSUMED.
3. **HSE for W cells.** The position of the W 5d level beyond PBE is unknown.
4. **Mass of the W slabs.** The 1 nm bands run aborted, and the 2 nm job ran without bands.
5. **Films thicker than 2 nm.** No slab exists, so every value at 6.3 and 13.2 nm is an extrapolation (spread in §5).
6. **Compensation and the effective donor density.** No V_O, H, O_i or W-complex calculations exist yet (COMPLETE_PLAN 2B, item 3). N_d,eff stays FITTED.
7. **Interfaces.** The Al2O3/IWO interface and the air-exposed surface are not computed (2B, item 4). D_it and Q_f stay ASSUMED/FITTED.
8. **Band tails and localization.** Crystalline cells have no tails (amorphous series, plan 2A). N_t and W_TA stay FITTED.
9. **Dielectric constant.** There is no DFPT calculation. ε_r stays MEASURED (9.3).
10. **Mobility.** Scattering is not computed. μ_band stays FITTED; DFT gives only m*.
11. **Other.** The temperature coefficients (EGALPHA/EGBETA), the gate-field (Stark) shift of the subbands, the Pd/IWO barrier with pinning, and second structural samples are not computed.

## 8. Reproduce

```
"<venv>\Scripts\python.exe" analysis_2026-10-10_campaign\dft_to_tcad_extract.py
```

- **Runtime.** About 1 minute.
- **What it reads.** Only QE output files.
- **What it writes.** `dft_inputs_raw.json` (full machine output) and `dft_inputs.json` (curated, labelled, with sources), both in this folder.
- **What it does not do.** It changes no other file and launches no simulator.
