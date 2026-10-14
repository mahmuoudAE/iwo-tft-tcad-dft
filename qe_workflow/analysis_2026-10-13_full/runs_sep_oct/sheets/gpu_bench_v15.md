# gpu_bench_v15

**Purpose.** GPU benchmark: the slab1_v15 SCF on one H100 NVL (QE 7.3.1 GPU) to compare cost and results with the CPU run.

Folder `cern_htcondor/results/gpu_bench_v15`; data `runs_sep_oct/out/gpu_bench_v15.json` (+ `gpu_bench_v15_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| gpu_bench_v15_driver.log | 475 | 3af3826c29352312 | loose | driver |
| scf.in | 5037 | 04eb909f3ebe53a8 | loose | pw_in |
| scf.out | 152140 | fda51ea012e20894 | loose | pw_out |
| steps.sh | 27 | a7d5ef8aefb09efb | loose | steps |

Tarball `gpu_bench_v15_results.tar.gz` (22254 B, sha256 8a27296de5af8c9a): 4 members; identical to the loose copy: 4; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0

## Resources and run history

- `gpu_bench_v15_driver.log`: host b9pgpun303.cern.ch, 11 CPUs, wall limit 28800 s, GPU: 1 GPU(s), NVIDIA H100 NVL, 95830 MiB, job total 575 s, start 2026-09-28T14:55:01Z
  - step scf: -nk 1, max_seconds 26982, start 2026-09-28T14:55:19Z, end 2026-09-28T15:04:36Z, rc 0, PWSCF        :   9m 7.11s CPU   9m15.66s WALL
- HTCondor gpu_bench_v15 12759676.0: 11 CPUs, None GPU; seen 2026-09-28T14:56:42Z to 2026-09-28T14:56:42Z (1 samples); states {'2': 1} (1 idle, 2 running, 3 removed, 5 held); max scf_it 7, max BFGS 0; steps ['scf']; hw  
- `steps.sh`: `steps() { run_pw scf 1 }`

## Calculation `scf.out` (scf/relax)

QE v.7.3.1 started 28Sep2026 16:55:20; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 32425.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled; GPU used by master process:. Completed: JOB DONE; terminated 17: 4:36  28Sep2026; PWSCF time {'cpu': '9m 7.11s', 'wall': '9m15.66s', 'calls': None}; output lines 2640.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 26982
- &SYSTEM: ibrav = 0, nat = 96, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 328
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.3060902, 0.0, 0.0], [0.0, 10.3060902, 0.0], [0.0, 0.0, 24.87453893]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 96, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4757  a.u.; unit-cell volume = 17829.5146 (a.u.)^3; number of atoms/cell = 96; number of atomic types = 3; number of electrons = 624.00; number of Kohn-Sham states = 328; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.475688, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  4075609 G-vectors     FFT dimensions: ( 150, 150, 360) / Smooth grid:  1441173 G-vectors     FFT dimensions: ( 108, 108, 256)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '8.18 GB', 'Estimated max dynamical RAM per process': '29.10 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     623.9105, renormalised to     624.0000', 'Starting wfcs are  432 randomized atomic wfcs']

**Convergence** (1 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 46 | 1e-09 | -11888.29271202 |  | 0.04921 | 0.0157 | 0.265834 | 1.7e-05 | -4.34 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.0009706, 0.0], HOMO_eV = -0.022, LUMO_eV = 0.9366, E_Ry = -11888.29271202, E_all_electron_Ry = -289577.544635, acc_final_Ry = 1e-09, one_electron_Ry = -41586.61982252, hartree_Ry = 21147.14550892, xc_Ry = -1487.76931861, ewald_Ry = 17042.38348427, paw_one_center_Ry = -7003.43256407, converged_iterations = 46
- stress tensor (kbar): [[4.81, 0.0, 0.0], [0.0, 3.93, 0.0], [0.0, 0.0, -21.77]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 328, "n_occ": 312, "VBM_eV": -0.022, "VBM_k_index": 2, "CBM_eV": 0.9366, "CBM_k_index": 0, "gap_eV": 0.9586, "direct_gap_min_eV": 1.0153, "direct_gap_k_index": 0, "gap_type": "indirect", "VB_width_top_band_eV": 0.0567, "CB_width_bottom_band_eV": 0.9364, "E2_minus_E1_at_k0_eV": 1.5679}

**Warnings/errors**: message_from_routine x1 (first: line 29 'Message from routine setup:'); warning x3 (first: line 2637 'Warning: ieee_invalid is signaling'); c_bands_not_converged x20 (first: line 736 'c_bands:  2 eigenvalues not converged'); ieee x3 (first: line 2637 'Warning: ieee_invalid is signaling'); discouraged x1 (first: line 30 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized'); fortran_stop x1 (first: line 2640 'FORTRAN STOP')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `scf.in`: {"n_atoms": 96, "composition": {"H": 24, "In": 24, "O": 48}, "cell_lengths_A": [10.30609, 10.30609, 24.87454], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 2642.0615, "density_g_cm3": 2.2298, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 144, "min": 2.1671, "mean": 2.2189, "max": 2.2561, "std": 0.0317, "CN_In_hist": {"6": 24}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.97, "mean": 0.97, "max": 0.97, "std": 0.0, "CN_O_hist": {"0": 24, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 24}, "slab": {"vacuum_A": 15.0, "extent_A": 9.875, "thickness_H_H_A": 9.8745, "thickness_O_O_A": 8.0332, "thickness_In_In_A": 5.153}}

## Other files

- `.fetched`: ''
