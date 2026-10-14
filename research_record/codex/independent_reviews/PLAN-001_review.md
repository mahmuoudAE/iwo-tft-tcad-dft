# Review of PLAN-001 / HO-003

| Field | Value |
|---|---|
| Reviewer | Codex |
| Commit reviewed | Private HEAD 59f8df06e45b8f01d646e54155762679d53d256d; owner plan identified by HO-003 as f607cb5; public evidence f315b78 |
| Date | 2026-10-10 |
| Inputs | HO-003 Part B; COMPLETE_PLAN_2026-10.md; CERN_DFT_timeline_2026-10.pdf; charter, current state, research questions, ledger and queue |
| Phase 1 | PLAN-001_independent_assessment.md, committed at 59f8df0; unchanged. Its disclosed accidental Part B exposure prevents a strict blindness claim. |

## 2. Verdicts (after reading Part B)

**Overall proposal verdict: MODIFY.** Authorise only a bounded pilot after human approval, rather than the protected ten-structure production wave. No new calculations or infrastructure changes are authorised by this review. Findings below use the committed phase-1 checks; no network, ATLAS or CERN was used. The PDF's text was read locally by decompressing its content streams with Python's standard library.

### Claims and assumptions

All seven HO-003 assumptions remain **HYPOTHESIS** unless a narrower status is explicitly stated. A claim verdict is distinct from a charter status.

| Item | Verdict | Reason | Test that would change it |
|---|---|---|---|
| B1. MACE-MP-0 structures plus geometric QC and one short 80-atom bulk MD check suffice | REVISE | Neither the potential artifact nor domain validation is supplied. Bulk stability does not validate W environments, hydroxylated surfaces or the quenched ensemble. DFT relaxation cannot establish representative disorder. | Audit exact model/version/elements; compare DFT forces and relative energies on multiple bulk, W and surface snapshots, with tolerances declared before results; test two independent hosts. |
| B2. 125–170 atom slabs finish relaxation, SCF and DOS in 1–4 days | UNRESOLVED | Raw executable timings reproduce, but no queue or amorphous convergence bound exists. A relevant 176-atom relaxation took 41h28m before later stages. | Representative end-to-end pilot recording queue time, ionic-step count, RAM, restart and post-processing; revised conservative delivery estimate. |
| B3. ≤20 h DAG segments avoid credential expiry | REVISE | Segment duration does not demonstrate credential delegation/refresh. Existing driver omits QE save state and suppresses copy failures. A successor may start with expired credentials. | Two forced segments on fresh scratch, including a successor after the original credential lifetime; verify EOS access, complete checkpoint recovery and agreement with uninterrupted reference. |
| B4. Five thicknesses are the highest-value priority | REVISE | Thickness coverage comes before paired controls, seed variation and termination validation; the 2 nm composition differs. With no new measurements this cannot establish a device crossover. | A paired replicated pilot shows a W/thickness contrast larger than seed, composition, size and termination sensitivity. |
| B5. One sample gives useful indicative trends | REVISE | Individual model outputs can illustrate a possibility (**COMPUTED** when produced); one sample supplies no disorder statistics or robust trend. PDF wording “indicative statistics” must be removed. | Independent seeds and W placements establish variability; then specify the supported comparison and uncertainty. |
| B6. Runner is safe/acceptable and buildable in 1–2 days | UNRESOLVED | Merge approval, fixed templates and scoped key are sensible proposals, not a reviewed implementation or proof of account acceptability. No completed WF-001 design is named here. | WF-001 review, human account/setup approval and end-to-end test, including duplicate polling, retries, malformed tickets, output recovery and credential expiry. |
| B7. A2/A3/A1/A4 are highest-value ATLAS work at 15–20 launches | REVISE | Only 11 launches remain. A4 lacks a validated microscopic-to-TCAD mapping; A1 uses already-seen data. Cheap identifiability work should precede spending. | Itemised run matrix with incremental information and stop rules, within 11 launches or an explicit budget increase; mapping audit before A4. |
| Plan §0/Q8: RQ-001 is explained/closed by definitions | REVISE | Numerical compatibility is supported (C030/C032); actual recipe, units, provenance and near-floor physical interpretation remain unresolved (C024/C025/C031). | Fab documentation resolves recipe/provenance; registered repeat metrology resolves the steep section. No request for holdout release. |
| Plan: constant ~2% W series | REVISE | Phase 1 finds ~1.49% at 2 nm and ~1.98–1.99% elsewhere. The PDF's “2% needs ~250 atoms” is not necessary by composition arithmetic: In49WO75 is a 125-atom host with 2% W; lateral-size validity is a separate issue. | Exact final atom-count and lateral-size audit; retain the concentration exception or redesign without claiming fixed composition. |
| Q2/deliverable 1: slab DOS replaces fitted tail laws | REVISE | Finite-cell broadened DOS is not automatically an electrically active trap distribution. Surface termination, energy reference and smearing can create apparent tails. | Prespecified normalization, energy alignment, broadening/size/seed convergence and charge-state/occupancy mapping, with propagated uncertainty. |
| Studies 2/7: HSE-corrected amorphous gaps and electron-affinity thickness law | UNRESOLVED | A crystalline correction ratio is not validated for amorphous or localized states; vacuum alignment depends on termination and dipoles. | Matched representative hybrid checks and converged slab vacuum/dipole alignment; otherwise report PBE results with scope. |
| Mobility outputs: m*, free fraction and roughness explain μ_FE without fitting | REVISE | An amorphous supercell curvature is not automatically a transport mass; free-state classification needs a criterion; periodic surface heights are not measured roughness. ATLAS still needs transport/scattering assumptions. | Define each observable and mapping, validate sensitivity, freeze remaining parameters and report comparison as retrospective unless genuinely unseen data are registered. |
| Interface states determine D_it and Q_f | REVISE | DOS alone does not fix charged-defect occupations or fixed charge; interface chemistry and actual contacting oxide are unconfirmed. | Explicit charge/occupancy calculation and chemically justified interface ensemble, followed by independent C–V constraints when available. |
| Q5/Q6: ATLAS determines floor origin and critical thickness | REVISE | Simulated geometry/depletion can show sufficiency, not select a cause. C006/C027 remain HYPOTHESIS; one curve per thickness cannot identify a crossover. | Registered multi-V_D/current-terminal/isolation tests for floor; device statistics and thickness/provenance for crossover. |
| Full completion on 15 Oct | REVISE | Plan itself places full analysis and A1/A4 on 15–17 Oct and verification on 19–20 Oct. PDF calls 15 Oct a jobs target. Neither supports “everything finished.” | Human-selected definition of completion, revised critical path and measured pilot turnaround with analysis/verification reserve. |
| Pool probe establishes usable capacity | UNRESOLVED | Live probe transcript is not archived in supplied evidence; unclaimed capacity does not establish eligibility, queue waits or future allocation. | Archived account-specific pilot submission/resource and queue records. |

### Proposals and changed ordering

| Item | Verdict | Reason | Test that would change it |
|---|---|---|---|
| Analyse existing 2 nm W slab | ACCEPT | No new compute; closes an existing evidence gap. Use corrected band count and matched pure reference; report computed host/W character and filling. | Missing/mismatched outputs would require narrowing or deferring analysis. |
| Pd barrier = WF(Pd) − EA(IWO) | MODIFY | Useful only as an ideal Schottky–Mott estimate, not an actual Pd/IWO barrier or contact explanation; interface dipoles/pinning are absent. | Explicit interface or contact data support a device barrier. |
| ML environment and structure generation | MODIFY | Pin artifacts and audit chemistry first; geometric QC is necessary, not sufficient. Include O/H, W coordination, density excluding vacuum and periodic-image distances. | Domain/force checks pass for selected snapshots. |
| Short DFT ML check | MODIFY | Promote from priority 2 to prerequisite; include surface and W snapshots, not only one bulk MD trajectory. | Prespecified force/energy and structure checks pass. |
| Ten-structure wave 1 submitted immediately by hand | DEFER | Bypasses validation and proven restart; hand submission does not remove those dependencies. | Human-approved limited pilot passes scientific and delivery gates; expand only within measured resource/time budget. |
| Protected five-thickness series and existing cut order | MODIFY | Protect paired controls, second seed, termination comparison and recovery first. Cut intermediate/unpaired thickness coverage before controls. | Pilot establishes robustness, then add a second thickness with matched chemistry and controls. |
| Neutral vacancies: near W, far W, pure | MODIFY | A bounded crystal comparison is useful but cannot establish amorphous or thickness-dependent vacancy suppression. Define pristine references, O chemical potential, site choices, convergence and energy difference in advance. | Matched formation-energy results robust to site/cell choice justify extension; no outcome supports H4 without thickness comparison. |
| ~190-atom amorphous oxide interface wave 2 | DEFER | Two disordered materials and uncertain chemistry introduce extra validation; expensive before the simpler pilot is interpretable. | Verified contacting oxide, validated constituent structures and time budget for matched references/charge analysis. |
| Surface variants, second seeds, HfO2 extras | MODIFY | Second seed and one termination comparison are core controls; HfO2 expansion can wait. | Robust pilot makes additional surfaces/interfaces informative. |
| A2 off-current geometry | MODIFY | Start with analytic geometry bounds and a registered drain-voltage prediction; allocate minimal ATLAS cases to test numerical sufficiency. Unknown layout must remain explicit. | Verified layout and subsequent discriminating measurements select mechanism. |
| A3 thick-film depletion/critical-thickness scan | MODIFY | Use 1-D depletion and parameter degeneracy first; bounded ATLAS sensitivity is legitimate, fitting 31.8 nm is calibration. | Independent donor/back-surface constraints or replicated device trends discriminate mechanisms. |
| A1 leave-one-film-out shared surface/bulk model | MODIFY | Freeze choices and score all folds, including failures; call it retrospective cross-validation because every curve and earlier failure are known. | Truly unseen custodian-held data, frozen model and external registration support prospective prediction. |
| A4 DFT inputs → TCAD mobility/SS | DEFER | No defined conversion from DOS/IPR to trap kinetics, active density or band mobility; replacing inputs can disguise new fitting. | Written frozen mapping with units, occupancy, remaining calibration and uncertainty, reviewed before launches. |
| Raise ATLAS budget to ~90 | DEFER | Scope and necessity are not established; increasing cap adds 19 launches beyond 71, while 11 remain. | Human approval of itemised discriminating runs after cheap analysis and pilot gates. |
| Build autonomous runner in WF-002 | MODIFY | Review WF-001 separately. Bind approval to immutable spec/template/environment hashes; lock polling, record submission durably, reconcile interrupted submissions, bound retries and fail closed on invalid specs/transfers. Stage local scratch and use explicit verified checkpoint/output delivery. The repo key should not enter job payloads. | Reviewed design plus laptop-independent pilot and failure/recovery tests; otherwise use bounded supervised DAGs. |
| All files on EOS; AFS holds only key | MODIFY | Execution/recovery must work through EOS outages or token expiry. Define runner location, local scratch, durable state and manifests; do not assume EOS access remains live. | Recovery test proves persistence and delivery across segment boundaries/access failure. |
| 16/18 Oct submissions and 20 Oct hard stop | MODIFY | Cutoffs must depend on measured remaining runtime, queue allowance and export/recovery reserve. A hard stop must preserve recoverable results; a date alone is insufficient. | Conservative remaining-time estimate supports each final submission and verified export before access ends. |
| Defence/paper deliverables | MODIFY | Offer validated computational contrasts, explicit model non-identifiability and retrospective comparisons; retain mechanism claims as HYPOTHESIS. No venue-driven promotion or unvalidated “computed laws.” | Independent validation and registered unseen tests support stronger statements. |

**Recommended sequence (proposal MODIFY):** (1) existing W-slab analysis, offline checkpoint audit and analytic model audit; (2) human-approved small restart/delivery pilot and bulk/W/surface potential checks; (3) one thickness with paired pure/W hosts, two independent hosts and a bounded termination comparison, exact composition and analysis protocol frozen; (4) only after passing gates, either a second matched thickness or the bounded neutral-vacancy comparison, chosen by remaining time and the scientific question. The illustrative controls are a minimum robustness screen, not proof of ensemble convergence. If validation fails, stop expansion and report the negative result; do not automatically substitute a hurried full DFT quench.

**Most strengthening result:** a reproducible paired W/pure contrast that survives seed and termination changes under validated DFT, with a clear limitation on its relation to devices. **Most weakening failure:** the apparent thickness/W trend disappears or reverses under those controls, showing the protected series measures model construction rather than robust physics. Both outcomes are useful evidence; neither justifies erasing registered TCAD failures.

## 3. Proposed ledger changes

No new production result exists, so this review promotes no mechanism claim. Retained entries below are explicit recommendations, not edits to the ledger. Proposed new IDs are provisional and must be assigned by the owner.

| Claim ID | Current status | Proposed status | Evidence |
|---|---|---|---|
| C005 | INFERRED | UNRESOLVED; reword “gate leakage is not established or excluded” | Flat I_D versus V_G alone, without I_G, cannot establish the categorical exclusion; alternatives remain in HO-003 B5/context. |
| C006 | HYPOTHESIS | HYPOTHESIS, retained | Single-V_D floor and fitted strip constant; future A2 geometry is a sufficiency test, not mechanism identification. |
| C014 | FALSIFIED | FALSIFIED, retained; restrict wording to the tested V1/V2 shared-parameter predictions | Registered failures do not falsify every possible shared-parameter model; A1 cannot retrospectively convert those failures into successes. |
| C015 / C016 | FITTED | FITTED, retained | No validated amorphous law or independent donor constraint has been produced. |
| C017 | DERIVED | DERIVED, retained; say “two-anchor surface/bulk decomposition” | Algebraic decomposition is not physical identification; surface/interior DOS needs active-trap mapping. |
| C020 / C022 | COMPUTED | COMPUTED, retained with crystalline scope | Existing crystalline calculations; proposed amorphous runs do not yet supply evidence. |
| C021 | COMPUTED | COMPUTED, retained; distinguish stoichiometry from bonding/phase assignment | Phase 1 reproduces In8O24H24 = In(OH)3 composition but does not verify the asserted structural phase or remeasure thickness. Complete existing-result logging first. |
| C023 | LITERATURE-SUPPORTED | LITERATURE-SUPPORTED, retained | Neutral crystal vacancies and IPR proposals do not yet test the general device statement. |
| C024 / C025 | UNRESOLVED | UNRESOLVED, retained | RQ-001 numerical reconciliation does not confirm recipe/provenance or near-thermal physical interpretation. |
| C026 | OBSERVED | OBSERVED, retained | One device per film; no new device statistics. |
| C027 / C028 | HYPOTHESIS | HYPOTHESIS, retained | No new measurements; simulated depletion and disorder do not establish measured critical thickness or anomaly. |
| C029 | DERIVED | DERIVED, retained; explicitly retrospective/calibration in A3 | Known 31.8 nm curve, independently reproduced in phase 1. |
| C030 / C032 | DERIVED | DERIVED, retained | Numerical definition/estimator compatibility; limits from reviewed RQ-001 remain. |
| C031 | INFERRED | INFERRED, retained | Leading candidate for recipe, not confirmed method; plan's “definitions, done” language overstates it. |
| NEW-PLAN-ML | Not registered (HO-003 B1) | HYPOTHESIS | Potential adequacy for quenched In–W–O/H surfaces is unvalidated. Record validation requirements before production. |
| NEW-PLAN-DELIVERY | Not registered (B2/B3/B6) | UNRESOLVED | Historical timings reproduced; credential, full restart, queue and runner delivery claims lack end-to-end evidence. Keep operational claims separate from scientific predictions. |
| NEW-PLAN-WTREND | Not registered (B4/B5; studies 3–6) | HYPOTHESIS | W changes amorphous edge localization/tails beyond seed, termination, concentration and periodic-size effects; falsifier is no robust paired contrast. |
| NEW-PLAN-MAPPING | Not registered (Q2/Q7; A4) | HYPOTHESIS | Finite-cell DOS and localization can constrain electrically active TCAD trap/transport inputs; mapping and independent tests remain absent. |

Human decision: approve a capped pilot and conditional expansion, or postpone production; define whether 15 Oct means delivered jobs or reviewed results, and approve any separate ATLAS budget increase. Record the decision in the decision log through the owner/humans. This review is not a go instruction.
