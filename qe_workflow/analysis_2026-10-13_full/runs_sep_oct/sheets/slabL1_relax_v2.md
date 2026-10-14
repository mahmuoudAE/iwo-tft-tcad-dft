# slabL1_relax_v2

**Purpose.** 0.51 nm slab (one cation plane): vc-relax, SCF, planar average, projwfc/PDOS, bands.

Folder `cern_htcondor/results/slabL1_relax_v2`; data `runs_sep_oct/out/slabL1_relax_v2.json` (+ `slabL1_relax_v2_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| avg_slabL1_relax_v2.in | 41 | 878bc0e483d7ea21 | loose | avg_in |
| avg_slabL1_relax_v2.out | 1386 | dd0ed9ed988683ec | loose | avg_out |
| bands.in | 5558 | bd82c5b9a1d3259b | loose | pw_in |
| bands.out | 60517 | fe984ba22bfdf768 | loose | pw_out |
| bands.tmpl | 4045 | ca3d680d9c07b2ca | loose | pw_tmpl |
| pp_slabL1_relax_v2.in | 96 | f8cf07daa8a8899b | loose | post_in |
| pp_slabL1_relax_v2.out | 2366 | 9117bdb34f1de187 | loose | pp_out |
| projwfc_slabL1_relax_v2.in | 160 | 182108f7e42a9227 | loose | post_in |
| projwfc_slabL1_relax_v2.out | 812982 | c188801a2db87bdd | loose | projwfc_out |
| scf.in | 4750 | 2a43d0c9887dc4a8 | loose | pw_in |
| scf.out | 101984 | 48f0e7cb8e817ae0 | loose | pw_out |
| scf.tmpl | 3237 | 5d41671c65097acc | loose | pw_tmpl |
| slabL1_relax_v2_avg.dat | 138000 | a8cbc1cff84a8846 | loose | avg_dat |
| slabL1_relax_v2_driver.log | 983 | d50be57266481472 | loose | driver |
| steps.sh | 812 | c17fe5142be5a6a5 | loose | steps |
| vcrelax.in | 3412 | 7f476ac5efd060ae | loose | pw_in |
| vcrelax.out | 2499278 | 8f0bd6add71ea014 | loose | pw_out |

Tarball `slabL1_relax_v2_results.tar.gz` (1491124 B, sha256 06a9c0228f660f15): 114 members; identical to the loose copy: 17; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 97

PDOS set `pdos`: 97 files.

## Resources and run history

- `slabL1_relax_v2_driver.log`: host b9pgpun005.cern.ch, 11 CPUs, wall limit 259200 s, GPU: 1 GPU(s), NVIDIA H100 NVL, 95830 MiB, job total 22374 s, start 2026-10-05T20:17:07Z
  - step vcrelax: -nk 1, max_seconds 257381, start 2026-10-05T20:17:26Z, end 2026-10-06T01:18:29Z, rc 0, PWSCF        :      4h58m CPU      5h 0m WALL
  - step scf: -nk 1, max_seconds 239318, start 2026-10-06T01:18:29Z, end 2026-10-06T01:46:29Z, rc 0, PWSCF        :  26m16.73s CPU  27m55.88s WALL
  - step bands: -nk 1, max_seconds 237607, start 2026-10-06T01:47:00Z, end 2026-10-06T02:30:01Z, rc 0, PWSCF        :  40m49.95s CPU  42m31.33s WALL
  - log: [2026-10-05T20:17:26Z] pools for the CPU steps: 1 (NCPU 11)
  - log: [2026-10-06T01:46:46Z] planar average slabL1_relax_v2: 3000 lines
  - log: [2026-10-06T01:47:00Z] pdos slabL1_relax_v2: 97 files
- HTCondor slabL1_relax_v2 12835386.0: 11 CPUs, 1 GPU; seen 2026-10-05T19:50:32Z to 2026-10-06T02:29:43Z (71 samples); states {'1': 5, '2': 66} (1 idle, 2 running, 3 removed, 5 held); max scf_it 3058, max BFGS 81; steps ['vcrelax', 'scf', 'bands']; hw ['1xNVIDIA H100 NVL|0%', '1xNVIDIA H100 NVL|1%', '1xNVIDIA H100 NVL|10%', '1xNVIDIA H100 NVL|13%', '1xNVIDIA H100 NVL|14%', '1xNVIDIA H100 NVL|2%', '1xNVIDIA H100 NVL|31%', '1xNVIDIA H100 NVL|35%', '1xNVIDIA H100 NVL|37%', '1xNVIDIA H100 NVL|38%', '1xNVIDIA H100 NVL|40%', '1xNVIDIA H100 NVL|43%', '1xNVIDIA H100 NVL|44%', '1xNVIDIA H100 NVL|45%', '1xNVIDIA H100 NVL|5%', '1xNVIDIA H100 NVL|54%', '1xNVIDIA H100 NVL|59%', '1xNVIDIA H100 NVL|64%', '1xNVIDIA H100 NVL|68%', '1xNVIDIA H100 NVL|7%', '1xNVIDIA H100 NVL|75%', '1xNVIDIA H100 NVL|8%', '1xNVIDIA H100 NVL|80%', '1xNVIDIA H100 NVL|85%', '1xNVIDIA H100 NVL|9%', '1xNVIDIA H100 NVL|94%', '1xNVIDIA H100 NVL|95%', '1xNVIDIA H100 NVL|96%'] ['Intel(R) Xeon(R) Platinum 8468']
- `steps.sh`: `steps() { # 2026-10-05: faster copy of STEPS_THIN_SLAB. Pools chosen at run time from the CPUs actually granted (CERN sizes # jobs by memory; -nk must divide the rank count, see iwo_slab2_final_cpu); 4 irreducible k-points NKP=1; for p in 4 2; do [ $((NCPU % p)) -eq 0 ] && { NKP=$p; break; }; done log "pools for the CPU steps: $NKP (NCPU $NCPU)" run_pw vcrelax $NKP python qeio.py converged vcrelax.out || { log "relaxation did not finish; later steps skipped"; return 0; } for t in scf bands; do python qeio.py newgeom $t.tmpl vcrelax.out > $t.in; done clean_tmp export FORCE_CPU=1 # one QE version (CPU 7.5) for SCF, pp.x, projwfc.x and bands run_pw scf $NKP || return 0 run_ppavg slab "$JOB" 4.8689 run_pdos slab "$JOB" "$(python qeio.py fermi scf.out)" $NKP run_pw bands $NKP }`

## Calculation `bands.out` (bands)

QE v.7.5 started 6Oct2026 3:47: 1; 11 MPI x 1 threads on 1 node(s); pools 1; R&G division 11; node memory 81890.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: JOB DONE; terminated 4:29:32   6Oct2026; PWSCF time {'cpu': '40m49.95s', 'wall': '42m31.33s', 'calls': None}; output lines 1059.

**Input settings** (every namelist variable):

- &CONTROL: calculation = bands, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 237607
- &SYSTEM: ibrav = 0, nat = 56, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 152
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.695454135, 0.0, 0.0], [0.0, 10.018786038, 0.0], [0.0, 0.0, 30.09211344]]}
- K_POINTS: {"mode": "tpiba", "n": 21, "points_first_last": [[0.0, 0.0, 0.0, 1.0], [0.1739764, 0.1739764, 0.0, 1.0]], "path_points": [[0.0, 0.0, 0.0, 1.0], [0.02460398, 0.0, 0.0, 1.0], [0.04920796, 0.0, 0.0, 1.0], [0.07381193, 0.0, 0.0, 1.0], [0.09841591, 0.0, 0.0, 1.0], [0.12301989, 0.0, 0.0, 1.0], [0.14762387, 0.0, 0.0, 1.0], [0.17222785, 0.0, 0.0, 1.0], [0.19683182, 0.0, 0.0, 1.0], [0.2214358, 0.0, 0.0, 1.
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 56, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 20.2115  a.u.; unit-cell volume = 21760.2371 (a.u.)^3; number of atoms/cell = 56; number of atomic types = 3; number of electrons = 272.00; number of Kohn-Sham states = 152; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [20.211479, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=    21 (sum of weights 2.0); FFT: Dense  grid:  4974197 G-vectors     FFT dimensions: ( 160, 144, 432) / Smooth grid:  1758717 G-vectors     FFT dimensions: ( 120, 108, 320)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '321.53 MB', 'Estimated max dynamical RAM per process': '1.73 GB', 'Estimated total dynamical RAM': '19.02 GB'}; start: ['Starting wfcs are  192 randomized atomic wfcs']
- Band-structure run: {'diag': 'Davidson diagonalization with overlap', 'kpts_done': 21, 'ethr': 'ethr =  3.68E-13,  avg # of iterations =120.0'}

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 21, "n_bands": 152, "n_occ": 136, "VBM_eV": -4.7232, "VBM_k_index": 0, "CBM_eV": -1.5819, "CBM_k_index": 0, "gap_eV": 3.1413, "direct_gap_min_eV": 3.1413, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.0338, "CB_width_bottom_band_eV": 0.1789, "E2_minus_E1_at_k0_eV": 1.8872}

**Warnings/errors**: message_from_routine x1 (first: line 33 'Message from routine setup:'); c_bands_not_converged x21 (first: line 441 'c_bands:  2 eigenvalues not converged'); ieee x2 (first: line 1058 'Note: The following floating-point exceptions are signalling: IEEE_UNDERFLOW_FLAG IEEE_DEN'); discouraged x1 (first: line 34 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Calculation `scf.out` (scf/relax)

QE v.7.5 started 6Oct2026 3:18:30; 11 MPI x 1 threads on 1 node(s); pools 1; R&G division 11; node memory 86992.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: JOB DONE; terminated 3:46:25   6Oct2026; PWSCF time {'cpu': '26m16.73s', 'wall': '27m55.88s', 'calls': None}; output lines 1961.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 239318
- &SYSTEM: ibrav = 0, nat = 56, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 152
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.695454135, 0.0, 0.0], [0.0, 10.018786038, 0.0], [0.0, 0.0, 30.09211344]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 56, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 20.2115  a.u.; unit-cell volume = 21760.2371 (a.u.)^3; number of atoms/cell = 56; number of atomic types = 3; number of electrons = 272.00; number of Kohn-Sham states = 152; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [20.211479, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  4974197 G-vectors     FFT dimensions: ( 160, 144, 432) / Smooth grid:  1758717 G-vectors     FFT dimensions: ( 120, 108, 320)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '520.87 MB', 'Estimated max dynamical RAM per process': '2.34 GB', 'Estimated total dynamical RAM': '25.79 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     271.9700, renormalised to     272.0000', 'Starting wfcs are  192 randomized atomic wfcs']

**Convergence** (1 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 46 | 7.5e-10 | -4315.41561777 |  | 0.0005317 | 0.000211 | 0.002729 | 3.4e-05 | -0.03 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.001244, 0.0], HOMO_eV = -4.7219, LUMO_eV = -1.5818, E_Ry = -4315.41561777, E_all_electron_Ry = -97749.274645, acc_final_Ry = 7.5e-10, one_electron_Ry = -18036.07384004, hartree_Ry = 9123.85649876, xc_Ry = -567.0911679, ewald_Ry = 7575.07578084, paw_one_center_Ry = -2411.18288943, converged_iterations = 46
- stress tensor (kbar): [[0.25, 0.0, 0.0], [0.0, 0.07, 0.0], [0.0, 0.0, -0.42]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 152, "n_occ": 136, "VBM_eV": -4.7219, "VBM_k_index": 2, "CBM_eV": -1.5818, "CBM_k_index": 0, "gap_eV": 3.1401, "direct_gap_min_eV": 3.1412, "direct_gap_k_index": 0, "gap_type": "indirect", "VB_width_top_band_eV": 0.0179, "CB_width_bottom_band_eV": 0.6157, "E2_minus_E1_at_k0_eV": 1.8873}

**Warnings/errors**: message_from_routine x1 (first: line 29 'Message from routine setup:'); c_bands_not_converged x22 (first: line 475 'c_bands:  1 eigenvalues not converged'); discouraged x1 (first: line 30 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Calculation `vcrelax.out` (scf/relax)

QE v.7.3.1 started 5Oct2026 22:17:28; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 83919.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled; GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled. Completed: JOB DONE; terminated 3:18:23   6Oct2026; PWSCF time {'cpu': '4h58m', 'wall': '5h 0m', 'calls': None}; output lines 56460.

**Input settings** (every namelist variable):

- &CONTROL: calculation = vc-relax, prefix = vcr, outdir = ./tmp, pseudo_dir = ./, verbosity = low, tprnfor = .true., tstress = .true., max_seconds = 257381, nstep = 300, etot_conv_thr = 1.0d-4, forc_conv_thr = 1.0d-3
- &SYSTEM: ibrav = 0, nat = 56, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 144
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- &IONS: ion_dynamics = bfgs
- &CELL: cell_dynamics = bfgs, cell_dofree = 2Dxy, press_conv_thr = 0.5
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.3060902, 0.0, 0.0], [0.0, 10.3060902, 0.0], [0.0, 0.0, 30.09211344]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 56, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4757  a.u.; unit-cell volume = 21569.3556 (a.u.)^3; number of atoms/cell = 56; number of atomic types = 3; number of electrons = 272.00; number of Kohn-Sham states = 144; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; energy convergence thresh. = 1.0E-04; force convergence thresh. = 1.0E-03; press convergence thresh. = 5.0E-01; Exchange-correlation = SLA  PW   PBX  PBC; nstep = 300; celldm = [19.475688, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0) (re-read 3 times in the final SCF)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  4974197 G-vectors     FFT dimensions: ( 160, 144, 432) / Smooth grid:  1758717 G-vectors     FFT dimensions: ( 120, 108, 320)
- RAM (pw.x estimate): {'Estimated max dynamical RAM per process': '25.71 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     271.9700, renormalised to     272.0000', 'Starting wfcs are  192 randomized atomic wfcs', 'Initial potential from superposition of free atoms', 'starting charge     271.9700, renormalised to     272.0000', 'Starting wfcs are  192 randomized atomic wfcs']

**Convergence** (84 SCF + BFGS): bfgs converged in  83 scf cycles and  82 bfgs steps (criteria: energy <  1.0E-04 Ry, force <  1.0E-03 Ry/Bohr, cell <  5.0E-01 kbar) final energy None final enthalpy -4315.414870707 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 55 | 7.3e-10 | -4314.75707914 | -4314.7570791402 | 0.04849 | 0.0171 | 0.221853 | 2.9e-05 | -4.38 | 3199.09079 | 10.3101, 10.3113 | 0.05121 |
| 1 | 29 | 8.5e-10 | -4314.7974635 | -4314.797463497 | 0.03403 | 0.0154 | 0.20017 | 1.8e-05 | -4.86 | 3204.04755 | 10.3174, 10.3199 | 0.05634 |
| 2 | 29 | 2.3e-10 | -4314.84556753 | -4314.8455675318 | 0.03491 | 0.0142 | 0.184353 | 2.7e-05 | -3.46 | 3215.15072 | 10.3347, 10.3383 | 0.08452 |
| 3 | 35 | 1.8e-10 | -4314.90802657 | -4314.9080265722 | 0.03161 | 0.013 | 0.168658 | 2.9e-05 | -0.98 | 3236.0157 | 10.3685, 10.3715 | 0.1268 |
| 4 | 39 | 7.2e-11 | -4314.96835638 | -4314.9683563761 | 0.03451 | 0.0137 | 0.178026 | 7e-06 | 2.26 | 3267.4866 | 10.4203, 10.4203 | 0.1516 |
| 5 | 31 | 1.9e-10 | -4315.0159828 | -4315.0159828012 | 0.03687 | 0.0132 | 0.170477 | 2.7e-05 | 4.99 | 3299.27218 | 10.4726, 10.4691 | 0.1492 |
| 6 | 32 | 2.5e-10 | -4315.0507108 | -4315.0507107985 | 0.0236 | 0.00916 | 0.118772 | 6e-05 | 5.92 | 3331.88637 | 10.5252, 10.5198 | 0.1498 |
| 7 | 45 | 2e-10 | -4315.07557138 | -4315.0755713806 | 0.01796 | 0.00825 | 0.106911 | 3.2e-05 | 4.63 | 3358.68502 | 10.5669, 10.5626 | 0.122 |
| 8 | 38 | 1.4e-10 | -4315.09479935 | -4315.0947993487 | 0.02413 | 0.00895 | 0.116031 | 3.5e-05 | 2.59 | 3384.83975 | 10.6063, 10.6053 | 0.1217 |
| 9 | 37 | 1.8e-10 | -4315.11106375 | -4315.1110637525 | 0.02469 | 0.00838 | 0.108596 | 1.7e-05 | -1.32 | 3385.70259 | 10.6060, 10.6083 | 0.05315 |
| 10 | 41 | 1.6e-10 | -4315.12368883 | -4315.1236888309 | 0.01213 | 0.00568 | 0.073582 | 2.2e-05 | -2.99 | 3386.06024 | 10.6059, 10.6095 | 0.05741 |
| 11 | 35 | 1.1e-10 | -4315.13346357 | -4315.1334635744 | 0.01417 | 0.0062 | 0.08042 | 2.3e-05 | -4.59 | 3373.05269 | 10.5860, 10.5886 | 0.06805 |
| 12 | 36 | 6.7e-11 | -4315.14444992 | -4315.1444499153 | 0.01813 | 0.00611 | 0.07914 | 6e-06 | -4.7 | 3360.00203 | 10.5681, 10.5655 | 0.101 |
| 13 | 50 | 1.1e-10 | -4315.15757919 | -4315.1575791879 | 0.02911 | 0.00789 | 0.102248 | 2.5e-05 | -5.05 | 3329.0612 | 10.5260, 10.5100 | 0.158 |
| 14 | 48 | 2.6e-10 | -4315.1777488 | -4315.1777487959 | 0.03746 | 0.00998 | 0.129376 | 3.1e-05 | -4.21 | 3281.46106 | 10.4606, 10.4245 | 0.2438 |
| 15 | 43 | 8.3e-11 | -4315.20348239 | -4315.2034823894 | 0.03188 | 0.0098 | 0.127068 | 2.7e-05 | -2.03 | 3242.75375 | 10.4100, 10.3517 | 0.2375 |
| 16 | 55 | 4.3e-11 | -4315.22168621 | -4315.2216862057 | 0.03569 | 0.0152 | 0.19641 | 1e-05 | -2.8 | 3202.96215 | 10.3504, 10.2835 | 0.1948 |
| 17 | 54 | 3e-11 | -4315.22783577 | -4315.2278357739 | 0.03119 | 0.0146 | 0.189855 | 7e-06 | 3.69 | 3223.41492 | 10.3786, 10.3211 | 0.1074 |
| 18 | 32 | 1.9e-10 | -4315.24444122 | -4315.2444412245 | 0.0133 | 0.00566 | 0.073348 | 2.2e-05 | -0.51 | 3223.05816 | 10.3748, 10.3237 | 0.02881 |
| 19 | 46 | 7.3e-11 | -4315.2496351 | -4315.2496350955 | 0.01216 | 0.00463 | 0.05998 | 1e-05 | -1.16 | 3219.42858 | 10.3663, 10.3206 | 0.03169 |
| 20 | 31 | 5.7e-11 | -4315.25380985 | -4315.2538098472 | 0.01188 | 0.00463 | 0.060074 | 7e-06 | -1.27 | 3212.54491 | 10.3507, 10.3140 | 0.04752 |
| 21 | 28 | 5.3e-11 | -4315.2597778 | -4315.2597778017 | 0.009969 | 0.00446 | 0.057781 | 1.1e-05 | -1.05 | 3201.48351 | 10.3265, 10.3026 | 0.07124 |
| 22 | 33 | 9e-11 | -4315.26656159 | -4315.2665615947 | 0.01051 | 0.00458 | 0.059392 | 1e-05 | -0.56 | 3185.85035 | 10.2899, 10.2887 | 0.1068 |
| 23 | 42 | 1e-10 | -4315.27352186 | -4315.2735218552 | 0.009892 | 0.00499 | 0.064683 | 2e-05 | 0.48 | 3178.04776 | 10.2720, 10.2814 | 0.05837 |
| 24 | 26 | 4.3e-11 | -4315.27749523 | -4315.2774952348 | 0.01053 | 0.00487 | 0.06313 | 1e-05 | 1.05 | 3169.19901 | 10.2501, 10.2746 | 0.08751 |
| 25 | 32 | 5.3e-11 | -4315.28498638 | -4315.2849863803 | 0.009589 | 0.0046 | 0.059619 | 1.8e-05 | 1.66 | 3161.06801 | 10.2262, 10.2723 | 0.1312 |
| 26 | 48 | 5.8e-11 | -4315.29589522 | -4315.2958952247 | 0.009065 | 0.00472 | 0.061134 | 2.7e-05 | 1.76 | 3174.30692 | 10.2336, 10.3078 | 0.1742 |
| 27 | 37 | 7.9e-11 | -4315.30521648 | -4315.3052164767 | 0.02242 | 0.0108 | 0.140142 | 2.8e-05 | 1.96 | 3174.65248 | 10.2287, 10.3139 | 0.1422 |
| 28 | 60 | 9e-11 | -4315.30768179 | -4315.307681788 | 0.0197 | 0.00964 | 0.124949 | 1.3e-05 | -0.57 | 3197.64317 | 10.2760, 10.3408 | 0.1353 |
| 29 | 40 | 1.2e-10 | -4315.31670193 | -4315.3167019307 | 0.02201 | 0.00994 | 0.128853 | 1.7e-05 | 0.22 | 3204.5517 | 10.2845, 10.3545 | 0.04579 |
| 30 | 44 | 6.5e-11 | -4315.32387981 | -4315.3238798147 | 0.0121 | 0.00533 | 0.06906 | 1e-05 | 0.46 | 3223.70561 | 10.3136, 10.3871 | 0.09242 |
| 31 | 40 | 1e-10 | -4315.33109608 | -4315.3310960793 | 0.01291 | 0.00576 | 0.074649 | 1.6e-05 | -0.1 | 3239.92915 | 10.3418, 10.4109 | 0.08063 |
| 32 | 36 | 3e-11 | -4315.33641706 | -4315.3364170649 | 0.01529 | 0.006 | 0.077802 | 1.5e-05 | -0.4 | 3250.3843 | 10.3604, 10.4257 | 0.05337 |
| 33 | 39 | 1e-10 | -4315.34097599 | -4315.3409759869 | 0.01072 | 0.00518 | 0.067167 | 3e-05 | -0.3 | 3259.06391 | 10.3722, 10.4417 | 0.0762 |
| 34 | 32 | 7e-11 | -4315.34638345 | -4315.3463834479 | 0.01194 | 0.00558 | 0.072372 | 2e-05 | -0.09 | 3265.42839 | 10.3785, 10.4557 | 0.08391 |
| 35 | 31 | 1.1e-10 | -4315.35194611 | -4315.3519461142 | 0.01072 | 0.00526 | 0.068202 | 3.4e-05 | 0.26 | 3276.19626 | 10.3891, 10.4794 | 0.126 |
| 36 | 39 | 2.7e-11 | -4315.35885021 | -4315.3588502078 | 0.01177 | 0.00458 | 0.059427 | 1.2e-05 | 0.57 | 3295.5894 | 10.4119, 10.5184 | 0.1701 |
| 37 | 45 | 7.2e-11 | -4315.3658006 | -4315.3658005972 | 0.008595 | 0.0033 | 0.042792 | 1.8e-05 | 1.0 | 3317.57771 | 10.4426, 10.5575 | 0.1249 |
| 38 | 43 | 6.6e-11 | -4315.36842226 | -4315.3684222593 | 0.0126 | 0.0042 | 0.054501 | 1.3e-05 | 0.25 | 3345.43452 | 10.4877, 10.6004 | 0.1291 |
| 39 | 34 | 6.6e-11 | -4315.37096548 | -4315.3709654835 | 0.01402 | 0.00664 | 0.086127 | 1e-05 | 0.44 | 3347.7885 | 10.4944, 10.6010 | 0.01938 |
| 40 | 34 | 4.2e-11 | -4315.3733452 | -4315.3733451964 | 0.00743 | 0.00314 | 0.040719 | 1.6e-05 | -0.13 | 3345.46967 | 10.4984, 10.5897 | 0.03208 |
| 41 | 35 | 4.3e-11 | -4315.37558101 | -4315.3755810097 | 0.00544 | 0.00229 | 0.029643 | 1.4e-05 | -0.5 | 3347.05588 | 10.5106, 10.5824 | 0.03547 |
| 42 | 51 | 6.6e-12 | -4315.37775767 | -4315.3777576682 | 0.008105 | 0.00316 | 0.041011 | 6e-06 | -0.86 | 3347.34573 | 10.5242, 10.5696 | 0.05318 |
| 43 | 30 | 4.8e-11 | -4315.38045556 | -4315.3804555553 | 0.01193 | 0.00364 | 0.047165 | 1.1e-05 | -1.07 | 3347.46882 | 10.5426, 10.5515 | 0.07976 |
| 44 | 28 | 1.1e-10 | -4315.38385679 | -4315.3838567856 | 0.01328 | 0.00335 | 0.043406 | 2.3e-05 | -1.17 | 3346.42496 | 10.5632, 10.5277 | 0.09687 |
| 45 | 28 | 5.2e-11 | -4315.38733496 | -4315.3873349639 | 0.009583 | 0.00249 | 0.032269 | 1.3e-05 | -1.04 | 3346.21115 | 10.5775, 10.5128 | 0.07327 |
| 46 | 35 | 8e-12 | -4315.38954853 | -4315.3895485302 | 0.004405 | 0.00225 | 0.029184 | 5e-06 | -0.8 | 3348.95929 | 10.5924, 10.5066 | 0.07346 |
| 47 | 38 | 1.7e-11 | -4315.39110958 | -4315.3911095761 | 0.00468 | 0.00239 | 0.031037 | 1.4e-05 | -0.67 | 3352.55982 | 10.6071, 10.5033 | 0.06944 |
| 48 | 38 | 2.7e-11 | -4315.39234697 | -4315.3923469704 | 0.007748 | 0.00251 | 0.032514 | 8e-06 | -0.68 | 3353.64462 | 10.6221, 10.4919 | 0.07683 |
| 49 | 27 | 4.7e-11 | -4315.39384147 | -4315.39384147 | 0.008487 | 0.00265 | 0.034366 | 9e-06 | -0.64 | 3350.03591 | 10.6345, 10.4684 | 0.07403 |
| 50 | 25 | 9.3e-12 | -4315.39545781 | -4315.3954578137 | 0.005314 | 0.00264 | 0.034273 | 7e-06 | -0.46 | 3343.27936 | 10.6419, 10.4400 | 0.08158 |
| 51 | 24 | 3.5e-11 | -4315.39669325 | -4315.3966932476 | 0.005474 | 0.00229 | 0.029707 | 1.2e-05 | -0.16 | 3337.82846 | 10.6472, 10.4178 | 0.06392 |
| 52 | 51 | 3.4e-11 | -4315.39751369 | -4315.3975136876 | 0.004973 | 0.00192 | 0.024938 | 9e-06 | 0.08 | 3332.31748 | 10.6566, 10.3914 | 0.076 |
| 53 | 34 | 3.3e-11 | -4315.39849884 | -4315.3984988389 | 0.005032 | 0.00195 | 0.02529 | 1.2e-05 | 0.28 | 3328.52921 | 10.6743, 10.3624 | 0.08374 |
| 54 | 35 | 4.9e-11 | -4315.39970743 | -4315.399707426 | 0.006093 | 0.00222 | 0.028732 | 1e-05 | 0.32 | 3324.19577 | 10.7054, 10.3189 | 0.1259 |
| 55 | 35 | 3.8e-11 | -4315.40139965 | -4315.4013996472 | 0.005721 | 0.00252 | 0.032652 | 1.4e-05 | 0.29 | 3322.32672 | 10.7557, 10.2648 | 0.157 |
| 56 | 30 | 5.1e-11 | -4315.40316107 | -4315.4031610672 | 0.006398 | 0.00251 | 0.03258 | 1.6e-05 | 0.01 | 3318.93858 | 10.7882, 10.2234 | 0.1207 |
| 57 | 41 | 2.6e-11 | -4315.4043985 | -4315.4043985003 | 0.005369 | 0.00216 | 0.027956 | 7e-06 | -0.06 | 3321.45066 | 10.8428, 10.1797 | 0.1513 |
| 58 | 36 | 3.8e-11 | -4315.40572645 | -4315.4057264541 | 0.005504 | 0.00246 | 0.031935 | 1.7e-05 | -0.62 | 3312.62616 | 10.8513, 10.1447 | 0.1031 |
| 59 | 35 | 2.5e-11 | -4315.40673322 | -4315.4067332242 | 0.00393 | 0.00203 | 0.026357 | 1e-05 | -0.4 | 3310.20889 | 10.8543, 10.1345 | 0.02994 |
| 60 | 38 | 1.1e-11 | -4315.40765338 | -4315.4076533759 | 0.003329 | 0.0017 | 0.022089 | 7e-06 | -0.53 | 3305.16679 | 10.8497, 10.1233 | 0.03296 |
| 61 | 36 | 3.1e-11 | -4315.40834328 | -4315.4083432787 | 0.002654 | 0.00133 | 0.017183 | 2.5e-05 | -0.53 | 3299.16319 | 10.8479, 10.1066 | 0.04945 |
| 62 | 24 | 1.2e-11 | -4315.40884668 | -4315.4088466766 | 0.002485 | 0.00107 | 0.013919 | 8e-06 | -0.53 | 3290.9375 | 10.8479, 10.0814 | 0.07423 |
| 63 | 41 | 2.4e-11 | -4315.40934513 | -4315.4093451258 | 0.002276 | 0.00096 | 0.012438 | 9e-06 | -0.52 | 3278.95239 | 10.8490, 10.0437 | 0.1115 |
| 64 | 26 | 2e-11 | -4315.40989583 | -4315.4098958256 | 0.003026 | 0.00108 | 0.014006 | 8e-06 | -0.52 | 3265.63803 | 10.8504, 10.0016 | 0.1247 |
| 65 | 24 | 2.9e-11 | -4315.41044833 | -4315.4104483338 | 0.003607 | 0.00125 | 0.016234 | 6e-06 | -0.51 | 3251.51294 | 10.8503, 9.9584 | 0.1282 |
| 66 | 27 | 1.9e-11 | -4315.41109014 | -4315.4110901368 | 0.003198 | 0.00126 | 0.016384 | 3e-06 | -0.46 | 3241.97916 | 10.8472, 9.9321 | 0.07827 |
| 67 | 29 | 2.3e-11 | -4315.41162615 | -4315.4116261456 | 0.002208 | 0.00106 | 0.0137 | 1.4e-05 | -0.38 | 3240.23056 | 10.8417, 9.9318 | 0.015 |
| 68 | 32 | 1.5e-11 | -4315.41190012 | -4315.4119001224 | 0.001643 | 0.000848 | 0.010997 | 6e-06 | -0.3 | 3241.58894 | 10.8357, 9.9414 | 0.02859 |
| 69 | 29 | 1.6e-11 | -4315.4120448 | -4315.4120447992 | 0.001455 | 0.000737 | 0.009557 | 1e-05 | -0.24 | 3242.75402 | 10.8294, 9.9508 | 0.02807 |
| 70 | 49 | 9.6e-12 | -4315.41215905 | -4315.4121590481 | 0.001375 | 0.000714 | 0.009257 | 1e-05 | -0.2 | 3242.69163 | 10.8209, 9.9584 | 0.02322 |
| 71 | 32 | 8.7e-12 | -4315.41230025 | -4315.4123002489 | 0.001795 | 0.000764 | 0.009899 | 6e-06 | -0.15 | 3240.95662 | 10.8115, 9.9617 | 0.02557 |
| 72 | 33 | 6.7e-12 | -4315.41248567 | -4315.4124856729 | 0.002053 | 0.000867 | 0.011244 | 5e-06 | -0.1 | 3236.82415 | 10.7975, 9.9619 | 0.03837 |
| 73 | 29 | 1.7e-11 | -4315.41277464 | -4315.412774638 | 0.002 | 0.000978 | 0.012679 | 1.1e-05 | -0.01 | 3231.15278 | 10.7799, 9.9607 | 0.04798 |
| 74 | 35 | 1.6e-11 | -4315.41313549 | -4315.4131354948 | 0.002759 | 0.00101 | 0.01305 | 1e-05 | 0.08 | 3227.36201 | 10.7649, 9.9629 | 0.04122 |
| 75 | 33 | 1.6e-11 | -4315.41346607 | -4315.4134660722 | 0.002719 | 0.000949 | 0.012306 | 6e-06 | 0.15 | 3226.40395 | 10.7544, 9.9697 | 0.03574 |
| 76 | 31 | 2.4e-11 | -4315.4137577 | -4315.4137576989 | 0.002296 | 0.00091 | 0.011794 | 1.6e-05 | 0.16 | 3227.84911 | 10.7469, 9.9811 | 0.03375 |
| 77 | 38 | 3.6e-12 | -4315.41396926 | -4315.4139692576 | 0.003325 | 0.00111 | 0.014341 | 6e-06 | 0.16 | 3229.68031 | 10.7386, 9.9945 | 0.03961 |
| 78 | 43 | 1.2e-11 | -4315.41421646 | -4315.4142164646 | 0.002815 | 0.000944 | 0.012232 | 5e-06 | 0.06 | 3231.42556 | 10.7208, 10.0165 | 0.06496 |
| 79 | 42 | 1.1e-11 | -4315.41449654 | -4315.4144965353 | 0.004171 | 0.00129 | 0.016721 | 8e-06 | 0.07 | 3229.31437 | 10.7061, 10.0237 | 0.04048 |
| 80 | 41 | 1.3e-11 | -4315.41472529 | -4315.4147252936 | 0.001585 | 0.00049 | 0.006355 | 4e-06 | -0.07 | 3226.49264 | 10.6967, 10.0237 | 0.02585 |
| 81 | 26 | 1.3e-11 | -4315.41484081 | -4315.4148408066 | 0.0007369 | 0.000374 | 0.004845 | 8e-06 | -0.04 | 3224.53446 | 10.6955, 10.0188 | 0.01441 |
| 82 | 22 | 7.7e-12 | -4315.41487071 |  | 0.0005363 | 0.000213 | 0.002755 | 4e-06 | -0.04 |  |  |  |
| 83 | 54 | 7.7e-12 | -4315.41561801 |  | 0.0005286 | 0.00021 | 0.002723 | 4e-06 | -0.02 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.001244, 0.0], HOMO_eV = -4.7221, LUMO_eV = -1.5819, E_Ry = -4315.41561801, E_all_electron_Ry = -97749.274645, acc_final_Ry = 7.7e-12, one_electron_Ry = -18036.07423749, hartree_Ry = 9123.85699829, xc_Ry = -567.09125478, ewald_Ry = 7575.07577942, paw_one_center_Ry = -2411.18290346, converged_iterations = 54
- stress tensor (kbar): [[0.26, 0.0, 0.0], [0.0, 0.08, 0.0], [0.0, 0.0, -0.41]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 144, "n_occ": 136, "VBM_eV": -4.7221, "VBM_k_index": 2, "CBM_eV": -1.5819, "CBM_k_index": 0, "gap_eV": 3.1402, "direct_gap_min_eV": 3.1413, "direct_gap_k_index": 0, "gap_type": "indirect", "VB_width_top_band_eV": 0.0178, "CB_width_bottom_band_eV": 0.6157, "E2_minus_E1_at_k0_eV": 1.8873}

**Final geometry** (vs `vcrelax.in`): {"n_atoms": 56, "composition": {"H": 24, "In": 8, "O": 24}, "cell_lengths_A": [10.69545, 10.01879, 30.09211], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3224.5345, "density_g_cm3": 0.6832, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 48, "min": 2.1755, "mean": 2.2102, "max": 2.2388, "std": 0.027, "CN_In_hist": {"6": 8}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9728, "mean": 0.9773, "max": 0.9798, "std": 0.0032, "CN_O_hist": {"1": 24}}}, "CN_O_by_cations_hist": {"2": 24}, "slab": {"vacuum_A": 25.48, "extent_A": 4.612, "thickness_H_H_A": 4.6118, "thickness_O_O_A": 3.046, "thickness_In_In_A": 0.8429}, "displacement_vs_initial": {"max_A": 1.5627, "atom": "H49", "mean_A": 0.5472, "n_gt_0p1_A": 52, "by_element_max_A": {"H": 1.5627, "In": 0.1257, "O": 0.3833}, "outer_3A_mean_A": 0.5472, "interior_mean_A": null}, "reference_input": "vcrelax.in"}

**Warnings/errors**: message_from_routine x1 (first: line 29 'Message from routine setup:'); warning x3 (first: line 56457 'Warning: ieee_invalid is signaling'); c_bands_not_converged x76 (first: line 342 'c_bands:  2 eigenvalues not converged'); ieee x3 (first: line 56457 'Warning: ieee_invalid is signaling'); discouraged x1 (first: line 30 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized'); fortran_stop x1 (first: line 56460 'FORTRAN STOP')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `bands.in`: {"n_atoms": 56, "composition": {"H": 24, "In": 8, "O": 24}, "cell_lengths_A": [10.69545, 10.01879, 30.09211], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3224.5345, "density_g_cm3": 0.6832, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 48, "min": 2.1755, "mean": 2.2102, "max": 2.2388, "std": 0.027, "CN_In_hist": {"6": 8}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9728, "mean": 0.9773, "max": 0.9798, "std": 0.0032, "CN_O_hist": {"1": 24}}}, "CN_O_by_cations_hist": {"2": 24}, "slab": {"vacuum_A": 25.48, "extent_A": 4.612, "thickness_H_H_A": 4.6118, "thickness_O_O_A": 3.046, "thickness_In_In_A": 0.8429}}
- `scf.in`: {"n_atoms": 56, "composition": {"H": 24, "In": 8, "O": 24}, "cell_lengths_A": [10.69545, 10.01879, 30.09211], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3224.5345, "density_g_cm3": 0.6832, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 48, "min": 2.1755, "mean": 2.2102, "max": 2.2388, "std": 0.027, "CN_In_hist": {"6": 8}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9728, "mean": 0.9773, "max": 0.9798, "std": 0.0032, "CN_O_hist": {"1": 24}}}, "CN_O_by_cations_hist": {"2": 24}, "slab": {"vacuum_A": 25.48, "extent_A": 4.612, "thickness_H_H_A": 4.6118, "thickness_O_O_A": 3.046, "thickness_In_In_A": 0.8429}}
- `vcrelax.in`: {"n_atoms": 56, "composition": {"H": 24, "In": 8, "O": 24}, "cell_lengths_A": [10.30609, 10.30609, 30.09211], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3196.2487, "density_g_cm3": 0.6893, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 48, "min": 2.1671, "mean": 2.221, "max": 2.2561, "std": 0.0387, "CN_In_hist": {"6": 8}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.97, "mean": 0.97, "max": 0.97, "std": 0.0, "CN_O_hist": {"1": 24}}}, "CN_O_by_cations_hist": {"2": 24}, "slab": {"vacuum_A": 25.0, "extent_A": 5.092, "thickness_H_H_A": 5.0921, "thickness_O_O_A": 3.184, "thickness_In_In_A": 0.6968}}

Geometry consistency (input of the follow-on step vs relax final coordinates): {"scf.in vs final of vcrelax.out": {"max_pos_diff_A": 0.0, "max_cell_diff_A": 0.0}, "bands.in vs final of vcrelax.out": {"max_pos_diff_A": 0.0, "max_cell_diff_A": 0.0}}

## projwfc `projwfc_slabL1_relax_v2.out`

natomwfc 192, nbnd 152, nkstot 4, states 192, spilling 0.006, Loewdin total 270.374, PROJWFC      :      9.59s CPU     13.26s WALL, done True

| element | n | total charge mean (min-max) | s | p | d |
|---|---|---|---|---|---|
| In | 8 | 11.7921 (11.7851-11.7992) | 0.7065 | 1.0929 | 9.9927 |
| O | 24 | 6.7304 (6.7264-6.7367) | 1.6911 | 5.0393 | 0.0 |
| H | 24 | 0.6045 (0.6024-0.6077) | 0.6045 | 0.0 | 0.0 |

## PDOS `pdos`

{"n_files": 97, "E_window_eV": [-12.722, -0.712], "dE_eV": 0.01, "integral_dos_window": 146.01, "integral_dos_below_EF_or_VBM": 142.16, "reference_energy_eV": -4.7219}

| element, l | files | states in window | states below reference |
|---|---|---|---|
| H s | 24 | 7.632 | 7.241 |
| In d | 8 | 1.47 | 1.43 |
| In p | 8 | 6.19 | 6.078 |
| In s | 8 | 5.648 | 4.932 |
| O p | 24 | 118.624 | 116.521 |
| O s | 24 | 5.022 | 4.658 |

## Planar average `slabL1_relax_v2_avg.dat`

{"n_points": 3000, "V_min_eV": -10.3019, "V_max_eV": 1.6099, "window_A": 0.01003, "z_mean_V_eV": 0.42568, "E_vac_eV": 1.60991, "vacuum_flatness_meV": 0.01, "vacuum_slope_meV_per_A": 0.0, "IP_eV": 6.3318, "EA_eV": 3.1917}
- `avg_slabL1_relax_v2.in` input: `1 slabL1_relax_v2_v.pp 1.0 3000 3 4.8689`
- `pp_slabL1_relax_v2.in` input: `&INPUTPP prefix = 'slab', outdir = './tmp', filplot = 'slabL1_relax_v2_v.pp', plot_num = 11 /`
- `projwfc_slabL1_relax_v2.in` input: `&PROJWFC prefix = 'slab', outdir = './tmp', filpdos = 'pdos/slabL1_relax_v2' Emin = -12.7219, Emax = -0.7219, DeltaE = 0.01, degauss = 0.0073, ngauss = 0 /`
- `avg_slabL1_relax_v2.out`: done True; Program AVERAGE v.7.5 starts on  6Oct2026 at  3:46:43 / Reading header from file  slabL1_relax_v2_v.pp / Reading data from file  slabL1_relax_v2_v.pp / AVERAGE      :      3.17s CPU      3.24s WALL / This run was terminated on:   3:46:46   6Oct2026
- `pp_slabL1_relax_v2.out`: done True; Program POST-PROC v.7.5 starts on  6Oct2026 at  3:46:30 / Reading xml data from directory: / Calling punch_plot, plot_num =  11 / Writing data to file  slabL1_relax_v2_v.pp / POST-PROC    :      9.32s CPU     10.08s WALL

## Other files

- `.fetched`: ''
