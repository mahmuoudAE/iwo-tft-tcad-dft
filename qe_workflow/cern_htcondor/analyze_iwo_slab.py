"""1 nm IWO slab vs pure 1 nm slab (same relaxed in-plane cell, same settings).
Band edges at Gamma from the SCF eigenvalues (band nocc-1 = VB top, band nocc = CB bottom, nocc = 312 for both),
vacuum level from the planar average, E_F (IWO is metallic: 3 extra electrons), W-O bonds, W 5d PDOS centroid,
in-plane CB mass (parabolic, |k| <= 0.05 1/A) from the bands run."""
import glob
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collect_results import eig, H2M, RY, BOHR  # noqa: E402

R = Path(__file__).resolve().parent / 'results'


def edges(d, nocc=312):
    ks, ev = eig(d / 'scf.out', nocc)
    g = int(np.argmin(np.linalg.norm(ks, axis=1)))
    z, v = np.loadtxt(next(d.glob('*_avg.dat')), usecols=(0, 1), unpack=True)
    c = z.max() + (z[1] - z[0]); evac = v[np.minimum(z, c - z) * BOHR < 2.0].mean() * RY
    t = (d / 'scf.out').read_text(errors='replace')
    ef = re.findall(r'the Fermi energy is\s+(-?[\d.]+)', t)
    out = {'E_vac': evac, 'VB_G': ev[g, nocc - 1], 'CB_G': ev[g, nocc], 'E_F': float(ef[-1]) if ef else None}
    out['mstar'] = float('nan')
    try:   # the IWO bands run aborted (Davidson, rc 161): mass then not available
        kb, eb = eig(d / 'bands.out', nocc)
        k = np.linalg.norm(kb, axis=1)[:11]; e = eb[:11, nocc] - eb[0, nocc]; s = k <= 0.0501
        out['mstar'] = H2M / np.polyfit(k[s] ** 2, e[s], 1)[0]
    except Exception:
        pass
    return out


p, w = edges(R / 'slab1r_final_cpu'), edges(R / 'iwo_slab1_final_cpu')
for name, x in (('pure 1 nm', p), ('IWO 1 nm', w)):
    ef = f"{x['E_F'] - x['CB_G']:+.3f} eV" if x['E_F'] is not None else 'insulating'
    print(f"{name:10s} gap(G) {x['CB_G'] - x['VB_G']:.4f} eV | Evac-CB {x['E_vac'] - x['CB_G']:.4f} | Evac-VB {x['E_vac'] - x['VB_G']:.4f} | "
          f"E_F - CB {ef} | m* {x['mstar']:.4f} m0")
print(f"W effect: dGap {(w['CB_G'] - w['VB_G']) - (p['CB_G'] - p['VB_G']):+.4f} eV, dEA {(w['E_vac'] - w['CB_G']) - (p['E_vac'] - p['CB_G']):+.4f} eV, "
      f"dm* {w['mstar'] - p['mstar']:+.4f} m0")
from ase.io import read
from ase.neighborlist import neighbor_list
at = read(R / 'iwo_slab1_W24d_x1' / 'relax.out', format='espresso-out', index=-1)
iw = [i for i, s in enumerate(at.get_chemical_symbols()) if s == 'W'][0]
i, j, dd = neighbor_list('ijd', at, 2.6)
print('W-O (A):', np.round(np.sort(dd[(i == iw) & (at.numbers[j] == 8)]), 3).tolist())
f = sorted(glob.glob(str(R / 'iwo_slab1_final_cpu' / 'pdos' / '*(W)_wfc#*(d)')))
if f:
    e, ld = np.loadtxt(f[0], usecols=(0, 1), unpack=True)
    ef = w['E_F']; up = e > w['CB_G']
    print(f"W 5d: weight below E_F {ld[e <= ef].sum() / ld.sum():.2f}; centroid of W 5d above the CB minimum at "
          f"CB + {(e[up] * ld[up]).sum() / ld[up].sum() - w['CB_G']:.2f} eV (window to E_F + 4 eV)")
