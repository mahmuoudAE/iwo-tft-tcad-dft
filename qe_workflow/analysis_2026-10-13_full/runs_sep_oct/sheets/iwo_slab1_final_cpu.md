# iwo_slab1_final_cpu

**Purpose.** CPU final SCF, planar average, projwfc/PDOS and bands of the relaxed 1 nm IWO slab.

Folder `cern_htcondor/results/iwo_slab1_final_cpu`; data `runs_sep_oct/out/iwo_slab1_final_cpu.json` (+ `iwo_slab1_final_cpu_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| avg_iwo_slab1_final_cpu.in | 45 | 805e67c60e895831 | loose | avg_in |
| avg_iwo_slab1_final_cpu.out | 1314 | 2abb434ba8be584f | loose | avg_out |
| bands.in | 8514 | 84581614b11a0fe2 | loose | pw_in |
| bands.out | 28061 | c7aa0b00f756c46e | loose | pw_out |
| iwo_slab1_final_cpu_avg.dat | 138000 | 99eadb10dc2f630c | loose | avg_dat |
| iwo_slab1_final_cpu_driver.log | 659 | 2b7a1126332138c1 | loose | driver |
| pp_iwo_slab1_final_cpu.in | 100 | c2f4820f637ea26b | loose | post_in |
| pp_iwo_slab1_final_cpu.out | 2450 | a39e3bc2ea839297 | loose | pp_out |
| projwfc_iwo_slab1_final_cpu.in | 162 | ecff82fe610596e0 | loose | post_in |
| projwfc_iwo_slab1_final_cpu.out | 2643018 | ccea85d2a846d54a | loose | projwfc_out |
| scf.in | 7706 | 078ca3269b785193 | loose | pw_in |
| scf.out | 150442 | a543d0ac5922f7bd | loose | pw_out |
| steps.sh | 264 | 94a2c8d67eb63320 | loose | steps |

Tarball `iwo_slab1_final_cpu_results.tar.gz` (2648866 B, sha256 a3a5e9bf4ac84754): 208 members; identical to the loose copy: 13; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 195

PDOS set `pdos`: 195 files.

## Resources and run history

- `iwo_slab1_final_cpu_driver.log`: host b9p22p5620.cern.ch, 16 CPUs, wall limit 86400 s, GPU: none (CPU), job total 13531 s, start 2026-09-30T17:35:47Z
  - step scf: -nk 1, max_seconds 84590, start 2026-09-30T17:35:57Z, end 2026-09-30T20:31:58Z, rc 0, PWSCF        :      2h42m CPU      2h55m WALL
  - step bands: -nk 1, max_seconds 73950, start 2026-09-30T20:33:17Z, end 2026-09-30T21:21:17Z, rc 161, 
  - log: [2026-09-30T20:32:26Z] planar average iwo_slab1_final_cpu: 3000 lines
  - log: [2026-09-30T20:33:16Z] pdos iwo_slab1_final_cpu: 195 files
- HTCondor iwo_slab1_final_cpu 12790248.0: 16 CPUs, 0 GPU; seen 2026-09-30T17:27:16Z to 2026-09-30T21:19:00Z (42 samples); states {'1': 2, '2': 40} (1 idle, 2 running, 3 removed, 5 held); max scf_it 60, max BFGS 0; steps ['scf', 'bands']; hw  ['AMD EPYC 7302 16-Core Processor']
- `steps.sh`: `steps() { clean_tmp export FORCE_CPU=1 # one QE version (CPU 7.5) for SCF, pp.x and projwfc.x; one pool (NCPU may be odd) run_pw scf 1 || return 0 run_ppavg slab "$JOB" 4.8833 run_pdos slab "$JOB" "$(python qeio.py fermi scf.out)" 1 run_pw bands 1 }`

**What failed and why (from the files above).** SCF, planar average and projwfc completed; the bands step (Davidson) aborted with "Error in routine cdiaghg (417): problems computing cholesky" (bands.out line 480: factorisation of the computed overlap matrix failed; underlying cause unresolved, not evidence of a defective geometry or pseudopotential) and MPI_ABORT (rc 161). No in-plane mass for the W slab.

## Calculation `bands.out` (bands)

QE v.7.5 started 30Sep2026 22:33:17; 16 MPI x 1 threads on 1 node(s); pools 1; R&G division 16; node memory 50041.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: NO (no JOB DONE); terminated None; PWSCF time None; output lines 499.

**Input settings** (every namelist variable):

- &CONTROL: calculation = bands, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 73950
- &SYSTEM: ibrav = 0, nat = 96, ntyp = 4, ecutwfc = 71, ecutrho = 568, occupations = smearing, smearing = mv, degauss = 0.01, nbnd = 336
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "W", "mass": 183.84, "pseudo": "W.pbe-spn-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.33643106, 0.0, 0.0], [0.0, 10.33450421, 0.0], [0.0, 0.0, 34.87453893]]}
- K_POINTS: {"mode": "tpiba", "n": 21, "points_first_last": [[0.0, 0.0, 0.0, 1.0], [0.17448858, 0.17448858, 0.0, 1.0]], "path_points": [[0.0, 0.0, 0.0, 1.0], [0.02467641, 0.0, 0.0, 1.0], [0.04935282, 0.0, 0.0, 1.0], [0.07402923, 0.0, 0.0, 1.0], [0.09870565, 0.0, 0.0, 1.0], [0.12338206, 0.0, 0.0, 1.0], [0.14805847, 0.0, 0.0, 1.0], [0.17273488, 0.0, 0.0, 1.0], [0.19741129, 0.0, 0.0, 1.0], [0.2220877, 0.0, 0.0, 
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 96, "labels": ["H", "In", "O", "W"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.5330  a.u.; unit-cell volume = 25140.0035 (a.u.)^3; number of atoms/cell = 96; number of atomic types = 4; number of electrons = 625.00; number of Kohn-Sham states = 336; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.533024, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); W W.pbe-spn-kjpaw_psl.1.0.0.UPF md5 03c3df5b60893f488392c7401945500a (Projector augmented-wave + core cor, Z 14.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 2 Sym. Ops. (no inversion) found ( 1 have fractional translation); k points: number of k points=    21  Marzari-Vanderbilt smearing, width (Ry)=  0.0100 (sum of weights 2.0); FFT: Dense  grid:  5746731 G-vectors     FFT dimensions: ( 150, 150, 500) / Smooth grid:  2031701 G-vectors     FFT dimensions: ( 108, 108, 360)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '429.52 MB', 'Estimated max dynamical RAM per process': '1.67 GB', 'Estimated total dynamical RAM': '26.75 GB'}; start: ['Starting wfcs are  436 randomized atomic wfcs']
- Band-structure run: {'diag': 'Davidson diagonalization with overlap', 'kpts_done': 2}

**Warnings/errors**: message_from_routine x1 (first: line 34 'Message from routine setup:'); c_bands_not_converged x1 (first: line 474 'c_bands: 58 eigenvalues not converged'); error x3 (first: line 479 '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'); discouraged x1 (first: line 35 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x4 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized'); s_matrix x1 (first: line 481 'problems computing cholesky'); mpi_abort x2 (first: line 486 'MPI_ABORT was invoked on rank 2 in communicator MPI_COMM_WORLD')
- QE/MPI error lines: [[480, 'Error in routine  cdiaghg (417): problems computing cholesky'], [486, 'MPI_ABORT was invoked on rank 2 in communicator MPI_COMM_WORLD'], [490, 'NOTE: invoking MPI_ABORT causes Open MPI to kill all MPI processes.'], [495, 'prterun has exited due to process rank 8 with PID 0 on node b9p22p5620 calling']]
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized']

## Calculation `scf.out` (scf/relax)

QE v.7.5 started 30Sep2026 19:35:58; 16 MPI x 1 threads on 1 node(s); pools 1; R&G division 16; node memory 17109.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: JOB DONE; terminated 22:31:31  30Sep2026; PWSCF time {'cpu': '2h42m', 'wall': '2h55m', 'calls': None}; output lines 2697.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 84590
- &SYSTEM: ibrav = 0, nat = 96, ntyp = 4, ecutwfc = 71, ecutrho = 568, occupations = smearing, smearing = mv, degauss = 0.01, nbnd = 336
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "W", "mass": 183.84, "pseudo": "W.pbe-spn-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.33643106, 0.0, 0.0], [0.0, 10.33450421, 0.0], [0.0, 0.0, 34.87453893]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 96, "labels": ["H", "In", "O", "W"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.5330  a.u.; unit-cell volume = 25140.0035 (a.u.)^3; number of atoms/cell = 96; number of atomic types = 4; number of electrons = 625.00; number of Kohn-Sham states = 336; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.533024, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); W W.pbe-spn-kjpaw_psl.1.0.0.UPF md5 03c3df5b60893f488392c7401945500a (Projector augmented-wave + core cor, Z 14.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 2 Sym. Ops. (no inversion) found ( 1 have fractional translation); k points: number of k points=     4  Marzari-Vanderbilt smearing, width (Ry)=  0.0100 (sum of weights 2.0); FFT: Dense  grid:  5746731 G-vectors     FFT dimensions: ( 150, 150, 500) / Smooth grid:  2031701 G-vectors     FFT dimensions: ( 108, 108, 360)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '766.02 MB', 'Estimated max dynamical RAM per process': '2.59 GB', 'Estimated total dynamical RAM': '41.47 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     624.9136, renormalised to     625.0000', 'Starting wfcs are  436 randomized atomic wfcs']

**Convergence** (1 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 60 | 2.9e-10 | -12238.28910785 |  | 0.000984 | 0.000362 | 0.006148 | 4.4e-05 | 0.93 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.03875, 0.0], E_F_eV = 0.5811, E_Ry = -12238.28910785, E_all_electron_Ry = -310100.465648, acc_final_Ry = 2.9e-10, mTS_Ry = -0.00299457, internal_energy_Ry = -12238.28611328, one_electron_Ry = -78725.20225196, hartree_Ry = 39662.69393129, xc_Ry = -1481.05007885, ewald_Ry = 35641.74619176, paw_one_center_Ry = -7336.47390551, converged_iterations = 60
- stress tensor (kbar): [[1.94, 0.0, 0.26], [0.0, 1.71, 0.0], [0.26, 0.0, -0.87]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 336, "E_F_eV": 0.5811, "bands_fully_below_EF": 312, "bands_crossing_EF_1based": [313], "highest_band_below_EF_max_eV": 0.1547, "lowest_band_above_EF_min_eV": 0.7246}

**Warnings/errors**: message_from_routine x1 (first: line 30 'Message from routine setup:'); c_bands_not_converged x16 (first: line 661 'c_bands:  2 eigenvalues not converged'); ieee x3 (first: line 2695 'Note: The following floating-point exceptions are signalling: IEEE_UNDERFLOW_FLAG IEEE_DEN'); discouraged x1 (first: line 31 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x4 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized']

## Input geometries

- `bands.in`: {"n_atoms": 96, "composition": {"H": 24, "In": 23, "O": 48, "W": 1}, "cell_lengths_A": [10.33643, 10.3345, 34.87454], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3725.3642, "density_g_cm3": 1.6121, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 138, "min": 2.1474, "mean": 2.2379, "max": 2.5581, "std": 0.0788, "CN_In_hist": {"6": 23}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 1.88, "mean": 1.9996, "max": 2.212, "std": 0.1506, "CN_W_hist": {"6": 1}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9727, "mean": 0.9792, "max": 0.9903, "std": 0.0071, "CN_O_hist": {"0": 24, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 24}, "slab": {"vacuum_A": 25.417, "extent_A": 9.458, "thickness_H_H_A": 9.4577, "thickness_O_O_A": 7.9761, "thickness_In_In_A": 5.2733, "thickness_W_W_A": 0.0}}
- `scf.in`: {"n_atoms": 96, "composition": {"H": 24, "In": 23, "O": 48, "W": 1}, "cell_lengths_A": [10.33643, 10.3345, 34.87454], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3725.3642, "density_g_cm3": 1.6121, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 138, "min": 2.1474, "mean": 2.2379, "max": 2.5581, "std": 0.0788, "CN_In_hist": {"6": 23}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 1.88, "mean": 1.9996, "max": 2.212, "std": 0.1506, "CN_W_hist": {"6": 1}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9727, "mean": 0.9792, "max": 0.9903, "std": 0.0071, "CN_O_hist": {"0": 24, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 24}, "slab": {"vacuum_A": 25.417, "extent_A": 9.458, "thickness_H_H_A": 9.4577, "thickness_O_O_A": 7.9761, "thickness_In_In_A": 5.2733, "thickness_W_W_A": 0.0}}

## projwfc `projwfc_iwo_slab1_final_cpu.out`

natomwfc 436, nbnd 336, nkstot 4, states 436, spilling 0.0039, Loewdin total 622.538, PROJWFC      :     45.35s CPU     49.07s WALL, done True

| element | n | total charge mean (min-max) | s | p | d |
|---|---|---|---|---|---|
| In | 23 | 11.8659 (11.8361-11.9212) | 0.7428 | 1.132 | 9.9911 |
| W | 1 | 13.202 (13.202-13.202) | 2.4333 | 6.9467 | 3.8221 |
| O | 48 | 6.7012 (6.5284-6.7324) | 1.7178 | 4.9835 | 0.0 |
| H | 24 | 0.6151 (0.6051-0.6265) | 0.6151 | 0.0 | 0.0 |

## PDOS `pdos`

{"n_files": 195, "E_window_eV": [-7.419, 3.701], "dE_eV": 0.01, "integral_dos_window": 302.955, "integral_dos_below_EF_or_VBM": 256.119, "reference_energy_eV": 0.5811}

| element, l | files | states in window | states below reference |
|---|---|---|---|
| H s | 24 | 6.082 | 3.549 |
| In d | 23 | 3.198 | 3.152 |
| In p | 23 | 21.645 | 15.716 |
| In s | 23 | 24.443 | 10.883 |
| O p | 48 | 222.764 | 211.334 |
| O s | 48 | 9.924 | 5.953 |
| W d | 1 | 6.546 | 3.042 |
| W p | 2 | 0.666 | 0.466 |
| W s | 2 | 0.262 | 0.226 |

## Planar average `iwo_slab1_final_cpu_avg.dat`

{"n_points": 3000, "V_min_eV": -10.2725, "V_max_eV": 3.4228, "window_A": 0.01162, "z_mean_V_eV": 0.99417, "E_vac_eV": 3.42284, "vacuum_flatness_meV": 0.024, "vacuum_slope_meV_per_A": -0.0001, "work_function_eV": 2.8417}
- `avg_iwo_slab1_final_cpu.in` input: `1 iwo_slab1_final_cpu_v.pp 1.0 3000 3 4.8833`
- `pp_iwo_slab1_final_cpu.in` input: `&INPUTPP prefix = 'slab', outdir = './tmp', filplot = 'iwo_slab1_final_cpu_v.pp', plot_num = 11 /`
- `projwfc_iwo_slab1_final_cpu.in` input: `&PROJWFC prefix = 'slab', outdir = './tmp', filpdos = 'pdos/iwo_slab1_final_cpu' Emin = -7.4189, Emax = 4.5811, DeltaE = 0.01, degauss = 0.0073, ngauss = 0 /`
- `avg_iwo_slab1_final_cpu.out`: done True; Program AVERAGE v.7.5 starts on 30Sep2026 at 22:32:20 / Reading header from file  iwo_slab1_final_cpu_v.pp / Reading data from file  iwo_slab1_final_cpu_v.pp / AVERAGE      :      5.23s CPU      5.39s WALL / This run was terminated on:  22:32:26  30Sep2026
- `pp_iwo_slab1_final_cpu.out`: done True; Program POST-PROC v.7.5 starts on 30Sep2026 at 22:31:59 / Reading xml data from directory: / Calling punch_plot, plot_num =  11 / Writing data to file  iwo_slab1_final_cpu_v.pp / POST-PROC    :     18.86s CPU     20.59s WALL

## Other files

- `.fetched`: ''

## Checks against RESULTS_LOG

| quantity | re-derived | logged | reference | status |
|---|---|---|---|---|
| bands step rc | 161 | 161 | RESULTS_LOG.md:613 | match |
