# Current state of the IWO project (2026-10-07)

- **Labels** follow charter §3.
- **Paths** are relative to the public repository unless they start with `private:`. The public repository is github.com/mahmuoudAE/iwo-tft-tcad-dft, local checkout `..\IWO_PHYSICS_CONSTRAINED_MODEL_V1`, evidence commit `f315b78`.
- **Sources.** Every number below comes from one of:
  - the files named here;
  - the published paper (`private:sources/`);
  - the 2026-10-07 check of `data/experimental_clean.csv` (section D).

## A. The project in brief

- **Devices.** Bottom-gate W:In2O3 (IWO) thin-film transistors with 2.0, 6.3, 13.2 and 31.8 nm channels. The NTU fab group made and measured them and published the results (Januar et al. 2026).
- **Our work.**
  - Physics-based TCAD (Silvaco ATLAS) of these devices.
  - Our own DFT (Quantum ESPRESSO, run locally and at CERN).
  - A written extraction protocol for threshold, SS and mobility.
- **Model versions.**
  - V1 is calibrated per film.
  - V2 adds DFT thickness laws.
  - Every out-of-sample test of the 6.3 nm threshold has failed, including the registered V2 test.
- **Plan.** The user has set Nature as the target. The plan `private:claude/NATURE_PLAN.md` is PROPOSED, not approved.

## B. People and ownership

- **Mahmoud (the user).** TCAD and DFT; owns this record.
- **Supervisors and advisers.** Supervisor: Mukul. Also involved: Prof. Wu.
- **Fab and data owner.** Prof. Min-Hung Lee's group at National Taiwan University (Dr. Mochamad Januar, Zhao-Feng Luo).
- **Co-author of the paper.** Prof. Kou-Chen Liu (Chang Gung University).
- **Data access.** The measured data belong to the fab. Their paper releases data only "upon reasonable request".

## C. The device and the published paper [LITERATURE-SUPPORTED unless marked]

Januar, Luo, Liu & Lee, "Unified Analytic Framework for Thickness-Dependent Transport and Trap-State Modulation in Ultrathin W:In2O3 Field-Effect Transistors", *Small Structures* 7, e202500807 (2026), doi:10.1002/sstr.202500807. Open access (CC BY); copy in `private:sources/`.

### Process and structure
- **Stack:** n+ Si / TiN 50 nm (PVD, patterned) / HfO2 + Al2O3 (ALD, 250 °C) / channel / Pd 70 nm source and drain.
- **Channel:** IWO (~2 % W) or In2O3, pulsed-DC sputtered (30 W, 10 kHz).
- **Anneal:** RTA at 150 °C for 600 s.
- **Microstructure:** HRTEM shows no long-range crystallinity. SEM shows nanoscale grains, smaller in IWO, growing with thickness (SI Fig. S4).

### Their model
- The current is a blend of a band term, a tail term and an interface-trap term, plus a constant off-current:
  I_off = (W/L) q D_n t_s n_FB (1 − e^(−qV_D/kT)).
- Eight parameters are fitted per device. They report 200 Monte Carlo refits with VIF ≤ 2.42.
- Mobility law: μ_sr = μ0/(1 + θ_r V_ov) · (1 − Δ_sr/t)².

### Their DFT
- Crystalline bixbyite In2O3 and W:In2O3 with 5.3 % W.
- PBE functional, cutoffs 71/639 Ry, 8×8×8 k-points.
- Interface slabs In2O3/HfO2 and IWO/HfO2.

### Claims relevant to us

| Topic | What the paper says |
|---|---|
| W (Sec. 2.3) | W passivates O vacancies and "promotes smoother charge delocalization". |
| Crossover (Sec. 2.5) | One model "captures the crossover from near-band transport in thicker channels to disorder- and interface-limited transport in ultrathin films". |
| Off-current | I_off ∝ t_s n_FB. In 2 nm IWO, I_off < 1e-13 A/µm and the device is in enhancement mode. |
| IWO mobility | μ_max 27.4 → 5.1 cm²/Vs from 13.2 to 2 nm; the 6.3 nm value is ≈ 4 (read from Fig. 5a). In Fig. 5d the mobility falls as V_G rises. |
| SS | 60–70 mV/dec, "near-thermal"; ≈ 62 mV/dec at 2 nm in Figs. 4d and 6e. |
| Roughness | Δ_sr = 2.87 Å for IWO and 3.75 Å for In2O3, consistent with AFM. |
| Other data in the paper | Positive and negative bias stress, 65/85 °C curves, an annealing series (RT, 150, 200 °C), and In2O3 devices at 3, 10 and 11 nm. |

**Not in our data files:**
- the In2O3 curves;
- the stress, temperature and annealing series;
- C–V data (SI Fig. S1).

## D. Our measured data and their analysis

### Data
- **Files [MEASURED].** `data/experimental_clean.csv`; the raw workbook is `data/experimental_raw_preserved_IWO-TFT.xlsx`.
- **Content.** One transfer curve per film:
  - V_G from −3 to +3 V in 121 points (50 mV steps);
  - V_D = 0.7 V;
  - films of 2.0, 6.3, 13.2 and 31.8 nm.
- **Missing.** No reverse sweep, no gate current, no second V_D, and only one device per film.
- **Geometry (taken from the device schematic, not measured by us).**
  - W/L = 290/20 µm.
  - HfO2 15 nm (ε 19.57, from SI Fig. S1).
  - Al2O3 2 nm (ε 9.0, assumed). In our model it lies on top of the HfO2, touching the channel.
  - Geometric C_ox = 8.9554e-7 F/cm².
  - T = 300 K, assumed.

### Extraction
- Protocol: `analysis_2026-10-06_extraction/PROTOCOL.md`, registered at commit `7a61687`.
- Amendment A1 (commit `7ce7116`) adds a window normalised by I_on.
- The same code processes the measured and the TCAD curves.

### Results

Each cell gives the measured value / the TCAD value. Measured values are DERIVED; TCAD values are COMPUTED.

| | 2.0 nm | 6.3 nm | 13.2 nm | 31.8 nm |
|---|---|---|---|---|
| V_th,cc at 1e-9 A/µm (V) | 0.662 / 0.680 | 0.644 / 0.653 | 0.083 / 0.054 | none: I_D never falls below 1e-9 |
| I_D(+3 V) (A/µm) | 5.09e-7 | 4.03e-7 | 3.07e-6 | 3.59e-6 |
| I_D(−3 V) (A/µm) | 1.9e-16 | 1.9e-13 | 6.8e-12 | 3.0e-7 |
| Off-state floor (A/µm) | 4.61e-15 | 1.53e-13 | 6.60e-12 | — |
| I_on/I_off (measured) | 1.1e8 | 2.6e6 | 4.7e5 | ≈ 12 over the sweep |
| SS, normalised window [2.15e-5, 2.15e-4]·I_on (mV/dec) | 123.6 ± 1.0 / 126.4 | 122.7 ± 9.3 / 121.3 | 115.3 ± 2.4 / 131.3 | — |
| SS, fixed window 5e-11 to 5e-10 A/µm (mV/dec) | 165.6 / 179.9 | 177.6 / 182.6 | 106.1 (floor-corrected) / 122.2 | — |
| μ_FE = L g_m/(W C_ox V_D) at 3 V (cm²/Vs) | 12.15 / 11.10 | 10.74 / 8.39 | 49.07 / 48.85 | — |
| Peak of measured μ_FE | 12.1 at 3.0 V | 10.9 at 2.85 V | 50.2 at 2.8 V | — |
| Power-law exponent γ (measured / TCAD) | — | 1.13 / 0.57 | 0.27 ± 0.08 / 0.23 ± 0.10 | — |

In the TCAD, I_on and V_th,cc are calibration targets. They agree by construction.

### Observations [OBSERVED or DERIVED; one device per film]

1. **SS collapse.** Plotted against I_D/I_on, the local SS of the 2.0, 6.3 and 13.2 nm films falls on one curve, in the measurement and in the TCAD.
2. **Post hoc SS agreement ranges.** One rule for all films: |ΔSS| ≤ 5 mV/dec over one-decade windows (`AGREEMENT_WINDOWS.md`).

   | Film | Range (A/µm) | Points | Measured / TCAD SS (mV/dec) |
   |---|---|---|---|
   | 2.0 nm | 5.6e-14 to 1e-10 | 6 | 89.1 ± 0.5 / 89.3 |
   | 6.3 nm | 1.5e-12 to 1e-9 | 8 | 145.6 ± 3.7 / 145.5 |
   | 13.2 nm | none | — | TCAD 16–25 mV/dec too high in the clean range; +44 at 1e-9 to 1e-8 |

   At 13.2 nm, agreement appears only after the floor is subtracted (1e-11 to 1e-10 A/µm, 2 points, 91.8 vs 90.9 mV/dec). This assumes an additive floor and is not claimed.
3. **The thickness dependence is not uniform.**

   | Quantity | 2.0 → 6.3 nm | 6.3 → 13.2 nm |
   |---|---|---|
   | V_th,cc shift | −0.018 V | −0.561 V |
   | Peak μ_FE | × 0.9 | × 4.6 |
   | I_on | × 0.79 | × 7.6 |
   | Local exponent of the off-state floor | 3.1 | 5.1 |

   - The 31.8 nm device does not turn off.
   - A single power-law fit through the three floors gives t^3.85.
   - With one device per film, a smooth law cannot be told apart from a crossover.
4. **The off-state floor does not depend on V_G** (within 3 % at 13.2 nm). Gate leakage is therefore unlikely [INFERRED]; no gate current was recorded.

## E. TCAD models [COMPUTED; parameters FITTED unless marked]

### V1
Model file `config/iwo_material_model.yaml`; final runs `run_0038_2p0`, `run_0039_6p3_tuned` and `run_0040_13p2`.

- **Fitted per film.**
  - The fixed interface charge Q_f, fitted to V_th,cc: 1.73e12 cm⁻² shared by 2.0 and 13.2 nm; 8.7e10 cm⁻² for 6.3 nm.
  - The band mobility, fitted to I_on.
- **Tail states.**
  - Acceptor tail width W_TA = 40 meV, fitted to the 2.0 nm subthreshold region.
  - N_t(t) = 2e19·(2/t)^0.75 cm⁻³eV⁻¹. This is a two-point law: the anchor comes from the V0 2 nm fit, the exponent from the ratio in the paper's Fig. 5a.
- **Other traps.**
  - Deep Gaussian at E_c − 0.6 eV, 5e16 cm⁻³eV⁻¹.
  - D_it = 2.92e11 cm⁻²eV⁻¹ at E_c − 0.30 eV, in a 0.25 nm layer.
- **Donors.** N_D,eff(t) = 2.5e17·[1 + (t/20)^4] cm⁻³. It is fitted to the V0 per-film values (2e17 / 3e17 / 3e17 / 2.65e18) and is not identifiable.
- **Untested alternative.** Surface + bulk traps, N_t·t = N_s + N_b·t, with N_s = 3.57e12 cm⁻² and N_b = 2.15e18 cm⁻³ [DERIVED from the two anchors].
- **Failed validation.** The earlier V1 run `run_0014` (6.3 nm, shared parameters) missed V_th by −0.29 V [FALSIFIED as a prediction].
- **Mechanism study of 2026-09-25** (`analysis_2026-09-25/SYNTHESIS.md`):
  - The parameters are not unique. Work function, χ, Q_f and ΔE_c act as one number; μ_band trades off against N_t, and R_sd against α.
  - Every thickness law is a two-point law.
  - Confinement is physically expected but cannot be identified from I_D–V_G.
  - The 6.3 nm miss splits into a rigid 0.294 V shift plus a 0.16–0.19 V shape part. Its cause has not been assigned.
  - A thickness-independent R_sd cannot create the trend: θ_net < 0 in all films, and R_sd would need 83 % of V_D at 2 nm.
  - The 31.8 nm device is a documented model failure.

### V2
Model file `config/iwo_material_model_v2.yaml`; analysis in `analysis_2026-10-06_V2/`.

- **What changed.** DFT thickness laws.
- **Registration.** Pre-registered in `T0_PRECHECKS.md` (commit `7b75ee6`); correction `a914165`; outcomes `852dc8a`.
- **Results.**

  | Test | Result |
  |---|---|
  | T2, 13.2 nm anchor | PASS |
  | T2, 2.0 nm anchor | FAIL, on RMSE only (0.0661 vs 0.0600 dec predicted; tolerance 0.005) |
  | T3, 6.3 nm held out | FALSIFIED as registered (below) |

  For T3 the measured V_th,cc is 0.644 V and I_on 4.03e-7 A/µm. Both variants fail:

  | Variant | μ_band | Predicted V_th,cc | Predicted I_on |
  |---|---|---|---|
  | P | 38.4 | 0.270 V | +288 % |
  | E (I_on-normalised) | 9.9 | 0.417 V | matched by construction |
- **T1, off-current strip (variant D).**
  - The strip is added after the solver: I = I_ATLAS + G(t)·V_D.
  - (W/L)_par = 1.0e-4 per µm, fitted on 13.2 nm.
  - Predicted/measured floor: 0.46 at 2.0 nm and 0.64 at 6.3 nm.
  - Status: HYPOTHESIS, with one fitted constant.

### Numerical uncertainty
About 0.7 %. The DOS-grid offset on I_on is +2.5 / +1.0 / +0.5 % at 2.0 / 6.3 / 13.2 nm.

## F. DFT [COMPUTED]

- **Where.**
  - `qe_workflow/`;
  - protocols: `bulk_In2O3_protocol/PROTOCOL.md` and `cern_htcondor/PROTOCOL_CERN.md`;
  - log: `cern_htcondor/results/RESULTS_LOG.md`;
  - report chapter: `report_latex_full/chapters/13_dft.tex`.
- **Bulk bixbyite In2O3** (PAW-PBE, 71 Ry, 3×3×3 k-points): PBE gap 1.19 eV.
- **Confinement slabs** (Lin et al. 2022 recipe).

  | Slab | ΔE_g | Notes |
  |---|---|---|
  | 1 nm | +0.90 eV PBE; +0.95–1.00 eV with HSE correction | HSE/PBE ratio 1.06–1.11. Lin et al. report +0.94 eV. |
  | 2 nm | +0.335 eV | m* = 0.206 m0 (Δm* +0.047). The 1 → 2 nm change sits in the conduction band. |
- **Thinner slabs** (preliminary, not yet in `RESULTS_LOG.md`).
  - 0.75 nm: PBE gap 2.20 eV.
  - 0.51 nm: 3.14 eV; the slab relaxed into an In(OH)3-like layer.
- **W in crystalline cells.**
  - The W 5d level is resonant about 1.2–1.8 eV above the host conduction-band bottom.
  - In a 1 nm slab, E_F lies 1.23 eV above the CB bottom, and 2 of W's 3 electrons go into the host CB.
  - Band-count pitfall: In 4d and W 5s5p are in the valence, so the VB top of a W cell is band n_pure − 1.
- **2 nm W slab** (`iwo_slab2_final_cpu`): final SCF and projwfc done; analysis pending.
- **Not done yet.** Amorphous structures, defects (V_O, H), interfaces with Al2O3 or HfO2, contacts.
- **Validity.** PBE (with an HSE check for the 1 nm confinement) on crystalline structures only, while the real films are amorphous or nanocrystalline.

## G. Off-current

- **Floors [DERIVED].** 4.61e-15 / 1.53e-13 / 6.60e-12 A/µm, i.e. 1.3 pA, 44 pA and 1.9 nA in total. The 2.0 nm floor is at the level of the measurement setup.
- **Excluded so far [INFERRED].** Gate leakage (the floor is flat in V_G, but no gate current was recorded), the instrument range, and a gated back layer.
- **Competing hypotheses.**
  - (a) An ungated IWO strip in parallel. It is ohmic, so the floor scales with V_D, and mesa isolation would remove it.
  - (b) The paper's diffusion form, which saturates for V_D ≫ kT/q.
- **How to separate them.** Measure the floor against V_D. Going from 0.1 to 0.7 V, (a) predicts ×7 and (b) ×1.02.

## H. Open discrepancies and problems

1. **Mobility.**
   - The paper gives μ_max 27.4 / ≈ 4 / 5.1 cm²/Vs (13.2 / 6.3 / 2.0 nm), falling with V_G.
   - Ours peaks at 50 / 11 / 12 cm²/Vs and rises up to about 3 V.
   - A difference in definition, C_ox or V_D is suspected [UNRESOLVED].
   - **RQ-001 (2026-10-09, HO-002; reviewed by Codex, verdict MODIFY; owner response R-RQ-001).**
     - The peak of the saturation-formula mobility on our curves is 5.09 / 3.86 / 27.40 cm²/Vs, with the protocol C_ox and no free factor. This reproduces the paper's values [DERIVED, C030; independently reproduced by Codex].
     - That formula is the leading candidate for the paper's method; the recipe and sweep provenance are unconfirmed [INFERRED, C031]. Conditional on the V_T definition, the formula is outside its validity range at its peak: at 6.3 nm under all three V_T definitions, and at every film under V_th,cc.
     - No single C_ox or V_D reconciles the g_m-based μ_FE.
2. **SS at 2 nm.**
   - The paper gives 60–70 mV/dec.
   - We get 89.1 ± 0.5 mV/dec over 3.3 decades, and 123.6 in the normalised window.
   - Values near 60 occur only next to the floor. The two-point minimum at 6.3 nm is 33.4 mV/dec, i.e. noise (SYNTHESIS H.2, item 2.4) [UNRESOLVED].
   - **RQ-001 (2026-10-09, HO-002; reviewed by Codex, verdict MODIFY; owner response R-RQ-001).**
     - The paper's own Fig. 1b gives SS = 61.8 / 87.4 / 119.3 mV/dec for 2.0 / 6.3 / 13.2 nm (digitised), so "60–70" holds only at 2 nm.
     - Steepest-slope estimators that start 1–12× above the floor reproduce these values within 5–15 % [DERIVED, C032]. That makes the paper's values compatible with several near-floor estimators. The paper's exact method is unknown.
     - Whether the 2 nm steep section (≈ 5–30 pA total, 0.10–0.15 V wide) is channel behaviour or instrumental is UNRESOLVED. The noise Monte Carlo covers only two estimators, under an idealised noise model.
     - The registered windows sample the curve 3–4 decades higher.
3. **Gate-oxide interface.** Our model puts Al2O3 against the channel, while the paper's DFT uses IWO/HfO2. Ask the fab.
4. **6.3 nm.**
   - Out-of-sample V_th predictions failed three times (V1 run_0014; V2 variants P and E).
   - This film also has the strongest V_G dependence of mobility (γ = 1.13) and the lowest peak mobility in both the paper's analysis and ours.
5. **31.8 nm.** The device never turns off and is a model failure. The user excluded it in September.
   - It is NOT a holdout: it has been in our data all along.
6. **Data permission.** The fab's raw curves are in the public repository:
   - `data/experimental_raw_preserved_IWO-TFT.xlsx`;
   - `data/experimental_clean.csv`;
   - `inputs/astra_IWO_PRIORITY_THREE_20260912/IWO_PRIORITY_THREE_20260912/audit/sources/IWO-TFT (1).xlsx`.

   The paper releases data only on request.
7. **Thickness.** The thicknesses are nominal; how they were measured is unknown.
8. **Fab runs.** We do not know whether the four devices come from one fab run, or what their sweep history was.

## I. Evidence index (public repository at f315b78)

| Topic | Files |
|---|---|
| Measured data | `data/experimental_clean.csv`, `data/experimental_raw_preserved_IWO-TFT.xlsx` |
| Extraction | `analysis_2026-10-06_extraction/`: PROTOCOL.md, extraction.py, run_extraction.py, results.json, results_table.csv, mobility_vs_vg.csv, RESULTS_TABLES.md, A1_RESULTS.md, results_a1.json, FINAL_SUMMARY.md, PAPER_FIGURES.md, AGREEMENT_WINDOWS.md, agreement_windows.json, METHODS_TEXT.md |
| Traps | `analysis_2026-10-06_traps/`: TRAPS.md, trap_parameters.json |
| V2 tests | `analysis_2026-10-06_V2/`: T0_PRECHECKS.md, T0_REGISTRATION.txt, T0_CORRECTION.md, T2_T3_RESULTS.md |
| Mechanism study | `analysis_2026-09-25/`: SYNTHESIS.md, PREDICTIONS_REGISTER.md, the S1–S6 reports, REVIEW |
| Models | `config/iwo_material_model.yaml`, `config/iwo_material_model_v2.yaml`, `config/geometry.yaml`, `config/solver.yaml` |
| Runs | `results/RUN_INDEX.csv`; `results/runs/run_0038…, run_0039…, run_0040…` (V1 final); `run_0058…, run_0059…, run_0060…` (V2) |
| DFT | `qe_workflow/` (see section F) |
| Reports | `report_latex_full/` (chapters 13_dft.tex and 14_model_v2.tex), `docs/SUPERVISOR_SUMMARY.md`, `FINAL_STATUS.md` |
| Private | `private:claude/NATURE_PLAN.md`, `private:sources/Januar2026_SmallStructures.pdf` |

## J. Pending human decisions

See `04_TASK_QUEUE.yaml` (HUM-*).
- Adopt this charter and this private repository.
- Hold the fab meeting: scope, authorship, data custody, consent for AI tools, and permission for the data already in the public repository.
- Decide on an ATLAS budget beyond 71 launches (60 used).
- Decide go or no-go for T4 (registered sub-1 nm predictions).
- Log in to CERN when DFT resumes.

## K. Tool facts that cost launches to learn

### ATLAS
- **Launching.**
  - Use `deckbuild.exe -run device.in -outfile deckbuild.out` from a fresh run directory.
  - Run launches sequentially; parallel launches failed.
  - Give the 31.8 nm film a 1500 s timeout.
- **Statements and units.**
  - MOBILITY statements between SOLVEs are ignored.
  - MAXTRAPS ≤ 10.
  - DEFECTS take cm⁻³/eV; INTDEFECTS take cm⁻²/eV.
  - CONTACT RESISTANCE is in Ω·µm.
  - INTERFACE QF works on the IWO/Air boundary.
- **Convergence and mesh.**
  - Depletion needs XANDRNORM and CR.TOLER 7.88e-16.
  - Refine the 13.2 nm mesh by ×0.7; ×0.5 exceeds memory.
- **Temperature.** With user.default=silicon, a constant MUN still carries a (T/300)^−1.5 factor. Declare tmun for any T ≠ 300 K.
- **Extraction.** SS_min from a stepped grid is not robust; use a fixed-current SS.

### Quantum ESPRESSO
- **Structures.**
  - Build structures with ASE/spglib and verify them: 24 symmetry operations for primitive bixbyite, In–O 2.12–2.21 Å.
  - Use ibrav=0 with CELL_PARAMETERS.
- **Memory.** A 176-atom slab needs about 66 GB for the final SCF.
- **Metallic 2 nm slabs.** Use conv_thr 1e-8 with beta 0.1.

### CERN
- Kerberos tickets of running jobs are not renewed, so in-job copies to EOS fail. Use `snapshot_jobs.sh`.
- Never `condor_release` a job that ran for more than 1 h: it restarts from step 1.

---

## Change log

- **2026-10-09, R-RQ-001** (Claude, owner response to the Codex review of HO-002; `claude/responses_to_codex/RQ-001_response.md`).
  - §"Mobility" RQ-001 bullet: "The paper probably used that formula … for at least 6.3 nm" replaced by the leading-candidate and conditional-validity wording (objections O1, O10).
  - §"SS at 2 nm" RQ-001 bullet: compatibility wording and the Monte Carlo scope added (O4, O5).
  - Original wording is in git at `b2d668e`.
