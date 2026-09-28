"""Read-only: same-metric leverage of the confinement package vs fitted/assumed parameters at 2 nm.
Compares fixed-current SS (1e-11..1e-10, 1e-10..1e-9), SS_cc (1e-10..1e-8) and the non-rigidity of the
horizontal shift (shift at 1e-8 minus shift at 1e-11) for one-at-a-time pairs vs run_0012 (or run_0038).
Output: syn_leverage_out.txt next to this script."""
import csv, math
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
RUNS = {d.name[:8]: d for d in (ROOT / 'results' / 'runs').iterdir() if d.is_dir()}
out = []
def p(s): out.append(s); print(s)
def load(run):
    vg, i = [], []
    with open(RUNS[run] / 'comparison.csv') as f:
        for r in csv.DictReader(f):
            vg.append(float(r['vg_V'])); i.append(float(r['atlas_A_per_um']))
    return np.array(vg), np.array(i)
def v_at(vg, idv, lv):
    for k in range(len(vg) - 1):
        a, b = idv[k], idv[k + 1]
        if a > 0 and b > 0 and (a - lv) * (b - lv) <= 0 and a != b:
            return vg[k] + (vg[k + 1] - vg[k]) * (math.log10(lv) - math.log10(a)) / (math.log10(b) - math.log10(a))
    return None
def mets(run):
    vg, i = load(run)
    v = {lv: v_at(vg, i, lv) for lv in (1e-11, 1e-10, 1e-9, 1e-8)}
    return {'V1e-9': v[1e-9], 'SS11_10': (v[1e-10] - v[1e-11]) * 1e3, 'SS10_9': (v[1e-9] - v[1e-10]) * 1e3,
            'SScc': (v[1e-8] - v[1e-10]) / 2 * 1e3, 'v': v}
PAIRS = [('run_0012', 'run_0016', 'confinement package removed (dEc + m*)'),
         ('run_0012', 'run_0024', 'WTA +5 meV'),
         ('run_0012', 'run_0025', 'Dit x3'),
         ('run_0012', 'run_0023', 'Nt x1.5'),
         ('run_0012', 'run_0022', 'Nd x2'),
         ('run_0038', 'run_0050', 'm* x1.3 (DOS 384/192)'),
         ('run_0038', 'run_0048', 'WF +0.1 eV (DOS 384/192)')]
p('2 nm one-at-a-time pairs: deltas (pert - ref) of V(1e-9) [mV], SS 1e-11..1e-10, SS 1e-10..1e-9, SS_cc [mV/dec], non-rigidity = shift(1e-8) - shift(1e-11) [mV]')
for ref, pert, lab in PAIRS:
    a, b = mets(ref), mets(pert)
    nonrig = ((b['v'][1e-8] - a['v'][1e-8]) - (b['v'][1e-11] - a['v'][1e-11])) * 1e3
    p(f'{pert} vs {ref} {lab:40s} dV(1e-9) {1e3 * (b["V1e-9"] - a["V1e-9"]):+7.1f}  dSS11_10 {b["SS11_10"] - a["SS11_10"]:+6.1f}  '
      f'dSS10_9 {b["SS10_9"] - a["SS10_9"]:+6.1f}  dSScc {b["SScc"] - a["SScc"]:+6.1f}  non-rigidity {nonrig:+6.1f}')
(Path(__file__).with_name('syn_leverage_out.txt')).write_text('\n'.join(out) + '\n', encoding='utf-8')
