#!/bin/bash
# CERN chain 1 (user-approved 2026-09-27): install QE 7.5 into EOS via conda-pack, upload and submit the small
# HTCondor test job, wait for it and report. Uses the existing SSH master session only (no password).
set -u
CP=~/.ssh/cm-cern; H=melrashe@lxplus.cern.ch
S() { ssh -o BatchMode=yes -o ConnectTimeout=30 -o ControlPath=$CP $H "$@"; }
L="/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff (1)/IWO_PHYSICS_CONSTRAINED_MODEL_V1/qe_workflow/cern_htcondor"
echo "[0] $(date -u +%FT%TZ) session check"; S 'hostname' || { echo "SSH master not available"; exit 1; }
echo "[1] $(date -u +%FT%TZ) building QE environment and packing it to EOS"
if S 'test -s /eos/user/m/melrashe/qe/qe-7.5-env.tar.gz'; then echo "package already present"; else
  sed 's/\r$//' "$L/setup_qe_pack.sh" | S 'bash -s' > "$L/setup_qe_pack.log" 2>&1; echo "rc=$?"; tail -5 "$L/setup_qe_pack.log"; fi
S 'ls -lh /eos/user/m/melrashe/qe/qe-7.5-env.tar.gz' || { echo "PACKAGE MISSING - stopping before the test job"; exit 2; }
echo "[2] $(date -u +%FT%TZ) uploading the test job to ~/qe_test (AFS home)"
S 'mkdir -p ~/qe_test/logs'
for f in w_bcc.in run_qe_test.sh qe_test.sub W.pbe-spn-kjpaw_psl.1.0.0.UPF; do
  scp -q -o BatchMode=yes -o ControlPath=$CP "$L/qe_test/$f" "$H:qe_test/$f" || { echo "upload of $f failed"; exit 3; }; done
S 'cd ~/qe_test && sed -i "s/\r$//" run_qe_test.sh qe_test.sub w_bcc.in && chmod +x run_qe_test.sh && ls -l'
echo "[3] $(date -u +%FT%TZ) submitting"
S 'cd ~/qe_test && condor_submit qe_test.sub' | tee "$L/qe_test_submit.log"
CL=$(grep -oE 'cluster [0-9]+' "$L/qe_test_submit.log" | awk '{print $2}'); echo "cluster=$CL"
[ -n "$CL" ] || { echo "submission failed"; exit 4; }
echo "[4] $(date -u +%FT%TZ) waiting for the job (max 3 h)"
for i in $(seq 1 90); do
  st=$(S "condor_q $CL -af JobStatus 2>/dev/null"); [ -z "$st" ] && break
  [ "$st" = "5" ] && { echo "job HELD:"; S "condor_q $CL -af HoldReason"; break; }
  sleep 120; done
echo "[5] $(date -u +%FT%TZ) result"
S "cd ~/qe_test && tail -30 logs/qe_test.$CL.0.out; echo '--- stderr:'; tail -15 logs/qe_test.$CL.0.err; echo '--- pw.x output:'; grep -E '^!|convergence has been achieved|WALL|Parallel version|Number of MPI' w_bcc.out 2>/dev/null; condor_history $CL -limit 1 -af RemoteWallClockTime RequestCpus MemoryUsage ExitCode 2>/dev/null"
echo "CERN CHAIN1 DONE $(date -u +%FT%TZ)"
