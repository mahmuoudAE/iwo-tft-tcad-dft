# 02. Provenance and recomputation of every number in the remaining C10 S2/S3/S4/S5 decks (2026-10-14)

**What this file is.** A table of every numerical value that enters the remaining S2, S3, S4 and S5 decks of the registered C10 campaign. For each value it gives the value, the unit, the deck statement it enters, the label and the source. Every value that is CALCULATED, or that comes from a FITTED law, was recomputed independently with the project venv (`IWO_ATLAS_Model_claude/.venv`, Python 3.13, scipy 1.18.1, numpy 2.5.3). The script output is in §6 and the scripts are in §7.

**Sources read.**
- `CAMPAIGN_DESIGN.md`, read in full;
- `campaign_matrix.json`: all 185 entries;
- `config/physics_options.yaml`, `geometry.yaml`, `solver.yaml`, `iwo_material_model_v2.yaml`;
- `run_0061` `material_model_used.json` and `device.in`, and the gate-tunnelling statements of `run_0067` `device.in`;
- `dft_inputs.json`, crystalline only;
- `build_iwo_decks.py`, `make_campaign_matrix.py`, `profile_shared.py` / `profile_s4s5.py` (constants only), `S2_PREP.md`;
- register sections H-A to H-F, H-J, A41(d) and §3;
- the 5.28 manual text (authority);
- the paper digests in `report_latex_full/digest/papers/`.

**Not read.**
- No output of run_0075/0076/0077;
- nothing under any `sealed/` folder;
- no AFF-6p3 or STRIP-6p3 output (their *matrix definitions* were built as decks, like every other entry);
- no amorphous DFT quantity.

**How the decks were checked.**
- The decks were built **in memory only**, with `campaign_tools.entry_deck(..., V3)`. No simulator was called. `python -I -B` was used, so no `.pyc` was written; the `__pycache__` timestamps were checked unchanged afterwards.
- Every value written into the 93 planned_fixed S2/S3/S4a decks was parsed from the deck text and compared with the laws.
- Each S2/S3 deck was then diffed against its film's primary baseline deck (S0-01 / S1-01 / S1-02), to show exactly which statements carry each option (§6.2).

**Labels.**
- MEASURED: the target devices or the fab.
- COMPUTED: our crystalline DFT, file cited.
- LITERATURE: full citation; DOI given where the project bibliography has one.
- CALCULATED: formula and inputs shown.
- FITTED: the data it was fitted to are named.
- ASSUMED.
- NUMERICAL: a solver or mesh setting. This is a sub-case of ASSUMED, kept separate for clarity.
- UNVERIFIED: a source that could not be checked against a local copy of its text.

---

## 0. Findings in brief

1. **All CALCULATED and FITTED-law values reproduce.**
   - Across CAMPAIGN_DESIGN §4, the matrix `derived_per_film` / `shared_start_values`, `physics_options.yaml` and the decks, no value differs from the independent recomputation by more than 0.5 %.
   - The largest difference is 0.165 %: ΔE_g(13.2 nm) printed as 0.0274 eV against 0.02735 eV (rounding).
   - The refit of the three DFT laws through the COMPUTED crystalline points reproduces a and p to ≤ 0.004 %.
   - The Lenzlinger–Snow constants reproduce to ≤ 0.11 %. They also match the free-electron constants printed in the ATLAS 5.28 manual, Table 3-158: 1.5414e-6 and 6.8308e7.
   - The regenerated S4a Latin hypercube (seeds 20261010/20261011) matches the matrix to ≤ 0.154 %, which is the 4-significant-figure rounding.
2. **Deck level.**
   - In the 93 planned_fixed S2/S3/S4a decks, every IWO MATERIAL, DEFECTS, DOPING, INTERFACE, MOBILITY and ARICHN value equals its law value within 0.05 %.
   - Every option statement carries the documented numbers (§6.2).
3. **The matrix `params` dictionary is stale in 11 S3 entries (16 fields, 2–85 %).**
   - The fields are MUN, NC300_3d and NTA of S3-01..03, S3-05/06, S3-08/09, S3-10, S3-24/25 and S3-27.
   - The decks are correct, because they come from the `overrides`. The profiler reads each run's `material_model_used.json`, not `params`.
   - Any table, supplement or Codex digest built from `params` would print wrong numbers. Example: S3-01 lists MUN 12.977 cm²/Vs, but the deck has 15.865 cm²/Vs (CALCULATED, mass factor off).
4. **S3-04 and S3-07 at 2.0 nm have exactly the solver statements of the S0-01 deck**; only the header comments differ (checked with `ct.statements`).
   - Bulk-only and 50:50 tails coincide with the surface tail at t = 2 nm.
   - S4A-01-2p0 is also identical to S0-01, as designed (reuse).
   - The register already keeps them out (§3, "duplicates"). Launching them would spend 2 launches on nothing.
5. **Count mismatch, document only.**
   - CAMPAIGN_DESIGN §1/§6 says 181 planned + 19 reserve, S2 = 17 and S3 = 27.
   - The matrix has 185 + 15, S2 = 18 (+1 S2r) and S3 = 29 (STRIP-6p3, AFF-2p0/6p3 and S0-02-DOS2 were added later).
   - The matrix field `model_file_env` still says V2, but every C10 config uses V3. S2_PREP §1 records the V2 = V3 statement equivalence (101 decks); it was not re-run here.
6. **Label and source problems (no numeric mismatch).** Details in §3.
   - **Δ_sr = 0.287 nm is labelled LITERATURE.** In Januar 2026 it is an *extracted effective roughness from their model fitted to the same devices* (main text, Fig. 5f). It is therefore FITTED on the target data (circularity), not an independent literature value.
   - **χ_HfO2 = 2.5 eV is labelled LITERATURE (Robertson 2000).** The route stated in `physics_options.yaml` (χ_Si 4.05 − CBO 1.5) gives 2.55 eV, 2.0 % off. On the nominal FNORD/QTNLSC current that is a factor ×2.0–3.2 (CALCULATED, §6).
   - **E_g(HfO2) = 5.8 eV is labelled LITERATURE (Robertson 2000).** To my recollection the cited table gives 6.0 eV (UNVERIFIED). It does not enter electron-only QTNLSC.EL tunnelling (INFERRED from the manual's single-band ME.TUNNEL description).
   - **The m*(t) convention is ASSUMED, not stated as such.** It adds the PBE increment to the literature bulk mass. A multiplicative transfer would give m*(2 nm) = 0.270 m0 instead of 0.2554 m0 (+5.7 %, CALCULATED).
   - Applying crystalline-slab DFT laws to channels that Januar 2026 reports as lacking long-range crystallinity (HRTEM, main text) is an ASSUMED transfer. H-K tests it.
7. **§4 lists 31 ASSUMED or NUMERICAL items (11 that can move a fitted value or a verdict) and 11 citations to pin.** The ones most likely to matter for a Nature-level claim:
   - ε_Al2O3 = 9.0 (C_ox −6.0 % / +4.3 % at 7 / 11, CALCULATED);
   - the oxide tunnelling masses (0.20 / 0.35 nominal);
   - the capture cross-section 1e-15 cm²;
   - TAT.SLICEPTS left at the default 12 (untested; the ITAT convergence stays UNRESOLVED under A41);
   - the 2 µm contact overlap;
   - the constant N_D (FITTED V1 amplitude, form ASSUMED).

---

## 1. Constants used for every recomputation

| Symbol | Value | Label / source |
|---|---|---|
| q, h, k_B, m0 | 1.602176634e-19 C, 6.62607015e-34 J s, 1.380649e-23 J/K, 9.1093837015e-31 kg | LITERATURE: SI 2019 exact values and CODATA 2018 m0 (same as `build_iwo_decks.py:23-24`) |
| ε0 | 8.8541878128e-14 F/cm | LITERATURE (CODATA 2018) |
| kT at 300 K | 0.0258520 eV | CALCULATED, k_B T/q |

---

## 2. Master table

Values are listed at 2.0 / 6.3 / 13.2 nm where they depend on the film. "Check" is the independent recomputation (§6); "OK" means ≤ 0.5 %.

### 2.1 Structure, stack and bias (every deck)

| # | Quantity | Value | Unit | Enters the deck as | Label | Source / formula | Check |
|---|---|---|---|---|---|---|---|
| G1 | Channel length L | 20 | µm | x-extent between the Pd volumes (x = 2…22 µm) | MEASURED | fab schematic (geometry.yaml; Januar 2026 Sec. 2.1) | — |
| G2 | Contact overlap | 2 | µm | Pd electrodes x = 0–2 and 22–24 µm; Q_f and gate span x = 0–24 | ASSUMED | not reported (geometry.yaml) | — |
| G3 | Simulated width | 1 | µm | `mesh width=1.0` (currents in A/µm) | NUMERICAL | geometry.yaml | — |
| G4 | Physical width W | 290 | µm | not in the deck; only for totals (I_total = 290 × I) | MEASURED | fab schematic | — |
| G5 | t_IWO | 2.0 / 6.3 / 13.2 | nm | `region 1/2 y.min=-t` | MEASURED (fab); identification with the DFT H–H thickness ASSUMED | geometry.yaml; DFT_TO_TCAD | — |
| G6 | HfO2 thickness | 15 | nm | `region num=4 y=0.002…0.017` | MEASURED (fab schematic) | geometry.yaml | — |
| G7 | Al2O3 thickness | 2 | nm | `region num=3 y=0…0.002` | MEASURED (fab schematic); position touching the channel ASSUMED (H.3) | geometry.yaml | — |
| G8 | ε_HfO2 | 19.57 | — | `material region=4 permittivity=19.57` | MEASURED (Januar 2026 SI Fig. S1); SI text not available locally, so UNVERIFIED here | geometry.yaml | — |
| G9 | ε_Al2O3 | 9.0 (S6: 7, 11) | — | `material region=3 permittivity=9.0` | **ASSUMED** ("not reported"); to be measured or cited | geometry.yaml | C_ox −6.03 % / +4.26 % at 7 / 11 (CALCULATED) |
| G10 | ε_IWO | 9.3 | — | `material material=IWO permittivity=9.3` | MEASURED (Januar 2026 SI Fig. S1, 9.30 ± 0.04); the main text says "approximately 9" (verified in the digest l.158-160) | v3 model | — |
| G11 | C_ox | 8.95537e-7 | F/cm² | header only; enters the profiling (ΔV = −q ΔQ_f/C_ox) | CALCULATED: ε0/(15e-7/19.57 + 2e-7/9.0) | build_iwo_decks.cox | OK (0.000 %) |
| G12 | TiN gate | 50 nm, Conductor volume | nm | `region num=6 material=Conductor y=0.017…0.067` | MEASURED (Januar 2026 Sec. 2.1, verified in the digest) | — | — |
| G13 | Gate work function | 4.7 | eV | `contact name=gate workfunction=4.7` | **ASSUMED** ("TiN 4.5–4.9 eV": range has no citation, to be cited); degenerate with Q_f and χ, so held fixed | v3 model | — |
| G14 | Pd S/D | 70 nm volumes, ideal ohmic | — | `electrode name=source/drain material=Palladium`, no workfunction | thickness MEASURED (schematic); ohmic ASSUMED | geometry.yaml | — |
| G15 | Air above the channel | 70 nm | nm | `region num=7 material=Air` | ASSUMED (no cap reported) | geometry.yaml | — |
| G16 | T | 300 | K | `models … temp=300` | ASSUMED (temperature not recorded) | v3 model | — |
| G17 | V_D | 0.7 | V | `solve vstep=0.1 vfinal=0.7 name=drain` | MEASURED (schematic; the workbook has no units) | geometry.yaml | — |
| G18 | V_G sweep | −3 → 3; steps 0.2 to −1 V, 0.05 to 1.5 V, 0.1 to 3 V | V | stepped `solve vstep/vfinal name=gate` | range MEASURED (data grid); steps NUMERICAL | solver.yaml | — |

### 2.2 IWO MATERIAL statement (`material material=IWO …`)

| # | Quantity | 2.0 / 6.3 / 13.2 nm | Unit | Parameter | Label | Source / formula | Check |
|---|---|---|---|---|---|---|---|
| M1 | E_g,bulk | 3.05 | eV | inside EG300 | LITERATURE: Fan et al., *Nanomaterials* **11**, 3070 (2021), DOI 10.3390/nano11113070. A simulation input of a different a-IWO device; the paper text is not available locally, so the value is UNVERIFIED here. The ±0.2 eV uncertainty in the model file is ASSUMED. | v3 model | — |
| M2 | ΔE_g(t) = 0.81431·t^−1.31518 | 0.32725 / 0.07236 / 0.02735 | eV | inside EG300 | FITTED (log least squares) to COMPUTED PBE points 1.3099 / 0.8998 / 0.3352 eV at t_HH 0.695 / 0.930 / 1.962 nm (`dft_inputs.json` films.*.dEg_PBE_eV); 6.3/13.2 nm are extrapolations | dft_to_tcad_extract.py:219 | refit a, p ≤ 0.000 %; the design's 0.0274 is 0.165 % off (rounding) |
| M3 | EG300 = E_g,bulk + ΔE_g | 3.37725 / 3.12236 / 3.07735 | eV | `eg300=` | CALCULATED | — | deck = law (≤ 0.05 %) |
| M4 | χ_bulk | 4.3 | eV | inside AFFINITY | LITERATURE (Fan 2021, "composition-mixing estimate"; UNVERIFIED here); ±0.3 eV ASSUMED. Degenerate with G13 and Q_f | v3 model | — |
| M5 | ΔE_c(t) = 0.70147·t^−1.31669 (fit3) | 0.28161 / 0.06216 / 0.02347 | eV | inside AFFINITY | FITTED (log LSQ) to COMPUTED PBE points 1.0586 / 0.8478 / 0.2813 eV (EA route at 0.695/0.930 nm, two-step at 1.962 nm); residuals +7 / −9 / +2.7 %; extrapolation spread 0.046–0.062 / 0.013–0.024 eV (dft_inputs laws.dEc_eV) | dft_inputs.json | refit ≤ 0.001 % |
| M6 | AFFINITY = χ_bulk − ΔE_c | 4.01839 / 4.23784 / 4.27653 | eV | `affinity=` | CALCULATED | — | OK (≤ 0.001 %) |
| M7 | m*_bulk | 0.208 | m0 | inside m*(t) | LITERATURE: Stokey et al., *J. Appl. Phys.* **129**, 225102 (2021), DOI 10.1063/5.0052848, 0.208 ± 0.006 m_e at n = 2.81e17 cm⁻³ (verified in the digest l.81) | — | — |
| M8 | Δm(t) = 0.11116·t^−1.26387 | 0.04629 / 0.01086 / 0.00426 | m0 | inside m*(t) | FITTED (log LSQ) to COMPUTED PBE in-plane increments 0.1758 / 0.1221 / 0.0474 m0 over the PBE bulk 0.159 | dft_inputs laws.dm_m0 | refit ≤ 0.004 % |
| M9 | m*(t) = 0.208 + Δm(t) | 0.25429 / 0.21886 / 0.21226 | m0 | not written directly; enters M10, M13, ARICHN, ME.TUNNEL, MASS.TUNNEL and the BQP mass | CALCULATED. **Additive transfer of the PBE increment onto the literature mass is ASSUMED** (multiplicative: 0.270 m0 at 2 nm, +5.7 %) | — | OK (≤ 0.020 %) |
| M10 | NC300 | 1.373e19 (quasi-2D) / 2.56928e18 / 2.45405e18 | cm⁻³ | `nc300=` | CALCULATED. 2.0 nm: N2D/t = m* m0 kT/(π ħ² t) = 1.37306e19, written as 1.373e19 through `physics_options.nc300_override_cm3[2.0]`. 6.3/13.2 nm: 2(2π m* m0 kT/h²)^1.5 | dft_inputs; make_campaign_matrix | OK (≤ 0.011 %) |
| M10a | Single-subband criterion at 2.0 nm | E21 = 0.7191 eV = 27.8 kT; second-subband weight 8.3e-13 | — | decides whether M10 uses N2D/t | E21 COMPUTED (slab2_relax_c2 bands.out, Γ); the rule "E21 > 10 kT" is ASSUMED (pre-registered) | dft_inputs films.2.0 | E_F − E1 = 0.120 eV at n_s 1.28e13 cm⁻² and 0.158 eV at C_ox·3 V/q (CALCULATED), at least 4.6× below E21 |
| M10b | Quasi-2D NC in `dft_inputs` | 1.3791e19 (with the DFT-point mass 0.2554) | cm⁻³ | not used (the deck uses the law mass 0.25429) | CALCULATED | — | 0.44 % from the deck value (below threshold; both conventions exist) |
| M10c | Degenerate overstatement of the quasi-2D NC in the 3-D FD form | 1.72 at η = 4.7 | — | model limitation, not an input | CALCULATED: F_1/2(η)/ln(1+e^η) = 8.115/4.709 | DFT_TO_TCAD §3 (8.10/4.70) | OK |
| M10d | Equivalent band shift of the NC override | −37.51 | meV | — | CALCULATED: −kT ln(1.37306e19/3.21785e18) | — | OK |
| M11 | NV300 | 1e19 | cm⁻³ | `nv300=` | ASSUMED (holes not solved) | v3 model | — |
| M12 | μ_band start (overrides `mu_band_fitted[t]`) | 17.6897 / 44.1956 / 63.2597 | cm²/Vs | inside MUN | CALCULATED from the shared law μ∞·(0.208/m*)/(1+ℓ/t) at μ∞ = 100.0053 and ℓ = 7.2484 nm. These two pass exactly through the V2 FITTED anchors 17.6897 (2.0) and 63.2597 (13.2), which were FITTED to the measured I_on(3 V). | make_campaign_matrix:46-51 | ℓ, μ∞ reproduced to 4 digits |
| M13 | Mass factor 0.208/m*(t) | 0.81796 / 0.95039 / 0.97992 | — | inside μ_band | CALCULATED | — | mass-only ratio 2.0/13.2 = 0.8347 (H-D forecast 0.835) |
| M14 | Δ_sr | 0.287 | nm | inside MUN | **labelled LITERATURE, but FITTED**: Januar 2026 Fig. 5f "extracted effective roughness" from their unified model fitted to the same devices (digest l.590-592), i.e. derived from the target data. The (1 − Δ_sr/t)² form is a project choice (V1), so ASSUMED. | v3 model | — |
| M15 | Roughness factor (1 − 0.287/t)² | 0.73359 / 0.91096 / 0.95699 | — | inside MUN | CALCULATED | — | — |
| M16 | MUN = μ_band·(1 − Δ_sr/t)² | 12.977 / 40.2606 / 60.5388 | cm²/Vs | `mun=` (and the IGZO `mobility … mun=`) | CALCULATED (FITTED start) | — | OK (≤ 0.023 %) |
| M17 | μ_p | 0.01 | cm²/Vs | `mup=` | ASSUMED | v3 model | — |
| M18 | τ_n0 = τ_p0 | 1e-6 (S2-01/03: 1e-9) | s | `taun0= taup0=` | ASSUMED (background SRH); extreme ASSUMED | v3 model; matrix | — |
| M19 | TMUN | 0 | — | `tmun=0` | NUMERICAL (single temperature) | solver override | — |

### 2.3 DEFECTS, DOPING and INTERFACE

| # | Quantity | Value (2.0 / 6.3 / 13.2 nm) | Unit | Statement | Label | Source / formula | Check |
|---|---|---|---|---|---|---|---|
| D1 | N_s (start) | 4e12 | cm⁻² | through Nt2 = N_s/2 nm = 2e19 (`thickness_laws.Nt_cm3.Nt2`) | FITTED start (V1 2 nm anchor Nt·t, FITTED to the 2 nm transfer curve); launched in S4 | v3 model | — |
| D2 | N_t = N_s/t | 2.0e19 / 6.3492e18 / 3.0303e18 | cm⁻³ | inside NTA | CALCULATED | — | OK |
| D3 | W_T (WTA) | 0.040 | eV | `wta=` (regions 1, 2) | FITTED start (V1 2 nm value) | v3 model | T_t = W_T/k_B = 464.2 K (CALCULATED) |
| D4 | NTA = N_t/W_T | 5.0e20 / 1.5873e20 / 7.5758e19 | cm⁻³ eV⁻¹ | `nta=` | CALCULATED | — | deck = law |
| D5 | Deep acceptor Gaussian (region 1) | NGA 5e16 cm⁻³ eV⁻¹, EGA 0.6 eV, WGA 0.15 eV | — | `nga= ega= wga=` | ASSUMED (V2 continuity). The Fan 2021 range 2.5–3.7e16 is for a different device (LITERATURE, UNVERIFIED here) | v3 model | — |
| D6 | Interface acceptor sheet | 3e11 cm⁻² eV⁻¹ at E_c − 0.3 eV, W 0.12 eV | — | becomes region 2 (0.25 nm layer) | ASSUMED. The literature scale 6.3e11 cm⁻² eV⁻¹ is LITERATURE: Wang et al., *Front. Mater.* **9**, 850451 (2022), DOI 10.3389/fmats.2022.850451 (HfO2/In2O3, subthreshold method citing Si et al. 2021; verified in the digest l.308) | v3 model | — |
| D7 | Interface layer thickness | 0.25 | nm | region 2 y = −0.00025…0 µm | NUMERICAL (halving it changes I_D by 0.009 dec, EMPIRICAL V1) | geometry.yaml | — |
| D8 | Region-2 merged Gaussian (D5 + D6/0.25 nm, moment-matched) | NGA 1.16757e19, EGA 0.301554, WGA 0.123975 | cm⁻³ eV⁻¹, eV, eV | `defects region=2 nga= ega= wga=` | CALCULATED (area and first two moments preserved; build_iwo_decks.moment_matched_gaussian). Sheet amplitude 3e11/0.25 nm = 1.2e19 | — | reproduced exactly |
| D9 | NTD, NGD | 0, 0 | cm⁻³ eV⁻¹ | `ntd=0 ngd=0` | ASSUMED zero | v3 model | — |
| D10 | WTD, WGD, EGD | 0.1 eV, 0.1 eV, E_g − 0.1 = 3.27725 / 3.02236 / 2.97735 eV | eV | `wtd= wgd= egd=` | NUMERICAL placeholders, inert while NTD = NGD = 0 | — | OK |
| D11 | Capture cross-sections, all 8 (sigtae … siggdh) | 1e-15 (S2-01/03: 1e-13; S2-02: 1e-20) | cm² | `sigtae=…siggdh=` | **ASSUMED, "to be cited before publication"** (CAMPAIGN_DESIGN:193) | — | — |
| D12 | DOS quadrature | numa 384, numd 192 (DOS2: 768/384) | — | `numa= numd=` | NUMERICAL (×2 check run_0016: 0.006 dec) | matrix | — |
| D13 | N_D | 2.5e17 | cm⁻³ | `doping uniform n.type conc=2.5e+17 region=1,2` | FITTED V1 donor amplitude (V1 law fitted to the V0 per-film 2e17 / 3e17 / 3e17 / 2.65e18), kept; **constant form ASSUMED** | v3 model provenance | — |
| D14 | Q_f (start) | 1.38345e12 | cm⁻² | `interface qf=1.38345e+12 y=±1e-7 µm` (IWO/Al2O3 boundary) | FITTED start (V2: least squares on the 2 and 13.2 nm anchors by exact rigid shift); profiled in S4 | v2/v3 model | ΔV_FB = −qQ_f/C_ox = −0.24751 V (CALCULATED; header −0.2475) |

### 2.4 Solver and mesh (every deck)

| # | Quantity | Value | Statement | Label | Note |
|---|---|---|---|---|---|
| N1 | Statistics and models | `fermi srh temp=300 print` | `models` | ASSUMED model choice (CAMPAIGN_DESIGN §3) | S3-26: `srh temp=300 print` (Boltzmann); S2-02: no `srh` |
| N2 | Newton settings | maxtraps 10, itlimit 80, climit 1e-6, ir.tol 1e-19 | `method newton trap …` | NUMERICAL | solver.yaml |
| N3 | Strict CR.TOLER (depletion) | 1e-17 / 2.28e-17 / 7.88e-16 A | `cr.toler=` with xandrnorm | CALCULATED from MEASURED: max(1e-17 A, 1e-5 × smallest active measured current: 1.369e-13 / 2.284e-12 / 7.879e-11 A/µm) | recomputed from data/experimental_clean.csv; matches the S2-01/02 deck (7.88e-16) |
| N4 | On-state CR.TOLER | 5e-18 | `cr.toler=5e-18 ^xandrnorm` | NUMERICAL | above 1e-9 A/µm measured current |
| N5 | Carriers | 1 (S2-01..03: 2) | `method … carriers=` | ASSUMED (electron-only, A13 / S1-06) | — |
| N6 | x-mesh | 0.3 / 0.05 / 0.01 / 0.05 / 0.2 / 0.7 µm at x = 0 / 1.8 / 2 / 2.2 / 3 / 12 (mirrored) | `x.mesh` | NUMERICAL | 117 x lines (EMPIRICAL from run node counts) |
| N7 | y-mesh IWO bulk | min(1.0, t/8) = 0.25 / 0.7875 / 1.0 nm | `y.mesh loc=-t` | NUMERICAL | 32-bit memory limit ~30k nodes (geometry.yaml) |
| N8 | y-mesh IWO/Al2O3 interface | 0.0625 nm at y = −0.25, −0.125, 0 nm | `y.mesh` | NUMERICAL | kept unchanged by S2-11 |
| N9 | y-mesh Al2O3 / HfO2 | 0.25 nm at y = 2 nm; 1.0 nm at y = 17 nm (FNORD: 0.25 nm both; S2-11: 0.125 / 0.5 nm) | `y.mesh loc=0.002 / 0.017` | NUMERICAL | §2.8 |
| N10 | Timeouts | S2: 900–5400 s; S3: 1200–3600 s; S4/S5: 1600 / 2000 / 3100 s | run_campaign (not in the deck) | NUMERICAL | matrix `timeout_s` |

### 2.5 S2 options (off-current floor), as written into the decks (§6.2)

| # | Run(s) | Quantity | Value | Statement | Label / source | Check |
|---|---|---|---|---|---|---|
| S2a | S2-01 (13.2), S2-03 (2.0) | Extreme SRH lifetime | 1e-9 s | `taun0=1e-09 taup0=1e-09` | ASSUMED (beyond the reasonable range by design) | — |
| S2b | S2-01, S2-03 | Extreme capture σ | 1e-13 cm² (all 8) | DEFECTS regions 1, 2 | ASSUMED (×100) | — |
| S2c | S2-01 / S2-03 | Channel TAT mass | 0.2123 / 0.2543 m0 | `models … trap.tunnel trap.hurkx mass.tunnel=` | m*(t) CALCULATED (M9); its use as the trap-tunnelling mass is ASSUMED (D11 of the design) | = m*(13.2), m*(2.0) to 4 digits |
| S2d | S2-02 (13.2) | Suppressed σ, SRH off | 1e-20 cm²; `models fermi temp=300 print` | DEFECTS; MODELS | ASSUMED reference | — |
| S2e | S2-01..03 | Two carriers | `carriers=2` | METHOD | ASSUMED test | — |
| S2f | S2-04/05/06/12/13 | Nominal HfO2 χ / E_g / me.tunnel | 2.5 eV / 5.8 eV / 0.20 m0 | `material region=4 affinity=2.5 eg300=5.8 me.tunnel=0.2` | χ: labelled LITERATURE (Robertson, *J. Vac. Sci. Technol. B* **18**, 1785 (2000); the DOI is not in the project files and the digits were not checked against the paper: **UNVERIFIED**). Stated route χ_Si 4.05 − CBO 1.5 = **2.55** eV (2.0 % off the 2.5 used). E_g 5.8: **UNVERIFIED** (I recall 6.0 in that table). me.tunnel 0.20: **ASSUMED** "inside 0.1–0.4", source to be pinned | χ mismatch 2.0 % (§3 F5) |
| S2g | same | Nominal Al2O3 χ / E_g / me.tunnel | 1.25 eV / 8.8 eV / 0.35 m0 | `material region=3 affinity=1.25 eg300=8.8 me.tunnel=0.35` | χ = 4.05 − 2.8 = 1.25 (CALCULATED from the LITERATURE CBO, UNVERIFIED digits); E_g 8.8 LITERATURE (UNVERIFIED); mass ASSUMED "inside 0.3–0.5" | OK by construction |
| S2h | S2-07/08/09/10/11, S0-02-DOS2 | Worst-case oxide set | HfO2 3.2 / 5.8 / 0.10; Al2O3 1.6 / 8.8 / 0.30 | same statements | ASSUMED leakage-maximising scenario (not a rigorous bound) | — |
| S2i | QTNLSC runs | Gate contact tunnelling mass | 1.0 | `contact name=gate workfunction=4.7 qtunn.cmass=1` | ASSUMED = ATLAS default (5.28 manual Table 3-132, l.13735) | verified |
| S2j | QTNLSC runs | S/D excluded from the nearest-electrode search | flag | `contact name=source/drain exclude_near` | NUMERICAL choice (manual p.303, p.1157; run_0066 diagnosis) | — |
| S2k | — | Barriers implied by the deck affinities | nominal: TiN/HfO2 2.20, TiN/Al2O3 3.45, IWO/Al2O3 2.768 / 2.988 / 3.027 eV; worst: 1.50, 3.10, 2.418 / 2.638 / 2.677 eV | — | CALCULATED (§6 I) | — |
| S2l | S2-09/10 (FNORD worst) | F.AE, F.BE | 2.171e-6 A/V², 8.628e7 V/cm | `models … fnord f.ae=2.171e-06 f.be=8.628e+07` | CALCULATED: A = q³/(8πhφ m_r) = 1.0276e-5, B = 8π√(2 m_r m0) φ^1.5/(3qh) = 3.9684e7 at φ = 4.7 − 3.2 = 1.5 eV, m_r = 0.10. Transferred to the field ATLAS evaluates (the Al2O3/IWO segment, manual l.13034-13038): F.AE = A/r², F.BE = rB, r = 19.57/9.0 = 2.17444. Form: Lenzlinger & Snow, *J. Appl. Phys.* **40**, 278 (1969), DOI not in the project files (UNVERIFIED); the constants match ATLAS Table 3-158 | OK (0.110 % / 0.012 %) |
| S2m | (no run in the matrix) | FNORD nominal | F.AE 7.402e-7, F.BE 2.167e8 | physics_options only | CALCULATED (φ 2.2, m_r 0.20) | OK (0.098 % / 0.027 %); with χ_HfO2 = 2.55: 7.582e-7 / 2.094e8 |
| S2n | S2-12/13 | Oxide TAT traps | 1e19 cm⁻³, acceptor, 1.0 eV below the HfO2 E_c, σ_n = σ_p = 1e-13 cm² | `doping region=4 uniform tat.trap conc=1e+19 acceptor sign=1e-13 sigp=1e-13 e.level=1` | ASSUMED high-defect bound; σ ASSUMED (installed example quantumex20). E.LEVEL for acceptors is measured below E_c (manual l.4799-4800) | — |
| S2o | S2-12/13 | Trap charge out of Poisson; slice points | `^tat.poisson`; TAT.SLICEPTS not set, so the default 12 | `models … itat.sc.el ^tat.poisson` | NUMERICAL; default 12 verified (manual Table 3-139, l.14730); **untested** (S2_PREP §6); convergence UNRESOLVED under A41(d) | — |
| S2p | S2-14/15 (Q_f on), S2-16/17 (Q_f = 0) | Strip length; V_D steps | L_p = 20 µm; 0 → 0.1 V (0.05 V steps) → 0.7 V (0.1 V steps) | separate two-terminal deck, `interface qf=1.38345e+12` or `qf=0`, `solve … name=drain` | L_p ASSUMED; Q_f on the ungated surface ASSUMED (both run); steps NUMERICAL | — |
| S2q | strip | Registered ohmic ratio | I(0.7)/I(0.1) = 7.000 ± 0.5 | prediction, not an input | CALCULATED (0.7/0.1); diffusion form (1 − e^(−0.7/kT))/(1 − e^(−0.1/kT)) = 1.0213; the ±0.5 margin is ASSUMED | OK |
| S2r | strip, post-solve | (W/L)_par | V2 reference 1e-4 µm⁻¹ | `physics_options.strip.wl_par_per_um` (not in the separate deck) | FITTED (V2 variant D on the 13.2 nm floor); refitted on 13.2 nm (H-B) | — |
| S2s | S2-11 | Oxide y-mesh factor | 0.5 → spacing 0.125 nm at y = 2 nm and 0.5 nm at y = 17 nm | `y.mesh loc=0.002 spac=0.000125`, `loc=0.017 spac=0.0005` | NUMERICAL (registered; FAILED its 0.1 dec stability test) | deck verified |
| S2t | S0-02-DOS2; A41(d) DOS2 | DOS ×2 | numa 768, numd 384 | DEFECTS | NUMERICAL | deck verified |
| S2u | A41(d) OXM (conditional) | S2-04/06/08 + oxide factor 0.5 | as S2s | as S2s | NUMERICAL; at most 6 launches, each only on its trigger | — |

### 2.6 S3 options (model-form branches)

| # | Run(s) | Quantity | Value (2.0 / 6.3 / 13.2 nm) | Statement | Label / source | Check |
|---|---|---|---|---|---|---|
| B1 | S3-01..03 | No confinement | ΔE_c = ΔE_g = Δm = 0 → AFFINITY 4.3, EG300 3.05, m* 0.208, NC300 2.38049e18 (3-D bulk), egd 2.95 | `material … eg300=3.05 affinity=4.3 nc300=2.38049e+18` | CALCULATED (law amplitudes set to 0, ASSUMED intervention) | deck = law |
| B2 | S3-01..03 | μ_band without the mass factor | 21.6265 / 46.5024 / 64.5561 → MUN 15.865 / 42.362 / 61.7794 cm²/Vs | `mun=` | CALCULATED μ∞/(1+ℓ/t) × roughness | deck = law; **matrix `params.MUN` stale** (§3 F1) |
| B3 | AFF-2p0 / AFF-6p3 | Affinity only | AFFINITY 4.3 (ΔE_c 0); everything else as S0-01 / S1-01 | `affinity=4.3` (the only statement change) | CALCULATED; expected ΔV_th,cc −281.6 / −62.2 ± 5 mV (A13; ±5 mV ASSUMED) | ΔE_c(2.0) = 281.61 meV, ΔE_c(6.3) = 62.16 meV |
| B4 | S3-04..06 | Bulk-only tail | N_t = 2e19 at every t (alpha 0) → NTA 5e20 | `nta=5e+20` | ASSUMED branch | **S3-04 = S0-01 deck** (0 statement differences) |
| B5 | S3-07..09 | 50:50 tail | Nt2 = 1e19 (N_s/2 as a surface term) + bulk 1e19 → N_t 2e19 / 1.3175e19 / 1.1515e19 → NTA 5e20 / 3.29365e20 / 2.87879e20 | `nta=` | ASSUMED branch; `nt_bulk_cm3` labelled "FITTED branch" | **S3-07 = S0-01 deck** |
| B6 | S3-10 | No tail (6.3 nm) | NTA 0 | `nta=0` | ASSUMED branch | — |
| B7 | S3-11..16, S3-27 | IGZO.TOKYO | GAMMA0 −0.31 / +0.30; TGAMMA 178.4 K; NCRIT 1e20 cm⁻³; MUN restated | `mobility material=IWO igzo.tokyo mun=… tmun=0 tmup=0 igzo.gamma0= igzo.tgamma=178.4 igzo.ncrit=1e+20` | GAMMA0 −0.31, TGAMMA 178.4 K and NCRIT 1.0e20 are the ATLAS defaults (5.28 manual Table 3-61, l.8256-8258), which trace to Abe et al., *Thin Solid Films* **559**, 40–43 (2014) (manual ref. 161; DOI UNVERIFIED). +0.30 ASSUMED. NCRIT labelled ASSUMED (it equals the default; degenerate with MUN) | γ(300 K) = TGAMMA/T + GAMMA0 = 0.2847 / 0.8947 (CALCULATED); μ(1e19)/MUN = 0.721 / 0.357 |
| B8 | S3-27 (6.3) | Native profiling check | Q_f 2.38345e12 (+1e12), MUN 24.1564 (×0.6) | `interface qf=2.38345e+12`; `mun=24.1564` | ASSUMED test factors | shift −0.1789 V (CALCULATED); **matrix `params.MUN` stale** |
| B9 | S3-17..23 | Schottky barrier φ_B | 0.2 / 0.5 eV (S3-23: 0.5 without lowering) | `contact name=source/drain workfun=AFFINITY+φ_B surf.rec [barrier] e.tunnel me.tunnel=m* ^ins.ohmic` | ASSUMED grid (selected on data, so FITTED in effect) | workfun 4.21839 / 4.43784 / 4.47653 (0.2) and 4.51839 / 4.73784 / 4.77653 (0.5): deck = law |
| B10 | S3-17..23 | ARICHN | 30.558 / 26.300 / 25.5076 A cm⁻² K⁻² | `arichn=` on the IWO material | CALCULATED: 120.17·m*(t); A* = 4πq m0 k_B²/h³ = 120.173 (CALCULATED) | OK (0.003 %) |
| B11 | S3-17..23 | Contact ME.TUNNEL | 0.25429 / 0.218856 / 0.212263 m0 | `e.tunnel me.tunnel=` | m*(t) CALCULATED; identification ASSUMED | — |
| B12 | S3-17..23 | Top mesh under the contacts | 0.1 nm | y.mesh | NUMERICAL | — |
| B13 | S3-24 / S3-25 (2.0) | BQP | ngamma 1.2, nalpha 0.5, qdir 2; mass 0.139 / 0.2543 m0 set as ml = mt1 = mt2 | `models … bqp.n bqp.ngamma=1.2 bqp.nalpha=0.5 bqp.qdir=2`; `material … ml= mt1= mt2=` | 1.2 / 0.5 are the ATLAS defaults (manual l.34791-34792), labelled ASSUMED. 0.139: MODEL (box through two DFT E21 spacings, 2 parameters, 2 points). 0.2543: CALCULATED (M9). With DFT shifts off: MUN 15.865. **Whether ml/mt1/mt2 change anything other than the BQP mass for a user material is UNVERIFIED** | — |
| B14 | S3-26 | Boltzmann | `models srh temp=300 print` | MODELS | ASSUMED ablation | — |

### 2.7 S4 and S5 (calibration and leave-one-film-out)

| # | Quantity | Start / value | Range | Enters | Label | Check |
|---|---|---|---|---|---|---|
| C1 | ΔV₀ via Q_f | 1.38345e12 cm⁻² | Q_f −1.411e12 … 4.178e12 (|ΔV₀| ≤ 0.5 V ↔ ±2.7948e12) | profiled offline (exact rigid shift); native only in S4c/S4d/S5 | FITTED (shared); start FITTED V2; the 0.5 V bound is ASSUMED | CALCULATED (design −1.4e12 … 4.2e12, rounded) |
| C2 | μ∞ | 100.005 cm²/Vs | 10–300 | profiled (I ∝ MUN), written as `mu_band_fitted[t]` | FITTED; range ASSUMED | M12 |
| C3 | ℓ | 7.248 nm | 0–50 nm | profiled jointly | FITTED (empirical law); range ASSUMED | M12 |
| C4 | N_s | 4e12 (candidate 1) | 1e12–1e13, log | Nt2 = N_s/2 nm | FITTED by launches; range ASSUMED | LHS ≤ 0.154 % |
| C5 | W_T | 0.040 eV | 0.025–0.060 eV | `wta=` | FITTED; range ASSUMED | — |
| C6 | GAMMA0 (only if IGZO is adopted) | −0.31 | −0.6 … +0.6 | `igzo.gamma0=` | FITTED; range ASSUMED | γ(300 K) −0.005 … 1.195 (CALCULATED) |
| C7 | S4a LHS (14 points + start) | seeds 20261010 (2-D) and 20261011 (3-D) | map N_s = 10^(12+u), W_T = 0.025 + 0.035u, G0 = −0.6 + 1.2u | 45 decks (§6 K lists all values) | ASSUMED design (pre-registered); values CALCULATED | regenerated: max deviation 0.154 % (4-s.f. rounding) |
| C8 | S4b trust region | half an S4a stratum = range/28 per dimension (0.0357 dec in N_s, 1.25 meV in W_T, 0.043 in G0); duplicate separation 1/56 | — | candidate generation | ASSUMED (profile_s4s5.py A1 ruling) | CALCULATED |
| C9 | S4c / S4d / S5 decks | profiled Q_f, μ∞, ℓ written natively; S5: 4 adaptive candidates × 2 training films + 2 frozen predictions per fold | — | `{fit:…}` / `{fold:…}` tokens | FITTED (values do not exist yet) | — |
| C10 | Profiling transforms | ΔV = −qΔQ_f/C_ox with C_ox 8.95537e-7 F/cm²; I ∝ MUN | — | profile_shared.py:24, :60; profile_s4s5.py | CALCULATED; exact only without tunnelling, Schottky or G–R terms (S1-07 / S3-27 check) | C_ox OK |
| C11 | Acceptance and objective (scoring, not deck) | RMSE ≤ 0.15 dec; ΔV_th ≤ 0.10 V; I_on ±30 %; SS and μ_FE ±20 %; S4c 0.01 dec | — | score code | ASSUMED engineering limits (Codex) | — |

### 2.8 Tunnelling-mesh parameters (inputs to the convergence branch in `00_user_request_tunnelling_mesh.md`)

| # | Quantity | Value | Where | Label / source |
|---|---|---|---|---|
| Q1 | Registered slicing | automatic (`qt_mesh: 0`), slices locally perpendicular to each semiconductor–oxide segment | physics_options.gate_tunnelling | NUMERICAL; manual l.13660-13676 (Atlas-built mesh → automatic) |
| Q2 | Device oxide y-mesh (automatic slicing samples it; *inferred*, not stated by the manual) | Al2O3 0.0625 nm (y = 0) → 0.25 nm (y = 2 nm); HfO2 → 1.0 nm (y = 17 nm); run_0067: 15 Al2O3 + 28 HfO2 intervals | `y.mesh` | NUMERICAL; interval counts EMPIRICAL (run_0067 equilibrium.str, S2_PREP §6) |
| Q3 | S2-11 refinement | ×0.5 at y = 2 and 17 nm (0.125 / 0.5 nm); ≈ 22 + 55 intervals (estimate); y = 0 line kept | as above | NUMERICAL; interval counts CALCULATED estimate (S2_PREP §6) |
| Q4 | QT mesh, if `qt_mesh: 1` (run_0063..0066 form) | slice spacing 0.2 µm (24 µm / 0.2 = 120 slices), point spacing 0.5 nm (17 nm / 0.5 = 34 points, plus one point beyond each face) | `qtx.mesh loc=0/24 spac=0.2`, `qty.mesh loc=-0.0005 / 0.0175 spac=0.0005` | NUMERICAL. The QT mesh must enclose the oxide (run_0065: a flush mesh was ignored). On the rectangular QT mesh the current was booked to the electrodes only and KCL failed (run_0066) |
| Q5 | Proposed QT cross-check series (not self-consistent) | point 0.5 → 0.25 nm (34 → 68 points), slice 0.2 → 0.1 µm (120 → 240 slices) | same | NUMERICAL proposal (user request, 2026-10-14) |
| Q6 | Node counts and memory | run_0067 9,594 nodes (117 × 82), 1.69 GB peak of 4 GB; run_0062 13,689 nodes (117 × 117), out of memory at the old 2 GB limit; 13.2 nm OXM ≈ 117 × 138 = 16.1k nodes (estimate); run_0070 24,255 nodes ran without QTNLSC; 32-bit limit ~30k nodes | — | EMPIRICAL (run logs as cited in A41(d), S2_PREP §6, geometry.yaml); 16.1k is a CALCULATED estimate |
| Q7 | ITAT slices | TAT.SLICEPTS default 12 (≈ 1.4 nm per point across 17 nm, CALCULATED) | not set in S2-12/13 | ATLAS default (manual l.14730); convergence untested |

---

## 3. Flags: mismatches and label problems

| ID | Where | What | Size | Effect | Fix proposed |
|---|---|---|---|---|---|
| F1 | `campaign_matrix.json` `params` (S3-01, -02, -03, -24, -25) | `MUN_cm2Vs` keeps the confinement-on value (12.977 / 40.2607 / 60.5388) and `Nc300_3d_cm3` keeps the DFT-mass value (3.218e18 …). The decks use 15.865 / 42.362 / 61.7794 and 2.38049e18 | 2.0–35 % | none on the decks; wrong if `params` is tabulated | regenerate `params` from the overrides (generator `P(t, …)` with massfac=False / conf=False); results-informed amendment not needed (bookkeeping) |
| F2 | `params` (S3-05, -06, -08, -09, -10) | `NTA_cm3_eV` keeps the surface-tail value; the decks have 5e20 (bulk-only), 3.29365e20 / 2.87879e20 (50:50) and 0 (none) | 52–100 % | same as F1 | same |
| F3 | `params` (S3-27) | `MUN_cm2Vs` 40.2607; the deck has 24.1564 (`igzo.mun` is correct) | 66.7 % | same | same |
| F4 | S3-04, S3-07 | solver statements identical to S0-01 (only the header comments differ) | — | 2 wasted launches if run | keep them out (register §3 already does); mark them `duplicate_of: S0-01` in the matrix |
| F5 | χ_HfO2 nominal | 2.5 eV used; the stated route χ_Si (4.05) − CBO (1.5) = 2.55 eV | 2.0 % | nominal FN/QTNLSC current ×2.0–3.2 (CALCULATED at E_HfO2 5e6–3e6 V/cm); immaterial for the ≥ 9-decade nominal margin, but a citation error | relabel "CALCULATED from LITERATURE CBO, rounded" or use 2.55; pin Robertson 2000 against its text |
| F6 | E_g(HfO2) | 5.8 eV labelled LITERATURE (Robertson 2000) | UNVERIFIED (6.0 eV recalled) | no effect on electron QTNLSC.EL (INFERRED) | cite a source for 5.8 or use the cited table value |
| F7 | Δ_sr = 0.287 nm | labelled LITERATURE; it is an effective roughness FITTED by Januar et al. to the same devices | label | circularity: a fitted feature of the target data sits inside "independent" MUN | relabel "FITTED (Januar 2026, same devices)"; S6 sensitivity Δ_sr = 0 and 0.375 nm (In2O3 value, same paper) |
| F8 | m*(t) convention | additive transfer of the PBE Δm onto 0.208 is not labelled ASSUMED | 5.7 % at 2 nm vs multiplicative | NC300(2 nm) and the mass factor ±5.7 %, partly absorbed by μ∞/ℓ and Q_f | label ASSUMED; add it to S6 (or report it as an analytic NC sensitivity: −kT ln 1.057 = −1.4 meV) |
| F9 | Counts | design 181 + 19 (S2 17, S3 27) vs matrix 185 + 15 (S2 18 + 1, S3 29) | — | bookkeeping | update CAMPAIGN_DESIGN §1/§6 or add an erratum line |
| F10 | `model_file_env` | the matrix says V2; every C10 config says V3 | — | none (V2 + overrides = V3 + overrides, S2_PREP §1; not re-run here) | edit the matrix field at the next regeneration |
| F11 | E_F − E1 ≤ 0.12 eV at V_G = 3 V (design D14) | holds for n_s = 1.28e13 cm⁻² (V_G − V_th ≈ 2.29 V); with the full C_ox·3 V it is 0.158 eV | statement scope | the criterion (E21 = 0.719 eV) holds either way (≥ 4.6×) | state the V_th assumption |
| F12 | Quasi-2D NC: `dft_inputs` 1.3791e19 vs deck 1.37306e19 | two masses (DFT point at 1.962 nm vs law at 2.0 nm) | 0.44 % | none (below threshold) | keep the register NC convention 1.373e19 (A13) |
| F13 | FNORD nominal set | defined (F.AE 7.402e-7, F.BE 2.167e8) but no matrix run uses it | — | none | note it as unused |
| F14 | ε_HfO2 19.57 and ε_IWO 9.30 | labelled MEASURED (SI Fig. S1); the SI is not in the local corpus | UNVERIFIED here | — | add the SI text to the digest |

No numerical mismatch above 0.5 % was found between CAMPAIGN_DESIGN §4, `physics_options.yaml`, the matrix overrides / `derived_per_film` and the recomputation. All values above 0.5 % are the `params` bookkeeping fields (F1–F3).

---

## 4. ASSUMED and "to be cited" values in the remaining decks, by expected impact

**A. Can move a fitted value or a verdict.**
1. **ε_Al2O3 = 9.0** (G9).
   - C_ox and therefore every ΔV₀ ↔ Q_f conversion and μ_FE: −6.0 % / +4.3 % for 7 / 11 (CALCULATED).
   - Measure it or cite a source for ALD Al2O3 at 250 °C.
2. **Oxide tunnelling masses**: HfO2 0.20 / 0.10, Al2O3 0.35 / 0.30 m0 (S2f–h).
   - FN and QTNLSC currents depend exponentially on √m.
   - "Source to be pinned before publication."
3. **Oxide affinities** (S2f–h): Robertson 2000 digits UNVERIFIED; F5 and F6.
4. **Capture σ = 1e-15 cm²** (D11): "to be cited before publication".
5. **Gate work function 4.7 eV** (G13): the "TiN 4.5–4.9 eV range" is uncited. It is degenerate with Q_f, so only ΔV₀ is reportable, not Q_f as a physical charge.
6. **χ_bulk 4.3 eV and E_g,bulk 3.05 eV** (M1, M4): LITERATURE estimates of another device (Fan 2021; paper text not local, UNVERIFIED).
7. **N_D constant form** (D13): the amplitude is FITTED (V1); the form is ASSUMED. ×0.1 / ×10 in S6.
8. **Contact overlap 2 µm and ideal ohmic Pd** (G2, G14).
9. **Crystalline-to-amorphous transfer, and t ≡ t_HH**, of all DFT laws (M2, M5, M8). H-K tests it; Januar 2026 reports no long-range crystallinity.
10. **Δ_sr form and value** (M14, F7).
11. **Additive mass convention** (M9, F8).

**B. Test or bound definitions (ASSUMED by design; the conclusions are conditional on them).**
- SRH extremes: τ 1e-9 s, σ 1e-13 / 1e-20 cm² (S2a–d).
- Worst-case oxide set (S2h).
- TAT traps: 1e19 cm⁻³, 1.0 eV, σ 1e-13 cm² (quantumex20) (S2n).
- Strip L_p 20 µm and Q_f on the ungated surface (S2p).
- Schottky grid {0.2, 0.5} eV (B9).
- IGZO GAMMA0 +0.30 and NCRIT (B7).
- BQP defaults 1.2 / 0.5 and the box mass 0.139 (MODEL) (B13).
- S1-07 / S3-27 factors: +1e12 cm⁻², ×0.6 (B8).
- All S4 ranges and the |ΔV₀| ≤ 0.5 V bound (C1–C6).
- Deep Gaussian 5e16 cm⁻³ eV⁻¹ at E_c − 0.6 eV (D5).
- D_it sheet 3e11 cm⁻² eV⁻¹ (D6; the literature scale 6.3e11 is verified).
- NV300 1e19 cm⁻³ and μ_p 0.01 cm²/Vs (M11, M17).
- T = 300 K (G16).
- Acceptance limits (C11).

**C. Numerical (convergence evidence exists or is planned).**
- DOS 384/192 (D12).
- The interface layer 0.25 nm (D7).
- The mesh (N6–N9, Q2–Q6).
- CR.TOLER (N3, N4).
- TAT.SLICEPTS 12: **no evidence** (Q7).
- QT-mesh settings (Q4, Q5).

**Citations to pin (UNVERIFIED in this audit):**
- Robertson 2000, JVST B 18, 1785 (digits and DOI);
- Lenzlinger & Snow 1969, JAP 40, 278 (DOI); the constants themselves are verified against ATLAS Table 3-158 and first principles;
- Abe et al. 2014, TSF 559, 40 (DOI);
- Fan 2021: values against the paper text;
- Januar 2026 SI Fig. S1: the ε values;
- a source for χ_Si = 4.05 eV, for example a standard textbook, to be pinned;
- the TiN work-function range;
- ε_Al2O3;
- the oxide tunnelling-mass ranges;
- the capture cross-section;
- the Ielmini ITAT model reference.

---

## 5. What is solid

These numbers are reproduced here from labelled inputs and can be quoted with their labels:
- every CALCULATED number in the decks: AFFINITY, EG300, m*, NC300 (3-D and quasi-2D), MUN, NTA, the region-2 merged Gaussian, ARICHN, the Schottky work functions, F.AE/F.BE, C_ox and ΔV_FB;
- the three DFT laws (FITTED to the COMPUTED crystalline points; refit identical);
- the S4a LHS values.

The weak points are labels and literature pinning (§3, §4), not arithmetic.

---

## 6. Recomputation output (verbatim)

### 6.1 `recompute.py` (python -I -B; read-only; no simulator)

```text
kT(300 K) = 0.0258520 eV (CALCULATED, kB T / q)

## A. DFT thickness laws a*t^-p: refit through the COMPUTED crystalline points (log least squares)
dEc: points t_HH [0.695, 0.93, 1.962] -> [1.0586, 0.8478, 0.2813]; refit a=0.70147 p=1.31669 (registered a=0.70147 p=1.31669: OK (0.001 %), OK (0.000 %)); rel. residuals [0.07, -0.09, 0.027]
   at 2.0/6.3/13.2 nm (registered law): 0.28161, 0.06216, 0.02347
dEg: points t_HH [0.695, 0.93, 1.962] -> [1.3099, 0.8998, 0.3352]; refit a=0.81431 p=1.31518 (registered a=0.81431 p=1.31518: OK (0.000 %), OK (0.000 %)); rel. residuals [0.003, -0.004, 0.001]
   at 2.0/6.3/13.2 nm (registered law): 0.32725, 0.07236, 0.02735
dm: points t_HH [0.695, 0.93, 1.962] -> [0.1758, 0.1221, 0.0474]; refit a=0.11116 p=1.26387 (registered a=0.11116 p=1.26387: OK (0.004 %), OK (0.000 %)); rel. residuals [0.002, -0.002, 0.001]
   at 2.0/6.3/13.2 nm (registered law): 0.04629, 0.01086, 0.00426

## B. Band inputs per film (CAMPAIGN_DESIGN 4.1 values checked)
t=2.0: dEc=0.28161 OK (0.003 %) | dEg=0.32725 OK (0.015 %) | AFFINITY=4.3-dEc=4.01839 OK (0.000 %) | EG300=3.05+dEg=3.37725 | egd=EG300-0.1=3.27725 | m*=0.25429 OK (0.004 %)
t=6.3: dEc=0.06216 OK (0.061 %) | dEg=0.07236 OK (0.052 %) | AFFINITY=4.3-dEc=4.23784 OK (0.001 %) | EG300=3.05+dEg=3.12236 | egd=EG300-0.1=3.02236 | m*=0.21886 OK (0.020 %)
t=13.2: dEc=0.02347 OK (0.117 %) | dEg=0.02735 OK (0.165 %) | AFFINITY=4.3-dEc=4.27653 OK (0.001 %) | EG300=3.05+dEg=3.07735 | egd=EG300-0.1=2.97735 | m*=0.21226 OK (0.018 %)
HSE-high option x1.107 at 2.0 nm: dEc 0.3117 eV (S6 only)

## C. NC300: 3-D 2(2 pi m* m0 kT/h^2)^1.5 and quasi-2D N2D/t = m* m0 kT/(pi hbar^2 t)
bulk m*=0.208: NC3D=2.38049e+18 (dft_inputs 2.3805e18: OK (0.000 %))
t=2.0: m*=0.25429 NC3D=3.21785e+18 NCq2D=1.37306e+19 used=1.37306e+19 OK (0.005 %)
t=6.3: m*=0.21886 NC3D=2.56928e+18 NCq2D=3.75154e+18 used=2.56928e+18 OK (0.011 %)
t=13.2: m*=0.21226 NC3D=2.45405e+18 NCq2D=1.73657e+18 used=2.45405e+18 OK (0.002 %)
dft_inputs quasi-2D with the DFT-point mass 0.2554: 1.37906e+19 (file 1.3791e19) vs law mass: ratio 1.00437
single subband: E21 = 0.7191 eV (COMPUTED) = 27.82 kT; 10 kT = 0.2585 eV; second-subband weight exp(-E21/kT) = 8.31e-13
quasi-2D/3-D ratio 4.2670; equivalent Ec shift -kT ln(ratio) = -37.51 meV
  n_s = C_ox x 2.29 V / q = 1.280e+13 cm^-2 -> E_F - E1 = kT ln(exp(n_s/N2D)-1) = 0.1203 eV (< E21 by 6.0x)
  n_s = C_ox x 3.0 V / q = 1.677e+13 cm^-2 -> E_F - E1 = kT ln(exp(n_s/N2D)-1) = 0.1578 eV (< E21 by 4.6x)
  degenerate overstatement F1/2(4.7)/ln(1+e^eta) = 8.115/4.709 = 1.723
  degenerate overstatement F1/2(4.64)/ln(1+e^eta) = 7.972/4.650 = 1.714
n at 2 V overdrive in 2 nm: C_ox*2/(q t) = 5.590e+19 cm^-3

## D. Mobility: mu_band = mu_inf (0.208/m*)/(1+l/t), MUN = mu_band (1-0.287/t)^2
anchors (V2 FITTED) 17.6897 @2.0, 63.2597 @13.2 -> ell = 7.2484 nm, mu_inf = 100.0053 cm2/Vs (design 7.25 / 100.0; matrix 7.248 / 100.005)
t=2.0: mass factor 0.81796, mu_band=17.6897, roughness=0.73359, MUN=12.9770 OK (0.023 %); no-mass-factor mu_band=21.6265 -> MUN 15.8650; x0.6 MUN 7.7862
t=6.3: mass factor 0.95039, mu_band=44.1956, roughness=0.91096, MUN=40.2607 OK (0.002 %); no-mass-factor mu_band=46.5024 -> MUN 42.3620; x0.6 MUN 24.1564
t=13.2: mass factor 0.97992, mu_band=63.2597, roughness=0.95699, MUN=60.5388 OK (0.002 %); no-mass-factor mu_band=64.5561 -> MUN 61.7794; x0.6 MUN 36.3233
mass-only band-mobility ratio 2.0/13.2 = m*(13.2)/m*(2.0) = 0.8347 (design 0.83, register forecast 0.835)

## E. Tail and interface DOS
Ns=4e+12, WT=0.04: t=2.0: Nt=Ns/t=2.0000e+19 NTA=Nt/WT=5.0000e+20; bulk-only Nt=2.0000e+19; 50:50 Nt=2.0000e+19
Ns=4e+12, WT=0.04: t=6.3: Nt=Ns/t=6.3492e+18 NTA=Nt/WT=1.5873e+20; bulk-only Nt=2.0000e+19; 50:50 Nt=1.3175e+19
Ns=4e+12, WT=0.04: t=13.2: Nt=Ns/t=3.0303e+18 NTA=Nt/WT=7.5758e+19; bulk-only Nt=2.0000e+19; 50:50 Nt=1.1515e+19
Nt2 = Ns/2 nm = 2.0000e+19; Tt = WT/kB = 464.2 K
interface sheet 3e11 cm^-2/eV / 0.25 nm = 1.2000e+19 cm^-3/eV; region-2 moment-matched Gaussian: nga=1.16757e+19 ega=0.301554 wga=0.123975 (run_0061 deck 1.16757e19 / 0.301554 / 0.123975)

## F. Gate stack and Q_f
C_HfO2=1.15518e-06, C_Al2O3=3.98438e-06, C_ox(series)=8.95537e-07 F/cm2 (deck header 8.9554e-07: OK (0.000 %)); EOT=3.856 nm (k_SiO2 3.9 LITERATURE)
Q_f 1.38345e12 -> dV_FB = -q Q_f / C_ox = -0.24751 V (deck -0.2475); dV0 0.5 V <-> dQf 2.7948e+12 cm^-2; range -1.411e+12 .. 4.178e+12 (design -1.4e12 .. 4.2e12)
S1-07 / S3-27 dQf = +1e12 -> rigid shift -0.1789 V
  S6 eps_Al2O3=7.0: C_ox=8.4150e-07 (-6.03 %)
  S6 eps_Al2O3=11.0: C_ox=9.3369e-07 (+4.26 %)

## G. Schottky branch
free-electron Richardson constant 4 pi q m0 kB^2/h^3 = 120.173 A/cm2/K2 (physics_options 120.17: OK (0.003 %))
t=2.0: ARICHN=120.17 m*=30.558; workfun=AFFINITY+0.2/0.5 = 4.2184 / 4.5184 eV; me.tunnel = m* = 0.2543
t=6.3: ARICHN=120.17 m*=26.300; workfun=AFFINITY+0.2/0.5 = 4.4378 / 4.7378 eV; me.tunnel = m* = 0.2189
t=13.2: ARICHN=120.17 m*=25.508; workfun=AFFINITY+0.2/0.5 = 4.4765 / 4.7765 eV; me.tunnel = m* = 0.2123

## H. FNORD constants (Lenzlinger-Snow form) and field transfer
prefactors: q^3/(8 pi h q) = 1.54143e-06 A/V^2 (x 1/(phi m_r)); 8 pi sqrt(2 m0) q^1.5/(3 q h) = 6.83089e+07 V/cm (x sqrt(m_r) phi^1.5); r = eps_HfO2/eps_Al2O3 = 2.17444
nominal: phi=2.2 eV m_r=0.2: A=3.5033e-06 A/V^2, B=9.9684e+07 V/cm -> F.AE=A/r^2=7.4093e-07, F.BE=rB=2.1676e+08  [F.AE OK (0.098 %), F.BE OK (0.027 %)]
worst: phi=1.5 eV m_r=0.1: A=1.0276e-05 A/V^2, B=3.9684e+07 V/cm -> F.AE=A/r^2=2.1734e-06, F.BE=rB=8.6290e+07  [F.AE OK (0.110 %), F.BE OK (0.012 %)]
nominal, chi_HfO2=4.05-1.5=2.55: phi=2.15 eV m_r=0.2: A=3.5847e-06 A/V^2, B=9.6305e+07 V/cm -> F.AE=A/r^2=7.5816e-07, F.BE=rB=2.0941e+08
  sensitivity at E_HfO2=3e+06 V/cm: J(phi 2.15)/J(phi 2.2) = 3.16
  sensitivity at E_HfO2=5e+06 V/cm: J(phi 2.15)/J(phi 2.2) = 2.01

## I. Barrier heights implied by the oxide sets (CALCULATED from the deck affinities)
nominal: TiN(4.7)/HfO2 2.20 eV; TiN/Al2O3 3.45 eV; IWO(2.0)/Al2O3 2.768, IWO/HfO2 1.518; IWO(6.3)/Al2O3 2.988, IWO/HfO2 1.738; IWO(13.2)/Al2O3 3.027, IWO/HfO2 1.777
worst: TiN(4.7)/HfO2 1.50 eV; TiN/Al2O3 3.10 eV; IWO(2.0)/Al2O3 2.418, IWO/HfO2 0.818; IWO(6.3)/Al2O3 2.638, IWO/HfO2 1.038; IWO(13.2)/Al2O3 2.677, IWO/HfO2 1.077
Robertson-2000 route (UNVERIFIED digits): chi = chi_Si 4.05 - CBO: HfO2 4.05-1.5 = 2.55 (used 2.5: 2.0 %); Al2O3 4.05-2.8 = 1.25

## J. IGZO.TOKYO exponent, strip ratio, floors
GAMMA0=-0.31: gamma(300 K) = TGAMMA/T + GAMMA0 = 178.4/300 + GAMMA0 = 0.2847; mu(n=1e19)/MUN = 0.7206
GAMMA0=+0.30: gamma(300 K) = TGAMMA/T + GAMMA0 = 178.4/300 + GAMMA0 = 0.8947; mu(n=1e19)/MUN = 0.3570
GAMMA0=-0.60: gamma(300 K) = TGAMMA/T + GAMMA0 = 178.4/300 + GAMMA0 = -0.0053; mu(n=1e19)/MUN = 1.0062
GAMMA0=+0.60: gamma(300 K) = TGAMMA/T + GAMMA0 = 178.4/300 + GAMMA0 = 1.1947; mu(n=1e19)/MUN = 0.2527
ohmic strip I(0.7)/I(0.1) = 7.000; diffusion form (1-exp(-0.7/kT))/(1-exp(-0.1/kT)) = 1.0213
measured floor ratio 13.2/2.0 = 1431.7; exponent ln(ratio)/ln(13.2/2.0) = 3.851; totals x290 um: 1.337e-12 / 1.914e-09 A
lateral field 0.7 V/20 um = 350 V/cm; v = MUN(13.2) x E = 2.119e+04 cm/s
Debye length (eps 9.3, N_D 2.5e17) = 7.29 nm

## K. S4a Latin hypercube regenerated (scipy.stats.qmc, seeds 20261010 / 20261011)
cand  2: Ns=1.2038e+12 WT=0.04492 | IGZO: Ns=7.9105e+12 WT=0.03494 G0=+0.0582 | matrix Ns=1.2040e+12 WT=0.0449 Nt2=6.02e+18 IGZO {'Ns_cm2': 7910000000000.0, 'WT_eV': 0.0349, 'gamma0': 0.058} | max rel dev 0.121 %
cand  3: Ns=2.2648e+12 WT=0.02927 | IGZO: Ns=8.8748e+12 WT=0.02890 G0=-0.5251 | matrix Ns=2.2650e+12 WT=0.0293 Nt2=1.1325e+19 IGZO {'Ns_cm2': 8875000000000.0, 'WT_eV': 0.0289, 'gamma0': -0.525} | max rel dev 0.097 %
cand  4: Ns=8.8574e+12 WT=0.05724 | IGZO: Ns=3.1950e+12 WT=0.03796 G0=+0.2844 | matrix Ns=8.8570e+12 WT=0.0572 Nt2=4.4285e+19 IGZO {'Ns_cm2': 3195000000000.0, 'WT_eV': 0.038, 'gamma0': 0.284} | max rel dev 0.117 %
cand  5: Ns=2.9844e+12 WT=0.05186 | IGZO: Ns=1.2497e+12 WT=0.02736 G0=-0.1432 | matrix Ns=2.9840e+12 WT=0.0519 Nt2=1.492e+19 IGZO {'Ns_cm2': 1250000000000.0, 'WT_eV': 0.0274, 'gamma0': -0.143} | max rel dev 0.154 %
cand  6: Ns=1.5491e+12 WT=0.04886 | IGZO: Ns=2.3219e+12 WT=0.04557 G0=-0.2086 | matrix Ns=1.5490e+12 WT=0.0489 Nt2=7.745e+18 IGZO {'Ns_cm2': 2322000000000.0, 'WT_eV': 0.0456, 'gamma0': -0.209} | max rel dev 0.079 %
cand  7: Ns=6.7851e+12 WT=0.04148 | IGZO: Ns=3.9028e+12 WT=0.03586 G0=-0.0674 | matrix Ns=6.7850e+12 WT=0.0415 Nt2=3.3925e+19 IGZO {'Ns_cm2': 3903000000000.0, 'WT_eV': 0.0359, 'gamma0': -0.067} | max rel dev 0.114 %
cand  8: Ns=8.4678e+12 WT=0.03858 | IGZO: Ns=3.0275e+12 WT=0.03199 G0=-0.4042 | matrix Ns=8.4680e+12 WT=0.0386 Nt2=4.234e+19 IGZO {'Ns_cm2': 3027000000000.0, 'WT_eV': 0.032, 'gamma0': -0.404} | max rel dev 0.060 %
cand  9: Ns=4.6405e+12 WT=0.05340 | IGZO: Ns=1.7277e+12 WT=0.04465 G0=+0.1779 | matrix Ns=4.6400e+12 WT=0.0534 Nt2=2.32e+19 IGZO {'Ns_cm2': 1728000000000.0, 'WT_eV': 0.0446, 'gamma0': 0.178} | max rel dev 0.108 %
cand 10: Ns=5.9473e+12 WT=0.02660 | IGZO: Ns=1.1562e+12 WT=0.05129 G0=+0.4762 | matrix Ns=5.9470e+12 WT=0.0266 Nt2=2.9735e+19 IGZO {'Ns_cm2': 1156000000000.0, 'WT_eV': 0.0513, 'gamma0': 0.476} | max rel dev 0.018 %
cand 11: Ns=2.2777e+12 WT=0.03219 | IGZO: Ns=5.2153e+12 WT=0.05573 G0=-0.4610 | matrix Ns=2.2780e+12 WT=0.0322 Nt2=1.139e+19 IGZO {'Ns_cm2': 5215000000000.0, 'WT_eV': 0.0557, 'gamma0': -0.461} | max rel dev 0.051 %
cand 12: Ns=3.7735e+12 WT=0.03431 | IGZO: Ns=4.6483e+12 WT=0.05458 G0=+0.0884 | matrix Ns=3.7740e+12 WT=0.0343 Nt2=1.887e+19 IGZO {'Ns_cm2': 4648000000000.0, 'WT_eV': 0.0546, 'gamma0': 0.088} | max rel dev 0.041 %
cand 13: Ns=1.1018e+12 WT=0.04508 | IGZO: Ns=6.5190e+12 WT=0.05851 G0=+0.3461 | matrix Ns=1.1020e+12 WT=0.0451 Nt2=5.51e+18 IGZO {'Ns_cm2': 6519000000000.0, 'WT_eV': 0.0585, 'gamma0': 0.346} | max rel dev 0.048 %
cand 14: Ns=1.7375e+12 WT=0.03505 | IGZO: Ns=2.0700e+12 WT=0.04805 G0=+0.5432 | matrix Ns=1.7370e+12 WT=0.035 Nt2=8.685e+18 IGZO {'Ns_cm2': 2070000000000.0, 'WT_eV': 0.0481, 'gamma0': 0.543} | max rel dev 0.135 %
cand 15: Ns=3.3863e+12 WT=0.05976 | IGZO: Ns=1.5265e+12 WT=0.04131 G0=-0.3329 | matrix Ns=3.3860e+12 WT=0.0598 Nt2=1.693e+19 IGZO {'Ns_cm2': 1526000000000.0, 'WT_eV': 0.0413, 'gamma0': -0.333} | max rel dev 0.073 %
LHS worst relative deviation (incl. 4-s.f. rounding) 0.154 %

## L. Deck statements built in memory (campaign_tools.entry_deck, V3 model) vs the laws and vs the matrix params dict
entries checked: 93
  S3-01 MATRIX params.MUN_cm2Vs=12.977 vs deck-consistent 15.865 (18.20 %)
  S3-01 MATRIX params.Nc300_3d_cm3=3.218e+18 vs deck-consistent 2.38049e+18 (35.18 %)
  S3-02 MATRIX params.MUN_cm2Vs=40.2607 vs deck-consistent 42.362 (4.96 %)
  S3-02 MATRIX params.Nc300_3d_cm3=2.569e+18 vs deck-consistent 2.38049e+18 (7.92 %)
  S3-03 MATRIX params.MUN_cm2Vs=60.5388 vs deck-consistent 61.7794 (2.01 %)
  S3-03 MATRIX params.Nc300_3d_cm3=2.454e+18 vs deck-consistent 2.38049e+18 (3.09 %)
  S3-05 MATRIX params.NTA_cm3_eV=1.5873e+20 vs deck-consistent 5e+20 (68.25 %)
  S3-06 MATRIX params.NTA_cm3_eV=7.57576e+19 vs deck-consistent 5e+20 (84.85 %)
  S3-08 MATRIX params.NTA_cm3_eV=1.5873e+20 vs deck-consistent 3.29365e+20 (51.81 %)
  S3-09 MATRIX params.NTA_cm3_eV=7.57576e+19 vs deck-consistent 2.87879e+20 (73.68 %)
  S3-10 MATRIX params.NTA_cm3_eV=1.5873e+20 vs deck-consistent 0 (15873015873015870652416.00 %)
  S3-27 MATRIX params.MUN_cm2Vs=40.2607 vs deck-consistent 24.1564 (66.67 %)
  S3-24 MATRIX params.MUN_cm2Vs=12.977 vs deck-consistent 15.865 (18.20 %)
  S3-24 MATRIX params.Nc300_3d_cm3=3.218e+18 vs deck-consistent 2.38049e+18 (35.18 %)
  S3-25 MATRIX params.MUN_cm2Vs=12.977 vs deck-consistent 15.865 (18.20 %)
  S3-25 MATRIX params.Nc300_3d_cm3=3.218e+18 vs deck-consistent 2.38049e+18 (35.18 %)

## Flags (document value differs from the recomputation by > 0.5 %)
  none
```

### 6.2 `deckdiff.py`: statements of each S2/S3 deck that differ from its film baseline (S0-01 / S1-01 / S1-02); mesh lines shown only for S2-11; strip decks: interface and solve lines

```text
S2-01 (13.2 nm) vs S1-02: +6 statements
    material material=IWO user.group=semiconductor user.default=silicon eg300=3.07735 affinity=4.27653 permittivity=9.3 nc300=2.45405e+18 nv300=1e+19 mun=60.5388 mup=0.01 taun0=1e-09 taup0=1e-09 tmun=0
    models fermi srh temp=300 print trap.tunnel trap.hurkx mass.tunnel=0.2123
    defects region=1 continuous numa=384 numd=192 nta=7.57576e+19 wta=0.04 ntd=0 wtd=0.1 nga=5e+16 ega=0.6 wga=0.15 ngd=0 egd=2.97735 wgd=0.1 sigtae=1e-13 sigtah=1e-13 sigtde=1e-13 sigtdh=1e-13 siggae=1e-13 siggah=1e-13 siggde=1e-13 siggdh=1e-13 afile=acceptor_r1.
    defects region=2 continuous numa=384 numd=192 nta=7.57576e+19 wta=0.04 ntd=0 wtd=0.1 nga=1.16757e+19 ega=0.301554 wga=0.123975 ngd=0 egd=2.97735 wgd=0.1 sigtae=1e-13 sigtah=1e-13 sigtde=1e-13 sigtdh=1e-13 siggae=1e-13 siggah=1e-13 siggde=1e-13 siggdh=1e-13 afi
    method newton trap maxtraps=10 itlimit=80 climit=1e-6 ir.tol=1e-19 cr.toler=7.88e-16 xandrnorm carriers=2
    method newton trap maxtraps=10 itlimit=80 climit=1e-6 ir.tol=1e-19 cr.toler=5e-18 ^xandrnorm carriers=2
S2-02 (13.2 nm) vs S1-02: +5 statements
    models fermi temp=300 print
    defects region=1 continuous numa=384 numd=192 nta=7.57576e+19 wta=0.04 ntd=0 wtd=0.1 nga=5e+16 ega=0.6 wga=0.15 ngd=0 egd=2.97735 wgd=0.1 sigtae=1e-20 sigtah=1e-20 sigtde=1e-20 sigtdh=1e-20 siggae=1e-20 siggah=1e-20 siggde=1e-20 siggdh=1e-20 afile=acceptor_r1.
    defects region=2 continuous numa=384 numd=192 nta=7.57576e+19 wta=0.04 ntd=0 wtd=0.1 nga=1.16757e+19 ega=0.301554 wga=0.123975 ngd=0 egd=2.97735 wgd=0.1 sigtae=1e-20 sigtah=1e-20 sigtde=1e-20 sigtdh=1e-20 siggae=1e-20 siggah=1e-20 siggde=1e-20 siggdh=1e-20 afi
    method newton trap maxtraps=10 itlimit=80 climit=1e-6 ir.tol=1e-19 cr.toler=7.88e-16 xandrnorm carriers=2
    method newton trap maxtraps=10 itlimit=80 climit=1e-6 ir.tol=1e-19 cr.toler=5e-18 ^xandrnorm carriers=2
S2-03 (2.0 nm) vs S0-01: +6 statements
    material material=IWO user.group=semiconductor user.default=silicon eg300=3.37725 affinity=4.01839 permittivity=9.3 nc300=1.373e+19 nv300=1e+19 mun=12.977 mup=0.01 taun0=1e-09 taup0=1e-09 tmun=0
    models fermi srh temp=300 print trap.tunnel trap.hurkx mass.tunnel=0.2543
    defects region=1 continuous numa=384 numd=192 nta=5e+20 wta=0.04 ntd=0 wtd=0.1 nga=5e+16 ega=0.6 wga=0.15 ngd=0 egd=3.27725 wgd=0.1 sigtae=1e-13 sigtah=1e-13 sigtde=1e-13 sigtdh=1e-13 siggae=1e-13 siggah=1e-13 siggde=1e-13 siggdh=1e-13 afile=acceptor_r1.dat df
    defects region=2 continuous numa=384 numd=192 nta=5e+20 wta=0.04 ntd=0 wtd=0.1 nga=1.16757e+19 ega=0.301554 wga=0.123975 ngd=0 egd=3.27725 wgd=0.1 sigtae=1e-13 sigtah=1e-13 sigtde=1e-13 sigtdh=1e-13 siggae=1e-13 siggah=1e-13 siggde=1e-13 siggdh=1e-13 afile=acc
    method newton trap maxtraps=10 itlimit=80 climit=1e-6 ir.tol=1e-19 cr.toler=1e-17 xandrnorm carriers=2
    method newton trap maxtraps=10 itlimit=80 climit=1e-6 ir.tol=1e-19 cr.toler=5e-18 ^xandrnorm carriers=2
S2-04 (2.0 nm) vs S0-01: +7 statements
    material region=3 affinity=1.25 eg300=8.8 me.tunnel=0.35
    material region=4 affinity=2.5 eg300=5.8 me.tunnel=0.2
    contact name=gate workfunction=4.7 qtunn.cmass=1
    contact name=source exclude_near
    contact name=drain exclude_near
    models fermi srh temp=300 print qtnlsc.el qtnl.derivs
S2-05 (6.3 nm) vs S1-01: +7 statements
    material region=3 affinity=1.25 eg300=8.8 me.tunnel=0.35
    material region=4 affinity=2.5 eg300=5.8 me.tunnel=0.2
    contact name=gate workfunction=4.7 qtunn.cmass=1
    contact name=source exclude_near
    contact name=drain exclude_near
    models fermi srh temp=300 print qtnlsc.el qtnl.derivs
S2-06 (13.2 nm) vs S1-02: +7 statements
    material region=3 affinity=1.25 eg300=8.8 me.tunnel=0.35
    material region=4 affinity=2.5 eg300=5.8 me.tunnel=0.2
    contact name=gate workfunction=4.7 qtunn.cmass=1
    contact name=source exclude_near
    contact name=drain exclude_near
    models fermi srh temp=300 print qtnlsc.el qtnl.derivs
S2-07 (6.3 nm) vs S1-01: +7 statements
    material region=3 affinity=1.6 eg300=8.8 me.tunnel=0.3
    material region=4 affinity=3.2 eg300=5.8 me.tunnel=0.1
    contact name=gate workfunction=4.7 qtunn.cmass=1
    contact name=source exclude_near
    contact name=drain exclude_near
    models fermi srh temp=300 print qtnlsc.el qtnl.derivs
S2-08 (13.2 nm) vs S1-02: +7 statements
    material region=3 affinity=1.6 eg300=8.8 me.tunnel=0.3
    material region=4 affinity=3.2 eg300=5.8 me.tunnel=0.1
    contact name=gate workfunction=4.7 qtunn.cmass=1
    contact name=source exclude_near
    contact name=drain exclude_near
    models fermi srh temp=300 print qtnlsc.el qtnl.derivs
S2-09 (2.0 nm) vs S0-01: +6 statements
    material region=3 affinity=1.6 eg300=8.8 me.tunnel=0.3
    material region=4 affinity=3.2 eg300=5.8 me.tunnel=0.1
    models fermi srh temp=300 print fnord f.ae=2.171e-06 f.be=8.628e+07
S2-10 (13.2 nm) vs S1-02: +6 statements
    material region=3 affinity=1.6 eg300=8.8 me.tunnel=0.3
    material region=4 affinity=3.2 eg300=5.8 me.tunnel=0.1
    models fermi srh temp=300 print fnord f.ae=2.171e-06 f.be=8.628e+07
S2-11 (2.0 nm) vs S0-01: +9 statements
    y.mesh loc=0.002 spac=0.000125
    y.mesh loc=0.017 spac=0.0005
    material region=3 affinity=1.6 eg300=8.8 me.tunnel=0.3
    material region=4 affinity=3.2 eg300=5.8 me.tunnel=0.1
    contact name=gate workfunction=4.7 qtunn.cmass=1
    contact name=source exclude_near
    contact name=drain exclude_near
    models fermi srh temp=300 print qtnlsc.el qtnl.derivs
S2-12 (2.0 nm) vs S0-01: +8 statements
    doping region=4 uniform tat.trap conc=1e+19 acceptor sign=1e-13 sigp=1e-13 e.level=1
    material region=3 affinity=1.25 eg300=8.8 me.tunnel=0.35
    material region=4 affinity=2.5 eg300=5.8 me.tunnel=0.2
    contact name=gate workfunction=4.7 qtunn.cmass=1
    contact name=source exclude_near
    contact name=drain exclude_near
    models fermi srh temp=300 print qtnlsc.el qtnl.derivs itat.sc.el ^tat.poisson
S2-13 (13.2 nm) vs S1-02: +8 statements
    doping region=4 uniform tat.trap conc=1e+19 acceptor sign=1e-13 sigp=1e-13 e.level=1
    material region=3 affinity=1.25 eg300=8.8 me.tunnel=0.35
    material region=4 affinity=2.5 eg300=5.8 me.tunnel=0.2
    contact name=gate workfunction=4.7 qtunn.cmass=1
    contact name=source exclude_near
    contact name=drain exclude_near
    models fermi srh temp=300 print qtnlsc.el qtnl.derivs itat.sc.el ^tat.poisson
S2-14 (13.2 nm, strip deck): built separately; key lines:
    interface qf=1.38345e+12 x.min=0 x.max=24 y.min=-0.0000001 y.max=0.0000001
    solve init
    solve vstep=0.05 vfinal=0.1 name=drain
    solve vstep=0.1 vfinal=0.7 name=drain
S2-15 (2.0 nm, strip deck): built separately; key lines:
    interface qf=1.38345e+12 x.min=0 x.max=24 y.min=-0.0000001 y.max=0.0000001
    solve init
    solve vstep=0.05 vfinal=0.1 name=drain
    solve vstep=0.1 vfinal=0.7 name=drain
S2-16 (13.2 nm, strip deck): built separately; key lines:
    interface qf=0 x.min=0 x.max=24 y.min=-0.0000001 y.max=0.0000001
    solve init
    solve vstep=0.05 vfinal=0.1 name=drain
    solve vstep=0.1 vfinal=0.7 name=drain
S2-17 (2.0 nm, strip deck): built separately; key lines:
    interface qf=0 x.min=0 x.max=24 y.min=-0.0000001 y.max=0.0000001
    solve init
    solve vstep=0.05 vfinal=0.1 name=drain
    solve vstep=0.1 vfinal=0.7 name=drain
STRIP-6p3 (6.3 nm, strip deck): built separately; key lines:
    interface qf=1.38345e+12 x.min=0 x.max=24 y.min=-0.0000001 y.max=0.0000001
    solve init
    solve vstep=0.05 vfinal=0.1 name=drain
    solve vstep=0.1 vfinal=0.7 name=drain
S0-02-DOS2 (2.0 nm) vs S0-01: +9 statements
    material region=3 affinity=1.6 eg300=8.8 me.tunnel=0.3
    material region=4 affinity=3.2 eg300=5.8 me.tunnel=0.1
    contact name=gate workfunction=4.7 qtunn.cmass=1
    contact name=source exclude_near
    contact name=drain exclude_near
    models fermi srh temp=300 print qtnlsc.el qtnl.derivs
    defects region=1 continuous numa=768 numd=384 nta=5e+20 wta=0.04 ntd=0 wtd=0.1 nga=5e+16 ega=0.6 wga=0.15 ngd=0 egd=3.27725 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=acceptor_r1.dat df
    defects region=2 continuous numa=768 numd=384 nta=5e+20 wta=0.04 ntd=0 wtd=0.1 nga=1.16757e+19 ega=0.301554 wga=0.123975 ngd=0 egd=3.27725 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=acc
S3-01 (2.0 nm) vs S0-01: +3 statements
    material material=IWO user.group=semiconductor user.default=silicon eg300=3.05 affinity=4.3 permittivity=9.3 nc300=2.38049e+18 nv300=1e+19 mun=15.865 mup=0.01 taun0=1e-06 taup0=1e-06 tmun=0
    defects region=1 continuous numa=384 numd=192 nta=5e+20 wta=0.04 ntd=0 wtd=0.1 nga=5e+16 ega=0.6 wga=0.15 ngd=0 egd=2.95 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=acceptor_r1.dat dfile
    defects region=2 continuous numa=384 numd=192 nta=5e+20 wta=0.04 ntd=0 wtd=0.1 nga=1.16757e+19 ega=0.301554 wga=0.123975 ngd=0 egd=2.95 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=accept
S3-02 (6.3 nm) vs S1-01: +3 statements
    material material=IWO user.group=semiconductor user.default=silicon eg300=3.05 affinity=4.3 permittivity=9.3 nc300=2.38049e+18 nv300=1e+19 mun=42.362 mup=0.01 taun0=1e-06 taup0=1e-06 tmun=0
    defects region=1 continuous numa=384 numd=192 nta=1.5873e+20 wta=0.04 ntd=0 wtd=0.1 nga=5e+16 ega=0.6 wga=0.15 ngd=0 egd=2.95 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=acceptor_r1.dat 
    defects region=2 continuous numa=384 numd=192 nta=1.5873e+20 wta=0.04 ntd=0 wtd=0.1 nga=1.16757e+19 ega=0.301554 wga=0.123975 ngd=0 egd=2.95 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=a
S3-03 (13.2 nm) vs S1-02: +3 statements
    material material=IWO user.group=semiconductor user.default=silicon eg300=3.05 affinity=4.3 permittivity=9.3 nc300=2.38049e+18 nv300=1e+19 mun=61.7794 mup=0.01 taun0=1e-06 taup0=1e-06 tmun=0
    defects region=1 continuous numa=384 numd=192 nta=7.57576e+19 wta=0.04 ntd=0 wtd=0.1 nga=5e+16 ega=0.6 wga=0.15 ngd=0 egd=2.95 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=acceptor_r1.dat
    defects region=2 continuous numa=384 numd=192 nta=7.57576e+19 wta=0.04 ntd=0 wtd=0.1 nga=1.16757e+19 ega=0.301554 wga=0.123975 ngd=0 egd=2.95 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=
S3-04 (2.0 nm) vs S0-01: +0 statements
S3-05 (6.3 nm) vs S1-01: +2 statements
    defects region=1 continuous numa=384 numd=192 nta=5e+20 wta=0.04 ntd=0 wtd=0.1 nga=5e+16 ega=0.6 wga=0.15 ngd=0 egd=3.02236 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=acceptor_r1.dat df
    defects region=2 continuous numa=384 numd=192 nta=5e+20 wta=0.04 ntd=0 wtd=0.1 nga=1.16757e+19 ega=0.301554 wga=0.123975 ngd=0 egd=3.02236 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=acc
S3-06 (13.2 nm) vs S1-02: +2 statements
    defects region=1 continuous numa=384 numd=192 nta=5e+20 wta=0.04 ntd=0 wtd=0.1 nga=5e+16 ega=0.6 wga=0.15 ngd=0 egd=2.97735 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=acceptor_r1.dat df
    defects region=2 continuous numa=384 numd=192 nta=5e+20 wta=0.04 ntd=0 wtd=0.1 nga=1.16757e+19 ega=0.301554 wga=0.123975 ngd=0 egd=2.97735 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=acc
S3-07 (2.0 nm) vs S0-01: +0 statements
S3-08 (6.3 nm) vs S1-01: +2 statements
    defects region=1 continuous numa=384 numd=192 nta=3.29365e+20 wta=0.04 ntd=0 wtd=0.1 nga=5e+16 ega=0.6 wga=0.15 ngd=0 egd=3.02236 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=acceptor_r1.
    defects region=2 continuous numa=384 numd=192 nta=3.29365e+20 wta=0.04 ntd=0 wtd=0.1 nga=1.16757e+19 ega=0.301554 wga=0.123975 ngd=0 egd=3.02236 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afi
S3-09 (13.2 nm) vs S1-02: +2 statements
    defects region=1 continuous numa=384 numd=192 nta=2.87879e+20 wta=0.04 ntd=0 wtd=0.1 nga=5e+16 ega=0.6 wga=0.15 ngd=0 egd=2.97735 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=acceptor_r1.
    defects region=2 continuous numa=384 numd=192 nta=2.87879e+20 wta=0.04 ntd=0 wtd=0.1 nga=1.16757e+19 ega=0.301554 wga=0.123975 ngd=0 egd=2.97735 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afi
S3-10 (6.3 nm) vs S1-01: +2 statements
    defects region=1 continuous numa=384 numd=192 nta=0 wta=0.04 ntd=0 wtd=0.1 nga=5e+16 ega=0.6 wga=0.15 ngd=0 egd=3.02236 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=acceptor_r1.dat dfile=
    defects region=2 continuous numa=384 numd=192 nta=0 wta=0.04 ntd=0 wtd=0.1 nga=1.16757e+19 ega=0.301554 wga=0.123975 ngd=0 egd=3.02236 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=accepto
S3-11 (2.0 nm) vs S0-01: +1 statements
    mobility material=IWO igzo.tokyo mun=12.977 mup=0.01 tmun=0 tmup=0 igzo.gamma0=-0.31 igzo.tgamma=178.4 igzo.ncrit=1e+20
S3-12 (6.3 nm) vs S1-01: +1 statements
    mobility material=IWO igzo.tokyo mun=40.2606 mup=0.01 tmun=0 tmup=0 igzo.gamma0=-0.31 igzo.tgamma=178.4 igzo.ncrit=1e+20
S3-13 (13.2 nm) vs S1-02: +1 statements
    mobility material=IWO igzo.tokyo mun=60.5388 mup=0.01 tmun=0 tmup=0 igzo.gamma0=-0.31 igzo.tgamma=178.4 igzo.ncrit=1e+20
S3-14 (2.0 nm) vs S0-01: +1 statements
    mobility material=IWO igzo.tokyo mun=12.977 mup=0.01 tmun=0 tmup=0 igzo.gamma0=0.3 igzo.tgamma=178.4 igzo.ncrit=1e+20
S3-15 (6.3 nm) vs S1-01: +1 statements
    mobility material=IWO igzo.tokyo mun=40.2606 mup=0.01 tmun=0 tmup=0 igzo.gamma0=0.3 igzo.tgamma=178.4 igzo.ncrit=1e+20
S3-16 (13.2 nm) vs S1-02: +1 statements
    mobility material=IWO igzo.tokyo mun=60.5388 mup=0.01 tmun=0 tmup=0 igzo.gamma0=0.3 igzo.tgamma=178.4 igzo.ncrit=1e+20
S3-17 (2.0 nm) vs S0-01: +4 statements
    material material=IWO user.group=semiconductor user.default=silicon eg300=3.37725 affinity=4.01839 permittivity=9.3 nc300=1.373e+19 nv300=1e+19 mun=12.977 mup=0.01 taun0=1e-06 taup0=1e-06 tmun=0 arichn=30.558
    contact name=source workfun=4.21839 surf.rec barrier e.tunnel me.tunnel=0.25429 ^ins.ohmic
    contact name=drain workfun=4.21839 surf.rec barrier e.tunnel me.tunnel=0.25429 ^ins.ohmic
S3-18 (6.3 nm) vs S1-01: +5 statements
    material material=IWO user.group=semiconductor user.default=silicon eg300=3.12236 affinity=4.23784 permittivity=9.3 nc300=2.56928e+18 nv300=1e+19 mun=40.2606 mup=0.01 taun0=1e-06 taup0=1e-06 tmun=0 arichn=26.3
    contact name=source workfun=4.43784 surf.rec barrier e.tunnel me.tunnel=0.218856 ^ins.ohmic
    contact name=drain workfun=4.43784 surf.rec barrier e.tunnel me.tunnel=0.218856 ^ins.ohmic
S3-19 (13.2 nm) vs S1-02: +6 statements
    material material=IWO user.group=semiconductor user.default=silicon eg300=3.07735 affinity=4.27653 permittivity=9.3 nc300=2.45405e+18 nv300=1e+19 mun=60.5388 mup=0.01 taun0=1e-06 taup0=1e-06 tmun=0 arichn=25.5076
    contact name=source workfun=4.47653 surf.rec barrier e.tunnel me.tunnel=0.212263 ^ins.ohmic
    contact name=drain workfun=4.47653 surf.rec barrier e.tunnel me.tunnel=0.212263 ^ins.ohmic
S3-20 (2.0 nm) vs S0-01: +4 statements
    material material=IWO user.group=semiconductor user.default=silicon eg300=3.37725 affinity=4.01839 permittivity=9.3 nc300=1.373e+19 nv300=1e+19 mun=12.977 mup=0.01 taun0=1e-06 taup0=1e-06 tmun=0 arichn=30.558
    contact name=source workfun=4.51839 surf.rec barrier e.tunnel me.tunnel=0.25429 ^ins.ohmic
    contact name=drain workfun=4.51839 surf.rec barrier e.tunnel me.tunnel=0.25429 ^ins.ohmic
S3-21 (6.3 nm) vs S1-01: +5 statements
    material material=IWO user.group=semiconductor user.default=silicon eg300=3.12236 affinity=4.23784 permittivity=9.3 nc300=2.56928e+18 nv300=1e+19 mun=40.2606 mup=0.01 taun0=1e-06 taup0=1e-06 tmun=0 arichn=26.3
    contact name=source workfun=4.73784 surf.rec barrier e.tunnel me.tunnel=0.218856 ^ins.ohmic
    contact name=drain workfun=4.73784 surf.rec barrier e.tunnel me.tunnel=0.218856 ^ins.ohmic
S3-22 (13.2 nm) vs S1-02: +6 statements
    material material=IWO user.group=semiconductor user.default=silicon eg300=3.07735 affinity=4.27653 permittivity=9.3 nc300=2.45405e+18 nv300=1e+19 mun=60.5388 mup=0.01 taun0=1e-06 taup0=1e-06 tmun=0 arichn=25.5076
    contact name=source workfun=4.77653 surf.rec barrier e.tunnel me.tunnel=0.212263 ^ins.ohmic
    contact name=drain workfun=4.77653 surf.rec barrier e.tunnel me.tunnel=0.212263 ^ins.ohmic
S3-27 (6.3 nm) vs S1-01: +3 statements
    material material=IWO user.group=semiconductor user.default=silicon eg300=3.12236 affinity=4.23784 permittivity=9.3 nc300=2.56928e+18 nv300=1e+19 mun=24.1564 mup=0.01 taun0=1e-06 taup0=1e-06 tmun=0
    mobility material=IWO igzo.tokyo mun=24.1564 mup=0.01 tmun=0 tmup=0 igzo.gamma0=-0.31 igzo.tgamma=178.4 igzo.ncrit=1e+20
    interface qf=2.38345e+12 x.min=0 x.max=24 y.min=-0.0000001 y.max=0.0000001
S3-23 (6.3 nm) vs S1-01: +5 statements
    material material=IWO user.group=semiconductor user.default=silicon eg300=3.12236 affinity=4.23784 permittivity=9.3 nc300=2.56928e+18 nv300=1e+19 mun=40.2606 mup=0.01 taun0=1e-06 taup0=1e-06 tmun=0 arichn=26.3
    contact name=source workfun=4.73784 surf.rec e.tunnel me.tunnel=0.218856 ^ins.ohmic
    contact name=drain workfun=4.73784 surf.rec e.tunnel me.tunnel=0.218856 ^ins.ohmic
S3-24 (2.0 nm) vs S0-01: +4 statements
    material material=IWO user.group=semiconductor user.default=silicon eg300=3.05 affinity=4.3 permittivity=9.3 nc300=2.38049e+18 nv300=1e+19 mun=15.865 mup=0.01 taun0=1e-06 taup0=1e-06 tmun=0 ml=0.139 mt1=0.139 mt2=0.139
    models fermi srh temp=300 print bqp.n bqp.ngamma=1.2 bqp.nalpha=0.5 bqp.qdir=2
    defects region=1 continuous numa=384 numd=192 nta=5e+20 wta=0.04 ntd=0 wtd=0.1 nga=5e+16 ega=0.6 wga=0.15 ngd=0 egd=2.95 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=acceptor_r1.dat dfile
    defects region=2 continuous numa=384 numd=192 nta=5e+20 wta=0.04 ntd=0 wtd=0.1 nga=1.16757e+19 ega=0.301554 wga=0.123975 ngd=0 egd=2.95 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=accept
S3-25 (2.0 nm) vs S0-01: +4 statements
    material material=IWO user.group=semiconductor user.default=silicon eg300=3.05 affinity=4.3 permittivity=9.3 nc300=2.38049e+18 nv300=1e+19 mun=15.865 mup=0.01 taun0=1e-06 taup0=1e-06 tmun=0 ml=0.2543 mt1=0.2543 mt2=0.2543
    models fermi srh temp=300 print bqp.n bqp.ngamma=1.2 bqp.nalpha=0.5 bqp.qdir=2
    defects region=1 continuous numa=384 numd=192 nta=5e+20 wta=0.04 ntd=0 wtd=0.1 nga=5e+16 ega=0.6 wga=0.15 ngd=0 egd=2.95 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=acceptor_r1.dat dfile
    defects region=2 continuous numa=384 numd=192 nta=5e+20 wta=0.04 ntd=0 wtd=0.1 nga=1.16757e+19 ega=0.301554 wga=0.123975 ngd=0 egd=2.95 wgd=0.1 sigtae=1e-15 sigtah=1e-15 sigtde=1e-15 sigtdh=1e-15 siggae=1e-15 siggah=1e-15 siggde=1e-15 siggdh=1e-15 afile=accept
S3-26 (2.0 nm) vs S0-01: +1 statements
    models srh temp=300 print
AFF-2p0 (2.0 nm) vs S0-01: +1 statements
    material material=IWO user.group=semiconductor user.default=silicon eg300=3.37725 affinity=4.3 permittivity=9.3 nc300=1.373e+19 nv300=1e+19 mun=12.977 mup=0.01 taun0=1e-06 taup0=1e-06 tmun=0
AFF-6p3 (6.3 nm) vs S1-01: +1 statements
    material material=IWO user.group=semiconductor user.default=silicon eg300=3.12236 affinity=4.3 permittivity=9.3 nc300=2.56928e+18 nv300=1e+19 mun=40.2606 mup=0.01 taun0=1e-06 taup0=1e-06 tmun=0
```

### 6.3 Strict CR.TOLER check (data/experimental_clean.csv, MEASURED)

```text
2.0 median floor 4.606e-15 min active 1.369e-13 -> cr.toler 1.000e-17
6.3 median floor 1.528e-13 min active 2.284e-12 -> cr.toler 2.284e-17
13.2 median floor 6.597e-12 min active 7.879e-11 -> cr.toler 7.879e-16
```

---

## 7. Scripts (run from the scratchpad, outside the repository; reproduced here so the numbers can be regenerated)

Run: `.venv/Scripts/python.exe -I -B recompute.py "<...>/IWO_PHYSICS_CONSTRAINED_MODEL_V1"` (same for `deckdiff.py`). Both only read files and build decks in memory.

### 7.1 recompute.py

```python
"""Independent recomputation of every CALCULATED / FITTED-law number that enters the remaining C10 S2/S3/S4/S5 decks.
Read-only: reads dft_inputs.json (crystalline DFT points only), campaign_matrix.json, config/*.yaml; builds decks in memory with
campaign_tools.entry_deck (no simulator, no file writes; run with python -I -B so no .pyc is written).
Usage: python -I -B recompute.py <V1 package root>
"""
import json, math, re, sys
from pathlib import Path
import numpy as np
from scipy import integrate
from scipy.stats import qmc

ROOT = Path(sys.argv[1]); CAMP = ROOT / 'analysis_2026-10-10_campaign'
# ---------------------------------------------------------------- constants (SI 2019 exact / CODATA 2018)
q = 1.602176634e-19; h = 6.62607015e-34; hb = h / (2 * math.pi); kB = 1.380649e-23; m0 = 9.1093837015e-31; eps0 = 8.8541878128e-14  # F/cm
T = 300.0; kT = kB * T / q
FILMS = (2.0, 6.3, 13.2)
flags = []
def chk(name, doc, mine, tol=0.005):
    rel = abs(doc / mine - 1) if mine != 0 else abs(doc)
    s = 'OK' if rel <= tol else 'MISMATCH'
    if s != 'OK': flags.append(f'{name}: document {doc:.6g} vs recomputed {mine:.6g} ({rel*100:.2f} %)')
    return f'{s} ({rel*100:.3f} %)'
def hdr(s): print('\n## ' + s)

print(f'kT(300 K) = {kT:.7f} eV (CALCULATED, kB T / q)')
# ---------------------------------------------------------------- A. DFT laws refit (log least squares, as dft_to_tcad_extract.py:219)
hdr('A. DFT thickness laws a*t^-p: refit through the COMPUTED crystalline points (log least squares)')
dft = json.loads((CAMP / 'dft_inputs.json').read_text(encoding='utf-8'))
F = dft['films']; pts_t = [F[k]['thickness_HH_nm']['value'] for k in ('0.75', '1.0', '2.0')]
REG = {'dEc': (0.70147, 1.31669, 'dEc_PBE_eV'), 'dEg': (0.81431, 1.31518, 'dEg_PBE_eV'), 'dm': (0.11116, 1.26387, 'dm_PBE_m0')}
LAW = {}
for name, (a_reg, p_reg, key) in REG.items():
    ys = [F[k][key]['value'] for k in ('0.75', '1.0', '2.0')]
    A = np.vstack([np.ones(3), -np.log(pts_t)]).T
    (la, p), *_ = np.linalg.lstsq(A, np.log(ys), rcond=None); a = math.exp(la)
    LAW[name] = (a_reg, p_reg)
    res = [float(a * t ** -p / y - 1) for t, y in zip(pts_t, ys)]
    print(f'{name}: points t_HH {pts_t} -> {ys}; refit a={a:.5f} p={p:.5f} (registered a={a_reg} p={p_reg}: {chk(name+".a", a_reg, a)}, '
          f'{chk(name+".p", p_reg, p)}); rel. residuals {[round(r, 3) for r in res]}')
    print('   at 2.0/6.3/13.2 nm (registered law): ' + ', '.join(f'{a_reg * t ** -p_reg:.5f}' for t in FILMS))
dEc = lambda t: LAW['dEc'][0] * t ** -LAW['dEc'][1]
dEg = lambda t: LAW['dEg'][0] * t ** -LAW['dEg'][1]
dm = lambda t: LAW['dm'][0] * t ** -LAW['dm'][1]
mst = lambda t: 0.208 + dm(t)
DOC = {'dEc': (0.2816, 0.0622, 0.0235), 'dEg': (0.3273, 0.0724, 0.0274), 'aff': (4.0184, 4.2378, 4.2765), 'm': (0.2543, 0.2189, 0.2123),
       'nc': (1.373e19, 2.569e18, 2.454e18), 'mun': (12.98, 40.26, 60.54)}
hdr('B. Band inputs per film (CAMPAIGN_DESIGN 4.1 values checked)')
for i, t in enumerate(FILMS):
    print(f't={t}: dEc={dEc(t):.5f} {chk("dEc", DOC["dEc"][i], dEc(t))} | dEg={dEg(t):.5f} {chk("dEg", DOC["dEg"][i], dEg(t))} | '
          f'AFFINITY=4.3-dEc={4.3 - dEc(t):.5f} {chk("AFFINITY", DOC["aff"][i], 4.3 - dEc(t))} | EG300=3.05+dEg={3.05 + dEg(t):.5f} | '
          f'egd=EG300-0.1={3.05 + dEg(t) - 0.1:.5f} | m*={mst(t):.5f} {chk("m*", DOC["m"][i], mst(t))}')
print(f'HSE-high option x1.107 at 2.0 nm: dEc {1.107 * dEc(2.0):.4f} eV (S6 only)')
# ---------------------------------------------------------------- C. NC300
hdr('C. NC300: 3-D 2(2 pi m* m0 kT/h^2)^1.5 and quasi-2D N2D/t = m* m0 kT/(pi hbar^2 t)')
nc3 = lambda m: 2 * (2 * math.pi * m * m0 * kB * T / h ** 2) ** 1.5 / 1e6
n2d = lambda m: m * m0 * kB * T / (math.pi * hb ** 2) / 1e4            # cm^-2
ncq = lambda t, m: n2d(m) / (t * 1e-7)
print(f'bulk m*=0.208: NC3D={nc3(0.208):.5e} (dft_inputs 2.3805e18: {chk("Nc bulk", 2.3805e18, nc3(0.208))})')
for i, t in enumerate(FILMS):
    m = mst(t); val = ncq(t, m) if t == 2.0 else nc3(m)
    print(f't={t}: m*={m:.5f} NC3D={nc3(m):.5e} NCq2D={ncq(t, m):.5e} used={val:.5e} {chk("NC300", DOC["nc"][i], val)}')
mq = F['2.0']['mstar_TCAD_V2convention_m0']['value']
print(f'dft_inputs quasi-2D with the DFT-point mass {mq}: {ncq(2.0, mq):.5e} (file 1.3791e19) vs law mass: ratio {ncq(2.0, mq) / ncq(2.0, mst(2.0)):.5f}')
E21 = F['2.0']['E2_minus_E1_Gamma_eV']['value']
print(f'single subband: E21 = {E21} eV (COMPUTED) = {E21 / kT:.2f} kT; 10 kT = {10 * kT:.4f} eV; second-subband weight exp(-E21/kT) = {math.exp(-E21 / kT):.2e}')
r = ncq(2.0, mst(2.0)) / nc3(mst(2.0)); print(f'quasi-2D/3-D ratio {r:.4f}; equivalent Ec shift -kT ln(ratio) = {-kT * math.log(r) * 1e3:.2f} meV')
Cox = eps0 / (15e-7 / 19.57 + 2e-7 / 9.0)
N2 = n2d(mst(2.0))
for vov in (2.29, 3.0):
    ns = Cox * vov / q; eta = math.log(math.expm1(ns / N2))
    print(f'  n_s = C_ox x {vov} V / q = {ns:.3e} cm^-2 -> E_F - E1 = kT ln(exp(n_s/N2D)-1) = {eta * kT:.4f} eV (< E21 by {E21 / (eta * kT):.1f}x)')
F12 = lambda e: 2 / math.sqrt(math.pi) * integrate.quad(lambda x: math.sqrt(x) / (1 + math.exp(x - e)), 0, 80)[0]
for eta in (4.7, 4.64):
    print(f'  degenerate overstatement F1/2({eta})/ln(1+e^eta) = {F12(eta):.3f}/{math.log1p(math.exp(eta)):.3f} = {F12(eta) / math.log1p(math.exp(eta)):.3f}')
print(f'n at 2 V overdrive in 2 nm: C_ox*2/(q t) = {Cox * 2 / q / 2e-7:.3e} cm^-3')
# ---------------------------------------------------------------- D. mobility law
hdr('D. Mobility: mu_band = mu_inf (0.208/m*)/(1+l/t), MUN = mu_band (1-0.287/t)^2')
f2, f13 = 0.208 / mst(2.0), 0.208 / mst(13.2); rr = 17.6897 / 63.2597; k = f2 / f13
ell = (k - rr) / (rr / 2 - k / 13.2); muinf = 63.2597 * (1 + ell / 13.2) / f13
print(f'anchors (V2 FITTED) 17.6897 @2.0, 63.2597 @13.2 -> ell = {ell:.4f} nm, mu_inf = {muinf:.4f} cm2/Vs (design 7.25 / 100.0; matrix 7.248 / 100.005)')
for i, t in enumerate(FILMS):
    mb = muinf * (0.208 / mst(t)) / (1 + ell / t); rough = (1 - 0.287 / t) ** 2; mb0 = muinf / (1 + ell / t)
    print(f't={t}: mass factor {0.208 / mst(t):.5f}, mu_band={mb:.4f}, roughness={rough:.5f}, MUN={mb * rough:.4f} {chk("MUN", DOC["mun"][i], mb * rough)}; '
          f'no-mass-factor mu_band={mb0:.4f} -> MUN {mb0 * rough:.4f}; x0.6 MUN {mb * rough * 0.6:.4f}')
print(f'mass-only band-mobility ratio 2.0/13.2 = m*(13.2)/m*(2.0) = {mst(13.2) / mst(2.0):.4f} (design 0.83, register forecast 0.835)')
# ---------------------------------------------------------------- E. traps
hdr('E. Tail and interface DOS')
for Ns, WT in ((4e12, 0.040),):
    for t in FILMS:
        Nt = Ns / (t * 1e-7); print(f'Ns={Ns:.3g}, WT={WT}: t={t}: Nt=Ns/t={Nt:.4e} NTA=Nt/WT={Nt / WT:.4e}; bulk-only Nt={Ns / 2e-7:.4e}; '
                                     f'50:50 Nt={Ns / 2 / (t * 1e-7) + Ns / 2 / 2e-7:.4e}')
print(f'Nt2 = Ns/2 nm = {4e12 / 2e-7:.4e}; Tt = WT/kB = {0.04 / (kB / q):.1f} K')
a_i = 3e11 / 0.25e-7
def mmg(a_b, w_b, e_b, a_i, w_i, e_i):
    mass = a_b * w_b + a_i * w_i; e = (a_b * w_b * e_b + a_i * w_i * e_i) / mass
    var = (a_b * w_b * (w_b ** 2 / 2 + (e_b - e) ** 2) + a_i * w_i * (w_i ** 2 / 2 + (e_i - e) ** 2)) / mass
    w = math.sqrt(2 * var); return e, w, mass / w
e, w, n = mmg(5e16, 0.15, 0.6, a_i, 0.12, 0.3)
print(f'interface sheet 3e11 cm^-2/eV / 0.25 nm = {a_i:.4e} cm^-3/eV; region-2 moment-matched Gaussian: nga={n:.6g} ega={e:.6g} wga={w:.6g} '
      f'(run_0061 deck 1.16757e19 / 0.301554 / 0.123975)')
# ---------------------------------------------------------------- F. C_ox and Q_f
hdr('F. Gate stack and Q_f')
CHf, CAl = eps0 * 19.57 / 15e-7, eps0 * 9.0 / 2e-7
print(f'C_HfO2={CHf:.5e}, C_Al2O3={CAl:.5e}, C_ox(series)={Cox:.5e} F/cm2 (deck header 8.9554e-07: {chk("Cox", 8.9554e-7, Cox)}); EOT={3.9 * 8.8541878128e-14 / Cox * 1e7:.3f} nm (k_SiO2 3.9 LITERATURE)')
print(f'Q_f 1.38345e12 -> dV_FB = -q Q_f / C_ox = {-q * 1.38345e12 / Cox:.5f} V (deck -0.2475); dV0 0.5 V <-> dQf {0.5 * Cox / q:.4e} cm^-2; '
      f'range {1.38345e12 - 0.5 * Cox / q:.3e} .. {1.38345e12 + 0.5 * Cox / q:.3e} (design -1.4e12 .. 4.2e12)')
print(f'S1-07 / S3-27 dQf = +1e12 -> rigid shift {-q * 1e12 / Cox:.4f} V')
for ea in (7.0, 11.0):
    c = eps0 / (15e-7 / 19.57 + 2e-7 / ea); print(f'  S6 eps_Al2O3={ea}: C_ox={c:.4e} ({(c / Cox - 1) * 100:+.2f} %)')
# ---------------------------------------------------------------- G. Schottky
hdr('G. Schottky branch')
Astar = 4 * math.pi * q * m0 * kB ** 2 / h ** 3 / 1e4
print(f'free-electron Richardson constant 4 pi q m0 kB^2/h^3 = {Astar:.3f} A/cm2/K2 (physics_options 120.17: {chk("A*", 120.17, Astar)})')
for t in FILMS:
    print(f't={t}: ARICHN=120.17 m*={120.17 * mst(t):.3f}; workfun=AFFINITY+0.2/0.5 = {4.3 - dEc(t) + 0.2:.4f} / {4.3 - dEc(t) + 0.5:.4f} eV; me.tunnel = m* = {mst(t):.4f}')
# ---------------------------------------------------------------- H. FN constants
hdr('H. FNORD constants (Lenzlinger-Snow form) and field transfer')
def AB(phi, mr):
    phiJ = phi * q
    A = q ** 3 / (8 * math.pi * h * phiJ) / mr                                  # A/V^2
    B = 8 * math.pi * math.sqrt(2 * mr * m0) * phiJ ** 1.5 / (3 * q * h) / 100   # V/cm
    return A, B
rfn = 19.57 / 9.0
print(f'prefactors: q^3/(8 pi h q) = {q ** 3 / (8 * math.pi * h * q):.5e} A/V^2 (x 1/(phi m_r)); 8 pi sqrt(2 m0) q^1.5/(3 q h) = {8 * math.pi * math.sqrt(2 * m0) * q ** 1.5 / (3 * q * h) / 100:.5e} V/cm (x sqrt(m_r) phi^1.5); r = eps_HfO2/eps_Al2O3 = {rfn:.5f}')
for name, phi, mr, fae_doc, fbe_doc in (('nominal', 2.2, 0.20, 7.402e-7, 2.167e8), ('worst', 1.5, 0.10, 2.171e-6, 8.628e7), ('nominal, chi_HfO2=4.05-1.5=2.55', 2.15, 0.20, None, None)):
    A, B = AB(phi, mr); fae, fbe = A / rfn ** 2, B * rfn
    s = f'{name}: phi={phi} eV m_r={mr}: A={A:.4e} A/V^2, B={B:.4e} V/cm -> F.AE=A/r^2={fae:.4e}, F.BE=rB={fbe:.4e}'
    if fae_doc: s += f'  [F.AE {chk("F.AE " + name, fae_doc, fae)}, F.BE {chk("F.BE " + name, fbe_doc, fbe)}]'
    print(s)
for E in (3e6, 5e6):   # V/cm in HfO2: J ratio nominal 2.55-chi vs 2.5-chi
    A1, B1 = AB(2.2, 0.2); A2, B2 = AB(2.15, 0.2)
    print(f'  sensitivity at E_HfO2={E:.0e} V/cm: J(phi 2.15)/J(phi 2.2) = {A2 * math.exp(-B2 / E) / (A1 * math.exp(-B1 / E)):.2f}')
hdr('I. Barrier heights implied by the oxide sets (CALCULATED from the deck affinities)')
for sname, cH, cA in (('nominal', 2.5, 1.25), ('worst', 3.2, 1.6)):
    print(f'{sname}: TiN(4.7)/HfO2 {4.7 - cH:.2f} eV; TiN/Al2O3 {4.7 - cA:.2f} eV; ' + '; '.join(
        f'IWO({t})/Al2O3 {4.3 - dEc(t) - cA:.3f}, IWO/HfO2 {4.3 - dEc(t) - cH:.3f}' for t in FILMS))
print(f'Robertson-2000 route (UNVERIFIED digits): chi = chi_Si 4.05 - CBO: HfO2 4.05-1.5 = 2.55 (used 2.5: {abs(2.5 / 2.55 - 1) * 100:.1f} %); Al2O3 4.05-2.8 = 1.25')
# ---------------------------------------------------------------- J. IGZO, strip, floors
hdr('J. IGZO.TOKYO exponent, strip ratio, floors')
for g0 in (-0.31, 0.30, -0.6, 0.6):
    print(f'GAMMA0={g0:+.2f}: gamma(300 K) = TGAMMA/T + GAMMA0 = 178.4/300 + GAMMA0 = {178.4 / 300 + g0:.4f}; mu(n=1e19)/MUN = {(1e19 / 1e20) ** ((178.4 / 300 + g0) / 2):.4f}')
print(f'ohmic strip I(0.7)/I(0.1) = {0.7 / 0.1:.3f}; diffusion form (1-exp(-0.7/kT))/(1-exp(-0.1/kT)) = {(-math.expm1(-0.7 / kT)) / (-math.expm1(-0.1 / kT)):.4f}')
fl = (4.61e-15, 1.53e-13, 6.60e-12)
print(f'measured floor ratio 13.2/2.0 = {fl[2] / fl[0]:.1f}; exponent ln(ratio)/ln(13.2/2.0) = {math.log(fl[2] / fl[0]) / math.log(6.6):.3f}; '
      f'totals x290 um: {fl[0] * 290:.3e} / {fl[2] * 290:.3e} A')
print(f'lateral field 0.7 V/20 um = {0.7 / 20e-4:.0f} V/cm; v = MUN(13.2) x E = {60.54 * 350:.3e} cm/s')
print(f'Debye length (eps 9.3, N_D 2.5e17) = {math.sqrt(9.3 * eps0 * kT / (q * 2.5e17)) * 1e7:.2f} nm')
# ---------------------------------------------------------------- K. LHS
hdr('K. S4a Latin hypercube regenerated (scipy.stats.qmc, seeds 20261010 / 20261011)')
mx = json.loads((CAMP / 'campaign_matrix.json').read_text(encoding='utf-8'))
lhs2 = qmc.LatinHypercube(d=2, seed=20261010).random(14); lhs3 = qmc.LatinHypercube(d=3, seed=20261011).random(14)
runs = {r_['id']: r_ for r_ in mx['runs']}
worst = 0.0
for i in range(14):
    ns, wt = 10 ** (12 + lhs2[i][0]), 0.025 + 0.035 * lhs2[i][1]
    ns3, wt3, g3 = 10 ** (12 + lhs3[i][0]), 0.025 + 0.035 * lhs3[i][1], -0.6 + 1.2 * lhs3[i][2]
    p = runs[f'S4A-{i + 2:02d}-2p0']['params']; ig = p['if_igzo_branch_adopted']
    ov = {o.split('=')[0]: o.split('=')[1] for o in runs[f'S4A-{i + 2:02d}-2p0']['campaign_entry']['overrides']}
    d = max(abs(p['Ns_cm2'] / ns - 1), abs(p['WT_eV'] / wt - 1), abs(ig['Ns_cm2'] / ns3 - 1), abs(ig['WT_eV'] / wt3 - 1), abs(ig['gamma0'] - g3) / 1.2,
            abs(float(ov['thickness_laws.Nt_cm3.Nt2']) / (ns / 2e-7) - 1)); worst = max(worst, d)
    print(f'cand {i + 2:2d}: Ns={ns:.4e} WT={wt:.5f} | IGZO: Ns={ns3:.4e} WT={wt3:.5f} G0={g3:+.4f} | matrix Ns={p["Ns_cm2"]:.4e} WT={p["WT_eV"]} Nt2={ov["thickness_laws.Nt_cm3.Nt2"]} '
          f'IGZO {ig} | max rel dev {d * 100:.3f} %')
print(f'LHS worst relative deviation (incl. 4-s.f. rounding) {worst * 100:.3f} %')
# ---------------------------------------------------------------- L. deck-level check of every planned_fixed S2/S3/S4a entry
hdr('L. Deck statements built in memory (campaign_tools.entry_deck, V3 model) vs the laws and vs the matrix params dict')
sys.path.insert(0, str(CAMP)); import campaign_tools as ct  # noqa: E402
def kv(line):
    return {m_.group(1).lower(): m_.group(2) for m_ in re.finditer(r'([A-Za-z0-9_.]+)=([^\s]+)', line)}
def joined(text):
    out, cur = [], ''
    for l in text.splitlines():
        if l.lstrip().startswith('#'): continue
        if l.rstrip().endswith('\\'): cur += l.rstrip()[:-1] + ' '; continue
        out.append(cur + l); cur = ''
    return out
nchk = 0; probs = []
for r_ in mx['runs']:
    if r_['status'] != 'planned_fixed' or not r_['stage'].startswith(('S2', 'S3', 'S4a')): continue
    e = dict(r_['campaign_entry']); t = float(e['thickness']); ov = {}
    for o in e.get('overrides', []): kk, vv = o.split('=', 1); ov[kk] = vv
    try:
        txt, meta = ct.entry_deck(e, ct.V3)
    except Exception as ex:
        probs.append(f'{e["id"]}: deck build failed {ex!r}'); continue
    L = joined(txt); mat = next((kv(l) for l in L if l.startswith('material material=IWO')), {})
    d1 = next((kv(l) for l in L if l.startswith('defects region=1')), {}); dop = next((kv(l) for l in L if l.startswith('doping uniform n.type')), {})
    itf = next((kv(l) for l in L if l.startswith('interface qf=')), {}); mob = next((kv(l) for l in L if l.startswith('mobility material=IWO')), {})
    a_c = float(ov.get('thickness_laws.dEc_eV.a', 0.70147)); a_g = float(ov.get('thickness_laws.dEg_QC_eV.a', 0.81431)); b_m = float(ov.get('thickness_laws.mstar_m0.b', 0.11116))
    m_ = 0.208 + b_m * t ** -1.26387
    nc_e = float(ov[f'solver.physics_options.nc300_override_cm3[{t}]']) if f'solver.physics_options.nc300_override_cm3[{t}]' in ov else nc3(m_)
    Nt_e = float(ov['thickness_laws.Nt_cm3.Nt2']) * (2 / t) ** float(ov['thickness_laws.Nt_cm3.alpha']) + float(ov.get('solver.physics_options.nt_bulk_cm3', 0))
    WT_e = float(ov['thickness_laws.WTA_eV.value']); mb_e = float(ov[f'thickness_laws.mu0_cm2Vs.mu_band_fitted[{t}]']); mun_e = mb_e * (1 - 0.287 / t) ** 2
    exp_ = {'affinity': 4.3 - a_c * t ** -1.31669, 'eg300': 3.05 + a_g * t ** -1.31518, 'nc300': nc_e, 'mun': mun_e}
    got = {'affinity': float(mat.get('affinity', 'nan')), 'eg300': float(mat.get('eg300', 'nan')), 'nc300': float(mat.get('nc300', 'nan')),
           'mun': float(mob['mun']) if mob else float(mat.get('mun', 'nan'))}
    if Nt_e > 0: exp_['nta'] = Nt_e / WT_e; got['nta'] = float(d1.get('nta', 'nan'))
    exp_['conc'] = float(ov['thickness_laws.Nd_eff_cm3.Nd0']); got['conc'] = float(dop.get('conc', 'nan'))
    exp_['qf'] = float(ov['traps.fixed_interface_charge_Qf_cm2.value']); got['qf'] = float(itf.get('qf', 'nan'))
    if 'arichn' in mat: exp_['arichn'] = 120.17 * m_; got['arichn'] = float(mat['arichn'])
    for kk in exp_:
        if exp_[kk] == 0 and got[kk] == 0: continue
        rel = abs(got[kk] / exp_[kk] - 1) if exp_[kk] else abs(got[kk])
        if not rel <= 5e-4: probs.append(f'{e["id"]} deck {kk}={got[kk]:.6g} vs law {exp_[kk]:.6g} ({rel * 100:.3f} %)')
    p = r_['params']; pmap = {'affinity_eV': exp_['affinity'], 'Nc300_cm3': nc_e, 'MUN_cm2Vs': mun_e, 'mu_band_cm2Vs': mb_e, 'mstar_m0': m_, 'Nt_cm3': Nt_e,
                              'NTA_cm3_eV': Nt_e / WT_e if WT_e else 0, 'Qf_cm2': exp_['qf'], 'WT_eV': WT_e}
    if 'Nc300_3d_cm3' in p: pmap['Nc300_3d_cm3'] = nc3(m_)
    for kk, vv in pmap.items():
        if kk in p and isinstance(p[kk], (int, float)) and not (vv == 0 and p[kk] == 0):
            rel = abs(p[kk] / vv - 1) if vv else abs(p[kk])
            if rel > 0.005: probs.append(f'{e["id"]} MATRIX params.{kk}={p[kk]:.6g} vs deck-consistent {vv:.6g} ({rel * 100:.2f} %)')
    sc = p.get('schottky') or {}
    if 'workfun_eV' in sc:
        wf = next((float(kv(l)['workfun']) for l in L if l.startswith('contact name=source')), float('nan'))
        if abs(wf - sc['workfun_eV']) > 5e-4: probs.append(f'{e["id"]} Schottky workfun deck {wf} vs params {sc["workfun_eV"]}')
    ig = p.get('igzo') or {}
    if 'mun' in ig and mob and abs(float(mob['mun']) / ig['mun'] - 1) > 0.005: probs.append(f'{e["id"]} params.igzo.mun={ig["mun"]} vs deck mobility mun={mob["mun"]}')
    nchk += 1
print(f'entries checked: {nchk}')
for s in probs: print('  ' + s)
hdr('Flags (document value differs from the recomputation by > 0.5 %)')
for s in flags: print('  ' + s)
if not flags: print('  none')
```

### 7.2 deckdiff.py

```python
"""Statements of every planned_fixed S2/S3 entry that differ from its film's primary baseline deck (in-memory build; no writes)."""
import json, sys, difflib
from pathlib import Path
CAMP = Path(sys.argv[1]) / 'analysis_2026-10-10_campaign'
sys.path.insert(0, str(CAMP)); import campaign_tools as ct  # noqa: E402
mx = json.loads((CAMP / 'campaign_matrix.json').read_text(encoding='utf-8')); R = {r['id']: r for r in mx['runs']}
def joined(text):
    out, cur = [], ''
    for l in text.splitlines():
        if l.lstrip().startswith('#') or not l.strip(): continue
        if l.rstrip().endswith('\\'): cur += l.rstrip()[:-1] + ' '; continue
        out.append(' '.join((cur + l).split())); cur = ''
    return out
base = {2.0: 'S0-01', 6.3: 'S1-01', 13.2: 'S1-02'}
B = {t: joined(ct.entry_deck(R[i]['campaign_entry'], ct.V3)[0]) for t, i in base.items()}
for r in mx['runs']:
    if r['status'] != 'planned_fixed' or not r['stage'].startswith(('S2', 'S3')): continue
    e = r['campaign_entry']; t = float(e['thickness'])
    if e.get('mode') == 'strip':
        print(f'{e["id"]} ({t} nm, strip deck): built separately; key lines:')
        for l in joined(ct.entry_deck(e, ct.V3)[0]):
            if l.startswith(('interface', 'electrode', 'solve', 'region', 'contact')): print('    ' + l[:200])
        continue
    S = joined(ct.entry_deck(e, ct.V3)[0])
    add = [l for l in S if l not in B[t]]
    print(f'{e["id"]} ({t} nm) vs {base[t]}: +{len(add)} statements')
    for l in add:
        if l.startswith(('solve', 'log', 'save', 'extract', 'output', 'probe', 'tonyplot')): continue
        print('    ' + l[:260])
```
