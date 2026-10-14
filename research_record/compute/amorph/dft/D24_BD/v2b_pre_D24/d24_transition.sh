#!/bin/bash
# D-24 transition (README_D24_BD.txt section 3a). A chain whose last finished RELAX segment ran the pre-D-24 steps has
# a relax.in written by the old rule (the last printed geometry, possibly an unvalidated trial whose SCF failed). This
# re-classifies that segment with the D-24 rules, by running the chain's own D-24 steps() on the segment's relax.out
# in a /tmp directory (pw.x is not run), and with --apply makes the chain consistent before its next segment:
#   CONTINUE  -> relax.in = the lowest-energy validated geometry if it differs (backup relax.in.pre_transition_<yyyymmddThhmmssZ>)
#   FAILED    -> the chain stays stopped: the D24-transition line in segment_stop is replaced by a STOP line with the
#                D-24 verdict ([category], reason, geomsel summary); relax_s<k>_bestvalid.in is kept if it is known;
#                relax.in is not changed (the decision is section 3's)
#   CONVERGED -> nothing to change (the DAG has moved on to FINAL)
# and then removes the install-time 'STOP <utc> D24-transition ...' line from segment_stop (other lines are kept).
# Read-only without --apply. Refuses while a RELAX job of the chain is running (its output transfer would overwrite
# relax.in). Every --apply is logged in runs/<name>/d24_transition.log.
# usage: bash ~/iwo_amorph/common/d24_transition.sh <name> [--apply]
set -u
B=${D24_BASE:-/afs/cern.ch/user/m/melrashe/iwo_amorph}
N=${1:-}; APPLY=0; [ "${2:-}" = --apply ] && APPLY=1
die() { echo "d24_transition ${N:-?}: $*" >&2; exit 1; }
[ -n "$N" ] || die "usage: d24_transition.sh <name> [--apply]"
case "$N" in aIO_0p8_s1|*/*|vac*|.*) die "not one of the 16 D-24 chains" ;; esac
D=$B/runs/$N; [ -d "$D" ] || die "no $D"
STEPS=$D/steps_relax.sh; grep -q 'geomsel\.py' "$STEPS" 2>/dev/null || STEPS=$D/steps_relax.sh.D24
grep -q 'geomsel\.py' "$STEPS" 2>/dev/null || die "no D-24 steps_relax.sh in $D"
GEO=$B/common/geomsel.py; [ -f "$GEO" ] || GEO=$B/common/geomsel.py.D24
[ -f "$GEO" ] || die "no common/geomsel.py"
utc=$(date -u +%FT%TZ); stamp=$(date -u +%Y%m%dT%H%M%SZ)

# 1. no RELAX job of the chain may be running or transferring output
busy() { condor_q -constraint "regexp(\"^${N}_relax_s[0-9]+\$\", IWOJob) && (JobStatus == 2 || JobStatus == 6 || JobStatus == 7)" -af ClusterId ProcId JobStatus; }
b=$(busy) || die "condor_q failed"
[ -z "$b" ] || die "a RELAX job of this chain is running ($b): run again after it has ended"

# 2. the newest segment tarball that holds a relax.out (a guarded or preflight stop packs none)
k=""
for t in $(ls "$D" | sed -n 's/^relax_s\([0-9][0-9]*\)_results\.tar\.gz$/\1/p' | sort -rn); do
  if tar tzf "$D/relax_s${t}_results.tar.gz" 2>/dev/null | grep -qx 'relax.out'; then k=$t; break; fi
done
[ -n "$k" ] || die "no relax_s<k>_results.tar.gz with a relax.out: nothing to re-classify"
TB=$D/relax_s${k}_results.tar.gz
tar tzf "$TB" | grep -qx "relax_s${k}_lineage.log" && die "relax_s$k already ran the D-24 steps: nothing to re-classify"
W=$(mktemp -d /tmp/d24_transition.XXXX) || die "mktemp failed"; trap 'rm -rf "$W"' EXIT
mkdir -p "$W/old" "$W/run"
tar xzf "$TB" -C "$W/old" relax.out relax.in 2>/dev/null; tar xzf "$TB" -C "$W/old" "relax_s${k}_driver.log" 2>/dev/null
[ -s "$W/old/relax.out" ] && [ -s "$W/old/relax.in" ] || die "relax.out or relax.in missing in $TB"
old=$(grep -h -o 'relax status: [A-Z]*' "$W/old/relax_s${k}_driver.log" 2>/dev/null | tail -1 | awk '{print $3}')
[ -n "$old" ] || old=$(cat "$D/RELAX_STATUS" 2>/dev/null)

# 3. the segment's input: saved by install_D24_BD.sh while the segment ran; else, after an old-rule FAILED, the
#    tarball's relax.in (the old steps changed relax.in only on CONTINUE / CONVERGED); else a template only
#    (its cards are right, its positions are the old rule's output, not the input)
if [ -s "$D/relax_s${k}_input.in" ]; then TPL=$D/relax_s${k}_input.in; exact=1; tsrc="relax_s${k}_input.in (saved at install)"
elif [ "$old" = FAILED ]; then TPL=$W/old/relax.in; exact=1; tsrc="tarball relax.in (old status FAILED: unchanged input)"
else TPL=$W/old/relax.in; exact=0; tsrc="tarball relax.in as a template only (input positions not kept by the pre-D-24 tarball)"
fi

# 4. the chain's relax.in must still be what that segment wrote
cmp -s "$D/relax.in" "$W/old/relax.in" && same=yes || same=no

# 5. D-24 classification: the chain's own steps(), pw.x replaced by the existing relax.out
cp "$TPL" "$W/run/relax.in"; cp "$W/old/relax.out" "$W/run/relax.out"; cp "$GEO" "$W/run/geomsel.py"
cp "$B/common/qeio.py" "$W/run/qeio.py"; cp "$STEPS" "$W/run/steps.sh"
( cd "$W/run" || exit 1
  JOB=relax_s$k
  python() { python3 "$@"; }
  run_pw() { return 0; }
  log() { echo "$*" >> steps.log; }
  nvidia-smi() { sleep 0; }
  source ./steps.sh
  steps ) > "$W/run/steps.stdout" 2>&1
st=$(cat "$W/run/RELAX_STATUS" 2>/dev/null)
line=$(cat "$W/run/steps.log" 2>/dev/null | grep 'relax status:' | tail -1)
sel=$(sed -n 's/^geomsel: //p' "$W/run/relax_s${k}_lineage.log" 2>/dev/null)
best=$(echo "$sel" | sed -n 's/.* best=\([^ ]*\) .*/\1/p')
rows() { awk '/^[ \t]*ATOMIC_POSITIONS/{f=1; next} f && NF >= 4 && $1 ~ /^[A-Z][a-z]?[0-9]*$/ {print $1, $2, $3, $4; next} f {f=0}' "$1" | md5sum | cut -c1-12; }
bv=""; [ -s "$W/run/relax_s${k}_bestvalid.in" ] && bv=$W/run/relax_s${k}_bestvalid.in
if [ -n "$bv" ] && [ "$best" = 0 ] && [ "$exact" = 0 ]; then bv=""; bvnote="best validated geometry = the segment input, which this tarball does not keep"; else bvnote=""; fi

echo "chain $N, segment relax_s$k ($TB)"
echo "  old rule:   ${old:-unknown}; relax.in rows $(rows "$W/old/relax.in") (chain relax.in unchanged since: $same)"
echo "  D-24 rule:  ${line#*relax status: }"
echo "  input used: $tsrc"
[ "$st" = CONTINUE ] && echo "  selected:   rows $(rows "$W/run/relax.in") (best=$best)"
[ -n "$bv" ] && echo "  bestvalid:  rows $(rows "$bv") (best=$best)"
[ -n "$bvnote" ] && echo "  bestvalid:  none written ($bvnote)"
[ -n "$st" ] || die "the D-24 steps produced no status: $(tail -3 "$W/run/steps.stdout" | tr '\n' ' ')"
if [ "$old" = CONVERGED ] && [ "$st" != CONVERGED ]; then
  echo "  WARNING: the old rule accepted this relaxation and the DAG has moved on to FINAL; D-24 says $st. Do not release FINAL before review."
fi
[ "$APPLY" = 1 ] || { echo "  (read-only; add --apply to act)"; exit 0; }

# 6. apply
[ "$same" = yes ] || die "runs/$N/relax.in differs from what relax_s$k wrote: changed by hand? Nothing applied."
b=$(busy) || die "condor_q failed"; [ -z "$b" ] || die "a RELAX job of this chain started ($b): nothing applied; run again after it ends"
act="none"
case "$st" in
  CONTINUE)
    if [ "$(rows "$W/run/relax.in")" != "$(rows "$D/relax.in")" ]; then
      cp -p "$D/relax.in" "$D/relax.in.pre_transition_$stamp" && cp "$W/run/relax.in" "$D/relax.in.D24tmp" \
        && chmod --reference="$D/relax.in" "$D/relax.in.D24tmp" && mv -f "$D/relax.in.D24tmp" "$D/relax.in" || die "relax.in update failed"
      act="relax.in = lowest-energy validated geometry (best=$best; old relax.in kept as relax.in.pre_transition_$stamp)"
    else
      act="relax.in already holds the selected geometry"
    fi ;;
  FAILED)
    [ -n "$bv" ] && { cp "$bv" "$D/relax_s${k}_bestvalid.in" || die "bestvalid copy failed"; }
    g=$(cat "$W/run/segment_guard" 2>/dev/null)
    [ -n "$g" ] || die "the D-24 steps wrote no guard line"
    printf 'STOP %s d24_transition: %s (D-24 re-classification of a pre-D-24 segment)\n' "$utc" "${g#FAILED * }" >> "$D/segment_stop" \
      || die "segment_stop write failed"
    act="chain stopped (segment_stop) with the D-24 verdict${bv:+; relax_s${k}_bestvalid.in written}" ;;
  CONVERGED) act="nothing (the DAG has moved on to FINAL)" ;;
esac
if [ -f "$D/segment_stop" ] && grep -q '^STOP [^ ]* D24-transition' "$D/segment_stop"; then
  grep -v '^STOP [^ ]* D24-transition' "$D/segment_stop" > "$D/segment_stop.D24tmp"
  removed=$(grep '^STOP [^ ]* D24-transition' "$D/segment_stop" | tr '\n' ' ')
  mv -f "$D/segment_stop.D24tmp" "$D/segment_stop" || die "segment_stop update failed"
  act="$act; removed: $removed"
fi
echo "$utc relax_s$k old=${old:-unknown} d24=${line#*relax status: } input=$tsrc action: $act" >> "$D/d24_transition.log"
echo "  applied: $act"
b=$(busy); [ -z "$b" ] || echo "  WARNING: a RELAX job of this chain started during the update ($b); check relax.in after it ends and run again"
exit 0
