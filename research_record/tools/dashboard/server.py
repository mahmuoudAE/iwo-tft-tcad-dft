#!/usr/bin/env python3
"""IWO Mission Control: local, read-only dashboard server (Python 3.12 stdlib only; run inside WSL Ubuntu).

    python3 server.py                 # serve http://127.0.0.1:8765 (port: --port or env IWO_DASH_PORT)
    python3 server.py --once [--out F] [--no-cern]   # run every collector once, print/save the JSON, exit

Routes (GET only): /  /index.html (+ whitelisted static files)  /api/status  /api/refresh[?cern=1]
                   /api/history[?hours=H&max=N]  (read-only, capped CERN history for the sparklines)
Everything else is 404. There are no write endpoints and no actions: the server only reads project files,
local process tables and (through the EXISTING SSH ControlMaster) CERN queue/status files.
/api/refresh needs the header `X-IWO-Refresh: 1` and is refused (403) for cross-site requests (Origin /
Sec-Fetch-Site), so another web page open in the browser cannot make the server query CERN.
"""
import argparse
import collections
import errno
import json
import os
import re
import signal
import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import collectors as C  # noqa: E402

VERSION = '1.0'
SCHEMA = 'iwo-mission-control/1'
HISTORY = HERE / 'history.jsonl'
HISTORY_CAP = 5000
HISTORY_IN_STATUS_HOURS = 24.0   # /api/status carries the history of the last 24 h (time window, not a count) ...
HISTORY_IN_STATUS_MAX = 600      # ... at most this many points (the newest)
LOCAL_INTERVAL = 30
GIT_INTERVAL = 300
CERN_INTERVAL = 300              # scheduled CERN snapshot every 300 s after the LAST attempt (manual ones included)
CERN_MIN_GAP = C.CERN_MIN_GAP_S  # >= 120 s between any two CERN queries, enforced under the CERN lock for every caller
CERN_FORCE_MIN_GAP = CERN_MIN_GAP
LOCAL_FORCE_MIN_GAP = 5
HISTORY_API_MAX_HOURS = 24.0 * 31   # /api/history: at most 31 days back ...
HISTORY_API_MAX_POINTS = 1000       # ... and at most 1000 points per response (evenly thinned)

# Static files: exact names in this directory, plus flat files under ./static/ with a safe name and extension.
STATIC_EXACT = {'/': 'index.html', '/index.html': 'index.html', '/app.js': 'app.js', '/app.css': 'app.css',
                '/style.css': 'style.css', '/favicon.svg': 'favicon.svg', '/favicon.ico': 'favicon.ico'}
STATIC_DIR = HERE / 'static'
STATIC_EXT = {'.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
              '.css': 'text/css; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png', '.ico': 'image/x-icon',
              '.woff2': 'font/woff2', '.json': 'application/json'}
RE_STATIC = re.compile(r'^/static/([A-Za-z0-9][A-Za-z0-9_.-]{0,80})$')

LOCAL_COLLECTORS = ('atlas', 'ml', 'codex', 'register', 'ledger', 'meta')


class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.env = {}                      # name -> envelope
        self.history = collections.deque(maxlen=HISTORY_CAP)
        self.started = time.time()
        self.last_local = 0.0
        self.local_lock = threading.Lock()
        self.git_lock = threading.Lock()
        self.stop = threading.Event()
        self.port = None
        self.hist_file_lines = 0

    def put(self, name, env):
        with self.lock:
            self.env[name] = env

    def get(self, name):
        with self.lock:
            return self.env.get(name)


S = State()


# ----------------------------------------------------------------------------------------- refreshers
def run_local(min_gap=None):
    """Run the local collectors. min_gap=None (scheduled loop): wait for the lock. With min_gap (manual refresh): skip
    when another local collection is running ('busy') or the last one finished less than min_gap s ago ('too_soon').
    The gap is checked while holding the lock, so N concurrent refreshes give one collection. Returns the outcome."""
    if min_gap is None:
        S.local_lock.acquire()
    elif not S.local_lock.acquire(blocking=False):
        return 'busy'
    try:
        if min_gap is not None and time.time() - S.last_local < min_gap:
            return 'too_soon'
        S.put('atlas', C.envelope(C.collect_atlas))
        S.put('codex', C.envelope(C.collect_codex))
        S.put('register', C.envelope(C.collect_register))
        S.put('ledger', C.envelope(C.collect_ledger))
        S.put('ml', C.envelope(C.collect_ml))
        reg = (S.get('register') or {}).get('data')
        S.put('meta', C.envelope(C.collect_meta, reg))
        S.last_local = time.time()
        return 'ran'
    finally:
        S.local_lock.release()


def run_git():
    with S.git_lock:
        S.put('git', C.envelope(C.collect_git))


def run_cern(min_gap=CERN_MIN_GAP, persist=True):
    """One CERN snapshot through C.cern_refresh (busy / minimum-gap check and query under one lock).
    persist=False (--once): the history point is kept in memory only, history.jsonl is not touched.
    Returns (outcome, envelope or None, retry_after_s)."""
    outcome, env, retry = C.cern_refresh(min_gap)
    if outcome != 'ran':
        return outcome, None, retry
    S.put('cern', env)
    d = env.get('data') or {}
    if d.get('master') and not d.get('stale') and d.get('summary'):
        pt = C.cern_history_point(d)
        S.history.append(pt)
        if persist:
            append_history(pt)
    # ML rows join the CERN QC data: refresh them right away
    S.put('ml', C.envelope(C.collect_ml))
    return outcome, env, None


def cern_loop(first_delay=1.0):
    """Scheduled CERN snapshots, CERN_INTERVAL s after the last attempt (a manual refresh restarts the clock, so the
    loop never queries right after one). cern_refresh also enforces CERN_MIN_GAP under its lock."""
    if S.stop.wait(first_delay):
        return
    while not S.stop.is_set():
        last = C.CERN_STATE['last_attempt_epoch']
        now = time.time()
        wait = (last + CERN_INTERVAL - now) if (last and last <= now) else 0.0
        if wait > 0:
            S.stop.wait(min(wait, CERN_INTERVAL))
            continue
        try:
            run_cern(CERN_MIN_GAP)
        except Exception as e:  # never let the thread die
            print('run_cern failed: %r' % (e,), file=sys.stderr)
        S.stop.wait(1.0)


def append_history(pt):
    """Append one compact point; keep the file at <= HISTORY_CAP lines (rewritten from the in-memory deque)."""
    try:
        if S.hist_file_lines + 1 > HISTORY_CAP:
            tmp = HISTORY.with_suffix('.jsonl.tmp')
            pts = list(S.history)[-HISTORY_CAP:]
            tmp.write_text(''.join(json.dumps(x, separators=(',', ':')) + '\n' for x in pts), encoding='utf-8')
            os.replace(tmp, HISTORY)
            S.hist_file_lines = len(pts)
        else:
            with open(HISTORY, 'a', encoding='utf-8') as f:
                f.write(json.dumps(pt, separators=(',', ':')) + '\n')
            S.hist_file_lines += 1
    except OSError as e:
        print('history write failed: %s' % e, file=sys.stderr)


def load_history():
    try:
        lines = HISTORY.read_text(encoding='utf-8').splitlines()
    except OSError:
        return
    S.hist_file_lines = len(lines)
    for ln in lines[-HISTORY_CAP:]:
        try:
            S.history.append(json.loads(ln))
        except ValueError:
            pass


def loop(fn, interval, first_delay=0.0):
    if S.stop.wait(first_delay):
        return
    while not S.stop.is_set():
        t0 = time.time()
        try:
            fn()
        except Exception as e:  # collectors never raise, but never let a thread die
            print('%s failed: %r' % (fn.__name__, e), file=sys.stderr)
        S.stop.wait(max(1.0, interval - (time.time() - t0)))


# ----------------------------------------------------------------------------------------- status
def history_copy():
    """Snapshot of the in-memory history (the CERN thread appends without the lock; retry if it mutates mid-copy)."""
    for _ in range(5):
        try:
            return list(S.history)
        except RuntimeError:  # deque mutated during iteration
            time.sleep(0.01)
    return []


def history_window(hours, max_points):
    """Points from the last `hours`, evenly thinned to at most `max_points` (the newest point is always kept)."""
    since = time.time() - hours * 3600.0
    pts = [p for p in history_copy() if (p.get('t') or 0) >= since]
    n = len(pts)
    if n > max_points:
        idx = sorted({int(round(i * (n - 1) / float(max_points - 1))) for i in range(max_points)})
        pts = [pts[i] for i in idx]
    return n, pts


def build_status():
    now = time.time()
    with S.lock:
        env = dict(S.env)
    since = now - HISTORY_IN_STATUS_HOURS * 3600.0
    hist = [p for p in history_copy() if (p.get('t') or 0) >= since][-HISTORY_IN_STATUS_MAX:]
    out ={'schema': SCHEMA, 'version': VERSION, 'generated_utc': C.utc_iso(now), 'generated_epoch': round(now, 1),
           'server': {'pid': os.getpid(), 'host': '127.0.0.1', 'port': S.port, 'started_utc': C.utc_iso(S.started),
                      'uptime_s': round(now - S.started), 'read_only': True,
                      'intervals_s': {'local': LOCAL_INTERVAL, 'git': GIT_INTERVAL, 'cern': CERN_INTERVAL,
                                      'cern_force_min_gap': CERN_FORCE_MIN_GAP, 'cern_min_gap': CERN_MIN_GAP},
                      'cern_last_attempt_utc': C.utc_iso(C.CERN_STATE['last_attempt_epoch']) if C.CERN_STATE['last_attempt_epoch'] else None,
                      'cern_next_auto_in_s': None}}
    if C.CERN_STATE['last_attempt_epoch']:
        out['server']['cern_next_auto_in_s'] = max(0, round(C.CERN_STATE['last_attempt_epoch'] + CERN_INTERVAL - now))
    for name in ('atlas', 'cern', 'ml', 'codex', 'register', 'ledger', 'git', 'meta'):
        e = env.get(name)
        if e is None:
            out[name] = {'ok': False, 'updated_utc': None, 'error': 'not collected yet', 'data': None}
        else:
            e = dict(e)
            e['age_s'] = round(now - e['updated_epoch'], 1) if e.get('updated_epoch') else None
            d = e.get('data')
            if name == 'cern' and isinstance(d, dict) and d.get('snapshot_utc'):
                # age of the shown CERN data NOW (not when the collector last ran), so a stalled CERN thread is visible
                ep = C.parse_utc(d['snapshot_utc'])
                if ep:
                    e['data'] = dict(d, snapshot_age_s=round(now - ep))
            out[name] = e
    try:
        out['alerts'] = C.derive_alerts({k: out[k] for k in ('atlas', 'cern', 'ml', 'codex', 'register', 'ledger', 'git', 'meta')})
    except Exception as e:
        out['alerts'] = [{'severity': 'warn', 'text': 'alert derivation failed: %r' % e, 'source': 'server', 'key': 'alerts_error'}]
    out['alert_counts'] = dict(collections.Counter(a['severity'] for a in out['alerts']))
    out['history'] = hist
    return out


# ----------------------------------------------------------------------------------------- HTTP
ALLOWED_HOSTS = ('localhost', '127.0.0.1', '[::1]')


class Handler(BaseHTTPRequestHandler):
    server_version = 'IWO-MissionControl/' + VERSION
    sys_version = ''

    def log_message(self, fmt, *args):  # quiet; errors only
        pass

    def _host_ok(self):
        h = (self.headers.get('Host') or '').strip().lower()
        host = h.rsplit(':', 1)[0] if not h.startswith('[') else h.split(']')[0] + ']'
        return host in ALLOWED_HOSTS

    def _send(self, code, body, ctype='application/json; charset=utf-8', extra=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, separators=(',', ':'), default=str, allow_nan=False).encode('utf-8')
        elif isinstance(body, str):
            body = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('X-Frame-Options', 'DENY')
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)

    def _404(self):
        self._send(404, {'error': 'not found'})

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        if not self._host_ok():
            return self._send(403, {'error': 'host not allowed'})
        u = urlsplit(self.path)
        path = u.path
        if path == '/api/status':
            return self._send(200, _safe_json(build_status()))
        if path == '/api/refresh':
            return self._refresh(parse_qs(u.query))
        if path == '/api/history':
            return self._history(parse_qs(u.query))
        fname = STATIC_EXACT.get(path)
        if fname:
            return self._file(HERE / fname)
        m = RE_STATIC.match(path)
        if m and '..' not in m.group(1):
            return self._file(STATIC_DIR / m.group(1), base=STATIC_DIR)
        return self._404()

    def _file(self, p, base=HERE):
        try:
            rp = p.resolve()
            if rp.parent != base.resolve() or not rp.is_file():
                return self._404()
            ctype = STATIC_EXT.get(rp.suffix.lower())
            if not ctype:
                return self._404()
            return self._send(200, rp.read_bytes(), ctype)
        except OSError:
            return self._404()

    def _history(self, q):
        """GET /api/history?hours=H&max=N: read-only window of the in-memory CERN history (no file access)."""
        def arg(name, default, lo, hi, cast):
            try:
                v = cast((q.get(name) or [default])[0])
            except (TypeError, ValueError, OverflowError):
                v = default
            if v != v:  # NaN
                v = default
            return min(max(v, lo), hi)
        hours = arg('hours', 24.0, 0.25, HISTORY_API_MAX_HOURS, float)
        mx = arg('max', 600, 10, HISTORY_API_MAX_POINTS, int)
        n, pts = history_window(hours, mx)
        return self._send(200, _safe_json({'hours': hours, 'max': mx, 'n_total': n, 'n': len(pts),
                                           'generated_epoch': round(time.time(), 1), 'points': pts}))

    def _own_origins(self):
        return {'http://%s:%s' % (h, S.port) for h in ('localhost', '127.0.0.1', '[::1]')}

    def _cross_site(self):
        """Why a side-effecting request is refused, or None. Browsers send Sec-Fetch-Site and Origin; the page's own
        fetch also sends X-IWO-Refresh: 1, which a page on another origin cannot add without a CORS preflight
        (this server answers no OPTIONS request), and which no <img>/no-cors request can carry."""
        sfs = (self.headers.get('Sec-Fetch-Site') or '').strip().lower()
        if sfs and sfs not in ('same-origin', 'none'):
            return 'cross-site request refused (Sec-Fetch-Site: %s)' % sfs
        origin = (self.headers.get('Origin') or '').strip().lower()
        if origin and origin not in self._own_origins():
            return 'cross-site request refused (Origin: %s)' % origin
        if (self.headers.get('X-IWO-Refresh') or '').strip() != '1':
            return 'missing header X-IWO-Refresh: 1 (the dashboard page sends it; with curl add -H "X-IWO-Refresh: 1")'
        return None

    def _refresh(self, q):
        why = self._cross_site()
        if why:
            return self._send(403, {'error': why})
        want_cern = (q.get('cern') or ['0'])[0] in ('1', 'true', 'yes')
        res = {'local': None, 'cern': None}
        lo = run_local(LOCAL_FORCE_MIN_GAP)
        res['local'] = {'ran': 'refreshed', 'busy': 'skipped (a local collection is already in progress)'}.get(
            lo, 'skipped (refreshed %.0f s ago)' % (time.time() - S.last_local))
        code = 200
        if want_cern:
            outcome, env, retry = run_cern(CERN_MIN_GAP)
            if outcome == 'busy':
                code = 429
                res['cern'] = 'refused: a CERN query is already in progress'
                res['retry_after_s'] = retry or 30
            elif outcome == 'too_soon':
                code = 429
                gap = time.time() - (C.CERN_STATE['last_attempt_epoch'] or 0)
                res['cern'] = 'refused: last CERN query %.0f s ago (minimum gap %d s)' % (gap, CERN_MIN_GAP)
                res['retry_after_s'] = retry
            else:
                res['cern'] = 'refreshed' if env.get('ok') else 'failed: %s' % env.get('error')
        out = _safe_json(build_status())
        out['refresh'] = res
        extra = {'Retry-After': str(res['retry_after_s'])} if code == 429 else None
        return self._send(code, out, extra=extra)


def _safe_json(o):
    """Replace NaN/inf (not valid JSON) with None."""
    if isinstance(o, float):
        return o if o == o and o not in (float('inf'), float('-inf')) else None
    if isinstance(o, dict):
        return {k: _safe_json(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_safe_json(v) for v in o]
    return o


def port_free(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('127.0.0.1', port))
        return True
    except OSError:
        return False
    finally:
        s.close()


# ----------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description='IWO Mission Control (read-only dashboard)')
    ap.add_argument('--port', type=int, default=int(os.environ.get('IWO_DASH_PORT', '8765')))
    ap.add_argument('--once', action='store_true', help='run every collector once, print JSON, exit')
    ap.add_argument('--out', help='with --once: also write the JSON to this file')
    ap.add_argument('--no-cern', action='store_true', help='skip the CERN collector')
    ap.add_argument('--version', action='store_true')
    a = ap.parse_args()
    if a.version:
        print('IWO Mission Control %s, python %s, dashboard %s' % (VERSION, sys.version.split()[0], HERE))
        return 0
    S.port = a.port

    if a.once:
        load_history()
        timings = {}
        t = time.time()
        run_local()
        timings['local_s'] = round(time.time() - t, 2)
        t = time.time()
        run_git()
        timings['git_s'] = round(time.time() - t, 2)
        if not a.no_cern:
            t = time.time()
            run_cern(min_gap=0, persist=False)   # one-shot: never appends to history.jsonl
            timings['cern_s'] = round(time.time() - t, 2)
        st = _safe_json(build_status())
        st['once_timings'] = timings
        txt = json.dumps(st, indent=1, default=str, allow_nan=False)
        if a.out:
            Path(a.out).write_text(txt + '\n', encoding='utf-8')
            print('wrote %s (%d bytes); timings %s' % (a.out, len(txt), timings))
        else:
            print(txt)
        return 0

    if not port_free(a.port):
        print('port %d on 127.0.0.1 is already in use (dashboard already running?). '
              'Open http://localhost:%d or pick another port with --port / IWO_DASH_PORT.' % (a.port, a.port), file=sys.stderr)
        return 2
    load_history()
    httpd = ThreadingHTTPServer(('127.0.0.1', a.port), Handler)
    httpd.daemon_threads = True
    threads = [threading.Thread(target=loop, args=(run_local, LOCAL_INTERVAL), name='local', daemon=True),
               threading.Thread(target=loop, args=(run_git, GIT_INTERVAL, 2.0), name='git', daemon=True),
               threading.Thread(target=cern_loop, args=(1.0,), name='cern', daemon=True)]
    for th in threads:
        th.start()

    def _stop(*_):
        S.stop.set()
        threading.Thread(target=httpd.shutdown, daemon=True).start()
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    print('IWO Mission Control %s: http://localhost:%d  (read-only; Ctrl+C to stop)' % (VERSION, a.port), flush=True)
    try:
        httpd.serve_forever(poll_interval=0.5)
    finally:
        S.stop.set()
        httpd.server_close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
