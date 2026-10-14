# A23 (i) PBE bulk references: aIO_bulk_s1, aIWO_bulk_s1

Local mirror of `~/iwo_amorph/runs/aIO_bulk_s1/` and `~/iwo_amorph/runs/aIWO_bulk_s1/` (files under `runs/`,
byte-identical to CERN, md5-checked 2026-10-11T01:00Z). Built by `compute/amorph/dft/make_bulkref.py`
(CERN `common/make_bulkref.py`, md5 141edd2ce337bd4b3ce70ee2a88fd80a); provenance in each `runs/<name>/PROVENANCE`.
Dry check: `check_bulkref.py` (run on CERN read-only before submission: RESULT: PASS).

Setup (register A23 (i)): relax atoms only (fixed cell), PAW 60/480 Ry, k 2x2x2, Gaussian 0.005, repaired relax
machinery (pilot node script, exit 0 CONVERGED / 1 CONTINUE / 2 FAILED; CONVERGED only with 'bfgs converged';
DAG `RETRY RELAX 8 UNLESS-EXIT 2`), 1 GPU H100|H200|A100 (no MIG), 64 GB. FINAL: SCF 71/568 Ry, Gaussian 0.005,
projections via the slab export machinery, CPU 32 / 100 GB, submitted by DAGMan with `hold = True` (A15 gate:
release only after the smearing audit and the D-24 export are in place).

## Submission log

| UTC | name | batch name | DAGMan cluster | RELAX node cluster (seg 0) | state at record |
|---|---|---|---|---|---|
| 2026-10-11T01:01:44Z | aIO_bulk_s1 | aIO_bulk_s1_ref | 12888461 | 12888463 | RELAX idle; FINAL Un-Ready (not submitted) |
| 2026-10-11T01:01:44Z | aIWO_bulk_s1 | aIWO_bulk_s1_ref | 12888462 | 12888464 | RELAX idle; FINAL Un-Ready (not submitted) |

Command (in each run dir): `condor_submit_dag -batch-name <name>_ref <name>.dag`.
Queue check 2026-10-11T01:01:59Z: before 55 entries (23 DAGMan + 32 node jobs), after 59 (+12888461, +12888462
DAGMan; +12888463, +12888464 RELAX, 1 GPU, 66000 MB). DAGMan tables: Queued 1, Un-Ready 1 (FINAL) for both.
Not submitted: A23 (ii) In31WO48 HSE06 and (iii) aIO_bulk_s1 HSE06 (staged under `compute/amorph/hse/`).
Next: copy outputs with `snapshot_jobs.sh` while segments run; after RELAX CONVERGED, FINAL appears held and is
released only through the A15 gate.
