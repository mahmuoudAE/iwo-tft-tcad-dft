#!/usr/bin/env python3
"""Amorphous In2O3 / W:In2O3 structures with a MACE foundation potential (melt-quench), for later DFT relaxation.

mode 'slab': periodic box of height t (the film thickness) at the target density -> melt -> quench -> open a vacuum
gap along z (cleave) -> short anneal of the free slab -> passivate under-coordinated surface sites by dissociated
water (OH on a cation + H on an oxygen, pairwise, so the electron count is unchanged) -> relax.
mode 'bulk': periodic cube at the target density -> melt -> quench -> relax (no cleave, no passivation).
mode 'interface': a-Al2O3 layer melt-quenched first, then the film is melted and quenched on top of it with the
oxide held fixed, the stack is cleaved below the oxide (one buried oxide/film interface, film top = back channel),
annealed with all atoms free, passivated on both outer surfaces and relaxed. Rules: SLAB_PROTOCOL.md.
The substrate is a-HfO2 instead when the spec's substrate has n_Hf (A18 HfO2 control, SLAB_PROTOCOL.md 9); that
cell alone also gets reported-only diagnostics in its QC file (hf_diag(), oxide MSD over the 3000 K hold, the state
right after the anneal), which change no PASS/FAIL rule and no output of any other cell.

Outputs (prefix = spec name): <name>.xyz (extended XYZ, final), <name>_qe.txt (CELL_PARAMETERS + ATOMIC_POSITIONS),
<name>_qc.json (quality-control metrics and PASS/FAIL), <name>_md.csv (time, T, E_pot per 100 steps),
<name>_snapshots.xyz (frames for the DFT force check: melt, quenched, final).

Usage: python mace_amorph.py --spec spec.json --model <model file or name> [--device cuda] [--quick]
spec keys: name, mode, thickness_nm (slab), n_In, n_W, n_O, density_gcc, seed, vacuum_A (slab)
"""
import argparse
import csv
import json
import math
import sys
import time

import numpy as np
from ase import Atoms, units
from ase.constraints import FixAtoms
from ase.data import atomic_masses, atomic_numbers
from ase.io import write
from ase.md.langevin import Langevin
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.neighborlist import neighbor_list
from ase.optimize import FIRE

CAT = ('In', 'W', 'Al', 'Hf')
FILM = ('In', 'W')
SUBCAT = ('Al', 'Hf')   # substrate (gate-oxide) cations: a-Al2O3, or a-HfO2 for the A18 control
# coordination cutoffs (A): first minimum of g(r) for amorphous In2O3 is ~2.7-2.8 A; W-O and Al-O bonds are shorter
CUT = {('In', 'O'): 2.75, ('O', 'In'): 2.75, ('W', 'O'): 2.45, ('O', 'W'): 2.45, ('Al', 'O'): 2.30, ('O', 'Al'): 2.30,
       ('O', 'H'): 1.20, ('H', 'O'): 1.20}
# Hf-O (A18): first shell 2.0-2.3 A in a-HfO2 (m-HfO2 bonds 2.03-2.25 A), next Hf-O shell >= ~3.4 A -> 2.65 A sits in
# the empty gap, 0.4 A beyond the longest first-shell bond
CUT.update({('Hf', 'O'): 2.65, ('O', 'Hf'): 2.65})
# minimum distances for the random start (A); W-W kept apart so the dopants start dilute (SLAB_PROTOCOL.md)
# Hf uses the generic values (A18): 2.9 A < Hf-Hf 3.3-3.5 A and 1.9 A < Hf-O 2.0-2.2 A in a-HfO2; 46 Hf at 2.9 A
# already fill a hard-sphere fraction 0.35 of the 9.6 g/cm3 box (random-sequential-addition limit ~0.38)
MIN_START = {'cc': 2.9, 'oo': 2.4, 'co': 1.9, 'ww': 6.0}
# closest acceptable contacts in the final structure (A)
QC_MIN = {('In', 'O'): 1.90, ('W', 'O'): 1.65, ('O', 'O'): 2.15, ('In', 'In'): 2.70, ('In', 'W'): 2.70,
          ('W', 'W'): 2.60, ('H', 'H'): 1.40, ('In', 'H'): 1.70, ('W', 'H'): 1.70, ('Al', 'O'): 1.60,
          ('Al', 'Al'): 2.50, ('Al', 'In'): 2.60, ('Al', 'W'): 2.60, ('Al', 'H'): 1.50}
# Hf contacts (A18), same relative margins as the existing limits (cation-O ~0.87 x mean bond; cation-cation ~0.8 x
# the first cation-cation peak and ~0.85 x the metal bond): Hf-O 1.85 (a-HfO2 mean 2.10 A, shortest m-HfO2 bond 2.03 A);
# Hf-Hf 2.80 (a-HfO2 first Hf-Hf peak 3.3-3.5 A, hcp Hf metal 3.13 A); Hf-In 2.75 and Hf-W 2.70 (means of the
# like-cation limits, as Al-In / Al-W); Hf-H 1.80 (Hf-H hydride bonds 1.85-2.1 A)
QC_MIN.update({('Hf', 'O'): 1.85, ('Hf', 'Hf'): 2.80, ('Hf', 'In'): 2.75, ('Hf', 'W'): 2.70, ('Hf', 'H'): 1.80})
L_MIN, VAC_MIN, RHO_REF = 12.5, 15.0, 7.0   # A, A, g/cm3 (registered in SLAB_PROTOCOL.md)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def random_pack(symbols, cell, rng, zrange=(0.0, 1.0), fixed_sym=(), fixed_pos=None, max_tries=200000):
    """Rejection sampling with minimum-image distances in a fully periodic box; cations first, then O.
    New atoms go into the fractional z window zrange; atoms in fixed_sym/fixed_pos are already there."""
    cell = np.asarray(cell, float)
    inv = np.linalg.inv(cell)
    nf = len(fixed_sym)
    allsym = list(fixed_sym) + list(symbols)
    order = sorted(range(len(symbols)), key=lambda k: symbols[k] == 'O')
    pos = np.zeros((nf + len(symbols), 3))
    if nf:
        pos[:nf] = fixed_pos
    placed = list(range(nf))

    def need(a, b):
        if a == 'W' and b == 'W':
            return MIN_START['ww']
        if a == 'O' and b == 'O':
            return MIN_START['oo']
        return MIN_START['co'] if 'O' in (a, b) else MIN_START['cc']

    scale = 1.0
    for k in order:
        for attempt in range(max_tries):
            if attempt and attempt % 20000 == 0:
                scale *= 0.95   # relax the minimum distances slowly if the box is crowded
            f3 = rng.random(3)
            f3[2] = zrange[0] + (zrange[1] - zrange[0]) * f3[2]
            p = f3 @ cell
            if placed:
                d = p - pos[placed]
                frac = d @ inv
                frac -= np.round(frac)
                r = np.linalg.norm(frac @ cell, axis=1)
                if (r < np.array([need(symbols[k], allsym[j]) for j in placed]) * scale).any():
                    continue
            pos[nf + k] = p
            placed.append(nf + k)
            break
        else:
            raise RuntimeError(f'could not place atom {k} ({symbols[k]})')
    return pos[nf:]


def coordination(atoms):
    i, j = neighbor_list('ij', atoms, CUT)
    sym = atoms.get_chemical_symbols()
    cn_o = np.zeros(len(atoms), int)     # O neighbours of a cation
    cn_cat = np.zeros(len(atoms), int)   # cation neighbours of an O
    for a, b in zip(i, j):
        if sym[a] in CAT and sym[b] == 'O':
            cn_o[a] += 1
        if sym[a] == 'O' and sym[b] in CAT:
            cn_cat[a] += 1
    return cn_o, cn_cat


def md_block(atoms, calc, t_start, t_end, ps, writer, t0, dt_fs=1.0, friction=0.01):
    """Langevin MD with the target temperature ramped linearly from t_start to t_end."""
    atoms.calc = calc
    n = int(round(ps * 1000 / dt_fs))
    dyn = Langevin(atoms, timestep=dt_fs * units.fs, temperature_K=t_start, friction=friction / units.fs)
    chunk = 100
    for s in range(0, n, chunk):
        dyn.set_temperature(temperature_K=t_start + (t_end - t_start) * s / max(n, 1))
        dyn.run(min(chunk, n - s))
        writer.writerow([round(t0 + (s + chunk) * dt_fs / 1000, 3), round(atoms.get_temperature(), 1),
                         round(atoms.get_potential_energy(), 4)])
    return t0 + n * dt_fs / 1000


def relax(atoms, calc, fmax, steps):
    atoms.calc = calc
    opt = FIRE(atoms, logfile=None)
    opt.run(fmax=fmax, steps=steps)
    return opt.nsteps, float(np.abs(atoms.get_forces()).max())


def place_free(atoms, origin, direction, bond, avoid=1.6):
    """Point at 'bond' from origin along direction; rotate towards +-z until no atom is closer than 'avoid'."""
    d = direction / (np.linalg.norm(direction) + 1e-12)
    zsign = 1.0 if d[2] >= 0 else -1.0
    for w in np.linspace(0.0, 1.0, 11):
        dd = (1 - w) * d + w * np.array([0, 0, zsign])
        dd /= np.linalg.norm(dd)
        p = origin + bond * dd
        test = atoms.copy()
        test.append('H')
        test.positions[-1] = p
        if test.get_distances(len(test) - 1, range(len(test) - 1), mic=True).min() > avoid:
            return p, dd
    zz = np.array([0, 0, zsign])
    return origin + bond * zz, zz


def passivate(atoms, surf_depth=3.5):
    """Dissociated-water passivation: OH on under-coordinated surface cations, H on under-coordinated surface O.
    Equal numbers of OH and H keep the electron count unchanged."""
    cn_o, cn_cat = coordination(atoms)
    sym = atoms.get_chemical_symbols()
    n0 = len(sym)   # neighbour directions are taken from the unpassivated slab only
    z = atoms.positions[:, 2]
    zmin, zmax = z.min(), z.max()
    zmid = 0.5 * (zmin + zmax)
    surf = (z < zmin + surf_depth) | (z > zmax - surf_depth)
    # under-coordinated = at least 2 below the amorphous bulk value (In ~5.3, W ~6, Al ~4.5; O on In/W ~3.5, on Al ~3)
    # Hf (A18): a-HfO2 mean CN ~6-7 -> CN <= 5; O with a substrate-cation (Al or Hf) majority: <= 1 (a-HfO2 O ~3.3)
    cats = [k for k in range(n0) if surf[k] and sym[k] in CAT and cn_o[k] <= {'In': 4, 'W': 5, 'Al': 3, 'Hf': 5}[sym[k]]]
    i, j = neighbor_list('ij', atoms, CUT)
    n_sub = np.bincount(i[np.isin(np.array(sym)[j], SUBCAT)], minlength=n0)
    oxys = [k for k in range(n0) if surf[k] and sym[k] == 'O' and cn_cat[k] <= (1 if 2 * n_sub[k] > cn_cat[k] else 2)]
    cats.sort(key=lambda k: cn_o[k])
    oxys.sort(key=lambda k: cn_cat[k])
    npair = min(len(cats), len(oxys))
    added = []

    def away_from(k, partner):
        d = np.zeros(3)
        for j in range(n0):
            if partner(sym[j]):
                r = atoms.get_distance(k, j, mic=True, vector=True)
                if 1e-6 < np.linalg.norm(r) < CUT[('In', 'O')]:
                    d -= r / np.linalg.norm(r)
        return d + 0.7 * np.array([0, 0, 1.0 if atoms.positions[k, 2] > zmid else -1.0])

    for k in cats[:npair]:
        p_o, dd = place_free(atoms, atoms.positions[k], away_from(k, lambda s: s == 'O'),
                             {'In': 2.05, 'W': 1.90, 'Al': 1.80, 'Hf': 1.95}[sym[k]])   # Hf-OH ~1.95 A (A18)
        atoms.append('O')
        atoms.positions[-1] = p_o
        p_h, _ = place_free(atoms, p_o, dd, 0.97, avoid=1.3)
        atoms.append('H')
        atoms.positions[-1] = p_h
        added.append(('OH', int(k)))
    for k in oxys[:npair]:
        p_h, _ = place_free(atoms, atoms.positions[k], away_from(k, lambda s: s in CAT), 0.98, avoid=1.3)
        atoms.append('H')
        atoms.positions[-1] = p_h
        added.append(('H', int(k)))
    return added, len(cats) - npair, len(oxys) - npair


def remove_water(atoms, deleted=None):
    """Delete H2O molecules recombined from the dissociated-water passivation (O bound to no cation and to exactly
    two H). One OH + one H go together, so the electron count stays unchanged (SLAB_PROTOCOL.md 7).
    deleted: optional list that receives the deleted indices (A18 fix; the default changes nothing)."""
    sym = np.array(atoms.get_chemical_symbols())
    _, cn_cat = coordination(atoms)
    ih, jh = neighbor_list('ij', atoms, {('O', 'H'): 1.2})
    drop = []
    for k in np.where((sym == 'O') & (cn_cat == 0))[0]:
        hs = [int(b) for a, b in zip(ih, jh) if a == k and sym[b] == 'H']
        if len(hs) == 2:
            drop += [int(k)] + hs
    if drop:
        del atoms[sorted(set(drop))]
    if deleted is not None:   # A18 fix: the caller keeps its per-atom origin labels aligned (HfO2 cell only)
        deleted.extend(sorted(set(drop)))
    return len(drop) // 3


# A18 verification fixes (called by qc() for the HfO2 cell only; reported only: no PASS/FAIL rule, no output of
# any Al2O3, slab or bulk cell changes). Partition of the interface region (A): film atoms within OUTER_FACE_A of the
# lowest substrate cation sit on the OUTER oxide face (left there by the periodic film melt, whose top touches the
# oxide bottom), not at the buried interface; buried exchange = film / substrate cations more than BURIED_A past z_if
# (the percentile midpoint puts a few cations of each set on the wrong side of z_if by construction).
OUTER_FACE_A, BURIED_A = 3.0, 1.0


def iface_partition(atoms, scat, origin=None):
    """Reported-only partition of an interface cell (SLAB_PROTOCOL.md 9): film cations (and film-origin O, when the
    origin labels are known) on the OUTER oxide face, buried exchange across z_if, and every O-O contact below the
    QC limit with its region. scat: substrate cation ('Hf' in qc(); 'Al' only in the post-hoc iface_audit.py).
    origin: optional per-atom labels 1 = substrate, 2 = film, 0 = added by passivation."""
    sym = np.array(atoms.get_chemical_symbols())
    z = atoms.positions[:, 2]
    film, sc = np.isin(sym, FILM), sym == scat
    org = None if origin is None else np.asarray(origin)
    area = float(np.linalg.norm(np.cross(atoms.cell[0], atoms.cell[1])))
    z_if = float(0.5 * (np.percentile(z[sc], 95) + np.percentile(z[film], 5)))
    z_sc0, z_top = float(z[sc].min()), float(z[film].max())
    outer = z < z_sc0 + OUTER_FACE_A
    out = {'z_lowest_sub_cation_A': z_sc0, 'z_if_A': z_if}
    out['outer_face_film_cations'] = [[int(k), str(sym[k]), round(float(z[k] - z_sc0), 2)]
                                      for k in np.where(film & outer)[0]]
    out['outer_face_film_cations_per_nm2'] = round(len(out['outer_face_film_cations']) / (area / 100), 2)
    if org is not None:
        out['outer_face_film_O'] = [[int(k), round(float(z[k] - z_sc0), 2)]
                                    for k in np.where((org == 2) & (sym == 'O') & outer)[0]]
    out['buried_film_cations_in_oxide'] = [[int(k), str(sym[k]), round(float(z[k] - z_if), 2)]
                                           for k in np.where(film & ~outer & (z < z_if - BURIED_A))[0]]
    out[f'buried_{scat}_in_film'] = [[int(k), round(float(z[k] - z_if), 2)] for k in np.where(sc & (z > z_if + BURIED_A))[0]]
    out['n_film_cations_within_1A_below_if'] = int((film & ~outer & (z < z_if) & (z >= z_if - BURIED_A)).sum())
    out[f'n_{scat}_within_1A_above_if'] = int((sc & (z > z_if) & (z <= z_if + BURIED_A)).sum())
    # every O-O contact below the QC limit: where it is, which side each O came from, H attached
    ih, jh = neighbor_list('ij', atoms, {('O', 'H'): 1.2})
    nh = np.bincount(ih[(sym[ih] == 'O') & (sym[jh] == 'H')], minlength=len(atoms))
    i, j, d = neighbor_list('ijd', atoms, QC_MIN[('O', 'O')])
    sites = []
    for a, b, r in zip(i, j, d):
        if a < b and sym[a] == 'O' and sym[b] == 'O':
            zm = 0.5 * (z[a] + z[b])
            region = ('outer_oxide_face' if zm < z_sc0 + OUTER_FACE_A else 'film_top' if zm > z_top - OUTER_FACE_A
                      else 'interface' if abs(zm - z_if) <= OUTER_FACE_A else 'oxide_interior' if zm < z_if
                      else 'film_interior')
            s = {'O': [int(a), int(b)], 'd_A': round(float(r), 3), 'z_A': [round(float(z[a]), 2), round(float(z[b]), 2)],
                 'region': region, 'n_H': [int(nh[a]), int(nh[b])]}
            if org is not None:
                s['origin'] = [{0: 'passivation', 1: 'substrate', 2: 'film'}[int(org[k])] for k in (a, b)]
            sites.append(s)
    out['OO_contacts_below_limit'] = sites
    return out


def hf_diag(atoms, origin=None):
    """Reported-only diagnostics of an interface cell on a-HfO2 (SLAB_PROTOCOL.md 9): iface_partition() plus the
    Hf-O bond-length distribution (A21), the Hf-Hf pair histogram, the Hf-O-Hf angle histogram and the oxide
    interior density (amorphous / crystalline check of the a-HfO2 layer)."""
    out = iface_partition(atoms, 'Hf', origin)
    sym = np.array(atoms.get_chemical_symbols())
    z = atoms.positions[:, 2]
    area = float(np.linalg.norm(np.cross(atoms.cell[0], atoms.cell[1])))
    # Hf-O bond-length distribution (first shell, the 2.65 A coordination cutoff)
    ib, jb, db = neighbor_list('ijd', atoms, {('Hf', 'O'): CUT[('Hf', 'O')]})
    dh = db[(sym[ib] == 'Hf') & (sym[jb] == 'O')]
    if len(dh):
        edges = np.round(np.arange(1.80, 2.65 + 1e-9, 0.05), 2)
        out['Hf_O_bond_hist_0p05A'] = {f'{lo:.2f}': int(c) for lo, c in zip(edges[:-1], np.histogram(dh, bins=edges)[0])}
        out['Hf_O_bond_stats_A'] = {'n': int(len(dh)), 'n_below_1p80': int((dh < 1.80).sum()),
                                    **{k: round(float(f(dh)), 3) for k, f in (
                                        ('min', np.min), ('p5', lambda x: np.percentile(x, 5)),
                                        ('p50', np.median), ('p95', lambda x: np.percentile(x, 95)), ('max', np.max),
                                        ('mean', np.mean), ('std', np.std))}}
    # Hf-Hf pair histogram (a-HfO2: broad 3.3-3.5 and 3.7-3.9 A shells; m-HfO2 gives sharp shells)
    ip, jp, dp = neighbor_list('ijd', atoms, 5.0)
    dhh = dp[(sym[ip] == 'Hf') & (sym[jp] == 'Hf') & (ip < jp)]
    if len(dhh):
        edges = np.round(np.arange(2.8, 5.0 + 1e-9, 0.1), 1)
        hh = np.histogram(dhh, bins=edges)[0]
        out['Hf_Hf_hist_0p1A'] = {f'{lo:.1f}': int(c) for lo, c in zip(edges[:-1], hh)}
        first = hh[edges[:-1] < 4.0]
        out['Hf_Hf_first_peak_A'] = round(float(edges[int(np.argmax(first))] + 0.05), 2)
        out['Hf_Hf_min_A'] = round(float(dhh.min()), 3)
    # Hf-O-Hf angles at O (both Hf within the 2.65 A cutoff), 10 deg bins
    io, jo, vo = neighbor_list('ijD', atoms, {('Hf', 'O'): CUT[('Hf', 'O')]})
    ang = []
    for k in np.where(sym == 'O')[0]:
        v = vo[(io == k) & (sym[jo] == 'Hf')]
        for p in range(len(v)):
            for q in range(p + 1, len(v)):
                c = np.dot(v[p], v[q]) / (np.linalg.norm(v[p]) * np.linalg.norm(v[q]))
                ang.append(math.degrees(math.acos(max(-1.0, min(1.0, c)))))
    if ang:
        edges = np.arange(60, 181, 10)
        out['Hf_O_Hf_angle_hist_10deg'] = {int(lo): int(c) for lo, c in zip(edges[:-1], np.histogram(ang, bins=edges)[0])}
        out['Hf_O_Hf_angle_mean_deg'] = round(float(np.mean(ang)), 1)
    # oxide interior density: all atoms between 2 A above the lowest Hf and 2 A below z_if
    lo, hi = out['z_lowest_sub_cation_A'] + 2.0, out['z_if_A'] - 2.0
    if hi - lo > 2.0:
        win = (z >= lo) & (z <= hi)
        out['oxide_interior_density_gcc'] = round(float(atoms.get_masses()[win].sum() * 1.66054 / (area * (hi - lo))), 3)
        out['oxide_interior_window_A'] = [round(lo, 2), round(hi, 2)]
    return out


def qc(atoms, mode, origin=None):
    sym = np.array(atoms.get_chemical_symbols())
    out = {'n_atoms': len(atoms), 'composition': {s: int((sym == s).sum()) for s in sorted(set(sym))}}
    n_in, n_w = int((sym == 'In').sum()), int((sym == 'W').sum())
    out['W_fraction_of_metals'] = n_w / max(n_in + n_w, 1)
    cn_o, cn_cat = coordination(atoms)
    inn = sym == 'In'
    out['In_CN_mean'] = float(cn_o[inn].mean())
    out['In_CN_hist'] = {int(c): int((cn_o[inn] == c).sum()) for c in sorted(set(cn_o[inn]))}
    if n_w:
        out['W_CN'] = [int(c) for c in cn_o[sym == 'W']]
    out['O_CN_mean'] = float(cn_cat[sym == 'O'].mean())
    i, j, d = neighbor_list('ijd', atoms, {('In', 'O'): 2.75})
    sel = (sym[i] == 'In') & (sym[j] == 'O')
    out['In_O_bond_mean_A'] = float(d[sel].mean()) if sel.any() else None
    ii, jj, dd = neighbor_list('ijd', atoms, 3.5)
    worst = {}
    for (a, b) in QC_MIN:
        m = (sym[ii] == a) & (sym[jj] == b)
        if m.any():
            worst[f'{a}-{b}'] = round(float(dd[m].min()), 3)
    out['min_distances_A'] = worst
    # chemistry that should not exist: O2/peroxide, water molecules, free O, isolated atoms
    i2, j2 = neighbor_list('ij', atoms, 1.6)
    out['n_short_OO'] = int(((sym[i2] == 'O') & (sym[j2] == 'O')).sum() // 2)
    hcount = np.zeros(len(atoms), int)
    ih, jh = neighbor_list('ij', atoms, {('O', 'H'): 1.2})
    for a, b in zip(ih, jh):
        if sym[a] == 'O' and sym[b] == 'H':
            hcount[a] += 1
    out['n_water'] = int(((sym == 'O') & (cn_cat == 0) & (hcount >= 2)).sum())
    out['n_free_O'] = int(((sym == 'O') & (cn_cat == 0) & (hcount == 0)).sum())
    ia, _ = neighbor_list('ij', atoms, 3.2)
    out['n_isolated'] = int((np.bincount(ia, minlength=len(atoms)) == 0).sum())
    z = atoms.positions[:, 2]
    lat = float(min(np.linalg.norm(atoms.cell[0]), np.linalg.norm(atoms.cell[1])))
    out['lateral_min_A'] = lat
    if mode != 'bulk':
        area = float(np.linalg.norm(np.cross(atoms.cell[0], atoms.cell[1])))
        film = np.isin(sym, FILM)
        # film/oxide boundary (interface mode): midway between the top substrate-cation (Al, or Hf for A18) and the
        # bottom film cation layers
        scat = 'Al' if (sym == 'Al').any() else ('Hf' if (sym == 'Hf').any() else None)
        z_if = 0.5 * (np.percentile(z[sym == scat], 95) + np.percentile(z[film], 5)) if scat else None
        in_film = (sym != 'H') & ((z > z_if) if z_if is not None else True)
        zf = z[in_film]
        # thickness definitions (SLAB_PROTOCOL.md): t_eq = mass-equivalent at RHO_REF (primary label),
        # t_span = outermost non-H film atoms, t_cat = outermost film cations; t_rho comes later from the DFT density
        mass = sum(atomic_masses[atomic_numbers[s]] for s in sym[in_film])
        out['t_eq_A'] = float(mass * 1.66054 / (RHO_REF * area))
        out['t_span_A'] = float(zf.max() - zf.min())
        out['t_cat_A'] = float(z[film].max() - z[film].min())
        out['mean_density_gcc_over_t_span'] = float(mass * 1.66054 / (area * out['t_span_A']))
        out['vacuum_A'] = float(atoms.cell[2, 2] - (z.max() - z.min()))
        top, bot = zf.max(), zf.min()
        h_top, h_bot = int(((sym == 'H') & (z > z.mean())).sum()), int(((sym == 'H') & (z <= z.mean())).sum())
        out['H_per_nm2_top_bottom'] = [round(h_top / (area / 100), 2), round(h_bot / (area / 100), 2)]
        if n_w:   # depth of every W below the nearer film boundary (surface or oxide interface)
            out['W_depth_A'] = [round(float(min(zw - bot, top - zw)), 2) for zw in z[sym == 'W']]
        if z_if is not None:
            out['interface_z_A'] = float(z_if)
            out['n_film_cations_in_oxide'] = int((film & (z < z_if)).sum())
            out[f'n_{scat}_in_film'] = int(((sym == scat) & (z > z_if)).sum())
            out[f'{scat}_CN_mean'] = float(cn_o[sym == scat].mean())
            if scat == 'Hf':   # A18, reported only: a-HfO2 coordination and bond length (amorphous check)
                out['Hf_CN_hist'] = {int(c): int((cn_o[sym == 'Hf'] == c).sum()) for c in sorted(set(cn_o[sym == 'Hf']))}
                ih2, jh2, dh2 = neighbor_list('ijd', atoms, {('Hf', 'O'): CUT[('Hf', 'O')]})
                selh = (sym[ih2] == 'Hf') & (sym[jh2] == 'O')
                out['Hf_O_bond_mean_A'] = float(dh2[selh].mean()) if selh.any() else None
                # A18 verification fixes (reported only): bond-length distribution (A21), outer-face vs buried
                # interface partition, O-O contact sites, Hf-Hf / Hf-O-Hf histograms, oxide interior density
                out.update(hf_diag(atoms, origin))
    else:
        out['density_gcc'] = float(atoms.get_masses().sum() * 1.66054 / atoms.get_volume())
    if n_w:   # closest W-W distance including periodic images (1 W per cell -> the lattice vector)
        iw = np.where(sym == 'W')[0]
        dww = [atoms.get_distance(a, b, mic=True) for a in iw for b in iw if a < b]
        out['W_W_min_A'] = float(min([lat] + dww))
    fails = []
    if mode != 'bulk' and lat < L_MIN:
        fails.append(f'in-plane cell {lat:.2f} A below {L_MIN} A')
    if out['In_O_bond_mean_A'] is None or not (2.08 <= out['In_O_bond_mean_A'] <= 2.26):
        fails.append('mean In-O bond outside 2.08-2.26 A')
    if not (4.6 <= out['In_CN_mean'] <= 6.3):
        fails.append('mean In coordination outside 4.6-6.3')
    for k, v in worst.items():
        a, b = k.split('-')
        if v < QC_MIN[(a, b)]:
            fails.append(f'{k} contact {v} A below {QC_MIN[(a, b)]} A')
    for k in ('n_short_OO', 'n_water', 'n_free_O', 'n_isolated'):
        if out[k] > 0:
            fails.append(f'{k} = {out[k]}')
    if mode != 'bulk' and out['vacuum_A'] < VAC_MIN:
        fails.append(f'vacuum gap below {VAC_MIN} A')
    out['QC'] = 'PASS' if not fails else 'FAIL'
    out['QC_reasons'] = fails
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--spec', required=True)
    ap.add_argument('--model', required=True)
    ap.add_argument('--device', default='cuda')
    ap.add_argument('--quick', action='store_true', help='very short MD for a smoke test')
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    name, mode = spec['name'], spec['mode']
    rng = np.random.default_rng(spec['seed'])
    from mace.calculators import mace_mp
    calc32 = mace_mp(model=a.model, device=a.device, default_dtype='float32')
    calc64 = mace_mp(model=a.model, device=a.device, default_dtype='float64')

    symbols = ['In'] * spec['n_In'] + ['W'] * spec['n_W'] + ['O'] * spec['n_O']
    mass_amu = sum(atomic_masses[atomic_numbers[s]] for s in symbols)
    vol_A3 = mass_amu * 1.66054 / spec['density_gcc']
    f = open(f'{name}_md.csv', 'w', newline='')
    wr = csv.writer(f)
    wr.writerow(['time_ps', 'T_K', 'Epot_eV'])
    sc = 0.05 if a.quick else 1.0
    rsteps = (lambda n: 40) if a.quick else (lambda n: n)   # smoke test: cap the relaxation steps too
    tps, nsub = 0.0, 0
    origin, extra = None, {}   # A18 fixes, HfO2 cell only: per-atom origin labels and reported-only diagnostics
    if mode in ('slab', 'interface'):
        t = spec['thickness_nm'] * 10.0
        L = spec.get('lateral_A') or math.sqrt(vol_A3 / t)   # paired IWO/IO cells share lateral_A
        cell = np.diag([L, L, t])
    else:
        L = vol_A3 ** (1 / 3)
        cell = np.diag([L, L, L])
    if mode == 'interface':
        # gate-side oxide: a-Al2O3 melt-quenched alone in a periodic box, then held fixed while the film is made on it
        # (a-HfO2 when the substrate spec has n_Hf: A18 HfO2 control, same recipe)
        sub = spec['substrate']
        scat = 'Hf' if 'n_Hf' in sub else 'Al'
        ssym = [scat] * sub[f'n_{scat}'] + ['O'] * sub['n_O']
        tsub = sub['thickness_A']
        sat = Atoms(ssym, positions=random_pack(ssym, np.diag([L, L, tsub]), rng), cell=np.diag([L, L, tsub]), pbc=True)
        relax(sat, calc32, fmax=0.5, steps=300)
        MaxwellBoltzmannDistribution(sat, temperature_K=3000, rng=rng)
        p_hold = sat.positions.copy() if scat == 'Hf' else None
        tps = md_block(sat, calc32, 3000, 3000, 4.0 * sc, wr, tps)
        if scat == 'Hf':   # A18 fix, reported only: does the oxide diffuse during the 3000 K hold? (unwrapped MD)
            dr2, ss = ((sat.positions - p_hold) ** 2).sum(axis=1), np.array(ssym)
            extra['oxide_3000K_hold_MSD_A2'] = {'hold_ps': 4.0 * sc, 'Hf': round(float(dr2[ss == 'Hf'].mean()), 3),
                                                'O': round(float(dr2[ss == 'O'].mean()), 3)}
        tps = md_block(sat, calc32, 3000, 300, 6.0 * sc, wr, tps)
        relax(sat, calc64, fmax=0.05, steps=rsteps(1000))
        sat.wrap()
        log(f"a-{ {'Al': 'Al2O3', 'Hf': 'HfO2'}[scat] } layer done ({tps:.2f} ps)")
        cell = np.diag([L, L, tsub + t])
        new = random_pack(symbols, cell, rng, zrange=(tsub / (tsub + t), 1.0), fixed_sym=ssym, fixed_pos=sat.positions)
        nsub = len(ssym)
        atoms = Atoms(ssym + symbols, positions=np.vstack([sat.positions, new]), cell=cell, pbc=True)
        atoms.set_constraint(FixAtoms(indices=range(nsub)))
        if scat == 'Hf':
            origin = np.array([1] * nsub + [2] * len(symbols))   # 1 substrate, 2 film, 0 passivation (added later)
    else:
        atoms = Atoms(symbols, positions=random_pack(symbols, cell, rng), cell=cell, pbc=True)
    log(f'{name}: {len(atoms)} atoms, box {np.diag(cell).round(3).tolist()} A')
    nstep, fm = relax(atoms, calc32, fmax=0.5, steps=300)
    log(f'pre-relax: {nstep} steps, max force {fm:.2f} eV/A')

    snaps = []
    MaxwellBoltzmannDistribution(atoms, temperature_K=3000, rng=rng)
    tps = md_block(atoms, calc32, 3000, 3000, 6.0 * sc, wr, tps)
    snaps.append(('melt_3000K', atoms.copy()))
    log(f'melt done ({tps:.2f} ps)')
    tps = md_block(atoms, calc32, 3000, 300, 9.0 * sc, wr, tps)
    tps = md_block(atoms, calc32, 300, 300, 2.0 * sc, wr, tps)
    snaps.append(('quenched_300K', atoms.copy()))
    log(f'quench done ({tps:.2f} ps)')
    info = {'md_ps': tps}
    if mode in ('slab', 'interface'):
        vac = spec.get('vacuum_A', 10.0)
        # cleave plane: z = 0 for a film; 1 A below the fixed oxide for an interface (oxide bottom = outer surface)
        zc = atoms.positions[:nsub, 2].min() - 1.0 if nsub else 0.0
        frac = atoms.get_scaled_positions(wrap=True)
        zz = (atoms.positions[:, 2] - zc) % cell[2, 2]
        atoms.set_constraint()
        atoms.set_cell(np.diag([cell[0, 0], cell[1, 1], cell[2, 2] + 2 * vac]), scale_atoms=False)
        atoms.positions[:, 0] = frac[:, 0] * cell[0, 0]
        atoms.positions[:, 1] = frac[:, 1] * cell[1, 1]
        atoms.positions[:, 2] = zz + vac
        atoms.set_momenta(np.zeros((len(atoms), 3)))
        MaxwellBoltzmannDistribution(atoms, temperature_K=800, rng=rng)
        tps = md_block(atoms, calc32, 800, 800, 3.0 * sc, wr, tps)
        tps = md_block(atoms, calc32, 800, 300, 3.0 * sc, wr, tps)
        snaps.append(('slab_annealed', atoms.copy()))
        if origin is not None:   # A18 fix, reported only: state right after the anneal, before relax and passivation
            cn_a, _ = coordination(atoms)
            sa = np.array(atoms.get_chemical_symbols()) == 'Hf'
            extra['slab_annealed_diag'] = {'Hf_CN_hist': {int(c): int((cn_a[sa] == c).sum()) for c in sorted(set(cn_a[sa]))},
                                           **hf_diag(atoms, origin)}
        log(f'slab anneal done ({tps:.2f} ps)')
        nstep, fm = relax(atoms, calc64, fmax=0.05, steps=rsteps(1500))
        log(f'slab relax before passivation: {nstep} steps, max force {fm:.3f}')
        if spec.get('passivate', True):
            added, left_cat, left_o = passivate(atoms)
            if origin is not None:
                origin = np.concatenate([origin, np.zeros(len(atoms) - len(origin), int)])
            info.update({'md_ps': tps, 'passivation': added, 'unpaired_undercoordinated_cations': left_cat,
                         'unpaired_undercoordinated_O': left_o})
            log(f'passivation: {len(added)} groups added; unpaired: {left_cat} cations, {left_o} O')
        else:
            info.update({'md_ps': tps, 'passivation': 'none (bare surfaces, termination control)'})
            log('passivation skipped (bare surfaces)')
    atoms.set_momenta(np.zeros((len(atoms), 3)))
    nstep, fm = relax(atoms, calc64, fmax=0.05, steps=rsteps(3000))
    log(f'final relax: {nstep} steps, max force {fm:.3f} eV/A')
    if mode != 'bulk' and spec.get('passivate', True):
        dl = [] if origin is not None else None
        nwat = remove_water(atoms, dl)
        if dl:
            origin = np.delete(origin, dl)
        info['water_removed'] = nwat
        if nwat:
            nstep, fm = relax(atoms, calc64, fmax=0.05, steps=rsteps(1500))
            log(f'{nwat} recombined H2O removed; re-relax: {nstep} steps, max force {fm:.3f} eV/A')
    f.close()
    snaps.append(('final', atoms.copy()))

    res = qc(atoms, mode, origin)
    info.update(extra)   # empty except for the HfO2 cell
    res.update(info)
    res.update({'spec': spec, 'final_max_force_eV_A': fm, 'model': a.model,
                'energy_eV': float(atoms.get_potential_energy())})
    json.dump(res, open(f'{name}_qc.json', 'w'), indent=1, default=str)
    write(f'{name}.xyz', atoms, format='extxyz')
    for tag, s in snaps:   # snapshots with MACE energies/forces for the DFT force check
        s.set_constraint()   # unconstrained forces (the oxide is fixed in the interface melt snapshot)
        s.calc = calc64
        s.info['tag'] = tag
        s.info['mace_energy_eV'] = float(s.get_potential_energy())
        s.arrays['mace_forces'] = s.get_forces().copy()
        s.calc = None
        write(f'{name}_snapshots.xyz', s, format='extxyz', append=True)
    with open(f'{name}_qe.txt', 'w') as g:
        g.write('CELL_PARAMETERS angstrom\n')
        for v in atoms.cell:
            g.write('  {:.10f} {:.10f} {:.10f}\n'.format(*v))
        g.write('ATOMIC_POSITIONS angstrom\n')
        for s, p in zip(atoms.get_chemical_symbols(), atoms.positions):
            g.write(f'{s:2s} {p[0]:14.8f} {p[1]:14.8f} {p[2]:14.8f}\n')
    log(f"QC {res['QC']} {res['QC_reasons']}")
    return 0 if res['QC'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
