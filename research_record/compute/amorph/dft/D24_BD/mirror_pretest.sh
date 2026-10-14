#!/bin/bash
# Pre-test of staging v2c BEFORE it is staged: a /tmp mirror of the parts of ~/iwo_amorph the tests read (copied with
# mtimes, read-only on AFS), the v2c README / install / d24_transition from the upload dir laid over it, the mirror's
# D24_BD_staged.md5 regenerated, then test_D24_BD.sh with D24_TREE=<mirror>. usage: bash mirror_pretest.sh <upload dir>
set -u
U=$1; B=$HOME/iwo_amorph
RUNS="aIO_0p7_s1 aIO_1p0_s1 aIO_1p5_s1 aIO_2p0_s1 aIO_2p0_s2 aIWO_0p7_s1 aIWO_0p7_s1_bare aIWO_0p8_s2
      aIWO_1p0_Al2O3_s2 aIWO_1p0_s1 aIWO_1p5_s1 aIWO_2p0_Al2O3_s2 aIWO_2p0_comp_s1 aIWO_2p0_s1 aIWO_2p0_s1_bare aIWO_2p0_s2"
BENCH=aIWO_1p0_Al2O3_s2
M=$(mktemp -d /tmp/d24v2c_mirror.XXXX); T=$M/iwo_amorph; mkdir -p "$T/common" "$T/runs/aIO_0p8_s1"
( cd "$B/common" && cp -p relax_node.sh driver.sh qeio.py relax_node.sh.D24 geomsel.py.D24 d24_transition.sh install_D24_BD.sh \
    README_D24_BD.txt D24_BD_staged.md5 D24_BD_baseline.md5 "$T/common/" )
cp -p "$B/runs/aIO_0p8_s1/geomsel.py" "$B/runs/aIO_0p8_s1/relax.sub" "$B/runs/aIO_0p8_s1/steps_relax.sh" "$T/runs/aIO_0p8_s1/"
for r in $RUNS; do
  mkdir -p "$T/runs/$r"
  ( cd "$B/runs/$r" && cp -p relax.sub steps_relax.sh relax.sub.D24 steps_relax.sh.D24 relax.in "$T/runs/$r/" \
    && for f in RELAX_STATUS relax.sub.D24_2gpu relax_s*_results.tar.gz; do [ -e "$f" ] && cp -p "$f" "$T/runs/$r/"; done; true )
done
for f in README_D24_BD.txt install_D24_BD.sh d24_transition.sh; do cp "$U/$f" "$T/common/$f.tmp" && chmod --reference="$T/common/$f" "$T/common/$f.tmp" && mv -f "$T/common/$f.tmp" "$T/common/$f"; done
( cd "$T" && { md5sum common/relax_node.sh.D24 common/geomsel.py.D24 common/d24_transition.sh runs/$BENCH/relax.sub.D24_2gpu
  for r in $RUNS; do md5sum runs/$r/relax.sub.D24 runs/$r/steps_relax.sh.D24; done; } > common/D24_BD_staged.md5 )
echo "mirror $T: $(find "$T" -type f | wc -l) files; manifest diff vs AFS:"; diff "$B/common/D24_BD_staged.md5" "$T/common/D24_BD_staged.md5"
D24_TREE=$T bash "$U/test_D24_BD.sh" "$U"
