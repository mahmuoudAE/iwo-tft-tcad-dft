"""Independent readers for the Quantum ESPRESSO outputs of the IWO DFT study (analysis_2026-10-13_full).

Written from scratch for this re-derivation: nothing is imported from collect_results.py, analyze_slabs.py,
dft_to_tcad_extract.py or the other earlier analysis scripts, so a bug there cannot propagate here.
Every reader returns its value together with the provenance "relative/path:line" (path relative to qe_workflow/),
so that the report can cite each number at file:line.

Constants: 1 Ry = 13.605693122994 eV, 1 bohr = 0.529177210903 A, hbar^2/(2 m0) = 3.80998212 eV A^2 (CODATA 2018, as QE 7.x).
"""
import json
import math
import re
from functools import lru_cache
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
QE = HERE.parent                                   # qe_workflow/
RES = QE / 'cern_htcondor' / 'results'
BULK = QE / 'bulk_In2O3_protocol'
PSEUDO = QE / 'pseudo'
OUT = HERE / 'out'
FIGS = HERE / 'figures'

RY = 13.605693122994
BOHR = 0.529177210903
H2M = 3.80998212                   # hbar^2 / (2 m0), eV A^2
KB = 8.617333262e-5                # eV/K
NUM = re.compile(r'-?\d+\.\d+(?:[eEdD][-+]?\d+)?')


# ---------------------------------------------------------------- provenance
def rel(p):
    """Path relative to qe_workflow/; '../x' for the rest of IWO_PHYSICS_CONSTRAINED_MODEL_V1; 'private:x' for the
    private research repository."""
    p = Path(p).resolve()
    for base, pre in ((QE, ''), (QE.parent, '../'), (QE.parents[1] / 'iwo-tft-research-private', 'private:')):
        try:
            return pre + p.relative_to(base).as_posix()
        except ValueError:
            continue
    return p.as_posix()


def src(p, line):
    return f'{rel(p)}:{line}'


class V(dict):
    """A value with provenance and a label: V(value, src, label, note)."""
    def __init__(self, value, source, label='COMPUTED', note=None, unit=None):
        super().__init__(value=value, src=source, label=label)
        if note:
            self['note'] = note
        if unit:
            self['unit'] = unit


@lru_cache(maxsize=None)
def lines(p):
    return Path(p).read_text(encoding='utf-8', errors='replace').splitlines()


def grep(p, rx, flags=0):
    """All matches as (match, 1-based line number)."""
    r = re.compile(rx, flags)
    out = []
    for i, l in enumerate(lines(str(p)), 1):
        m = r.search(l)
        if m:
            out.append((m, i))
    return out


def last(p, rx):
    g = grep(p, rx)
    if not g:
        raise LookupError(f'{rx!r} not found in {rel(p)}')
    return g[-1]


def first(p, rx):
    g = grep(p, rx)
    if not g:
        raise LookupError(f'{rx!r} not found in {rel(p)}')
    return g[0]


def nums(s):
    """Numbers of a QE line; QE glues negative numbers ('-1.2-3.4'), so a space is put before each minus."""
    return [float(x.replace('d', 'e').replace('D', 'e')) for x in NUM.findall(re.sub(r'(?<=\d)-', ' -', s))]


# ---------------------------------------------------------------- pw.x scalar read-outs
def homo_lumo(p):
    m, i = last(p, r'highest occupied, lowest unoccupied level \(ev\):\s+(-?[\d.]+)\s+(-?[\d.]+)')
    return float(m.group(1)), float(m.group(2)), src(p, i)


def etot(p, bang=True):
    m, i = last(p, r'^!\s+total energy\s+=\s+(-?[\d.]+) Ry' if bang else r'total energy\s+=\s+(-?[\d.]+) Ry')
    return float(m.group(1)), src(p, i)


def fermi(p):
    m, i = last(p, r'the Fermi energy is\s+(-?[\d.]+) ev')
    return float(m.group(1)), src(p, i)


def nelec(p):
    m, i = first(p, r'number of electrons\s+=\s+([\d.]+)')
    return float(m.group(1)), src(p, i)


def nks(p):
    m, i = first(p, r'number of k points=\s+(\d+)')
    return int(m.group(1)), src(p, i)


def symops(p):
    m, i = first(p, r'(\d+) Sym\. Ops\.')
    return int(m.group(1)), src(p, i)


def pressure(p):
    m, i = last(p, r'P=\s+(-?[\d.]+)')
    return float(m.group(1)), src(p, i)


def scf_iters(p):
    m, i = last(p, r'convergence has been achieved in\s+(\d+) iterations')
    return int(m.group(1)), src(p, i)


def job_done(p):
    return any('JOB DONE' in l for l in lines(str(p)))


def version(p):
    m, i = first(p, r'Program PWSCF (v\.[\d.]+)')
    return m.group(1), src(p, i)


def alat_A(p):
    m, i = first(p, r'lattice parameter \(alat\)\s+=\s+([\d.]+)\s+a\.u\.')
    return float(m.group(1)) * BOHR, src(p, i)


def lattice_alat(p):
    """a(1..3) printed by pw.x in units of alat (first occurrence)."""
    a = []
    for k in (1, 2, 3):
        m, i = first(p, rf'a\({k}\) = \(\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s*\)')
        a.append([float(m.group(j)) for j in (1, 2, 3)])
    return np.array(a)


# ---------------------------------------------------------------- input files (ibrav = 0, CELL_PARAMETERS angstrom)
def read_struct_in(p):
    """cell (A), symbols, fractional and Cartesian coordinates from a pw.x input or a 'final coordinates' block."""
    L = lines(str(p))
    ic = next(i for i, l in enumerate(L) if l.strip().upper().startswith('CELL_PARAMETERS'))
    assert 'angstrom' in L[ic].lower(), L[ic]
    cell = np.array([nums(L[ic + j])[:3] for j in (1, 2, 3)])
    ia = next(i for i, l in enumerate(L) if l.strip().upper().startswith('ATOMIC_POSITIONS'))
    assert 'crystal' in L[ia].lower(), L[ia]
    sym, frac = [], []
    for l in L[ia + 1:]:
        t = l.split()
        if len(t) < 4 or not re.match(r'^[A-Z][a-z]?\d*$', t[0]):
            break
        sym.append(re.sub(r'\d+$', '', t[0]))
        frac.append([float(x) for x in t[1:4]])
    frac = np.array(frac)
    return cell, sym, frac, frac @ cell, src(p, ia + 1)


def final_struct_out(p):
    """Last 'Begin final coordinates' block of a relax/vc-relax output (cell in angstrom if printed, else from input)."""
    L = lines(str(p))
    b = max(i for i, l in enumerate(L) if 'Begin final coordinates' in l)
    e = next(i for i in range(b, len(L)) if 'End final coordinates' in L[i])
    blk = L[b:e]
    cell = None
    for j, l in enumerate(blk):
        if l.strip().startswith('CELL_PARAMETERS'):
            assert 'angstrom' in l, l
            cell = np.array([nums(blk[j + k])[:3] for k in (1, 2, 3)])
    ia = next(j for j, l in enumerate(blk) if l.strip().startswith('ATOMIC_POSITIONS'))
    assert 'crystal' in blk[ia], blk[ia]
    sym, frac = [], []
    for l in blk[ia + 1:]:
        t = l.split()
        if len(t) < 4:
            break
        sym.append(re.sub(r'\d+$', '', t[0]))
        frac.append([float(x) for x in t[1:4]])
    return cell, sym, np.array(frac), src(p, b + 1)


def neighbours(cell, frac, i, species_sym, sym, rmax=2.7):
    """Distances from atom i to atoms of a species within rmax (A), all periodic images (-1..1)."""
    out = []
    shifts = np.array([[a, b, c] for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1)])
    for j, s in enumerate(sym):
        if s != species_sym or j == i:
            continue
        d = frac[j] - frac[i]
        d -= np.rint(d)
        for sh in shifts:
            r = np.linalg.norm((d + sh) @ cell)
            if r < rmax:
                out.append(r)
    return sorted(out)


# ---------------------------------------------------------------- eigenvalues
def eig_blocks(p, after=('End of band structure calculation', 'End of self-consistent calculation')):
    """Eigenvalue blocks printed after the LAST 'End of ...' marker: list of (k_cart [2pi/alat], eigenvalues, line)."""
    L = lines(str(p))
    start = max((i for i, l in enumerate(L) if any(a in l for a in after)), default=None)
    if start is None:
        raise LookupError(f'no eigenvalue section in {rel(p)}')
    blocks, mode, cur = [], 'skip', None
    for i in range(start, len(L)):
        l = L[i]
        if 'bands (ev)' in l and 'k =' in l:
            k = nums(l.split('(')[0].split('=')[1])[:3]
            cur = [np.array(k), [], i + 1]
            blocks.append(cur)
            mode = 'eig'
            continue
        if mode == 'eig':
            s = l.strip()
            if not s:
                continue
            if re.search(r'[a-zA-Z]', s):
                mode = 'skip'
                continue
            cur[1].extend(nums(s))
    return [(b[0], np.array(b[1]), src(p, b[2])) for b in blocks]


def occ_blocks(p):
    """'occupation numbers' blocks (verbosity = 'high') after the last 'End of self-consistent calculation', one per k."""
    L = lines(str(p))
    start = max(i for i, l in enumerate(L) if 'End of self-consistent calculation' in l)
    blocks, mode = [], 'skip'
    for i in range(start, len(L)):
        l = L[i]
        if 'occupation numbers' in l:
            blocks.append([[], i + 1])
            mode = 'occ'
            continue
        if mode == 'occ':
            s = l.strip()
            if not s:
                continue
            if re.search(r'[a-zA-Z]', s):
                mode = 'skip'
                continue
            blocks[-1][0].extend(nums(s))
    return [(np.array(b[0]), src(p, b[1])) for b in blocks]


def wgauss_mv(x):
    """QE wgauss for Marzari-Vanderbilt cold smearing (ngauss = -1); x = (E_F - e) / degauss."""
    xp = x - 1.0 / math.sqrt(2.0)
    return 0.5 * math.erf(xp) + 1.0 / math.sqrt(2.0 * math.pi) * math.exp(-min(200.0, xp * xp)) + 0.5


def kweights(p):
    """k-point weights of the SCF list (cart. coord.), sum = 2 for nspin = 1."""
    n, _ = nks(p)
    g = grep(p, r'k\(\s*\d+\) = \(\s*([-\d. ]+)\), wk =\s+([\d.]+)')
    return np.array([float(m.group(2)) for m, _ in g[:n]])


# ---------------------------------------------------------------- planar average (average.x output: z [bohr], V [Ry], Vmacro [Ry])
def avg_dat(d):
    f = next(Path(d).glob('*_avg.dat'))
    a = np.loadtxt(f)
    return a[:, 0], a[:, 1], a[:, 2], rel(f)


def macro(z, v, w):
    """Running mean over a window w (bohr), periodic in z."""
    dz = z[1] - z[0]
    n = max(1, int(round(w / dz)))
    ext = np.concatenate([v[-n:], v, v[:n]])
    return np.convolve(ext, np.ones(n) / n, mode='same')[n:-n]


# ---------------------------------------------------------------- projwfc
def projwfc(p):
    """states {n: (atom index 0-based, element, wfc number, l)}; kblocks: list of {band: (E, {state: w}, |psi|^2, line)}."""
    L = lines(str(p))
    states = {}
    rs = re.compile(r'state #\s*(\d+): atom\s+(\d+) \((\w+)\s*\)\s*, wfc\s+(\d+) \(l=(\d)')
    re_e = re.compile(r'==== e\(\s*(\d+)\) =\s*(-?[\d.]+) eV ====')
    re_c = re.compile(r'([\d.]+)\*\[#\s*(\d+)\]')
    kblocks, cur, band = [], None, None
    for i, l in enumerate(L, 1):
        m = rs.search(l)
        if m:
            states[int(m.group(1))] = (int(m.group(2)) - 1, m.group(3), int(m.group(4)), int(m.group(5)))
            continue
        if l.startswith(' k = '):
            cur = {}
            kblocks.append(cur)
            band = None
            continue
        if cur is None:
            continue
        m = re_e.search(l)
        if m:
            band = int(m.group(1))
            cur[band] = [float(m.group(2)), {}, None, i]
            continue
        if band is not None and '|psi|^2' in l:
            cur[band][2] = float(l.split('=')[1])
            band = None
            continue
        if band is not None:
            for c, s in re_c.findall(l):
                cur[band][1][int(s)] = cur[band][1].get(int(s), 0.0) + float(c)
        if 'Lowdin Charges' in l:
            break
    return states, kblocks


def proj_weights(states, comp, key):
    """Sum projection weights by a key function of the state tuple, e.g. key=lambda st: st[1]+'spdf'[st[3]]."""
    out = {}
    for s, w in comp.items():
        k = key(states[s])
        out[k] = out.get(k, 0.0) + w
    return out


def pdos_sum(d, select):
    """Sum of the ldos column of pdos files in d/pdos whose (atom, element, wfc label) passes select."""
    E, tot = None, None
    rx = re.compile(r'pdos_atm#(\d+)\((\w+)\)_wfc#(\d+)\((\w)\)$')
    files = []
    for f in sorted((Path(d) / 'pdos').iterdir()):
        m = rx.search(f.name)
        if not m or not select(int(m.group(1)), m.group(2), int(m.group(3)), m.group(4)):
            continue
        a = np.loadtxt(f, comments='#')
        E = a[:, 0] if E is None else E
        tot = a[:, 1] if tot is None else tot + a[:, 1]
        files.append(f.name)
    return E, tot, files


# ---------------------------------------------------------------- UPF local potential (G = 0 term of vltot)
def upf_alpha(upf):
    """QE's G = 0 term of the local pseudopotential, vloc0 = int_0^rcut r (r V_loc(r) + 2 Z) dr (Ry bohr^3, before 4 pi/Omega),
    with rcut = 10 bohr, msh odd and QE's simpson rule (upflib/simpsn.f90), exactly as PW/src/vloc_mod / vloc_of_g."""
    t = Path(upf).read_text()

    def arr(tag):
        m = re.search(rf'<{tag}(?:\s[^>]*)?>(.*?)</{tag}>', t, re.S)
        return np.array(m.group(1).split(), float)
    r, rab, vl = arr('PP_R'), arr('PP_RAB'), arr('PP_LOCAL')
    z = float(re.search(r'z_valence="\s*([-\d.eE+]+)"', t).group(1))
    msh = next((i + 1 for i in range(len(r)) if r[i] > 10.0), len(r))
    msh = 2 * ((msh + 1) // 2) - 1
    f = r[:msh] * (r[:msh] * vl[:msh] + 2.0 * z)
    g = f * rab[:msh] / 3.0
    s = 0.0
    for i in range(1, msh - 1, 2):
        s += g[i - 1] + 4 * g[i] + g[i + 1]
    return s, z, msh


def slab_vacuum(d, scf_in='scf.in', min_dist=5.0):
    """Vacuum level from the planar average: points farther than min_dist (A) from every atom plane (periodic in z).
    Returns E_vac (eV), spread (meV), mean of the two vacuum sides split at the cell middle of the vacuum gap
    (left = just above the slab top, right = just below the slab bottom, through the periodic boundary)."""
    z, vp, vm, f = avg_dat(d)
    cell, sym, frac, cart, s_in = read_struct_in(Path(d) / scf_in)
    c = float(cell[2, 2])
    za = np.mod(cart[:, 2], c)
    zA = z * BOHR
    dist = np.min(np.abs(((zA[:, None] - za[None, :]) + c / 2) % c - c / 2), axis=1)
    win = dist > min_dist
    # split the vacuum window into the side above the slab top and the side below the slab bottom
    top, bot = za.max(), za.min()
    up = win & (zA > top)
    lo = win & (zA < bot)
    ev = float(vp[win].mean() * RY)
    # linear ramp in the vacuum (a polar slab without dipole correction has a constant field there)
    zu = np.where(zA > top, zA, zA + c)[win]
    slope = float(np.polyfit(zu, vp[win] * RY, 1)[0])
    return {'E_vac_eV': ev, 'spread_meV': float((vp[win].max() - vp[win].min()) * RY * 1000), 'n_points': int(win.sum()),
            'ramp_slope_meV_per_A': slope * 1000, 'ramp_over_window_meV': slope * 1000 * float(zu.max() - zu.min()),
            'vacuum_gap_A': float(c - (top - bot)),
            'above_top_eV': float(vp[up].mean() * RY) if up.any() else None,
            'below_bottom_eV': float(vp[lo].mean() * RY) if lo.any() else None, 'src': f, 'cell_c_A': c,
            'slab_z_range_A': [float(bot), float(top)]}


def dump(name, obj):
    OUT.mkdir(exist_ok=True)
    (OUT / f'{name}.json').write_text(json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o)))
