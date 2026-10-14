"""Plain plotting-software (Origin-like) style for the DFT study figures.

Colours and fonts are taken from the package style (report_latex_full/figures/src/style.py); the grid is switched
off for the plain look. No text inside the panels: every explanation goes into the caption (DFT_FULL_STUDY.md).
save() writes figures/<stem>.png (300 dpi) and figures/<stem>.pdf.
"""
import importlib.util
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
_pkg_style = HERE.parents[1] / 'report_latex_full' / 'figures' / 'src' / 'style.py'
_spec = importlib.util.spec_from_file_location('pkg_style', _pkg_style)
_ps = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ps)
CYCLE, FILM, GREY = _ps.CYCLE, _ps.FILM, _ps.GREY
ACCENT, ACCENT2, OK, FAIL, WARN = _ps.ACCENT, _ps.ACCENT2, _ps.OK, _ps.FAIL, _ps.WARN
FULL_W, HALF_W = _ps.FULL_W, _ps.HALF_W
plt.rcParams.update({'axes.grid': False, 'xtick.minor.visible': True, 'ytick.minor.visible': True,
                     'xtick.major.size': 3.5, 'ytick.major.size': 3.5, 'xtick.minor.size': 2, 'ytick.minor.size': 2,
                     'lines.markersize': 4.5, 'legend.handlelength': 1.8})
# element / character colours used in every PDOS figure
EL = {'In': '#0072B2', 'O': '#D55E00', 'W': '#009E73', 'H': '#7F7F7F', 'tot': '#000000'}
FIGS = HERE / 'figures'


def panel(ax, s, x=-0.16, y=1.02):
    ax.text(x, y, f'({s})', transform=ax.transAxes, fontsize=9.5, fontweight='bold', va='bottom')


def save(fig, stem):
    FIGS.mkdir(exist_ok=True)
    fig.savefig(FIGS / f'{stem}.pdf')
    fig.savefig(FIGS / f'{stem}.png', dpi=300)
    plt.close(fig)
    print('saved', stem)
