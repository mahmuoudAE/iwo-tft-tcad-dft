# canary_cont_c1

**Purpose.** Workflow test: second segment of the continuation test (restarts from vcrelax_prev.in).

Folder `cern_htcondor/results/canary_cont_c1`; data `runs_sep_oct/out/canary_cont_c1.json` (+ `canary_cont_c1_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| bands.tmpl | 1615 | 65478787d19086b5 | loose | pw_tmpl |
| canary_cont_c1_driver.log | 485 | 6b756948a9770fab | loose | driver |
| scf.tmpl | 807 | 34b2de4e390bf1fe | loose | pw_tmpl |
| steps.sh | 310 | be48c63421274d92 | loose | steps |
| vcrelax.in | 1059 | e68f810a5b46e97b | loose | pw_in |
| vcrelax.out | 54557 | 67709cc7606beed3 | loose | pw_out |
| vcrelax_prev.in | 979 | 70bec12c3ae8327e | loose | pw_in |

Tarball `canary_cont_c1_results.tar.gz` (12193 B, sha256 1915a2a4659187fd): 7 members; identical to the loose copy: 7; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0

## Resources and run history

- `canary_cont_c1_driver.log`: host b9g34p0623.cern.ch, 2 CPUs, wall limit 7200 s, GPU: none (CPU), job total 317 s, start 2026-09-30T08:15:28Z
  - step vcrelax: -nk 2, max_seconds 5384, start 2026-09-30T08:15:44Z, end 2026-09-30T08:20:44Z, rc 0, PWSCF        :   3m49.20s CPU   4m 7.26s WALL
  - log: [2026-09-30T08:20:45Z] relaxation did not finish; later steps skipped
- HTCondor: no entry in status_history.jsonl (it starts 2026-09-28T14:19Z).
- `steps.sh`: `steps() { run_pw vcrelax 2 python qeio.py converged vcrelax.out || { log "relaxation did not finish; later steps skipped"; return 0; } for t in scf bands; do python qeio.py newgeom $t.tmpl vcrelax.out > $t.in; done clean_tmp run_pw scf 2 || return 0 run_ppavg slab "$JOB" 1.4976 run_pw bands 2 }`

**What failed and why (from the files above).** By design: the continuation segment starts from the last geometry of canary_cont (vcrelax_prev.in = the previous input; vcrelax.in carries the new positions) with nstep = 3 again, and again stops on the step limit ("relaxation did not finish").

## Calculation `vcrelax.out` (scf/relax)

QE v.7.5 started 30Sep2026 10:15:46; 2 MPI x 1 threads on 1 node(s); pools 2; R&G division -; node memory 1057.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: no GPU line. Completed: JOB DONE; terminated 10:19:53  30Sep2026; PWSCF time {'cpu': '3m49.20s', 'wall': '4m 7.26s', 'calls': None}; output lines 1462.

**Input settings** (every namelist variable):

- &CONTROL: calculation = vc-relax, prefix = vcr, outdir = ./tmp, pseudo_dir = ./, verbosity = low, tprnfor = .true., tstress = .true., max_seconds = 5384, nstep = 3, etot_conv_thr = 1.0d-4, forc_conv_thr = 1.0d-3
- &SYSTEM: ibrav = 0, nat = 3, ntyp = 1, ecutwfc = 40, ecutrho = 320, occupations = smearing, smearing = mv, degauss = 0.02, nbnd = 29
- &ELECTRONS: conv_thr = 1.0d-6, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- &IONS: ion_dynamics = bfgs
- &CELL: cell_dynamics = bfgs, cell_dofree = 2Dxy, press_conv_thr = 0.5
- ATOMIC_SPECIES: [{"species": "W", "mass": 183.84, "pseudo": "W.pbe-spn-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[3.025196416, 0.0, 0.0], [0.0, 3.025196416, 0.0], [0.0, 0.0, 11.17]]}
- K_POINTS: {"mode": "automatic", "grid": ["6", "6", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 3, "labels": ["W"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 5.7168  a.u.; unit-cell volume = 689.8536 (a.u.)^3; number of atoms/cell = 3; number of atomic types = 1; number of electrons = 42.00; number of Kohn-Sham states = 29; kinetic-energy cutoff = 40.0000  Ry; charge density cutoff = 320.0000  Ry; scf convergence threshold = 1.0E-06; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; energy convergence thresh. = 1.0E-04; force convergence thresh. = 1.0E-03; press convergence thresh. = 5.0E-01; Exchange-correlation = SLA  PW   PBX  PBC; nstep = 3; celldm = [5.716793, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: W W.pbe-spn-kjpaw_psl.1.0.0.UPF md5 03c3df5b60893f488392c7401945500a (Projector augmented-wave + core cor, Z 14.0)
- Symmetry: 8 Sym. Ops. (no inversion) found; k points: number of k points=    10  Marzari-Vanderbilt smearing, width (Ry)=  0.0200 (sum of weights 2.0); FFT: Dense  grid:    66709 G-vectors     FFT dimensions: (  36,  36, 125) / Smooth grid:    23665 G-vectors     FFT dimensions: (  24,  24,  90)
- RAM (pw.x estimate): {'Estimated max dynamical RAM per process': '154.21 MB', 'Estimated total dynamical RAM': '292.13 MB'}; start: ['Initial potential from superposition of free atoms', 'starting charge      41.9983, renormalised to      42.0000', 'Starting wfcs are   39 randomized atomic wfcs']

**Convergence** (3 SCF + BFGS):   final energy None final enthalpy None max steps reached

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 20 | 8.6e-07 | -2280.40521879 | -2280.4052187926 | 0.02264 | 0.00977 | 0.029309 | 0.001209 | 5.72 | 102.12719 | 3.0237, 3.0237 | 0.02264 |
| 1 | 14 | 9.8e-07 | -2280.40598087 | -2280.4059808677 | 0.01591 | 0.00692 | 0.020767 | 0.001534 | 0.3 | 101.78745 | 3.0187, 3.0187 | 0.02491 |
| 2 | 40 | 2e-08 | -2280.40670604 | -2280.4067060426 | 0.01108 | 0.00501 | 0.015031 | 0.000369 | -2.54 | 101.08844 | 3.0083, 3.0083 | 0.03736 |

**Final energies** (last SCF): negative_rho = [0.06439, 0.0], E_F_eV = 8.4582, E_Ry = -2280.40670604, E_all_electron_Ry = -96857.255719, acc_final_Ry = 2e-08, mTS_Ry = -0.00341522, internal_energy_Ry = -2280.40329082, one_electron_Ry = -840.80983199, hartree_Ry = 429.20579247, xc_Ry = -120.00024441, ewald_Ry = 67.90445688, paw_one_center_Ry = -1816.70346377, converged_iterations = 40, bfgs_energy_error_Ry = 0.00073, enthalpy_old_Ry = -2280.4059808677, enthalpy_new_Ry = -2280.4067060426
- stress tensor (kbar): [[-9.29, 0.0, 0.0], [0.0, -9.29, 0.0], [0.0, 0.0, 10.97]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 10, "n_bands": 29, "E_F_eV": 8.4582, "bands_fully_below_EF": 19, "bands_crossing_EF_1based": [20, 21, 22, 23], "highest_band_below_EF_max_eV": 7.4392, "lowest_band_above_EF_min_eV": 8.9749}

**Warnings/errors**: message_from_routine x1 (first: line 29 'Message from routine setup:'); discouraged x1 (first: line 30 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x1 (first: line 28 'file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized'); max_steps x1 (first: line 1380 'The maximum number of steps has been reached.')
- messages: ['file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `vcrelax.in`: {"n_atoms": 3, "composition": {"W": 3}, "cell_lengths_A": [3.0252, 3.0252, 11.17], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 102.2258, "density_g_cm3": 8.9588, "bonds": {}, "slab": {"vacuum_A": 8.056, "extent_A": 3.114, "thickness_W_W_A": 3.1135}}
- `vcrelax_prev.in`: {"n_atoms": 3, "composition": {"W": 3}, "cell_lengths_A": [3.17, 3.17, 11.17], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 112.2462, "density_g_cm3": 8.159, "bonds": {}, "slab": {"vacuum_A": 8.0, "extent_A": 3.17, "thickness_W_W_A": 3.17}}

## Other files

- `.fetched`: ''
