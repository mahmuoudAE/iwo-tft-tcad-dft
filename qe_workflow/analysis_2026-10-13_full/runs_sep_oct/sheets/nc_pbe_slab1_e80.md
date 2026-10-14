# nc_pbe_slab1_e80

**Purpose.** NC PBE single point of the relaxed 1 nm slab, 80 Ry.

Folder `cern_htcondor/results/nc_pbe_slab1_e80`; data `runs_sep_oct/out/nc_pbe_slab1_e80.json` (+ `nc_pbe_slab1_e80_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| nc_pbe_slab1_e80_driver.log | 480 | edbd74e37c4e1359 | loose | driver |
| scf.in | 5011 | 9256b860b0faa3f4 | loose | pw_in |
| scf.out | 138569 | 090418822f882c3f | loose | pw_out |
| steps.sh | 27 | a7d5ef8aefb09efb | loose | steps |

Tarball `nc_pbe_slab1_e80_results.tar.gz` (21425 B, sha256 b3e2dc4c5b6dc27f): 4 members; identical to the loose copy: 4; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0

## Resources and run history

- `nc_pbe_slab1_e80_driver.log`: host b9pgpun003.cern.ch, 11 CPUs, wall limit 86400 s, GPU: 1 GPU(s), NVIDIA H100 NVL, 95830 MiB, job total 380 s, start 2026-09-30T17:28:25Z
  - step scf: -nk 1, max_seconds 84580, start 2026-09-30T17:28:45Z, end 2026-09-30T17:34:45Z, rc 0, PWSCF        :   5m32.35s CPU   5m42.20s WALL
- HTCondor nc_pbe_slab1_e80 12790233.3: 11 CPUs, 1 GPU; seen 2026-09-30T16:47:32Z to 2026-09-30T17:32:55Z (5 samples); states {'1': 4, '2': 1} (1 idle, 2 running, 3 removed, 5 held); max scf_it 27, max BFGS 0; steps ['scf']; hw ['1xNVIDIA H100 NVL|49%'] ['Intel(R) Xeon(R) Platinum 8468']
- `steps.sh`: `steps() { run_pw scf 1 }`

## Calculation `scf.out` (scf/relax)

QE v.7.3.1 started 30Sep2026 19:28:46; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 261411.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled; GPU used by master process:. Completed: JOB DONE; terminated 19:34:28  30Sep2026; PWSCF time {'cpu': '5m32.35s', 'wall': '5m42.20s', 'calls': None}; output lines 2337.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = nc, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 84580
- &SYSTEM: ibrav = 0, nat = 96, ntyp = 3, ecutwfc = 80, ecutrho = 320, occupations = fixed, nbnd = 328
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.3, electron_maxstep = 150, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In_ONCV_PBE-1.2.upf"}, {"species": "O", "mass": 15.999, "pseudo": "O_ONCV_PBE-1.2.upf"}, {"species": "H", "mass": 1.008, "pseudo": "H_ONCV_PBE-1.2.upf"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.33643106, 0.0, 0.0], [0.0, 10.33450421, 0.0], [0.0, 0.0, 34.87453893]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 96, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.5330  a.u.; unit-cell volume = 25140.0035 (a.u.)^3; number of atoms/cell = 96; number of atomic types = 3; number of electrons = 624.00; number of Kohn-Sham states = 328; kinetic-energy cutoff = 80.0000  Ry; charge density cutoff = 320.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.3000; number of iterations used = 8  local-TF  mixing; Exchange-correlation = PBE; celldm = [19.533024, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In_ONCV_PBE-1.2.upf md5 2123f823f6143602c63cd302e3a0bdd6 (Norm-conserving, Z 13.0); O O_ONCV_PBE-1.2.upf md5 e36c48deb68f4e355fffe4602be2c42c (Norm-conserving, Z 6.0); H H_ONCV_PBE-1.2.upf md5 bf21e08b90ac4ce7d0149ac4e8138190 (Norm-conserving, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  2430543 G-vectors     FFT dimensions: ( 120, 120, 375) / None
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '12.25 GB', 'Estimated max dynamical RAM per process': '18.79 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     621.3932, renormalised to     624.0000', 'Starting wfcs are random']

**Convergence** (1 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 34 | 3e-10 | -4073.90318614 |  | 0.005059 | 0.00231 | 0.039255 | 3.7e-05 | -2.66 |  |  |  |

**Final energies** (last SCF): negative_rho = [6.06e-06, 0.0], HOMO_eV = -2.1683, LUMO_eV = -0.3615, E_Ry = -4073.90318614, acc_final_Ry = 3e-10, one_electron_Ry = -78516.91654175, hartree_Ry = 39464.77124179, xc_Ry = -692.51498705, ewald_Ry = 35670.75710087, converged_iterations = 34
- stress tensor (kbar): [[-2.29, 0.0, 0.0], [0.0, -2.44, 0.0], [0.0, 0.0, -3.26]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 328, "n_occ": 312, "VBM_eV": -2.1683, "VBM_k_index": 0, "CBM_eV": -0.3615, "CBM_k_index": 0, "gap_eV": 1.8068, "direct_gap_min_eV": 1.8068, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.0269, "CB_width_bottom_band_eV": 0.8561, "E2_minus_E1_at_k0_eV": 1.4962}

**Warnings/errors**: message_from_routine x1 (first: line 26 'Message from routine setup:'); warning x3 (first: line 2334 'Warning: ieee_invalid is signaling'); c_bands_not_converged x2 (first: line 643 'c_bands:  1 eigenvalues not converged'); ieee x3 (first: line 2334 'Warning: ieee_invalid is signaling'); discouraged x1 (first: line 27 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); fortran_stop x1 (first: line 2337 'FORTRAN STOP')
- messages: ['Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `scf.in`: {"n_atoms": 96, "composition": {"H": 24, "In": 24, "O": 48}, "cell_lengths_A": [10.33643, 10.3345, 34.87454], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3725.3642, "density_g_cm3": 1.5814, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 144, "min": 2.1647, "mean": 2.219, "max": 2.3078, "std": 0.0389, "CN_In_hist": {"6": 24}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9719, "mean": 0.9775, "max": 0.9864, "std": 0.0064, "CN_O_hist": {"0": 24, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 24}, "slab": {"vacuum_A": 25.571, "extent_A": 9.303, "thickness_H_H_A": 9.3033, "thickness_O_O_A": 7.8762, "thickness_In_In_A": 5.1515}}

## Other files

- `.fetched`: ''

## Checks against RESULTS_LOG

| quantity | re-derived | logged | reference | status |
|---|---|---|---|---|
| gap on SCF grid (eV) | 1.8068 | 1.8068 | RESULTS_LOG.md:599 | match |
