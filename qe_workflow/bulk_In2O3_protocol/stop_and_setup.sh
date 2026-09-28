#!/bin/bash
for p in $(pgrep -f "run_convergence"); do [ "$p" != "$$" ] && kill "$p"; done
pkill -x pw.x; pkill -x mpirun; sleep 2
echo "running pw.x: $(pgrep -c -x pw.x)"
~/miniforge3/bin/conda install -y -n qe -c conda-forge ase spglib > /tmp/ase.log 2>&1; tail -1 /tmp/ase.log
~/miniforge3/envs/qe/bin/python -c "import ase, spglib; print('ase', ase.__version__, 'spglib', spglib.__version__)"
