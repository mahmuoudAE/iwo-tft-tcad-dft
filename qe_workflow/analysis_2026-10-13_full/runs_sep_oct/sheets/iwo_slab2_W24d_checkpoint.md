# iwo_slab2_W24d_checkpoint

**Purpose.** EOS checkpoint of the 2 nm IWO slab relax (one H100 NVL): converged relax.out.

Folder `cern_htcondor/results/iwo_slab2_W24d_checkpoint`; data `runs_sep_oct/out/iwo_slab2_W24d_checkpoint.json` (+ `iwo_slab2_W24d_checkpoint_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| bands.tmpl | 9527 | bc093711ac2b1c6c | loose | pw_tmpl |
| iwo_slab2_W24d_driver.log | 436 | 87cb846e2045aadd | loose | driver |
| relax.in | 8814 | 4dd1e733395b42a0 | loose | pw_in |
| relax.out | 2141372 | fc02251d513f4c03 | loose | pw_out |
| scf.tmpl | 8719 | e810838a68f08402 | loose | pw_tmpl |
| steps.sh | 469 | e8654acaa71abfe3 | loose | steps |

Tarball `iwo_slab2_W24d_12827176.tar.gz` (517795 B, sha256 3c31c0ddb4df34f1): 6 members; identical to the loose copy: 6; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0

## Resources and run history

- `iwo_slab2_W24d_driver.log`: host b9pgpun003.cern.ch, 33 CPUs, wall limit 259200 s, GPU: 1 GPU(s), NVIDIA H100 NVL, 95830 MiB, job total None s, start 2026-10-04T13:52:08Z
  - step relax: -nk 1, max_seconds 257378, start 2026-10-04T13:52:30Z, end 2026-10-05T06:42:35Z, rc 0, PWSCF        :     16h39m CPU     16h49m WALL
- HTCondor iwo_slab2_W24d 12827176.1: 33 CPUs, 1 GPU; seen 2026-10-04T13:39:30Z to 2026-10-05T09:22:51Z (212 samples); states {'1': 3, '2': 209} (1 idle, 2 running, 3 removed, 5 held); max scf_it 1550, max BFGS 27; steps ['relax', 'scf']; hw ['', '1xNVIDIA H100 NVL|0%', '1xNVIDIA H100 NVL|1%', '1xNVIDIA H100 NVL|10%', '1xNVIDIA H100 NVL|100%', '1xNVIDIA H100 NVL|11%', '1xNVIDIA H100 NVL|12%', '1xNVIDIA H100 NVL|13%', '1xNVIDIA H100 NVL|14%', '1xNVIDIA H100 NVL|16%', '1xNVIDIA H100 NVL|17%', '1xNVIDIA H100 NVL|18%', '1xNVIDIA H100 NVL|26%', '1xNVIDIA H100 NVL|4%', '1xNVIDIA H100 NVL|48%', '1xNVIDIA H100 NVL|5%', '1xNVIDIA H100 NVL|57%', '1xNVIDIA H100 NVL|58%', '1xNVIDIA H100 NVL|6%', '1xNVIDIA H100 NVL|60%', '1xNVIDIA H100 NVL|8%', '1xNVIDIA H100 NVL|88%', '1xNVIDIA H100 NVL|9%', '1xNVIDIA H100 NVL|93%', '1xNVIDIA H100 NVL|94%', '1xNVIDIA H100 NVL|95%', '1xNVIDIA H100 NVL|96%', '1xNVIDIA H100 NVL|97%', '1xNVIDIA H100 NVL|98%', '1xNVIDIA H100 NVL|99%'] ['', 'Intel(R) Xeon(R) Platinum 8468']
- `steps.sh`: `steps() { run_pw relax 1 python qeio.py converged relax.out || { log "relaxation did not finish; later steps skipped"; return 0; } for t in scf bands; do python qeio.py newgeom $t.tmpl relax.out > $t.in; done clean_tmp export FORCE_CPU=1 # one QE version (CPU 7.5) for SCF, pp.x and projwfc.x; one pool (NCPU may be odd) run_pw scf 1 || return 0 run_ppavg slab "$JOB" 4.8745 run_pdos slab "$JOB" "$(python qeio.py fermi scf.out)" 1 run_pw bands 1 }`

## Calculation `relax.out` (scf/relax)

QE v.7.3.1 started 4Oct2026 15:52:31; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 294759.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled. Completed: JOB DONE; terminated 8:41:56   5Oct2026; PWSCF time {'cpu': '16h39m', 'wall': '16h49m', 'calls': None}; output lines 39722.

**Input settings** (every namelist variable):

- &CONTROL: calculation = relax, prefix = rel, outdir = ./tmp, pseudo_dir = ./, verbosity = low, tprnfor = .true., tstress = .true., max_seconds = 257378, nstep = 300, etot_conv_thr = 1.0d-4, forc_conv_thr = 1.0d-3
- &SYSTEM: ibrav = 0, nat = 176, ntyp = 4, ecutwfc = 71, ecutrho = 568, occupations = smearing, smearing = mv, degauss = 0.01, nbnd = 677
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- &IONS: ion_dynamics = bfgs
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "W", "mass": 183.84, "pseudo": "W.pbe-spn-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.31791632, 0.0, 0.0], [0.0, 10.30849134, 0.0], [0.0, 0.0, 45.18062913]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 176, "labels": ["H", "In", "O", "W"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4980  a.u.; unit-cell volume = 32429.1815 (a.u.)^3; number of atoms/cell = 176; number of atomic types = 4; number of electrons = 1329.00; number of Kohn-Sham states = 677; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; energy convergence thresh. = 1.0E-04; force convergence thresh. = 1.0E-03; Exchange-correlation = SLA  PW   PBX  PBC; nstep = 300; celldm = [19.498036, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); W W.pbe-spn-kjpaw_psl.1.0.0.UPF md5 03c3df5b60893f488392c7401945500a (Projector augmented-wave + core cor, Z 14.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 2 Sym. Ops. (no inversion) found ( 1 have fractional translation); k points: number of k points=     4  Marzari-Vanderbilt smearing, width (Ry)=  0.0100 (sum of weights 2.0); FFT: Dense  grid:  7413139 G-vectors     FFT dimensions: ( 150, 150, 648) / Smooth grid:  2620949 G-vectors     FFT dimensions: ( 108, 108, 480)
- RAM (pw.x estimate): {'Estimated max dynamical RAM per process': '82.25 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge    1328.7946, renormalised to    1329.0000', 'Starting wfcs are  916 randomized atomic wfcs']

**Convergence** (29 SCF + BFGS): bfgs converged in  29 scf cycles and  28 bfgs steps (criteria: energy <  1.0E-04 Ry, force <  1.0E-03 Ry/Bohr) final energy -27385.206187481 final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 70 | 7.2e-10 | -27384.98747561 |  | 0.07675 | 0.0121 | 0.277402 | 0.000145 | -0.93 |  |  | 0.1112 |
| 1 | 54 | 7.9e-10 | -27385.05648954 |  | 0.06504 | 0.00968 | 0.222514 | 0.000138 | -0.73 |  |  | 0.1223 |
| 2 | 50 | 3.4e-10 | -27385.11287151 |  | 0.05447 | 0.00752 | 0.172775 | 7.9e-05 | -0.11 |  |  | 0.1835 |
| 3 | 47 | 5.4e-10 | -27385.16795919 |  | 0.03345 | 0.00447 | 0.102627 | 7.8e-05 | 1.13 |  |  | 0.2462 |
| 4 | 86 | 1.8e-10 | -27385.180519 |  | 0.03201 | 0.00506 | 0.116375 | 5.1e-05 | 4.3 |  |  | 0.09267 |
| 5 | 66 | 2.2e-10 | -27385.18910786 |  | 0.01603 | 0.00212 | 0.048662 | 3e-05 | 2.63 |  |  | 0.02546 |
| 6 | 43 | 1.4e-10 | -27385.19183461 |  | 0.01367 | 0.00177 | 0.04075 | 4.4e-05 | 2.81 |  |  | 0.02801 |
| 7 | 44 | 7.5e-11 | -27385.19442062 |  | 0.01126 | 0.00152 | 0.035031 | 3.1e-05 | 2.88 |  |  | 0.04202 |
| 8 | 63 | 6.6e-11 | -27385.19764241 |  | 0.007896 | 0.00121 | 0.02783 | 3.6e-05 | 3.07 |  |  | 0.06302 |
| 9 | 41 | 1.4e-11 | -27385.20040194 |  | 0.008482 | 0.0011 | 0.02538 | 2.1e-05 | 3.2 |  |  | 0.03299 |
| 10 | 42 | 7.6e-11 | -27385.20141949 |  | 0.006158 | 0.00116 | 0.026672 | 3.8e-05 | 3.24 |  |  | 0.02385 |
| 11 | 45 | 4.6e-11 | -27385.20228763 |  | 0.005786 | 0.000961 | 0.022071 | 2e-05 | 3.13 |  |  | 0.02623 |
| 12 | 57 | 4.5e-11 | -27385.20323788 |  | 0.003984 | 0.000781 | 0.017954 | 2.3e-05 | 3.02 |  |  | 0.02331 |
| 13 | 49 | 1.5e-11 | -27385.20397314 |  | 0.003869 | 0.000718 | 0.016503 | 1.6e-05 | 2.93 |  |  | 0.01222 |
| 14 | 65 | 3.4e-11 | -27385.20429339 |  | 0.003942 | 0.00067 | 0.0154 | 2.5e-05 | 2.92 |  |  | 0.01313 |
| 15 | 47 | 2.7e-11 | -27385.20461096 |  | 0.003209 | 0.000554 | 0.012739 | 2.3e-05 | 2.91 |  |  | 0.01417 |
| 16 | 44 | 3e-11 | -27385.20487211 |  | 0.001851 | 0.00046 | 0.010565 | 2.4e-05 | 2.88 |  |  | 0.0157 |
| 17 | 46 | 1.5e-11 | -27385.20508321 |  | 0.002019 | 0.000409 | 0.009408 | 9e-06 | 2.83 |  |  | 0.01113 |
| 18 | 57 | 1.9e-11 | -27385.20521906 |  | 0.00175 | 0.000379 | 0.008708 | 1.2e-05 | 2.77 |  |  | 0.01179 |
| 19 | 49 | 1.1e-11 | -27385.20535932 |  | 0.001922 | 0.000359 | 0.00826 | 1.1e-05 | 2.67 |  |  | 0.01094 |
| 20 | 44 | 1e-11 | -27385.20549088 |  | 0.001621 | 0.000359 | 0.008256 | 6e-06 | 2.58 |  |  | 0.009331 |
| 21 | 48 | 9.1e-12 | -27385.20560941 |  | 0.001738 | 0.000354 | 0.008131 | 1.3e-05 | 2.47 |  |  | 0.007603 |
| 22 | 54 | 1.1e-11 | -27385.20571091 |  | 0.001667 | 0.000336 | 0.007712 | 1.4e-05 | 2.41 |  |  | 0.006463 |
| 23 | 73 | 9.4e-12 | -27385.20580382 |  | 0.001687 | 0.000317 | 0.007291 | 1.5e-05 | 2.32 |  |  | 0.007472 |
| 24 | 68 | 8.6e-12 | -27385.20589827 |  | 0.001502 | 0.000317 | 0.007281 | 1.6e-05 | 2.23 |  |  | 0.007907 |
| 25 | 49 | 9.1e-12 | -27385.20598346 |  | 0.001435 | 0.00032 | 0.007347 | 1.2e-05 | 2.14 |  |  | 0.007974 |
| 26 | 53 | 4.2e-12 | -27385.20605669 |  | 0.001291 | 0.00029 | 0.00667 | 1.1e-05 | 2.03 |  |  | 0.006651 |
| 27 | 43 | 9.1e-12 | -27385.20612352 |  | 0.001031 | 0.00025 | 0.005754 | 1e-05 | 1.95 |  |  | 0.007697 |
| 28 | 54 | 8.7e-12 | -27385.20618748 |  | 0.0008154 | 0.000234 | 0.005386 | 8e-06 | 1.86 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.0459, 0.0], E_F_eV = 2.3492, E_Ry = -27385.20618748, E_all_electron_Ry = -693758.168521, acc_final_Ry = 8.7e-12, mTS_Ry = -0.00132155, internal_energy_Ry = -27385.20486593, one_electron_Ry = -272001.15745918, hartree_Ry = 136782.94247313, xc_Ry = -3322.87613255, ewald_Ry = 127677.07172814, paw_one_center_Ry = -16521.18547546, converged_iterations = 54, bfgs_energy_error_Ry = 6.4e-05
- stress tensor (kbar): [[2.86, 0.0, 0.21], [0.0, 2.91, 0.0], [0.21, 0.0, -0.2]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 677, "E_F_eV": 2.3492, "bands_fully_below_EF": 664, "bands_crossing_EF_1based": [665], "highest_band_below_EF_max_eV": 2.0843, "lowest_band_above_EF_min_eV": 2.4184}

**Final geometry** (vs `relax.in`): {"n_atoms": 176, "composition": {"H": 24, "In": 55, "O": 96, "W": 1}, "cell_lengths_A": [10.31792, 10.30849, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5089, "density_g_cm3": 2.7848, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 330, "min": 2.1292, "mean": 2.2283, "max": 2.5046, "std": 0.0617, "CN_In_hist": {"6": 55}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 1.8665, "mean": 1.9767, "max": 2.1897, "std": 0.1506, "CN_W_hist": {"6": 1}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9725, "mean": 0.9779, "max": 0.987, "std": 0.0063, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.458, "extent_A": 19.722, "thickness_H_H_A": 19.7222, "thickness_O_O_A": 18.2838, "thickness_In_In_A": 15.5749, "thickness_W_W_A": 0.0}, "displacement_vs_initial": {"max_A": 0.4256, "atom": "O97", "mean_A": 0.0486, "n_gt_0p1_A": 10, "by_element_max_A": {"H": 0.0635, "In": 0.1014, "O": 0.4256, "W": 0.0942}, "outer_3A_mean_A": 0.033, "interior_mean_A": 0.0575}, "reference_input": "relax.in"}

**Warnings/errors**: message_from_routine x1 (first: line 30 'Message from routine setup:'); warning x4 (first: line 10128 'WARNING: bfgs curvature condition failed, Theta= 0.982'); c_bands_not_converged x28 (first: line 391 'c_bands:  3 eigenvalues not converged'); ieee x3 (first: line 39719 'Warning: ieee_invalid is signaling'); discouraged x1 (first: line 31 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x4 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized'); fortran_stop x1 (first: line 39722 'FORTRAN STOP')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized']

## Input geometries

- `relax.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 55, "O": 96, "W": 1}, "cell_lengths_A": [10.31792, 10.30849, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5089, "density_g_cm3": 2.7848, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 330, "min": 2.1616, "mean": 2.2197, "max": 2.3007, "std": 0.0356, "CN_In_hist": {"6": 55}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 2.1671, "mean": 2.223, "max": 2.2623, "std": 0.0406, "CN_W_hist": {"6": 1}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9722, "mean": 0.9773, "max": 0.9858, "std": 0.0061, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.557, "extent_A": 19.623, "thickness_H_H_A": 19.6233, "thickness_O_O_A": 18.2137, "thickness_In_In_A": 15.4861, "thickness_W_W_A": 0.0}}

## Checks against RESULTS_LOG

| quantity | re-derived | logged | reference | status |
|---|---|---|---|---|
| BFGS steps | 28 | 28 | RESULTS_LOG.md:533 | match |
| relax wall (h) | 16.817 | 16.816666666666666 | RESULTS_LOG.md:533 | match |
| final energy (Ry) | -27385.206187481 | -27385.206187481 | RESULTS_LOG.md:533 | match |
| max displacement (A) | 0.4256 | 0.43 | RESULTS_LOG.md:512 | match |
| W displacement (A) | 0.0942 | 0.09 | RESULTS_LOG.md:512 | match |
| W-O mean (A) | 1.9767 | 1.977 | RESULTS_LOG.md:512 | match |
