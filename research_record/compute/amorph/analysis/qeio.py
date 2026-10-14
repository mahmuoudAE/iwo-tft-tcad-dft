"""Parsers for the Quantum ESPRESSO outputs of a FINAL export (D-24) and of the crystalline reference runs.

Supported inputs (all may be gzip-compressed):
  data-file-schema.xml   eigenvalues, k-weights, QE occupations, Fermi level(s), smearing, nspin, nbnd, nelec, geometry,
                         total energy (QE >= 6.4 schema; lsda supported, noncollinear refused)
  atomic_proj.xml        projwfc.x Loewdin projections <phi_i|psi_nk>, streamed; per-atom weights, W-5d weight and
                         completeness (sum over all orbitals) per state; lsda via the ATOMIC_WFC 'spin' attribute
  projwfc_map_final.dat  or the 'state #' lines of a projwfc.x output: orbital -> atom, species, l, m
  occ_kw_final.dat + proj_atoms_final.dat   the D-24 AFS tables (1e-6 rounded atom weights)
  projwfc.x text output  printed components (>= 0.001 only, 3 decimals): APPROXIMATE, crystalline reproduction only
  pw.x input / output    geometry, smearing, eigenvalues, k-weights, Fermi level (crystalline reproduction)
  average.x avg.dat      z (bohr), planar average (Ry), macroscopic average (Ry); the window from the avg input
Energies are returned in eV, lengths in Angstrom.
"""
import gzip
import hashlib
import io
import json
import os
import re
import xml.etree.ElementTree as ET

import numpy as np

from .register import BOHR_A, HA_EV, RY_EV


# ---------------------------------------------------------------- files
def open_text(path):
    """Text handle for a plain or .gz file."""
    if str(path).endswith('.gz'):
        return io.TextIOWrapper(gzip.open(path, 'rb'), encoding='utf-8', errors='replace')
    return open(path, encoding='utf-8', errors='replace')


def open_binary(path):
    return gzip.open(path, 'rb') if str(path).endswith('.gz') else open(path, 'rb')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def first_existing(directory, names):
    """First of names (also tried with .gz) in the FIRST directory that has any of them: directories are searched in the
    order given (rc3: directory order wins over name order, so a file beside a tarball cannot override the tarball's
    own file)."""
    dirs = [directory] if isinstance(directory, (str, os.PathLike)) else list(directory)
    for d in dirs:
        for n in names:
            for cand in (n, n + '.gz'):
                p = os.path.join(d, cand)
                if os.path.isfile(p):
                    return p
    return None


def load_json(path):
    """JSON from a file written in any UTF-8 flavour (BOM tolerated), independent of the platform encoding."""
    with open(path, encoding='utf-8-sig') as f:
        return json.load(f)


def element_of(label):
    """Species label -> element ('In1' -> 'In', 'O2' -> 'O'; A25 split labels)."""
    s = re.sub(r'[^A-Za-z]', '', label)
    return s[:1].upper() + s[1:].lower() if s else s


def _floats(text):
    return np.array(text.split(), dtype=float) if text and text.strip() else np.zeros(0)


# ---------------------------------------------------------------- data-file-schema.xml
def read_schema(path):
    """Everything the read-out needs from data-file-schema.xml. Raises ValueError for unsupported runs."""
    with open_binary(path) as fh:
        root = ET.parse(fh).getroot()
    out_el = root.find('output')
    if out_el is None:
        raise ValueError(f'{path}: no <output> element')
    bs = out_el.find('band_structure')
    if bs is None:
        raise ValueError(f'{path}: no <band_structure>')
    flag = lambda el, tag: (el.findtext(tag) or 'false').strip().lower() == 'true'
    lsda, noncolin = flag(bs, 'lsda'), flag(bs, 'noncolin')
    if noncolin:
        raise ValueError(f'{path}: noncollinear runs are not supported')
    nspin = 2 if lsda else 1
    if lsda:
        nb_up = int(bs.findtext('nbnd_up') or bs.findtext('nbnd'))
        nb_dw = int(bs.findtext('nbnd_dw') or bs.findtext('nbnd'))
        if nb_up != nb_dw:
            raise ValueError(f'{path}: nbnd_up {nb_up} != nbnd_dw {nb_dw} is not supported')
        nbnd = nb_up
    else:
        nbnd = int(bs.findtext('nbnd'))
    nelec = float(bs.findtext('nelec'))
    ef = None
    if bs.find('fermi_energy') is not None:
        v = float(bs.findtext('fermi_energy')) * HA_EV
        ef = [v] * nspin
    elif bs.find('two_fermi_energies') is not None:
        ef = list(_floats(bs.findtext('two_fermi_energies')) * HA_EV)
    homo = bs.findtext('highestOccupiedLevel')
    lumo = bs.findtext('lowestUnoccupiedLevel')
    occ_kind = (bs.findtext('occupations_kind') or '').strip().lower()
    sm = bs.find('smearing')
    if sm is None:
        sm = root.find('input/bands/smearing')
    smearing, degauss_ev = None, 0.0
    if sm is not None:
        smearing = (sm.text or '').strip()
        degauss_ev = float(sm.get('degauss', '0')) * HA_EV
    if not occ_kind:
        occ_kind = 'smearing' if smearing else 'fixed'
    ks = bs.findall('ks_energies')
    xk, wk, e, f = [], [], [], []
    for k in ks:
        kp = k.find('k_point')
        xk.append([float(x) for x in kp.text.split()])
        wk.append(float(kp.get('weight')))
        ev = _floats(k.findtext('eigenvalues')) * HA_EV
        oc = _floats(k.findtext('occupations'))
        if len(ev) != nspin * nbnd or len(oc) != nspin * nbnd:
            raise ValueError(f'{path}: k-point with {len(ev)} eigenvalues, expected {nspin * nbnd}')
        e.append(ev.reshape(nspin, nbnd))
        f.append(oc.reshape(nspin, nbnd))
    nks = len(ks)
    e = np.transpose(np.array(e), (1, 0, 2))           # [spin, k, band]
    f = np.transpose(np.array(f), (1, 0, 2))
    wk = np.array([wk] * nspin)                         # the same k-weights in both channels
    st = out_el.find('atomic_structure')
    names = [a.get('name') for a in st.find('atomic_positions').findall('atom')]
    pos = np.array([[float(x) for x in a.text.split()] for a in st.find('atomic_positions').findall('atom')]) * BOHR_A
    cell = np.array([[float(x) for x in st.find('cell').findtext(t).split()] for t in ('a1', 'a2', 'a3')]) * BOHR_A
    etot = out_el.findtext('total_energy/etot')
    settings = schema_settings(root)
    return {
        'path': path, 'nspin': nspin, 'nbnd': nbnd, 'nks': nks, 'nelec': nelec, 'ef_ev': ef,
        'homo_ev': float(homo) * HA_EV if homo else None, 'lumo_ev': float(lumo) * HA_EV if lumo else None,
        'occupations_kind': occ_kind, 'smearing': smearing, 'degauss_ev': degauss_ev,
        'xk': np.array(xk), 'wk_raw': wk, 'e_ev': e, 'f_qe': f,
        'labels': names, 'species': [element_of(n) for n in names], 'positions_A': pos, 'cell_A': cell,
        'etot_ry': float(etot) * 2.0 if etot else None, 'settings': settings,
    }


def _f(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def schema_settings(root):
    """Run settings that a comparison must find identical (common gauge) and the C6 start: functional, hybrid flags,
    cutoffs (Ry), k mesh, smearing, nspin, pseudopotential files, starting magnetisations, SCF convergence."""
    inp = root.find('input')
    s = {'source': 'data-file-schema.xml'}
    if inp is not None:
        s['functional'] = (inp.findtext('dft/functional') or '').strip()
        hyb = inp.find('dft/hybrid')
        if hyb is None:
            s['hybrid'] = None
        else:
            s['hybrid'] = {c.tag: ((c.text or '').strip() if not c.attrib else dict(c.attrib, text=(c.text or '').strip()))
                           for c in hyb}
            q = hyb.find('qpoint_grid')
            s['q_mesh'] = None if q is None else [int(q.get(a, '0')) for a in ('nqx1', 'nqx2', 'nqx3')]
            ef = _f(hyb.findtext('ecutfock'))
            s['ecutfock_Ry'] = None if ef is None else round(2 * ef, 8)
        s['lsda'] = (inp.findtext('spin/lsda') or 'false').strip() == 'true'
        sm = inp.find('bands/smearing')
        s['smearing'] = None if sm is None else (sm.text or '').strip()
        s['degauss_Ry'] = None if sm is None else round(2 * float(sm.get('degauss', '0')), 10)
        s['occupations'] = (inp.findtext('bands/occupations') or '').strip()
        s['tot_magnetization'] = _f(inp.findtext('bands/tot_magnetization'))
        s['ecutwfc_Ry'] = None if _f(inp.findtext('basis/ecutwfc')) is None else round(2 * _f(inp.findtext('basis/ecutwfc')), 8)
        s['ecutrho_Ry'] = None if _f(inp.findtext('basis/ecutrho')) is None else round(2 * _f(inp.findtext('basis/ecutrho')), 8)
        mp = inp.find('k_points_IBZ/monkhorst_pack')
        s['k_mesh'] = None if mp is None else [int(mp.get(a, '0')) for a in ('nk1', 'nk2', 'nk3', 'k1', 'k2', 'k3')]
        sp = []
        for e in inp.findall('atomic_species/species'):
            sp.append({'name': e.get('name'), 'pseudo_file': (e.findtext('pseudo_file') or '').strip(),
                       'starting_magnetization': _f(e.findtext('starting_magnetization')) or 0.0})
        s['species'] = sp
    conv = root.findtext('output/convergence_info/scf_conv/convergence_achieved')
    s['scf_converged'] = None if conv is None else conv.strip() == 'true'
    s['n_scf_steps'] = _f(root.findtext('output/convergence_info/scf_conv/n_scf_steps'))
    for key in ('paw', 'uspp'):
        v = root.findtext(f'output/algorithmic_info/{key}')
        s[key] = None if v is None else v.strip() == 'true'
    pd = root.find('output/atomic_species')
    s['pseudo_dir'] = None if pd is None else pd.get('pseudo_dir')
    s['pseudo_md5'] = {e.get('name'): e.findtext('pseudo_file') for e in (pd.findall('species') if pd is not None else [])}
    return s


def pw_in_settings(path):
    """The same settings from a pw.x input (table source); SCF convergence must come from the pw.x output."""
    with open_text(path) as fh:
        text = fh.read()
    clean = '\n'.join(_clean_lines(text))
    s = {'source': os.path.basename(str(path))}
    num = lambda k: _f((_namelist_value(text, k) or '').lower().replace('d', 'e') or None)
    s['ecutwfc_Ry'], s['ecutrho_Ry'] = num('ecutwfc'), num('ecutrho')
    s['degauss_Ry'] = num('degauss')
    s['smearing'] = _namelist_value(text, 'smearing')
    s['occupations'] = _namelist_value(text, 'occupations')
    s['lsda'] = (_namelist_value(text, 'nspin') or '1').strip() == '2'
    s['functional'] = (_namelist_value(text, 'input_dft') or '').strip()
    s['hybrid'] = None
    m = re.search(r'^\s*K_POINTS\s*[({]?\s*automatic\s*[)}]?\s*\n\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', clean,
                  re.I | re.M)
    s['k_mesh'] = [int(x) for x in m.groups()] if m else None
    sp = []
    lines = clean.splitlines()
    heads = [i for i, l in enumerate(lines) if l.strip().upper().startswith('ATOMIC_SPECIES')]
    if heads:
        for l in lines[heads[-1] + 1:]:
            p = l.split()
            if len(p) < 3 or not p[2].lower().endswith('.upf'):
                break
            mag = _namelist_value(text, 'starting_magnetization', str(len(sp) + 1))
            sp.append({'name': p[0], 'pseudo_file': p[2],
                       'starting_magnetization': float(mag.lower().replace('d', 'e')) if mag else 0.0})
    s['species'] = sp
    s['scf_converged'] = None
    return s


# ---------------------------------------------------------------- projwfc state map
_RE_MAP = re.compile(r'state #\s*(\d+):\s*atom\s+(\d+)\s*\(\s*(\S+?)\s*\)\s*,\s*wfc\s+(\d+)\s*\(l=\s*(\d+)\s+m=\s*(-?\d+)\)')


def read_state_map(path):
    """[(atom0, species_label, wfc, l, m)] in state order, from projwfc_map_final.dat or a projwfc.x output."""
    rows = {}
    table = os.path.basename(str(path)).replace('.gz', '').endswith('.dat')
    with open_text(path) as fh:
        for line in fh:
            if table:                     # projwfc_map_final.dat: state atom species wfc l m
                if line.startswith('#') or not line.strip():
                    continue
                p = line.split()
                if len(p) != 6:
                    raise ValueError(f'{path}: bad map line {line.strip()!r}')
                rows[int(p[0])] = (int(p[1]) - 1, p[2], int(p[3]), int(p[4]), int(p[5]))
                continue
            m = _RE_MAP.search(line)
            if m:
                i, a, s, w, l, mm = m.groups()
                rows[int(i)] = (int(a) - 1, s, int(w), int(l), int(mm))
            elif rows and line.startswith(' k = '):
                break                     # projwfc.x output: the map precedes the first k block
    if not rows:
        raise ValueError(f'{path}: no projwfc state map found')
    idx = sorted(rows)
    if idx != list(range(1, len(idx) + 1)):
        raise ValueError(f'{path}: state indices are not 1..{len(idx)}')
    return [rows[i] for i in idx]


def map_matrices(state_map, species):
    """(atom index per orbital, W-5d mask per orbital) after checking the map against the structure species."""
    nat = len(species)
    atom = np.array([r[0] for r in state_map])
    if atom.min() < 0 or atom.max() >= nat:
        raise ValueError('state map refers to atoms outside the structure')
    bad = [i for i, r in enumerate(state_map) if element_of(r[1]) != species[r[0]]]
    if bad:
        raise ValueError(f'state map species disagree with the structure at {len(bad)} orbitals (first {bad[0] + 1})')
    if set(atom) != set(range(nat)):
        raise ValueError(f'{nat - len(set(atom))} atoms carry no projection orbital')
    w5d = np.array([species[r[0]] == 'W' and r[3] == 2 for r in state_map])
    return atom, w5d


# ---------------------------------------------------------------- atomic_proj.xml
def _parse_complex(text, nbnd):
    v = np.array(text.split(), dtype=float)
    if v.size != 2 * nbnd:
        raise ValueError(f'ATOMIC_WFC with {v.size} numbers, expected {2 * nbnd}')
    return v[0::2] ** 2 + v[1::2] ** 2


def read_atomic_proj(path, atom_of, is_w5d, nat):
    """Stream atomic_proj.xml. Returns per spin channel and k (order of appearance within the channel):
    atom weights [nspin, nks, nbnd, nat], raw W-5d weight, completeness, eigenvalues (eV), k weights, header."""
    nwfc = len(atom_of)
    M = np.zeros((nwfc, nat))
    M[np.arange(nwfc), atom_of] = 1.0
    hdr, blocks = {}, []
    cur = None
    with open_binary(path) as fh:
        for ev, el in ET.iterparse(fh, events=('start', 'end')):
            tag = el.tag
            if ev == 'start':
                if tag == 'HEADER':
                    hdr = dict(el.attrib)
                elif tag == 'PROJS':
                    cur['rows'] = np.zeros((nwfc, int(hdr['NUMBER_OF_BANDS'])))
                    cur['seen'] = np.zeros(nwfc, dtype=bool)
                continue
            if tag == 'K-POINT':
                cur = {'weight': float(el.get('Weight', el.get('weight', 'nan'))),
                       'xk': [float(x) for x in el.text.split()], 'spin': None}
            elif tag == 'E':
                cur['e'] = _floats(el.text)
                el.clear()
            elif tag == 'ATOMIC_WFC':
                i = int(el.get('index')) - 1
                if not 0 <= i < nwfc:
                    raise ValueError(f'{path}: ATOMIC_WFC index {i + 1} outside the state map ({nwfc})')
                sp = el.get('spin')
                if sp is not None:
                    sp = int(sp)
                    if cur['spin'] is None:
                        cur['spin'] = sp
                    elif cur['spin'] != sp:
                        raise ValueError(f'{path}: mixed spin attributes inside one k block')
                cur['rows'][i] = _parse_complex(el.text, cur['rows'].shape[1])
                cur['seen'][i] = True
                el.clear()
            elif tag == 'PROJS':
                if not cur['seen'].all():
                    raise ValueError(f'{path}: k block {len(blocks) + 1} misses {int((~cur["seen"]).sum())} orbitals')
                sq = cur.pop('rows')
                cur.pop('seen')
                cur['atom_w'] = sq.T @ M                     # [nbnd, nat]
                cur['w5d'] = sq[is_w5d].sum(axis=0)          # [nbnd]
                cur['compl'] = sq.sum(axis=0)
                blocks.append(cur)
                el.clear()
    if not hdr:
        raise ValueError(f'{path}: no HEADER')
    nbnd = int(hdr['NUMBER_OF_BANDS'])
    nspin = int(hdr.get('NUMBER_OF_SPIN_COMPONENTS', '1'))
    if hdr.get('NON-COLINEAR_CALCULATION', 'F').strip().upper() in ('T', 'TRUE', '.TRUE.'):
        raise ValueError(f'{path}: noncollinear projections are not supported')
    if int(hdr['NUMBER_OF_ATOMIC_WFC']) != nwfc:
        raise ValueError(f'{path}: {hdr["NUMBER_OF_ATOMIC_WFC"]} atomic wavefunctions, state map has {nwfc}')
    units = hdr.get('UNITS_FOR_ENERGY', 'Rydberg').lower()
    escale = RY_EV if units.startswith('ry') else HA_EV
    if nspin not in (1, 2):
        raise ValueError(f'{path}: NUMBER_OF_SPIN_COMPONENTS {nspin} not supported')
    # spin channel of each block: the 'spin' attribute when present, else QE order (all up k, then all down k)
    nb = len(blocks)
    if nspin == 2 and nb % 2:
        raise ValueError(f'{path}: odd number of k blocks ({nb}) in a spin-polarised file')
    for j, b in enumerate(blocks):
        if b['spin'] is None:
            b['spin'] = 1 if (nspin == 1 or j < nb // 2) else 2
        if not 1 <= b['spin'] <= nspin:
            raise ValueError(f'{path}: spin {b["spin"]} in a file with {nspin} spin component(s)')
    chan = [[b for b in blocks if b['spin'] == s + 1] for s in range(nspin)]
    nks = len(chan[0])
    if any(len(c) != nks for c in chan):
        raise ValueError(f'{path}: spin channels hold {[len(c) for c in chan]} k blocks')
    nk_hdr = int(hdr['NUMBER_OF_K-POINTS'])
    if nk_hdr not in (nks, nks * nspin):
        raise ValueError(f'{path}: header says {nk_hdr} k-points, file holds {nks} per spin channel')
    stack = lambda key: np.array([[b[key] for b in c] for c in chan])
    e = stack('e') * escale
    if e.shape[-1] != nbnd:
        raise ValueError(f'{path}: <E> holds {e.shape[-1]} values, header says {nbnd} bands')
    ef = hdr.get('FERMI_ENERGY')
    return {
        'path': path, 'header': hdr, 'nspin': nspin, 'nks': nks, 'nbnd': nbnd,
        'atom_w': stack('atom_w'), 'w5d': stack('w5d'), 'compl': stack('compl'), 'e_ev': e,
        'wk': np.array([[b['weight'] for b in c] for c in chan]),
        'xk': np.array([[b['xk'] for b in c] for c in chan]),
        'ef_ev': float(ef) * escale if ef else None,
    }


# ---------------------------------------------------------------- D-24 AFS tables
def _header_value(lines, key, cast=str):
    """First 'key value' pair in the header lines whose value converts with cast (prose lines are skipped)."""
    for l in lines:
        for m in re.finditer(rf'(?<![\w-]){re.escape(key)}\s+(\S+)', l):
            try:
                return cast(m.group(1))
            except ValueError:
                continue
    return None


def read_tables(directory, job='final'):
    """occ_kw_<job>.dat + proj_atoms_<job>.dat (D-24 v2). lsda tables are reconstructed (see the docstring of
    _lsda_from_tables); the result carries proj_kind 'table' (atom weights rounded to 1e-6)."""
    occ_p = first_existing(directory, [f'occ_kw_{job}.dat'])
    pa_p = first_existing(directory, [f'proj_atoms_{job}.dat'])
    if not occ_p or not pa_p:
        raise FileNotFoundError(f'{directory}: occ_kw_{job}.dat or proj_atoms_{job}.dat missing')
    with open_text(occ_p) as fh:
        occ_lines = fh.read().splitlines()
    oh = [l for l in occ_lines if l.startswith('#')]
    occ = np.array([l.split() for l in occ_lines if l.strip() and not l.startswith('#')], dtype=float)
    nelec = _header_value(oh, 'nelec', float)
    nbnd = _header_value(oh, 'nbnd', int)
    nks = _header_value(oh, 'nks', int)
    lsda = (_header_value(oh, 'lsda') or 'False').lower() == 'true'
    ef = _header_value(oh, 'fermi_energy_eV', float)
    smearing = _header_value(oh, 'smearing')
    deg_ry = _header_value(oh, 'degauss_Ry', float)
    with open_text(pa_p) as fh:
        pa_lines = fh.read().splitlines()
    ph = [l for l in pa_lines if l.startswith('#')]
    cols = next(l for l in ph if l.startswith('# columns:')).split(':', 1)[1].split()
    nat = _header_value(ph, 'nat', int)
    w_cols = [c for c in cols if c.startswith('d_W')]   # header: 'ik ibnd e_eV f_nk w_k completeness PR_n w_1 ... w_N d_W<a>'
    tab =np.array([l.split() for l in pa_lines if l.strip() and not l.startswith('#')], dtype=float)
    if tab.shape[1] != 7 + nat + len(w_cols):
        raise ValueError(f'{pa_p}: {tab.shape[1]} columns, expected 7 + nat {nat} + {len(w_cols)} W columns')
    nspin = 2 if lsda else 1
    w_atoms = [int(c[3:]) - 1 for c in w_cols]
    species_runs = next((l for l in ph if l.startswith('# atoms (pw.x order')), '')
    species = []
    for sp_, a_, b_ in re.findall(r'(\w+) (\d+)-(\d+)', species_runs.split(':', 1)[-1]):
        species += [element_of(sp_)] * (int(b_) - int(a_) + 1)
    w_true = [i for i, e in enumerate(species) if e == 'W']
    if sorted(w_atoms) != w_true:
        raise ValueError(f'tables: W-5d columns missing or wrong (d_W columns for atoms {[a + 1 for a in w_atoms]}, W '
                         f'atoms {[a + 1 for a in w_true]}): the W-5d weight cannot be read')
    ik_t, n_t = tab[:, 0].astype(int), tab[:, 1].astype(int)
    if lsda:
        # occ rows: ik 1..nks, ibnd 1..2 nbnd (up then down); proj rows: ik 1..2 nks (up k, then down k), ibnd 1..nbnd
        if occ.shape[0] != nks * 2 * nbnd or tab.shape[0] != 2 * nks * nbnd:
            raise ValueError('lsda tables: unexpected row counts')
        spin_o, k_o, b_o = (occ[:, 1] > nbnd).astype(int), occ[:, 0].astype(int) - 1, (occ[:, 1].astype(int) - 1) % nbnd
        spin_t, k_t, b_t = (ik_t > nks).astype(int), (ik_t - 1) % nks, n_t - 1
    else:
        if occ.shape[0] != nks * nbnd or tab.shape[0] != nks * nbnd:
            raise ValueError(f'tables: {occ.shape[0]} occ rows, {tab.shape[0]} projection rows, expected {nks * nbnd}')
        spin_o, k_o, b_o = np.zeros(len(occ), int), occ[:, 0].astype(int) - 1, occ[:, 1].astype(int) - 1
        spin_t, k_t, b_t = np.zeros(len(tab), int), ik_t - 1, n_t - 1
    e = np.full((nspin, nks, nbnd), np.nan)
    f = np.full((nspin, nks, nbnd), np.nan)
    wk = np.full((nspin, nks), np.nan)
    e[spin_o, k_o, b_o] = occ[:, 2]
    f[spin_o, k_o, b_o] = occ[:, 3]
    wk[spin_o, k_o] = occ[:, 4]
    atom_w = np.full((nspin, nks, nbnd, nat), np.nan)
    atom_w[spin_t, k_t, b_t] = tab[:, 7:7 + nat] * 1e-6
    compl = np.full((nspin, nks, nbnd), np.nan)
    compl[spin_t, k_t, b_t] = tab[:, 5]
    w5d = np.zeros((nspin, nks, nbnd))
    if w_cols:
        w5d[spin_t, k_t, b_t] = tab[:, 7 + nat:].sum(axis=1) * 1e-6
    for name, arr in (('eigenvalues', e), ('occupations', f), ('atom weights', atom_w), ('completeness', compl)):
        if np.isnan(arr).any():
            raise ValueError(f'tables: {name} incomplete after the (spin, k, band) reconstruction')
    # spin-up rows of the projection table carry e: they must equal the occupation table
    eu = tab[spin_t == 0, 2]
    de = np.nanmax(np.abs(eu - e[0, k_t[spin_t == 0], b_t[spin_t == 0]])) if eu.size else 0.0
    if de > 2e-5:
        raise ValueError(f'tables: projection and occupation eigenvalues differ by {de:.2e} eV')
    species_runs = next((l for l in ph if l.startswith('# atoms (pw.x order')), '')
    species = []
    for s, a, b in re.findall(r'(\w+) (\d+)-(\d+)', species_runs.split(':', 1)[-1]):
        species += [element_of(s)] * (int(b) - int(a) + 1)
    if len(species) != nat:
        raise ValueError(f'{pa_p}: species runs give {len(species)} atoms, nat {nat}')
    return {
        'paths': [occ_p, pa_p], 'nspin': nspin, 'nks': nks, 'nbnd': nbnd, 'nelec': nelec, 'ef_ev': [ef] * nspin,
        'smearing': smearing, 'degauss_ev': deg_ry * RY_EV if deg_ry is not None else 0.0,
        'e_ev': e, 'f_qe': f, 'wk_norm': wk, 'atom_w': atom_w, 'w5d': w5d, 'compl': compl, 'species': species,
        'W_atoms': w_atoms, 'lsda_reconstructed': lsda,
    }


# ---------------------------------------------------------------- projwfc.x text output (approximate)
_RE_E = re.compile(r'==== e\(\s*(\d+)\) =\s+(-?[\d.]+) eV')
_RE_C = re.compile(r'([\d.]+)\*\[#\s*(\d+)\]')
_RE_PSI = re.compile(r'\|psi\|\^2 = ([\d.]+)')


def read_projwfc_text(path, atom_of, is_w5d, nat):
    """Per-state components printed by projwfc.x (|c|^2 >= 0.001, 3 decimals) and |psi|^2. nspin = 1 only.
    Atom weights are TRUNCATED: PR_n from them is approximate. Returns [1, nks, nbnd, ...] arrays."""
    ks, cur, state = [], None, None
    with open_text(path) as fh:
        for line in fh:
            if line.startswith(' k = '):
                cur = {}
                ks.append(cur)
                continue
            if cur is None:
                if 'SPIN' in line and ('UP' in line or 'DOWN' in line):
                    raise ValueError(f'{path}: spin-polarised projwfc text is not supported')
                continue
            m = _RE_E.search(line)
            if m:
                state = [float(m.group(2)), {}, None]
                cur[int(m.group(1))] = state
                continue
            if state is not None:
                for c, s in _RE_C.findall(line):
                    state[1][int(s) - 1] = state[1].get(int(s) - 1, 0.0) + float(c)
                m = _RE_PSI.search(line)
                if m:
                    state[2] = float(m.group(1))
                    state = None
    if not ks:
        raise ValueError(f'{path}: no k blocks')
    nbnd = max(max(k) for k in ks)
    nks = len(ks)
    e = np.full((1, nks, nbnd), np.nan)
    atom_w = np.zeros((1, nks, nbnd, nat))
    w5d = np.zeros((1, nks, nbnd))
    compl = np.full((1, nks, nbnd), np.nan)
    for ik, k in enumerate(ks):
        for n, (en, comp, psi) in k.items():
            e[0, ik, n - 1] = en
            compl[0, ik, n - 1] = psi if psi is not None else np.nan
            for i, c in comp.items():
                atom_w[0, ik, n - 1, atom_of[i]] += c
                if is_w5d[i]:
                    w5d[0, ik, n - 1] += c
    if np.isnan(e).any():
        raise ValueError(f'{path}: missing states in some k blocks')
    return {'path': path, 'nks': nks, 'nbnd': nbnd, 'e_ev': e, 'atom_w': atom_w, 'w5d': w5d, 'compl': compl}


# ---------------------------------------------------------------- pw.x input and output
_QUOTED = re.compile(r"'(?:[^']|'')*'|\"(?:[^\"]|\"\")*\"")


def _clean_lines(text):
    """Input lines without comments: '!' to end of line outside quotes, and lines starting with '#'."""
    out = []
    for line in text.splitlines():
        line = _strip_comment(line)
        out.append('' if line.lstrip().startswith('#') else line)
    return out


def namelist_assignments(text):
    """[(namelist, name, index or None, value)] of every assignment inside the &name ... / namelists, with comments
    stripped and quoted character values masked first, so that text inside quotes or comments can never be read as an
    assignment or as a namelist delimiter. Names are lower case; quoted values are returned without their quotes."""
    strings = []

    def mask(m):
        strings.append(m.group(0))
        return f'\x00{len(strings) - 1}\x00'
    masked = _QUOTED.sub(mask, '\n'.join(_clean_lines(text)))
    out = []
    for blk in re.finditer(r'&(\w+)([^/]*)/', masked):
        for m in re.finditer(r'(?<![\w%\x00])([A-Za-z_]\w*)\s*(\(([^)]*)\))?\s*=\s*([^,\s]+)', blk.group(2)):
            v = m.group(4)
            q = re.fullmatch(r'\x00(\d+)\x00', v)
            if q:
                v = strings[int(q.group(1))][1:-1]
            elif '\x00' in v:
                v = None                                   # value glued to a quoted string: not a plain token
            idx = None if m.group(2) is None else re.sub(r'\s+', '', m.group(3))
            out.append((blk.group(1).lower(), m.group(1).lower(), idx, v))
    return out


def _namelist_value(text, key, index=None):
    """The single assignment of key (key(index)) in the namelists; None if absent; repeated assignments refused."""
    hits = [v for nl, n, idx, v in namelist_assignments(text) if n == key.lower() and idx == index]
    if len(hits) > 1:
        raise ValueError(f'namelist variable {key}{"" if index is None else f"({index})"} assigned {len(hits)} times')
    return None if not hits or hits[0] is None else hits[0].strip()


def _fortran_float(s):
    return float(s.lower().replace('d', 'e'))


def read_pw_in(path):
    """Geometry and run settings of a pw.x input (ibrav = 0; CELL_PARAMETERS angstrom/bohr/alat;
    ATOMIC_POSITIONS crystal/angstrom/bohr/alat)."""
    with open_text(path) as fh:
        text = fh.read()
    lines = _clean_lines(text)
    ibrav = _namelist_value(text, 'ibrav')
    if ibrav is not None and int(ibrav) != 0:
        raise ValueError(f'{path}: ibrav {ibrav} not supported (ibrav = 0 only)')
    nat = int(_namelist_value(text, 'nat'))
    alat = None
    cd = _namelist_value(text, 'celldm', '1')
    if cd:
        alat = _fortran_float(cd) * BOHR_A
    a_ = _namelist_value(text, 'A')
    if a_ and alat is None:
        alat = _fortran_float(a_)

    def card(key):
        heads = [i for i, l in enumerate(lines) if l.strip().upper().startswith(key)]
        if not heads:
            raise ValueError(f'{path}: no {key}')
        i = heads[-1]
        unit = re.sub(r'[(){}]', ' ', lines[i]).split()[1:2]
        return i, (unit[0].lower() if unit else '')

    i, cu = card('CELL_PARAMETERS')
    cell = np.array([[_fortran_float(x) for x in lines[i + j].split()[:3]] for j in (1, 2, 3)])
    if cu == 'bohr':
        cell = cell * BOHR_A
    elif cu in ('alat', ''):
        cell = cell * alat
    i, pu = card('ATOMIC_POSITIONS')
    if pu not in ('', 'alat', 'bohr', 'angstrom', 'crystal'):
        raise ValueError(f'{path}: ATOMIC_POSITIONS unit {pu!r} not supported (crystal_sg / Wyckoff positions)')
    pu = pu or 'alat'                                 # QE default (deprecated): alat units
    if pu == 'alat' and alat is None:
        raise ValueError(f'{path}: ATOMIC_POSITIONS in alat units without celldm(1) / A')
    labels, pos = [], []
    rows = [l for l in lines[i + 1:] if l.strip()][:nat]
    if len(rows) != nat:
        raise ValueError(f'{path}: ATOMIC_POSITIONS has {len(rows)} rows, nat {nat}')
    for l in rows:
        p = l.split()
        labels.append(p[0])
        pos.append([_fortran_float(x) for x in p[1:4]])
    pos = np.array(pos)
    if pu == 'crystal':
        pos = pos @ cell
    elif pu == 'bohr':
        pos = pos * BOHR_A
    elif pu == 'alat':
        pos = pos * alat
    occ = (_namelist_value(text, 'occupations') or 'fixed').lower()
    sm = _namelist_value(text, 'smearing')
    deg = _namelist_value(text, 'degauss')
    nspin = int(_namelist_value(text, 'nspin') or 1)
    return {'path': path, 'labels': labels, 'species': [element_of(s) for s in labels], 'positions_A': pos,
            'cell_A': cell, 'occupations': occ, 'smearing': sm if occ == 'smearing' else None,
            'degauss_ev': _fortran_float(deg) * RY_EV if deg and occ == 'smearing' else 0.0, 'nspin': nspin}


_NUM = re.compile(r'-?\d+\.\d+')
_SMEAR_TXT = {'gaussian': 'gaussian', 'methfessel-paxton': 'mp', 'marzari-vanderbilt': 'mv', 'fermi-dirac': 'fd'}


def read_pw_out(path):
    """Eigenvalues (last printout), k-weights, QE occupations (verbosity high), Fermi level, smearing, convergence."""
    with open_text(path) as fh:
        t = fh.read()
    nks_tot = int(re.search(r'number of k points=\s*(\d+)', t).group(1))
    m = re.search(r'number of k points=\s*\d+\s+(.*?)smearing, width \(Ry\)=\s*([\d.eE+-]+)', t)
    smearing, deg = None, 0.0
    if m:
        smearing = _SMEAR_TXT.get(m.group(1).strip().lower(), m.group(1).strip().lower())
        deg = float(m.group(2)) * RY_EV
    head = t.split('number of k points=', 1)[1]
    wk = np.array([float(x) for x in re.findall(r'k\(\s*\d+\) = \([-\d. ]+\), wk =\s+([\d.]+)', head)[:nks_tot]])
    nelec = float(re.search(r'number of electrons\s+=\s+([\d.]+)', t).group(1))
    nbnd = int(re.search(r'number of Kohn-Sham states=\s*(\d+)', t).group(1))
    lsda = '------ SPIN UP ----' in t
    nspin = 2 if lsda else 1
    marker = 'End of self-consistent calculation' if 'End of self-consistent calculation' in t \
        else 'End of band structure calculation'
    last = t.rsplit(marker, 1)[-1]
    blocks = re.split(r'\n\s*k =\s*', last)[1:]
    e, f = [], []
    for b in blocks[:nks_tot]:
        body = b.split('bands (ev):', 1)[1]
        parts = re.split(r'occupation numbers', body, maxsplit=1)
        ev_txt = parts[0]
        ev_txt = re.split(r'\n\s*\n\s*(?:highest|the Fermi|the spin|Writing|total energy|------)', ev_txt)[0]
        ev = [float(x) for x in _NUM.findall(ev_txt.replace('-', ' -'))][:nbnd]
        e.append(ev)
        if len(parts) > 1:
            oc = [float(x) for x in _NUM.findall(parts[1])][:nbnd]
            f.append(oc)
    if len(e) != nks_tot or any(len(x) != nbnd for x in e):
        raise ValueError(f'{path}: eigenvalue blocks incomplete ({len(e)} of {nks_tot})')
    nks = nks_tot // nspin
    e = np.array(e).reshape(nspin, nks, nbnd)
    f_qe = np.array(f).reshape(nspin, nks, nbnd) if len(f) == nks_tot and all(len(x) == nbnd for x in f) else None
    wk = wk.reshape(nspin, nks)
    efs = re.findall(r'the Fermi energy is\s+(-?[\d.]+)', t)
    ef2 = re.findall(r'the spin up/dw Fermi energies are\s+(-?[\d.]+)\s+(-?[\d.]+)', t)
    ef = [float(efs[-1])] * nspin if efs else ([float(x) for x in ef2[-1]] if ef2 else None)
    hl = re.findall(r'highest occupied, lowest unoccupied level \(ev\):\s+(-?[\d.]+)\s+(-?[\d.]+)', t)
    etot = re.findall(r'^!\s+total energy\s+=\s+(-?[\d.]+) Ry', t, re.M)
    return {'path': path, 'nspin': nspin, 'nks': nks, 'nbnd': nbnd, 'nelec': nelec, 'wk_raw': wk, 'e_ev': e,
            'f_qe': f_qe, 'ef_ev': ef, 'smearing': smearing, 'degauss_ev': deg,
            'homo_lumo_ev': (float(hl[-1][0]), float(hl[-1][1])) if hl else None,
            'converged': 'convergence has been achieved' in t and 'convergence NOT achieved' not in t,
            'etot_ry': float(etot[-1]) if etot else None}


# ---------------------------------------------------------------- average.x
def _strip_comment(line):
    """Fortran namelist line without its '!' comment (quotes respected)."""
    q = None
    for i, ch in enumerate(line):
        if q:
            if ch == q:
                q = None
        elif ch in ('"', "'"):
            q = ch
        elif ch == '!':
            return line[:i]
    return line


def pp_plot_num(text):
    """plot_num of the single active &INPUTPP namelist of a pp.x input; None if the namelist is missing or repeated,
    or plot_num is absent, repeated, indexed or not an integer literal (ambiguous inputs are never assumed)."""
    masked = _QUOTED.sub("''", '\n'.join(_clean_lines(text)))
    if len(re.findall(r'&inputpp\b', masked, re.I)) != 1:
        return None
    hits = [(idx, v) for nl, n, idx, v in namelist_assignments(text) if nl == 'inputpp' and n == 'plot_num']
    if len(hits) != 1 or hits[0][0] is not None or hits[0][1] is None:
        return None
    try:
        return int(hits[0][1])
    except ValueError:
        return None


def read_avg(path, avg_in=None, pp_in=None):
    """z (bohr), planar average (Ry), macroscopic average (Ry); window (bohr) from the average.x input and plot_num
    from the pp.x input, if given."""
    plot_num = None
    if pp_in and os.path.isfile(pp_in):
        with open_text(pp_in) as fh:
            plot_num = pp_plot_num(fh.read())
    d = np.loadtxt(path)
    window = None
    if avg_in and os.path.isfile(avg_in):
        with open_text(avg_in) as fh:
            vals = [l.strip() for l in fh if l.strip()]
        try:
            window = float(vals[-1].replace('d', 'e'))
        except ValueError:
            window = None
    return {'path': path, 'z_bohr': d[:, 0], 'planar_ry': d[:, 1], 'macro_ry': d[:, 2] if d.shape[1] > 2 else None,
            'window_bohr': window, 'plot_num': plot_num}
