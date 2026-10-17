"""Tests of prelaunch_gate_c10_j.py (register A59; NO launch; no repo file written except the temporary ./test_tmp_c10_j, removed at the end).

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"; & <venv python> -I -B analysis_2026-10-10_campaign/test_prelaunch_gate_c10_j.py
In-process cases load the gate chain (pinned) and patch: a synthetic register / decision log (the real files' lines plus, per case, synthetic A59
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


def logs(tag, a58=True, draft=False, a61=True):
    TMP.mkdir(exist_ok=True); reg, dec = TMP / f'reg_{tag}.md', TMP / f'dec_{tag}.md'
    C = J0.chain()[0][-1]
    r = C.REGISTER.read_text(encoding='utf-8').splitlines(); d = C.DECISIONS.read_text(encoding='utf-8').splitlines()
    r = [l for l in r if not l.startswith('### A59')]; d = [l for l in d if 'A59' not in l]
    if a58:
        r.append('### A59: S6 / S7 execution entries (s6s7_plans.py), PA-19 v3 allocation, prelaunch_gate_c10_j.py' + (' (draft)' if draft else ''))
        d.append('| D-86 | x | Register A59: S6, S7, s6s7_plans.py, prelaunch_gate_c10_j.py | x | x | IN FORCE |')
    r = [l for l in r if not l.startswith('### A61')]; d = [l for l in d if 'Register A61' not in l]
    if a61:
        r.append('### A61: S6 resume after the interrupted launch run_0201: one --retry S6-21, prelaunch_gate_c10_j.py v2, window rule')
        d.append('| D-98 | x | Register A61: run_0201 interrupted; --retry S6-21; prelaunch_gate_c10_j.py | x | x | IN FORCE |')
    reg.write_text('\n'.join(r) + '\n', encoding='utf-8'); dec.write_text('\n'.join(d) + '\n', encoding='utf-8'); return reg, dec


def a58_rows(spec, start=182):
    """spec: [(id, finished, deck_ok)] in launch order, run ids from run_0182"""
    out = []
    for k, (i, done, ok) in enumerate(spec):
        rid = f'run_{start + k:04d}'; e = REC['entries'][i]; pin = REC['dry_build'][i]
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
    def base(extra=(), done19=19):   # the real sequence: S6 order[:19] finished (run_0182..run_0200), run_0201 S6-21 STARTED only
        return a58_rows([(i, True, True) for i in ORDER[:done19]]) + a58_rows([('S6-21', False, True)], start=182 + done19) + list(extra)
    T = lambda h, m: datetime(2026, 10, 17, h, m, tzinfo=timezone.utc)
    try:
        L = logs('ok')
        expect('  real order: ORDER[19] is S6-21', ORDER[19], 'S6-21')
        out = case('run_0201 interrupted, A61 logged, 00:30Z -> 0, b7r with --retry S6-21, 1 entry from run_0202', 0, index('ok', base()), L, clock=T(0, 30))
        expect('  command: b7r --retry S6-21, run_0202, 1 entry', out.rstrip().endswith('config/campaign_C10_S6_b7r.json --retry S6-21') and 'run_0202' in out and 'these 1 entry' in out, True)
        case('window: 00:44Z (end 00:44 + 900 + 120 s = 01:01Z) -> 4', 4, index('w1', base()), L, clock=T(0, 44))
        case('window: 00:42Z (end 00:59Z) -> 0', 0, index('w0', base()), L, clock=T(0, 42))
        case('A61 not logged -> 1', 1, index('n61', base()), logs('n61', a61=False), clock=T(0, 30))
        case('retry started, no finish row -> 3', 3, index('ru', base(a58_rows([('S6-21', False, True)], start=202))), L, clock=T(0, 30))
        out = case('retry finished -> 0, b7 (S6-14) without --retry', 0, index('rf', base(a58_rows([('S6-21', True, True)], start=202))), L, clock=T(0, 20))
        expect('  command: b7, S6-14, run_0203, 1 entry', out.rstrip().endswith('scripts/run_campaign.py config/campaign_C10_S6_b7.json') and 'S6-14' in out
               and 'run_0203' in out and 'these 1 entry' in out, True)
        case('a third S6-21 run -> 1', 1, index('r3', base(a58_rows([('S6-21', True, True)], start=202) + a58_rows([('S6-21', True, True)], start=203))), L, clock=T(0, 20))
        case('run_0201 gets a finish row -> 1', 1, index('f201', base([{'run_id': 'run_0201', 'label': 'c10_s6_21_6p3', 'exit_code': '0', 'notes': 'synthetic finish'}])), L, clock=T(0, 30))
        case('run_0201 missing (S6-21 never started) -> 1', 1, index('m201', a58_rows([(i, True, True) for i in ORDER[:19]])), L, clock=T(0, 30))
        case('retry deck differs from the record -> 1', 1, index('rd', base(a58_rows([('S6-21', True, False)], start=202))), L, clock=T(0, 20))
        rest = [('S6-21', True, True)] + [(i, True, True) for i in ORDER[20:22]]
        out = case('all S6 done -> 4 (S7: no completed 31.8 nm run, not launchable in the window)', 4, index('s7', base(a58_rows(rest, start=202))), L, clock=T(0, 10))
        expect('  names the window rule', 'A61 window rule' in out, True)
        case('out of order (S6-11 before S6-14 after the retry) -> 1', 1, index('o', base(a58_rows([('S6-21', True, True), ('S6-11', True, True)], start=202))), L, clock=T(0, 10))
        case('unknown label above run_0181 -> 1', 1, index('unk', base([{'run_id': 'run_0202', 'label': 'c10_s6_16_2p0', 'notes': f'STARTED model={MODEL}'}])), L, clock=T(0, 30))
        case('a Silvaco process -> 1', 1, index('sil', base()), L, procs=[(4242, 'deckbuild.exe', 'deckbuild')], clock=T(0, 30))
        case('an unreadable python command line -> 1', 1, index('unv', base()), L, procs=[(4244, 'python3.13.exe', None)], clock=T(0, 30))
        case('fit violated (other never-cut 51: 141 + 0 + ... ) -> 1', 1, index('fit', base()), L, patch=lambda m: setattr(m, 'OTHER_NEVER_CUT', 200), clock=T(0, 30))
        case('generator pin differs -> 1', 1, index('gp', base()), L, patch=lambda m: setattr(m, 'GEN_SHA', '0' * 64), clock=T(0, 30))
        case('record seal differs -> 1', 1, index('rs', base()), L, patch=lambda m: setattr(m, 'RECORD_SEAL', '0' * 64), clock=T(0, 30))
        case('not committed -> 1', 1, index('nc', base()), L, git=(False, 'not in HEAD'), clock=T(0, 30))
        jm = load(HERE / 'prelaunch_gate_c10_j.py', 'gj_pin'); jm.I_GATE_SHA = '0' * 64
        with contextlib.redirect_stdout(io.StringIO()): expect('I gate pin differs -> main exits 1', jm.main(['--check']), 1)
        expect('unit: constants', (J0.LAST_S5, J0.INTERRUPTED, J0.RETRY_J, J0.WINDOW_END.isoformat(), J0.EXPECTED_S, J0.I_GATE_SHA[:8]),
               ('run_0181', ('run_0150', 'run_0160', 'run_0201'), 'S6-21', '2026-10-17T01:00:00+00:00', {2.0: 510, 6.3: 900, 13.2: 1290}, '2f4d74d8'))
    finally:
        os.chdir(cwd); shutil.rmtree(TMP, ignore_errors=True)
    n = sum(results); print(f'{n}/{len(results)} passed'); return 0 if n == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
