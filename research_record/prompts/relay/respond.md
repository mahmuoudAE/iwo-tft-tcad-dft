RELAY MODE. Task {TASK}. You are the OWNER ({AGENT}) answering the review by {OTHER}.

1. Read {OTHER_REVIEW_DIR}{TASK}_independent_assessment.md and {OTHER_REVIEW_DIR}{TASK}_review.md.
2. Do NOT defend your work. For every objection add one row to a table:
   objection | evidence supporting it | evidence against it | your original assumption | revised assessment |
   test that would resolve it | action
   and classify it ACCEPTED / PARTIALLY ACCEPTED / EVIDENCE DISAGREES / UNRESOLVED.
   Leave UNRESOLVED whatever the evidence cannot settle. Do not resolve uncertainty rhetorically.
3. Write {RESPONSE_FILE}. Change your own earlier files only where an objection is ACCEPTED, and log each change at
   the bottom of the changed file. {LEDGER_RULE}
4. Relay rules: write only in {ALLOWED}; no git commit or push; no network; no ATLAS; no CERN.
5. End with the decisions the humans must take (at most three), each with the options and your recommendation.
