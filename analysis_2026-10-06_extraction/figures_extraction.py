#!/usr/bin/env python3
"""Figures for PROTOCOL.md / RESULTS.md: how each quantity is extracted (threshold, SS, mobility versus V_G) and
the measured-versus-TCAD comparison panels. Reads the curves through run_extraction and the numbers from
results.json (run run_extraction.py first). Output: figures/*.png (300 dpi) and *.pdf.
"""
import json
import math
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

OUT = HERE / 'figures'
OUT.mkdir(exist_ok=True)
R = json.loads((HERE / 'results.json').read_text())
MEAS = rx.load_measured()
TC = {t: rx.load_tcad(t) for t in rx.FILMS}
BOX = dict(fc='white', ec='0.75', lw=0.5, alpha=0.95, pad=2.0)
TXT = dict(fontsize=6.2, linespacing=1.4, bbox=BOX)
LEG = dict(fontsize=6.2, frameon=True, framealpha=0.95, edgecolor='0.75', handlelength=1.8)
MK = dict(ls='none', marker='o', ms=3.0, mfc='none', mec='k', mew=0.7)


def fr(t):
    return R['films'][str(t)]


def save(fig, name):
    fig.savefig(OUT / f'{name}.pdf')
    fig.savefig(OUT / f'{name}.png', dpi=300)
    plt.close(fig)
    print('saved', name)


def letters(ax):
    for a, s in zip(ax.flat, 'abcdefghi'):
        panel_label(a, s, x=-0.27, y=1.03)


# ------------------------------------------------------------------ threshold
def fig_threshold():
    fig, ax = plt.subplots(2, 3, figsize=(7.2, 5.0), gridspec_kw=dict(hspace=0.42, wspace=0.42))
    for c, t in enumerate(rx.FILMS):
        vg, i = MEAS[t]; tc = TC[t]; f = fr(t); m, s = f['measured'], f['simulated']
        col = FILM[t]
        # (row 1) constant current
        a = ax[0, c]
        vcc, vcs = m['vth_cc']['v'], s['vth_cc']['v']
        a.semilogy(vg, i, label='measured', **MK)
        a.semilogy(tc['vg'], np.where(tc['i'] > 0, tc['i'], np.nan), '-', color=col, lw=1.3, label='TCAD')
        (v1, i1), (v2, i2) = m['vth_cc']['bracket']
        a.semilogy([v1, v2], [i1, i2], 'o', ms=3.4, color='k')
        a.semilogy([v1, v2], [i1, i2], '-', color='k', lw=0.6)
        a.axhline(rx.I_CC, color='0.35', lw=0.8, ls='--')
        a.plot([vcc], [rx.I_CC], marker='x', color='k', ms=6, mew=1.2)
        a.plot([vcs], [rx.I_CC], marker='x', color=col, ms=6, mew=1.2)
        a.set_xlim(vcc - 0.32, vcc + 0.32); a.set_ylim(1e-11, 1e-7)
        a.set_xlabel('$V_G$ (V)'); a.set_ylabel('$I_D$ (A/$\\mu$m)')
        a.set_title(f'{t:.1f} nm', fontsize=8.5)
        a.text(0.04, 0.96, f"$V_{{th,cc}}$ at $10^{{-9}}$ A/$\\mu$m\nmeas. {vcc:.3f} $\\pm$ {m['vth_cc']['sig']:.3f} V\n"
               f"TCAD {vcs:.3f} $\\pm$ {s['vth_cc']['sig']:.3f} V", transform=a.transAxes, va='top', **TXT)
        if c == 2:
            a.legend(loc='lower right', **LEG)
        # (row 2) linear extrapolation with -V_D/2, shown for completeness
        b = ax[1, c]
        b.plot(vg, i * 1e6, **MK)
        b.plot(tc['vg'], tc['i'] * 1e6, '-', color=col, lw=1.3)
        for e, cc in ((m['elr'], 'k'), (s['elr'], col)):
            i_star = e['gm_max'] * (e['vg_star'] - e['v_intercept'])
            b.plot([e['v_intercept'], e['vg_star']], [0, i_star * 1e6], '--', color=cc, lw=0.9)
            b.plot([e['v_intercept']], [0], 's', ms=3.6, mfc='white', mec=cc, mew=0.9)
            b.plot([e['v']], [0], '^', ms=4.2, color=cc)
        b.axhline(0, color='k', lw=0.5)
        top = 1.12 * max(i.max(), tc['i'].max()) * 1e6
        b.set_xlim(0, 3.08); b.set_ylim(-0.06 * top, top)
        b.set_xlabel('$V_G$ (V)'); b.set_ylabel('$I_D$ ($\\mu$A/$\\mu$m)')
        b.text(0.04, 0.96, f"$V_{{th,ELR}} = V_{{G,i}} - V_D/2$\nmeas. {m['elr']['v']:.3f} V\nTCAD {s['elr']['v']:.3f} V\n"
               f"$g_{{m,max}}$ at {m['elr']['vg_star']:.2f} / {s['elr']['vg_star']:.2f} V\n(sweep-limited)", transform=b.transAxes, va='top', **TXT)
        if c == 2:
            from matplotlib.lines import Line2D
            b.legend(handles=[Line2D([], [], ls='--', color='0.3', lw=0.9, label='tangent'),
                              Line2D([], [], ls='none', marker='s', ms=3.6, mfc='white', mec='0.3', label='$V_{G,i}$'),
                              Line2D([], [], ls='none', marker='^', ms=4.2, color='0.3', label='$V_{th,ELR}$')],
                     loc='lower right', **LEG)
    letters(ax)
    save(fig, 'fig1_threshold_extraction')


# ------------------------------------------------------------------ subthreshold swing
def fig_ss():
    fig, ax = plt.subplots(2, 3, figsize=(7.2, 5.0), gridspec_kw=dict(hspace=0.42, wspace=0.42))
    lo, hi = rx.WIN
    for c, t in enumerate(rx.FILMS):
        vg, i = MEAS[t]; tc = TC[t]; f = fr(t); m, s = f['measured'], f['simulated']; col = FILM[t]
        fl = f['floor']
        corrected = 'corrected' in m['ss']
        ms = m['ss']['corrected'] if corrected else m['ss']['raw']
        a = ax[0, c]
        a.axhspan(lo, hi, color='#DCE6F2', lw=0)
        a.semilogy(vg, i, label='measured', **MK)
        if corrected:
            ic = i - fl
            a.semilogy(vg, np.where(ic > 0, ic, np.nan), ls='none', marker='D', ms=2.6, mfc='none', mec='0.45', mew=0.7,
                       label='measured $-$ floor')
            a.axhline(fl, color='0.45', lw=0.8, ls=':')
            a.axhline(10 * fl, color='0.45', lw=0.8, ls='-.')
            a.text(0.97, fl * 1.25, 'floor', transform=a.get_yaxis_transform(), ha='right', fontsize=5.8, color='0.35')
            a.text(0.97, 10 * fl * 1.25, '10$\\times$floor', transform=a.get_yaxis_transform(), ha='right', fontsize=5.8, color='0.35')
        a.semilogy(tc['vg'], np.where(tc['i'] > 0, tc['i'], np.nan), '-', color=col, lw=1.3, label='TCAD')
        sr = s['ss']['raw']
        a.plot([sr['lo']['v'], sr['hi']['v']], [lo, hi], '+', color=col, ms=7, mew=1.2, zorder=5)
        a.plot([ms['lo']['v'], ms['hi']['v']], [lo, hi], 'x', color='k', ms=5.5, mew=1.1, zorder=6)
        x0, x1 = ms['lo']['v'] - 0.33, ms['hi']['v'] + 0.33
        a.set_xlim(x0, x1); a.set_ylim(1e-12, 1e-8)
        a.set_xlabel('$V_G$ (V)'); a.set_ylabel('$I_D$ (A/$\\mu$m)'); a.set_title(f'{t:.1f} nm', fontsize=8.5)
        lab = 'meas.' + (' (floor-corr.)' if corrected else '')
        if corrected:   # the upper left is taken by the legend; the lower right is empty for this film
            a.text(0.97, 0.04, f"SS (shaded window)\n{lab} {m['ss']['ss']:.1f} $\\pm$ {m['ss']['sig']:.1f}\n"
                   f"TCAD {s['ss']['ss']:.1f} $\\pm$ {s['ss']['sig']:.1f} mV/dec", transform=a.transAxes, ha='right', va='bottom', **TXT)
            a.legend(loc='upper left', **LEG)
        else:
            a.text(0.04, 0.96, f"SS (shaded window)\n{lab} {m['ss']['ss']:.1f} $\\pm$ {m['ss']['sig']:.1f}\n"
                   f"TCAD {s['ss']['ss']:.1f} $\\pm$ {s['ss']['sig']:.1f} mV/dec", transform=a.transAxes, va='top', **TXT)
        b = ax[1, c]
        b.axvspan(lo, hi, color='#DCE6F2', lw=0)
        x, y = ex.local_ss(vg, i)
        b.semilogx(x, y, **MK)
        if corrected:
            x2, y2 = ex.local_ss(vg, i - fl)
            b.semilogx(x2, y2, ls='none', marker='D', ms=2.6, mfc='none', mec='0.45', mew=0.7)
        xs, ys = ex.local_ss(tc['vg'], tc['i'])
        b.semilogx(xs, ys, '-', color=col, lw=1.3)
        b.axvline(fl, color='0.45', lw=0.8, ls=':'); b.axvline(10 * fl, color='0.45', lw=0.8, ls='-.')
        b.axhline(ex.S_TH, color='0.55', lw=0.7, ls='--')
        b.text(8e-9, ex.S_TH + 4, '$(kT/q)\\ln 10$', fontsize=5.8, color='0.4', ha='right', va='bottom')
        b.plot([lo, hi], [m['ss']['ss']] * 2, '-', color='k', lw=2.2, alpha=0.8)
        b.plot([lo, hi], [s['ss']['ss']] * 2, '-', color=col, lw=2.2, alpha=0.8)
        b.set_xlim(1e-13, 1e-8); b.set_ylim(40, 320)
        b.set_xlabel('$I_D$ (A/$\\mu$m)'); b.set_ylabel('local SS (mV/dec)')
        from matplotlib.lines import Line2D
        if c == 0:
            b.legend(handles=[Line2D([], [], label='measured', **MK), Line2D([], [], color=col, lw=1.3, label='TCAD')],
                     loc='upper left', **LEG)
        if c == 2:
            b.legend(handles=[Line2D([], [], color='0.45', lw=0.8, ls=':', label='measured floor'),
                              Line2D([], [], color='0.45', lw=0.8, ls='-.', label='10 $\\times$ floor')], loc='upper left', **LEG)
    letters(ax)
    save(fig, 'fig2_ss_extraction')


# ------------------------------------------------------------------ mobility versus V_G
def fig_mobility():
    fig, ax = plt.subplots(2, 3, figsize=(7.2, 5.0), gridspec_kw=dict(hspace=0.42, wspace=0.42))
    for c, t in enumerate(rx.FILMS):
        vg, i = MEAS[t]; tc = TC[t]; f = fr(t); m, s = f['measured'], f['simulated']; col = FILM[t]
        mu_n = f['tcad']['mu_n']
        _, sig_pts = ex.gm_sigma(vg, i)
        k = (vg >= 1.0 - 1e-9) & (vg <= 3.0 + 1e-9)
        mu = ex.MU_FACTOR * ex.gm(vg, i)
        a = ax[0, c]
        a.errorbar(vg[k], mu[k], yerr=ex.MU_FACTOR * sig_pts[k], fmt='o', ms=3.0, mfc='none', mec='k', mew=0.7, ecolor='0.4',
                   elinewidth=0.6, capsize=0, label='measured')
        ks = (tc['vg'] >= 1.0 - 1e-9) & (tc['vg'] <= 3.0 + 1e-9)
        a.plot(tc['vg'][ks], ex.MU_FACTOR * ex.gm(tc['vg'], tc['i'])[ks], '-', color=col, lw=1.3, label='TCAD')
        a.axhline(mu_n, color=col, lw=0.8, ls=':')
        a.set_xlim(0.95, 3.05); a.set_ylim(0, 1.18 * max(mu_n, mu[k].max()))
        a.text(1.02, mu_n * 1.02, f'TCAD $\\mu_n$ = {mu_n:.1f}', fontsize=5.8, color=col, va='bottom')
        a.set_xlabel('$V_G$ (V)'); a.set_ylabel('$\\mu_{FE}$ (cm$^2$/Vs)'); a.set_title(f'{t:.1f} nm', fontsize=8.5)
        if c == 0:
            a.legend(loc='lower right', **LEG)
        b = ax[1, c]
        xx = np.linspace(1.0, 3.0, 201)
        for r, cc, lab in ((m, 'k', 'measured'), (s, col, 'TCAD')):
            curves = np.array([ex.mu_ch(xx, q) for q in [r['pl']] + r['pl_alt']])
            b.fill_between(xx, np.nanmin(curves, axis=0), np.nanmax(curves, axis=0), color=cc, alpha=0.13, lw=0)
            b.plot(xx, curves[0], '--' if cc == 'k' else '-', color=cc, lw=1.2,
                   label=f"{'meas.' if cc == 'k' else 'TCAD'}: $\\gamma$ {r['pl']['gamma']:.2f}, $V_T$ {r['pl']['vt']:.2f} V")
        b.axhline(mu_n, color=col, lw=0.8, ls=':')
        b.text(1.02, mu_n * 1.02, f'TCAD $\\mu_n$ = {mu_n:.1f}', fontsize=5.8, color=col, va='bottom')
        b.set_xlim(0.95, 3.05); b.set_ylim(0, 1.62 * mu_n)
        b.set_xlabel('$V_G$ (V)'); b.set_ylabel('$\\mu_{ch}$ (cm$^2$/Vs)')
        b.legend(loc='upper center', **LEG)
    letters(ax)
    save(fig, 'fig3_mobility_vs_vg')


# ------------------------------------------------------------------ comparison panels
def comparison_panels():
    t = np.array(rx.FILMS)
    C1, C2 = '#0072B2', '#D55E00'

    def new(letter, ylabel):
        fig, a = plt.subplots(figsize=(HALF_W, 2.55))
        panel_label(a, letter)
        a.set_xlabel('IWO thickness (nm)'); a.set_ylabel(ylabel); a.set_xticks(rx.FILMS)
        return fig, a

    def pair(a, mv, ms, sv, ss, c, lab):
        a.errorbar(t, mv, yerr=ms, fmt='o-', color=c, ms=4, lw=1, capsize=2, elinewidth=0.8, label=f'{lab}, measured')
        a.errorbar(t, sv, yerr=ss, fmt='s--', color=c, ms=5, lw=1, mfc='none', mew=1.1, capsize=2, elinewidth=0.8, label=f'{lab}, TCAD')

    g = lambda src, path: [eval(f"fr(x)['{src}']" + path) for x in rx.FILMS]
    fig, a = new('a', 'threshold voltage (V)')
    pair(a, g('measured', "['vth_cc']['v']"), g('measured', "['vth_cc']['sig']"), g('simulated', "['vth_cc']['v']"),
         g('simulated', "['vth_cc']['sig']"), C1, '$V_{th,cc}$')
    a.set_ylim(-0.1, 0.9); a.legend(loc='lower left', **LEG)
    a.text(0.96, 0.95, '$I_D = 10^{-9}$ A/$\\mu$m ($I_DL/W$ = 20 nA)\n$V_D$ = 0.7 V', transform=a.transAxes, ha='right', va='top', **TXT)
    save(fig, 'compare_a_threshold')

    fig, a = new('b', 'SS (mV/dec)')
    pair(a, g('measured', "['ss']['ss']"), g('measured', "['ss']['sig']"), g('simulated', "['ss']['ss']"),
         g('simulated', "['ss']['sig']"), C1, 'SS')
    raw = fr(13.2)['measured']['ss']['raw']
    a.errorbar([13.2], [raw['ss']], yerr=[raw['sig']], fmt='D', color=C1, ms=4.5, mfc='none', mew=1.0, capsize=2,
               label='measured, without floor correction')
    a.set_ylim(80, 210); a.legend(loc='lower left', **LEG)
    a.text(0.96, 0.95, 'window $5\\times10^{-11}$-$5\\times10^{-10}$ A/$\\mu$m', transform=a.transAxes, ha='right', va='top', **TXT)
    save(fig, 'compare_b_ss')

    fig, a = new('c', '$\\mu_{FE}$ (cm$^2$/Vs)')
    for v, c in (('2.0', C1), ('3.0', C2)):
        pair(a, g('measured', f"['mu_fe']['{v}']['mu_fe']"), g('measured', f"['mu_fe']['{v}']['sig']"),
             g('simulated', f"['mu_fe']['{v}']['mu_fe']"), g('simulated', f"['mu_fe']['{v}']['sig']"), c, f'$V_G$ = {v[0]} V')
    a.set_ylim(0, 62); a.legend(loc='upper left', ncol=2, **LEG)
    save(fig, 'compare_c_mobility')

    fig, a = new('d', 'power-law exponent $\\gamma$')
    pair(a, g('measured', "['pl']['gamma']"), g('measured', "['pl']['tot_gamma']"), g('simulated', "['pl']['gamma']"),
         g('simulated', "['pl']['tot_gamma']"), C1, '$\\gamma$')
    a.set_ylim(-0.2, 1.8); a.legend(loc='upper right', **LEG)
    a.text(0.04, 0.05, '$\\mu_{ch}=\\mu_0(V_G-V_T)^{\\gamma}$, fit 1-3 V\nerror bars: statistical + fit range', transform=a.transAxes,
           va='bottom', **TXT)
    save(fig, 'compare_d_gamma')


if __name__ == '__main__':
    fig_threshold()
    fig_ss()
    fig_mobility()
    comparison_panels()
