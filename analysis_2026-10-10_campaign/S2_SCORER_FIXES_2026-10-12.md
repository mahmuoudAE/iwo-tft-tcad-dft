## 8. Scorer fixes required by Codex's review (2026-10-12)

*To append to S2_PREP.md. This section implements Codex's review of 2026-10-12T13:18Z (CODEX_WORK_CHAT.md, reply item 5, "Scorer changes required before primary scoring"). It is not a new rule.*

**Scope and sealing.**
- No ATLAS launch, no deckbuild call and no launch path was used. `scripts/run_campaign.py` was not touched.
- Nothing was committed.
- Only run_0061..run_0074 and synthetic data were used.
  - No run directory from 2026-10-12 (run_0075 or later) and nothing under `results/sealed/` was opened, listed, parsed or scored.
  - `results/RUN_INDEX.csv` was read once, for orientation, through a filter anchored to `^run_00(6[1-9]|7[0-4]),`, so no later row was displayed or parsed.
  - The scorer itself never reads RUN_INDEX. It takes run status from each run's own files.
- The 31-line register text block quoted in the docstring (`Register:` … H-F) is byte-identical to the frozen version (checked by script).
- No threshold, band or registered number changed.
- Only the "Definitions used to apply the rules" section of the docstring changed. Its new items are marked [C1]..[C5] (lines 38-91).

### 8.1 Fixes

| # | Codex finding | Fix (file:line in the new `score_register.py`) |
|---|---|---|
| C1 | Arbitrary source text qualifies an I_D resolution, and an I_G self-pair can qualify a ceiling | `qualify` :301, used by `resolution` :265 and `ig_resolution` :289. A resolution is demonstrated only by a `resolution_pair` JSON (:431) that is **re-computed from its two run directories at every use**. The run-file sha256 and the candidate must match the JSON. The pair must also meet all of these: two **distinct** runs; accepted runner status; complete and finite exports; a **verified numerical intervention** (`intervention` :397); candidate and value finite and positive; value ≥ candidate. For an I_G ceiling, both runs must have gate tunnelling and neither may be under test. The intervention check: the `execution.json` overrides may differ only in DOS levels, `geometry.mesh.spacing_factor` or the oxide y-mesh factor (KNOBS :165), and the `device.in` statements only in the matching mesh-spacing or numa/numd lines, with at least one changed. Film and `material_model_used.json` must be the same. The pair JSON, its sha256 and the run-file sha256 go into every output (`resolution_evidence`, `evidence`). The CLI refuses anything else with exit 2 (`Refused` :171, `main` :1085). A function call reports it as not demonstrated (PROVISIONAL). |
| C2 | Generation subtraction understates its ceiling (±5.4e-21, R = 6e-21) | `gen_core` :614. When both currents are below resolution the ceiling is R_a + R_b (:634). In the one-run-resolved case the bounds use the other run's resolution (:632). Codex's example now gives *unresolved* (ceiling 1.2e-20 > 1e-20), not *consistent*. |
| C3 | Invalid required data can PASS (NaN mesh point; failed or timed-out nominal run) | `run_problems` :197 and `usable` :217 are called by every scoring function. The run must have completed: status REAL_ATLAS_SCORED, _PREDICTION or _STRIP, or KCL_FAILED with per-point censoring. It also needs return code 0, no timeout, no simulator error, the ATLAS banner, every requested point exported, finite values and no duplicate bias points. Otherwise the verdict is `invalid (...)`, never a pass. `load` :189 and `strip_iv` :542 no longer crash on a run without an export. In the core rules, `bad_points` :223 (called by `gen_core` :619 and `mesh_core` :664) returns `invalid` for a non-finite V_G or required value, or for a bias point present in one run only. `strip_point` :548 rejects a non-finite current. |
| C4 | PROVISIONAL dropped (`hc_worst`) | `prov` :330 now applies to every verdict computed under the KCL PROXY or under a resolution that is not demonstrated, including unresolved ones. It covers: AFF shift and rigidity (:508-509), `hb_ratio`, `hb_transfer`, `hc_nominal`, `hc_generation`, `hc_mesh`, `hc_worst` (:765) and `hc_explains` (:822). The §7.1 floor criteria count a point valid above the §7.1 KCL limit, which *is* the proxy (`lim71` :338). So `floor_qualification` (:734) keeps `hc_worst` and `hc_explains` PROVISIONAL unless a demonstrated I_D-type resolution at or below that limit is given (`hc_explains` now accepts `--resolution`). |
| C5 | Mesh evidence not bound to its runs and scope | `hc_mesh` :687 requires a verified oxide y-mesh refinement of the reference, with the run being the refined one. Otherwise the verdict is `not demonstrated (...)`, and the comparison is kept only as `comparison_verdict`. The output records `inputs`, `evidence` (sha256 of both runs' files), `intervention` and `scope` (mechanism, film, oxide set and run pair; "does not certify: other films; ITAT; generation"). `mesh_convergence` :776 (used by `hc_explains`) re-scores the mesh JSON from its inputs and requires unchanged sha256 (:791). It counts the mesh JSON only for a mechanism run with the same mechanism and film as the S2-11 pair (:794). Another film and ITAT are never certified. A different oxide set inside that scope is disclosed. |

### 8.2 Judgement calls to review (none changes a registered rule)

1. **Which runs count as completed.**
   - KCL_FAILED stays scorable, with per-point censoring. The frozen R17 rule "KCL-censored at −3 V → unresolved" presupposes this.
   - SIGN_REVERSAL (e.g. run_0066) and every other non-accepted status is `invalid`.
   - A resolution pair needs accepted statuses only.
2. **Scope of an S2-11 verdict.** It follows Codex's wording: QTNLSC on the 2.0 nm film.
   - S2-04 (2.0 nm, *nominal* oxide set) is inside that scope. S2-11 refines the *worst*-set deck.
   - The set difference is disclosed in `convergence_evidence`, not refused.
   - If the oxide set should also be part of the scope, that needs a decision. Note that it would make H-C falsification by S2-04 impossible without a further refinement run.
3. **I_D-type resolution.**
   - Codex's list does not ask for a circularity rule, so none was added (the I_G-ceiling rule is unchanged).
   - Cross-film use is not refused. The pair's film is recorded (`pair_films_nm`).
   - Both points belong to the open resolution-method sign-off.
4. **Material-model identity in `intervention`.**
   - Checked against the S2-11 launch form without launching: the v3 model plus the S2-11 overrides dumps a `material_model_used.json` identical to run_0067's (sha256 974b23ea…, the RUN_INDEX model hash).
   - The dry-built `s2_prep_decks/S2-11` deck verifies as an oxide y-mesh refinement of run_0067: 2 statements, refined = run.
   - S2-04 is correctly rejected (`gate_tunnelling.set` is not a numerical knob).
5. **File binding.** A mesh or pair JSON becomes unusable when any bound run file changes, for example if a runner `rescore` rewrites `execution.json`. It must then be re-scored.

### 8.3 Selftest: 61/61

- **32 original cases:** all pass.
  - One was amended: "a resolution without a source is not demonstrated" (line 1011). Its second clause asserted that free text *with* a source is demonstrated, which is the behaviour C1 removes. That clause was taken out and inverted as rejection probe R1.
- **29 new cases** (`probes` :871). They use synthetic run directories in a temporary folder.
  - **R** = rejection probe (24). A broken implementation answers it wrongly.
  - **P** = positive or regression control (5).

| Kind | New selftest name |
|---|---|
| R | resolution: a free-text I_D source is not demonstrated (item 1) |
| P | resolution: a qualified DOS x2 pair JSON (distinct completed runs, verified intervention, file-bound) is demonstrated |
| R | resolution: a pair without a verified numerical intervention (physics override and deck change) is not demonstrated |
| R | resolution: a self-pair (one run twice) is not demonstrated |
| R | resolution: run files changed after the pair JSON was written (sha256 mismatch) are not demonstrated |
| R | resolution: a value below the pair candidate, NaN or negative is not demonstrated |
| R | resolution: a pair containing a timed-out run is not demonstrated |
| R | I_G ceiling: a self-pair of a gate-tunnelling run is not demonstrated (item 1) |
| P | I_G ceiling: a qualified oxide-mesh pair of gate-tunnelling runs not under test is demonstrated |
| R | nominal: a timed-out run with one exported -3 V point is invalid, never PASS (item 3) |
| R | nominal: a failed run (simulator error) is invalid, never PASS |
| R | nominal: a completed run with a NaN elsewhere in its export is invalid, never PASS |
| P | nominal: a completed run under a qualified I_G ceiling -> PASS (positive control) |
| R | CLI: a resolution cited with free text exits 2 (I_D-type and I_G ceiling; item 1) |
| R | generation: +5.4e-21 vs -5.4e-21 at R = 6e-21 is not consistent with 1e-20 (ceiling R_a + R_b = 1.2e-20; item 2) |
| R | generation: a NaN window current is invalid, never consistent (item 3) |
| R | S2-11: three resolved points plus a NaN point are invalid, never PASS (item 3) |
| R | S2-11: a NaN V_G is invalid, never PASS (item 3) |
| R | strip: a NaN in the export is invalid, never a ratio verdict (item 3) |
| R | hc_worst: a verdict under the KCL PROXY carries PROVISIONAL (item 4) |
| R | hc_explains: a verdict under the KCL PROXY carries PROVISIONAL (item 4) |
| R | AFF: the registered shift verdict under the KCL PROXY carries PROVISIONAL (item 4) |
| R | hc_nominal and hc_generation verdicts under the KCL PROXY start with PROVISIONAL (item 4) |
| R | S2-11 hc_mesh names its run pair, scope (QTNLSC, 2.0 nm) and file evidence (item 5) |
| R | S2-11 hc_mesh on a self-pair (no refinement) is not demonstrated, never PASS (items 1, 5) |
| R | S2-11 mesh evidence does not certify another film (13.2 nm QTNLSC run; item 5) |
| P | S2-11 mesh evidence certifies a 2.0 nm QTNLSC run (positive control) |
| P | S2-11 mesh evidence never certifies ITAT (S2-12/S2-13; regression) |
| R | S2-11 mesh score whose run files changed after scoring is not taken as convergence (item 5) |

**Mutation check.**
- **Method:** the same `probes(M, tmp)` was run with M = the pre-fix scorer (git HEAD copy, sha256 `519df51c…3c5e`).
- **Rejection probes:** **24/24 fail on the pre-fix code.** Every one fails by returning the wrong answer (e.g. PASS, "consistent", demonstrated = True, exit 0, converged = True), not by raising.
- **Controls:** 5/5 pass on both versions.
- **Reasons checked:** every rejection in the new code was printed and checked for its intended reason. Examples:
  - the self-pair is refused as "self-pair: the two runs are the same run";
  - the 13.2 nm run is refused as "outside the S2-11 scope (QTNLSC, 2 nm film …)";
  - the tampered mesh score is refused as "sha256 mismatch".
- **To reproduce:** load the HEAD copy as a module and call `score_register.probes(old_module, tmpdir)`.

### 8.4 Smoke set (run_0061..run_0074 only; all labelled *smoke test, not a registered result*)

The 12 previous outputs were moved to `register_scores/superseded_2026-10-12_codex_review/`. The set was re-run, and the outputs were compared field by field, ignoring the new evidence fields.

| Smoke test | Before → now | Why |
|---|---|---|
| `resolution_pair` run_0071/run_0061 (DOS ×2) | 3.28709e-18, unchanged | Now `qualified: true` (intervention: DOS grid, 2 deck statements, refined = run) |
| `resolution_pair` run_0070/run_0069 (mesh ×0.7) | 2.85347e-18, unchanged | `qualified: true` (mesh spacing factor, 19 statements) |
| `aff` run_0072/run_0061 | identical (+142.15 mV, 14 levels, PROVISIONAL NOT RIGID) | — |
| `he_alloff`, `s3_minus_s105` | identical (±0.14215 V) | — |
| `hc_nominal` run_0061 | "unresolved: below resolution …" → "PROVISIONAL (resolution not demonstrated): unresolved: …" | C4 prefix |
| `hc_nominal` run_0067, I_G source = the I_D pair JSON | FAIL (PROVISIONAL), exit 0 → **refused, exit 2** ("pair column id_A_per_um, not ig_raw_A") | C1 |
| `hc_nominal` run_0067, PROXY (replacement record) | "PROVISIONAL (resolution not demonstrated): FAIL" (\|I_G(−3 V)\| 2.75e-12 > 4.61e-17) | Same substance as before |
| `hc_generation` run_0071/run_0061, free-text source | unresolved, exit 0 → **refused, exit 2** | C1 |
| `hc_generation` run_0071/run_0061, source = the qualified pair JSON | Demonstrated. 0 resolved points; ceiling 3.29e-18 → **6.58e-18**; still unresolved (above the 1e-20 bound) | C2 (R_a + R_b) |
| `hc_mesh` run_0065/run_0067 (PROXY) | "PROVISIONAL …: FAIL" → **"not demonstrated (… no override differs: no numerical intervention)"**; the old FAIL is kept as `comparison_verdict` | C1/C5: two S0-02 repair attempts are not a refinement pair |
| `hc_mesh` run_0067/run_0067, free-text source | PASS → **refused, exit 2** | C1 |
| `hc_mesh` run_0067/run_0067, qualified pair JSON | PASS → **"not demonstrated (… self-pair …)"**; `comparison_verdict` PASS (identity) | C1/C5 |
| `hc_worst` run_0067/0061 as both films | unresolved → "PROVISIONAL (…; 7.1 floor validity rests on the KCL limit): unresolved …" | C4 |
| `hc_explains` run_0067/run_0061 | "does not explain the floor" → the same with the PROVISIONAL prefix | C4 |
| New: `hc_nominal` run_0073 (TIMEOUT), run_0062 (SIMULATOR_ERROR), `hc_mesh` run_0066 (SIGN_REVERSAL)/run_0067 | `invalid (…)` (before: crash on the missing CSV, or scored) | C3 |

Every change is explained by C1-C5. No number changed except the generation ceiling (C2).

### 8.5 Files

- `analysis_2026-10-10_campaign/score_register.py`:
  - before: 611 lines, sha256 `519df51cb5e26c4aded5f542e387653d3cf1046410c32ded60024178849d3c5e`;
  - after: 1095 lines, sha256 `da4da6918d8cf001c88eee5f98a032500086b413b955af8ef8f49718aa0cb690`. **Superseded by §9; do not freeze (Codex re-review).**
- `register_scores/`: 15 new smoke JSONs. The 12 previous ones are in `superseded_2026-10-12_codex_review/`.
- This file.

**Still open:**
- The resolution method needs the user's sign-off as a logged amendment. It must be frozen before the S2-11 outputs are unsealed (Codex 13:18Z (c)).
- The executable DIAG stop gates (Codex §4) are not part of this change.

## 9. Re-review fixes (Codex re-review 2026-10-12 ~15:28Z: GO-WITH-CHANGES, do not freeze da4da691)

*This section implements Codex's re-review: fixes 6-8 and rulings (a)-(c). No registered rule text, threshold or band changed.*

**Same rules as §8.**
- No launch.
- Nothing from S2-11 or `results/sealed/`; only run_0061..run_0074 and synthetic data. RUN_INDEX was not read in this round.
- `scripts/run_campaign.py` and `post_run_checks.py` were not changed (checked with `git status`).
- No commit.
- The frozen register-text block of the docstring is still byte-identical.
- New docstring items are marked [C6]..[C8] and [Ruling a/b/c] (lines 38-110).

### 9.1 Fixes

| # | Codex finding | Fix (file:line in the new `score_register.py`) |
|---|---|---|
| 6 | KCL censoring does not reach `hc_worst` (`floor_metrics` ignores `kcl_pass`) | New `floor_metrics_masked` (:860) inside the scorer. `post_run_checks.floor_metrics` is not touched, so its other callers keep their behaviour. It reproduces post_run_checks with censoring applied first. A KCL-failed run point is never valid and never enters a slope, ratio or control subtraction. `ctrl_at` (:846) takes the control's own KCL-passed point, or interpolates only between two KCL-passed neighbours. It never interpolates across a censored control point or extrapolates: such a point is *unsupported*. Below the existing support minima (slope ≥ 3 valid points, ratio ≥ 1 supported point) the metric is None and its sub-result *unresolved*. Used by `hc_worst` (:914), `hc_explains` (:981) and `leak_slopes` (:889). In `hc_explains`, censored or unsupported window points give "unresolved (insufficient support …)" (:1004) unless the valid fraction fails even with every censored point counted valid. The registered KCL criterion still blocks falsification. |
| 7 | Resolution qualification can be vacuous (all points disagree, `qualified = True`) | `resolution_pair` (:541; :570 for the support rule) qualifies only with agreement support and full bias coverage; the frozen values are in §9.3. The JSON reports `support_points_above_candidate`, `support_points_within_1dec`, `bias_coverage` and `support_rule`. An entirely disagreeing pair demonstrates nothing. |
| 8 | Refinement direction taken from overrides, not deck values (masked) | `intervention` (:469) compares the **actual deck values**. Only one kind of knob may change, and the statement count and order must match. Exactly the lines that knob sets must change, each by the ratio the overrides claim (`RATIO_RTOL` 1e-3; :521):<br>• oxide factor: only the y.mesh lines at `OXIDE_LINES_UM` = 0.002 and 0.017 µm, never y = 0 (from `build_iwo_decks.py:311-312`);<br>• mesh factor: every x/y.mesh line;<br>• DOS: numa and numd on every defects line.<br>The refined run is the one with the smaller actual spacing or more DOS levels. A coarsening deck under a "×0.5" override is refused. |

### 9.2 Rulings

- **(a) Run validity:** already implemented. Completed KCL_FAILED runs are scored with pointwise censoring, which now also reaches the floor metrics (fix 6). SIGN_REVERSAL runs stay invalid.
- **(b) Same oxide set for convergence:** `mesh_convergence` (:952, check at :973) certifies only a mechanism run with **exactly the physical settings of the S2-11 reference**. Those settings are film, oxide set and every other non-numerical override, the material model and the deck (`settings`, :448). The worst-set S2-11 therefore does not certify the nominal S2-04, which stays *convergence not demonstrated*. `hc_mesh` (:813) records these settings in its `scope`.
- **(c) Application scope, frozen** (`qualify` :332):
  - **Same quantity, film, settings and bias range:** a resolution applies only to its own quantity (`id_A_per_um` or `ig_raw_A`), its own film and physical settings (:367), and its compared V_G range. This holds for **every** run it is applied to. `load` (:215) records each run's directory and V_G range for this check.
  - **No cross-film transfer.**
  - **Independence:** a pair that contains a tested run is refused as ceiling evidence for the upper-bound tests `hc_nominal` and `hc_generation` (:359, :776). Such a pair stays usable for non-upper-bound uses (AFF, hb_*, §7.1 floor validity, `hc_mesh`), as ruling (c) allows.
  - **`hc_mesh`:** it refuses only its own pair, as circular (:832). An I_D-type resolution is out of scope for its I_G quantity (:833).

### 9.3 Frozen support and coverage values (part of the resolution-method sign-off)

| Constant | Value | Why |
|---|---|---|
| `RES_SUPPORT_MIN` | 3 | Minimum number of agreeing points with both currents above the candidate R. It is the minimum count already used in this scorer (AFF ≥ 3 levels, S2-11 ≥ 3 points resolved in both runs, floor slope ≥ 3 points). It is the smallest count that is not a single or paired coincidence, for a claim made about every current above R. |
| `RES_NEAR_DEC` | 1 decade | At least one supporting point must lie within one decade above R. Otherwise the claim at R is extrapolated across a gap with no evidence. *Disclosure:* both existing numerical pairs have exactly one supporting point in that first decade (S1-04 DOS ×2: 48 support points in all; S1-03 mesh ×0.7: 56). So 1 decade is the tightest value they satisfy, and it was chosen knowing those already-seen pairs. No S2 data were involved. |
| `RES_BIAS_COVERAGE` | 1.0 | Every bias point of both runs is compared (full sweeps only). The compared V_G range is the scope's supported bias range. |
| `RATIO_RTOL` | 1e-3 | Deck ratio against the claimed ratio. Deck numbers are printed with 6 significant digits. |
| `OXIDE_LINES_UM` | (0.002, 0.017) | y = t_Al2O3 and t_Al2O3 + t_HfO2 (generator). The y = 0 line is never part of the oxide intervention (R13). |

### 9.4 Selftest: 77/77

- **Totals:** 32 original cases plus 45 review cases. The 45 are 39 rejection probes (24 from round 1, 15 new) and 6 controls.
- **New in this round (16):**

| Kind | Name |
|---|---|
| R | S2-11 (worst oxide set) does not certify a nominal-set 2.0 nm QTNLSC run such as S2-04 (ruling b) |
| R | scope: a 2.0 nm resolution is not applied to a 13.2 nm run (no cross-film transfer; ruling c) |
| R | scope: a resolution is not applied to a run with other physical settings (gate tunnelling on; ruling c) |
| R | scope: an I_D-type resolution is not applied to the I_G quantity of S2-11 (ruling c) |
| R | scope: a pair containing the tested runs is no independent ceiling evidence for the generation upper-bound test (ruling c) |
| R | scope: a resolution from a pair compared on V_G >= -1 V is not applied to a run swept from -3 V (supported bias range; ruling c) |
| R | pair: an entirely disagreeing verified pair (1e-23 vs 1e-21 at every bias) demonstrates nothing (fix 7) |
| R | pair: agreement only 12 decades above the candidate (no support within 1 decade) demonstrates nothing (fix 7) |
| R | pair: a pair comparing only half of the bias points (coverage 0.52 < 1) demonstrates nothing (fix 7) |
| R | intervention: overrides claim oxide x0.5 but the deck spacings coarsen x2 -> not a refinement, never a mesh pass (fix 8) |
| R | intervention: the y = 0 IWO interface line also changed -> not the claimed oxide-line intervention (fix 8) |
| R | intervention: overrides claim DOS x2 but the deck numa/numd are x4 -> not verified (fix 8) |
| R | hc_worst: a flat curve with one KCL-failed endpoint raised ten decades is flat, never a PASS (fix 6, Codex counterexample) |
| R | hc_worst: no control subtraction across KCL-censored control brackets; insufficient support -> unresolved, never PASS (fix 6) |
| R | hc_explains: a KCL-censored window point leaves the 7.2 criteria unestablished -> unresolved, not "does not explain" (fix 6) |
| P | masked floor metrics equal post_run_checks.floor_metrics when nothing is censored (regression) |

- **Round-1 probes changed:**
  - **"certifies a 2.0 nm QTNLSC run":** its synthetic run used the nominal set, so under ruling (b) it became the first R probe above. It was replaced by the control "certifies a 2.0 nm QTNLSC run with the same physical settings".
  - **Scored runs now loaded:** round-1 probes now pass their scored runs through `load`, so the scope check sees them.
  - **S2-11 mesh probes:** they now use an in-scope I_G ceiling pair. The I_D DOS pair is out of scope for I_G under ruling (c).

**Mutation check** (same probes on earlier versions; synthetic data):

| Version | Rejection probes failing | Failing by exception | Controls passing |
|---|---|---|---|
| Pre-fix `519df51c…` | 39/39 | 0 | 6/6 |
| Round-1 `da4da691…` | the 15 new ones (15/39; the 24 round-1 probes pass, as they should) | 0 | 6/6 |

- The new code's stated reason was printed for every new rejection and checked.
- Examples:
  - S2-04 is refused by "overrides [gate_tunnelling.set=nominal] vs [set=worst]";
  - the coarsening deck by "deck spacing ratio 2 … differs from the claimed 0.5";
  - Codex's endpoint counterexample now gives slope 2e-15 dec/V: flat, so FAIL, not PASS.

### 9.5 Checks on real data (run_0061..run_0074 only)

- **Masked metrics equal post_run_checks on uncensored runs:** `floor_metrics_masked` was compared with `post_run_checks.floor_metrics` on 8 real run/control pairs (26 values compared, maximum difference 0, `verdict_inputs` equal).
- **Interventions verified from the real deck values:**
  - S1-04/S0-01: DOS ratio 2.0/2.0 on 2 defects lines, refined = run.
  - S1-03/S1-02: ratio 0.7 on all 19 mesh lines, refined = run.
  - Dry-built `s2_prep_decks/S2-11` against run_0067: ratio 0.5 on exactly the two oxide lines, refined = run. Its settings are identical to run_0067's, so it is in scope.
  - Dry-built S2-04 is refused.
  - run_0065/run_0067 is refused (no intervention).

### 9.6 Smoke set (re-run; round-1 outputs moved to `register_scores/superseded_2026-10-12_codex_rereview/`)

| Smoke test | Round 1 → now | Why |
|---|---|---|
| `resolution_pair` run_0071/0061 and run_0070/0069 | Still qualified, same candidates (3.28709e-18, 2.85347e-18). New fields: support 48 / 56 points, 1 within a decade each; coverage 1.0; scope V_G [-3, 3]; deck ratios 2.0 / 0.7 | Fixes 7, 8 |
| `aff`, `he_alloff`, `s3_minus_s105`, the 4 `hc_nominal`, `hc_mesh` run_0065 and run_0066 | identical (only the `hc_mesh` resolution label text changed) | — |
| `hc_worst` run_0067/0061 | Same verdict. Sub-result text now reads "insufficient support: 2 valid uncensored floor points < 3"; censored lists empty | Fix 6 (no censoring in these runs, so same numbers) |
| `hc_explains` run_0067/0061 | Same verdict ("does not explain", 12.5 % valid); new censoring fields empty | Fix 6 |
| `hc_generation` run_0071/0061 with the DOS pair | demonstrated (ceiling 6.58e-18) → **refused, exit 2**: the pair contains the tested runs. Record re-run under the PROXY: PROVISIONAL unresolved | Ruling (c), independence |
| `hc_mesh` run_0067/0067 with the DOS pair | not demonstrated (self-pair) → **refused, exit 2**: I_D resolution out of scope for I_G. PROXY record: still "not demonstrated (self-pair)" | Ruling (c), quantity |
| `aff` run_0072/0061 with the DOS pair (new) | **refused, exit 2**: run_0072 (S1-05) has other settings (nc300 override) | Ruling (c), settings |
| `hc_explains` run_0071/0061 with the DOS pair (new; in scope, not an upper-bound use) | "does not explain the floor" **without** PROVISIONAL: a demonstrated resolution 3.29e-18 below the §7.1 limit | The in-scope path works on real data |
| free-text sources; the I_D pair cited as an I_G ceiling | refused, exit 2 (as round 1) | — |

### 9.7 Consequences that need a decision (nothing changed here)

1. **Under rulings (b) and (c), almost every primary S2/AFF verdict will be PROVISIONAL or unresolved with the current run plan.** A demonstrated verdict needs a refinement pair with the same quantity, film, physical settings and bias range; for an upper-bound test, the pair must also contain no tested run.
   - **What exists:** I_D resolutions for the S0-01 settings (S1-04 pair, 2.0 nm) and the S1-02 settings (S1-03 pair, 13.2 nm) only. No I_G resolution exists at all.
   - **S2-11:** its verdict will be PROVISIONAL. It needs an I_G ceiling with run_0067's settings that is not the S2-11 pair itself, and none exists. One option is one more numerical refinement of S0-02, e.g. DOS ×2. It would form an in-scope I_G pair, allowed for this non-upper-bound use.
   - **S2-04 / S2-06 nominal:** each film needs an independent, nominal-set I_G refinement pair (two runs, neither S2-04 nor S2-06).
   - **S2-01 / S2-02 generation:** the two runs have different settings, so they need two independent pairs. They also need a second, per-run resolution input; `gen_core` already takes `res_b`, but the CLI input is not implemented.
   - **H-C falsification through QTNLSC:** with the current plan, convergence cannot be certified for any registered entry (S2-04 is the nominal set; S2-06 and S2-08 are 13.2 nm).
   - **AFF, hb_* and hc_worst:** no in-scope pair exists, so they stay PROVISIONAL.
   - Adding runs is a plan change: a logged amendment and the user's decision.
2. **Independence rule for `hc_mesh`.** It applies ruling (c)'s "a pair containing the tested run may establish that run's refinement stability". `hc_mesh` therefore accepts an I_G pair containing run_0067 (or S2-11) through another verified intervention. It refuses only its own pair. Round 1 refused any pair containing either run. Please confirm.
3. **`hc_explains` label.** Censored or unsupported support now reads *unresolved* instead of *does not explain*. Both mean "no falsification from this run".

### 9.8 Files

- `analysis_2026-10-10_campaign/score_register.py`: 1342 lines, sha256 `6651044e48270ff3511749f7d596fe6a830bb45fd59c78c6d54bdb94a61fdc7d`. It supersedes da4da691. **Superseded by §10; do not freeze (Codex round 3).**
- `register_scores/`: 16 smoke JSONs, one of them new (`smoke_hc_explains_run_0071_run_0061.json`). The round-1 outputs are in `superseded_2026-10-12_codex_rereview/` (15).
- This file: §9 appended.
- The mutation and reason scripts are in the session scratchpad, not the repository. To reproduce, call `score_register.probes(M, tmpdir)` with M = the pre-fix or round-1 file loaded as a module.

## 10. Round 3 (Codex ~15:55Z: fixes 6-8 accepted; do not freeze 6651044e)

*This section implements Codex's round 3: fixes 9-11 and the round-3 rulings, plus one defect found here and disclosed (§10.2). No registered rule text, threshold or band changed.*

**Same rules as §8 and §9.**
- No launch, no commit.
- Nothing from S2-11 or `results/sealed/`; only run_0061..run_0074 and synthetic data.
- `scripts/run_campaign.py` and `post_run_checks.py` unchanged (checked with `git status`).
- Frozen register-text block of the docstring still byte-identical.
- New docstring items: [C9]..[C11] and [Round 3 rulings] (lines 40, 71-80).

### 10.1 Fixes

| # | Codex finding | Fix (file:line in the new `score_register.py`) |
|---|---|---|
| 9 | Numerical-scope guard: masked settings let a DOS 384/192 vs 768/384 pair qualify a target run with DOS 1/1 | `qualify` (:368; :411-419). Each scored run's **actual** numerical settings must equal one pair endpoint's: `numerics` (:363) is the sha256 of the deck statements with every value unmasked, and the endpoints are recorded in `application_scope` (:636). Otherwise the result is "a separate qualification is needed". This applies to every use except `hc_mesh`: the upper-bound tests (`hc_nominal`, `hc_generation`), the floor-validity (ceiling) use in `hc_explains`/`hc_worst`, and AFF and hb_*. `hc_mesh` (`refine_ok`, :896) may instead use a target that is a **verified, componentwise finer** refinement of an endpoint (`intervention`, refined = target). An unverified or coarser target grid is refused. |
| 10 | Componentwise refinement: DOS 768/96 vs 384/192 was verified with refined = 'mixed' | `intervention` (:590): 'mixed' (one grid finer, one coarser) is not verified, so it is never refinement evidence. |
| 11 | Per-run resolution inputs | `role_res` (:348). Per-run (per-curve) resolutions for `hc_generation` (:834; roles run and control), `hc_explains` (:1058; run, control) and `hc_worst` (:989; run, control, run_2p0, control_2p0). The CLI flags are `--resolution-<role> R --resolution-<role>-source PAIR.json` (:1442). Each run is scope-checked on its own: quantity, film, settings, bias range and numerical endpoint. The upper-bound independence check covers all tested runs. A set with a missing (or inapplicable) role, or one mixed with a single `--resolution`, is refused with exit 2 (:1455; under strict, also in the functions). The subtraction still uses R_a + R_b (:847). `floor_qualification` (:976) is now per run, each against the §7.1 limit of its own film. |

### 10.2 Defect found and fixed in this round (not raised by Codex)

`gen_core`, generation upper-bound verdict (:825).
- **Rule:** the documented rule allows FAIL only when a resolved lower bound exceeds 1e-20.
- **Defect:** the code passed the largest upper bound to `censored_upper`. A point resolved in one run only, with lower bound x − R ≤ 1e-20 < upper bound x + R, was therefore scored FAIL. The defect has been present since the original scorer (pre-fix line 386).
- **Fix:** such a point is now *unresolved*, never FAIL.
- **Smoke impact:** none; the real smoke pair has no such point.
- **New rejection probe:** it fails on all three earlier versions.

### 10.3 Rulings recorded

- **Support values:** 3 agreeing points above the candidate, one of them within a decade, full bias coverage, ratio tolerance 1e-3.
  - They are accepted as an **ASSUMED operational method**.
  - Disclosure: the one-decade value was chosen with the already-seen S1 pairs (S1-03, S1-04). It is prospective for S2, not a blind validation of S1.
  - Pair agreement establishes **numerical stability under the tested intervention, not an absolute error bound**. Every demonstrated statement now says so (`qualify` :368).
- **`hc_mesh` rule, confirmed with the numerical-scope guard:**
  - A DOS comparison and the oxide-mesh comparison may share run_0067. The output records this in `resolution_pair_relation` (:902): the resolution pair, the mesh pair, `shared_baseline` and `independent: false`, with a note that it is not independent evidence. The two comparisons are never called independent.
  - The exact pair under test can never provide its own resolution (`forbid_pair`).

### 10.4 Selftest: 90/90

- **Totals:** 32 original cases plus 58 review cases. The 58 are 48 rejection probes and 10 controls.
- **New in this round (13):**

| Kind | Name |
|---|---|
| R | numerics: a DOS 384/192 vs 768/384 pair does not qualify a target run with DOS 1/1 (fix 9, Codex counterexample) |
| R | numerics: hc_nominal (upper bound) on a DOS 1/1 run is not demonstrated by the 384/192 vs 768/384 I_G pair, never PASS (fix 9) |
| R | numerics: the floor-validity (ceiling) use in hc_explains on a DOS 1/1 run is not demonstrated (fix 9) |
| R | numerics: hc_mesh refuses an I_G pair made on a finer global mesh (target S2-11/S0-02 grids coarser than both endpoints; fix 9) |
| R | numerics: hc_mesh refuses a target grid that differs from the pair endpoints by an unverified change (y = 0 line, no override; fix 9) |
| R | hc_mesh: a DOS pair sharing run_0067 with the S2-11 comparison is accepted via the verified refinement route, recorded as a shared baseline, never independent (round 3 ruling) |
| P | hc_mesh: the exact pair under test cannot provide its own resolution evidence (regression) |
| R | intervention: DOS 768/96 vs 384/192 (one grid finer, one coarser) is not a verified refinement and demonstrates nothing (fix 10) |
| R | CLI: per-run resolution inputs with a role missing (hc_generation control; hc_worst control_2p0) exit 2 (fix 11) |
| P | per-run: hc_generation with its own in-scope independent pair for a gated mechanism and an ungated control is demonstrated (R_a + R_b; fix 11) |
| P | per-run: hc_explains with per-run in-scope pairs has non-PROVISIONAL floor criteria (fix 11) |
| P | per-run: hc_worst with four per-run in-scope pairs across two films is non-PROVISIONAL (fix 11) |
| R | generation: a one-sided point with lower bound 5e-21 <= 1e-20 < upper bound 2.5e-20 is unresolved, not FAIL (defect found in round 3) |

- One round-2 probe was adapted because `resolution_source` is now a per-run dict.

**Mutation check** (same probes on earlier versions; synthetic data):

| Version | Rejection probes failing | Failing by exception | Controls passing |
|---|---|---|---|
| Round-2 `6651044e…` | **9/48: exactly the 9 new ones** (24 round-1 and 15 round-2 probes pass, as they should) | 0 | 7/10 |
| Pre-fix `519df51c…` | **48/48** | 1 (its `hc_explains` has no resolution argument) | 7/10 |
| Round-1 `da4da691…` (for completeness) | 24/48 | 0 | 7/10 |

- **Controls:** the 3 per-run controls use the new `per_run` API, so they raise on every earlier version (not applicable there).
- **Reasons checked:** the new code's stated reason was printed for every new rejection and checked. Examples:
  - for the DOS 1/1 target, "its actual numerical settings (deck values) equal neither pair endpoint; a separate qualification is needed";
  - for the coarser and unverified targets, "neither a pair endpoint nor a verified finer refinement of one";
  - for the mixed pair, "not a componentwise refinement: DOS ratios numa 2, numd 0.5";
  - the shared-baseline case passes through "run_9911: verified oxide y-mesh factor refinement (finer, deck ratio 0.5) of endpoint run_0067".

### 10.5 Smoke set (run_0061..run_0074 only; round-2 outputs moved to `register_scores/superseded_2026-10-12_codex_round3/`)

| Smoke test | Round 2 → now | Why |
|---|---|---|
| `resolution_pair` ×2, `aff`, `he_alloff`, `s3_minus_s105`, 4 × `hc_nominal`, 3 × `hc_mesh` | identical | — |
| `hc_generation` run_0071/0061 (PROXY), `hc_worst` run_0067/0061 ×2, `hc_explains` run_0067/0061 and run_0071/0061 | Same values and verdicts. The resolution fields are now per-run dicts, and the PROVISIONAL reason names the roles | Fix 11 (format) |
| `hc_generation` run_0071/0061, per-run inputs (new) | **refused, exit 2**: each per-run pair contains the tested runs, so it is not independent | Ruling (c) per run |
| `hc_explains` run_0071/0061, per-run inputs (new) | Demonstrated, same as the single-input form ("does not explain", no PROVISIONAL) | Fix 11 |
| `hc_explains` run_0067/0061, per-run inputs (new) | **refused, exit 2**: run_0067 (gated) is outside the DOS pair's settings | Fix 11 / ruling (c) |
| `hc_worst` run_0070/run_0069/run_0071/run_0061, four per-run inputs (S1-03 pair for 13.2 nm, S1-04 pair for 2.0 nm; new) | **demonstrated, non-PROVISIONAL**: "unresolved (neither criterion fails and at least one could not be evaluated)" | Fix 11 on real data |
| The same with the control_2p0 input missing (new) | **refused, exit 2** | Fix 11 |
| The earlier refusals (free text, I_D pair as I_G ceiling, non-independent pair, I_D for I_G, AFF settings) | still exit 2 | — |

### 10.6 Files

- `analysis_2026-10-10_campaign/score_register.py`: 1486 lines, sha256 **`c0f28bb942508a81a0f59b4a4c1e720bbfdbe8d9466d7e002476d64dcc10b55a`**. It supersedes 6651044e.
- `register_scores/`: 17 smoke JSONs, one of them new (`smoke_hc_worst_run_0070_run_0069_run_0071_run_0061.json`). Earlier sets are in `superseded_2026-10-11_review/`, `superseded_2026-10-12_codex_review/` (round 0), `superseded_2026-10-12_codex_rereview/` (round 1) and `superseded_2026-10-12_codex_round3/` (round 2).
- **Still open:**
  - §9.7 (needs matched refinement runs to make primary verdicts demonstrated; a plan change) is unchanged by this round.
  - Per-run inputs remove the "one source for two settings" obstacle, but each run still needs its own in-scope, numerically matched (and, for upper-bound tests, independent) pair.
