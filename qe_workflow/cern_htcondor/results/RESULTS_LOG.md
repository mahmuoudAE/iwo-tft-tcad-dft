# CERN results log

## 2026-10-05 18:23Z: surface-state check of the relaxed 2 nm slab (slab2r_pdos_cpu, cluster 12834125)

Job: SCF (24 CPUs, 2 pools, 10 h 41 min wall) + planar average + projwfc.x. Analysis script: `surface_state_check.py`. Its measure was defined before the output was read; no protocol criterion existed.

**Result: the band edges are not surface states.** Both are confined, bulk-like states.

| State | Weight on the surface OH groups (H + O bonded to H) | Elements | Profile across the slab (8 slices, bottom → top) |
|---|---|---|---|
| VBM (band 664) | 0.2 % (these atoms are 27.3 % of all atoms) | O 100 % (interior O) | 0.00 0.09 0.17 0.24 0.24 0.17 0.09 0.00 (peaked at the centre, like the lowest confined state) |
| CBM (band 665) | 1.4 % | In 60 %, O 40 % | interior |
| Reference, VBM − 20 bands | 14 % | — | spread out (0.07 at the outer slices) |

**Consequences:**
- The alignment-based split (2 nm: dEc +0.281, dEv −0.054 eV) describes bulk-like band edges.
- The open caveat "whether the VBM is a surface state" is closed for 2 nm.
- The device-relevant dEc never depended on this question.

## 2026-10-05 (local): dEc/dEv partition relative to bulk (campaign item 1.3), two-step alignment

Scripts: bulk_In2O3_protocol/run_bulk_potential.sh and bulk_alignment.py. The intermediate bulk_v11.cube/.pp were deleted on 2026-10-06 because the disk was full; they can be regenerated with the script.

**Method.**
- Bulk: cell average of the pp.x plot_num 11 potential of the relaxed bulk (prefix vcr, a = 10.306 A): <V> = 4.1687 eV. From bands_path.out, E_v - <V> = 3.9098 eV and E_c - <V> = 4.7985 eV.
- Slabs: macroscopic average of the same potential at the slab centre.

**Window.** The planar-average period of bixbyite along [001] is a/2, not a/4.
- With the a/4 window used so far for the vacuum levels, the slab interior oscillates by 177-205 meV. The result (2 nm: dEc +0.157, dEv -0.179 eV) disagrees with the EA/IP route by about 80 meV, so it is rejected.
- The a/2 window gives an interior plateau within 8 meV at 2 nm (1 meV with the double a/2 * a/4 average). At 1 nm the spread is 69 meV.

**Result.** dEg is split exactly (dEc - dEv = dEg in every case).

| Film | Route | dEc (eV) | dEv (eV) | CB share |
|---|---|---|---|---|
| 2 nm | two-step, a/2 window | +0.281 | -0.054 | 0.84 |
| 2 nm | double average | +0.287 | -0.049 | 0.86 |
| 1 nm | two-step, a/2 window | +0.819 | -0.081 | 0.91 |
| 1 nm | EA/IP route (recommended) | +0.848 | -0.056 | 0.94 |

**Checks.**
- The 1 nm film has almost no bulk-like interior. Its recommended values therefore come from the 2 nm two-step result plus the same-termination EA/IP differences (+0.567 / -0.002 eV).
- Between 1 and 2 nm, the two-step route gives dEc +0.538 and dEv -0.027 eV (a/2), or +0.551 and -0.013 eV (double average), against +0.567 and -0.002 eV from EA/IP. They agree within 15-30 meV.

**Caveats.**
- In-plane strain of the slabs relative to bulk: +0.29 % (1 nm) and +0.07 % (2 nm). It is not corrected; it is likely a few meV at 2 nm.
- PBE only.
- Whether the VBM is a surface state is still open (slab2r_pdos_cpu).

**Consequence for TCAD.** V1 assumes dEg = dEc. The computed CB share is about 0.84-0.94, so dEc is about 0.28 eV at 2 nm and about 0.85 eV at 1 nm. The PBE dEg is 0.335 and 0.900 eV.

## 2026-10-05 (12:50Z): 2 nm IWO final SCF lost to a faulty stuck rule; recovery job submitted

- **What happened.**
  - iwo_slab2_W24d (relax converged, 28 BFGS steps) ran its final SCF on the CPU (QE 7.5, 33 MPI, 1 pool, conv_thr 1e-9). At 09:21Z it was at iteration 86, about 80-110 s per iteration. The estimated accuracy had stalled at 8e-9 to 1e-8 Ry since about iteration 80, so it might not have reached 1e-9 within electron_maxstep 150.
  - At 09:23Z the watchdog removed it as "STUCK (no SCF iteration after 60 min)". A single status sample read scf_it = 0, and the rule's 60 min counts from the job start.
  - The resubmission it reported is not in the queue. Its fate is NOT DETERMINED FROM AVAILABLE DATA; the condor_history query timed out.
- **Nothing of the relaxation was lost.** relax.out is in iwo_slab2_W24d_checkpoint/ and live_snapshots/. Relaxed structure: structures_v2/relaxed_pbe/slab2r_W24d_relaxed.json. Max displacement 0.43 A (W 0.09 A). W-O 1.866, 1.874, 2.19 A, each twice, mean 1.977 A (W6+).
- **Fix in dft_flow.sh.** A job counts as stuck only after 3 consecutive cycles with scf_it = 0, and the counter resets otherwise. The auto loop was restarted (bsrximyfh), because a running bash loop keeps the old function definitions.
- **Recovery.** iwo_slab2_final_cpu (cluster 12835131; 24 CPUs requested, 33 allocated, 100 GB) runs SCF + planar average + projwfc on the relaxed geometry, without bands.
  - Deviation: conv_thr 1e-8 Ry instead of 1e-9 (5.7e-11 Ry per atom), and mixing_beta 0.1 instead of 0.2.
  - Reason: the 1e-9 SCF stalled, and the eigenvalues and projections need far less precision than 1e-8 Ry.
- **slab2r_pdos_cpu** (cluster 12834125) is running its SCF: 38 iterations at 12:53Z, about 8 min per iteration. The pure 2 nm needed 70 iterations, so the projections are expected around 18-19Z.

## 2026-10-05: CORRECTION of the IWO band assignment; 2 nm IWO relaxed; 2 nm CPU cross-check

**Correction (my analysis error, found today).**
- **The error.** The IWO cells have one occupied band FEWER below the gap than the pure cells. The In PAW set has 4d10 in the valence (5 bands per In); the W set has 5s2 5p6 (4 bands). The earlier analysis took band n_pure (312 in the 1 nm slab) as the IWO valence-band top.
- **projwfc, 1 nm IWO, first k.** Band 311 is O 2p at -2.366 eV (the VB top). Band 312 is the host CB bottom at -0.647 eV (In 5s 0.50, O 2s 0.21). Band 313 is W 5d (0.56) at 0.576 eV. Band 314 is the next host CB level at 0.766 eV.
- **Corrected 1 nm IWO.**
  - E_F is 1.23 eV above the host CB bottom. Band 312 lies below E_F at all k and holds 2 of the 3 donated electrons; about 1 electron sits in the W 5d-derived band.
  - The W level is resonant 1.22 eV above the CB bottom.
  - Gap (VB top to CB bottom) 1.719 eV (pure 1.789). EA 4.069, IP 5.789 eV (pure 3.928 / 5.717).
- **What was wrong before.** The earlier entries reported a "W level 0.19 eV below the CB" and an "unexplained 1.1-1.65 eV vacuum-scale shift". Both were artefacts of the band count.
- **Bulk W24d (80 atoms).** Band 351 is the VB top and band 352 the host CB (In 5s 0.67), 1.76 eV below E_F at the first k. Band 353 (W 5d 0.54) is at E_F. How the electrons divide between the CB and the W band is not determined.
- **Fixed.** analyze_iwo_slab.py (nvb = 311 for IWO); make_dft_figures.py fig_alignment; 13_dft.tex (sections on W in bulk and in the 1 nm film, status table, key result); onepage.tex; CAMPAIGN_PLAN item 2.0 (resolved) and gate G2.

**2 nm IWO (iwo_slab2_W24d, H100 NVL).**
- The relax converged in 28 BFGS steps (16 h 49 min). Final energy -27385.2061874810 Ry. The final SCF on the GPU started at 06:42Z.
- Last SCF of the relax (nvb = 663):
  - Band 664 (host CB1) is 1.238 eV below E_F at Gamma. Band 665 (CB2) is partly filled.
  - The flat bands 666/667 (widths 239/135 meV, presumably W-derived) are at least 0.069 eV above E_F, so just empty.
  - Projections are pending; they need a CPU run.

**2 nm CPU cross-check (slab2r_final_cpu).**
- The SCF (24 CPUs, 9 h 57 min, 70 iterations) gives HOMO/LUMO 0.0474 / 1.2713 eV, a gap of 1.2239 eV, identical to the GPU run. The planar average was done.
- The job was then held for memory in the bands step (-nk 4, 72 GB) after 10.1 h and was not released (watchdog rule).
- The surface-state projection did not run. It needs a new CPU job: scf + projwfc, without bands.

## 2026-10-04 (13:30Z): 2 nm bands finished; mass; chain submitted by hand

- **Job end.** slab2_relax_c2 finished all steps after 182892 s (50.8 h); bands run 8 h 22 min on the GPU, rc 0. Fetched 10:03Z.
- **Mass.** In-plane CB mass of the relaxed 2 nm slab: 0.2064 m0 [100], 0.2059 m0 [110] (fit |k| <= 0.05 1/A, 4 points, same as 1 nm). Increment over bulk (0.159): +0.047 m0. Lin et al. p. 21540: 0.23 m0 (increment 0.06 from rounded values). Ours is 10 % lower (6 % at 1 nm). No criterion was set for the mass.
- **Sub-band spacing at Gamma.** Next empty level 0.719 eV above the CBM (1 nm: 1.499 eV).
- **Against the V1 laws at 2.02 nm.** dEg 0.335 vs 0.348 eV (-4 %); dm* 0.047 vs 0.049 m0 (-3 %). At 0.99 nm: 0.900 vs 0.933 eV, 0.122 vs 0.133 m0.
- **Chain failure.** The chain slab2_relax fired but failed: `wsl.exe: cannot execute binary file: Exec format error`. Windows interop does not work inside the WSL distro "Ubuntu", where the automation now runs. The three steps were run by hand: the structure build and generate in Ubuntu-22.04, then submit from Ubuntu. Cluster 12827176: slab2r_final_cpu (16 CPUs, 72 GB), iwo_slab2_W24d (1 GPU, 100 GB) and its CPU twin.
- **Fix in analyze_slabs.py.** A missing "Total force" no longer aborts collect_results.py. This affected HSE runs without forces.
- **Report.** 13_dft.tex now has the 2 nm results. Figures updated: confinement, levels, alignment, Lin parity. The PDF has 403 pages.

## 2026-10-04: relaxed 2 nm slab (slab2_relax_c2, H100 NVL; read from the live snapshot, bands still running)

**Relaxation.** The vc-relax converged: 70 BFGS steps, 72 SCF cycles, 41.5 h wall time.
- Final enthalpy: -27035.66548 Ry.
- Total force: 0.0072 Ry/bohr.
- In-plane cell: 10.318 x 10.309 A.
- Thickness: H to H 19.62 A, O to O 18.21 A.

**Final SCF.** The final SCF ran on the GPU in 56 min. The density was converted with dat2h5.py, and the planar average ran (first production use; it worked).

**Band edges.**
- Gap: 1.2239 eV. Bulk gap 0.8887 eV, so **dEg(2 nm) = +0.335 eV**. Lin et al.: +0.33 eV at 1.98 nm, so criterion 7 is met. The V1 law gives 0.348 eV at 2.02 nm.
- EA = 4.495 eV, IP = 5.719 eV. The vacuum plateau is flat.

**Partition between 1 and 2 nm** (same termination; the 1 nm values come from slab1r_final_cpu with the same read-out):
- dEc(1) - dEc(2) = EA(2) - EA(1) = +0.567 eV.
- dEv(1) - dEv(2) = IP(1) - IP(2) = -0.002 eV.
- The sum, +0.565 eV, equals dEg(1) - dEg(2).
- So the whole 1 -> 2 nm change of the gap is in the conduction band.

**Open checks.**
- Is the VBM a surface (O-H) state? That would also make the IP thickness-independent; to be checked with a projection.
- The partition relative to bulk needs the two-step alignment (plan item 1.3).
- The mass comes from the bands run, which is running.
## 2026-10-03: cause of the missing checkpoints found; laptop-side snapshots added

- **Running job.** slab2_relax_c2 (H100 NVL) is at 40 BFGS steps after 23 h. Its CPU twin had done 2 steps and was removed by the upgrade rule.
- **The job's Kerberos ticket was not renewed.** Inside the job (condor_ssh_to_job), the ticket is valid from 10/02 04:41 to 10/03 05:41 CEST, renewable until 10/07, yet it was never renewed. A test xrdcp to EOS from the job failed with "[3010] ... unauthorized identity used: Permission denied". The same copy from the author's lxplus session succeeds. EOS checkpoints of jobs running longer than about 25 h therefore fail silently. This is the most likely reason why slab2_relax_x1 left no checkpoint; it is plausible, not proven for that job.
- **Safety net.** `cern_htcondor/snapshot_jobs.sh` copies the text outputs of the running 2 nm job to `results/live_snapshots/<job>/` every 15 min, through the author's session. An interrupted relaxation can continue from its last geometry, because qeio.py newgeom reads the last printed geometry.
## 2026-10-02: 2 nm relaxation lost after convergence; re-run submitted

**What happened.** slab2_relax_x1 (cluster 12788377, 1 x H100 NVL, 8 CPUs, 32 GB) finished its vc-relax: 68 BFGS steps, last energy change below 0.2 mRy per step. The gap at the last steps was 1.22 eV, about +0.33 eV above bulk; this is provisional and not used. The following final SCF (occupied + 16 bands, verbosity high) needed 65.9 GB. The vc-relax itself had run at 31.4 GB. The job was held for memory (code 34). A held job's working directory is deleted, and no EOS checkpoint of this job exists, so the relaxed geometry is lost. The held job was removed before the watchdog could release it, because a release would have restarted it from its first step.

**Why no checkpoint.** NOT DETERMINED FROM AVAILABLE DATA. The driver copies to EOS after every step and checkpoints of other GPU jobs exist. A possible cause is that the job's stored credentials expired before the copy, but this was not verified.

**Fixes.**
- dft_flow.sh: the memory in jobs.txt is now a floor for every allocation, including FORCE_GPU.
- dft_flow.sh: memory-held jobs that ran for more than 1 h are no longer released; they are reported for a resubmission from their checkpoint.
- make_jobs.py: 2 nm jobs now request 100 GB on GPU and 72 GB on 16 CPUs, and the CPU final run uses at most 2 pools.

**Re-run.** slab2_relax_c2 (cluster 12806569) uses the same input as slab2_relax_x1 (the same starting geometry), 100 GB, and the new driver, which converts the GPU density for pp.x. Its own final SCF, planar average and bands therefore give gap, mass, EA and IP. The chain now adds only the CPU final run and the 2 nm IWO slab.
## 2026-10-01: HSE06 check of the PBE confinement (SG15 NC, 80 Ry, PAW-PBE geometries)

| | bulk gap (Gamma) | 1 nm slab gap | dEg |
|---|---|---|---|
| PBE | 0.9204 eV | 1.8068 eV | 0.8864 eV |
| HSE06 (q = 1, ecutfock 160 Ry) | 2.1080 eV | 3.0475 eV | 0.9395 eV |

**Ratio dEg(HSE)/dEg(PBE) = 1.060**, so criterion met (< 10 %) and the PBE confinement is accepted.

**Settings checks.**
- ecutfock 160 vs 320 Ry: bulk HSE gap unchanged (2.1080 eV).
- EXX q = 3x3x3: bulk HSE gap 2.0662 eV (-42 meV). If the slab gap does not shift equally (worst case), the ratio becomes 1.107, so **ratio range 1.06-1.11**.
- NC-PBE dEg (0.886 eV) vs PAW-PBE (0.900 eV): 1.6 % difference.

**Result.** 1 nm dEg = +0.90 eV (PBE, PAW), +0.95-1.00 eV HSE-corrected; Lin et al. +0.94 eV.

## 2026-09-30: 1 nm IWO slab (W on central 24d site; relax on GPU 27 BFGS steps, E = -12238.28910896 Ry)

**Run.** Final SCF, planar average and PDOS on CPU (iwo_slab1_final_cpu). The bands run aborted (Davidson, rc 161), so no mass is available.

**W-O bonds.** 1.880 x 2, 1.907 x 2, 2.212 x 2 A.

**Comparison with the pure relaxed 1 nm slab** (same cell and settings; analyze_iwo_slab.py). Band numbering: nocc = 312 (band indices in the table are 1-based).

| quantity | pure | IWO |
|---|---|---|
| band 313 - band 312 at Gamma | 1.7885 eV | 1.2228 eV |
| E_vac - band 313 | 3.93 eV | 2.85 eV |
| E_F - band 313 | insulating | +0.005 eV |

**Projection** (projwfc, first k-point).
- Band 313 of the IWO slab, at 0.576 eV, is **~56 % W 5d** (W states #62-66).
- Band 314, at 0.766 eV, is delocalized host CB (each atomic component <= 3 %).

**Interpretation (PBE, preliminary).**
- W forms a W-5d-derived state about 0.19 eV below the host CB, and E_F is pinned in it. The 3 donated electrons stay largely at W, so W acts as a localized/deep donor in the 1 nm film.
- This is consistent with the weak moments in bulk (0.6-0.7 muB), and with the inference that W electrons are largely not free carriers in the TFT channel.

**Caveats.**
- One W position, 4.2 % W, PBE (which usually under-localizes).
- **Bulk check (done 2026-09-30).** In the 80-atom cells (4x4x4 SCF, projwfc, first k-point), band 352 (VB top) has 1.5 % W weight, while the bands at and just above E_F carry about half their weight on W 5d:
  - 24d: bands 353-355 have 0.55 / 0.48 / 0.30 W weight; E_F = 10.794 eV.
  - 8b: bands 353-355 have 0.50 / 0.50 / 0.58 W weight; E_F = 10.758 eV.

  **The W-5d character at E_F is therefore a W property (PBE), not a confinement effect.**
- **Next check.** An HSE06 (NC) calculation of the W cell would test the d-state position.
- The large shift of both edges relative to E_vac with W (about 1.1-1.6 eV) needs checking before any use.

## 2026-09-29: relaxed 1 nm slab (slab1_relax_gpu, finished 11:58Z)

**Run.** vc-relax (atoms + in-plane cell) on a GPU: A100 for 54 BFGS steps, after 13 CPU steps.
- Final enthalpy -11888.81122571 Ry.
- Residual force 0.0061 Ry/bohr, which does not meet the 1e-3 criterion. See the note below.
- In-plane cell 10.336 x 10.335 A (bulk 10.306). Lin et al.: 10.26 / 10.36 A.

| quantity | this work | Lin et al. 2022 (p. 21540, 21542) |
|---|---|---|
| gap, relaxed 1 nm slab | 1.7885 eV | 1.88 eV (0.95 nm) |
| **dEg = slab - bulk** | **+0.900 eV** (bulk 0.889 eV) | **+0.94 eV** |
| in-plane CB mass | 0.281 m0 (bulk 0.159) | 0.30 m0 (bulk 0.17) |
| mass increment | +0.122 m0 | +0.13 m0 |

- **Criterion 7: the recipe is reproduced.** dEg agrees with Lin et al. within 0.04 eV (criterion 0.1 eV), and the mass increment within 0.01 m0.
- **Relaxation matters.** The unrelaxed slab opened the gap by only +0.07 eV, so the relaxed value is the one to use.
- **Residual force.** The total force of 0.0061 Ry/bohr is the norm over all 96 atoms. BFGS reported convergence, i.e. the energy and force criteria as QE applies them per component.
- **EA/IP missing.** The planar-average step (CPU pp.x reading the GPU 7.3.1 save) aborted, so EA and IP of the relaxed slab are missing. A CPU SCF of the final geometry with pp.x is needed for the band-edge partition.

## 2026-09-29: IWO bulk complete (iwo_W24d finished 08:57Z; iwo_W8b 2026-09-28 17:10Z)

| quantity | W on 8b | W on 24d |
|---|---|---|
| E relax, 3x3x3 (Ry) | -15496.3476466 | -15496.3666037 |
| E SCF, 4x4x4 (Ry) | -15496.34766084 | -15496.36660308 |
| W-O (A) | 6 x 1.972 | 1.892 x 2, 1.902 x 2, 2.152 x 2 (mean 1.982) |
| spin-polarized, 3x3x3: E (Ry), M | -15496.34931870, 0.74 muB | -15496.36803594, 0.62 muB |
| E(spin) - E(no spin) | -1.67 mRy (-22.7 meV) | -1.43 mRy (-19.5 meV) |

- **Criterion 1 (k-points) is met.**
  - The site preference is dE = E(8b) - E(24d) = +0.2580 eV at 3x3x3 and +0.2577 eV at 4x4x4; the change of 0.3 meV is below 10 meV.
  - Energy changes between the grids are below 1 microRy per atom.
- **Result: W prefers the 24d site by 0.258 eV.** At 600 K (kT = 52 meV), the occupation ratio 24d:8b is 3 exp(4.96), about 430:1, so 8b is practically empty.
- **Criterion 3 (oxidation state).** The mean W-O bond of 1.97-1.98 A matches W6+ (Shannon 1.98 A), not W4+ (2.04 A).
- **Criterion 4 (magnetism) is not met at 3x3x3.** Both sites develop a weak moment (0.6-0.7 muB per cell, about 20 meV lower in energy). Coarse sampling of a degenerate electron gas can produce spurious Stoner moments, so this is **preliminary**; a spin-polarized check at 4x4x4 is needed before any claim.
- The PDOS (W 5d versus CBM) is in `iwo_W24d/pdos`; its analysis is pending.

## 2026-09-29: slab2_relax_gpu1 removed

Cluster 12759807 was removed by CERN's SYSTEM_PERIODIC_REMOVE ("disk usage exceeded") at 05:58Z. The job's memory use stayed at about 156 MB for about 12 h, so pw.x never reached the SCF. No step finished, so no checkpoint exists. It was resubmitted as cluster 12772910, with an inspection after 12 min to find the cause.

## 2026-09-28 notes
- **slab2_v25 lost.** Removed at the 24 h wall-time limit during its CG bands step: a single k-point outran the 30 min max_seconds margin, and the job ended without a results tarball. It is not resubmitted; slab2_relax (running since about 09:00Z, Davidson bands, 7-day limit) supersedes it.
- **W site (preliminary).** The relax outputs were copied from the running jobs into `iwo_*_partial/`. At the 3x3x3 k-point grid, both cells relaxed and BFGS converged.
  - Final energies: E(W8b) = -15496.3476466 Ry, E(W24d) = -15496.3666037 Ry.
  - **dE = E(8b) - E(24d) = +0.01896 Ry = +0.258 eV**, so W prefers the 24d site.
  - The protocol k-point check (4x4x4) for W24d is still running.
- **SSH master lost at 12:06Z.** Jobs continue at CERN; the user's re-login is needed to fetch results. (read-out with analyze_slabs.py; criteria in ../PROTOCOL_CERN.md)

## slab1_v35: 1 nm slab, unrelaxed, 35 A vacuum (cluster 12756318, finished 2026-09-27T04:16Z)

**Run:** 16 CPUs, 4 pools. SCF 1 h 48 min wall (77 iterations); bands 1 h 29 min.
- 8 symmetry operations (with inversion); 4 irreducible k-points.

**Band edges:**
- VBM -1.9695 eV, CBM -1.0109 eV, so the KS gap is 0.959 eV.
- E_vac = 2.422 eV; the vacuum plateau is flat to < 0.01 meV.
- EA = 3.433 eV, IP = 4.392 eV.

**Status: preliminary, not a confinement value.**
- The geometry is unrelaxed. The total force is 0.27 Ry/bohr, dominated by the H atoms placed at a fixed 0.97 A.
- Lin et al. report 1.88 eV for their relaxed 0.95 nm slab. The unrelaxed gap is far below this and close to the bulk PBE gap.
- Possible reason: surface or O-H states at the band edges before relaxation. NOT DETERMINED FROM AVAILABLE DATA; decided by slab1_relax.
- The bulk reference gap at a = 10.306 A comes from stage 3.
- The vacuum test itself (EA and IP versus vacuum size) is valid at fixed geometry. It is completed when v15 and v25 finish.

## Vacuum convergence: 1 nm slab, unrelaxed (slab1_v15 and v25 finished 2026-09-27 ~23:50Z)

| vacuum | gap (eV) | EA (eV) | IP (eV) | SCF iterations |
|---|---|---|---|---|
| 15 A | 0.9586 | 3.4331 | 4.3917 | 46 |
| 25 A | 0.9586 | 3.4332 | 4.3918 | 64 |
| 35 A | 0.9586 | 3.4332 | 4.3918 | 77 |

**Criterion 6 (changes < 10 meV) is met by a wide margin:** changes are at most 0.1 meV. This is expected, because the slab is centrosymmetric and non-polar, so it carries no dipole. **25 A (Lin et al.) is confirmed.** The vacuum plateau is flat within 0.01 meV in every case.

**Cost note.** With CG diagonalization, the bands step took 13.7-13.9 h on 16 CPUs, against 1.5 h with Davidson for slab1_v35, which gave no failure. Davidson was therefore restored for the bands step of slab2_relax, which had not started. The jobs already running keep CG, and their max_seconds guard stops a bands run cleanly before the wall-time limit.
