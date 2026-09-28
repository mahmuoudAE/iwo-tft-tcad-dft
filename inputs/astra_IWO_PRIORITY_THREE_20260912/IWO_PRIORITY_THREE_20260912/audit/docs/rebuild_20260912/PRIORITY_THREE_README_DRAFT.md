# IWO model for 2, 6.3 and 13.2 nm channels — companion README draft

This note describes the exact completed native ATLAS runs below. It is prepared for a later delivery; **it does not grant numerical PASS to the 6.3 or 13.2 nm candidates**. Before publication, the final manifest must identify each selected run and its matching, reverified certificate. A change of physical candidate requires updated metrics and controls. The 31.8 nm branch is deferred.

| Film | Exact native source run | Delivery config / generator key |
|---|---|---|
| 2 nm | `20260912T074527_865393_fit_bulk_width04_2nm` | `config/iwo_2p0nm.json` / `2p0` |
| 6.3 nm | `20260912T124657_803129_priority3_fit6_mu12_retry2` | `config/iwo_6p3nm.json` / `6p3` |
| 13.2 nm | `20260912T122359_458630_priority3_fit13_nd89` | `config/iwo_13p2nm.json` / `13p2` |

Each configuration retains other thickness entries for provenance; use **its listed key**. Those other entries are not the selected parameter sets for the other devices.

## Structure and electrical model

The target stack is n⁺Si support / TiN 50 nm / HfO₂ 15 nm / Al₂O₃ 2 nm / IWO / Pd source and drain 70 nm. A continuous ideal TiN gate screens the support, so the electrical domain ends at the gate and excludes substrate carrier transport. Air fills the exposed channel space; no SiO₂ overlayer is added. Metals use conductor regions and explicit electrical contact boundaries.

| Shared input | Value |
|---|---|
| Channel length / physical width | 20 / 290 µm |
| Source and drain overlap length | 2 µm each; an unmeasured assumption |
| Simulated width | 1 µm |
| Transfer sweep | 121 original gate targets, −3 to +3 V in 0.05 V steps |
| Drain bias / temperature | 0.7 V / 300 K |
| Relative permittivity: IWO / HfO₂ / Al₂O₃ | 9.3 / 19.57 / 9.0 |
| IWO bandgap / electron affinity | 3.05 / 4.30 eV |
| Effective gate work function | 4.765 eV |
| Source/drain electrical boundary | Work function 4.45 eV with surface recombination; effective electron barrier 0.15 eV |
| IWO Nc / Nv | 5e18 / 1e19 cm⁻³ at 300 K |
| Background electron/hole lifetimes | 1e-6 s / 1e-6 s |
| Specified trap capture cross sections | 1e-15 cm² |

ATLAS solves classical Poisson/drift-diffusion with Fermi statistics, background SRH and the electron continuity equation. Band mobility is constant within each film; native free-carrier/trap occupancy and electrostatics determine the current. `METHOD TRAP` controls failed bias-step cutback; it does not create physical traps. These inputs do not enable quantum transport, dielectric conduction, added leakage, stress/illumination defect generation, contact tunneling or series resistance.

The material/contact inputs include effective fitted values and explicit priors. They are not a uniquely measured IWO database. In particular, the custom-material contact emission defaults remain 110/30 A cm⁻² K⁻² for electron/hole Richardson constants, without an explicit override. Earlier ATHENA work represented deposition geometry; it did not predict oxygen incorporation, sputter chemistry or defect populations. The selected decks construct their electrical mesh directly in ATLAS.

## Film parameters and trap families

The enabled bulk acceptor tail is `gTA(E) = NTA × exp[(E−Ec)/WTA]` within the bandgap. Its capacity is `NTA × WTA × [1−exp(−Eg/WTA)]`; multiply by thickness in cm for the sheet-equivalent capacity. Capacity is not occupied charge: native occupancy is solved separately. No extra analytical trapping factor is multiplied into the current.

| Film | Uniform ND (cm⁻³) | Band mobility (cm²/V s) | NTA (cm⁻³ eV⁻¹) | WTA (eV) | Tail capacity (cm⁻²) |
|---|---:|---:|---:|---:|---:|
| 2 nm | 2e17 | 13.3 | 5.5e20 | 0.040 | 4.4e12 |
| 6.3 nm | 1e17 | 12.0 | 3.7142857142857145e20 | 0.040 | 9.36e12 |
| 13.2 nm | 8.9e17 | 55.0 | 7.142857142857143e19 | 0.035 | 3.3e12 |

| Family | State in these selected inputs |
|---|---|
| Bulk acceptor exponential tail | **Enabled**, with the NTA/WTA above |
| Uniform shallow donor background | **Enabled**, with ND above; not an identified oxygen-vacancy Gaussian |
| Bulk donor tail | Zero amplitude (`NTD=0`) |
| Bulk acceptor and donor Gaussians | Zero amplitudes (`NGA=NGD=0`); stored centers/widths create no populated family |
| Interface traps, including Gaussian fields | Disabled: `defects.interface=false`; no `INTDEFECTS` command |
| Tokyo/PRPMOB transport fields | Dormant; the selected transport mode is constant mobility |

Dormant JSON fields are retained for provenance, including the old 2 nm interface peak. They are not active traps. The fitted tail represents effective localized-state behavior; the transfer data do not uniquely identify its chemical species or justify adding every available defect model.

## Actual comparison with the measurements

The initial working target is **active log RMSE ≤0.05 decades and absolute +3 V current error <5%**, with positive native current at every active target. For each film, the fixed active mask is measured `ID > 5 × median(measured ID for −2 ≤ VG ≤ −0.5 V)`. It is an analyst scoring convention, not an instrument detection limit. The subthreshold scoring region is the active subset with measured `ID ≤0.01 × measured ID(+3 V)`; “on” is the remaining active subset. No optimization-dependent remasking is used.

Linear residuals are signed native `ID/width − measured ID`. Log residuals are `log10(native ID/width) − log10(measured ID)` only where the signed native current is positive. All original points remain in the CSV and linear errors. A missing logarithm is not replaced with a leakage floor.

| Film | Region | Linear RMSE, A/µm (N) | Positive log RMSE, decades (positive N / region N) |
|---|---|---:|---:|
| 2 nm | Active | 6.70618977e-9 (57) | **0.03339362 (57/57)** |
| 2 nm | Subthreshold | 5.39529710e-11 (14) | 0.06032087 (14/14) |
| 2 nm | On | 7.72103617e-9 (43) | 0.01713296 (43/43) |
| 2 nm | All | 4.60278386e-9 (121) | 1.53029679 (67/121) |
| 6.3 nm | Active | 1.46316869e-8 (56) | **0.04920549 (56/56)** |
| 6.3 nm | Subthreshold | 2.09549880e-10 (12) | 0.05508456 (12/12) |
| 6.3 nm | On | 1.65064062e-8 (44) | 0.04747593 (44/44) |
| 6.3 nm | All | 9.95395622e-9 (121) | 1.81347681 (67/121) |
| 13.2 nm | Active | 6.57867733e-8 (62) | **0.04902804 (62/62)** |
| 13.2 nm | Subthreshold | 2.17932361e-9 (10) | 0.10185866 (10/10) |
| 13.2 nm | On | 7.18280903e-8 (52) | 0.02950898 (52/52) |
| 13.2 nm | All | 4.70914158e-8 (121) | 2.40220925 (75/121) |

The +3 V current errors are **+0.69037%, +1.96668%, and +2.45230%** for 2, 6.3 and 13.2 nm respectively. All three meet the stated active/current targets. They retain **54, 54 and 46 native zeros**, with no negative native drain samples; thus their all-region log values above are incomplete positive-only metrics. The measured low-current plateaus are not reproduced. These are not mean percentage-accuracy claims.

Reducing 6.3 nm mobility from 13 to 12 improved the active and endpoint errors but worsened the late 2.5→3 V slope error from −4.98% to −12.28%; its middle 1.5→2 V slope error remains +23.01%. Raising 13.2 nm ND improved early turn-on and the active aggregate but slightly worsened its on-region and all-point linear RMSE; its late slope error is −2.59%. These tradeoffs remain visible even when the initial active target is met.

**Numerical status:** read the final delivery's `PRIORITY_MANIFEST.json` and each `numerical/<key>/reverified_certificate.json`, including the exact reference run ID and validation scope. The known 2 nm reference has a reverified width/x/y/DOS certificate. This draft makes no final PASS claim for the 6.3 or 13.2 nm controls. Individual native completion and a good active score cannot replace those certificates or establish full-curve, quantum, process-chemistry or predictive validity.

## Using the inputs and reproducing them

In the delivery layout, open `decks/combined/IWO_SELECTED_ALL.in` in DeckBuild for the three devices sequentially, or choose `decks/individual/iwo_2p0nm.in`, `iwo_6p3nm.in` or `iwo_13p2nm.in` for one film. The combined file contains three verified source blocks with distinct output names; its assembled form has not itself been executed by the delivery helper. Every geometry/equilibrium/off/final `.str` and transfer `.log` has a TonyPlot command: five per device, fifteen in the combined input.

Use a fresh working directory with a legitimately licensed installation and an available execution allowance; do not write future outputs over copied evidence. Native current divided by simulated width in µm gives A/µm. At width 1 µm the numeric values coincide. Multiply normalized current by 290 µm for physical total current; do not divide it again by the physical width.

The copied renderer and exact configurations reproduce the evaluated batch commands. With Python and the supplied NumPy requirement, run from the delivery root, for example:

```powershell
python scripts/rebuild_model.py --config config/iwo_6p3nm.json --key 6p3 --out reproduced/iwo_6p3nm_batch.in --batch
```

Use the matching configuration/key from the first table for the other films. `--batch` suppresses interactive TonyPlot calls in this reproduced input. The generator reads the original gate-voltage targets; measured currents never create its device response. Generation is not simulator execution. LF versus Windows CRLF can change input byte hashes without changing commands; native provenance always uses the exact runfile bytes recorded in `execution.json`.

Fresh linear/log overlays and residuals belong under `reports/` and `overview/`; native evidence copies belong under `decks/evidence/`. The empty 31.8 nm overview panel must remain labeled as unselected/deferred. The final manifest and evidence hashes, rather than historical “uncalibrated” titles or dormant JSON fields, identify what was actually run and what was verified.

Draft metrics were read from the exact strict-native reports: the 2 nm report in the active-fit checkpoint, `results/priority_three_20260912/report_fit6_mu12`, and `report_fit13_nd89`. The full current comparison and slope tradeoffs are preserved in `actual_calibration_tradeoffs.json`. No simulator or existing delivery was modified to prepare this note.
