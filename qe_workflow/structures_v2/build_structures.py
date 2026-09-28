"""Build and verify every structure used for the CERN (HTCondor) stage of the DFT study.

Usage (WSL, qe env):  python build_structures.py <vc-relax output | exp> <output folder>

The host is the PBE-relaxed bixbyite cell of stage 2 (or, with 'exp', the experimental structure of
M. Marezio, Acta Cryst. 20, 723 (1966), used only to test this script). Structures written:

  bulk_conv   80-atom conventional cell (Ia-3), standardized with spglib
  iwo_W8b     one In on an 8b site replaced by W  (In31 W O48, W/(W+In) = 3.1 %)
  iwo_W24d    one In on a 24d site replaced by W
  slab1_vNN   slab made with the recipe of Lin et al., ACS Nano 16, 21536 (2022), p. 21542:
              conventional cell, the In layer at the cell boundary removed, the top and bottom O
              layers passivated with one H per O, NN angstrom of vacuum
  slab2_v25   the same recipe applied to the 1x1x2 supercell

Every structure is checked (composition, electron count, symmetry, bond lengths, minimum distances);
a failed check stops the script. Output: one JSON file per structure (cell and Cartesian positions
in angstrom) and summary.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import spglib
from ase import Atoms
from ase.io import read
from ase.neighborlist import neighbor_list
from ase.spacegroup import crystal

SYMPREC = 1e-3
D_OH = 0.97        # O-H bond length of a surface hydroxyl (A), starting value before relaxation
Z = {'In': 49, 'W': 74, 'O': 8, 'H': 1}


def spg(at):
    return spglib.get_symmetry_dataset((at.cell[:], at.get_scaled_positions(), at.numbers), symprec=SYMPREC)


def host(src):
    if src == 'exp':
        at = crystal(['In', 'In', 'O'], basis=[(0.25, 0.25, 0.25), (-0.0336, 0.0, 0.25), (0.3905, 0.1529, 0.3832)],
                     spacegroup=206, cellpar=[10.117, 10.117, 10.117, 90, 90, 90])
        origin = 'experimental structure, Marezio (1966)'
    else:
        prim = read(src, format='espresso-out', index=-1)
        lat, pos, num = spglib.standardize_cell((prim.cell[:], prim.get_scaled_positions(), prim.numbers),
                                                to_primitive=False, no_idealize=False, symprec=SYMPREC)
        at = Atoms(numbers=num, cell=lat, scaled_positions=pos, pbc=True)
        origin = f'PBE vc-relax output {src}, primitive volume {prim.get_volume():.4f} A^3'
    ds = spg(at)
    a = at.cell.lengths()
    assert len(at) == 80, len(at)
    assert ds.number == 206 and len(ds.rotations) == 48, (ds.number, len(ds.rotations))
    assert np.allclose(a, a[0], atol=1e-4) and np.allclose(at.cell.angles(), 90, atol=1e-3)
    i, j, d = neighbor_list('ijd', at, 2.6)
    ino = np.unique(np.round(d[(at.numbers[i] == 49) & (at.numbers[j] == 8)], 3))
    info = {'origin': origin, 'a_A': round(float(a[0]), 5), 'spacegroup': f'{ds.international} ({ds.number})',
            'n_ops': len(ds.rotations), 'In_O_bonds_A': ino.tolist()}
    return at, ds, info


def substitute(at, ds, letter):
    idx = next(k for k in range(len(at)) if at.numbers[k] == 49 and ds.wyckoffs[k] == letter)
    d = at.copy()
    d.numbers[idx] = Z['W']
    ds2 = spg(d)
    i, j, dist = neighbor_list('ijd', d, 2.6)
    wo = np.sort(dist[(i == idx) & (d.numbers[j] == 8)])
    nIn, nO = (d.numbers == 49).sum(), (d.numbers == 8).sum()
    expected_ops = 48 // {'b': 8, 'd': 24}[letter]          # orbit-stabilizer: 48 operations / site multiplicity
    assert len(ds2.rotations) == expected_ops, (letter, len(ds2.rotations))
    assert len(wo) == 6 and wo.max() < 2.4
    info = {'W_site': f'{letter} (host site symmetry {ds.site_symmetry_symbols[idx]})', 'W_index': int(idx),
            'formula': f'In{nIn}W1O{nO}', 'cation_fraction_W': round(1 / (nIn + 1), 5),
            'spacegroup': f'{ds2.international} ({ds2.number})', 'n_ops': len(ds2.rotations),
            'W_O_unrelaxed_A': np.round(wo, 4).tolist(),
            'extra_electrons_vs_host': 3}
    return d, info


def lin_slab(conv, nz, vac):
    """Lin et al. 2022 recipe: remove the cation layer at the cell boundary, one H per O that lost In neighbours."""
    sup = conv.repeat((1, 1, nz))
    c = sup.cell[2, 2]
    z = sup.positions[:, 2] % c
    cat = np.isin(sup.numbers, [Z['In'], Z['W']])
    rm = cat & (np.minimum(z, c - z) < 0.6)            # the cation layer at z = 0 is corrugated by about +-0.35 A
    assert rm.sum() == 8, rm.sum()
    i, j, D = neighbor_list('ijD', sup, 2.6)
    lost, coord_after = {}, {}
    for o in np.where(sup.numbers == Z['O'])[0]:
        m = (i == o) & cat[j]
        gone = m & rm[j]
        if gone.any():
            lost[o] = D[gone].sum(axis=0)
            coord_after[o] = int((m & ~rm[j]).sum())
    h = np.array([sup.positions[o] + D_OH * v / np.linalg.norm(v) for o, v in lost.items()])
    keep = ~rm
    slab = Atoms(numbers=np.concatenate([sup.numbers[keep], np.ones(len(h), int)]),
                 positions=np.vstack([sup.positions[keep], h]), cell=sup.cell[:], pbc=True)
    zmin, zmax = slab.positions[:, 2].min(), slab.positions[:, 2].max()
    slab.cell[2] = [0, 0, (zmax - zmin) + vac]
    slab.positions[:, 2] += vac / 2 - zmin
    nIn, nO, nH = [(slab.numbers == Z[s]).sum() for s in ('In', 'O', 'H')]
    assert 3 * nIn + nH == 2 * nO, ('electron count', nIn, nO, nH)   # In3+, O2-, H+: closed shell
    # geometry checks
    i2, j2, d2 = neighbor_list('ijd', slab, 3.0)
    pairs = [(slab.numbers[a], slab.numbers[b], dd) for a, b, dd in zip(i2, j2, d2) if a < b]
    oh = [dd for x, y, dd in pairs if {x, y} == {1, 8} and dd < 1.2]
    assert len(oh) == nH and all(abs(x - D_OH) < 1e-6 for x in oh)
    others = [dd for x, y, dd in pairs if not ({x, y} == {1, 8} and dd < 1.2) and not ({x, y} == {49, 8} and dd < 2.4)]
    dmin_other = min(others)
    assert dmin_other > 1.4, ('close contact', dmin_other)
    zs = slab.positions[:, 2]
    zO = zs[slab.numbers == 8]
    zc = slab.cell[2, 2] / 2
    top = sum(1 for o in lost if sup.positions[o, 2] > c / 2)
    ds = spg(slab)
    flips = [r for r in ds.rotations if r[2, 2] == -1]
    info = {'recipe': 'Lin et al. ACS Nano 16, 21536 (2022), p. 21542', 'supercell': f'1x1x{nz}',
            'formula': f'In{nIn}O{nO}H{nH}', 'n_atoms': len(slab), 'removed_cations': int(rm.sum()),
            'H_top_bottom': [top, len(lost) - top],
            'surface_O_In_coordination_after_removal': {str(k): list(coord_after.values()).count(k)
                                                        for k in sorted(set(coord_after.values()))},
            'thickness_O_to_O_A': round(float(zO.max() - zO.min()), 3),
            'thickness_H_to_H_A': round(float(zs.max() - zs.min()), 3),
            'vacuum_A': vac, 'cell_c_A': round(float(slab.cell[2, 2]), 4),
            'inplane_a_A': round(float(slab.cell[0, 0]), 5),
            'spacegroup': f'{ds.international} ({ds.number})', 'n_ops': len(ds.rotations),
            'surfaces_equivalent_by_symmetry': bool(flips),
            'min_distance_nonbonded_A': round(float(dmin_other), 3), 'slab_centre_z_A': round(float(zc), 3)}
    return slab, info


def save(at, name, info, out):
    rec = {'name': name, 'cell_A': np.round(at.cell[:], 8).tolist(), 'symbols': at.get_chemical_symbols(),
           'positions_A': np.round(at.positions, 8).tolist(), 'checks': info}
    (out / f'{name}.json').write_text(json.dumps(rec, indent=1))


def main():
    src, out = sys.argv[1], Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    conv, ds, hinfo = host(src)
    summary = {'bulk_conv': hinfo}
    save(conv, 'bulk_conv', hinfo, out)
    for letter in ('b', 'd'):
        d, info = substitute(conv, ds, letter)
        name = f'iwo_W{"8b" if letter == "b" else "24d"}'
        save(d, name, info, out)
        summary[name] = info
    for nz, vac in ((1, 15.0), (1, 25.0), (1, 35.0), (2, 25.0)):
        s, info = lin_slab(conv, nz, vac)
        name = f'slab{nz}_v{int(vac)}'
        save(s, name, info, out)
        summary[name] = info
    (out / 'summary.json').write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == '__main__':
    main()
