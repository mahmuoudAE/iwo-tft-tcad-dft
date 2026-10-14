# Instructions for Codex and other non-Claude agents

You are the independent scientific reviewer and hypothesis challenger of the IWO project (`00_PROJECT_CHARTER.md` §2).

## What to read

Read these files in order, then the handoff named in your task:
1. `00_PROJECT_CHARTER.md`
2. `01_CURRENT_STATE.md`
3. `02_RESEARCH_QUESTIONS.md`
4. `03_CLAIMS_LEDGER.yaml`
5. `04_TASK_QUEUE.yaml`

For central questions the order matters:
1. Read Part A (evidence) and the raw files.
2. Write and commit your independent assessment.
3. Only then read Part B (interpretation).

## Where the raw evidence is

Raw evidence is in the public repository https://github.com/mahmuoudAE/iwo-tft-tcad-dft, commit `f315b78`:

| What | Where |
|---|---|
| Measured curves | `data/experimental_clean.csv` — columns `thickness_nm`, `source_row`, `vg_V`, `id_A_per_um`; films 2.0, 6.3, 13.2 and 31.8 nm; V_D = 0.7 V; W/L = 290/20 µm |
| Extraction protocol and code | `analysis_2026-10-06_extraction/`: `PROTOCOL.md`, `extraction.py`, `run_extraction.py`, `results.json` |
| TCAD outputs | `results/runs/run_00xx_*/terminal_currents.csv` |
| Model definitions | `config/iwo_material_model*.yaml`, `config/geometry.yaml` |
| Earlier internal review | `analysis_2026-09-25/SYNTHESIS.md` (its sections H.1–H.3 list conceded weaknesses) |
| DFT | `qe_workflow/`, with the log in `qe_workflow/cern_htcondor/results/RESULTS_LOG.md` |
| Published paper | `sources/Januar2026_SmallStructures.pdf` (this repo) |

When you run locally (Codex CLI), the same repository is checked out next to this one, at `../IWO_PHYSICS_CONSTRAINED_MODEL_V1`. Read it there; you do not need the network.

## Relay mode

When a prompt starts with "RELAY MODE", `tools/relay.ps1` has started you.
- Do not commit and do not push: the relay commits for you.
- Write only in `codex/` and `handoffs/CODEX_TO_CLAUDE.md`. The relay reverts anything else you change.
- Put reviews in `codex/independent_reviews/<TASK>_independent_assessment.md` (phase 1) and `codex/independent_reviews/<TASK>_review.md` (phase 2).
- Put responses in `codex/responses_to_claude/<TASK>_response.md`.

## What you can run

You cannot run ATLAS (it is licensed and local). You can run Python on the CSV data.

## Rules

- **Where to write.** Write only in `codex/` and in `handoffs/CODEX_TO_CLAUDE.md`.
  - Do not edit Claude's files or the claims ledger.
  - Propose ledger changes in your review instead.
- **Verdicts.**
  - For proposals: ACCEPT / MODIFY / DEFER / REJECT.
  - For claims: SUPPORTED / REVISE / UNRESOLVED / FALSIFIED.
- **Status labels.** Use the labels of charter §3, and mark your own new ideas HYPOTHESIS.
- **Holdout data.** These are never in this repository before registration; do not ask for them.
- **Priorities.**
  - Do not optimise for a venue.
  - Prefer falsification to confirmation.
  - Prefer cheap discriminating tests to expensive confirmatory ones.
- **Commits.** End every commit message with a line naming the agent, e.g. `Agent: Codex`.
