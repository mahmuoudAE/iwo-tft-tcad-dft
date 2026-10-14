#!/bin/bash
# H-L vacancy DAG node FINAL: single-point SCF at k 4x4x4 on the relaxed geometry (GPU, same container as RELAX).
# Based on common/final_node.sh. Differences: no pp.x / projwfc.x; scf.in, scf.out and FINAL_STATUS always exist
# (they are transferred back, a missing file would hold the job). Exit codes (DAG: RETRY FINAL 1 UNLESS-EXIT 2):
#   0 = DONE: 'JOB DONE', a converged total energy (a line starting with '!'), 'convergence has been achieved'
#       and no 'convergence NOT achieved' (A19)
#   2 = not replayed (deterministic, the same input would fail again):
#       SCF_NOT_CONVERGED   'convergence NOT achieved' in scf.out
#       RELAX_NOT_CONVERGED relax.out without 'bfgs converged' (A19); the k4 SCF is not run
#   1 = FAILED: anything else (scf.out empty or missing, no 'JOB DONE', or no '!' energy, e.g. a max_seconds stop
#       inside the SCF, which QE ends with 'JOB DONE' but without 'convergence NOT achieved'); replayed once
LIMIT=${1:-72000}
cd "${_CONDOR_SCRATCH_DIR:-$PWD}" || exit 1
if ! grep -q 'bfgs converged' relax.out 2>/dev/null; then
  touch final_results.tar.gz scf.in scf.out
  echo RELAX_NOT_CONVERGED > FINAL_STATUS; echo "relax.out has no 'bfgs converged': FINAL SCF not run (exit 2, not replayed)"; exit 2
fi
cp steps_final.sh steps.sh
bash driver.sh final "$LIMIT"
[ -f final_results.tar.gz ] || touch final_results.tar.gz
[ -f scf.in ] || touch scf.in
[ -f scf.out ] || touch scf.out
if grep -q 'convergence NOT achieved' scf.out; then
  echo SCF_NOT_CONVERGED > FINAL_STATUS; echo "final SCF not converged (exit 2, not replayed)"; exit 2
fi
if grep -q 'JOB DONE' scf.out && grep -q '^!' scf.out && grep -q 'convergence has been achieved' scf.out; then
  echo DONE > FINAL_STATUS; echo "final SCF done: $(grep '^!' scf.out | tail -1)"; exit 0
fi
echo FAILED > FINAL_STATUS; echo "final SCF failed: no converged energy (exit 1, replayed once)"; exit 1
