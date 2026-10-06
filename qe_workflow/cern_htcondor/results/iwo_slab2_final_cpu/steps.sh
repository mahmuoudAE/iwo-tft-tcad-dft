steps() {
  export FORCE_CPU=1   # one QE version (CPU 7.5) for SCF, pp.x and projwfc.x
  # one pool: CERN allocates CPUs by memory (100 GB -> 33 CPUs), and -nk 2 aborted on 33 ranks (2026-10-05)
  run_pw scf 1 || return 0
  run_ppavg slab "$JOB" 4.8745
  run_pdos slab "$JOB" "$(python qeio.py fermi scf.out)" 1
}
