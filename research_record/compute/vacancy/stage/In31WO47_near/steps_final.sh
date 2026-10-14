steps() {
  # H-L k-point check (A17): one SCF at k 4x4x4 on the relaxed geometry of the last RELAX segment; no pp.x / projwfc.x.
  # relax.out is the converged segment's output (FINAL runs only after RELAX exit 0 = CONVERGED).
  python qeio.py converged relax.out || { log "relax.out has no final coordinates: FINAL SCF not run"; return 0; }
  python qeio.py newgeom final.tmpl relax.out > scf.in
  run_pw scf 1 || return 0
}
