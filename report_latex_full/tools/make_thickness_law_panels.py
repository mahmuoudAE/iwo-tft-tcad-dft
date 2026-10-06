#!/usr/bin/env python3
"""The five panels of the thickness-law figure (make_figures.thickness_laws) as individual figures, drawn with the
same plotting code and report style (figures/src/style.py). Changes against the combined figure (user requests,
2026-10-06): (b) carries its references and the DFT points of this work with the V2 law, and its legend sits in the
empty upper-right corner (in the combined figure the legend marker, at the panel centre, looks like a fourth data
point); (c) and (d) carry the definitions of N_t and N_d,eff.
Output: figures/thickness_laws_individual/thickness_law_{a..e}_*.{pdf,png}
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'figures' / 'src'))
from style import *  # noqa: F401,F403  (plt, ACCENT, ACCENT2, GREY, FILM, HALF_W, panel_label)
import matplotlib.pyplot as plt

OUT = HERE.parent / 'figures' / 'thickness_laws_individual'
OUT.mkdir(parents=True, exist_ok=True)
for old in OUT.glob('thickness_law_*'):
    old.unlink()
Q = 1.602176634e-19
t = np.linspace(0.9, 32, 400); hb = 1.054571817e-34; me = 9.1093837015e-31
FILMS = [2.0, 6.3, 13.2]
SIZE = (HALF_W, 2.55)


def panel(letter):
    fig, a = plt.subplots(figsize=SIZE)
    panel_label(a, letter)
    return fig, a


def verticals(a):
    for x in FILMS:
        a.axvline(x, color=FILM[x], lw=0.6, ls=':')


def save(fig, name):
    fig.savefig(OUT / f'{name}.pdf')
    fig.savefig(OUT / f'{name}.png', dpi=300)
    plt.close(fig)


# (a) conduction-band shift: as in the combined figure
fig, a = panel('a')
a.loglog(t, 0.9205 * t ** -1.3815, color=ACCENT, lw=1.4, label=r'ATLAS law 0.9205 $t^{-1.3815}$')
for m, ls in [(0.18, ':'), (0.26, '--'), (0.35, '-.')]:
    a.loglog(t, (hb * np.pi) ** 2 / (2 * m * me * (t * 1e-9) ** 2) / Q, ls, color=GREY, lw=0.9, label=rf'infinite well $m^*$={m}')
a.loglog([1.98, 0.95], [0.33, 0.94], 'o', color='k', ms=4, label='Lin 2022 PBE slabs')
a.loglog([1.5], [0.6], 's', color='k', ms=4, label='Si 2021 PBE')
a.loglog([2.0, 6.3, 13.2], [0.2556, 0.0359, 0.016], 'D', color=ACCENT2, ms=4, label='S3 SP-equivalent shift (Q1)')
a.set_ylim(3e-3, 3); a.set_xlabel('t (nm)'); a.set_ylabel(r'$\Delta E_c$ (eV)'); a.legend(fontsize=5.6, loc='lower left')
save(fig, 'thickness_law_a_dEc')

# (b) effective mass: V1 law with Lin 2022 increments on the measured bulk mass; DFT points and V2 law of this work
fig, a = panel('b')
a.plot(t, 0.208 + 0.1311 * t ** -1.412, color=ACCENT, label='V1 law')
tv2 = t[t >= 0.95]
a.plot(tv2, 0.208 + 0.11416 * tv2 ** -1.29453, '--', color=ACCENT2, lw=1.1, label='V2 law (this work)')
a.axhline(0.208, color=GREY, lw=0.8, ls='-.', label='bulk 0.208, Stokey 2021')
a.plot([3.52, 1.98, 0.95], [0.228, 0.268, 0.338], 'o', color='k', ms=4, label='0.208 + PBE increments, Lin 2022')
a.plot([1.98, 0.95], [0.208 + (0.20615 - 0.159), 0.208 + (0.281 - 0.159)], 's', color=ACCENT2, ms=4,
       label='0.208 + PBE increments, this work')
verticals(a)
a.set_xscale('log'); a.set_xlabel('t (nm)'); a.set_ylabel(r'$m^*/m_0$'); a.set_ylim(0.195, 0.372)
a.legend(fontsize=5.4, loc='upper right', frameon=True, framealpha=0.92, edgecolor='0.75')
save(fig, 'thickness_law_b_mstar')

# (c) tail-state density: as in the combined figure, with the definition of N_t
fig, a = panel('c')
a.loglog(t, 2e19 * (2 / t) ** 0.75, color=ACCENT, label=r'law $2\times10^{19}(2/t)^{0.75}$')
a.loglog(t, 2.15e18 + 3.57e12 / (t * 1e-7), '--', color=ACCENT2, label='surface + bulk')
a.loglog([2.0, 10.0], [5.3e19, 3.39e18], 's', color='k', ms=4, label='Januar 2026 (PBS devices)')
verticals(a)
a.set_xlabel('t (nm)'); a.set_ylabel(r'$N_t$ (cm$^{-3}$)'); a.legend(fontsize=5.6, loc='upper right', frameon=True, framealpha=0.92, edgecolor='0.75')
a.text(0.04, 0.05, '$N_t=\\int g_{TA}\\,dE\\approx N_{TA}W_{TA}$\n$g_{TA}=N_{TA}\\,e^{(E-E_c)/W_{TA}}$\n$W_{TA}$ = 40 meV\n'
       'acceptor-like CB-tail states', transform=a.transAxes, fontsize=5.6, va='bottom', linespacing=1.4,
       bbox=dict(fc='white', ec='none', alpha=0.85, pad=1.5))
save(fig, 'thickness_law_c_Nt')

# (d) effective donor density: as in the combined figure, with the definition of N_d,eff
fig, a = panel('d')
a.semilogy(t, 2.5e17 * (1 + (t / 20) ** 4), color=ACCENT)
verticals(a)
a.set_xlabel('t (nm)'); a.set_ylabel(r'$N_{d,eff}$ (cm$^{-3}$)')
a.text(0.04, 0.95, '$N_{d,eff}=N_{d0}\\,[1+(t/t_c)^4]$\n$N_{d0}=2.5\\times10^{17}$ cm$^{-3}$, $t_c$ = 20 nm\n'
       'ionized background donors (net),\nnot the W concentration', transform=a.transAxes, fontsize=5.6, va='top', linespacing=1.4,
       bbox=dict(fc='white', ec='none', alpha=0.85, pad=1.5))
save(fig, 'thickness_law_d_Nd')

# (e) roughness factor: as in the combined figure
fig, a = panel('e')
a.plot(t, (1 - 0.287 / t) ** 2, color=ACCENT)
verticals(a)
a.set_xscale('log'); a.set_xlabel('t (nm)'); a.set_ylabel(r'$(1-\Delta_{sr}/t)^2$')
save(fig, 'thickness_law_e_roughness')
print('written to', OUT)
