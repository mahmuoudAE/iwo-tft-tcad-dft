#!/usr/bin/env python3
"""Self-test of the 2026-10-13 runner changes (S2_RUNNER_GATES_2026-10-13.md). NO simulator call and NO ATLAS launch.

Everything runs in a temporary folder: synthetic run directories (score_register._st_run, the frozen scorer's own selftest writer),
a temporary RUN_INDEX.csv, and harmless stand-in processes (cmd.exe, python, PING.EXE as the 'viewer'). Nothing under results/runs or
results/sealed is read; the real RUN_INDEX.csv is never read or written.
Real launch paths are blocked twice: subprocess.Popen refuses any executable named deckbuild / dbascii / atlas* / tonyplot / sflm or any
argument under C:/sedatools (RealLaunchAttempted), and the campaign tests replace run_campaign.execute / execute_output / execute_strip
by fakes.
  A  run_campaign gates: plans without gates behave exactly as the committed HEAD run_campaign.py (launch calls, RUN_INDEX rows, summary,
     console); FIRED / UNRESOLVED / continue / hold / --ack-gate with a cited audit / failed checkpoint / external control / refusals;
     decisions bound to declaration, scorer and input/evidence hashes (Codex blocker 2); the state-only surface (blocker 3); the generated
     campaign_C10_DIAG.json walked through all four gates; value-free gate output.
  B  run_atlas.launch + proc_guard: output identical to communicate(); the run_0075 hang pattern reproduced with the former code (blocked)
     and bounded with the new code; viewer policy record (default) / kill; job disabled -> still bounded; a still-parented KEEP child
     survives; a hanging cleanup command is bounded and an error does not stop the cleanup (blocker 1).
  C  run_atlas.execute / execute_strip with a fake simulator: post_export_hang from deckbuild.out itself, diagnostic only; exit_code stays
     'timeout'; seal_notes gives a status-only RUN_INDEX note.
  python analysis_2026-10-10_campaign/runner_selftest_2026-10-13.py
"""
import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent; PKG = HERE.parent
sys.path.insert(0, str(PKG / 'scripts')); sys.path.insert(0, str(HERE))


# ---------------------------------------------------------------- real launches blocked
class RealLaunchAttempted(RuntimeError):
    pass


_RealPopen = subprocess.Popen


class GuardedPopen(_RealPopen):
    def __init__(self, args, *a, **k):
        al = [str(x) for x in (args if isinstance(args, (list, tuple)) else [args])]
        exe = Path(al[0].strip('"')).name.lower() if al else ''
        if re.search(r'deckbuild|dbascii|^atlas|tonyplot|sflm', exe) or any('sedatools' in x.lower() for x in al):
            raise RealLaunchAttempted(' '.join(al))
        super().__init__(args, *a, **k)


subprocess.Popen = GuardedPopen

import campaign_gates as cg   # noqa: E402
import proc_guard as pg       # noqa: E402
import run_atlas as ra        # noqa: E402
import run_campaign as rc     # noqa: E402
import score_register as sr   # noqa: E402  (frozen; used only for its synthetic run-directory writer _st_run)

RESULTS = []
LIM = {2.0: 4.60552e-16, 6.3: 1.53e-14, 13.2: 6.6e-13}   # 7.1 KCL proxy per film (max(1e-17, 0.1 x floor))
GATE_RE = re.compile(r'^GATE [A-Za-z0-9._-]+ \[[A-Za-z0-9._:-]+\] after [A-Za-z0-9._-]+: (FIRED|NOT_FIRED|UNRESOLVED) -> (STOP|continue) \(decision [0-9a-f]{16}\)$')
ACK_RE = re.compile(r'^GATE [A-Za-z0-9._-]+: stop decision [0-9a-f]{16} acknowledged \(audit cited\); the plan continues$')
SCI = re.compile(r'\d\.?\d*[eE][-+]?\d+')
HEX = re.compile(r'\b[0-9a-f]{16,64}\b')   # decision ids and sha256 values are not numbers
PATHS = re.compile(r'"[^"]*[\\/][^"]*"')   # JSON strings holding a file path
REC_KEYS = {'gate', 'rule_id', 'after', 'test', 'inputs', 'state', 'evaluation', 'action', 'evaluated_utc', 'acknowledged_utc', 'decision_id',
            'binding_sha256', 'binding', 'ack_audit', 'superseded_by'}
METRIC_KEYS = {'active_rmse_dec', 'sub_rmse_dec', 'on_rmse_dec', 'Id3V_err_pct', 'sim', 'exp', 'max_kcl_A', 'strip', 'run_index_note', 'traceback',
               'mu_recalibrated', 'placeholders', 'overrides'}


ONLY = set()   # --only A17,B8: run only the cases whose id is listed


def case(name, fn):
    if ONLY and name.split(' ', 1)[0] not in ONLY: return
    t0 = time.time()
    try:
        ok, why = fn()
    except Exception as e:
        ok, why = False, f'{type(e).__name__}: {e}'
    RESULTS.append((name, bool(ok), why, time.time() - t0))
    print(('ok   ' if ok else 'FAIL ') + name + f'  [{time.time() - t0:.1f} s]' + (f'\n       {str(why)[:400]}' if why else ''), flush=True)


# ---------------------------------------------------------------- A: campaign sandbox
class Fakes:
    """fake run_atlas.execute / execute_output / execute_strip: a synthetic run directory and RUN_INDEX rows, never a launch"""
    def __init__(self, spec=None):
        self.spec = spec or {}; self.calls = []; self.kwargs = []

    def _make(self, mode, t, label, ov, k):
        self.calls.append((mode, float(t), label, tuple(ov))); self.kwargs.append(dict(k))
        sp = self.spec.get(label, {}); t = float(t)
        with ra._LOCK: rid = ra.next_id()
        name = f'{rid}_{label}'; od = f'results/runs/{name}'
        ra.append({'run_id': rid, 'timestamp_utc': 'T0', 'thickness_nm': t, 'label': label, 'output_dir': od, 'notes': 'STARTED fake (selftest)'})
        if sp.get('metrics'):   # what a real launch prints (sealed in state-only plans)
            print('{"run_id": "%s", "active_rmse_log10": 0.777123}' % rid); sys.stderr.write('RuntimeWarning: 0.888456\n')
        if sp.get('raise'):
            ra.append({'run_id': rid, 'timestamp_utc': 'T1', 'thickness_nm': t, 'label': label, 'output_dir': od, 'exit_code': 1, 'notes': 'FAKE FAILURE'})
            raise RuntimeError(f'{rid}: fake launch failure 0.999321 (selftest)')
        g = sr._GRID; i_d = sp.get('i_d', np.minimum(10.0 ** (-9 + 4.0 * (g - 0.5)), 1e-6)); i_g = sp.get('i_g', np.zeros(len(g)))
        sr._st_run(ra.RUNS, name, rid, label, t, np.broadcast_to(i_d, g.shape).copy(), i_g=np.broadcast_to(i_g, g.shape).copy(), lim=LIM.get(t, 1e-17))
        if sp.get('metrics'): add_metrics(ra.RUNS / name)
        ra.append({'run_id': rid, 'timestamp_utc': 'T1', 'thickness_nm': t, 'label': label, 'output_dir': od, 'exit_code': 0, 'converged': 'yes', 'notes': 'FAKE OK'})
        return ra.RUNS / name

    def execute(self, t, label, ov, timeout=None, **k): return self._make('transfer', t, label, ov, k)
    def execute_strip(self, t, label, ov, timeout=None, **k): return self._make('strip', t, label, ov, k)
    def execute_output(self, t, label, ov, vgs, vd, timeout=None, **k): return self._make('output', t, label, ov, k)


def add_metrics(d):
    """synthetic fit metrics (marker values 0.4321 / 12.3456 / 0.7654) so the state-only tests can look for leaks"""
    ex = json.loads((Path(d) / 'execution.json').read_text())
    ex['fit_metrics'] = {'regions': {'active': {'rmse_log10': 0.4321}, 'subthreshold': {'rmse_log10': 0.4321}, 'on': {'rmse_log10': 0.4321}}, 'on_error_3V_percent': 12.3456}
    ex['device_metrics_sim'] = {'Ion_A_per_um': 0.7654}; ex['device_metrics_exp'] = {'Ion_A_per_um': 0.7654}
    (Path(d) / 'execution.json').write_text(json.dumps(ex))


@contextlib.contextmanager
def sandbox(module, fakes):
    tmp = Path(tempfile.mkdtemp(prefix='iwo_runner_selftest_')); root = tmp / 'pkg'
    for d in ('results/runs', 'results/campaigns', 'config'): (root / d).mkdir(parents=True, exist_ok=True)
    shutil.copy(PKG / 'config' / 'solver.yaml', root / 'config' / 'solver.yaml')
    saved_ra = (ra.INDEX, ra.RUNS, ra.ROOT); saved_m = (module.ROOT, module.execute, module.execute_output, module.execute_strip)
    ra.INDEX, ra.RUNS, ra.ROOT = root / 'results' / 'RUN_INDEX.csv', root / 'results' / 'runs', root
    module.ROOT, module.execute, module.execute_output, module.execute_strip = root, fakes.execute, fakes.execute_output, fakes.execute_strip
    try:
        yield root
    finally:
        ra.INDEX, ra.RUNS, ra.ROOT = saved_ra; module.ROOT, module.execute, module.execute_output, module.execute_strip = saved_m
        shutil.rmtree(tmp, ignore_errors=True)


def run_main(module, argv):
    buf = io.StringIO(); code = 0; old = sys.argv; sys.argv = ['run_campaign.py'] + [str(a) for a in argv]
    try:
        with contextlib.redirect_stdout(buf): module.main()
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
        if isinstance(e.code, str): buf.write(e.code + '\n')
    finally:
        sys.argv = old
    return code, buf.getvalue()


def head_module():
    """the committed (HEAD) scripts/run_campaign.py, loaded as a separate module (None if git is unavailable)"""
    try:
        src = subprocess.run(['git', '-C', str(PKG), 'show', 'HEAD:scripts/run_campaign.py'], capture_output=True, text=True, check=True).stdout
    except Exception:
        return None
    if 'gates' in src: return None   # HEAD already contains this change: no baseline to compare with
    p = Path(tempfile.mkdtemp(prefix='iwo_head_')) / 'run_campaign_head.py'; p.write_text(src)
    spec = importlib.util.spec_from_file_location('run_campaign_head', p); m = importlib.util.module_from_spec(spec); before = list(sys.path)
    spec.loader.exec_module(m); sys.path[:] = before
    return m


def write_plan(d, stem, plan):
    p = Path(d) / f'{stem}.json'; p.write_text(json.dumps(plan, indent=1)); return p


def norm_console(s, root=None):
    """wall-clock seconds and the (per-sandbox) temporary root are the only parts allowed to differ"""
    s = re.sub(r'"wall_s": [0-9.]+', '"wall_s": X', s)
    return s.replace(str(root), '<ROOT>') if root is not None else s


def norm_summary(p):
    j = json.loads(Path(p).read_text())
    for r in j.get('runs', []): r.pop('wall_s', None); r.pop('traceback', None)
    return j


def gate(gid, after, test='hc_nominal', runs=None, on_unresolved='continue', **kw):
    g = {'id': gid, 'rule_id': 'S2-STOP-NULL', 'after': after, 'test': test, 'runs': runs or {'run': {'entry': after}}, 'on_fired': 'stop',
         'on_unresolved': on_unresolved, 'scorer': 'analysis_2026-10-10_campaign/score_register.py', 'scorer_sha256': sr_sha()}
    g.update(kw); return g


def sr_sha(): return cg.sha256(PKG / 'analysis_2026-10-10_campaign' / 'score_register.py')


def value_free(console, root):
    """every gate console line matches the fixed format; no scientific-notation number in gate/STOP lines; records hold only allowed keys"""
    bad = [l for l in console.splitlines() if l.startswith('GATE ') and not (GATE_RE.match(l) or ACK_RE.match(l))]
    bad += [l for l in console.splitlines() if (l.startswith('GATE ') or l.startswith('STOP: gate')) and SCI.search(HEX.sub('', l))]
    for f in (Path(root) / 'results' / 'campaigns').glob('*.json'):
        for r in json.loads(f.read_text()).get('gates', []):
            if set(r) - REC_KEYS: bad.append(f'record keys {sorted(set(r) - REC_KEYS)}')
    for f in (Path(root) / 'results' / 'campaigns').glob('*.gates.jsonl'):
        for l in f.read_text().splitlines():
            r = json.loads(l)
            if set(r) - REC_KEYS: bad.append(f'jsonl keys {sorted(set(r) - REC_KEYS)}')
            if SCI.search(HEX.sub('', PATHS.sub('""', l))): bad.append('number in jsonl')   # file paths (random temp names) are not values
    return bad


def last_stop(summary_path):
    return [r for r in json.loads(Path(summary_path).read_text())['gates'] if r['action'] == 'stop'][-1]


def write_audit(d, rec, cite=True):
    """a completed-audit file naming the gate and (if cite) its decision id"""
    p = Path(tempfile.mkdtemp(prefix='iwo_audit_', dir=d)) / f'AUDIT_{rec["gate"]}.md'
    p.write_text(f'Audit of gate {rec["gate"]}' + (f', decision {rec["decision_id"]}' if cite else '') + ': KCL, CR.TOLER and deck audited (selftest).\n')
    return p


PLAIN = {'campaign': 'T_plain', 'purpose': 'runner selftest (no gates)', 'runs': [
    {'id': 'A', 'thickness': 2.0, 'label': 't_a_2p0', 'overrides': ['solver.tmun=0']},
    {'id': 'B', 'thickness': 13.2, 'label': 't_b_13p2', 'mode': 'strip', 'overrides': []},
    {'id': 'C', 'thickness': 6.3, 'label': 't_c_6p3', 'mode': 'output', 'output_vgs': [1, 2], 'overrides': []},
    {'id': 'D', 'thickness': 2.0, 'label': 't_d_2p0', 'overrides': []}]}
C10P = {'campaign': 'C10_T', 'purpose': 'runner selftest (C10 guards, no gates)', 'runs': [
    {'id': 'A', 'thickness': 2.0, 'label': 'c10_ta_2p0', 'overrides': []},
    {'id': 'B', 'thickness': 2.0, 'label': 'c10_tb_2p0', 'overrides': []},
    {'id': 'C', 'thickness': 13.2, 'label': 'c10_tc_13p2', 'overrides': []}]}


def ungated_identical():
    head = head_module()
    if head is None: return True, 'SKIPPED: no git HEAD baseline without gates'
    out = {}
    pd = Path(tempfile.mkdtemp(prefix='iwo_plans_'))
    pp, pc = write_plan(pd, 'campaign_T_plain', PLAIN), write_plan(pd, 'campaign_C10_T', C10P)
    for tag, mod in (('head', head), ('new', rc)):
        f = Fakes({'t_d_2p0': {'raise': True}})
        with sandbox(mod, f) as root:
            ra.append({'run_id': 'run_0001', 'timestamp_utc': 'T', 'thickness_nm': 2.0, 'label': 'c10_tb_2p0', 'output_dir': 'results/runs/run_0001_gone', 'notes': 'STARTED earlier'})
            r1 = run_main(mod, [pp]); r2 = run_main(mod, [pp]); r3 = run_main(mod, [pc]); r4 = run_main(mod, [pc, '--retry', 'B'])
            out[tag] = {'codes': [r[0] for r in (r1, r2, r3, r4)], 'console': [norm_console(r[1], root) for r in (r1, r2, r3, r4)], 'calls': list(f.calls),
                        'index': ra.INDEX.read_text(), 'summaries': {p.name: norm_summary(p) for p in sorted((root / 'results' / 'campaigns').glob('*.json'))},
                        'files': sorted(p.name for p in (root / 'results' / 'campaigns').iterdir())}
    diff = [k for k in out['head'] if out['head'][k] != out['new'][k]]
    if 'console' in diff:
        a, b = '\n'.join(out['head']['console']).splitlines(), '\n'.join(out['new']['console']).splitlines()
        first = next((f'{x!r} vs {y!r}' for x, y in zip(a, b) if x != y), f'{len(a)} vs {len(b)} lines')
        return False, f'differs in {diff}; first console difference: {first}'
    return not diff, f'differs in {diff}' if diff else f'{len(out["new"]["calls"])} fake launches in 4 invocations, identical'


def gated_run(spec, plan_runs, gates_, steps, pre=None, stem='campaign_T_gates', extra=None, edit=None):
    """run a gated plan once per step in one sandbox; a step is an argv list or a function(ctx) -> argv list (ctx: root, summary path,
    plan path, plan dict, temp dir) that may also rewrite the plan; returns (codes, consoles, calls per run, summary, jsonl lines, bad, ctx)"""
    f = Fakes(spec); pd = Path(tempfile.mkdtemp(prefix='iwo_plans_'))
    plan = {'campaign': stem.replace('campaign_', ''), 'purpose': 'runner selftest (gates)', 'runs': plan_runs, 'gates': gates_, **(extra or {})}
    p = write_plan(pd, stem, plan); codes, cons, calls = [], [], []
    with sandbox(rc, f) as root:
        ctx = {'root': root, 'summary': root / 'results' / 'campaigns' / f'{stem}.json', 'plan_path': p, 'plan': plan, 'dir': pd, 'fakes': f}
        if pre: pre()
        for st in steps:
            argv = st(ctx) if callable(st) else st
            n0 = len(f.calls); c, o = run_main(rc, [p] + argv); codes.append(c); cons.append(o); calls.append([x[2] for x in f.calls[n0:]])
        s = ctx['summary']; summ = json.loads(s.read_text()) if s.exists() else {}
        jl = s.with_name(s.stem + '.gates.jsonl'); jlines = jl.read_text().splitlines() if jl.exists() else []
        bad = value_free('\n'.join(cons), root)
        ctx['files'] = sorted(str(x.relative_to(root)).replace('\\', '/') for x in root.rglob('*') if x.is_file())
        ctx['texts'] = {str(x.relative_to(root)).replace('\\', '/'): x.read_text(errors='replace') for x in root.rglob('*') if x.is_file() and x.suffix in ('.json', '.jsonl', '.log', '.csv')}
    return codes, cons, calls, summ, jlines, bad, ctx


def ack(gid):
    """step: acknowledge the last stop decision of gid with a valid audit file"""
    def st(ctx):
        r = [x for x in json.loads(ctx['summary'].read_text())['gates'] if x['gate'] == gid and x['action'] == 'stop'][-1]
        return ['--ack-gate', gid, '--ack-audit', str(write_audit(ctx['dir'], r))]
    return st


R3 = [{'id': 'A', 'thickness': 2.0, 'label': 'g_a_2p0', 'overrides': []}, {'id': 'B', 'thickness': 2.0, 'label': 'g_b_2p0', 'overrides': []},
      {'id': 'C', 'thickness': 13.2, 'label': 'g_c_13p2', 'overrides': []}]
BIG_IG = {'g_a_2p0': {'i_g': -1e-12}}   # |I_G(-3 V)| = 1e-12 A/um > proxy 4.6e-16 and bound 4.6e-17 at 2.0 nm -> FAIL


def t_fired():
    codes, cons, calls, s, jl, bad, _ = gated_run(BIG_IG, R3, [gate('G1', 'A')], [[]])
    g = s['gates'][0]
    ok = codes == [3] and calls == [['g_a_2p0']] and g['state'] == 'FIRED' and g['action'] == 'stop' and len(jl) == 1 and not bad \
        and 'CAMPAIGN STOPPED BY GATE' in cons[0] and '1e-12' not in cons[0] and len(g['decision_id']) == 16
    return ok, f'codes {codes} calls {calls} state {g["state"]} decision {g["decision_id"]} bad {bad}'


def t_unresolved_continue():
    codes, cons, calls, s, jl, bad, _ = gated_run({}, R3, [gate('G1', 'A', on_unresolved='continue')], [[]])
    g = s['gates'][0]
    return codes == [0] and calls == [['g_a_2p0', 'g_b_2p0', 'g_c_13p2']] and g['state'] == 'UNRESOLVED' and g['action'] == 'continue' and not bad, \
        f'codes {codes} calls {calls} state {g["state"]}'


def t_unresolved_stop():
    codes, cons, calls, s, jl, bad, _ = gated_run({}, R3, [gate('G1', 'A', on_unresolved='stop')], [[]])
    g = s['gates'][0]
    return codes == [3] and calls == [['g_a_2p0']] and g['state'] == 'UNRESOLVED' and g['action'] == 'stop' and not bad, f'codes {codes} calls {calls}'


def t_hold_and_ack():
    """a stop holds; --ack-gate without an audit, with --ack-audit alone, or with an audit not naming the decision is refused; a valid
    audit citation acknowledges exactly that decision (path, sha256, decision recorded)"""
    def no_cite(ctx): return ['--ack-gate', 'G1', '--ack-audit', str(write_audit(ctx['dir'], last_stop(ctx['summary']), cite=False))]
    steps = [[], [], ['--ack-gate', 'G1'], ['--ack-audit', 'x.md'], no_cite, ack('G1'), []]
    codes, cons, calls, s, jl, bad, _ = gated_run(BIG_IG, R3, [gate('G1', 'A')], steps)
    g = s['gates'][0]; au = g.get('ack_audit') or {}
    ok = codes == [3, 3, 3, 1, 3, 0, 0] and calls == [['g_a_2p0'], [], [], [], [], ['g_b_2p0', 'g_c_13p2'], []] and len(s['gates']) == 1 \
        and 'nothing launched' in cons[1] and 'must cite the completed audit' in cons[2] and 'needs --ack-gate' in cons[3] \
        and 'must name the gate G1 and its decision' in cons[4] and au.get('acknowledges_decision') == g['decision_id'] and len(au.get('sha256', '')) == 64 and not bad
    return ok, f'codes {codes} calls {calls} records {len(s["gates"])} ack {au}'


def t_after_last_entry():
    codes, cons, calls, s, jl, bad, _ = gated_run({'g_c_13p2': {'i_g': -1e-10}}, R3, [gate('G3', 'C')], [[]])
    return codes == [3] and calls == [['g_a_2p0', 'g_b_2p0', 'g_c_13p2']] and s['gates'][0]['state'] == 'FIRED' and not bad, f'codes {codes} calls {calls}'


def t_generation_external_control():
    pre = lambda: sr._st_run(ra.RUNS, 'run_0001_ctrl', 'run_0001', 'ext_ctrl_2p0', 2.0, np.full(len(sr._GRID), 1e-19), lim=LIM[2.0]) and \
        ra.append({'run_id': 'run_0001', 'timestamp_utc': 'T', 'thickness_nm': 2.0, 'label': 'ext_ctrl_2p0', 'output_dir': 'results/runs/run_0001_ctrl', 'notes': 'STARTED'})
    spec = {'g_a_2p0': {'i_d': 1e-15}}   # resolved 1e-15 vs 1e-19 (one-sided) -> lower bound >> 1e-20 -> FAIL
    G = [gate('GG', 'A', test='hc_generation', runs={'run': {'entry': 'A'}, 'control': {'run_id': 'run_0001', 'label': 'ext_ctrl_2p0'}})]
    c1, _, k1, s1, _, b1, _ = gated_run(spec, R3, G, [[]], pre=pre)
    Gm = [gate('GG', 'A', test='hc_generation', runs={'run': {'entry': 'A'}, 'control': {'run_id': 'run_0001', 'label': 'WRONG'}}, on_unresolved='stop')]
    c2, _, k2, s2, _, b2, _ = gated_run(spec, R3, Gm, [[]], pre=pre)
    ok = c1 == [3] and s1['gates'][0]['state'] == 'FIRED' and s1['gates'][0]['inputs'] == {'run': 'run_0002', 'control': 'run_0001'} \
        and c2 == [3] and s2['gates'][0]['state'] == 'UNRESOLVED' and s2['gates'][0]['evaluation'] == 'missing_run' and not (b1 or b2)
    return ok, f'{c1} {s1["gates"][0]["state"]} {s1["gates"][0]["inputs"]} | {c2} {s2["gates"][0]["evaluation"]}'


def t_failed_checkpoint():
    codes, cons, calls, s, jl, bad, _ = gated_run({'g_a_2p0': {'raise': True}}, R3, [gate('G1', 'A', on_unresolved='stop')], [[]])
    g = s['gates'][0]
    return codes == [3] and calls == [['g_a_2p0']] and g['state'] == 'UNRESOLVED' and g['evaluation'] == 'missing_run' and not bad, f'{codes} {g["state"]} {g["evaluation"]}'


def t_retry_reevaluates():
    def retry(ctx): return ack('G1')(ctx) + ['--retry', 'A']
    codes, cons, calls, s, jl, bad, _ = gated_run(BIG_IG, R3, [gate('G1', 'A')], [[], retry])
    ins = [r['inputs']['run'] for r in s['gates']]
    return codes == [3, 3] and calls == [['g_a_2p0'], ['g_a_2p0']] and ins == ['run_0001', 'run_0002'] and s['gates'][0].get('superseded_by') == s['gates'][1]['decision_id'] \
        and not bad, f'{codes} {calls} {ins}'


def t_rebinding():
    """Codex blocker 2: an old UNRESOLVED/continue decision does not survive (a) a policy change to stop with new resolution evidence,
    (b) a change of an input run's files, (c) a legacy record without a binding; each gives a new evaluation before anything proceeds"""
    def policy_and_evidence(ctx):
        ev = ctx['dir'] / 'pair_evidence.json'; ev.write_text('{"test": "not a resolution pair (selftest)"}')
        ctx['plan']['gates'][0].update(on_unresolved='stop', kwargs={'ig_given': 1e-18, 'ig_source': str(ev)}); write_plan(ctx['dir'], 'campaign_T_gates', ctx['plan'])
        return []
    def touch_input(ctx):
        rd = ctx['root'] / json.loads(ctx['summary'].read_text())['runs'][0]['run_dir'] / 'terminal_currents.csv'; rd.write_text(rd.read_text() + '\n')
        return ack('G1')(ctx)
    def legacy(ctx):   # the decision as the earlier (unbound) code wrote it: no binding, no decision id
        j = json.loads(ctx['summary'].read_text())
        j['gates'] = [{k: v for k, v in r.items() if k not in ('binding', 'binding_sha256', 'decision_id')} for r in j['gates']]
        ctx['summary'].write_text(json.dumps(j)); return []
    c1, _, k1, s1, _, b1, _ = gated_run({}, R3, [gate('G1', 'A', on_unresolved='continue')], [[], policy_and_evidence, touch_input])
    d1 = [(r['action'], r.get('superseded_by') is not None) for r in s1['gates']]
    bsh = [r['binding']['evidence_sha256'] for r in s1['gates']]
    c2, _, k2, s2, _, b2, _ = gated_run({}, R3, [gate('G1', 'A', on_unresolved='continue')], [[], legacy])
    ok = c1 == [0, 3, 3] and k1 == [['g_a_2p0', 'g_b_2p0', 'g_c_13p2'], [], []] and d1 == [('continue', True), ('stop', True), ('stop', False)] \
        and bsh[0] == {} and len(bsh[1]) == 1 and c2 == [0, 0] and k2 == [['g_a_2p0', 'g_b_2p0', 'g_c_13p2'], []] and len(s2['gates']) == 2 \
        and s2['gates'][0].get('superseded_by') == s2['gates'][1]['decision_id'] and not (b1 or b2)
    return ok, f'(a,b) codes {c1} decisions {d1}; (c) legacy codes {c2} records {len(s2["gates"])}'


def t_ack_bound_to_decision():
    """an acknowledgement covers exactly its decision: after a declaration change the gate is re-evaluated and stops again"""
    def change_decl(ctx):
        ctx['plan']['gates'][0]['note'] = 'declaration edited after the acknowledgement'; write_plan(ctx['dir'], 'campaign_T_gates', ctx['plan']); return []
    codes, cons, calls, s, jl, bad, _ = gated_run(BIG_IG, R3, [gate('G1', 'A')], [[], ack('G1'), change_decl, [], ack('G1')])
    g = s['gates']
    ok = codes == [3, 0, 3, 3, 0] and calls == [['g_a_2p0'], ['g_b_2p0', 'g_c_13p2'], [], [], []] and len(g) == 2 and g[0]['decision_id'] != g[1]['decision_id'] \
        and g[0]['ack_audit']['acknowledges_decision'] == g[0]['decision_id'] and g[1]['ack_audit']['acknowledges_decision'] == g[1]['decision_id'] and not bad
    return ok, f'codes {codes} calls {calls} decisions {[r["decision_id"] for r in g]}'


def t_state_only():
    """Codex blocker 3 / D7: console, campaign summary and RUN_INDEX-facing record are state-only; the full record (metrics, reused-run
    RUN_INDEX note, error text, launch prints) is in the sealed sidecar; launches get seal_notes=True; resume reads the sidecar"""
    runs = [{'id': 'A', 'thickness': 2.0, 'label': 'c10_sa_2p0', 'overrides': []}, {'id': 'B', 'thickness': 2.0, 'label': 'c10_sb_2p0', 'overrides': []},
            {'id': 'C', 'thickness': 2.0, 'label': 'c10_sc_2p0', 'overrides': []}]
    spec = {'c10_sa_2p0': {'metrics': True}, 'c10_sc_2p0': {'raise': True, 'metrics': True}}

    def pre():   # B: an earlier successful launch of the same entry, with metrics in execution.json and in its RUN_INDEX note (reused, not launched)
        e = runs[1]; d = ra.RUNS / 'run_0001_c10_sb_2p0'
        sr._st_run(ra.RUNS, d.name, 'run_0001', e['label'], 2.0, np.minimum(10.0 ** (-9 + 4.0 * (sr._GRID - 0.5)), 1e-6), lim=LIM[2.0]); add_metrics(d)
        ex = json.loads((d / 'execution.json').read_text()); ex['overrides'] = []; ex['mode'] = 'transfer'; (d / 'execution.json').write_text(json.dumps(ex))
        (d / 'material_model_used.json').write_text(rc.current_material_text([])); (d / 'device.in').write_text(rc.current_deck_text(e, []))
        for n in ('STARTED earlier', 'active RMSE 0.4321 dec; Id(3V) +12.3456%'):
            ra.append({'run_id': 'run_0001', 'timestamp_utc': 'T', 'thickness_nm': 2.0, 'label': e['label'], 'output_dir': f'results/runs/{d.name}', 'notes': n})
    so = {'state_only': {'sealed_dir': 'results/sealed/campaigns'}}

    def resume(ctx):   # the sidecar after the first invocation (a C10 resume replaces C's error record by its 'already launched' record)
        ctx['full_1'] = (ctx['root'] / 'results' / 'sealed' / 'campaigns' / 'campaign_C10_TS.full.json').read_text(); return []
    codes, cons, calls, s, jl, bad, ctx = gated_run(spec, runs, [gate('G1', 'A', on_unresolved='continue')], [[], resume], pre=pre, stem='campaign_C10_TS', extra=so)
    pub = ctx['texts'].get('results/campaigns/campaign_C10_TS.json', ''); full = ctx.get('full_1', '') + ctx['texts'].get('results/sealed/campaigns/campaign_C10_TS.full.json', '')
    log = ctx['texts'].get('results/sealed/campaigns/campaign_C10_TS.console.log', '')
    markers = ('0.4321', '12.3456', '0.7654', '0.777123', '0.888456', '0.999321')
    leaks = [m for m in markers if m in '\n'.join(cons) or m in pub]
    pub_keys = {k for r in s['runs'] for k in r} & METRIC_KEYS
    ok = codes == [0, 0] and calls == [['c10_sa_2p0', 'c10_sc_2p0'], []] and not leaks and not pub_keys and 'placeholders' not in s \
        and all(m in full for m in ('0.4321', '12.3456', '0.999321')) and '0.777123' in log and '0.888456' in log \
        and all(k == {'seal_notes': True} for k in ctx['fakes'].kwargs) and s['surface'].startswith('STATE-ONLY') \
        and [r['state'] for r in s['runs']] == ['completed', 'reused', 'failed'] and not bad
    return ok, f'codes {codes} calls {calls} leaks {leaks} metric keys in public summary {sorted(pub_keys)} states {[r["state"] for r in s["runs"]]}'


def t_evidence_freshness():
    """Codex rev-2 item 2 (regression): the binding covers the CURRENT files of both run directories a cited resolution pair references,
    missing-file states included: changing a referenced execution.json, then deleting a referenced file, with PAIR.json unchanged, each
    gives a new evaluation (a cached decision never survives stale evidence)"""
    ev = Path(tempfile.mkdtemp(prefix='iwo_evidence_')); g_ = sr._GRID
    a = sr._st_run(ev, 'pair_run_a', 'run_9101', 'pair_a_2p0', 2.0, np.full(len(g_), 1e-12), lim=LIM[2.0])
    b = sr._st_run(ev, 'pair_run_b', 'run_9102', 'pair_b_2p0', 2.0, np.full(len(g_), 1e-12), lim=LIM[2.0])
    pair = ev / 'pair.json'; pair.write_text(json.dumps({'test': sr.PAIR_TEST, 'column': 'ig_raw_A', 'run_dir': a, 'ref_dir': b}))
    G = [gate('G1', 'A', on_unresolved='continue', kwargs={'ig_given': 1e-18, 'ig_source': str(pair)})]

    def edit_exec(ctx):
        p = Path(a) / 'execution.json'; j = json.loads(p.read_text()); j['edited_after_the_decision'] = True; p.write_text(json.dumps(j)); return []

    def delete_csv(ctx): (Path(b) / 'terminal_currents.csv').unlink(); return []
    codes, cons, calls, s, jl, bad, _ = gated_run({}, R3, G, [[], edit_exec, delete_csv])
    sup = [r.get('superseded_by') is not None for r in s['gates']]
    refs = [((r['binding']['evidence_sha256'].get(str(pair)) or {}).get('referenced_runs') or {}) for r in s['gates']]
    missing = refs[-1].get('ref_dir', {}).get('files_sha256', {}).get('terminal_currents.csv', 'absent') if refs else 'absent'
    ok = codes == [0, 0, 0] and len(s['gates']) == 3 and sup == [True, True, False] and missing is None and not bad
    return ok, f'codes {codes}; decisions {len(s["gates"])}; superseded {sup}; deleted file recorded as {missing!r}'


def t_superseded_not_reused():
    """Codex rev-2 item 3 (regression): A = UNRESOLVED/stop (unacknowledged); a declaration change gives B (continue), superseding A; the
    declaration is then restored to A's: only the ACTIVE decision may be reused, so the gate is evaluated again and stops"""
    def to_continue(ctx):
        ctx['plan']['gates'][0]['on_unresolved'] = 'continue'; write_plan(ctx['dir'], 'campaign_T_gates', ctx['plan']); return []

    def restore(ctx):
        ctx['plan']['gates'][0]['on_unresolved'] = 'stop'; write_plan(ctx['dir'], 'campaign_T_gates', ctx['plan']); return []
    codes, cons, calls, s, jl, bad, _ = gated_run({}, R3, [gate('G1', 'A', on_unresolved='stop')], [[], to_continue, restore])
    g = s['gates']; acts = [r['action'] for r in g]
    ok = codes == [3, 0, 3] and calls == [['g_a_2p0'], ['g_b_2p0', 'g_c_13p2'], []] and acts == ['stop', 'continue', 'stop'] \
        and g[0]['binding_sha256'] == g[2]['binding_sha256'] and len({r['decision_id'] for r in g}) == 3 and not bad
    return ok, f'codes {codes}; actions {acts}; decision ids unique {len({r.get("decision_id") for r in g}) == len(g)}'


def t_state_only_refusals():
    pd = Path(tempfile.mkdtemp(prefix='iwo_plans_')); f = Fakes(); out = []
    with sandbox(rc, f) as root:
        for nm, so in (('outside results/sealed', {'sealed_dir': 'results/campaigns'}), ('parent dir', {'sealed_dir': 'results/sealed/../x'}),
                       ('extra key', {'sealed_dir': 'results/sealed/c', 'print': True})):
            p = write_plan(pd, 'campaign_T_so', {'campaign': 'T_so', 'runs': R3, 'state_only': so}); c, o = run_main(rc, [p]); out.append((nm, c, 'state_only refused' in o))
        p = write_plan(pd, 'campaign_T_so', {'campaign': 'T_so', 'runs': R3, 'state_only': {'sealed_dir': 'results/sealed/c'}})
        c, o = run_main(rc, [p, '--workers', '2']); out.append(('workers 2', c, 'state_only refused' in o))
    bad = [x for x in out if not (x[1] == 1 and x[2])]
    return not bad and not f.calls, f'not refused: {bad}'


def t_refusals():
    pd = Path(tempfile.mkdtemp(prefix='iwo_plans_')); f = Fakes(); out = []
    variants = {'unknown test': [gate('G1', 'A', test='hc_mesh')], 'after not in plan': [gate('G1', 'Z')],
                'entry after checkpoint': [gate('G1', 'A', runs={'run': {'entry': 'B'}})], 'on_fired continue': [gate('G1', 'A', on_fired='continue')],
                'no on_unresolved': [{k: v for k, v in gate('G1', 'A').items() if k != 'on_unresolved'}], 'scorer hash differs': [gate('G1', 'A', scorer_sha256='0' * 64)],
                'value-bearing rule id': [gate('G1', 'A', rule_id='I_G 1e-12')], 'unknown key': [gate('G1', 'A', print_values=True)], 'empty list': [],
                'rule_basis not text': [gate('G1', 'A', rule_basis=1)]}
    with sandbox(rc, f) as root:
        for nm, gl in variants.items():
            p = write_plan(pd, 'campaign_T_ref', {'campaign': 'T_ref', 'runs': R3, 'gates': gl}); c, o = run_main(rc, [p]); out.append((nm, c, 'gates refused' in o))
        p = write_plan(pd, 'campaign_T_ref', {'campaign': 'T_ref', 'runs': R3, 'gates': [gate('G1', 'A')]}); c, o = run_main(rc, [p, '--workers', '2']); out.append(('workers 2', c, 'gates refused' in o))
        p = write_plan(pd, 'campaign_T_ref', {'campaign': 'T_ref', 'runs': R3}); c, o = run_main(rc, [p, '--ack-gate', 'G1']); out.append(('ack on ungated plan', c, 'gates refused' in o))
        nolaunch = not f.calls and not list((root / 'results' / 'runs').iterdir())
    bad = [x for x in out if not (x[1] == 1 and x[2])]
    return not bad and nolaunch, f'{len(out)} refusals; not refused: {bad}; launches {len(f.calls)}'


def t_child_output_discarded():
    """a scorer that prints currents: the parent keeps the state token only (fake scorer module, its own sha256)"""
    d = Path(tempfile.mkdtemp(prefix='iwo_fake_scorer_')); s = d / 'fake_scorer.py'
    s.write_text("import sys\ndef hc_nominal(run, **k):\n    print('I_G(-3 V) = 1.234e-12 A/um'); sys.stderr.write('7.7e-15\\n')\n"
                 "    return {'verdict': 'PROVISIONAL (resolution not demonstrated): FAIL', 'abs_IG_m3V_A_per_um': 1.234e-12}\n")
    g = {'test': 'hc_nominal', 'scorer': str(s), 'scorer_sha256': cg.sha256(s)}
    st = cg.evaluate(g, {'run': str(d)}); st2 = cg.evaluate({**g, 'scorer_sha256': '0' * 64}, {'run': str(d)})
    maps = [cg.state_of(v) for v in ('FAIL', 'PROVISIONAL (resolution not demonstrated): FAIL', 'PASS', 'below resolution (1e-21 A/um), consistent',
                                     'unresolved: below resolution (4.61e-16 A/um, not demonstrated)', 'invalid (x); never a pass', 'not demonstrated (x)', None)]
    ok = st == ('FIRED', 'ok') and st2 == ('UNRESOLVED', 'scorer_hash_mismatch') and maps == ['FIRED', 'FIRED', 'NOT_FIRED', 'NOT_FIRED', 'UNRESOLVED', 'UNRESOLVED', 'UNRESOLVED', 'UNRESOLVED']
    return ok, f'{st} {st2} {maps}'


def t_diag_walk():
    """the generated config/campaign_C10_DIAG.json (C10 guards, state-only surface) with fakes: four supervised stops, each resumed with a
    cited audit, then the remaining 13 entries; nothing of the synthetic metrics reaches the console or the ordinary summary"""
    plan = json.loads((PKG / 'config' / 'campaign_C10_DIAG.json').read_text()); assert plan.get('gates') and not cg.validate(plan) and plan.get('state_only')
    flat = np.full(len(sr._GRID), 1e-11)
    spec = {'c10_s2_11_2p0': {'metrics': True},
            'c10_s2_06_13p2': {'i_g': -1e-10},                 # 13.2 nm nominal: |I_G| 1e-10 > proxy 6.6e-13 -> FIRED
            'c10_s2_03_2p0': {'i_d': 1e-15},                    # 2.0 nm, S2-03 vs run_0061 (1e-19): anomaly checkpoint FIRED
            'c10_s2_01_13p2': {'i_d': flat}, 'c10_s2_02_13p2': {'i_d': flat}}   # identical -> within the 0.1 dec spread -> UNRESOLVED

    def pre():
        for k in range(1, 61): ra.append({'run_id': f'run_{k:04d}', 'timestamp_utc': 'T', 'thickness_nm': 2.0, 'label': f'pre_{k}', 'output_dir': '', 'notes': 'STARTED'})
        sr._st_run(ra.RUNS, 'run_0061_2p0_c10_s0_01_2p0', 'run_0061', 'c10_s0_01_2p0', 2.0, np.full(len(sr._GRID), 1e-19), lim=LIM[2.0])
        ra.append({'run_id': 'run_0061', 'timestamp_utc': 'T', 'thickness_nm': 2.0, 'label': 'c10_s0_01_2p0', 'output_dir': 'results/runs/run_0061_2p0_c10_s0_01_2p0', 'notes': 'STARTED'})
    steps = [[], ack('G-S2-04-nominal'), ack('G-S2-06-nominal'), ack('G-S2-03-anomaly'), ack('G-S2-01-generation')]
    codes, cons, calls, s, jl, bad, ctx = gated_run(spec, plan['runs'], plan['gates'], steps, pre=pre, stem='campaign_C10_DIAG',
                                                    extra={k: plan[k] for k in ('state_only',)})
    st = [(g['gate'], g['rule_id'], g['state'], g['action'], g['inputs']) for g in s['gates']]
    want = [('G-S2-04-nominal', 'S2-STOP-NULL', 'UNRESOLVED', 'stop', {'run': 'run_0063'}), ('G-S2-06-nominal', 'S2-STOP-NULL', 'FIRED', 'stop', {'run': 'run_0064'}),
            ('G-S2-03-anomaly', 'S2-ANOMALY-CARRIER', 'FIRED', 'stop', {'run': 'run_0065', 'control': 'run_0061'}),
            ('G-S2-01-generation', 'S2-STOP-NULL', 'UNRESOLVED', 'stop', {'run': 'run_0066', 'control': 'run_0067'})]
    leaks = [m for m in ('0.4321', '12.3456', '0.777123') if m in '\n'.join(cons) or m in ctx['texts'].get('results/campaigns/campaign_C10_DIAG.json', '')]
    ok = codes == [3, 3, 3, 3, 0] and calls[:4] == [['c10_s2_11_2p0', 'c10_s2_04_2p0'], ['c10_s2_06_13p2'], ['c10_s2_03_2p0'], ['c10_s2_01_13p2', 'c10_s2_02_13p2']] \
        and len(calls[4]) == 13 and st == want and all(g.get('ack_audit') for g in s['gates']) and not leaks \
        and 'results/sealed/campaigns/campaign_C10_DIAG.full.json' in ctx['files'] and not bad
    return ok, f'codes {codes}; calls {[len(c) for c in calls]}; gates {[(g[0], g[2]) for g in st]}; leaks {leaks}; bad {bad}'


# ---------------------------------------------------------------- B/C: launch, proc_guard, execute with a fake simulator
FAKE_CMD = r"""@echo off
set MODE=%1
goto %MODE%
:normal
echo line one
echo line two
echo err line 1>&2
exit /b 0
:orphan_exit
echo deck done
start "" /b cmd /c start "" /b ping -n 90 127.0.0.1
exit /b 0
:orphan_wait
start "" /b cmd /c start "" /b ping -n 90 127.0.0.1
"%PYEXE%" -c "import time; time.sleep(600)"
exit /b 0
:child_viewer
start "" /b ping -n 90 127.0.0.1
"%PYEXE%" -c "import time; time.sleep(4)"
echo deck done
exit /b 0
:exports_exit
"%PYEXE%" "%~dp0write_exports.py" %2 %3 finished
exit /b 0
:exports_hang
"%PYEXE%" "%~dp0write_exports.py" %2 %3 finished
"%PYEXE%" -c "import time; time.sleep(600)"
exit /b 0
:exports_hang_unfinished
"%PYEXE%" "%~dp0write_exports.py" %2 %3 unfinished
"%PYEXE%" -c "import time; time.sleep(600)"
exit /b 0
:exports_hang_streams_only
"%PYEXE%" "%~dp0write_exports.py" %2 %3 unfinished
echo ATLAS version 0.0.0.R finished at (selftest, launcher stream only)
"%PYEXE%" -c "import time; time.sleep(600)"
exit /b 0
:keep_child
start "" /b ping -n 90 127.0.0.1
"%PYEXE%" -c "import time; time.sleep(600)"
exit /b 0
:hang
"%PYEXE%" -c "import time; time.sleep(600)"
exit /b 0
"""
WRITE_EXPORTS = r'''import re, sys
deck, out, how = sys.argv[1], sys.argv[2], sys.argv[3]
names = []
for l in open(deck).read().splitlines():
    if l.lstrip().startswith('#'): continue
    names += [n for n in re.findall(r'\boutf(?:ile)?\s*=\s*"?([^"\s]+)"?', l, re.I) if n not in names]
vg = [round(-3 + 0.05 * k, 6) for k in range(121)]
idv = [min(10 ** (-9 + 4 * (v - 0.5)), 1e-6) + 1e-16 for v in vg]
for n in names:
    col = {'idvg.dat': idv, 'isvg.dat': [-x for x in idv], 'igvg.dat': [0.0] * len(vg)}.get(n, [1.0] * len(vg))
    with open(n, 'w') as f:
        f.write('fake export (runner selftest)\n'); f.writelines(f'{v:.6g} {y:.6e}\n' for v, y in zip(vg, col))
with open(out, 'w') as f:
    f.write('\n*** fake simulator (runner selftest) ***\n')
    if how == 'finished': f.write('EXTRACT> quit\nquit\n\nATLAS version 0.0.0.R finished at (selftest)\n')
'''


def fake_dir():
    d = Path(tempfile.mkdtemp(prefix='iwo_fakesim_')); (d / 'fake_sim.cmd').write_text(FAKE_CMD.replace('\n', '\r\n')); (d / 'write_exports.py').write_text(WRITE_EXPORTS)
    os.environ['PYEXE'] = sys.executable
    return d


def fake_argv(d, mode): return ['cmd', '/c', str(d / 'fake_sim.cmd'), mode, '{deck}', '{stdout}']


def pings_since(t0):
    """PING.EXE processes created after t0 (the stand-in viewers of this selftest)"""
    out = []
    for pid, (ppid, name) in pg.snapshot().items():
        if name.lower() == 'ping.exe':
            ct, alive = pg.proc_info(pid)
            if alive and ct and pg.ft_epoch(ct) >= t0 - 1: out.append((pid, ct))
    return out


def kill_pings(t0):
    for pid, ct in pings_since(t0): pg.terminate(pid, ct)


@contextlib.contextmanager
def guard_env(viewers=None, policy=None, job=None, grace=None):
    saved = (pg.VIEWERS, os.environ.get('IWO_ATLAS_VIEWERS'), os.environ.get('IWO_ATLAS_JOB'), ra.PIPE_GRACE_S, ra.KILL_WAIT_S)
    if viewers is not None: pg.VIEWERS = viewers
    if policy is not None: os.environ['IWO_ATLAS_VIEWERS'] = policy
    if job is not None: os.environ['IWO_ATLAS_JOB'] = job
    if grace is not None: ra.PIPE_GRACE_S = grace; ra.KILL_WAIT_S = grace
    try:
        yield
    finally:
        pg.VIEWERS = saved[0]; ra.PIPE_GRACE_S, ra.KILL_WAIT_S = saved[3], saved[4]
        for k, v in (('IWO_ATLAS_VIEWERS', saved[1]), ('IWO_ATLAS_JOB', saved[2])):
            if v is None: os.environ.pop(k, None)
            else: os.environ[k] = v


def t_launch_equivalent():
    d = fake_dir(); w = Path(tempfile.mkdtemp(prefix='iwo_run_')); argv = ['cmd', '/c', str(d / 'fake_sim.cmd'), 'normal']
    ref = subprocess.run(argv, cwd=w, capture_output=True, text=True)
    out, err, to, rcode, rec = ra.launch(argv, w, 30)
    return (out, err, rcode, to) == (ref.stdout, ref.stderr, ref.returncode, False) and rec['kill'] is None and rec['job'].startswith('assigned'), \
        f'{out!r} {err!r} vs {ref.stdout!r} {ref.stderr!r}; job {rec["job"]}'


def t_old_pattern_hangs_new_bounded():
    """run_0075: deckbuild waits behind a viewer whose parent exited (outside the tree) and that holds the pipes"""
    d = fake_dir(); argv = ['cmd', '/c', str(d / 'fake_sim.cmd'), 'orphan_wait']; t0 = time.time()
    box = {}

    def old():
        p = subprocess.Popen(argv, cwd=d, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try: p.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            subprocess.run(['taskkill', '/T', '/F', '/PID', str(p.pid)], capture_output=True); p.communicate()
        box['done'] = time.time()
    th = threading.Thread(target=old, daemon=True); th.start(); th.join(15)
    old_blocked = th.is_alive(); kill_pings(t0); th.join(20)
    t1 = time.time()
    with guard_env(policy='record'):
        out, err, timed, rcode, rec = ra.launch(argv, d, 3)
    dt = time.time() - t1; left = pings_since(t1)
    killed = [x for x in rec['kill']['targets'] if x['name'].lower() == 'ping.exe' and x['result'] == 'terminated']
    kill_pings(t0)
    ok = old_blocked and timed and dt < 3 + 15 and killed and not left and rec['pipes']['stdout_eof']
    return ok, f'old blocked {old_blocked}; new {dt:.1f} s timed_out {timed}; ping terminated {len(killed)}; left {len(left)}; pipes {rec["pipes"]}'


def t_viewer_kill_policy():
    d = fake_dir(); w = Path(tempfile.mkdtemp(prefix='iwo_run_')); t0 = time.time()
    with guard_env(viewers=('ping.exe',), policy='kill'):
        out, err, timed, rcode, rec = ra.launch(['cmd', '/c', str(d / 'fake_sim.cmd'), 'child_viewer'], w, 30)
    v = rec['viewers']; dt = time.time() - t0; left = pings_since(t0); kill_pings(t0)
    return (not timed) and rcode == 0 and v and v[0]['result'] == 'terminated' and dt < 15 and not left and 'deck done' in out, \
        f'timed {timed} rc {rcode} viewers {v} {dt:.1f} s'


def t_orphan_exit_kill_and_record():
    """deck finished, an orphaned viewer holds the pipes: policy kill -> normal finish; policy record -> bounded timeout kill"""
    d = fake_dir(); w = Path(tempfile.mkdtemp(prefix='iwo_run_')); t0 = time.time(); argv = ['cmd', '/c', str(d / 'fake_sim.cmd'), 'orphan_exit']
    with guard_env(viewers=('ping.exe',), policy='kill'):
        o1, e1, to1, r1, rec1 = ra.launch(argv, w, 20)
    t1 = time.time()
    with guard_env(viewers=('ping.exe',), policy='record'):
        o2, e2, to2, r2, rec2 = ra.launch(argv, w, 4)
    dt2 = time.time() - t1; left = pings_since(t0); kill_pings(t0)
    ok = (not to1) and rec1['viewers'] and rec1['viewers'][0]['result'] == 'terminated' and to2 and rec2['viewers'][0]['policy'] == 'record' \
        and any(x['result'] == 'terminated' for x in rec2['kill']['targets']) and dt2 < 4 + 15 and not left
    return ok, f'kill: timed {to1}; record: timed {to2} {dt2:.1f} s; left {len(left)}'


def t_job_disabled_still_bounded():
    """no job object: a pipe holder that the parent-pid tracking may miss cannot stall the runner (bounded waits)"""
    d = fake_dir(); w = Path(tempfile.mkdtemp(prefix='iwo_run_')); t0 = time.time()
    with guard_env(policy='record', job='0', grace=3):
        out, err, timed, rcode, rec = ra.launch(['cmd', '/c', str(d / 'fake_sim.cmd'), 'orphan_wait'], w, 3)
    dt = time.time() - t0; kill_pings(t0)
    return timed and dt < 3 + 3 + 6 + 5 and rec['job'].startswith('disabled'), f'{dt:.1f} s; job {rec["job"]}; pipes {rec["pipes"]}; kill {[(x["name"], x["result"]) for x in rec["kill"]["targets"]]}'


def t_guard_defaults():
    """Codex D4 and blocker 1: viewer policy defaults to 'record'; the cleanup has no /T tree kill; KEEP holds the licence daemons"""
    saved = os.environ.pop('IWO_ATLAS_VIEWERS', None)
    try: pol = pg.Guard().policy
    finally:
        if saved is not None: os.environ['IWO_ATLAS_VIEWERS'] = saved
    src = (PKG / 'scripts' / 'proc_guard.py').read_text()
    ok = pol == 'record' and '/T' not in pg.FALLBACK_CMD and "'/T'" not in src and 'sflm_monitord.exe' in pg.KEEP and pg.CMD_TIMEOUT_S > 0 and pg.CLEANUP_BUDGET_S > 0
    return ok, f'policy {pol}; fallback {pg.FALLBACK_CMD}; keep {pg.KEEP}'


def t_keep_child_survives():
    """Codex blocker 1: a still-parented licence daemon (KEEP; stand-in PING.EXE) survives the timeout cleanup; the former
    `taskkill /T /F /PID` killed it"""
    d = fake_dir(); w = Path(tempfile.mkdtemp(prefix='iwo_run_')); argv = ['cmd', '/c', str(d / 'fake_sim.cmd'), 'keep_child']; t0 = time.time()
    p = subprocess.Popen(argv, cwd=w, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(2.5)
    before = pings_since(t0); subprocess.run(['taskkill', '/T', '/F', '/PID', str(p.pid)], capture_output=True, timeout=30); time.sleep(0.5)
    old_killed = bool(before) and not pings_since(t0); kill_pings(t0)
    t1 = time.time(); saved = pg.KEEP; pg.KEEP = ('ping.exe',)
    try:
        with guard_env(policy='record', grace=2):
            out, err, timed, rcode, rec = ra.launch(argv, w, 3)
    finally:
        pg.KEEP = saved
    alive = pings_since(t1); k = rec['kill']; kept = [x for x in k['kept'] if x['name'].lower() == 'ping.exe']
    term = [x for x in k['targets'] if x['result'].startswith('terminated')]; kill_pings(t0)
    ok = old_killed and timed and alive and kept and kept[0].get('alive_after_cleanup') and term and not any(x['name'].lower() == 'ping.exe' for x in k['targets'])
    return ok, f'former taskkill /T killed it: {old_killed}; new: kept {[(x["name"], x["alive_after_cleanup"]) for x in kept]}, terminated {[x["name"] for x in term]}'


def t_hung_cleanup_bounded():
    """Codex blocker 1: a hanging cleanup command is bounded (CMD_TIMEOUT_S, CLEANUP_BUDGET_S), and an error on one process does not stop
    the cleanup of the others (simulated TerminateProcess error and failure on the python stand-ins; the real cmd.exe root is terminated)"""
    d = fake_dir(); w = Path(tempfile.mkdtemp(prefix='iwo_run_')); argv = ['cmd', '/c', str(d / 'fake_sim.cmd'), 'hang']
    real = pg.terminate; flag = {'raised': 0}

    def fake_terminate(pid, ct):
        if pg.snapshot().get(pid, (None, ''))[1].lower().startswith('python'):
            if not flag['raised']: flag['raised'] = 1; raise RuntimeError('simulated TerminateProcess error')
            return 'terminate failed (error 5, simulated)'
        return real(pid, ct)
    saved = (pg.terminate, pg.FALLBACK_CMD, pg.CMD_TIMEOUT_S, pg.CLEANUP_BUDGET_S)
    pg.terminate, pg.FALLBACK_CMD, pg.CMD_TIMEOUT_S, pg.CLEANUP_BUDGET_S = fake_terminate, (sys.executable, '-c', 'import time; time.sleep(30)  # pid {pid}'), 2.0, 6.0
    try:
        with guard_env(policy='record', grace=2):
            t1 = time.time(); out, err, timed, rcode, rec = ra.launch(argv, w, 3); dt = time.time() - t1
    finally:
        pg.terminate, pg.FALLBACK_CMD, pg.CMD_TIMEOUT_S, pg.CLEANUP_BUDGET_S = saved
    k = rec['kill']
    for r in rec['processes_seen']:   # clean up what the simulated failures left alive (tracked processes of this launch only)
        ct, alive = pg.proc_info(r['pid'])
        if alive and r['name'].lower().startswith(('python', 'cmd')): real(r['pid'], ct)
    ok = timed and dt < 3 + 6 + 2 + 4 + 5 and any('fallback timed out' in f['result'] for f in k['fallback']) and k['errors'] \
        and any(t['name'].lower() == 'cmd.exe' and t['result'] == 'terminated' for t in k['targets'])
    return ok, f'{dt:.1f} s; fallback {[f["result"] for f in k["fallback"]]}; errors {k["errors"]}; targets {[(t["name"], t["result"][:40]) for t in k["targets"]]}'


def _keep_member_run(unidentifiable):
    """a still-parented KEEP stand-in (PING.EXE, in the job) that the Toolhelp snapshots never show (as for a process created after the
    snapshot); unidentifiable: its image-name query fails as well"""
    d = fake_dir(); w = Path(tempfile.mkdtemp(prefix='iwo_run_')); argv = ['cmd', '/c', str(d / 'fake_sim.cmd'), 'keep_child']; t1 = time.time()
    real_snap = pg.snapshot; real_name = getattr(pg, 'exe_name', None)
    ping = lambda pid: any(p == pid and v[1].lower() == 'ping.exe' for p, v in real_snap().items())
    saved = (pg.KEEP, pg.snapshot)
    pg.KEEP = ('ping.exe',); pg.snapshot = lambda: {p: v for p, v in real_snap().items() if v[1].lower() != 'ping.exe'}
    if unidentifiable: pg.exe_name = lambda pid, *a: None if ping(pid) else (real_name(pid, *a) if real_name else None)
    try:
        with guard_env(policy='record', grace=2):
            out, err, timed, rcode, rec = ra.launch(argv, w, 3)
    finally:
        pg.KEEP, pg.snapshot = saved
        if real_name is not None: pg.exe_name = real_name
        elif hasattr(pg, 'exe_name'): delattr(pg, 'exe_name')
    alive = pings_since(t1); kill_pings(t1)
    return timed, alive, rec['kill']


def t_keep_member_identified():
    """Codex rev-2 item 1 (regression): a job member the snapshot does not show (name '?') is identified by its image name before any
    termination: a KEEP daemon so identified survives"""
    timed, alive, k = _keep_member_run(False)
    named = [x['name'] for x in k['targets']]
    ok = timed and alive and any(x['name'].lower() == 'ping.exe' for x in k['kept']) and '?' not in named and 'ping.exe' not in [n.lower() for n in named]
    return ok, f'ping alive {bool(alive)}; kept {[x["name"] for x in k["kept"]]}; targets {named}'


def t_unidentified_member_deferred():
    """Codex rev-2 item 1 (regression): a member whose executable name cannot be verified is never terminated (nor given the fallback),
    is re-scanned in every pass, and is reported as unidentified and as a survivor"""
    timed, alive, k = _keep_member_run(True)
    un = k.get('unidentified') or []
    ok = timed and alive and un and all(u.get('alive_after_cleanup') for u in un) and any(s.get('unidentified') for s in k['survivors']) \
        and not any(x['name'] == '?' for x in k['targets']) and not k['fallback']
    return ok, f'ping alive {bool(alive)}; unidentified {un}; survivors {k["survivors"]}; targets {[x["name"] for x in k["targets"]]}'


@contextlib.contextmanager
def atlas_sandbox(mode):
    """run_atlas.execute* with a temporary RUN_INDEX/runs folder and runner.argv replaced by the fake simulator"""
    d = fake_dir(); tmp = Path(tempfile.mkdtemp(prefix='iwo_exec_')); root = tmp / 'pkg'
    for x in ('results/runs', 'config'): (root / x).mkdir(parents=True)
    shutil.copy(PKG / 'config' / 'solver.yaml', root / 'config' / 'solver.yaml')
    saved = (ra.INDEX, ra.RUNS, ra.ROOT, ra.load_configs); real = ra.load_configs

    def cfg():
        m, g, s = real(); s['runner']['argv'] = fake_argv(d, mode); return m, g, s
    ra.INDEX, ra.RUNS, ra.ROOT, ra.load_configs = root / 'results' / 'RUN_INDEX.csv', root / 'results' / 'runs', root, cfg
    try:
        yield root
    finally:
        ra.INDEX, ra.RUNS, ra.ROOT, ra.load_configs = saved


def last_run(root):
    rows = ra.rows(); d = root / rows[-1]['output_dir']; return rows, json.loads((d / 'execution.json').read_text())


def t_execute_post_export_hang():
    """Codex D5: post_export_hang is diagnostic metadata only; completion is read from deckbuild.out itself (a completion line in the
    launcher stream alone does not count); timeout facts unchanged"""
    out = {}; notes = []
    for mode in ('exports_hang', 'exports_hang_unfinished', 'exports_hang_streams_only', 'exports_exit'):
        with atlas_sandbox(mode) as root, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try: ra.execute(2.0, f'selftest_{mode}', [], timeout=12)
            except RuntimeError as e: out[mode + '_error'] = str(e)
            rows, ex = last_run(root)
            b = ex.get('post_export_hang_basis') or {}
            out[mode] = (ex['status'], ex['timed_out'], ex.get('post_export_hang', 'absent'), rows[-1]['exit_code'],
                         b.get('all_deck_outputs_exist_with_mtime_before_kill'), b.get('deckbuild_out_shows_completion'), ex['scan']['finished'],
                         ex['process_guard']['kill'] is not None)
            if b: notes.append(b.get('note', ''))
    want = {'exports_hang': ('REAL_ATLAS_SCORED', True, True, 'timeout', True, True, True, True),
            'exports_hang_unfinished': ('REAL_ATLAS_SCORED', True, False, 'timeout', True, False, False, True),
            'exports_hang_streams_only': ('REAL_ATLAS_SCORED', True, False, 'timeout', True, False, True, True),
            'exports_exit': ('REAL_ATLAS_SCORED', False, 'absent', '0', None, None, True, False)}
    ok = all(out.get(k) == v for k, v in want.items()) and notes and all(n.startswith('DIAGNOSTIC METADATA ONLY') for n in notes)
    return ok, json.dumps(out)


def t_execute_seal_notes():
    """state-only plans: run_atlas.execute(seal_notes=True) writes a status-only RUN_INDEX finish note, keeps the full note in execution.json
    and prints no result"""
    with atlas_sandbox('exports_exit') as root:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()): ra.execute(2.0, 'selftest_sealed', [], timeout=30, seal_notes=True)
        rows, ex = last_run(root)
    n = rows[-1]['notes']
    ok = n == 'REAL_ATLAS_SCORED: state-only (note sealed in execution.json run_index_note_sealed)' and 'active RMSE' in ex['run_index_note_sealed'] \
        and 'rmse' not in buf.getvalue().lower() and rows[0]['notes'].startswith('STARTED')
    return ok, f'RUN_INDEX note {n!r}; console {buf.getvalue()[:80]!r}'


def t_strip_timeout_not_evaluated():
    with atlas_sandbox('hang') as root, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        try: ra.execute_strip(2.0, 'selftest_strip_hang', [], timeout=4); raised = False
        except RuntimeError: raised = True
        rows, ex = last_run(root)
    return raised and ex['status'] == 'TIMEOUT' and ex['post_export_hang'] is None and rows[-1]['exit_code'] == 'timeout', \
        f'{ex["status"]} {ex.get("post_export_hang")} {rows[-1]["exit_code"]}'


def t_no_real_launch_possible():
    try:
        subprocess.Popen(['C:/sedatools/exe/deckbuild.exe', '-run', 'device.in']); return False, 'not blocked'
    except RealLaunchAttempted:
        return True, 'blocked'


def main():
    t0 = time.time()
    case('guard: a real deckbuild launch is refused in this selftest', t_no_real_launch_possible)
    case('A1 plans without gates: launches, RUN_INDEX rows, summaries and console identical to HEAD run_campaign.py', ungated_identical)
    case('A2 FIRED gate stops before the next launch (exit 3), value-free record', t_fired)
    case('A3 UNRESOLVED + on_unresolved=continue: the plan continues', t_unresolved_continue)
    case('A4 UNRESOLVED + on_unresolved=stop: stops before the next launch', t_unresolved_stop)
    case('A5 a stop holds; --ack-gate needs --ack-audit naming the gate and decision; the acknowledgement records audit path, sha256, decision', t_hold_and_ack)
    case('A6 gate after the last entry is evaluated at the end', t_after_last_entry)
    case('A7 hc_generation with an external control (run_id + label); label mismatch -> UNRESOLVED missing_run', t_generation_external_control)
    case('A8 failed checkpoint launch -> UNRESOLVED missing_run', t_failed_checkpoint)
    case('A9 --retry of the checkpoint gives new inputs and a new evaluation (old decision superseded)', t_retry_reevaluates)
    case('A10 invalid gate declarations / --workers 2 / --ack-gate without gates: refused, nothing launched', t_refusals)
    case('A11 the child discards scorer prints; state mapping; scorer hash re-checked in the child', t_child_output_discarded)
    case('A12 generated campaign_C10_DIAG.json (state-only): four supervised stops with cited audits, then the remaining 13 entries', t_diag_walk)
    case('A13 blocker 2: a cached UNRESOLVED/continue decision is re-evaluated after policy+evidence change, input-file change, legacy record', t_rebinding)
    case('A14 an acknowledgement covers only its decision: a declaration change re-evaluates and stops again', t_ack_bound_to_decision)
    case('A15 blocker 3: state-only console/summary/RUN_INDEX-facing record; full record and launch prints sealed; resume from the sidecar', t_state_only)
    case('A16 invalid state_only declarations / --workers 2: refused, nothing launched', t_state_only_refusals)
    case('A17 rev-2 item 2: a changed or missing file in a run referenced by the cited resolution pair re-evaluates the gate', t_evidence_freshness)
    case('A18 rev-2 item 3: a superseded decision is never reused; restoring its binding re-evaluates and stops', t_superseded_not_reused)
    case('B0 defaults: viewer policy record (D4); no /T in the cleanup; KEEP licence daemons', t_guard_defaults)
    case('B1 launch(): stdout/stderr/returncode identical to Popen(text=True).communicate()', t_launch_equivalent)
    case('B2 run_0075 pattern: former code blocks; launch() returns bounded and terminates the orphaned viewer (job)', t_old_pattern_hangs_new_bounded)
    case('B3 viewer policy kill (opt-in): a viewer is terminated when first seen; the run ends normally', t_viewer_kill_policy)
    case('B4 orphaned viewer after the deck finished: policy kill -> normal end; record -> bounded timeout kill', t_orphan_exit_kill_and_record)
    case('B5 job object disabled: still bounded (no indefinite wait)', t_job_disabled_still_bounded)
    case('B6 blocker 1: a still-parented KEEP child survives the cleanup (the former taskkill /T killed it)', t_keep_child_survives)
    case('B7 blocker 1: a hanging cleanup command is bounded and an error on one process does not stop the cleanup', t_hung_cleanup_bounded)
    case('B8 rev-2 item 1: a job member missing from the snapshot is identified by image name; a KEEP daemon survives', t_keep_member_identified)
    case('B9 rev-2 item 1: an unidentifiable member is never terminated, re-scanned, reported as unidentified survivor', t_unidentified_member_deferred)
    case('C1 D5: post_export_hang from deckbuild.out itself (stream-only completion does not count); diagnostic note; exit_code stays timeout', t_execute_post_export_hang)
    case('C2 execute_strip() timeout: status TIMEOUT, post_export_hang null (not evaluated)', t_strip_timeout_not_evaluated)
    case('C3 execute(seal_notes=True): status-only RUN_INDEX note, full note in execution.json, no result printed', t_execute_seal_notes)
    n = sum(ok for _, ok, _, _ in RESULTS)
    print(f'{n}/{len(RESULTS)} ok  ({time.time() - t0:.0f} s)')
    return 0 if n == len(RESULTS) else 1


if __name__ == '__main__':
    if '--only' in sys.argv: ONLY.update(x.strip() for x in sys.argv[sys.argv.index('--only') + 1].split(',') if x.strip())
    sys.exit(main())
