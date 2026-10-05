steps() {
  export FORCE_CPU=1   # one QE version (CPU 7.5) for SCF, pp.x and projwfc.x
  run_pw scf 2 || return 0
  run_ppavg slab "$JOB" 4.8745
  run_pdos slab "$JOB" "$(python qeio.py fermi scf.out)" 2
}
