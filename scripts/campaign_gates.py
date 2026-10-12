#!/usr/bin/env python3
"""Executable stop gates for scripts/run_campaign.py plans (2026-10-13; Codex 2026-10-12T13:18Z: "Split or supervise DIAG at the nominal
and generation checkpoints. The frozen rule requires stopping when a nominal/SRH null test produces floor-scale current
(analysis_2026-10-10_campaign/CAMPAIGN_DESIGN.md:304); the runner currently continues except for budget errors.").

OPT-IN: only a plan with a "gates" list is gated. run_campaign.py does not import this module for a plan without gates.

Declaration (plan JSON, "gates": [...]):
  {"id": "G-S2-04-nominal", "rule_id": "S2-STOP-NULL", "rule_ref": "<text>", "after": "S2-04", "test": "hc_nominal" | "hc_generation",
   "runs": {"run": REF[, "control": REF]}, "on_fired": "stop", "on_unresolved": "stop" | "continue",
   "scorer": "analysis_2026-10-10_campaign/score_register.py", "scorer_sha256": "<sha256 of the frozen scorer>", "kwargs": {}, "note": "<text>"}
  REF = {"entry": "<id of an entry of this plan at or before 'after'>"}  (its run in this plan's summary: launched or reused)
      | {"run_id": "run_NNNN", "label": "<its RUN_INDEX label>"}       (a run outside the plan; the label must match RUN_INDEX)
  kwargs (optional) are passed to the scorer function: hc_nominal ig_given/ig_source; hc_generation given/source/per_run. Without them the
  scorer uses its KCL PROXY resolution (register section 0).
A plan with an invalid gate, a scorer whose sha256 differs from scorer_sha256, or --workers != 1 is refused before any launch.

Evaluation: once the checkpoint entry 'after' has a record in the plan summary, and before the plan proceeds to its next entry, the frozen
scorer function score_register.<test>(run[, control]) is called on the run directories IN A SEPARATE PYTHON PROCESS (-B, sha256 re-checked
there, every print of the scorer swallowed; the parent keeps only one token line). The verdict string maps to a state:
  FIRED       verdict (a 'PROVISIONAL (...): ' prefix removed) starts with 'FAIL': a resolved exceedance of the registered bound
              (nominal: |I_G(-3 V)| > 1e-2 x floor; generation: resolved |dI_D| > 1e-20 A/um). Under the KCL proxy, a resolved current
              lies above max(1e-17 A, 0.1 x floor), i.e. it is floor-scale.
  NOT_FIRED   'PASS' or 'below resolution' (consistent with the bound; needs a demonstrated resolution).
  UNRESOLVED  anything else ('unresolved', 'invalid', 'not demonstrated'), a missing run, a hash mismatch, an error or a timeout.
FIRED -> stop (on_fired must be "stop"); UNRESOLVED -> on_unresolved; NOT_FIRED -> continue.
Operational rule (Codex D2, 2026-10-12T20:28Z): stopping on a resolved exceedance of the registered bound is a PROSPECTIVE, STRICTER
operational rule; it is not a verbatim implementation of the floor-scale rule of CAMPAIGN_DESIGN.md:304 and a FIRED gate is not itself a
hypothesis falsification (declared per gate in 'rule_basis').

Decision binding (Codex blocker 2; rev-2 items 2 and 3, 2026-10-12T21:01Z): a decision is reused only while it is the gate's ACTIVE
decision (not superseded) and its BINDING is current. BINDING = the sha256 of the full gate declaration (canonical JSON: test, runs,
policies, kwargs, notes), the scorer file's sha256, the sha256 of each input run's scored files (INPUT_FILES, missing files as null), and
for every evidence file cited in kwargs its sha256 plus the current INPUT_FILES of the run directories it references (resolution_pair
run_dir / ref_dir, missing files as null). Any change (policy, declaration, scorer, a rescored or retried run, new or stale resolution
evidence) gives a new evaluation before the plan proceeds; the earlier decision is kept and marked superseded, and a superseded decision is
never reused, even when its binding comes back. decision_id is unique per evaluation (sha256 of binding, gate, sequence and time).

Output (console line, <plan>.json "gates", results/campaigns/<plan>.gates.jsonl) is limited to: gate id, rule id, checkpoint, test, the
input run ids, the state, an evaluation token (ok / missing_run / error / timeout / scorer_hash_mismatch / no_state_line), the action,
the decision id, the binding hashes and the times. No current, no verdict text, nothing of any other run. A stop holds: a later invocation
launches nothing until --ack-gate GATE_ID --ack-audit FILE is given, where FILE is the completed audit and names the gate id and the
decision id (Codex D1); the acknowledgement records the audit path, its sha256 and the decision it acknowledges, and never carries over to
a new decision.

  python scripts/campaign_gates.py --child      (internal: one evaluation; JSON request on stdin, one 'GATE_STATE <state> <token>' line)
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib
import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
TESTS = {'hc_nominal': ('run',), 'hc_generation': ('run', 'control')}            # frozen scorer functions usable as gates, with their roles
KWARGS = {'hc_nominal': ('ig_given', 'ig_source'), 'hc_generation': ('given', 'source', 'per_run')}
KEYS = {'id', 'rule_id', 'rule_ref', 'rule_basis', 'after', 'test', 'runs', 'on_fired', 'on_unresolved', 'kwargs', 'scorer', 'scorer_sha256', 'note'}
INPUT_FILES = ('execution.json', 'device.in', 'material_model_used.json', 'terminal_currents.csv', 'strip_iv.csv')   # = score_register.EVID
CHILD_TIMEOUT_S = 900
_LINE = re.compile(r'^GATE_STATE (FIRED|NOT_FIRED|UNRESOLVED) (\w+)$')


def now(): return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
def sha256(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canon(x): return json.dumps(x, sort_keys=True, separators=(',', ':'), default=str)
def _pkg_path(p): q = Path(str(p)); return q if q.is_absolute() else PKG / q   # the child evaluates with cwd = PKG


def evidence_paths(kw):
    """evidence files cited in a gate's kwargs (resolution_pair JSONs)"""
    kw = kw or {}; out = [kw.get('source'), kw.get('ig_source')]
    out += [v[1] for v in (kw.get('per_run') or {}).values() if isinstance(v, (list, tuple)) and len(v) > 1]
    return [str(x) for x in out if x]


def run_files(d):
    """sha256 of every INPUT_FILE of a run directory, None for a missing file (missing-file states are part of the binding)"""
    return {f: (sha256(Path(d) / f) if (Path(d) / f).is_file() else None) for f in INPUT_FILES}


def evidence_state(e):
    """an evidence file and the CURRENT files of the run directories it references (Codex rev-2 item 2: a resolution_pair JSON names
    run_dir and ref_dir; changing or deleting a file there must change the binding even when the JSON itself is unchanged)"""
    p = _pkg_path(e)
    if not p.is_file(): return {'sha256': None, 'referenced_runs': None}
    out = {'sha256': sha256(p), 'referenced_runs': {}}
    try: j = json.loads(p.read_text())
    except Exception: out['referenced_runs'] = 'unreadable JSON'; return out
    for key in ('run_dir', 'ref_dir'):
        if isinstance(j, dict) and isinstance(j.get(key), str):
            d = _pkg_path(j[key]); out['referenced_runs'][key] = {'dir': j[key], 'exists': d.is_dir(), 'files_sha256': run_files(d)}
    return out


def binding(g, ins):
    """(binding dict, binding sha256) of a gate decision: declaration, scorer file, input run files and cited evidence files with the
    current files of the runs they reference, missing files included (docstring)"""
    sp = _pkg_path(g['scorer'])
    b = {'gate_declaration_sha256': hashlib.sha256(canon(g).encode()).hexdigest(), 'scorer_sha256': sha256(sp) if sp.is_file() else None,
         'inputs': {role: {'run_id': v[0], 'files_sha256': (run_files(v[1]) if v[1] else None)} for role, v in sorted(ins.items())},
         'evidence_sha256': {e: evidence_state(e) for e in evidence_paths(g.get('kwargs'))}}
    return b, hashlib.sha256(canon(b).encode()).hexdigest()


def state_of(verdict):
    """frozen-scorer verdict string -> FIRED / NOT_FIRED / UNRESOLVED (module docstring)"""
    v = str(verdict or '')
    if v.startswith('PROVISIONAL'): v = v.split('): ', 1)[1] if '): ' in v else ''
    if v.startswith('FAIL'): return 'FIRED'
    if v.startswith('PASS') or v.startswith('below resolution'): return 'NOT_FIRED'
    return 'UNRESOLVED'


# ---------------------------------------------------------------- parent side (run_campaign.py)
def validate(plan, workers=1):
    """list of problems with the plan's gates ([] = valid); any problem refuses the plan before a launch"""
    gates = plan.get('gates')
    if not isinstance(gates, list) or not gates: return ['"gates" must be a non-empty list']
    pos = {e['id']: k for k, e in enumerate(plan.get('runs', []))}; errs = []; seen = set()
    for g in gates:
        gid = g.get('id') if isinstance(g, dict) else None
        if not isinstance(gid, str) or not re.fullmatch(r'[A-Za-z0-9._-]+', gid): errs.append(f'gate id must match [A-Za-z0-9._-]+: {str(g)[:80]}'); continue
        if gid in seen: errs.append(f'{gid}: duplicate gate id')
        seen.add(gid)
        if set(g) - KEYS: errs.append(f'{gid}: unknown keys {sorted(set(g) - KEYS)}')
        errs += [f'{gid}: {k} must be text' for k in ('rule_ref', 'rule_basis', 'note') if k in g and not isinstance(g[k], str)]
        if not isinstance(g.get('rule_id'), str) or not re.fullmatch(r'[A-Za-z0-9._:-]+', g['rule_id']): errs.append(f'{gid}: rule_id must be a short token [A-Za-z0-9._:-]+')
        a = g.get('after')
        if a not in pos: errs.append(f'{gid}: after {a!r} is not an entry id of this plan')
        t = g.get('test')
        if t not in TESTS: errs.append(f'{gid}: test {t!r} is not one of {sorted(TESTS)}'); continue
        runs = g.get('runs')
        if not isinstance(runs, dict) or set(runs) != set(TESTS[t]): errs.append(f'{gid}: runs must name exactly the roles {list(TESTS[t])}')
        else:
            for role, ref in runs.items():
                if isinstance(ref, dict) and set(ref) == {'entry'}:
                    if ref['entry'] not in pos: errs.append(f'{gid}: {role} entry {ref["entry"]!r} is not in this plan')
                    elif a in pos and pos[ref['entry']] > pos[a]: errs.append(f'{gid}: {role} entry {ref["entry"]} comes after the checkpoint {a}')
                elif isinstance(ref, dict) and set(ref) == {'run_id', 'label'}:
                    if not re.fullmatch(r'run_\d{4}', str(ref['run_id'])) or not isinstance(ref['label'], str): errs.append(f'{gid}: {role} run_id/label malformed')
                else: errs.append(f'{gid}: {role} must be {{"entry": ID}} or {{"run_id": "run_NNNN", "label": LABEL}}')
        if g.get('on_fired') != 'stop': errs.append(f'{gid}: on_fired must be "stop"')
        if g.get('on_unresolved') not in ('stop', 'continue'): errs.append(f'{gid}: on_unresolved must be "stop" or "continue" (no default)')
        kw = g.get('kwargs', {})
        if not isinstance(kw, dict) or set(kw) - set(KWARGS[t]): errs.append(f'{gid}: kwargs allowed for {t}: {list(KWARGS[t])}')
        sp, ss = g.get('scorer'), g.get('scorer_sha256')
        if not isinstance(sp, str) or not isinstance(ss, str): errs.append(f'{gid}: scorer and scorer_sha256 are required')
        elif not (PKG / sp).is_file(): errs.append(f'{gid}: scorer {sp} not found')
        elif sha256(PKG / sp) != ss.lower(): errs.append(f'{gid}: {sp} sha256 differs from the declared frozen scorer_sha256')
    if workers != 1: errs.append(f'gated plans are sequential only (--workers 1, got {workers})')
    return errs


def inputs(g, res, index_rows, root):
    """{role: (run_id or None, absolute run directory or None, problem or None)} of a gate"""
    out = {}
    for role, ref in g['runs'].items():
        if 'entry' in ref:
            recs = [r for r in res.get('runs', []) if r.get('id') == ref['entry']]
            r = recs[-1] if recs else None
            if r is None: out[role] = (None, None, 'no record')
            elif not r.get('run_dir'): out[role] = (None, None, 'entry has no run')
            else: out[role] = (r.get('run_id'), str(Path(root) / r['run_dir']), None)
        else:
            rows = [x for x in index_rows if x.get('run_id') == ref['run_id']]
            if not rows: out[role] = (ref['run_id'], None, 'run_id not in RUN_INDEX')
            elif any(x.get('label') != ref['label'] for x in rows): out[role] = (ref['run_id'], None, 'label mismatch')
            else:
                od = rows[-1].get('output_dir'); out[role] = (ref['run_id'], str(Path(root) / od) if od else None, None if od else 'no output_dir')
    return out


def evaluate(g, dirs, timeout=CHILD_TIMEOUT_S):
    """(state, evaluation token) of one gate on {role: run directory}; the scorer runs in a child process whose output is discarded"""
    req = {'test': g['test'], 'runs': dirs, 'scorer': str(PKG / g['scorer']), 'scorer_sha256': g['scorer_sha256'].lower(), 'kwargs': g.get('kwargs') or {}}
    try:
        cp = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--child'], input=json.dumps(req), capture_output=True,
                            text=True, errors='replace', timeout=timeout, cwd=str(PKG), env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    except subprocess.TimeoutExpired: return 'UNRESOLVED', 'timeout'
    except Exception: return 'UNRESOLVED', 'error'
    ms = [m for m in (_LINE.match(l.strip()) for l in (cp.stdout or '').splitlines()) if m]   # everything else (stdout, stderr) is dropped
    return (ms[-1].group(1), ms[-1].group(2)) if ms else ('UNRESOLVED', 'no_state_line')


def _log_path(out): return Path(out).with_name(Path(out).stem + '.gates.jsonl')


def _jsonl(out, rec):
    with _log_path(out).open('a') as f: f.write(json.dumps(rec) + '\n')


def resume_hint(r): return f'--ack-gate {r["gate"]} --ack-audit <completed audit file naming {r["gate"]} and decision {r["decision_id"]}>'


def active(res, gid):
    """the ACTIVE decision of a gate: its latest decision that no later decision superseded (None if there is none)"""
    act = [r for r in res.get('gates', []) if r.get('gate') == gid and not r.get('superseded_by')]
    return act[-1] if act else None


def check(plan, res, save, out, root, index_rows):
    """evaluate every gate whose checkpoint has a record unless its ACTIVE decision has the CURRENT binding (gate declaration, scorer,
    input run files, evidence files and the runs they reference). A superseded decision is never reused, even when its binding comes back
    (Codex rev-2 item 3): a new evaluation is made. An active, current, unacknowledged stop is returned again. Prints one value-free line
    per evaluation, appends the decision to res['gates'] (save()) and to <plan>.gates.jsonl, marks the gate's earlier decisions superseded;
    returns the first decision whose action is 'stop', else None"""
    res.setdefault('gates', []); have = {r.get('id') for r in res.get('runs', [])}
    for g in plan['gates']:
        if g['after'] not in have: continue
        ins = inputs(g, res, index_rows(), root); ids = {k: v[0] for k, v in ins.items()}; b, bsha = binding(g, ins)
        a = active(res, g['id'])
        if a is not None and a.get('binding_sha256') == bsha:
            if a.get('action') == 'stop' and not a.get('acknowledged_utc'): return a
            continue
        state, ev = ('UNRESOLVED', 'missing_run') if any(v[2] or not v[1] for v in ins.values()) else evaluate(g, {k: v[1] for k, v in ins.items()})
        action = 'stop' if state == 'FIRED' or (state == 'UNRESOLVED' and g['on_unresolved'] == 'stop') else 'continue'
        t = now(); n = sum(r.get('gate') == g['id'] for r in res['gates'])
        did = hashlib.sha256(f'{bsha}|{g["id"]}|{n}|{t}'.encode()).hexdigest()[:16]   # unique per evaluation, also when a binding recurs
        rec = {'gate': g['id'], 'rule_id': g['rule_id'], 'after': g['after'], 'test': g['test'], 'inputs': ids, 'state': state, 'evaluation': ev,
               'action': action, 'decision_id': did, 'binding_sha256': bsha, 'binding': b, 'evaluated_utc': t}
        for r in res['gates']:
            if r['gate'] == g['id'] and not r.get('superseded_by'): r['superseded_by'] = rec['decision_id']
        res['gates'].append(rec); save(); _jsonl(out, rec)
        print(f'GATE {g["id"]} [{g["rule_id"]}] after {g["after"]}: {state} -> {"STOP" if action == "stop" else "continue"} (decision {rec["decision_id"]})', flush=True)
        if action == 'stop': return rec
    return None


def audit_citation(audit, r):
    """(ok, why, record) for an acknowledgement of stop decision r: the audit file must exist, be non-empty and name the gate id and the
    decision id (Codex D1: the acknowledgement cites the completed audit and stays bound to that decision)"""
    if not audit: return False, 'an acknowledgement must cite the completed audit: --ack-audit FILE', None
    p = Path(audit); p = p if p.is_absolute() else Path.cwd() / p
    if not p.is_file() or p.stat().st_size == 0: return False, f'audit file {audit} is missing or empty', None
    txt = p.read_text(errors='replace')
    if r['gate'] not in txt or r['decision_id'] not in txt:
        return False, f'audit file {audit} must name the gate {r["gate"]} and its decision {r["decision_id"]}', None
    rel = str(p.resolve().relative_to(PKG)).replace('\\', '/') if p.resolve().is_relative_to(PKG) else str(p.resolve())
    return True, '', {'path': rel, 'sha256': sha256(p), 'acknowledges_decision': r['decision_id']}


def held(plan, res, acks, audit, save, out, root, index_rows):
    """(stops that hold, problems). A stop decision holds unless acknowledged with a valid audit citation (--ack-gate + --ack-audit). A
    stop whose binding is no longer the gate's current binding holds no more: the gate is re-evaluated (check) before the plan proceeds.
    A stop of a gate no longer declared is marked superseded."""
    gm = {g['id']: g for g in plan['gates']}; cur = {}; hold, probs = [], []
    for r in res.get('gates', []):
        if r.get('action') != 'stop' or r.get('acknowledged_utc') or r.get('superseded_by'): continue
        g = gm.get(r['gate'])
        if g is None: r['superseded_by'] = 'gate no longer declared in the plan'; continue
        if r['gate'] not in cur: cur[r['gate']] = binding(g, inputs(g, res, index_rows(), root))[1]
        if r.get('binding_sha256') != cur[r['gate']]: continue   # stale decision: a new evaluation comes first (check)
        if r['gate'] not in acks: hold.append(r); continue
        ok, why, info = audit_citation(audit, r)
        if not ok: probs.append(f'--ack-gate {r["gate"]} refused: {why}'); hold.append(r); continue
        r['acknowledged_utc'] = now(); r['ack_audit'] = info
        _jsonl(out, {'gate': r['gate'], 'decision_id': r['decision_id'], 'acknowledged_utc': r['acknowledged_utc'], 'ack_audit': info})
        print(f'GATE {r["gate"]}: stop decision {r["decision_id"]} acknowledged (audit cited); the plan continues', flush=True)
    save()
    return hold, probs


# ---------------------------------------------------------------- child (one evaluation, isolated process)
def child():
    def emit(state, ev): sys.__stdout__.write(f'GATE_STATE {state} {ev}\n'); sys.__stdout__.flush()
    try:
        req = json.loads(sys.stdin.read()); sp = Path(req['scorer'])
        if req['test'] not in TESTS: return emit('UNRESOLVED', 'error')
        if sha256(sp) != req['scorer_sha256']: return emit('UNRESOLVED', 'scorer_hash_mismatch')
        sink = io.StringIO()
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            sys.path.insert(0, str(sp.parent)); sr = importlib.import_module(sp.stem)
            if Path(sr.__file__).resolve() != sp.resolve() or sha256(sr.__file__) != req['scorer_sha256']: raise RuntimeError('scorer module mismatch')
            kw = dict(req.get('kwargs') or {})
            if kw.get('per_run'): kw['per_run'] = {k: tuple(v) for k, v in kw['per_run'].items()}
            r = getattr(sr, req['test'])(*[req['runs'][role] for role in TESTS[req['test']]], **kw)
        emit(state_of(r.get('verdict')), 'ok')
    except Exception:
        emit('UNRESOLVED', 'error')


if __name__ == '__main__':
    if sys.argv[1:] == ['--child']: child()
    else: print(__doc__); sys.exit(2)
