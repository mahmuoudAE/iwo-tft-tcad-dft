"""Two-step band alignment of the relaxed 1 and 2 nm slabs to bulk In2O3 (campaign item 1.3).

Step 1 (bulk): E_v,bulk - <V>_bulk, with <V> the cell average of the pp.x plot_num 11 potential (bulk_v11.cube,
        relaxed bulk, prefix vcr) and E_v / E_c from bands_path.out (VBM band 176 maximum, CBM band 177 minimum).
Step 2 (slab): the macroscopic average of the same potential (window a/4) at the slab centre, from <job>_avg.dat.
Then E_v,bulk-aligned = Vbar_slab(centre) + (E_v - <V>)_bulk, and
     dEv(t) = E_VBM,slab - E_v,bulk-aligned,  dEc(t) = E_CBM,slab - E_c,bulk-aligned,  dEc - dEv = dEg (identity).
Caveats printed: plateau flatness at the centre (the 1 nm film has almost no bulk-like interior) and the in-plane
strain of the slab against the bulk lattice (10.306 A).
"""
import re
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
R = HERE.parent / 'cern_htcondor' / 'results'
RY, BOHR = 13.605693122994, 0.529177210903


def read_cube(f):
    lines = Path(f).read_text().splitlines()
    nat = abs(int(lines[2].split()[0]))
    n = [int(lines[3 + i].split()[0]) for i in range(3)]
    data = np.array(' '.join(lines[6 + nat:]).split(), float)
    assert data.size == n[0] * n[1] * n[2], (data.size, n)
    return data


def bands_edges(f, nocc):
    t = Path(f).read_text(errors='replace')
    blocks = re.findall(r'bands \(ev\):\s+(.*?)(?=\n\s*\n)', t, re.S)
    ev = np.array([[float(x) for x in re.findall(r'-?\d+\.\d+', b.replace('-', ' -'))][:nocc + 1] for b in blocks])
    return ev[:, nocc - 1].max(), ev[:, nocc].min()


v_bulk = read_cube(HERE / 'bulk_v11.cube')
vmean = v_bulk.mean()                                    # Ry (pp.x units)
ev_b, ec_b = bands_edges(HERE / 'bands_path.out', 176)
dv_b, dc_b = ev_b - vmean * RY, ec_b - vmean * RY
print(f'bulk: <V> = {vmean:.6f} Ry = {vmean * RY:.4f} eV; E_v = {ev_b:.4f}, E_c = {ec_b:.4f} eV; gap {ec_b - ev_b:.4f} eV')
print(f'      E_v - <V> = {dv_b:.4f} eV, E_c - <V> = {dc_b:.4f} eV')

rows = []
for job, label, a_inplane in (('slab1r_final_cpu', '1 nm', 10.3355), ('slab2_relax_c2', '2 nm', 10.3135)):
    d = R / job
    z, vp, vm = np.loadtxt(next(d.glob('*_avg.dat')), usecols=(0, 1, 2), unpack=True)   # bohr, Ry, Ry
    sc = (d / 'scf.out').read_text(errors='replace')
    vbm, cbm = map(float, re.findall(r'highest occupied, lowest unoccupied level \(ev\):\s+(-?[\d.]+)\s+(-?[\d.]+)', sc)[-1])
    # slab centre from the In positions of the SCF input (crystal coordinates along c)
    sin = (d / 'scf.in').read_text()
    c = float(re.findall(r'CELL_PARAMETERS angstrom\s*\n.*\n.*\n\s*[-\d.]+\s+[-\d.]+\s+([-\d.]+)', sin)[0]) / BOHR
    zin = np.array([float(m) for m in re.findall(r'^\s*In\s+[-\d.]+\s+[-\d.]+\s+([-\d.]+)', sin, re.M)]) * c
    zc = 0.5 * (zin.min() + zin.max())
    half_period = 10.306 / 4 / BOHR / 2
    win = np.abs(z - zc) <= half_period                  # +- a/8 around the centre
    vc = np.interp(zc, z, vm)
    spread = (vm[win].max() - vm[win].min()) * RY * 1000
    ev_al, ec_al = vc * RY + dv_b, vc * RY + dc_b
    dEv, dEc = vbm - ev_al, cbm - ec_al
    rows.append((label, dEc, dEv))
    print(f'{label} ({job}): centre z = {zc * BOHR:.2f} A, Vbar(centre) = {vc * RY:.4f} eV, plateau spread over +-a/8 = {spread:.0f} meV')
    print(f'      slab VBM {vbm:.4f}, CBM {cbm:.4f} eV -> dEv = {dEv:+.4f} eV, dEc = {dEc:+.4f} eV, dEc - dEv = {dEc - dEv:.4f} eV '
          f'(dEg {cbm - vbm - (ec_b - ev_b):.4f}); share in CB {dEc / (dEc - dEv):.2f}; in-plane strain {100 * (a_inplane / 10.306 - 1):+.2f} %')
(l1, c1, v1), (l2, c2, v2) = rows
print(f'check against the EA/IP route: dEc(1)-dEc(2) = {c1 - c2:+.4f} eV (EA route +0.5665), dEv(1)-dEv(2) = {v1 - v2:+.4f} eV (IP route -0.0019)')


def macro(z, vp, w):
    """Macroscopic average: running mean of the planar average over a window w (bohr), periodic in z."""
    dz = z[1] - z[0]; n = max(1, int(round(w / dz)))
    k = np.ones(n) / n
    ext = np.concatenate([vp[-n:], vp, vp[:n]])
    return np.convolve(ext, k, mode='same')[n:-n]


print('\n--- repeat with the true planar-average period of bixbyite along [001], a/2 (Ia-3: no a/4 translation in z)')
print('    and the double average a/2 * a/4; slab interior plateau quality decides which is usable')
res = {}
for job, label in (('slab1r_final_cpu', '1 nm'), ('slab2_relax_c2', '2 nm')):
    d = R / job
    z, vp = np.loadtxt(next(d.glob('*_avg.dat')), usecols=(0, 1), unpack=True)
    sc = (d / 'scf.out').read_text(errors='replace')
    vbm, cbm = map(float, re.findall(r'highest occupied, lowest unoccupied level \(ev\):\s+(-?[\d.]+)\s+(-?[\d.]+)', sc)[-1])
    sin = (d / 'scf.in').read_text()
    c = float(re.findall(r'CELL_PARAMETERS angstrom\s*\n.*\n.*\n\s*[-\d.]+\s+[-\d.]+\s+([-\d.]+)', sin)[0]) / BOHR
    zin = np.array([float(m) for m in re.findall(r'^\s*In\s+[-\d.]+\s+[-\d.]+\s+([-\d.]+)', sin, re.M)]) * c
    zc = 0.5 * (zin.min() + zin.max())
    for name, w in (('a/2', 10.306 / 2 / BOHR), ('a/2*a/4', None)):
        vm = macro(z, macro(z, vp, 10.306 / 4 / BOHR), 10.306 / 2 / BOHR) if w is None else macro(z, vp, w)
        win = np.abs(z - zc) <= 10.306 / 8 / BOHR
        vc = np.interp(zc, z, vm)
        spread = (vm[win].max() - vm[win].min()) * RY * 1000
        dEv, dEc = vbm - (vc * RY + dv_b), cbm - (vc * RY + dc_b)
        res[(label, name)] = (dEc, dEv, spread)
        print(f'{label} {name:8s}: Vbar(centre) {vc * RY:.4f} eV, spread +-a/8 {spread:5.0f} meV -> dEc {dEc:+.4f}, dEv {dEv:+.4f} eV, CB share {dEc / (dEc - dEv):.2f}')
for name in ('a/2', 'a/2*a/4'):
    c1, v1, _ = res[('1 nm', name)]; c2, v2, _ = res[('2 nm', name)]
    print(f'{name:8s} check: dEc(1)-dEc(2) {c1 - c2:+.4f} (EA route +0.5665), dEv(1)-dEv(2) {v1 - v2:+.4f} (IP route -0.0019)')
# recommended: two-step only for the 2 nm film (the 1 nm film has no bulk-like interior); 1 nm from the same-termination
# EA/IP differences, which need no interior plateau
c2, v2, s2 = res[('2 nm', 'a/2')]
print(f'\nRECOMMENDED (2 nm two-step, a/2 window; 1 nm via EA/IP differences):')
print(f'  2 nm: dEc = {c2:+.4f}, dEv = {v2:+.4f} eV (plateau spread {s2:.0f} meV)')
print(f'  1 nm: dEc = {c2 + 0.5665:+.4f}, dEv = {v2 - 0.0019:+.4f} eV')
