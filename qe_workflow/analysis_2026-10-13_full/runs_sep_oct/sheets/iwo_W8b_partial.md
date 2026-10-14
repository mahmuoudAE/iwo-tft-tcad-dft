# iwo_W8b_partial

**Purpose.** Copy of the running iwo_W8b relax output taken 2026-09-28 (preliminary site preference); plus the k4 SCF and PDOS as fetched later.

Folder `cern_htcondor/results/iwo_W8b_partial`; data `runs_sep_oct/out/iwo_W8b_partial.json` (+ `iwo_W8b_partial_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| iwo_W8b_driver.log | 633 | b19ac10601198808 | loose | driver |
| relax.in | 4414 | 0ec900d5ea24193b | loose | pw_in |
| relax.out | 892960 | 2190c37b11e9992d | loose | pw_out |
| scf_k4.in | 6479 | 0ab0ee01ac66385d | loose | pw_in |
| scf_k4.out | 358119 | e8c7d53f6db71223 | loose | pw_out |

Tarball `part.tgz` (2655620 B, sha256 7694f48da9da38ed): 200 members; identical to the loose copy: 5; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 195

PDOS set `pdos`: 195 files.

## Resources and run history

- `iwo_W8b_driver.log`: host b9g12p0039.cern.ch, 32 CPUs, wall limit 259200 s, GPU: none (CPU), job total None s, start 2026-09-27T08:46:55Z
  - step relax: -nk 4, max_seconds 257383, start 2026-09-27T08:47:12Z, end 2026-09-27T18:50:13Z, rc 0, PWSCF        :      9h 6m CPU     10h 2m WALL
  - step scf_k4: -nk 8, max_seconds 221201, start 2026-09-27T18:50:14Z, end 2026-09-27T20:11:07Z, rc 0, PWSCF        :      1h12m CPU      1h20m WALL
  - step bands: -nk 8, max_seconds 216290, start 2026-09-27T20:12:05Z, end None, rc None, 
  - log: [2026-09-27T20:12:05Z] pdos iwo_W8b: 195 files
- HTCondor iwo_W8b 12756948.0: 32 CPUs, None GPU; seen 2026-09-28T14:19:54Z to 2026-09-28T17:01:07Z (17 samples); states {'2': 17} (1 idle, 2 running, 3 removed, 5 held); max scf_it 25, max BFGS 0; steps ['bands', 'spin_k3']; hw  

## Calculation `relax.out` (scf/relax)

QE v.7.5 started 27Sep2026 10:47:14; 32 MPI x 1 threads on 1 node(s); pools 4; R&G division 8; node memory 104158.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: JOB DONE; terminated 20:50:13  27Sep2026; PWSCF time {'cpu': '9h 6m', 'wall': '10h 2m', 'calls': None}; output lines 12983.

**Input settings** (every namelist variable):

- &CONTROL: calculation = relax, prefix = rel, outdir = ./tmp, pseudo_dir = ./, verbosity = low, tprnfor = .true., tstress = .true., max_seconds = 257383, nstep = 300, etot_conv_thr = 1.0d-4, forc_conv_thr = 1.0d-3
- &SYSTEM: ibrav = 0, nat = 80, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = smearing, smearing = mv, degauss = 0.01
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.3, electron_maxstep = 100
- &IONS: ion_dynamics = bfgs
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "W", "mass": 183.84, "pseudo": "W.pbe-spn-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.3060902, 0.0, 0.0], [0.0, 10.3060902, 0.0], [0.0, 0.0, 10.3060902]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "3", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 80, "labels": ["In", "O", "W"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4757  a.u.; unit-cell volume = 7387.1755 (a.u.)^3; number of atoms/cell = 80; number of atomic types = 3; number of electrons = 705.00; number of Kohn-Sham states = 424; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.3000; number of iterations used = 8  plain     mixing; energy convergence thresh. = 1.0E-04; force convergence thresh. = 1.0E-03; Exchange-correlation = SLA  PW   PBX  PBC; nstep = 300; celldm = [19.475688, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); W W.pbe-spn-kjpaw_psl.1.0.0.UPF md5 03c3df5b60893f488392c7401945500a (Projector augmented-wave + core cor, Z 14.0)
- Symmetry: 6 Sym. Ops., with inversion, found ( 3 have fractional translation); k points: number of k points=     6  Marzari-Vanderbilt smearing, width (Ry)=  0.0100 (sum of weights 2.0); FFT: Dense  grid:  1688647 G-vectors     FFT dimensions: ( 150, 150, 150) / Smooth grid:   596713 G-vectors     FFT dimensions: ( 108, 108, 108)
- RAM (pw.x estimate): {'Estimated max dynamical RAM per process': '828.93 MB', 'Estimated total dynamical RAM': '24.70 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     704.8841, renormalised to     705.0000', 'Starting wfcs are  484 randomized atomic wfcs']

**Convergence** (17 SCF + BFGS): bfgs converged in  17 scf cycles and  16 bfgs steps (criteria: energy <  1.0E-04 Ry, force <  1.0E-03 Ry/Bohr) final energy -15496.3476465985 final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 21 | 2.8e-10 | -15496.18401347 |  | 0.06044 | 0.0159 | 0.245837 | 4.1e-05 | -2.6 |  |  | 0.09103 |
| 1 | 16 | 2e-10 | -15496.23799045 |  | 0.04705 | 0.0127 | 0.196785 | 3.1e-05 | -1.43 |  |  | 0.1001 |
| 2 | 16 | 1.5e-10 | -15496.28222593 |  | 0.03528 | 0.00942 | 0.145899 | 5.2e-05 | 0.68 |  |  | 0.1502 |
| 3 | 15 | 1.9e-10 | -15496.32089995 |  | 0.02646 | 0.00496 | 0.07678 | 6.2e-05 | 5.76 |  |  | 0.1051 |
| 4 | 15 | 1e-10 | -15496.33062533 |  | 0.01639 | 0.00476 | 0.07371 | 2.5e-05 | 10.54 |  |  | 0.03 |
| 5 | 13 | 6.7e-11 | -15496.33535494 |  | 0.01316 | 0.00393 | 0.060837 | 1.9e-05 | 10.65 |  |  | 0.033 |
| 6 | 13 | 7.5e-11 | -15496.33966267 |  | 0.009436 | 0.00291 | 0.045092 | 3.5e-05 | 10.68 |  |  | 0.0495 |
| 7 | 14 | 5.3e-11 | -15496.343836 |  | 0.004725 | 0.00164 | 0.025448 | 3e-05 | 10.95 |  |  | 0.05011 |
| 8 | 15 | 2.1e-11 | -15496.34556283 |  | 0.004698 | 0.00128 | 0.019847 | 1.8e-05 | 11.41 |  |  | 0.006872 |
| 9 | 13 | 1.1e-11 | -15496.34593884 |  | 0.003969 | 0.00115 | 0.017846 | 1.2e-05 | 11.54 |  |  | 0.007559 |
| 10 | 13 | 1.9e-11 | -15496.34633171 |  | 0.003071 | 0.00096 | 0.014873 | 1.7e-05 | 11.66 |  |  | 0.01134 |
| 11 | 13 | 1.9e-11 | -15496.34679606 |  | 0.001756 | 0.000692 | 0.010727 | 1.4e-05 | 11.84 |  |  | 0.01701 |
| 12 | 15 | 1.7e-11 | -15496.34719998 |  | 0.001222 | 0.000517 | 0.008016 | 1.7e-05 | 12.1 |  |  | 0.009953 |
| 13 | 14 | 3.6e-12 | -15496.34732853 |  | 0.001255 | 0.000536 | 0.008297 | 8e-06 | 12.24 |  |  | 0.006247 |
| 14 | 13 | 1.2e-11 | -15496.34743024 |  | 0.001285 | 0.0005 | 0.007752 | 1.2e-05 | 12.29 |  |  | 0.006871 |
| 15 | 14 | 6.7e-12 | -15496.34755238 |  | 0.001199 | 0.000398 | 0.006162 | 1e-05 | 12.29 |  |  | 0.007799 |
| 16 | 14 | 3.5e-12 | -15496.3476466 |  | 0.0007275 | 0.000291 | 0.004501 | 7e-06 | 12.22 |  |  |  |

**Final energies** (last SCF): E_F_eV = 10.786, E_Ry = -15496.3476466, E_all_electron_Ry = -404180.058057, acc_final_Ry = 3.5e-12, mTS_Ry = -0.0026065, internal_energy_Ry = -15496.3450401, one_electron_Ry = -1477.23512986, hartree_Ry = 1369.34356421, xc_Ry = -1835.18815127, ewald_Ry = -4035.60657535, paw_one_center_Ry = -9517.65874782, converged_iterations = 14, bfgs_energy_error_Ry = 9.4e-05
- stress tensor (kbar): [[12.22, 1.65, 1.65], [1.65, 12.22, 1.65], [1.65, 1.65, 12.22]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 6, "n_bands": 424, "E_F_eV": 10.786, "bands_fully_below_EF": 352, "bands_crossing_EF_1based": [353], "highest_band_below_EF_max_eV": 10.5884, "lowest_band_above_EF_min_eV": 10.8732}

**Final geometry** (vs `relax.in`): {"n_atoms": 80, "composition": {"In": 31, "O": 48, "W": 1}, "cell_lengths_A": [10.30609, 10.30609, 10.30609], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 1094.6665, "density_g_cm3": 6.8431, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 186, "min": 2.1295, "mean": 2.2296, "max": 2.4071, "std": 0.0616, "CN_In_hist": {"6": 31}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 1.9716, "mean": 1.9716, "max": 1.9716, "std": 0.0, "CN_W_hist": {"6": 1}}}, "CN_O_by_cations_hist": {"4": 48}, "displacement_vs_initial": {"max_A": 0.2745, "atom": "O17", "mean_A": 0.052, "n_gt_0p1_A": 6, "by_element_max_A": {"In": 0.0406, "O": 0.2745, "W": 0.0}}, "reference_input": "relax.in"}

**Warnings/errors**: message_from_routine x1 (first: line 1021 'Message from routine setup:'); warning x2 (first: line 5342 'WARNING: bfgs curvature condition failed, Theta= 0.990'); c_bands_not_converged x11 (first: line 1317 'c_bands:  2 eigenvalues not converged'); ieee x12 (first: line 12972 'Note: The following floating-point exceptions are signalling: IEEE_UNDERFLOW_FLAG IEEE_DEN'); discouraged x1 (first: line 1022 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 1018 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Calculation `scf_k4.out` (scf/relax)

QE v.7.5 started 27Sep2026 20:50:16; 32 MPI x 1 threads on 1 node(s); pools 8; R&G division 4; node memory 93779.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: JOB DONE; terminated 22:11: 6  27Sep2026; PWSCF time {'cpu': '1h12m', 'wall': '1h20m', 'calls': None}; output lines 4093.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = iwo, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 221201
- &SYSTEM: ibrav = 0, nat = 80, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = smearing, smearing = mv, degauss = 0.01
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.3, electron_maxstep = 100
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "W", "mass": 183.84, "pseudo": "W.pbe-spn-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.3060902, 0.0, 0.0], [0.0, 10.3060902, 0.0], [0.0, 0.0, 10.3060902]]}
- K_POINTS: {"mode": "automatic", "grid": ["4", "4", "4", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 80, "labels": ["In", "O", "W"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4757  a.u.; unit-cell volume = 7387.1755 (a.u.)^3; number of atoms/cell = 80; number of atomic types = 3; number of electrons = 705.00; number of Kohn-Sham states = 424; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.3000; number of iterations used = 8  plain     mixing; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.475688, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); W W.pbe-spn-kjpaw_psl.1.0.0.UPF md5 03c3df5b60893f488392c7401945500a (Projector augmented-wave + core cor, Z 14.0)
- Symmetry: 6 Sym. Ops., with inversion, found ( 3 have fractional translation); k points: number of k points=    14  Marzari-Vanderbilt smearing, width (Ry)=  0.0100 (sum of weights 2.0); FFT: Dense  grid:  1688647 G-vectors     FFT dimensions: ( 150, 150, 150) / Smooth grid:   596713 G-vectors     FFT dimensions: ( 108, 108, 108)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '796.01 MB', 'Estimated max dynamical RAM per process': '1.60 GB', 'Estimated total dynamical RAM': '48.36 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     704.8841, renormalised to     705.0000', 'Starting wfcs are  484 randomized atomic wfcs']

**Convergence** (1 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 21 | 8e-10 | -15496.34766084 |  | 0.001473 | 0.000465 | 0.007211 | 3.5e-05 | 12.28 |  |  |  |

**Final energies** (last SCF): E_F_eV = 10.7577, E_Ry = -15496.34766084, E_all_electron_Ry = -404180.058071, acc_final_Ry = 8e-10, mTS_Ry = -0.00204102, internal_energy_Ry = -15496.34561982, one_electron_Ry = -1477.20999683, hartree_Ry = 1369.31431522, xc_Ry = -1835.18403087, ewald_Ry = -4035.60657529, paw_one_center_Ry = -9517.65933205, converged_iterations = 21
- stress tensor (kbar): [[12.28, 1.75, 1.75], [1.75, 12.28, 1.75], [1.75, 1.75, 12.28]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 14, "n_bands": 424, "E_F_eV": 10.7577, "bands_fully_below_EF": 352, "bands_crossing_EF_1based": [353], "highest_band_below_EF_max_eV": 10.7012, "lowest_band_above_EF_min_eV": 10.8086}

**Warnings/errors**: message_from_routine x1 (first: line 1021 'Message from routine setup:'); c_bands_not_converged x6 (first: line 1525 'c_bands:  1 eigenvalues not converged'); ieee x24 (first: line 4070 'Note: The following floating-point exceptions are signalling: IEEE_UNDERFLOW_FLAG IEEE_DEN'); discouraged x1 (first: line 1022 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 1018 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `relax.in`: {"n_atoms": 80, "composition": {"In": 31, "O": 48, "W": 1}, "cell_lengths_A": [10.30609, 10.30609, 10.30609], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 1094.6665, "density_g_cm3": 6.8431, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 186, "min": 2.1671, "mean": 2.2196, "max": 2.2561, "std": 0.0341, "CN_In_hist": {"6": 31}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 2.2146, "mean": 2.2146, "max": 2.2146, "std": 0.0, "CN_W_hist": {"6": 1}}}, "CN_O_by_cations_hist": {"4": 48}}
- `scf_k4.in`: {"n_atoms": 80, "composition": {"In": 31, "O": 48, "W": 1}, "cell_lengths_A": [10.30609, 10.30609, 10.30609], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 1094.6665, "density_g_cm3": 6.8431, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 186, "min": 2.1295, "mean": 2.2296, "max": 2.4071, "std": 0.0616, "CN_In_hist": {"6": 31}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 1.9716, "mean": 1.9716, "max": 1.9716, "std": 0.0, "CN_W_hist": {"6": 1}}}, "CN_O_by_cations_hist": {"4": 48}}

Geometry consistency (input of the follow-on step vs relax final coordinates): {"scf_k4.in vs final of relax.out": {"max_pos_diff_A": 0.0, "max_cell_diff_A": 0.0}}

## PDOS `pdos`

{"n_files": 195, "E_window_eV": [2.758, 14.768], "dE_eV": 0.01, "integral_dos_window": 360.403, "integral_dos_below_EF_or_VBM": 290.39, "reference_energy_eV": 10.7577}

| element, l | files | states in window | states below reference |
|---|---|---|---|
| In d | 31 | 4.669 | 4.562 |
| In p | 31 | 35.065 | 23.08 |
| In s | 31 | 45.901 | 19.261 |
| O p | 48 | 252.993 | 233.096 |
| O s | 48 | 10.369 | 5.033 |
| W d | 1 | 7.164 | 3.121 |
| W p | 2 | 0.646 | 0.483 |
| W s | 2 | 0.281 | 0.248 |

## Checks against RESULTS_LOG

| quantity | re-derived | logged | reference | status |
|---|---|---|---|---|
| E relax (Ry), part of dE 0.01896 | -15496.3476465985 | -15496.3476466 | RESULTS_LOG.md:687 | match |
