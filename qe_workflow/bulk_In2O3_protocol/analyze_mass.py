"""Conduction-band effective mass at Gamma from a non-SCF run on Gamma + points along [100], [110], [111].

Usage: python analyze_mass.py <bands output> <number of occupied bands> [k-points per direction, default 10]
Protocol (PROTOCOL.md section 5): parabolic fit E = E0 + hbar^2 k^2 / (2 m*) for |k| <= 0.05 1/A;
non-parabolicity from a Kane fit E (1 + alpha E) = hbar^2 k^2 / (2 m*) over the whole range (|k| <= 0.15 1/A),
with E measured from the CBM. hbar^2 / (2 m0) = 3.80998 eV A^2 (CODATA 2018 constants).
"""
import re
import sys

import numpy as np

H2M = 3.80998212
text = open(sys.argv[1], errors='replace').read()
nocc = int(sys.argv[2])
nper = int(sys.argv[3]) if len(sys.argv) > 3 else 10
alat = float(re.search(r'lattice parameter \(alat\)\s+=\s+([\d.]+)', text).group(1)) * 0.529177210903
blocks = re.findall(r'k =\s*([-\d. ]+?)\s*\(\s*\d+ PWs\)\s+bands \(ev\):\s+(.*?)(?=\n\s*\n\s*(?:k =|highest|the Fermi|Writing|occupation)|\n\s*\n\s*\n)', text, re.S)
ks, ev = [], []
for kb, eb in blocks:
    kk = [float(x) for x in re.findall(r'-?\d+\.\d+', kb.replace('-', ' -'))][:3]
    e = [float(x) for x in re.findall(r'-?\d+\.\d+', eb.replace('-', ' -'))]
    ks.append(np.array(kk) * 2 * np.pi / alat)
    ev.append(e)
ev = np.array([e[:nocc + 2] for e in ev])
vbm_g, cbm_g = ev[0, nocc - 1], ev[0, nocc]
print(f'alat {alat:.5f} A; {len(ks)} k-points; at Gamma: VB top {vbm_g:.4f} eV, CB bottom {cbm_g:.4f} eV, direct gap {cbm_g - vbm_g:.4f} eV')
res = {}
for n, name in enumerate(['[100]', '[110]', '[111]']):
    idx = [0] + list(range(1 + n * nper, 1 + (n + 1) * nper))
    k = np.array([np.linalg.norm(ks[i]) for i in idx])
    e = ev[idx, nocc] - cbm_g
    s = k <= 0.05 + 1e-6
    c2 = np.polyfit(k[s] ** 2, e[s], 1)[0]
    m_par = H2M / c2
    # Kane: E + alpha E^2 = (H2M/m) k^2  ->  linear least squares in (1/m, alpha) with E, E^2 known
    A = np.column_stack([H2M * k[1:] ** 2, -e[1:] ** 2])
    inv_m, alpha = np.linalg.lstsq(A, e[1:], rcond=None)[0]
    res[name] = (m_par, 1 / inv_m, alpha)
    print(f'{name}: m*(parabolic, |k|<=0.05) = {m_par:.4f} m0; Kane fit (|k|<={k.max():.3f}): m* = {1 / inv_m:.4f} m0, alpha = {alpha:.3f} 1/eV; '
          f'E(k=0.15) - CBM = {e[-1]:.4f} eV')
m = np.array([v[0] for v in res.values()])
print(f'mean parabolic m* = {m.mean():.4f} m0 (spread {m.max() - m.min():.4f}); isotropy check across directions')
