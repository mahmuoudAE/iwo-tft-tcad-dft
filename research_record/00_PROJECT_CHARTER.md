# IWO research collaboration charter

This charter applies to:
- the humans: Mahmoud, Mukul, Prof. Wu and the NTU fab group;
- the AI agents: Claude Code, Codex and Astra.

Status: **PROPOSED 2026-10-07.** Record its adoption in `05_DECISION_LOG.md`.

## 1. Objective

The objective is the strongest scientifically defensible result the IWO project can produce.

A Nature-family paper is the ambition (decision D-08 in the log). It is not the optimisation target, so no claim is shaped to fit a venue.

## 2. Roles

| | Claude Code | Codex / Astra |
|---|---|---|
| Primary role | Evidence engineer; computational lead (ATLAS, Quantum ESPRESSO, analysis); provenance and reproducibility; keeper of the claims ledger | Independent reviewer; hypothesis challenger; physics strategist; experiment designer |
| Must not | Declare its own interpretation proven | Change computational evidence to fit its preferred explanation |
| Can run | ATLAS (local licence), QE (local and CERN), Python | Python on the repository data; reasoning and designs |

Humans decide (Section 9). The split separates duties; it says nothing about capability.

## 3. Status labels

Every scientific statement carries exactly one label:

`OBSERVED` · `MEASURED` · `COMPUTED` · `DERIVED` · `FITTED` · `LITERATURE-SUPPORTED` · `INFERRED` · `HYPOTHESIS` · `UNRESOLVED` · `FALSIFIED`

| Label | Meaning |
|---|---|
| MEASURED | Raw instrument data |
| DERIVED | A quantity extracted from data by a written protocol |
| FITTED | A parameter or law adjusted to data |
| COMPUTED | Output of a simulation with stated inputs |
| OBSERVED | A pattern seen in data, not yet quantified by a protocol |

Never promote a statement to a stronger label without new evidence. Record every promotion and demotion in `03_CLAIMS_LEDGER.yaml`.

## 4. Fitting rule

**No target-device-specific post-hoc fitting.**

- Global parameters may be calibrated on a declared calibration set and on independent measurements (C–V, Hall, XRR, temperature data and similar).
- After calibration the model is frozen with a commit and a tag. Predictions for new thicknesses, compositions or devices are then registered before the data are seen.
- Anything tuned after a holdout has been revealed is calibration and is never called prediction.

## 5. Communication

- Agents communicate through files and commits, never through undocumented chat.
- Chat history is not the scientific record; the repository is.
- Agreement between AI systems is not evidence. Experiments, registered predictions and the judgement of human experts are.

Every handoff follows `templates/HANDOFF_TEMPLATE.md` and contains these fields:
- TASK ID
- GIT COMMIT
- QUESTION
- DATA USED
- DATA EXCLUDED
- METHOD
- RESULT
- UNCERTAINTY
- INTERPRETATION
- ALTERNATIVE INTERPRETATIONS
- WHAT WOULD FALSIFY THE RESULT
- FILES CREATED
- RECOMMENDED NEXT ACTION

A handoff is split into Part A (evidence) and Part B (interpretation).

## 6. Independence rule

For a central question the reviewer works in this order:
1. Read Part A of the handoff and the raw files.
2. Write an independent assessment and commit it.
3. Only then read Part B and give a verdict: `SUPPORTED` · `REVISE` · `UNRESOLVED` · `FALSIFIED`.

The owner answers each objection in one of three ways: new evidence, a changed claim, or a discriminating test. Rhetoric is not an answer.

**Process weight.**
- The full loop (owner → independent review → response → arbitration) is only for central items: registrations, headline claims, and decisions that cost a fab run or more than a week of compute.
- Routine tasks get the owner's work plus a light review.
- AI reviewers share training priors and can share blind spots. The real safeguards are holdout custody, external timestamps and the humans.

## 7. Prediction rule

1. Define the calibration data.
2. Define the holdout data.
3. Freeze the model with a commit and a tag.
4. Register the numerical predictions, with uncertainties and pass/fail criteria (`templates/PREDICTION_REGISTRATION_TEMPLATE.md`).
5. Timestamp the registration outside this repository: a Zenodo or OSF DOI, or at least a tag pushed to GitHub.
6. Only then does the custodian release the holdout data.

Before step 5, holdout data never enter any repository, chat or AI tool. The fab, as data custodian, holds them.

## 8. Data rules

- Never overwrite raw measurements or original DFT/TCAD outputs.
- Never delete negative results.
- Never move unpublished or permission-restricted data to a public repository.
- Unpublished fab data go to AI services (Anthropic, OpenAI) only with the fab's consent.
- Known issue: the raw curves from the published paper are already in the public repository (`01_CURRENT_STATE.md` §H.6). Permission is pending.

## 9. Decision rule

Humans have final authority:
- Mahmoud, with Mukul and Prof. Wu;
- the fab, for anything involving its devices, data or authorship.

AI agents recommend. Without explicit approval they may not:
- start expensive calculations;
- commit to fab campaigns;
- release data publicly;
- push to a new remote;
- put claims in a manuscript.

Accepted decisions are recorded in `05_DECISION_LOG.md` and nowhere else.
