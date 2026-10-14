#!/bin/bash
# Codex work chat: send a milestone digest to the persistent Codex scientific-monitor session and log the exchange.
# usage (WSL): bash tools/codex_advise.sh "<topic>" <digest.md>
# Read-only Codex with live web search. The first call starts the session (BRIEF.md) and stores its id in session_id.txt;
# later calls resume it, so Codex keeps the whole history. Every exchange is appended to CODEX_WORK_CHAT.md.
set -e
ROOT="/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff (1)"
CHAT="$ROOT/iwo-tft-research-private/codex/work_chat"
LOG="$CHAT/CODEX_WORK_CHAT.md"; SID="$CHAT/session_id.txt"
TOPIC="$1"; DIGEST="$2"; [ -s "$DIGEST" ] || { echo "usage: codex_advise.sh <topic> <digest.md>"; exit 2; }
TS=$(date -u +%Y-%m-%dT%H:%MZ); MSG=$(mktemp); OUT=$(mktemp); EV=$(mktemp)
# model/effort by task need (user, 2026-10-13); 3rd arg = tier, env CODEX_MODEL/CODEX_EFFORT override:
#   record   gpt-5.6-sol medium  for-the-record notes, no question asked
#   check    gpt-6-sol   high    periodic monitor, small confirmations
#   review   gpt-6.1-sol xhigh   re-reviews of fixes, small amendments
#   critical gpt-6.1-sol ultra   freezes, register amendments, release/read-out gates, scientific verdicts
TIER=${3:-}; [ -z "$TIER" ] && case "$TOPIC" in "Periodic monitor"*) TIER=check;; *) TIER=critical;; esac
case "$TIER" in record) M0=gpt-5.6-sol; E0=medium;; check) M0=gpt-6-sol; E0=high;; review) M0=gpt-6.1-sol; E0=xhigh;; *) TIER=critical; M0=gpt-6.1-sol; E0=ultra;; esac
MODEL=${CODEX_MODEL:-$M0}; EFF=${CODEX_EFFORT:-$E0}
MOPT=(-m "$MODEL" -c "model_reasoning_effort=\"$EFF\"")
{ [ -s "$SID" ] || { cat "$CHAT/BRIEF.md"; echo; }; echo "## Milestone: $TOPIC ($TS)"; echo; cat "$DIGEST"; echo; [ "$TIER" = record ] || cat "$CHAT/STANDING_QUESTIONS.md"; echo "Token economy: answer only what is asked, verdict first, no restated digest, no repeated open-questions list; never trade accuracy for brevity."; } > "$MSG"
cd "$ROOT"
if [ -s "$SID" ]; then
  if ! codex --search exec resume "$(cat "$SID")" - "${MOPT[@]}" -c sandbox_mode='"read-only"' --skip-git-repo-check -o "$OUT" < "$MSG" > "$EV" 2>&1; then
    grep -q 'active writer' "$EV" && echo "BLOCKED: the session is open interactively (tools/codex_chat.sh); close it and resend" || tail -5 "$EV"
    exit 5
  fi
else
  codex --search exec "${MOPT[@]}" --sandbox read-only --skip-git-repo-check --cd "$ROOT" --json -o "$OUT" - < "$MSG" > "$EV" 2>/dev/null
  grep -o '"thread_id":"[^"]*"' "$EV" | head -1 | cut -d'"' -f4 > "$SID"
  [ -s "$SID" ] || { echo "could not read the session id"; exit 3; }
fi
[ -s "$OUT" ] || { echo "Codex returned no answer"; exit 4; }
{ echo; echo "---"; echo; echo "## $TS: Claude to Codex: $TOPIC (model $MODEL, effort $EFF)"; echo; cat "$DIGEST"; echo; echo "### Codex reply ($TS)"; echo; cat "$OUT"; echo; echo "### Claude decision"; echo; echo "_pending_"; } >> "$LOG"
cat "$OUT"
rm -f "$MSG" "$OUT" "$EV"
# (app mirror disabled 2026-10-10: the Codex app lists only chats it created; WSL mode could not load org settings)
