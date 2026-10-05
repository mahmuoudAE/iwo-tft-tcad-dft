#!/bin/bash
# Bulk reference for the two-step band alignment (Van de Walle & Martin 1987): the cell average of the same potential
# that the slab planar averages use (pp.x plot_num = 11: bare ionic + Hartree), from the relaxed bulk SCF (prefix vcr,
# a = 10.306 A). Output: bulk_v11.cube (3D grid); its mean is computed by bulk_alignment.py.
set -e
cd "$(dirname "$0")"
QE=$HOME/miniforge3/envs/qe/bin
cat > pp_bulk_v11.in <<EOF
&INPUTPP
  prefix = 'vcr', outdir = './tmp', filplot = 'bulk_v11.pp', plot_num = 11
/
&PLOT
  iflag = 3, output_format = 6, fileout = 'bulk_v11.cube'
/
EOF
$QE/mpirun -np 4 $QE/pp.x -in pp_bulk_v11.in > pp_bulk_v11.out 2>&1
tail -3 pp_bulk_v11.out
ls -la bulk_v11.cube
