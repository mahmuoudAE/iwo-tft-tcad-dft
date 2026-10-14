# C3 SUBMISSION v2 (only after Codex GO on digest_c3_v2.md and the logged F10 C3-plan addendum v2; standing user go
# 2026-10-14 ~11:10Z). Fail-closed (Codex C3 reply): pinned top-level manifest and shared-input hashes; every scheduler
# query must succeed; exactly one held job per IWOJob after submission, verified zero starts, RequestGPUs 0; the submit
# receipt and the held ad are preserved; an uncertain submission stops the loop for reconciliation (no retry).
# v2.1 (Codex C3 v2 reply): per-slot SHA256SUMS (incl. the live runs/<run>/relax.in) checked before submission and
# before release; condor_submit must exit 0 with exactly one receipt line, else stop (receipt kept).
set -u
A=/afs/cern.ch/user/m/melrashe/iwo_amorph; B=$A/checks/c3_companions; FS=$A/runs/fullstop_20261013.log
MAN_PIN=172b70710a2b6dc3301a4d76c031971ae4d2dd1f583a7b9c4b04581ffa38a4f1
SHARED_PIN=596812f2125e1ea186d0c64c2e6afe60aa4dec201053ea70ac7a9f08870e5dea
TS=$(date -u +%Y%m%dT%H%M%SZ); LOG=$B/SUBMIT_$TS.log; REC=$B/receipts_$TS; mkdir -p "$REC"
say() { echo "[$(date -u +%FT%TZ)] c3 $*" | tee -a "$LOG" >> "$FS"; echo "[$(date -u +%FT%TZ)] $*"; }
die() { say "STOP: $*"; exit 3; }
[ "$(sha256sum < $B/MANIFEST_SHA256.txt | cut -c1-64)" = "$MAN_PIN" ] || die "top-level manifest is not the reviewed one"
(cd "$B" && sha256sum -c --quiet MANIFEST_SHA256.txt) || die "staged files differ from the reviewed manifest"
[ "$(sha256sum < $B/SHARED_SHA256.txt | cut -c1-64)" = "$SHARED_PIN" ] || die "shared-input list is not the reviewed one"
(cd "$A" && sha256sum -c --quiet "$B/SHARED_SHA256.txt") || die "live common/ inputs or UPFs differ from the reviewed hashes"
q1() { local v; v=$(timeout 120 condor_q "$1" -af "$2" 2>/dev/null) || return 1; [ -n "$v" ] || return 1; echo "$v"; }
# submission order (F7 / A40): 0.7, 1.0, (0.8 deferred/pending), bulk
for run in aIWO_0p7_s1_mv_c3_w002 aIWO_0p7_s1_mv_c3_w005 aIWO_1p0_s1_c3_w002 aIWO_1p0_s1_c3_w005 aIO_1p0_s1_c3_w002 aIO_1p0_s1_c3_w005 \
           aIO_bulk_s1_c3_w002 aIO_bulk_s1_c3_w005 aIWO_bulk_s1_c3_w002 aIWO_bulk_s1_c3_w005; do
  S=$B/$run; R=$A/runs/$run
  (cd "$S" && sha256sum -c --quiet SHA256SUMS) || die "$run: slot inputs (incl. live runs/$run/relax.in) differ from its SHA256SUMS"
  all=$(timeout 120 condor_q -af IWOJob 2>/dev/null) || die "condor_q failed before $run"
  n=$(grep -cx "${run}_final" <<< "$all")
  [ "$n" = 0 ] || die "$n queued job(s) with IWOJob ${run}_final before submission"
  out=$(cd "$R" && timeout 120 condor_submit "$S/final.sub" 2>&1); src=$?
  echo "$out" > "$REC/$run.submit.txt"
  cl=$(grep -o -E '^1 job\(s\) submitted to cluster [0-9]+' <<< "$out" | grep -o -E '[0-9]+$')
  [ "$src" = 0 ] && [ -n "$cl" ] && [ "$(grep -c 'submitted to cluster' <<< "$out")" = 1 ] || \
    die "SUBMISSION UNCERTAIN for $run (rc $src; receipt kept $REC/$run.submit.txt): reconcile with condor_q -af IWOJob ClusterId before any retry"
  all=$(timeout 120 condor_q -af IWOJob ClusterId 2>/dev/null) || die "condor_q failed after submitting $run ($cl): left as submitted, on hold"
  [ "$(grep -c "^${run}_final " <<< "$all")" = 1 ] || die "not exactly one job ${run}_final after submission ($cl)"
  timeout 120 condor_q $cl -l > "$REC/$run.$cl.ad.txt" 2>&1 || die "ad of $cl not captured"
  EXP="$A/common/driver.sh,$A/common/qeio.py,$A/common/dat2h5.py,$A/common/pseudo,relax.in,$S/final.tmpl,$S/steps_final.sh"
  js=$(q1 $cl JobStatus) && hr=$(q1 $cl HoldReasonCode) && ns=$(q1 $cl NumJobStarts) && gp=$(q1 $cl RequestGPUs) && \
  iw=$(q1 $cl IWOJob) && wd=$(q1 $cl Iwd) && cm=$(q1 $cl Cmd) && ti=$(q1 $cl TransferInput) || die "query of $cl failed (left on hold)"
  bad=""
  [ "$js" = 5 ] || bad="$bad JobStatus=$js"; [ "$hr" = 15 ] || bad="$bad HoldReasonCode=$hr"
  case "$ns" in 0|undefined) ;; *) bad="$bad NumJobStarts=$ns";; esac
  [ "$gp" = 0 ] || bad="$bad RequestGPUs=$gp"
  [ "$iw" = "${run}_final" ] || bad="$bad IWOJob"; [ "$wd" = "$R" ] || bad="$bad Iwd"; [ "$cm" = "$S/final_node.sh" ] || bad="$bad Cmd"
  [ "$(tr -d ' ' <<< "$ti")" = "$EXP" ] || bad="$bad TransferInput"
  [ -z "$bad" ] || die "NOT READY $run $cl:$bad (left on hold)"
  c0=$(q1 $cl RequestCpus) && m0=$(q1 $cl RequestMemory) || die "request query of $cl failed"
  if [ "$c0" != 34 ] || [ "$m0" != 128000 ]; then
    timeout 120 condor_qedit $cl RequestCpus 34 >/dev/null 2>&1 && timeout 120 condor_qedit $cl RequestMemory 128000 >/dev/null 2>&1 || die "qedit of $cl failed"
    say "qedit $run $cl RequestCpus/RequestMemory $c0/$m0 -> 34/128000 (CERN submit transform; as 12904001)"
  fi
  [ "$(q1 $cl RequestCpus)" = 34 ] && [ "$(q1 $cl RequestMemory)" = 128000 ] || die "$cl request not 34/128000 (left on hold)"
  (cd "$S" && sha256sum -c --quiet SHA256SUMS) || die "$run $cl: slot inputs changed before release (left on hold)"
  timeout 120 condor_release $cl >/dev/null 2>&1 || die "release of $cl failed (left on hold)"
  say "released $run cluster $cl prio $(q1 $cl JobPrio) status $(q1 $cl JobStatus) (receipt $REC/$run.submit.txt, ad $REC/$run.$cl.ad.txt)"
done
say "end $TS"
