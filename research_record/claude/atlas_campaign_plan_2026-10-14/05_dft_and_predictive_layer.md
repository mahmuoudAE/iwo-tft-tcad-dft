# 05: DFT inputs and the predictive layer (C10 campaign plan, 2026-10-14)

**Status: PLAN (proposal).** Nothing was launched, committed or pushed. No registered file, config, data, result, register or ledger was edited. Every amendment and launch proposed here needs a Codex review, a manual check against the ATLAS 5.28 manual text (the TCAD check rule) and the user's go.

**What I read.**
- Read in full: `CAMPAIGN_DESIGN.md`, `DFT_TO_TCAD.md` and `HF_DEFINITIONS_DRAFT_2026-10-13.md`.
- Read in part:
  - `dft_inputs.json`: laws, films, bulk, hse_check;
  - `profile_s4s5.py`: docstring, `loo_select`, `loo_score`, `jac_analysis`, `jacobian`, `sensitivity`. Its sha256 is `429b3a3f…`, the frozen v4 file;
  - `profile_shared.py`: `mu_law`, `transformed_log`;
  - `scripts/run_atlas.py`: the predict, output and strip paths;
  - `scripts/run_campaign.py`: the dispatch code;
  - `scripts/build_iwo_decks.py`: T handling, `read_meas`, `law`/points;
  - `campaign_matrix.json`: S5–S7 rows and counts;
  - `results/RUN_INDEX.csv`: labels only;
  - register H-A to H-K, A41 and §3;
  - work chat: the S2-11 digest with the Codex reply of 2026-10-13T03:36Z, and the v4 freeze of 08:49Z;
  - `01_CURRENT_STATE.md`;
  - the summary fields of `register_scores/hc_mesh_run_0076_run_0067.json`.
- Crystalline DFT only:
  - `bands_masses/BANDS_MASSES.md` §1–7;
  - `DFT_FULL_STUDY.md` summary, §1–8 and §11;
  - `runs_sep_oct/MASTER_TABLE.md`: key findings and the run table. All 41 folders are crystalline.

**What I did not open:** any `results/runs/*` directory, any `sealed/` folder, the AFF-6p3 or STRIP-6p3 outputs, `DFT_FULL_STUDY.md` §12–15 (§13 holds the amorphous force checks), and every amorphous electronic quantity.

**Labels.**
- MEASURED: the fab's devices, via `01_CURRENT_STATE.md` §D.
- COMPUTED: our crystalline DFT, with the file cited.
- LITERATURE: a full citation. For journal papers the citation and DOI are as checked in `BANDS_MASSES.md` §5 on 2026-10-14; I did not re-check them here.
- CALCULATED: the formula and inputs are shown, and the arithmetic is in `scratchpad/calc05.py`.
- FITTED and ASSUMED: as in the charter.
- Launch counts are plan quantities (ASSUMED design choices). Sums and counts of records are CALCULATED.

---

## 1. Bottom line

### (a) DFT inputs

1. **No frozen DFT input is contradicted.** The independent re-derivation of 2026-10-13/14 reproduces every frozen law and every deck value.
   - dEc fit3: 0.70176·t^−1.3176 against frozen 0.70147·t^−1.31669. Both are FITTED to the COMPUTED 0.695/0.930/1.962 nm points.
   - At 2.0 / 6.3 / 13.2 nm the re-derived law gives 0.2815 / 0.0621 / 0.0234 eV, against frozen 0.2816 / 0.0622 / 0.0235 eV (CALCULATED).
   - The C10 deck AFFINITY and EG300 values are reproduced within 0.2 meV, and NC300 within 0.27 % (`DFT_FULL_STUDY.md` §4).
   - dEg, Δm*, E21, the HSE ratio (1.0599–1.1071) and the quasi-2D NC300 at 2 nm (1.373e19 against 1.374e19 cm⁻³) all agree.
2. **One new crystalline fact enlarges an uncertainty but does not change a value.** The 0.695 nm slab is polar.
   - Its vacuum ramp is −347.1 meV, where 27 meV of asymmetry had been recorded (COMPUTED, `slabL2_relax_v2_avg.dat`).
   - So the EA-route point dEc(0.695) = 1.0589 eV carries a ±0.1736 eV reference-choice sensitivity (ASSUMED half-ramp, not a bound).
   - Propagated through fit3, dEc(6.3 nm) spans 0.0531–0.0746 eV. The registered S6 band was 0.046–0.062 eV, plus S6-05 HSE at 0.0688.
   - After the shared ΔV₀ absorbs the common part, the remaining film-to-film differential is at most 3.4 meV (CALCULATED, §2.1). That is negligible against the ±0.10 V acceptance and against H-E's "crystalline-input uncertainty < 0.10 V".
3. **Every other new crystalline result moves a deck quantity by at most about 3 meV-equivalent, or enters only n_i.** These are:
   - the Kane non-parabolicity;
   - band-edge versus 3-point masses;
   - the W-induced mass increase of +5 to +7.5 %;
   - the HSE mass estimates;
   - the computed N_v, about 190 times the deck NV300;
   - the corrected sign of dEv(1 nm).
4. **Recommendation: do not amend the frozen fit3 law.**
   - An amendment now would be result-informed: S0/S1/S2-11 were seen first.
   - It cannot change runs 0061–0077.
   - It would split the S3/S4 archive, because `require_shared_model` refuses mixed non-fitted settings.
   - Instead:
     - (i) log a disclosure caveat;
     - (ii) propagate the dEc variants offline at **zero launches** by exact per-film affinity shifts, conditional on the registered AFF-2p0/AFF-6p3 rigidity test;
     - (iii) before freezing any sub-2 nm prediction, run the dipole-corrected 0.75 nm SCF (`BANDS_MASSES.md` §6 item 7, about 3 h). Below 2 nm the dEc input is the dominant uncertainty (±0.10 to ±0.19 eV).

### (b) Predictive layer

- **Three classes, never mixed:**
  - calibration: S4;
  - retrospective leave-one-film-out: S5, with the frozen `s4s5-hf-v4` code;
  - prospective: P1–P5, frozen after S4c and S5 and before any new measurement, through `predictions/registered/` (charter §7).
- **Free uncertainty propagation (0 launches)** covers:
  - the profiled nuisances ΔV₀/Q_f, μ∞ and ℓ (exact shift and scale);
  - the DFT dEc spread and the HSE factor (rigid shifts, conditional on AFF);
  - uniform mass factors (the μ part is exact; the NC part is ≤ 2.8 meV).
- **Launches are needed for:**
  - the NC convention (non-rigid; S1-05 gave +142 mV);
  - the launched parameters N_s, W_T and GAMMA0;
  - temperature, V_D and thickness.
- **Cost.**
  - S5: 30 launches (registered).
  - Prospective layer: 32 (full) or 12 (minimum).
  - Gates tie each product to the S4c/S5 outcome, so a failed shared model spends little.
- **Code items before any prospective launch:**
  - `run_campaign.py` cannot yet pass `predict`;
  - NC.F = 1 for the quasi-2D NC at T ≠ 300 K;
  - the output and strip modes at an unmeasured thickness;
  - dry builds of every new deck.

---

## 2. Part A: frozen DFT inputs against the new crystalline analyses

**Sources.**
- Frozen: `analysis_2026-10-10_campaign/dft_inputs.json` (generated 2026-10-10T10:46Z), `DFT_TO_TCAD.md`, and model V3 (`config/iwo_material_model_v3.yaml`, as quoted in `IMPLEMENTATION.md` §4).
- New: `qe_workflow/analysis_2026-10-13_full/bands_masses/BANDS_MASSES.md` (BM), `DFT_FULL_STUDY.md` (FS) and `runs_sep_oct/MASTER_TABLE.md` (MT).
- All new numbers are PBE (PAW, 71 Ry) unless marked HSE06.

### 2.1 Laws at the device thicknesses (eV, or m0 for Δm)

| Quantity | Frozen (dft_inputs.json) | New re-derivation | Δ at 2.0 / 6.3 / 13.2 nm | Label | Verdict |
|---|---|---|---|---|---|
| dEc fit3 | 0.70147·t^−1.31669 → 0.2816 / 0.0622 / 0.0235 | 0.70176·t^−1.3176 → 0.2815 / 0.0621 / 0.0234 (FS §4, BM §3.1) | −0.1 / −0.1 / −0.1 meV | FITTED to COMPUTED points; Δ CALCULATED | agrees |
| dEc fit2 (0.930 + 1.962 nm only) | 0.76158·t^−1.47779 → 0.2734 / 0.0502 / 0.0168 (diagnostic) | 0.76182·t^−1.47845 → 0.2734 / 0.0501 / 0.0168 | 0 | FITTED | agrees. Codex (2026-10-13) wants it as the primary *for any new fit* until a dipole-corrected 0.75 nm point exists |
| dEc, 0.695 point moved by −0.1736 / +0.1736 eV | not recorded (only a 27 meV asymmetry) | 0.2888 / 0.0746 / 0.0312 and 0.2756 / 0.0531 / 0.0184 (BM §3.1, fit3_0p695_low / _high) | +7.2 / +12.5 / +7.7 and −6.0 / −9.1 / −5.1 meV vs frozen | FITTED; ±0.1736 ASSUMED reference sensitivity | **new uncertainty**, outside the registered S6 band at 6.3 nm (0.046–0.062) by up to 12.6 meV (vs S6-05 HSE 0.0688: 5.8 meV) |
| dEc, HSE ×r (r = 1.0599 / 1.1071) | ×1.0599–1.1071, ASSUMED transfer from 1 nm | same r (FS §4) | +16.9 / +3.7 / +1.4 (r1); +30.2 / +6.7 / +2.5 meV (r3) | r COMPUTED at 1 nm only; transfer ASSUMED | agrees; still measured at 1 nm only |
| dEg fit3 | 0.81431·t^−1.31518 → 0.3273 / 0.0724 / 0.0274 | 0.81466·t^−1.3155 → 0.3273 / 0.0724 / 0.0273 | ≤ 0.1 meV | FITTED | agrees. Enters only n_i (holes not solved) |
| Δm* fit3 (deck basis, 3-point) | 0.11116·t^−1.26387 → 0.0463 / 0.0109 / 0.0043 | 0.11144·t^−1.2611 → 0.0465 / 0.0109 / 0.0043; band-edge (Kane) basis 0.1145·t^−1.2755 → 0.0473 / 0.0109 / 0.0043 (BM §2.7) | ≤ +0.0010 m0 | FITTED | agrees; basis effect ≤ 0.4 % in m*(2 nm) |
| Subband box MODEL (δ 1.396 nm, m_z 0.139 m0) | low-end dEc 0.2344 / 0.0456 / 0.0127; NC ×1.467 at 6.3 nm | not re-derived (E21 points re-derived: 0.7191 / 1.4988 eV, match) | — | MODEL | unchanged |

**Effect on the calibration (CALCULATED).**
- The shared Q_f profiles a common V_G shift away exactly (CAMPAIGN_DESIGN §5.2).
- Only the per-film differential δ_t − mean(δ) survives. Per variant:

  | Variant | Differential at 2.0 / 6.3 / 13.2 nm |
  |---|---|
  | fit2 | +0.8 / −3.1 / +2.3 meV |
  | 0.695 point at −0.1736 eV | −2.0 / +3.4 / −1.4 meV |
  | 0.695 point at +0.1736 eV | +0.7 / −2.3 / +1.6 meV |
  | HSE r3 | +17.1 / −6.4 / −10.6 meV (already registered as S6-04..06) |

- Under the registered AFF expectation (ΔV_th,cc = +Δ(dEc), 1:1 within ±5 mV; H-E/A13), this is a 3.4 mV differential at most for the new polar sensitivity, and 17 mV for HSE.
- Measured against the 0.23–0.37 V 6.3 nm miss and the 0.10 V acceptance, **the new DFT information cannot change any calibration verdict.**

### 2.2 The DFT points behind the laws (COMPUTED)

| Point (t_HH, nm) | Quantity | Frozen | New | Note |
|---|---|---|---|---|
| 1.962 (2 nm) | gap / dEg | 1.2239 / 0.3352 | 1.2239 / 0.3352 | GPU 7.3.1 and CPU 7.5 reruns agree within 0.1 meV (FS §3) |
| 1.962 | dEc two-step, a/2 window | 0.2813 | 0.2812 (a/2); 0.2866 (a/2·a/4 window) | bulk ⟨V⟩ independently re-derived by the UPF G = 0 route, 4.16867 eV, validated on 10 slabs to 0.0 meV (FS §2). The window choice adds +5.4 meV at 2 nm only |
| 1.962 | m* [100] 3-point / Kane band edge | 0.2064 / — | 0.2064 / 0.2026 | basis difference −1.8 % (BM §2.3) |
| 1.962 | E21 | 0.7191 | 0.7191 | single subband (> 10 kT) confirmed |
| 0.930 (1 nm) | dEc (EA route) / dEg | 0.8478 / 0.8998 | 0.8477 / 0.8998 | the two-step route has no interior plateau (spread 69 meV) |
| 0.930 | dEv | −0.052 | −0.0521 (sign error in RESULTS_LOG −0.056 corrected 2026-10-14, FS §8 item 1) | not used in TCAD |
| 0.695 (0.75 nm) | dEc / dEg / Δm | 1.0586 / 1.3099 / 0.1758 | 1.0589 ± 0.1736 / 1.3099 / 0.176 | **polar slab** (4 symmetry operations, no dipole correction), FS §3. dEg is independent of the vacuum reference; its sensitivity to the artificial field is untested |
| 0.461 (0.51 nm) | — | excluded (In(OH)3-like) | confirmed In8(OH)24 (FS §3) | outside every law |
| bulk | HSE06 gap; r | 2.0662–2.108 eV; 1.0599 / 1.1071 | same (FS §4, MT) | 89 of 92 RESULTS_LOG values re-derived; the 3 that differ are job metadata (MT) |

### 2.3 New crystalline findings that the frozen inputs do not contain, and their TCAD size

| Finding (new) | Value | Label | TCAD size | Size label |
|---|---|---|---|---|
| CB non-parabolicity (Kane α) | 0.584 1/eV bulk (range 0.551–0.63); 0.47 at 2 nm | COMPUTED (BM §2.1, §2.7) | NC +5.7 % (3-D) / +2.5 % (quasi-2D) ⇒ kT·ln(1.057) = 1.43 meV, kT·ln(1.025) = 0.64 meV. Degenerate conductivity mass m(1 + 2αE_F) = ×1.113 at 2 nm with E_F − E_1 = 0.12 eV (DFT_TO_TCAD §3) ⇒ ≤ 0.047 dec on I_D(3 V) at 2 nm, a shape term the parabolic DD deck cannot carry | CALCULATED (E_F from the frozen design note) |
| Band-edge vs 3-point mass basis | bulk 0.1541 vs 0.1588 m0 (−3 %) | COMPUTED | none on Δm (increments ≤ 0.001 m0); the deck uses 0.208 + Δm | CALCULATED |
| W raises the host-CB mass | +5 % bulk (COMPUTED); +6.5 / +7.5 % at 1 / 2 nm (ESTIMATED from the SCF grid; no W-slab band run) | COMPUTED / ESTIMATED (BM §2.5) | a uniform factor on m* is absorbed exactly by μ∞ (μ_law ∝ 1/m*). NC part ×1.076–1.115 ⇒ 1.9–2.8 meV equivalent | CALCULATED |
| HSE06 mass | bulk 0.1541 → 0.159–0.193 m0; 1 nm 0.2793 → 0.283–0.293 | ESTIMATED (3 grid points, BM §2.6; "model sensitivity, not an uncertainty bound") | supports D3 (PBE underestimates the mass); Δm(1 nm, HSE) 0.090–0.134 brackets PBE 0.125: not resolved | — |
| Computed N_v | 1.93e21 cm⁻³ (grid spread 1.92–2.67e21) against deck NV300 1e19 | COMPUTED vs ASSUMED (BM §2.2, §4) | n_i = √(N_c N_v)·exp(−E_g/2kT): 2.0 nm 5.0e-10 → 7.0e-9 cm⁻³; 13.2 nm 7.0e-8 → 9.7e-7 cm⁻³ (×13.9). The SRH generation bound scales at most ×14: ≤ 8e-29 (audit §7.1) → ≤ 1.1e-27 A/µm, still about 12 dec below the 2.0 nm floor of 4.61e-15 A/µm (MEASURED/DERIVED) | CALCULATED |
| Experiment-anchored gap | King et al., Phys. Rev. B 79, 205211 (2009), doi:10.1103/PhysRevB.79.205211: 2.93 ± 0.15 eV; deck 3.05 (Fan 2021) | LITERATURE | n_i only (×10 at −0.12 eV): negligible | CALCULATED |
| W donor placement | resonant level 1.22–1.80 eV above the host CB, but within ≤ 0.1 eV of E_F at Γ at 1.4–3e21 cm⁻³ filling | COMPUTED (FS §5–6) | supports the constant shared N_D (FITTED V1 amplitude); dilute-limit ionisation is INFERRED, not computed (C022 caveat) | — |
| Termination | ideal OH gives no gap states; the CB bottom is never surface-dominated | COMPUTED (FS §3) | D_it and Q_f stay ASSUMED/FITTED | — |

### 2.4 Bulk mass choice D3 (0.208 m0 + Δm)

**Sources.**
- LITERATURE:
  - Stokey et al., J. Appl. Phys. 129, 225102 (2021), doi:10.1063/5.0052848: 0.208 ± 0.006 m0 (optical Hall, 2.8e17 cm⁻³);
  - Feneberg et al., Phys. Rev. B 93, 045203 (2016), doi:10.1103/PhysRevB.93.045203: 0.18 m0 at zero density.
- COMPUTED: PBE 0.1541 (Kane) or 0.1588 (3-point).
- ESTIMATED: HSE06 0.159–0.193.

**Reading.**
- The PBE mass is low because the PBE gap is too small; the HSE estimate moves toward experiment.
- The frozen 0.208 sits at the top of the literature range. The registered S6-07..09 (0.159) brackets the low side, and 0.18 lies inside that bracket.
- The bulk mass is additive with Δm, so it changes the film-to-film mass ratio. It is therefore not absorbed exactly; S6-07..09 measures it with 3 registered launches.
- The mass-only band-mobility ratio μ(2.0)/μ(13.2) is 0.2123/0.2543 = 0.835 on the deck basis, or 0.832 on the band-edge basis (CALCULATED). Both are inside H-D's registered 0.75–0.95, which A22 reports as "unresolved: not computed" for the amorphous dispersion. The crystalline result does not change that status.
- **Not contradicted.**

### 2.5 Verdict and what an amendment could or could not do

**Contradicted:** none.

**Understated uncertainty:** the fit3 extrapolation band at 6.3 and 13.2 nm. The ±0.1736 eV polar sensitivity is not in the frozen S6 range.

**What a change could not do:**
- It could not alter the decks of runs 0061–0077. They carry the fit3 AFFINITY values 4.01839 / 4.23784 / 4.27653 eV, verified in FS §4.
- It could not alter S1-07's binding to the run_0061 digest.

**Why not to amend the primary law:**
- Switching the primary to fit2 now would be result-informed: the DFT study came after S0/S1 and S2-11 were seen.
- It would force a new baseline triple, 3 launches.
- It would also force a re-bind of every native confirmation.
- Its whole effect on the calibration is ≤ 3.4 mV differential.

**Proposed instead** (an analysis addendum, not a registered test; no launch):
- **A-DFT-1 (disclosure).** Record in the register or work chat that:
  - the frozen fit3 law includes a polar 0.695 nm point (±0.1736 eV ASSUMED reference sensitivity);
  - the registered S6 confinement band does not cover dEc(6.3) up to 0.0746 eV or dEc(13.2) up to 0.0312 eV;
  - the effect on the calibration is ≤ 3.4 mV differential (CALCULATED above).
- **A-DFT-2 (zero-launch propagation).** Once AFF-2p0 and AFF-6p3 pass their frozen ±5 mV rigidity rule, re-profile the S4 optimum and the S5 records with per-film V_G shifts δ_t = Δ(dEc)(t) for each variant (fit2, ±0.1736, HSE r1/r3, box MODEL). Report how ΔV₀, μ∞, ℓ and √J move.
  - This is exact in the model: χ, the band-referenced traps and the ohmic contacts all move with E_c, and the gate work function and Q_f are fixed.
  - It is **not** exact for the Schottky branch, where the barrier is WF − χ, or for tunnelling runs. If AFF fails rigidity, this item falls back to launches (2 per variant per film; not proposed).
  - A new offline script would import `profile_shared` and leave the frozen code unchanged. It needs Codex review and a manual check.
- **A-DFT-3 (DFT, before P4).** Run a dipole-corrected 0.75 nm SCF:
  - `tefield/dipfield`, `edir = 3`, as specified in BM §6 item 7;
  - about 3 h, plus about 10 h if a re-relaxation is needed;
  - optional: the HSE r at 0.75 nm, BM §6 item 10, about 3 h GPU.
  - This is the only DFT action that materially narrows a planned prediction. It would replace the ±0.1736 eV sensitivity with a value; see Bengtsson, Phys. Rev. B 59, 12301 (1999), doi:10.1103/PhysRevB.59.12301, on dipole corrections.
  - Submission falls under the user's standing GPU go (to 21 Oct), with Codex. That is not decided here.

---

## 3. Part B: the predictive layer

### 3.1 Classes (each number in a report carries one)

| Class | What | Data seen? | Can it be called validation? |
|---|---|---|---|
| **CALIBRATION** | S4a/S4b/S4c on 2.0 / 6.3 / 13.2 nm; S6 sensitivities | all three curves are fitted | never (CAMPAIGN_DESIGN §0) |
| **RETROSPECTIVE LOO** | S5: one film held out per fold, frozen record, native held-out run | all four curves were seen before the campaign | "retrospective transferability within already-seen devices, not validation" (`loo_score` label) |
| **RETROSPECTIVE-PUBLISHED** | comparisons with curves that exist in the paper but not in our data files (65/85 °C, annealing; 01_CURRENT_STATE §C) | published figures; prior viewing must be disclosed | no; a semi-blind consistency check at best |
| **PROSPECTIVE** | frozen and timestamped before a new measurement exists: V_D series, output curves, new temperatures, sub-2 nm films, replicate devices | no | yes, the only class that can test predictive power |

### 3.2 Calibration products used downstream (S4; no new launches)
- **S4c native best triple:** this is the frozen model. Its curves are the reference for every prospective product.
- **Profiled nuisances** (ΔV₀ via one Q_f, μ∞, ℓ) with the near-optimal set (§3.5 U1).
- **Jacobian** (`profile_s4s5.py jacobian`) over (lNs, W_T[, g0], dV0, lmu, ell).
  - It is scaled by the design ranges (SCALE: lNs 1.0; W_T 0.035 eV; g0 1.2; dV0 1 V; lmu log10(30); ell 50 nm).
  - It reports singular values, condition numbers, correlations and weak combinations.
  - The rule is frozen (A8/B5): condition number > 100 or |corr| > 0.95 means combinations are reported; a rank deficiency leaves individual values UNRESOLVED.
  - The launched columns are approximate archive derivatives, diagnostics only.
- **S4d runner-up branch:** the model-form alternative for every prediction (U9).

### 3.3 S5 leave-one-film-out under the frozen `s4s5-hf-v4` definitions

**Frozen code.**
- `profile_s4s5.py` sha256 `429b3a3f3f5c…0a4e` and `hf_score_draft.py` sha256 `96a2147e…1c81`. Both match the files on disk (checked 2026-10-14).
- Tag `s4s5-hf-v4-429b3a3f-frozen-20261013` (local), freeze commits 484ab8d + 2c8c530 (work chat l.5850).
- `loo_score` refuses a record whose `code_sha256` differs (Codex v3 fix 2), so this code must not be edited before S5 is scored.

**Design (CAMPAIGN_DESIGN §6; matrix S5-H*).** 30 launches = 3 folds × (4 training candidates × 2 training films + 2 frozen held-out runs).
- Fold order: the 6.3 nm fold first (register §3 item 7).
- Training objective: the two-film J. The pool is the S4a archive plus that fold's S5 candidates only (A6). S4b is excluded because it saw all three films.
- The branch is re-selected inside each fold from the training films' S3 results (`loo_branch`, sealed).
- A fold that picks a different branch uses the four registered A7 local points. **A7 is DRAFT:**
  - it needs a logged register amendment and the user's go;
  - first the S4C purpose text must read 0.01 dec (not 0.005) and the matrix must be regenerated.
- Freezing needs:
  - exactly four distinct fold candidates (ruling a: separation ≥ 1/56, distinct deck inputs);
  - a complete and resolved S4a inventory (ruling b). A terminal ineligible candidate is excluded only by a prospective `--exclusions` record.
- Each frozen record binds:
  - the held-out Q_f and μ_band(t_held) from the training-fold law;
  - the coordinates and branch;
  - the decision sha256 and the inventory digests;
  - the input-only expected held-out signature (quasi-2D NC300 at 2.0 nm only);
  - the code sha256.
- **The record's sha256 is committed externally (git tag or work chat) before the native held-out launch.** `loo_score FROZEN NATIVE --committed SHA` then scores §5.3 natively: μ_FE at 1.5/2/3 V and I_D(3 V) on native points (A10).
- **The runner-up measures optimiser uncertainty only**, never a second prediction.
- **Falsification:** any held-out film failing §5.3 falsifies transferability of this model form. It is reported, not repaired.
- **Disabled routes (stay disabled):** contacts folds are refused; the S4c confirmation route is disabled (`S4C_ROUTE_AVAILABLE = False`); D5 contacts route is unavailable.
- **H-F and H-J.**
  - The 6.3 nm fold is "test listed, no separate H-F prediction" (Codex ruling choice 5).
  - The H-J forecasts stay as recorded (Claude): leaving out 6.3 nm gives −0.33 ± 0.10 V and I_on ×3–6; leaving out 2.0 nm puts ℓ at the 50 nm bound; leaving out 13.2 nm gives I_on ×0.15–0.4.

**Addition proposed for the predictive layer (zero launches; must be frozen before the first S5 launch, otherwise it is result-informed):**

- **LOO-1, error extraction.**
  - For each fold, extract the held-out errors e_t: ΔV_th,cc (V), Δlog10 I_D(3 V) (dec), ΔSS (%), Δμ_FE(2 V) (%), and the active log-RMSE.
  - Use `campaign_extract.py` on the native held-out run, best record.
  - Also extract the best − runner-up differences, as the optimiser spread.
- **LOO-2, transfer-error floor rule (ASSUMED rule, to be frozen now).**
  - A prospective prediction at a new thickness t* < 2.0 nm carries a band no narrower than |e_2.0| of fold H2p0. That fold extrapolates from 6.3 + 13.2 nm to the thinnest film, the closest analogue.
  - A prediction at a calibrated film under new conditions (T, V_D) carries a band no narrower than that film's S4c calibration residual.
- **LOO-3, jackknife parameter spread.**
  - Compute it from the three folds' profiled (ΔV₀, μ∞, ℓ) and coordinates (N_s, W_T): var_JK = ((n−1)/n)·Σ(θ_i − θ̄)², with n = 3 (CALCULATED).
  - With n = 3 it is a coarse diagnostic, reported and not used as a confidence interval.

### 3.4 Prospective products P1–P5 (frozen after S4c and S5, before any new measurement)

**Common rules.**
- **Model:** the S4c native triple (frozen commit and tag) and its adopted branches.
- **Labels:** `c10_p*`.
- **Runner:** launched through `run_campaign.py` plans, sequentially, after the code items of §3.8.
- **Band:** the union of U1–U9 in §3.5, but never narrower than the LOO-2 floor.
- **Pass/fail rule:**
  - PASS: the measured value lies inside the frozen band;
  - FAIL: it lies outside. That falsifies the model form for that quantity;
  - a PASS counts as *discriminating* only if each competing model's frozen prediction lies outside the band;
  - a prediction whose band is wider than the separation of the competing models is registered as **non-discriminating**, or not registered at all (§3.5, prediction-identifiability filter).

#### P1. I_off against V_D (off-state floor mechanism)
- **Quantity:** I_D, I_S and I_G against V_D (0.05 to 0.7 V) at V_G = −2, −1 and −0.5 V, for 2.0 / 6.3 / 13.2 nm; and the ratio R = I_off(0.7)/I_off(0.1).
- **Competing frozen predictions:**
  - ungated ohmic strip (H-B): R = 7.0 ± 0.5 (registered);
  - the paper's diffusion form I_off ∝ (1 − e^(−qV_D/kT)): R = (1 − e^(−0.7/0.025852))/(1 − e^(−0.1/0.025852)) = 1.021 (CALCULATED, T = 300 K ASSUMED);
  - the intrinsic ATLAS channel: expected below the KCL resolution (1e-17 A) at 2.0 nm, then reported as *below resolution* (register §0 censoring rule).
- **Model floor:** I_floor,pred(t, V_D) = I_ATLAS(V_D) + I_strip(t, V_D)·L_p·(W/L)_par.
  - (W/L)_par is FITTED on 13.2 nm (the frozen calibration film, H-B).
  - L_p = 20 µm (ASSUMED).
  - The strip decks already step V_D from 0 to 0.1 to 0.7 V (S2-14/15, S6-24..26), so they need no new launch.
- **I_G is not predicted quantitatively.**
  - S2-11 FAILED its registered mesh test: resolved |I_G| changed by up to 2.86 dec (COMPUTED by ATLAS, `hc_mesh_run_0076_run_0067.json`).
  - So any I_G(V_D) statement stays PROVISIONAL until the tunnelling-mesh convergence branch (user request 00) converges. Only a ranking is registered.
- **Runs:**
  - 1 output-mode launch per film: `mode: output`, `output_vgs` [−2, −1, −0.5, 1, 2, 3], shared with P2;
  - V_D segments [[0.1, 0.02], [0.7, 0.05], [3.0, 0.1]] (ASSUMED; subject to a dry build);
  - **3 launches.**
- **Measurement asked of the fab:** I_D, I_S and I_G against V_D at off-state V_G on the same devices. The data show no second V_D and no I_G (01_CURRENT_STATE §D).
- **Class:** PROSPECTIVE.

#### P2. Low-V_D output curves and the V_D = 0.1 V transfer
- **Quantities:**
  - I_D(V_D) at V_G = 1, 2, 3 V;
  - the linear-region conductance g_d0 = ∂I_D/∂V_D as V_D → 0;
  - the saturation onset;
  - V_th,cc, SS and I_D(3 V) from a transfer at V_D = 0.1 V.
- **Competing models:**
  - the primary ideal ohmic Pd contacts (R_sd = 0, ASSUMED), which give a linear onset;
  - the Schottky branch (shared φ_B ∈ {0.2, 0.5} eV, ASSUMED grid; S3), which gives a superlinear (S-shaped) low-V_D onset in ATLAS. Both are frozen.
- **Runs:**
  - the output families are shared with P1, 0 extra;
  - V_D = 0.1 V transfers (override `geometry.drain_bias_V=0.1`, a supported prefix): **3 launches, optional.**
- **Earlier V1 ID–VD predictions** (run_0041–0043, a different model) stay historical and are not reused.
- **Class:** PROSPECTIVE.

#### P3. Temperature
- **Quantities:** V_th,cc(T), SS (fixed window), I_D(3 V) and μ_FE(2 V) at T = 338.15 and 358.15 K, i.e. 65 and 85 °C.
  - The paper reports 65/85 °C curves (LITERATURE: Januar, Luo, Liu & Lee, Small Structures 7, e202500807 (2026), doi:10.1002/sstr.202500807; 01_CURRENT_STATE §C).
  - Which films were measured is not in our record; check the paper before registering.
  - Against those published figures the class is **RETROSPECTIVE-PUBLISHED**, with prior viewing disclosed.
  - It is PROSPECTIVE only for raw data released after the timestamp, or for a new temperature (e.g. 398.15 K).
- **Model content:**
  - **Constant band mobility:** `tmun=0`. μ_band does not depend on T (ASSUMED). 01_CURRENT_STATE §K warns that with `user.default=silicon` an undeclared TMUN gives (T/300)^−1.5.
  - **NC(T):** NC(T) = NC300·(T/300)^NC.F (LITERATURE: ATLAS 5.28 manual, Table 3-1, `atlas_manual_pages.txt` l.3826–3829; NC.F default 1.5; manual, no DOI).
    - 1.5 is right for the 3-D parabolic DOS.
    - The quasi-2D N2D/t at 2.0 nm scales ∝ T, so it needs NC.F = 1 (CALCULATED).
    - The error without it is 1.74 / 2.73 meV-equivalent at 338 / 358 K (kT·ln((T/300)^0.5), CALCULATED). This is code item C-P3.
  - **Band gap:** EGALPHA = 0 (the generator writes `egalpha=0` when T ≠ 300; ASSUMED, no DFT temperature coefficient, DFT_TO_TCAD §7 item 11).
  - **Other inputs:** Q_f, N_D, the trap DOS and the oxide are T-independent (ASSUMED).
  - **If IGZO.TOKYO is adopted:**
    - γ = TGAMMA/T + GAMMA0 and μ = MUN·(T/300)^−TMUN·(n/NCRIT)^(γ/2) (manual eqs. 3-264..266 and Table 3-61, l.8205–8258);
    - TGAMMA = 178.4 K is the IGZO default (LITERATURE manual; transfer to IWO ASSUMED);
    - with the default GAMMA0 −0.31, γ = 0.285 at 300 K, 0.218 at 338 K and 0.188 at 358 K (CALCULATED);
    - the S4-fitted GAMMA0 then replaces −0.31.
- **Discrimination:** the T-dependence of SS and of V_th probes W_T against kT, through trap statistics, and the mobility law (constant against TGAMMA).
- **Runs:**
  - 3 films × 2 T = 6;
  - W_T-edge candidates (§3.5 U2) at 358 K for 2.0 and 13.2 nm: +4;
  - **10 in total; minimum 4** (2.0 and 13.2 nm at both temperatures).

#### P4. Sub-2 nm films (1.0 and 0.75 nm; no 0.51 nm prediction)

**DFT inputs (crystalline only; CALCULATED from the FITTED laws and the COMPUTED points).**

| t* (nominal) | dEc fit3 (primary) | dEc envelope, PBE: law variants at t*, and the DFT point at its own t_HH | + HSE (×1.1071) | dEg fit3 | m* law (0.208 + Δm) / DFT point basis | NC quasi-2D (N2D/t*) / 3-D | E21 (COMPUTED) | AFFINITY / EG300 (fit3) |
|---|---|---|---|---|---|---|---|---|
| 1.0 | 0.7015 | 0.654 (fit3, 0.695 point at −0.1736) to 0.848 (point at t_HH 0.930) | ≤ 0.939 | 0.8143 | 0.3192 / 0.3303 | 3.447e19 / 4.525e18 (ratio 7.62, −52.5 meV) | 1.499 eV (0.930 nm) | 3.5985 / 3.8643 |
| 0.75 | 1.0245 | 0.918 (fit3, 0.695 point at −0.1736) to 1.166 (fit2) | ≤ 1.291 | 1.1888 | 0.3679 / 0.384 | 5.297e19 / 5.600e18 (ratio 9.46, −58.1 meV) | 1.815 eV (0.695 nm) | 3.2755 / 4.2388 |

- **Formulas.** N2D = m*·kT/(πħ²) = 1.0799e13·(m*/m0) cm⁻² at 300 K, divided by t*. NC3D = 2(2πm*kT/h²)^1.5.
- **Assumptions:**
  - the nominal device thickness equals t_HH (ASSUMED, as for the calibrated films);
  - the single-subband criterion of D14 holds at both t*, with E21 ≥ 1.5 eV ≫ 10 kT. So the quasi-2D NC is the provisional primary and the 3-D NC is the robustness branch (register §3, A13).
- **Illustration only, at the S4 *start* values (not a prediction):**
  - N_t = N_s/t* = 4.0e19 and 5.33e19 cm⁻³;
  - the roughness factor (1 − 0.287/t*)² = 0.508 and 0.381, with Δ_sr = 0.287 nm (LITERATURE: Januar 2026);
  - MUN = 4.02 and 2.02 cm²/Vs.
- **0.51 nm is not predicted.**
  - The 0.461 nm DFT film relaxed into In8(OH)24 (COMPUTED), outside the recipe and excluded from every law.
  - The roughness factor falls to 0.191 (CALCULATED), close to the singularity of that law.
  - At most a labelled scenario; 0 launches recommended.

**Bands and DFT uncertainty.**
- From dEc alone: about ±0.10 V at 1.0 nm and ±0.12 V (PBE) to ±0.19 V (with HSE) at 0.75 nm. These assume the 1:1 AFF mapping (CALCULATED, half-widths of the envelopes above).
- The NC convention (quasi-2D against 3-D) is non-rigid. At 2.0 nm it gave +142 mV, against a +37.5 mV statistics shift (S1-05, COMPUTED by ATLAS, NC audit).
- Scaled by the same ratio of 3.79 (ASSUMED transfer), the −52.5 / −58.1 meV statistics shifts suggest about 0.20 / 0.22 V at 1.0 / 0.75 nm (CALCULATED estimate). **The NC convention is therefore the largest model-form uncertainty below 2 nm**, and both conventions are launched.

**Quantities:** V_th,cc, SS (fixed window), I_D(3 V), and the floor. The floor comes from the strip deck at t*, with (W/L)_par frozen from 13.2 nm.

**Runs (13 full):**

| Purpose | Launches |
|---|---|
| Primary (quasi-2D), 1.0 and 0.75 nm | 2 |
| 3-D NC branch (calibrated separately in S4, A13) | 2 |
| DFT-point basis (m*/NC at t_HH, dEc point) | 2 |
| U2 edge candidates | 4 |
| Strip floor decks | 2 |
| Native transformation check at 0.75 nm (Q_f + 1e12 cm⁻², MUN ×0.6, the S1-07 analogue: exactness is natively confirmed at 2.0 nm only) | 1 |

**Minimum 4:** primary and 3-D NC at both thicknesses.

**Gates:**
- **G1:** run P4 only if:
  - (i) the S5 fold H2p0 PRED-best passes §5.3;
  - (ii) S4c passes §5.3 at 2.0 nm;
  - (iii) the user lifts **D-07** ("T4 sub-1 nm predictions: not yet", in force).
  - Otherwise report "no predictive basis below 2 nm", spend 0 and save 13.
- **G1b:** A-DFT-3 (the dipole-corrected 0.75 nm point) exists before the 0.75 nm prediction is frozen. Otherwise the 0.75 nm band stays at ±0.19 V from dEc alone and is likely non-discriminating.

**Blind-rule note:** P4 uses crystalline inputs only. An amorphous-informed variant (H-K, N1) would be a separate later registration, after the registered release.

**Class:** PROSPECTIVE. No sub-2 nm device exists in the data; the fab would have to fabricate one.

#### P5. Replicate devices
- **Prediction:** the frozen S4c curves themselves, with 0 launches.
- **What it gives:** the device-to-device spread that the acceptance thresholds lack. They are ASSUMED engineering limits with one device per film (CAMPAIGN_DESIGN §5.3).
- **Class:** PROSPECTIVE (CAMPAIGN_DESIGN §11 lists replicates).

### 3.5 Uncertainty propagation

| # | Source | Method | Launches | Label of the band |
|---|---|---|---|---|
| U1 | Profiled nuisances ΔV₀ (Q_f), μ∞, ℓ | **Exact transformation**: I(V_G) → s·I(V_G + qδQ_f/C_ox), with s = μ_law(μ∞, ℓ, t*, m*(t*))/μ_launched (`profile_shared.transformed_log`, no extrapolation). Near-optimal set: every (ΔV₀, μ∞, ℓ) with √J ≤ √J_best + 0.01 dec (the S4c tolerance) and + 0.03 dec (the S3 materiality threshold). Both tolerances are ASSUMED; report both. The envelope of the transformed prediction curves is the band | 0 | CALCULATED (exact in the continuum equations; natively confirmed at 2.0 nm by S1-07, max deviation 2.05e-4 dec; not for the Schottky or tunnelling runs) |
| U2 | Launched N_s, W_T [, GAMMA0] | From the S4a+S4b archive: the near-optimal candidates (√J ≤ best + 0.03 dec); take the two extreme along the weakest launched Jacobian combination and launch the prediction at best ± edge | 2 per prediction condition (only where listed in §3.4) | FITTED-set spread; approximate (A8), not a confidence interval |
| U3 | DFT dEc variants: fit2, 0.695 ± 0.1736, box MODEL | per-film rigid V_G shift δ_t = Δ(dEc)(t), then re-profile (A-DFT-2) | 0 (conditional on AFF rigidity PASS) | CALCULATED |
| U4 | NC convention (quasi-2D against 3-D) at ≤ 2 nm | launch both: the register's 3-D NC robustness branch, calibrated separately in S4 | ×2 for P4 (included); P1–P3 at 2.0 nm use the S4 3-D branch's own S4c curve if it exists | COMPUTED by ATLAS |
| U5 | Mass inputs: bulk 0.208 against 0.159 (S6-07..09, registered); W +5–7.5 %; band-edge basis; Kane | uniform factors: μ part exact (absorbed by μ∞), NC part ≤ 2.8 meV (CALCULATED); the bulk-mass change is non-uniform, so the S6 runs are used | 0 extra | CALCULATED / COMPUTED |
| U6 | HSE against PBE | dEc ×1.0599–1.1071 through U3 (one-sided). dEg only through n_i (≤ 1e-6 cm⁻³, negligible). HSE masses (ESTIMATED +1–5 % at 1 nm) through U5 | 0 | CALCULATED; r transfer ASSUMED |
| U7 | LOO transfer error | the LOO-2 floor rule (§3.3), frozen before S5 | 0 (inside S5's 30) | retrospective |
| U8 | Numerics | mesh ×0.7 and DOS ×2: ≤ 0.0005 dec (S1-03/04, COMPUTED); profiling exactness 2.05e-4 dec (S1-07). QTNLSC I_G: 2.86 dec mesh sensitivity, so I_G is PROVISIONAL | 0 | COMPUTED |
| U9 | Model form | the S4d runner-up branch is evaluated at every prospective condition, reported beside the primary | +1 per P1/P2/P3 condition, *optional*; not in the totals | COMPUTED by ATLAS |

**Prediction-identifiability filter** (ASSUMED method, frozen with the registration):
- For each quantity q, compute its sensitivity to the Jacobian's weak right-singular vectors (s_max/s_k > 100):
  - exact for the profiled block (dV0, lmu, ell) at t*;
  - from the U2 edge launches for the launched block.
- If the spread of q over the near-optimal set (U1 ∪ U2) exceeds the separation between the competing models that q is meant to discriminate, q is registered as **non-discriminating** and not claimed as a test.
- This prevents registering predictions that the calibration does not constrain. The condition-number and correlation rule of CAMPAIGN_DESIGN §5.4 governs the parameter statements.

### 3.6 Cost and budget

| Product | Full | Minimum | Class |
|---|---:|---:|---|
| S5 LOO (registered) | 30 | 30 | retrospective |
| P1 + P2 output families | 3 | 3 | prospective |
| P2 V_D = 0.1 V transfers | 3 | 0 | prospective |
| P3 temperature | 10 | 4 | retrospective-published / prospective |
| P4 sub-2 nm (gated G1/G1b) | 13 | 4 | prospective |
| P5 replicates | 0 | 0 | prospective |
| Repairs for P1–P4 | 3 | 1 | — |
| **Prospective total (CALCULATED)** | **32** | **12** | |

**Budget pool (CALCULATED):**
- C10 launches used: 17 (run_0061–0077; c10_* rows in `RUN_INDEX.csv`). That leaves 183 of the 200 cap (`solver.yaml` max_launches 260).
- The register §3 plan spends about 110–140 of the then 186. With S2-11's rerun and S0-02-DOS2 added outside it, at least 44 stay uncommitted; at least 38 if all six A41(d) refinements trigger.
- After a tunnelling-mesh branch of about 2–6 launches, the uncommitted pool is about 32–36.
- So the minimum layer (12) fits. The full layer (32) fits only if the plan spends toward its low end, for example through the S4b early stop or the S6 early exit. Otherwise P4 and P3 are cut to their minimum first.
- Every launch also needs the per-launch go and the pre-launch gate.

### 3.7 Freezing and registration protocol (charter §7)

1. **Before the first S5 launch:** log LOO-1..3 (§3.3) and the U1/U2 tolerances as a register amendment. No launch.
2. **After S4c:** commit and tag the model; run A-DFT-2 (0 launches); write the U1 envelope script (new file; Codex review and manual check).
3. **After S5 is scored:** apply gates G1–G3:
   - G1: P4, as in §3.4;
   - G2: P3 only for films that pass S4c §5.3;
   - G3: P2 only for films that pass the S4c V_th and I_on criteria;
   - P1 is ungated: it discriminates floor mechanisms.
4. **For each product, write `predictions/registered/REG-<n>.md`** from the template. It holds:
   - the quantity and its extraction script with commit;
   - the predicted value and band, with sources U1–U9;
   - the competing models' frozen values;
   - the decision rule.
5. **Before releasing the band**, run the identifiability filter (§3.5).
6. **Timestamp outside the repository** (GitHub tag, Zenodo or OSF), and get the custodian's (the fab's) confirmation that no data are released before it. Only then may the measurement be requested.
7. **Results** go to `predictions/revealed/`. Failures are reported in full.

### 3.8 Code items and checks (no launch; each needs `regress_all_decks.py` / `regress_sealed_aware.py` → "unexpected differences 0", Codex review and the manual 5.28 check)

| Id | Item | Why (as read) |
|---|---|---|
| C-P1 | `run_campaign.py` entry flag `"predict": true` → `execute(..., predict=True)` | `run_campaign.py:73` calls `execute` without `predict`. At an unmeasured t*, `read_meas` returns an empty grid and `execute` fails at `base[0]` (before `reserve`, so no launch is consumed, as read). Direct `run_atlas.py --predict` would bypass the C10 plan gates |
| C-P2 | Output and strip modes at an unmeasured thickness: pass `meas=None` / the predict switch; strip KCL limit fallback to 1e-17 A | `execute_output` calls `reserve()` **before** `build_deck(meas=read_meas(t))`, which gets empty arrays (median of an empty slice → NaN). A crash there would consume a C10 launch. `execute_strip` takes its KCL limit from the measured floor |
| C-P3 | Emit `nc.f=1` for IWO when the quasi-2D NC300 override is active **and** T ≠ 300 K | NC(T) = NC300·(T/300)^NC.F, default 1.5 (manual Table 3-1). Emitting it only at T ≠ 300 keeps every existing deck byte-identical |
| C-P4 | Offline per-film affinity-shift re-profiling (A-DFT-2) and the U1 envelope (new scripts that import `profile_shared`; frozen v4 code untouched) | zero-launch propagation |
| C-P5 | Dry builds (`build_deck` only) of one deck per new mode: output at off-state V_G, `drain_bias_V=0.1`, T = 358.15 K with `tmun=0` on every MOBILITY and MATERIAL line (strip regions included), t* = 1.0 / 0.75 nm with the quasi-2D override | catch syntax and NaN paths without spending launches |

### 3.9 What each outcome can claim

| Outcome | Claim allowed | Claim not allowed |
|---|---|---|
| S4c passes at all films | "one shared, DFT-informed model *calibrates* the three films" | validation, prediction |
| S5: held-out film passes | "retrospective transferability within already-seen devices" for that fold | out-of-sample validation |
| S5: held-out film fails | "transferability of this model form is falsified" (reported, not repaired) | rescue by per-film parameters |
| P1: R measured ≈ 7 inside the band, and the diffusion form (1.02) outside it | "the floor is ohmic and V_D-linear, as predicted by the ungated-strip model" | that the strip *is* the physical path (it needs mesa isolation) |
| P1: R ≈ 1.02 | the strip model is falsified for the floor; the diffusion form is consistent | — |
| P3 inside the band (published figures) | "consistent with the published T-series (retrospective-published)" | prospective validation |
| P4 inside the band, discriminating | "prospective prediction of a sub-2 nm device from DFT-informed confinement passed" | that crystalline DFT describes amorphous films (H-K stays separate) |
| P4 outside the band | falsifies the extrapolation (laws, NC convention or transport law); the U3/U4 decomposition says which input could account for it | post-hoc refit presented as prediction |
| Any band non-discriminating | "not tested by this measurement" | either PASS or FAIL language |

### 3.10 Open risks
- **AFF rigidity may fail.** Then U3 and A-DFT-2 need launches, 2 per variant per film; these are not budgeted.
- **The exact transformation at t* < 2 nm is natively confirmed only at 2.0 nm.** P4 includes 1 check launch.
- **I_G cannot be predicted** until the tunnelling-mesh convergence branch converges. S2-11 FAIL: 2.86 dec; Codex 2026-10-13T03:36Z keeps the QTNLSC H-C verdicts PROVISIONAL/UNRESOLVED.
- **Timeouts at t* < 2 nm.** N_t is higher and the films thinner. Use the 2.0 nm timeout ×1.5 (ASSUMED) and verify it in the dry build.
- **One device per film.** Every acceptance threshold is an ASSUMED engineering limit, not a confidence interval; P5 is the remedy.
- **Data custody.** The fab owns the data, and registration needs its timestamp confirmation (01_CURRENT_STATE §B, §H.6).
- **D-07 is in force** and blocks P4 until the user decides.
