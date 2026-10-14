#!/bin/bash
# Re-runs the read-only band-structure / effective-mass / TCAD-parameter analysis (no DFT run).
# Needs the parent analysis outputs (../out/f03, f05, f06, f08, f09, f10 JSON): run ../run_all.sh first if they are missing.
# Usage: bash run_all.sh [python]
set -e
cd "$(dirname "$0")"
PY="${1:-python}"
mkdir -p out figures
for s in b01_masses b02_band_figures b03_gaps_laws b04_tcad b05_holes make_bm_report; do
  "$PY" "$s.py" > "out/$s.log" 2>&1 || { echo "FAILED $s"; exit 1; }
  echo "ok $s"
done
