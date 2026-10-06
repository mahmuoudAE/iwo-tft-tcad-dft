#!/usr/bin/env python3
"""Full picture of the 13.2 nm device: transfer curve over the whole sweep (log and linear), measured, measured minus the
off-state floor, and TCAD (run 0040 rescaled); the normalised SS window and the floor-removed agreement window; local SS
against current. Output: figures/film_13p2_full.(png|pdf)."""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'report_latex_full' / 'figures' / 'src'))
import extraction as ex  # noqa: E402
import run_extraction as rx  # noqa: E402
from style import plt, FILM, panel_label  # noqa: E402

t = 13.2
col = FILM[t]
vg, i = rx.load_measured()[t]; tc = rx.load_tcad(t); fl = ex.off_floor(vg, i)
A1 = json.loads((HERE / 'results_a1.json').read_text())['films'][str(t)]['results']['main']
AG = {(r['film'], r['variant']): r for r in json.loads((HERE / 'agreement_windows.json').read_text())}[(t, 'floor removed')]
R = json.loads((HERE / 'results.json').read_text())['films'][str(t)]
nlo, nhi = A1['window']
BOX = dict(fc='white', ec='0.75', lw=0.5, pad=2.0)
LEG = dict(fontsize=6.0, frameon=True, framealpha=0.95, edgecolor='0.75')
fig, ax = plt.subplots(1, 3, figsize=(7.6, 2.9), gridspec_kw=dict(wspace=0.42, width_ratios=[1.15, 1, 1]))

a = ax[0]
a.axhspan(nlo, nhi, color='#2E86C1', alpha=0.25, lw=0)
a.axhspan(AG['lo'], AG['hi'], facecolor='none', edgecolor='#C0392B', hatch='////', lw=0)
a.axhline(fl, color='0.45', ls=':', lw=0.9)
a.semilogy(vg, i, 'o', ms=2.6, mfc='none', mec='k', mew=0.7, label='measured')
ic = i - fl
a.semilogy(vg, np.where(ic > 0, ic, np.nan), 'D', ms=2.3, mfc='none', mec='0.5', mew=0.6, label='measured $-$ floor')
a.semilogy(tc['vg'], np.where(tc['i'] > 0, tc['i'], np.nan), '-', color=col, lw=1.4, label='TCAD')
a.set_xlim(-3, 3); a.set_ylim(1e-18, 1e-4)
a.set_xlabel('$V_G$ (V)'); a.set_ylabel('$I_D$ (A/$\\mu$m)')
a.legend(loc='lower right', **LEG)
a.text(-2.85, fl / 6, f'floor {fl:.1e}', fontsize=5.8, color='0.35')
a.text(-2.85, 3e-6, '$V_D$ = 0.7 V, $W$ = 290 $\\mu$m, $L$ = 20 $\\mu$m', fontsize=5.8)
panel_label(a, 'a', x=-0.25)

b = ax[1]
b.plot(vg, i * 1e6, 'o', ms=2.6, mfc='none', mec='k', mew=0.7, label='measured')
b.plot(tc['vg'], tc['i'] * 1e6, '-', color=col, lw=1.4, label='TCAD')
b.set_xlim(-1, 3); b.set_ylim(-0.1, 4.7)
b.set_xlabel('$V_G$ (V)'); b.set_ylabel('$I_D$ ($\\mu$A/$\\mu$m)')
b.legend(loc='upper left', **LEG)
m, s = R['measured'], R['simulated']
b.text(0.03, 0.80, f"measured / TCAD\n$V_{{th,cc}}$: {m['vth_cc']['v']:.3f} / {s['vth_cc']['v']:.3f} V\n"
       f"$I_{{on}}$: {i[-1]:.2e} (fitted)\n$\\mu_{{FE}}$(3 V): {m['mu_fe']['3.0']['mu_fe']:.1f} / {s['mu_fe']['3.0']['mu_fe']:.1f} cm$^2$/Vs\n"
       f"SS, normalised window:\n   {A1['measured']:.1f} $\\pm$ {A1['sig_measured']:.1f} / {A1['tcad']:.1f} mV/dec\n"
       f"SS, floor removed,\n   {AG['lo']:.0e}-{AG['hi']:.0e} A/$\\mu$m:\n   {AG['ss_meas']:.1f} $\\pm$ {AG['sig_meas']:.1f} / {AG['ss_tcad']:.1f} mV/dec",
       transform=b.transAxes, ha='left', va='top', fontsize=5.0, linespacing=1.3, bbox=BOX)
panel_label(b, 'b', x=-0.25)

c = ax[2]
c.axvspan(nlo, nhi, color='#2E86C1', alpha=0.25, lw=0, label='normalised window')
c.axvspan(AG['lo'], AG['hi'], facecolor='none', edgecolor='#C0392B', hatch='////', lw=0, label='floor-removed agreement')
x, y = ex.local_ss(vg, i); k = x > 1.5 * fl
c.semilogx(x[k], y[k], 'o', ms=2.6, mfc='none', mec='k', mew=0.7)
x2, y2 = ex.local_ss(vg, ic); k2 = x2 > 0.3 * fl
c.semilogx(x2[k2], y2[k2], 'D', ms=2.3, mfc='none', mec='0.5', mew=0.6)
xs, ys = ex.local_ss(tc['vg'], tc['i'])
c.semilogx(xs, ys, '-', color=col, lw=1.3)
c.axvline(fl, color='0.45', ls=':', lw=0.9); c.axvline(10 * fl, color='0.45', ls='-.', lw=0.7)
c.axhline(ex.S_TH, color='0.55', ls='--', lw=0.7)
c.set_xlim(1e-13, 1e-8); c.set_ylim(40, 320)
c.set_xlabel('$I_D$ (A/$\\mu$m)'); c.set_ylabel('local SS (mV/dec)')
c.legend(loc='upper left', **LEG)
panel_label(c, 'c', x=-0.25)
fig.suptitle('13.2 nm IWO TFT: measured vs TCAD', fontsize=8.5, y=1.02)
fig.savefig(HERE / 'figures' / 'film_13p2_full.pdf', bbox_inches='tight')
fig.savefig(HERE / 'figures' / 'film_13p2_full.png', dpi=300, bbox_inches='tight')
