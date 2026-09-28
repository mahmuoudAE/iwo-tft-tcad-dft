# Priority-three IWO assessment

These are selected completed native ATLAS runs for 2, 6.3 and 13.2 nm. The 31.8 nm branch is deferred and excluded from this delivery. The overview retains its explicitly empty 31.8 nm panel.

Active targets are fixed at RMSE ≤0.05 decade and absolute +3 V current error <5%, with complete positive native current on the original active mask. Numerical scope and full-curve/predictive validity are separate.

| Film | Active log RMSE (points) | +3 V error | All-point linear RMSE (A/µm) | Positive logs / targets | Zero / negative | Active targets | Numerical scope |
|---|---:|---:|---:|---:|---:|---|---|
| 2 nm | 0.0333936 (57/57) | +0.69037% | 4.60278e-09 | 67/121 | 54 / 0 | MET | DEVICE_WIDTH_X_Y_DOS |
| 6.3 nm | 0.0492055 (56/56) | +1.9667% | 9.95396e-09 | 67/121 | 54 / 0 | MET | DEVICE_X_Y_DOS_WITH_TRANSFERRED_WIDTH_UNIT_CONVENTION |
| 13.2 nm | 0.049028 (62/62) | +2.4523% | 4.70914e-08 | 75/121 | 46 / 0 | MET | NOT_VERIFIED_BY_THIS_DELIVERY |

Selected native run IDs:

- 2 nm: `20260912T074527_865393_fit_bulk_width04_2nm`.
- 6.3 nm: `20260912T124657_803129_priority3_fit6_mu12_retry2`.
- 13.2 nm: `20260912T122359_458630_priority3_fit13_nd89`.

Every original measured point and signed native current is retained. Zero/negative currents have no log residual: they remain counted and remain in linear errors, with gaps in log plots. No artificial leakage floor is added. The active mask is an analyst convention, not an instrument detection limit.

Each supplied numerical certificate was reloaded against the exact selected reference, its pinned evidence and native controls. A prior physical candidate’s certificate is rejected. NOT_SUPPLIED confers no numerical pass. A transferred width-unit convention is named explicitly and is not a repeated width test.

Active target agreement does not establish the complete measured low-current curve, unique defect species, contact coefficients, quantum transport, calibrated sputter chemistry or prediction outside these measured conditions. Full-curve fit and predictive validity are not granted by this package.

Selected-run raw evidence is copied under decks/evidence. Numerical certificate JSONs and their recomputed results are copied under numerical; raw numerical control runs remain in their original project directories and are identified by the recorded paths and hashes. The combined deck was assembled from verified blocks but was not itself executed by the delivery helper.
