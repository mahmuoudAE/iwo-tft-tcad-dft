#!/bin/bash
# DAG node FINAL: SCF at the protocol cutoff on the relaxed geometry, planar-averaged potential, projwfc (CPU, QE 7.5).
LIMIT=${1:-72000}
cd "${_CONDOR_SCRATCH_DIR:-$PWD}" || exit 1
cp steps_final.sh steps.sh
bash driver.sh final "$LIMIT"
[ -f final_results.tar.gz ] || touch final_results.tar.gz
grep -q 'JOB DONE' scf.out 2>/dev/null
