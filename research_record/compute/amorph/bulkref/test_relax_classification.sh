#!/bin/bash
# A23 (i): synthetic test of the copied relax classification (relax_node_bulk.sh + steps_relax.sh + geomsel.py + qeio.py)
# usage: bash test_relax_classification.sh <run dir> <common dir>
# Runs the real node script in a temp dir with a mock driver.sh whose run_pw writes a synthetic relax.out, then checks
# the exit code, RELAX_STATUS, the restart geometry in relax.in and that every transfer_output file exists.
RUN=${1:?run dir}; COMMON=${2:?common dir}
T=$(mktemp -d /tmp/a23cls.XXXX); trap 'rm -rf "$T"' EXIT
PASS=0; FAIL=0
cat > "$T/relax0.in" <<'EOF'
&CONTROL
  calculation = 'relax', prefix = 'rlx', outdir = './tmp', pseudo_dir = './pseudo'
/
K_POINTS automatic
  2 2 2 0 0 0

ATOMIC_POSITIONS angstrom
  In 0.00000000 0.00000000 0.00000000
  O 2.10000000 0.00000000 0.00000000

EOF
# mock driver: same interface as common/driver.sh (log, run_pw, steps.sh sourced, steps called)
cat > "$T/driver.sh" <<'EOF'
JOB=$1
log() { echo "[mock] $*" >> "${JOB}_driver.log"; }
python() { python3 "$@"; }
run_pw() { cp "$FIXTURE" "$1.out"; grep -q 'convergence NOT achieved' "$1.out" && return 1; grep -q 'JOB DONE' "$1.out"; }
source ./steps.sh
steps
tar czf "${JOB}_results.tar.gz" *.log 2>/dev/null
EOF
E() { printf '!    total energy              =   %s Ry\n' "$1"; }
G() { printf 'ATOMIC_POSITIONS (angstrom)\nIn       %s   0.000000000   0.000000000\nO        2.100000000   0.000000000   0.000000000\n\n' "$1"; }
mk() {  # mk <name> ; body from stdin
  cat > "$T/fx_$1.out"
}
# (a) converged: E0, G1+E1, G2+E2, bfgs converged, final block repeats G2
{ E -100.0; G 0.010; E -100.5; G 0.020; E -100.6; echo '     bfgs converged in   2 scf cycles and   2 bfgs steps'
  echo 'Begin final coordinates'; G 0.020; echo 'End final coordinates'; echo 'JOB DONE.'; } | mk conv
# (b) BFGS failure: QE prints final coordinates but no 'bfgs converged'; best validated = G1 (E -100.7)
{ E -100.0; G 0.030; E -100.7; G 0.040; E -100.65; echo '     The maximum number of steps has been reached.'
  echo '     bfgs failed after   2 scf cycles'; echo 'Begin final coordinates'; G 0.040; echo 'End final coordinates'
  echo 'JOB DONE.'; } | mk bfgsfail
# (c) SCF failure inside the segment
{ E -100.0; G 0.050; echo '     convergence NOT achieved after 300 iterations: stopping'; echo 'JOB DONE.'; } | mk scffail
# (d) max_seconds stop: G1 validated (E -100.4), trial G2 printed without its own energy -> restart from G1, not G2
{ E -100.0; G 0.060; E -100.4; G 0.070; echo '     Maximum CPU time exceeded'; echo 'JOB DONE.'; } | mk timeout
# (e) no new validated geometry: only the input energy, then an unevaluated trial
{ E -100.0; G 0.080; echo '     Maximum CPU time exceeded'; echo 'JOB DONE.'; } | mk nonew
# (f) pw.x crashed before any output
: | mk empty
# (g) BFGS history reset: the input geometry stays the lowest energy -> FAILED (no progress)
{ E -100.9; G 0.090; E -100.5; G 0.095; E -100.4; echo '     bfgs failed'; echo 'Begin final coordinates'; G 0.095
  echo 'End final coordinates'; echo 'JOB DONE.'; } | mk noprogress

check() {  # check <fixture> <exit> <status> <x of In in relax.in after the node>
  local d="$T/case_$1"; mkdir -p "$d"
  cp "$RUN/relax_node_bulk.sh" "$RUN/steps_relax.sh" "$RUN/geomsel.py" "$COMMON/qeio.py" "$T/driver.sh" "$d/"
  cp "$T/relax0.in" "$d/relax.in"
  ( cd "$d" && FIXTURE="$T/fx_$1.out" _CONDOR_SCRATCH_DIR="$d" bash ./relax_node_bulk.sh 3 72000 > node.log 2>&1 ); local rc=$?
  local st; st=$(cat "$d/RELAX_STATUS" 2>/dev/null)
  local x; x=$(awk '/^ATOMIC_POSITIONS/{f=1;next} f&&$1=="In"{print $2; exit}' "$d/relax.in")
  local miss=""
  for o in relax_s3_results.tar.gz relax.in RELAX_STATUS relax.out SEGMENT_SUMMARY; do [ -e "$d/$o" ] || miss="$miss $o"; done
  if [ "$rc" = "$2" ] && [ "$st" = "$3" ] && awk -v a="$x" -v b="$4" 'BEGIN{exit !(a+0==b+0)}' && [ -z "$miss" ]; then
    PASS=$((PASS+1)); echo "  ok   $1: exit $rc, $st, In x = $x, summary: $(cat "$d/SEGMENT_SUMMARY")"
  else
    FAIL=$((FAIL+1)); echo "  FAIL $1: exit $rc (want $2), status '$st' (want $3), In x = $x (want $4), missing outputs:${miss:- none}"
    sed 's/^/       /' "$d/node.log"
  fi
}
echo "== synthetic relax classification ($RUN)"
check conv       0 CONVERGED 0.020
check bfgsfail   1 CONTINUE  0.030
check scffail    2 FAILED    0.000
check timeout    1 CONTINUE  0.060
check nonew      2 FAILED    0.000
check empty      2 FAILED    0.000
check noprogress 2 FAILED    0.000
echo "RESULT: $PASS passed, $FAIL failed"
[ "$FAIL" = 0 ]
