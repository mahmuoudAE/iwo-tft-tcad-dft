# production-size timing of export_tables (D-24 v2) on a synthetic 414-atom, 1928-band, 1-k projection set, in /tmp
D=/tmp/d24f_scale; cd $D || exit 1; rm -rf tmp *.dat projwfc_final.out
/usr/bin/time -f "gen: %e s, max RSS %M kB" nice -n 19 timeout 1200 python3 gen_synth.py $D 1
ls -la tmp/slab.save
/usr/bin/time -f "export_tables: %e s, max RSS %M kB" nice -n 19 timeout 1200 bash -c 'python() { python3 "$@"; }; JOB=final; source ./steps_final.sh.D24; export_tables tmp/slab.save final' > tables.out 2> time.err
cat time.err; grep -E 'proj_atoms|consistency|atomic_proj_(k|bands|wfc)|projwfc_map' export_checks_final.dat
echo "proj_atoms_final.dat: $(grep -vc '^#' proj_atoms_final.dat) rows, $(stat -c %s proj_atoms_final.dat) B, gz $(gzip -c proj_atoms_final.dat | wc -c) B"
head -9 proj_atoms_final.dat | cut -c1-200
rm -rf $D/tmp
