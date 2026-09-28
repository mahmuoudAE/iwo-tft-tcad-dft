#!/bin/bash
# Free CPU slots by size and GPU nodes in the CERN HTCondor pool -> JSON on stdout (read-only queries).
# Usage (distro holding the SSH master): bash resources.sh > results/resources.json
S="ssh -o BatchMode=yes -o ConnectTimeout=30 -o ControlPath=$HOME/.ssh/cm-cern melrashe@lxplus.cern.ch"
$S 'bash -s' <<'EOF'
cpu=$(timeout 120 condor_status -constraint 'PartitionableSlot =?= true' -af Cpus Memory 2>/dev/null |
  awk '{c+=$1; if($1>=8&&$2>=16000)a++; if($1>=16&&$2>=32000)b++; if($1>=32&&$2>=64000)d++; if($1>=64&&$2>=128000)e++}
       END{printf "\"free_cores\":%d,\"slots_8c\":%d,\"slots_16c\":%d,\"slots_32c\":%d,\"slots_64c\":%d", c, a, b, d, e}')
gpu=$(timeout 120 condor_status -constraint 'TotalGPUs > 0' -af:, Machine TotalGPUs GPUs GPUs_DeviceName 2>/dev/null |
  awk -F', ' '{m[$1]=1; tot+=$2; f=($3=="undefined"?0:$3); free+=f; name[$4]+=$2; fr[$4]+=f}
       END{printf "\"gpu_nodes\":%d,\"gpus_total\":%d,\"gpus_free\":%d,\"gpu_models\":{", length(m), tot, free;
           s=""; for(k in name){printf "%s\"%s\":[%d,%d]", s, k, name[k], fr[k]; s=","}; printf "}"}')
printf '{"time":"%s",%s,%s}\n' "$(date -u +%FT%TZ)" "$cpu" "$gpu"
EOF
