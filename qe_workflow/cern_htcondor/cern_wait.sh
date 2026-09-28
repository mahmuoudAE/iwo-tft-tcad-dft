#!/bin/bash
# Watch an HTCondor cluster; fetch every finished job's results; exit on the first new result,
# on a held job, when the queue is empty, or when the SSH master is gone (jobs keep running at CERN).
# Usage: cern_wait.sh <cluster> <remote dir> <local results folder> [poll seconds]
set -uo pipefail
CL=$1; RDIR=$2; RES=$3; POLL=${4:-600}
CP=~/.ssh/cm-cern; H=melrashe@lxplus.cern.ch
S="ssh -o BatchMode=yes -o ControlPath=$CP $H"
log() { echo "[$(date -u +%FT%TZ)] $*"; }
mkdir -p "$RES"
while true; do
  if ! ssh -O check -o ControlPath=$CP $H > /dev/null 2>&1; then log "SSH master lost; jobs continue at CERN"; exit 3; fi
  Q=$($S "condor_q $CL -af IWOJob JobStatus RemoteWallClockTime" 2>/dev/null)
  REMOTE=$($S "cd $RDIR && ls *_results.tar.gz 2>/dev/null")
  NEW=0
  for f in $REMOTE; do
    j=${f%_results.tar.gz}
    [ -e "$RES/$j/.fetched" ] && continue
    mkdir -p "$RES/$j"
    scp -q -o BatchMode=yes -o ControlPath=$CP "$H:$RDIR/$f" "$RES/$j/" && tar xzf "$RES/$j/$f" -C "$RES/$j" && touch "$RES/$j/.fetched"
    log "fetched $j: $(tail -1 "$RES/$j/${j}_driver.log" 2>/dev/null)"
    NEW=1
  done
  HELD=$(echo "$Q" | awk '$2==5{print $1}')
  if [ -n "$HELD" ]; then
    log "held: $HELD"; $S "condor_q $CL -af IWOJob HoldReason"; exit 4
  fi
  if [ "$NEW" = 1 ] || [ -z "$Q" ]; then
    log "queue (job status wall_s; 1 idle, 2 running):"; echo "$Q"
    [ -z "$Q" ] && log "queue empty"
    exit 0
  fi
  sleep "$POLL"
done
