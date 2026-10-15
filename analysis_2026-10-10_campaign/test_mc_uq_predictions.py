"""Tests of mc_uq_predictions.py (register A55; NO launch; no run directory, P output, sealed run or measured curve opened; only synthetic
curves, synthetic profiles, injected objective functions and temporary JSON files in ./test_tmp_mcuq, removed at the end).

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"; python -I -B analysis_2026-10-10_campaign/test_mc_uq_predictions.py
"""
import hashlib, json, math, shutil, sys
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))
import mc_uq_predictions as M  # noqa: E402

TMP = HERE / 'test_tmp_mcuq'
results = []
COX, QA, MREF = M.ce.ex.COX, M.P4.QF_ANCHOR, 0.208
VG = np.round(np.arange(-3.0, 3.0 + 1e-9, 0.05), 10)


def expect(name, got, want):
    ok = got == want; results.append(ok); print(f"{'ok  ' if ok else 'FAIL'} {name}: {got}", flush=True)


def refused(f, *a, **k):
    try: f(*a, **k); return None
    except SystemExit as e: return str(e)


def g(u): return 1e-15 + 2e-8 * np.logaddexp(0.0, u / 0.1)


def vt(qf, t): return 0.2 + 0.01 * t - M.ps.Q * (qf - QA) / COX


def run(t, qf, mu_inf, ell, mstar=0.25, rid='syn', dvt=0.0, vg=VG):
    mb = M.ps.mu_law(mu_inf, ell, t, mstar)
    return {'run_id': rid, 't': t, 'qf': qf, 'mu_band': mb, 'mstar': mstar, 'cox': COX, 'vg': vg.copy(),
            'i': (mb / 50.0) * g(vg - vt(qf, t) - dvt), 'eligibility': {'eligible': True}, 'breakers': [], 'digest': rid}


def info_at(qf, mu_inf, ell, mstar=0.25):
    out = {}
    for t in (2.0, 6.3, 13.2):
        r = run(t, qf, mu_inf, ell, mstar); i = r['i']
        out[t] = {'vg': VG.copy(), 'i': i, 'floor': 1e-14, 'a1_window': (2e-11, 2e-10)}
    return out


def prof(v, mu, ell, s=0.0):
    return {'valid': True, 'profiled': {'dV0_from_anchor_V': v, 'mu_inf_cm2Vs': mu, 'ell_nm': ell, 'sqrtJ_dec': s}}


def quadJ(v0, lmu0, ell0, w):
    def J(R, info, dQf, mu, ell):
        v = -M.ps.Q * (R[0]['qf'] + dQf - QA) / R[0]['cox']
        s = ((v - v0) / w[0]) ** 2 + ((math.log(mu) - lmu0) / w[1]) ** 2 + ((ell - ell0) / w[2]) ** 2
        return s ** 2, {2.0: {'sub': {'coverage': 1.0}, 'on': {'coverage': 1.0}}}
    return J


def main():
    TMP.mkdir(exist_ok=True)
    try:
        # pins and guards
        expect('pins: real frozen files match', M.check_pins() is None, True)
        expect('pins: changed dependency -> refused', refused(M.check_pins, {'analysis_2026-10-10_campaign/profile_s4s5.py': '0' * 64}) is not None, True)
        expect('guard: run id in sealed list -> refused', refused(M.guard, 'results/runs/run_0075_2p0_x', {'run_0075'}) is not None, True)
        expect('guard: results/sealed path -> refused', refused(M.guard, 'results/sealed/run_0001_x', set()) is not None, True)
        expect('guard: ordinary run passes', M.guard('results/runs/run_0120_2p0_x', {'run_0075'}), None)
        f = TMP / 'src.json'; f.write_text(json.dumps({'a': [{'e': -0.0123}]})); sh = hashlib.sha256(f.read_bytes()).hexdigest()
        expect('verified_source: wrong sha256 -> refused', refused(M.verified_source, {'path': str(f), 'sha256': '0' * 64}) is not None, True)
        expect('verified_source + json_at: value', M.json_at(M.verified_source({'path': str(f), 'sha256': sh}), ['a', 0, 'e']), -0.0123)

        # exact relations
        q1 = QA + 0.1 * COX / M.ps.Q          # +q dQ / C_ox = 0.1 V (two grid steps)
        r0, r1 = run(6.3, QA, 100.0, 10.0), run(6.3, q1, 100.0, 10.0)
        vg, i = M.transfer_T(r0, q1, 100.0, 10.0)
        v_a, v_b = M.q_transfer(vg, i, 'vth_cc_V'), M.q_transfer(r1['vg'], r1['i'], 'vth_cc_V')
        expect('transfer_T: Q_f shift reproduces the native V_th,cc (1e-9 V)', abs(v_a - v_b) < 1e-9, True)
        expect('transfer_T: V_th shift = -q dQ / C_ox', abs((v_a - M.q_transfer(r0['vg'], r0['i'], 'vth_cc_V')) + 0.1) < 1e-9, True)
        vg2, i2 = M.transfer_T(r0, QA, 150.0, 10.0)
        expect('transfer_T: MUN scale = mu_law ratio (log10 I_D(3 V))',
               abs(M.q_transfer(vg2, i2, 'log10_id_3V') - M.q_transfer(r0['vg'], r0['i'], 'log10_id_3V') - math.log10(1.5)) < 1e-12, True)
        expect('transfer_T: SS in the fixed window invariant under the Q_f shift (1e-6 mV/dec)',
               abs(M.q_transfer(vg, i, 'ss_fixed_mV_dec') - M.q_transfer(r1['vg'], r1['i'], 'ss_fixed_mV_dec')) < 1e-6, True)
        expect('q_transfer: mu_FE outside the curve -> None', M.q_transfer(vg[:50], i[:50], 'mu_fe_2.0'), None)
        expect('q_transfer: ss_a1 without window -> refused', refused(M.q_transfer, vg, i, 'ss_a1_mV_dec') is not None, True)
        expect('q_transfer: unknown quantity -> refused', refused(M.q_transfer, vg, i, 'vth_elr') is not None, True)
        expect('qf_of inverts dV0_from_anchor', abs(-M.ps.Q * (M.qf_of(0.123, COX) - QA) / COX - 0.123) < 1e-12, True)

        # output families (log-linear in V_G: the interpolated shift is exact)
        vd = np.array([0.05, 0.1, 0.4, 0.7])
        fam = {vg_: (vd, 10 ** (-12 + 1.5 * vg_ + 0.3 * vd), -10 ** (-12 + 1.5 * vg_ + 0.3 * vd)) for vg_ in (-2.0, -1.0, -0.5)}
        P1 = {'run_id': 'p1', 't': 6.3, 'qf': QA, 'mu_band': M.ps.mu_law(100.0, 10.0, 6.3, 0.25), 'mstar': 0.25, 'cox': COX, 'family': fam, 'breakers': []}
        qs = QA + 0.07 * COX / M.ps.Q
        expect('out_log: shifted V_G interpolated exactly on a log-linear family',
               abs(M.out_log(P1, qs, 100.0, 10.0, -1.0, 0.7, 'id') - (-12 + 1.5 * (-0.93) + 0.21)) < 1e-12, True)
        expect('out_log: shift outside the native V_G range -> None', M.out_log(P1, qs, 100.0, 10.0, -0.5, 0.7, 'id'), None)
        expect('out_log: I_S magnitude', abs(M.out_log(P1, QA, 100.0, 10.0, -2.0, 0.1, 'is') - (-12 - 3 + 0.03)) < 1e-12, True)
        expect('out_log: I_G -> refused (ranked only)', refused(M.out_log, P1, QA, 100.0, 10.0, -1.0, 0.7, 'ig') is not None, True)
        expect('out_log: non-native V_D -> refused', refused(M.out_log, P1, QA, 100.0, 10.0, -1.0, 0.3, 'id') is not None, True)
        a = M.out_log(P1, QA, 300.0, 0.0, -1.0, 0.7, 'id') - M.out_log(P1, QA, 300.0, 0.0, -1.0, 0.1, 'id')
        expect('out_log: MUN scale cancels in a V_D ratio', abs(a - 0.3 * 0.6) < 1e-12, True)

        # confidence set (injected quadratic objective)
        R = [{'qf': QA, 'cox': COX, 't': 2.0}]
        A, st = M.near_optimal(R, {}, prof(0.0, 100.0, 20.0), 0.04, 1, quadJ(0.0, math.log(100.0), 20.0, (1.0, 0.3, 5.0)), m=256)
        sj = [math.sqrt(quadJ(0.0, math.log(100.0), 20.0, (1.0, 0.3, 5.0))(R, {}, M.qf_of(x[0], COX) - QA, math.exp(x[1]), x[2])[0]) for x in A]
        expect('near_optimal: every accepted point within the threshold', max(sj) <= 0.04 + 1e-12, True)
        expect('near_optimal: profiled optimum always accepted', bool(np.allclose(A[0], [0.0, math.log(100.0), 20.0])), True)
        expect('near_optimal: box grown in dV0 beyond HALF0', st['rounds'][-1]['half'][0] > M.HALF0[0], True)
        expect('near_optimal: closed set (no open dimension)', st['open'], [])
        A2, st2 = M.near_optimal(R, {}, prof(0.0, 100.0, 49.9), 0.04, 1, quadJ(0.0, math.log(100.0), 49.9, (0.2, 0.3, 5.0)), m=256)
        expect('near_optimal: ell at the profile bound flagged upper', ['ell_nm', 'upper'] in st2['at_profile_bound'], True)
        A3, st3 = M.near_optimal(R, {}, prof(0.0, 100.0, 20.0), 0.04, 1, quadJ(0.0, math.log(100.0), 20.0, (0.004, 0.006, 0.1)), m=256)
        expect('near_optimal: tiny set -> box halved', st3['rounds'][1]['half'][0] < M.HALF0[0], True)
        old = M.MAX_ROUNDS; M.MAX_ROUNDS = 2
        try:
            _, st4 = M.near_optimal(R, {}, prof(0.0, 100.0, 25.0), 0.04, 1, quadJ(0.0, math.log(100.0), 25.0, (0.2, 0.3, 200.0)), m=128)
        finally: M.MAX_ROUNDS = old
        expect('near_optimal: interior edge still reached after the last round -> OPEN', 'ell_nm' in st4['open'], True)
        X1, _ = M.near_optimal(R, {}, prof(0.0, 100.0, 20.0), 0.04, 7, quadJ(0.0, math.log(100.0), 20.0, (0.2, 0.3, 5.0)), m=128)
        X2, _ = M.near_optimal(R, {}, prof(0.0, 100.0, 20.0), 0.04, 7, quadJ(0.0, math.log(100.0), 20.0, (0.2, 0.3, 5.0)), m=128)
        expect('near_optimal: deterministic for a fixed seed', bool(np.array_equal(X1, X2)), True)

        # real frozen triple_J on synthetic curves: the truth is in the set, J(truth) = 0
        tru = (QA - 0.05 * COX / M.ps.Q, 120.0, 8.0); infoS = info_at(*tru)   # grid-aligned shift (one 0.05 V step)
        RS = [run(t, QA, 100.0, 7.248) for t in (2.0, 6.3, 13.2)]
        vtru = -M.ps.Q * (tru[0] - QA) / COX
        s0, cov = M.sqrtJ_at(RS, infoS, (vtru, math.log(tru[1]), tru[2]))
        expect('sqrtJ_at (frozen triple_J): J = 0 at the synthetic truth', (s0 < 1e-9, cov), (True, True))
        AS, stS = M.near_optimal(RS, infoS, prof(vtru, tru[1], tru[2]), 0.01, 3, m=128)
        expect('near_optimal (frozen triple_J): accepted set non-empty and contains the truth', bool(len(AS) >= 1 and np.allclose(AS[0], [vtru, math.log(120.0), 8.0])), True)

        # draws, bands, floors, reading
        pools = {'a': np.zeros((10, 3)), 'b': np.ones((1000, 3))}
        d = M.draw(pools, 2000, 5); na = sum(1 for c, _ in d if c == 'a')
        expect('draw: equal weight per candidate (|n_a - 1000| < 100)', abs(na - 1000) < 100, True)
        expect('draw: deterministic for a fixed seed', [c for c, _ in M.draw(pools, 50, 5)] == [c for c, _ in M.draw(pools, 50, 5)], True)
        u = list(np.linspace(0, 1, 101))
        b = M.band(u, {'ell_nm': u}, [('ell_nm', 'upper')])
        expect('band: quantiles', (round(b['q05'], 6), round(b['median'], 6), round(b['q95'], 6)), (0.05, 0.5, 0.95))
        expect('band: rho > 0 with ell at the upper bound -> q95 open', b['one_sided'][0]['edge'], 'q95 open (upper edge one-sided)')
        expect('band: rho < 0 -> q05 open', M.band(u, {'ell_nm': u[::-1]}, [('ell_nm', 'upper')])['one_sided'][0]['edge'], 'q05 open (lower edge one-sided)')
        expect('band: constant parameter -> side undetermined', M.band(u, {'ell_nm': [50.0] * 101}, [('ell_nm', 'upper')])['one_sided'][0]['edge'], 'side undetermined')
        expect('band: None values dropped and counted', M.band([None, 1.0, 2.0], {}, [])['n_dropped'], 1)
        expect('floored: abs floor widens', M.floored({'q05': 0.4, 'median': 0.5, 'q95': 0.6}, 0.3, 'abs'), [0.2, 0.8])
        expect('floored: narrower floor keeps the MC band', M.floored({'q05': 0.4, 'median': 0.5, 'q95': 0.6}, 0.01, 'abs'), [0.4, 0.6])
        expect('floored: pct floor', [round(z, 9) for z in M.floored({'q05': 9.0, 'median': 10.0, 'q95': 11.0}, 20.0, 'pct')], [8.0, 12.0])
        expect('reading: 3/3 PASS', M.reading_label({'H6p3': 'PASS', 'H2p0': 'PASS', 'H13p2': 'PASS'}).startswith('calibration-conditional with'), True)
        expect('reading: 2 FAIL -> FALSIFIED', M.reading_label({'H6p3': 'FAIL', 'H2p0': 'FAIL', 'H13p2': 'PASS'}).startswith('TRANSFERABILITY FALSIFIED'), True)
        expect('reading: 1 FAIL', M.reading_label({'H6p3': 'PASS', 'H2p0': 'FAIL', 'H13p2': 'PASS'}).startswith('TRANSFERABILITY FAILED in fold H2p0'), True)
        expect('reading: UNRESOLVED fold -> UNKNOWN', M.reading_label({'H6p3': 'PASS', 'H2p0': 'UNRESOLVED', 'H13p2': 'PASS'}).startswith('TRANSFERABILITY UNKNOWN'), True)

        # U2 transfer: candidate c differs from b by +0.02 V in V_T at the reference film
        Pb = run(6.3, QA, 100.0, 10.0, rid='P')
        ref = {'b': run(6.3, QA, 100.0, 10.0, rid='Ab'), 'c': run(6.3, QA, 100.0, 10.0, rid='Ac', dvt=0.05)}
        prod = {'id': 'P3-x', 'product': 'P3', 'kind': 'transfer', 'quantities': ['vth_cc_V', 'mu_fe_2.0'], 'u2_reference_film': 6.3}
        dr = [('b', np.array([0.0, math.log(100.0), 10.0])), ('c', np.array([0.0, math.log(100.0), 10.0]))]
        infoA = info_at(QA, 100.0, 10.0)
        vals, _ = M.eval_product(prod, Pb, dr, COX, 'b', ref, infoA, 'U1+U2')
        expect('U2: Delta = 0 for the base candidate', abs(vals['vth_cc_V'][0] - M.q_transfer(Pb['vg'], Pb['i'], 'vth_cc_V')) < 1e-12, True)
        expect('U2: additive N_s / W_T transfer (+0.05 V, grid-aligned)', abs(vals['vth_cc_V'][1] - vals['vth_cc_V'][0] - 0.05) < 1e-9, True)
        vals1, _ = M.eval_product(prod, Pb, dr, COX, 'b', ref, infoA, 'U1')
        expect('U1: no transfer term', abs(vals1['vth_cc_V'][1] - vals1['vth_cc_V'][0]) < 1e-12, True)
        expect('U1+U2 for an output product -> UNRESOLVED (None)', M.eval_product({'kind': 'output'}, P1, dr, COX, 'b', ref, infoA, 'U1+U2')[0], None)

        # one branch end to end on synthetic curves with the frozen triple_J
        cands = [{'id': 'b', 'k': 0, 'R': [run(t, QA, 100.0, 7.248, rid=f'b{t}') for t in (2.0, 6.3, 13.2)], 'prof': prof(vtru, tru[1], tru[2], 0.0)},
                 {'id': 'c', 'k': 1, 'R': [run(t, QA, 100.0, 7.248, rid=f'c{t}', dvt=0.003) for t in (2.0, 6.3, 13.2)], 'prof': None},
                 {'id': 'z', 'k': 2, 'R': [], 'prof': {'valid': False, 'profiled': {}}}]
        Pt = run(6.3, QA, 100.0, 7.248, rid='Pt')
        prods = [(dict(prod, quantities=['vth_cc_V', 'ss_fixed_mV_dec', 'log10_id_3V', 'mu_fe_2.0']), Pt),
                 ({'id': 'P1-x', 'product': 'P1', 'kind': 'output', 'points': [{'vg': -1.0, 'vd': 0.7, 'current': 'id'}],
                   'ratios': [{'vg': -1.0, 'vd_num': 0.7, 'vd_den': 0.1, 'current': 'id'}]}, P1)]
        fl = [{'product_id': 'P3-x', 'quantity': 'vth_cc_V', 'floor': 0.05, 'kind': 'abs'}]
        res = M.run_branch('syn', cands, 'b', prods, infoS, fl, m=64, n=200)
        expect('run_branch: both deltas reported', sorted(res['sets']), ['0.01', '0.03'])
        expect('run_branch: candidates without a valid profile never qualify', res['sets']['0.03']['qualifying'], ['b'])
        bt = res['products']['P3-x']['bands']['0.01']
        expect('run_branch: U1 and U1+U2 both reported', sorted(bt), ['U1', 'U1+U2'])
        expect('run_branch: U1 band finite for every draw', bt['U1']['vth_cc_V']['n_finite'], 200)
        expect('run_branch: LOO-2 floor applied', bt['U1']['vth_cc_V']['loo2_floor']['F'], 0.05)
        expect('run_branch: output product U2 UNRESOLVED', res['products']['P1-x']['bands']['0.03']['U1+U2'].startswith('UNRESOLVED'), True)
        expect('run_branch: base without a valid profile -> refused', refused(M.run_branch, 'syn', cands, 'z', prods, infoS, m=8, n=4) is not None, True)

        # manifest refusals before any run is opened
        man = TMP / 'man.json'
        man.write_text(json.dumps({'branches': [{'name': 'x', 'products': [{'id': 'q', 'product': 'P5', 'kind': 'transfer', 'run': 'results/runs/run_9999_x'}]}]}))
        expect('bands: product outside P1..P4 -> refused', refused(M.bands, man, TMP / 'o.json') is not None, True)
        man.write_text(json.dumps({'branches': [{'name': 'x', 'products': [{'id': 'q', 'product': 'P1', 'kind': 'strip', 'run': 'results/runs/run_9999_x'}]}]}))
        expect('bands: unregistered kind -> refused', refused(M.bands, man, TMP / 'o.json') is not None, True)
        man.write_text(json.dumps({'branches': [{'name': 'x', 'products': [{'id': 'q', 'product': 'P1', 'kind': 'output', 'run': 'results/sealed/run_9999_x'}]}]}))
        expect('bands: sealed P path -> refused before opening', refused(M.bands, man, TMP / 'o.json') is not None, True)
        expect('CLI: no arguments -> 2', M.main([]), 2)
        expect('constants: N, M, seed, deltas', (M.N_DRAWS, M.M_PROP, M.SEED, M.DELTAS), (4000, 4096, 20261016, (0.01, 0.03)))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print(f'{sum(results)}/{len(results)} passed'); return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main())
