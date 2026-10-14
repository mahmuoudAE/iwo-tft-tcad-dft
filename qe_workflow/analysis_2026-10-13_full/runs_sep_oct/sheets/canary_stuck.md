# canary_stuck

**Purpose.** Workflow test: a job that only sleeps 4500 s (stuck-job detection).

Folder `cern_htcondor/results/canary_stuck`; data `runs_sep_oct/out/canary_stuck.json` (+ `canary_stuck_arrays.json.gz`: eigenvalues and occupations at every k, SCF accuracy traces, final forces, Loewdin charges per atom). All crystalline. Values COMPUTED (read from the outputs).

## Files

| path | bytes | sha256 (16) | source | kind |
|---|---|---|---|---|
| .fetched | 0 | e3b0c44298fc1c14 | loose | other |
| canary_stuck_driver.log | 255 | 255f67f3d0aeaade | loose | driver |
| steps.sh | 25 | fb349771440d1c41 | loose | steps |

Tarball `canary_stuck_results.tar.gz` (345 B, sha256 33fe829808ce41da): 2 members; identical to the loose copy: 2; DIFFERENT from the loose copy: none; only in the tarball (parsed from it): none; pdos members: 0

## Resources and run history

- `canary_stuck_driver.log`: host b9g42p1019.cern.ch, 2 CPUs, wall limit 7200 s, GPU: none (CPU), job total 4517 s, start 2026-09-30T08:06:13Z
- HTCondor: no entry in status_history.jsonl (it starts 2026-09-28T14:19Z).
- `steps.sh`: `steps() { sleep 4500 }`

**What failed and why (from the files above).** By design: steps() only sleeps 4500 s (stuck-job detection test); no pw.x run.

## Other files

- `.fetched`: ''
