cd ~/iwo_amorph
P() { grep -E "$1" "$2" 2>/dev/null; }
for c in In32O48 In31WO48 In32O47 In31WO47_far In31WO47_near In31WO47_near72; do
  v=vac/$c; a=checks/gpumax_work/a20_g002/$c
  echo "######## $c"
  echo "-- relax.in settings"; grep -E "degauss|smearing|mixing|conv_thr|electron_maxstep|forc_conv|etot_conv|nspin|ecutwfc|ecutrho|occupations|tot_charge" $v/relax.in | tr -s ' ' | tr '\n' ';'; echo; grep -A1 K_POINTS $v/relax.in | tr '\n' ' '; echo
  echo "-- relax.out"; echo "bfgs_conv=$(grep -c 'bfgs converged' $v/relax.out) n_bang=$(grep -c '^!' $v/relax.out) scf_fail=$(grep -c 'convergence NOT achieved' $v/relax.out) end=$(grep -c 'End of BFGS' $v/relax.out) job_done=$(grep -c 'JOB DONE' $v/relax.out)"
  grep '^!' $v/relax.out | tail -2; grep 'smearing contrib' $v/relax.out | tail -1; grep 'Total force' $v/relax.out | tail -1; grep -E 'number of bfgs steps|Final energy|final energy' $v/relax.out | tail -2
  grep -m1 'number of electrons' $v/relax.out; grep -m1 'number of k points' $v/relax.out; grep -m1 'Program PWSCF' $v/relax.out
  echo "-- SEGMENT_SUMMARY"; cat $v/SEGMENT_SUMMARY 2>/dev/null | head -8
  echo "-- FINAL scf.in/scf.out (k4)"; grep -E "degauss|smearing|mixing|conv_thr|calculation" $v/scf.in | tr -s ' ' | tr '\n' ';'; echo; grep -A1 K_POINTS $v/scf.in | tr '\n' ' '; echo
  echo "conv=$(grep -c 'convergence has been achieved' $v/scf.out) notach=$(grep -c 'convergence NOT achieved' $v/scf.out) done=$(grep -c 'JOB DONE' $v/scf.out)"; grep '^!' $v/scf.out; grep 'smearing contrib' $v/scf.out | tail -1; grep 'internal energy' $v/scf.out | tail -1; grep -m1 'number of k points' $v/scf.out; grep 'convergence has been achieved' $v/scf.out
  echo "-- A20(ii)"; t=$a/a20g002_${c}_results.tar.gz; tar tzf $t | tr '\n' ' '; echo
  d=$(mktemp -d); tar xzf $t -C $d; o=$(ls $d/*.out $d/*/*.out 2>/dev/null | grep -v -i driver | head -3); echo "outs: $o"
  for f in $o; do echo "  [$f] conv=$(grep -c 'convergence has been achieved' $f) notach=$(grep -c 'convergence NOT achieved' $f) done=$(grep -c 'JOB DONE' $f)"; grep '^!' $f; grep 'smearing contrib' $f | tail -1; grep 'internal energy' $f | tail -1; grep -m1 'number of k points' $f; grep 'convergence has been achieved' $f; grep -m1 'Program PWSCF' $f; done
  echo "  diff a20 scf.in vs vac scf.in:"; diff $a/scf.in $v/scf.in | head -12
  rm -rf $d
done
