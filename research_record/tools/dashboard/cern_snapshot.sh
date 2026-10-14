#!/bin/bash
# WSL runner: ship cern_snapshot.py as a base64 ARGUMENT (ssh stdin stays /dev/null), print JSON lines to stdout.
# exit 9 = no SSH master (nothing touched on CERN). Uses ONLY the existing ControlMaster: ProxyCommand=/bin/false makes
# ssh fail instead of opening a new connection if the master disappears between the check and the call.
H=melrashe@lxplus.cern.ch
CP=$HOME/.ssh/cm-cern
PY="$(dirname "$0")/cern_snapshot.py"
timeout 15 ssh -O check -o BatchMode=yes -o ControlPath="$CP" $H </dev/null >/dev/null 2>&1 || { echo '{"k":"error","error":"NO_SSH_MASTER"}'; exit 9; }
B64=$(base64 -w0 "$PY")
timeout 40 ssh -o BatchMode=yes -o ControlPath="$CP" -o ControlMaster=no -o ProxyCommand=/bin/false -o ConnectTimeout=10 \
  -o GSSAPIAuthentication=no -o PubkeyAuthentication=no -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no \
  $H "echo $B64 | base64 -d | timeout 30 python3 -" </dev/null
