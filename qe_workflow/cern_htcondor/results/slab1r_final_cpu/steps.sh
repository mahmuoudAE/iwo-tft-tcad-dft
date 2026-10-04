steps() {
  run_pw scf 4 || return 0
  run_ppavg slab "$JOB" 4.8833
  run_pw bands 4
}
