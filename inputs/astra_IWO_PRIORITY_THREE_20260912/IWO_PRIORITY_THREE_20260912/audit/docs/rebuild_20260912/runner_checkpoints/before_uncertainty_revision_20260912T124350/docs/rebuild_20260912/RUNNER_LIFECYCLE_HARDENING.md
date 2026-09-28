# Missing native completion evidence and bounded runner hardening

Prepared 2026-09-12 after read-only comparison and mocked software tests. No simulator was launched for this change. This is a process-lifecycle repair, not a model-physics change or a relaxation of native completion acceptance.

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
- Fail closed if an observed child disappears before ownership can be pinned, tracking fails, an owned descendant exits nonzero, cleanup remains unresolved, or bookkeeping fails. A prelaunch durable poison guard is written before `Popen`; atomic guard updates preserve it if storage fails. Missing or malformed lifecycle evidence cannot authorize another engine.
- On timeout, terminate only identity-pinned owned processes, rescan after termination for newly observed children, and reserve cleanup time inside the original deadline. No helper process, name-based kill, or unrelated process termination is used. If the bounded wait cannot establish closure, the mutex is eventually released but the persistent guard blocks a subsequent launch pending lifecycle review.
- Recompute remaining UTC budget after project preparation, convert it to an anchored monotonic deadline, and check again immediately before `Popen`. Preparation and bookkeeping cannot add time to the session allowance. Expiry during preparation creates no launch reservation; expiry after a durable reservation but before `Popen` conservatively retains that reservation, records failure, and launches nothing.

All newly started native processes retain `CREATE_NO_WINDOW`; simulator TEMP/TMP remain in the project. The implementation uses only Python's standard library and native Windows APIs.

This tracks **observed** process lineage. A completely unobserved, short-lived intermediate is a known snapshot limitation; this is not complete process-tree certification. File quiescence cannot recover text that the native application never forwards or writes. The repair therefore **does not guarantee** the missing banner will recur or disappear. An exact fresh retry remains necessary; missing native completion evidence must still reject that retry.

## Verification and change preservation

The 13 mocked lifecycle tests, 18 existing/extended combined-generation and budget tests, and 19 package tests pass (50 total). They cover delayed child exit/output, deadline cleanup, stuck/vanished children, PID reuse, parent-exit query ordering, post-kill closure, nonzero descendant exit, atomic guard failure, preparation/bookkeeping deadline expiry, durable launch reservation, and spawn-index write failure. No real simulator or real process termination is used by these tests. Test TEMP/TMP and fixtures stay under project `tmp`. A separate read-only native API check opened only the current Python process handle and checked structure layout/identity; it performed no process creation or termination.

No exact immediate pre-hardening backup or Git repository was found. `runner_checkpoints/20260912T123822` preserves an untouched older delivery copy, a tested working snapshot, and **explicitly labeled reconstructed** pre-hardening files for review. The reconstruction is not claimed to be byte-identical to the immediate original. Its README and hashes record that limitation. Later reviewed changes are stored in a separate checkpoint rather than overwriting it.

The next simulator action belongs to the root task: an exact fresh 6.3 nm retry under the unchanged remaining launch/time allowance, after independent runner review. Native result selection, numerical controls, and fit reporting remain separate acceptance steps.
