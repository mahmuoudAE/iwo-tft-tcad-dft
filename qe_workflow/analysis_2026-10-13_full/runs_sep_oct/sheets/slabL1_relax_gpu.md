# slabL1_relax_gpu

**Purpose.** Superseded 0.51 nm slab relax (marker only; replaced by slabL1_relax_v2).

Folder `cern_htcondor/results/slabL1_relax_gpu`; data `runs_sep_oct/out/slabL1_relax_gpu.json` (+ `slabL1_relax_gpu_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| SUPERSEDED.txt | 239 | 189f6bf23009db19 | loose | other |

## Resources and run history

- HTCondor slabL1_relax_gpu 12835237.0: 16 CPUs, 0 GPU; seen 2026-10-05T17:51:31Z to 2026-10-05T21:12:33Z (34 samples); states {'2': 34} (1 idle, 2 running, 3 removed, 5 held); max scf_it 475, max BFGS 10; steps ['vcrelax']; hw  ['AMD EPYC 9655 96-Core Processor']

**What failed and why (from the files above).** Removed 2026-10-05T21:14Z, superseded by slabL1_relax_v2 (identical inputs); no results kept (SUPERSEDED.txt).

## Other files

- `.fetched`: ''
- `SUPERSEDED.txt`: 'Removed 2026-10-05T21:14Z: superseded by the faster copy slabL1_relax_v2 (and its CPU twin slabL1_relax_v2__cpu), identical inputs. The .fetched marker stops dft_flow.sh from fetching or continuing this job; no results were kept from it.'
