#!/usr/bin/env python3
"""Measured vs simulated device metrics, panels (a)-(d) of the measured-metrics figure as individual figures.
Measured: data/experimental_clean.csv. Simulated: the calibrated V1 ATLAS runs 0038 / 0039 / 0040 on the measured grid,
0039 and 0040 scaled exactly to the recalibrated band mobility (make_figures.FINAL). Same extractor for both
(scripts/extract_metrics.py through make_figures.met, fixed_ss, mu_sat).
Output: figures/metrics_comparison_individual/metric_compare_{a..d}_*.{pdf,png}; prints every plotted value.
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_figures as mf  # noqa: E402
from style import HALF_W, panel_label  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

OUT = HERE.parent / 'figures' / 'metrics_comparison_individual'
OUT.mkdir(parents=True, exist_ok=True)
for old in OUT.glob('metric_compare_*'):
    old.unlink()
FILMS = mf.FILMS
C1, C2 = '#0072B2', '#D55E00'      # the original series colours (blue, orange)


def metric_set(vg, i, is_sim, t):
    m = mf.met(vg, i, is_sim, t)
    return dict(vcc=m['Vth_cc_1e-9_V'], vlin=m['Vth_lin_V'], ss1=mf.fixed_ss(vg, i, 1e-11, 1e-10), mufe=m['mu_FE_cm2Vs'],
                musat=float(np.nanmax(mf.mu_sat(vg, i)[vg > -0.5])), ion=m['Ion_A_per_um'])


meas, sim, ss_sub = {}, {}, {}
for t in FILMS:
    vg, i = mf.meas(t)
    meas[t] = metric_set(vg, i, False, t)
    ss_sub[t] = mf.fixed_ss(vg, i - mf.floor(vg, i), 1e-11, 1e-10)     # measured, off-state floor subtracted
    rid, s = mf.FINAL[t]
    vs, isim = mf.sim(rid, s)
    sim[t] = metric_set(vs, isim, True, t)
t = np.array(FILMS)
M = lambda k: [meas[x][k] for x in FILMS]
S = lambda k: [sim[x][k] for x in FILMS]
BOX = dict(fc='white', ec='none', alpha=0.85, pad=1.5)
TXT = dict(fontsize=5.6, linespacing=1.45, bbox=BOX)
LEG = dict(fontsize=5.6, frameon=True, framealpha=0.92, edgecolor='0.75', handlelength=1.8)


def fig_(letter, ylabel, log=False):
    fig, a = plt.subplots(figsize=(HALF_W, 2.55))
    panel_label(a, letter)
    a.set_xlabel('IWO thickness (nm)'); a.set_ylabel(ylabel); a.set_xticks(FILMS)
    if log:
        a.set_yscale('log')
    return fig, a


def pair(a, k, c, lab):
    a.plot(t, M(k), 'o-', color=c, ms=4, lw=1, label=f'{lab}, measured')
    a.plot(t, S(k), 's--', color=c, ms=5, lw=1, mfc='none', mew=1.1, label=f'{lab}, ATLAS')


def save(fig, name):
    fig.savefig(OUT / f'{name}.pdf')
    fig.savefig(OUT / f'{name}.png', dpi=300)
    plt.close(fig)


# (a) thresholds
fig, a = fig_('a', 'threshold (V)')
pair(a, 'vcc', C1, '$V_{th,cc}$'); pair(a, 'vlin', C2, '$V_{th,lin}$')
a.set_ylim(-0.05, 2.75)
a.legend(ncol=2, loc='upper center', **LEG)
a.text(0.04, 0.385, '$V_{th,cc}$: $V_G$ at $I_D = 10^{-9}$ A/$\\mu$m\n$V_{th,lin} = V_G^* - I_D(V_G^*)/g_{m,max}$\n'
       '$V_G^*$: $V_G$ of maximum $g_m$', transform=a.transAxes, va='center', **TXT)
save(fig, 'metric_compare_a_threshold')

# (b) subthreshold slope 1e-11..1e-10 A/um
fig, a = fig_('b', 'SS (mV/dec)')
pair(a, 'ss1', C1, '$SS_{[10^{-11},\\,10^{-10}]}$')
a.plot([13.2], [ss_sub[13.2]], 'D', color=C1, ms=4.5, mfc='none', mew=1.1, label='measured, floor subtracted')
a.set_ylim(80, 150)
a.legend(loc='lower left', **LEG)
a.text(0.04, 0.95, '$SS = \\Delta V_G\\,/\\,\\Delta\\log_{10} I_D$\nbetween $I_D = 10^{-11}$ and $10^{-10}$ A/$\\mu$m',
       transform=a.transAxes, va='top', **TXT)
save(fig, 'metric_compare_b_ss')

# (c) mobility
fig, a = fig_('c', r'mobility (cm$^2$/Vs)')
pair(a, 'mufe', C1, '$\\mu_{FE}$'); pair(a, 'musat', C2, '$\\mu_{sat}$')
a.set_ylim(0, 62)
a.legend(ncol=2, loc='upper left', **LEG)
a.text(0.04, 0.74, '$\\mu_{FE} = g_{m,max}\\,L\\,/\\,(W C_{ox} V_D)$\n$\\mu_{sat} = \\max\\,(2L/W C_{ox})\\,(\\partial\\sqrt{I_D}/\\partial V_G)^2$\n'
       '$L$ = 20 $\\mu$m, $V_D$ = 0.7 V\n$C_{ox}$ = 0.896 $\\mu$F/cm$^2$', transform=a.transAxes, va='top', **TXT)
save(fig, 'metric_compare_c_mobility')

# (d) on-current
fig, a = fig_('d', r'$I_{on}$ (A/$\mu$m)', log=True)
pair(a, 'ion', C1, '$I_{on}$')
a.legend(loc='lower right', **LEG)
a.text(0.04, 0.95, '$I_{on} = I_D(V_G = 3$ V$)$, $V_D$ = 0.7 V', transform=a.transAxes, va='top', **TXT)
save(fig, 'metric_compare_d_ion')

for k in ('vcc', 'vlin', 'ss1', 'mufe', 'musat', 'ion'):
    print(f'{k:6} measured', ' '.join(f'{v:.4g}' for v in M(k)), '| ATLAS', ' '.join(f'{v:.4g}' for v in S(k)))
print('ss1 measured, floor subtracted:', ' '.join(f'{ss_sub[x]:.4g}' for x in FILMS))
print('written to', OUT)
