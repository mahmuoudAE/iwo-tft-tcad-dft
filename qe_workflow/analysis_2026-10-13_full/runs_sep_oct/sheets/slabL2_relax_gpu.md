# slabL2_relax_gpu

**Purpose.** Superseded 0.75 nm slab relax (marker only; replaced by slabL2_relax_v2).

Folder `cern_htcondor/results/slabL2_relax_gpu`; data `runs_sep_oct/out/slabL2_relax_gpu.json` (+ `slabL2_relax_gpu_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| SUPERSEDED.txt | 239 | ff2b36c6307c8e1c | loose | other |

## Resources and run history

- HTCondor slabL2_relax_gpu 12835237.1: 16 CPUs, 0 GPU; seen 2026-10-05T17:51:31Z to 2026-10-05T21:12:33Z (34 samples); states {'2': 34} (1 idle, 2 running, 3 removed, 5 held); max scf_it 66, max BFGS 0; steps ['vcrelax']; hw ['', 'Intel(R) Xeon(R) Silver 4216 CPU @ 2.10GHz'] ['', 'Intel(R) Xeon(R) Silver 4216 CPU @ 2.10GHz']

**What failed and why (from the files above).** Removed 2026-10-05T21:14Z, superseded by slabL2_relax_v2 (identical inputs); no results kept (SUPERSEDED.txt).

## Other files

- `.fetched`: ''
- `SUPERSEDED.txt`: 'Removed 2026-10-05T21:14Z: superseded by the faster copy slabL2_relax_v2 (and its CPU twin slabL2_relax_v2__cpu), identical inputs. The .fetched marker stops dft_flow.sh from fetching or continuing this job; no results were kept from it.'
