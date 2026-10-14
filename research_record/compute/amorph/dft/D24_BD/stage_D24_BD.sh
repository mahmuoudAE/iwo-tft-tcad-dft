#!/bin/bash
# Stage D-24 B+D (v2) on lxplus: only NEW files (*.D24, *.D24_2gpu, README_D24_BD.txt, install_D24_BD.sh,
# d24_transition.sh, the two md5 manifests); no live file changes.
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
# the live files must be the versions this build was written and tested against
want() { [ "$(md5sum < "$2" | cut -c1-32)" = "$1" ] || { echo "REFUSE: $2 is not the expected version ($1)"; exit 1; }; }
want 140cb49e008f04c1391a5df46a227b7a common/relax_node.sh
want 60d11efdd63d3521fc631699c04226dc common/driver.sh
want 1bc0f1472fedda6d866c22e53a3949a2 common/qeio.py
want 5bfbae7841fd84344ea4065c67fa1af9 runs/aIO_0p8_s1/geomsel.py
for r in $RUNS; do want bcc29d43f57ba98129a0e54f44923192 runs/$r/steps_relax.sh; done

# relax.sub.D24 = live relax.sub + D-24 transfers + MIG exclusion (+ the benchmark request for item D)
d24sub() {   # d24sub <live relax.sub> <out>
  sed -e "/^transfer_input_files/ s|\$|, $GEO, segment_guard, segment_stop|" \
      -e '/^transfer_output_files/ s|$|, segment_guard|' \
      -e 's#^\(requirements *= regexp("H100|H200", TARGET.GPUs_DeviceName)\)$#\1 \&\& !regexp("MIG", TARGET.GPUs_DeviceName)#' \
      -e '/^queue/ i # D-24 (2026-10-11): geomsel.py, segment_guard and segment_stop (fail-fast stops), MIG slices excluded; see common/README_D24_BD.txt' \
      "$1" > "$2"
  local n1 n2 n3
  n1=$(grep -c "^transfer_input_files.*, relax.in, steps_relax.sh, $GEO, segment_guard, segment_stop\$" "$2")
  n2=$(grep -c '^transfer_output_files.*RELAX_STATUS, segment_guard$' "$2")
  n3=$(grep -c '^requirements *= regexp("H100|H200", TARGET.GPUs_DeviceName) && !regexp("MIG", TARGET.GPUs_DeviceName)$' "$2")
  [ "$n1" = 1 ] && [ "$n2" = 1 ] && [ "$n3" = 1 ] || { echo "$1: relax.sub edit did not match exactly once ($n1 $n2 $n3)"; exit 1; }
}
tmp=$(mktemp)
for r in $RUNS; do
  d=runs/$r
  if [ "$r" = "$BENCH" ]; then put "$U/steps_relax.sh.D24.bench" $d/steps_relax.sh.D24; else put "$U/steps_relax.sh.D24" $d/steps_relax.sh.D24; fi
  d24sub $d/relax.sub "$tmp"
  if [ "$r" = "$BENCH" ]; then
    sed -e '/^queue/ i # D-24 item D revert file: the 2 x H100|H200 request from before the benchmark, with the D-24 transfers (README section 4)' "$tmp" > "$tmp.2"
    put "$tmp.2" $d/relax.sub.D24_2gpu
    sed -i -e 's|^request_gpus .*|request_gpus            = 1|' \
           -e 's#^requirements .*#requirements            = regexp("H200", TARGET.GPUs_DeviceName) \&\& !regexp("MIG", TARGET.GPUs_DeviceName)#' \
           -e '/^queue/ i # D-24 item D: single-H200 benchmark (was request_gpus 2, H100|H200). Revert = swap in relax.sub.D24_2gpu (never relax.sub.pre_D24 unless the full section 5 rollback is done), README_D24_BD.txt section 4' "$tmp"
    [ "$(grep -c '^request_gpus *= 1$' "$tmp")" = 1 ] && [ "$(grep -c '^requirements *= regexp("H200", TARGET.GPUs_DeviceName) && !regexp("MIG", TARGET.GPUs_DeviceName)$' "$tmp")" = 1 ] \
      || { echo "$r: benchmark edit did not match"; exit 1; }
  fi
  put "$tmp" $d/relax.sub.D24
done
rm -f "$tmp" "$tmp.2"
put "$U/relax_node.sh.D24" common/relax_node.sh.D24 && chmod 755 common/relax_node.sh.D24
put runs/aIO_0p8_s1/geomsel.py common/geomsel.py.D24 && chmod 644 common/geomsel.py.D24
put "$U/d24_transition.sh" common/d24_transition.sh && chmod 755 common/d24_transition.sh
put "$U/README_D24_BD.txt" common/README_D24_BD.txt
put "$U/install_D24_BD.sh" common/install_D24_BD.sh && chmod 644 common/install_D24_BD.sh

# manifests: the live files the staged ones were derived from, and the staged files as tested
m=$(mktemp)
{ md5sum common/relax_node.sh common/driver.sh common/qeio.py
  for r in $RUNS; do md5sum runs/$r/relax.sub runs/$r/steps_relax.sh; done; } > "$m"; put "$m" common/D24_BD_baseline.md5
{ md5sum common/relax_node.sh.D24 common/geomsel.py.D24 common/d24_transition.sh runs/$BENCH/relax.sub.D24_2gpu
  for r in $RUNS; do md5sum runs/$r/relax.sub.D24 runs/$r/steps_relax.sh.D24; done; } > "$m"; put "$m" common/D24_BD_staged.md5
rm -f "$m"; chmod 644 common/D24_BD_baseline.md5 common/D24_BD_staged.md5

echo "== staged files"; ls -la common/*.D24 common/README_D24_BD.txt common/install_D24_BD.sh common/d24_transition.sh common/D24_BD_*.md5
md5sum runs/*/steps_relax.sh.D24 | awk '{print $1}' | sort | uniq -c
echo "== diff common/relax_node.sh"; diff -u common/relax_node.sh common/relax_node.sh.D24
echo "== diff steps_relax.sh (15 runs)"; diff -u runs/aIWO_1p0_s1/steps_relax.sh runs/aIWO_1p0_s1/steps_relax.sh.D24
echo "== diff steps_relax.sh.D24 (15 runs) -> $BENCH"; diff -u runs/aIWO_1p0_s1/steps_relax.sh.D24 runs/$BENCH/steps_relax.sh.D24
for r in aIWO_1p0_s1 aIWO_2p0_Al2O3_s2 $BENCH; do echo "== diff relax.sub $r"; diff -u runs/$r/relax.sub runs/$r/relax.sub.D24; done
echo "== diff relax.sub.D24 -> relax.sub.D24_2gpu ($BENCH)"; diff runs/$BENCH/relax.sub.D24 runs/$BENCH/relax.sub.D24_2gpu
echo "== relax.sub.D24 variants (name-normalised md5)"
for r in $RUNS; do sed "s/$r/NAME/g" runs/$r/relax.sub.D24 | md5sum | sed "s/-/$r/"; done | sort | uniq -c -w32
