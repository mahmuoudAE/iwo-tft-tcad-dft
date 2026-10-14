#!/bin/bash
# A23 (ii) W-cell hybrid check: crystalline In31WO48 (80 atoms, W on 24d) at the H-L-relaxed geometry.
# usage: bash launch.sh [--dry] [relax.out]   (default relax.out: ~/iwo_amorph/vac/In31WO48/relax.out)
# Refuses without 'bfgs converged'. NOT to be run before the H-L relaxation has converged. See README.md.
export NAME=In31WO48
export SRC_IN=$HOME/iwo_amorph/vac/In31WO48/relax.in
export RELAX_OUT_DEFAULT=$HOME/iwo_amorph/vac/In31WO48/relax.out
export K=2 NBND=432 NEL=719 NV=358 POOLS_PBE=4    # SG15 N_el = 31x13 + 28 + 48x6 = 719; N_ex = 3 (W6+ on an In3+ site, no extra O); N_v = (719 - 3)/2 = 358 (PAW: 351 = n_pure - 1)
exec bash "$HOME/iwo_amorph/hse/tools/launch_nc.sh" "$@"
