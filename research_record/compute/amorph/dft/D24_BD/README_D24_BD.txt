D-24 items B and D: safe continuation of the 16 slab relaxations, single-H200 benchmark (staging v2c)
==================================================================================================
Built 2026-10-11 (staged, not installed); v2 after the verification of v1 (revert path of item D, transition of the
running pre-D-24 segments, manual stop that a running job cannot overwrite, drift checks in the install, failure
category in the guard, MIG slices excluded); v2c: install step 6 re-checks for RELAX jobs that started during the
install, and d24_transition.sh handles a chain whose newest segment already ran the D-24 steps (section 3a).
Scope: the 16 chains runs/<name>/ except runs/aIO_0p8_s1 (A15 pilot, own scripts) and except vac/ (own node
scripts). Install: bash ~/iwo_amorph/common/install_D24_BD.sh --dry-run, then without --dry-run.
Rollback: section 5. Earlier stagings: common/D24_BD_backup/{v1,v2a,v2b}.pre_D24/.

1. What changes (item B)
------------------------
- runs/<name>/steps_relax.sh: the pilot's repaired classification (geomsel.py, byte-identical to the pilot's):
    any 'convergence NOT achieved'                     -> FAILED [scf]
    'bfgs converged' + final coordinates (A19)         -> CONVERGED, relax.in = final geometry
    >= 1 new SCF-validated geometry                    -> CONTINUE from the lowest-energy validated geometry
    anything else                                      -> FAILED [infra | early | noprogress | parse]
  A validated geometry is a fresh-BFGS restart point, not necessarily an accepted BFGS step.
  On FAILED it writes 'FAILED <utc> <job> [<category>]: <reason>; geomsel: <summary>' into segment_guard and keeps
  the lowest-energy validated geometry, if any, as relax_s<seg>_bestvalid.in. Categories:
    scf        an SCF did not converge
    infra      relax.out missing or empty (container / EOS fetch / node failure, runaway output), or a GPU memory or
               CUDA error in it ('Out of memory allocating', CUDA_ERROR_*, cudaError*, 'Accelerator Fatal Error')
    early      pw.x stopped before its first SCF energy for another reason (input error, 'Error in routine ...')
    noprogress SCF energies, but no new validated geometry (e.g. time limit inside the second SCF)
    parse      'bfgs converged', but the final geometry could not be extracted
  Every segment also packs relax_s<seg>_input.in (its own input) and relax_s<seg>_lineage.log (status, reason,
  selection, positions md5).
- runs/<name>/relax.sub: transfer_input_files += common/geomsel.py, segment_guard, segment_stop;
  transfer_output_files += segment_guard; requirements += && !regexp("MIG", TARGET.GPUs_DeviceName) (the H100|H200
  regexp also matches the MIG slices 'NVIDIA H100L-1-12C MIG 1g.12gb' and '...2g.24gb'; a match would now stop the
  chain with an infra FAILED instead of retrying). Idle ads keep their device clause: no MIG slot offers 22 CPU /
  66 GB today.
- runs/<name>/segment_guard (input and output, written by the steps) and runs/<name>/segment_stop (input only, written
  by people and by the install): new, empty. Never delete them while D-24 ads exist (a missing input file holds the
  job); empty them instead.
- common/relax_node.sh: three stops before driver.sh unpacks anything (seconds, exit 1, RELAX_STATUS FAILED,
  relax_s<seg>_results.tar.gz = relax_s<seg>_driver.log note + relax.in + segment_guard + segment_stop, every
  TransferOutput entry present):
    a. segment_stop holds a line starting with STOP (or FAILED);
    b. segment_guard holds a line starting with FAILED (or STOP);
    c. preflight: steps_relax.sh needs geomsel.py but the job ad did not transfer it (an ad from before D-24,
       e.g. a held job released later). The DAG retry then comes from the new relax.sub.
  All are inert for nodes that do not transfer the files / do not use geomsel (vac, pilot, old ads).
- Idle RELAX node jobs get the same transfer additions by condor_qedit (constraint JobStatus == 1).
- common/d24_transition.sh: re-classifies the last pre-D-24 segment of a chain (section 3a).
- Install order: inert files and transition stops (1), idle ads (2), relax.sub (3), relax_node.sh (4), steps (5), then a
  transition re-check (6) for RELAX jobs that were idle in step 1 and started before step 5 ended (a job reads
  steps_relax.sh when it starts, so such a job may run the pre-D-24 steps).

Why a guard: these DAGs were started without UNLESS-EXIT, and DAGMan reads the .dag only at start. A FAILED
segment exits 1 like a CONTINUE, so DAGMan would replay it from the unchanged relax.in, up to 8 times x 20 h.
Trade-off (accepted for the pilot): an infrastructure failure now stops the chain until a person resets it, where
the old scripts retried; the [infra] category makes that reset routine (section 3).

2. Living with the stops
------------------------
- Find stopped chains:   grep -H -E '^(STOP|FAILED)' ~/iwo_amorph/runs/*/segment_stop ~/iwo_amorph/runs/*/segment_guard
- A stopped retry still waits in the GPU queue for a match, then stops in seconds. Each consumes one of the
  8 retries; when they are used up the DAG ends with a rescue DAG (<name>.dag.rescue001). Nothing runs pw.x.
- Diagnose from the FAILED segment's tarball (runs/<name>/relax_s<seg>_results.tar.gz, also on EOS
  checkpoints/relax_s<seg>_<cluster>.tar.gz): relax.out, relax_s<seg>_lineage.log, relax_s<seg>_bestvalid.in.
- Stop a chain by hand (works at any time, also while one of its jobs runs; the next segment stops at its start):
      echo "STOP $(date -u +%FT%TZ) manual: <reason>" >> ~/iwo_amorph/runs/<name>/segment_stop
  Do not write segment_guard by hand: a running D-24 job transfers its own copy back when it ends and would
  overwrite it.

3. Resetting a stopped chain (user / main session decision)
----------------------------------------------------------
 1. Decide what the next segment starts from and change runs/<name>/relax.in only if needed, e.g.
      tar xzf relax_s<k>_results.tar.gz relax_s<k>_bestvalid.in && cp relax.in relax.in.pre_reset_<utc> \
        && cp relax_s<k>_bestvalid.in relax.in
    (or the A15 rescue settings, once the pilot verdict allows them). After an [infra] FAILED nothing needs to
    change: relax.in is still the segment's input (check relax.out / the job .err first). For a transition segment
    the best validated geometry may come from the previous segment's relax.out: see 3a.
 2. Keep the stop texts and clear them, only while no RELAX job of the chain is running (idle is fine; a running
    stopped job transfers its segment_guard back and would re-arm it):
      u=$(date -u +%Y%m%dT%H%M%SZ); cp segment_guard segment_guard.$u; cp segment_stop segment_stop.$u
      : > segment_guard; : > segment_stop
 3. Then, depending on the RELAX node state (condor_q -dag; IWOJob <name>_relax_s<seg>):
    - DAG alive, node job idle: nothing else; the files are read from runs/<name>/ when that job starts.
    - DAG alive, node job held: condor_release only if it ran < 1 h (project rule); otherwise leave it to the user.
    - DAG finished (retries used up, rescue file written): move the old segment tarballs first, because the
      rescue run restarts $(RETRY) at 0 and would overwrite relax_s0_results.tar.gz:
        mkdir attempt<N> && mv relax_s*_results.tar.gz attempt<N>/
      then, from runs/<name>/:  condor_submit_dag <name>.dag   (DAGMan picks up the rescue file itself).
 4. Log the reset (time, reason, new relax.in md5) in the work chat.

3a. Transition segments (chains whose last segment ran the pre-D-24 steps)
---------------------------------------------------------------------------
The old steps wrote relax.in = the last printed geometry, which can be an unvalidated trial whose SCF failed (the
aIO_0p7_s1 s0 case). The first D-24 segment would start from it and probably repeat the failing SCF for hours before
it ends FAILED, and that FAILED segment has no relax_s<seg>_bestvalid.in (nothing in it was validated). Therefore the
install arms segment_stop ('STOP <utc> D24-transition: ...') for every chain whose RELAX job is running at install
time (it carries the pre-D-24 steps; its input relax.in is kept as relax_s<k>_input.in) or whose relax.in is still the
one its last finished segment wrote (pre-D-24 rule). A chain whose relax.in a person replaced after that segment gets
no line: whoever replaced it owns the restart (review with d24_transition.sh <name>, read-only; its --apply refuses
such a chain). After the file swaps the install checks again (step 6): a RELAX job that was idle in step 1 and started
before the swaps ended (JobCurrentStartDate up to 10 s after them) may have taken the pre-D-24 steps, so its chain
gets the same line. If that job took the D-24 steps after all, d24_transition.sh reports 'already ran the D-24
steps' and --apply only removes the line (the segment's own D-24 verdict governs).
Status at staging (2026-10-11): running s0 of aIO_1p0_s1 12883942, aIWO_0p7_s1 12883952,
aIWO_0p7_s1_bare 12884017, aIWO_0p8_s2 12884030, aIWO_1p0_s1 12883943; finished s0 (s1 held) of aIO_0p7_s1 and
aIO_2p0_s1. When the chain's pre-D-24 segment has ended (no RELAX job of the chain running; its next retry may be
idle or already stopped), run
      bash ~/iwo_amorph/common/d24_transition.sh <name>            (read-only verdict)
      bash ~/iwo_amorph/common/d24_transition.sh <name> --apply
It runs the chain's own D-24 steps() on that segment's relax.out in /tmp and
  CONTINUE  -> sets relax.in to the lowest-energy validated geometry if it differs (relax.in.pre_transition_<stamp>);
  FAILED    -> keeps the chain stopped with a 'STOP <utc> d24_transition: relax_s<k> [<category>]: ...' line and
               writes relax_s<k>_bestvalid.in when the best validated geometry is known; then section 3;
  CONVERGED -> nothing (the DAG is at FINAL);
then removes the D24-transition line. It refuses while a RELAX job of the chain runs and when relax.in was changed
after the segment; every --apply is logged in runs/<name>/d24_transition.log. If the next retry is still idle when
--apply is done, no retry is used.
The two held chains (finished s0, s1 held after an output-transfer failure; the held s1 ads are pre-D-24, so a job
released after the install stops at the preflight within seconds and the next retry comes from the D-24 relax.sub):
- aIO_0p7_s1: D-24 verdict of s0 FAILED [scf], best validated geometry = g3 (E = -24017.02019226 Ry, lowest of the
  validated geometries 0-3; g4 is the trial whose SCF failed after 200 iterations and was the old-rule relax.in).
- aIO_2p0_s1: D-24 verdict of s0 FAILED [scf], nothing validated (its first SCF, at the input geometry, failed after
  200 iterations, 4 h 58 min).
- State at v2c staging (live check 2026-10-11 ~02:15 CEST): the A15 rescue work replaced relax.in of both chains at
  01:58 CEST (old files kept as relax.in.pre_rescue, inputs in rescue_staging/): Gaussian 0.005 Ry, mixing_beta 0.1,
  electron_maxstep 300, mixing_ndim 12, verbosity 'high'; positions aIO_0p7_s1 = g3 (rows md5 b2ba576b80c5 = the
  D-24 selection), aIO_2p0_s1 = the s0 input (06ba5b09745f). The install therefore arms no transition stop for these
  two chains; the restart is the rescue decision. If either relax.in is put back to the s0 output before the
  install, the chain gets the line and the tool behaves as above (tested on /tmp copies: FAILED [scf], bestvalid =
  independent argmin g3 for aIO_0p7_s1, none for aIO_2p0_s1).

4. Item D: single-H200 benchmark (runs/aIWO_1p0_Al2O3_s2 only)
-------------------------------------------------------------
Change: the idle RELAX job (s0) and relax.sub go from 2 x H100|H200 to 1 x H200 (request_gpus 1,
regexp("H200", TARGET.GPUs_DeviceName) && !regexp("MIG", ...); environment QE_NK=1 kept). Inputs, container (QE 7.3.1
GPU) and tolerances are identical. On this schedd the user requirement lives in the job attribute
PreVerRequirements (Requirements -> PreGPURequirements -> PreAfsRequirements -> PreCvmfsRequirements ->
PreVerRequirements), and the CERN transform sets RequestCpus 22 / RequestMemory 66000 for 1 and 2 GPUs alike, so host
resources do not change. Its steps_relax.sh logs nvidia-smi (timestamp, index, name, memory.used, memory.total,
utilization.gpu) every 120 s into gpumem.log (packed via *.log) and prints the peak into the driver log.
Staged next to it: runs/aIWO_1p0_Al2O3_s2/relax.sub.D24_2gpu = the D-24 relax.sub with the old 2 x H100|H200
request (plus the MIG exclusion), i.e. the revert file.

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

Abort / revert rule. Revert = swap in relax.sub.D24_2gpu (never relax.sub.pre_D24 unless the full section 5
rollback is done: relax.sub.pre_D24 does not transfer geomsel.py, so with the D-24 steps installed every retry
would stop at the preflight and use up the 8 retries):
      cd ~/iwo_amorph/runs/aIWO_1p0_Al2O3_s2 && cp relax.sub relax.sub.D24_1gpu && cp relax.sub.D24_2gpu relax.sub.tmp \
        && mv -f relax.sub.tmp relax.sub
  If the RELAX node job is idle, also: condor_qedit -constraint 'ClusterId == <id> && JobStatus == 1'
  PreVerRequirements back to regexp("H100|H200",TARGET.GPUs_DeviceName) (the install substitution in reverse) and
  RequestGPUs 2 (either order; 1 x H100|H200 and 2 x H200 are both valid intermediate states). If the
  benchmark segment ended FAILED, clear the guard per section 3 (an [infra] FAILED needs no relax.in change).
- REVERT if relax.out or the job .err shows "Out of memory allocating", "cudaErrorMemoryAllocation",
  "cdiaghg_gpu", any other CUDA allocation error, or pw.x ends before the first '!' energy. The D-24 logic marks
  such a segment FAILED [infra] or [early] and arms the guard by itself, so nothing is replayed.
- REVERT if the job is still idle 12 h after the conversion (no H200 slot; the queue gain is gone). At staging all
  16 H200 GPUs (b9pgpun801, b9pgpun802) were claimed.
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
  If the benchmark RELAX job is still idle: condor_qedit it back to regexp("H100|H200",TARGET.GPUs_DeviceName) in
  PreVerRequirements and RequestGPUs 2 (as in section 4).
  Keep common/geomsel.py, segment_guard and segment_stop (empty them): the edited idle ads still transfer them,
  and a missing input file holds the job; they are inert with the old scripts.

6. make_dft.py follow-up (NOT done here: the file belongs to the HfO2 build agent)
---------------------------------------------------------------------------------
New chains written by make_dft.py (e.g. the H-M HfO2 cells) still get the pre-D-24 steps_relax.sh and relax.sub.
Port: steps_relax.sh = runs/<any>/steps_relax.sh.D24 (not the benchmark variant); relax.sub
transfer_input_files += common/geomsel.py, segment_guard, segment_stop, transfer_output_files += segment_guard,
requirements += && !regexp("MIG", TARGET.GPUs_DeviceName); create an empty segment_guard and segment_stop per run.
New DAGs can also get 'RETRY RELAX 8 UNLESS-EXIT 2' with a node script that exits 2 on FAILED (as the pilot); the
stop files then stay as a second line of defence.

7. Files
--------
common/relax_node.sh.D24, common/geomsel.py.D24 (= runs/aIO_0p8_s1/geomsel.py), common/d24_transition.sh,
common/install_D24_BD.sh, common/D24_BD_staged.md5 (staged files as tested), common/D24_BD_baseline.md5 (live files
the staged ones were derived from), runs/<16>/steps_relax.sh.D24, runs/<16>/relax.sub.D24,
runs/aIWO_1p0_Al2O3_s2/relax.sub.D24_2gpu.
