"""Bounded Windows tracking of observed, identity-pinned child processes.

Uses only the standard library. Snapshots are used internally to find children;
only proven owned identities are retained or eligible for termination. This
does not supply or replace a simulator's native completion evidence.
"""
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import time


class WindowsProcesses:
    def __init__(self):
        self.dll = ctypes.WinDLL('kernel32', use_last_error=True)
        signatures = {
            'CreateToolhelp32Snapshot': ([wintypes.DWORD, wintypes.DWORD], wintypes.HANDLE),
            'OpenProcess': ([wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
            'CloseHandle': ([wintypes.HANDLE], wintypes.BOOL),
            'WaitForSingleObject': ([wintypes.HANDLE, wintypes.DWORD], wintypes.DWORD),
            'GetProcessTimes': ([wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4, wintypes.BOOL),
            'GetExitCodeProcess': ([wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)], wintypes.BOOL),
            'TerminateProcess': ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
            'QueryFullProcessImageNameW': ([wintypes.HANDLE, wintypes.DWORD,
                wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)], wintypes.BOOL),
        }
        class Entry(ctypes.Structure):
            _fields_ = [('dwSize', wintypes.DWORD), ('cntUsage', wintypes.DWORD),
                        ('th32ProcessID', wintypes.DWORD), ('th32DefaultHeapID', ctypes.c_size_t),
                        ('th32ModuleID', wintypes.DWORD), ('cntThreads', wintypes.DWORD),
                        ('th32ParentProcessID', wintypes.DWORD), ('pcPriClassBase', wintypes.LONG),
                        ('dwFlags', wintypes.DWORD), ('szExeFile', wintypes.WCHAR * 260)]
        self.Entry = Entry
        for name in ('Process32FirstW', 'Process32NextW'):
            signatures[name] = ([wintypes.HANDLE, ctypes.POINTER(Entry)], wintypes.BOOL)
        for name, (arguments, result) in signatures.items():
            function = getattr(self.dll, name)
            function.argtypes, function.restype = arguments, result

    def snapshot(self):
        handle = self.dll.CreateToolhelp32Snapshot(2, 0)
        if handle == ctypes.c_void_p(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        entry, result = self.Entry(), []
        self.snapshot_names = {}
        entry.dwSize = ctypes.sizeof(entry)
        try:
            valid = self.dll.Process32FirstW(handle, ctypes.byref(entry))
            while valid:
                result.append((int(entry.th32ProcessID), int(entry.th32ParentProcessID)))
                self.snapshot_names[int(entry.th32ProcessID)] = entry.szExeFile
                valid = self.dll.Process32NextW(handle, ctypes.byref(entry))
            if ctypes.get_last_error() != 18:  # ERROR_NO_MORE_FILES
                raise ctypes.WinError(ctypes.get_last_error())
        finally:
            self.close(handle)
        return result

    def open(self, pid):
        handle = self.dll.OpenProcess(0x100000 | 0x1000 | 0x0001, False, pid)
        if not handle:
            error = ctypes.get_last_error()
            if error in (87, 1168):  # process ended before it could be opened
                return None
            raise ctypes.WinError(error)
        return handle

    def close(self, handle):
        self.dll.CloseHandle(handle)

    def times(self, handle):
        values = [wintypes.FILETIME() for _ in range(4)]
        if not self.dll.GetProcessTimes(handle, *[ctypes.byref(v) for v in values]):
            raise ctypes.WinError(ctypes.get_last_error())
        return tuple((int(v.dwHighDateTime) << 32) | int(v.dwLowDateTime) for v in values[:2])

    def running(self, handle):
        state = self.dll.WaitForSingleObject(handle, 0)
        if state not in (0, 258):
            raise ctypes.WinError(ctypes.get_last_error())
        return state == 258

    def exit_code(self, handle):
        value = wintypes.DWORD()
        if not self.dll.GetExitCodeProcess(handle, ctypes.byref(value)):
            raise ctypes.WinError(ctypes.get_last_error())
        return int(value.value)

    def terminate(self, handle):
        if not self.running(handle):
            return 'ALREADY_EXITED'
        if not self.dll.TerminateProcess(handle, 1):
            error = ctypes.get_last_error()
            # TerminateProcess returns ERROR_ACCESS_DENIED if normal exit won
            # the race. Ignore that error only after this pinned handle signals.
            if not self.running(handle):
                return 'EXITED_DURING_TERMINATION_REQUEST'
            raise ctypes.WinError(error)
        return 'TERMINATION_REQUEST_ACCEPTED'

    def image_name(self, handle):
        size = wintypes.DWORD(32768)
        buffer = ctypes.create_unicode_buffer(size.value)
        if not self.dll.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
            raise ctypes.WinError(ctypes.get_last_error())
        return Path(buffer.value).name


class OwnedTree:
    def __init__(self, proc, api=None, clock=time.monotonic):
        self.api, self.clock = api or WindowsProcesses(), clock
        self.started, self.root_pid = clock(), proc.pid
        # Borrow Popen's pinned root handle; never close it here.
        root = int(proc._handle)
        created, _ = self.api.times(root)
        self.entries = {proc.pid: dict(pid=proc.pid, parent_pid=None, handle=root,
                                      created_filetime=created, borrowed=True,
                                      first_observed_elapsed_seconds=0.)}
        self.identify(self.entries[proc.pid])
        self.missed_short_lived = 0
        self.uncertain_lineage = False
        self.missed_pids = set()
        self.missed_observations = []
        self.termination_attempts = []

    def identify(self, entry):
        try:
            entry['executable_basename'] = self.api.image_name(entry['handle'])
        except OSError as exc:
            entry['executable_basename'] = None
            entry['image_identity_error'] = str(exc)

    def missed(self, pid, parent, reason, name=None):
        # A vanished observed child may have launched a surviving grandchild.
        # Never silently treat that incomplete lineage as a clean tree exit.
        if pid not in self.missed_pids:
            self.missed_observations.append(dict(pid=pid, observed_parent_pid=parent,
                snapshot_executable_basename=name, identity_pinned=False, reason=reason,
                observed_elapsed_seconds=self.clock()-self.started))
        self.missed_pids.add(pid)
        self.missed_short_lived = len(self.missed_pids)
        self.uncertain_lineage = True

    def scan(self):
        pending = self.api.snapshot()
        names = getattr(self.api, 'snapshot_names', {}).copy()
        changed = True
        while changed:
            changed = False
            for pid, parent in pending:
                if pid in self.entries or parent not in self.entries:
                    continue
                ancestor = self.entries[parent]
                handle = self.api.open(pid)
                if handle is None:
                    self.missed(pid, parent, 'PROCESS_ENDED_BEFORE_OPEN', names.get(pid))
                    continue
                keep = False
                try:
                    created, _ = self.api.times(handle)
                    parent_live = self.api.running(ancestor['handle'])
                    # Query signaled state first: a false result guarantees the
                    # subsequent exit FILETIME is defined, including kill races.
                    parent_created, parent_exit = self.api.times(ancestor['handle'])
                    # A reused parent PID cannot confer ownership on a newer
                    # unrelated child. Native creation/exit times pin lineage.
                    if created >= parent_created and (parent_live or created <= parent_exit):
                        # The candidate may have exited and its PID been reused
                        # between snapshot and OpenProcess. Refresh its parent
                        # while this pinned identity is still alive. A signaled
                        # handle cannot establish the refreshed snapshot's identity.
                        refreshed = dict(self.api.snapshot())
                        if refreshed.get(pid) != parent or not self.api.running(handle):
                            self.missed(pid, parent, 'REFRESHED_LINEAGE_OR_LIVE_IDENTITY_UNAVAILABLE', names.get(pid))
                            continue
                        self.entries[pid] = dict(pid=pid, parent_pid=parent, handle=handle,
                            created_filetime=created, borrowed=False,
                            first_observed_elapsed_seconds=self.clock()-self.started)
                        self.identify(self.entries[pid])
                        keep, changed = True, True
                finally:
                    if not keep:
                        self.api.close(handle)

    def live(self):
        return [entry for entry in self.entries.values() if self.api.running(entry['handle'])]

    def terminate_owned(self):
        # Root/known parents first prevent further launches. Held handles, not
        # bare reused PIDs or name matching, identify every termination target.
        errors = []
        for entry in self.entries.values():
            try:
                if not self.api.running(entry['handle']):
                    continue
                outcome = self.api.terminate(entry['handle'])
                self.termination_attempts.append(dict(pid=entry['pid'],
                    created_filetime=entry['created_filetime'], outcome=outcome))
            except OSError as exc:
                error = dict(pid=entry['pid'], created_filetime=entry['created_filetime'],
                             error=str(exc))
                errors.append(error)
                self.termination_attempts.append({**error, 'outcome': 'TERMINATION_FAILED'})
        return errors

    def evidence(self):
        result = []
        for entry in self.entries.values():
            row = {k: v for k, v in entry.items() if k not in ('handle', 'borrowed')}
            row['still_running'] = self.api.running(entry['handle'])
            row['exit_code'] = None if row['still_running'] else self.api.exit_code(entry['handle'])
            result.append(row)
        return result

    def close(self):
        for entry in self.entries.values():
            if not entry['borrowed']:
                self.api.close(entry['handle'])


def file_signature(directory):
    return tuple(sorted((p.name, p.stat().st_size, p.stat().st_mtime_ns)
                        for p in Path(directory).iterdir() if p.is_file()))


def ensure_no_pending_owned(guard, api=None):
    """Fail closed after a cleanup failure; never stop a process at startup."""
    guard = Path(guard)
    if not guard.exists():
        return
    record = json.loads(guard.read_text())
    if record.get('unobserved_children_possible'):
        raise RuntimeError('Prior owned-process tracking failed; lifecycle guard requires review')
    api = api or WindowsProcesses()
    for entry in record['owned_processes']:
        handle = api.open(entry['pid'])
        if handle is None:
            continue
        try:
            if api.times(handle)[0] == entry['created_filetime'] and api.running(handle):
                raise RuntimeError('A previously owned simulator process is still running; next launch blocked')
        finally:
            api.close(handle)
    guard.unlink()  # fixed project-local guard only, after every identity ended


def write_guard(guard, record):
    """Replace atomically so a failed update leaves the broad poison intact."""
    guard = Path(guard)
    guard.parent.mkdir(parents=True, exist_ok=True)
    temporary = guard.with_name(guard.name + '.pending-write')
    with temporary.open('w', encoding='utf-8') as stream:
        json.dump(record, stream)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(guard)


def wait_owned_tree(proc, directory, deadline, guard, clock=time.monotonic,
                    sleep=time.sleep, tree_factory=OwnedTree, signature=file_signature,
                    quiet_seconds=.75, poll_seconds=.1):
    """Use the original deadline, reserving bounded time for owned cleanup."""
    started = clock()
    cleanup_reserve = min(2., max(0., (deadline-started)/4))
    stop_at = deadline-cleanup_reserve
    tree, failure, error = None, None, None
    stable_since, previous, quiet_observed = None, None, 0.
    launcher_exit_at = None
    cleanup_errors = []
    try:
        tree = tree_factory(proc, clock=clock)
        while clock() < stop_at:
            tree.scan()
            # An ephemeral helper is a lineage gap, not a simulator failure.
            # Keep observing within the original deadline and retain the guard
            # for separate reconciliation after natural native completion.
            launcher = proc.poll()
            if launcher is not None and launcher_exit_at is None:
                launcher_exit_at = clock()-started
            if launcher is not None and not tree.live():
                current = signature(directory)
                if current != previous:
                    previous, stable_since = current, clock()
                quiet_observed = clock()-stable_since
                if quiet_observed >= quiet_seconds:
                    break
            else:
                stable_since, previous = None, None
            sleep(min(poll_seconds, max(0., stop_at-clock())))
        else:
            failure = 'TIMEOUT_OWN_PROCESS_TREE_TERMINATED'
    except Exception as exc:
        failure, error = 'OWNED_PROCESS_TRACKING_FAILED', str(exc)
    uncertain_lineage = failure == 'OWNED_PROCESS_TRACKING_FAILED' or (tree is not None and tree.uncertain_lineage)
    if failure:
        try:
            if tree is not None:
                while True:
                    try:
                        tree.scan()
                    except Exception as exc:
                        uncertain_lineage, error = True, str(exc)
                    cleanup_errors.extend(tree.terminate_owned() or [])
                    # Capture a child created between the pre-kill snapshot
                    # and its owned parent's termination before testing closure.
                    try:
                        tree.scan()
                    except Exception as exc:
                        uncertain_lineage, error = True, str(exc)
                    uncertain_lineage = uncertain_lineage or tree.uncertain_lineage
                    if not tree.live() or clock() >= deadline:
                        break
                    sleep(min(poll_seconds, max(0., deadline-clock())))
            elif proc.poll() is None:
                proc.kill()  # root identity only; no unrelated/name-based kill
        except Exception as exc:
            error = str(exc) if error is None else error + '; cleanup: ' + str(exc)
    try:
        try:
            owned = tree.evidence() if tree is not None else []
        except Exception as exc:
            uncertain_lineage, error = True, str(exc)
            owned = [{**{k: v for k, v in entry.items() if k not in ('handle', 'borrowed')},
                      'still_running': True, 'exit_code': None} for entry in tree.entries.values()]
        unresolved = tree is None or uncertain_lineage or any(row['still_running'] for row in owned)
        review_required = False
        if unresolved:
            write_guard(guard, dict(owned_processes=owned,
                root_pid=proc.pid, run_directory=str(Path(directory).resolve()),
                unobserved_children_possible=tree is None or uncertain_lineage,
                missed_observations=tree.missed_observations if tree is not None else [],
                status='BLOCK_NEXT_LAUNCH_UNTIL_OWNED_EXIT'))
            if failure is not None or tree is None or any(row['still_running'] for row in owned):
                failure = 'OWNED_PROCESS_CLEANUP_UNRESOLVED'
            else:
                review_required = True
        elif Path(guard).exists():
            # The prelaunch poison marker is cleared only after identity-pinned
            # closure. Storage errors leave it in place and block the next launch.
            Path(guard).unlink()
        launcher = proc.poll()
        nonzero_children = [row['pid'] for row in owned
                            if row['pid'] != proc.pid and row['exit_code'] not in (None, 0)]
        if failure is None and nonzero_children:
            failure = 'OWNED_DESCENDANT_EXIT_NONZERO'
        result = dict(status=failure or ('PROCESS_EXITED_LIFECYCLE_REVIEW_REQUIRED' if review_required
                                        else 'PROCESS_EXITED_NOT_YET_VALIDATED'),
                      returncode=launcher if failure is None else None,
                      lifecycle=dict(launcher_returncode=launcher,
                        launcher_exit_observed_elapsed_seconds=launcher_exit_at,
                        observed_owned_processes=owned,
                        observed_owned_all_exited=tree is not None and not any(row['still_running'] for row in owned),
                        lineage_closure_verified=not unresolved,
                        lifecycle_review_required=review_required or unresolved,
                        tracking_scope='Observed lineage pinned by process handles and native creation/exit times; short-lived unobserved descendants cannot be certified.',
                        short_lived_processes_missed=tree.missed_short_lived if tree is not None else None,
                        missed_observations=tree.missed_observations if tree is not None else [],
                        owned_termination_attempts=tree.termination_attempts if tree is not None else [],
                        cleanup_errors=cleanup_errors,
                        output_quiet_seconds_required=quiet_seconds,
                        output_quiet_seconds_observed=quiet_observed,
                        output_drain_passed=failure is None and quiet_observed >= quiet_seconds,
                        cleanup_reserve_seconds=cleanup_reserve,
                        original_deadline_monotonic=deadline, lifecycle_error=error,
                        native_completion_required_separately=True))
    finally:
        if tree is not None:
            tree.close()
    return result
