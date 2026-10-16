"""Tests of prelaunch_gate_c10_j.py (register A58; NO launch; no repo file written except the temporary ./test_tmp_c10_j, removed at the end).

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"; & <venv python> -I -B analysis_2026-10-10_campaign/test_prelaunch_gate_c10_j.py
In-process cases load the gate chain (pinned) and patch: a synthetic register / decision log (the real files' lines plus, per case, synthetic A58
lines), a synthetic RUN_INDEX (the state columns run_id, label, exit_code, deck_sha256, model_sha256 of the real rows, notes reduced to
"STARTED model=..." or "synthetic finish"; plus the cases' synthetic S6 / S7 rows), a fake process list, a stubbed git check and a fixed clock.
"""
import contextlib, csv, importlib.util, io, json, os, shutil, sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent; PKG = HERE.parent; TMP = HERE / 'test_tmp_c10_j'
FIELDS = ['run_id', 'timestamp_utc', 'thickness_nm', 'label', 'deck_sha256', 'model_sha256', 'command', 'simulator', 'exit_code', 'converged',
          'elapsed_s', 'output_dir', 'notes']
MODEL = 'config/iwo_material_model_v3.yaml'
results = []


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def expect(name, got, want):
    ok = got == want; results.append(ok); print(f"{'ok  ' if ok else 'FAIL'} {name}: {got}", flush=True)


J0 = load(HERE / 'prelaunch_gate_c10_j.py', 'gj_constants')
REC = json.loads((PKG / J0.RECORD_REL).read_text())
ORDER = [i for _, ids in REC['batches'] for i in ids]
REAL = [r for r in csv.DictReader((PKG / 'results' / 'RUN_INDEX.csv').open(newline=''))]


def logs(tag, a58=True, draft=False):
    TMP.mkdir(exist_ok=True); reg, dec = TMP / f'reg_{tag}.md', TMP / f'dec_{tag}.md'
    C = J0.chain()[0][-1]
    r = C.REGISTER.read_text(encoding='utf-8').splitlines(); d = C.DECISIONS.read_text(encoding='utf-8').splitlines()
    r = [l for l in r if not l.startswith('### A58')]; d = [l for l in d if 'A58' not in l]
    if a58:
        r.append('### A58: S6 / S7 execution entries (s6s7_plans.py), PA-19 v3 allocation, prelaunch_gate_c10_j.py' + (' (draft)' if draft else ''))
        d.append('| D-85 | x | Register A58: S6, S7, s6s7_plans.py, prelaunch_gate_c10_j.py | x | x | IN FORCE |')
    reg.write_text('\n'.join(r) + '\n', encoding='utf-8'); dec.write_text('\n'.join(d) + '\n', encoding='utf-8'); return reg, dec


def a58_rows(spec):
    """spec: [(id, finished, deck_ok)] in launch order, run ids from run_0182"""
    out = []
    for k, (i, done, ok) in enumerate(spec):
        rid = f'run_{182 + k:04d}'; e = REC['entries'][i]; pin = REC['dry_build'][i]
        out.append({'run_id': rid, 'label': e['label'], 'deck_sha256': pin['deck_sha256'] if ok else '0' * 64, 'model_sha256': pin['model_sha256'],
                    'notes': f'STARTED model={MODEL}'})
        if done: out.append({'run_id': rid, 'label': e['label'], 'exit_code': '0', 'notes': 'synthetic finish'})
    return out


def index(tag, extra, finish_0160=False):
    TMP.mkdir(exist_ok=True); p = TMP / f'idx_{tag}.csv'
    with p.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
        for r in REAL:
            if int(r['run_id'][4:]) > 181: continue
            started = r['notes'].startswith('STARTED')
            w.writerow({'run_id': r['run_id'], 'label': r['label'], 'deck_sha256': r['deck_sha256'], 'model_sha256': r['model_sha256'],
                        'exit_code': r['exit_code'], 'notes': (f'STARTED model={MODEL}' if f'model={MODEL}' in r['notes'].split() else 'STARTED') if started else 'synthetic finish'})
        if finish_0160: w.writerow({'run_id': 'run_0160', 'label': 'c10_s4d_2p0_2p0', 'exit_code': '0', 'notes': 'synthetic finish'})
        for row in extra: w.writerow({k: row.get(k, '') for k in FIELDS})
    return p


def case(name, want, idx, reg_dec, procs=(), patch=None, clock=datetime(2026, 10, 16, 2, 0, tzinfo=timezone.utc), git=(True, 'synthetic HEAD'), argv=('--check',)):
    j = load(HERE / 'prelaunch_gate_c10_j.py', 'gj_case'); mods, why = j.chain()
    I, H, G2, G, FG, DE, C = mods
    C.list_processes = lambda: list(procs); C.INDEX = idx; C.REGISTER, C.DECISIONS = reg_dec
    I.committed_in_git = lambda relp: git; j.now = lambda: clock
    if patch: patch(j)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): rc = j.run(*mods, C.Gate(), list(argv))
    out = buf.getvalue(); expect(name, rc, want)
    if rc != want: print(out)
    return out


def main():
    cwd = os.getcwd()
    try:
        L = logs('ok')
        out = case('real state, A58 logged -> 0, campaign_C10_S6_b1, 3 entries from run_0182', 0, index('ok', []), L)
        expect('  command names b1, first run id run_0182, 3 entries',
               out.rstrip().endswith('scripts/run_campaign.py config/campaign_C10_S6_b1.json') and 'first run id run_0182' in out and 'these 3 entries' in out, True)
        case('A58 not logged -> 1', 1, index('n58', []), logs('n58', a58=False))
        case('A58 heading draft -> 1', 1, index('d58', []), logs('d58', draft=True))
        case('S6-01 started, no finish row -> 3', 3, index('u', a58_rows([('S6-01', False, True)])), L)
        out = case('S6-01, S6-02 done -> 0, b1, 1 entry (S6-03) from run_0184', 0, index('p', a58_rows([('S6-01', True, True), ('S6-02', True, True)])), L)
        expect('  S6-03 next', 'S6-03' in out and 'run_0184' in out and 'these 1 entry' in out, True)
        out = case('b1 done -> 0, b2', 0, index('b2', a58_rows([(i, True, True) for i in ORDER[:3]])), L)
        expect('  command names b2', out.rstrip().endswith('config/campaign_C10_S6_b2.json'), True)
        case('out of order (S6-02 first) -> 1', 1, index('o', a58_rows([('S6-02', True, True)])), L)
        case('STARTED-row deck differs from the record -> 1', 1, index('dk', a58_rows([('S6-01', True, False)])), L)
        case('unknown label above run_0181 -> 1', 1, index('unk', [{'run_id': 'run_0182', 'label': 'c10_s6_16_2p0', 'notes': f'STARTED model={MODEL}'}]), L)
        case('a second run id for one label -> 1', 1, index('two', a58_rows([('S6-01', True, True)]) +
                                                            [dict(r, run_id='run_0183') for r in a58_rows([('S6-01', True, True)])]), L)
        out = case('all A58 done -> 4', 4, index('all', a58_rows([(i, True, True) for i in ORDER])), L)
        expect('  names the read-out', 'A58 read-out' in out, True)
        out = case('cutoff: 09:00Z, b1 (1600 + 2000 + 360 s) -> 4', 4, index('c1', []), L, clock=datetime(2026, 10, 16, 9, 0, tzinfo=timezone.utc))
        expect('  names the cutoff', 'cutoff' in out, True)
        case('cutoff: 08:50Z, b1 latest start 09:56Z -> 0', 0, index('c2', []), L, clock=datetime(2026, 10, 16, 8, 50, tzinfo=timezone.utc))
        case('cutoff: after 10:00Z -> 4', 4, index('c3', []), L, clock=datetime(2026, 10, 16, 10, 1, tzinfo=timezone.utc))
        out = case('S7 last: everything but S7 done, 09:00Z: S7 latest start 09:54Z -> 0', 0, index('s7', a58_rows([(i, True, True) for i in ORDER[:-2]])), L,
                   clock=datetime(2026, 10, 16, 9, 0, tzinfo=timezone.utc))
        expect('  command names S7', out.rstrip().endswith('config/campaign_C10_S7.json'), True)
        case('run_0160 gets a finish row (not the registered interruption) -> 1', 1, index('f160', [], finish_0160=True), L)
        case('a Silvaco process -> 1', 1, index('sil', []), L, procs=[(4242, 'deckbuild.exe', 'deckbuild')])
        case('a runner python -> 1', 1, index('run', []), L, procs=[(4243, 'python.exe', 'python scripts/run_campaign.py config/x.json')])
        case('an unreadable python command line -> 1', 1, index('unv', []), L, procs=[(4244, 'python3.13.exe', None)])
        case('fit violated (other never-cut 56: 121 + 24 + 56 = 201) -> 1', 1, index('fit', []), L, patch=lambda m: setattr(m, 'OTHER_NEVER_CUT', 56))
        case('fit at the limit (55: 200) -> 0', 0, index('fit2', []), L, patch=lambda m: setattr(m, 'OTHER_NEVER_CUT', 55))
        case('generator pin differs -> 1', 1, index('gp', []), L, patch=lambda m: setattr(m, 'GEN_SHA', '0' * 64))
        case('record seal differs -> 1', 1, index('rs', []), L, patch=lambda m: setattr(m, 'RECORD_SEAL', '0' * 64))
        case('record not committed -> 1', 1, index('nc', []), L, git=(False, 'not in HEAD'))
        jm = load(HERE / 'prelaunch_gate_c10_j.py', 'gj_pin'); jm.I_GATE_SHA = '0' * 64
        with contextlib.redirect_stdout(io.StringIO()): expect('I gate pin differs -> main exits 1', jm.main(['--check']), 1)
        expect('unit: constants', (J0.LAST_S5, J0.INTERRUPTED, J0.OTHER_NEVER_CUT, J0.CUTOFF.isoformat(), J0.I_GATE_SHA[:8]),
               ('run_0181', ('run_0150', 'run_0160'), 32, '2026-10-16T10:00:00+00:00', '2f4d74d8'))
    finally:
        os.chdir(cwd); shutil.rmtree(TMP, ignore_errors=True)
    n = sum(results); print(f'{n}/{len(results)} passed'); return 0 if n == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
