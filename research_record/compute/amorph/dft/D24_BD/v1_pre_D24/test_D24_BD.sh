#!/bin/bash
# D-24 B+D tests on lxplus, in a /tmp directory only. Uses the STAGED files on AFS exactly as staged:
# common/relax_node.sh.D24, common/geomsel.py.D24, runs/*/steps_relax.sh.D24, common/qeio.py, common/driver.sh
# (test copy with the 60 s runaway-guard poll shortened to 1 s). pw.x is faked: 'mpirun' prints a prepared relax.out.
# usage: bash test_D24_BD.sh <upload dir with make_cases.py and fixtures/>
set -u
U=$1; B=$HOME/iwo_amorph
T=$(mktemp -d /tmp/d24bd_test.XXXX); echo "test dir $T on $(hostname)"
mkdir -p "$T/src" "$T/fakeenv/bin" "$T/real"
cp "$B/common/relax_node.sh.D24" "$T/src/relax_node.sh"
cp "$B/common/geomsel.py.D24" "$T/src/geomsel.py"
cp "$B/common/qeio.py" "$T/src/qeio.py"
cp "$B/runs/aIWO_1p0_s1/steps_relax.sh.D24" "$T/src/steps_relax.sh"
cp "$B/runs/aIWO_1p0_Al2O3_s2/steps_relax.sh.D24" "$T/src/steps_relax_bench.sh"
cp "$B/common/relax_node.sh" "$T/src/relax_node_old.sh"
cp "$B/runs/aIWO_1p0_s1/steps_relax.sh" "$T/src/steps_relax_old.sh"
sed 's/^    sleep 60$/    sleep 1/' "$B/common/driver.sh" > "$T/src/driver.sh"
echo "== test-only driver change:"; diff "$B/common/driver.sh" "$T/src/driver.sh"
cat > "$T/fakeenv/bin/mpirun" <<'EOF'
#!/bin/bash
# fake 'mpirun ... pw.x -in relax.in': prints the prepared output
[ -n "${CASE_OUT:-}" ] && [ -f "$CASE_OUT" ] && cat "$CASE_OUT"
sleep "${CASE_SLEEP:-0}"
exit 0
EOF
cat > "$T/fakeenv/bin/nvidia-smi" <<'EOF'
#!/bin/bash
echo "timestamp, index, name, memory.used [MiB], memory.total [MiB], utilization.gpu [%]"
i=0; while :; do echo "$(date '+%Y/%m/%d %H:%M:%S.000'), 0, NVIDIA H200, $((80000 + 1500 * i)) MiB, 143771 MiB, 91 %"; i=$((i + 1)); sleep 1; done
EOF
chmod +x "$T/fakeenv/bin/"*; ln -s /usr/bin/python3 "$T/fakeenv/bin/python"; ln -s /usr/bin/true "$T/fakeenv/bin/pw.x"
python3 "$U/make_cases.py" "$T/cases"

inx() { awk '/^[ \t]*ATOMIC_POSITIONS/{getline; print $2; exit}' "$1"; }   # In x of the first atom
# runcase <tag> <node script> <steps file> <seg> <relax.in> <case output or -> <guard text> [ad: new|old] [geomsel: yes|no]
runcase() {
  local tag=$1 node=$2 steps=$3 seg=$4 rin=$5 out=$6 guard=$7 ad=${8:-new} geo=${9:-yes}
  local d=$T/run_$tag; rm -rf "$d"; mkdir -p "$d"
  cp "$T/src/driver.sh" "$T/src/qeio.py" "$d/"; cp "$rin" "$d/relax.in"; cp "$steps" "$d/steps_relax.sh"
  [ "$geo" = yes ] && cp "$T/src/geomsel.py" "$d/"
  local tout="relax_s${seg}_results.tar.gz,relax.in,RELAX_STATUS"
  if [ "$ad" = new ]; then printf '%s' "$guard" > "$d/segment_guard"; tout="$tout,segment_guard"; fi
  printf 'ClusterId = 990%s\nProcId = 0\nRequestCpus = 1\nTransferOutput = "%s"\n' "$seg" "$tout" > "$d/.job.ad"
  local t0 t1 rc
  t0=$(date +%s%N)
  ( cd "$d" && env _CONDOR_SCRATCH_DIR="$d" _CONDOR_JOB_AD="$d/.job.ad" QE_LOCAL="$T/fakeenv" NCPU_OVERRIDE=1 \
      CASE_OUT="$([ "$out" = - ] || echo "$out")" CASE_SLEEP="${CASE_SLEEP:-0}" bash "$node" "$seg" 72000 > node.stdout 2>&1 < /dev/null )
  rc=$?; t1=$(date +%s%N)
  local miss=""; for f in $(echo "$tout" | tr ',' ' '); do [ -e "$d/$f" ] || miss="$miss $f"; done
  R_RC=$rc; R_ST=$(cat "$d/RELAX_STATUS" 2>/dev/null); R_X=$(inx "$d/relax.in"); R_G=$(head -c 160 "$d/segment_guard" 2>/dev/null)
  echo "--- $tag: exit $rc, $(( (t1 - t0) / 1000000 )) ms, RELAX_STATUS $R_ST, relax.in In x $R_X, missing outputs:${miss:- none}"
  echo "    guard: ${R_G:-<empty or absent>}"
  echo "    node stdout: $(tail -1 "$d/node.stdout")"
  echo "    tarball: $(tar tzf "$d/relax_s${seg}_results.tar.gz" 2>/dev/null | sort | tr '\n' ' ')"
  [ -f "$d/relax_s${seg}_lineage.log" ] && sed 's/^/    lineage: /' "$d/relax_s${seg}_lineage.log"
  grep -h 'relax status' "$d/relax_s${seg}_driver.log" 2>/dev/null | sed 's/^/    driver log: /' | cut -c1-260
}
PASS=0; FAIL=0
check() {   # check <label> <condition text> <0|1>
  if [ "$3" = 0 ]; then PASS=$((PASS + 1)); echo "    PASS $1"; else FAIL=$((FAIL + 1)); echo "    FAIL $1: $2"; fi
}

echo; echo "===== A. synthetic QE-format cases through the full node path (new relax_node.sh + driver.sh + steps + geomsel)"
while read -r name st x guard; do
  out=$T/cases/$name.out; [ -f "$out" ] || out=-
  runcase "$name" "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 3 "$T/cases/relax.in" "$out" ""
  g=empty; [ -n "$R_G" ] && g=armed
  erc=1; [ "$st" = CONVERGED ] && erc=0
  [ "$R_ST" = "$st" ] && [ "$R_X" = "$x" ] && [ "$g" = "$guard" ] && [ "$R_RC" = "$erc" ]
  check "$name" "want $st x=$x guard=$guard exit=$erc" $?
done < "$T/cases/expected.txt"
bx=$(inx "$T/run_T3_scf_not_achieved_after_steps/relax_s3_bestvalid.in" 2>/dev/null)
[ "$bx" = 5.0100000000 ]; check "T3 keeps the best validated geometry (g1) as relax_s3_bestvalid.in" "got $bx" $?

echo; echo "===== B. guard chain: the FAILED segment of T3 is followed by retry s4 (a case that would converge)"
d3=$T/run_T3_scf_not_achieved_after_steps
cp "$d3/relax.in" "$T/ap_relax.in"   # what the access point holds after T3's output transfer
runcase guard_s4 "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 4 "$T/ap_relax.in" "$T/cases/T1_bfgs_converged.out" "$(cat "$d3/segment_guard")"
d=$T/run_guard_s4
[ "$R_RC" = 1 ] && [ "$R_ST" = FAILED ] && [ ! -e "$d/relax.out" ] && ! grep -q 'job relax_s4 host' "$d/relax_s4_driver.log" \
  && cmp -s "$d/relax.in" "$T/ap_relax.in" && [ "$(cat "$d/segment_guard")" = "$(cat "$d3/segment_guard")" ]
check "guard stops s4 before driver.sh (no pw.x, relax.in and guard unchanged, all outputs present)" "see above" $?
echo "    elapsed check: node stdout = $(cat "$d/node.stdout")"

echo; echo "===== C. inertness and preflight"
runcase I1_old_ad_old_steps "$T/src/relax_node.sh" "$T/src/steps_relax_old.sh" 3 "$T/cases/relax.in" "$T/cases/T4_timelimit_midscf_with_steps.out" "" old yes
[ "$R_RC" = 1 ] && [ "$R_ST" = CONTINUE ] && [ "$R_X" = 5.0300000000 ]
check "I1 new node + pre-D-24 steps + no segment_guard: old behaviour unchanged (CONTINUE from last printed g3)" "got $R_ST $R_X" $?
runcase I1ref_old_node "$T/src/relax_node_old.sh" "$T/src/steps_relax_old.sh" 3 "$T/cases/relax.in" "$T/cases/T4_timelimit_midscf_with_steps.out" "" old yes
[ "$R_ST" = CONTINUE ] && [ "$R_X" = 5.0300000000 ]; check "I1ref old node gives the same (reference)" "got $R_ST $R_X" $?
runcase I2_preflight_old_ad "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 3 "$T/cases/relax.in" "$T/cases/T1_bfgs_converged.out" "" old no
[ "$R_RC" = 1 ] && [ "$R_ST" = FAILED ] && [ ! -e "$T/run_I2_preflight_old_ad/relax.out" ] && [ ! -e "$T/run_I2_preflight_old_ad/segment_guard" ] && [ "$R_X" = 5.0000000000 ]
check "I2 preflight: new steps without geomsel.py stop in seconds, no guard written, relax.in kept" "got $R_ST" $?
runcase I3_guard_cleared_comment "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 3 "$T/cases/relax.in" "$T/cases/T4_timelimit_midscf_with_steps.out" "# cleared 2026-10-11 by user (was FAILED ...)"
[ "$R_ST" = CONTINUE ] && [ "$R_X" = 5.0100000000 ]; check "I3 a guard without a leading FAILED line is inert" "got $R_ST" $?

echo; echo "===== D. benchmark steps (aIWO_1p0_Al2O3_s2 variant): GPU-memory sampler (fake nvidia-smi, 1 s)"
CASE_SLEEP=4 runcase bench "$T/src/relax_node.sh" "$T/src/steps_relax_bench.sh" 0 "$T/cases/relax.in" "$T/cases/T4_timelimit_midscf_with_steps.out" ""
grep -h 'gpumem' "$T/run_bench/relax_s0_driver.log" | sed 's/^/    /'
n=$(tar xzf "$T/run_bench/relax_s0_results.tar.gz" -O gpumem.log 2>/dev/null | wc -l); sleep 2
left=$(pgrep -u "$USER" -f "$T/fakeenv/bin/nvidia-smi" | wc -l)
[ "$R_ST" = CONTINUE ] && [ "$n" -ge 3 ] && [ "$left" = 0 ]; check "bench: CONTINUE, gpumem.log packed ($n lines), sampler stopped ($left left)" "" $?

echo; echo "===== E. real QE outputs"
tar xzf "$B/runs/aIO_2p0_s1/relax_s0_results.tar.gz" -C "$T/real" relax.out relax.in relax_s0_driver.log && \
  mv "$T/real/relax.out" "$T/real/aIO_2p0_s1_s0.out" && mv "$T/real/relax.in" "$T/real/aIO_2p0_s1_s0.in" && mv "$T/real/relax_s0_driver.log" "$T/real/aIO_2p0_s1_s0_driver.log"
mkdir -p "$T/real/x" && tar xzf "$B/runs/aIO_0p7_s1/relax_s0_results.tar.gz" -C "$T/real/x" && \
  mv "$T/real/x/relax.out" "$T/real/aIO_0p7_s1_s0.out" && mv "$T/real/x/relax.in" "$T/real/aIO_0p7_s1_s0.in"
F=$U/fixtures
runcase R1_canary_converged "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 1 "$F/canary_race.in" "$F/canary_race.out" ""
python3 "$T/src/qeio.py" newgeom "$F/canary_race.in" "$F/canary_race.out" > "$T/r1_expect.in"
[ "$R_RC" = 0 ] && [ "$R_ST" = CONVERGED ] && cmp -s <(sed -n '/ATOMIC_POSITIONS/,$p' "$T/r1_expect.in") <(sed -n '/ATOMIC_POSITIONS/,$p' "$T/run_R1_canary_converged/relax.in")
check "R1 real QE 7.x relax, bfgs converged (2 atoms): CONVERGED, final coordinates" "got $R_ST" $?
runcase R2_slab176_converged "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 1 "$F/slab2.in" "$F/slab2.out" ""
[ "$R_RC" = 0 ] && [ "$R_ST" = CONVERGED ]; check "R2 real QE 7.3.1 GPU relax, 176 atoms, bfgs converged: CONVERGED" "got $R_ST" $?
# R3: the same real output cut 40 lines after its 10th '!' energy, then the time-limit message
L=$(grep -n '^!' "$F/slab2.out" | sed -n 10p | cut -d: -f1)
{ head -n $((L + 40)) "$F/slab2.out"; printf '\n     Maximum CPU time exceeded\n\n     max_seconds     =   70184.00\n'; } > "$T/r3.out"
want=$(python3 - "$T/r3.out" <<'PY'
import sys
L = open(sys.argv[1]).read().splitlines(); g = -1; E = {}; blocks = {}
for i, l in enumerate(L):
    if l.startswith('!'): E[max(g, 0)] = float(l.split('=')[1].split()[0])
    if l.strip().startswith('ATOMIC_POSITIONS') and 'Begin final' not in '\n'.join(L[max(0, i-3):i]):
        g = max(g, 0) + 1; blocks[g] = L[i + 1].split()
b = min(E, key=E.get); print(b, len(E), blocks[b][1] if b > 0 else 'input')
PY
)
runcase R3_slab176_timelimit "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 1 "$F/slab2.in" "$T/r3.out" ""
echo "    independent parse (best geometry, validated count, first x): $want"
[ "$R_ST" = CONTINUE ] && [ "$R_X" = "$(echo "$want" | awk '{print $3}')" ]; check "R3 real output cut by the time limit after 10 validated geometries: CONTINUE from the lowest-energy one" "got $R_ST $R_X" $?
runcase R4_aIO_2p0_s1_s0 "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 0 "$T/real/aIO_2p0_s1_s0.in" "$T/real/aIO_2p0_s1_s0.out" ""
[ "$R_RC" = 1 ] && [ "$R_ST" = FAILED ] && [ -n "$R_G" ]; check "R4 real aIO_2p0_s1 s0 (268 atoms, first SCF not converged): FAILED + guard" "got $R_ST" $?
echo "    aIO_2p0_s1 s0: $(grep -c 'iteration #' "$T/real/aIO_2p0_s1_s0.out") SCF iterations; $(grep -h 'pw.x relax' "$T/real/aIO_2p0_s1_s0_driver.log" | tr '\n' ' ' | cut -c1-220)"
echo "    aIO_0p7_s1 s0 (real; old logic CONTINUEd from the last printed geometry), new geomsel:"
( cd "$T/real" && cp "$T/src/geomsel.py" "$T/src/qeio.py" . && python3 geomsel.py aIO_0p7_s1_s0.in aIO_0p7_s1_s0.out; \
  echo "    'convergence NOT achieved' count: $(grep -c 'convergence NOT achieved' aIO_0p7_s1_s0.out); bfgs converged: $(grep -c 'bfgs converged' aIO_0p7_s1_s0.out)" ) | sed 's/^/    /'

echo; echo "===== F. install script: syntax, and the PreVerRequirements substitution on the live benchmark ad (read-only)"
bash -n "$B/common/install_D24_BD.sh" && echo "    install_D24_BD.sh syntax ok"
pv=$(condor_q 12884198 -af:r PreVerRequirements)
nv=${pv/regexp(\"H100|H200\",TARGET.GPUs_DeviceName)/regexp(\"H200\",TARGET.GPUs_DeviceName)}
echo "    now:   $pv"; echo "    after: $nv"
[ "$nv" != "$pv" ] && [ "${nv//H100/}" = "$nv" ]; check "PreVerRequirements edit replaces only the device clause" "" $?
echo; echo "===== RESULT: $PASS passed, $FAIL failed (test dir $T)"
