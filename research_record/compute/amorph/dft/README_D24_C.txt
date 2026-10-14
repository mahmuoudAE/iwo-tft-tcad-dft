D-24 item C: register A14/A16 export of the FINAL SCFs (staging v2, 2026-10-11)
==============================================================================
Staged, NOT installed. v1 (staged 2026-10-10 23:52 CEST) was verified; v2 answers that verification. v1 files:
common/D24_C_backup/v1.pre_D24/. Scope: the 16 slab chains runs/<name>/ and, when named, aIO_bulk_s1 aIWO_bulk_s1 and
the A15 pilot aIO_0p8_s1 (main session's decision). Not vac/ (own node scripts), not final.sub, no queue action.

1. Install (after the user's go, before any FINAL condor_release; refuses while a FINAL runs)
---------------------------------------------------------------------------------------------
    bash ~/iwo_amorph/install_D24.sh                      # dry run
    bash ~/iwo_amorph/install_D24.sh --apply aIO_bulk_s1 aIWO_bulk_s1   [+ aIO_0p8_s1 if the main session decides]
  - common/steps_final.sh and runs/<16>/steps_final.sh <- steps_final.sh.D24 (only from the pre-D-24 sha256 38a423a4)
  - runs/<16>/final.tmpl: verbosity 'low' -> 'high' (one line; scf.out then prints f_nk for every k)
  - common/final_node.sh <- final_node.sh.D24 (only from the pre-D-24 sha256 fb4012a8). Exit 0 only for a converged
    final SCF ('convergence has been achieved', '!' energy, JOB DONE, no 'convergence NOT achieved'); before, JOB DONE
    alone gave 0, also after a non-converged SCF or a max_seconds stop. Exit 1 -> 'RETRY FINAL 1' submits the retry
    through final.sub (hold = True): it waits on hold. Copy runs/<name>/final_results.tar.gz aside before releasing
    it (same file name; the first attempt is also in EOS checkpoints/final_<ClusterId>.tar.gz). A steps_final.sh
    without export_final (the pilot until it is given D-24) keeps the old rule.
  - new: common/export_pull.sh, common/lineage_relax.sh (from their .D24 files)
  Every replaced file keeps a *.pre_D24 copy.

2. What each FINAL writes (steps_final.sh.D24, on the worker)
-------------------------------------------------------------
  Before pw.x: lineage_final.dat (job ad, sha256 of every input, geometry check relax.in = scf.in, as-run scf.in) and
  an EOS write probe (exp/EOS_PROBE, 'EOS write probe' in final_driver.log, line eos_probe in lineage_final.dat).
  After a converged SCF, pp.x and projwfc.x:
  AFS (runs/<name>/final_results.tar.gz), enough for A16 without EOS:
    occ_kw_final.dat        e_nk, f_nk, w_k (normalised, spin factor 2), electron-count check
    proj_atoms_final.dat    every band at every k: Loewdin weight of every atom (orbitals summed; all atoms, H and
                            oxide included) and the 5d weight of every W atom, units of 1e-6, with f_nk, w_k,
                            completeness and PR_n. Regions, PR_n, N_v accounting and W-5d fractions follow from it
                            and the geometry in scf.in.
    projwfc_map_final.dat, projwfc_states_final.dat, pdos_species_final.dat, final_avg.dat, export_checks_final.dat,
    export_manifest_final.dat (first lines: '# export complete' | '# export INCOMPLETE: ...' | '# LOST with the
    sandbox: ...' | '# export NONE: the final SCF did not converge'), inputs, logs.
  EOS (/eos/user/m/melrashe/qe/exports/<name>/final_<ClusterId>/, sha256 MANIFEST): atomic_proj.xml.gz,
    data-file-schema.xml.gz, projwfc_final.out.gz, pdos_atoms.tar.gz, final_small.tar.gz, and for the 2.0 nm cells
    save_nowfc.tar.gz (charge density). EOS calls have timeouts; after a timeout or past the driver deadline the
    remaining in-job copies are skipped (SKIPPED).
  If an EOS copy fails: exp/EXPORT_PENDING, and the job waits up to 6 h (never past its deadline + 1 h) for the
  puller (section 3). Without a pull, the per-atom PDOS and the full projwfc output go into the AFS tarball; the complex
  projections and the charge density are lost, and the manifest says so. (Keeping save_nowfc on AFS instead was not
  done: ~150-185 MB per 2.0 nm cell against the 2 GB AFS quota, and a quota overflow holds jobs and loses sandboxes.)

3. The puller: common/export_pull.sh (lxplus, every 15 min)
------------------------------------------------------------
  For each RUNNING FINAL (IWOJob *_final, not val_*): one condor_ssh_to_job read of exp/EOS_PROBE, exp/EXPORT_PENDING
  and exp/EXPORT_PULLED; pending files are streamed to EOS, sha256-checked, then it writes exp/EXPORT_PULLED into the
  sandbox (its only write into a job; the job then finishes). A FAILED probe is logged once per job. Never condor_rm /
  release / qedit. Log: ~/iwo_amorph/logs/export_pull.log. Exit 3 = no Kerberos ticket, 4 = condor_q failed.
  Run it from the laptop loop next to snapshot_jobs.sh, through the ControlMaster:
      ssh -o BatchMode=yes -o ControlMaster=no -o ControlPath=$HOME/.ssh/cm-cern melrashe@lxplus.cern.ch \
          'bash ~/iwo_amorph/common/export_pull.sh' </dev/null
  and, so that a laptop or ControlMaster outage longer than the 6 h wait does not lose an export, also from acron.
  Staged acrontab line (NOT installed; acron needs the user's own CERN credential setup, which only the user does):
      */15 * * * * lxplus.cern.ch bash /afs/cern.ch/user/m/melrashe/iwo_amorph/common/export_pull.sh > /dev/null 2>&1
  Two pullers at once are harmless (each file is sha256-checked; EXPORT_PULLED is written by rename).

4. Rollback
-----------
  cd ~/iwo_amorph
  for f in common/steps_final.sh common/final_node.sh runs/*/steps_final.sh runs/*/final.tmpl; do
    [ -f "$f.pre_D24" ] && cp -p "$f.pre_D24" "$f"; done
  rm -f common/export_pull.sh common/lineage_relax.sh     (and remove the acrontab line if one was added)
  A FINAL already running keeps the files it started with.

5. v2 against v1 (verification of 2026-10-11)
---------------------------------------------
  - export_pull.sh: condor_ssh_to_job (ssh without -n) swallowed the job list from the loop's stdin, so only the first
    running FINAL was ever checked. Now ssh_job has </dev/null and the list comes on fd 3. Tested with 3 running fake
    finals (the first without EXPORT_PENDING): v1 checked only the first, v2 pulled the other two in the same round.
  - proj_atoms_final.dat on AFS (above); EOS write probe at job start; puller from acron (staged line).
  - final_node.sh.D24 (exit code follows SCF convergence).
  - lineage_relax.sh: as-run input of every segment (item-B relax_s<seg>_input.in, else the EOS checkpoint), item-B
    lineage.log / geomsel selection as the validated step, chain check, only CONVERGED/CONTINUE segments can be the
    writer of relax.in (a stopped segment packs it unchanged), --to-eos also copies the EOS checkpoints.
  - every EOS call in steps_final.sh has a timeout; skipped after a hang or past the deadline.

6. Not changed here (main session's decisions, before any release)
------------------------------------------------------------------
  - final.sub request_memory 100 GB / request_disk 60 GB for every cell (126-414 atoms) look too small (QE estimates:
    ~115 to >200 GB RAM, 46-74 GB wavefunctions); a held job loses its sandbox. See TODO_D24_make_dft.md section 3.
  - the pilot aIO_0p8_s1: install_D24.sh --apply aIO_0p8_s1 gives it the export and the new exit rule.
  - a short real 1-CPU job on a small H-containing cell would prove the batch EOS write and the real
    condor_ssh_to_job pull end to end (needs the user's go).
