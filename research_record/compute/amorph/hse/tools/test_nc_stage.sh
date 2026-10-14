#!/bin/bash
# A23 (ii)/(iii) staging tests (no submission: condor_submit_dag is shadowed by a stub that fails loudly).
# usage: bash test_nc_stage.sh   (on lxplus, after staging ~/iwo_amorph/hse)
export PYTHONDONTWRITEBYTECODE=1
A=$HOME/iwo_amorph; H=$A/hse; TOOLS=$H/tools
T=$(mktemp -d /tmp/a23nc.XXXX); trap 'rm -rf "$T"' EXIT
mkdir -p "$T/bin"; printf '#!/bin/sh\necho "STUB condor_submit_dag called: $*"; exit 97\n' > "$T/bin/condor_submit_dag"
chmod +x "$T/bin/condor_submit_dag"; export PATH="$T/bin:$PATH"
P=0; F=0
ok() { if [ "$1" = 0 ]; then P=$((P+1)); echo "  ok   $2"; else F=$((F+1)); echo "  FAIL $2"; fi; }

echo "== syntax"
for f in $TOOLS/*.sh $H/In31WO48/launch.sh $H/aIO_bulk_s1/launch.sh; do bash -n "$f"; ok $? "bash -n ${f#$H/}"; done
for f in $TOOLS/*.py; do python3 -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$f"; ok $? "python parse ${f#$H/}"; done

# synthetic converged relax.out from a relax.in: positions + small shift, 'bfgs converged', final block
synth() {  # synth <relax.in> <out> <mode: conv|noconv>
  python3 - "$1" "$2" "$3" <<'PY'
import sys
src, out, mode = sys.argv[1:]
L = open(src).read().splitlines()
i = next(n for n, l in enumerate(L) if l.startswith('ATOMIC_POSITIONS'))
unit = L[i].split()[1]
body = []
for l in L[i + 1:]:
    if not l.strip():
        break
    s, x, y, z = l.split()[:4]
    body.append(f'{s} {float(x) + (0.001 if unit == "crystal" else 0.01):.10f} {y} {z}')
blk = [f'ATOMIC_POSITIONS ({unit})'] + body + ['']
txt = ['!    total energy              =   -1000.0 Ry'] + blk + ['!    total energy              =   -1000.1 Ry']
if mode == 'conv':
    txt += ['     bfgs converged in   1 scf cycles and   1 bfgs steps', 'Begin final coordinates'] + blk + ['End final coordinates']
else:
    txt += ['     bfgs failed', 'Begin final coordinates'] + blk + ['End final coordinates']
open(out, 'w').write('\n'.join(txt + ['JOB DONE.', '']))
PY
}

for PK in In31WO48 aIO_bulk_s1; do
  echo "== package $PK"
  eval "$(grep '^export' $H/$PK/launch.sh)"
  python3 $TOOLS/make_nc.py --src "$SRC_IN" --k "$K" --nbnd "$NBND" --out $H/$PK >/dev/null; ok $? "preview inputs at the source geometry"
  python3 $TOOLS/check_nc.py --pkg $H/$PK --nel "$NEL" --k "$K" --nbnd "$NBND" --src "$SRC_IN" --preview > "$T/$PK.check" 2>&1
  ok $? "check_nc.py --preview ($(tail -1 "$T/$PK.check"))"
  W=$T/w_$PK; mkdir -p "$W/pkg" "$W/r1" "$W/r2" "$W/r3"; cp $H/$PK/nc.sub "$W/pkg/"; mkdir -p "$W/pkg/logs"
  ln -s $H/pseudo "$W/pseudo"; ln -s $H/pseudo_proj "$W/pseudo_proj"
  export PKG=$W/pkg TOOLS
  out=$(bash $H/$PK/launch.sh --dry "$W/none.out" 2>&1); [ $? = 3 ] && grep -q REFUSED <<< "$out"; ok $? "refuses a missing relax.out"
  synth "$SRC_IN" "$W/r1/relax.out" noconv
  out=$(bash $H/$PK/launch.sh --dry "$W/r1/relax.out" 2>&1); [ $? = 3 ] && grep -q "bfgs converged" <<< "$out"; ok $? "refuses without 'bfgs converged' (BFGS failure with final coordinates)"
  synth "$SRC_IN" "$W/r2/relax.out" conv; echo CONTINUE > "$W/r2/RELAX_STATUS"
  out=$(bash $H/$PK/launch.sh --dry "$W/r2/relax.out" 2>&1); [ $? = 3 ] && grep -q RELAX_STATUS <<< "$out"; ok $? "refuses when RELAX_STATUS != CONVERGED"
  synth "$SRC_IN" "$W/r3/relax.out" conv; echo CONVERGED > "$W/r3/RELAX_STATUS"
  out=$(bash $H/$PK/launch.sh --dry "$W/r3/relax.out" 2>&1); rc=$?
  [ $rc = 0 ] && grep -q "dry run" <<< "$out" && [ -s "$W/pkg/scf_pbe.in" ] && [ -s "$W/pkg/scf_hse.in" ]; ok $? "dry launch on a converged relax.out builds and checks the inputs (rc $rc)"
  [ $rc = 0 ] || echo "$out" | tail -15
  first=$(awk '/^ATOMIC_POSITIONS/{getline; print $2; exit}' "$W/pkg/scf_hse.in")
  src1=$(awk '/^ATOMIC_POSITIONS/{getline; print $2; exit}' "$SRC_IN")
  python3 -c "import sys; sys.exit(0 if abs(float('$first')-float('$src1'))>1e-4 else 1)"; ok $? "positions taken from relax.out ($src1 -> $first)"
  want=$(printf 'JOB PBE nc.sub\nVARS PBE nc_name="%s" nc_tag="pbe" nc_pools="%s"\nRETRY PBE 1 UNLESS-EXIT 2\nJOB HSE nc.sub\nVARS HSE nc_name="%s" nc_tag="hse" nc_pools="1"\nRETRY HSE 1 UNLESS-EXIT 2\nPARENT PBE CHILD HSE' "$PK" "$POOLS_PBE" "$PK")
  [ "$(cat "$W/pkg/$PK.dag")" = "$want" ]; ok $? "DAG text"
  touch "$W/pkg/$PK.dag.condor.sub"
  out=$(bash $H/$PK/launch.sh --dry "$W/r3/relax.out" 2>&1); [ $? = 3 ] && grep -q "already submitted" <<< "$out"; ok $? "refuses a second launch"
  unset PKG
done

echo "== nc_node.sh exit classification (mock driver)"
cat > "$T/driver.sh" <<'EOF'
JOB=$1
log() { :; }
run_pw() { cp "$FX_SCF" "$1.out"; }
run_pdos() { cp "$FX_PROJ" "projwfc_$2.out"; mkdir -p "tmp/$1.save"; [ -n "$FX_XML" ] && echo "<PROJECTIONS/>" > "tmp/$1.save/atomic_proj.xml"; return 0; }
python() { echo 10.0; }
checkpoint() { :; }
CKPT_EOS=/nonexistent; CLUSTER=0
source ./steps.sh
steps
tar czf "${JOB}_results.tar.gz" steps.sh
EOF
printf '!!   total energy = -1 Ry\n     convergence has been achieved in 3 iterations\nJOB DONE.\n' > "$T/scf_hse_ok"
printf '!    total energy = -1 Ry\n     convergence has been achieved in 3 iterations\nJOB DONE.\n' > "$T/scf_pbe_ok"
printf '     convergence NOT achieved after 150 iterations\nJOB DONE.\n' > "$T/scf_bad"
printf '!    total energy = -1 Ry\n     convergence has been achieved in 3 iterations\n     Maximum CPU time exceeded\nJOB DONE.\n' > "$T/scf_hse_cut"
printf 'JOB DONE.\n' > "$T/proj_ok"; : > "$T/proj_bad"; : > "$T/empty"
node() {  # node <label> <tag> <scf fixture> <proj fixture> <xml yes|""> <want rc> <want status>
  local d="$T/n_$1"; mkdir -p "$d/pseudo_proj" "$d/pseudo"; cp $TOOLS/nc_node.sh $TOOLS/steps_nc.sh "$T/driver.sh" "$d/"
  touch "$d/pseudo_proj/X_ONCV_PBE-1.2.upf"
  ( cd "$d" && FX_SCF=$3 FX_PROJ=$4 FX_XML=$5 _CONDOR_SCRATCH_DIR=$d bash ./nc_node.sh test "$2" 1000 1 > node.log 2>&1 ); local rc=$?
  local miss=""; for o in "test_$2_results.tar.gz" "scf_$2.out" "projwfc_$2.out" "atomic_proj_$2.xml" "data-file-schema_$2.xml" "STATUS_$2"; do [ -e "$d/$o" ] || miss="$miss $o"; done
  [ $rc = "$6" ] && [ "$(cat "$d/STATUS_$2")" = "$7" ] && [ -z "$miss" ]; ok $? "$1: exit $rc ($6), $(cat "$d/STATUS_$2") ($7), outputs present${miss:+, MISSING$miss}"
}
node hse_done hse "$T/scf_hse_ok"  "$T/proj_ok"  yes 0 DONE
node pbe_done pbe "$T/scf_pbe_ok"  "$T/proj_ok"  yes 0 DONE
node hse_cut  hse "$T/scf_hse_cut" "$T/proj_ok"  yes 1 FAILED
node scf_bad  hse "$T/scf_bad"     "$T/proj_ok"  yes 2 SCF_NOT_CONVERGED
node proj_bad pbe "$T/scf_pbe_ok"  "$T/proj_bad" ""  2 PROJ_FAILED
node crashed  hse "$T/empty"       "$T/proj_bad" ""  1 FAILED
echo "RESULT: $P passed, $F failed"
[ $F = 0 ]
