#!/usr/bin/env python3
"""State-only campaign surface (2026-10-13; Codex blocker 3 and ruling D7, CODEX_WORK_CHAT 2026-10-12T20:28Z): "Console redirection does not
seal campaign summaries ... Provide an opt-in state-only surface covering console, summaries and automatic monitors, while keeping full
records sealed."

OPT-IN per plan: "state_only": {"sealed_dir": "results/sealed/<subdir>"}. run_campaign.py does not import this module otherwise.
With it, for that plan:
  console            one state line per entry: id, run_id, runner status, state (completed / failed / reused / not launched), wall_s.
                     No metric, note, error text or traceback. Everything the launch prints (run_atlas result JSON, warnings, the
                     timeout message) goes to <sealed_dir>/<plan>.console.log instead.
  campaign summary   results/campaigns/<plan>.json holds the STATE projection only (STATE_KEYS per run, the value-free gate decisions);
                     the full record (summaries with metrics, RUN_INDEX notes of reused runs, error texts, tracebacks, placeholders) is
                     <sealed_dir>/<plan>.full.json, which is also what a resumed invocation reads.
  RUN_INDEX notes    the finish note of a launch is status-only ('<STATUS>: state-only (note sealed in execution.json ...)'); the full
                     note is kept in the run's own execution.json (run_atlas seal_notes=True). The STARTED note is unchanged.
  gates              already value-free (scripts/campaign_gates.py).
The run directories themselves stay as before (sealed by convention). Nothing here changes what is launched.
"""
from __future__ import annotations

import contextlib
import json
from pathlib import Path, PurePosixPath

STATE_KEYS = ('id', 'thickness', 'label', 'mode', 'purpose', 'run_id', 'run_dir', 'status', 'wall_s', 'not_relaunched', 'reused_earlier_launch',
              'earlier_run_ids')


def validate(plan, workers=1):
    so = plan.get('state_only'); errs = []
    if not isinstance(so, dict) or set(so) != {'sealed_dir'} or not isinstance(so.get('sealed_dir'), str):
        return ['state_only must be {"sealed_dir": "results/sealed/<subdir>"}']
    p = PurePosixPath(so['sealed_dir'].replace('\\', '/'))
    if p.is_absolute() or '..' in p.parts or p.parts[:2] != ('results', 'sealed'): errs.append('state_only.sealed_dir must be a relative path under results/sealed/')
    if workers != 1: errs.append(f'state-only plans are sequential only (--workers 1, got {workers}): the launch output is redirected per process')
    return errs


def paths(root, stem, so):
    d = Path(root) / so['sealed_dir']; d.mkdir(parents=True, exist_ok=True)
    return d / f'{stem}.full.json', d / f'{stem}.console.log'


def state(r):
    """state projection of one run record (no metric, note, error text, traceback, override value derived from a result)"""
    s = {k: r[k] for k in STATE_KEYS if k in r}
    s['state'] = ('failed' if r.get('error') else 'reused' if r.get('reused_earlier_launch') else 'completed' if r.get('run_dir') else 'not launched')
    if r.get('error'): s['error'] = 'sealed (full text in the sealed record)'
    if r.get('earlier_records'): s['earlier_records'] = [state(x) for x in r['earlier_records']]
    return s


def save(res, out, full, root):
    """full record -> the sealed sidecar; state projection -> the ordinary campaign summary"""
    Path(full).write_text(json.dumps(res, indent=1, default=float))
    rel = str(Path(full).relative_to(root)).replace('\\', '/') if Path(full).is_relative_to(root) else str(full)
    pub = {'campaign': res.get('campaign'), 'purpose': res.get('purpose'), 'plan_file': res.get('plan_file'),
           'surface': f'STATE-ONLY (Codex blocker 3 / D7): no metric, note, error text, traceback or placeholder; full record sealed in {rel}',
           'runs': [state(r) for r in res.get('runs', [])]}
    if 'gates' in res: pub['gates'] = res['gates']
    Path(out).write_text(json.dumps(pub, indent=1, default=float))


def console(r):
    s = state(r); return json.dumps({k: s.get(k) for k in ('id', 'run_id', 'status', 'state', 'wall_s')})


@contextlib.contextmanager
def sealed_io(log):
    """stdout and stderr of a launch -> the sealed console log (process-wide: state-only plans are sequential)"""
    with open(log, 'a', encoding='utf-8', errors='replace') as f, contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
        yield
