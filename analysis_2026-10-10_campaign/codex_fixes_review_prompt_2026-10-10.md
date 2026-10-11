You are an independent, ADVERSARIAL, read-only reviewer. Working directory IWO_PHYSICS_CONSTRAINED_MODEL_V1 (Silvaco ATLAS 5.28
deck generator + a 200-launch campaign). The author has just applied fixes for seven blocking review findings. The full diff of
the fixes is analysis_2026-10-10_campaign/fixes_after_review_2026-10-10.diff (two new files are included in full at its end).
Find what is still WRONG or MISSING. Do not re-confirm what is fine at length.

=== HARD RULES (read-only) ===
- Do not modify, create or delete any file. Do not use the network.
- NEVER launch Silvaco: do not run deckbuild.exe, scripts/run_atlas.py, scripts/run_campaign.py, or anything under /mnt/c/sedatools/exe.
- Do NOT execute any Windows executable (*.exe, including the Windows Python venv) through WSL interop. Linux python3 has no
  NumPy/PyYAML/SciPy; use it only for arithmetic or plain-text parsing. Static reading, grep, sed -n, awk are fine.
- Report only what you verified; otherwise say UNVERIFIED. Cite file:line.

Findings and the fixes claimed:
1. strict_xy rejected the DeckBuild point-count line ('36 2 2', 2nd line of every extract file). FIX: module-level
   run_atlas.strict_xy(path) skips exactly one all-numeric 3-integer line before the first data row and requires the data-row
   count to equal its first value. Claimed tests: all 198 real terminal-current exports under results/runs pass; a 12-case mock of
   execute_strip using copies of results/runs/run_0041_*/idvd_vg1.dat / isvd_vg1.dat gives the expected statuses.
2. Launch cap not enforced. FIX: config/solver.yaml max_launches 271 -> 260 (RUN_INDEX has 60 distinct run IDs); run_campaign.py:
   C10 plans refuse --workers != 1, count c10_* labels in RUN_INDEX (cap 200), and never re-launch an entry whose label already has
   a RUN_INDEX row (any C10 plan; success reused, failure reported; --retry ID to override). Check the loop logic in main() for
   any path that launches twice, skips silently, or stops early; check that labels are unique across all C10 plan entries
   (config/campaign_C10_*.json incl. templates) and that no other launch path (run_atlas.py CLI) bypasses the 260 cap.
3. post_run_checks.py could report ACTIVE_AS_REQUESTED for inactive options. FIX: solver_lines() drops everything before
   'go atlas', echoed 'ATLAS>'/'EXTRACT>' lines and '#' comments; per-option ACTIVE / NOT_ACTIVE / UNVERIFIED; in-solver strip
   checks regions 8/9 material IWO + semicond. and the electron mu in the mobility summary; IGZO needs the model named; each
   gate-current model separately (single model: nonzero I_G, since I_G is exactly 0 in all 51 earlier runs; QTNLSC+ITAT:
   --gate-control run of the same deck without oxide TAT). Look at results/runs/run_0040_*/deckbuild.out for the real table
   formats (lines 237-433) and check the parsers against them (e.g. REGIONAL MATERIAL PARAMETERS column alignment, the
   'mu  = 57.7925' line format, region numbering when the in-solver strip regions 8-12 exist plus electrodes).
4. N_D label. FIX: V3 yaml, make_campaign_matrix.py, CAMPAIGN_DESIGN.md (D12, section 3 table, 4.4, 11), deck header (from the
   V3 label): 'FITTED V1 donor amplitude, kept fixed; constant thickness dependence ASSUMED'. Search for any remaining place
   that still calls N_D ASSUMED / not fitted (CAMPAIGN_DESIGN.md, IMPLEMENTATION.md, DFT_TO_TCAD.md, GENERATOR_AUDIT.md,
   config/*.yaml, sample_decks/NEW_STATEMENTS.md).
5. Oxide TAT charge. FIX: new option oxide_tat.poisson (default 1 = ATLAS default, emits nothing); poisson=0 appends
   '^tat.poisson' to the MODELS line; S2-12/S2-13 now carry solver.physics_options.oxide_tat.poisson=0
   (sample_decks/extra/S2-12_*.in). Check syntax against the manual (report_latex_full/tools/atlas_manual_pages.txt around
   l.14541 and the p.327 example) and whether ITAT.SC.EL current is still computed with ^TAT.POISSON.
6. FNORD constants. FIX: F.AE = A/r^2, F.BE = r B with r = 19.57/9.0 (HfO2-barrier Lenzlinger-Snow A, B) in
   config/physics_options.yaml sets and in the S2-09/S2-10 matrix overrides (worst 2.171e-6 / 8.628e7; nominal 7.402e-7 /
   2.167e8). Recompute; check that the overrides in config/campaign_C10_S2_offfloor.json and sample_decks/extra/S2-10_*.in carry
   the new values and that nothing else still uses the old ones.
7. C12/C13 missing. FIX: analysis_2026-10-10_campaign/campaign_extract.py (wrapper around the registered
   analysis_2026-10-06_extraction/run_extraction.analyse; J windows; compare with S1 rules) and profile_shared.py (check / profile
   / adopt; surrogate / loo / jacobian NOT implemented, disclosed). Review the transformation sign (I_new(V) = I_old(V + q dQf/Cox)),
   the mu-law scale (mu_band_new(t)/mu_band_run(t)), the J definition vs CAMPAIGN_DESIGN.md 5.1, the no-extrapolation handling, the
   optimizer bounds (|dV0| <= 0.5 V, mu_inf 10..300, ell 0..50), and whether 'check' compares the right things for S1-07 (S1-07 vs
   S0-01 differ in Qf and mu_band_fitted[2.0] only? read config/campaign_C10_S1_baselines.json and the S0a plan).
   Claimed real-data evidence: check run_0003 vs run_0001 (Qf +1.73e12 only) max 0.00096 dec on the J windows; run_0008 vs run_0003
   and run_0009 vs run_0004 (mu only) <= 4e-6 dec.

Also: any new defect introduced by the fixes; anything that would now waste a launch or mislabel a fitted quantity.
Answer in at most ~600 words: per item OK / FIX (exact change) / UNVERIFIED, then "New defects".
