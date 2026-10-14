# Framing-chapter audit (2026-10-14): disposition

Source: audit agent report on 00_abstract, 01_introduction, 03_device_data (skim), 09_mechanisms (skim), 11_validation,
12_conclusions, 14_model_v2; flagged lines spot-checked by the main session (03:27, 03:237-240, 03:272-274, 03:288,
09:86, 09:340, 11:34, 11:44, 11:85, 11:96, 11:118, 11:132, 14:16, 14:71, 14:84, 14:193, 14:266-274, 14:360).

| Chapter | Disposition |
|---|---|
| 00_abstract, 01_introduction | Replaced by M00_abstract, M01_introduction (stale launch counts 52/60, overclaims "reproduced exactly", "show that", strip "reproduces t^3.85"; missing C10, register, H-L, MACE, D-43, RQ-001, permission). No label of these files is referenced elsewhere. |
| 12_conclusions | Replaced by M15_conclusions. Overclaims: "Demonstrated" for C030/C031 and for the CB share; inversion "validated"; floor law and leakage rejection; "Publication-ready claims"; superseded 13.2 nm SS agreement (C010, D-06). M15 must define: ch:conclusions, sec:concl-demonstrated, sec:concl-supported, sec:concl-plausible, tab:concl-plausible, sec:concl-corrections, sec:concl-claims. |
| 03_device_data | Revised copy (patch_reused.py): stack order as assumption; C030/C031/C033 wording. |
| 09_mechanisms | Revised copy: "demonstrated (provenance)" -> numerical match / definition inferred. Remaining: slope 3.78 vs 3.85 (S4) left as in baseline. |
| 11_validation | Revised copy: revision note (historical status), run_0060 added, timestamps, >= 10 devices, QE done. Tier plan kept as historical. |
| 14_model_v2 | Revised copy: C004/C005 labels, untested cause of 2 nm RMSE miss, T4 deferred (D-07), sub-nm films pointer. |

Not audited (reused verbatim; check in Gate 6 review): 02a-02d literature, 04/05 derivations, 06 numerics,
07 calibration, 08 six nm, 10 predictions, appendices A-E.

Global note from the audit: the baseline's hypothesis names "C1..C10" (12_conclusions table) collide with ledger IDs
C001-C040 and with the "C10 campaign". The monograph refers to ledger claims as C0nn (three digits) and to the campaign
as "campaign C10".
