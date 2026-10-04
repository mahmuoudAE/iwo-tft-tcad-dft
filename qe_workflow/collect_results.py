"""Collect every finished DFT result into cern_htcondor/results/summary.json (read by the dashboard).

Bulk (local, bulk_In2O3_protocol): relaxed a, fundamental gap, CB mass at Gamma.
Slabs (CERN): gap, EA, IP, dEg vs bulk, compared with Lin et al., ACS Nano 16, 21536 (2022), p. 21542.
IWO bulk (CERN): relaxed energies, site preference dE = E(8b) - E(24d), W-O bonds vs Shannon radii.
Only numbers present in output files are reported; anything missing stays null.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
B, R = HERE / 'bulk_In2O3_protocol', HERE / 'cern_htcondor' / 'results'
sys.path.insert(0, str(HERE / 'cern_htcondor'))
from analyze_slabs import one as slab_one  # noqa: E402

RY, BOHR, H2M = 13.605693122994, 0.529177210903, 3.80998212
LIN = {'a_A': 10.30, 'gap_bulk_eV': 0.94, 'gap_095nm_eV': 1.88, 'gap_198nm_eV': 1.27,
       'mstar_bulk': 0.17, 'mstar_095nm': 0.30, 'mstar_198nm': 0.23, 'page': 'p. 21540, 21542'}


def eig(path, nocc):
    t = open(path, errors='replace').read()
    alat = float(re.search(r'lattice parameter \(alat\)\s+=\s+([\d.]+)', t).group(1)) * BOHR
    bl = re.findall(r'k =\s*([-\d. ]+?)\s*\(\s*\d+ PWs\)\s+bands \(ev\):\s+(.*?)(?=\n\s*\n\s*(?:k =|highest|the Fermi|Writing|occupation)|\n\s*\n\s*\n)', t, re.S)
    ks = np.array([[float(x) for x in re.findall(r'-?\d+\.\d+', k.replace('-', ' -'))][:3] for k, _ in bl]) * 2 * np.pi / alat
    ev = np.array([[float(x) for x in re.findall(r'-?\d+\.\d+', e.replace('-', ' -'))][:nocc + 2] for _, e in bl])
    return ks, ev


def bulk():
    out = {}
    vr = B / 'vcrelax_ecut71_k3.out'
    if vr.exists():
        v = re.findall(r'new unit-cell volume =\s+[\d.]+ a\.u\.\^3 \(\s*([\d.]+) Ang\^3', vr.read_text(errors='replace'))
        if v:
            out['a_A'] = round((2 * float(v[-1])) ** (1 / 3), 4)
            out['a_exp_A'] = 10.117
    if (B / 'bands_path.out').exists():
        _, ev = eig(B / 'bands_path.out', 176)
        out['gap_fundamental_eV'] = round(ev[:, 176].min() - ev[:, 175].max(), 4)
    if (B / 'bands_gamma.out').exists():
        ks, ev = eig(B / 'bands_gamma.out', 176)
        k = np.linalg.norm(ks, axis=1)
        e = ev[:, 176] - ev[0, 176]
        s = (k <= 0.0501)
        out['mstar_m0'] = round(H2M / np.polyfit(k[s] ** 2, e[s], 1)[0], 4)
        out['gap_gamma_eV'] = round(ev[0, 176] - ev[0, 175], 4)
    return out


def slab_mass(d):
    f = d / 'bands.out'
    if not f.exists() or 'JOB DONE' not in f.read_text(errors='replace'):
        return None
    nocc = int(re.search(r'number of electrons\s+=\s+([\d.]+)', f.read_text(errors='replace')).group(1).split('.')[0]) // 2
    ks, ev = eig(f, nocc)
    k = np.linalg.norm(ks, axis=1)
    e = ev[:, nocc] - ev[0, nocc]
    first = slice(0, 11)                       # Gamma + [100] points
    s = k[first] <= 0.0501
    return round(H2M / np.polyfit(k[first][s] ** 2, e[first][s], 1)[0], 4)


def slabs(gap_bulk):
    rows = []
    for d in sorted(R.iterdir()):
        if not d.is_dir() or not (d / 'scf.out').exists() or 'failed' in d.name:
            continue
        r = slab_one(d)
        if not r:
            continue
        r = {k: (float(v) if isinstance(v, (np.floating,)) else v) for k, v in r.items()}
        r['relaxed'] = 'relax' in d.name
        r['mstar_m0'] = slab_mass(d)
        if gap_bulk:
            r['dEg_eV'] = round(r['gap_eV'] - gap_bulk, 4)
        rows.append(r)
    return rows


def iwo():
    from ase.io import read
    from ase.neighborlist import neighbor_list
    res = {}
    for site in ('8b', '24d'):
        cands = [R / f'iwo_W{site}', R / f'iwo_W{site}_checkpoint', R / f'iwo_W{site}_partial']
        d = next((c for c in cands if (c / 'relax.out').exists() and 'Final energy' in (c / 'relax.out').read_text(errors='replace')), None)
        if not d:
            continue
        t = (d / 'relax.out').read_text(errors='replace')
        at = read(d / 'relax.out', format='espresso-out', index=-1)
        w = [i for i, s in enumerate(at.get_chemical_symbols()) if s == 'W'][0]
        i, j, dist = neighbor_list('ijd', at, 2.6)
        wo = np.sort(dist[(i == w) & (at.numbers[j] == 8)])
        rec = {'source': d.name, 'E_Ry': float(re.findall(r'Final energy\s+=\s+([-\d.]+)', t)[-1]),
               'bfgs_steps': int(re.findall(r'(\d+) bfgs steps', t)[-1]) if re.findall(r'(\d+) bfgs steps', t) else None,
               'W_O_A': np.round(wo, 3).tolist(), 'W_O_mean_A': round(float(wo.mean()), 3)}
        sp = d / 'spin_k3.out'
        if sp.exists():
            m = re.findall(r'total magnetization\s+=\s+(-?[\d.]+)', sp.read_text(errors='replace'))
            rec['total_magnetization_muB'] = float(m[-1]) if m else None
        res[site] = rec
    if '8b' in res and '24d' in res:
        res['dE_8b_minus_24d_eV'] = round((res['8b']['E_Ry'] - res['24d']['E_Ry']) * RY, 3)
        res['preferred_site'] = '24d' if res['dE_8b_minus_24d_eV'] > 0 else '8b'
    res['shannon_W_O_A'] = {'W6+': 1.98, 'W5+': 2.00, 'W4+': 2.04, 'In3+': 2.18}
    return res


def gap_of(f):
    t = f.read_text(errors='replace') if f.exists() else ''
    m = re.findall(r'highest occupied, lowest unoccupied level \(ev\):\s+(-?[\d.]+)\s+(-?[\d.]+)', t)
    return (round(float(m[-1][1]) - float(m[-1][0]), 4), 'JOB DONE' in t) if m else (None, False)


def hse(slab_rows):
    """HSE06 single points (protocol: dEg(HSE)/dEg(PBE) within 10 % -> PBE confinement accepted)."""
    res = {}
    for d in sorted(R.glob('hse_*')):
        if d.is_dir() and not d.name.endswith('_x4'):
            g, done = gap_of(d / 'scf.out')
            res[d.name] = {'gap_eV': g, 'finished': done}
    b, s = res.get('hse_bulk_nq1', {}).get('gap_eV'), res.get('hse_slab1', {}).get('gap_eV')
    pbe = next((r.get('dEg_eV') for r in slab_rows if r['job'] == 'slab1r_final_cpu'), None)
    if b and s:
        res['dEg_HSE_eV'] = round(s - b, 4)
        if pbe:
            res['dEg_PBE_eV'] = pbe; res['ratio_HSE_PBE'] = round((s - b) / pbe, 3)
            res['criterion_10pct_met'] = abs((s - b) / pbe - 1) < 0.10
    if res.get('hse_bulk_nq3', {}).get('gap_eV') and b:
        res['bulk_gap_q_sensitivity_eV'] = round(res['hse_bulk_nq3']['gap_eV'] - b, 4)
    return res


def iwo_slabs():
    """W-doped slabs (metallic): relaxed W-O bonds, E_F, work function E_vac - E_F, CB mass at Gamma."""
    from ase.io import read
    from ase.neighborlist import neighbor_list
    out = {}
    for d in sorted(R.glob('iwo_slab*')):
        if not d.is_dir() or not (d / 'relax.out').exists():
            continue
        rec = {}
        t = (d / 'relax.out').read_text(errors='replace')
        if 'End final coordinates' in t:
            at = read(d / 'relax.out', format='espresso-out', index=-1)
            w = [i for i, s in enumerate(at.get_chemical_symbols()) if s == 'W'][0]
            i, j, dist = neighbor_list('ijd', at, 2.6)
            rec['W_O_A'] = np.round(np.sort(dist[(i == w) & (at.numbers[j] == 8)]), 3).tolist()
            rec['E_final_Ry'] = float(re.findall(r'Final energy\s+=\s+([-\d.]+)', t)[-1])
        s = (d / 'scf.out').read_text(errors='replace') if (d / 'scf.out').exists() else ''
        ef = re.findall(r'the Fermi energy is\s+(-?[\d.]+)', s)
        if ef:
            rec['E_F_eV'] = float(ef[-1])
            avg = next(d.glob('*_avg.dat'), None)
            if avg:
                z, v = np.loadtxt(avg, usecols=(0, 1), unpack=True); c = z.max() + (z[1] - z[0])
                rec['work_function_eV'] = round(float(v[np.minimum(z, c - z) * BOHR < 2.0].mean() * RY - rec['E_F_eV']), 4)
        rec['mstar_m0'] = slab_mass(d)
        out[d.name] = rec
    return out


def main():
    b = bulk()
    sl = slabs(b.get('gap_fundamental_eV'))
    summary = {'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'bulk': b,
               'slabs': sl, 'iwo': iwo(), 'hse': hse(sl), 'iwo_slabs': iwo_slabs(), 'lin2022': LIN}
    (R / 'summary.json').write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1)[:3000])


if __name__ == '__main__':
    main()
