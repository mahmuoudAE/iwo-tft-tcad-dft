#!/bin/bash
# D-24 B+D tests (staging v2c) on lxplus, in a /tmp directory only. Uses the STAGED files on AFS exactly as staged:
# common/relax_node.sh.D24, common/geomsel.py.D24, common/d24_transition.sh, common/install_D24_BD.sh,
# runs/*/steps_relax.sh.D24, runs/*/relax.sub.D24(_2gpu), common/qeio.py, common/driver.sh (test copy with the 60 s
# runaway-guard poll shortened to 1 s). pw.x is faked: 'mpirun' prints a prepared relax.out. The install and the
# transition tool run against /tmp copies of the tree (D24_BASE) with a fake condor_q built from the live queue
# (read-only) and a logging condor_qedit; nothing on AFS and no job is changed.
# usage: bash test_D24_BD.sh <upload dir with make_cases.py and fixtures/>
set -u
U=$1; B=${D24_TREE:-$HOME/iwo_amorph}   # D24_TREE: a /tmp mirror of the tree (pre-test before staging)
RUNS="aIO_0p7_s1 aIO_1p0_s1 aIO_1p5_s1 aIO_2p0_s1 aIO_2p0_s2 aIWO_0p7_s1 aIWO_0p7_s1_bare aIWO_0p8_s2
      aIWO_1p0_Al2O3_s2 aIWO_1p0_s1 aIWO_1p5_s1 aIWO_2p0_Al2O3_s2 aIWO_2p0_comp_s1 aIWO_2p0_s1 aIWO_2p0_s1_bare aIWO_2p0_s2"
BENCH=aIWO_1p0_Al2O3_s2
T=$(mktemp -d /tmp/d24bd_test.XXXX); echo "test dir $T on $(hostname) $(date -u +%FT%TZ)"
mkdir -p "$T/src" "$T/fakeenv/bin" "$T/real" "$T/qstub" "$T/blocked" "$T/dry"
cp "$B/common/relax_node.sh.D24" "$T/src/relax_node.sh"
cp "$B/common/geomsel.py.D24" "$T/src/geomsel.py"
cp "$B/common/qeio.py" "$T/src/qeio.py"
cp "$B/runs/aIWO_1p0_s1/steps_relax.sh.D24" "$T/src/steps_relax.sh"
cp "$B/runs/$BENCH/steps_relax.sh.D24" "$T/src/steps_relax_bench.sh"
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
F=$U/fixtures

PASS=0; FAIL=0
check() {   # check <label> <detail> <0|1>
  if [ "$3" = 0 ]; then PASS=$((PASS + 1)); echo "    PASS $1"; else FAIL=$((FAIL + 1)); echo "    FAIL $1: $2"; fi
}
inx() { awk '/^[ \t]*ATOMIC_POSITIONS/{getline; print $2; exit}' "$1"; }   # In x of the first atom
rows() { awk '/^[ \t]*ATOMIC_POSITIONS/{f=1; next} f && NF >= 4 && $1 ~ /^[A-Z][a-z]?[0-9]*$/ {print $1, $2, $3, $4; next} f {f=0}' "$1"; }
# runcase <tag> <node> <steps> <seg> <relax.in> <case out|-> <guard text> [ad: new|old] [geomsel: yes|no] [segment_stop text]
#   new ad = the D-24 relax.sub / edited idle ad: transfers geomsel.py, segment_guard, segment_stop in, segment_guard out
runcase() {
  local tag=$1 node=$2 steps=$3 seg=$4 rin=$5 out=$6 guard=$7 ad=${8:-new} geo=${9:-yes} stop=${10:-}
  local d=$T/run_$tag; rm -rf "$d"; mkdir -p "$d"
  cp "$T/src/driver.sh" "$T/src/qeio.py" "$d/"; cp "$rin" "$d/relax.in"; cp "$steps" "$d/steps_relax.sh"
  [ "$geo" = yes ] && cp "$T/src/geomsel.py" "$d/"
  local tout="relax_s${seg}_results.tar.gz,relax.in,RELAX_STATUS"
  if [ "$ad" = new ]; then printf '%s' "$guard" > "$d/segment_guard"; printf '%s' "$stop" > "$d/segment_stop"; tout="$tout,segment_guard"; fi
  printf 'ClusterId = 990%s\nProcId = 0\nRequestCpus = 1\nTransferOutput = "%s"\n' "$seg" "$tout" > "$d/.job.ad"
  local t0 t1 rc
  t0=$(date +%s%N)
  ( cd "$d" && env _CONDOR_SCRATCH_DIR="$d" _CONDOR_JOB_AD="$d/.job.ad" QE_LOCAL="${FAKEENV:-$T/fakeenv}" NCPU_OVERRIDE=1 \
      CASE_OUT="$([ "$out" = - ] || echo "$out")" CASE_SLEEP="${CASE_SLEEP:-0}" bash "$node" "$seg" 72000 > node.stdout 2>&1 < /dev/null )
  rc=$?; t1=$(date +%s%N)
  local miss=""; for f in $(echo "$tout" | tr ',' ' '); do [ -e "$d/$f" ] || miss="$miss $f"; done
  R_RC=$rc; R_ST=$(cat "$d/RELAX_STATUS" 2>/dev/null); R_X=$(inx "$d/relax.in"); R_G=$(head -c 200 "$d/segment_guard" 2>/dev/null)
  R_S=$(cat "$d/segment_stop" 2>/dev/null); R_MISS=$miss; R_D=$d; R_MS=$(( (t1 - t0) / 1000000 ))
  echo "--- $tag: exit $rc, $R_MS ms, RELAX_STATUS $R_ST, relax.in In x $R_X, missing outputs:${miss:- none}"
  echo "    guard: ${R_G:-<empty or absent>}"
  echo "    node stdout: $(tail -1 "$d/node.stdout" | cut -c1-240)"
  echo "    tarball: $(tar tzf "$d/relax_s${seg}_results.tar.gz" 2>/dev/null | sort | tr '\n' ' ')"
  [ -f "$d/relax_s${seg}_lineage.log" ] && sed 's/^/    lineage: /' "$d/relax_s${seg}_lineage.log" | cut -c1-240
  grep -h 'relax status' "$d/relax_s${seg}_driver.log" 2>/dev/null | sed 's/^/    driver log: /' | cut -c1-260
}
cat > "$T/indep.py" <<'EOF'
"""Independent geometry bookkeeping (split on ATOMIC_POSITIONS headers; not geomsel's code path).
usage: indep.py <relax.out> [<rows out for the best validated geometry>] [<rows out for the last printed geometry>]
prints: best_index best_energy n_geometries validated_indices"""
import re, sys
EN = re.compile(r'^!+\s+total energy\s+=\s+(-?[0-9.]+) Ry', re.M)
body = open(sys.argv[1]).read().split('Begin final coordinates')[0]
parts = re.split(r'^ATOMIC_POSITIONS.*$', body, flags=re.M)
geoms = []
for k, p in enumerate(parts):
    rows = None
    if k > 0:
        rows = []
        for l in p.splitlines():
            if not l.strip():
                if rows:
                    break
                continue
            if not re.match(r'^\s*[A-Z][a-z]?\d*\s+-?\d', l):
                break
            rows.append(l.split()[:4])
    e = EN.findall(p)
    geoms.append((rows, float(e[0]) if e else None))
v = [(e, k) for k, (r, e) in enumerate(geoms) if e is not None]
if not v:
    print('none none', len(geoms), '-')
    sys.exit()
e, b = min(v)
print(b, repr(e), len(geoms), ','.join(str(k) for e2, k in sorted(v, key=lambda x: x[1])))
if len(sys.argv) > 2 and b > 0:
    open(sys.argv[2], 'w').write('\n'.join(' '.join(r) for r in geoms[b][0]) + '\n')
if len(sys.argv) > 3:
    open(sys.argv[3], 'w').write('\n'.join(' '.join(r) for r in geoms[-1][0]) + '\n')
EOF

echo; echo "===== 0. staged files = tested files; live files = derivation baseline"
( cd "$B" && md5sum -c --quiet common/D24_BD_staged.md5 && md5sum -c --quiet common/D24_BD_baseline.md5 ); check "manifests D24_BD_staged.md5 and D24_BD_baseline.md5 verify on AFS" "" $?

echo; echo "===== A. synthetic QE-format cases through the full node path (new relax_node.sh + driver.sh + steps + geomsel)"
while read -r name st x guard cat; do
  out=$T/cases/$name.out; [ -f "$out" ] || out=-
  runcase "$name" "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 3 "$T/cases/relax.in" "$out" ""
  g=empty; [ -n "$R_G" ] && g=armed
  erc=1; [ "$st" = CONVERGED ] && erc=0
  okc=0; [ "$cat" = - ] || { [[ "$R_G" == "FAILED "*" relax_s3 [$cat]: "* ]] && grep -q "^segment relax_s3: FAILED \[$cat\]" "$R_D/relax_s3_lineage.log"; okc=$?; }
  [ "$R_ST" = "$st" ] && [ "$R_X" = "$x" ] && [ "$g" = "$guard" ] && [ "$R_RC" = "$erc" ] && [ "$okc" = 0 ] && [ -z "$R_MISS" ]
  check "$name" "want $st x=$x guard=$guard [$cat] exit=$erc" $?
done < "$T/cases/expected.txt"
bx=$(inx "$T/run_T3_scf_not_achieved_after_steps/relax_s3_bestvalid.in" 2>/dev/null)
[ "$bx" = 5.0100000000 ]; check "T3 keeps the best validated geometry (g1) as relax_s3_bestvalid.in" "got $bx" $?

echo; echo "===== B. guard chain: the FAILED segment of T3 is followed by retry s4 (a case that would converge)"
d3=$T/run_T3_scf_not_achieved_after_steps
cp "$d3/relax.in" "$T/ap_relax.in"   # what the access point holds after T3's output transfer
runcase guard_s4 "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 4 "$T/ap_relax.in" "$T/cases/T1_bfgs_converged.out" "$(cat "$d3/segment_guard")"
d=$T/run_guard_s4
[ "$R_RC" = 1 ] && [ "$R_ST" = FAILED ] && [ ! -e "$d/relax.out" ] && ! grep -q 'job relax_s4 host' "$d/relax_s4_driver.log" \
  && cmp -s "$d/relax.in" "$T/ap_relax.in" && [ "$(cat "$d/segment_guard")" = "$(cat "$d3/segment_guard")" ] && [ -z "$R_MISS" ]
check "guard stops s4 before driver.sh (no pw.x, relax.in and guard unchanged, all outputs present, $R_MS ms)" "see above" $?

echo; echo "===== C. segment_stop (input only), inertness and preflight"
STOPL="STOP 2026-10-11T00:00:00Z manual: test stop"
runcase S1_stop_manual "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 3 "$T/cases/relax.in" "$T/cases/T1_bfgs_converged.out" "" new yes "$STOPL"
[ "$R_RC" = 1 ] && [ "$R_ST" = FAILED ] && [ ! -e "$R_D/relax.out" ] && [ "$R_X" = 5.0000000000 ] && [ "$R_S" = "$STOPL" ] && [ -z "$R_G" ] \
  && [ -z "$R_MISS" ] && tar tzf "$R_D/relax_s3_results.tar.gz" | grep -qx segment_stop && grep -q "segment_stop: $STOPL" "$R_D/node.stdout"
check "S1 STOP line in segment_stop: stop before pw.x, relax.in / segment_stop / empty guard unchanged, outputs present" "" $?
runcase S2_stop_comment "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 3 "$T/cases/relax.in" "$T/cases/T4_timelimit_midscf_with_steps.out" "" new yes "# cleared 2026-10-11 (was STOP ...)"
[ "$R_ST" = CONTINUE ] && [ "$R_X" = 5.0100000000 ]; check "S2 segment_stop without a leading STOP/FAILED line is inert" "got $R_ST" $?
runcase S3_stop_failed_word "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 3 "$T/cases/relax.in" "$T/cases/T4_timelimit_midscf_with_steps.out" "" new yes "FAILED manual: written with the old README habit"
[ "$R_ST" = FAILED ] && [ ! -e "$R_D/relax.out" ]; check "S3 a FAILED line in segment_stop also stops" "got $R_ST" $?
runcase S4_stop_second_line "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 3 "$T/cases/relax.in" "$T/cases/T4_timelimit_midscf_with_steps.out" "" new yes "$(printf '# note\nSTOP x manual: second line')"
[ "$R_ST" = FAILED ] && [ ! -e "$R_D/relax.out" ]; check "S4 a STOP line after a comment stops" "got $R_ST" $?
runcase S5_guard_stop_word "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 3 "$T/cases/relax.in" "$T/cases/T4_timelimit_midscf_with_steps.out" "STOP x manual"
[ "$R_ST" = FAILED ] && [ ! -e "$R_D/relax.out" ]; check "S5 a STOP line in segment_guard also stops" "got $R_ST" $?
n_in=0; n_out=0; for r in $RUNS; do for s in "$B/runs/$r/relax.sub.D24" $([ "$r" = "$BENCH" ] && echo "$B/runs/$r/relax.sub.D24_2gpu"); do
  grep -q '^transfer_input_files.*, segment_guard, segment_stop$' "$s" && n_in=$((n_in + 1))
  grep '^transfer_output_files' "$s" | grep -q segment_stop || n_out=$((n_out + 1)); done; done
[ "$n_in" = 17 ] && [ "$n_out" = 17 ]; check "S6 all 17 staged relax.sub files transfer segment_stop in and never out ($n_in, $n_out)" "" $?
runcase I1_old_ad_old_steps "$T/src/relax_node.sh" "$T/src/steps_relax_old.sh" 3 "$T/cases/relax.in" "$T/cases/T4_timelimit_midscf_with_steps.out" "" old yes
[ "$R_RC" = 1 ] && [ "$R_ST" = CONTINUE ] && [ "$R_X" = 5.0300000000 ]
check "I1 new node + pre-D-24 steps + no segment files: old behaviour unchanged (CONTINUE from last printed g3)" "got $R_ST $R_X" $?
runcase I1ref_old_node "$T/src/relax_node_old.sh" "$T/src/steps_relax_old.sh" 3 "$T/cases/relax.in" "$T/cases/T4_timelimit_midscf_with_steps.out" "" old yes
[ "$R_ST" = CONTINUE ] && [ "$R_X" = 5.0300000000 ]; check "I1ref old node gives the same (reference)" "got $R_ST $R_X" $?
runcase I2_preflight_old_ad "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 3 "$T/cases/relax.in" "$T/cases/T1_bfgs_converged.out" "" old no
[ "$R_RC" = 1 ] && [ "$R_ST" = FAILED ] && [ ! -e "$R_D/relax.out" ] && [ ! -e "$R_D/segment_guard" ] && [ "$R_X" = 5.0000000000 ]
check "I2 preflight: new steps without geomsel.py stop in seconds, no guard written, relax.in kept" "got $R_ST" $?
runcase I3_guard_cleared_comment "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 3 "$T/cases/relax.in" "$T/cases/T4_timelimit_midscf_with_steps.out" "# cleared 2026-10-11 by user (was FAILED ...)"
[ "$R_ST" = CONTINUE ] && [ "$R_X" = 5.0100000000 ]; check "I3 a guard without a leading FAILED line is inert" "got $R_ST" $?

echo; echo "===== D. benchmark steps (aIWO_1p0_Al2O3_s2 variant): GPU-memory sampler (fake nvidia-smi, 1 s)"
CASE_SLEEP=4 runcase bench "$T/src/relax_node.sh" "$T/src/steps_relax_bench.sh" 0 "$T/cases/relax.in" "$T/cases/T4_timelimit_midscf_with_steps.out" ""
grep -h 'gpumem' "$T/run_bench/relax_s0_driver.log" | sed 's/^/    /'
n=$(tar xzf "$T/run_bench/relax_s0_results.tar.gz" -O gpumem.log 2>/dev/null | wc -l); sleep 2
left=$(pgrep -u "$USER" -f "$T/fakeenv/bin/nvidia-smi" | wc -l)
[ "$R_ST" = CONTINUE ] && [ "$n" -ge 3 ] && [ "$left" = 0 ]; check "bench: CONTINUE, gpumem.log packed ($n lines), sampler stopped ($left left)" "" $?
diff <(sed '/D-24 benchmark/,/local gpumon/d; /kill "\$gpumon"/d; /log "gpumem/d' "$T/src/steps_relax_bench.sh") "$T/src/steps_relax.sh" > /dev/null
check "bench steps = common D-24 steps + the sampler block only" "" $?

echo; echo "===== E. real QE outputs"
tar xzf "$B/runs/aIO_2p0_s1/relax_s0_results.tar.gz" -C "$T/real" relax.out relax.in relax_s0_driver.log && \
  mv "$T/real/relax.out" "$T/real/aIO_2p0_s1_s0.out" && mv "$T/real/relax.in" "$T/real/aIO_2p0_s1_s0.in" && mv "$T/real/relax_s0_driver.log" "$T/real/aIO_2p0_s1_s0_driver.log"
mkdir -p "$T/real/x" && tar xzf "$B/runs/aIO_0p7_s1/relax_s0_results.tar.gz" -C "$T/real/x" && \
  mv "$T/real/x/relax.out" "$T/real/aIO_0p7_s1_s0.out" && mv "$T/real/x/relax.in" "$T/real/aIO_0p7_s1_s0.in"
runcase R1_canary_converged "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 1 "$F/canary_race.in" "$F/canary_race.out" ""
python3 "$T/src/qeio.py" newgeom "$F/canary_race.in" "$F/canary_race.out" > "$T/r1_expect.in"
[ "$R_RC" = 0 ] && [ "$R_ST" = CONVERGED ] && cmp -s <(sed -n '/ATOMIC_POSITIONS/,$p' "$T/r1_expect.in") <(sed -n '/ATOMIC_POSITIONS/,$p' "$T/run_R1_canary_converged/relax.in")
check "R1 real QE 7.x relax, bfgs converged (2 atoms): CONVERGED, final coordinates" "got $R_ST" $?
runcase R2_slab176_converged "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 1 "$F/slab2.in" "$F/slab2.out" ""
[ "$R_RC" = 0 ] && [ "$R_ST" = CONVERGED ]; check "R2 real QE 7.3.1 GPU relax, 176 atoms, bfgs converged: CONVERGED" "got $R_ST" $?
L=$(grep -n '^!' "$F/slab2.out" | sed -n 10p | cut -d: -f1)
{ head -n $((L + 40)) "$F/slab2.out"; printf '\n     Maximum CPU time exceeded\n\n     max_seconds     =   70184.00\n'; } > "$T/r3.out"
want=$(python3 "$T/indep.py" "$T/r3.out" "$T/r3.best")
runcase R3_slab176_timelimit "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 1 "$F/slab2.in" "$T/r3.out" ""
echo "    independent parse (best, E, n_geom, validated): $want"
[ "$R_ST" = CONTINUE ] && cmp -s <(rows "$R_D/relax.in") "$T/r3.best"; check "R3 real output cut by the time limit after 10 validated geometries: CONTINUE from the lowest-energy one" "got $R_ST" $?
runcase R4_aIO_2p0_s1_s0 "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 0 "$T/real/aIO_2p0_s1_s0.in" "$T/real/aIO_2p0_s1_s0.out" ""
[ "$R_RC" = 1 ] && [ "$R_ST" = FAILED ] && [[ "$R_G" == *" relax_s0 [scf]: SCF not converged"* ]]; check "R4 real aIO_2p0_s1 s0 (268 atoms, first SCF not converged): FAILED [scf] + guard" "got $R_ST" $?
runcase R5_aIO_0p7_s1_s0 "$T/src/relax_node.sh" "$T/src/steps_relax.sh" 0 "$T/real/aIO_0p7_s1_s0.in" "$T/real/aIO_0p7_s1_s0.out" ""
want=$(python3 "$T/indep.py" "$T/real/aIO_0p7_s1_s0.out" "$T/r5.best"); echo "    independent parse (best, E, n_geom, validated): $want"
[ "$R_ST" = FAILED ] && [[ "$R_G" == *"[scf]"* ]] && cmp -s <(rows "$R_D/relax_s0_bestvalid.in") "$T/r5.best" && [ "$(echo "$want" | awk '{print $1, $2}')" = "3 -24017.02019226" ]
check "R5 real aIO_0p7_s1 s0: FAILED [scf], bestvalid = independent argmin g3 (E -24017.02019226)" "got $R_ST" $?

echo; echo "===== F. install script syntax; PreVerRequirements substitution on the live benchmark ad (read-only)"
bash -n "$B/common/install_D24_BD.sh" && bash -n "$B/common/d24_transition.sh"; check "install_D24_BD.sh and d24_transition.sh parse" "" $?
pv=$(condor_q 12884198 -af:r PreVerRequirements)
nv=${pv/regexp(\"H100|H200\",TARGET.GPUs_DeviceName)/regexp(\"H200\",TARGET.GPUs_DeviceName)}
echo "    now:   $pv"; echo "    after: $nv"
[ "$nv" != "$pv" ] && [ "${nv//H100/}" = "$nv" ]; check "PreVerRequirements edit replaces only the device clause" "" $?

echo; echo "===== G. install in /tmp sandboxes (D24_BASE), fake condor_q from the live queue, logging condor_qedit"
FAKEQ=$T/q.tsv; export FAKEQ
condor_q -constraint 'regexp("_relax_s[0-9]+$", IWOJob)' -af:t ClusterId ProcId JobStatus IWOJob JobCurrentStartDate TransferInput TransferOutput RequestGPUs > "$T/q.raw" \
  || { echo "condor_q failed"; exit 1; }
while IFS=$'\t' read -r c p st iwo t0 tin tout ng; do
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$c" "$p" "$st" "$iwo" "$t0" "$tin" "$tout" "$(condor_q "$c.$p" -af:r PreVerRequirements)" "$ng"
done < "$T/q.raw" > "$FAKEQ"
echo "    fake queue: $(wc -l < "$FAKEQ") RELAX jobs: $(cut -f3,4 "$FAKEQ" | sort -k2 | tr '\t\n' ': ')"
cat > "$T/qstub/condor_q" <<'EOF'
#!/usr/bin/env python3
"""fake condor_q: reads $FAKEQ (TSV ClusterId ProcId JobStatus IWOJob JobCurrentStartDate TransferInput TransferOutput
PreVerRequirements RequestGPUs); supports the calls of install_D24_BD.sh and d24_transition.sh only."""
import os, re, sys
cols = ['ClusterId', 'ProcId', 'JobStatus', 'IWOJob', 'JobCurrentStartDate', 'TransferInput', 'TransferOutput',
        'PreVerRequirements', 'RequestGPUs']
qf = os.environ['FAKEQ']   # FAKEQ_LATE replaces it once the file FAKEQ_LATE_IF exists (a job starting mid-install)
if os.environ.get('FAKEQ_LATE') and os.environ.get('FAKEQ_LATE_IF') and os.path.exists(os.environ['FAKEQ_LATE_IF']):
    qf = os.environ['FAKEQ_LATE']
rows = [dict(zip(cols, l.rstrip('\n').split('\t'))) for l in open(qf) if l.strip()]
a = sys.argv[1:]
cons, ids, fmt, attrs, i = None, [], '-af', [], 0
while i < len(a):
    if a[i] == '-constraint':
        cons = a[i + 1]; i += 2
    elif a[i].startswith('-af'):
        fmt, attrs = a[i], a[i + 1:]; break
    else:
        ids.append(a[i]); i += 1
def ok(r):
    if ids:
        return f"{r['ClusterId']}.{r['ProcId']}" in ids or r['ClusterId'] in ids
    if cons:
        m = re.search(r'regexp\("(.*?)", IWOJob\)', cons)
        if m and not re.search(m.group(1), r['IWOJob']):
            return False
        if 'JobStatus == 2' in cons and r['JobStatus'] not in ('2', '6', '7'):
            return False
    return True
for r in rows:
    if ok(r):
        vals = [r.get(x, 'undefined') for x in attrs]
        if os.environ.get('STUB_EMPTY_TIN') == f"{r['ClusterId']}.{r['ProcId']}":
            vals = ['' if x == 'TransferInput' else v for x, v in zip(attrs, vals)]
        print('\n'.join(f'{x} = {v}' for x, v in zip(attrs, vals)) if fmt == '-af:lr' else ' '.join(vals))
EOF
printf '#!/bin/bash\necho "$*" >> "${QEDITLOG:-/dev/null}"\nexit 0\n' > "$T/qstub/condor_qedit"
for c in condor_rm condor_release condor_hold condor_submit condor_submit_dag condor_vacate_job; do
  printf '#!/bin/bash\necho "FORBIDDEN %s $*" >&2\nexit 97\n' "$c" > "$T/blocked/$c"
done
for c in cp mv touch chmod rm ln condor_qedit; do printf '#!/bin/bash\necho "STUB-BLOCKED %s $*" >&2\nexit 97\n' "$c" > "$T/dry/$c"; done
chmod +x "$T/qstub/"* "$T/blocked/"* "$T/dry/"*
mksb() {   # mksb <dir>: /tmp copy of the parts of the tree the install and the tool use (mtimes kept)
  local S=$1/iwo_amorph r f; mkdir -p "$S/common" "$S/runs/aIO_0p8_s1"
  ( cd "$B/common" && cp -p relax_node.sh driver.sh qeio.py relax_node.sh.D24 geomsel.py.D24 d24_transition.sh install_D24_BD.sh \
      D24_BD_staged.md5 D24_BD_baseline.md5 README_D24_BD.txt "$S/common/" )
  cp -p "$B/runs/aIO_0p8_s1/geomsel.py" "$B/runs/aIO_0p8_s1/relax.sub" "$B/runs/aIO_0p8_s1/steps_relax.sh" "$S/runs/aIO_0p8_s1/"
  for r in $RUNS; do
    mkdir -p "$S/runs/$r"
    ( cd "$B/runs/$r" && cp -p relax.sub steps_relax.sh relax.sub.D24 steps_relax.sh.D24 relax.in "$S/runs/$r/" \
      && for f in RELAX_STATUS relax.sub.D24_2gpu relax_s*_results.tar.gz; do [ -e "$f" ] && cp -p "$f" "$S/runs/$r/"; done; true )
  done
}
treesum() { ( cd "$1" && find . -type f | sort | xargs md5sum | md5sum | cut -c1-32 ); }
isrun() { case " $(echo $RUNS) " in *" $1 "*) return 0 ;; esac; return 1; }
# expected per the fake queue and the copied tarballs (independent of the install code)
EXP_IDLE=""; EXP_TRANS=""; EXP_RUNNING=""
while IFS=$'\t' read -r c p st iwo t0 rest; do
  r=${iwo%_relax_s*}; isrun "$r" || continue
  [ "$st" = 1 ] && EXP_IDLE="$EXP_IDLE $c.$p"
  case "$st" in 2|6|7) EXP_RUNNING="$EXP_RUNNING $r" ;; esac
done < "$FAKEQ"
EXP_EDITED=""   # chains whose relax.in was replaced by hand after their last finished segment (v2c: no transition stop)
for r in $RUNS; do
  if case " $EXP_RUNNING " in *" $r "*) true ;; *) false ;; esac; then EXP_TRANS="$EXP_TRANS $r"; continue; fi
  tb=$(ls "$B/runs/$r"/relax_s*_results.tar.gz 2>/dev/null | sed 's/.*relax_s\([0-9]*\)_results.*/\1/' | sort -rn | head -1)
  [ -n "$tb" ] || continue
  mkdir -p "$T/tb_$r"; tar xzf "$B/runs/$r/relax_s${tb}_results.tar.gz" -C "$T/tb_$r" relax.in 2>/dev/null
  if cmp -s "$T/tb_$r/relax.in" "$B/runs/$r/relax.in"; then EXP_TRANS="$EXP_TRANS $r"; else EXP_EDITED="$EXP_EDITED $r"; fi
done
nidle=$(echo $EXP_IDLE | wc -w); echo "    expected: idle ads$EXP_IDLE; transition stops:$EXP_TRANS; running:$EXP_RUNNING; relax.in edited after the last segment:${EXP_EDITED:- none}"
SBX() { env PATH="$T/qstub:$T/blocked:$PATH" D24_BASE="$1/iwo_amorph" QEDITLOG="${QEDITLOG:-/dev/null}" STUB_EMPTY_TIN="${STUB_EMPTY_TIN:-}"   bash "$1/iwo_amorph/common/${2}" "${@:3}"; }

SB=$T/sb1; mksb "$SB"; s0=$(treesum "$SB"); S=$SB/iwo_amorph; p0=$(treesum "$S/runs/aIO_0p8_s1")
( env PATH="$T/dry:$T/qstub:$T/blocked:$PATH" D24_BASE="$SB/iwo_amorph" bash "$SB/iwo_amorph/common/install_D24_BD.sh" --dry-run ) > "$T/g1.log" 2>&1; rc=$?
hits=$(grep -c -E 'STUB-BLOCKED|FORBIDDEN' "$T/g1.log"); nq=$(grep -c '^+ condor_qedit' "$T/g1.log"); nt=$(grep -c 'append to .*D24-transition' "$T/g1.log")
[ "$rc" = 0 ] && [ "$hits" = 0 ] && [ "$(treesum "$SB")" = "$s0" ] && [ "$nq" = $((2 * nidle + 2)) ] && [ "$nt" = "$(echo $EXP_TRANS | wc -w)" ]
check "G1 dry run: exit $rc, no mutating command reached ($hits), tree unchanged, $nq qedits (want $((2 * nidle + 2))), $nt transition stops" "" $?
grep -E '^\+ (condor_qedit|append)' "$T/g1.log" | cut -c1-230 | sed 's/^/      /'

QEDITLOG=$T/qedit.log; : > "$QEDITLOG"
SBX "$SB" install_D24_BD.sh > "$T/g2.log" 2>&1; rc=$?
tail -22 "$T/g2.log" | cut -c1-220 | sed 's/^/      /'
bad=""
for r in $RUNS; do
  cmp -s "$S/runs/$r/relax.sub" "$B/runs/$r/relax.sub.D24" || bad="$bad sub:$r"
  cmp -s "$S/runs/$r/relax.sub.pre_D24" "$B/runs/$r/relax.sub" || bad="$bad subbak:$r"
  cmp -s "$S/runs/$r/steps_relax.sh" "$B/runs/$r/steps_relax.sh.D24" || bad="$bad steps:$r"
  cmp -s "$S/runs/$r/steps_relax.sh.pre_D24" "$B/runs/$r/steps_relax.sh" || bad="$bad stepsbak:$r"
  [ -f "$S/runs/$r/segment_guard" ] && [ ! -s "$S/runs/$r/segment_guard" ] || bad="$bad guard:$r"
  ntr=$(grep -c '^STOP [^ ]* D24-transition: ' "$S/runs/$r/segment_stop" 2>/dev/null)
  if case " $EXP_TRANS " in *" $r "*) true ;; *) false ;; esac; then [ "$ntr" = 1 ] || bad="$bad trans:$r"; else [ "$ntr" = 0 ] && [ ! -s "$S/runs/$r/segment_stop" ] || bad="$bad notrans:$r"; fi
  if case " $EXP_RUNNING " in *" $r "*) true ;; *) false ;; esac; then
    k=$(awk -F'\t' -v r="$r" '$4 ~ "^"r"_relax_s[0-9]+$" && ($3 == 2 || $3 == 6 || $3 == 7) {sub(/.*_relax_s/, "", $4); print $4}' "$FAKEQ")
    cmp -s "$S/runs/$r/relax_s${k}_input.in" "$B/runs/$r/relax.in" || bad="$bad input:$r"
  fi
done
cmp -s "$S/common/relax_node.sh" "$B/common/relax_node.sh.D24" && cmp -s "$S/common/relax_node.sh.pre_D24" "$B/common/relax_node.sh" \
  && cmp -s "$S/common/geomsel.py" "$B/common/geomsel.py.D24" || bad="$bad common"
[ "$(treesum "$S/runs/aIO_0p8_s1")" = "$p0" ] || bad="$bad pilot"
[ "$rc" = 0 ] && [ -z "$bad" ]; check "G2 install: 16 relax.sub / steps / relax_node swapped with .pre_D24 backups, empty guards, transition stops and saved inputs exactly as expected, pilot untouched" "rc $rc;$bad" $?
ned=0; for r in $EXP_EDITED; do grep -q "$r: relax.in was changed after relax_s[0-9]* (by hand): no transition stop" "$T/g2.log" && [ ! -s "$S/runs/$r/segment_stop" ] || ned=1; done
[ "$ned" = 0 ]; check "G2 chains whose relax.in was replaced after their last segment (${EXP_EDITED:- none}): reported, no transition stop" "" $?
GEO=$S/common/geomsel.py; badq=""
for j in $EXP_IDLE; do
  c=${j%.*}; tin=$(awk -F'\t' -v c="$c" '$1 == c {print $6}' "$FAKEQ"); tout=$(awk -F'\t' -v c="$c" '$1 == c {print $7}' "$FAKEQ")
  grep -qxF -- "-constraint ClusterId == $c && ProcId == 0 && JobStatus == 1 TransferInput \"$tin,$GEO,segment_guard,segment_stop\"" "$QEDITLOG" || badq="$badq tin:$c"
  grep -qxF -- "-constraint ClusterId == $c && ProcId == 0 && JobStatus == 1 TransferOutput \"$tout,segment_guard\"" "$QEDITLOG" || badq="$badq tout:$c"
done
bc=$(awk -F'\t' -v r="$BENCH" '$4 ~ "^"r"_relax_s[0-9]+$" && $3 == 1 {print $1}' "$FAKEQ")
nb=$(grep -c -E "^-constraint ClusterId == $bc && ProcId == 0 && JobStatus == 1 (PreVerRequirements \(regexp\(\"H200\",TARGET.GPUs_DeviceName\)\) && |RequestGPUs 1$)" "$QEDITLOG")
nall=$(wc -l < "$QEDITLOG")
[ -z "$badq" ] && [ "$nb" = 2 ] && [ "$nall" = $((2 * nidle + 2)) ] && ! grep -q 'FORBIDDEN' "$T/g2.log"
check "G2 qedits: exactly TransferInput += geomsel.py,segment_guard,segment_stop and TransferOutput += segment_guard on the $nidle idle ads, H200 + 1 GPU on $bc only ($nall edits)" "$badq nb=$nb" $?
s1=$(treesum "$SB"); SBX "$SB" install_D24_BD.sh > "$T/g3.log" 2>&1; rc=$?
[ "$rc" != 0 ] && [ "$(treesum "$SB")" = "$s1" ]; check "G3 a second install refuses and changes nothing: $(grep -m1 -E 'changed|already|missing' "$T/g3.log" | cut -c1-120)" "rc $rc" $?
SB2=$T/sb2; mksb "$SB2"; echo "# drift" >> "$SB2/iwo_amorph/runs/aIO_1p5_s1/relax.sub"; s0=$(treesum "$SB2")
QEDITLOG=$T/qedit2.log SBX "$SB2" install_D24_BD.sh > "$T/g4.log" 2>&1; rc=$?
[ "$rc" != 0 ] && [ "$(treesum "$SB2")" = "$s0" ] && grep -q 'live files changed since staging' "$T/g4.log" && [ ! -s "$T/qedit2.log" ]
check "G4 a live relax.sub changed after staging: install refuses at step 0, nothing changed" "rc $rc" $?
SB3=$T/sb3; mksb "$SB3"; echo "# drift" >> "$SB3/iwo_amorph/runs/aIWO_2p0_s2/steps_relax.sh.D24"; s0=$(treesum "$SB3")
QEDITLOG=$T/qedit3.log SBX "$SB3" install_D24_BD.sh > "$T/g5.log" 2>&1; rc=$?
[ "$rc" != 0 ] && [ "$(treesum "$SB3")" = "$s0" ] && grep -q 'staged files changed' "$T/g5.log" && [ ! -s "$T/qedit3.log" ]
check "G5 a staged file changed after testing: install refuses at step 0, nothing changed" "rc $rc" $?
SB4=$T/sb4; mksb "$SB4"; first=$(echo $EXP_IDLE | awk '{print $1}')
: > "$T/qedit4.log"; QEDITLOG=$T/qedit4.log STUB_EMPTY_TIN=$first SBX "$SB4" install_D24_BD.sh > "$T/g6.log" 2>&1; rc=$?
nsw=0; for r in $RUNS; do cmp -s "$SB4/iwo_amorph/runs/$r/relax.sub" "$B/runs/$r/relax.sub" || nsw=$((nsw + 1)); done
[ "$rc" != 0 ] && grep -q "unexpected TransferInput" "$T/g6.log" && [ "$nsw" = 0 ] && cmp -s "$SB4/iwo_amorph/common/relax_node.sh" "$B/common/relax_node.sh" \
  && ! grep -q "ClusterId == ${first%.*} " "$T/qedit4.log"
check "G6 condor_q returns an empty TransferInput for $first: install stops in step 2, that ad not edited, no file swapped" "rc $rc nsw $nsw" $?
# G7 (v2c) two RELAX jobs that are idle in steps 1-2 start during the install: the fake queue switches once
#    common/relax_node.sh.pre_D24 exists (after step 4). L1 started before the cutoff (it may have read the pre-D-24
#    steps): step 6 arms its chain and keeps its input. L2 started an hour later (D-24 steps for certain): not armed.
SB5=$T/sb5; mksb "$SB5"; S5=$SB5/iwo_amorph
inlist() { case " $1 " in *" $2 "*) return 0 ;; esac; return 1; }   # inlist <list> <item>
lates=""
for r in $(awk -F'\t' '$3 == 1 {r = $4; sub(/_relax_s[0-9]+$/, "", r); print r}' "$FAKEQ"); do
  isrun "$r" && [ "$r" != "$BENCH" ] && ! inlist "$EXP_TRANS" "$r" && ! inlist "$lates" "$r" && lates="$lates $r"
done
L1=$(echo $lates | awk '{print $1}'); L2=$(echo $lates | awk '{print $2}')
if [ -n "$L1" ] && [ -n "$L2" ]; then
  now=$(date +%s)
  awk -F'\t' -v OFS='\t' -v a="$L1" -v b="$L2" -v t1="$now" -v t2="$((now + 3600))" '
    $4 ~ "^"a"_relax_s[0-9]+$" && $3 == 1 {$3 = 2; $5 = t1}
    $4 ~ "^"b"_relax_s[0-9]+$" && $3 == 1 {$3 = 2; $5 = t2} {print}' "$FAKEQ" > "$T/q_late.tsv"
  export FAKEQ_LATE=$T/q_late.tsv FAKEQ_LATE_IF=$S5/common/relax_node.sh.pre_D24
  : > "$T/qedit5.log"; QEDITLOG=$T/qedit5.log SBX "$SB5" install_D24_BD.sh > "$T/g7.log" 2>&1; rc=$?
  unset FAKEQ_LATE FAKEQ_LATE_IF
  grep -E 'started during|already armed' "$T/g7.log" | cut -c1-230 | sed 's/^/      /'
  k1=$(awk -F'\t' -v a="$L1" '$4 ~ "^"a"_relax_s[0-9]+$" {sub(/.*_relax_s/, "", $4); print $4}' "$T/q_late.tsv")
  badl=""
  [ "$(grep -c '^STOP [^ ]* D24-transition: relax_s[0-9]* (job [0-9.]*) started during the install' "$S5/runs/$L1/segment_stop")" = 1 ] \
    && [ "$(grep -c '^STOP' "$S5/runs/$L1/segment_stop")" = 1 ] || badl="$badl L1stop"
  cmp -s "$S5/runs/$L1/relax_s${k1}_input.in" "$B/runs/$L1/relax.in" || badl="$badl L1input"
  [ ! -s "$S5/runs/$L2/segment_stop" ] && ! ls "$S5/runs/$L2"/relax_s*_input.in > /dev/null 2>&1 || badl="$badl L2"
  for r in $EXP_TRANS; do [ "$(grep -c '^STOP' "$S5/runs/$r/segment_stop")" = 1 ] || badl="$badl dup:$r"; done
  n7=$(grep -l '^STOP' "$S5"/runs/*/segment_stop 2>/dev/null | wc -l)
  [ "$rc" = 0 ] && [ -z "$badl" ] && [ "$n7" = $(( $(echo $EXP_TRANS | wc -w) + 1 )) ]
  check "G7 step 6: $L1 (started before the cutoff) armed with its input kept; $L2 (started after) not armed; no duplicate lines ($n7 chains stopped)" "rc $rc;$badl" $?
else
  echo "    G7 skipped: fewer than two idle non-benchmark chains without a transition stop in the live queue"
fi
# G8 (v2c) the tarball rule both ways, independent of the live state: X with relax.in = its s0 output (armed),
#    Y with relax.in replaced after s0 (not armed, reported)
SB6=$T/sb6; mksb "$SB6"; S6=$SB6/iwo_amorph; X=aIO_0p7_s1; Y=aIO_2p0_s1
if [ -f "$S6/runs/$X/relax_s0_results.tar.gz" ] && [ -f "$S6/runs/$Y/relax_s0_results.tar.gz" ]; then
  tar xzf "$S6/runs/$X/relax_s0_results.tar.gz" -O relax.in > "$S6/runs/$X/relax.in"
  { tar xzf "$S6/runs/$Y/relax_s0_results.tar.gz" -O relax.in; echo "! replaced by hand (test)"; } > "$S6/runs/$Y/relax.in"
  : > "$T/qedit6.log"; QEDITLOG=$T/qedit6.log SBX "$SB6" install_D24_BD.sh > "$T/g8.log" 2>&1; rc=$?
  grep -E "^\[.*\] ($X|$Y): " "$T/g8.log" | cut -c1-200 | sed 's/^/      /'
  [ "$rc" = 0 ] && [ "$(grep -c "^STOP [^ ]* D24-transition: relax_s0 ended with the pre-D-24 steps" "$S6/runs/$X/segment_stop")" = 1 ] \
    && [ ! -s "$S6/runs/$Y/segment_stop" ] && grep -q "$Y: relax.in was changed after relax_s0 (by hand): no transition stop" "$T/g8.log"
  check "G8 tarball rule: $X (relax.in = s0 output) armed; $Y (relax.in replaced after s0) not armed, reported" "rc $rc" $?
fi

echo; echo "===== H. transition tool on the installed sandbox sb1"
fq() {   # fq <run> <JobStatus> [<IWOJob>]: change the fake queue entry of a chain
  awk -F'\t' -v OFS='\t' -v r="$1" -v st="$2" -v iwo="${3:-}" '$4 ~ "^"r"_relax_s[0-9]+$" {$3 = st; if (iwo != "") $4 = iwo} {print}' "$FAKEQ" > "$FAKEQ.tmp" && mv "$FAKEQ.tmp" "$FAKEQ"
}
TR() { SBX "$SB" d24_transition.sh "$@"; }
R=$S/runs
# H1/H2 real aIO_0p7_s1 (s1 held, pre-D-24 ad)
d=$R/aIO_0p7_s1; s0=$(treesum "$d"); TR aIO_0p7_s1 > "$T/h1.log" 2>&1; rc=$?; sed 's/^/      /' "$T/h1.log" | cut -c1-230
[ "$rc" = 0 ] && [ "$(treesum "$d")" = "$s0" ] && grep -q 'D-24 rule:  FAILED \[scf\]' "$T/h1.log" && grep -q 'best=3' "$T/h1.log"
check "H1 aIO_0p7_s1 read-only: FAILED [scf], best=3, nothing changed" "rc $rc" $?
# H1r (v2c) a held chain whose live relax.in was replaced after s0 (the A15 rescue inputs, 2026-10-11 01:58 CEST) has no
#     transition line and --apply refuses; the sandbox copy is then put back to the s0 output to test the tool itself
for C in aIO_0p7_s1 aIO_2p0_s1; do
  inlist "$EXP_EDITED" "$C" || continue
  dd=$R/$C; s0=$(treesum "$dd"); TR "$C" --apply > "$T/h1r_$C.log" 2>&1; rc=$?
  [ "$rc" != 0 ] && grep -q 'differs from what relax_s0 wrote' "$T/h1r_$C.log" && [ "$(treesum "$dd")" = "$s0" ] && [ ! -s "$dd/segment_stop" ]
  check "H1r $C (relax.in replaced after s0): no transition line, --apply refuses, nothing changed" "rc $rc" $?
  tar xzf "$dd/relax_s0_results.tar.gz" -O relax.in > "$dd/relax.in"   # sandbox only
done
cp "$d/relax.in" "$T/h2_relax.in"; TR aIO_0p7_s1 --apply > "$T/h2.log" 2>&1; rc=$?; grep applied "$T/h2.log" | cut -c1-230 | sed 's/^/      /'
[ "$rc" = 0 ] && ! grep -q 'D24-transition' "$d/segment_stop" && [ "$(grep -c '^STOP [^ ]* d24_transition: relax_s0 \[scf\]: SCF not converged' "$d/segment_stop")" = 1 ] \
  && cmp -s <(rows "$d/relax_s0_bestvalid.in") "$T/r5.best" && cmp -s "$d/relax.in" "$T/h2_relax.in" && [ -s "$d/d24_transition.log" ] && [ ! -s "$d/segment_guard" ]
check "H2 aIO_0p7_s1 --apply: stays stopped with the [scf] verdict, relax_s0_bestvalid.in = independent g3, relax.in unchanged" "rc $rc" $?
# H3 real aIO_2p0_s1
d=$R/aIO_2p0_s1; cp "$d/relax.in" "$T/h3_relax.in"; TR aIO_2p0_s1 --apply > "$T/h3.log" 2>&1; rc=$?; grep -E 'D-24 rule|applied' "$T/h3.log" | cut -c1-200 | sed 's/^/      /'
[ "$rc" = 0 ] && grep -q '^STOP [^ ]* d24_transition: relax_s0 \[scf\]' "$d/segment_stop" && ! grep -q D24-transition "$d/segment_stop" && [ ! -e "$d/relax_s0_bestvalid.in" ] && cmp -s "$d/relax.in" "$T/h3_relax.in"
check "H3 aIO_2p0_s1 --apply: stays stopped [scf], no bestvalid (nothing validated), relax.in unchanged" "rc $rc" $?
# H4 refusal while the chain's job runs
first_run=$(echo $EXP_RUNNING | awk '{print $1}')
if [ -n "$first_run" ]; then
  s0=$(treesum "$R/$first_run"); TR "$first_run" --apply > "$T/h4.log" 2>&1; rc=$?
  [ "$rc" != 0 ] && grep -q 'is running' "$T/h4.log" && [ "$(treesum "$R/$first_run")" = "$s0" ]; check "H4 $first_run (job running): refuses, nothing changed" "rc $rc" $?
fi
# H5 full transition of a running chain: old-rule end of s0 on a real 176-atom output cut inside the SCF of an unvalidated
#    trial (g10), s1 started with the D-24 ad and stopped by the install's transition line, tool, then s2 runs
C=aIWO_1p0_s1; d=$R/$C
python3 - "$F/slab2.out" "$T/h5.out" <<'PY'
import sys
L = open(sys.argv[1]).read().splitlines()
bang = [i for i, l in enumerate(L) if l.startswith('!')]
a = next(i for i in range(bang[9], len(L)) if L[i].startswith('ATOMIC_POSITIONS'))
b = a + 1
while L[b].strip():
    b += 1
tail = [l for l in L[b:b + 60] if not l.startswith('!')][:40]
open(sys.argv[2], 'w').write('\n'.join(L[:b] + tail + ['', '     Maximum CPU time exceeded', '', '     max_seconds     =   70184.00', '']))
PY
want=$(python3 "$T/indep.py" "$T/h5.out" "$T/h5.best" "$T/h5.last"); echo "    independent parse of the cut (best, E, n_geom, validated): $want"
runcase H5_old_s0 "$T/src/relax_node_old.sh" "$T/src/steps_relax_old.sh" 0 "$F/slab2.in" "$T/h5.out" "" old no
[ "$R_ST" = CONTINUE ] && cmp -s <(rows "$R_D/relax.in") "$T/h5.last" && ! cmp -s "$T/h5.last" "$T/h5.best"
check "H5a pre-D-24 rule continues from the last printed geometry, an unvalidated trial (the hazard)" "got $R_ST" $?
cp "$R_D/relax.in" "$R_D/relax_s0_results.tar.gz" "$R_D/RELAX_STATUS" "$d/"; cp "$F/slab2.in" "$d/relax_s0_input.in"   # transfer back; the segment's input
fq "$C" 1 "${C}_relax_s1"
runcase H5_s1_stopped "$S/common/relax_node.sh" "$d/steps_relax.sh" 1 "$d/relax.in" "$F/slab2.out" "$(cat "$d/segment_guard")" new yes "$(cat "$d/segment_stop")"
[ "$R_RC" = 1 ] && [ ! -e "$R_D/relax.out" ] && grep -q 'segment_stop: STOP .* D24-transition' "$R_D/node.stdout" && cmp -s "$R_D/relax.in" "$d/relax.in"
check "H5b s1 (D-24 ad) is stopped by the install's transition line in $R_MS ms, relax.in unchanged" "" $?
cp "$R_D/relax_s1_results.tar.gz" "$R_D/relax.in" "$R_D/RELAX_STATUS" "$R_D/segment_guard" "$d/"
TR "$C" > "$T/h5c.log" 2>&1; rc=$?; sed 's/^/      /' "$T/h5c.log" | cut -c1-230
[ "$rc" = 0 ] && grep -q 'segment relax_s0 ' "$T/h5c.log" && grep -q 'D-24 rule:  CONTINUE' "$T/h5c.log"
check "H5c tool skips the stop tarball s1, re-classifies s0: CONTINUE" "rc $rc" $?
TR "$C" --apply > "$T/h5d.log" 2>&1; rc=$?; grep applied "$T/h5d.log" | cut -c1-230 | sed 's/^/      /'
[ "$rc" = 0 ] && cmp -s <(rows "$d/relax.in") "$T/h5.best" && cmp -s <(rows "$d"/relax.in.pre_transition_*) "$T/h5.last" && ! grep -q '^STOP' "$d/segment_stop"
check "H5d --apply: relax.in = independent lowest-energy validated geometry, old one kept, no STOP line left" "rc $rc" $?
fq "$C" 1 "${C}_relax_s2"
runcase H5_s2_runs "$S/common/relax_node.sh" "$d/steps_relax.sh" 2 "$d/relax.in" "$F/slab2.out" "$(cat "$d/segment_guard")" new yes "$(cat "$d/segment_stop")"
[ "$R_RC" = 0 ] && [ "$R_ST" = CONVERGED ]; check "H5e the next segment runs normally (here: converges)" "got $R_ST" $?
# H6 old-rule CONTINUE from an unvalidated trial whose D-24 verdict is FAILED [noprogress] with best = input (g0)
C=aIWO_0p7_s1; d=$R/$C; fq "$C" 1 "${C}_relax_s1"
runcase H6_old_s0 "$T/src/relax_node_old.sh" "$T/src/steps_relax_old.sh" 0 "$T/cases/relax.in" "$T/cases/T5_no_new_validated_step.out" "" old no
cp "$R_D/relax.in" "$R_D/relax_s0_results.tar.gz" "$R_D/RELAX_STATUS" "$d/"; rm -f "$d/relax_s0_input.in"
TR "$C" > "$T/h6a.log" 2>&1; rc=$?; grep -E 'rule|input used|bestvalid' "$T/h6a.log" | cut -c1-200 | sed 's/^/      /'
[ "$rc" = 0 ] && grep -q 'D-24 rule:  FAILED \[noprogress\]' "$T/h6a.log" && grep -q 'bestvalid:  none written (best validated geometry = the segment input' "$T/h6a.log"
check "H6a without the saved input: FAILED [noprogress], the input geometry is not guessed from the template" "rc $rc" $?
cp "$T/cases/relax.in" "$d/relax_s0_input.in"; TR "$C" --apply > "$T/h6b.log" 2>&1; rc=$?
[ "$rc" = 0 ] && [ "$(inx "$d/relax_s0_bestvalid.in")" = 5.0000000000 ] && [ "$(inx "$d/relax.in")" = 5.0100000000 ] && grep -q '^STOP [^ ]* d24_transition: relax_s0 \[noprogress\]' "$d/segment_stop"
check "H6b with the saved input: bestvalid = input (x 5.00), stays stopped, relax.in (old trial x 5.01) left for the section 3 decision" "rc $rc" $?
# H7 relax.in changed by hand after the segment: refused; restored: applied
C=aIWO_0p8_s2; d=$R/$C; fq "$C" 1 "${C}_relax_s1"
runcase H7_old_s0 "$T/src/relax_node_old.sh" "$T/src/steps_relax_old.sh" 0 "$T/cases/relax.in" "$T/cases/T4_timelimit_midscf_with_steps.out" "" old no
cp "$R_D/relax.in" "$R_D/relax_s0_results.tar.gz" "$R_D/RELAX_STATUS" "$d/"; cp "$T/cases/relax.in" "$d/relax_s0_input.in"; echo "# edited" >> "$d/relax.in"
s0=$(treesum "$d"); TR "$C" --apply > "$T/h7a.log" 2>&1; rc=$?
[ "$rc" != 0 ] && grep -q 'differs from what relax_s0 wrote' "$T/h7a.log" && [ "$(treesum "$d")" = "$s0" ]; check "H7a relax.in edited by hand: --apply refuses, nothing changed" "rc $rc" $?
cp "$R_D/relax.in" "$d/relax.in"; TR "$C" --apply > "$T/h7b.log" 2>&1; rc=$?
[ "$rc" = 0 ] && [ "$(inx "$d/relax.in")" = 5.0100000000 ] && ! grep -q '^STOP' "$d/segment_stop"; check "H7b restored: CONTINUE from validated g1 (x 5.01) instead of the old trial g3 (x 5.03)" "rc $rc" $?
# H8 newest segment already D-24: refused
C=aIWO_0p7_s1_bare; d=$R/$C; fq "$C" 1 "${C}_relax_s1"
runcase H8_d24_s0 "$S/common/relax_node.sh" "$d/steps_relax.sh" 0 "$T/cases/relax.in" "$T/cases/T4_timelimit_midscf_with_steps.out" "" new yes ""
cp "$R_D/relax.in" "$R_D/relax_s0_results.tar.gz" "$R_D/RELAX_STATUS" "$R_D/segment_guard" "$d/"
grep -q '^STOP [^ ]* D24-transition' "$d/segment_stop"; check "H8 precondition: $C carries the install's transition line (it was running)" "" $?
s0=$(treesum "$d"); TR "$C" > "$T/h8a.log" 2>&1; rc=$?; sed 's/^/      /' "$T/h8a.log" | cut -c1-200
[ "$rc" = 0 ] && grep -q 'relax_s0 already ran the D-24 steps' "$T/h8a.log" && grep -q 'apply removes it' "$T/h8a.log" && [ "$(treesum "$d")" = "$s0" ]
check "H8a newest segment already D-24, read-only: reported, nothing changed" "rc $rc" $?
printf '# kept note\n' >> "$d/segment_stop"; cp "$d/relax.in" "$T/h8_relax.in"; cp "$d/segment_guard" "$T/h8_guard"
TR "$C" --apply > "$T/h8b.log" 2>&1; rc=$?; grep applied "$T/h8b.log" | cut -c1-200 | sed 's/^/      /'
[ "$rc" = 0 ] && ! grep -q 'D24-transition' "$d/segment_stop" && grep -qx '# kept note' "$d/segment_stop" && cmp -s "$d/relax.in" "$T/h8_relax.in" \
  && cmp -s "$d/segment_guard" "$T/h8_guard" && grep -q 'already D-24' "$d/d24_transition.log"
check "H8b --apply removes only the D24-transition line (other lines, relax.in, segment_guard unchanged), logged" "rc $rc" $?
s0=$(treesum "$d"); TR "$C" --apply > "$T/h8c.log" 2>&1; rc=$?
[ "$rc" != 0 ] && grep -q 'no D24-transition line: nothing to do' "$T/h8c.log" && [ "$(treesum "$d")" = "$s0" ]; check "H8c again: nothing to do, refused, nothing changed" "rc $rc" $?
# H8d a newer D-24 segment whose tarball has a lineage log but no relax.out (pw.x skipped) is the one reported, not s0
mkdir -p "$T/h8d" && printf 'segment relax_s1: FAILED [infra] (relax.out missing or empty)\n' > "$T/h8d/relax_s1_lineage.log" \
  && tar czf "$d/relax_s1_results.tar.gz" -C "$T/h8d" relax_s1_lineage.log
echo "STOP 2026-10-11T00:00:00Z D24-transition: test line" >> "$d/segment_stop"
TR "$C" > "$T/h8d.log" 2>&1; rc=$?
[ "$rc" = 0 ] && grep -q 'segment relax_s1 ' "$T/h8d.log" && grep -q 'relax_s1 already ran the D-24 steps: segment relax_s1: FAILED \[infra\]' "$T/h8d.log"
check "H8d a D-24 tarball without relax.out (lineage only) is taken as the newest segment" "rc $rc" $?
TR aIO_0p8_s1 > "$T/h9.log" 2>&1; rc=$?
[ "$rc" != 0 ] && grep -q 'not one of the 16' "$T/h9.log"; check "H9 the pilot is refused" "rc $rc" $?

echo; echo "===== I. item D revert file relax.sub.D24_2gpu"
b1=$B/runs/$BENCH/relax.sub.D24; b2=$B/runs/$BENCH/relax.sub.D24_2gpu
diff "$b1" "$b2" | sed 's/^/      /'
other=$(diff "$b1" "$b2" | grep '^[<>]' | grep -v -E '^[<>] (request_gpus|requirements|#)' | wc -l)
[ "$other" = 0 ] && grep -q '^request_gpus *= 2$' "$b2" && grep -q '^requirements *= regexp("H100|H200", TARGET.GPUs_DeviceName) && !regexp("MIG", TARGET.GPUs_DeviceName)$' "$b2" \
  && grep -q '^transfer_input_files.*geomsel.py, segment_guard, segment_stop$' "$b2" && grep -q '^transfer_output_files.*, segment_guard$' "$b2" \
  && [ "$(grep -v '^#' "$b2" | md5sum)" = "$(grep -v '^#' "$B/runs/$BENCH/relax.sub" | sed -e "s|^\(transfer_input_files.*\)$|\1, /afs/cern.ch/user/m/melrashe/iwo_amorph/common/geomsel.py, segment_guard, segment_stop|" -e 's|^\(transfer_output_files.*\)$|\1, segment_guard|' -e 's#^\(requirements .*\)$#\1 \&\& !regexp("MIG", TARGET.GPUs_DeviceName)#' | md5sum)" ]
check "I1 D24_2gpu = live bench relax.sub (2 x H100|H200) + D-24 transfers + MIG exclusion; differs from the 1-GPU file only in request_gpus / requirements / comments" "" $?
grep -q 'never relax.sub.pre_D24' "$b1" && grep -q 'swap in relax.sub.D24_2gpu (never relax.sub.pre_D24' "$B/common/README_D24_BD.txt" && ! grep -q 'revert = relax.sub.pre_D24' "$b1" "$B/common/README_D24_BD.txt"
check "I2 README section 4 and the relax.sub.D24 comment name relax.sub.D24_2gpu as the revert, not relax.sub.pre_D24" "" $?
runcase I3_revert_2gpu_ad "$T/src/relax_node.sh" "$T/src/steps_relax_bench.sh" 2 "$T/cases/relax.in" "$T/cases/T4_timelimit_midscf_with_steps.out" "" new yes ""
[ "$R_ST" = CONTINUE ]; check "I3 a retry from relax.sub.D24_2gpu (D-24 transfers) runs normally" "got $R_ST" $?
runcase I4_revert_pre_D24_ad "$T/src/relax_node.sh" "$T/src/steps_relax_bench.sh" 2 "$T/cases/relax.in" "$T/cases/T4_timelimit_midscf_with_steps.out" "" old no
[ "$R_ST" = FAILED ] && [ ! -e "$R_D/relax.out" ] && grep -q preflight "$R_D/node.stdout"
check "I4 (the v1 hazard) a retry from relax.sub.pre_D24 with the D-24 steps stops at the preflight, so it must not be the revert" "got $R_ST" $?

echo; echo "===== J. MIG exclusion: the staged requirements evaluated against the live slot ads (condor_status, read-only)"
before=$(condor_status -const 'regexp("H100|H200", GPUs_DeviceName)'  -af GPUs_DeviceName 2>/dev/null | sort | uniq -c | tr '\n' ';')
echo "    H100|H200 (as before): $before"
okj=0
for s in $(for r in $RUNS; do echo "$B/runs/$r/relax.sub.D24"; done) "$b2"; do
  e=$(sed -n 's/^requirements *= //p' "$s" | sed 's/TARGET\.//g')
  m=$(condor_status -const "$e" -af GPUs_DeviceName 2>/dev/null | sort | uniq -c | tr '\n' ';')
  case "$m" in *MIG*|'') okj=1; echo "    BAD $s: $m" ;; esac
done
e=$(sed -n 's/^requirements *= //p' "$b1" | sed 's/TARGET\.//g'); mb=$(condor_status -const "$e" -af GPUs_DeviceName 2>/dev/null | sort | uniq -c | tr '\n' ';')
echo "    bench 1 x H200: $mb"
case "$mb" in *H100*|*MIG*|'') okj=1 ;; esac
[[ "$before" == *MIG* ]] && [ "$okj" = 0 ]; check "J the old clause matches MIG slices; every staged requirements matches H100 NVL / H200 slots and no MIG slice" "" $?

echo; echo "===== RESULT: $PASS passed, $FAIL failed (test dir $T)"
