# cpu_relax_snapshots

**Purpose.** Snapshots of the CPU vc-relax of slab1_relax and slab2_relax taken before the GPU continuations.

Folder `cern_htcondor/results/cpu_relax_snapshots`; data `runs_sep_oct/out/cpu_relax_snapshots.json` (+ `cpu_relax_snapshots_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| slab1_relax_vcrelax.out | 690230 | 04679d12ee427684 | loose | pw_out |
| slab2_relax_vcrelax.out | 429936 | fd09f113acc8578c | loose | pw_out |

## Resources and run history

- HTCondor: no entry in status_history.jsonl (it starts 2026-09-28T14:19Z).

**What failed and why (from the files above).** Non-fatal: the CPU vc-relax printed UCX errors at start (bnxt_re0: ibv_create_cq failed; uct_iface_open failed) and then ran; the snapshots stop mid-run (no JOB DONE) because the GPU continuations superseded them.

## Calculation `slab1_relax_vcrelax.out` (scf/relax)

QE v.7.5 started 27Sep2026 16:36:25; 16 MPI x 1 threads on 1 node(s); pools 4; R&G division 4; node memory 122054.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: NO (no JOB DONE); terminated None; PWSCF time None; output lines 13631.
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4757  a.u.; unit-cell volume = 24997.2915 (a.u.)^3; number of atoms/cell = 96; number of atomic types = 3; number of electrons = 624.00; number of Kohn-Sham states = 320; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; energy convergence thresh. = 1.0E-04; force convergence thresh. = 1.0E-03; press convergence thresh. = 5.0E-01; Exchange-correlation = SLA  PW   PBX  PBC; nstep = 300; celldm = [19.475688, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  5713967 G-vectors     FFT dimensions: ( 150, 150, 500) / Smooth grid:  2020553 G-vectors     FFT dimensions: ( 108, 108, 360)
- RAM (pw.x estimate): {'Estimated max dynamical RAM per process': '3.79 GB', 'Estimated total dynamical RAM': '56.51 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     623.9105, renormalised to     624.0000', 'Starting wfcs are  432 randomized atomic wfcs']

**Convergence** (15 SCF + BFGS):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 72 | 7.9e-10 | -11888.29270282 | -11888.2927028213 | 0.04921 | 0.0157 | 0.265845 | 4.8e-05 | -3.08 | 3708.16153 | 10.3121, 10.3110 | 0.05136 |
| 1 | 42 | 5.1e-10 | -11888.34222222 | -11888.3422222219 | 0.02968 | 0.0109 | 0.184703 | 0.000132 | -4.08 | 3718.12866 | 10.3271, 10.3237 | 0.08006 |
| 2 | 58 | 2.7e-10 | -11888.38374683 | -11888.3837468303 | 0.02114 | 0.00905 | 0.153566 | 4.1e-05 | -1.48 | 3724.69688 | 10.3366, 10.3325 | 0.03886 |
| 3 | 36 | 2.1e-10 | -11888.40488977 | -11888.4048897742 | 0.02141 | 0.00772 | 0.130981 | 4.2e-05 | -2.42 | 3732.15759 | 10.3471, 10.3426 | 0.04278 |
| 4 | 35 | 9.6e-11 | -11888.42557007 | -11888.4255700702 | 0.01776 | 0.00679 | 0.115174 | 2.3e-05 | -3.09 | 3742.6102 | 10.3617, 10.3570 | 0.06423 |
| 5 | 38 | 1.2e-10 | -11888.44896637 | -11888.4489663689 | 0.01306 | 0.00612 | 0.103869 | 1.8e-05 | -3.91 | 3756.84726 | 10.3809, 10.3772 | 0.09646 |
| 6 | 37 | 4.7e-11 | -11888.46937619 | -11888.46937619 | 0.01654 | 0.00691 | 0.117232 | 2.7e-05 | -4.91 | 3761.80835 | 10.3872, 10.3846 | 0.04783 |
| 7 | 38 | 5.9e-11 | -11888.47934136 | -11888.4793413561 | 0.01602 | 0.00625 | 0.106068 | 3.2e-05 | -4.96 | 3764.35149 | 10.3891, 10.3897 | 0.07917 |
| 8 | 48 | 3.4e-11 | -11888.49473128 | -11888.4947312836 | 0.01287 | 0.0046 | 0.077997 | 1e-05 | -4.35 | 3759.9845 | 10.3818, 10.3850 | 0.0627 |
| 9 | 43 | 6.8e-11 | -11888.50609379 | -11888.5060937908 | 0.01179 | 0.00469 | 0.079627 | 2.8e-05 | -3.35 | 3752.27089 | 10.3700, 10.3754 | 0.05791 |
| 10 | 38 | 1.1e-10 | -11888.51474754 | -11888.5147475398 | 0.01159 | 0.00434 | 0.073678 | 2.5e-05 | -2.2 | 3742.79952 | 10.3562, 10.3630 | 0.05418 |
| 11 | 33 | 3.9e-11 | -11888.52299753 | -11888.5229975349 | 0.01454 | 0.00451 | 0.076491 | 1.7e-05 | -0.82 | 3731.37836 | 10.3400, 10.3476 | 0.08289 |
| 12 | 45 | 1.2e-10 | -11888.53345838 | -11888.5334583805 | 0.01314 | 0.0049 | 0.083154 | 4.1e-05 | 1.08 | 3726.9117 | 10.3343, 10.3410 | 0.06534 |
| 13 | 39 | 5.9e-11 | -11888.54170682 | -11888.5417068187 | 0.01121 | 0.00447 | 0.075858 | 2.3e-05 | 2.44 | 3731.73026 | 10.3418, 10.3468 | 0.06288 |
| 14 | 34 | None | None |  |  |  |  |  |  |  |  |  |

**Final energies** (last SCF): negative_rho = [0.00196, 0.0]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 320, "n_occ": 312, "VBM_eV": -1.6226, "VBM_k_index": 3, "CBM_eV": 0.0496, "CBM_k_index": 0, "gap_eV": 1.6722, "direct_gap_min_eV": 1.6727, "direct_gap_k_index": 0, "gap_type": "indirect", "VB_width_top_band_eV": 0.0217, "CB_width_bottom_band_eV": 0.8789, "E2_minus_E1_at_k0_eV": 1.2025}

**Warnings/errors**: message_from_routine x1 (first: line 317 'Message from routine setup:'); c_bands_not_converged x3 (first: line 884 'c_bands:  1 eigenvalues not converged'); error x32 (first: line 1 '[1790519785.584810] [b9p06p3387:212  :0]        ib_iface.c:1376 UCX  ERROR bnxt_re0: ibv_c'); discouraged x1 (first: line 318 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 314 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized'); ucx_error x32 (first: line 1 '[1790519785.584810] [b9p06p3387:212  :0]        ib_iface.c:1376 UCX  ERROR bnxt_re0: ibv_c')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Calculation `slab2_relax_vcrelax.out` (scf/relax)

QE v.7.5 started 29Sep2026 14:11:22; 32 MPI x 1 threads on 1 node(s); pools 2; R&G division 16; node memory 642658.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: NO (no JOB DONE); terminated None; PWSCF time None; output lines 6484.
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4757  a.u.; unit-cell volume = 32384.4670 (a.u.)^3; number of atoms/cell = 176; number of atomic types = 3; number of electrons = 1328.00; number of Kohn-Sham states = 672; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; energy convergence thresh. = 1.0E-04; force convergence thresh. = 1.0E-03; press convergence thresh. = 5.0E-01; Exchange-correlation = SLA  PW   PBX  PBC; nstep = 300; celldm = [19.475688, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  7403139 G-vectors     FFT dimensions: ( 150, 150, 648) / Smooth grid:  2617449 G-vectors     FFT dimensions: ( 108, 108, 480)
- RAM (pw.x estimate): {'Estimated max dynamical RAM per process': '3.09 GB', 'Estimated total dynamical RAM': '97.03 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge    1327.7914, renormalised to    1328.0000', 'Starting wfcs are  912 randomized atomic wfcs']

**Convergence** (4 SCF + BFGS):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 86 | 7.3e-10 | -27035.14864497 | -27035.1486449703 | 0.04928 | 0.0116 | 0.26585 | 0.000129 | -2.28 | 4802.99625 | 10.3109, 10.3101 | 0.05136 |
| 1 | 54 | 4.4e-10 | -27035.19809269 | -27035.1980926942 | 0.02968 | 0.00807 | 0.185349 | 7.5e-05 | -3.29 | 4812.6606 | 10.3221, 10.3196 | 0.08049 |
| 2 | 88 | 2.6e-10 | -27035.23976791 | -27035.2397679134 | 0.02112 | 0.00685 | 0.157302 | 4.3e-05 | -1.79 | 4817.97704 | 10.3281, 10.3251 | 0.03934 |
| 3 | 30 | None | None |  |  |  |  |  |  |  |  |  |

**Final energies** (last SCF): negative_rho = [0.002145, 0.0]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 672, "n_occ": 664, "VBM_eV": 0.8408, "VBM_k_index": 0, "CBM_eV": 1.9472, "CBM_k_index": 0, "gap_eV": 1.1064, "direct_gap_min_eV": 1.1064, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.0151, "CB_width_bottom_band_eV": 1.0923, "E2_minus_E1_at_k0_eV": 0.6374}

**Warnings/errors**: message_from_routine x1 (first: line 1021 'Message from routine setup:'); c_bands_not_converged x8 (first: line 1635 'c_bands:  1 eigenvalues not converged'); discouraged x1 (first: line 1022 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 1018 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Checks against RESULTS_LOG

| quantity | re-derived | logged | reference | status |
|---|---|---|---|---|
| CPU BFGS steps before the GPU (slab1) | 13 | 13 | RESULTS_LOG.md:645 | match |
