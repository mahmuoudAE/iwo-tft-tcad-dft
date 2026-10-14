"""rc3 test builders: sealed, certified-style cell records (Gaussian FINALs, valid planar averages) and the registered
constructions (C1 parent / paired cells / atom maps, C2 dilution, C6 starts with a split first-shell O label, C5
PAW / NC / HSE settings, interface cells). Synthetic data only; nothing here is a physics result."""
import itertools

import numpy as np

from analysis.tests.helpers import manifest, pp_certified, qualification
from analysis.tests.synth import SynthCell, bulk_structure, slab_structure
from analysis.certify import unqualified
from analysis.geometry import Structure
from analysis.register import BOHR_A, RY_EV
from analysis.report import cell_result
from analysis.section1 import Section1
from analysis.smearing import ngauss_of, wgauss

_SEED = itertools.count(5000)
PAW_SPECIES = [{'name': e, 'pseudo_file': f'{e}.pbe-paw.UPF', 'starting_magnetization': 0.0} for e in ('H', 'In', 'O', 'W')]
NC_SPECIES = [{'name': e, 'pseudo_file': f'{e}_ONCV_PBE_sg15.upf', 'starting_magnetization': 0.0}
              for e in ('H', 'In', 'O', 'W')]
PAW = {'functional': 'PBE', 'paw': True, 'uspp': False, 'hybrid': None, 'species': PAW_SPECIES}


# ---------------------------------------------------------------- geometries
def slab(dx=0.0, n_int=50, shell_O=True, w=True):
    """Slab with a 12.25 A interior (alignment can be valid), one interior W (w) and (shell_O) one O moved to 2.0 A of
    the W (its first shell). dx shifts every atom along x (another network / seed)."""
    st, idx = slab_structure(n_int=n_int, w_interior_index=10 if w else None, target_nex=1 if w else 0)
    sp, pos = list(st.species), st.pos.copy()
    if shell_O and w:
        j = idx['W'] + 1
        sp[j] = 'O'
        pos[j] = pos[idx['W']] + [2.0, 0.0, 0.0]
        idx = dict(idx, shell=j)
    pos[:, 0] += dx
    return Structure(sp, pos, st.cell), idx


def bulk(dx=0.0):
    st = bulk_structure()
    pos = st.pos.copy()
    pos[:, 0] += dx
    st = Structure(st.species, pos, st.cell)
    return st, {'interior': list(range(st.nat)), 'W': 5, 'top': [], 'bottom': [], 'H': []}


def interface(dx=0.0):
    """Al2O3-like substrate (z 5..16 A) under an In/O/W film (z 17..40 A) with H on top: interface mode, a film interior
    of ~17 A (alignment can be valid)."""
    sp, pos = [], []
    for i, z in enumerate(np.arange(5.0, 16.01, 0.5)):
        sp.append('Al' if i % 2 == 0 else 'O')
        pos.append([(i % 4) * 2.5 + dx, (i // 4 % 4) * 2.5, z])
    film = np.arange(17.0, 40.01, 0.5)
    w_at = None
    for i, z in enumerate(film):
        e = 'In' if i % 2 == 0 else 'O'
        if abs(z - 28.0) < 1e-9:
            e, w_at = 'W', len(sp)
        sp.append(e)
        pos.append([(i % 4) * 2.5 + dx, (i // 4 % 4) * 2.5, z])
    for j in range(3):
        sp.append('H')
        pos.append([0.5 + 2.5 * j + dx, 1.25, 41.0])
    st = Structure(sp, pos, [[12.0, 0, 0], [0, 12.0, 0], [0, 0, 70.0]])
    from analysis.geometry import regions
    m, _ = regions(st, 'interface')
    return st, {'interior': [i for i in range(st.nat) if m['interior'][i]], 'W': w_at,
                'interface': [i for i in range(st.nat) if m['interface'][i]]}


def flat_avg(st, V_ev=1.0, slope=0.0, plot_num=11):
    """A complete plot_num 11 planar average over the cell (flat at V_ev, optional ramp in eV/A)."""
    c_b = float(st.cell[2, 2]) / BOHR_A
    z = np.linspace(0, c_b, 3001)[:-1]
    v = V_ev + slope * (z * BOHR_A - 0.5 * c_b * BOHR_A)
    return {'z_bohr': z, 'planar_ry': v / RY_EV, 'macro_ry': None, 'window_bohr': 4.0, 'plot_num': plot_num}


# ---------------------------------------------------------------- electronic states + record
def _ef_for_half(fam, deg_ev, E):
    """E_F at which a state at E holds f = 1/2 for this smearing family."""
    ng = ngauss_of(fam)
    lo, hi = -5.0, 5.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if wgauss(np.array([mid]), ng)[0] < 0.5:
            lo = mid
        else:
            hi = mid
    return E + 0.5 * (lo + hi) * deg_ev


def states(st, idx, nex=1, vb=-2.0, edge=0.0, w_E=0.5, top=1.5, loc_w=False, nspin=1, w5d=0.9, extra=()):
    """Valence (4 bands: vb-1, vb-0.5, vb-0.2 on all atoms, vb on the interior); then for nex = 1 the donor (extended
    host edge at `edge`, W state at w_E, top band) or the ECB (W trap 0.5 eV below the edge); for nex = 0 an empty edge.
    Returns (SynthCell, nelec, energy that must hold f = 1/2 or None for E_F mid-gap)."""
    ALL = list(range(st.nat))
    sc = SynthCell(st, nspin=nspin)
    sc.add(vb - 1.0, ALL).add(vb - 0.5, ALL).add(vb - 0.2, ALL).add(vb, idx['interior'])
    W = idx.get('W')
    if nex == 1 and loc_w:
        sc.add(edge - 0.5, {W: 1.0}, w5d=w5d).add(edge, ALL).add(w_E, ALL)
        half = edge - 0.5
    elif nex == 1:
        sc.add(edge, ALL)
        if W is not None:
            sc.add(w_E, {W: 1.0}, w5d=w5d)
        half = edge
    else:
        sc.add(edge, ALL)
        if W is not None:
            sc.add(w_E, {W: 1.0}, w5d=w5d)
        half = None
    for args, kw in extra:
        sc.add(*args, **kw)
    sc.add(top, ALL)
    return sc, 8.0 + nex, half


def make(name='aIWO_2p0_s1', geo=None, kind='W-doped', nex=None, vb=-2.0, edge=0.0, w_E=0.5, top=1.5, loc_w=False,
         w_ry=0.001, fam='gaussian', shift=0.0, nspin=1, settings=None, source='xml', V=1.0, avg=True, seed=None,
         geometry='polished', relaxation='converged', smearing_ok=True, certified=True, man_extra=None, etot=None,
         extra=(), mode='auto', labels=None, w5d=0.9, w5d_convention='normalised', q=None, ef=None, upf_hashes=None):
    """A sealed cell record of the current code (report.cell_result) with a certified-style qualification."""
    st, idx = geo if geo is not None else slab()
    if labels is not None:
        st = Structure(st.species, st.pos, st.cell, labels)
    if nex is None:
        nex = 1 if kind == 'W-doped' else 0
    sc, nelec, half = states(st, idx, nex=nex, vb=vb + shift, edge=edge + shift, w_E=w_E + shift, top=top + shift,
                             loc_w=loc_w, nspin=nspin, w5d=w5d, extra=extra)
    deg = w_ry * RY_EV
    if ef is None:
        ef = _ef_for_half(fam, deg, half) if half is not None else 0.5 * (vb + edge) + shift
    sets = dict(PAW)
    sets.update(settings or {})
    data = sc.build(nelec, ef=ef, smearing=fam, degauss_ev=deg, etot_ry=etot, settings=sets)
    man = None
    if certified:
        man = manifest(nex, kind, next(_SEED) if seed is None else seed)
        man['passivation'] = 'none' if (man_extra or {}).get('passivation') == 'none' else 'dissociated-water'
        man.update(man_extra or {})
        if q is None:
            q = qualification(man, relaxation=relaxation, smearing=smearing_ok, geometry=geometry,
                              pseudos=pp_certified(data, upf_hashes))
    elif q is None:
        q = unqualified('no certificate given')
    if avg is True:
        avg = flat_avg(st, V)
    c = Section1(data, st, name=name, nex=None if man else nex, mode=mode, avg=avg or None, manifest=man,
                 w5d_convention=w5d_convention)
    return cell_result(c, source, qual=q)


# ---------------------------------------------------------------- constructions
def c1_parent(dx=0.0, n_sites=4):
    """aIO parent slab with n_sites interior In octahedra (six O at 2.1 A: CN 6) and surface layers; no W."""
    sp, pos = [], []
    for i, z in enumerate((10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0)):
        sp.append('In' if i % 2 == 0 else 'O')
        pos.append([1.0 + 2.0 * i, 1.0, z])
    centres = [(3.75, 3.75), (11.25, 3.75), (3.75, 11.25), (11.25, 11.25)][:n_sites]
    sites = []
    for (x, y) in centres:
        sites.append(len(sp))
        sp.append('In')
        pos.append([x, y, 17.5])
        for d in ((2.1, 0, 0), (-2.1, 0, 0), (0, 2.1, 0), (0, -2.1, 0), (0, 0, 2.1), (0, 0, -2.1)):
            sp.append('O')
            pos.append([x + d[0], y + d[1], 17.5 + d[2]])
    for i, z in enumerate((22.0, 22.5, 23.0, 23.5, 24.0, 24.5, 25.0)):
        sp.append('In' if i % 2 == 0 else 'O')
        pos.append([1.0 + 2.0 * i, 13.0, z])
    pos = np.array(pos)
    pos[:, 0] += dx
    st = Structure(sp, pos, [[15.0, 0, 0], [0, 15.0, 0], [0, 0, 40.0]])
    from analysis.geometry import regions
    m, _ = regions(st, 'slab')
    return st, {'interior': [i for i in range(st.nat) if m['interior'][i]], 'W': None, 'sites': sites}


def c1_paired(parent_geo, k):
    """Parent with site k (0-based in parent_geo sites) In -> W and one O added at 2.12 A of the W; the atom map
    (paired 1-based -> parent 1-based, added O -> None)."""
    st, idx = parent_geo
    s = idx['sites'][k]
    sp = list(st.species)
    sp[s] = 'W'
    pos = np.vstack([st.pos, st.pos[s] + [1.5, 1.5, 0.0]])
    sp.append('O')
    stc = Structure(sp, pos, st.cell)
    amap = {str(i + 1): i + 1 for i in range(st.nat)}
    amap[str(stc.nat)] = None
    return (stc, dict(idx, W=s, added_O=stc.nat - 1)), amap


def atom_map(paired_rec, parent_rec, m):
    return {'paired_geometry_sha256': paired_rec['geometry_sha256'],
            'parent_geometry_sha256': parent_rec['geometry_sha256'], 'paired_to_parent': dict(m)}


def c1_set(t='0p7', main_loc_w=True, paired_loc_w=(True, True, True), main_geo=None, parent_dx=0.0, parent_kw=None,
           **kw):
    """Main (independent quench), parent (aIO), three paired cells (sites 1-3) and their atom maps."""
    pg = c1_parent(parent_dx)
    parent = make(f'aIO_{t}_s1', geo=pg, kind='undoped', **dict(kw, **(parent_kw or {})))
    paired, maps = [], []
    for k, lw in enumerate(paired_loc_w):
        geo, m = c1_paired(pg, k)
        cons = {'type': 'C1-paired', 'parent_geometry_sha256': parent['geometry_sha256'],
                'site': pg[1]['sites'][k] + 1, 'draw_rank': k + 1}
        r = make(f'aIWO_{t}_C1{"abc"[k]}', geo=geo, loc_w=lw, man_extra={'construction': cons}, **kw)
        paired.append(r)
        maps.append(atom_map(r, parent, m))
    main = make(f'aIWO_{t}_s1', geo=main_geo or slab(0.37), loc_w=main_loc_w, **kw)
    return main, parent, paired, maps


def diluted(full_geo, full_rec, loc_w=True, **kw):
    """C2: 2 x 1 lateral supercell of the paired cell, W -> In and the added O removed in the second image."""
    st, idx = full_geo
    a = st.cell[0]
    sp = list(st.species) + list(st.species)
    pos = np.vstack([st.pos, st.pos + a])
    w2 = st.nat + idx['W']
    sp[w2] = 'In'
    drop = st.nat + idx['added_O']
    keep = [i for i in range(len(sp)) if i != drop]
    cell = np.array(st.cell)
    cell[0] = 2 * a
    std = Structure([sp[i] for i in keep], pos[keep], cell)
    interior = [keep.index(i) for i in idx['interior'] + [st.nat + j for j in idx['interior']] if i in keep]
    cons = {'type': 'C2-diluted', 'source_geometry_sha256': full_rec['geometry_sha256']}
    k = list(full_rec['run_settings']['k_mesh'])
    k[0] = max(1, -(-k[0] // 2))
    return make(full_rec['cell'] + '_2x1', geo=(std, {'interior': interior, 'W': idx['W']}), loc_w=loc_w,
                man_extra={'construction': cons}, settings=dict(kw.pop('settings', {}) or {}, k_mesh=k), **kw)


def spin_starts(ref_name, geo, loc_w=False, e_loc=-10.002, e_deloc=-10.001, **kw):
    """C6: the localised start (moment on W and on its first-shell O, split label O1) and the delocalised start (equal
    0.1 on every species), nspin = 2, XML source, at the geometry `geo` (which has one shell O, idx['shell'])."""
    st, idx = geo
    labels = list(st.species)
    labels[idx['shell']] = 'O1'
    loc_sp = [dict(s, starting_magnetization=0.5 if s['name'] == 'W' else 0.0) for s in PAW_SPECIES]
    loc_sp.append({'name': 'O1', 'pseudo_file': 'O.pbe-paw.UPF', 'starting_magnetization': 0.3})
    de_sp = [dict(s, starting_magnetization=0.1) for s in PAW_SPECIES]
    a = make(ref_name, geo=geo, nspin=2, etot=e_loc, labels=labels, loc_w=loc_w,
             settings={'lsda': True, 'species': loc_sp}, **kw)
    b = make(ref_name, geo=geo, nspin=2, etot=e_deloc, loc_w=loc_w, settings={'lsda': True, 'species': de_sp}, **kw)
    return a, b


def c5_runs(name, geo, loc_w=False, hse_loc_w=None, gamma=False, common=None, **kw):
    """PAW-PBE (production k-mesh), NC-PBE and HSE06 (SG15, 80 Ry, ecutfock 160, q = k) at one geometry and width."""
    k = [2, 2, 1, 0, 0, 0]
    kk = [1, 1, 1, 0, 0, 0] if gamma else k
    nc = {'functional': 'PBE', 'paw': False, 'uspp': False, 'hybrid': None, 'species': NC_SPECIES, 'ecutwfc_Ry': 80.0,
          'ecutrho_Ry': 320.0, 'k_mesh': kk}
    hse = dict(nc, functional='HSE', hybrid={'exx_fraction': 0.25, 'screening_parameter': 0.106},
               ecutfock_Ry=160.0, q_mesh=list(kk[:3]))
    common = common or {}
    nc, hse = dict(nc, **common), dict(hse, **common)
    paw = make(name, geo=geo, loc_w=loc_w, settings=dict({'k_mesh': k}, **common), **kw)
    ncr = make(name + '_NC', geo=geo, loc_w=loc_w, settings=nc, **kw)
    hr = make(name + '_HSE06', geo=geo, loc_w=loc_w if hse_loc_w is None else hse_loc_w, settings=hse, **kw)
    return paw, ncr, hr
