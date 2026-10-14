# Draft amendment A43 (administrative continuation after the 13 Oct GPU full stop) and decision D-46: NOT LOGGED (draft v6)

Drafted 2026-10-13 by Claude (DFT side) after Codex's review of checker v9 (case 2: "For this existing pause, log an explicitly result-informed administrative-continuation amendment **before resumption**, preserving remaining budget, prior rescue use, terminal status and gates. Do not backdate it or describe it as pre-pause registration."). Nothing in the register, the decision log or on lxplus was changed by this draft. Nothing was submitted or resumed.

**Draft v2 (2026-10-14, Codex GO-WITH-CHANGES on v1):** item 3 no longer adds a stop after failed restart gates or qualifications (A35/A36 exploratory continuation is preserved). Item 4 keeps A34's documented bestvalid rollback exception. Items 1 and 7 add the rescue-file RETRY verification (configuration plus count enforcement). Table (1b) records the A15-era aIO_2p0_s1 rescue separately from A39. v1 is kept as `A43_pause_continuation_draft.md.v1`.

**Draft v3 (2026-10-14):**
- Table (1b) is filled from lxplus metadata only: dagman.out RELAX node events, DAG and rescue files, RELAX_STATUS, segment_stop, tarball names and sizes, and the first line of the D-24 lineage logs (the classifier label). Raw outputs: golist/r32_a43_meta.out, r34_a43_status.out.
- The pause start is corrected to the segment_stop stamp 2026-10-13T03:13:17Z.
- The rescue-file rule is reconciled: an oversized file keeps its chain held.
- The three segment outcomes are disclosed, and the guard-only retries are listed separately.
- condor_history returned no record within its 240 s timeout (r33), so the counts rest on DAGMan's own event log.

v2 is kept as `.v2`.

**Draft v4 (2026-10-14, Codex GO-WITH-CHANGES on v3):**
- The budget is worded as remaining before resumption, including guard-only executions during the pause.
- The historical +9 authorization of aIO_2p0_s1 is bound (D-27 item 2 / A25).
- The s0 failure categories of both A36 cells are bound from their segment_guard backup labels (both [scf], before the A36 rescue start). The raw output golist/r35_a36_cat.out was moved without reopening to `scratchpad/sealed/r35_a36_cat.out.SEALED` (sha256 041e4513cc5751dbb1a0da4d0490084e51b4e7d15b1be0b3cbdb2cd51afe0360); the disclosed exposure stands. The label text needed is quoted in table (1b), and the probe script r35_a36_cat.sh is kept.
- **Sight disclosure:** the segment_guard label lines also carry the D-24 geomsel summary (n_scf, n_geom, the E0/Ebest totals and SCF iteration counts of s0). They were displayed while the category was read on 2026-10-13T21:34Z, are not used by A43 and are not copied here.

v3 is kept as `.v3`.

**Draft v5 (2026-10-14, after Codex 2026-10-13T21:31Z GO-WITH-CHANGES on the count-enforcement design and 21:47Z on v4):**
- Item 1 now **registers the count-enforcement procedure** (Codex (i): the new DAG and configuration form needs A43's explicit authorization). The procedure: a per-chain `<name>.a43.dag` with RETRY = remaining - 1 and DAGMAN_RESET_RETRIES_UPON_RESCUE = False; a `-no_submit` dry run; submission of the **reviewed** `.condor.sub` with `condor_submit`; the DAGMan ad bound to the reviewed files.
- The claim that the False setting stops a later invocation adding executions is removed. Before any later invocation, the budget is recomputed and its authorization required.
- Item 2 now **registers A39's separate +9 DAG form** (genuine exhaustion, once per chain). It records that change to A39's "existing .rescueNNN" action before use.
- The sight sentence in the sources is corrected (Codex: re-exposure of relaxation-SCF totals already disclosed in A36; no new target unblinding). A dated A36 sight-history note is drafted separately (drafts13oct/A36_sight_history_note_draft.md).
- Item 6 clarifies the never-started non-DAG jobs (C4 polishes, MACE frames): they are outside item 1 and need no DAG procedure.
- Numbering re-checked: A42/D-45 were logged 2026-10-13T21:33Z (private commit 382d80a), so A43 and D-46 are the next free numbers.

v4 is kept as `.v4`.

**Draft v6 (2026-10-14, Codex 08:59Z GO to log after corrections, applied):**
- The raw A36 label output is described as moved without reopening to `scratchpad/sealed/r35_a36_cat.out.SEALED` (sha256 041e4513cc5751dbb1a0da4d0490084e51b4e7d15b1be0b3cbdb2cd51afe0360).
- Retry lines are required only when retries occur.
- The reviewed F5 rule text is bound prospectively (annex A43_annex_F5_rule.md, sha256 8aceddaaacf919c5d5e9c882efef05361610f122c1b99f964aea4a0260d155ac).
- v5 is kept as `.v5`.

**Numbering (checked read-only 2026-10-13):**
- Register: highest logged amendment is A42 (2026-10-13T21:33Z). A40 (C3 protocol) is drafted but not logged. A32/A33 are reserved. **A43 is free.**
- Decision log: highest logged is D-45 (A42). D-43 is reserved for the release decision. **D-46 is free.**
- Re-check both at logging. If A42 is logged later than A43, the numbers stay as drafted (they are reservations, not order).

**Placeholders to fill at logging:** `09:05`, `Codex 2026-10-14T08:59Z: GO to log A43/D-46 after the text corrections (applied in draft v6)`, `2026-10-14 ~08:50Z (work chat USER GO: log A43 and resubmit the two C4 polishes on their registered 1-GPU route)` and `<COMMIT>`. Table (1b) is filled from bound metadata (v3/v4); bind the raw outputs (golist/r32_a43_meta.out a6b76768…, r34_a43_status.out 1cddc18b…) by sha256 in the entry; the A36 category labels are quoted in table (1b) (their raw output was moved without reopening to `scratchpad/sealed/r35_a36_cat.out.SEALED` (sha256 041e4513cc5751dbb1a0da4d0490084e51b4e7d15b1be0b3cbdb2cd51afe0360)). No output energies are needed.

---

## (1) Register section-2 text (to append after A42)

```markdown
### A43: administrative continuation after the 13 Oct GPU full stop: same epoch, preserved budget, no new allowance (result-informed administrative amendment, added after the pause began at 2026-10-13T03:13:17Z and before any paused job resumes; logged 2026-10-14T09:05Z; Codex review: Codex 2026-10-14T08:59Z: GO to log A43/D-46 after the text corrections (applied in draft v6); user go: 2026-10-14 ~08:50Z (work chat USER GO: log A43 and resubmit the two C4 polishes on their registered 1-GPU route); decision D-46)

- **Type: result-informed administrative continuation.** This is **not** a pre-pause suspension rule, and it is not backdated.
  - The pause began at **2026-10-13T03:13:17Z**, when `STOP 2026-10-13T03:13:17Z manual: full stop of GPU requests ...` was armed in segment_stop of the 7 DAG chains. The time is the stamp of that line, identical in all 7 files. User decision ~03:20Z; Codex GO-WITH-CHANGES for steps 1-3 (work chat 03:18Z/03:40Z).
  - This text was written after the pause began. It is logged before the first execution of any resumed job.
  - Information that may be known at logging, disclosed:
    - **the three segments running at the pause (outcomes known at logging, from dagman.out (local CEST minus 2 h) and the lineage-log label):**
      - aIO_2p0_s1 s2, job 12901845: terminated 2026-10-13T07:29:22Z, `segment relax_s2: CONTINUE`;
      - aIWO_0p7_s1_bare s2, job 12901160: terminated 08:23:19Z, `CONTINUE`;
      - aIWO_0p8_s2 s3, job 12901263 (A35 epoch): terminated 08:34:38Z, `CONTINUE`.
      All results were returned (relax_s<k>_results.tar.gz with saved input, lineage log and returned relax.in).
    - **guard-only retries (listed separately; each is one counted execution).** These node retries started and stopped at the armed segment_stop before pw.x, then were held: 12910599 (aIO_2p0_s1 s3, 08:35:17Z), 12910971 (aIWO_0p7_s1_bare s3, 08:35:18Z), 12911057 (aIWO_0p8_s2 s4, 08:35:19Z). They wrote RELAX_STATUS FAILED (stop, not a pw.x failure). Their DAGMans 12891110, 12884014 and 12884028 were removed at 20:55Z.
    - the removal records of the never-started jobs;
    - the queue and priority figures.
  - No energy, force or electronic quantity of any chain is used by this rule.
- **Scope.** The 7 DAG chains whose segment_stop was armed:
  - running at 03:13:17Z: aIO_2p0_s1 (job 12901845, rescue DAG 12891110), aIWO_0p7_s1_bare (12901160, DAG 12884014) and aIWO_0p8_s2 (12901263, A35 epoch, DAG 12884028);
  - idle and never started, DAGMan removed: aIO_2p0_s2 (DAGMan 12884189, node 12905862), aIWO_2p0_s1 (12884195, 12905564), aIWO_2p0_s2 (12884196, 12901989; A36) and aIWO_2p0_comp_s1 (12884377, 12901955; A36). Their relax.in md5s d2572847 / 08a6523e / 0df5ad47 / 09eab9f1 were kept.
  - It also covers the never-started non-DAG jobs that were removed: the C4 polishes 12904172 and 12904173, and the MACE GPU frames 12890593.0/.1.
- **Rule (Codex wording adopted).** The administrative continuation:
  - continues the same epoch;
  - retains each chain's existing remaining execution budget and prior rescue usage;
  - grants no additional A39 allowance.
  All terminal failures and restart gates remain binding.
  1. **Budget.** Each chain resumes with exactly the **remaining RELAX node executions before resumption, including the guard-only executions during the pause** (table 1b): 9 per DAG (RELAX + RETRY 8) minus the executions already used, where one execution is one cluster, guard-only node attempts are included, and an eviction or re-execution inside one cluster is not counted.
     - HTCondor would reset retries on the rescue submission. That count is never inherited.
     - **Configuration plus count enforcement (Codex).** The resubmission sets `DAGMAN_RESET_RETRIES_UPON_RESCUE = False` (DAG-local configuration, procedural). This governs only rescue files written after it is set; it cannot repair rescue files already written with reset counts (for example the files written when the four idle DAGMans were removed on 13 Oct).
     - Before any resumed execution, every chain's existing rescue file is read. The RELAX node's remaining `RETRY` is recorded and must satisfy RETRY + 1 <= the preserved remaining executions.
     - **An oversized rescue file is never used:** its chain is not resubmitted from it. No rescue file and no `RETRY` line is edited (A39: no edit of RETRY).
     - **Count-enforcement procedure (registered here; design GO-WITH-CHANGES from Codex 2026-10-13T21:31Z; drafts13oct/A43_count_enforcement_draft.md).** For each chain, after the archive move of item 7:
       - (a) new files in runs/<name>/ only:
         - `a43_dagman.config` containing exactly `DAGMAN_RESET_RETRIES_UPON_RESCUE = False`;
         - `<name>.a43.dag` = `<name>.dag` with exactly two changes: `RETRY RELAX <remaining - 1>` (4 / 4 / 3 / 7 / 7 / 7 / 7 for table (1b)) and one `CONFIG a43_dagman.config` line.
         Node submit files, relax.in and every existing file stay unchanged. There must be no rescue or recovery state under the new basename.
       - (b) `condor_submit_dag -no_submit <name>.a43.dag` writes `<name>.a43.dag.condor.sub`. It is reviewed and its sha256 recorded: exactly one scheduler-universe DAGMan job, the audited condor_dagman executable, the chain's run directory, `-Dag <name>.a43.dag` and `-DoRescueFrom 0`, and no other recovery or force option.
       - (c) Submission submits **that reviewed file** with `condor_submit <name>.a43.dag.condor.sub | tee submit_a43.txt`. It does not run `condor_submit_dag` again, which could regenerate the reviewed bytes. The submitted DAGMan ad is bound to the reviewed files (cluster from the submit record; its Cmd, Iwd and Arguments equal the reviewed file).
       - (d) After startup, the DAGMan header must report the False setting. **When retries occur**, every retry line must read "retry #k of <RETRY>"; a successful first execution writes none.
       - (e) **Any later invocation** of any DAG for the chain (A43 or A39) first recomputes the remaining budget and requires its registered authorization and reviewed DAG form. The False setting lowers the retries written into a later rescue file, but it does not stop a further invocation from adding an initial execution.
     - **Execution gate.** A DAG chain resumes only after this entry is logged, the F9 checker version that verifies (a)-(d) is frozen, and the first real `.condor.sub` and DAGMan ad are audited (Codex: "execution still requires the corrected checker and real-file audit").
     - **Measured 2026-10-13T21:08Z:** all seven existing rescue files read `RETRY RELAX 8` (DAGMAN_RESET_RETRIES_UPON_RESCUE was True in every DAGMan), i.e. 9 executions, above every chain's preserved remaining count. All seven DAG chains therefore resume only through the procedure above.
     - **aIO_2p0_s1 receives no fresh allowance because its existing rescue DAG 12891110 was removed.**
  2. **Prior rescue use.** The administrative continuation does not count as, consume, renew or replace the A39 administrative rescue ("once in total per chain"). A39 remains available afterwards only under its own trigger (retry exhaustion with the last segment CONTINUE or a resumed non-[scf] category). Prior rescue use is preserved as recorded in (1b).
     - **A39 +9 DAG form (registered here; changes A39's "existing .rescueNNN" action before any use; Codex 21:31Z (ii) and 21:47Z).** With `DAGMAN_RESET_RETRIES_UPON_RESCUE = False` kept, an exhausted chain's rescue file carries no fresh retries. A39's administrative rescue is therefore run as `<name>.a39.dag`: the original DAG with `RETRY RELAX 8` and the same `CONFIG` line. It is prepared, dry-run, submitted and bound exactly as in item 1 (a)-(e). It adds at most 9 RELAX executions, is available **once per chain**, and only after **genuine exhaustion**: remaining executions 0 and A39's existing trigger and eligibility (last segment CONTINUE or a resumed non-[scf] category; never after a terminal failure, a failed or missed qualification, a failed gate, parking or a cut). Nothing else in A39 changes.
  3. **Terminal and inherited status (unchanged rules; A43 adds no stop).**
     - A chain that wrote FAILED [scf] under a one-attempt rule (A28, A35, A36, D-43 F5), or that is parked or cut, is not resumed. These are the registered stops.
     - A failed restart gate or a failed or missed qualification is not a new stop. The chain keeps the status the registered rule gives it: under A35/A36 its relaxation becomes **exploratory**, inherited by descendants, and the chain may continue exactly as A35/A36 permit. That status is preserved across the pause and is not cleared or upgraded by it.
     - Clearing segment_stop does not clear segment_guard and revives nothing.
  4. **Same epoch, geometry and settings.**
     - A CONTINUE segment resumes from its returned relax.in.
     - A FAILED segment is handled only under README_D24_BD section 3 and its registered rule. A geometry-only reset from the independently verified bestvalid is allowed where that rule permits it.
     - An [infra] failure keeps the segment input (A30 rollback), **except** A34's documented case: a fatal GPU/CUDA error after a new validated geometry archives relax_s<k>_bestvalid.in (D-37 guard-ordering fix), and that case is recognised. It is **not usable** until its restoration evidence (the permitted rollback rule, the restored input, labels and resource request, and the failure evidence) is defined and reviewed. F9 v13 refuses it. Its scope stays the chains where that fix is installed (D-37: aIO_2p0_s1, aIO_2p0_s2, aIWO_2p0_s1, aIWO_2p0_s2, aIWO_2p0_comp_s1, aIWO_0p7_s1, aIWO_0p7_s1_bare; A34(ii): aIWO_1p0_Al2O3_s2). None of the seven paused chains needs it.
     - The A35/A36 one-attempt rules override all of this.
     - No setting, smearing, mixing, tolerance or submit file changes. The rescue DAG's local s0 is not a new physics epoch.
  5. **Gates.** Every mandatory restart gate applies across the pause boundary as at any segment boundary (A35 from s4; A36 from s2). A missing or unevaluable gate counts as failed. Qualification SCFs stay required as registered.
  6. **Never-started removed jobs.** They had no execution event (NumJobStarts 0), so they used no RELAX execution, no retry and no one-attempt rule.
     - DAG nodes resume through their chain's rescue file under items 1-5.
     - The C4 polishes and the MACE frames are **not** DAG chains: item 1 (rescue files, count-enforcement procedure) does not apply to them.
     - They may be resubmitted, after this entry is logged and with the user's go for the submission, as new clusters with byte-identical submit files and inputs (sha256 checked against the 12 Oct submission record checks/gpumax_work/submit_20261012T131733Z.log for the C4 polishes).
     - The removed cluster IDs (12904172, 12904173, 12890593.0/.1) are recorded and never count as attempts.
     - **F5 bound prospectively (D-43 is still a draft):** the resubmitted C4 polishes follow the reviewed F5 rule text, quoted in the annex `A43_annex_F5_rule.md` (sha256 of the F5 block 8aceddaaacf919c5d5e9c882efef05361610f122c1b99f964aea4a0260d155ac). It covers the one attempt, the infrastructure-stop repeat, the convergence deadline 17 Oct 10:00 UTC, the fresh final-geometry qualification due 20 Oct 12:00 UTC, the restart gates and the zero-step rule, and it starts at their first execution. A later D-43 logging may not weaken it for these two jobs.
     - The A34 14 Oct 12:00Z CPU fallback for the MACE frames is unchanged.
  7. **Evidence and order.** Before resumption, each chain's archives are moved to attempt<N>/ (README_D24_BD section 3) and indexed by (run, DAG generation, local segment, cluster).
     - A per-chain F9 transition record is written: schema iwo-f9-transition/2, kind section3_rescue, authorization `A43-<chain>`, with remaining_before = remaining_after = the (1b) value, prior_rescues and terminal_failure no.
     - The record is attached to the chain's first resumed execution, even if that is a guard-only node attempt. It is bound with the chain's A43 DAG files from item 1 (a)-(d). A guard-only first execution counts against the budget, but it does not move the chain's registered scientific position (the next pw.x segment keeps the pending transition, for example the A36 rescue start from bestvalid).
     - F9 checks it against this entry (basis `continuation_amendment`: result-informed; logged after the pause start and before the resumed first execution; state preserved; no additional executions).
  8. **Dates unchanged.** These are unchanged: the 17 Oct 10:00Z cutoff, the 18 Oct 22:00Z last submission, the A39 read-out rules and admission measurements (14 Oct 06:00-12:00Z), section 3 and every hypothesis, threshold and tolerance. The pause shifts no date.
- **Not claimed.** That the pause cost nothing. Queue position and internal optimizer or electronic state are not preserved; a resumed segment restarts fresh (registered fresh start) from the preserved geometry.
```

### (1b) Per-chain preserved state (filled 2026-10-13T21:08-21:13Z from lxplus metadata; F9 registry entry `A43-<chain>`)

| Chain | RELAX clusters with an execute event (one execution each; an eviction or hold inside a cluster is not counted) | Executions used | Allowance → remaining | Prior rescue use | Status at the pause (labels) | Epoch / mandatory gates across the boundary | Resume geometry (relax.in md5) | Rescue file |
|---|---|---|---|---|---|---|---|---|
| aIO_2p0_s1 | gen 1, DAGMan 12883893: 12883895, 12885292 (one eviction plus hold/release, one cluster), 12890465, 12890466, 12890491, 12890492, 12890493, 12890494 and 12890495 (seven exit-1 retries within seconds, 2026-10-11 ~06:26-06:27Z), exhausted. Gen 2, rescue DAG 12891110: 12891111, 12891752 (hold/release, one cluster), 12901845 (s2), 12910599 (guard-only) | 9 + 4 = 13 | 9 + 9 historical = 18 → **5** | **1 historical rescue** (A15-era rescue001, written 2026-10-11T06:27:44Z after exhaustion; **not** A39's +9; A39 unused). Bound authorization (basis historical_rescue, +9):
- D-27 item (2): aIO_2p0_s1 on 1 H100 NVL with split labels (A25); user approval ~08:10Z after Codex GO-WITH-CHANGES on the 07:57Z request.
- Register A25 logged 2026-10-11T08:14Z.
- Work-chat action note 2026-10-11T10:15Z: "rescue DAG 12891110, node 12891111".
- The rescue DAG was submitted 09:42:39Z, after the authorization; its first execution, 12891111, ran 09:56:28Z.
- F9 entry: authorization_ref "D-27 (2) / A25", rule_logged_utc 2026-10-11T08:14:00Z, additional_executions 9. | s2 CONTINUE; s3 guard-only stop | A15 Gaussian epoch / none registered | e857581c… | rescue002 `RETRY RELAX 8` (9 > 5: held) |
| aIWO_0p7_s1_bare | gen 1, DAGMan 12884014: 12884017, 12891036, 12901160 (s2), 12910971 (guard-only) | 4 | 9 → **5** | none | s2 CONTINUE; s3 guard-only stop | MV epoch / none | 024391e9… | rescue001 `RETRY RELAX 8` (9 > 5: held) |
| aIWO_0p8_s2 | gen 1, DAGMan 12884028: 12884030, 12889333, 12893894 (two holds and one eviction, one cluster), 12901263 (s3, A35), 12911057 (guard-only) | 5 | 9 → **4** (consistent with the A35 note of 12 Oct: 6 remained before 12901263) | none | s3 CONTINUE (A35 epoch); s4 guard-only stop | A35 epoch from s3 / gate across the boundary into the first resumed pw.x segment | c7e15cb7… | rescue001 `RETRY RELAX 8` (9 > 4: held) |
| aIO_2p0_s2 | gen 1, DAGMan 12884189: 12884197 (s0, D-41 48 h); 12905862 submitted, never started, removed | 1 | 9 → **8** | none | s0 CONTINUE | registered epoch / none | d2572847… | rescue001 `RETRY RELAX 8` (9 > 8: held) |
| aIWO_2p0_s1 | gen 1, DAGMan 12884195: 12884201 (s0); 12905564 never started, removed | 1 | 9 → **8** | none | s0 CONTINUE (conditional A36 not triggered) | MV epoch / none | 08a6523e… | rescue001 `RETRY RELAX 8` (9 > 8: held) |
| aIWO_2p0_s2 | gen 1, DAGMan 12884196: 12884203 (s0); 12901989 never started, removed | 1 | 9 → **8** | none | s0 **FAILED [scf]** (segment_guard label 2026-10-12T09:57:56Z, backup segment_guard.20261012T132139Z; before the A36 rescue start at s1; A36 rescue staged for s1) | A36 epoch from s1 / gates from s2 | 0df5ad47… (A36-staged) | rescue001 `RETRY RELAX 8` (9 > 8: held) |
| aIWO_2p0_comp_s1 | gen 1, DAGMan 12884377: 12884378 (s0); 12901955 never started, removed | 1 | 9 → **8** | none | s0 **FAILED [scf]** (segment_guard label 2026-10-12T09:38:54Z, backup segment_guard.20261012T132140Z; before the A36 rescue start at s1; A36 rescue staged for s1) | A36 epoch from s1 / gates from s2 | 09eab9f1… (A36-staged) | rescue001 `RETRY RELAX 8` (9 > 8: held) |

**Sources.**
- dagman.out ULOG_SUBMIT / EXECUTE / TERMINATED / HELD / EVICTED / RELEASED lines for Node RELAX. These are in local CEST; UTC = local minus 2 h, cross-checked against each rescue file's "Created ... UTC" line.
- The .dag and .dag.rescueNNN files, RELAX_STATUS, segment_stop, tarball names and sizes, and the first lineage-log line.
- No relax.out or driver log was opened. **Correction (v5):** the segment_guard label lines read for the two A36 categories (2026-10-13T21:34Z) also displayed the s0 geomsel summary, including the E0/Ebest relaxation-SCF totals. Codex (21:47Z) classifies this as re-exposure of totals already disclosed in A36, with no new target unblinding; the A36 sight-history note is drafted separately. No forces or electronic quantities were displayed.
- The s0 failure categories of the two A36 cells are bound from their segment_guard backups (labels only; see the v4 sight disclosure): both FAILED [scf] before the A36 rescue start, so they are not terminal under A36's one-attempt rule.

Non-DAG removed, never started: 12904172, 12904173 (C4 polishes) and 12890593.0/.1 (MACE GPU frames). None of them is an attempt.

## (2) Register section-5 row

```markdown
| A43 | Result-informed administrative continuation after the 13 Oct GPU full stop (pause from 2026-10-13T03:13:17Z; logged after it, before any resumption; not backdated): same epoch, each chain's remaining RELAX executions, prior rescue use, terminal status and restart gates preserved; no additional A39 allowance (A39 stays once per chain under its own trigger); rescue-retry reset never inherited; DAG chains resume only through the registered A43 DAG form (RETRY = remaining - 1, DAGMAN_RESET_RETRIES_UPON_RESCUE = False, reviewed -no_submit .condor.sub submitted with condor_submit, DAGMan ad bound) after the corrected F9 checker and a real-file audit; A39's +9 registered as its own DAG form (genuine exhaustion, once per chain); never-started removed jobs are not attempts (C4 polishes and MACE frames resubmittable as byte-identical new clusters with the user's go); 7 DAG chains + C4 polishes 12904172/3 + MACE 12890593.0/.1; dates unchanged | Codex review of checker v9 (case 2), the full stop (03:18Z reply), the count-enforcement design (21:31Z) and A43 v4 (21:47Z): Codex 2026-10-14T08:59Z: GO to log A43/D-46 after the text corrections (applied in draft v6); user go 2026-10-14 ~08:50Z (work chat USER GO: log A43 and resubmit the two C4 polishes on their registered 1-GPU route); D-46 |
```

## (3) Decision-log row D-46

```markdown
| D-46 | 2026-10-14 | Register A43 logged at 09:05Z (result-informed administrative continuation after the 13 Oct GPU full stop; per-chain preserved state table bound by sha256). DAG chains resume only after this entry, the frozen F9 checker that verifies the A43 DAG form, the real-file audit, the per-chain F9 transition records and the user's re-authentication on lxplus; never-started non-DAG jobs (C4 polishes, MACE frames) may be resubmitted after this entry with the user's go. | Mahmoud (2026-10-14 ~08:50Z (work chat USER GO: log A43 and resubmit the two C4 polishes on their registered 1-GPU route)) | Codex (checker v9 review; full-stop reply; count-enforcement design 21:31Z; A43 v4 21:47Z) | IN FORCE |
```

## (4) Notes for whoever logs this
- Fill table (1b) only from metadata: dagman.out node attempt lines, node user logs (001 events per cluster) and condor_history. Bind the raw outputs by sha256 in the entry. Do not open any relax.out energy.
- **Codex answers encoded:** (i) configuration plus count enforcement through the registered A43 DAG form (item 1); (ii) the A15-era aIO_2p0_s1 rescue is recorded separately and is not A39's +9; (iii) the three segment outcomes are disclosed (v3). A39's +9 DAG form is registered in item 2.
- Complete table (1b) from metadata before logging (Codex: GO-WITH-CHANGES requires it).
- The F9 checker (v14 draft and later) enforces this entry's shape and item 1 (a)-(d). Registry entries `A43-<chain>` are added to f9_common.REGISTERED_RESCUE_AUTHORIZATIONS only with the logged values (basis `continuation_amendment`, `result_informed: True`, `pause_started_utc 2026-10-13T03:13:17Z`, `rule_logged_utc` = the logging time, `preserved` = table (1b)).
