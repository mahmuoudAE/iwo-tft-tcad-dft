# S2 runner changes for Codex review (2026-10-13), revision 3

**Status:** not committed. No ATLAS launch was made. DIAG is not launched.

**Revision 3** fixes the three items of Codex's revision-2 review (GO-WITH-CHANGES, ~21:01Z). Each was added first as a regression case, which failed on the revision-2 code (run with `--only A17,A18,B8,B9`: 0/4 ok), and then fixed (4/4). Details are in the "Revision 3" section at the end.

**Revision 2** applied Codex's GO-WITH-CHANGES review of 2026-10-12T20:28Z: all three blockers were fixed and rulings D1 to D8 encoded. The sections below describe revision 2; where revision 3 changed something, the Revision 3 section says so.

**Budget:** unchanged, 75 of 260 global launches used and 15 of 200 C10 launches. `results/RUN_INDEX.csv` is unchanged (mtime 2026-10-12T16:34:32Z, 60405 bytes).

**Sealing.** For run_0075 I did only three things:
- listed the file names, sizes and mtimes in `results/runs/run_0075_*`;
- read `device.in` (deck input only);
- ran `regress_all_decks.py`.

I did not open `results/sealed/`, any other run_0075 file, the run_0075 notes or metric columns in RUN_INDEX, or `results/campaigns/campaign_C10_DIAGa_S2-11.json`, which holds run_0075's metrics by construction. All tests use temporary folders, synthetic run directories and stand-in processes.

## 1. Executable stop gates (Codex 13:18Z; blocker 2; D1, D2, D3, D8)

**Files and lines**
- `scripts/campaign_gates.py` (new, 259 lines):
  - module docstring: the operational rule (D2) :27 and decision binding :31;
  - `INPUT_FILES` :65, `binding` :83, `resume_hint` :180;
  - `check` :183, `audit_citation` :204, `held` :217;
  - the isolated child evaluator `child` is at the end of the file.
- `scripts/run_campaign.py`:
  - `--ack-gate` :171 and `--ack-audit` :173;
  - gate validation :178-183;
  - the stop holds until a valid acknowledgement :200-205;
  - gates checked before each entry :213, and at the end, then exit 3 :236-240.

**How a gate works**
- The scorer is the frozen `hc_nominal` / `hc_generation` in a separate `python -B` process. Its output is dropped except one state line.
- The verdict maps to a state (the `PROVISIONAL (...): ` prefix is stripped first):

| Verdict | State |
|---|---|
| starts with `FAIL` | FIRED |
| starts with `PASS` or `below resolution` | NOT_FIRED |
| anything else | UNRESOLVED |

- The plan is refused if a gate is malformed, if the scorer's hash differs from the declared value, or if `--workers` is not 1.

**Blocker 2: decisions are bound.**
- A decision is reused only if its binding still matches. The binding is the sha256 of:
  - the full gate declaration (canonical JSON);
  - the scorer file;
  - each input run's scored files: `execution.json`, `device.in`, `material_model_used.json`, `terminal_currents.csv`, `strip_iv.csv`;
  - every evidence file cited in `kwargs`.
- Any change gives a new evaluation before the plan proceeds. That covers a policy change, new resolution evidence, a rescored or retried run, a declaration edit, or a legacy record with no binding.
- The earlier decision is kept and marked `superseded_by`.
- `decision_id` is the first 16 hex digits of the binding hash.

**D1: UNRESOLVED stops, and resuming needs an audit.**
- For the first DIAG execution, UNRESOLVED also stops the plan.
- To resume, run `--ack-gate GATE_ID --ack-audit FILE`. FILE must exist and must name the gate id and the decision id; the STOP line prints both.
- The acknowledgement records the audit path, its sha256 and the decision it acknowledges.
- It never carries over to a new decision.

**D2: the rule is stricter than the design text.** Every DIAG gate carries `rule_basis`. It says that stopping on a resolved exceedance of the registered bound is a prospective, stricter operational rule. It is not a verbatim implementation of CAMPAIGN_DESIGN.md:304, and a FIRED gate is not itself a falsification.

**D3: S2-03 is an anomaly checkpoint.**
- `G-S2-03-anomaly` has its own rule id, `S2-ANOMALY-CARRIER`. It is a carrier-confounded anomaly checkpoint (S2-03 against S0-01, run_0061) and cannot isolate generation.
- `G-S2-01-generation` (S2-01 against S2-02) remains the matched mechanism test under `S2-STOP-NULL`.

**D8: DIAG states what is automatic.** The DIAG text now says that the declared gates and the budget/cap are automatic, and every other stop stays manual. This is done through `GATED_GLOBAL_RULE` and `GATES_ENFORCED_BY`, for DIAG only.

**What a gate outputs:** the gate, rule, checkpoint, test and input run ids; the state; a token; the action; the decision id; the hashes; and the times. It never includes a current or any verdict text.

## 2. Hang fix and cleanup (blocker 1; D4, D5, D6)

**Files and lines**
- `scripts/proc_guard.py` (new, 346 lines):
  - `FALLBACK_CMD`, `CMD_TIMEOUT_S` (10 s), `CLEANUP_BUDGET_S` (60 s), `KILL_PASSES` (3) :43-46;
  - `Guard.__init__` :174 (viewer policy default `record`);
  - `_candidates` :258, `_fallback` :274, `kill_all` :292;
  - the `capture` note :344.
- `scripts/run_atlas.py`:
  - `launch` :147, `deckbuild_out_completed` :190, `HANG_NOTE` :198, `hang_class` :201, `sealed_note` :217;
  - `execute` :229 and :276, `execute_output` :304 and :329, `execute_strip` :354 and :379.

**Blocker 1: the timeout cleanup is bounded and never touches licence daemons.**
- There is no `taskkill /T` any more. Each process of the launch is terminated individually with an identity check (`TerminateProcess`, creation time compared): job members, recorded descendants, and the launched process last.
- It runs up to 3 re-scan passes.
- Licence daemons (`KEEP`) are never terminated, even while still parented.
- If `TerminateProcess` fails, a single-process fallback command runs. It never uses /T, has its identity re-checked first, is bounded at 10 s per command and 60 s in total, and its result is recorded.
- An error on one process is recorded and the cleanup continues.
- After the kill, the runner waits at most 60 s for deckbuild and 30 s per pipe.

**Launch is unchanged.** Same Popen argv, cwd and pipes. `exit_code`, `timed_out`, `returncode` and statuses keep their facts.

**D4: viewers are only recorded by default.** `IWO_ATLAS_VIEWERS=kill` is opt-in until a supervised DeckBuild test qualifies it; the stand-ins prove the plumbing only. Job-object capture is recorded as best-effort.

**D5: `post_export_hang` is diagnostic metadata only.**
- Completion is now read from `deckbuild.out` itself (`deckbuild_out_shows_completion`). A completion line in the launcher stream alone does not count.
- The basis is stated as "exists with mtime before the kill", explicitly not proof of complete exports.
- Timeout and return-code facts and the frozen scorer's rejection of timed-out runs are unchanged.

**D6: hidden desktop deferred.** It is not implemented.

## 3. State-only surface (blocker 3; D7)

**Files and lines**
- `scripts/campaign_sealed.py` (new, 72 lines): `STATE_KEYS` :25, `validate` :29, `state` :44, `save` :53, `console` :64, `sealed_io` :69.
- `scripts/run_campaign.py`:
  - docstring :27;
  - `run_entry` passes `seal_notes=True` and redirects the launch's output :55-65;
  - setup and resume from the sidecar :184-199;
  - `save` / `line` replace the three summary writes and the two run prints.
- `analysis_2026-10-10_campaign/make_campaign_configs.py`: `GATE_RULE_BASIS` :109, `ANOMALY_RULE_REF` :112, `GATES` :122, `STATE_ONLY` :130, `GATES_ENFORCED_BY` :131, `GATED_GLOBAL_RULE` :134; written at :182; `--check` :216-224.

**What the opt-in key does.** A plan with `"state_only": {"sealed_dir": "results/sealed/..."}` (DIAG uses `results/sealed/campaigns`) gets these surfaces:

| Surface | What it contains |
|---|---|
| Console | One line per entry: id, run_id, runner status, state (completed / failed / reused / not launched), wall_s |
| `results/campaigns/<plan>.json` | The state projection and the value-free gate decisions |
| RUN_INDEX finish note | Status only; the full note is kept as `run_index_note_sealed` in the run's own `execution.json` (STARTED note unchanged) |
| `<sealed_dir>/<plan>.full.json` | The full record: metrics, reused-run RUN_INDEX notes, error texts, tracebacks, placeholders. Resume reads it |
| `<sealed_dir>/<plan>.console.log` | Everything a launch prints |

- State-only plans must run with `--workers 1`.
- run_0075 keeps its "possibly exposed" label (D7); prevention cannot restore it.
- **Recommendation for the main session:** move the existing `results/campaigns/campaign_C10_DIAGa_S2-11.json` under `results/sealed/` without opening it.

**Configs.** `config/campaign_C10_DIAG.json` was regenerated.
- Changed keys: `gates`, `state_only`, `stop_rules_enforced_by`, and one line of `global_rules`.
- The 19 run entries are identical, and the other 21 files in `config/*.json` are byte-identical.

## Tests and results (all after the final edit)

| Check | Result |
|---|---|
| `regress_all_decks.py` | `identical 58; unexpected differences 0`. The 58th deck is run_0075's, added after the earlier 57-count. |
| `make_campaign_configs.py --check` | `verbatim and in matrix order: YES`, exit 0. DIAG gates and state_only validated. |
| `score_register.py selftest` | `90/90 ok`. Hashes unchanged: c0f28bb9...b55a, and post_run_checks 39d3d51d...d91f. |
| `runner_selftest_2026-10-13.py` (814 lines) | `28/28 ok` (147 s). Real deckbuild/atlas/tonyplot/sflm executables and `C:\sedatools` arguments are refused, and the execute functions are faked. |

What the new cases cover:
- **A1:** plans with neither key still behave identically to the committed HEAD `run_campaign.py`.
- **A5 (acknowledgement rules):**
  - `--ack-gate` without an audit is refused;
  - `--ack-audit` alone is refused;
  - an audit that does not name the decision is refused;
  - a valid audit is recorded with its path, sha256 and decision.
- **A9:** a retry gives a new decision and supersedes the old one.
- **A12 (generated DIAG plan, state-only):** four stops, each resumed with a cited audit, then 13 entries; no marker leaks.
- **A13 (blocker 2):** a cached UNRESOLVED/continue decision is re-evaluated after:
  - a policy change plus new evidence;
  - an input-file change;
  - a legacy record with no binding.
- **A14:** after a declaration change, the gate stops again and needs a new acknowledgement.
- **A15 (blocker 3):**
  - no metric, error text or launch print reaches the console or the ordinary summary;
  - the full record and the prints are in the sealed sidecar;
  - every launch received `seal_notes=True`;
  - resume reads the sidecar.
- **A16:** invalid `state_only` declarations are refused.
- **B0:** defaults are `record`, there is no /T, and KEEP is set.
- **B6 (blocker 1):** a still-parented KEEP child survives the new cleanup; the former `taskkill /T` killed it.
- **B7 (blocker 1):**
  - a hanging fallback command is bounded at 2 s;
  - a simulated termination error is recorded;
  - the cleanup continues and terminates the root;
  - the whole run takes 10.0 s.
- **C1 (D5):**
  - `post_export_hang` is true only when `deckbuild.out` itself shows completion;
  - a completion line in the launcher stream alone gives false;
  - the diagnostic note is present;
  - `exit_code` stays `timeout`.
- **C3:** `seal_notes` gives a status-only RUN_INDEX note.

## Revision 3 (Codex revision-2 review, ~21:01Z)

Each item was first added as a regression case. Run on the revision-2 code, all four cases failed:

| Case | Revision-2 result |
|---|---|
| A17 | binding without the referenced runs (AttributeError on the missing structure) |
| A18 | codes [3, 0, 0]: the third invocation neither stopped nor evaluated |
| B8 | the stand-in licence daemon was terminated under the name `?` |
| B9 | the same, and nothing was reported as unidentified |

All four pass after the fixes.

**1. An unidentified job member could bypass KEEP** (`scripts/proc_guard.py`).
- `exe_name(pid, ct)` :134 reads the image name through a handle to the process itself (QueryFullProcessImageNameW :131). It returns a name only if the process's creation time still equals `ct`.
- `_candidates` :281 now queries the job before the snapshot (:285). The snapshot name is kept for the record only.
- `kill_all` :316 decides only on the verified name (:337). A member whose name cannot be verified is never terminated and never given the fallback. It is not marked handled, so it is re-scanned in every pass, and it is reported in `unidentified` and, if alive, in `survivors` (:365).
- A process that exits before it can be identified is listed in `exited_before_identification` (:342) and not touched.
- The opt-in viewer kill also uses the verified name (:272).
- **Tests:**
  - B8: a job member hidden from every snapshot is identified as `PING.EXE`, kept, and survives.
  - B9: an unidentifiable member is scanned 3 times, never terminated, gets no fallback, and is reported as an unidentified survivor.

**2. Stale evidence could keep a cached decision** (`scripts/campaign_gates.py`).
- `run_files` :85 hashes every INPUT_FILE of a run directory, recording a missing file as null.
- `evidence_state` :90 binds each cited evidence file together with the current files of the `run_dir` and `ref_dir` it references. Missing directories and files are included, and an unreadable JSON is marked as such.
- `binding` :104 uses both, for the input runs as well.
- **Test A17:** a pair JSON stays unchanged while a referenced `execution.json` is edited and then a referenced `terminal_currents.csv` is deleted. This gives 3 decisions (the first two superseded), and the deleted file is recorded as null.

**3. A superseded decision could be reused** (`scripts/campaign_gates.py`).
- `active` :204 returns a gate's latest non-superseded decision. `check` :210 reuses only the active decision, and only while its binding is current (:220).
- An active, current, unacknowledged stop is returned again.
- `decision_id` is now unique per evaluation (:227), so an audit can never cite an earlier evaluation that had the same binding.
- `held` already ignores superseded decisions.
- **Test A18:** A is an unacknowledged stop. B (a continue after a policy change) supersedes it. When A's declaration is restored, the gate is evaluated again and stops: codes [3, 0, 3], actions stop / continue / stop, three distinct decision ids.

**Self-test changes:** `--only ID[,ID]` selects cases (:79). The value-free scan ignores JSON path strings (:72), because a random temp-folder name (`iwo_audit_5c1e1nyj`) had matched the number pattern.

**Codex notes recorded:**
- run_0075 keeps its timeout facts and its "possibly exposed" label.
- `post_export_hang` does not change frozen-scorer eligibility.
- The supervised viewer test is needed only before enabling `IWO_ATLAS_VIEWERS=kill`. It is not needed for DIAG with the default `record`.

**Checks (revision 3, after the final edit)**

| Check | Result |
|---|---|
| `regress_all_decks.py` | `identical 58; unexpected differences 0` |
| `make_campaign_configs.py --check` | YES, exit 0 |
| `score_register.py selftest` | 90/90, sha256 c0f28bb9...b55a unchanged |
| `runner_selftest_2026-10-13.py` | 32/32 ok (173 s) |

No stand-in processes were left running, `results/RUN_INDEX.csv` is unchanged, and `results/sealed/campaigns` does not exist (the tests used temporary roots).

**sha256 of the changed and new files (revision 3)**

These hashes were taken after the final edit. This changelog cannot list its own hash.

| sha256 | file | changed in rev 3 |
|---|---|---|
| `6ac38ea89e0735d167c4df85e7b3efaeca83427970d172f4dd8b7b9fc48e7d80` | `scripts/proc_guard.py` (new, 385 lines) | yes |
| `c5e2fd5bb5711f7ab366d85fd8c13cb6bd3efcad387460308ea309e6348c0ceb` | `scripts/campaign_gates.py` (new, 293 lines) | yes |
| `09d374d220efb17995d12d611aba13c9617ad1f761d3fb8dec95ae1fdbf8608c` | `scripts/campaign_sealed.py` (new) | no |
| `fb6e802f8c1cb71b56e153ed99504cc8e7e83d4c8eb7af8f13dc421d0fd125ac` | `scripts/run_campaign.py` | no |
| `b7927ac5b9747d5531ac827d220da6004e4a144d672ae16ab9bca2a28f46e6ae` | `scripts/run_atlas.py` | no |
| `0ab12c192b323b4c296e14ba7c92812f64893dc09534d54e0c42c24b22ce9d2e` | `analysis_2026-10-10_campaign/make_campaign_configs.py` | no |
| `430a6d1abc107ced12f6878047c1ddfaffc011d653fb840bcd10497e9dda8474` | `config/campaign_C10_DIAG.json` | no |
| `f956e01b84ac0251d007eb17275504deabcb8b584df5046299d93996bc423520` | `analysis_2026-10-10_campaign/runner_selftest_2026-10-13.py` (new, 900 lines) | yes |

Unchanged reference files:
- `analysis_2026-10-10_campaign/score_register.py` (frozen): `c0f28bb942508a81a0f59b4a4c1e720bbfdbe8d9466d7e002476d64dcc10b55a`
- `analysis_2026-10-10_campaign/post_run_checks.py`: `39d3d51d3b2470b1396196bcfce34dc4a8f0a6acd3bcb2a213001dc5ec3ed91f`

## Still open (not runner work)

- The user's sign-off of the resolution method.
- The run_0075 rulings: timeout eligibility and the "possibly exposed" label.
- The audit files for the D1 acknowledgements during DIAG.
- A supervised DeckBuild test before viewer termination (D4) or the hidden desktop (D6) is adopted.
- TonyPlot's origin remains ASSUMED.
