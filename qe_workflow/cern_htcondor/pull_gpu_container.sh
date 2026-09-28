#!/bin/bash
# Pull NVIDIA's GPU build of Quantum ESPRESSO (NGC, user-approved 2026-09-28) into EOS as a SIF image.
# Runs on lxplus in the background; log: /eos/user/m/melrashe/qe/pull_qe_gpu.log
S="ssh -o BatchMode=yes -o ControlPath=$HOME/.ssh/cm-cern melrashe@lxplus.cern.ch"
$S 'bash -s' <<'EOF'
D=/eos/user/m/melrashe/qe
cat > /tmp/$USER-pull.sh <<'IN'
export APPTAINER_CACHEDIR=/tmp/$USER-apptainer-cache APPTAINER_TMPDIR=/tmp/$USER-apptainer-tmp
mkdir -p $APPTAINER_CACHEDIR $APPTAINER_TMPDIR
D=/eos/user/m/melrashe/qe
echo "start $(date -u +%FT%TZ) on $(hostname)"
apptainer pull /tmp/$USER-qe-7.3.1-gpu.sif docker://nvcr.io/hpc/quantum_espresso:qe-7.3.1 && \
  cp /tmp/$USER-qe-7.3.1-gpu.sif $D/qe-7.3.1-gpu.sif && ls -la $D/qe-7.3.1-gpu.sif && \
  apptainer exec $D/qe-7.3.1-gpu.sif bash -c 'which pw.x; ls /usr/local/qe* 2>/dev/null | head -3; nvcc --version 2>/dev/null | tail -1'
rm -rf /tmp/$USER-qe-7.3.1-gpu.sif $APPTAINER_CACHEDIR $APPTAINER_TMPDIR
echo "PULL DONE $(date -u +%FT%TZ)"
IN
nohup bash /tmp/$USER-pull.sh > $D/pull_qe_gpu.log 2>&1 < /dev/null &
echo "pull started on $(hostname), pid $!"
EOF
