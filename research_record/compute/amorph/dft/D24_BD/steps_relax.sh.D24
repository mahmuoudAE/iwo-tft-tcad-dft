steps() {
  # D-24 (user go 2026-10-11): repaired continuation for the 16 slab chains, the same classification as the A15 pilot
  # (aIO_0p8_s1; geomsel.py is byte-identical to the pilot's):
  #   any SCF not converged ('convergence NOT achieved')          -> FAILED
  #   relaxation finished ('bfgs converged' + final coordinates)   -> CONVERGED, relax.in = final geometry (A19)
  #   >= 1 new electronically validated geometry                   -> CONTINUE from the lowest-energy validated geometry
  #   anything else (no or empty relax.out, no new validated one)  -> FAILED
  # Validated = its SCF converged ('!' energy). It is a fresh-BFGS restart point, not necessarily an accepted BFGS step
  # (Codex, 2026-10-10). QE also prints final coordinates after a BFGS failure; such a run falls through to the
  # CONTINUE / FAILED rules and never restarts from an unevaluated trial geometry.
  # These DAGs have no UNLESS-EXIT, so FAILED also writes 'FAILED <utc> <job> [<category>]: <reason>' into
  # segment_guard; the shared relax_node.sh then stops every later retry of the chain within seconds (reset:
  # ~/iwo_amorph/common/README_D24_BD.txt). Categories: scf (SCF not converged), infra (no or empty relax.out, or a GPU
  # memory / CUDA error in it), early (pw.x stopped before its first SCF energy for another reason), noprogress (SCF
  # energies, but no new validated geometry), parse (final geometry not extractable).
  # Lineage (A14), packed with the segment (*.in, *.log): ${JOB}_input.in = this segment's own input,
  # ${JOB}_lineage.log = status, reason and selection; on FAILED the lowest-energy validated geometry, if any,
  # is kept as ${JOB}_bestvalid.in for a manual resume.
  run_pw relax 1
  cp relax.in "${JOB}_input.in"
  rm -f relax_next.in relax_conv.in
  local summary st=FAILED why="" cat=""
  if [ -s relax.out ]; then summary=$(python geomsel.py relax.in relax.out 2>&1 | tr '\n' ' '); else summary="no relax.out"; fi
  if [ ! -s relax.out ]; then
    why="relax.out missing or empty"; cat=infra
  elif grep -q 'convergence NOT achieved' relax.out; then
    why="SCF not converged ($(grep -c 'convergence NOT achieved' relax.out)x)"; cat=scf
  elif grep -q 'bfgs converged' relax.out && python qeio.py converged relax.out; then
    if python qeio.py newgeom relax.in relax.out > relax_conv.in && grep -q ATOMIC_POSITIONS relax_conv.in; then
      mv relax_conv.in relax.in; st=CONVERGED
    else
      why="bfgs converged, but the final geometry could not be extracted"; cat=parse
    fi
  elif [ -s relax_next.in ] && [[ "$summary" == *best_new=yes* ]]; then
    cp relax_next.in relax.in; st=CONTINUE
  else
    why="no new electronically validated geometry"
    if grep -q -E 'Out of memory allocating|CUDA_ERROR|cudaError|Accelerator Fatal Error' relax.out; then
      cat=infra; why="$why; GPU memory / CUDA error: $(grep -m1 -o -E 'Out of memory allocating|CUDA_ERROR[A-Z_]*|cudaError[A-Za-z]*|Accelerator Fatal Error' relax.out)"
    elif ! grep -q '^!' relax.out; then
      cat=early; why="$why; pw.x stopped before its first SCF energy"
    else
      cat=noprogress
    fi
  fi
  echo "$st" > RELAX_STATUS
  if [ "$st" = FAILED ]; then
    [ -s relax_next.in ] && cp relax_next.in "${JOB}_bestvalid.in"
    echo "FAILED $(date -u +%FT%TZ) ${JOB} [${cat}]: ${why}; geomsel: ${summary}" > segment_guard
  fi
  {
    echo "segment ${JOB}: ${st}${cat:+ [${cat}]}${why:+ (${why})}"
    echo "geomsel: ${summary}"
    echo "geomsel.py md5 $(md5sum < geomsel.py | cut -c1-32)"
    echo "positions md5: input $(d24_posmd5 "${JOB}_input.in")  next relax.in $(d24_posmd5 relax.in)"
  } > "${JOB}_lineage.log"
  rm -f relax_next.in relax_conv.in
  log "relax status: ${st}${cat:+ [${cat}]}${why:+ (${why})}; geomsel: ${summary}"
}

d24_posmd5() {   # md5 (12 chars) of the ATOMIC_POSITIONS rows: segment k's 'next' equals segment k+1's 'input'
  awk '/^[ \t]*ATOMIC_POSITIONS/{f=1; next} f && NF >= 4 && $1 ~ /^[A-Z][a-z]?[0-9]*$/ {print $1, $2, $3, $4; next} f {f=0}' "$1" \
    | md5sum | cut -c1-12
}
