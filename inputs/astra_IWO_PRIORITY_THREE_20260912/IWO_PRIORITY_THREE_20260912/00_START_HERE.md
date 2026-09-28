# Start here — IWO priority-three delivery

This package contains actual native ATLAS results for the selected 2, 6.3 and 13.2 nm devices, their reproducible code, and original measurement comparisons. The 31.8 nm model is deferred.

- **Complete input:** [IWO_SELECTED_ALL.in](decks/combined/IWO_SELECTED_ALL.in), with separate device inputs under decks/individual/. All four structures and the transfer log per device have TonyPlot commands.
- **Results and physics:** [MODEL_AND_RESULTS.md](MODEL_AND_RESULTS.md). Active log RMSE is 0.033394, 0.049205 and 0.049028 decade; +3 V current error is +0.690%, +1.967% and +2.452% respectively.
- **Numerical status:** 2 nm width/x/y/DOS PASS. 6.3 nm x/y/DOS PASS with the width-unit convention transferred from 2 nm. 13.2 nm x/y PASS; its DOS check is missing, so its overall numerical status remains INCOMPLETE.
- **Each run:** [RUNS_THIS_EXTENSION.md](RUNS_THIS_EXTENSION.md) covers all ten starts: eight native passes and two rejected attempts. [RUN_BY_RUN_SUMMARY.md](RUN_BY_RUN_SUMMARY.md) covers the complete history.
- **Continuation:** [HANDOFF_STATUS.md](HANDOFF_STATUS.md) records exact selected IDs, remaining work and the prepared next command. The ten-start cap was reached; the four-hour wall-clock window was not exhausted. One additional 13.2 nm DOS start awaits approval.

The measured off-current plateaus are not reproduced. Native zeros remain visible in the accounting and are not replaced by artificial logarithmic floors. These are active-region fits, not a 100% realistic model, unique defect identification, calibrated sputter process, quantum transfer curve or predictive validation.

The outer PRIORITY_MANIFEST.json and nested decks/DELIVERY_MANIFEST.json are unchanged helper manifests. The outer manifest includes certificates only for 2 and 6.3 nm. Its NOT_SUPPLIED entry for 13.2 nm grants no numerical pass. Additional original controls and the explicit partial assessment are in audit/; no missing control was fabricated.

The audit folder preserves original project-relative evidence, historical certificate bytes, source/runner snapshots and lifecycle sidecars. Its STAGING_MANIFEST.json and COPY_STAGE_1.json document earlier copying stages; PACKET_MANIFEST.json at this package root describes the final contents. Old absolute paths in historical records remain provenance, not instructions to follow those paths after relocation.

Fresh checks using the COPIED audit scripts and raw files produced [VERIFICATION_SUMMARY.json](audit/verification/20260912T135828_674097Z/VERIFICATION_SUMMARY.json): 2 nm PASS, 6.3 nm scoped PASS, 13.2 nm INCOMPLETE because DOS is missing. This integration invoked no simulator. From this delivery root, recheck after copying or moving the package with Python and NumPy:

```powershell
python -B audit/verify_copied_evidence.py
```

A new verification directory is created each time. Exit 1 denotes the explicitly incomplete 13.2 nm control set; exit 2 denotes a rejected input or failure. Original certificates and raw files are never rewritten. See audit/VERIFY_COPIED_EVIDENCE.md for details.

The combined DeckBuild input was assembled from individually executed, command-matched native blocks. Its combined form has not itself been run. Future simulation outputs should be written in a new working directory, with a legitimate installation and an available user-approved allowance. Native current divided by simulated width gives A/um; multiply normalized current by 290 um for total device current.

The original workbook, paper, screenshot and all four CSVs remain unchanged. All 182 existing software tests passed before a later report-only wording change; the new verifier passed eight additional standalone guard tests. Native completion, numerical refinement, measurement agreement and predictive validity are separate claims. No installation executable, licensed manual, license configuration, or secret was bundled.
