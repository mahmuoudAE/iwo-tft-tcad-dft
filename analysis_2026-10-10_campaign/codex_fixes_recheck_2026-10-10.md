# Codex re-check of the responses to its fix review (2026-10-10)

- **What this is.** The final answer of a read-only Codex run (codex-cli 0.162.0 in WSL "Ubuntu", `codex exec --sandbox read-only`). Prompt: `codex_fixes_recheck_prompt_2026-10-10.md`; full log: `codex_fixes_recheck.log`. Codex ran no simulator and changed no file.
- **Outcome.** All FIX points and the three new defects were adopted (IMPLEMENTATION.md §11.9). These last changes were tested by the self-tests in `selftest_2026-10-10/` but were not sent to Codex a third time.

---

Read-only inspection only; no scripts executed, files changed, or network used.

- **(a) OK for re-launching; FIX retry bookkeeping.** Subtracting `retry` works. However, the old successful record remains when the retry fails; the next resume treats that ID as done. In `run_campaign.py:158–160`, replace prior records for the ID with the latest attempt, or compute `done` from each ID’s latest attempt only.

- **(b) OK.** `reserve()` uses the minimum of the overridden value and the freshly read disk cap. An override cannot raise that cap.

- **(c) FIX; electron isolation is correct.** TMUN comparison at `post_run_checks.py:146` compares formatting, not numeric values: equivalent `0`, `0.0`, and scientific notation can disagree. Parse floats and compare numerically. Control checks add the claimed conditions, but identical overrides do not establish identical historical geometry/solver inputs after config edits. Verify saved effective inputs or normalized decks. Before `np.interp` at `:208`, require finite control currents and complete voltage coverage; missing exports currently crash, and endpoint clamping can produce false activation evidence. Return both models UNVERIFIED.

- **(d) FIX; coverage/convergence verdicts and ordinary result exit mapping are correct.** Rounded Qf equality admits unequal starting charges; compare actual values with explicit tight tolerance. Detect breakers from effective settings, including defaults, rather than enabled override strings alone (`profile_shared.py:53`). Refusals raise string `SystemExit`, yielding **1**, although the stated mapping requires **3**. Filter `--allow-approximate` from adoption’s branch operands; currently it can become a fourth run argument. Pass the flag to both triples and propagate APPROXIMATE from either.

- **(e) FIX.** `run_campaign.py:110` distinguishes only strip/non-strip, so output and transfer can reuse each other. Normalize and compare all modes; also verify output sweeps and saved geometry/solver or regenerated deck identity.

New defects include stale retry success, refusal exit-code mismatch, and adoption flag parsing.
