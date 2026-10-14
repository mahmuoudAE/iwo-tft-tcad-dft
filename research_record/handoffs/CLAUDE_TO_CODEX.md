# Handoffs from Claude to Codex

Newest first. Each handoff follows `templates/HANDOFF_TEMPLATE.md`.

---

## HO-003: The 10–21 Oct compute plan, for independent review before anything is submitted (task PLAN-001)

| Field | Value |
|---|---|
| TASK ID | PLAN-001 (owner Claude, reviewer Codex) |
| GIT COMMIT | Plan: `claude/plans/COMPLETE_PLAN_2026-10.md` and `claude/plans/CERN_DFT_timeline_2026-10.pdf` (private repo, commit f607cb5). Evidence: public repo `f315b78`. |
| QUESTION | Is this the best use of 11 days of CERN (target: finished by 15 Oct) and the local ATLAS budget, with no new measurements? Is it feasible and safe? What should be cut, changed or added? |
| DATA USED | The CERN probe of 2026-10-10 (below); past job timings from `qe_workflow/cern_htcondor/results/*/*.out`; the inventory of existing DFT results; `01_CURRENT_STATE.md` |
| DATA EXCLUDED | — |
| METHOD | Collation only. Nothing has been submitted to CERN, and nothing installed. |

**Reviewer: read Part A and check it against the files first; commit your independent assessment; only then read Part B and the plan.**

### PART A — EVIDENCE

**A1. Constraints [stated by Mahmoud, 2026-10-09/10]**
- No new measurements are possible.
- CERN access ends on 21 Oct.
- Mahmoud wants everything finished by 15 Oct.

**A2. CERN probe, 2026-10-10 09:26 UTC, via the SSH master [OBSERVED]**
- **Credentials:** Kerberos and AFS tokens valid until 11 Oct 12:26.
- **Tools present:** `condor_submit`, `condor_submit_dag`, `acrontab` (works; currently empty), `git`, `python3`, `apptainer`.
- **Jobs:** none of ours running.
- **Pool:** 10,427 jobs, 2,100 running; about 5,539 unclaimed cores.
- **GPU slots:** A100-40GB 74, H100 NVL 56, V100/V100S 63, H200 19.
- **Storage:**
  - AFS home: 86 % → **18 %** after deleting the stale `~/.conda/pkgs` (2026-10-10, by Mahmoud).
  - EOS `/eos/user/m/melrashe` holds `qe-7.5-env.tar.gz` and a GPU container `qe-7.3.1-gpu.sif`.
- **GitHub:** reachable from lxplus over ssh on ports 22 and 443 (`Permission denied (publickey)`; no key installed yet).

**A3. Past CERN timings [DERIVED; `PWSCF ... WALL` lines]**

| Run | Atoms | k-points | MPI ranks | Wall time |
|---|---|---|---|---|
| `iwo_W24d` spin SCF | 80 | 10 | 32 | 2h39m (26 SCF iterations) |
| `iwo_W24d` relax | 80 | 10 | 32 | 23h48m |
| `iwo_W8b` relax | 80 | 6 | 32 | 10h02m |
| `slab1r_final_cpu` SCF | 96 | 4 | 16 | 2h19m |
| `iwo_slab2_final_cpu` SCF | 176 | 4 | 33 | 8h05m (91 SCF iterations) |
| `slabL2_relax_v2` vc-relax | 76 | 4 | 1 | 9h58m |
| `slabL2_relax_v2` SCF | 76 | 4 | 11 | 1h06m |

**A4. Existing DFT inventory [DERIVED from the result folders]**
- **Crystalline In₂O₃ slabs:** 0.51 nm (56 atoms), 0.75 nm (76), 1 nm (96), 2 nm (176).
- **Crystalline IWO slabs** (1 W each): 1 nm (96), 2 nm (176).
- **80-atom bulk:** In₂O₃, and IWO with W at the 24d and 8b sites.
- **Not yet existing:** amorphous structures, defects, interfaces.

**A5. Size arithmetic used by the plan [DERIVED]**
- An amorphous film at ~7.0 g/cm³ has about 76 atoms/nm³, of which about 30 are metal atoms.
- 2 % W therefore means 1 W per ~50 metal atoms, i.e. about 1.7 nm³ of film per W.
- Resulting in-plane cells:

| Thickness (nm) | In-plane cell (nm) |
|---|---|
| 2.0 | 1.05 (1 W = 1.5 %) |
| 1.5 | 1.05 |
| 1.0 | 1.29 |
| 0.8 | 1.44 |
| 0.7 | 1.54 |

**A6. Known pitfalls [`01_CURRENT_STATE.md` section K, and the memory of earlier failures]**
- Running jobs lose Kerberos and EOS access after about 25 h.
- `condor_release` restarts a job from step 1; a converged 2 nm relaxation was lost this way.
- The first generated structures were defective (2 symmetry operations instead of 24).
- Metallic 2 nm slabs stall near 1e-8 Ry.

### PART B — INTERPRETATION AND THE PLAN

The plan is in `claude/plans/COMPLETE_PLAN_2026-10.md`. Its main assumptions, each a HYPOTHESIS until tested:

1. **ML structures.** MACE-MP-0 (a universal ML potential) gives amorphous In–W–O structures good enough to start DFT relaxations. A QC gate (density, bonds, coordination) plus a short DFT MD check on an 80-atom bulk is enough validation for a thesis.
2. **Timing.** Amorphous slabs of 125–170 atoms relax and finish their SCF and DOS in 1–4 days per job, if submitted by 11 Oct.
3. **Credentials.** Splitting jobs into restartable DAG segments of ≤ 20 h avoids the credential expiry seen earlier.
4. **The 5-slab series is the right priority.** Amorphous a-IWO and a-In₂O₃ at 2 / 1.5 / 1 / 0.8 / 0.7 nm, at constant ~2 % W, is the highest-value use of CERN. It ranks ahead of vacancies, the Al₂O₃ interface and surface variants.
5. **Value of one sample.** One sample per structure gives indicative trends that are useful at a defence.
6. **Runner security.** An acron-driven runner (tickets in a private repo, approval by merge, whitelisted templates, a deploy key limited to that repo) is safe and acceptable on a CERN account, and can be built and tested in about 1–2 days.
7. **ATLAS outputs.** A2 (off-current geometry), A3 (critical thickness, 31.8 nm), A1 (leave-one-film-out) and A4 (DFT inputs → μ_FE) are the ATLAS runs with the most value; about 15–20 launches.

**Questions for the reviewer:**
- (a) Is any assumption likely to fail, and what is the cheapest early check?
- (b) Is the job set the best use of the time? What would you cut or add, and in what order?
- (c) Is the ML-then-DFT protocol defensible as described, or does it need a different validation?
- (d) Is the timeline realistic for 15 Oct?
- (e) Is the runner design safe and robust on CERN (acron, DAGMan, EOS, deploy key)? What would you change before building it in WF-002?
- (f) Which single result would most strengthen the thesis, and which single failure would most weaken it?

| Field | Value |
|---|---|
| UNCERTAINTY | All time estimates are scaled from the past runs in A3. Queue waits are unknown. |
| WHAT WOULD FALSIFY THE PLAN | The timing test shows the slab DFT jobs take more than 4 days; the QC gate fails for the ML structures; or acron/DAGMan cannot run QE with its environment from EOS. |
| RECOMMENDED NEXT ACTION | Codex reviews (`tools\relay.ps1 -Task PLAN-001 -Owner claude -Step review -CodexInWsl`); Claude responds; Mahmoud decides and says go. |

---

## R-RQ-001: Owner response to the Codex review of HO-002 (2026-10-09)

- **Full response.** `claude/responses_to_codex/RQ-001_response.md`.
- **Classification of the 17 objections.** 11 ACCEPTED, 2 PARTIALLY ACCEPTED, 0 EVIDENCE DISAGREES, 4 UNRESOLVED.
- **Ledger.** No status changes. C031 claim text and the caveats of C024, C025 and C030–C033 were revised, each with a history line.
- **HO-002.** Part B was revised in place where an objection was accepted. The original wording is kept in the change log at the bottom of this file. Part A is unchanged.
- **Main correction.** The noise Monte Carlo covers only two estimators at 10× floor, with σ measured 1–2 decades above the 2 nm steep section. It therefore cannot support "noise does not create it" for the estimators that match the paper, and says nothing about instrumental origin.
- **Human decisions.** Three, listed in §3 of the response: the fab request, repeat metrology for the 2 nm steep section, and a blinded re-review.

---

## HO-002: Mobility and SS reconciled with the published values (task RQ-001)

| Field | Value |
|---|---|
| TASK ID | RQ-001 (owner Claude, reviewer Codex) |
| GIT COMMIT | Evidence: public repo `f315b78` (HEAD; `data/` and `analysis_2026-10-06_extraction/` clean). This handoff: the private-repo commit made by the relay on top of `c53a146`. |
| QUESTION | Which definitions, C_ox, V_D and windows reproduce the paper's μ_max (27.4 / ≈4 / 5.1 cm²/Vs) and SS (60–70 mV/dec)? Which values are right for these devices? |
| DATA USED | `data/experimental_raw_preserved_IWO-TFT.xlsx` rows 2–122 (rawest form; identical to `data/experimental_clean.csv`, largest difference 0); the paper `private:sources/Januar2026_SmallStructures.pdf` (text, and pixels of Fig. 1b); protocol code `analysis_2026-10-06_extraction/extraction.py` (imported, not re-implemented) |
| DATA EXCLUDED | **31.8 nm:** excluded from every comparison. The paper has no 31.8 nm device, and the curve never turns off. Its values are still listed in `mobility_definitions.csv`. **TCAD curves:** not used; not in RQ-001's allowed data. **The paper's SI:** not available to us (Figs. S1, S7, S8 and S10 are known only from their captions). |
| METHOD | `claude/evidence/RQ-001/digitise_fig1b.py`, then `rq001_reconcile.py` (settings in `claude/evidence/RQ-001/README.md`). **Mobility:** six definitions at the protocol C_ox; six C_ox variants. **SS:** 31 method variants: two-point minimum; steepest 3/4/5/7 points; one-decade windows starting 2–100× floor; raw and floor-corrected; floor margins 1/3/10×; the registered S1 and A1 windows. **Noise:** Monte Carlo of the minimum-SS estimators (2000 draws). |

**Reviewer: read Part A and the raw files first, commit your independent assessment, and only then read Part B.**

### PART A — EVIDENCE (no interpretation)

#### A1. What the paper states [LITERATURE-SUPPORTED]
1. **μ_max values.**
   - The text gives μ_max = 5.1 cm²/Vs (2 nm) and 27.4 cm²/Vs (13.2 nm) (Sec. 2.2, 2.8).
   - The Fig. 1b axis is labelled "μ_max"; SI Fig. S8 is captioned "maximum field-effect mobility μmax".
   - The main text gives no mobility formula, C_ox value, W/L or V_D.
2. **SS.**
   - Text: "near-thermal-limit SS (60–70 mV dec⁻¹)" (Sec. 2.2).
   - "SS" is also one of the eight fitted parameters of the compact model: Eq. 1e; the VIF list in Sec. 2.5 ("SS = 1.22"); SI Fig. S10e ("S").
   - Figs. 4d and 6e and SI Figs. S9, S11 and S12 call SS an "extracted parameter".
3. **I_off.** Model Eq. 1a adds a constant I_off to the blended current.

#### A2. Digitised Fig. 1b, IWO markers [DERIVED; `paper_fig1b_digitised.csv`]
**Read uncertainty.** ±1.5 px. The 60 mV/dec dashed line sits 1.4 px from where the axis calibration puts it.

| | 2.0 nm | 6.3 nm | 13.2 nm |
|---|---|---|---|
| μ_max (cm²/Vs) | 4.95 ± 0.46 | 3.73 ± 0.46 | 27.2 ± 0.46 |
| SS (mV/dec) | 61.8 ± 1.8 | 87.4 ± 2.6 | 119.3 ± 3.5 |
| I_off (axis labelled "A") | 3.3e-15 | 1.4e-13 | 6.8e-12 |
| Our floor (A/µm, C003) | 4.61e-15 | 1.53e-13 | 6.60e-12 |

- **The SS values are not 60–70 mV/dec at every thickness.** Only the 2 nm value lies in that range.
- **The I_off markers agree with our per-µm floors** within factors of 0.71, 0.93 and 1.02.

#### A3. Mobility [DERIVED unless marked; `mobility_definitions.csv`, `mobility_scale_test.csv`]
Settings: C_ox = 8.955e-7 F/cm² (protocol, fixed at commit 7a61687), W/L = 290/20, V_D = 0.7 V. "Peak" means the largest value for 0 ≤ V_G ≤ 3 V.

| Definition | 2.0 nm | 6.3 nm | 13.2 nm | Ratio 13.2/2.0 (paper 5.37) |
|---|---|---|---|---|
| μ_FE,lin = L·g_m/(W·C_ox·V_D), peak | 12.15 | 10.95 | 50.17 | 4.13 |
| **μ_sat = 2L/(W·C_ox)·(d√I_D/dV_G)², peak** | **5.09** (at 1.75 V) | **3.86** (2.55 V) | **27.40** (0.95 V) | **5.39** |
| μ_eff, V_T = V_th,cc, peak | 8.17 | 6.42 | 38.16 | 4.67 |
| μ_eff, V_T = V_th,ELR, peak | 15.15 | 14.00 | 68.43 | 4.52 |
| μ_eff, V_T from the power-law fit, peak | 7.43 | 5.52 | 40.95 | 5.51 |
| Y-function μ0 | 8.11 ± 0.17 | 5.81 ± 0.33 | 39.5 ± 0.5 | 4.87 |
| Paper | 5.1 (text) | 3.73 (digitised) | 27.4 (text) | 5.37 |

1. **μ_sat matches the paper's values with no adjustable factor.**
   - Deviations: −0.3 % at 2.0 nm, +0.01 % at 13.2 nm (against the text values), and +3.4 % at 6.3 nm (against 3.73 ± 0.46 digitised).
   - With one free common factor, the next best are:
     - μ_eff with the power-law V_T: factor 0.68, residuals ≤ 1.3 %;
     - Y-function: factor 0.66, residuals ≤ 5 %.
2. **Sensitivity of the μ_sat peak to the derivative estimator** (central, forward, backward, Savitzky–Golay 5/7/9 points): 5.04–5.11, 3.78–3.90 and 25.9–27.5 cm²/Vs.
3. **No constant factor reconciles the g_m-based μ_FE.**
   - The ratio paper/ours is 0.42, 0.34 and 0.55 for 2.0, 6.3 and 13.2 nm.
   - The C_ox that would make each film match is 2.13e-6, 2.45e-6 and 1.64e-6 F/cm².
   - The V_D that would make each film match, at the protocol C_ox, is 1.67, 1.92 and 1.28 V.
4. **C_ox variants.** Every mobility scales as 1/C_ox.

   | Variant | C_ox (F/cm²) | μ_sat peaks (2.0 / 6.3 / 13.2 nm, cm²/Vs) |
   |---|---|---|
   | HfO2 15 nm only (ε 19.57) | 1.155e-6 | 3.94 / 2.99 / 21.2 |
   | HfO2 ε 25 + Al2O3 | 1.077e-6 | — |
   | HfO2 ε 16 + Al2O3 ε 7 | 7.24e-7 | — |
   | Series channel layer (2 nm, ε 9) | 7.31e-7 | — |
   | C_eff = 0.87 C_ox | 7.79e-7 | — |
5. **Is μ_sat used inside its validity range (V_G − V_T ≤ V_D = 0.7 V) at its peak?**

   | Overdrive at the μ_sat peak (V) | 2.0 nm | 6.3 nm | 13.2 nm |
   |---|---|---|---|
   | With V_T from the power-law fit | 1.28 | 2.23 | 0.69 |
   | With V_T,ELR | 0.44 | 1.08 | 0.26 |
6. **Algebra [DERIVED].** For a square-law device with constant μ in the linear regime, μ_sat = μ·V_D/(2V_ov − V_D). It equals μ at V_ov = V_D and falls as 1/V_ov above that.
7. **Shape.** μ_sat falls with V_G beyond its peak in every film; at 3 V it is 3.24, 3.20 and 8.71 cm²/Vs. μ_FE,lin rises up to about 3 V [DERIVED; Fig. 1].
8. **Protocol M2 channel mobility** μ_ch = μ0(V_G − V_T)^γ at 1, 2 and 3 V:
   - 2.0 nm: 2.1 / 5.5 / 8.8 cm²/Vs;
   - 6.3 nm: 1.4 / 3.8 / 6.4;
   - 13.2 nm: 30.0 / 37.8 / 42.8.

   [FITTED model, protocol §3.3]

#### A4. SS [DERIVED; `ss_method_scoring.csv`, `ss_sliding_window.csv`, `ss_noise_mc.csv`]
Paper SS used for scoring: the digitised 61.8 / 87.4 / 119.3 mV/dec. Thermionic limit: 59.5 mV/dec at 300 K.

| Method (floor margin) | 2.0 nm | 6.3 nm | 13.2 nm | Largest deviation |
|---|---|---|---|---|
| Floor-corrected steepest 4 points (≥ 3× floor) | 64.8 | 91.5 | 119.1 | 5.0 % |
| One-decade window from 3× floor | 61.7 | 82.9 | 110.7 | 7.2 % |
| Floor-corrected steepest 3 points (≥ 3× floor) | 59.2 (below the thermionic limit) | 81.7 | 110.7 | 7.2 % |
| One-decade window from 5× floor | 61.1 | 89.7 | 107.8 | 9.6 % |
| Steepest 3 points | 63.6 | 89.7 | 104.5 | 12.4 % |
| Two-point minimum (≥ 10× floor) | 69.4 | 88.4 | 105.7 | 12.4 % |
| Steepest 5 points | 72.7 | 101.9 | 116.3 | 17.7 % |
| One-decade window from 100× floor | 78.9 | 131.7 | 179.0 | 50.6 % |
| A1 window [2.15e-5, 2.15e-4]·I_on (registered amendment) | 123.6 ± 1.0 | 122.7 ± 9.3 | 115.3 ± 2.4 | 100 % |
| S1 window 5e-11 to 5e-10 A/µm (registered) | 165.6 | 177.6 | 111.9 (raw) | 168 % |

1. **Scope of the search.** 31 variants were scored. The 14 within 15 % of the paper in all three films all start at a current 1–12× the floor. The registered windows start 3–4 decades higher at 2.0 nm.
2. **Window position at 2.0 nm.**
   - One-decade SS is 60.6–69.3 mV/dec (σ 1.7–2.4) for windows starting 3.9–22× the floor, i.e. 1.8e-14 to 1.0e-13 A/µm (5–29 pA in total).
   - It rises monotonically above that: 84.5 at 1e-12, 121 at 1e-11, 195 at 1e-10 A/µm.
3. **Noise.** The noise σ_log10 near the low-current levels is 0.0048, 0.156 and 0.015 decades for 2.0, 6.3 and 13.2 nm (protocol estimator `noise_log`).

   | Two-point minimum (≥ 10× floor), 95 % Monte Carlo range | Smoothed reference | Measured |
   |---|---|---|
   | 2.0 nm: 68.0–69.8 | 69.4 | 69.4 |
   | 6.3 nm: 48.8–100.4 (median 70.7) | 80.6 | 88.4 |
   | 13.2 nm: 102.9–118.5 | 112.7 | 105.7 |

4. **Sub-thermal values.** Some estimators give SS below 59.5 mV/dec:
   - the two-point minimum at 2.0 nm with margin ≤ 3× (58.6);
   - floor-corrected 3 points at 2.0 nm (59.2);
   - one-decade windows within 1× floor at 6.3 nm (41.8–51.2, σ 41–53).

#### A5. Other checks
- **Raw vs clean data.** The raw workbook and `experimental_clean.csv` are identical for all four films (121 points each) [DERIVED].
- **Rounding check on the workbook currents** (I × 290 having ≤ 4 significant digits):

  | Fraction of points | 2.0 nm | 6.3 nm | 13.2 nm | 31.8 nm |
  |---|---|---|---|---|
  | I × 290 | 0.11 | 0.30 | 0.65 | 0.19 |
  | I × 1 | 0.04–0.05 | 0.04–0.05 | 0.04–0.05 | 0.01 |
  | I × 14.5 | 0.13 | 0.22 | 0.27 | 0.16 |

  For 2.0 nm the test cannot tell the factors apart [OBSERVED].
- **Reproduction of protocol numbers.** The script reproduces the registered numbers exactly: μ_FE peaks 12.1 / 10.9 / 50.2 and A1 SS 123.6 / 122.7 / 115.3 [DERIVED].

- **UNCERTAINTY:**
  - **Digitisation.** ±1.5 px, i.e. ±0.46 cm²/Vs and ±3 % for SS.
  - **μ_sat estimator spread.** As in A3.2.
  - **SS.** Protocol §3.4 uncertainties, plus the noise Monte Carlo.
  - **Not included:**
    - the C_ox uncertainty (it scales all mobilities together);
    - contact resistance;
    - device-to-device spread (one device per film);
    - the forking-paths effect of scoring 31 SS variants (the best of 31 is optimistic).
- **FILES CREATED:** `claude/evidence/RQ-001/`: `README.md`, `rq001_reconcile.py`, `digitise_fig1b.py`, `paper_fig1b_digitised.csv`, `mobility_definitions.csv`, `mobility_scale_test.csv`, `ss_methods.csv`, `ss_method_scoring.csv`, `ss_sliding_window.csv`, `ss_noise_mc.csv`, `rq001_results.json`, `figures/fig1_mobility_definitions.png`, `figures/fig2_ss_sliding_window.png`, `figures/fig3_local_ss.png`.

### PART B — INTERPRETATION (the reviewer reads this only after their independent assessment)

- **INTERPRETATION:**
  1. **Mobility.** The leading candidate for the paper's μ_max is the peak of the saturation-formula mobility, computed from V_D = 0.7 V curves with C_ox·(W/L) equal to 8.96e-7 F/cm² × 290/20 [INFERRED; no probability is stated] [rev. 2026-10-09, R-RQ-001].
     - Why: a fixed protocol constant and no free factor reproduce two text values to 0.3 % and the digitised third to 3 %. The peaks constrain only the product C_ox × W/L × current normalisation, not each factor. μ_eff (power-law V_T) and the Y-function also fit, with one common factor.
     - What it shows: a definition difference is sufficient to explain the earlier "factor-of-two disagreement" (C024) on our curves. Whether the paper used these same curves (sweep provenance, A vs A/µm) is not established, so C024 stays UNRESOLVED [rev. 2026-10-09, R-RQ-001].
     - Fig. 5d: the paper's falling mobility with V_G is what the saturation formula produces by itself in the linear regime, μ_sat ∝ 1/(2V_ov − V_D) [INFERRED; Fig. 5d may instead be the model μ_sr, which falls by construction].
  2. **SS.** The paper's SS values are compatible with several near-floor estimators. The 31-variant search cannot identify which method, if any of them, the paper used [INFERRED] [rev. 2026-10-09, R-RQ-001].
     - The match is at the 5–15 % level, by several near-floor estimators. The exact method is not identified: possibly the fitted Eq. 1e parameter, which acts on top of a constant I_off.
     - The paper's "60–70 mV/dec" holds only for 2.0 nm; 6.3 and 13.2 nm are about 87 and 119 in its own Fig. 1b [DERIVED from A2].
     - At 2.0 nm the near-floor steep section exists in the recorded values [OBSERVED]. Under independent log-normal noise with σ measured at 1e-12 to 1e-10 A/µm, the Monte Carlo bias of two estimators (two-point minimum and steepest-5, both at 10× floor) is < 2 mV/dec. The MC does not cover the margin-1–3 estimators that match the paper. It also uses noise measured 1–2 decades above the steep section, and cannot detect offsets, range changes, settling or correlated noise, because its "truth" is the smoothed measured curve. Whether the section is channel behaviour is UNRESOLVED. It spans only 0.6–1.3 decades (steepest-3: 0.10 V), at 5–30 pA in total, right above a floor at the setup level [rev. 2026-10-09, R-RQ-001].
  3. **Which values are right for these devices.**
     - **Mobility.** No single number is "the" mobility.
       - For V_D = 0.7 V transfer curves, μ_FE,lin (12.1 / 10.9 / 50.2 at about 3 V) needs no fitted threshold. It is C_ox-normalised transconductance at V_D = 0.7 V, not intrinsic or band mobility: C_ox is geometric, and contacts and gate-dependent charge enter g_m [rev. 2026-10-09, R-RQ-001].
       - Conditional on the V_T definition, μ_sat is outside its validity range (V_G − V_T > V_D) at its peak: at 6.3 nm under all three definitions (power-law, ELR, V_th,cc), and at all three films under V_th,cc (overdrive 1.09 / 1.91 / 0.87 V). No V_T is a measured regime boundary [rev. 2026-10-09, R-RQ-001].
       - The power-law μ_ch (protocol M2) gives the overdrive dependence within that fitted model [FITTED], valid only inside its 1–3 V fit range. At 13.2 nm the μ_sat peak (0.95 V) lies outside that range [rev. 2026-10-09, R-RQ-001].
       - Quote the paper's value as "paper-reported μ_max, numerically reproduced by the saturation-formula peak", never next to μ_FE,lin without both definitions. Every value carries units, C_ox, V_D, derivative and grid [rev. 2026-10-09, R-RQ-001].
     - **SS.** "SS" must always carry its current window, point count and floor handling.
       - The paper's Fig. 1b markers (≈ 62 / 87 / 119 for 2.0 / 6.3 / 13.2 nm), our closest near-floor estimate (floor-corrected steepest 4 points: 64.8 / 91.5 / 119.1) and the I_on-normalised value (124 / 123 / 115) are three different quantities. The last two describe different parts of the subthreshold curve [rev. 2026-10-09, R-RQ-001].
       - They imply equivalent trap densities that differ by more than ×10 (from N_SS = (SS/59.5 − 1)·C_ox/q: about 2e11 vs about 6e12 cm⁻²eV⁻¹ at 2 nm) [DERIVED arithmetic; physical meaning HYPOTHESIS].
- **ALTERNATIVE INTERPRETATIONS:**
  - **Mobility.**
    - (a) The paper used μ_eff or the Y-function with an unreported factor of about 0.67, e.g. V_D = 1.0 V in the formula (×0.70). This also fits within 1–5 %, but needs an extra assumption.
    - (b) The μ_sat agreement is a coincidence and the paper's μ_max is the model μmax of Eq. 5. Against this: the zero-parameter, three-film agreement.
    - (c) A different C_ox combined with a compensating W/L.
  - **SS.**
    - (a) SS is the fitted Eq. 1e parameter.
    - (b) A minimum local slope on a finer or different sweep.
    - (c) A different device or sweep from ours (the PBS device of Fig. 6 starts at 62).
    - (d) Floor subtraction with a different floor value.
- **WHAT WOULD FALSIFY THE RESULT:**
  - **Mobility.** The fab states a mobility formula other than the saturation one, or a C_ox or W/L that changes C_ox·W/L by more than about 5 %.
  - **SS.**
    - The fab's stated SS method, applied to our curves, gives values far from 62 / 87 / 119.
    - The Fig. 1b devices are not our curves (that would also undo A2's I_off agreement).
  - **Either.** A re-run of `rq001_reconcile.py` by the reviewer gives different numbers.
- **RECOMMENDED NEXT ACTION:**
  1. Codex reviews (`/review RQ-001`), and in particular checks the μ_sat derivation and the forking-paths risk in A4.
  2. Mahmoud asks the fab the six questions in `claude/evidence/RQ-001/README.md` (HUM-001).
  3. Until the fab answers, report every mobility and SS with its definition and window. C024 and C025 stay UNRESOLVED; new claims C030–C033 are added.
  4. No ATLAS, CERN or network action is needed for this task.

---

## HO-001: Material for an independent review of NATURE_PLAN.md (task RQ-005)

| Field | Value |
|---|---|
| TASK ID | RQ-005 (owner Codex, reviewer Claude) |
| GIT COMMIT | Evidence: public repo `f315b78`. This file: the private-repo commit that adds it (see `git log`). |
| QUESTION | Is the proposed programme the fastest credible route to an important, defensible result? Which parts should be accepted, modified, deferred or rejected? |
| DATA USED | `data/experimental_clean.csv` (all four films); the outputs listed in `01_CURRENT_STATE.md` §I; the published paper |
| DATA EXCLUDED | None withheld. There is no holdout yet: the only "blind" test so far (6.3 nm, V2 T3) is spent. |
| METHOD | Collation of existing results. No new calculations in this handoff, except a check of `experimental_clean.csv` on 2026-10-07 that gave the 31.8 nm values. |

**Reviewer: read Part A and the raw files first, commit your independent assessment, and only then read Part B.**

---

### PART A — EVIDENCE (no interpretation)

#### A1. Verified facts

All values are in `01_CURRENT_STATE.md` §C–G and `03_CLAIMS_LEDGER.yaml`. The most decision-relevant ones:

1. **Data.** One device per film (2.0, 6.3, 13.2, 31.8 nm), one V_D (0.7 V), no reverse sweep and no I_G. The geometry (W/L = 290/20 µm, 15 nm HfO2 + 2 nm Al2O3, C_ox 8.9554e-7 F/cm²) comes from the device schematic. [MEASURED / taken from the schematic]

2. **Extracted values.** Same protocol for measured and TCAD curves:

   | | 2.0 nm | 6.3 nm | 13.2 nm | 31.8 nm |
   |---|---|---|---|---|
   | V_th,cc (V) | 0.662 | 0.644 | 0.083 | none (never off) |
   | Off-state floor (A/µm) | 4.61e-15 | 1.53e-13 | 6.60e-12 | — (I_D(−3 V) = 3.0e-7) |
   | I_D(3 V) (A/µm) | 5.09e-7 | 4.03e-7 | 3.07e-6 | 3.59e-6 |
   | Peak g_m-based μ_FE (cm²/Vs) | 12.1 | 10.9 | 50.2 | — |

   [DERIVED]

3. **SS** (normalised window [2.15e-5, 2.15e-4]·I_on), measured vs TCAD:
   - 2.0 nm: 123.6 ± 1.0 vs 126.4 mV/dec;
   - 6.3 nm: 122.7 ± 9.3 vs 121.3;
   - 13.2 nm: 115.3 ± 2.4 vs 131.3.

   Local SS against I_D/I_on collapses onto one curve for the three thinner films. [DERIVED / COMPUTED / OBSERVED]

4. **The TCAD is calibrated per film.**
   - Q_f is fitted to V_th,cc (one value for 2.0 and 13.2 nm, another for 6.3 nm).
   - μ_band is fitted to I_on.
   - The tail width is fitted on 2.0 nm.
   - The thickness laws are two-point laws.
   - Work function, χ, Q_f and ΔE_c are not separately identifiable; μ_band trades off against N_t. [FITTED / DERIVED]

5. **Every out-of-sample 6.3 nm threshold test failed:** V1 run_0014 −0.29 V; V2 registered variants P −0.37 V and E −0.23 V. [FALSIFIED]

6. **At 13.2 nm the TCAD reproduces μ_FE(V_G) from 1 to 3 V within ±6 %**, with the level set by calibration. At 2.0 and 6.3 nm it does not (6.3 nm: γ 0.57 vs 1.13). [COMPUTED]

7. **DFT**, crystalline structures, PBE:
   - The confinement gap increase is +0.335 eV at 2 nm and +0.90 eV at 1 nm (HSE-corrected +0.95–1.00 eV).
   - A 0.51 nm slab relaxes to an In(OH)3-like layer with a 3.14 eV gap (preliminary).
   - The W 5d level is resonant 1.2–1.8 eV above the CBM.
   - No amorphous, defect, interface or contact calculations exist. [COMPUTED]

8. **The published paper** (`sources/`) already contains:
   - the thickness series;
   - an 8-parameter analytic model with Monte Carlo identifiability;
   - crystalline DFT and IWO/HfO2 interface slabs;
   - a DOS reconstruction;
   - roughness-limited mobility;
   - PBS/NBS, 65/85 °C and annealing studies;
   - an off-current model I_off ∝ t·n_FB (Eq. 1f);
   - the qualitative claims "W ... promotes smoother charge delocalization" (Sec. 2.3) and "crossover from near-band transport in thicker channels to disorder- and interface-limited transport in ultrathin films" (Sec. 2.5).

   [LITERATURE-SUPPORTED]

#### A2. Current discrepancies

1. **Mobility.**
   - Paper: μ_max 27.4 / ≈ 4 / 5.1 cm²/Vs (13.2 / 6.3 / 2.0 nm), falling with V_G (Fig. 5d).
   - Ours, from the same curves: g_m-based μ_FE peaks at 50.2 / 10.9 / 12.1, rising up to about 3 V.
   - The paper's definition, C_ox and V_D are not known to us.
2. **SS at 2 nm.**
   - Paper: 60–70 mV/dec (≈ 62 in Figs. 4d and 6e).
   - Ours: 89.1 ± 0.5 over 3.3 decades (5.6e-14 to 1e-10 A/µm) and 123.6 in the normalised window.
   - Two-point minima near the floor reach 33.4 mV/dec at 6.3 nm, i.e. noise.
3. **6.3 nm.**
   - The prediction failure is listed in A1, item 5.
   - The miss decomposes into a rigid 0.294 V shift plus a 0.16–0.19 V shape part (`analysis_2026-09-25/SYNTHESIS.md` §A.2).
   - Eight electrostatic variants were excluded quantitatively.
4. **Off-current against V_D.**
   - No V_D-dependent data exist.
   - Our ungated-strip model (ohmic) and the paper's Eq. 1f (diffusion) predict ×7 and ×1.02 respectively, going from 0.1 to 0.7 V.
   - The strip has one constant fitted on 13.2 nm; it predicts the 2.0 and 6.3 nm floors at 0.46 and 0.64 of the measured values.
5. **Crystalline vs amorphous.** All DFT, the paper's and ours, is crystalline, while the HRTEM in the paper shows no long-range order.
6. **Gate-oxide interface.** Our TCAD has Al2O3 (2 nm) against the channel; the paper's DFT interface is IWO/HfO2. Not confirmed with the fab.
7. **Thickness dependence is not uniform** (one device each):
   - from 2.0 to 6.3 nm, V_th −0.018 V, μ ×0.9 and I_on ×0.79;
   - from 6.3 to 13.2 nm, V_th −0.561 V, μ ×4.6 and I_on ×7.6;
   - 31.8 nm never turns off;
   - the floor's local exponent goes from 3.1 to 5.1.

#### A7. Holdout opportunities

Each of these must stay hidden from calibration until predictions are registered:

| Data | Status |
|---|---|
| New measurements of the existing chips: floor against V_D, reverse sweeps, I_G, other devices of the same films | Truly unseen. The best near-term holdout. |
| 65/85 °C transfer curves (paper SI Fig. S12) | Unseen in our data files. Eligible only if nobody on our side has looked at SI Fig. S12 (to be confirmed). |
| In2O3 transfer curves (3/10/11 nm) | Not in our data files, but seen as figures (Fig. 1a). Weak holdout. |
| Bias-stress series | Seen as figures (Fig. 6). Weak holdout. |
| Any new fab run (thickness × W matrix, sub-1 nm, mesa structures) | Strong holdout, if the fab acts as custodian. |
| 31.8 nm curve | **NOT eligible.** It has been in `data/experimental_clean.csv` since September, and the V1 model is known to fail on it. |

---

### PART B — INTERPRETATION (read only after your independent assessment)

#### B3. Assumptions in NATURE_PLAN.md

Every item is an assumption or hypothesis, not a result.

| # | Assumption | Status | Evidence so far |
|---|---|---|---|
| 1 | The fab can and will make two new device runs within about 8 months | HYPOTHESIS | Not asked yet (HUM-001) |
| 2 | A model without target-device post-hoc fitting predicts new devices within useful tolerances (e.g. V_th ±0.1 V) | HYPOTHESIS | Three out-of-sample V_th failures at 6.3 nm count against it |
| 3 | Independent measurements (C–V, Hall, XRR, XPS, temperature) can pin the non-identifiable parameter combinations | HYPOTHESIS | Plausible in principle (SYNTHESIS item 0.4); not shown |
| 4 | Sub-1 nm sputtered IWO is continuous and switches | HYPOTHESIS | DFT suggests 0.51 nm may become an insulating In(OH)3-like layer |
| 5 | The floor is an ungated strip | HYPOTHESIS | — |
| 6 | Our mobility and SS definitions are the ones to report | ASSUMPTION | May change after RQ-001 |
| 7 | Amorphous DFT will reveal a W-specific effect that crystalline DFT misses | HYPOTHESIS | — |
| 8 | A record device is achievable | HYPOTHESIS, no evidence | Best existing device: 13.2 nm, μ_FE 50, on/off 4.7e5 |
| 9 | An application (2T0C or a two-tier stack) strengthens the paper | ASSUMPTION | The external proposal suggests making it a late gate; Claude agrees |
| 10 | Pre-registered device modelling is novel enough to count as a contribution | ASSUMPTION | No literature search has been done |
| 11 | The plan's "31.8 nm blind test" | ERROR, corrected | The curve was already in our data |

#### B4. Proposed central claim (the strongest claim the plan is trying to test)

- Global parameters are calibrated on declared training devices and on independent measurements, then frozen.
- With them, a physics model predicts the transfer characteristics of W:In2O3 TFTs, in registered blind tests, at thicknesses and W contents it has never seen.
- The same model identifies what limits the channel at the atomic scale (surface vs bulk traps, confinement, W chemistry).
- Possible extension to be tested: the model locates a critical thickness t_c(C_W) (H1).

#### B5. Strongest alternative explanations

| Mechanism in the plan | Alternatives |
|---|---|
| Thickness trend from traps and confinement | (a) back-surface depletion by adsorbates; (b) donor density growing with thickness; (c) onset of crystallinity or grain growth; (d) device-to-device spread with no real trend change |
| SS values | Window position relative to the floor; VG grid phase; noise; different definitions |
| Mobility | Definition and C_ox; contact resistance; trap filling (θ_net < 0) |
| Off-state floor | Ungated strip; diffusion (Eq. 1f); edge or substrate leakage; setup limit (2.0 nm) |
| 6.3 nm anomaly | Device spread; thickness error; batch; sweep history; real non-monotonic physics |
| W effect | Fewer V_O (the paper's view); localization/IPR (H2); Coulomb scattering; m* change; W as a donor |

#### B6. Minimum new data

**REQUIRED**
1. Harmonised definitions: the fab's C_ox, V_D, mobility formula and SS method.
2. At least 10 devices per thickness on the existing chips, each with:
   - multi-V_D transfer curves (0.05 / 0.1 / 0.7 / 1.0 V);
   - forward and reverse sweeps;
   - I_G;
   - the floor against V_D.
3. True thicknesses (XRR/TEM) and the run provenance of each device.
4. One new fab run: a dense thickness series (3–15 nm), at least two W contents, mesa and blanket structures, at least 5 devices per split.
5. C–V on MOS capacitors (Q_f, D_it).

**NICE-TO-HAVE**
- gated Hall;
- TLM;
- temperature series from 250 to 400 K;
- XPS (O 1s, W 4f);
- EXAFS;
- sub-1 nm devices;
- more than two W contents;
- an application demonstration;
- amorphous DFT;
- In2O3 control devices in the same run.

#### B8. Risks, and results that would make the direction scientifically uninteresting

1. **Mobility and SS.** After harmonisation, IWO is unremarkable against the literature.
2. **Statistics.** With device statistics, the thickness trends fall within device-to-device spread, so no clean law or t_c exists.
3. **Off-state floor.** It turns out to be a layout or setup artefact. That is an engineering fix, not physics.
4. **Prediction quality.** V3 passes blind tests only with uncertainty bands too wide to be informative.
5. **Sub-1 nm.** The films are discontinuous or insulating.
6. **Amorphous DFT.** It shows no W-specific effect beyond V_O chemistry, which the paper already claims.
7. **Origin of t_c.** It is simply the onset of crystallinity (structural), a known effect in sputtered In2O3.
8. **Fab capacity.** The fab cannot provide statistics or a new run. Without new data there is no route beyond a modelling paper.

| Field | Value |
|---|---|
| UNCERTAINTY | All trends rest on one device per film. The parameter values are non-unique (C018). |
| WHAT WOULD FALSIFY THE PLAN'S PREMISE | Items 1, 2 and 8 above. |
| FILES CREATED | This handoff; `01_CURRENT_STATE.md`; `02_RESEARCH_QUESTIONS.md`; `03_CLAIMS_LEDGER.yaml`; `claude/NATURE_PLAN.md` (copy, status PROPOSED) |
| RECOMMENDED NEXT ACTION | Codex runs RQ-005 (`prompts/02_CODEX_INDEPENDENT_REVIEW.md`). In parallel, Claude runs RQ-001 and RQ-003, which need no new data. |

---

## Change log

### 2026-10-09, R-RQ-001 (Claude, owner response to the Codex review of HO-002; see `claude/responses_to_codex/RQ-001_response.md`)

These HO-002 Part B passages were revised in place; each is marked "[rev. 2026-10-09, R-RQ-001]". The original wording was as follows (also in git at `b2d668e`):

1. **B1 (O1).** "The paper's μ_max is, with high probability, the peak of the saturation-formula mobility, computed from these same V_D = 0.7 V curves with C_ox ≈ 8.96e-7 F/cm² and W/L = 290/20 [INFERRED]."
2. **B1 (O2).** "What it resolves: the earlier "factor-of-two disagreement" (C024) is a difference of definition, not of data."
3. **B2 (O4).** "The paper's SS values behave like a "steepest slope just above the off-state floor" quantity [INFERRED]."
4. **B2 (O5).** "At 2.0 nm the near-floor steep section is real in the sense that noise does not create it (Monte Carlo bias < 2 mV/dec). But it spans only 0.6–1.3 decades, at 5–30 pA in total, right above a floor at the setup level."
5. **B3 (O9, O10, O11, O15).**
   - "For V_D = 0.7 V transfer curves the valid model-free quantity is μ_FE,lin (12.1 / 10.9 / 50.2 at about 3 V)."
   - "μ_sat is outside its validity range at its peak in at least the 6.3 nm film, under both V_T definitions."
   - "The power-law μ_ch (protocol M2) gives the overdrive dependence."
   - "The paper's μ_max should be quoted only as "saturation-formula peak", never next to μ_FE,lin."
6. **B3 (O14).**
   - "SS. "SS" must always carry its current window."
   - "The near-floor minimum (≈ 62 / 87 / 119 for 2.0 / 6.3 / 13.2 nm) and the I_on-normalised value (124 / 123 / 115) describe different parts of the subthreshold curve."

The R-RQ-001 entry at the top of the file was also added.
