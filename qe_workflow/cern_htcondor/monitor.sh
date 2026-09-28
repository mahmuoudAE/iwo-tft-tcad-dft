#!/bin/bash
# 30-minute monitor (user request 2026-09-27): logs every check to monitor.log and exits (to notify Claude) when
#  - a job's results appear in one of the remote job folders (fetched into results/<job>/),
#  - a job is held, a running job has too many threads (> 3 per rank), or its SCF stops advancing,
#  - the SSH master is gone, or the local stage 3 has finished.
# Usage (distro Ubuntu): monitor.sh "<remote dir> <remote dir> ..."
C="/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff (1)/IWO_PHYSICS_CONSTRAINED_MODEL_V1/qe_workflow"
DIRS=${1:-$(sed 's/\r$//' "$C/cern_htcondor/remote_dirs.txt" | tr '\n' ' ')}   # default: every submitted job folder
RES="$C/cern_htcondor/results"; LOG="$C/cern_htcondor/monitor.log"
CP=$HOME/.ssh/cm-cern; H=melrashe@lxplus.cern.ch
S="ssh -o BatchMode=yes -o ControlPath=$CP $H"
declare -A LASTIT=()
while true; do
  now=$(date -u +%FT%TZ)
  if ! ssh -O check -o ControlPath=$CP $H > /dev/null 2>&1; then echo "$now SSH master lost" | tee -a "$LOG"; exit 3; fi
  EVENT=""
  # results
  for d in $DIRS; do
    for f in $($S "cd $d 2>/dev/null && ls *_results.tar.gz 2>/dev/null"); do
      j=${f%_results.tar.gz}; [ -e "$RES/$j/.fetched" ] && continue
      mkdir -p "$RES/$j"
      scp -q -o BatchMode=yes -o ControlPath=$CP "$H:$d/$f" "$RES/$j/" && tar xzf "$RES/$j/$f" -C "$RES/$j" && touch "$RES/$j/.fetched"
      EVENT="$EVENT fetched:$j"
    done
  done
  # queue, threads and SCF progress of running jobs
  Q=$($S "condor_q -af ClusterId ProcId IWOJob JobStatus" 2>/dev/null)
  echo "$now queue: $(echo "$Q" | awk '{printf "%s=%s ", $3, ($4==2?"run":($4==1?"idle":($4==5?"HELD":$4)))}')" >> "$LOG"
  echo "$Q" | awk '$4==5' | grep -q . && EVENT="$EVENT held:$(echo "$Q" | awk '$4==5{printf "%s ", $3}')"
  while read -r cl pr job st; do
    [ "$st" = "2" ] || continue
    info=$($S "timeout 90 condor_ssh_to_job $cl.$pr 'bash -s'" 2>/dev/null <<'EOF' | tail -1
o=$(ls -t *.out 2>/dev/null | head -1); echo "$(pgrep -c pw.x) $(ps -L -C pw.x --no-headers | wc -l) $(grep -c 'iteration #' $o 2>/dev/null) $o"
EOF
)
    set -- $info
    [ $# -ge 3 ] || continue
    echo "   $job: ranks=$1 threads=$2 scf_iterations=$3 in $4" >> "$LOG"
    # GPU jobs run few ranks with OpenMP threads on purpose: only multi-rank CPU jobs are checked
    [ "$1" -gt 2 ] && [ "$2" -gt $(( 3 * $1 )) ] && EVENT="$EVENT threads:$job"
    key="$cl.$pr.$4"
    [ "$3" -gt 0 ] && [ -n "${LASTIT[$key]:-}" ] && [ "${LASTIT[$key]}" = "$3" ] && EVENT="$EVENT stalled:$job"
    LASTIT[$key]=$3
  done <<< "$Q"
  # local stage 3
  grep -qE 'STAGE3 (DONE|STOPPED)' "$C/bulk_In2O3_protocol/stage3.log" 2>/dev/null && [ ! -e "$RES/.stage3_reported" ] && { touch "$RES/.stage3_reported"; EVENT="$EVENT stage3_done"; }
  if [ -n "$EVENT" ]; then echo "$now EVENT:$EVENT" | tee -a "$LOG"; tail -12 "$LOG"; exit 0; fi
  sleep 1800
done
