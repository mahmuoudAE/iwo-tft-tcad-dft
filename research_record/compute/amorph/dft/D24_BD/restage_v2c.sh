#!/bin/bash
# Replace staging v2b (staged 2026-10-11 00:09 CEST) by v2c: common/README_D24_BD.txt, common/install_D24_BD.sh and
# common/d24_transition.sh change, and the d24_transition.sh line of common/D24_BD_staged.md5. The v2b files are COPIED
# to common/D24_BD_backup/v2b.pre_D24/common/ first; each replacement is copy-to-temp + rename with the old mode.
# No live file and no job is touched. usage: bash restage_v2c.sh <upload dir>
set -u
U=$1; B=$HOME/iwo_amorph; cd "$B" || exit 1
RUNS="aIO_0p7_s1 aIO_1p0_s1 aIO_1p5_s1 aIO_2p0_s1 aIO_2p0_s2 aIWO_0p7_s1 aIWO_0p7_s1_bare aIWO_0p8_s2
      aIWO_1p0_Al2O3_s2 aIWO_1p0_s1 aIWO_1p5_s1 aIWO_2p0_Al2O3_s2 aIWO_2p0_comp_s1 aIWO_2p0_s1 aIWO_2p0_s1_bare aIWO_2p0_s2"
BENCH=aIWO_1p0_Al2O3_s2
BK=common/D24_BD_backup/v2b.pre_D24
[ -e "$BK" ] && { echo "REFUSE: $BK exists"; exit 1; }
ls -d runs/*/segment_guard runs/*/segment_stop runs/*/*.pre_D24 common/relax_node.sh.pre_D24 common/geomsel.py 2>/dev/null | grep -q . \
  && { echo "REFUSE: install traces found (D-24 already installed?)"; exit 1; }
want() { [ "$(md5sum < "$2" | cut -c1-32)" = "$1" ] || { echo "REFUSE: $2 is not the v2b staged version"; exit 1; }; }
want 77ed9fe9c188f5404c200ef0caa4a958 common/README_D24_BD.txt
want 773a61a72f92d6982564312bd821fed7 common/install_D24_BD.sh
want f9ed20fda7c8d3e448c86d6b68aff6b3 common/d24_transition.sh
want 97c48d66987aac68450cbbba14fc1c9d common/D24_BD_staged.md5
md5sum -c --quiet common/D24_BD_staged.md5 || { echo "REFUSE: staged files changed since v2b"; exit 1; }
for f in README_D24_BD.txt install_D24_BD.sh d24_transition.sh; do bash -n "$U/$f" 2>/dev/null || [ "$f" = README_D24_BD.txt ] || { echo "REFUSE: $U/$f does not parse"; exit 1; }; done
mkdir -p "$BK/common" && cp -p common/README_D24_BD.txt common/install_D24_BD.sh common/d24_transition.sh common/D24_BD_staged.md5 "$BK/common/" \
  || { echo "backup failed"; exit 1; }
put() { cp "$1" "$2.v2ctmp" && chmod --reference="$2" "$2.v2ctmp" && mv -f "$2.v2ctmp" "$2" || { echo "FAILED: $2"; exit 1; }; }
put "$U/README_D24_BD.txt" common/README_D24_BD.txt
put "$U/install_D24_BD.sh" common/install_D24_BD.sh
put "$U/d24_transition.sh" common/d24_transition.sh
m=$(mktemp)
{ md5sum common/relax_node.sh.D24 common/geomsel.py.D24 common/d24_transition.sh runs/$BENCH/relax.sub.D24_2gpu
  for r in $RUNS; do md5sum runs/$r/relax.sub.D24 runs/$r/steps_relax.sh.D24; done; } > "$m"
put "$m" common/D24_BD_staged.md5; rm -f "$m"
echo "== backup $BK"; ls -la "$BK/common"
echo "== manifest change"; diff "$BK/common/D24_BD_staged.md5" common/D24_BD_staged.md5
md5sum -c --quiet common/D24_BD_staged.md5 && echo "staged manifest ok"; md5sum -c --quiet common/D24_BD_baseline.md5 && echo "baseline manifest ok"
ls -la common/README_D24_BD.txt common/install_D24_BD.sh common/d24_transition.sh common/D24_BD_staged.md5
md5sum common/README_D24_BD.txt common/install_D24_BD.sh common/d24_transition.sh common/D24_BD_staged.md5
ls -d runs/*/segment_guard runs/*/segment_stop runs/*/*.pre_D24 common/relax_node.sh.pre_D24 common/geomsel.py 2>/dev/null | head -3; echo "(no install traces if empty above)"
