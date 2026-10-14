---
description: Draft a prediction registration (frozen model, holdout, numbers with uncertainties, pass/fail rule) before any data are revealed
argument-hint: <REG-number> <short title>
---
Draft the prediction registration $ARGUMENTS with templates/PREDICTION_REGISTRATION_TEMPLATE.md in
predictions/registered/.

1. Check that the model is frozen: name the commit and propose a tag (e.g. `model-v3-frozen-<date>`). If it is not
   frozen, stop and say what must be frozen first.
2. State the calibration data and the holdout data exactly, and who holds the holdout (the fab).
3. Give each predicted quantity with its extraction script and commit, its value, its uncertainty and its pass criterion.
   Give the competing model's prediction for the same quantities.
4. Write the decision rule for pass / fail / partial pass.
5. Leave the timestamp section empty: the external timestamp (Zenodo/OSF DOI or a pushed tag) is a human step.
   Remind me of it, and that the custodian must not release the data before it.

Never look at, request or simulate the holdout data.
