#!/bin/bash
# Open the Codex work chat interactively (WSL): resumes the scientific-monitor session, read-only, with web search.
# Interactive turns are stored in Codex's session file (ask Claude to log decisions in CODEX_WORK_CHAT.md).
# While this is open it holds the session writer lock: the automatic digests (codex_advise.sh) cannot resume. Exit (Ctrl-C) when done.
ROOT="/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff (1)"
SID=$(cat "$ROOT/iwo-tft-research-private/codex/work_chat/session_id.txt")
cd "$ROOT" && exec codex resume "$SID" -m gpt-6.1-sol -c model_reasoning_effort='"ultra"' --sandbox read-only --search
