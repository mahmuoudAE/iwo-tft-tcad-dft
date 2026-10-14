steps() {
  python qeio.py newgeom final.tmpl relax.in > scf.in
  NKP=1; for p in 4 3 2; do [ $((NCPU % p)) -eq 0 ] && { NKP=$p; break; }; done
  log "pools: $NKP (NCPU $NCPU)"
  export FORCE_CPU=1   # one QE version (CPU 7.5) for scf, pp.x and projwfc.x
  run_pw scf $NKP || return 0
  run_ppavg slab "$JOB" 4.0
  run_pdos slab "$JOB" "$(python qeio.py fermi scf.out)" $NKP
}
