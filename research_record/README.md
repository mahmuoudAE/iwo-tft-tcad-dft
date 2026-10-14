# iwo-tft-research-private

This is the PRIVATE research record of the IWO (W:In2O3) thin-film-transistor project, which combines TCAD, DFT and experiments with the NTU fab group. Keep this repository private.

The public, reproducible code and the analysis of the published data live in another repository: https://github.com/mahmuoudAE/iwo-tft-tcad-dft (local copy: `../IWO_PHYSICS_CONSTRAINED_MODEL_V1`).

## Start here

| File | What it is |
|---|---|
| `00_PROJECT_CHARTER.md` | Rules for the humans and the AI agents |
| `01_CURRENT_STATE.md` | What exists, with pointers to the evidence |
| `02_RESEARCH_QUESTIONS.md` | The hypotheses being tested |
| `03_CLAIMS_LEDGER.yaml` | Every claim, with its status label |
| `04_TASK_QUEUE.yaml` | Who does what next |
| `05_DECISION_LOG.md` | Decisions made by the humans |
| `CLAUDE.md` / `AGENTS.md` | Instructions that Claude Code and Codex load automatically |
| `prompts/` | Ready-to-paste prompts: a new Claude chat, the Codex review, Astra's hypotheses and arbitration. `prompts/relay/` holds the relay's templates. |
| `SETUP_AGENTS.md` | Step-by-step setup of Claude Code + Codex and the relay (`tools/relay.ps1`) |

## Folders

| Folder | What goes in it |
|---|---|
| `claude/` | Claude's plans, evidence, reports and responses |
| `codex/` | Codex's reviews, hypothesis tests and experiment designs |
| `handoffs/` | Messages between the agents |
| `predictions/` | `registered/` before any data are revealed; `revealed/` after |
| `decisions/` | Arbitration outputs |
| `data_private/` | Unpublished data, only after registration (see its README) |
| `templates/` | File formats |
| `tools/` | Push helpers |
| `sources/` | The published paper |
