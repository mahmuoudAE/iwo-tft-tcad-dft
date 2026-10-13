# H-F operational definitions: DRAFT v3, 2026-10-13 (not frozen)

**Status: DRAFT.** These definitions are not frozen, and nothing here is a registered score. They may be used for scoring only after the user freezes them by a logged entry (work-chat entry or register amendment), after a Codex review and a manual check under the TCAD check rule. Until then `config/campaign_C10_DIAG_HF.json` stays held (`runnable=false`).

**What changed since v1.** Codex reviewed v1 on 2026-10-13 (~01:55Z): "NO to freezing the current profiling/H-F code. GO-WITH-CHANGES on the definitions." This v2:
- encodes Codex's rulings on the drafter's choices 1-5 (each marked **Codex ruling 2026-10-13** below);
- implements blocking fix B4: no falsification from an unqualified profile, and a missing prescribed branch leaves the assessment UNRESOLVED;
- depends on the revised `profile_s4s5.py` (blocking fixes B1-B3 and B5, rulings A1-A10; see §9).

**What changed in v3.** Codex reviewed v2 on 2026-10-13 (~03:10Z): FIX_FIRST, do not freeze the v2 hashes. This v3:
- **v2 fix 3:** a native confirmation counts only as a sealed `profile_s4s5.native_confirmation` record. That record wraps the unchanged `profile_shared.check` with:
  - both endpoints' eligibility;
  - the designated roles: S3-27 against S3-12, S1-07 against S0-01;
  - both run digests.
  H-F accepts the record only for its own role and for the reference run actually used. A raw check dict, a timed-out endpoint, or an S1-07 PASS offered for S3-27 confirms nothing.
- **v2 fix 4:** every D1-D5 input is checked against its designated run (label and film; the baseline also against the start parameters). S1-02's 13.2 nm curve can no longer stand in for S1-01 at 6.3 nm.
- **Ruling (e):** a valid evaluated confirmation FAIL counts as evaluated and cannot falsify. A missing, timed-out or unevaluable confirmation is UNKNOWN.
- The profiling side fixes (v2 fixes 1-2) and rulings (a)-(d), (f) are in `profile_s4s5.py` (§9).

**Scope.** The four pieces that `S2_PREP.md` §6 (l.167-173) lists as missing for H-F, plus the falsification clause they feed:
- the two-film reference;
- the baseline shape RMSE;
- the IGZO gain and the γ targets;
- the frozen S3-17..S3-23 contact trigger.

**What was done to write it:**
- Nothing was launched or committed. The register (`iwo-tft-research-private/codex/work_chat/HYPOTHESIS_REGISTER.md`, tag `register-rev2-frozen-20261010T1833Z`) was read only.
- **No H-F quantity was computed on any run.** No real 2.0 + 13.2 nm profile, nothing against the measured 6.3 nm curve, no S4/S5 result. All H-F tests use synthetic curves. `results/sealed/` and run_0075 were not opened.

**Drafter's disclosure (what I had seen while drafting):**
- the register §0 headline numbers for S1-01 (active RMSE 1.18 dec; I_D(3 V) ×4.87);
- the V2 profiling result in `IMPLEMENTATION.md` §11.7: the V2 triple's 6.3 nm shape-only residual was 0.036 dec at a free shift of +0.24 V. That is a different model (V2, not the C10 baseline), but it uses the same metric as the shape RMSE below.

D1 and D2 results carry this disclosure in their output (`disclosure`).

**Code** (all uncommitted drafts):
- `analysis_2026-10-10_campaign/hf_score_draft.py`: functions only; the only CLI command is `selftest`. Every result carries `status = DRAFT (...)`, the register tag and the rulings note.
- `test_hf_score_draft.py`: 46/46 on synthetic curves:
  - 5 regression cases for B4 and ruling 4;
  - 7 regression cases for v2 fixes 3-4.
- The profiling comes from `profile_s4s5.py`: `profile_films`, `adopt_films`, `acceptance`, `transformed_points`, `qualification`, `at_start`, `native_confirmation`, `confirmation_status`, `run_digest`.

**Roles (v2 fix 4)** — the campaign matrix labels:

| Role | Label | Film |
|---|---|---|
| S0-01 | `c10_s0_01_2p0` | 2.0 nm |
| S1-01 | `c10_s1_01_6p3` | 6.3 nm |
| S1-02 | `c10_s1_02_13p2` | 13.2 nm |
| S3-10 | `c10_s3_10_6p3` | 6.3 nm |
| S3-11 | `c10_s3_11_2p0` | 2.0 nm |
| S3-12 | `c10_s3_12_6p3` | 6.3 nm |
| S3-13 | `c10_s3_13_13p2` | 13.2 nm |

Confirmation endpoints:
- S1-07 (`c10_s1_07_2p0`) against S0-01;
- S3-27 (`c10_s3_27_6p3`) against S3-12.
- Hashes are listed in §10.

## 0. Sources

| Item | Where |
|---|---|
| H-F test list | Register l.239-242: "S3-10 to S3-13, with **native confirmation S3-27 required** before any branch counts"; "Contacts S3-17 to S3-23 are conditional. **Trigger, frozen now:** run them only if the 6.3 nm shape RMSE stays > 0.15 dec after S3-10 to S3-13"; "The S5 fold that leaves out 6.3 nm." |
| H-F predictions | Register l.243-246 (quoted in each section below) |
| H-F falsification | Register l.247: "Falsified if the baseline passes, or any natively confirmed branch passes §5.3 for all three films." |
| Origin of the numbers | Register rev1 (`HYPOTHESIS_REGISTER_rev1.md`) l.129-132 |
| Codex's original H06 | `CODEX_WORK_CHAT.md` l.237: observable "residual after diagnostic free shift/scale, γ and g_m" (the frozen l.247 text governs) |
| Shape decomposition | `CAMPAIGN_DESIGN.md` l.244: "per-film free shift and scale give the shape-only residual"; matrix S3-10: "Shape compared after profiling shift and scale" |
| Windows, transformations, acceptance, adoption | `CAMPAIGN_DESIGN.md` §5.1, §5.2, §5.3, S3 rule (l.308-322) |
| Codex review of v1 | 2026-10-13 ~01:55Z: blocking fixes B1-B5, rulings A1-A10 and on H-F choices 1-5 |

## 1. Common building block: the 6.3 nm shape RMSE (`shape_fit`)

**Codex ruling 2026-10-13 (choice 1).** The shape RMSE is the equal-window √J after a free shift and scale. It is computed by grid plus refinement over ±0.5 V and needs ≥ 95 % coverage. Bound hits are UNRESOLVED. "Baseline" means S1-01 at the start parameters.

**Definition.** The shape RMSE of one film is the square root of the film's J term, (RMSE²_sub + RMSE²_on)/2. It uses the CAMPAIGN_DESIGN §5.1 windows on the measured grid:
- sub: measured I_D in [10 × floor, 1e-9 A/µm];
- on: V_G 1..3 V.

The simulated curve is transformed with the best rigid shift dV and current scale s, I(V) → s·I(V − dV).

**Computation:**
- the exact transformation of `profile_shared.transformed_log` (PCHIP of log I, no extrapolation);
- the scale in closed form for each dV;
- dV on a 5 mV grid over ±0.5 V, then a bounded scalar refinement. The search is global within the bound and deterministic.

**Validity (else UNRESOLVED):**
- the run must be eligible (B1: completed, complete finite export);
- the optimum must not sit at the ±0.5 V bound;
- both windows need ≥ 95 % coverage at the optimum.

**Reported, not scored:**
- the near-optimal dV and s ranges (grid shifts within 0.01 dec of the minimum);
- the runner's active log-RMSE of the same shifted and scaled curve.

## 2. D1: two-film reference (`two_film_reference`)

**Register l.244:** "Two-film reference: 6.3 nm needs a rigid shift of +0.28 ± 0.08 V and a current scale of 0.15 to 0.35."

**Codex ruling 2026-10-13 (choice 2).**
- The training pair is the quasi-2D S0-01 plus S1-02.
- The extra profiled shift and scale are scored separately and jointly.
- The direct V_th difference is diagnostic only.
- The optimum is scored, and the degeneracy ranges are reported.

**Definition:**
1. S0-01 (2.0 nm, run_0061, with the quasi-2D `nc300_override_cm3[2.0]`) and S1-02 (13.2 nm, run_0069) are profiled with `profile_s4s5.profile_films` for the shared (ΔV₀ via one Q_f, μ∞, ℓ).
   - The 2.0 nm run without the quasi-2D NC (the 3-D NC S1-05) is refused.
   - All three runs must be at the S1-01 start parameters (`at_start`).
2. The two-film model at 6.3 nm is S1-01 (run_0068), moved by the shared ΔV₀ and scaled by μ_law(6.3)/μ_band(S1-01).
3. The needed shift dV_n and scale s_n are the extra rigid shift and scale on top of that prediction that minimise the 6.3 nm J term: dV_n = dV_free − ΔV₀(two-film) and s_n = s_free / s_law.
4. Sign: dV_n > 0 means the predicted 6.3 nm curve must move to more positive V_G (its V_th,cc is too low).

**Three scored statements** (`scored`), at the optimum, both edges inclusive:
- shift: 0.20 ≤ dV_n ≤ 0.36 V;
- scale: 0.15 ≤ s_n ≤ 0.35;
- joint: PASS iff both PASS.

`verdict` is the joint statement.

**UNRESOLVED if:**
- the two-film training profile is not qualified: not valid (coverage / optimizer), or a profiled value at a range bound;
- or the 6.3 nm free fit is not valid.

**Reported, not scored:**
- the degeneracy ranges of dV_n and s_n;
- the two-film prediction's own 6.3 nm J term (H-J reporting rule, register l.302);
- the direct V_th,cc difference, labelled DIAGNOSTIC.
  - On the synthetic family, a rigid +0.28 V anomaly with ×0.25 scale gives a direct difference of +0.42 V. That is why it is not scored.

## 3. D2: baseline shape RMSE (`baseline_shape`)

**Register l.245:** "Baseline shape RMSE > 0.15 dec."

**Codex ruling 2026-10-13 (choice 1).** "Baseline" is S1-01 at the start parameters.

**Codex v2 fix 4 (2026-10-13).** The input must be the S1-01 run at 6.3 nm, checked by label and film. Any other run is refused, including S1-02 at 13.2 nm.

**Definition.** The §1 shape RMSE of S1-01 (run_0068, checked by `at_start`) against the measured 6.3 nm curve:
- > 0.15 dec: PASS;
- ≤ 0.15 dec: FAIL;
- invalid fit: UNRESOLVED.

## 4. D3: IGZO.TOKYO gain and γ targets (`igzo_prediction`)

**Register l.246:** "IGZO.TOKYO improves 6.3 nm by ≥ 0.05 dec and moves γ toward 0.9 to 1.3, and gives γ ≥ 0.5 at 13.2 nm (measured 0.27). It is therefore not adopted under the rule that no film may get worse."

**Codex ruling 2026-10-13 (choice 3).**
- The shape gain is primary.
- "Toward" means a reduced distance to [0.9, 1.3], or remaining inside if already inside.
- γ is the native γ; failed or bound fits are unresolved.
- The no-worse forecast requires actual worsening, not insufficient gain alone.

**Runs.** S3-11, S3-12 and S3-13 (start parameters, IGZO.TOKYO GAMMA0 −0.31), against S0-01, S1-01 and S1-02 (start parameters). Both sets are checked by `at_start`; another seed is refused.

**Gate (register l.240; v2 fix 3).** Every part is UNRESOLVED unless a sealed `native_confirmation` record exists that:
- has role S3-27 (endpoints `c10_s3_27_6p3` and `c10_s3_12_6p3`);
- has both endpoints eligible;
- has a reference digest equal to the digest of the S3-12 run passed in;
- says PASS.

The following never open the gate:
- a raw check dict;
- a timed-out endpoint (UNKNOWN);
- an S1-07 record;
- a record bound to another S3-12.

**Parts:**
- **a) Primary.** Shape RMSE(S1-01) − shape RMSE(S3-12) ≥ 0.05 dec.
  - The 6.3 nm √(J term) gain in the three-film shared profiles is reported only.
- **b) Toward the band.** Uses the native power-law γ: `extraction.pl_fit` over V_G 1..3 V on the measured grid, from the native curve.
  - If γ(S1-01) is outside [0.9, 1.3]: PASS iff |γ(S3-12) − band| < |γ(S1-01) − band|.
  - If γ(S1-01) is inside: PASS iff γ(S3-12) stays inside.
  - A failed or V_T-bound fit of either run gives UNRESOLVED.
  - Strict "inside the band" is reported as a diagnostic.
- **c) γ at 13.2 nm.** Native γ(S3-13) ≥ 0.5. A failed or bound fit gives UNRESOLVED.
- **d) Not adopted.** Uses the S3 adoption arithmetic on the three profiled triples.
  - PASS only with an actual worsening: some film's RMSE_sub or RMSE_on worse by > 0.03 dec.
  - FAIL if IGZO passes the arithmetic, or if it is not adopted through the gain clause only.
  - UNRESOLVED if either adoption profile is not qualified.

**Verdict.** D3 PASS iff a, b, c and d all PASS. Any FAIL gives FAIL; otherwise UNRESOLVED.

## 5. D4: contact trigger (`contact_trigger`)

**Register l.241:** "run them only if the 6.3 nm shape RMSE stays > 0.15 dec after S3-10 to S3-13."

**Codex ruling 2026-10-13 (choice 4).** Reading A, with exactly the prescribed roles. Missing or unconfirmed IGZO makes the trigger UNRESOLVED.

**Definition.** The input is exactly the roles S1-01, S3-10 (no tail) and S3-12 (IGZO). Each role is a valid §1 shape fit at 6.3 nm of the role's run: label and digest are required (v2 fix 4). S3-12 counts only with the sealed S3-27 record bound to that S3-12 digest (v2 fix 3).
- FIRE (launch S3-17..S3-23) iff every value is > 0.15 dec.
- DO NOT FIRE if one is ≤ 0.15 dec (a value of exactly 0.15 does not fire).

**UNRESOLVED if:**
- the S3-27 confirmation is failed, missing, UNKNOWN, unsealed, of another role, or bound to another S3-12. S3-12 is never silently dropped (v1 dropped it);
- a role is missing or extra;
- a fit is invalid or comes from the wrong run.

The v1 alternative reading B (the adopted model) was removed.

## 6. D5: falsification (`falsification`, helpers `profiled_triple_acceptance`, `prescribed_branches`)

**Register l.247:** "Falsified if the baseline passes, or any natively confirmed branch passes §5.3 for all three films."

**Codex ruling 2026-10-13 (choice 4).** Either valid baseline shape acceptance or valid all-film §5.3 acceptance is retained as a falsification route.

**Codex blocking fix B4 (2026-10-13).** Valid, qualified profiles are required before falsification. A missing prescribed branch leaves the complete assessment UNRESOLVED.

**Codex ruling 2026-10-13 (e) and v2 fixes 3-4.**
- A valid evaluated confirmation FAIL counts as evaluated and cannot falsify.
- A missing, timed-out or unevaluable confirmation is UNKNOWN.
- A decisive qualified falsification can stand on its own.
- A complete NOT FALSIFIED requires the prescribed inventory.
- Every route checks role identity: the shape route needs the S1-01 6.3 nm fit; the triples need their kind's runs (baseline S0-01/S1-01/S1-02, IGZO S3-11/12/13).

**Routes.** Any route that fires gives FALSIFIED:
- **(i) Baseline shape route.** A *valid* baseline shape fit (D2) with shape RMSE ≤ 0.15 dec, i.e. no shape residual.
- **(ii) Baseline §5.3 route.** A *qualified* baseline triple passes every §5.3 criterion at all three films. Qualified means:
  - the shared profile is valid (coverage ≥ 95 %, optimizer converged);
  - it is OK, not APPROXIMATE;
  - no profiled value is at a range bound;
  - the transformation is natively confirmed: a sealed S1-07 record bound to the S0-01 run of the triple, PASS.
  `profiled_triple_acceptance` replaces every film's verdict with "unresolved (profile not qualified …)" when any condition fails. The computed criteria are kept only as `diagnostic_acceptance_unqualified`. `falsification` recomputes the qualification from the embedded profile; it never trusts a flag.
- **(iii) Branch route.** The route is chosen by the registered branch name first (v4, Codex v3 fix 1):
  - IGZO: only a qualified S3-11/12/13 triple (`profiled_triple_acceptance(kind='IGZO')`) with a sealed S3-27 record bound to its S3-12. A valid S3-27 FAIL means evaluated, cannot falsify; a missing or UNKNOWN one means UNKNOWN. A native route attached to the IGZO name is refused (UNKNOWN).
  - Contacts: **route unavailable** (`CONTACT_ROUTE_AVAILABLE = False`; Codex v3 ruling ii). The contact run roles and one shared contact model are not registered, so the row is UNKNOWN and cannot falsify; with D4 FIRE, D5 is UNRESOLVED. The native-5.3 code path is kept but unreachable until those are registered.
  - Any other branch name: no route (UNKNOWN).

**Prescribed branches** (`prescribed_branches(contact_trigger)`):
- IGZO.TOKYO always;
- contacts (S3-17..S3-23) iff D4 FIRE;
- unknown (`None`) if D4 is UNRESOLVED.

**Verdict:**
- FALSIFIED if any route fires.
- Otherwise UNRESOLVED if any of these holds:
  - the prescribed set is unknown;
  - a prescribed branch is missing;
  - a prescribed branch has no native confirmation result (`None`);
  - a prescribed branch is not evaluable;
  - a baseline route is unresolved.
- Otherwise NOT FALSIFIED.

**Further rules:**
- A branch whose native confirmation is a valid evaluated FAIL cannot falsify (register l.247; ruling e) and counts as evaluated. A missing or UNKNOWN one leaves the assessment UNRESOLVED.
- A non-prescribed one-film branch (S3-10) does not block the verdict.

**Known limitation of route (ii) offline.** A profiled curve moved to negative V_G does not cover V_G = 3 V. I_D(3 V) and μ_FE(3 V) are then unresolved (no extrapolation; tested). Interpolation between gm points of a covered profiled curve is labelled (A10).

## 7. S5 fold leaving out 6.3 nm (`s5_fold_6p3`)

**Codex ruling 2026-10-13 (choice 5).** "Test listed, no separate H-F prediction". H-J's forecast is retained. The function returns that statement and scores nothing.

## 8. Not covered by the register text

- **IGZO GAMMA0 +0.30** (S3-14..S3-16) is conditional in rev1 and not in the rev2 diagnostic set. Only GAMMA0 −0.31 is scored; another seed is refused.
- **Measured γ values** 1.13 (6.3 nm; `CAMPAIGN_DESIGN.md` l.118) and 0.27 (13.2 nm; register l.246) are quoted, not used.

## 9. Profiling rulings this draft depends on (`profile_s4s5.py` v2)

Each entry is a **Codex ruling 2026-10-13**; the details are in the `profile_s4s5.py` docstring.
- **A1:** trust box half-width = range/28, with no later nn switching. The proposal is the lowest-ranked *distinct* feasible point, with deterministic ties. Exhaustion is an optimizer stall, never three invented non-improvements.
- **A2:** S4a plus the completed S4b.
- **A3:** full quadratic in J, with full design-matrix rank required. Fit errors are diagnostics only.
- **A4:** running-best native √J improvement. Unresolved attempts do not establish < 0.01 dec.
- **A5:** signed mean on-window residual over the complete S4a inventory (15). Unknown, potentially-best candidates prevent the abort conclusion.
- **A6:** two-film J, using S4a plus that fold's S5 only. Four distinct candidates, then a distinct best and runner-up. No early primary freeze.
- **A7:** branch re-selection is enforced. A changed-branch fold uses four registered S3-centred local points: 2-D box corners or 3-D tetrahedral points at the A1 half-width, within the design ranges, ranked on training data only. **This amends the adaptive-generation rule. It needs a logged register amendment and the user's go before use:** the code freezes nothing in this mode without `--amendment REF`.
- **A8:** frozen scales and neighbour variants, with conservative flagging. Rank deficiency means combinations / UNRESOLVED (B5: full column rank). Archive derivatives are approximate diagnostics, not confidence intervals.
- **A9:** same-film comparisons. Only the designated film-local S6-23 is filled from the base, and it is labelled.
- **A10:** interpolation is labelled on covered profiled curves. Native sampling is required for S5 native scoring. The S4c tolerance is 0.01 dec.
  - The `campaign_matrix.json` S4C-* purpose text still says 0.005 dec. The needed edit belongs to the agent that owns the matrix.
- **Nuisance range:** ±0.5 V is anchored to one baseline Q_f (1.38345e12 cm⁻²). Repeated profiling gains no range.

Codex v2 review 2026-10-13 (~03:10Z):
- **Fix 1:** `profile_films` itself enforces one shared model: coordinates, branch, material model, shared overrides, tunnelling/Schottky options.
- **Fix 2:** every frozen S5 record carries an input-only expected held-out settings signature, in the S4a and the A7 mode: the training runs' shared settings plus the registered film-keyed inputs (quasi-2D NC300 at 2.0 nm only). `loo_score` always checks it.
- **Fix 3:** `native_confirmation` / `confirmation_status` (above).
- **(a)** ASSUMED spending rule: separation ≥ 1/56 (h/2) plus distinct deck-rounded inputs. Deck rounding alone decides equality to a registered A7 point.
- **(b)** A missing or UNKNOWN S4a candidate blocks the unconditional best/runner-up freeze; the conditional ranking is a DIAGNOSTIC. A terminal ineligible candidate is excluded only by a prospective, explicit exclusion record (`--exclusions`).
- **(c)** KCL_FAILED excluded; other convergence flags visible.
- **(d)** A7 at range/28. Two selected branches use the frozen original nuisance starts. No proposal without centre values. The amendment text is drafted separately and is not logged.
- **(f)** Bound-limited values are used in the search with warnings and remain unqualified for acceptance, falsification, D1 and D3d.

## 10. Decisions needed and order

1. **Freeze.** Codex reviews the v2 fixes and the encoded rulings. Then the user's logged freeze entry, with the sha256 of `hf_score_draft.py` and `profile_s4s5.py` (replacement hashes below; the v2 hashes f014ffc3... / fd64fb6e... are NOT to be frozen (Codex v2 review)) and the manual TCAD check. **DIAG_HF stays held until then.**
2. **A7** needs its own logged register amendment and the user's go before any changed-branch fold launch. The draft text is in the scratchpad (`A7_amendment_draft.md`), not logged.
   - The S4C purpose text must read 0.01 dec before logging. That edit belongs to the matrix owner.
3. **D1 and D2 need no launch** once frozen. They use only the already-seen S0-01, S1-01 and S1-02. They will be reported as retrospective, with the disclosure above, including the known V2 result.
4. **AFF-6p3 and STRIP-6p3 outputs stay sealed** in the meantime (work chat l.3852).
5. **Once frozen,** `campaign_C10_DIAG_HF.json` may be set to `runnable: true` (S3-11, S3-12, S3-13, S3-27, S3-10). D3 also needs S3-27 checked before any IGZO part counts.

**Hashes of this draft (v3, uncommitted):**
- `hf_score_draft.py`: `22fe24cdb4ef9d078d0b8e5fa948536310c0c534ad7fe02d88be9516bd2f6639`
- `profile_s4s5.py`: `0efe74fd3c5217fc1e53e539336d948bee3a519190b948281cd456d0d02e3cba`
- tests: 46/46 (`test_hf_score_draft.py`) and 113/113 (`test_profile_s4s5.py`)
