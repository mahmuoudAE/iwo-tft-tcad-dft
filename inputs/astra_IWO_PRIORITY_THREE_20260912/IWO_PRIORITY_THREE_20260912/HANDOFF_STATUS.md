# IWO priority-three handoff

Updated 2026-09-12T13:59:20.758149+00:00. No simulator is running. This delivery is a numerically checked active-region calibration checkpoint, not full-curve or predictive validation.

## Outcome and selected native runs

| Film | Selected run | Active log RMSE (decade) | Ion error at +3 V | All-121 signed linear RMSE (A/um) | Numerical evidence |
|---|---|---:|---:|---:|---|
| 2 nm | 20260912T074527_865393_fit_bulk_width04_2nm | 0.03339362339 | +0.6903669% | 4.60278386e-9 | Native width, x, y, DOS PASS |
| 6.3 nm | 20260912T124657_803129_priority3_fit6_mu12_retry2 | 0.04920549218 | +1.96668265% | 9.95395622e-9 | Exact-candidate x, y, DOS PASS; width-unit convention transferred from 2 nm |
| 13.2 nm | 20260912T122359_458630_priority3_fit13_nd89 | 0.04902803895 | +2.45229844% | 4.70914158e-8 | Exact-candidate x/y PASS; DOS MISSING; overall INCOMPLETE |

All selected runs completed all 121 native gate targets and pass signed-current/KCL, probe, bias and raw-hash checks. Values come from the full-precision native logs; old diagnostic exports may differ slightly through rounding. All three meet the initial active RMSE <=0.05 decade / absolute endpoint error <5% engineering targets on the fixed measured-current masks. This is not a full measured-curve fit.

The measured low-current plateaus remain unresolved: native zero counts are 54/121, 54/121 and 46/121. Those points remain in linear residuals, with no invented positive floor in log residuals. Subthreshold and slope tradeoffs remain in MODEL_AND_RESULTS.md. Quantum charge sensitivity for 2 nm is a separate diagnostic, not a quantum transfer-curve certificate. The chosen direct-ATLAS model enables a continuous bulk acceptor tail and shallow donor background; Gaussian/interface families remain dormant. No calibrated ATHENA sputter-defect chemistry or unique oxygen-vacancy identification is claimed. The 31.8 nm branch is deferred under the user's priority; no new 31.8 nm run was launched in this extension.

## Completed continuation

Ten simulator starts were used in this extension: eight strict-native passes and two rejected attempts. The first 6.3 nm mobility trial lacked the required native completion banner. Its first retry was aborted during startup by an over-strict helper-tracking policy; no device solve was obtained. The corrected runner then completed the byte-identical second retry. Failed inputs and raw logs were preserved, not relabeled as accepted simulations.

6.3 nm controls: x `20260912T125515_583761_priority3_verify6_x`, y `20260912T130613_869036_priority3_verify6_y`, DOS `20260912T131716_348906_priority3_verify6_dos`. Maximum active changes are 0.000240965, 0.001522058 and 0.000845864 decade; endpoint changes are 0.0346441%, 0.2592756% and 0.1801543%. Certificate: results/priority_three_20260912/numerical_6.json.

13.2 nm controls: x `20260912T132642_597382_priority3_verify13_x`, y `20260912T134058_082088_priority3_verify13_y`. Maximum active changes are 0.000197563 and 0.001153035 decade; endpoint changes are 0.0218630% and 0.0110458%. Partial assessment: results/priority_three_20260912/numerical_13_partial.json. No DOS result exists for this selected donor density.

The final native run exited and its read-only process reconciliation at 13:54:45 UTC found no recorded/missed process, installed ATLAS instance, or helper referring to that run. Only project-local guards were archived/cleared. The two pre-existing unrelated DeckBuild GUIs were preserved. Lifecycle sidecars retain observed-helper uncertainty; reconciliation does not retroactively prove unseen process lineage.

## Artifacts and verification

The new delivery is deliveries/priority_three_delivery_20260912/. Complete sequential input: decks/combined/IWO_SELECTED_ALL.in. Individual inputs are under decks/individual/. Every saved structure and transfer log has a TonyPlot command: 15 calls across three devices. The assembled combined input itself was not rerun; its three physics blocks reproduce the exact executed native inputs.

The audit/ supplement contains hash-matched original native runs, numerical controls, retry/lifecycle records, original data/source hashes, code and scope documents. Original certificates remain unchanged. Fresh portable checks imported the checkers from this copied audit directory and recomputed the 2 nm certificate and 6/13 assessments: 2 nm PASS, 6.3 nm scoped PASS, 13.2 nm INCOMPLETE with DOS missing. Read audit/verification/20260912T135828_674097Z/VERIFICATION_SUMMARY.json. The verifier's exit code 1 means the explicitly missing check, not corrupted evidence or a simulator failure.

The original workbook, paper, screenshot and four measurement CSV hashes were rechecked: all seven unchanged. Full software suite: 182 tests passed before the later report-only prose change; the new portable-verifier guards passed eight standalone tests. The actual copied-evidence integration above is additional read-only validation. No licensed installation/manual contents are distributed. Native Windows DeckBuild 5.0.10.R / ATLAS 5.28.1.R was used with C:/sedatools/exe/deckbuild.exe -run device.in -outfile deckbuild.out.

Detailed final phase summary: docs/rebuild_20260912/PRIORITY_THREE_RUNS_CURRENT.md and results/priority_three_20260912/priority_three_runs_current.json. Complete global history: RUN_BY_RUN_SUMMARY.md (70 invocations / 75 reserved engine stages; older combined invocations explain the difference). Earlier deliveries and snapshots remain preserved.

## Limit and exact next command

The user approved another four hours, 12:06:11–16:06:11 UTC on 12 September 2026. The ten-start cap carried into this extension is now reached (65 prior reserved stages; 75 cumulative cap). The wall-clock window has not been exhausted. A pending user request asks for ONE additional start to complete 13.2 nm DOS resolution within that same deadline; no answer has arrived. Do not treat elapsed time or remaining wall time as approval, and do not reset the index.

After explicit approval, archive the current budget and raise its cumulative launch cap from 75 to 76, preserving the deadline and recording the exact approval. Then run this already prepared, isolated numerical control from the original project root:

```powershell
.\.venv\Scripts\python.exe scripts/rebuild_trial.py --config config/priority3_verify13_dos.json --key 13p2 --label priority3_verify13_dos --timeout 1500
```

Until that approval arrives, this command is not authorized. After completion, compare against the selected 13.2 nm reference, reconcile any lifecycle guard, and construct a fresh full scoped 13.2 nm certificate from its exact x/y/DOS runs. Publish a new delivery version rather than changing this immutable checkpoint. If the original deadline has passed, obtain a new bounded runtime allowance as well.
