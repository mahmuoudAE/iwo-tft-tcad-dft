#!/usr/bin/env python3
"""IWO Mission Control: read-only data collectors (Python 3.12 stdlib only; PyYAML is used when present).

Every public collector returns {ok, updated_utc, error, data} and never raises.
Nothing here writes to a project file, launches ATLAS, or changes anything on CERN.
CERN is read only through the EXISTING SSH ControlMaster (~/.ssh/cm-cern); if `ssh -O check` fails, nothing else
is attempted. The snapshot call also carries ProxyCommand=/bin/false, so if the master vanishes between the check and
the call, ssh fails instead of opening a new connection to lxplus.
"""
import base64
import collections
import csv
import glob
import json
import os
import re
import subprocess
import threading
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

# ----------------------------------------------------------------------------------------------- paths
DASH = Path(__file__).resolve().parent
PRIV = Path(os.environ.get('IWO_PRIV', DASH.parent.parent))
ROOT = Path(os.environ.get('IWO_ROOT', PRIV.parent))
PUB = Path(os.environ.get('IWO_PUB', ROOT / 'IWO_PHYSICS_CONSTRAINED_MODEL_V1'))
ANA = PUB / 'analysis_2026-10-10_campaign'
CHAT = PRIV / 'codex' / 'work_chat'
SPECS = PRIV / 'compute' / 'amorph' / 'specs'
AMORPH = PRIV / 'compute' / 'amorph'

CERN_HOST = 'melrashe@lxplus.cern.ch'
CERN_CP = os.path.expanduser('~/.ssh/cm-cern')
CERN_SNAPSHOT_PY = DASH / 'cern_snapshot.py'
# Options for the snapshot call. ssh tries the ControlMaster socket (ControlPath) BEFORE it would connect; only if the
# master is missing or stale does it fall back to a direct connection, and ProxyCommand=/bin/false turns that fallback
# into an immediate failure (no TCP connection to lxplus, no authentication attempt). The auth options are a second guard.
CERN_SSH_OPTS = ['-o', 'BatchMode=yes', '-o', 'ControlPath=' + CERN_CP, '-o', 'ControlMaster=no',
                 '-o', 'ProxyCommand=/bin/false', '-o', 'ConnectTimeout=10',
                 '-o', 'GSSAPIAuthentication=no', '-o', 'PubkeyAuthentication=no',
                 '-o', 'PasswordAuthentication=no', '-o', 'KbdInteractiveAuthentication=no']
CERN_MIN_GAP_S = 120          # never two CERN snapshots less than this apart (enforced under the CERN lock)

PS_EXE = '/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe'

C10_CAP_DEFAULT = 200
SEGMENT_LIMIT_S = 72000            # relax segments (make_dft.py: relax.sub args '$(seg) 72000')
FINAL_LIMIT_S = 72000              # final SCF, cells <= 200 atoms ('tomorrow')
FINAL_LIMIT_BIG_S = 250000         # final SCF, cells > 200 atoms ('testmatch'; make_dft.py fin_s)
FINAL_BIG_ATOMS = 200
DAG_RETRIES = 8
ML_ROUNDS = (('ml_jobs.txt', 'wave rev2', 12883773), ('ml_jobs_r1.txt', 'r1', 12883944),
             ('ml_jobs_r2.txt', 'r2', 12883953), ('ml_jobs_r3.txt', 'r3', 12884291))

# Deadlines (UTC). cern_target (15 Oct) and cern_end (21 Oct) are the project dates set for the dashboard; the other
# three are from HYPOTHESIS_REGISTER.md section 3, which the register collector re-reads (new dates there are added).
STATIC_DEADLINES = [
    ('cern_analysis_code_frozen', 'CERN: analysis code frozen', '2026-10-12T18:00:00Z'),
    ('cern_target', 'CERN target date', '2026-10-15T00:00:00Z'),
    ('cern_unconverged_exploratory', 'CERN: unconverged relaxations labelled exploratory', '2026-10-17T10:00:00Z'),
    ('cern_last_submission', 'CERN: last job submission', '2026-10-18T22:00:00Z'),
    ('cern_end', 'CERN access ends', '2026-10-21T23:59:59Z'),
]

JOB_STATUS = {1: 'idle', 2: 'running', 3: 'removed', 4: 'completed', 5: 'held', 6: 'transferring', 7: 'suspended'}


# ----------------------------------------------------------------------------------------------- helpers
def now_epoch():
    return time.time()


def utc_iso(t=None):
    if t is None:
        t = time.time()
    return datetime.fromtimestamp(t, timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def parse_utc(s):
    """'2026-10-10T16:44:31Z' / '2026-10-10T16:44Z' -> epoch (None on failure)."""
    if not s:
        return None
    s = s.strip()
    for fmt in ('%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%MZ', '%Y-%m-%dT%H:%M:%S'):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            pass
    return None


def parse_local(s, fmt):
    """Local wall time without zone (WSL TZ, +08:00) -> epoch."""
    try:
        return time.mktime(time.strptime(s, fmt))
    except (ValueError, OverflowError):
        return None


def fnum(x):
    try:
        if x is None or x == '':
            return None
        v = float(x)
        return v if v == v else None
    except (TypeError, ValueError):
        return None


def short(s, n=240):
    if s is None:
        return None
    s = str(s)
    return s if len(s) <= n else s[:n - 1] + '\u2026'


def stat_info(p):
    try:
        s = os.stat(p)
        return {'size': s.st_size, 'mtime': s.st_mtime}
    except OSError:
        return None


def read_text(p, tail=None):
    """UTF-8 text with CRLF normalised; tail = last N bytes only."""
    with open(p, 'rb') as f:
        if tail:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - tail))
        b = f.read()
    return b.decode('utf-8', 'replace').replace('\r\n', '\n').replace('\r', '\n')


_CACHE = {}
_CACHE_LOCK = threading.Lock()


def cached(path, loader):
    """Re-parse a file only when its (mtime, size) changes."""
    p = str(path)
    st = os.stat(p)
    key = (st.st_mtime_ns, st.st_size)
    with _CACHE_LOCK:
        hit = _CACHE.get((p, loader.__name__))
    if hit and hit[0] == key:
        return hit[1]
    val = loader(p)
    with _CACHE_LOCK:
        _CACHE[(p, loader.__name__)] = (key, val)
    return val


def load_json(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def load_text(p):
    return read_text(p)


def run_cmd(argv, timeout=20, cwd=None, env=None):
    """subprocess with stdin=/dev/null; returns (rc, stdout, stderr, seconds). Never raises."""
    t = time.time()
    try:
        p = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=timeout, cwd=cwd, env=env)
        return (p.returncode, p.stdout.decode('utf-8', 'replace'), p.stderr.decode('utf-8', 'replace'),
                round(time.time() - t, 3))
    except subprocess.TimeoutExpired:
        return ('timeout', '', 'timeout after %ss' % timeout, round(time.time() - t, 3))
    except Exception as e:  # missing binary etc.
        return ('exec-error', '', repr(e)[:200], round(time.time() - t, 3))


def envelope(fn, *a, **kw):
    """Run a collector body; body returns data (dict). Optional data keys __ok__/__error__ override the envelope."""
    t0 = time.time()
    try:
        data = fn(*a, **kw)
        ok = True
        err = None
        if isinstance(data, dict):
            ok = data.pop('__ok__', True)
            err = data.pop('__error__', None)
        return {'ok': bool(ok), 'updated_utc': utc_iso(), 'updated_epoch': round(time.time(), 1), 'error': err,
                'duration_s': round(time.time() - t0, 3), 'data': data}
    except Exception as e:
        return {'ok': False, 'updated_utc': utc_iso(), 'updated_epoch': round(time.time(), 1),
                'error': '%s: %s' % (type(e).__name__, short(str(e), 300)),
                'traceback': short(traceback.format_exc(), 2000),
                'duration_s': round(time.time() - t0, 3), 'data': None}


# =============================================================================================== ATLAS
RE_STARTED = re.compile(r'^STARTED points=(\d+) timeout=(\d+)s launch (\d+)/(\d+)(?: model=(\S+))?')
RE_STARTED_ANY = re.compile(r'timeout=(\d+)s')
RE_SCORED = re.compile(r'active RMSE (\S+) dec; Id\(3V\) ([+-]\S+)%; nonpos (\d+); maxKCL (\S+)')
RE_VALFAIL = re.compile(r'(SIGN_REVERSAL|KCL_FAILED): max KCL (\S+) A')
RE_TOTAL_TIME = re.compile(r'Total time:\s+([\d.]+)\s+(sec|min)\.')
RE_RUNID = re.compile(r'run_\d{4}')


def classify_notes(notes, exit_code):
    n = notes or ''
    if RE_SCORED.search(n):
        return 'REAL_ATLAS_SCORED'
    if 'no idvg.dat' in n:
        return 'TIMEOUT' if exit_code == 'timeout' else 'NO_EXPORT'
    m = RE_VALFAIL.search(n)
    if m:
        return m.group(1)
    if n.startswith('Error:') or 'Error:' in n[:40]:
        return 'SIMULATOR_ERROR'
    if 'missing requested gate points' in n:
        return 'INCOMPLETE_EXPORT'
    if 'PREDICTION' in n[:40]:
        return 'PREDICTION'
    if 'partial from' in n:
        return 'PARTIAL'
    if exit_code == 'timeout':
        return 'TIMEOUT'
    return 'UNKNOWN'


RE_RUN_ID = re.compile(r'^run_\d{4}$')


def _load_run_index(p):
    """RUN_INDEX.csv rows with every value a string. The runner appends to this file during each launch, so a poll can
    catch a half-written last row: rows with missing or extra columns, or without run_id / timestamp / label, are
    returned separately as `bad` (reported as warnings) instead of being parsed."""
    good, bad = [], []
    with open(p, encoding='utf-8', newline='') as f:
        rdr = csv.DictReader(f)
        for i, r in enumerate(rdr, start=2):
            partial = None in r or any(v is None for v in r.values())
            r = {k: (v or '') for k, v in r.items() if k is not None}
            if partial or not RE_RUN_ID.match(r.get('run_id', '')) or not r.get('timestamp_utc') or not r.get('label'):
                bad.append('line %d (%s): incomplete row skipped' % (i, short(r.get('run_id') or '?', 20)))
                continue
            good.append(r)
    return good, bad


def _solver_cap():
    try:
        txt = cached(PUB / 'config' / 'solver.yaml', load_text)
        m = re.search(r'^\s*max_launches:\s*(\d+)', txt, re.M)
        return int(m.group(1)) if m else None
    except OSError:
        return None


def _transfer_progress(run_dir):
    """Points written so far, last Vg and (Vg, Id_drain) pairs from transfer.log (column 9 = drain current)."""
    tl = run_dir / 'transfer.log'
    if not tl.exists():
        return {'points': 0, 'last_vg': None, 'curve': [], 'exists': False}
    pts = []
    with open(tl, 'rb') as f:
        for raw in f:
            if raw.startswith(b'd '):
                parts = raw.split()
                try:
                    vg = float(parts[1])
                    idr = float(parts[9]) if len(parts) > 9 else None
                    ig = float(parts[3]) if len(parts) > 3 else None
                except (ValueError, IndexError):
                    continue
                pts.append([vg, idr, ig])
    return {'points': len(pts), 'last_vg': pts[-1][0] if pts else None, 'exists': True,
            'curve': [[p[0], p[1]] for p in pts]}


def _deckbuild_liveness(run_dir):
    db = run_dir / 'deckbuild.out'
    si = stat_info(db)
    if not si:
        return {'exists': False}
    out = {'exists': True, 'size': si['size'], 'mtime_utc': utc_iso(si['mtime']),
           'age_s': round(time.time() - si['mtime'], 1)}
    try:
        tail = read_text(db, tail=65536)
        m = RE_TOTAL_TIME.findall(tail)
        if m:
            v, unit = m[-1]
            out['last_total_time'] = '%s %s' % (v, unit)
            out['last_total_time_s'] = round(float(v) * (60 if unit == 'min' else 1), 1)
        last = [ln for ln in tail.split('\n') if ln.strip()]
        out['last_line'] = short(last[-1], 200) if last else None
    except OSError:
        pass
    return out


def windows_processes():
    """Windows python*/atlas*/deckbuild processes via PowerShell CIM (WSL: /init <exe> <argv0> args)."""
    script = ("$ProgressPreference='SilentlyContinue'; "
              "Get-CimInstance Win32_Process -Filter \"Name like 'python%' or Name like 'atlas%' or Name='deckbuild.exe'\" | "
              "ForEach-Object { '{0}|{1}|{2}|{3}|{4}' -f $_.ProcessId, $_.ParentProcessId, $_.Name, "
              "$_.CreationDate.ToUniversalTime().ToString('s'), $_.CommandLine }")
    enc = base64.b64encode(script.encode('utf-16-le')).decode()
    if os.path.exists('/init') and os.path.exists(PS_EXE):
        argv = ['/init', PS_EXE, 'powershell.exe', '-NoProfile', '-NonInteractive', '-EncodedCommand', enc]
    else:  # running natively on Windows
        argv = ['powershell.exe', '-NoProfile', '-NonInteractive', '-EncodedCommand', enc]
    rc, out, err, sec = run_cmd(argv, timeout=25)
    res = {'ok': rc == 0, 'rc': rc, 'sec': sec, 'error': None if rc == 0 else short(err.strip() or 'rc %s' % rc, 200),
           'atlas': [], 'deckbuild': [], 'runner': [], 'nc_audit': [], 'other_python': []}
    if rc != 0:
        return res
    seen = set()
    for line in out.replace('\r', '').split('\n'):
        if not line.strip() or line.count('|') < 4:
            continue
        pid, ppid, name, created, cmd = line.split('|', 4)
        rec = {'pid': int(pid) if pid.isdigit() else pid, 'ppid': int(ppid) if ppid.isdigit() else ppid, 'name': name,
               'started_utc': created + 'Z' if created else None, 'cmdline': short(cmd, 300)}
        ep = parse_utc(rec['started_utc']) if created else None
        rec['age_s'] = round(time.time() - ep) if ep else None
        lname = name.lower()
        if lname.startswith('atlas'):
            res['atlas'].append(rec)
        elif lname == 'deckbuild.exe':
            res['deckbuild'].append(rec)
        elif lname.startswith('python'):
            if cmd in seen:  # venv python.exe launcher + python3.13.exe child share the CommandLine
                continue
            seen.add(cmd)
            if re.search(r'run_campaign|run_atlas', cmd):
                res['runner'].append(rec)
            elif 'nc_audit' in cmd:
                res['nc_audit'].append(rec)
            else:
                res['other_python'].append({k: rec[k] for k in ('pid', 'name', 'started_utc', 'age_s')})
    return res


def _matrix():
    p = ANA / 'campaign_matrix.json'
    m = cached(p, load_json)
    return m


def _stop_rules_design():
    """CAMPAIGN_DESIGN.md section 'Stop and decision rules' -> [{group, rules[]}] (prose)."""
    p = ANA / 'CAMPAIGN_DESIGN.md'
    txt = cached(p, load_text)
    m = re.search(r'^#+\s*Stop and decision rules\s*$', txt, re.M)
    if not m:
        return []
    rest = txt[m.end():]
    end = re.search(r'^#{1,3} ', rest, re.M)
    block = rest[:end.start()] if end else rest
    groups, cur = [], None
    for ln in block.split('\n'):
        h = re.match(r'^\*\*(.+?)\*\*\s*$', ln.strip())
        if h:
            cur = {'group': h.group(1), 'rules': []}
            groups.append(cur)
        elif ln.startswith('- ') and cur is not None:
            cur['rules'].append(short(ln[2:].strip(), 500))
        elif ln.startswith('  ') and ln.strip().startswith('- ') and cur is not None and cur['rules']:
            cur['rules'][-1] = short(cur['rules'][-1] + ' / ' + ln.strip()[2:], 600)
    return groups


def collect_atlas():
    warnings = []
    rows, bad_rows = cached(PUB / 'results' / 'RUN_INDEX.csv', _load_run_index)
    if bad_rows:
        warnings.append('RUN_INDEX.csv: %s' % '; '.join(bad_rows[-3:]))
    by = collections.OrderedDict()
    for r in rows:
        by.setdefault(r['run_id'], []).append(r)
    cap = _solver_cap()

    try:
        M = _matrix()
    except Exception as e:
        M = {'runs': [], 'stage_counts': {}, 'cap': C10_CAP_DEFAULT, 'reserve_launches': None, 'planned_launches': None}
        warnings.append('campaign_matrix.json: %s' % e)
    lab2entry = {e['campaign_entry']['label']: e for e in M.get('runs', []) if e.get('campaign_entry')}
    id2entry = {e['id']: e for e in M.get('runs', [])}
    c10_cap = int(M.get('cap') or C10_CAP_DEFAULT)

    # ---- per-run summary
    runs = []
    for rid, rr in by.items():
        started = next((r for r in rr if r['notes'].startswith('STARTED')), None)
        done = [r for r in rr if not r['notes'].startswith('STARTED') and not r['command'].startswith('RESCORE')]
        resc = [r for r in rr if r['command'].startswith('RESCORE')]
        comp = done[-1] if done else None
        final = resc[-1] if resc else comp
        label = rr[0]['label']
        s = {'run_id': rid, 'label': label, 'thickness_nm': fnum(rr[0]['thickness_nm']), 'c10': label.startswith('c10_'),
             'output_dir': rr[0]['output_dir'], 'model': None, 'points_requested': None, 'timeout_s': None,
             'launch_no': None, 'started_utc': started['timestamp_utc'] if started else rr[0]['timestamp_utc'],
             'finished_utc': comp['timestamp_utc'] if comp else None, 'exit_code': comp['exit_code'] if comp else None,
             'converged': comp['converged'] if comp else None, 'elapsed_s': fnum(comp['elapsed_s']) if comp else None,
             'notes': short(final['notes'], 220) if final else short(rr[-1]['notes'], 220),
             'rescored': bool(resc), 'status_notes': None, 'active_rmse_dec': None, 'Id3V_err_pct': None,
             'nonpos': None, 'max_kcl_A': None, 'stage': None, 'entry_id': None}
        if started:
            m = RE_STARTED.match(started['notes'])
            if m:
                s['points_requested'], s['timeout_s'], s['launch_no'] = int(m.group(1)), int(m.group(2)), int(m.group(3))
                s['model'] = m.group(5)
            else:
                m2 = RE_STARTED_ANY.search(started['notes'])
                s['timeout_s'] = int(m2.group(1)) if m2 else None
                s['mode_note'] = short(started['notes'], 120)
        if final:
            s['status_notes'] = classify_notes(final['notes'], comp['exit_code'] if comp else None)
            m = RE_SCORED.search(final['notes'])
            if m:
                s['active_rmse_dec'], s['Id3V_err_pct'] = fnum(m.group(1)), fnum(m.group(2))
                s['nonpos'], s['max_kcl_A'] = int(m.group(3)), fnum(m.group(4))
            mv = RE_VALFAIL.search(final['notes'])
            if mv:
                s['max_kcl_A'] = fnum(mv.group(2))
        else:
            s['status_notes'] = 'STARTED_ONLY'
        e = lab2entry.get(label)
        if e:
            s['stage'], s['entry_id'] = e['stage'], e['id']
        s['started_epoch'] = parse_utc(s['started_utc'])
        s['finished_epoch'] = parse_utc(s['finished_utc'])
        runs.append(s)

    run_by_id = {r['run_id']: r for r in runs}
    newest = max(runs, key=lambda r: int(r['run_id'][4:])) if runs else None

    # authoritative status from execution.json (C10 runs + newest), cached by mtime
    for r in runs:
        if not (r['c10'] or r is newest):
            continue
        ex = PUB / r['output_dir'] / 'execution.json'
        r['execution_json'] = ex.exists()
        if r['execution_json']:
            try:
                e = cached(ex, load_json)
                r['status'] = e.get('status')
                v = e.get('validation') or {}
                r['validation'] = {k: v.get(k) for k in ('max_kcl_abs_A', 'kcl_fail_count', 'wrong_sign_count',
                                                         'nonpositive_count', 'kcl_abs_limit_applied_A')}
                sc = e.get('scan') or {}
                r['convergence_flags'] = len(sc.get('convergence_flags') or [])
                r['scan_errors'] = [short(x, 160) for x in (sc.get('errors') or [])][:5]
                r['timed_out'] = e.get('timed_out')
            except Exception as ex_:
                warnings.append('%s execution.json: %s' % (r['run_id'], ex_))
    for r in runs:
        r.setdefault('status', None)
        r['status_final'] = r['status'] or r['status_notes']

    # ---- launches / budget
    c10_ids = [r['run_id'] for r in runs if r['c10']]
    exit_counts = collections.Counter(r['exit_code'] for r in runs if r['exit_code'] is not None)
    orphans = [r['run_id'] for r in runs if r['finished_utc'] is None and r is not newest]

    # ---- campaign summaries (results/campaigns/campaign_C10_*.json)
    entries = {}
    plan_results = {}
    for fp in sorted(glob.glob(str(PUB / 'results' / 'campaigns' / 'campaign_C10_*.json'))):
        stem = os.path.basename(fp)[len('campaign_C10_'):-len('.json')]
        try:
            d = cached(fp, load_json)
        except Exception as e:
            warnings.append('%s: %s' % (os.path.basename(fp), e))
            continue
        plan_results[stem] = {'file': os.path.basename(fp), 'n_records': len(d.get('runs', [])),
                              'mtime_utc': utc_iso(os.path.getmtime(fp))}
        for r in d.get('runs', []):
            rid = r.get('run_id')
            err = r.get('error')
            if not rid and err:
                m = RE_RUNID.search(err)
                rid = m.group(0) if m else None
            rec = {'id': r.get('id'), 'plan': stem, 'label': r.get('label'), 'thickness_nm': r.get('thickness'),
                   'run_id': rid, 'status': r.get('status') or ('ERROR' if err else None),
                   'error': short(err, 200), 'reused': bool(r.get('reused_earlier_launch')),
                   'earlier_records': len(r.get('earlier_records') or []),
                   'elapsed_s': r.get('elapsed_s'), 'wall_s': r.get('wall_s'),
                   'active_rmse_dec': r.get('active_rmse_dec'), 'sub_rmse_dec': r.get('sub_rmse_dec'),
                   'on_rmse_dec': r.get('on_rmse_dec'), 'Id3V_err_pct': r.get('Id3V_err_pct'),
                   'max_kcl_A': r.get('max_kcl_A'), 'purpose': short(r.get('purpose'), 260),
                   'n_overrides': len(r.get('overrides') or [])}
            for side in ('sim', 'exp'):
                d2 = r.get(side) or {}
                rec[side] = {k: d2.get(k) for k in ('Vth_cc_1e-9_V', 'SS_mV_dec', 'mu_FE_cm2Vs', 'Ion_A_per_um',
                                                     'Ioff_A_per_um', 'Ion_over_Ioff')} if d2 else None
            e = id2entry.get(rec['id'])
            rec['stage'] = e['stage'] if e else None
            old = entries.get(rec['id'])
            if old is None or (old['reused'] and not rec['reused']):
                entries[rec['id']] = rec
    # transfer progress for failed entries (e.g. the S1-06 timeout)
    for rec in entries.values():
        if rec['status'] == 'ERROR' and rec['run_id'] in run_by_id:
            rd = PUB / run_by_id[rec['run_id']]['output_dir']
            tp = _transfer_progress(rd)
            rec['points_logged'] = tp['points']
            rec['last_vg'] = tp['last_vg']
            rec['points_requested'] = run_by_id[rec['run_id']]['points_requested']

    # ---- stages
    stage_counts = M.get('stage_counts') or {}
    spent = collections.Counter()
    launched_entries = collections.defaultdict(set)
    for r in runs:
        if r['c10'] and r['stage']:
            spent[r['stage']] += 1
            launched_entries[r['stage']].add(r['entry_id'])
    stages = []
    for st, planned in stage_counts.items():
        ids = [e['id'] for e in M.get('runs', []) if e['stage'] == st]
        scored = sum(1 for i in ids if (entries.get(i) or {}).get('status') == 'REAL_ATLAS_SCORED')
        failed = sum(1 for i in ids if i in entries and entries[i]['status'] != 'REAL_ATLAS_SCORED')
        stages.append({'stage': st, 'planned': planned, 'entries_launched': len(launched_entries[st]),
                       'launches_spent': spent[st], 'scored': scored, 'failed': failed,
                       'retries': spent[st] - len(launched_entries[st]),
                       'progress': round(scored / planned, 4) if planned else None,
                       'matrix_status': dict(collections.Counter(e['status'] for e in M.get('runs', []) if e['stage'] == st))})
    retries_total = sum(s['retries'] for s in stages)
    reserve = M.get('reserve_launches')
    unmatched = [r['label'] for r in runs if r['c10'] and not r['stage']]
    if unmatched:
        warnings.append('C10 labels not in campaign_matrix.json (charged to the reserve): %s' % ', '.join(unmatched[:5]))
    # Every C10 launch that is not the first launch of a planned matrix entry comes out of the reserve: retries of
    # planned entries AND launches of entries outside campaign_matrix.json (e.g. new registered diagnostic entries).
    first_launches = sum(len(v) for v in launched_entries.values())
    reserve_used = len(c10_ids) - first_launches
    s0 = next((s for s in stages if s['stage'].startswith('S0')), None)
    budget = {
        'total_used': len(by), 'total_cap': cap, 'total_left': (cap - len(by)) if cap else None,
        'c10_used': len(c10_ids), 'c10_cap': c10_cap, 'c10_left': c10_cap - len(c10_ids),
        'c10_first': min(c10_ids) if c10_ids else None, 'c10_last': max(c10_ids) if c10_ids else None,
        'planned_launches': M.get('planned_launches'), 'reserve_launches': reserve,
        'planned_first_launches': first_launches, 'retries': retries_total, 'unplanned_launches': len(unmatched),
        'unplanned_labels': unmatched[:20],
        'reserve_used': reserve_used, 'reserve_left': (reserve - reserve_used) if reserve is not None else None,
        's0_reserve_used': s0['retries'] if s0 else None, 's0_reserve_max': 3,
        'exit_code_counts': dict(exit_counts), 'rows': len(rows),
    }

    # ---- verdicts (S1 rules)
    verdicts = []
    run2entry = {e['run_id']: e['id'] for e in entries.values() if e.get('run_id')}
    for fp in sorted(glob.glob(str(ANA / 'extract' / 'compare_*.json')) + glob.glob(str(ANA / 'profile' / 'check_*.json'))):
        try:
            d = cached(fp, load_json)
        except Exception as e:
            warnings.append('%s: %s' % (os.path.basename(fp), e))
            continue
        run = d.get('run') or d.get('native')
        v = str(d.get('verdict') or '')
        cls = 'PASS' if v.startswith('PASS') else 'FAIL' if v.startswith('FAIL') else 'UNVERIFIED' if v.startswith('UNVERIFIED') else 'OTHER'
        verdicts.append({'file': os.path.relpath(fp, ANA).replace('\\', '/'), 'run': run, 'ref': d.get('ref') or d.get('reference'),
                         'entry_id': run2entry.get(run), 'verdict': short(v, 200), 'class': cls, 'rule': short(d.get('rule'), 200),
                         'dVth_cc_mV': d.get('dVth_cc_mV'), 'dSS_mV_dec': d.get('dSS_fixed_mV_dec'),
                         'd_active_rmse_dec': d.get('d_active_rmse_dec'),
                         'max_dev_dec': d.get('max_abs_dev_native_grid_above_1e-14_dec'),
                         'mtime_utc': utc_iso(os.path.getmtime(fp))})
    for rec in entries.values():
        if rec['status'] == 'ERROR' and not any(v['run'] == rec['run_id'] for v in verdicts):
            rr = run_by_id.get(rec['run_id']) or {}
            timed_out = rr.get('exit_code') == 'timeout' or rr.get('timed_out') is True
            if timed_out:
                lim = rr.get('timeout_s') or rr.get('elapsed_s')
                text = 'TIMEOUT after %s s, %s/%s points, last V_G %s V' % (
                    ('%.0f' % lim) if lim is not None else '?', rec.get('points_logged') if rec.get('points_logged') is not None else '?',
                    rec.get('points_requested') or '?', rec.get('last_vg') if rec.get('last_vg') is not None else '?')
                cls = 'TIMEOUT'
            else:
                text, cls = 'UNRESOLVED: %s' % (rec['error'] or 'error'), 'UNRESOLVED'
            verdicts.append({'file': None, 'run': rec['run_id'], 'ref': None, 'entry_id': rec['id'],
                             'verdict': text, 'class': cls, 'detail': rec['error'],
                             'rule': None, 'points_logged': rec.get('points_logged'), 'last_vg': rec.get('last_vg'),
                             'points_requested': rec.get('points_requested')})
    verdicts.sort(key=lambda v: (v.get('entry_id') or 'ZZ', v.get('run') or ''))

    # rule outcomes per stage, kept apart from solver outcomes ('scored' / 'failed' above are solver results only)
    entry_stage = {e['id']: e['stage'] for e in M.get('runs', [])}
    for s in stages:
        vs = [v for v in verdicts if v.get('entry_id') and entry_stage.get(v['entry_id']) == s['stage']]
        s['rule_pass'] = sum(1 for v in vs if v['class'] == 'PASS')
        s['rule_fail'] = sum(1 for v in vs if v['class'] == 'FAIL')
        s['rule_other'] = sum(1 for v in vs if v['class'] not in ('PASS', 'FAIL'))

    # ---- post-run checks
    post = []
    for fp in sorted(glob.glob(str(ANA / 'post_run' / 'run_*.json'))):
        try:
            d = cached(fp, load_json)
        except Exception as e:
            warnings.append('%s: %s' % (os.path.basename(fp), e))
            continue
        fm = d.get('floor_metrics') or {}
        act = d.get('activation') or {}
        post.append({'run_id': d.get('run_id'), 'status_runner': d.get('status_runner'), 'model_file': d.get('model_file'),
                     'activation': act.get('status'), 'missing': act.get('missing') or [],
                     'valid_fraction': fm.get('valid_fraction'), 'sign_reversals': len(fm.get('sign_reversals_vg') or []),
                     'floor_ratio_dec': fm.get('floor_ratio_dec'), 'ig_ratio_dec': fm.get('ig_ratio_dec'),
                     'verdict_inputs': fm.get('verdict_inputs')})
    have_post = {p['run_id'] for p in post}
    post_missing = [r['run_id'] for r in runs if r['c10'] and r['status_final'] == 'REAL_ATLAS_SCORED' and r['run_id'] not in have_post]

    # ---- processes + active run
    procs = windows_processes()
    solver_alive = bool(procs['atlas'] or procs['deckbuild'])
    runner_alive = bool(procs['runner'])
    active = None
    state = 'IDLE'
    if newest:
        rd = PUB / newest['output_dir']
        in_progress = newest['finished_utc'] is None
        if in_progress:
            exj = (rd / 'execution.json').exists()
            tp = _transfer_progress(rd)
            live = _deckbuild_liveness(rd)
            el = time.time() - newest['started_epoch'] if newest['started_epoch'] else None
            if exj:
                state = 'FINISHING'
            elif procs['ok']:
                state = 'RUNNING' if (solver_alive or runner_alive) else 'STALE'
            else:  # process query failed: fall back to log activity
                state = 'RUNNING' if (live.get('age_s') is not None and live['age_s'] < 600) else 'STALE'
            to = newest['timeout_s']
            req = newest['points_requested']
            eta_rate = None
            if tp['points'] >= 3 and req and el:
                eta_rate = round(el / tp['points'] * (req - tp['points']))
            active = {'run_id': newest['run_id'], 'label': newest['label'], 'entry_id': newest['entry_id'],
                      'stage': newest['stage'], 'thickness_nm': newest['thickness_nm'],
                      'started_utc': newest['started_utc'], 'elapsed_s': round(el) if el else None,
                      'timeout_s': to, 'timeout_remaining_s': round(to - el) if (to and el) else None,
                      'eta_rate_s': eta_rate, 'points': tp['points'], 'points_requested': req,
                      'progress': round(tp['points'] / req, 4) if req else None,
                      'phase': 'ramp / initial solve' if tp['points'] == 0 else 'gate sweep',
                      'last_vg': tp['last_vg'], 'execution_json': exj, 'deckbuild': live,
                      'curve': tp['curve']}
        else:
            if runner_alive:
                state = 'BETWEEN_LAUNCHES'
            elif solver_alive:
                state = 'SOLVER_UNTRACKED'
    last_c10_scored = None
    for r in sorted(runs, key=lambda r: int(r['run_id'][4:]), reverse=True):
        if r['c10'] and r['status_final'] == 'REAL_ATLAS_SCORED':
            last_c10_scored = r
            break
    last_curve = None
    if last_c10_scored:
        cp = PUB / last_c10_scored['output_dir'] / 'comparison.csv'
        if cp.exists():
            try:
                with open(cp, encoding='utf-8', newline='') as f:
                    rdr = csv.DictReader(f)
                    pts = [[fnum(x.get('vg_V')), fnum(x.get('measured_A_per_um')), fnum(x.get('atlas_A_per_um')),
                            int(x.get('active_fit_region') or 0)] for x in rdr]
                last_curve = {'run_id': last_c10_scored['run_id'], 'label': last_c10_scored['label'],
                              'entry_id': last_c10_scored['entry_id'], 'columns': ['vg_V', 'measured_A_per_um', 'atlas_A_per_um', 'active'],
                              'points': pts}
            except Exception as e:
                warnings.append('comparison.csv: %s' % e)

    # ---- NC audit ladder
    nc_dir = ANA / 'nc_audit'
    nc_files = sorted(os.listdir(nc_dir)) if nc_dir.is_dir() else []
    if 'NC_AUDIT.md' in nc_files:
        nc_state = 'REPORT'
    elif procs['nc_audit']:
        nc_state = 'RUNNING'
    elif 'nc_audit_results.json' in nc_files:
        nc_state = 'RESULTS'
    elif 'nc_audit.py' in nc_files:
        nc_state = 'SCRIPT_ONLY'
    else:
        nc_state = 'ABSENT'
    nc = {'state': nc_state, 'files': [{'name': f, 'mtime_utc': utc_iso(os.path.getmtime(nc_dir / f)),
                                        'size': os.path.getsize(nc_dir / f)} for f in nc_files if not f.startswith('__')],
          'process': procs['nc_audit'][:2]}

    # ---- plans (config/campaign_C10_*.json)
    plans = []
    for fp in sorted(glob.glob(str(PUB / 'config' / 'campaign_C10_*.json'))):
        b = os.path.basename(fp)
        stem = b[len('campaign_C10_'):-len('.json')]
        template = stem.endswith('.template')
        try:
            d = cached(fp, load_json)
        except Exception as e:
            warnings.append('%s: %s' % (b, e))
            continue
        ids = [r.get('id') for r in d.get('runs', [])]
        done_ids = [i for i in ids if i in entries]
        plans.append({'plan': stem, 'template': template, 'runnable': bool(d.get('runnable')) and not template,
                      'n_entries': len(ids), 'n_recorded': len(done_ids),
                      'has_results': stem in plan_results, 'stop_rules': [short(x, 400) for x in d.get('stop_rules') or []],
                      'stop_rules_enforced_by': d.get('stop_rules_enforced_by'),
                      'next_entries': [{'id': r.get('id'), 'label': r.get('label'), 'thickness_nm': r.get('thickness'),
                                        'timeout_s': r.get('timeout'), 'purpose': short(r.get('purpose'), 200),
                                        'expectation': short(r.get('pre_registered_expectation'), 260)}
                                       for r in d.get('runs', []) if r.get('id') not in entries][:6]})
    next_plan = next((p['plan'] for p in plans if p['runnable'] and p['n_recorded'] < p['n_entries']
                      and p['plan'] != 'MIN10'), None)

    recent = sorted(runs, key=lambda r: int(r['run_id'][4:]), reverse=True)[:25]
    data = {
        'state': state, 'active_run': active, 'newest_run_id': newest['run_id'] if newest else None,
        'last_run': {k: newest.get(k) for k in ('run_id', 'label', 'entry_id', 'stage', 'thickness_nm', 'started_utc',
                                                'finished_utc', 'exit_code', 'converged', 'elapsed_s', 'status_final',
                                                'active_rmse_dec', 'Id3V_err_pct', 'max_kcl_A', 'notes')} if newest else None,
        'budget': budget, 'stages': stages, 'entries': sorted(entries.values(), key=lambda e: e['id']),
        'recent_runs': [{k: r.get(k) for k in ('run_id', 'label', 'entry_id', 'stage', 'thickness_nm', 'c10', 'started_utc',
                                               'finished_utc', 'exit_code', 'converged', 'elapsed_s', 'status_final',
                                               'status_notes', 'active_rmse_dec', 'Id3V_err_pct', 'nonpos', 'max_kcl_A',
                                               'timeout_s', 'points_requested', 'rescored', 'notes')} for r in recent],
        'verdicts': verdicts, 'post_run': post, 'post_run_missing': post_missing, 'nc_audit': nc,
        'processes': procs, 'plans': plans, 'next_plan': next_plan, 'plan_results': plan_results,
        'stop_rules_design': _safe(_stop_rules_design, warnings, []),
        'orphans': orphans, 'last_scored_curve': last_curve, 'warnings': warnings,
        'paths': {'run_index': str(PUB / 'results' / 'RUN_INDEX.csv'), 'analysis': str(ANA)},
    }
    return data


def _safe(fn, warnings, default):
    try:
        return fn()
    except Exception as e:
        warnings.append('%s: %s' % (fn.__name__, e))
        return default


# =============================================================================================== CERN
_CERN_LOCK = threading.Lock()
CERN_STATE = {'last_good': None, 'last_good_epoch': None, 'last_attempt_epoch': None, 'master': None,
              'last_error': None, 'runtime_s': None, 'structs_raw': None}


def cern_lock_busy():
    """True while a CERN query holds the lock (non-blocking probe)."""
    if _CERN_LOCK.acquire(blocking=False):
        _CERN_LOCK.release()
        return False
    return True


def ssh_master_alive():
    rc, out, err, sec = run_cmd(['ssh', '-O', 'check', '-o', 'BatchMode=yes', '-o', 'ControlPath=' + CERN_CP, CERN_HOST],
                                timeout=15)
    return rc == 0, sec, short((err or out).strip(), 160)


def cern_snapshot_lines():
    """Ship cern_snapshot.py as a base64 ARGUMENT over the existing master (ssh stdin = /dev/null). Read-only.
    CERN_SSH_OPTS makes the call fail (instead of dialling lxplus) if the master has gone since `ssh -O check`."""
    b64 = base64.b64encode(CERN_SNAPSHOT_PY.read_bytes()).decode()
    remote = 'echo %s | base64 -d | timeout 30 python3 -' % b64
    argv = ['ssh'] + CERN_SSH_OPTS + [CERN_HOST, remote]
    rc, out, err, sec = run_cmd(argv, timeout=45)
    recs = []
    bad = 0
    for ln in out.split('\n'):
        ln = ln.strip()
        if not ln:
            continue
        try:
            recs.append(json.loads(ln))
        except ValueError:
            bad += 1
    return rc, recs, short(err.strip(), 300), sec, bad


def _job_kind(a):
    cmd = a.get('Cmd') or ''
    if a.get('JobUniverse') == 7 or cmd.endswith('condor_dagman'):
        return 'dag'
    if cmd.endswith('relax_node.sh'):
        return 'relax'
    if cmd.endswith('final_node.sh'):
        return 'final'
    if cmd.endswith('val_node.sh'):
        return 'val'
    if cmd.endswith('ml_driver.sh'):
        return 'ml'
    iw = a.get('IWOJob') or ''          # per-run node scripts (e.g. the A15 pilot) keep the IWOJob naming
    if re.search(r'_relax_s\d+$', iw):
        return 'relax'
    if iw.endswith('_final'):
        return 'final'
    return 'other'


def _struct_base(n):
    """Structure of a job or DAG: 'aIO_0p8_s1_pilot' (a pilot/rescue DAG of the same run) -> 'aIO_0p8_s1'."""
    return re.sub(r'_pilot\d*$', '', n or '') or n


RE_IWOJOB = re.compile(r'^(.+)_(relax_s(\d+)|final)$')
RE_NAME = re.compile(r'^(aIWO|aIO)_(bulk|\d+p\d+)(?:_(Al2O3|comp))?_s(\d+)(?:_(bare))?$')


def name_info(n):
    m = RE_NAME.match(n or '')
    if not m:
        return {'family': None, 't_nm': None, 'variant': None, 'seed_tag': None}
    fam, t, sub, seed, bare = m.groups()
    variant = 'bulk' if t == 'bulk' else (sub or ('bare' if bare else 'std'))
    return {'family': fam, 't_nm': None if t == 'bulk' else float(t.replace('p', '.')), 'variant': variant,
            'seed_tag': 's' + seed}


def load_specs():
    specs = {}
    rounds = {}
    for fn, label, cl in ML_ROUNDS:
        p = AMORPH / fn
        try:
            for n in read_text(p).split():
                rounds[n] = {'round': label, 'cluster': cl, 'list': fn}
        except OSError:
            pass
    for fp in sorted(glob.glob(str(SPECS / 'spec_*.json'))):
        try:
            d = cached(fp, load_json)
        except Exception:
            continue
        n = d.get('name') or os.path.basename(fp)[5:-5]
        ni = name_info(n)
        nIn, nW, nO = d.get('n_In') or 0, d.get('n_W') or 0, d.get('n_O') or 0
        sub = d.get('substrate') or None
        atoms_pre = nIn + nW + nO + ((sub or {}).get('n_Al') or 0) + ((sub or {}).get('n_O') or 0)
        comp = '_comp_' in n
        variant = ('bulk' if d.get('mode') == 'bulk' else 'Al2O3' if sub else 'comp' if comp
                   else 'bare' if d.get('passivate') is False else 'std')
        specs[n] = {'name': n, 'mode': d.get('mode'), 'family': ni['family'] or ('aIWO' if nW else 'aIO'),
                    't_nm': d.get('thickness_nm', ni['t_nm']), 'variant': variant, 'seed_tag': ni['seed_tag'],
                    'seed': d.get('seed'), 'n_In': nIn, 'n_W': nW, 'n_O': nO,
                    'W_pct': round(100.0 * nW / (nIn + nW), 2) if (nIn + nW) else None,
                    'excess_e': 0 if comp else nW, 'atoms_pre_passivation': atoms_pre,
                    'lateral_A': d.get('lateral_A'), 'vacuum_A': d.get('vacuum_A'), 'passivate': d.get('passivate'),
                    'substrate': sub, 'density_gcc': d.get('density_gcc'), **(rounds.get(n) or {'round': None})}
    return specs


def gpus_for_atoms(n):
    if not n:
        return None
    return 1 if n <= 200 else (2 if n <= 350 else 4)


def _args_limit(args):
    """Wall limit (s) from a node's Args: the last integer >= 600 ('1 72000' -> 72000, '250000' -> 250000)."""
    nums = [int(x) for x in re.findall(r'\b\d+\b', str(args or ''))]
    nums = [x for x in nums if x >= 600]
    return nums[-1] if nums else None


def node_limit_s(node, atoms):
    """Wall limit of the running relax/final node: from its Args, else the make_dft.py rule."""
    if not node:
        return None
    if node.get('limit_s'):
        return node['limit_s']
    if node.get('kind') == 'final':
        return FINAL_LIMIT_BIG_S if (atoms or 0) > FINAL_BIG_ATOMS else FINAL_LIMIT_S
    return SEGMENT_LIMIT_S


def build_cern(recs, specs):
    by = collections.defaultdict(list)
    for r in recs:
        by[r.get('k')].append(r)
    meta = (by.get('meta') or [{}])[0]
    server_now = meta.get('now') or time.time()
    jobs = []
    for a in by.get('job', []):
        cmd = a.get('Cmd') or ''
        if not ('/iwo_amorph/' in cmd or a.get('JobUniverse') == 7):
            continue
        k = _job_kind(a)
        st = a.get('JobStatus')
        stime = a.get('ServerTime') or server_now
        j = {'cluster': a.get('ClusterId'), 'proc': a.get('ProcId'), 'kind': k, 'status': JOB_STATUS.get(st, str(st)),
             'status_code': st, 'batch': a.get('JobBatchName'), 'iwojob': a.get('IWOJob'), 'node': a.get('DAGNodeName'),
             'dagman_id': a.get('DAGManJobId'), 'gpus': a.get('RequestGpus'), 'cpus': a.get('RequestCpus'),
             'mem_mb': a.get('RequestMemory'), 'flavour': a.get('JobFlavour'), 'host': (a.get('RemoteHost') or '').split('@')[-1] or None,
             'starts': a.get('NumJobStarts'), 'gpu_mem_mb': a.get('GPUsMemoryUsage'), 'gpu_util': a.get('GPUsAverageUsage'),
             'rss_gb': round(a['ResidentSetSize'] / 1048576.0, 2) if a.get('ResidentSetSize') else None,
             'hold_reason': short(a.get('HoldReason'), 200), 'hold_code': a.get('HoldReasonCode'),
             'qdate_utc': utc_iso(a['QDate']) if a.get('QDate') else None,
             'running_h': round((stime - a['JobCurrentStartDate']) / 3600.0, 2) if st == 2 and a.get('JobCurrentStartDate') else None,
             'in_status_h': round((stime - a['EnteredCurrentStatus']) / 3600.0, 2) if a.get('EnteredCurrentStatus') else None}
        m = RE_IWOJOB.match(a.get('IWOJob') or '')
        if m and k in ('relax', 'final'):
            j['struct'] = _struct_base(m.group(1))
            j['seg'] = int(m.group(3)) if m.group(3) else None
            # wall limit passed to the node script (relax: '$(seg) 72000'; final: '72000' or '250000', see make_dft.py)
            j['limit_s'] = _args_limit(a.get('Args')) or (SEGMENT_LIMIT_S if k == 'relax' else None)
            j['segment_used_frac'] = (round(j['running_h'] * 3600 / j['limit_s'], 3)
                                      if j['running_h'] is not None and j['limit_s'] else None)
        elif k == 'val':
            j['struct'] = (a.get('IWOJob') or '')[4:] or None
        elif k == 'ml':
            j['struct'] = a.get('IWOJob')
        elif k == 'dag':
            j['struct'] = _struct_base(a.get('JobBatchName'))
            j['dag_batch'] = a.get('JobBatchName')
            j['dag'] = {x[4:]: a.get(x) for x in ('DAG_Status', 'DAG_InRecovery', 'DAG_NodesTotal', 'DAG_NodesDone',
                                                  'DAG_NodesFailed', 'DAG_NodesQueued', 'DAG_NodesReady', 'DAG_NodesUnready',
                                                  'DAG_JobsIdle', 'DAG_JobsRunning', 'DAG_JobsHeld', 'DAG_JobsCompleted') if x in a}
        jobs.append(j)

    counts = collections.defaultdict(lambda: collections.Counter())
    for j in jobs:
        counts[j['kind']][j['status']] += 1
    total = collections.Counter(j['status'] for j in jobs if j['kind'] != 'dag')
    running_nodes = [j for j in jobs if j['kind'] != 'dag' and j['status'] == 'running']
    summary = {'jobs_total': sum(total.values()), 'by_status': dict(total), 'by_kind': {k: dict(v) for k, v in counts.items()},
               'dags_in_queue': sum(1 for j in jobs if j['kind'] == 'dag'),
               'held': sum(1 for j in jobs if j['status'] == 'held'),
               'gpus_in_use': sum(j['gpus'] or 0 for j in running_nodes),
               'gpus_requested_idle': sum(j['gpus'] or 0 for j in jobs if j['status'] == 'idle' and j['kind'] != 'dag'),
               'gpu_mem_used_gb': round(sum(j['gpu_mem_mb'] or 0 for j in running_nodes) / 1024.0, 1),
               'cpus_in_use': sum(j['cpus'] or 0 for j in running_nodes)}

    runs = {r['name']: r for r in by.get('run', [])}
    structs = {r['name']: r for r in by.get('struct', [])}
    q_ok = any(x.get('name') == 'condor_q' and x.get('rc') == 0 for x in by.get('src', []))
    summary['queue_ok'] = q_ok
    summary['history_ok'] = any(x.get('name') == 'condor_history' and x.get('rc') == 0 for x in by.get('src', []))
    jobs_by_struct = collections.defaultdict(list)
    for j in jobs:
        if j.get('struct'):
            jobs_by_struct[j['struct']].append(j)

    names = sorted(set(specs) | set(structs) | set(runs))
    rows = []
    for n in names:
        sp = specs.get(n) or {}
        ni = name_info(n)
        s = structs.get(n) or {}
        r = runs.get(n)
        st = s.get('state') or []
        js = jobs_by_struct.get(n, [])
        dagjob = next((j for j in js if j['kind'] == 'dag'), None)
        nodejobs = sorted([j for j in js if j['kind'] in ('relax', 'final')], key=lambda j: (j['status'] != 'running', -(j.get('seg') or 0)))
        node = nodejobs[0] if nodejobs else None
        mljob = next((j for j in js if j['kind'] == 'ml'), None)
        atoms = s.get('qc_n_atoms') or sp.get('atoms_pre_passivation')
        is_bulk = '_bulk_' in n or sp.get('mode') == 'bulk'
        segs = sorted((r or {}).get('segs') or [], key=lambda x: (x.get('seg') is None, x.get('seg')))
        finished = [x for x in segs if x.get('status')]
        last_seg = finished[-1] if finished else None
        final_tgz = (r or {}).get('final_tgz')
        flags = []
        # ---- pipeline stage + display state
        level = 'ok'
        if 'rejected' in st:
            stage, level = 'REJECTED (replaced by next seed)', 'muted'
        elif is_bulk:
            stage, level = 'BULK: force-check source only', 'muted'
        elif not s.get('ml_tgz') and not st:
            stage = 'ML running' if mljob else 'ML pending'
            level = 'info'
        elif 'dag' not in st:
            stage, level = 'COLLECTED, DFT not started', 'warn'
        else:
            relax_converged = (last_seg or {}).get('status') == 'CONVERGED' or (r or {}).get('relax_status') == 'CONVERGED'
            dag_failed_reasons = []
            if r:
                if r.get('rescue'):
                    dag_failed_reasons.append('rescue file')
                if r.get('dag_exit') not in (None, 0):
                    dag_failed_reasons.append('dagman exit %s' % r.get('dag_exit'))
                if last_seg and last_seg.get('status') == 'FAILED' and (last_seg.get('seg') or 0) >= DAG_RETRIES:
                    dag_failed_reasons.append('segment %s FAILED (last retry)' % last_seg.get('seg'))
                if final_tgz is not None and final_tgz.get('size') == 0:
                    dag_failed_reasons.append('final_results.tar.gz empty')
            if dagjob and (dagjob.get('dag') or {}).get('NodesFailed'):
                dag_failed_reasons.append('DAG_NodesFailed=%s' % dagjob['dag']['NodesFailed'])
            if q_ok and not dagjob and not (r or {}).get('dag_done'):
                dag_failed_reasons.append('dagman left the queue without completing')
            if (r or {}).get('dag_done') and final_tgz and final_tgz.get('size'):
                stage, level = 'DONE (final SCF complete)', 'done'
            elif dag_failed_reasons:
                stage, level = 'DAG FAILED', 'crit'
                flags.extend(dag_failed_reasons)
            elif relax_converged:
                if node and node['kind'] == 'final':
                    stage = 'FINAL SCF %s' % node['status']
                else:
                    stage = 'RELAX CONVERGED, final pending'
            elif ((last_seg and last_seg.get('status') == 'FAILED') or
                  (not last_seg and (r or {}).get('relax_status') == 'FAILED')):
                # RELAX_STATUS / last segment FAILED: a real relaxation failure (crit), even while DAGMan retries it
                k = (last_seg or {}).get('seg') or 0
                nxt = next((j for j in nodejobs if j.get('seg') == k + 1), None)
                if nxt:
                    stage = 'FAILED s%d, retry %d/%d %s' % (k, k + 1, DAG_RETRIES, nxt['status'])
                else:
                    stage = 'FAILED s%d, waiting for retry' % k
                level = 'crit'
                if (last_seg or {}).get('bfgs') == 0:
                    flags.append('no progress (0 BFGS steps; next segment restarts from the same geometry)')
            elif node:
                stage = 'RELAX s%s %s' % (node.get('seg'), node['status'])
                level = 'ok' if node['status'] == 'running' else 'info'
            else:
                stage = 'DAG queued'
                level = 'info'
            if dagjob and dagjob.get('dag_batch') and dagjob['dag_batch'] != n and stage != 'DAG FAILED':
                stage += ' · DAG %s' % dagjob['dag_batch']     # e.g. the A15 pilot DAG
            if node and node['status'] == 'held':
                level = 'crit'
                flags.append('HELD: %s' % (node.get('hold_reason') or ''))
        segs_done = len([x for x in segs if x.get('status')])
        lim = node_limit_s(node, atoms)
        used = (round(node['running_h'] * 3600 / lim, 3)
                if node and node.get('running_h') is not None and lim else None)
        row = {'name': n, 'family': sp.get('family') or ni['family'], 't_nm': sp.get('t_nm', ni['t_nm']),
               'variant': sp.get('variant') or ni['variant'], 'seed_tag': sp.get('seed_tag') or ni['seed_tag'],
               'mode': sp.get('mode'), 'W_pct': sp.get('W_pct'), 'excess_e': sp.get('excess_e'),
               'atoms': atoms, 'atoms_pre_passivation': sp.get('atoms_pre_passivation'),
               'gpus': (node or {}).get('gpus') or (gpus_for_atoms(atoms) if ('dag' in st and not is_bulk) else None),
               'gpus_rule': gpus_for_atoms(atoms) if not is_bulk else None,
               'ml_round': sp.get('round'), 'ml_done': bool(s.get('ml_tgz')),
               'ml_exit': s.get('ml_exit'), 'qc': s.get('qc_QC'), 'qc_reasons': s.get('qc_QC_reasons') or [],
               'collected': 'collected' in st, 'accepted': 'dag' in st, 'rejected': 'rejected' in st,
               'gpuoom_resubmitted': bool(s.get('old')), 'bulk': is_bulk,
               'condor_status': (node or {}).get('status'), 'node_kind': (node or {}).get('kind'),
               'node_seg': (node or {}).get('seg'), 'host': (node or {}).get('host'),
               'running_h': (node or {}).get('running_h'), 'idle_h': (node or {}).get('in_status_h') if (node or {}).get('status') == 'idle' else None,
               'segment_used_frac': used, 'segment_limit_s': lim, 'starts': (node or {}).get('starts'),
               'gpu_mem_gb': round(node['gpu_mem_mb'] / 1024.0, 1) if node and node.get('gpu_mem_mb') else None,
               'relax_segments': [{k: x.get(k) for k in ('seg', 'status', 'bfgs', 'cluster')} for x in segs],
               'segments_done': segs_done,
               'relax_status': (r or {}).get('relax_status'),
               'relax_status_utc': utc_iso(r['relax_status_mtime']) if r and r.get('relax_status_mtime') else None,
               'last_retry': (r or {}).get('last_retry'), 'dag_status': (r or {}).get('dag_status'),
               'dag_cluster': (dagjob or {}).get('cluster'), 'dag_batch': (dagjob or {}).get('dag_batch'),
               'dag_file': (r or {}).get('dag_file'), 'dag_lock': (r or {}).get('lock'),
               'dag_done': (r or {}).get('dag_done'), 'final_done': bool((r or {}).get('dag_done') and final_tgz and final_tgz.get('size')),
               'node_table': (r or {}).get('node_table'),
               'dagman_out_age_s': round(server_now - r['dagman_out']['mtime']) if r and r.get('dagman_out') else None,
               'qc_detail': {k[3:]: s.get(k) for k in ('qc_t_eq_A', 'qc_vacuum_A', 'qc_lateral_min_A', 'qc_n_water',
                                                       'qc_water_removed', 'qc_n_short_OO', 'qc_W_W_min_A',
                                                       'qc_final_max_force_eV_A', 'qc_md_ps') if k in s},
               'stage': stage, 'level': level, 'flags': flags}
        rows.append(row)

    val = []
    vjobs = {j['struct']: j for j in jobs if j['kind'] == 'val'}
    for v in by.get('val', []):
        j = vjobs.get(v['name'])
        val.append({'name': v['name'], 'results': bool(v.get('results') and v['results'].get('size')),
                    'outs': v.get('outs') or [], 'status': (j or {}).get('status') or ('done' if v.get('results') else 'not in queue'),
                    'cluster': (j or {}).get('cluster'), 'cpus': (j or {}).get('cpus'), 'mem_mb': (j or {}).get('mem_mb'),
                    'in_status_h': (j or {}).get('in_status_h'), 'running_h': (j or {}).get('running_h'),
                    'host': (j or {}).get('host')})
    hist = []
    for a in by.get('hist', []):
        k = _job_kind(a)
        hist.append({'cluster': a.get('ClusterId'), 'kind': k, 'job': a.get('IWOJob') or a.get('JobBatchName'),
                     'batch': a.get('JobBatchName'), 'status': JOB_STATUS.get(a.get('JobStatus'), a.get('JobStatus')),
                     'exit_code': a.get('ExitCode'), 'by_signal': a.get('ExitBySignal'),
                     'wall_h': round(a['RemoteWallClockTime'] / 3600.0, 2) if a.get('RemoteWallClockTime') is not None else None,
                     'ended_utc': utc_iso(a.get('CompletionDate') or a.get('EnteredCurrentStatus')) if (a.get('CompletionDate') or a.get('EnteredCurrentStatus')) else None,
                     'ended_epoch': a.get('CompletionDate') or a.get('EnteredCurrentStatus'),
                     'remove_reason': short(a.get('RemoveReason'), 120), 'last_hold': short(a.get('LastHoldReason'), 120),
                     'host': (a.get('LastRemoteHost') or '').split('@')[-1] or None, 'starts': a.get('NumJobStarts')})
    hist.sort(key=lambda h: h.get('ended_epoch') or 0, reverse=True)
    quota = (by.get('quota') or [None])[0]
    srcs = {s['name']: {k: s.get(k) for k in ('rc', 'sec', 'n')} for s in by.get('src', [])}
    done = (by.get('done') or [None])[0]
    stage_counts = collections.Counter()
    for r in rows:
        stage_counts[r['level']] += 1
    pipe = {'structures': len(rows), 'ml_done': sum(1 for r in rows if r['ml_done']),
            'qc_pass': sum(1 for r in rows if r['qc'] == 'PASS'),
            'accepted_dft': sum(1 for r in rows if r['accepted']), 'rejected': sum(1 for r in rows if r['rejected']),
            'bulk': sum(1 for r in rows if r['bulk']), 'dft_runs': len(runs),
            'relax_running': sum(1 for r in rows if r['node_kind'] == 'relax' and r['condor_status'] == 'running'),
            'relax_idle': sum(1 for r in rows if r['node_kind'] == 'relax' and r['condor_status'] == 'idle'),
            'relax_converged': sum(1 for r in rows if r['relax_status'] == 'CONVERGED'),
            'last_segment_failed': sum(1 for r in rows if (r['relax_segments'] and [x for x in r['relax_segments'] if x['status']] and
                                                         [x for x in r['relax_segments'] if x['status']][-1]['status'] == 'FAILED')),
            'segments_done': sum(r['segments_done'] for r in rows),
            'final_running': sum(1 for r in rows if r['node_kind'] == 'final' and r['condor_status'] == 'running'),
            'final_done': sum(1 for r in rows if r['final_done']),
            'dag_failed': sum(1 for r in rows if r['level'] == 'crit' and r['stage'] == 'DAG FAILED'),
            'relax_failed': sum(1 for r in rows if r['stage'].startswith('FAILED')),
            'by_level': dict(stage_counts)}
    return {'meta': {k: meta.get(k) for k in ('host', 'now', 'schema', 'root')},
            'remote_now_utc': utc_iso(server_now), 'summary': summary, 'pipeline_summary': pipe,
            'pipeline': rows, 'jobs': sorted(jobs, key=lambda j: (j['kind'], j['status'], j.get('struct') or '')),
            'validation': {'submitted': (by.get('valstate') or [{}])[0].get('submitted'),
                           'n_jobs': (by.get('valstate') or [{}])[0].get('n_jobs'), 'jobs': val,
                           'results': sum(1 for v in val if v['results'])},
            'history': hist, 'quota': quota, 'failed_dirs': (by.get('failed_dirs') or [{}])[0].get('dirs') or [],
            'sources': srcs, 'remote_sec': (done or {}).get('sec'), 'complete': done is not None,
            'n_records': len(recs)}


def cern_refresh(min_gap=CERN_MIN_GAP_S):
    """The ONLY entry point for a CERN query. Under one lock: refuse when another CERN query is running ('busy') or the
    last attempt started less than `min_gap` s ago ('too_soon'); otherwise run one snapshot ('ran').
    The check and the query are atomic, so no two callers (scheduled loop, manual refresh) can query CERN back to back.
    Returns (outcome, envelope or None, retry_after_s or None)."""
    if not _CERN_LOCK.acquire(blocking=False):
        return 'busy', None, 30
    try:
        last = CERN_STATE['last_attempt_epoch']
        gap = time.time() - last if last else None
        if gap is not None and min_gap and 0 <= gap < min_gap:   # gap < 0: clock went back; allow
            return 'too_soon', None, int(min_gap - gap) + 1
        return 'ran', envelope(_cern_snapshot_locked), None
    finally:
        _CERN_LOCK.release()


def _cern_snapshot_locked():
    """Collector body; the caller holds _CERN_LOCK. Keeps the last good snapshot when a refresh fails."""
    t0 = time.time()
    CERN_STATE['last_attempt_epoch'] = t0
    alive, sec_chk, msg = ssh_master_alive()
    CERN_STATE['master'] = alive
    res = {'master': alive, 'master_check_s': sec_chk, 'last_attempt_utc': utc_iso(t0)}
    if not alive:
        CERN_STATE['last_error'] = 'NO_SSH_MASTER'
        res.update(_cern_last_good())
        res['__ok__'] = False
        res['__error__'] = 'NO_SSH_MASTER: the SSH master to lxplus is gone; log in again (no CERN access attempted)'
        return res
    try:
        specs = load_specs()
    except Exception:
        specs = {}
    rc, recs, err, sec, bad = cern_snapshot_lines()
    runtime = round(time.time() - t0, 2)
    CERN_STATE['runtime_s'] = runtime
    if recs and recs[0].get('k') == 'error':
        CERN_STATE['last_error'] = recs[0].get('error')
        res.update(_cern_last_good())
        res['__ok__'] = False
        res['__error__'] = 'remote: %s' % recs[0].get('error')
        return res
    if not any(r.get('k') == 'meta' for r in recs):
        CERN_STATE['last_error'] = 'snapshot failed rc=%s %s' % (rc, err)
        res.update(_cern_last_good())
        res['__ok__'] = False
        res['__error__'] = 'snapshot failed (rc %s, %.1f s): %s' % (rc, sec, err or 'no output')
        return res
    snap = build_cern(recs, specs)
    snap['runtime_s'] = runtime
    snap['ssh_rc'] = rc
    snap['bad_lines'] = bad
    CERN_STATE['structs_raw'] = [r for r in recs if r.get('k') == 'struct']
    CERN_STATE['last_good'] = snap
    CERN_STATE['last_good_epoch'] = time.time()
    CERN_STATE['last_error'] = None
    res.update(snap)
    res['snapshot_utc'] = utc_iso(CERN_STATE['last_good_epoch'])
    res['snapshot_age_s'] = 0
    res['stale'] = False
    if rc != 0 or not snap['complete']:
        res['__ok__'] = False
        res['__error__'] = 'partial snapshot (ssh rc %s, done record %s): %s' % (rc, snap['complete'], err)
    return res


def _cern_last_good():
    lg = CERN_STATE.get('last_good')
    if not lg:
        return {'stale': True, 'snapshot_utc': None, 'snapshot_age_s': None}
    d = dict(lg)
    d['stale'] = True
    d['snapshot_utc'] = utc_iso(CERN_STATE['last_good_epoch'])
    d['snapshot_age_s'] = round(time.time() - CERN_STATE['last_good_epoch'])
    return d


def cern_history_point(snap):
    """Compact counts-only point for history.jsonl."""
    s, p = snap.get('summary') or {}, snap.get('pipeline_summary') or {}
    bk = s.get('by_kind') or {}
    q = snap.get('quota') or {}
    return {'t': int(time.time()), 'run': (s.get('by_status') or {}).get('running', 0),
            'idle': (s.get('by_status') or {}).get('idle', 0), 'held': s.get('held', 0),
            'relax_run': (bk.get('relax') or {}).get('running', 0), 'relax_idle': (bk.get('relax') or {}).get('idle', 0),
            'final_run': (bk.get('final') or {}).get('running', 0), 'val_idle': (bk.get('val') or {}).get('idle', 0),
            'val_run': (bk.get('val') or {}).get('running', 0), 'dags': s.get('dags_in_queue', 0),
            'gpus': s.get('gpus_in_use', 0), 'gpu_mem_gb': s.get('gpu_mem_used_gb', 0),
            'segs': p.get('segments_done', 0), 'seg_failed': p.get('last_segment_failed', 0),
            'converged': p.get('relax_converged', 0), 'final_done': p.get('final_done', 0),
            'dag_failed': p.get('dag_failed', 0), 'val_results': (snap.get('validation') or {}).get('results', 0),
            'quota_pct': q.get('pct')}


# =============================================================================================== ML
def collect_ml():
    specs = load_specs()
    structs = {r['name']: r for r in CERN_STATE.get('structs_raw') or []}
    rows = []
    for n, sp in specs.items():
        s = structs.get(n) or {}
        st = s.get('state') or []
        rows.append({**{k: sp.get(k) for k in ('name', 'family', 't_nm', 'variant', 'seed_tag', 'seed', 'mode', 'W_pct',
                                               'excess_e', 'atoms_pre_passivation', 'lateral_A', 'round', 'cluster')},
                     'ml_done': bool(s.get('ml_tgz')) if s else None,
                     'ml_exit': s.get('ml_exit'), 'qc': s.get('qc_QC'), 'qc_reasons': s.get('qc_QC_reasons') or [],
                     'vacuum_only_fail': bool(s.get('qc_QC') == 'FAIL' and s.get('qc_QC_reasons') and
                                              all(x.startswith('vacuum gap') for x in s['qc_QC_reasons'])),
                     'atoms_dft': s.get('qc_n_atoms'), 'state': st, 'rejected': 'rejected' in st, 'accepted': 'dag' in st,
                     't_eq_A': s.get('qc_t_eq_A'), 'n_water': s.get('qc_n_water'), 'water_removed': s.get('qc_water_removed'),
                     'final_max_force_eV_A': s.get('qc_final_max_force_eV_A'),
                     'qc_detail': {k[3:]: s.get(k) for k in ('qc_vacuum_A', 'qc_lateral_min_A', 'qc_md_ps',
                                                             'qc_final_max_force_eV_A') if k in s}})
    names = set(specs)
    repl = []
    for r in rows:
        if r['rejected']:
            m = re.match(r'^(.*_s)(\d+)(.*)$', r['name'])
            cand = '%s%d%s' % (m.group(1), int(m.group(2)) + 1, m.group(3)) if m else None
            rr = next((x for x in rows if x['name'] == cand), None)
            repl.append({'rejected': r['name'], 'reasons': r['qc_reasons'], 'replacement': cand if cand in names else None,
                         'replacement_state': (rr or {}).get('state'), 'replacement_qc': (rr or {}).get('qc')})
    have = bool(structs)
    summary = {'specs': len(specs), 'ml_done': sum(1 for r in rows if r['ml_done']) if have else None,
               'qc_pass': sum(1 for r in rows if r['qc'] == 'PASS') if have else None,
               'qc_fail_vacuum_only_accepted': sum(1 for r in rows if r['vacuum_only_fail'] and r['accepted']) if have else None,
               'rejected': sum(1 for r in rows if r['rejected']) if have else None,
               'accepted_dft': sum(1 for r in rows if r['accepted']) if have else None,
               'bulk': sum(1 for r in rows if r['mode'] == 'bulk'),
               'by_round': dict(collections.Counter(r['round'] for r in rows)),
               'by_family': dict(collections.Counter(r['family'] for r in rows)),
               'by_variant': dict(collections.Counter(r['variant'] for r in rows))}
    return {'summary': summary, 'structures': sorted(rows, key=lambda r: (r['family'] or '', r['t_nm'] or 99, r['name'])),
            'replacements': repl,
            'qc_source': 'CERN snapshot %s' % utc_iso(CERN_STATE['last_good_epoch']) if have else 'none yet (needs one CERN snapshot)',
            'qc_source_age_s': round(time.time() - CERN_STATE['last_good_epoch']) if have else None}


# =============================================================================================== Codex
RE_ENTRY = re.compile(r'^## (\d{4}-\d\d-\d\dT\d\d:\d\dZ): Claude to Codex: (.+?)(?: \(model ([^,()]+), effort ([^)]+)\))?$', re.M)
RE_REPLY = re.compile(r'^### Codex reply \(([^)]*)\)$', re.M)
RE_DECISION = re.compile(r'^### Claude decision$', re.M)
# "**1. Verdict: CONCERN \u2014 text**", "**Verdict: FIX_FIRST. text**", "**1. Verdict: STOP.** text", "Verdict: OK"
RE_VERDICT = re.compile(r'^[^\w\n]*(?:\d\.[ \t]*)?\**[ \t]*(?:\d\.[ \t]*)?Verdict\**[ \t]*:?[ \t]*\**[ \t]*'
                        r'([A-Z][A-Z_-]*[A-Z])\b\**[ \t]*[.:;]?[ \t]*\**[ \t]*(?:[\u2014\u2013-][ \t]*)?(.*?)\**[ \t]*$', re.M)
# Fallback when the reply has no "Verdict" line: a bold verdict word opening the reply ("**FREEZE_OK_WITH_EDITS.** text")
VERDICT_WORDS = r'FREEZE_OK_WITH_EDITS|FREEZE_OK|FREEZE_READY|FIX_FIRST|CONCERN|PROCEED|NO_GO|STOP|OK|GO'
RE_VERDICT_LEAD = re.compile(r'^[^\w\n]*\*\*[ \t]*(' + VERDICT_WORDS + r')\b[ \t]*[.:;]?[ \t]*\*\*[ \t]*[.:;]?[ \t]*'
                             r'(?:[\u2014\u2013-][ \t]*)?(.*?)[ \t]*$')
RE_ANY_ENTRY = re.compile(r'^## \d{4}-\d\d-\d\dT\d\d:\d\d', re.M)   # any dated section (exchanges and action notes)


def parse_verdict(reply):
    """(verdict word, text) from a Codex reply, or (None, None)."""
    v = RE_VERDICT.search(reply)
    if v:
        return v.group(1), (v.group(2) or None)
    first = next((ln for ln in reply.split('\n') if ln.strip()), '')
    m = RE_VERDICT_LEAD.match(first)
    if m:
        return m.group(1), (m.group(2) or None)
    return None, None
RE_DEC_DATE = re.compile(r'\*\*Decision \(Claude, (\d{4}-\d\d-\d\d)\)')
RE_DEC_INLINE = re.compile(r'\*\*Decision \(Claude, [^)]*\)[:.]?\s*([^.*]+)')
RE_DEC_WORD = re.compile(r'(not adopted|partly adopted|adopted|rejected|deferred|proposed)', re.I)
RE_DEC_SUB = re.compile(r'^\*\*(Adopted|Partly adopted|Not adopted|Proposed to the user)\*\*\s*$', re.M)
RE_ALOG = [
    ('no_change', re.compile(r'^(\d{4}-\d\d-\d\d \d\d:\d\d) no change, not sent$')),
    ('not_sent', re.compile(r'^(\d{4}-\d\d-\d\d \d\d:\d\d) NOT sent \(rc (\d+)\): (.*)$')),
    ('sent', re.compile(r'^(\d{4}-\d\d-\d\d \d\d:\d\d) sent; (.*)$')),
    ('stop_date', re.compile(r'^(\d{4}-\d\d-\d\d) past 21 Oct, stop$')),
]


def parse_work_chat(txt):
    hs = list(RE_ENTRY.finditer(txt))
    out = []
    for i, m in enumerate(hs):
        end = hs[i + 1].start() if i + 1 < len(hs) else len(txt)
        nxt = RE_ANY_ENTRY.search(txt, m.end(), end)   # an action note ("## <time>: Claude, action note") ends it too
        body = txt[m.end(): nxt.start() if nxt else end]
        rp = RE_REPLY.search(body)
        dcs = list(RE_DECISION.finditer(body))
        reply = body[rp.end(): dcs[-1].start()] if rp and dcs else (body[rp.end():] if rp else '')
        vw, vt = parse_verdict(reply)
        dec = body[dcs[-1].end():].strip() if dcs else ''
        dec = re.split(r'\n---\s*(?:\n|$)', dec)[0].strip()
        first = next((ln.strip() for ln in dec.split('\n') if ln.strip()), '')
        pending = (not dcs) or first.startswith('_pending_') or not first
        dd = RE_DEC_DATE.search(dec)
        outcomes = []
        mi = RE_DEC_INLINE.search(first)
        outcome_text = mi.group(1).strip() if mi else None
        if outcome_text:
            mw = RE_DEC_WORD.match(outcome_text)
            if mw:
                outcomes.append(mw.group(1).lower())
        outcomes += [x.lower() for x in RE_DEC_SUB.findall(dec)]
        topic = m.group(2)
        out.append({'ts_utc': m.group(1), 'epoch': parse_utc(m.group(1)), 'topic': topic, 'model': m.group(3),
                    'effort': m.group(4), 'kind': 'periodic' if topic.startswith('Periodic monitor') else 'milestone',
                    'reply_ts': rp.group(1) if rp else None, 'replied': bool(rp),
                    'verdict': vw, 'verdict_text': short(vt, 300) if vt else None,
                    'decision': {'pending': pending, 'date': dd.group(1) if dd else None,
                                 'outcomes': sorted(set(outcomes)), 'outcome_text': short(outcome_text, 160),
                                 'first_line': short(first, 260)}})
    return out


def _proc_table():
    """All Linux processes: pid -> {ppid, comm, args[], etimes}."""
    try:
        clk = os.sysconf('SC_CLK_TCK')
        with open('/proc/uptime') as f:
            up = float(f.read().split()[0])
    except (OSError, ValueError):
        return {}
    tab = {}
    for d in os.listdir('/proc'):
        if not d.isdigit():
            continue
        try:
            with open('/proc/%s/cmdline' % d, 'rb') as f:
                args = [a.decode('utf-8', 'replace') for a in f.read().split(b'\0') if a]
            with open('/proc/%s/stat' % d) as f:
                st = f.read()
            rpar = st.rfind(')')
            comm = st[st.find('(') + 1:rpar]
            fields = st[rpar + 2:].split()
            ppid = int(fields[1])
            start = int(fields[19]) / clk
            tab[int(d)] = {'ppid': ppid, 'comm': comm, 'args': args, 'etimes': round(up - start, 1)}
        except (OSError, ValueError, IndexError):
            continue
    return tab


_SESSION_CACHE = {'sid': None, 'path': None, 'checked': 0}
AUTODIGEST_CYCLES = 30            # codex_autodigest.sh N (default); the real N is in the process environment, never read
_LOOP_MEMO = {}                   # pid -> {ends_epoch, last_seen}: loops seen by this server process


def _autodigest_state(loops, alog, now):
    """'running' | 'finished' (the loops ran their N cycles) | 'stopped_by_codex' (STOP verdict) |
    'stopped_after_end_date' (past 21 Oct) | 'not_running' (gone early: crashed or killed). Returns (state, ended_epoch)."""
    if loops:
        return 'running', None
    if alog.get('stop_verdict_seen'):
        return 'stopped_by_codex', None
    if (alog.get('last') or {}).get('kind') == 'stop_date':
        return 'stopped_after_end_date', (alog['last'] or {}).get('epoch')
    if _LOOP_MEMO:
        ends = max(v['ends_epoch'] for v in _LOOP_MEMO.values())
        gone = max(v['last_seen'] for v in _LOOP_MEMO.values())
        # each cycle also spends time on the digest and the Codex call, so a loop that ran all N cycles ends AFTER
        # start + N * interval; vanishing before that estimate (2 min slack) means it was killed or crashed
        return ('finished', gone) if gone >= ends - 120 else ('not_running', gone)
    cycles = sum((alog.get('counts') or {}).get(k, 0) for k in ('no_change', 'not_sent', 'sent'))
    if cycles >= AUTODIGEST_CYCLES:            # this server never saw the loops; the log shows a full run
        return 'finished', (alog.get('last') or {}).get('epoch')
    return 'not_running', None


def _session_file(sid):
    """Path of the Codex session file whose name contains `sid` (walks file NAMES only; never opens a file)."""
    base = os.path.expanduser('~/.codex/sessions')
    c = _SESSION_CACHE
    if c['sid'] == sid and c['path'] and os.path.exists(c['path']):
        return c['path']
    if c['sid'] == sid and time.time() - c['checked'] < 600:
        return c['path']
    path = None
    for dp, dn, fns in os.walk(base):
        for fn in fns:
            if sid in fn:
                path = os.path.join(dp, fn)
                break
        if path:
            break
    c.update(sid=sid, path=path, checked=time.time())
    return path


def collect_codex():
    warnings = []
    chat_p = CHAT / 'CODEX_WORK_CHAT.md'
    entries = cached(chat_p, lambda p: parse_work_chat(read_text(p)))
    chat_st = stat_info(chat_p)

    # autodigest.log
    alog_p = CHAT / 'autodigest.log'
    alog = {'exists': alog_p.exists(), 'lines': 0, 'counts': {}, 'last': None, 'last_sent': None, 'last_not_sent': None,
            'recent': []}
    if alog['exists']:
        lines = [ln for ln in read_text(alog_p).split('\n') if ln.strip()]
        alog['lines'] = len(lines)
        cnt = collections.Counter()
        parsed = []
        for ln in lines:
            rec = {'raw': short(ln, 220), 'kind': 'unparsed'}
            for kind, rx in RE_ALOG:
                m = rx.match(ln)
                if m:
                    rec['kind'] = kind
                    rec['local'] = m.group(1)
                    rec['epoch'] = parse_local(m.group(1), '%Y-%m-%d %H:%M' if ' ' in m.group(1) else '%Y-%m-%d')
                    if kind == 'not_sent':
                        rec['rc'], rec['msg'] = int(m.group(2)), short(m.group(3), 200)
                    if kind == 'sent':
                        rec['verdict_line'] = short(m.group(2), 200)
                    break
            cnt[rec['kind']] += 1
            parsed.append(rec)
        alog['counts'] = dict(cnt)
        alog['last'] = parsed[-1] if parsed else None
        alog['last_sent'] = next((p for p in reversed(parsed) if p['kind'] == 'sent'), None)
        alog['last_not_sent'] = next((p for p in reversed(parsed) if p['kind'] == 'not_sent'), None)
        alog['recent'] = parsed[-10:]
        alog['stop_verdict_seen'] = any(p['kind'] == 'sent' and 'STOP' in (p.get('verdict_line') or '') for p in parsed)
    for fn in ('.last_digest_hash', '.lock'):
        si = stat_info(CHAT / fn)
        alog[fn.strip('.') + '_mtime_utc'] = utc_iso(si['mtime']) if si else None

    # loops, sends, interactive sessions (Linux /proc; WSL only)
    tab = _proc_table()
    now = time.time()
    loops, sends, interactive, advise = [], [], [], []
    seen_cmd = set()
    for pid, p in tab.items():
        a = p['args']
        joined = ' '.join(a)
        if a and os.path.basename(a[0]) == 'bash' and any(x.endswith('codex_autodigest.sh') for x in a[1:3]):
            kids = [(cp, c) for cp, c in tab.items() if c['ppid'] == pid]
            sl = next(((cp, c) for cp, c in kids if c['comm'] == 'sleep'), None)
            rec = {'pid': pid, 'started_utc': utc_iso(now - p['etimes']), 'age_s': round(p['etimes'])}
            if sl:
                try:
                    dur = float(sl[1]['args'][1])
                except (IndexError, ValueError):
                    dur = None
                rec['phase'] = 'sleeping'
                rec['interval_s'] = dur
                if dur is not None:
                    rem = dur - sl[1]['etimes']
                    rec['next_wake_utc'] = utc_iso(now + rem)
                    rec['next_wake_epoch'] = round(now + rem)
                    rec['next_wake_in_s'] = round(rem)
            else:
                rec['phase'] = 'cycle in progress'
                rec['children'] = [c['comm'] for _, c in kids][:5]
            iv = rec.get('interval_s') or 14400
            rec['cycle_estimate'] = int(p['etimes'] // iv) + 1
            rec['cycles_max'] = AUTODIGEST_CYCLES
            rec['ends_estimate_epoch'] = round(now - p['etimes'] + AUTODIGEST_CYCLES * iv)
            rec['ends_estimate_utc'] = utc_iso(rec['ends_estimate_epoch'])
            loops.append(rec)
            _LOOP_MEMO[pid] = {'ends_epoch': rec['ends_estimate_epoch'], 'last_seen': now}
        elif a and os.path.basename(a[0]) == 'bash' and any(x.endswith('codex_advise.sh') for x in a[1:3]):
            i = next(i for i, x in enumerate(a) if x.endswith('codex_advise.sh'))
            advise.append({'pid': pid, 'topic': short(a[i + 1], 160) if len(a) > i + 1 else None, 'age_s': round(p['etimes'])})
        elif any(os.path.basename(x) == 'codex' for x in a[:2]) and 'resume' in a:
            key = ' '.join(a[a.index('resume') - 1:])
            if key in seen_cmd:
                continue
            seen_cmd.add(key)
            rec = {'pid': pid, 'age_s': round(p['etimes']), 'started_utc': utc_iso(now - p['etimes'])}
            m = re.search(r'model_reasoning_effort="?(\w+)', joined)
            rec['effort'] = m.group(1) if m else None
            (sends if 'exec' in a else interactive).append(rec)
    loops.sort(key=lambda r: r['pid'])
    next_due = min((l['next_wake_epoch'] for l in loops if l.get('next_wake_epoch')), default=None)
    ad_state, ad_ended = _autodigest_state(loops, alog, now)
    writer = 'interactive' if interactive else 'send_in_flight' if sends else 'free'

    # Codex session: read the session ID from work_chat/session_id.txt, find the file whose NAME contains it under
    # ~/.codex/sessions (file names only) and stat it. The session file's contents are never read, auth.json is never
    # touched, and the ID itself is not returned (only session_id_present, mtime and size).
    sess = {'session_id_present': False}
    try:
        sid = read_text(CHAT / 'session_id.txt').strip()
        sess['session_id_present'] = bool(sid)
        if sid and os.path.isdir(os.path.expanduser('~/.codex/sessions')):
            sp = _session_file(sid)
            si = stat_info(sp) if sp else None
            if si:
                sess['last_active_utc'] = utc_iso(si['mtime'])
                sess['last_active_age_s'] = round(now - si['mtime'])
                sess['size_bytes'] = si['size']
            else:
                sess['note'] = 'session file not found under ~/.codex/sessions'
    except OSError as e:
        warnings.append('session_id.txt: %s' % e)

    milestone = [e for e in entries if e['kind'] == 'milestone']
    periodic = [e for e in entries if e['kind'] == 'periodic']
    pending = [e for e in entries if e['decision']['pending']]
    return {'entries': entries, 'n_entries': len(entries), 'n_milestone': len(milestone), 'n_periodic': len(periodic),
            'pending_decisions': len(pending), 'pending_milestone_decisions': sum(1 for e in pending if e['kind'] == 'milestone'),
            'last_entry': entries[-1] if entries else None,
            'last_verdict': next((e['verdict'] for e in reversed(entries) if e['verdict']), None),
            'verdict_counts': dict(collections.Counter(e['verdict'] for e in entries if e['verdict'])),
            'work_chat_mtime_utc': utc_iso(chat_st['mtime']) if chat_st else None,
            'work_chat_bytes': chat_st['size'] if chat_st else None,
            'autodigest': {'log': alog, 'loops': loops, 'alive': bool(loops), 'n_loops': len(loops),
                           'state': ad_state, 'ended_utc': utc_iso(ad_ended) if ad_ended else None,
                           'ends_estimate_utc': utc_iso(max(l['ends_estimate_epoch'] for l in loops)) if loops else None,
                           'cycles_max': AUTODIGEST_CYCLES,
                           'next_due_utc': utc_iso(next_due) if next_due else None,
                           'next_due_in_s': round(next_due - now) if next_due else None},
            'activity': {'writer_lock': writer, 'sends_in_flight': sends, 'interactive_sessions': interactive,
                         'advise_running': advise},
            'session': sess, 'warnings': warnings}


# =============================================================================================== register
# An amendment that waits for the user's approval (same rule as the page's codexWaitsForUser)
RE_AWAITS_USER = re.compile(r"\*\*Proposed\b|needs the user'?s go|user approval", re.I)


def _register_list_after(txt, label_rx):
    """Items of a '- **Label:** ...' line: the inline text as one item, or its indented sub-list."""
    m = re.search(r'^([ \t]*)- ' + label_rx + r'[ \t]*([^\n]*)\n((?:\1[ \t]+- [^\n]*\n?)*)', txt, re.M)
    if not m:
        return []
    items = [x.strip()[2:].rstrip(';.') for x in m.group(3).split('\n') if x.strip().startswith('- ')]
    if not items and m.group(2).strip():
        items = [m.group(2).strip().rstrip('.')]
    return [short(x, 200) for x in items]


def _register_todo(txt):
    """Open freeze steps: '- **Still to do:** ...' or '**Still to do before the freeze:**' (inline or sub-list)."""
    return _register_list_after(txt, r'\*\*Still to do(?: before the freeze)?:\*\*')


RE_HYP_OUTCOME = re.compile(r'\*\*(?:Outcome|Result)(?!\s+rule)[^*\n]{0,40}?\*\*:?\s*\**\s*'
                            r'(PARTLY SUPPORTED|SUPPORTED|FALSIFIED|UNRESOLVED|PASSED|FAILED)\b', re.I)
RE_HYP_BOLD_OUTCOME = re.compile(r'\*\*(Partly supported|Supported|SUPPORTED|Falsified|FALSIFIED|Passed|PASSED)\.?\*\*(?!:)')


def _hyp_outcome(b):
    """Scored outcome of a hypothesis section, only from an explicit declaration ('**Outcome:** SUPPORTED', or a bold
    '**Falsified.**' / '**Supported**' standing alone). Labels inside a frozen outcome RULE ('**Supported:** both
    predictions hold ...') are definitions, not results, and are ignored."""
    m = RE_HYP_OUTCOME.search(b)
    word = m.group(1) if m else None
    if not word:
        lines, skip_indent = [], None
        for ln in b.split('\n'):      # drop the '- **Outcome rule ...**' bullet and its indented children
            ind = len(ln) - len(ln.lstrip())
            if skip_indent is not None:
                if not ln.strip() or ind > skip_indent:
                    continue
                skip_indent = None
            if re.match(r'^\s*- \*\*Outcome rule', ln):
                skip_indent = ind
                continue
            lines.append(ln)
        m2 = RE_HYP_BOLD_OUTCOME.search('\n'.join(lines))
        word = m2.group(1) if m2 else None
    if not word:
        return None
    w = word.upper()
    return {'PASSED': 'SUPPORTED', 'FAILED': 'FALSIFIED'}.get(w, w)


def _count_registered(b):
    """Number of registered predictions/criteria: the bullets (or table rows) directly under the
    '**Registered prediction(s)/acceptance**' heading; 1 when the prediction is stated inline."""
    lines = b.split('\n')
    for i, ln in enumerate(lines):
        mh = re.match(r'^(\s*)- \*\*Registered (?:predictions?|acceptance)\b', ln)
        if not mh:
            continue
        ind = len(mh.group(1))
        child, n, table = None, 0, []
        for ln2 in lines[i + 1:]:
            if not ln2.strip():
                continue
            ind2 = len(ln2) - len(ln2.lstrip())
            if ind2 <= ind:
                break
            s = ln2.strip()
            if s.startswith('|'):
                table.append(s)
            elif s.startswith('- '):
                if child is None:
                    child = ind2
                if ind2 == child and not re.search(r'\bfalsif', s, re.I):
                    n += 1
        if len(table) >= 2 and re.match(r'^\|[\s:|-]+\|$', table[1]):
            n += len(table) - 2
        return n or 1
    return 0


def collect_register():
    p = CHAT / 'HYPOTHESIS_REGISTER.md'
    txt = cached(p, load_text)
    m = re.search(r'^\*\*Status: (.+?)\*\*', txt, re.M)
    status = m.group(1) if m else None
    frozen_text = bool(status and re.search(r'\bfrozen\b', status, re.I) and not re.search(r'not frozen', status, re.I))
    rc, out, err, sec = _git(PRIV, 'tag', '-l', timeout=20)
    tags = [t for t in out.split() if t] if rc == 0 else []
    freeze_tags = [t for t in tags if re.search(r'freeze|register|frozen', t, re.I)]
    rev = re.search(r'revision (\d+)', txt[:300])
    prereq = _register_todo(txt)
    done_items = _register_list_after(txt, r'\*\*Done:\*\*')
    hyps = []
    for h in re.finditer(r'^\| (H-[A-K]) \| (.+?) \| (.+?) \| (.+?) \| (\d) \|$', txt, re.M):
        hyps.append({'id': h.group(1), 'title': h.group(2), 'codex_id': h.group(3), 'claude_id': h.group(4),
                     'priority': int(h.group(5))})
    secs = {}
    sm = list(re.finditer(r'^### (H-[A-K]): (.+)$', txt, re.M))
    for i, s in enumerate(sm):
        end = sm[i + 1].start() if i + 1 < len(sm) else len(txt)
        nxt = re.search(r'^## ', txt[s.end():end], re.M)
        body = txt[s.end(): s.end() + nxt.start()] if nxt else txt[s.end():end]
        secs[s.group(1)] = body
    for h in hyps:
        b = secs.get(h['id'], '')
        pend = re.search(r'\*\*Pending \((A\d+)\)', b)
        cost = re.search(r'\*\*Cost:?\*\*:?\s*([^\n]+)', b)
        outcome = _hyp_outcome(b)
        if outcome:
            st = outcome
        elif pend:
            st = 'PENDING (%s)' % pend.group(1)
        else:
            st = 'REGISTERED, UNTESTED' + ('' if (frozen_text or freeze_tags) else ' (draft)')
        h['status'] = st
        h['pending_amendment'] = pend.group(1) if pend else None
        h['cost'] = short(cost.group(1).strip(), 80) if cost else None
        h['n_registered_predictions'] = _count_registered(b)
        h['has_falsifier'] = bool(re.search(r'\*\*Falsified if|\*\*Failed:?\*\*|\bfalsifies\b', b))
    amends = []
    am = re.search(r'^## 5\..*$', txt, re.M)
    if am:
        for a in re.finditer(r'^\| (A\d+) \| (.+?) \| (.+?) \|$', txt[am.end():], re.M):
            chg = a.group(2)
            pending = '**Pending:**' in chg
            awaiting = bool(RE_AWAITS_USER.search(chg))
            amends.append({'id': a.group(1), 'change': short(chg.replace('**Pending:**', '').strip(), 260),
                           'reason': short(a.group(3), 160), 'pending': pending or awaiting,
                           'awaiting_user': awaiting})
    diag = re.search(r'\*\*(?:That is )?(\d+) entries(?:,| and)\s*(?:(\d+) launches)?[,\s]*([^*]*)\*\*', txt)
    dls = []
    sec3 = re.search(r'^## 3\.(.*?)(?=^## 4\.)', txt, re.M | re.S)
    if sec3:
        for d in re.finditer(r'\*\*(\d{1,2}) Oct (\d\d:\d\d):\*\*\s*([^\n]+)', sec3.group(1)):
            iso = '2026-10-%02dT%s:00Z' % (int(d.group(1)), d.group(2))
            dls.append({'utc': iso, 'epoch': parse_utc(iso), 'text': short(d.group(3), 200)})
    budget = re.search(r'\*\*Budget:\*\*\s*([^\n]+)', txt)
    si = stat_info(p)
    return {'status_line': status, 'revision': int(rev.group(1)) if rev else None, 'frozen': frozen_text or bool(freeze_tags),
            'freeze_tags': freeze_tags, 'all_tags': tags[:20], 'freeze_prerequisites': prereq,
            'freeze_done': done_items,
            'hypotheses': hyps, 'priority_counts': dict(collections.Counter(h['priority'] for h in hyps)),
            'amendments': amends, 'amendments_pending': [a['id'] for a in amends if a['pending']],
            'amendments_awaiting_user': [a['id'] for a in amends if a['awaiting_user']],
            'diagnostic_set': {'n': int(diag.group(1)), 'n_entries': int(diag.group(1)),
                               'n_launches': int(diag.group(2)) if diag.group(2) else None,
                               'state': diag.group(3).strip(' .,') or None} if diag else None,
            'cern_deadlines': dls, 'budget_snapshot': short(budget.group(1), 200) if budget else None,
            'mtime_utc': utc_iso(si['mtime']) if si else None,
            'rev1_present': (CHAT / 'HYPOTHESIS_REGISTER_rev1.md').exists()}


# =============================================================================================== ledger
def _yaml_list(p):
    txt = read_text(p)
    try:
        import yaml  # PyYAML 6 is in WSL python3; optional
        d = yaml.safe_load(txt)
        if isinstance(d, list):
            return d, 'pyyaml'
    except Exception:
        pass
    # fallback: top-level "- key: value" blocks, two-space child keys
    items = []
    for blk in re.split(r'^(?=- \w+:)', txt, flags=re.M):
        if not blk.startswith('- '):
            continue
        d = {}
        for m in re.finditer(r'^(?:- |  )(\w+):\s*(.*)$', blk, re.M):
            v = m.group(2).strip().strip('"')
            d.setdefault(m.group(1), v)
        items.append(d)
    return items, 'regex-fallback'


def collect_ledger():
    warnings = []
    # decisions
    dp = PRIV / '05_DECISION_LOG.md'
    dtxt = cached(dp, load_text)
    decisions = []
    for ln in dtxt.split('\n'):
        if not re.match(r'^\| D-\d+', ln):
            continue
        f = ln.split('|')
        if len(f) < 8:
            warnings.append('decision row with %d fields' % len(f))
            continue
        stc = f[6].strip()
        m = re.match(r'^(IN FORCE|SUPERSEDED|PENDING)', stc)
        decisions.append({'id': f[1].strip(), 'num': int(re.search(r'\d+', f[1]).group(0)), 'date': f[2].strip(),
                          'decision': short(f[3].strip(), 300), 'by': f[4].strip(), 'basis': short(f[5].strip(), 160),
                          'status': m.group(1) if m else 'OTHER', 'status_text': short(stc, 120)})
    decisions.sort(key=lambda d: d['num'])
    dcounts = dict(collections.Counter(d['status'] for d in decisions))
    newest_dec_date = max((d['date'][:10] for d in decisions), default=None)

    # tasks
    tasks_raw, how_t = cached(PRIV / '04_TASK_QUEUE.yaml', _yaml_list)
    tasks = []
    for t in tasks_raw:
        if not isinstance(t, dict):
            continue
        st = str(t.get('status', ''))
        m = re.match(r'[A-Z_]+', st)
        owner = t.get('owner')
        tasks.append({'id': t.get('task_id'), 'title': short(t.get('title'), 160),
                      'owner': short(owner if isinstance(owner, str) else json.dumps(owner, default=str), 80),
                      'reviewer': short(t.get('reviewer'), 60) if isinstance(t.get('reviewer'), str) else t.get('reviewer'),
                      'status': m.group(0) if m else (st or 'UNKNOWN'), 'status_text': short(st, 160),
                      'priority': t.get('priority'), 'depends_on': t.get('depends_on'), 'blocks': t.get('blocks')})
    tcounts = dict(collections.Counter(t['status'] for t in tasks))
    open_tasks = [t for t in tasks if t['status'] != 'DONE']
    tq_si = stat_info(PRIV / '04_TASK_QUEUE.yaml')

    # claims
    claims_raw, how_c = cached(PRIV / '03_CLAIMS_LEDGER.yaml', _yaml_list)
    ccounts = dict(collections.Counter(str(c.get('status')) for c in claims_raw if isinstance(c, dict)))
    claims_flagged = [{'id': c.get('id'), 'status': c.get('status'), 'claim': short(c.get('claim'), 200)}
                      for c in claims_raw if isinstance(c, dict) and str(c.get('status')) in ('UNRESOLVED', 'FALSIFIED', 'HYPOTHESIS')]

    # current state
    cp = PRIV / '01_CURRENT_STATE.md'
    ctxt = cached(cp, load_text)
    m = re.search(r'^# Current state of the IWO project \((\d{4}-\d\d-\d\d)\)', ctxt, re.M)
    sections = [{'id': s.group(1), 'title': s.group(2)} for s in re.finditer(r'^## ([A-K])\. (.+)$', ctxt, re.M)]
    changes = [{'date': c.group(1), 'what': c.group(2).strip()} for c in re.finditer(r'^- \*\*(\d{4}-\d\d-\d\d), ([^*]+)\*\*', ctxt, re.M)]
    jm = re.search(r'^## J\..*?$(.*?)(?=^## )', ctxt, re.M | re.S)
    pending_human = [short(x.strip()[2:], 200) for x in (jm.group(1).split('\n') if jm else []) if x.strip().startswith('- ')]
    csi = stat_info(cp)
    latest_change = max((c['date'] for c in changes), default=None)
    stale = bool(newest_dec_date and ((latest_change or m.group(1) if m else '') < newest_dec_date))
    return {'decisions': decisions, 'decision_counts': dcounts, 'newest_decision_date': newest_dec_date,
            'pending_decisions': [d for d in decisions if d['status'] == 'PENDING'],
            'tasks': tasks, 'task_counts': tcounts, 'open_tasks': len(open_tasks), 'tasks_parser': how_t,
            'task_queue_mtime_utc': utc_iso(tq_si['mtime']) if tq_si else None,
            'claims_counts': ccounts, 'claims_total': sum(ccounts.values()), 'claims_parser': how_c,
            'claims_flagged': claims_flagged,
            'current_state': {'title_date': m.group(1) if m else None, 'mtime_utc': utc_iso(csi['mtime']) if csi else None,
                              'sections': sections, 'latest_change': changes[-1] if changes else None,
                              'n_changes': len(changes), 'pending_human_decisions': pending_human,
                              'stale': stale, 'stale_reason': ('change log ends %s, newest decision %s' % (latest_change, newest_dec_date)) if stale else None},
            'warnings': warnings}


# =============================================================================================== git
WIN_GIT = '/mnt/c/Program Files/Git/cmd/git.exe'


def win_path(p):
    """/mnt/c/x/y -> C:\\x\\y (None if not a /mnt/<drive> path)."""
    m = re.match(r'^/mnt/([a-zA-Z])(/.*)?$', str(p))
    if not m:
        return None
    return m.group(1).upper() + ':' + (m.group(2) or '/').replace('/', '\\')


def _git(repo, *args, timeout=60):
    """Read-only git. On /mnt/c, WSL git re-hashes every tracked file on each status (stat data written by Windows
    git never match and --no-optional-locks forbids refreshing the index: ~55 s for the public repo), so the
    Windows git.exe is used through /init when available (0.2 s, same answer with core.longpaths=true for this
    call only). Nothing is written: --no-optional-locks, no fetch, no config change."""
    env = {**os.environ, 'GIT_OPTIONAL_LOCKS': '0', 'GIT_TERMINAL_PROMPT': '0'}
    wp = win_path(repo)
    if wp and os.path.exists('/init') and os.path.exists(WIN_GIT):
        argv = ['/init', WIN_GIT, 'git.exe', '-c', 'core.longpaths=true', '--no-optional-locks', '-C', wp] + list(args)
        rc, out, err, sec = run_cmd(argv, timeout=timeout, env=env)
        if rc == 0:
            return rc, out.replace('\r\n', '\n'), err, sec
    return run_cmd(['git', '--no-optional-locks', '-C', str(repo)] + list(args), timeout=timeout, env=env)


def git_repo_state(repo):
    t0 = time.time()
    r = {'path': str(repo), 'name': repo.name}
    rc, out, err, _ = _git(repo, 'log', '-1', '--format=%h|%cI|%s')
    if rc != 0:
        r['error'] = short(err.strip(), 200)
        return r
    h, ci, subj = (out.strip().split('|', 2) + ['', ''])[:3]
    r.update(head=h, commit_time=ci, subject=short(subj, 160))
    rc, out, err, _ = _git(repo, 'rev-parse', '--abbrev-ref', 'HEAD')
    r['branch'] = out.strip() if rc == 0 else None
    rc, out, err, sec = _git(repo, 'status', '--porcelain', timeout=90)
    if rc == 0:
        lines = [ln for ln in out.split('\n') if ln.strip()]
        r['dirty'] = len(lines)
        r['untracked'] = sum(1 for ln in lines if ln.startswith('??'))
        r['modified'] = r['dirty'] - r['untracked']
        r['dirty_sample'] = [ln[3:] for ln in lines[:12]]
    else:
        r['dirty'] = None
        r['status_error'] = short(err.strip(), 160)
    r['status_s'] = sec
    rc, out, err, _ = _git(repo, 'rev-list', '--count', 'origin/main..HEAD')
    r['unpushed'] = int(out.strip()) if rc == 0 and out.strip().isdigit() else None
    rc, out, err, _ = _git(repo, 'rev-list', '--count', 'HEAD..origin/main')
    r['behind_cached'] = int(out.strip()) if rc == 0 and out.strip().isdigit() else None
    fh = stat_info(repo / '.git' / 'FETCH_HEAD')
    r['last_fetch_utc'] = utc_iso(fh['mtime']) if fh else None
    rc, out, err, _ = _git(repo, 'tag', '--sort=-creatordate')
    r['tags'] = [t for t in out.split('\n') if t.strip()][:5] if rc == 0 else []
    r['seconds'] = round(time.time() - t0, 2)
    return r


def collect_git():
    repos = {'priv': git_repo_state(PRIV), 'pub': git_repo_state(PUB)}
    errs = ['%s: %s' % (k, v['error']) for k, v in repos.items() if v.get('error')]
    if errs:
        repos['__ok__'] = False
        repos['__error__'] = '; '.join(errs)
    repos['note'] = 'unpushed/behind use the cached origin/main (no fetch); see last_fetch_utc'
    return repos


# =============================================================================================== meta
def collect_meta(register_data=None):
    now = time.time()
    dls = []
    seen = set()
    for key, label, iso in STATIC_DEADLINES:
        ep = parse_utc(iso)
        dls.append({'key': key, 'label': label, 'utc': iso, 'epoch': ep, 'remaining_s': round(ep - now),
                    'source': 'dashboard config'})
        seen.add(iso)
    for d in (register_data or {}).get('cern_deadlines') or []:
        if d['utc'] in seen:
            continue
        dls.append({'key': 'register_' + d['utc'][5:16].replace(':', '').replace('-', ''), 'label': 'CERN (register): ' + d['text'],
                    'utc': d['utc'], 'epoch': d['epoch'], 'remaining_s': round(d['epoch'] - now), 'source': 'HYPOTHESIS_REGISTER.md'})
    dls.sort(key=lambda d: d['epoch'])
    nxt = next((d for d in dls if d['remaining_s'] > 0), None)
    lt = time.localtime(now)
    return {'server_time_utc': utc_iso(now), 'server_epoch': round(now, 1),
            'server_time_local': time.strftime('%Y-%m-%d %H:%M:%S', lt), 'local_tz': time.strftime('%Z %z', lt),
            'deadlines': dls, 'next_deadline': nxt,
            'cern_target_utc': '2026-10-15T00:00:00Z', 'cern_end_utc': '2026-10-21T23:59:59Z',
            'paths': {'root': str(ROOT), 'pub': str(PUB), 'priv': str(PRIV), 'dashboard': str(DASH)}}


# =============================================================================================== alerts
SEV_ORDER = {'crit': 0, 'warn': 1, 'info': 2}


def derive_alerts(st):
    """st = {name: envelope}. Returns [{severity, text, source, key}] sorted crit -> info."""
    A = []

    def add(sev, text, source, key):
        A.append({'severity': sev, 'text': text, 'source': source, 'key': key})

    def D(name):
        e = st.get(name) or {}
        return e.get('data') or {}

    now = time.time()
    for name, e in st.items():
        if isinstance(e, dict) and e.get('ok') is False and name != 'cern':
            add('warn', 'Collector %s failed: %s' % (name, e.get('error')), name, 'collector_%s' % name)

    # ---- CERN
    ce = st.get('cern') or {}
    c = ce.get('data') or {}
    if ce and ce.get('updated_utc') is None:
        add('info', 'CERN not queried yet (first snapshot runs shortly after start)', 'cern', 'cern_pending')
    elif ce:
        if c.get('master') is False:
            age = c.get('snapshot_age_s')
            add('crit', 'SSH master to lxplus is gone: log in again. %s' %
                (('CERN data shown are %d min old.' % (age // 60)) if age is not None else 'No earlier CERN snapshot to show.'),
                'cern', 'cern_master_down')
        elif ce.get('ok') is False:
            add('warn', 'CERN refresh failed: %s' % ce.get('error'), 'cern', 'cern_refresh_failed')
        if c.get('snapshot_age_s') and c['snapshot_age_s'] > 1200:
            add('warn', 'CERN snapshot is %d min old.' % (c['snapshot_age_s'] // 60), 'cern', 'cern_stale')
        for j in c.get('jobs') or []:
            if j.get('status') == 'held':
                add('crit', 'HELD job %s (%s): %s' % (j.get('iwojob') or j.get('batch'), j.get('cluster'), j.get('hold_reason') or ''),
                    'cern', 'held_%s' % j.get('cluster'))
        for r in c.get('pipeline') or []:
            if r['stage'].startswith('FAILED'):
                # RELAX_STATUS / last segment FAILED: crit (the row's level), also while DAGMan retries it
                add('crit' if r['level'] == 'crit' else 'warn', '%s: RELAX %s%s; last segment ended %s' % (r['name'], r['stage'],
                    ' + no progress' if any('no progress' in f for f in r['flags']) else '', r.get('relax_status_utc') or '?'),
                    'cern', 'relax_failed_%s' % r['name'])
            elif r['level'] == 'crit':
                add('crit', '%s: %s%s' % (r['name'], r['stage'], (' (' + '; '.join(r['flags']) + ')') if r['flags'] else ''),
                    'cern', 'dag_failed_%s' % r['name'])
            elif r['stage'] == 'COLLECTED, DFT not started':
                add('warn', '%s collected but DFT not started (pseudopotential or collect problem?)' % r['name'],
                    'cern', 'collect_%s' % r['name'])
            if r.get('ml_exit') not in (None, 0, 2):
                add('crit', '%s: ML driver exit %s (error)' % (r['name'], r['ml_exit']), 'cern', 'mlexit_%s' % r['name'])
            if r.get('ml_done') and not r.get('collected'):
                add('warn', '%s: ML output present but not collected' % r['name'], 'cern', 'notcollected_%s' % r['name'])
            if r.get('segment_used_frac') and r['segment_used_frac'] > 0.9 and r.get('condor_status') == 'running':
                add('info', '%s: %s at %.0f%% of its %.0f h wall limit' % (
                    r['name'], 'final SCF' if r.get('node_kind') == 'final' else 'relax segment s%s' % r.get('node_seg'),
                    100 * r['segment_used_frac'], (r.get('segment_limit_s') or SEGMENT_LIMIT_S) / 3600.0),
                    'cern', 'seglimit_%s' % r['name'])
        v = c.get('validation') or {}
        idle_v = [j for j in v.get('jobs') or [] if j.get('status') == 'idle']
        if idle_v:
            h = max((j.get('in_status_h') or 0) for j in idle_v)
            add('warn' if h > 12 else 'info', '%d force-check (val) jobs idle, longest %.1f h (48 CPU / 102 GB each)' % (len(idle_v), h),
                'cern', 'val_idle')
        q = c.get('quota') or {}
        if q.get('pct') is not None and q['pct'] >= 80:
            add('warn' if q['pct'] < 95 else 'crit', 'AFS quota %s%% used' % q['pct'], 'cern', 'quota')
    # ---- deadlines
    for d in (D('meta').get('deadlines') or []):
        rem = d['remaining_s']
        if 0 < rem <= 12 * 3600:
            add('crit', '%s in %.1f h (%s)' % (d['label'], rem / 3600, d['utc']), 'meta', 'deadline_%s' % d['key'])
        elif 0 < rem <= 48 * 3600:
            add('warn', '%s in %.1f h (%s)' % (d['label'], rem / 3600, d['utc']), 'meta', 'deadline_%s' % d['key'])
        elif 0 < rem <= 96 * 3600:
            add('info', '%s in %.1f d (%s)' % (d['label'], rem / 86400, d['utc']), 'meta', 'deadline_%s' % d['key'])

    # ---- ATLAS
    a = D('atlas')
    if a:
        stt = a.get('state')
        ar = a.get('active_run') or {}
        if stt == 'RUNNING':
            add('info', 'ATLAS %s (%s) running: %s/%s points, %s s left before timeout' % (
                ar.get('run_id'), ar.get('entry_id') or ar.get('label'), ar.get('points'), ar.get('points_requested'),
                ar.get('timeout_remaining_s')), 'atlas', 'atlas_running')
            if ar.get('timeout_remaining_s') is not None and ar['timeout_remaining_s'] < 0:
                add('warn', 'ATLAS %s is past its timeout' % ar.get('run_id'), 'atlas', 'atlas_overdue')
        elif stt == 'STALE':
            add('crit', 'ATLAS %s has a STARTED row but no solver process and no execution.json (crashed?)' % ar.get('run_id'),
                'atlas', 'atlas_stale')
        elif stt == 'SOLVER_UNTRACKED':
            add('warn', 'An ATLAS/DeckBuild process is alive but no run is open in RUN_INDEX', 'atlas', 'atlas_untracked')
        elif stt == 'BETWEEN_LAUNCHES':
            add('info', 'Campaign runner alive, between launches', 'atlas', 'atlas_between')
        lr = a.get('last_run') or {}
        if lr.get('exit_code') == 'timeout':
            add('warn', 'Last ATLAS run %s (%s) timed out' % (lr.get('run_id'), lr.get('entry_id')), 'atlas', 'atlas_last_timeout')
        for v in a.get('verdicts') or []:
            if v['class'] == 'FAIL':
                add('warn', '%s (%s vs %s): %s' % (v.get('entry_id') or v['run'], v['run'], v.get('ref'), v['verdict']),
                    'atlas', 'verdict_%s' % v['run'])
            elif v['class'] in ('UNRESOLVED', 'UNVERIFIED', 'TIMEOUT'):
                add('warn', '%s (%s): %s' % (v.get('entry_id') or v['run'], v['run'], v['verdict']), 'atlas', 'verdict_%s' % v['run'])
        b = a.get('budget') or {}
        left = b.get('c10_left')
        if left is not None:
            if left <= 5:
                add('crit', 'C10 launch budget nearly exhausted: %d of %d left' % (left, b.get('c10_cap')), 'atlas', 'budget_c10')
            elif left <= 20:
                add('warn', 'C10 launch budget low: %d of %d left' % (left, b.get('c10_cap')), 'atlas', 'budget_c10')
        if b.get('reserve_left') is not None:
            if b['reserve_left'] < 0:
                add('crit', 'C10 reserve overspent by %d launches' % -b['reserve_left'], 'atlas', 'budget_reserve')
            elif b['reserve_left'] <= 5:
                add('warn', 'C10 reserve low: %d of %d left' % (b['reserve_left'], b.get('reserve_launches')), 'atlas', 'budget_reserve')
            else:
                add('info', 'C10 reserve: %d of %d left (%d used: %d retries, %d unplanned launches)' % (
                    b['reserve_left'], b.get('reserve_launches'), b.get('reserve_used'), b.get('retries') or 0,
                    b.get('unplanned_launches') or 0), 'atlas', 'budget_reserve')
        if b.get('s0_reserve_used') and b['s0_reserve_used'] > b.get('s0_reserve_max', 3):
            add('info', 'S0 used %d reserve launches (design limit %d), disclosed as a protocol deviation' % (
                b['s0_reserve_used'], b.get('s0_reserve_max', 3)), 'atlas', 'budget_s0')
        if b.get('total_left') is not None and b['total_left'] <= 10:
            add('warn', 'solver.yaml max_launches: %d of %d left' % (b['total_left'], b.get('total_cap')), 'atlas', 'budget_total')
        nc = a.get('nc_audit') or {}
        if nc.get('state') == 'RUNNING':
            add('info', 'NC audit running (gates H-E/N1 amendment A13 and S3)', 'atlas', 'nc_audit')
        elif nc.get('state') == 'RESULTS':
            add('info', 'NC audit results written; NC_AUDIT.md report not yet written', 'atlas', 'nc_audit')
        if a.get('post_run_missing'):
            add('info', 'post_run checks missing for %s' % ', '.join(a['post_run_missing']), 'atlas', 'post_run_missing')
        pr = a.get('processes') or {}
        if pr.get('ok') is False:
            add('warn', 'Windows process query failed: %s' % pr.get('error'), 'atlas', 'proc_query')

    # ---- Codex
    cx = D('codex')
    if cx:
        pd = [e for e in cx.get('entries') or [] if e['decision']['pending']]
        if pd:
            add('warn', '%d Codex reply(ies) await a Claude decision: %s' % (len(pd), '; '.join(
                '%s %s [%s]' % (e['ts_utc'], short(e['topic'], 60), e.get('verdict')) for e in pd[:3])), 'codex', 'codex_pending')
        ad = cx.get('autodigest') or {}
        cern_end = parse_utc(next(x[2] for x in STATIC_DEADLINES if x[0] == 'cern_end'))
        ads = ad.get('state')
        if not ad.get('alive'):
            if ads == 'finished':
                ended = parse_utc(ad.get('ended_utc')) if ad.get('ended_utc') else None
                add('warn' if (cern_end and now < cern_end) else 'info',
                    'Codex autodigest finished its %d cycles%s; periodic Codex monitoring has stopped%s' % (
                        ad.get('cycles_max') or AUTODIGEST_CYCLES, (' on %s' % ad['ended_utc'][:10]) if ended else '',
                        ' before CERN access ends (21 Oct). Restart it if monitoring should continue' if (cern_end and now < cern_end) else ''),
                    'codex', 'autodigest_finished')
            elif ads == 'stopped_after_end_date':
                add('info', 'Codex autodigest stopped after 21 Oct, as designed', 'codex', 'autodigest_finished')
            elif ads == 'stopped_by_codex':
                pass   # reported below as codex_stop (crit)
            else:
                add('crit', 'Codex autodigest loop is not running and had not finished its cycles (no codex_autodigest.sh '
                    'process: crashed or killed?)', 'codex', 'autodigest_dead')
        else:
            if ad.get('n_loops', 0) > 1:
                add('info', '%d autodigest loops are running (they share .last_digest_hash/.lock; a 4 h window can send twice)' % ad['n_loops'],
                    'codex', 'autodigest_multi')
            ends = parse_utc(ad.get('ends_estimate_utc')) if ad.get('ends_estimate_utc') else None
            if ends and cern_end and ends < cern_end:
                add('info', 'Codex autodigest loops end about %s (%d cycles of 4 h), before CERN access ends on 21 Oct; '
                    'periodic monitoring stops then' % (ad['ends_estimate_utc'][:16].replace('T', ' ') + 'Z',
                                                         ad.get('cycles_max') or AUTODIGEST_CYCLES),
                    'codex', 'autodigest_ends_early')
        lg = (ad.get('log') or {})
        if lg.get('last') and lg['last'].get('kind') == 'not_sent':
            add('warn', 'Last autodigest cycle NOT sent (rc %s): %s' % (lg['last'].get('rc'), lg['last'].get('msg')), 'codex', 'autodigest_notsent')
        if lg.get('stop_verdict_seen'):
            add('crit', 'Codex returned a STOP verdict in a periodic digest', 'codex', 'codex_stop')
        if cx.get('last_verdict') in ('STOP',):
            add('crit', 'Latest Codex verdict: STOP', 'codex', 'codex_last_stop')
        act = cx.get('activity') or {}
        if act.get('writer_lock') == 'interactive':
            add('info', 'Codex session is open interactively (holds the writer lock; periodic sends will be blocked)', 'codex', 'codex_interactive')
        elif act.get('writer_lock') == 'send_in_flight':
            topic = (act.get('advise_running') or [{}])[0].get('topic')
            add('info', 'Codex send in flight%s' % (': ' + topic if topic else ''), 'codex', 'codex_sending')

    # ---- register
    rg = D('register')
    if rg and not rg.get('frozen'):
        todo = rg.get('freeze_prerequisites') or []
        add('warn', 'Hypothesis register not frozen (%s). %s' % (rg.get('status_line'),
            ('Still to do: ' + '; '.join(todo)) if todo else 'No open freeze step is listed in the register.'),
            'register', 'register_not_frozen')
    if rg and rg.get('amendments_pending'):
        aw = set(rg.get('amendments_awaiting_user') or [])
        add('info', 'Register amendments pending: %s' % ', '.join(
            '%s%s' % (x, ' (needs your go)' if x in aw else '') for x in rg['amendments_pending']), 'register', 'register_amend')
    # ---- ledger
    lg_ = D('ledger')
    if lg_:
        if lg_.get('pending_decisions'):
            add('info', 'Human decisions PENDING: %s' % ', '.join('%s (%s)' % (d['id'], d['status_text']) for d in lg_['pending_decisions']),
                'ledger', 'ledger_pending')
        cs = lg_.get('current_state') or {}
        if cs.get('stale'):
            add('info', '01_CURRENT_STATE.md is stale: %s' % cs.get('stale_reason'), 'ledger', 'current_state_stale')
    # ---- git
    g = D('git')
    for k in ('priv', 'pub'):
        r = g.get(k) or {}
        if r.get('unpushed'):
            add('info', '%s: %d unpushed commit(s) (vs cached origin/main, fetched %s)' % (r.get('name'), r['unpushed'], r.get('last_fetch_utc')),
                'git', 'unpushed_%s' % k)
        if r.get('dirty'):
            add('info', '%s: %d uncommitted entries in git status (%d untracked; an untracked directory counts once)' % (
                r.get('name'), r['dirty'], r.get('untracked') or 0), 'git', 'dirty_%s' % k)
    A.sort(key=lambda x: (SEV_ORDER.get(x['severity'], 9), x['source']))
    return A
