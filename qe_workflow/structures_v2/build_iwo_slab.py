"""IWO slab from the relaxed pure slab (design recorded in PROTOCOL_CERN.md before any run).

Usage: python build_iwo_slab.py <relaxed slab vc-relax output> <name> <outdir>
Writes <name>_pure.json (relaxed pure slab, for the CPU re-run of the band edges) and <name>_W24d.json:
one In of the central cation layer replaced by W. In the conventional-cell slabs that layer (z = 1/2 of the
cell) holds only 24d cations, the site W prefers in bulk (dE = 0.258 eV). Checks: composition, W-O bonds,
nearest cation to the slab centre, and whether a symmetry operation maps z -> -z (then no slab dipole).
"""
import json
import sys
from pathlib import Path

import numpy as np
import spglib
from ase.io import read
from ase.neighborlist import neighbor_list


def save(at, path, checks):
    path.write_text(json.dumps({'cell_A': np.round(at.cell[:], 8).tolist(), 'symbols': at.get_chemical_symbols(),
                                'positions_A': np.round(at.positions, 8).tolist(), 'checks': checks}, indent=1))


def main():
    src, name, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    pure = read(src, format='espresso-out', index=-1)
    zc = pure.positions[:, 2].mean()
    cat = [i for i, s in enumerate(pure.get_chemical_symbols()) if s == 'In']
    k = min(cat, key=lambda i: abs(pure.positions[i, 2] - zc))
    doped = pure.copy(); doped.symbols[k] = 'W'
    i, j, d = neighbor_list('ijd', doped, 2.6)
    wo = np.sort(d[(i == k) & (doped.numbers[j] == 8)])
    ds = spglib.get_symmetry_dataset((doped.cell[:], doped.get_scaled_positions(), doped.numbers), symprec=1e-3)
    flip = any(r[2, 2] == -1 for r in ds.rotations)
    n = {s: doped.get_chemical_symbols().count(s) for s in ('In', 'W', 'O', 'H')}
    checks = {'source': src, 'W_index': int(k), 'W_distance_from_centre_A': round(float(abs(pure.positions[k, 2] - zc)), 3),
              'formula': f"In{n['In']}W{n['W']}O{n['O']}H{n['H']}", 'W_cation_fraction': round(1 / (n['In'] + 1), 4),
              'W_O_unrelaxed_A': np.round(wo, 3).tolist(), 'spacegroup': f'{ds.international} ({ds.number})', 'n_ops': len(ds.rotations),
              'z_flip_symmetry': bool(flip), 'dipole_correction_needed': not flip,
              'extra_electrons_vs_pure': 3}
    assert len(wo) == 6 and wo.max() < 2.4, wo
    save(pure, out / f'{name}_pure.json', {'source': src})
    save(doped, out / f'{name}_W24d.json', checks)
    print(json.dumps(checks, indent=1))


if __name__ == '__main__':
    main()
