#!/bin/bash
# Codex periodic monitor (WSL). Every INTERVAL s (default 4 h): build a status digest of the ATLAS C10 campaign and the CERN
# DFT jobs. Send it to the Codex work chat (tools/codex_advise.sh) only if it changed since the last send.
# Stops on a Codex STOP verdict (exit 5), after N cycles, or after 21 Oct 2026. Log: codex/work_chat/autodigest.log.
# CERN status is read only through an existing SSH master; the loop never logs in.
ROOT="/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff (1)"; PUB="$ROOT/IWO_PHYSICS_CONSTRAINED_MODEL_V1"
CHAT="$ROOT/iwo-tft-research-private/codex/work_chat"; ALOG="$CHAT/autodigest.log"
INTERVAL=${INTERVAL:-14400}; N=${N:-30}
H=melrashe@lxplus.cern.ch; CP="-o BatchMode=yes -o ControlPath=$HOME/.ssh/cm-cern"
for i in $(seq 1 "$N"); do
  sleep "$INTERVAL"
  [ "$(date +%Y%m%d)" -gt 20261021 ] && { echo "$(date +%F) past 21 Oct, stop" >> "$ALOG"; exit 0; }
  D=$(mktemp)
  { echo "# Periodic monitor digest (automatic, $(date -u +%FT%H:%MZ))"; echo
    echo "## ATLAS C10 campaign"
    python3 - "$PUB/results/campaigns" <<'PY'
import glob, json, os, sys
rows = []
for f in sorted(glob.glob(sys.argv[1] + '/campaign_C10_*.json'), key=os.path.getmtime):
    try: d = json.load(open(f))
    except Exception: continue
    sealed = 'DIAG' in os.path.basename(f)   # S2 diagnostics stay sealed until the resolution method is frozen (Codex 2026-10-12)
    for r in d.get('runs', []):
        if sealed:
            rows.append((os.path.basename(f)[:-5], r.get('id'), r.get('run_id'), r.get('status'), 'SEALED', 'SEALED', (r.get('error') or '')[:90]))
        else:
            rows.append((os.path.basename(f)[:-5], r.get('id'), r.get('run_id'), r.get('status'), r.get('active_rmse_dec'), r.get('Id3V_err_pct'), (r.get('error') or '')[:90]))
print(f'{len(rows)} plan entries recorded (latest 15):')
for x in rows[-15:]:
    print('-', ' | '.join(f'{v:.4g}' if isinstance(v, float) else str(v) for v in x))
PY
    echo; echo "## CERN DFT"
    if ssh -O check $CP $H >/dev/null 2>&1; then
      ssh $CP $H 'cd ~/iwo_amorph; condor_q -af:j JobBatchName Cmd JobStatus 2>/dev/null | grep -v dagman | awk "{n=split(\$3,a,\"/\"); print \$2, a[n], (\$4==2?\"RUN\":(\$4==1?\"idle\":(\$4==5?\"HELD\":\$4)))}" | sort | uniq -c
        for d in runs/*/; do n=$(basename $d); st=$(cat $d/RELAX_STATUS 2>/dev/null); seg=$(ls $d/relax_s*_results.tar.gz 2>/dev/null | wc -l); fin=$([ -s $d/final_results.tar.gz ] && echo FINAL_DONE); echo "$n segments=$seg last=${st:-none} $fin"; done
        echo "force-check outputs: $(ls val/*.tar.gz 2>/dev/null | wc -l)"' </dev/null
    else echo "CERN not reachable from this laptop (no SSH master), so there is no CERN status this cycle."; fi
  } > "$D"
  h=$(grep -v '^# Periodic' "$D" | md5sum | cut -c1-32)
  if [ "$h" = "$(cat "$CHAT/.last_digest_hash" 2>/dev/null)" ]; then echo "$(date '+%F %H:%M') no change, not sent" >> "$ALOG"; rm -f "$D"; continue; fi
  R=$(flock "$CHAT/.lock" bash "$ROOT/iwo-tft-research-private/tools/codex_advise.sh" "Periodic monitor $(date -u +%FT%H:%MZ)" "$D" 2>&1); rc=$?
  if [ $rc -ne 0 ]; then   # not sent (e.g. session open interactively): keep the old hash so the next cycle retries
    echo "$(date '+%F %H:%M') NOT sent (rc $rc): $(echo "$R" | tail -1 | cut -c1-160)" >> "$ALOG"; rm -f "$D"; continue; fi
  echo "$h" > "$CHAT/.last_digest_hash"
  V=$(echo "$R" | grep -m1 -i 'verdict' | cut -c1-160)
  echo "$(date '+%F %H:%M') sent; $V" >> "$ALOG"; rm -f "$D"
  if echo "$V" | grep -q 'STOP'; then echo "$R"; echo "CODEX VERDICT: STOP"; exit 5; fi
done
