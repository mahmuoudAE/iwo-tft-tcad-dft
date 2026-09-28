#!/bin/bash
# Stage 2: variable-cell relaxation of bulk In2O3 at the converged settings (71 Ry, 3x3x3), 2026-09-27.
# Input derived from scf_ecut71_k3.in: calculation 'vc-relax', prefix 'vcr', nstep 100; BFGS; the cubic symmetry
# (24 operations) is kept by pw.x. pw.x performs the final SCF with the plane-wave basis of the relaxed cell.
cd "$(dirname "$0")"
sed -e "s/calculation = 'scf', prefix = 'ec71'/calculation = 'vc-relax', prefix = 'vcr', nstep = 100/" scf_ecut71_k3.in > vcrelax_ecut71_k3.in
grep -q "vc-relax" vcrelax_ecut71_k3.in || { echo "input generation failed"; exit 1; }
export OMP_NUM_THREADS=1
echo "stage2 start $(date -u +%FT%TZ)" >> stage2.log
~/miniforge3/envs/qe/bin/mpirun -np 10 --bind-to core ~/miniforge3/envs/qe/bin/pw.x -nk 2 -in vcrelax_ecut71_k3.in > vcrelax_ecut71_k3.out 2>&1
echo "stage2 end $(date -u +%FT%TZ) rc=$?" >> stage2.log
grep -E "^!|P=|Final enthalpy|bfgs converged|End final coordinates|CELL_PARAMETERS" vcrelax_ecut71_k3.out | tail -12 >> stage2.log
echo "STAGE2 DONE $(date -u +%FT%TZ)" >> stage2.log
