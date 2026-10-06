#!/usr/bin/env python3
"""Where the traps are in the V1 TCAD device and how each one is defined and computed.
All parameters are parsed from the device.in decks of the final runs 0038 / 0039 / 0040; the trap tables that ATLAS
wrote (acceptor_r1.dat, acceptor_r2.dat) are overlaid as a check. Output: figures/trap_locations, trap_dos, trap_occupancy
(.png/.pdf) and trap_parameters.json.
"""
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(PKG / 'report_latex_full' / 'figures' / 'src'))
from style import plt, FILM  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

OUT = HERE / 'figures'
OUT.mkdir(exist_ok=True)
RUNS = {2.0: 'run_0038_*', 6.3: 'run_0039_*', 13.2: 'run_0040_*'}
KT = 0.025852  # eV at 300 K


def run_dir(t):
    return next((PKG / 'results' / 'runs').glob(RUNS[t]))


def parse(t):
    txt = (run_dir(t) / 'device.in').read_text()
    lines = txt.replace('\\\n', ' ').splitlines()
    p = {}
    for ln in lines:
        s = ln.strip()
        m = re.match(r'defects region=(\d)', s)
        if m:
            reg = int(m.group(1))
            for key in ('nta', 'wta', 'nga', 'ega', 'wga', 'ntd', 'ngd', 'sigtae'):
                v = re.search(rf'\b{key}=([0-9.eE+-]+)', s)
                p[f'{key}_r{reg}'] = float(v.group(1))
        if s.startswith('interface') and 'qf=' in s:
            p['qf'] = float(re.search(r'qf=([0-9.eE+-]+)', s).group(1))
        if s.startswith('doping uniform') and 'region=1' in s:
            p['nd'] = float(re.search(r'conc=([0-9.eE+-]+)', s).group(1))
        if s.startswith('region num=1'):
            p['t_r1_nm'] = -1e3 * float(re.search(r'y.min=([0-9.eE+-]+)', s).group(1)) - 0.25
        if s.startswith('region num=2'):
            p['t_r2_nm'] = 1e3 * (float(re.search(r'y.max=([0-9.eE+-]+)', s).group(1)) - float(re.search(r'y.min=([0-9.eE+-]+)', s).group(1)))
        if 'eg300=' in s:
            p['eg'] = float(re.search(r'eg300=([0-9.eE+-]+)', s).group(1))
    p['thickness_nm'] = t
    p['Nt_tail_cm3'] = p['nta_r1'] * p['wta_r1']                         # N_TA W_TA
    p['tail_sheet_cm2'] = p['Nt_tail_cm3'] * t * 1e-7
    p['deep_total_cm3'] = math.sqrt(math.pi) * p['nga_r1'] * p['wga_r1']
    p['deep_sheet_cm2'] = p['deep_total_cm3'] * p['t_r1_nm'] * 1e-7
    p['dit_peak_cm2eV'] = p['nga_r2'] * p['t_r2_nm'] * 1e-7              # sheet = volume density x 0.25 nm
    p['dit_total_cm2'] = math.sqrt(math.pi) * p['dit_peak_cm2eV'] * p['wga_r2']
    return p


def atlas_table(t, reg):
    rows = [l.split()[1:] for l in (run_dir(t) / f'acceptor_r{reg}.dat').read_text().splitlines() if l.startswith('d ')]
    a = np.array(rows, float)
    return a[:, 0], a[:, 1], a[:, 2]          # energy below Ec (eV), tail, Gaussian (cm^-3 eV^-1)


P = {t: parse(t) for t in RUNS}
(HERE / 'trap_parameters.json').write_text(json.dumps({str(k): v for k, v in P.items()}, indent=1))
p2 = P[2.0]

# ------------------------------------------------------------------ figure 1: locations in the device
fig, ax = plt.subplots(figsize=(7.4, 3.7))
ax.set_xlim(-7.5, 46); ax.set_ylim(-0.9, 7.2); ax.axis('off')
layers = [(0.0, 1.2, '#9AA3AD', 'TiN gate, 50 nm'), (1.2, 2.7, '#C9D7E8', 'HfO$_2$, 15 nm'),
          (2.7, 3.25, '#E7EEF6', 'Al$_2$O$_3$, 2 nm'), (3.25, 4.75, '#F3C89B', '')]
for y0, y1, c, lab in layers:
    ax.add_patch(Rectangle((0, y0), 24, y1 - y0, fc=c, ec='k', lw=0.6))
    if lab:
        ax.text(12, (y0 + y1) / 2, lab, ha='center', va='center', fontsize=7.5)
r2 = (3.25, 3.55)   # region 2 drawn enlarged
ax.add_patch(Rectangle((0, r2[0]), 24, r2[1] - r2[0], fc='#E8A0C8', ec='k', lw=0.5, hatch='////'))
for x0 in (0, 21.5):
    ax.add_patch(Rectangle((x0, 4.75), 2.5, 1.3, fc='#B0B4BA', ec='k', lw=0.6, hatch='\\\\'))
ax.text(1.25, 6.25, 'Pd S', ha='center', fontsize=6.5); ax.text(22.75, 6.25, 'Pd D', ha='center', fontsize=6.5)
ax.text(12, 5.45, 'air (no passivation)', ha='center', va='center', fontsize=7, style='italic', color='0.35')
ax.text(12, 4.15, 'IWO channel, $t$ = 2.0 / 6.3 / 13.2 nm', ha='center', va='center', fontsize=7.2,
        bbox=dict(fc='#F3C89B', ec='none', pad=0.5))
rng = np.random.default_rng(3)
xs = np.r_[rng.uniform(1.0, 23.0, 22), rng.uniform(1.0, 23.0, 14)]
ys = np.r_[rng.uniform(4.40, 4.68, 22), rng.uniform(3.62, 3.90, 14)]
ok = ~((xs > 4.0) & (xs < 20.0) & (ys > 3.95) & (ys < 4.38))
ax.plot(xs[ok], ys[ok], ls='none', marker='_', ms=5, mew=1.2, color='#C0392B')                       # tail (whole film)
ax.plot([3.0, 7.5, 16.5, 20.5, 11.0, 2.0], [4.55, 3.75, 3.80, 4.55, 4.60, 3.72], ls='none', marker='D', ms=3.2, color='#6C3483')
ax.plot(np.linspace(1.0, 23.0, 23), np.full(23, 3.40), ls='none', marker='x', ms=3.5, mew=0.9, color='#1A5276')  # D_it
ax.plot(np.linspace(0.6, 23.4, 30), np.full(30, 3.25), ls='none', marker='+', ms=5, mew=1.1, color='#117A65')   # Q_f
# region brackets on the left
for (y0, y1, lab) in ((3.55, 4.75, 'region 1\n(bulk IWO)'), (3.25, 3.55, 'region 2: 0.25 nm\n(drawn enlarged)')):
    ax.plot([-0.4, -0.7, -0.7, -0.4], [y0 + 0.03, y0 + 0.03, y1 - 0.03, y1 - 0.03], color='0.3', lw=0.7)
    ax.text(-0.95, (y0 + y1) / 2, lab, ha='right', va='center', fontsize=6.2, color='0.25', linespacing=1.2)
ax.annotate('IWO/Al$_2$O$_3$\ninterface', (-0.2, 3.25), xytext=(-0.95, 2.65), ha='right', va='center', fontsize=6.2, color='0.25',
            arrowprops=dict(arrowstyle='-', lw=0.6, color='0.3'))
info = [
    ('#C0392B', dict(marker='_', ms=7, mew=1.6), 'Acceptor-like band tail, whole IWO film',
     f"$g_{{TA}}=N_{{TA}}\\,e^{{-(E_c-E)/W_{{TA}}}}$, $W_{{TA}}$ = {1e3 * p2['wta_r1']:.0f} meV\n"
     f"$N_t=N_{{TA}}W_{{TA}}$ = 2.0 / 0.85 / 0.49 $\\times10^{{19}}$ cm$^{{-3}}$ (fitted at 2 nm, law in $t$)"),
    ('#6C3483', dict(marker='D', ms=4), 'Deep acceptor Gaussian, region 1',
     f"$E_c-{p2['ega_r1']:.1f}$ eV, width {p2['wga_r1']:.2f} eV, {p2['deep_total_cm3']:.1e} cm$^{{-3}}$ in total (assumed)"),
    ('#1A5276', dict(marker='x', ms=5, mew=1.2), 'Interface acceptor states $D_{it}$, region 2',
     f"$E_c-{p2['ega_r2']:.2f}$ eV, peak {p2['dit_peak_cm2eV']:.1e} cm$^{{-2}}$eV$^{{-1}}$, {p2['dit_total_cm2']:.1e} cm$^{{-2}}$ (assumed)"),
    ('#117A65', dict(marker='+', ms=7, mew=1.4), 'Fixed positive charge $Q_f$ at the interface (not a trap)',
     f"{P[2.0]['qf']:.2e} cm$^{{-2}}$ (2.0, 13.2 nm), {P[6.3]['qf']:.1e} (6.3 nm); fitted on $V_{{th,cc}}$"),
]
for n, (c, mk, head, body) in enumerate(info):
    y = 6.6 - 1.62 * n
    ax.plot([26.2], [y + 0.12], ls='none', color=c, **mk)
    ax.text(27.0, y + 0.12, head, fontsize=7.0, fontweight='bold', color=c, va='center')
    ax.text(27.0, y - 0.5, body, fontsize=6.1, va='center', linespacing=1.35)
ax.text(-7.3, -0.5, 'Not modelled: traps in Al$_2$O$_3$ and HfO$_2$, at the Al$_2$O$_3$/HfO$_2$ interface and at the air-side '
        f"surface; donor-like traps. Background donors $N_D$ = {P[2.0]['nd']:.1e} cm$^{{-3}}$ (shallow, not traps). Not to scale.",
        fontsize=6.0, color='0.3')
fig.savefig(OUT / 'trap_locations.pdf'); fig.savefig(OUT / 'trap_locations.png', dpi=300); plt.close(fig)
# ------------------------------------------------------------------ figure 2: energy distributions
E = np.linspace(0, 1.2, 600)       # energy below Ec (eV)
fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw=dict(wspace=0.35))
for t in RUNS:
    p = P[t]
    a.semilogy(E, p['nta_r1'] * np.exp(-E / p['wta_r1']), color=FILM[t], lw=1.3, label=f'tail, {t:.1f} nm')
    e_at, tail_at, _ = atlas_table(t, 1)
    a.semilogy(e_at[::12], tail_at[::12], 'o', ms=2.4, mfc='none', mec=FILM[t], mew=0.6)
gd = p2['nga_r1'] * np.exp(-((E - p2['ega_r1']) / p2['wga_r1']) ** 2)
a.semilogy(E, gd, '--', color='#6C3483', lw=1.2, label='deep Gaussian (all $t$)')
e_at, _, g_at = atlas_table(2.0, 1)
a.semilogy(e_at[::12], g_at[::12], 's', ms=2.2, mfc='none', mec='#6C3483', mew=0.6)
a.set_xlim(0, 1.2); a.set_ylim(1e14, 1e21)
a.set_xlabel('$E_c - E$ (eV)'); a.set_ylabel('trap DOS (cm$^{-3}$ eV$^{-1}$)')
a.set_title('(a) bulk IWO (region 1)', fontsize=8, loc='left')
a.legend(loc='upper right', fontsize=6.0, frameon=True, framealpha=0.95, edgecolor='0.75', title='lines: deck formula\nsymbols: ATLAS table',
         title_fontsize=5.6)
dit = p2['dit_peak_cm2eV'] * np.exp(-((E - p2['ega_r2']) / p2['wga_r2']) ** 2)
tail_sheet = p2['nta_r2'] * np.exp(-E / p2['wta_r2']) * p2['t_r2_nm'] * 1e-7
b.semilogy(E, dit, '-', color='#1A5276', lw=1.3, label='$D_{it}$ Gaussian')
b.semilogy(E, tail_sheet, ':', color='#C0392B', lw=1.1, label='tail in the same 0.25 nm (2 nm film)')
e_at, _, g_at = atlas_table(2.0, 2)
b.semilogy(e_at[::12], g_at[::12] * p2['t_r2_nm'] * 1e-7, 's', ms=2.2, mfc='none', mec='#1A5276', mew=0.6)
b.set_xlim(0, 1.2); b.set_ylim(1e8, 1e14)
b.set_xlabel('$E_c - E$ (eV)'); b.set_ylabel('sheet DOS (cm$^{-2}$ eV$^{-1}$)')
b.set_title('(b) interface layer (region 2, 0.25 nm)', fontsize=8, loc='left')
b.legend(loc='upper right', fontsize=6.0, frameon=True, framealpha=0.95, edgecolor='0.75')
b.text(0.97, 0.06, f"ATLAS volume density = sheet / 0.25 nm\n= {p2['nga_r2']:.2e} cm$^{{-3}}$eV$^{{-1}}$ at peak", transform=b.transAxes,
       ha='right', va='bottom', fontsize=5.8, bbox=dict(fc='white', ec='0.75', lw=0.5, pad=1.5))
fig.savefig(OUT / 'trap_dos.pdf'); fig.savefig(OUT / 'trap_dos.png', dpi=300); plt.close(fig)

# ------------------------------------------------------------------ figure 3: how the trapped charge is computed
fig, ax = plt.subplots(figsize=(4.2, 2.9))
g = p2['nta_r1'] * np.exp(-E / p2['wta_r1']) + gd
res = []
for ef, c, lab in ((0.45, '#7F8C8D', 'off state'), (0.04, '#C0392B', 'near threshold')):
    f = 1 / (1 + np.exp((ef - E) / KT))           # occupancy of a level at E below Ec when E_F is ef below Ec
    nt = np.trapezoid(g * f, E)
    res.append((lab, ef, nt))
    ax.fill_between(E, 1e14, np.maximum(g * f, 1e14), color=c, alpha=0.35, lw=0, label=f'filled, $E_F=E_c-{ef:.2f}$ eV ({lab}, example)')
ax.semilogy(E, g, 'k-', lw=1.2, label='$g(E)$, 2.0 nm (tail + deep)')
ax.set_xlim(0, 1.0); ax.set_ylim(1e14, 1e21)
ax.set_xlabel('$E_c - E$ (eV)'); ax.set_ylabel('cm$^{-3}$ eV$^{-1}$')
ax.legend(loc='upper right', fontsize=5.8, frameon=True, framealpha=0.95, edgecolor='0.75')
ax.text(0.97, 0.05, '$n_t=\\int g(E)\\,f(E)\\,dE$,  $f=1/[1+e^{(E-E_F)/kT}]$\n' +
        '\n'.join(f'{lab}: $n_t$ = {nt:.1e} cm$^{{-3}}$' for lab, ef, nt in res), transform=ax.transAxes, ha='right', va='bottom',
        fontsize=5.8, bbox=dict(fc='white', ec='0.75', lw=0.5, pad=1.5))
fig.savefig(OUT / 'trap_occupancy.pdf'); fig.savefig(OUT / 'trap_occupancy.png', dpi=300); plt.close(fig)
for t, p in P.items():
    print(t, {k: (f'{v:.4g}' if isinstance(v, float) else v) for k, v in p.items()})
print('occupancy', res)
