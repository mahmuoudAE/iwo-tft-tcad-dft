"""Figures for the A57 (D-80) measured-data extraction Monte Carlo output. Reads only mc_measured_extraction_out.json and RUN_LOG_A57.txt
in this folder; plots the stored registered values and 95 % intervals (no recomputation). Origin-like style: white, black, Arial, ticks inside.

    python make_figures_A57.py
"""
import hashlib, json, re, sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
OUT = HERE / 'mc_measured_extraction_out.json'
LOG = HERE / 'RUN_LOG_A57.txt'
MC = HERE.parent / 'mc_measured_extraction.py'
CSV = HERE.parents[1] / 'data' / 'experimental_clean.csv'
FILM = {2.0: '#0072B2', 6.3: '#D55E00', 13.2: '#009E73'}          # package film colours (report_latex_full/figures/src/style.py)
VG = (1.0, 1.5, 2.0, 2.5, 3.0)

plt.rcParams.update({'font.family': 'Arial', 'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic',
                     'font.size': 9, 'axes.linewidth': 1.0, 'axes.edgecolor': 'black', 'axes.facecolor': 'white', 'figure.facecolor': 'white',
                     'xtick.direction': 'in', 'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True, 'xtick.minor.visible': True,
                     'ytick.minor.visible': True, 'axes.grid': False, 'legend.frameon': False, 'legend.fontsize': 7, 'pdf.fonttype': 42})


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def bar(ax, x, q, mk, col, scale=1.0):
    """95 % interval drawn on its own (it need not contain the registered value), registered value as an open marker"""
    v, (lo, hi) = q['registered_value'] * scale, (z * scale for z in q['ci95'])
    ax.errorbar([x], [(lo + hi) / 2], yerr=[[(hi - lo) / 2], [(hi - lo) / 2]], fmt='none', ecolor=col, capsize=3, lw=1)
    ax.plot([x], [v], mk, color=col, mfc='none', ms=5)


def main():
    d = json.loads(OUT.read_text()); F = {float(t): v['quantities'] for t, v in d['films'].items()}
    end = re.search(r'end_utc: (\S+)', LOG.read_text()).group(1)
    fig, axs = plt.subplots(1, 4, figsize=(12.0, 3.4))
    # (a) mu_FE vs V_G: registered value (open markers) and replicate 95 % band
    ax = axs[0]
    for t, Q in F.items():
        reg = [Q[f'mu_fe_{v:.1f}']['registered_value'] for v in VG]; lo = [Q[f'mu_fe_{v:.1f}']['ci95'][0] for v in VG]
        hi = [Q[f'mu_fe_{v:.1f}']['ci95'][1] for v in VG]
        ax.fill_between(VG, lo, hi, color=FILM[t], alpha=0.25, lw=0); ax.plot(VG, reg, 'o', color=FILM[t], mfc='none', ms=5)
    ax.set_xlabel('Gate voltage $V_G$ (V)'); ax.set_ylabel('Field-effect mobility $\\mu_{FE}$ (cm$^2$ V$^{-1}$ s$^{-1}$)')
    ax.set_xlim(0.8, 3.2)
    # (b) SS: fixed 5e-11..5e-10 window (with floor rule) and A1 window
    ax = axs[1]
    for t, Q in F.items():
        bar(ax, t - 0.3, Q['ss_fixed_mV_dec'], 'o', FILM[t]); bar(ax, t + 0.3, Q['ss_a1_mV_dec'], 's', FILM[t])
    ax.set_xlabel('IWO film thickness (nm)'); ax.set_ylabel('Subthreshold swing SS (mV dec$^{-1}$)')
    # (c) V_th: constant current 1e-9 and 5e-10 A/um, ELR, power-law V_T
    ax = axs[2]
    for t, Q in F.items():
        for k, (key, mk) in enumerate((('vth_cc_V', 'o'), ('vth_cc_5e-10_V', 's'), ('vth_elr_V', '^'), ('pl_vt_V', 'D'))):
            bar(ax, t + (k - 1.5) * 0.35, Q[key], mk, FILM[t])
    ax.set_xlabel('IWO film thickness (nm)'); ax.set_ylabel('Threshold voltage $V_{th}$ (V)')
    # (d) off-current floor
    ax = axs[3]
    for t, Q in F.items():
        bar(ax, t, Q['off_floor_A_per_um'], 'o', FILM[t])
    ax.set_yscale('log'); ax.set_xlabel('IWO film thickness (nm)'); ax.set_ylabel('Off-current floor $I_{off}$ (A µm$^{-1}$)')
    for ax, s in zip(axs, 'abcd'):
        ax.text(-0.2, 1.02, f'({s})', transform=ax.transAxes, fontweight='bold')
        if s != 'a': ax.set_xlim(0, 15.5); ax.set_xticks(list(F))
    h = [Line2D([], [], color=FILM[t], marker='o', mfc='none', ls='none') for t in F] + [Patch(color='#7F7F7F', alpha=0.25)]
    l = [f'{t:.1f} nm film: registered value on the original measured curve' for t in F] + ['(a) shaded: replicate 95 % interval (2.5-97.5 %)']
    h += [Line2D([], [], color='black', marker=m, mfc='none', ls='-', lw=1) for m in 'os^D']
    l += ['(b) SS fixed window 5e-11...5e-10 A/µm (floor rule); (c) V$_{th}$ constant current 1e-9 A/µm; (d) floor; bars = 95 % interval',
          '(b) SS A1 window [r, 10 r] x I$_{on}$ (fixed); (c) V$_{th}$ constant current 5e-10 A/µm; bars = 95 % interval',
          '(c) V$_{th}$ extrapolation in the linear region (ELR); bars = 95 % interval',
          '(c) power-law V$_T$ (fit 1-3 V, first 400 replicates); bars = 95 % interval']
    fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=2, fontsize=7)
    src = (f'Data: {OUT.as_posix()}, produced {end} by mc_measured_extraction.py (sha256 {sha(MC)[:8]}; output sha256 {sha(OUT)[:8]}), register A57 / D-80. '
           f'Measured input: {CSV.as_posix()} (sha256 {sha(CSV)[:8]}; MEASURED, already seen: extraction uncertainty, not a blind test). '
           f'Noise model ASSUMED (SMU specification not supplied); N = {d["n"]} replicates per film (power law on {d["n_pl"]}), seed {d["seed"]} + film index.')
    fig.text(0.01, -0.32, src, fontsize=6, wrap=True, va='top', ha='left')
    fig.tight_layout()
    for ext, kw in (('pdf', {}), ('png', {'dpi': 300})):
        fig.savefig(HERE / f'fig_A57_measured_extraction_mc.{ext}', bbox_inches='tight', **kw)
    print('saved fig_A57_measured_extraction_mc.pdf / .png')


if __name__ == '__main__':
    main()
