"""Crystallographic data for the 3D dashboard (run with the WSL qe-env python: ASE 3.29 + spglib 2.7).
Conventional cell: built from the Ia-3 definition (Marezio 1966 Wyckoff parameters), as in build_structure.py.
Primitive cell: read from structure_primitive.json, i.e. exactly the 40 atoms used in the pw.x inputs.
Writes structure_display.json: lattice, positions, Wyckoff letters, site symmetries, periodic neighbour lists
(ASE neighbor_list with shift vectors), unique pair distances by element pair, coordination numbers, cell data."""
import json
from collections import Counter, defaultdict
import numpy as np, spglib
from ase import Atoms
from ase.spacegroup import crystal
from ase.neighborlist import neighbor_list

A = 10.117
MAREZIO = [('In', '8b', (0.25, 0.25, 0.25)), ('In', '24d', (-0.0336, 0.0, 0.25)), ('O', '48e', (0.3905, 0.1529, 0.3832))]
conv = crystal([s for s, _, _ in MAREZIO], basis=[p for _, _, p in MAREZIO], spacegroup=206, cellpar=[A, A, A, 90, 90, 90])
P = json.load(open('structure_primitive.json'))
prim = Atoms(symbols=P['species'], scaled_positions=P['frac'], cell=P['lattice_A'], pbc=True)
MASS = {'In': 114.818, 'O': 15.999}; NA = 6.02214076e23

def describe(at, cut=3.8):
    ds = spglib.get_symmetry_dataset((at.cell[:], at.get_scaled_positions(), at.numbers), symprec=1e-4)
    sym = at.get_chemical_symbols()
    i, j, d, S = neighbor_list('ijdS', at, cut)
    nb = [[int(a), int(b), round(float(c), 4), [int(x) for x in s]] for a, b, c, s in zip(i, j, d, S)]
    pairs = defaultdict(Counter)                       # unique pairs: i<j, or i==j with the lexicographically positive shift
    for a, b, c, s in zip(i, j, d, S):
        if a < b or (a == b and tuple(s) > tuple(-s)):
            key = '-'.join(sorted([sym[a], sym[b]], key=lambda e: e != 'In'))
            pairs[key][round(float(c), 3)] += 1
    cn = [int(sum(1 for a, b, c, _ in zip(i, j, d, S) if a == k and c < 2.6 and sym[b] != sym[k])) for k in range(len(at))]
    vol = at.get_volume(); mass = sum(MASS[s] for s in sym) / NA
    return {'lattice': np.round(at.cell[:], 6).tolist(), 'frac': np.round(at.get_scaled_positions(), 8).tolist(), 'species': sym,
            'wyckoff': [str(w) for w in ds.wyckoffs], 'site_symmetry': [str(x) for x in ds.site_symmetry_symbols],
            'spacegroup': ds.international, 'number': int(ds.number), 'pointgroup': ds.pointgroup, 'n_ops': len(ds.rotations),
            'n_ops_with_translation': int(sum(1 for t in ds.translations if np.linalg.norm(t - np.round(t)) > 1e-6)),
            'neighbors': nb, 'pair_distances': {k: sorted([[dd, n] for dd, n in v.items()]) for k, v in pairs.items()},
            'coordination': cn, 'volume_A3': round(vol, 4), 'density_g_cm3': round(mass / (vol * 1e-24), 4),
            'formula_units': sym.count('In') // 2, 'natoms': len(at)}

out = {'conventional': describe(conv), 'primitive': describe(prim), 'a_A': A,
       'marezio': [{'element': s, 'wyckoff': w, 'x': p[0], 'y': p[1], 'z': p[2]} for s, w, p in MAREZIO],
       'note': 'Conventional cell regenerated from the Ia-3 definition; primitive cell identical to the pw.x inputs.'}
json.dump(out, open('structure_display.json', 'w'))
for k in ('conventional', 'primitive'):
    d = out[k]
    print(k, d['natoms'], 'atoms', d['spacegroup'], d['n_ops'], 'ops', 'density', d['density_g_cm3'], 'g/cm3',
          'CN In', sorted(set(c for c, s in zip(d['coordination'], d['species']) if s == 'In')),
          'CN O', sorted(set(c for c, s in zip(d['coordination'], d['species']) if s == 'O')),
          'wyckoff', dict(Counter(zip(d['species'], d['wyckoff']))))
print('In-O distances (conv):', out['conventional']['pair_distances']['In-O'][:6])
print('In-In shortest (conv):', out['conventional']['pair_distances'].get('In-In', [])[:3], ' O-O shortest:', out['conventional']['pair_distances'].get('O-O', [])[:3])
