"""IWO bulk read-out: relaxed W-O bonds (protocol item 3) and, if present, W 5d PDOS weight vs E_F (item 5).
Usage: python analyze_iwo.py <job folder> [<job folder> ...]"""
import glob
import re
import sys

import numpy as np
from ase.io import read
from ase.neighborlist import neighbor_list

SHANNON = {'W6+': 1.98, 'W5+': 2.00, 'W4+': 2.04, 'In3+': 2.18}   # r(cation, CN6) + r(O2-, CN4), Shannon (1976)
for d in sys.argv[1:]:
    at = read(f'{d}/relax.out', format='espresso-out', index=-1)
    w = [i for i, s in enumerate(at.get_chemical_symbols()) if s == 'W'][0]
    i, j, dist = neighbor_list('ijd', at, 2.6)
    wo = np.sort(dist[(i == w) & (at.numbers[j] == 8)])
    ino = dist[(at.numbers[i] == 49) & (at.numbers[j] == 8)]
    e = float(re.findall(r'Final energy\s+=\s+([-\d.]+)', open(f'{d}/relax.out').read())[-1])
    print(f'{d}: E_final {e:.7f} Ry; W-O = {np.round(wo, 3).tolist()} A, mean {wo.mean():.3f} A; '
          f'mean In-O {ino.mean():.3f} A; Shannon W6+/W5+/W4+/In3+ = {SHANNON}')
    pd = sorted(glob.glob(f'{d}/pdos/*(W)_wfc#*(d)'))
    if pd:
        ef = float(re.findall(r'the Fermi energy is\s+([-\d.]+)', open(f'{d}/scf_k4.out').read())[-1])
        e_, ldos = np.loadtxt(pd[0], usecols=(0, 1), unpack=True)
        tot = np.loadtxt(glob.glob(f'{d}/pdos/*pdos_tot')[0], usecols=(0, 1), unpack=True)
        occ = ldos[e_ <= ef].sum() / ldos.sum()
        above = e_ > ef
        cen = (e_[above] * ldos[above]).sum() / ldos[above].sum() - ef
        # CBM estimate: lowest energy above the valence band where the total DOS rises again
        print(f'   E_F = {ef:.4f} eV; W 5d weight in window below E_F = {occ:.2f}; centroid of W 5d above E_F at E_F + {cen:.2f} eV '
              f'(window {e_.min() - ef:.1f} to +{e_.max() - ef:.1f} eV)')
