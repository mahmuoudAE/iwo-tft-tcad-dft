# Predictions

- `registered/`: one file per registration (`templates/PREDICTION_REGISTRATION_TEMPLATE.md`). It is written and timestamped before the holdout data are released.
- `revealed/`: the measured results and the pass/fail evaluation, written after the release.

## Rules (charter §7)

1. **Freeze first.** Register only after the model is frozen with a commit and a tag.
2. **Timestamp outside this repo.** Use a Zenodo or OSF DOI, or a tag pushed to GitHub.
3. **No edits afterwards.** Never edit a registered file once it has been timestamped.
4. **Keep the data out until then.** The custodian (the fab) releases holdout data only after the timestamp. Holdout data never enter this repo, any chat or any AI tool before the timestamp.
5. **Report everything.** Failed predictions are reported in full and never deleted.
