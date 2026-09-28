"""Read-out of the slab jobs: band edges, vacuum level, electron affinity (EA) and ionization potential (IP).

Usage: python analyze_slabs.py <results folder>
For every job folder with scf.out and <job>_avg.dat:
  VBM, CBM   highest occupied / lowest unoccupied Kohn-Sham level of the SCF (3x3x1 grid, includes Gamma)
  E_vac      planar average of the electrostatic potential (pp.x plot_num 11, Ry -> eV) in the middle of the
             vacuum, i.e. within 2 A of the cell boundary (the slab is centred in the cell); the spread of the
             planar average in that window is reported as a flatness check
  EA = E_vac - CBM,  IP = E_vac - VBM,  gap = CBM - VBM
Writes slabs_summary.json and prints a table.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

RY = 13.605693122994
BOHR = 0.529177210903


def one(d):
    scf = (d / 'scf.out').read_text(errors='replace')
    m = re.findall(r'highest occupied, lowest unoccupied level \(ev\):\s+(-?[\d.]+)\s+(-?[\d.]+)', scf)
    if not m:
        return None
    vbm, cbm = map(float, m[-1])
    avg = next(d.glob('*_avg.dat'), None)
    rec = {'job': d.name, 'VBM_eV': vbm, 'CBM_eV': cbm, 'gap_eV': round(cbm - vbm, 4),
           'scf_iterations': int(re.findall(r'convergence has been achieved in\s+(\d+)', scf)[-1]),
           'total_force_Ry_bohr': float(re.findall(r'Total force =\s+([\d.]+)', scf)[-1])}
    if avg:
        z, v = np.loadtxt(avg, usecols=(0, 1), unpack=True)
        c = z.max() + (z[1] - z[0])
        dist = np.minimum(z, c - z) * BOHR                      # distance from the cell boundary (A)
        win = dist < 2.0
        evac = v[win].mean() * RY
        rec.update({'E_vac_eV': round(evac, 4), 'vacuum_plateau_spread_meV': round((v[win].max() - v[win].min()) * RY * 1000, 2),
                    'EA_eV': round(evac - cbm, 4), 'IP_eV': round(evac - vbm, 4)})
    return rec


def main():
    root = Path(sys.argv[1])
    recs = [r for r in (one(d) for d in sorted(root.iterdir()) if d.is_dir() and (d / 'scf.out').exists()) if r]
    (root / 'slabs_summary.json').write_text(json.dumps(recs, indent=1))
    for r in recs:
        print(r)


if __name__ == '__main__':
    main()
