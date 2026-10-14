# iwo_slab1_W24d_x1

**Purpose.** 1 nm IWO slab (W on the central 24d site): relax on one H100; the following final SCF wrote a runaway output and was stopped.

Folder `cern_htcondor/results/iwo_slab1_W24d_x1`; data `runs_sep_oct/out/iwo_slab1_W24d_x1.json` (+ `iwo_slab1_W24d_x1_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| bands.in | 8514 | 7ea52f6a05fe7599 | loose | pw_in |
| bands.tmpl | 5924 | 2b17ad1c73036aff | loose | pw_tmpl |
| iwo_slab1_W24d_x1_driver.log | 672 | 1413bd17246e17e8 | loose | driver |
| relax.in | 5198 | faa0e6ec9fb9a802 | loose | pw_in |
| relax.out | 1259493 | fb2f909116e69aa4 | loose | pw_out |
| scf.in | 7707 | a861bbd571d8f9a5 | loose | pw_in |
| scf.tmpl | 5116 | a485aacde6e7781e | loose | pw_tmpl |
| steps.sh | 469 | 8af7a63cb1fcc314 | loose | steps |

Tarball `iwo_slab1_W24d_x1_results.tar.gz` (88484691 B, sha256 abf4aa4b15cc49ed): 9 members; identical to the loose copy: 8; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0; not loaded: ['scf.out (9381515352 B: too large: streamed separately (stream_runaway.py))']

## Resources and run history

- `iwo_slab1_W24d_x1_driver.log`: host b9pgpun003.cern.ch, 11 CPUs, wall limit 259200 s, GPU: 1 GPU(s), NVIDIA H100 NVL, 95830 MiB, job total 16310 s, start 2026-09-30T12:26:27Z
  - step relax: -nk 1, max_seconds 257382, start 2026-09-30T12:26:45Z, end 2026-09-30T16:56:47Z, rc 0, PWSCF        :      4h28m CPU      4h29m WALL
  - step scf: -nk 1, max_seconds 241179, start 2026-09-30T16:56:48Z, end 2026-09-30T16:57:48Z, rc 143, 
  - log: [2026-09-30T16:57:48Z] scf.out exceeded 2 GB: runaway output, pw.x stopped
- HTCondor iwo_slab1_W24d_x1 12788378.0: 11 CPUs, 1 GPU; seen 2026-09-30T11:01:18Z to 2026-09-30T16:58:51Z (66 samples); states {'1': 16, '2': 50} (1 idle, 2 running, 3 removed, 5 held); max scf_it 1036, max BFGS 26; steps ['relax', 'scf']; hw ['1xNVIDIA H100 NVL|0%', '1xNVIDIA H100 NVL|11%', '1xNVIDIA H100 NVL|12%', '1xNVIDIA H100 NVL|13%', '1xNVIDIA H100 NVL|15%', '1xNVIDIA H100 NVL|16%', '1xNVIDIA H100 NVL|17%', '1xNVIDIA H100 NVL|19%', '1xNVIDIA H100 NVL|35%', '1xNVIDIA H100 NVL|5%', '1xNVIDIA H100 NVL|59%', '1xNVIDIA H100 NVL|8%', '1xNVIDIA H100 NVL|86%', '1xNVIDIA H100 NVL|9%', '1xNVIDIA H100 NVL|91%', '1xNVIDIA H100 NVL|92%', '1xNVIDIA H100 NVL|97%', '1xNVIDIA H100 NVL|98%', 'Intel(R) Xeon(R) Platinum 8468'] ['', 'Intel(R) Xeon(R) Platinum 8468']
- `steps.sh`: `steps() { run_pw relax 1 python qeio.py converged relax.out || { log "relaxation did not finish; later steps skipped"; return 0; } for t in scf bands; do python qeio.py newgeom $t.tmpl relax.out > $t.in; done clean_tmp export FORCE_CPU=1 # one QE version (CPU 7.5) for SCF, pp.x and projwfc.x; one pool (NCPU may be odd) run_pw scf 1 || return 0 run_ppavg slab "$JOB" 4.8833 run_pdos slab "$JOB" "$(python qeio.py fermi scf.out)" 1 run_pw bands 1 }`

**What failed and why (from the files above).** The relax (GPU, 1 rank) converged. The follow-on SCF was started with 11 MPI ranks and never produced pw.x output: UCX reported that InfiniBand memory registration failed (ibv_reg_mr ... Cannot allocate memory; the message suggests raising max locked memory, ulimit -l) and flooded scf.out (a restrictive memlock limit is plausible but its value was not measured); the driver stopped it after 60 s at > 2 GB (rc 143), yet the packed file is 9.38 GB (see below; the NUL-byte count describes the file content, not its cause). The geometry was carried on in iwo_slab1_final_cpu.

**Runaway scf.out (tar member, 9381515352 B, sha256 a5a3f19b0fadc452; streamed, never written to disk):** 17055930 lines; 5944745457 NUL bytes (63.4 %, first at offset 0); marker counts {'Program PWSCF': 0, 'JOB DONE': 0, '!    total energy': 0, 'Error in routine': 0, 'UCX  ERROR': 17054662}; most frequent lines: '[#] [b#pgpun#:# :#]           mpool.c:#  UCX  ERROR Failed to allocate memory pool (name=rc_recv_desc) chunk: ' x8524598; '[#] [b#pgpun#:# :#]           ib_md.c:#  UCX  ERROR ibv_reg_mr(address=#x#, length=#, access=#xf) failed: Cann' x2333171; '[#] [b#pgpun#:# :#]           ib_md.c:#  UCX  ERROR ibv_reg_mr(address=#x#a#, length=#, access=#xf) failed: Ca' x2322220. Source: `out/iwo_slab1_W24d_x1_runaway_scf.json` (stream_runaway.py, stream_runaway_nul.py).

## Calculation `relax.out` (scf/relax)

QE v.7.3.1 started 30Sep2026 14:26:46; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 285285.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled. Completed: JOB DONE; terminated 18:56:44  30Sep2026; PWSCF time {'cpu': '4h28m', 'wall': '4h29m', 'calls': None}; output lines 24741.

**Input settings** (every namelist variable):

- &CONTROL: calculation = relax, prefix = rel, outdir = ./tmp, pseudo_dir = ./, verbosity = low, tprnfor = .true., tstress = .true., max_seconds = 257382, nstep = 300, etot_conv_thr = 1.0d-4, forc_conv_thr = 1.0d-3
- &SYSTEM: ibrav = 0, nat = 96, ntyp = 4, ecutwfc = 71, ecutrho = 568, occupations = smearing, smearing = mv, degauss = 0.01
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- &IONS: ion_dynamics = bfgs
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "W", "mass": 183.84, "pseudo": "W.pbe-spn-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.33643106, 0.0, 0.0], [0.0, 10.33450421, 0.0], [0.0, 0.0, 34.87453893]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 96, "labels": ["H", "In", "O", "W"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.5330  a.u.; unit-cell volume = 25140.0035 (a.u.)^3; number of atoms/cell = 96; number of atomic types = 4; number of electrons = 625.00; number of Kohn-Sham states = 376; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; energy convergence thresh. = 1.0E-04; force convergence thresh. = 1.0E-03; Exchange-correlation = SLA  PW   PBX  PBC; nstep = 300; celldm = [19.533024, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); W W.pbe-spn-kjpaw_psl.1.0.0.UPF md5 03c3df5b60893f488392c7401945500a (Projector augmented-wave + core cor, Z 14.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 2 Sym. Ops. (no inversion) found ( 1 have fractional translation); k points: number of k points=     4  Marzari-Vanderbilt smearing, width (Ry)=  0.0100 (sum of weights 2.0); FFT: Dense  grid:  5746731 G-vectors     FFT dimensions: ( 150, 150, 500) / Smooth grid:  2031701 G-vectors     FFT dimensions: ( 108, 108, 360)
- RAM (pw.x estimate): {'Estimated max dynamical RAM per process': '42.10 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge     624.9136, renormalised to     625.0000', 'Starting wfcs are  436 randomized atomic wfcs']

**Convergence** (28 SCF + BFGS): bfgs converged in  28 scf cycles and  27 bfgs steps (criteria: energy <  1.0E-04 Ry, force <  1.0E-03 Ry/Bohr) final energy -12238.2891089616 final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 59 | 6.2e-10 | -12238.10543769 |  | 0.0722 | 0.0144 | 0.245114 | 0.000104 | -1.22 |  |  | 0.1011 |
| 1 | 31 | 9.7e-10 | -12238.1599217 |  | 0.0597 | 0.0119 | 0.201514 | 0.000143 | -1.1 |  |  | 0.1112 |
| 2 | 28 | 5e-10 | -12238.20418861 |  | 0.04976 | 0.00917 | 0.155578 | 8.8e-05 | -0.39 |  |  | 0.1668 |
| 3 | 36 | 2.2e-10 | -12238.24847953 |  | 0.03277 | 0.00589 | 0.099996 | 6.3e-05 | 0.67 |  |  | 0.2502 |
| 4 | 57 | 3.6e-11 | -12238.25906655 |  | 0.02882 | 0.00658 | 0.111688 | 2.1e-05 | 4.19 |  |  | 0.09333 |
| 5 | 34 | 2.1e-10 | -12238.26807123 |  | 0.01412 | 0.00273 | 0.046358 | 4.1e-05 | 2.24 |  |  | 0.01921 |
| 6 | 32 | 1.2e-10 | -12238.27032845 |  | 0.01289 | 0.00234 | 0.03965 | 5.1e-05 | 2.3 |  |  | 0.02113 |
| 7 | 31 | 1.1e-10 | -12238.27240553 |  | 0.0117 | 0.00212 | 0.035895 | 4.9e-05 | 2.31 |  |  | 0.0317 |
| 8 | 34 | 9.3e-11 | -12238.27520584 |  | 0.01024 | 0.00183 | 0.031032 | 4.3e-05 | 2.36 |  |  | 0.04755 |
| 9 | 36 | 4.2e-11 | -12238.27851862 |  | 0.007828 | 0.00155 | 0.026371 | 3.1e-05 | 2.43 |  |  | 0.07132 |
| 10 | 38 | 5.7e-11 | -12238.28170967 |  | 0.006268 | 0.00146 | 0.024839 | 2.9e-05 | 2.56 |  |  | 0.05225 |
| 11 | 40 | 5.7e-11 | -12238.28289553 |  | 0.005075 | 0.00161 | 0.02738 | 2.4e-05 | 2.55 |  |  | 0.01464 |
| 12 | 37 | 3.8e-11 | -12238.28364105 |  | 0.00493 | 0.00144 | 0.024482 | 2.7e-05 | 2.43 |  |  | 0.01611 |
| 13 | 39 | 4e-11 | -12238.28468432 |  | 0.004078 | 0.00119 | 0.020195 | 2.2e-05 | 2.27 |  |  | 0.02416 |
| 14 | 40 | 2.9e-11 | -12238.28608526 |  | 0.004164 | 0.00113 | 0.019193 | 1.7e-05 | 2.02 |  |  | 0.01964 |
| 15 | 39 | 4.1e-11 | -12238.28667718 |  | 0.003964 | 0.00111 | 0.018829 | 1.7e-05 | 1.79 |  |  | 0.01212 |
| 16 | 32 | 3.7e-11 | -12238.28706592 |  | 0.002981 | 0.00098 | 0.016625 | 2.3e-05 | 1.67 |  |  | 0.01333 |
| 17 | 34 | 1.5e-11 | -12238.2874956 |  | 0.001967 | 0.000765 | 0.012978 | 1.7e-05 | 1.52 |  |  | 0.01713 |
| 18 | 38 | 1.9e-11 | -12238.28789036 |  | 0.002003 | 0.00072 | 0.01222 | 1.5e-05 | 1.36 |  |  | 0.007906 |
| 19 | 37 | 1.8e-11 | -12238.2880796 |  | 0.00214 | 0.000709 | 0.012036 | 1.7e-05 | 1.28 |  |  | 0.01231 |
| 20 | 38 | 1.5e-11 | -12238.28831736 |  | 0.002023 | 0.000658 | 0.011169 | 1.8e-05 | 1.2 |  |  | 0.01003 |
| 21 | 39 | 1.9e-11 | -12238.28848647 |  | 0.001599 | 0.000571 | 0.009696 | 2e-05 | 1.16 |  |  | 0.009276 |
| 22 | 39 | 1.2e-11 | -12238.28861993 |  | 0.00136 | 0.000484 | 0.008207 | 1.1e-05 | 1.13 |  |  | 0.008152 |
| 23 | 33 | 1.3e-11 | -12238.28872531 |  | 0.001474 | 0.000474 | 0.008047 | 1.7e-05 | 1.1 |  |  | 0.01068 |
| 24 | 36 | 5.5e-12 | -12238.28884094 |  | 0.001536 | 0.000468 | 0.007945 | 1.1e-05 | 1.05 |  |  | 0.01222 |
| 25 | 40 | 7.8e-12 | -12238.28895323 |  | 0.001458 | 0.000432 | 0.007339 | 6e-06 | 0.99 |  |  | 0.0114 |
| 26 | 35 | 3.6e-12 | -12238.28904364 |  | 0.001099 | 0.000381 | 0.006473 | 5e-06 | 0.95 |  |  | 0.008471 |
| 27 | 38 | 9.4e-12 | -12238.28910896 |  | 0.0009835 | 0.000362 | 0.006147 | 1.3e-05 | 0.93 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.03875, 0.0], E_F_eV = 0.581, E_Ry = -12238.28910896, E_all_electron_Ry = -310100.465649, acc_final_Ry = 9.4e-12, mTS_Ry = -0.00299458, internal_energy_Ry = -12238.28611438, one_electron_Ry = -78725.20134273, hartree_Ry = 39662.69296792, xc_Ry = -1481.05002692, ewald_Ry = 35641.7461939, paw_one_center_Ry = -7336.47390655, converged_iterations = 38, bfgs_energy_error_Ry = 6.5e-05
- stress tensor (kbar): [[1.94, 0.0, 0.26], [0.0, 1.71, 0.0], [0.26, 0.0, -0.87]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 376, "E_F_eV": 0.581, "bands_fully_below_EF": 312, "bands_crossing_EF_1based": [313], "highest_band_below_EF_max_eV": 0.1546, "lowest_band_above_EF_min_eV": 0.7245}

**Final geometry** (vs `relax.in`): {"n_atoms": 96, "composition": {"H": 24, "In": 23, "O": 48, "W": 1}, "cell_lengths_A": [10.33643, 10.3345, 34.87454], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3725.3642, "density_g_cm3": 1.6121, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 138, "min": 2.1474, "mean": 2.2379, "max": 2.5581, "std": 0.0788, "CN_In_hist": {"6": 23}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 1.88, "mean": 1.9996, "max": 2.212, "std": 0.1506, "CN_W_hist": {"6": 1}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9727, "mean": 0.9792, "max": 0.9903, "std": 0.0071, "CN_O_hist": {"0": 24, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 24}, "slab": {"vacuum_A": 25.417, "extent_A": 9.458, "thickness_H_H_A": 9.4577, "thickness_O_O_A": 7.9761, "thickness_In_In_A": 5.2733, "thickness_W_W_A": 0.0}, "displacement_vs_initial": {"max_A": 0.4011, "atom": "O66", "mean_A": 0.0796, "n_gt_0p1_A": 18, "by_element_max_A": {"H": 0.1187, "In": 0.1389, "O": 0.4011, "W": 0.0737}, "outer_3A_mean_A": 0.0756, "interior_mean_A": 0.0877}, "reference_input": "relax.in"}

**Warnings/errors**: message_from_routine x1 (first: line 30 'Message from routine setup:'); warning x5 (first: line 2089 'WARNING: bfgs curvature condition failed, Theta= 0.992'); c_bands_not_converged x138 (first: line 344 'c_bands:  2 eigenvalues not converged'); ieee x3 (first: line 24738 'Warning: ieee_invalid is signaling'); discouraged x1 (first: line 31 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x4 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized'); fortran_stop x1 (first: line 24741 'FORTRAN STOP')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized']

## Input geometries

- `bands.in`: {"n_atoms": 96, "composition": {"H": 24, "In": 23, "O": 48, "W": 1}, "cell_lengths_A": [10.33643, 10.3345, 34.87454], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3725.3642, "density_g_cm3": 1.6121, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 138, "min": 2.1474, "mean": 2.2379, "max": 2.5581, "std": 0.0788, "CN_In_hist": {"6": 23}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 1.88, "mean": 1.9996, "max": 2.212, "std": 0.1506, "CN_W_hist": {"6": 1}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9727, "mean": 0.9792, "max": 0.9903, "std": 0.0071, "CN_O_hist": {"0": 24, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 24}, "slab": {"vacuum_A": 25.417, "extent_A": 9.458, "thickness_H_H_A": 9.4577, "thickness_O_O_A": 7.9761, "thickness_In_In_A": 5.2733, "thickness_W_W_A": 0.0}}
- `relax.in`: {"n_atoms": 96, "composition": {"H": 24, "In": 23, "O": 48, "W": 1}, "cell_lengths_A": [10.33643, 10.3345, 34.87454], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3725.3642, "density_g_cm3": 1.6121, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 138, "min": 2.1647, "mean": 2.2187, "max": 2.3078, "std": 0.0385, "CN_In_hist": {"6": 23}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 2.1659, "mean": 2.2257, "max": 2.2833, "std": 0.048, "CN_W_hist": {"6": 1}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9719, "mean": 0.9775, "max": 0.9864, "std": 0.0064, "CN_O_hist": {"0": 24, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 24}, "slab": {"vacuum_A": 25.571, "extent_A": 9.303, "thickness_H_H_A": 9.3033, "thickness_O_O_A": 7.8762, "thickness_In_In_A": 5.1515, "thickness_W_W_A": 0.0}}
- `scf.in`: {"n_atoms": 96, "composition": {"H": 24, "In": 23, "O": 48, "W": 1}, "cell_lengths_A": [10.33643, 10.3345, 34.87454], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 3725.3642, "density_g_cm3": 1.6121, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 138, "min": 2.1474, "mean": 2.2379, "max": 2.5581, "std": 0.0788, "CN_In_hist": {"6": 23}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 1.88, "mean": 1.9996, "max": 2.212, "std": 0.1506, "CN_W_hist": {"6": 1}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9727, "mean": 0.9792, "max": 0.9903, "std": 0.0071, "CN_O_hist": {"0": 24, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 24}, "slab": {"vacuum_A": 25.417, "extent_A": 9.458, "thickness_H_H_A": 9.4577, "thickness_O_O_A": 7.9761, "thickness_In_In_A": 5.2733, "thickness_W_W_A": 0.0}}

Geometry consistency (input of the follow-on step vs relax final coordinates): {"scf.in vs final of relax.out": {"max_pos_diff_A": 0.0, "max_cell_diff_A": 0.0}, "bands.in vs final of relax.out": {"max_pos_diff_A": 0.0, "max_cell_diff_A": 0.0}}

## Other files

- `.fetched`: ''

## Checks against RESULTS_LOG

| quantity | re-derived | logged | reference | status |
|---|---|---|---|---|
| BFGS steps | 27 | 27 | RESULTS_LOG.md:611 | match |
| final energy (Ry) | -12238.2891089616 | -12238.28910896 | RESULTS_LOG.md:611 | match |
| W-O mean (A) (log: 1.880 x2, 1.907 x2, 2.212 x2) | 1.9996 | 1.9997 | RESULTS_LOG.md:615 | match |
