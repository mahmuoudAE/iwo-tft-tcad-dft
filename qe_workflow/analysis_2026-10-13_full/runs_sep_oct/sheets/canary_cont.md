# canary_cont

**Purpose.** Workflow test (toy 3-atom W slab cell, 2Dxy vc-relax): continuation logic, with nstep = 3 forcing an unconverged stop.

Folder `cern_htcondor/results/canary_cont`; data `runs_sep_oct/out/canary_cont.json` (+ `canary_cont_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| bands.tmpl | 1615 | 65478787d19086b5 | loose | pw_tmpl |
| canary_cont_driver.log | 482 | ad71777f31ca4399 | loose | driver |
| scf.tmpl | 807 | 34b2de4e390bf1fe | loose | pw_tmpl |
| steps.sh | 310 | be48c63421274d92 | loose | steps |
| vcrelax.in | 978 | 3c0320626cce1529 | loose | pw_in |
| vcrelax.out | 62166 | b52d9dec92b784f1 | loose | pw_out |

Tarball `canary_cont_results.tar.gz` (12869 B, sha256 315ee050d0d21ce8): 6 members; identical to the loose copy: 6; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0

## Resources and run history

- `canary_cont_driver.log`: host b9g42p1021.cern.ch, 2 CPUs, wall limit 7200 s, GPU: none (CPU), job total 317 s, start 2026-09-30T08:06:13Z
  - step vcrelax: -nk 2, max_seconds 5384, start 2026-09-30T08:06:29Z, end 2026-09-30T08:11:29Z, rc 0, PWSCF        :   4m28.43s CPU   4m46.94s WALL
  - log: [2026-09-30T08:11:30Z] relaxation did not finish; later steps skipped
- HTCondor: no entry in status_history.jsonl (it starts 2026-09-28T14:19Z).
- `steps.sh`: `steps() { run_pw vcrelax 2 python qeio.py converged vcrelax.out || { log "relaxation did not finish; later steps skipped"; return 0; } for t in scf bands; do python qeio.py newgeom $t.tmpl vcrelax.out > $t.in; done clean_tmp run_pw scf 2 || return 0 run_ppavg slab "$JOB" 1.4976 run_pw bands 2 }`

**What failed and why (from the files above).** By design: nstep = 3 in vcrelax.in stops the toy 3-atom W vc-relax after 3 SCF steps ("The maximum number of steps has been reached", vcrelax.out line 1607); qeio.py then reports it unconverged and the driver logs "relaxation did not finish; later steps skipped" (the continuation logic under test).

## Calculation `vcrelax.out` (scf/relax)

QE v.7.5 started 30Sep2026 10: 6:31; 2 MPI x 1 threads on 1 node(s); pools 2; R&G division -; node memory 10892.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: no GPU line. Completed: JOB DONE; terminated 10:11:18  30Sep2026; PWSCF time {'cpu': '4m28.43s', 'wall': '4m46.94s', 'calls': None}; output lines 1689.

**Input settings** (every namelist variable):

- &CONTROL: calculation = vc-relax, prefix = vcr, outdir = ./tmp, pseudo_dir = ./, verbosity = low, tprnfor = .true., tstress = .true., max_seconds = 5384, nstep = 3, etot_conv_thr = 1.0d-4, forc_conv_thr = 1.0d-3
- &SYSTEM: ibrav = 0, nat = 3, ntyp = 1, ecutwfc = 40, ecutrho = 320, occupations = smearing, smearing = mv, degauss = 0.02, nbnd = 29
- &ELECTRONS: conv_thr = 1.0d-6, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- &IONS: ion_dynamics = bfgs
- &CELL: cell_dynamics = bfgs, cell_dofree = 2Dxy, press_conv_thr = 0.5
- ATOMIC_SPECIES: [{"species": "W", "mass": 183.84, "pseudo": "W.pbe-spn-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[3.17, 0.0, 0.0], [0.0, 3.17, 0.0], [0.0, 0.0, 11.17]]}
- K_POINTS: {"mode": "automatic", "grid": ["6", "6", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 3, "labels": ["W"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 5.9904  a.u.; unit-cell volume = 757.4750 (a.u.)^3; number of atoms/cell = 3; number of atomic types = 1; number of electrons = 42.00; number of Kohn-Sham states = 29; kinetic-energy cutoff = 40.0000  Ry; charge density cutoff = 320.0000  Ry; scf convergence threshold = 1.0E-06; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; energy convergence thresh. = 1.0E-04; force convergence thresh. = 1.0E-03; press convergence thresh. = 5.0E-01; Exchange-correlation = SLA  PW   PBX  PBC; nstep = 3; celldm = [5.990432, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: W W.pbe-spn-kjpaw_psl.1.0.0.UPF md5 03c3df5b60893f488392c7401945500a (Projector augmented-wave + core cor, Z 14.0)
- Symmetry: 8 Sym. Ops. (no inversion) found; k points: number of k points=    10  Marzari-Vanderbilt smearing, width (Ry)=  0.0200 (sum of weights 2.0); FFT: Dense  grid:    73061 G-vectors     FFT dimensions: (  36,  36, 125) / Smooth grid:    25805 G-vectors     FFT dimensions: (  25,  25,  90)
- RAM (pw.x estimate): {'Estimated max dynamical RAM per process': '167.59 MB', 'Estimated total dynamical RAM': '317.34 MB'}; start: ['Initial potential from superposition of free atoms', 'starting charge      41.9983, renormalised to      42.0000', 'Starting wfcs are   39 randomized atomic wfcs']

**Convergence** (3 SCF + BFGS):   final energy None final enthalpy None max steps reached

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 19 | 6.9e-07 | -2280.37136677 | -2280.3713667736 | 0.05819 | 0.0247 | 0.073968 | 0.000821 | -105.92 | 107.40628 | 3.1009, 3.1009 | 0.12 |
| 1 | 33 | 4.4e-07 | -2280.39734513 | -2280.397345131 | 0.01997 | 0.00848 | 0.025453 | 0.001931 | -53.49 | 102.20555 | 3.0249, 3.0249 | 0.132 |
| 2 | 43 | 1.6e-07 | -2280.40598587 | -2280.4059858719 | 0.03178 | 0.0136 | 0.040907 | 0.001184 | 12.44 | 102.22576 | 3.0252, 3.0252 | 0.02721 |

**Final energies** (last SCF): negative_rho = [0.07347, 0.0], E_F_eV = 8.3941, E_Ry = -2280.40598587, E_all_electron_Ry = -96857.254999, acc_final_Ry = 1.6e-07, mTS_Ry = -0.00206166, internal_energy_Ry = -2280.40392421, one_electron_Ry = -859.42850885, hartree_Ry = 438.47938529, xc_Ry = -120.05691223, ewald_Ry = 77.31017092, paw_one_center_Ry = -1816.70805935, converged_iterations = 43, bfgs_energy_error_Ry = 0.0086, enthalpy_old_Ry = -2280.397345131, enthalpy_new_Ry = -2280.4059858719
- stress tensor (kbar): [[3.2, 0.0, 0.0], [0.0, 3.2, 0.0], [0.0, 0.0, 30.93]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 10, "n_bands": 29, "E_F_eV": 8.3941, "bands_fully_below_EF": 19, "bands_crossing_EF_1based": [20, 21, 22, 23], "highest_band_below_EF_max_eV": 7.397, "lowest_band_above_EF_min_eV": 8.8391}

**Warnings/errors**: message_from_routine x1 (first: line 29 'Message from routine setup:'); discouraged x1 (first: line 30 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x1 (first: line 28 'file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized'); max_steps x1 (first: line 1607 'The maximum number of steps has been reached.')
- messages: ['file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `vcrelax.in`: {"n_atoms": 3, "composition": {"W": 3}, "cell_lengths_A": [3.17, 3.17, 11.17], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 112.2462, "density_g_cm3": 8.159, "bonds": {}, "slab": {"vacuum_A": 8.0, "extent_A": 3.17, "thickness_W_W_A": 3.17}}

## Other files

- `.fetched`: ''
