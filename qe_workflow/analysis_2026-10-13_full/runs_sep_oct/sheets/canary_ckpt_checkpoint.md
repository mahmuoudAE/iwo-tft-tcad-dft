# canary_ckpt_checkpoint

**Purpose.** Workflow test (toy 2-atom W cell): EOS checkpoint written during a relax.

Folder `cern_htcondor/results/canary_ckpt_checkpoint`; data `runs_sep_oct/out/canary_ckpt_checkpoint.json` (+ `canary_ckpt_checkpoint_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| canary_ckpt_driver.log | 358 | 9b5e0bb3224f1e4e | loose | driver |
| relax.in | 816 | 2d1df199d97a4236 | loose | pw_in |
| relax.out | 65637 | a2df673461edddf3 | loose | pw_out |
| steps.sh | 42 | d24993ab7430243c | loose | steps |

Tarball `canary_ckpt_12786696.tar.gz` (11743 B, sha256 b07c3301fbd25944): 4 members; identical to the loose copy: 4; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0

## Resources and run history

- `canary_ckpt_driver.log`: host b9g42p1033.cern.ch, 2 CPUs, wall limit 7200 s, GPU: none (CPU), job total None s, start 2026-09-30T08:06:13Z
  - step relax: -nk 1, max_seconds 5384, start 2026-09-30T08:06:29Z, end 2026-09-30T08:08:29Z, rc 0, PWSCF        :   1m41.93s CPU   1m45.32s WALL
- HTCondor: no entry in status_history.jsonl (it starts 2026-09-28T14:19Z).
- `steps.sh`: `steps() { run_pw relax 1 sleep 3000 }`

## Calculation `relax.out` (scf/relax)

QE v.7.5 started 30Sep2026 10: 6:31; 2 MPI x 1 threads on 1 node(s); pools 1; R&G division 2; node memory 869.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: no GPU line. Completed: JOB DONE; terminated 10: 8:17  30Sep2026; PWSCF time {'cpu': '1m41.93s', 'wall': '1m45.32s', 'calls': None}; output lines 1751.

**Input settings** (every namelist variable):

- &CONTROL: calculation = relax, prefix = rel, outdir = ./tmp, pseudo_dir = ./, verbosity = low, tprnfor = .true., tstress = .true., max_seconds = 5384, nstep = 300, etot_conv_thr = 1.0d-4, forc_conv_thr = 1.0d-3
- &SYSTEM: ibrav = 0, nat = 2, ntyp = 1, ecutwfc = 40, ecutrho = 320, occupations = smearing, smearing = mv, degauss = 0.02
- &ELECTRONS: conv_thr = 1.0d-6, mixing_beta = 0.3, electron_maxstep = 100
- &IONS: ion_dynamics = bfgs
- ATOMIC_SPECIES: [{"species": "W", "mass": 183.84, "pseudo": "W.pbe-spn-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[3.17, 0.0, 0.0], [0.0, 3.17, 0.0], [0.0, 0.0, 3.17]]}
- K_POINTS: {"mode": "automatic", "grid": ["4", "4", "4", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 2, "labels": ["W"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 5.9904  a.u.; unit-cell volume = 214.9683 (a.u.)^3; number of atoms/cell = 2; number of atomic types = 1; number of electrons = 28.00; number of Kohn-Sham states = 18; kinetic-energy cutoff = 40.0000  Ry; charge density cutoff = 320.0000  Ry; scf convergence threshold = 1.0E-06; mixing beta = 0.3000; number of iterations used = 8  plain     mixing; energy convergence thresh. = 1.0E-04; force convergence thresh. = 1.0E-03; Exchange-correlation = SLA  PW   PBX  PBC; nstep = 300; celldm = [5.990432, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: W W.pbe-spn-kjpaw_psl.1.0.0.UPF md5 03c3df5b60893f488392c7401945500a (Projector augmented-wave + core cor, Z 14.0)
- Symmetry: 8 Sym. Ops. (no inversion) found; k points: number of k points=    18  Marzari-Vanderbilt smearing, width (Ry)=  0.0200 (sum of weights 2.0); FFT: Dense  grid:    20719 G-vectors     FFT dimensions: (  36,  36,  36) / Smooth grid:     7249 G-vectors     FFT dimensions: (  25,  25,  25)
- RAM (pw.x estimate): {'Estimated max dynamical RAM per process': '41.72 MB', 'Estimated total dynamical RAM': '83.43 MB'}; start: ['Initial potential from superposition of free atoms', 'starting charge      27.9989, renormalised to      28.0000', 'Starting wfcs are   26 randomized atomic wfcs']

**Convergence** (4 SCF + BFGS): bfgs converged in   4 scf cycles and   3 bfgs steps (criteria: energy <  1.0E-04 Ry, force <  1.0E-03 Ry/Bohr) final energy -1520.5174993013 final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 8 | 3.8e-07 | -1520.51617112 |  | 0.02759 | 0.0159 | 0.039013 | 0.000377 | -1.59 |  |  | 0.02759 |
| 1 | 23 | 2.9e-07 | -1520.51726584 |  | 0.01047 | 0.00605 | 0.014811 | 0.001289 | -3.22 |  |  | 0.01688 |
| 2 | 24 | 9e-08 | -1520.51749484 |  | 0.001724 | 0.000995 | 0.002438 | 0.000372 | -3.72 |  |  | 0.003327 |
| 3 | 36 | 4.7e-09 | -1520.5174993 |  | 0.0002743 | 0.000158 | 0.000388 | 3.4e-05 | -3.74 |  |  |  |

**Final energies** (last SCF): E_F_eV = 22.2292, E_Ry = -1520.5174993, E_all_electron_Ry = -64571.750175, acc_final_Ry = 4.7e-09, mTS_Ry = 0.00165516, internal_energy_Ry = -1520.51915446, one_electron_Ry = -22.66405006, hartree_Ry = 31.55131499, xc_Ry = -80.14545892, ewald_Ry = -238.14301345, paw_one_center_Ry = -1211.11794701, converged_iterations = 36, bfgs_energy_error_Ry = 4.5e-06
- stress tensor (kbar): [[-3.75, 0.0, 0.0], [0.0, -3.74, 0.0], [0.0, 0.0, -3.74]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 18, "n_bands": 18, "E_F_eV": 22.2292, "bands_fully_below_EF": 12, "bands_crossing_EF_1based": [13, 14, 15, 16], "highest_band_below_EF_max_eV": 21.3415, "lowest_band_above_EF_min_eV": 23.8991}

**Final geometry** (vs `relax.in`): {"n_atoms": 2, "composition": {"W": 2}, "cell_lengths_A": [3.17, 3.17, 3.17], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 31.855, "density_g_cm3": 19.1664, "bonds": {}, "displacement_vs_initial": {"max_A": 0.0253, "atom": "W1", "mean_A": 0.0253, "n_gt_0p1_A": 0, "by_element_max_A": {"W": 0.0253}}, "reference_input": "relax.in"}

**Warnings/errors**: message_from_routine x1 (first: line 29 'Message from routine setup:'); discouraged x1 (first: line 30 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x1 (first: line 28 'file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized'); scf_correction_large x1 (first: line 1163 'SCF correction compared to forces is large: reduce conv_thr to get better values')
- messages: ['file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `relax.in`: {"n_atoms": 2, "composition": {"W": 2}, "cell_lengths_A": [3.17, 3.17, 3.17], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 31.855, "density_g_cm3": 19.1664, "bonds": {}}
