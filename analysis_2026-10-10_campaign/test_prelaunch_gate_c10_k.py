"""Tests of prelaunch_gate_c10_k.py (NO launch; no repo file written except the temporary ./test_tmp_c10_k, removed at the end).

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"; & <venv python> -I -B analysis_2026-10-10_campaign/test_prelaunch_gate_c10_k.py
In-process cases load the gate (and through it gate J and the chain, pinned) and patch: a synthetic register / decision log (the real lines plus,
per case, a synthetic K amendment line), a synthetic RUN_INDEX (state columns of the real rows up to run_0181; synthetic A59 rows with the A59
record's dry-build pins; the cases' K rows), a fake process list, stubbed git / REG-001 / tag checks and a fixed clock.
"""
import contextlib, csv, importlib.util, io, json, os, shutil, sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent; PKG = HERE.parent; TMP = HERE / 'test_tmp_c10_k'
FIELDS = ['run_id', 'timestamp_utc', 'thickness_nm', 'label', 'deck_sha256', 'model_sha256', 'command', 'simulator', 'exit_code', 'converged',
          'elapsed_s', 'output_dir', 'notes']
MODEL = 'config/iwo_material_model_v3.yaml'
results = []


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def expect(name, got, want):
    ok = got == want; results.append(ok); print(f"{'ok  ' if ok else 'FAIL'} {name}: {got}", flush=True)


K0 = load(HERE / 'prelaunch_gate_c10_k.py', 'gk_constants'); J0 = load(HERE / 'prelaunch_gate_c10_j.py', 'gj_constants_k')
JREC = json.loads((PKG / J0.RECORD_REL).read_text()); KREC = json.loads((PKG / K0.RECORD_REL).read_text())
JORDER = [i for _, ids in JREC['batches'] for i in ids]; KORDER = [i for _, ids in KREC['batches'] for i in ids]
REAL = [r for r in csv.DictReader((PKG / 'results' / 'RUN_INDEX.csv').open(newline='')) if int(r['run_id'][4:]) <= 181]


def logs(tag, kline=True):
    TMP.mkdir(exist_ok=True); reg, dec = TMP / f'reg_{tag}.md', TMP / f'dec_{tag}.md'; C = J0.chain()[0][-1]
    r = C.REGISTER.read_text(encoding='utf-8').splitlines(); d = C.DECISIONS.read_text(encoding='utf-8').splitlines()
    r = [l for l in r if not l.startswith(f'### {K0.AMEND}:')]; d = [l for l in d if f'Register {K0.AMEND}' not in l]
    if kline:
        r.append(f'### {K0.AMEND}: F13-F15 and P1 execution entries (fp_plans.py), PA-15 / REG-001, prelaunch_gate_c10_k.py')
        d.append(f'| D-99 | x | Register {K0.AMEND}: F13-F15, P1, prelaunch_gate_c10_k.py | x | x | IN FORCE |')
    r = [l for l in r if not l.startswith('### A62') and not l.startswith('### A63')]; d = [l for l in d if 'Register A62' not in l and 'Register A63' not in l]
    r.append('### A63: S7 resume after the interrupted launch run_0205: one --retry S7-01, prelaunch_gate_c10_j.py v4')
    d.append('| D-97 | x | Register A63: run_0205 interrupted; --retry S7-01; prelaunch_gate_c10_j.py | x | x | IN FORCE |')
    r.append('### A62: S7, F13-F15 and P1 resume: no end-by window while the user is online; prelaunch_gate_c10_j.py v3, prelaunch_gate_c10_k.py v2')
    d.append('| D-98 | x | Register A62: S7, F13-F15, P1; prelaunch_gate_c10_j.py v3, prelaunch_gate_c10_k.py v2 | x | x | IN FORCE |')
    reg.write_text('\n'.join(r) + '\n', encoding='utf-8'); dec.write_text('\n'.join(d) + '\n', encoding='utf-8'); return reg, dec


def rows_for(rec, spec, start):
    out = []
    for k, (i, done) in enumerate(spec):
        rid = f'run_{start + k:04d}'; e = rec['entries'][i]; pin = rec['dry_build'][i]
        note = f'STARTED model={MODEL}' if e.get('mode') != 'output' else 'STARTED output prediction'
        out.append({'run_id': rid, 'label': e['label'], 'deck_sha256': pin['deck_sha256'], 'model_sha256': pin['model_sha256'], 'notes': note})
        if done: out.append({'run_id': rid, 'label': e['label'], 'exit_code': '0', 'notes': 'synthetic finish'})
    return out


def index(tag, j_done=24, k_spec=(), extra=()):
    TMP.mkdir(exist_ok=True); p = TMP / f'idx_{tag}.csv'
    with p.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
        for r in REAL:
            started = r['notes'].startswith('STARTED')
            w.writerow({'run_id': r['run_id'], 'label': r['label'], 'deck_sha256': r['deck_sha256'], 'model_sha256': r['model_sha256'], 'exit_code': r['exit_code'],
                        'notes': (f'STARTED model={MODEL}' if f'model={MODEL}' in r['notes'].split() else 'STARTED') if started else 'synthetic finish'})
        jr = rows_for(JREC, [(i, True) for i in JORDER[:19]], 182)   # the real sequence: run_0182..run_0200
        e21 = JREC['entries']['S6-21']; p21 = JREC['dry_build']['S6-21']
        jr.append({'run_id': 'run_0201', 'label': e21['label'], 'deck_sha256': p21['deck_sha256'], 'model_sha256': p21['model_sha256'], 'notes': f'STARTED model={MODEL}'})   # interrupted (A61)
        jr += rows_for(JREC, [(i, True) for i in JORDER[19:22]], 202)   # the S6-21 retry, S6-14, S6-11 (run_0202..run_0204)
        e71 = JREC['entries']['S7-01']; p71 = JREC['dry_build']['S7-01']
        jr.append({'run_id': 'run_0205', 'label': e71['label'], 'deck_sha256': p71['deck_sha256'], 'model_sha256': p71['model_sha256'], 'notes': f'STARTED model={MODEL}'})   # interrupted (A63)
        jr += rows_for(JREC, [(i, True) for i in JORDER[22:j_done]], 206)   # the S7-01 retry, S7-02
        kr = rows_for(KREC, list(k_spec), 184 + j_done)
        for row in jr + kr + list(extra): w.writerow({k: row.get(k, '') for k in FIELDS})
    return p


def case(name, want, idx, reg_dec, procs=(), patch=None, clock=datetime(2026, 10, 16, 6, 0, tzinfo=timezone.utc), git=(True, 'synthetic HEAD'),
         reg=(True, 'synthetic'), tag=(True, 'synthetic'), argv=('--check',)):
    k = load(HERE / 'prelaunch_gate_c10_k.py', 'gk_case')
    J = load(k.J_GATE, 'gj_for_k'); mods, why = J.chain(); I, H, G2, G, FG, DE, C = mods
    C.list_processes = lambda: list(procs); C.INDEX = idx; C.REGISTER, C.DECISIONS = reg_dec
    I.committed_in_git = lambda relp: git; k.now = lambda: clock; k.reg_ok = lambda seal: reg; k.tag_ok = lambda: tag
    if patch: patch(k)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): rc = k.run(J, *mods, C.Gate(), list(argv))
    out = buf.getvalue(); expect(name, rc, want)
    if rc != want: print(out)
    return out


def main():
    cwd = os.getcwd()
    try:
        L = logs('ok'); F3 = [(i, True) for i in KORDER[:3]]
        out = case('S6 / S7 complete -> 0, F13-F15 single plan __S3-26 (A62), 1 entry from run_0208', 0, index('f', 24), L)
        expect('  command names campaign_C10_F13_F15__S3-26, run_0208', out.rstrip().endswith('config/campaign_C10_F13_F15__S3-26.json') and 'run_0208' in out and 'these 1 entry' in out, True)
        out = case('S3-26 done -> 0, __S3-24', 0, index('f2', 24, [('S3-26', True)]), L)
        expect('  command names __S3-24', out.rstrip().endswith('config/campaign_C10_F13_F15__S3-24.json'), True)
        out = case('S6 / S7 incomplete (S7-02 missing) -> 4', 4, index('inc', 23), L)
        expect('  names register order', 'register order' in out, True)
        case('K amendment not logged -> 1', 1, index('nl', 24), logs('nl', kline=False))
        out = case('F done -> 0, P1-2p0', 0, index('p', 24, F3), L)
        expect('  command names P1 2.0 nm', out.rstrip().endswith('config/campaign_C10_P1_2p0.json'), True)
        case('P1 next but REG-001 missing -> 1', 1, index('r', 24, F3), L, reg=(False, 'missing'))
        case('P1 next but no model tag -> 1', 1, index('t', 24, F3), L, tag=(False, 'missing'))
        out = case('F + P1-2p0 + P1-6p3 done -> 0, P1-13p2', 0, index('p13', 24, [(i, True) for i in KORDER[:5]]), L)
        expect('  command names P1 13.2 nm', out.rstrip().endswith('config/campaign_C10_P1_13p2.json'), True)
        out = case('all done -> 4', 4, index('all', 24, [(i, True) for i in KORDER]), L)
        expect('  names p1_floor', 'p1_floor.py' in out, True)
        case('a K run started without a finish row -> 3', 3, index('u', 24, [('S3-26', False)]), L)
        case('out of order (S3-24 first) -> 1', 1, index('o', 24, [('S3-24', True)]), L)
        case('K run before S6 / S7 complete -> 1', 1, index('early', 23, [('S3-26', True)]), L)
        case('STARTED-row deck differs -> 1', 1, index('dk', 24, extra=[{'run_id': 'run_0208', 'label': 'c10_s3_26_2p0', 'deck_sha256': '0' * 64,
                                                                          'model_sha256': KREC['dry_build']['S3-26']['model_sha256'], 'notes': f'STARTED model={MODEL}'}]), L)
        case('unknown label above run_0181 -> 1', 1, index('unk', 24, extra=[{'run_id': 'run_0208', 'label': 'c10_s3_17_2p0', 'notes': f'STARTED model={MODEL}'}]), L)
        case('no end-by window (A62): F plan at 23:00Z -> 0', 0, index('c0', 24), L, clock=datetime(2026, 10, 17, 23, 0, tzinfo=timezone.utc))
        case('a Silvaco process -> 1', 1, index('sil', 24), L, procs=[(4242, 'deckbuild.exe', 'deckbuild')])
        case('an unreadable python command line -> 1', 1, index('unv', 24), L, procs=[(4244, 'python3.13.exe', None)])
        case('generator pin differs -> 1', 1, index('gp', 24), L, patch=lambda m: setattr(m, 'GEN_SHA', '0' * 64))
        case('record seal differs -> 1', 1, index('rs', 24), L, patch=lambda m: setattr(m, 'RECORD_SEAL', '0' * 64))
        case('not committed -> 1', 1, index('nc', 24), L, git=(False, 'not in HEAD'))
        km = load(HERE / 'prelaunch_gate_c10_k.py', 'gk_pin'); km.J_GATE_SHA = '0' * 64
        with contextlib.redirect_stdout(io.StringIO()): expect('J gate pin differs -> main exits 1', km.main(['--check']), 1)
        expect('unit: constants', (K0.TAG, KORDER, K0.SINGLE_BATCHES_K),
               ('model-c10-s4c-frozen-20261016', ['S3-26', 'S3-24', 'S3-25', 'P1-2p0', 'P1-6p3', 'P1-13p2'], ('campaign_C10_F13_F15',)))
    finally:
        os.chdir(cwd); shutil.rmtree(TMP, ignore_errors=True)
    n = sum(results); print(f'{n}/{len(results)} passed'); return 0 if n == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
