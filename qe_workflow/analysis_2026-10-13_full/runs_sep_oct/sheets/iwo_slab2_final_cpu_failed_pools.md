# iwo_slab2_final_cpu_failed_pools

**Purpose.** First attempt of iwo_slab2_final_cpu: stopped after 60 s by an MPI pool error.

Folder `cern_htcondor/results/iwo_slab2_final_cpu_failed_pools`; data `runs_sep_oct/out/iwo_slab2_final_cpu_failed_pools.json` (+ `iwo_slab2_final_cpu_failed_pools_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| iwo_slab2_final_cpu_driver.log | 369 | c2472295432855cf | loose | driver |
| scf.in | 8721 | 904738e012d2af7b | loose | pw_in |
| scf.out | 2590 | f29343cc0420ba65 | loose | pw_out |
| steps.sh | 207 | ee0961c9e2c0a17b | loose | steps |

Tarball `iwo_slab2_final_cpu_results.tar.gz` (5276 B, sha256 842917b8c0dbcf37): 4 members; identical to the loose copy: 4; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0

## Resources and run history

- `iwo_slab2_final_cpu_driver.log`: host b9p12p1627.cern.ch, 33 CPUs, wall limit 86400 s, GPU: none (CPU), job total 71 s, start 2026-10-05T12:53:32Z
  - step scf: -nk 2, max_seconds 84589, start 2026-10-05T12:53:43Z, end 2026-10-05T12:54:43Z, rc 1, 
- HTCondor iwo_slab2_final_cpu 12835131.0: 33 CPUs, 0 GPU; seen 2026-10-05T12:50:54Z to 2026-10-05T12:50:54Z (1 samples); states {'1': 1} (1 idle, 2 running, 3 removed, 5 held); max scf_it 0, max BFGS 0; steps []; hw  
- HTCondor iwo_slab2_final_cpu 12835211.0: 33 CPUs, 0 GPU; seen 2026-10-05T16:20:34Z to 2026-10-06T00:25:53Z (84 samples); states {'1': 1, '2': 83} (1 idle, 2 running, 3 removed, 5 held); max scf_it 91, max BFGS 0; steps ['scf']; hw  ['AMD EPYC 7543 32-Core Processor']
- `steps.sh`: `steps() { export FORCE_CPU=1 # one QE version (CPU 7.5) for SCF, pp.x and projwfc.x run_pw scf 2 || return 0 run_ppavg slab "$JOB" 4.8745 run_pdos slab "$JOB" "$(python qeio.py fermi scf.out)" 2 }`

**What failed and why (from the files above).** pw.x stopped 60 s after start with "Error in routine mp_start_pools (1): invalid number of pools, parent_nproc /= nproc_pool * npool" (scf.out line 43): 33 MPI ranks cannot be split into -nk 2 pools. This is cluster 12835131; the successful rerun with -nk 1 is cluster 12835211 (folder iwo_slab2_final_cpu).

## Calculation `scf.out` (scf/relax)

QE v.7.5 started 5Oct2026 14:53:44; 33 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 162634.0 MiB; ; ; GPU: no GPU line. Completed: NO (no JOB DONE); terminated None; PWSCF time None; output lines 53.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 84589
- &SYSTEM: ibrav = 0, nat = 176, ntyp = 4, ecutwfc = 71, ecutrho = 568, occupations = smearing, smearing = mv, degauss = 0.01, nbnd = 688
- &ELECTRONS: conv_thr = 1.0d-8, mixing_beta = 0.1, electron_maxstep = 200, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "W", "mass": 183.84, "pseudo": "W.pbe-spn-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.3179162589, 0.0, 0.0], [0.0, 10.3084960013, 0.0], [0.0, 0.0, 45.1806282459]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 176, "labels": ["H", "In", "O", "W"], "n_constrained": 0}
- Echoed parameters: 
- Pseudopotentials: 
- Symmetry: None; k points: None (sum of weights None); FFT: None / None
- RAM (pw.x estimate): {}; start: None

**Warnings/errors**: message_from_routine x1 (first: line 39 'Message from routine setup:'); error x3 (first: line 42 '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'); discouraged x1 (first: line 40 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x4 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized'); mpi_abort x2 (first: line 31 'MPI_ABORT was invoked on rank 16 in communicator MPI_COMM_WORLD')
- QE/MPI error lines: [[31, 'MPI_ABORT was invoked on rank 16 in communicator MPI_COMM_WORLD'], [35, 'NOTE: invoking MPI_ABORT causes Open MPI to kill all MPI processes.'], [43, 'Error in routine mp_start_pools (1): invalid number of pools, parent_nproc /= nproc_pool * npool'], [49, 'prterun has exited due to process rank 32 with PID 0 on node b9p12p1627 calling']]
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized']

## Input geometries

- `scf.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 55, "O": 96, "W": 1}, "cell_lengths_A": [10.31792, 10.3085, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5109, "density_g_cm3": 2.7848, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 330, "min": 2.1292, "mean": 2.2283, "max": 2.5046, "std": 0.0617, "CN_In_hist": {"6": 55}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 1.8665, "mean": 1.9767, "max": 2.1897, "std": 0.1506, "CN_W_hist": {"6": 1}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9725, "mean": 0.9779, "max": 0.987, "std": 0.0063, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.458, "extent_A": 19.722, "thickness_H_H_A": 19.7222, "thickness_O_O_A": 18.2838, "thickness_In_In_A": 15.5749, "thickness_W_W_A": 0.0}}

## Other files

- `.fetched`: ''
