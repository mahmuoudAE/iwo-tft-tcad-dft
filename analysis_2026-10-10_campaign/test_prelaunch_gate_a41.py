"""Failure-path tests of prelaunch_gate_a41.py and analysis_2026-10-10_campaign/regress_sealed_aware.py (NO launch, NO repo file written).

Run from the package root with the project venv, isolated, IWO_MODEL_FILE set:
    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"; & <venv python> -I -B test_prelaunch_gate_a41.py
Subprocess cases run the real gate (bad environment, wrong cwd, no -I, a real process named tonyplot.exe = a renamed copy of the system
PING.EXE, a real python process whose command line contains 'run_campaign'). In-process cases import the gate / wrapper and patch one
constant or input (expected hash, process list, synthetic RUN_INDEX / inventory written to ./test_tmp). Synthetic RUN_INDEX files hold
run_id/label rows only (plus synthetic STARTED rows for A41 runs); no real row content beyond run_id and label is copied.
"""
import contextlib, csv, importlib.util, io, json, os, shutil, subprocess, sys, time
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent; GATE = HERE / 'prelaunch_gate_a41.py'; TMP = HERE / 'test_tmp'
PKG = Path(r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1")
VENV_PY = r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_ATLAS_Model_claude\.venv\Scripts\python.exe"
FIELDS = ['run_id', 'timestamp_utc', 'thickness_nm', 'label', 'deck_sha256', 'model_sha256', 'command', 'simulator', 'exit_code', 'converged',
          'elapsed_s', 'output_dir', 'notes']
results = []


def expect(name, got, want):
    ok = got == want if not callable(want) else want(got)
    results.append(ok); print(f"{'ok  ' if ok else 'FAIL'} {name}: exit {got}", flush=True)


def sub(name, want, env=None, args=('-I', '-B'), cwd=PKG, py=VENV_PY, show=()):
    e = dict(os.environ); e.update(env or {}); [e.pop(k) for k, v in (env or {}).items() if v is None]
    p = subprocess.run([py, *args, str(GATE)], cwd=str(cwd), env=e, capture_output=True, text=True, timeout=600)
    for line in p.stdout.splitlines():
        if line.startswith('[FAIL]') or any(s in line for s in show): print('       ' + line)
    expect(name, p.returncode, want)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def inproc(name, want, patch, show=()):
    g = load(GATE, 'gate_under_test'); patch(g); os.chdir(PKG); buf = io.StringIO()
    with contextlib.redirect_stdout(buf): rc = g.main()
    for line in buf.getvalue().splitlines():
        if line.startswith('[FAIL]') or line.startswith('NOTHING') or any(s in line for s in show): print('       ' + line)
    expect(name, rc, want)


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


D11, DD2 = '3034b7e276d40f8f8e3587219cbafe82c97c9db43ce23706938e18b4285ee956', '09bb893d3254c9f0de24238e5b6f5eca3fa99c549c8d3f9456709eec95ff8e85'
MAT = '974b23ea65ceaa38185221c1a62bb6f1b4eef54fd4884bb7eaadc38a83f18204'
NOTE = 'STARTED points=1 timeout=5400s launch 76/260 model=config/iwo_material_model_v3.yaml'
R76 = {'run_id': 'run_0076', 'label': 'c10_s2_11_2p0', 'deck_sha256': D11, 'model_sha256': MAT, 'notes': NOTE}
R77 = {'run_id': 'run_0077', 'label': 'c10_s0_02_dos2_2p0', 'deck_sha256': DD2, 'model_sha256': MAT, 'notes': NOTE}
I76 = {'run_id': 'run_0076', 'label': 'c10_s2_11_2p0', 'entry': 'S2-11', 'model_file': 'config/iwo_material_model_v3.yaml', 'deck_sha256': D11,
       'model_sha256': MAT, 'reason': 'synthetic test'}
I77 = dict(I76, run_id='run_0077', label='c10_s0_02_dos2_2p0', entry='S0-02-DOS2', deck_sha256=DD2)

if __name__ == '__main__':
    assert os.environ.get('IWO_MODEL_FILE') == 'config/iwo_material_model_v3.yaml' and sys.flags.isolated, 'run with -I and IWO_MODEL_FILE set'
    print('== subprocess cases (real gate process)')
    sub('baseline: all checks pass', 0, show=('GATE PASSED', 'scripts/run_campaign.py'))
    sub('IWO_MODEL_FILE unset', 1, env={'IWO_MODEL_FILE': None})
    sub('IWO_MODEL_FILE = V2 model (env, deck and material hash mismatch)', 1, env={'IWO_MODEL_FILE': 'config/iwo_material_model_v2.yaml'})
    sub('IWO_ATLAS_VIEWERS=kill', 1, env={'IWO_ATLAS_VIEWERS': 'kill'})
    sub('IWO_ATLAS_JOB=0', 1, env={'IWO_ATLAS_JOB': '0'})
    sub('not isolated (no -I)', 1, args=('-B',))
    sub('wrong working directory', 1, cwd=HERE)
    base_py = getattr(sys, '_base_executable', sys.executable)
    sub(f'non-venv interpreter ({Path(base_py).name} outside the venv)', lambda rc: rc != 0, py=base_py)
    fake = TMP / 'fakeproc'; fake.mkdir(parents=True, exist_ok=True); tp = fake / 'tonyplot.exe'
    shutil.copyfile(Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32' / 'PING.EXE', tp)
    pr = subprocess.Popen([str(tp), '-n', '120', '127.0.0.1'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1.0)
    try: sub(f'fake process tonyplot.exe running (pid {pr.pid})', 1, show=('tonyplot.exe pid',))
    finally: pr.kill(); pr.wait(10)
    sl = subprocess.Popen([base_py, '-c', 'import time; time.sleep(120)', 'FAKE-run_campaign-cmdline-probe'], stdout=subprocess.DEVNULL); time.sleep(1.0)
    try: sub(f'python process with run_campaign in its command line (pid {sl.pid})', 1, show=('run_atlas / run_campaign',))
    finally: sl.kill(); sl.wait(10)
    sub('baseline again after the fake processes ended', 0)

    print('== in-process cases (one constant or input patched)')
    inproc('mismatched expected S2-11 deck hash', 1, lambda g: setattr(g, 'DECK', dict(g.DECK, **{'S2-11': '0' * 64})))
    inproc('mismatched expected S0-02-DOS2 deck hash', 1, lambda g: setattr(g, 'DECK', dict(g.DECK, **{'S0-02-DOS2': '0' * 64})))
    inproc('mismatched expected material hash', 1, lambda g: setattr(g, 'MATERIAL', '1' * 64))
    inproc('mismatched plan hash (dry build not run)', 1, lambda g: setattr(g, 'PLAN_SHA', '2' * 64))
    inproc('mismatched scripts/run_campaign.py hash', 1, lambda g: setattr(g, 'SCRIPTS', dict(g.SCRIPTS, **{'run_campaign.py': '3' * 64})))
    inproc('mismatched score_register.py hash', 1, lambda g: setattr(g, 'OTHER', {**g.OTHER, 'analysis_2026-10-10_campaign/score_register.py': '4' * 64}))
    inproc('fake process list: deckbuild.exe', 1, lambda g: setattr(g, 'list_processes', lambda: [(4242, 'deckbuild.exe', '')]))
    inproc('fake process list: atlas.exe + tonyplot3d.exe', 1, lambda g: setattr(g, 'list_processes', lambda: [(1, 'atlas.exe', ''), (2, 'tonyplot3d.exe', '')]))
    inproc('fake process list: python.exe running scripts/run_atlas.py', 1,
           lambda g: setattr(g, 'list_processes', lambda: [(4243, 'python.exe', r'python.exe scripts\run_atlas.py 2.0 x')]))
    inproc('fake process list: python3.13.exe (Store interpreter) running run_campaign', 1,
           lambda g: setattr(g, 'list_processes', lambda: [(4244, 'python3.13.exe', r'python3.13.exe scripts/run_campaign.py config/x.json')]))
    inproc('licence daemon only (sflm_monitord.exe) is allowed', 0, lambda g: setattr(g, 'list_processes', lambda: [(7, 'sflm_monitord.exe', '')]))

    def unreadable(): raise RuntimeError('simulated tasklist failure')
    inproc('process list unreadable (fail closed)', 1, lambda g: setattr(g, 'list_processes', unreadable))
    print('== unverifiable python processes (Codex 2026-10-13 record-note review)')
    gm = load(GATE, 'gate_merge')
    m1 = gm.merge_processes([['python3.13.exe', '4244', 'Console', '1', '9,999 K']], [{'ProcessId': 4244, 'Name': 'python3.13.exe', 'CommandLine': None}])
    expect('merge: tasklist python3.13.exe 4244 + CIM same PID CommandLine=null -> None', m1, [(4244, 'python3.13.exe', None)])
    m2 = gm.merge_processes([['python.exe', '4245', 'Console', '1', '9 K']], [{'ProcessId': 1, 'Name': 'System', 'CommandLine': None}])
    expect('merge: python PID in tasklist but missing from CIM -> None', [x for x in m2 if x[0] == 4245], [(4245, 'python.exe', None)])
    m3 = gm.merge_processes([['python.exe', '4246', 'Console', '1', '9 K']], [{'ProcessId': 4246, 'Name': 'notepad.exe', 'CommandLine': 'notepad x'}])
    expect('merge: image-name conflict for one PID -> None for both names', sorted(m3), [(4246, 'notepad.exe', None), (4246, 'python.exe', None)])
    m4 = gm.merge_processes([['python3.13.exe', '4247', 'Console', '1', '9 K']], [{'ProcessId': 4247, 'Name': 'python3.13.exe', 'CommandLine': 'python3.13.exe x.py'}])
    expect('merge: readable command line kept', m4, [(4247, 'python3.13.exe', 'python3.13.exe x.py')])
    inproc('gate: Codex counterexample (python3.13.exe 4244, CIM CommandLine null) stops as UNVERIFIABLE', 1,
           lambda g: setattr(g, 'list_processes', lambda: g.merge_processes([['python3.13.exe', '4244', 'Console', '1', '9 K']],
                                                                            [{'ProcessId': 4244, 'Name': 'python3.13.exe', 'CommandLine': None}])),
           show=('UNVERIFIABLE',))
    inproc('gate: python PID missing from CIM stops as UNVERIFIABLE', 1,
           lambda g: setattr(g, 'list_processes', lambda: g.merge_processes([['python.exe', '4245', 'Console', '1', '9 K']],
                                                                            [{'ProcessId': 1, 'Name': 'System', 'CommandLine': None}])))
    inproc('gate: python with a readable unrelated command line is allowed', 0,
           lambda g: setattr(g, 'list_processes', lambda: [(4248, 'python.exe', 'python.exe -m http.server')]))
    print('== in-process RUN_INDEX states (synthetic index and inventory)')
    def st(idx, inv): return lambda g: (setattr(g, 'INDEX', idx), setattr(g, 'INVENTORY', inv))
    base_inv = synth_inv([], 'inv_base.json')
    inproc('state B (rerun started) but rerun missing from the inventory', 1, st(synth_index([R76], 'idx_B.csv'), base_inv))
    inproc('state B (rerun started, inventoried): no --retry, DOS2 -> run_0077', 0, st(synth_index([R76], 'idx_B.csv'), synth_inv([I76], 'inv_B.json')),
           show=('GATE PASSED', 'This invocation', 'scripts/run_campaign.py'))
    inproc('state B with a wrong STARTED-row deck_sha256', 1, st(synth_index([dict(R76, deck_sha256='5' * 64)], 'idx_Bd.csv'), synth_inv([I76], 'inv_B.json')))
    inproc('state B with a STARTED note lacking model=', 1, st(synth_index([dict(R76, notes='STARTED points=1')], 'idx_Bn.csv'), synth_inv([I76], 'inv_B.json')))
    inproc('state B with inventory values other than registered', 1, st(synth_index([R76], 'idx_B.csv'), synth_inv([dict(I76, deck_sha256=DD2)], 'inv_Bw.json')))
    inproc('state C (both started): nothing to launch', 4, st(synth_index([R76, R77], 'idx_C.csv'), synth_inv([I76, I77], 'inv_C.json')))
    inproc('state D: DOS2 row without rerun row (order not followed)', 1,
           st(synth_index([dict(R77, run_id='run_0076')], 'idx_D.csv'), synth_inv([dict(I77, run_id='run_0076')], 'inv_D.json')))
    inproc('third S2-11 launch (two rerun ids)', 1, st(synth_index([R76, dict(R76, run_id='run_0077')], 'idx_3.csv'),
                                                       synth_inv([I76, dict(I76, run_id='run_0077')], 'inv_3.json')))
    inproc('another launch after run_0075 (ids shifted)', 1, st(synth_index([{'run_id': 'run_0076', 'label': 'c10_s2_04_2p0', 'notes': 'STARTED'}], 'idx_O.csv'), base_inv))

    print('== regress_sealed_aware.py guard paths (in-process, synthetic inventory)')
    for nm, inv, want in (('inventory without run_0075 -> STOP before reading', synth_inv([], 'w_empty.json'), 2),
                          ('inventory with a wrong deck_sha256 for run_0075', None, 1)):
        w = load(PKG / 'analysis_2026-10-10_campaign' / 'regress_sealed_aware.py', 'wrapper_under_test')
        if inv is not None:
            d = json.loads(inv.read_text()); d['runs'] = []; inv.write_text(json.dumps(d))
        else:
            d = json.loads((PKG / 'config' / 'sealed_runs.json').read_text()); d['runs'][0]['deck_sha256'] = '6' * 64
            inv = TMP / 'w_bad.json'; inv.write_text(json.dumps(d))
        w.INVENTORY = inv; os.chdir(PKG); buf = io.StringIO()
        with contextlib.redirect_stdout(buf): rc = w.main()
        for line in buf.getvalue().splitlines():
            if line.startswith('STOP') or line.startswith('run_0075') or line.startswith('identical'): print('       ' + line)
        expect(nm, rc, want)
    shutil.rmtree(TMP, ignore_errors=True)
    print(f'{sum(results)}/{len(results)} ok')
    sys.exit(0 if all(results) else 1)
