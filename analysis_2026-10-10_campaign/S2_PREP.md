# S2/S3 preparation for the frozen hypothesis register (2026-10-11)

**Register:** `iwo-tft-research-private/codex/work_chat/HYPOTHESIS_REGISTER.md`, tag `register-rev2-frozen-20261010T1833Z`. The register was read but not edited, and nothing in the private repository changed.

**Nothing was launched** (this preparation or the review fixes in §7).
- No `deckbuild.exe`, `run_atlas.py` or `run_campaign.py` launch.
- `results/RUN_INDEX.csv` has the same SHA-256 before and after (`4B60BC41…1F0F`), and there are still 74 run directories.
- Nothing was committed or pushed.

**Budget:**
- C10: 14 of 200 launches used (run_0061 to run_0074).
- Global: 74 of 260 (`config/solver.yaml` `max_launches`).

## 1. What changed

Line numbers are those after the review fixes of §7.

| File:line | Change |
|---|---|
| `scripts/build_iwo_decks.py:164` | Adds `o['oxide_mesh_factor'] = 1.0` (the default) and `o['zeroed'] = ()` (§7 R4). |
| `scripts/build_iwo_decks.py:165-175` | Review R4: `physics_options.intervention` (`none` default, `affinity_only`, `confinement_off`). It adds a comment-only `[B] OPTION … intervention` header line. |
| `scripts/build_iwo_decks.py:188-192` | Reads `gate_tunnelling.oxide_mesh_factor` (`None` → 1.0; a 0 now reaches the check, R5). Raises an error unless 0 < f ≤ 1 with gate tunnelling on. |
| `scripts/build_iwo_decks.py:218-223` | Comment corrected (R1): run_0067 has 15 Al2O3 and 28 HfO2 y intervals; the actual S2-11 refinement is stated. |
| `scripts/build_iwo_decks.py:225-228` | When f ≠ 1, adds a header line `[H] OPTION oxide y-mesh factor`. |
| `scripts/build_iwo_decks.py:311` | `sp_al *= f; sp_hf *= f`: the y.mesh lines at y = 0.002 and 0.017 µm. The y = 0 IWO/Al2O3 line is kept (R1/R13). Slicing and S/D `exclude_near` are untouched. |
| `scripts/build_iwo_decks.py:335-339` | R4: checks that the named laws evaluate to 0 and relabels those law lines `SET TO 0 (intervention)`. These are comment lines only. |
| `config/physics_options.yaml:24-27, 54-56` | `intervention: none` (R4) and `oxide_mesh_factor: 1.0`, with the actual refinement noted. The `qt_point_nm` comment says it is inert and was the old S2-11. |
| `make_campaign_matrix.py:106-133` | `base_overrides(..., aff_off=False)`. With `True`, `thickness_laws.dEc_eV.a` becomes 0, and (R4) `solver.physics_options.intervention=affinity_only` is added. |
| `make_campaign_matrix.py:252-267` | **S2-11 redefined.** It is S0-02 plus `gate_tunnelling.oxide_mesh_factor=0.5`. The inert `qt_point_nm`/`qt_slice_um` overrides are removed. Timeout ×4.5 = 5400 s (R3). The purpose states the actual refinement (R1). |
| `make_campaign_matrix.py:317` | S3-01..03 add `solver.physics_options.intervention=confinement_off` (R4; comment-only header). |
| `make_campaign_matrix.py:298-305` | **STRIP-6p3** (label `c10_strip_6p3_6p3`). Built exactly as S2-14/15: Q_f on, baseline shared overrides, `strip.L_p_um=20`, mode `strip`. |
| `make_campaign_matrix.py:374-383` | **AFF-2p0 / AFF-6p3** (labels `c10_aff_2p0_2p0`, `c10_aff_6p3_6p3`). These are `base_overrides(t, P(t), aff_off=True)`. Expected shifts: −281.6 / −62.2 ± 5 mV. |
| `campaign_matrix.json` | Regenerated: 184 entries, 16 in reserve. Against the pre-review file, only S2-11 (purpose, timeout), AFF-2p0/6p3 and S3-01..03 (one override each) changed. The other 177 entries are identical (JSON compare). |
| `make_campaign_configs.py:28-49, 129-139, 142-173, 199-213` | `DIAG` (24 ids, register order), `DIAG_PLANS`, `HOLD`, `runnable=false` plans with a `not_runnable_reason`, and verification of the runnable flag (R9, R12). |
| `config/campaign_C10_DIAGa_S2-11.json`, `campaign_C10_DIAG.json`, `campaign_C10_DIAG_HF.json` | Register route: S2-11 alone; then 19 entries (S2, S3 confinement, AFF); then the 5 H-F entries, **held** (`runnable=false`) until H-F scoring is frozen (R12). |
| `config/campaign_C10_S2_offfloor.json`, `campaign_C10_S3_branches.json`, `campaign_C10_MIN10.json` | Now `runnable=false` with the reason, plus a `HOLD:` stop rule (R9). Every plan file's `stop_rules_enforced_by` now says that run_campaign refuses `runnable=false` plans. Template purposes say to set runnable true after resolving. `--check`: verbatim and in order, YES. |
| `scripts/run_campaign.py:158-159` | R9: refuses a plan with `"runnable": false` before any launch, RUN_INDEX read or summary write. |
| `regress_all_decks.py:22-26` | Adds run_0062 to run_0066 to `KNOWN_DIFF`. See §3. |
| New: `s2_prep_decks.py`, `s2_prep_decks/` | 26 dry-built decks, plus `deck_diffs.txt` (every differing line). |
| New: `score_register.py`, `register_scores/` | Frozen scorer (review-fixed, §7), plus smoke outputs (all labelled). The superseded `smoke_hc_worst_run_0067.json` was moved to `register_scores/superseded_2026-10-11_review/`. |

`make_sample_decks.py` was re-run. All 12 sample files are byte-identical to the pre-review ones, and it reports 0 unreviewed statements. `check_v3_equivalence.py`: 101 planned_fixed decks have identical solver statements in V2 and V3; the S0-01 header check is OK. All 101 planned_fixed matrix decks were hashed against the pre-review snapshot. Only AFF-2p0, AFF-6p3 and S3-01..03 changed, and only in comment lines.

## 2. Dry-built decks: diffs (`s2_prep_decks/deck_diffs.txt`)

Counts are differing lines, removed plus added: statements / comments. S2-14/15 already had the V_D steps 0 → 0.1 → 0.7 V (REG-001) and Q_f on, and S2-16/17 had Q_f off, so nothing needed fixing. The script checks this automatically.

| # | Entry | Reference: statements / comments | What differs (statements) |
|---|---|---|---|
| 1 | S2-11 | S0-02 (run_0067): 4 / 1 | `y.mesh loc=0.002 spac=0.00025→0.000125`; `y.mesh loc=0.017 spac=0.001→0.0005`; no `qt*.mesh`. `y.mesh loc=0 spac=6.25e-05` is unchanged (see §6) |
| 2 | S2-04 | S0-01: 10 / 4 | oxide MATERIAL nominal, `qtunn.cmass`, `exclude_near` ×2, MODELS `qtnlsc.el qtnl.derivs`, `log … j.tun` |
| 3 | S2-06 | S1-02: 10 / 4 | the same at 13.2 nm |
| 4 | S2-03 | S0-01: 16 / 2 | τ 1e-9, σ 1e-13 (DEFECTS ×2), MODELS `trap.tunnel trap.hurkx mass.tunnel=0.2543`, `carriers=2` |
| 5 | S2-01 | S1-02: 16 / 2 | the same at 13.2 nm (`mass.tunnel=0.2123`) |
| 6 | S2-02 | S1-02: 14 / 2; S2-01: 12 / 2 | MODELS without `srh`, σ 1e-20, `carriers=2` |
| 7 | S2-08 | S1-02: 10 / 4; S2-06: 4 / 4 | worst oxide set |
| 8 | S2-12 | S2-04: 3 / 2 | `doping region=4 uniform tat.trap …`, MODELS `+ itat.sc.el ^tat.poisson`. No `TAT.SLICEPTS`, so the default 12 applies (§6) |
| 9 | S2-13 | S2-06: 3 / 2 | the same at 13.2 nm |
| 10 | S2-14 | S1-02: 37 / 9 | strip construction (no gate, L_p 20 µm, drain sweep) |
| 11 | S2-15 | S2-14: 34 / 27 | thickness only |
| 12 | S2-16 | S2-14: 2 / 2 | `interface qf=1.38345e+12 → qf=0` |
| 13 | S2-17 | S2-15: 2 / 2 | `interface qf=1.38345e+12 → qf=0` |
| 14 | STRIP-6p3 | S2-14: 34 / 26; S2-15: 34 / 27; S1-01: 35 / 9 | thickness only, against the other strip decks |
| 15-17 | S3-01 / 02 / 03 | S0-01 / S1-01 / S1-02: 10 / 18, 17, 17 | eg300, affinity, nc300 (3-D, bulk mass), mun (no mass factor), egd (follows E_g). The comments include the R4 intervention line and three relabelled law lines |
| 18 | AFF-2p0 | S0-01: **2 / 5** | **only** `affinity=4.01839 → 4.3`. Comments: the dEc line (relabelled `SET TO 0 (intervention)`), the AFFINITY line and the R4 `[B] OPTION affinity-only intervention` line |
| 19 | AFF-6p3 | S1-01: **2 / 5** | **only** `affinity=4.23784 → 4.3` |
| — | S3-01 vs AFF-2p0 | 10 / 15 | eg300, nc300, mun, egd: the non-affinity confinement inputs, so AFF + rest = S3-01 |
| 20-22 | S3-11 / 12 / 13 | 1 / 2 each | `mobility material=IWO igzo.tokyo … gamma0=-0.31` |
| 23 | S3-27 | S3-12: 6 / 6 | Q_f +1e12, MUN ×0.6 (material and mobility lines) |
| 24 | S3-10 | S1-01: 4 / 4 | `nta=0` (both DEFECTS) |
| 25-26 | S6-13 / S6-15 | S0-01 / S1-02: 4 / 2 | `doping … conc=2.5e+18` ×2. **ILLUSTRATIVE**: the matrix entries still carry `{frozen model}` |

The reference decks are byte-identical to the launched `device.in` of run_0061, run_0067, run_0068 and run_0069 (checked again after the review fixes: `checks: all passed`).

## 3. Regression

Run before any change, `regress_all_decks.py` gave: `identical 57; unexpected differences 5`.
- The 5 are run_0062 to run_0066, the S0-02 repair history.
- Their decks used intermediate QTNLSC forms (a 0.25 nm HfO2 line, QTX/QTY meshes) that overrides can no longer reproduce.
- Today's generator rebuilds them as the run_0067 deck. This was verified line by line.
- They were already failing the gate before this work, and are now listed in `KNOWN_DIFF`.
- **Protocol deviation, disclosed (review R23).** This gate read `unexpected differences 5` from the post-run_0066 QTNLSC change onward. Runs run_0067 to run_0074 were therefore launched while the gate was red, against CAMPAIGN_DESIGN.md:290 ("must print `unexpected differences 0` before the next launch"). The 5 differences were reclassified as known on 2026-10-11, after line-by-line verification. This line still has to be logged in the work chat by the main session; the private repository was not touched here.

After the S2 preparation and after the review fixes, the output is line-for-line the same: 75 lines, the same rebuilt SHA for every run, last line `identical 57; unexpected differences 0`.

## 4. Scorer (`score_register.py`; frozen rule text and tag are in the docstring)

**`selftest`: 32/32 OK.** The 11 original cases still pass, plus 21 review cases (R6, R7, R14 to R20):
- the masked V_th,cc equals `extraction.crossing`;
- the top level comes from the curve maximum;
- a censored V_th,cc bracket gives unresolved, and there is no fall-back to an earlier crossing;
- a resolution without a source is not demonstrated, and neither is an I_G ceiling given as free text;
- seven S2-11 cases, on a run_0067-like I_G profile;
- five generation cases;
- the worst-case disjunction;
- the falsification rule;
- the labels: pinned run, sensitivity and design pairs.

A mutation check confirmed that the old `v_at` fails its new case and the old `hc_mesh` fails five of the seven new S2-11 cases.

**Smoke tests on existing runs.** All are labelled *smoke test, not a registered result*:

| Smoke test | Result |
|---|---|
| `aff` run_0072 against run_0061 (S1-05 against S0-01) | ΔV_th,cc = +142.15 mV. 14 levels, 1e-13 to 3.4e-7 A/µm. Max deviation 101.5 mV: NOT RIGID (PROVISIONAL). Unchanged by the review; matches NC_AUDIT.md. |
| `he_alloff` / `s3_minus_s105` run_0072, run_0061 | ±0.14215 V, unchanged |
| `hc_nominal` run_0067, with `--resolution-ig 3.3e-18` citing the DOS ×2 I_D pair | The source is refused as an I_G ceiling (pair column id_A_per_um). \|I_G(−3 V)\| = 2.75e-12 against a bound of 4.6e-17: FAIL (PROVISIONAL: resolution not demonstrated) |
| `hc_nominal` run_0061 | I_G = 0: unresolved (below resolution, not demonstrated) |
| `hc_generation` run_0071 against run_0061, 3.29e-18 with a source | Before R6/R17 this would have been a FAIL at 5.37e-18 (noise against noise). Now: 0 resolved points; all are below resolution; verdict unresolved (resolution 3.29e-18 > bound 1e-20) |
| `hc_mesh` run_0065 against run_0067 (PROXY) | run_0065 has I_G = 0 at every point. 25 points are resolved in run_0067 only, so the change is ≥ 8.95 dec. Verdict: PROVISIONAL FAIL. The old code dropped these points and called the result unresolved |
| `hc_mesh` run_0067 against itself, 3.29e-18 | 31 points resolved in both runs, change 0.0 dec: PASS (identity check) |
| `hc_worst` run_0067/run_0061 used as both films | One film, 12.5 % valid floor points: unresolved |
| `hc_explains` run_0067 against run_0061 | Valid 12.5 % < 80 % and slope not OK: does not explain the floor |
| `resolution_pair` | DOS ×2, 2.0 nm: 3.287e-18 A/µm. Mesh ×0.7, 13.2 nm: 2.853e-18 A/µm. The JSON now records the run directories and the gate-tunnelling flags |
| `hb_ratio` / `hb_transfer` | Synthetic strips only (scratch, not stored). An ohmic strip gives 7.0, PASS. Below-resolution gives unresolved. The transfer arithmetic was checked by hand. |

**Not defined by the register: "demonstrated resolution".**
- There is one resolution per quantity (R14):
  - **I_D-type** (`--resolution` + a required `--resolution-source`; the CLI refuses a bare value).
  - **I_G ceiling** (`--resolution-ig` + `--resolution-ig-source`). The source must be a `resolution_pair` JSON on `ig_raw_A` from two gate-tunnelling runs, not under test. This is the only route to a non-PROVISIONAL `hc_nominal` verdict.
  - `hc_mesh` uses the I_G ceiling if one is given. The S2-11/S0-02 pair itself is refused as circular. Otherwise it uses the I_D-type current resolution, labelled as such.
- Until a value is supplied, every verdict uses the runner's KCL limit as a **PROXY**. Such a verdict is labelled PROVISIONAL and can never pass an upper bound.
- `resolution_pair` *proposes* a value from a refinement pair. It is not registered. **The method needs the user's sign-off as a logged amendment** (open).
- The AFF level floor does not depend on this value as long as the resolution is ≤ 1e-14 A/µm.

## 5. Launch list (register §3 order; nothing launched)

**24 launches now, in three plan files:**
1. `config/campaign_C10_DIAGa_S2-11.json`: **S2-11** (timeout 5400 s). Score it with `score_register.py hc_mesh <run> results/runs/run_0067_…` before going on. The reference is pinned to run_0067; any other S0-02 attempt scores only as a smoke test.
2. `config/campaign_C10_DIAG.json` (19 entries; it reuses the S2-11 launch, so 18 are new):
   - S2-04, S2-06, S2-03, S2-01, S2-02, S2-08, S2-12, S2-13;
   - S2-14, S2-15, S2-16, S2-17, STRIP-6p3;
   - S3-01, S3-02, S3-03;
   - AFF-2p0, AFF-6p3.

   The order within S2 after S2-11 follows the 2026-10-10 decision (nominal leakage, then generation, then strips). The register does not freeze it.
3. `config/campaign_C10_DIAG_HF.json`: S3-11, S3-12, S3-13, S3-27, S3-10. **Held** (`runnable=false`, refused by run_campaign) until the H-F scoring (§6) is implemented and frozen, with a logged entry; then set `runnable` to true.

**Plus 2 later:** S6-13 and S6-15, at order step 8, after S4c, once `{frozen model}` is resolved.

**Total 26.** C10 use becomes 33/200 after DIAGa + DIAG, 38/200 after DIAG_HF, and 40/200 at the end.

**Not launchable (`runnable=false`, R9):** `campaign_C10_S2_offfloor`, `campaign_C10_S3_branches` and `campaign_C10_MIN10`. They hold kept-out, trigger-gated or later-order entries, or do not start with S2-11. IMPLEMENTATION.md §6.2 still shows the old stage-plan route; for S2/S3 it is superseded by this list.

## 6. Open items and risks

- **S2-11 size.**
  - run_0062 matches S2-11 in both node count and oxide intervals per slice: 13,689 nodes and 75 intervals, against about 13,689 and about 77. run_0067 has 9,594 nodes and 43 intervals.
  - A geometric-grading estimate reproduces run_0067 (82 y lines) and run_0062 (117) exactly, and gives 117 y lines for S2-11.
  - run_0062 ran out of memory at `solve init` after 14 s at the old 2 GB limit. The limit is now 4 GB (LAA), and run_0067 peaked at 1.69 GB.
  - Time scaling of run_0067 (1246 s; run_0061 without tunnelling took 396 s) gives roughly 2200 to 3400 s, hence the 5400 s timeout (R3).
  - Memory use is unverifiable without a launch. An out-of-memory failure shows within seconds and costs one launch.
- **What S2-11 refines (R1, R2, R13, R22).**
  - The factor halves the spacing at y = 0.002 and 0.017 µm. The y = 0 IWO/Al2O3 line (0.0625 nm, shared with the IWO interface mesh) is kept. Halving it would also regrade the IWO interface region and mix two effects.
  - Measured in run_0067 `equilibrium.str`: Al2O3 has 15 intervals (0.06 to 0.25 nm) and HfO2 has 28 (0.24 to 0.99 nm).
  - Estimated for S2-11: Al2O3 has about 22 intervals (largest 0.125 nm, smallest 0.06 nm unchanged) and HfO2 about 55. The Conductor goes from 7 to about 8 intervals, a side effect.
  - So S2-11 refines the Al2O3 about ×1.5 and the HfO2 about ×2. A PASS at ≤ 0.1 dec reads as convergence under that refinement.
  - **Why the oxide mesh is the accuracy control for QTNLSC:**
    - 5.28 manual, PDF p.298: "The method uses a stepwise approximation of the potential. Consequently, it is recommended to use a fine mesh in the tunnelling direction."
    - 2004 manual, p.3-90 (QTUNN): the potential is approximated as piecewise constant, so results are best with "at least several mesh points in the tunnelling direction" in the oxide.
    - 5.28 p.302: for an Atlas-built mesh "everything including the direction of tunneling is determined automatically", with slices locally perpendicular to each semiconductor-oxide segment.
    - The x-mesh (117 lines) is unchanged, so the slice count and positions do not change. EXCLUDE_NEAR (p.303) does not depend on the mesh.
    - That the points along a slice are the device y-mesh nodes is *inferred* from these passages, not stated.
  - **The S2-11 verdict covers QTNLSC only.** The ITAT currents of S2-12/S2-13 use their own interpolated slice points, `TAT.SLICEPTS`. The default is 12 (MODELS table, p.326); the manual example uses 21. That is about 1.4 nm per point across the 17 nm stack, or 1 to 2 points in the 2 nm Al2O3. 5.28 p.322 says it "should be chosen so that the calculated currents are largely unchanged if one uses a slightly higher or lower value". This is untested. Under the H-C "converged" clause, S2-12/S2-13 therefore cannot count as converged without a logged amendment, for example a TAT.SLICEPTS sensitivity launch. `hc_explains` reports this. The frozen decks are unchanged.
  - The S2-11 definition still needs confirmation under the TCAD check rule (Codex review + manual check) before the launch.
- **H-C scoring.** Thickness scaling for the worst case is now implemented: S2-08 and S0-02 = run_0067; S2-07 is kept out. So is the falsification rule (`hc_explains`). Nominal leakage is registered at 2.0 and 13.2 nm only (S2-05 is kept out). For generation, (S2-01, S2-02) is the register pair (A9). (S2-03, S0-01) is a CAMPAIGN_DESIGN 7.1 pair, confounded by the carrier count.
- **H-F scoring is not implemented.** The missing pieces:
  - the two-film reference: shift +0.28 ± 0.08 V and scale 0.15 to 0.35 for 6.3 nm, against a shared profile on 2.0 and 13.2 nm only (`profile_shared.py profile` needs a triple today);
  - the baseline shape RMSE > 0.15 dec (`profile_shared.py` gives `shape_only_sqrtJ_dec`);
  - the IGZO gain of at least 0.05 dec and the γ targets (`campaign_extract` `pl_fit` gives γ);
  - the frozen S3-17..S3-23 contact trigger.

  Their operational definitions must be written and frozen first. Until then `campaign_C10_DIAG_HF` stays held.
- **Not yet reviewed.** Per the TCAD check rule, the generator options and the review-fixed scorer still need the Codex review and a manual check. The user's sign-off on the resolution method is open (logged amendment).

## 7. Review findings and fixes (2026-10-11)

Each finding was checked against the code, the run files and both manuals before it was fixed. Nothing was launched; RUN_INDEX is unchanged.

| # | Finding (file) | Outcome | What was done / why |
|---|---|---|---|
| R1 | S2-11 refines Al2O3 about ×1.47, not ×2; stale "8 + 15 points" comment and "about twice" purpose (generator:296) | **Fixed (disclosure; deck unchanged)** | Verified: run_0067 has 15 Al2O3 / 28 HfO2 intervals; grading gives about 22 / 55 for S2-11. The comment at `build_iwo_decks.py:218-223`, the S2-11 purpose, the YAML comment, §6 and the `hc_mesh` output field `refinement` now state about ×1.5 Al2O3 and about ×2 HfO2 |
| R2 | Open item cites only p.302; ITAT TAT.SLICEPTS not covered (S2_PREP:135) | **Fixed** | Quotes verified (5.28 p.298, p.302, p.303, p.322, p.326; 2004 p.3-90); §6 rewritten. The S2-11 verdict covers QTNLSC only; S2-12/S2-13 are not converged without an amendment (also a DIAG stop rule and in `hc_explains`). Decks unchanged |
| R3 | S2-11 timeout ×3 too tight; run_0062 is the same size (matrix:261) | **Fixed** | Verified: run_0067 1246 s, run_0061 396 s, run_0062 out of memory after 14 s. `timeout_mult` 4.5 gives 5400 s; matrix and plans regenerated; `--check` YES |
| R4 | AFF headers call the zeroed dEc "FITTED"; same in S3-01..03 (generator:332) | **Fixed** | New `physics_options.intervention` (default `none`: nothing emitted). AFF uses `affinity_only` and S3-01..03 use `confinement_off`. The result is a header line plus relabelled law lines; the solver statements are identical (checked). Wrong use (non-zero law, unknown value) raises an error |
| R5 | `oxide_mesh_factor=0` silently becomes 1.0 (generator:179) | **Fixed** | Verified; now `None` → 1.0, otherwise `float`. The values 0, 0.0, −0.5 and 1.5 raise; 1.0 gives the S0-02 deck byte for byte |
| R6 | `hc_generation` ignores `valid_mask`; noise against noise scores FAIL (scorer:255, register lens) | **Fixed** | `gen_core`. A difference is resolved only if both currents are resolved and differ by > 0.1 dec or in sign, or if one is resolved more than 0.1 dec above res (lower bound \|I\| − res). Otherwise it is below resolution with a stated ceiling. Smoke: run_0071 against run_0061 at 3.29e-18 is now unresolved, not FAIL |
| R7 | `hc_mesh` skips points censored in one run (scorer:267, register lens) | **Fixed** | `mesh_core`. A one-sided change of more than 0.1 dec is a FAIL; otherwise the point is unresolved, never dropped. KCL-censored points give unresolved, and PASS needs ≥ 3 points resolved in both runs (implementation definition, like the AFF 3-level rule); the point count is reported |
| R8 | Worst case scored on flatness only, labelled FAIL when flat (scorer:280) | **Fixed** | `hc_worst S2-08 S1-02 S0-02(run_0067) S0-01`. It gives a flatness sub-result (total I_D slope, §7.1) and a thickness-scaling sub-result (Δ d_floor_ratio > 0.5 dec; S2-07 kept out). Verdict: PASS if either fails, FAIL only if both hold, otherwise unresolved. The slopes of \|I_G\| and ΔI_D are reported, not scored |
| R9 | Kept-out and conditional runs sit in runnable plans; MIN10/S2 do not start with S2-11 (config) | **Fixed** | Verified (`runnable` true; `run_campaign.py` ignored the flag). S2_offfloor, S3_branches and MIN10 are now `runnable=false` with a reason and a `HOLD:` stop rule. `run_campaign.py` refuses such plans; a no-launch check (launch paths patched to raise) showed that all 4 held plans and a template are refused, and RUN_INDEX is unchanged |
| R10 | Run pairs keyed by label; S1-06 pair; S2-03/S0-01 not a register pair (scorer:78) | **Fixed** | Verified: 6 runs share `c10_s0_02_2p0`; run_0073 TIMEOUT, no CSV. `PIN` makes `c10_s0_02_2p0` count only as run_0067 (`hc_mesh`, `hc_worst`). (S2-01, S1-06) is removed. (S2-03, S0-01) is labelled a design-defined pair, confounded by the carrier count, file prefix `design_` |
| R11 | The no-Q_f H-B branch is labelled a registered test (scorer:224) | **Fixed** | Labelled `sensitivity, not a registered prediction`, file prefix `sensitivity_` |
| R12 | H-F scorers and the H-C falsification rule missing (scorer:1) | **Partly fixed** | `hc_explains` implements the four §7.2 criteria plus convergence (QTNLSC through a registered S2-11 PASS via `--mesh-score`; ITAT and generation not demonstrated). H-F is **not** implemented, because its operational definitions are not written. Instead the 5 H-F entries were split into `campaign_C10_DIAG_HF.json`, held (`runnable=false`) until that scoring is frozen |
| R13 | S2-11 refines the oxide only in part (generator:297, register lens) | **Fixed by disclosure; alternative not taken** | The finding's "13 → 21, ×1.7" is replaced by the measured 15 and an estimated about 22 (×1.5). An extra oxide-side line cannot halve the y = 0 spacing without touching the IWO interface mesh. Confirmation of the definition under the TCAD check rule stays open (§6) |
| R14 | Any `--resolution` counts as demonstrated for every quantity; above_abs_floor acts as a resolution floor (scorer:94) | **Fixed (sign-off open)** | One resolution per quantity; the I_G ceiling for `hc_nominal` requires a gate-tunnelling `resolution_pair` JSON (checked from the run directories) and refuses circular use. `above_abs_floor` censors only under the KCL PROXY. The user's sign-off of the method as a logged amendment cannot be done in code and remains open |
| R15 | AFF departs from A16: top level, fall-back crossing, unmasked ΔV_th,cc (scorer:109) | **Fixed** | Top level = min over the curves of max(I > 0) / 1.5, the register wording; levels still need valid brackets. (b) and (c) as R18 and R19 |
| R16 | `hc_mesh` drops resolved-to-censored points; synthetic multi-decade changes score PASS (scorer:267, regression lens) | **Fixed** | Same change as R7. The reviewer's two synthetic cases are in `selftest` on a run_0067-like profile and now FAIL |
| R17 | `hc_generation` ignores `kcl_pass`; a KCL-failed point gives FAIL (scorer:255, regression lens) | **Fixed** | Same change as R6. A KCL-censored window point makes the verdict at best unresolved (selftest case) |
| R18 | `v_at` falls back to an earlier crossing (scorer:109) | **Fixed** | Last upward crossing of the whole curve; a censored bracket gives None. Selftest case (floor oscillation plus a censored turn-on bracket) |
| R19 | ΔV_th,cc from unmasked curves (scorer:167) | **Fixed** | `vth_cc` uses the validity mask, so a censored 1e-9 bracket gives an unresolved shift and rigidity. `he_alloff`/`s3_minus_s105` use the KCL mask (the 1e-9 brackets lie far above any resolution). Smoke values unchanged |
| R20 | A bare `--resolution` counts as demonstrated (scorer:94) | **Fixed** | The CLI refuses `--resolution`/`--resolution-ig` without a source (exit 2, checked); the function marks such a value as not demonstrated |
| R21 | `oxide_mesh_factor=0` gives an unmarked S0-02 duplicate (generator:179, regression lens) | **Fixed** | Same change as R5 |
| R22 | S2-11 deck: disclose ×1.5 / ×2 (s2_prep_decks/S2-11:53) | **Fixed by disclosure** | As R1. The Codex digest is not written here (work chat, private repository); the main session should carry the same line |
| R23 | Gate was red for run_0067..0074 (regress_all_decks:26, process) | **Fixed by disclosure** | Verified: the scratch output of 02:40 (pre-change generator, old KNOWN_DIFF) reads `unexpected differences 5`, and run_0067..0074 rebuild identically with that generator. A deviation line was added to §3. CAMPAIGN_DESIGN.md was not edited (its stop rules are in the register's freeze list), and the work chat is in the private repository; the main session must log it |

No finding was rejected as wrong. Two numerical details in R13 and R22 (13 or 14 → 21 Al2O3 intervals) were corrected to the measured 15 and an estimated about 22.

**Re-run after the fixes:**
- `regress_all_decks.py`: identical 57; unexpected differences 0, with the same per-run SHA as before.
- `check_v3_equivalence.py`: 101/101 identical solver statements; S0-01 header OK.
- `make_campaign_configs.py --check`: YES; held plans S2_offfloor, S3_branches, MIN10 and DIAG_HF.
- `s2_prep_decks.py`: all checks passed.
- `make_sample_decks.py`: 12/12 byte-identical.
- `score_register.py selftest`: 32/32.
- Smoke set: 12/12 exit 0.
