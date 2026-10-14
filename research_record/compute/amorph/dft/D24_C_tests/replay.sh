#!/bin/bash
# D-24 v2 replay test (WSL Ubuntu-22.04). usage: replay.sh <tag> <mode> [steps file] [run name]
# Runs the real final_node.sh(.D24) + driver.sh (CERN copies) + steps_final.sh(.D24) in QE_LOCAL mode. pw.x, pp.x,
# average.x, projwfc.x and mpirun are stubs that replay the outputs of the real local QE run d24ok (In15WO24, 40 atoms,
# 7 k, 230 bands; ~/d24test/fake_eos_d24ok), so no QE memory is needed. xrdcp/xrdfs stubs write a fake EOS tree.
#   ok       in-job copies succeed
#   fail     in-job xrdcp and the FUSE fallback fail, nobody pulls (EXPORT_WAIT_S 20)
#   pend     as fail, plus an "lxplus" loop: export_pull.sh.D24 v2 with a stub condor_q that lists another RUNNING final
#            WITHOUT EXPORT_PENDING first, then this job; condor_ssh_to_job stub drains its stdin like ssh without -n
#   hang     xrdcp/xrdfs hang (sleep 600); EXPORT_IO_TIMEOUT / EXPORT_PROBE_TIMEOUT 4 s; nobody pulls
#   projfail in-job copies succeed; projwfc.x writes no atomic_proj.xml (e.g. out of memory)
#   nc       pw.x output with 'convergence NOT achieved' (then JOB DONE)
#   maxsec   pw.x stopped by max_seconds before convergence (then JOB DONE)
set -u
SP=/mnt/c/Users/moham/AppData/Local/Temp/claude/C--Users-moham-Downloads-IWO-Local-Codex-Handoff--1--IWO-ATLAS-Model-claude/7c34fe97-c389-4002-8f70-9615a643e20b/scratchpad
ST=$SP/d24f/stage/common; ORIG=$SP/d24/cern_orig
TAG=$1 MODE=$2 STEPS=${3:-$ST/steps_final.sh.D24} NAME=${4:-test_2p0_s1}
NODE=${NODE:-$ST/final_node.sh.D24}
SRC=~/d24test/fake_eos_d24ok/eos/user/m/melrashe/qe/exports/test_2p0_s1/final_992421
T=~/d24f_test; W=$T/$TAG; FE=$T/fake_eos_$TAG; RS=$T/replay_src
chmod -R u+w "$W" "$FE" 2>/dev/null; rm -rf "$W" "$FE" "$W".*; mkdir -p "$W/pseudo" "$FE/eos/user/m/melrashe/qe" "$W.bin" "$W.qe/bin" "$W.lx"
if [ ! -f "$RS/done" ]; then   # the recorded QE outputs, unpacked once
  rm -rf "$RS"; mkdir -p "$RS/save" "$RS/small" && cd "$RS"
  tar xzf "$SRC/final_small.tar.gz" -C small; tar xzf "$SRC/pdos_atoms.tar.gz"; tar xzf "$SRC/save_nowfc.tar.gz" -C save
  zcat "$SRC/atomic_proj.xml.gz" > atomic_proj.xml; zcat "$SRC/projwfc_final.out.gz" > projwfc_final.out; touch done
fi
cp $ORIG/{driver.sh,qeio.py,dat2h5.py} "$W/"; cp "$NODE" "$W/final_node.sh"; cp "$STEPS" "$W/steps_final.sh"
cp ~/d24test/inputs/final.tmpl ~/d24test/inputs/relax.in "$W/"; sed -i "s/verbosity = 'low'/verbosity = 'high'/" "$W/final.tmpl"
cp ~/toytest/gen/pseudo/{In,W,O}.*.UPF "$W/pseudo/"
CL=88$(printf '%s' "$TAG" | cksum | cut -c1-4)
printf 'ClusterId = %s\nProcId = 0\nGlobalJobId = "test#%s.0#0"\nIWOJob = "%s_final"\nDAGManJobId = 12884201\nDAGNodeName = "FINAL"\nRequestCpus = 4\n' \
  "$CL" "$CL" "$NAME" > "$W.jobad"
# --- QE stubs (replay) ---
Q=$W.qe/bin
ln -s ~/miniforge3/envs/qe/bin/python $Q/python
cat > $Q/mpirun <<'EOF'
#!/bin/bash
while [ $# -gt 0 ] && [[ $1 != *.x ]]; do shift; done
exec "$@"
EOF
cat > $Q/pw.x <<EOF
#!/bin/bash
mkdir -p tmp/slab.save && cp -r $RS/save/slab.save/. tmp/slab.save/ && head -c 50000 /dev/urandom > tmp/slab.save/wfc1.hdf5
case \${PWMODE:-ok} in
  nc)     sed -e 's/convergence has been achieved in .*/convergence NOT achieved after 200 iterations: stopping/' -e '/^!/d' $RS/small/scf.out;;
  maxsec) sed -n '1,/iteration #  3/p' $RS/small/scf.out; echo '     Maximum CPU time exceeded'; echo; echo '   JOB DONE.';;
  *)      cat $RS/small/scf.out;;
esac
EOF
cat > $Q/pp.x <<'EOF'
#!/bin/bash
echo "stub pp.x"; echo "dummy" > final_v.pp; echo "   JOB DONE."
EOF
cat > $Q/average.x <<EOF
#!/bin/bash
cat > /dev/null; cp $RS/small/final_avg.dat avg.dat
EOF
cat > $Q/projwfc.x <<EOF
#!/bin/bash
mkdir -p pdos; cp $RS/pdos/* pdos/; cp $RS/small/pdos/*pdos_tot pdos/
[ "\${PWMODE:-ok}" = projfail ] || cp $RS/atomic_proj.xml tmp/slab.save/atomic_proj.xml
cat $RS/projwfc_final.out
EOF
# --- EOS stubs ---
XF=0; HANG=0; case $MODE in fail|pend) XF=1;; hang) HANG=1;; esac
cat > "$W.bin/xrdcp" <<XR
#!/bin/bash
echo "xrdcp \$*" >> $W.eos_calls
[ $HANG = 1 ] && exec sleep 600
[ $XF = 1 ] && { echo "stub xrdcp: [ERROR] Server responded with an error: [3010] Unable to open - unauthorized identity used" >&2; exit 54; }
args=(); ck=0; for a in "\$@"; do case "\$a" in -C) ck=1;; -f|-s|adler32) ;; *) args+=("\$a");; esac; done
src=\${args[0]}; dst=\${args[1]}; dst=$FE\${dst#root://eosuser.cern.ch/}
mkdir -p "\$(dirname "\$dst")" && cp -f "\$src" "\$dst" || exit 50
if [ \$ck = 1 ]; then python3 -c "import sys,zlib
def a(p):
    v=1
    with open(p,'rb') as f:
        for b in iter(lambda: f.read(1<<20), b''): v=zlib.adler32(b,v)
    return v
sys.exit(0 if a(sys.argv[1])==a(sys.argv[2]) else 1)" "\$src" "\$dst" || exit 51; fi
XR
cat > "$W.bin/xrdfs" <<XS
#!/bin/bash
echo "xrdfs \$*" >> $W.eos_calls
[ $HANG = 1 ] && exec sleep 600
[ $XF = 1 ] && exit 54
shift; cmd=\$1; shift
case \$cmd in
  mkdir) [ "\$1" = -p ] && shift; mkdir -p "$FE\$1";;
  stat) [ -e "$FE\$1" ] && echo "Size:       \$(stat -c %s "$FE\$1")" || exit 1;;
esac
XS
printf '#!/bin/bash\nexit 1\n' > "$W.bin/klist"   # no ticket on the test worker
chmod +x "$W.bin"/* "$Q"/*
export PATH="$W.bin:$PATH" QE_LOCAL=$W.qe NCPU_OVERRIDE=4 MPIOPT="--bind-to none" _CONDOR_SCRATCH_DIR=$W _CONDOR_JOB_AD=$W.jobad \
       EXPORT_RETRY_SLEEP=1 PWMODE=$MODE
case $MODE in
  ok|projfail|nc|maxsec) export EXPORT_EOS=/eos/user/m/melrashe/qe/exports;;
  fail) export EXPORT_EOS=/proc/no_eos/exports EXPORT_WAIT_S=20;;
  hang) export EXPORT_EOS=/proc/no_eos/exports EXPORT_WAIT_S=20 EXPORT_IO_TIMEOUT=4 EXPORT_PROBE_TIMEOUT=4;;
  pend) export EXPORT_EOS=$FE/eos/user/m/melrashe/qe/exports EXPORT_WAIT_S=600
        chmod 555 "$FE/eos/user/m/melrashe/qe"     # the in-job FUSE fallback must fail too
        OTHER=$T/sb_${TAG}_other; rm -rf $OTHER; mkdir -p $OTHER/exp; echo "OK 2026-10-11T00:00:00Z XRD_ADLER32; kerberos: x" > $OTHER/exp/EOS_PROBE
        cat > "$W.lx/condor_q" <<CQ
#!/bin/bash
echo "5550 0 aIWO_0p7_s9_final 2"
echo "5551 0 val_aIWO_2p0_s1_final 2"
echo "$CL 0 ${NAME}_final 2"
echo "5552 0 aIO_1p0_s9_final 1"
CQ
        cat > "$W.lx/condor_ssh_to_job" <<CS
#!/bin/bash
echo "\$1: \$2" >> $W.ssh_calls
case \$1 in 5550.0) d=$OTHER;; $CL.0) d=$W;; *) exit 255;; esac
(cd "\$d" && bash -c "\$2" < /dev/null); rc=\$?
timeout 3 cat > /dev/null    # ssh without -n reads its stdin to the end
exit \$rc
CS
        printf '#!/bin/bash
exit 0
' > "$W.lx/klist"; chmod +x "$W.lx"/*   # lxplus side: valid ticket
        ( until [ -f "$W/exp/EXPORT_PENDING" ] || [ -f "$W/final_results.tar.gz" ]; do sleep 2; done
          echo "[puller] EXPORT_PENDING seen: $(tr '\n' ' ' < "$W/exp/EXPORT_PENDING" 2>/dev/null)"
          chmod 755 "$FE/eos/user/m/melrashe/qe"; sleep 3
          PATH="$W.lx:$PATH" PULL_LOG=$W.pull.log PULL_SEEN=$W.pull.seen PULL_DEST_PREFIX=$FE/eos/user/m/melrashe/ \
            bash $ST/export_pull.sh.D24; echo "[puller] round 1 exit $?"
          echo "[puller] ssh calls in round 1: $(cut -d: -f1 $W.ssh_calls | sort | uniq -c | tr -s ' ' | tr '\n' ';')"
          PATH="$W.lx:$PATH" PULL_LOG=$W.pull.log PULL_SEEN=$W.pull.seen PULL_DEST_PREFIX=$FE/eos/user/m/melrashe/ \
            bash $ST/export_pull.sh.D24; echo "[puller] round 2 (no-op) exit $?"
        ) > "$W.puller.out" 2>&1 &
        ;;
esac
cd "$W"; t0=$(date +%s)
bash final_node.sh 20000 > final_node.stdout 2>&1; rc=$?
echo "TAG $TAG MODE $MODE final_node.sh exit $rc after $(( $(date +%s) - t0 )) s"
wait
echo "--- final_node.stdout"; cat final_node.stdout | tail -4
echo "--- driver log (export / lineage / probe lines)"; grep -E 'export|lineage|probe|SCF|steps finished' final_driver.log | sed 's/^\[[^]]*\] //'
echo "--- export_manifest_final.dat"; cat export_manifest_final.dat 2>/dev/null | grep -v '^# status\|^# FAILED\|^# file\|^# D-24'
echo "--- export_checks (proj_atoms / consistency)"; grep -E 'proj_atoms|consistency|electron_count|min_compl' export_checks_final.dat 2>/dev/null
echo "--- lineage_final.dat"; grep -E 'eos_probe|geometry_check|scf.in' lineage_final.dat 2>/dev/null
echo "--- AFS tarball: $(stat -c %s final_results.tar.gz) B, $(tar tzf final_results.tar.gz | wc -l) members; proj_atoms: $(tar tzf final_results.tar.gz | grep -c proj_atoms_final.dat), pdos_atm: $(tar tzf final_results.tar.gz | grep -c pdos_atm), full projwfc: $(tar tzf final_results.tar.gz | grep -cx projwfc_final.out)"
dest=$(awk '$2=="eos_dest"{print $3}' exp/MANIFEST 2>/dev/null)
for d in "$FE$dest" "$dest"; do [ -n "$dest" ] && [ -d "$d" ] && {
  echo "--- EOS dir $d"; ls "$d" | tr '\n' ' '; echo
  grep -v '^#' exp/MANIFEST | while read -r f sz sh; do
    if [ -f "$d/$f" ]; then echo "  $f $( [ "$(sha256sum < "$d/$f" | cut -c1-64)" = "$sh" ] && echo sha256-OK || echo sha256-MISMATCH)"; else echo "  $f absent"; fi; done; }; done
echo "--- EOS calls: $(wc -l < $W.eos_calls 2>/dev/null || echo 0)"
[ -f "$W.puller.out" ] && { echo "--- puller"; cat "$W.puller.out"; cat "$W.pull.log" 2>/dev/null; }
exit 0
