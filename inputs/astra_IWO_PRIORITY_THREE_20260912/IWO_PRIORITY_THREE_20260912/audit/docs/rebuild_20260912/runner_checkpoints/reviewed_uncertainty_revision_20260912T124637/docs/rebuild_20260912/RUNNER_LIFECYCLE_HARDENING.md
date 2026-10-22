# Missing native completion evidence and bounded runner hardening

Prepared 2026-09-12 after read-only comparison and mocked software tests; updated after the root task's 12:40 UTC retry exposed an overly aggressive helper policy. The software-editing agent launched no simulator. This is a process-lifecycle repair, not a model-physics change or a relaxation of native completion acceptance.

## Observed failure

`20260912T121627_947928_priority3_fit6_mu12` reached the 121 requested gate targets, wrote the final structure and exports, and ended its text at `EXTRACT> quit` followed by `quit`. The launcher returned zero after 428.907 seconds, below its 900-second timeout; launcher stderr is empty. Its 154,321-byte `deckbuild.out` contains **no ATLAS finished banner**. All output hashes frozen in its execution record still match after the later audit. The run remains unverified and must not be used as an accepted fitted result.

The retained run `20260912T091742_999942_extension02_charge_6p3nm` has the same closing extraction sequence followed by `ATLAS version 5.28.1.R finished at Sat Sep 12 17:25:20 2026`. Its launcher returned zero after 457.844 seconds, stderr is empty, and all saved hashes also match. Its raw output is 154,384 bytes. These runs have different mobility parameters and are not an exact-deck reproduction pair.

An independent historical exact-deck pair shows the intermittent symptom: `20260912T070700_067594_class_interface_2nm` lacks the banner, whereas `20260912T070939_155897_class_interface_repeat_2nm` includes it. Both `device.in` files have SHA256 `1e0634c8f935e445fd1089cda0f925ba22c83e30b06e295ac6110c5f0b8853b7`; both returned launcher zero with empty stderr and unchanged recorded output hashes. Their durations were 90.328 and 93.047 seconds respectively.

No Python timeout was recorded for the missing-banner 6.3 nm run. Unchanged raw hashes show that the banner was not simply appended after Python took its hash. Intermittent native shutdown or forwarded-output capture is plausible, but the exact loss mechanism is **not proven** by the available old records.

## Concrete management gap and repair

A read-only observation of a later, separate owned run showed five process levels: the DeckBuild wrapper, versioned DeckBuild, ATLAS wrapper, versioned ATLAS, and `atlas2`. The old runner waited only for its direct `Popen` launcher. It did not record descendant exit times or wait for the native output file to become quiet. That gap is repaired without changing the native deck, configuration, raw historical results, or checker.

The revised `local_probe.py` uses `owned_process_lifecycle.py` to:

- Keep the project mutex during the bounded wait for observed owned descendants and a 0.75-second period of unchanged output file sizes/timestamps. Every return still requires the separate native completion check.
- Pin candidate process identities with Windows handles and creation times, refresh their parent association while the candidate is still running, and check the parent's signaled state before using its exit time. Unrelated processes are neither adopted nor terminated. Only owned identity details are recorded; broad snapshots are used internally to discover parent relationships.
- Preserve a next-launch guard if an observed child disappears before ownership can be pinned. The current simulator continues its bounded natural run; a missed helper alone does not trigger termination. If all observed processes exit and output drains normally, the actual launcher return code is retained with `PROCESS_EXITED_LIFECYCLE_REVIEW_REQUIRED`; this does not assert complete lineage closure. A separate recorded review must reconcile the guard before another launch. Tracking errors, nonzero observed descendant exit, unresolved live processes, or bookkeeping failure remain failures. A prelaunch durable poison guard is written before `Popen`; atomic guard updates preserve it if storage fails. Missing or malformed lifecycle evidence cannot authorize another engine.
- On timeout, terminate only identity-pinned owned processes, rescan after termination for newly observed children, and reserve cleanup time inside the original deadline. No helper process, name-based kill, or unrelated process termination is used. If the bounded wait cannot establish closure, the mutex is eventually released but the persistent guard blocks a subsequent launch pending lifecycle review.
- Recompute remaining UTC budget after project preparation, convert it to an anchored monotonic deadline, and check again immediately before `Popen`. Preparation and bookkeeping cannot add time to the session allowance. Expiry during preparation creates no launch reservation; expiry after a durable reservation but before `Popen` conservatively retains that reservation, records failure, and launches nothing.

All newly started native processes retain `CREATE_NO_WINDOW`; simulator TEMP/TMP remain in the project. The implementation uses only Python's standard library and native Windows APIs.

This tracks **observed** process lineage. A completely unobserved, short-lived intermediate is a known snapshot limitation; this is not complete process-tree certification. File quiescence cannot recover text that the native application never forwards or writes. The repair therefore **does not guarantee** the missing banner will recur or disappear. An exact fresh retry remains necessary; missing native completion evidence must still reject that retry.

## Actual startup abort and correction

The first guarded retry, `20260912T124052_500555_priority3_fit6_mu12_retry`, ended after 5.969 seconds with `OWNED_PROCESS_CLEANUP_UNRESOLVED`. Its unchanged input deck hash equals the missing-banner candidate's hash, `af274661c5dc74d3ec57000997ab821e466fdca2872b6912e423679336b2c3a1`. Its output contains only the ATLAS startup banner. The former helper policy raised immediately after one short-lived child could not be pinned, then terminated the launcher. This was **a runner-induced startup abort**, not a TCAD convergence failure or a fit result.

Eleven owned identities were recorded; several helpers had already exited zero, and a burst of child creation occurred around ATLAS startup. That run did not record the missing PID or the handle causing its cleanup `WinError 5`, so the exact helper and error target cannot be reconstructed. Windows documents that `TerminateProcess` on an already terminated process returns access denied; this makes an exit race plausible, not proven for that run. The corrected implementation rechecks the same pinned handle after a failed termination request, ignores the error only if it is signaled, records each attempted target/outcome, and continues cleanup of other proven owned handles after one error. See the [Microsoft TerminateProcess documentation](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-terminateprocess).

New evidence records owned executable basenames from held process handles, plus missed PID, observed parent, unpinned snapshot basename, observation time, and reason. Basenames do not confer ownership, excuse a nonzero exit, or establish native success. A missed helper is now retained as reviewable uncertainty while the legitimate simulator is allowed to finish within its existing deadline. Native banner, hashes, all requested points, signed currents, KCL, and model checks are unchanged.

The root task separately reconciled the failed retry: all eleven recorded owned PIDs were absent and no current ATLAS process was found; unrelated pre-existing GUI sessions were left alone. It archived the guard before removing only that project marker. Evidence is in `results/priority_three_20260912/lifecycle_recovery_1240/reconciliation.json` and `prior_pending_guard.json`. That reconciliation does not turn the aborted retry into a valid simulation.

## Verification and change preservation

The 16 mocked lifecycle tests, 18 existing/extended combined-generation and budget tests, and 19 package tests pass (53 total). They cover delayed child exit/output, deadline cleanup, stuck/vanished children, PID reuse, parent-exit query ordering, post-kill closure, nonzero descendant exit despite a helper gap, atomic guard failure, preparation/bookkeeping deadline expiry, durable launch reservation, spawn-index write failure, continued cleanup after one handle error, and signaled rechecking after access denied. No real simulator or real process termination is used by these tests. Test TEMP/TMP and fixtures stay under project `tmp`. A separate read-only native API check opened only the current Python process handle and checked structure layout/identity; it performed no process creation or termination.

No exact immediate pre-hardening backup or Git repository was found. `runner_checkpoints/20260912T123822` preserves an untouched older delivery copy, a tested working snapshot, and **explicitly labeled reconstructed** pre-hardening files for review. The reconstruction is not claimed to be byte-identical to the immediate original. Its README and hashes record that limitation. Later reviewed changes are stored in a separate checkpoint rather than overwriting it.

The helper-policy correction has an exact prechange byte-copy backup at `runner_checkpoints/before_uncertainty_revision_20260912T124350`, including source, tests, prior note, and SHA256 manifest.

The next simulator action belongs to the root task: an exact fresh 6.3 nm retry under the unchanged remaining launch/time allowance, after independent runner review. Native result selection, numerical controls, and fit reporting remain separate acceptance steps.
