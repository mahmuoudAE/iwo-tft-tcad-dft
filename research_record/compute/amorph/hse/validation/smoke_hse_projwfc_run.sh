#!/bin/bash
# smoke test: projwfc.x (QE 7.5) on an HSE06 save made with pristine SG15 files, after swapping in the PP_CHI copies
source ~/miniforge3/etc/profile.d/conda.sh; conda activate qe
S=/mnt/c/Users/moham/AppData/Local/Temp/claude/C--Users-moham-Downloads-IWO-Local-Codex-Handoff--1--IWO-ATLAS-Model-claude/7c34fe97-c389-4002-8f70-9615a643e20b/scratchpad/a23v/smoke
M="/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff (1)/iwo-tft-research-private/compute/amorph/hse"
P="/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff (1)/IWO_PHYSICS_CONSTRAINED_MODEL_V1/qe_workflow/pseudo"
W=/tmp/a23vsmoke; rm -rf $W; mkdir -p $W/pseudo; cd $W
export OMP_NUM_THREADS=1
for e in In O W; do cp "$P/${e}_ONCV_PBE-1.2.upf" pseudo/; done
cp $S/hse.in .
mpirun -np 2 --bind-to none pw.x -nk 2 -in hse.in > hse.out 2>&1; echo "pw rc=$?"
grep -E "^!!|convergence has been|Fermi|JOB DONE|PWSCF.*WALL" hse.out | tail -5
for f in "$M"/pseudo_proj/*.upf; do cp -f "$f" tmp/hse.save/; cp -f "$f" pseudo/; done
python3 "$M/tools/set_natomwfc.py" tmp/hse.save
EF=$(grep Fermi hse.out | tail -1 | awk '{print $(NF-1)}')
printf "&PROJWFC\n  prefix = 'hse', outdir = './tmp', filpdos = 'pdos/hse'\n  Emin = %s, Emax = %s, DeltaE = 0.01, degauss = 0.0073, ngauss = 0\n/\n" $(awk -v e=$EF 'BEGIN{print e-8, e+4}') > proj.in
mkdir -p pdos
mpirun -np 2 --bind-to none projwfc.x -nk 2 -in proj.in > proj.out 2>&1; echo "projwfc rc=$?"
grep -E "Error|state #|spilling|JOB DONE" proj.out | head -40
ls -la tmp/hse.save/atomic_proj.xml
cp hse.out proj.out $S/
cd /; rm -rf $W
