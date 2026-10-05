# Correction to the T0 pre-registration (written before the 6.3 nm T3 result existed)

Written 2026-10-05, about 18:20Z. At that time the V2 2 nm run (run_0058) had finished, the 13.2 nm run was in progress, and the 6.3 nm T3 run had not started.

The registered files are kept unchanged:
- `T0_PRECHECKS.md` and `T0_REGISTRATION.txt`;
- `t0_results_registered.json` (= the registered `t0_results.json`, same SHA-256 9b39c2e7…);
- `t0_prechecks_registered.py` (SHA-256 03e809a5…).

## What was wrong
The exact transformation (`transform()` in `t0_prechecks.py`) moves a calibrated ATLAS curve along Vg. It looked up the current at Vg − ΔV and **clipped** that value to the simulated range, −3 to +3 V. For a curve moved to the left (ΔV < 0), the points above 3 V + ΔV were therefore set to I(3 V).

| Film | Net shift | Effect |
|---|---|---|
| 2.0 nm | −0.0128 V | small |
| 6.3 nm | −0.256 V (tuned → shared Qf, then V2) | the last 0.26 V of the registered 6.3 nm prediction was flat |

Found by: run_0058 gave Id(3 V) +0.83 %, against 0.00 % in the registered prediction.

Not affected:
- curves moved to the right (13.2 nm);
- the subthreshold region, including Vth_cc at 1e-9 A/µm.

## Fix
Above the last simulated point, the current is now extrapolated linearly from the last three simulated points (`transform()`, comment "CORRECTION 2026-10-05"). This is reasonable because the on-state current is near-linear in Vg.

The registered Qf scan is not redone for the comparison. The runs use the registered V2 parameters (Qf 1.38345e12; μ_band 17.6897, 63.2597 and the T3 value 38.3893), so the corrected predictions below are computed at exactly those parameters (`t0_correction.py` → `t0_correction.json`).

## Corrected predictions at the as-run parameters (registered values in brackets)

| Case | Active RMSE (dec) | Vth_cc (V) | Vth_lin (V) | SS_cc (mV/dec) | Ion (A/µm) |
|---|---|---|---|---|---|
| 2.0 nm anchor | 0.0600 [0.0600] | 0.6681 [0.6681] | 1.5440 [1.5218] | 291.1 [291.1] | 5.134e-7 [5.090e-7] |
| 13.2 nm anchor | 0.0973 [0.0973] | 0.1034 [0.1034] | 1.0430 [1.0430] | 191.8 [191.8] | 3.071e-6 [3.071e-6] |
| 6.3 nm, variant P (μ_band 38.3893) | 1.038 [1.036] | 0.271 [0.271] | 1.218 [1.206] | 220.1 [220.1] | 1.559e-6 [1.337e-6] |
| 6.3 nm, variant E | 0.547 [0.594] | 0.417 [0.398] | 1.218 [1.206] | 300.1 [289.5] | 4.034e-7 (normalised) |

Variant E uses μ_band 9.935 [registered 11.58].

## Consequences
- **Pre-registered verdicts unchanged:** T3 still FAILS on Vth_cc in both variants, and on Ion, SS_cc and RMSE in P.
- **T2 comparison:** ATLAS is compared with both the registered and the corrected predictions; both are reported.
- **2 nm anchor mobility:** the ATLAS on-current is +0.83 % above the measurement. As in V1, the final V2 anchor mobility is the exact rescale μ_band × Ion_meas/Ion_ATLAS. This is a calibration step, not a test.
