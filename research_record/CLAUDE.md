# Instructions for Claude Code in this repository

This is the PRIVATE research record of the IWO (W:In2O3) thin-film-transistor project. Never make it public.

At the start of every session, read in this order:
1. `00_PROJECT_CHARTER.md`
2. `01_CURRENT_STATE.md`
3. `04_TASK_QUEUE.yaml`
4. `05_DECISION_LOG.md`
5. the newest files in `handoffs/` and `codex/`

## Your role

You own the computational and evidence tasks, and you review Codex's tasks (charter §2).

- Work on tasks from `04_TASK_QUEUE.yaml`, or on what the user asks in chat. In the second case, add the task to the queue.
- End every task with a handoff (`templates/HANDOFF_TEMPLATE.md`) that keeps evidence (Part A) apart from interpretation (Part B).
- Update `03_CLAIMS_LEDGER.yaml` whenever a claim's status changes.

## Workspace

| What | Where |
|---|---|
| This private record | `C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\iwo-tft-research-private` |
| Public code and analysis of the published data | `..\IWO_PHYSICS_CONSTRAINED_MODEL_V1`. Git branch `main`, remote github.com/mahmuoudAE/iwo-tft-tcad-dft, evidence commit `f315b78`. |
| Older packages (read only, never overwrite) | `..\IWO_ATLAS_Model_claude` (V0; it holds the Python venv) and the Astra package |
| Python | `..\IWO_ATLAS_Model_claude\.venv\Scripts\python.exe`. System Python 3.13 also has pandas, but no openpyxl. |
| Silvaco ATLAS 5.28 (32-bit, ~30k nodes) | `C:\sedatools`. Launch only through `scripts/run_atlas.py` of the public repo. The launch budget is in `config/solver.yaml` (60 of 71 used). |
| Quantum ESPRESSO 7.5 | WSL `Ubuntu-22.04`, conda env `qe` (`~/miniforge3/envs/qe`) |
| CERN lxplus / HTCondor | Through WSL `Ubuntu`, using the SSH ControlMaster socket `~/.ssh/cm-cern`. Scripts are in `qe_workflow/cern_htcondor/` (`dft_flow.sh`, `snapshot_jobs.sh`). |
| Thesis report (LaTeX) | `..\IWO_PHYSICS_CONSTRAINED_MODEL_V1\report_latex_full`. Build with `tools/build_pdf.py`; MiKTeX lives under `%LOCALAPPDATA%\Programs\MiKTeX` and is not on PATH. |

## Hard rules

### CERN
- Never request, store, print or enter the CERN password or 2FA code. The user logs in.
- Before any CERN action, run `ssh -O check`. If the master connection is gone, stop and ask the user to log in.
- Submit jobs through HTCondor only.

### GitHub, public repo
- Standing permission: commit and push corrections from WSL `Ubuntu` with `tools/push_public.sh`. That script runs a secret scan and a 50 MB file check first.
- The credential store holds the token. Never read or print it.
- Never put restricted or unpublished data in the public repo.

### GitHub, this private repo
- The remote is github.com/mahmuoudAE/iwo-tft-research-private (private).
- Push only when the user asks, unless `05_DECISION_LOG.md` records a standing permission.
- Always push with `tools/push_private.sh`. It aborts unless the unauthenticated GitHub API returns 404 (i.e. the repo is private), and it scans for secrets with `grep -a`.

### ATLAS
- Run launches one at a time.
- Write sweeps as stepped `solve vstep=... vfinal=... name=gate` blocks.
- Keep the physical structure (`structure: full`).
- Ask before queuing more than a handful of launches, and before raising the budget.
- Solver pitfalls are listed in `01_CURRENT_STATE.md` §K.

### Integrity
- Never overwrite raw data or original outputs.
- Never delete negative results.
- Register predictions before the data are seen (charter §7).
- Holdout data must never enter this repository before registration.

### Commits
End every commit message with `Co-Authored-By: Claude <noreply@anthropic.com>`, naming the model in use.

## Project tools in `.claude/`

| Kind | Items |
|---|---|
| Subagents | `evidence-auditor`, `atlas-runner`, `dft-cern`, `figure-maker`, `ledger-keeper` |
| Commands | `/status`, `/handoff <TASK>`, `/register <REG> <title>`, `/review <TASK>` |
| Hook (`.claude/hooks/guard.py`) | Blocks a raw `git push` and any change to `data_private/raw/`. Asks the user before ATLAS launches and CERN actions. |

## Relay mode

When a prompt starts with "RELAY MODE", `tools/relay.ps1` has started you headless.
- Do not commit, push, launch ATLAS or contact CERN: the relay commits for you, and the hook refuses the rest.
- Write only in the areas the prompt lists. The relay reverts anything else.
- Claude's reviews of Codex tasks go to `claude/reviews/<TASK>_independent_assessment.md` and `claude/reviews/<TASK>_review.md`.
- Responses go to `claude/responses_to_codex/<TASK>_response.md`.

## How the user works

- **Language.** Plain language. Explain terms, and give every number with units and a source.
- **Figures.**
  - Use a plain plotting-software style (Origin-like): no text boxes inside the panels; everything is explained in the captions.
  - Use the panel letters the user asks for.
- **Honest framing.**
  - Say what was fitted and what was tested.
  - Report mismatches as findings (decision D-06).
  - Never cherry-pick windows, devices or floor treatments to manufacture agreement.
- **Compute.** Few, well-chosen ATLAS launches. Start expensive compute only after the user says go.
