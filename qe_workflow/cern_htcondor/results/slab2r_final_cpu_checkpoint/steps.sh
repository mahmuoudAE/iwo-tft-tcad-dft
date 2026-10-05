steps() {
  run_pw scf 2 || return 0
  run_ppavg slab "$JOB" 4.8745
  run_pw bands 4
}
