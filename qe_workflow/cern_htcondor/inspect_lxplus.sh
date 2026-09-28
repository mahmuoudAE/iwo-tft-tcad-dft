#!/bin/bash
# Read-only inspection of the lxplus environment (no files are created or changed remotely).
t() { timeout "$@"; }
echo "== host"; hostname; whoami; cat /etc/redhat-release 2>/dev/null; uname -r; echo "cores: $(nproc)"; free -g | sed -n 1,2p
echo "== Quantum ESPRESSO"
command -v pw.x || echo "pw.x: not in PATH"
command -v module >/dev/null 2>&1 && (t 30 module avail 2>&1 | grep -i -E 'espresso|quantum|qe/' | head) || echo "environment modules: not available"
echo "LCG releases mentioning espresso/quantum:"; t 60 ls /cvmfs/sft.cern.ch/lcg/releases 2>/dev/null | grep -i -E 'espresso|quantum' | head || true
echo "container runtime:"; command -v apptainer singularity 2>/dev/null; t 20 apptainer --version 2>/dev/null
echo "conda/mamba in PATH:"; command -v conda mamba micromamba 2>/dev/null || echo "none"
echo "compilers/MPI in PATH:"; command -v gfortran mpirun 2>/dev/null || echo "none"
echo "== storage"; echo "HOME=$HOME"
t 20 fs listquota "$HOME" 2>/dev/null
W=/afs/cern.ch/work/${USER:0:1}/$USER; if [ -d "$W" ]; then echo "AFS workspace $W:"; t 20 fs listquota "$W"; else echo "AFS workspace: not present ($W)"; fi
E=/eos/user/${USER:0:1}/$USER; if [ -d "$E" ]; then echo "EOS home $E present"; t 30 eos root://eosuser.cern.ch quota "$E/" 2>/dev/null | head -15; else echo "EOS home: not present"; fi
df -h /tmp | tail -1
echo "== HTCondor"
t 20 condor_version | head -1
t 30 condor_q 2>&1 | tail -4
echo "slot sizes on the pool (count, Cpus, Memory MB) of partitionable slots:"
t 90 condor_status -constraint 'PartitionableSlot =?= true' -af TotalSlotCpus TotalSlotMemory 2>/dev/null | sort | uniq -c | sort -rn | head -12
echo "configured flavour / runtime settings visible to the user:"
t 30 condor_config_val -dump 2>/dev/null | grep -i -E 'flavour|maxruntime|max_jobs_submitted|max_jobs_per_owner' | head -20
