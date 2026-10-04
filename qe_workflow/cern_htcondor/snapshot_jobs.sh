#!/bin/bash
# Safety net for long jobs whose own EOS checkpoints fail (the job's Kerberos ticket expired after ~25 h and was not
# renewed: xrdcp from slab2_relax_c2 refused with "unauthorized identity", 2026-10-03). Every INTERVAL minutes the text
# outputs of each running job matching PATTERN are copied to the laptop through the author's lxplus session
# (condor_ssh_to_job), into results/live_snapshots/<job>/. A relaxation can then be continued from its last geometry.
# Usage: bash snapshot_jobs.sh [PATTERN] [INTERVAL_MIN] [HOURS]
PAT=${1:-slab2_relax}; MIN=${2:-15}; HOURS=${3:-96}
HERE="$(cd "$(dirname "$0")" && pwd)"; OUT="$HERE/results/live_snapshots"; mkdir -p "$OUT"
S="ssh -o BatchMode=yes -o ConnectTimeout=30 -o ControlPath=$HOME/.ssh/cm-cern melrashe@lxplus.cern.ch"
end=$(( $(date +%s) + HOURS * 3600 ))
while [ "$(date +%s)" -lt "$end" ]; do
  while read -r id job st <&3; do
    [ "$st" = 2 ] || continue
    d="$OUT/$job"; mkdir -p "$d"; tmp="$d.part.tgz"
    if $S "timeout 300 condor_ssh_to_job $id 'tar czf - --ignore-failed-read *.out *.in *.log *_avg.dat pdos 2>/dev/null'" > "$tmp" 2>/dev/null \
       && [ -s "$tmp" ] && tar xzf "$tmp" -C "$d" 2>/dev/null; then
      echo "$(date -u +%FT%TZ) $job ($id): $(grep -c 'number of bfgs steps' "$d"/*relax.out 2>/dev/null | tail -1) bfgs steps, files: $(ls "$d" | tr '\n' ' ')" >> "$OUT/snapshots.log"
    fi
    rm -f "$tmp"
  done 3< <($S "condor_q -af ClusterId ProcId IWOJob JobStatus" 2>/dev/null | awk -v p="$PAT" '$3 ~ p {print $1"."$2, $3, $4}')
  sleep $(( MIN * 60 ))
done
