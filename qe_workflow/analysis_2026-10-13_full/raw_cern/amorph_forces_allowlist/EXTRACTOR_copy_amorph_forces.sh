# Read-only. Amorphous force checks C034/C035/C037 (sight rule: energies, forces, SCF bookkeeping only).
# pw.x outputs are NEVER copied: an allowlist filter keeps only '!' energies, -TS, Total force/SCF correction,
# the first 'Forces acting on atoms' block, convergence lines, k/electron/atom counts, version, JOB DONE.
set -e
T=$(mktemp -d); O=$T/out; mkdir -p $O
allow() {  # $1 = scf.out path, $2 = destination
  awk '/Forces acting on atoms \(cartesian axes, Ry\/au\)/ {nf++; if (nf==1) {f=1; print NR": "$0; next}}
       f==1 && /atom +[0-9]+ type +[0-9]+ +force =/ {print NR": "$0; next}
       f==1 && /(contrib|Total force|SCF correction|^ *$)/ && !/atom/ {if ($0 !~ /^ *$/) f=0}
       /^!|Total force =|convergence has been achieved|convergence NOT achieved|number of k points=|number of electrons|number of atoms\/cell|Program PWSCF|JOB DONE|smearing contrib|internal energy E=F\+TS/ {print NR": "$0}' "$1" \
  | grep -E '^[0-9]+: (!    total energy|     smearing contrib|     internal energy E=F\+TS|     Total force =|     convergence has been achieved|     convergence NOT achieved|     number of k points=|     number of electrons|     number of atoms/cell|     Program PWSCF|   JOB DONE|     Forces acting on atoms|     atom +[0-9]+ type +[0-9]+ +force =)' > "$2"
}
cd ~/iwo_amorph
echo "### SHA256 originals"
# C034
for s in mv gauss; do r=checks/A27_C4_smear/results_20261011T121728Z/$s; mkdir -p $O/C034/$s; sha256sum $r/scf.out checks/A27_C4_smear/$s/a27c4_${s}_results.tar.gz
  allow $r/scf.out $O/C034/$s/scf.allow.txt; cp $r/scf.in $O/C034/$s/scf.in; done
cp checks/A27_C4_smear/results_20261011T121728Z/compare_c4.json $O/C034/ ; grep -v -i -E 'fermi|gap|homo|lumo|eigen|edge|highest' checks/A27_C4_smear/results_20261011T121728Z/compare_result.txt > $O/C034/compare_result.filtered.txt || true
# C035
for s in unsplit split; do mkdir -p $O/C035/$s $T/x/$s; tb=checks/A25_split_equiv/$s/a25eq_${s}_results.tar.gz; sha256sum $tb
  tar xzf $tb -C $T/x/$s; f=$(find $T/x/$s -name scf.out | head -1); echo "member $s $(sha256sum $f | cut -c1-64)"
  allow $f $O/C035/$s/scf.allow.txt; cp checks/A25_split_equiv/$s/scf.in $O/C035/$s/scf.in; done
cp checks/A25_split_equiv/split/label_map.tsv $O/C035/split/
for r in $(find checks/A25_split_equiv -maxdepth 2 -name compare_result.txt); do mkdir -p $O/C035/$(dirname ${r#checks/A25_split_equiv/}); grep -v -i -E 'fermi|gap|homo|lumo|eigen|edge|highest' $r > $O/C035/$(dirname ${r#checks/A25_split_equiv/})/compare_result.filtered.txt || true; echo "compare $r"; done
# C037 (frames with a returned tarball only)
for fr in aIWO_bulk_s1_melt_3000K aIWO_bulk_s1_quenched_300K aIWO_bulk_s1_final aIO_bulk_s1_quenched_300K aIO_bulk_s1_final aIWO_0p7_s1_final; do
  v=val/$fr; mkdir -p $O/C037/$fr $T/y/$fr; sha256sum $v/val_results.tar.gz; tar xzf $v/val_results.tar.gz -C $T/y/$fr
  f=$(find $T/y/$fr -name scf.out | head -1); echo "member $fr $(sha256sum $f | cut -c1-64)"
  allow $f $O/C037/$fr/scf.allow.txt; cp $v/scf.in $v/mace_ref.json $O/C037/$fr/; done
cp val/val_jobs.txt $O/C037/
rm -rf $T/x $T/y
echo "### allowlist line counts"; find $O -name scf.allow.txt -exec wc -l {} \;
echo "### BEGIN TAR"; tar czf - -C $O . | base64 -w 0; echo; echo "### END TAR"
rm -rf $T
