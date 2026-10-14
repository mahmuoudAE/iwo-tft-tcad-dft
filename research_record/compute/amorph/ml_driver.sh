#!/bin/bash
# HTCondor worker: unpack the MACE environment from EOS, build one amorphous structure, return all outputs.
# usage: ml_driver.sh <name>     (needs spec_<name>.json and mace_amorph.py in the sandbox)
set -uo pipefail
NAME=$1
cd "${_CONDOR_SCRATCH_DIR:-$PWD}" || exit 1
log() { echo "[$(date -u +%FT%TZ)] $*" | tee -a "${NAME}_driver.log"; }
ENV_EOS=/eos/user/m/melrashe/iwo_amorph/env/mace-env.tar.gz
MODEL_EOS=/eos/user/m/melrashe/iwo_amorph/env/mace-mpa-0-medium.model
finish() { tar czf "${NAME}_ml.tar.gz" ${NAME}_* ${NAME}.xyz 2>/dev/null; log "packed $(tar tzf ${NAME}_ml.tar.gz 2>/dev/null | wc -l) files"; }
trap finish EXIT
log "host $(hostname) gpu: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)"
for f in ENV MODEL; do
  src_var="${f}_EOS"; dst=$([ $f = ENV ] && echo env.tar.gz || echo model.model)
  xrdcp -s "root://eosuser.cern.ch/${!src_var}" "$dst" 2>/dev/null || cp "${!src_var}" "$dst" || { log "cannot fetch ${!src_var}"; exit 3; }
done
mkdir -p env && tar -xzf env.tar.gz -C env && rm -f env.tar.gz
set +u; source env/bin/activate && conda-unpack; set -u
export OMP_NUM_THREADS=${OMP_NUM_THREADS_OVERRIDE:-4}
DEV=cpu; nvidia-smi -L >/dev/null 2>&1 && DEV=cuda
log "device $DEV; python $(python -c 'import sys; print(sys.version.split()[0])')"
python mace_amorph.py --spec "spec_${NAME}.json" --model model.model --device "$DEV" > "${NAME}_ml.log" 2>&1
log "mace_amorph.py exit $? (0 = QC PASS, 2 = QC FAIL, other = error)"
rm -rf env model.model
exit 0
