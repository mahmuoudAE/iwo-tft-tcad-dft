#!/bin/bash
# Upload a generated jobs folder to lxplus (~/<remote dir>) and submit it to HTCondor.
# Usage: cern_submit.sh <local jobs folder> <remote dir>
# Uses the SSH master connection opened by the user (no password or 2FA handled here).
set -uo pipefail
LOCAL=$1; RDIR=$2
CP=~/.ssh/cm-cern; H=melrashe@lxplus.cern.ch
S="ssh -o BatchMode=yes -o ControlPath=$CP $H"
log() { echo "[$(date -u +%FT%TZ)] $*"; }
ssh -O check -o ControlPath=$CP $H 2>&1 || { log "SSH master not running: nothing submitted"; exit 2; }
$S "test -e $RDIR" && { log "remote $RDIR exists: refusing to overwrite"; exit 3; }
log "upload $LOCAL -> $RDIR"
tar czf - -C "$LOCAL" . | $S "mkdir -p $RDIR/logs && tar xzf - -C $RDIR && sed -i 's/\r$//' $RDIR/driver.sh $RDIR/*/steps.sh && chmod +x $RDIR/driver.sh && du -sh $RDIR"
log "submit"
$S "cd $RDIR && condor_submit jobs.sub" 2>&1 | tee /tmp/cern_submit_$$.txt
CL=$(grep -oE 'cluster [0-9]+' /tmp/cern_submit_$$.txt | awk '{print $2}')
[ -n "$CL" ] || { log "submission failed"; exit 4; }
echo "$CL" > "$LOCAL/cluster.txt"
log "cluster $CL"
$S "condor_q $CL -af IWOJob RequestCpus JobStatus"
