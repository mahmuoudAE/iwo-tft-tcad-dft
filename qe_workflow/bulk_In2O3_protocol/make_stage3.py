"""Stage 3 inputs: electronic structure of the PBE-relaxed bulk In2O3 (after stage 2).

Both runs are non-self-consistent ('bands') on the density of the final SCF of the vc-relax (prefix 'vcr'),
with the final cell and positions of vcrelax_ecut71_k3.out and the stage-1 settings (71 Ry, nbnd 190).
  bands_path.in   Gamma-H-N-Gamma-P-H|P-N of the bcc Brillouin zone (path of W. Setyawan and
                  S. Curtarolo, Comput. Mater. Sci. 49, 299 (2010)), about 15 points per 2*pi/a
  bands_gamma.in  Gamma plus 10 points along [100], [110] and [111], |k| <= 0.15 1/A, for the
                  conduction-band mass (parabolic fit within 0.05 1/A, protocol section 5)
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'cern_htcondor' / 'jobs' / 'common'))
import qeio  # noqa: E402

out = open('vcrelax_ecut71_k3.out').read()
if 'End final coordinates' not in out:
    sys.exit('stage 2 has not finished: no final coordinates')
tmpl = open('scf_ecut71_k3.in').read()
old = "calculation = 'scf', prefix = 'ec71'"
assert old in tmpl
tmpl = tmpl.replace(old, "calculation = 'bands', prefix = 'vcr', verbosity = 'high'")
# first attempt (Davidson) aborted in pool 2 after 9 of 16 k-points with 'eigenvalues not converged' warnings
# (MPI abort, error code 251); conjugate-gradient diagonalization is slower but robust for non-SCF runs
assert 'mixing_beta = 0.4' in tmpl
tmpl = tmpl.replace('mixing_beta = 0.4', "mixing_beta = 0.4, diagonalization = 'cg'")
cell, pos = qeio.final_geometry(out)
tmpl = qeio.replace_card(qeio.replace_card(tmpl, 'CELL_PARAMETERS', cell), 'ATOMIC_POSITIONS', pos)
a1 = np.array([float(x) for x in cell[1].split()])
alat = np.linalg.norm(a1)                  # pw.x alat for ibrav = 0 with CELL_PARAMETERS angstrom
a_conv = 2 * alat / np.sqrt(3)             # conventional cubic lattice constant

# crystal coordinates on b1, b2, b3 of the primitive cell a1 = (-1,1,1)a/2, a2 = (1,-1,1)a/2, a3 = (1,1,-1)a/2
G, H, N, P = (0, 0, 0), (0.5, 0.5, -0.5), (0, 0, 0.5), (0.25, 0.25, 0.25)
cart = {G: (0, 0, 0), H: (0, 0, 1), N: (0.5, 0.5, 0), P: (0.5, 0.5, 0.5)}   # in units of 2*pi/a
path = [G, H, N, G, P, H, P, N]
jump_after = {5}                            # H|P: no points between H and the following P
lines = []
for i, k in enumerate(path):
    if i == len(path) - 1:
        n = 1
    elif i in jump_after:
        n = 1
    else:
        n = max(2, round(15 * np.linalg.norm(np.subtract(cart[path[i + 1]], cart[k]))))
    lines.append('  %.6f %.6f %.6f %d' % (*k, n))
card = ['K_POINTS crystal_b', f'  {len(path)}'] + lines
Path('bands_path.in').write_text(qeio.replace_card(tmpl, 'K_POINTS', card))

pts = [[0.0, 0.0, 0.0]]
for d in ([1, 0, 0], [1, 1, 0], [1, 1, 1]):
    u = np.array(d, float) / np.linalg.norm(d)
    pts += [list(u * 0.15 * i / 10 * alat / (2 * np.pi)) for i in range(1, 11)]
card = ['K_POINTS tpiba', f'  {len(pts)}'] + ['  %.8f %.8f %.8f 1.0' % tuple(k) for k in pts]
Path('bands_gamma.in').write_text(qeio.replace_card(tmpl, 'K_POINTS', card))
print(f'relaxed a = {a_conv:.5f} A (alat = {alat:.5f} A); path points {sum(int(l.split()[-1]) for l in lines)}; gamma set {len(pts)}')
