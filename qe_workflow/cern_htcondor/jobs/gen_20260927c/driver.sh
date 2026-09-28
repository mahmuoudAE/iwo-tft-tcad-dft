#!/bin/bash
# HTCondor worker driver for the IWO / In2O3 DFT jobs.
# Usage: driver.sh <job> <wall-time limit in s>
# Unpacks Quantum ESPRESSO (conda-pack archive on EOS), runs steps() from the job's steps.sh and always
# packs the outputs into <job>_results.tar.gz, even when a step fails.
# Local test mode: QE_LOCAL=<conda env>, NCPU_OVERRIDE=<n>, MPIOPT="--bind-to none --oversubscribe".
set -uo pipefail
JOB=$1
LIMIT=${2:-86400}
START=$(date +%s)
DEADLINE=$(( START + LIMIT ))
PACK_EOS=/eos/user/m/melrashe/qe/qe-7.5-env.tar.gz
# the slot's CPUs are hardware threads; PRRTE counts physical cores and refuses 32 ranks on a 32-CPU slot
# without :OVERSUBSCRIBE (first submission, 2026-09-27: all 32-CPU jobs stopped after 18 s)
MPIOPT=${MPIOPT:---bind-to none --map-by :OVERSUBSCRIBE}
cd "${_CONDOR_SCRATCH_DIR:-$PWD}" || exit 1
NCPU=$(awk -F' = ' '/^RequestCpus/{print $2}' "${_CONDOR_JOB_AD:-/dev/null}" 2>/dev/null || true)
NCPU=${NCPU_OVERRIDE:-${NCPU:-$(nproc)}}

log() { echo "[$(date -u +%FT%TZ)] $*" | tee -a "${JOB}_driver.log"; }

pack() {
  shopt -s nullglob
  local f=( *.out *.in *.tmpl *.dat *.log steps.sh pdos/* )
  tar czf "${JOB}_results.tar.gz" "${f[@]}"
  echo "packed ${#f[@]} files into ${JOB}_results.tar.gz"
}
trap pack EXIT

log "job $JOB host $(hostname) cpus $NCPU limit ${LIMIT}s"
if [ -n "${QE_LOCAL:-}" ]; then
  export PATH="$QE_LOCAL/bin:$PATH"
else
  xrdcp -s "root://eosuser.cern.ch/${PACK_EOS}" qe-env.tar.gz 2>/dev/null || cp "$PACK_EOS" qe-env.tar.gz
  mkdir -p qe-env && tar -xzf qe-env.tar.gz -C qe-env && rm -f qe-env.tar.gz
  set +u   # the conda-pack activate script reads unset variables
  source qe-env/bin/activate && conda-unpack
  set -u
fi
export OMP_NUM_THREADS=1
log "pw.x: $(command -v pw.x)  python: $(command -v python)"

# run_pw <name> <npool>: runs <name>.in; max_seconds is set so that pw.x stops cleanly before the wall-time limit
run_pw() {
  local rem=$(( DEADLINE - $(date +%s) - 1800 ))
  if [ "$rem" -lt 3600 ]; then log "skip $1: only ${rem}s left"; return 1; fi
  sed -i "s/max_seconds = [0-9.d]*/max_seconds = $rem/" "$1.in"
  log "pw.x $1 start (-nk $2, max_seconds $rem)"
  mpirun -np "$NCPU" $MPIOPT pw.x -nk "$2" -in "$1.in" > "$1.out" 2>&1
  log "pw.x $1 end rc=$? $(grep 'PWSCF.*WALL' "$1.out" | tail -1 | sed 's/^ *//')"
  if grep -q 'convergence NOT achieved' "$1.out"; then log "$1: SCF not converged"; return 1; fi
  grep -q 'JOB DONE' "$1.out"
}

# run_ppavg <prefix> <tag> <window in bohr>: planar and macroscopic average of the electrostatic potential along z
run_ppavg() {
  printf "&INPUTPP\n  prefix = '%s', outdir = './tmp', filplot = '%s_v.pp', plot_num = 11\n/\n" "$1" "$2" > "pp_$2.in"
  mpirun -np "$NCPU" $MPIOPT pp.x -in "pp_$2.in" > "pp_$2.out" 2>&1
  printf '1\n%s_v.pp\n1.0\n3000\n3\n%s\n' "$2" "$3" > "avg_$2.in"
  average.x < "avg_$2.in" > "avg_$2.out" 2>&1
  [ -f avg.dat ] && mv avg.dat "$2_avg.dat"
  log "planar average $2: $(wc -l < "$2_avg.dat" 2>/dev/null || echo 0) lines"
}

# run_pdos <prefix> <tag> <fermi eV> <npool>: projected density of states from E_F-8 eV to E_F+4 eV
run_pdos() {
  mkdir -p pdos
  local lo hi
  lo=$(awk -v e="$3" 'BEGIN{print e-8}'); hi=$(awk -v e="$3" 'BEGIN{print e+4}')
  printf "&PROJWFC\n  prefix = '%s', outdir = './tmp', filpdos = 'pdos/%s'\n  Emin = %s, Emax = %s, DeltaE = 0.01, degauss = 0.0073, ngauss = 0\n/\n" \
    "$1" "$2" "$lo" "$hi" > "projwfc_$2.in"
  mpirun -np "$NCPU" $MPIOPT projwfc.x -nk "$4" -in "projwfc_$2.in" > "projwfc_$2.out" 2>&1
  log "pdos $2: $(ls pdos | wc -l) files"
}

clean_tmp() { rm -rf tmp; }

source ./steps.sh
steps
log "steps finished after $(( $(date +%s) - START )) s"
rm -rf qe-env tmp
