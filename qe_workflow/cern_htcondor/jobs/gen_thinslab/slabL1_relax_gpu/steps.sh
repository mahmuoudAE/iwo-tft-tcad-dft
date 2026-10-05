steps() {
  run_pw vcrelax 1
  python qeio.py converged vcrelax.out || { log "relaxation did not finish; later steps skipped"; return 0; }
  for t in scf bands; do python qeio.py newgeom $t.tmpl vcrelax.out > $t.in; done
  clean_tmp
  export FORCE_CPU=1   # one QE version (CPU 7.5) for SCF, pp.x, projwfc.x and bands; one pool (NCPU may be odd)
  run_pw scf 1 || return 0
  run_ppavg slab "$JOB" 4.8689
  run_pdos slab "$JOB" "$(python qeio.py fermi scf.out)" 1
  run_pw bands 1
}
