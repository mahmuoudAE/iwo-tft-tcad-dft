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

# checkpoint: copy the outputs so far to EOS after every step, so a job removed at the wall-time limit
# still leaves its finished steps (slab2_v25 lost 16 h of SCF this way on 2026-09-28)
CLUSTER=$(awk -F' = ' '/^ClusterId/{print $2}' "${_CONDOR_JOB_AD:-/dev/null}" 2>/dev/null || true)
CKPT_EOS=/eos/user/m/melrashe/qe/checkpoints
checkpoint() {
  [ -n "${QE_LOCAL:-}" ] && return 0
  pack > /dev/null 2>&1
  xrdcp -f -s "${JOB}_results.tar.gz" "root://eosuser.cern.ch/${CKPT_EOS}/${JOB}_${CLUSTER:-0}.tar.gz" 2>/dev/null \
    || cp -f "${JOB}_results.tar.gz" "${CKPT_EOS}/${JOB}_${CLUSTER:-0}.tar.gz" 2>/dev/null || true
}

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
# one thread per MPI rank. HTCondor at CERN sets OMP/OPENBLAS/MKL_NUM_THREADS = RequestCpus in the job
# environment; OpenBLAS then started 64 threads in each of 64 ranks (measured 65 threads per pw.x,
# node load > 1000) and the first production jobs ran 17-30x slower (2026-09-27)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_THREAD_LIMIT=1
log "pw.x:$(command -v pw.x)  python: $(command -v python)"

# GPU mode (RequestGPUs > 0): pw.x from NVIDIA's QE 7.3.1 GPU container (NGC, on EOS), one MPI rank per GPU,
# the remaining CPUs as OpenMP threads; post-processing (pp.x, projwfc.x, python) stays on the CPU environment
NGPU=$(awk -F' = ' '/^RequestGPUs/{print $2}' "${_CONDOR_JOB_AD:-/dev/null}" 2>/dev/null || true); NGPU=${NGPU:-0}
SIF_EOS=/eos/user/m/melrashe/qe/qe-7.3.1-gpu.sif
if [ "$NGPU" -gt 0 ] 2>/dev/null; then
  xrdcp -s "root://eosuser.cern.ch/${SIF_EOS}" qe-gpu.sif 2>/dev/null || cp "$SIF_EOS" qe-gpu.sif
  log "GPU mode: $NGPU GPU(s), $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null | head -1)"
fi
pw_cmd() {   # pw_cmd <npool> <input>
  # FORCE_CPU=1: run on the CPU environment even in a GPU job (final SCF + pp.x/projwfc.x must share one QE
  # version: CPU pp.x aborted on the GPU 7.3.1 save of slab1_relax_gpu, 2026-09-29)
  if [ "$NGPU" -gt 0 ] 2>/dev/null && [ -z "${FORCE_CPU:-}" ]; then
    # UCX restricted to shared memory + CUDA: on b9pgpun00x nodes UCX tried InfiniBand, failed to lock memory
    # (ulimit -l 8 MB) and wrote the same error endlessly (324 GB relax.out, GPU idle; 2026-09-30)
    OMP_NUM_THREADS=$(( NCPU / NGPU )) UCX_TLS=self,sm,cuda_copy,cuda_ipc apptainer exec --nv -B "$PWD" --pwd "$PWD" qe-gpu.sif \
      /usr/local/openmpi/bin/mpirun --allow-run-as-root -np "$NGPU" --bind-to none -x OMP_NUM_THREADS -x UCX_TLS /usr/local/qe/bin/pw.x -nk "$NGPU" -in "$2"
  else
    mpirun -np "$NCPU" $MPIOPT pw.x -nk "$1" -in "$2"
  fi
}

# run_pw <name> <npool>: runs <name>.in; max_seconds is set so that pw.x stops cleanly before the wall-time limit
run_pw() {
  local rem=$(( DEADLINE - $(date +%s) - 1800 ))
  if [ "$rem" -lt 3600 ]; then log "skip $1: only ${rem}s left"; return 1; fi
  sed -i "s/max_seconds = [0-9.d]*/max_seconds = $rem/" "$1.in"
  log "pw.x $1 start (-nk $2, max_seconds $rem)"
  pw_cmd "$2" "$1.in" > "$1.out" 2>&1 &
  local pid=$!
  while kill -0 "$pid" 2>/dev/null; do   # runaway guard: an output file above 2 GB means a looping error
    sleep 60
    if [ "$(stat -c %s "$1.out" 2>/dev/null || echo 0)" -gt 2000000000 ]; then
      log "$1.out exceeded 2 GB: runaway output, pw.x stopped"; pkill -P "$pid"; kill "$pid"
      head -c 20000 "$1.out" > "$1.out.head"; tail -c 20000 "$1.out" > "$1.out.tail"; : > "$1.out"; break
    fi
  done
  wait "$pid"
  log "pw.x $1 end rc=$? $(grep 'PWSCF.*WALL' "$1.out" | tail -1 | sed 's/^ *//')"
  checkpoint
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
  checkpoint
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
  checkpoint
}

clean_tmp() { rm -rf tmp; }

source ./steps.sh
steps
log "steps finished after $(( $(date +%s) - START )) s"
rm -rf qe-env tmp qe-gpu.sif
