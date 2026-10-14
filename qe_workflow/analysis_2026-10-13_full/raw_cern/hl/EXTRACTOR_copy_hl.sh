# read-only: stream crystalline H-L text files (no wavefunctions/densities) as base64 tar; sha256 list first
set -e
T=$(mktemp -d); cd ~/iwo_amorph
L=""
for c in In32O48 In31WO48 In32O47 In31WO47_far In31WO47_near In31WO47_near72; do
  for f in relax.in relax.out scf.in scf.out SEGMENT_SUMMARY RELAX_STATUS FINAL_STATUS; do [ -f vac/$c/$f ] && L="$L vac/$c/$f"; done
  a=checks/gpumax_work/a20_g002/$c; L="$L $a/scf.in"
  mkdir -p $T/a20/$c; tar xzf $a/a20g002_${c}_results.tar.gz -C $T/a20/$c scf.out
  mkdir -p $T/final/$c; tar xzf vac/$c/final_results.tar.gz -C $T/final/$c scf.out scf.in 2>/dev/null || tar tzf vac/$c/final_results.tar.gz > $T/final/$c/LIST
done
L="$L vac/In31WO47_near/attempt1/relax.in vac/In31WO47_near/attempt1/relax.out vac/In31WO47_near/attempt1/SEGMENT_SUMMARY vac/In31WO47_near/a28_staging/MANIFEST.md5 vac/In31WO47_near/relax.in.pre_A28_20261011T130452Z hse/validation/chi_compare_In31WO48_gamma.txt hse/In31WO48/README.md"
echo "### SHA256 (remote originals)"
sha256sum $L
for c in In32O48 In31WO48 In32O47 In31WO47_far In31WO47_near In31WO47_near72; do sha256sum checks/gpumax_work/a20_g002/$c/a20g002_${c}_results.tar.gz vac/$c/final_results.tar.gz; done
(cd $T && sha256sum a20/*/scf.out final/*/* | sed 's|^|tarmember |')
echo "### BEGIN TAR"
tar czf - $L -C $T a20 final | base64 -w 0
echo
echo "### END TAR"
rm -rf $T
