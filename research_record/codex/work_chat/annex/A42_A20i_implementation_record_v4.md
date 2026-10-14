# A20(i) implementation record, version 4: H-L spin-polarised single points (staged, NOT submitted; annex of the draft amendment A42)

- **Version 2:** 2026-10-13T03:07Z by Claude (DFT side), after two internal reviews of version 1 (both GO-WITH-CHANGES; section 13). Version 1 (02:20Z, sha256 aff3c5d070c0df605f75dc95fc393d1e4f4dc651c79f7fcf0c3782a03b25dd33) is kept locally in `v1_backup_20261013T0220Z/` and on lxplus in `a20_spin/v1_superseded_20261013T022045Z/`.
- **Version 3:** 2026-10-13T03:55Z by Claude (DFT side), after the Codex reply to the 03:26Z digest (H-L logging GO; A20(i) GO-WITH-CHANGES, FIX_FIRST before freezing the comparator or submitting). Changed: the comparator (v3: the Condor disposition of the bound job vetoes counting for attempt 1 and the fallback; each attempt bound to its submitted cluster.proc from the saved `condor_submit` stdout; only the bound job's events, in log order; missing or ambiguous evidence -> start UNRESOLVED; labels for a higher-energy A trigger and a missing B; wording), its tests (rejection tests written first: 27/40 on the v2 comparator, 40/40 on v3), the submit-file comments, the README and this record (§3 seed units, §4, §6, §7, §11-§14). **Inputs, manifest, jobs.txt, builder and the functional submit-file lines are unchanged.** Version 2 (sha256 aa9730fdac1d8013ee73e5437af7edc564b1d97d4a8a4e41e54fda51563f4daa) is kept locally as `v2/A20i_implementation_record_v2.md`; the v2 comparator files on lxplus in `a20_spin/v2_comparator_superseded_20261013T0355Z/`.
- **Version 4:** 2026-10-13 by Claude (DFT side), after the Codex reply on the A42 draft (FIX_FIRST: two event-policy counterexamples). Changed: the comparator (v4: a removal is a system removal only with evidence in its reason, SYSTEM_PERIODIC_REMOVE / PeriodicRemove; a missing or unrecognised reason, or "by user condor", is UNRESOLVED with no fallback; the permitted hold/release sequence is enforced before a termination is accepted), its tests (rejection tests written first: 42/47 on the v3 comparator, 47/47 on v4), the submit-file comments, the README, the budget wording (§8) and this record (§0, §6, §7, §8, §11, §13, §14). **Inputs, manifest, jobs.txt, builder and the functional submit-file lines are unchanged.** Version 3 (sha256 16a5fb1f8dd4021fd1c3172035129825fcdcd360657e5abc2df2060402b25d34) is kept locally in `v3_backup_20261013/`; the v3 staged tree in `v3/`. **lxplus still holds the v3 staged files; v4 is local only** (installing it needs the user's go; lxplus was not touched).
- **What changed from v1 (in v2):** the evaluation rules (sections 4-6), the comparator, the manifest metadata (pseudo md5s, canonical geometry hashes, rule fields), the submit-file comments and the README. **The 24 staged inputs are byte-identical to v1** (checked on lxplus with `cmp` before anything was replaced).
- **Staged at:** lxplus `~/iwo_amorph/checks/gpumax_work/a20_spin/`: `BUILD_v2_20261013T030746Z.txt` (final), `BUILD_v2_20261013T030503Z.txt` (in `v2_draft_20261013T030503Z/`, with the canonical-geometry and parser checks), `MD5SUMS`, dry-run ads `dryrun_v2_20261013T030746Z.ad` and `dryrun_v2_fb_20261013T030746Z.ad`, `README.txt` ("NOT SUBMITTED").
- **Jobs:** 12 (6 cells x 2 seed starts), one HTCondor cluster, 1 GPU each. Fallbacks, if needed, are a second cluster (section 6).
- **Submission:** nothing has been submitted. Before any `condor_submit`: amendment A42 (`A42_A20i_amendment_draft.md`, this record as its annex) is logged with decision D-45 after Codex review of the final text and the user's go; submission after the GPU pause (Codex).
- **Scope:** crystalline cells only (`vac/`, `checks/gpumax_work/a20_g002`, the new `a20_spin`). No amorphous file was opened and no git repository was touched.

## 0. Disclosure (to be quoted wherever A20(i) is reported)

> The A20(i) implementation choices recorded here were fixed on 2026-10-13 (version 1 at 02:20Z, version 2 at 03:07Z after internal review, version 3 at 03:55Z after the Codex review: comparator binding and counting fixes, labels; version 4 later on 2026-10-13 after the Codex review of the A42 draft: removal-reason evidence and the hold/release sequence), **after** the H-L k3/k4 and A20(ii) energy differences had been read (2026-10-13 00:25-00:31Z). They are therefore result-informed. They were frozen, and the comparator was hashed, before any A20(i) spin output (H-L settings) existed. A stage-4 In31WO48 spin-polarised output with different settings (QE 7.5 on CPU, MV 0.01 Ry, k 3x3x3: M_tot 0.62 muB/cell, 19.5 meV below its nspin=1 energy) was read during the design and informed start B. The result-informed choices are: the seed sites and values of both starts; the second start; the split-label species; the primary cell energy min(E_A, E_B, E_nspin1); the additive trigger rule over the primary and the registered start-A readings, with min(A,B) and B-only reported only; the branch and metastable flag definitions; the split-label equivalence gate and its precedence over triggers; the "registered start A incomplete" outcome; the 2026-10-17T10:00Z deadline for A20(i); the single fallback (A28-style mixing, new for A20(i)), its mechanical list and its single go; the removal, pause and monitoring rules; the submission-record binding and the disposition rule for counting (v3); the removal-reason evidence rule and the hold/release sequence rule (v4); the labels "not robust to the registered spin-start branch; metastable start" and "second-start sensitivity unresolved" (v3); and the comparator. The registered A20(i) text (A20, 2026-10-10T20:42Z) is unchanged.

The stage-4 run (`qe_workflow/cern_htcondor/results/iwo_W24d/spin_k3.out`, 2026-09-29): QE 7.5 CPU, MV 0.01 Ry, conv_thr 1e-9, k 3x3x3, `starting_magnetization(W) = 0.5`, beta 0.2; converged in 26 iterations to M_tot 0.62 and |M| 0.72 muB/cell, W-site moment 0.20, 1.43 mRy (19.5 meV) below the stage-4 nspin=1 k3 relax-final energy. It is a different-settings number, not an H-L number.

## 1. Registered text and the conditions this record meets

**Register A20(i), verbatim:** "a spin-polarised single point (nspin = 2, small starting magnetisation on W and its O neighbours, total magnetisation free) on the relaxed geometries of all six cells, k 3x3x3, 1 GPU (A100 allowed); ΔE_local and ΔE_dop recomputed; robustness: a shift > 50 meV in a registered difference or a verdict flip -> H-L 'not robust'; the registered score is still shown". Valence electrons: In32O48 704, In31WO48 705, In32O47 698, In31WO47_* 699 (In 13, W 14, O 6).

| Condition (source) | Section |
|---|---|
| Freeze seeds, neighbour selection, identical settings, failure handling before any spin output (Codex) | §2, §3, §6 |
| Meaningful seed for the undoped vacancy; total magnetisation free; "a single start tests one branch" (Codex) | §3, §2, §4 |
| Bind the archived input geometries; energy equality is not geometry evidence (Codex) | §1a |
| Disclose the post-result timing (Codex; review 2 blocking 3) | §0 |
| nspin=1 state inside the primary energy (review 1 blocking) | §4 |
| Triggers only add; the registered start-A reading can trigger (review 2 blocking 1) | §4 |
| Log as a result-informed amendment before submission (review 2 blocking 2) | §12 |
| No discretionary retry routes (review 2 blocking 4; review 1 minor) | §6 |

### 1a. Geometry binding (every cell; no energy is used as geometry evidence)

- **Bound structure (a):** the `Begin/End final coordinates` block of `vac/<cell>/relax.out` (one `bfgs converged` line per file) with the relax.in cell (fixed-cell relaxations, a = 10.3060902 A). For the four vacancy cells this block is identical (Δ = 0) to the last BFGS geometry printed before it, which is the geometry of the last '!' energy, E_REF (section 5). So E_REF and the staged positions refer to the same structure.
- **Canonical geometry sha256** (geometry_binding.md: CELL_PARAMETERS + ATOMIC_POSITIONS, numbers re-printed `%.10f`) was recomputed on lxplus on 2026-10-13T03:05Z from the actual files: (a) = `vac/<cell>/scf.in` (k4 FINAL input) = every staged input (attempt 1 and fallback, starts A and B; labels O1/In1 normalised to O/In), and = the value frozen in the manifest. Result: **BOUND for all six cells** (BUILD_v2_20261013T030503Z). The builder also asserts it for every input it writes.
- **Rolling relax.in (caveat):** `steps_relax.sh` overwrites `vac/<cell>/relax.in` with the converged geometry before packing, so relax.in equals (a) by construction and is **not** independent evidence; v1 cited it, v2 does not. The relaxation starts are bound from the pw.x header positions, the built `.xyz`, and parent (a) minus one O (geometry_binding.md section 2).
- **near (O30) A28 lineage:** attempt 1 (DAG 12886356; RELAX 12886362, inferred by elimination) started from In31WO48 (a) minus O30 exactly (`attempt1/relax.in` md5 1dbac6b93ae28ee094ecea35cd7c7256, canonical 80e8ccb43889b2e5...) and failed at BFGS geometry 3 (s0 archive `attempt1/relax_s0_results.tar.gz` md5 ef8b9bcc8968eddff09d4c69f663877b, sha256 1d414b8b4a5d6b64...). Restart 1 (DAGMan 12892680, RELAX 12892681) started from attempt-1 geometry 2 exactly (`a28_staging/relax.in.A28` md5 0dbaae0253e27a7fa93755019d120bdf = MANIFEST.md5, sha256 afbc59b4debc43b0...; canonical 6d2572e3976e8108...) with the A19 settings unchanged; it converged ('bfgs converged in 19 scf cycles and 18 bfgs steps'). **The A28 fallback was not used.**

| Cell | Atoms | e- | canonical (a) sha256 (first 16) | `vac/<cell>/scf.in` md5 | `relax.out` md5 | `scf.out` md5 | QE BFGS steps |
|---|---|---|---|---|---|---|---|
| In32O48 | 80 | 704 | 4a38745af874a820 | f07243438cfa7870fad7ee8118c92e71 | ec532bce6f2d381440460a16e57fd797 | 331a91dac6ebab255989b74b9338729f | 0 |
| In31WO48 | 80 | 705 | 190b69fd7895d167 | c7861e1f35254d9e7fcbe8a9df8ed2d3 | fee15ef06369c21a7a77bf388eb1a451 | 0b38b421e054a171e53fd9adb9f75c1b | 0 |
| In32O47 | 79 | 698 | 22d5673303e3e6ca | e5d64dc63f2ca6438b965e6eaeb054fb | 634f627f9da7a761be08a0d090194019 | ca6125f24b7f6a526f8f775a758469fd | 13 |
| In31WO47_far (O32) | 79 | 699 | d1904a6a7e039809 | 082a00f6a6bc0b2a34cb82982c3dd885 | a8f04a195f36ab10da844c594c5ca86c | 6db225cc1c1eb62bee469eccda90e72d | 16 |
| In31WO47_near (O30, registered) | 79 | 699 | db53075a4ec265a6 | 19e95727cf027c5836ea4b13d10452fa | 0eef1518151c028cd504fa23d258e489 | cac699c8374119223222702392c2bbaa | 18 (restart 1) |
| In31WO47_near72 (sensitivity) | 79 | 699 | 00588209500d4887 | 02ef748f1ca094bcfed9d7d0f5b16996 | e7cf6a3ddfb2fd6fc7102f8bc957ff36 | 3d0404dd20a2b8a87d47d0d60d15b2be | 29 |

BFGS steps are QE's own 'bfgs converged' counts (digest_hl_a20ii.md quoted the last 'number of bfgs steps' counter, one lower). Full hashes: geometry_binding.md and the manifest.

**Vacancy sites** (order-preserving match against the parent; agree with `compute/vacancy/BUILD_REPORT.md`): In32O47 = In32O48 minus O17; far = In31WO48 minus O32 (W-O 6.84785 A; O32/O33 symmetry pair unsplit, A19 fixes O32); near = minus O30 (1.89194 A; O30/O69 unsplit); near72 = minus O72 (1.90237 A; +0.01043 A, no TIE). W is index0 4 (QE #5) in all four W cells. Maximum displacement against "parent minus site": In32O47 0.140, far 0.204, near 0.248, near72 0.521 A.

## 2. Settings: identical A19 numerics plus spin (unchanged from v1)

Each staged `scf.in` is `vac/<cell>/scf.in` with only: `ntyp` raised for the split species; one new `&SYSTEM` line `nspin = 2, starting_magnetization(i) = ...`; O1/In1 `ATOMIC_SPECIES` lines (same masses and **same PAW files**); relabelled seeded atoms; `K_POINTS` 4 4 4 -> **3 3 3** 0 0 0. Unchanged: Gaussian **0.005** Ry, conv_thr **1e-8**, plain mixing **beta 0.3**, **electron_maxstep 100**, ecut 71/568 Ry, verbosity 'high', tprnfor, tstress, the cell and every coordinate. `tot_magnetization` is **not set** (free total magnetisation, one Fermi level).

Run environment as a20_g002 (12904174): `bin/check_node.sh` (md5 4484f987…) -> `common/driver.sh` (md5 60d11efd…) in GPU mode, QE **7.3.1** GPU container, 1 MPI rank, `QE_NK=1`; pseudo md5s In 235b15e6…, O e99d9cef…, W 03c3df5b… (now checked in every output, §6). Resources: 1 GPU `regexp("H100|A100") && !regexp("MIG")`, `request_cpus` 8, `request_memory` 32768 MB, `request_disk` 40 GB, "workday", wall limit 27000 s, `priority 5`, `+IWOJob "A20_spin_<cell>_<start>"`.

The comparator rejects any attempt whose `scf.in` differs from the staged one (md5 with the `max_seconds` value blanked, because `driver.sh` rewrites it).

## 3. Seeds and neighbour selection (values unchanged from v1; unit note added in v3)

QE's `starting_magnetization` is per species, so seeded atoms carry split labels **O1** / **In1** (same files as O / In); W keeps its label. Rules (minimum image, applied by `build_a20i.py` to the bound geometry):
1. **W first shell (W cells):** O within **2.6 A** of W (index0 4); gap 2.164 -> 3.807 A in every W cell, so any cutoff in 2.2-3.8 A selects the same atoms (6 O in In31WO48 and far, 5 in near and near72).
2. **Vacancy cation shell:** cations within **2.8 A** of the removed O's parent position; gap 2.470 -> 3.737 A; exactly 4 per vacancy cell.
3. **In32O48 (matched sites):** In site 4 (W's site in the W cells) and its 6 O (2.167-2.256 A, next 3.894 A), plus the 4 In bonded to O17 (In32O47's vacancy site). Closed shell (704 e-, -TS = 0 at k3 and k4), so every seed must decay to M = 0: the clean test of the split-label + nspin = 2 machinery for both labels (§5).

| Cell | W | O1 = W first shell (index0; A) | In1 (index0; A) |
|---|---|---|---|
| In32O48 | - (site 4 is In1) | 73, 72, 69, 30, 25, 27 (2.167-2.256) | site 4 + O17 shell 54, 1, 50, 6 (2.167-2.256) |
| In31WO48 | 4 | 30, 69, 72, 73, 25, 27 (1.892-2.152) | none |
| In32O47 | - | none | vacancy shell 53, 1, 6, 49 (2.186-2.379; next 3.896) |
| In31WO47_far | 4 | 68, 30, 71, 72, 27, 25 (1.884-2.164; next 3.903) | vacancy shell 43, 0, 7, 15 (1.958-2.375; next 3.903); vacancy 6.849 A from W |
| In31WO47_near | 4 | 72, 71, 68, 25, 27 (1.879-2.062; 5-fold) | W + In 9, 2, 13 (2.188-2.433; next 3.737); vacancy 2.139 A from W |
| In31WO47_near72 | 4 | 72, 25, 30, 69, 27 (1.790-2.058; 5-fold) | W + In 40, 55, 47 (2.185-2.470; next 3.956); vacancy 2.036 A from W |

| Start | In32O48 | In31WO48 | In32O47 | far | near / near72 |
|---|---|---|---|---|---|
| **A** (registered "small") | O1 0.1, In1 0.1 (10.1 muB nominal) | W 0.1, O1 0.1 (5.0) | In1 0.1 (5.2) | W 0.1, O1 0.1, In1 0 (5.0) | W 0.1, O1 0.1, In1 0 (4.4) |
| **B** (cation-large) | O1 0.1, In1 0.5 (36.1) | W 0.5, O1 0.1 (10.6) | In1 0.5 (26.0) | W 0.5, O1 0.1, In1 0.5 (36.6) | W 0.5, O1 0.1, In1 0.5 (29.5) |

**Seed units (Codex 03:26Z):** QE 7.3.1 reads `starting_magnetization` as a fractional spin polarisation of each species' valence charge (-1 to 1), i.e. per valence electron. The muB values in the table are nominal starting moments (seed x valence electrons, summed over the seeded atoms). In1 = 0.5 is a large nominal seed (about 6.5 muB per In1 atom in the starting density), not a 0.5 muB moment; no seed value is a measured or expected moment.

Reasons: A follows the registered words in the W cells (W and its O neighbours only; In1 exists as a label but carries 0, so A and B differ in one `&SYSTEM` line). In32O47 has no W, so its meaningful site is the vacancy shell (Codex). 0.1 is small per atom (the nominal moment counts the full valence, including In 4d10, W 5s5p and filled O 2p; in stage 4 a nominal 7 muB on W gave M_tot 0.09 after one iteration). B targets a W-5d-like moment and a polarised vacancy-bound state; W 0.5 is the stage-4 value (result-informed, §0). O1 stays 0.1 in B.

**Disclosed limits of the seeds (review 1):** (i) neither start seeds the delocalised In-5s conduction band that carries the W and V_O electrons; the stage-4 run nevertheless reached a delocalised branch from a W-only seed (W 0.20 of M_tot 0.62), so the risk of missing it is judged low; (ii) B's 0.5 on In1 is 6.5 muB nominal per In, counting the filled 4d10 shell, which is not physical and may slow the plain-mixing SCF (B starts may need the fallback); (iii) **asymmetry (review 2):** start A seeds the vacancy shell in In32O47 but not in far (In1 = 0), so the A-only ΔE_dop is seeded asymmetrically. A uniform small seed on all In for B in In31WO48 was considered and **not** adopted (it would change the job set; needs the user's go if wanted).

## 4. Spin branches and the verdict (pre-declared, v3)

1. **Start result.** A start counts if attempt 1 counts, or else if its single fallback counts (§6); otherwise it is UNRESOLVED.
2. **Primary cell energy.** E_s(cell) = min(E_A, E_B, E_nspin1) over the cell's counted starts, where E_nspin1 = E_REF (§5). The M = 0 solution is a stationary state of the same nspin=2 functional, so a start that lands on a magnetic branch **above** it does not enter E_s. At least one counted start is required; a cell with none is UNRESOLVED. E_s is the lowest of the tested stationary states (conservative); it is **not** shown to be the spin ground state.
3. **Readings.** Every reading forms ΔE_local(O30) = E(near) - E(far), ΔE_dop = [E(far) - E(In31WO48)] - [E(In32O47) - E(In32O48)] and the O72 sensitivity:
   - **primary**: E_s per cell;
   - **A_only**: the registered start A as converged (the literal reading of A20(i)), including a branch above nspin=1;
   - reported only: **min_AB** (lowest counted start, without nspin=1) and **B_only**. B is result-informed and enters the verdict only through the primary, as a lower state.
4. **Triggers.** Shift = reading - nspin=1 k3 value (+0.5578, +0.6643, +0.7259 eV). A registered difference triggers if |shift| > 50 meV (exactly 50.0 does not) or its threshold status flips. **Flip** = a change of threshold satisfaction at k3, the registered mesh (ΔE_local >= +0.3 eV, ΔE_dop > +0.05 eV). O72 never triggers. **Triggers only add:** a trigger in the primary **or** in A_only makes H-L "not robust"; the label names every reading that triggered.
5. **A20(i) verdict, in this order:**
   1. gate failure (§5): "UNRESOLVED (equivalence gate failed; raw triggers: <list or none>)";
   2. a trigger in the primary: "not robust (triggered by: <reading:difference, ...>)" (A_only triggers are listed too); H-L is reported "not robust" and the registered score is still shown;
   3. a trigger in A_only only (start A lies above the lowest tested state in at least one cell; v3, Codex): "not robust to the registered spin-start branch; metastable start (start A above the lowest tested state in: <cells>; triggered by: <...>; primary reading unchanged: no trigger)"; H-L is reported "not robust" (A20; registered spin-start branch, metastable start; primary reading unchanged);
   4. a registered difference missing in the primary: "UNRESOLVED (cell missing: ...)";
   5. a registered difference missing in A_only: "UNRESOLVED (registered start A incomplete: ...; primary reading: no trigger)";
   6. otherwise "robust".
   Suffixes (pre-declared, registered-difference cells only): "incomplete branch coverage: <cells>" (only B counted); "second-start sensitivity unresolved: <cells>" (only A counted: no two-start robustness claim; v3, Codex); "fallback SCF path (branch may differ): <cell/start>"; "branch-dependent cells: <cells>"; "metastable starts: <cell/start>"; "reported variants differ from primary: <min_AB, B_only>".
6. **Flags.** Branch-dependent if both starts count and |E_A - E_B| > 1 meV, or ||M_tot,A| - |M_tot,B|| > 0.05, or |M_abs,A - M_abs,B| > 0.05 muB/cell (spin-flipped equivalent states are not flagged; equal M_tot with different M_abs is). Metastable: a magnetic start more than 1e-5 Ry above E_REF.
7. **Header and combined status** printed with every result: the registered score with separated statuses (ΔE_local(O30) +0.5578 / +0.5321 eV, UNRESOLVED significance, k4 not adopted; ΔE_dop +0.7259 / +0.7226 eV, PASS under registered settings; A20(ii) width-robust at k3; H-L UNRESOLVED), and "H-L UNRESOLVED (...); A20(ii) width-robust at k3; A20(i) <verdict> at k3, <coverage>", where coverage is "two starts" only if both starts count in every registered-difference cell, and otherwise names the cells ("second-start sensitivity unresolved: ...", "registered start A missing: ...", "no counted start: ...").
8. A20(i) does not change ΔE_local's "UNRESOLVED significance" (k-mesh), adopts nothing at k4, and H-L stays UNRESOLVED overall whatever A20(i) gives.

## 5. Split-label equivalence gate

A counted start is gate-applicable if its final |M_tot| <= 0.01 and |M_abs| <= 0.01 muB/cell (QE prints 2 decimals). Every gate-applicable start must reproduce its cell's nspin=1 k3 Gaussian 0.005 energy within **1e-5 Ry**. Every counted In32O48 start must be gate-applicable and pass, and at least one In32O48 start must count. **A gate failure makes A20(i) UNRESOLVED and takes precedence over triggers; the label lists the raw triggers so none is hidden.**

| Cell | E_REF (Ry; k3 relax final, r23.out) |
|---|---|
| In32O48 | -15146.85585849 |
| In31WO48 | -15496.36629681 |
| In32O47 | -15105.09003220 |
| far | -15454.54711429 |
| near | -15454.50612023 |
| near72 | -15454.49828792 |

**Basis of the baseline (stated, not validated for all cells):** E_REF is the last '!' energy of the relaxation, an SCF of the same input, settings and conv_thr on the bound geometry (§1a). Equality with a fresh standalone k3 SCF was shown only for In32O48 and In32O47 (A20(ii), 1e-8 Ry, smearing inactive); for the four metallic W cells it rests on theory (expected agreement ~1e-7 Ry). Splitting the species lowers the symmetry (In32O48: Ia-3 with 6 k -> P1 with 14 k at the same MP grid), so the gate also checks the symmetry reduction.

## 6. Failure handling, removal, pause and monitoring (pre-declared; no other retries)

**An attempt counts only if** its bound job (item 0) left the queue by termination (its only terminal event), and the results tarball is readable; its `scf.in` is the staged one (md5, `max_seconds` blanked); the output says `Program PWSCF v.7.3.1`; **every 'MD5 check sum' of the pseudopotentials equals the frozen value** (species numbered as in the manifest, so the split labels are checked too); the electron count is as staged; "convergence has been achieved" is present, "convergence NOT achieved" absent, "JOB DONE" present; and the pw.x end time in the driver log is <= **2026-10-17T10:00Z** (deadline for A20(i), result-informed, §0).

A valid archive of a removed job, or of a job that has not left the queue (for example a snapshot copy), never counts (v3; Codex FIX_FIRST).

0. **Binding (v3, Codex FIX_FIRST).** Attempt 1 is submitted as `condor_submit a20_spin.sub | tee submit_attempt1.txt`; the start on line i of `jobs.txt` (= the manifest job list) is job <cluster>.i, with <cluster> from the single "N job(s) submitted to cluster C." line (N = 12). Fallbacks are submitted as `condor_submit a20_spin_fb.sub | tee submit_fallback.txt`; the start on line j of `fb_list.txt` is <fallback cluster>.j (N = lines of fb_list.txt). Only the bound job's events in the attempt's own user log are evaluated, in log order. **Missing or ambiguous evidence** (no submission record or a count mismatch, no user log, events of any other job in that log, not exactly one submit event, event times out of order, more than one terminal event or events after it) gives the disposition "unresolved": the attempt does not count and allows no fallback, so the start is UNRESOLVED. The disposition is checked for **both** attempts.
1. **Attempt 1** = the staged `<cell>/<start>/scf.in`. HTCondor's automatic re-execution after an eviction is **part of attempt 1** (with ON_EXIT transfer only the final execution returns output). Releasing a job held before it ran > 1 h is administrative. Both are counted from `logs/check.log` (execute, evict, hold, release events) and reported, never hidden.
2. **One fallback per start**, named **"A20(i) fallback (A28-style mixing settings, new for A20(i); proposed A42)"**. A28 declared its fallback for the near relaxation only and never used it; this is a new declaration. It changes only `&ELECTRONS`: `mixing_mode = 'local-TF'`, `mixing_beta = 0.1`, `mixing_ndim = 12`, `electron_maxstep = 300` (conv_thr and seeds unchanged). **A28's "the SCF path changes, not the converged energy" does not hold for a multi-stable spin SCF:** a fallback can reach a different branch, so a fallback-derived start is labelled "fallback SCF path; branch may differ".
3. **Mechanical fallback list.** `fb_list.txt` is made only by `python3 -I a20i_compare.py --fallback-list a20i_manifest.json . fb_list.txt 2> fb_why_<UTC>.txt` (v3: the comparator writes the file itself and refuses, exit 3, once `submit_fallback.txt` exists, because the submitted list binds the fallback procs). It lists exactly the starts whose bound attempt-1 job left the queue (terminated, or removed under the objective conditions of item 5), does not count, ended before the deadline, and has no fallback submitted yet (no fallback user log). The command prints no energy or magnetisation.
4. **One go.** A single user go covers all fallbacks; declining it makes A20(i) UNRESOLVED as a whole (not start by start). If a fallback does not count, the start is UNRESOLVED. No third attempt, no setting changes, no k5.
5. **Removal.** A running A20(i) job is removed only if the **system** holds it after > 1 h of running (never `condor_release`d) or the wall time ends it. Any other removal, including removal after a user `condor_hold` of a running job, makes the start UNRESOLVED with no fallback; the comparator enforces this from the bound job's user-log events (removal reason, hold reason, and that the job was running at the hold; v3). **v4 (Codex FIX_FIRST):** a removal counts as a system removal only with evidence in its reason (SYSTEM_PERIODIC_REMOVE / PeriodicRemove); a missing or unrecognised reason is UNRESOLVED with no fallback (the absence of "condor_rm" or "by user" proves nothing), and CERN's "by user condor" stays UNRESOLVED until the administrative cause is evidenced. The hold/release sequence is checked before any terminal event is accepted: an idle job may be held and released, and a system hold after <= 1 h of running may be released (administrative); releasing a `condor_hold` of a running job (a pause) or a system hold after > 1 h of running makes the start UNRESOLVED, whatever follows (HTCondor records the release as its own event, 013, so termination alone cannot show compliance).
6. **Pause policy (user's GPU question).** Running A20(i) jobs are excluded from any general pause of DFT jobs. Idle (never started) A20(i) jobs may be held and released at any time (administrative). Recommendation: submit A20(i) only once the pause schedule is decided.
7. **Monitoring blind.** Only `condor_q`/`condor_history` status and the HTCondor user logs are looked at while jobs run. Outputs of running jobs may be copied with `snapshot_jobs.sh` for safekeeping (running jobs lose Kerberos), but no `scf.out` energy or magnetisation is read before every start is final and the comparator runs.

## 7. Outputs and the comparator (frozen before any A20(i) output)

Per start: '!' energy, E - E_nspin1 (meV), final M_tot and M_abs, -TS, E_F, SCF iterations, which attempt was used and why any attempt did not count, pseudo md5s, HTCondor event counts, per-site moments of W, every O1 and every In1 ("not printed" if QE 7.3.1 omits them) and the largest |site moment|, gate status, metastable flag. Per cell: E_s, its source (A, B or nspin1), E_s - E_nspin1, counted starts, branch differences, flags. Global: registered score header, gate, the four readings with shifts/flips/triggers, the verdict, `H_L_robustness_under_A20i`, the combined status.

| File (v4, local; lxplus holds v3) | sha256 |
|---|---|
| `a20i_compare.py` (v4; v3 was b7989ad677ddf6c38f476fae82fb5ea52fca6d50432eca3dab0b3662d02da041, v2 e8f67013…) | 87e2ae1c510477cfc961fd6f49b2fa45825182a6a5ffcfcfc1f1f7b984832949 |
| `a20i_manifest.json` (embedded in the comparator; changed manifest -> exit 2) | 08c0741ea8badc67ac6f9a93e74cff149b4d5ae320f2a6ab9b39db4e12bb155d |
| `a20i_compare_test.py` (v4; v3 was a5a13114…) | f24c84f2858e9016852fa2dcab1372fe21d814a4baa75765be8ddb35e248ad22 |
| `build_a20i.py` | d107068677ab9a66d6793be137b6dfd10879fb8486bf4f7bce4365a5df6c9198 |
| `a20_spin.sub` (comments only changed; v3 2b6680c6…) | 1653ff567443f1312b4eee7edfee1c7c0d5443ab5a1cdee067e0782831c77568 |
| `a20_spin_fb.sub` (comments only changed; v3 03e6abb2…) | 7fee9ac937b930d9f1fdefdb4ddef0780f42b96bbfdac670a369eea9f5d322dd |
| `README.txt` (v3 e2c540ca…) | a03cc045cb75f19cf02b6c6b068eb09d391ed311594ab6749782d6c9e2793671 |
| `jobs.txt` | 951ef70999d108b5aece945d29c5f7960529a686426ef511a6b98972b48b8c64 |
| lxplus `MD5SUMS` (59 files, regenerated 2026-10-13T03:53Z; describes the v3 tree; to be regenerated when v4 is installed) | b54adf86b7100cf74e6ead56a89122afcb92c38b93b7f5fde8063e38c385e5d8 |

The 24 input sha256 values are in Appendix A. Use after all starts are final: `python3 -I a20i_compare.py a20i_manifest.json <copy of the a20_spin tree including logs/, jobs.txt, fb_list.txt, submit_attempt1.txt, submit_fallback.txt> a20i_result.json`.

**Tests (v4).** Synthetic (invented numbers): **47/47 PASS** locally (WSL Python 3.12.3; `v4/test_v4.out`); not yet run on lxplus (v4 not installed). The Codex FIX_FIRST tests were written first and fail on the v3 comparator (**42/47**, `v4/test_v4_against_v3_comparator.out`): E1a abort with a missing reason (v3: "objective (system removal)", fallback used), E1b unrecognised removal text, E1c "by user condor", E2a system hold after 2 h of running, released, re-executed and terminated (v3: counted), E2b user `condor_hold` of a running job, released (v3: counted). Controls passing on both: E1d evidenced SYSTEM_PERIODIC_REMOVE removal (fallback allowed), E2c system hold after 30 min of running, released (counts).

**Tests (v3).** Synthetic (invented numbers): **40/40 PASS** locally (WSL Python 3.12.3) and on lxplus (Python 3.9.25, 2026-10-13T03:53Z). The Codex FIX_FIRST tests were written first and fail on the v2 comparator (**27/40**, `v3/test_v3_against_v2_comparator.out`): D1a valid archive of a manually removed running job (v2: "robust"), D1b fallback removed manually while running (v2: counted), D1c archive of a job that has not left the queue, D2a an older completed job in the same user log hiding the bound job's removal (v2: forbidden fallback used, and listed by `--fallback-list`), D2b log of the wrong proc, D2c no submission record, D2d two terminal events out of order, D2e fallback without a submission record, R2 (relabelled) and LB1 (labels), W1 (wording), L2 (fallback-list guard). Real-format check of v3 on lxplus: the user-log parser binds the six a20_g002 logs to 12904174.0-.5 (terminated, 1 execution each) and rejects each log for a wrong proc ("other jobs"); `--fallback-list` on the unsubmitted tree lists nothing (no submission record) and leaves `fb_list.txt` empty. v2 tests, unchanged: the v1 cases plus the review cases: nspin=1 in the primary (R2, R4), A_only-only trigger (R2), spin-flipped equivalent states (R3) and equal M_tot / different M_abs (R3b), a single metastable start (R4), a gate failure with a trigger elsewhere shown as raw trigger (R5), a pseudo md5 mismatch on a split label (P1), fallback refused after `condor_rm` of a running job (F1), fallback allowed after a system hold > 1 h with an eviction re-execution counted (F2), fallback refused after a user `condor_hold` (F3), and `--fallback-list` (L1, no number printed). **Real-format checks on lxplus:** the pseudo-md5 parser reads all six a20_g002 (QE 7.3.1) outputs and matches the frozen md5s; the user-log parser reads their `check.log` (1 execution, terminated); `--fallback-list` on the unsubmitted tree lists nothing. v1 had also run the moment/energy parsers on the real QE 7.5 stage-4 spin output.

## 8. Resources (estimate; nothing measured at nspin 2 yet)

Measured at nspin=1, k3 (A20(ii), 12904174, A100-PCIE-40GB): GPU peak 16.7-17.1 GB (nvidia-smi) at 6, 10 and 14 k, so device memory does **not** grow with the k count; host 5980, 7990 and ~9600 MB at 6, 10 and 14 k, which fits 3.3 GB + 0.45 GB per k; 6-13 min (16-26 iterations); every job used 1.00 of its 8 CPUs.
- **nspin=2:** GPU ~17-20 GB (worst case ~34 GB, inside A100-40GB). Host: up to 28 spin-k points -> ~16-18 GB; 32 GB is a ~2x margin. Time: ~0.5-1.5 h per job, ~6-15 GPU-h for the 12 first attempts (estimate); **fallbacks add cost** (at most 12). A fallback (<= 300 iterations at ~56 s) is **estimated** at up to ~4.7 h; this is an estimate, not a verified hard maximum (the enforced limits are max_seconds ~25,180 s and the "workday" wall time).
- **CPUs (review 1, optional):** not lowered. CERN's RebalanceMemCpu transform ties CPUs to memory at 3000 MB per CPU (register A-log: 84000 MB -> 28 CPUs; 82944 MB -> 27/81000), so 2-4 CPUs with the 32 GB needed would be raised again; the granted CPUs/memory will be read from the job log. 12 independent 1-GPU jobs finish sooner than multi-GPU jobs.
- **Register cost note:** A20 listed 12 SCFs (6 spin + 6 width). Two starts make the spin part 12 (A20 total 18), up to 24 spin SCFs with fallbacks.

## 9. Local smoke test (unchanged from v1; parse/setup only)

QE 7.5, WSL, 10 ranks `-nk 2`, ecut 20/160 Ry: In32O48/A, far/B, near/A and In32O47/B parsed and reached "Self-consistent Calculation"; QE printed the expected starting magnetic structure, 704/699/699/698 electrons, P1 with 14 k, and r_m 1.69 bohr for every species. No energy was produced or read.

## 10. What to log (task-level)

| Item | Status |
|---|---|
| H-L overall | **UNRESOLVED** |
| ΔE_local(O30) | **UNRESOLVED significance**: +0.5578 eV (k3) / +0.5321 eV (k4), k3->k4 -25.7 meV > 10 meV; "threshold satisfied at both tested meshes" (diagnostic wording); k4 not adopted |
| ΔE_dop | **PASS under registered settings**: +0.7259 eV; k3->k4 -3.4 meV |
| A20(ii) | width-robust **at k3**: +0.505 / +0.190 meV |
| A20(i) | **UNASSESSED** (staged v2 with comparator v3 on lxplus, comparator v4 local only; not submitted; A42 drafted, not logged) |
| Geometry binding | all six cells BOUND (canonical hash; §1a) |

**Ledger caveats for A20(i) when it is computed:** PBE (PAW), crystalline 80/79-atom cells, neutral, k3 only, collinear, two seeds, result-informed implementation (§0). The W cells have odd electron counts (705, 699) and are metallic at k3 (In31WO48 -TS -1.86 mRy): with k3 and Gaussian 0.005 Ry a partly filled discrete k-level can spin-polarise as a sampling artefact, and the stage-4 result (M_tot 0.62, -19.5 meV) is compatible with that. A "robust" A20(i) only bounds the shifts under these numerics; it does not establish the magnetic ground state, and a moment found is not evidence of physical magnetism (A20 allows no k or width check of the spin result). M_tot, M_abs, -TS and E_F are reported per start.

**RESULTS_LOG entry when submitted:** cluster id, the 12 job ids, submit time, this record's path and sha256, the comparator and manifest sha256.

## 11. Choices: settled in v2 (frozen as written unless changed before submission)

| v1 open choice | v2 setting |
|---|---|
| Two starts per cell | kept: 12 jobs (dropping In32O48/B would give 11; it stays because it gate-tests the In1 0.5 path on the closed-shell host) |
| Primary energy | min(E_A, E_B, E_nspin1); additive triggers over primary and A_only (§4) |
| Infrastructure failures | one fallback for any non-counting attempt 1, list made mechanically; eviction re-executions are part of attempt 1; an identical-input retry was considered (review 1 option) and not adopted, to keep one second-attempt path |
| Seed values | as v1, with the limits disclosed (§3) |
| Löwdin moments | not staged; QE sphere-integrated site moments are recorded |
| Logging | H-L logged 2026-10-13 03:40Z (RESULTS_LOG, public ee27e4e; C038, private 6cfd5fb); A42 drafted, not logged |

**Still needs a decision:** (1) Codex review of the final A42 text (`A42_A20i_amendment_draft.md`) and its logging with D-45; (2) the user's go for `condor_submit a20_spin.sub | tee submit_attempt1.txt` (12 jobs, 1 x A100/H100 each), after the GPU pause. Settled by Codex (03:26Z reply): keep min(A, B, nspin1) and the additive A-only trigger, with the labels of §4.5; no extra seed expansion.

## 12. Amendment text

The amendment is drafted separately in `A42_A20i_amendment_draft.md` (result-informed amendment A42, decision D-45; not logged). This record is its annex. The v2 draft text that stood here is superseded by that file (it said "reported, not registered"; Codex asked for "reported sensitivity; does not replace the original registered score").

## 13. Review findings and how v2/v3 handle them

| # | Review / severity | Finding | v2 handling |
|---|---|---|---|
| 1 | R1 blocking | E_s excluded the nspin=1 state | primary = min(A, B, nspin1); min(A,B) reported (§4.2) |
| 2 | R2 blocking | A-only trigger could be labelled "robust" | triggers additive over primary and A_only; A_only missing -> UNRESOLVED; tests R2, R4 (§4) |
| 3 | R2 blocking | design is an amendment, not a note | A42 text drafted (§12); not applied (task rules); Codex review + user go needed |
| 4 | R2 blocking | disclosure block said "before any spin output" | rewritten with the stage-4 read and the full list of result-informed rules (§0) |
| 5 | R2 blocking | discretionary retry routes | mechanical list, one go, removal conditions enforced from the user log, blind monitoring, re-executions counted, fallback renamed (§6) |
| 6 | R1 minor | fallback may change branch; eviction retries | labelled; eviction = part of attempt 1 (§6) |
| 7 | R1+R2 minor | signed dM; M_abs not compared | |abs| difference and M_abs difference (§4.6; tests R3, R3b) |
| 8 | R1+R2 minor | pseudopotentials not checked | every PP md5 checked by species number (test P1; real QE 7.3.1 format checked) |
| 9 | R1+R2 minor | gate hides triggers; W baseline unvalidated | label lists raw triggers (test R5); baseline basis stated (§5) |
| 10 | R1 minor | odd-electron metallic cells; sampling artefact | caveat in §10 and the ledger caveats |
| 11 | R1 minor | seeds miss the In-5s band; 0.5 on In1 | disclosed (§3); no change |
| 12 | R1 minor | resources; 8 CPUs idle | data added (§8); CPUs not lowered (RebalanceMemCpu) |
| 13 | R1+R2 minor | relax.in is rolling; near A28 lineage | caveat; canonical-hash binding; A28 md5s and ids (§1a) |
| 14 | R2 minor | variational rationale; A asymmetry for ΔE_dop | rationale "lowest tested, conservative" (§4.2); asymmetry disclosed (§3) |
| 15 | R2 minor | registered score not shown; flip undefined | fixed header + combined status; flip defined at k3 (§4.4, §4.7) |
| 16 | R2 minor | asymmetric start failures hide coverage loss | "incomplete branch coverage" suffix (§4.5) |
| 17 | R2 minor | pause plan vs frozen rules | pause policy and user-hold rule (§6.5-6.6; test F3) |
| 18 | Codex 03:26Z, blocking | attempt 1's Condor disposition never vetoed counting | v3: counting needs the bound job's termination, for both attempts (§6; tests D1a-D1c) |
| 19 | Codex 03:26Z, blocking | events not bound to cluster.proc; any historical termination won | v3: binding from the saved condor_submit stdout; bound job's events only, in order; missing/ambiguous -> UNRESOLVED (§6.0; tests D2a-D2e, L2) |
| 20 | Codex 03:26Z | higher-energy A trigger; missing B | labels "not robust to the registered spin-start branch; metastable start" and "second-start sensitivity unresolved" (§4.5, §4.7; tests R2, LB1) |
| 21 | Codex 03:26Z | "reported, not registered" | "reported sensitivity; does not replace the original registered score" (§12, comparator; test W1) |
| 23 | Codex (A42 draft), blocking | an abort with a missing reason was a "system removal" and allowed a fallback | v4: system removal only with evidence; missing / unrecognised reason or "by user condor" -> UNRESOLVED, no fallback (§6 item 5; tests E1a-E1d) |
| 24 | Codex (A42 draft), blocking | a released late system hold could still count | v4: hold/release sequence enforced before termination is accepted (§6 item 5; tests E2a-E2c) |
| 25 | Codex (A42 draft) | budget wording | 6-15 GPU-h is the first-attempt estimate, fallbacks add cost, 4.7 h is an estimate (§8) |
| 22 | Codex 03:26Z | seed units | QE seeds are a polarisation per valence electron; In1 = 0.5 is nominal (§3) |

## 14. Files

**v4 additions:** local `v4/` (`stage_build/` = the v4 staged files, `add_v4_tests.py`, `patch_compare_v4.py`, `patch_record_v4.py`, `runtest.sh`, `test_v4.out`, `test_v4_against_v3_comparator.out`); `v3_backup_20261013/` (record v3, A42 draft v1, v3 comparator and test). Nothing installed on lxplus.

**v3 additions:** local `v3/` (`stage_build/` = the v3 staged files, `patch_compare.py`, `patch_test.py`, `new_tests.py`, `patch_stage_text.py`, `patch_record.py`, `test_v3.out`, `test_v3_against_v2_comparator.out`, `mk_install.py`, `install_v3.sh`/`.out`); lxplus `v2_comparator_superseded_20261013T0355Z/` (v2 comparator, test, subs, README, MD5SUMS) and `BUILD_v3_comparator_20261013T0355Z.txt`.

**Local** (`scratchpad/hl_a20i/`): this record; `a20i_compare.py`, `a20i_compare_test.py`, `a20i_compare_test.out`, `build_a20i.py` (v2); `stage/a20_spin/` (exact copy of the v2 tree, with both v2 BUILD files and the lxplus MD5SUMS); `v2/` (work files, `stage_v2.sh`/`.out`, `restage_v2.sh`/`.out`, `patch_builder.py`); `v1_backup_20261013T0220Z/` (v1 record, comparator, test, builder, drafts, staged tree; `SHA256_v1.txt`); `geometry_binding.md`; `HL_log_drafts.md`.

**lxplus** (`~/iwo_amorph/checks/gpumax_work/a20_spin/`): `README.txt`, `BUILD_v2_20261013T030746Z.txt`, `MD5SUMS`, `a20_spin.sub` (12 jobs), `a20_spin_fb.sub` + empty `fb_list.txt`, dry runs `dryrun_v2_20261013T030746Z.ad` (12 procs, rc 0) and `dryrun_v2_fb_20261013T030746Z.ad` (test list only, rc 0), `jobs.txt`, the four frozen evaluation files, `<cell>/<A|B>/{scf.in, logs/, fallback/{scf.in, logs/}}`, `v1_superseded_20261013T022045Z/`, `v2_draft_20261013T030503Z/`. `condor_q` showed no A20_spin job at 03:07Z.

## Appendix A. Staged inputs (sha256; byte-identical to v1)

| Input | sha256 |
|---|---|
| In32O48/A/scf.in | 6c6d948c7ff2d980a8c9545968c747f06f733fb6323b3c0cfece0fb87152d171 |
| In32O48/A/fallback/scf.in | 9dea125129ef96efa75f5acad8a914f28bfd888329b830b65f00a771cc1cdc66 |
| In32O48/B/scf.in | b6ee41876323c00f7ea58dbb6c6947f5ddb8a3f56edb45d10cdd631668b9dd4c |
| In32O48/B/fallback/scf.in | f439a03d474d25af9ad8ecf35244cc30265096f3876736bb6a37de86edfd0f17 |
| In31WO48/A/scf.in | a194950946d27c546245ab6f7d9b9458009b3c8c6e9e4b9ba206fd2fea3223f0 |
| In31WO48/A/fallback/scf.in | 63a6e5d772498eadddd7e92e29a5050616298f95f6b91637a503203736084c2e |
| In31WO48/B/scf.in | 38cff8b241b75196ead99258356b986a50e63df79ace4305d896cb343d53912f |
| In31WO48/B/fallback/scf.in | d18af52a3839d2e56d948b751966da8ff035b83907cfd87f2ebf2581e0495f08 |
| In32O47/A/scf.in | 05bbd7b2275d035f1bd87655a248b2c8688edd5968a38589b9474c850b769aed |
| In32O47/A/fallback/scf.in | 2b263a2104be3819aa618f6b88da86521cf77e09d906d20535be149970fb1b3e |
| In32O47/B/scf.in | 613e2112bf5add96f5bd3772710cb6fb73540d6cc27e6ff325edf6daf6c0037c |
| In32O47/B/fallback/scf.in | 63cbe8cc7f940c2247c857f84ed2039ef5187c08418929276d5f6621ef329e23 |
| In31WO47_far/A/scf.in | d77659f489ccf49c750d121c31a2d09113666589c7d65b08dcfb2d59e66f9f1f |
| In31WO47_far/A/fallback/scf.in | 1d7fcece22cd4c05967fde120353db45f2b00c3c5dd4ec74a2b97fbfa50424e7 |
| In31WO47_far/B/scf.in | a69d3a08bc7a18c284ee95a46b66f047066eb6fcc2779a61164d87cfea916c5c |
| In31WO47_far/B/fallback/scf.in | 5e6fe550c6464ff40a04aa7396550579a4d5ac906ab75bb047c41e46e5a34dec |
| In31WO47_near/A/scf.in | 42b41a04a706802575b8364bb158edbccdd4e20fbae4759cd5f43cb3968f5c8b |
| In31WO47_near/A/fallback/scf.in | bfbeaea2a26263f149062942c5983a01f0cd538c927b8489019cbfec6305b57f |
| In31WO47_near/B/scf.in | c819ace2917742123bcdfce1d4e950db86688c5a0e1fafd2d22d832f7704c62e |
| In31WO47_near/B/fallback/scf.in | 28b448828d6fba3235d6f70d16a4a44cf8a8a1f5e4934c3c52bf07868bcf186d |
| In31WO47_near72/A/scf.in | 1e0bcf88ff55cdfd45473451386393a91b3e651920a5356a2c80ea8059919f69 |
| In31WO47_near72/A/fallback/scf.in | a6ac7992b065e63059241eb958c70d9006145f67eb8258e06a389d20495cf222 |
| In31WO47_near72/B/scf.in | a522be28ae1e2b48be3a6e4754dd8cafcc856d89d00e8639b6131d53e43460ad |
| In31WO47_near72/B/fallback/scf.in | d2fedb66c7d220d6ac5f8b61788974281f0319a0ed655edcc48633f9e7fd74cd |
