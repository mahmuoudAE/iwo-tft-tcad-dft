#!/bin/bash
# Keep the lxplus SSH master session (ControlPath ~/.ssh/cm-cern) usable for up to 48 h (user request, 2026-09-27).
# Every 5 min: a no-op through the master (resets its 10 h idle timer and keeps the TCP connection active).
# Every 6 h: renew the Kerberos ticket and AFS token on lxplus (kinit -R; aklog); no password is used; works while
# the ticket is renewable (until 2026-10-02 00:47 CERN time).
# Stops after 48 h, when ~/.cern_keepalive_stop exists, or if the master connection is gone. Log: ~/cern_keepalive.log
CP=~/.ssh/cm-cern; H=melrashe@lxplus.cern.ch; LOG=~/cern_keepalive.log
HOURS=${1:-48}   # 2026-09-27: user extended the unattended period to 4 days (run with 96)
END=$(( $(date +%s) + HOURS*3600 )); n=0
echo "$(date -u +%FT%TZ) keepalive started (pid $$), ends $(date -u -d @$END +%FT%TZ)" >> "$LOG"
while [ "$(date +%s)" -lt "$END" ]; do
  if [ -f ~/.cern_keepalive_stop ]; then echo "$(date -u +%FT%TZ) stop file found; keepalive ended" >> "$LOG"; rm -f ~/.cern_keepalive_stop; exit 0; fi
  if [ $((n % 72)) -eq 0 ]; then CMD='kinit -R && aklog && klist | grep -A1 krbtgt | tr -s " " | head -2'; else CMD='true'; fi
  if ssh -o BatchMode=yes -o ConnectTimeout=30 -o ControlPath=$CP $H "$CMD" >> "$LOG" 2>&1; then
    [ $((n % 72)) -eq 0 ] && echo "$(date -u +%FT%TZ) ping $n ok, ticket renewed" >> "$LOG"
  else
    echo "$(date -u +%FT%TZ) master connection lost; keepalive stopped (log in again to restore access)" >> "$LOG"; exit 1
  fi
  n=$((n+1)); sleep 300
done
echo "$(date -u +%FT%TZ) $HOURS h reached; keepalive ended (the session now closes after 10 h without use)" >> "$LOG"
