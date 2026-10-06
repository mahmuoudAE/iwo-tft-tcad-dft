#!/usr/bin/env python3
"""The five panels of the measured-metrics figure (make_figures.measured_metrics) as individual figures, with the same
data, extractor and style. Changes against the combined figure (user request, 2026-10-06): panel (b) shows only the
fixed-current slope between 1e-11 and 1e-10 A/um, and each panel carries the formula of its metric.
Output: figures/measured_metrics_individual/measured_metric_{a..e}_*.{pdf,png}; prints the plotted values.
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_figures as mf  # noqa: E402  (meas, met, fixed_ss, mu_sat, floor, FILMS; style loaded through it)
from style import HALF_W, panel_label  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

OUT = HERE.parent / 'figures' / 'measured_metrics_individual'
OUT.mkdir(parents=True, exist_ok=True)
for old in OUT.glob('measured_metric_*'):
    old.unlink()
FILMS = mf.FILMS
rows = {}
for t in FILMS:
    vg, i = mf.meas(t); m = mf.met(vg, i, False, t)
    rows[t] = dict(vcc=m['Vth_cc_1e-9_V'], vlin=m['Vth_lin_V'], ss1=mf.fixed_ss(vg, i, 1e-11, 1e-10), mufe=m['mu_FE_cm2Vs'],
                   musat=float(np.nanmax(mf.mu_sat(vg, i)[vg > -0.5])), ion=m['Ion_A_per_um'], fl=mf.floor(vg, i))
t = np.array(FILMS)
g = lambda k: [rows[x][k] for x in FILMS]
BOX = dict(fc='white', ec='none', alpha=0.85, pad=1.5)
TXT = dict(fontsize=5.8, linespacing=1.45, bbox=BOX)


def panel(letter, ylabel, series, log=False, legend=None):
    fig, a = plt.subplots(figsize=(HALF_W, 2.55))
    panel_label(a, letter)
    for k, lab in series:
        a.plot(t, g(k), 'o-', ms=4, lw=1, label=lab)
    a.set_xlabel('IWO thickness (nm)'); a.set_ylabel(ylabel); a.set_xticks(FILMS)
    if log:
        a.set_yscale('log')
    if legend:
        a.legend(fontsize=6.5, loc=legend)
    return fig, a


def save(fig, name):
    fig.savefig(OUT / f'{name}.pdf')
    fig.savefig(OUT / f'{name}.png', dpi=300)
    plt.close(fig)


# (a) thresholds
fig, a = panel('a', 'threshold (V)', [('vcc', r'$V_{th,cc}$'), ('vlin', r'$V_{th,lin}$')], legend='lower left')
a.text(0.04, 0.5, '$V_{th,cc}$: $V_G$ at $I_D = 10^{-9}$ A/$\\mu$m\n$V_{th,lin} = V_G^* - I_D(V_G^*)/g_{m,max}$\n'
       '$V_G^*$: $V_G$ of maximum $g_m$', transform=a.transAxes, va='center', **TXT)
a.set_ylim(-0.05, 2.25)
save(fig, 'measured_metric_a_threshold')

# (b) subthreshold slope, fixed-current window only
fig, a = panel('b', 'SS (mV/dec)', [('ss1', r'$SS_{[10^{-11},\,10^{-10}]}$')], legend='lower right')
a.text(0.04, 0.95, '$SS = \\Delta V_G\\,/\\,\\Delta\\log_{10} I_D$\nbetween $I_D = 10^{-11}$ and $10^{-10}$ A/$\\mu$m',
       transform=a.transAxes, va='top', **TXT)
a.set_ylim(110, 145)
save(fig, 'measured_metric_b_ss')

# (c) mobility
fig, a = panel('c', r'mobility (cm$^2$/Vs)', [('mufe', r'$\mu_{FE}$ (linear)'), ('musat', 'saturation formula')], legend='upper left')
a.text(0.04, 0.78, '$\\mu_{FE} = g_{m,max}\\,L\\,/\\,(W C_{ox} V_D)$\n$\\mu_{sat} = \\max\\,(2L/W C_{ox})\\,(\\partial\\sqrt{I_D}/\\partial V_G)^2$\n'
       '$L$ = 20 $\\mu$m, $V_D$ = 0.7 V\n$C_{ox}$ = 0.896 $\\mu$F/cm$^2$', transform=a.transAxes, va='top', **TXT)
save(fig, 'measured_metric_c_mobility')

# (d) on-current
fig, a = panel('d', r'$I_{on}$ (A/$\mu$m)', [('ion', r'$I_{on}$ at 3 V')], log=True)
a.text(0.04, 0.95, '$I_{on} = I_D(V_G = 3$ V$)$, $V_D$ = 0.7 V', transform=a.transAxes, va='top', **TXT)
save(fig, 'measured_metric_d_ion')

# (e) off-state floor
fig, a = panel('e', r'off-floor (A/$\mu$m)', [('fl', 'off-band median')], log=True)
a.text(0.04, 0.95, 'off-floor = median of $I_D$\nover $-2 \\leq V_G \\leq -0.5$ V', transform=a.transAxes, va='top', **TXT)
save(fig, 'measured_metric_e_floor')

for k in ('vcc', 'vlin', 'ss1', 'mufe', 'musat', 'ion', 'fl'):
    print(k, ' '.join(f'{v:.4g}' for v in g(k)))
print('written to', OUT)
