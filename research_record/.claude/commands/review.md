---
description: Review a task owned by Codex - independent assessment first (committed), then verdicts
argument-hint: <TASK-ID>
---
You are the reviewer of task $ARGUMENTS, which Codex owns.

Phase 1 (independent assessment):
1. Read only PART A of the newest handoff for $ARGUMENTS in handoffs/CODEX_TO_CLAUDE.md and the files it cites.
   Do not read Part B or Codex's interpretation files yet.
2. Re-derive the key numbers (use the evidence-auditor subagent).
3. Write claude/reviews/$ARGUMENTS_independent_assessment.md (templates/REVIEW_TEMPLATE.md section 1) and commit it locally.

Phase 2 (verdicts):
4. Now read Part B and the files it names.
5. Write claude/reviews/$ARGUMENTS_review.md (sections 2 and 3): one verdict per claim or proposal with the reason and
   the test that would change it; proposed ledger changes.
6. Add a short pointer at the top of handoffs/CLAUDE_TO_CODEX.md, commit locally, do not push.
