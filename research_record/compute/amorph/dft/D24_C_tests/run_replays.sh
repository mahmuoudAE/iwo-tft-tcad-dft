#!/bin/bash
# all replay modes in sequence; one log per mode in scratchpad d24f/test/logs
L=/mnt/c/Users/moham/AppData/Local/Temp/claude/C--Users-moham-Downloads-IWO-Local-Codex-Handoff--1--IWO-ATLAS-Model-claude/7c34fe97-c389-4002-8f70-9615a643e20b/scratchpad/d24f/test
mkdir -p $L/logs
for m in ${MODES:-ok fail pend hang projfail nc maxsec}; do
  free -m | awk '/Mem/{print "mem available MB", $7}' > $L/logs/r_$m.log
  bash $L/replay.sh r_$m $m >> $L/logs/r_$m.log 2>&1
  echo "done $m: $(grep -m1 'final_node.sh exit' $L/logs/r_$m.log)"
done
# the A15 pilot keeps its pre-D-24 steps_final.sh: final_node.sh.D24 must keep the old rule for it
bash $L/replay.sh r_pilot_nc nc /mnt/c/Users/moham/AppData/Local/Temp/claude/C--Users-moham-Downloads-IWO-Local-Codex-Handoff--1--IWO-ATLAS-Model-claude/7c34fe97-c389-4002-8f70-9615a643e20b/scratchpad/d24/cern_orig/steps_final.sh aIO_0p8_s1 > $L/logs/r_pilot_nc.log 2>&1
echo "done pilot_nc: $(grep -m1 'final_node.sh exit' $L/logs/r_pilot_nc.log)"
