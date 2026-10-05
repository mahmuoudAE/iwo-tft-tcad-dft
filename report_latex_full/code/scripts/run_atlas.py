#!/usr/bin/env python3
"""Launch ONE real ATLAS run of a generated deck, validate terminal currents, score against the
measurement, and append to results/RUN_INDEX.csv. Never substitutes a Python model for the solver.

  python scripts/run_atlas.py --thickness 2 --label v1_baseline [--override k=v ...] [--stride 2] [--vg-min -1] [--timeout 1500]
  python scripts/run_atlas.py --rescore results/runs/run_0003_...

Validation (declared): |Id+Is+Ig| <= max(1e-17 A, 0.1 x min measured Id) + 1 % x sum|I|; Id above that floor must be
positive; every requested gate point exported; ATLAS completion (banner or processed EXTRACT quit); no parser/license error.
Scoring: measured region masks (all / active / subthreshold / on / low-current) frozen from the measurement only;
log10 residual = log10(max(pred, 1e-40)) - log10(meas); signed raw currents kept in terminal_currents.csv.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re, shutil, subprocess, sys, threading, time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, yaml
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_iwo_decks import ROOT, KEYS, load_configs, set_dotted, build_deck, read_meas
from extract_metrics import metrics

RUNS = ROOT / 'results' / 'runs'; INDEX = ROOT / 'results' / 'RUN_INDEX.csv'
FIELDS = ['run_id', 'timestamp_utc', 'thickness_nm', 'label', 'deck_sha256', 'model_sha256', 'command', 'simulator', 'exit_code', 'converged', 'elapsed_s', 'output_dir', 'notes']

def sha(s): return hashlib.sha256(s.encode()).hexdigest()
def rows(): return list(csv.DictReader(INDEX.open(newline=''))) if INDEX.is_file() else []
def next_id():
    n = 0
    for r in rows():
        m = re.match(r'run_(\d+)', r.get('run_id', '')); n = max(n, int(m.group(1))) if m else n
    return f'run_{n + 1:04d}'
def launches(): return len({r['run_id'] for r in rows()})
# parallel campaigns (2026-09-28): run IDs, the launch budget and RUN_INDEX writes are guarded by one lock;
# IDs reserved by running threads count against the budget before their first RUN_INDEX row exists
_LOCK = threading.RLock(); _PENDING = set()
def append(row):
    with _LOCK:
        new = not INDEX.is_file(); INDEX.parent.mkdir(parents=True, exist_ok=True)
        with INDEX.open('a', newline='') as f:
            w = csv.DictWriter(f, fieldnames=FIELDS); (w.writeheader() if new else None); w.writerow({k: row.get(k, '') for k in FIELDS})
def reserve(r, t, label):
    with _LOCK:
        used = {x['run_id'] for x in rows()} | _PENDING
        if len(used) >= int(r['max_launches']): raise RuntimeError(f'launch budget {r["max_launches"]} reached; ask before increasing')
        n = max([int(m.group(1)) for u in used for m in [re.match(r'run_(\d+)', u)] if m] + [0])
        rid = f'run_{n + 1:04d}'; _PENDING.add(rid)
        slug = re.sub(r'[^A-Za-z0-9]+', '_', label).strip('_')[:40]; dest = RUNS / f'{rid}_{KEYS[t]}_{slug}'; dest.mkdir(parents=True)
        return rid, dest

def read_xy(p: Path):
    pts = []
    for line in p.read_text(errors='replace').splitlines():
        w = line.replace(',', ' ').split()
        if len(w) != 2: continue
        try: x, y = (float(z.replace('D', 'E')) for z in w)
        except ValueError: continue
        pts.append((x, y))
    if len(pts) < 3: raise RuntimeError(f'{p}: fewer than 3 numeric rows')
    a = np.array(pts)
    if np.any(np.diff(a[:, 0]) < -1e-9): raise RuntimeError('export is not an increasing sweep')
    u = {float(x): float(y) for x, y in a}; xs = np.array(sorted(u)); return xs, np.array([u[x] for x in xs])

def scan(text):
    lines = text.splitlines()
    warn = [l.strip() for l in lines if re.search(r'\bwarning\b', l, re.I)][:50]
    flags = [l.strip() for l in lines if re.search(r'fail|diverg|not converge|abort|too many trap', l, re.I)][:50]
    # DeckBuild EXTRACT post-processing lines are excluded from the simulator-error scan (an EXTRACT syntax problem does not invalidate the ATLAS solution; missing exports are detected separately).
    err = [l.strip() for l in lines if not l.lstrip().upper().startswith('EXTRACT') and any(re.search(p, l, re.I) for p in [r'invalid\s+parameter', r'unknown\s+(?:parameter|statement|material)', r'license.*(?:denied|failed|unavailable)', r'cannot\s+open', r'error\s*#', r'fatal\s+error', r'syntax error', r'unrecognized', r'memory allocation failure'])][:50]
    return {'warnings': warn, 'convergence_flags': flags, 'errors': err, 'banner': bool(re.search(r'ATLAS version .* finished', text)), 'finished': bool(re.search(r'ATLAS version .* finished', text) or re.search(r'EXTRACT>\s*quit', text)), 'static_solutions': len(re.findall(r'Obtaining static solution', text))}

def regions(vg, meas, t, mult):
    o = float(np.median(meas[(vg >= -2) & (vg <= -.5)])); active = meas > mult * o if t < 20 else np.ones(len(meas), bool)
    on = active & (meas >= 1e-2 * meas.max()); return {'all': np.ones(len(meas), bool), 'active': active, 'subthreshold': active & ~on, 'on': on, 'low_current': ~active}, o

def score(vg, meas, pred, t, s):
    masks, o = regions(vg, meas, t, s['scoring']['active_multiplier']); eps = s['scoring']['logging_epsilon_A_per_um']
    le = np.log10(np.maximum(pred, eps)) - np.log10(meas); lin = pred - meas
    def reg(m):
        if not m.any(): return {'count': 0}
        return {'count': int(m.sum()), 'rmse_log10': float(np.sqrt(np.mean(le[m] ** 2))), 'max_abs_log10': float(abs(le[m]).max()), 'mean_log10': float(le[m].mean()), 'rmse_linear_A_per_um': float(np.sqrt(np.mean(lin[m] ** 2))), 'median_abs_relative': float(np.median(abs(pred[m] / meas[m] - 1)))}
    return {'regions': {k: reg(m) for k, m in masks.items()}, 'on_error_3V_percent': float(100 * (pred[-1] / meas[-1] - 1)), 'nonpositive_pred_count': int((pred <= 0).sum()), 'off_band_median_A_per_um': o,
            'max_abs_log10_active': float(abs(le[masks['active']]).max()), 'log_treatment': f'log10(max(pred,{eps:g})) - log10(meas)'}, masks['active'], le

def plots(dest, vg, meas, pred, t, title):
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    except Exception: return
    fig, ax = plt.subplots(1, 3, figsize=(14, 4)); e = 1e-40
    ax[0].semilogy(vg, meas, 'k.', ms=4, label='measured (workbook)'); ax[0].semilogy(vg, np.maximum(pred, e), 'r-', lw=1.2, label='ATLAS (this run)'); ax[0].set_ylim(1e-17, 1e-5); ax[0].set_title(f'{t} nm log | {title}')
    ax[1].plot(vg, meas * 1e6, 'k.', ms=4, label='measured'); ax[1].plot(vg, pred * 1e6, 'r-', lw=1.2, label='ATLAS'); ax[1].set_ylabel('Id (uA/um)'); ax[1].set_title('linear')
    ax[2].plot(vg, np.log10(np.maximum(pred, e)) - np.log10(meas), 'b.-', ms=3, lw=.8); ax[2].axhline(0, color='k', lw=.6); ax[2].set_ylim(-1, 1); ax[2].set_ylabel('log10(ATLAS/measured)'); ax[2].set_title('residual (clipped to +/-1 dec)')
    for a in ax: a.set_xlabel('Vg (V)'); a.grid(alpha=.3)
    ax[0].legend(fontsize=8); ax[1].legend(fontsize=8); fig.tight_layout(); fig.savefig(dest / 'overlay_residual.png', dpi=130); plt.close(fig)

def meas_floor(vg, meas):
    """Measured off-band floor: median Id over Vg in [-2, -0.5] V (robust; the single-point minimum of the 2 nm
    curve, 1.1e-16 A/um at -3 V, is an outlier 40x below its own floor of 4.6e-15)."""
    return float(np.median(meas[(vg >= -2) & (vg <= -.5)]))

def validate(dest, xv, idr, isr, igr, floor, s):
    r = s['runner']; abs_lim = max(float(r['kcl_absolute_limit_A']), float(r['kcl_floor_fraction']) * floor); rel = float(r['kcl_relative_limit']); sign = float(r['expected_drain_sign'])
    imb = np.abs(idr + isr + igr); sc = abs(idr) + abs(isr) + abs(igr); ok = imb <= abs_lim + rel * sc; above = abs(idr) > abs_lim; signed = sign * idr; wrong = above & (signed < 0)
    with (dest / 'terminal_currents.csv').open('w', newline='') as f:
        w = csv.writer(f); w.writerow(['vg_V', 'id_raw_A', 'is_raw_A', 'ig_raw_A', 'id_A_per_um', 'kcl_abs_A', 'kcl_pass', 'above_abs_floor']); w.writerows(zip(xv, idr, isr, igr, signed, imb, ok.astype(int), above.astype(int)))
    return signed, {'kcl_abs_limit_applied_A': abs_lim, 'kcl_floor_basis': 'max(1e-17 A, 0.1 x median measured Id over Vg in [-2,-0.5] V)', 'measured_floor_A_per_um': floor, 'max_kcl_abs_A': float(imb.max()), 'kcl_fail_count': int((~ok).sum()), 'kcl_fail_vg': [float(v) for v in xv[~ok]][:20], 'wrong_sign_count': int(wrong.sum()), 'nonpositive_count': int((signed <= 0).sum())}, ('SIGN_REVERSAL' if wrong.any() else 'KCL_FAILED' if not ok.all() else 'OK')

def parse_segments(text):
    """'-1:0.2,1.5:0.05,3:0.1' -> [(end, step), ...]; 'none' -> None (per-point solves)."""
    if text is None or str(text).lower() in ('none', 'off', ''): return None
    return [(float(a), float(b)) for a, b in (seg.split(':') for seg in str(text).split(','))]

def execute(t, label, overrides, stride=1, vg_min=None, timeout=None, smoke=False, vstep=None, segments='config', full='config', predict=False):
    """segments: [(end V, step V), ...] for ATLAS stepped SOLVE VSTEP/VFINAL/NAME=gate blocks ('config' = solver.yaml
    sweep.segments; None = one SOLVE per 0.05 V point). vstep: single-step shorthand. full: physical structure
    (Air / Pd volumes / Al2O3 / HfO2 / Conductor gate; 'config' = geometry.yaml structure == 'full').
    Steps must be multiples of the 0.05 V measured grid; the run is scored at the solved points only.
    predict (2026-10-06): no measured curve (any thickness); the Vg grid comes from geometry.yaml, KCL is validated with
    the 1e-17 A absolute limit, nothing is scored, and the curve is written to prediction.csv."""
    m, g, s = load_configs()
    for o in overrides:
        k, v = o.split('=', 1)   # 'solver.' / 'geometry.' prefixes address solver.yaml / geometry.yaml (numerical checks); else the material model
        if k.startswith('solver.'): set_dotted(s, k[7:], v)
        elif k.startswith('geometry.'): set_dotted(g, k[9:], v)
        else: set_dotted(m, k, v)
    if full == 'config': full = str(g.get('structure', 'reduced')).lower() == 'full'
    if segments == 'config': segments = [tuple(x) for x in s['sweep']['segments']] if str(s.get('sweep', {}).get('mode', 'pointwise')) == 'stepped' else None
    if vstep: segments = [(float(g['gate_sweep_V']['stop']), float(vstep))]
    if predict:
        sw = g['gate_sweep_V']; vg = np.round(np.arange(sw['start'], sw['stop'] + 1e-9, sw['step']), 6); meas = None
    else:
        vg, meas = read_meas(t)
    base = vg[vg >= vg_min - 1e-9] if vg_min is not None else vg
    if segments:
        pts = [float(base[0])]; a = float(base[0])
        for e, st_ in segments:
            if abs(st_ / 0.05 - round(st_ / 0.05)) > 1e-6: raise ValueError('segment steps must be multiples of the 0.05 V measured grid')
            n = int(round((e - a) / st_)); pts += [round(a + i * st_, 6) for i in range(1, n + 1)]; a = float(e)
        targets = np.array(sorted(set(pts) & set(np.round(base, 6).tolist())))
    else:
        targets = base[::stride] if stride > 1 else base
        if stride > 1 and targets[-1] != vg[-1]: targets = np.append(targets, vg[-1])
    r = s['runner']
    rid, dest = reserve(r, t, label)
    text, meta = build_deck(t, m, g, s, meas=None if predict else (vg, meas), targets=targets, smoke=smoke, full=full, segments=segments); (dest / 'device.in').write_text(text, encoding='ascii')
    mtxt = json.dumps(m, indent=2, default=float); (dest / 'material_model_used.json').write_text(mtxt); (dest / 'metadata.json').write_text(json.dumps(meta, indent=2, default=float))
    argv = [z.replace('{deck}', 'device.in').replace('{stdout}', 'deckbuild.out') for z in r['argv']]
    if not Path(argv[0]).is_file() and shutil.which(argv[0]) is None: raise RuntimeError(f'executable not found: {argv[0]}')
    to = timeout or (r['timeout_seconds']['thick'] if t > 20 else r['timeout_seconds']['default'])
    import build_iwo_decks as _b
    row = {'run_id': rid, 'timestamp_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'thickness_nm': t, 'label': label, 'deck_sha256': sha(text), 'model_sha256': sha(mtxt), 'command': ' '.join(argv), 'simulator': 'DeckBuild 5.0.10.R + ATLAS 5.28.1.R', 'output_dir': str(dest.relative_to(ROOT)).replace('\\', '/'), 'notes': f'STARTED points={len(targets)} timeout={to}s launch {launches() + 1}/{r["max_launches"]}' + ('' if _b.MODEL_FILE == 'config/iwo_material_model.yaml' else f' model={_b.MODEL_FILE}') + (' PREDICTION (no measurement)' if predict else '')}
    append(row); t0 = time.monotonic()
    p = subprocess.Popen(argv, cwd=dest, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try: out, err = p.communicate(timeout=to); timed_out = False
    except subprocess.TimeoutExpired:
        subprocess.run(['taskkill', '/T', '/F', '/PID', str(p.pid)], capture_output=True); out, err = p.communicate(); timed_out = True
    el = time.monotonic() - t0; (dest / 'launcher_stdout.txt').write_text(out or ''); (dest / 'launcher_stderr.txt').write_text(err or '')
    tr = (dest / 'deckbuild.out').read_text(errors='replace') if (dest / 'deckbuild.out').exists() else ''; sc = scan((out or '') + (err or '') + tr)
    ex = {'run_id': rid, 'thickness_nm': t, 'label': label, 'elapsed_s': el, 'returncode': p.returncode, 'timed_out': timed_out, 'scan': sc, 'requested_points': int(len(targets)), 'overrides': overrides}
    def finish(status, conv, note):
        ex['status'] = status; (dest / 'execution.json').write_text(json.dumps(ex, indent=2, default=float)); append({**row, 'timestamp_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'exit_code': 'timeout' if timed_out else p.returncode, 'converged': conv, 'elapsed_s': f'{el:.1f}', 'notes': note})
    if sc['errors']: finish('SIMULATOR_ERROR', 'no', sc['errors'][0][:120]); raise RuntimeError(f'{rid}: {sc["errors"][0]}')
    if not (dest / 'idvg.dat').exists(): finish('TIMEOUT' if timed_out else 'NO_EXPORT', 'no', 'no idvg.dat'); raise RuntimeError(f'{rid}: no export (timeout={timed_out}); inspect {dest}')
    xv, idr = read_xy(dest / 'idvg.dat'); xg, igr = read_xy(dest / 'igvg.dat'); xs, isr = read_xy(dest / 'isvg.dat'); igr = np.interp(xv, xg, igr); isr = np.interp(xv, xs, isr)
    if np.min(abs(xv[:, None] - targets[None, :]), axis=0).max() > 1e-6: finish('INCOMPLETE_EXPORT', 'partial', 'missing requested gate points'); raise RuntimeError(f'{rid}: incomplete export')
    signed, v, verdict = validate(dest, xv, idr, isr, igr, 0.0 if predict else meas_floor(vg, meas), s); ex['validation'] = v; ex['scan']['banner_present'] = sc['banner']
    if verdict != 'OK': finish(verdict, 'yes', f'{verdict}: max KCL {v["max_kcl_abs_A"]:.2g} A'); raise RuntimeError(f'{rid}: {verdict}; inspect {dest}/terminal_currents.csv')
    if predict:
        ex['device_metrics_sim'] = metrics(xv, signed, True, None)
        with (dest / 'prediction.csv').open('w', newline='') as f:
            w = csv.writer(f); w.writerow(['vg_V', 'atlas_A_per_um']); w.writerows(zip(xv, signed))
        dm = ex['device_metrics_sim']
        finish('REAL_ATLAS_PREDICTION', 'yes' if not sc['convergence_flags'] else 'yes-with-flags', f'PREDICTION Vth_cc {dm["Vth_cc_1e-9_V"]}; Id(3V) {dm["Ion_A_per_um"]:.3e}; maxKCL {v["max_kcl_abs_A"]:.1e}')
        print(json.dumps({'run_id': rid, 'Vth_cc': dm['Vth_cc_1e-9_V'], 'Ion': dm['Ion_A_per_um'], 'maxKCL_A': v['max_kcl_abs_A'], 'flags': len(sc['convergence_flags']), 'elapsed_s': round(el)}, indent=1))
        return dest
    if vg_min is None:
        pred = np.interp(vg, xv, signed); met, active, le = score(vg, meas, pred, t, s); ex['fit_metrics'] = met
        ex['device_metrics_sim'] = metrics(vg, pred, True, t); ex['device_metrics_exp'] = metrics(vg, meas, False, t)
        with (dest / 'comparison.csv').open('w', newline='') as f:
            w = csv.writer(f); w.writerow(['vg_V', 'measured_A_per_um', 'atlas_A_per_um', 'log10_error', 'linear_error_A_per_um', 'active_fit_region']); w.writerows(zip(vg, meas, pred, le, pred - meas, active.astype(int)))
        plots(dest, vg, meas, pred, t, rid)
        finish('REAL_ATLAS_SCORED', 'yes' if not sc['convergence_flags'] else 'yes-with-flags', f'active RMSE {met["regions"]["active"]["rmse_log10"]:.4f} dec; Id(3V) {met["on_error_3V_percent"]:+.2f}%; nonpos {met["nonpositive_pred_count"]}; maxKCL {v["max_kcl_abs_A"]:.1e}')
        print(json.dumps({'run_id': rid, 'active_rmse_log10': met['regions']['active']['rmse_log10'], 'active_max': met['max_abs_log10_active'], 'sub_rmse': met['regions']['subthreshold'].get('rmse_log10'), 'on_rmse': met['regions']['on'].get('rmse_log10'), 'Id3V_err_pct': met['on_error_3V_percent'], 'nonpositive': met['nonpositive_pred_count'], 'maxKCL_A': v['max_kcl_abs_A'], 'flags': len(sc['convergence_flags']), 'elapsed_s': round(el)}, indent=1))
    else:
        finish('REAL_ATLAS_PARTIAL_SWEEP', 'yes' if not sc['convergence_flags'] else 'yes-with-flags', f'partial from {vg_min} V; maxKCL {v["max_kcl_abs_A"]:.1e}'); print(rid, 'partial sweep done', dest)
    return dest

def execute_output(t, label, overrides, vgs, vd_segments, timeout=None):
    """PREDICTION launch (2026-09-25): ID-VD families at fixed Vg with the same material model/structure as the
    transfer runs. No measured counterpart exists, so nothing is scored; terminal-current KCL is validated per point
    (limit 1e-17 A + 1 % of sum|I|) and the curves are written to output_characteristics.csv."""
    m, g, s = load_configs()
    for o in overrides:
        k, v = o.split('=', 1)
        if k.startswith('solver.'): set_dotted(s, k[7:], v)
        elif k.startswith('geometry.'): set_dotted(g, k[9:], v)
        else: set_dotted(m, k, v)
    full = str(g.get('structure', 'reduced')).lower() == 'full'; r = s['runner']
    rid, dest = reserve(r, t, label)
    text, meta = build_deck(t, m, g, s, meas=read_meas(t), full=full, output_vgs=vgs, vd_segments=vd_segments); (dest / 'device.in').write_text(text, encoding='ascii')
    mtxt = json.dumps(m, indent=2, default=float); (dest / 'material_model_used.json').write_text(mtxt); (dest / 'metadata.json').write_text(json.dumps(meta, indent=2, default=float))
    argv = [z.replace('{deck}', 'device.in').replace('{stdout}', 'deckbuild.out') for z in r['argv']]
    to = timeout or r['timeout_seconds']['thick']
    row = {'run_id': rid, 'timestamp_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'thickness_nm': t, 'label': label, 'deck_sha256': sha(text), 'model_sha256': sha(mtxt), 'command': ' '.join(argv), 'simulator': 'DeckBuild 5.0.10.R + ATLAS 5.28.1.R', 'output_dir': str(dest.relative_to(ROOT)).replace('\\', '/'), 'notes': f'STARTED output prediction Vg={vgs} timeout={to}s launch {launches() + 1}/{r["max_launches"]}'}
    append(row); t0 = time.monotonic()
    p = subprocess.Popen(argv, cwd=dest, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try: out, err = p.communicate(timeout=to); timed_out = False
    except subprocess.TimeoutExpired:
        subprocess.run(['taskkill', '/T', '/F', '/PID', str(p.pid)], capture_output=True); out, err = p.communicate(); timed_out = True
    el = time.monotonic() - t0; (dest / 'launcher_stdout.txt').write_text(out or ''); (dest / 'launcher_stderr.txt').write_text(err or '')
    tr = (dest / 'deckbuild.out').read_text(errors='replace') if (dest / 'deckbuild.out').exists() else ''; sc = scan((out or '') + (err or '') + tr)
    ex = {'run_id': rid, 'thickness_nm': t, 'label': label, 'mode': 'output_prediction', 'elapsed_s': el, 'returncode': p.returncode, 'timed_out': timed_out, 'scan': sc, 'overrides': overrides, 'output_vgs': meta['output_vgs']}
    def finish(status, conv, note):
        ex['status'] = status; (dest / 'execution.json').write_text(json.dumps(ex, indent=2, default=float)); append({**row, 'timestamp_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'exit_code': 'timeout' if timed_out else p.returncode, 'converged': conv, 'elapsed_s': f'{el:.1f}', 'notes': note})
    if sc['errors']: finish('SIMULATOR_ERROR', 'no', sc['errors'][0][:120]); raise RuntimeError(f'{rid}: {sc["errors"][0]}')
    rows_out, worst, fails = [], 0.0, 0
    for v, tag in zip(meta['output_vgs'], meta['output_tags']):
        if not (dest / f'idvd_{tag}.dat').exists(): finish('TIMEOUT' if timed_out else 'NO_EXPORT', 'no', f'no idvd_{tag}.dat'); raise RuntimeError(f'{rid}: no export for {tag}')
        xv, idr = read_xy(dest / f'idvd_{tag}.dat'); xs, isr = read_xy(dest / f'isvd_{tag}.dat'); xg, igr = read_xy(dest / f'igvd_{tag}.dat')
        isr = np.interp(xv, xs, isr); igr = np.interp(xv, xg, igr); imb = np.abs(idr + isr + igr); ok = imb <= float(r['kcl_absolute_limit_A']) + float(r['kcl_relative_limit']) * (abs(idr) + abs(isr) + abs(igr))
        worst = max(worst, float(imb.max())); fails += int((~ok).sum())
        rows_out += [(v, vd, idv, isv, igv, int(k)) for vd, idv, isv, igv, k in zip(xv, idr, isr, igr, ok)]
    with (dest / 'output_characteristics.csv').open('w', newline='') as f:
        w = csv.writer(f); w.writerow(['vg_V', 'vd_V', 'id_A_per_um', 'is_A_per_um', 'ig_A_per_um', 'kcl_pass']); w.writerows(rows_out)
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6, 4.5)); a = np.array([r_[:3] for r_ in rows_out])
        for v in meta['output_vgs']: sel = a[:, 0] == v; ax.plot(a[sel, 1], a[sel, 2] * 1e6, '-o', ms=2.5, label=f'Vg = {v:g} V')
        ax.set_xlabel('Vd (V)'); ax.set_ylabel('Id (uA/um)'); ax.set_title(f'{t} nm ID-VD PREDICTION ({rid})'); ax.grid(alpha=.3); ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(dest / 'idvd_prediction.png', dpi=130); plt.close(fig)
    except Exception: pass
    ex['validation'] = {'max_kcl_abs_A': worst, 'kcl_fail_count': fails}
    status = 'REAL_ATLAS_PREDICTION' if fails == 0 else 'KCL_FAILED'
    finish(status, 'yes' if not sc['convergence_flags'] else 'yes-with-flags', f'{status}: ID-VD Vg={meta["output_vgs"]}; points {len(rows_out)}; maxKCL {worst:.1e}')
    print(json.dumps({'run_id': rid, 'status': status, 'points': len(rows_out), 'maxKCL_A': worst, 'elapsed_s': round(el)}, indent=1))
    if fails: raise RuntimeError(f'{rid}: KCL failed at {fails} points; inspect {dest}/output_characteristics.csv')
    return dest

def rescore(run_dir, reason):
    """Redo validation + scoring of an existing run from its exported currents (no simulator call). The original
    execution.json is kept as execution_before_rescore.json and a RESCORED row is appended to RUN_INDEX.csv."""
    dest = Path(run_dir) if Path(run_dir).is_absolute() else ROOT / run_dir
    ex = json.loads((dest / 'execution.json').read_text()); t = float(ex['thickness_nm']); rid = ex['run_id']
    if not (dest / 'execution_before_rescore.json').exists(): shutil.copy(dest / 'execution.json', dest / 'execution_before_rescore.json')
    m, g, s = load_configs(); vg, meas = read_meas(t)
    xv, idr = read_xy(dest / 'idvg.dat'); xg, igr = read_xy(dest / 'igvg.dat'); xs, isr = read_xy(dest / 'isvg.dat'); igr = np.interp(xv, xg, igr); isr = np.interp(xv, xs, isr)
    signed, v, verdict = validate(dest, xv, idr, isr, igr, meas_floor(vg, meas), s); ex['validation'] = v; ex['rescore'] = {'reason': reason, 'timestamp_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'previous_status': ex.get('status')}
    row = {'run_id': rid, 'timestamp_utc': ex['rescore']['timestamp_utc'], 'thickness_nm': t, 'label': ex['label'], 'deck_sha256': sha((dest / 'device.in').read_text()), 'model_sha256': sha((dest / 'material_model_used.json').read_text()),
           'command': 'RESCORE (no simulator call)', 'simulator': 'DeckBuild 5.0.10.R + ATLAS 5.28.1.R', 'exit_code': ex.get('returncode'), 'converged': 'yes', 'elapsed_s': f'{ex.get("elapsed_s", 0):.1f}', 'output_dir': str(dest.relative_to(ROOT)).replace('\\', '/')}
    if verdict != 'OK':
        ex['status'] = verdict; (dest / 'execution.json').write_text(json.dumps(ex, indent=2, default=float)); append({**row, 'notes': f'RESCORED ({reason}): still {verdict}, max KCL {v["max_kcl_abs_A"]:.2g} A'}); raise RuntimeError(f'{rid}: {verdict} after rescore')
    pred = np.interp(vg, xv, signed); met, active, le = score(vg, meas, pred, t, s); ex['fit_metrics'] = met
    ex['device_metrics_sim'] = metrics(vg, pred, True, t); ex['device_metrics_exp'] = metrics(vg, meas, False, t); ex['status'] = 'REAL_ATLAS_SCORED'
    with (dest / 'comparison.csv').open('w', newline='') as f:
        w = csv.writer(f); w.writerow(['vg_V', 'measured_A_per_um', 'atlas_A_per_um', 'log10_error', 'linear_error_A_per_um', 'active_fit_region']); w.writerows(zip(vg, meas, pred, le, pred - meas, active.astype(int)))
    plots(dest, vg, meas, pred, t, rid); (dest / 'execution.json').write_text(json.dumps(ex, indent=2, default=float))
    note = f'RESCORED ({reason}): active RMSE {met["regions"]["active"]["rmse_log10"]:.4f} dec; Id(3V) {met["on_error_3V_percent"]:+.2f}%; nonpos {met["nonpositive_pred_count"]}; maxKCL {v["max_kcl_abs_A"]:.1e}'
    append({**row, 'notes': note}); print(note); return dest

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--rescore', help='existing run directory: redo validation/scoring from its exported currents (no launch)'); ap.add_argument('--reason', default='rescore')
    ap.add_argument('--thickness', type=float); ap.add_argument('--label', default='run'); ap.add_argument('--override', action='append', default=[])
    ap.add_argument('--predict', action='store_true', help='PREDICTION transfer run (2026-10-06): any thickness, no measured curve, nothing scored')
    ap.add_argument('--stride', type=int, default=1); ap.add_argument('--vg-min', type=float); ap.add_argument('--timeout', type=int); ap.add_argument('--smoke', action='store_true')
    ap.add_argument('--vstep', type=float, help='single-step ATLAS stepped sweep, e.g. 0.1 (overrides --segments)')
    ap.add_argument('--segments', default='config', help="stepped sweep 'end:step,end:step,...' e.g. '-1:0.2,1.5:0.05,3:0.1'; 'none' = per-point; default from solver.yaml")
    ap.add_argument('--structure', choices=['config', 'full', 'reduced'], default='config', help='full = physical metal/dielectric volumes; default from geometry.yaml')
    ap.add_argument('--output-vgs', help="PREDICTION mode: ID-VD families at these gate voltages, e.g. '1,2,3'")
    ap.add_argument('--vd-segments', default='0.5:0.05,3:0.1', help="drain sweep 'end:step,...' from 0 V for --output-vgs"); a = ap.parse_args()
    if a.rescore: rescore(a.rescore, a.reason); return
    if a.thickness is None: ap.error('--thickness required')
    if not a.predict and a.thickness not in (2.0, 6.3, 13.2, 31.8): ap.error('no measured curve for this thickness: use --predict')
    if a.output_vgs:
        execute_output(a.thickness, a.label, a.override, [float(v) for v in a.output_vgs.split(',')], parse_segments(a.vd_segments), a.timeout); return
    execute(a.thickness, a.label, a.override, a.stride, a.vg_min, a.timeout, a.smoke, a.vstep,
            segments=('config' if a.segments == 'config' else parse_segments(a.segments)), full=('config' if a.structure == 'config' else a.structure == 'full'),
            predict=a.predict)

if __name__ == '__main__':
    try: main()
    except RuntimeError as e: print('FAILED:', e, file=sys.stderr); sys.exit(2)
