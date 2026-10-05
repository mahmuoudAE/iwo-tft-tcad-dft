"""Is the valence-band maximum (VBM) of a pure slab a surface state? (projwfc.x projections, no new calculation)

Usage: python surface_state_check.py <job folder with scf.in, scf.out, projwfc_*.out>
Measure (defined before looking at the result, 2026-10-05): for the band-edge states (VBM = band n_occ, CBM = n_occ+1,
at every irreducible k-point of the SCF grid) the projected weight per atom is summed over the atomic states of each
atom. Reported:
  * share of the projected weight on the surface OH groups (H atoms and the O atoms bonded to an H), compared with the
    share of these atoms among all atoms (number fraction) and among the O atoms;
  * the weight profile along z in slices of a/8 (about 1.3 A);
  * the same for a deeper valence state (VBM - 20 bands) as a reference.
A surface state would put a weight on the OH groups far above their number fraction and peak at the outer slices.
"""
import re
import sys
from pathlib import Path

import numpy as np

d = Path(sys.argv[1])
inp = (d / 'scf.in').read_text()
cell = np.array([[float(x) for x in l.split()] for l in inp.split('CELL_PARAMETERS angstrom')[1].strip().splitlines()[:3]])
pos_block = inp.split('ATOMIC_POSITIONS crystal')[1].split('K_POINTS')[0].strip().splitlines()
sym = [l.split()[0] for l in pos_block]
frac = np.array([[float(x) for x in l.split()[1:4]] for l in pos_block])
cart = frac @ cell
z = cart[:, 2]
nat = len(sym)
# surface OH: O within 1.15 A of an H
H = [i for i, s in enumerate(sym) if s == 'H']
O = [i for i, s in enumerate(sym) if s == 'O']
oh_O = set()
for h in H:
    for o in O:
        dv = cart[o] - cart[h]
        dv[:2] -= np.rint(np.linalg.solve(cell[:2, :2].T, dv[:2])) @ cell[:2, :2]
        if np.linalg.norm(dv) < 1.15:
            oh_O.add(o)
surf = set(H) | oh_O
scf = (d / 'scf.out').read_text(errors='replace')
nocc = int(round(float(re.search(r'number of electrons\s+=\s+([\d.]+)', scf).group(1)))) // 2
pj = next(d.glob('projwfc_*.out')).read_text(errors='replace')
state_atom = {int(m.group(1)): int(m.group(2)) - 1 for m in re.finditer(r'state #\s*(\d+): atom\s+(\d+)', pj)}
blocks = re.split(r'\n\s*k =\s+', pj)[1:]


def weights(band):
    """per-atom projected weight of one band, k-averaged with equal weights over the listed k-points; band energies"""
    w = np.zeros(nat); es = []
    for b in blocks:
        m = re.search(r'==== e\(\s*%d\) =\s*(-?[\d.]+) eV ====(.*?)(?:\|psi\|\^2 = ([\d.]+))' % band, b, re.S)
        if not m:
            continue
        es.append(float(m.group(1)))
        for c, s in re.findall(r'([\d.]+)\*\[#\s*(\d+)\]', m.group(2)):
            w[state_atom[int(s)]] += float(c)
    return w / max(len(es), 1), es


zs = np.linspace(z.min() - 0.01, z.max() + 0.01, 9)
mid = 0.5 * (z.min() + z.max())
print(f'{d.name}: {nat} atoms, n_occ = {nocc}, k-point blocks {len(blocks)}; surface OH atoms {len(surf)} ({len(surf) / nat:.1%} of atoms), '
      f'OH-O {len(oh_O)} of {len(O)} O ({len(oh_O) / len(O):.1%})')
for name, band in (('VBM', nocc), ('CBM', nocc + 1), ('VBM-20 (reference)', nocc - 20)):
    w, es = weights(band)
    tot = w.sum()
    sh = sum(w[i] for i in surf) / tot
    oO = sum(w[i] for i in oh_O) / max(sum(w[i] for i in O), 1e-12)
    byel = {e: sum(w[i] for i in range(nat) if sym[i] == e) / tot for e in ('In', 'O', 'H')}
    prof = [sum(w[i] for i in range(nat) if lo <= z[i] < hi) / tot for lo, hi in zip(zs[:-1], zs[1:])]
    print(f'  {name:20} E {min(es):.3f}..{max(es):.3f} eV | weight on surface OH {sh:.1%} (number share {len(surf) / nat:.1%}); '
          f'OH-O share of the O weight {oO:.1%} (number {len(oh_O) / len(O):.1%}); by element ' + ', '.join(f'{k} {v:.1%}' for k, v in byel.items()))
    print('      z profile (8 slices, bottom->top): ' + ' '.join(f'{p:.2f}' for p in prof))
