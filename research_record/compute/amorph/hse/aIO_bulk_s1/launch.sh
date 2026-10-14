#!/bin/bash
# A23 (iii) amorphous-bulk hybrid check: aIO_bulk_s1 (125 atoms) at its PBE-relaxed geometry from A23 (i).
# usage: bash launch.sh [--dry] [relax.out]   (default relax.out: ~/iwo_amorph/runs/aIO_bulk_s1/relax.out)
# Refuses without 'bfgs converged' (and RELAX_STATUS = CONVERGED next to it). k = Gamma (see README.md).
export NAME=aIO_bulk_s1
export SRC_IN=$HOME/iwo_amorph/runs/aIO_bulk_s1/relax.in
export RELAX_OUT_DEFAULT=$HOME/iwo_amorph/runs/aIO_bulk_s1/relax.out
export K=1 NBND=660 NEL=1100 NV=550 POOLS_PBE=1   # SG15 N_el = 50x13 + 75x6 = 1100; N_v = 550 (N_ex = 0)
exec bash "$HOME/iwo_amorph/hse/tools/launch_nc.sh" "$@"
