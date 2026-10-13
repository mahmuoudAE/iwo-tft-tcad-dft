# read-only provenance query: crystalline vac/ and checks/gpumax_work/a20_g002 only
cd ~/iwo_amorph || exit 1
for c in In32O48 In31WO48 In32O47 In31WO47_far In31WO47_near In31WO47_near72; do
  v=vac/$c; a=checks/gpumax_work/a20_g002/$c
  echo "######## $c"
  echo "-- vac files:"; ls $v | tr '\n' ' ' | cut -c1-900; echo
  [ -d $v/logs ] && { echo "-- vac logs:"; ls $v/logs | tr '\n' ' ' | cut -c1-900; echo; }
  echo "-- vac condor user-log submit/terminate lines:"
  for f in $(ls $v/*.log $v/logs/*.log 2>/dev/null); do grep -hE '^00[05] \(' $f 2>/dev/null | sed "s|^|  $(basename $f): |" | head -12; grep -hE 'return value' $f 2>/dev/null | head -6 | sed 's/^/     /'; done
  echo "-- a20 files:"; ls -R $a | tr '\n' ' ' | cut -c1-600; echo
  for f in $(ls $a/*.log $a/logs/*.log 2>/dev/null); do grep -hE '^00[05] \(' $f 2>/dev/null | sed "s|^|  $(basename $f): |" | head -6; grep -hE 'return value' $f | head -3 | sed 's/^/     /'; done
  echo "-- sha256 inputs:"; sha256sum $v/relax.in $v/scf.in $a/scf.in 2>/dev/null | awk '{print substr($1,1,16), $2}'
done
