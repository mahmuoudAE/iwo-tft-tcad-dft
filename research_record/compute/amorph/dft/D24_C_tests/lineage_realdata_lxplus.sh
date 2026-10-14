# lineage_relax.sh v2 on COPIES of two real run directories (pre-item-B segments, real EOS checkpoints read-only)
L=/tmp/d24f_lin; rm -rf $L/runs $L/eos; mkdir -p $L/runs $L/eos
for r in aIO_0p7_s1 aIO_2p0_s1; do mkdir -p $L/runs/$r/logs
  cp -p ~/iwo_amorph/runs/$r/relax_s*_results.tar.gz ~/iwo_amorph/runs/$r/relax.in ~/iwo_amorph/runs/$r/RELAX_STATUS ~/iwo_amorph/runs/$r/relax.in.pre_* $L/runs/$r/
  cp -p ~/iwo_amorph/runs/$r/logs/relax* $L/runs/$r/logs/; done
echo "### aIO_0p7_s1 (--to-eos into /tmp)"; RUNS=$L/runs EXPORT_EOS=$L/eos bash $L/lineage_relax.sh aIO_0p7_s1 --to-eos; echo "exit $?"
ls -la $L/eos/aIO_0p7_s1/relax_segments
echo "### aIO_2p0_s1"; RUNS=$L/runs bash $L/lineage_relax.sh aIO_2p0_s1; echo "exit $?"
echo "### live run dirs untouched: $(ls ~/iwo_amorph/runs/aIO_0p7_s1/lineage_relax.dat ~/iwo_amorph/runs/aIO_2p0_s1/lineage_relax.dat 2>&1 | grep -c 'No such')/2 without lineage_relax.dat"
