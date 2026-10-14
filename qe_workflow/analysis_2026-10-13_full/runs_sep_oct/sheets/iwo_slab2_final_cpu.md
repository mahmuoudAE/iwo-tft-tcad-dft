# iwo_slab2_final_cpu

**Purpose.** Recovery CPU SCF + planar average + projwfc of the relaxed 2 nm IWO slab (conv_thr 1e-8, beta 0.1).

Folder `cern_htcondor/results/iwo_slab2_final_cpu`; data `runs_sep_oct/out/iwo_slab2_final_cpu.json` (+ `iwo_slab2_final_cpu_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| avg_iwo_slab2_final_cpu.in | 45 | f030d76d3eb50062 | loose | avg_in |
| avg_iwo_slab2_final_cpu.out | 1745 | 0d99ff9a004a0dc2 | loose | avg_out |
| iwo_slab2_final_cpu_avg.dat | 138000 | 8ad91a0cccffdef7 | loose | avg_dat |
| iwo_slab2_final_cpu_driver.log | 546 | c3045ad733448877 | loose | driver |
| pp_iwo_slab2_final_cpu.in | 100 | 9c77790078e78b8f | loose | post_in |
| pp_iwo_slab2_final_cpu.out | 2451 | 9b5a92453b8d97a4 | loose | pp_out |
| projwfc_iwo_slab2_final_cpu.in | 162 | 005d723b12394a5c | loose | post_in |
| projwfc_iwo_slab2_final_cpu.out | 7929909 | 36e60e57a4f1f416 | loose | projwfc_out |
| scf.in | 8721 | e7f85d86451d83e3 | loose | pw_in |
| scf.out | 253493 | 701b3b5179977b42 | loose | pw_out |
| steps.sh | 315 | c5ebe3cc579dbba3 | loose | steps |

Tarball `iwo_slab2_final_cpu_results.tar.gz` (5863524 B, sha256 d429a88b48e01fd8): 398 members; identical to the loose copy: 11; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 387

PDOS set `pdos`: 387 files.

## Resources and run history

- `iwo_slab2_final_cpu_driver.log`: host b9p06p6732.cern.ch, 33 CPUs, wall limit 86400 s, GPU: none (CPU), job total 29327 s, start 2026-10-05T16:22:27Z
  - step scf: -nk 1, max_seconds 84591, start 2026-10-05T16:22:36Z, end 2026-10-06T00:28:42Z, rc 0, PWSCF        :      7h44m CPU      8h 5m WALL
  - log: [2026-10-06T00:29:14Z] planar average iwo_slab2_final_cpu: 3000 lines
  - log: [2026-10-06T00:31:13Z] pdos iwo_slab2_final_cpu: 387 files
- HTCondor iwo_slab2_final_cpu 12835131.0: 33 CPUs, 0 GPU; seen 2026-10-05T12:50:54Z to 2026-10-05T12:50:54Z (1 samples); states {'1': 1} (1 idle, 2 running, 3 removed, 5 held); max scf_it 0, max BFGS 0; steps []; hw  
- HTCondor iwo_slab2_final_cpu 12835211.0: 33 CPUs, 0 GPU; seen 2026-10-05T16:20:34Z to 2026-10-06T00:25:53Z (84 samples); states {'1': 1, '2': 83} (1 idle, 2 running, 3 removed, 5 held); max scf_it 91, max BFGS 0; steps ['scf']; hw  ['AMD EPYC 7543 32-Core Processor']
- `steps.sh`: `steps() { export FORCE_CPU=1 # one QE version (CPU 7.5) for SCF, pp.x and projwfc.x # one pool: CERN allocates CPUs by memory (100 GB -> 33 CPUs), and -nk 2 aborted on 33 ranks (2026-10-05) run_pw scf 1 || return 0 run_ppavg slab "$JOB" 4.8745 run_pdos slab "$JOB" "$(python qeio.py fermi scf.out)" 1 }`

## Calculation `scf.out` (scf/relax)

QE v.7.5 started 5Oct2026 18:22:37; 33 MPI x 1 threads on 1 node(s); pools 1; R&G division 33; node memory 153915.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: JOB DONE; terminated 2:27:54   6Oct2026; PWSCF time {'cpu': '7h44m', 'wall': '8h 5m', 'calls': None}; output lines 4305.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 84591
- &SYSTEM: ibrav = 0, nat = 176, ntyp = 4, ecutwfc = 71, ecutrho = 568, occupations = smearing, smearing = mv, degauss = 0.01, nbnd = 688
- &ELECTRONS: conv_thr = 1.0d-8, mixing_beta = 0.1, electron_maxstep = 200, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "W", "mass": 183.84, "pseudo": "W.pbe-spn-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.3179162589, 0.0, 0.0], [0.0, 10.3084960013, 0.0], [0.0, 0.0, 45.1806282459]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 176, "labels": ["H", "In", "O", "W"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4980  a.u.; unit-cell volume = 32429.1953 (a.u.)^3; number of atoms/cell = 176; number of atomic types = 4; number of electrons = 1329.00; number of Kohn-Sham states = 688; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-08; mixing beta = 0.1000; number of iterations used = 8  local-TF  mixing; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.498036, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); W W.pbe-spn-kjpaw_psl.1.0.0.UPF md5 03c3df5b60893f488392c7401945500a (Projector augmented-wave + core cor, Z 14.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 2 Sym. Ops. (no inversion) found ( 1 have fractional translation); k points: number of k points=     4  Marzari-Vanderbilt smearing, width (Ry)=  0.0100 (sum of weights 2.0); FFT: Dense  grid:  7413147 G-vectors     FFT dimensions: ( 150, 150, 648) / Smooth grid:  2620949 G-vectors     FFT dimensions: ( 108, 108, 480)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '893.93 MB', 'Estimated max dynamical RAM per process': '2.51 GB', 'Estimated total dynamical RAM': '82.78 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge    1328.7946, renormalised to    1329.0000', 'Starting wfcs are  916 randomized atomic wfcs']

**Convergence** (1 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 91 | 9.5e-09 | -27385.20618325 |  | 0.0007972 | 0.000234 | 0.005386 | 0.000174 | 1.8 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.04591, 0.0], E_F_eV = 2.3496, E_Ry = -27385.20618325, E_all_electron_Ry = -693758.168517, acc_final_Ry = 9.5e-09, mTS_Ry = -0.00132166, internal_energy_Ry = -27385.20486159, one_electron_Ry = -272001.03541876, hartree_Ry = 136782.88247112, xc_Ry = -3322.87628641, ewald_Ry = 127677.0099023, paw_one_center_Ry = -16521.18552983, converged_iterations = 91
- stress tensor (kbar): [[2.8, 0.0, 0.21], [0.0, 2.85, 0.0], [0.21, 0.0, -0.26]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 688, "E_F_eV": 2.3496, "bands_fully_below_EF": 664, "bands_crossing_EF_1based": [665], "highest_band_below_EF_max_eV": 2.0847, "lowest_band_above_EF_min_eV": 2.4188}

**Warnings/errors**: message_from_routine x1 (first: line 30 'Message from routine setup:'); c_bands_not_converged x9 (first: line 923 'c_bands:  1 eigenvalues not converged'); ieee x19 (first: line 4287 'Note: The following floating-point exceptions are signalling: IEEE_UNDERFLOW_FLAG IEEE_DEN'); discouraged x1 (first: line 31 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x4 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized']

## Input geometries

- `scf.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 55, "O": 96, "W": 1}, "cell_lengths_A": [10.31792, 10.3085, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5109, "density_g_cm3": 2.7848, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 330, "min": 2.1292, "mean": 2.2283, "max": 2.5046, "std": 0.0617, "CN_In_hist": {"6": 55}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 1.8665, "mean": 1.9767, "max": 2.1897, "std": 0.1506, "CN_W_hist": {"6": 1}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9725, "mean": 0.9779, "max": 0.987, "std": 0.0063, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.458, "extent_A": 19.722, "thickness_H_H_A": 19.7222, "thickness_O_O_A": 18.2838, "thickness_In_In_A": 15.5749, "thickness_W_W_A": 0.0}}

## projwfc `projwfc_iwo_slab2_final_cpu.out`

natomwfc 916, nbnd 688, nkstot 4, states 916, spilling 0.0031, Loewdin total 1324.842, PROJWFC      :   1m49.23s CPU   1m57.24s WALL, done True

| element | n | total charge mean (min-max) | s | p | d |
|---|---|---|---|---|---|
| In | 55 | 11.8686 (11.8356-11.8989) | 0.7215 | 1.1563 | 9.9907 |
| O | 96 | 6.7112 (6.5139-6.7335) | 1.7295 | 4.9817 | 0.0 |
| W | 1 | 13.1006 (13.1006-13.1006) | 2.4301 | 6.9463 | 3.7242 |
| H | 24 | 0.6124 (0.603-0.6216) | 0.6124 | 0.0 | 0.0 |

## PDOS `pdos`

{"n_files": 387, "E_window_eV": [-5.65, 5.35], "dE_eV": 0.01, "integral_dos_window": 618.524, "integral_dos_below_EF_or_VBM": 571.503, "reference_energy_eV": 2.3496}

| element, l | files | states in window | states below reference |
|---|---|---|---|
| H s | 24 | 7.703 | 6.559 |
| In d | 55 | 8.33 | 8.257 |
| In p | 55 | 48.124 | 40.786 |
| In s | 55 | 47.25 | 33.198 |
| O p | 96 | 477.324 | 463.605 |
| O s | 96 | 17.37 | 11.837 |
| W d | 1 | 6.567 | 3.033 |
| W p | 2 | 0.638 | 0.496 |
| W s | 2 | 0.257 | 0.228 |

## Planar average `iwo_slab2_final_cpu_avg.dat`

{"n_points": 3000, "V_min_eV": -8.1097, "V_max_eV": 5.8576, "window_A": 0.01506, "z_mean_V_eV": 1.72031, "E_vac_eV": 5.85757, "vacuum_flatness_meV": 0.029, "vacuum_slope_meV_per_A": 0.0001, "work_function_eV": 3.508}
- `avg_iwo_slab2_final_cpu.in` input: `1 iwo_slab2_final_cpu_v.pp 1.0 3000 3 4.8745`
- `pp_iwo_slab2_final_cpu.in` input: `&INPUTPP prefix = 'slab', outdir = './tmp', filplot = 'iwo_slab2_final_cpu_v.pp', plot_num = 11 /`
- `projwfc_iwo_slab2_final_cpu.in` input: `&PROJWFC prefix = 'slab', outdir = './tmp', filpdos = 'pdos/iwo_slab2_final_cpu' Emin = -5.6504, Emax = 6.3496, DeltaE = 0.01, degauss = 0.0073, ngauss = 0 /`
- `avg_iwo_slab2_final_cpu.out`: done True; Program AVERAGE v.7.5 starts on  6Oct2026 at  2:29: 7 / Reading header from file  iwo_slab2_final_cpu_v.pp / Reading data from file  iwo_slab2_final_cpu_v.pp / AVERAGE      :      6.77s CPU      6.99s WALL / This run was terminated on:   2:29:14   6Oct2026
- `pp_iwo_slab2_final_cpu.out`: done True; Program POST-PROC v.7.5 starts on  6Oct2026 at  2:28:43 / Reading xml data from directory: / Calling punch_plot, plot_num =  11 / Writing data to file  iwo_slab2_final_cpu_v.pp / POST-PROC    :     21.22s CPU     22.43s WALL

## Other files

- `.fetched`: ''

## Checks against RESULTS_LOG

| quantity | re-derived | logged | reference | status |
|---|---|---|---|---|
| HTCondor cluster of the run whose outputs are used (log: 12835131) | 12835211.0 | 12835131.0 | RESULTS_LOG.md:514 | DIFFERS (dated erratum 2026-10-14 in RESULTS_LOG) |
| CPUs allocated | 33 | 33 | RESULTS_LOG.md:514 | match |
| conv_thr (input) | 1e-08 | 1e-08 | RESULTS_LOG.md:515 | match |
| mixing_beta (input) | 0.1 | 0.1 | RESULTS_LOG.md:515 | match |
