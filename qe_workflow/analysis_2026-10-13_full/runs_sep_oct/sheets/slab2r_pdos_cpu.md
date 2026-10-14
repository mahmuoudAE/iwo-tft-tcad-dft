# slab2r_pdos_cpu

**Purpose.** CPU SCF + planar average + projwfc of the relaxed 2 nm slab (surface-state check).

Folder `cern_htcondor/results/slab2r_pdos_cpu`; data `runs_sep_oct/out/slab2r_pdos_cpu.json` (+ `slab2r_pdos_cpu_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| avg_slab2r_pdos_cpu.in | 41 | cedbc90f53ecbf5a | loose | avg_in |
| avg_slab2r_pdos_cpu.out | 1736 | 58cf5a136e53fc96 | loose | avg_out |
| pp_slab2r_pdos_cpu.in | 96 | a5eef7cab6c354e0 | loose | post_in |
| pp_slab2r_pdos_cpu.out | 2366 | 260a328c34ed76db | loose | pp_out |
| projwfc_slab2r_pdos_cpu.in | 158 | fd0942b726a1f61d | loose | post_in |
| projwfc_slab2r_pdos_cpu.out | 8592328 | e2c9a8867c49f472 | loose | projwfc_out |
| scf.in | 8642 | 62dfca67b9e9ae24 | loose | pw_in |
| scf.out | 244023 | b49ea4946a0a134c | loose | pw_out |
| slab2r_pdos_cpu_avg.dat | 138000 | 0b37debc1a7afb03 | loose | avg_dat |
| slab2r_pdos_cpu_driver.log | 534 | 56eeb97c680bc5d5 | loose | driver |
| steps.sh | 129 | 53001cc9bd5598e3 | loose | steps |

Tarball `slab2r_pdos_cpu_results.tar.gz` (5936791 B, sha256 24fa32a929bcee57): 396 members; identical to the loose copy: 11; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 385

PDOS set `pdos`: 385 files.

## Resources and run history

- `slab2r_pdos_cpu_driver.log`: host b9p04p4241.cern.ch, 24 CPUs, wall limit 86400 s, GPU: none (CPU), job total 38656 s, start 2026-10-05T07:35:30Z
  - step scf: -nk 2, max_seconds 84590, start 2026-10-05T07:35:40Z, end 2026-10-05T18:16:47Z, rc 0, PWSCF        :     10h23m CPU     10h41m WALL
  - log: [2026-10-05T18:17:25Z] planar average slab2r_pdos_cpu: 3000 lines
  - log: [2026-10-05T18:19:44Z] pdos slab2r_pdos_cpu: 385 files
- HTCondor slab2r_pdos_cpu 12834125.0: 24 CPUs, 0 GPU; seen 2026-10-05T07:35:29Z to 2026-10-05T18:15:25Z (89 samples); states {'2': 89} (1 idle, 2 running, 3 removed, 5 held); max scf_it 76, max BFGS 0; steps ['scf']; hw [''] ['', 'AMD EPYC 7543 32-Core Processor']
- `steps.sh`: `steps() { run_pw scf 2 || return 0 run_ppavg slab "$JOB" 4.8745 run_pdos slab "$JOB" "$(python qeio.py fermi scf.out)" 2 }`

## Calculation `scf.out` (scf/relax)

QE v.7.5 started 5Oct2026 9:35:41; 24 MPI x 1 threads on 1 node(s); pools 2; R&G division 12; node memory 217250.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: JOB DONE; terminated 20:16:44   5Oct2026; PWSCF time {'cpu': '10h23m', 'wall': '10h41m', 'calls': None}; output lines 4070.

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
| 0 | 76 | 4.3e-10 | -27035.66492227 |  | 0.0008631 | 0.000311 | 0.007155 | 9.8e-05 | -0.45 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.002107, 0.0], HOMO_eV = 0.0475, LUMO_eV = 1.2713, E_Ry = -27035.66492227, E_all_electron_Ry = -673235.702639, acc_final_Ry = 4.3e-10, one_electron_Ry = -272838.06894029, hartree_Ry = 137216.08086297, xc_Ry = -3329.72164898, ewald_Ry = 128104.25312711, paw_one_center_Ry = -16188.20832307, converged_iterations = 76
- stress tensor (kbar): [[0.05, 0.0, 0.0], [0.0, 0.12, 0.0], [0.0, 0.0, -1.51]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 680, "n_occ": 664, "VBM_eV": 0.0475, "VBM_k_index": 0, "CBM_eV": 1.2713, "CBM_k_index": 0, "gap_eV": 1.2238, "direct_gap_min_eV": 1.2238, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.0136, "CB_width_bottom_band_eV": 1.0517, "E2_minus_E1_at_k0_eV": 0.7192}

**Warnings/errors**: message_from_routine x1 (first: line 29 'Message from routine setup:'); c_bands_not_converged x2 (first: line 882 'c_bands:  1 eigenvalues not converged'); ieee x12 (first: line 4059 'Note: The following floating-point exceptions are signalling: IEEE_UNDERFLOW_FLAG IEEE_DEN'); discouraged x1 (first: line 30 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `scf.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 56, "O": 96}, "cell_lengths_A": [10.31792, 10.30849, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5089, "density_g_cm3": 2.7609, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 336, "min": 2.1616, "mean": 2.2197, "max": 2.3007, "std": 0.0357, "CN_In_hist": {"6": 56}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9722, "mean": 0.9773, "max": 0.9858, "std": 0.0061, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.557, "extent_A": 19.623, "thickness_H_H_A": 19.6233, "thickness_O_O_A": 18.2137, "thickness_In_In_A": 15.4861}}

## projwfc `projwfc_slab2r_pdos_cpu.out`

natomwfc 912, nbnd 680, nkstot 4, states 912, spilling 0.0031, Loewdin total 1323.841, PROJWFC      :   2m 2.85s CPU   2m17.37s WALL, done True

| element | n | total charge mean (min-max) | s | p | d |
|---|---|---|---|---|---|
| In | 56 | 11.8537 (11.8264-11.8662) | 0.7005 | 1.1621 | 9.9911 |
| O | 96 | 6.7228 (6.6995-6.7339) | 1.7269 | 4.9958 | 0.0 |
| H | 24 | 0.6105 (0.6017-0.6192) | 0.6105 | 0.0 | 0.0 |

## PDOS `pdos`

{"n_files": 385, "E_window_eV": [-7.952, 4.058], "dE_eV": 0.01, "integral_dos_window": 591.738, "integral_dos_below_EF_or_VBM": 570.273, "reference_energy_eV": 0.0475}

| element, l | files | states in window | states below reference |
|---|---|---|---|
| H s | 24 | 7.817 | 7.33 |
| In d | 56 | 8.636 | 8.483 |
| In p | 56 | 44.129 | 41.689 |
| In s | 56 | 38.867 | 33.47 |
| O p | 96 | 474.122 | 464.278 |
| O s | 96 | 14.328 | 11.568 |

## Planar average `slab2r_pdos_cpu_avg.dat`

{"n_points": 3000, "V_min_eV": -7.9484, "V_max_eV": 5.7663, "window_A": 0.01506, "z_mean_V_eV": 1.71003, "E_vac_eV": 5.7663, "vacuum_flatness_meV": 0.019, "vacuum_slope_meV_per_A": 0.0001, "IP_eV": 5.7188, "EA_eV": 4.495}
- `avg_slab2r_pdos_cpu.in` input: `1 slab2r_pdos_cpu_v.pp 1.0 3000 3 4.8745`
- `pp_slab2r_pdos_cpu.in` input: `&INPUTPP prefix = 'slab', outdir = './tmp', filplot = 'slab2r_pdos_cpu_v.pp', plot_num = 11 /`
- `projwfc_slab2r_pdos_cpu.in` input: `&PROJWFC prefix = 'slab', outdir = './tmp', filpdos = 'pdos/slab2r_pdos_cpu' Emin = -7.9525, Emax = 4.0475, DeltaE = 0.01, degauss = 0.0073, ngauss = 0 /`
- `avg_slab2r_pdos_cpu.out`: done True; Program AVERAGE v.7.5 starts on  5Oct2026 at 20:17:17 / Reading header from file  slab2r_pdos_cpu_v.pp / Reading data from file  slab2r_pdos_cpu_v.pp / AVERAGE      :      7.82s CPU      8.04s WALL / This run was terminated on:  20:17:25   5Oct2026
- `pp_slab2r_pdos_cpu.out`: done True; Program POST-PROC v.7.5 starts on  5Oct2026 at 20:16:48 / Reading xml data from directory: / Calling punch_plot, plot_num =  11 / Writing data to file  slab2r_pdos_cpu_v.pp / POST-PROC    :     25.70s CPU     27.32s WALL

## Other files

- `.fetched`: ''

## Checks against RESULTS_LOG

| quantity | re-derived | logged | reference | status |
|---|---|---|---|---|
| CPUs (driver) | 24 | 24 | RESULTS_LOG.md:459 | match |
| pools | 2 | 2 | RESULTS_LOG.md:459 | match |
| SCF wall (h) | 10.683 | 10.683333333333334 | RESULTS_LOG.md:459 | match |
