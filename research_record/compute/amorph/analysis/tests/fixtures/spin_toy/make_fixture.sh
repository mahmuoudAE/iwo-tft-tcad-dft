#!/bin/bash
# Real QE 7.5 nspin = 2 fixture for the read-out tests (A27 C6 path). A 5-atom TOY cell: a triplet O2 molecule
# (1.21 A) and a closed-shell H2O molecule in a 10 x 8 x 8 A box; PAW psl 1.0.0, 45/360 Ry, local-TF mixing,
# Gaussian 0.01 Ry, 2 k-points without symmetry. The O labels are split (O1 on O2, O2 on H2O) so the two spin starts
# differ by species. File-format and spin-accounting fixture only, NOT a physics result (no W: the W-5d spin path is
# covered by the synthetic tests). With N_ex = 2 (the two pi* electrons above N_v = 9) the accounting closes in both
# nspin = 1 and nspin = 2. Three runs at identical geometry and settings:
#   ref   nspin = 1
#   spinA nspin = 2, localised start  (starting_magnetization: O2 molecule 0.5, others 0)
#   spinB nspin = 2, uniform start    (starting_magnetization: 0.1 on every species)
# each followed by projwfc.x (Loewdin projections -> atomic_proj.xml). The kept files are gzipped next to this script.
# usage (WSL Ubuntu-22.04): bash make_fixture.sh <pseudo dir> [work dir]
set -euo pipefail
PSEUDO=${1:?pseudo dir}
OUT=$(cd "$(dirname "$0")" && pwd)
W=${2:-/tmp/iwo_spin_fixture}
BIN=${QE_BIN:-$HOME/miniforge3/envs/qe/bin}
NP=${NP:-4}
export OMP_NUM_THREADS=1
rm -rf "$W"; mkdir -p "$W"; cd "$W"
geom() {
cat <<'EOF'
CELL_PARAMETERS angstrom
  10.0 0.0 0.0
  0.0 8.0 0.0
  0.0 0.0 8.0
ATOMIC_POSITIONS angstrom
  O1  2.500 4.000 3.395
  O1  2.500 4.000 4.605
  O2  7.000 4.000 4.000
  H   7.757 4.586 4.000
  H   6.243 4.586 4.000
K_POINTS automatic
  2 1 1 0 0 0
EOF
}
run() {  # run <tag> <nspin> <starting magnetisation lines>
  local tag=$1 nspin=$2 mag=$3
  cat > "pw_$tag.in" <<EOF
&CONTROL
  calculation = 'scf', prefix = '$tag', outdir = './tmp', pseudo_dir = '$PSEUDO', verbosity = 'high'
/
&SYSTEM
  ibrav = 0, nat = 5, ntyp = 3, ecutwfc = 45, ecutrho = 360, nosym = .true.
  occupations = 'smearing', smearing = 'gaussian', degauss = 0.01, nbnd = 16, nspin = $nspin
$mag
/
&ELECTRONS
  conv_thr = 1.0d-8, mixing_beta = 0.2, mixing_mode = 'local-TF', electron_maxstep = 300
/
ATOMIC_SPECIES
  O1 15.999 O.pbe-n-kjpaw_psl.1.0.0.UPF
  O2 15.999 O.pbe-n-kjpaw_psl.1.0.0.UPF
  H  1.008 H.pbe-kjpaw_psl.1.0.0.UPF
$(geom)
EOF
  "$BIN/mpirun" -np "$NP" "$BIN/pw.x" -in "pw_$tag.in" > "pw_$tag.out" 2>&1
  grep -q 'convergence has been achieved' "pw_$tag.out"
  printf "&PROJWFC\n  prefix = '%s', outdir = './tmp', filpdos = 'pdos_%s'\n/\n" "$tag" "$tag" > "projwfc_$tag.in"
  "$BIN/mpirun" -np "$NP" "$BIN/projwfc.x" -in "projwfc_$tag.in" > "projwfc_$tag.out" 2>&1
  for f in data-file-schema.xml atomic_proj.xml; do gzip -c "tmp/$tag.save/$f" > "$OUT/${f%.xml}_$tag.xml.gz"; done
  gzip -c "projwfc_$tag.out" > "$OUT/projwfc_$tag.out.gz"
  cp "pw_$tag.in" "$OUT/"
  gzip -c "pw_$tag.out" > "$OUT/pw_$tag.out.gz"
  echo "$tag: $(grep -m1 '^!' "pw_$tag.out"); $(grep 'total magnetization' "pw_$tag.out" | tail -1)"
}
run ref 1 ""
run spinA 2 "  starting_magnetization(1) = 0.5"
run spinB 2 "  starting_magnetization(1) = 0.1, starting_magnetization(2) = 0.1, starting_magnetization(3) = 0.1"
( cd "$OUT" && sha256sum ./*.gz ./*.in > SHA256SUMS )
echo "fixture written to $OUT"
