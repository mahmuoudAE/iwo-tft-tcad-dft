# Priority-three phase: all ten completed attempts

Final phase snapshot: **2026-09-12T13:56:55.081500+00:00**. The phase began at **12:06:11 UTC, 12 September 2026**. All ten starts have finished: **eight strict native passes and two rejected attempts**. No simulator remains active according to the completed phase/reconciliation records. These are global invocations 61-70 and cumulative reserved simulator stages 66-75; earlier multi-engine invocations explain the different counts. Failed starts count toward the ten-start allowance.

No approval for an additional simulator start was received. The 13.2 nm DOS-resolution control remains unexecuted, and its candidate-specific numerical certificate is explicitly incomplete. Native completion, lifecycle reconciliation, numerical resolution and fit quality remain separate.

| # / global | Run and purpose | Change | Actual outcome |
|---|---|---|---|
| 1 / 61 | [20260912T120614_604542_resume_6nm_y01_ymesh](audit/results/local_session_20260910/runs/20260912T120614_604542_resume_6nm_y01_ymesh/device.in)<br>6.3 nm prior-candidate vertical mesh check | Previous MUN=13 physical candidate; double IWO/Al2O3/HfO2 intervals 8/4/10 to 16/8/20. | Native PASS, all 121 targets; active log RMSE **0.06311004**; +3 V error **+10.168137%**. ymesh PASS: maximum active difference 0.00152200344 decade; endpoint difference 0.259256%. Elapsed 597.687 s. |
| 2 / 62 | [20260912T121627_947928_priority3_fit6_mu12](audit/results/local_session_20260910/runs/20260912T121627_947928_priority3_fit6_mu12/device.in)<br>6.3 nm isolated band-mobility trial | MUN 13 to 12 cm^2/(V s); preserve ND, bulk-tail capacity/width, gate and contacts. | **REJECTED:** launcher returned 0, but the native ATLAS completion banner is missing. No accepted fit score. Elapsed 428.907 s. |
| 3 / 63 | [20260912T122359_458630_priority3_fit13_nd89](audit/results/local_session_20260910/runs/20260912T122359_458630_priority3_fit13_nd89/device.in)<br>13.2 nm isolated donor-density trial | ND 8.6e17 to 8.9e17 cm^-3; preserve MUN=55, tail capacity/width, gate and contacts. | Native PASS, all 121 targets; active log RMSE **0.04902804**; +3 V error **+2.452298%**. Elapsed 542.563 s. |
| 4 / 64 | [20260912T124052_500555_priority3_fit6_mu12_retry](audit/results/local_session_20260910/runs/20260912T124052_500555_priority3_fit6_mu12_retry/device.in)<br>6.3 nm exact-input first retry | Same physics/input as run 2; first owned-process lifecycle hardening. | **FAILED STARTUP:** missing ephemeral-helper observation triggered an overly strict abort; owned cleanup reported WinError 5. No accepted fit score. Elapsed 5.969 s. |
| 5 / 65 | [20260912T124657_803129_priority3_fit6_mu12_retry2](audit/results/local_session_20260910/runs/20260912T124657_803129_priority3_fit6_mu12_retry2/device.in)<br>6.3 nm exact-input second retry | Same physics/input as runs 2 and 4; corrected bounded handling of short-lived-helper uncertainty. | Native PASS, all 121 targets; active log RMSE **0.04920549**; +3 V error **+1.966683%**. Elapsed 420.938 s. |
| 6 / 66 | [20260912T125515_583761_priority3_verify6_x](audit/results/local_session_20260910/runs/20260912T125515_583761_priority3_verify6_x/device.in)<br>Selected 6.3 nm lateral mesh check | MUN=12; x spacing 0.5 to 0.25 um and contact-edge spacing 0.05 to 0.025 um. | Native PASS, all 121 targets; active log RMSE **0.04917524**; +3 V error **+1.931357%**. xmesh PASS: maximum active difference 0.000240964648 decade; endpoint difference 0.034644%. Elapsed 601.656 s. |
| 7 / 67 | [20260912T130613_869036_priority3_verify6_y](audit/results/local_session_20260910/runs/20260912T130613_869036_priority3_verify6_y/device.in)<br>Selected 6.3 nm vertical mesh check | MUN=12; double IWO/Al2O3/HfO2 intervals 8/4/10 to 16/8/20. | Native PASS, all 121 targets; active log RMSE **0.04891051**; +3 V error **+1.702308%**. ymesh PASS: maximum active difference 0.00152205812 decade; endpoint difference 0.259276%. Elapsed 633.812 s. |
| 8 / 68 | [20260912T131716_348906_priority3_verify6_dos](audit/results/local_session_20260910/runs/20260912T131716_348906_priority3_verify6_dos/device.in)<br>Selected 6.3 nm DOS resolution check | MUN=12; bulk NUMA/NUMD 192/96 to 384/192. Donor amplitude remains zero. | Native PASS, all 121 targets; active log RMSE **0.04971074**; +3 V error **+2.150380%**. dos PASS: maximum active difference 0.000845863932 decade; endpoint difference 0.180154%. Elapsed 516.313 s. |
| 9 / 69 | [20260912T132642_597382_priority3_verify13_x](audit/results/local_session_20260910/runs/20260912T132642_597382_priority3_verify13_x/device.in)<br>Selected 13.2 nm lateral mesh check | ND=8.9e17; x spacing 0.5 to 0.25 um and contact-edge spacing 0.05 to 0.025 um. | Native PASS, all 121 targets; active log RMSE **0.04897436**; +3 V error **+2.429899%**. xmesh PASS: maximum active difference 0.000197562593 decade; endpoint difference 0.021863%. Elapsed 828.000 s. |
| 10 / 70 | [20260912T134058_082088_priority3_verify13_y](audit/results/local_session_20260910/runs/20260912T134058_082088_priority3_verify13_y/device.in)<br>Selected 13.2 nm vertical mesh check | ND=8.9e17; double IWO/Al2O3/HfO2 intervals 8/4/10 to 16/8/20. | Native PASS, all 121 targets; active log RMSE **0.04914416**; +3 V error **+2.463615%**. ymesh PASS: maximum active difference 0.00115303506 decade; endpoint difference 0.011046%. Elapsed 817.375 s. |

## Numerical scope at the end of this allowance

The selected 6.3 nm MUN=12 run passes its own lateral-mesh, vertical-mesh and DOS comparisons. Its certificate is **PASS_SCOPED_EXTENSION_NUMERICS**: device-specific x/y/DOS plus the actual reverified 2 nm width-unit convention. No per-device 6.3 nm width test was performed. This is numerical evidence for the exact candidate, not a prediction certificate or a complete off-current fit.

The selected 13.2 nm ND=8.9e17 cm^-3 run passes its own x and y comparisons. X changes active current by at most **0.000197562593 decade** and endpoint current by **0.02186296%**; y changes them by **0.001153035064 decade** and **0.01104577%**. Its DOS control has not been launched. `numerical_13_partial.json` is **INCOMPLETE**, with `validated_scope=NONE`; x/y passes are not a complete numerical certificate.

The 2 nm selected model retains its full width/x/y/DOS certificate from the preceding phase. Start 1 tested the previous **MUN=13** 6.3 nm physical model; it does not certify the later MUN=12 candidate. Starts 6-8 provide the candidate-specific evidence for MUN=12.

## Residuals retain the unfitted low-current samples

| Phase # | Active log RMSE (decade) | +3 V error (%) | All-point signed linear RMSE (A/um) | All positive-log RMSE (decade) | Positive-log denominator | Native zero count |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 0.06311004 | +10.168137 | 1.90544482e-08 | 1.80506129 | 67/121 | 54 |
| 3 | 0.04902804 | +2.452298 | 4.70914158e-08 | 2.40220925 | 75/121 | 46 |
| 5 | 0.04920549 | +1.966683 | 9.95395622e-09 | 1.81347681 | 67/121 | 54 |
| 6 | 0.04917524 | +1.931357 | 9.90935433e-09 | 1.81899916 | 67/121 | 54 |
| 7 | 0.04891051 | +1.702308 | 9.61870759e-09 | 1.81346038 | 67/121 | 54 |
| 8 | 0.04971074 | +2.150380 | 1.01538227e-08 | 1.81348833 | 67/121 | 54 |
| 9 | 0.04897436 | +2.429899 | 4.6806576e-08 | 2.40805539 | 75/121 | 46 |
| 10 | 0.04914416 | +2.463615 | 4.72768249e-08 | 2.40253737 | 75/121 | 46 |

The working fit targets are active log RMSE <=0.05 decade and absolute +3 V current error <5%. The active mask remains measured I >5 times the measured median over -2<=Vg<=-0.5 V; the original mask is not reoptimized. The selected 6.3 and 13.2 nm candidates meet those active targets. All 121 signed samples remain in linear metrics. Logarithms are undefined at native zero/negative current; missing logarithms and their denominators are exposed rather than repaired with a leakage floor. The JSON companion includes active, subthreshold, on, low-current and all-point metrics for every accepted run.

## Why the identical 6.3 nm inputs were retried

Starts 2, 4 and 5 have identical actual input bytes and saved configurations. Recomputed device.in SHA256 is `af274661c5dc74d3ec57000997ab821e466fdca2872b6912e423679336b2c3a1`; input_config.json SHA256 is `7411cf29426cd8048dd88586359c8f6b7f22ae995cf521ca7a2ec13d71cf73d4`. Start 2 lacks the mandatory native completion banner, so saved endpoints alone were rejected. Start 4 failed because the first lifecycle safeguard reacted too aggressively to a short-lived helper. The corrected runner keeps bounded monitoring and the one-engine guard through native completion, records helper uncertainty, and requires a separate no-overlap reconciliation before another launch. It does not manufacture a native completion marker or relax scientific gates. Start 5 supplies the completed verified result.

The later selected6 and numerical-control execution records retain `PROCESS_EXITED_LIFECYCLE_REVIEW_REQUIRED` where applicable. Root subsequently recorded read-only no-overlap reconciliation for starts 5-10; start 4 has a separate recovery record. This is not complete retrospective identification of every missed helper. Original raw statuses remain unchanged.

## Evidence

- [Final current-phase JSON](audit/results/priority_three_20260912/priority_three_runs_current.json) pins the final read index, completed execution/input hashes, metrics, recomputed comparisons and reconciliation references.
- [6.3 nm scoped numerical certificate](audit/results/priority_three_20260912/numerical_6.json) identifies the exact MUN=12 reference and its controls.
- [13.2 nm incomplete numerical report](audit/results/priority_three_20260912/numerical_13_partial.json) preserves the missing DOS check.
- [6.3 nm retry input identity](audit/results/priority_three_20260912/fit6_retry_input_identity.json) preserves the exact-input comparison.
- [Runner lifecycle diagnosis](audit/docs/rebuild_20260912/RUNNER_LIFECYCLE_HARDENING.md) records the startup failure, correction and safeguards.
- [Global run history](audit/results/rebuild_20260912/run_history_20260912T135521_917970/RUN_BY_RUN_SUMMARY.md) was regenerated after all ten attempts finished: 70 invocations and 75 reserved engine stages.

This is the single authorized finalization of the current phase report. The earlier frozen snapshot, evidence plan and packet staging were preserved. No simulator, budget modification, HANDOFF edit or raw-evidence copy/edit was performed by this reporting task.
