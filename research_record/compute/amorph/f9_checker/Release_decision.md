# D-42 draft v5: read-out release decision (Codex 2026-10-12T20:44Z: policy GO; checker/writers FIX_FIRST, items fixed; NOT logged, NOT committed)
F9 code is now draft v15 (Codex FIX_FIRST on F9 v5 to v14, 2026-10-13/14; digest_13oct_v6.md to digest_13oct_v8.md, golist/digest_checker_v9.md to _v15.md). This file's text is v5 apart from the [F9 v6-v15] references, the corrected review statement in C, one D-43 scope wording and the v9-v15 release gates and A15 table below; v5 to v14 are kept as Release_decision.md.v5 to .v14.

v4 is kept as Release_decision.md.v4 (v3, v2, v1 likewise). v5 changes (Codex 20:44Z), each with rejection tests (digest_13oct_v5.md):
1. **Attempt disposition.** A C3 attempt without output must be explained by its own terminal event in the slot user log: a non-zero exit, a signal or an abort. A normal exit 0 without output, or no terminal event, makes the inventory underivable, which blocks qualification. [F9 v6 tightens this: digest_13oct_v6.md, blocker 1.] [D-43 wording change (Codex v7 review: GO, prospective; encoded in F9 v7/v8; not yet logged in D-43): "An unresolved C3 attempt makes only its own frozen slot UNRESOLVED and blocks only the claims of that cell and geometry. Every attempt is retained explicitly. Ambiguous ownership, or a corrupted global inventory, blocks all affected claims. The A15 three-role requirement remains global."]
2. **As-run input.** FINAL, reference and companion inputs must be the scf.in that pw.x actually read. Its sha256 is recorded in the D-24 lineage file (`sha256 <h> scf.in as-run ...`, steps_final.sh.D24:193-200), and that lineage file must itself be a certified run file (rc7 binds lineage_<job>.dat). Any other exported .in is refused, and a missing as-run line is an unresolved A14 gap.
3. **Both endpoints fresh.** The start mode of both C3 endpoints is derived from their as-run inputs. A density-seeded 0.001 Ry reference never counts, and the FAIL veto applies whatever the start mode.
4. **Export formats.** The D-24 exp/MANIFEST format (`# run <name> cluster <N> written_utc <t>`, then `<basename> <bytes> <sha256>`) is supported. Archive members are bound by recomputing their sha256 from a listed archive.
   - Direct listing counts only in the in-job D-24 MANIFEST.
   - A sha256sum record may vouch for returned archives only, so a member list generated later is never provenance.
   - FINAL-type runs require the in-job MANIFEST. For C3 attempts its cluster must match and written_utc must not be after the job's end.
5. **Wording.** "MM/DD stamps are refused" is replaced (F9 below).

v4 header (kept):
# D-42 draft v4: read-out release decision (Codex 2026-10-12T20:25Z: policy GO; checker/writers FIX_FIRST, six items fixed)

v3 is kept as Release_decision.md.v3 (v2, v1 likewise). v4 changes (Codex 20:25Z), each with rejection tests (digest_13oct_v4.md):
1. **Force blocks.** A force block counts only if its atom indices are 1..N exactly once and each printed type equals the input type.
2. **Convergence.** These are separate assertions:
   - the registered ionic thresholds (forc_conv_thr 1e-3 AND etot_conv_thr 1e-4; QE defaults recorded as such);
   - the final residual (max force component <= 1e-3 Ry/bohr; last energy change in the converging segment <= 1e-4 Ry);
   - no terminal SCF failure in the active epoch. Earlier-epoch failures are disclosed, not vetoed.
3. **Input provenance.** Every input and output a writer uses is bound to the run's export manifest (sha256), or to snapshot metadata. FINAL, companion and reference exports must contain every certified run file. Missing provenance makes a record underivable.
4. **C3 inventory.** It is derived from the frozen F10 C3 plan plus one HTCondor user log per slot. Every submitted attempt, fresh or density-seeded, is accounted for; every exported attempt has exactly one report, and every report belongs to an attempt.
5. **A31(f) roles.** They are derived from bound relaxation_lineage status records at the (extension-aware) cutoff; nothing is copied from parameters.
6. **Job logs.** The real lxplus header format ('NNN (c.p.s) MM/DD HH:MM:SS') is supported. Year and zone come only from a bound offset-evidence file with a validity window (CEST until 2026-10-25T01:00Z); the clock is never read.
- Policy changes accepted by Codex (GO): polish restart gates; the density-seeded FAIL veto; no admission record -> no exploratory read-out; the 80 h export window; retained MV H-H companions; terminal-preserving rescue limits. A conservative geometry-hash rejection is accepted and is **never overridden manually**.

v3 changes (Codex 15:56Z):
1. **F9 v3.** Records are now written by blind writers (f9_writers.py) and re-derived by the checker from their sha256-bound sources. The settings-hash field set is frozen.
2. **Numbers and inventory.** Qualifications and restart gates are judged on numbers against the tolerances, and the mandatory gate inventory is derived from the complete lineage.
3. **Dates.** There is no date override; dates move only through a verified extension record.
4. **A15 candidate.** Choosing the candidate width can no longer bypass a failed C3, and C3 is read from the complete inventory.
5. **Tests.** 54 end-to-end tests on synthetic fixtures.
6. **F5.** Restart gates also apply to multi-segment polishes (new; flagged for Codex).
7. **F7.** MV-geometry C3 companions are added for the 0.7 nm H-H reference, and A39 read-outs run only if admitted.
8. **F12.** H2 is confirmed by Codex. The H3 note gives the request-time explanation and marks arrival times "unavailable".
9. **F13 and release (C).** Export sizes are checked against the quota. Release now also needs Codex's audit of the writers and of their first real records.

Changes from v1 (Codex 15:08Z, applied in v2):
1. **F9 completed and implemented** as a standalone checker. v2 had 58 tests; v3 supersedes it. It requires exact run/geometry/settings linkage, A19 timing, inherited gates, final qualification, genuine MV-parent → Gaussian lineage for 'polished', named A15 roles and widths, provisional status, and applicable fresh-start C3 coverage.
2. When a certificate changes, the bound cell records and comparisons are recomputed (B.2b).
3. C4 polishes need a fresh final-geometry qualification, zero-step included (F5).
4. A bare SCF failure means park (F6). "MV against MV" describes geometries; the FINAL smearing stays Gaussian.
5. Thin cells may be released before the cutoff once F1-F13 are implemented and passed (C).
6. The pinned venv is required (F11). A14 gaps are preserved, and the AFS transfers and quota are verified (F13, new).
7. Housekeeping items for the user's go (F12).

D-41 is taken (48 h segments, 14:56Z), so this is D-42. One decision row covers A37, A38, A39, A40 and this release. If they are logged separately, they are renumbered D-42 to D-46.

---

**D-42 (draft).** The first reader command that computes an electronic quantity (`python -m analysis cell`) runs only after F1-F13 are committed, with their sha256 recorded in this row, and only on certificates for which F9 returns CLAIMS_OK. After that, the commands follow the fixed order in section B. 2.0 nm read-outs also wait for the cutoff (A39 sight rule).

## A. Frozen first (committed, hashes in the D-42 row)
- **F1-F4.** A37 (H-N endpoint; formal reporting override; C2/C5 cut; footnote †); A38 (result-informed override of the ML_VALIDATION.md:32 stop action; trigger kept); A39 (cutoff read-outs); A40 (C3 companions; density-seeded exclusion; zero-step reuse; 2.0 nm C3/C6 scope).
- **F5. C4 polish: failure route and qualification.** Polishes 12904172 (0.7 nm) and 12904173 (1.0 nm); settings as submitted 13:17Z [fill from checks/gpumax_work/submit_20261012T131733Z.log].
  - **Infrastructure stop** before the first energy: one repeat with identical input.
  - **FAILED [scf], or no verified 'bfgs converged' by 17 Oct 10:00 UTC:** one attempt only. There is no rescue: no other smearing, mixing or solver.
    - C4 is MISSING at that thickness, and the class is reported on the MV geometry only, labelled "C4 polish not converged".
    - A partial polish geometry is never certified 'polished' and gets no A39 read-out.
  - **Fresh final-geometry qualification (required, zero-step included; Codex 15:08Z).**
    - After 'bfgs converged', a fresh-start 'scf' with forces is run at the polish's final geometry with the polish relaxation settings (Gaussian 0.005 Ry, same cutoffs, k-points, nbnd, nspin, dipole keys, labels).
    - It is compared with the polish's last SCF within 1e-5 Ry in F and 1e-3 Ry/bohr in max |ΔF| (A35 tolerances).
    - It is due by 20 Oct 12:00 UTC. A non-converged qualification fails. An infrastructure stop before the first energy may be repeated with identical input. It needs its own submit with the user's go.
    - A failed or missing qualification means C4 is MISSING at that thickness.
  - **Restart gates of a polish (v3, new; flagged for Codex).** If a polish spans more than one segment with identical settings, the A35 restart gate (1e-5 Ry, 1e-3 Ry/bohr) applies at every boundary. A failed or unevaluable gate means C4 is MISSING at that thickness (the F9 inventory).
    - It is set before any polish output has been read by us. It adds no stop: chains continue as before.
  - **Zero-step convergence** (positions hash equal to the MV parent): the existing A26 FINAL is the polished reference only under A40 rule 4 (i)-(vi), which includes the qualification above. Otherwise a new polished FINAL runs.
  - **After convergence and qualification:** the polished FINAL (A26 settings) runs at the CPU-3 priority. The FINAL may run concurrently with the qualification, but certification waits for the qualification result.
- **F6. Bare route and H-H.**
  - aIWO_0p7_s1_bare stays on MV 0.01, the registered aIWO relaxation family.
  - **"MV against MV" describes the geometries.** H-H at 0.7 nm compares:
    - aIWO_0p7_s1 at its MV-converged geometry (A26 FINAL 12902517);
    - aIWO_0p7_s1_bare at its MV-converged geometry.

    Both FINALs are Gaussian 0.001 Ry (A26); the FINAL smearing stays Gaussian. The C4-polished OH geometry is never used for H-H.
  - **Bare FAILED [scf]: park** (Codex 15:08Z). segment_stop STOP armed, the retry not released, the DAG removed only on the user's go (D-35 precedent). H-H 0.7 nm is then UNRESOLVED. Any other route (for example MV plus aids) would need its own amendment; none is pre-declared. A Gaussian rescue is excluded, because it would break the MV-geometry pairing.
  - **Not converged at the cutoff:** H-H 0.7 nm UNRESOLVED. The A39 read-out at G* is an observation only. The 2.0 nm part of H-H stays UNRESOLVED (D-35).
- **F7. CPU priority order.** One list, sorted by JobPrio. Thin-cell jobs use 34-CPU slots and may run concurrently.
  - **CPU-1:** A15 audit FINALs (A31(a)) of the converged 2.0 nm roles (comp; aIWO_2p0_s1 or the s2 backup; aIO_2p0_s1 or the s2 backup). 0.001 Ry first, then 0.002 and 0.005 Ry. Section 3 priority 1.
  - **CPU-2:** other primary FINALs of converged cells: aIWO_2p0_s2 and aIO_2p0_s2 (when not used as backups), then aIWO_0p7_s1_bare (termination pair).
  - **CPU-3:** thin-cell H-N controls:
    - polish qualifications and polished FINALs (0.7, then 1.0 nm);
    - C3 companions (A40 order), including the MV-geometry companions of aIWO_0p7_s1 for the H-H reference (A40 rule 3);
    - C6 (0.7, then 1.0 nm);
    - C1 FINALs (0.7 nm).
  - **CPU-4:** A34(i) val CPU-fallback frames, before 17 Oct 10:00 only (A38).
  - **CPU-5:** A39 cutoff read-outs in the A39(c) order, only those admitted on 14 Oct (q + T + X ≤ 80 h). There is no read-out otherwise, and no automatic fallback.
  - **CPU-6:** non-duplicated 2.0 nm C3 companions where primary qualification needs them (A40 item 7). 2.0 nm C6 is cut.
- **F8. Claims table** (annex), frozen as its own file claims_table_v1.md, with its sha256 in the D-42 row.
- **F9. Certificate assertions v3 (standalone, not the frozen reader).** Three files make up F9: cert_assert.py (checker), f9_writers.py (blind record writers) and f9_common.py (frozen definitions). They are frozen with their sha256s and the test file's sha256.
  - **Use.** F9 runs after `certify`/`validate-cert` and before `cell`, under the F11 venv: `python -I -B cert_assert.py <cert> [--reports …] [--extension <record>] --json <out>`. Exit code 0 (CLAIMS_OK) is required.
  - **Why.** certify.py checks only that evidence files are sha256-bound (certify.py:231-245, 347-382). Codex: "Hash binding alone does not establish evidence semantics."
  - **Records are re-derived, not trusted (Codex 15:56Z, item 4).** Every evidence record (schema iwo-f9-evidence/2) is written by f9_writers.py as a pure function of sha256-bound sources:
    - pw.x inputs;
    - QE text outputs, read through the A39(a6) allowlist with its deny assertion;
    - HTCondor job logs with an explicit time zone: 'Z' or offset stamps, or naive stamps, or the real lxplus header format 'NNN (cluster.proc.sub) MM/DD HH:MM:SS' (v4). Naive and MM/DD stamps take their year and UTC offset only from a bound four-line offset evidence (utc, local, valid_from, valid_to) captured on the submit host; the clock is never read;
    - snapshot metadata;
    - `certify` stdout (allowlisted keys) and sealed rc7 reports (allowlisted keys);
    - certificates and other records;
    - for an extension, the redacted confirmation and its work-chat entry.

    The checker resolves the sources by sha256, re-runs the same derivation, and rejects the record if the result differs or if the writer fingerprint differs from the frozen one. A PASS label, an edited number, an omitted gate or a dropped segment cannot pass; each case is tested.
  - **Record types:**
    - relaxation_lineage: the complete, contiguous segments from s0/p0; epochs; A19 timing from the job log; the mandatory gates with their numbers;
    - qualification_scf;
    - final_run;
    - c3_companion_run: start mode and diff gate derived from the inputs;
    - c4_polish;
    - a15_provisional;
    - readout_manifest: the complete C3 inventory;
    - cutoff_selection: A39(a);
    - cern_extension.
  - **Frozen settings-hash field set (Codex item 4; f9_common.SETTINGS_FIELDS).**
    - Included &CONTROL keys: tefield, dipfield, lelfield, lorbm.
    - Included &SYSTEM keys: ibrav, nat, ntyp, ecutwfc, ecutrho, ecutfock, occupations, smearing, degauss, nspin, nbnd, tot_charge, tot_magnetization, starting_magnetization(i), input_dft, exx_fraction, screening_parameter, nqx1-3, assume_isolated, edir, emaxpos, eopreg, eamp, nosym, noinv, vdw_corr, lda_plus_u, hubbard_u(i), noncolin, lspinorb.
    - Included &ELECTRONS keys: conv_thr, mixing_beta, mixing_mode, mixing_ndim, electron_maxstep, diagonalization, diago_full_acc, scf_must_converge.
    - Included cards: ATOMIC_SPECIES (label, mass, UPF, in order), K_POINTS, the per-atom label sequence, and the cell rounded to 1e-4 Å.
    - Excluded on purpose (run-control, restart and driver keys): calculation, title, prefix, outdir, pseudo_dir, restart_mode, startingpot, startingwfc, max_seconds, verbosity, disk_io, wf_collect, tprnfor, tstress, iprint, forc_conv_thr, etot_conv_thr, nstep, ion_dynamics, upscale, bfgs_ndim, trust_radius_*, w_1, w_2.
    - Smearing names are normalised: gauss = gaussian; m-v, marzari-vanderbilt and cold = mv.
    - Any change to the set is a new F9 version.
  - **Numbers, not labels (Codex item 1).** The qualification and every restart gate are judged on finite ΔF and max |ΔF| over all 3N force components, recomputed from the bound outputs.
    - A gate or qualification passes only if |ΔF| ≤ 1e-5 Ry and max |ΔF| ≤ 1e-3 Ry/bohr (both inclusive).
    - The qualification must also be a fresh start with the relaxation's frozen settings hash, compared with the relaxation's last SCF at the final geometry, and completed after convergence and by the qualification deadline.
  - **Mandatory restart-gate inventory (Codex item 1).** The inventory is derived from the complete lineage: every boundary between consecutive segments of the last settings epoch. It applies to:
    - the gated cells aIWO_0p8_s2, aIWO_2p0_s2 and aIWO_2p0_comp_s1;
    - the gated routes A35, A36 and A36-conditional;
    - C4 polishes (F5, new in v3).

    A missing or unevaluable gate fails; an omitted gate never means "not exercised". For ungated registered routes the inventory is empty by rule, and F9 states this.
  - **Dates (Codex item 2).** These dates are frozen in f9_common:
    - cutoff 17 Oct 10:00:00Z;
    - qualification deadline 20 Oct 12:00:00Z;
    - last submission 18 Oct 22:00:00Z;
    - exploratory export 20 Oct 18:00:00Z.

    The only thing that moves them is a verified cern_extension record, which shifts every date not yet passed when it was logged. The record is re-derived, and its work-chat entry must contain the confirmation sha256 under a heading at the logged minute. There is no date option: `--cutoff` and `--qualification-deadline` are rejected by the CLI (tested).
  - **C3 and the A15 candidate (Codex item 3; A31(e)).** 'qualified' needs the complete C3 inventory: a readout_manifest record over every C3 output of the F10 manifest. Every applicable comparison (same cell, same geometry) is examined:
    - any FAIL, fresh or density-seeded, rejects the claim at every width;
    - at the candidate width, a fresh C3 PASS is required, with this run as the compared width against the 0.001 Ry reference at this geometry;
    - at 0.001 Ry, fresh PASS at 0.002 and 0.005 Ry is required, with this run as the reference;
    - comparisons at another geometry never count (a polish never qualifies its MV parent geometry).
  - **Unchanged from v2:**
    - 'converged': lineage at the certified geometry; A19 ≤ cutoff; no failed gate, own or inherited (parent lineage records and parent certificates, recursively); the qualification where A35, A36 or F5 requires it.
    - 'exploratory': linked to a lineage or cutoff_selection record at the certified geometry.
    - 'mv': an MV-only lineage passing every 'converged' assertion.
    - 'polished':
      - an A27 C4 cell, never aIWO_2p0_s2 or aIWO_0p8_s2;
      - a genuine MV parent certificate passing 'converged' and 'mv' recursively;
      - a Gaussian 0.005 polish from the parent geometry to the certified geometry, with its qualification;
      - a final_run binding the run files, geometry and UPFs, with a Gaussian FINAL;
      - zero-step reuse only under A40 rule 4.
    - 'qualified': a final_run at exactly the certified width; the A31(d) record checked against a sealed rc7 audit (named roles, substitutions, widths, non-null candidate, "provisional (EA not evaluated)"). C3 reports alone never qualify.
    - --reports flags STALE records (B.2b).
  - **Tests (54, synthetic fixtures only; digest v3).** Each runs end to end from raw synthetic inputs, outputs (with decoy Fermi and eigenvalue lines), job logs and certify stdout. They cover:
    - the three Codex examples;
    - the gate inventory (pass, energy fail, force fail, unevaluable, omitted, dropped segment);
    - qualification (tolerances, freshness, deadline, edited numbers);
    - extension (verified, late, forged, no revival);
    - C3 and the candidate (FAIL at either width, its own C3, density-seeded FAIL, another geometry, missing width, tampered inventory entry);
    - MV-parent lineage, inherited failures, zero-step identity, A15 roles;
    - the writers (allowlist, settings hash, naive CEST logs with offset evidence, cutoff selection and ties, CLI);
    - sight abort, output allowlist and staleness;
    - a cross-check against the frozen rc7 `_evidence_ok`.
  - **v5 additions (Codex 20:44Z).**
    - Explained dispositions for attempts without output.
    - As-run scf.in binding through the certified lineage file.
    - Freshness of both C3 endpoints.
    - The D-24 MANIFEST format and archive-member provenance (recomputed member hashes; direct listing only in the in-job manifest).

    Tests: 75 (digest v5).
  - **[F9 v6] (Codex 2026-10-13 ~01:45Z; draft).** See digest_13oct_v6.md (blockers 1 and 2). Tests: 88 (digest v6).
  - **[F9 v7] (Codex v6 review 2026-10-13T02:10Z; draft).** See digest_13oct_v7.md (four items and the rulings). Tests: 104 (digest v7).
  - **[F9 v8] (Codex v7 review; draft).** See digest_13oct_v8.md (three items and the rulings). Tests: 112 (digest v8).
  - **[F9 v9] (Codex v8 review, FIX_FIRST; draft).** See golist/digest_checker_v9.md. Tests: 123.
    - Every relaxation segment must be the registered fresh start (restart_mode / startingpot / startingwfc with the QE defaults resolved; `restart` implies `startingpot='file'`); RELAX asserts it.
    - A bestvalid member counts only if it is the validated minimum recomputed from the segment's bound evaluations. A paused CONTINUE resumes from the returned relax.in; only a FAILED segment may restart from its verified best validated geometry (Codex ruling, conditional approval).
    - **Section-3 rescues (rescue DAG, attempt<N+1>)** need a REGISTERED authorization (f9_common.REGISTERED_RESCUE_AUTHORIZATIONS, empty in this draft): run, preceding attempt, the lineage's node-execution budget and its basis. The basis is either exhaustion (the previous attempt used all 9 executions of RELAX + RETRY 8) or a **prospective suspension rule** logged no later than the previous attempt's last terminal event. Each authorization is used once. The record (schema iwo-f9-transition/2) restates the remaining executions (never reset: HTCondor resets retries on a rescue by default), the prior rescue use and the terminal-failure status, and each must equal the derived value. **The ~15 Oct pause continuation therefore needs its suspension rule logged before the pause; a section-3 record alone is refused.**
    - No section-3 reset or rescue may follow an SCF failure after a rescue start (no revival after a terminal A35/A36 failure).
    - Label splits only in the A25/A30/A34 cell scope (aIO_2p0_s1; aIO_1p5_s1, aIO_2p0_s2, aIWO_1p5_s1, aIWO_2p0_comp_s1, aIWO_2p0_s1, aIWO_2p0_s1_bare, aIWO_2p0_s2; aIWO_1p0_Al2O3_s2), In -> In1/In2 and O -> O1/O2 only.
    - **Registered FINAL template.** A positive certificate that needs a FINAL requires its settings (width excluded) to equal the registered FINAL template of the cell (f9_common.REGISTERED_FINAL_TEMPLATES, empty in this draft). Cutoffs, k-mesh, spin and SCF settings can no longer drift.
    - **Release gates added by v9:** the FINAL template keys (from the A26 / polished-FINAL templates) and any rescue authorization must be registered (logged prospectively) before use; the capture tools and the first real-record audit remain release gates.
  - **[F9 v10] (Codex v9 review, FIX_FIRST; draft).** See golist/digest_checker_v10.md. Tests: 133.
    - **DAG allowance from attempt 1 (ruling a):** 9 RELAX node executions (one per cluster; guard-only node attempts count; an eviction / re-execution inside one cluster does not). It grows only by an authorized rescue: the registered A39 administrative rescue adds 9, once per chain, only after exhaustion with the last segment CONTINUE or a non-[scf] FAILED category. A suspension or continuation grants nothing.
    - **Pause binding:** a suspension rule must predate the actual pause start. For the 13 Oct full stop (pause from 2026-10-13T03:17Z) the continuation needs the result-informed administrative-continuation amendment A43 (drafted: drafts13oct/A43_pause_continuation_draft.md; D-46), logged before resumption and preserving each chain's remaining executions, prior rescue use, terminal status and gates.
    - **Relabeling (ruling c):** alternating In1/In2 and O1/O2 atom map, balanced counts, construction equivalence with the bound unsplit input (only labels and ntyp differ), and an authorized cell for the declared resource route (A25 / A30 / A34), kept separate from the A35/A36 settings route. ntyp leaves the epoch key.
    - **Ruling (b):** README section 3 covers a geometry-only failure reset from the independently verified bestvalid; A35/A36 terminal failures and the A30 rollback rule override it ([infra] reset keeps the segment input); settings or failure-handling changes need an amendment.
  - **[F9 v11] (Codex v10 review, FIX_FIRST; draft).** See golist/digest_checker_v11.md. Tests: 139.
    - A new attempt whose first execution is guard-only needs the same verified rescue record (authorization, budget, rescue file) as a pw.x first execution.
    - A split needs both registered alternating splits (In and O); one alone fails.
    - G* applies the registered minimum and tie rules to all eligible evaluations before deduplication.
    - Every rescue binds its rescue file: the RELAX node's remaining RETRY + 1 must not exceed the preserved remaining executions (DAGMAN_RESET_RETRIES_UPON_RESCUE = False plus count enforcement; existing files are not repaired by the setting).
    - Historical rescues (the A15-era aIO_2p0_s1 rescue DAG) are their own basis with their contemporaneous authorization, never A39's +9.
    - Split resource routes are bound to the split segment's own cluster (RequestGpus 1, H100 and non-MIG Requirements, the route's environment).
    - A34's documented bestvalid rollback exception for [infra] is kept.
  - **[F9 v12] (Codex v11 review, FIX_FIRST; draft).** See golist/digest_checker_v12.md. Tests: 146.
    - Resource predicates are structural: the Requirements must be a top-level conjunction containing the exact H100 clause and the exact negated MIG clause (no OR bypass, no negated H100). Environment assignments must be unique and equal the route's values. A29 permits NV_ACC_MEM_MANAGE=0 for aIO_2p0_s1.
    - Guard-only rescues keep their authorization. The terminal-status checks run at every administrative boundary in execution order. No pw.x continuation follows a D-24 FAILED [scf] after a rescue start.
    - The [infra] bestvalid exception holds only on the D-37 / A34(ii) chains, with a rollback record logged between the failure and the reset.
    - Real rescue files (lxplus, 2026-10-13T21:08Z) confirm the `RETRY RELAX <n>` format. All seven read 8 (reset), so A43 keeps every chain held until a reviewed count-enforcement procedure exists.
  - **[F9 v13] (Codex v12 review, FIX_FIRST; draft).** See golist/digest_checker_v13.md.
    - Requirements are parsed by an escape-aware ClassAd scan: no top-level ||, no ?: conditional; =?= is allowed. Both predicates must be on TARGET.GPUs_DeviceName; other forms only after a real-ad audit.
    - The [infra] bestvalid exception is disabled until its restoration evidence is supported.
    - Registered transitions are keyed on the scientific position (node executions before the segment), so an A36 rescue resumed as a2.s0 after the pause is accepted with its gates.
    - The A43 count-enforcement files are verified: DAG identity, config, exact RETRY = remaining - 1, the -no_submit dry run, and the dagman.out header.
  - **[F9 v14] (Codex v13 review, FIX_FIRST; draft).** See golist/digest_checker_v14.md.
    - A43 submission binding: the reviewed -no_submit .condor.sub must be exactly one scheduler-universe DAGMan, with the audited executable, the run directory and only permitted arguments. It is submitted with condor_submit, and the submitted DAGMan ad and the A43 dagman.out are linked to it and to the first resumed RELAX node.
    - The execution budget is counted separately from the rescue anchor (the scientific position). A guard-only first resumed execution carries the pending A36 bestvalid transition to the first actual SCF.
    - The audited executable path and run root are ASSUMED until the first real files are audited.
  - **[F9 v15] (Codex 2026-10-14T08:59Z; draft).** See golist/digest_checker_v15.md.
    - The dry-run arguments are parsed with HTCondor's new-syntax quoting, and every resulting argument is whitelisted.
    - The submit file may hold only `key = value` lines and one `queue`; include, conditionals, error/warning directives and continuations are refused.
    - Real-ad finding (C4 resubmission 2026-10-14): CERN transforms Requirements into `(TARGET.Hostgroup =?= ...) && PreGPURequirements`, with the H100/non-MIG clause in PreVerRequirements. The split-route check needs a reviewed chain resolution before it can accept a real ad.
    - **A15 rescue chains (README_D24_BD.txt:116-125), tabulated; still not derivable (safe gap):**

      | Chain | s0 (pre-D-24) | D-24 verdict of s0 | Rescue state (installed 2026-10-11 01:58 CEST; relax.in.pre_rescue kept, inputs in rescue_staging/) | Start geometry | Evidence | Why F9 cannot derive it yet |
      |---|---|---|---|---|---|---|
      | aIO_0p7_s1 | pre-D-24 steps; old-rule relax.in = g4, a trial whose SCF failed after 200 iterations | FAILED [scf]; best validated = g3 (E = -24017.02019226 Ry, lowest of validated g0-g3) | Gaussian 0.005 Ry, mixing_beta 0.1, mixing_ndim 12, electron_maxstep 300, verbosity 'high' (A15 pilot) | g3 (rows md5 b2ba576b80c5, = the D-24 selection) | README_D24_BD.txt:116-125; /tmp-copy check (FAILED [scf], bestvalid = independent argmin g3) | a pre-item-B s0 carries no D-24 status, so the A15 trigger (FAILED [scf]) and the reset are not bound evidence; the A15 transition is not in REGISTERED_TRANSITIONS |
      | aIO_2p0_s1 | pre-D-24 steps; first SCF at the input geometry failed after 200 iterations (4 h 58 min) | FAILED [scf]; nothing validated | same A15 rescue settings | the s0 input (rows md5 06ba5b09745f) | README_D24_BD.txt:116-125 | as above; later A25 split-label route (scope now enforced) |

  - **v4 additions (Codex 20:25Z).** These are in addition to the above:
    - force-block identity validation;
    - registered-threshold, residual and terminal-failure assertions;
    - export-manifest binding of every input and output;
    - the plan- and log-derived C3 inventory;
    - derived A31(f) roles;
    - real-format job logs with bound offset evidence.

    The checker also re-derives every record that another record references. Tests: 60 (digest v4).
  - **Trust boundary (stated).** F9 proves that each record is the frozen writer's output on its bound files, and that run, geometry, settings and UPF are linked. It does not prove that the bound files are the right ones. That rests on:
    - the F10 manifest, committed before sight;
    - cluster ids in the job logs;
    - Codex's audit of the first real records.

    The C3 inventory is complete only if the manifest lists every C3 output.
- **F10. Read-out manifest.** Committed before the first `cell`. It lists:
  - every command of section B, with its inputs (paths, and sha256 where they exist) and output names;
  - the F9 result JSON of every certificate;
  - the series specs (MV-geometry and Gaussian/polished), with both 2.0 nm seeds in the 2.0 nm slot (A37);
  - the A37 override line;
  - the A40 item-7 2.0 nm C3 list;
  - (v4) the frozen C3 plan file (iwo-f10-c3-plan/1: slot, cell, geometry, width) and, for each slot, the path of its single HTCondor user log. Both are committed before any companion is submitted;
  - (v4) the offset-evidence file of the submit host (utc/local/valid_from/valid_to), captured with the user's approval;
  - the F9 readout_manifest record listing every C3 output: the complete C3 inventory that F9 reads (v3). Each C3 output is added with its sha256 as it is written, and none is omitted.

  A command outside the manifest needs a logged addendum stating that it was added after sight.
- **F11. Pinned reader environment (required; Codex 15:08Z).**
  - **Code:** tag readout-1.0.0-rc7-frozen-20261011T2249Z (8a74a5e).
    - code_sha256 fff642a13a62db6d0cde3e4704cdbf343913fc1972d9fa95d79f7ad8f4e01158, recomputed 2026-10-12 ~23:40Z and equal to the D-32 value; __pycache__ unchanged by the F9 tests (read-only import, bytecode off).
    - Tests sha256 d8f96f26…. `git diff` against the tag is empty for compute/amorph/analysis.
    - .gitattributes eol=lf, so the files are byte-identical under Windows and WSL.
  - **Interpreter: a dedicated venv,** Python 3.13.14 with numpy==2.2.6 only. Invoked as `<venv>\python -E -B -m analysis …` from compute/amorph. The F9 checker is run with `<venv>\python -I -B` (stdlib only).
    - The user-site interpreter is not used for read-outs. -I breaks `-m analysis` (-P implied), and -s loses numpy (user site); both were tested 2026-10-12.
    - Record `python -VV`, `numpy.__version__`, the sha256 of `pip freeze` and the OS build in the manifest.
    - Delete analysis/__pycache__ before step 0 (stale cpython-313 caches exist).
  - **IWO_REGISTER** is the absolute path of the committed register (F12). Every output records its sha256 (certify.py:99-101, 126, 434).
  - Exports are read from the local archive copies with a sha256 manifest, never directly from CERN.
- **F12. Register state and housekeeping (text proposals; nothing applied without the user's go).**
  - The register commit and tag that contain A37-A40 and the D-42 row.
  - No register edit is made during a read-out session. An amendment logged between sessions changes the register hash and is disclosed.
  - **H1. Header line 4.** It lists "A1 to A16; A17 to A31, A34 and A35 added after the freeze". Proposed: "A1 to A16; A17 to A31 and A34 to A40 added after the freeze; A32 and A33 reserved …". As of today it omits A36.
  - **H2. A27 C1 composition erratum (confirmed by Codex 15:56Z by input-only counting; a logged erratum, Codex 13:15Z / work chat:3550).** Register:472 gives the film formulas only ("In49W1O76 against In50O75"). The 0.7 nm cells carry dissociated-water passivation. Proposed erratum line: "the 0.7 nm C1 parent aIO_0p7_s1 is In50O83H16 (149 atoms); each C1 paired cell is In49W1O84H16 (150 atoms: one W replaces one In, one O is added in the W first shell, H atoms retained); N_ex = 1 and 2 % cation W are unchanged; the parent, the retained H and the construction rules are unchanged."
  - **H3. Work-chat timestamps (Codex 15:56Z: append the explanation; label unrecoverable arrival times as unavailable).** Proposed note, appended to the work chat without rewriting any heading: "Note (<UTC>): every 'Codex reply' heading carries the request start time set by tools/codex_advise.sh (TS at line 11, used for both headings at line 28), not the reply arrival time. The replies cited elsewhere as 13:15Z (D-40, A36) and 14:54Z (D-41, A36 erratum) are those headed 13:05Z and 14:48Z. Their arrival times, and those of all earlier replies, are unavailable (not recorded). Cited times are kept as written; no heading is changed."
- **F13. Export integrity (new; Codex 15:08Z).**
  - AFS transfers and quota are verified as in A39(d): a test transfer before P1, daily `fs listquota`, and an off-CERN sha256 for every file.
  - A14 gaps are preserved and carried with every read-out of the run.
  - A read-out whose export is not verified off CERN is not opened.
  - **Export sizes (v3; Codex 15:56Z).** The per-run-type size table of A39(d) is compared with the AFS quota and the ≤ 1 GB pending rule before the replacement hashes are frozen. It uses file sizes only, from local listings.

## B. Order of commands
0. **Environment check (F11 venv).** The fingerprint equals fff642a1…. The frozen tests pass. `python -m analysis crystalline` prints REPRODUCED (3 % W-5d, ΔE_c 0.281 eV, section 3). `cert_assert.py --self-test` passes.
1. **`certify` per cell** (cli.py:176-195). It prints the certificate path, source, run-file sha256, geometry hash, pseudopotential hashes, mode and the gate block.
   - **`validate-cert`** (cli.py:198-215) prints the qualification block, provenance hashes and GATE.
   - Neither computes or prints an electronic quantity.
   - stdout and stderr go to files. A key-allowlist check of the printed JSON runs before a person reads it, because a traceback could carry file text.
2. **F9 `cert_assert.py`** on every certificate. A non-zero exit means the certificate is recompiled with the 'permitted' statuses printed by F9 (never with a stronger claim), and F9 is rerun. Then commit the certificates, the F9 JSONs and the hash table.
   - **2b. Re-certification (Codex: recompute bound comparisons when certificates change).** A certificate may change after first sight, for example from smearing 'pending' to 'qualified' once the audit and fresh C3 exist. Then:
     - the old certificate is kept and marked superseded;
     - F9 is run on the new one;
     - `cell` is rerun with it;
     - every comparison and series output that bound the old certificate is recomputed. `cert_assert.py --reports` must show no STALE entry among the outputs of record;
     - both versions are kept and disclosed.
3. **`cell` per cell, in the manifest order:** aIO_bulk_s1, aIWO_bulk_s1, aIO_1p0_s1, aIWO_1p0_s1 (MV), aIWO_1p0_s1 (polished), aIO_0p8_s1, aIWO_0p8_s2, aIO_0p7_s1, aIWO_0p7_s1 (MV), aIWO_0p7_s1 (polished), aIWO_0p7_s1_bare, then the companions.
   - **This is the first sight.** Each output (self_sha256) is committed as it is written.
   - A rerun is allowed only for a logged technical fault or under 2b, and both outputs are kept.
4. **`compare`** (c3, c4, c6, c1, attribution, pair, hh, hk) per the manifest. Then **`series`** with the registered specs (A37: both 2.0 nm seeds). Last, `hg` and `audit`, once 2.0 nm read-outs exist.
   - compare and series accept only sealed outputs of the same code (compare.py:66-76, 1124-1134).
   - The H-N report applies the A37 override: the registered outcome is UNRESOLVED, and the raw rc7 string is reported as a diagnostic.
5. **Report.** Every report carries:
   - footnote † on every 2.0 nm H-G/H-N row;
   - the A38 disclosure line, and the A38 limitation if TRIGGERED;
   - spin at 2.0 nm "untested" (A40);
   - the A35/A36 lineage and smearing columns;
   - "A15 width provisional (EA not evaluated)" wherever a width is qualified;
   - the claims-table wording.
- **Rationale for the order.** certify, validate-cert and F9 print hashes and statuses only. `cell` is the only step that reads electronic data. compare and series only combine sealed outputs.

## C. Timing and sight
- **Earliest release (thin and bulk cells).** Before the cutoff is allowed (Codex 15:08Z), once all of the following hold:
  - F1-F13 are committed;
  - F9 (checker, writers, frozen definitions) is frozen with its replacement hashes, and its tests pass under the F11 venv;
  - the writers have produced the real thin-cell records, and Codex has audited them: their fidelity to the calculations, the job-log time zone and the first certificates (Codex 15:56Z: "the missing writers must establish their fidelity to calculations");
  - the export sizes and the AFS quota are verified (F13);
  - F9 returns CLAIMS_OK for every certificate in the manifest;
  - Codex has reviewed the current text and F9, and the user has given the go. Review history so far: policy GO on draft v5 (2026-10-12T20:44Z); F9 v5 FIX_FIRST (2026-10-13 ~01:45Z); F9 v6 FIX_FIRST (2026-10-13T02:10Z); F9 v7 FIX_FIRST (Codex v7 review, scope wording GO prospectively); F9 v8 FIX_FIRST (Codex v8 review: four items, A35 s1 aids confirmed, returned-or-bestvalid conditionally approved); F9 v9 FIX_FIRST (Codex v9 review: initial budget, pause binding, split construction; rulings a-c); F9 v10 FIX_FIRST (Codex v10 review: guard-only rescue bypass, partial split, G* before deduplication; A43 GO-WITH-CHANGES); F9 v11 FIX_FIRST (Codex v11 review: resource predicates, guard-only terminal checks, [infra] exception scope; A43 v2 GO-WITH-CHANGES); F9 v12 FIX_FIRST (Codex: Requirements parsing, rollback evidence, scientific position; A42 GO to log, logged D-45); F9 v13 FIX_FIRST (Codex 21:47Z: submission binding, rescue anchor; sight classification; A39 +9 form to register in A43); F9 v14 FIX_FIRST (Codex 08:59Z: argument quoting, include directives); A43/D-46 logged 2026-10-14T09:05Z; F9 v15 not yet reviewed.
- **Geometry-hash linkage (Codex 20:25Z).** A rejection caused by a geometry-hash mismatch (for example a coordinate on a 1e-4 Å rounding boundary) stands. It is never overridden manually. The claim is withdrawn or re-derived from corrected inputs.
- **2.0 nm:** no read-out before the cutoff (A39). Blind completion checks are allowed.
- **Sight history.** After the first `cell`, every later amendment or control cut carries a sight-history line naming the read-outs seen, and preserves the original UNRESOLVED scores (Codex 14:54Z, 15:08Z).
- **D-12 / A38 record.** D-12's stop clause, as it applies to aIWO_2p0_s1 under ML_VALIDATION.md:32, is overridden by A38 (a result-informed amendment). Ordinary FAIL continuation (ML_VALIDATION.md:28-31) stands.

---

## Annex: claims table draft (F8; to be frozen as claims_table_v1.md)

| Hyp | Registered outcome expected at the cutoff | Allowed wording | Not allowed |
|---|---|---|---|
| H-A, H-B, H-C, H-E, H-F, H-J, H-L | Not affected by these drafts (TCAD; H-L crystalline) | as registered | — |
| H-D | Mass-only: "unresolved: not computed" (A22) | "Scattering branch fitted with crystalline masses; amorphous localisation at ≤ 1 nm (conditional)" | Any amorphous-mass statement |
| H-G † | UNRESOLVED unless the 2.0 nm roles converge and the width qualifies (F9) | "On converged ≤ 1 nm and bulk networks (conditional on the provisional width), and on the 2.0 nm networks (lineage stated; exploratory where not converged; spin untested), the W excess electron occupies …" | "H-G supported/falsified" unless scored; "W is a fully ionised donor"; charge-transition levels |
| H-H | 2.0 nm UNRESOLVED (D-35). 0.7 nm on MV geometries with Gaussian FINALs (F6); scorable only if bare converges and the width qualifies on both MV geometries (fresh MV-geometry C3, A40 rule 3), otherwise UNRESOLVED | "At 0.7 nm the OH cell shows [no] occupied localised surface state within 0.3 eV below the host edge (MV geometries; conditional)" | Any 2.0 nm termination claim; aligned shifts at 0.7 nm; a polished-geometry H-H |
| H-I | UNRESOLVED (A34) | "An exploratory 1.0 nm Al2O3-interface cell shows [no] localised interface state near the edge" | Any H-I verdict or offset |
| H-K † | UNRESOLVED (needs both converged 2.0 nm seeds; aligned edges withheld) | "The amorphous PBE host gap widens by x eV from bulk to 0.7 nm (conditional); the 2.0 nm value is y (exploratory where not converged)" | "Agrees with the crystalline law" as a test result |
| H-M | UNRESOLVED (no route) | — | Any HfO2 statement |
| H-N † | UNRESOLVED in every branch (A37 formal override; raw rc7 output reported as a diagnostic) | "Per-cell readings at bulk, 1.0, 0.8 and 0.7 nm are … (each with its width condition and C3/C4/C6 status); the 2.0 nm cells read … (lineage stated; a difference is a lineage-confounded cell discrepancy); no thickness crossover is claimed or excluded" | "W efficacy breaks down below t"; "W stays a donor down to 0.7 nm" as a result; SAMPLE-DEPENDENT, seed dependence or sample dependence at 2.0 nm; any registered outcome other than UNRESOLVED |
| C3 (per cell) | Reported per cell | "width-robust within C3 tolerances, cell-local; A15 not met" (fresh start only); "(density-seeded; reported, not counted)"; any C3 FAIL at a geometry blocks the qualification of that geometry at every width | C3 PASS as a smearing qualification or as a resolved class |
| Structures | C037 FAIL; A38 verdict; A38 disclosure | "MACE structures relaxed by DFT for N steps (residual largest force X eV/Å)"; the A38 limitation if TRIGGERED ("possible topology bias remains uncorrected"); the final-frame label ("UNDETERMINED, treated as exposed" until the identity check); "ML_VALIDATION.md:32 stop action superseded by A38 (result-informed amendment)" | "Relaxed 2.0 nm amorphous slabs" for unconverged cells; ML-stage structure statistics; any statement that the stop rule was applied |

† = the A37 footnote (partial unblinding of 2.0 nm relaxation-SCF Fermi energies and KS eigenvalues, 12 Oct).
