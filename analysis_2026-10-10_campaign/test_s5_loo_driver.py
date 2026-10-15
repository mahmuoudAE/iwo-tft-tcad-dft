"""Tests of s5_loo_driver.py (register A53; NO launch; no ATLAS output read; no repo file written except the temporary ./test_tmp_s5_driver, removed
at the end).

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"; & <venv python> -I -B analysis_2026-10-10_campaign/test_s5_loo_driver.py
Synthetic inputs only, plus the registered matrix entries (campaign_matrix.json f06e8d77) and the generator (run_campaign.current_deck_text) for the
template / deck checks. The deck integration cases rebuild the S4A-01 start point through the S5 entry path and compare it with the registered
PA-12 deck pins of the A50 gate (run_0061 / run_0068 / run_0069 STARTED rows), i.e. registered inputs, not outputs.
"""
import contextlib, importlib.util, io, json, math, os, shutil, sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent; PKG = HERE.parent; TMP = HERE / 'test_tmp_s5_driver'
os.environ['IWO_MODEL_FILE'] = 'config/iwo_material_model_v3.yaml'
results = []


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


S = load(HERE / 's5_loo_driver.py', 's5_driver_under_test')
GG = load(HERE / 'prelaunch_gate_c10_g.py', 'gg_constants_for_s5')


def expect(name, got, want):
    ok = got == want; results.append(ok); print(f"{'ok  ' if ok else 'FAIL'} {name}: {got}", flush=True)


def raises(name, f, *a, **k):
    try: f(*a, **k); ok = False; why = 'no refusal'
    except SystemExit as e: ok = True; why = str(e)[:90]
    results.append(ok); print(f"{'ok  ' if ok else 'FAIL'} {name}: refused ({why})" if ok else f'FAIL {name}: {why}', flush=True)


def seal(d):
    d = json.loads(S._canon({k: v for k, v in d.items() if k != 'sha256'})); d['sha256'] = S.tsha(S._canon(d)); return d


class FakeP:
    """the two frozen helpers deck_of needs (DECK rounding as profile_s4s5.DECK)"""
    DECK = {'lNs': lambda v: float(f'{10 ** v:.4g}'), 'WT': lambda v: round(float(v), 4), 'g0': lambda v: None if v is None else round(float(v), 3)}
    @staticmethod
    def deck_inputs(x, dims): return tuple(FakeP.DECK[d](x[d]) for d in dims)


def main():
    try:
        mx = S.matrix_by_id()
        # ---- invocation structure and labels
        inv = S.invocation_order(); ids = [i for h, st in inv for i in S.entry_ids(h, st)]
        expect('15 invocations, 30 entries, all distinct', (len(inv), len(ids), len(set(ids))), (15, 30, 30))
        expect('fold order H6p3, H2p0, H13p2; first invocation t1 of H6p3', ([S.FID[h] for h in S.FOLDS], inv[0]), (['H6p3', 'H2p0', 'H13p2'], (6.3, 't1')))
        expect('every S5 entry id is a matrix S5 entry (stage S5_leave_one_film_out)', all(mx.get(i, {}).get('stage') == 'S5_leave_one_film_out' for i in ids), True)
        expect('the 30 ids == the 30 matrix S5 ids', sorted(ids) == sorted(k for k, r in mx.items() if r['stage'] == 'S5_leave_one_film_out'), True)
        expect('H6p3 t1 entries at the training films 2.0 / 13.2', S.entry_ids(6.3, 't1'), ['S5-H6p3-1-2p0', 'S5-H6p3-1-13p2'])
        expect('H13p2 pred entries', S.entry_ids(13.2, 'pred'), ['S5-H13p2-PRED-best', 'S5-H13p2-PRED-runner_up'])
        expect('matrix labels / timeouts of H6p3 t1 and pred', [(mx[i]['campaign_entry']['label'], mx[i]['campaign_entry']['timeout']) for i in
                                                                S.entry_ids(6.3, 't1') + S.entry_ids(6.3, 'pred')],
               [('c10_s5_h6p3_1_2p0_2p0', 1600), ('c10_s5_h6p3_1_13p2_13p2', 3100), ('c10_s5_h6p3_pred_best_6p3', 2000), ('c10_s5_h6p3_pred_runner_up_6p3', 2000)])
        expect('training films', [S.train_of(h) for h in S.FOLDS], [[2.0, 13.2], [6.3, 13.2], [2.0, 6.3]])
        raises('held 5.0 refused', S.held_of, '5.0')
        expect('held "6.3" -> 6.3', S.held_of('6.3'), 6.3)

        # ---- caller flags on the training films (A53 (b))
        shape = {'branch': {'2.0': {'shape_only_sqrtJ_dec': 0.10}, '6.3': {'shape_only_sqrtJ_dec': 0.50}, '13.2': {'shape_only_sqrtJ_dec': 0.205}},
                 'base': {'2.0': {'shape_only_sqrtJ_dec': 0.10}, '6.3': {'shape_only_sqrtJ_dec': 0.05}, '13.2': {'shape_only_sqrtJ_dec': 0.20}}}
        expect('pure_on: changes <= 0.01 at both training films (held film ignored) -> True', S.pure_on(shape, [2.0, 13.2])[0], True)
        expect('pure_on: 6.3 change 0.45 -> False', S.pure_on(shape, [6.3, 13.2])[0], False)
        expect('pure_on: missing film -> None', S.pure_on({'branch': {}, 'base': {}}, [2.0])[0], None)
        expect('pure_on: tolerance edge 0.01 -> True', S.pure_on({'branch': {'2.0': {'shape_only_sqrtJ_dec': 0.11}}, 'base': {'2.0': {'shape_only_sqrtJ_dec': 0.10}}}, [2.0])[0], True)
        act = {'S0-01': {'status': 'ACTIVE_AS_REQUESTED'}, 'S3-06': {'status': 'ACTIVE_AS_REQUESTED'}, 'S3-12': {'status': 'OPTION_NOT_ACTIVE'},
               'S3-13': {'status': 'ACTIVE_AS_REQUESTED', 'regions_1_2': {'state': 'ACTIVE'}}, 'S3-11': {'status': 'ACTIVE_AS_REQUESTED', 'regions_1_2': {'state': 'NOT ACTIVE'}}}
        expect('activation_on: training roles active -> True', S.activation_on(act, {2.0: 'S0-01', 6.3: 'S3-12', 13.2: 'S3-06'}, [2.0, 13.2]), True)
        expect('activation_on: inactive held-film role ignored, inactive training role -> False',
               (S.activation_on(act, {2.0: 'S0-01', 6.3: 'S3-12', 13.2: 'S3-06'}, [6.3, 13.2])), False)
        expect('activation_on: IGZO regions 1/2 not active -> False', S.activation_on(act, {2.0: 'S3-11', 13.2: 'S3-13'}, [2.0, 13.2]), False)
        expect('activation_on: role missing -> None', S.activation_on(act, {2.0: 'S9-99', 13.2: 'S3-13'}, [2.0, 13.2]), None)

        class A:   # fake A49 module (roles -> run dirs under results/runs)
            BASE = ('S0-01', 'S1-01', 'S1-02')
            BRANCHES = [{'name': 'tail bulk (S3-04=S0-01, S3-05, S3-06)', 'group': 'tail', 'roles': ('S0-01', 'S3-05', 'S3-06')},
                        {'name': 'IGZO.TOKYO GAMMA0 -0.31 (S3-11, S3-12, S3-13)', 'group': 'mobility', 'roles': ('S3-11', 'S3-12', 'S3-13')}]
            @staticmethod
            def run_dir(k): return PKG / 'results' / 'runs' / f'synthetic_{k}'
        ad = {'chosen': {'tail': None, 'mobility': None}, 'branches': [
            {'name': A.BRANCHES[0]['name'], 'activation': {'S0-01': {'status': 'ACTIVE_AS_REQUESTED'}, 'S3-05': {'status': 'ACTIVE_AS_REQUESTED'},
                                                          'S3-06': {'status': 'ACTIVE_AS_REQUESTED'}}, 'shape_only': shape},
            {'name': A.BRANCHES[1]['name'], 'activation': act, 'shape_only': {'branch': shape['base'], 'base': shape['base']}}]}
        el = {'S0-01': True, 'S3-05': True, 'S3-06': True, 'S3-11': True, 'S3-12': False, 'S3-13': True}
        sp = S.branch_spec(6.3, A, ad, el)
        expect('branch_spec H6p3: base / runs list all films (frozen sel() filters), full-data choice []',
               (sorted(sp['base']), sorted(sp['branches'][0]['runs']), sp['full_data_choice']), (['13.2', '2.0', '6.3'], ['13.2', '2.0', '6.3'], []))
        expect('branch_spec H6p3 flags: tail (conv, act, pure) / IGZO (S3-12 ineligible but held out)',
               [(b['converged'], b['activation_ok'], b['pure_shift_or_scale']) for b in sp['branches']], [(True, True, True), (True, False, True)])
        sp2 = S.branch_spec(2.0, A, ad, el)
        expect('branch_spec H2p0: IGZO not converged (S3-12 is a training film); tail pure False (6.3 change)',
               [(b['converged'], b['pure_shift_or_scale']) for b in sp2['branches']], [(True, False), (False, True)])
        ad2 = dict(ad, chosen={'tail': 'tail bulk (S3-04=S0-01, S3-05, S3-06)', 'mobility': None})
        expect('branch_spec: full-data choice from the A49 record', S.branch_spec(6.3, A, ad2, el)['full_data_choice'], ['tail bulk (S3-04=S0-01, S3-05, S3-06)'])

        # ---- override replacement and coordinates
        tpl = ['a=1', f'{S.NT2}=2e+19', 'b=2', f'{S.WTA}=0.04']
        expect('_replace: exactly the given keys', S._replace(tpl, {S.NT2: '3e+19', S.WTA: '0.05'}), ['a=1', f'{S.NT2}=3e+19', 'b=2', f'{S.WTA}=0.05'])
        raises('_replace: key absent from the template refused', S._replace, tpl, {S.QF: '1e12'})
        raises('_replace: key twice in the template refused', S._replace, tpl + [f'{S.NT2}=1'], {S.NT2: '3e+19'})
        expect('tail_values surface: Nt2 = N_s / 2 nm', S.tail_values(tpl, 8.857e12), {S.NT2: '4.4285e+19'})
        expect('tail_values 50:50: Nt2 = nt_bulk = N_s / 2 / 2 nm', S.tail_values(tpl + [f'{S.NTB}=1e+19'], 4e12), {S.NT2: '1e+19', S.NTB: '1e+19'})
        cx = S.coords_of_overrides([f'{S.NT2}=1e+19', f'{S.NTB}=1e+19', f'{S.WTA}=0.0572', f'{S.G0}=-0.274'])
        expect('coords_of_overrides 50:50 + IGZO: N_s = (Nt2 + nt_bulk) x 2 nm', (round(10 ** cx['lNs'] / 1e12, 9), cx['WT'], cx['g0']), (4.0, 0.0572, -0.274))
        expect('deck_of (frozen DECK rounding)', S.deck_of({'lNs': math.log10(8.85712e12), 'WT': 0.057234, 'g0': None}, ('lNs', 'WT'), FakeP),
               {'Ns_cm2': 8.857e12, 'WT_eV': 0.0572, 'gamma0': None})

        # ---- entries from the registered templates; deck integration against the registered PA-12 pins
        nuis = lambda t, qf, mu: [f'{S.QF}={qf}', f'{S.MU(t)}={mu}']
        e = S.launch_entry(mx, 'S5-H6p3-1-2p0', 2.0, 'S4A-01-2p0', {'Ns_cm2': 4e12, 'WT_eV': 0.04, 'gamma0': None}, nuis(2.0, '1.38345e+12', '17.6897'), 'x', 'y')
        expect('launch_entry at the start point: overrides == the S4A-01-2p0 matrix overrides', e['overrides'], mx['S4A-01-2p0']['campaign_entry']['overrides'])
        expect('launch_entry: matrix id / label / timeout / stage', (e['id'], e['label'], e['timeout'], e['stage']),
               ('S5-H6p3-1-2p0', 'c10_s5_h6p3_1_2p0_2p0', 1600, 'S5_leave_one_film_out'))
        pins = S.dry_build({'S5-H6p3-1-2p0': e})
        expect('deck integration: S5 entry at the start point == the registered S4A-01-2p0 / run_0061 deck pin (PA-12)',
               pins['S5-H6p3-1-2p0']['deck_sha256'], GG.REUSE['S4A-01-2p0'][2])
        e13 = S.launch_entry(mx, 'S5-H6p3-1-13p2', 13.2, 'S4A-01-13p2', {'Ns_cm2': 4e12, 'WT_eV': 0.04, 'gamma0': None}, nuis(13.2, '1.38345e+12', '63.2597'), 'x', 'y')
        expect('deck integration: 13.2 nm start point == the run_0069 deck pin', S.dry_build({'k': e13})['k']['deck_sha256'], GG.REUSE['S4A-01-13p2'][2])
        e2 = S.launch_entry(mx, 'S5-H6p3-1-2p0', 2.0, 'S4A-01-2p0', {'Ns_cm2': 8.857e12, 'WT_eV': 0.0572, 'gamma0': None}, nuis(2.0, '1.61169e+12', '7.81346'), 'x', 'y')
        diff = sorted({S._okey(o) for o in set(e2['overrides']) ^ set(mx['S4A-01-2p0']['campaign_entry']['overrides'])})
        expect('launch_entry: only Nt2, W_T, Q_f and mu_band[2.0] differ from the template', diff, sorted([S.NT2, S.WTA, S.QF, S.MU(2.0)]))
        expect('the same values == the registered S4C-2p0 overrides (S4A-04 at the profiled Q_f / mu_band)',
               e2['overrides'], json.loads((PKG / 'config' / 'campaign_C10_S4c.json').read_text())['runs'][0]['overrides'])
        raises('launch_entry: nuisance keys not exactly Q_f and mu_band[t] refused', S.launch_entry, mx, 'S5-H6p3-1-2p0', 2.0, 'S4A-01-2p0',
               {'Ns_cm2': 4e12, 'WT_eV': 0.04, 'gamma0': None}, nuis(13.2, '1e12', '1'), 'x', 'y')
        raises('launch_entry: GAMMA0 on a constant-mobility template refused', S.launch_entry, mx, 'S5-H6p3-1-2p0', 2.0, 'S4A-01-2p0',
               {'Ns_cm2': 4e12, 'WT_eV': 0.04, 'gamma0': -0.3}, nuis(2.0, '1e12', '1'), 'x', 'y')
        raises('launch_entry: IGZO template without GAMMA0 refused', S.launch_entry, mx, 'S5-H6p3-1-2p0', 2.0, 'S3-11',
               {'Ns_cm2': 4e12, 'WT_eV': 0.04, 'gamma0': None}, nuis(2.0, '1e12', '1'), 'x', 'y')
        eg = S.launch_entry(mx, 'S5-H2p0-1-6p3', 6.3, 'S3-12', {'Ns_cm2': 5e12, 'WT_eV': 0.045, 'gamma0': -0.274}, nuis(6.3, '1.5e+12', '30'), 'x', 'y')
        kv = {S._okey(o): o.split('=', 1)[1] for o in eg['overrides']}
        expect('A7 IGZO entry: GAMMA0 replaced, IGZO model kept', (kv[S.G0], kv['solver.physics_options.mobility.model'], kv[S.NT2]), ('-0.274', 'igzo_tokyo', '2.5e+19'))
        expect('template_for: none / tail / IGZO / tail + IGZO', [S.template_for([], 2.0), S.template_for(['tail 50:50 (S3-07=S0-01, S3-08, S3-09)'], 6.3),
                                                                  S.template_for(['IGZO.TOKYO GAMMA0 +0.30 (S3-14, S3-15, S3-16)'], 13.2),
                                                                  S.template_for(['IGZO.TOKYO GAMMA0 -0.31 (S3-11, S3-12, S3-13)', 'tail bulk (S3-04=S0-01, S3-05, S3-06)'], 2.0)],
               [('S4A-01-2p0', None), ('S3-08', None), ('S3-16', None), ('S3-04', 'S3-11')])
        tid, tov = S.combined_template(mx, ['IGZO.TOKYO GAMMA0 -0.31 (S3-11, S3-12, S3-13)', 'tail bulk (S3-04=S0-01, S3-05, S3-06)'], 13.2)
        expect('combined template: S3-06 + the four IGZO mobility overrides', (tid, tov[:len(mx['S3-06']['campaign_entry']['overrides'])] == mx['S3-06']['campaign_entry']['overrides'],
                                                                               [S._okey(o) for o in tov[-4:]]), ('S3-06+S3-13', True, list(S.MOBILITY_KEYS)))
        raises('template_for: two tails refused', S.template_for, ['tail bulk (S3-04=S0-01, S3-05, S3-06)', 'tail 50:50 (S3-07=S0-01, S3-08, S3-09)'], 2.0)

        # ---- held-out entries from a frozen record (synthetic record of S4a candidate S4A-04)
        x4 = S.coords_of_overrides(mx['S4A-04-2p0']['campaign_entry']['overrides'])
        fr = {'candidate': 'S4A-04', 'stage': 'S4a', 'coords': x4, 'held_out': {'overrides': [f'{S.QF}=1.6e+12', f'{S.MU(6.3)}=26.4']}, 'sha256': 'f' * 64,
              'training_sqrtJ_dec': 0.5, 'role': 'primary prediction'}
        pe = S.pred_entry(mx, 6.3, 'best', fr, {}, {'fold_choice': []})
        k6 = {S._okey(o): o.split('=', 1)[1] for o in pe['overrides']}
        expect('pred_entry S4A-04 at 6.3: Nt2 / W_T from its matrix entry, Q_f / mu_band[6.3] from the record; id / label / timeout',
               (k6[S.NT2], k6[S.WTA], k6[S.QF], k6[S.MU(6.3)], pe['id'], pe['label'], pe['timeout']),
               ('4.4285e+19', '0.0572', '1.6e+12', '26.4', 'S5-H6p3-PRED-best', 'c10_s5_h6p3_pred_best_6p3', 2000))
        expect('pred_entry: only the four keys differ from S4A-01-6p3',
               sorted({S._okey(o) for o in set(pe['overrides']) ^ set(mx['S4A-01-6p3']['campaign_entry']['overrides'])}), sorted([S.NT2, S.WTA, S.QF, S.MU(6.3)]))
        raises('pred_entry: frozen coordinates that differ from the candidate entry refused', S.pred_entry, mx, 6.3, 'best',
               dict(fr, coords=dict(x4, WT=0.05)), {}, {'fold_choice': []})
        raises('pred_entry: held-out overrides at the wrong film refused', S.pred_entry, mx, 6.3, 'best',
               dict(fr, held_out={'overrides': [f'{S.QF}=1.6e+12', f'{S.MU(2.0)}=26.4']}), {}, {'fold_choice': []})
        k_rec = {2: {'entries': {'S5-H6p3-2-2p0': {'overrides': S._replace(mx['S4A-01-2p0']['campaign_entry']['overrides'], {S.NT2: '3.3e+19', S.WTA: '0.0451'})}}}}
        fr5 = dict(fr, candidate='S5-H6p3-2', stage='S5', coords=S.coords_of_overrides(k_rec[2]['entries']['S5-H6p3-2-2p0']['overrides']))
        k5 = {S._okey(o): o.split('=', 1)[1] for o in S.pred_entry(mx, 6.3, 'runner_up', fr5, k_rec, {'fold_choice': []})['overrides']}
        expect('pred_entry of a fold candidate: strings from its training record', (k5[S.NT2], k5[S.WTA]), ('3.3e+19', '0.0451'))

        # ---- RUN_INDEX state, run directories, fold candidates
        rows = [{'run_id': 'run_0160', 'label': 'c10_s5_h6p3_1_2p0_2p0', 'exit_code': '', 'started': True},
                {'run_id': 'run_0160', 'label': 'c10_s5_h6p3_1_2p0_2p0', 'exit_code': '0', 'started': False},
                {'run_id': 'run_0161', 'label': 'c10_s5_h6p3_1_13p2_13p2', 'exit_code': '', 'started': True},
                {'run_id': 'run_0157', 'label': 'c10_s4c_2p0_2p0', 'exit_code': '0', 'started': False}]
        st = S.index_state(rows)
        expect('index_state: S5 labels only; finished / unfinished', {k: (v['first'], v['finished']) for k, v in st.items()},
               {'c10_s5_h6p3_1_2p0_2p0': ('run_0160', True), 'c10_s5_h6p3_1_13p2_13p2': ('run_0161', False)})
        TMP.mkdir(exist_ok=True); runs = TMP / 'runs'; (runs / 'run_0160_2p0_c10_s5_h6p3_1_2p0_2p0').mkdir(parents=True, exist_ok=True)
        expect('run_dir_of: finished run with directory', S.run_dir_of('c10_s5_h6p3_1_2p0_2p0', 2.0, st, runs)[1], None)
        expect('run_dir_of: unfinished run refused', 'no finish row' in S.run_dir_of('c10_s5_h6p3_1_13p2_13p2', 13.2, st, runs)[1], True)
        st2 = S.index_state(rows + [{'run_id': 'run_0162', 'label': 'c10_s5_h6p3_1_2p0_2p0', 'exit_code': '', 'started': True}])
        expect('run_dir_of: two run ids for one label refused', '2 run ids' in S.run_dir_of('c10_s5_h6p3_1_2p0_2p0', 2.0, st2, runs)[1], True)
        S.OUTD = TMP / 's5_A53'
        rec1 = seal({'entries': {'S5-H6p3-1-2p0': {'label': 'c10_s5_h6p3_1_2p0_2p0', 'thickness': 2.0},
                                 'S5-H6p3-1-13p2': {'label': 'c10_s5_h6p3_1_13p2_13p2', 'thickness': 13.2}}})
        expect('write_once: new record written', S.write_once(S.path(6.3, 't1'), rec1), True)
        expect('write_once: identical content is a no-op', S.write_once(S.path(6.3, 't1'), rec1), False)
        raises('write_once: other content never overwrites', S.write_once, S.path(6.3, 't1'), seal({'x': 1}))
        expect('last_record H6p3 == 1', S.last_record(6.3), 1)
        c, bad = S.fold_candidates(6.3, 1, st, runs)
        expect('fold_candidates: t1 incomplete (13.2 nm run unfinished)', (len(c), len(bad), 'no finish row' in bad[0]), (1, 1, True))
        rows.append({'run_id': 'run_0161', 'label': 'c10_s5_h6p3_1_13p2_13p2', 'exit_code': '0', 'started': False})
        (runs / 'run_0161_13p2_c10_s5_h6p3_1_13p2_13p2').mkdir(exist_ok=True)
        c, bad = S.fold_candidates(6.3, 1, S.index_state(rows), runs)
        expect('fold_candidates: t1 complete -> one S5 candidate on the two training films', (bad, c[0]['id'], c[0]['stage'], c[0]['fold'], sorted(c[0]['runs'])),
               ([], 'S5-H6p3-1', 'S5', 6.3, ['13.2', '2.0']))
        S.path(6.3, 't1').write_text(json.dumps(dict(rec1, entries={})))
        expect('fold_candidates: an edited record is refused', 'does not match its sha256' in S.fold_candidates(6.3, 1, S.index_state(rows), runs)[1][0], True)
        dec_same = {'same_as_full_data': True}; dec_a7 = {'same_as_full_data': False}
        fa = S.fold_archive(6.3, dec_same, c)
        expect('fold_archive (same branch): 15 S4a candidates (A51) + the fold candidates', (len(fa['candidates']), fa['candidates'][0]['id'], fa['candidates'][-1]['id']),
               (16, 'S4A-01', 'S5-H6p3-1'))
        expect('fold_archive (A7): the fold candidates only', len(S.fold_archive(6.3, dec_a7, c)['candidates']), 1)

        # ---- LOO arithmetic
        jk = S.jackknife([1.0, 2.0, 4.0])
        expect('LOO-3 jackknife: var_JK = (n-1)/n sum (x - mean)^2', (jk['n'], round(jk['mean'], 12), round(jk['var_JK'], 12)), (3, round(7 / 3, 12), round(2 / 3 * (16 / 9 + 1 / 9 + 25 / 9), 12)))
        expect('LOO-3 jackknife: fewer than two values -> None', S.jackknife([1.0, None])['var_JK'], None)
        acc = {'verdict': 'FAIL: active_rmse_dec', 'criteria': {'active_rmse_dec': {'value': 0.4}, 'dVth_cc_V': {'value': -0.2}, 'Id3V_err_pct': {'value': 100.0},
                                                                 'SS_a1_err_pct': {'value': 10.0, 'sim_mV_dec': 220.0, 'meas_mV_dec': 200.0},
                                                                 'mu_FE_err_pct': {'per_V': {'2.0': {'value': -50.0, 'sim': 5.0, 'meas': 10.0}}}}}
        l1 = S.loo1(acc)
        expect('LOO-1 from the frozen acceptance', (l1['dVth_cc_V'], round(l1['dlog10_Id3V_dec'], 12), l1['dSS_mV_dec'], l1['dmuFE_2V_cm2Vs'], l1['active_rmse_dec']),
               (-0.2, round(math.log10(2.0), 12), 20.0, -5.0, 0.4))
        expect('LOO-1: unresolved I_D(3 V) stays None', S.loo1({**acc, 'criteria': {**acc['criteria'], 'Id3V_err_pct': {'value': None}}})['dlog10_Id3V_dec'], None)
        expect('pins of the driver pass on this tree', S.pin_problems(), [])
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print(f'{sum(results)}/{len(results)} passed'); return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main())
