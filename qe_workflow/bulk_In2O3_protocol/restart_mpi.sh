#!/bin/bash
# Restart stage 1 with MPI (10 ranks, 1 thread, 2 k-point pools); 2026-09-26.
cd "$(dirname "$0")"
pkill -f run_convergence.sh; pkill pw.x; sleep 3
cat > run_convergence.sh <<'EOF'
#!/bin/bash
# Stage 1: cutoff and k-point convergence of bulk In2O3 (40-atom primitive bixbyite, PBE-PAW). MPI: 10 ranks x 1 thread, 2 k-pools.
set -u
export OMP_NUM_THREADS=1
PW=~/miniforge3/envs/qe/bin/pw.x
MPI=~/miniforge3/envs/qe/bin/mpirun
for f in scf_ecut50_k3 scf_ecut60_k3 scf_ecut71_k3 scf_ecut85_k3 scf_ecut71_k2 scf_ecut71_k4; do
  if grep -q "JOB DONE" $f.out 2>/dev/null; then echo "skip $f"; continue; fi
  echo "start $f $(date -u +%FT%TZ)"
  $MPI -np 10 --bind-to core $PW -nk 2 -in $f.in > $f.out 2>&1
  echo "end   $f $(date -u +%FT%TZ)"
  grep -E "^!|highest occupied|P=" $f.out | tail -3
done
echo "STAGE1 DONE $(date -u +%FT%TZ)"
EOF
rm -f scf_ecut50_k3.out; rm -rf tmp
nohup setsid bash run_convergence.sh > convergence.log 2>&1 < /dev/null &
sleep 150
echo "pw.x processes: $(pgrep -c pw.x)"
grep -E "Number of MPI|K-points division|iteration #" scf_ecut50_k3.out | tail -3
