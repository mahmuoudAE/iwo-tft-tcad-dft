#!/bin/bash
# lineage_relax.sh v2 (and v1 for comparison) on fake run directories with pre-item-B and item-B segments, fake EOS
# checkpoints, a stub condor_q and the d24ok final archive.
SP=/mnt/c/Users/moham/AppData/Local/Temp/claude/C--Users-moham-Downloads-IWO-Local-Codex-Handoff--1--IWO-ATLAS-Model-claude/7c34fe97-c389-4002-8f70-9615a643e20b/scratchpad/d24f
V1=$SP/v1/lineage_relax.sh.D24; V2=$SP/stage/common/lineage_relax.sh.D24
T=~/d24f_test/lin; rm -rf $T; mkdir -p $T/runs $T/ckpt $T/eos $T/bin; W=$(mktemp -d)
IN=~/d24test/inputs/relax.in
printf '#!/bin/bash\n[ -n "${CQ:-}" ] && printf "%%b" "$CQ"\nexit 0\n' > $T/bin/condor_q; chmod +x $T/bin/condor_q
export PATH=$T/bin:$PATH RUNS=$T/runs CKPT_EOS=$T/ckpt EXPORT_EOS=$T/eos
geom() { sed "s/^\(  In [0-9.-]*\) /\1$1 /" $IN; }                  # geometry variant k: a different relax.in
asrun() { sed "s/max_seconds = [0-9.d]*/max_seconds = $2/" $1; }     # what run_pw makes of an input
relaxout() {   # relaxout <n energies> <n printed geometries> <converged yes|no>
  local i; for ((i = 0; i < $1; i++)); do echo "!    total energy              =   -$((8000 + i)).5 Ry"; [ $i -lt $2 ] && printf 'ATOMIC_POSITIONS (angstrom)\nIn 0 0 0\n\n'; done
  for ((; i < $2; i++)); do printf 'ATOMIC_POSITIONS (angstrom)\nIn 0 0 0\n\n'; done
  [ $3 = yes ] && printf '     bfgs converged in   %d scf cycles\nBegin final coordinates\nATOMIC_POSITIONS (angstrom)\nIn 0 0 0\nEnd final coordinates\n' $1
}
seg_old() {   # pre-item-B segment: seg cluster status input output n_e n_g conv ; AFS archive = OUTPUT relax.in; EOS ckpt = as-run input
  local R=$1 s=$2 c=$3 d=$W/$1_s$2; mkdir -p $d/ck
  cp $6 $d/relax.in; relaxout $7 $8 $9 > $d/relax.out; echo "[x] relax status: $4; BFGS steps this segment: $7" > $d/relax_s${s}_driver.log
  tar czf $T/runs/$R/relax_s${s}_results.tar.gz -C $d relax.in relax.out relax_s${s}_driver.log; touch $T/runs/$R/logs/relax_s$s.$c.out
  asrun $5 7100$s > $d/ck/relax.in; cp $d/relax.out $d/ck/; tar czf $T/ckpt/relax_s${s}_$c.tar.gz -C $d/ck relax.in relax.out
  echo "000 ($c.000.000) 10/10 12:00:00 Job submitted from host" >> $T/runs/$R/logs/relax.log
}
seg_new() {   # item-B segment: + relax_s<seg>_input.in and relax_s<seg>_lineage.log in the AFS archive
  local R=$1 s=$2 c=$3 d=$W/$1_s$2; mkdir -p $d/ck
  asrun $5 7200$s > $d/relax_s${s}_input.in; cp $6 $d/relax.in; relaxout $7 $8 $9 > $d/relax.out
  echo "[x] relax status: $4; geomsel: ${10}" > $d/relax_s${s}_driver.log
  printf 'segment relax_s%s: %s\ngeomsel: %s\ngeomsel.py md5 x\npositions md5: input a next relax.in b\n' $s $4 "${10}" > $d/relax_s${s}_lineage.log
  tar czf $T/runs/$R/relax_s${s}_results.tar.gz -C $d relax.in relax.out relax_s${s}_driver.log relax_s${s}_input.in relax_s${s}_lineage.log
  touch $T/runs/$R/logs/relax_s$s.$c.out
  cp $d/relax_s${s}_input.in $d/ck/relax.in; tar czf $T/ckpt/relax_s${s}_$c.tar.gz -C $d/ck relax.in
  echo "000 ($c.000.000) 10/10 12:00:00 Job submitted from host" >> $T/runs/$R/logs/relax.log
}
seg_stop() {  # item-B stop before pw.x (guard / preflight): note driver log + unchanged relax.in, no checkpoint
  local R=$1 s=$2 c=$3 d=$W/$1_s$2; mkdir -p $d
  cp $4 $d/relax.in; : > $d/segment_guard; : > $d/segment_stop
  echo "[x] relax status: FAILED (stopped before pw.x on b9x); preflight: steps_relax.sh needs geomsel.py" > $d/relax_s${s}_driver.log
  tar czf $T/runs/$R/relax_s${s}_results.tar.gz -C $d relax_s${s}_driver.log relax.in segment_guard segment_stop
  touch $T/runs/$R/logs/relax_s$s.$c.out; echo "000 ($c.000.000) 10/10 12:00:00 Job submitted from host" >> $T/runs/$R/logs/relax.log
}
geom 1 > $W/g0; geom 2 > $W/g1; geom 3 > $W/g2
# run A: s0 pre-B CONTINUE (last printed geometry not SCF-validated), s1 B CONTINUE, s2 stopped, s3 B CONVERGED
R=test_2p0_s1; mkdir -p $T/runs/$R/logs
seg_old  $R 0 12884100 CONTINUE $W/g0 $W/g1 3 3 no
seg_new  $R 1 12884200 CONTINUE $W/g1 $W/g2 3 3 no "n_scf=3 n_geom=4 best=2 best_new=yes E0=-8000.5 Ebest=-8002.5 scf_iters=9,8,7 scf_fail=0 fermi_warn=0"
seg_stop $R 2 12884300 $W/g2
seg_new  $R 3 12884400 CONVERGED $W/g2 $IN 5 5 yes "n_scf=5 n_geom=6 best=5 best_new=yes E0=-8000.5 Ebest=-8004.5 scf_iters=9 scf_fail=0 fermi_warn=0"
echo "000 (12884999.000.000) 10/10 12:00:00 Job submitted from host" >> $T/runs/$R/logs/relax.log   # a cluster nobody names
cp $IN $T/runs/$R/relax.in; echo CONVERGED > $T/runs/$R/RELAX_STATUS
echo "### A1 v2, gate time (no final archive)"; bash $V2 $R; echo "exit $?"
cp ~/d24test/d24ok/final_results.tar.gz $T/runs/$R/
echo "### A2 v2, collection (d24ok final archive) + --to-eos"; bash $V2 $R final_results.tar.gz --to-eos | tail -9; echo "exit ${PIPESTATUS[0]}"; ls $T/eos/$R/relax_segments
echo "  EOS copy of the s0 checkpoint = as-run input of s0: $(tar xzf $T/eos/$R/relax_segments/relax_s0_ckpt_12884100.tar.gz -O relax.in | grep -o 'max_seconds = [0-9]*')"
# run B: the chain stopped after s1 (s2 stopped by the preflight): v1 names s2 as the writer, v2 names s1
R=test_1p0_s1; mkdir -p $T/runs/$R/logs
seg_old  $R 0 12885100 CONTINUE $W/g0 $W/g1 4 3 no
seg_new  $R 1 12885200 CONTINUE $W/g1 $W/g2 3 3 no "n_scf=3 n_geom=4 best=1 best_new=yes E0=-8000.5 Ebest=-8001.5 scf_iters=9 scf_fail=0 fermi_warn=0"
seg_stop $R 2 12885300 $W/g2
cp $W/g2 $T/runs/$R/relax.in; echo FAILED > $T/runs/$R/RELAX_STATUS
echo "### B1 v1 on the stopped chain"; bash $V1 $R | grep -E 'written by|^seg'
echo "### B2 v2 on the stopped chain (segment 3 still in the queue, idle)"; CQ="12885400 test_1p0_s1_relax_s3 1\n" bash $V2 $R | grep -vE '^#'; echo "exit $?"
# run C: a finished segment whose inputs are gone (stdout file only), and a reset between s0 and s1
R=test_0p7_s1; mkdir -p $T/runs/$R/logs
seg_old  $R 0 12886100 CONTINUE $W/g0 $W/g1 3 2 no
seg_new  $R 1 12886200 CONTINUE $W/g0 $W/g2 3 3 no "n_scf=3 n_geom=4 best=1 best_new=yes E0=-8000.5 Ebest=-8001.5 scf_iters=9 scf_fail=0 fermi_warn=0"
touch $T/runs/$R/logs/relax_s2.12886300.out
cp $W/g2 $T/runs/$R/relax.in
echo "### C v2: reset before s1 (chain NO), s2 without any record (A14 INCOMPLETE, exit 2)"; bash $V2 $R | grep -vE '^#'; echo "exit ${PIPESTATUS[0]}"
rm -rf $W
