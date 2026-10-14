#!/bin/bash
# A23 (ii)/(iii) shared launcher, called by hse/<name>/launch.sh, which sets
#   NAME SRC_IN RELAX_OUT_DEFAULT K NBND NEL NV POOLS_PBE
# usage (through the package): bash launch.sh [--dry] [<converged relax.out>]
#   1. refuses unless relax.out has 'bfgs converged' and 'End final coordinates' (and a RELAX_STATUS next to it, if
#      present, says CONVERGED); refuses if this package's DAG was already submitted
#   2. copies relax.out to relax_source.out; builds scf_pbe.in / scf_hse.in (make_nc.py) and checks them (check_nc.py)
#   3. writes <name>.dag (PBE, then HSE; RETRY 1 UNLESS-EXIT 2) and LAUNCH_RECORD
#   4. condor_submit_dag (not with --dry)
set -euo pipefail
: "${NAME:?}" "${SRC_IN:?}" "${RELAX_OUT_DEFAULT:?}" "${K:?}" "${NBND:?}" "${NEL:?}" "${NV:?}" "${POOLS_PBE:?}"
DRY=0
if [ "${1:-}" = --dry ]; then DRY=1; shift; fi
RELAX_OUT=${1:-$RELAX_OUT_DEFAULT}
PKG=${PKG:-$HOME/iwo_amorph/hse/$NAME}
TOOLS=${TOOLS:-$HOME/iwo_amorph/hse/tools}
cd "$PKG"
refuse() { echo "REFUSED: $*"; exit 3; }
[ ! -e "$NAME.dag.condor.sub" ] || refuse "$NAME.dag was already submitted from $PKG (see $NAME.dag.dagman.out)"
[ -s "$RELAX_OUT" ] || refuse "$RELAX_OUT missing or empty"
grep -q 'bfgs converged' "$RELAX_OUT" || refuse "no 'bfgs converged' in $RELAX_OUT (A23 needs the converged geometry)"
grep -q 'End final coordinates' "$RELAX_OUT" || refuse "no 'End final coordinates' in $RELAX_OUT"
ST=$(dirname "$RELAX_OUT")/RELAX_STATUS
if [ -f "$ST" ] && [ "$(cat "$ST")" != CONVERGED ]; then refuse "$ST says $(cat "$ST")"; fi
cp -f "$RELAX_OUT" relax_source.out
python3 "$TOOLS/make_nc.py" --src "$SRC_IN" --relax-out relax_source.out --k "$K" --nbnd "$NBND" --out "$PKG"
python3 "$TOOLS/check_nc.py" --pkg "$PKG" --nel "$NEL" --k "$K" --nbnd "$NBND" --src "$SRC_IN" \
  || refuse "check_nc.py failed (inputs left in $PKG for inspection, nothing submitted)"
cat > "$NAME.dag" <<EOF
JOB PBE nc.sub
VARS PBE nc_name="$NAME" nc_tag="pbe" nc_pools="$POOLS_PBE"
RETRY PBE 1 UNLESS-EXIT 2
JOB HSE nc.sub
VARS HSE nc_name="$NAME" nc_tag="hse" nc_pools="1"
RETRY HSE 1 UNLESS-EXIT 2
PARENT PBE CHILD HSE
EOF
mkdir -p logs
{ echo "launch $(date -u +%FT%TZ) dry=$DRY host=$(hostname)"
  echo "relax.out: $RELAX_OUT md5 $(md5sum < "$RELAX_OUT" | cut -c1-32)"
  echo "N_el(NC) $NEL, N_v $NV, k $K, nbnd $NBND, PBE pools $POOLS_PBE"
  md5sum scf_pbe.in scf_hse.in "$NAME.dag" nc.sub; } >> LAUNCH_RECORD
if [ "$DRY" = 1 ]; then echo "dry run: scf_pbe.in, scf_hse.in and $NAME.dag written; nothing submitted"; exit 0; fi
condor_submit_dag -batch-name "a23_$NAME" "$NAME.dag"
