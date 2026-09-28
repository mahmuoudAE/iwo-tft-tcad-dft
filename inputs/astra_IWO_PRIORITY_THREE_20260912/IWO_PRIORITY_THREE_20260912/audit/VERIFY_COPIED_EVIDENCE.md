# Recheck the copied native evidence

Place `verify_copied_evidence.py` at the supplement root, beside these copied items:

- `verification_inputs.json`
- `scripts/rebuild_model.py`, `scripts/rebuild_check.py`, `scripts/rebuild_extension_check.py`
- `MANIFEST_SHA256.json` and all four original `data/iwo_*nm.csv` files
- Complete selected/control native run directories under `results/`, preserving project-relative layout.

Use Python with NumPy installed, preferably the supplied dependency versions. From any working directory, run the wrapper by its path:

```powershell
python -B .\verify_copied_evidence.py
```

The wrapper derives its root from its own file location. It rejects absolute or traversing input paths, mismatched native run IDs, cached checkers from another project, and outputs overlapping native evidence. It imports the copied checker modules and their copied renderer; it imports no simulator runner and launches no simulator. It writes no bytecode into copied scripts.

A new `verification/YYYYMMDDTHHMMSS_microsecondsZ/` directory receives:

- A snapshot of the input mapping.
- A fresh 2 nm width/x/y/DOS certificate computed by the copied native checker.
- Fresh 6.3 and 13.2 nm x/y/DOS assessments using that newly created 2 nm certificate as their local width-unit basis.
- `VERIFICATION_SUMMARY.json` with statuses, unchanged checker thresholds, exact module origins and hashes.

Original absolute paths stored in old certificates are not followed. Original certificates, configs, data and native runs remain untouched. Reports can contain the current supplement's absolute paths; rerunning after moving the supplement produces new local reports.

The root agent supplies the exact selected run IDs and relative copied paths in this schema:

```json
{
  "schema_version": 1,
  "devices": {
    "2p0": {
      "reference": {"path": "results/local_session_20260910/runs/EXACT_2NM_REFERENCE", "run_id": "EXACT_2NM_REFERENCE"},
      "controls": {
        "width": {"path": "results/local_session_20260910/runs/EXACT_2NM_WIDTH", "run_id": "EXACT_2NM_WIDTH"},
        "xmesh": {"path": "results/local_session_20260910/runs/EXACT_2NM_X", "run_id": "EXACT_2NM_X"},
        "ymesh": {"path": "results/local_session_20260910/runs/EXACT_2NM_Y", "run_id": "EXACT_2NM_Y"},
        "dos": {"path": "results/local_session_20260910/runs/EXACT_2NM_DOS", "run_id": "EXACT_2NM_DOS"}
      }
    },
    "6p3": {
      "reference": {"path": "results/local_session_20260910/runs/EXACT_6NM_REFERENCE", "run_id": "EXACT_6NM_REFERENCE"},
      "controls": {
        "xmesh": {"path": "results/local_session_20260910/runs/EXACT_6NM_X", "run_id": "EXACT_6NM_X"},
        "ymesh": {"path": "results/local_session_20260910/runs/EXACT_6NM_Y", "run_id": "EXACT_6NM_Y"},
        "dos": {"path": "results/local_session_20260910/runs/EXACT_6NM_DOS", "run_id": "EXACT_6NM_DOS"}
      }
    },
    "13p2": {
      "reference": {"path": "results/local_session_20260910/runs/EXACT_13NM_REFERENCE", "run_id": "EXACT_13NM_REFERENCE"},
      "controls": {
        "xmesh": null,
        "ymesh": null,
        "dos": null
      }
    }
  }
}
```

Replace each placeholder with an exact copied native run. Only unavailable 13.2 nm controls may be `null`; an absent path must not masquerade as a completed control. Missing 13.2 nm controls produce explicit `INCOMPLETE` status and a list of missing controls. A supplied control that fails evidence or numerical checks is rejected; missing controls cannot hide that failure.

Exit codes: 0 = all mapped numerical scopes pass; 1 = valid available evidence but an explicitly missing 13.2 nm control; 2 = rejected input/evidence or a numerical failure. Full numerical PASS grants no measurement-fit, off-current, quantum, microscopic-defect or process-prediction claim. The 6.3/13.2 nm scopes transfer the width-unit convention from the freshly recomputed 2 nm pair; they do not assert repeated per-film width tests.

Lifecycle reconciliation sidecars remain a separate audit record. This wrapper does not claim retrospective closure of missed helper lineage. No verification output is an additional ATLAS simulation.

The standalone synthetic guard tests are `tests/test_verify_copied_evidence.py` in the working project. They exercise path and run-ID checks, missing-control scope, copied import origin, output protection and absence of runner imports; they do not verify or generate native simulation data.

