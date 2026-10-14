"""Tests of prelaunch_gate_c10.py (NO launch; no repo file written except the temporary ./test_tmp_c10, removed at the end).

Run from the package root with the project venv, isolated, IWO_MODEL_FILE set:
    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"; & <venv python> -I -B analysis_2026-10-10_campaign/test_prelaunch_gate_c10.py
Subprocess cases run the real gate (environment, cwd, -I; the real state, where PA-1 is not logged yet). In-process cases import the gate and
patch one constant or input: synthetic register / decision log (PA-1, PA-2 logged), synthetic RUN_INDEX (run_id/label of the real rows plus
synthetic rows above run_0077: no real row content beyond run_id and label is copied), synthetic inventory, synthetic S1-06R execution.json
and S1-rule record, synthetic check-8 audit (audits/S1-06R_check8_<run>.json), synthetic DIAG state projection and audit file, a fake process list.
"""
import contextlib, csv, importlib.util, io, json, os, shutil, subprocess, sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent; GATE = HERE / 'prelaunch_gate_c10.py'; TMP = HERE / 'test_tmp_c10'
PKG = Path(r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1")
VENV_PY = r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_ATLAS_Model_claude\.venv\Scripts\python.exe"
FIELDS = ['run_id', 'timestamp_utc', 'thickness_nm', 'label', 'deck_sha256', 'model_sha256', 'command', 'simulator', 'exit_code', 'converged',
          'elapsed_s', 'output_dir', 'notes']
MODEL = 'config/iwo_material_model_v3.yaml'
results = []


def expect(name, got, want):
    ok = got == want if not callable(want) else want(got)
    results.append(ok); print(f"{'ok  ' if ok else 'FAIL'} {name}: {got}", flush=True)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


G0 = load(GATE, 'gate_constants')   # pinned values for the synthetic rows


def sub(name, want, env=None, args=('-I', '-B'), cwd=PKG, extra=(), show=()):
    e = dict(os.environ); e.update({k: v for k, v in (env or {}).items() if v is not None}); [e.pop(k, None) for k, v in (env or {}).items() if v is None]
    p = subprocess.run([VENV_PY, *args, str(GATE), *extra], cwd=str(cwd), env=e, capture_output=True, text=True, timeout=900)
    fails = [l for l in p.stdout.splitlines() if l.startswith('[FAIL]')]
    for l in fails + [l for l in p.stdout.splitlines() if any(s in l for s in show)]: print('       ' + l)
    expect(name, (p.returncode, len(fails)) if callable(want) is False and isinstance(want, tuple) else p.returncode, want)


def inproc(name, want, *patches, show=(), argv=()):
    g = load(GATE, 'gate_under_test'); g.list_processes = lambda: []
    for p in patches: p(g)
    os.chdir(PKG); buf = io.StringIO()
    with contextlib.redirect_stdout(buf): rc = g.main(list(argv))
    out = buf.getvalue()
    for line in out.splitlines():
        if line.startswith(('[FAIL]', '[STOP]', 'NOTHING', 'GATE PASSED', 'GATE STOP')) or any(s in line for s in show): print('       ' + line)
    expect(name, rc, want); return out


def real_pairs():   # run_id and label only
    return [(r['run_id'], r['label']) for r in csv.DictReader((PKG / 'results' / 'RUN_INDEX.csv').open(newline=''))]


def synth_index(extra, fname):
    TMP.mkdir(exist_ok=True); p = TMP / fname
    with p.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
        for rid, lab in real_pairs(): w.writerow({'run_id': rid, 'label': lab, 'notes': 'SYNTHETIC'})
        for row in extra: w.writerow({k: row.get(k, '') for k in FIELDS})
    return p


def synth_inv(runs, fname):
    TMP.mkdir(exist_ok=True); p = TMP / fname
    base = json.loads((PKG / 'config' / 'sealed_runs.json').read_text()); base['runs'] = base['runs'] + runs
    p.write_text(json.dumps(base, indent=1)); return p


def synth_logs(pa1=True, pa2=True, draft=False):
    TMP.mkdir(exist_ok=True); tag = f'{int(pa1)}{int(pa2)}{int(draft)}'; reg, dec = TMP / f'register_{tag}.md', TMP / f'decisions_{tag}.md'   # one file pair per variant
    h = ['### A40: unrelated']
    if pa1: h.append('### A45: S1-06 two-carrier continuation repair (one launch, S1-06R)' + (' (draft)' if draft else ''))
    if pa2: h.append('### A46: the same continuation in the S2-01, S2-02 and S2-03 decks')
    reg.write_text('\n'.join(h) + '\n')
    d = ['| D-58 | x | unrelated | IN FORCE |']
    if pa1: d.append('| D-59 | 2026-10-16 | PA-1 S1-06R continuation repair logged | user | Codex | IN FORCE |')
    if pa2: d.append('| D-60 | 2026-10-16 | PA-2 continuation in S2-01/02/03 | user | Codex | IN FORCE |')
    dec.write_text('\n'.join(d) + '\n')
    return lambda g: (setattr(g, 'REGISTER', reg), setattr(g, 'DECISIONS', dec))


def started(rid, eid, **kw):
    r = {'run_id': rid, 'label': G0.LABEL[eid], 'deck_sha256': G0.DECK[eid], 'model_sha256': G0.MATERIAL[eid],
         'notes': f'STARTED points=76 timeout=3600s launch 78/260 model={MODEL}'}
    r.update(kw); return r


def finish(rid, eid, code, out=''):
    return {'run_id': rid, 'label': G0.LABEL[eid], 'exit_code': code, 'output_dir': out, 'notes': 'FINISHED (synthetic)'}


def inv_row(rid, eid, **kw):
    r = {'run_id': rid, 'label': G0.LABEL[eid], 'entry': eid, 'model_file': MODEL, 'deck_sha256': G0.DECK[eid], 'model_sha256': G0.MATERIAL[eid],
         'reason': 'synthetic test'}
    r.update(kw); return r


def check8(rid='run_0078', raw=None, drop=(), ent='S1-06R', **kw):
    """write the synthetic check-8 audit TMP/audits/<ent>_check8_<rid>.json for entry ent: all values as required, kw overrides values, drop removes keys,
    raw writes that text instead"""
    au = TMP / 'audits'; au.mkdir(parents=True, exist_ok=True); p = au / f'{ent}_check8_{rid}.json'
    a = {'entry': ent, 'run': rid, 'deck_sha256': G0.DECK[ent], 'exported_rows': 76, 'vg_m1p6_count': 1, 'continuation_rows_exported': 0,
         'off_grid_trap_rows': 0, 'vg_set_complete': True, 'vg_unique': True, 'values_finite': True, 'log_reopen_ok': True, 'result': 'PASS',
         'evidence': {'exported_rows': 'terminal_currents.csv (synthetic)'}, 'auditor': 'synthetic test'}
    a.update(kw); [a.pop(k, None) for k in drop]
    p.write_text(raw if raw is not None else json.dumps(a)); return p


def run_dir(d, rid, label, exj=None, vg=None, nan=False):
    """synthetic run directory: execution.json of a completed run (kw exj overrides fields) and terminal_currents.csv (synthetic numbers) on
    the registered grid, or on vg"""
    d = Path(d); d.mkdir(parents=True, exist_ok=True)
    e = {'run_id': rid, 'label': label, 'status': 'REAL_ATLAS_SCORED', 'returncode': 0, 'timed_out': False, 'scan': {'errors': [], 'finished': True},
         'requested_points': 76}
    e.update(exj or {}); (d / 'execution.json').write_text(json.dumps(e))
    vg = list(G0.REG_GRID) if vg is None else vg
    with (d / 'terminal_currents.csv').open('w', newline='') as f:
        w = csv.writer(f); w.writerow(['vg_V', 'id_raw_A', 'is_raw_A', 'ig_raw_A', 'id_A_per_um', 'kcl_abs_A', 'kcl_pass', 'above_abs_floor'])
        for k, v in enumerate(vg):
            w.writerow([v, 'nan' if (nan and k == 40) else 1e-12 * (k + 1), -1e-12 * (k + 1), 1e-18, 1e-13 * (k + 1), 1e-20, 1, 1])
    return str(d)


def s106r_dir(status='REAL_ATLAS_SCORED', verdict='PASS', rid='run_0078', record=True, audit=True, exj=None, vg=None, nan=False):
    d = run_dir(TMP / f'{rid}_s106r', rid, G0.LABEL['S1-06R'], exj=dict(exj or {}, status=status), vg=vg, nan=nan)
    ex = TMP / 'extract'; ex.mkdir(exist_ok=True)
    rec = ex / f'compare_{rid}_vs_run_0069.json'
    if record: rec.write_text(json.dumps({'run': rid, 'ref': 'run_0069', 'rule': 'S1-06 (two carriers) vs S1-02', 'verdict': verdict}))
    elif rec.exists(): rec.unlink()
    if audit: check8(rid)
    else: (TMP / 'audits' / f'S1-06R_check8_{rid}.json').unlink(missing_ok=True)
    return d


def synth_solver(text_from, text_to, fname):
    """config/solver.yaml copy with one text replacement"""
    TMP.mkdir(exist_ok=True); p = TMP / fname; t = (PKG / 'config' / 'solver.yaml').read_text()
    assert text_from in t; p.write_text(t.replace(text_from, text_to)); return p


def st(idx=None, inv=None, extract=True, state=None, sealed=True):
    def f(g):
        if idx is not None: g.INDEX = idx
        if inv is not None: g.INVENTORY = inv
        if extract: g.EXTRACT = TMP / 'extract'; g.AUDITS = TMP / 'audits'
        g.DIAG_STATE = state if state is not None else TMP / 'no_state.json'
        if sealed: g.SEALED_DIR = TMP / 'sealed'
    return f


if __name__ == '__main__':
    assert os.environ.get('IWO_MODEL_FILE') == MODEL and sys.flags.isolated, 'run with -I and IWO_MODEL_FILE set'
    shutil.rmtree(TMP, ignore_errors=True)   # no state left by an interrupted earlier run
    pa1_logged = all(G0.amendment_logged(['S1-06R'], ['S1-06R']))   # real register / decision log
    print(f'== subprocess cases (real gate process, real state: PA-1 {"logged" if pa1_logged else "not logged yet"})')
    if pa1_logged: sub('real state (PA-1 logged, nothing started): exit 0, no failure', (0, 0), extra=('--check',))
    else: sub('real state: exit 1 with exactly the two PA-1 failures', (1, 2), extra=('--check',))
    sub('IWO_MODEL_FILE unset', 1, env={'IWO_MODEL_FILE': None})
    sub('IWO_MODEL_FILE = V2 model', 1, env={'IWO_MODEL_FILE': 'config/iwo_material_model_v2.yaml'})
    sub('IWO_ATLAS_VIEWERS=kill', 1, env={'IWO_ATLAS_VIEWERS': 'kill'})
    sub('not isolated (no -I)', 1, args=('-B',))
    sub('wrong working directory', 1, cwd=HERE)

    print('== in-process: next run S1-06R')
    logs = synth_logs(); base_inv = synth_inv([], 'inv_base.json'); idx0 = synth_index([], 'idx0.csv')
    out = inproc('PA-1/PA-2 logged, nothing started: PASS, next S1-06R', 0, logs, st(idx0, base_inv), show=('scripts/run_campaign.py',))
    expect('  command names the S1R plan and no --retry', 'campaign_C10_S1r_repair.json' in out and '--retry' not in out, True)
    expect('  builder line: pinned bytes 734125a8, Codex 19:02Z (a) acceptance (no other review claim)',
           'pinned bytes 734125a8 (Codex 2026-10-14T19:02Z (a): builder accepted)' in out and 'reviewed 2026-10-15' not in out, True)
    expect('  NO.TRAP unset in the S1-06R and PA-2 decks', '[OK] NO.TRAP unset' in out, True)
    expect('  budget: max_launches == 260 and C10 cap 200 checked', '[OK] config/solver.yaml: exactly one max_launches and it == 260' in out
           and '[OK] C10 cap == 200 (gate constant and run_campaign.C10_CAP' in out, True)
    expect('  REG_GRID: 76 points, -1.6 once, no continuation point, = the run_0069 (S1-02) V_G set',
           len(G0.REG_GRID) == 76 and G0.REG_GRID.count(-1.6) == 1 and not set(G0.CONT_VG) & set(G0.REG_GRID)
           and sorted(round(float(r['vg_V']), 6) + 0.0 for r in csv.DictReader((PKG / G0.S1_02_DIR / 'terminal_currents.csv').open(newline=''))) == list(G0.REG_GRID), True)
    print("== Codex 2026-10-14T19:02Z probe 3 (max_launches 261) and the caps")
    inproc('Codex probe 3: max_launches raised to 261', 1, logs, st(idx0, base_inv), lambda g: setattr(g, 'SOLVER', synth_solver('max_launches: 260', 'max_launches: 261', 'solver_261.yaml')))
    inproc('max_launches lowered to 259', 1, logs, st(idx0, base_inv), lambda g: setattr(g, 'SOLVER', synth_solver('max_launches: 260', 'max_launches: 259', 'solver_259.yaml')))
    inproc('a second max_launches line', 1, logs, st(idx0, base_inv), lambda g: setattr(g, 'SOLVER', synth_solver('max_launches: 260', 'max_launches: 260\n  max_launches: 261', 'solver_2x.yaml')))
    inproc('C10 cap raised to 201 (gate constant)', 1, logs, st(idx0, base_inv), lambda g: setattr(g, 'C10_CAP', 201))
    inproc('PA-1 heading marked draft', 1, synth_logs(draft=True), st(idx0, base_inv))
    inproc('PA-1 not in the decision log / register', 1, synth_logs(pa1=False), st(idx0, base_inv))
    inproc('mismatched pinned S1-06R deck hash', 1, logs, st(idx0, base_inv), lambda g: setattr(g, 'DECK', dict(g.DECK, **{'S1-06R': '0' * 64})))
    inproc('mismatched pinned S2-03 material hash', 1, logs, st(idx0, base_inv), lambda g: setattr(g, 'MATERIAL', dict(g.MATERIAL, **{'S2-03': '1' * 64})))
    inproc('mismatched DIAG plan hash', 1, logs, st(idx0, base_inv), lambda g: setattr(g, 'PLAN_SHA', dict(g.PLAN_SHA, **{G0.DIAG_REL: '2' * 64})))
    inproc('builder hash = public-repo 1375164 (pre-change builder pinned)', 1, logs, st(idx0, base_inv),
           lambda g: setattr(g, 'SCRIPTS', dict(g.SCRIPTS, **{'build_iwo_decks.py': g.BUILDER_1375164})))
    inproc('mismatched score_register.py hash', 1, logs, st(idx0, base_inv), lambda g: setattr(g, 'OTHER', {**g.OTHER, 'analysis_2026-10-10_campaign/score_register.py': '4' * 64}))
    inproc('fake process: deckbuild.exe', 1, logs, st(idx0, base_inv), lambda g: setattr(g, 'list_processes', lambda: [(4242, 'deckbuild.exe', '')]))
    inproc('fake process: python running run_campaign', 1, logs, st(idx0, base_inv),
           lambda g: setattr(g, 'list_processes', lambda: [(4243, 'python3.13.exe', r'python3.13.exe scripts/run_campaign.py config/x.json')]))
    inproc('fake process: python with unreadable command line', 1, logs, st(idx0, base_inv), lambda g: setattr(g, 'list_processes', lambda: [(4244, 'python.exe', None)]))

    def unreadable(): raise RuntimeError('simulated tasklist failure')
    inproc('process list unreadable (fail closed)', 1, logs, st(idx0, base_inv), lambda g: setattr(g, 'list_processes', unreadable))
    print('== in-process: RUN_INDEX states')
    inproc('DIAG run before S1-06R (order)', 1, logs, st(synth_index([started('run_0078', 'S2-04'), finish('run_0078', 'S2-04', '0')], 'idx_o.csv'),
                                                       synth_inv([inv_row('run_0078', 'S2-04')], 'inv_o.json')))
    print('== Codex 2026-10-14T19:02Z probe 2 (B1 recorded before S1-06R) and the launch order')
    d79 = s106r_dir(rid='run_0079'); inv_b1 = synth_inv([inv_row('run_0078', 'S2-04')], 'inv_b1.json')
    state0 = TMP / 'diag_state0.json'; state0.write_text(json.dumps({'runs': [], 'gates': []}))
    out = inproc('Codex probe 2: B1 (S2-04) run_0078 before S1-06R run_0079 (valid, check 8 and S1 rule PASS)', 1, logs,
                 st(synth_index([started('run_0078', 'S2-04'), finish('run_0078', 'S2-04', '0'), started('run_0079', 'S1-06R', output_dir=d79),
                                 finish('run_0079', 'S1-06R', '0', d79)], 'idx_b1.csv'), inv_b1, state=state0))
    expect('  the failure is the order check', '[FAIL] order: STARTED runs above run_0077' in out, True)
    inproc('B1 before S1-06R, S1-06R timed out', 1, logs, st(synth_index([started('run_0078', 'S2-04'), finish('run_0078', 'S2-04', '0'),
                                                                         started('run_0079', 'S1-06R'), finish('run_0079', 'S1-06R', 'timeout')], 'idx_b1t.csv'), inv_b1, state=state0))
    inproc('S2-06 before S2-04 (DIAG order skipped)', 1, logs, st(synth_index([started('run_0078', 'S1-06R'), finish('run_0078', 'S1-06R', 'timeout'),
                                                                              started('run_0079', 'S2-06'), finish('run_0079', 'S2-06', '0')], 'idx_o2.csv'),
                                                                 synth_inv([inv_row('run_0079', 'S2-06')], 'inv_o2.json'), state=state0))
    inproc('another label above run_0077', 1, logs, st(synth_index([{'run_id': 'run_0078', 'label': 'c10_s3_04_2p0', 'notes': 'STARTED'}], 'idx_x.csv'), base_inv))
    inproc('third S2-11 launch', 1, logs, st(synth_index([started('run_0078', 'S2-11')], 'idx_3.csv'), base_inv))
    inproc('S1-06R started, no finish row: STOP', 3, logs, st(synth_index([started('run_0078', 'S1-06R')], 'idx_r.csv'), base_inv))
    inproc('S1-06R STARTED row with a wrong deck_sha256', 1, logs, st(synth_index([started('run_0078', 'S1-06R', deck_sha256='5' * 64),
                                                                                  finish('run_0078', 'S1-06R', 'timeout')], 'idx_rd.csv'), base_inv))
    inproc('S1-06R STARTED note without model=', 1, logs, st(synth_index([started('run_0078', 'S1-06R', notes='STARTED points=76'),
                                                                         finish('run_0078', 'S1-06R', 'timeout')], 'idx_rn.csv'), base_inv))
    idx_to = synth_index([started('run_0078', 'S1-06R'), finish('run_0078', 'S1-06R', 'timeout')], 'idx_to.csv')
    out = inproc('S1-06R timed out (electron-only ASSUMED): PASS, next S2-04 (DIAG)', 0, logs, st(idx_to, base_inv), show=('ASSUMED', 'scripts/run_campaign.py'))
    expect('  command names the DIAG plan', 'campaign_C10_DIAG.json' in out and 'continues' in out.lower(), True)
    expect('  timed-out S1-06R is not interpreted: no check-8 audit required (none exists)',
           'no check-8 audit is required' in out and not (TMP / 'audits' / 'S1-06R_check8_run_0078.json').exists(), True)
    inproc('S1-06R timed out, PA-2 not logged', 1, synth_logs(pa2=False), st(idx_to, base_inv))
    d = s106r_dir(verdict='PASS')
    idx_ok = synth_index([started('run_0078', 'S1-06R', output_dir=d), finish('run_0078', 'S1-06R', '0', d)], 'idx_ok.csv')
    out = inproc('S1-06R valid, check-8 audit as required, S1 rule PASS: PASS, next S2-04', 0, logs, st(idx_ok, base_inv), show=('S1 rule', 'check 8', 'run_problems'))
    expect('  run_problems (both endpoints) before check 8 before the S1 rule', '[OK] frozen run_problems: none for S1-06R run_0078 and S1-02 run_0069' in out
           and out.index('[OK] frozen run_problems') < out.index('[OK] check 8') < out.index('[OK] S1 rule'), True)
    s106r_dir(verdict='FAIL (drop the electron-only assumption)')
    out = inproc('S1-06R valid, S1 rule FIRED: STOP', 3, logs, st(idx_ok, base_inv))
    expect('  the stop is the S1 rule (check 8 passed)', '[OK] check 8' in out and 'S1 rule FIRED' in out, True)
    s106r_dir(record=False)
    out = inproc('S1-06R valid, no S1-rule record: STOP', 3, logs, st(idx_ok, base_inv), show=('campaign_extract.py compare',))
    expect('  comparison command names both actual run directories (not a bare run_0069)',
           f'campaign_extract.py compare "{d}" "results/runs/run_0069_13p2_c10_s1_02_13p2" --rule s1_06' in out, True)
    print('== Codex 2026-10-14T19:02Z probe 1: frozen run_problems on both S1 endpoints before a PASS is accepted')
    for name, exj in [('Codex probe 1: REAL_ATLAS_SCORED with timeout, simulator errors and no completion banner',
                       {'timed_out': True, 'scan': {'errors': ['simulated error'], 'finished': False}}),
                      ('REAL_ATLAS_SCORED, timed out only', {'timed_out': True}),
                      ('REAL_ATLAS_SCORED, simulator error only', {'scan': {'errors': ['simulated error'], 'finished': True}}),
                      ('REAL_ATLAS_SCORED, no completion banner only', {'scan': {'errors': [], 'finished': False}}),
                      ('REAL_ATLAS_SCORED, return code 1', {'returncode': 1}), ('REAL_ATLAS_SCORED, no timeout flag', {'timed_out': None}),
                      ('REAL_ATLAS_SCORED, 77 requested points', {'requested_points': 77})]:
        s106r_dir(verdict='PASS', exj=exj)
        out = inproc(f'{name} (check-8 audit and S1-rule PASS record present): STOP', 3, logs, st(idx_ok, base_inv))
        expect('  no PASS accepted: ASSUMED, never TESTED; no command', 'ASSUMED, never TESTED' in out and 'electron-only TESTED' not in out
               and 'GATE PASSED' not in out, True)
    for name, kw in [('77 rows (continuation row -1.65 V leaked)', {'vg': list(G0.REG_GRID) + [-1.65]}),
                     ('a duplicate -1.6 V row in place of -1.8 V', {'vg': [(-1.6 if v == -1.8 else v) for v in G0.REG_GRID]}),
                     ('a non-finite current', {'nan': True})]:
        s106r_dir(verdict='PASS', **kw)
        inproc(f'S1-06R export with {name}: STOP (run_problems)', 3, logs, st(idx_ok, base_inv))
    s106r_dir(verdict='PASS')
    ref_bad = run_dir(TMP / 'ref_timeout', 'run_0069', 'c10_s1_02_13p2', exj={'timed_out': True})
    out = inproc('S1-02 reference endpoint timed out: STOP', 3, logs, st(idx_ok, base_inv), lambda g: setattr(g, 'S1_02_DIR', ref_bad))
    expect('  no PASS accepted', 'ASSUMED, never TESTED' in out and 'electron-only TESTED' not in out, True)
    ref_other = run_dir(TMP / 'ref_other', 'run_0068', 'c10_s1_01_13p2')
    inproc('S1-02 reference directory of another run: STOP', 3, logs, st(idx_ok, base_inv), lambda g: setattr(g, 'S1_02_DIR', ref_other))
    inproc('S1-02 reference directory missing: STOP', 3, logs, st(idx_ok, base_inv), lambda g: setattr(g, 'S1_02_DIR', str(TMP / 'no_ref')))
    print('== check 8 COMPUTED from the S1-06R export (complete V_G set; run_problems clean)')
    for name, vg in [('-1.65 V in place of -1.6 V (76 unique rows)', [(-1.65 if v == -1.6 else v) for v in G0.REG_GRID]),
                     ('an off-grid cut-back row -1.5 V in place of -1.4 V', [(-1.5 if v == -1.4 else v) for v in G0.REG_GRID])]:
        s106r_dir(verdict='PASS', vg=vg)
        out = inproc(f'computed check 8: {name}: STOP (UNVERIFIED)', 3, logs, st(idx_ok, base_inv))
        expect('  stop is the computed check 8 (no deletion); S1 rule not read', 'check 8 COMPUTED' in out and 'UNVERIFIED' in out
               and 'S1 rule (' not in out, True)
    s106r_dir(verdict='UNVERIFIED')
    inproc('S1-06R valid, S1 rule UNVERIFIED: STOP', 3, logs, st(idx_ok, base_inv))
    s106r_dir(status='KCL_FAILED', record=False, audit=False)
    inproc('S1-06R exit 0 but runner status KCL_FAILED (invalid -> ASSUMED, no audit needed): PASS', 0, logs, st(idx_ok, base_inv))

    print('== in-process: check 8 (valid S1-06R, S1 rule PASS; DIAG opens only with a passing check-8 audit)')
    s106r_dir(verdict='PASS', audit=False)
    out = inproc('no check-8 audit: STOP, DIAG not opened', 3, logs, st(idx_ok, base_inv))
    expect('  stop names check 8 and the audit path; S1 rule not read; no command',
           'check 8 (continuation log handling) not passed' in out and 'audits/S1-06R_check8_run_0078.json' in out
           and 'S1 rule (' not in out and 'GATE PASSED' not in out and 'run_campaign.py' not in out, True)
    for name, kw in [('exported_rows 79 (leaked continuation or trap rows)', {'exported_rows': 79}), ('exported_rows "76" (string)', {'exported_rows': '76'}),
                     ('exported_rows 76.0 (float)', {'exported_rows': 76.0}), ('vg_m1p6_count 2', {'vg_m1p6_count': 2}),
                     ('continuation_rows_exported 3', {'continuation_rows_exported': 3}), ('off_grid_trap_rows 1', {'off_grid_trap_rows': 1}),
                     ('off_grid_trap_rows false (boolean)', {'off_grid_trap_rows': False}), ('log_reopen_ok false', {'log_reopen_ok': False}),
                     ('log_reopen_ok "true" (string)', {'log_reopen_ok': 'true'}), ('result FAIL', {'result': 'FAIL'}),
                     ('result UNRESOLVED', {'result': 'UNRESOLVED'}), ('another run id', {'run': 'run_0079'}),
                     ('another deck sha256', {'deck_sha256': '7' * 64}), ('entry S1-06', {'entry': 'S1-06'}), ('empty evidence', {'evidence': ''}),
                     ('vg_set_complete false', {'vg_set_complete': False}), ('vg_unique "true" (string)', {'vg_unique': 'true'}),
                     ('values_finite 1 (integer)', {'values_finite': 1})]:
        check8(**kw); inproc(f'check-8 audit with {name}: STOP', 3, logs, st(idx_ok, base_inv))
    for key in ('exported_rows', 'vg_m1p6_count', 'continuation_rows_exported', 'off_grid_trap_rows', 'vg_set_complete', 'vg_unique', 'values_finite',
                'log_reopen_ok', 'evidence'):
        check8(drop=(key,)); inproc(f'check-8 audit without {key}: STOP', 3, logs, st(idx_ok, base_inv))
    check8(raw='{not json'); inproc('check-8 audit unreadable: STOP', 3, logs, st(idx_ok, base_inv))
    check8(raw='[76, 1, 0, 0, true]'); inproc('check-8 audit not a JSON object: STOP', 3, logs, st(idx_ok, base_inv))
    check8()
    idx_nx = synth_index([started('run_0078', 'S1-06R', output_dir=str(TMP / 'missing')), finish('run_0078', 'S1-06R', '0', str(TMP / 'missing'))], 'idx_nx.csv')
    inproc('S1-06R exit 0 without a readable execution.json: STOP', 3, logs, st(idx_nx, base_inv))
    s106r_dir(verdict='PASS')
    rows4 = [started('run_0078', 'S1-06R', output_dir=d), finish('run_0078', 'S1-06R', '0', d), started('run_0079', 'S2-04'), finish('run_0079', 'S2-04', '0')]
    state = TMP / 'diag_state.json'; state.write_text(json.dumps({'runs': [], 'gates': []}))
    inproc('S2-04 started but missing from the inventory', 1, logs, st(synth_index(rows4, 'idx_4.csv'), base_inv, state=state))
    inv4 = synth_inv([inv_row('run_0079', 'S2-04')], 'inv_4.json')
    out = inproc('S2-04 done and inventoried: PASS, next S2-06', 0, logs, st(synth_index(rows4, 'idx_4.csv'), inv4, state=state), show=('Next run',))
    expect('  next run is S2-06', 'Next run: S2-06' in out, True)
    inproc('S2-04 inventoried with another deck sha256', 1, logs, st(synth_index(rows4, 'idx_4.csv'), synth_inv([inv_row('run_0079', 'S2-04', deck_sha256='6' * 64)], 'inv_4w.json'), state=state))
    inproc('S2-04 done but the DIAG state projection is missing', 1, logs, st(synth_index(rows4, 'idx_4.csv'), inv4))
    stop = {'gate': 'G-S2-04-nominal', 'decision_id': 'abcdef0123456789', 'state': 'FIRED', 'action': 'stop'}
    state_s = TMP / 'diag_state_stop.json'; state_s.write_text(json.dumps({'runs': [], 'gates': [stop]}))
    inproc('DIAG gate stop not acknowledged: STOP', 3, logs, st(synth_index(rows4, 'idx_4.csv'), inv4, state=state_s))
    aud = TMP / 'audit.md'; aud.write_text('Audit of G-S2-04-nominal decision abcdef0123456789: completed.')
    out = inproc('DIAG gate stop with a cited audit: PASS with --ack-gate', 0, logs, st(synth_index(rows4, 'idx_4.csv'), inv4, state=state_s), argv=('--ack-audit', str(aud)))
    expect('  command carries --ack-gate G-S2-04-nominal', '--ack-gate G-S2-04-nominal' in out, True)
    bad = TMP / 'audit_bad.md'; bad.write_text('Audit of G-S2-04-nominal only.')
    inproc('DIAG gate stop, audit without the decision id: STOP', 3, logs, st(synth_index(rows4, 'idx_4.csv'), inv4, state=state_s), argv=('--ack-audit', str(bad)))
    print('== in-process: check 8 for the PA-2 runs (record only; their sealed run directories are never opened)')
    rows_s206 = rows4 + [started('run_0080', 'S2-06'), finish('run_0080', 'S2-06', '0')]
    inv_pa2 = synth_inv([inv_row('run_0079', 'S2-04'), inv_row('run_0080', 'S2-06'), inv_row('run_0081', 'S2-03')], 'inv_pa2.json')
    idx_pa2 = synth_index(rows_s206 + [started('run_0081', 'S2-03'), finish('run_0081', 'S2-03', '0')], 'idx_pa2.csv')
    out = inproc('S2-03 finished (exit 0) without a check-8 record: STOP', 3, logs, st(idx_pa2, inv_pa2, state=state))
    expect('  stop names the S2-03 record', 'S2-03_check8_run_0081.json missing' in out, True)
    check8('run_0081', ent='S2-03')
    out = inproc('S2-03 check-8 record as required: PASS, next S2-01', 0, logs, st(idx_pa2, inv_pa2, state=state), show=('Next run', 'PA-2 S2-03'))
    expect('  next run is S2-01', 'Next run: S2-01' in out and '[OK] check 8 (PA-2 S2-03 run_0081, record)' in out, True)
    for name, kw in [('the S1-06R deck sha256', {'deck_sha256': G0.DECK['S1-06R']}), ('entry S1-06R', {'entry': 'S1-06R'}),
                     ('an off-grid cut-back row (off_grid_trap_rows 1)', {'off_grid_trap_rows': 1}), ('vg_set_complete false', {'vg_set_complete': False}),
                     ('result UNVERIFIED', {'result': 'UNVERIFIED'})]:
        check8('run_0081', ent='S2-03', **kw); inproc(f'S2-03 check-8 record with {name}: STOP', 3, logs, st(idx_pa2, inv_pa2, state=state))
    (TMP / 'audits' / 'S2-03_check8_run_0081.json').unlink()
    idx_pa2t = synth_index(rows_s206 + [started('run_0081', 'S2-03'), finish('run_0081', 'S2-03', 'timeout')], 'idx_pa2t.csv')
    inproc('S2-03 timed out (not interpreted): no check-8 record required: PASS', 0, logs, st(idx_pa2t, inv_pa2, state=state))
    rows_all = [started('run_0078', 'S1-06R', output_dir=d), finish('run_0078', 'S1-06R', '0', d)]; invs = []
    for k, e in enumerate(G0.DIAG_ORDER[1:]):
        rid = f'run_{79 + k:04d}'; rows_all += [started(rid, e), finish(rid, e, '0')]; invs.append(inv_row(rid, e))
        if e in G0.PA2: check8(rid, ent=e)
    inproc('everything started: NOTHING TO LAUNCH (4, not a pass)', 4, logs, st(synth_index(rows_all, 'idx_all.csv'), synth_inv(invs, 'inv_all.json'), state=state))
    print('== check mode labels the output and keeps the exit code')
    out = inproc('--check, PASS state', 0, logs, st(idx0, base_inv), argv=('--check',))
    expect('  check-mode banner and would-be command', 'CHECK MODE' in out and 'Would-be command' in out, True)
    shutil.rmtree(TMP, ignore_errors=True)
    print(f'{sum(results)}/{len(results)} ok')
    sys.exit(0 if all(results) else 1)
