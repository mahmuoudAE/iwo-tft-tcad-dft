#!/bin/bash
# =====================================================================================================
#  dft_flow.sh - the complete IWO / In2O3 DFT workflow in one file (CERN HTCondor + local)
# =====================================================================================================
#  Run in WSL, in the distro that holds your CERN SSH session ("Ubuntu"). QE and Python come from
#  ~/miniforge3/envs/qe (or from the "Ubuntu-22.04" distro automatically).
#
#  SESSION
#    login                  print the one-line CERN login (YOU type password + 2FA; never automated)
#    check                  is the CERN session alive?
#    keepalive [HOURS]      keep the session alive (ping 5 min, Kerberos/AFS renewal 6 h), default 96 h
#
#  BUILD AND SUBMIT
#    build [vc-relax.out]   build + verify all structures from the relaxed bulk
#    generate NAME [j1,j2]  write job folders jobs/gen_NAME (all jobs of make_jobs.py or a subset)
#    submit NAME [j1,j2]    AUTO-ALLOCATE and submit: CPU size or GPU chosen per job (see ALLOCATION);
#                           skips jobs already queued or finished
#    plan NAME [j1,j2]      show the allocation that submit would use, without submitting
#    resubmit-missing NAME  regenerate + submit the jobs that have neither results nor a queue entry
#    cancel JOB             remove a job from the queue by name
#
#  OBSERVE
#    resources              free CPU slots by size and free GPUs by model (JSON)
#    status [--json]        queue + live progress of every running job (step, SCF iterations, BFGS steps)
#    hw                     CPU and GPU model under every running job
#    fetch                  download finished results (and EOS checkpoints of jobs that died)
#    missing                jobs with neither results nor a queue entry
#    analyze                all results -> cern_htcondor/results/summary.json
#    dashboard [PORT]       live page http://localhost:PORT (default 8767)
#
#  AUTOMATION (real time)
#    auto [MIN] [--notify]  every MIN minutes (default 10): status, resources, fetch, analyze, and the
#                           WATCHDOG (see below); --notify exits on the first event (used by Claude)
#
#  LOCAL
#    local NAME JOB [NCPU]  run one generated job on this computer with the same driver
#
#  ALLOCATION (decided per job from its size in jobs_info.json and the free resources at that moment)
#    large  (>= 90 atoms, slabs)   1 GPU on H100 NVL / H200 if one is free, else 32 CPUs if >= 3 such slots,
#                                  else 16 CPUs          [GPU measured 8.2x faster than 16 CPUs, 2026-09-28]
#    medium (< 90 atoms, >= 8 k)   32 CPUs if >= 3 free 32-CPU slots, else 16 CPUs
#    small                         16 CPUs
#    memory = 2 GB per CPU (min 32 GB); GPU jobs 64 GB; 32+ CPU jobs go to CERN's 10-slot bigmcore pool
#  WATCHDOG (in auto)
#    held for memory  -> resubmitted with 1.5x memory      idle > 3 h -> resubmitted with the next smaller
#    no progress between two cycles -> reported as an event   allocation (GPU -> 32 CPU -> 16 CPU)
#    a finished result -> fetched + analysed + reported      SSH session lost -> reported, jobs keep running
# =====================================================================================================
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CH="$HERE/cern_htcondor"; JOBS="$CH/jobs"; RES="$CH/results"; STRUCT="$HERE/structures_v2"
H=${CERN_USER:-melrashe}@lxplus.cern.ch; CP=$HOME/.ssh/cm-cern
S="ssh -o BatchMode=yes -o ConnectTimeout=30 -o ControlPath=$CP $H"
DIRS_FILE="$CH/remote_dirs.txt"; CKPT=/eos/user/m/melrashe/qe/checkpoints
EVENTS="$CH/events.log"; LOGF="$CH/monitor.log"
if [ -x "$HOME/miniforge3/envs/qe/bin/python" ]; then QE=$HOME/miniforge3/envs/qe; inqe() { "$@"; }
else QE=/home/$(whoami)/miniforge3/envs/qe; inqe() { wsl.exe -d Ubuntu-22.04 --cd "$PWD" -e "$@"; }; fi
PY="$QE/bin/python"
mkdir -p "$RES"; touch "$DIRS_FILE"
log() { echo "[$(date -u +%FT%TZ)] $*"; }
event() { echo "$(date -u +%FT%TZ) $*" | tee -a "$EVENTS"; EV="${EV:-} $*"; }
alive() { ssh -O check -o ControlPath=$CP $H > /dev/null 2>&1; }
need_master() { alive || { log "no CERN session: run '$0 login' and log in yourself"; exit 2; }; }
lf() { sed 's/\r$//' "$1"; }

# ---------------------------------------------------------------------------------------- session
cmd_keepalive() {
  local end=$(( $(date +%s) + ${1:-96} * 3600 )) n=0
  while [ "$(date +%s)" -lt "$end" ]; do
    local c='true'; [ $((n % 72)) -eq 0 ] && c='kinit -R && aklog'
    $S "$c" > /dev/null 2>&1 || { event "SSH session lost (keepalive)"; exit 1; }
    [ $((n % 72)) -eq 0 ] && log "keepalive: ticket renewed" >> "$LOGF"
    n=$((n + 1)); sleep 300
  done
}

# ---------------------------------------------------------------------------------------- queries
queue() { $S "condor_q -af ClusterId ProcId IWOJob JobStatus RequestCpus RequestGPUs EnteredCurrentStatus HoldReasonCode 2>/dev/null" | awk 'NF>=5'; }

cmd_resources() {
  $S 'bash -s' <<'EOF'
cpu=$(timeout 120 condor_status -constraint 'PartitionableSlot =?= true' -af Cpus Memory 2>/dev/null |
  awk '{c+=$1; if($1>=16&&$2>=32000)b++; if($1>=32&&$2>=64000)d++; if($1>=64&&$2>=128000)e++}
       END{printf "\"free_cores\":%d,\"slots_16c\":%d,\"slots_32c\":%d,\"slots_64c\":%d", c, b, d, e}')
gpu=$(timeout 120 condor_status -constraint 'TotalGPUs > 0' -af:, Machine TotalGPUs GPUs GPUs_DeviceName 2>/dev/null |
  awk -F', ' '{m[$1]=1; tot+=$2; f=($3=="undefined"?0:$3); free+=f; name[$4]+=$2; fr[$4]+=f; if($4~/H100 NVL|H200/) fast+=f}
       END{printf "\"gpu_nodes\":%d,\"gpus_total\":%d,\"gpus_free\":%d,\"fast_gpus_free\":%d,\"gpu_models\":{", length(m), tot, free, fast;
           s=""; for(k in name){printf "%s\"%s\":[%d,%d]", s, k, name[k], fr[k]; s=","}; printf "}"}')
printf '{"time":"%s",%s,%s}\n' "$(date -u +%FT%TZ)" "$cpu" "$gpu"
EOF
}

peek() {   # CLUSTER.PROC -> "step it bfgs energy acc kpts"
  $S "timeout 90 condor_ssh_to_job $1 'bash -s'" 2>/dev/null <<'EOF' | tail -1
o=$(ls -t *.out 2>/dev/null | grep -vE '^(pp_|avg_|projwfc_)' | head -1)
it=$(grep -c 'iteration #' "$o" 2>/dev/null); b=$(grep 'number of bfgs steps' "$o" 2>/dev/null | tail -1 | awk '{print $NF}')
e=$(grep '^!' "$o" 2>/dev/null | tail -1 | awk '{print $5}'); a=$(grep 'estimated scf accuracy' "$o" 2>/dev/null | tail -1 | awk '{print $5}')
g=$(nvidia-smi --query-gpu=name,utilization.gpu --format=csv,noheader,nounits 2>/dev/null | awk -F', ' '{n=$1; u+=$2; c++} END{if(c) printf "%dx%s|%d%%", c, n, u/c}' | tr ' ' '_')
cpu=$(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2 | sed 's/^ *//' | tr ' ' '_')
echo "${o%.out} ${it:-0} ${b:-0} ${e:-NA} ${a:-NA} $(grep -c 'Computing kpt' "$o" 2>/dev/null) ${g:-none} ${cpu:-NA}"
EOF
}

cmd_status() {
  need_master; local Q; Q=$(queue)
  if [ "${1:-}" = "--json" ]; then
    local first=1; printf '{"time":"%s","jobs":[' "$(date -u +%FT%TZ)"
    while read -r cl pr job st cpu gpu since hold; do
      [ -n "$cl" ] || continue
      local step=NA it=0 bf=0 en=NA acc=NA kp=0 gm=none cm=NA
      [ "$st" = 2 ] && read -r step it bf en acc kp gm cm <<< "$(peek "$cl.$pr")"
      [ $first = 1 ] || printf ','; first=0
      printf '{"job":"%s","id":"%s.%s","state":%s,"cpus":%s,"gpus":"%s","step":"%s","scf_it":%s,"bfgs":%s,"energy":"%s","acc":"%s","kpts":%s,"since":%s,"gpu_hw":"%s","cpu_hw":"%s"}' \
        "$job" "$cl" "$pr" "$st" "$cpu" "$gpu" "${step:-NA}" "${it:-0}" "${bf:-0}" "${en:-NA}" "${acc:-NA}" "${kp:-0}" "${since:-0}" "${gm//_/ }" "${cm//_/ }"
    done <<< "$Q"
    printf '],"finished":['; first=1
    for d in "$RES"/*/; do [ -e "$d/.fetched" ] || continue; [ $first = 1 ] || printf ','; first=0; printf '"%s"' "$(basename "$d")"; done
    printf ']}\n'
  else
    printf '%-18s %-12s %-5s %-4s %-3s %-9s %6s %5s %s\n' JOB ID STATE CPUS GPU STEP SCF_IT BFGS LAST_ENERGY_Ry
    while read -r cl pr job st cpu gpu since hold; do
      [ -n "$cl" ] || continue
      local s=$st; case $st in 1) s=idle;; 2) s=run;; 5) s=HELD;; esac
      local step=- it=- bf=- en=- acc kp
      [ "$st" = 2 ] && read -r step it bf en acc kp <<< "$(peek "$cl.$pr")"
      printf '%-18s %-12s %-5s %-4s %-3s %-9s %6s %5s %s\n' "$job" "$cl.$pr" "$s" "$cpu" "$gpu" "$step" "$it" "$bf" "$en"
    done <<< "$Q"
  fi
}

cmd_hw() {
  need_master
  queue | while read -r cl pr job st rest; do
    [ "$st" = 2 ] || { echo "$job: not running"; continue; }
    $S "timeout 90 condor_ssh_to_job $cl.$pr 'bash -s'" 2>/dev/null <<EOF | tail -1
echo "$job | \$(hostname -s) | CPU: \$(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2 | sed 's/^ *//') x \$(nproc) | GPU: \$(nvidia-smi --query-gpu=name,utilization.gpu --format=csv,noheader 2>/dev/null | head -1)"
EOF
  done
}

# ---------------------------------------------------------------------------------------- results
cmd_fetch() {
  need_master; local Q; Q=$(queue | awk '{print $3}')
  for d in $(lf "$DIRS_FILE"); do
    for f in $($S "cd $d 2>/dev/null && ls *_results.tar.gz 2>/dev/null"); do
      local j=${f%_results.tar.gz}; [ -e "$RES/$j/.fetched" ] && continue
      mkdir -p "$RES/$j"
      scp -q -o BatchMode=yes -o ControlPath=$CP "$H:$d/$f" "$RES/$j/" && tar xzf "$RES/$j/$f" -C "$RES/$j" && touch "$RES/$j/.fetched" \
        && event "RESULT $j fetched ($(tail -1 "$RES/$j/${j}_driver.log" 2>/dev/null | cut -c1-80))"
    done
  done
  for f in $($S "ls $CKPT 2>/dev/null"); do          # checkpoints of jobs that died without final results
    local j=${f%_*}
    echo "$Q" | grep -qx "$j" && continue; [ -e "$RES/$j/.fetched" ] && continue; [ -e "$RES/${j}_checkpoint/$f" ] && continue
    mkdir -p "$RES/${j}_checkpoint"
    scp -q -o BatchMode=yes -o ControlPath=$CP "$H:$CKPT/$f" "$RES/${j}_checkpoint/" && tar xzf "$RES/${j}_checkpoint/$f" -C "$RES/${j}_checkpoint" \
      && event "CHECKPOINT $j (job ended without final results)"
  done
}

cmd_analyze() { (cd "$HERE" && inqe "$PY" collect_results.py) > /dev/null 2>&1 && log "summary.json updated"; }
all_jobs() { for g in "$JOBS"/gen_*/jobs.txt; do lf "$g" | awk '{print $1}'; done | sort -u; }
cmd_missing() {
  need_master; local Q; Q=$(queue | awk '{print $3}')
  for j in $(all_jobs); do [ -e "$RES/$j/.fetched" ] || echo "$Q" | grep -qx "$j" || echo "$j"; done
}

# ---------------------------------------------------------------------------------------- allocation
# allocate ATOMS NK RESOURCES_JSON [DOWNGRADE] -> "cpus mem_MB gpus"
allocate() {
  local atoms=$1 nk=$2 r=$3 down=${4:-0}
  local fast s32; fast=$(echo "$r" | grep -o '"fast_gpus_free":[0-9]*' | cut -d: -f2); s32=$(echo "$r" | grep -o '"slots_32c":[0-9]*' | cut -d: -f2)
  local opts=()
  if [ "$atoms" -ge 90 ]; then [ "${fast:-0}" -ge 1 ] && opts+=("16 64000 1"); [ "${s32:-0}" -ge 3 ] && opts+=("32 64000 0"); opts+=("16 32000 0")
  elif [ "$nk" -ge 8 ]; then [ "${s32:-0}" -ge 3 ] && opts+=("32 64000 0"); opts+=("16 32000 0")
  else opts+=("16 32000 0"); fi
  local i=$(( down < ${#opts[@]} ? down : ${#opts[@]} - 1 )); echo "${opts[$i]}"
}

plan_jobs() {   # plan_jobs GEN ONLY RES_JSON -> lines "job cpus mem disk flavour limit gpus"
  local g="$JOBS/gen_$1" only=$2 r=$3
  while read -r j cpu mem disk flav limit gpus; do
    [ -n "$j" ] || continue
    [ -n "$only" ] && ! echo ",$only," | grep -q ",$j," && continue
    local atoms nk; read -r atoms nk <<< "$(python3 -c "import json,sys;d=[x for x in json.load(open(sys.argv[1])) if x['job']==sys.argv[2]][0];k=d['irreducible_k'];print(d['n_atoms'],k if isinstance(k,int) else max(k.values()))" "$g/jobs_info.json" "$j" 2>/dev/null || echo "0 0")"
    local down=0; [ -f "$g/.downgrade_$j" ] && down=$(cat "$g/.downgrade_$j")
    read -r c m gp <<< "$(allocate "${atoms:-0}" "${nk:-0}" "$r" "$down")"
    echo "$j $c $m $disk $flav $limit $gp"
  done < <(lf "$g/jobs.txt")
}

cmd_plan() {
  need_master; local r; r=$(cmd_resources)
  echo "resources: $r" | cut -c1-200
  printf '%-18s %5s %7s %4s\n' JOB CPUS MEM_MB GPUS
  plan_jobs "$1" "${2:-}" "$r" | awk '{printf "%-18s %5s %7s %4s\n", $1, $2, $3, $7}'
}

cmd_generate() {
  (cd "$JOBS" && inqe "$PY" make_jobs.py ../../structures_v2/relaxed_pbe "gen_$1" ${2:-} > "gen_$1.log" 2>&1) \
    && log "generated jobs/gen_$1: $(lf "$JOBS/gen_$1/jobs.txt" | awk '{printf "%s ", $1}')" || { cat "$JOBS/gen_$1.log"; exit 1; }
}

cmd_submit() {
  need_master
  local name=$1 only=${2:-} g="$JOBS/gen_$1"
  [ -f "$g/jobs.txt" ] || { log "no $g/jobs.txt: run generate first"; exit 1; }
  local Q r; Q=$(queue | awk '{print $3}'); r=$(cmd_resources); local keep=()
  while read -r line; do
    local j=${line%% *}
    if echo "$Q" | grep -qx "$j"; then log "skip $j: already queued"; continue; fi
    if [ -e "$RES/$j/.fetched" ]; then log "skip $j: already finished"; continue; fi
    keep+=("$line"); log "allocate $j: $(echo "$line" | awk '{print $2" CPUs, "$3" MB, "$7" GPU"}')"
  done < <(plan_jobs "$name" "$only" "$r")
  [ ${#keep[@]} -gt 0 ] || { log "nothing to submit"; return 0; }
  local stamp rdir tmp; stamp=$(date -u +%Y%m%d_%H%M%S); rdir="qe_jobs_${name}_$stamp"; tmp=$(mktemp -d)
  cp -r "$g"/. "$tmp"/; printf '%s\n' "${keep[@]}" > "$tmp/jobs.txt"
  $S "mkdir -p $CKPT"
  bash <(lf "$CH/cern_submit.sh") "$tmp" "$rdir" && echo "$rdir" >> "$DIRS_FILE" && echo "$name" > "$CH/.gen_of_$rdir"
  cp "$tmp/cluster.txt" "$g/cluster_$stamp.txt" 2>/dev/null; rm -rf "$tmp"
}

cmd_cancel() { need_master; $S "condor_rm -constraint 'IWOJob == \"$1\"'"; }

# ---------------------------------------------------------------------------------------- automation
gen_of_job() { for g in "$JOBS"/gen_*/jobs.txt; do lf "$g" | awk '{print $1}' | grep -qx "$1" && basename "$(dirname "$g")" | sed 's/^gen_//'; done | tail -1; }

watchdog() {   # held for memory -> 1.5x memory; idle > 3 h -> next smaller allocation; stalled -> event
  local now; now=$(date +%s)
  while read -r cl pr job st cpu gpu since hold; do
    [ -n "$cl" ] || continue
    local gen; gen=$(gen_of_job "$job")
    if [ "$st" = 5 ]; then
      if [ "$hold" = 34 ] || $S "condor_q $cl.$pr -af HoldReason" | grep -qi memory; then
        local m; m=$($S "condor_q $cl.$pr -af RequestMemory"); m=$(( m * 3 / 2 ))
        $S "condor_qedit $cl.$pr RequestMemory $m && condor_release $cl.$pr" > /dev/null && event "HELD(memory) $job -> RequestMemory $m MB, released"
      else event "HELD $job: $($S "condor_q $cl.$pr -af HoldReason" | cut -c1-120)"; fi
    elif [ "$st" = 1 ] && [ -n "$gen" ] && [ $(( now - ${since:-now} )) -gt 10800 ]; then
      local f="$JOBS/gen_$gen/.downgrade_$job" d=0; [ -f "$f" ] && d=$(cat "$f"); echo $(( d + 1 )) > "$f"
      $S "condor_rm $cl.$pr" > /dev/null && cmd_submit "$gen" "$job" > /dev/null 2>&1 && event "IDLE>3h $job -> resubmitted with a smaller allocation (level $((d + 1)))"
    fi
  done <<< "$(queue)"
}

cmd_auto() {
  local min=${1:-10} notify=${2:-}; declare -A last=() lastt=() warned=()
  while true; do
    EV=""
    if ! alive; then event "SSH session lost; jobs keep running at CERN; log in again"; [ -n "$notify" ] && exit 3; sleep $(( min * 60 )); continue; fi
    cmd_status --json > "$RES/status.json.tmp" && mv "$RES/status.json.tmp" "$RES/status.json"
    lf "$RES/status.json" >> "$RES/status_history.jsonl"
    cmd_resources > "$RES/resources.json.tmp" 2>/dev/null && mv "$RES/resources.json.tmp" "$RES/resources.json"
    # stalled jobs: SCF count unchanged for more than 30 min while running an SCF step (reported once)
    local now; now=$(date +%s)
    while read -r job it step; do
      if [ "${last[$job]:-}" != "$it" ]; then last[$job]=$it; lastt[$job]=$now; warned[$job]=""; continue; fi
      [ "$it" -gt 0 ] && [ -z "${warned[$job]}" ] && [ $(( now - ${lastt[$job]} )) -gt 1800 ] && { event "STALLED $job ($step, $it iterations, no progress for 30 min)"; warned[$job]=1; }
    done < <(python3 -c "import json;[print(j['job'],j['scf_it'],j['step']) for j in json.load(open('$RES/status.json'))['jobs'] if j['state']==2]" 2>/dev/null)
    cmd_fetch; watchdog; cmd_analyze
    echo "$(date -u +%FT%TZ) cycle: $(python3 -c "import json;print(' '.join(f\"{j['job']}={({1:'idle',2:'run',5:'HELD'}).get(j['state'],j['state'])}/{j['scf_it']}\" for j in json.load(open('$RES/status.json'))['jobs']))" 2>/dev/null)" >> "$LOGF"
    [ -n "$notify" ] && [ -n "$EV" ] && { log "events:$EV"; exit 0; }
    sleep $(( min * 60 ))
  done
}

cmd_local() {
  local name=$1 job=$2 ncpu=${3:-8} g="$JOBS/gen_$1"; local w=$HOME/dft_local/$job
  rm -rf "$w"; mkdir -p "$w"; cp -r "$g/$job"/. "$g"/pseudo/. "$w"/; cp "$g/driver.sh" "$g/qeio.py" "$w"/
  local limit; limit=$(lf "$g/jobs.txt" | awk -v j="$job" '$1==j{print $6}')
  inqe bash -c "cd '$w' && QE_LOCAL='$QE' NCPU_OVERRIDE=$ncpu MPIOPT='--bind-to none --map-by :OVERSUBSCRIBE' bash driver.sh '$job' '${limit:-86400}'"
  mkdir -p "$HERE/results_local/$job"; tar xzf "$w/${job}_results.tar.gz" -C "$HERE/results_local/$job" && log "results in results_local/$job"
}

case "${1:-}" in
  login)  echo "Type this in an Ubuntu terminal (you enter password + 2FA yourself):"
          echo "ssh -fN -o ControlMaster=yes -o ControlPath=~/.ssh/cm-cern -o ControlPersist=yes -o ServerAliveInterval=60 -o ServerAliveCountMax=10 $H" ;;
  check)  ssh -O check -o ControlPath=$CP $H ;;
  keepalive) need_master; cmd_keepalive "${2:-96}" ;;
  build)  (cd "$STRUCT" && inqe "$PY" build_structures.py "${2:-../bulk_In2O3_protocol/vcrelax_ecut71_k3.out}" relaxed_pbe | tail -5) ;;
  generate) cmd_generate "${2:?name}" "${3:-}" ;;
  plan)   cmd_plan "${2:?name}" "${3:-}" ;;
  submit) cmd_submit "${2:?name}" "${3:-}" ;;
  resubmit-missing) m=$(cmd_missing | paste -sd, -); [ -n "$m" ] || { log "no missing jobs"; exit 0; }; cmd_generate "${2:?name}" "$m" && cmd_submit "$2" ;;
  cancel) cmd_cancel "${2:?job}" ;;
  resources) need_master; cmd_resources | tee "$RES/resources.json" ;;
  status) cmd_status "${2:-}" ;;
  hw)     cmd_hw ;;
  fetch)  cmd_fetch ;;
  missing) cmd_missing ;;
  analyze) cmd_analyze ;;
  auto|watch) cmd_auto "${2:-10}" "${3:-}" ;;
  dashboard) python3 "$HERE/dashboard_cern.py" "${2:-8767}" ;;
  local)  cmd_local "${2:?name}" "${3:?job}" "${4:-8}" ;;
  *) sed -n '2,52p' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
