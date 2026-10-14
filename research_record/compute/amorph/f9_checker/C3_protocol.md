# A40 draft v5: C3 width companions (file name kept from v1: C3_protocol.md; Codex 2026-10-12T20:44Z: policy GO; v5 F9 notes below; F9 code now draft v15, see digest_13oct_v6.md to digest_13oct_v8.md and golist/digest_checker_v9.md to _v15.md; v3 Codex 15:56Z GO-WITH-CHANGES, applied; NOT logged, NOT committed)

v2 is kept as C3_protocol.md.v2 and v1 as .v1. v3 changes (Codex 15:56Z):
- The MV-geometry C3 companions needed for the 0.7 nm H-H reference are retained. If they do not pass, H-H 0.7 nm is explicitly UNRESOLVED.
- C3 qualifies only the geometry it ran on: polished-geometry comparisons never qualify a moved-from MV geometry (rule 3; F9-enforced).
- The native-Gaussian aIWO_2p0_s2 exception is stated explicitly (rule 3).
- New, flagged for Codex: a density-seeded FAIL still blocks qualification (rule 2).
- F9 now reads C3 from the complete inventory (readout_manifest record). It also re-derives every companion record (start mode and diff gate) from the inputs.

Changes from v1 (applied in v2):
1. **A40, not a protocol.** Codex: "use A40, because excluding density-seeded comparisons changes eligibility".
2. Density-seeded comparisons are run if needed and **reported, but excluded from fresh-start qualification**.
3. A cell-local C3 PASS while the class stays UNRESOLVED is stated to be legitimate.
4. Zero-step reuse of a polish requires all of the following: an actual converged polish; exact geometry, settings and UPF identity; a fresh final-geometry qualification (D-42 F5); and newly bound polish evidence.
5. 2.0 nm: non-duplicated C3 needed for primary qualification is kept, and the audit comparisons are reused. The extra endpoint C6 at 2.0 nm is cut, with spin robustness stated as "untested".

Sources: register A27 C3 (493-496), A26, A31(b), (d), (e), C4 (498-501), budget (517-532); D-39, D-40; Codex 13:15Z ("Primary C3/C6 calculations must use the resulting Gaussian geometries") and 15:08Z; rc7 compare.py c3 (434-460), tolerance_compare (383-427), control_status (1153-1187), smearing_audit (1061-1120); register.py:70-71, 77-82, 94-98; certify.py:218-221, 354-375; readout.py:259-261.

---

### A40: C3 width companions (Gaussian 0.002 and 0.005 Ry against the A26 0.001 Ry reference), fresh-start eligibility, zero-step polish reuse, and the 2.0 nm C3/C6 scope (added after the freeze, 2026-10-1xT<hh:mm>Z, before any companion has run and before any reference FINAL has been read by the reader; Codex 15:08Z: A40; user go; decision D-42)

- **Scope.**
  - The C3 control (A27) for the cells in the table below.
  - The comparison is the A26 Gaussian 0.001 Ry reference FINAL against Gaussian 0.002 and 0.005 Ry companions at the same geometry. These are the pending widths while the A15 audit is pending (register.py:96-97; compare.py:447).
  - The reader binds C3 to a 0.001 Ry cell only when **both** widths pass (compare.py:1169-1179).
  - The A15 audit itself (A31(a)-(d), including its A31(b) fallback) is unchanged. A40 changes only what counts as C3 evidence.
- **Why an amendment.** Excluding density-seeded runs from counting changes which comparisons are eligible: for the series C3 control, for the A31(e) common width, and for the D-42 F9 'qualified' assertion. That is a rule change.
- **Rule.**
  0. **Frozen slots and one log per slot (v4; F9 inventory, Codex 20:25Z).**
     - Before any companion is submitted, every C3 slot (cell, geometry hash, width) is listed in the frozen F10 C3 plan.
     - Every attempt for a slot, fresh or an A31(b) density-seeded fallback, is submitted with that slot's single HTCondor user log.
     - Each attempt's inputs and outputs are exported with a sha256 manifest that also contains its certified run files.
     - F9 derives the inventory from the plan, the logs and the reports. An unaccounted attempt, a missing report or a stray report makes the inventory underivable, and the cell then cannot be qualified.
  1. **Identical settings except degauss.**
     - Each companion input is the reference's as-run input (from its A14 export) with exactly one changed physical line: degauss = 0.002 or 0.005.
     - Everything else is identical: smearing 'gaussian', the explicit nbnd value, cutoffs, k-mesh, conv_thr, mixing line, dipole keys, pseudopotentials (sha256 via lineage), original element labels, QE build (7.5 CPU), -nk 1 and the D-39 resources.
     - Only the prefix, outdir and job names may also differ.
     - A diff gate prints the changed lines and the md5 of both inputs. Any other difference blocks submission. The gate result is written into the companion's F9 'c3_companion_run' record (changed_physical_lines = ['degauss']).
     - Export: D-24, with projections and, for slabs, planar averages.
  2. **Fresh start; density-seeded runs are reported, not counted.**
     - Fresh start means startingpot and startingwfc at their defaults, an empty private outdir, and no copied density or wavefunctions. It is recorded as start_mode 'fresh'.
     - If the SCF does not converge, the A31(b) fallback is allowed once: a new SCF from a converged sibling width's density, sibling order as in A31(b). The run is then labelled **'density-seeded'** (start_mode 'density-seeded').
     - A density-seeded comparison is computed and reported as "<status> (density-seeded; reported, not counted)". It is excluded from fresh-start qualification:
       - it does not count towards the series C3 control. It is not listed in the `series` controls, so its width counts as MISSING (compare.py:1175-1178);
       - it does not count towards the A31(e) common width;
       - it does not count towards the F9 'qualified' C3 coverage.
     - Reason: finding E (A35) shows that distinct SCF branches are possible in W cells. Seeding from a sibling may carry its branch over and bias the comparison towards agreement.
     - The same counting rule applies to A15 audit runs reused as C3 (item 7): an audit run that used the A31(b) fallback is density-seeded for C3 counting. The audit outcome itself is unchanged.
     - **Both endpoints (v5; Codex 20:44Z).** A comparison counts only if BOTH the 0.001 Ry reference and the companion are fresh starts, each derived from the as-run scf.in recorded in its certified lineage file. A density-seeded reference, including an audit run that used the A31(b) fallback, is reported, not counted.
     - **Attempts without output (v5).** Every attempt in a slot's user log must have its report, or a terminal event showing it failed (non-zero exit, signal, abort). A job that ended normally without its output, or one with no terminal event, blocks the cell's qualification. [F9 v6 tightens this: digest_13oct_v6.md, blocker 1.] [F9 v7: the attempt's slot is UNRESOLVED and only that cell and geometry are blocked; D-43 wording in Release_decision.md item 1 (Codex GO, prospective).]
     - **A density-seeded FAIL still blocks (v3, new; F9).** A density-seeded comparison never counts towards a PASS. A FAIL, fresh or density-seeded, blocks the smearing qualification of that run at every width. Seeding biases towards agreement, so a disagreement despite it is informative.
  3. **Geometry. C3 qualifies only the geometry it was run on (Codex 15:56Z).** A C3 comparison applies to a run only if its reference and compared runs share that run's geometry hash. F9 enforces this from the complete C3 inventory (test_mv_geometry_not_qualified_by_polished_c3). Polished-geometry comparisons therefore never qualify a moved-from MV geometry.
     - W cells at the C4 endpoints and at 1.0 nm use their **C4-polished** geometry for the H-N reading, so each needs a polished 0.001 Ry reference FINAL plus two companions.
     - **MV geometry used as the 0.7 nm H-H reference (Codex 15:56Z: retain, or leave H-H unresolved).** H-H at 0.7 nm compares MV geometries (D-42 F6): aIWO_0p7_s1 at its MV geometry (A26 FINAL 12902517) against aIWO_0p7_s1_bare.
       - The MV-geometry companions 0.002 and 0.005 Ry of aIWO_0p7_s1 are therefore **retained** (table below), as are those of the bare cell.
       - If either cell lacks fresh C3 PASS at both widths on its MV geometry by 20 Oct 12:00 UTC, **H-H 0.7 nm is UNRESOLVED**, stated explicitly.
       - If the 0.7 nm polish converges in zero steps (rule 4), the polished and MV geometries are the same geometry, so one companion set serves both.
     - Other MV-geometry FINALs (aIWO_1p0_s1 MV) stay C4 "class on the MV geometry" reports and get no C3.
     - aIO cells, aIWO_bulk_s1 and aIWO_0p8_s2 use their own Gaussian 0.005-relaxed geometries (A15, A23, A35).
     - **Native-Gaussian exception: aIWO_2p0_s2 (stated explicitly, Codex 15:56Z).** It has only its A36 Gaussian-lineage geometry: no MV-converged geometry, and it is never polished (A36, A37).
       - Where its C3 is needed for primary qualification (item 7), it runs at that native Gaussian-lineage geometry, and only if the cell is relaxation-converged and A36-qualified.
       - It is labelled "Gaussian geometry (A36); no MV geometry; C4 not satisfied". This is the second exception to the polished-geometry rule, alongside aIWO_0p8_s2 (A35).
  4. **Zero-step polish reuse (Codex 15:08Z).** The existing A26 FINAL may serve as the polished 0.001 Ry reference, with no new FINAL, only if all of the following hold. Otherwise a new polished FINAL runs.
     - (i) **Actual converged polish.** The polish printed 'bfgs converged' (A19) at a verified time ≤ the cutoff, with zero ionic steps.
     - (ii) **Exact geometry identity.** The rc7 geometry hash of the polish final geometry equals that of the MV parent's final geometry and the existing FINAL's certified geometry.
     - (iii) **Exact settings identity.** (F9 v9: every FINAL used for a positive certificate, not only a reused one, must match the registered FINAL template of its cell apart from the width; the template keys are frozen in f9_common.REGISTERED_FINAL_TEMPLATES before use.) The existing FINAL's as-run input equals the A26 polished-FINAL template for that cell except prefix, outdir and job names: the diff gate of rule 1 with zero changed physical lines. The settings sha256 is pinned in the reuse record.
     - (iv) **UPF identity.** The sha256 of every UPF of the polish and of the FINAL are equal, equal to the run lineage, and equal to the certificate's pseudopotential block.
     - (v) **Fresh final-geometry qualification.** The D-42 F5 qualification SCF of the polish has passed. Zero-step cases are included.
     - (vi) **Newly bound polish evidence.** A new certificate of the existing FINAL binds the polish record (C4 record, polish lineage, qualification and reuse record) in its geometry block.
       - The old certificate is superseded.
       - Every cell record and comparison bound to the old certificate is recomputed (D-42 B.2b).
       - F9 checks (i)-(vi): cert_assert.py tests test_zero_step_polish_reuse_passes, test_settings_identity, test_upf_identity, test_reuse_needs_actual_converged_polish, test_zero_step_polish_still_needs_qualification.
  5. **Cells (thin and bulk).**

     | Cell | Geometry | 0.001 reference | Companions |
     |---|---|---|---|
     | aIO_bulk_s1 | A23 Gaussian | existing (FINAL_DONE) | 0.002, 0.005 |
     | aIWO_bulk_s1 | A23 Gaussian | existing (FINAL_DONE) | 0.002, 0.005 |
     | aIO_0p7_s1 | A15 Gaussian | existing (FINAL_DONE) | 0.002, 0.005 |
     | aIO_1p0_s1 | A15 Gaussian | existing (FINAL_DONE) | 0.002, 0.005 |
     | aIO_0p8_s1 | A15 Gaussian | 12904001 (running; A14 INCOMPLETE disclosed and preserved) | 0.002, 0.005, after it completes |
     | aIWO_1p0_s1 | C4 polish (12904173) | new polished FINAL, or the existing one under rule 4 | 0.002, 0.005 |
     | aIWO_0p7_s1 | C4 polish (12904172) | new polished FINAL, or the existing one under rule 4 | 0.002, 0.005 |
     | aIWO_0p8_s2 | A35 Gaussian | its FINAL, only if converged and A35-qualified | 0.002, 0.005 |
     | aIWO_0p7_s1 (MV geometry; H-H reference, v3) | MV (A26 FINAL 12902517) | existing (12902517) | 0.002, 0.005 (shared with the polished set if the polish is zero-step) |
     | aIWO_0p7_s1_bare | MV geometry (H-H: MV geometries; FINALs Gaussian 0.001, D-42 F6) | its FINAL, only if converged | 0.002, 0.005 |

     - Count: up to 20 companions plus 2 polished references (A: each about the reference's measured wall time; to be filled in from the job records).
     - Order: 0.7 nm (aIWO_0p7_s1 polished, aIO_0p7_s1, aIWO_0p7_s1 MV), then 1.0 nm, 0.8 nm, bulk, then bare.
     - Deadline: every run complete and exported by 20 Oct 12:00 UTC (H-N single points). Otherwise that width is MISSING.
     - The runs are blind computations. They may be submitted before the D-42 release, and their outputs are read only after it.
  6. **Comparison and tolerances (unchanged).**
     - One `compare c3 <ref> <other>` per width, without --audit-width while A15 is pending.
     - The reader refuses: a geometry-hash mismatch (450-451); differing functional, cutoffs, k or lsda (452-454); a self-comparison (441-442).
     - Pass criteria (register.py:70-71): the class is unchanged; edges move ≤ 0.05 eV (absolute host and valence edges, Δ_W, E_F − host edge, host gap); fractions move ≤ 5 percentage points on interval bounds.
  7. **2.0 nm C3 and C6 (Codex 15:08Z).**
     - **Audit cells: reuse, no duplicate runs.** The A31(a) audit runs (0.005, 0.002 and 0.001 Ry at fixed geometry on the audit roles) are the 2.0 nm C3 comparisons of those cells. `compare c3` is run on the audit outputs (0.001 against 0.002, 0.001 against 0.005). No companion is run for an audit cell.
     - **Non-duplicated 2.0 nm C3 needed for primary qualification is kept.** It applies to a relaxation-converged (and, where required, qualified) 2.0 nm cell outside the audit whose 0.001 Ry FINAL needs the A31(e) common-width route: aIWO_2p0_s2 and aIO_2p0_s2 when they are not A31(f) backups.
       - Such a cell gets companions 0.002 and 0.005 at CPU-6 (D-42 F7).
       - An unconverged cell gets none: it cannot be primary.
       - The exact list is fixed in the F10 manifest after the A31(f) role decision at the cutoff, from relaxation status only.
     - **2.0 nm C6 is cut** (it served only the unreachable H-N endpoint, A37).
       - Its requirement text is kept: C6 at 2.0 nm is listed MISSING by rc7, and any claim needing it stays UNRESOLVED.
       - Every 2.0 nm H-G/H-N row states "spin robustness: untested (C6 cut, A40)".
       - C6 at 0.7 nm (and 1.0 nm, reported) is unchanged.
  8. **Labels.**
     - A cell with fresh C3 PASS at both widths is reported as **"width-robust within C3 tolerances, cell-local; A15 not met"**. Its C3 quantities and class_if_resolved do not change between 0.001 and 0.005 Ry at this geometry.
     - That label is not a smearing qualification. It does not transfer to another cell, does not resolve any class, and does not meet A15 (the 2.0 nm audit, which also needs EA). On its own it does not meet A31(e), which also needs a non-null A15 candidate.
     - **A cell-local C3 PASS while the class stays UNRESOLVED is legitimate** (Codex 15:08Z). The C3 status and the class status are reported side by side, and neither is inferred from the other.
     - C3 FAIL at any width gives "width-sensitive (C3 FAIL at x Ry)", and the affected quantities are UNRESOLVED.
- **What the frozen reader will show.**
  - **Certificates.** The smearing block stays **'pending'** for every cell unless the A15 audit gives a non-null candidate and A31(d)/(e) are complete, as checked by F9 (cert_assert.py).
    - C3 reports alone never qualify (F9 test test_c3_alone_never_qualifies).
    - certify.py:357-375 would accept any sha256-bound file with a matching numeric width. The semantics are enforced by F9 before `cell`.
    - Consequence: every class stays UNRESOLVED with "smearing qualification pending (A26/A15; not certified)" (certify.py:220-221; readout.py:259-261). class_if_resolved is reported.
  - **C3 statuses** can still read PASS or FAIL. c3 calls tolerance_compare with drop_smearing=True (compare.py:457, 393-394), and compares class_if_resolved (400-403).
    - Other qualification gaps (relaxation not converged, flagged states) make the status UNRESOLVED unless an item fails (421-426).
  - **Series.** control_status gives C3 'PASS' for a 0.001 Ry cell when both widths pass, without checking the smearing qualification in that role (1169-1179). So the series controls table can show C3 PASS while every class is UNRESOLVED. This is expected, legitimate and reported as such.
- **Not changed.** C3 tolerances, roles and the self-comparison rule; A15 and the A31 audit (including its fallback); C4; C6 at 0.7 and 1.0 nm; rc7.
- **Sight history.**
  - No reference FINAL has been read by the reader. The aIWO_1p0_s1 completeness statistics are known (A37).
  - No 0.002 or 0.005 Ry slab FINAL exists.
  - The 2.0 nm partial unblinding (footnote †) concerns the 2.0 nm cells of item 7, whose rows carry †. It does not concern the thin or bulk cells.

**Section 5 row:**

| A40 | C3 width companions 0.002/0.005 Ry against the A26 0.001 Ry reference: one changed physical line (diff gate, derived from the inputs); fresh start. Density-seeded comparisons (A31(b) fallback) are reported, never counted (series C3, A31(e), F9); any applicable FAIL, fresh or density-seeded, blocks qualification. C3 applies only to the geometry it ran on: polished-geometry comparisons never qualify an MV geometry. Polished geometries for the C4 W cells. MV-geometry companions retained for the 0.7 nm H-H reference (aIWO_0p7_s1 MV, bare), otherwise H-H 0.7 nm UNRESOLVED. Native-Gaussian exceptions aIWO_2p0_s2 (A36) and aIWO_0p8_s2 (A35). Zero-step polish reuse only with an actual converged polish, exact geometry/settings/UPF identity, a fresh final-geometry qualification and newly bound evidence. 2.0 nm: audit comparisons reused as C3; non-duplicated C3 kept where primary qualification needs it; 2.0 nm C6 cut, spin robustness "untested". Cell-local C3 PASS with the class UNRESOLVED is legitimate | Density-seeding changes eligibility; Codex 15:08Z and 15:56Z; finding E; D-42 |
