steps() {
  run_pw vcrelax 4
  python qeio.py converged vcrelax.out || { log "relaxation did not finish; later steps skipped"; return 0; }
  for t in scf bands; do python qeio.py newgeom $t.tmpl vcrelax.out > $t.in; done
  clean_tmp
  run_pw scf 4 || return 0
  run_ppavg slab "$JOB" 4.8689
  run_pw bands 16
}
