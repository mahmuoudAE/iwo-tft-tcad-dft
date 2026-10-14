# slabL2_relax_v2

**Purpose.** 0.75 nm slab (two cation planes): vc-relax, SCF, planar average, projwfc/PDOS, bands.

Folder `cern_htcondor/results/slabL2_relax_v2`; data `runs_sep_oct/out/slabL2_relax_v2.json` (+ `slabL2_relax_v2_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| avg_slabL2_relax_v2.in | 41 | acdf47f732679534 | loose | avg_in |
| avg_slabL2_relax_v2.out | 1386 | 7fd617813fc17a8e | loose | avg_out |
| bands.in | 6998 | 2ff0562d987ad2d4 | loose | pw_in |
| bands.out | 79018 | 2b6355085009ace6 | loose | pw_out |
| bands.tmpl | 4945 | bf59d4df63b6b615 | loose | pw_tmpl |
| pp_slabL2_relax_v2.in | 96 | 877d51d1103a2fb4 | loose | post_in |
| pp_slabL2_relax_v2.out | 2366 | bd275ed53fd661c3 | loose | pp_out |
| projwfc_slabL2_relax_v2.in | 159 | 4775ae79af708a46 | loose | post_in |
| projwfc_slabL2_relax_v2.out | 1635671 | 01e08a0623d16464 | loose | projwfc_out |
| scf.in | 6190 | d36b3b2d1f7eb0b1 | loose | pw_in |
| scf.out | 131962 | 0bd3171ab9705703 | loose | pw_out |
| scf.tmpl | 4137 | 3e8e99dfcee12566 | loose | pw_tmpl |
| slabL2_relax_v2_avg.dat | 138000 | 794bf8a86dea67a4 | loose | avg_dat |
| slabL2_relax_v2_driver.log | 984 | 3d4f42f53b6a3820 | loose | driver |
| steps.sh | 812 | c17fe5142be5a6a5 | loose | steps |
| vcrelax.in | 4312 | 1ad24163040f2bc0 | loose | pw_in |
| vcrelax.out | 3095976 | 2b126ca96f7c062b | loose | pw_out |

Tarball `slabL2_relax_v2_results.tar.gz` (2469848 B, sha256 d702401ec3a8e27d): 162 members; identical to the loose copy: 17; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 145

PDOS set `pdos`: 145 files.

## Resources and run history

- `slabL2_relax_v2_driver.log`: host b9pgpun302.cern.ch, 11 CPUs, wall limit 259200 s, GPU: 1 GPU(s), NVIDIA H100 NVL, 95830 MiB, job total 45305 s, start 2026-10-05T21:23:04Z
  - step vcrelax: -nk 1, max_seconds 257381, start 2026-10-05T21:23:23Z, end 2026-10-06T07:22:27Z, rc 0, PWSCF        :      9h53m CPU      9h58m WALL
  - step scf: -nk 1, max_seconds 221436, start 2026-10-06T07:22:28Z, end 2026-10-06T08:29:29Z, rc 0, PWSCF        :      1h 3m CPU      1h 6m WALL
  - step bands: -nk 1, max_seconds 217376, start 2026-10-06T08:30:08Z, end 2026-10-06T09:58:09Z, rc 0, PWSCF        :      1h23m CPU      1h27m WALL
  - log: [2026-10-05T21:23:23Z] pools for the CPU steps: 1 (NCPU 11)
  - log: [2026-10-06T08:29:46Z] planar average slabL2_relax_v2: 3000 lines
  - log: [2026-10-06T08:30:07Z] pdos slabL2_relax_v2: 145 files
- HTCondor slabL2_relax_v2 12835386.2: 11 CPUs, 1 GPU; seen 2026-10-05T19:50:32Z to 2026-10-06T09:58:10Z (150 samples); states {'1': 16, '2': 134} (1 idle, 2 running, 3 removed, 5 held); max scf_it 3486, max BFGS 77; steps ['vcrelax', 'scf', 'bands']; hw ['1xNVIDIA H100 NVL|0%', '1xNVIDIA H100 NVL|1%', '1xNVIDIA H100 NVL|10%', '1xNVIDIA H100 NVL|11%', '1xNVIDIA H100 NVL|12%', '1xNVIDIA H100 NVL|13%', '1xNVIDIA H100 NVL|14%', '1xNVIDIA H100 NVL|20%', '1xNVIDIA H100 NVL|22%', '1xNVIDIA H100 NVL|27%', '1xNVIDIA H100 NVL|3%', '1xNVIDIA H100 NVL|33%', '1xNVIDIA H100 NVL|4%', '1xNVIDIA H100 NVL|45%', '1xNVIDIA H100 NVL|48%', '1xNVIDIA H100 NVL|50%', '1xNVIDIA H100 NVL|55%', '1xNVIDIA H100 NVL|59%', '1xNVIDIA H100 NVL|6%', '1xNVIDIA H100 NVL|60%', '1xNVIDIA H100 NVL|64%', '1xNVIDIA H100 NVL|66%', '1xNVIDIA H100 NVL|7%', '1xNVIDIA H100 NVL|72%', '1xNVIDIA H100 NVL|77%', '1xNVIDIA H100 NVL|78%', '1xNVIDIA H100 NVL|79%', '1xNVIDIA H100 NVL|8%', '1xNVIDIA H100 NVL|82%', '1xNVIDIA H100 NVL|83%', '1xNVIDIA H100 NVL|84%', '1xNVIDIA H100 NVL|88%', '1xNVIDIA H100 NVL|89%', '1xNVIDIA H100 NVL|9%', '1xNVIDIA H100 NVL|91%', '1xNVIDIA H100 NVL|95%', '1xNVIDIA H100 NVL|96%', '1xNVIDIA H100 NVL|97%', '1xNVIDIA H100 NVL|98%'] ['Intel(R) Xeon(R) Platinum 8468']
- `steps.sh`: `steps() { # 2026-10-05: faster copy of STEPS_THIN_SLAB. Pools chosen at run time from the CPUs actually granted (CERN sizes # jobs by memory; -nk must divide the rank count, see iwo_slab2_final_cpu); 4 irreducible k-points NKP=1; for p in 4 2; do [ $((NCPU % p)) -eq 0 ] && { NKP=$p; break; }; done log "pools for the CPU steps: $NKP (NCPU $NCPU)" run_pw vcrelax $NKP python qeio.py converged vcrelax.out || { log "relaxation did not finish; later steps skipped"; return 0; } for t in scf bands; do python qeio.py newgeom $t.tmpl vcrelax.out > $t.in; done clean_tmp export FORCE_CPU=1 # one QE version (CPU 7.5) for SCF, pp.x, projwfc.x and bands run_pw scf $NKP || return 0 run_ppavg slab "$JOB" 4.8689 run_pdos slab "$JOB" "$(python qeio.py fermi scf.out)" $NKP run_pw bands $NKP }`

## Calculation `bands.out` (bands)

QE v.7.5 started 6Oct2026 10:30: 8; 11 MPI x 1 threads on 1 node(s); pools 1; R&G division 11; node memory 44644.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: JOB DONE; terminated 11:57:12   6Oct2026; PWSCF time {'cpu': '1h23m', 'wall': '1h27m', 'calls': None}; output lines 1287.

**Input settings** (every namelist variable):

- &CONTROL: calculation = bands, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 217376
- &SYSTEM: ibrav = 0, nat = 76, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 240
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.428398884, 0.0, 0.0], [0.0, 10.292830784, 0.0], [0.0, 0.0, 32.48332619]]}
- K_POINTS: {"mode": "tpiba", "n": 21, "points_first_last": [[0.0, 0.0, 0.0, 1.0], [0.1739764, 0.1739764, 0.0, 1.0]], "path_points": [[0.0, 0.0, 0.0, 1.0], [0.02460398, 0.0, 0.0, 1.0], [0.04920796, 0.0, 0.0, 1.0], [0.07381193, 0.0, 0.0, 1.0], [0.09841591, 0.0, 0.0, 1.0], [0.12301989, 0.0, 0.0, 1.0], [0.14762387, 0.0, 0.0, 1.0], [0.17222785, 0.0, 0.0, 1.0], [0.19683182, 0.0, 0.0, 1.0], [0.2214358, 0.0, 0.0, 1.
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 76, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.7068  a.u.; unit-cell volume = 23529.3301 (a.u.)^3; number of atoms/cell = 76; number of atomic types = 3; number of electrons = 448.00; number of Kohn-Sham states = 240; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.706818, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 4 Sym. Ops. (no inversion) found ( 3 have fractional translation); k points: number of k points=    21 (sum of weights 2.0); FFT: Dense  grid:  5379071 G-vectors     FFT dimensions: ( 150, 150, 480) / Smooth grid:  1901577 G-vectors     FFT dimensions: ( 108, 108, 360)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '454.96 MB', 'Estimated max dynamical RAM per process': '2.06 GB', 'Estimated total dynamical RAM': '22.68 GB'}; start: ['Starting wfcs are  312 randomized atomic wfcs']
- Band-structure run: {'diag': 'Davidson diagonalization with overlap', 'kpts_done': 21, 'ethr': 'ethr =  2.23E-13,  avg # of iterations =120.0'}

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 21, "n_bands": 240, "n_occ": 224, "VBM_eV": -3.3536, "VBM_k_index": 0, "CBM_eV": -1.1551, "CBM_k_index": 0, "gap_eV": 2.1985, "direct_gap_min_eV": 2.1985, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.0162, "CB_width_bottom_band_eV": 0.2336, "E2_minus_E1_at_k0_eV": 1.8152}

**Warnings/errors**: message_from_routine x1 (first: line 33 'Message from routine setup:'); c_bands_not_converged x21 (first: line 437 'c_bands:  2 eigenvalues not converged'); ieee x3 (first: line 1285 'Note: The following floating-point exceptions are signalling: IEEE_UNDERFLOW_FLAG IEEE_DEN'); discouraged x1 (first: line 34 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Calculation `scf.out` (scf/relax)

QE v.7.5 started 6Oct2026 9:22:28; 11 MPI x 1 threads on 1 node(s); pools 1; R&G division 11; node memory 49397.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: JOB DONE; terminated 10:29: 7   6Oct2026; PWSCF time {'cpu': '1h 3m', 'wall': '1h 6m', 'calls': None}; output lines 2483.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 221436
- &SYSTEM: ibrav = 0, nat = 76, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 240
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.428398884, 0.0, 0.0], [0.0, 10.292830784, 0.0], [0.0, 0.0, 32.48332619]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 76, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.7068  a.u.; unit-cell volume = 23529.3301 (a.u.)^3; number of atoms/cell = 76; number of atomic types = 3; number of electrons = 448.00; number of Kohn-Sham states = 240; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.706818, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 4 Sym. Ops. (no inversion) found ( 3 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  5379071 G-vectors     FFT dimensions: ( 150, 150, 480) / Smooth grid:  1901577 G-vectors     FFT dimensions: ( 108, 108, 360)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '786.51 MB', 'Estimated max dynamical RAM per process': '3.02 GB', 'Estimated total dynamical RAM': '33.18 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     447.9402, renormalised to     448.0000', 'Starting wfcs are  312 randomized atomic wfcs']

**Convergence** (1 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 63 | 4.4e-10 | -8102.10627865 |  | 0.0009857 | 0.000405 | 0.006119 | 6.7e-05 | -0.12 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.001582, 0.0], HOMO_eV = -3.3537, LUMO_eV = -1.1551, E_Ry = -8102.10627865, E_all_electron_Ry = -193663.661754, acc_final_Ry = 4.4e-10, one_electron_Ry = -44304.70880986, hartree_Ry = 22355.23996325, xc_Ry = -1027.52397121, ewald_Ry = 19582.23988161, paw_one_center_Ry = -4707.35334245, converged_iterations = 63
- stress tensor (kbar): [[0.03, 0.0, 0.0], [0.0, -0.05, 0.0], [0.0, 0.0, -0.34]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 240, "n_occ": 224, "VBM_eV": -3.3537, "VBM_k_index": 0, "CBM_eV": -1.1551, "CBM_k_index": 0, "gap_eV": 2.1986, "direct_gap_min_eV": 2.1986, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.046, "CB_width_bottom_band_eV": 0.7539, "E2_minus_E1_at_k0_eV": 1.8151}

**Warnings/errors**: message_from_routine x1 (first: line 29 'Message from routine setup:'); c_bands_not_converged x29 (first: line 471 'c_bands:  2 eigenvalues not converged'); discouraged x1 (first: line 30 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Calculation `vcrelax.out` (scf/relax)

QE v.7.3.1 started 5Oct2026 23:23:24; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 51686.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled; GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled. Completed: JOB DONE; terminated 9:22:20   6Oct2026; PWSCF time {'cpu': '9h53m', 'wall': '9h58m', 'calls': None}; output lines 66994.

**Input settings** (every namelist variable):

- &CONTROL: calculation = vc-relax, prefix = vcr, outdir = ./tmp, pseudo_dir = ./, verbosity = low, tprnfor = .true., tstress = .true., max_seconds = 257381, nstep = 300, etot_conv_thr = 1.0d-4, forc_conv_thr = 1.0d-3
- &SYSTEM: ibrav = 0, nat = 76, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 232
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- &IONS: ion_dynamics = bfgs
- &CELL: cell_dynamics = bfgs, cell_dofree = 2Dxy, press_conv_thr = 0.5
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.3060902, 0.0, 0.0], [0.0, 10.3060902, 0.0], [0.0, 0.0, 32.48332619]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 76, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4757  a.u.; unit-cell volume = 23283.3235 (a.u.)^3; number of atoms/cell = 76; number of atomic types = 3; number of electrons = 448.00; number of Kohn-Sham states = 232; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; energy convergence thresh. = 1.0E-04; force convergence thresh. = 1.0E-03; press convergence thresh. = 5.0E-01; Exchange-correlation = SLA  PW   PBX  PBC; nstep = 300; celldm = [19.475688, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0) (re-read 3 times in the final SCF)
- Symmetry: 4 Sym. Ops. (no inversion) found ( 3 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  5379071 G-vectors     FFT dimensions: ( 150, 150, 480) / Smooth grid:  1901577 G-vectors     FFT dimensions: ( 108, 108, 360)
- RAM (pw.x estimate): {'Estimated max dynamical RAM per process': '33.10 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     447.9402, renormalised to     448.0000', 'Starting wfcs are  312 randomized atomic wfcs', 'Initial potential from superposition of free atoms', 'starting charge     447.9402, renormalised to     448.0000', 'Starting wfcs are  312 randomized atomic wfcs']

**Convergence** (80 SCF + BFGS): bfgs converged in  79 scf cycles and  78 bfgs steps (criteria: energy <  1.0E-04 Ry, force <  1.0E-03 Ry/Bohr, cell <  5.0E-01 kbar) final energy None final enthalpy -8102.1054119767 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 108 | 9.8e-10 | -8101.52990232 | -8101.5299023203 | 0.0473 | 0.0177 | 0.267162 | 5.2e-05 | -3.68 | 3453.639 | 10.3113, 10.3110 | 0.04956 |
| 1 | 31 | 8.3e-10 | -8101.58068256 | -8101.5806825609 | 0.02987 | 0.0123 | 0.185489 | 0.000144 | -4.34 | 3463.21921 | 10.3260, 10.3249 | 0.08441 |
| 2 | 58 | 2.8e-10 | -8101.62379217 | -8101.6237921739 | 0.02824 | 0.0107 | 0.161426 | 4.6e-05 | -0.88 | 3470.44493 | 10.3370, 10.3354 | 0.03929 |
| 3 | 30 | 1.6e-10 | -8101.64739815 | -8101.6473981516 | 0.02956 | 0.00986 | 0.148868 | 4.9e-05 | -1.66 | 3478.47455 | 10.3493, 10.3471 | 0.04325 |
| 4 | 29 | 1.5e-10 | -8101.67098028 | -8101.6709802752 | 0.02727 | 0.00976 | 0.14731 | 3.5e-05 | -2.14 | 3490.19264 | 10.3670, 10.3642 | 0.06495 |
| 5 | 51 | 2.2e-10 | -8101.7020203 | -8101.7020202961 | 0.0226 | 0.00963 | 0.145369 | 3.9e-05 | -2.72 | 3507.01858 | 10.3923, 10.3888 | 0.09757 |
| 6 | 47 | 1.2e-10 | -8101.73851679 | -8101.7385167938 | 0.02612 | 0.00995 | 0.150182 | 2.5e-05 | -3.48 | 3530.9529 | 10.4279, 10.4240 | 0.1467 |
| 7 | 50 | 6.3e-11 | -8101.77214595 | -8101.7721459457 | 0.02858 | 0.0115 | 0.173347 | 2.9e-05 | -4.42 | 3544.03297 | 10.4467, 10.4438 | 0.09345 |
| 8 | 46 | 2.4e-10 | -8101.78876629 | -8101.7887662856 | 0.02374 | 0.00876 | 0.132206 | 5.8e-05 | -4.09 | 3551.35509 | 10.4563, 10.4558 | 0.07867 |
| 9 | 45 | 9.9e-11 | -8101.80228597 | -8101.8022859718 | 0.01357 | 0.00535 | 0.080832 | 3.6e-05 | -2.9 | 3552.51239 | 10.4561, 10.4594 | 0.06317 |
| 10 | 45 | 9.8e-11 | -8101.81237907 | -8101.812379071 | 0.01672 | 0.00615 | 0.092885 | 2.7e-05 | -1.58 | 3550.89951 | 10.4511, 10.4596 | 0.08014 |
| 11 | 42 | 9.9e-11 | -8101.82227999 | -8101.8222799851 | 0.01451 | 0.00538 | 0.081228 | 3.4e-05 | -0.86 | 3536.58385 | 10.4264, 10.4421 | 0.07835 |
| 12 | 52 | 9.3e-11 | -8101.83327132 | -8101.8332713167 | 0.01714 | 0.00628 | 0.094835 | 1.7e-05 | 0.63 | 3524.24753 | 10.4056, 10.4265 | 0.07379 |
| 13 | 42 | 1.7e-10 | -8101.84080936 | -8101.8408093616 | 0.01557 | 0.00571 | 0.086272 | 3.6e-05 | 0.87 | 3513.49883 | 10.3894, 10.4109 | 0.05164 |
| 14 | 38 | 1.5e-10 | -8101.84805292 | -8101.848052923 | 0.01043 | 0.0046 | 0.069526 | 3.7e-05 | 1.0 | 3510.14503 | 10.3850, 10.4054 | 0.04393 |
| 15 | 66 | 6.4e-11 | -8101.85457082 | -8101.8545708154 | 0.01308 | 0.00511 | 0.077191 | 2e-05 | 0.73 | 3508.84862 | 10.3839, 10.4027 | 0.06587 |
| 16 | 46 | 1.2e-10 | -8101.86192663 | -8101.8619266336 | 0.01442 | 0.00552 | 0.08339 | 4.3e-05 | 0.51 | 3508.30093 | 10.3843, 10.4006 | 0.09879 |
| 17 | 63 | 8.5e-11 | -8101.8707575 | -8101.870757497 | 0.01468 | 0.00609 | 0.092023 | 3.3e-05 | 0.32 | 3508.40797 | 10.3865, 10.3987 | 0.1482 |
| 18 | 39 | 5e-11 | -8101.88169948 | -8101.8816994834 | 0.01749 | 0.00673 | 0.101581 | 2e-05 | -0.03 | 3509.10558 | 10.3919, 10.3954 | 0.2223 |
| 19 | 47 | 1.6e-10 | -8101.89645586 | -8101.896455865 | 0.01676 | 0.0067 | 0.101105 | 3.2e-05 | -0.57 | 3509.74061 | 10.3964, 10.3928 | 0.1709 |
| 20 | 56 | 1.1e-10 | -8101.91001438 | -8101.9100143845 | 0.01281 | 0.00562 | 0.084898 | 3e-05 | -0.99 | 3508.26826 | 10.3975, 10.3874 | 0.1826 |
| 21 | 48 | 1e-10 | -8101.92399352 | -8101.9239935237 | 0.01465 | 0.0049 | 0.074039 | 4.7e-05 | -1.36 | 3506.08223 | 10.3949, 10.3834 | 0.05468 |
| 22 | 48 | 9.7e-11 | -8101.93086032 | -8101.9308603175 | 0.02376 | 0.00778 | 0.117509 | 3.9e-05 | -0.76 | 3501.53824 | 10.3882, 10.3766 | 0.164 |
| 23 | 56 | 1.3e-10 | -8101.932593 | -8101.9325929958 | 0.02652 | 0.0077 | 0.116205 | 2.2e-05 | -2.54 | 3500.59416 | 10.3858, 10.3763 | 0.08375 |
| 24 | 57 | 1.1e-10 | -8101.94279901 | -8101.9427990113 | 0.01584 | 0.00544 | 0.082165 | 1.9e-05 | -1.32 | 3497.87696 | 10.3799, 10.3741 | 0.0664 |
| 25 | 38 | 9e-11 | -8101.94979733 | -8101.9497973278 | 0.01012 | 0.00363 | 0.054759 | 2.9e-05 | -1.0 | 3494.89234 | 10.3748, 10.3703 | 0.08063 |
| 26 | 41 | 7.2e-11 | -8101.95599773 | -8101.9559977273 | 0.007504 | 0.00307 | 0.046334 | 1.9e-05 | -1.33 | 3490.84016 | 10.3688, 10.3643 | 0.06362 |
| 27 | 43 | 4.8e-11 | -8101.95930177 | -8101.9593017744 | 0.0118 | 0.00355 | 0.053552 | 2.4e-05 | -1.41 | 3488.46331 | 10.3662, 10.3599 | 0.1093 |
| 28 | 34 | 5.9e-11 | -8101.96409961 | -8101.9640996051 | 0.01326 | 0.00504 | 0.076051 | 2.9e-05 | -1.58 | 3485.08678 | 10.3613, 10.3548 | 0.05904 |
| 29 | 36 | 8.9e-11 | -8101.96871279 | -8101.9687127948 | 0.01085 | 0.00467 | 0.070486 | 3.4e-05 | -0.7 | 3482.87067 | 10.3587, 10.3507 | 0.0882 |
| 30 | 50 | 6.1e-11 | -8101.97423513 | -8101.9742351264 | 0.009535 | 0.00377 | 0.056983 | 3.4e-05 | 0.5 | 3481.83703 | 10.3581, 10.3483 | 0.09349 |
| 31 | 40 | 7.7e-11 | -8101.97952254 | -8101.9795225434 | 0.01031 | 0.00392 | 0.059233 | 3.9e-05 | 1.79 | 3481.75724 | 10.3606, 10.3455 | 0.1455 |
| 32 | 34 | 6.4e-11 | -8101.98539495 | -8101.9853949498 | 0.01254 | 0.00509 | 0.076908 | 4.6e-05 | 2.47 | 3490.37148 | 10.3771, 10.3546 | 0.1399 |
| 33 | 44 | 1.1e-10 | -8101.99124649 | -8101.9912464929 | 0.01517 | 0.00585 | 0.088368 | 4e-05 | 3.4 | 3498.49732 | 10.3952, 10.3607 | 0.1437 |
| 34 | 44 | 1.4e-10 | -8101.99682069 | -8101.9968206942 | 0.01558 | 0.00543 | 0.081917 | 6.2e-05 | 2.31 | 3514.9841 | 10.4271, 10.3776 | 0.09762 |
| 35 | 39 | 1.1e-10 | -8102.00465291 | -8102.0046529052 | 0.009168 | 0.00412 | 0.062179 | 2.7e-05 | 0.74 | 3530.56306 | 10.4584, 10.3925 | 0.1354 |
| 36 | 42 | 6.4e-11 | -8102.01006202 | -8102.010062023 | 0.02013 | 0.00532 | 0.080353 | 2e-05 | -0.5 | 3542.96936 | 10.4814, 10.4061 | 0.06795 |
| 37 | 39 | 1.8e-10 | -8102.01436125 | -8102.01436125 | 0.01329 | 0.00499 | 0.075288 | 4e-05 | -1.05 | 3556.41927 | 10.5087, 10.4184 | 0.1567 |
| 38 | 40 | 1.2e-10 | -8102.01911295 | -8102.019112953 | 0.02287 | 0.00566 | 0.085484 | 5e-05 | -2.01 | 3558.89672 | 10.5147, 10.4198 | 0.07327 |
| 39 | 40 | 9.8e-11 | -8102.02528898 | -8102.0252889812 | 0.02054 | 0.00462 | 0.069819 | 3.1e-05 | -1.67 | 3558.92793 | 10.5172, 10.4174 | 0.07996 |
| 40 | 34 | 1.8e-10 | -8102.03099249 | -8102.0309924863 | 0.01408 | 0.00402 | 0.060669 | 2.6e-05 | -1.42 | 3561.17556 | 10.5260, 10.4153 | 0.119 |
| 41 | 48 | 1.2e-10 | -8102.03566972 | -8102.0356697211 | 0.01826 | 0.00488 | 0.073756 | 3.3e-05 | -1.86 | 3552.28819 | 10.5168, 10.3983 | 0.09187 |
| 42 | 41 | 1.5e-10 | -8102.04018665 | -8102.0401866519 | 0.01828 | 0.006 | 0.090559 | 2.4e-05 | -1.42 | 3557.48664 | 10.5371, 10.3935 | 0.2493 |
| 43 | 53 | 1e-10 | -8102.04290288 | -8102.0429028835 | 0.03012 | 0.00811 | 0.122518 | 3e-05 | -2.83 | 3552.78429 | 10.5266, 10.3901 | 0.07822 |
| 44 | 53 | 2.5e-10 | -8102.05021449 | -8102.0502144884 | 0.008489 | 0.00327 | 0.049327 | 5.3e-05 | -1.73 | 3545.48836 | 10.5199, 10.3754 | 0.08045 |
| 45 | 51 | 1.7e-11 | -8102.05602248 | -8102.0560224767 | 0.008447 | 0.00303 | 0.045678 | 1.1e-05 | -1.09 | 3535.19851 | 10.5103, 10.3547 | 0.1206 |
| 46 | 49 | 7.1e-11 | -8102.06149509 | -8102.0614950881 | 0.01014 | 0.00336 | 0.050738 | 2.1e-05 | -0.47 | 3519.78372 | 10.4960, 10.3237 | 0.1807 |
| 47 | 46 | 4.2e-11 | -8102.06771863 | -8102.0677186269 | 0.009798 | 0.00367 | 0.055345 | 2.3e-05 | 0.19 | 3493.14775 | 10.4679, 10.2730 | 0.2424 |
| 48 | 39 | 6.5e-11 | -8102.0734856 | -8102.0734855966 | 0.01339 | 0.00433 | 0.06532 | 2.2e-05 | 1.28 | 3485.58594 | 10.4582, 10.2603 | 0.05143 |
| 49 | 40 | 1.2e-10 | -8102.07676684 | -8102.076766838 | 0.01004 | 0.00331 | 0.049909 | 3e-05 | 1.78 | 3480.47905 | 10.4585, 10.2449 | 0.1361 |
| 50 | 45 | 6.2e-11 | -8102.08192887 | -8102.0819288722 | 0.0098 | 0.00375 | 0.05655 | 3e-05 | 1.3 | 3489.85009 | 10.4760, 10.2553 | 0.06004 |
| 51 | 46 | 2.7e-11 | -8102.08608 | -8102.0860800004 | 0.01196 | 0.0041 | 0.061902 | 1.2e-05 | 0.35 | 3497.38689 | 10.4915, 10.2624 | 0.07805 |
| 52 | 42 | 8.2e-11 | -8102.08947929 | -8102.0894792862 | 0.009967 | 0.00339 | 0.051212 | 3.7e-05 | -0.52 | 3504.36446 | 10.5039, 10.2706 | 0.05983 |
| 53 | 43 | 6e-11 | -8102.09305607 | -8102.0930560735 | 0.008616 | 0.00277 | 0.041765 | 2.6e-05 | -1.11 | 3501.34586 | 10.5027, 10.2630 | 0.09648 |
| 54 | 42 | 1.2e-11 | -8102.09560434 | -8102.0956043446 | 0.00633 | 0.00208 | 0.031383 | 1.5e-05 | -1.43 | 3496.73513 | 10.4935, 10.2585 | 0.04596 |
| 55 | 46 | 4.9e-11 | -8102.09703744 | -8102.0970374383 | 0.007188 | 0.0019 | 0.028734 | 2.3e-05 | -1.01 | 3491.06348 | 10.4847, 10.2504 | 0.02568 |
| 56 | 38 | 6.2e-11 | -8102.09778556 | -8102.0977855562 | 0.003281 | 0.00137 | 0.020623 | 3.3e-05 | -0.77 | 3486.62279 | 10.4766, 10.2453 | 0.02372 |
| 57 | 45 | 1.4e-11 | -8102.09846766 | -8102.0984676591 | 0.003282 | 0.00127 | 0.019142 | 1.1e-05 | -0.51 | 3484.83973 | 10.4709, 10.2457 | 0.02939 |
| 58 | 37 | 2.2e-11 | -8102.09927103 | -8102.0992710293 | 0.005189 | 0.00161 | 0.02425 | 2e-05 | -0.24 | 3483.85659 | 10.4673, 10.2463 | 0.03921 |
| 59 | 27 | 2.3e-11 | -8102.09997005 | -8102.0999700463 | 0.006021 | 0.00171 | 0.025828 | 2e-05 | -0.17 | 3485.96612 | 10.4678, 10.2520 | 0.02382 |
| 60 | 46 | 3.9e-11 | -8102.10058226 | -8102.1005822554 | 0.003254 | 0.00114 | 0.017173 | 2.1e-05 | -0.08 | 3487.09704 | 10.4675, 10.2556 | 0.02742 |
| 61 | 37 | 2.3e-11 | -8102.10105799 | -8102.1010579939 | 0.002387 | 0.000879 | 0.013274 | 1.5e-05 | -0.03 | 3486.91722 | 10.4649, 10.2577 | 0.02196 |
| 62 | 40 | 2.1e-11 | -8102.10140405 | -8102.1014040461 | 0.002266 | 0.000935 | 0.014117 | 1.7e-05 | 0.06 | 3486.37828 | 10.4602, 10.2606 | 0.02695 |
| 63 | 38 | 4e-12 | -8102.10179428 | -8102.1017942754 | 0.002439 | 0.000973 | 0.014689 | 8e-06 | 0.12 | 3486.42436 | 10.4554, 10.2655 | 0.02539 |
| 64 | 35 | 1.3e-11 | -8102.1021751 | -8102.102175103 | 0.002581 | 0.000937 | 0.014146 | 1e-05 | 0.1 | 3487.65588 | 10.4522, 10.2723 | 0.02195 |
| 65 | 32 | 2.3e-11 | -8102.10252449 | -8102.1025244933 | 0.002816 | 0.000862 | 0.013015 | 1.8e-05 | -0.02 | 3489.79635 | 10.4510, 10.2798 | 0.02237 |
| 66 | 35 | 1.8e-11 | -8102.10283826 | -8102.1028382632 | 0.002237 | 0.000868 | 0.01311 | 1.6e-05 | -0.2 | 3492.03149 | 10.4507, 10.2866 | 0.02044 |
| 67 | 42 | 1.8e-11 | -8102.10313497 | -8102.103134973 | 0.002991 | 0.000934 | 0.014105 | 7e-06 | -0.39 | 3493.79211 | 10.4496, 10.2928 | 0.02757 |
| 68 | 40 | 3e-11 | -8102.10345846 | -8102.1034584568 | 0.002799 | 0.000934 | 0.014096 | 2.6e-05 | -0.51 | 3494.27823 | 10.4463, 10.2976 | 0.0399 |
| 69 | 39 | 2.1e-11 | -8102.10381409 | -8102.103814092 | 0.003022 | 0.000922 | 0.01392 | 1.9e-05 | -0.55 | 3493.16427 | 10.4401, 10.3004 | 0.04777 |
| 70 | 35 | 1.7e-11 | -8102.10419756 | -8102.1041975568 | 0.0028 | 0.000879 | 0.013275 | 8e-06 | -0.46 | 3490.78751 | 10.4324, 10.3010 | 0.04775 |
| 71 | 47 | 1.8e-11 | -8102.10453173 | -8102.104531734 | 0.002499 | 0.000766 | 0.011569 | 1.1e-05 | -0.32 | 3488.65279 | 10.4269, 10.3001 | 0.02696 |
| 72 | 45 | 2.5e-11 | -8102.10477522 | -8102.1047752159 | 0.002779 | 0.000778 | 0.011752 | 1.6e-05 | -0.16 | 3487.09528 | 10.4236, 10.2987 | 0.02357 |
| 73 | 38 | 2.4e-11 | -8102.10495475 | -8102.104954747 | 0.00178 | 0.000586 | 0.008846 | 2.2e-05 | -0.14 | 3486.78532 | 10.4243, 10.2972 | 0.01253 |
| 74 | 37 | 1.7e-11 | -8102.10509521 | -8102.1050952111 | 0.001944 | 0.000586 | 0.008846 | 1.6e-05 | -0.08 | 3487.01742 | 10.4258, 10.2964 | 0.01047 |
| 75 | 31 | 9.6e-12 | -8102.10520022 | -8102.1052002242 | 0.001652 | 0.000559 | 0.008445 | 8e-06 | -0.16 | 3487.47982 | 10.4278, 10.2958 | 0.006817 |
| 76 | 34 | 4.6e-12 | -8102.10528322 | -8102.1052832221 | 0.001809 | 0.000489 | 0.007391 | 8e-06 | -0.19 | 3487.34922 | 10.4286, 10.2946 | 0.01266 |
| 77 | 32 | 6.7e-12 | -8102.10535237 | -8102.105352369 | 0.001621 | 0.000447 | 0.006751 | 7e-06 | -0.19 | 3486.68699 | 10.4284, 10.2928 | 0.01394 |
| 78 | 30 | 7.1e-12 | -8102.10541198 |  | 0.0009904 | 0.000406 | 0.006128 | 6e-06 | -0.14 |  |  |  |
| 79 | 94 | 9e-12 | -8102.10627948 |  | 0.0009843 | 0.000405 | 0.006118 | 4e-06 | -0.13 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.001582, 0.0], HOMO_eV = -3.3536, LUMO_eV = -1.1551, E_Ry = -8102.10627948, E_all_electron_Ry = -193663.661755, acc_final_Ry = 9e-12, one_electron_Ry = -44304.70811108, hartree_Ry = 22355.23920773, xc_Ry = -1027.52390886, ewald_Ry = 19582.23988516, paw_one_center_Ry = -4707.35335243, converged_iterations = 94
- stress tensor (kbar): [[0.02, 0.0, 0.0], [0.0, -0.06, 0.0], [0.0, 0.0, -0.35]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 232, "n_occ": 224, "VBM_eV": -3.3536, "VBM_k_index": 0, "CBM_eV": -1.1551, "CBM_k_index": 0, "gap_eV": 2.1985, "direct_gap_min_eV": 2.1985, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.0461, "CB_width_bottom_band_eV": 0.7539, "E2_minus_E1_at_k0_eV": 1.8151}

**Final geometry** (vs `vcrelax.in`): {"n_atoms": 76, "composition": {"H": 24, "In": 16, "O": 36}, "cell_lengths_A": [10.4284, 10.29283, 32.48333], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3486.687, "density_g_cm3": 1.1607, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 96, "min": 2.1658, "mean": 2.2171, "max": 2.2992, "std": 0.036, "CN_In_hist": {"6": 16}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9718, "mean": 0.9779, "max": 0.9863, "std": 0.0055, "CN_O_hist": {"0": 12, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 12}, "slab": {"vacuum_A": 25.53, "extent_A": 6.953, "thickness_H_H_A": 6.9532, "thickness_O_O_A": 5.4208, "thickness_In_In_A": 2.921}, "displacement_vs_initial": {"max_A": 1.5024, "atom": "H71", "mean_A": 0.3584, "n_gt_0p1_A": 44, "by_element_max_A": {"H": 1.5024, "In": 0.0645, "O": 0.3785}, "outer_3A_mean_A": 0.4158, "interior_mean_A": 0.0522}, "reference_input": "vcrelax.in"}

**Warnings/errors**: message_from_routine x1 (first: line 29 'Message from routine setup:'); warning x3 (first: line 66991 'Warning: ieee_invalid is signaling'); c_bands_not_converged x60 (first: line 582 'c_bands:  2 eigenvalues not converged'); ieee x3 (first: line 66991 'Warning: ieee_invalid is signaling'); discouraged x1 (first: line 30 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized'); fortran_stop x1 (first: line 66994 'FORTRAN STOP')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `bands.in`: {"n_atoms": 76, "composition": {"H": 24, "In": 16, "O": 36}, "cell_lengths_A": [10.4284, 10.29283, 32.48333], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3486.687, "density_g_cm3": 1.1607, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 96, "min": 2.1658, "mean": 2.2171, "max": 2.2992, "std": 0.036, "CN_In_hist": {"6": 16}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9718, "mean": 0.9779, "max": 0.9863, "std": 0.0055, "CN_O_hist": {"0": 12, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 12}, "slab": {"vacuum_A": 25.53, "extent_A": 6.953, "thickness_H_H_A": 6.9532, "thickness_O_O_A": 5.4208, "thickness_In_In_A": 2.921}}
- `scf.in`: {"n_atoms": 76, "composition": {"H": 24, "In": 16, "O": 36}, "cell_lengths_A": [10.4284, 10.29283, 32.48333], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3486.687, "density_g_cm3": 1.1607, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 96, "min": 2.1658, "mean": 2.2171, "max": 2.2992, "std": 0.036, "CN_In_hist": {"6": 16}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9718, "mean": 0.9779, "max": 0.9863, "std": 0.0055, "CN_O_hist": {"0": 12, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 12}, "slab": {"vacuum_A": 25.53, "extent_A": 6.953, "thickness_H_H_A": 6.9532, "thickness_O_O_A": 5.4208, "thickness_In_In_A": 2.921}}
- `vcrelax.in`: {"n_atoms": 76, "composition": {"H": 24, "In": 16, "O": 36}, "cell_lengths_A": [10.30609, 10.30609, 32.48333], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3450.2326, "density_g_cm3": 1.173, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 96, "min": 2.1671, "mean": 2.2194, "max": 2.2561, "std": 0.0336, "CN_In_hist": {"6": 16}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.97, "mean": 0.97, "max": 0.97, "std": 0.0, "CN_O_hist": {"0": 12, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 12}, "slab": {"vacuum_A": 25.0, "extent_A": 7.483, "thickness_H_H_A": 7.4833, "thickness_O_O_A": 5.6086, "thickness_In_In_A": 2.9249}}

Geometry consistency (input of the follow-on step vs relax final coordinates): {"scf.in vs final of vcrelax.out": {"max_pos_diff_A": 0.0, "max_cell_diff_A": 0.0}, "bands.in vs final of vcrelax.out": {"max_pos_diff_A": 0.0, "max_cell_diff_A": 0.0}}

## projwfc `projwfc_slabL2_relax_v2.out`

natomwfc 312, nbnd 240, nkstot 4, states 312, spilling 0.0046, Loewdin total 445.956, PROJWFC      :     14.32s CPU     20.63s WALL, done True

| element | n | total charge mean (min-max) | s | p | d |
|---|---|---|---|---|---|
| In | 16 | 11.8272 (11.8204-11.8315) | 0.7027 | 1.1326 | 9.9919 |
| O | 36 | 6.7254 (6.7015-6.7405) | 1.7071 | 5.0183 | 0.0 |
| H | 24 | 0.6085 (0.6019-0.6189) | 0.6085 | 0.0 | 0.0 |

## PDOS `pdos`

{"n_files": 145, "E_window_eV": [-11.354, 0.656], "dE_eV": 0.01, "integral_dos_window": 220.767, "integral_dos_below_EF_or_VBM": 214.369, "reference_energy_eV": -3.3537}

| element, l | files | states in window | states below reference |
|---|---|---|---|
| H s | 24 | 7.704 | 7.308 |
| In d | 16 | 2.675 | 2.648 |
| In p | 16 | 12.551 | 12.011 |
| In s | 16 | 11.429 | 9.677 |
| O p | 36 | 177.911 | 175.238 |
| O s | 36 | 6.685 | 5.832 |

## Planar average `slabL2_relax_v2_avg.dat`

{"n_points": 3000, "V_min_eV": -11.1226, "V_max_eV": 2.7078, "window_A": 0.01083, "z_mean_V_eV": 0.72087, "E_vac_eV": 2.56221, "vacuum_flatness_meV": 210.983, "vacuum_slope_meV_per_A": -13.5975, "IP_eV": 5.9159, "EA_eV": 3.7173}
- `avg_slabL2_relax_v2.in` input: `1 slabL2_relax_v2_v.pp 1.0 3000 3 4.8689`
- `pp_slabL2_relax_v2.in` input: `&INPUTPP prefix = 'slab', outdir = './tmp', filplot = 'slabL2_relax_v2_v.pp', plot_num = 11 /`
- `projwfc_slabL2_relax_v2.in` input: `&PROJWFC prefix = 'slab', outdir = './tmp', filpdos = 'pdos/slabL2_relax_v2' Emin = -11.3537, Emax = 0.6463, DeltaE = 0.01, degauss = 0.0073, ngauss = 0 /`
- `avg_slabL2_relax_v2.out`: done True; Program AVERAGE v.7.5 starts on  6Oct2026 at 10:29:42 / Reading header from file  slabL2_relax_v2_v.pp / Reading data from file  slabL2_relax_v2_v.pp / AVERAGE      :      3.37s CPU      3.45s WALL / This run was terminated on:  10:29:46   6Oct2026
- `pp_slabL2_relax_v2.out`: done True; Program POST-PROC v.7.5 starts on  6Oct2026 at 10:29:29 / Reading xml data from directory: / Calling punch_plot, plot_num =  11 / Writing data to file  slabL2_relax_v2_v.pp / POST-PROC    :      9.62s CPU     10.44s WALL

## Other files

- `.fetched`: ''
