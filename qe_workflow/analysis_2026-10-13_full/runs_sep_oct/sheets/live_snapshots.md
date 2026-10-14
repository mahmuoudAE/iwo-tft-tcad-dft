# live_snapshots

**Purpose.** Laptop-side 15-min snapshots of the running 2 nm jobs (snapshot_jobs.sh): slab2_relax_c2 (+CPU twin), slab2r_final_cpu (incl. the held bands step), slab2r_pdos_cpu, iwo_slab2_W24d (+CPU twin, incl. its killed final SCF), iwo_slab2_final_cpu.

Folder `cern_htcondor/results/live_snapshots`; data `runs_sep_oct/out/live_snapshots.json` (+ `live_snapshots_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| iwo_slab2_W24d/bands.in | 14275 | 4918ff71b32c65b5 | loose | pw_in |
| iwo_slab2_W24d/iwo_slab2_W24d_driver.log | 502 | fd7a15083a1b8ecc | loose | driver |
| iwo_slab2_W24d/relax.in | 8814 | 4dd1e733395b42a0 | loose | pw_in |
| iwo_slab2_W24d/relax.out | 2141372 | fc02251d513f4c03 | loose | pw_out |
| iwo_slab2_W24d/scf.in | 13468 | ae3d833bec3c1dec | loose | pw_in |
| iwo_slab2_W24d/scf.out | 94186 | 5b6c87a3f8b2a9f1 | loose | pw_out |
| iwo_slab2_W24d__cpu/iwo_slab2_W24d__cpu_driver.log | 282 | 941b0646a29dc502 | loose | driver |
| iwo_slab2_W24d__cpu/relax.in | 8814 | e305747db95008ce | loose | pw_in |
| iwo_slab2_W24d__cpu/relax.out | 21119 | 58a29d8d8a48d676 | loose | pw_out |
| iwo_slab2_final_cpu/iwo_slab2_final_cpu_driver.log | 278 | 39f0893b7dbc3398 | loose | driver |
| iwo_slab2_final_cpu/scf.in | 8721 | e7f85d86451d83e3 | loose | pw_in |
| iwo_slab2_final_cpu/scf.out | 97554 | 8885a06165e57e76 | loose | pw_out |
| slab2_relax_c2/avg_slab2_relax_c2.in | 40 | e1f1019078c6d006 | loose | avg_in |
| slab2_relax_c2/avg_slab2_relax_c2.out | 1385 | 2d28a9c785f509b6 | loose | avg_out |
| slab2_relax_c2/bands.in | 14223 | e8a86d0e59685626 | loose | pw_in |
| slab2_relax_c2/bands.out | 43873 | 40285b268b551aee | loose | pw_out |
| slab2_relax_c2/pp_slab2_relax_c2.in | 95 | dd1e8cd848541336 | loose | post_in |
| slab2_relax_c2/pp_slab2_relax_c2.out | 2366 | a6a3fb072a0ef827 | loose | pp_out |
| slab2_relax_c2/scf.in | 13391 | 67ca29f51c2f26dc | loose | pw_in |
| slab2_relax_c2/scf.out | 257899 | e271abc8511b18b6 | loose | pw_out |
| slab2_relax_c2/slab2_relax_c2_avg.dat | 138000 | 93db87f1927dba51 | loose | avg_dat |
| slab2_relax_c2/slab2_relax_c2_driver.log | 905 | 0bf8e956565604eb | loose | driver |
| slab2_relax_c2/vcrelax.in | 13565 | 9ebd7cc47ea9ab74 | loose | pw_in |
| slab2_relax_c2/vcrelax.out | 5253552 | 14c606ae09e594f5 | loose | pw_out |
| slab2_relax_c2/vcrelax_initial.in | 8812 | afbeea9e49456bd6 | loose | pw_in |
| slab2_relax_c2__cpu/slab2_relax_c2__cpu_driver.log | 284 | 0ef2b4162b42421c | loose | driver |
| slab2_relax_c2__cpu/vcrelax.in | 13565 | cb2384995629f0f0 | loose | pw_in |
| slab2_relax_c2__cpu/vcrelax.out | 179231 | ba455d7a131e5e1b | loose | pw_out |
| slab2_relax_c2__cpu/vcrelax_initial.in | 8812 | afbeea9e49456bd6 | loose | pw_in |
| slab2_relax_c2_vcrelax.out | 2891945 | 807172c7218f1646 | loose | pw_out |
| slab2r_final_cpu/avg_slab2r_final_cpu.in | 42 | 4b9100260b55383a | loose | avg_in |
| slab2r_final_cpu/avg_slab2r_final_cpu.out | 1309 | 719dbef0089b19b2 | loose | avg_out |
| slab2r_final_cpu/bands.in | 9450 | d2452ef2cfd1322a | loose | pw_in |
| slab2r_final_cpu/bands.out | 41413 | 75355da225d7105a | loose | pw_out |
| slab2r_final_cpu/pp_slab2r_final_cpu.in | 97 | 65409a62afe48642 | loose | post_in |
| slab2r_final_cpu/pp_slab2r_final_cpu.out | 2368 | 462646d445b93c72 | loose | pp_out |
| slab2r_final_cpu/scf.in | 8642 | 62dfca67b9e9ae24 | loose | pw_in |
| slab2r_final_cpu/scf.out | 240033 | f0024e861835313c | loose | pw_out |
| slab2r_final_cpu/slab2r_final_cpu_avg.dat | 138000 | 2c921d498e4c1e03 | loose | avg_dat |
| slab2r_final_cpu/slab2r_final_cpu_driver.log | 494 | 473ad6287e518c31 | loose | driver |
| slab2r_pdos_cpu/scf.in | 8642 | 62dfca67b9e9ae24 | loose | pw_in |
| slab2r_pdos_cpu/scf.out | 236092 | fdfc3ddc2e6d3dac | loose | pw_out |
| slab2r_pdos_cpu/slab2r_pdos_cpu_driver.log | 274 | b336a8801d3d4110 | loose | driver |
| snapshots.log | 43584 | fe9deb46e2d3b626 | loose | other |

## Resources and run history

- `iwo_slab2_W24d/iwo_slab2_W24d_driver.log`: host b9pgpun003.cern.ch, 33 CPUs, wall limit 259200 s, GPU: 1 GPU(s), NVIDIA H100 NVL, 95830 MiB, job total None s, start 2026-10-04T13:52:08Z
  - step relax: -nk 1, max_seconds 257378, start 2026-10-04T13:52:30Z, end 2026-10-05T06:42:35Z, rc 0, PWSCF        :     16h39m CPU     16h49m WALL
  - step scf: -nk 1, max_seconds 196772, start 2026-10-05T06:42:36Z, end None, rc None, 
- `iwo_slab2_W24d__cpu/iwo_slab2_W24d__cpu_driver.log`: host b9p06p1809.cern.ch, 16 CPUs, wall limit 259200 s, GPU: none (CPU), job total None s, start 2026-10-04T13:35:02Z
  - step relax: -nk 1, max_seconds 257389, start 2026-10-04T13:35:13Z, end None, rc None, 
- `iwo_slab2_final_cpu/iwo_slab2_final_cpu_driver.log`: host b9p06p6732.cern.ch, 33 CPUs, wall limit 86400 s, GPU: none (CPU), job total None s, start 2026-10-05T16:22:27Z
  - step scf: -nk 1, max_seconds 84591, start 2026-10-05T16:22:36Z, end None, rc None, 
- `slab2_relax_c2/slab2_relax_c2_driver.log`: host b9pgpun501.cern.ch, 33 CPUs, wall limit 259200 s, GPU: 1 GPU(s), NVIDIA H100 NVL, 95830 MiB, job total None s, start 2026-10-02T07:12:04Z
  - step vcrelax: -nk 2, max_seconds 257382, start 2026-10-02T07:12:22Z, end 2026-10-04T00:40:42Z, rc 0, PWSCF        :   1d16h53m CPU   1d17h28m WALL
  - step scf: -nk 2, max_seconds 108080, start 2026-10-04T00:40:44Z, end 2026-10-04T01:36:44Z, rc 0, PWSCF        :  46m31.63s CPU  55m55.64s WALL
  - step bands: -nk 2, max_seconds 104693, start 2026-10-04T01:37:11Z, end None, rc None, 
  - log: tmp/slab.save/charge-density.hdf5: ngm_g 7413139, nspin 1, gamma_only False, first G [0, 0, 0], rho(G) 0.04095077
  - log: [2026-10-04T01:36:48Z] charge density converted to HDF5 for pp.x
  - log: [2026-10-04T01:37:11Z] planar average slab2_relax_c2: 3000 lines
- `slab2_relax_c2__cpu/slab2_relax_c2__cpu_driver.log`: host b9p08p3507.cern.ch, 16 CPUs, wall limit 259200 s, GPU: none (CPU), job total None s, start 2026-10-02T02:46:17Z
  - step vcrelax: -nk 2, max_seconds 257389, start 2026-10-02T02:46:28Z, end None, rc None, 
- `slab2r_final_cpu/slab2r_final_cpu_driver.log`: host b9p12p6312.cern.ch, 24 CPUs, wall limit 86400 s, GPU: none (CPU), job total None s, start 2026-10-04T13:35:02Z
  - step scf: -nk 2, max_seconds 84590, start 2026-10-04T13:35:12Z, end 2026-10-04T23:33:18Z, rc 0, PWSCF        :      9h36m CPU      9h57m WALL
  - step bands: -nk 4, max_seconds 48669, start 2026-10-04T23:33:53Z, end None, rc None, 
  - log: [2026-10-04T23:33:52Z] planar average slab2r_final_cpu: 3000 lines
- `slab2r_pdos_cpu/slab2r_pdos_cpu_driver.log`: host b9p04p4241.cern.ch, 24 CPUs, wall limit 86400 s, GPU: none (CPU), job total None s, start 2026-10-05T07:35:30Z
  - step scf: -nk 2, max_seconds 84590, start 2026-10-05T07:35:40Z, end None, rc None, 
- HTCondor slab2_relax 12757723.1: 32 CPUs, None GPU; seen 2026-09-28T14:19:54Z to 2026-09-28T18:34:13Z (28 samples); states {'2': 28} (1 idle, 2 running, 3 removed, 5 held); max scf_it 62, max BFGS 0; steps ['vcrelax']; hw  ['Intel(R) Xeon(R) CPU E5-2650 v4 @ 2.20GHz']
- HTCondor slab2_relax_gpu 12759677.1: 21 CPUs, None GPU; seen 2026-09-28T15:17:28Z to 2026-09-28T17:42:31Z (15 samples); states {'1': 15} (1 idle, 2 running, 3 removed, 5 held); max scf_it 0, max BFGS 0; steps []; hw  
- HTCondor slab2_relax_gpu1 12759802.0: 16 CPUs, None GPU; seen 2026-09-28T17:52:51Z to 2026-09-28T17:52:51Z (1 samples); states {'1': 1} (1 idle, 2 running, 3 removed, 5 held); max scf_it 0, max BFGS 0; steps []; hw  
- HTCondor slab2_relax_gpu1 12759807.0: 16 CPUs, None GPU; seen 2026-09-28T18:03:11Z to 2026-09-29T03:15:24Z (83 samples); states {'1': 4, '2': 79} (1 idle, 2 running, 3 removed, 5 held); max scf_it 0, max BFGS 0; steps ['vcrelax']; hw ['', '1xNVIDIA H100 NVL|0%'] ['', 'Intel(R) Xeon(R) Platinum 8468']
- HTCondor slab2_relax_gpu1 12772910.0: 21 CPUs, 1 GPU; seen 2026-09-29T09:05:18Z to 2026-09-29T12:04:51Z (34 samples); states {'1': 34} (1 idle, 2 running, 3 removed, 5 held); max scf_it 0, max BFGS 0; steps []; hw  
- HTCondor slab2_relax_gpu1 12773048.0: 32 CPUs, 0 GPU; seen 2026-09-29T12:11:04Z to 2026-09-30T00:54:38Z (145 samples); states {'1': 1, '2': 144} (1 idle, 2 running, 3 removed, 5 held); max scf_it 275, max BFGS 3; steps ['vcrelax']; hw  ['AMD EPYC 9655 96-Core Processor']
- HTCondor slab2_relax_gpu8 12783002.0: 11 CPUs, 1 GPU; seen 2026-09-30T00:01:40Z to 2026-09-30T05:07:14Z (43 samples); states {'1': 10, '2': 31, '3': 2} (1 idle, 2 running, 3 removed, 5 held); max scf_it 0, max BFGS 0; steps ['vcrelax']; hw ['', '1xNVIDIA H100 NVL|0%'] ['', 'Intel(R) Xeon(R) Platinum 8468']
- HTCondor slab2_relax_gpu8 12786255.0: 11 CPUs, 1 GPU; seen 2026-09-30T05:12:31Z to 2026-09-30T08:01:49Z (31 samples); states {'1': 31} (1 idle, 2 running, 3 removed, 5 held); max scf_it 0, max BFGS 0; steps []; hw  
- HTCondor slab2_relax_x2 12786472.0: 21 CPUs, 2 GPU; seen 2026-09-30T06:00:39Z to 2026-09-30T08:01:49Z (22 samples); states {'1': 22} (1 idle, 2 running, 3 removed, 5 held); max scf_it 0, max BFGS 0; steps []; hw  
- HTCondor slab2_relax_x4 12786473.0: 42 CPUs, 4 GPU; seen 2026-09-30T06:00:39Z to 2026-09-30T08:01:49Z (22 samples); states {'1': 22} (1 idle, 2 running, 3 removed, 5 held); max scf_it 0, max BFGS 0; steps []; hw  
- HTCondor slab2_relax_gpu8 12786699.0: 16 CPUs, 0 GPU; seen 2026-09-30T09:23:28Z to 2026-09-30T11:39:51Z (26 samples); states {'2': 26} (1 idle, 2 running, 3 removed, 5 held); max scf_it 19, max BFGS 0; steps ['vcrelax']; hw  ['AMD EPYC 7302 16-Core Processor']
- HTCondor slab2_relax_x1 12788377.0: 11 CPUs, 1 GPU; seen 2026-09-30T11:01:18Z to 2026-10-02T02:34:08Z (414 samples); states {'1': 8, '2': 406} (1 idle, 2 running, 3 removed, 5 held); max scf_it 3408, max BFGS 69; steps ['vcrelax', 'scf']; hw ['1xNVIDIA H100 NVL|0%', '1xNVIDIA H100 NVL|10%', '1xNVIDIA H100 NVL|100%', '1xNVIDIA H100 NVL|11%', '1xNVIDIA H100 NVL|12%', '1xNVIDIA H100 NVL|13%', '1xNVIDIA H100 NVL|14%', '1xNVIDIA H100 NVL|16%', '1xNVIDIA H100 NVL|17%', '1xNVIDIA H100 NVL|18%', '1xNVIDIA H100 NVL|20%', '1xNVIDIA H100 NVL|21%', '1xNVIDIA H100 NVL|25%', '1xNVIDIA H100 NVL|26%', '1xNVIDIA H100 NVL|28%', '1xNVIDIA H100 NVL|31%', '1xNVIDIA H100 NVL|34%', '1xNVIDIA H100 NVL|37%', '1xNVIDIA H100 NVL|4%', '1xNVIDIA H100 NVL|40%', '1xNVIDIA H100 NVL|44%', '1xNVIDIA H100 NVL|48%', '1xNVIDIA H100 NVL|5%', '1xNVIDIA H100 NVL|65%', '1xNVIDIA H100 NVL|71%', '1xNVIDIA H100 NVL|72%', '1xNVIDIA H100 NVL|73%', '1xNVIDIA H100 NVL|8%', '1xNVIDIA H100 NVL|80%', '1xNVIDIA H100 NVL|81%', '1xNVIDIA H100 NVL|83%', '1xNVIDIA H100 NVL|9%', '1xNVIDIA H100 NVL|93%', '1xNVIDIA H100 NVL|94%', '1xNVIDIA H100 NVL|95%', '1xNVIDIA H100 NVL|96%', '1xNVIDIA H100 NVL|97%', '1xNVIDIA H100 NVL|98%', '1xNVIDIA H100 NVL|99%'] ['Intel(R) Xeon(R) Platinum 8468']
- HTCondor slab2_relax_c2 12806569.0: 33 CPUs, 1 GPU; seen 2026-10-02T02:41:56Z to 2026-10-04T09:57:26Z (311 samples); states {'1': 10, '2': 301} (1 idle, 2 running, 3 removed, 5 held); max scf_it 3611, max BFGS 69; steps ['vcrelax', 'scf', 'bands']; hw ['1xNVIDIA H100 NVL|0%', '1xNVIDIA H100 NVL|10%', '1xNVIDIA H100 NVL|100%', '1xNVIDIA H100 NVL|11%', '1xNVIDIA H100 NVL|12%', '1xNVIDIA H100 NVL|13%', '1xNVIDIA H100 NVL|15%', '1xNVIDIA H100 NVL|16%', '1xNVIDIA H100 NVL|19%', '1xNVIDIA H100 NVL|28%', '1xNVIDIA H100 NVL|32%', '1xNVIDIA H100 NVL|33%', '1xNVIDIA H100 NVL|36%', '1xNVIDIA H100 NVL|4%', '1xNVIDIA H100 NVL|5%', '1xNVIDIA H100 NVL|6%', '1xNVIDIA H100 NVL|7%', '1xNVIDIA H100 NVL|71%', '1xNVIDIA H100 NVL|72%', '1xNVIDIA H100 NVL|73%', '1xNVIDIA H100 NVL|74%', '1xNVIDIA H100 NVL|75%', '1xNVIDIA H100 NVL|76%', '1xNVIDIA H100 NVL|77%', '1xNVIDIA H100 NVL|78%', '1xNVIDIA H100 NVL|79%', '1xNVIDIA H100 NVL|8%', '1xNVIDIA H100 NVL|82%', '1xNVIDIA H100 NVL|9%', '1xNVIDIA H100 NVL|92%', '1xNVIDIA H100 NVL|93%', '1xNVIDIA H100 NVL|94%', '1xNVIDIA H100 NVL|96%', '1xNVIDIA H100 NVL|97%', '1xNVIDIA H100 NVL|98%', '1xNVIDIA H100 NVL|99%'] ['Intel(R) Xeon(R) Platinum 8468']
- HTCondor slab2_relax_c2__cpu 12806569.1: 16 CPUs, 0 GPU; seen 2026-10-02T02:41:56Z to 2026-10-03T06:14:29Z (11 samples); states {'1': 1, '2': 10} (1 idle, 2 running, 3 removed, 5 held); max scf_it 141, max BFGS 1; steps ['vcrelax']; hw  ['AMD EPYC 7543 32-Core Processor']
- HTCondor slab2r_final_cpu 12827176.0: 24 CPUs, 0 GPU; seen 2026-10-04T13:39:30Z to 2026-10-05T07:29:53Z (192 samples); states {'2': 108, '5': 84} (1 idle, 2 running, 3 removed, 5 held); max scf_it 70, max BFGS 0; steps ['scf', 'bands']; hw  ['AMD EPYC 7543 32-Core Processor']
- HTCondor iwo_slab2_W24d 12827176.1: 33 CPUs, 1 GPU; seen 2026-10-04T13:39:30Z to 2026-10-05T09:22:51Z (212 samples); states {'1': 3, '2': 209} (1 idle, 2 running, 3 removed, 5 held); max scf_it 1550, max BFGS 27; steps ['relax', 'scf']; hw ['', '1xNVIDIA H100 NVL|0%', '1xNVIDIA H100 NVL|1%', '1xNVIDIA H100 NVL|10%', '1xNVIDIA H100 NVL|100%', '1xNVIDIA H100 NVL|11%', '1xNVIDIA H100 NVL|12%', '1xNVIDIA H100 NVL|13%', '1xNVIDIA H100 NVL|14%', '1xNVIDIA H100 NVL|16%', '1xNVIDIA H100 NVL|17%', '1xNVIDIA H100 NVL|18%', '1xNVIDIA H100 NVL|26%', '1xNVIDIA H100 NVL|4%', '1xNVIDIA H100 NVL|48%', '1xNVIDIA H100 NVL|5%', '1xNVIDIA H100 NVL|57%', '1xNVIDIA H100 NVL|58%', '1xNVIDIA H100 NVL|6%', '1xNVIDIA H100 NVL|60%', '1xNVIDIA H100 NVL|8%', '1xNVIDIA H100 NVL|88%', '1xNVIDIA H100 NVL|9%', '1xNVIDIA H100 NVL|93%', '1xNVIDIA H100 NVL|94%', '1xNVIDIA H100 NVL|95%', '1xNVIDIA H100 NVL|96%', '1xNVIDIA H100 NVL|97%', '1xNVIDIA H100 NVL|98%', '1xNVIDIA H100 NVL|99%'] ['', 'Intel(R) Xeon(R) Platinum 8468']
- HTCondor iwo_slab2_W24d__cpu 12827176.2: 16 CPUs, 0 GPU; seen 2026-10-04T13:39:30Z to 2026-10-04T13:56:27Z (4 samples); states {'2': 4} (1 idle, 2 running, 3 removed, 5 held); max scf_it 3, max BFGS 0; steps ['relax']; hw  ['AMD EPYC 7543 32-Core Processor']
- HTCondor slab2r_pdos_cpu 12834125.0: 24 CPUs, 0 GPU; seen 2026-10-05T07:35:29Z to 2026-10-05T18:15:25Z (89 samples); states {'2': 89} (1 idle, 2 running, 3 removed, 5 held); max scf_it 76, max BFGS 0; steps ['scf']; hw [''] ['', 'AMD EPYC 7543 32-Core Processor']
- HTCondor iwo_slab2_final_cpu 12835131.0: 33 CPUs, 0 GPU; seen 2026-10-05T12:50:54Z to 2026-10-05T12:50:54Z (1 samples); states {'1': 1} (1 idle, 2 running, 3 removed, 5 held); max scf_it 0, max BFGS 0; steps []; hw  
- HTCondor iwo_slab2_final_cpu 12835211.0: 33 CPUs, 0 GPU; seen 2026-10-05T16:20:34Z to 2026-10-06T00:25:53Z (84 samples); states {'1': 1, '2': 83} (1 idle, 2 running, 3 removed, 5 held); max scf_it 91, max BFGS 0; steps ['scf']; hw  ['AMD EPYC 7543 32-Core Processor']

**What failed and why (from the files above).** Snapshots of running jobs: incomplete outputs are expected (no JOB DONE). The iwo_slab2_W24d final SCF (QE 7.5 CPU build: steps.sh exports FORCE_CPU=1 before it; 33 ranks on the H100 node; no GPU line in scf.out) stops at iteration 86 with the accuracy at 8e-9 to 1e-8 Ry: it was removed by the faulty stuck rule (RESULTS_LOG 2026-10-05). The slab2r_final_cpu bands step (-nk 4) stops early: held for memory.

## Calculation `iwo_slab2_W24d/relax.out` (scf/relax)

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

**Final geometry** (vs `iwo_slab2_W24d/relax.in`): {"n_atoms": 176, "composition": {"H": 24, "In": 55, "O": 96, "W": 1}, "cell_lengths_A": [10.31792, 10.30849, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5089, "density_g_cm3": 2.7848, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 330, "min": 2.1292, "mean": 2.2283, "max": 2.5046, "std": 0.0617, "CN_In_hist": {"6": 55}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 1.8665, "mean": 1.9767, "max": 2.1897, "std": 0.1506, "CN_W_hist": {"6": 1}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9725, "mean": 0.9779, "max": 0.987, "std": 0.0063, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.458, "extent_A": 19.722, "thickness_H_H_A": 19.7222, "thickness_O_O_A": 18.2838, "thickness_In_In_A": 15.5749, "thickness_W_W_A": 0.0}, "displacement_vs_initial": {"max_A": 0.4256, "atom": "O97", "mean_A": 0.0486, "n_gt_0p1_A": 10, "by_element_max_A": {"H": 0.0635, "In": 0.1014, "O": 0.4256, "W": 0.0942}, "outer_3A_mean_A": 0.033, "interior_mean_A": 0.0575}, "reference_input": "iwo_slab2_W24d/relax.in"}

**Warnings/errors**: message_from_routine x1 (first: line 30 'Message from routine setup:'); warning x4 (first: line 10128 'WARNING: bfgs curvature condition failed, Theta= 0.982'); c_bands_not_converged x28 (first: line 391 'c_bands:  3 eigenvalues not converged'); ieee x3 (first: line 39719 'Warning: ieee_invalid is signaling'); discouraged x1 (first: line 31 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x4 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized'); fortran_stop x1 (first: line 39722 'FORTRAN STOP')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized']

## Calculation `iwo_slab2_W24d/scf.out` (scf/relax)

QE v.7.5 started 5Oct2026 8:42:37; 33 MPI x 1 threads on 1 node(s); pools 1; R&G division 33; node memory 264967.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: NO (no JOB DONE); terminated None; PWSCF time None; output lines 2069.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 196772
- &SYSTEM: ibrav = 0, nat = 176, ntyp = 4, ecutwfc = 71, ecutrho = 568, occupations = smearing, smearing = mv, degauss = 0.01, nbnd = 688
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "W", "mass": 183.84, "pseudo": "W.pbe-spn-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.31791632, 0.0, 0.0], [0.0, 10.30849134, 0.0], [0.0, 0.0, 45.18062913]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 176, "labels": ["H", "In", "O", "W"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4980  a.u.; unit-cell volume = 32429.1815 (a.u.)^3; number of atoms/cell = 176; number of atomic types = 4; number of electrons = 1329.00; number of Kohn-Sham states = 688; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.498036, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); W W.pbe-spn-kjpaw_psl.1.0.0.UPF md5 03c3df5b60893f488392c7401945500a (Projector augmented-wave + core cor, Z 14.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 2 Sym. Ops. (no inversion) found ( 1 have fractional translation); k points: number of k points=     4  Marzari-Vanderbilt smearing, width (Ry)=  0.0100 (sum of weights 2.0); FFT: Dense  grid:  7413139 G-vectors     FFT dimensions: ( 150, 150, 648) / Smooth grid:  2620949 G-vectors     FFT dimensions: ( 108, 108, 480)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '893.92 MB', 'Estimated max dynamical RAM per process': '2.51 GB', 'Estimated total dynamical RAM': '82.78 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge    1328.7946, renormalised to    1329.0000', 'Starting wfcs are  916 randomized atomic wfcs']

**Convergence** (1 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 86 | None | None |  |  |  |  |  |  |  |  |  |

**Final energies** (last SCF): negative_rho = [0.0459, 0.0]

**Warnings/errors**: message_from_routine x1 (first: line 30 'Message from routine setup:'); c_bands_not_converged x8 (first: line 753 'c_bands:  1 eigenvalues not converged'); discouraged x1 (first: line 31 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x4 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized']

## Calculation `iwo_slab2_W24d__cpu/relax.out` (scf/relax)

QE v.7.5 started 4Oct2026 15:35:14; 16 MPI x 1 threads on 1 node(s); pools 1; R&G division 16; node memory 88774.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: NO (no JOB DONE); terminated None; PWSCF time None; output lines 361.

**Input settings** (every namelist variable):

- &CONTROL: calculation = relax, prefix = rel, outdir = ./tmp, pseudo_dir = ./, verbosity = low, tprnfor = .true., tstress = .true., max_seconds = 257389, nstep = 300, etot_conv_thr = 1.0d-4, forc_conv_thr = 1.0d-3
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
- RAM (pw.x estimate): {'Estimated max dynamical RAM per process': '5.15 GB', 'Estimated total dynamical RAM': '82.38 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge    1328.7946, renormalised to    1329.0000', 'Starting wfcs are  916 randomized atomic wfcs']

**Convergence** (1 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 1 | None | None |  |  |  |  |  |  |  |  |  |

**Final energies** (last SCF): 

**Warnings/errors**: message_from_routine x1 (first: line 30 'Message from routine setup:'); discouraged x1 (first: line 31 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x4 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized']

## Calculation `iwo_slab2_final_cpu/scf.out` (scf/relax)

QE v.7.5 started 5Oct2026 18:22:37; 33 MPI x 1 threads on 1 node(s); pools 1; R&G division 33; node memory 153915.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: NO (no JOB DONE); terminated None; PWSCF time None; output lines 2155.

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
| 0 | 91 | None | None |  |  |  |  |  |  |  |  |  |

**Final energies** (last SCF): negative_rho = [0.04599, 0.0]

**Warnings/errors**: message_from_routine x1 (first: line 30 'Message from routine setup:'); c_bands_not_converged x9 (first: line 923 'c_bands:  1 eigenvalues not converged'); discouraged x1 (first: line 31 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x4 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file W.pbe-spn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  6S 5P 5D renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized']

## Calculation `slab2_relax_c2/bands.out` (bands)

QE v.7.3.1 started 4Oct2026 3:37:13; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 151093.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled; GPU used by master process:. Completed: NO (no JOB DONE); terminated None; PWSCF time None; output lines 760.

**Input settings** (every namelist variable):

- &CONTROL: calculation = bands, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 104693
- &SYSTEM: ibrav = 0, nat = 176, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 680
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF, diagonalization = cg
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.317916322, 0.0, 0.0], [0.0, 10.308491343, 0.0], [0.0, 0.0, 45.18062913]]}
- K_POINTS: {"mode": "tpiba", "n": 21, "points_first_last": [[0.0, 0.0, 0.0, 1.0], [0.1739764, 0.1739764, 0.0, 1.0]], "path_points": [[0.0, 0.0, 0.0, 1.0], [0.02460398, 0.0, 0.0, 1.0], [0.04920796, 0.0, 0.0, 1.0], [0.07381193, 0.0, 0.0, 1.0], [0.09841591, 0.0, 0.0, 1.0], [0.12301989, 0.0, 0.0, 1.0], [0.14762387, 0.0, 0.0, 1.0], [0.17222785, 0.0, 0.0, 1.0], [0.19683182, 0.0, 0.0, 1.0], [0.2214358, 0.0, 0.0, 1.
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 176, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4980  a.u.; unit-cell volume = 32429.1815 (a.u.)^3; number of atoms/cell = 176; number of atomic types = 3; number of electrons = 1328.00; number of Kohn-Sham states = 680; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.498036, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=    21 (sum of weights 2.0); FFT: Dense  grid:  7413139 G-vectors     FFT dimensions: ( 150, 150, 648) / Smooth grid:  2620949 G-vectors     FFT dimensions: ( 108, 108, 480)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '14.64 GB', 'Estimated max dynamical RAM per process': '45.79 GB'}; start: ['Starting wfcs are  912 randomized atomic wfcs']
- Band-structure run: {'diag': 'CG style diagonalization', 'kpts_done': 21}

**Warnings/errors**: message_from_routine x1 (first: line 34 'Message from routine setup:'); warning x1 (first: line 1 'WARNING: Skipping mount /tmp [tmp]: /tmp doesn't exist in container'); c_bands_not_converged x20 (first: line 681 'c_bands: 11 eigenvalues not converged'); discouraged x1 (first: line 35 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 27 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Calculation `slab2_relax_c2/scf.out` (scf/relax)

QE v.7.3.1 started 4Oct2026 2:40:46; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 108583.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled; GPU used by master process:. Completed: JOB DONE; terminated 3:36:41   4Oct2026; PWSCF time {'cpu': '46m31.63s', 'wall': '55m55.64s', 'calls': None}; output lines 4283.

**Input settings** (every namelist variable):

- &CONTROL: calculation = scf, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 108080
- &SYSTEM: ibrav = 0, nat = 176, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 680
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.317916322, 0.0, 0.0], [0.0, 10.308491343, 0.0], [0.0, 0.0, 45.18062913]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 176, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4980  a.u.; unit-cell volume = 32429.1815 (a.u.)^3; number of atoms/cell = 176; number of atomic types = 3; number of electrons = 1328.00; number of Kohn-Sham states = 680; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.498036, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  7413139 G-vectors     FFT dimensions: ( 150, 150, 648) / Smooth grid:  2620949 G-vectors     FFT dimensions: ( 108, 108, 480)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '28.14 GB', 'Estimated max dynamical RAM per process': '82.10 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge    1327.7914, renormalised to    1328.0000', 'Starting wfcs are  912 randomized atomic wfcs']

**Convergence** (1 SCF):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 75 | 7.5e-10 | -27035.66492689 |  | 0.0008609 | 0.000311 | 0.007153 | 0.000103 | -0.4 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.002107, 0.0], HOMO_eV = 0.0473, LUMO_eV = 1.2712, E_Ry = -27035.66492689, E_all_electron_Ry = -673235.702643, acc_final_Ry = 7.5e-10, one_electron_Ry = -272838.07837541, hartree_Ry = 137216.09044251, xc_Ry = -3329.72167443, ewald_Ry = 128104.25303152, paw_one_center_Ry = -16188.20835107, converged_iterations = 75
- stress tensor (kbar): [[0.1, 0.0, 0.0], [0.0, 0.16, 0.0], [0.0, 0.0, -1.46]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 680, "n_occ": 664, "VBM_eV": 0.0473, "VBM_k_index": 0, "CBM_eV": 1.2712, "CBM_k_index": 0, "gap_eV": 1.2239, "direct_gap_min_eV": 1.2239, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.0135, "CB_width_bottom_band_eV": 1.0517, "E2_minus_E1_at_k0_eV": 0.7192}

**Warnings/errors**: message_from_routine x1 (first: line 30 'Message from routine setup:'); warning x4 (first: line 1 'WARNING: Skipping mount /tmp [tmp]: /tmp doesn't exist in container'); c_bands_not_converged x2 (first: line 865 'c_bands:  1 eigenvalues not converged'); ieee x3 (first: line 4280 'Warning: ieee_invalid is signaling'); discouraged x1 (first: line 31 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 27 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized'); fortran_stop x1 (first: line 4283 'FORTRAN STOP')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Calculation `slab2_relax_c2/vcrelax.out` (scf/relax)

QE v.7.3.1 started 2Oct2026 9:12:24; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 37861.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled; GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled. Completed: JOB DONE; terminated 2:40:25   4Oct2026; PWSCF time {'cpu': '1d16h53m', 'wall': '1d17h28m', 'calls': None}; output lines 96366.

**Input settings** (every namelist variable):

- &CONTROL: calculation = vc-relax, prefix = vcr, outdir = ./tmp, pseudo_dir = ./, verbosity = low, tprnfor = .true., tstress = .true., max_seconds = 257382, nstep = 300, etot_conv_thr = 1.0d-4, forc_conv_thr = 1.0d-3
- &SYSTEM: ibrav = 0, nat = 176, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 672
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- &IONS: ion_dynamics = bfgs
- &CELL: cell_dynamics = bfgs, cell_dofree = 2Dxy, press_conv_thr = 0.5
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.328080023, 0.0, 0.0], [0.0, 10.325066496, 0.0], [0.0, 0.0, 45.18062913]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 176, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.5172  a.u.; unit-cell volume = 32513.3206 (a.u.)^3; number of atoms/cell = 176; number of atomic types = 3; number of electrons = 1328.00; number of Kohn-Sham states = 672; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; energy convergence thresh. = 1.0E-04; force convergence thresh. = 1.0E-03; press convergence thresh. = 5.0E-01; Exchange-correlation = SLA  PW   PBX  PBC; nstep = 300; celldm = [19.517243, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0) (re-read 3 times in the final SCF)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  7413139 G-vectors     FFT dimensions: ( 150, 150, 648) / Smooth grid:  2620949 G-vectors     FFT dimensions: ( 108, 108, 480)
- RAM (pw.x estimate): {'Estimated max dynamical RAM per process': '82.07 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge    1327.7914, renormalised to    1328.0000', 'Starting wfcs are  912 randomized atomic wfcs', 'Initial potential from superposition of free atoms', 'starting charge    1327.7914, renormalised to    1328.0000', 'Starting wfcs are  912 randomized atomic wfcs']

**Convergence** (73 SCF + BFGS): bfgs converged in  72 scf cycles and  70 bfgs steps (criteria: energy <  1.0E-04 Ry, force <  1.0E-03 Ry/Bohr, cell <  5.0E-01 kbar) final energy None final enthalpy -27035.6654809032 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 93 | 4.7e-10 | -27035.26282772 | -27035.2628277204 | 0.02143 | 0.00596 | 0.137062 | 8.5e-05 | -2.68 | 4819.17263 | 10.3291, 10.3266 | 0.02483 |
| 1 | 47 | 7.8e-10 | -27035.27774175 | -27035.277741752 | 0.01201 | 0.00431 | 0.098965 | 7.9e-05 | -2.86 | 4820.11372 | 10.3299, 10.3278 | 0.02731 |
| 2 | 52 | 1e-10 | -27035.29081595 | -27035.2908159487 | 0.01049 | 0.00363 | 0.083508 | 5.2e-05 | -3.48 | 4821.02226 | 10.3304, 10.3293 | 0.04097 |
| 3 | 41 | 7.4e-11 | -27035.30503536 | -27035.3050353553 | 0.0146 | 0.00417 | 0.0958 | 4.2e-05 | -3.48 | 4821.8331 | 10.3307, 10.3308 | 0.06146 |
| 4 | 45 | 1.5e-10 | -27035.32165062 | -27035.3216506166 | 0.02113 | 0.00492 | 0.113028 | 2.1e-05 | -3.59 | 4822.29245 | 10.3302, 10.3322 | 0.0922 |
| 5 | 40 | 1.4e-10 | -27035.34101592 | -27035.3410159238 | 0.02174 | 0.00512 | 0.117628 | 4.2e-05 | -3.41 | 4821.45819 | 10.3288, 10.3318 | 0.06364 |
| 6 | 62 | 1.1e-10 | -27035.3532864 | -27035.3532864027 | 0.01275 | 0.00358 | 0.082367 | 4e-05 | -2.82 | 4819.46482 | 10.3267, 10.3297 | 0.04671 |
| 7 | 59 | 1.2e-10 | -27035.36118316 | -27035.3611831563 | 0.007997 | 0.00249 | 0.057195 | 4.8e-05 | -2.1 | 4817.56922 | 10.3249, 10.3274 | 0.03198 |
| 8 | 49 | 5.8e-11 | -27035.36537123 | -27035.3653712292 | 0.008965 | 0.00291 | 0.066977 | 3e-05 | -1.67 | 4814.89254 | 10.3224, 10.3242 | 0.04682 |
| 9 | 45 | 6.4e-11 | -27035.37168204 | -27035.3716820365 | 0.01485 | 0.00342 | 0.078513 | 2.5e-05 | -1.29 | 4811.76185 | 10.3196, 10.3202 | 0.07021 |
| 10 | 59 | 8.9e-11 | -27035.38147317 | -27035.381473167 | 0.01699 | 0.00389 | 0.089455 | 2.3e-05 | -0.83 | 4809.03777 | 10.3173, 10.3167 | 0.1053 |
| 11 | 48 | 7.4e-11 | -27035.39361805 | -27035.3936180549 | 0.0134 | 0.00422 | 0.096874 | 2.1e-05 | -0.65 | 4808.20298 | 10.3172, 10.3150 | 0.1108 |
| 12 | 56 | 1.3e-10 | -27035.40450571 | -27035.4045057081 | 0.007417 | 0.00304 | 0.069845 | 6.7e-05 | -0.36 | 4809.85188 | 10.3191, 10.3166 | 0.1014 |
| 13 | 69 | 6e-11 | -27035.41019606 | -27035.4101960577 | 0.01624 | 0.00464 | 0.106611 | 2e-05 | -1.15 | 4814.4328 | 10.3242, 10.3214 | 0.06072 |
| 14 | 45 | 5.7e-11 | -27035.41887019 | -27035.4188701903 | 0.01208 | 0.0035 | 0.080399 | 2.5e-05 | -1.33 | 4817.01519 | 10.3271, 10.3240 | 0.07139 |
| 15 | 63 | 7.5e-11 | -27035.42570444 | -27035.4257044351 | 0.009184 | 0.00279 | 0.064101 | 4.2e-05 | -1.53 | 4819.08372 | 10.3298, 10.3257 | 0.07855 |
| 16 | 55 | 4.2e-11 | -27035.43238953 | -27035.4323895281 | 0.007612 | 0.00238 | 0.054648 | 2e-05 | -1.57 | 4819.81847 | 10.3315, 10.3256 | 0.1065 |
| 17 | 65 | 6.1e-11 | -27035.43832574 | -27035.4383257431 | 0.006285 | 0.00245 | 0.056384 | 4e-05 | -1.55 | 4819.00785 | 10.3311, 10.3243 | 0.06143 |
| 18 | 45 | 4.1e-11 | -27035.44166737 | -27035.4416673702 | 0.005536 | 0.00198 | 0.045474 | 1.6e-05 | -1.36 | 4816.27775 | 10.3285, 10.3210 | 0.04548 |
| 19 | 43 | 4.8e-11 | -27035.44556872 | -27035.4455687177 | 0.007594 | 0.00205 | 0.047151 | 1.9e-05 | -0.81 | 4814.66118 | 10.3269, 10.3192 | 0.06533 |
| 20 | 50 | 5.9e-11 | -27035.44760063 | -27035.4476006343 | 0.007572 | 0.00238 | 0.054646 | 3e-05 | -1.14 | 4813.59493 | 10.3252, 10.3186 | 0.04236 |
| 21 | 51 | 6.3e-11 | -27035.45002736 | -27035.4500273638 | 0.005399 | 0.00182 | 0.041777 | 2e-05 | -0.85 | 4813.59684 | 10.3244, 10.3194 | 0.04021 |
| 22 | 46 | 3e-11 | -27035.45321347 | -27035.4532134727 | 0.0045 | 0.00145 | 0.033388 | 3.3e-05 | -0.83 | 4814.41958 | 10.3244, 10.3211 | 0.05558 |
| 23 | 37 | 2.7e-11 | -27035.45649704 | -27035.456497037 | 0.004115 | 0.00145 | 0.033219 | 1.3e-05 | -0.92 | 4815.58591 | 10.3253, 10.3227 | 0.08417 |
| 24 | 41 | 3.6e-11 | -27035.45903662 | -27035.459036623 | 0.004592 | 0.00169 | 0.038737 | 3e-05 | -1.03 | 4817.04921 | 10.3269, 10.3242 | 0.09007 |
| 25 | 48 | 1.6e-11 | -27035.46150245 | -27035.4615024514 | 0.004474 | 0.00169 | 0.038929 | 9e-06 | -1.06 | 4818.53268 | 10.3290, 10.3253 | 0.07274 |
| 26 | 39 | 2.1e-11 | -27035.46393986 | -27035.4639398607 | 0.004448 | 0.00146 | 0.033441 | 2.5e-05 | -0.95 | 4819.89269 | 10.3315, 10.3257 | 0.06503 |
| 27 | 53 | 3.9e-11 | -27035.46637557 | -27035.4663755736 | 0.005151 | 0.00145 | 0.033234 | 1.8e-05 | -0.81 | 4821.25146 | 10.3345, 10.3256 | 0.05425 |
| 28 | 36 | 3.8e-11 | -27035.46872589 | -27035.4687258929 | 0.005812 | 0.00173 | 0.039694 | 2e-05 | -0.69 | 4822.73579 | 10.3385, 10.3249 | 0.08013 |
| 29 | 45 | 4.1e-11 | -27035.47137814 | -27035.4713781361 | 0.006663 | 0.00193 | 0.044328 | 1.8e-05 | -0.84 | 4823.80611 | 10.3428, 10.3228 | 0.09586 |
| 30 | 43 | 5.8e-11 | -27035.47419568 | -27035.4741956761 | 0.00741 | 0.00249 | 0.057112 | 2.7e-05 | -0.69 | 4823.93503 | 10.3461, 10.3198 | 0.1068 |
| 31 | 50 | 4.3e-11 | -27035.47694822 | -27035.4769482175 | 0.01399 | 0.00333 | 0.076611 | 2.4e-05 | -1.31 | 4821.53437 | 10.3446, 10.3162 | 0.03802 |
| 32 | 37 | 1.3e-10 | -27035.48153914 | -27035.4815391359 | 0.008068 | 0.00283 | 0.065052 | 6.4e-05 | -1.13 | 4817.76663 | 10.3431, 10.3096 | 0.114 |
| 33 | 59 | 4.9e-11 | -27035.48776407 | -27035.4877640742 | 0.01297 | 0.00367 | 0.084276 | 3.3e-05 | -1.11 | 4810.23137 | 10.3369, 10.2996 | 0.1891 |
| 34 | 37 | 9.5e-11 | -27035.49713499 | -27035.4971349877 | 0.02755 | 0.00605 | 0.139113 | 3.7e-05 | -0.9 | 4804.52631 | 10.3279, 10.2964 | 0.0816 |
| 35 | 47 | 2.6e-10 | -27035.50550597 | -27035.5055059684 | 0.01081 | 0.00403 | 0.092561 | 6.2e-05 | 0.18 | 4800.0265 | 10.3232, 10.2914 | 0.2447 |
| 36 | 51 | 1.1e-10 | -27035.51659099 | -27035.5165909931 | 0.03521 | 0.0072 | 0.165429 | 4.5e-05 | -0.2 | 4802.89805 | 10.3244, 10.2965 | 0.1273 |
| 37 | 45 | 2.2e-10 | -27035.53358456 | -27035.5335845588 | 0.02785 | 0.00534 | 0.122697 | 6.6e-05 | -0.21 | 4803.76101 | 10.3236, 10.2991 | 0.1571 |
| 38 | 41 | 2.4e-10 | -27035.54666428 | -27035.5466642792 | 0.02429 | 0.00487 | 0.111982 | 5e-05 | -0.49 | 4804.37915 | 10.3225, 10.3015 | 0.1728 |
| 39 | 48 | 2e-10 | -27035.56173334 | -27035.5617333373 | 0.01974 | 0.00439 | 0.100969 | 4.9e-05 | -0.83 | 4803.88453 | 10.3205, 10.3024 | 0.2593 |
| 40 | 44 | 1.5e-10 | -27035.57638142 | -27035.5763814228 | 0.03214 | 0.00704 | 0.161859 | 5.4e-05 | -2.01 | 4810.85266 | 10.3240, 10.3139 | 0.2916 |
| 41 | 45 | 2.6e-10 | -27035.53850722 | -27035.5385072227 | 0.07567 | 0.0184 | 0.422849 | 4.1e-05 | -1.58 | 4806.12133 | 10.3216, 10.3061 | 0.09368 |
| 42 | 72 | 2e-10 | -27035.5869208 | -27035.5869208026 | 0.01367 | 0.00439 | 0.100922 | 7e-05 | -1.87 | 4804.27183 | 10.3198, 10.3040 | 0.1454 |
| 43 | 47 | 7.5e-11 | -27035.59750855 | -27035.597508553 | 0.01824 | 0.00507 | 0.116488 | 3.5e-05 | -2.5 | 4799.5905 | 10.3167, 10.2970 | 0.09067 |
| 44 | 42 | 1.6e-10 | -27035.61415256 | -27035.6141525629 | 0.01905 | 0.00508 | 0.116813 | 7e-05 | -2.07 | 4792.28641 | 10.3106, 10.2874 | 0.1194 |
| 45 | 36 | 7e-11 | -27035.62680083 | -27035.6268008304 | 0.01201 | 0.00383 | 0.087955 | 3e-05 | -1.3 | 4788.46578 | 10.3059, 10.2839 | 0.1008 |
| 46 | 40 | 1.1e-10 | -27035.63497276 | -27035.6349727591 | 0.009056 | 0.00297 | 0.068238 | 4.9e-05 | -0.75 | 4783.4406 | 10.2968, 10.2822 | 0.1961 |
| 47 | 41 | 7.7e-11 | -27035.63846315 | -27035.6384631474 | 0.02372 | 0.00593 | 0.136262 | 3.5e-05 | -1.37 | 4784.26125 | 10.2925, 10.2883 | 0.04889 |
| 48 | 52 | 1.4e-10 | -27035.64443719 | -27035.6444371864 | 0.01592 | 0.00437 | 0.100427 | 5.6e-05 | 0.26 | 4785.95996 | 10.2932, 10.2913 | 0.0472 |
| 49 | 56 | 9.4e-11 | -27035.64928375 | -27035.649283752 | 0.005878 | 0.00199 | 0.045683 | 3.1e-05 | -0.42 | 4785.69974 | 10.2911, 10.2928 | 0.03952 |
| 50 | 58 | 3.3e-11 | -27035.65225132 | -27035.6522513163 | 0.00359 | 0.00141 | 0.032387 | 2.1e-05 | -0.64 | 4786.62436 | 10.2888, 10.2971 | 0.06439 |
| 51 | 69 | 3.1e-11 | -27035.6551726 | -27035.6551726047 | 0.004606 | 0.0015 | 0.034406 | 1.7e-05 | -0.6 | 4789.20888 | 10.2902, 10.3012 | 0.02951 |
| 52 | 47 | 3.4e-11 | -27035.65692007 | -27035.6569200744 | 0.00514 | 0.00141 | 0.032378 | 1.8e-05 | -0.5 | 4793.40325 | 10.2939, 10.3065 | 0.03839 |
| 53 | 45 | 3.5e-11 | -27035.65850655 | -27035.6585065479 | 0.004621 | 0.00129 | 0.0296 | 2.4e-05 | -0.61 | 4797.97377 | 10.2991, 10.3111 | 0.01941 |
| 54 | 59 | 3.8e-11 | -27035.65965304 | -27035.6596530435 | 0.002841 | 0.00108 | 0.024827 | 2e-05 | -0.84 | 4800.95017 | 10.3029, 10.3137 | 0.01309 |
| 55 | 60 | 9.7e-12 | -27035.66037489 | -27035.6603748866 | 0.002182 | 0.000861 | 0.019792 | 9e-06 | -1.08 | 4802.44567 | 10.3051, 10.3147 | 0.01196 |
| 56 | 52 | 1.2e-11 | -27035.66095179 | -27035.6609517913 | 0.002233 | 0.000782 | 0.017974 | 1.3e-05 | -1.21 | 4802.71202 | 10.3059, 10.3145 | 0.01215 |
| 57 | 37 | 2.1e-11 | -27035.6615184 | -27035.6615184005 | 0.002103 | 0.00078 | 0.017918 | 2e-05 | -1.23 | 4802.10096 | 10.3056, 10.3135 | 0.01483 |
| 58 | 38 | 9.4e-12 | -27035.66206959 | -27035.6620695897 | 0.001874 | 0.000759 | 0.017446 | 1.4e-05 | -1.11 | 4801.17063 | 10.3049, 10.3122 | 0.0201 |
| 59 | 34 | 1.1e-11 | -27035.66257107 | -27035.6625710735 | 0.001691 | 0.000743 | 0.017079 | 1.7e-05 | -0.92 | 4800.53496 | 10.3047, 10.3110 | 0.01955 |
| 60 | 50 | 7.5e-12 | -27035.66304292 | -27035.6630429175 | 0.001991 | 0.00075 | 0.017226 | 8e-06 | -0.73 | 4800.53548 | 10.3056, 10.3101 | 0.02673 |
| 61 | 50 | 1.9e-11 | -27035.66354762 | -27035.6635476234 | 0.00285 | 0.000757 | 0.017389 | 1.5e-05 | -0.61 | 4801.36541 | 10.3077, 10.3098 | 0.03124 |
| 62 | 41 | 2e-11 | -27035.66398119 | -27035.6639811867 | 0.002667 | 0.000665 | 0.015272 | 1.2e-05 | -0.62 | 4802.54514 | 10.3100, 10.3101 | 0.02565 |
| 63 | 49 | 2.5e-11 | -27035.66428146 | -27035.6642814613 | 0.00173 | 0.000534 | 0.012267 | 1.8e-05 | -0.73 | 4803.59101 | 10.3119, 10.3104 | 0.01966 |
| 64 | 38 | 1.3e-11 | -27035.66450196 | -27035.6645019638 | 0.001188 | 0.000482 | 0.011065 | 1.4e-05 | -0.83 | 4804.34087 | 10.3132, 10.3107 | 0.0139 |
| 65 | 48 | 4.4e-12 | -27035.66470419 | -27035.6647041897 | 0.001296 | 0.000497 | 0.011409 | 1e-05 | -0.89 | 4804.8085 | 10.3143, 10.3107 | 0.01429 |
| 66 | 47 | 9.4e-12 | -27035.66490884 | -27035.6649088446 | 0.00133 | 0.00051 | 0.011721 | 1.6e-05 | -0.86 | 4804.89453 | 10.3148, 10.3103 | 0.01038 |
| 67 | 55 | 7.8e-12 | -27035.66506595 | -27035.6650659477 | 0.001111 | 0.000455 | 0.010454 | 1.1e-05 | -0.76 | 4804.82998 | 10.3152, 10.3097 | 0.01027 |
| 68 | 36 | 9.2e-12 | -27035.66518762 | -27035.6651876198 | 0.000889 | 0.000368 | 0.008454 | 1.3e-05 | -0.63 | 4804.84066 | 10.3158, 10.3092 | 0.01013 |
| 69 | 46 | 7.5e-12 | -27035.66529062 | -27035.6652906249 | 0.000689 | 0.000316 | 0.007263 | 1.4e-05 | -0.52 | 4805.0735 | 10.3168, 10.3087 | 0.01107 |
| 70 | 42 | 9.1e-12 | -27035.66539153 | -27035.6653915258 | 0.0008819 | 0.000316 | 0.007261 | 9e-06 | -0.44 | 4805.5089 | 10.3179, 10.3085 | 0.009889 |
| 71 | 54 | 7.4e-12 | -27035.6654809 |  | 0.000863 | 0.000311 | 0.007153 | 1e-05 | -0.43 |  |  |  |
| 72 | 98 | 9.7e-12 | -27035.66492694 |  | 0.0008626 | 0.000311 | 0.007154 | 1.4e-05 | -0.43 |  |  |  |

**Final energies** (last SCF): negative_rho = [0.002107, 0.0], HOMO_eV = 0.0475, LUMO_eV = 1.2713, E_Ry = -27035.66492694, E_all_electron_Ry = -673235.702643, acc_final_Ry = 9.7e-12, one_electron_Ry = -272838.07316665, hartree_Ry = 137216.08519503, xc_Ry = -3329.7216415, ewald_Ry = 128104.25305226, paw_one_center_Ry = -16188.20836607, converged_iterations = 98
- stress tensor (kbar): [[0.06, 0.0, 0.0], [0.0, 0.13, 0.0], [0.0, 0.0, -1.49]]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 672, "n_occ": 664, "VBM_eV": 0.0475, "VBM_k_index": 0, "CBM_eV": 1.2713, "CBM_k_index": 0, "gap_eV": 1.2238, "direct_gap_min_eV": 1.2238, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.0136, "CB_width_bottom_band_eV": 1.0517, "E2_minus_E1_at_k0_eV": 0.7192}

**Final geometry** (vs `slab2_relax_c2/vcrelax_initial.in`): {"n_atoms": 176, "composition": {"H": 24, "In": 56, "O": 96}, "cell_lengths_A": [10.31792, 10.30849, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5089, "density_g_cm3": 2.7609, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 336, "min": 2.1616, "mean": 2.2197, "max": 2.3007, "std": 0.0357, "CN_In_hist": {"6": 56}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9722, "mean": 0.9773, "max": 0.9858, "std": 0.0061, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.557, "extent_A": 19.623, "thickness_H_H_A": 19.6233, "thickness_O_O_A": 18.2137, "thickness_In_In_A": 15.4861}, "displacement_vs_initial": {"max_A": 1.2979, "atom": "H153", "mean_A": 0.1345, "n_gt_0p1_A": 40, "by_element_max_A": {"H": 1.2979, "In": 0.0389, "O": 0.3437}, "outer_3A_mean_A": 0.3503, "interior_mean_A": 0.0112}, "reference_input": "slab2_relax_c2/vcrelax_initial.in"}

**Warnings/errors**: message_from_routine x1 (first: line 29 'Message from routine setup:'); warning x3 (first: line 96363 'Warning: ieee_invalid is signaling'); c_bands_not_converged x27 (first: line 792 'c_bands:  1 eigenvalues not converged'); ieee x3 (first: line 96363 'Warning: ieee_invalid is signaling'); discouraged x1 (first: line 30 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized'); fortran_stop x1 (first: line 96366 'FORTRAN STOP')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Calculation `slab2_relax_c2__cpu/vcrelax.out` (scf/relax)

QE v.7.5 started 2Oct2026 4:46:28; 16 MPI x 1 threads on 1 node(s); pools 2; R&G division 8; node memory 105587.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: NO (no JOB DONE); terminated None; PWSCF time None; output lines 3435.

**Input settings** (every namelist variable):

- &CONTROL: calculation = vc-relax, prefix = vcr, outdir = ./tmp, pseudo_dir = ./, verbosity = low, tprnfor = .true., tstress = .true., max_seconds = 257389, nstep = 300, etot_conv_thr = 1.0d-4, forc_conv_thr = 1.0d-3
- &SYSTEM: ibrav = 0, nat = 176, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 672
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- &IONS: ion_dynamics = bfgs
- &CELL: cell_dynamics = bfgs, cell_dofree = 2Dxy, press_conv_thr = 0.5
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.328080023, 0.0, 0.0], [0.0, 10.325066496, 0.0], [0.0, 0.0, 45.18062913]]}
- K_POINTS: {"mode": "automatic", "grid": ["3", "3", "1", "0", "0", "0"]}
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 176, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.5172  a.u.; unit-cell volume = 32513.3206 (a.u.)^3; number of atoms/cell = 176; number of atomic types = 3; number of electrons = 1328.00; number of Kohn-Sham states = 672; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; energy convergence thresh. = 1.0E-04; force convergence thresh. = 1.0E-03; press convergence thresh. = 5.0E-01; Exchange-correlation = SLA  PW   PBX  PBC; nstep = 300; celldm = [19.517243, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  7431975 G-vectors     FFT dimensions: ( 150, 150, 648) / Smooth grid:  2627561 G-vectors     FFT dimensions: ( 108, 108, 480)
- RAM (pw.x estimate): {'Estimated max dynamical RAM per process': '6.19 GB', 'Estimated total dynamical RAM': '97.19 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge    1327.7914, renormalised to    1328.0000', 'Starting wfcs are  912 randomized atomic wfcs']

**Convergence** (3 SCF + BFGS):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 93 | 5.6e-10 | -27035.26282339 | -27035.2628233904 | 0.02143 | 0.00596 | 0.137058 | 7.8e-05 | -2.69 | 4819.14982 | 10.3291, 10.3265 | 0.02483 |
| 1 | 39 | 1.3e-10 | -27035.27773666 | -27035.2777366552 | 0.01201 | 0.00431 | 0.099039 | 3.6e-05 | -2.86 | 4820.09162 | 10.3299, 10.3278 | 0.02731 |
| 2 | 9 | None | None |  |  |  |  |  |  |  |  |  |

**Final energies** (last SCF): negative_rho = [0.006808, 0.0]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 672, "n_occ": 664, "VBM_eV": 0.7446, "VBM_k_index": 0, "CBM_eV": 1.8542, "CBM_k_index": 0, "gap_eV": 1.1096, "direct_gap_min_eV": 1.1096, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.0109, "CB_width_bottom_band_eV": 1.0899, "E2_minus_E1_at_k0_eV": 0.6665}

**Warnings/errors**: message_from_routine x1 (first: line 29 'Message from routine setup:'); c_bands_not_converged x15 (first: line 707 'c_bands:  1 eigenvalues not converged'); discouraged x1 (first: line 30 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Calculation `slab2_relax_c2_vcrelax.out` (scf/relax)

QE v.7.3.1 started 2Oct2026 9:12:24; 1 MPI x 1 threads on 1 node(s); pools 1; R&G division -; node memory 37861.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: a serial algorithm will be used; GPU: GPU acceleration is ACTIVE.  1 visible GPUs per MPI rank; GPU-aware MPI enabled. Completed: NO (no JOB DONE); terminated None; PWSCF time None; output lines 53130.
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.5172  a.u.; unit-cell volume = 32513.3206 (a.u.)^3; number of atoms/cell = 176; number of atomic types = 3; number of electrons = 1328.00; number of Kohn-Sham states = 672; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; scf convergence threshold = 1.0E-09; mixing beta = 0.2000; number of iterations used = 8  local-TF  mixing; energy convergence thresh. = 1.0E-04; force convergence thresh. = 1.0E-03; press convergence thresh. = 5.0E-01; Exchange-correlation = SLA  PW   PBX  PBC; nstep = 300; celldm = [19.517243, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=     4 (sum of weights 2.0); FFT: Dense  grid:  7431975 G-vectors     FFT dimensions: ( 150, 150, 648) / Smooth grid:  2627561 G-vectors     FFT dimensions: ( 108, 108, 480)
- RAM (pw.x estimate): {'Estimated max dynamical RAM per process': '82.11 GB'}; start: ['Initial potential from superposition of free atoms', 'starting charge    1327.7914, renormalised to    1328.0000', 'Starting wfcs are  912 randomized atomic wfcs']

**Convergence** (41 SCF + BFGS):   final energy None final enthalpy None 

| step | iter | final acc (Ry) | E (Ry) | enthalpy (Ry) | max F comp | rms F | total F (Ry/bohr) | SCF corr | P (kbar) | V (A^3) | a, b (A) | trust r (bohr) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 93 | 4.7e-10 | -27035.26282772 | -27035.2628277204 | 0.02143 | 0.00596 | 0.137062 | 8.5e-05 | -2.68 | 4819.17263 | 10.3291, 10.3266 | 0.02483 |
| 1 | 47 | 7.8e-10 | -27035.27774175 | -27035.277741752 | 0.01201 | 0.00431 | 0.098965 | 7.9e-05 | -2.86 | 4820.11372 | 10.3299, 10.3278 | 0.02731 |
| 2 | 52 | 1e-10 | -27035.29081595 | -27035.2908159487 | 0.01049 | 0.00363 | 0.083508 | 5.2e-05 | -3.48 | 4821.02226 | 10.3304, 10.3293 | 0.04097 |
| 3 | 41 | 7.4e-11 | -27035.30503536 | -27035.3050353553 | 0.0146 | 0.00417 | 0.0958 | 4.2e-05 | -3.48 | 4821.8331 | 10.3307, 10.3308 | 0.06146 |
| 4 | 45 | 1.5e-10 | -27035.32165062 | -27035.3216506166 | 0.02113 | 0.00492 | 0.113028 | 2.1e-05 | -3.59 | 4822.29245 | 10.3302, 10.3322 | 0.0922 |
| 5 | 40 | 1.4e-10 | -27035.34101592 | -27035.3410159238 | 0.02174 | 0.00512 | 0.117628 | 4.2e-05 | -3.41 | 4821.45819 | 10.3288, 10.3318 | 0.06364 |
| 6 | 62 | 1.1e-10 | -27035.3532864 | -27035.3532864027 | 0.01275 | 0.00358 | 0.082367 | 4e-05 | -2.82 | 4819.46482 | 10.3267, 10.3297 | 0.04671 |
| 7 | 59 | 1.2e-10 | -27035.36118316 | -27035.3611831563 | 0.007997 | 0.00249 | 0.057195 | 4.8e-05 | -2.1 | 4817.56922 | 10.3249, 10.3274 | 0.03198 |
| 8 | 49 | 5.8e-11 | -27035.36537123 | -27035.3653712292 | 0.008965 | 0.00291 | 0.066977 | 3e-05 | -1.67 | 4814.89254 | 10.3224, 10.3242 | 0.04682 |
| 9 | 45 | 6.4e-11 | -27035.37168204 | -27035.3716820365 | 0.01485 | 0.00342 | 0.078513 | 2.5e-05 | -1.29 | 4811.76185 | 10.3196, 10.3202 | 0.07021 |
| 10 | 59 | 8.9e-11 | -27035.38147317 | -27035.381473167 | 0.01699 | 0.00389 | 0.089455 | 2.3e-05 | -0.83 | 4809.03777 | 10.3173, 10.3167 | 0.1053 |
| 11 | 48 | 7.4e-11 | -27035.39361805 | -27035.3936180549 | 0.0134 | 0.00422 | 0.096874 | 2.1e-05 | -0.65 | 4808.20298 | 10.3172, 10.3150 | 0.1108 |
| 12 | 56 | 1.3e-10 | -27035.40450571 | -27035.4045057081 | 0.007417 | 0.00304 | 0.069845 | 6.7e-05 | -0.36 | 4809.85188 | 10.3191, 10.3166 | 0.1014 |
| 13 | 69 | 6e-11 | -27035.41019606 | -27035.4101960577 | 0.01624 | 0.00464 | 0.106611 | 2e-05 | -1.15 | 4814.4328 | 10.3242, 10.3214 | 0.06072 |
| 14 | 45 | 5.7e-11 | -27035.41887019 | -27035.4188701903 | 0.01208 | 0.0035 | 0.080399 | 2.5e-05 | -1.33 | 4817.01519 | 10.3271, 10.3240 | 0.07139 |
| 15 | 63 | 7.5e-11 | -27035.42570444 | -27035.4257044351 | 0.009184 | 0.00279 | 0.064101 | 4.2e-05 | -1.53 | 4819.08372 | 10.3298, 10.3257 | 0.07855 |
| 16 | 55 | 4.2e-11 | -27035.43238953 | -27035.4323895281 | 0.007612 | 0.00238 | 0.054648 | 2e-05 | -1.57 | 4819.81847 | 10.3315, 10.3256 | 0.1065 |
| 17 | 65 | 6.1e-11 | -27035.43832574 | -27035.4383257431 | 0.006285 | 0.00245 | 0.056384 | 4e-05 | -1.55 | 4819.00785 | 10.3311, 10.3243 | 0.06143 |
| 18 | 45 | 4.1e-11 | -27035.44166737 | -27035.4416673702 | 0.005536 | 0.00198 | 0.045474 | 1.6e-05 | -1.36 | 4816.27775 | 10.3285, 10.3210 | 0.04548 |
| 19 | 43 | 4.8e-11 | -27035.44556872 | -27035.4455687177 | 0.007594 | 0.00205 | 0.047151 | 1.9e-05 | -0.81 | 4814.66118 | 10.3269, 10.3192 | 0.06533 |
| 20 | 50 | 5.9e-11 | -27035.44760063 | -27035.4476006343 | 0.007572 | 0.00238 | 0.054646 | 3e-05 | -1.14 | 4813.59493 | 10.3252, 10.3186 | 0.04236 |
| 21 | 51 | 6.3e-11 | -27035.45002736 | -27035.4500273638 | 0.005399 | 0.00182 | 0.041777 | 2e-05 | -0.85 | 4813.59684 | 10.3244, 10.3194 | 0.04021 |
| 22 | 46 | 3e-11 | -27035.45321347 | -27035.4532134727 | 0.0045 | 0.00145 | 0.033388 | 3.3e-05 | -0.83 | 4814.41958 | 10.3244, 10.3211 | 0.05558 |
| 23 | 37 | 2.7e-11 | -27035.45649704 | -27035.456497037 | 0.004115 | 0.00145 | 0.033219 | 1.3e-05 | -0.92 | 4815.58591 | 10.3253, 10.3227 | 0.08417 |
| 24 | 41 | 3.6e-11 | -27035.45903662 | -27035.459036623 | 0.004592 | 0.00169 | 0.038737 | 3e-05 | -1.03 | 4817.04921 | 10.3269, 10.3242 | 0.09007 |
| 25 | 48 | 1.6e-11 | -27035.46150245 | -27035.4615024514 | 0.004474 | 0.00169 | 0.038929 | 9e-06 | -1.06 | 4818.53268 | 10.3290, 10.3253 | 0.07274 |
| 26 | 39 | 2.1e-11 | -27035.46393986 | -27035.4639398607 | 0.004448 | 0.00146 | 0.033441 | 2.5e-05 | -0.95 | 4819.89269 | 10.3315, 10.3257 | 0.06503 |
| 27 | 53 | 3.9e-11 | -27035.46637557 | -27035.4663755736 | 0.005151 | 0.00145 | 0.033234 | 1.8e-05 | -0.81 | 4821.25146 | 10.3345, 10.3256 | 0.05425 |
| 28 | 36 | 3.8e-11 | -27035.46872589 | -27035.4687258929 | 0.005812 | 0.00173 | 0.039694 | 2e-05 | -0.69 | 4822.73579 | 10.3385, 10.3249 | 0.08013 |
| 29 | 45 | 4.1e-11 | -27035.47137814 | -27035.4713781361 | 0.006663 | 0.00193 | 0.044328 | 1.8e-05 | -0.84 | 4823.80611 | 10.3428, 10.3228 | 0.09586 |
| 30 | 43 | 5.8e-11 | -27035.47419568 | -27035.4741956761 | 0.00741 | 0.00249 | 0.057112 | 2.7e-05 | -0.69 | 4823.93503 | 10.3461, 10.3198 | 0.1068 |
| 31 | 50 | 4.3e-11 | -27035.47694822 | -27035.4769482175 | 0.01399 | 0.00333 | 0.076611 | 2.4e-05 | -1.31 | 4821.53437 | 10.3446, 10.3162 | 0.03802 |
| 32 | 37 | 1.3e-10 | -27035.48153914 | -27035.4815391359 | 0.008068 | 0.00283 | 0.065052 | 6.4e-05 | -1.13 | 4817.76663 | 10.3431, 10.3096 | 0.114 |
| 33 | 59 | 4.9e-11 | -27035.48776407 | -27035.4877640742 | 0.01297 | 0.00367 | 0.084276 | 3.3e-05 | -1.11 | 4810.23137 | 10.3369, 10.2996 | 0.1891 |
| 34 | 37 | 9.5e-11 | -27035.49713499 | -27035.4971349877 | 0.02755 | 0.00605 | 0.139113 | 3.7e-05 | -0.9 | 4804.52631 | 10.3279, 10.2964 | 0.0816 |
| 35 | 47 | 2.6e-10 | -27035.50550597 | -27035.5055059684 | 0.01081 | 0.00403 | 0.092561 | 6.2e-05 | 0.18 | 4800.0265 | 10.3232, 10.2914 | 0.2447 |
| 36 | 51 | 1.1e-10 | -27035.51659099 | -27035.5165909931 | 0.03521 | 0.0072 | 0.165429 | 4.5e-05 | -0.2 | 4802.89805 | 10.3244, 10.2965 | 0.1273 |
| 37 | 45 | 2.2e-10 | -27035.53358456 | -27035.5335845588 | 0.02785 | 0.00534 | 0.122697 | 6.6e-05 | -0.21 | 4803.76101 | 10.3236, 10.2991 | 0.1571 |
| 38 | 41 | 2.4e-10 | -27035.54666428 | -27035.5466642792 | 0.02429 | 0.00487 | 0.111982 | 5e-05 | -0.49 | 4804.37915 | 10.3225, 10.3015 | 0.1728 |
| 39 | 48 | 2e-10 | -27035.56173334 | -27035.5617333373 | 0.01974 | 0.00439 | 0.100969 | 4.9e-05 | -0.83 | 4803.88453 | 10.3205, 10.3024 | 0.2593 |
| 40 | 20 | None | None |  |  |  |  |  |  |  |  |  |

**Final energies** (last SCF): negative_rho = [0.002055, 0.0]

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 672, "n_occ": 664, "VBM_eV": -0.0226, "VBM_k_index": 2, "CBM_eV": 1.195, "CBM_k_index": 0, "gap_eV": 1.2176, "direct_gap_min_eV": 1.2215, "direct_gap_k_index": 0, "gap_type": "indirect", "VB_width_top_band_eV": 0.0127, "CB_width_bottom_band_eV": 1.0524, "E2_minus_E1_at_k0_eV": 0.7175}

**Warnings/errors**: message_from_routine x1 (first: line 29 'Message from routine setup:'); c_bands_not_converged x27 (first: line 792 'c_bands:  1 eigenvalues not converged'); discouraged x1 (first: line 30 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Calculation `slab2r_final_cpu/bands.out` (bands)

QE v.7.5 started 5Oct2026 1:33:53; 24 MPI x 1 threads on 1 node(s); pools 4; R&G division 6; node memory 137447.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: NO (no JOB DONE); terminated None; PWSCF time None; output lines 681.

**Input settings** (every namelist variable):

- &CONTROL: calculation = bands, prefix = slab, outdir = ./tmp, pseudo_dir = ./, verbosity = high, tprnfor = .true., tstress = .true., max_seconds = 48669
- &SYSTEM: ibrav = 0, nat = 176, ntyp = 3, ecutwfc = 71, ecutrho = 568, occupations = fixed, nbnd = 680
- &ELECTRONS: conv_thr = 1.0d-9, mixing_beta = 0.2, electron_maxstep = 150, mixing_mode = local-TF
- ATOMIC_SPECIES: [{"species": "In", "mass": 114.818, "pseudo": "In.pbe-dn-kjpaw_psl.1.0.0.UPF"}, {"species": "O", "mass": 15.999, "pseudo": "O.pbe-n-kjpaw_psl.1.0.0.UPF"}, {"species": "H", "mass": 1.008, "pseudo": "H.pbe-kjpaw_psl.1.0.0.UPF"}]
- CELL_PARAMETERS: {"unit": "angstrom", "vectors": [[10.31791632, 0.0, 0.0], [0.0, 10.30849134, 0.0], [0.0, 0.0, 45.18062913]]}
- K_POINTS: {"mode": "tpiba", "n": 21, "points_first_last": [[0.0, 0.0, 0.0, 1.0], [0.17417603, 0.17417603, 0.0, 1.0]], "path_points": [[0.0, 0.0, 0.0, 1.0], [0.02463221, 0.0, 0.0, 1.0], [0.04926442, 0.0, 0.0, 1.0], [0.07389663, 0.0, 0.0, 1.0], [0.09852884, 0.0, 0.0, 1.0], [0.12316105, 0.0, 0.0, 1.0], [0.14779326, 0.0, 0.0, 1.0], [0.17242548, 0.0, 0.0, 1.0], [0.19705769, 0.0, 0.0, 1.0], [0.2216899, 0.0, 0.0, 
- ATOMIC_POSITIONS: {"unit": "crystal", "n": 176, "labels": ["H", "In", "O"], "n_constrained": 0}
- Echoed parameters: bravais-lattice index = 0; lattice parameter (alat) = 19.4980  a.u.; unit-cell volume = 32429.1815 (a.u.)^3; number of atoms/cell = 176; number of atomic types = 3; number of electrons = 1328.00; number of Kohn-Sham states = 680; kinetic-energy cutoff = 71.0000  Ry; charge density cutoff = 568.0000  Ry; Exchange-correlation = SLA  PW   PBX  PBC; celldm = [19.498036, 0.0, 0.0, 0.0, 0.0, 0.0]
- Pseudopotentials: In In.pbe-dn-kjpaw_psl.1.0.0.UPF md5 235b15e6a7fdfd96486e0ecdcb5b12c6 (Projector augmented-wave + core cor, Z 13.0); O O.pbe-n-kjpaw_psl.1.0.0.UPF md5 e99d9cef9b487d1ca56f5b95ecd0fd7a (Projector augmented-wave + core cor, Z 6.0); H H.pbe-kjpaw_psl.1.0.0.UPF md5 d81a744832360e4a8af0b0b5b123bc2a (Projector augmented-wave, Z 1.0)
- Symmetry: 8 Sym. Ops., with inversion, found ( 6 have fractional translation); k points: number of k points=    21 (sum of weights 2.0); FFT: Dense  grid:  7413139 G-vectors     FFT dimensions: ( 150, 150, 648) / Smooth grid:  2620949 G-vectors     FFT dimensions: ( 108, 108, 480)
- RAM (pw.x estimate): {'Estimated static dynamical RAM per process': '2.44 GB', 'Estimated max dynamical RAM per process': '5.80 GB', 'Estimated total dynamical RAM': '139.27 GB'}; start: ['Starting wfcs are  912 randomized atomic wfcs']
- Band-structure run: {'diag': 'Davidson diagonalization with overlap', 'kpts_done': 1}

**Warnings/errors**: message_from_routine x1 (first: line 33 'Message from routine setup:'); discouraged x1 (first: line 34 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Calculation `slab2r_final_cpu/scf.out` (scf/relax)

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

## Calculation `slab2r_pdos_cpu/scf.out` (scf/relax)

QE v.7.5 started 5Oct2026 9:35:41; 24 MPI x 1 threads on 1 node(s); pools 2; R&G division 12; node memory 217250.0 MiB; Using Slab Decomposition; Subspace diagonalization in iterative solution of the eigenvalue problem: one sub-group per band group will be used; GPU: no GPU line. Completed: NO (no JOB DONE); terminated None; PWSCF time None; output lines 3916.

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
| 0 | 76 | 4.3e-10 | -27035.66492227 |  | 0.0008631 | 0.000311 | 0.007155 | 9.8e-05 |  |  |  |  |

**Final energies** (last SCF): negative_rho = [0.002107, 0.0], HOMO_eV = 0.0475, LUMO_eV = 1.2713, E_Ry = -27035.66492227, E_all_electron_Ry = -673235.702639, acc_final_Ry = 4.3e-10, one_electron_Ry = -272838.06894029, hartree_Ry = 137216.08086297, xc_Ry = -3329.72164898, ewald_Ry = 128104.25312711, paw_one_center_Ry = -16188.20832307, converged_iterations = 76

**Bands** (final eigenvalues, every k in the arrays file): {"n_k": 4, "n_bands": 680, "n_occ": 664, "VBM_eV": 0.0475, "VBM_k_index": 0, "CBM_eV": 1.2713, "CBM_k_index": 0, "gap_eV": 1.2238, "direct_gap_min_eV": 1.2238, "direct_gap_k_index": 0, "gap_type": "direct", "VB_width_top_band_eV": 0.0136, "CB_width_bottom_band_eV": 1.0517, "E2_minus_E1_at_k0_eV": 0.7192}

**Warnings/errors**: message_from_routine x1 (first: line 29 'Message from routine setup:'); c_bands_not_converged x2 (first: line 882 'c_bands:  1 eigenvalues not converged'); discouraged x1 (first: line 30 'using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead'); renormalized_wfc x3 (first: line 26 'file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized')
- messages: ['file In.pbe-dn-kjpaw_psl.1.0.0.UPF: wavefunction(s)  5S 5P 4D renormalized', 'file O.pbe-n-kjpaw_psl.1.0.0.UPF: wavefunction(s)  2S 2P renormalized', 'file H.pbe-kjpaw_psl.1.0.0.UPF: wavefunction(s)  1S renormalized', 'Message from routine setup: using ibrav=0 with symmetry is DISCOURAGED, use correct ibrav instead']

## Input geometries

- `iwo_slab2_W24d/bands.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 55, "O": 96, "W": 1}, "cell_lengths_A": [10.31792, 10.30849, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5089, "density_g_cm3": 2.7848, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 330, "min": 2.1292, "mean": 2.2283, "max": 2.5046, "std": 0.0617, "CN_In_hist": {"6": 55}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 1.8665, "mean": 1.9767, "max": 2.1897, "std": 0.1506, "CN_W_hist": {"6": 1}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9725, "mean": 0.9779, "max": 0.987, "std": 0.0063, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.458, "extent_A": 19.722, "thickness_H_H_A": 19.7222, "thickness_O_O_A": 18.2838, "thickness_In_In_A": 15.5749, "thickness_W_W_A": 0.0}}
- `iwo_slab2_W24d/relax.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 55, "O": 96, "W": 1}, "cell_lengths_A": [10.31792, 10.30849, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5089, "density_g_cm3": 2.7848, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 330, "min": 2.1616, "mean": 2.2197, "max": 2.3007, "std": 0.0356, "CN_In_hist": {"6": 55}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 2.1671, "mean": 2.223, "max": 2.2623, "std": 0.0406, "CN_W_hist": {"6": 1}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9722, "mean": 0.9773, "max": 0.9858, "std": 0.0061, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.557, "extent_A": 19.623, "thickness_H_H_A": 19.6233, "thickness_O_O_A": 18.2137, "thickness_In_In_A": 15.4861, "thickness_W_W_A": 0.0}}
- `iwo_slab2_W24d/scf.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 55, "O": 96, "W": 1}, "cell_lengths_A": [10.31792, 10.30849, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5089, "density_g_cm3": 2.7848, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 330, "min": 2.1292, "mean": 2.2283, "max": 2.5046, "std": 0.0617, "CN_In_hist": {"6": 55}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 1.8665, "mean": 1.9767, "max": 2.1897, "std": 0.1506, "CN_W_hist": {"6": 1}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9725, "mean": 0.9779, "max": 0.987, "std": 0.0063, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.458, "extent_A": 19.722, "thickness_H_H_A": 19.7222, "thickness_O_O_A": 18.2838, "thickness_In_In_A": 15.5749, "thickness_W_W_A": 0.0}}
- `iwo_slab2_W24d__cpu/relax.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 55, "O": 96, "W": 1}, "cell_lengths_A": [10.31792, 10.30849, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5089, "density_g_cm3": 2.7848, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 330, "min": 2.1616, "mean": 2.2197, "max": 2.3007, "std": 0.0356, "CN_In_hist": {"6": 55}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 2.1671, "mean": 2.223, "max": 2.2623, "std": 0.0406, "CN_W_hist": {"6": 1}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9722, "mean": 0.9773, "max": 0.9858, "std": 0.0061, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.557, "extent_A": 19.623, "thickness_H_H_A": 19.6233, "thickness_O_O_A": 18.2137, "thickness_In_In_A": 15.4861, "thickness_W_W_A": 0.0}}
- `iwo_slab2_final_cpu/scf.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 55, "O": 96, "W": 1}, "cell_lengths_A": [10.31792, 10.3085, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5109, "density_g_cm3": 2.7848, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 330, "min": 2.1292, "mean": 2.2283, "max": 2.5046, "std": 0.0617, "CN_In_hist": {"6": 55}}, "W-O": {"cutoff_A": 2.6, "n": 6, "min": 1.8665, "mean": 1.9767, "max": 2.1897, "std": 0.1506, "CN_W_hist": {"6": 1}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9725, "mean": 0.9779, "max": 0.987, "std": 0.0063, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.458, "extent_A": 19.722, "thickness_H_H_A": 19.7222, "thickness_O_O_A": 18.2838, "thickness_In_In_A": 15.5749, "thickness_W_W_A": 0.0}}
- `slab2_relax_c2/bands.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 56, "O": 96}, "cell_lengths_A": [10.31792, 10.30849, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5089, "density_g_cm3": 2.7609, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 336, "min": 2.1616, "mean": 2.2197, "max": 2.3007, "std": 0.0357, "CN_In_hist": {"6": 56}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9722, "mean": 0.9773, "max": 0.9858, "std": 0.0061, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.557, "extent_A": 19.623, "thickness_H_H_A": 19.6233, "thickness_O_O_A": 18.2137, "thickness_In_In_A": 15.4861}}
- `slab2_relax_c2/scf.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 56, "O": 96}, "cell_lengths_A": [10.31792, 10.30849, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5089, "density_g_cm3": 2.7609, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 336, "min": 2.1616, "mean": 2.2197, "max": 2.3007, "std": 0.0357, "CN_In_hist": {"6": 56}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9722, "mean": 0.9773, "max": 0.9858, "std": 0.0061, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.557, "extent_A": 19.623, "thickness_H_H_A": 19.6233, "thickness_O_O_A": 18.2137, "thickness_In_In_A": 15.4861}}
- `slab2_relax_c2/vcrelax.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 56, "O": 96}, "cell_lengths_A": [10.32808, 10.32507, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4817.977, "density_g_cm3": 2.7538, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 336, "min": 2.1459, "mean": 2.2203, "max": 2.2844, "std": 0.0367, "CN_In_hist": {"6": 56}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9679, "mean": 0.9698, "max": 0.9708, "std": 0.0014, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.051, "extent_A": 20.13, "thickness_H_H_A": 20.1301, "thickness_O_O_A": 18.2896, "thickness_In_In_A": 15.5995}}
- `slab2_relax_c2/vcrelax_initial.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 56, "O": 96}, "cell_lengths_A": [10.30609, 10.30609, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4798.8829, "density_g_cm3": 2.7647, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 336, "min": 2.1671, "mean": 2.2192, "max": 2.2561, "std": 0.0328, "CN_In_hist": {"6": 56}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.97, "mean": 0.97, "max": 0.97, "std": 0.0, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.0, "extent_A": 20.181, "thickness_H_H_A": 20.1806, "thickness_O_O_A": 18.3393, "thickness_In_In_A": 15.4591}}
- `slab2_relax_c2__cpu/vcrelax.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 56, "O": 96}, "cell_lengths_A": [10.32808, 10.32507, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4817.977, "density_g_cm3": 2.7538, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 336, "min": 2.1459, "mean": 2.2203, "max": 2.2844, "std": 0.0367, "CN_In_hist": {"6": 56}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9679, "mean": 0.9698, "max": 0.9708, "std": 0.0014, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.051, "extent_A": 20.13, "thickness_H_H_A": 20.1301, "thickness_O_O_A": 18.2896, "thickness_In_In_A": 15.5995}}
- `slab2_relax_c2__cpu/vcrelax_initial.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 56, "O": 96}, "cell_lengths_A": [10.30609, 10.30609, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4798.8829, "density_g_cm3": 2.7647, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 336, "min": 2.1671, "mean": 2.2192, "max": 2.2561, "std": 0.0328, "CN_In_hist": {"6": 56}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.97, "mean": 0.97, "max": 0.97, "std": 0.0, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.0, "extent_A": 20.181, "thickness_H_H_A": 20.1806, "thickness_O_O_A": 18.3393, "thickness_In_In_A": 15.4591}}
- `slab2r_final_cpu/bands.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 56, "O": 96}, "cell_lengths_A": [10.31792, 10.30849, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5089, "density_g_cm3": 2.7609, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 336, "min": 2.1616, "mean": 2.2197, "max": 2.3007, "std": 0.0357, "CN_In_hist": {"6": 56}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9722, "mean": 0.9773, "max": 0.9858, "std": 0.0061, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.557, "extent_A": 19.623, "thickness_H_H_A": 19.6233, "thickness_O_O_A": 18.2137, "thickness_In_In_A": 15.4861}}
- `slab2r_final_cpu/scf.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 56, "O": 96}, "cell_lengths_A": [10.31792, 10.30849, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5089, "density_g_cm3": 2.7609, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 336, "min": 2.1616, "mean": 2.2197, "max": 2.3007, "std": 0.0357, "CN_In_hist": {"6": 56}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9722, "mean": 0.9773, "max": 0.9858, "std": 0.0061, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.557, "extent_A": 19.623, "thickness_H_H_A": 19.6233, "thickness_O_O_A": 18.2137, "thickness_In_In_A": 15.4861}}
- `slab2r_pdos_cpu/scf.in`: {"n_atoms": 176, "composition": {"H": 24, "In": 56, "O": 96}, "cell_lengths_A": [10.31792, 10.30849, 45.18063], "cell_angles_deg": [90.0, 90.0, 90.0], "volume_A3": 4805.5089, "density_g_cm3": 2.7609, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 336, "min": 2.1616, "mean": 2.2197, "max": 2.3007, "std": 0.0357, "CN_In_hist": {"6": 56}}, "O-H": {"cutoff_A": 1.2, "n": 24, "min": 0.9722, "mean": 0.9773, "max": 0.9858, "std": 0.0061, "CN_O_hist": {"0": 72, "1": 24}}}, "CN_O_by_cations_hist": {"2": 24, "4": 72}, "slab": {"vacuum_A": 25.557, "extent_A": 19.623, "thickness_H_H_A": 19.6233, "thickness_O_O_A": 18.2137, "thickness_In_In_A": 15.4861}}

Geometry consistency (input of the follow-on step vs relax final coordinates): {"iwo_slab2_W24d/scf.in vs final of iwo_slab2_W24d/relax.out": {"max_pos_diff_A": 0.0, "max_cell_diff_A": 0.0}, "iwo_slab2_W24d/bands.in vs final of iwo_slab2_W24d/relax.out": {"max_pos_diff_A": 0.0, "max_cell_diff_A": 0.0}, "slab2_relax_c2/scf.in vs final of slab2_relax_c2/vcrelax.out": {"max_pos_diff_A": 0.0, "max_cell_diff_A": 0.0}, "slab2_relax_c2/bands.in vs final of slab2_relax_c2/vcrelax.out": {"max_pos_diff_A": 0.0, "max_cell_diff_A": 0.0}}

## Planar average `slab2_relax_c2/slab2_relax_c2_avg.dat`

{"n_points": 3000, "V_min_eV": -7.9484, "V_max_eV": 5.7662, "window_A": 0.01506, "z_mean_V_eV": 1.71003, "E_vac_eV": 5.76622, "vacuum_flatness_meV": 0.019, "vacuum_slope_meV_per_A": 0.0001, "IP_eV": 5.7189, "EA_eV": 4.495}

## Planar average `slab2r_final_cpu/slab2r_final_cpu_avg.dat`

{"n_points": 3000, "V_min_eV": -7.9484, "V_max_eV": 5.7662, "window_A": 0.01506, "z_mean_V_eV": 1.71003, "E_vac_eV": 5.76621, "vacuum_flatness_meV": 0.019, "vacuum_slope_meV_per_A": 0.0001, "IP_eV": 5.7188, "EA_eV": 4.4949}
- `slab2_relax_c2/avg_slab2_relax_c2.in` input: `1 slab2_relax_c2_v.pp 1.0 3000 3 4.8689`
- `slab2_relax_c2/pp_slab2_relax_c2.in` input: `&INPUTPP prefix = 'slab', outdir = './tmp', filplot = 'slab2_relax_c2_v.pp', plot_num = 11 /`
- `slab2r_final_cpu/avg_slab2r_final_cpu.in` input: `1 slab2r_final_cpu_v.pp 1.0 3000 3 4.8745`
- `slab2r_final_cpu/pp_slab2r_final_cpu.in` input: `&INPUTPP prefix = 'slab', outdir = './tmp', filplot = 'slab2r_final_cpu_v.pp', plot_num = 11 /`
- `slab2_relax_c2/avg_slab2_relax_c2.out`: done True; Program AVERAGE v.7.5 starts on  4Oct2026 at  3:37: 6 / Reading header from file  slab2_relax_c2_v.pp / Reading data from file  slab2_relax_c2_v.pp / AVERAGE      :      4.22s CPU      4.41s WALL / This run was terminated on:   3:37:11   4Oct2026
- `slab2_relax_c2/pp_slab2_relax_c2.out`: done True; Program POST-PROC v.7.5 starts on  4Oct2026 at  3:36:49 / Reading xml data from directory: / Calling punch_plot, plot_num =  11 / Writing data to file  slab2_relax_c2_v.pp / POST-PROC    :     13.74s CPU     14.71s WALL
- `slab2r_final_cpu/avg_slab2r_final_cpu.out`: done True; Program AVERAGE v.7.5 starts on  5Oct2026 at  1:33:46 / Reading header from file  slab2r_final_cpu_v.pp / Reading data from file  slab2r_final_cpu_v.pp / AVERAGE      :      5.88s CPU      6.01s WALL / This run was terminated on:   1:33:52   5Oct2026
- `slab2r_final_cpu/pp_slab2r_final_cpu.out`: done True; Program POST-PROC v.7.5 starts on  5Oct2026 at  1:33:19 / Reading xml data from directory: / Calling punch_plot, plot_num =  11 / Writing data to file  slab2r_final_cpu_v.pp / POST-PROC    :     24.25s CPU     25.50s WALL

## Other files

- `snapshots.log`: '2026-10-03T06:14:29Z slab2_relax_c2 (12806569.0): 40 bfgs steps, files: slab2_relax_c2_driver.log vcrelax.in vcrelax.out vcrelax_initial.in \n2026-10-03T06:14:31Z slab2_relax_c2__cpu (12806569.1): 2 bfgs steps, files: slab2_relax_c2__cpu_driver.log vcrelax.in vcrelax.out vcrelax_initial.in \n2026-10-0'

## Checks against RESULTS_LOG

| quantity | re-derived | logged | reference | status |
|---|---|---|---|---|
| slab2_relax_c2 CPU twin: completed SCF (geometry) steps in its last snapshot (BFGS counter reached 1) | 2 | 2 | RESULTS_LOG.md:580 | match |
| slab2r_final_cpu bands step pools (log -nk 4) | 4 | 4 | RESULTS_LOG.md:541 | match |
| iwo_slab2_W24d final-SCF snapshot: QE version (log: 7.5 CPU) | v.7.5 | v.7.5 | RESULTS_LOG.md:509 | match |
| iwo_slab2_W24d final-SCF snapshot: MPI processes (log: 33) | 33 | 33 | RESULTS_LOG.md:509 | match |
| iwo_slab2_W24d final SCF ran on the GPU? (scf.out GPU lines; node had an H100) | False | True | RESULTS_LOG.md:533 | DIFFERS (dated erratum 2026-10-14 in RESULTS_LOG) |
| iwo_slab2_W24d final-SCF snapshot: SCF iterations reached (log: 86) | 86 | 86 | RESULTS_LOG.md:509 | match |
