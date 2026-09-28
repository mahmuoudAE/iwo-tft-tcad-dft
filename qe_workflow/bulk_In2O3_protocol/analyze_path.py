"""Band path read-out (stage 3b): VBM/CBM location and gap along Gamma-H-N-Gamma-P-H|P-N; optional plot.
Usage: python analyze_path.py bands_path.out 176 [plot.png]"""
import re
import sys

import numpy as np

text = open(sys.argv[1], errors='replace').read()
nocc = int(sys.argv[2])
alat = float(re.search(r'lattice parameter \(alat\)\s+=\s+([\d.]+)', text).group(1)) * 0.529177210903
blocks = re.findall(r'k =\s*([-\d. ]+?)\s*\(\s*\d+ PWs\)\s+bands \(ev\):\s+(.*?)(?=\n\s*\n\s*(?:k =|highest|the Fermi|Writing|occupation)|\n\s*\n\s*\n)', text, re.S)
ks = np.array([[float(x) for x in re.findall(r'-?\d+\.\d+', kb.replace('-', ' -'))][:3] for kb, _ in blocks]) * 2 * np.pi / alat
ev = np.array([[float(x) for x in re.findall(r'-?\d+\.\d+', eb.replace('-', ' -'))][:nocc + 8] for _, eb in blocks])
d = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(ks, axis=0), axis=1))])
jump = np.linalg.norm(np.diff(ks, axis=0), axis=1) > 0.3        # H|P discontinuity: no distance added
d = np.concatenate([[0], np.cumsum(np.where(jump, 0, np.linalg.norm(np.diff(ks, axis=0), axis=1)))])
iv, ic = ev[:, nocc - 1].argmax(), ev[:, nocc].argmin()
print(f'{len(ks)} k-points; VBM {ev[iv, nocc - 1]:.4f} eV at k = {np.round(ks[iv] / (2 * np.pi / (alat * 2 / np.sqrt(3))), 3)} (2pi/a); '
      f'CBM {ev[ic, nocc]:.4f} eV at k = {np.round(ks[ic] / (2 * np.pi / (alat * 2 / np.sqrt(3))), 3)} (2pi/a)')
print(f'VB at Gamma {ev[0, nocc - 1]:.4f} eV -> VBM - VB(Gamma) = {1000 * (ev[iv, nocc - 1] - ev[0, nocc - 1]):.1f} meV; '
      f'fundamental gap {ev[ic, nocc] - ev[iv, nocc - 1]:.4f} eV; direct gap at Gamma {ev[0, nocc] - ev[0, nocc - 1]:.4f} eV')
if len(sys.argv) > 3:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    ref = ev[iv, nocc - 1]
    fig, ax = plt.subplots(figsize=(6, 4.5))
    for b in range(ev.shape[1]):
        ax.plot(d, ev[:, b] - ref, color='k' if b < nocc else '0.35', lw=0.8)
    labels = ['$\\Gamma$', 'H', 'N', '$\\Gamma$', 'P', 'H|P', 'N']
    ticks = [d[0]] + [d[i + 1] for i in range(len(d) - 1) if False]
    ax.set_xlim(d[0], d[-1]); ax.set_ylim(-3, 4)
    ax.axhline(0, ls=':', color='0.5', lw=0.6)
    ax.set_ylabel('Energy relative to VBM (eV)')
    ax.set_title('In$_2$O$_3$ (bixbyite), PBE, a = 10.306 A')
    fig.tight_layout(); fig.savefig(sys.argv[3], dpi=200)
    print('plot written', sys.argv[3])
