#!/bin/bash
# A23 (ii)/(iii) DAG node: NC single point (TAG = pbe | hse) + projwfc.x, CPU (QE 7.5) via common/driver.sh.
# usage: nc_node.sh <name> <tag> <wall-time limit s> <pools>
# Every transfer_output file exists at exit: <name>_<tag>_results.tar.gz, scf_<tag>.out, projwfc_<tag>.out,
# atomic_proj_<tag>.xml, data-file-schema_<tag>.xml, STATUS_<tag>.
# Exit codes (DAG: RETRY <node> 1 UNLESS-EXIT 2):
#   0 DONE              'JOB DONE', converged energy ('!!' for hse, '!' for pbe), 'convergence has been achieved',
#                       projwfc 'JOB DONE' and a non-empty atomic_proj_<tag>.xml
#   2 SCF_NOT_CONVERGED 'convergence NOT achieved' (deterministic: not replayed)
#   2 PROJ_FAILED       the SCF finished but projwfc.x failed (not replayed: rerun projwfc only, by hand)
#   1 FAILED            anything else (crash, eviction, max_seconds stop): replayed once
NAME=${1:?name}; TAG=${2:?tag}; LIMIT=${3:-250000}; POOLS=${4:-1}
cd "${_CONDOR_SCRATCH_DIR:-$PWD}" || exit 1
export NC_TAG=$TAG NC_POOLS=$POOLS
cp steps_nc.sh steps.sh
echo FAILED > "STATUS_$TAG"
bash driver.sh "${NAME}_${TAG}" "$LIMIT"
for f in "${NAME}_${TAG}_results.tar.gz" "scf_$TAG.out" "projwfc_$TAG.out" "atomic_proj_$TAG.xml" "data-file-schema_$TAG.xml"; do
  [ -f "$f" ] || touch "$f"
done
OUT=scf_$TAG.out
if [ "$TAG" = hse ]; then E='^!!'; else E='^!'; fi
if grep -q 'convergence NOT achieved' "$OUT"; then
  S=SCF_NOT_CONVERGED; RC=2
elif grep -q 'JOB DONE' "$OUT" && grep -q "$E" "$OUT" && grep -q 'convergence has been achieved' "$OUT"; then
  if grep -q 'JOB DONE' "projwfc_$TAG.out" && [ -s "atomic_proj_$TAG.xml" ]; then S=DONE; RC=0; else S=PROJ_FAILED; RC=2; fi
else
  S=FAILED; RC=1
fi
echo "$S" > "STATUS_$TAG"
echo "$NAME $TAG: $S (exit $RC) $(grep "$E" "$OUT" 2>/dev/null | tail -1)"
exit $RC
