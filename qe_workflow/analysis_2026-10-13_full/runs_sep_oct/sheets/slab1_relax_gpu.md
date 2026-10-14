# slab1_relax_gpu

**Purpose.** vc-relax (atoms + in-plane cell, 2Dxy) of the 1 nm slab on a GPU after CPU steps; final SCF, planar average, bands (in-plane CB mass).

Folder `cern_htcondor/results/slab1_relax_gpu`; data `runs_sep_oct/out/slab1_relax_gpu.json` (+ `slab1_relax_gpu_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| avg_slab1_relax_gpu.in | 41 | 15a09605d04f4693 | loose | avg_in |
| avg_slab1_relax_gpu.out | 1598 | c274f7c625a96a5b | loose | avg_out |
| bands.in | 8462 | 6d2621b3d5bb8243 | loose | pw_in |
| bands.out | 101284 | 224c9ec8ce1dd222 | loose | pw_out |
| bands.tmpl | 5869 | 4abafafcae1f4727 | loose | pw_tmpl |
| pp_slab1_relax_gpu.in | 96 | 953995c6d2caab4c | loose | post_in |
| pp_slab1_relax_gpu.out | 19957 | 7ad2820a502a2c6d | loose | pp_out |
| scf.in | 7630 | 3862a31488e350e7 | loose | pw_in |
| scf.out | 159048 | 7f6a5ca8c1edca40 | loose | pw_out |
| scf.tmpl | 5037 | 440478ce403aa22b | loose | pw_tmpl |
| slab1_relax_gpu_driver.log | 872 | af57359ccac7f0be | loose | driver |
| steps.sh | 310 | a96f86388fae0db4 | loose | steps |
| vcrelax.in | 7804 | 9524e9988513ecc4 | loose | pw_in |
| vcrelax.out | 2512846 | 575331c5b76407e8 | loose | pw_out |
| vcrelax_initial.in | 5211 | 4a7c9b91304eec58 | loose | pw_in |

Tarball `slab1_relax_gpu_results.tar.gz` (553166 B, sha256 7c66d43cc12b301d): 15 members; identical to the loose copy: 15; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0

## Resources and run history

- `slab1_relax_gpu_driver.log`: host b9g57n0021.cern.ch, 11 CPUs, wall limit 259200 s, GPU: 1 GPU(s), NVIDIA A100-PCIE-40GB, 40960 MiB, job total 74575 s, start 2026-09-28T15:15:04Z
  - step vcrelax: -nk 2, max_seconds 257382, start 2026-09-28T15:15:22Z, end 2026-09-29T06:47:23Z, rc 0, PWSCF        :      8h15m CPU     15h31m WALL
  - step scf: -nk 2, max_seconds 201460, start 2026-09-29T06:47:24Z, end 2026-09-29T07:18:58Z, rc 0, PWSCF        :  10m46.87s CPU  31m30.21s WALL
  - step bands: -nk 2, max_seconds 199557, start 2026-09-29T07:19:07Z, end 2026-09-29T11:57:58Z, rc 0, PWSCF        :      1h50m CPU      4h38m WALL
  - log: [2026-09-29T07:19:07Z] planar average slab1_relax_gpu: 0 lines
- HTCondor slab1_relax_gpu 12759677.0: 11 CPUs, None GPU; seen 2026-09-28T15:17:28Z to 2026-09-29T11:54:19Z (181 samples); states {'2': 181} (1 idle, 2 running, 3 removed, 5 held); max scf_it 2197, max BFGS 53; steps ['vcrelax', 'scf', 'bands']; hw ['1xNVIDIA A100-PCIE-40GB|0%', '1xNVIDIA A100-PCIE-40GB|1%', '1xNVIDIA A100-PCIE-40GB|10%', '1xNVIDIA A100-PCIE-40GB|11%', '1xNVIDIA A100-PCIE-40GB|12%', '1xNVIDIA A100-PCIE-40GB|13%', '1xNVIDIA A100-PCIE-40GB|15%', '1xNVIDIA A100-PCIE-40GB|16%', '1xNVIDIA A100-PCIE-40GB|27%', '1xNVIDIA A100-PCIE-40GB|39%', '1xNVIDIA A100-PCIE-40GB|4%', '1xNVIDIA A100-PCIE-40GB|42%', '1xNVIDIA A100-PCIE-40GB|43%', '1xNVIDIA A100-PCIE-40GB|44%', '1xNVIDIA A100-PCIE-40GB|45%', '1xNVIDIA A100-PCIE-40GB|46%', '1xNVIDIA A100-PCIE-40GB|47%', '1xNVIDIA A100-PCIE-40GB|48%', '1xNVIDIA A100-PCIE-40GB|49%', '1xNVIDIA A100-PCIE-40GB|50%', '1xNVIDIA A100-PCIE-40GB|51%', '1xNVIDIA A100-PCIE-40GB|52%', '1xNVIDIA A100-PCIE-40GB|53%', '1xNVIDIA A100-PCIE-40GB|54%', '1xNVIDIA A100-PCIE-40GB|58%', '1xNVIDIA A100-PCIE-40GB|6%', '1xNVIDIA A100-PCIE-40GB|60%', '1xNVIDIA A100-PCIE-40GB|63%', '1xNVIDIA A100-PCIE-40GB|7%', '1xNVIDIA A100-PCIE-40GB|71%', '1xNVIDIA A100-PCIE-40GB|73%', '1xNVIDIA A100-PCIE-40GB|75%', '1xNVIDIA A100-PCIE-40GB|78%', '1xNVIDIA A100-PCIE-40GB|8%', '1xNVIDIA A100-PCIE-40GB|80%', '1xNVIDIA A100-PCIE-40GB|81%', '1xNVIDIA A100-PCIE-40GB|83%', '1xNVIDIA A100-PCIE-40GB|86%', '1xNVIDIA A100-PCIE-40GB|87%', '1xNVIDIA A100-PCIE-40GB|88%', '1xNVIDIA A100-PCIE-40GB|90%', '1xNVIDIA A100-PCIE-40GB|91%', '1xNVIDIA A100-PCIE-40GB|92%', '1xNVIDIA A100-PCIE-40GB|93%', '1xNVIDIA A100-PCIE-40GB|94%', '1xNVIDIA A100-PCIE-40GB|95%', '1xNVIDIA A100-PCIE-40GB|96%', '1xNVIDIA A100-PCIE-40GB|97%', '1xNVIDIA A100-PCIE-40GB|98%'] ['AMD EPYC 7313 16-Core Processor']
- `steps.sh`: `steps() { run_pw vcrelax 2 python qeio.py converged vcrelax.out || { log "relaxation did not finish; later steps skipped"; return 0; } for t in scf bands; do python qeio.py newgeom $t.tmpl vcrelax.out > $t.in; done clean_tmp run_pw scf 2 || return 0 run_ppavg slab "$JOB" 4.8689 run_pw bands 2 }`

## Calculation `bands.out` (bands)

QE v.7.3.1 started 29Sep2026 9:19:10; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 61534.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled; GPU used by master process:. Completed: JOB DONE; terminated 13:57:57  29Sep2026; PWSCF time {'cpu': '1h50m', 'wall': '4h38m', 'calls': None}; output lines 1607.

**Input settings** (every namelist variable):

- &CONTROL: calculation = bands, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 199557
- &SYSTEM: ibrav = 0, nat = 96, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 328
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF, diagonalization = cg
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.33643106, 0.0, 0.0], [0.0, 10.334504206, 0.0], [0.0, 0.0, 34.87453893]]}
- K_POINTS: {"mode": "tpiba", "n": 21, "points_first_last": [[0.0, 0.0, 0.0, 1.0], [0.1739764, 0.1739764, 0.0, 1.0]], "path_points": [[0.0, 0.0, 0.0, 1.0], [0.02460398, 0.0, 0.0, 1.0], [0.04920796, 0.0, 0.0, 1.0], [0.07381193, 0.0, 0.0, 1.0], [0.09841591, 0.0, 0.0, 1.0], [0.12301989, 0.0, 0.0, 1.0], [0.14762387, 0.0, 0.0, 1.0], [0.17222785, 0.0, 0.0, 1.0], [0.19683182, 0.0, 0.0, 1.0], [0.2214358, 0.0, 0.0, 1.
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 96, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.5330  a.u.; unit-cell volume = 25140.0035 (a.u.)^3; number of atoms/cell = 96; number of atomic types = 3; number of electrons = 624.00; number of Kohn-Sham states = 328; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.533024, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=    21 (sum of weights 2.0); FFT: Dense  grid:  5746731 G-vectors     FFT dimensions: ( 150, 150, 500) / Smooth grid:  2031701 G-vectors     FFT dimensions: ( 108, 108, 360)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '6.38 GB', 'Estimated max dynamical RAM per process': '26.42 GB'}; start: ['Starting wfcs are  432 randomized atomic wfcs']
- Band-structure run: {'diag': 'CG style diagonalization', 'kpts_done': 21, 'ethr': 'ethr =  1.60E-13,  avg # of iterations = 78.1'}

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 21, "n_bands": 328, "n_occ": 312, "VBM_eV": -2.3403, "VBM_k_index": 0, "CBM_eV": -0.5518, "CBM_k_index": 0, "gap_eV": 1.7885, "direct_gap_min_eV": 1.7885, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.0092, "CB_width_bottom_band_eV": 0.2781, "E2_minus_E1_at_k0_eV": 1.4988}

**Warnings/errors**: message_from_routine x1 (first: line 34 'Message from routine setup:'); warning x4 (first: line 1 'WARNING: Skipping mount /tmp [tmp]: /tmp doesn't exist in container'); c_bands_not_converged x21 (first: line 521 'c_bands: 14 eigenvalues not converged'); ieee x3 (first: line 1604 'Warning: ieee_invalid is signaling'); discouraged x1 (first: line 35 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 27 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized'); fortran_stop x1 (first: line 1607 'FORTRAN STOP')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Calculation `scf.out` (scf/relax)

QE v.7.3.1 started 29Sep2026 8:47:27; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 68788.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled; GPU used by master process:. Completed: JOB DONE; terminated 9:18:57  29Sep2026; PWSCF time {'cpu': '10m46.87s', 'wall': '31m30.21s', 'calls': None}; output lines 2806.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 201460
- &SYSTEM: ibrav = 0, nat = 96, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 328
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.33643106, 0.0, 0.0], [0.0, 10.334504206, 0.0], [0.0, 0.0, 34.87453893]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 96, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.5330  a.u.; unit-cell volume = 25140.0035 (a.u.)^3; number of atoms/cell = 96; number of atomic types = 3; number of electrons = 624.00; number of Kohn-Sham states = 328; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.533024, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  5746731 G-vectors     FFT dimensions: ( 150, 150, 500) / Smooth grid:  2031701 G-vectors     FFT dimensions: ( 108, 108, 360)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '11.51 GB', 'Estimated max dynamical RAM per process': '41.02 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     623.9105, renormalised to     624.0000', 'Starting wfcs are  432 randomized atomic wfcs']

**Convergence** (1 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 54 | 4.3e-10 | -11888.81106216 |  | 0.000768 | 0.00036 | 0.006105 | 3.6e-05 | -0.32 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.00179, 0.0], HOMO_eV = -2.3402, LUMO_eV = -0.5517, E_Ry = -11888.81106216, E_all_electron_Ry = -289578.062985, acc_final_Ry = 4.3e-10, one_electron_Ry = -78759.3520355, hartree_Ry = 39691.25649261, xc_Ry = -1487.94939565, ewald_Ry = 35670.75711453, paw_one_center_Ry = -7003.52323816, converged_iterations = 54
- stress tensor (kbar): [[-0.06, 0.0, 0.0], [0.0, -0.13, 0.0], [0.0, 0.0, -0.77]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 328, "n_occ": 312, "VBM_eV": -2.3402, "VBM_k_index": 0, "CBM_eV": -0.5517, "CBM_k_index": 0, "gap_eV": 1.7885, "direct_gap_min_eV": 1.7885, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.03, "CB_width_bottom_band_eV": 0.8601, "E2_minus_E1_at_k0_eV": 1.4988}

**Warnings/errors**: message_from_routine x1 (first: line 30 'Message from routine setup:'); warning x4 (first: line 1 'WARNING: Skipping mount /tmp [tmp]: /tmp doesn't exist in container'); c_bands_not_converged x11 (first: line 791 'c_bands:  2 eigenvalues not converged'); ieee x3 (first: line 2803 'Warning: ieee_invalid is signaling'); discouraged x1 (first: line 31 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 27 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized'); fortran_stop x1 (first: line 2806 'FORTRAN STOP')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Calculation `vcrelax.out` (scf/relax)

QE v.7.3.1 started 28Sep2026 17:15:25; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 71328.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled; GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled. Completed: JOB DONE; terminated 8:47:21  29Sep2026; PWSCF time {'cpu': '8h15m', 'wall': '15h31m', 'calls': None}; output lines 50592.

**Input settings** (every namelist variable):

- &CONTROL: calculation = vc-relax, prefix = vcr, outdir = ./tmp, pseudo_dir = ./, verbosity = low, tprnfor = .true., tstress = .true., max_seconds = 257382, nstep = 300, etot_conv_thr = 1.0d-4, forc_conv_thr = 1.0d-3
- &SYSTEM: ibrav = 0, nat = 96, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 320
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- &IONS: ion_dynamics = bfgs
- &CELL: cell_dynamics = bfgs, cell_dofree = 2Dxy, press_conv_thr = 0.5
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.341816426, 0.0, 0.0], [0.0, 10.346773563, 0.0], [0.0, 0.0, 34.87453893]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 96, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.5432  a.u.; unit-cell volume = 25182.9640 (a.u.)^3; number of atoms/cell = 96; number of atomic types = 3; number of electrons = 624.00; number of Kohn-Sham states = 320; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; energy convergence thresh. = 1.0E-04; force convergence thresh. = 1.0E-03; press convergence thresh. = 5.0E-01; Exchange-correlation = SLA  PW   PBX  PBC; nstep = 300; celldm = [19.543201, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0) (re-read 3 times in the final SCF)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  5746731 G-vectors     FFT dimensions: ( 150, 150, 500) / Smooth grid:  2031701 G-vectors     FFT dimensions: ( 108, 108, 360)
- RAM (pw.x estimate): {'Estimated max dynamical RAM per process': '41.00 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     623.9105, renormalised to     624.0000', 'Starting wfcs are  432 randomized atomic wfcs', 'Initial potential from superposition of free atoms', 'starting charge     623.9105, renormalised to     624.0000', 'Starting wfcs are  432 randomized atomic wfcs']

**Convergence** (58 SCF + BFGS): bfgs converged in  57 scf cycles and  54 bfgs steps (criteria: energy <  1.0E-04 Ry, force <  1.0E-03 Ry/Bohr, cell <  5.0E-01 kbar) final energy None final enthalpy -11888.8112257101 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 62 | 4.9e-10 | -11888.5496256 | -11888.5496256045 | 0.01076 | 0.00383 | 0.064979 | 3.5e-05 | 2.74 | 3736.62872 | 10.3489, 10.3532 | 0.02185 |
| 1 | 30 | 6.6e-10 | -11888.55265957 | -11888.5526595661 | 0.008701 | 0.00362 | 0.061353 | 9e-05 | 2.9 | 3747.90458 | 10.3654, 10.3680 | 0.05042 |
| 2 | 30 | 4.1e-11 | -11888.55799897 | -11888.5579989736 | 0.007927 | 0.00295 | 0.050079 | 2.2e-05 | 1.48 | 3764.74514 | 10.3900, 10.3899 | 0.07563 |
| 3 | 35 | 6.2e-11 | -11888.56298355 | -11888.562983554 | 0.005741 | 0.00221 | 0.037487 | 2.2e-05 | -0.76 | 3774.82126 | 10.4049, 10.4028 | 0.04563 |
| 4 | 39 | 4e-11 | -11888.56545272 | -11888.5654527194 | 0.004904 | 0.00235 | 0.039832 | 1.8e-05 | -2.01 | 3784.7828 | 10.4198, 10.4153 | 0.05354 |
| 5 | 41 | 3.8e-11 | -11888.5689238 | -11888.5689238044 | 0.006287 | 0.00254 | 0.043072 | 2.1e-05 | -3.16 | 3790.813 | 10.4292, 10.4225 | 0.07735 |
| 6 | 38 | 5.1e-11 | -11888.57352428 | -11888.5735242816 | 0.007933 | 0.00288 | 0.048916 | 1.1e-05 | -3.79 | 3788.82922 | 10.4270, 10.4192 | 0.09562 |
| 7 | 42 | 7.5e-11 | -11888.57913209 | -11888.5791320912 | 0.007234 | 0.00338 | 0.057327 | 2.3e-05 | -3.47 | 3778.9746 | 10.4133, 10.4058 | 0.1132 |
| 8 | 37 | 4.9e-11 | -11888.58536902 | -11888.5853690212 | 0.009922 | 0.00393 | 0.066764 | 1.1e-05 | -2.36 | 3761.13177 | 10.3878, 10.3821 | 0.1284 |
| 9 | 41 | 6.2e-11 | -11888.59300693 | -11888.5930069345 | 0.01203 | 0.004 | 0.067813 | 2.6e-05 | -0.67 | 3745.04125 | 10.3647, 10.3607 | 0.1465 |
| 10 | 40 | 1.1e-10 | -11888.60044961 | -11888.6004496065 | 0.01118 | 0.00321 | 0.054559 | 2.1e-05 | 0.16 | 3734.95968 | 10.3500, 10.3476 | 0.04526 |
| 11 | 39 | 1e-10 | -11888.60429933 | -11888.6042993337 | 0.007327 | 0.0031 | 0.052533 | 3.5e-05 | 1.14 | 3738.10407 | 10.3550, 10.3512 | 0.06497 |
| 12 | 39 | 3.2e-11 | -11888.6061686 | -11888.6061686004 | 0.007302 | 0.00284 | 0.048244 | 2.3e-05 | -0.14 | 3743.41031 | 10.3631, 10.3578 | 0.02502 |
| 13 | 36 | 2.3e-11 | -11888.60822622 | -11888.6082262217 | 0.005897 | 0.00208 | 0.035277 | 1.8e-05 | -0.56 | 3747.21037 | 10.3699, 10.3615 | 0.02755 |
| 14 | 39 | 4.7e-11 | -11888.61092474 | -11888.6109247421 | 0.005938 | 0.00181 | 0.030668 | 2.4e-05 | -0.93 | 3747.9174 | 10.3733, 10.3601 | 0.04133 |
| 15 | 38 | 3.3e-11 | -11888.61359782 | -11888.6135978154 | 0.006098 | 0.00209 | 0.0354 | 2.1e-05 | -1.01 | 3745.92778 | 10.3740, 10.3539 | 0.0678 |
| 16 | 39 | 4e-11 | -11888.6163958 | -11888.6163957976 | 0.008354 | 0.00263 | 0.044621 | 1.4e-05 | -0.97 | 3743.02646 | 10.3743, 10.3456 | 0.06966 |
| 17 | 45 | 4.4e-11 | -11888.61942752 | -11888.619427522 | 0.008936 | 0.00257 | 0.043621 | 1.9e-05 | -0.65 | 3739.72566 | 10.3759, 10.3349 | 0.101 |
| 18 | 34 | 7e-11 | -11888.62301166 | -11888.6230116612 | 0.009166 | 0.00351 | 0.059582 | 1.4e-05 | -0.74 | 3738.7944 | 10.3834, 10.3248 | 0.1355 |
| 19 | 51 | 8.9e-11 | -11888.62793721 | -11888.6279372139 | 0.01097 | 0.00405 | 0.068696 | 2.4e-05 | 0.3 | 3741.73633 | 10.3960, 10.3204 | 0.1342 |
| 20 | 37 | 8.1e-11 | -11888.63214322 | -11888.6321432161 | 0.01334 | 0.00507 | 0.086076 | 2.5e-05 | -0.95 | 3751.23066 | 10.4151, 10.3277 | 0.1044 |
| 21 | 35 | 5.5e-11 | -11888.6424845 | -11888.6424844991 | 0.01483 | 0.00464 | 0.078739 | 3.1e-05 | -1.79 | 3755.76338 | 10.4270, 10.3283 | 0.1149 |
| 22 | 42 | 1.3e-10 | -11888.65154204 | -11888.6515420428 | 0.0162 | 0.00492 | 0.083497 | 1.8e-05 | -1.93 | 3760.69968 | 10.4402, 10.3289 | 0.1724 |
| 23 | 44 | 6.4e-11 | -11888.66579782 | -11888.6657978179 | 0.01224 | 0.00422 | 0.071554 | 1e-05 | -1.56 | 3758.16167 | 10.4590, 10.3033 | 0.482 |
| 24 | 40 | 2.4e-11 | -11888.61766097 | -11888.6176609714 | 0.08757 | 0.025 | 0.42383 | 1e-05 | -3.67 | 3760.27106 | 10.4434, 10.3245 | 0.08173 |
| 25 | 45 | 5.8e-11 | -11888.66887727 | -11888.6688772732 | 0.01983 | 0.00565 | 0.095808 | 1.4e-05 | -1.79 | 3749.95467 | 10.4355, 10.3039 | 0.2052 |
| 26 | 42 | 1.6e-10 | -11888.68001593 | -11888.6800159261 | 0.03168 | 0.00807 | 0.137034 | 4.3e-05 | -0.85 | 3732.33155 | 10.4120, 10.2787 | 0.132 |
| 27 | 41 | 2.9e-10 | -11888.69364623 | -11888.6936462349 | 0.02389 | 0.00629 | 0.106761 | 5.6e-05 | 1.12 | 3719.32096 | 10.3962, 10.2584 | 0.158 |
| 28 | 35 | 1.5e-10 | -11888.70658436 | -11888.7065843633 | 0.02361 | 0.00678 | 0.11505 | 2.2e-05 | 1.86 | 3711.53114 | 10.3855, 10.2475 | 0.1519 |
| 29 | 34 | 6.2e-11 | -11888.72249515 | -11888.7224951498 | 0.01934 | 0.00635 | 0.10774 | 1.5e-05 | 2.09 | 3706.02354 | 10.3885, 10.2294 | 0.4553 |
| 30 | 53 | 1.8e-10 | -11888.69897385 | -11888.6989738523 | 0.05482 | 0.0222 | 0.375949 | 3.1e-05 | -2.23 | 3709.91511 | 10.3864, 10.2421 | 0.1335 |
| 31 | 51 | 6.4e-11 | -11888.72919663 | -11888.7291966341 | 0.02197 | 0.00849 | 0.144105 | 2.3e-05 | 1.0 | 3715.12638 | 10.3954, 10.2477 | 0.1974 |
| 32 | 43 | 1.8e-10 | -11888.74659355 | -11888.7465935507 | 0.02096 | 0.00859 | 0.145735 | 5.6e-05 | -1.18 | 3721.35536 | 10.4023, 10.2581 | 0.08551 |
| 33 | 40 | 5.5e-11 | -11888.7604874 | -11888.7604874049 | 0.01216 | 0.00503 | 0.085429 | 2.8e-05 | -1.78 | 3718.54181 | 10.3982, 10.2543 | 0.1882 |
| 34 | 41 | 5.1e-11 | -11888.77132985 | -11888.771329853 | 0.01653 | 0.0062 | 0.105135 | 1.8e-05 | -2.78 | 3709.20992 | 10.3813, 10.2452 | 0.1174 |
| 35 | 33 | 7e-11 | -11888.78464974 | -11888.7846497399 | 0.01263 | 0.00426 | 0.072252 | 2.2e-05 | -1.31 | 3698.10113 | 10.3635, 10.2321 | 0.1182 |
| 36 | 35 | 6.2e-11 | -11888.79232437 | -11888.7923243704 | 0.009958 | 0.00384 | 0.065159 | 1.8e-05 | -0.41 | 3690.75995 | 10.3491, 10.2260 | 0.04382 |
| 37 | 49 | 9.6e-11 | -11888.79755632 | -11888.7975563231 | 0.006638 | 0.00291 | 0.049302 | 1.4e-05 | 1.42 | 3691.92239 | 10.3480, 10.2302 | 0.0757 |
| 38 | 35 | 4e-11 | -11888.79998935 | -11888.799989351 | 0.007793 | 0.00276 | 0.046759 | 1.9e-05 | 0.67 | 3699.3036 | 10.3541, 10.2447 | 0.04464 |
| 39 | 37 | 5.3e-11 | -11888.80256322 | -11888.8025632245 | 0.004535 | 0.00201 | 0.034128 | 1.4e-05 | 0.01 | 3708.25228 | 10.3579, 10.2657 | 0.06483 |
| 40 | 31 | 4e-11 | -11888.80449481 | -11888.8044948141 | 0.005647 | 0.00192 | 0.032548 | 3e-05 | -0.66 | 3711.1796 | 10.3548, 10.2769 | 0.03451 |
| 41 | 48 | 3.9e-11 | -11888.80576567 | -11888.8057656699 | 0.00481 | 0.00163 | 0.027731 | 5e-06 | -0.75 | 3713.96496 | 10.3460, 10.2933 | 0.05057 |
| 42 | 35 | 2.2e-11 | -11888.80727397 | -11888.8072739742 | 0.00451 | 0.00174 | 0.029496 | 1.9e-05 | -0.86 | 3715.43808 | 10.3388, 10.3046 | 0.03475 |
| 43 | 44 | 2.5e-11 | -11888.80814835 | -11888.8081483487 | 0.004309 | 0.00158 | 0.02685 | 1.3e-05 | -0.87 | 3717.23633 | 10.3333, 10.3150 | 0.03198 |
| 44 | 37 | 2.6e-11 | -11888.80881792 | -11888.8088179246 | 0.003061 | 0.00116 | 0.019693 | 6e-06 | -0.93 | 3719.0264 | 10.3304, 10.3229 | 0.02422 |
| 45 | 36 | 1.9e-11 | -11888.8093023 | -11888.8093022983 | 0.002147 | 0.000889 | 0.015094 | 6e-06 | -1.0 | 3720.22897 | 10.3284, 10.3283 | 0.01651 |
| 46 | 37 | 1.5e-11 | -11888.80969289 | -11888.8096928878 | 0.001944 | 0.000833 | 0.014141 | 1e-05 | -1.0 | 3720.48749 | 10.3258, 10.3316 | 0.01354 |
| 47 | 31 | 1.4e-11 | -11888.81003228 | -11888.8100322794 | 0.002849 | 0.000822 | 0.013957 | 8e-06 | -0.88 | 3719.76171 | 10.3226, 10.3328 | 0.01146 |
| 48 | 30 | 1.3e-11 | -11888.81031697 | -11888.8103169721 | 0.003282 | 0.000724 | 0.012294 | 1.2e-05 | -0.65 | 3718.54603 | 10.3194, 10.3326 | 0.01067 |
| 49 | 33 | 2.8e-11 | -11888.8105345 | -11888.8105344966 | 0.002337 | 0.000574 | 0.009735 | 1.3e-05 | -0.38 | 3717.77504 | 10.3179, 10.3320 | 0.009184 |
| 50 | 31 | 1.2e-11 | -11888.81067339 | -11888.810673388 | 0.001152 | 0.000464 | 0.007876 | 1e-05 | -0.2 | 3717.76495 | 10.3181, 10.3318 | 0.007714 |
| 51 | 37 | 8.6e-12 | -11888.8107802 | -11888.8107802049 | 0.0007991 | 0.00041 | 0.00695 | 9e-06 | -0.12 | 3718.66764 | 10.3202, 10.3322 | 0.00757 |
| 52 | 31 | 6.5e-12 | -11888.81088081 | -11888.8108808133 | 0.00121 | 0.000403 | 0.006834 | 7e-06 | -0.12 | 3720.34979 | 10.3241, 10.3330 | 0.01195 |
| 53 | 37 | 5.8e-12 | -11888.81098371 | -11888.8109837145 | 0.001348 | 0.000416 | 0.007061 | 6e-06 | -0.18 | 3722.33254 | 10.3287, 10.3339 | 0.01413 |
| 54 | 32 | 3.1e-12 | -11888.81107521 | -11888.8110752081 | 0.001211 | 0.000402 | 0.006817 | 5e-06 | -0.25 | 3724.05281 | 10.3329, 10.3344 | 0.01293 |
| 55 | 37 | 4.7e-12 | -11888.81115338 | -11888.8111533811 | 0.001197 | 0.00037 | 0.006275 | 6e-06 | -0.3 | 3725.36417 | 10.3364, 10.3345 | 0.01091 |
| 56 | 33 | 3.7e-12 | -11888.81122571 |  | 0.0007678 | 0.00036 | 0.006106 | 9e-06 | -0.31 |  |  |  |
| 57 | 71 | 7.3e-12 | -11888.81106217 |  | 0.000768 | 0.00036 | 0.006106 | 6e-06 | -0.31 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.00179, 0.0], HOMO_eV = -2.3403, LUMO_eV = -0.5518, E_Ry = -11888.81106217, E_all_electron_Ry = -289578.062986, acc_final_Ry = 7.3e-12, one_electron_Ry = -78759.35282322, hartree_Ry = 39691.2573983, xc_Ry = -1487.94948743, ewald_Ry = 35670.75711171, paw_one_center_Ry = -7003.52326153, converged_iterations = 71
- stress tensor (kbar): [[-0.04, 0.0, 0.0], [0.0, -0.12, 0.0], [0.0, 0.0, -0.75]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 320, "n_occ": 312, "VBM_eV": -2.3403, "VBM_k_index": 0, "CBM_eV": -0.5518, "CBM_k_index": 0, "gap_eV": 1.7885, "direct_gap_min_eV": 1.7885, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.03, "CB_width_bottom_band_eV": 0.8601, "E2_minus_E1_at_k0_eV": 1.4988}

**Final geometry** (vs `vcrelax_initial.in`): {"n_atoms": 96, "composition": {"H": 24, "In": 24, "O": 48}, "cell_lengths_A": [10.33643, 10.3345, 34.87454], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3725.3642, "density_g_cm3": 1.5814, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 144, "min": 2.1647, "mean": 2.219, "max": 2.3078, "std": 0.0389, "CN_In_hist": {"6": 24}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9719, "mean": 0.9775, "max": 0.9864, "std": 0.0064, "CN_O_hist": {"0": 24, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 24}, "slab": {"vacuum_A": 25.571, "extent_A": 9.303, "thickness_H_H_A": 9.3033, "thickness_O_O_A": 7.8762, "thickness_In_In_A": 5.1515}, "displacement_vs_initial": {"max_A": 1.306, "atom": "H73", "mean_A": 0.2437, "n_gt_0p1_A": 40, "by_element_max_A": {"H": 1.306, "In": 0.0343, "O": 0.3567}, "outer_3A_mean_A": 0.3517, "interior_mean_A": 0.0276}, "reference_input": "vcrelax_initial.in"}

**Warnings/errors**: message_from_routine x1 (first: line 29 'Message from routine setup:'); warning x3 (first: line 50589 'Warning: ieee_invalid is signaling'); c_bands_not_converged x22 (first: line 393 'c_bands:  2 eigenvalues not converged'); ieee x3 (first: line 50589 'Warning: ieee_invalid is signaling'); discouraged x1 (first: line 30 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized'); fortran_stop x1 (first: line 50592 'FORTRAN STOP')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `bands.in`: {"n_atoms": 96, "composition": {"H": 24, "In": 24, "O": 48}, "cell_lengths_A": [10.33643, 10.3345, 34.87454], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3725.3642, "density_g_cm3": 1.5814, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 144, "min": 2.1647, "mean": 2.219, "max": 2.3078, "std": 0.0389, "CN_In_hist": {"6": 24}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9719, "mean": 0.9775, "max": 0.9864, "std": 0.0064, "CN_O_hist": {"0": 24, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 24}, "slab": {"vacuum_A": 25.571, "extent_A": 9.303, "thickness_H_H_A": 9.3033, "thickness_O_O_A": 7.8762, "thickness_In_In_A": 5.1515}}
- `scf.in`: {"n_atoms": 96, "composition": {"H": 24, "In": 24, "O": 48}, "cell_lengths_A": [10.33643, 10.3345, 34.87454], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3725.3642, "density_g_cm3": 1.5814, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 144, "min": 2.1647, "mean": 2.219, "max": 2.3078, "std": 0.0389, "CN_In_hist": {"6": 24}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9719, "mean": 0.9775, "max": 0.9864, "std": 0.0064, "CN_O_hist": {"0": 24, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 24}, "slab": {"vacuum_A": 25.571, "extent_A": 9.303, "thickness_H_H_A": 9.3033, "thickness_O_O_A": 7.8762, "thickness_In_In_A": 5.1515}}
- `vcrelax.in`: {"n_atoms": 96, "composition": {"H": 24, "In": 24, "O": 48}, "cell_lengths_A": [10.34182, 10.34677, 34.87454], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3731.7303, "density_g_cm3": 1.5787, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 144, "min": 2.1514, "mean": 2.2111, "max": 2.299, "std": 0.0377, "CN_In_hist": {"6": 24}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9717, "mean": 0.9727, "max": 0.9732, "std": 0.0007, "CN_O_hist": {"0": 24, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 24}, "slab": {"vacuum_A": 25.273, "extent_A": 9.601, "thickness_H_H_A": 9.6012, "thickness_O_O_A": 7.9489, "thickness_In_In_A": 5.1443}}
- `vcrelax_initial.in`: {"n_atoms": 96, "composition": {"H": 24, "In": 24, "O": 48}, "cell_lengths_A": [10.30609, 10.30609, 34.87454], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3704.2164, "density_g_cm3": 1.5904, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 144, "min": 2.1671, "mean": 2.2189, "max": 2.2561, "std": 0.0317, "CN_In_hist": {"6": 24}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.97, "mean": 0.97, "max": 0.97, "std": 0.0, "CN_O_hist": {"0": 24, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 24}, "slab": {"vacuum_A": 25.0, "extent_A": 9.875, "thickness_H_H_A": 9.8745, "thickness_O_O_A": 8.0332, "thickness_In_In_A": 5.153}}

Geometry consistency (input of the follow-on step vs relax final coordinates): {"scf.in vs final of vcrelax.out": {"max_pos_diff_A": 0.0, "max_cell_diff_A": 0.0}, "bands.in vs final of vcrelax.out": {"max_pos_diff_A": 0.0, "max_cell_diff_A": 0.0}}
- `avg_slab1_relax_gpu.in` input: `1 slab1_relax_gpu_v.pp 1.0 3000 3 4.8689`
- `pp_slab1_relax_gpu.in` input: `&INPUTPP prefix = 'slab', outdir = './tmp', filplot = 'slab1_relax_gpu_v.pp', plot_num = 11 /`
- `avg_slab1_relax_gpu.out`: done False; Program AVERAGE v.7.5 starts on 29Sep2026 at  9:19: 7 / Reading header from file  slab1_relax_gpu_v.pp
- `pp_slab1_relax_gpu.out`: done False; Program POST-PROC v.7.5 starts on 29Sep2026 at  9:19: 1 / Reading xml data from directory: / terminated by signals sent by prterun (as reported here).

## Other files

- `.fetched`: ''

## Checks against RESULTS_LOG

| quantity | re-derived | logged | reference | status |
|---|---|---|---|---|
| BFGS steps (GPU) | 54 | 54 | RESULTS_LOG.md:645 | match |
| GPU model | True | True | RESULTS_LOG.md:645 | match |
| final enthalpy (Ry) | -11888.8112257101 | -11888.81122571 | RESULTS_LOG.md:646 | match |
| total force at convergence (Ry/bohr) | 0.006106 | 0.0061 | RESULTS_LOG.md:647 | match |
| in-plane a (A) | 10.33643 | 10.336 | RESULTS_LOG.md:648 | match |
| in-plane b (A) (last-digit rounding allowed) | 10.3345 | 10.335 | RESULTS_LOG.md:648 | match |
