#!/bin/bash
# Re-runs the whole read-only analysis (no DFT runs). Usage: bash run_all.sh [python]
set -e
cd "$(dirname "$0")"
PY="${1:-python}"
for s in f01_bulk_convergence f02_bulk_structure_bands f03_bulk_alignment f04_slab_vacuum f05_slab_series f07_hse_ratio \
         f06_confinement_laws f08_slab_pdos_surface f09_iwo_bulk f10_iwo_slabs f11_hl_vacancy f12_relax_traces \
         f13_hl_raw f14_amorph_force_checks; do
  "$PY" "$s.py" > "out/$s.log" 2>&1 || { echo "FAILED $s"; exit 1; }
  echo "ok $s"
done
"$PY" make_report.py
