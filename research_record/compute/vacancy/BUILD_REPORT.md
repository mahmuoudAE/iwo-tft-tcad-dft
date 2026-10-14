# H-L crystalline oxygen-vacancy cells: build report (2026-10-11)

This is the build and staging record for H-L (register amendment A17, decision D-19). The frozen definitions are in
`codex/work_chat/HYPOTHESIS_REGISTER.md`, section "### H-L". The register was not edited.

**Status: staged on CERN, NOT submitted.** Revision 2 (2026-10-11) applies the verification findings (section 6).
Revision 3 (2026-10-11) applies register amendment A19: a sixth cell, In31WO47_near72, tighter RELAX and FINAL
acceptance, and the frozen selector `select_near.py` (section 8, "A19 changes").

**Submission gate (open).** Submission needs the user's go.
- The near-site reading (section 1, "Site-selection decision") is settled by register A19, which takes option (c):
  both near candidates are computed, and `select_near.py` picks the registered one on the H-L-relaxed In31WO48.
- The submission entry (section 7) is written into RESULTS_LOG.md at submission.

**Index convention used throughout:**
- **index0** is the 0-based position in the 80-atom list (Python, `build_facts.json`).
- **QE #** is index0 + 1, the atom number QE prints.

## 1. Structures (`make_vac.py`; numbers in `build_facts.json`)

| cell | origin | atoms | valence electrons | min distance (A) | symmetry (spglib, 1e-3) | irreducible k (spglib) 3x3x3 / 4x4x4 |
|---|---|---|---|---|---|---|
| In32O48 | `structures_v2/relaxed_pbe/bulk_conv.json` | 80 | 704 | 2.167 (In-O) | Ia-3 (206), 48 ops in the cubic cell | 4 / 11 |
| In31WO48 | **relaxed** stage-4 iwo_W24d (`results/iwo_W24d/relax.out`, final coordinates) | 80 | 705 | 1.892 (W-O) | P2 (3), 2 ops | 10 / 30 |
| In32O47 | In32O48 minus O index0 17 (QE #18) | 79 | 698 | 2.167 | P1 | 14 / 36 |
| In31WO47_near | relaxed In31WO48 minus O index0 30 (QE #31) | 79 | 699 | 1.892 | P1 | 14 / 36 |
| In31WO47_near72 (A19) | relaxed In31WO48 minus O index0 72 (QE #73) | 79 | 699 | 1.892 | P1 | 14 / 36 |
| In31WO47_far | relaxed In31WO48 minus O index0 32 (QE #33) | 79 | 699 | 1.892 | P1 | 14 / 36 |

Valence electrons: In 13, W 14, O 6. These match `z_valence` in the UPF headers on CERN. The W cells have an
odd electron count and are run spin-unpolarised, as H-L freezes.

### Host and cell checks
- **Lattice:** a = 10.3060902 A, cubic. This matches H-L's 10.3061 to within 5e-5 A.
- **Symmetry:** spglib finds Ia-3. The 40-atom primitive cell has **24 operations**.
  - All 48 O atoms form one orbit (48e).
  - The In atoms form two orbits (8b, 24d).
- **In-O bonds:** 2.167 to 2.256 A, with every In 6-fold coordinated.
  - The usual 2.12 to 2.21 A check range is for the experimental a = 10.117 A.
  - Scaled by the PBE/expt ratio of 1.0187, it becomes 2.16 to 2.25 A, which is consistent.

### W cell
- **Cell:** the stage-4 run was a fixed-cell `relax`, so its CELL_PARAMETERS equal the host cell (|diff| < 1e-8 A).
  No rescaling was needed.
- **Stage-4 relaxation:** 18 BFGS steps, E = -15496.3666037 Ry. Settings: mv 0.01 Ry, conv_thr 1e-9, QE 7.5 on CPU.
- **W site:** W is index0 4 (QE #5). It replaces host In index0 4, which spglib places at Wyckoff 24d.
- **Geometry source:** the relaxed In31WO48 geometry is the "Begin final coordinates" block of
  `cern_htcondor/results/iwo_W24d/relax.out`. The staged In31WO48 equals it exactly (max |dfrac| = 0).
  - **Trap:** `structures_v2/relaxed_pbe/iwo_W24d.json` is the **unrelaxed** W substitution, despite the folder name.
    Only its host lattice is PBE-relaxed.
  - It differs from the relaxed geometry by max |dfrac| = 0.0246 (0.253 A in one Cartesian component, 0.392 A as a
    displacement norm). W itself moved 0.056 A.
  - Do not rebuild or audit In31WO48 from that json. The atom order is identical in both files.
- **After relaxation:** In-O 2.125 to 2.478 A. The W-O first shell is 1.8919, 1.9024 and 2.1523 A, each twice
  (C2 pairs).

### Vacancy sites (H-L rules, applied to the stage-4 relaxed In31WO48)
Distances within 1e-3 A count as ties, and the lowest index among tied O is chosen. Exact values are from
`check_site_rule.py`, which uses the relax.in cell.

| site | removed O | distance | tie partner | next distinct | margin |
|---|---|---|---|---|---|
| **near** (shortest W-O) | index0 30 = **QE #31** | W-O 1.89194 A | index0 69 = QE #70 (C2-equivalent) | index0 72/73 = QE #73/#74, 1.90237 A | **0.0104 A** |
| **far** (largest minimum-image W-O) | index0 32 = **QE #33** | 6.84785 A | index0 33 = QE #34 (C2-equivalent) | index0 29/70 = QE #30/#71, 6.76580 A | 0.082 A |
| **host V_O** (O nearest the cell centre) | index0 17 = **QE #18** | 2.3012 A from the centre | index0 21, 25, 69, 73, 77 = QE #22, 26, 70, 74, 78 | all 48 O are one 48e orbit | n/a |

The next layer after the near pair is index0 25/27 (QE #26/#28) at 2.1523 A. The cubic cell allows a W-O
distance of at most 8.925 A.

Neighbours and coordination:
- **near:** cation neighbours W 1.892, In index0 9 (QE #10) 2.339, In index0 2 (QE #3) 2.456 and In index0 13 (QE #14)
  2.478 A. In the vacancy cell, W and 3 In become 5-fold coordinated.
- **far:** neighbours In 2.160, 2.212, 2.219 and 2.268 A (index0 44, 0, 7, 15 = QE #45, 1, 8, 16). W stays 6-fold.
- **host V_O:** 4 In become 5-fold coordinated.

Removal was checked by atom-by-atom position matching, and only that O is missing:
- near removes QE #31;
- far removes QE #33;
- In32O47 removes QE #18.

### Site-selection decision (verification findings 1 and 5; RESOLVED by register A19 = option (c), see section 8)
H-L says to pick the sites "in the relaxed In31WO48", and "Both are chosen from the relaxed host before the vacancy
runs". The staged sites come from the **stage-4** relaxation (mv 0.01 Ry, QE 7.5 CPU), not from the H-L-settings
relaxation of In31WO48 (Gaussian 0.005 Ry, QE 7.3.1 GPU). If all five DAGs go in together, that H-L relaxation cannot
finish before the vacancy runs start.
- The near choice has a margin of only 0.0104 A.
- Fixing the reading after vacancy energies exist would weaken the pre-registration.
- ΔE_local is scored against +0.3 eV, and the alternative near site (QE #73/#74) is a different first-shell O.

The user must pick one option and record it, dated, in RESULTS_LOG.md or the ledger before submission. The register
is not edited.
- **(a) Stage-4 reading.** "The relaxed In31WO48" means the stage-4 geometry. QE #31 (near) and QE #33 (far) are
  final whatever the H-L relaxation gives.
  - The contingency is declared in advance, before any vacancy energy exists. Once the H-L In31WO48 converges, run
    `python check_site_rule.py <In31WO48 relax.out>`. It compares QE #31/#70 with #73/#74, and #33/#34 with #30/#71.
  - If the order flips, it is either a reported note only, or it triggers one amendment run. Which one must be
    chosen now.
  - Submission: all five DAGs at once.
- **(b) H-L-settings reading.** Submit In32O48, In31WO48, In32O47 and In31WO47_far now.
  - Build and submit In31WO47_near only after the H-L In31WO48 relaxation converges, re-applying the rule with
    `check_site_rule.py`.
  - Delay: about 1 day, still inside 17 Oct 10:00 UTC.
  - For consistency, the far site should then be re-checked the same way before the far run is scored.
  - `make_vac.py` would need a small change to cut the near cell from the H-L relax.out. It is not prepared yet.
- **(c) Pre-submission amendment.** Add a sixth run, In31WO47_near with QE #73 removed, and register now which
  near energy scores ΔE_local. For example: the site that `check_site_rule.py` selects on the H-L In31WO48; the
  other site is reported.
  - No delay and no post-result choice. Cost: one more relaxation plus one k4 SCF.
  - The sixth cell is not built yet.

`check_site_rule.py` on the stage-4 relax.out reproduces the staged choices (exit 0): near QE #31/#70, far QE #33/#34.
Exit codes: 3 = near differs, 4 = far differs, 5 = both differ.

**Decision: register A19 (2026-10-10T19:26Z) takes option (c).** The sixth cell is In31WO47_near72 (QE #73 removed).
The registered ΔE_local uses the candidate that `select_near.py` selects on the H-L-relaxed In31WO48. The other
candidate is reported as a sensitivity. A far-order reversal is reported with a flag, with no extra run.

## 2. Settings and their source

| setting | value | source |
|---|---|---|
| cell | 80-atom conventional, a = 10.3060902 A, fixed (`calculation='relax'`, ibrav 0 + CELL_PARAMETERS) | H-L |
| functional / pseudopotentials | PBE; In.pbe-dn, O.pbe-n, W.pbe-spn kjpaw_psl.1.0.0 (~/iwo_amorph/common/pseudo; sha256 equal to the stage-4 set `cern_htcondor/jobs/gen_20260927/pseudo`, re-checked 2026-10-11) | H-L |
| cutoffs | ecutwfc 71, ecutrho 568 Ry | H-L |
| k-points | 3x3x3 for the relaxation, 4x4x4 for the final SCF, Monkhorst-Pack unshifted (0 0 0) | H-L (mesh), stage 4 (no shift) |
| occupations | smearing, gaussian, degauss 0.005 Ry | H-L (stage 4 used mv 0.01) |
| spin, charge | nspin 1, tot_charge 0 (defaults) | H-L |
| ionic thresholds | forc_conv_thr 1.0d-3, etot_conv_thr 1.0d-4, BFGS | H-L (BFGS: stage 4) |
| conv_thr | 1.0d-8 (relaxation and final) | **declared deviation**: stage 4 used 1e-9 (see below) |
| mixing | plain (default), mixing_beta 0.3, electron_maxstep 100 | stage 4. Stage-4 SCFs took 17 to 24 iterations |
| nstep | 300 per segment | stage 4 |
| tprnfor, tstress | .true. (the stress shows the fixed-cell pressure of each defect) | stage 4 |
| nbnd, startingwfc, symmetry | QE defaults | stage 4 |
| verbosity | 'high' (relaxation and final) | **declared deviation** for the relaxation: the stage-4 relax used 'low'. The stage-4 scf_k4 used 'high' |
| pseudo_dir, outdir, max_seconds | './pseudo', './tmp', 1.0d8 (driver.sh resets it to the time left) | amorph machinery |
| executable | pw.x from the NGC QE 7.3.1 GPU container (driver.sh GPU mode), 1 GPU, -nk 1 | **declared deviation**: stage 4 ran QE 7.5 on CPU |

### Declared deviations from the stage-4 protocol (finding 4)
None of these are frozen by H-L. All are identical in the five cells, so every H-L difference is internally
consistent. They were kept, and are to be declared in the RESULTS_LOG submission entry (section 7):
- **conv_thr 1.0d-8** instead of 1e-9.
  - The SCF energy error is ~1e-8 Ry (1.4e-7 eV), far below the 10 meV k-check and the 0.05 and 0.3 eV thresholds.
  - The QE relax default `upscale` = 100 tightens the SCF threshold automatically near ionic convergence.
  - Why it was kept: under the repaired machinery a non-converged SCF is FAILED and not replayed. The looser value
    lowers that risk at the smaller Gaussian 0.005 smearing.
- **verbosity 'high'** in the relaxation. It changes only the output volume. geomsel.py and qeio.py do not depend on it.
- **pw.x QE 7.3.1 GPU** instead of QE 7.5 CPU.
  - PROTOCOL_CERN.md "GPU validation" (2026-09-28) gives dE = 5e-7 Ry with an identical iteration count.
  - **Rule:** H-L energies are never mixed with stage-4 QE 7.5 energies. All ten H-L energies come from one code and
    container.

## 3. Job layout on CERN: `~/iwo_amorph/vac/<name>/`
Each run directory holds:
- the inputs: `relax.in`, `final.tmpl` (k 4x4x4 SCF template), `<name>.xyz`, `logs/`;
- byte-identical copies of the repaired pilot scripts (sha256 equal to `runs/aIO_0p8_s1`, checked on lxplus):
  - `relax_node_vac.sh`, copied from `relax_node_pilot.sh`. Exit 0 = CONVERGED, 1 = CONTINUE, 2 = FAILED;
  - `steps_relax.sh`;
  - `geomsel.py`.
  - Their comments still say "PILOT A15 (aIO_0p8_s1 only)". The logic is unchanged.
- `steps_final.sh`: checks that relax.out has final coordinates, runs `qeio.py newgeom final.tmpl relax.out`, then `run_pw scf 1`;
- `final_node_vac.sh` (new): this is common/final_node.sh with these changes:
  - no pp.x or projwfc.x;
  - scf.in, scf.out and FINAL_STATUS always exist, so the output transfer cannot hold the job;
  - revision 2 exit codes (findings 2 and 3):

    | exit | FINAL_STATUS | condition | DAG |
    |---|---|---|---|
    | 0 | DONE | 'JOB DONE' **and** a converged energy line (`^!`) | done |
    | 2 | SCF_NOT_CONVERGED | 'convergence NOT achieved' (deterministic) | **not replayed** |
    | 1 | FAILED | anything else: scf.out empty or missing, no 'JOB DONE', or no `^!` line (e.g. a max_seconds stop inside the SCF, which QE ends with 'JOB DONE' but without the NOT-converged message), or a lost node | replayed once |

  - **Revision 3 (A19):** DONE also needs 'convergence has been achieved'. A relax.out without 'bfgs converged'
    exits 2 (RELAX_NOT_CONVERGED) before any SCF. See section 8.

- `relax.sub`:
  - resources: 1 GPU, `requirements = regexp("H100|H200", ...)`, 8 CPUs, 64 GB, 60 GB disk;
  - environment and flavour: `QE_NK=1`, flavour "tomorrow";
  - arguments and inputs: `$(seg) 72000`; common driver/qeio/dat2h5/pseudo plus relax.in, steps_relax.sh, geomsel.py;
  - outputs: relax_s$(seg)_results.tar.gz, relax.in, RELAX_STATUS, relax.out, SEGMENT_SUMMARY.
- `final.sub`:
  - resources: 1 GPU on H100 or H200, 8 CPUs, 64 GB, flavour "tomorrow";
  - inputs: common driver/qeio/dat2h5/pseudo plus relax.in, relax.out, final.tmpl, steps_final.sh;
  - outputs: final_results.tar.gz, scf.in, scf.out, FINAL_STATUS.
  - It has **no `hold = True`**: the A15 hold gate belongs only to the slab smearing audit.
- `<name>.dag` (revision 2):
  `JOB RELAX relax.sub / VARS RELAX seg="$(RETRY)" / RETRY RELAX 8 UNLESS-EXIT 2 / JOB FINAL final.sub / RETRY FINAL 1 UNLESS-EXIT 2 / PARENT RELAX CHILD FINAL`.
  - Neither a non-converged relaxation SCF nor a non-converged k4 SCF is ever replayed with identical input.

### Dry checks
**Lxplus, 2026-10-11 (revision 1):**
- `bash -n` passed on all node and step scripts. `ast.parse` passed on geomsel.py. No CR characters.
- Input parse: nat equals the number of positions; ntyp equals the number of species; every UPF exists.
  - Composition and electrons: 704, 705, 698, 699, 699.
  - K_POINTS 3 3 3 / 4 4 4; smearing line 'gaussian', 0.005.
- The executables exist and are executable. All transfer inputs exist, except relax.out for FINAL, which RELAX produces.
- The 5 DAG files are identical.
- No `vac_` job is in the queue.
- Local dry test: `qeio.py newgeom` and `geomsel.py` ran correctly on the stage-4 relax.out with the In31WO48 files.

**Revision 2, 2026-10-11:**
- `make_vac.py` was patched (DAG, final node, 1-based indices in the facts) and re-run in WSL Ubuntu-22.04, env qe.
  - Only the 5 `<name>.dag` and the 5 `final_node_vac.sh` changed in stage/.
  - Every input (relax.in, final.tmpl, *.sub, *.xyz) and every pilot copy is sha256-identical to revision 1.
  - Only the `meta.origin` text of the structures/*.json changed (QE numbers added).
- `final_node_vac.sh` was exercised with a stub driver.sh and canned scf.out files:

  | scf.out case | exit | FINAL_STATUS |
  |---|---|---|
  | converged | 0 | DONE |
  | 'convergence NOT achieved' | 2 | SCF_NOT_CONVERGED |
  | max_seconds stop with JOB DONE and no `!` | 1 | FAILED |
  | empty | 1 | FAILED |
  | missing | 1 | FAILED |

- The 10 files were uploaded to CERN.
  - The upload aborts if a DAG file or a `vac_` job exists.
  - On lxplus: `bash -n` ok, no CR, modes rwxr-xr-x as before. Every DAG has 'RETRY RELAX 8 UNLESS-EXIT 2' and
    'RETRY FINAL 1 UNLESS-EXIT 2'.
  - The full mirror check gives **60/60 files sha256-identical** between local stage/ and ~/iwo_amorph/vac/.
  - No DAGMan files exist, and `condor_q` shows 0 `vac_` jobs.
- No script on CERN common/ reads FINAL_STATUS, so the new status token SCF_NOT_CONVERGED breaks nothing.

## 4. Files
- **Local** (`compute/vacancy/`):
  - `make_vac.py` (the generator; rerunnable in WSL Ubuntu-22.04, env qe) and `build_facts.json`
    (selection entries carry both `index0` and `qe1`);
  - `check_site_rule.py` (new, numpy only): applies the frozen near/far rules to any converged In31WO48 relax.out
    and compares the result with the staged sites;
  - `select_near.py` (A19, frozen, standard library only): the registered near-candidate selector (section 8);
  - `structures/<name>.{json,xyz}`;
  - `stage/<name>/`, a mirror of what was uploaded;
  - `pilot_copy/`: the CERN sources of relax_node_pilot.sh, steps_relax.sh, geomsel.py, qeio.py, driver.sh and final_node.sh.
- **CERN:** `~/iwo_amorph/vac/{In32O48,In31WO48,In32O47,In31WO47_near,In31WO47_near72,In31WO47_far}/`.
  - Revision 2 changed nothing under runs/ or the pilot.
  - Revision 3 (A19) changed one pilot file, `runs/aIO_0p8_s1/steps_relax.sh`, with a backup (section 8).

## 5. Submit commands (only after the user's go; check the SSH master first)
Under A19 all six DAGs go in together. The option (a) and (b) commands of revision 2 are withdrawn.
```
ssh -O check -o BatchMode=yes -o ControlPath=$HOME/.ssh/cm-cern melrashe@lxplus.cern.ch
ssh -o BatchMode=yes -o ControlMaster=no -o ControlPath=$HOME/.ssh/cm-cern melrashe@lxplus.cern.ch \
  'for n in In32O48 In31WO48 In32O47 In31WO47_near In31WO47_near72 In31WO47_far; do (cd ~/iwo_amorph/vac/$n && condor_submit_dag $n.dag); done' </dev/null
```
Once the H-L In31WO48 relaxation converges, run `python select_near.py <its relax.out>` and record the output in
RESULTS_LOG.md. A19 fixes the registered candidate at that point.
Afterwards:
- Record every cluster id in `qe_workflow/cern_htcondor/results/RESULTS_LOG.md` (draft entry in section 7).
- Use `snapshot_jobs.sh` for copies. It selects jobs by IWOJob pattern, for example `bash snapshot_jobs.sh vac_ 15 120`.

Deadline: 17 Oct 10:00 UTC. A relaxation that has not converged by then leaves H-L unresolved.

## 6. Verification findings (2026-10-11) and what was done
Every finding was re-checked independently before acting: a new script (not importing make_vac.py) read the stage-4
relax.out, the staged inputs, iwo_W24d.json and the DAG/node files. All seven findings were confirmed; none was
skipped as wrong.

| # | severity | finding | verified | action |
|---|---|---|---|---|
| 1 | major | Sites chosen from the stage-4 relaxation, not the H-L In31WO48. Submitting all five at once fixes one reading of the rule. | Yes. Staged In31WO48 = stage-4 final coordinates (max dfrac 0). Near margin 0.0104 A, far margin 0.082 A. Removed atoms QE #31 / #33. | **Needs a user decision; cannot be applied by the agent.** Options (a), (b) and (c) are written up in section 1. `check_site_rule.py` was added for the contingency and for option (b). Submission is gated. |
| 2 | minor | `RETRY FINAL 1` replays a deterministic non-converged k4 SCF. | Yes. The old node exited 1 for every non-DONE case, and the DAG had no UNLESS-EXIT. | **Applied.** Exit 2 on 'convergence NOT achieved'; `RETRY FINAL 1 UNLESS-EXIT 2` in all 5 DAGs (local and CERN). |
| 3 | minor | DONE did not require a converged energy. | Yes, an unguarded case. As recalled from QE's electrons_scf (no QE source is available locally), a max_seconds stop inside the SCF loop skips the 'convergence NOT achieved' write, and pw.x still prints 'JOB DONE'. This was not reproduced in a live run; the added check is strictly more conservative either way. | **Applied.** DONE now also requires a line matching `^!`. Tested with canned outputs. |
| 4 | minor | conv_thr 1e-8, relax verbosity 'high' and QE 7.3.1 GPU differ from stage 4. | Yes. Stage-4 relax.in has conv_thr 1e-9 and verbosity 'low'; scf_k4.in has 1e-9 and 'high'. | **Applied as declared deviations** (section 2, and the RESULTS_LOG draft in section 7); the inputs are unchanged. RESULTS_LOG.md lies outside this task's write scope, so the entry must be pasted at submission. |
| 5 | minor | Same site-choice ambiguity: write the reading and the reversal contingency down in advance. | Yes (as 1). | **Folded into 1.** The contingency check is ready (`check_site_rule.py`). Whether a reversal triggers an amendment run or only a note is part of the pending user decision. |
| 6 | minor | 0-based indices risk an off-by-one error. | Yes. index0 30/69, 72/73, 32/33, 17 are QE #31/70, 73/74, 33/34, 18. | **Applied.** Both conventions appear in this report, in `build_facts.json` (`qe1`, `ties_qe1`, `next_distinct_qe1`, `W_qe1`, cation neighbours as [symbol, index0, qe1, d]), in structures/*.json origins, in `check_site_rule.py` output and in the RESULTS_LOG draft. |
| 7 | minor | `relaxed_pbe/iwo_W24d.json` is unrelaxed. | Yes. Max abs dfrac 0.0246 (0.253 A in one component, 0.392 A as a norm); its `checks` hold `W_O_unrelaxed_A`. | **Applied.** Noted in section 1 and in `build_facts.json` (`sources.W.note_iwo_W24d_json`); the json itself was not touched. |

## 7. RESULTS_LOG.md submission entry (draft; paste at the top of the log at submission, fill in the brackets)
```
## 2026-10-[DD] ([HH:MM]Z): H-L crystalline oxygen-vacancy cells submitted (register A17 + A19, decision D-19)
- DAG clusters (condor_submit_dag): In32O48 [id], In31WO48 [id], In32O47 [id], In31WO47_near [id], In31WO47_near72 [id], In31WO47_far [id].
- Cells (80-atom bixbyite, a = 10.3060902 A fixed; build: iwo-tft-research-private/compute/vacancy, BUILD_REPORT.md):
  - In32O48 = structures_v2/relaxed_pbe/bulk_conv.json; In32O47 = minus O index0 17 (QE #18).
  - In31WO48 = W on 24d (index0 4, QE #5), geometry = final coordinates of results/iwo_W24d/relax.out (stage 4).
    NOTE: structures_v2/relaxed_pbe/iwo_W24d.json is the UNRELAXED W substitution, not this geometry.
  - near = minus O index0 30 (QE #31; tie QE #70), W-O 1.8919 A; next W-O pair QE #73/#74 at 1.9024 A (margin 0.0104 A).
  - far = minus O index0 32 (QE #33; tie QE #34), 6.8478 A; next pair QE #30/#71 at 6.7658 A (margin 0.082 A).
  - near72 (A19) = minus O index0 72 (QE #73; tie QE #74), W-O 1.9024 A.
- Site rule (register A19, option c): both near candidates computed; the registered DeltaE_local uses the one that
  select_near.py selects on the H-L-relaxed In31WO48 (shortest W-O bond); the other is a sensitivity. Far stays
  QE #33; a reversal on the H-L host is reported with a flag, with no extra run.
- Settings fixed by A19 for all six cells: conv_thr 1e-8, plain mixing beta 0.3, electron_maxstep 100, nstep 300,
  QE 7.3.1 GPU.
- Frozen by H-L: PBE, pslibrary 1.0.0 PAW, 71/568 Ry, k 3x3x3 relax + k 4x4x4 SCF, Gaussian 0.005 Ry,
  spin-unpolarised, neutral, forces 1e-3 Ry/bohr, energy 1e-4 Ry.
- Declared deviations from the stage-4 protocol (fixed by A19, not frozen by H-L; identical in all six cells):
  conv_thr 1e-8 (stage 4: 1e-9); relax verbosity 'high' (stage 4: 'low'); pw.x QE 7.3.1 GPU, NGC container
  (stage 4: QE 7.5 CPU; GPU validation dE = 5e-7 Ry); smearing Gaussian 0.005 (H-L) vs stage-4 mv 0.01.
  H-L energies are never mixed with stage-4 QE 7.5 energies.
- Machinery: repaired pilot relax node (RETRY RELAX 8 UNLESS-EXIT 2), CONVERGED only with 'bfgs converged' (A19);
  final node exit 2 on a non-converged SCF or a relax.out without 'bfgs converged' (RETRY FINAL 1 UNLESS-EXIT 2);
  DONE requires a '!' energy and 'convergence has been achieved' (A19).
- Status: submitted, no results. Claims stay PENDING until relaxation and k4 check converge
  (then COMPUTED, caveats: PBE, crystalline not amorphous, neutral only, 80-atom cell-limited "far").
```

## 8. A19 changes (revision 3, 2026-10-11 local = 2026-10-10 about 19:35Z; register amendment A19, 2026-10-10T19:26Z)
These changes were applied before any H-L job was submitted. **Nothing was submitted.** The register was not edited.

| A19 item | what was done | files |
|---|---|---|
| (1) sixth cell | **In31WO47_near72** = relaxed stage-4 In31WO48 minus O index0 72 (**QE #73**), W-O 1.90237 A. Its C2 partner is index0 73 (QE #74), at the same distance. `make_vac.py` builds it exactly like In31WO47_near (index0 30 = QE #31, 1.89194 A): same source block, same generator, same checks, and asserts that index0 72 is the lowest index of the next-distinct pair at 1.9024 A. The cell has 79 atoms (In31 W O47), 699 electrons, symmetry P1, 14 / 36 irreducible k. Cation neighbours of the removed O: W 1.9024 A, and In index0 40/55/47 (QE #41/#56/#48) at 2.385/2.400/2.446 A, so W and 3 In become 5-fold. | `make_vac.py` (NAMES, NEAR72, the cell, `selection.near72` in `build_facts.json`); `structures/In31WO47_near72.{json,xyz}`; `stage/In31WO47_near72/` |
| (2) RELAX convergence | CONVERGED needs 'bfgs converged' **and** final coordinates. After a BFGS failure, QE also prints 'Begin/End final coordinates'. That case now falls through to the geomsel.py rules: CONTINUE from the lowest-energy validated geometry if it is new, otherwise FAILED. | `pilot_copy/steps_relax.sh`, copied byte-identically to `stage/*/steps_relax.sh` (sha256 cf6f515a...) and to the CERN pilot |
| (3) k4 FINAL acceptance | DONE (exit 0) needs 'JOB DONE', a `^!` energy and 'convergence has been achieved', with no 'convergence NOT achieved'. 'convergence NOT achieved' gives exit 2 (SCF_NOT_CONVERGED), which is not replayed. New guard: a relax.out without 'bfgs converged' gives exit 2 (RELAX_NOT_CONVERGED) before any SCF. All other cases give exit 1 (FAILED), replayed once, as in revision 2. The DAG line `RETRY FINAL 1 UNLESS-EXIT 2` was already in revision 2, so the six DAG files are byte-identical to revision 2. | `make_vac.py` FINAL_NODE, which writes `stage/*/final_node_vac.sh` |
| (4) selection script | `select_near.py` (frozen, standard library only), described below | `select_near.py` |
| (5) settings | No change: conv_thr 1.0d-8, plain mixing (the default; no `mixing_mode` line), mixing_beta 0.3, electron_maxstep 100, nstep 300, and QE 7.3.1 GPU (request_gpus 1, which selects driver.sh GPU mode with `/eos/user/m/melrashe/qe/qe-7.3.1-gpu.sif`). `make_vac.py` and the dry check now assert these settings for all six cells. | `make_vac.py` |

### select_near.py
- **Input:** the H-L-relaxed In31WO48 relax.out.
  - It needs 'bfgs converged' and a complete 'Begin/End final coordinates' block, otherwise exit 2.
  - It reads the final crystal coordinates.
  - Distances are minimum-image in the fixed cubic cell, a = 10.3060902 A. The printed alat (within 1e-4 A) and the
    identity crystal axes are checked against this cell.
  - It checks for 80 atoms (In31 W1 O48), W at index0 4, and O at every reported index.
- **Output:** the W-O distances of O index0 30, 69, 72 and 73 (QE #31, #70, #73, #74), the six shortest W-O, the
  global shortest with its ties, and the far ordering (O32/O33 against O29/O70).
- **Rule:**
  - Find the global shortest W-O. Distances within 1e-3 A of it are tied (the tolerance of `make_vac.py`), and the
    lowest index among them is selected.
  - If the selected O is in {30, 69}, the registered cell is In31WO47_near. If it is in {72, 73}, it is
    In31WO47_near72. Otherwise the result is NONE (exit 3).
  - Flags: a tie between the two pairs (then the lowest-index rule gives O30), a within-pair split above 1e-3 A
    (broken C2), and a far reversal (FAR_ORDER = REVERSED; A19: flag only).
- **Exit codes:** 0 = selected; 2 = input not usable; 3 = neither candidate.
- **Test on the stage-4 relax.out** (`cern_htcondor/results/iwo_W24d/relax.out`, sha256 67f29bad...):
```
bfgs converged in  19 scf cycles and  18 bfgs steps; Final energy             =  -15496.3666036746 Ry
cell: cubic, a = 10.3060902 A (fixed); W = index0 4 (QE #5); index0 = 0-based, QE # = index0+1
W-O distances of the candidates:
  O index0 30 (QE #31)     1.89194 A
  O index0 69 (QE #70)     1.89194 A
  O index0 72 (QE #73)     1.90237 A
  O index0 73 (QE #74)     1.90237 A
shortest W-O bonds: 30/#31 1.89194, 69/#70 1.89194, 72/#73 1.90237, 73/#74 1.90237, 25/#26 2.15232, 27/#28 2.15232 (index0/QE#, A)
global shortest: O index0 30 (QE #31) 1.89194 A; tied within 0.001 A: index0 [30, 69] = QE # [31, 70]
gap d(O72 pair) - d(O30 pair) = +0.01043 A (stage-4 value +0.0104)
far: O index0 32 (QE #33) 6.84785 A, O index0 33 (QE #34) 6.84785 A, O index0 29 (QE #30) 6.76580 A, O index0 70 (QE #71) 6.76580 A
largest W-O: 32/#33 6.84785, 33/#34 6.84785, 29/#30 6.76580, 70/#71 6.76580, 65/#66 6.63037, 67/#68 6.63037 (index0/QE#, A)
FAR_ORDER = kept: O32/O33 (QE #33/#34) 6.84785 A > O29/O70 (QE #30/#71) 6.76580 A, margin +0.08205 A
REGISTERED_NEAR = In31WO47_near (O index0 30 (QE #31), W-O 1.89194 A); sensitivity = In31WO47_near72 (O index0 72 (QE #73), W-O 1.90237 A)
exit 0
```
- **Synthetic edge cases** (edited copies of that file):

  | case | exit | result |
  |---|---|---|
  | O72/O73 pulled to 1.880 A | 0 | near72 |
  | O72/O73 at 1.8923 A | 0 | TIE flagged, near |
  | O25/O27 pulled to 1.85 A | 3 | NONE |
  | O29/O70 pushed to 6.90 A | 0 | FAR_ORDER = REVERSED |
  | 'bfgs converged' replaced by a 'bfgs failed' line | 2 | rejected |
  | alat changed | 2 | rejected |
  | O72 1.880 / O73 1.900 | 0 | split flagged, near72 |

### Stub tests (WSL Ubuntu-22.04, env qe)
**steps_relax.sh**, with run_pw stubbed to copy a canned relax.out:

| canned relax.out | revision 2 | A19 |
|---|---|---|
| stage-4 relax.out (converged) | CONVERGED | CONVERGED |
| same, with 'bfgs converged' replaced by a 'bfgs failed' line (final coordinates still printed) | **CONVERGED (the trap)** | **CONTINUE** (best = geometry 18, best_new=yes) |
| same, with one SCF 'convergence NOT achieved' | FAILED | FAILED |

**final_node_vac.sh**, with driver.sh stubbed:

| case | exit | FINAL_STATUS |
|---|---|---|
| converged | 0 | DONE |
| 'convergence NOT achieved' | 2 | SCF_NOT_CONVERGED |
| '!' + JOB DONE, but no 'convergence has been achieved' | 1 | FAILED |
| max_seconds stop | 1 | FAILED |
| empty scf.out | 1 | FAILED |
| missing scf.out | 1 | FAILED |
| relax.out without 'bfgs converged' | 2 | RELAX_NOT_CONVERGED, driver not run |

In every case all four transfer files exist.

### Dry checks
The same stdlib script was run on the local stage/ and, on lxplus, on ~/iwo_amorph/vac with ~/iwo_amorph/common/pseudo.
Both report ALL CHECKS PASSED (6 dirs).
- File set per dir. No CR characters. `bash -n` on every .sh. `ast.parse` of geomsel.py. Node scripts executable.
- For relax.in and final.tmpl:
  - nat equals the number of positions: 80, 80, 79, 79, 79, 79;
  - ntyp equals the number of species and the species used; every UPF exists on CERN;
  - composition and electrons: 704, 705, 698, 699, 699 (near72), 699;
  - K_POINTS 3 3 3 0 0 0 / 4 4 4 0 0 0;
  - smearing 'gaussian', degauss 0.005; cutoffs 71/568;
  - conv_thr 1.0d-8, mixing_beta 0.3, electron_maxstep 100, no mixing_mode; nstep 300, BFGS, 1.0d-4 / 1.0d-3;
  - cell cubic with a = 10.3060902; positions in crystal units.
- **The six inputs differ only in nat/ntyp, the W species line and the positions.** With those removed, the six
  relax.in are identical, and so are the six final.tmpl.
- Each vacancy cell equals its parent with exactly one O position line removed:
  - In32O47 = In32O48 minus index0 17;
  - near = In31WO48 minus 30;
  - near72 = In31WO48 minus 72;
  - far = In31WO48 minus 32.
- The DAG, node, step and geomsel files are identical across the six. The two .sub files differ only by the name,
  and both request 1 GPU.
- A negative test confirmed that the check is not vacuous: an injected mixing_beta change and an injected DAG change
  were both reported.

### Changes against revision 2 (local and CERN)
- **Changed in the five existing dirs:** only `steps_relax.sh` and `final_node_vac.sh`.
  - Every relax.in, final.tmpl, *.sub, *.dag, *.xyz, geomsel.py, relax_node_vac.sh and steps_final.sh is byte-identical to revision 2.
  - structures/*.json and *.xyz of the five cells are unchanged.
- **New:** `stage/In31WO47_near72/` (12 files plus logs/.keep).
- **Upload:** one tar over the existing ControlMaster.
  - It aborts if any `*.dag.*` DAGMan file exists in vac/, if condor_q shows a vac job, or if In31WO47_near72 already exists.
  - File modes are 755, as before.
- **Mirror check after the upload:** **72/72 files sha256-identical** between local stage/ and ~/iwo_amorph/vac/.
  No DAGMan files exist, and condor_q shows 0 vac jobs.
- `make_vac.py`, `BUILD_REPORT.md`, `select_near.py` and `check_site_rule.py` are local only. They were never on CERN.

### A15 pilot (`~/iwo_amorph/runs/aIO_0p8_s1/`)
- `steps_relax.sh` was patched with the same rule (sha256 76fec04f... -> cf6f515a..., mode 644 kept).
  - The backup is `steps_relax.sh.pre_A19` (cp -p).
  - The new file was written to a temporary file, checked by sha256 and moved into place.
- A before/after hash of every top-level file (DAGMan logs excluded) shows only steps_relax.sh changed, plus the new backup.
- Not touched: the pilot DAG (cluster 12885850, running), its relax_s0 node (12885853, running), every other pilot
  file and every other runs/* directory.
  - The running segment keeps the copy it received at start (the old rule).
  - The A19 rule applies from the pilot's next segment.

### Notes
- `~/iwo_amorph/common/steps_relax.sh` on CERN already has an A19 'bfgs converged' edit, with the backup
  `common/steps_relax.sh.pre_A19` dated 2026-10-10 21:29 CEST.
  - This task did not make that edit and did not touch common/.
  - Which slab runs use it, and whether the 16 slab DAGs should take the rule, is the separate user decision.
- "A failed SCF exits 2" is implemented as a deterministic SCF failure ('convergence NOT achieved').
  - A missing or empty scf.out, a killed node, or a max_seconds stop without a '!' energy still exits 1 and is
    replayed once, as in revision 2.
  - If A19 is meant to forbid that single replay too, the DAG line would become `RETRY FINAL 0` (not done).
- `check_site_rule.py` (revision 2) accepts any relax.out that has final coordinates. For the A19 selection use
  `select_near.py`, which requires 'bfgs converged'.

## Submission (A19 H-L, 2026-10-10 UTC)
Submitted from lxplus913 over the existing ControlMaster (BatchMode, ControlMaster=no). The user approved the
submission through the CERN-action permission prompt. Command per cell:
`(cd ~/iwo_amorph/vac/$n && condor_submit_dag -batch-name vac_$n $n.dag)`.

Guards checked just before the submission (all passed):
- Kerberos ticket valid (krbtgt until 2026-10-11 22:41 CEST); AFS token valid.
- Each of the six `$n.dag` was present, with no `*.dag.*` DAGMan files and only `logs/.keep` in logs/.
- No `vac_` job was in the queue.
- Local stage/ and ~/iwo_amorph/vac/ were sha256-identical for all 66 top-level files, re-checked at 19:50:52Z.

| cell | DAGMan cluster | submit time (UTC) | RELAX node (relax_s0) | node status at 19:52:36Z |
|---|---|---|---|---|
| In32O48 | 12886353 | 2026-10-10T19:52:21Z | 12886359 | idle |
| In31WO48 | 12886354 | 2026-10-10T19:52:21Z | 12886360 | idle |
| In32O47 | 12886355 | 2026-10-10T19:52:22Z | 12886361 | idle |
| In31WO47_near | 12886356 | 2026-10-10T19:52:22Z | 12886362 | idle |
| In31WO47_near72 | 12886357 | 2026-10-10T19:52:23Z | 12886363 | idle |
| In31WO47_far | 12886358 | 2026-10-10T19:52:23Z | 12886364 | idle |

- All six DAGMan jobs were running (status 2), and each dagman.out logs "Submitting HTCondor Node RELAX job(s)".
- The FINAL nodes were not yet submitted; that is expected, since FINAL is a child of RELAX.

**Queue, user melrashe**

| | `condor_q -af` rows | `-totals` (excludes DAGMan jobs) | idle | running | held |
|---|---|---|---|---|---|
| Before (19:52:21Z) | 42 | 25 | 17 | 7 | 1 |
| After (19:52:36Z) | 54 | 31 | 23 | 7 | 1 |

- The difference is exactly +6 DAGMan jobs and +6 RELAX nodes.
- The 42 pre-existing rows are unchanged (cluster.proc, status, batch name).
- The one held job, 12885292 (aIO_2p0_s1 relax_s1), was already held before this submission and was not touched.
- The A15 pilot (12885850 / 12885853) is still running.

Next: the outputs must be copied with snapshot_jobs.sh, because running jobs lose Kerberos. The registered near
candidate (O30 or O72) is selected with `select_near.py` on the H-L-relaxed In31WO48 relax.out, once DAG 12886354
converges with 'bfgs converged'.
