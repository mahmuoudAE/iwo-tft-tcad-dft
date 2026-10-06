#!/usr/bin/env python3
"""Figure of the post hoc SS agreement ranges (rule in agreement_windows.py): per film, the subthreshold transfer curve,
the agreement range shaded, the measured points inside it filled, and the SS of both over the range.
6.3 nm also shows its full clean range (all windows within the measurement uncertainty). Output: figures/ss_agreement_windows.(png|pdf)."""
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'report_latex_full' / 'figures' / 'src'))
import extraction as ex  # noqa: E402
import run_extraction as rx  # noqa: E402
from style import plt, FILM  # noqa: E402

RANGES = {2.0: [(5.62e-14, 1.0e-10, 'agreement range')],
          6.3: [(5.62e-12, 1.0e-10, 'agreement range'), (None, 1.0e-9, 'full clean range')],
          13.2: []}
XL = {2.0: (0.0, 0.75), 6.3: (0.05, 0.8), 13.2: (-0.45, 0.35)}
BOX = dict(fc='white', ec='0.75', lw=0.5, pad=2.0)
meas = rx.load_measured()
fig, ax = plt.subplots(1, 3, figsize=(7.4, 2.9), gridspec_kw=dict(wspace=0.38))
for a, t in zip(ax, rx.FILMS):
    vg, i = meas[t]; tc = rx.load_tcad(t); fl = ex.off_floor(vg, i); col = FILM[t]
    a.axhline(fl, color='0.5', ls=':', lw=0.8); a.axhline(10 * fl, color='0.5', ls='-.', lw=0.7)
    lines = []
    for n, (lo, hi, lab) in enumerate(RANGES[t]):
        lo = 10 * fl if lo is None else lo
        a.axhspan(lo, hi, color='#2E86C1' if n == 0 else '#AED6F1', alpha=0.28 if n == 0 else 0.25, lw=0, zorder=0)
        m = ex.ss_window(vg, i, lo, hi, False); s = ex.ss_window(tc['vg'], tc['i'], lo, hi, True)
        npts = int(((i >= lo) & (i <= hi)).sum())
        lines.append(f"{lab}: {lo:.1e}-{hi:.0e}\n({math.log10(hi / lo):.1f} dec, {npts} points)\n"
                     f"SS {m['ss']:.1f} $\\pm$ {m['sig']:.1f} meas. / {s['ss']:.1f} TCAD")
        if n == 0:
            k = (i >= lo) & (i <= hi)
            a.semilogy(vg[k], i[k], 'o', ms=3.4, color='k', zorder=6)
    a.semilogy(vg, np.where(i > 0, i, np.nan), 'o', ms=3.0, mfc='none', mec='k', mew=0.7, zorder=5, label='measured')
    a.semilogy(tc['vg'], np.where(tc['i'] > 0, tc['i'], np.nan), '-', color=col, lw=1.3, zorder=4, label='TCAD')
    if t == 13.2:
        a.axhspan(10 * fl, 1e-9, color='0.85', lw=0, zorder=0)
        m = ex.ss_window(vg, i, 1e-10, 1e-9, False); s = ex.ss_window(tc['vg'], tc['i'], 1e-10, 1e-9, True)
        lines.append(f"no $\\pm$5 mV/dec agreement in the\nclean range (grey, 1.2 dec)\n"
                     f"$10^{{-10}}$-$10^{{-9}}$: {m['ss']:.1f} meas. / {s['ss']:.1f} TCAD")
    a.set_xlim(*XL[t]); a.set_ylim(1e-15, 1e-8)
    a.set_xlabel('$V_G$ (V)'); a.set_ylabel('$I_D$ (A/$\\mu$m)'); a.set_title(f'{t:.1f} nm', fontsize=8.5)
    a.text(0.97, 0.03, '\n'.join(lines), transform=a.transAxes, ha='right', va='bottom', fontsize=5.4, linespacing=1.3, bbox=BOX)
    if t == 2.0:
        a.legend(loc='upper left', fontsize=6.0, frameon=True, framealpha=0.95, edgecolor='0.75')
fig.text(0.5, -0.13, 'Post hoc, descriptive: one-decade windows with |SS$_{TCAD}-$SS$_{meas}|\\leq$5 mV/dec, lower edge $\\geq$10$\\times$ floor (dash-dot; dotted: floor),\nupper edge $\\leq10^{-9}$ A/$\\mu$m (currents in A/$\\mu$m, SS in mV/dec). Filled points: measured points inside the agreement range.',
         ha='center', fontsize=6.0, color='0.3')
fig.savefig(HERE / 'figures' / 'ss_agreement_windows.pdf', bbox_inches='tight')
fig.savefig(HERE / 'figures' / 'ss_agreement_windows.png', dpi=300, bbox_inches='tight')
