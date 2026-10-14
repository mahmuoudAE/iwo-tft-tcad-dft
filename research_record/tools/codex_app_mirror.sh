#!/bin/bash
# Mirror the Codex work-chat session (WSL ~/.codex) into the Windows Codex app (C:\Users\moham\.codex) so it can be read
# in the app. The copy is refreshed after every Codex turn (called by codex_advise.sh). If the app copy changed since the
# last sync (the user typed in the app), it is NOT overwritten: the two copies have forked, and the user is warned.
ROOT="/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff (1)"; CHAT="$ROOT/iwo-tft-research-private/codex/work_chat"
WINHOME="/mnt/c/Users/moham/.codex"; SID=$(cat "$CHAT/session_id.txt")
SRC=$(ls -t $(find ~/.codex/sessions -name "*$SID.jsonl") 2>/dev/null | head -1); [ -s "$SRC" ] || { echo "mirror: session file not found"; exit 1; }
REL=${SRC#$HOME/.codex/}; DST="$WINHOME/$REL"; mkdir -p "$(dirname "$DST")"
LAST="$CHAT/.app_mirror_sha"
if [ -e "$DST" ] && [ -s "$LAST" ] && [ "$(sha256sum "$DST" | cut -c1-64)" != "$(cat "$LAST")" ]; then
  echo "mirror: the app copy was changed in the Codex app (forked); not overwritten"; exit 3; fi
cp "$SRC" "$DST.tmp" && mv "$DST.tmp" "$DST" && sha256sum "$DST" | cut -c1-64 > "$LAST"
grep -q "\"id\":\"$SID\"" "$WINHOME/session_index.jsonl" 2>/dev/null || \
  printf '{"id":"%s","thread_name":"IWO Codex work chat (scientific monitor, mirror from WSL)","updated_at":"%s"}\n' "$SID" "$(date -u +%Y-%m-%dT%H:%M:%S.0000000Z)" >> "$WINHOME/session_index.jsonl"
echo "mirror: $(basename "$DST") synced to the Codex app"
