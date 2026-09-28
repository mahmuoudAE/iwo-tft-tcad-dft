#!/bin/bash
# Stage 3 (local): waits for stage 2, then runs the two non-self-consistent band calculations.
cd "$(dirname "$0")"
until grep -q "STAGE2 DONE" stage2.log 2>/dev/null; do sleep 120; done
echo "stage3 start $(date -u +%FT%TZ)" >> stage3.log
~/miniforge3/envs/qe/bin/python make_stage3.py >> stage3.log 2>&1 || { echo "STAGE3 STOPPED: input generation failed" >> stage3.log; exit 1; }
export OMP_NUM_THREADS=1
for f in bands_gamma bands_path; do
  echo "$f start $(date -u +%FT%TZ)" >> stage3.log
  ~/miniforge3/envs/qe/bin/mpirun -np 10 --bind-to core ~/miniforge3/envs/qe/bin/pw.x -nk 2 -in $f.in > $f.out 2>&1
  echo "$f end $(date -u +%FT%TZ) rc=$? $(grep -c 'JOB DONE' $f.out)" >> stage3.log
done
echo "STAGE3 DONE $(date -u +%FT%TZ)" >> stage3.log
