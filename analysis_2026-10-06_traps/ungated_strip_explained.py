#!/usr/bin/env python3
"""Plain illustration of the ungated-strip hypothesis for the off-state floors (report chapter V2, table tab:v2-strip):
(a) top view with a strip of IWO outside the gate, (b) equivalent circuit, (c) measured floors vs the three strip variants
(one geometric factor fitted on 13.2 nm; ratios pred/meas from the report). Output: figures/ungated_strip_explained.(png|pdf)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'report_latex_full' / 'figures' / 'src'))
from style import plt, FILM  # noqa: E402
from matplotlib.patches import Rectangle, FancyArrowPatch  # noqa: E402

FLOOR = {2.0: 4.61e-15, 6.3: 1.53e-13, 13.2: 6.60e-12}               # measured, A/um
RATIO = {'N: no surface states': (5.07, 1.21, '#7F8C8D', 'v'),
         'D: one surface with interface acceptors': (0.48, 0.77, '#C0392B', 'o'),
         'Q: D + fixed charge': (134, 4.76, '#2E86C1', '^')}

fig = plt.figure(figsize=(7.4, 2.9))
# (a) top view
a = fig.add_axes([0.0, 0.05, 0.36, 0.85]); a.axis('off'); a.set_xlim(0, 10); a.set_ylim(0, 10)
a.add_patch(Rectangle((1.0, 1.0), 8.0, 7.6, fc='#F3C89B', ec='k', lw=0.6))                  # IWO film
a.add_patch(Rectangle((2.6, 2.4), 4.8, 4.8, fc='#9AA3AD', ec='k', lw=0.6, alpha=0.55))     # gate underneath
a.add_patch(Rectangle((1.0, 2.0), 1.9, 5.6, fc='#B0B4BA', ec='k', lw=0.6, hatch='\\\\'))   # source
a.add_patch(Rectangle((7.1, 2.0), 1.9, 5.6, fc='#B0B4BA', ec='k', lw=0.6, hatch='\\\\'))   # drain
a.text(1.95, 4.8, 'S', ha='center', va='center', fontsize=8, fontweight='bold')
a.text(8.05, 4.8, 'D', ha='center', va='center', fontsize=8, fontweight='bold')
a.text(5.0, 4.8, 'gated\nchannel', ha='center', va='center', fontsize=6.5)
a.add_patch(Rectangle((2.9, 7.25), 4.2, 0.35, fc='#C0392B', ec='none', alpha=0.55))         # ungated strip
a.add_patch(FancyArrowPatch((3.2, 7.42), (6.8, 7.42), arrowstyle='->', mutation_scale=7, color='#C0392B', lw=1.0))
a.text(5.0, 8.95, 'IWO outside the gate edge:\nconducts S$\\to$D whatever $V_G$ is', ha='center', fontsize=6.0, color='#C0392B',
       linespacing=1.2)
a.text(5.0, 0.35, 'top view (sketch; real location unknown)', ha='center', fontsize=5.8, color='0.35')
a.set_title('(a) where it could be', fontsize=8, loc='left')
# (b) circuit
b = fig.add_axes([0.37, 0.05, 0.22, 0.85]); b.axis('off'); b.set_xlim(0, 10); b.set_ylim(0, 10)
b.plot([1, 1, 3.6], [5, 7.5, 7.5], 'k-', lw=0.8); b.plot([6.4, 9, 9], [7.5, 7.5, 5], 'k-', lw=0.8); b.plot([1, 1, 9, 9], [5, 2.5, 2.5, 5], 'k-', lw=0.8)
b.add_patch(Rectangle((3.6, 6.7), 2.8, 1.6, fc='#F3C89B', ec='k', lw=0.7)); b.text(5, 7.5, 'TFT', ha='center', va='center', fontsize=7)
b.text(5, 8.9, '$I_{TFT}(V_G)$', ha='center', fontsize=6.5)
b.plot([3.6, 4.0, 4.4, 4.8, 5.2, 5.6, 6.0, 6.4], [2.5, 3.0, 2.0, 3.0, 2.0, 3.0, 2.0, 2.5], color='#C0392B', lw=1.0)
b.plot([1, 3.6], [2.5, 2.5], 'k-', lw=0.8); b.plot([6.4, 9], [2.5, 2.5], 'k-', lw=0.8)
b.text(5, 0.9, '$G_{strip}V_D$ (no $V_G$)', ha='center', fontsize=6.5, color='#C0392B')
b.text(0.5, 5, 'S', ha='right', va='center', fontsize=8, fontweight='bold'); b.text(9.5, 5, 'D', ha='left', va='center', fontsize=8, fontweight='bold')
b.set_title('(b) parallel path', fontsize=8, loc='left')
# (c) floors
c = fig.add_axes([0.70, 0.19, 0.29, 0.66])
ts = list(FLOOR)
c.semilogy(ts, [FLOOR[t] for t in ts], 's', ms=6, mfc='none', mec='k', mew=1.1, label='measured floor', zorder=5)
for lab, (r2, r63, col, mk) in RATIO.items():
    c.semilogy(ts, [FLOOR[2.0] * r2, FLOOR[6.3] * r63, FLOOR[13.2]], mk + '-', color=col, ms=4, lw=0.9, label=lab)
c.set_xticks(ts); c.set_xlabel('IWO thickness (nm)'); c.set_ylabel('off-state floor (A/$\\mu$m)')
c.set_ylim(1e-15, 3e-11)
c.legend(loc='lower right', fontsize=5.4, frameon=True, framealpha=0.95, edgecolor='0.75', handlelength=1.4)
c.set_title('(c) one factor fitted at 13.2 nm', fontsize=7.5)
fig.savefig(HERE / 'figures' / 'ungated_strip_explained.pdf'); fig.savefig(HERE / 'figures' / 'ungated_strip_explained.png', dpi=300)
