# nc_pbe_bulk_e100

**Purpose.** NC PBE bulk single point at 100 Ry (cutoff check of the NC set).

Folder `cern_htcondor/results/nc_pbe_bulk_e100`; data `runs_sep_oct/out/nc_pbe_bulk_e100.json` (+ `nc_pbe_bulk_e100_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| nc_pbe_bulk_e100_driver.log | 481 | d8417159348e5ee0 | loose | driver |
| scf.in | 2438 | 4e9f20cabce53c32 | loose | pw_in |
| scf.out | 77905 | cccb5f48f732be0f | loose | pw_out |
| steps.sh | 27 | a7d5ef8aefb09efb | loose | steps |

Tarball `nc_pbe_bulk_e100_results.tar.gz` (12357 B, sha256 93be375f42f503d1): 4 members; identical to the loose copy: 4; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0

## Resources and run history

- `nc_pbe_bulk_e100_driver.log`: host b9pgpun501.cern.ch, 11 CPUs, wall limit 28800 s, GPU: 1 GPU(s), NVIDIA H100 NVL, 95830 MiB, job total 80 s, start 2026-09-30T16:46:32Z
  - step scf: -nk 1, max_seconds 26980, start 2026-09-30T16:46:52Z, end 2026-09-30T16:47:52Z, rc 0, PWSCF        :     18.10s CPU     20.05s WALL
- HTCondor nc_pbe_bulk_e100 12790233.1: 11 CPUs, 1 GPU; seen 2026-09-30T16:47:32Z to 2026-09-30T16:47:32Z (1 samples); states {'2': 1} (1 idle, 2 running, 3 removed, 5 held); max scf_it 12, max BFGS 0; steps ['scf']; hw ['1xNVIDIA H100 NVL|0%'] ['Intel(R) Xeon(R) Platinum 8468']
- `steps.sh`: `steps() { run_pw scf 1 }`

## Calculation `scf.out` (scf/relax)

QE v.7.3.1 started 30Sep2026 18:46:53; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 97341.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled; GPU used by master process:. Completed: JOB DONE; terminated 18:47:14  30Sep2026; PWSCF time {'cpu': '18.10s', 'wall': '20.05s', 'calls': None}; output lines 1401.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = nc, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 26980
- &SYSTEM: ibrav = 0, nat = 40, ntyp = 2, ecutwfc = 100, ecutrho = 400, occupations = fixed, nbnd = 192
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.3, electron_maxstep = 150
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In_ONCV_PBE-1.2.upf"}, {"species": "O", "mass": 15.999, "pseudo": "O_ONCV_PBE-1.2.upf"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[-5.1530451, 5.1530451, 5.1530451], [5.1530451, -5.1530451, 5.1530451], [5.1530451, 5.1530451, -5.1530451]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "3", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 40, "labels": ["In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 16.8664  a.u.; unit-cell volume = 3693.5878 (a.u.)^3; number of atoms/cell = 40; number of atomic types = 2; number of electrons = 352.00; number of Kohn-Sham states = 192; kinetic-energy cutoff = 100.0000  Ry; charge density cutoff = 400.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.3000; number of iterations used = 8  plain     mixing; Exchange-correlation = PBE; celldm = [16.86644, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In_ONCV_PBE-1.2.upf md5 2123f823f6143602c63cd302e3a0bdd6 (Norm-conserving, Z 13.0); O O_ONCV_PBE-1.2.upf md5 e36c48deb68f4e355fffe4602be2c42c (Norm-conserving, Z 6.0)
- Symmetry: 24 Sym. Ops., with inversion, found (18 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:   498761 G-vectors     FFT dimensions: ( 108, 108, 108) / None
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '1.52 GB', 'Estimated max dynamical RAM per process': '2.37 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     350.3039, renormalised to     352.0000', 'Starting wfcs are random']

**Convergence** (1 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 12 | 2e-10 | -2441.24853882 |  | 0.0004787 | 0.000283 | 0.003101 | 2.9e-05 | -3.52 |  |  |  |

**Final energies** (last SCF): HOMO_eV = 8.9008, LUMO_eV = 9.8211, E_Ry = -2441.24853882, acc_final_Ry = 2e-10, one_electron_Ry = -583.1882556, hartree_Ry = 550.74994164, xc_Ry = -394.06304879, ewald_Ry = -2014.74717608, converged_iterations = 12
- stress tensor (kbar): [[-3.52, -0.0, -0.0], [-0.0, -3.52, -0.0], [0.0, -0.0, -3.52]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 192, "n_occ": 176, "VBM_eV": 8.9008, "VBM_k_index": 1, "CBM_eV": 9.8211, "CBM_k_index": 0, "gap_eV": 0.9203, "direct_gap_min_eV": 0.9216, "direct_gap_k_index": 0, "gap_type": "indirect", "VB_width_top_band_eV": 0.1166, "CB_width_bottom_band_eV": 2.4524, "E2_minus_E1_at_k0_eV": 4.2626}

**Warnings/errors**: message_from_routine x1 (first: line 26 'Message from routine setup:'); warning x3 (first: line 1398 'Warning: ieee_invalid is signaling'); ieee x3 (first: line 1398 'Warning: ieee_invalid is signaling'); discouraged x1 (first: line 27 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); fortran_stop x1 (first: line 1401 'FORTRAN STOP')
- messages: ['Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `scf.in`: {"n_atoms": 40, "composition": {"In": 16, "O": 24}, "cell_lengths_A": [8.92534, 8.92534, 8.92534], "cell_angles_deg": [109.471, 109.471, 109.471], "volume_A3": 547.3332, "density_g_cm3": 6.7384, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 96, "min": 2.1671, "mean": 2.2194, "max": 2.2561, "std": 0.0336, "CN_In_hist": {"6": 16}}}, "CN_O_by_cations_hist": {"4": 24}}

## Other files

- `.fetched`: ''
