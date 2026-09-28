#!/bin/bash
# HTCondor worker script for the small Quantum ESPRESSO test (bcc W, 1 atom).
# QE comes from a relocatable conda environment packed with conda-pack and stored on EOS (see ../setup_qe_pack.sh).
# The package is copied to the job's scratch directory, unpacked, and pw.x runs with MPI inside the allocated slot.
set -euo pipefail
PACK_EOS=/eos/user/m/melrashe/qe/qe-7.5-env.tar.gz
cd "${_CONDOR_SCRATCH_DIR:-$PWD}"
echo "host $(hostname)  start $(date -u +%FT%TZ)"
# CPUs allocated to this job (from the job ClassAd); fall back to nproc
NCPU=$(awk -F' = ' '/^RequestCpus/{print $2}' "${_CONDOR_JOB_AD:-/dev/null}" 2>/dev/null || true); NCPU=${NCPU:-$(nproc)}
echo "allocated CPUs: $NCPU"
# fetch the packed environment: XRootD first, FUSE mount as fallback
xrdcp -s "root://eosuser.cern.ch/${PACK_EOS}" qe-env.tar.gz 2>/dev/null || cp "$PACK_EOS" qe-env.tar.gz
mkdir -p qe-env && tar -xzf qe-env.tar.gz -C qe-env
set +u   # the conda-pack activate script reads unset variables (CONDA_PREFIX); strict mode is restored afterwards
source qe-env/bin/activate && conda-unpack
set -u
touch w_bcc.out   # ensures the output file exists for transfer even if pw.x fails
export OMP_NUM_THREADS=1
pw.x -h 2>/dev/null | head -1 || true
mpirun -np "$NCPU" --bind-to none pw.x -in w_bcc.in > w_bcc.out 2>&1
grep -E '^!|convergence has been achieved|PWSCF.*WALL' w_bcc.out || true
rm -rf qe-env qe-env.tar.gz tmp
echo "end $(date -u +%FT%TZ)"
