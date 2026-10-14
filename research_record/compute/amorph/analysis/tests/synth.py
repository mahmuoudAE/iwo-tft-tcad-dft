"""Synthetic cells for the tests: exact-binary geometries, explicit states, and writers of QE-format files
(data-file-schema.xml, atomic_proj.xml, projwfc.x map/out) so that the parsers and the real D-24 table exporter
(steps_final.sh.D24, export_tables) can be run on synthetic data. No DFT is run; nothing here is a physics result."""
import itertools
import math
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..')))

from analysis.data import ElectronicData   # noqa: E402
from analysis.geometry import Structure     # noqa: E402
from analysis.register import BOHR_A, HA_EV, RY_EV   # noqa: E402
from analysis.smearing import occupations   # noqa: E402

_SERIAL = itertools.count(1)   # unique pseudo-hash per synthetic build (id() is reused after garbage collection)
STEPS_FINAL_D24 = os.path.abspath(os.path.join(HERE, '..', '..', 'dft', 'steps_final.sh.D24'))


# ---------------------------------------------------------------- geometry
def slab_structure(n_bot=7, n_int=20, n_top=7, n_h_top=3, n_h_bot=3, w_interior_index=10, cell_xy=12.5, c=40.0,
                   species_override=None, target_nex=1):
    """Slab with exact-binary z: bottom-surface atoms at 10.0 .. 13.0 (the last exactly 3.0 A above the outermost),
    interior atoms from 13.25 in 0.25 A steps, top-surface atoms from z_top - 3.0 (exactly) to z_top in 0.5 A steps
    (n_top = 7), H 1 A outside each face. One W in the interior. Non-H atoms are In/O, with the In count chosen so that
    the formal-charge count equals target_nex when that is possible (the default 40-atom slab: In 11, W 1, O 22,
    H 6, N_ex 1, a composition a dissociated-water manifest can certify); otherwise they alternate In/O."""
    zb = [10.0 + 3.0 * i / (n_bot - 1) for i in range(n_bot)]
    zi = [13.25 + 0.25 * i for i in range(n_int)]
    z0 = 13.25 + 0.25 * n_int
    zt = [z0 + 3.0 * i / (n_top - 1) for i in range(n_top)]
    z = zb + zi + zt
    sp = ['In' if i % 2 == 0 else 'O' for i in range(len(z))]
    w_idx = n_bot + w_interior_index if w_interior_index is not None else None
    n_w = 1 if w_idx is not None else 0
    n_h = n_h_top + n_h_bot
    if target_nex is not None:
        num = target_nex + 2 * (len(z) - n_w) - 6 * n_w - n_h          # 3 In + 6 W + H - 2 O = target, O = rest
        if num % 5 == 0 and 0 < num // 5 < len(z) - n_w:
            n_in = num // 5
            others = [i for i in range(len(z)) if i != w_idx]
            pick = {others[int(round(j))] for j in np.linspace(0, len(others) - 1, n_in)}
            sp = ['In' if i in pick else 'O' for i in range(len(z))]
    if w_idx is not None:
        sp[w_idx] = 'W'
    pos = [[(i % 5) * 2.5, (i // 5 % 5) * 2.5, zz] for i, zz in enumerate(z)]
    ztop = max(z)
    for j in range(n_h_top):
        sp.append('H')
        pos.append([0.5 + 2.5 * j, 1.25, ztop + 1.0])
    for j in range(n_h_bot):
        sp.append('H')
        pos.append([0.5 + 2.5 * j, 1.25, 9.0])
    if species_override:
        for i, s in species_override.items():
            sp[i] = s
    st = Structure(sp, pos, [[cell_xy, 0, 0], [0, cell_xy, 0], [0, 0, c]])
    idx = {'bottom': list(range(n_bot)), 'interior': list(range(n_bot, n_bot + n_int)),
           'top': list(range(n_bot + n_int, n_bot + n_int + n_top)),
           'H': list(range(n_bot + n_int + n_top, len(sp))), 'W': w_idx}
    return st, idx


def bulk_structure(n=40, w_index=5):
    sp = ['In' if i % 2 == 0 else 'O' for i in range(n)]
    sp[w_index] = 'W'
    pos = [[(i % 4) * 2.5, (i // 4 % 4) * 2.5, (i // 16) * 2.5] for i in range(n)]
    return Structure(sp, pos, [[10.0, 0, 0], [0, 10.0, 0], [0, 0, 7.5]])


# ---------------------------------------------------------------- electronic states
class SynthCell:
    """Explicit states. add() appends one state to every (spin, k) unless spin/k are given; states are sorted by
    energy inside each (spin, k) at build time (band order)."""

    def __init__(self, st, nspin=1, nks=1, wk=None):
        self.st, self.nspin, self.nks = st, nspin, nks
        self.wk = np.ones(nks) if wk is None else np.asarray(wk, dtype=float)
        self.rows = {(s, k): [] for s in range(nspin) for k in range(nks)}

    def add(self, E, atoms, w5d=0.0, compl=1.0, f=0.0, spin=None, k=None):
        N = self.st.nat
        w = np.zeros(N)
        if isinstance(atoms, dict):
            for a, x in atoms.items():
                w[a] += x
        else:
            for a in atoms:
                w[a] += 1.0 / len(atoms)
        tot = w.sum()
        w = w / tot * compl if tot != 1.0 else w * compl
        for key in self.rows:
            if (spin is None or key[0] == spin) and (k is None or key[1] == k):
                self.rows[key].append((E, w, w5d * compl, compl, f))
        return self

    def build(self, nelec, ef=0.0, smearing=None, degauss_ev=0.0, etot_ry=None, proj_kind='exact', settings=None,
              source_tag=None):
        nb = {len(v) for v in self.rows.values()}
        if len(nb) != 1:
            raise ValueError(f'unequal band counts {nb}')
        nb = nb.pop()
        N = self.st.nat
        e = np.zeros((self.nspin, self.nks, nb))
        f = np.zeros_like(e)
        aw = np.zeros((self.nspin, self.nks, nb, N))
        w5 = np.zeros_like(e)
        cp = np.zeros_like(e)
        for (s, k), rows in self.rows.items():
            for n, (E, w, w5d, c, ff) in enumerate(sorted(rows, key=lambda r: r[0])):
                e[s, k, n], aw[s, k, n], w5[s, k, n], cp[s, k, n], f[s, k, n] = E, w, w5d, c, ff
        kind = 'smearing' if smearing else 'fixed'
        if smearing:   # QE's own occupations, as data-file-schema.xml would hold them
            efs = np.broadcast_to(np.atleast_1d(np.asarray(ef, dtype=float)), (self.nspin,))
            f = np.stack([occupations(e[s], efs[s], degauss_ev, smearing) for s in range(self.nspin)])
        sets = {'source': 'synthetic', 'functional': 'PBE', 'hybrid': None, 'lsda': self.nspin == 2,
                'smearing': smearing, 'degauss_Ry': None if not smearing else round(degauss_ev / RY_EV, 10),
                'occupations': kind, 'ecutwfc_Ry': 60.0, 'ecutrho_Ry': 480.0, 'k_mesh': [2, 2, 1, 0, 0, 0],
                'species': [{'name': e, 'pseudo_file': f'{e}.upf', 'starting_magnetization': 0.0}
                            for e in sorted(set(self.st.species))], 'scf_converged': True}
        sets.update(settings or {})
        tag = source_tag or f'synthetic-{next(_SERIAL)}'
        return ElectronicData(nspin=self.nspin, e_ev=e, wk_raw=np.tile(self.wk, (self.nspin, 1)), nelec=nelec,
                              ef_ev=ef, smearing=smearing, degauss_ev=degauss_ev, occupations_kind=kind, f_qe=f,
                              atom_w=aw, w5d=w5, compl=cp, proj_kind=proj_kind, species=self.st.species,
                              etot_ry=etot_ry, sources={'synthetic': {'sha256': tag}}, settings=sets)


def donor_cell(st=None, idx=None, nks=1, **kw):
    """Canonical DONOR cell (fixed occupations, N_ex = 1, N_v = 4): E_v -2.0 (interior, PR 0.5), host edge 0.0 (all
    atoms, PR 1, interior weight 0.5), W state 0.5 eV (W-5d 0.9, PR 1/40), top band 1.5 eV."""
    if st is None:
        st, idx = slab_structure()
    ALL = list(range(st.nat))
    sc = SynthCell(st, nks=nks)
    sc.add(-3.0, ALL, f=1.0).add(-2.5, ALL, f=1.0).add(-2.2, ALL, f=1.0).add(-2.0, idx['interior'], f=1.0)
    sc.add(0.0, ALL, f=0.5).add(0.5, {idx['W']: 1.0}, w5d=0.9).add(1.5, ALL)
    return sc, st, idx


# ---------------------------------------------------------------- QE-format writers
ORBITALS = {'In': [(0, 1), (1, 3), (2, 5)], 'W': [(0, 1), (1, 3), (2, 5), (0, 1)], 'O': [(0, 1), (1, 3)],
            'H': [(0, 1)], 'Al': [(0, 1), (1, 3)], 'Hf': [(0, 1), (1, 3), (2, 5)]}


def state_map(species, labels=None):
    """projwfc.x state map rows (atom, label, wfc, l, m); labels (e.g. A30 split In1/In2, O1/O2) as printed by QE."""
    rows = []
    for a, s in enumerate(species, 1):
        name = s if labels is None else labels[a - 1]
        for w, (l, nm) in enumerate(ORBITALS[s], 1):
            rows += [(a, name, w, l, m) for m in range(1, nm + 1)]
    return rows


def orbital_weights(data, species):
    """[spin, k, band, orbital] |c|^2 distributing each atom weight over its orbitals; W-5d weight on the W d set."""
    smap = state_map(species)
    ns, nk, nb, N = data.atom_w.shape
    out = np.zeros((ns, nk, nb, len(smap)))
    for a in range(N):
        orbs = [i for i, r in enumerate(smap) if r[0] == a + 1]
        if species[a] == 'W':
            d = [i for i in orbs if smap[i][3] == 2]
            nd = [i for i in orbs if smap[i][3] != 2]
            wd = np.minimum(data.w5d, data.atom_w[..., a])
            for i in d:
                out[..., i] = wd / len(d)
            for i in nd:
                out[..., i] = (data.atom_w[..., a] - wd) / len(nd)
        else:
            for i in orbs:
                out[..., i] = data.atom_w[..., a] / len(orbs)
    return out, smap


def write_schema(path, data, st, lsda=None, two_fermi=None, etot_ry=-100.0):
    lsda = data.nspin == 2 if lsda is None else lsda
    ha = lambda x: f'{x / HA_EV:.15e}'
    s = data.settings or {}
    sp = s.get('species') or [{'name': e, 'pseudo_file': f'{e}.upf', 'starting_magnetization': 0.0}
                              for e in sorted(set(st.species))]
    km = s.get('k_mesh') or [2, 2, 1, 0, 0, 0]
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<qes:espresso xmlns:qes="http://www.quantum-espresso.org/ns/qes/qes-1.0">',
         '<input>',
         f'<atomic_species ntyp="{len(sp)}">' + ''.join(
             f'<species name="{x["name"]}"><mass>1.0</mass><pseudo_file>{x["pseudo_file"]}</pseudo_file>'
             + (f'<starting_magnetization>{x["starting_magnetization"]}</starting_magnetization>' if lsda else '')
             + '</species>' for x in sp) + '</atomic_species>',
         f'<dft><functional>{s.get("functional", "PBE")}</functional></dft>',
         f'<spin><lsda>{"true" if lsda else "false"}</lsda><noncolin>false</noncolin></spin>',
         '<bands>' + (f'<smearing degauss="{data.degauss_ev / HA_EV:.15e}">{data.smearing}</smearing>'
                      if data.smearing else '') + f'<occupations>{data.occupations_kind}</occupations></bands>',
         f'<basis><ecutwfc>{s.get("ecutwfc_Ry", 60.0) / 2:.15e}</ecutwfc><ecutrho>{s.get("ecutrho_Ry", 480.0) / 2:.15e}'
         '</ecutrho></basis>',
         '<k_points_IBZ><monkhorst_pack nk1="{}" nk2="{}" nk3="{}" k1="{}" k2="{}" k3="{}">Monkhorst-Pack'
         '</monkhorst_pack></k_points_IBZ>'.format(*km),
         '</input>', '<output>',
         '<convergence_info><scf_conv><convergence_achieved>'
         + ('true' if s.get('scf_converged', True) else 'false')
         + '</convergence_achieved><n_scf_steps>10</n_scf_steps></scf_conv></convergence_info>',
         f'<atomic_structure nat="{st.nat}"><atomic_positions>']
    for i, (s, p) in enumerate(zip(st.labels, st.pos), 1):
        L.append(f'<atom name="{s}" index="{i}">' + ' '.join(f'{x / BOHR_A:.15e}' for x in p) + '</atom>')
    L.append('</atomic_positions><cell>' + ''.join(f'<a{j + 1}>' + ' '.join(f'{x / BOHR_A:.15e}' for x in st.cell[j])
                                                   + f'</a{j + 1}>' for j in range(3)) + '</cell></atomic_structure>')
    L.append(f'<total_energy><etot>{etot_ry / 2:.15e}</etot></total_energy>')
    L.append(f'<band_structure><lsda>{"true" if lsda else "false"}</lsda><noncolin>false</noncolin>')
    if lsda:
        L.append(f'<nbnd_up>{data.nbnd}</nbnd_up><nbnd_dw>{data.nbnd}</nbnd_dw>')
    else:
        L.append(f'<nbnd>{data.nbnd}</nbnd>')
    L.append(f'<nelec>{data.nelec:.15e}</nelec>')
    if two_fermi:
        L.append('<two_fermi_energies>' + ' '.join(ha(x) for x in two_fermi) + '</two_fermi_energies>')
    elif data.occupations_kind == 'smearing':
        L.append(f'<fermi_energy>{ha(data.ef[0])}</fermi_energy>')
    L.append(f'<occupations_kind>{data.occupations_kind}</occupations_kind>')
    if data.smearing:
        L.append(f'<smearing degauss="{data.degauss_ev / HA_EV:.15e}">{data.smearing}</smearing>')
    for k in range(data.nks):
        ev = np.concatenate([data.e[s, k] for s in range(data.nspin)])
        oc = np.concatenate([data.f_qe[s, k] for s in range(data.nspin)])
        L.append(f'<ks_energies><k_point weight="{data.wk_raw[0, k]:.15e}">0.0 0.0 {0.1 * k:.3f}</k_point>'
                 f'<npw>100</npw><eigenvalues size="{len(ev)}">' + ' '.join(ha(x) for x in ev) + '</eigenvalues>'
                 f'<occupations size="{len(oc)}">' + ' '.join(f'{x:.15e}' for x in oc) + '</occupations></ks_energies>')
    L.append('</band_structure></output></qes:espresso>')
    with open(path, 'w', newline='\n') as f:
        f.write('\n'.join(L) + '\n')


def write_atomic_proj(path, data, species, spin_attr=True, nk_header='per_spin', drop=None, phase=0.3, kcoords=None):
    """atomic_proj.xml in the QE 7 layout (all up k blocks, then all down). drop=(block, orbital) omits one orbital."""
    ow, smap = orbital_weights(data, species)
    nk_hdr = data.nks if nk_header == 'per_spin' else data.nks * data.nspin
    L = ['<?xml version="1.0"?>', '<PROJECTIONS>',
         f'<HEADER NUMBER_OF_BANDS="{data.nbnd}" NUMBER_OF_K-POINTS="{nk_hdr}" NUMBER_OF_SPIN_COMPONENTS="{data.nspin}" '
         f'NON-COLINEAR_CALCULATION="F" NUMBER_OF_ATOMIC_WFC="{len(smap)}" NUMBER_OF_ELECTRONS="{data.nelec}" '
         f'UNITS_FOR_ENERGY="Rydberg" FERMI_ENERGY="{data.ef[0] / RY_EV:.15e}"/>', '<EIGENSTATES>']
    blk = 0
    for s in range(data.nspin):
        for k in range(data.nks):
            kc = f'0.0 0.0 {0.1 * k:.3f}' if kcoords is None else ' '.join(f'{x:.6f}' for x in kcoords[k])
            L.append(f'<K-POINT Weight="{data.wk_raw[s, k]:.15e}">{kc}</K-POINT>')
            L.append('<E>' + ' '.join(f'{x / RY_EV:.15e}' for x in data.e[s, k]) + '</E>')
            L.append('<PROJS>')
            for i in range(len(smap)):
                if drop == (blk, i):
                    continue
                amp = np.sqrt(np.maximum(0.0, ow[s, k, :, i]))
                re_, im_ = amp * math.cos(phase * (i + 1)), amp * math.sin(phase * (i + 1))
                sa = f' spin="{s + 1}"' if spin_attr else ''
                L.append(f'<ATOMIC_WFC index="{i + 1}"{sa}>\n' + '\n'.join(f'{x:24.15E}{y:24.15E}' for x, y in zip(re_, im_))
                         + '\n</ATOMIC_WFC>')
            L.append('</PROJS>')
            blk += 1
    L += ['</EIGENSTATES>', '</PROJECTIONS>']
    with open(path, 'w', newline='\n') as f:
        f.write('\n'.join(L) + '\n')


def write_projwfc_out(path, data, species, labels=None):
    """Minimal projwfc.x output: the state map and, per k block, energies and |psi|^2 (the D-24 exporter reads both)."""
    smap = state_map(species, labels)
    L = ['     Atomic states used for projection', '']
    L += [f'     state #{i:5d}: atom {a:4d} ({s:<3s}), wfc {w:2d} (l={l} m={m:2d})' for i, (a, s, w, l, m) in
          enumerate(smap, 1)]
    for s in range(data.nspin):
        for k in range(data.nks):
            L.append(f' k =   0.0000000000  0.0000000000  {0.1 * k:.10f}')
            for n in range(data.nbnd):
                L.append(f'==== e({n + 1:5d}) = {data.e[s, k, n]:11.5f} eV ==== ')
                L.append('     psi = 1.000*[#   1]+')
                L.append(f'    |psi|^2 = {data.compl[s, k, n]:.3f}')
    with open(path, 'w', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    return smap


def write_lineage(directory, data, job='final'):
    """lineage_<job>.dat in the D-24 layout: one 'sha256 <hash> pseudo/<file>' line per pseudopotential of the run
    (synthetic hashes of the file names)."""
    import hashlib
    files = sorted({s['pseudo_file'] for s in (data.settings or {}).get('species', [])})
    path = os.path.join(directory, f'lineage_{job}.dat')
    lines = ['# synthetic lineage'] + [f'sha256 {hashlib.sha256(x.encode()).hexdigest()} pseudo/{x}' for x in files]
    with open(path, 'w', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    return path


def write_scf_in(path, st):
    L = ['&CONTROL', "  calculation = 'scf'", '/', '&SYSTEM', f'  ibrav = 0, nat = {st.nat}, ntyp = 4', '/',
         'CELL_PARAMETERS angstrom'] + ['  ' + ' '.join(f'{x:.10f}' for x in v) for v in st.cell] + \
        ['ATOMIC_POSITIONS angstrom'] + [f'  {s} ' + ' '.join(f'{x:.10f}' for x in p) for s, p in zip(st.labels, st.pos)]
    with open(path, 'w', newline='\n') as f:
        f.write('\n'.join(L) + '\n')


def d24_export_script():
    """The python program embedded in export_tables() of steps_final.sh.D24 (the frozen D-24 exporter)."""
    with open(STEPS_FINAL_D24, encoding='utf-8') as f:
        txt = f.read()
    body = txt.split('export_tables() {', 1)[1]
    m = re.search(r"<<'PY'\n(.*?)\nPY\n", body, re.S)
    return m.group(1)


def run_d24_exporter(workdir, data, st, python=sys.executable):
    """Write the synthetic FINAL files into workdir and run the real D-24 table exporter there."""
    sv = os.path.join(workdir, 'tmp', 'slab.save')
    os.makedirs(sv, exist_ok=True)
    write_schema(os.path.join(sv, 'data-file-schema.xml'), data, st)
    write_atomic_proj(os.path.join(sv, 'atomic_proj.xml'), data, st.species)
    write_projwfc_out(os.path.join(workdir, 'projwfc_final.out'), data, st.species, st.labels)
    write_scf_in(os.path.join(workdir, 'scf.in'), st)
    script = os.path.join(workdir, 'export_tables.py')
    with open(script, 'w', newline='\n') as f:
        f.write(d24_export_script())
    r = subprocess.run([python, script, 'tmp/slab.save', 'final'], cwd=workdir, capture_output=True, text=True)
    return r
