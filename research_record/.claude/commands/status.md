---
description: Project state in 15 lines (tasks, decisions, newest handoffs and reviews); edits nothing
---
Read 04_TASK_QUEUE.yaml, 05_DECISION_LOG.md, the newest entries in handoffs/, codex/ and claude/reviews/, and the output
of `git log --oneline -10` (use `wsl -d Ubuntu -- git ...` if git is not installed on Windows).

Report in at most 15 lines:
1. what changed since the last commit made by Claude;
2. open tasks by owner and status;
3. what is blocked on the humans (HUM-* tasks, PENDING decisions);
4. the single next step you recommend, and which agent should take it.

Do not edit any file.
