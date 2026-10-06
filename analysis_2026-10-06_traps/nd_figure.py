#!/usr/bin/env python3
"""Explanatory figure for the effective donor density N_D,eff of the V1 TCAD model: what it represents, the thickness
law used (values parsed from the final decks), and how strongly it acts on the threshold voltage.
Output: figures/nd_eff.(png|pdf)."""
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(PKG / 'report_latex_full' / 'figures' / 'src'))
from style import plt, FILM  # noqa: E402

Q, EPS0 = 1.602176634e-19, 8.8541878128e-14
COX, EPS_S = 8.955369814335959e-07, 9.3 * 8.8541878128e-14
RUNS = {2.0: 'run_0038_*', 6.3: 'run_0039_*', 13.2: 'run_0040_*'}
deck = {}
for t, pat in RUNS.items():
    txt = (next((PKG / 'results' / 'runs').glob(pat)) / 'device.in').read_text()
    deck[t] = float(re.search(r'doping uniform n\.type conc=([0-9.eE+-]+) region=1', txt).group(1))
ND0, TC, K = 2.5e17, 20.0, 4
law = lambda t: ND0 * (1 + (t / TC) ** K)
for t in deck:
    assert abs(deck[t] / law(t) - 1) < 1e-4, (t, deck[t], law(t))


def dvth(nd, t_nm):
    t = t_nm * 1e-7
    return Q * nd * t / COX, Q * nd * t ** 2 / (2 * EPS_S)


fig, ax = plt.subplots(1, 3, figsize=(7.4, 2.75), gridspec_kw=dict(wspace=0.42, width_ratios=[1.05, 1, 1]))
# (a) what it represents
a = ax[0]
a.set_xlim(0, 10); a.set_ylim(-1.8, 10); a.axis('off')
a.fill_between([0.5, 9.5], 8.2, 9.6, color='#D6E4F0'); a.plot([0.5, 9.5], [8.2, 8.2], 'k-', lw=1.2)
a.fill_between([0.5, 9.5], 0.2, 1.4, color='#E5E5E5'); a.plot([0.5, 9.5], [1.4, 1.4], 'k-', lw=1.2)
a.text(9.6, 8.2, '$E_c$', va='center', fontsize=7.5); a.text(9.6, 1.4, '$E_v$', va='center', fontsize=7.5)
for x in (1.4, 3.0, 4.6):
    a.plot([x - 0.45, x + 0.45], [7.55, 7.55], color='#117A65', lw=2)
    a.text(x, 7.0, '$\\oplus$', ha='center', va='center', fontsize=8, color='#117A65')
    a.annotate('', (x + 0.15, 8.9), (x, 7.7), arrowprops=dict(arrowstyle='->', lw=0.7, color='#117A65'))
    a.text(x + 0.35, 9.05, 'e$^-$', fontsize=6.5, color='#1A5276')
a.text(3.0, 5.75, 'shallow donors:\nO vacancies, W on In sites', ha='center', fontsize=6.0, color='#117A65', linespacing=1.2)
for x in (6.6, 8.2):
    a.plot([x - 0.45, x + 0.45], [4.0, 4.0], color='#C0392B', lw=2)
    a.text(x, 3.45, '$\\ominus$', ha='center', va='center', fontsize=8, color='#C0392B')
a.text(7.4, 2.4, 'compensating\nacceptors', ha='center', fontsize=6.0, color='#C0392B', linespacing=1.2)
a.text(5.0, -1.0, '$N_{D,eff}$ = net ionised shallow donors\n(not the W content)', ha='center', fontsize=6.4,
       fontweight='bold', linespacing=1.2)
a.set_title('(a) what it represents', fontsize=8, loc='left')
# (b) the thickness law used in the TCAD
b = ax[1]
tt = np.linspace(1, 35, 300)
b.semilogy(tt, law(tt), 'k-', lw=1.2, label='$N_{d0}[1+(t/t_c)^4]$')
for t, v in deck.items():
    b.semilogy([t], [v], 'o', ms=5, color=FILM[t], label=f'{t:.1f} nm')
b.semilogy([31.8], [law(31.8)], 'o', ms=4.5, mfc='none', mec='0.4', label='31.8 nm (extrapolated)')
b.axhspan(4.3e17, 4.5e17, color='#F5CBA7', lw=0)
b.text(1.0, 4.75e17, 'other IWO process', fontsize=5.6, color='#A04000')
b.set_xlim(0, 35); b.set_ylim(1e17, 4e18)
b.set_xlabel('IWO thickness $t$ (nm)'); b.set_ylabel('$N_{D,eff}$ (cm$^{-3}$)')
b.set_title('(b) value used in the TCAD', fontsize=8, loc='left')
b.legend(loc='upper left', fontsize=5.4, frameon=True, framealpha=0.95, edgecolor='0.75', handlelength=1.2)
b.text(0.97, 0.04, '$N_{d0}=2.5\\times10^{17}$ cm$^{-3}$, $t_c$ = 20 nm\nfitted; uniform DOPING in IWO', transform=b.transAxes,
       ha='right', va='bottom', fontsize=5.6, bbox=dict(fc='white', ec='0.75', lw=0.5, pad=1.5))
# (c) leverage on the threshold
c = ax[2]
t1, t2 = dvth(1e18, tt)
c.semilogy(tt, t1 + t2, 'k--', lw=1.0, label='per $10^{18}$ cm$^{-3}$')
s1, s2 = dvth(law(tt), tt)
c.semilogy(tt, s1 + s2, '-', color='#117A65', lw=1.3, label='with the V1 values')
for t in deck:
    u1, u2 = dvth(deck[t], t)
    c.semilogy([t], [u1 + u2], 'o', ms=5, color=FILM[t])
    c.annotate(f'{1e3 * (u1 + u2):.0f} mV', (t, u1 + u2), xytext=(4, -9), textcoords='offset points', fontsize=6, color=FILM[t])
c.set_xlim(0, 35); c.set_ylim(3e-3, 5)
c.set_xlabel('IWO thickness $t$ (nm)'); c.set_ylabel('$|\\Delta V_{th}|$ from donors (V)')
c.set_title('(c) effect on the threshold', fontsize=8, loc='left')
c.legend(loc='upper left', fontsize=5.8, frameon=True, framealpha=0.95, edgecolor='0.75')
c.text(0.97, 0.04, '$\\Delta V_{th}=-\\frac{qN_Dt}{C_{ox}}-\\frac{qN_Dt^2}{2\\varepsilon_s}$', transform=c.transAxes, ha='right',
       va='bottom', fontsize=7, bbox=dict(fc='white', ec='0.75', lw=0.5, pad=1.5))
fig.savefig(HERE / 'figures' / 'nd_eff.pdf'); fig.savefig(HERE / 'figures' / 'nd_eff.png', dpi=300); plt.close(fig)
for t in deck:
    u1, u2 = dvth(deck[t], t); p1, p2 = dvth(1e18, t)
    print(f'{t} nm: N_D,eff {deck[t]:.4e}; dVth {1e3 * (u1 + u2):.1f} mV (front {1e3 * u1:.1f}, film {1e3 * u2:.1f}); per 1e18: {p1 + p2:.3f} V')
