#!/usr/bin/env python3
"""Individual SS panels in a plain plotting-software style (no text boxes; everything explained in the captions):
(a) SS vs thickness, normalised window; (b) local SS vs I_D/I_on, all films; (c-e) local SS vs I_D per film with the
range of agreement shaded; (f) SS_TCAD - SS_meas in sliding one-decade windows. Values from results_a1.json,
agreement_windows.json and the curves. Output: figures/ss_origin/ss_{a..f}_*.(png|pdf)."""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'report_latex_full' / 'figures' / 'src'))
import extraction as ex  # noqa: E402
import run_extraction as rx  # noqa: E402
from style import plt, FILM, HALF_W, panel_label  # noqa: E402

OUT = HERE / 'figures' / 'ss_origin'
OUT.mkdir(parents=True, exist_ok=True)
A1 = json.loads((HERE / 'results_a1.json').read_text())
AG = {(r['film'], r['variant']): r for r in json.loads((HERE / 'agreement_windows.json').read_text())}
MEAS = rx.load_measured()
TC = {t: rx.load_tcad(t) for t in rx.FILMS}
FL = {t: ex.off_floor(*MEAS[t]) for t in rx.FILMS}
LEG = dict(fontsize=6.5, frameon=True, framealpha=1.0, edgecolor='0.6', fancybox=False, handlelength=1.8)
SHADE = {2.0: (AG[(2.0, 'raw')]['lo'], AG[(2.0, 'raw')]['hi']), 6.3: (10 * FL[6.3], 1e-9), 13.2: None}


def new(letter, size=(HALF_W, 2.55)):
    fig, a = plt.subplots(figsize=size)
    a.grid(False)
    panel_label(a, letter)
    return fig, a


def save(fig, name):
    fig.savefig(OUT / f'{name}.pdf'); fig.savefig(OUT / f'{name}.png', dpi=300); plt.close(fig); print('saved', name)


# (a) SS vs thickness in the normalised window
t = np.array(rx.FILMS)
r = [A1['films'][str(x)]['results']['main'] for x in rx.FILMS]
fig, a = new('a')
a.errorbar(t, [q['measured'] for q in r], yerr=[q['sig_measured'] for q in r], fmt='o-', color='#0072B2', ms=5, lw=1.2,
           capsize=2.5, elinewidth=0.9, label='measured')
a.errorbar(t, [q['tcad'] for q in r], yerr=[q['sig_tcad'] for q in r], fmt='s--', color='#D55E00', ms=5.5, lw=1.2, mfc='none',
           mew=1.2, capsize=2.5, elinewidth=0.9, label='TCAD')
a.set_xticks(rx.FILMS); a.set_xlabel('IWO thickness (nm)'); a.set_ylabel('SS (mV/dec)'); a.set_ylim(100, 145)
a.legend(loc='upper left', **LEG)
save(fig, 'ss_a_vs_thickness')

# (b) local SS vs normalised current
fig, a = new('b')
lo = A1['r_main']
a.axvspan(lo, 10 * lo, color='0.88', lw=0)
for x in rx.FILMS:
    vg, i = MEAS[x]; ion = float(i[-1])
    xs, ys = ex.local_ss(vg, i); m = xs >= 10 * FL[x]
    a.semilogx(xs[m] / ion, ys[m], 'o', ms=3.2, mfc='none', mec=FILM[x], mew=0.9)
    xt, yt = ex.local_ss(TC[x]['vg'], TC[x]['i'])
    a.semilogx(xt / ion, yt, '-', color=FILM[x], lw=1.3, label=f'{x:.1f} nm')
a.axhline(ex.S_TH, color='0.4', ls='--', lw=0.8)
a.set_xlim(1e-8, 1e-2); a.set_ylim(40, 320)
a.set_xlabel('$I_D/I_{on}$'); a.set_ylabel('SS (mV/dec)')
a.legend(loc='upper left', **LEG)
save(fig, 'ss_b_vs_normalised_current')

# (c-e) local SS vs I_D per film
for letter, x in zip('cde', rx.FILMS):
    fig, a = new(letter)
    vg, i = MEAS[x]; tc = TC[x]
    if SHADE[x]:
        a.axvspan(*SHADE[x], color='#BBD7EA', lw=0)
    else:
        a.axvspan(10 * FL[x], 1e-9, color='0.88', lw=0)
    xs, ys = ex.local_ss(vg, i); m = xs >= 1.5 * FL[x]
    a.semilogx(xs[m], ys[m], 'o', ms=3.4, mfc='none', mec='k', mew=0.9, label='measured')
    xt, yt = ex.local_ss(tc['vg'], tc['i'])
    a.semilogx(xt, yt, '-', color=FILM[x], lw=1.4, label='TCAD')
    a.axvline(FL[x], color='0.4', ls=':', lw=0.9)
    a.axhline(ex.S_TH, color='0.4', ls='--', lw=0.8)
    a.set_xlim(1e-14, 1e-8); a.set_ylim(40, 320)
    a.set_xlabel('$I_D$ (A/$\\mu$m)'); a.set_ylabel('SS (mV/dec)')
    a.legend(loc='upper left', title=f'{x:.1f} nm', title_fontsize=6.5, **LEG)
    save(fig, f"ss_{letter}_{str(x).replace('.', 'p')}nm")

# (f) Delta SS in sliding one-decade windows
fig, a = new('f')
a.axhspan(-5, 5, color='0.9', lw=0)
for x in rx.FILMS:
    w = [(e, d) for e, d in AG[(x, 'raw')]['windows']]
    allw = []
    vg, i = MEAS[x]; tc = TC[x]
    for e in np.arange(-14.0, -8.99, 0.25):
        lo_, hi_ = 10 ** e, 10 ** (e + 1)
        if lo_ < 2 * FL[x] or hi_ > 1.0001e-9:
            continue
        mm = ex.ss_window(vg, i, lo_, hi_, False); ss = ex.ss_window(tc['vg'], tc['i'], lo_, hi_, True)
        if mm['ss'] is None or ss['ss'] is None:
            continue
        allw.append((lo_ * 10 ** 0.5, ss['ss'] - mm['ss'], lo_ >= 10 * FL[x]))
    xs = np.array([q[0] for q in allw]); ds = np.array([q[1] for q in allw]); cl = np.array([q[2] for q in allw])
    a.semilogx(xs, ds, '-', color=FILM[x], lw=1.0)
    a.semilogx(xs[cl], ds[cl], 'o', ms=4, color=FILM[x], label=f'{x:.1f} nm')
    a.semilogx(xs[~cl], ds[~cl], 'o', ms=4, mfc='white', mec=FILM[x], mew=0.9)
a.axhline(0, color='k', lw=0.6)
a.set_xlim(1e-13, 1e-9); a.set_ylim(-20, 30)
a.set_xlabel('$I_D$ (A/$\\mu$m)'); a.set_ylabel('SS$_{TCAD}-$SS$_{meas}$ (mV/dec)')
a.legend(loc='upper left', **LEG)
save(fig, 'ss_f_difference')
