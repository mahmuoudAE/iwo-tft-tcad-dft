steps() {
  # 2026-10-05: faster copy of STEPS_THIN_SLAB. Pools chosen at run time from the CPUs actually granted (CERN sizes
  # jobs by memory; -nk must divide the rank count, see iwo_slab2_final_cpu); 4 irreducible k-points
  NKP=1; for p in 4 2; do [ $((NCPU % p)) -eq 0 ] && { NKP=$p; break; }; done
  log "pools for the CPU steps: $NKP (NCPU $NCPU)"
  run_pw vcrelax $NKP
  python qeio.py converged vcrelax.out || { log "relaxation did not finish; later steps skipped"; return 0; }
  for t in scf bands; do python qeio.py newgeom $t.tmpl vcrelax.out > $t.in; done
  clean_tmp
  export FORCE_CPU=1   # one QE version (CPU 7.5) for SCF, pp.x, projwfc.x and bands
  run_pw scf $NKP || return 0
  run_ppavg slab "$JOB" 4.8689
  run_pdos slab "$JOB" "$(python qeio.py fermi scf.out)" $NKP
  run_pw bands $NKP
}
