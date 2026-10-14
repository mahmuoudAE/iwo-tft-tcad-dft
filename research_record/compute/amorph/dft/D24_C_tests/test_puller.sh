#!/bin/bash
# export_pull.sh v1 (staged a779b5d9) vs v2 without QE. Fake sandboxes of RUNNING finals, in condor_q order:
#   1001 aIWO_2p0_s9_final  running, NO EXPORT_PENDING (still in its SCF), EOS_PROBE OK
#   1002 aIO_1p5_s9_final   running, EXPORT_PENDING (2 files), EOS_PROBE OK
#   1003 aIWO_1p0_s9_final  running, EXPORT_PENDING (2 files), EOS_PROBE FAILED
#   1004 aIO_2p0_s9_final   idle (never probed);  1005 val_aIWO_2p0_s1_final running (skipped by v2)
# The condor_ssh_to_job stub runs the command in the sandbox and then reads its stdin to the end, as ssh without -n.
SP=/mnt/c/Users/moham/AppData/Local/Temp/claude/C--Users-moham-Downloads-IWO-Local-Codex-Handoff--1--IWO-ATLAS-Model-claude/7c34fe97-c389-4002-8f70-9615a643e20b/scratchpad/d24f
V1=$SP/v1/export_pull.sh.D24; V2=$SP/stage/common/export_pull.sh.D24
T=$HOME/d24f_test/puller; rm -rf $T; mkdir -p $T/bin
E=$T/eos/user/m/melrashe/qe/exports
mkjob() {   # mkjob <cluster> <name> <pending yes|no> <probe OK|FAILED>
  local d=$T/sb_$1; mkdir -p $d/exp
  echo "$4 2026-10-11T00:00:00Z XRD_ADLER32; kerberos: krbtgt valid" > $d/exp/EOS_PROBE
  [ $3 = yes ] || return 0
  head -c 300000 /dev/urandom > $d/exp/atomic_proj.xml.gz; head -c 2000 /dev/urandom > $d/exp/final_small.tar.gz
  { echo "# eos_dest $E/$2/final_$1"; echo "# run $2 cluster $1"
    for f in atomic_proj.xml.gz final_small.tar.gz; do echo "$f $(stat -c %s $d/exp/$f) $(sha256sum < $d/exp/$f | cut -c1-64)"; done; } > $d/exp/MANIFEST
  printf 'atomic_proj.xml.gz\nfinal_small.tar.gz\n' > $d/exp/EXPORT_PENDING
}
reset() { rm -rf $T/sb_* $T/eos $T/ssh_calls $T/pull.log $T/pull.seen; mkdir -p $E
  mkjob 1001 aIWO_2p0_s9 no OK; mkjob 1002 aIO_1p5_s9 yes OK; mkjob 1003 aIWO_1p0_s9 yes FAILED; mkjob 1005 val_x no OK; }
cat > $T/bin/condor_q <<'EOF'
#!/bin/bash
[ -n "${CQ_FAIL:-}" ] && { echo "-- Failed to fetch ads from: <schedd>" >&2; exit 1; }
echo "1001 0 aIWO_2p0_s9_final 2"
echo "1002 0 aIO_1p5_s9_final 2"
echo "1003 0 aIWO_1p0_s9_final 2"
echo "1004 0 aIO_2p0_s9_final 1"
echo "1005 0 val_aIWO_2p0_s1_final 2"
echo "1006 0 aIWO_2p0_s1_relax_s0 2"
EOF
cat > $T/bin/condor_ssh_to_job <<EOF
#!/bin/bash
echo "\$1: \$2" >> $T/ssh_calls
c=\${1%.*}
[ -n "\${SSH_FAIL:-}" ] && [ "\$c" = "\$SSH_FAIL" ] && { timeout 3 cat > /dev/null; exit 255; }
if [ -d $T/sb_\$c ]; then (cd $T/sb_\$c && bash -c "\$2" < /dev/null); rc=\$?; else rc=255; fi
timeout 3 cat > /dev/null    # ssh without -n reads its stdin to the end
exit \$rc
EOF
printf '#!/bin/bash\n[ "${1:-}" = -s ] && exit ${KLIST_RC:-0}\necho ticket\n' > $T/bin/klist
chmod +x $T/bin/*
export PATH=$T/bin:$PATH PULL_LOG=$T/pull.log PULL_SEEN=$T/pull.seen PULL_DEST_PREFIX=$T/eos/user/m/melrashe/
state() {
  for c in 1001 1002 1003; do
    n=$(awk -v c=$c '$1==c{sub(/_final$/, "", $3); print $3}' <(condor_q))
    echo "  job $c ($n): on EOS: $(ls $E/$n/final_$c 2>/dev/null | tr '\n' ' ')| sandbox EXPORT_PULLED: $( [ -f $T/sb_$c/exp/EXPORT_PULLED ] && echo yes || echo no)"
  done
  echo "  condor_ssh_to_job calls per job: $(cut -d: -f1 $T/ssh_calls 2>/dev/null | sort | uniq -c | tr -s ' ' | tr '\n' ';')"
}
echo "### T1 v1 (staged, a779b5d9): one round"; reset; bash $V1 > /dev/null 2>&1; echo "  exit $?"; state
echo "### T2 v2: one round (1002 and 1003 must be pulled in this round; probe failure of 1003 reported once)"; reset; bash $V2; echo "  exit $?"; state
echo "  sha256 on EOS vs manifest:"; for c in 1002 1003; do d=$(ls -d $E/*/final_$c); grep -v '^#' $T/sb_$c/exp/MANIFEST | while read -r f sz sh; do echo "    $c $f $( [ "$(sha256sum < $d/$f | cut -c1-64)" = "$sh" ] && echo OK || echo MISMATCH)"; done; done
echo "### T3 v2: second round = no-op (no copy, no new probe report)"; : > $T/ssh_calls; bash $V2; echo "  exit $?"; state; echo "  log lines: $(wc -l < $T/pull.log)"
echo "### T4 v2: condor_ssh_to_job fails for the FIRST job (1001): the others are still served"; reset; SSH_FAIL=1001 bash $V2 | grep -v 'pulled (' ; state
echo "### T5 v2: corrupt transfer (manifest sha256 wrong for 1002): nothing marked pulled for 1002, no .part left"; reset
sed -i 's/^\(atomic_proj.xml.gz [0-9]*\) .*/\1 0000000000000000000000000000000000000000000000000000000000000000/' $T/sb_1002/exp/MANIFEST
bash $V2 | grep -E '1002'; state; echo "  .part files: $(find $E -name '*.part' | wc -l)"
echo "### T6 v2: no valid Kerberos ticket -> exit 3, nothing touched"; reset; KLIST_RC=1 bash $V2; echo "  exit $?"; state
echo "### T7 v2: condor_q fails -> exit 4"; reset; CQ_FAIL=1 bash $V2; echo "  exit $?"; state
