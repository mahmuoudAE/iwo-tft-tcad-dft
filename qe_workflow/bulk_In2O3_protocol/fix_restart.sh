#!/bin/bash
# Stop the mismatched run, verify symmetry of the corrected input, restart stage 1.
cd "$(dirname "$0")"
for p in $(pgrep -f "run_convergence"); do [ "$p" != "$$" ] && kill "$p"; done
pkill -x pw.x; pkill -x mpirun; sleep 3
mkdir -p defective_structure_runs
mv -f scf_ecut50_k3.out defective_structure_runs/scf_ecut50_k3_ibrav3_basis_mismatch.out 2>/dev/null
rm -rf ./tmp
~/miniforge3/envs/qe/bin/mpirun -np 10 --bind-to core ~/miniforge3/envs/qe/bin/pw.x -nk 2 -in scf_ecut50_k3.in > /tmp/symcheck.out 2>&1 &
sleep 40
grep "Sym. Ops" /tmp/symcheck.out
pkill -x pw.x; pkill -x mpirun; sleep 2
rm -rf ./tmp
nohup setsid bash run_convergence.sh > convergence.log 2>&1 < /dev/null &
sleep 5
echo "restarted, pw.x processes: $(pgrep -c -x pw.x)"
