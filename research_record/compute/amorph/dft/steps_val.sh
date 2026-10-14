steps() {
  NKP=1; for p in 4 2; do [ $((NCPU % p)) -eq 0 ] && { NKP=$p; break; }; done
  run_pw scf $NKP
}
