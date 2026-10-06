#!/usr/bin/env python3
"""Plain illustration of the surface + bulk trap picture: the same surface traps on every film, bulk traps in
proportion to thickness; per-area totals and per-volume densities. Output: figures/surface_bulk_explained.(png|pdf)."""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'report_latex_full' / 'figures' / 'src'))
from style import plt, FILM  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

NS, NB = 3.57e12, 2.15e18          # cm^-2, cm^-3 (audit S4, through the 2.0 and 13.2 nm anchors)
fig = plt.figure(figsize=(7.4, 3.3))
ax = fig.add_axes([0.0, 0.0, 0.62, 1.0]); ax.axis('off'); ax.set_xlim(0, 30); ax.set_ylim(-5.2, 15.5)
rng = np.random.default_rng(1)
x0 = 1.0
for t in (2.0, 6.3, 13.2):
    h = t * 0.75                                   # drawn height proportional to thickness
    w = 7.0
    ax.add_patch(Rectangle((x0, 0), w, h, fc='#F3C89B', ec='k', lw=0.7))
    xs = np.linspace(x0 + 0.4, x0 + w - 0.4, 9)
    ax.plot(xs, np.full(9, 0.0), 'o', ms=4, color='#1A5276', clip_on=False)            # surface traps: bottom face
    ax.plot(xs, np.full(9, h), 'o', ms=4, color='#1A5276', clip_on=False)              # top face
    nb = int(round(2.4 * t))                                                           # bulk traps grow with t
    ax.plot(rng.uniform(x0 + 0.4, x0 + w - 0.4, nb), rng.uniform(0.5, h - 0.5, nb) if h > 1.2 else np.full(nb, h / 2),
            's', ms=3, color='#C0392B')
    surf, bulk = NS, NB * t * 1e-7
    ax.text(x0 + w / 2, h + 0.9, f'{t:.1f} nm', ha='center', fontsize=8, fontweight='bold', color=FILM[t])
    ax.text(x0 + w / 2, -0.9, f'surface {surf / 1e12:.1f}\n+ bulk {bulk / 1e12:.2f}\n= {(surf + bulk) / 1e12:.1f} $\\times10^{{12}}$/cm$^2$\n'
            f'per volume: {(surf + bulk) / (t * 1e-7):.1e}/cm$^3$\nat the surface: {100 * surf / (surf + bulk):.0f} %',
            ha='center', va='top', fontsize=6.2, linespacing=1.3)
    x0 += w + 2.6
ax.plot([], [], 'o', ms=4, color='#1A5276', label='surface traps: same number per area on every film')
ax.plot([], [], 's', ms=3, color='#C0392B', label='bulk traps: number grows with thickness')
ax.legend(loc='upper left', fontsize=6.4, frameon=False, bbox_to_anchor=(0.0, 1.0))

b = fig.add_axes([0.71, 0.17, 0.27, 0.68])
tt = np.linspace(1.0, 20, 300)
b.plot(tt, NS / (tt * 1e-7) / 1e19, '-', color='#1A5276', lw=1.0, label='surface part $N_s/t$')
b.plot(tt, np.full_like(tt, NB / 1e19), '-', color='#C0392B', lw=1.0, label='bulk part $N_b$')
b.plot(tt, (NS / (tt * 1e-7) + NB) / 1e19, 'k--', lw=1.3, label='total')
for t in (2.0, 6.3, 13.2):
    b.plot([t], [(NS / (t * 1e-7) + NB) / 1e19], 'o', ms=5, color=FILM[t])
b.set_xlim(0, 20); b.set_ylim(0, 4)
b.set_xlabel('IWO thickness $t$ (nm)'); b.set_ylabel('traps per volume (10$^{19}$ cm$^{-3}$)')
b.legend(loc='upper right', fontsize=6.0, frameon=True, framealpha=0.95, edgecolor='0.75')
b.set_title('dividing by $t$: thin films look\nmore trapped per volume', fontsize=7.2)
fig.savefig(HERE / 'figures' / 'surface_bulk_explained.pdf'); fig.savefig(HERE / 'figures' / 'surface_bulk_explained.png', dpi=300)
