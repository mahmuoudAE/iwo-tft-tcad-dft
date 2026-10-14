#!/bin/bash
# Replace the v1 D-24 B+D staging by v2. The v1 staged files are MOVED into common/D24_BD_v1.pre_D24/ (backup, same
# relative paths); no live file is touched. Then runs the v2 stage script. usage: bash restage_v2.sh <upload dir>
set -u
U=$1; B=$HOME/iwo_amorph; cd "$B" || exit 1
RUNS="aIO_0p7_s1 aIO_1p0_s1 aIO_1p5_s1 aIO_2p0_s1 aIO_2p0_s2 aIWO_0p7_s1 aIWO_0p7_s1_bare aIWO_0p8_s2
      aIWO_1p0_Al2O3_s2 aIWO_1p0_s1 aIWO_1p5_s1 aIWO_2p0_Al2O3_s2 aIWO_2p0_comp_s1 aIWO_2p0_s1 aIWO_2p0_s1_bare aIWO_2p0_s2"
BENCH=aIWO_1p0_Al2O3_s2
GEO=/afs/cern.ch/user/m/melrashe/iwo_amorph/common/geomsel.py
BK=common/D24_BD_v1.pre_D24
want() { [ "$(md5sum < "$2" | cut -c1-32)" = "$1" ] || { echo "REFUSE: $2 is not the v1 staged version"; exit 1; }; }
# 1. the files to move must be exactly the v1 staging (nothing installed, nobody else changed them)
[ -e "$BK" ] && { echo "REFUSE: $BK exists"; exit 1; }
for f in common/d24_transition.sh common/D24_BD_staged.md5 common/D24_BD_baseline.md5 runs/$BENCH/relax.sub.D24_2gpu common/geomsel.py; do
  [ -e "$f" ] && { echo "REFUSE: $f exists already"; exit 1; }
done
ls runs/*/segment_guard runs/*/segment_stop runs/*/*.pre_D24 common/*.pre_D24 2>/dev/null | grep -q . && { echo "REFUSE: install traces found"; exit 1; }
want e2121e1fe39cf6f18f2747fcc2b46408 common/relax_node.sh.D24
want 5bfbae7841fd84344ea4065c67fa1af9 common/geomsel.py.D24
want e7143d4e796e7d9b0bbb69cc2c813377 common/README_D24_BD.txt
want b12862709f6bf3825553f7861f9d8ac8 common/install_D24_BD.sh
tmp=$(mktemp)
for r in $RUNS; do
  if [ "$r" = "$BENCH" ]; then want dee7ccf774889d81dea7bfbaacacffd0 runs/$r/steps_relax.sh.D24; else want 7a0bb65ded4747e41c31d9c24dced4a7 runs/$r/steps_relax.sh.D24; fi
  sed -e "/^transfer_input_files/ s|\$|, $GEO, segment_guard|" -e '/^transfer_output_files/ s|$|, segment_guard|' \
      -e '/^queue/ i # D-24 (2026-10-11): geomsel.py and segment_guard (fail-fast guard), see common/README_D24_BD.txt' runs/$r/relax.sub > "$tmp"
  if [ "$r" = "$BENCH" ]; then
    sed -i -e 's|^request_gpus .*|request_gpus            = 1|' -e 's|^requirements .*|requirements            = regexp("H200", TARGET.GPUs_DeviceName)|' \
      -e '/^queue/ i # D-24 item D: single-H200 benchmark (was request_gpus 2, H100|H200); revert = relax.sub.pre_D24' "$tmp"
  fi
  cmp -s "$tmp" runs/$r/relax.sub.D24 || { echo "REFUSE: runs/$r/relax.sub.D24 is not the v1 staged version"; exit 1; }
done
rm -f "$tmp"
echo "v1 staging verified"
# 2. move v1 into the backup tree
mkdir -p "$BK/common" || exit 1
mv common/relax_node.sh.D24 common/geomsel.py.D24 common/README_D24_BD.txt common/install_D24_BD.sh "$BK/common/" || exit 1
for r in $RUNS; do mkdir -p "$BK/runs/$r" && mv runs/$r/steps_relax.sh.D24 runs/$r/relax.sub.D24 "$BK/runs/$r/" || exit 1; done
echo "v1 moved to $BK: $(find "$BK" -type f | wc -l) files"
# 3. stage v2
bash "$U/stage_D24_BD.sh" "$U"
