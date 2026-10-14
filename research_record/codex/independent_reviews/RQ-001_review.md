# Review of RQ-001 / HO-002

| Field | Value |
|---|---|
| Reviewer | Codex |
| Commit reviewed | Private HEAD c10a976; newest RQ-001 handoff HO-002; public evidence f315b78 |
| Date | 2026-10-09 |

Phase 1 is preserved in `codex/independent_reviews/RQ-001_independent_assessment.md` (committed c10a976). Its disclosure that Part B was accidentally exposed before writing remains applicable: this is an independently implemented numerical review, not a strictly blinded assessment. Read the owner's README, both scripts, JSON and CSV evidence named in HO-002. Principal arithmetic was independently reproduced in phase 1; its listed unchecked quantities remain limitations. The owner script was not rerun because its dependencies are unavailable; no network installation was attempted. Phase 2 additionally checked all 31 scored variants (14 within 15%) and the trap-proxy arithmetic. Verdicts concern RQ-001, not older HO-001 or the wider programme.

## 2. Verdicts (after reading Part B)

### Claims

| Item | Verdict | Reason | Test that would change it |
|---|---|---|---|
| C030: saturation-formula peaks reproduce paper mobility values [DERIVED] | SUPPORTED | Independent central differences give 5.0865 / 3.8584 / 27.4029 cm²/Vs. Agreement is conditional on stated units and C_ox; no adjustable multiplier was used. It establishes numerical correspondence. | Reproduction with documented original units, capacitance or differentiation contradicts these values. |
| C031 / B1: paper used this formula on these same curves [INFERRED] | REVISE | A leading candidate, but “high probability” has no quantified basis. Peaks constrain the combined scale, not C_ox and geometry separately. Alternatives with common factors remain viable. | Apply the fab's original script/spreadsheet unchanged to the identified sweeps and reproduce the plotted values. |
| C024 / B1: discrepancy is a definition difference rather than different data [UNRESOLVED] | UNRESOLVED | Arithmetic reconciliation is strong; identical paper-device/sweep provenance and actual recipe are unconfirmed. | Fab confirms equation, scale and sweep identity; exact recipe reproduces all three values. |
| B1: falling saturation-formula mobility can arise from linear-regime algebra [DERIVED] | SUPPORTED | Constant-μ gradual-channel current gives μ_sat = μ V_D/(2V_ov − V_D), falling above V_ov = V_D. This is a conditional algebraic result. | An algebra or unit error in the stated current model. |
| B1: that effect explains paper Fig. 5d [INFERRED] | UNRESOLVED | Fig. 5d may display fitted μ_sr, which declines by construction; reproducing our curve shape does not identify that figure's source. | Fab supplies Fig. 5d data and plotting/extraction recipe. |
| C032: near-floor candidate estimators match paper SS within 5–15% [DERIVED] | SUPPORTED | Reproduced representative estimators; 31 variants were searched and 14 meet 15%. The best 5% is exploratory selection, not validation or a confidence bound. | Original units/data or independently checked scoring contradict the match; exact recipe identifies a different source. |
| B2: paper SS behaves like a near-floor steepest-slope quantity [INFERRED] | REVISE | Say “compatible with several near-floor estimators.” Fitted Eq. 1e SS, another sweep, and subtraction remain alternatives; the search cannot identify the method. | Obtain the original SS equation/window/floor handling and apply it unchanged. |
| B2: only 2 nm has 60–70 SS in Fig. 1b [DERIVED] | SUPPORTED | Visual inspection supports approximately 62 / 87 / 119 mV/dec. Scope this to the three IWO markers, not every device/figure. Exact centroid uncertainty was not independently regenerated. | Original plotted numerical data or an independent calibrated digitisation contradicts this ordering/range. |
| B2: near-floor 2 nm steep section is real because noise does not create it [UNRESOLVED] | REVISE | The section exists in recorded values [OBSERVED]. Monte Carlo uses the same smoothed curve as truth and independent log-Gaussian noise; it cannot exclude offsets, range transitions, settling or correlated errors. Its margin-10 estimators also do not validate every margin-1–3 estimator. | Preregister fine-grid repeated sweeps, grid phases, I_D/I_S/I_G, settling/range metadata and probe-lifted baseline; check persistence over a fixed current window. |
| C025: physical near-thermal 2 nm switching [UNRESOLVED] | UNRESOLVED | Narrow pA-level slopes and broad-window SS measure different curve regions. Neither noise simulation nor selected minimum establishes broad near-thermal switching or low trap density. | Original recipe/provenance plus the registered measurement controls above establish reproducibility and current origin. |
| B3: μ_FE,lin is the valid model-free mobility [DERIVED] | REVISE | Its arithmetic is directly defined, but physical interpretation assumes charge control and transport conditions. Report it as C_ox-normalised transconductance at V_D = 0.7 V, not intrinsic/band mobility. Contacts and gate-dependent charge/mobility remain relevant. | Independent C–V, low-V_D transfers and contact/output characterization show the required conditions. |
| B3 / C031 caveat: saturation formula is outside its validity range at 6.3 nm peak [INFERRED] | REVISE | Both owner threshold estimates give overdrive above 0.7 V, a strong conditional warning. Thresholds are model-dependent, not an independently measured saturation boundary; even saturation does not guarantee constant mobility. | Output curves at the peak gate bias establish regime, with independently constrained charge/threshold response. |
| B3: power-law μ_ch gives overdrive dependence [FITTED] | REVISE | It gives dependence within that fitted current model; it is not independently measured channel mobility. 13.2 nm evaluation at the 0.95 V peak is outside the 1–3 V fit interval. | Independent charge and transport data validate the fitted decomposition and extrapolation. |
| B3: SS must carry its window; near-floor and A1 values describe distinct regions [DERIVED] | SUPPORTED | Independent SS values reproduce the difference. Approximately 62 / 87 / 119 are paper markers, not the output of one confirmed common estimator on our curves. | Documented original window/data invalidates that attribution or region distinction. |
| B3: equivalent trap-density proxies differ by more than ×10 [DERIVED] | SUPPORTED | At assumed 300 K, 61.75 and 123.598 give 2.11e11 and 6.02e12 cm⁻²eV⁻¹, about ×28.5. This is conditional arithmetic. Actual trap-density attribution remains HYPOTHESIS because other capacitances, floor and transport effects are unresolved. | Independent capacitance/temperature or SS inputs alter the arithmetic; independent trap characterization is required to promote the physical interpretation. |
| C033: paper off-current markers numerically correspond to our floors [DERIVED] | SUPPORTED | Supplied digitisation gives ratios 0.71 / 0.93 / 1.02. Approximate positions were visually checked, exact pixel errors were not independently regenerated. At 2 nm the 29% difference exceeds the stated ~15% read uncertainty, so this is approximate correspondence. | Independent digitisation or original plot values contradict the ratios. |
| C033 implication: same curves/current normalisation [UNRESOLVED] | UNRESOLVED | Paper axis says A and our values are A/µm. Numerical correspondence and rounding statistics cannot resolve units or establish sweep identity. | Fab supplies original Fig. 1b dataset and width-normalisation/provenance records. |

### Proposals

| Item | Verdict | Reason | Test that would change it |
|---|---|---|---|
| Next action 1: independent review of algebra and SS selection | ACCEPT | Numerical review completed; preserve the phase-1 blinding disclosure. | A central decision requires strictly blinded review: use an unexposed reviewer. |
| Next action 2: Mahmoud asks six fab questions in README | ACCEPT | Cheapest direct discriminator; request existing recipe and provenance first. Include original script/spreadsheet and Figure 5d source, not only verbal formula names. No message sent by Codex. | Complete existing documentation answers the questions reproducibly. |
| Next action 3a: report each mobility and SS with definition/window | ACCEPT | Also state units, C_ox, V_D, derivative/grid, point count, floor handling and whether fitted. | A confirmed common protocol enables comparisons; definitions still accompany results. |
| B3: quote paper μ_max only as confirmed “saturation-formula peak” | MODIFY | Until confirmed, write “paper-reported μ_max; numerically reproduced by saturation-formula peaks.” Compare definitions explicitly if displayed together. | Fab verifies the original formula and dataset. |
| Next action 3b: keep C024/C025 UNRESOLVED, retain C030–C033 | MODIFY | Keep C024/C025 unresolved and C030/C032/C033 DERIVED; revise C031 language and provenance/uncertainty caveats as below. | Fab recipe and measurement controls justify a documented status change. |
| Next action 4: no ATLAS/CERN/network needed | ACCEPT | Existing arithmetic and fab documentation are sufficient for the next decision. | A clearly discriminating question emerges that existing evidence cannot address; humans authorize any costly work. |
| Adopt best-scoring near-floor method as a new reporting standard | REJECT | Not explicitly recommended by owner; reject this possible downstream use of the 31-way search. Matching published values is not a criterion for selecting an estimator. | A physically justified protocol is fixed before unseen repeat measurements and passes its controls. |

Overall recommendation: MODIFY. Accept the numerical reconciliation as a completed exploratory result; leave recipe attribution and physical validation open. First obtain the original fab recipe, then decide whether new registered metrology is necessary. Do not tune TCAD or promote intrinsic mobility/low-trap claims from these matches.

## 3. Proposed ledger changes

Status labels below are charter labels, distinct from the review verdicts above. These are proposals only; the ledger was not edited.

| Claim ID | Current status | Proposed status | Evidence |
|---|---|---|---|
| C024 | UNRESOLVED | UNRESOLVED (retain; revise caveat) | Add phase-1 reproduction and C030: numerical discrepancy can be reconciled by a definition candidate; original paper formula, scale and sweep provenance remain unverified. |
| C025 | UNRESOLVED | UNRESOLVED (retain; revise caveat) | Near-floor candidate slopes reproduce ~62 at 2 nm; A1 is 123.6. Noise Monte Carlo is conditional robustness, not proof against instrumental effects or evidence of low traps. |
| C030 | DERIVED | DERIVED (retain; add review evidence) | `codex/independent_reviews/RQ-001_check_results.json` independently reproduces central-difference peaks. Explicitly separate numerical correspondence from method attribution and intrinsic mobility. |
| C031 | INFERRED | INFERRED (retain; revise claim) | Replace “is” with “is a leading candidate for”; combined scale and same-sweep attribution remain unverified. Keep regime warning conditional on the two fitted/extrapolated threshold definitions. Confirmation requires the original fab recipe; no probability estimate is warranted. |
| C032 | DERIVED | DERIVED (retain; clarify scope) | Representative values independently reproduced; all 31 rows checked, 14 within 15%. Add selection caveat, corrected-current versus total-current floor-margin distinction, and no inference that the paper actually used a minimum slope. |
| C033 | DERIVED | DERIVED (retain; strengthen caveat) | Ratios from owner digitisation, approximate visual check only. Add unresolved A versus A/µm units, 29% discrepancy at 2 nm, and explicitly state that same-device/sweep provenance is not established. |

No other ledger status changes are warranted by RQ-001. No new physical claim is proposed: intrinsic mobility, instrumental origin of the steep section and trap-density interpretation remain unresolved. Any new mechanism proposed from them must be marked HYPOTHESIS.
