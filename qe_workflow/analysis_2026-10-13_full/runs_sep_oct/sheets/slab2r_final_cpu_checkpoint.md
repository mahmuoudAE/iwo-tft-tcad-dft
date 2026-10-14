# slab2r_final_cpu_checkpoint

**Purpose.** CPU cross-check SCF of the relaxed 2 nm slab with planar average; its bands step was held for memory.

Folder `cern_htcondor/results/slab2r_final_cpu_checkpoint`; data `runs_sep_oct/out/slab2r_final_cpu_checkpoint.json` (+ `slab2r_final_cpu_checkpoint_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| avg_slab2r_final_cpu.in | 42 | 4b9100260b55383a | loose | avg_in |
| avg_slab2r_final_cpu.out | 1309 | 719dbef0089b19b2 | loose | avg_out |
| bands.in | 9450 | 3053c8949a5f2551 | loose | pw_in |
| pp_slab2r_final_cpu.in | 97 | 65409a62afe48642 | loose | post_in |
| pp_slab2r_final_cpu.out | 2368 | 462646d445b93c72 | loose | pp_out |
| scf.in | 8642 | 62dfca67b9e9ae24 | loose | pw_in |
| scf.out | 240033 | f0024e861835313c | loose | pw_out |
| slab2r_final_cpu_avg.dat | 138000 | 2c921d498e4c1e03 | loose | avg_dat |
| slab2r_final_cpu_driver.log | 427 | 4d8f8576480663dd | loose | driver |
| steps.sh | 87 | a50950b8eb0dfcd8 | loose | steps |

Tarball `slab2r_final_cpu_12827176.tar.gz` (85119 B, sha256 f94914ae121e0a0d): 10 members; identical to the loose copy: 10; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0

## Resources and run history

- `slab2r_final_cpu_driver.log`: host b9p12p6312.cern.ch, 24 CPUs, wall limit 86400 s, GPU: none (CPU), job total None s, start 2026-10-04T13:35:02Z
  - step scf: -nk 2, max_seconds 84590, start 2026-10-04T13:35:12Z, end 2026-10-04T23:33:18Z, rc 0, PWSCF        :      9h36m CPU      9h57m WALL
  - log: [2026-10-04T23:33:52Z] planar average slab2r_final_cpu: 3000 lines
- HTCondor slab2r_final_cpu 12827176.0: 24 CPUs, 0 GPU; seen 2026-10-04T13:39:30Z to 2026-10-05T07:29:53Z (192 samples); states {'2': 108, '5': 84} (1 idle, 2 running, 3 removed, 5 held); max scf_it 70, max BFGS 0; steps ['scf', 'bands']; hw  ['AMD EPYC 7543 32-Core Processor']
- `steps.sh`: `steps() { run_pw scf 2 || return 0 run_ppavg slab "$JOB" 4.8745 run_pw bands 4 }`

## Calculation `scf.out` (scf/relax)

QE v.7.5 started 4Oct2026 15:35:13; 24 MPI x 1 threads on 1 node(s); pools 2; R&G division 12; node memory 159756.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: JOB DONE; terminated 1:32:58   5Oct2026; PWSCF time {'cpu': '9h36m', 'wall': '9h57m', 'calls': None}; output lines 3968.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 84590
- &SYSTEM: ibrav = 0, nat = 176, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 680
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.31791632, 0.0, 0.0], [0.0, 10.30849134, 0.0], [0.0, 0.0, 45.18062913]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 176, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4980  a.u.; unit-cell volume = 32429.1815 (a.u.)^3; number of atoms/cell = 176; number of atomic types = 3; number of electrons = 1328.00; number of Kohn-Sham states = 680; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.498036, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  7413139 G-vectors     FFT dimensions: ( 150, 150, 648) / Smooth grid:  2620949 G-vectors     FFT dimensions: ( 108, 108, 480)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '1.80 GB', 'Estimated max dynamical RAM per process': '4.12 GB', 'Estimated total dynamical RAM': '97.14 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge    1327.7914, renormalised to    1328.0000', 'Starting wfcs are  912 randomized atomic wfcs']

**Convergence** (1 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 70 | 9e-10 | -27035.66492226 |  | 0.0008655 | 0.000311 | 0.007157 | 0.000137 | -0.4 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.002107, 0.0], HOMO_eV = 0.0474, LUMO_eV = 1.2713, E_Ry = -27035.66492226, E_all_electron_Ry = -673235.702639, acc_final_Ry = 9e-10, one_electron_Ry = -272838.08063455, hartree_Ry = 137216.09268132, xc_Ry = -3329.72172797, ewald_Ry = 128104.25312711, paw_one_center_Ry = -16188.20836817, converged_iterations = 70
- stress tensor (kbar): [[0.1, 0.0, 0.0], [0.0, 0.16, 0.0], [0.0, 0.0, -1.46]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 680, "n_occ": 664, "VBM_eV": 0.0474, "VBM_k_index": 0, "CBM_eV": 1.2713, "CBM_k_index": 0, "gap_eV": 1.2239, "direct_gap_min_eV": 1.2239, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.0136, "CB_width_bottom_band_eV": 1.0516, "E2_minus_E1_at_k0_eV": 0.7191}

**Warnings/errors**: message_from_routine x1 (first: line 29 'Message from routine setup:'); c_bands_not_converged x2 (first: line 831 'c_bands:  1 eigenvalues not converged'); ieee x12 (first: line 3957 'Note: The following floating-point exceptions are signalling: IEEE_UNDERFLOW_FLAG IEEE_DEN'); discouraged x1 (first: line 30 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `bands.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 56, "O": 96}, "cell_lengths_A": [10.31792, 10.30849, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5089, "density_g_cm3": 2.7609, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 336, "min": 2.1616, "mean": 2.2197, "max": 2.3007, "std": 0.0357, "CN_In_hist": {"6": 56}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9722, "mean": 0.9773, "max": 0.9858, "std": 0.0061, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.557, "extent_A": 19.623, "thickness_H_H_A": 19.6233, "thickness_O_O_A": 18.2137, "thickness_In_In_A": 15.4861}}
- `scf.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 56, "O": 96}, "cell_lengths_A": [10.31792, 10.30849, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5089, "density_g_cm3": 2.7609, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 336, "min": 2.1616, "mean": 2.2197, "max": 2.3007, "std": 0.0357, "CN_In_hist": {"6": 56}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9722, "mean": 0.9773, "max": 0.9858, "std": 0.0061, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.557, "extent_A": 19.623, "thickness_H_H_A": 19.6233, "thickness_O_O_A": 18.2137, "thickness_In_In_A": 15.4861}}

## Planar average `slab2r_final_cpu_avg.dat`

{"n_points": 3000, "V_min_eV": -7.9484, "V_max_eV": 5.7662, "window_A": 0.01506, "z_mean_V_eV": 1.71003, "E_vac_eV": 5.76621, "vacuum_flatness_meV": 0.019, "vacuum_slope_meV_per_A": 0.0001, "IP_eV": 5.7188, "EA_eV": 4.4949}
- `avg_slab2r_final_cpu.in` input: `1 slab2r_final_cpu_v.pp 1.0 3000 3 4.8745`
- `pp_slab2r_final_cpu.in` input: `&INPUTPP prefix = 'slab', outdir = './tmp', filplot = 'slab2r_final_cpu_v.pp', plot_num = 11 /`
- `avg_slab2r_final_cpu.out`: done True; Program AVERAGE v.7.5 starts on  5Oct2026 at  1:33:46 / Reading header from file  slab2r_final_cpu_v.pp / Reading data from file  slab2r_final_cpu_v.pp / AVERAGE      :      5.88s CPU      6.01s WALL / This run was terminated on:   1:33:52   5Oct2026
- `pp_slab2r_final_cpu.out`: done True; Program POST-PROC v.7.5 starts on  5Oct2026 at  1:33:19 / Reading xml data from directory: / Calling punch_plot, plot_num =  11 / Writing data to file  slab2r_final_cpu_v.pp / POST-PROC    :     24.25s CPU     25.50s WALL

## Checks against RESULTS_LOG

| quantity | re-derived | logged | reference | status |
|---|---|---|---|---|
| CPUs (driver) | 24 | 24 | RESULTS_LOG.md:540 | match |
| SCF wall (h) | 9.95 | 9.95 | RESULTS_LOG.md:540 | match |
| SCF iterations | 70 | 70 | RESULTS_LOG.md:540 | match |
| HOMO (eV) | 0.0474 | 0.0474 | RESULTS_LOG.md:540 | match |
| LUMO (eV) | 1.2713 | 1.2713 | RESULTS_LOG.md:540 | match |
| CPUs allocated / MPI ranks (driver, HTCondor and pw.x agree on 24; log 410 also says 24; the logged 16 is the request_cpus of cern_htcondor/jobs/gen_iwoslab2/jobs.txt:1, found 2026-10-14) | 24 | 16 | RESULTS_LOG.md:550 | DIFFERS (dated erratum 2026-10-14 in RESULTS_LOG) |
