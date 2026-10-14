#!/usr/bin/env python3
"""Claude Code PreToolUse guard for the IWO private research repo.

- blocks a raw `git push`: only tools/push_private.sh and tools/push_public.sh may push, and only when the user asks;
- asks the user before an ATLAS launch or a CERN action (in headless relay mode the question cannot be answered,
  so the action is refused);
- blocks writes, moves and deletions in data_private/raw/ (raw data are read-only, charter section 8).

Input: the hook JSON on stdin. Exit 2 = block (stderr is shown to Claude). A JSON "ask" decision on stdout = prompt
the user. Malformed input fails open (exit 0) so that a broken hook never stops ordinary work.
"""
import json
import re
import sys


def ask(reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "permissionDecision": "ask",
                                             "permissionDecisionReason": reason}}))
    sys.exit(0)


def block(reason):
    print(reason, file=sys.stderr)
    sys.exit(2)


def git_subcommands(cmd):
    """Subcommand of every `git` call in a shell command; quoted text (messages, paths) is ignored."""
    subs = []
    for m in re.finditer(r"\bgit(?:\.exe)?\b", cmd, re.IGNORECASE):
        seg = re.split(r"[;\n|&]", cmd[m.end():], maxsplit=1)[0]
        seg = re.sub(r"\"[^\"]*\"|'[^']*'", " Q ", seg)
        toks = seg.split()
        i = 0
        while i < len(toks) and toks[i].startswith("-"):
            i += 2 if toks[i] in ("-C", "-c") else 1
        if i < len(toks):
            subs.append(toks[i].lower())
    return subs


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    tool = data.get("tool_name", "")
    inp = data.get("tool_input") or {}

    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        path = str(inp.get("file_path", "")).replace("\\", "/").lower()
        if "/data_private/raw/" in path:
            block("data_private/raw/ is read-only (charter section 8). Write derived files to data_private/derived/.")
        sys.exit(0)

    cmd = str(inp.get("command", ""))
    low = cmd.lower()
    if "push" in git_subcommands(cmd) and "push_private.sh" not in low and "push_public.sh" not in low:
        block("Raw 'git push' is blocked. Push only with tools/push_private.sh or tools/push_public.sh, "
              "and only when the user has asked for the push.")
    if re.search(r"\b(rm|del|remove-item|mv|move-item|set-content|out-file|add-content)\b[^\n]*data_private[/\\]raw", low):
        block("data_private/raw/ is read-only (charter section 8).")
    if (re.search(r"deckbuild(\.exe)?\s+-run", low)
            or (re.search(r"python[^\n]*run_atlas\.py", low) and "--rescore" not in low and "--help" not in low)
            or re.search(r"python[^\n]*run_campaign\.py", low)):
        ask("ATLAS launch: it uses the licence and the launch budget (config/solver.yaml). "
            "Approve only if you said go for this run.")
    if (re.search(r"\b(ssh|scp|rsync|sftp)\b[^\n]*(lxplus|cm-cern)", low)
            or re.search(r"\bcondor_(submit|rm|release|hold|qedit)\b", low)
            or re.search(r"dft_flow\.sh(?!\s+(status|check)\b)", low)):
        ask("CERN action: approve only if you are logged in and asked for this step. "
            "Never type passwords or 2FA codes into the chat.")
    sys.exit(0)


if __name__ == "__main__":
    main()
