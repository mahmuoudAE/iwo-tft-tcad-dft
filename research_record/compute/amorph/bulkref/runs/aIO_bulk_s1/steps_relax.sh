steps() {
  # PILOT A15 (aIO_0p8_s1 only; register A15, user go 2026-10-11). Repaired classification:
  #   any SCF not converged                      -> FAILED   (node exit 2: the DAG does not replay it)
  #   relaxation finished ('bfgs converged')     -> CONVERGED (exit 0)
  #   >= 1 new electronically validated geometry -> CONTINUE  (exit 1) from the lowest-energy validated geometry
  #   otherwise                                  -> FAILED   (exit 2)
  # A19 (2026-10-11): CONVERGED needs QE's 'bfgs converged'. QE also prints 'Begin/End final coordinates' after a
  # BFGS failure; that case falls through to the CONTINUE / FAILED rules (geomsel.py).
  run_pw relax 1
  SUMMARY=$(python geomsel.py relax.in relax.out 2>&1)
  echo "$SUMMARY" > SEGMENT_SUMMARY
  log "geomsel: $SUMMARY"
  if grep -q 'convergence NOT achieved' relax.out; then
    echo FAILED > RELAX_STATUS
  elif grep -q 'bfgs converged' relax.out && python qeio.py converged relax.out; then   # A19
    python qeio.py newgeom relax.in relax.out > relax_conv.in && mv relax_conv.in relax.in && echo CONVERGED > RELAX_STATUS
  elif [ -s relax_next.in ] && grep -q 'best_new=yes' SEGMENT_SUMMARY; then
    cp relax_next.in relax.in && echo CONTINUE > RELAX_STATUS
  else
    echo FAILED > RELAX_STATUS
  fi
  rm -f relax_next.in
  log "relax status: $(cat RELAX_STATUS)"
}
