D-24 items B and D: safe continuation of the 16 slab relaxations, single-H200 benchmark
=======================================================================================
Built 2026-10-11 (staged, not installed). Scope: the 16 chains runs/<name>/ except runs/aIO_0p8_s1 (A15 pilot,
own scripts) and except vac/ (own node scripts). Install: bash ~/iwo_amorph/common/install_D24_BD.sh --dry-run,
then without --dry-run. Rollback: section 5.

1. What changes (item B)
------------------------
- runs/<name>/steps_relax.sh: the pilot's repaired classification (geomsel.py, byte-identical to the pilot's):
    any 'convergence NOT achieved'                     -> FAILED
    'bfgs converged' + final coordinates (A19)         -> CONVERGED, relax.in = final geometry
    >= 1 new SCF-validated geometry                    -> CONTINUE from the lowest-energy validated geometry
    anything else (no relax.out, nothing new validated) -> FAILED
  A validated geometry is a fresh-BFGS restart point, not necessarily an accepted BFGS step.
  On FAILED it writes 'FAILED <utc> <job>: <reason>; geomsel: <summary>' into segment_guard and keeps the
  lowest-energy validated geometry, if any, as relax_s<seg>_bestvalid.in. Every segment also packs
  relax_s<seg>_input.in (its own input) and relax_s<seg>_lineage.log (status, reason, selection, positions md5).
- runs/<name>/relax.sub: transfer_input_files += common/geomsel.py, segment_guard;
  transfer_output_files += segment_guard.
- runs/<name>/segment_guard: new, empty.
- common/relax_node.sh: two stops before driver.sh unpacks anything (seconds, exit 1, RELAX_STATUS FAILED,
  relax_s<seg>_results.tar.gz = relax_s<seg>_driver.log note + relax.in + segment_guard, every TransferOutput
  entry present):
    a. segment_guard holds a line starting with FAILED;
    b. preflight: steps_relax.sh needs geomsel.py but the job ad did not transfer it (an ad from before D-24,
       e.g. a held job released later). The DAG retry then comes from the new relax.sub.
  Both are inert for nodes that do not transfer segment_guard / do not use geomsel (vac, pilot, old ads).
- Idle RELAX node jobs get the same two transfer additions by condor_qedit (constraint JobStatus == 1).

Why a guard: these DAGs were started without UNLESS-EXIT, and DAGMan reads the .dag only at start. A FAILED
segment exits 1 like a CONTINUE, so DAGMan would replay it from the unchanged relax.in, up to 8 times x 20 h.

2. Living with the guard
------------------------
- Find guarded chains:   grep -H FAILED ~/iwo_amorph/runs/*/segment_guard
- A guarded retry still waits in the GPU queue for a match, then stops in seconds. Each consumes one of the
  8 retries; when they are used up the DAG ends with a rescue DAG (<name>.dag.rescue001). Nothing runs pw.x.
- Diagnose from the FAILED segment's tarball (runs/<name>/relax_s<seg>_results.tar.gz, also on EOS
  checkpoints/relax_s<seg>_<cluster>.tar.gz): relax.out, relax_s<seg>_lineage.log, relax_s<seg>_bestvalid.in.

3. Resetting a guarded chain (user / main session decision)
-----------------------------------------------------------
 1. Decide what the next segment starts from and change runs/<name>/relax.in only if needed, e.g.
      tar xzf relax_s<k>_results.tar.gz relax_s<k>_bestvalid.in && cp relax.in relax.in.pre_reset_<utc> \
        && cp relax_s<k>_bestvalid.in relax.in
    (or the A15 rescue settings, once the pilot verdict allows them).
 2. Keep the guard text and clear it:
      cp segment_guard segment_guard.<utc> && : > segment_guard
 3. Then, depending on the RELAX node state (condor_q -dag; IWOJob <name>_relax_s<seg>):
    - DAG alive, node job idle: nothing else; the guard is read from runs/<name>/ when that job starts.
    - DAG alive, node job held: condor_release only if it ran < 1 h (project rule); otherwise leave it to the user.
    - DAG finished (retries used up, rescue file written): move the old segment tarballs first, because the
      rescue run restarts $(RETRY) at 0 and would overwrite relax_s0_results.tar.gz:
        mkdir attempt<N> && mv relax_s*_results.tar.gz attempt<N>/
      then, from runs/<name>/:  condor_submit_dag <name>.dag   (DAGMan picks up the rescue file itself).
 4. Log the reset (time, reason, new relax.in md5) in the work chat.
 Re-arming by hand (e.g. to stop a chain before its next segment):
      echo "FAILED $(date -u +%FT%TZ) manual: <reason>" > runs/<name>/segment_guard

4. Item D: single-H200 benchmark (runs/aIWO_1p0_Al2O3_s2 only)
-------------------------------------------------------------
Change: the idle RELAX job (s0) and relax.sub go from 2 x H100|H200 to 1 x H200 (request_gpus 1,
regexp("H200", TARGET.GPUs_DeviceName); environment QE_NK=1 kept). Inputs, container (QE 7.3.1 GPU) and
tolerances are identical. On this schedd the user requirement lives in the job attribute PreVerRequirements
(Requirements -> PreGPURequirements -> PreAfsRequirements -> PreCvmfsRequirements -> PreVerRequirements), and
the CERN transform sets RequestCpus 22 / RequestMemory 66000 for 1 and 2 GPUs alike, so host resources do not
change. Its steps_relax.sh logs nvidia-smi (timestamp, index, name, memory.used, memory.total, utilization.gpu)
every 120 s into gpumem.log (packed via *.log) and prints the peak into the driver log.

Expected GPU memory (300 atoms: Al60 H16 In49 O174 W1, 1891 e, nbnd 1135 default, c = 43.58 A, k 2x2x1):
- Reference: aIO_2p0_s1, 268 atoms (H12 In100 O156, 2248 e, nbnd 1349, c = 42.18 A) ran on one H100 NVL
  (95,312 MiB) at the limit (GpusMemory 95,628 MB); six 252-274-atom cells (2214-2264 e) ran out of device
  memory on one H100 at start-up (QE host estimates 130-173 GB per process).
- Scaling of the device arrays (npw ~ volume x1.033; nbnd x0.841; PAW projectors 3404 vs 3072, Al has 18):
  wavefunctions + Davidson (2 x nbnd) x0.87, beta projectors x1.15, dense grids x1.03; weighted ~0.94.
- Expected need: ~0.94 x (~95 GB) = ~90 GB (range 83-95 GB): marginal on one H100, ~60 % of one H200
  (143,148 MiB), headroom ~50-60 GB. The Davidson step of the first SCF is the peak.
- Caveat: nvidia-smi / GPUsMemoryUsage read 88-95 GB even for the 126-155-atom cells on H100s (allocator
  caching), so a high gpumem.log reading alone is not an out-of-memory signal.
- Speed reference: aIO_2p0_s1 s0 on one H100 NVL, ~200 SCF iterations in 4 h 58 min (~89 s/iteration).

Abort / revert rule (revert = relax.sub.pre_D24 for retries; if the node job is idle, condor_qedit
PreVerRequirements back to regexp("H100|H200",...) and RequestGPUs 2; clear the guard per section 3):
- REVERT if relax.out or the job .err shows "Out of memory allocating", "cudaErrorMemoryAllocation",
  "cdiaghg_gpu", any other CUDA allocation error, or pw.x ends before the first '!' energy. The D-24 logic marks
  such a segment FAILED and arms the guard by itself, so nothing is replayed.
- REVERT if the job is still idle 12 h after the conversion (no H200 slot; the queue gain is gone).
- REVERT if the segment completes with a mean SCF iteration time > 180 s (2x the H100 reference).
- PASS (fits with headroom): >= 1 new validated geometry (first SCF + forces + second SCF) without any memory
  error; record the gpumem.log peak and the s/iteration in RESULTS_LOG (job id). Only then offer to move the
  waiting 2-GPU cells (all <= 274 atoms) to 1 x H200 (a procedural log entry).
- A FAILED segment for a non-memory reason (SCF not converged) is no hardware verdict; it follows section 3.

5. Rollback
-----------
  cd ~/iwo_amorph
  for r in <16 runs>; do mv runs/$r/relax.sub.pre_D24 runs/$r/relax.sub; mv runs/$r/steps_relax.sh.pre_D24 runs/$r/steps_relax.sh; done
  mv common/relax_node.sh.pre_D24 common/relax_node.sh
  (common/geomsel.py and the empty segment_guard files are inert without the new scripts; the extra transfers in
   edited idle ads are harmless with the old scripts.)

6. make_dft.py follow-up (NOT done here: the file belongs to the HfO2 build agent)
---------------------------------------------------------------------------------
New chains written by make_dft.py (e.g. the H-M HfO2 cells) still get the pre-D-24 steps_relax.sh and relax.sub.
Port: steps_relax.sh = runs/<any>/steps_relax.sh.D24 (without the gpumem block); relax.sub
transfer_input_files += common/geomsel.py, segment_guard and transfer_output_files += segment_guard; create an
empty segment_guard per run. New DAGs can also get 'RETRY RELAX 8 UNLESS-EXIT 2' with a node script that exits 2
on FAILED (as the pilot); the guard then stays as a second line of defence.
