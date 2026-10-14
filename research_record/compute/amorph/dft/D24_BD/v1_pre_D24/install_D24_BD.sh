#!/bin/bash
# D-24 items B + D: activate the staged *.D24 files for the 16 slab chains (never runs/aIO_0p8_s1, never vac/).
# NOT run by the build agent. Review first:  bash ~/iwo_amorph/common/install_D24_BD.sh --dry-run
# Order: every step leaves the chains consistent, whatever job starts in between (README_D24_BD.txt section 1).
#   1. inert additions: common/geomsel.py, an empty segment_guard per run
#   2. idle RELAX node jobs only (condor_qedit with 'JobStatus == 1' in the constraint, so a job that started in
#      the meantime is never edited): TransferInput += geomsel.py, segment_guard; TransferOutput += segment_guard.
#      Item D, aIWO_1p0_Al2O3_s2 only: PreVerRequirements H100|H200 -> H200 first, then RequestGPUs 2 -> 1
#      (the intermediate state, 2 x H200, is itself valid).
#   3. relax.sub per run (next retry submissions)
#   4. common/relax_node.sh (guard + preflight; inert without a FAILED segment_guard)
#   5. steps_relax.sh per run
# Every replaced file keeps a <file>.pre_D24 backup; replacements are copy-to-temp + rename (atomic on AFS).
# Never condor_rm / condor_release / condor_hold here.
set -u
B=/afs/cern.ch/user/m/melrashe/iwo_amorph
cd "$B" || exit 1
DRY=0; [ "${1:-}" = --dry-run ] && DRY=1
RUNS="aIO_0p7_s1 aIO_1p0_s1 aIO_1p5_s1 aIO_2p0_s1 aIO_2p0_s2 aIWO_0p7_s1 aIWO_0p7_s1_bare aIWO_0p8_s2
      aIWO_1p0_Al2O3_s2 aIWO_1p0_s1 aIWO_1p5_s1 aIWO_2p0_Al2O3_s2 aIWO_2p0_comp_s1 aIWO_2p0_s1 aIWO_2p0_s1_bare aIWO_2p0_s2"
BENCH=aIWO_1p0_Al2O3_s2
GEO=$B/common/geomsel.py
say() { echo "[$(date -u +%FT%TZ)] $*"; }
run() { echo "+ $*"; [ "$DRY" = 1 ] && return 0; "$@" || { say "FAILED: $*"; exit 1; }; }
swap() {   # swap <staged> <target>: backup target as .pre_D24 (once), install staged atomically, keep the mode
  local new=$1 tgt=$2
  [ -e "$tgt.pre_D24" ] || run cp -p "$tgt" "$tgt.pre_D24"
  run cp "$new" "$tgt.D24tmp"
  run chmod --reference="$tgt" "$tgt.D24tmp"
  run mv -f "$tgt.D24tmp" "$tgt"
}

# 0. preconditions: everything staged, geomsel identical to the pilot's, nothing installed twice
for r in $RUNS; do
  [ "$r" = aIO_0p8_s1 ] && { say "pilot in RUNS"; exit 1; }
  for f in relax.sub.D24 steps_relax.sh.D24 relax.sub steps_relax.sh; do
    [ -s "runs/$r/$f" ] || { say "missing runs/$r/$f"; exit 1; }
  done
  grep -q 'geomsel.py' "runs/$r/steps_relax.sh" && { say "runs/$r/steps_relax.sh already D-24"; exit 1; }
done
for f in relax_node.sh.D24 geomsel.py.D24; do [ -s "common/$f" ] || { say "missing common/$f"; exit 1; }; done
[ "$(md5sum < common/geomsel.py.D24)" = "$(md5sum < runs/aIO_0p8_s1/geomsel.py)" ] || { say "geomsel.py.D24 differs from the pilot's"; exit 1; }
say "preconditions ok (dry run: $DRY)"

# 1. inert additions
if [ -e common/geomsel.py ]; then cmp -s common/geomsel.py common/geomsel.py.D24 || { say "common/geomsel.py exists and differs"; exit 1; }
else run cp -p common/geomsel.py.D24 common/geomsel.py; fi
for r in $RUNS; do [ -e "runs/$r/segment_guard" ] || run touch "runs/$r/segment_guard"; done

# 2. idle RELAX node jobs of the 16 chains
for r in $RUNS; do
  jobs=$(condor_q -constraint "regexp(\"^${r}_relax_s[0-9]+\$\", IWOJob)" -af ClusterId ProcId JobStatus) \
    || { say "condor_q failed for $r: stop (nothing after step 1 changed)"; exit 1; }
  [ -n "$jobs" ] || say "$r: no RELAX node job in the queue (between segments or DAG finished)"
  while read -r c p st; do
    [ -n "${c:-}" ] || continue
    if [ "$st" != 1 ]; then say "$r $c.$p JobStatus $st: not idle, not edited"; continue; fi
    q="ClusterId == $c && ProcId == $p && JobStatus == 1"
    tin=$(condor_q "$c.$p" -af TransferInput); tout=$(condor_q "$c.$p" -af TransferOutput)
    case "$tin" in *geomsel.py*) ;; *) run condor_qedit -constraint "$q" TransferInput "\"$tin,$GEO,segment_guard\"" ;; esac
    case "$tout" in *segment_guard*) ;; *) run condor_qedit -constraint "$q" TransferOutput "\"$tout,segment_guard\"" ;; esac
    if [ "$r" = "$BENCH" ]; then
      pv=$(condor_q "$c.$p" -af:r PreVerRequirements)
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
md5sum common/relax_node.sh common/geomsel.py runs/*/steps_relax.sh | sort | uniq -c -w32 2>/dev/null || true
grep -H 'segment_guard' runs/*/relax.sub | wc -l
