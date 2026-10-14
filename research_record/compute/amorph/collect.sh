#!/bin/bash
# Idempotent collector (lxplus): unpack finished ML outputs, start the DFT DAG for every QC-PASS slab, and submit the
# ML force-check jobs once their source structures exist. State: ~/iwo_amorph/state/<name>.{collected,dag,val}
# usage: bash ~/iwo_amorph/collect.sh            (safe to run any number of times)
cd ~/iwo_amorph || exit 1
mkdir -p state results
VALSET="aIWO_bulk_s1:melt_3000K,quenched_300K,final aIO_bulk_s1:quenched_300K,final aIWO_2p0_s1:slab_annealed,final aIWO_0p7_s1:final"
for tgz in *_ml.tar.gz; do
  [ -e "$tgz" ] || continue
  name=${tgz%_ml.tar.gz}
  if [ ! -e state/$name.collected ]; then
    mkdir -p results/$name && tar xzf "$tgz" -C results/$name && touch state/$name.collected
  fi
  qc=$(python3 -c "import json,sys; d=json.load(open('results/$name/${name}_qc.json')); print(d['QC'], '; '.join(d['QC_reasons']))" 2>/dev/null || echo "NO_QC_FILE")
  case "$name" in *_bulk_*) echo "$name: $qc (bulk: force-check source only)"; continue;; esac
  if [ -e state/$name.rejected ]; then
    echo "$name: rejected by QC earlier (replaced by a new seed)"
  elif [ ! -e state/$name.dag ]; then
    if python3 common/make_dft.py "$name"; then   # make_dft.py applies the QC rule (a vacuum-only FAIL is fixed there)
      (cd runs/$name && condor_submit_dag -batch-name "$name" "$name.dag" | tail -1) && touch state/$name.dag
    else
      echo "$name: $qc -> DFT not started"
      case "$qc" in FAIL*) touch state/$name.rejected;; esac
    fi
  else
    echo "$name: $qc, DAG submitted earlier"
  fi
done
if [ ! -e state/val.submitted ]; then
  ok=1; for item in $VALSET; do [ -s "results/${item%%:*}/${item%%:*}_snapshots.xyz" ] || ok=0; done
  if [ $ok = 1 ]; then
    python3 common/make_val.py $VALSET && condor_submit val/val.sub | tail -1 && touch state/val.submitted
  else
    echo "force check: waiting for source structures"
  fi
fi
condor_q -totals 2>/dev/null | tail -2 | head -1
