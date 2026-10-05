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
#    (jobs defined with 0 GPUs in make_jobs.py stay on CPUs)
#    large  (>= 90 atoms, slabs)   1 GPU (8 CPUs) on H100 NVL / H200 if one is free, else 32 CPUs if >= 3 such slots,
#                                  else 16 CPUs          [GPU measured 8.2x faster than 16 CPUs, 2026-09-28]
#    medium (< 90 atoms, >= 8 k)   32 CPUs if >= 3 free 32-CPU slots, else 16 CPUs
#    small                         16 CPUs
#    memory = 2 GB per CPU (min 32 GB); GPU jobs 64 GB; 32+ CPU jobs go to CERN's 10-slot bigmcore pool
#  NO-IDLE RULES (2026-09-30)
#    CPU twin      every 1-GPU job is also queued on 16 CPUs (JOB__cpu); the first copy to run wins, the others
#                  are removed (also for multi-GPU copies JOB_x2 / JOB_x4)
#    stuck start   running > 60 min in an SCF step without one SCF iteration -> removed and resubmitted (max 2x)
#    continuation  a relaxation that ends unfinished (time limit, eviction, checkpoint) is resubmitted from its
#                  last geometry as JOB_cN (max 5)
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
    if [ $((n % 72)) -eq 0 ]; then
      log "keepalive: ticket renewed" >> "$LOGF"
      # the ticket can be renewed only until its 'renew until' date; warn 24 h ahead (a new login is then needed)
      local ru; ru=$($S "klist 2>/dev/null | grep -A1 krbtgt | grep -o 'renew until.*' | cut -d' ' -f3,4")
      if [ -n "$ru" ] && [ $(( $(date -d "$ru" +%s 2>/dev/null || echo 0) - $(date +%s) )) -lt 86400 ]; then
        event "LOGIN NEEDED within 24 h: CERN ticket renewable only until $ru (run: ./dft_flow.sh login)"; fi
    fi
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
o=$(ls -t *.out 2>/dev/null | grep -vE '^(pp_|avg_|projwfc_)' | head -1); [ -n "$o" ] || o=NA.out   # no output yet -> step NA
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
      it=${it//[^0-9]/}; bf=${bf//[^0-9]/}; kp=${kp//[^0-9]/}   # strict JSON numbers (a 'NaN' BFGS count broke parsers)
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
        && event "RESULT $j fetched ($(tail -1 "$RES/$j/${j}_driver.log" 2>/dev/null | cut -c1-80))" && continue_job "$j" "$RES/$j"
    done
  done
  for f in $($S "ls $CKPT 2>/dev/null"); do          # checkpoints of jobs that died without final results
    local j=${f%_*}
    echo "$Q" | grep -qx "$j" && continue; [ -e "$RES/$j/.fetched" ] && continue; [ -e "$RES/${j}_checkpoint/$f" ] && continue
    mkdir -p "$RES/${j}_checkpoint"
    scp -q -o BatchMode=yes -o ControlPath=$CP "$H:$CKPT/$f" "$RES/${j}_checkpoint/" && tar xzf "$RES/${j}_checkpoint/$f" -C "$RES/${j}_checkpoint" \
      && event "CHECKPOINT $j (job ended without final results)" && continue_job "$j" "$RES/${j}_checkpoint"
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
  local atoms=$1 nk=$2 r=$3 down=${4:-0} gpu_ok=${5:-1}   # gpu_ok=0: job defined CPU-only in make_jobs.py
  [ "$gpu_ok" = 0 ] && r=$(echo "$r" | sed 's/"fast_gpus_free":[0-9]*/"fast_gpus_free":0/')
  local fast s32; fast=$(echo "$r" | grep -o '"fast_gpus_free":[0-9]*' | cut -d: -f2); s32=$(echo "$r" | grep -o '"slots_32c":[0-9]*' | cut -d: -f2)
  local opts=()
  # GPU jobs ask for 8 CPUs / 32 GB: a 16-CPU/64-GB GPU request waited > 3 h with 49 fast GPUs "free" (2026-09-29)
  # CPU jobs: 16 CPUs (normal pool). Requests of >= 32 CPUs go to CERN's 10-slot 'bigmcore' group and waited
  # 6 h on 2026-09-27, so 32 CPUs are used only for medium jobs when > 20 such slots are free
  if [ "$atoms" -ge 90 ]; then [ "${fast:-0}" -ge 1 ] && opts+=("8 32000 1"); opts+=("16 32000 0")
  elif [ "$nk" -ge 8 ]; then [ "${s32:-0}" -gt 20 ] && opts+=("32 64000 0"); opts+=("16 32000 0")
  else opts+=("16 32000 0"); fi
  local i=$(( down < ${#opts[@]} ? down : ${#opts[@]} - 1 )); echo "${opts[$i]}"
}

plan_jobs() {   # plan_jobs GEN ONLY RES_JSON -> lines "job cpus mem disk flavour limit gpus"
  local g="$JOBS/gen_$1" only=$2 r=$3
  while read -r j cpu mem disk flav limit gpus; do
    [ -n "$j" ] || continue
    [ -n "$only" ] && ! echo ",$only," | grep -q ",$j," && continue
    local atoms nk; read -r atoms nk <<< "$(python3 -c "import json,sys;d=[x for x in json.load(open(sys.argv[1])) if x['job']==sys.argv[2]][0];k=d['irreducible_k'];print(d['n_atoms'],k if isinstance(k,int) else max(k.values()))" "$g/jobs_info.json" "$j" 2>/dev/null || echo "0 0")"
    # FORCE_GPU=1: jobs defined with GPUs keep 1 GPU + 8 CPUs even if no fast GPU is free right now (upgrade copies)
    # memory: the value in jobs.txt is a floor (2 nm slab: the final SCF needed 66 GB and a 32 GB job was held, 2026-10-02)
    if [ -n "${FORCE_GPU:-}" ] && [ "${gpus:-0}" -ge 1 ]; then local fm=$((32000 * gpus)); [ "${mem:-0}" -gt "$fm" ] && fm=$mem
      echo "$j $((8 * gpus)) $fm $disk $flav $limit $gpus"; continue; fi
    # canary_* (fault-injection tests of the workflow rules): tiny fixed sizes, GPU if the job asks for one
    if [[ "$j" == canary_* ]]; then echo "$j 2 4000 $disk $flav $limit ${gpus:-0}"; continue; fi
    # multi-GPU jobs (gpus >= 2 in jobs.txt) keep their own size: 8 CPUs and 32 GB per GPU
    if [ "${gpus:-0}" -ge 2 ]; then echo "$j $((8 * gpus)) $((32000 * gpus)) $disk $flav $limit $gpus"; continue; fi
    local down=0; [ -f "$g/.downgrade_$j" ] && down=$(cat "$g/.downgrade_$j")
    read -r c m gp <<< "$(allocate "${atoms:-0}" "${nk:-0}" "$r" "$down" "$([ "${gpus:-0}" -gt 0 ] && echo 1 || echo 0)")"
    [ "${mem:-0}" -gt "$m" ] && m=$mem
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
  local Q r; Q=$(queue | awk '{print $3}'); r=$(cmd_resources); local keep=() twins=()
  while read -r line; do
    local j=${line%% *}
    if echo "$Q" | grep -qx "$j"; then log "skip $j: already queued"; continue; fi
    if [ -e "$RES/$j/.fetched" ]; then log "skip $j: already finished"; continue; fi
    keep+=("$line"); log "allocate $j: $(echo "$line" | awk '{print $2" CPUs, "$3" MB, "$7" GPU"}')"
    # CPU twin (TWIN=0 disables): a single-GPU job is also queued on 16 CPUs; the watchdog keeps whichever starts first
    if [ "${TWIN:-1}" = 1 ] && [ "$(echo "$line" | awk '{print $7}')" = 1 ] && [[ "$j" != *__cpu ]]; then
      local tc=16 tm=32000; [[ "$j" == canary_* ]] && { tc=2; tm=4000; }
      keep+=("$(echo "$line" | awk -v c=$tc -v m=$tm '{$1=$1"__cpu"; $2=c; $3=m; $7=0; print}')"); twins+=("$j"); log "  + CPU twin ${j}__cpu ($tc CPUs)"
    fi
  done < <(plan_jobs "$name" "$only" "$r")
  [ ${#keep[@]} -gt 0 ] || { log "nothing to submit"; return 0; }
  [ -n "${DRY:-}" ] && { log "DRY: would submit $(printf '%s; ' "${keep[@]}")"; return 0; }
  local stamp rdir tmp; stamp=$(date -u +%Y%m%d_%H%M%S); rdir="qe_jobs_${name}_$stamp"; tmp=$(mktemp -d)
  cp -r "$g"/. "$tmp"/; printf '%s\n' "${keep[@]}" > "$tmp/jobs.txt"
  for t in "${twins[@]}"; do cp -r "$tmp/$t" "$tmp/${t}__cpu"; done
  $S "mkdir -p $CKPT"
  bash <(lf "$CH/cern_submit.sh") "$tmp" "$rdir" && echo "$rdir" >> "$DIRS_FILE" && echo "$name" > "$CH/.gen_of_$rdir"
  cp "$tmp/cluster.txt" "$g/cluster_$stamp.txt" 2>/dev/null; rm -rf "$tmp"
}

cmd_cancel() { need_master; $S "condor_rm -constraint 'IWOJob == \"$1\"'"; }

# ---------------------------------------------------------------------------------------- automation
gen_of_job() { for g in "$JOBS"/gen_*/jobs.txt; do lf "$g" | awk '{print $1}' | grep -qx "$1" && basename "$(dirname "$g")" | sed 's/^gen_//'; done | tail -1; }

# continue_job JOB RESULT_DIR: a relaxation that ended unfinished (time limit, eviction, checkpoint only) is
# resubmitted from its last geometry as JOB_cN (same allocation rules)
continue_job() {
  local job=$1 rd=$2 base=${1%%__*} n=1
  [[ "$base" =~ _c([0-9]+)$ ]] && { n=$(( BASH_REMATCH[1] + 1 )); base=${base%_c[0-9]*}; }   # JOB_cK -> JOB_c(K+1)
  local gen; gen=$(gen_of_job "$job"); [ -n "$gen" ] || return 0
  local out; out=$(ls "$rd"/vcrelax.out "$rd"/relax.out 2>/dev/null | head -1); [ -n "$out" ] || return 0
  grep -q 'End final coordinates' "$out" && return 0
  grep -q 'ATOMIC_POSITIONS' "$out" || return 0
  [ "$n" -le 5 ] || { event "CONTINUE $job: 5 continuations reached, stopping"; return 0; }
  local gen0=${gen%_c[0-9]*}
  local ng="$JOBS/gen_${gen0}_c$n" nj="${base}_c$n" src="$JOBS/gen_$gen/$job"; [ -d "$src" ] || src="$JOBS/gen_$gen/${job%%__*}"
  [ -d "$ng" ] && rm -rf "$ng"
  mkdir -p "$ng"; cp -r "$src" "$ng/$nj"; cp "$JOBS/gen_$gen"/{qeio.py,jobs.sub} "$ng/"; cp -r "$JOBS/gen_$gen/pseudo" "$ng/"
  lf "$JOBS/common/driver.sh" > "$ng/driver.sh"
  local inp; inp=$(basename "$out" .out).in
  cp "$ng/$nj/$inp" "$ng/$nj/${inp%.in}_prev.in"
  python3 "$ng/qeio.py" newgeom "$ng/$nj/${inp%.in}_prev.in" "$out" > "$ng/$nj/$inp" || { event "CONTINUE $job failed (newgeom)"; return 0; }
  lf "$JOBS/gen_$gen/jobs.txt" | awk -v j="${job%%__*}" -v n="$nj" '$1==j{$1=n; print}' > "$ng/jobs.txt"
  sed "s/\"job\": \"${job%%__*}\"/\"job\": \"$nj\"/" "$JOBS/gen_$gen/jobs_info.json" > "$ng/jobs_info.json"
  cmd_submit "${gen0}_c$n" > /dev/null 2>&1 && event "CONTINUE $job unfinished -> $nj submitted from its last geometry ($(grep -c '^!' "$out") SCF cycles done)"
}

# submit_twin GEN JOB: queue a 16-CPU copy JOB__cpu of an idle GPU job (the GPU job stays queued)
submit_twin() {
  local g="$JOBS/gen_$1" j=$2 tmp stamp rdir; tmp=$(mktemp -d); stamp=$(date -u +%Y%m%d_%H%M%S); rdir="qe_jobs_$1_twin_$stamp"
  cp -r "$g"/. "$tmp"/; cp -r "$g/$j" "$tmp/${j}__cpu"
  lf "$g/jobs.txt" | awk -v j="$j" '$1==j{$1=$1"__cpu"; $2=16; $3=32000; $7=0; print}' > "$tmp/jobs.txt"
  lf "$JOBS/common/driver.sh" > "$tmp/driver.sh"
  bash <(lf "$CH/cern_submit.sh") "$tmp" "$rdir" > /dev/null 2>&1 && echo "$rdir" >> "$DIRS_FILE"; rm -rf "$tmp"
}

# group_done GROUP: a member has final results (not an unfinished relaxation)
group_done() {
  local d; for d in "$RES"/*/; do
    [ -e "$d.fetched" ] && [ "$(group_of "$(basename "$d")")" = "$1" ] || continue
    # only clean runs count as final: every pw.x step ended rc=0 (a failed run's tarball once removed its own
    # resubmission, 2026-09-30)
    grep -qE 'end rc=[1-9]' "$d"*_driver.log 2>/dev/null && continue
    local out; out=$(ls "$d"vcrelax.out "$d"relax.out 2>/dev/null | head -1)
    { [ -z "$out" ] || grep -q 'End final coordinates' "$out"; } && return 0
  done; return 1
}

# group_of NAME: race variants share a group: X__cpu (CPU twin), X_x2 / X_x4 (multi-GPU copies), X_gpu8 / X_gpu1
# (earlier GPU variants) and continuations X_cN -> X
group_of() { local b=${1%%__*}; b=${b%_checkpoint}; b=${b%_c[0-9]}; b=${b%_x[0-9]}; b=${b%_gpu[0-9]}; echo "$b"; }

# chains (cern_htcondor/chains.txt, one per line: GROUP|command): the command runs once, as soon as a finished
# relaxation of GROUP (any variant) has been fetched with "End final coordinates"; $OUT = that vc-relax/relax output
run_chains() {
  local cf="$CH/chains.txt"; [ -f "$cf" ] || return 0
  while IFS='|' read -r grp cmd <&3; do
    [ -n "$grp" ] && [ "${grp:0:1}" != "#" ] || continue
    local mark="$CH/.chain_done_$(echo "$grp$cmd" | md5sum | cut -c1-10)"; [ -e "$mark" ] && continue
    for d in "$RES"/*/; do
      local j; j=$(basename "$d"); [ "$(group_of "$j")" = "$grp" ] || continue
      local out; out=$(ls "$d"vcrelax.out "$d"relax.out 2>/dev/null | head -1)
      [ -n "$out" ] && grep -q 'End final coordinates' "$out" || continue
      touch "$mark"
      if [ -n "${DRY:-}" ]; then log "DRY chain $grp: OUT=$out; $cmd"; else
        (cd "$HERE" && OUT="$out" bash -c "$cmd") > "$CH/chain_$grp.log" 2>&1 && event "CHAIN $grp done: $cmd" || event "CHAIN $grp FAILED (see chain_$grp.log)"; fi
      break
    done
  done 3< <(lf "$cf")
}

watchdog() {   # held -> 1.5x memory; idle > 3 h -> smaller allocation; stuck at start -> resubmit; race groups
  local now; now=$(date +%s)
  # race groups. rank: GPU copy 1, CPU copy 0. A running copy removes idle copies of equal or lower rank; a GPU
  # copy that starts removes running CPU copies (upgrade: GPU measured ~8x faster); a group with final results
  # removes all its remaining copies
  local Q; Q=$(queue); declare -A best=() cpug=()
  # groups that already have a CPU copy (queued or running): no CPU twin is added for them
  while read -r cl pr job st cpu gpu rest; do [ -n "$cl" ] && [ "${gpu:-0}" = 0 ] && cpug[$(group_of "$job")]=1; done <<< "$Q"
  while read -r cl pr job st cpu gpu rest; do
    [ "$st" = 2 ] || continue; local g r; g=$(group_of "$job"); r=$([ "${gpu:-0}" -gt 0 ] 2>/dev/null && echo 1 || echo 0)
    [ -z "${best[$g]:-}" ] || [ "$r" -gt "${best[$g]}" ] && best[$g]=$r
  done <<< "$Q"
  # loops that call ssh read their lines from fd 3: ssh reads stdin and would swallow the remaining lines
  while read -r cl pr job st cpu gpu rest <&3; do
    [ -n "$cl" ] || continue; local g r; g=$(group_of "$job"); r=$([ "${gpu:-0}" -gt 0 ] 2>/dev/null && echo 1 || echo 0)
    if group_done "$g"; then $S "condor_rm $cl.$pr" > /dev/null && event "RACE $job removed ($g already has final results)"
    elif [ -n "${best[$g]:-}" ] && [ "$st" = 1 ] && [ "$r" -le "${best[$g]}" ]; then $S "condor_rm $cl.$pr" > /dev/null && event "RACE $job removed (a copy of $g runs)"
    elif [ -n "${best[$g]:-}" ] && [ "$st" = 2 ] && [ "$r" -lt "${best[$g]}" ]; then $S "condor_rm $cl.$pr" > /dev/null && event "UPGRADE $job (CPU) removed: a GPU copy of $g runs"; fi
  done 3<<< "$Q"
  # stuck at start: running > 60 min in an SCF-type step without a single SCF iteration (or without output).
  # 2026-10-05: one status sample with scf_it = 0 removed iwo_slab2_W24d, which was at SCF iteration 86 after 20 h of
  # running (a transient read of 0). A job now counts as stuck only after 3 consecutive cycles with that reading;
  # the counter of a job that is no longer a candidate is reset.
  local cand; cand=$(python3 -c "
import json,time
for j in json.load(open('$RES/status.json'))['jobs']:
    if j['state']==2 and j['scf_it']==0 and j['step'] in ('NA','relax','vcrelax','scf','scf_k4','spin_k3') and time.time()-j.get('since',time.time())>3600:
        print(j['job'], j['id'])" 2>/dev/null)
  for f in "$CH"/.stuckseen_*; do [ -e "$f" ] || continue; echo "$cand" | awk '{print $1}' | grep -qx "${f##*/.stuckseen_}" || rm -f "$f"; done
  while read -r job id <&3; do
    [ -n "$job" ] || continue
    local sf="$CH/.stuckseen_$job" n=0; [ -f "$sf" ] && n=$(cat "$sf"); n=$((n + 1)); echo "$n" > "$sf"
    [ "$n" -ge 3 ] || continue; rm -f "$sf"
    local f="$CH/.stuck_$job" k=0; [ -f "$f" ] && k=$(cat "$f"); [ "$k" -ge 2 ] && continue; echo $((k + 1)) > "$f"
    local gen; gen=$(gen_of_job "$job")
    $S "condor_rm $id" > /dev/null && [ -n "$gen" ] && cmd_submit "$gen" "$job" > /dev/null 2>&1 && event "STUCK $job (no SCF iteration in 3 consecutive checks after 60 min running) -> removed and resubmitted"
  done 3<<< "$cand"
  while read -r cl pr job st cpu gpu since hold <&3; do
    [ -n "$cl" ] || continue
    local gen; gen=$(gen_of_job "$job")
    if [ "$st" = 5 ]; then
      if [ "$hold" = 34 ] || $S "condor_q $cl.$pr -af HoldReason" | grep -qi memory; then
        # a release restarts the job from its first step: only jobs that ran < 1 h are released with 1.5x memory;
        # longer runs stay held for a resubmission from their checkpoint (slab2_relax_x1 lost 68 BFGS steps, 2026-10-02)
        local m wt; read -r m wt <<< "$($S "condor_q $cl.$pr -af RequestMemory RemoteWallClockTime")"; m=$(( m * 3 / 2 ))
        if [ "${wt%.*}" -lt 3600 ] 2>/dev/null; then
          $S "condor_qedit $cl.$pr RequestMemory $m && condor_release $cl.$pr" > /dev/null && event "HELD(memory) $job -> RequestMemory $m MB, released"
        elif [ ! -e "$CH/.heldnote_$cl.$pr" ]; then touch "$CH/.heldnote_$cl.$pr"
          event "HELD(memory) $job after ${wt%.*} s of running: NOT released (a release would restart it from the beginning); resubmit from its checkpoint with more memory"; fi
      else event "HELD $job: $($S "condor_q $cl.$pr -af HoldReason" | cut -c1-120)"; fi
    elif [ "$st" = 1 ] && [ -n "$gen" ] && [ "${gpu:-0}" -gt 0 ] 2>/dev/null && [ $(( now - ${since:-now} )) -gt 10800 ]; then
      # idle GPU job: keep it queued and add a CPU twin (if the group has none); the race/upgrade rules decide later
      # only if no CPU copy of the group is queued or running already (else the race rule removes it and it churns)
      # (no ssh inside this loop: ssh would consume the loop's here-string input)
      if [ -z "${cpug[$(group_of "$job")]:-}" ]; then
        submit_twin "$gen" "$job" && event "IDLE>3h $job (GPU) -> CPU twin ${job}__cpu added; GPU copy stays queued"; fi
    elif [ "$st" = 1 ] && [ -n "$gen" ] && [ $(( now - ${since:-now} )) -gt 10800 ]; then
      local f="$JOBS/gen_$gen/.downgrade_$job" d=0; [ -f "$f" ] && d=$(cat "$f"); echo $(( d + 1 )) > "$f"
      $S "condor_rm $cl.$pr" > /dev/null && cmd_submit "$gen" "$job" > /dev/null 2>&1 && event "IDLE>3h $job -> resubmitted with a smaller allocation (level $((d + 1)))"
    fi
  done 3<<< "$Q"
}

cmd_auto() {
  local min=${1:-10} notify=${2:-}; declare -A last=() lastt=() warned=()
  while true; do
    EV=""
    if ! alive; then event "SSH session lost; jobs keep running at CERN; log in again"; [ -n "$notify" ] && exit 3; sleep $(( min * 60 )); continue; fi
    cmd_status --json > "$RES/status.json.tmp" && mv "$RES/status.json.tmp" "$RES/status.json"
    lf "$RES/status.json" >> "$RES/status_history.jsonl"
    cmd_resources > "$RES/resources.json.tmp" 2>/dev/null && mv "$RES/resources.json.tmp" "$RES/resources.json" \
      && lf "$RES/resources.json" >> "$RES/resources_history.jsonl"   # free CPU/GPU history (best submission hours)
    # stalled jobs: SCF count unchanged for more than 30 min while running an SCF step (reported once)
    local now; now=$(date +%s)
    while read -r job it step; do
      if [ "${last[$job]:-}" != "$it" ]; then last[$job]=$it; lastt[$job]=$now; warned[$job]=""; continue; fi
      [ "$it" -gt 0 ] && [ -z "${warned[$job]}" ] && [ $(( now - ${lastt[$job]} )) -gt 1800 ] && { event "STALLED $job ($step, $it iterations, no progress for 30 min)"; warned[$job]=1; }
    done < <(python3 -c "import json;[print(j['job'],j['scf_it'],j['step']) for j in json.load(open('$RES/status.json'))['jobs'] if j['state']==2]" 2>/dev/null)
    cmd_fetch; watchdog; run_chains; cmd_analyze
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
