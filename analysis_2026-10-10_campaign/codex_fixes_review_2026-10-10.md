# Codex review of the review fixes (2026-10-10)

- **What this is.** The final answer of a read-only, adversarial Codex run (codex-cli 0.162.0 in WSL "Ubuntu", `codex exec --sandbox read-only`) on `fixes_after_review_2026-10-10.diff` (first version). Prompt: `codex_fixes_review_prompt_2026-10-10.md`; full log: `codex_fixes_review.log`. Codex ran no simulator and changed no file.
- **Outcome.** Every FIX point and both new defects were adopted (IMPLEMENTATION.md §11.9). Re-check: `codex_fixes_recheck_2026-10-10.md`.

---

1. **OK / UNVERIFIED:** A plain-Python equivalent of `strict_xy` accepted all 198 terminal exports, including counts and duplicate checks (`scripts/run_atlas.py:63–88`). The claimed 12-case `execute_strip` mock remains **UNVERIFIED**.

2. **FIX:** `--retry` cannot retry completed entries: `done` removes them before retry handling. Exclude retry IDs from `done` (`scripts/run_campaign.py:121–128`). The global cap is also overrideable through `--override solver.runner.max_launches=...`; execution applies overrides before `reserve`. Enforce the cap from an unoverrideable source (`scripts/run_atlas.py:44,147–150,170`). Across plans, 191 entries represent 181 labels; the ten duplicates are identical MIN10/stage entries, with no conflicting definitions verified.

3. **FIX:** Activation still admits false evidence:
   - `tmun` searches both electron and hole sections; matching hole `tmu` can falsely certify electron TMUN. Parse electrons only (`analysis_2026-10-10_campaign/post_run_checks.py:130–131`).
   - Gate-control matching checks override-set differences, but does not establish equal thickness, saved material, geometry, or disabled TAT. Compare effective inputs and require TAT off before attributing the current difference (`post_run_checks.py:177–186`).
   
   The demonstrated material and `mu = 57.7925` formats parse correctly. Actual regions 8–12 output remains **UNVERIFIED**.

4. **OK:** No remaining contradictory donor-amplitude label found in the requested sources. V3 explicitly distinguishes the fitted amplitude from assumed constant thickness dependence (`config/iwo_material_model_v3.yaml:124–127`).

5. **OK / UNVERIFIED:** The local manual explicitly separates disabling trap charge from selecting the tunnelling-current model (`report_latex_full/tools/atlas_manual_pages.txt:14541–14548,14745`). The sample retains `itat.sc.el` alongside `^tat.poisson` (`analysis_2026-10-10_campaign/sample_decks/extra/S2-12_c10_s2_12_2p0.in:88`). Runtime current remains **UNVERIFIED**.

6. **OK:** Recomputing the generator’s formulas gives nominal **7.40238e−7 / 2.167295e8**, worst **2.171365e−6 / 8.627916e7**. Overrides and sample match rounding (`config/campaign_C10_S2_offfloor.json:358–359,399–400`; `analysis_2026-10-10_campaign/sample_decks/extra/S2-10_c10_s2_10_13p2.in:84`).

7. **FIX:** Sign, mobility ratio, J windows, and objective bounds match the design (`profile_shared.py:54–56,107–120,139–144`). S1-07 differs from S0-01 only in Qf and the 2-nm mobility anchor. However:
   - Unequal starting Qf merely warns; adding identical dQf leaves unequal final Qf while reporting one shared fitted value. Reject the triple or shift each film to one absolute target (`profile_shared.py:128,164`).
   - Forbidden tunnelling/Schottky profiling merely warns, yet still labels results “exact”; refuse it (`profile_shared.py:130–131,169`).
   - `check` can report PASS with undercovered windows; `adopt` ignores coverage and optimizer success. Return UNVERIFIED pending native confirmation (`profile_shared.py:99–103,167,178–181`).
   
   Claimed real-data numerical deviations remain **UNVERIFIED**; surrogate/LOO/Jacobian remain missing (`profile_shared.py:187–188`).

**New defects**

`profile_shared.py` returns exit **0 even for FAIL/UNVERIFIED**, allowing automated gates to continue. Map verdicts to nonzero exits (`:197`). Also, successful label reuse checks only overrides—not thickness, mode, or saved model/deck identity—so changed inputs can silently reuse stale results (`scripts/run_campaign.py:97–100`).
