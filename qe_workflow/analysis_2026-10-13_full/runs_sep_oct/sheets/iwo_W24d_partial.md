# iwo_W24d_partial

**Purpose.** Copy of the running iwo_W24d relax output taken 2026-09-28 (preliminary site preference).

Folder `cern_htcondor/results/iwo_W24d_partial`; data `runs_sep_oct/out/iwo_W24d_partial.json` (+ `iwo_W24d_partial_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| iwo_W24d_driver.log | 427 | 69449e791db41f1c | loose | driver |
| relax.in | 4414 | 211e0b2cc32cdeb1 | loose | pw_in |
| relax.out | 1335990 | 67f29bad194b112b | loose | pw_out |

Tarball `part.tgz` (366623 B, sha256 af1da104a7c49dac): 3 members; identical to the loose copy: 3; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0

## Resources and run history

- `iwo_W24d_driver.log`: host b9g12p0056.cern.ch, 32 CPUs, wall limit 259200 s, GPU: none (CPU), job total None s, start 2026-09-27T08:46:56Z
  - step relax: -nk 8, max_seconds 257380, start 2026-09-27T08:47:16Z, end 2026-09-28T08:35:44Z, rc 0, PWSCF        :     21h26m CPU     23h48m WALL
  - step scf_k4: -nk 8, max_seconds 171671, start 2026-09-28T08:35:45Z, end None, rc None, 
- HTCondor iwo_W24d 12756948.1: 32 CPUs, None GPU; seen 2026-09-28T14:19:54Z to 2026-09-29T08:54:19Z (154 samples); states {'2': 154} (1 idle, 2 running, 3 removed, 5 held); max scf_it 26, max BFGS 0; steps ['bands', 'spin_k3']; hw  ['Intel(R) Xeon(R) CPU E5-2650 v4 @ 2.20GHz']

## Calculation `relax.out` (scf/relax)

QE v.7.5 started 27Sep2026 10:47:18; 32 MPI x 1 threads on 1 node(s); pools 8; R&G division 4; node memory 120010.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: JOB DONE; terminated 10:35:44  28Sep2026; PWSCF time {'cpu': '21h26m', 'wall': '23h48m', 'calls': None}; output lines 20261.

**Input settings** (every namelist variable):

- &CONTROL: calculation = relax, prefix = rel, outdir = ./tmp, pseudo_dir = ./, verbosity = low, tprnfor = .true., tstress = .true., max_seconds = 257380, nstep = 300, etot_conv_thr = 1.0d-4, forc_conv_thr = 1.0d-3
- &SYSTEM: ibrav = 0, nat = 80, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = smearing, smearing = mv, degauss = 0.01
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.3, electron_maxstep = 100
- &IONS: ion_dynamics = bfgs
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "W", "mass": 183.84, "pseudo": "W.pbe-spn-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.3060902, 0.0, 0.0], [0.0, 10.3060902, 0.0], [0.0, 0.0, 10.3060902]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "3", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 80, "labels": ["In", "O", "W"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4757  a.u.; unit-cell volume = 7387.1755 (a.u.)^3; number of atoms/cell = 80; number of atomic types = 3; number of electrons = 705.00; number of Kohn-Sham states = 424; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.3000; number of iterations used = 8  plain     mixing; energy convergence thresh. = 1.0E-04; force convergence thresh. = 1.0E-03; Exchange-correlation = SLA  PW   PBX  PBC; nstep = 300; celldm = [19.475688, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); W W.pbe-spn-kjpaw_psl.1.0.0.UPF md5 03c3df5b60893f488392c7401945500a (Projector augmented-wave + core cor, Z 14.0)
- Symmetry: 2 Sym. Ops. (no inversion) found ( 1 have fractional translation); k points: number of k points=    10  Marzari-Vanderbilt smearing, width (Ry)=  0.0100 (sum of weights 2.0); FFT: Dense  grid:  1688647 G-vectors     FFT dimensions: ( 150, 150, 150) / Smooth grid:   596713 G-vectors     FFT dimensions: ( 108, 108, 108)
- RAM (pw.x estimate): {'Estimated max dynamical RAM per process': '1.60 GB', 'Estimated total dynamical RAM': '48.36 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     704.8841, renormalised to     705.0000', 'Starting wfcs are  484 randomized atomic wfcs']

**Convergence** (19 SCF + BFGS): bfgs converged in  19 scf cycles and  18 bfgs steps (criteria: energy <  1.0E-04 Ry, force <  1.0E-03 Ry/Bohr) final energy -15496.3666036746 final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 23 | 7.8e-10 | -15496.17531085 |  | 0.07405 | 0.017 | 0.263489 | 2.4e-05 | -1.95 |  |  | 0.107 |
| 1 | 18 | 3.4e-10 | -15496.23828788 |  | 0.06413 | 0.014 | 0.217335 | 6.7e-05 | -0.73 |  |  | 0.1177 |
| 2 | 19 | 1.1e-10 | -15496.29025251 |  | 0.05252 | 0.0106 | 0.163768 | 2.6e-05 | 1.39 |  |  | 0.1766 |
| 3 | 18 | 5.2e-10 | -15496.33861554 |  | 0.03139 | 0.00601 | 0.093109 | 7.1e-05 | 6.78 |  |  | 0.214 |
| 4 | 20 | 9.7e-11 | -15496.35020484 |  | 0.02422 | 0.00549 | 0.085108 | 1.9e-05 | 16.35 |  |  | 0.06765 |
| 5 | 18 | 5.4e-11 | -15496.35561796 |  | 0.014 | 0.00268 | 0.04148 | 9e-06 | 12.24 |  |  | 0.01992 |
| 6 | 17 | 6.9e-11 | -15496.3576998 |  | 0.01229 | 0.00223 | 0.034521 | 1.1e-05 | 12.25 |  |  | 0.02191 |
| 7 | 17 | 9.7e-11 | -15496.35948528 |  | 0.01063 | 0.00187 | 0.02898 | 1.7e-05 | 12.43 |  |  | 0.03286 |
| 8 | 20 | 1.4e-11 | -15496.36155891 |  | 0.008352 | 0.00148 | 0.023004 | 4e-06 | 12.76 |  |  | 0.0493 |
| 9 | 19 | 3.3e-11 | -15496.36359917 |  | 0.006191 | 0.00122 | 0.018884 | 1.4e-05 | 13.31 |  |  | 0.05839 |
| 10 | 21 | 2.5e-11 | -15496.36471942 |  | 0.005039 | 0.00129 | 0.020033 | 4e-06 | 13.97 |  |  | 0.01497 |
| 11 | 20 | 5e-11 | -15496.36511591 |  | 0.004507 | 0.00115 | 0.017853 | 6e-06 | 13.99 |  |  | 0.01647 |
| 12 | 20 | 3.2e-11 | -15496.36569035 |  | 0.003072 | 0.00084 | 0.013016 | 7e-06 | 13.98 |  |  | 0.02452 |
| 13 | 20 | 2.4e-11 | -15496.36620704 |  | 0.002142 | 0.000612 | 0.009483 | 8e-06 | 13.96 |  |  | 0.004837 |
| 14 | 17 | 1.5e-11 | -15496.36630869 |  | 0.002256 | 0.00055 | 0.008525 | 7e-06 | 13.93 |  |  | 0.00532 |
| 15 | 19 | 4.8e-12 | -15496.3664176 |  | 0.002006 | 0.000439 | 0.006807 | 4e-06 | 13.9 |  |  | 0.007981 |
| 16 | 21 | 1.3e-12 | -15496.36651724 |  | 0.001469 | 0.000326 | 0.005055 | 2e-06 | 13.85 |  |  | 0.008708 |
| 17 | 20 | 2.3e-12 | -15496.3665725 |  | 0.001126 | 0.0003 | 0.004652 | 6e-06 | 13.8 |  |  | 0.006009 |
| 18 | 21 | 1e-12 | -15496.36660367 |  | 0.0009381 | 0.000278 | 0.004303 | 2e-06 | 13.78 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.03236, 0.0], E_F_eV = 10.8507, E_Ry = -15496.36660367, E_all_electron_Ry = -404180.077014, acc_final_Ry = 1e-12, mTS_Ry = -0.00219209, internal_energy_Ry = -15496.36441159, one_electron_Ry = -1472.33806959, hartree_Ry = 1366.99156216, xc_Ry = -1835.23351299, ewald_Ry = -4038.12338231, paw_one_center_Ry = -9517.66100886, converged_iterations = 21, bfgs_energy_error_Ry = 3.1e-05
- stress tensor (kbar): [[13.11, 0.0, 0.0], [0.0, 14.23, 0.46], [0.0, 0.46, 14.0]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 10, "n_bands": 424, "E_F_eV": 10.8507, "bands_fully_below_EF": 352, "bands_crossing_EF_1based": [353], "highest_band_below_EF_max_eV": 10.5683, "lowest_band_above_EF_min_eV": 10.9046}

**Final geometry** (vs `relax.in`): {"n_atoms": 80, "composition": {"In": 31, "O": 48, "W": 1}, "cell_lengths_A": [10.30609, 10.30609, 10.30609], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 1094.6665, "density_g_cm3": 6.8431, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 186, "min": 2.1246, "mean": 2.2298, "max": 2.4784, "std": 0.0648, "CN_In_hist": {"6": 31}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 1.8919, "mean": 1.9822, "max": 2.1523, "std": 0.1204, "CN_W_hist": {"6": 1}}}, "CN_O_by_cations_hist": {"4": 48}, "displacement_vs_initial": {"max_A": 0.3922, "atom": "O31", "mean_A": 0.054, "n_gt_0p1_A": 6, "by_element_max_A": {"In": 0.0821, "O": 0.3922, "W": 0.056}}, "reference_input": "relax.in"}

**Warnings/errors**: message_from_routine x1 (first: line 1021 'Message from routine setup:'); warning x2 (first: line 3159 'WARNING: bfgs curvature condition failed, Theta= 0.986'); c_bands_not_converged x12 (first: line 1338 'c_bands:  2 eigenvalues not converged'); ieee x24 (first: line 20238 'Note: The following floating-point exceptions are signalling: IEEE_UNDERFLOW_FLAG IEEE_DEN'); discouraged x1 (first: line 1022 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 1018 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `relax.in`: {"n_atoms": 80, "composition": {"In": 31, "O": 48, "W": 1}, "cell_lengths_A": [10.30609, 10.30609, 10.30609], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 1094.6665, "density_g_cm3": 6.8431, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 186, "min": 2.1671, "mean": 2.2193, "max": 2.2561, "std": 0.0334, "CN_In_hist": {"6": 31}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 2.1671, "mean": 2.221, "max": 2.2561, "std": 0.0387, "CN_W_hist": {"6": 1}}}, "CN_O_by_cations_hist": {"4": 48}}

## Checks against RESULTS_LOG

| quantity | re-derived | logged | reference | status |
|---|---|---|---|---|
| E relax (Ry), part of dE 0.01896 | -15496.3666036746 | -15496.3666037 | RESULTS_LOG.md:687 | match |
