# TODO for the main session: the make_dft.py side of D-24 items B and D (relax continuation)

Written 2026-10-11 by the D-24 B/D build agent, updated for staging v2 (after the verification of v1). make_dft.py was
NOT edited (the HfO2 build agent owns it). Without this change, every chain that make_dft.py writes from now on (e.g.
the H-M HfO2 cells) gets the pre-D-24 relax continuation, which restarts from unevaluated trial geometries and replays
FAILED segments.

1. steps_relax.sh written into each run: use `compute/amorph/dft/D24_BD/steps_relax.sh.D24` (CERN:
   `runs/<any of the 15>/steps_relax.sh.D24`), never the benchmark variant `steps_relax_bench.sh.D24` (nvidia-smi block).
2. relax.sub (v2):
   - `transfer_input_files` += `/afs/cern.ch/user/m/melrashe/iwo_amorph/common/geomsel.py, segment_guard, segment_stop`
   - `transfer_output_files` += `segment_guard` (never `segment_stop`: it is input-only, so a running job cannot
     overwrite a stop written by a person)
   - `requirements` += `&& !regexp("MIG", TARGET.GPUs_DeviceName)` (the H100|H200 regexp also matches the MIG slices
     'NVIDIA H100L-1-12C MIG 1g.12gb' and '...2g.24gb'; with D-24 an out-of-memory start there would stop the chain)
   Example files: `compute/amorph/dft/D24_BD/relax_sub_examples/`.
3. Create an empty `segment_guard` and an empty `segment_stop` in each new run directory (a missing input file holds the
   job; never delete them later, empty them).
4. New DAGs can use `RETRY RELAX 8 UNLESS-EXIT 2` with a node script that exits 2 on FAILED (as the pilot's
   relax_node_pilot.sh); the stop files then remain a second line of defence. Keep `common/relax_node.sh` as the
   executable for the 16 existing chains.
5. Check after the edit: generate one run into a scratch ROOT and `diff` its steps_relax.sh against
   `steps_relax.sh.D24` (identical) and its relax.sub against an installed `relax.sub` (only the name and the run's own
   request lines differ).
