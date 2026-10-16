"""Tests of p1_floor.py on SYNTHETIC run directories only (written to ./test_tmp_p1, removed at the end). No real run directory, no S6 or
P1 output and no measured curve is read (the measured floors are the frozen constants of post_run_checks.FLOORS, used by the frozen rule).

    & <venv python> -I -B analysis_2026-10-10_campaign/test_p1_floor.py
"""
import csv, json, math, shutil, sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent; TMP = HERE / 'test_tmp_p1'
sys.path.insert(0, str(HERE))
import p1_floor as P   # noqa: E402

RES = []


def expect(name, got, want, tol=None):
    ok = (abs(got - want) <= tol * max(1.0, abs(want))) if (tol is not None and isinstance(got, (int, float)) and got is not None) else got == want
    RES.append(bool(ok)); print(('PASS ' if ok else 'FAIL ') + name + ('' if ok else f'  got {got!r} want {want!r}'))


def strip_dir(name, t, g, lp=20.0, status='REAL_ATLAS_STRIP', nan_at=None):
    d = TMP / name; d.mkdir(parents=True, exist_ok=True); vds = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
    with (d / 'strip_iv.csv').open('w', newline='') as f:
        w = csv.writer(f); w.writerow(['vd_V', 'id_raw_A', 'is_raw_A', 'id_A_per_um', 'kcl_abs_A', 'kcl_pass'])
        for v in vds:
            i = float('nan') if nan_at == v else g * v
            w.writerow([v, i, -i, i, 0.0, 1])
    ex = {'run_id': name, 'thickness_nm': t, 'label': f'c10_s6_syn_{name}', 'mode': 'strip', 'status': status, 'returncode': 0, 'timed_out': False,
          'scan': {'finished': True, 'errors': []}, 'validation': {'requested_points': len(vds), 'kcl_abs_limit_applied_A': 1e-17}, 'strip': {'L_p_um': lp}}
    (d / 'execution.json').write_text(json.dumps(ex)); return d


def p1_dir(name, t, ia, status='REAL_ATLAS_PREDICTION', vgs=None, kcl_bad=None, drop=None):
    """ia(vg, vd) -> drain current A/um"""
    d = TMP / name; d.mkdir(parents=True, exist_ok=True); vgs = vgs or P.VGS_REG
    vds = [round(0.02 * k, 6) for k in range(1, 6)] + [round(0.1 + 0.05 * k, 6) for k in range(1, 13)] + [round(0.7 + 0.1 * k, 6) for k in range(1, 24)]
    with (d / 'output_characteristics.csv').open('w', newline='') as f:
        w = csv.writer(f); w.writerow(['vg_V', 'vd_V', 'id_A_per_um', 'is_A_per_um', 'ig_A_per_um', 'kcl_pass'])
        for vg in vgs:
            for vd in vds:
                if drop == (vg, vd): continue
                i = ia(vg, vd); w.writerow([vg, vd, i, -i, 0.0, 0 if kcl_bad == (vg, vd) else 1])
    ex = {'run_id': name, 'thickness_nm': t, 'label': f'c10_p1_syn_{name}', 'mode': 'output_prediction', 'status': status, 'returncode': 0, 'timed_out': False,
          'scan': {'finished': True, 'errors': []}, 'output_vgs': list(vgs)}
    (d / 'execution.json').write_text(json.dumps(ex)); return d


def main():
    shutil.rmtree(TMP, ignore_errors=True)
    try:
        M = P.scorer(); F = M.pc.FLOORS
        expect('diffusion competing value 1.021', round(P.COMPETING['diffusion']['R'], 3), 1.021)
        expect('strip competing value 7.0 +- 0.5', (P.COMPETING['strip_HB']['R'], P.COMPETING['strip_HB']['band']), (7.0, 0.5))
        g = {2.0: 1e-16, 6.3: 1e-15, 13.2: 1e-14}   # synthetic ohmic strips: I = g V_D
        S = {t: strip_dir(f's{t}', t, g[t]) for t in P.FILMS}
        tiny = {t: p1_dir(f'p{t}', t, lambda vg, vd: 1e-19) for t in P.FILMS}   # intrinsic channel below resolution
        r = P.predict(S, tiny, M)
        expect('sealed', P.seal_ok(r), True)
        expect('verdict COMPUTED', r['verdict'], 'COMPUTED')
        expect('(W/L)_par = FLOOR(13.2) / (I_strip(13.2, 0.7) L_p)', r['WL_par_per_um'], F[13.2] / (g[13.2] * 0.7 * 20.0), 1e-12)
        f13 = r['films']['13.2']['V_G']['-2.0']
        expect('13.2 nm floor at 0.7 V == the measured floor (calibration identity)', f13['points']['0.7']['I_floor_pred_A_per_um'], F[13.2], 1e-12)
        expect('ohmic strip, censored ATLAS: R_floor == 7', f13['R_floor'], 7.0, 1e-12)
        expect('censored ATLAS: R_ATLAS None, state below resolution', (f13['R_ATLAS'], f13['points']['0.1']['ATLAS_state'].startswith('below resolution')), (None, True))
        f2 = r['films']['2.0']['V_G']['-1.0']['points']['0.7']
        expect('2.0 nm transfer: floor = F13 x g2 / g13', f2['I_floor_pred_A_per_um'], F[13.2] * g[2.0] / g[13.2], 1e-12)
        expect('R_strip == 7 for an ohmic strip', r['films']['6.3']['R_strip'], 7.0, 1e-12)
        diff = {t: p1_dir(f'q{t}', t, lambda vg, vd: 1e-12 * (1 - math.exp(-vd / 0.025852))) for t in P.FILMS}   # diffusion-like channel, resolved
        r2 = P.predict(S, diff, M); p = r2['films']['2.0']['V_G']['-0.5']
        expect('resolved diffusion channel: R_ATLAS == 1.021', round(p['R_ATLAS'], 3), 1.021)
        expect('the ATLAS term is added to the strip term', p['points']['0.7']['I_floor_pred_A_per_um'],
               1e-12 * (1 - math.exp(-0.7 / 0.025852)) + F[13.2] * g[2.0] / g[13.2], 1e-12)
        expect('ATLAS fraction reported', 0 < p['points']['0.1']['ATLAS_fraction'] <= 1, True)
        expect('|I_S,pred| = |I_S,ATLAS| + strip term', p['points']['0.3']['abs_I_S_pred_A_per_um'],
               1e-12 * (1 - math.exp(-0.3 / 0.025852)) + F[13.2] * g[2.0] * 0.3 / (g[13.2] * 0.7), 1e-12)
        kb = dict(diff); kb[6.3] = p1_dir('k6', 6.3, lambda vg, vd: 1e-12, status='KCL_FAILED', kcl_bad=(-1.0, 0.1))
        r3 = P.predict(S, kb, M)
        expect('KCL_FAILED run accepted, the failed point censored', r3['films']['6.3']['V_G']['-1.0']['points']['0.1']['ATLAS_state'], 'censored (KCL)')
        bad = dict(diff); bad[2.0] = p1_dir('b2', 2.0, lambda vg, vd: 1e-12, status='TIMEOUT')
        r4 = P.predict(S, bad, M)
        expect('a failed P1 run: that film UNRESOLVED, verdict PARTIAL', (r4['films']['2.0']['verdict'].startswith('UNRESOLVED'), r4['verdict'].startswith('PARTIAL')), (True, True))
        miss = dict(diff); miss[13.2] = p1_dir('m13', 13.2, lambda vg, vd: 1e-12, drop=(-2.0, 0.7))
        expect('a missing registered point: UNRESOLVED', P.predict(S, miss, M)['films']['13.2']['verdict'].startswith('UNRESOLVED'), True)
        wv = dict(diff); wv[6.3] = p1_dir('w6', 6.3, lambda vg, vd: 1e-12, vgs=[-2.0, -1.0, -0.5])
        expect('output_vgs not as registered: UNRESOLVED', P.predict(S, wv, M)['films']['6.3']['verdict'].startswith('UNRESOLVED'), True)
        s2 = dict(S); s2[13.2] = strip_dir('n13', 13.2, g[13.2], nan_at=0.4)
        expect('a non-finite strip export: UNRESOLVED (frozen run_problems)', P.predict(s2, diff, M)['verdict'].startswith('UNRESOLVED'), True)
        s3 = dict(S); s3[6.3] = strip_dir('l6', 6.3, g[6.3], lp=10.0)
        expect('different L_p: UNRESOLVED', P.predict(s3, diff, M)['verdict'].startswith('UNRESOLVED'), True)
        s4 = dict(S); s4[13.2] = strip_dir('z13', 13.2, 1e-20)
        expect('13.2 nm strip below resolution at 0.7 V: UNRESOLVED', P.predict(s4, diff, M)['verdict'].startswith('UNRESOLVED (13.2'), True)
        s5 = dict(S); s5[2.0] = strip_dir('t2', 6.3, g[2.0])
        expect('strip run of the wrong film: UNRESOLVED', P.predict(s5, diff, M)['verdict'].startswith('UNRESOLVED'), True)
        expect('deterministic', P.predict(S, tiny, M)['sha256'], r['sha256'])
        expect('frozen pins checked (score_register c0f28bb9)', P.FROZEN['score_register.py'][:8], 'c0f28bb9')
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    n = sum(RES); print(f'{n}/{len(RES)} passed'); return 0 if n == len(RES) else 1


if __name__ == '__main__':
    sys.exit(main())
