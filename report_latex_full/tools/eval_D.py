"""Evaluate campaign D: overlap 4 um vs run_0038; tmun=0 at 358 K vs run_0045 x (358.15/300)^1.5."""
import csv, json
from pathlib import Path
import numpy as np
P = Path(__file__).resolve().parents[2]
res = json.loads((P / 'results/campaigns/campaign_D_checks.json').read_text())
def cur(rid):
    d = next((P / 'results/runs').glob(f'run_{rid}_*'))
    a = np.array([(float(r['vg_V']), float(r['atlas_A_per_um'])) for r in csv.DictReader((d / 'comparison.csv').open())]); return a[:, 0], a[:, 1]
for r in res['runs']:
    print(r['id'], r.get('run_id'), r.get('status'), r.get('error'))
    if not r.get('run_id'): continue
    rid = r['run_id'][4:]; v, i = cur(rid)
    if 'overlap' in r['id']:
        v0, i0 = cur('0038'); ok = (i > 1e-15) & (i0 > 1e-15); d = np.log10(i[ok] / i0[ok])
        print(f"  vs run_0038: Vth_cc {r['sim']['Vth_cc_1e-9_V']:.4f} (0038 0.6804), Ion {r['sim']['Ion_A_per_um']:.4e} ({100*(r['sim']['Ion_A_per_um']/5.09e-7-1):+.2f} %), max|dlog| {abs(d).max():.4f} dec")
    else:
        v0, i0 = cur('0045'); f = (358.15 / 300) ** 1.5; ok = i0 > 1e-15; ratio = i[ok] / (i0[ok] * f)
        print(f"  vs run_0045 x {f:.5f}: ratio min {ratio.min():.5f} max {ratio.max():.5f} (Vg>{v[ok][0]:.2f} V)")
