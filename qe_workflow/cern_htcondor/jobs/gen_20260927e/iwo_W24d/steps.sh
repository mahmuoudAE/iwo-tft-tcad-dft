steps() {
  run_pw relax 8
  python qeio.py converged relax.out || { log "relaxation did not finish; later steps skipped"; return 0; }
  for t in scf_k4 bands spin_k3; do python qeio.py newgeom $t.tmpl relax.out > $t.in; done
  clean_tmp
  run_pw scf_k4 16 || return 0
  run_pdos iwo "$JOB" "$(python qeio.py fermi scf_k4.out)" 16
  run_pw bands 16
  clean_tmp
  run_pw spin_k3 16
}
