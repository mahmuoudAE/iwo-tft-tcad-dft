#!/bin/bash
# Restart stage 1 from a clean state with the verified structure (2026-09-26).
cd "$(dirname "$0")"
mkdir -p defective_structure_runs
mv -f scf_ecut50_k3.out scf_ecut60_k3.out convergence.log defective_structure_runs/ 2>/dev/null
rm -rf tmp
nohup setsid bash run_convergence.sh > convergence.log 2>&1 < /dev/null &
sleep 200
echo "pw.x: $(pgrep -c -x pw.x)"
grep -E "Sym. Ops|iteration #" scf_ecut50_k3.out | head -1
grep -c "iteration #" scf_ecut50_k3.out
