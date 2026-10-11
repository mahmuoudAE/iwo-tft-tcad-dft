FIX FIRST.

1. **[BLOCKING] E — The enforced budget allows 211 launches and parallel execution**

   **Evidence:** `config/solver.yaml:18`; `scripts/run_atlas.py:39–46`; `scripts/run_campaign.py:75–87`. Independently counted 60 distinct run IDs in `results/RUN_INDEX.csv`.

   **Problem:** `271 − 60 = 211`, exceeding this campaign’s 200-launch cap. `--workers 2` remains accepted. The lock protects reservations within one process; it does not enforce sequential execution across separate campaign processes. Failed entries are retried on resume, and MIN10 completion is not shared automatically with stage plans.

   **Fix:** Enforce a campaign-wide counter capped at 200, including failures, and reject workers other than one for C10. Add a cross-process launch lock. If this campaign exclusively uses the remaining global allowance, 260 total launches would enforce the numerical cap.

   **New or earlier:** Earlier reviews identified retries and advised sequential execution; they did not identify the remaining enforcement gap as blocking. Current code retains it.

2. **[BLOCKING] F — Activation checks can certify inactive options**

   **Evidence:** `analysis_2026-10-10_campaign/post_run_checks.py:68–79`; `sample_decks/extra/S3-24_c10_s3_24_2p0.in:32`; `results/runs/run_0040_13p2_recal_dos384_13p2/deckbuild.out:4–35,339–340`.

   **Problem:** Four concrete weaknesses:
   - Missing electron mobility text returns `''`; the IGZO condition checks only that “Concentration Independent” is absent. I verified that this missing-summary predicate passes.
   - BQP accepts any non-`ATLAS>` line mentioning BQP. Existing outputs print deck comments without that prefix; the sample’s BQP header alone satisfies this test.
   - Strip activation checks only whether region 8 exists. The existing baseline run_0040 already prints region 8.
   - QTNLSC and ITAT share one “nonzero gate current” test. Active QTNLSC can therefore hide inactive ITAT. Neither BQP masses nor strip region mobilities are verified.

   **Fix:** Require positive model identification, exclude all input/comment echoes, verify strip regions’ material and mobility, and check each tunnelling model separately. Treat missing evidence as UNVERIFIED, not ACTIVE_AS_REQUESTED.

   **New or earlier:** Earlier passes left runtime activation unverified but missed these false-positive checks. Unfixed.

3. **[BLOCKING] C — V3 loses the donor density’s fitted provenance**

   **Evidence:** `config/iwo_material_model.yaml:92–97`; `config/iwo_material_model_v3.yaml:119–123`; `../iwo-tft-research-private/01_CURRENT_STATE.md:153`; `CAMPAIGN_DESIGN.md:499`.

   **Problem:** V1 explicitly labels the donor law FITTED. V3 retains its `Nd0 = 2.5e17 cm⁻³`, changes the thickness dependence to constant, and labels the value ASSUMED; the design additionally lists N_D as “Not fitted.” Retiring the thickness law does not erase the retained amplitude’s calibration history.

   **Fix:** Label it “FITTED V1 donor amplitude, retained and held fixed; constant thickness dependence ASSUMED.” Correct the design, matrix descriptions and emitted provenance accordingly.

   **New or earlier:** Not raised in either implementation review. Unfixed.

4. **[BLOCKING] B — The oxide-TAT comparison does not isolate tunnelling-induced drain current**

   **Evidence:** `campaign_matrix.json`, entries S2-12/S2-13; `sample_decks/extra/S2-12_c10_s2_12_2p0.in`, statements `doping … tat.trap conc=1e19 …` and `models … qtnlsc.el … itat.sc.el`; `IMPLEMENTATION.md:233–237`; manual marker **`===== PDF PAGE 323 =====`**, which states that TAT trap charge enters Poisson by default.

   **Problem:** The prescribed baseline comparison simultaneously adds direct tunnelling, oxide traps, trap-assisted tunnelling and oxide trapped charge. Fully occupied traps would provide up to `1e19 × 15e-7 = 1.5e13 cm⁻²`, substantially exceeding the fitted interface charge. A resulting ΔI_D can include an electrostatic transfer-curve shift; it is not necessarily collected gate leakage. The current `drain_share` calculation cannot distinguish those contributions.

   **Fix:** Use the existing same-film nominal QTNLSC runs to separate the direct-tunnelling contribution. Add a controlled diagnostic for oxide-charge versus tunnelling effects, and inspect trap occupancy and injected-current outputs. Until then, label ΔI_D as the combined response of the charged-oxide model, not TAT current collected by the drain.

   **New or earlier:** The design review requested matched controls, but neither implementation review checked this charge confounding. Unfixed.

5. **[BLOCKING] F — Transfer runs retain acceptance holes fixed only for strip runs**

   **Evidence:** `scripts/run_atlas.py:158–169,180–186`; compare `execute_strip()` checks at approximately `:266–270`.

   **Problem:** `execute()` can reach `REAL_ATLAS_SCORED` without rejecting `timed_out`, a nonzero return code, or `not sc['finished']`, provided exports exist and pass its remaining checks. Source and gate grids are interpolated onto the drain grid without independently requiring complete grids. A partially exported terminal current can therefore be extrapolated through missing points. Most campaign launches use this function.

   **Fix:** Apply the strip completion and finite-data safeguards to transfer execution. Require complete, matching terminal grids before KCL; finalize failures explicitly. Offline post-run checks should also reject unsuccessful runner status.

   **New or earlier:** Earlier reviews concentrated on the new strip function. These are inherited defects, unchanged but material to this campaign.

6. **[BLOCKING] E — Runnable plans still launch known duplicates**

   **Evidence:** `config/campaign_C10_S3_branches.json:147,254`; `config/campaign_C10_S4a_spacefilling.json:57,97,137`; `scripts/run_campaign.py:82–87`.

   **Problem:** The runner ignores `solver_identical_to`. S3-04/S3-07 repeat S0-01, and the three first S4a entries repeat the baselines when no branch is adopted. I independently compared S3-07 and S0-01: their noncomment solver lines are identical. Launching the supplied plans directly wastes these launches. MIN10 adds further overlap unless summaries are supplied to the trimming helper.

   **Fix:** Make executable plans exclude these entries automatically, or make the runner reuse the referenced successful result. Deduplicate across MIN10 and stage summaries.

   **New or earlier:** Earlier design review raised S4a reuse; IMPLEMENTATION documents both duplicate groups. The plans still require manual trimming, so the issue is not enforced away.

7. **[BLOCKING] B — Rectangular WKB transmission is incorrectly called an upper bound**

   **Evidence:** `analysis_2026-10-10_campaign/leakage_bounds.py:26–29`.

   **Problem:** The calculation uses a constant barrier across all 17 nm and prints “upper bound.” For an injection barrier lowered along the tunnelling direction by applied bias, the WKB action decreases and transmission increases. These zero-field rectangular transmissions do not upper-bound biased bilayer tunnelling. The arithmetic produces `2.2e-34` and `6.6e-51`, but their advertised bound interpretation is wrong.

   **Fix:** Rename them zero-field rectangular-barrier estimates. For a biased bound, integrate the stated piecewise oxide barriers and electrostatic potential, identifying injection direction and electron energy.

   **New or earlier:** Earlier reviews accepted conditional leakage estimates but did not correct this specific bound direction. Unfixed.

8. **[NON-BLOCKING] D — Numerical nulls cannot verify the quoted microscopic bounds**

   **Evidence:** `CAMPAIGN_DESIGN.md:382–384`; `post_run_checks.py:89–92`; `config/solver.yaml:19–21`; `01_CURRENT_STATE.md:185–186`.

   **Problem:** The predicted extreme-SRH contribution is ≤`1e-20 A/µm`, while the absolute KCL allowance at 13.2 nm is `6.6e-13 A`. Absence of a resolved excess cannot verify the microscopic prediction; it establishes only a much looser numerical null. Similarly, the S1 two-carrier decision threshold of 0.1% is below the recorded approximately 0.7% numerical uncertainty.

   **Fix:** Report unresolved contributions as below the demonstrated numerical sensitivity. Require matched numerical uncertainty before interpreting the 0.1% criterion.

   **New or earlier:** Earlier reviews discussed numerical checks but did not explicitly reconcile these thresholds. Unfixed.

9. **[NON-BLOCKING] B — FN arithmetic is correct, but its field/barrier pairing is not a bilayer leakage bound**

   **Evidence:** `config/physics_options.yaml:45–62`; `sample_decks/extra/S2-10_c10_s2_10_13p2.in:84`; `leakage_bounds.py:16–24`; manual markers **`===== PDF PAGE 288 =====`** and **`===== PDF PAGE 289 =====`**.

   **Problem:** The deck applies HfO2/TiN constants at the semiconductor-interface field, which is on the Al2O3 side. Under the script’s simple 3 V voltage division, fields are `1.550e6` and `3.371e6 V/cm`; the exponential is highly sensitive to that distinction. Actual gate-to-channel versus channel-to-gate barriers also differ. This run cannot independently validate a physical bilayer leakage magnitude.

   **Fix:** Retain it as an explicitly approximate model sensitivity; report interface field and injection direction alongside its result. Use QTNLSC for the piecewise barrier calculation after activation is established.

   **New or earlier:** Already raised by the design review and disclosed in current documentation. Disclosure fixes the framing, not the physical approximation.

10. **[NON-BLOCKING] F — “Strict” strip parsing still silently skips malformed numeric rows**

   **Evidence:** `scripts/run_atlas.py:276–282`.

   **Problem:** A row such as `0.1 corrupted` raises `ValueError` and is discarded as header text. If another valid 0.1 V row exists, all requested points can still pass. Thus the claimed rejection of malformed rows is incomplete.

   **Fix:** Recognize allowed headers explicitly; reject conversion failures on rows beginning with a numeric voltage.

   **New or earlier:** Both earlier passes requested strict parsing. The current implementation fixes finite values, conflicting numeric duplicates and missing points, but not this case.

Checked and found OK:

- New statement families match local manual/example syntax: QTNLSC/LOG, FNORD constants, TAT.TRAP, IGZO.TOKYO, Schottky and BQP. Relevant markers include **158–161, 195–196, 288–289, 301–303, 323–327, 839–842**. Installed examples `diodeex12`, `quantumex20`, `tftex21_aux.in` and `quantumex05` support the corresponding syntax.
- Sample continuations keep ARICHN and quantum masses on MATERIAL; new MATERIAL/MOBILITY/model declarations precede SOLVE INIT. No definite new keyword misspelling found.
- Schottky `WORKFUN = affinity + barrier`, ARICHN units, nm→µm mesh conversion and sheet-DOS conversion are correct.
- Reproduced FN constants and the published V1-based SRH arithmetic using Linux arithmetic only. Those SRH estimates are not updated V3 bounds.
- Earlier strip layer/Q_f fixes are present. Timeout-first, completion, finite-array, required-bias, sign and KCL checks are substantially repaired.
- No automatic V2 post-solver strip addition appears in the reviewed runner changes; no automatic summation of leakage paths found. BQP/dE_c and IGZO/in-solver-strip guards exist.
- Counts are 181 entries: 98 fixed runnable entries plus 83 templates; timeout sum is **110.861 h**. Raw templates contain unresolved overrides and are not executable as supplied.
- `CAMPAIGN_DESIGN.md` §11 honestly preserves V2’s failed registration and calls LOO retrospective; S7 is a stress check. Neither provides independent validation. The opening “out-of-sample evidence” wording should be tightened.
- QE status/resource diffs are monitoring updates, with no deck-generation dependency identified.

UNVERIFIED:

- Actual activation, Conductor-gate injection, BQP mass use, bilayer ITAT behaviour, split-electrode currents, node counts and timeout adequacy: no simulator launch permitted.
- Independent reproduction of the NumPy/PyYAML gates: those packages are unavailable. Static OFF-path inspection found no V1/V2 regression, but byte identity on every path is not established.
- `ifn."gate"` extraction: the supplied ATLAS text/examples did not independently establish it; require `ifnvg.dat` on the first FN run.
- Hand-resolved adaptive/frozen plans, calibrated 31.8 nm mobility-law propagation and the final S6-27 deck: these artifacts do not yet exist.
- Original publication/SI support for literature and target-device permittivity labels: citations are present, but their underlying source content was not independently verified.