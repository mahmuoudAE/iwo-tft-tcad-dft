SP=/mnt/c/Users/moham/AppData/Local/Temp/claude/C--Users-moham-Downloads-IWO-Local-Codex-Handoff--1--IWO-ATLAS-Model-claude/7c34fe97-c389-4002-8f70-9615a643e20b/scratchpad/d24f/test
D=~/d24f_test/r_ok; X=~/d24f_test/check_ok; rm -rf $X; mkdir -p $X; tar xzf $D/final_results.tar.gz -C $X
echo "AFS tarball members: $(tar tzf $D/final_results.tar.gz | tr '\n' ' ')"
echo "proj_atoms_final.dat: $(stat -c %s $X/proj_atoms_final.dat) B, gz $(gzip -c $X/proj_atoms_final.dat | wc -c) B, rows $(grep -vc '^#' $X/proj_atoms_final.dat)"
~/miniforge3/envs/qe/bin/python -I $SP/check_tables.py $X ~/d24f_test/replay_src/atomic_proj.xml 1
echo "fail-mode table identical to ok-mode table: $(tar xzf ~/d24f_test/r_fail/final_results.tar.gz -O proj_atoms_final.dat | cmp -s - $X/proj_atoms_final.dat && echo yes || echo NO)"
