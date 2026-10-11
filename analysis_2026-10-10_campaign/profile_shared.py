#!/usr/bin/env python3
"""C13 (CAMPAIGN_DESIGN.md 5.2, 6): exact shift/scale profiling of the shared parameters, offline. NO simulator call; reads
finished run directories (execution.json, material_model_used.json, terminal_currents.csv) and the measured curves; writes only
analysis_2026-10-10_campaign/profile/*.json.

  python analysis_2026-10-10_campaign/profile_shared.py check NATIVE_RUN REFERENCE_RUN
      S1-07 / S3-27 / S4c native check: the reference curve transformed by the Q_f and MUN differences of the two runs
      (read from their material_model_used.json; every other model, solver and geometry input must be identical) must
      reproduce the native run within 0.01 dec on every J-window point (CAMPAIGN_DESIGN 5.2 / S1 rule). Each point is compared
      forward (reference -> native) or, where the shift leaves the solved range, inverse (native -> reference); a point covered
      in neither direction makes the verdict UNVERIFIED. Tunnelling/Schottky pairs: NOT APPLICABLE. Also reports the full-curve
      maximum over the covered native points. Exit 0 PASS, 1 FAIL, 3 otherwise.
  python analysis_2026-10-10_campaign/profile_shared.py profile RUN_2p0 RUN_6p3 RUN_13p2 [--tag NAME]
      shared profiling of (dV0 via one Q_f, mu_inf, ell) on a film triple launched with the same shared inputs; reports the
      start and profiled sqrt(J), per-film RMSE_sub / RMSE_on, window coverage (< 95 % -> flagged, confirm natively), the
      profiled Q_f and mu law, and the DIAGNOSTIC per-film free shift + scale (shape-only residual; never a model).
      Refused when the three runs do not share one Q_f and one C_ox, or when a tunnelling/Schottky option is on (then
      --allow-approximate labels the result APPROXIMATE). Verdict OK / APPROXIMATE / UNVERIFIED (coverage < 95 % or optimizer).
  python analysis_2026-10-10_campaign/profile_shared.py adopt BRANCH_2p0 BRANCH_6p3 BRANCH_13p2 -- BASE_2p0 BASE_6p3 BASE_13p2
      S3 adoption arithmetic (both triples profiled the same way): sqrt(J) gain >= 0.03 dec and no film's RMSE_sub / RMSE_on
      worse by > 0.03 dec. Convergence at all films and activation (post_run_checks.py ACTIVE_AS_REQUESTED) are checked by
      the caller; the verdict line says so.
Transformations (exact in the continuum equations, CAMPAIGN_DESIGN 5.2):
  shift  I(V_G; Q_f) = I(V_G + q (Q_f - Q_f0) / C_ox; Q_f0)    (front Q_f sheet and gate both span the device);
  scale  I(V_G; MUN) = (MUN / MUN0) I(V_G; MUN0)               (electron-only DD, every electron mobility x one constant,
                                                                 incl. IGZO.TOKYO; NOT for Schottky or tunnelling runs).
  The mu law is mu_band(t) = mu_inf (m_ref / m*(t)) / (1 + ell / t); MUN = mu_band (1 - Dsr/t)^2, so the per-film scale is
  mu_band,new(t) / mu_band,run(t). No extrapolation: transformed points outside the solved V_G range are dropped and counted.
NOT IMPLEMENTED YET (needed only from S4b on; not needed for the S1 decisions, the S3 adoption or S4a): the S4b quadratic
surrogate, the S5 leave-one-film-out candidate selection and the identifiability Jacobian (CAMPAIGN_DESIGN 5.4). The
subcommands 'surrogate', 'loo' and 'jacobian' stop with that message."""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

import campaign_tools as ct
import campaign_extract as ce

OUT = ct.HERE / 'profile'
Q = 1.602176634e-19
TOL_DEC = 0.01


def run_info(run):
    d, exj, vg, i = ce.load_run(run); t = float(exj['thickness_nm']); ov = list(exj.get('overrides', []))
    m = json.loads((d / 'material_model_used.json').read_text())
    p = ct.bd.material_at(m, t)
    _, g, s = ct.configs(ct.V3, [o for o in ov if o.startswith(('solver.', 'geometry.'))])
    po = s.get('physics_options') or {}   # effective settings (physics_options.yaml defaults + overrides), not override strings
    breakers = [k for k in ('gate_tunnelling', 'oxide_tat', 'schottky_sd') if ct.bd.on((po.get(k) or {}).get('enabled'))]
    return dict(dir=d, run_id=exj['run_id'], t=t, vg=vg, i=i, m=m, p=p, cox=ct.bd.cox(g), overrides=ov, breakers=breakers,
                mstar=p['mstar_m0'], mu_band=p['mu_band'], mun=p['mu0'], qf=p['Qf_cm2'])


def transformed_log(r, dQf, scale, x):
    """log10 of the run's current transformed to Q_f + dQf and MUN x scale, at gate voltages x (NaN where not covered)"""
    return np.log10(scale) + ce.log_interp(r['vg'], r['i'], np.asarray(x, float) + Q * dQf / r['cox'])


def strip_keys(m, t):
    """material model without the two profiled inputs (Q_f value, mu_band at t / shared law), for the identity check"""
    m = json.loads(json.dumps(m)); m['traps']['fixed_interface_charge_Qf_cm2']['value'] = None
    mu = m['thickness_laws']['mu0_cm2Vs']; mu['mu_band_fitted'] = None; mu.pop('shared_law', None)
    bs = m['traps'].get('back_surface_donor_sheet')
    if bs is not None and not float(bs.get('peak_cm2_eV', 0) or 0): m['traps'].pop('back_surface_donor_sheet')   # absent == zero sheet (older model files)
    return m


def diff_dicts(a, b, path=''):
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b), key=str): out += diff_dicts(a.get(k), b.get(k), f'{path}.{k}' if path else str(k))
        return out
    return [] if a == b else [f'{path}: {a!r} vs {b!r}']


def check(native, ref):
    a, b = run_info(native), run_info(ref)
    if abs(a['t'] - b['t']) > 1e-9: raise SystemExit('check needs two runs of the same film')
    dQf = a['qf'] - b['qf']; scale = a['mun'] / b['mun']
    other = diff_dicts(strip_keys(a['m'], a['t']), strip_keys(b['m'], b['t']))
    sg_a = sorted(o for o in a['overrides'] if o.startswith(('solver.', 'geometry.'))); sg_b = sorted(o for o in b['overrides'] if o.startswith(('solver.', 'geometry.')))
    res = {'native': a['run_id'], 'reference': b['run_id'], 'thickness_nm': a['t'], 'dQf_cm2': dQf, 'dV_shift_V': -Q * dQf / a['cox'],
           'mun_scale': scale, 'cox_F_cm2': a['cox'], 'other_material_differences': other,
           'solver_geometry_override_differences': sorted(set(sg_a) ^ set(sg_b)), 'exactness_breakers': a['breakers'] + b['breakers']}
    info, _ = ce.measured(); M = info.get(a['t'])
    lt_native = ce.log_interp(a['vg'], a['i'], a['vg']); lt = transformed_log(b, dQf, scale, a['vg'])
    cov = np.isfinite(lt) & (a['i'] > 1e-14) & (lt > -14)   # full-curve check where both currents exceed 1e-14 A/um (deep off-state is noise-level)
    res['native_points_covered_above_1e-14'] = int(cov.sum()); res['native_points'] = int(len(a['vg']))
    res['max_abs_dev_native_grid_above_1e-14_dec'] = float(np.max(np.abs(lt[cov] - lt_native[cov]))) if cov.any() else None
    if M is None: res['verdict'] = 'UNVERIFIED (no measured film: no J windows)'; return res
    masks = {'sub': (M['i'] >= 10 * M['floor']) & (M['i'] <= 1e-9), 'on': (M['vg'] >= 1 - 1e-9) & (M['vg'] <= 3 + 1e-9)}
    # both directions test the same identity; a shift moves one end of the window out of the solved range in one direction only
    # (S1-07: forward loses the top of the on window, inverse covers it), so each J-window point is compared where it is covered
    fwd = (ce.log_interp(a['vg'], a['i'], M['vg']), transformed_log(b, dQf, scale, M['vg']))          # native vs transformed reference
    inv = (ce.log_interp(b['vg'], b['i'], M['vg']), transformed_log(a, -dQf, 1.0 / scale, M['vg']))   # reference vs back-transformed native
    for k, msk in masks.items():
        cf = msk & np.isfinite(fwd[0]) & np.isfinite(fwd[1]); ci = msk & np.isfinite(inv[0]) & np.isfinite(inv[1])
        dev = np.full(len(M['vg']), np.nan); dev[cf] = np.abs(fwd[1][cf] - fwd[0][cf])
        both = ci & np.isnan(dev); dev[both] = np.abs(inv[1][both] - inv[0][both])
        cov = msk & np.isfinite(dev)
        res[f'J_window_{k}'] = {'points': int(msk.sum()), 'covered_forward': int(cf.sum()), 'covered_inverse': int(ci.sum()), 'covered': int(cov.sum()),
                                'max_abs_dev_dec': float(np.max(dev[cov])) if cov.any() else None}
    devs = [res[f'J_window_{k}']['max_abs_dev_dec'] for k in masks]
    full = all(res[f'J_window_{k}']['covered'] == res[f'J_window_{k}']['points'] for k in masks)
    if other or res['solver_geometry_override_differences']: res['verdict'] = 'NOT A PURE Q_f/MUN PAIR (see differences): no verdict'
    elif res['exactness_breakers']: res['verdict'] = 'NOT APPLICABLE: tunnelling/Schottky run, exact scaling is not claimed (CAMPAIGN_DESIGN 5.2)'
    elif any(x is None for x in devs) or not full: res['verdict'] = 'UNVERIFIED (not every J-window point is covered in either direction)'
    else: res['verdict'] = ('PASS: profiling exact within 0.01 dec on every J-window point' if max(devs) <= TOL_DEC else
                            'FAIL: profiling approximate -> every S4b candidate run natively at the profiled Q_f and MUN (S1 rule)')
    return res


def mu_law(mu_inf, ell, t, mstar, m_ref=0.208): return mu_inf * (m_ref / mstar) / (1.0 + ell / t)


def triple_J(R, M, dQf, mu_inf, ell):
    per = {}; terms = []
    for r in R:
        s = mu_law(mu_inf, ell, r['t'], r['mstar']) / r['mu_band']; Mt = M[r['t']]
        lt = transformed_log(r, dQf, s, Mt['vg']); lm = np.log10(Mt['i'])
        masks = {'sub': (Mt['i'] >= 10 * Mt['floor']) & (Mt['i'] <= 1e-9), 'on': (Mt['vg'] >= 1 - 1e-9) & (Mt['vg'] <= 3 + 1e-9)}
        f = {}
        for k, msk in masks.items():
            c = msk & np.isfinite(lt); n = int(msk.sum())
            f[k] = {'rmse_dec': float(np.sqrt(np.mean((lt[c] - lm[c]) ** 2))) if c.any() else np.nan, 'coverage': float(c.sum()) / n if n else 0.0}
        f['J_term'] = (f['sub']['rmse_dec'] ** 2 + f['on']['rmse_dec'] ** 2) / 2; f['mun_scale'] = s; per[r['t']] = f; terms.append(f['J_term'])
    return float(np.mean(terms)), per


def profile(runs, tag=None, allow_approximate=False):
    R = [run_info(x) for x in runs]; info, _ = ce.measured()
    if sorted(r['t'] for r in R) != [2.0, 6.3, 13.2]: raise SystemExit('profile needs one run per film 2.0 / 6.3 / 13.2 nm')
    # one shared Q_f and one C_ox are the premise of a single profiled Q_f (review fix: refuse, do not warn)
    q0 = R[0]['qf']
    if any(abs(r['qf'] - q0) > 1e-9 * max(abs(q0), 1.0) for r in R): raise SystemExit(f'refused: the three runs do not share one Q_f ({[r["qf"] for r in R]})')
    if len({round(r['cox'], 15) for r in R}) > 1: raise SystemExit('refused: different C_ox in the triple')
    warn = []; brk = [f'{r["run_id"]}: {r["breakers"]}' for r in R if r['breakers']]
    if brk and not allow_approximate: raise SystemExit(f'refused: tunnelling/Schottky option on, the shift/scale profiling is not exact: {brk} (--allow-approximate labels the result APPROXIMATE)')
    if brk: warn.append(f'APPROXIMATE profiling (tunnelling/Schottky option on): {brk}; confirm natively before any adoption')
    sl = (R[0]['m']['thickness_laws']['mu0_cm2Vs'].get('shared_law') or {})
    mu0, ell0 = float(sl.get('mu_inf_cm2Vs', 100.005)), float(sl.get('ell_nm', 7.248))
    # start: the curves as launched (dQf = 0, every scale 1)
    terms0 = {}
    for r in R:
        Mt = info[r['t']]; w = ce.window_rmse(Mt['vg'], Mt['i'], Mt['floor'], r['vg'], r['i']); terms0[r['t']] = {'rmse_sub': w['sub']['rmse_dec'], 'rmse_on': w['on']['rmse_dec'], 'J_term': w['J_term']}
    J0 = float(np.mean([v['J_term'] for v in terms0.values()]))
    cox = R[0]['cox']; dq_max = 0.5 * cox / Q   # |dV0| <= 0.5 V
    def obj(x):
        dQf, lmu, ell = x[0] * 1e12, x[1], x[2]
        if abs(dQf) > dq_max or not (np.log(10) <= lmu <= np.log(300)) or not (0 <= ell <= 50): return 1e3
        J, per = triple_J(R, info, dQf, float(np.exp(lmu)), ell)
        return J if np.isfinite(J) else 1e3
    best = None
    for dv in np.linspace(-0.4, 0.4, 9):
        x0 = [dv * cox / Q / 1e12, np.log(mu0), ell0]
        r_ = minimize(obj, x0, method='Nelder-Mead', options={'xatol': 1e-6, 'fatol': 1e-10, 'maxiter': 4000})
        if best is None or r_.fun < best.fun: best = r_
    dQf, mu_inf, ell = best.x[0] * 1e12, float(np.exp(best.x[1])), float(best.x[2])
    J, per = triple_J(R, info, dQf, mu_inf, ell)
    # diagnostic only: per-film free shift + scale (shape-only residual), never a model
    shape = {}
    for r in R:
        def o2(x, r=r):
            Mt = info[r['t']]; lt = transformed_log(r, x[0] * 1e12, float(np.exp(x[1])), Mt['vg']); lm = np.log10(Mt['i'])
            ms = [(Mt['i'] >= 10 * Mt['floor']) & (Mt['i'] <= 1e-9), (Mt['vg'] >= 1 - 1e-9) & (Mt['vg'] <= 3 + 1e-9)]
            v = [np.mean((lt[m & np.isfinite(lt)] - lm[m & np.isfinite(lt)]) ** 2) if (m & np.isfinite(lt)).any() else 1e3 for m in ms]
            return float(np.mean(v)) if abs(x[0] * 1e12) <= dq_max else 1e3
        b2 = min((minimize(o2, [dv * cox / Q / 1e12, 0.0], method='Nelder-Mead') for dv in np.linspace(-0.4, 0.4, 5)), key=lambda z: z.fun)
        shape[r['t']] = {'free_dV_V': -Q * b2.x[0] * 1e12 / cox, 'free_scale': float(np.exp(b2.x[1])), 'shape_only_sqrtJ_dec': float(np.sqrt(b2.fun))}
    cov_ok = all(min(f['sub']['coverage'], f['on']['coverage']) >= 0.95 for f in per.values())
    res = {'tag': tag, 'runs': [r['run_id'] for r in R], 'warnings': warn, 'start': {'sqrtJ_dec': float(np.sqrt(J0)), 'per_film': terms0},
           'profiled': {'sqrtJ_dec': float(np.sqrt(J)), 'Qf_cm2': R[0]['qf'] + dQf, 'dQf_cm2': dQf, 'dV0_V': -Q * dQf / cox, 'mu_inf_cm2Vs': mu_inf, 'ell_nm': ell,
                        'per_film': {str(t): {'rmse_sub_dec': f['sub']['rmse_dec'], 'rmse_on_dec': f['on']['rmse_dec'], 'coverage_sub': f['sub']['coverage'],
                                              'coverage_on': f['on']['coverage'], 'mun_scale': f['mun_scale'], 'J_term': f['J_term']} for t, f in per.items()},
                        'coverage_ok_95pct': cov_ok, 'optimizer': {'fun': float(best.fun), 'nit': int(best.nit), 'success': bool(best.success)}},
           'diagnostic_shape_only': shape,
           'labels': ('APPROXIMATE (tunnelling/Schottky run) ' if brk else '') + 'Q_f, mu_inf, ell: FITTED (shared, exact-transformation profiling of launched '
                     'curves); calibration, not validation. The per-film free shift/scale is a diagnostic, never a model.'}
    if not cov_ok: res['warnings'].append('window coverage < 95 %: confirm the optimum natively (CAMPAIGN_DESIGN 5.2)')
    res['verdict'] = ('UNVERIFIED (coverage < 95 % or optimizer not converged: confirm natively)' if not (cov_ok and best.success) else
                      'APPROXIMATE' if brk else 'OK')
    return res


def adopt(branch, base, allow_approximate=False):
    a, b = profile(branch, 'branch', allow_approximate), profile(base, 'base', allow_approximate); gain = b['profiled']['sqrtJ_dec'] - a['profiled']['sqrtJ_dec']
    worse = {t: {k: a['profiled']['per_film'][t][k] - b['profiled']['per_film'][t][k] for k in ('rmse_sub_dec', 'rmse_on_dec')} for t in a['profiled']['per_film']}
    ok = gain >= 0.03 and all(v <= 0.03 for d in worse.values() for v in d.values())
    pre = 'UNVERIFIED: ' if 'UNVERIFIED' in a['verdict'] + b['verdict'] else 'APPROXIMATE: ' if 'APPROXIMATE' in (a['verdict'], b['verdict']) else ''
    return {'branch': a, 'base': b, 'sqrtJ_gain_dec': gain, 'per_film_worsening_dec': worse,
            'verdict': pre + ('ARITHMETIC PASS' if ok else 'ARITHMETIC FAIL') + ' (also required: converged at all films; activation ACTIVE_AS_REQUESTED; '
                       'not a pure shift/scale effect; at most two branches' + ('; Schottky: the reserve native check' if pre.startswith('APPROX') else '') + ')'}


def main(argv):
    if not argv: print(__doc__); return 2
    OUT.mkdir(exist_ok=True); cmd = argv[0]; approx = '--allow-approximate' in argv
    tag = argv[argv.index('--tag') + 1] if '--tag' in argv else None
    pos = [x for i, x in enumerate(argv) if not x.startswith('--allow') and x != '--tag' and not (i and argv[i - 1] == '--tag')]   # positional words; '--' kept
    if cmd in ('surrogate', 'loo', 'jacobian'):
        print(f'{cmd}: NOT IMPLEMENTED YET (needed from S4b / S5 / the identifiability report on; see the module docstring)'); return 3
    try:
        res, fn = run_cmd(cmd, pos, tag, approx)
    except SystemExit as e:   # refusals (unequal Q_f / C_ox, tunnelling or Schottky without --allow-approximate, wrong films)
        print(f'REFUSED: {e}'); return 3
    if res is None: print(__doc__); return 2
    fn.write_text(json.dumps(res, indent=1, default=float)); print(json.dumps(res, indent=1, default=float))
    v = str(res.get('verdict', ''))   # exit 0 only for a clean pass: PASS / OK / ARITHMETIC PASS; FAIL -> 1; anything else -> 3
    return 0 if v.startswith(('PASS', 'OK', 'ARITHMETIC PASS')) else 1 if v.startswith(('FAIL', 'ARITHMETIC FAIL')) else 3


def run_cmd(cmd, pos, tag, approx):
    if cmd == 'check':
        res = check(pos[1], pos[2]); fn = OUT / f'check_{res["native"]}_vs_{res["reference"]}.json'
    elif cmd == 'profile':
        if len(pos) != 4: raise SystemExit('profile needs exactly three run directories')
        res = profile(pos[1:4], tag, approx); fn = OUT / f'profile_{tag or "_".join(res["runs"])}.json'
    elif cmd == 'adopt':
        k = pos.index('--') if '--' in pos else -1
        if k != 4 or len(pos) != 8: raise SystemExit('adopt needs: adopt B2 B6 B13 -- R2 R6 R13')
        res = adopt(pos[1:4], pos[5:8], approx); fn = OUT / f'adopt_{"_".join(res["branch"]["runs"])}.json'
    else: return None, None
    return res, fn


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
