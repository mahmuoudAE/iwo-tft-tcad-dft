"""Tests of prelaunch_gate_c10_g2.py (register A51; NO launch; no repo file written except the temporary ./test_tmp_c10_g2, removed at the end).

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"; & <venv python> -I -B analysis_2026-10-10_campaign/test_prelaunch_gate_c10_g2.py
In-process cases import the gate and give it the pinned A50 (G), F, D/E and C10 gate modules with patched inputs: synthetic register / decision
log, synthetic RUN_INDEX (run_id/label of the real rows up to run_0077 only, plus synthetic STARTED rows of the reused run_0061/0068/0069 carrying
the pinned PA-12 hashes; synthetic S1-06R/DIAG rows run_0078..run_0096, D/E rows run_0097..run_0101, stage F rows run_0102..run_0113, S4a rows
run_0114..run_0149 with finish rows, the interrupted run_0150 (STARTED row only) and the cases' rows above: no real row content beyond run_id and
label is copied), a synthetic sealed-run inventory and a fake process list.
"""
import contextlib, csv, importlib.util, io, json, os, shutil, sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent; GATE2 = HERE / 'prelaunch_gate_c10_g2.py'; GG = HERE / 'prelaunch_gate_c10_g.py'
FGF = HERE / 'prelaunch_gate_c10_f.py'; DEG = HERE / 'prelaunch_gate_c10_de.py'; C10 = HERE / 'prelaunch_gate_c10.py'
TMP = HERE / 'test_tmp_c10_g2'; PKG = HERE.parent
FIELDS = ['run_id', 'timestamp_utc', 'thickness_nm', 'label', 'deck_sha256', 'model_sha256', 'command', 'simulator', 'exit_code', 'converged',
          'elapsed_s', 'output_dir', 'notes']
MODEL = 'config/iwo_material_model_v3.yaml'
results = []


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


G0 = load(GG, 'gg_constants'); F0 = load(FGF, 'gf_constants'); D0 = load(DEG, 'gde_constants'); C0 = load(C10, 'c10_constants')
O = G0.ORDER; I_INT = O.index('S4A-14-2p0')


def expect(name, got, want):
    ok = got == want; results.append(ok); print(f"{'ok  ' if ok else 'FAIL'} {name}: {got}", flush=True)


def logs(tag, a51=True, a50=True, draft=False, row_words=True):
    TMP.mkdir(exist_ok=True); reg, dec = TMP / f'reg_{tag}.md', TMP / f'dec_{tag}.md'
    h = ['### A48: stage F: PA-8 ...',
         '### A49: stage G1 prerequisites: 0-launch S3 decision before S4a ... (PA-8 adoption ...); S4a forms N/T/I/TI ... (PA-12); PA-16 ...; PA-20 ...']
    if a50: h.append('### A50: S4a execution entries of form N: S4A-02 .. S4A-15, route plans, prelaunch_gate_c10_g.py')
    if a51: h.append('### A51: S4a resume after the interrupted launch run_0150: one infrastructure retry of S4A-14-2p0 (--retry S4A-14-2p0), '
                     'prelaunch_gate_c10_g2.py' + (' (draft)' if draft else ''))
    r = ['| D-68 | x | A48 | x | x | IN FORCE |', '| D-69 | x | Register A49: s3_decision_a49.py, PA-8 | x | x | IN FORCE |']
    if a50: r.append('| D-70 | x | Register A50: form N, campaign_C10_S4a_b1, prelaunch_gate_c10_g.py | x | x | IN FORCE |')
    if a51: r.append('| D-71 | x | Register A51: run_0150 interrupted; ' + ('--retry S4A-14-2p0; ' if row_words else '') + 'prelaunch_gate_c10_g2.py | x | x | IN FORCE |')
    reg.write_text('\n'.join(h) + '\n'); dec.write_text('\n'.join(r) + '\n'); return reg, dec


def fin(rid, lab): return {'run_id': rid, 'label': lab, 'exit_code': '0', 'notes': 'synthetic finish'}


def prev_rows():
    rows = []
    for k, e in enumerate(C0.LAUNCH_ORDER):
        rid = f'run_{78 + k:04d}'; rows += [{'run_id': rid, 'label': C0.LABEL[e], 'notes': 'STARTED synthetic'}, fin(rid, C0.LABEL[e])]
    for k, e in enumerate(D0.ORDER):
        rid = f'run_{97 + k:04d}'; rows += [{'run_id': rid, 'label': D0.LABEL[e], 'notes': 'STARTED synthetic'}, fin(rid, D0.LABEL[e])]
    for k, e in enumerate(F0.ORDER):
        rid = f'run_{102 + k:04d}'; rows += [{'run_id': rid, 'label': F0.LABEL[e], 'notes': 'STARTED synthetic'}, fin(rid, F0.LABEL[e])]
    return rows


def s_row(rid, k, finish=True, deck=None):
    lab = G0.LABEL[k]; s = {'run_id': rid, 'label': lab, 'deck_sha256': deck or G0.DECK[k], 'model_sha256': G0.MATERIAL[k], 'notes': f'STARTED model={MODEL}'}
    return [s] + ([fin(rid, lab)] if finish else [])


def seq(keys, start, finish_last=True):
    out = []
    for i, k in enumerate(keys): out += s_row(f'run_{start + i:04d}', k, finish=finish_last or i < len(keys) - 1)
    return out


def base(int_finish=False, int_deck=None, last_unfinished=False):
    """S4A-02-2p0 .. S4A-13-13p2 = run_0114..run_0149 finished, run_0150 = S4A-14-2p0 STARTED only (the interrupted launch)"""
    return seq(O[:I_INT], 114, finish_last=not last_unfinished) + s_row('run_0150', 'S4A-14-2p0', finish=int_finish, deck=int_deck)


def index(tag, extra, inv_skip=()):
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
        for row in prev_rows() + extra: w.writerow({k: row.get(k, '') for k in FIELDS})
    inv = {'runs': []}; of = {v: k for k, v in G0.LABEL.items()}
    for row in extra:
        if row.get('notes', '').startswith('STARTED') and row['label'] in of and row['run_id'] not in inv_skip:
            k = of[row['label']]
            inv['runs'].append({'run_id': row['run_id'], 'label': row['label'], 'entry': k, 'model_file': MODEL, 'deck_sha256': G0.DECK[k],
                                'model_sha256': G0.MATERIAL[k], 'reason': 'synthetic'})
    ip = TMP / f'inv_{tag}.json'; ip.write_text(json.dumps(inv)); return p, ip


def case(name, want, idx_inv, reg_dec, procs=(), patch=None, env=None):
    g2 = load(GATE2, 'gg2_under_test'); G = load(GG, 'gg_under_test'); Fm = load(FGF, 'gf_under_test'); D = load(DEG, 'gde_under_test')
    C = load(C10, 'c10_under_test')
    C.list_processes = lambda: list(procs)
    C.INDEX, C.INVENTORY = idx_inv; C.REGISTER, C.DECISIONS = reg_dec; D.c10_module = lambda: C; Fm.de_module = lambda: D; G.f_module = lambda: Fm
    g2.g_module = lambda: G
    if patch: patch(g2)
    os.chdir(PKG); buf = io.StringIO(); old = dict(os.environ)
    if env: os.environ.update(env)
    try:
        with contextlib.redirect_stdout(buf): rc = g2.main(['--check'])
    finally: os.environ.clear(); os.environ.update(old)
    out = buf.getvalue(); [print('       ' + l) for l in out.splitlines() if l.startswith(('GATE PASSED', 'NOTHING', 'GATE STOP', '[FAIL]', '[STOP]', 'run_campaign', '&'))]
    expect(name, rc, want); return out


def main():
    R = 'S4A-14-2p0'
    try:
        L = logs('ok')
        out = case('interrupted run_0150, A51 logged -> 0, b3 with --retry, 6 entries', 0, index('int', base()), L)
        expect('  command carries --retry S4A-14-2p0, first run id run_0151, 6 entries',
               'scripts/run_campaign.py config/campaign_C10_S4a_b3.json --retry S4A-14-2p0' in out and 'first run id run_0151' in out
               and 'these 6 entries' in out and 'campaign_C10_S4a_b3.json: S4A-14-2p0' in out, True)
        case('A51 not logged -> 1', 1, index('n51', base()), logs('n51', a51=False))
        case('A51 draft heading -> 1', 1, index('d51', base()), logs('d51', draft=True))
        case('A51 row without --retry S4A-14-2p0 -> 1', 1, index('r51', base()), logs('r51', row_words=False))
        case('A50 not logged -> 1', 1, index('n50', base()), logs('n50', a50=False))
        case('run_0150 missing from the inventory -> 1', 1, index('inv', base(), inv_skip=('run_0150',)), L)
        case('run_0150 has a finish row -> 1', 1, index('ifin', base(int_finish=True)), L)
        case('run_0150 STARTED deck differs -> 1', 1, index('ideck', base(int_deck='0' * 64)), L)
        case('no run_0150 (batch 3 not interrupted) -> 1', 1, index('noint', seq(O[:I_INT], 114)), L)
        out = case('retry run_0151 finished -> 0, no --retry, 5 entries from S4A-14-6p3', 0, index('rdone', base() + s_row('run_0151', R)), L)
        expect('  command without --retry, first run id run_0152',
               out.rstrip().endswith('scripts/run_campaign.py config/campaign_C10_S4a_b3.json') and '--retry S4A' not in out.splitlines()[-1]
               and 'first run id run_0152' in out and 'these 5 entries' in out and 'campaign_C10_S4a_b3.json: S4A-14-6p3' in out, True)
        case('retry run_0151 started, no finish row -> 3', 3, index('runf', base() + s_row('run_0151', R, finish=False)), L)
        case('retry done, S4A-14-6p3 unfinished -> 3', 3, index('nunf', base() + s_row('run_0151', R) + s_row('run_0152', 'S4A-14-6p3', finish=False)), L)
        out = case('retry + S4A-14-6p3 done -> 0, 4 entries', 0, index('r2', base() + seq([R, 'S4A-14-6p3'], 151)), L)
        expect('  next S4A-14-13p2, 4 entries, run_0153', 'S4A-14-13p2' in out and 'these 4 entries' in out and 'run_0153' in out, True)
        case('all done (retry + 5) -> 4', 4, index('all', base() + seq(O[I_INT:], 151)), L)
        case('two retries of S4A-14-2p0 -> 1', 1, index('two', base() + s_row('run_0151', R) + s_row('run_0152', R)), L)
        case('S4A-14-6p3 before the retry (no retry) -> 1', 1, index('skip', base() + s_row('run_0151', 'S4A-14-6p3')), L)
        case('S4A-14-6p3 then the retry -> 1', 1, index('swap', base() + s_row('run_0151', 'S4A-14-6p3') + s_row('run_0152', R)), L)
        case('another unfinished run (run_0149) besides run_0150 -> 3', 3, index('u149', base(last_unfinished=True)), L)
        case('retry not inventoried -> 1', 1, index('rinv', base() + s_row('run_0151', R), inv_skip=('run_0151',)), L)
        case('retry STARTED deck differs -> 1', 1, index('rdeck', base() + s_row('run_0151', R, deck='1' * 64)), L)
        case('unknown label above run_0077 -> 1', 1, index('unk', base() + [{'run_id': 'run_0151', 'label': 'c10_s4b_01_2p0_2p0', 'notes': 'STARTED'}]), L)
        case('Silvaco process running -> 1', 1, index('proc', base()), L, procs=[(4242, 'deckbuild.exe', 'deckbuild.exe -run x')])
        case('runner python running -> 1', 1, index('rpy', base()), L, procs=[(4243, 'python.exe', 'python scripts/run_campaign.py config/x.json')])
        case('A51 fit violated (need 105: 90 + 6 + 105 > 200) -> 1', 1, index('fit', base()), L, patch=lambda m: setattr(m, 'NEED_AFTER_S4A', 105))
        case('A51 fit at the limit (need 104: 90 + 6 + 104 = 200) -> 0', 0, index('fit2', base()), L, patch=lambda m: setattr(m, 'NEED_AFTER_S4A', 104))
        case('IWO_MODEL_FILE wrong -> 1', 1, index('env', base()), L, env={'IWO_MODEL_FILE': 'config/iwo_material_model_v2.yaml'})
        case('A50 gate pin differs -> 1', 1, index('pin', base()), L, patch=lambda m: setattr(m, 'G_GATE_SHA', '0' * 64))
        expect('unit: interrupted run and retry entry', (I_INT, O[I_INT], O[I_INT - 1], len(O)), (36, 'S4A-14-2p0', 'S4A-13-13p2', 42))
        g2 = load(GATE2, 'gg2_unit')
        expect('unit: constants', (g2.INTERRUPTED, g2.RETRY_K, g2.NEED_AFTER_S4A, g2.G_GATE_SHA[:8]), ('run_0150', 'S4A-14-2p0', 100, '75a22c4d'))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print(f'{sum(results)}/{len(results)} passed'); return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main())
