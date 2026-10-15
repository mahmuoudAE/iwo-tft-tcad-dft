"""Tests of s4c_confirm_wrapper.py (register A52, PA-18; NO launch; no run directory opened; no repo file written except the temporary
./test_tmp_s4c, removed at the end).

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"; & <venv python> -I -B analysis_2026-10-10_campaign/test_s4c_confirm_wrapper.py
Synthetic native / reference run records (dicts with eligibility, digest, label, t, qf, mu_band, overrides), an injected checker in place of
profile_shared.check and injected file digests; the frozen modules are imported (after their pins are checked) only for _endpoint, seal,
S4C_ROUTE_AVAILABLE and the tolerance constants. The real campaign_matrix.json is read for the entry construction test (no run read).
"""
import json, os, shutil, sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))
import s4c_confirm_wrapper as W  # noqa: E402

TMP = HERE / 'test_tmp_s4c'
results = []


def expect(name, got, want):
    ok = got == want; results.append(ok); print(f"{'ok  ' if ok else 'FAIL'} {name}: {got}", flush=True)


def refused(f, *a, **k):
    try: f(*a, **k); return None
    except SystemExit as e: return str(e)


QF0, QF1 = 1.38345e12, 1.61169e12
MU0, MU1 = 17.6897, 7.81349


def base_ov(t, qf=QF0, mu=MU0, extra=()):
    return ['thickness_laws.Nt_cm3.Nt2=4.4285e+19', 'thickness_laws.WTA_eV.value=0.0572', f'traps.fixed_interface_charge_Qf_cm2.value={qf:.6g}',
            f'thickness_laws.mu0_cm2Vs.mu_band_fitted[{t}]={mu:.6g}', 'solver.tmun=0'] + list(extra)


def record(pss, t=2.0):
    k = W.entry_id('S4c', t)
    rec = {'candidate': 'S4A-04', 'code_sha256': W.FROZEN['profile_s4s5.py'], 'wrapper_sha256': W.wrapper_sha(),
           'entries': {k: {'id': k, 'thickness': t, 'label': W.label('S4c', t), 'overrides': base_ov(t, QF1, MU1), 'timeout': W.TIMEOUT[t]}},
           'dry_build': {k: {'deck_sha256': 'd' * 64, 'model_sha256': 'm' * 64}},
           'reference': {str(t): {'run_id': 'run_0120', 'label': 'c10_s4a_04_2p0_2p0', 'digest': 'r' * 64, 'dir': 'x'}},
           'profiled': {'Qf_cm2': 1.6116859e12, 'per_film': {str(t): {'mun_scale': MU1 / MU0}}},
           'native_launch_values': {'per_film': {str(t): {'mu_band_cm2Vs': 7.813494}}}}
    return pss.seal(rec)


def native(t=2.0, **kw):
    r = {'run_id': 'run_0157', 'label': W.label('S4c', t), 't': t, 'qf': QF1, 'mu_band': MU1, 'overrides': base_ov(t, QF1, MU1),
         'eligibility': {'eligible': True, 'problems': []}, 'digest': 'n' * 64, 'dir': ''}
    r.update(kw); return r


def reference(t=2.0, **kw):
    r = {'run_id': 'run_0120', 'label': 'c10_s4a_04_2p0_2p0', 't': t, 'qf': QF0, 'mu_band': MU0, 'overrides': base_ov(t),
         'eligibility': {'eligible': True, 'problems': []}, 'digest': 'r' * 64, 'dir': ''}
    r.update(kw); return r


FILES_OK = lambda d: {'deck_sha256': 'd' * 64, 'model_sha256': 'm' * 64, 'terminal_currents_sha256': 't' * 64}


def chk(verdict='PASS: profiling exact within 0.01 dec on every J-window point', **kw):
    def f(n, r):
        c = {'verdict': verdict, 'dQf_cm2': n['qf'] - r['qf'], 'mun_scale': n['mu_band'] / r['mu_band'], 'other_material_differences': [],
             'solver_geometry_override_differences': [], 'exactness_breakers': [], 'J_window_sub': {'max_abs_dev_dec': 0.001},
             'J_window_on': {'max_abs_dev_dec': 0.002}}
        c.update(kw); return c
    return f


def boom(n, r): raise AssertionError('the check must not run')


def main():
    try:
        TMP.mkdir(exist_ok=True)
        # (e) pins, frozen file unchanged, route still disabled in the frozen file, (f) tolerances
        expect('pins of frozen code, helpers and settings OK', W.pin_problems(), [])
        ps, pss, ce = W.frozen_modules()
        expect('frozen profile_s4s5.py sha256 == 429b3a3f (unchanged)', W.fsha(HERE / 'profile_s4s5.py') == W.FROZEN['profile_s4s5.py'] == pss.CODE_SHA, True)
        expect('frozen S4C_ROUTE_AVAILABLE stays False', pss.S4C_ROUTE_AVAILABLE, False)
        expect('frozen native_confirmation still refuses role S4c', 'disabled' in (refused(pss.native_confirmation, {}, {}, 'S4c') or ''), True)
        expect('(f) TOL_DEC == S4C_TOL_DEC == 0.01', (ps.TOL_DEC, pss.S4C_TOL_DEC, W.S4C_TOL_DEC), (0.01, 0.01, 0.01))
        cp = TMP / 'pins'; cp.mkdir(exist_ok=True); (cp / 'config').mkdir(exist_ok=True); (cp / 'scripts').mkdir(exist_ok=True)
        for f in list(W.FROZEN) + list(W.HELPERS): shutil.copy(HERE / f, cp / f)
        for f in W.SETTINGS: shutil.copy(W.PKG / f, cp / f)
        expect('pins on an identical copy -> none differ', W.pin_problems(cp, cp), [])
        (cp / 'profile_s4s5.py').write_text((HERE / 'profile_s4s5.py').read_text() + '\n# edited\n')
        expect('(e) edited profile_s4s5.py -> refused', [b[:15] for b in W.pin_problems(cp, cp)], ['profile_s4s5.py'])
        (cp / 'config' / 'solver.yaml').write_text('max_launches: 999\n')
        expect('(b) edited solver.yaml -> reported', any('solver.yaml' in b for b in W.pin_problems(cp, cp)), True)

        # (c) sealed record and the externally committed hash
        rec = record(pss)
        expect('committed record accepted', W.committed_record(rec, rec['sha256'])['sha256'] == rec['sha256'], True)
        expect('(c) wrong --committed -> refused', 'externally committed' in (refused(W.committed_record, rec, '0' * 64) or ''), True)
        expect('(c) no --committed -> refused', 'externally committed' in (refused(W.committed_record, rec, None) or ''), True)
        bad = dict(rec); bad['candidate'] = 'S4A-08'
        expect('(c) record edited after sealing -> refused', 'edited after sealing' in (refused(W.committed_record, bad, rec['sha256']) or ''), True)
        other = pss.seal({**{k: v for k, v in rec.items() if k != 'sha256'}, 'code_sha256': '0' * 64})
        expect('(e) record of other profile_s4s5 code -> refused', 'other profile_s4s5' in (refused(W.committed_record, other, other['sha256']) or ''), True)
        otherw = pss.seal({**{k: v for k, v in rec.items() if k != 'sha256'}, 'wrapper_sha256': '0' * 64})
        expect('record of another wrapper version -> refused', 'another version' in (refused(W.committed_record, otherw, otherw['sha256']) or ''), True)

        # entries: only the two written variables replaced
        nuis = {'per_film': {'2.0': {'overrides': [f'{W.QF_KEY}=1.61169e+12', f'{W.MU_KEY(2.0)}=7.81349']}}}
        ov = W.s4c_overrides(base_ov(2.0), 2.0, nuis)
        expect('s4c_overrides: differs from the base only in Q_f and mu_band_fitted[2.0]', W.override_difference(ov, base_ov(2.0)), sorted([W.QF_KEY, W.MU_KEY(2.0)]))
        expect('s4c_overrides: order kept', [o.split('=')[0] for o in ov] == [o.split('=')[0] for o in base_ov(2.0)], True)
        expect('s4c_overrides: base without mu_band -> refused', refused(W.s4c_overrides, [o for o in base_ov(2.0) if 'mu_band' not in o], 2.0, nuis) is not None, True)
        expect('s4c_overrides: base with Q_f twice -> refused', refused(W.s4c_overrides, base_ov(2.0) + [f'{W.QF_KEY}=1e12'], 2.0, nuis) is not None, True)
        nx = {'per_film': {'2.0': {'overrides': nuis['per_film']['2.0']['overrides'] + ['thickness_laws.WTA_eV.value=0.05']}}}
        expect('s4c_overrides: a third written variable -> refused', refused(W.s4c_overrides, base_ov(2.0), 2.0, nx) is not None, True)
        import campaign_tools as ct
        mx = ct.matrix(); P = {'per_film': {}}
        for t, (q, m) in {2.0: (QF1, MU1), 6.3: (QF1, 31.0), 13.2: (QF1, 53.0)}.items():
            P['per_film'][str(t)] = {'overrides': [f'{W.QF_KEY}={q:.6g}', f'{W.MU_KEY(t)}={m:.6g}']}
        E = W.make_entries(mx['runs'], 'S4A-04', P, 'analysis_2026-10-10_campaign/profile/s4c_record_A52.json')
        a04 = {r['id']: r['campaign_entry'] for r in mx['runs'] if r['id'].startswith('S4A-04-')}
        expect('make_entries: ids', sorted(E), sorted(['S4C-2p0', 'S4C-6p3', 'S4C-13p2', 'S4D-2p0', 'S4D-6p3', 'S4D-13p2']))
        expect('make_entries: labels / timeouts', [(E[k]['label'], E[k]['timeout']) for k in ('S4C-2p0', 'S4C-13p2', 'S4D-6p3')],
               [('c10_s4c_2p0_2p0', 1600), ('c10_s4c_13p2_13p2', 3100), ('c10_s4d_6p3_6p3', 2000)])
        expect('make_entries: S4C-t differs from S4A-04-t only in the written variables',
               all(W.override_difference(E[f'S4C-{g}']['overrides'], a04[f'S4A-04-{g}']['overrides']) == sorted([W.QF_KEY, W.MU_KEY(t)])
                   for t, g in W.TAG.items()), True)
        expect('make_entries: S4D-t = S4C-t + the four IGZO overrides (S3-11/12/13 strings)',
               all(E[f'S4D-{g}']['overrides'] == E[f'S4C-{g}']['overrides'] + W.IGZO_OVERRIDES for g in W.TAG.values()), True)
        s312 = next(r['campaign_entry']['overrides'] for r in mx['runs'] if r['id'] == 'S3-12')
        expect('IGZO overrides == the S3-12 mobility overrides', [o for o in s312 if 'mobility.' in o], W.IGZO_OVERRIDES)
        expect('S4C purpose corrected to 0.01 dec', '0.01 dec' in E['S4C-2p0']['purpose'] and '0.005' not in E['S4C-2p0']['purpose'], True)

        # (a), (b), (d), (f) one film
        cf = lambda n=None, r=None, c=None, f=FILES_OK: W.confirm_film(n or native(), r or reference(), rec, 2.0, c or chk(), f)
        expect('all bound, check PASS -> PASS', cf()['verdict'], 'PASS')
        expect('check FAIL -> FAIL', cf(c=chk('FAIL: profiling approximate'))['verdict'], 'FAIL')
        expect('check UNVERIFIED -> UNKNOWN', cf(c=chk('UNVERIFIED (not every J-window point is covered in either direction)'))['verdict'].startswith('UNKNOWN'), True)
        expect('(a) native ineligible -> UNKNOWN, check not run',
               cf(n=native(eligibility={'eligible': False, 'problems': ['timed out']}), c=boom)['verdict'].startswith('UNKNOWN (endpoint not eligible'), True)
        expect('(a) reference ineligible -> UNKNOWN, check not run',
               cf(r=reference(eligibility={'eligible': False, 'problems': ['x']}), c=boom)['verdict'].startswith('UNKNOWN (endpoint not eligible'), True)
        expect('(a) native without eligibility record -> UNKNOWN', cf(n={**native(), 'eligibility': None}, c=boom)['verdict'].startswith('UNKNOWN'), True)
        expect('native of another label -> REFUSED', cf(n=native(label='c10_s4a_04_2p0_2p0'), c=boom)['verdict'].startswith('REFUSED'), True)
        expect('native of another film -> REFUSED', cf(n=native(t=6.3), c=boom)['verdict'].startswith('REFUSED'), True)
        expect('(c) reference digest differs from the sealed one -> REFUSED', cf(r=reference(digest='z' * 64), c=boom)['verdict'].startswith('REFUSED'), True)
        expect('(c) another reference run -> REFUSED', cf(r=reference(run_id='run_0121'), c=boom)['verdict'].startswith('REFUSED'), True)
        expect('(b) native deck differs from the pinned dry build -> REFUSED',
               cf(f=lambda d: {**FILES_OK(d), 'deck_sha256': 'e' * 64}, c=boom)['verdict'].startswith('REFUSED'), True)
        expect('(b) native material differs -> REFUSED', cf(f=lambda d: {**FILES_OK(d), 'model_sha256': 'e' * 64}, c=boom)['verdict'].startswith('REFUSED'), True)
        w = base_ov(2.0, QF1, MU1); w[1] = 'thickness_laws.WTA_eV.value=0.05'
        o = cf(n=native(overrides=w), c=boom)
        expect('(b) a non-written override differs from the reference -> REFUSED', (o['verdict'].startswith('REFUSED'), o['settings']['only_written_variables']), (True, False))
        expect('(b) override difference = only the written variables in the PASS case', cf()['settings']['override_keys_differing_from_reference'],
               sorted([W.QF_KEY, W.MU_KEY(2.0)]))
        expect('(d) written Q_f differs from the profiled value -> REFUSED', cf(n=native(qf=1.62e12), c=boom)['verdict'].startswith('REFUSED'), True)
        expect('(d) written mu_band differs -> REFUSED', cf(n=native(mu_band=7.9), c=boom)['verdict'].startswith('REFUSED'), True)
        expect('(d) 6-significant-figure rounding accepted (rel 1e-5)', cf()['variable_reference']['written_equal_profiled_rel_1e-5'], True)
        expect('(f) exactness breaker reported by the frozen check -> UNKNOWN', cf(c=chk(exactness_breakers=['gate_tunnelling']))['verdict'].startswith('UNKNOWN'), True)
        expect('(f) other material difference -> UNKNOWN', cf(c=chk('NOT A PURE Q_f/MUN PAIR', other_material_differences=['x']))['verdict'].startswith('UNKNOWN'), True)
        expect('(f) check used another dQf -> UNKNOWN', cf(c=chk(dQf_cm2=1e12))['verdict'].startswith('UNKNOWN'), True)
        expect('record digests carried: native deck + terminal_currents sha256', (cf()['native']['deck_sha256'], cf()['native']['terminal_currents_sha256']),
               ('d' * 64, 't' * 64))

        # overall verdict
        mk = lambda *v: [{'film_nm': t, 'verdict': x} for t, x in zip(W.FILMS, v)]
        expect('overall: 3 PASS -> PASS', W.overall(mk('PASS', 'PASS', 'PASS')).startswith('PASS'), True)
        expect('overall: a FAIL -> FAIL (native reported, profiling audited)', W.overall(mk('PASS', 'FAIL', 'UNKNOWN (x)')).startswith('FAIL'), True)
        expect('overall: an UNKNOWN, no FAIL -> UNKNOWN, never PASS', W.overall(mk('PASS', 'UNKNOWN (x)', 'PASS')).startswith('UNKNOWN'), True)
        expect('overall: a REFUSED film -> UNKNOWN', W.overall(mk('PASS', 'PASS', 'REFUSED: y')).startswith('UNKNOWN'), True)

        # route plan binding
        rec3 = {'entries': {W.entry_id(s, t): {'id': W.entry_id(s, t), 'thickness': t, 'label': W.label(s, t), 'overrides': ['a=1'], 'timeout': W.TIMEOUT[t]}
                            for s in ('S4c', 'S4d') for t in W.FILMS}}
        (TMP / 'config').mkdir(exist_ok=True)
        good = {'runnable': True, 'runs': [dict(rec3['entries'][W.entry_id('S4c', t)], purpose='p') for t in W.FILMS]}
        (TMP / W.PLANS['S4c']).write_text(json.dumps(good))
        expect('plan == record entries -> no problem', W.plan_problems('S4c', rec3, TMP)[0], [])
        g2 = json.loads(json.dumps(good)); g2['runs'][1]['overrides'] = ['a=2']; (TMP / W.PLANS['S4c']).write_text(json.dumps(g2))
        expect('plan override differs -> problem', len(W.plan_problems('S4c', rec3, TMP)[0]), 1)
        g3 = dict(good, state_only={'sealed_dir': 'results/sealed/campaigns'}); (TMP / W.PLANS['S4c']).write_text(json.dumps(g3))
        expect('plan with state_only (not registered) -> problem', len(W.plan_problems('S4c', rec3, TMP)[0]), 1)
        expect('missing S4d plan -> problem', W.plan_problems('S4d', rec3, TMP)[0], [f'{W.PLANS["S4d"]} missing'])

        # S4d verdicts
        A = lambda p, v='ARITHMETIC PASS': {'arithmetic_pass': p, 'verdict': v}
        expect('s4d: arithmetic pass -> DOES NOT SURVIVE', W.s4d_verdict(True, True, True, A(True)).startswith('DOES NOT SURVIVE'), True)
        expect('s4d: arithmetic fail -> SURVIVES', W.s4d_verdict(True, True, True, A(False, 'ARITHMETIC FAIL')).startswith('SURVIVES'), True)
        expect('s4d: UNVERIFIED profile -> UNRESOLVED', W.s4d_verdict(True, True, True, A(False, 'UNVERIFIED: ARITHMETIC PASS')).startswith('UNRESOLVED'), True)
        expect('s4d: ineligible -> UNKNOWN', W.s4d_verdict(False, True, True, A(True)).startswith('UNKNOWN'), True)
        expect('s4d: IGZO not active -> UNKNOWN', W.s4d_verdict(True, False, True, A(True)).startswith('UNKNOWN'), True)
        expect('s4d: settings differ -> REFUSED', W.s4d_verdict(True, True, False, A(True)).startswith('REFUSED'), True)
        expect('s4d: adoption refused -> UNKNOWN', W.s4d_verdict(True, True, True, None).startswith('UNKNOWN'), True)

        # best candidate from a synthetic surrogate output
        rows = [{'id': f'S4A-{k:02d}', 'stage': 'S4a', 'sqrtJ': 0.6 + 0.01 * ((k * 7) % 15), 'state': 'valid'} for k in range(1, 16)]
        b = min(rows, key=lambda r: r['sqrtJ'])
        sur = {'code_sha256': W.FROZEN['profile_s4s5.py'], 'verdict': 'ABORT S4b: run S4c on the best candidate, ...', 'archive': rows,
               's4a_abort': {'n_valid': 15, 'n_missing': 0, 'n_invalid': 0, 'best_sqrtJ_dec': b['sqrtJ']}}
        expect('best_of_surrogate: lowest valid sqrt(J)', W.best_of_surrogate(sur)['id'], b['id'])
        expect('best_of_surrogate: not an abort verdict -> refused', refused(W.best_of_surrogate, dict(sur, verdict='PROPOSAL')) is not None, True)
        expect('best_of_surrogate: incomplete inventory -> refused',
               refused(W.best_of_surrogate, dict(sur, s4a_abort=dict(sur['s4a_abort'], n_valid=14, n_missing=1))) is not None, True)
        expect('best_of_surrogate: other code -> refused', refused(W.best_of_surrogate, dict(sur, code_sha256='0' * 64)) is not None, True)
        expect('CLI: no arguments -> 2', W.main([]), 2)
        expect('CLI: confirm with two runs -> 2', W.main(['confirm', 'a', 'b', '--committed', 'x']), 2)
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print(f'{sum(results)}/{len(results)} passed'); return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main())
