#!/bin/bash
# Fault-injection ("canary") test of the dft_flow.sh rules on CERN with tiny toy W jobs (2 CPUs, 4 GB).
# Run in distro Ubuntu from qe_workflow:  bash cern_htcondor/canary.sh
#   canary_cont   toy slab vc-relax limited to 3 BFGS steps per job -> rule "continuation" (canary_cont_c1, _c2 ...)
#                 and, when a continuation finishes the relaxation, rule "chain" (marker file)
#   canary_stuck  job that only sleeps 75 min (no pw.x output)        -> rule "stuck at start" (resubmitted, max 2)
#   canary_race   toy relax asking for 1 GPU                           -> rule "CPU twin / race" (canary_race__cpu)
#   canary_ckpt   toy relax, then sleeps; removed here after its EOS checkpoint appears -> rule "checkpoint fetch"
set -uo pipefail
W="$(cd "$(dirname "$0")/.." && pwd)"; J="$W/cern_htcondor/jobs"; G="$J/gen_canary"
S="ssh -o BatchMode=yes -o ControlPath=$HOME/.ssh/cm-cern melrashe@lxplus.cern.ch"
log() { echo "[$(date -u +%FT%TZ)] $*"; }
rm -rf "$G" "$J/gen_canary_toy"
wsl.exe -d Ubuntu-22.04 --cd "$J" -e /home/mahmoud/miniforge3/envs/qe/bin/python make_jobs.py --toy gen_canary_toy > /dev/null || exit 1
mkdir -p "$G"; cp "$J/gen_canary_toy"/{qeio.py,jobs.sub} "$G/"; cp -r "$J/gen_canary_toy/pseudo" "$G/"; sed 's/\r$//' "$J/common/driver.sh" > "$G/driver.sh"
cp -r "$J/gen_canary_toy/toy_slab" "$G/canary_cont"; sed -i 's/nstep = 300/nstep = 3/' "$G/canary_cont/vcrelax.in"
mkdir -p "$G/canary_stuck"; printf 'steps() {\n  sleep 4500\n}\n' > "$G/canary_stuck/steps.sh"
for n in canary_race canary_ckpt; do mkdir -p "$G/$n"; cp "$J/gen_canary_toy/toy_bulk/relax.in" "$G/$n/"; done
printf 'steps() {\n  run_pw relax 1\n}\n' > "$G/canary_race/steps.sh"
printf 'steps() {\n  run_pw relax 1\n  sleep 3000\n}\n' > "$G/canary_ckpt/steps.sh"
cat > "$G/jobs.txt" <<EOF
canary_cont 2 4000 2000000 longlunch 7200 0
canary_stuck 2 4000 2000000 longlunch 7200 0
canary_race 2 4000 2000000 longlunch 7200 1
canary_ckpt 2 4000 2000000 longlunch 7200 0
EOF
python3 -c "import json;print(json.dumps([{'job':j,'n_atoms':3,'irreducible_k':1} for j in ['canary_cont','canary_stuck','canary_race','canary_ckpt']]))" > "$G/jobs_info.json"
grep -q '^canary_cont|' "$W/cern_htcondor/chains.txt" || echo 'canary_cont|echo "chain fired for $OUT" > cern_htcondor/results/canary_chain_marker.txt' >> "$W/cern_htcondor/chains.txt"
rm -f "$W"/cern_htcondor/.stuck_canary_* "$W/cern_htcondor/results/canary_chain_marker.txt"
cd "$W" && bash ./dft_flow.sh submit canary || exit 1
# rule "checkpoint": remove canary_ckpt once its first checkpoint is on EOS
for i in $(seq 1 60); do
  if $S "ls /eos/user/m/melrashe/qe/checkpoints/ | grep -q '^canary_ckpt_'"; then
    $S "condor_rm -constraint 'IWOJob == \"canary_ckpt\"'" && log "canary_ckpt removed after its checkpoint appeared"; break; fi
  sleep 60
done
log "canaries submitted; dft_flow.sh auto reports each rule as it fires (events.log)"
