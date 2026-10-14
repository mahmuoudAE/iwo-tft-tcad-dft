#!/bin/bash
# Stage D-24 B+D on lxplus: only NEW files (*.D24, README_D24_BD.txt, install_D24_BD.sh); no existing file changes.
# usage: bash stage_D24_BD.sh <upload dir>
set -u
U=$1; B=$HOME/iwo_amorph
cd "$B" || exit 1
RUNS="aIO_0p7_s1 aIO_1p0_s1 aIO_1p5_s1 aIO_2p0_s1 aIO_2p0_s2 aIWO_0p7_s1 aIWO_0p7_s1_bare aIWO_0p8_s2
      aIWO_1p0_Al2O3_s2 aIWO_1p0_s1 aIWO_1p5_s1 aIWO_2p0_Al2O3_s2 aIWO_2p0_comp_s1 aIWO_2p0_s1 aIWO_2p0_s1_bare aIWO_2p0_s2"
BENCH=aIWO_1p0_Al2O3_s2
GEO=/afs/cern.ch/user/m/melrashe/iwo_amorph/common/geomsel.py
put() {   # put <src> <dst>: refuse to overwrite a different existing file (another agent's staging)
  if [ -e "$2" ] && ! cmp -s "$1" "$2"; then echo "REFUSE: $2 exists and differs"; exit 1; fi
  cp "$1" "$2"
}
# the old shared files must be the ones this build was diffed against
md5sum common/relax_node.sh common/driver.sh common/qeio.py runs/aIO_0p8_s1/geomsel.py

put "$U/relax_node.sh.D24" common/relax_node.sh.D24 && chmod 755 common/relax_node.sh.D24
put runs/aIO_0p8_s1/geomsel.py common/geomsel.py.D24 && chmod 644 common/geomsel.py.D24
put "$U/README_D24_BD.txt" common/README_D24_BD.txt
put "$U/install_D24_BD.sh" common/install_D24_BD.sh && chmod 644 common/install_D24_BD.sh
tmp=$(mktemp)
for r in $RUNS; do
  d=runs/$r
  [ "$(md5sum < $d/steps_relax.sh)" = "$(md5sum < runs/aIWO_1p0_s1/steps_relax.sh)" ] || { echo "$r: steps_relax.sh is not the common pre-D-24 version"; exit 1; }
  if [ "$r" = "$BENCH" ]; then put "$U/steps_relax.sh.D24.bench" $d/steps_relax.sh.D24; else put "$U/steps_relax.sh.D24" $d/steps_relax.sh.D24; fi
  sed -e "/^transfer_input_files/ s|\$|, $GEO, segment_guard|" \
      -e '/^transfer_output_files/ s|$|, segment_guard|' \
      -e '/^queue/ i # D-24 (2026-10-11): geomsel.py and segment_guard (fail-fast guard), see common/README_D24_BD.txt' \
      $d/relax.sub > "$tmp"
  if [ "$r" = "$BENCH" ]; then
    sed -i -e 's|^request_gpus .*|request_gpus            = 1|' \
           -e 's|^requirements .*|requirements            = regexp("H200", TARGET.GPUs_DeviceName)|' \
           -e '/^queue/ i # D-24 item D: single-H200 benchmark (was request_gpus 2, H100|H200); revert = relax.sub.pre_D24' "$tmp"
  fi
  n1=$(grep -c "geomsel.py, segment_guard\$" "$tmp"); n2=$(grep -c '^transfer_output_files.*RELAX_STATUS, segment_guard$' "$tmp")
  [ "$n1" = 1 ] && [ "$n2" = 1 ] || { echo "$r: relax.sub edit did not match exactly once ($n1 $n2)"; exit 1; }
  put "$tmp" $d/relax.sub.D24
done
rm -f "$tmp"
echo "== staged files"; ls -la common/*.D24 common/README_D24_BD.txt common/install_D24_BD.sh
md5sum runs/*/steps_relax.sh.D24 | sort | uniq -c -w32
echo "== diff common/relax_node.sh"; diff -u common/relax_node.sh common/relax_node.sh.D24
echo "== diff steps_relax.sh (15 runs)"; diff -u runs/aIWO_1p0_s1/steps_relax.sh runs/aIWO_1p0_s1/steps_relax.sh.D24
echo "== diff steps_relax.sh.D24 (15 runs) -> $BENCH"; diff -u runs/aIWO_1p0_s1/steps_relax.sh.D24 runs/$BENCH/steps_relax.sh.D24
for r in aIWO_1p0_s1 aIWO_2p0_s1 aIWO_2p0_Al2O3_s2 $BENCH; do echo "== diff relax.sub $r"; diff -u runs/$r/relax.sub runs/$r/relax.sub.D24; done
echo "== relax.sub.D24 variants (name-normalised md5)"
for r in $RUNS; do sed "s/$r/NAME/g" runs/$r/relax.sub.D24 | md5sum | sed "s/-/$r/"; done | sort | uniq -c -w32
