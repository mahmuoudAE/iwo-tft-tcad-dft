steps() {
  # A23 (ii)/(iii): one NC (SG15) single point, TAG = pbe | hse (exported by nc_node.sh), then projwfc.x.
  # CPU only (QE 7.5 conda env): the QE 7.3.1 GPU container has no projwfc.x, and the HDF5 QE 7.5 cannot read the
  # container's wfc*.dat; one QE version for pw.x and projwfc.x, as the slab finals (FORCE_CPU).
  export FORCE_CPU=1
  local T=${NC_TAG:?NC_TAG not set}
  log "NC single point $T: pools ${NC_POOLS:-1} (EXX: 1 pool, exxbuff is replicated per pool)"
  run_pw "scf_$T" "${NC_POOLS:-1}" || { log "scf_$T did not finish: no projwfc"; return 0; }
  # projection basis: the PP_CHI copies (pseudo_proj/, add_chi.py) replace the pristine SG15 files AFTER pw.x, in the
  # save and in the scratch pseudo dir (whichever projwfc.x reads); pw.x itself ran with the pristine files
  local f
  for f in pseudo_proj/*.upf; do
    cp -f "$f" "tmp/$T.save/$(basename "$f")"
    cp -f "$f" "pseudo/$(basename "$f")"
  done
  # projwfc.x reads natomwfc from data-file-schema.xml (0 with the pristine SG15 files): recompute it from the copies
  python set_natomwfc.py "tmp/$T.save" >> "${JOB}_driver.log" 2>&1 || log "set_natomwfc.py failed"
  local EF
  EF=$(python qeio.py fermi "scf_$T.out")
  run_pdos "$T" "$T" "$EF" 1
  log "projwfc $T: $(grep -c 'state #' "projwfc_$T.out" 2>/dev/null) atomic states, $(grep -m1 -i 'spilling' "projwfc_$T.out" 2>/dev/null)"
  cp -f "tmp/$T.save/atomic_proj.xml" "atomic_proj_$T.xml" 2>/dev/null || log "no atomic_proj.xml"
  cp -f "tmp/$T.save/data-file-schema.xml" "data-file-schema_$T.xml" 2>/dev/null || log "no data-file-schema.xml"
  # A14 export: projections, eigenvalues/occupations/k-weights, inputs and logs to EOS next to the checkpoints
  tar czf "${JOB}_proj.tar.gz" "atomic_proj_$T.xml" "data-file-schema_$T.xml" "projwfc_$T.out" "scf_$T.in" \
    "scf_$T.out" "projwfc_$T.in" 2>/dev/null
  xrdcp -f -s "${JOB}_proj.tar.gz" "root://eosuser.cern.ch/${CKPT_EOS}/${JOB}_proj_${CLUSTER:-0}.tar.gz" 2>/dev/null \
    || cp -f "${JOB}_proj.tar.gz" "${CKPT_EOS}/${JOB}_proj_${CLUSTER:-0}.tar.gz" 2>/dev/null || log "EOS export failed"
  checkpoint
}
