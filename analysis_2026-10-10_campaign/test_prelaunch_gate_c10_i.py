"""Tests of prelaunch_gate_c10_i.py (register A53; NO launch; no repo file written except the temporary ./test_tmp_c10_i, removed at the end).

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"; & <venv python> -I -B analysis_2026-10-10_campaign/test_prelaunch_gate_c10_i.py
In-process cases import the gate and give it the pinned H, G2, G, F, D/E and C10 gate modules with patched inputs: synthetic register / decision
log, synthetic RUN_INDEX (run_id/label of the real rows up to run_0077 only, plus synthetic STARTED rows of the reused run_0061/0068/0069 carrying
the pinned PA-12 hashes; synthetic S1-06R/DIAG rows run_0078..run_0096, D/E rows run_0097..run_0101, stage F rows run_0102..run_0113, S4a rows
run_0114..run_0156 with the interrupted run_0150, S4c rows run_0157..run_0159 with the pinned decks, and the cases' S4d / S5 rows: no real row
content beyond run_id and label is copied), the pinned S5 driver loaded with its record directory and run root moved to the temporary directory,
synthetic sealed driver records (entries built by the driver from the registered templates, dry builds by run_campaign.current_deck_text), plan
files written by the pinned generator into a temporary config directory, a fake process list and a stubbed git check.
"""
import contextlib, csv, importlib.util, io, json, os, shutil, sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent; PKG = HERE.parent; TMP = HERE / 'test_tmp_c10_i'
GATEI = HERE / 'prelaunch_gate_c10_i.py'; GATEH = HERE / 'prelaunch_gate_c10_h.py'; G2F = HERE / 'prelaunch_gate_c10_g2.py'; GG = HERE / 'prelaunch_gate_c10_g.py'
FGF = HERE / 'prelaunch_gate_c10_f.py'; DEG = HERE / 'prelaunch_gate_c10_de.py'; C10 = HERE / 'prelaunch_gate_c10.py'; DRV = HERE / 's5_loo_driver.py'
FIELDS = ['run_id', 'timestamp_utc', 'thickness_nm', 'label', 'deck_sha256', 'model_sha256', 'command', 'simulator', 'exit_code', 'converged',
          'elapsed_s', 'output_dir', 'notes']
MODEL = 'config/iwo_material_model_v3.yaml'
os.environ['IWO_MODEL_FILE'] = MODEL
results = []


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


I0 = load(GATEI, 'gi_constants'); H0 = load(GATEH, 'gh_constants'); G0 = load(GG, 'gg_constants'); F0 = load(FGF, 'gf_constants')
D0 = load(DEG, 'gde_constants'); C0 = load(C10, 'c10_constants')
OA = G0.ORDER; I_INT = OA.index('S4A-14-2p0')
if str(HERE) not in sys.path: sys.path.insert(0, str(HERE))
GEN = load(HERE / 'make_campaign_configs.py', 'mcc_for_tests')


def expect(name, got, want):
    ok = got == want; results.append(ok); print(f"{'ok  ' if ok else 'FAIL'} {name}: {got}", flush=True)


def driver():
    s = load(DRV, 's5_driver_test'); s.OUTD = TMP / 's5_A53'; s.RUNS = TMP / 'runs'; return s


S = driver(); MX = S.matrix_by_id(); FSHA = S.FROZEN['profile_s4s5.py']


def seal(d):
    d = json.loads(S._canon({k: v for k, v in d.items() if k != 'sha256'})); d['sha256'] = S.tsha(S._canon(d)); return d


def logs(tag, a53=True, draft=False, a54=True):
    TMP.mkdir(exist_ok=True); reg, dec = TMP / f'reg_{tag}.md', TMP / f'dec_{tag}.md'; s = H0.RECORD_SEAL[:16]
    h = ['### A49: stage G1 prerequisites: 0-launch S3 decision before S4a ... (PA-8 adoption ...); S4a forms N/T/I/TI ... (PA-12); PA-16 ...; PA-20 ...',
         '### A50: S4a execution entries of form N: S4A-02 .. S4A-15, route plans, prelaunch_gate_c10_g.py',
         '### A51: S4a resume after the interrupted launch run_0150: one infrastructure retry of S4A-14-2p0 (--retry S4A-14-2p0), prelaunch_gate_c10_g2.py',
         f'### A52: PA-18 S4c confirmation wrapper s4c_confirm_wrapper.py, record {s}..., S4c and S4d execution entries, prelaunch_gate_c10_h.py']
    if a53: h.append('### A53: S5 leave-one-film-out execution: s5_loo_driver.py, route plans, prelaunch_gate_c10_i.py' + (' (draft)' if draft else ''))
    if a54: h.append('### A54: S4d resume after the interrupted launch run_0160: one --retry S4D-2p0, prelaunch_gate_c10_i.py v2')
    r = ['| D-69 | x | Register A49: s3_decision_a49.py, PA-8 | x | x | IN FORCE |',
         '| D-70 | x | Register A50: form N, campaign_C10_S4a_b1, prelaunch_gate_c10_g.py | x | x | IN FORCE |',
         '| D-71 | x | Register A51: run_0150 interrupted; --retry S4A-14-2p0; prelaunch_gate_c10_g2.py | x | x | IN FORCE |',
         f'| D-75 | x | Register A52: PA-18 s4c_confirm_wrapper.py record {s}; prelaunch_gate_c10_h.py | x | x | IN FORCE |']
    if a53: r.append('| D-76 | x | Register A53: S5 s5_loo_driver.py; prelaunch_gate_c10_i.py | x | x | IN FORCE |')
    if a54: r.append('| D-77 | x | Register A54: run_0160 interrupted; --retry S4D-2p0; prelaunch_gate_c10_i.py | x | x | IN FORCE |')
    reg.write_text('\n'.join(h) + '\n'); dec.write_text('\n'.join(r) + '\n'); return reg, dec


def fin(rid, lab): return {'run_id': rid, 'label': lab, 'exit_code': '0', 'notes': 'synthetic finish'}


def prev_rows(s4c=True, s4d='done'):
    rows = []
    for k, e in enumerate(C0.LAUNCH_ORDER):
        rid = f'run_{78 + k:04d}'; rows += [{'run_id': rid, 'label': C0.LABEL[e], 'notes': 'STARTED synthetic'}, fin(rid, C0.LABEL[e])]
    for k, e in enumerate(D0.ORDER):
        rid = f'run_{97 + k:04d}'; rows += [{'run_id': rid, 'label': D0.LABEL[e], 'notes': 'STARTED synthetic'}, fin(rid, D0.LABEL[e])]
    for k, e in enumerate(F0.ORDER):
        rid = f'run_{102 + k:04d}'; rows += [{'run_id': rid, 'label': F0.LABEL[e], 'notes': 'STARTED synthetic'}, fin(rid, F0.LABEL[e])]
    keys = OA[:I_INT] + ['S4A-14-2p0'] + OA[I_INT:]
    for i, k in enumerate(keys):
        rid = f'run_{114 + i:04d}'; lab = G0.LABEL[k]
        rows.append({'run_id': rid, 'label': lab, 'deck_sha256': G0.DECK[k], 'model_sha256': G0.MATERIAL[k], 'notes': f'STARTED model={MODEL}'})
        if rid != 'run_0150': rows.append(fin(rid, lab))
    if s4c:
        for i, k in enumerate(H0.ORDER[:3]): rows += h_row(f'run_{157 + i:04d}', k)
    if s4d is not None: rows += h_row('run_0160', 'S4D-2p0', finish=(s4d == 'intr_finished'))   # A54: the interrupted launch
    if s4d == 'done':
        for i, k in enumerate(H0.ORDER[3:]): rows += h_row(f'run_{161 + i:04d}', k)
    return rows


def h_row(rid, k, finish=True):
    lab = H0.LABEL[k]; s = {'run_id': rid, 'label': lab, 'deck_sha256': H0.DECK[k], 'model_sha256': H0.MATERIAL[k], 'notes': f'STARTED model={MODEL}'}
    return [s] + ([fin(rid, lab)] if finish else [])


def index(tag, extra, s4c=True, s4d='done'):
    TMP.mkdir(exist_ok=True); p = TMP / f'idx_{tag}.csv'
    real = [(r['run_id'], r['label']) for r in csv.DictReader((PKG / 'results' / 'RUN_INDEX.csv').open(newline='')) if int(r['run_id'][4:]) <= 77]
    reuse = {rid: (lab, dk, mk) for rid, lab, dk, mk in G0.REUSE.values()}
    with p.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); done = set()
        for rid, lab in real:
            if rid in reuse and rid not in done:
                _, dk, mk = reuse[rid]; done.add(rid)
                w.writerow({'run_id': rid, 'label': lab, 'deck_sha256': dk, 'model_sha256': mk, 'notes': f'STARTED model={MODEL}'})
            else: w.writerow({'run_id': rid, 'label': lab, 'notes': 'SYNTHETIC'})
        for row in prev_rows(s4c, s4d) + extra: w.writerow({k: row.get(k, '') for k in FIELDS})
    return p


# ------------------------------------------------------------------------------------------------ synthetic S5 records (fold H6p3)
XDECK = {1: (5.0e12, 0.0451), 2: (5.5e12, 0.0466), 3: (6.0e12, 0.0472), 4: (6.5e12, 0.0489)}
RID = {('t1', 0): 164, ('t1', 1): 165, ('t2', 0): 166, ('t2', 1): 167, ('t3', 0): 168, ('t3', 1): 169, ('t4', 0): 170, ('t4', 1): 171,
       ('pred', 0): 172, ('pred', 1): 173}   # after the A54 S4d rows run_0160 (interrupted) .. run_0163
DEC = None


def decision():
    global DEC
    DEC = seal({'record': 'synthetic fold decision', 'held_out_nm': 6.3, 'same_as_full_data': True, 'fold_choice': [], 'verdict': 'SAME BRANCH CHOICE'})
    S.write_once(S.path(6.3, 'branch'), DEC); return DEC


def nuis(t): return [f'{S.QF}=1.5e+12', f'{S.MU(t)}=' + {2.0: '9.1', 6.3: '27.3', 13.2: '51.2'}[t]]


def entry(eid, t, k):
    ns, wt = XDECK[k]; return S.launch_entry(MX, eid, t, S.TEMPLATE[None][t], {'Ns_cm2': ns, 'WT_eV': wt, 'gamma0': None}, nuis(t), 'synthetic', 'synthetic')


def full_state(upto_step):
    rows = []
    for (st, j), n in RID.items():
        if S.STEPS.index(st) < S.STEPS.index(upto_step):
            eid = S.entry_ids(6.3, st)[j]; lab = MX[eid]['campaign_entry']['label']; t = float(MX[eid]['campaign_entry']['thickness'])
            rows += [{'run_id': f'run_{n:04d}', 'label': lab, 'exit_code': '', 'started': True}, {'run_id': f'run_{n:04d}', 'label': lab, 'exit_code': '0', 'started': False}]
            (S.RUNS / f'run_{n:04d}_{S.TAG[t]}_{lab}').mkdir(parents=True, exist_ok=True)
    return S.index_state(rows)


def train_record(k, cands=None):
    st = f't{k}'; ids = S.entry_ids(6.3, st); ents = {eid: entry(eid, t, k) for eid, t in zip(ids, S.train_of(6.3))}
    if cands is None: cands, bad = S.fold_candidates(6.3, k - 1, full_state(st)); assert not bad, bad
    rec = seal({'record': 'synthetic training record', 'fold': 'H6p3', 'held_out_nm': 6.3, 'training_films': [2.0, 13.2], 'k': k, 'step': st, 'mode': 'S4a archive',
                'decision_sha256': DEC['sha256'], 'fold_candidates_before': cands, 'entries': ents, 'dry_build': S.dry_build(ents),
                'driver_sha256': I0.DRIVER_SHA, 'code_sha256': FSHA})
    S.path(6.3, st).write_text(json.dumps(rec, indent=1)); return rec


def pred_record(bad_bind=False):
    fz = {rk: seal({'record': 'synthetic frozen', 'rank': rk, 'candidate': 'S4A-04'}) for rk in S.RANKS}
    for rk in S.RANKS: S.path(6.3, f'frozen_{rk}').write_text(json.dumps(fz[rk], indent=1))
    ids = S.entry_ids(6.3, 'pred'); ents = {eid: entry(eid, 6.3, j + 1) for j, eid in enumerate(ids)}
    rec = seal({'record': 'synthetic held-out record', 'fold': 'H6p3', 'held_out_nm': 6.3, 'step': 'pred', 'mode': 'S4a archive', 'decision_sha256': DEC['sha256'],
                'frozen': {rk: {'sha256': ('0' * 64 if bad_bind and rk == 'best' else fz[rk]['sha256'])} for rk in S.RANKS},
                'entries': ents, 'dry_build': S.dry_build(ents), 'driver_sha256': I0.DRIVER_SHA, 'code_sha256': FSHA})
    S.path(6.3, 'pred').write_text(json.dumps(rec, indent=1)); return rec


def plan_for(st, tweak=None):
    p = GEN.i_plan(6.3, st, S.path(6.3, st))
    if tweak: tweak(p)
    (TMP / 'config').mkdir(parents=True, exist_ok=True); (TMP / 'config' / f'campaign_C10_S5_h6p3_{st}.json').write_text(json.dumps(p, indent=1))


def s5_rows(steps, finish_last=True, deck=None, order=None):
    """STARTED (+ finish) rows of fold H6p3 entries of the given steps, in the registered order (or the given (step, j) order)"""
    seq = order or [(st, j) for st in steps for j in range(2)]; out = []
    for n_, (st, j) in enumerate(seq):
        rec = json.loads(S.path(6.3, st).read_text()); eid = S.entry_ids(6.3, st)[j]; e = rec['entries'][eid]; rid = f'run_{RID[(st, j)]:04d}'
        out.append({'run_id': rid, 'label': e['label'], 'deck_sha256': deck or rec['dry_build'][eid]['deck_sha256'],
                    'model_sha256': rec['dry_build'][eid]['model_sha256'], 'notes': f'STARTED model={MODEL}'})
        if finish_last or n_ < len(seq) - 1: out.append(fin(rid, e['label']))
    return out


def reset():
    shutil.rmtree(TMP / 's5_A53', ignore_errors=True); shutil.rmtree(TMP / 'runs', ignore_errors=True); shutil.rmtree(TMP / 'config', ignore_errors=True)
    (TMP / 's5_A53').mkdir(parents=True, exist_ok=True); (TMP / 'runs').mkdir(parents=True, exist_ok=True)


def case(name, want, idx, reg_dec, procs=(), patch=None, env=None, git=(True, 'synthetic HEAD'), argv=('--check',)):
    i = load(GATEI, 'gi_under_test'); h = load(GATEH, 'gh_under_test'); g2 = load(G2F, 'gg2_under_test'); G = load(GG, 'gg_under_test')
    Fm = load(FGF, 'gf_under_test'); D = load(DEG, 'gde_under_test'); C = load(C10, 'c10_under_test')
    C.list_processes = lambda: list(procs)
    C.INDEX = idx; C.REGISTER, C.DECISIONS = reg_dec; D.c10_module = lambda: C; Fm.de_module = lambda: D; G.f_module = lambda: Fm; g2.g_module = lambda: G
    h.g2_module = lambda: g2; i.h_module = lambda: h; i.driver_module = driver; i.CFG = TMP / 'config'
    if git is not None: i.committed_in_git = lambda relp: git
    if patch: patch(i)
    os.chdir(PKG); buf = io.StringIO(); old = dict(os.environ)
    if env: os.environ.update(env)
    try:
        with contextlib.redirect_stdout(buf): rc = i.main(list(argv))
    finally: os.environ.clear(); os.environ.update(old)
    out = buf.getvalue(); [print('       ' + l) for l in out.splitlines() if l.startswith(('GATE PASSED', 'NOTHING', 'GATE STOP', '[FAIL]', '[STOP]', '&'))]
    expect(name, rc, want); return out


def main():
    try:
        TMP.mkdir(exist_ok=True); L = logs('ok'); reset()
        out = case('no fold decision -> 4 (next: branch --held 6.3)', 4, index('n0', []), L)
        expect('  names the 0-launch driver step', 'branch --held 6.3' in out, True)
        decision()
        out = case('decision, no t1 record -> 4 (next --held 6.3)', 4, index('n1', []), L)
        expect('  names next --held 6.3', 'next --held 6.3' in out, True)
        train_record(1); plan_for('t1')
        out = case('t1 record + plan -> 0, campaign_C10_S5_h6p3_t1, 2 entries from run_0164', 0, index('t1', []), L)
        expect('  command: config/campaign_C10_S5_h6p3_t1.json, run_0164, 2 entries, no --retry',
               out.rstrip().endswith('scripts/run_campaign.py config/campaign_C10_S5_h6p3_t1.json') and 'first run id run_0164' in out and 'these 2 entries' in out, True)
        out = case('S4d incomplete (retry pending) -> 4 for S5 (S4d before S5)', 4, index('s4dp', [], s4d='intr'), L)
        expect('  names --s4d', '--s4d' in out, True)
        case('A54 not logged -> 1', 1, index('n54', []), logs('n54', a54=False))
        case('t1 record not committed in git HEAD -> 1', 1, index('git', []), L, git=(False, 'not in HEAD'))
        case('fit violated (need 68: 103 + 30 + 0 + 68 = 201 > 200) -> 1', 1, index('fit', []), L, patch=lambda m: setattr(m, 'NEED_AFTER_S5', 68))
        case('fit at the limit (need 67: 103 + 30 + 0 + 67 = 200) -> 0', 0, index('fit2', []), L, patch=lambda m: setattr(m, 'NEED_AFTER_S5', 67))
        case('A53 not logged -> 1', 1, index('n53', []), logs('n53', a53=False))
        case('A53 heading draft -> 1', 1, index('d53', []), logs('d53', draft=True))
        plan_for('t1', lambda p: p['runs'][0].update(timeout=1700))
        case('t1 plan differs from the generator (timeout) -> 1', 1, index('pl', []), L)
        plan_for('t1')
        good = S.path(6.3, 't1').read_text(); r = json.loads(good); r['k'] = 2; S.path(6.3, 't1').write_text(json.dumps(r, indent=1))
        case('t1 record edited after sealing -> 1', 1, index('sl', []), L)
        r = json.loads(good); r['driver_sha256'] = '1' * 64; S.path(6.3, 't1').write_text(json.dumps(seal(r), indent=1)); plan_for('t1')
        case('t1 record made by another driver -> 1', 1, index('dr', []), L)
        r = json.loads(good); r['dry_build']['S5-H6p3-1-2p0']['deck_sha256'] = '2' * 64; S.path(6.3, 't1').write_text(json.dumps(seal(r), indent=1)); plan_for('t1')
        case('t1 record dry build differs from the generator -> 1', 1, index('db', []), L)
        S.path(6.3, 't1').write_text(good); plan_for('t1')
        case('S5-H6p3-1-2p0 started, no finish row -> 3', 3, index('u1', s5_rows(['t1'], order=[('t1', 0)], finish_last=False)), L)
        out = case('S5-H6p3-1-2p0 done -> 0, same plan, 1 entry left from run_0165', 0, index('h1', s5_rows(['t1'], order=[('t1', 0)])), L)
        expect('  next S5-H6p3-1-13p2, run_0165', 'S5-H6p3-1-13p2' in out and 'run_0165' in out and 'these 1 entry' in out and 'campaign_C10_S5_h6p3_t1.json' in out.splitlines()[-1], True)
        case('S5-H6p3-1-13p2 started before -2p0 (order) -> 1', 1, index('or', s5_rows(['t1'], order=[('t1', 1)])), L)
        case('S5 STARTED deck differs from the record -> 1', 1, index('dk', s5_rows(['t1'], order=[('t1', 0)], deck='3' * 64)), L)
        case('unknown label above run_0077 -> 1', 1, index('unk', [{'run_id': 'run_0164', 'label': 'c10_s5_hx_1_2p0_2p0', 'notes': 'STARTED'}]), L)
        t1rows = s5_rows(['t1']); full_state('t2')
        out = case('t1 complete, no t2 record -> 4 (next --held 6.3)', 4, index('n2', t1rows), L)
        expect('  names next --held 6.3 (t2)', 'next --held 6.3' in out and 't2' in out, True)
        train_record(2, cands=[]); plan_for('t2')
        case('t2 record built on the wrong fold inventory -> 1', 1, index('wi', t1rows), L)
        S.path(6.3, 't2').unlink(); train_record(2); plan_for('t2')
        out = case('t1 complete, t2 record + plan -> 0, campaign_C10_S5_h6p3_t2 from run_0166', 0, index('t2', t1rows), L)
        expect('  command names the t2 plan and run_0166', out.rstrip().endswith('config/campaign_C10_S5_h6p3_t2.json') and 'run_0166' in out, True)
        for k in (3, 4): full_state(f't{k}'); train_record(k); plan_for(f't{k}')
        full_state('pred')
        out = case('t1..t4 complete, no held-out record -> 4 (freeze --held 6.3)', 4, index('n5', s5_rows(['t1', 't2', 't3', 't4'])), L)
        expect('  names freeze --held 6.3', 'freeze --held 6.3' in out, True)
        pred_record(bad_bind=True); plan_for('pred')
        case('held-out record bound to another frozen record -> 1', 1, index('pb', s5_rows(['t1', 't2', 't3', 't4'])), L)
        pred_record(); plan_for('pred')
        out = case('t1..t4 complete, held-out record + frozen records + plan -> 0, pred plan from run_0172', 0, index('pr', s5_rows(['t1', 't2', 't3', 't4'])), L)
        expect('  command names the pred plan and run_0172', out.rstrip().endswith('config/campaign_C10_S5_h6p3_pred.json') and 'run_0172' in out, True)
        out = case('fold H6p3 complete -> 4 (next fold: branch --held 2.0)', 4, index('h6', s5_rows(['t1', 't2', 't3', 't4', 'pred'])), L)
        expect('  names branch --held 2.0', 'branch --held 2.0' in out, True)
        stop = seal({'record': 'synthetic stop', 'fold': 'H6p3', 'started_entries': {'S5-H6p3-1-2p0': {}, 'S5-H6p3-1-13p2': {}}, 'driver_sha256': I0.DRIVER_SHA})
        S.path(6.3, 'stop').write_text(json.dumps(stop, indent=1))
        out = case('H6p3 stopped after t1 (committed stop record) -> 4 (next fold: branch --held 2.0)', 4, index('st', t1rows), L)
        expect('  names branch --held 2.0', 'branch --held 2.0' in out, True)
        case('a t2 run after the H6p3 stop -> 1 (not in the registered sequence)', 1, index('st2', s5_rows(['t1', 't2'])), L)
        S.path(6.3, 'stop').unlink()
        out = case('S4d mode, run_0160 interrupted -> 0, campaign_C10_S4d --retry S4D-2p0, 3 entries from run_0161', 0, index('s4d', [], s4d='intr'), L, argv=('--check', '--s4d'))
        expect('  command: S4d plan with --retry S4D-2p0, first run id run_0161, 3 entries',
               out.rstrip().endswith('scripts/run_campaign.py config/campaign_C10_S4d.json --retry S4D-2p0') and 'run_0161' in out and 'these 3 entries' in out, True)
        case('S4d mode, retry run_0161 started, no finish row -> 3', 3, index('s4du', h_row('run_0161', 'S4D-2p0', finish=False), s4d='intr'), L, argv=('--check', '--s4d'))
        out = case('S4d mode, retry finished -> 0, S4d plan, 2 entries from run_0162, no --retry', 0, index('s4dr', h_row('run_0161', 'S4D-2p0'), s4d='intr'), L, argv=('--check', '--s4d'))
        expect('  command: S4d plan without --retry, S4D-6p3, run_0162, 2 entries',
               out.rstrip().endswith('scripts/run_campaign.py config/campaign_C10_S4d.json') and 'S4D-6p3' in out and 'run_0162' in out and 'these 2 entries' in out, True)
        case('S4d mode, run_0160 has a finish row (not the registered interruption) -> 1', 1, index('s4df', [], s4d='intr_finished'), L, argv=('--check', '--s4d'))
        case('S4d mode, a third S4D-2p0 run -> 1', 1, index('s4d3', h_row('run_0161', 'S4D-2p0') + h_row('run_0162', 'S4D-2p0'), s4d='intr'), L, argv=('--check', '--s4d'))
        case('S4d mode, run_0160 missing -> 1', 1, index('s4dm', [], s4d=None), L, argv=('--check', '--s4d'))
        case('S4d mode, S4d complete -> 4', 4, index('s4dc', []), L, argv=('--check', '--s4d'))
        case('S4c incomplete (no S4c rows) -> 1', 1, index('nc', [], s4c=False), L)
        case('Silvaco process running -> 1', 1, index('proc', []), L, procs=[(4242, 'deckbuild.exe', 'deckbuild.exe -run x')])
        case('runner python running -> 1', 1, index('rpy', []), L, procs=[(4243, 'python.exe', 'python scripts/run_campaign.py config/x.json')])
        case('IWO_MODEL_FILE wrong -> 1', 1, index('env', []), L, env={'IWO_MODEL_FILE': 'config/iwo_material_model_v2.yaml'})
        case('H gate pin differs -> 1', 1, index('pin', []), L, patch=lambda m: setattr(m, 'H_GATE_SHA', '0' * 64))
        case('driver pin differs -> 1', 1, index('dpin', []), L, patch=lambda m: setattr(m, 'DRIVER_SHA', '0' * 64))
        case('generator pin differs -> 1', 1, index('gpin', []), L, patch=lambda m: setattr(m, 'GENERATOR_SHA', '0' * 64))
        expect('unit: constants', (I0.NEED_AFTER_S5, I0.LAST_S4C, I0.S5_TOTAL, I0.H_GATE_SHA[:8], I0.INTERRUPTED_D, I0.RETRY_D), (46, 'run_0159', 30, '3e96b825', 'run_0160', 'S4D-2p0'))
        expect('unit: next_invocation with nothing started -> H6p3 t1', I0.next_invocation(S, set(), [])[:2], (6.3, 't1'))
        expect('unit: next_invocation with H6p3 stopped -> H2p0 t1', I0.next_invocation(S, set(), [6.3])[:2], (2.0, 't1'))
        expect('unit: expected sequence length 30; stopped fold keeps its pre-stop entries', (len(I0.expected_sequence(S, {})),
                                                                                              len(I0.expected_sequence(S, {6.3: {'S5-H6p3-1-2p0'}}))), (30, 21))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print(f'{sum(results)}/{len(results)} passed'); return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main())
