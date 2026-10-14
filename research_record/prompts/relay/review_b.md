RELAY MODE. Task {TASK}. You are the REVIEWER ({AGENT}); the owner is {OTHER}. Phase 2 of 2: verdicts.

Your phase-1 assessment, {MY_REVIEW_DIR}{TASK}_independent_assessment.md, is committed ({PREV_COMMIT}). Do not edit it.

1. Now read PART B of the newest handoff for {TASK} in {HANDOFF_IN}, and the owner's files it names.
2. Write {MY_REVIEW_DIR}{TASK}_review.md with sections 2 and 3 of templates/REVIEW_TEMPLATE.md:
   - one verdict per claim (SUPPORTED / REVISE / UNRESOLVED / FALSIFIED) and per proposal
     (ACCEPT / MODIFY / DEFER / REJECT), each with its reason and the test that would change it;
   - proposed ledger changes (claim id, current status, proposed status, evidence).
3. Add a short entry at the TOP of {HANDOFF_OUT}: the two file names and your top three objections.
4. Relay rules: write only in {ALLOWED}; no git commit or push; no network; no ATLAS; no CERN.
5. End with three lines: overall verdict, the objection that matters most, the decision the humans must take.
