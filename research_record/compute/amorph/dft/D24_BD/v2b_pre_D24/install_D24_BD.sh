#!/bin/bash
# D-24 items B + D (staging v2): activate the staged files for the 16 slab chains (never runs/aIO_0p8_s1, never vac/).
# NOT run by the build agent. Review first:  bash ~/iwo_amorph/common/install_D24_BD.sh --dry-run
# Order: every step leaves the chains consistent, whatever job starts in between (README_D24_BD.txt section 1).
#   0. preconditions (read-only): the staged files are the tested ones (common/D24_BD_staged.md5); the live files are
#      the ones the staged files were derived from (common/D24_BD_baseline.md5: relax.sub and steps_relax.sh of the
#      16 runs, common/relax_node.sh, driver.sh, qeio.py); geomsel identical to the pilot's; nothing installed yet
#   1. inert additions: common/geomsel.py; an empty segment_guard and segment_stop per run; a transition stop
#      ('STOP <utc> D24-transition ...' in segment_stop) for each chain whose RELAX job is running now (it runs the
#      pre-D-24 steps) or that already has a segment tarball (its relax.in was written by the pre-D-24 rule); the
#      input of a running segment is kept as runs/<name>/relax_s<k>_input.in for common/d24_transition.sh
#   2. idle RELAX node jobs only (condor_qedit with 'JobStatus == 1' in the constraint, so a job that started in
#      the meantime is never edited): TransferInput += geomsel.py, segment_guard, segment_stop; TransferOutput +=
#      segment_guard. Item D, aIWO_1p0_Al2O3_s2 only: PreVerRequirements H100|H200 -> H200 first, then
#      RequestGPUs 2 -> 1 (the intermediate state, 2 x H200, is itself valid)
#   3. relax.sub per run (next retry submissions)
#   4. common/relax_node.sh (stop files + preflight; inert without a STOP / FAILED line)
#   5. steps_relax.sh per run
# Every replaced file keeps a <file>.pre_D24 backup; replacements are copy-to-temp + rename (atomic on AFS).
# Never condor_rm / condor_release / condor_hold here. D24_BASE overrides the tree (tests in /tmp only).
set -u
B=${D24_BASE:-/afs/cern.ch/user/m/melrashe/iwo_amorph}
cd "$B" || exit 1
DRY=0; [ "${1:-}" = --dry-run ] && DRY=1
RUNS="aIO_0p7_s1 aIO_1p0_s1 aIO_1p5_s1 aIO_2p0_s1 aIO_2p0_s2 aIWO_0p7_s1 aIWO_0p7_s1_bare aIWO_0p8_s2
      aIWO_1p0_Al2O3_s2 aIWO_1p0_s1 aIWO_1p5_s1 aIWO_2p0_Al2O3_s2 aIWO_2p0_comp_s1 aIWO_2p0_s1 aIWO_2p0_s1_bare aIWO_2p0_s2"
BENCH=aIWO_1p0_Al2O3_s2
GEO=$B/common/geomsel.py
say() { echo "[$(date -u +%FT%TZ)] $*"; }
run() { echo "+ $*"; [ "$DRY" = 1 ] && return 0; "$@" || { say "FAILED: $*"; exit 1; }; }
addline() {   # addline <file> <text>: append one line
  echo "+ append to $1: $2"; [ "$DRY" = 1 ] && return 0
  printf '%s\n' "$2" >> "$1" || { say "FAILED: append to $1"; exit 1; }
}
swap() {   # swap <staged> <target>: backup target as .pre_D24 (once), install staged atomically, keep the mode
  local new=$1 tgt=$2
  [ -e "$tgt.pre_D24" ] || run cp -p "$tgt" "$tgt.pre_D24"
  run cp "$new" "$tgt.D24tmp"
  run chmod --reference="$tgt" "$tgt.D24tmp"
  run mv -f "$tgt.D24tmp" "$tgt"
}
has() { echo ",$1," | tr -d ' ' | grep -q -F ",$2,"; }   # has <comma list> <item>
relax_jobs() {   # relax_jobs <run>: ClusterId ProcId JobStatus IWOJob JobCurrentStartDate of the chain's RELAX node jobs
  condor_q -constraint "regexp(\"^${1}_relax_s[0-9]+\$\", IWOJob)" -af ClusterId ProcId JobStatus IWOJob JobCurrentStartDate
}

# 0. preconditions
for f in common/D24_BD_staged.md5 common/D24_BD_baseline.md5 common/relax_node.sh.D24 common/geomsel.py.D24 \
         common/d24_transition.sh "runs/$BENCH/relax.sub.D24_2gpu"; do
  [ -s "$f" ] || { say "missing $f"; exit 1; }
done
md5sum -c --quiet common/D24_BD_staged.md5 || { say "staged files changed since staging/testing: re-stage and re-test"; exit 1; }
md5sum -c --quiet common/D24_BD_baseline.md5 || { say "live files changed since staging: re-stage and re-test"; exit 1; }
for r in $RUNS; do
  [ "$r" = aIO_0p8_s1 ] && { say "pilot in RUNS"; exit 1; }
  for f in relax.sub.D24 steps_relax.sh.D24 relax.sub steps_relax.sh relax.in; do
    [ -s "runs/$r/$f" ] || { say "missing runs/$r/$f"; exit 1; }
  done
  grep -q 'geomsel.py' "runs/$r/steps_relax.sh" && { say "runs/$r/steps_relax.sh already D-24"; exit 1; }
  grep -q "^runs/$r/relax.sub\$" <(awk '{print $2}' common/D24_BD_baseline.md5) || { say "runs/$r/relax.sub not in the baseline"; exit 1; }
done
[ "$(md5sum < common/geomsel.py.D24)" = "$(md5sum < runs/aIO_0p8_s1/geomsel.py)" ] || { say "geomsel.py.D24 differs from the pilot's"; exit 1; }
say "preconditions ok (dry run: $DRY)"

# 1. inert additions and transition stops
if [ -e common/geomsel.py ]; then cmp -s common/geomsel.py common/geomsel.py.D24 || { say "common/geomsel.py exists and differs"; exit 1; }
else run cp -p common/geomsel.py.D24 common/geomsel.py; fi
now=$(date -u +%FT%TZ)
for r in $RUNS; do
  d=runs/$r
  [ -e "$d/segment_guard" ] || run touch "$d/segment_guard"
  [ -e "$d/segment_stop" ] || run touch "$d/segment_stop"
  jobs=$(relax_jobs "$r") || { say "condor_q failed for $r: stop (only inert files changed so far)"; exit 1; }
  k=""; why=""
  while read -r c p st iwo t0; do
    [ -n "${c:-}" ] || continue
    case "$st" in
      2|6|7)
        k=${iwo##*_relax_s}; why="relax_s$k (job $c.$p) is running the pre-D-24 steps"
        if [ -e "$d/relax_s${k}_input.in" ]; then :
        elif [ "$t0" != undefined ] && [ "$(stat -c %Y "$d/relax.in")" -lt "$t0" ]; then
          run cp -p "$d/relax.in" "$d/relax_s${k}_input.in"
        else
          say "$r: relax.in changed after job $c.$p started: its input is not kept (d24_transition.sh then uses a template)"
        fi ;;
    esac
  done <<< "$jobs"
  if [ -z "$k" ]; then
    k=$(ls "$d" | sed -n 's/^relax_s\([0-9][0-9]*\)_results\.tar\.gz$/\1/p' | sort -rn | head -1)
    [ -n "$k" ] && why="relax_s$k ended with the pre-D-24 steps (relax.in written by the pre-D-24 rule)"
  fi
  if [ -n "$why" ]; then
    if grep -q '^STOP [^ ]* D24-transition' "$d/segment_stop" 2>/dev/null; then say "$r: transition stop already armed"
    else addline "$d/segment_stop" "STOP $now D24-transition: $why; when no RELAX job of this chain runs: bash ~/iwo_amorph/common/d24_transition.sh $r [--apply] (README_D24_BD.txt section 3a)"
    fi
  fi
done

# 2. idle RELAX node jobs of the 16 chains
for r in $RUNS; do
  jobs=$(relax_jobs "$r") || { say "condor_q failed for $r: stop (nothing after step 1 changed)"; exit 1; }
  [ -n "$jobs" ] || say "$r: no RELAX node job in the queue (between segments or DAG finished)"
  while read -r c p st iwo t0; do
    [ -n "${c:-}" ] || continue
    if [ "$st" != 1 ]; then say "$r $c.$p JobStatus $st: not idle, not edited"; continue; fi
    q="ClusterId == $c && ProcId == $p && JobStatus == 1"
    tin=$(condor_q "$c.$p" -af TransferInput) && tout=$(condor_q "$c.$p" -af TransferOutput) \
      || { say "$r $c.$p: condor_q failed: stop"; exit 1; }
    has "$tin" relax.in && has "$tin" steps_relax.sh && has "$tout" RELAX_STATUS \
      || { say "$r $c.$p: unexpected TransferInput '$tin' / TransferOutput '$tout': stop"; exit 1; }
    nin=$tin
    for a in "$GEO" segment_guard segment_stop; do has "$nin" "$a" || nin="$nin,$a"; done
    [ "$nin" = "$tin" ] || run condor_qedit -constraint "$q" TransferInput "\"$nin\""
    has "$tout" segment_guard || run condor_qedit -constraint "$q" TransferOutput "\"$tout,segment_guard\""
    if [ "$r" = "$BENCH" ]; then
      pv=$(condor_q "$c.$p" -af:r PreVerRequirements) || { say "condor_q failed"; exit 1; }
      nv=${pv/regexp(\"H100|H200\",TARGET.GPUs_DeviceName)/regexp(\"H200\",TARGET.GPUs_DeviceName)}
      if [ "$nv" = "$pv" ]; then say "$r: H100|H200 clause not found in PreVerRequirements: $pv"; exit 1; fi
      run condor_qedit -constraint "$q" PreVerRequirements "$nv"
      run condor_qedit -constraint "$q" RequestGPUs 1
    fi
    [ "$DRY" = 1 ] || condor_q "$c.$p" -af:lr JobStatus RequestGPUs TransferInput TransferOutput PreVerRequirements
  done <<< "$jobs"
done

# 3-5. files (each change is inert until a job starts with it)
for r in $RUNS; do swap "runs/$r/relax.sub.D24" "runs/$r/relax.sub"; done
swap common/relax_node.sh.D24 common/relax_node.sh
for r in $RUNS; do swap "runs/$r/steps_relax.sh.D24" "runs/$r/steps_relax.sh"; done

say "installed (dry run: $DRY). Check:"
md5sum common/relax_node.sh common/geomsel.py runs/*/steps_relax.sh 2>/dev/null | awk '{print $1}' | sort | uniq -c
echo "relax.sub with segment_stop: $(grep -l 'segment_stop' runs/*/relax.sub 2>/dev/null | wc -l)"
grep -H '^STOP' runs/*/segment_stop 2>/dev/null | cut -c1-220
