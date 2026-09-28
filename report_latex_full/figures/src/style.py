"""Shared figure style for the full LaTeX report (report_latex_full).

Every figure script does:
    import sys; sys.path.insert(0, r'<report_latex_full>/figures/src'); from style import *
    fig, ax = plt.subplots(...); ...; save(fig, 'stem')
save() writes figures/<stem>.pdf (vector, used by LaTeX) and figures/png/<stem>.png (preview).
Colours match the LaTeX colours in preamble.tex. Film colours are fixed across the whole report.
"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

FIG = Path(__file__).resolve().parents[1]
PKG = FIG.parents[1]                     # IWO_PHYSICS_CONSTRAINED_MODEL_V1
RUNS = PKG / 'results' / 'runs'
DATA = PKG / 'data' / 'experimental_clean.csv'

# Fixed film colours (colour-blind safe, Okabe-Ito based)
FILM = {2.0: '#0072B2', 6.3: '#D55E00', 13.2: '#009E73', 31.8: '#7F7F7F'}
FILM_LABEL = {2.0: '2.0 nm', 6.3: '6.3 nm', 13.2: '13.2 nm', 31.8: '31.8 nm'}
# Roles
MEAS = dict(color='black', marker='o', ms=2.6, lw=0, mfc='none', mew=0.7, label='measured')
SIM = dict(lw=1.5)
ACCENT = '#1F4E79'; ACCENT2 = '#B5462E'; OK = '#2E7D32'; WARN = '#B7791F'; FAIL = '#B3261E'; GREY = '#7F7F7F'
CYCLE = ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#E69F00', '#56B4E9', '#F0E442', '#000000', '#8C564B', '#7F7F7F']

plt.rcParams.update({
    'font.family': 'serif', 'font.serif': ['DejaVu Serif', 'Times New Roman', 'Times'], 'mathtext.fontset': 'dejavuserif',
    'font.size': 9, 'axes.labelsize': 9, 'axes.titlesize': 9.5, 'legend.fontsize': 7.5, 'xtick.labelsize': 8, 'ytick.labelsize': 8,
    'axes.linewidth': 0.8, 'xtick.direction': 'in', 'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
    'axes.grid': True, 'grid.alpha': 0.25, 'grid.linewidth': 0.5, 'legend.frameon': False,
    'axes.prop_cycle': matplotlib.cycler(color=CYCLE), 'savefig.bbox': 'tight', 'savefig.pad_inches': 0.03,
    'figure.dpi': 150, 'pdf.fonttype': 42,
})
FULL_W = 6.3    # inches, full text width
HALF_W = 3.1

def panel_label(ax, s, x=-0.14, y=1.04):
    ax.text(x, y, f'({s})', transform=ax.transAxes, fontsize=9.5, fontweight='bold', va='bottom')

def save(fig, stem):
    (FIG / 'png').mkdir(exist_ok=True)
    fig.savefig(FIG / f'{stem}.pdf')
    fig.savefig(FIG / 'png' / f'{stem}.png', dpi=170)
    plt.close(fig)
    print('saved', stem)
