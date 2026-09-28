# Observed portable-verifier software test result

This is a retrospective audit note transcribed from the already observed tool result. It is not an original captured stdout file, a new test execution, or a simulator result. The tests were not rerun merely to create this note.

Working directory:

`C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_ATLAS_Model`

Observed command:

```powershell
.\.venv\Scripts\python.exe -B -m unittest tests.test_verify_copied_evidence -v
```

Observed process exit code: **0**.

Observed unittest footer:

```text
Ran 8 tests in 0.285s

OK
```

All eight tests reported `ok`:

1. `test_copied_import_origins_and_no_bytecode_writes`
2. `test_foreign_cached_module_refused_without_import`
3. `test_missing_13_control_is_incomplete_but_present_failure_is_not_hidden`
4. `test_output_new_and_cannot_overlap_native_evidence`
5. `test_rejects_absolute_drive_relative_and_parent_traversal`
6. `test_rejects_duplicate_role_missing_required_run_and_non13_null`
7. `test_requires_exact_expected_run_identity_and_unique_roles`
8. `test_wrapper_contains_no_runner_or_subprocess_import`

The fixtures were explicitly synthetic and used their own temporary directories under project `tmp/`. These tests exercised wrapper guards only. The wrapper was not invoked against actual copied native evidence during this test run; that verification awaits the final supplement integration.

For portable bundled tests, retain `tests/test_verify_copied_evidence.py`, the wrapper at `results/priority_three_20260912/verify_copied_evidence.py` (the test import location), and an existing project-local `tmp/` directory. The operational wrapper is separately copied to the supplement root.

