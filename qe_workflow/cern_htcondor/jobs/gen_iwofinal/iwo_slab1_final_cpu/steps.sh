steps() {
  clean_tmp
  export FORCE_CPU=1   # one QE version (CPU 7.5) for SCF, pp.x and projwfc.x; one pool (NCPU may be odd)
  run_pw scf 1 || return 0
  run_ppavg slab "$JOB" 4.8833
  run_pdos slab "$JOB" "$(python qeio.py fermi scf.out)" 1
  run_pw bands 1
}
