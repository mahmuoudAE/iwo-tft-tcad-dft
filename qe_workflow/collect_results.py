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


def main():
    b = bulk()
    summary = {'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'bulk': b,
               'slabs': slabs(b.get('gap_fundamental_eV')), 'iwo': iwo(), 'lin2022': LIN}
    (R / 'summary.json').write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1)[:3000])


if __name__ == '__main__':
    main()
