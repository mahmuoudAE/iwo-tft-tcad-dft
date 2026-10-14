"""Geometry: cell mode (bulk / slab / interface), section-1 regions (A16, A24), first-shell O of W, atom matching.

Section 1 (frozen): "surface: atoms within 3.0 A of the outermost non-H atom of each face, plus H; interface: atoms
within 3.0 A of the film/oxide boundary plane; interior: the film atoms not in either."
A24 (interface cells): "the outer face is z < z(lowest substrate cation) + 3 A; the 'interface weight' counts only atoms
outside the outer face; outer-face atoms count in neither the interface nor the film interior; z_if is computed from
the substrate-cation p95 and the p5 of film cations not on the outer face."
A23 (ii): "for a bulk cell the interior means all atoms".

Distances along the slab normal are z distances (planar bands), as in mace_amorph.iface_partition(). The slab is
unwrapped across the periodic boundary at its largest empty z gap before any band is drawn.
"""
import itertools
import re

import numpy as np

from .register import (BULK_VACUUM_A, EPS, FILM_CATIONS, FORMAL_CHARGE, OUTER_FACE_A, REGION_CUT_A, SUBSTRATE_CATIONS,
                       W_O_FIRST_SHELL_A, Z_IF_PERCENTILES)


class Structure:
    def __init__(self, species, positions_A, cell_A, labels=None):
        self.species = list(species)
        self.pos = np.asarray(positions_A, dtype=float)
        self.cell = np.asarray(cell_A, dtype=float)
        self.labels = list(labels) if labels is not None else list(species)
        if self.pos.shape != (len(self.species), 3) or self.cell.shape != (3, 3):
            raise ValueError('structure: inconsistent shapes')

    @property
    def nat(self):
        return len(self.species)

    def count(self, el):
        return sum(1 for s in self.species if s == el)

    def composition(self):
        out = {}
        for s in self.species:
            out[s] = out.get(s, 0) + 1
        return out

    def formal_excess(self):
        """Excess electrons by formal charges (In+3, W+6, Al+3, Hf+4, H+1, O-2); None if another element is present."""
        if any(s not in FORMAL_CHARGE for s in self.species):
            return None
        return sum(FORMAL_CHARGE[s] for s in self.species)

    def geometry_hash(self):
        """sha256 of species, positions and cell rounded to 1e-4 A (binds certificates and comparisons)."""
        from .certify import geometry_hash
        return geometry_hash(self.species, self.pos, self.cell)

    def to_json(self):
        return {'species': self.species, 'labels': self.labels, 'positions_A': self.pos.round(6).tolist(),
                'cell_A': self.cell.round(6).tolist()}

    @classmethod
    def from_json(cls, d):
        return cls(d['species'], d['positions_A'], d['cell_A'], d.get('labels'))

    def distances_from(self, i, idx=None):
        """Minimum-image distances (A) from atom i to atoms idx (27 images; adequate for cutoffs below half a cell)."""
        idx = np.arange(self.nat) if idx is None else np.asarray(idx)
        d = self.pos[idx] - self.pos[i]
        best = np.full(len(idx), np.inf)
        for a, b, c in itertools.product((-1, 0, 1), repeat=3):
            sh = a * self.cell[0] + b * self.cell[1] + c * self.cell[2]
            best = np.minimum(best, np.linalg.norm(d + sh, axis=1))
        return best


def unwrap_z(st):
    """z (A) of every atom with the slab made contiguous: cut the cell at the largest empty z gap.
    Requires a3 along z and a1, a2 in the xy plane. Returns (z, origin_A, gap_A, c_A)."""
    a1, a2, a3 = st.cell
    if abs(a3[0]) > 1e-6 or abs(a3[1]) > 1e-6 or abs(a1[2]) > 1e-6 or abs(a2[2]) > 1e-6:
        raise ValueError('cell is not of slab form (a3 must be along z, a1 and a2 in the xy plane)')
    c = a3[2]
    frac = np.mod(st.pos[:, 2] / c, 1.0)
    order = np.argsort(frac)
    fs = frac[order]
    gaps = np.diff(np.concatenate([fs, [fs[0] + 1.0]]))
    g = int(np.argmax(gaps))
    start = fs[(g + 1) % len(fs)]
    z = np.mod(frac - start, 1.0) * c + start * c
    return z, start * c, gaps[g] * c, c


def detect_mode(st, name=None):
    """'bulk' (no vacuum gap >= 5 A), 'interface' (a substrate cation present), else 'slab'. The name is a
    cross-check only: a disagreement is returned as a warning."""
    warn = []
    try:
        _, _, gap, _ = unwrap_z(st)
        geo = 'bulk' if gap < BULK_VACUUM_A else 'slab'
    except ValueError:
        geo = 'bulk'
    if geo == 'slab' and any(s in SUBSTRATE_CATIONS for s in st.species):
        geo = 'interface'
    hint = None
    if name:
        if 'bulk' in name:
            hint = 'bulk'
        elif 'Al2O3' in name or 'HfO2' in name:
            hint = 'interface'
        elif re.search(r'_\d+p\d+', name):
            hint = 'slab'
    if hint and hint != geo:
        warn.append(f'cell name {name!r} suggests {hint}, geometry says {geo}')
    return geo, warn


def regions(st, mode):
    """Boolean masks (surface, interface, outer_face, film, oxide, interior, H) and the planes used."""
    nat = st.nat
    sp = np.array(st.species)
    H = sp == 'H'
    none = np.zeros(nat, dtype=bool)
    info = {'mode': mode, 'warnings': []}
    if mode == 'bulk':
        masks = {'H': H, 'surface': none.copy(), 'interface': none.copy(), 'outer_face': none.copy(),
                 'film': ~none, 'oxide': none.copy(), 'interior': ~none}
        info.update({'z_A': st.pos[:, 2].tolist(), 'interior_z_range_A': None})
        return _finish(masks, info, nat)
    z, origin, gap, c = unwrap_z(st)
    info.update({'z_origin_A': origin, 'vacuum_gap_A': gap, 'c_A': c})
    flip = False
    if mode == 'interface':
        sub = np.isin(sp, SUBSTRATE_CATIONS)
        fc = np.isin(sp, FILM_CATIONS)
        if not sub.any() or not fc.any():
            raise ValueError('interface cell without substrate or film cations')
        if z[sub].mean() > z[fc].mean():            # oxide on top: mirror so that the oxide is at the bottom
            z = -z
            flip = True
    info['orientation_flipped'] = flip
    nonH = ~H
    z_top, z_bot = float(z[nonH].max()), float(z[nonH].min())
    surface = H | (nonH & (z >= z_top - REGION_CUT_A - EPS)) | (nonH & (z <= z_bot + REGION_CUT_A + EPS))
    info.update({'z_top_nonH_A': z_top, 'z_bottom_nonH_A': z_bot})
    if mode == 'slab':
        masks = {'H': H, 'surface': surface, 'interface': none.copy(), 'outer_face': none.copy(), 'film': ~none,
                 'oxide': none.copy(), 'interior': ~surface}
    else:
        z_sc0 = float(z[sub].min())
        outer = z < z_sc0 + OUTER_FACE_A - EPS
        p_hi, p_lo = Z_IF_PERCENTILES
        z_if = float(0.5 * (np.percentile(z[sub], p_hi) + np.percentile(z[fc & ~outer], p_lo)))
        interface = (np.abs(z - z_if) <= REGION_CUT_A + EPS) & ~outer
        film = (z > z_if) & ~outer
        oxide = (z <= z_if) & ~outer
        masks = {'H': H, 'surface': surface, 'interface': interface, 'outer_face': outer, 'film': film,
                 'oxide': oxide, 'interior': film & ~surface & ~interface}
        info.update({'z_lowest_substrate_cation_A': z_sc0, 'z_if_A': z_if,
                     'outer_face_film_cations': int((fc & outer).sum()),
                     'outer_face_film_cations_per_nm2': float((fc & outer).sum() / (abs(np.linalg.det(st.cell[:2, :2])) / 100.0))})
    zi = z[masks['interior']]
    info['z_A'] = z.tolist()
    info['interior_z_range_A'] = [float(zi.min()), float(zi.max())] if zi.size else None
    return _finish(masks, info, nat)


def _finish(masks, info, nat):
    info['counts'] = {k: int(v.sum()) for k, v in masks.items()}
    info['n_atoms'] = nat
    info['interior_fraction'] = masks['interior'].sum() / nat
    info['overlap_surface_interface'] = int((masks['surface'] & masks['interface']).sum())
    return masks, info


def z_in_frame(z_bohr_avg, info, bohr_a):
    """Map average.x z values (bohr, 0..c) into the unwrapped (and possibly mirrored) frame of regions()."""
    z = np.asarray(z_bohr_avg) * bohr_a
    origin, c = info['z_origin_A'], info['c_A']
    z = np.mod(z - origin, c) + origin
    return -z if info.get('orientation_flipped') else z


def first_shell_O(st, i, cutoff=W_O_FIRST_SHELL_A):
    """Indices of O atoms within cutoff (A, minimum image) of atom i."""
    o = np.array([j for j, s in enumerate(st.species) if s == 'O'])
    if o.size == 0:
        return []
    d = st.distances_from(i, o)
    return [int(j) for j in o[d <= cutoff + EPS]]


def match_atoms(child, parent, tol_A=1.2, swap=(('W', 'In'),)):
    """Map child atom index -> parent atom index by nearest position (minimum image), same element (or an allowed
    substitution child->parent such as W->In). Unmatched child atoms (an added O) map to None. A parent atom is used at
    most once; ties are resolved by distance order (greedy). Returns (mapping, report)."""
    allowed = {(a, a) for a in set(child.species) | set(parent.species)} | set(swap)
    pairs = []
    for i in range(child.nat):
        cand = [j for j in range(parent.nat) if (child.species[i], parent.species[j]) in allowed]
        if not cand:
            continue
        # distance of child atom i to parent atoms, minimum image in the parent cell
        d = np.full(len(cand), np.inf)
        delta = parent.pos[cand] - child.pos[i]
        for a, b, c in itertools.product((-1, 0, 1), repeat=3):
            sh = a * parent.cell[0] + b * parent.cell[1] + c * parent.cell[2]
            d = np.minimum(d, np.linalg.norm(delta + sh, axis=1))
        for j, dist in zip(cand, d):
            if dist <= tol_A:
                pairs.append((dist, i, j))
    pairs.sort()
    mapping, used = {}, set()
    for dist, i, j in pairs:
        if i in mapping or j in used:
            continue
        mapping[i] = j
        used.add(j)
    unmatched_child = [i for i in range(child.nat) if i not in mapping]
    unmatched_parent = [j for j in range(parent.nat) if j not in used]
    rep = {'unmatched_child': unmatched_child, 'unmatched_parent': unmatched_parent,
           'max_distance_A': max((d for d, i, j in pairs if mapping.get(i) == j), default=0.0)}
    return {i: mapping.get(i) for i in range(child.nat)}, rep
