# Prompt 1: start a new Claude Code chat

## Before you paste it

1. In the Claude desktop app, open a new Code session with the working folder set to
   `C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\iwo-tft-research-private`.
2. Add these folders to the session:
   - `C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1` (the public repo checkout);
   - `...\IWO_PHYSICS_CONSTRAINED_MODEL_V1\qe_workflow`.
3. `CLAUDE.md` loads automatically. The prompt below therefore stays short; the context lives in the files, not in the chat.

## Paste this

```text
You are continuing the IWO TFT research project in a fresh session. The repository in this folder is the
project's private research record; CLAUDE.md has the rules and the paths.

1. Read 00_PROJECT_CHARTER.md, 01_CURRENT_STATE.md, 02_RESEARCH_QUESTIONS.md, 03_CLAIMS_LEDGER.yaml,
   04_TASK_QUEUE.yaml, 05_DECISION_LOG.md and handoffs/CLAUDE_TO_CODEX.md.
2. Spot-check 01_CURRENT_STATE.md against the public repo (../IWO_PHYSICS_CONSTRAINED_MODEL_V1 at commit
   f315b78). Re-derive at least: V_th,cc and the floors from data/experimental_clean.csv, the T3 numbers from
   analysis_2026-10-06_V2/T2_T3_RESULTS.md, and the mobility peaks from analysis_2026-10-06_extraction/mobility_vs_vg.csv.
   Report every mismatch. Do not fix anything silently.
3. Tell me in no more than 15 lines what you understand the state to be, what is blocked on humans, and which
   task you will start.
4. Then start RQ-001 (mobility and SS definitions) as owner. Work in claude/evidence/RQ-001/, end with a
   handoff in handoffs/CLAUDE_TO_CODEX.md (Part A evidence, Part B interpretation), and commit.

Do not launch ATLAS, submit CERN jobs or push anywhere without my explicit go.
```

## Later sessions

Use this short prompt:

```text
Continue the IWO project. Read CLAUDE.md, 04_TASK_QUEUE.yaml, 05_DECISION_LOG.md and the newest files in handoffs/
and codex/. Summarise in 10 lines what changed since the last commit you made, then continue with <TASK-ID>.
```
