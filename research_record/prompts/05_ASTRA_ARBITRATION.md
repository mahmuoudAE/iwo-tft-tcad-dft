# Prompt 5: Astra arbitrates (only if the disagreement remains)

## Before you paste it

- Attach these files:
  - `claude/NATURE_PLAN.md`
  - `handoffs/CLAUDE_TO_CODEX.md` (HO-001)
  - both Codex review files
  - `claude/responses_to_codex/NATURE_PLAN_RESPONSE.md`
  - `01_CURRENT_STATE.md`
- Save the answer as `decisions/30_DAY_RESEARCH_DECISION.md`.
- It is a recommendation until the humans accept it in `05_DECISION_LOG.md`.
- Suggested level: xHigh.

## Paste this

```text
Act as the senior scientific adjudicator. Read Claude's plan, Claude's evidence handoff, Codex's independent
assessment and review, Claude's response, and the current-state file.

Do not choose a winner. For every disputed point classify:
RESOLVED BY EVIDENCE / CLAUDE STRONGER / CODEX STRONGER / UNRESOLVED / REQUIRES EXPERIMENT,
and say why in one or two sentences.

Then build ONE 30-day research programme with these constraints: maximum information gain; minimum unnecessary DFT;
minimum unnecessary fabrication; real holdout data preserved; rigour never traded for a headline; Nature publication
not assumed; falsification preferred over confirmation.

The programme must contain no more than:
3 computational priorities
3 experimental priorities
1 registered prediction (with its numbers, tolerances and the data custodian)
1 explicit stop/go criterion
```
