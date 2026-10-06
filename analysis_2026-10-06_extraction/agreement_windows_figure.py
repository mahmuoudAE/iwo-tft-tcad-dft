#!/usr/bin/env python3
"""Figure of the post hoc SS agreement ranges (rule and numbers from agreement_windows.py / agreement_windows.json).
Row 1: measured I_D as measured; row 2: measured I_D minus the off-state floor. Per panel: subthreshold transfer curve,
TCAD, the agreement range shaded, measured points inside it filled. Output: figures/ss_agreement_windows.(png|pdf)."""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'report_latex_full' / 'figures' / 'src'))
import extraction as ex  # noqa: E402
import run_extraction as rx  # noqa: E402
from style import plt, FILM  # noqa: E402

RES = {(r['film'], r['variant']): r for r in json.loads((HERE / 'agreement_windows.json').read_text())}
XL = {2.0: (0.0, 0.75), 6.3: (0.05, 0.8), 13.2: (-0.45, 0.35)}
BOX = dict(fc='white', ec='0.75', lw=0.5, pad=2.0)
meas = rx.load_measured()
fig, ax = plt.subplots(2, 3, figsize=(7.4, 5.4), gridspec_kw=dict(wspace=0.38, hspace=0.42))
for row, variant in enumerate(('raw', 'floor removed')):
    for col_i, t in enumerate(rx.FILMS):
        a = ax[row, col_i]
        vg, i0 = meas[t]; tc = rx.load_tcad(t); fl = ex.off_floor(vg, i0); col = FILM[t]
        i = i0 - fl if variant == 'floor removed' else i0
        r = RES[(t, variant)]
        a.axhline(fl, color='0.5', ls=':', lw=0.8)
        a.axhline(r['admissible_from'], color='0.5', ls='-.', lw=0.7)
        mk = 'o' if variant == 'raw' else 'D'
        a.semilogy(vg, np.where(i > 0, i, np.nan), mk, ms=3.0 if mk == 'o' else 2.7, mfc='none', mec='k', mew=0.7, zorder=5,
                   label='measured' if variant == 'raw' else 'measured $-$ floor')
        a.semilogy(tc['vg'], np.where(tc['i'] > 0, tc['i'], np.nan), '-', color=col, lw=1.3, zorder=4, label='TCAD')
        if 'lo' in r:
            a.axhspan(r['lo'], r['hi'], color='#2E86C1', alpha=0.28, lw=0, zorder=0)
            k = (i >= r['lo']) & (i <= r['hi'])
            a.semilogy(vg[k], i[k], mk, ms=3.4 if mk == 'o' else 3.0, color='k', zorder=6)
            txt = (f"{r['lo']:.1e}-{r['hi']:.0e} A/$\\mu$m\n{r['decades']:.2f} dec, {r['n_points']} points\n"
                   f"SS {r['ss_meas']:.1f} $\\pm$ {r['sig_meas']:.1f} meas.\n     {r['ss_tcad']:.1f} TCAD (mV/dec)")
        else:
            a.axhspan(r['admissible_from'], 1e-9, color='0.85', lw=0, zorder=0)
            txt = f"no window within $\\pm$5 mV/dec\nin the admissible range (grey)\nmin |$\\Delta$| = {min(abs(d) for _, d in r['windows']):.1f} mV/dec"
        a.text(0.97, 0.03, txt, transform=a.transAxes, ha='right', va='bottom', fontsize=5.5, linespacing=1.3, bbox=BOX)
        a.set_xlim(*XL[t]); a.set_ylim(1e-15, 1e-8)
        a.set_xlabel('$V_G$ (V)'); a.set_ylabel('$I_D$ (A/$\\mu$m)')
        a.set_title(f"{t:.1f} nm, {'measured' if variant == 'raw' else 'measured, floor removed'}", fontsize=7.8)
        if col_i == 0:
            a.legend(loc='upper left', fontsize=5.8, frameon=True, framealpha=0.95, edgecolor='0.75')
fig.text(0.5, 0.0, 'Post hoc, descriptive. One-decade windows with |SS$_{TCAD}-$SS$_{meas}|\\leq$5 mV/dec, upper edge $\\leq10^{-9}$ A/$\\mu$m; '
         'lower edge $\\geq$10$\\times$ floor (top row) or $\\geq$1$\\times$ floor (bottom row, assumes an additive,\n'
         'gate-independent floor). Dotted: measured floor; dash-dot: lowest admissible edge. Filled symbols: measured points inside the agreement range.',
         ha='center', va='top', fontsize=5.8, color='0.3')
fig.savefig(HERE / 'figures' / 'ss_agreement_windows.pdf', bbox_inches='tight')
fig.savefig(HERE / 'figures' / 'ss_agreement_windows.png', dpi=300, bbox_inches='tight')
