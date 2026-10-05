steps() {
  run_pw scf 2 || return 0
  run_ppavg slab "$JOB" 4.8745
  run_pdos slab "$JOB" "$(python qeio.py fermi scf.out)" 2
}
