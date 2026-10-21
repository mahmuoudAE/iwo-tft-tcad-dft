# CERN results log

## 2026-10-21 01:18Z: A58 tier-B force check (6 bulk frames, cluster 13035943): aIWO_bulk FAIL on the W first shell, aIO_bulk PASS (claim C044)

Line numbers: this entry adds 6 lines above the earlier entries; their original line N is now N + 6.

- **Jobs.** 13035943.0-.5, QE 7.5 CPU, unchanged val_node.sh / steps_val.sh, ML_VALIDATION settings (60/480 Ry, MV 0.01 Ry, k 2x2x2, conv_thr 1e-7), accepted ranks 1 / 11 / 21 of aIWO_bulk and aIO_bulk at the final MACE geometry; all return value 0. Frozen compare_val.py 4ae21f15; output compare_val_A58_B.json af07dfad.
- **Result.** aIWO_bulk FAIL: RMSE_W1 0.497 / 0.590 / 0.520 eV/A (limit 0.25), RMSE_all 0.128-0.148, MAE 0.063-0.067. aIO_bulk PASS: RMSE_all 0.062-0.079, MAE 0.048-0.061 eV/A. Forces only; amorphous MACE-quenched bulk cells at MACE geometries; PBE PAW, spin-unpolarised; tier B ran after the A66 window (A69).

## 2026-10-19 15:50Z: A58 force check (MACE-MPA-0 vs DFT forces, 18 thin-cell frames, cluster 13015772): aIWO thin types FAIL on the W first shell, aIO thin types INCOMPLETE (claim C043)

Line numbers: this entry adds 9 lines above the earlier entries; their original line N is now N + 9.

- **Jobs.** 13015772.0-.17, QE 7.5 CPU (D-96 route), unchanged val_node.sh / steps_val.sh, ML_VALIDATION settings (60/480 Ry, Marzari-Vanderbilt 0.01 Ry, k 2x2x1, conv_thr 1e-7, default nbnd), accepted ranks 1 / 11 / 21 of each type at the final MACE geometry; all return value 0, 2026-10-19 07:15-15:45Z. Frozen comparator compare_val.py 4ae21f15 (python -I), output compare_val_A58_T.json 77208b39; exit 3 (INCOMPLETE overall).
- **aIWO_0p7 / aIWO_0p8 / aIWO_1p0: FAIL.** RMSE_W1 (W + O within 2.60 A, 6-7 atoms) 0.504-1.026, 0.589-0.645, 0.613-1.032 eV/A (limit 0.25); RMSE_all 0.137-0.255, MAE 0.075-0.130 eV/A; no frame above RMSE_all 0.30 (not DIAGNOSTIC_ONLY).
- **aIO_0p7 / aIO_0p8 / aIO_1p0: INCOMPLETE.** Two computed frames each, all within the limits (RMSE_all 0.084-0.132, MAE 0.064-0.100 eV/A; no W). Not scored (SCF not converged at the val settings: R1 / R3 / R5): aIO_0p7_k01, aIO_0p8_k21, aIO_1p0_k01; no registered retry exists for val frames.
- **Caveats.** Forces only; PBE PAW, spin-unpolarised; amorphous MACE-quenched OH/H-terminated slabs at MACE geometries (not DFT-relaxed, not crystalline). Same W-first-shell failure as the 2026-10-12 force check (C037).

## 2026-10-19 10:22Z: A58 R0 CPU-vs-CPU repeat (crystalline 1 nm IWO slab), cluster 13016026: the registered R0 projection check is not met by the CPU route against itself (diagnostic, D-106)

Line numbers: this entry adds 20 lines above the 2026-10-19 07:41Z entry; its original line N is now N + 20.

- **Run.** 13016026.0 used the CPU QE 7.5 route with the same template (283b29b7) as R0 CPU 12986008, on 24 MPI ranks instead of 42. It ran on b9p34p1014 and returned 0 with A58_STATUS CONVERGED. pw.x took 2 h 13 m wall and the steps 8109 s. All D-24 export checks pass. After normal termination the schedd put the job back to idle (LastJobStatus 2, NumJobStarts 1). The outputs were copied to r0_gpufix/cpu_rep_keep_13016026 (tarball sha256 1131bd06...) and the requeued job was removed at 10:24:21Z.
- **Registered r0_compare.py (fce8033b), 13016026 vs 12986008: INCOMPLETE.** E 7.0e-8 Ry, F 3.3e-4 Ry/bohr, EIG 1.60 meV and OCC 5.3e-6 all PASS. All rc7 checks also PASS: class ECB = ECB, delta f_locW 3.1e-6, host edge 1.30 meV, gap 0.11 meV. The 1 meV degenerate clusters differ at 2 k-points, so PROJ/COMPL are not evaluated. This is the same verdict as GPU 13015768 vs CPU 12986008.
- **Matched-group diagnostic (gpufix/pairdiag.py; not the registered rule).** Each cell gives groups / groups with max per-atom |dw| > 1e-3 / max |dw|:

| | GPU 13015768 vs CPU 12986008 | CPU 13016026 vs CPU 12986008 | GPU 13015768 vs CPU 13016026 |
|---|---|---|---|
| r0_compare 1 meV cluster mismatch (k-points) | 4 | 2 | 2 |
| EIG max abs / mean shift (meV) | 1.39 / +1.15 | 1.59 / +1.40 | 0.42 / -0.25 |
| 1 meV groups | 1548 / 429 / 0.0426 | 1550 / 363 / 0.0356 | 1550 / 73 / 0.0107 |
| 5 meV groups | 1259 / 200 / 0.0125 | 1259 / 145 / 0.0106 | 1260 / 7 / 0.0035 |
| 10 meV groups | 1009 / 56 / 0.0055 | 1010 / 43 / 0.0048 | 1010 / 10 / 0.0017 |
| 50 meV groups | 348 / 0 / 0.0007 | 348 / 0 / 0.0006 | 349 / 0 / 0.0002 |

- **Reading.** The per-atom weight differences at 1 meV grouping (0.043 GPU-CPU) are of the same size between two CPU runs (0.036). They are run-to-run mixing within near-degenerate In 4d semicore manifolds, not a GPU effect. The GPU run agrees more closely with the CPU repeat (0.011) than the two CPU runs agree with each other. The frozen R0 PROJ rule (1 meV clusters, 1e-3) is not met by the registered CPU route against itself. The A58 gate is unchanged (no gate change; decision for the main session / user).
- **Caveats.** PBE PAW, spin-unpolarised, Gaussian 0.001 Ry. Crystalline 1 nm (001) slab, OH/H-terminated; route diagnostic only, no physics claim. Two CPU runs and one fixed-route GPU run: the spread is measured from one pair per route.

## 2026-10-19 07:41Z: A58 GPU route fix, R0 re-test (crystalline 1 nm IWO slab), cluster 13015768: post-processing fixed; registered r0_compare INCOMPLETE

Line numbers: this entry adds 10 lines above the 2026-10-18 21:08Z entry; its original line N is now N + 10.

- **Cause of the R0 GPU POSTPROC (12986006).** QE 7.3.1 (GPU container) writes data-file-schema.xml in the QEXSD 23.03.10 layout: `wf_collected` and `num_of_atomic_wfc` are children of `<band_structure>`. QE 7.5 (QEXSD 25.05.21) reads `wf_collected` from `<output><convergence_info>` and `num_of_atomic_wfc` from an attribute of `<output><atomic_structure>`. On the 7.3.1 file, QE 7.5 projwfc.x printed "Wavefunctions not in collected format?!?" and stopped with "Cannot project on zero atomic wavefunctions!", so atomic_proj.xml and the projection tables were missing. The wfc2h5 conversion itself was correct (5/5 files).
- **Fix.** wfc2h5.py v2 (sha256 5548d0b2...) copies the two values unchanged into the QE 7.5 places. It adds one line and one attribute and removes nothing. The wavefunction code is byte-identical to v1. Physics settings are unchanged. Local QE 7.5 test (toy In-O slab with dipole correction): the 7.3.1-layout XML reproduces both errors; after the XML step, atomic_proj.xml, 11 PDOS files, the planar average and the projwfc/pp printouts are identical to the native 7.5 save.
- **R0 GPU re-test, 13015768.0.** Ran on 1 x H100 NVL, b9pgpun501, 24 CPUs. A58_STATUS CONVERGED. pw.x took 24 m 20 s wall and the whole job 1616 s. Peak host memory 17090 MB, peak GPU memory 25694 MB. D-24 export checks: electron_count PASS, proj_atoms PASS (96/96), projection_consistency PASS (0.000500). 5 files went to EOS.
- **Registered r0_compare.py (fce8033b) against R0 CPU 12986008: INCOMPLETE (exit 3).** E 1.18e-6 Ry, F 4.6e-4 Ry/bohr, EIG 1.38 meV and OCC 1.8e-5 all PASS. rc7 `cell --source table` also PASS: class ECB = ECB; delta f_ext 7e-106, f_locW 1.2e-5, f_W5d 1.9e-5; host edge 1.05 meV, valence edge 1.18 meV, host gap 0.12 meV, E_F - edge 0.12 meV. **PROJ/COMPL are not evaluated** because the 1 meV degenerate clusters differ at 4 k-points. At k1, k4 and k5, band splittings sit on the 1.000 meV boundary (for example 1.000 vs 1.010 meV). At k3, band 320 lies at the E_F + 1.5 eV window edge, and the GPU eigenvalues sit about 0.9 meV higher than the CPU ones, nearly rigidly. A diagnostic outside the registered rule (union of both runs' groups) shows that the per-atom weights of near-degenerate In 4d semicore manifolds rotate between runs. Max |dw| is 0.043 with 1 meV groups (429/1548 groups above 1e-3), 0.0055 at 10 meV and 0.0007 at 50 meV (0 above 1e-3). The GPU route is therefore **not R0-qualified** under the frozen gate. A58 stays on the CPU route (A64) unless a logged decision changes the gate.
- **Caveats.** PBE PAW, spin-unpolarised, Gaussian 0.001 Ry. Crystalline 1 nm (001) slab with OH/H termination; the study cells are amorphous. Route qualification only, no physics claim.

## 2026-10-18 21:08Z: A58 ensemble (amorphous MACE-quench sensitivity), stage 1 outcomes and stage 2 submission (route change to CPU, D-96 / register A64)

Line numbers: this entry adds 10 lines above the 2026-10-14 entries; their original line N is now N + 10.

- **R0 CPU, crystalline 1 nm IWO slab (96 atoms, A26 FINAL template, nbnd 407, k 3x3x1), cluster 12986008.0, QE 7.5 CPU, 42 CPUs granted:** A58_STATUS CONVERGED, rc 0, pw.x 1 h 1 m wall, steps 3785 s, peak 28057 MB; D-24 export checks: electron_count_check PASS (625.000000 of 625), proj_atoms_check PASS (96/96 atoms), projection_consistency PASS (max |psi2 projwfc - atomic_proj| 0.000500); 5 export files on EOS. COMPUTED (route qualification only; no physics claim).
- **R0 GPU, same slab, cluster 12986006.0, QE 7.3.1 GPU container pw.x:** SCF rc 0, post-processing FAILED (A58_STATUS POSTPROC: atomic_proj / proj_atoms missing, projection_consistency FAIL): the GPU save does not yet feed the QE 7.5 CPU projwfc.x through wfc2h5. GPU route withdrawn (D-96); the GPU-vs-CPU comparison is not run.
- **MACE pilot, cluster 12986010.0 (13 samples, MACE-MPA-0, GPU):** ens_pilot_report.py PASS (13/13 built, median 478.4 s per sample). MACE QC only: 2 PASS, 10 FAIL on vacuum gap only (accepted by rule), 1 FAIL on an O-O contact; the repeated seed does not reproduce (RMS displacement 5.93 A; GPU float32 nondeterminism).
- **Submitted 2026-10-18T21:08:23Z, idle:** production MACE tier T round 1, cluster 13015586 (36 GPU jobs, 216 samples); bridge single points on QE 7.5 CPU (registered seeds' own MACE geometries, 0.7 / 0.8 / 1.0 nm aIWO and aIO), cluster 13015587.0-.5 (42 CPUs / 126000 MB granted, MaxRuntime 43200). Outputs are sealed (blind until the D-43 release). The 180-sample ensemble DFT is not submitted: the 18 Oct 22:00Z last-submission date applies and its MACE geometries do not exist yet.
- **Caveats for any later A58 number:** PBE PAW, spin-unpolarised, Gaussian 0.001 Ry; amorphous MACE-MPA-0 melt-quench networks at MACE geometries (not DFT-relaxed); OH/H-terminated vacuum slabs; QE 7.5 CPU throughout.

## 2026-10-14 (local): band structures, electron and hole masses, gaps vs thickness and TCAD-ready parameters of the crystalline DFT cells (read-only re-derivation, no new run; claims C039, C040)

**Scope.** Re-derived from the raw pw.x / projwfc outputs (analysis files local: qe_workflow/analysis_2026-10-13_full/bands_masses, BANDS_MASSES.md with b01-b05 scripts, JSON and figures BM1-BM9; not yet in the repository). No amorphous output was opened. Codex review (work chat 2026-10-14T07:57Z and 08:48Z, both CONCERN) with its wording corrections applied. User go 2026-10-14.

Line numbers: this entry sits above the 2026-10-14 errata entry; original line N of the entries before 2026-10-14 is now line N + 130 (the errata entry's "add 72" refers to the file before this entry).

**Source runs (job ids).**
- Bulk In2O3, local WSL runs: bulk_In2O3_protocol/bands_gamma.out (Gamma + 10 points along [100], [110], [111]), bands_path.out (G-H-N-G-P-H|P-N), vcrelax_ecut71_k3.out, scf_ecut71_k4.out.
- Slabs: slab2_relax_c2 (12806569.0), slab1r_final_cpu (12783163.0; GPU twin slab1_relax_gpu 12759677.0), slabL1_relax_v2 / slabL2_relax_v2 (12835386.0 / .2); unrelaxed vacuum checks slab1_v15/v25/v35.
- W cells: iwo_W8b / iwo_W24d (12756948.0 / .1), iwo_slab1_final_cpu (12790248.0), iwo_slab2_final_cpu (12835211.0).
- HSE06 (SG15 NC, 80 Ry): nc_pbe_bulk_e80 (12790233.0), nc_hse_bulk_e80 (12790233.2), nc_hse_bulk_q3_f160_e80 (12790513.1), nc_pbe_slab1_e80 (12790233.3), nc_hse_slab1_f160_e80 (12790513.2).
- H-L parent In32O48 (80-atom cell; relax 12886359 and its k4 FINAL, see the 2026-10-13 H-L entry): dispersion and valence-DOS check only.

**Electrons (PBE, COMPUTED unless labelled).**
- Bulk band-edge mass (10-point Kane fit) 0.1541 m0, isotropic within 0.2 %; Kane alpha 0.58 1/eV (0.55-0.63). The deck basis (4 points incl. Gamma, free intercept) gives 0.1588 m0; anchored parabolas grow from 0.156 (25 meV window) to 0.189 m0 (450 meV).
- Bulk gap 0.8887 eV, indirect by 4.4 meV (VBM at 0.2 G-H, 0.122 1/A); direct gap at Gamma 0.8931 eV.
- Slabs (H-H 0.461 / 0.695 / 0.930 / 1.962 nm): in-plane 2-D DOS band-edge masses 0.443 / 0.337 / 0.279 / 0.203 m0; alpha 0.24 / 0.31 / 0.36 / 0.47 1/eV.
- FITTED dm = 0.1145 t^-1.2755 (fit3, band-edge basis). The quoted sigma is residual scatter only, with one residual degree of freedom; it excludes functional, termination, thickness-definition and polar-field errors.
- Checks: GPU vs CPU agree within 0.0006 m0; vacuum 15 / 25 / 35 A agree within 0.0002 m0; relaxation raises the 1 nm mass by 18 %.
- W (3.1 %, bulk): host-CB band-edge mass 0.162 m0 (+5 %). W slabs: ESTIMATED only, +6.5 % (1 nm) and +7.5 % (2 nm), from the SCF grid (no band run).
- HSE06: ESTIMATED by a calibrated 3-point Kane fit on SCF grids. The estimates suggest a bulk mass of 0.159-0.193 m0 and a 1 nm mass of 0.283-0.293 m0; the range is a model sensitivity, not an uncertainty bound. The HSE confinement increment is unresolved.

**Gaps and laws.**
- r = dEg(HSE)/dEg(PBE) = 1.060 / 1.107. HSE-corrected Eg: 2.44-2.46 eV at 2 nm, 3.06 eV at 1 nm (ASSUMED r rule).
- dEg fit3 = 0.8147 t^-1.3155 (equal to V3).
- dEc: the primary fit without the polar 0.695 nm point is fit2, p = 1.478. dEc(6.3 nm) spans 0.050-0.075 eV over the fit options.
- -dEv: no power law (0.052 / 0.054 eV at 0.93 / 1.96 nm).

**TCAD.**
- The C10 decks are reproduced to <= 0.11 meV in Eg and affinity, 0.0002 m0 in m* and 0.1 % in Nc.
- Not in the decks: the Kane alpha (+5.7 % Nc 3-D, +2.5 % quasi-2-D) and the HSE r factor in dEg (+6 to +11 %).
- The tunnelling (out-of-plane / evanescent) mass is not computed (ASSUMED in any use).
- W level 1.2-1.8 eV above E_C at the DFT filling. "Fully ionised" holds only if the level stays high at device density (INFERRED).
- OH slabs have no gap states.

**Holes (PBE).**
- **No single band-edge hole mass.** The bulk VB top is 3-fold degenerate at Gamma (bands 174-176) with a camel back. Off-Gamma maxima: +4.44 meV at 0.122 1/A along <100> (global VBM; longitudinal mass 4.03 +- 0.14 m0) and +1.62 meV at 0.175 1/A along <110> (17.8 m0). All lie far below kT.
- **Directional curvature masses near Gamma** (windows 2-10 points; COMPUTED, primary result):
  - band 174: 3.2-3.3 [100], 4.3-4.6 [110], 7.2-7.9 [111] m0;
  - band 175: 6.9-8.9 [100], 8.7-19.8 [110], 7.2-7.9 [111] m0;
  - band 176: rises along [100] and [110] (negative masses) and is unresolved or flat along [111].
- **Angular averages** (ESTIMATED diagnostic under an untested 3-direction cubic-harmonic model, no transport significance): 4.4-4.6 m0 (band 174) and 7.9-11.0 m0 (band 175).
- **Valence DOS.** Boltzmann integral of the grid DOS (window-saturated by 0.2-0.3 eV; k-mesh convergence not established): N_V(300 K) = 1.6-2.7e21 cm^-3 over four grids and two VBM references. That gives m_h,DOS = (N_V / 2.5094e19)^(2/3) = 16-22 m0; the 80-atom k4 grid gives 1.93e21 cm^-3 and 18.1 m0. HSE06 on the k3 grid gives 0.71-0.93 times the PBE m_h,DOS. The deck NV300 = 1e19 (ASSUMED) implies 0.54 m0.
- **Slabs.** Only the 0.75 nm slab gives a resolved local curvature: 5.9 [100] / 3.3 [110] m0. That is an OH-derived band in a polar slab, with the next band 29 meV lower (Boltzmann factor 0.32), so it is not a single-band transport mass.
  - 0.51 nm: Gamma masses 1.14 / 2.04 m0, but a second maximum on the grid lies 1.3 meV higher.
  - 1 nm and 2 nm: the top two bands are within 3.3 and 9.3 meV.
  - Quasi-3-D N_V 1.8-2.9e21 cm^-3.
  - W slabs: chord masses only (SCF grid).
- **TCAD impact.** The decks run carriers=1 electrons. With the computed N_V, n_i at 2 nm rises from 5.0e-10 to 6.7e-9 cm^-3, and the equilibrium SRH generation bound is 3.4e-3 cm^-3 s^-1. The hole emission rate is evaluated only at the centre of the E_C - 0.6 eV Gaussian: 4e-34 s^-1, with ASSUMED capture parameters; it is not a bound on the whole Gaussian or on field-assisted emission. A constant NV300 = 2e21 at every thickness would be ASSUMED (informed by the COMPUTED crystalline values); the frozen C10 parameters keep 1e19.
- **Self-trapping.** Hybrid-functional work predicts that holes self-trap in In2O3 (Varley et al., PRB 85, 081109(R), 2012). N_V is a free-hole band integral, not a hole-transport description.

**Caveats.**
- PBE, crystalline (001) slabs with one OH termination. The device films are amorphous or nanocrystalline.
- 0.51 nm is In8(OH)24, outside every law.
- 0.695 nm is polar without dipole correction.
- Coarse k-grids for every DOS quantity.
- Proposed runs, with costs, are in BANDS_MASSES.md Section 6. Codex priority: the dipole-corrected 0.75 nm SCF first; dense-k N_V only if a claim depends on it.

## 2026-10-14 (local): errata to the entries of 2026-10-04, 2026-10-05 and 2026-10-12 (original lines kept unchanged)

Found in the read-only re-derivation of the crystalline DFT outputs (qe_workflow/analysis_2026-10-13_full, local). Codex GO: work chat 2026-10-13T10:23Z (item 1) and 2026-10-13T22:06Z (items 2-4); item 5 is wording only. User go 2026-10-14. Only the 1 nm dEv of item 1 changes a number; no deck, law or verdict uses it. Line numbers below are those of the entries before this insertion (add 72 for the current file).

1. **Sign of the 1 nm dEv (EA/IP route): lines 363, 366-367 and 440-441.**
   - Line 440 says dEv(1) - dEv(2) = IP(1) - IP(2) = -0.002 eV. With the same termination, a lower VBM raises the IP. So dEv(1) - dEv(2) = -(IP(1) - IP(2)) = IP(2) - IP(1) = **+0.002 eV** (+0.0019; IP 5.7170 eV at 1 nm, 5.7189 eV at 2 nm).
   - Line 441: the gap change is the **difference** of the edge shifts, dEg(1) - dEg(2) = [dEc(1) - dEc(2)] - [dEv(1) - dEv(2)] = 0.567 - 0.002 = +0.565 eV (0.5665 - 0.0019 = 0.5646). The value is right; the word "sum" is wrong.
   - Line 363: the recommended 1 nm dEv (EA/IP route) is **-0.052 eV** (-0.0521), not -0.056. dEc +0.848 eV and the CB share 0.94 are unchanged. Now dEc - dEv = 0.8477 + 0.0521 = 0.8998 eV = dEg(1) exactly; the logged pair gave 0.904.
   - Lines 366-367: "+0.567 / -0.002 eV" are EA(2) - EA(1) and IP(1) - IP(2). The dEv difference they imply is +0.002 eV, so line 367's "+0.567 and -0.002 eV from EA/IP" should read "+0.567 and +0.002 eV". The agreement statement still holds: the two-step dEv differences -0.027 eV (a/2) and -0.013 eV (double average) differ from +0.002 eV by 29 and 15 meV.
   - Code: bulk_In2O3_protocol/bulk_alignment.py line 105 used `v2 - 0.0019`. It now uses `v2 + 0.0019`, with a comment pointing here. The two printed "IP route" reference labels now read +0.0019.
   - Rerun 2026-10-14: bulk_v11.cube was regenerated locally with pp.x (same &INPUTPP/&PLOT settings as pp_bulk_v11.in, prefix vcr) and deleted again afterwards; <V> = 4.1687 eV is reproduced. The only changed number is the 1 nm dEv, -0.0559 -> -0.0521 eV. All other printed values are identical.
   - TCAD: none. dEv is used by no deck, dEc is unchanged, and analysis_2026-10-10_campaign/dft_inputs.json already has -0.052 eV (dEv = dEc - dEg).
2. **Cluster of the 2 nm IWO recovery job: line 384.**
   - Cluster 12835131 (jobs/gen_iwoslab2final/cluster_20261005_125042.txt) is the attempt that stopped after 60 s with "Error in routine mp_start_pools (1): invalid number of pools": 33 MPI ranks cannot be split into -nk 2 (results/iwo_slab2_final_cpu_failed_pools/scf.out:43-44).
   - The SCF, planar average and projwfc used everywhere (2 nm W-slab projections, C022) come from the rerun with -nk 1: **cluster 12835211** (jobs/gen_iwoslab2final/cluster_20261005_162023.txt; results/iwo_slab2_final_cpu/; PWSCF 8 h 05 min wall, conv_thr 1e-8, beta 0.1).
   - Both attempts stay in the provenance.
3. **Build used for the 2 nm IWO final SCF: line 403** ("The final SCF on the GPU started at 06:42Z").
   - The job sat on an H100 NVL node (b9pgpun003), and the relax did run on the GPU (QE 7.3.1).
   - steps.sh exports FORCE_CPU=1 before the SCF (results/iwo_slab2_W24d_checkpoint/steps.sh:6). The SCF output is the **QE 7.5 CPU build with 33 MPI ranks** and has no GPU-acceleration line (results/live_snapshots/iwo_slab2_W24d/scf.out:2, :14).
   - Line 379 ("on the CPU (QE 7.5, 33 MPI, 1 pool ...)") is the correct description.
4. **CPUs of slab2r_final_cpu: line 420** ("16 CPUs, 72 GB").
   - HTCondor allocated **24 CPUs** and pw.x ran 24 MPI ranks (results/slab2r_final_cpu_checkpoint/slab2r_final_cpu_driver.log:1; scf.out:14), as line 410 says.
   - The 16 is the requested request_cpus of the submit file (jobs/gen_iwoslab2/jobs.txt:1 through jobs.sub:12 `request_cpus = $(ncpu)`). The CERN pool sized the slot by memory. In the same cluster (12827176), iwo_slab2_W24d requested 8 CPUs and received 33.
5. **W force in the 0.7 nm MACE frame: line 174** ("the W atom feels 1.05 eV/A in DFT against 0.002 in MACE").
   - These numbers are the largest Cartesian components: |F_x| = 1.049 (DFT) and 0.0024 eV/A (MACE).
   - The vector norms are **1.084 eV/A (DFT) and 0.003 eV/A (MACE)**. Source: frame 12884015.7, aIWO_0p7_s1 final, atom 50 (W); recomputed from the scf.out force block and mace_ref.json, forces only.
   - Wording only. RMSE_W1 and all verdicts use components and are unchanged.

## 2026-10-14 (local): 0.51 nm and 0.75 nm slabs logged (slabL1_relax_v2 = cluster 12835386.0, slabL2_relax_v2 = 12835386.2; claim C021) and the filling caveat of C022

**Runs.**
- Each job had 11 CPUs and 1 H100 NVL.
- vc-relax on the GPU (QE 7.3.1): cell_dofree = '2Dxy', forc_conv_thr 1e-3 Ry/bohr, k 3x3x1.
- Then, with the QE 7.5 CPU build (11 MPI ranks): SCF (conv_thr 1e-9), bands (21 k: Gamma + 10 along [100] + 10 along [110]), planar average and projwfc.
- Settings: PBE PAW 71/568 Ry, (001) slabs, 24 H per cell like the 1 and 2 nm films, no dipole correction.
- Finished 2026-10-06T02:30Z (0.51 nm) and 09:58Z (0.75 nm). The numbers below were re-derived on 2026-10-13 from the raw outputs (analysis_2026-10-13_full, f05).

**Results (PBE, COMPUTED).**

| | 0.51 nm (slabL1_relax_v2) | 0.75 nm (slabL2_relax_v2) |
|---|---|---|
| composition | In8O24H24 = In8(OH)24 | In16O36H24 |
| thickness H-H / O-O (nm) | 0.461 / 0.305 | 0.695 / 0.542 |
| in-plane cell (A) | 10.696 x 10.019 | 10.428 x 10.293 |
| symmetry operations | 8 | 4 |
| relax (vcrelax.out) | 82 BFGS steps (line 55348), max force component 5.4e-4 Ry/bohr | 78 BFGS steps (line 65346), 9.9e-4 Ry/bohr |
| gap, HOMO/LUMO of scf.out | 3.1401 eV (line 1389) | 2.1986 eV (line 1771) |
| dEg vs bulk 0.8887 eV | +2.251 eV | +1.310 eV |
| EA / IP (eV) | 3.192 / 6.332 | 3.717 / 5.916 (mean vacuum level; polar, see caveats) |
| dEc / dEv (eV; 2 nm two-step + EA/IP differences) | +1.585 / -0.667 | +1.059 / -0.251 |
| in-plane CB mass [100] / [110] (m0; 4-point fit, abs(k) <= 0.045 1/A, as at 1 and 2 nm) | 0.428 / 0.445 | 0.335 / 0.338 |
| E2 - E1 at Gamma (bands.out) | 1.887 eV | 1.815 eV |
| VB-top character (projwfc, k-weighted) | O 2p, 98 % on OH oxygens | O 2p, 75 % on OH oxygens |

**Caveats.**
- **0.51 nm.** The relaxed film is exactly In8(OH)24: all 24 O are bonded to H and every In is six-fold. It is an In(OH)3-like layer, not an oxide film. It stays outside the termination recipe and out of every thickness law.
- **0.75 nm is polar and has no dipole correction.**
  - The vacuum potential has a ramp of -13.6 meV/A, i.e. -347 meV across the vacuum gap. The two vacuum-side plateau means differ by 106 meV, against the 27 meV asymmetry recorded in analysis_2026-10-10_campaign/dft_inputs.json:449.
  - EA, IP and dEc therefore depend on the vacuum reference: dEc(0.695 nm) = 1.059 eV +- 0.17 eV. The +-0.17 eV is half the ramp, an ASSUMED reference-choice sensitivity, not an error bound.
  - The gap does not depend on the vacuum reference, but its sensitivity to the artificial field is untested.
- **Use in fits.** The 0.695 nm point is excluded from any new primary dEc fit until a dipole-corrected SCF exists. That run must check both vacuum plateaus, the gap and the residual forces before deciding whether to re-relax.
- **Frozen laws.** The V3 / C10 fit3 laws (dEc, dEg, dm), which include this point, are kept with this caveat; changing them needs a result-informed amendment. Under the +-0.17 eV sensitivity, fit3 dEc(6.3 nm) ranges 0.053-0.075 eV, partly outside the configured S6 band of 0.046-0.062 eV.
- **Scope.** Crystalline (001) slabs, PBE only (no HSE at these thicknesses), one OH termination. The device films are amorphous or nanocrystalline.

**C022 caveat (W level; Codex-refined wording, 2026-10-13T10:23Z).**
- **Placement near E_F.** In every W cell the W-5d-rich level lies roughly 0.1 eV or less from E_F at Gamma: bulk 8b +0.090, bulk 24d +0.001, 1 nm -0.005, 2 nm +0.103 eV. This does not describe the whole dispersive band. E_F lies 1.2-1.8 eV inside the host CB (3 donated electrons per cell, 1.4e21-3e21 cm^-3).
- **Level positions.** The level lies 1.22 (1 nm), 1.34 (2 nm), 1.76 (bulk 24d) and 1.80 eV (bulk 8b) above the host CB bottom at Gamma. These are COMPUTED at this filling only.
- **What is computed and what is interpreted.** The near-E_F placement is COMPUTED. Pinning of the level by the band filling is an interpretation that would need a density series.
- **W-5d counts.** The counts (0.09-0.43 electrons) are Loewdin projections of occupied above-VB states. They are not the total W charge or a uniquely defined trapped-electron fraction. The MV occupations are numerical smearing weights.
- **Device densities.** That the level stays above E_C at device densities (E_F below E_C) is INFERRED, not computed: PBE only, no HSE for the W cells, no lower-density cell.
- **Sources.** projwfc_iwo_W8b.out, projwfc_iwo_W24d.out, projwfc_iwo_slab1_final_cpu.out and projwfc_iwo_slab2_final_cpu.out (cluster 12835211), each with the Fermi energy of its scf.out.

## 2026-10-13 03:40Z: H-L crystalline oxygen-vacancy test scored (six cells, k3/k4 FINALs) with the A20(ii) smearing sensitivity (12904174.0-.5): H-L UNRESOLVED (ΔE_local significance unresolved; ΔE_dop PASS; A20(i) spin unassessed)

**Question.** Register H-L (A17, with A19, A20 and A28): does W suppress oxygen vacancies in crystalline bixbyite In2O3? μ_O cancels in both registered differences:
- ΔE_local = E(In31WO47, near) − E(In31WO47, far). Prediction: ≥ +0.3 eV.
- ΔE_dop = [E(In31WO47, far) − E(In31WO48)] − [E(In32O47) − E(In32O48)]. Prediction: > +0.05 eV.

A20 adds two rules:
- A k3→k4 change above 10 meV in a registered difference means "unresolved significance". The k4 value is reported and is not adopted automatically as converged. This qualifies the H-L section's "the k4 value is used".
- A sensitivity that shifts a difference by more than 50 meV, or flips a verdict, means "not robust".

**Setup.**
- Cells: the bixbyite conventional cell with a fixed a = 10.3061 Å and W on 24d.
  - Parents In32O48 and In31WO48 have 80 atoms.
  - Vacancy cells In32O47, In31WO47_far, In31WO47_near and In31WO47_near72 have 79 atoms.
  - Electron counts: 704, 705, 698, and 699 for each In31WO47 cell.
- Sites (A19/A20 rule, applied to the H-L-relaxed In31WO48, which took 0 BFGS steps):
  - Registered near is O30 (W–O 1.89194 Å). Its symmetry partner O69 is unsplit. The O72 pair is +0.01043 Å longer, so no TIE.
  - O72 (In31WO47_near72) is the sensitivity.
  - Far is O32. The host order is unchanged.
- Settings (fixed for all six cells):
  - PBE, pslibrary 1.0.0 PAW, 71/568 Ry, Gaussian 0.005 Ry, spin-unpolarised, neutral cells.
  - conv_thr 1e-8, plain mixing β 0.3, electron_maxstep 100.
  - BFGS: nstep 300, forc_conv_thr 1e-3 Ry/bohr, etot_conv_thr 1e-4 Ry.
  - QE 7.3.1 GPU. These energies are never mixed with the stage-4 QE 7.5 energies.
- k-points:
  - Relaxation at k 3x3x3: 6, 10 and 14 irreducible points (In32O48, In31WO48, vacancy cells).
  - FINAL single point at k 4x4x4: 14, 30 and 36 points.
  - A20(ii) single point at k 3x3x3 with Gaussian 0.002 Ry. Its inputs differ from the k4 FINAL inputs only in degauss and K_POINTS (diff: two changed lines per cell).
- Jobs: all ended with normal termination, return value 0. Relaxations were submitted 2026-10-10T19:52Z. Every relaxation and FINAL ended on 2026-10-11, before the 17 Oct 10:00 UTC cutoff. The A20(ii) jobs ran on A100-PCIE-40GB, were submitted 2026-10-12T13:17Z and ended 13:25-17:35Z.

| Cell | Atoms | RELAX (QE BFGS steps) | FINAL k4 | A20(ii) |
|---|---|---|---|---|
| In32O48 | 80 | 12886359 (0) | 12890814 | 12904174.0 |
| In31WO48 | 80 | 12886360 (0) | 12890820 | 12904174.2 |
| In32O47 | 79 | 12886361 (13) | 12890914 | 12904174.1 |
| In31WO47_far (O32) | 79 | 12886364 (16) | 12891120 | 12904174.5 |
| In31WO47_near (O30, registered) | 79 | 12892681 (18; A28 restart 1) | 12894133 | 12904174.3 |
| In31WO47_near72 (O72, sensitivity) | 79 | 12886363 (29) | 12891408 | 12904174.4 |

- A28 history of the registered near cell:
  - Attempt 1 was DAG 12886356. Its RELAX job is 12886362, identified by elimination within the 12886359-64 block. The logs are archived in `vac/In31WO47_near/attempt1/` and were not re-read here. It had three validated SCFs. The SCF at BFGS step 3 did not converge in 100 iterations, and the DAG ended with rescue001.
  - Restart 1 was DAGMan 12892680 / RELAX 12892681, submitted 2026-10-11T13:04Z. It started from geometry 2 (E = −15454.49343800 Ry) with the A19 settings unchanged. Its relax.in differs from far's only in max_seconds.
  - Restart 1 ended 'bfgs converged in 19 scf cycles and 18 bfgs steps', no SCF failed. One SCF took 90 of 100 iterations.
  - The pre-declared fallback (local-TF, β 0.1, maxstep 300, ndim 12) was **not used**.
- Checks:
  - All six relaxations printed 'bfgs converged' with no SCF failure.
  - Every k4 FINAL and every A20(ii) SCF converged. FINAL took 14/24/17/25/21/21 iterations and A20(ii) took 18/23/16/26/24/20, in the order In32O48, In31WO48, In32O47, far, near, near72.
  - The relax '!' energy equals QE's Final energy in each cell (assert < 1e-7 Ry).
- Geometry: **all six cells BOUND** (read-only pass on lxplus 2026-10-13T02:04-02:11Z, re-checked 03:05Z; no energy used as evidence).
  - The canonical sha256 of CELL_PARAMETERS + ATOMIC_POSITIONS (numbers re-printed %.10f) of the relax.out `Begin final coordinates` block, with the relax.in cell, equals that of the k4 FINAL input (vac scf.in and final_results.tar.gz::scf.in) and of the A20(ii) input (a20_g002 scf.in and its results-tarball copy): Δ = 0 in every cell. Hashes (first 16 hex): In32O48 4a38745af874a820, In31WO48 190b69fd7895d167, In32O47 22d5673303e3e6ca, far d1904a6a7e039809, near db53075a4ec265a6, near72 00588209500d4887.
  - The geometry each pw.x run printed in its scf.out header (FINAL, FINAL tarball, A20(ii) tarball) matches to <= 5e-8 crystal (7-decimal print rounding). Same atom count, species order and cell (Δcell = 0) in every input.
  - Starting geometries: each vacancy cell started from its relaxed parent minus one O, with the other atoms within 5e-10 and the order preserved (In32O47 = In32O48 − O17; far = In31WO48 − O32; near = − O30; near72 = − O72). The near restart 1 started from attempt-1 geometry 2 exactly (relax.in.A28 md5 0dbaae02…, as in MANIFEST.md5); attempt 1 started from In31WO48 minus O30 exactly.
  - The archived relax.in files equal the converged geometry by construction (`steps_relax.sh` rewrites relax.in before packing), so they are not cited as evidence.
  - Settings differences: vac scf.in -> a20 scf.in only degauss and K_POINTS; a20 scf.in -> its tarball copy only max_seconds (runtime rewrite by driver.sh).
  - Energy equality (In32O48 and In32O47 reproduce their k3 relax energies to 1e-8 Ry at 0.002 Ry, smearing inactive) is consistent but is not used as identity evidence.
  - Structure note: in the relaxed In32O48 the In-O first shell is 2.1671-2.2561 Å, above the protocol's 2.12-2.21 Å window because the cell is the frozen PBE host (a = 10.3061 Å, ~1.9 % above experiment). Details: `qe_workflow/cern_htcondor/results/evidence_20261013_HL/geometry_binding.md`.
- Input file sha256 values (first 16 hex; relax.in / FINAL scf.in / A20(ii) scf.in), read 2026-10-13 ~02:05Z:

  | Cell | relax.in | FINAL scf.in | A20(ii) scf.in |
  |---|---|---|---|
  | In32O48 | e89421cc96b92580 | a9968110956481ed | 11e2e9030d83df0c |
  | In31WO48 | 3b8b7db5fb65ef84 | 1bd9105027571e3d | 2e7d010f9e9b5c32 |
  | In32O47 | 25a3156ca1494caf | 2bdc62ef2eef85a4 | 5f8ebf81b00b52fe |
  | far | d98ff7b6d8b0771c | 130ddcb1d0fc9476 | 6f593dd5863e57a2 |
  | near | 335e745559fef92d | fc417c04dad8a04b | 24a4cf10a178cbf6 |
  | near72 | 52a3626d246811ac | 6d460182adfe14a0 | c114f167b7c6a469 |

- Analysis:
  - Files read: `~/iwo_amorph/vac/<cell>/{relax.in,relax.out,scf.in,scf.out}`, and the scf.out inside `~/iwo_amorph/checks/gpumax_work/a20_g002/<cell>/a20g002_<cell>_results.tar.gz`.
  - Script `hl_a20ii.py` (sha256 3f5062d9b77a909e20584e9800a8f5828e5b4611f154f7d31ca81f2d4071b4cf) parsed the raw grep `r23.out` (570ece79...) into `hl_a20ii.json` (e356a586...), all archived in `qe_workflow/cern_htcondor/results/evidence_20261013_HL/` (with r23.sh, q1_prov.*, g5_bind.*, geometry_binding.md, the first digest and SHA256SUMS). Conversion: 1 Ry = 13.605693122994 eV. E is the QE '!' total energy, which includes −TS.
  - Label fix after the Codex review: the field holding −TS was named `minus_TS_mRy` but held Ry values. It is now `minus_TS_Ry` (values in Ry, unchanged). The differences are unaffected.

**Result: H-L UNRESOLVED overall.**

| Difference (eV) | k3, G 0.005 | k4, G 0.005 | k3→k4 | k3, G 0.002 | A20(ii) shift | Registered status |
|---|---|---|---|---|---|---|
| ΔE_local, O30 (registered) | +0.5578 | +0.5321 | −25.7 meV | +0.5583 | +0.5 meV | **UNRESOLVED significance** (≥ +0.3 eV; threshold satisfied at both tested meshes; diagnostic wording) |
| ΔE_local, O72 (sensitivity) | +0.6643 | +0.6230 | −41.3 meV | +0.6650 | +0.7 meV | reported only |
| ΔE_dop | +0.7259 | +0.7226 | −3.4 meV | +0.7261 | +0.2 meV | **PASS under registered settings** (> +0.05 eV) |

- Status of each component:
  - **ΔE_local(O30): UNRESOLVED significance.** The k3→k4 change (−25.7 meV) exceeds 10 meV. The k4 value is reported and not adopted as converged. This is not a PASS.
  - **ΔE_dop: PASS under registered settings** (k3, Gaussian 0.005 Ry, spin-unpolarised, neutral). The k3→k4 change is −3.4 meV.
  - **A20(ii): width-robust at k3.** Shifts are +0.5 and +0.2 meV, against the 50 meV rule, and no verdict flips. This says nothing about k4 or spin.
  - **A20(i) spin: UNASSESSED.** It is staged on lxplus (version 2, 12 single-GPU jobs, not submitted). Codex (03:26Z digest): GO-WITH-CHANGES with two comparator fixes required before the comparator is frozen or anything is submitted; submission after the GPU pause. The implementation is result-informed and goes in as a result-informed amendment (proposed A42) with the user's go.
  - **H-L overall: UNRESOLVED.** Do not write "H-L supported".
- Forecasts (not the test): ΔE_local +0.5 to +1.5 eV and ΔE_dop +0.5 to +3 eV. Both registered differences lie inside them at k3 and k4.
- Per-cell k3→k4 (meV): In32O48 −1.7, In31WO48 −3.5, In32O47 +26.8, far +21.6, near −4.1, near72 −19.7.
- Per-cell width shift, G 0.002 − G 0.005 at k3 (meV): In32O48 0.0, In31WO48 +11.7, In32O47 0.0, far +11.9, near +12.4, near72 +12.6.
- −TS (mRy) at k3 G 0.005 / k4 G 0.005 / k3 G 0.002:

  | Cell | k3 G 0.005 | k4 G 0.005 | k3 G 0.002 |
  |---|---|---|---|
  | In32O48 | 0 | 0 | 0 |
  | In31WO48 | −1.857 | −1.596 | −0.400 |
  | In32O47 | −0.0001 | −0.321 | 0 |
  | far | −1.903 | −2.754 | −0.385 |
  | near | −1.811 | −1.560 | −0.494 |
  | near72 | −1.917 | −1.911 | −0.470 |

**Reading.**
- The two differences behave differently under the mesh change:
  - ΔE_local moves by −25.7 meV between meshes. Most of that comes from the far cell (+21.6 meV) against the near cell (−4.1 meV).
  - ΔE_dop moves by only −3.4 meV, because the far (+21.6) and In32O47 (+26.8) shifts largely cancel.
- In32O47 is smearing-inactive at k3 (−TS of 1e-4 mRy) but not at k4 (−0.321 mRy). The sampled occupations of the neutral V_O cell change with the mesh.
- In the four W cells, the width corrections are of similar size (+11.7 to +12.6 meV) and cancel in both differences. This explains why the differences are stable without showing that the individual energies are converged.
- The zero-width estimates F + |TS|/2 agree between the two widths within 1.6-3.5 meV per cell. They are a diagnostic only, not a registered quantity.
- O72 sensitivity:
  - O72 − O30 is +0.1066 eV (k3) and +0.0910 eV (k4). This is arithmetic on the values above.
  - No registered rule applies to the site sensitivity. O30 stays the registered near site under A19/A20.
- Scope of the result: these are neutral-cell differences. Hybrid-functional work (Chatratin et al., Phys. Rev. Materials 3, 074604, 2019) finds:
  - charge-dependent vacancy relaxations;
  - donor transitions near the CBM;
  - functional and k-sampling sensitivity.

  Therefore this result does not establish charge-state thermodynamics and does not isolate a Fermi-level mechanism.
- Next steps:
  - A20(i) first (Codex GO-WITH-CHANGES; comparator fixes first): built and staged (version 2, after two internal reviews), not submitted.
    - Implementation choices are fixed after the H-L differences were seen, and the build discloses that.
    - Seeds, neighbour selection, identical settings and failure handling are frozen before any spin output.
    - The undoped vacancy (In32O47) gets a meaningful seed treatment.
    - Total magnetisation stays free.
    - One start tests one spin branch.
  - k5 on near/far is deferred. If run, it is an optional diagnostic, reported only, and cannot repair the registered label.

**Caveats.**
- PBE (PAW) with neutral cells only: no charged states and no finite-size corrections. PBE has a gap error.
- Spin-unpolarised. In31WO48 (705 e) and the three In31WO47 cells (699 e) have odd electron counts, and A20(i) has not run.
- The cell has 3.125 % W (1 W per 32 cations). The far site is only about 6-8 Å from W and its images, so ΔE_local is a cell-limited estimate.
- ΔE_dop mixes local chemistry, strain, band filling and periodic-image effects. It is not an upper bound on the Fermi-level effect. The doping is far above the TFT channel density.
- Crystalline reference test only. It does not test the amorphous films.
- The Gaussian width is a numerical parameter. A20(ii) covers k3 only.
- Only '!' energies, −TS, convergence lines, k-point and electron counts, and input diffs were read. No amorphous (aIO_*/aIWO_*) quantity was opened.
- Codex review: work chat 2026-10-13T01:51Z, reply received about 02:00Z. Verdict CONCERN; GO-WITH-CHANGES to logging. Codex reproduced the differences from the saved grep. Logging GO on the 03:26Z digest (reply ~03:35Z), after the user's request "analyse the A20(ii) results" (2026-10-13 ~00:25Z).

## 2026-10-12 12:35Z: MACE-MPA-0 force check (ML_VALIDATION.md), six CPU frames (cluster 12884015 procs .0-.4, .7): OVERALL FAIL (W first shell); 2.0 nm frames pending (12890593.0/.1)

**Question.** ML_VALIDATION.md: do MACE-MPA-0 forces on the plan snapshots agree with DFT single-point forces? Limits per scored frame: RMSE_all <= 0.15, MAE_all <= 0.10, RMSE_W1 (W + O within 2.60 A) <= 0.25 eV/A. Melt frames are reported, not scored.

**Setup.**
- Inputs from make_val.py (mace_ref.json and scf.in per frame, written 2026-10-10 12:22Z); DFT atom i = MACE atom i, no reordering, no net-force removal.
- DFT: QE 7.5 CPU, PBE PAW (In Zval 13 with 4d, W Zval 14 with 5s5p, O 6, H 1), 60/480 Ry, Marzari-Vanderbilt 0.01 Ry, spin-unpolarised, conv_thr 1e-7, beta 0.2, -nk 1. k 2x2x2 (bulk, 8 k-points) and 2x2x1 (0.7 nm slab, 27 A cell height, 4 k-points). Unsplit labels.
- Jobs (all exit 0, one start, no hold; 15 CPUs / 46080 MB, the 0.7 nm frame 33 / 101376; peak RSS 16.8-17.3 GiB bulk, 54.2 GiB 0.7 nm):
  - .0 melt_3000K: 18383 s, 31 SCF iterations
  - .1 aIWO quenched: 10759 s, 29 iterations
  - .2 aIWO final: 10099 s, 29 iterations
  - .3 aIO quenched: 11239 s, 30 iterations
  - .4 aIO final: 10516 s, 33 iterations
  - .7 aIWO_0p7 final: 5896 s, 47 iterations
- Comparator compare_val.py v1.0.0, frozen in private-repo commit d0179e1 (sha256 4ae21f15...a58a62d) before any val output was read, run unmodified (python -I), exit 1. No fail rule R1-R12 fired; scf.out geometry agrees with scf.in. An independent stdlib recompute (no import of the comparator) matches RMSE, MAE and RMSE_W1 to 4 decimals.
- Tarball sha256 prefixes: melt b4e4c7f7, aIWO-q 6e780c02, aIWO-f eee14029, aIO-q c1cc3d63, aIO-f 95ea5d18, 0p7-f e7aa2076.

**Result: OVERALL FAIL. aIO bulk PASS; aIWO bulk FAIL on RMSE_W1 only; aIWO 0.7 nm FAIL on all three limits.**

| Frame (job) | Status | RMSE_all | MAE_all | RMSE_W1 | Verdict |
|---|---|---|---|---|---|
| aIWO_bulk_s1 melt_3000K (12884015.0) | REPORTED | 0.311 | 0.171 | 1.108 | - |
| aIWO_bulk_s1 quenched_300K (.1) | SCORED | 0.121 | 0.068 | **0.434** | FAIL |
| aIWO_bulk_s1 final (.2) | SCORED | 0.122 | 0.068 | **0.449** | FAIL |
| aIO_bulk_s1 quenched_300K (.3) | SCORED | 0.068 | 0.052 | N/A | PASS |
| aIO_bulk_s1 final (.4) | SCORED | 0.065 | 0.049 | N/A | PASS |
| aIWO_0p7_s1 final (.7) | SCORED | **0.206** | **0.110** | **0.815** | FAIL |
| aIWO_2p0_s1 slab_annealed / final (12890593.0/.1, A34 GPU route) | MISSING (idle, 0 starts) | - | - | - | - |

All values in eV/A.

- Structures: aIWO_bulk_s1 FAIL, aIO_bulk_s1 PASS, aIWO_2p0_s1 INCOMPLETE, aIWO_0p7_s1 FAIL.
- OVERALL FAIL (rule D7: one failed structure fails the check). The 2.0 nm frames cannot change it.
- Stop rule (aIWO_2p0_s1, RMSE_all > 0.30): UNDETERMINED; one 2.0 nm frame above 0.30 triggers it, clearing it needs both.

**Reading.**
- The error sits in the W first shell. Each cell has one W with 6 O within 2.60 A, so the shell has 7 atoms; it carries 71-75% of the squared force error. The shell failure is driven more by the shell O atoms (RMSE 0.46) than by W itself (0.17 quenched, 0.37 final); in the 0.7 nm final frame the W atom feels 1.05 eV/A in DFT against 0.002 in MACE.
- Outside the shell (arithmetic on the comparator outputs, used in no verdict): RMSE 0.063-0.066 (aIWO bulk) and 0.107 (0.7 nm), against 0.065-0.068 for aIO.
- Final frames are MACE-relaxed (MACE force rms 0.005-0.013 eV/A, small but nonzero), so RMSE_all there approximately equals the component RMS of the DFT residual force at the MACE minimum (DFT-MACE correlation about 0): these frames mainly test how well the MACE equilibrium transfers to DFT. All frames test force agreement; the quenched and melt frames test it over a wide force range (DFT force rms 0.58-2.0 eV/A, correlation 0.98-0.99). (Wording corrected after the Codex review of 2026-10-12T13:15Z.)
- Plan consequence (ML_VALIDATION.md, D-12): production DFT relaxations continue; the ML structures are starting points relaxed by DFT, not validated amorphous models; ML-stage-only structural statistics (coordination, density) are not reported as results.

**Caveats.**
- PBE (PAW), spin-unpolarised, MV 0.01 Ry, QE 7.5 CPU; MACE-MPA-0 forces on MACE snapshots.
- Amorphous melt-quench cells, one sample each, not crystalline. The 0.7 nm cell is a slab (In49 W1 O83 H14) with OH/H termination and vacuum; the bulk cells have no surface.
- RMSE_W1 rests on one W environment per frame (21 force components). The aIWO quenched and final frames share the same W neighbours, so they are not independent.
- Possible contributor to the W-O error (ASSUMED, not tested): the MACE-MPA-0 training data (MPtrj/sAlex) use PBE+U for W oxides, while these SCFs are plain PBE.
- SCF-correction force norm 1.1-1.6e-3 Ry/bohr (about 0.03-0.04 eV/A total) at conv_thr 1e-7.
- Job MemoryUsage values from HTCondor are rounded; peaks above are RSS. Only forces and SCF bookkeeping were read; no energies, projections, gaps or edges.

## 2026-10-12 07:22Z: aIWO_0p8_s2 relaxation segments s0-s2: three SCF failures and restart non-reproducibility at production tolerance (DAG 12884028; jobs 12884030, 12889333, 12893894)

**Question.** The 0.8 nm W-doped slab aIWO_0p8_s2 (an H-N cell) relaxes with Marzari-Vanderbilt smearing 0.01 Ry. How far did its first three segments get, why did each end, and does a fresh restart reproduce the continued SCF at the same geometry? Codex asked for this diagnosis before another attempt (work chat 2026-10-12T00:20Z).

**Setup.**
- Cell: aIWO_0p8_s2 (seed 82, the replacement for the QC-rejected aIWO_0p8_s1). 147 atoms: the amorphous In49 W1 O76 film of the spec (0.8 nm, lateral 14.4338 Å, 10 Å vacuum), with both faces terminated by dissociated water (OH + H pairs, SLAB_PROTOCOL §4). 1163 electrons, nspin 1, 698 bands.
- Settings: PBE PAW (pseudopotential md5 identical in all three segments), 60/480 Ry, 2x2x1 k (4 k-points), dipole correction (tefield/dipfield, edir 3), MV 0.01 Ry, conv_thr 1e-7, BFGS with forc_conv_thr 1e-3 and etot_conv_thr 1e-4. QE 7.3.1 GPU on 1 H100 (1 rank).
- Segments (D-24 steps md5 61b079ad, geomsel.py 5bfbae78):
  - s0, job 12884030: pre-D-24 mixing (beta 0.2, local-TF, 8 history steps, at most 200 iterations).
  - s1, job 12889333: the aids of the 2026-10-11T03:15Z reset (beta 0.1, mixing_ndim 12, at most 300 iterations); starts at s0 g13.
  - s2, job 12893894: the same settings as s1 (the inputs differ only in max_seconds); starts at s1 g10.
- Read: the relax.out of `runs/aIWO_0p8_s2/relax_s{0,1,2}_results.tar.gz` (md5 24423e228fa9d2b1832ba6b543c77f86, 65a855e65ab70ab67bbe7a975c362479, 1fd8de15cd6ecb9bc055d99030645fe2).

**Result 1: three SCF failures, each after converged SCFs. The relaxation is not converged.** F is the QE '!' total energy, which includes -TS.

| Segment (job) | Start | Validated steps (converged SCFs) | F (Ry), first -> last | How it ended |
|---|---|---|---|---|
| s0 (12884030) | s0 input | 14 (g0-g13) | -24364.16185 -> -24364.21122 | SCF at g14 not converged in 200 iterations (accuracy 8.4e-7 to 2.7e-4 Ry after iteration 10). The old steps said CONTINUE; the D-24 re-classification gave FAILED [scf] (2026-10-11T03:14:20Z) |
| s1 (12889333) | s0 g13 | 11 (g0-g10) | -24364.20721 -> -24364.22109 | SCF at g11 not converged in 300 iterations (accuracy 1.8e-5 to 3.2e-4 Ry after iteration 10). FAILED [scf] 2026-10-11T15:42:37Z |
| s2 (12893894) | s1 g10 | 2 (g0-g1) | -24364.22108 -> -24364.22156 | SCF at g2, after a 0.0032 Å step (largest atom move), not converged in 300 iterations (accuracy 8.5e-6 to 1.5e-4 Ry over iterations 11-300). FAILED [scf] 2026-10-12T05:50:37Z |

- Best validated geometry: s2 g1, F = -24364.22155515 Ry. Its largest force component is 4.651e-3 Ry/bohr (largest per-atom force 5.10e-3), above forc_conv_thr (1e-3).
- It is kept as relax_s2_bestvalid.in (md5 7ce25d2602bde39483bd8f45ba9f497a; position-rows md5 e0098124335b by the 03:15Z convention; d24_posmd5 e24b17e60a84).
- Status at 07:06Z: the chain is stopped by its guard (FAILED [scf]). The next retry (12901263, segment s3) is idle with 0 starts.

**Result 2: restart non-reproducibility at production tolerance (conv_thr 1e-7).** "Continued" means the SCF started from the previous BFGS step inside the same pw.x run. "Fresh" means a new pw.x run.
- At fixed geometry and identical settings (s1 g10 -> s2 g0), a fresh MV SCF gave ΔF 1.18e-5 Ry and max |ΔF| 4.99e-3 Ry/bohr.
- Across the s0 -> s1 restart, where the mixing settings also changed (beta 0.2, 8 history steps, 200 iterations -> beta 0.1, mixing_ndim 12, 300 iterations), it gave 4.0e-3 Ry and 2.69e-2 Ry/bohr.

| Quantity | g13: s0 (continued) -> s1 (fresh, mixing changed) | g10: s1 (continued) -> s2 g0 (fresh, same settings) |
|---|---|---|
| ΔF | **+4.01e-3 Ry** | **+1.18e-5 Ry** |
| max \|ΔF\| over 441 force components | **2.69e-2 Ry/bohr** | **4.99e-3 Ry/bohr** |
| Δ internal energy | +9.48 mRy | -1.47 mRy |
| -TS | +5.18 -> -0.30 mRy | -0.21 -> +1.27 mRy |
| Δ Hartree / Δ one-electron | +3.620 / -3.612 Ry | -0.127 / +0.126 Ry |
| Electric-field (dipole) correction energy | 5.18 -> 3.83 mRy | 4.43 -> 4.55 mRy |
| ΔEwald | -5e-8 Ry | +4e-8 Ry |
| Largest force component | 1.01e-2 -> 2.85e-2 Ry/bohr | 5.30e-3 -> 5.51e-3 Ry/bohr |

- **Same geometry, by record.**
  - geomsel.py copies the segment input and replaces only ATOMIC_POSITIONS with the printed coordinates of the selected step. The relaxation is fixed-cell ('relax').
  - The fresh segment's input is that copy of the previous segment's validated geometry. Its position rows (coordinates with species labels) hash equal to the previous segment's bestvalid file: d24_posmd5 aad143fa86fe (s0 bestvalid = s1 input) and 59daedf1ee26 (s1 bestvalid = s2 input). The rows md5 (bb3cd88a6bde, 5a37d5ee3f89) and the xyz-only and raw-row hashes also match.
  - The cell, species and k-point cards are carried from the segment input by that construction. They were not hashed separately. The namelists differ only in max_seconds (s1 -> s2), or in max_seconds and the mixing line (s0 -> s1).
  - The Ewald agreement (within 5e-8 Ry) is consistent with this, but it is not used as the identity test.

**Reading.**
- The observation is restart non-reproducibility at production tolerance. The s1 -> s2 pair has identical settings, so the effect needs no change of settings. That pair would fail A35's restart gate on both tolerances (1e-5 Ry, 1e-3 Ry/bohr).
- Interpretation open:
  - It may be an incomplete-SCF force error at conv_thr 1e-7. QE prints this as the SCF correction to the forces, and those values in the s0-s2 relax.out have not been read yet.
  - It may instead be two distinct converged electronic branches. This is ASSUMED, and so is any dipole mechanism.
  - The SCF-correction forces are to be read before any stronger attribution.
- Supporting numbers for the ASSUMED dipole mechanism: at g13, Hartree moves +3.62 Ry, one-electron -3.61 Ry, and the dipole-correction energy changes. That pair also changed the mixing settings.
- Conditions shared with the cell: odd electron count (1163), spin-unpolarised MV, dipole correction. These are not sufficient on their own: the 1.0 nm W cell, also odd-electron with MV and the dipole correction, reproduced its relax energy to 4e-8 Ry in a fresh single point (entry 2026-10-11 10:41Z).
- Numerical-path invariance cannot be assumed for this cell. Register A28 states it ("This changes the SCF path, not the converged energy beyond conv_thr") for the crystalline H-L cell; this observation does not falsify A28's result there.
- Consequence: this cell's MV force reproducibility across a restart is about 5e-3 Ry/bohr or worse, above forc_conv_thr (1e-3). An MV-against-Gaussian force comparison at 1e-3 Ry/bohr cannot resolve anything for this cell.

**Caveats.**
- PBE (PAW), spin-unpolarised, MV 0.01 Ry. One amorphous melt-quench 0.8 nm W-doped slab with its own OH + H termination. Two fixed-geometry comparisons.
- QE 7.3.1 GPU, the relaxation route. The QE 7.5 CPU FINAL route was not used for any of these numbers.
- The shared conditions are a list, not a tested cause. The SCF-correction force term was not read.
- Sight (A27 rule): only energies, energy components, forces and SCF bookkeeping are used.
  - The diagnosis and check scripts also parsed the relax-SCF Fermi energies of s0-s2. They appear in the review digest (work chat 2026-10-12T07:08Z) but are not used here or for any decision.
  - No projections, PR_n, gaps or edges were read. No FINAL exists for this cell.
- Next: register A35 (Gaussian 0.005 Ry rescue from s2 g1, one attempt, with a final qualification SCF).

## 2026-10-11 13:36Z: A25 split-label force qualification (clusters 12891652 unsplit, 12891653 split): PASS

**Question.** Register A25 runs aIO_2p0_s1 with split species labels (In -> In1/In2, O -> O1/O2) to fit one GPU. Does the split change the energy or the forces? A25 pass rule: |ΔE| ≤ 1e-5 Ry and max |ΔF| ≤ 1e-5 Ry/bohr over all components, split against unsplit at identical geometry and settings.

**Setup.**
- Geometry: aIO_1p0_s1, the best validated geometry of segment s0 (134 atoms, In50 O78 H6). Position rows md5 `e1bfc3f3324a` (frozen copy `source/relax.in.aIO_1p0_s1`, md5 432f746c...).
- Settings: the A15 relax settings (PBE PAW, 60/480 Ry, 2x2x1 k, dipole correction, Gaussian 0.005 Ry, β 0.1, local-TF, mixing_ndim 12, at most 300 iterations). Changes: calculation 'scf', &IONS dropped, and a check-only conv_thr of 1e-14 Ry in both runs; production uses 1e-7.
  - Why 1e-14: at 1e-7 this cell's Total SCF correction is 1.3e-3 Ry/bohr, far above the tolerance. The SCF correction scales as about 4.5·sqrt(scf accuracy), so 1e-14 is needed to stay below the frozen 1e-6 Ry/bohr noise gate.
- Labels: the production rule, the alternating split of `a25_labels.py` (md5 93caf6fc..., also used for aIO_2p0_s1). In1/In2 25/25, O1/O2 39/39, H 6.
- The two inputs differ only in ntyp, the species card and the 128 In/O row labels. This was re-derived line by line (`verify_inputs.py`); the label-blind rows md5 is `e1bfc3f3324a` in both.
- Inputs: `~/iwo_amorph/checks/A25_split_equiv/{unsplit,split}/scf.in` (md5 ecb07951..., 716b14c5...).
- Runs: one H100 NVL each (QE 7.3.1 GPU, 1 rank, -nk 1), exit 0.
  - Unsplit: b9pgpun002, 45 min, 99 SCF iterations to 7.5e-15 Ry.
  - Split: b9pgpun006, 53 min, 113 iterations to 4.3e-15 Ry. The SCF path differs, but the converged state is the same.
- Comparator `compare_forces.py` v2 (md5 69129a67...) and its outcome classes were frozen before submission. Record: `results_20261011T133634Z/compare_result.txt` (md5 4ad9f7cc...).

**Result: PASS. The split changes neither energy nor forces beyond SCF noise.**

| Quantity | Value |
|---|---|
| E unsplit / split | −23796.88119572 / −23796.88119571 Ry |
| \|ΔE\| | **1e-8 Ry** (tolerance 1e-5) |
| max \|ΔF\| over all 402 components | **3e-8 Ry/bohr** (atom 70, y; tolerance 1e-5) |
| max \|ΔF\| by species | In 2e-8, O 3e-8, H 1e-8 Ry/bohr |
| SCF correction (norm, recomputed from the per-atom block) | unsplit 3.7e-7, split 3.3e-7 Ry/bohr (gate 1e-6; both print 0.000000) |
| Fermi energy | −0.9146 eV in both |

Sanity: the unsplit E is 6e-8 Ry below the first SCF of relax_s1 (job 12890833) at the same geometry and conv_thr 1e-7 (−23796.88119566 Ry).

**GPU memory (diagnostic only; nvidia-smi samples every 2 s, including the CUDA context and the caching pool).**
- SCF phase: unsplit 77.9 GB, split 66.7 GB. This matches QE's RAM estimate: 60.61 GB unsplit, 49.94 GB split.
- Force step: the split rose from 66.7 to 80.6 GB. In the unsplit run the force step stayed inside its 77.9 GB plateau, so its own increment is not visible.
- So at 134 atoms the split lowered the SCF-phase memory, but the split run's overall peak was 2.6 GB higher, set by the force step. This tests nothing about the 268-atom aIO_2p0_s1 force step that A25 is meant to fit.

**Caveats.**
- PBE (PAW), spin-unpolarised. One amorphous melt-quench cell (1.0 nm aIO, its own H termination), one geometry (not the final relaxed one).
- Qualified at conv_thr 1e-14. At the production 1e-7, SCF noise (1.3e-3 Ry/bohr) is many orders larger than the split effect.
- The split was tested on 134 atoms with the rule used for the 268-atom aIO_2p0_s1. No other cell is covered.
- A rollout to other cells still needs its own approval.
- Only energies, forces and SCF bookkeeping were read.

## 2026-10-11 10:41Z: smearing force check on the relaxed 1.0 nm W-doped slab (register A27 C4 screen = A15 force check; clusters 12891104 MV, 12891105 Gaussian)

**Question.** The W-doped slabs were relaxed with Marzari-Vanderbilt smearing 0.01 Ry, the undoped rescue slabs with Gaussian 0.005 Ry. Does that choice move the atoms? Test: at one fixed geometry, compute the forces with both smearings. Frozen rule (A15): if any force component differs by more than 1e-3 Ry/bohr, the smearing choice counts as a geometry uncertainty.

**Setup.**
- Geometry: final coordinates of the converged aIWO_1p0_s1 relax (segment s0, 'bfgs converged in 36 scf cycles and 35 bfgs steps'; 138 atoms, In49 W1 O80 H8). Position rows md5 `b8567368325a6d68a114e15771308e9b` in both inputs, equal to the relax output and the run's relax.in.
- Settings as the relax (PBE PAW, 60/480 Ry, 2x2x1 k, dipole correction, conv_thr 1e-7, beta 0.2 local-TF). The only differences: calculation 'scf', &IONS dropped, and the smearing line.
- Inputs `~/iwo_amorph/checks/A27_C4_smear/{mv,gauss}/scf.in` (md5 e02556f8..., 5644ad23...). Each ran on one H100 NVL (QE 7.3.1 GPU), exit 0.
- Run times: MV 32 min 51 s (68 SCF iterations); Gaussian 40 min 11 s (83 iterations).

**Result: the smearing choice does not move the atoms beyond the threshold.**

| Quantity | Value |
|---|---|
| E(MV) − last relax energy (−24232.38894468 Ry) | +4e-8 Ry (sanity: agrees) |
| max \|ΔF\| over all components, ΔF = F(Gauss) − F(MV) | **2.42e-4 Ry/bohr** (W atom 50, x component) |
| RMS over all 414 components | 6.7e-5 Ry/bohr |
| max per-atom \|ΔF\| | 2.85e-4 Ry/bohr |
| max \|ΔF\| by species | In 2.1e-4, W 2.4e-4, O 2.1e-4, H 5.0e-5 |
| largest residual force (max component) | MV 9.50e-4, Gaussian 9.47e-4 Ry/bohr |
| A15 verdict | max \|ΔF\| ≤ 1e-3 Ry/bohr: **not a geometry uncertainty** |

The largest differences, after W50, are on O111, In3, In41 and O73.

**Caveats.**
- The model is PBE, spin-unpolarised. It is one amorphous melt-quench cell (1.0 nm, its own H termination) at one geometry.
- This is a screen, not a relaxation. Under A27 the Gaussian 0.005 polish of the decisive cells is still required.
- A15's own check names a 2.0 nm geometry; that is not covered here.
- The resolution is set by the SCF tolerance. The MV run's total SCF correction is 1.3e-3 Ry/bohr (norm over all atoms; Gaussian 5.6e-4). An RMS ΔF of 6.7e-5 is at that noise level.
- Read path: the outputs were read from the EOS checkpoints (`a27c4_mv_12891104.tar.gz`, `a27c4_gauss_12891105.tar.gz`; scf.out md5 0f3dc4b4..., ffe1b0ee...) because the lxplus session had lost its AFS token.
- Pending: the official record `collect_c4.sh` (with the relax-force sanity) still has to run on AFS.
- Only energies and forces were read (A27 sight rule).

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
