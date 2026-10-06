#!/usr/bin/env python3
"""Explanatory figure for the band-tail density N_t(t) of the V1 TCAD: the law used (values parsed from the decks),
where its two constants come from, and the surface + bulk alternative of the audit (S4). Output: figures/nt_law.(png|pdf)."""
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(PKG / 'report_latex_full' / 'figures' / 'src'))
from style import plt, FILM  # noqa: E402

RUNS = {2.0: 'run_0038_*', 6.3: 'run_0039_*', 13.2: 'run_0040_*'}
deck = {}
for t, pat in RUNS.items():
    s = (next((PKG / 'results' / 'runs').glob(pat)) / 'device.in').read_text().replace('\\\n', ' ')
    m = re.search(r'defects region=1.*?nta=([0-9.eE+-]+) wta=([0-9.eE+-]+)', s)
    deck[t] = float(m.group(1)) * float(m.group(2))          # N_t = N_TA W_TA
NT2, ALPHA = 2.0e19, 0.75
law = lambda t: NT2 * (2.0 / t) ** ALPHA
NS, NB = 3.57e12, 2.15e18                                   # surface + bulk through the same anchors (report, S4)
sb = lambda t: NS / (t * 1e-7) + NB
for t in deck:
    assert abs(deck[t] / law(t) - 1) < 1e-3, (t, deck[t], law(t))

tt = np.linspace(1.0, 35, 400)
fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw=dict(wspace=0.38))
a.loglog(tt, law(tt), 'k-', lw=1.3, label='V1 law $N_t^{(2)}(2/t)^{0.75}$')
a.loglog(tt, sb(tt), '--', color='#7D3C98', lw=1.1, label='surface + bulk (audit, preferred form)')
for t, v in deck.items():
    a.loglog([t], [v], 'o', ms=5.5, color=FILM[t], zorder=5)
a.annotate('', (13.2, NT2 / 4), (2.0, NT2), arrowprops=dict(arrowstyle='->', lw=0.9, color='#A04000', shrinkA=6, shrinkB=6))
a.text(4.6, 1.25e19, 'ratio 1/4 from the target paper\n(Fig. 5a): $\\alpha=\\ln4/\\ln6.6=0.73$', fontsize=5.8, color='#A04000',
       linespacing=1.2)
a.text(2.15, 2.25e19, 'anchor: fitted on the\n2 nm device (V0)', fontsize=5.8, color='#0072B2', va='bottom', linespacing=1.2)
a.loglog([2.0, 10.0], [5.3e19, 3.39e18], 'x', ms=6, mew=1.2, color='0.45', label="paper's stress-model values (not used)")
a.set_xlim(1, 35); a.set_ylim(1e18, 1.5e20)
a.set_xticks([1, 2, 5, 10, 20]); a.set_xticklabels(['1', '2', '5', '10', '20'])
a.set_xlabel('IWO thickness $t$ (nm)'); a.set_ylabel('$N_t = N_{TA}W_{TA}$ (cm$^{-3}$)')
a.set_title('(a) tail density per volume', fontsize=8, loc='left')
a.legend(loc='lower left', fontsize=5.6, frameon=True, framealpha=0.95, edgecolor='0.75', handlelength=1.6)
b.plot(tt, law(tt) * tt * 1e-7 / 1e12, 'k-', lw=1.3, label='V1 law')
b.plot(tt, sb(tt) * tt * 1e-7 / 1e12, '--', color='#7D3C98', lw=1.1, label='$N_s + N_b t$')
for t, v in deck.items():
    b.plot([t], [v * t * 1e-7 / 1e12], 'o', ms=5.5, color=FILM[t], zorder=5, label=f'{t:.1f} nm')
b.axhline(NS / 1e12, color='#7D3C98', lw=0.6, ls=':')
b.text(34, NS / 1e12 - 0.35, '$N_s = 3.6\\times10^{12}$ cm$^{-2}$ (surface/interface part)', ha='right', fontsize=5.6, color='#7D3C98')
b.set_xlim(0, 35); b.set_ylim(0, 12)
b.set_xlabel('IWO thickness $t$ (nm)'); b.set_ylabel('sheet tail density $N_t t$ (10$^{12}$ cm$^{-2}$)')
b.set_title('(b) tail density per area', fontsize=8, loc='left')
b.legend(loc='upper left', fontsize=5.8, frameon=True, framealpha=0.95, edgecolor='0.75', handlelength=1.6)
fig.savefig(HERE / 'figures' / 'nt_law.pdf'); fig.savefig(HERE / 'figures' / 'nt_law.png', dpi=300); plt.close(fig)
for t, v in deck.items():
    print(f'{t} nm: N_t {v:.3e} cm-3 (law {law(t):.3e}; surface+bulk {sb(t):.3e}); sheet {v * t * 1e-7:.2e} cm-2')
