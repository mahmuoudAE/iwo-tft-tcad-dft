# nc_pbe_bulk_e80

**Purpose.** Norm-conserving (SG15) PBE single point of bulk In2O3 at the PAW-PBE geometry, 80 Ry (HSE reference).

Folder `cern_htcondor/results/nc_pbe_bulk_e80`; data `runs_sep_oct/out/nc_pbe_bulk_e80.json` (+ `nc_pbe_bulk_e80_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| nc_pbe_bulk_e80_driver.log | 480 | 54877a6114e68f67 | loose | driver |
| scf.in | 2437 | c1f964450d6eac49 | loose | pw_in |
| scf.out | 78716 | baf9dab4c6a599bf | loose | pw_out |
| steps.sh | 27 | a7d5ef8aefb09efb | loose | steps |

Tarball `nc_pbe_bulk_e80_results.tar.gz` (12406 B, sha256 f5709353fdfd3de0): 4 members; identical to the loose copy: 4; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0

## Resources and run history

- `nc_pbe_bulk_e80_driver.log`: host b9pgpun501.cern.ch, 11 CPUs, wall limit 28800 s, GPU: 1 GPU(s), NVIDIA H100 NVL, 95830 MiB, job total 81 s, start 2026-09-30T16:47:53Z
  - step scf: -nk 1, max_seconds 26980, start 2026-09-30T16:48:13Z, end 2026-09-30T16:49:13Z, rc 0, PWSCF        :     16.09s CPU     17.68s WALL
- HTCondor nc_pbe_bulk_e80 12790233.0: 11 CPUs, 1 GPU; seen 2026-09-30T16:47:32Z to 2026-09-30T16:47:32Z (1 samples); states {'1': 1} (1 idle, 2 running, 3 removed, 5 held); max scf_it 0, max BFGS 0; steps []; hw  
- `steps.sh`: `steps() { run_pw scf 1 }`

## Calculation `scf.out` (scf/relax)

QE v.7.3.1 started 30Sep2026 18:48:15; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 96171.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled; GPU used by master process:. Completed: JOB DONE; terminated 18:48:33  30Sep2026; PWSCF time {'cpu': '16.09s', 'wall': '17.68s', 'calls': None}; output lines 1419.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = nc, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 26980
- &SYSTEM: ibrav = 0, nat = 40, ntyp = 2, ecutwfc = 80, ecutrho = 320, occupations = fixed, nbnd = 192
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.3, electron_maxstep = 150
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In_ONCV_PBE-1.2.upf"}, {"species": "O", "mass": 15.999, "pseudo": "O_ONCV_PBE-1.2.upf"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[-5.1530451, 5.1530451, 5.1530451], [5.1530451, -5.1530451, 5.1530451], [5.1530451, 5.1530451, -5.1530451]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "3", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 40, "labels": ["In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 16.8664  a.u.; unit-cell volume = 3693.5878 (a.u.)^3; number of atoms/cell = 40; number of atomic types = 2; number of electrons = 352.00; number of Kohn-Sham states = 192; kinetic-energy cutoff = 80.0000  Ry; charge density cutoff = 320.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.3000; number of iterations used = 8  plain     mixing; Exchange-correlation = PBE; celldm = [16.86644, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In_ONCV_PBE-1.2.upf md5 2123f823f6143602c63cd302e3a0bdd6 (Norm-conserving, Z 13.0); O O_ONCV_PBE-1.2.upf md5 e36c48deb68f4e355fffe4602be2c42c (Norm-conserving, Z 6.0)
- Symmetry: 24 Sym. Ops., with inversion, found (18 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:   356799 G-vectors     FFT dimensions: ( 100, 100, 100) / None
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '1.10 GB', 'Estimated max dynamical RAM per process': '1.70 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     350.3039, renormalised to     352.0000', 'Starting wfcs are random']

**Convergence** (1 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 13 | 4e-10 | -2441.24253197 |  | 0.0003349 | 0.000188 | 0.002058 | 5e-06 | -6.99 |  |  |  |

**Final energies** (last SCF): HOMO_eV = 8.9005, LUMO_eV = 9.8209, E_Ry = -2441.24253197, acc_final_Ry = 4e-10, one_electron_Ry = -583.17212411, hartree_Ry = 550.73876174, xc_Ry = -394.06199352, ewald_Ry = -2014.74717608, converged_iterations = 13
- stress tensor (kbar): [[-6.99, -0.0, -0.0], [-0.0, -6.99, -0.0], [-0.0, -0.0, -6.99]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 192, "n_occ": 176, "VBM_eV": 8.9005, "VBM_k_index": 1, "CBM_eV": 9.8209, "CBM_k_index": 0, "gap_eV": 0.9204, "direct_gap_min_eV": 0.9216, "direct_gap_k_index": 0, "gap_type": "indirect", "VB_width_top_band_eV": 0.1166, "CB_width_bottom_band_eV": 2.4525, "E2_minus_E1_at_k0_eV": 4.263}

**Warnings/errors**: message_from_routine x1 (first: line 26 'Message from routine setup:'); warning x3 (first: line 1416 'Warning: ieee_invalid is signaling'); ieee x3 (first: line 1416 'Warning: ieee_invalid is signaling'); discouraged x1 (first: line 27 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); fortran_stop x1 (first: line 1419 'FORTRAN STOP')
- messages: ['Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `scf.in`: {"n_atoms": 40, "composition": {"In": 16, "O": 24}, "cell_lengths_A": [8.92534, 8.92534, 8.92534], "cell_angles_deg": [109.471, 109.471, 109.471], "volume_A3": 547.3332, "density_g_cm3": 6.7384, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 96, "min": 2.1671, "mean": 2.2194, "max": 2.2561, "std": 0.0336, "CN_In_hist": {"6": 16}}}, "CN_O_by_cations_hist": {"4": 24}}

## Other files

- `.fetched`: ''

## Checks against RESULTS_LOG

| quantity | re-derived | logged | reference | status |
|---|---|---|---|---|
| gap on SCF grid (eV) | 0.9204 | 0.9204 | RESULTS_LOG.md:599 | match |
