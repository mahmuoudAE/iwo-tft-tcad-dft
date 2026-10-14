#!/bin/bash
# eos_put (steps_final.sh.D24 v2) unit test: deadline skip, skip after a hang, timeout bound, global state kept
SP=/mnt/c/Users/moham/AppData/Local/Temp/claude/C--Users-moham-Downloads-IWO-Local-Codex-Handoff--1--IWO-ATLAS-Model-claude/7c34fe97-c389-4002-8f70-9615a643e20b/scratchpad/d24f
T=~/d24f_test/eosput; rm -rf $T; mkdir -p $T/bin $T/fe && cd $T
cat > bin/xrdcp <<X
#!/bin/bash
[ -n "\${HANGX:-}" ] && exec sleep 600
a=(); for x in "\$@"; do case \$x in -C|-f|-s|adler32) ;; *) a+=("\$x");; esac; done
d=$T/fe\${a[1]#root://eosuser.cern.ch/}; mkdir -p "\$(dirname "\$d")"; cp "\${a[0]}" "\$d"
X
printf '#!/bin/bash\n[ -n "${HANGX:-}" ] && exec sleep 600\nexit 0\n' > bin/xrdfs; chmod +x bin/*
export PATH=$T/bin:$PATH JOB=final EXPORT_RETRY_SLEEP=1
source $SP/stage/common/steps_final.sh.D24
head -c 3000000 /dev/urandom > f.bin
DEADLINE=$(( $(date +%s) + 3600 )); eos_put f.bin /eos/x/d; echo "1 future deadline: $EOS_ST (hung='$EOS_HUNG') $(cmp -s f.bin fe/eos/x/d/f.bin && echo copy-identical)"
DEADLINE=$(( $(date +%s) - 1 )); eos_put f.bin /eos/x/d2; echo "2 past deadline:   $EOS_ST $( [ -e fe/eos/x/d2/f.bin ] && echo copied || echo 'not copied')"
DEADLINE=$(( $(date +%s) + 3600 )); EXPORT_IO_TIMEOUT=2 EXPORT_PROBE_TIMEOUT=2; export HANGX=1
t0=$(date +%s); eos_put f.bin /proc/nowhere; echo "3 hanging EOS:     $EOS_ST after $(( $(date +%s) - t0 )) s, EOS_HUNG set: $( [ -n "$EOS_HUNG" ] && echo yes || echo no)"
unset HANGX; t0=$(date +%s); eos_put f.bin /eos/x/d3; echo "4 after a hang:    $EOS_ST after $(( $(date +%s) - t0 )) s (no new EOS call: $( [ -e fe/eos/x/d3/f.bin ] && echo NO || echo yes))"
EOS_HUNG=; eos_put f.bin /eos/x/d3; echo "5 hang cleared:    $EOS_ST"
grep -c 'timed out' final_export.log | sed 's/^/  timeouts logged: /'; pgrep -f 'sleep 600' | wc -l | sed 's/^/  leftover sleep processes: /'
