#!/bin/bash
# Re-builds runs_sep_oct (read-only on the run folders; no tar member is written to disk). Usage: bash run_all.sh [python]
set -e
cd "$(dirname "$0")"
PY="${1:-python}"
"$PY" stream_runaway.py       # streams the 9.4 GB tar member (minutes); writes out/iwo_slab1_W24d_x1_runaway_scf.json
"$PY" stream_runaway_nul.py   # second streaming pass: NUL bytes and pw.x markers
"$PY" extract_runs.py         # out/<run>.json, out/<run>_arrays.json.gz
"$PY" sheets.py               # sheets/<run>.md, MASTER_TABLE.md, out/master.json, out/checks_vs_results_log.json
"$PY" figures_runs.py         # figures/figR1..R5 (PNG 300 dpi + PDF)
