#!/bin/bash
# Replace the first v2 staging (00:05 UTC+2, this build) by the corrected one (tool backup-file name, README 3a text,
# test log fix). The first v2 files are MOVED into common/D24_BD_backup/v2a.pre_D24/ after checking they are unchanged since
# staging; no live file is touched. usage: bash restage_v2b.sh <upload dir>
set -u
U=$1; B=$HOME/iwo_amorph; cd "$B" || exit 1
RUNS="aIO_0p7_s1 aIO_1p0_s1 aIO_1p5_s1 aIO_2p0_s1 aIO_2p0_s2 aIWO_0p7_s1 aIWO_0p7_s1_bare aIWO_0p8_s2
      aIWO_1p0_Al2O3_s2 aIWO_1p0_s1 aIWO_1p5_s1 aIWO_2p0_Al2O3_s2 aIWO_2p0_comp_s1 aIWO_2p0_s1 aIWO_2p0_s1_bare aIWO_2p0_s2"
BENCH=aIWO_1p0_Al2O3_s2
BK=common/D24_BD_backup/v2a.pre_D24
[ -e "$BK" ] && { echo "REFUSE: $BK exists"; exit 1; }
ls -d runs/*/segment_guard runs/*/segment_stop runs/*/*.pre_D24 common/relax_node.sh.pre_D24 common/geomsel.py 2>/dev/null | grep -q . && { echo "REFUSE: install traces found"; exit 1; }
# the v1 backup directory moves under common/D24_BD_backup/ so that no directory matches common/*.pre_D24
if [ -d common/D24_BD_v1.pre_D24 ]; then
  [ -e common/D24_BD_backup/v1.pre_D24 ] && { echo "REFUSE: common/D24_BD_backup/v1.pre_D24 exists"; exit 1; }
  mkdir -p common/D24_BD_backup && mv common/D24_BD_v1.pre_D24 common/D24_BD_backup/v1.pre_D24 || exit 1
fi
md5sum -c --quiet common/D24_BD_staged.md5 || { echo "REFUSE: staged files changed since the first v2 staging"; exit 1; }
[ "$(md5sum < common/README_D24_BD.txt | cut -c1-32)" = 097901892593d74673cd29728e4c6a36 ] && \
[ "$(md5sum < common/install_D24_BD.sh | cut -c1-32)" = 773a61a72f92d6982564312bd821fed7 ] || { echo "REFUSE: README / install changed"; exit 1; }
mkdir -p "$BK/common" || exit 1
mv common/relax_node.sh.D24 common/geomsel.py.D24 common/d24_transition.sh common/README_D24_BD.txt common/install_D24_BD.sh \
   common/D24_BD_staged.md5 common/D24_BD_baseline.md5 "$BK/common/" || exit 1
for r in $RUNS; do
  mkdir -p "$BK/runs/$r" && mv runs/$r/steps_relax.sh.D24 runs/$r/relax.sub.D24 "$BK/runs/$r/" || exit 1
done
mv runs/$BENCH/relax.sub.D24_2gpu "$BK/runs/$BENCH/" || exit 1
echo "first v2 moved to $BK: $(find "$BK" -type f | wc -l) files"
bash "$U/stage_D24_BD.sh" "$U" > /tmp/d24v2_stage.log 2>&1; rc=$?
grep -E 'REFUSE|did not match' /tmp/d24v2_stage.log; echo "stage exit $rc"
md5sum common/relax_node.sh.D24 common/d24_transition.sh common/README_D24_BD.txt common/install_D24_BD.sh common/D24_BD_*.md5
md5sum runs/*/steps_relax.sh.D24 | awk '{print $1}' | sort | uniq -c
