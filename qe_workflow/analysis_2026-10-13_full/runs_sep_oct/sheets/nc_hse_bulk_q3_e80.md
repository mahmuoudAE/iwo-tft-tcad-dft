# nc_hse_bulk_q3_e80

**Purpose.** HSE06 bulk with EXX q 3x3x3 and default ecutfock (did not run to completion).

Folder `cern_htcondor/results/nc_hse_bulk_q3_e80`; data `runs_sep_oct/out/nc_hse_bulk_q3_e80.json` (+ `nc_hse_bulk_q3_e80_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| nc_hse_bulk_q3_e80_driver.log | 436 | 05bc1eef89e5f641 | loose | driver |
| scf.in | 2487 | b254f45ae2ea635c | loose | pw_in |
| scf.out | 1960 | bb7b35897c3ca189 | loose | mpi_error |
| steps.sh | 27 | a7d5ef8aefb09efb | loose | steps |

Tarball `nc_hse_bulk_q3_e80_results.tar.gz` (2030 B, sha256 0683ba44b1b3d448): 4 members; identical to the loose copy: 4; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0

## Resources and run history

- `nc_hse_bulk_q3_e80_driver.log`: host b9pgpun003.cern.ch, 11 CPUs, wall limit 86400 s, GPU: 1 GPU(s), NVIDIA H100 NVL, 95830 MiB, job total 95 s, start 2026-09-30T17:34:46Z
  - step scf: -nk 1, max_seconds 84565, start 2026-09-30T17:35:21Z, end 2026-09-30T17:36:21Z, rc 1, 
- HTCondor: no entry in status_history.jsonl (it starts 2026-09-28T14:19Z).
- `steps.sh`: `steps() { run_pw scf 1 }`
- MPI start failure in `scf.out`: As of version 3.0.0, the "sm" BTL is no longer available in Open MPI. / Host:      b9pgpun003.cern.ch / Component: sm / It looks like MPI_INIT failed for some reason; your parallel process is; signatures {mpi_init_failed: line 2}

**What failed and why (from the files above).** MPI_INIT failed before pw.x started (scf.out): the requested "sm" BTL component was not available in that Open MPI runtime and mca_bml_base_open() failed on b9pgpun003; rc 1 after 60 s. The q 3x3x3 bulk HSE was obtained instead by nc_hse_bulk_q3_f160_e80.

## Input geometries

- `scf.in`: {"n_atoms": 40, "composition": {"In": 16, "O": 24}, "cell_lengths_A": [8.92534, 8.92534, 8.92534], "cell_angles_deg": [109.471, 109.471, 109.471], "volume_A3": 547.3332, "density_g_cm3": 6.7384, "bonds": {"In-O": {"cutoff_A": 2.6, "n": 96, "min": 2.1671, "mean": 2.2194, "max": 2.2561, "std": 0.0336, "CN_In_hist": {"6": 16}}}, "CN_O_by_cations_hist": {"4": 24}}

## Other files

- `.fetched`: ''
