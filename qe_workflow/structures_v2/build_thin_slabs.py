"""Thinner In2O3 (001) slabs with the termination of Lin et al. (2022) - N cation layers kept (2026-10-05).

Usage (WSL, qe env):  python build_thin_slabs.py <bulk vc-relax output> <output folder>

Generalization of build_structures.lin_slab. In the conventional bixbyite cell the cations form four (001) planes
(z = 0, c/4, c/2, 3c/4; corrugated by about +-0.35 A) and every O bonds to four cations. A slab with N contiguous
cation planes keeps those cations, every O bonded to at least one kept cation, and puts one H on each O that lost
cation neighbours (along the sum of its lost bond vectors, O-H 0.97 A), exactly as in lin_slab. A kept O must have
2 or 4 kept bonds (asserted), so one H per surface O gives the closed shell 3 nIn + nH = 2 nO.

Check: N = 3 (planes c/4, c/2, 3c/4) must reproduce slab1_v25 of build_structures.py (same composition and the same
positions up to a rigid translation). Written: slabL1_v25 (N = 1, In8 O24 H24) and slabL2_v25 (N = 2, In16 O36 H24).
"""
import json
import sys
from pathlib import Path

import numpy as np
from ase import Atoms
from ase.neighborlist import neighbor_list

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_structures import D_OH, Z, host, save, spg  # noqa: E402


def thin_slab(conv, planes, vac):
    c = conv.cell[2, 2]
    z = conv.positions[:, 2] % c
    cat = np.isin(conv.numbers, [Z['In'], Z['W']])
    plane = np.rint(z / (c / 4)).astype(int) % 4                    # cation plane index 0..3 (corrugation << c/8)
    assert np.all(np.abs(z[cat] - np.rint(z[cat] / (c / 4)) * (c / 4)) < 0.6), 'cation not on a (001) plane'
    kept_cat = cat & np.isin(plane, planes)
    i, j, D = neighbor_list('ijD', conv, 2.6)
    keep_o, lost = [], {}
    for o in np.where(conv.numbers == Z['O'])[0]:
        m = (i == o) & cat[j]
        nk, nl = int((m & kept_cat[j]).sum()), int((m & ~kept_cat[j]).sum())
        assert nk + nl == 4, ('O coordination', o, nk + nl)
        if nk == 0:
            continue
        assert nk in (2, 4), ('kept O with', nk, 'kept bonds')
        keep_o.append(o)
        if nl:
            lost[o] = D[m & ~kept_cat[j]].sum(axis=0)
    # unwrap kept atoms around the kept cations (the slab must not straddle the cell boundary in z)
    zc = np.mean(conv.positions[kept_cat, 2])
    idx = np.concatenate([np.where(kept_cat)[0], np.array(keep_o, int)])
    pos = conv.positions[idx].copy()
    pos[:, 2] -= c * np.rint((pos[:, 2] - zc) / c)
    opos = {o: pos[len(np.where(kept_cat)[0]) + k] for k, o in enumerate(keep_o)}
    h = np.array([opos[o] + D_OH * v / np.linalg.norm(v) for o, v in lost.items()])
    num = np.concatenate([conv.numbers[idx], np.ones(len(h), int)])
    slab = Atoms(numbers=num, positions=np.vstack([pos, h]), cell=conv.cell[:], pbc=True)
    zmin, zmax = slab.positions[:, 2].min(), slab.positions[:, 2].max()
    slab.cell[2] = [0, 0, (zmax - zmin) + vac]
    slab.positions[:, 2] += vac / 2 - zmin
    nIn, nO, nH = [(slab.numbers == Z[s]).sum() for s in ('In', 'O', 'H')]
    assert 3 * nIn + nH == 2 * nO, ('electron count', nIn, nO, nH)
    i2, j2, d2 = neighbor_list('ijd', slab, 3.0)
    pairs = [(slab.numbers[a], slab.numbers[b], dd) for a, b, dd in zip(i2, j2, d2) if a < b]
    oh = [dd for x, y, dd in pairs if {x, y} == {1, 8} and dd < 1.2]
    assert len(oh) == nH and all(abs(x - D_OH) < 1e-6 for x in oh), 'O-H bonds'
    others = [dd for x, y, dd in pairs if not ({x, y} == {1, 8} and dd < 1.2) and not ({x, y} == {49, 8} and dd < 2.4)]
    dmin = min(others)
    assert dmin > 1.4, ('close contact', dmin)
    zs = slab.positions[:, 2]
    zO = zs[slab.numbers == 8]
    ds = spg(slab)
    flips = [r for r in ds.rotations if r[2, 2] == -1]
    zH = zs[slab.numbers == 1]
    mid = 0.5 * (zs.max() + zs.min())
    info = {'recipe': 'Lin et al. ACS Nano 16, 21536 (2022), p. 21542, generalized to N cation planes (build_thin_slabs.py)',
            'cation_planes_kept': [int(p) for p in planes], 'formula': f'In{nIn}O{nO}H{nH}', 'n_atoms': len(slab),
            'H_top_bottom': [int((zH > mid).sum()), int((zH < mid).sum())],
            'thickness_O_to_O_A': round(float(zO.max() - zO.min()), 3),
            'thickness_H_to_H_A': round(float(zs.max() - zs.min()), 3),
            'vacuum_A': vac, 'cell_c_A': round(float(slab.cell[2, 2]), 4), 'inplane_a_A': round(float(slab.cell[0, 0]), 5),
            'spacegroup': f'{ds.international} ({ds.number})', 'n_ops': len(ds.rotations),
            'surfaces_equivalent_by_symmetry': bool(flips), 'min_distance_nonbonded_A': round(float(dmin), 3)}
    return slab, info


def same_up_to_translation(a, b):
    """Same species and positions (mod in-plane lattice) after aligning the centroids."""
    if sorted(a.get_chemical_symbols()) != sorted(b['symbols']):
        return False, 'composition differs'
    pb = np.array(b['positions_A'])
    pa = a.positions - a.positions.mean(axis=0) + pb.mean(axis=0)
    cell = np.array(b['cell_A'])
    worst = 0.0
    for s in set(b['symbols']):
        A, B = pa[np.array(a.get_chemical_symbols()) == s], pb[np.array(b['symbols']) == s]
        for p in A:
            d = B - p
            d[:, :2] -= np.rint(d[:, :2] @ np.linalg.inv(cell[:2, :2])) @ cell[:2, :2]
            worst = max(worst, np.linalg.norm(d, axis=1).min())
    return worst < 1e-3, f'max deviation {worst:.2e} A'


def main():
    src, out = sys.argv[1], Path(sys.argv[2])
    conv, ds, hinfo = host(src)
    ref = json.loads((out / 'slab1_v25.json').read_text())
    s3, i3 = thin_slab(conv, [1, 2, 3], 25.0)
    ok, msg = same_up_to_translation(s3, ref)
    print(f'check N=3 vs slab1_v25: {i3["formula"]}, {msg} -> {"PASS" if ok else "FAIL"}')
    assert ok, 'the generalized recipe does not reproduce slab1_v25'
    summary = {}
    for name, planes in (('slabL1_v25', [2]), ('slabL2_v25', [1, 2])):
        s, info = thin_slab(conv, planes, 25.0)
        save(s, name, info, out)
        summary[name] = info
    print(json.dumps(summary, indent=1))


if __name__ == '__main__':
    main()
