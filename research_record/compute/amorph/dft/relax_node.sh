#!/bin/bash
# DAG node RELAX: one <= 20 h segment of a QE relaxation. Exit 0 when BFGS converged (DAG moves on to FINAL),
# exit 1 otherwise; DAGMan then retries the node, i.e. submits the next segment from the updated relax.in.
# relax.in, RELAX_STATUS and relax_s<seg>_results.tar.gz always exist at the end, so the output transfer never fails.
# D-24 (2026-10-11): three fail-fast stops before driver.sh unpacks anything; each ends the job within seconds:
#  1. segment_stop (input only, never transferred back): a line starting with STOP (or FAILED) written by a person or
#     by install_D24_BD.sh (transition of a chain whose last segment ran the pre-D-24 steps). A running job cannot
#     overwrite it, so it can be armed at any time.
#  2. segment_guard (input and output): steps_relax.sh writes 'FAILED <utc> <job> [<category>]: <reason>' into it when a
#     segment fails, so every later retry of the chain stops here instead of replaying the failed segment for hours
#     (these DAGs have no UNLESS-EXIT).
#     1 and 2 are inert when the node does not transfer the file (vac DAGs, the A15 pilot, ads submitted before D-24)
#     or when it holds no such line. Reset: ~/iwo_amorph/common/README_D24_BD.txt section 3.
#  3. preflight. A steps_relax.sh that needs geomsel.py, started by a job ad that does not transfer it (submitted
#     before D-24), stops without running pw.x; the DAG retry is submitted from the new relax.sub.
SEG=${1:-0}; LIMIT=${2:-72000}
cd "${_CONDOR_SCRATCH_DIR:-$PWD}" || exit 1

stop_now() {   # stop_now <reason>: RELAX_STATUS FAILED, a small note as the segment tarball, all outputs present, exit 1
  echo FAILED > RELAX_STATUS
  # the note uses the driver-log name and 'relax status:' line, so lineage tools and the dashboard read it
  echo "[$(date -u +%FT%TZ)] relax status: FAILED (stopped before pw.x on $(hostname)); $1" > "relax_s${SEG}_driver.log"
  local f m=("relax_s${SEG}_driver.log")
  for f in relax.in segment_guard segment_stop; do [ -f "$f" ] && m+=("$f"); done
  tar czf "relax_s${SEG}_results.tar.gz" "${m[@]}" 2>/dev/null || touch "relax_s${SEG}_results.tar.gz"
  for f in $(awk -F' = ' '/^TransferOutput /{print $2}' "${_CONDOR_JOB_AD:-/dev/null}" 2>/dev/null | tr -d '"' | tr ',' ' '); do
    case "$f" in
      *.in) ;;   # never create an empty relax.in: it would replace the chain's geometry on the access point
      *) [ -e "$f" ] || touch "$f" ;;
    esac
  done
  echo "segment $SEG stopped: $1"
  exit 1
}

for g in segment_stop segment_guard; do
  if [ -s "$g" ] && grep -q -E '^(STOP|FAILED)' "$g"; then
    stop_now "$g: $(grep -m1 -E '^(STOP|FAILED)' "$g")"
  fi
done
if grep -q 'geomsel\.py' steps_relax.sh 2>/dev/null && [ ! -f geomsel.py ]; then
  stop_now "preflight: steps_relax.sh needs geomsel.py, which this job ad does not transfer (submitted before D-24)"
fi

cp steps_relax.sh steps.sh
echo FAILED > RELAX_STATUS
bash driver.sh "relax_s${SEG}" "$LIMIT"
[ -f "relax_s${SEG}_results.tar.gz" ] || tar czf "relax_s${SEG}_results.tar.gz" ./*.log 2>/dev/null || touch "relax_s${SEG}_results.tar.gz"
STATUS=$(cat RELAX_STATUS)
echo "segment $SEG finished with status $STATUS"
[ "$STATUS" = CONVERGED ]
