#!/bin/bash
# install_D24.sh v2 on a fake ~/iwo_amorph tree (stub condor_q): dry run, apply, re-apply, guards
SP=/mnt/c/Users/moham/AppData/Local/Temp/claude/C--Users-moham-Downloads-IWO-Local-Codex-Handoff--1--IWO-ATLAS-Model-claude/7c34fe97-c389-4002-8f70-9615a643e20b/scratchpad
ST=$SP/d24f/stage; O=$SP/d24/cern_orig
T=~/d24f_test/fake_root; rm -rf $T; mkdir -p $T/common $T/runs $T/bin
cp $O/steps_final.sh $O/final_node.sh $T/common/; cp $ST/common/*.D24 $T/common/; cp $ST/install_D24.sh $T/
RUNS="aIO_0p7_s1 aIO_1p0_s1 aIO_1p5_s1 aIO_2p0_s1 aIO_2p0_s2 aIWO_0p7_s1 aIWO_0p7_s1_bare aIWO_0p8_s2 aIWO_1p0_Al2O3_s2 aIWO_1p0_s1 aIWO_1p5_s1 aIWO_2p0_Al2O3_s2 aIWO_2p0_comp_s1 aIWO_2p0_s1 aIWO_2p0_s1_bare aIWO_2p0_s2 aIO_0p8_s1"
for r in $RUNS; do mkdir -p $T/runs/$r; cp $O/steps_final.sh $T/runs/$r/; cp $O/final.tmpl.aIWO_2p0_s1 $T/runs/$r/final.tmpl
  [ $r = aIO_0p8_s1 ] || { cp $ST/common/steps_final.sh.D24 $T/runs/$r/; sed "s/verbosity = 'low'/verbosity = 'high'/" $T/runs/$r/final.tmpl > $T/runs/$r/final.tmpl.D24; }; done
for b in aIO_bulk_s1 aIWO_bulk_s1; do mkdir -p $T/runs/$b; cp $O/steps_final.sh $T/runs/$b/; sed "s/verbosity = 'low'/verbosity = 'high'/" $O/final.tmpl.aIWO_2p0_s1 > $T/runs/$b/final.tmpl; done
q() { printf '#!/bin/bash\n%s\n' "$1" > $T/bin/condor_q; chmod +x $T/bin/condor_q; }
q 'echo "aIWO_2p0_s1_relax_s0 2"; echo "val_aIWO_2p0_s1_final 2"'
export PATH=$T/bin:$PATH IWO_ROOT=$T
snap() { (cd $T && find . -type f -not -path "./bin/*" | sort | xargs sha256sum); }
snap > /tmp/d24f_before.txt
echo "### dry run (a val_*_final job runs: allowed)"; bash $T/install_D24.sh | tail -5; snap > /tmp/d24f_after.txt; cmp -s /tmp/d24f_before.txt /tmp/d24f_after.txt && echo "dry run changed nothing ($(wc -l < /tmp/d24f_after.txt) files compared)"
echo "### apply (+ 2 bulk dirs)"; bash $T/install_D24.sh --apply aIO_bulk_s1 aIWO_bulk_s1 | tail -3; echo "exit ${PIPESTATUS[0]}"
cd $T
echo "pre_D24 backups: $(find . -name '*.pre_D24' | wc -l) (expected 1 common steps + 16 steps + 16 tmpl + 2 bulk steps + final_node = 36)"
cmp runs/aIWO_2p0_s1/steps_final.sh common/steps_final.sh.D24 && cmp runs/aIO_bulk_s1/steps_final.sh common/steps_final.sh.D24 && echo "run + bulk steps = D24"
cmp common/final_node.sh common/final_node.sh.D24 && [ -x common/final_node.sh ] && echo "final_node.sh = D24, executable"
cmp common/export_pull.sh common/export_pull.sh.D24 && cmp common/lineage_relax.sh common/lineage_relax.sh.D24 && echo "export_pull.sh, lineage_relax.sh installed"
diff runs/aIWO_2p0_s1/final.tmpl.pre_D24 runs/aIWO_2p0_s1/final.tmpl
cmp runs/aIO_0p8_s1/steps_final.sh $O/steps_final.sh && grep -c "verbosity = 'low'" runs/aIO_0p8_s1/final.tmpl && echo "pilot untouched"
echo "### re-apply (idempotent)"; bash $T/install_D24.sh --apply | grep -v 'already' | tail -3; echo "exit ${PIPESTATUS[0]}"
echo "### guard: a slab FINAL running"; q 'echo "aIWO_2p0_s1_final 2"'; bash $T/install_D24.sh --apply; echo "exit $?"
echo "### guard: condor_q fails"; q 'echo "Failed to fetch ads" >&2; exit 1'; bash $T/install_D24.sh --apply; echo "exit $?"
echo "### guard: live files changed after staging"; q 'true'
cp runs/aIWO_2p0_s1/steps_final.sh.pre_D24 runs/aIWO_2p0_s1/steps_final.sh; echo "# edit" >> runs/aIWO_2p0_s1/steps_final.sh
cp common/final_node.sh.pre_D24 common/final_node.sh; echo "# edit" >> common/final_node.sh
echo "# local edit" >> common/export_pull.sh
bash $T/install_D24.sh --apply | grep -iE 'unexpected|left alone|done'; echo "exit ${PIPESTATUS[0]}"
echo "### pilot only when named"; q 'true'; cp $O/final_node.sh common/final_node.sh; bash $T/install_D24.sh --apply aIO_0p8_s1 | grep aIO_0p8_s1; cmp runs/aIO_0p8_s1/steps_final.sh common/steps_final.sh.D24 && echo "pilot steps = D24 when named"
