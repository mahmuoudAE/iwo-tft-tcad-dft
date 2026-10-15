# A57 / D-80 result: measured-data extraction Monte Carlo (run 2026-10-15T21:56:50Z-22:11:55Z)

Run once with the frozen code `../mc_measured_extraction.py` (sha256 8c9c4aff…, pins and mirror check passed inside the run; inputs
unchanged before and after), IWO_MODEL_FILE = config/iwo_material_model_v3.yaml, project venv interpreter; 0 ATLAS launches.
MEASURED input: `IWO_PHYSICS_CONSTRAINED_MODEL_V1/data/experimental_clean.csv` (sha256 e27a53e8…), films 2.0 / 6.3 / 13.2 nm.
Output `mc_measured_extraction_out.json` (file sha256 2c354272…; LF text ef8edd0c…, see RUN_LOG_A57.txt). Figure
`fig_A57_measured_extraction_mc.pdf/.png`. No Codex review (D-63).

**Status.** The curves are MEASURED and were already seen (they calibrate every campaign stage). This is the uncertainty of the
EXTRACTION under an ASSUMED noise model (SG 7/3 residual block resampling + gain N(0, 0.1 %) + offset N(0, 0.1 × floor); the fab has not
supplied the SMU specification). It is not a blind test and not a prediction interval. Values are the registered extraction
(CALCULATED from MEASURED data); intervals are 2.5-97.5 % of N = 2000 replicates per film (power-law quantities on the first 400).
Failed replicates: 0 of 6000.

**Floor definition used.** Off-current floor = median I_D over V_G −2 … −0.5 V of the transfer curve (run_extraction.floor_with_sigma),
the same definition as the A56 floors. It is not the minimum measured current.

## Registered value [replicate 95 % interval] per film

| quantity (unit) | 2.0 nm | 6.3 nm | 13.2 nm |
|---|---|---|---|
| μ_FE at V_G 1.0 V (cm² V⁻¹ s⁻¹) | 1.57 [0.93, 1.60] | 1.29 [0.62, 1.50] | 28.7 [21.7, 30.1] |
| μ_FE at V_G 2.0 V (cm² V⁻¹ s⁻¹) | 8.77 [8.57, 9.05] | 6.17 [5.92, 6.46] | 45.0 [43.8, 46.8] |
| μ_FE at V_G 3.0 V (cm² V⁻¹ s⁻¹) | 12.15 [10.52, 13.51] | 10.74 [8.78, 11.99] | 49.1 [43.0, 54.3] |
| μ_ch at 3.0 V, power law (cm² V⁻¹ s⁻¹) | 8.763 [8.746, 8.782] | 6.438 [6.425, 6.452] | 42.82 [42.74, 42.92] |
| SS, fixed window 5e-11…5e-10 A/µm (mV dec⁻¹) | 165.6 [153.4, 174.8] | 177.6 [151.5, 185.9] | 106.1 [103.5, 108.5] |
| SS, A1 window (mV dec⁻¹) | 123.6 [109.0, 130.6] | 122.7 [115.6, 134.9] | 115.3 [110.4, 116.6] |
| V_th, constant current 1e-9 A/µm (V) | 0.662 [0.641, 0.663] | 0.644 [0.627, 0.652] | 0.0825 [0.0793, 0.0833] |
| V_th, constant current 5e-10 A/µm (V) | 0.591 [0.579, 0.592] | 0.569 [0.544, 0.575] | 0.0414 [0.0387, 0.0425] |
| V_th, ELR (V) | 1.313 [1.310, 1.446] | 1.470 [1.456, 1.576] | 0.694 [0.690, 0.841] |
| V_T, power law (V) | 0.4658 [0.4653, 0.4666] | 0.3194 [0.3184, 0.3212] | 0.25781 [0.25785, 0.26027] |
| off-current floor (A/µm) | 4.61e-15 [3.48e-15, 5.33e-15] | 1.53e-13 [1.13e-13, 1.75e-13] | 6.60e-12 [5.34e-12, 7.88e-12] |

## Reading

- The fixed-window SS interval half-widths (10.7 / 17.2 / 2.5 mV dec⁻¹) are much larger than the registered σ (0.6 / 2.0 / 2.0
  mV dec⁻¹, a fit error only) at 2.0 and 6.3 nm and comparable at 13.2 nm. The 6.3 nm SS interval [151.5, 185.9] is the widest.
- The power-law intervals (V_T widths 0.001-0.003 V) are far narrower than the registered σ (0.17 / 0.04 / 0.09 V). That σ includes the
  alternative fit windows, which A57 leaves out by design (A57 (c)). The window choice, not the noise, dominates the power-law uncertainty.
- The 13.2 nm power-law V_T (0.25781 V) lies just below its replicate interval (by 4e-5 V). The 2.0 nm V_th(5e-10), and the 13.2 nm μ0
  and γ, sit at an interval edge. Several intervals are one-sided around the registered value: ELR upward (up to +0.15 V),
  μ_FE(1.0 V) and the constant-current V_th mainly downward. The cause has not been examined.
- The floor interval runs from 19-26 % below to 15-19 % above the registered value. The replicate medians are 4-6 % below it at 2.0
  and 6.3 nm and 0.3 % below at 13.2 nm.
