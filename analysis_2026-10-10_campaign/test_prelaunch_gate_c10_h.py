"""Tests of prelaunch_gate_c10_h.py (register A52; NO launch; no repo file written except the temporary ./test_tmp_c10_h, removed at the end).

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"; & <venv python> -I -B analysis_2026-10-10_campaign/test_prelaunch_gate_c10_h.py
In-process cases import the gate and give it the pinned G2, G, F, D/E and C10 gate modules with patched inputs: synthetic register / decision
log, synthetic RUN_INDEX (run_id/label of the real rows up to run_0077 only, plus synthetic STARTED rows of the reused run_0061/0068/0069 carrying
the pinned PA-12 hashes; synthetic S1-06R/DIAG rows run_0078..run_0096, D/E rows run_0097..run_0101, stage F rows run_0102..run_0113, S4a rows
run_0114..run_0149 finished, the interrupted run_0150 (STARTED row only), the A51 retry and the rest of batch 3 run_0151..run_0156 finished, and the
cases' S4c/S4d rows above: no real row content beyond run_id and label is copied), a fake process list and a stubbed git check (the record commit
is checked for real only in the last, informational case).
"""
import contextlib, csv, importlib.util, io, os, shutil, sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent; GATEH = HERE / 'prelaunch_gate_c10_h.py'; G2F = HERE / 'prelaunch_gate_c10_g2.py'; GG = HERE / 'prelaunch_gate_c10_g.py'
FGF = HERE / 'prelaunch_gate_c10_f.py'; DEG = HERE / 'prelaunch_gate_c10_de.py'; C10 = HERE / 'prelaunch_gate_c10.py'
TMP = HERE / 'test_tmp_c10_h'; PKG = HERE.parent
FIELDS = ['run_id', 'timestamp_utc', 'thickness_nm', 'label', 'deck_sha256', 'model_sha256', 'command', 'simulator', 'exit_code', 'converged',
          'elapsed_s', 'output_dir', 'notes']
MODEL = 'config/iwo_material_model_v3.yaml'
results = []


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


H0 = load(GATEH, 'gh_constants'); G0 = load(GG, 'gg_constants'); F0 = load(FGF, 'gf_constants'); D0 = load(DEG, 'gde_constants'); C0 = load(C10, 'c10_constants')
O = H0.ORDER; OA = G0.ORDER; I_INT = OA.index('S4A-14-2p0')


def expect(name, got, want):
    ok = got == want; results.append(ok); print(f"{'ok  ' if ok else 'FAIL'} {name}: {got}", flush=True)


def logs(tag, a52=True, a51=True, draft=False, row_seal=True):
    TMP.mkdir(exist_ok=True); reg, dec = TMP / f'reg_{tag}.md', TMP / f'dec_{tag}.md'
    s = H0.RECORD_SEAL[:16]
    h = ['### A49: stage G1 prerequisites: 0-launch S3 decision before S4a ... (PA-8 adoption ...); S4a forms N/T/I/TI ... (PA-12); PA-16 ...; PA-20 ...',
         '### A50: S4a execution entries of form N: S4A-02 .. S4A-15, route plans, prelaunch_gate_c10_g.py']
    if a51: h.append('### A51: S4a resume after the interrupted launch run_0150: one infrastructure retry of S4A-14-2p0 (--retry S4A-14-2p0), prelaunch_gate_c10_g2.py')
    if a52: h.append(f'### A52: PA-18 S4c confirmation wrapper s4c_confirm_wrapper.py, record {s}..., S4c and S4d execution entries, prelaunch_gate_c10_h.py'
                     + (' (draft)' if draft else ''))
    r = ['| D-69 | x | Register A49: s3_decision_a49.py, PA-8 | x | x | IN FORCE |',
         '| D-70 | x | Register A50: form N, campaign_C10_S4a_b1, prelaunch_gate_c10_g.py | x | x | IN FORCE |']
    if a51: r.append('| D-71 | x | Register A51: run_0150 interrupted; --retry S4A-14-2p0; prelaunch_gate_c10_g2.py | x | x | IN FORCE |')
    if a52: r.append('| D-75 | x | Register A52: PA-18 s4c_confirm_wrapper.py' + (f' record {s}' if row_seal else '') + '; prelaunch_gate_c10_h.py | x | x | IN FORCE |')
    reg.write_text('\n'.join(h) + '\n'); dec.write_text('\n'.join(r) + '\n'); return reg, dec


def fin(rid, lab): return {'run_id': rid, 'label': lab, 'exit_code': '0', 'notes': 'synthetic finish'}


def prev_rows(s4a_last_unfinished=False):
    rows = []
    for k, e in enumerate(C0.LAUNCH_ORDER):
        rid = f'run_{78 + k:04d}'; rows += [{'run_id': rid, 'label': C0.LABEL[e], 'notes': 'STARTED synthetic'}, fin(rid, C0.LABEL[e])]
    for k, e in enumerate(D0.ORDER):
        rid = f'run_{97 + k:04d}'; rows += [{'run_id': rid, 'label': D0.LABEL[e], 'notes': 'STARTED synthetic'}, fin(rid, D0.LABEL[e])]
    for k, e in enumerate(F0.ORDER):
        rid = f'run_{102 + k:04d}'; rows += [{'run_id': rid, 'label': F0.LABEL[e], 'notes': 'STARTED synthetic'}, fin(rid, F0.LABEL[e])]
    keys = OA[:I_INT] + ['S4A-14-2p0'] + OA[I_INT:]      # run_0114..run_0149, run_0150 (interrupted), run_0151..run_0156
    for i, k in enumerate(keys):
        rid = f'run_{114 + i:04d}'; lab = G0.LABEL[k]
        rows.append({'run_id': rid, 'label': lab, 'deck_sha256': G0.DECK[k], 'model_sha256': G0.MATERIAL[k], 'notes': f'STARTED model={MODEL}'})
        if rid != 'run_0150' and not (s4a_last_unfinished and rid == 'run_0156'): rows.append(fin(rid, lab))
    return rows


def h_row(rid, k, finish=True, deck=None):
    lab = H0.LABEL[k]; s = {'run_id': rid, 'label': lab, 'deck_sha256': deck or H0.DECK[k], 'model_sha256': H0.MATERIAL[k], 'notes': f'STARTED model={MODEL}'}
    return [s] + ([fin(rid, lab)] if finish else [])


def seq(keys, start=157, finish_last=True):
    out = []
    for i, k in enumerate(keys): out += h_row(f'run_{start + i:04d}', k, finish=finish_last or i < len(keys) - 1)
    return out


def index(tag, extra, s4a_last_unfinished=False):
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
        for row in prev_rows(s4a_last_unfinished) + extra: w.writerow({k: row.get(k, '') for k in FIELDS})
    return p


def case(name, want, idx, reg_dec, procs=(), patch=None, env=None, git=(True, 'synthetic HEAD')):
    h = load(GATEH, 'gh_under_test'); g2 = load(G2F, 'gg2_under_test'); G = load(GG, 'gg_under_test'); Fm = load(FGF, 'gf_under_test')
    D = load(DEG, 'gde_under_test'); C = load(C10, 'c10_under_test')
    C.list_processes = lambda: list(procs)
    C.INDEX = idx; C.REGISTER, C.DECISIONS = reg_dec; D.c10_module = lambda: C; Fm.de_module = lambda: D; G.f_module = lambda: Fm; g2.g_module = lambda: G
    h.g2_module = lambda: g2
    if git is not None: h.committed_in_git = lambda rel, sha: git
    if patch: patch(h)
    os.chdir(PKG); buf = io.StringIO(); old = dict(os.environ)
    if env: os.environ.update(env)
    try:
        with contextlib.redirect_stdout(buf): rc = h.main(['--check'])
    finally: os.environ.clear(); os.environ.update(old)
    out = buf.getvalue(); [print('       ' + l) for l in out.splitlines() if l.startswith(('GATE PASSED', 'NOTHING', 'GATE STOP', '[FAIL]', '[STOP]', '&'))]
    expect(name, rc, want); return out


def main():
    try:
        L = logs('ok')
        out = case('S4a complete, A52 logged, no S4c run -> 0, campaign_C10_S4c, 3 entries from run_0157', 0, index('fresh', []), L)
        expect('  command: run_campaign.py config/campaign_C10_S4c.json, no --retry, first run id run_0157, 3 entries',
               out.rstrip().endswith('scripts/run_campaign.py config/campaign_C10_S4c.json') and 'first run id run_0157' in out and 'these 3 entries' in out, True)
        case('A52 not logged -> 1', 1, index('n52', []), logs('n52', a52=False))
        case('A52 heading draft -> 1', 1, index('d52', []), logs('d52', draft=True))
        case('A52 decision row without the record seal prefix -> 1', 1, index('r52', []), logs('r52', row_seal=False))
        case('A51 not logged -> 1', 1, index('n51', []), logs('n51', a51=False))
        case('record not committed in git HEAD -> 1', 1, index('git', []), L, git=(False, 'not in HEAD'))
        case('S4C-2p0 started, no finish row -> 3', 3, index('u1', h_row('run_0157', 'S4C-2p0', finish=False)), L)
        out = case('S4C-2p0, S4C-6p3 done -> 0, S4c plan, 1 entry left (S4C-13p2)', 0, index('c2', seq(O[:2])), L)
        expect('  next S4C-13p2, run_0159', 'S4C-13p2' in out and 'run_0159' in out and 'campaign_C10_S4c.json' in out.splitlines()[-1], True)
        out = case('S4c complete -> 0, campaign_C10_S4d, 3 entries from run_0160', 0, index('c3', seq(O[:3])), L)
        expect('  command: config/campaign_C10_S4d.json, run_0160, 3 entries',
               out.rstrip().endswith('scripts/run_campaign.py config/campaign_C10_S4d.json') and 'run_0160' in out and 'these 3 entries' in out, True)
        case('S4c complete, S4D-2p0 unfinished -> 3', 3, index('d1u', seq(O[:4], finish_last=False)), L)
        case('all six done -> 4', 4, index('all', seq(O)), L)
        case('S4D-2p0 before S4C-13p2 (order) -> 1', 1, index('ord', seq(['S4C-2p0', 'S4C-6p3', 'S4D-2p0'])), L)
        case('S4D first -> 1', 1, index('ord2', seq(['S4D-2p0'])), L)
        case('two runs of S4C-2p0 -> 1', 1, index('two', seq(['S4C-2p0', 'S4C-2p0'])), L)
        case('S4C-2p0 STARTED deck differs -> 1', 1, index('deck', h_row('run_0157', 'S4C-2p0', deck='0' * 64)), L)
        case('S4a incomplete (run_0156 without finish row) -> 1', 1, index('s4a', [], s4a_last_unfinished=True), L)
        case('unknown label above run_0077 -> 1', 1, index('unk', [{'run_id': 'run_0157', 'label': 'c10_s4b_01_2p0_2p0', 'notes': 'STARTED'}]), L)
        case('Silvaco process running -> 1', 1, index('proc', []), L, procs=[(4242, 'deckbuild.exe', 'deckbuild.exe -run x')])
        case('runner python running -> 1', 1, index('rpy', []), L, procs=[(4243, 'python.exe', 'python scripts/run_campaign.py config/x.json')])
        case('IWO_MODEL_FILE wrong -> 1', 1, index('env', []), L, env={'IWO_MODEL_FILE': 'config/iwo_material_model_v2.yaml'})
        case('IWO_ATLAS_VIEWERS set -> 1', 1, index('view', []), L, env={'IWO_ATLAS_VIEWERS': '1'})
        case('G2 gate pin differs -> 1', 1, index('pin', []), L, patch=lambda m: setattr(m, 'G2_GATE_SHA', '0' * 64))
        case('wrapper pin differs -> 1', 1, index('wpin', []), L, patch=lambda m: setattr(m, 'WRAPPER_SHA', '0' * 64))
        case('record seal pin differs -> 1', 1, index('seal', []), L, patch=lambda m: setattr(m, 'RECORD_SEAL', '1' * 64))
        case('S4c plan pin differs -> 1', 1, index('plan', []), L, patch=lambda m: m.PLAN_SHA.update({m.P_C: '2' * 64}))
        case('deck pin differs from the record dry build -> 1', 1, index('dpin', []), L, patch=lambda m: m.DECK.update({'S4D-6p3': '3' * 64}))
        case('A52 fit violated (need 99: 96 + 6 + 99 > 200) -> 1', 1, index('fit', []), L, patch=lambda m: setattr(m, 'NEED_AFTER_S4CD', 99))
        case('A52 fit at the limit (need 98: 96 + 6 + 98 = 200) -> 0', 0, index('fit2', []), L, patch=lambda m: setattr(m, 'NEED_AFTER_S4CD', 98))
        expect('unit: constants', (H0.NEED_AFTER_S4CD, H0.LAST_S4A, H0.INTERRUPTED, H0.G2_GATE_SHA[:8], len(H0.ORDER), H0.LABEL['S4D-13p2']),
               (76, 'run_0156', 'run_0150', '144fff2f', 6, 'c10_s4d_13p2_13p2'))
        expect('unit: S4d material == S4c material per film (IGZO options are solver-side)', [H0.MATERIAL[f'S4C-{t}'] == H0.MATERIAL[f'S4D-{t}'] for t in H0.TAGS], [True] * 3)
        ok, det = H0.committed_in_git(H0.RECORD_REL, H0.RECORD_FILE_SHA)
        print(f'info (not counted): real git check of the record commit: {ok} ({det})')
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print(f'{sum(results)}/{len(results)} passed'); return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main())
