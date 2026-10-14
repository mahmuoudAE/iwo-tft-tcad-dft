# slab2_relax_c2

**Purpose.** vc-relax (2Dxy) of the 2 nm slab on one H100 NVL (rerun after the lost slab2_relax_x1), final SCF, planar average, bands.

Folder `cern_htcondor/results/slab2_relax_c2`; data `runs_sep_oct/out/slab2_relax_c2.json` (+ `slab2_relax_c2_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| avg_slab2_relax_c2.in | 40 | e1f1019078c6d006 | loose | avg_in |
| avg_slab2_relax_c2.out | 1385 | 2d28a9c785f509b6 | loose | avg_out |
| bands.in | 14223 | e8a86d0e59685626 | loose | pw_in |
| bands.out | 182819 | 5c46e47cd7f2e2f0 | loose | pw_out |
| bands.tmpl | 9470 | 13395163e6b38e83 | loose | pw_tmpl |
| pp_slab2_relax_c2.in | 95 | dd1e8cd848541336 | loose | post_in |
| pp_slab2_relax_c2.out | 2366 | a6a3fb072a0ef827 | loose | pp_out |
| scf.in | 13391 | 67ca29f51c2f26dc | loose | pw_in |
| scf.out | 257899 | e271abc8511b18b6 | loose | pw_out |
| scf.tmpl | 8638 | 234695783e58fae4 | loose | pw_tmpl |
| slab2_relax_c2_avg.dat | 138000 | 93db87f1927dba51 | loose | avg_dat |
| slab2_relax_c2_driver.log | 1047 | c702fc0e8a943892 | loose | driver |
| steps.sh | 310 | a96f86388fae0db4 | loose | steps |
| vcrelax.in | 13565 | 9ebd7cc47ea9ab74 | loose | pw_in |
| vcrelax.out | 5253552 | 14c606ae09e594f5 | loose | pw_out |
| vcrelax_initial.in | 8812 | afbeea9e49456bd6 | loose | pw_in |

Tarball `slab2_relax_c2_results.tar.gz` (1223449 B, sha256 198f6be943256f98): 16 members; identical to the loose copy: 16; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0

## Resources and run history

- `slab2_relax_c2_driver.log`: host b9pgpun501.cern.ch, 33 CPUs, wall limit 259200 s, GPU: 1 GPU(s), NVIDIA H100 NVL, 95830 MiB, job total 182892 s, start 2026-10-02T07:12:04Z
  - step vcrelax: -nk 2, max_seconds 257382, start 2026-10-02T07:12:22Z, end 2026-10-04T00:40:42Z, rc 0, PWSCF        :   1d16h53m CPU   1d17h28m WALL
  - step scf: -nk 2, max_seconds 108080, start 2026-10-04T00:40:44Z, end 2026-10-04T01:36:44Z, rc 0, PWSCF        :  46m31.63s CPU  55m55.64s WALL
  - step bands: -nk 2, max_seconds 104693, start 2026-10-04T01:37:11Z, end 2026-10-04T10:00:15Z, rc 0, PWSCF        :      8h15m CPU      8h22m WALL
  - log: tmp/slab.save/charge-density.hdf5: ngm_g 7413139, nspin 1, gamma_only False, first G [0, 0, 0], rho(G) 0.04095077
  - log: [2026-10-04T01:36:48Z] charge density converted to HDF5 for pp.x
  - log: [2026-10-04T01:37:11Z] planar average slab2_relax_c2: 3000 lines
- HTCondor slab2_relax_c2 12806569.0: 33 CPUs, 1 GPU; seen 2026-10-02T02:41:56Z to 2026-10-04T09:57:26Z (311 samples); states {'1': 10, '2': 301} (1 idle, 2 running, 3 removed, 5 held); max scf_it 3611, max BFGS 69; steps ['vcrelax', 'scf', 'bands']; hw ['1xNVIDIA H100 NVL|0%', '1xNVIDIA H100 NVL|10%', '1xNVIDIA H100 NVL|100%', '1xNVIDIA H100 NVL|11%', '1xNVIDIA H100 NVL|12%', '1xNVIDIA H100 NVL|13%', '1xNVIDIA H100 NVL|15%', '1xNVIDIA H100 NVL|16%', '1xNVIDIA H100 NVL|19%', '1xNVIDIA H100 NVL|28%', '1xNVIDIA H100 NVL|32%', '1xNVIDIA H100 NVL|33%', '1xNVIDIA H100 NVL|36%', '1xNVIDIA H100 NVL|4%', '1xNVIDIA H100 NVL|5%', '1xNVIDIA H100 NVL|6%', '1xNVIDIA H100 NVL|7%', '1xNVIDIA H100 NVL|71%', '1xNVIDIA H100 NVL|72%', '1xNVIDIA H100 NVL|73%', '1xNVIDIA H100 NVL|74%', '1xNVIDIA H100 NVL|75%', '1xNVIDIA H100 NVL|76%', '1xNVIDIA H100 NVL|77%', '1xNVIDIA H100 NVL|78%', '1xNVIDIA H100 NVL|79%', '1xNVIDIA H100 NVL|8%', '1xNVIDIA H100 NVL|82%', '1xNVIDIA H100 NVL|9%', '1xNVIDIA H100 NVL|92%', '1xNVIDIA H100 NVL|93%', '1xNVIDIA H100 NVL|94%', '1xNVIDIA H100 NVL|96%', '1xNVIDIA H100 NVL|97%', '1xNVIDIA H100 NVL|98%', '1xNVIDIA H100 NVL|99%'] ['Intel(R) Xeon(R) Platinum 8468']
- `steps.sh`: `steps() { run_pw vcrelax 2 python qeio.py converged vcrelax.out || { log "relaxation did not finish; later steps skipped"; return 0; } for t in scf bands; do python qeio.py newgeom $t.tmpl vcrelax.out > $t.in; done clean_tmp run_pw scf 2 || return 0 run_ppavg slab "$JOB" 4.8689 run_pw bands 2 }`

## Calculation `bands.out` (bands)

QE v.7.3.1 started 4Oct2026 3:37:13; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 151093.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled; GPU used by master process:. Completed: JOB DONE; terminated 11:59:29   4Oct2026; PWSCF time {'cpu': '8h15m', 'wall': '8h22m', 'calls': None}; output lines 2691.

**Input settings** (every namelist variable):

- &CONTROL: calculation = bands, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 104693
- &SYSTEM: ibrav = 0, nat = 176, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 680
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF, diagonalization = cg
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.317916322, 0.0, 0.0], [0.0, 10.308491343, 0.0], [0.0, 0.0, 45.18062913]]}
- K_POINTS: {"mode": "tpiba", "n": 21, "points_first_last": [[0.0, 0.0, 0.0, 1.0], [0.1739764, 0.1739764, 0.0, 1.0]], "path_points": [[0.0, 0.0, 0.0, 1.0], [0.02460398, 0.0, 0.0, 1.0], [0.04920796, 0.0, 0.0, 1.0], [0.07381193, 0.0, 0.0, 1.0], [0.09841591, 0.0, 0.0, 1.0], [0.12301989, 0.0, 0.0, 1.0], [0.14762387, 0.0, 0.0, 1.0], [0.17222785, 0.0, 0.0, 1.0], [0.19683182, 0.0, 0.0, 1.0], [0.2214358, 0.0, 0.0, 1.
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 176, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4980  a.u.; unit-cell volume = 32429.1815 (a.u.)^3; number of atoms/cell = 176; number of atomic types = 3; number of electrons = 1328.00; number of Kohn-Sham states = 680; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.498036, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=    21 (sum of weights 2.0); FFT: Dense  grid:  7413139 G-vectors     FFT dimensions: ( 150, 150, 648) / Smooth grid:  2620949 G-vectors     FFT dimensions: ( 108, 108, 480)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '14.64 GB', 'Estimated max dynamical RAM per process': '45.79 GB'}; start: ['Starting wfcs are  912 randomized atomic wfcs']
- Band-structure run: {'diag': 'CG style diagonalization', 'kpts_done': 21, 'ethr': 'ethr =  1.00E-13,  avg # of iterations = 77.7'}

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 21, "n_bands": 680, "n_occ": 664, "VBM_eV": 0.0475, "VBM_k_index": 0, "CBM_eV": 1.2714, "CBM_k_index": 0, "gap_eV": 1.2239, "direct_gap_min_eV": 1.2239, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.0114, "CB_width_bottom_band_eV": 0.3631, "E2_minus_E1_at_k0_eV": 0.7191}

**Warnings/errors**: message_from_routine x1 (first: line 34 'Message from routine setup:'); warning x4 (first: line 1 'WARNING: Skipping mount /tmp [tmp]: /tmp doesn't exist in container'); c_bands_not_converged x21 (first: line 681 'c_bands: 11 eigenvalues not converged'); ieee x3 (first: line 2688 'Warning: ieee_invalid is signaling'); discouraged x1 (first: line 35 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 27 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized'); fortran_stop x1 (first: line 2691 'FORTRAN STOP')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Calculation `scf.out` (scf/relax)

QE v.7.3.1 started 4Oct2026 2:40:46; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 108583.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled; GPU used by master process:. Completed: JOB DONE; terminated 3:36:41   4Oct2026; PWSCF time {'cpu': '46m31.63s', 'wall': '55m55.64s', 'calls': None}; output lines 4283.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 108080
- &SYSTEM: ibrav = 0, nat = 176, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 680
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.317916322, 0.0, 0.0], [0.0, 10.308491343, 0.0], [0.0, 0.0, 45.18062913]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 176, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4980  a.u.; unit-cell volume = 32429.1815 (a.u.)^3; number of atoms/cell = 176; number of atomic types = 3; number of electrons = 1328.00; number of Kohn-Sham states = 680; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.498036, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  7413139 G-vectors     FFT dimensions: ( 150, 150, 648) / Smooth grid:  2620949 G-vectors     FFT dimensions: ( 108, 108, 480)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '28.14 GB', 'Estimated max dynamical RAM per process': '82.10 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge    1327.7914, renormalised to    1328.0000', 'Starting wfcs are  912 randomized atomic wfcs']

**Convergence** (1 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 75 | 7.5e-10 | -27035.66492689 |  | 0.0008609 | 0.000311 | 0.007153 | 0.000103 | -0.4 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.002107, 0.0], HOMO_eV = 0.0473, LUMO_eV = 1.2712, E_Ry = -27035.66492689, E_all_electron_Ry = -673235.702643, acc_final_Ry = 7.5e-10, one_electron_Ry = -272838.07837541, hartree_Ry = 137216.09044251, xc_Ry = -3329.72167443, ewald_Ry = 128104.25303152, paw_one_center_Ry = -16188.20835107, converged_iterations = 75
- stress tensor (kbar): [[0.1, 0.0, 0.0], [0.0, 0.16, 0.0], [0.0, 0.0, -1.46]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 680, "n_occ": 664, "VBM_eV": 0.0473, "VBM_k_index": 0, "CBM_eV": 1.2712, "CBM_k_index": 0, "gap_eV": 1.2239, "direct_gap_min_eV": 1.2239, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.0135, "CB_width_bottom_band_eV": 1.0517, "E2_minus_E1_at_k0_eV": 0.7192}

**Warnings/errors**: message_from_routine x1 (first: line 30 'Message from routine setup:'); warning x4 (first: line 1 'WARNING: Skipping mount /tmp [tmp]: /tmp doesn't exist in container'); c_bands_not_converged x2 (first: line 865 'c_bands:  1 eigenvalues not converged'); ieee x3 (first: line 4280 'Warning: ieee_invalid is signaling'); discouraged x1 (first: line 31 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 27 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized'); fortran_stop x1 (first: line 4283 'FORTRAN STOP')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Calculation `vcrelax.out` (scf/relax)

QE v.7.3.1 started 2Oct2026 9:12:24; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 37861.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled; GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled. Completed: JOB DONE; terminated 2:40:25   4Oct2026; PWSCF time {'cpu': '1d16h53m', 'wall': '1d17h28m', 'calls': None}; output lines 96366.

**Input settings** (every namelist variable):

- &CONTROL: calculation = vc-relax, prefix = vcr, outdir = ./tmp, pseudo_dir = ./, verbosity = low, tprnfor = .true., tstress = .true., max_seconds = 257382, nstep = 300, etot_conv_thr = 1.0d-4, forc_conv_thr = 1.0d-3
- &SYSTEM: ibrav = 0, nat = 176, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 672
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- &IONS: ion_dynamics = bfgs
- &CELL: cell_dynamics = bfgs, cell_dofree = 2Dxy, press_conv_thr = 0.5
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.328080023, 0.0, 0.0], [0.0, 10.325066496, 0.0], [0.0, 0.0, 45.18062913]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 176, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.5172  a.u.; unit-cell volume = 32513.3206 (a.u.)^3; number of atoms/cell = 176; number of atomic types = 3; number of electrons = 1328.00; number of Kohn-Sham states = 672; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; energy convergence thresh. = 1.0E-04; force convergence thresh. = 1.0E-03; press convergence thresh. = 5.0E-01; Exchange-correlation = SLA  PW   PBX  PBC; nstep = 300; celldm = [19.517243, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0) (re-read 3 times in the final SCF)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  7413139 G-vectors     FFT dimensions: ( 150, 150, 648) / Smooth grid:  2620949 G-vectors     FFT dimensions: ( 108, 108, 480)
- RAM (pw.x estimate): {'Estimated max dynamical RAM per process': '82.07 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge    1327.7914, renormalised to    1328.0000', 'Starting wfcs are  912 randomized atomic wfcs', 'Initial potential from superposition of free atoms', 'starting charge    1327.7914, renormalised to    1328.0000', 'Starting wfcs are  912 randomized atomic wfcs']

**Convergence** (73 SCF + BFGS): bfgs converged in  72 scf cycles and  70 bfgs steps (criteria: energy <  1.0E-04 Ry, force <  1.0E-03 Ry/Bohr, cell <  5.0E-01 kbar) final energy None final enthalpy -27035.6654809032 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 93 | 4.7e-10 | -27035.26282772 | -27035.2628277204 | 0.02143 | 0.00596 | 0.137062 | 8.5e-05 | -2.68 | 4819.17263 | 10.3291, 10.3266 | 0.02483 |
| 1 | 47 | 7.8e-10 | -27035.27774175 | -27035.277741752 | 0.01201 | 0.00431 | 0.098965 | 7.9e-05 | -2.86 | 4820.11372 | 10.3299, 10.3278 | 0.02731 |
| 2 | 52 | 1e-10 | -27035.29081595 | -27035.2908159487 | 0.01049 | 0.00363 | 0.083508 | 5.2e-05 | -3.48 | 4821.02226 | 10.3304, 10.3293 | 0.04097 |
| 3 | 41 | 7.4e-11 | -27035.30503536 | -27035.3050353553 | 0.0146 | 0.00417 | 0.0958 | 4.2e-05 | -3.48 | 4821.8331 | 10.3307, 10.3308 | 0.06146 |
| 4 | 45 | 1.5e-10 | -27035.32165062 | -27035.3216506166 | 0.02113 | 0.00492 | 0.113028 | 2.1e-05 | -3.59 | 4822.29245 | 10.3302, 10.3322 | 0.0922 |
| 5 | 40 | 1.4e-10 | -27035.34101592 | -27035.3410159238 | 0.02174 | 0.00512 | 0.117628 | 4.2e-05 | -3.41 | 4821.45819 | 10.3288, 10.3318 | 0.06364 |
| 6 | 62 | 1.1e-10 | -27035.3532864 | -27035.3532864027 | 0.01275 | 0.00358 | 0.082367 | 4e-05 | -2.82 | 4819.46482 | 10.3267, 10.3297 | 0.04671 |
| 7 | 59 | 1.2e-10 | -27035.36118316 | -27035.3611831563 | 0.007997 | 0.00249 | 0.057195 | 4.8e-05 | -2.1 | 4817.56922 | 10.3249, 10.3274 | 0.03198 |
| 8 | 49 | 5.8e-11 | -27035.36537123 | -27035.3653712292 | 0.008965 | 0.00291 | 0.066977 | 3e-05 | -1.67 | 4814.89254 | 10.3224, 10.3242 | 0.04682 |
| 9 | 45 | 6.4e-11 | -27035.37168204 | -27035.3716820365 | 0.01485 | 0.00342 | 0.078513 | 2.5e-05 | -1.29 | 4811.76185 | 10.3196, 10.3202 | 0.07021 |
| 10 | 59 | 8.9e-11 | -27035.38147317 | -27035.381473167 | 0.01699 | 0.00389 | 0.089455 | 2.3e-05 | -0.83 | 4809.03777 | 10.3173, 10.3167 | 0.1053 |
| 11 | 48 | 7.4e-11 | -27035.39361805 | -27035.3936180549 | 0.0134 | 0.00422 | 0.096874 | 2.1e-05 | -0.65 | 4808.20298 | 10.3172, 10.3150 | 0.1108 |
| 12 | 56 | 1.3e-10 | -27035.40450571 | -27035.4045057081 | 0.007417 | 0.00304 | 0.069845 | 6.7e-05 | -0.36 | 4809.85188 | 10.3191, 10.3166 | 0.1014 |
| 13 | 69 | 6e-11 | -27035.41019606 | -27035.4101960577 | 0.01624 | 0.00464 | 0.106611 | 2e-05 | -1.15 | 4814.4328 | 10.3242, 10.3214 | 0.06072 |
| 14 | 45 | 5.7e-11 | -27035.41887019 | -27035.4188701903 | 0.01208 | 0.0035 | 0.080399 | 2.5e-05 | -1.33 | 4817.01519 | 10.3271, 10.3240 | 0.07139 |
| 15 | 63 | 7.5e-11 | -27035.42570444 | -27035.4257044351 | 0.009184 | 0.00279 | 0.064101 | 4.2e-05 | -1.53 | 4819.08372 | 10.3298, 10.3257 | 0.07855 |
| 16 | 55 | 4.2e-11 | -27035.43238953 | -27035.4323895281 | 0.007612 | 0.00238 | 0.054648 | 2e-05 | -1.57 | 4819.81847 | 10.3315, 10.3256 | 0.1065 |
| 17 | 65 | 6.1e-11 | -27035.43832574 | -27035.4383257431 | 0.006285 | 0.00245 | 0.056384 | 4e-05 | -1.55 | 4819.00785 | 10.3311, 10.3243 | 0.06143 |
| 18 | 45 | 4.1e-11 | -27035.44166737 | -27035.4416673702 | 0.005536 | 0.00198 | 0.045474 | 1.6e-05 | -1.36 | 4816.27775 | 10.3285, 10.3210 | 0.04548 |
| 19 | 43 | 4.8e-11 | -27035.44556872 | -27035.4455687177 | 0.007594 | 0.00205 | 0.047151 | 1.9e-05 | -0.81 | 4814.66118 | 10.3269, 10.3192 | 0.06533 |
| 20 | 50 | 5.9e-11 | -27035.44760063 | -27035.4476006343 | 0.007572 | 0.00238 | 0.054646 | 3e-05 | -1.14 | 4813.59493 | 10.3252, 10.3186 | 0.04236 |
| 21 | 51 | 6.3e-11 | -27035.45002736 | -27035.4500273638 | 0.005399 | 0.00182 | 0.041777 | 2e-05 | -0.85 | 4813.59684 | 10.3244, 10.3194 | 0.04021 |
| 22 | 46 | 3e-11 | -27035.45321347 | -27035.4532134727 | 0.0045 | 0.00145 | 0.033388 | 3.3e-05 | -0.83 | 4814.41958 | 10.3244, 10.3211 | 0.05558 |
| 23 | 37 | 2.7e-11 | -27035.45649704 | -27035.456497037 | 0.004115 | 0.00145 | 0.033219 | 1.3e-05 | -0.92 | 4815.58591 | 10.3253, 10.3227 | 0.08417 |
| 24 | 41 | 3.6e-11 | -27035.45903662 | -27035.459036623 | 0.004592 | 0.00169 | 0.038737 | 3e-05 | -1.03 | 4817.04921 | 10.3269, 10.3242 | 0.09007 |
| 25 | 48 | 1.6e-11 | -27035.46150245 | -27035.4615024514 | 0.004474 | 0.00169 | 0.038929 | 9e-06 | -1.06 | 4818.53268 | 10.3290, 10.3253 | 0.07274 |
| 26 | 39 | 2.1e-11 | -27035.46393986 | -27035.4639398607 | 0.004448 | 0.00146 | 0.033441 | 2.5e-05 | -0.95 | 4819.89269 | 10.3315, 10.3257 | 0.06503 |
| 27 | 53 | 3.9e-11 | -27035.46637557 | -27035.4663755736 | 0.005151 | 0.00145 | 0.033234 | 1.8e-05 | -0.81 | 4821.25146 | 10.3345, 10.3256 | 0.05425 |
| 28 | 36 | 3.8e-11 | -27035.46872589 | -27035.4687258929 | 0.005812 | 0.00173 | 0.039694 | 2e-05 | -0.69 | 4822.73579 | 10.3385, 10.3249 | 0.08013 |
| 29 | 45 | 4.1e-11 | -27035.47137814 | -27035.4713781361 | 0.006663 | 0.00193 | 0.044328 | 1.8e-05 | -0.84 | 4823.80611 | 10.3428, 10.3228 | 0.09586 |
| 30 | 43 | 5.8e-11 | -27035.47419568 | -27035.4741956761 | 0.00741 | 0.00249 | 0.057112 | 2.7e-05 | -0.69 | 4823.93503 | 10.3461, 10.3198 | 0.1068 |
| 31 | 50 | 4.3e-11 | -27035.47694822 | -27035.4769482175 | 0.01399 | 0.00333 | 0.076611 | 2.4e-05 | -1.31 | 4821.53437 | 10.3446, 10.3162 | 0.03802 |
| 32 | 37 | 1.3e-10 | -27035.48153914 | -27035.4815391359 | 0.008068 | 0.00283 | 0.065052 | 6.4e-05 | -1.13 | 4817.76663 | 10.3431, 10.3096 | 0.114 |
| 33 | 59 | 4.9e-11 | -27035.48776407 | -27035.4877640742 | 0.01297 | 0.00367 | 0.084276 | 3.3e-05 | -1.11 | 4810.23137 | 10.3369, 10.2996 | 0.1891 |
| 34 | 37 | 9.5e-11 | -27035.49713499 | -27035.4971349877 | 0.02755 | 0.00605 | 0.139113 | 3.7e-05 | -0.9 | 4804.52631 | 10.3279, 10.2964 | 0.0816 |
| 35 | 47 | 2.6e-10 | -27035.50550597 | -27035.5055059684 | 0.01081 | 0.00403 | 0.092561 | 6.2e-05 | 0.18 | 4800.0265 | 10.3232, 10.2914 | 0.2447 |
| 36 | 51 | 1.1e-10 | -27035.51659099 | -27035.5165909931 | 0.03521 | 0.0072 | 0.165429 | 4.5e-05 | -0.2 | 4802.89805 | 10.3244, 10.2965 | 0.1273 |
| 37 | 45 | 2.2e-10 | -27035.53358456 | -27035.5335845588 | 0.02785 | 0.00534 | 0.122697 | 6.6e-05 | -0.21 | 4803.76101 | 10.3236, 10.2991 | 0.1571 |
| 38 | 41 | 2.4e-10 | -27035.54666428 | -27035.5466642792 | 0.02429 | 0.00487 | 0.111982 | 5e-05 | -0.49 | 4804.37915 | 10.3225, 10.3015 | 0.1728 |
| 39 | 48 | 2e-10 | -27035.56173334 | -27035.5617333373 | 0.01974 | 0.00439 | 0.100969 | 4.9e-05 | -0.83 | 4803.88453 | 10.3205, 10.3024 | 0.2593 |
| 40 | 44 | 1.5e-10 | -27035.57638142 | -27035.5763814228 | 0.03214 | 0.00704 | 0.161859 | 5.4e-05 | -2.01 | 4810.85266 | 10.3240, 10.3139 | 0.2916 |
| 41 | 45 | 2.6e-10 | -27035.53850722 | -27035.5385072227 | 0.07567 | 0.0184 | 0.422849 | 4.1e-05 | -1.58 | 4806.12133 | 10.3216, 10.3061 | 0.09368 |
| 42 | 72 | 2e-10 | -27035.5869208 | -27035.5869208026 | 0.01367 | 0.00439 | 0.100922 | 7e-05 | -1.87 | 4804.27183 | 10.3198, 10.3040 | 0.1454 |
| 43 | 47 | 7.5e-11 | -27035.59750855 | -27035.597508553 | 0.01824 | 0.00507 | 0.116488 | 3.5e-05 | -2.5 | 4799.5905 | 10.3167, 10.2970 | 0.09067 |
| 44 | 42 | 1.6e-10 | -27035.61415256 | -27035.6141525629 | 0.01905 | 0.00508 | 0.116813 | 7e-05 | -2.07 | 4792.28641 | 10.3106, 10.2874 | 0.1194 |
| 45 | 36 | 7e-11 | -27035.62680083 | -27035.6268008304 | 0.01201 | 0.00383 | 0.087955 | 3e-05 | -1.3 | 4788.46578 | 10.3059, 10.2839 | 0.1008 |
| 46 | 40 | 1.1e-10 | -27035.63497276 | -27035.6349727591 | 0.009056 | 0.00297 | 0.068238 | 4.9e-05 | -0.75 | 4783.4406 | 10.2968, 10.2822 | 0.1961 |
| 47 | 41 | 7.7e-11 | -27035.63846315 | -27035.6384631474 | 0.02372 | 0.00593 | 0.136262 | 3.5e-05 | -1.37 | 4784.26125 | 10.2925, 10.2883 | 0.04889 |
| 48 | 52 | 1.4e-10 | -27035.64443719 | -27035.6444371864 | 0.01592 | 0.00437 | 0.100427 | 5.6e-05 | 0.26 | 4785.95996 | 10.2932, 10.2913 | 0.0472 |
| 49 | 56 | 9.4e-11 | -27035.64928375 | -27035.649283752 | 0.005878 | 0.00199 | 0.045683 | 3.1e-05 | -0.42 | 4785.69974 | 10.2911, 10.2928 | 0.03952 |
| 50 | 58 | 3.3e-11 | -27035.65225132 | -27035.6522513163 | 0.00359 | 0.00141 | 0.032387 | 2.1e-05 | -0.64 | 4786.62436 | 10.2888, 10.2971 | 0.06439 |
| 51 | 69 | 3.1e-11 | -27035.6551726 | -27035.6551726047 | 0.004606 | 0.0015 | 0.034406 | 1.7e-05 | -0.6 | 4789.20888 | 10.2902, 10.3012 | 0.02951 |
| 52 | 47 | 3.4e-11 | -27035.65692007 | -27035.6569200744 | 0.00514 | 0.00141 | 0.032378 | 1.8e-05 | -0.5 | 4793.40325 | 10.2939, 10.3065 | 0.03839 |
| 53 | 45 | 3.5e-11 | -27035.65850655 | -27035.6585065479 | 0.004621 | 0.00129 | 0.0296 | 2.4e-05 | -0.61 | 4797.97377 | 10.2991, 10.3111 | 0.01941 |
| 54 | 59 | 3.8e-11 | -27035.65965304 | -27035.6596530435 | 0.002841 | 0.00108 | 0.024827 | 2e-05 | -0.84 | 4800.95017 | 10.3029, 10.3137 | 0.01309 |
| 55 | 60 | 9.7e-12 | -27035.66037489 | -27035.6603748866 | 0.002182 | 0.000861 | 0.019792 | 9e-06 | -1.08 | 4802.44567 | 10.3051, 10.3147 | 0.01196 |
| 56 | 52 | 1.2e-11 | -27035.66095179 | -27035.6609517913 | 0.002233 | 0.000782 | 0.017974 | 1.3e-05 | -1.21 | 4802.71202 | 10.3059, 10.3145 | 0.01215 |
| 57 | 37 | 2.1e-11 | -27035.6615184 | -27035.6615184005 | 0.002103 | 0.00078 | 0.017918 | 2e-05 | -1.23 | 4802.10096 | 10.3056, 10.3135 | 0.01483 |
| 58 | 38 | 9.4e-12 | -27035.66206959 | -27035.6620695897 | 0.001874 | 0.000759 | 0.017446 | 1.4e-05 | -1.11 | 4801.17063 | 10.3049, 10.3122 | 0.0201 |
| 59 | 34 | 1.1e-11 | -27035.66257107 | -27035.6625710735 | 0.001691 | 0.000743 | 0.017079 | 1.7e-05 | -0.92 | 4800.53496 | 10.3047, 10.3110 | 0.01955 |
| 60 | 50 | 7.5e-12 | -27035.66304292 | -27035.6630429175 | 0.001991 | 0.00075 | 0.017226 | 8e-06 | -0.73 | 4800.53548 | 10.3056, 10.3101 | 0.02673 |
| 61 | 50 | 1.9e-11 | -27035.66354762 | -27035.6635476234 | 0.00285 | 0.000757 | 0.017389 | 1.5e-05 | -0.61 | 4801.36541 | 10.3077, 10.3098 | 0.03124 |
| 62 | 41 | 2e-11 | -27035.66398119 | -27035.6639811867 | 0.002667 | 0.000665 | 0.015272 | 1.2e-05 | -0.62 | 4802.54514 | 10.3100, 10.3101 | 0.02565 |
| 63 | 49 | 2.5e-11 | -27035.66428146 | -27035.6642814613 | 0.00173 | 0.000534 | 0.012267 | 1.8e-05 | -0.73 | 4803.59101 | 10.3119, 10.3104 | 0.01966 |
| 64 | 38 | 1.3e-11 | -27035.66450196 | -27035.6645019638 | 0.001188 | 0.000482 | 0.011065 | 1.4e-05 | -0.83 | 4804.34087 | 10.3132, 10.3107 | 0.0139 |
| 65 | 48 | 4.4e-12 | -27035.66470419 | -27035.6647041897 | 0.001296 | 0.000497 | 0.011409 | 1e-05 | -0.89 | 4804.8085 | 10.3143, 10.3107 | 0.01429 |
| 66 | 47 | 9.4e-12 | -27035.66490884 | -27035.6649088446 | 0.00133 | 0.00051 | 0.011721 | 1.6e-05 | -0.86 | 4804.89453 | 10.3148, 10.3103 | 0.01038 |
| 67 | 55 | 7.8e-12 | -27035.66506595 | -27035.6650659477 | 0.001111 | 0.000455 | 0.010454 | 1.1e-05 | -0.76 | 4804.82998 | 10.3152, 10.3097 | 0.01027 |
| 68 | 36 | 9.2e-12 | -27035.66518762 | -27035.6651876198 | 0.000889 | 0.000368 | 0.008454 | 1.3e-05 | -0.63 | 4804.84066 | 10.3158, 10.3092 | 0.01013 |
| 69 | 46 | 7.5e-12 | -27035.66529062 | -27035.6652906249 | 0.000689 | 0.000316 | 0.007263 | 1.4e-05 | -0.52 | 4805.0735 | 10.3168, 10.3087 | 0.01107 |
| 70 | 42 | 9.1e-12 | -27035.66539153 | -27035.6653915258 | 0.0008819 | 0.000316 | 0.007261 | 9e-06 | -0.44 | 4805.5089 | 10.3179, 10.3085 | 0.009889 |
| 71 | 54 | 7.4e-12 | -27035.6654809 |  | 0.000863 | 0.000311 | 0.007153 | 1e-05 | -0.43 |  |  |  |
| 72 | 98 | 9.7e-12 | -27035.66492694 |  | 0.0008626 | 0.000311 | 0.007154 | 1.4e-05 | -0.43 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.002107, 0.0], HOMO_eV = 0.0475, LUMO_eV = 1.2713, E_Ry = -27035.66492694, E_all_electron_Ry = -673235.702643, acc_final_Ry = 9.7e-12, one_electron_Ry = -272838.07316665, hartree_Ry = 137216.08519503, xc_Ry = -3329.7216415, ewald_Ry = 128104.25305226, paw_one_center_Ry = -16188.20836607, converged_iterations = 98
- stress tensor (kbar): [[0.06, 0.0, 0.0], [0.0, 0.13, 0.0], [0.0, 0.0, -1.49]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 672, "n_occ": 664, "VBM_eV": 0.0475, "VBM_k_index": 0, "CBM_eV": 1.2713, "CBM_k_index": 0, "gap_eV": 1.2238, "direct_gap_min_eV": 1.2238, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.0136, "CB_width_bottom_band_eV": 1.0517, "E2_minus_E1_at_k0_eV": 0.7192}

**Final geometry** (vs `vcrelax_initial.in`): {"n_atoms": 176, "composition": {"H": 24, "In": 56, "O": 96}, "cell_lengths_A": [10.31792, 10.30849, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5089, "density_g_cm3": 2.7609, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 336, "min": 2.1616, "mean": 2.2197, "max": 2.3007, "std": 0.0357, "CN_In_hist": {"6": 56}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9722, "mean": 0.9773, "max": 0.9858, "std": 0.0061, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.557, "extent_A": 19.623, "thickness_H_H_A": 19.6233, "thickness_O_O_A": 18.2137, "thickness_In_In_A": 15.4861}, "displacement_vs_initial": {"max_A": 1.2979, "atom": "H153", "mean_A": 0.1345, "n_gt_0p1_A": 40, "by_element_max_A": {"H": 1.2979, "In": 0.0389, "O": 0.3437}, "outer_3A_mean_A": 0.3503, "interior_mean_A": 0.0112}, "reference_input": "vcrelax_initial.in"}

**Warnings/errors**: message_from_routine x1 (first: line 29 'Message from routine setup:'); warning x3 (first: line 96363 'Warning: ieee_invalid is signaling'); c_bands_not_converged x27 (first: line 792 'c_bands:  1 eigenvalues not converged'); ieee x3 (first: line 96363 'Warning: ieee_invalid is signaling'); discouraged x1 (first: line 30 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized'); fortran_stop x1 (first: line 96366 'FORTRAN STOP')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `bands.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 56, "O": 96}, "cell_lengths_A": [10.31792, 10.30849, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5089, "density_g_cm3": 2.7609, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 336, "min": 2.1616, "mean": 2.2197, "max": 2.3007, "std": 0.0357, "CN_In_hist": {"6": 56}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9722, "mean": 0.9773, "max": 0.9858, "std": 0.0061, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.557, "extent_A": 19.623, "thickness_H_H_A": 19.6233, "thickness_O_O_A": 18.2137, "thickness_In_In_A": 15.4861}}
- `scf.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 56, "O": 96}, "cell_lengths_A": [10.31792, 10.30849, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5089, "density_g_cm3": 2.7609, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 336, "min": 2.1616, "mean": 2.2197, "max": 2.3007, "std": 0.0357, "CN_In_hist": {"6": 56}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9722, "mean": 0.9773, "max": 0.9858, "std": 0.0061, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.557, "extent_A": 19.623, "thickness_H_H_A": 19.6233, "thickness_O_O_A": 18.2137, "thickness_In_In_A": 15.4861}}
- `vcrelax.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 56, "O": 96}, "cell_lengths_A": [10.32808, 10.32507, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4817.977, "density_g_cm3": 2.7538, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 336, "min": 2.1459, "mean": 2.2203, "max": 2.2844, "std": 0.0367, "CN_In_hist": {"6": 56}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9679, "mean": 0.9698, "max": 0.9708, "std": 0.0014, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.051, "extent_A": 20.13, "thickness_H_H_A": 20.1301, "thickness_O_O_A": 18.2896, "thickness_In_In_A": 15.5995}}
- `vcrelax_initial.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 56, "O": 96}, "cell_lengths_A": [10.30609, 10.30609, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4798.8829, "density_g_cm3": 2.7647, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 336, "min": 2.1671, "mean": 2.2192, "max": 2.2561, "std": 0.0328, "CN_In_hist": {"6": 56}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.97, "mean": 0.97, "max": 0.97, "std": 0.0, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.0, "extent_A": 20.181, "thickness_H_H_A": 20.1806, "thickness_O_O_A": 18.3393, "thickness_In_In_A": 15.4591}}

Geometry consistency (input of the follow-on step vs relax final coordinates): {"scf.in vs final of vcrelax.out": {"max_pos_diff_A": 0.0, "max_cell_diff_A": 0.0}, "bands.in vs final of vcrelax.out": {"max_pos_diff_A": 0.0, "max_cell_diff_A": 0.0}}

## Planar average `slab2_relax_c2_avg.dat`

{"n_points": 3000, "V_min_eV": -7.9484, "V_max_eV": 5.7662, "window_A": 0.01506, "z_mean_V_eV": 1.71003, "E_vac_eV": 5.76622, "vacuum_flatness_meV": 0.019, "vacuum_slope_meV_per_A": 0.0001, "IP_eV": 5.7189, "EA_eV": 4.495}
- `avg_slab2_relax_c2.in` input: `1 slab2_relax_c2_v.pp 1.0 3000 3 4.8689`
- `pp_slab2_relax_c2.in` input: `&INPUTPP prefix = 'slab', outdir = './tmp', filplot = 'slab2_relax_c2_v.pp', plot_num = 11 /`
- `avg_slab2_relax_c2.out`: done True; Program AVERAGE v.7.5 starts on  4Oct2026 at  3:37: 6 / Reading header from file  slab2_relax_c2_v.pp / Reading data from file  slab2_relax_c2_v.pp / AVERAGE      :      4.22s CPU      4.41s WALL / This run was terminated on:   3:37:11   4Oct2026
- `pp_slab2_relax_c2.out`: done True; Program POST-PROC v.7.5 starts on  4Oct2026 at  3:36:49 / Reading xml data from directory: / Calling punch_plot, plot_num =  11 / Writing data to file  slab2_relax_c2_v.pp / POST-PROC    :     13.74s CPU     14.71s WALL

## Other files

- `.fetched`: ''

## Checks against RESULTS_LOG

| quantity | re-derived | logged | reference | status |
|---|---|---|---|---|
| BFGS steps | 70 | 70 | RESULTS_LOG.md:556 | match |
| SCF cycles | 72 | 72 | RESULTS_LOG.md:556 | match |
| vc-relax wall (h) | 41.467 | 41.5 | RESULTS_LOG.md:556 | match |
| final enthalpy (Ry) | -27035.6654809032 | -27035.66548 | RESULTS_LOG.md:557 | match |
| total force at convergence (Ry/bohr) | 0.007154 | 0.0072 | RESULTS_LOG.md:558 | match |
| in-plane a (A) | 10.31792 | 10.318 | RESULTS_LOG.md:559 | match |
| in-plane b (A) (last-digit rounding allowed) | 10.30849 | 10.309 | RESULTS_LOG.md:559 | match |
| H-H thickness (A) | 19.6233 | 19.62 | RESULTS_LOG.md:560 | match |
| O-O thickness (A) | 18.2137 | 18.21 | RESULTS_LOG.md:560 | match |
| final SCF wall (h) | 0.932 | 0.9333333333333333 | RESULTS_LOG.md:562 | match |
| total job time (s) | 182892 | 182892 | RESULTS_LOG.md:546 | match |
| bands wall (h) | 8.367 | 8.366666666666667 | RESULTS_LOG.md:546 | match |
| gap (eV) | 1.2239 | 1.2239 | RESULTS_LOG.md:565 | match |
| EA (eV) | 4.495 | 4.495 | RESULTS_LOG.md:566 | match |
| IP (eV) | 5.7189 | 5.719 | RESULTS_LOG.md:566 | match |
