# Master table: CERN runs 20 Sep - 7 Oct 2026 (41 folders)

## Key findings (read from out/*.json)

- Coverage: 41 folders, 418 files (tarball members included), 67 pw.x outputs (42 QE 7.5, 25 QE 7.3.1 GPU), 7 projwfc outputs, 8 PDOS sets; every tarball member compared byte-for-byte with its loose copy: all identical.
- Each pseudopotential file has one MD5 in every run (PAW pslibrary 1.0.0 set; SG15 ONCV 1.2 set for the NC/HSE checks): H.pbe-kjpaw_psl.1.0.0.UPF d81a744832360e4a8af0b0b5b123bc2a; H_ONCV_PBE-1.2.upf bf21e08b90ac4ce7d0149ac4e8138190; In.pbe-dn-kjpaw_psl.1.0.0.UPF 235b15e6a7fdfd96486e0ecdcb5b12c6; In_ONCV_PBE-1.2.upf 2123f823f6143602c63cd302e3a0bdd6; O.pbe-n-kjpaw_psl.1.0.0.UPF e99d9cef9b487d1ca56f5b95ecd0fd7a; O_ONCV_PBE-1.2.upf e36c48deb68f4e355fffe4602be2c42c; W.pbe-spn-kjpaw_psl.1.0.0.UPF 03c3df5b60893f488392c7401945500a.
- GPU benchmark: the slab1_v15 SCF on one H100 (QE 7.3.1) took 9m15.66s against 1h16m on 16 CPU cores (QE 7.5), 46 vs 46 iterations, energy difference 4.7e-07 Ry.
- HSE runs converge the EXX loop in 6 outer cycles (bulk, dexx 7.0e-03 -> 1.2e-10 Ry).
- iwo_slab1_W24d_x1: its packed scf.out is 9.38 GB with no pw.x line (Program PWSCF x0): 17054662 UCX ERROR lines (UCX: InfiniBand memory registration failed; restrictive memlock plausible, not measured) and 5.94 GB of NUL bytes from offset 0; the driver log says it stopped the step at > 2 GB after 60 s (rc 143). Streamed only; never written to disk.
- Failure causes identified in the files (details in the sheets): MPI slot shortage (failed_20260927a, 32 ranks), invalid pool split 33/2 (iwo_slab2_final_cpu_failed_pools), MPI_INIT failure, "sm" BTL not available in that Open MPI runtime (nc_hse_bulk_q3_e80), CUDA out of memory at the first EXX step with the default ecutfock (nc_hse_slab1_e80), cdiaghg Cholesky factorisation failure in the 1 nm W slab bands (rc 161; cause unresolved), UCX memory-registration error flood (iwo_slab1_W24d_x1 final SCF; cause plausible, not measured).
- Checks against RESULTS_LOG: 92 quoted values re-derived, 89 match; 3 differ:
  - slab2r_final_cpu_checkpoint: CPUs allocated / MPI ranks (driver, HTCondor and pw.x agree on 24; log 410 also says 24; the logged 16 is the request_cpus of cern_htcondor/jobs/gen_iwoslab2/jobs.txt:1, found 2026-10-14): re-derived 24, logged 16 (RESULTS_LOG.md:550).
  - iwo_slab2_final_cpu: HTCondor cluster of the run whose outputs are used (log: 12835131): re-derived 12835211.0, logged 12835131.0 (RESULTS_LOG.md:514).
  - live_snapshots: iwo_slab2_W24d final SCF ran on the GPU? (scf.out GPU lines; node had an H100): re-derived False, logged True (RESULTS_LOG.md:533).

One row per folder; details in `sheets/<run>.md` and `out/<run>.json`. Main output = the pw.x output with the most SCF steps. Gap = LUMO - HOMO of its last SCF (insulators) or E_F (smearing). All crystalline; COMPUTED. Checks: RESULTS_LOG quotations verified line by line.

| run | purpose | main output | QE | hardware | atoms | composition | ecut | k | smearing | SCF steps | BFGS | E final (Ry) | gap or E_F (eV) | job s | step rc | checks (differ) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [slab1_v15](sheets/slab1_v15.md) | Vacuum-convergence test, unrelaxed 1 nm In2O3(001) slab (H/OH-terminated, 96 atoms), 15 A  | scf.out | v.7.5 | 16 CPUs | 96 | {'H': 24, 'In': 24, 'O': 48} | 71.0000  Ry | 4 | fixed | 1 |  | -11888.29271155 | 0.9586 | 54679 | [0, 0] | 5 (0) |
| [slab1_v25](sheets/slab1_v25.md) | Vacuum-convergence test, unrelaxed 1 nm slab, 25 A vacuum (the Lin et al. value): SCF, pla | scf.out | v.7.5 | 16 CPUs | 96 | {'H': 24, 'In': 24, 'O': 48} | 71.0000  Ry | 4 | fixed | 1 |  | -11888.29270282 | 0.9586 | 53814 | [0, 0] | 5 (0) |
| [slab1_v35](sheets/slab1_v35.md) | Vacuum-convergence test, unrelaxed 1 nm slab, 35 A vacuum: SCF, planar average, bands (Dav | scf.out | v.7.5 | 16 CPUs | 96 | {'H': 24, 'In': 24, 'O': 48} | 71.0000  Ry | 4 | fixed | 1 |  | -11888.29270349 | 0.9586 | 11910 | [0, 0] | 13 (0) |
| [gpu_bench_v15](sheets/gpu_bench_v15.md) | GPU benchmark: the slab1_v15 SCF on one H100 NVL (QE 7.3.1 GPU) to compare cost and result | scf.out | v.7.3.1 | 1 GPU(s), NVIDIA H100 NVL, 95830 MiB | 96 | {'H': 24, 'In': 24, 'O': 48} | 71.0000  Ry | 4 | fixed | 1 |  | -11888.29271202 | 0.9586 | 575 | [0] | 0 (0) |
| [iwo_W8b](sheets/iwo_W8b.md) | 80-atom bulk IWO (In31 W O48, 3.1 % W) with W on the 8b site: relax (k3), SCF k4, projwfc/ | relax.out | v.7.5 | 32 CPUs | 80 | {'In': 31, 'O': 48, 'W': 1} | 71.0000  Ry | 6 | Marzari-Vanderbilt smearing | 17 | n  17 scf cycles and  16 bfgs steps | -15496.3476466 | 10.786 | 116622 | [0, 0, 0, 0] | 5 (0) |
| [iwo_W8b_partial](sheets/iwo_W8b_partial.md) | Copy of the running iwo_W8b relax output taken 2026-09-28 (preliminary site preference); p | relax.out | v.7.5 | 32 CPUs | 80 | {'In': 31, 'O': 48, 'W': 1} | 71.0000  Ry | 6 | Marzari-Vanderbilt smearing | 17 | n  17 scf cycles and  16 bfgs steps | -15496.3476466 | 10.786 | None | [0, 0, None] | 1 (0) |
| [iwo_W24d](sheets/iwo_W24d.md) | 80-atom bulk IWO with W on the 24d site: relax (k3), SCF k4, projwfc/PDOS, bands, spin-pol | relax.out | v.7.5 | 32 CPUs | 80 | {'In': 31, 'O': 48, 'W': 1} | 71.0000  Ry | 10 | Marzari-Vanderbilt smearing | 19 | n  19 scf cycles and  18 bfgs steps | -15496.36660367 | 10.8507 | 173398 | [0, 0, 0, 0] | 5 (0) |
| [iwo_W24d_partial](sheets/iwo_W24d_partial.md) | Copy of the running iwo_W24d relax output taken 2026-09-28 (preliminary site preference). | relax.out | v.7.5 | 32 CPUs | 80 | {'In': 31, 'O': 48, 'W': 1} | 71.0000  Ry | 10 | Marzari-Vanderbilt smearing | 19 | n  19 scf cycles and  18 bfgs steps | -15496.36660367 | 10.8507 | None | [0, None] | 1 (0) |
| [slab1_relax_gpu](sheets/slab1_relax_gpu.md) | vc-relax (atoms + in-plane cell, 2Dxy) of the 1 nm slab on a GPU after CPU steps; final SC | vcrelax.out | v.7.3.1 | 1 GPU(s), NVIDIA A100-PCIE-40GB, 40960 MiB | 96 | {'H': 24, 'In': 24, 'O': 48} | 71.0000  Ry | 4 | fixed | 58 | n  57 scf cycles and  54 bfgs steps | -11888.81106217 | 1.7885 | 74575 | [0, 0, 0] | 6 (0) |
| [cpu_relax_snapshots](sheets/cpu_relax_snapshots.md) | Snapshots of the CPU vc-relax of slab1_relax and slab2_relax taken before the GPU continua | slab1_relax_vcrelax.out | v.7.5 | - | None | None | 71.0000  Ry | 4 | fixed | 15 |  | None | None | None | [] | 1 (0) |
| [slab1r_final_cpu](sheets/slab1r_final_cpu.md) | CPU final SCF of the relaxed 1 nm slab geometry (QE 7.5) with planar average and bands (EA | scf.out | v.7.5 | 16 CPUs | 96 | {'H': 24, 'In': 24, 'O': 48} | 71.0000  Ry | 4 | fixed | 1 |  | -11888.81106135 | 1.7885 | 25080 | [0, 0] | 1 (0) |
| [iwo_slab1_W24d_x1](sheets/iwo_slab1_W24d_x1.md) | 1 nm IWO slab (W on the central 24d site): relax on one H100; the following final SCF wrot | relax.out | v.7.3.1 | 1 GPU(s), NVIDIA H100 NVL, 95830 MiB | 96 | {'H': 24, 'In': 23, 'O': 48, 'W': 1} | 71.0000  Ry | 4 | Marzari-Vanderbilt smearing | 28 | n  28 scf cycles and  27 bfgs steps | -12238.28910896 | 0.581 | 16310 | [0, 143] | 3 (0) |
| [iwo_slab1_final_cpu](sheets/iwo_slab1_final_cpu.md) | CPU final SCF, planar average, projwfc/PDOS and bands of the relaxed 1 nm IWO slab. | scf.out | v.7.5 | 16 CPUs | 96 | {'H': 24, 'In': 23, 'O': 48, 'W': 1} | 71.0000  Ry | 4 | Marzari-Vanderbilt smearing | 1 |  | -12238.28910785 | 0.5811 | 13531 | [0, 161] | 1 (0) |
| [nc_pbe_bulk_e80](sheets/nc_pbe_bulk_e80.md) | Norm-conserving (SG15) PBE single point of bulk In2O3 at the PAW-PBE geometry, 80 Ry (HSE  | scf.out | v.7.3.1 | 1 GPU(s), NVIDIA H100 NVL, 95830 MiB | 40 | {'In': 16, 'O': 24} | 80.0000  Ry | 4 | fixed | 1 |  | -2441.24253197 | 0.9204 | 81 | [0] | 1 (0) |
| [nc_pbe_bulk_e100](sheets/nc_pbe_bulk_e100.md) | NC PBE bulk single point at 100 Ry (cutoff check of the NC set). | scf.out | v.7.3.1 | 1 GPU(s), NVIDIA H100 NVL, 95830 MiB | 40 | {'In': 16, 'O': 24} | 100.0000  Ry | 4 | fixed | 1 |  | -2441.24853882 | 0.9203 | 80 | [0] | 0 (0) |
| [nc_pbe_slab1_e80](sheets/nc_pbe_slab1_e80.md) | NC PBE single point of the relaxed 1 nm slab, 80 Ry. | scf.out | v.7.3.1 | 1 GPU(s), NVIDIA H100 NVL, 95830 MiB | 96 | {'H': 24, 'In': 24, 'O': 48} | 80.0000  Ry | 4 | fixed | 1 |  | -4073.90318614 | 1.8068 | 380 | [0] | 1 (0) |
| [nc_hse_bulk_e80](sheets/nc_hse_bulk_e80.md) | HSE06 bulk single point (NC, 80 Ry, EXX q 1x1x1, default ecutfock). | scf.out | v.7.3.1 | 1 GPU(s), NVIDIA H100 NVL, 95830 MiB | 40 | {'In': 16, 'O': 24} | 80.0000  Ry | 4 | fixed | 7 |  | -2430.30794454 | 2.108 | 2239 | [0] | 1 (0) |
| [nc_hse_bulk_f160_e80](sheets/nc_hse_bulk_f160_e80.md) | HSE06 bulk with ecutfock 160 Ry (ecutfock check). | scf.out | v.7.3.1 | 1 GPU(s), NVIDIA H100 NVL, 95830 MiB | 40 | {'In': 16, 'O': 24} | 80.0000  Ry | 4 | fixed | 7 |  | -2430.30794254 | 2.108 | 805 | [0] | 0 (0) |
| [nc_hse_bulk_q3_e80](sheets/nc_hse_bulk_q3_e80.md) | HSE06 bulk with EXX q 3x3x3 and default ecutfock (did not run to completion). | None | None | 1 GPU(s), NVIDIA H100 NVL, 95830 MiB | 40 | {'In': 16, 'O': 24} | None | None | fixed | None |  | None | None | 95 | [1] | 0 (0) |
| [nc_hse_bulk_q3_f160_e80](sheets/nc_hse_bulk_q3_f160_e80.md) | HSE06 bulk with EXX q 3x3x3 and ecutfock 160 Ry (q-sampling check). | scf.out | v.7.3.1 | 1 GPU(s), NVIDIA H100 NVL, 95830 MiB | 40 | {'In': 16, 'O': 24} | 80.0000  Ry | 4 | fixed | 7 |  | -2430.41903839 | 2.0662 | 15383 | [0] | 1 (0) |
| [nc_hse_slab1_e80](sheets/nc_hse_slab1_e80.md) | HSE06 1 nm slab, default ecutfock (stopped after the PBE pre-step). | scf.out | v.7.3.1 | 1 GPU(s), NVIDIA H100 NVL, 95830 MiB | 96 | {'H': 24, 'In': 24, 'O': 48} | 80.0000  Ry | 4 | fixed | 1 |  | -4073.90318614 | 1.8068 | 439 | [1] | 0 (0) |
| [nc_hse_slab1_f160_e80](sheets/nc_hse_slab1_f160_e80.md) | HSE06 1 nm slab, ecutfock 160 Ry (the slab HSE gap used for the ratio). | scf.out | v.7.3.1 | 1 GPU(s), NVIDIA H100 NVL, 95830 MiB | 96 | {'H': 24, 'In': 24, 'O': 48} | 80.0000  Ry | 4 | fixed | 8 |  | -4057.48873487 | 3.0475 | 14486 | [0] | 1 (0) |
| [slab2_relax_c2](sheets/slab2_relax_c2.md) | vc-relax (2Dxy) of the 2 nm slab on one H100 NVL (rerun after the lost slab2_relax_x1), fi | vcrelax.out | v.7.3.1 | 1 GPU(s), NVIDIA H100 NVL, 95830 MiB | 176 | {'H': 24, 'In': 56, 'O': 96} | 71.0000  Ry | 4 | fixed | 73 | n  72 scf cycles and  70 bfgs steps | -27035.66492694 | 1.2238 | 182892 | [0, 0, 0] | 15 (0) |
| [iwo_slab2_W24d_checkpoint](sheets/iwo_slab2_W24d_checkpoint.md) | EOS checkpoint of the 2 nm IWO slab relax (one H100 NVL): converged relax.out. | relax.out | v.7.3.1 | 1 GPU(s), NVIDIA H100 NVL, 95830 MiB | 176 | {'H': 24, 'In': 55, 'O': 96, 'W': 1} | 71.0000  Ry | 4 | Marzari-Vanderbilt smearing | 29 | n  29 scf cycles and  28 bfgs steps | -27385.20618748 | 2.3492 | None | [0] | 6 (0) |
| [slab2r_final_cpu_checkpoint](sheets/slab2r_final_cpu_checkpoint.md) | CPU cross-check SCF of the relaxed 2 nm slab with planar average; its bands step was held  | scf.out | v.7.5 | 24 CPUs | 176 | {'H': 24, 'In': 56, 'O': 96} | 71.0000  Ry | 4 | fixed | 1 |  | -27035.66492226 | 1.2239 | None | [0] | 6 (1) |
| [iwo_slab2_final_cpu](sheets/iwo_slab2_final_cpu.md) | Recovery CPU SCF + planar average + projwfc of the relaxed 2 nm IWO slab (conv_thr 1e-8, b | scf.out | v.7.5 | 33 CPUs | 176 | {'H': 24, 'In': 55, 'O': 96, 'W': 1} | 71.0000  Ry | 4 | Marzari-Vanderbilt smearing | 1 |  | -27385.20618325 | 2.3496 | 29327 | [0] | 4 (1) |
| [iwo_slab2_final_cpu_failed_pools](sheets/iwo_slab2_final_cpu_failed_pools.md) | First attempt of iwo_slab2_final_cpu: stopped after 60 s by an MPI pool error. | scf.out | v.7.5 | 33 CPUs | 176 | {'H': 24, 'In': 55, 'O': 96, 'W': 1} | None | None | fixed | 0 |  | None | None | 71 | [1] | 0 (0) |
| [slab2r_pdos_cpu](sheets/slab2r_pdos_cpu.md) | CPU SCF + planar average + projwfc of the relaxed 2 nm slab (surface-state check). | scf.out | v.7.5 | 24 CPUs | 176 | {'H': 24, 'In': 56, 'O': 96} | 71.0000  Ry | 4 | fixed | 1 |  | -27035.66492227 | 1.2238 | 38656 | [0] | 3 (0) |
| [slabL1_relax_gpu](sheets/slabL1_relax_gpu.md) | Superseded 0.51 nm slab relax (marker only; replaced by slabL1_relax_v2). | None | None | - | None | None | None | None | fixed | None |  | None | None | None | [] | 0 (0) |
| [slabL2_relax_gpu](sheets/slabL2_relax_gpu.md) | Superseded 0.75 nm slab relax (marker only; replaced by slabL2_relax_v2). | None | None | - | None | None | None | None | fixed | None |  | None | None | None | [] | 0 (0) |
| [slabL1_relax_v2](sheets/slabL1_relax_v2.md) | 0.51 nm slab (one cation plane): vc-relax, SCF, planar average, projwfc/PDOS, bands. | vcrelax.out | v.7.3.1 | 1 GPU(s), NVIDIA H100 NVL, 95830 MiB | 56 | {'H': 24, 'In': 8, 'O': 24} | 71.0000  Ry | 4 | fixed | 84 | n  83 scf cycles and  82 bfgs steps | -4315.41561801 | 3.1402 | 22374 | [0, 0, 0] | 0 (0) |
| [slabL2_relax_v2](sheets/slabL2_relax_v2.md) | 0.75 nm slab (two cation planes): vc-relax, SCF, planar average, projwfc/PDOS, bands. | vcrelax.out | v.7.3.1 | 1 GPU(s), NVIDIA H100 NVL, 95830 MiB | 76 | {'H': 24, 'In': 16, 'O': 36} | 71.0000  Ry | 4 | fixed | 80 | n  79 scf cycles and  78 bfgs steps | -8102.10627948 | 2.1985 | 45305 | [0, 0, 0] | 0 (0) |
| [live_snapshots](sheets/live_snapshots.md) | Laptop-side 15-min snapshots of the running 2 nm jobs (snapshot_jobs.sh): slab2_relax_c2 ( | slab2_relax_c2/vcrelax.out | v.7.3.1 | 1 GPU(s), NVIDIA H100 NVL, 95830 MiB | 176 | {'H': 24, 'In': 56, 'O': 96} | 71.0000  Ry | 4 | fixed | 73 | n  72 scf cycles and  70 bfgs steps | -27035.66492694 | 1.2238 | None | [0, None] | 6 (1) |
| [canary_ckpt_checkpoint](sheets/canary_ckpt_checkpoint.md) | Workflow test (toy 2-atom W cell): EOS checkpoint written during a relax. | relax.out | v.7.5 | 2 CPUs | 2 | {'W': 2} | 40.0000  Ry | 18 | Marzari-Vanderbilt smearing | 4 | n   4 scf cycles and   3 bfgs steps | -1520.5174993 | 22.2292 | None | [0] | 0 (0) |
| [canary_cont](sheets/canary_cont.md) | Workflow test (toy 3-atom W slab cell, 2Dxy vc-relax): continuation logic, with nstep = 3  | vcrelax.out | v.7.5 | 2 CPUs | 3 | {'W': 3} | 40.0000  Ry | 10 | Marzari-Vanderbilt smearing | 3 |  | -2280.40598587 | 8.3941 | 317 | [0] | 0 (0) |
| [canary_cont_c1](sheets/canary_cont_c1.md) | Workflow test: second segment of the continuation test (restarts from vcrelax_prev.in). | vcrelax.out | v.7.5 | 2 CPUs | 3 | {'W': 3} | 40.0000  Ry | 10 | Marzari-Vanderbilt smearing | 3 |  | -2280.40670604 | 8.4582 | 317 | [0] | 0 (0) |
| [canary_race](sheets/canary_race.md) | Workflow test: GPU half of a GPU/CPU twin race (toy W cell relax). | relax.out | v.7.3.1 | 1 GPU(s), NVIDIA H100 NVL, 95830 MiB | 2 | {'W': 2} | 40.0000  Ry | 18 | Marzari-Vanderbilt smearing | 4 | n   4 scf cycles and   3 bfgs steps | -1520.51749921 | 22.2292 | 119 | [0] | 0 (0) |
| [canary_race__cpu](sheets/canary_race__cpu.md) | Workflow test: CPU half of the twin race. | relax.out | v.7.5 | 2 CPUs | 2 | {'W': 2} | 40.0000  Ry | 18 | Marzari-Vanderbilt smearing | 4 | n   4 scf cycles and   3 bfgs steps | -1520.51749922 | 22.2292 | 136 | [0] | 0 (0) |
| [canary_stuck](sheets/canary_stuck.md) | Workflow test: a job that only sleeps 4500 s (stuck-job detection). | None | None | 2 CPUs | None | None | None | None | fixed | None |  | None | None | 4517 | [] | 0 (0) |
| [ckpt_write_test_checkpoint](sheets/ckpt_write_test_checkpoint.md) | EOS write test from lxplus (one text file). | None | None | - | None | None | None | None | fixed | None |  | None | None | None | [] | 0 (0) |
| [failed_20260927a](sheets/failed_20260927a.md) | First submission of 2026-09-27 (iwo_W8b, iwo_W24d, slab1_relax, slab2_relax, each fetched  | None | None | 32 CPUs | 80 | {'In': 31, 'O': 48, 'W': 1} | None | None | fixed | None |  | None | None | 19 | [1] | 0 (0) |

## Checks against RESULTS_LOG (all)

| run | quantity | re-derived | logged | reference | status |
|---|---|---|---|---|---|
| slab1_v15 | SCF iterations | 46 | 46 | RESULTS_LOG.md:713 | match |
| slab1_v15 | gap (eV) | 0.9586 | 0.9586 | RESULTS_LOG.md:713 | match |
| slab1_v15 | EA (eV) | 3.4331 | 3.4331 | RESULTS_LOG.md:713 | match |
| slab1_v15 | IP (eV) | 4.3917 | 4.3917 | RESULTS_LOG.md:713 | match |
| slab1_v25 | SCF iterations | 64 | 64 | RESULTS_LOG.md:714 | match |
| slab1_v25 | gap (eV) | 0.9586 | 0.9586 | RESULTS_LOG.md:714 | match |
| slab1_v25 | EA (eV) | 3.4332 | 3.4332 | RESULTS_LOG.md:714 | match |
| slab1_v25 | IP (eV) | 4.3918 | 4.3918 | RESULTS_LOG.md:714 | match |
| slab1_v35 | SCF iterations | 77 | 77 | RESULTS_LOG.md:715 | match |
| slab1_v35 | gap (eV) | 0.9586 | 0.9586 | RESULTS_LOG.md:715 | match |
| slab1_v35 | EA (eV) | 3.4331 | 3.4332 | RESULTS_LOG.md:715 | match |
| slab1_v35 | IP (eV) | 4.3918 | 4.3918 | RESULTS_LOG.md:715 | match |
| slab1_v35 | CPUs (driver) | 16 | 16 | RESULTS_LOG.md:694 | match |
| slab1_v35 | pools | 4 | 4 | RESULTS_LOG.md:694 | match |
| slab1_v35 | SCF wall (h) | 1.8 | 1.8 | RESULTS_LOG.md:694 | match |
| slab1_v35 | bands wall (h) | 1.483 | 1.4833 | RESULTS_LOG.md:694 | match |
| slab1_v35 | symmetry ops | 8 | 8 | RESULTS_LOG.md:695 | match |
| slab1_v35 | irreducible k | 4 | 4 | RESULTS_LOG.md:695 | match |
| slab1_v35 | VBM (eV) | -1.9695 | -1.9695 | RESULTS_LOG.md:698 | match |
| slab1_v35 | CBM (eV) | -1.0109 | -1.0109 | RESULTS_LOG.md:698 | match |
| slab1_v35 | E_vac (eV) | 2.42225 | 2.422 | RESULTS_LOG.md:699 | match |
| slab1_v15 | bands wall (h), logged range 13.7-13.9 | 13.9 | 13.8 | RESULTS_LOG.md:719 | match |
| slab1_v25 | bands wall (h), logged range 13.7-13.9 | 13.767 | 13.8 | RESULTS_LOG.md:719 | match |
| iwo_W8b | E relax k3 (Ry) | -15496.3476465985 | -15496.3476466 | RESULTS_LOG.md:666 | match |
| iwo_W24d | E relax k3 (Ry) | -15496.3666036746 | -15496.3666037 | RESULTS_LOG.md:666 | match |
| iwo_W8b | E SCF k4 (Ry) | -15496.34766084 | -15496.34766084 | RESULTS_LOG.md:667 | match |
| iwo_W24d | E SCF k4 (Ry) | -15496.36660308 | -15496.36660308 | RESULTS_LOG.md:667 | match |
| iwo_W8b | E spin k3 (Ry) | -15496.3493187 | -15496.3493187 | RESULTS_LOG.md:669 | match |
| iwo_W24d | E spin k3 (Ry) | -15496.36803594 | -15496.36803594 | RESULTS_LOG.md:669 | match |
| iwo_W8b | total magnetisation | 0.74 | 0.74 | RESULTS_LOG.md:669 | match |
| iwo_W24d | total magnetisation | 0.62 | 0.62 | RESULTS_LOG.md:669 | match |
| iwo_W8b | W-O mean (A) | 1.9716 | 1.972 | RESULTS_LOG.md:668 | match |
| iwo_W24d | W-O mean (A) | 1.9822 | 1.982 | RESULTS_LOG.md:668 | match |
| iwo_W8b_partial | E relax (Ry), part of dE 0.01896 | -15496.3476465985 | -15496.3476466 | RESULTS_LOG.md:687 | match |
| iwo_W24d_partial | E relax (Ry), part of dE 0.01896 | -15496.3666036746 | -15496.3666037 | RESULTS_LOG.md:687 | match |
| slab1_relax_gpu | BFGS steps (GPU) | 54 | 54 | RESULTS_LOG.md:645 | match |
| slab1_relax_gpu | GPU model | True | True | RESULTS_LOG.md:645 | match |
| cpu_relax_snapshots | CPU BFGS steps before the GPU (slab1) | 13 | 13 | RESULTS_LOG.md:645 | match |
| slab1_relax_gpu | final enthalpy (Ry) | -11888.8112257101 | -11888.81122571 | RESULTS_LOG.md:646 | match |
| slab1_relax_gpu | total force at convergence (Ry/bohr) | 0.006106 | 0.0061 | RESULTS_LOG.md:647 | match |
| slab1_relax_gpu | in-plane a (A) | 10.33643 | 10.336 | RESULTS_LOG.md:648 | match |
| slab1_relax_gpu | in-plane b (A) (last-digit rounding allowed) | 10.3345 | 10.335 | RESULTS_LOG.md:648 | match |
| slab1r_final_cpu | gap (eV) | 1.7885 | 1.7885 | RESULTS_LOG.md:652 | match |
| iwo_slab1_W24d_x1 | BFGS steps | 27 | 27 | RESULTS_LOG.md:611 | match |
| iwo_slab1_W24d_x1 | final energy (Ry) | -12238.2891089616 | -12238.28910896 | RESULTS_LOG.md:611 | match |
| iwo_slab1_W24d_x1 | W-O mean (A) (log: 1.880 x2, 1.907 x2, 2.212 x2) | 1.9996 | 1.9997 | RESULTS_LOG.md:615 | match |
| iwo_slab1_final_cpu | bands step rc | 161 | 161 | RESULTS_LOG.md:613 | match |
| nc_pbe_bulk_e80 | gap on SCF grid (eV) | 0.9204 | 0.9204 | RESULTS_LOG.md:599 | match |
| nc_pbe_slab1_e80 | gap on SCF grid (eV) | 1.8068 | 1.8068 | RESULTS_LOG.md:599 | match |
| nc_hse_bulk_e80 | HSE gap on SCF grid (eV) | 2.108 | 2.108 | RESULTS_LOG.md:600 | match |
| nc_hse_slab1_f160_e80 | HSE gap on SCF grid (eV) | 3.0475 | 3.0475 | RESULTS_LOG.md:600 | match |
| nc_hse_bulk_q3_f160_e80 | HSE gap q3 (eV), log -42 meV vs q1 | 2.0662 | 2.0662 | RESULTS_LOG.md:606 | match |
| slab2_relax_c2 | BFGS steps | 70 | 70 | RESULTS_LOG.md:556 | match |
| slab2_relax_c2 | SCF cycles | 72 | 72 | RESULTS_LOG.md:556 | match |
| slab2_relax_c2 | vc-relax wall (h) | 41.467 | 41.5 | RESULTS_LOG.md:556 | match |
| slab2_relax_c2 | final enthalpy (Ry) | -27035.6654809032 | -27035.66548 | RESULTS_LOG.md:557 | match |
| slab2_relax_c2 | total force at convergence (Ry/bohr) | 0.007154 | 0.0072 | RESULTS_LOG.md:558 | match |
| slab2_relax_c2 | in-plane a (A) | 10.31792 | 10.318 | RESULTS_LOG.md:559 | match |
| slab2_relax_c2 | in-plane b (A) (last-digit rounding allowed) | 10.30849 | 10.309 | RESULTS_LOG.md:559 | match |
| slab2_relax_c2 | H-H thickness (A) | 19.6233 | 19.62 | RESULTS_LOG.md:560 | match |
| slab2_relax_c2 | O-O thickness (A) | 18.2137 | 18.21 | RESULTS_LOG.md:560 | match |
| slab2_relax_c2 | final SCF wall (h) | 0.932 | 0.9333333333333333 | RESULTS_LOG.md:562 | match |
| slab2_relax_c2 | total job time (s) | 182892 | 182892 | RESULTS_LOG.md:546 | match |
| slab2_relax_c2 | bands wall (h) | 8.367 | 8.366666666666667 | RESULTS_LOG.md:546 | match |
| slab2_relax_c2 | gap (eV) | 1.2239 | 1.2239 | RESULTS_LOG.md:565 | match |
| slab2_relax_c2 | EA (eV) | 4.495 | 4.495 | RESULTS_LOG.md:566 | match |
| slab2_relax_c2 | IP (eV) | 5.7189 | 5.719 | RESULTS_LOG.md:566 | match |
| iwo_slab2_W24d_checkpoint | BFGS steps | 28 | 28 | RESULTS_LOG.md:533 | match |
| iwo_slab2_W24d_checkpoint | relax wall (h) | 16.817 | 16.816666666666666 | RESULTS_LOG.md:533 | match |
| iwo_slab2_W24d_checkpoint | final energy (Ry) | -27385.206187481 | -27385.206187481 | RESULTS_LOG.md:533 | match |
| iwo_slab2_W24d_checkpoint | max displacement (A) | 0.4256 | 0.43 | RESULTS_LOG.md:512 | match |
| iwo_slab2_W24d_checkpoint | W displacement (A) | 0.0942 | 0.09 | RESULTS_LOG.md:512 | match |
| iwo_slab2_W24d_checkpoint | W-O mean (A) | 1.9767 | 1.977 | RESULTS_LOG.md:512 | match |
| slab2r_final_cpu_checkpoint | CPUs (driver) | 24 | 24 | RESULTS_LOG.md:540 | match |
| slab2r_final_cpu_checkpoint | SCF wall (h) | 9.95 | 9.95 | RESULTS_LOG.md:540 | match |
| slab2r_final_cpu_checkpoint | SCF iterations | 70 | 70 | RESULTS_LOG.md:540 | match |
| slab2r_final_cpu_checkpoint | HOMO (eV) | 0.0474 | 0.0474 | RESULTS_LOG.md:540 | match |
| slab2r_final_cpu_checkpoint | LUMO (eV) | 1.2713 | 1.2713 | RESULTS_LOG.md:540 | match |
| slab2r_final_cpu_checkpoint | CPUs allocated / MPI ranks (driver, HTCondor and pw.x agree on 24; log 410 also says 24; the logged 16 is the request_cpus of cern_htcondor/jobs/gen_iwoslab2/jobs.txt:1, found 2026-10-14) | 24 | 16 | RESULTS_LOG.md:550 | DIFFERS (dated erratum 2026-10-14 in RESULTS_LOG) |
| live_snapshots | slab2_relax_c2 CPU twin: completed SCF (geometry) steps in its last snapshot (BFGS counter reached 1) | 2 | 2 | RESULTS_LOG.md:580 | match |
| live_snapshots | slab2r_final_cpu bands step pools (log -nk 4) | 4 | 4 | RESULTS_LOG.md:541 | match |
| iwo_slab2_final_cpu | HTCondor cluster of the run whose outputs are used (log: 12835131) | 12835211.0 | 12835131.0 | RESULTS_LOG.md:514 | DIFFERS (dated erratum 2026-10-14 in RESULTS_LOG) |
| iwo_slab2_final_cpu | CPUs allocated | 33 | 33 | RESULTS_LOG.md:514 | match |
| iwo_slab2_final_cpu | conv_thr (input) | 1e-08 | 1e-08 | RESULTS_LOG.md:515 | match |
| iwo_slab2_final_cpu | mixing_beta (input) | 0.1 | 0.1 | RESULTS_LOG.md:515 | match |
| slab2r_pdos_cpu | CPUs (driver) | 24 | 24 | RESULTS_LOG.md:459 | match |
| slab2r_pdos_cpu | pools | 2 | 2 | RESULTS_LOG.md:459 | match |
| slab2r_pdos_cpu | SCF wall (h) | 10.683 | 10.683333333333334 | RESULTS_LOG.md:459 | match |
| live_snapshots | iwo_slab2_W24d final-SCF snapshot: QE version (log: 7.5 CPU) | v.7.5 | v.7.5 | RESULTS_LOG.md:509 | match |
| live_snapshots | iwo_slab2_W24d final-SCF snapshot: MPI processes (log: 33) | 33 | 33 | RESULTS_LOG.md:509 | match |
| live_snapshots | iwo_slab2_W24d final SCF ran on the GPU? (scf.out GPU lines; node had an H100) | False | True | RESULTS_LOG.md:533 | DIFFERS (dated erratum 2026-10-14 in RESULTS_LOG) |
| live_snapshots | iwo_slab2_W24d final-SCF snapshot: SCF iterations reached (log: 86) | 86 | 86 | RESULTS_LOG.md:509 | match |
