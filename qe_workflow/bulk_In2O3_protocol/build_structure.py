"""Build bixbyite In2O3 from its crystallographic definition and verify it (run with the WSL qe env python).
Space group Ia-3 (No. 206), a = 10.117 A; Wyckoff positions (M. Marezio, Acta Cryst. 20, 723 (1966)):
  In1 8b (1/4, 1/4, 1/4); In2 24d (u, 0, 1/4) with u = -0.0336; O 48e (0.3905, 0.1529, 0.3832).
Writes structure_primitive.json (40-atom primitive cell from spglib) after checks."""
import json
import numpy as np, spglib
from ase.spacegroup import crystal
from ase.neighborlist import neighbor_list
a = 10.117
conv = crystal(['In', 'In', 'O'], basis=[(0.25, 0.25, 0.25), (-0.0336, 0.0, 0.25), (0.3905, 0.1529, 0.3832)], spacegroup=206, cellpar=[a, a, a, 90, 90, 90])
syms = conv.get_chemical_symbols()
print('conventional cell atoms:', len(conv), {s: syms.count(s) for s in set(syms)})
cell = (conv.cell[:], conv.get_scaled_positions(), conv.numbers)
ds = spglib.get_symmetry_dataset(cell, symprec=1e-4)
print('space group:', ds.international, ds.number, '| symmetry operations (conventional):', len(ds.rotations))
i, j, d = neighbor_list('ij' + 'd', conv, 2.6)
ino = sorted({round(x, 3) for x, p, q in zip(d, i, j) if syms[p] == 'In' and syms[q] == 'O'})
print('In-O bond lengths < 2.6 A:', ino, '(expected about 2.12-2.23 A for In2O3)')
lat, pos, num = spglib.find_primitive(cell, symprec=1e-4)
print('primitive cell atoms:', len(num), '| lattice vectors (A):'); print(np.round(lat, 5))
dsp = spglib.get_symmetry_dataset((lat, pos, num), symprec=1e-4)
print('primitive: space group', dsp.international, '| operations:', len(dsp.rotations))
assert len(conv) == 80 and ds.number == 206 and len(num) == 40 and min(ino) > 2.0 and max(ino) < 2.3
json.dump({'lattice_A': lat.tolist(), 'frac': pos.tolist(), 'species': ['In' if n == 49 else 'O' for n in num],
           'source': 'Ia-3, a=10.117 A, Marezio 1966 Wyckoff parameters; primitive cell from spglib'}, open('structure_primitive.json', 'w'), indent=1)
print('CHECKS PASSED; wrote structure_primitive.json')
