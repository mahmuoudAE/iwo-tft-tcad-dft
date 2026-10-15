"""Tests of prelaunch_gate_c10_g.py (register A50; NO launch; no repo file written except the temporary ./test_tmp_c10_g, removed at the end).

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"; & <venv python> -I -B analysis_2026-10-10_campaign/test_prelaunch_gate_c10_g.py
In-process cases import the gate and give it the pinned F, D/E and C10 gate modules with patched inputs: synthetic register / decision log,
synthetic RUN_INDEX (run_id/label of the real rows up to run_0077 only, plus synthetic STARTED rows of the reused run_0061/0068/0069 carrying the
pinned PA-12 hashes; synthetic S1-06R/DIAG rows run_0078..run_0096, D/E rows run_0097..run_0101, stage F rows run_0102..run_0113 and S4a rows
above: no real row content beyond run_id and label is copied), a synthetic sealed-run inventory and a fake process list.
"""
import contextlib, csv, importlib.util, io, json, os, shutil, sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent; GATE = HERE / 'prelaunch_gate_c10_g.py'; FGF = HERE / 'prelaunch_gate_c10_f.py'
DEG = HERE / 'prelaunch_gate_c10_de.py'; C10 = HERE / 'prelaunch_gate_c10.py'
TMP = HERE / 'test_tmp_c10_g'; PKG = HERE.parent
FIELDS = ['run_id', 'timestamp_utc', 'thickness_nm', 'label', 'deck_sha256', 'model_sha256', 'command', 'simulator', 'exit_code', 'converged',
          'elapsed_s', 'output_dir', 'notes']
MODEL = 'config/iwo_material_model_v3.yaml'
results = []


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


G0 = load(GATE, 'gg_constants'); F0 = load(FGF, 'gf_constants'); D0 = load(DEG, 'gde_constants'); C0 = load(C10, 'c10_constants')


def expect(name, got, want):
    ok = got == want; results.append(ok); print(f"{'ok  ' if ok else 'FAIL'} {name}: {got}", flush=True)


def logs(tag, a50=True, a49=True, draft=False):
    TMP.mkdir(exist_ok=True); reg, dec = TMP / f'reg_{tag}.md', TMP / f'dec_{tag}.md'
    h = ['### A48: stage F: PA-8 ...']
    if a49: h.append('### A49: stage G1 prerequisites: 0-launch S3 decision before S4a ... (PA-8 adoption ...); S4a forms N/T/I/TI ... (PA-12); PA-16 ...; PA-20 ...')
    if a50: h.append('### A50: S4a execution entries of form N: S4A-02 .. S4A-15, route plans, prelaunch_gate_c10_g.py' + (' (draft)' if draft else ''))
    r = ['| D-68 | x | A48 | x | x | IN FORCE |']
    if a49: r.append('| D-69 | x | Register A49: s3_decision_a49.py, PA-8 | x | x | IN FORCE |')
    if a50: r.append('| D-70 | x | Register A50: form N, campaign_C10_S4a_b1, prelaunch_gate_c10_g.py | x | x | IN FORCE |')
    reg.write_text('\n'.join(h) + '\n'); dec.write_text('\n'.join(r) + '\n'); return reg, dec


def fin(rid, lab): return {'run_id': rid, 'label': lab, 'exit_code': '0', 'notes': 'synthetic finish'}


def prev_rows(drop_last_f=False):
    rows = []
    for k, e in enumerate(C0.LAUNCH_ORDER):
        rid = f'run_{78 + k:04d}'; rows += [{'run_id': rid, 'label': C0.LABEL[e], 'notes': 'STARTED synthetic'}, fin(rid, C0.LABEL[e])]
    for k, e in enumerate(D0.ORDER):
        rid = f'run_{97 + k:04d}'; rows += [{'run_id': rid, 'label': D0.LABEL[e], 'notes': 'STARTED synthetic'}, fin(rid, D0.LABEL[e])]
    for k, e in enumerate(F0.ORDER):
        rid = f'run_{102 + k:04d}'; rows += [{'run_id': rid, 'label': F0.LABEL[e], 'notes': 'STARTED synthetic'}, fin(rid, F0.LABEL[e])]
    return rows[:-1] if drop_last_f else rows


def s_row(rid, k, finish=True, deck=None):
    lab = G0.LABEL[k]; s = {'run_id': rid, 'label': lab, 'deck_sha256': deck or G0.DECK[k], 'model_sha256': G0.MATERIAL[k], 'notes': f'STARTED model={MODEL}'}
    return [s] + ([fin(rid, lab)] if finish else [])


def seq(keys, start=114, finish_last=True):
    out = []
    for i, k in enumerate(keys): out += s_row(f'run_{start + i:04d}', k, finish=finish_last or i < len(keys) - 1)
    return out


def index(tag, extra, drop_last_f=False, inv_skip=(), reuse_deck=None):
    TMP.mkdir(exist_ok=True); p = TMP / f'idx_{tag}.csv'
    real = [(r['run_id'], r['label']) for r in csv.DictReader((PKG / 'results' / 'RUN_INDEX.csv').open(newline='')) if int(r['run_id'][4:]) <= 77]
    reuse = {rid: (lab, dk, mk) for rid, lab, dk, mk in G0.REUSE.values()}
    with p.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); done = set()
        for rid, lab in real:
            if rid in reuse and rid not in done:
                lab_, dk, mk = reuse[rid]; done.add(rid)
                w.writerow({'run_id': rid, 'label': lab, 'deck_sha256': (reuse_deck or dk) if rid == 'run_0068' else dk, 'model_sha256': mk,
                            'notes': f'STARTED model={MODEL}'})
            else: w.writerow({'run_id': rid, 'label': lab, 'notes': 'SYNTHETIC'})
        for row in prev_rows(drop_last_f) + extra: w.writerow({k: row.get(k, '') for k in FIELDS})
    inv = {'runs': []}; of = {v: k for k, v in G0.LABEL.items()}
    for row in extra:
        if row.get('notes', '').startswith('STARTED') and row['label'] in of and row['run_id'] not in inv_skip:
            k = of[row['label']]
            inv['runs'].append({'run_id': row['run_id'], 'label': row['label'], 'entry': k, 'model_file': MODEL, 'deck_sha256': G0.DECK[k],
                                'model_sha256': G0.MATERIAL[k], 'reason': 'synthetic'})
    ip = TMP / f'inv_{tag}.json'; ip.write_text(json.dumps(inv)); return p, ip


def case(name, want, idx_inv, reg_dec, procs=(), patch=None, env=None):
    g = load(GATE, 'gg_under_test'); Fm = load(FGF, 'gf_under_test'); D = load(DEG, 'gde_under_test'); C = load(C10, 'c10_under_test')
    C.list_processes = lambda: list(procs)
    C.INDEX, C.INVENTORY = idx_inv; C.REGISTER, C.DECISIONS = reg_dec; D.c10_module = lambda: C; Fm.de_module = lambda: D; g.f_module = lambda: Fm
    if patch: patch(g)
    os.chdir(PKG); buf = io.StringIO(); old = dict(os.environ)
    if env: os.environ.update(env)
    try:
        with contextlib.redirect_stdout(buf): rc = g.main(['--check'])
    finally: os.environ.clear(); os.environ.update(old)
    out = buf.getvalue(); [print('       ' + l) for l in out.splitlines() if l.startswith(('GATE PASSED', 'NOTHING', 'GATE STOP', '[FAIL]', '[STOP]'))]
    expect(name, rc, want); return out


def main():
    O = G0.ORDER
    try:
        L = logs('ok')
        out = case('logged, no S4a run -> 0, campaign_C10_S4a_b1', 0, index('none', []), L)
        expect('  names b1, 15 entries, run_0114', 'Next plan config/campaign_C10_S4a_b1.json: S4A-02-2p0' in out and 'these 15 entries' in out
               and 'first run id run_0114' in out, True)
        case('A50 not logged -> 1', 1, index('n50', []), logs('n50', a50=False))
        case('A50 draft heading -> 1', 1, index('d50', []), logs('d50', draft=True))
        case('A49 not logged -> 1', 1, index('n49', []), logs('n49', a49=False))
        case('stage F not exhausted (S3-09 finish row missing) -> 1', 1, index('fx', [], drop_last_f=True), L)
        case('S4a run unfinished -> 3', 3, index('unf', seq(O[:2], finish_last=False)), L)
        out = case('b1 partly done (5) -> 0, b1 again for 10', 0, index('part', seq(O[:5])), L)
        expect('  b1 from S4A-03-13p2, 10 entries', 'campaign_C10_S4a_b1.json: S4A-03-13p2' in out and 'these 10 entries' in out and 'run_0119' in out, True)
        out = case('b1 done -> 0, b2 (15)', 0, index('b1', seq(O[:15])), L)
        expect('  names b2 from S4A-07-2p0', 'campaign_C10_S4a_b2.json: S4A-07-2p0' in out and 'these 15 entries' in out, True)
        out = case('b1 + b2 done -> 0, b3 (12)', 0, index('b2', seq(O[:30])), L)
        expect('  names b3 from S4A-12-2p0, 12 entries', 'campaign_C10_S4a_b3.json: S4A-12-2p0' in out and 'these 12 entries' in out, True)
        case('all 42 done -> 4', 4, index('all', seq(O)), L)
        case('out of order (S4A-02-6p3 first) -> 1', 1, index('ord', seq([O[1]])), L)
        case('candidate skipped (S4A-03 before S4A-02 finished) -> 1', 1, index('skip', seq(O[:2] + [O[3]])), L)
        case('wrong STARTED deck sha -> 1', 1, index('deck', s_row('run_0114', O[0], deck='0' * 64)), L)
        case('started S4a run missing from the inventory -> 1', 1, index('inv', seq(O[:2]), inv_skip=('run_0115',)), L)
        case('two run ids for one label -> 1', 1, index('dup', seq([O[0], O[0]])), L)
        case('S4a label at or below run_0113 -> 1', 1, index('early', s_row('run_0100', O[0])), L)
        case('unknown label above run_0077 -> 1', 1, index('unk', [{'run_id': 'run_0114', 'label': 'c10_s4b_01_2p0_2p0', 'notes': 'STARTED'}]), L)
        case('PA-12: reused run_0068 deck differs -> 1', 1, index('reuse', [], reuse_deck='1' * 64), L)
        case('Silvaco process running -> 1', 1, index('proc', []), L, procs=[(4242, 'deckbuild.exe', 'deckbuild.exe -run x')])
        case('runner python running -> 1', 1, index('rpy', []), L, procs=[(4243, 'python.exe', 'python scripts/run_campaign.py config/x.json')])
        case('A49 (h) fit violated (need 106) -> 1', 1, index('fit', []), L, patch=lambda g: setattr(g, 'NEED_AFTER_S4A', 106))
        case('IWO_MODEL_FILE wrong -> 1', 1, index('env', []), L, env={'IWO_MODEL_FILE': 'config/iwo_material_model_v2.yaml'})
        case('decision record pin differs -> 1', 1, index('dec', []), L, patch=lambda g: g.FROZEN.__setitem__(g.DECISION, '0' * 64))
        # decision_ok units
        TMP.mkdir(exist_ok=True)
        dn = TMP / 'dN.json'; dn.write_text(json.dumps({'s4a_form': {'form': 'N', 'launches': 42}, 'chosen': {'tail': None, 'mobility': None},
                                                        'verdict': 'DECIDED: S4a form N (surface tail, ...)'}))
        dt = TMP / 'dT.json'; dt.write_text(json.dumps({'s4a_form': {'form': 'T', 'launches': 43}, 'chosen': {'tail': 'tail bulk', 'mobility': None},
                                                        'verdict': 'DECIDED: S4a form T (bulk tail, ...)'}))
        du = TMP / 'dU.json'; du.write_text(json.dumps({'s4a_form': {'form': 'N', 'launches': 42}, 'chosen': {'tail': None, 'mobility': None},
                                                        'verdict': 'UNRESOLVED: ...'}))
        expect('unit: decision form N -> ok', G0.decision_ok(dn)[0], True)
        expect('unit: decision form T -> not ok', G0.decision_ok(dt)[0], False)
        expect('unit: decision UNRESOLVED -> not ok', G0.decision_ok(du)[0], False)
        expect('unit: decision unreadable -> not ok', G0.decision_ok(TMP / 'missing.json')[0], False)
        expect('unit: order = 42 ids, matrix order, labels', (len(G0.ORDER), G0.ORDER[0], G0.ORDER[-1], G0.LABEL['S4A-10-13p2']),
               (42, 'S4A-02-2p0', 'S4A-15-13p2', 'c10_s4a_10_13p2_13p2'))
        expect('unit: NEED_AFTER_S4A', G0.NEED_AFTER_S4A, 100)
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print(f'{sum(results)}/{len(results)} passed'); return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main())
