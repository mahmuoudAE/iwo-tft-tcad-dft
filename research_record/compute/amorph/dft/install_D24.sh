#!/bin/bash
# D-24 install (lxplus), staging v2 (2026-10-11). NOT RUN by the build agent: run only after the user's go, and before
# any FINAL condor_release.
#   bash ~/iwo_amorph/install_D24.sh [--apply] [extra run names...]
#     without --apply: dry run, prints what would change; --apply installs, with *.pre_D24 backups.
#     Extra run names (e.g. aIO_bulk_s1 aIWO_bulk_s1, created after staging) get common/steps_final.sh.D24 and the
#     verbosity change too. The A15 pilot aIO_0p8_s1 is processed only when named here (main session's decision).
# Changes: common/steps_final.sh and runs/<16 dirs>/steps_final.sh <- their staged *.D24 copy (only if the live file
# still has the pre-D24 sha256), final.tmpl: verbosity 'low' -> 'high' (one line, applied to the live file, diff checked),
# common/final_node.sh <- common/final_node.sh.D24 (only if the live file has the pre-D24 sha256; it keeps the old exit
# rule for a steps_final.sh without export_final, i.e. the pilot until it is given the D-24 steps), and the new
# common/lineage_relax.sh and common/export_pull.sh from their .D24 files. Nothing else (no final.sub, no queue action).
# Refuses while any FINAL job (IWOJob *_final except val_*) is running, and when condor_q cannot be read.
# Rollback: README_D24_C.txt section 4.
set -uo pipefail
cd "${IWO_ROOT:-$HOME/iwo_amorph}" || exit 1
APPLY=0; [ "${1:-}" = --apply ] && { APPLY=1; shift; }
EXTRA="$*"
PRE_STEPS=38a423a41d3fedc627b7b64f3801919ee75bf621aebc1baf0593d4cb0f239bcd   # steps_final.sh as of 2026-10-11 (common = runs)
PRE_NODE=fb4012a81e62a5cb01734e6a3b0a11da1a2d023af24c50d563d56f17d4721ad1    # common/final_node.sh as of 2026-10-11
RUNS="aIO_0p7_s1 aIO_1p0_s1 aIO_1p5_s1 aIO_2p0_s1 aIO_2p0_s2 aIWO_0p7_s1 aIWO_0p7_s1_bare aIWO_0p8_s2 aIWO_1p0_Al2O3_s2
      aIWO_1p0_s1 aIWO_1p5_s1 aIWO_2p0_Al2O3_s2 aIWO_2p0_comp_s1 aIWO_2p0_s1 aIWO_2p0_s1_bare aIWO_2p0_s2"
q=$(condor_q -af IWOJob JobStatus 2>&1) || { echo "condor_q failed, nothing installed: $(head -c 300 <<< "$q")"; exit 3; }
running=$(awk '$1 ~ /_final$/ && $1 !~ /^val_/ && $2 == 2' <<< "$q")
[ -n "$running" ] && { echo "FINAL job(s) running, nothing installed:"; echo "$running"; exit 2; }
do_() { if [ $APPLY = 1 ]; then "$@"; else echo "would: $*"; fi; }
err=0
put_steps() {   # put_steps <live steps_final.sh>: installs the staged <live>.D24 (must equal common/steps_final.sh.D24)
  local live=$1 new=$1.D24 h
  [ -f "$new" ] || new=common/steps_final.sh.D24   # run directories created after staging
  cmp -s "$new" common/steps_final.sh.D24 || { echo "$new differs from common/steps_final.sh.D24, skipped"; err=1; return; }
  h=$(sha256sum "$live" | cut -c1-64)
  if [ "$h" = "$(sha256sum "$new" | cut -c1-64)" ]; then echo "$live: already D-24"; return; fi
  if [ "$h" != "$PRE_STEPS" ]; then echo "$live: UNEXPECTED sha256 $h (changed since staging), skipped"; err=1; return; fi
  [ -e "$live.pre_D24" ] || do_ cp -p "$live" "$live.pre_D24"
  do_ cp "$new" "$live"
}
put_tmpl() {    # put_tmpl <live final.tmpl>
  local t=$1 n
  n=$(grep -c "verbosity = 'low'" "$t")
  if [ "$n" = 0 ] && grep -q "verbosity = 'high'" "$t"; then echo "$t: already verbosity high"; return; fi
  [ "$n" = 1 ] || { echo "$t: $n 'verbosity = low' lines (expected 1), skipped"; err=1; return; }
  [ -e "$t.pre_D24" ] || do_ cp -p "$t" "$t.pre_D24"
  do_ sed -i "s/verbosity = 'low'/verbosity = 'high'/" "$t"
  if [ $APPLY = 1 ]; then
    n=$(diff "$t.pre_D24" "$t" | grep -c '^[<>]')
    [ "$n" = 2 ] || { echo "$t: diff has $n changed lines (expected 2), restoring"; cp -p "$t.pre_D24" "$t"; err=1; return; }
    [ -f "$t.D24" ] && ! cmp -s "$t" "$t.D24" && echo "$t: note, the live template changed after staging (e.g. A15 degauss); verbosity set on the live version"
  fi
}
put_node() {    # common/final_node.sh <- common/final_node.sh.D24
  local live=common/final_node.sh new=common/final_node.sh.D24 h
  [ -f "$new" ] || { echo "$new missing"; err=1; return; }
  h=$(sha256sum "$live" | cut -c1-64)
  if [ "$h" = "$(sha256sum "$new" | cut -c1-64)" ]; then echo "$live: already D-24"; return; fi
  if [ "$h" != "$PRE_NODE" ]; then echo "$live: UNEXPECTED sha256 $h (changed since staging), skipped"; err=1; return; fi
  [ -e "$live.pre_D24" ] || do_ cp -p "$live" "$live.pre_D24"
  do_ cp "$new" "$live.tmp_D24"; do_ chmod +x "$live.tmp_D24"; do_ mv -f "$live.tmp_D24" "$live"   # rename: atomic on AFS
}
for f in steps_final.sh.D24 final_node.sh.D24 lineage_relax.sh.D24 export_pull.sh.D24; do
  [ -f common/$f ] || { echo "common/$f missing, nothing installed"; exit 1; }
done
put_steps common/steps_final.sh
for r in $RUNS $EXTRA; do
  [ -d "runs/$r" ] || { echo "runs/$r missing"; err=1; continue; }
  put_steps "runs/$r/steps_final.sh"; put_tmpl "runs/$r/final.tmpl"
done
put_node
for f in lineage_relax.sh export_pull.sh; do
  if [ -e "common/$f" ]; then
    cmp -s "common/$f" "common/$f.D24" && { echo "common/$f: already D-24"; continue; }
    echo "common/$f exists and differs from common/$f.D24, left alone"; err=1; continue
  fi
  do_ cp common/$f.D24 common/$f; do_ chmod +x common/$f
done
echo "done (apply=$APPLY, errors=$err, extra runs: ${EXTRA:-none})."
exit $err
