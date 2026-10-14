# nc_hse_slab1_f160_e80

**Purpose.** HSE06 1 nm slab, ecutfock 160 Ry (the slab HSE gap used for the ratio).

Folder `cern_htcondor/results/nc_hse_slab1_f160_e80`; data `runs_sep_oct/out/nc_hse_slab1_f160_e80.json` (+ `nc_hse_slab1_f160_e80_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| nc_hse_slab1_f160_e80_driver.log | 491 | 0bc6b8533f9b6a15 | loose | driver |
| scf.in | 5078 | 6c3a7fe28cc8e050 | loose | pw_in |
| scf.out | 367735 | 2a4c19d37763ed14 | loose | pw_out |
| steps.sh | 27 | a7d5ef8aefb09efb | loose | steps |

Tarball `nc_hse_slab1_f160_e80_results.tar.gz` (53014 B, sha256 c54e9fe262cf0e5c): 4 members; identical to the loose copy: 4; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0

## Resources and run history

- `nc_hse_slab1_f160_e80_driver.log`: host b9pgpun002.cern.ch, 11 CPUs, wall limit 259200 s, GPU: 1 GPU(s), NVIDIA H100 NVL, 95830 MiB, job total 14486 s, start 2026-09-30T22:58:45Z
  - step scf: -nk 1, max_seconds 257376, start 2026-09-30T22:59:09Z, end 2026-10-01T03:00:11Z, rc 0, PWSCF        :      3h59m CPU      4h 0m WALL
- HTCondor nc_hse_slab1_f160_e80 12790250.2: 11 CPUs, 1 GPU; seen 2026-09-30T17:44:25Z to 2026-09-30T20:02:28Z (25 samples); states {'1': 25} (1 idle, 2 running, 3 removed, 5 held); max scf_it 0, max BFGS 0; steps []; hw  
- HTCondor nc_hse_slab1_f160_e80 12790499.2: 11 CPUs, 1 GPU; seen 2026-09-30T20:14:01Z to 2026-09-30T20:14:01Z (1 samples); states {'1': 1} (1 idle, 2 running, 3 removed, 5 held); max scf_it 0, max BFGS 0; steps []; hw  
- HTCondor nc_hse_slab1_f160_e80 12790513.2: 11 CPUs, 1 GPU; seen 2026-09-30T20:22:03Z to 2026-10-01T02:56:40Z (71 samples); states {'1': 28, '2': 43} (1 idle, 2 running, 3 removed, 5 held); max scf_it 92, max BFGS 0; steps ['scf']; hw ['1xNVIDIA H100 NVL|0%', '1xNVIDIA H100 NVL|98%', '1xNVIDIA H100 NVL|99%'] ['Intel(R) Xeon(R) Platinum 8468']
- `steps.sh`: `steps() { run_pw scf 1 }`

## Calculation `scf.out` (scf/relax)

QE v.7.3.1 started 1Oct2026 0:59:11; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 310917.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled; GPU used by master process:. Completed: JOB DONE; terminated 4:59:51   1Oct2026; PWSCF time {'cpu': '3h59m', 'wall': '4h 0m', 'calls': None}; output lines 6027.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = nc, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 257376
- &SYSTEM: ibrav = 0, nat = 96, ntyp = 3, ecutwfc = 80, ecutrho = 320, occupations = fixed, nbnd = 328, input_dft = hse, nqx1 = 1, nqx2 = 1, nqx3 = 1, ecutfock = 160
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.3, electron_maxstep = 150, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In_ONCV_PBE-1.2.upf"}, {"species": "O", "mass": 15.999, "pseudo": "O_ONCV_PBE-1.2.upf"}, {"species": "H", "mass": 1.008, "pseudo": "H_ONCV_PBE-1.2.upf"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.33643106, 0.0, 0.0], [0.0, 10.33450421, 0.0], [0.0, 0.0, 34.87453893]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 96, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: Exchange-correlation = HSE; EXX-fraction = 0.25; EXX q-point mesh = q-point mesh:     1    1    1; bravais-lattice index = 0; lattice parameter (alat) = 19.5330  a.u.; unit-cell volume = 25140.0035 (a.u.)^3; number of atoms/cell = 96; number of atomic types = 3; number of electrons = 624.00; number of Kohn-Sham states = 328; kinetic-energy cutoff = 80.0000  Ry; charge density cutoff = 320.0000  Ry; cutoff for Fock operator = 160.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.3000; number of iterations used = 8  local-TF  mixing; celldm = [19.533024, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In_ONCV_PBE-1.2.upf md5 2123f823f6143602c63cd302e3a0bdd6 (Norm-conserving, Z 13.0); O O_ONCV_PBE-1.2.upf md5 e36c48deb68f4e355fffe4602be2c42c (Norm-conserving, Z 6.0); H H_ONCV_PBE-1.2.upf md5 bf21e08b90ac4ce7d0149ac4e8138190 (Norm-conserving, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  2430543 G-vectors     FFT dimensions: ( 120, 120, 375) / None
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '51.89 GB', 'Estimated max dynamical RAM per process': '58.43 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     621.3932, renormalised to     624.0000', 'Starting wfcs are random']
- HSE/EXX: 7 outer cycles, dexx trace [0.01333401, 0.00025321, 8.97e-06, 4.1e-07, 2e-08, 1.4e-09, 1.9e-10], Fock energy trace (Ry) [-126.11869902, -126.14150182, -126.14603117, -126.14696008, -126.14710608, -126.14715403, -126.14718385], reached True, EXX grid:   859245 G-vectors     FFT dimensions: (  80,  80, 270)

**Convergence** (8 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 34 | 3e-10 | -4073.90318614 |  |  |  |  |  |  |  |  |  |
| 1 | 23 | 7.2e-10 | -4057.47346112 |  |  |  |  |  |  |  |  |  |
| 2 | 14 | 4.7e-10 | -4057.48842462 |  |  |  |  |  |  |  |  |  |
| 3 | 9 | 3.4e-10 | -4057.48872348 |  |  |  |  |  |  |  |  |  |
| 4 | 5 | 6.5e-10 | -4057.48873434 |  |  |  |  |  |  |  |  |  |
| 5 | 3 | 7.6e-10 | -4057.48873484 |  |  |  |  |  |  |  |  |  |
| 6 | 3 | 2.6e-10 | -4057.48873487 |  |  |  |  |  |  |  |  |  |
| 7 | 1 | 8.5e-10 | -4057.48873487 |  | 0.0238 | 0.011 | 0.186488 | 0.000195 | 5.1 |  |  |  |

**Final energies** (last SCF): HOMO_eV = -3.1764, LUMO_eV = -0.1289, E_Ry = -4057.48873487, acc_final_Ry = 8.5e-10, converged_iterations = 1, E_bang2_Ry = -4057.48873487, dexx_Ry = 1.9e-10, half_fock_Ry = 252.29433788, fock2_Ry = -126.14718385
- stress tensor (kbar): [[7.12, 0.0, 0.0], [0.0, 6.28, 0.0], [0.0, 0.0, 1.9]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 328, "n_occ": 312, "VBM_eV": -3.1764, "VBM_k_index": 0, "CBM_eV": -0.1289, "CBM_k_index": 0, "gap_eV": 3.0475, "direct_gap_min_eV": 3.0475, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.0241, "CB_width_bottom_band_eV": 0.8648, "E2_minus_E1_at_k0_eV": 1.6049}

**Warnings/errors**: message_from_routine x1 (first: line 34 'Message from routine setup:'); warning x4 (first: line 6023 'Warning: ieee_invalid is signaling'); c_bands_not_converged x2 (first: line 663 'c_bands:  1 eigenvalues not converged'); ieee x4 (first: line 6023 'Warning: ieee_invalid is signaling'); discouraged x1 (first: line 35 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); fortran_stop x1 (first: line 6027 'FORTRAN STOP')
- messages: ['Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `scf.in`: {"n_atoms": 96, "composition": {"H": 24, "In": 24, "O": 48}, "cell_lengths_A": [10.33643, 10.3345, 34.87454], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3725.3642, "density_g_cm3": 1.5814, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 144, "min": 2.1647, "mean": 2.219, "max": 2.3078, "std": 0.0389, "CN_In_hist": {"6": 24}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9719, "mean": 0.9775, "max": 0.9864, "std": 0.0064, "CN_O_hist": {"0": 24, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 24}, "slab": {"vacuum_A": 25.571, "extent_A": 9.303, "thickness_H_H_A": 9.3033, "thickness_O_O_A": 7.8762, "thickness_In_In_A": 5.1515}}

## Other files

- `.fetched`: ''

## Checks against RESULTS_LOG

| quantity | re-derived | logged | reference | status |
|---|---|---|---|---|
| HSE gap on SCF grid (eV) | 3.0475 | 3.0475 | RESULTS_LOG.md:600 | match |
