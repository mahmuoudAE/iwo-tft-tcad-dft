# IWO / In2O3 DFT workflow: quick start (VS Code)

Open this folder (`qe_workflow`) in VS Code. The tasks are under **Terminal > Run Task... > DFT: ...**. All of them call `dft_flow.sh`.

| Step | Task / command | Where it runs |
|---|---|---|
| 0 | `DFT: show CERN login command`: you type the printed ssh line and enter your password and 2FA yourself | WSL "Ubuntu" |
| 1 | `DFT: build structures`: builds and checks all cells and slabs from the relaxed bulk | local (WSL "Ubuntu-22.04", conda env `qe`) |
| 2 | `DFT: generate jobs`: writes `cern_htcondor/jobs/gen_<name>/`; the job list and sizes are in `cern_htcondor/jobs/make_jobs.py` | local |
| 3 | `DFT: submit jobs to CERN`: uploads and submits; skips jobs that are already queued or finished | CERN HTCondor |
| 4 | `DFT: watch` + `DFT: dashboard`: every 10 min it records status, fetches results and analyses them; live page at http://localhost:8767 | local + CERN |
| 5 | `DFT: missing jobs` / `DFT: resubmit missing jobs`: finds and resubmits jobs that have neither results nor a queue entry | CERN |
| 6 | `DFT: run one job locally`: runs the same job, with the same driver, on this computer; results go to `results_local/` | local |

## Files

**Protocols.** Methods, criteria (fixed in advance) and every deviation:
- `bulk_In2O3_protocol/PROTOCOL.md` (stages 1-3, local);
- `cern_htcondor/PROTOCOL_CERN.md` (stage 4).

**Results.**
- `cern_htcondor/results/<job>/`: one folder per job (raw outputs).
- `results/RESULTS_LOG.md`: the dated log.
- `results/summary.json`: all numbers, written by `collect_results.py`.

**Job driver.** `cern_htcondor/jobs/common/driver.sh` does four things:
- unpacks QE from EOS;
- forces 1 thread per MPI rank;
- stops pw.x before the wall-time limit;
- saves a checkpoint to EOS after every step (`/eos/user/m/melrashe/qe/checkpoints`); `fetch` downloads it if a job dies.

**Monitors.**
- `cern_htcondor/monitor.sh`: 30-min checks, used by Claude for notifications; log in `monitor.log`.
- `dft_flow.sh watch`: feeds the dashboard.

## Rules kept in every script
- No password or 2FA code is ever stored or typed by a script. Everything reuses the SSH session that you open yourself.
- Only numbers present in output files are reported. Missing values stay empty; nothing is estimated in their place.
