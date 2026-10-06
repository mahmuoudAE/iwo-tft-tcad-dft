#!/usr/bin/env python3
"""Main-text figure candidates for the manuscript: the comparisons in which the TCAD agrees with the data, each
labelled with what was fitted. The full comparison, including the disagreements, is in figures/fig1-4 and compare_*
(Supplementary). Output: figures/paper/paper_{a,b,c}_*.{png,pdf}.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PKG / 'report_latex_full' / 'figures' / 'src'))
import extraction as ex  # noqa: E402
import run_extraction as rx  # noqa: E402
from style import plt, FILM, HALF_W, panel_label  # noqa: E402

OUT = HERE / 'figures' / 'paper'
OUT.mkdir(parents=True, exist_ok=True)
R = json.loads((HERE / 'results.json').read_text())
A1 = json.loads((HERE / 'results_a1.json').read_text())
MEAS = rx.load_measured()
TC = {t: rx.load_tcad(t) for t in rx.FILMS}
LEG = dict(fontsize=6.3, frameon=True, framealpha=0.95, edgecolor='0.75', handlelength=1.8)
TXT = dict(fontsize=6.0, linespacing=1.4, bbox=dict(fc='white', ec='0.75', lw=0.5, pad=2.0))


def save(fig, name):
    fig.savefig(OUT / f'{name}.pdf'); fig.savefig(OUT / f'{name}.png', dpi=300); plt.close(fig); print('saved', name)


# (a) transfer curves, all films, log scale (calibrated: Q_f and mu_band fitted per film)
fig, a = plt.subplots(figsize=(HALF_W, 2.7))
panel_label(a, 'a')
for t in rx.FILMS:
    vg, i = MEAS[t]; tc = TC[t]; col = FILM[t]
    a.semilogy(vg, i, 'o', ms=2.6, mfc='none', mec=col, mew=0.7)
    a.semilogy(tc['vg'], np.where(tc['i'] > 0, tc['i'], np.nan), '-', color=col, lw=1.3, label=f'{t:.1f} nm')
a.set_xlim(-1.0, 3.0); a.set_ylim(1e-15, 1e-5)
a.set_xlabel('$V_G$ (V)'); a.set_ylabel('$I_D$ (A/$\\mu$m)')
a.legend(loc='lower right', title='circles: measured\nlines: TCAD', title_fontsize=5.8, **LEG)
a.text(0.04, 0.96, '$V_D$ = 0.7 V', transform=a.transAxes, va='top', fontsize=6.3)
save(fig, 'paper_a_transfer_curves')

# (b) 13.2 nm field-effect mobility versus V_G, with the residual
t = 13.2
vg, i = MEAS[t]; tc = TC[t]; col = FILM[t]
_, sig = ex.gm_sigma(vg, i)
k = (vg >= 1.0 - 1e-9) & (vg <= 3.0 + 1e-9)
mu = ex.MU_FACTOR * ex.gm(vg, i)
ks = (tc['vg'] >= 1.0 - 1e-9) & (tc['vg'] <= 3.0 + 1e-9)
mus = ex.MU_FACTOR * ex.gm(tc['vg'], tc['i'])
fig, (a, r) = plt.subplots(2, 1, figsize=(HALF_W, 3.2), sharex=True, gridspec_kw=dict(height_ratios=[3, 1.2], hspace=0.08))
panel_label(a, 'b')
a.errorbar(vg[k], mu[k], yerr=ex.MU_FACTOR * sig[k], fmt='o', ms=3.0, mfc='none', mec='k', mew=0.7, ecolor='0.45', elinewidth=0.6,
           label='measured')
a.plot(tc['vg'][ks], mus[ks], '-', color=col, lw=1.4, label='TCAD')
a.set_ylim(20, 56); a.set_ylabel('$\\mu_{FE}$ (cm$^2$/Vs)')
a.legend(loc='lower right', **LEG)
a.text(0.04, 0.95, '13.2 nm, $V_D$ = 0.7 V\n$\\mu_{FE} = L g_m/(W C_{ox} V_D)$', transform=a.transAxes, va='top', **TXT)
mus_on_meas = np.interp(vg[k], tc['vg'], mus)
rel = 100 * (mus_on_meas - mu[k]) / mu[k]
rsig = 100 * np.hypot(ex.MU_FACTOR * sig[k], ex.SIM_REL_GM * mus_on_meas) / mu[k]
r.axhspan(-2, 2, color='0.92', lw=0)
r.errorbar(vg[k], rel, yerr=rsig, fmt='o', ms=2.4, color=col, mfc='none', mew=0.7, elinewidth=0.6)
r.axhline(0, color='k', lw=0.6)
r.set_ylim(-9, 9); r.set_xlim(0.95, 3.05)
r.set_xlabel('$V_G$ (V)'); r.set_ylabel('TCAD/meas.$-$1 (%)', fontsize=7)
save(fig, 'paper_b_mobility_13nm')

# (c) local SS versus normalised current, all films (measured points >= 10 x floor)
fig, a = plt.subplots(figsize=(HALF_W, 2.7))
panel_label(a, 'c')
lo_n = A1['r_main']
a.axvspan(lo_n, 10 * lo_n, color='#DCE6F2', lw=0)
for t in rx.FILMS:
    vg, i = MEAS[t]; tc = TC[t]; col = FILM[t]
    fl = R['films'][str(t)]['floor']; ion = float(i[-1])
    x, y = ex.local_ss(vg, i); m = x >= 10 * fl
    xs, ys = ex.local_ss(tc['vg'], tc['i'])
    a.semilogx(x[m] / ion, y[m], 'o', ms=2.8, mfc='none', mec=col, mew=0.8)
    a.semilogx(xs / ion, ys, '-', color=col, lw=1.2, label=f'{t:.1f} nm')
a.axhline(ex.S_TH, color='0.5', lw=0.7, ls='--')
a.text(2e-8, ex.S_TH + 4, '$(kT/q)\\ln 10$', fontsize=5.8, color='0.4', va='bottom')
a.set_xlim(1e-8, 1e-2); a.set_ylim(40, 320)
a.set_xlabel('$I_D / I_{on}$'); a.set_ylabel('SS (mV/dec)')
a.legend(loc='upper left', title='circles: measured\nlines: TCAD', title_fontsize=5.8, **LEG)
save(fig, 'paper_c_ss_vs_normalised_current')
