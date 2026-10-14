#!/bin/bash
# Validation job: one SCF with forces on a MACE snapshot (CPU, QE 7.5).
LIMIT=${1:-72000}
cd "${_CONDOR_SCRATCH_DIR:-$PWD}" || exit 1
cp steps_val.sh steps.sh
bash driver.sh val "$LIMIT"
[ -f val_results.tar.gz ] || touch val_results.tar.gz
grep -q 'JOB DONE' scf.out 2>/dev/null
