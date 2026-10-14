#!/bin/bash
# Verifier's independent D-24 B+D tests (read-only on AFS; everything runs in /tmp), adapted to staging v2 by the builder:
# relax.sub regeneration with the v2 edit (segment_stop, MIG exclusion, D24_2gpu), new ads carry an empty segment_stop,
# guard comparison by content (the v1 harness dropped the trailing newline), 'sed' not stubbed in the dry run (the v2
# install uses it read-only in a pipeline; it never runs sed -i). usage: bash vtest2.sh <bundle dir>
set -u
U=$1; B=$HOME/iwo_amorph
T=$(mktemp -d /tmp/vBD_test.XXXX); echo "verifier test dir $T on $(hostname) $(date -u +%FT%TZ)"
mkdir -p "$T/src" "$T/fakeenv/bin" "$T/real" "$T/stubs"
cp "$B/common/relax_node.sh.D24" "$T/src/relax_node.sh"
cp "$B/common/geomsel.py.D24" "$T/src/geomsel.py"
cp "$B/common/qeio.py" "$T/src/qeio.py"
cp "$B/runs/aIO_2p0_s2/steps_relax.sh.D24" "$T/src/steps_relax.sh"
cp "$B/runs/aIWO_1p0_Al2O3_s2/steps_relax.sh.D24" "$T/src/steps_bench.sh"
cp "$B/runs/aIO_2p0_s2/steps_relax.sh" "$T/src/steps_old.sh"
sed 's/^    sleep 60$/    sleep 1/' "$B/common/driver.sh" > "$T/src/driver.sh"
echo "== test-only driver diff: $(diff "$B/common/driver.sh" "$T/src/driver.sh" | grep -c '^[<>]') lines"
echo "== staged identity"
md5sum "$B"/runs/*/steps_relax.sh.D24 | awk '{print $1}' | sort | uniq -c
md5sum "$B"/runs/*/steps_relax.sh | awk '{print $1}' | sort | uniq -c
md5sum "$B/common/relax_node.sh" "$B/common/relax_node.sh.D24" "$B/common/geomsel.py.D24" "$B/runs/aIO_0p8_s1/geomsel.py" "$B/common/driver.sh" "$B/common/qeio.py"
echo "== bench steps vs common D24 steps"; diff "$T/src/steps_relax.sh" "$T/src/steps_bench.sh"
echo "== relax.sub.D24 regenerated from the LIVE relax.sub (staging sed) == staged?"
GEO=/afs/cern.ch/user/m/melrashe/iwo_amorph/common/geomsel.py
RUNS="aIO_0p7_s1 aIO_1p0_s1 aIO_1p5_s1 aIO_2p0_s1 aIO_2p0_s2 aIWO_0p7_s1 aIWO_0p7_s1_bare aIWO_0p8_s2 aIWO_1p0_Al2O3_s2 aIWO_1p0_s1 aIWO_1p5_s1 aIWO_2p0_Al2O3_s2 aIWO_2p0_comp_s1 aIWO_2p0_s1 aIWO_2p0_s1_bare aIWO_2p0_s2"
for r in $RUNS; do
  d=$B/runs/$r
  sed -e "/^transfer_input_files/ s|\$|, $GEO, segment_guard, segment_stop|" -e '/^transfer_output_files/ s|$|, segment_guard|' \
      -e 's#^\(requirements *= regexp("H100|H200", TARGET.GPUs_DeviceName)\)$#\1 \&\& !regexp("MIG", TARGET.GPUs_DeviceName)#' \
      -e '/^queue/ i # D-24 (2026-10-11): geomsel.py, segment_guard and segment_stop (fail-fast stops), MIG slices excluded; see common/README_D24_BD.txt' "$d/relax.sub" > "$T/sub.$r"
  if [ "$r" = aIWO_1p0_Al2O3_s2 ]; then
    sed -e '/^queue/ i # D-24 item D revert file: the 2 x H100|H200 request from before the benchmark, with the D-24 transfers (README section 4)' "$T/sub.$r" > "$T/sub2.$r"
    cmp -s "$T/sub2.$r" "$d/relax.sub.D24_2gpu" && echo "$r: relax.sub.D24_2gpu regenerated same" || echo "$r: relax.sub.D24_2gpu regenerated DIFFERS"
    sed -i -e 's|^request_gpus .*|request_gpus            = 1|' -e 's#^requirements .*#requirements            = regexp("H200", TARGET.GPUs_DeviceName) \&\& !regexp("MIG", TARGET.GPUs_DeviceName)#' \
      -e '/^queue/ i # D-24 item D: single-H200 benchmark (was request_gpus 2, H100|H200). Revert = swap in relax.sub.D24_2gpu (never relax.sub.pre_D24 unless the full section 5 rollback is done), README_D24_BD.txt section 4' "$T/sub.$r"
  fi
  cmp -s "$T/sub.$r" "$d/relax.sub.D24" && s=same || s=DIFFERS
  miss=""
  for f in $(grep '^transfer_input_files' "$d/relax.sub.D24" | cut -d= -f2- | tr ',' ' '); do
    case "$f" in /*) p=$f ;; *) p=$d/$f ;; esac
    if [ ! -e "$p" ]; then
      case "$f" in segment_guard|segment_stop|$GEO) miss="$miss [$f: created by install step 1]" ;; *) miss="$miss MISSING:$f" ;; esac
    fi
  done
  echo "$r: regenerated $s; gpus $(grep -E '^request_gpus' "$d/relax.sub.D24" | awk '{print $3}') req $(grep '^requirements' "$d/relax.sub.D24" | cut -d'"' -f2); inputs:${miss:- all exist}; out:$(grep '^transfer_output_files' "$d/relax.sub.D24" | cut -d= -f2-)"
done

printf '#!/bin/bash\n[ -n "${CASE_OUT:-}" ] && [ -f "$CASE_OUT" ] && cat "$CASE_OUT"\nsleep "${CASE_SLEEP:-0}"\nexit 0\n' > "$T/fakeenv/bin/mpirun"
chmod +x "$T/fakeenv/bin/mpirun"; ln -s /usr/bin/python3 "$T/fakeenv/bin/python"; ln -s /usr/bin/true "$T/fakeenv/bin/pw.x"
echo "== system nvidia-smi on this host: $(command -v nvidia-smi || echo none)"

tar xzf "$B/runs/aIO_0p7_s1/relax_s0_results.tar.gz" -C "$T/real" relax.out relax.in
python3 "$U/vcases.py" "$U/fixtures/slab2.out" "$T/real/relax.out" "$T/cases"

rows() { awk '/^[ \t]*ATOMIC_POSITIONS/{f=1; next} f && NF >= 4 && $1 ~ /^[A-Z][a-z]?[0-9]*$/ {print $1, $2, $3, $4; next} f {f=0}' "$1"; }
PASS=0; FAIL=0
ok() { if [ "$2" = 0 ]; then PASS=$((PASS + 1)); echo "    PASS $1"; else FAIL=$((FAIL + 1)); echo "    FAIL $1"; fi; }
# vrun <tag> <steps> <seg> <relax.in template> <case out|-> <guard text> <ad: new|old> <geomsel: yes|no>
vrun() {
  local tag=$1 steps=$2 seg=$3 rin=$4 out=$5 guard=$6 ad=$7 geo=$8
  local d=$T/run_$tag; rm -rf "$d"; mkdir -p "$d"
  cp "$T/src/driver.sh" "$T/src/qeio.py" "$d/"; cp "$rin" "$d/relax.in"; cp "$steps" "$d/steps_relax.sh"
  [ "$geo" = yes ] && cp "$T/src/geomsel.py" "$d/"
  local tout="relax_s${seg}_results.tar.gz,relax.in,RELAX_STATUS"
  if [ "$ad" = new ]; then printf '%s' "$guard" > "$d/segment_guard"; : > "$d/segment_stop"; tout="$tout,segment_guard"; fi
  printf 'ClusterId = 991%s\nProcId = 0\nRequestCpus = 22\nRequestGPUs = 0\nTransferOutput = "%s"\n' "$seg" "$tout" > "$d/.job.ad"
  ( cd "$d" && env _CONDOR_SCRATCH_DIR="$d" _CONDOR_JOB_AD="$d/.job.ad" QE_LOCAL="${FAKEENV:-$T/fakeenv}" NCPU_OVERRIDE=1 \
      CASE_OUT="$([ "$out" = - ] || echo "$out")" CASE_SLEEP="${CASE_SLEEP:-0}" bash "$T/src/relax_node.sh" "$seg" 72000 > node.stdout 2>&1 < /dev/null )
  V_RC=$?; V_ST=$(cat "$d/RELAX_STATUS" 2>/dev/null); V_G=$(head -c 200 "$d/segment_guard" 2>/dev/null)
  V_MISS=""; for f in $(echo "$tout" | tr ',' ' '); do [ -e "$d/$f" ] || V_MISS="$V_MISS $f"; done
  V_D=$d
  echo "--- $tag: exit $V_RC, status $V_ST, missing outputs:${V_MISS:- none}; guard: ${V_G:-<empty/absent>}"
  echo "    node: $(tail -1 "$d/node.stdout" | cut -c1-200)"
}

echo; echo "===== V-A: cases cut from REAL QE 7.3.1 outputs, full node path, new ad"
while IFS=$'\t' read -r name st guard rf; do
  case $name in C8_*) tmpl=$T/real/relax.in ;; *) tmpl=$U/fixtures/slab2.in ;; esac
  vrun "$name" "$T/src/steps_relax.sh" 2 "$tmpl" "$T/cases/$name.out" "" new yes
  erc=1; [ "$st" = CONVERGED ] && erc=0
  g=empty; [ -n "$V_G" ] && g=armed
  if [ "$rf" = - ]; then cmp -s <(rows "$V_D/relax.in") <(rows "$tmpl"); pos=$?; else cmp -s <(rows "$V_D/relax.in") "$rf"; pos=$?; fi
  [ "$V_RC" = "$erc" ] && [ "$V_ST" = "$st" ] && [ "$g" = "$guard" ] && [ -z "$V_MISS" ] && [ "$pos" = 0 ]
  ok "$name: want $st/$guard/exit $erc, relax.in rows as expected (pos cmp $pos)" $?
  if [ -f "$T/cases/$name.bestrows" ]; then
    cmp -s <(rows "$V_D/relax_s2_bestvalid.in") "$T/cases/$name.bestrows"; ok "$name: relax_s2_bestvalid.in = independent lowest-energy validated geometry" $?
  fi
  grep -h 'relax status' "$V_D/relax_s2_driver.log" | cut -c1-230 | sed 's/^/    /'
done < "$T/cases/expect.tsv"
cp "$T/run_C8_real_aIO_0p7_s1_s0/segment_guard" "$T/guard_C8"

echo; echo "===== V-B: next retry after the real C8 FAILED segment (guard armed), new/edited ad"
vrun guard_next "$T/src/steps_relax.sh" 3 "$T/run_C8_real_aIO_0p7_s1_s0/relax.in" "$T/cases/C1_full_converged.out" "$(cat "$T/guard_C8")" new yes
[ "$V_RC" = 1 ] && [ "$V_ST" = FAILED ] && [ ! -e "$V_D/relax.out" ] && [ -z "$V_MISS" ] && [ "$(cat "$V_D/segment_guard")" = "$(cat "$T/guard_C8")" ] \
  && cmp -s <(rows "$V_D/relax.in") <(rows "$T/real/relax.in") && tar tzf "$V_D/relax_s3_results.tar.gz" | grep -q segment_guard
ok "guard: stop before pw.x; relax.in, guard unchanged; all outputs incl. tarball present" $?
vrun guard_noad "$T/src/steps_relax.sh" 3 "$T/real/relax.in" - "" old no
[ "$V_RC" = 1 ] && [ "$V_ST" = FAILED ] && [ ! -e "$V_D/segment_guard" ] && [ -z "$V_MISS" ] && [ -n "$(rows "$V_D/relax.in")" ]
ok "released pre-D-24 ad (no geomsel/segment_guard transfer) + new steps: preflight stop, no segment_guard created, outputs present" $?
vrun old_ad_old_steps "$T/src/steps_old.sh" 3 "$U/fixtures/slab2.in" "$T/cases/C5_bfgsfail_trial.out" "" old no
[ "$V_ST" = CONTINUE ] && [ -z "$V_MISS" ]; ok "pre-D-24 ad + pre-D-24 steps under the new node: old behaviour, outputs present" $?
vrun guard_comment "$T/src/steps_relax.sh" 3 "$U/fixtures/slab2.in" "$T/cases/C4_timelimit_g2.out" "# reset 2026-10-11 (was: FAILED ...)" new yes
[ "$V_ST" = CONTINUE ]; ok "reset guard (comment line) is inert" $?
vrun guard_2ndline "$T/src/steps_relax.sh" 3 "$U/fixtures/slab2.in" "$T/cases/C4_timelimit_g2.out" "$(printf '# note\nFAILED manual: stop')" new yes
[ "$V_ST" = FAILED ] && [ ! -e "$V_D/relax.out" ]; ok "manual re-arm on a later line still stops" $?

echo; echo "===== V-C: benchmark steps"
mkdir -p "$T/fakeenv2/bin"; cp "$T/fakeenv/bin/mpirun" "$T/fakeenv2/bin/"; ln -s /usr/bin/python3 "$T/fakeenv2/bin/python"; ln -s /usr/bin/true "$T/fakeenv2/bin/pw.x"
FAKEENV=$T/fakeenv2 CASE_SLEEP=2 vrun bench_no_smi "$T/src/steps_bench.sh" 0 "$U/fixtures/slab2.in" "$T/cases/C4_timelimit_g2.out" "" new yes
[ "$V_ST" = CONTINUE ] && [ -z "$V_MISS" ]; ok "bench without nvidia-smi: classification unaffected, outputs present" $?
grep -h gpumem "$V_D/relax_s0_driver.log" | sed 's/^/    /'
printf '#!/bin/bash\necho "timestamp, index, name, memory.used [MiB], memory.total [MiB], utilization.gpu [%%]"\nwhile :; do echo "$(date +%%Y/%%m/%%d), 0, NVIDIA H200, 91000 MiB, 143771 MiB, 97 %%"; sleep 1; done\n' > "$T/fakeenv/bin/nvidia-smi"
chmod +x "$T/fakeenv/bin/nvidia-smi"
CASE_SLEEP=3 vrun bench_smi "$T/src/steps_bench.sh" 0 "$U/fixtures/slab2.in" "$T/cases/C2_scffail_g5.out" "" new yes
sleep 2; left=$(pgrep -u "$USER" -f "$T/fakeenv/bin/nvidia-smi" | wc -l)
[ "$V_ST" = FAILED ] && [ -n "$V_G" ] && tar tzf "$V_D/relax_s0_results.tar.gz" | grep -q gpumem.log && [ "$left" = 0 ]
ok "bench FAILED segment: guard armed, gpumem.log packed, sampler stopped ($left left)" $?
grep -h gpumem "$V_D/relax_s0_driver.log" | sed 's/^/    /'

echo; echo "===== V-D: install dry run with every mutating command stubbed"
for c in condor_qedit condor_rm condor_release condor_hold condor_submit condor_submit_dag cp mv touch chmod rm ln; do
  printf '#!/bin/bash\necho "STUB-BLOCKED %s $*" >&2\nexit 97\n' "$c" > "$T/stubs/$c"; /usr/bin/chmod +x "$T/stubs/$c"
done
( PATH=$T/stubs:$PATH bash "$B/common/install_D24_BD.sh" --dry-run ) > "$T/dry.log" 2>&1; echo "    dry-run exit $?"
echo "    stub hits: $(grep -c STUB-BLOCKED "$T/dry.log")"
cut -c1-420 "$T/dry.log"
echo; echo "===== RESULT: $PASS passed, $FAIL failed ($T)"
