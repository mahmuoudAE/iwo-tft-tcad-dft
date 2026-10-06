#!/usr/bin/env python3
"""The five panels of the V1 thickness-law figure (make_figures.thickness_laws) as individual figures, each with its
references and, for Nt and Nd_eff, their definitions written on the figure (user request 2026-10-06).
Same laws and data points as the combined figure:
  laws  config/iwo_material_model.yaml (V1), fitted in scripts/material_laws.py
  data  tables/THICKNESS_LAW_EVIDENCE.csv (Lin 2022, Si 2021, Stokey 2021, Januar 2026);
        S3 Schroedinger-Poisson shifts (analysis_2026-09-25/scratch/S3/s3_sp1d_notraps_out.txt);
        surface + bulk Nt alternative (analysis_2026-09-25/S4_defects_traps.md, line 40)
Output: figures/thickness_laws_individual/thickness_law_{a..e}_*.{png,pdf}
"""
import sys
import textwrap
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'figures' / 'src'))
from style import *  # noqa: F401,F403  (plt, ACCENT, ACCENT2, GREY, FILM, ...)
import matplotlib.pyplot as plt

OUT = HERE.parent / 'figures' / 'thickness_laws_individual'
OUT.mkdir(parents=True, exist_ok=True)
Q = 1.602176634e-19; HB = 1.054571817e-34; ME = 9.1093837015e-31
T = np.linspace(0.9, 32, 400)
FILMS = [(2.0, FILM[2.0]), (6.3, FILM[6.3]), (13.2, FILM[13.2])]
REF = {
    'Lin': 'Lin et al., ACS Nano 16, 21536 (2022)',
    'Si': 'Si et al., Nano Lett. 21, 500 (2021)',
    'Stokey': 'Stokey et al., J. Appl. Phys. 129, 225102 (2021)',
    'Januar': 'Januar et al., Small Struct. 7, e202500807 (2026)',
    'Kim': 'Kim et al., Appl. Phys. Lett. 125, 173507 (2024)',
}


def frame(title, xlabel, ylabel, logx=True, logy=False):
    fig = plt.figure(figsize=(6.2, 5.2))
    ax = fig.add_axes([0.13, 0.43, 0.82, 0.50])
    ax.set_title(title, fontsize=9.5, loc='left')
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    if logx:
        ax.set_xscale('log')
    if logy:
        ax.set_yscale('log')
    for t, c in FILMS:
        ax.axvline(t, color=c, lw=0.7, ls=':')
    return fig, ax


def wrap_keep_math(text, width):
    """Greedy word wrap that never breaks inside a $...$ formula (a broken formula prints raw LaTeX)."""
    import re
    words, merged, buf = text.split(' '), [], None
    for w in words:
        if buf is None:
            if w.count('$') % 2:
                buf = w
            else:
                merged.append(w)
        else:
            buf += ' ' + w
            if w.count('$') % 2:
                merged.append(buf); buf = None
    if buf:
        merged.append(buf)

    def vis(w):   # rough printed width: commands count as their name, braces and ^ _ $ as nothing
        return len(re.sub(r'[{}^_$\\]', '', w))
    lines, cur, n = [], [], 0
    for w in merged:
        k = vis(w)
        if cur and n + 1 + k > width:
            lines.append(' '.join(cur)); cur, n = [w], k
        else:
            n = n + 1 + k if cur else k; cur.append(w)
    if cur:
        lines.append(' '.join(cur))
    return lines


def note(fig, blocks):
    """blocks: list of (heading, text); written below the axes, wrapped without splitting formulas."""
    y = 0.30
    for head, text in blocks:
        fig.text(0.04, y, head, fontsize=7.6, fontweight='bold', va='top')
        lines = wrap_keep_math(text, 104)
        fig.text(0.04, y - 0.028, '\n'.join(lines), fontsize=7.0, va='top', linespacing=1.35)
        y -= 0.028 + 0.0255 * len(lines) + 0.022


def save(fig, name):
    for ext in ('png', 'pdf'):
        fig.savefig(OUT / f'{name}.{ext}', dpi=220)
    plt.close(fig)


# (a) conduction-band confinement shift ------------------------------------------------------------------------------
fig, ax = frame('(a) Conduction-band confinement shift $\\Delta E_c(t)$, model V1', 'IWO thickness $t$ (nm)', '$\\Delta E_c$ (eV)', logy=True)
ax.plot(T, 0.9205 * T ** -1.3815, color=ACCENT, lw=1.6, label='V1 law $0.9205\\,t^{-1.3815}$ eV')
for m, ls in [(0.18, ':'), (0.26, '--'), (0.35, '-.')]:
    ax.plot(T, (HB * np.pi) ** 2 / (2 * m * ME * (T * 1e-9) ** 2) / Q, ls, color=GREY, lw=0.9, label=f'infinite well, $m^*$ = {m} $m_0$')
ax.plot([0.95, 1.98], [0.94, 0.33], 'o', color='k', ms=5, label='Lin 2022, PBE slabs [1]')
ax.plot([1.5], [0.6], 's', color='k', ms=5, label='Si 2021, PBE [2]')
ax.plot([2.0, 6.3, 13.2], [0.2556, 0.0359, 0.016], 'D', color=ACCENT2, ms=4.5, label='Schrodinger-Poisson equivalent (S3)')
ax.set_ylim(3e-3, 3); ax.legend(fontsize=6.6, loc='upper right', framealpha=0.92)
note(fig, [('What is plotted',
            'The upward shift of the conduction-band edge of a thin film relative to bulk. V1 law: log-log fit through the three '
            'DFT points. Grey: lowest level of an infinite square well, $E_1 = \\hbar^2\\pi^2/(2m^*t^2)$, the large-$t$ limit; above '
            'about 3 nm the V1 power law lies above it. Diamonds: shifts equivalent in subthreshold to a 1-D Schrodinger-Poisson '
            'solution (specialist study S3, case Q1, $n_s = 10^{10}$ cm$^{-2}$). Dotted lines: the measured films 2.0 / 6.3 / 13.2 nm.'),
           ('References',
            f'[1] {REF["Lin"]}, p. 21542: PBE gap opening +0.94 eV (0.95 nm) and +0.33 eV (1.98 nm).  '
            f'[2] {REF["Si"]}, p. 504: PBE conduction-band shift +0.60 eV for 1.5 nm In$_2$O$_3$ on Al$_2$O$_3$.  '
            'Both are pure In$_2$O$_3$ used as a proxy for IWO.')])
save(fig, 'thickness_law_a_dEc')

# (b) effective mass ---------------------------------------------------------------------------------------------------
fig, ax = frame('(b) Electron effective mass $m^*(t)$, model V1', 'IWO thickness $t$ (nm)', '$m^*/m_0$')
ax.plot(T, 0.208 + 0.1311 * T ** -1.412, color=ACCENT, lw=1.6, label='V1 law $0.208 + 0.1311\\,t^{-1.412}$')
ax.axhline(0.208, color=GREY, lw=0.9, ls='--', label='bulk 0.208 $m_0$, measured [1]')
pts = [(0.95, 0.30), (1.98, 0.23), (3.52, 0.19)]
ax.plot([t for t, _ in pts], [0.208 + m - 0.17 for _, m in pts], 'o', color='k', ms=5, label='0.208 + PBE slab increment [2]')
for t, m in pts:
    ax.annotate(f'{m:.2f} $-$ 0.17 = +{m - 0.17:.2f}', (t, 0.208 + m - 0.17), textcoords='offset points', xytext=(7, 3), fontsize=6.4)
ax.set_ylim(0.19, 0.37); ax.legend(fontsize=6.8, loc='upper right', framealpha=0.92)
note(fig, [('What is plotted',
            'Effective mass of the conduction electrons. The bulk value is a measurement; only the change with thickness is taken '
            'from DFT: each dot is 0.208 $m_0$ plus the PBE slab mass minus the PBE bulk mass of [2] (written next to each dot). '
            'The curve is a log-log fit through these three increments (scripts/material_laws.py). In ATLAS the mass enters only '
            'through the conduction-band density of states, $N_c \\propto (m^*)^{3/2}$.'),
           ('References',
            f'[1] {REF["Stokey"]}: 0.208 $m_0$ from optical Hall measurements on an In$_2$O$_3$ single crystal '
            '($n = 2.8\\times10^{17}$ cm$^{-3}$), Abstract and Sec. IV.C.  '
            f'[2] {REF["Lin"]}, p. 21540: PBE masses 0.30 / 0.23 / 0.19 $m_0$ for 0.95 / 1.98 / 3.52 nm slabs and 0.17 $m_0$ for bulk.')])
save(fig, 'thickness_law_b_mstar')

# (c) tail-state density -----------------------------------------------------------------------------------------------
fig, ax = frame('(c) Band-tail trap density $N_t(t)$, model V1', 'IWO thickness $t$ (nm)', '$N_t$ (cm$^{-3}$)', logy=True)
ax.plot(T, 2e19 * (2 / T) ** 0.75, color=ACCENT, lw=1.6, label='V1 law $2\\times10^{19}\\,(2/t)^{0.75}$')
ax.plot(T, 2.15e18 + 3.57e12 / (T * 1e-7), '--', color=ACCENT2, lw=1.3, label='surface + bulk alternative')
ax.plot([2.0, 10.0], [5.3e19, 3.39e18], 's', color='k', ms=5, label='Januar 2026, PBS devices [1]')
ax.legend(fontsize=6.8, loc='upper right', framealpha=0.92)
note(fig, [('Definition',
            '$N_t$ is the total density of acceptor-like band-tail states below the conduction-band edge. Their density of states '
            'is $g_{TA}(E) = N_{TA}\\,\\exp[(E-E_c)/W_{TA}]$, so $N_t = \\int g_{TA}\\,dE \\approx N_{TA}W_{TA}$ with the shared width '
            '$W_{TA}$ = 40 meV ($T_t$ = 464 K). ATLAS receives $N_{TA} = N_t/W_{TA}$ (DEFECTS statement). Electrons trapped in these '
            'states do not conduct; their filling sets the subthreshold slope and part of the threshold.'),
           ('Source of the curves',
            'V1 law: FITTED - anchored on the 2 nm ATLAS fit; exponent 0.75 from the ~4x ratio between 13.2 and 2 nm reported '
            'in [1]. Surface + bulk alternative: $N_t = N_b + N_s/t$ through the same anchors, $N_b = 2.15\\times10^{18}$ cm$^{-3}$, '
            '$N_s = 3.57\\times10^{12}$ cm$^{-2}$ (specialist study S4); it differs by 8 % at 6.3 nm.'),
           ('References',
            f'[1] {REF["Januar"]}, p. 9 (compact-model extraction on separate PBS devices, unstressed) and Sec. 2.8 / Fig. 5a.')])
save(fig, 'thickness_law_c_Nt')

# (d) effective donor density ------------------------------------------------------------------------------------------
fig, ax = frame('(d) Effective donor density $N_{d,eff}(t)$, model V1', 'IWO thickness $t$ (nm)', '$N_{d,eff}$ (cm$^{-3}$)', logx=False, logy=True)
ax.plot(T, 2.5e17 * (1 + (T / 20) ** 4), color=ACCENT, lw=1.6, label='V1 law $2.5\\times10^{17}\\,[1+(t/20\\,\\mathrm{nm})^4]$')
for t, c in FILMS:
    v = 2.5e17 * (1 + (t / 20) ** 4)
    ax.plot(t, v, 'o', color=c, ms=5)
    m, e = f'{v:.2e}'.split('e')
    ax.annotate(f'{m}$\\times10^{{{int(e)}}}$', (t, v), textcoords='offset points', xytext=(-4, 9), fontsize=6.4, ha='center')
ax.set_ylim(2e17, 2.6e18); ax.legend(fontsize=6.8, loc='upper left', framealpha=0.92)
note(fig, [('Definition',
            '$N_{d,eff}$ is the density of electrically active, fully ionized background donors, spread uniformly through the film '
            '(ATLAS DOPING, n-type). It lumps every net source of free electrons - W donors left after compensation, oxygen vacancies, '
            'hydrogen - into one number. It is NOT the W concentration: about 2 % W corresponds to roughly $10^{20}$-$10^{21}$ cm$^{-3}$ '
            'atoms, so almost all W donors must be compensated in these films.'),
           ('Source of the curve',
            'FITTED law (no direct measurement): nearly flat up to ~10 nm and steep beyond, to describe the thick, always-on 31.8 nm '
            'film. Its effect on the threshold is small for the thin films: $qN_{d,eff}t/C_{ox}$ = 0.009 / 0.028 / 0.070 V at '
            '2 / 6.3 / 13.2 nm. Qualitative support only: trap densities rising with thickness in a different IWO process [1].'),
           ('References', f'[1] {REF["Kim"]}.')])
save(fig, 'thickness_law_d_Nd')

# (e) roughness factor -------------------------------------------------------------------------------------------------
fig, ax = frame('(e) Surface-roughness mobility factor, model V1', 'IWO thickness $t$ (nm)', '$(1-\\Delta_{sr}/t)^2$')
ax.plot(T, (1 - 0.287 / T) ** 2, color=ACCENT, lw=1.6, label='$(1-\\Delta_{sr}/t)^2$, $\\Delta_{sr}$ = 2.87 Å [1]')
for t, c in FILMS:
    v = (1 - 0.287 / t) ** 2
    ax.plot(t, v, 'o', color=c, ms=5)
    ax.annotate(f'{v:.3f}', (t, v), textcoords='offset points', xytext=(5, -11), fontsize=6.4)
ax.set_ylim(0.4, 1.02); ax.legend(fontsize=6.8, loc='lower right', framealpha=0.92)
note(fig, [('What is plotted',
            'Factor by which surface roughness reduces the mobility of a thin film: the ATLAS mobility is '
            '$\\mu_0 = \\mu_{band}\\,(1-\\Delta_{sr}/t)^2$. Values at the measured films: 0.734 / 0.911 / 0.957.'),
           ('References', f'[1] {REF["Januar"]}, Sec. 2.9 and Fig. 5f: effective roughness $\\Delta_{{sr}}$ = 2.87 Å from the fit of mobility against thickness.')])
save(fig, 'thickness_law_e_roughness')
print('written to', OUT)
