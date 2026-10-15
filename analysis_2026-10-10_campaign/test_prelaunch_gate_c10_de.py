"""Tests of prelaunch_gate_c10_de.py (register A47; NO launch; no repo file written except the temporary ./test_tmp_c10_de, removed at the end).

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"; & <venv python> -I -B analysis_2026-10-10_campaign/test_prelaunch_gate_c10_de.py
In-process cases import the gate, give it the pinned C10 gate module with patched inputs: synthetic register / decision log, synthetic RUN_INDEX
(run_id/label of the real rows up to run_0077 only; synthetic S1-06R/DIAG rows run_0078..run_0096 and D/E rows above: no real row content
beyond run_id and label is copied), a fake process list, synthetic T2a deckbuild.out files.
"""
import contextlib, csv, importlib.util, io, os, shutil, sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent; GATE = HERE / 'prelaunch_gate_c10_de.py'; C10 = HERE / 'prelaunch_gate_c10.py'; TMP = HERE / 'test_tmp_c10_de'
PKG = HERE.parent
FIELDS = ['run_id', 'timestamp_utc', 'thickness_nm', 'label', 'deck_sha256', 'model_sha256', 'command', 'simulator', 'exit_code', 'converged',
          'elapsed_s', 'output_dir', 'notes']
MODEL = 'config/iwo_material_model_v3.yaml'
results = []


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


G0 = load(GATE, 'gde_constants'); C0 = load(C10, 'c10_constants')


def expect(name, got, want):
    ok = got == want; results.append(ok); print(f"{'ok  ' if ok else 'FAIL'} {name}: {got}", flush=True)


def logs(tag, heading=True, row=True, draft=False):
    TMP.mkdir(exist_ok=True); reg, dec = TMP / f'reg_{tag}.md', TMP / f'dec_{tag}.md'
    h = ['### A46: PA-2 revert: S2-03, S2-01 and S2-02 back to their registered decks']
    if heading: h.append('### A47: PA-4 and PA-5 entries: T0r, T2a, T2b, S2-09, S2-10' + (' (draft)' if draft else ''))
    r = ['| D-65 | x | PA-2 revert | x | x | IN FORCE |']
    if row: r.append('| D-67 | x | A47: PA-4 T0r T2a T2b, PA-5 S2-09 S2-10, branch_d_readout.py | x | x | IN FORCE |')
    reg.write_text('\n'.join(h) + '\n'); dec.write_text('\n'.join(r) + '\n'); return reg, dec


def c10_rows():
    rows = []
    for k, e in enumerate(C0.LAUNCH_ORDER):
        rid = f'run_{78 + k:04d}'; lab = C0.LABEL[e]
        rows += [{'run_id': rid, 'label': lab, 'notes': 'STARTED synthetic'}, {'run_id': rid, 'label': lab, 'exit_code': '0', 'notes': 'synthetic finish'}]
    return rows


def de_row(rid, k, finish=True, deck=None, od=''):
    lab = G0.LABEL[k]; s = {'run_id': rid, 'label': lab, 'deck_sha256': deck or G0.DECK[k], 'model_sha256': G0.MATERIAL[k], 'notes': f'STARTED model={MODEL}'}
    return [s] + ([{'run_id': rid, 'label': lab, 'exit_code': '0', 'output_dir': od, 'notes': 'synthetic finish'}] if finish else [])


def index(tag, extra, drop_last_c10=False):
    TMP.mkdir(exist_ok=True); p = TMP / f'idx_{tag}.csv'
    real = [(r['run_id'], r['label']) for r in csv.DictReader((PKG / 'results' / 'RUN_INDEX.csv').open(newline='')) if int(r['run_id'][4:]) <= 77]
    rows = c10_rows()
    if drop_last_c10: rows = rows[:-2]
    with p.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
        for rid, lab in real: w.writerow({'run_id': rid, 'label': lab, 'notes': 'SYNTHETIC'})
        for row in rows + extra: w.writerow({k: row.get(k, '') for k in FIELDS})
    return p


def t2a_dir(name, oom):
    d = TMP / name; d.mkdir(parents=True, exist_ok=True)
    (d / 'deckbuild.out').write_text(('Error: Memory allocation failure.  Try killing processes\n' if oom else 'ATLAS> # Memory allocation failure in a comment\nok\n'))
    return d.relative_to(PKG).as_posix()


def case(name, want, idx, reg_dec, show=('GATE PASSED', 'NOTHING', 'GATE STOP', '[FAIL]', '[STOP]')):
    g = load(GATE, 'gde_under_test'); C = load(C10, 'c10_under_test'); C.list_processes = lambda: []
    C.INDEX = idx; C.REGISTER, C.DECISIONS = reg_dec; g.c10_module = lambda: C
    os.chdir(PKG); buf = io.StringIO()
    with contextlib.redirect_stdout(buf): rc = g.main(['--check'])
    out = buf.getvalue(); [print('       ' + l) for l in out.splitlines() if l.startswith(show) or 'Next plan' in l]
    expect(name, rc, want); return out


def main():
    try:
        L = logs('ok'); ok_od = t2a_dir('t2a_ok', False); oom_od = t2a_dir('t2a_oom', True)
        out = case('logged, no D/E run -> 0, campaign_C10_Dmesh', 0, index('none', []), L)
        expect('  names campaign_C10_Dmesh first', 'Next plan config/campaign_C10_Dmesh.json' in out, True)
        case('not logged -> 1', 1, index('none2', []), logs('no', heading=False, row=False))
        case('draft heading -> 1', 1, index('none3', []), logs('draft', draft=True))
        out = case('T0r, T2a done (no OOM) -> 0, T2b plan', 0, index('t2', de_row('run_0097', 'T0r') + de_row('run_0098', 'T2a', od=ok_od)), L)
        expect('  names campaign_C10_Dmesh_T2b', 'Next plan config/campaign_C10_Dmesh_T2b.json' in out, True)
        out = case('T2a OOM -> 0, E plan (T2b skipped)', 0, index('oom', de_row('run_0097', 'T0r') + de_row('run_0098', 'T2a', od=oom_od)), L)
        expect('  names campaign_C10_Efnord', 'Next plan config/campaign_C10_Efnord.json' in out, True)
        case('T2b after a T2a OOM -> 1', 1, index('oomt2b', de_row('run_0097', 'T0r') + de_row('run_0098', 'T2a', od=oom_od) + de_row('run_0099', 'T2b')), L)
        out = case('S2-09 done -> 0, E plan for S2-10', 0, index('e1', de_row('run_0097', 'T0r') + de_row('run_0098', 'T2a', od=ok_od) + de_row('run_0099', 'T2b')
                                                              + de_row('run_0100', 'S2-09')), L)
        expect('  E plan names S2-10 only', 'S2-10 (c10_s2_10_13p2), first run id run_0101' in out and 'S2-09 (' not in out.split('Next plan')[1], True)
        case('all done -> 4', 4, index('all', de_row('run_0097', 'T0r') + de_row('run_0098', 'T2a', od=ok_od) + de_row('run_0099', 'T2b')
                                         + de_row('run_0100', 'S2-09') + de_row('run_0101', 'S2-10')), L)
        case('all done with T2b skipped (OOM) -> 4', 4, index('alloom', de_row('run_0097', 'T0r') + de_row('run_0098', 'T2a', od=oom_od)
                                                              + de_row('run_0099', 'S2-09') + de_row('run_0100', 'S2-10')), L)
        case('T2a before T0r -> 1', 1, index('order', de_row('run_0097', 'T2a', od=ok_od)), L)
        case('E before D -> 1', 1, index('order2', de_row('run_0097', 'S2-09')), L)
        case('unfinished T0r -> 3', 3, index('unfin', de_row('run_0097', 'T0r', finish=False)), L)
        case('DIAG not exhausted (AFF-6p3 missing) -> 1', 1, index('diag', [], drop_last_c10=True), L)
        case('wrong STARTED deck sha -> 1', 1, index('deck', de_row('run_0097', 'T0r', deck='0' * 64)), L)
        case('unknown label above run_0077 -> 1', 1, index('unk', [{'run_id': 'run_0097', 'label': 'c10_s2_05_6p3', 'notes': 'STARTED'}]), L)
        case('two run ids for T0r -> 1', 1, index('dup', de_row('run_0097', 'T0r') + de_row('run_0098', 'T0r')), L)
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print(f'{sum(results)}/{len(results)} passed'); return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main())
