# iwo_W8b

**Purpose.** 80-atom bulk IWO (In31 W O48, 3.1 % W) with W on the 8b site: relax (k3), SCF k4, projwfc/PDOS, bands, spin-polarised k3.

Folder `cern_htcondor/results/iwo_W8b`; data `runs_sep_oct/out/iwo_W8b.json` (+ `iwo_W8b_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| bands.in | 7701 | aac0c059471a5cec | loose | pw_in |
| bands.out | 312394 | d626641d0afcc470 | loose | pw_out |
| bands.tmpl | 5540 | 22084bd3e0b3aa90 | loose | pw_tmpl |
| iwo_W8b_driver.log | 936 | c12cfed5b018cb52 | loose | driver |
| projwfc_iwo_W8b.in | 149 | 3842b731552a28e4 | loose | post_in |
| projwfc_iwo_W8b.out | 15330900 | 14b5fe5d066cd83f | loose | projwfc_out |
| relax.in | 4414 | 0ec900d5ea24193b | loose | pw_in |
| relax.out | 892960 | 2190c37b11e9992d | loose | pw_out |
| scf_k4.in | 6479 | 0ab0ee01ac66385d | loose | pw_in |
| scf_k4.out | 358119 | e8c7d53f6db71223 | loose | pw_out |
| scf_k4.tmpl | 4318 | adadc52ea99ff098 | loose | pw_tmpl |
| spin_k3.in | 6524 | 8f74146648d4720e | loose | pw_in |
| spin_k3.out | 244722 | 17bc72750a2f33ce | loose | pw_out |
| spin_k3.tmpl | 4363 | 12cdd211e0bf8d70 | loose | pw_tmpl |
| steps.sh | 379 | b5145120d12e7b05 | loose | steps |

Tarball `iwo_W8b_results.tar.gz` (4864227 B, sha256 9507167047f1e5d6): 210 members; identical to the loose copy: 15; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 195

PDOS set `pdos`: 195 files.

## Resources and run history

- `iwo_W8b_driver.log`: host b9g12p0039.cern.ch, 32 CPUs, wall limit 259200 s, GPU: none (CPU), job total 116622 s, start 2026-09-27T08:46:55Z
  - step relax: -nk 4, max_seconds 257383, start 2026-09-27T08:47:12Z, end 2026-09-27T18:50:13Z, rc 0, PWSCF        :      9h 6m CPU     10h 2m WALL
  - step scf_k4: -nk 8, max_seconds 221201, start 2026-09-27T18:50:14Z, end 2026-09-27T20:11:07Z, rc 0, PWSCF        :      1h12m CPU      1h20m WALL
  - step bands: -nk 8, max_seconds 216290, start 2026-09-27T20:12:05Z, end 2026-09-28T15:15:39Z, rc 0, PWSCF        :     16h54m CPU     19h 3m WALL
  - step spin_k3: -nk 8, max_seconds 147672, start 2026-09-28T15:15:43Z, end 2026-09-28T17:10:37Z, rc 0, PWSCF        :      1h42m CPU      1h54m WALL
  - log: [2026-09-27T20:12:05Z] pdos iwo_W8b: 195 files
- HTCondor iwo_W8b 12756948.0: 32 CPUs, None GPU; seen 2026-09-28T14:19:54Z to 2026-09-28T17:01:07Z (17 samples); states {'2': 17} (1 idle, 2 running, 3 removed, 5 held); max scf_it 25, max BFGS 0; steps ['bands', 'spin_k3']; hw  
- `steps.sh`: `steps() { run_pw relax 4 python qeio.py converged relax.out || { log "relaxation did not finish; later steps skipped"; return 0; } for t in scf_k4 bands spin_k3; do python qeio.py newgeom $t.tmpl relax.out > $t.in; done clean_tmp run_pw scf_k4 8 || return 0 run_pdos iwo "$JOB" "$(python qeio.py fermi scf_k4.out)" 8 run_pw bands 8 clean_tmp run_pw spin_k3 8 }`

## Calculation `bands.out` (bands)

QE v.7.5 started 27Sep2026 22:12: 7; 32 MPI x 1 threads on 1 node(s); pools 8; R&G division 4; node memory 86449.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: JOB DONE; terminated 17:15:39  28Sep2026; PWSCF time {'cpu': '16h54m', 'wall': '19h 3m', 'calls': None}; output lines 3317.

**Input settings** (every namelist variable):

- &CONTROL: calculation = bands, prefix = iwo, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 216290
- &SYSTEM: ibrav = 0, nat = 80, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = smearing, smearing = mv, degauss = 0.01
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.3, electron_maxstep = 100, diagonalization = cg
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "W", "mass": 183.84, "pseudo": "W.pbe-spn-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.3060902, 0.0, 0.0], [0.0, 10.3060902, 0.0], [0.0, 0.0, 10.3060902]]}
- K_POINTS: {"mode": "tpiba", "n": 31, "points_first_last": [[0.0, 0.0, 0.0, 1.0], [0.14205113, 0.14205113, 0.14205113, 1.0]], "path_points": [[0.0, 0.0, 0.0, 1.0], [0.02460398, 0.0, 0.0, 1.0], [0.04920796, 0.0, 0.0, 1.0], [0.07381193, 0.0, 0.0, 1.0], [0.09841591, 0.0, 0.0, 1.0], [0.12301989, 0.0, 0.0, 1.0], [0.14762387, 0.0, 0.0, 1.0], [0.17222785, 0.0, 0.0, 1.0], [0.19683182, 0.0, 0.0, 1.0], [0.2214358, 0.0
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 80, "labels": ["In", "O", "W"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4757  a.u.; unit-cell volume = 7387.1755 (a.u.)^3; number of atoms/cell = 80; number of atomic types = 3; number of electrons = 705.00; number of Kohn-Sham states = 424; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.475688, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); W W.pbe-spn-kjpaw_psl.1.0.0.UPF md5 03c3df5b60893f488392c7401945500a (Projector augmented-wave + core cor, Z 14.0)
- Symmetry: 6 Sym. Ops., with inversion, found ( 3 have fractional translation); k points: number of k points=    31  Marzari-Vanderbilt smearing, width (Ry)=  0.0100 (sum of weights 1.999999); FFT: Dense  grid:  1688647 G-vectors     FFT dimensions: ( 150, 150, 150) / Smooth grid:   596713 G-vectors     FFT dimensions: ( 108, 108, 108)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '541.63 MB', 'Estimated max dynamical RAM per process': '787.16 MB', 'Estimated total dynamical RAM': '24.60 GB'}; start: ['Starting wfcs are  484 randomized atomic wfcs']
- Band-structure run: {'diag': 'CG style diagonalization', 'kpts_done': 4, 'ethr': 'ethr =  1.42E-13,  avg # of iterations = 77.2'}

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 31, "n_bands": 424, "E_F_eV": 10.7577, "bands_fully_below_EF": 352, "bands_crossing_EF_1based": [], "highest_band_below_EF_max_eV": 9.4672, "lowest_band_above_EF_min_eV": 10.8065}

**Warnings/errors**: message_from_routine x1 (first: line 1025 'Message from routine setup:'); c_bands_not_converged x4 (first: line 1476 'c_bands: 26 eigenvalues not converged'); ieee x24 (first: line 3294 'Note: The following floating-point exceptions are signalling: IEEE_UNDERFLOW_FLAG IEEE_DEN'); discouraged x1 (first: line 1026 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 1018 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

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

## Calculation `spin_k3.out` (scf/relax)

QE v.7.5 started 28Sep2026 17:15:45; 32 MPI x 1 threads on 1 node(s); pools 8; R&G division 4; node memory 49927.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: JOB DONE; terminated 19:10:37  28Sep2026; PWSCF time {'cpu': '1h42m', 'wall': '1h54m', 'calls': None}; output lines 2518.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = spin, outdir = ./tmp, pseudo_dir = ./, verbosity = low, tprnfor = .true., tstress = .true., max_seconds = 147672
- &SYSTEM: ibrav = 0, nat = 80, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = smearing, smearing = mv, degauss = 0.01, nspin = 2, starting_magnetization(3) = 0.5
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 100
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "W", "mass": 183.84, "pseudo": "W.pbe-spn-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.3060902, 0.0, 0.0], [0.0, 10.3060902, 0.0], [0.0, 0.0, 10.3060902]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "3", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 80, "labels": ["In", "O", "W"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4757  a.u.; unit-cell volume = 7387.1755 (a.u.)^3; number of atoms/cell = 80; number of atomic types = 3; number of electrons = 705.00; number of Kohn-Sham states = 424; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  plain     mixing; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.475688, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); W W.pbe-spn-kjpaw_psl.1.0.0.UPF md5 03c3df5b60893f488392c7401945500a (Projector augmented-wave + core cor, Z 14.0)
- Symmetry: 6 Sym. Ops., with inversion, found ( 3 have fractional translation); k points: number of k points=     6  Marzari-Vanderbilt smearing, width (Ry)=  0.0100 (sum of weights 1.0); FFT: Dense  grid:  1688647 G-vectors     FFT dimensions: ( 150, 150, 150) / Smooth grid:   596713 G-vectors     FFT dimensions: ( 108, 108, 108)
- RAM (pw.x estimate): {'Estimated max dynamical RAM per process': '1.76 GB', 'Estimated total dynamical RAM': '50.59 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     704.8841, renormalised to     705.0000', 'Starting wfcs are  484 randomized atomic wfcs']

**Convergence** (1 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 26 | 4e-10 | -15496.3493187 |  | 0.004345 | 0.00124 | 0.01915 | 3.1e-05 | 12.07 |  |  |  |

**Final energies** (last SCF): total_magnetization = 0.74, absolute_magnetization = 0.82, E_F_eV = 10.7634, E_Ry = -15496.3493187, E_all_electron_Ry = -404180.059729, acc_final_Ry = 4e-10, mTS_Ry = -0.00070079, internal_energy_Ry = -15496.34861792, one_electron_Ry = -1477.30206832, hartree_Ry = 1369.43015865, xc_Ry = -1835.21385476, ewald_Ry = -4035.60657529, paw_one_center_Ry = -9517.65627819, converged_iterations = 26
- stress tensor (kbar): [[12.07, 1.28, 1.28], [1.28, 12.07, 1.28], [1.28, 1.28, 12.07]]

**Bands** (final eigenvalues, every k in the arrays file): {"spin_up": {"n_k": 6, "n_bands": 424, "E_F_eV": 10.7634, "bands_fully_below_EF": 352, "bands_crossing_EF_1based": [353], "highest_band_below_EF_max_eV": 10.5704, "lowest_band_above_EF_min_eV": 10.7982}, "spin_down": {"n_k": 6, "n_bands": 424, "E_F_eV": 10.7634, "bands_fully_below_EF": 352, "bands_crossing_EF_1based": [353], "highest_band_below_EF_max_eV": 10.5971, "lowest_band_above_EF_min_eV": 11.0138}}

**Warnings/errors**: message_from_routine x1 (first: line 1021 'Message from routine setup:'); c_bands_not_converged x2 (first: line 1335 'c_bands:  4 eigenvalues not converged'); ieee x32 (first: line 2487 'Note: The following floating-point exceptions are signalling: IEEE_DENORMAL'); discouraged x1 (first: line 1022 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 1018 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `bands.in`: {"n_atoms": 80, "composition": {"In": 31, "O": 48, "W": 1}, "cell_lengths_A": [10.30609, 10.30609, 10.30609], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 1094.6665, "density_g_cm3": 6.8431, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 186, "min": 2.1295, "mean": 2.2296, "max": 2.4071, "std": 0.0616, "CN_In_hist": {"6": 31}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 1.9716, "mean": 1.9716, "max": 1.9716, "std": 0.0, "CN_W_hist": {"6": 1}}}, "CN_O_by_cations_hist": {"4": 48}}
- `relax.in`: {"n_atoms": 80, "composition": {"In": 31, "O": 48, "W": 1}, "cell_lengths_A": [10.30609, 10.30609, 10.30609], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 1094.6665, "density_g_cm3": 6.8431, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 186, "min": 2.1671, "mean": 2.2196, "max": 2.2561, "std": 0.0341, "CN_In_hist": {"6": 31}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 2.2146, "mean": 2.2146, "max": 2.2146, "std": 0.0, "CN_W_hist": {"6": 1}}}, "CN_O_by_cations_hist": {"4": 48}}
- `scf_k4.in`: {"n_atoms": 80, "composition": {"In": 31, "O": 48, "W": 1}, "cell_lengths_A": [10.30609, 10.30609, 10.30609], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 1094.6665, "density_g_cm3": 6.8431, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 186, "min": 2.1295, "mean": 2.2296, "max": 2.4071, "std": 0.0616, "CN_In_hist": {"6": 31}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 1.9716, "mean": 1.9716, "max": 1.9716, "std": 0.0, "CN_W_hist": {"6": 1}}}, "CN_O_by_cations_hist": {"4": 48}}
- `spin_k3.in`: {"n_atoms": 80, "composition": {"In": 31, "O": 48, "W": 1}, "cell_lengths_A": [10.30609, 10.30609, 10.30609], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 1094.6665, "density_g_cm3": 6.8431, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 186, "min": 2.1295, "mean": 2.2296, "max": 2.4071, "std": 0.0616, "CN_In_hist": {"6": 31}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 1.9716, "mean": 1.9716, "max": 1.9716, "std": 0.0, "CN_W_hist": {"6": 1}}}, "CN_O_by_cations_hist": {"4": 48}}

Geometry consistency (input of the follow-on step vs relax final coordinates): {"scf_k4.in vs final of relax.out": {"max_pos_diff_A": 0.0, "max_cell_diff_A": 0.0}, "bands.in vs final of relax.out": {"max_pos_diff_A": 0.0, "max_cell_diff_A": 0.0}, "spin_k3.in vs final of relax.out": {"max_pos_diff_A": 0.0, "max_cell_diff_A": 0.0}}

## projwfc `projwfc_iwo_W8b.out`

natomwfc 484, nbnd 424, nkstot 14, states 484, spilling 0.0024, Loewdin total 703.306, PROJWFC      :     49.85s CPU     56.13s WALL, done True

| element | n | total charge mean (min-max) | s | p | d |
|---|---|---|---|---|---|
| W | 1 | 13.1596 (13.1596-13.1596) | 2.446 | 6.9642 | 3.7494 |
| In | 31 | 11.8831 (11.8732-11.8907) | 0.7267 | 1.1662 | 9.9902 |
| O | 48 | 6.7036 (6.5886-6.7242) | 1.7411 | 4.9626 | 0.0 |

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
- `projwfc_iwo_W8b.in` input: `&PROJWFC prefix = 'iwo', outdir = './tmp', filpdos = 'pdos/iwo_W8b' Emin = 2.7577, Emax = 14.7577, DeltaE = 0.01, degauss = 0.0073, ngauss = 0 /`

## Other files

- `.fetched`: ''

## Checks against RESULTS_LOG

| quantity | re-derived | logged | reference | status |
|---|---|---|---|---|
| E relax k3 (Ry) | -15496.3476465985 | -15496.3476466 | RESULTS_LOG.md:666 | match |
| E SCF k4 (Ry) | -15496.34766084 | -15496.34766084 | RESULTS_LOG.md:667 | match |
| E spin k3 (Ry) | -15496.3493187 | -15496.3493187 | RESULTS_LOG.md:669 | match |
| total magnetisation | 0.74 | 0.74 | RESULTS_LOG.md:669 | match |
| W-O mean (A) | 1.9716 | 1.972 | RESULTS_LOG.md:668 | match |
