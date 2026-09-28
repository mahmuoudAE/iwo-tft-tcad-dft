#!/bin/bash
# ONE-TIME SETUP on lxplus (NOT RUN YET; run only after approval).
# Builds a Quantum ESPRESSO 7.5 conda environment on the node's local /tmp (the 2 GB AFS home is too small),
# packs it with conda-pack into one relocatable archive, and stores that archive on EOS (1 TB quota),
# from where every HTCondor job copies and unpacks it. The /tmp build is removed afterwards.
set -euo pipefail
BUILD=/tmp/$USER-qe-build
DEST=/eos/user/${USER:0:1}/$USER/qe
conda create -y -p "$BUILD" -c conda-forge --override-channels qe=7.5 openmpi conda-pack
"$BUILD/bin/pw.x" -h 2>/dev/null | head -1 || true
mkdir -p "$DEST"
"$BUILD/bin/conda-pack" -p "$BUILD" -o "$DEST/qe-7.5-env.tar.gz" --ignore-missing-files
ls -lh "$DEST/qe-7.5-env.tar.gz"
rm -rf "$BUILD"
