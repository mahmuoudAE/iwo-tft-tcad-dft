# Independent active-fit checkpoint review

Result: PASS for the explicitly labeled active-fit checkpoint; this is not final numerical certification of all three films.

Reviewed `deliveries/priority_three_active_fit_checkpoint_20260912` and `scripts/rebuild_priority_delivery.py` without launching a simulator, altering copied evidence, or changing the helper.

## Independent checks

- All 149 priority-manifest, 84 nested delivery-manifest, and 152 checkpoint-verification artifact hashes match.
- Each selected source passes the current strict native loader, including its original 121 gate targets and signed terminal-current checks. All copied raw artifacts match their source hashes: 24 files for 2 nm, 26 each for 6.3 and 13.2 nm.
- Copied configurations and measured CSVs match their evaluated sources exactly. The copied renderer resolves its own delivery root and reproduces all original simulation commands; the saved batch reproductions agree.
- Individual delivery commands differ only in the explicitly checked output filenames and added TonyPlot calls. The combined deck reconstructs exactly from the three verified blocks, has unique output names, and includes 15 TonyPlot calls covering all 12 saved structures and three transfer logs. No execution of the combined deck or TonyPlot GUI is claimed.
- The exact 2 nm certificate was independently reloaded and recomputed against its original width, lateral-mesh, vertical-mesh and DOS controls. The other two certificate scopes are correctly absent.
- All 11 `test_rebuild_priority_delivery` software tests pass.
- The original workbook, screenshot and main paper match their original `HANDOFF_MANIFEST.json` SHA-256 entries.
- Visual inspection of the logarithmic overview confirms the three selected native curves, explicit native zero counts, visible disagreement with measured off-current plateaus, and an empty deferred 31.8 nm panel.

| Film | Exact selected native run | Active log RMSE (decade) | +3 V current error | Native zero targets |
|---|---|---:|---:|---:|
| 2 nm | 20260912T074527_865393_fit_bulk_width04_2nm | 0.03339362339 | +0.6903669% | 54 |
| 6.3 nm | 20260912T124657_803129_priority3_fit6_mu12_retry2 | 0.04920549218 | +1.9666826% | 54 |
| 13.2 nm | 20260912T122359_458630_priority3_fit13_nd89 | 0.04902803895 | +2.4522984% | 46 |

## Scope and final-packet traceability

The assessment correctly distinguishes active-region agreement from complete low-current agreement, numerical convergence, unique defect chemistry, quantum transport and sputter-process prediction. It preserves native zeros and all measured points instead of adding a fitted leakage floor. The shared native bulk-tail model and thickness-specific parameter selections are inputs to an empirical calibration, not a unique microscopic identification. The combined input remains an assembled, unexecuted delivery artifact.

One traceability gap should be closed in the separate final packet: the copied 6.3 nm execution record retains `PROCESS_EXITED_LIFECYCLE_REVIEW_REQUIRED`, but the checkpoint does not copy or reference `results/priority_three_20260912/lifecycle_review_fit6/reconciliation.json`. That existing report records the subsequent current-process inspection and no-overlap reconciliation. Include it and its hash, preserving the original execution record. This is current no-overlap evidence; it does not retrospectively identify every missed historical helper.

The selected numerical control raw runs remain in their original project directories, as the checkpoint explicitly states. The 6.3 and 13.2 nm numerical certificates must be supplied only after their exact candidate-specific controls pass in the separate final delivery.

