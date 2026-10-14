#!/bin/bash
# PILOT A15 node script (aIO_0p8_s1 only). Same as common/relax_node.sh except the exit code:
# 0 = CONVERGED, 1 = CONTINUE (DAGMan retries = next segment), 2 = FAILED (RETRY ... UNLESS-EXIT 2: not replayed).
SEG=${1:-0}; LIMIT=${2:-72000}
cd "${_CONDOR_SCRATCH_DIR:-$PWD}" || exit 2
cp steps_relax.sh steps.sh
echo FAILED > RELAX_STATUS
bash driver.sh "relax_s${SEG}" "$LIMIT"
[ -f "relax_s${SEG}_results.tar.gz" ] || tar czf "relax_s${SEG}_results.tar.gz" ./*.log 2>/dev/null || touch "relax_s${SEG}_results.tar.gz"
[ -f relax.out ] || touch relax.out
[ -f SEGMENT_SUMMARY ] || echo "no summary" > SEGMENT_SUMMARY
STATUS=$(cat RELAX_STATUS)
echo "segment $SEG finished with status $STATUS: $(cat SEGMENT_SUMMARY)"
case "$STATUS" in CONVERGED) exit 0 ;; CONTINUE) exit 1 ;; *) exit 2 ;; esac
