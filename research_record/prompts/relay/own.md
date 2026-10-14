RELAY MODE. Task {TASK}. You are the OWNER ({AGENT}); {OTHER} will review your work independently.

1. Read {INSTR}, 00_PROJECT_CHARTER.md, 01_CURRENT_STATE.md, 03_CLAIMS_LEDGER.yaml and the entry for {TASK} in
   04_TASK_QUEUE.yaml. Do the task exactly as specified there; if the entry is unclear, do the smallest defensible
   version and say what you left out.
2. Evidence: this repository and the public repository checkout at {PUBLIC} (evidence commit f315b78). Re-derive
   numbers from the rawest file; reuse the protocol code instead of re-implementing it.
3. Put your scripts, tables and figures in {AREA}{TASK}/.
4. Write a handoff at the TOP of {HANDOFF_OUT} with templates/HANDOFF_TEMPLATE.md: PART A evidence only, PART B
   interpretation, alternatives and falsifiers. Label every statement (charter section 3).
5. Relay rules:
   - write only in: {ALLOWED};
   - do NOT run git commit or git push (the relay commits and checks what you changed);
   - do NOT launch ATLAS, contact CERN, install software or use the network. If the task needs one of these,
     stop there and write it under RECOMMENDED NEXT ACTION.
6. End with five lines: what you did, the main result, the main uncertainty, open problems, files created.
