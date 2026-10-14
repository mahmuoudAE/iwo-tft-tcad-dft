# slab1_v35

**Purpose.** Vacuum-convergence test, unrelaxed 1 nm slab, 35 A vacuum: SCF, planar average, bands (Davidson).

Folder `cern_htcondor/results/slab1_v35`; data `runs_sep_oct/out/slab1_v35.json` (+ `slab1_v35_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| avg_slab1_v35.in | 35 | 43ab7853640b3d67 | loose | avg_in |
| avg_slab1_v35.out | 1295 | 6ea440af1dff52f5 | loose | avg_out |
| bands.in | 5845 | c293dbe9d6eb88ea | loose | pw_in |
| bands.out | 137549 | 6a26a7392ea96529 | loose | pw_out |
| pp_slab1_v35.in | 90 | 275c43e180b86a8a | loose | post_in |
| pp_slab1_v35.out | 39651 | a99b67ece564c078 | loose | pp_out |
| scf.in | 5037 | 0a8f78ec7871ca59 | loose | pw_in |
| scf.out | 199984 | d4dd2759aad0628f | loose | pw_out |
| slab1_v35_avg.dat | 138000 | e79d719676155834 | loose | avg_dat |
| slab1_v35_driver.log | 622 | 3ea389ef79a1f3b0 | loose | driver |
| steps.sh | 87 | f095ead260c50369 | loose | steps |

Tarball `slab1_v35_results.tar.gz` (98879 B, sha256 0534200344e6c66b): 11 members; identical to the loose copy: 11; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0

## Resources and run history

- `slab1_v35_driver.log`: host b9p34p1014.cern.ch, 16 CPUs, wall limit 86400 s, GPU: none (CPU), job total 11910 s, start 2026-09-27T00:57:43Z
  - step scf: -nk 4, max_seconds 84590, start 2026-09-27T00:57:53Z, end 2026-09-27T02:46:00Z, rc 0, PWSCF        :      7h39m CPU      1h48m WALL
  - step bands: -nk 4, max_seconds 78079, start 2026-09-27T02:46:24Z, end 2026-09-27T04:16:13Z, rc 0, PWSCF        :      7h 6m CPU      1h29m WALL
  - log: [2026-09-27T00:57:53Z] pw.x: /pool/condor/dir_604919/qe-env/bin/pw.x  python: /pool/condor/dir_604919/qe-env/bin/python
  - log: [2026-09-27T02:46:24Z] planar average slab1_v35: 3000 lines
- HTCondor: no entry in status_history.jsonl (it starts 2026-09-28T14:19Z).
- `steps.sh`: `steps() { run_pw scf 4 || return 0 run_ppavg slab "$JOB" 4.8689 run_pw bands 4 }`

## Calculation `bands.out` (bands)

QE v.7.5 started 27Sep2026 4:46:26; 16 MPI x 1 threads on 1 node(s); pools 4; R&G division 4; node memory 158313.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: JOB DONE; terminated 6:16:13  27Sep2026; PWSCF time {'cpu': '7h 6m', 'wall': '1h29m', 'calls': None}; output lines 1792.

**Input settings** (every namelist variable):

- &CONTROL: calculation = bands, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 78079
- &SYSTEM: ibrav = 0, nat = 96, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 328
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.3060902, 0.0, 0.0], [0.0, 10.3060902, 0.0], [0.0, 0.0, 44.87453893]]}
- K_POINTS: {"mode": "tpiba", "n": 21, "points_first_last": [[0.0, 0.0, 0.0, 1.0], [0.1739764, 0.1739764, 0.0, 1.0]], "path_points": [[0.0, 0.0, 0.0, 1.0], [0.02460398, 0.0, 0.0, 1.0], [0.04920796, 0.0, 0.0, 1.0], [0.07381193, 0.0, 0.0, 1.0], [0.09841591, 0.0, 0.0, 1.0], [0.12301989, 0.0, 0.0, 1.0], [0.14762387, 0.0, 0.0, 1.0], [0.17222785, 0.0, 0.0, 1.0], [0.19683182, 0.0, 0.0, 1.0], [0.2214358, 0.0, 0.0, 1.
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 96, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4757  a.u.; unit-cell volume = 32165.0684 (a.u.)^3; number of atoms/cell = 96; number of atomic types = 3; number of electrons = 624.00; number of Kohn-Sham states = 328; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.475688, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=    21 (sum of weights 2.0); FFT: Dense  grid:  7352879 G-vectors     FFT dimensions: ( 150, 150, 648) / Smooth grid:  2599559 G-vectors     FFT dimensions: ( 108, 108, 480)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '2.05 GB', 'Estimated max dynamical RAM per process': '4.44 GB', 'Estimated total dynamical RAM': '71.02 GB'}; start: ['Starting wfcs are  432 randomized atomic wfcs']
- Band-structure run: {'diag': 'Davidson diagonalization with overlap', 'kpts_done': 6, 'ethr': 'ethr =  1.60E-13,  avg # of iterations =120.0'}

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 21, "n_bands": 328, "n_occ": 312, "VBM_eV": -1.9948, "VBM_k_index": 20, "CBM_eV": -1.0109, "CBM_k_index": 0, "gap_eV": 0.9839, "direct_gap_min_eV": 1.0153, "direct_gap_k_index": 0, "gap_type": "indirect", "VB_width_top_band_eV": 0.0314, "CB_width_bottom_band_eV": 0.3165, "E2_minus_E1_at_k0_eV": 1.5677}

**Warnings/errors**: message_from_routine x1 (first: line 273 'Message from routine setup:'); c_bands_not_converged x6 (first: line 762 'c_bands:  6 eigenvalues not converged'); ieee x12 (first: line 1781 'Note: The following floating-point exceptions are signalling: IEEE_UNDERFLOW_FLAG IEEE_DEN'); discouraged x1 (first: line 274 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 266 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Calculation `scf.out` (scf/relax)

QE v.7.5 started 27Sep2026 2:57:55; 16 MPI x 1 threads on 1 node(s); pools 4; R&G division 4; node memory 391180.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: JOB DONE; terminated 4:46: 0  27Sep2026; PWSCF time {'cpu': '7h39m', 'wall': '1h48m', 'calls': None}; output lines 3252.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 84590
- &SYSTEM: ibrav = 0, nat = 96, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 328
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.3060902, 0.0, 0.0], [0.0, 10.3060902, 0.0], [0.0, 0.0, 44.87453893]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 96, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4757  a.u.; unit-cell volume = 32165.0684 (a.u.)^3; number of atoms/cell = 96; number of atomic types = 3; number of electrons = 624.00; number of Kohn-Sham states = 328; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.475688, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  7352879 G-vectors     FFT dimensions: ( 150, 150, 648) / Smooth grid:  2599559 G-vectors     FFT dimensions: ( 108, 108, 480)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '2.10 GB', 'Estimated max dynamical RAM per process': '4.93 GB', 'Estimated total dynamical RAM': '73.64 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     623.9105, renormalised to     624.0000', 'Starting wfcs are  432 randomized atomic wfcs']

**Convergence** (1 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 77 | 5.5e-10 | -11888.29270349 |  | 0.04921 | 0.0157 | 0.265842 | 2.9e-05 | -2.4 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.002184, 0.0], HOMO_eV = -1.9695, LUMO_eV = -1.0109, E_Ry = -11888.29270349, E_all_electron_Ry = -289577.544627, acc_final_Ry = 5.5e-10, one_electron_Ry = -116709.35026438, hartree_Ry = 58663.8512659, xc_Ry = -1487.76968758, ewald_Ry = 54648.40853996, paw_one_center_Ry = -7003.43255739, converged_iterations = 77
- stress tensor (kbar): [[2.67, 0.0, 0.0], [0.0, 2.18, 0.0], [0.0, 0.0, -12.06]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 328, "n_occ": 312, "VBM_eV": -1.9695, "VBM_k_index": 2, "CBM_eV": -1.0109, "CBM_k_index": 0, "gap_eV": 0.9586, "direct_gap_min_eV": 1.0153, "direct_gap_k_index": 0, "gap_type": "indirect", "VB_width_top_band_eV": 0.0567, "CB_width_bottom_band_eV": 0.9364, "E2_minus_E1_at_k0_eV": 1.5678}

**Warnings/errors**: message_from_routine x1 (first: line 269 'Message from routine setup:'); c_bands_not_converged x9 (first: line 1270 'c_bands:  1 eigenvalues not converged'); discouraged x1 (first: line 270 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 266 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `bands.in`: {"n_atoms": 96, "composition": {"H": 24, "In": 24, "O": 48}, "cell_lengths_A": [10.30609, 10.30609, 44.87454], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4766.3714, "density_g_cm3": 1.236, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 144, "min": 2.1671, "mean": 2.2189, "max": 2.2561, "std": 0.0317, "CN_In_hist": {"6": 24}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.97, "mean": 0.97, "max": 0.97, "std": 0.0, "CN_O_hist": {"0": 24, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 24}, "slab": {"vacuum_A": 35.0, "extent_A": 9.875, "thickness_H_H_A": 9.8745, "thickness_O_O_A": 8.0332, "thickness_In_In_A": 5.153}}
- `scf.in`: {"n_atoms": 96, "composition": {"H": 24, "In": 24, "O": 48}, "cell_lengths_A": [10.30609, 10.30609, 44.87454], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4766.3714, "density_g_cm3": 1.236, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 144, "min": 2.1671, "mean": 2.2189, "max": 2.2561, "std": 0.0317, "CN_In_hist": {"6": 24}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.97, "mean": 0.97, "max": 0.97, "std": 0.0, "CN_O_hist": {"0": 24, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 24}, "slab": {"vacuum_A": 35.0, "extent_A": 9.875, "thickness_H_H_A": 9.8745, "thickness_O_O_A": 8.0332, "thickness_In_In_A": 5.153}}

## Planar average `slab1_v35_avg.dat`

{"n_points": 3000, "V_min_eV": -10.4053, "V_max_eV": 2.4223, "window_A": 0.01496, "z_mean_V_eV": 0.76667, "E_vac_eV": 2.42225, "vacuum_flatness_meV": 0.025, "vacuum_slope_meV_per_A": -0.0, "IP_eV": 4.3918, "EA_eV": 3.4331}
- `avg_slab1_v35.in` input: `1 slab1_v35_v.pp 1.0 3000 3 4.8689`
- `pp_slab1_v35.in` input: `&INPUTPP prefix = 'slab', outdir = './tmp', filplot = 'slab1_v35_v.pp', plot_num = 11 /`
- `avg_slab1_v35.out`: done True; Program AVERAGE v.7.5 starts on 27Sep2026 at  4:46:19 / Reading header from file  slab1_v35_v.pp / Reading data from file  slab1_v35_v.pp / AVERAGE      :      4.88s CPU      5.01s WALL / This run was terminated on:   4:46:24  27Sep2026
- `pp_slab1_v35.out`: done True; Program POST-PROC v.7.5 starts on 27Sep2026 at  4:46: 2 / Reading xml data from directory: / Calling punch_plot, plot_num =  11 / Writing data to file  slab1_v35_v.pp / POST-PROC    :     16.45s CPU     15.19s WALL

## Other files

- `.fetched`: ''

## Checks against RESULTS_LOG

| quantity | re-derived | logged | reference | status |
|---|---|---|---|---|
| SCF iterations | 77 | 77 | RESULTS_LOG.md:715 | match |
| gap (eV) | 0.9586 | 0.9586 | RESULTS_LOG.md:715 | match |
| EA (eV) | 3.4331 | 3.4332 | RESULTS_LOG.md:715 | match |
| IP (eV) | 4.3918 | 4.3918 | RESULTS_LOG.md:715 | match |
| CPUs (driver) | 16 | 16 | RESULTS_LOG.md:694 | match |
| pools | 4 | 4 | RESULTS_LOG.md:694 | match |
| SCF wall (h) | 1.8 | 1.8 | RESULTS_LOG.md:694 | match |
| bands wall (h) | 1.483 | 1.4833 | RESULTS_LOG.md:694 | match |
| symmetry ops | 8 | 8 | RESULTS_LOG.md:695 | match |
| irreducible k | 4 | 4 | RESULTS_LOG.md:695 | match |
| VBM (eV) | -1.9695 | -1.9695 | RESULTS_LOG.md:698 | match |
| CBM (eV) | -1.0109 | -1.0109 | RESULTS_LOG.md:698 | match |
| E_vac (eV) | 2.42225 | 2.422 | RESULTS_LOG.md:699 | match |
