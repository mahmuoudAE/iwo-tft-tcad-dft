# C10 ATLAS campaign: state, gates, budget and cost model (2026-10-14)

**What this is.** A read-only audit of what is left of the registered C10 campaign and what can be launched now under the frozen register. It is a planning input. It is not a registration, not an amendment and not a launch request.

**What was done to write it.**
- Nothing was launched, committed, pushed or edited. The only file written is this one.
- No CERN contact, no `results/sealed/` access, no AFF-6p3 or STRIP-6p3 output (neither exists yet), and no amorphous DFT quantity.
- Not opened: any output of run_0075, run_0076 or run_0077. Their RUN_INDEX timing rows were read. Their scored JSONs in `register_scores/` were read as allowed.
- Read for timing only: run_0061 to run_0074 `execution.json` and `deckbuild.out`, and the `transfer.log` row count of run_0073 and run_0069. These are all runs that were seen before register revision 2.

**Labels.**
- MEASURED (runtime) = runner wall clock (RUN_INDEX `elapsed_s`) or ATLAS's printed "Time for bias point". It is a measured runtime of our tool, not device data.
- CALCULATED = arithmetic shown, from the inputs cited.
- ASSUMED = an estimate with no measurement behind it.
- CALCULATED (ATLAS) = a simulator output as scored by the frozen `score_register.py` (c0f28bb9).
- Paths are relative to `IWO_PHYSICS_CONSTRAINED_MODEL_V1/` unless they start with `private:` (`iwo-tft-research-private/`).

---

## 1. Bottom line

1. **Budget.** 17 of 200 C10 launches are used (run_0061 to run_0077, failures included). 183 remain. This equals the global counter: 77 of 260 used (`config/solver.yaml` max_launches 260).
   - 11 of the 185 matrix entries are done; 174 are unlaunched.
   - The matrix reserve of 15 has 6 already spent: the 5 extra S0-02 repairs and the S2-11 rerun. The **effective reserve is 9** if every remaining matrix entry ran. It drops to 3 if all six A41(d) trigger launches run. This matches register A41(e).
2. **Launchable now (registered, plan runnable, reviewed): only `config/campaign_C10_DIAG.json`.** It has 18 new launches; S2-11 is reused as run_0076. It still needs the pre-launch checks and the user's go for that launch.
   - Everything else is held, conditional, kept out, template-only, or premature (§4).
   - One hazard: `campaign_C10_S4a_spacefilling.json` is marked `runnable: true` although its prerequisites (S3 adoption) do not exist (§4.9).
3. **All four DIAG stop gates will stop the plan, whatever ATLAS returns.** This follows from the frozen scorer (CALCULATED from the code, §4.1):
   - `hc_nominal` and `hc_generation` can only give PASS with a demonstrated in-scope resolution;
   - A41(d) registers no ceiling run for S2-04, S2-06, S2-01 or S2-02;
   - so every gate ends UNRESOLVED or FIRED, and each needs an audited `--ack-gate`. Plan for 4 audit files.
4. **QTNLSC is not mesh-converged** (S2-11 registered FAIL: max 2.86 dec, 73 of 75 resolved points > 0.1 dec).
   - Every QTNLSC-based H-C verdict (S2-04, S2-06, S2-08, and the QTNLSC part of S2-12/13) stays PROVISIONAL or UNRESOLVED.
   - Worst-set floor-scale currents may not be interpreted (S2 stop rule).
   - A further mesh series needs a new result-informed amendment (Codex 2026-10-13T03:36Z). §5 gives the tunnelling-mesh branch.
5. **Two-carrier runs are the largest launch-validity risk in DIAG.**
   - S1-06 (13.2 nm, two carriers) stalled for 48.6 min at V_G −1.8 → −1.6 V and timed out at 3600 s (CALCULATED from run_0073 `deckbuild.out`, §6.2).
   - S2-01 and S2-02 are the same film and carrier count, plus extreme or suppressed SRH, with the same 3600 s timeout. They will probably time out and be invalid (ASSUMED from that precedent).
   - The register allows one S1-06 continuation repair (register §3). Doing it first is the largest legitimate saving available (§7).
6. **The full registered path does not fit under 200.** It needs 186 new launches against 183 available (§3.3):
   - all S3/S4/S5/S6/S7 entries;
   - contacts (if triggered) and the Schottky check;
   - the S1-06 repair;
   - the unbudgeted 3-D NC robustness branch;
   - all A41(d) triggers;
   - the reserve items.

   It fits only if the design's own early exits or the savings in §7 apply. Reinstating the kept-out FNORD, BQP, Boltzmann and S2-05/07 entries (7) plus a tunnelling-mesh branch (2–4) needs those savings.
7. **Wall time** (sequential, one 32-bit licence; CALCULATED from measured runtimes, §6):
   - C10 so far: 5.66 h, of which 47 % was two timeouts;
   - DIAG: about 6.3 h typical (10.4 h if every run hits its timeout);
   - lean full path to S7: about 25 h typical;
   - full registered path: about 36 h typical;
   - timeout-sum upper bounds are about 82 h (lean) and about 122 h (full).

---

## 2. Done so far (RUN_INDEX rows labelled `c10_*`; MEASURED runtime)

| Run | Label (entry) | Exit / converged | Wall s | Note |
|---|---|---|---:|---|
| run_0061 | c10_s0_01_2p0 (S0-01) | 0 / yes | 395.8 | baseline 2.0 nm |
| run_0062 | c10_s0_02_2p0 (S0-02) | 0 / no | 14.2 | memory failure (automatic slicing, old 2 GB limit) |
| run_0063 | c10_s0_02_2p0 | 0 / no | 15.5 | memory failure |
| run_0064 | c10_s0_02_2p0 | 0 / no | 24.8 | memory failure |
| run_0065 | c10_s0_02_2p0 | 0 / yes | 388.7 | QT mesh flush with the oxide, ignored ("must enclose oxide") |
| run_0066 | c10_s0_02_2p0 | 0 / yes | 588.6 | rectangular QT mesh; SIGN_REVERSAL, KCL failed (no continuity coupling) |
| run_0067 | c10_s0_02_2p0 | 0 / yes | 1246.0 | **pinned S0-02** (QTNLSC worst set, automatic slicing) |
| run_0068 | c10_s1_01_6p3 (S1-01) | 0 / yes | 493.7 | |
| run_0069 | c10_s1_02_13p2 (S1-02) | 0 / yes | 735.4 | |
| run_0070 | c10_s1_03_13p2 (S1-03) | 0 / yes | 1786.5 | mesh ×0.7, 24,255 nodes |
| run_0071 | c10_s1_04_2p0 (S1-04) | 0 / yes | 476.8 | DOS ×2 |
| run_0072 | c10_s1_05_2p0 (S1-05) | 0 / yes | 295.7 | 3-D NC (registered expectation FAILED, A13) |
| run_0073 | c10_s1_06_13p2 (S1-06) | timeout / no | 3600.5 | two carriers; **unresolved, repair allowed (register §3)** |
| run_0074 | c10_s1_07_2p0 (S1-07) | 0 / yes | 310.3 | profiling check PASS (2.05e-4 dec, register §0) |
| run_0075 | c10_s2_11_2p0 (S2-11) | timeout / yes | 6060.0 | sealed; invalid for scoring, never substituted (A41(b)) |
| run_0076 | c10_s2_11_2p0 (S2-11) | 0 / yes | 2172.4 | **registered S2-11: FAIL** (hc_mesh 2.858 dec); viewed by the user (not blind) |
| run_0077 | c10_s0_02_dos2_2p0 (S0-02-DOS2) | 0 / yes | 1783.5 | DOS2 I_G pair qualified, R = 2.20233e-31 A/µm |

- **Sum:** 20,388.4 s = 5.66 h (CALCULATED).
- **Lost to the two timeouts:** run_0073 + run_0075 = 9,660.5 s = 47.4 % (CALCULATED).
- **Matrix entries done (11):** S0-01, S0-02, S1-01 to S1-07, S2-11, S0-02-DOS2. S1-06 counts as launched: its label has a row, so `run_campaign.py` reports it and never relaunches it without `--retry`.

---

## 3. Remaining entries and budget

### 3.1 S2 (17 unlaunched of 19)

Common to every S2 entry:
- 2.0/6.3/13.2 nm share the start parameters: Q_f 1.38345e12 cm⁻², N_s 4e12 cm⁻², W_T 0.040 eV, N_D 2.5e17 cm⁻³, μ∞ 100.005 cm²/Vs, ℓ 7.248 nm. All are ASSUMED start values or FITTED anchors (matrix `shared_start_values`).
- Model file V3, sequential.

| Id | Film | Flags / key params (matrix) | Done | Plan / status |
|---|---|---|---|---|
| S2-01 | 13.2 | SRH extreme τ 1e-9 s, σ 1e-13 cm², TRAP.TUNNEL + TRAP.HURKX, MASS.TUNNEL 0.2123, carriers 2; timeout 3600 | no | DIAG |
| S2-02 | 13.2 | SRH suppressed, σ 1e-20 cm², carriers 2; 3600 | no | DIAG (matched control, A9) |
| S2-03 | 2.0 | as S2-01 with MASS.TUNNEL 0.2543; 1800 | no | DIAG (anomaly checkpoint) |
| S2-04 | 2.0 | QTNLSC nominal oxide (HfO2 χ 2.5/E_g 5.8/m 0.20; Al2O3 1.25/8.8/0.35); 1800 | no | DIAG |
| S2-05 | 6.3 | QTNLSC nominal; 2200 | no | **kept out** (register §3) |
| S2-06 | 13.2 | QTNLSC nominal; 3600 | no | DIAG |
| S2-07 | 6.3 | QTNLSC worst (HfO2 3.2/5.8/0.10; Al2O3 1.6/8.8/0.30); 2200 | no | **kept out** |
| S2-08 | 13.2 | QTNLSC worst; 3600 | no | DIAG |
| S2-09 | 2.0 | FNORD worst, F.AE 2.171e-6 A/V², F.BE 8.628e7 V/cm (CALCULATED, field-transferred); 1800 | no | **kept out** ("FNORD duplicate") |
| S2-10 | 13.2 | FNORD worst; 3600 | no | **kept out** |
| S2-11 | 2.0 | QTNLSC worst, oxide y-mesh ×0.5 | **yes** (run_0076; run_0075 invalid) | done: FAIL |
| S2-12 | 2.0 | QTNLSC nominal + ITAT (HfO2 traps 1e19 cm⁻³, 1.0 eV, ^tat.poisson); 2400 | no | DIAG |
| S2-13 | 13.2 | as S2-12; 4800 | no | DIAG |
| S2-14 | 13.2 | strip deck, Q_f on, V_D 0.1/0.7 V; 900 | no | DIAG |
| S2-15 | 2.0 | strip, Q_f on; 900 | no | DIAG |
| S2-16 | 13.2 | strip, Q_f = 0; 900 | no | DIAG |
| S2-17 | 2.0 | strip, Q_f = 0; 900 | no | DIAG |
| STRIP-6p3 | 6.3 | strip, Q_f on; 900 | no | DIAG; **sealed** (§4.6) |
| S0-02-DOS2 | 2.0 | S0-02 with DOS 768/384 | **yes** (run_0077) | done |

### 3.2 S3 (29 unlaunched)

| Id | Film | Flags | Plan / status |
|---|---|---|---|
| S3-01 / 02 / 03 | 2.0 / 6.3 / 13.2 | no confinement (ΔE_c = ΔE_g = Δm = 0, 3-D NC) | DIAG (H-E) |
| AFF-2p0 / AFF-6p3 | 2.0 / 6.3 | affinity shift only off | DIAG (H-E); **AFF-6p3 sealed** |
| S3-04 / S3-07 | 2.0 | bulk tail / 50:50 tail | **kept out as duplicates.** At t = 2 nm, N_t = N_s/2 nm = 2e19 cm⁻³ in every placement (CALCULATED), so the deck equals S0-01 |
| S3-05 / 06 | 6.3 / 13.2 | bulk tail (N_t 2e19, 3.15× / 6.6× the surface tail) | later order (register §3 step 5); no runnable plan |
| S3-08 / 09 | 6.3 / 13.2 | 50:50 tail | later order (step 5); no runnable plan |
| S3-10 | 6.3 | no tail | DIAG_HF (held) |
| S3-11 / 12 / 13 | 2.0 / 6.3 / 13.2 | IGZO.TOKYO GAMMA0 −0.31 (TGAMMA 178.4 K, NCRIT 1e20, MUN 12.977/40.2607/60.5388) | DIAG_HF (held) |
| S3-27 | 6.3 | S3-12 with Q_f +1e12 cm⁻² and MUN ×0.6 (24.1564): native IGZO profiling check | DIAG_HF (held) |
| S3-14 / 15 / 16 | 2.0 / 6.3 / 13.2 | IGZO GAMMA0 +0.30 | later order; status **ambiguous** (§4.6) |
| S3-17 / 18 / 19 | 2.0 / 6.3 / 13.2 | Schottky 0.2 eV + image-force lowering; workfun 4.2184/4.4378/4.4765 eV, ARICHN 30.56/26.30/25.51 | **trigger-gated** (H-F D4); register order step 10 |
| S3-20 / 21 / 22 | 2.0 / 6.3 / 13.2 | Schottky 0.5 eV + lowering | trigger-gated |
| S3-23 | 6.3 | Schottky 0.5 eV, no lowering | trigger-gated |
| S3-24 / S3-25 | 2.0 | BQP, DFT shift off (m_z 0.139 / 0.2543) | **kept out** |
| S3-26 | 2.0 | Boltzmann | **kept out** |

### 3.3 S4a/S4b/S4c/S4d/S5 (99 unlaunched) and the budget arithmetic

| Stage | Entries | Parameters | Plan |
|---|---:|---|---|
| S4a | 45 (15 candidates × 3 films) | pre-registered Latin hypercube in (N_s, W_T), seed 20261010; 3-D variant with GAMMA0, seed 20261011 (`if_igzo_branch_adopted`). Candidate 1 = start point. Q_f, μ∞ and ℓ are profiled offline | `campaign_C10_S4a_spacefilling.json`, **runnable=true (hazard, §4.9)** |
| S4b | 18 (6 × 3) | `{fit:…}` tokens from the quadratic surrogate | template |
| S4c | 3 | best model, profiled Q_f and MUN written natively | template |
| S4d | 3 | runner-up S3 branch at calibrated values | template |
| S5 | 30 | 3 folds × (4 training candidates × 2 films + 2 frozen predictions) | template |

**Budget (CALCULATED from RUN_INDEX and `campaign_matrix.json`).**

| Quantity | Launches |
|---|---:|
| C10 used (17 distinct run ids, failures included) | 17 |
| C10 remaining under the cap (200 − 17), equal to the global 260 − 77 | 183 |
| Matrix entries unlaunched (185 − 11) | 174 |
| Effective matrix reserve (200 − 17 − 174) | **9** (A41(e)) |
| … if all six A41(d) refinements run | 3 |
| … if Codex's bounded 2-launch mesh amendment is added (03:36Z) | 7, or 1 with all triggers |
| Kept-out entries the register path does not launch (S2-05, S2-07, S2-09, S2-10, S3-04, S3-07, S3-24, S3-25, S3-26, S6-16..S6-19, S6-27) | 14 (practical headroom) |

**Registered or committed launches that are not matrix entries:**

| Item | Launches |
|---|---:|
| S1-06 continuation repair (register §3) | 1 |
| Schottky native check (design §5.2, only if contacts run) | 1 |
| A41(d) refinements (conditional) | ≤ 6 |
| **3-D NC robustness branch "calibrated separately in S4"** (register §3, l.2169) | no matrix entries exist: **unbudgeted**, about 15–16 (§7, F3) |
| Reserve items: PRPMOB diagnostic; Schottky × IGZO combination | 1 + 1 |
| TAT.SLICEPTS sensitivity (only by amendment) | 1–2 |
| N1 affinity-only runs (conditional on the amorphous ΔE_c law; blind read-out) | 3 |

**Scenarios (new launches; CALCULATED counts).**

| Scenario | New launches | C10 total |
|---|---:|---:|
| **Lean.** DIAG 18 + DIAG_HF 5 + tails 4 + IGZO +0.30 3 + S4a 42 (candidate 1 reused) + S4b 0 (S4a abort) + S4c 3 + S4d 3 + S5 30 + S6 12 (early exit 10 + S6-13/15) + S7 2 + S1-06 repair 1 + 3-D NC 15; no contacts | 138 | 155 |
| **Full register path, no early exits.** 160 non-kept-out matrix entries (incl. contacts 7, S4a 45, S4b 18, S6 22) + Schottky check 1 + S1-06 1 + 3-D NC 16 + A41(d) 6 + PRPMOB 1 + combination 1 | 186 | **203 (over the cap by 3)** |
| Full path + tunnelling-mesh branch (4) + the 7 kept-out runs the user listed (FNORD ×2, S2-05/07, BQP ×2, Boltzmann) | 197 | 214 |

So the user's full wish list fits only with the design's early exits:
- the S4a abort saves 18;
- the S4b early stop saves up to 9;
- the S6 early exit saves up to 12.

It also needs the savings of §7. Claude's registered forecast (H-J: best S4a √J 0.25–0.65 dec) makes the S4a abort plausible. That is a forecast, not a result.

---

## 4. Gates, approvals, sealing, order and amendments, by item

### 4.1 DIAG (18 new launches): approved, launchable after checks

**Order (frozen in the plan, hash-bound):** S2-11 (reused, run_0076) → S2-04 → S2-06 → S2-03 → S2-01 → S2-02 → S2-08 → S2-12 → S2-13 → S2-14 → S2-15 → S2-16 → S2-17 → STRIP-6p3 → S3-01 → S3-02 → S3-03 → AFF-2p0 → AFF-6p3.

**Approval state.**
- Registered diagnostic set (register §3, A12/A16).
- Codex TCAD review: DIAG GO-WITH-CHANGES (2026-10-12T13:18Z). The changes were made through runner revisions 1–3: Codex OK 21:14Z; S2_RUNNER_GATES rev 3.
- Codex 2026-10-13T03:36Z: "Continue the approved DIAG screens through their stop gates."
- **Still needed:**
  - the user's go for this launch;
  - the pre-launch checks: `regress_sealed_aware.py` must print "unexpected differences 0"; `make_campaign_configs.py --check`; the scorer hash c0f28bb9 and its selftest; runner files equal to 1375164;
  - no DeckBuild, ATLAS or TonyPlot process running.

**Automatic gates** (`campaign_gates.py`; FIRED or UNRESOLVED stop with exit 3; resuming needs `--ack-gate ID --ack-audit FILE`, where the audit names the gate id and the decision id):

| Gate | After | Test | Rule |
|---|---|---|---|
| G-S2-04-nominal | S2-04 | hc_nominal \|I_G(−3 V)\| ≤ 1e-2 × floor (2.0 nm floor 4.61e-15 A/µm, MEASURED/derived, design §7) | S2-STOP-NULL |
| G-S2-06-nominal | S2-06 | hc_nominal (13.2 nm floor 6.60e-12 A/µm, MEASURED/derived) | S2-STOP-NULL |
| G-S2-03-anomaly | S2-03 | hc_generation against run_0061; confounded by the carrier count | S2-ANOMALY-CARRIER |
| G-S2-01-generation | S2-02 | hc_generation S2-01 against S2-02, ≤ 1e-20 A/µm | S2-STOP-NULL |

**Every gate will stop (CALCULATED from the frozen code).**
- `censored_upper` (score_register.py:645-654) returns PASS or "below resolution, consistent" only when the resolution is *demonstrated*.
- `hc_nominal` (:782-793) and `gen_core` (:795-831) otherwise return "unresolved …" or "FAIL (PROVISIONAL …)".
- The gate maps these to UNRESOLVED or FIRED (S2_RUNNER_GATES §1).
- A41(d) registers no in-scope ceiling run for S2-04/S2-06 or S2-01/S2-02, and the DOS2 pair does not transfer to the nominal set or to 13.2 nm (A41(c)). So no demonstrated resolution can exist.
- A timed-out S2-01 or S2-02 gives "invalid", which is UNRESOLVED and also stops.
- **Result:** four stops and four audit files are certain. The 18 launches run in up to five invocations.

**Manual stop rules** (plan stop_rules; CAMPAIGN_DESIGN §6 S2):
- A nominal or SRH null result at floor scale means stop and audit KCL, CR.TOLER and the deck.
- Worst-set floor-scale current may be interpreted only after S2-11 agrees within 0.1 dec. **S2-11 failed, so S2-08 floor-scale results cannot be read as explaining the floor.**
- Strip decks must give I(0.7)/I(0.1) = 7.0 ± 0.5. Otherwise "the strip is not ohmic in ATLAS" is the result.

**Sealing.** The plan is state-only (`results/sealed/campaigns`). Console, summary and RUN_INDEX notes carry status only. Scoring follows the register's unsealing order.

### 4.2 Consequences of the QTNLSC mesh non-convergence (S2-11 FAIL)

**Facts** (CALCULATED (ATLAS), `register_scores/hc_mesh_run_0076_run_0067.json`):
- 75 of 76 points resolved in both runs; 73 exceed 0.1 dec.
- Maximum 2.858 dec at V_G = −0.7 V: |I_G| 1.31e-22 → 9.43e-20 A/µm.
- At −3 V: 2.746e-12 → 5.675e-12 A/µm, 0.315 dec.
- In the 7.1 floor window [−2, −0.5] V: 16 points, median |Δ| 0.42 dec (range 0.05–2.86).
- The refined |I_G| is larger at only 21 % of points, so the change is not monotonic in direction.
- No sign changes.

**Consequences under the register:**
1. The H-C prediction "resolved leakage under S2-11 changes by ≤ 0.1 dec" FAILED. It stays recorded and cannot be erased by a later pass (Codex 03:36Z).
2. Physical H-C stays **UNRESOLVED**. Falsification still needs a converged mechanism that passes all four 7.2 criteria.
3. S2-04, S2-06 and S2-08 have other physical settings. S2-11 neither certifies nor formally fails them; their labels stay PROVISIONAL or UNRESOLVED.
4. S2-12/S2-13 inherit QTNLSC (nominal) and also have the separate TAT.SLICEPTS issue (§4.4).
5. **Decision relevance.** The worst-set slope criterion is evaluated over [−2, −0.5] V. That is where the mesh change reaches 0.05–2.86 dec, so the worst-case flatness and thickness-scaling verdicts (hc_worst, hc_explains) are not mesh-robust. This makes the mesh question decision-relevant. Codex's condition for a new series is met in substance, but it needs the amendment of §5.

### 4.3 A41(d) trigger: matched oxide-mesh refinements (≤ 6 launches)

- **When:** after each of S2-04, S2-06 and S2-08 and its control (S0-01, S1-02, S1-02) completes. Run `score_register.py hc_explains <mech> <ctrl>` once, with `--mesh-score` = the registered S2-11 score and no `--resolution*`, before any other output of that run is inspected.
- **TRIGGERED** when either holds:
  - (A) verdict "unresolved (passes all four 7.2 floor criteria" and not converged;
  - (B) verdict "unresolved (insufficient support" and no computable criterion fails (d_floor_ratio within 0.5 dec, |slope| ≤ slope_limit).
- The trigger is binding, with no override. S2-11's FAIL itself triggers nothing (Codex 03:36Z).
- **If triggered:**
  - DOS2 first (timeout ×2), then OXM (timeout ×3). The labels are registered: `c10_s2_04_dos2_2p0`, `c10_s2_04_oxm_2p0`, `c10_s2_06_dos2_13p2`, `c10_s2_06_oxm_13p2`, `c10_s2_08_dos2_13p2`, `c10_s2_08_oxm_13p2`.
  - **Prerequisite:** a scorer amendment limited to REG['hc_mesh'] for these three label pairs and PIN entries, with a new hash, Codex review and freeze. Then its own state-only plan, a pre-launch gate and the user's go per launch.
  - An OOM or failure makes that mechanism's convergence UNRESOLVED, with no repeat.
- **Size and risk:**
  - 13.2 nm OXM is about 117 × 138 ≈ 16.1k nodes (register estimate, CALCULATED).
  - QTNLSC memory at 9,594 nodes was 1.69 GB of 4 GB (S2_PREP §6).
  - Memory at 16.1k nodes is unverified.
- **Expectation (ASSUMED):** given S2-11, an OXM pair is more likely to fail than pass. A triggered pair mainly documents non-convergence.

### 4.4 S2 items not covered by A41

- **Generation (S2-01/02/03):** no mechanism-specific refinement exists. The verdicts stay PROVISIONAL or UNRESOLVED (A41(d)).
  - The timeout risk is in §6.2.
  - The two-carrier continuation (S1-06 repair) must not be silently applied to the S2-01/02/03 decks. Their deck text is registered, so a change needs a logged amendment (numerical, not physics) and a Codex/TCAD check.
- **ITAT (S2-12/13):** TAT.SLICEPTS = 12 (the default) is untested.
  - The 5.28 manual says to choose it so that currents are "largely unchanged" for a slightly higher or lower value (S2_PREP §6, citing PDF p.322 and p.326).
  - Convergence stays UNRESOLVED without an amendment, for example a TAT.SLICEPTS sensitivity launch (1–2).
- **Strips (S2-14..17, STRIP-6p3):**
  - H-B calibration film frozen at 13.2 nm, with the Q_f-on branch.
  - Predictions: ratio 7.0 ± 0.5; floors within 0.5 dec at 6.3 and 2.0 nm.
  - Frozen repeats S6-24..26 come later.
  - No strip deck has ever run (no RUN_INDEX row). Its runtime is ASSUMED.

### 4.5 S3 confinement and AFF (in DIAG)

- **H-E registered bands (A13):**
  - all-off ΔV_th,cc: 2.0 nm −0.13 ± 0.03 V (the original −0.23 ± 0.04 V is also scored); 6.3 nm −0.062 ± 0.015 V; 13.2 nm −0.023 ± 0.008 V;
  - S3-01 − S1-05 = −0.272 ± 0.010 V;
  - AFF-2p0 −281.6 ± 5 mV; AFF-6p3 −62.2 ± 5 mV;
  - the shift must be rigid within ±5 mV, with scoring frozen (A16).
- **Caveat from the crystalline DFT re-derivation** (work chat 2026-10-13T10:23Z; crystalline only, allowed):
  - the 0.75 nm fit3 point comes from a polar slab;
  - a ±0.17 eV vacuum-reference sensitivity (ASSUMED, not a bound) maps to ΔE_c(6.3 nm) 0.053–0.075 eV, against the configured 0.0622 eV (COMPUTED law);
  - AFF-6p3 tests the deck's own ΔE_c, so it is unaffected as a model-consistency check;
  - changing the fit3 law or the S6-01..06 range needs a result-informed amendment (Codex).

### 4.6 H-F set (DIAG_HF: S3-11, S3-12, S3-13, S3-27, S3-10), IGZO and contacts

- **Status:** held (`runnable: false`). Hold reason: "no frozen code scores the H-F predictions yet."
  - S4b/S5 and H-F v4 were frozen on 2026-10-13 at about 09:30Z (commits 484ab8d and 2c8c530, tag `s4s5-hf-v4-429b3a3f-frozen-20261013`, local, not pushed; work chat).
  - The config was generated at about 01:57Z on 13 Oct (file mtime, local UTC+8), before that freeze.
  - **Needed:** regenerate the plan with runnable=true (`make_campaign_configs.py`, `--check`, a Codex check), then the user's go. No register amendment is needed for the five registered entries.
- **S3-27 role.** S3-27 is S3-12 with Q_f +1e12 cm⁻² and MUN ×0.6. It is checked against the transformed S3-12 (≤ 0.01 dec). It serves three purposes:
  1. Design §5.2/S3: the IGZO branch may use exact offline profiling only if S3-27 passes. Otherwise every IGZO S4b candidate runs natively at the profiled values.
  2. Register H-F (A7): native S3-27 confirmation is required "before any branch counts".
  3. H-F v4: D3 (IGZO gain and γ), the D4 contact trigger and the D5 IGZO falsification route accept only a sealed `native_confirmation` record (role S3-27, bound to the digest of the S3-12 run actually used). A missing, timed-out or unevaluable S3-27 makes D3/D4/D5 UNKNOWN or UNRESOLVED. A valid FAIL counts as evaluated but cannot falsify.

  Order consequence: S3-27 must follow S3-12 and must complete within its 2000 s timeout.
- **IGZO activation is UNVERIFIED for `user.material`** (GENERATOR_AUDIT l.50, l.312). The design says the first 6.3 nm launch must show it in the REGIONAL MOBILITY MODEL SUMMARY (post_run_checks activation).
  - The plan order is S3-11 (2.0 nm) first, and `run_campaign.py` continues after a failure.
  - An inactive model would burn S3-11, S3-12, S3-13 and S3-27 (§7, F5).
- **IGZO GAMMA0 +0.30 (S3-14..16).** "Conditional in rev1 and not in the rev2 diagnostic set; only GAMMA0 −0.31 is scored" (H-F draft §8). The design's S3 rule ("the better GAMMA0 seeds S4") needs it. **A Codex ruling is needed:** later-order plan, or an amendment.
- **Contacts (S3-17..23, 7 launches).**
  - Frozen trigger (register H-F; H-F v4 D4): fire only if every one of S1-01, S3-10 and S3-12 (with S3-27) has a 6.3 nm shape RMSE > 0.15 dec. If S3-27 is missing or fails, the trigger is UNRESOLVED.
  - Register order puts contacts at **step 10, after S7**. A fired contact branch therefore cannot be adopted into S4 under the current order, which conflicts with the design's S3 adoption route.
  - H-F v4 D5 has `CONTACT_ROUTE_AVAILABLE = False`: the contact roles and one shared contact model are not registered. Contacts cannot falsify H-F, and with D4 FIRE, D5 is UNRESOLVED.
  - **Amendments needed** if the user wants Schottky as a real S3 branch: (i) contact roles and a shared-barrier contact model; (ii) a placement before S4; (iii) a matrix entry and label for the **Schottky native check** (design: "one reserve launch of the same check"; it has no entry today).
  - The activation of a Schottky contact on IWO is also unproven; check the first launch before the other six.
- **Sealing.**
  - **AFF-6p3 and STRIP-6p3** have not run. They are in DIAG (state-only, so sealed by construction).
  - The work chat (2026-10-13T01:40Z reply; l.4641, 4649, 5095) says they "remain sealed until the [H-F] replacement hashes are frozen". The v4 freeze is recorded, but a logged unsealing decision before reading them is still advisable. This is my reading: **confirm with Codex**.
- **Order (register §3):** IGZO with S3-27 (step 3), then S3-10 (step 4), then tail runs (step 5).

### 4.7 Tail placement (S3-05/06/08/09)

- These are registered later-order entries (step 5) with no runnable plan. They need their own plan file (`make_campaign_configs.py`, `--check`, Codex) before launch.
- S3-04/S3-07 are not needed (§3.2).
- The S3 adoption rule picks the lowest √J of {surface, bulk, 50:50}. "None" (S3-10, 6.3 nm only) is a diagnostic, not a candidate placement.

### 4.8 Kept-out entries the user asked for

| Entry | What it is | Register status | What it takes |
|---|---|---|---|
| S2-09, S2-10 | FNORD worst | kept out ("FNORD duplicates") | logged amendment + own plan labelled exploratory (S2_offfloor hold) |
| S2-05, S2-07 | QTNLSC 6.3 nm, nominal and worst | kept out | the same |
| S3-24, S3-25 | BQP pair | kept out | the same |
| S3-26 | Boltzmann | kept out | the same |

- FNORD has no tunnelling mesh: it uses the field at the Al2O3/IWO segment. After the S2-11 FAIL it is the only leakage formulation in the design that does not depend on the oxide slice mesh. It is still a single-barrier upper estimate (design §7.3).
- Reinstating S2-09/S2-10 as an independent cross-check has a scientific case. That is a result-informed amendment.

### 4.9 S4/S5 gates and open items

- **S4a hazard.** `campaign_C10_S4a_spacefilling.json` is runnable=true now. Its own stop rule says it is valid only if S3 adopted no branch, and S4A-01-* must then be removed (identical to S0-01/S1-01/S1-02).
  - Launching it before DIAG, DIAG_HF, the tails and the S3 adoption decision would break the register order (step 6). It would also waste 3 launches.
  - Recommend holding it (runnable=false) until the S3 adoption is logged. That is a config regeneration with Codex.
  - If a branch is adopted, the candidates must be regenerated (3-D LHS with GAMMA0 if IGZO).
- **S4a abort** (profile_s4s5 v4, frozen): best √J > 0.30 dec AND ≥ 80 % same-sign 6.3 nm on-state error over the complete inventory of 15. Any unknown candidate makes the abort UNRESOLVED (B3). So every S4a candidate must complete; a timeout blocks the abort.
- **S4b:** stops after 3 successive resolved improvements < 0.01 dec, or on optimizer stall (A1). Unused launches return to the reserve.
- **S4c:** the purpose text in `campaign_matrix.json` still says 0.005 dec, while the frozen tolerance is 0.01 dec (H-F draft §9 A10; work chat "S4C edit needed before logging"). **The matrix owner must edit it** (a regenerated matrix, regression and Codex).
- **S5:**
  - branches are re-selected inside each fold;
  - a changed-branch fold needs **amendment A7** (local S3-centred points), logged with the user's go before use (H-F draft §9, §10);
  - the 6.3 nm fold runs first (register §3).
- **S1-06 rule** (design §6 S1): if two carriers change I_D by > 1e-3 relative above 1e-14 A/µm, every later run becomes two-carrier with timeout ×1.5.
  - It is unresolved until the repair runs.
  - Given the S1-06 stall, triggering it would multiply the S4/S5 cost and the timeout risk. **Resolve it before S4a.**
- **3-D NC robustness branch** (register §3): "calibrated separately in S4". There are no matrix entries, labels or plan. It needs registration of entries (no new physics: the S1-05 `nc_mode 3d` form) and Codex review (§7, F3).

---

## 5. Tunnelling-mesh convergence branch (user request 2026-10-14; `00_user_request_tunnelling_mesh.md`)

### 5.1 Manual basis (verified in this audit)

- **5.28 text** (`report_latex_full/tools/atlas_manual_pages.txt`):
  - l.13505-13507: T(E) by a transfer matrix on "a stepwise approximation of the potential", so "a fine mesh in the tunnelling direction" is recommended.
  - l.13660-13676 (PDF p.302 "Mesh Considerations"):
    - the model is quasi-1D on slices through the insulator;
    - for an Atlas-built mesh "everything including the direction of tunneling is determined automatically", with slices locally perpendicular to each semiconductor-oxide segment (SHAPEOX is the alternative);
    - QTX.MESH/QTY.MESH are the stated option for Athena/DevEdit meshes; the QT mesh must "enclose the insulator and … not overextend"; tunnelling is along y by default (QTUNN.DIR 0); Table 3-130 lists NODE, LOCATION, X, RATIO, SPACING.
  - l.13633-13646: QTNLSC.EL and QTNL.DERIVS (extra Jacobian terms; more time per iteration).
  - l.13700-13704: carriers are booked to the electrode they flow into; NEARFLG and EXCLUDE_NEAR.
- **2004 text** (`atlas_user_manual_740p.txt`):
  - l.8728-8757: the QTX/QTY mesh is for Athena/DevEdit meshes, in y unless QTUNN.DIR = 1; it is unnecessary for a semi-classical simulation on a general mesh.
  - l.27757: QTUNN.DIR is used only with a QTX/QTY mesh.
- **Codex 03:36Z, before any further refinement:** check the actual oxide intervals and interface coordinates, not only the factors (the present ×0.5 refines Al2O3 about ×1.5 and HfO2 about ×2, and keeps y = 0); QTNLSC.EL and QTNL.DERIVS; unchanged masses and barriers; S/D EXCLUDE_NEAR; slice allocation; signed currents; KCL.
  - A dry build plus a structure-file interval count of the new deck costs **no launch**.

### 5.2 Options, cost and risk

**T1. Automatic slicing (self-consistent, KCL-closing; decision-grade).** Bounded per Codex: "one further refinement, then one conditional refinement if needed and feasible" (2 launches).
- **T1a** `oxide_mesh_factor=0.25`: an existing option; `build_iwo_decks.py:190-192` accepts 0 < f ≤ 1, so no code change.
  - Same non-uniformity as S2-11 (y = 0 kept).
  - Size (CALCULATED, ASSUMED geometric grading from S2_PREP §6: oxide intervals 43 → ~77 at ×0.5 → ~145 at ×0.25): y lines ≈ 82 + 102 = 184, so about 117 × 184 ≈ 21.5k nodes.
  - Memory (ASSUMED linear in nodes from 1.69 GB at 9,594): about 3.8 GB against the 4 GB LAA limit. **High OOM risk.** OOM shows within seconds (run_0062: 14.2 s), so it is a cheap failure, but it spends a launch.
  - Time (ASSUMED exponent 1.27 from the non-QTNLSC mesh pair: 1786.5/735.4 s for 24,255/12,051 nodes, ln 2.43 / ln 2.01): 1246 s × 2.24^1.27 ≈ 3,470 s, about 1.0 h. Timeout 7,200 s suggested.
- **T1b** a uniform-oxide variant (Codex's unequal-refinement concern), for example Al2O3 and HfO2 spacings halved together *including* a refined y = 0 interface line.
  - It needs a new generator option, regression "unexpected differences 0", and Codex plus a manual check.
  - Halving the y = 0 line also regrades the IWO interface mesh, which mixes two effects (S2_PREP §6). That is a reason to keep T1a as the primary form.
- **Scoring:** the frozen `hc_mesh` can score a ×0.25 vs ×0.5 pair (deck ratio 0.5) only after a scorer REG/PIN amendment registers the new label pair, as in A41(d).
- **T1 claims:**
  - PASS (≤ 0.1 dec on ≥ 3 resolved points, full coverage): "QTNLSC I_G at 2.0 nm, worst set, stable under a further ×0.5 oxide refinement at the ×0.5 level". Scope is that film and oxide set only (A41 scope rule). It does not erase the S2-11 FAIL.
  - FAIL: "QTNLSC not demonstrably convergent within the feasible 32-bit mesh". I_G is reported as a mesh-dependent range; H-C leakage rests on the CALCULATED bounds (`leakage_bounds.py`) and any independent formulation (FNORD, if reinstated).
  - OOM: UNRESOLVED, with no factor change (the A41(d) precedent).

**T2. Rectangular QT mesh** (`qt_mesh=1`, `qt_slice_um`, `qt_point_nm`; existing options, the run_0063..0066 form). Not self-consistent: run_0066 booked the tunnel current to the electrodes only, its DD currents were bit-identical to run_0061/0065, and KCL failed.
- It is a **magnitude cross-check only.**
- **The coarse level already exists:** run_0066 (0.2 µm, 0.5 nm). So T2 costs 2 launches, not 3:
  - (0.2 µm, 0.25 nm): QT grid 121 × 71 = 8,591 points;
  - (0.1 µm, 0.25 nm): 241 × 71 = 17,111 points;
  - against 121 × 37 = 4,477 for run_0066 (CALCULATED: a 24 µm oxide span in x; in y the 17 nm stack plus one point spacing of overhang on each side, `build_iwo_decks.py:419-428`).
- Memory is unverified (QT points add to the 9,594 device nodes).
- Time: about 600–1,200 s each (ASSUMED, from run_0066's 588.6 s).
- The frozen scorer cannot score these (a KCL failure is invalid). A new diagnostic comparison script is needed (Codex check). These are never registered tests.
- **T2 claims:** convergence or non-convergence of the post-processed (non-coupled) I_G magnitude on a QT mesh, and agreement in order of magnitude with T1. It can never qualify or fail H-C.

### 5.3 Amendment, budget and order

- **Amendment:** result-informed (after the S2-11 FAIL; run_0076 was viewed by the user, so not blind). It needs:
  - entries and labels (for example `c10_s2_11_oxm2_2p0`, `c10_s0_02_qtm2_2p0`, `c10_s0_02_qtm3_2p0`);
  - the scorer REG/PIN lines for T1;
  - a T2 diagnostic script;
  - OOM → UNRESOLVED;
  - no repeat;
  - Codex review plus the manual check (TCAD check rule);
  - the user's go per launch.
- **Budget:** T1 1 + 1 conditional, T2 2 → 2–4 launches. Matrix reserve 9 → 5–7 (or −1 to 1 if all six A41(d) triggers run). That is only covered by the kept-out headroom of §3.3.
- **Wall time:** T1 about 2 × 1.0 h; T2 about 2 × 0.25 h, so about 2.5 h typical; timeout bound about 5 h (CALCULATED from the estimates above).
- **Order:** after the DIAG QTNLSC mechanism runs have their first `hc_explains` (the A41(d) screen), so that the mesh series answers a decision-relevant question. Before any S2-08 interpretation. Independent of S3/S4.

---

## 6. Cost model

### 6.1 Measured runtimes per film and model (MEASURED runtime, RUN_INDEX; ratios CALCULATED)

| Case | Run | Nodes (`deckbuild.out`) | Wall s | Ratio |
|---|---|---:|---:|---|
| 2.0 nm baseline | run_0061 | 9,594 | 395.8 | 1 |
| 2.0 nm 3-D NC | run_0072 | 9,594 | 295.7 | 0.75 |
| 2.0 nm Q_f/MUN check | run_0074 | 9,594 | 310.3 | 0.78 |
| 2.0 nm DOS ×2 | run_0071 | 9,594 | 476.8 | 1.20 |
| 6.3 nm baseline | run_0068 | 10,179 | 493.7 | — |
| 13.2 nm baseline | run_0069 | 12,051 | 735.4 | — |
| 13.2 nm mesh ×0.7 | run_0070 | 24,255 | 1786.5 | 2.43 vs run_0069 |
| 2.0 nm QTNLSC worst (automatic slicing) | run_0067 | 9,594 | 1246.0 | **3.148** vs run_0061 |
| 2.0 nm QTNLSC + oxide ×0.5 | run_0075 | ~13.7k | ~1635 to exports | 1.31 vs run_0067 (CALCULATED from register A41(b): start 14:53:22Z, exports by 15:20:37Z; no output opened) |
| same, rerun | run_0076 | — | 2172.4 | includes a probable viewer wait (ASSUMED, work chat) |
| 2.0 nm QTNLSC DOS ×2 | run_0077 | — | 1783.5 | 1.43 (upper; viewer wait not excluded) |
| 2.0 nm QT-mesh form | run_0066 | 9,594 + QT | 588.6 | — |
| 13.2 nm two carriers | run_0073 | 12,051 | **> 3600 (timeout)** | — |

- Per-bias-point sums (ATLAS "Time for bias point"; CALCULATED): run_0061 303 s of 395.8 s; run_0067 1165 s of 1246 s; run_0069 632 s of 735.4 s.
- About 77–94 % of the wall time is the 113 bias solutions (303/395.8, 632/735.4, 1165/1246); the rest is mesh, init and exports.
- Standard DOS triple (2.0 + 6.3 + 13.2 nm) = 1,624.9 s = 0.451 h (CALCULATED).

### 6.2 Why S1-06 timed out (decisive for S2-01/02/03)

From run_0073 `deckbuild.out` (CALCULATED from its printed totals):
- The run reached V_G = −1.8 V at 5.16 min.
- The next printed total is 53.72 min. That is **48.6 min of non-converging retries between −1.8 and −1.6 V** in the strict-acceptance depletion block (`cr.toler` strict, `xandrnorm`, carriers=2): 22 × "Newton algorithm did not converge in 80 iterations", 20 × "Taking smaller bias step", 2 × "Bias step cut back more than 10 times".
- ATLAS then continued from −1.75 V under the on-state acceptance, at about 6.4 s per point, and was killed at V_G = 1.1 V.
- 65 of 76 points were exported (run_0069: 76). The per-point sum is only 617 s of 3,600 s.
- So the cost is a depletion-window convergence stall, not slow solving.
- **S2-01 and S2-02** (13.2 nm, carriers=2, 3600 s, extreme or suppressed SRH) are expected to hit the same stall and time out → invalid, gate UNRESOLVED (ASSUMED from the precedent).
- **S2-03** (2.0 nm, carriers=2, 1800 s) has no precedent.

### 6.3 Stage estimates

- Typical = measured base × the factors above.
- New-physics factors are ASSUMED: IGZO ×1.15; Schottky ×1.35; BQP ×1.75; ITAT ×1.3 on QTNLSC; strip decks 300 s; S1-06 repair about 1 h.
- Upper = the sum of the entry timeouts in the matrix.
- All in hours (CALCULATED).

| Stage | Launches | Typical h | Timeout-sum h | Notes |
|---|---:|---:|---:|---|
| DIAG S2 (13 new) | 13 | 5.58 | 8.25 | includes S2-01/02 at 3600 s each (expected timeouts) |
| DIAG S3 + AFF | 5 | 0.70 | 2.17 | |
| DIAG_HF | 5 | 0.81 | 2.83 | |
| Tails S3-05/06/08/09 | 4 | 0.68 | 2.17 | |
| IGZO +0.30 S3-14..16 | 3 | 0.52 | 1.86 | ruling needed |
| Contacts S3-17..23 | 7 | 1.40 | 4.83 | trigger-gated |
| Schottky native check | 1 | 0.19 | 0.61 | needs an entry |
| S4a | 45 (42) | 6.77 (6.32) | 27.9 (26.1) | IGZO adopted: about 7.8 |
| S4b | 0–18 | 0–2.71 | 0–11.2 | abort or early stop |
| S4c / S4d | 3 / 3 | 0.45 / 0.45 | 1.86 / 1.86 | |
| S5 | 30 | 4.51 | 18.6 | folds 1.59 / 1.53 / 1.40 h |
| 3-D NC branch (2.0 nm only) | 15–16 | 1.65–1.76 | 6.7–7.1 | unbudgeted, §4.9 |
| S1-06 repair | 1 | ~1.0 | ~1.5 | ASSUMED |
| A41(d) refinements | ≤ 6 | 4.47 | 12.5 | DOS2 ×1.43, OXM ×1.31 of each mechanism |
| Tunnelling mesh T1 + T2 | 2–4 | ~2.4 | ~5.0 | §5 |
| Kept-out 7 (if amended) | 7 | 2.35 | 4.06 | |
| S6 | 12–22 | 1.60–3.10 | 6.3–12.5 | |
| S7 | 2 | 0.50 | 1.67 | |

**Totals (CALCULATED):**
- Lean path (138 launches): about **24.8 h** typical; about 82 h timeout-sum.
- Full register path (186 launches): about **36 h** typical; about 122 h timeout-sum.
- Design reference: 43 h typical for its 181 launches, 112 h timeout-sum (CAMPAIGN_DESIGN §1).
- Human audit time at the four DIAG gates and between stages comes on top.

---

## 7. Savings

### 7.1 Already in the design or register

- **Exact profiling of ΔV₀, μ∞ and ℓ** (69 instead of 84 calibration launches, D5). The S1-07 profiling check passed (2.05e-4 dec).
- **S4A-01 reuse** if no branch is adopted (3 launches).
- **S4a abort / S4b skip** (18).
- **S4b early stop** (up to 9).
- **S5 sharing the S4a archive** (30 instead of 36, D6).
- **S6 early exit** (27 → 10).
- **Kept-out entries** (14).
- **A41:** one rerun, one DOS2 run, and a triggered (not automatic) refinement ceiling of 6.

### 7.2 Further savings that do not change registered physics (each needs only what is stated)

| # | Saving | Gain | What it needs |
|---|---|---|---|
| F1 | Never run S3-04/S3-07. Prove the redundancy by dry-build deck-text hash equality with run_0061 (deck_sha256 d2fd986f…) | 2 launches (confirm) | dry build only |
| F2 | Extend S4A-01 reuse to a *single* adopted branch already run at the start parameters in S3: IGZO −0.31 = S3-11/12/13; bulk tail = S0-01/S3-05/S3-06; 50:50 = S0-01/S3-08/S3-09 | 3 launches, 0.45 h | the design text covers only "no branch": a logged procedural note + deck-hash equality + Codex |
| F3 | 3-D NC robustness branch: launch only the 2.0 nm member of each S4a candidate. The 6.3/13.2 nm decks are identical in both NC branches (the NC override is keyed to 2.0 nm only, `profile_s4s5.FILM_KEYED`) | about 30 launches, about 5.5 h, against a naive 45-launch branch | entry registration + Codex (needed anyway: unbudgeted) |
| F4 | **S1-06 continuation repair first** (register-allowed, 1 launch, Codex check). Then decide by amendment whether the same continuation goes into S2-01/02/03. Resolve the S1 two-carrier rule before S4a | avoids about 2 likely invalid 3600 s launches (S2-01/02) and the risk that every later run becomes two-carrier at ×1.5 timeouts | Codex ruling on placement before DIAG's generation runs; an amendment for the S2 decks |
| F5 | **Activation-first ordering for new physics.** Split DIAG_HF so that S3-12 (6.3 nm, the design's activation launch) runs alone, then S3-27, then S3-11/13/10. The same pattern applies to the first Schottky and BQP launch | up to 3–4 launches and about 1 h if IGZO.TOKYO is inactive for `user.material` | plan regeneration + `--check` + Codex; no physics change |
| F6 | Prepare the four DIAG gate audit templates in advance (the stops are certain, §4.1) | wall-clock only | none |
| F7 | Viewer discipline: no DeckBuild GUI clicks during launches. A TonyPlot window holds DeckBuild until the timeout: run_0075 was killed at 5400 s; run_0076 shows 2172 s wall against about 1635 s of compute for the same deck | avoids a full timeout and an invalid run per incident | procedure (kill mode still needs the supervised test, D4) |
| F8 | Dry-build interval counts before T1/T2 (Codex 03:36Z) and an OOM pre-assessment | avoids a predictable OOM launch | none |
| F9 | Hold S4a (runnable=false) until the S3 adoption is logged | prevents 3 redundant launches and an out-of-order start | config regeneration + Codex |

**Not legitimate (they would change registered rules):**
- skipping a DIAG entry;
- stopping S4a before the 15-candidate inventory;
- changing timeouts or tolerances of registered decks without an amendment;
- reading sealed outputs to decide the order.

---

## 8. What is launchable now, in the register order

1. **`campaign_C10_DIAG`** (18 new launches). Needs the pre-launch checks and the user's go. Expect four gate stops with audits. Recommended *before* it, subject to a Codex ruling: the S1-06 repair (F4).
2. Then, each after its own preparation:
   - DIAG_HF (needs regeneration after the v4 freeze; activation-first split F5);
   - the tail plan;
   - the IGZO +0.30 ruling;
   - the H-F D4 trigger evaluation;
   - the S3 adoption;
   - S4a (regenerated if a branch is adopted; F2/F3);
   - S4b/S4c/S4d (S4C text fix);
   - S5 (A7 amendment if a fold changes branch);
   - S6 targeted (S6-13, S6-15);
   - S7;
   - conditional: contacts (amendments in §4.6), N1, N2.
3. In parallel, as amendments to draft (no launch until logged, Codex-reviewed and approved by the user):
   - the tunnelling-mesh branch (§5);
   - the S1-06 continuation for the S2 two-carrier decks;
   - TAT.SLICEPTS;
   - kept-out FNORD/BQP/Boltzmann/S2-05/07 if wanted (exploratory);
   - the 3-D NC branch entries;
   - the Schottky native-check entry and contact roles;
   - the A41(d) scorer REG/PIN amendment (only once a trigger fires).

## 9. Sources

**Public repo:**
- `analysis_2026-10-10_campaign/CAMPAIGN_DESIGN.md` (full);
- `analysis_2026-10-10_campaign/campaign_matrix.json` (185 entries);
- `results/RUN_INDEX.csv` (rows 122-155);
- `config/campaign_C10_*.json`;
- `config/solver.yaml`;
- `config/physics_options.yaml` l.42-78;
- `scripts/build_iwo_decks.py` l.190-226, l.300-311, l.415-428;
- `analysis_2026-10-10_campaign/score_register.py` l.429-454, 642-654, 782-850;
- `analysis_2026-10-10_campaign/profile_s4s5.py` (rules grep);
- `analysis_2026-10-10_campaign/HF_DEFINITIONS_DRAFT_2026-10-13.md`;
- `analysis_2026-10-10_campaign/S2_RUNNER_GATES_2026-10-13.md`;
- `analysis_2026-10-10_campaign/S2_PREP.md` §5-6;
- `analysis_2026-10-10_campaign/GENERATOR_AUDIT.md` l.46-50, 298-315;
- `analysis_2026-10-10_campaign/register_scores/hc_mesh_run_0076_run_0067.json`;
- `analysis_2026-10-10_campaign/register_scores/smoke_resolution_pair_run_0077_run_0067.json`;
- runs run_0061 to run_0074 (`execution.json`, `deckbuild.out`).

**Private repo:**
- `private:codex/work_chat/HYPOTHESIS_REGISTER.md` l.1-303 (§0, H-A to H-J), l.1568-1975 (A41), l.2146-2300 (§3, §4, amendment table);
- `private:codex/work_chat/CODEX_WORK_CHAT.md`, entries 2026-10-12T13:18Z, 2026-10-13T01:40Z reply, 03:36Z, 03:40Z, ~09:30Z note, 10:23Z.

**Manuals:**
- ATLAS 5.28 text l.13500-13510, 13630-13725 (authority);
- 2004 manual l.8728-8758, 27750-27760.
