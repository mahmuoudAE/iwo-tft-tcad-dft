#!/usr/bin/env python3
"""Descriptive map of where the measured and TCAD subthreshold swings agree: one-decade windows slid in 0.25-decade
steps; Delta = SS_TCAD - SS_measured with its 1 sigma; open symbols where the window's lower edge is < 10 x the measured
floor (floor-affected), filled where clean. Not used to choose any reported window. Output: figures/ss_agreement_map.(png|pdf)."""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'report_latex_full' / 'figures' / 'src'))
import extraction as ex  # noqa: E402
import run_extraction as rx  # noqa: E402
from style import plt, FILM, HALF_W  # noqa: E402

meas = rx.load_measured()
fig, a = plt.subplots(figsize=(HALF_W * 1.35, 2.8))
a.axhspan(-5, 5, color='0.93', lw=0)
for t in rx.FILMS:
    vg, i = meas[t]; tc = rx.load_tcad(t); fl = ex.off_floor(vg, i)
    xs, ds, ss, clean = [], [], [], []
    for e in np.arange(-14.0, -8.49, 0.25):
        lo = 10 ** e; hi = 10 * lo
        if lo < 2 * fl or hi > 1.0001e-9:
            continue
        m = ex.ss_window(vg, i, lo, hi, False); s = ex.ss_window(tc['vg'], tc['i'], lo, hi, True)
        if m['ss'] is None or s['ss'] is None:
            continue
        xs.append(lo * 10 ** 0.5); ds.append(s['ss'] - m['ss']); ss.append(np.hypot(m['sig'], s['sig'])); clean.append(lo >= 10 * fl)
    xs, ds, ss, clean = map(np.array, (xs, ds, ss, clean))
    a.fill_between(xs, ds - 2 * ss, ds + 2 * ss, color=FILM[t], alpha=0.15, lw=0)
    a.semilogx(xs, ds, '-', color=FILM[t], lw=1.0)
    a.semilogx(xs[clean], ds[clean], 'o', ms=3.5, color=FILM[t], label=f'{t:.1f} nm')
    a.semilogx(xs[~clean], ds[~clean], 'o', ms=3.5, mfc='white', mec=FILM[t])
a.axhline(0, color='k', lw=0.6)
a.set_xlim(1e-13, 1e-9); a.set_ylim(-30, 50)
a.set_xlabel('window centre $I_D$ (A/$\\mu$m), one-decade windows'); a.set_ylabel('SS$_{TCAD}$ $-$ SS$_{meas}$ (mV/dec)')
a.legend(loc='upper left', fontsize=6.3, frameon=True, framealpha=0.95, edgecolor='0.75',
         title='filled: >= 10x floor; open: floor-affected\nbands: $\\pm2\\sigma$; grey: $\\pm$5 mV/dec', title_fontsize=5.6)
fig.savefig(HERE / 'figures' / 'ss_agreement_map.pdf'); fig.savefig(HERE / 'figures' / 'ss_agreement_map.png', dpi=300)
