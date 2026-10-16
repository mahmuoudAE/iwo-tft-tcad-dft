"""P1 floor model (PA-15 / REG-001, 2026-10-16; no Codex review, D-63): the frozen procedure that turns the frozen strip decks S6-24..26
and the P1 output runs into the registered P1 predictions. Written and committed BEFORE any S6-24..26 or P1 output is read.

    python -I -B analysis_2026-10-10_campaign/p1_floor.py predict --strip 2.0=DIR 6.3=DIR 13.2=DIR --p1 2.0=DIR 6.3=DIR 13.2=DIR [--out FILE]

Rules (05_dft_and_predictive_layer.md 3.4 P1; register H-B; frozen scorer score_register.py c0f28bb9 hb_transfer):
  (W/L)_par   FITTED on 13.2 nm only (the frozen H-B calibration film), exactly as the frozen scorer: (W/L)_par = FLOOR(13.2) /
              (I_strip(13.2, 0.7 V) x L_p), FLOOR = post_run_checks.FLOORS (MEASURED / DERIVED median over V_G -2 .. -0.5 V), L_p from the
              strip runs (must be one value). Strip points through the frozen strip_point (resolution = the frozen PROXY: the runner KCL
              absolute limit of the run, not a demonstrated resolution).
  floor       I_floor,pred(t, V_G, V_D) = I_ATLAS(t, V_G, V_D) + I_strip(t, V_D) x L_p x (W/L)_par at V_D 0.1, 0.3, 0.7 V and V_G -2, -1,
              -0.5 V. I_ATLAS = the P1 output run's drain current at that native point; a point with |I_D| below the resolution (1e-17 A/um,
              the runner KCL absolute limit, PROXY) or failing KCL is CENSORED: it contributes 0 and is labelled; the fraction
              I_ATLAS / I_floor,pred is reported. |I_S,pred| = |I_S,ATLAS| + I_strip x L_p x (W/L)_par (ASSUMED: the strip carries the same
              current into the source). I_G is not predicted (no gate-leakage physics in the frozen model; QTNLSC unresolved, S2-11 FAIL).
  ratios      R_floor = I_floor,pred(0.7) / I_floor,pred(0.1); R_ATLAS = I_ATLAS(0.7) / I_ATLAS(0.1) (only if both resolved);
              R_strip = I_strip(0.7) / I_strip(0.1). Competing frozen values: strip 7.0 +- 0.5 (H-B), diffusion 1.021 (CALCULATED, 300 K).
  validity    strip runs: the frozen run_problems (complete, finite export, scorable status); P1 runs: status REAL_ATLAS_PREDICTION or
              KCL_FAILED (KCL-failed points censored point by point), return code 0, not timed out, no simulator error, the registered
              output_vgs, every used (V_G, V_D) point present and finite. Anything else: the prediction is UNRESOLVED, never estimated.
The record is sealed (sha256 of the canonical JSON) and never overwritten. Labels: COMPUTED (ATLAS) currents; (W/L)_par FITTED on the
measured 13.2 nm floor; L_p ASSUMED; calibration-conditional (the frozen model FAILED S4a / S4c 5.3) and, under A55 (j), sensitivity only.
"""
import csv
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True

PKG = Path(r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1")
HERE = PKG / 'analysis_2026-10-10_campaign'
FROZEN = {'score_register.py': 'c0f28bb942508a81a0f59b4a4c1e720bbfdbe8d9466d7e002476d64dcc10b55a',
          'campaign_extract.py': '1f6f324a0841d50bb20baf7f94b6444d688aaf4cbdf71707594a06f26e3e63ba',
          'campaign_tools.py': '3b0403d9c5cc5423cb80dabc3765f9a781b7a06b512082b6f210971a9417ab0d',
          'post_run_checks.py': '39d3d51d3b2470b1396196bcfce34dc4a8f0a6acd3bcb2a213001dc5ec3ed91f'}
FILMS = (2.0, 6.3, 13.2)
CAL_FILM = 13.2
VGS_REG = [-2.0, -1.0, -0.5, 1.0, 2.0, 3.0]
VG_OFF = (-2.0, -1.0, -0.5)
VD_PTS = (0.1, 0.3, 0.7)
RES_P1 = 1e-17                       # A/um: runner KCL absolute limit (PROXY, not demonstrated)
COMPETING = {'strip_HB': {'R': 7.0, 'band': 0.5, 'label': 'register H-B (frozen 2026-10-10)'},
             'diffusion': {'R': (1 - math.exp(-0.7 / 0.025852)) / (1 - math.exp(-0.1 / 0.025852)), 'label': 'CALCULATED, T = 300 K ASSUMED'}}
P1_STATUS = ('REAL_ATLAS_PREDICTION', 'KCL_FAILED')


def fsha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tsha(s): return hashlib.sha256(s.encode()).hexdigest()


def _canon(d): return json.dumps(d, sort_keys=True, default=float, separators=(',', ':'))


def seal(d):
    d = {k: v for k, v in d.items() if k != 'sha256'}; d['sha256'] = tsha(_canon(d)); return d


def seal_ok(d): return isinstance(d, dict) and d.get('sha256') == tsha(_canon({k: v for k, v in d.items() if k != 'sha256'}))


def scorer():
    """the frozen scorer, loaded only after its sha256 and those of the modules it imports match"""
    bad = [f for f, h in FROZEN.items() if fsha(HERE / f) != h]
    if bad: raise SystemExit(f'frozen files differ: {bad}')
    if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location('score_register_frozen_p1', HERE / 'score_register.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def read_output(d):
    """(execution.json, {(vg, vd): (id, is, kcl_ok)}, problems) of a P1 output run"""
    d = Path(d); p = []
    try: ex = json.loads((d / 'execution.json').read_text())
    except Exception as e: return None, {}, [f'execution.json unreadable ({type(e).__name__})']
    if ex.get('status') not in P1_STATUS: p.append(f'runner status {ex.get("status")}')
    if ex.get('returncode') != 0: p.append(f'return code {ex.get("returncode")}')
    if ex.get('timed_out') is not False: p.append('timed out or no timeout flag')
    if (ex.get('scan') or {}).get('errors'): p.append('simulator error')
    if [float(v) for v in ex.get('output_vgs') or []] != VGS_REG: p.append(f'output_vgs {ex.get("output_vgs")} != {VGS_REG}')
    pts = {}
    f = d / 'output_characteristics.csv'
    if not f.is_file(): return ex, {}, p + ['no output_characteristics.csv']
    with f.open(newline='') as fh:
        for r in csv.DictReader(fh):
            try: k = (round(float(r['vg_V']), 6), round(float(r['vd_V']), 6)); v = (float(r['id_A_per_um']), float(r['is_A_per_um']), int(float(r['kcl_pass'])) == 1)
            except (KeyError, ValueError): p.append('unparsable row'); continue
            if k in pts: p.append(f'duplicate point {k}')
            pts[k] = v
    for vg in VG_OFF:
        for vd in VD_PTS:
            v = pts.get((vg, vd))
            if v is None: p.append(f'missing point V_G {vg} V_D {vd}')
            elif not (math.isfinite(v[0]) and math.isfinite(v[1])): p.append(f'non-finite at V_G {vg} V_D {vd}')
    return ex, pts, p


def atlas_term(v):
    """(current used in the sum, state) of one P1 point: censored below the resolution or on a KCL failure"""
    i = abs(v[0])
    if not v[2]: return 0.0, 'censored (KCL)'
    if i < RES_P1: return 0.0, f'below resolution ({i:.3g} < {RES_P1:g} A/um, PROXY)'
    return i, 'resolved'


def predict(strip_dirs, p1_dirs, M=None):
    M = M or scorer(); out = {'record': 'P1 floor-model prediction (PA-15 / REG-001; frozen p1_floor.py)', 'code_sha256': fsha(Path(__file__)),
                              'frozen': FROZEN, 'floors_measured': {str(t): M.pc.FLOORS[t] for t in FILMS}, 'competing': COMPETING,
                              'inputs': {'strip': {str(t): str(strip_dirs[t]) for t in FILMS}, 'p1': {str(t): str(p1_dirs[t]) for t in FILMS}}}
    strips = {}
    for t in FILMS:
        d, exj, c = M.strip_iv(strip_dirs[t]); strips[t] = (d, exj, c)
    inv = M.usable(*[(x[1], x[2]) for x in strips.values()])
    lp = {x[1].get('strip', {}).get('L_p_um') for x in strips.values()}
    films_t = {t: float(strips[t][1].get('thickness_nm', 'nan')) for t in FILMS}
    if inv or len(lp) != 1 or None in lp or any(abs(films_t[t] - t) > 1e-6 for t in FILMS):
        out['verdict'] = f'UNRESOLVED (strip runs: {inv or ""} L_p {sorted(lp, key=str)} films {films_t})'; return seal(out)
    L_p = float(lp.pop()); res = {t: M.resolution([strips[t][1]], None, None)[0] for t in FILMS}
    I = {t: {vd: M.strip_point(strips[t][2], vd, res[t]) for vd in VD_PTS} for t in FILMS}
    out['strip'] = {str(t): {'run_id': strips[t][1].get('run_id'), 'label': strips[t][1].get('label'), 'resolution_A_per_um': res[t],
                             'I_strip_A_per_um': {str(vd): I[t][vd][0] for vd in VD_PTS}, 'state': {str(vd): I[t][vd][1] for vd in VD_PTS}} for t in FILMS}
    out['L_p_um'] = L_p
    i13 = I[CAL_FILM][0.7][0]
    if i13 is None: out['verdict'] = f'UNRESOLVED (13.2 nm calibration strip at 0.7 V: {I[CAL_FILM][0.7][1]})'; return seal(out)
    wl = M.pc.FLOORS[CAL_FILM] / (i13 * L_p); out['WL_par_per_um'] = wl
    films, unresolved = {}, []
    for t in FILMS:
        ex, pts, prob = read_output(p1_dirs[t])
        if ex is not None and abs(float(ex.get('thickness_nm', 'nan')) - t) > 1e-6: prob.append(f'thickness {ex.get("thickness_nm")} != {t}')
        if prob: films[str(t)] = {'verdict': 'UNRESOLVED (P1 run: ' + '; '.join(prob) + ')'}; unresolved.append(t); continue
        rs = {vd: I[t][vd][0] for vd in VD_PTS}; per = {'run_id': ex.get('run_id'), 'label': ex.get('label'), 'R_strip': (rs[0.7] / rs[0.1]) if rs[0.1] and rs[0.7] else None, 'V_G': {}}
        for vg in VG_OFF:
            row = {}
            for vd in VD_PTS:
                v = pts[(vg, vd)]; ia, sa = atlas_term(v); st = rs[vd] * L_p * wl if rs[vd] is not None else None
                fl = (ia + st) if st is not None else None
                row[str(vd)] = {'I_ATLAS_A_per_um': abs(v[0]), 'ATLAS_state': sa, 'I_strip_term_A_per_um': st,
                                'I_floor_pred_A_per_um': fl, 'log10_I_floor_pred': (math.log10(fl) if fl and fl > 0 else None),
                                'ATLAS_fraction': (ia / fl if fl else None), 'abs_I_S_pred_A_per_um': (abs(v[1]) + st) if st is not None else None}
            f1, f7 = row['0.1']['I_floor_pred_A_per_um'], row['0.7']['I_floor_pred_A_per_um']
            a1, a7 = row['0.1'], row['0.7']
            per['V_G'][str(vg)] = {'points': row, 'R_floor': (f7 / f1) if (f1 and f7) else None,
                                   'R_ATLAS': (a7['I_ATLAS_A_per_um'] / a1['I_ATLAS_A_per_um']) if (a1['ATLAS_state'] == 'resolved' and a7['ATLAS_state'] == 'resolved') else None}
        films[str(t)] = per
    out['films'] = films
    out['verdict'] = 'COMPUTED' if not unresolved else f'PARTIAL: films {unresolved} UNRESOLVED'
    out['labels'] = ('COMPUTED (ATLAS) currents; (W/L)_par FITTED on the measured 13.2 nm floor; L_p ASSUMED; calibration-conditional (the frozen '
                     'model FAILED S4a and S4c 5.3) and sensitivity only under A55 (j); prospective only for data released after the external timestamp')
    return seal(out)


def _pairs(xs):
    d = {}
    for x in xs:
        k, v = x.split('=', 1); d[float(k)] = Path(v) if Path(v).is_absolute() else PKG / v
    if sorted(d) != list(FILMS): raise SystemExit(f'need exactly the films {FILMS}: got {sorted(d)}')
    return d


def main(argv):
    if not argv or argv[0] != 'predict' or '--strip' not in argv or '--p1' not in argv: print(__doc__); return 2
    i, j = argv.index('--strip'), argv.index('--p1'); k = argv.index('--out') if '--out' in argv else len(argv)
    strip = _pairs(argv[i + 1:j]); p1 = _pairs(argv[j + 1:k])
    out = Path(argv[k + 1]) if k < len(argv) else HERE / 'profile' / 'p1_floor_record.json'
    if out.exists(): raise SystemExit(f'{out} exists: never overwritten')
    rec = predict(strip, p1); out.write_text(json.dumps(rec, indent=1, default=float) + '\n')
    print(json.dumps({'record': str(out), 'sha256': rec['sha256'], 'verdict': rec['verdict']}, indent=1)); return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
