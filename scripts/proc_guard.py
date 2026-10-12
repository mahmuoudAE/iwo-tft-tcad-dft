#!/usr/bin/env python3
"""Process guard for the DeckBuild launches of scripts/run_atlas.py (2026-10-13; Windows, stdlib ctypes only; no simulator logic).

Why (run_0075, CODEX_WORK_CHAT 2026-10-12T16:40Z, disclosure 2): DeckBuild kept running behind an open TonyPlot viewer until the 5400 s
timeout; `taskkill /T /F /PID <deckbuild>` then killed the deckbuild tree, but a second viewer whose parent had already exited (outside
the tree) still held the inherited stdout/stderr pipe handles, so the runner's second, unbounded p.communicate() stalled until that window
was closed by hand.

What it does, WITHOUT changing how deckbuild is started (run_atlas keeps the same Popen argv, cwd and stdout/stderr pipes):
  attach(pid)  puts the launched process into a new job object right after CreateProcess. Limit JOB_OBJECT_LIMIT_BREAKAWAY_OK only (a child
               that asks to break away still starts; no kill-on-close: the job changes nothing in the process lifetimes). Every process a
               job member creates later is in the job, even after its own parent has exited (a viewer started through a launcher stub).
               CAPTURE IS BEST-EFFORT (Codex D4, 2026-10-12T20:28Z): the assignment follows the launch and breakaway is allowed, so a child
               created before the assignment or one that breaks away is only caught by parent-pid tracking. Failure is recorded and the
               guard falls back to parent-pid tracking. IWO_ATLAS_JOB=0 disables the job.
  poll()       records every process of the launch once (job members + parent-pid descendants of the launched pid, creation time checked
               against PID reuse) and applies the viewer policy to VIEWERS (tonyplot.exe, tonyplot3d.exe): 'record' (DEFAULT, Codex D4: until
               a supervised DeckBuild test qualifies viewer termination; stand-ins prove the plumbing only) only records a viewer;
               IWO_ATLAS_VIEWERS=kill terminates it when it is first seen.
  kill_all()   on a timeout (Codex blocker 1, 2026-10-12T20:28Z): identity-checked TerminateProcess on every recorded, job or tree process of
               the launch, one process at a time, children before the launched process, in up to KILL_PASSES passes; the licence daemons
               (KEEP) are NEVER terminated, whatever their parent (no `taskkill /T` tree kill any more: it killed still-parented children
               before any exclusion could apply). Every decision uses the VERIFIED executable name (exe_name: image name read through the
               process handle, creation time checked; Codex rev-2 item 1, 2026-10-12T21:01Z), never a snapshot name: a job member created after
               the snapshot is still identified, and a process whose name cannot be verified is never terminated, is re-scanned in every
               pass and is reported as unidentified (and as a survivor if alive). Only when TerminateProcess fails is a single-process fallback command run (FALLBACK_CMD,
               never /T), bounded by CMD_TIMEOUT_S and by the overall CLEANUP_BUDGET_S; an error on one process is recorded and the cleanup
               continues. Returns what was terminated, kept, failed and what survived.
PipeReader / decode: the launcher's stdout/stderr are read by daemon threads (as communicate() does) and decoded exactly like the former
text=True (locale encoding, universal newlines; errors='replace' instead of an exception), so a bounded wait can give up on a pipe that a
foreign process keeps open.
"""
from __future__ import annotations

import locale
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone

VIEWERS = ('tonyplot.exe', 'tonyplot3d.exe')                                  # Silvaco viewers (C:/sedatools/lib/tonyplot*/.../*.exe)
KEEP = ('sflm_monitord.exe', 'rpc.sflmserverd.exe', 'sflm.exe', 'sflmserverd.exe')   # licence daemons: never killed (run_0075 launch started
#                                                                               sflm_monitord.exe, which outlives the run by design)
FALLBACK_CMD = ('taskkill', '/F', '/PID', '{pid}')   # one process, never /T; only after a TerminateProcess failure
CMD_TIMEOUT_S = 10.0       # bound of one fallback command
CLEANUP_BUDGET_S = 60.0    # bound of all fallback commands of one cleanup
KILL_PASSES = 3            # re-scan passes (a process started while the cleanup runs is caught by the next pass)
WIN = sys.platform == 'win32'


def utc(epoch=None):
    return datetime.fromtimestamp(time.time() if epoch is None else epoch, timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-4] + 'Z'


def decode(data: bytes) -> str:
    """bytes -> text exactly as Popen(text=True).communicate() returns it (the TextIOWrapper default encoding: UTF-8 in UTF-8 mode, else
    the locale encoding; '\\r\\n' and '\\r' -> '\\n'), but with errors='replace' so an undecodable byte cannot raise"""
    enc = 'utf-8' if sys.flags.utf8_mode else locale.getencoding()
    return data.decode(enc, errors='replace').replace('\r\n', '\n').replace('\r', '\n')


class PipeReader(threading.Thread):
    """daemon thread draining one pipe of the launched process into memory; done is set at EOF (or on a read error)"""
    def __init__(self, f):
        super().__init__(daemon=True); self.f = f; self.chunks = []; self.error = None; self.done = threading.Event(); self.start()

    def run(self):
        try:
            rd = getattr(self.f, 'read1', self.f.read)
            while True:
                b = rd(65536)
                if not b: break
                self.chunks.append(b)
        except Exception as e:   # recorded, never raised into the runner
            self.error = f'{type(e).__name__}: {e}'
        finally:
            self.done.set()

    def data(self) -> bytes:
        return b''.join(list(self.chunks))


if WIN:
    import ctypes
    from ctypes import wintypes

    k32 = ctypes.WinDLL('kernel32', use_last_error=True)
    PROCESS_TERMINATE, PROCESS_SET_QUOTA, PROCESS_QUERY_LIMITED_INFORMATION = 0x0001, 0x0100, 0x1000
    TH32CS_SNAPPROCESS, STILL_ACTIVE = 0x2, 259
    JobObjectBasicProcessIdList, JobObjectExtendedLimitInformation = 3, 9
    JOB_OBJECT_LIMIT_BREAKAWAY_OK = 0x0800
    INVALID_HANDLE = ctypes.c_void_p(-1).value

    class PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [('dwSize', wintypes.DWORD), ('cntUsage', wintypes.DWORD), ('th32ProcessID', wintypes.DWORD),
                    ('th32DefaultHeapID', ctypes.c_size_t), ('th32ModuleID', wintypes.DWORD), ('cntThreads', wintypes.DWORD),
                    ('th32ParentProcessID', wintypes.DWORD), ('pcPriClassBase', ctypes.c_long), ('dwFlags', wintypes.DWORD),
                    ('szExeFile', ctypes.c_wchar * 260)]

    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [('PerProcessUserTimeLimit', ctypes.c_int64), ('PerJobUserTimeLimit', ctypes.c_int64), ('LimitFlags', wintypes.DWORD),
                    ('MinimumWorkingSetSize', ctypes.c_size_t), ('MaximumWorkingSetSize', ctypes.c_size_t), ('ActiveProcessLimit', wintypes.DWORD),
                    ('Affinity', ctypes.c_size_t), ('PriorityClass', wintypes.DWORD), ('SchedulingClass', wintypes.DWORD)]

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [(n, ctypes.c_uint64) for n in ('ReadOperationCount', 'WriteOperationCount', 'OtherOperationCount',
                                                     'ReadTransferCount', 'WriteTransferCount', 'OtherTransferCount')]

    class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [('BasicLimitInformation', JOBOBJECT_BASIC_LIMIT_INFORMATION), ('IoInfo', IO_COUNTERS), ('ProcessMemoryLimit', ctypes.c_size_t),
                    ('JobMemoryLimit', ctypes.c_size_t), ('PeakProcessMemoryUsed', ctypes.c_size_t), ('PeakJobMemoryUsed', ctypes.c_size_t)]

    class JOBOBJECT_BASIC_PROCESS_ID_LIST(ctypes.Structure):
        _fields_ = [('NumberOfAssignedProcesses', wintypes.DWORD), ('NumberOfProcessIdsInList', wintypes.DWORD),
                    ('ProcessIdList', ctypes.c_size_t * 2048)]

    for _n, _a, _r in (('CreateJobObjectW', [ctypes.c_void_p, wintypes.LPCWSTR], wintypes.HANDLE),
                       ('SetInformationJobObject', [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD], wintypes.BOOL),
                       ('AssignProcessToJobObject', [wintypes.HANDLE, wintypes.HANDLE], wintypes.BOOL),
                       ('QueryInformationJobObject', [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)], wintypes.BOOL),
                       ('OpenProcess', [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
                       ('GetProcessTimes', [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4, wintypes.BOOL),
                       ('GetExitCodeProcess', [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)], wintypes.BOOL),
                       ('TerminateProcess', [wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
                       ('CloseHandle', [wintypes.HANDLE], wintypes.BOOL),
                       ('CreateToolhelp32Snapshot', [wintypes.DWORD, wintypes.DWORD], wintypes.HANDLE),
                       ('Process32FirstW', [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)], wintypes.BOOL),
                       ('Process32NextW', [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)], wintypes.BOOL),
                       ('QueryFullProcessImageNameW', [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)], wintypes.BOOL)):
        getattr(k32, _n).argtypes = _a; getattr(k32, _n).restype = _r

    def exe_name(pid, ct=None):
        """VERIFIED executable name of a live process (Codex rev-2 item 1): image name read through a handle of the process itself, and
        only if its creation time equals ct (when given); None when it cannot be verified (gone, access denied, pid reused)"""
        h = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h: return None
        try:
            c, x, kt, ut = (wintypes.FILETIME() for _ in range(4))
            if ct is not None and not (k32.GetProcessTimes(h, ctypes.byref(c), ctypes.byref(x), ctypes.byref(kt), ctypes.byref(ut))
                                       and ((c.dwHighDateTime << 32) | c.dwLowDateTime) == ct): return None
            buf = ctypes.create_unicode_buffer(32768); n = wintypes.DWORD(len(buf))
            if not k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n)): return None
            return buf.value.replace('/', '\\').rsplit('\\', 1)[-1] or None
        finally:
            k32.CloseHandle(h)

    def snapshot():
        """{pid: (ppid, exe name)} of every process (Toolhelp32)"""
        h = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0); out = {}
        if not h or h == INVALID_HANDLE: return out
        try:
            e = PROCESSENTRY32W(); e.dwSize = ctypes.sizeof(e); ok = k32.Process32FirstW(h, ctypes.byref(e))
            while ok:
                out[int(e.th32ProcessID)] = (int(e.th32ParentProcessID), e.szExeFile); ok = k32.Process32NextW(h, ctypes.byref(e))
        finally:
            k32.CloseHandle(h)
        return out

    def proc_info(pid):
        """(creation FILETIME as int, alive?) or (None, False) if the process cannot be opened (gone, or access denied)"""
        h = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h: return None, False
        try:
            c, x, kt, ut = (wintypes.FILETIME() for _ in range(4)); code = wintypes.DWORD()
            if not k32.GetProcessTimes(h, ctypes.byref(c), ctypes.byref(x), ctypes.byref(kt), ctypes.byref(ut)): return None, False
            alive = bool(k32.GetExitCodeProcess(h, ctypes.byref(code))) and code.value == STILL_ACTIVE
            return (c.dwHighDateTime << 32) | c.dwLowDateTime, alive
        finally:
            k32.CloseHandle(h)

    def ft_epoch(ft): return (ft - 116444736000000000) / 1e7 if ft else None

    def terminate(pid, ct):
        """TerminateProcess(pid, 1) only if it is still the process created at ct (PID-reuse guard); returns a result word"""
        h = k32.OpenProcess(PROCESS_TERMINATE | PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h: return 'gone' if proc_info(pid)[0] is None else f'open failed (error {ctypes.get_last_error()})'
        try:
            c, x, kt, ut = (wintypes.FILETIME() for _ in range(4))
            if ct is not None and k32.GetProcessTimes(h, ctypes.byref(c), ctypes.byref(x), ctypes.byref(kt), ctypes.byref(ut)) \
                    and ((c.dwHighDateTime << 32) | c.dwLowDateTime) != ct:
                return 'gone (pid reused by another process; not touched)'
            code = wintypes.DWORD()
            if k32.GetExitCodeProcess(h, ctypes.byref(code)) and code.value != STILL_ACTIVE: return 'already exited'
            return 'terminated' if k32.TerminateProcess(h, 1) else f'terminate failed (error {ctypes.get_last_error()})'
        finally:
            k32.CloseHandle(h)


class Guard:
    """process guard of ONE deckbuild launch (see the module docstring); every method is best-effort and never raises into the runner"""
    def __init__(self, viewers=None, viewer_policy=None, use_job=None, keep=None):
        self.viewers = tuple(x.lower() for x in (VIEWERS if viewers is None else viewers))
        self.keep = tuple(x.lower() for x in (KEEP if keep is None else keep))
        self.policy = (viewer_policy or os.environ.get('IWO_ATLAS_VIEWERS', 'record')).lower()   # Codex D4: default record
        if self.policy not in ('kill', 'record'): self.policy = 'record'
        self.use_job = (os.environ.get('IWO_ATLAS_JOB', '1') != '0') if use_job is None else use_job
        self.job = None; self.job_note = 'not attempted'; self.root = None; self.root_ct = None
        self.seen = {}; self.viewer_log = []; self.kill = None; self.errors = []

    # ---- setup
    def attach(self, pid):
        self.root = int(pid)
        if not WIN: self.job_note = 'not Windows: no job, no tracking'; return
        try:
            self.root_ct, _ = proc_info(self.root)
            if not self.use_job: self.job_note = 'disabled (IWO_ATLAS_JOB=0)'
            else:
                j = k32.CreateJobObjectW(None, None)
                if not j: self.job_note = f'CreateJobObject failed (error {ctypes.get_last_error()})'
                else:
                    info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION(); info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_BREAKAWAY_OK
                    k32.SetInformationJobObject(j, JobObjectExtendedLimitInformation, ctypes.byref(info), ctypes.sizeof(info))
                    h = k32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_TERMINATE, False, self.root)
                    ok = bool(h) and bool(k32.AssignProcessToJobObject(j, h)); err = ctypes.get_last_error()
                    if h: k32.CloseHandle(h)
                    if ok: self.job = j; self.job_note = 'assigned (JOB_OBJECT_LIMIT_BREAKAWAY_OK; no kill-on-close)'
                    else: k32.CloseHandle(j); self.job_note = f'AssignProcessToJobObject failed (error {err}): parent-pid tracking only'
            self.poll()
            pre = [p for p, r in self.seen.items() if p != self.root]   # children created before the assignment are not in the job
            if self.job and pre: self.job_note += f'; {len(pre)} child(ren) existed before the assignment (tracked by parent pid)'
        except Exception as e:
            self.errors.append(f'attach: {type(e).__name__}: {e}')

    def job_pids(self):
        if not (WIN and self.job): return []
        b = JOBOBJECT_BASIC_PROCESS_ID_LIST()
        if not k32.QueryInformationJobObject(self.job, JobObjectBasicProcessIdList, ctypes.byref(b), ctypes.sizeof(b), None): return []
        return [int(b.ProcessIdList[i]) for i in range(b.NumberOfProcessIdsInList)]

    # ---- tracking
    def _alive_known(self):
        """{pid: creation time} of the root and every recorded process that is still the same process"""
        known = {}
        if self.root is not None:
            ct, alive = proc_info(self.root)
            if alive and (self.root_ct is None or ct == self.root_ct): known[self.root] = ct
        for pid, r in self.seen.items():
            ct, alive = proc_info(pid)
            if alive and ct == r['_ct']: known[pid] = ct
        return known

    def poll(self):
        """record the processes of this launch (job members + parent-pid descendants, creation-time ordered) and apply the viewer policy"""
        if not WIN or self.root is None: return
        try:
            snap = snapshot(); members = set(self.job_pids()); known = self._alive_known(); now = time.time()
            new = {}
            for pid in members:
                if pid in snap and pid not in known:
                    ct, alive = proc_info(pid)
                    if alive: new[pid] = ct
            grew = True
            while grew:
                grew = False
                for pid, (ppid, _) in snap.items():
                    if pid in known or pid in new: continue
                    pct = known.get(ppid, new.get(ppid))
                    if ppid in known or ppid in new:
                        ct, alive = proc_info(pid)
                        if alive and ct is not None and (pct is None or ct >= pct): new[pid] = ct; grew = True
            for pid, ct in new.items():
                if pid in self.seen and self.seen[pid]['_ct'] == ct: continue
                ppid, name = snap.get(pid, (None, '?'))
                self.seen[pid] = {'pid': pid, 'ppid': ppid, 'name': name, 'created_utc': utc(ft_epoch(ct)) if ct else None,
                                  'first_seen_utc': utc(now), 'in_job': pid in members, '_ct': ct}
            for pid, r in list(self.seen.items()):
                if pid == self.root or r['name'].lower() not in self.viewers or r.get('_viewer_done'): continue
                v = {'pid': pid, 'name': r['name'], 'ppid': r['ppid'], 'created_utc': r['created_utc'], 'first_seen_utc': r['first_seen_utc'], 'policy': self.policy}
                if self.policy == 'kill':   # opt-in (D4); terminated only under its verified executable name (rev-2 item 1)
                    vn = exe_name(pid, r['_ct'])
                    if not vn: v['result'] = 'not terminated: executable name not verified'
                    elif vn.lower() in self.viewers and vn.lower() not in self.keep: v['result'] = terminate(pid, r['_ct']); v['killed_utc'] = utc()
                    else: v['result'] = f'not terminated: verified name {vn}'
                r['_viewer_done'] = True; self.viewer_log.append(v)
        except Exception as e:
            self.errors.append(f'poll: {type(e).__name__}: {e}')

    # ---- timeout kill (Codex blocker 1, 2026-10-12T20:28Z)
    def _candidates(self):
        """{pid: (creation time, snapshot name or None, source)} of every live process of the launch: the launched process, the recorded
        ones (same creation time as when first seen: PID-reuse guard) and the job members. The job is queried BEFORE the snapshot, and the
        snapshot name is for the record only: kill_all decides on the VERIFIED executable name (exe_name), never on this one."""
        members = set(self.job_pids()); snap = snapshot(); out = {}
        if self.root is not None:
            ct, alive = proc_info(self.root)
            if alive and (self.root_ct is None or ct == self.root_ct): out[self.root] = (ct, snap.get(self.root, (None, None))[1], 'launched')
        for pid, r in self.seen.items():
            ct, alive = proc_info(pid)
            if alive and ct == r['_ct']: out[pid] = (ct, r['name'], 'job' if pid in members else 'tracked')
        for pid in members:
            if pid not in out:
                ct, alive = proc_info(pid)
                if alive: out[pid] = (ct, snap.get(pid, (None, None))[1], 'job')
        return out

    def _fallback(self, pid, ct, rec, t_end):
        """single-process fallback command after a TerminateProcess failure: identity re-checked first, never /T, bounded by CMD_TIMEOUT_S
        and the cleanup budget; any failure is recorded, never raised"""
        if time.monotonic() >= t_end: return 'fallback skipped (cleanup budget exhausted)'
        c, alive = proc_info(pid)
        if not alive: return 'gone before the fallback'
        if ct is not None and c != ct: return 'pid reused: fallback not run'
        cmd = [x.replace('{pid}', str(pid)) for x in FALLBACK_CMD]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, errors='replace', timeout=max(0.1, min(CMD_TIMEOUT_S, t_end - time.monotonic())))
            out = f'fallback returncode {r.returncode}'
        except subprocess.TimeoutExpired:
            out = f'fallback timed out (bounded at {CMD_TIMEOUT_S:g} s)'
        except Exception as e:
            out = f'fallback error {type(e).__name__}'
        rec['fallback'].append({'pid': pid, 'command': ' '.join(cmd), 'result': out})
        return out

    def kill_all(self, reason, popen=None, wait_s=60.0):
        """identity-checked TerminateProcess per process (children first, the launched process last), decided on the VERIFIED executable
        name (exe_name: read through the process handle, creation time checked; Codex rev-2 item 1): KEEP never terminated; a process whose
        name cannot be verified is never terminated nor given the fallback, is NOT marked handled (re-scanned in every pass) and is reported
        as unidentified and, if alive, as a survivor. Up to KILL_PASSES re-scans; bounded single-process fallback only after a TerminateProcess
        failure; errors are recorded and the cleanup continues; then a bounded wait (wait_s) for the launched process."""
        rec = {'reason': reason, 'utc': utc(), 'epoch_s': time.time(),
               'method': ('identity-checked TerminateProcess per process on the verified executable name, no /T tree kill; KEEP never terminated; '
                          'unidentified processes never terminated; bounded single-process fallback'),
               'targets': [], 'kept': [], 'unidentified': [], 'exited_before_identification': [], 'fallback': [], 'errors': [], 'survivors': []}
        t_end = time.monotonic() + CLEANUP_BUDGET_S; handled = set(); unident = {}
        for k in range(KILL_PASSES):
            try:
                self.poll(); cand = self._candidates() if WIN else {}
            except Exception as e:
                rec['errors'].append(f'scan {k + 1}: {type(e).__name__}: {e}'); cand = {}
            new = {p: v for p, v in cand.items() if (p, v[0]) not in handled}
            if not new: break
            for pid in sorted(new, key=lambda p: (p == self.root, p)):
                ct, sname, src = new[pid]
                try:
                    name = exe_name(pid, ct)
                    if not name:
                        c, alive = proc_info(pid)
                        if not (alive and c == ct):   # it exited meanwhile: nothing to terminate, nothing touched
                            handled.add((pid, ct)); unident.pop((pid, ct), None)
                            rec['exited_before_identification'].append({'pid': pid, 'snapshot_name': sname, 'source': src}); continue
                        # deferred: not handled, re-scanned next pass, reported at the end
                        u = unident.setdefault((pid, ct), {'pid': pid, 'snapshot_name': sname, 'source': src, 'scans': 0}); u['scans'] += 1; continue
                    handled.add((pid, ct)); unident.pop((pid, ct), None)
                    if name.lower() in self.keep:
                        rec['kept'].append({'pid': pid, 'name': name, 'source': src, 'why': 'licence daemon (KEEP, verified name): never terminated'}); continue
                    res = terminate(pid, ct)
                    if res.startswith(('terminate failed', 'open failed')): res += '; ' + self._fallback(pid, ct, rec, t_end)
                    rec['targets'].append({'pid': pid, 'name': name, 'source': src, 'pass': k + 1, 'result': res})
                except Exception as e:
                    handled.add((pid, ct)); rec['errors'].append(f'{pid} {sname}: {type(e).__name__}: {e}')
            time.sleep(0.2)
        try:
            if popen is not None:
                if not WIN: popen.kill()
                try: popen.wait(timeout=wait_s); rec['launched_process_exited'] = True
                except subprocess.TimeoutExpired: rec['launched_process_exited'] = False
            if WIN:
                time.sleep(0.3)
                for t in rec['targets']:
                    ct, alive = proc_info(t['pid'])
                    if alive and ct == ((self.seen.get(t['pid']) or {}).get('_ct', ct)): rec['survivors'].append({'pid': t['pid'], 'name': t['name']})
                for t in rec['kept']: t['alive_after_cleanup'] = proc_info(t['pid'])[1]
                for (pid, ct), u in unident.items():
                    c, alive = proc_info(pid); u['alive_after_cleanup'] = bool(alive and c == ct); rec['unidentified'].append(u)
                    if u['alive_after_cleanup']: rec['survivors'].append({'pid': pid, 'name': u['snapshot_name'], 'unidentified': True})
        except Exception as e:
            rec['errors'].append(f'wait/survivors: {type(e).__name__}: {e}')
        self.kill = rec
        return rec

    def close(self):
        if WIN and self.job:
            try: k32.CloseHandle(self.job)
            except Exception: pass
            self.job = None

    def record(self):
        """JSON-able record for execution.json['process_guard']"""
        return {'version': '2026-10-13c', 'job': self.job_note, 'viewer_policy': self.policy, 'viewer_names': list(self.viewers),
                'keep_names': list(self.keep), 'launched_pid': self.root,
                'capture': 'best-effort: job assignment follows the launch and breakaway is allowed (Codex D4); parent-pid tracking otherwise',
                'processes_seen': [{k: v for k, v in r.items() if not k.startswith('_')} for r in self.seen.values()],
                'viewers': self.viewer_log, 'kill': self.kill, 'errors': self.errors}
