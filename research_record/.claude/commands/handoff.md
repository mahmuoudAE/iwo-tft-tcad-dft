---
description: Write the handoff for a finished task (Part A evidence, Part B interpretation), audit its numbers, update the record and commit locally
argument-hint: <TASK-ID>
---
Write the handoff for task $ARGUMENTS.

1. Use templates/HANDOFF_TEMPLATE.md. Put it at the TOP of handoffs/CLAUDE_TO_CODEX.md as the next HO number.
   Part A = evidence only (numbers with units, status labels, file paths, commits). Part B = interpretation,
   alternative interpretations, what would falsify the result, recommended next action.
2. Before saving, give every number in Part A to the evidence-auditor subagent and fix the handoff (not the
   evidence) where it reports a mismatch.
3. Let the ledger-keeper subagent update 03_CLAIMS_LEDGER.yaml, 01_CURRENT_STATE.md and 04_TASK_QUEUE.yaml
   (status IN_REVIEW, reviewer named).
4. Commit locally with a message "<TASK-ID>: <one-line result>" ending with the Co-Authored-By line. Do not push.
5. Tell me the commit hash and the exact command for the review step:
   pwsh -ExecutionPolicy Bypass -File tools\relay.ps1 -Task $ARGUMENTS -Owner claude -Step review
