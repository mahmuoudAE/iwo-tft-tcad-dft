# slab1r_final_cpu

**Purpose.** CPU final SCF of the relaxed 1 nm slab geometry (QE 7.5) with planar average and bands (EA/IP, gap, mass).

Folder `cern_htcondor/results/slab1r_final_cpu`; data `runs_sep_oct/out/slab1r_final_cpu.json` (+ `slab1r_final_cpu_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| avg_slab1r_final_cpu.in | 42 | 4237cd66606ffa41 | loose | avg_in |
| avg_slab1r_final_cpu.out | 1309 | 63fe05e97f4c749d | loose | avg_out |
| bands.in | 5847 | a00ff1a08472fd81 | loose | pw_in |
| bands.out | 137397 | bf8c57d222a56a5d | loose | pw_out |
| pp_slab1r_final_cpu.in | 97 | 830f477051f82d8d | loose | post_in |
| pp_slab1r_final_cpu.out | 39658 | 32a57a7b467cee24 | loose | pp_out |
| scf.in | 5039 | fe1601bfb2863e9b | loose | pw_in |
| scf.out | 179929 | d77b355b5e894dda | loose | pw_out |
| slab1r_final_cpu_avg.dat | 138000 | be0f144c0f035134 | loose | avg_dat |
| slab1r_final_cpu_driver.log | 635 | 6ba8aeed4e1624a5 | loose | driver |
| steps.sh | 87 | 8005189785b859e9 | loose | steps |

Tarball `slab1r_final_cpu_results.tar.gz` (100532 B, sha256 876a5b1002d34e52): 11 members; identical to the loose copy: 11; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0

## Resources and run history

- `slab1r_final_cpu_driver.log`: host b9p02p9432.cern.ch, 16 CPUs, wall limit 86400 s, GPU: none (CPU), job total 25080 s, start 2026-09-30T00:32:41Z
  - step scf: -nk 4, max_seconds 84588, start 2026-09-30T00:32:53Z, end 2026-09-30T02:51:56Z, rc 0, PWSCF        :      2h14m CPU      2h19m WALL
  - step bands: -nk 4, max_seconds 76216, start 2026-09-30T02:52:25Z, end 2026-09-30T07:30:40Z, rc 0, PWSCF        :      4h32m CPU      4h38m WALL
  - log: [2026-09-30T02:52:24Z] planar average slab1r_final_cpu: 3000 lines
- HTCondor slab1r_final_cpu 12783163.0: 16 CPUs, 0 GPU; seen 2026-09-30T00:27:59Z to 2026-09-30T07:28:41Z (64 samples); states {'1': 1, '2': 63} (1 idle, 2 running, 3 removed, 5 held); max scf_it 47, max BFGS 0; steps ['scf', 'bands']; hw  ['AMD EPYC 7543 32-Core Processor']
- `steps.sh`: `steps() { run_pw scf 4 || return 0 run_ppavg slab "$JOB" 4.8833 run_pw bands 4 }`

## Calculation `bands.out` (bands)

QE v.7.5 started 30Sep2026 4:52:26; 16 MPI x 1 threads on 1 node(s); pools 4; R&G division 4; node memory 133359.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: JOB DONE; terminated 9:30:40  30Sep2026; PWSCF time {'cpu': '4h32m', 'wall': '4h38m', 'calls': None}; output lines 1790.

**Input settings** (every namelist variable):

- &CONTROL: calculation = bands, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 76216
- &SYSTEM: ibrav = 0, nat = 96, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 328
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.33643106, 0.0, 0.0], [0.0, 10.33450421, 0.0], [0.0, 0.0, 34.87453893]]}
- K_POINTS: {"mode": "tpiba", "n": 21, "points_first_last": [[0.0, 0.0, 0.0, 1.0], [0.17448858, 0.17448858, 0.0, 1.0]], "path_points": [[0.0, 0.0, 0.0, 1.0], [0.02467641, 0.0, 0.0, 1.0], [0.04935282, 0.0, 0.0, 1.0], [0.07402923, 0.0, 0.0, 1.0], [0.09870565, 0.0, 0.0, 1.0], [0.12338206, 0.0, 0.0, 1.0], [0.14805847, 0.0, 0.0, 1.0], [0.17273488, 0.0, 0.0, 1.0], [0.19741129, 0.0, 0.0, 1.0], [0.2220877, 0.0, 0.0, 
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 96, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.5330  a.u.; unit-cell volume = 25140.0035 (a.u.)^3; number of atoms/cell = 96; number of atomic types = 3; number of electrons = 624.00; number of Kohn-Sham states = 328; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.533024, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=    21 (sum of weights 2.0); FFT: Dense  grid:  5746731 G-vectors     FFT dimensions: ( 150, 150, 500) / Smooth grid:  2031701 G-vectors     FFT dimensions: ( 108, 108, 360)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '1.60 GB', 'Estimated max dynamical RAM per process': '3.47 GB', 'Estimated total dynamical RAM': '55.52 GB'}; start: ['Starting wfcs are  432 randomized atomic wfcs']
- Band-structure run: {'diag': 'Davidson diagonalization with overlap', 'kpts_done': 6, 'ethr': 'ethr =  1.60E-13,  avg # of iterations =120.0'}

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 21, "n_bands": 328, "n_occ": 312, "VBM_eV": -2.3402, "VBM_k_index": 0, "CBM_eV": -0.5517, "CBM_k_index": 0, "gap_eV": 1.7885, "direct_gap_min_eV": 1.7885, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.0093, "CB_width_bottom_band_eV": 0.2796, "E2_minus_E1_at_k0_eV": 1.4988}

**Warnings/errors**: message_from_routine x1 (first: line 273 'Message from routine setup:'); c_bands_not_converged x6 (first: line 762 'c_bands:  6 eigenvalues not converged'); ieee x10 (first: line 1781 'Note: The following floating-point exceptions are signalling: IEEE_UNDERFLOW_FLAG IEEE_DEN'); discouraged x1 (first: line 274 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 266 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Calculation `scf.out` (scf/relax)

QE v.7.5 started 30Sep2026 2:32:55; 16 MPI x 1 threads on 1 node(s); pools 4; R&G division 4; node memory 104105.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: JOB DONE; terminated 4:51:56  30Sep2026; PWSCF time {'cpu': '2h14m', 'wall': '2h19m', 'calls': None}; output lines 2738.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 84588
- &SYSTEM: ibrav = 0, nat = 96, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 328
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.33643106, 0.0, 0.0], [0.0, 10.33450421, 0.0], [0.0, 0.0, 34.87453893]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 96, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.5330  a.u.; unit-cell volume = 25140.0035 (a.u.)^3; number of atoms/cell = 96; number of atomic types = 3; number of electrons = 624.00; number of Kohn-Sham states = 328; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.533024, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  5746731 G-vectors     FFT dimensions: ( 150, 150, 500) / Smooth grid:  2031701 G-vectors     FFT dimensions: ( 108, 108, 360)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '1.64 GB', 'Estimated max dynamical RAM per process': '3.86 GB', 'Estimated total dynamical RAM': '57.57 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     623.9105, renormalised to     624.0000', 'Starting wfcs are  432 randomized atomic wfcs']

**Convergence** (1 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 47 | 6.4e-10 | -11888.81106135 |  | 0.0007675 | 0.00036 | 0.006104 | 2.5e-05 | -0.3 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.00179, 0.0], HOMO_eV = -2.3403, LUMO_eV = -0.5518, E_Ry = -11888.81106135, E_all_electron_Ry = -289578.062985, acc_final_Ry = 6.4e-10, one_electron_Ry = -78759.35335568, hartree_Ry = 39691.25810087, xc_Ry = -1487.94966038, ewald_Ry = 35670.75710107, paw_one_center_Ry = -7003.52324721, converged_iterations = 47
- stress tensor (kbar): [[-0.04, 0.0, 0.0], [0.0, -0.12, 0.0], [0.0, 0.0, -0.75]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 328, "n_occ": 312, "VBM_eV": -2.3403, "VBM_k_index": 0, "CBM_eV": -0.5518, "CBM_k_index": 0, "gap_eV": 1.7885, "direct_gap_min_eV": 1.7885, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.03, "CB_width_bottom_band_eV": 0.8601, "E2_minus_E1_at_k0_eV": 1.4989}

**Warnings/errors**: message_from_routine x1 (first: line 269 'Message from routine setup:'); c_bands_not_converged x1 (first: line 983 'c_bands:  2 eigenvalues not converged'); ieee x2 (first: line 2737 'Note: The following floating-point exceptions are signalling: IEEE_UNDERFLOW_FLAG IEEE_DEN'); discouraged x1 (first: line 270 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 266 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `bands.in`: {"n_atoms": 96, "composition": {"H": 24, "In": 24, "O": 48}, "cell_lengths_A": [10.33643, 10.3345, 34.87454], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3725.3642, "density_g_cm3": 1.5814, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 144, "min": 2.1647, "mean": 2.219, "max": 2.3078, "std": 0.0389, "CN_In_hist": {"6": 24}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9719, "mean": 0.9775, "max": 0.9864, "std": 0.0064, "CN_O_hist": {"0": 24, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 24}, "slab": {"vacuum_A": 25.571, "extent_A": 9.303, "thickness_H_H_A": 9.3033, "thickness_O_O_A": 7.8762, "thickness_In_In_A": 5.1515}}
- `scf.in`: {"n_atoms": 96, "composition": {"H": 24, "In": 24, "O": 48}, "cell_lengths_A": [10.33643, 10.3345, 34.87454], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3725.3642, "density_g_cm3": 1.5814, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 144, "min": 2.1647, "mean": 2.219, "max": 2.3078, "std": 0.0389, "CN_In_hist": {"6": 24}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9719, "mean": 0.9775, "max": 0.9864, "std": 0.0064, "CN_O_hist": {"0": 24, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 24}, "slab": {"vacuum_A": 25.571, "extent_A": 9.303, "thickness_H_H_A": 9.3033, "thickness_O_O_A": 7.8762, "thickness_In_In_A": 5.1515}}

## Planar average `slab1r_final_cpu_avg.dat`

{"n_points": 3000, "V_min_eV": -10.2257, "V_max_eV": 3.3767, "window_A": 0.01162, "z_mean_V_eV": 0.98091, "E_vac_eV": 3.37669, "vacuum_flatness_meV": 0.021, "vacuum_slope_meV_per_A": -0.0001, "IP_eV": 5.717, "EA_eV": 3.9285}
- `avg_slab1r_final_cpu.in` input: `1 slab1r_final_cpu_v.pp 1.0 3000 3 4.8833`
- `pp_slab1r_final_cpu.in` input: `&INPUTPP prefix = 'slab', outdir = './tmp', filplot = 'slab1r_final_cpu_v.pp', plot_num = 11 /`
- `avg_slab1r_final_cpu.out`: done True; Program AVERAGE v.7.5 starts on 30Sep2026 at  4:52:20 / Reading header from file  slab1r_final_cpu_v.pp / Reading data from file  slab1r_final_cpu_v.pp / AVERAGE      :      4.68s CPU      4.78s WALL / This run was terminated on:   4:52:24  30Sep2026
- `pp_slab1r_final_cpu.out`: done True; Program POST-PROC v.7.5 starts on 30Sep2026 at  4:51:58 / Reading xml data from directory: / Calling punch_plot, plot_num =  11 / Writing data to file  slab1r_final_cpu_v.pp / POST-PROC    :     18.79s CPU     19.82s WALL

## Other files

- `.fetched`: ''

## Checks against RESULTS_LOG

| quantity | re-derived | logged | reference | status |
|---|---|---|---|---|
| gap (eV) | 1.7885 | 1.7885 | RESULTS_LOG.md:652 | match |
