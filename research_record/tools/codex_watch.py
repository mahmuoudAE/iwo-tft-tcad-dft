#!/usr/bin/env python3
"""Live, read-only view of the Codex work-chat session (and the helper sub-threads Codex opens in ultra mode).

usage (WSL):  python3 tools/codex_watch.py [--all]
Follows ~/.codex/sessions/**/rollout-*.jsonl written in the last 3 hours (new files are picked up as they appear)
and prints reasoning summaries, web searches, commands, file reads and messages as they happen. Ctrl+C to stop.
It never writes anything and never talks to Codex. --all prints the history of the followed files first.
"""
import glob
import json
import os
import sys
import time
from pathlib import Path

SESS = Path.home() / '.codex' / 'sessions'
MAIN = (Path(__file__).resolve().parents[1] / 'codex' / 'work_chat' / 'session_id.txt')
MAIN_ID = MAIN.read_text().strip() if MAIN.exists() else ''
C = {'main': '\033[36m', 'sub': '\033[35m', 'dim': '\033[2m', 'b': '\033[1m', 'r': '\033[0m', 'y': '\033[33m', 'g': '\033[32m'}
W = 160


def short(s, n=W):
    s = ' '.join(str(s).split())
    return s if len(s) <= n else s[:n - 1] + '…'


def fmt(rec):
    p = rec.get('payload') or {}
    t = p.get('type') or rec.get('type', '')
    if t == 'reasoning':
        parts = [x.get('text', '') for x in p.get('summary', []) if isinstance(x, dict)]
        return ('think', ' '.join(parts)) if any(parts) else None
    if t == 'agent_reasoning':
        return ('think', p.get('text', ''))
    if t in ('web_search_call', 'web_search_begin', 'web_search_end'):
        a = p.get('action') or {}
        q = a.get('query') or p.get('query') or a.get('url') or ''
        return ('search', q) if q else None
    if t in ('function_call', 'custom_tool_call', 'local_shell_call'):
        if p.get('name') == 'send_message':
            return ('run', 'hands its findings to the lead thread')
        args = p.get('arguments') or p.get('input') or p.get('action') or ''
        try:
            a = json.loads(args) if isinstance(args, str) else args
            cmd = a.get('cmd') or a.get('command') or a
            if isinstance(cmd, list):
                cmd = ' '.join(map(str, cmd))
        except Exception:
            cmd = args
        return ('run', f"{p.get('name', '')} {cmd}")
    if t in ('exec_command_begin',):
        cmd = p.get('command')
        return ('run', ' '.join(cmd) if isinstance(cmd, list) else cmd)
    if t == 'message' and p.get('role') == 'assistant':
        txt = ' '.join(c.get('text', '') for c in p.get('content', []) if isinstance(c, dict))
        return ('reply', txt) if txt else None
    if t == 'agent_message':
        return ('reply', p.get('message', ''))
    if t == 'task_complete':
        return ('done', 'turn finished')
    return None


def main():
    show_all = '--all' in sys.argv
    start = time.time()
    pos = {}
    print(f"{C['b']}Codex live view{C['r']}  (read-only; main session {MAIN_ID[:8]}…; Ctrl+C to stop)\n")
    while True:
        for f in glob.glob(str(SESS / '**' / 'rollout-*.jsonl'), recursive=True):
            try:
                st = os.stat(f)
            except OSError:
                continue
            if f not in pos:
                if st.st_mtime < start - 3 * 3600:
                    continue
                pos[f] = 0 if show_all or st.st_ctime > start else st.st_size
                tag = 'main' if MAIN_ID and MAIN_ID in f else 'sub ' + Path(f).stem[-8:]
                print(f"{C['dim']}following {tag}: {Path(f).name}{C['r']}")
            if st.st_size <= pos[f]:
                continue
            with open(f, encoding='utf-8', errors='replace') as fh:
                fh.seek(pos[f])
                chunk = fh.read()
                pos[f] = fh.tell()
            tag = 'lead' if MAIN_ID and MAIN_ID in f else 'help'
            for line in chunk.splitlines():
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                out = fmt(rec)
                if not out:
                    continue
                kind, text = out
                ts = (rec.get('timestamp') or '')[11:19]
                col = C['main'] if tag == 'lead' else C['sub']
                if kind == 'reply' and not text.strip():
                    continue
                kc = {'think': C['dim'], 'search': C['y'], 'run': C['y'], 'reply': C['g'], 'done': C['b']}[kind]
                body = text if kind == 'reply' else short(text)
                print(f"{col}{ts} {tag:4}{C['r']} {kc}{kind:6}{C['r']} {body}")
        sys.stdout.flush()
        time.sleep(1.5)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
