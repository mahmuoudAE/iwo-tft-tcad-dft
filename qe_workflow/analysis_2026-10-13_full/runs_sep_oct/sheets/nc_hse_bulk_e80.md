# nc_hse_bulk_e80

**Purpose.** HSE06 bulk single point (NC, 80 Ry, EXX q 1x1x1, default ecutfock).

Folder `cern_htcondor/results/nc_hse_bulk_e80`; data `runs_sep_oct/out/nc_hse_bulk_e80.json` (+ `nc_hse_bulk_e80_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| nc_hse_bulk_e80_driver.log | 482 | aa689e482feea797 | loose | driver |
| scf.in | 2487 | 6186d16d504f0a24 | loose | pw_in |
| scf.out | 199180 | 1d223a06d3c08c87 | loose | pw_out |
| steps.sh | 27 | a7d5ef8aefb09efb | loose | steps |

Tarball `nc_hse_bulk_e80_results.tar.gz` (24458 B, sha256 051826e056f8dcfc): 4 members; identical to the loose copy: 4; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0

## Resources and run history

- `nc_hse_bulk_e80_driver.log`: host b9pgpun501.cern.ch, 11 CPUs, wall limit 86400 s, GPU: 1 GPU(s), NVIDIA H100 NVL, 95830 MiB, job total 2239 s, start 2026-09-30T16:50:36Z
  - step scf: -nk 1, max_seconds 84581, start 2026-09-30T16:50:55Z, end 2026-09-30T17:27:55Z, rc 0, PWSCF        :  36m21.00s CPU  36m41.44s WALL
- HTCondor nc_hse_bulk_e80 12790233.2: 11 CPUs, 1 GPU; seen 2026-09-30T16:47:32Z to 2026-09-30T17:27:16Z (4 samples); states {'1': 1, '2': 3} (1 idle, 2 running, 3 removed, 5 held); max scf_it 44, max BFGS 0; steps ['scf']; hw ['1xNVIDIA H100 NVL|0%'] ['Intel(R) Xeon(R) Platinum 8468']
- `steps.sh`: `steps() { run_pw scf 1 }`

## Calculation `scf.out` (scf/relax)

QE v.7.3.1 started 30Sep2026 18:50:57; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 95516.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled; GPU used by master process:. Completed: JOB DONE; terminated 19:27:38  30Sep2026; PWSCF time {'cpu': '36m21.00s', 'wall': '36m41.44s', 'calls': None}; output lines 3431.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = nc, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 84581
- &SYSTEM: ibrav = 0, nat = 40, ntyp = 2, ecutwfc = 80, ecutrho = 320, occupations = fixed, nbnd = 192, input_dft = hse, nqx1 = 1, nqx2 = 1, nqx3 = 1
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.3, electron_maxstep = 150
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In_ONCV_PBE-1.2.upf"}, {"species": "O", "mass": 15.999, "pseudo": "O_ONCV_PBE-1.2.upf"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[-5.1530451, 5.1530451, 5.1530451], [5.1530451, -5.1530451, 5.1530451], [5.1530451, 5.1530451, -5.1530451]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "3", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 40, "labels": ["In", "O"], "n_constrained": 0}
- Echoed parameters: Exchange-correlation = HSE; EXX-fraction = 0.25; EXX q-point mesh = q-point mesh:     1    1    1; bravais-lattice index = 0; lattice parameter (alat) = 16.8664  a.u.; unit-cell volume = 3693.5878 (a.u.)^3; number of atoms/cell = 40; number of atomic types = 2; number of electrons = 352.00; number of Kohn-Sham states = 192; kinetic-energy cutoff = 80.0000  Ry; charge density cutoff = 320.0000  Ry; cutoff for Fock operator = 320.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.3000; number of iterations used = 8  plain     mixing; celldm = [16.86644, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In_ONCV_PBE-1.2.upf md5 2123f823f6143602c63cd302e3a0bdd6 (Norm-conserving, Z 13.0); O O_ONCV_PBE-1.2.upf md5 e36c48deb68f4e355fffe4602be2c42c (Norm-conserving, Z 6.0)
- Symmetry: 24 Sym. Ops., with inversion, found (18 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:   356799 G-vectors     FFT dimensions: ( 100, 100, 100) / None
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '9.82 GB', 'Estimated max dynamical RAM per process': '10.43 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     350.3039, renormalised to     352.0000', 'Starting wfcs are random']
- HSE/EXX: 6 outer cycles, dexx trace [0.00699193, 8.2e-05, 1.8e-06, 6e-08, 2.6e-09, 1.2e-10], Fock energy trace (Ry) [-70.16379604, -70.17182071, -70.17341468, -70.17368092, -70.17373627, -70.17373322], reached True, EXX grid:   356799 G-vectors     FFT dimensions: ( 100, 100, 100)

**Convergence** (7 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 13 | 4e-10 | -2441.24253197 |  |  |  |  |  |  |  |  |  |
| 1 | 11 | 2.9e-11 | -2430.30017071 |  |  |  |  |  |  |  |  |  |
| 2 | 8 | 2e-10 | -2430.3078489 |  |  |  |  |  |  |  |  |  |
| 3 | 5 | 5.9e-10 | -2430.30794235 |  |  |  |  |  |  |  |  |  |
| 4 | 4 | 2.5e-11 | -2430.30794446 |  |  |  |  |  |  |  |  |  |
| 5 | 2 | 5.4e-10 | -2430.30794453 |  |  |  |  |  |  |  |  |  |
| 6 | 1 | 6.6e-11 | -2430.30794454 |  | 0.003637 | 0.00213 | 0.023364 | 1.3e-05 | 21.73 |  |  |  |

**Final energies** (last SCF): HOMO_eV = 7.8856, LUMO_eV = 9.9936, E_Ry = -2430.30794454, acc_final_Ry = 6.6e-11, converged_iterations = 1, E_bang2_Ry = -2430.30794454, dexx_Ry = 1.2e-10, half_fock_Ry = 140.34746949, fock2_Ry = -70.17373322
- stress tensor (kbar): [[21.73, 0.0, -0.0], [0.0, 21.73, -0.0], [-0.0, 0.0, 21.73]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 192, "n_occ": 176, "VBM_eV": 7.8856, "VBM_k_index": 0, "CBM_eV": 9.9936, "CBM_k_index": 0, "gap_eV": 2.108, "direct_gap_min_eV": 2.108, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.1181, "CB_width_bottom_band_eV": 2.4848, "E2_minus_E1_at_k0_eV": 4.4974}

**Warnings/errors**: message_from_routine x1 (first: line 34 'Message from routine setup:'); warning x4 (first: line 3427 'Warning: ieee_invalid is signaling'); ieee x4 (first: line 3427 'Warning: ieee_invalid is signaling'); discouraged x1 (first: line 35 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); fortran_stop x1 (first: line 3431 'FORTRAN STOP')
- messages: ['Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `scf.in`: {"n_atoms": 40, "composition": {"In": 16, "O": 24}, "cell_lengths_A": [8.92534, 8.92534, 8.92534], "cell_angles_deg": [109.471, 109.471, 109.471], "volume_A3": 547.3332, "density_g_cm3": 6.7384, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 96, "min": 2.1671, "mean": 2.2194, "max": 2.2561, "std": 0.0336, "CN_In_hist": {"6": 16}}}, "CN_O_by_cations_hist": {"4": 24}}

## Other files

- `.fetched`: ''

## Checks against RESULTS_LOG

| quantity | re-derived | logged | reference | status |
|---|---|---|---|---|
| HSE gap on SCF grid (eV) | 2.108 | 2.108 | RESULTS_LOG.md:600 | match |
