"""Synthesis-stage read-only checks (no ATLAS, no package file modified).
Run from the package root with ..\\IWO_ATLAS_Model_claude\\.venv\\Scripts\\python.exe
Outputs: analysis_2026-09-25/scratch/SYNTHESIS/syn_checks_out.txt
(a) horizontal offsets Vg_meas(I) - Vg_sim(I) at fixed currents (rigid vs shape part of misses)
(b) one-offset Vth_cc stories with/without confinement (re-derivation of REVIEW V11 from execution.json)
(c) SHA-256 of every file hashed in PREDICTIONS_REGISTER.md section 10, compared with the registered value
"""
import csv, hashlib, json, math, re, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
OUT = Path(__file__).with_name('syn_checks_out.txt')
lines = []
def p(*a):
    s = ' '.join(str(x) for x in a); lines.append(s); print(s)

RUNS = {d.name[:8]: d for d in (ROOT / 'results' / 'runs').iterdir() if d.is_dir()}

def load_meas(t):
    vg, idv = [], []
    with open(ROOT / 'data' / 'experimental_clean.csv') as f:
        for r in csv.DictReader(f):
            if abs(float(r['thickness_nm']) - t) < 1e-6:
                vg.append(float(r['vg_V'])); idv.append(float(r['id_A_per_um']))
    return np.array(vg), np.array(idv)

def load_sim(run, scale=1.0):
    vg, idv = [], []
    with open(RUNS[run] / 'comparison.csv') as f:
        for r in csv.DictReader(f):
            vg.append(float(r['vg_V'])); idv.append(float(r['atlas_A_per_um']) * scale)
    return np.array(vg), np.array(idv)

def v_at(vg, idv, level):
    # first upward crossing, log-linear (same rule as extract_metrics.crossing)
    for i in range(len(vg) - 1):
        a, b = idv[i], idv[i + 1]
        if a > 0 and b > 0 and (a - level) * (b - level) <= 0 and a != b:
            return vg[i] + (vg[i + 1] - vg[i]) * (math.log10(level) - math.log10(a)) / (math.log10(b) - math.log10(a))
    return None

LEVELS = [1e-11, 1e-10, 1e-9, 1e-8, 3e-8, 1e-7, 2e-7, 3e-7]
CASES = [
    (2.0, 'run_0012', 1.0, '2 nm calibrated (96/48)'),
    (2.0, 'run_0038', 17.6897 / 17.69, '2 nm B1 recal (384/192)'),
    (2.0, 'run_0016', 1.0, '2 nm no confinement, Qf 1.73e12'),
    (6.3, 'run_0014', 1.0, '6.3 nm shared params (mu 12.4)'),
    (6.3, 'run_0015', 1.0, '6.3 nm tuned (Qf 8.7e10, mu 11.69)'),
    (6.3, 'run_0039', 11.582 / 11.41, '6.3 nm B2 recal'),
    (6.3, 'run_0034', 1.0, '6.3 nm A6 no-QC, Qf 4.76e10'),
    (6.3, 'run_0030', 1.0, '6.3 nm A3 back charge'),
    (6.3, 'run_0037', 1.0, '6.3 nm B0 re-partition'),
    (6.3, 'run_0052', 1.0, '6.3 nm C1 near-Ec band'),
    (13.2, 'run_0013', 1.0, '13.2 nm calibrated'),
    (13.2, 'run_0040', 61.6046 / 60.39, '13.2 nm B3 recal'),
    (13.2, 'run_0017', 1.0, '13.2 nm no confinement'),
]
p('=== (a) horizontal offset Vg_meas(I) - Vg_sim(I) in V (positive: measured curve reaches I later)')
p('levels (A/um):', ' '.join(f'{x:.0e}' for x in LEVELS))
for t, run, sc, lab in CASES:
    vm, im = load_meas(t); vs, isim = load_sim(run, sc)
    row = []
    for lv in LEVELS:
        a, b = v_at(vm, im, lv), v_at(vs, isim, lv)
        row.append('   n/a' if (a is None or b is None) else f'{a - b:+.3f}')
    p(f'{run} {lab:38s}', ' '.join(row))

p('\n=== (a2) 6.3 nm run_0014 miss split: rigid (offset at 1e-9) and shape (offset(I) - offset(1e-9))')
vm, im = load_meas(6.3)
for run in ['run_0014', 'run_0015', 'run_0034']:
    vs, isim = load_sim(run)
    o9 = v_at(vm, im, 1e-9) - v_at(vs, isim, 1e-9)
    shape = {lv: (v_at(vm, im, lv) - v_at(vs, isim, lv)) - o9 for lv in [1e-8, 3e-8, 1e-7, 2e-7, 3e-7]}
    p(run, f'rigid(1e-9) {o9:+.3f} V =', f'{o9 / 0.17891:+.2f}e12 cm^-2 ;', 'shape part:', ', '.join(f'{k:.0e}: {v:+.3f}' for k, v in shape.items()))

p('\n=== (b) one-offset Vth_cc stories from execution.json (rigid Qf shift exact, 0.17891 V per 1e12)')
def ex(run):
    return json.load(open(RUNS[run] / 'execution.json'))
def vs(run): return ex(run)['device_metrics_sim']['Vth_cc_1e-9_V']
def vm(run): return ex(run)['device_metrics_exp']['Vth_cc_1e-9_V']
QOC = 0.17891  # V per 1e12 cm^-2
# residual (model - measured) at the shared Qf 1.73e12
qc = {2.0: vs('run_0012') - vm('run_0012'), 6.3: vs('run_0014') - vm('run_0014'), 13.2: vs('run_0013') - vm('run_0013')}
# no-QC at Qf 1.73e12: 2 nm run_0016, 13.2 nm run_0017, 6.3 nm run_0034 shifted back from Qf 4.76e10 to 1.73e12
noqc = {2.0: vs('run_0016') - vm('run_0016'), 6.3: vs('run_0034') - QOC * (1.73 - 0.0476) - vm('run_0034'), 13.2: vs('run_0017') - vm('run_0017')}
for name, res in (('with confinement', qc), ('without confinement', noqc)):
    r = np.array([res[t] for t in (2.0, 6.3, 13.2)])
    lsq = r - r.mean()
    loo = [r[i] - np.mean(np.delete(r, i)) for i in range(3)]
    anch = {t: [r[j] - r[i] for j in range(3) if j != i] for i, t in enumerate((2.0, 6.3, 13.2))}
    p(f'{name}: raw residuals at Qf 1.73e12 {dict((t, round(float(x), 4)) for t, x in zip((2.0, 6.3, 13.2), r))}')
    p(f'   LSQ one-offset rms {np.sqrt(np.mean(lsq ** 2)):.4f} V ; LOO rms {np.sqrt(np.mean(np.square(loo))):.4f} V')
    for t, m in anch.items():
        p(f'   anchor {t} nm -> held-out misses {[round(float(x), 4) for x in m]} rms {np.sqrt(np.mean(np.square(m))):.4f} V')

p('\n=== (c) SHA-256 of PREDICTIONS_REGISTER.md section-10 files vs registered values')
reg = (ROOT / 'analysis_2026-09-25' / 'PREDICTIONS_REGISTER.md').read_text(encoding='utf-8')
n_ok = n_bad = 0
for rel, h in re.findall(r'\|\s*`([^`]+)`\s*\|\s*`([0-9a-f]{64})`\s*\|', reg):
    fp = ROOT / rel.replace('/', '\\') if sys.platform.startswith('win') else ROOT / rel
    if not fp.exists():
        p('MISSING', rel); n_bad += 1; continue
    now = hashlib.sha256(fp.read_bytes()).hexdigest()
    ok = now == h
    n_ok += ok; n_bad += (not ok)
    if not ok: p('CHANGED', rel, 'registered', h[:12], 'now', now[:12])
p(f'files matching registered hash: {n_ok}; changed/missing: {n_bad}')
p('register file itself SHA-256:', hashlib.sha256((ROOT / 'analysis_2026-09-25' / 'PREDICTIONS_REGISTER.md').read_bytes()).hexdigest())

OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
