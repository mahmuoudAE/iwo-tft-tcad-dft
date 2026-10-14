# Review of PLAN-001 / HO-003

| Field | Value |
|---|---|
| Reviewer | Codex |
| Commit reviewed | Private HEAD b78680c50bb5fc4f1c99d2d425a3a0199e3de6f7; public evidence HEAD f315b78dc4958a0749ec9121ab9a287d2fa66f10 |
| Date | 2026-10-10 |
| Scope | Phase 1 evidence assessment; no proposal verdicts |

## 1. Independent assessment

**Independence limitation.** This is not a strictly blinded phase-1 assessment. My first successful handoff extraction used an incorrect boundary and displayed HO-003 Part B, plus later handoff material. I reported the mistake immediately. I did not open the owner's plan, PDF timeline, response files or separate interpretation files. The results below are independently checked against raw evidence, but independence of hypothesis selection cannot be claimed. A fresh reviewer is needed if strict blindness is required. No commit or push was made, as required by relay mode.

### What the evidence supports, with status labels

- **DERIVED:** Every A3 timing row is reproduced from the raw `PWSCF ... WALL` line, with matching atom counts, irreducible k-points and reported parallel core counts. These are executable wall times, not queue-to-delivery times. Raw paths below are relative to `../IWO_PHYSICS_CONSTRAINED_MODEL_V1/qe_workflow/cern_htcondor/results/`.

| Raw file | Atoms | k-points | Reported cores | WALL |
|---|---:|---:|---:|---|
| iwo_W24d/spin_k3.out | 80 | 10 | 32 | 2h39m; 26 iterations |
| iwo_W24d/relax.out | 80 | 10 | 32 | 23h48m |
| iwo_W8b/relax.out | 80 | 6 | 32 | 10h02m |
| slab1r_final_cpu/scf.out | 96 | 4 | 16 | 2h19m |
| iwo_slab2_final_cpu/scf.out | 176 | 4 | 33 | 8h05m; 91 iterations |
| slabL2_relax_v2/vcrelax.out | 76 | 4 | 1 | 9h58m |
| slabL2_relax_v2/scf.out | 76 | 4 | 11 | 1h06m |

- **DERIVED:** An additional relevant benchmark, `slab2_relax_c2/vcrelax.out`, reports **1d17h28m = 41h28m**, for 176 atoms and four irreducible k-points. The results log identifies it as a GPU relaxation. The one-core banner does not mean a comparable CPU-only run. Hardware, symmetry, occupations, starting geometry and SCF convergence must accompany any timing extrapolation.
- **DERIVED:** At the assumed density 7.0 g/cm³, stoichiometric In2O3 has 75.9185 atoms/nm³ and 30.3674 metal atoms/nm³, using molar mass 277.633 g/mol. One W per 50 metal atoms requires **1.64650 nm³**. A5's 76, 30 and approximately 1.7 are consistent rounding; the density itself is an assumption, not a measurement of these films.

| t (nm) | A5 lateral size (nm) | Estimated host atoms, excluding termination | One-W metal fraction (%) | Lateral size for exactly 2% (nm) |
|---|---:|---:|---:|---:|
| 2.0 | 1.05 | 167.40 | 1.493 | 0.9073 |
| 1.5 | 1.05 | 125.55 | 1.991 | 1.0477 |
| 1.0 | 1.29 | 126.34 | 1.979 | 1.2832 |
| 0.8 | 1.44 | 125.94 | 1.985 | 1.4346 |
| 0.7 | 1.54 | 126.03 | 1.984 | 1.5337 |

- **DERIVED:** A5 explicitly acknowledges the 2 nm exception. That cell has approximately 25% less W fraction than the other cells. Integer stoichiometry and added surface atoms require a final composition audit; density arithmetic alone is not an actual structure.
- **DERIVED:** The inspected SCF inputs establish existing slab compositions: In8O24H24 (56 atoms), In16O36H24 (76), In24O48H24 (96), In23WO48H24 (96), and In55WO96H24 (176). Existing W fractions are **4.167% at 1 nm and 1.786% at 2 nm**, not a constant-composition series. The thinnest structure has exactly the composition In(OH)3; composition alone does not establish its bonding phase. Surface H is 42.86% of the 56-atom cell and 31.58% of the 76-atom cell.
- **OBSERVED:** The inspected inventory and `RESULTS_LOG.md` establish crystalline reference calculations and existing projections that can be analysed without launching new jobs. No amorphous/defect/interface calculation was identified in the inspected evidence; this is an inventory statement, not proof that none exists outside it.
- **OBSERVED:** The results log documents expired in-job EOS access, memory holds, lost output and a watchdog that incorrectly removed a progressing SCF. These operational failures have already occurred and affect usable turnaround.
- **OBSERVED:** `jobs/common/driver.sh` packs `*.out`, `*.in`, `*.tmpl`, `*.dat`, `*.log`, `steps.sh` and `pdos/*`, but not `tmp/*.save`. Its checkpoint transfer falls through to `|| true`. The current mechanism does not prove that a complete electronic restart survives a segment boundary, and copy failure can be hidden.
- **DERIVED:** A direct CSV re-extraction gives constant-current thresholds **0.6618205 / 0.6440037 / 0.0825222 V** at 1e-9 A/µm. The 31.8 nm curve never crosses that current; its endpoint on/off ratio is **11.9761**. Each thickness has 121 points. These reproduce the stated threshold pattern and thick-film failure. Endpoint ratios for thin films are not the protocol floor-based on/off ratios.

Reproduction uses only Python's standard library. Script: `codex/independent_reviews/PLAN-001_check.py`; machine-readable results: `PLAN-001_check_results.json`. No network, ATLAS, CERN access or new simulation was used.

### What the evidence does not support

- **UNRESOLVED:** Completion by 15 Oct. Historical executable times do not supply queue distributions, amorphous ionic-step counts, required memory, restart overhead, post-processing time or analysis time. The nominal 10–21 Oct access window is not the same as the 10–15 Oct delivery target. The 41h28m relaxation makes a multi-day runtime plausible but cannot establish an upper bound.
- **UNRESOLVED:** A representative amorphous-film mechanism from a single small periodic cell. Changes in thickness, lateral size, W fraction, termination, seed and W placement can all change the output. A DOS or localization trend alone does not demonstrate a mobility edge or device transport crossover.
- **UNRESOLVED:** Validity of any proposed ML potential for In–W–O or its surfaces. Part A supplies no model artifact, supported-element audit, training-domain evidence, DFT force comparison or structural ensemble. Plausible density and bond lengths are necessary checks but insufficient force-field validation.
- **UNRESOLVED:** Autonomous credential refresh or restart safety. A new DAG node is not evidence that usable credentials are refreshed. Geometry continuation and full wavefunction/charge-density/BFGS restart are different procedures and must be named and tested separately.
- **UNRESOLVED:** A scientific critical thickness, W-dependent shift or microscopic cause of the 6.3 nm failure. Single-device existing curves cannot distinguish those from batch, history, contact or thickness variation. More calculations cannot supply the missing device statistics.
- **UNRESOLVED:** Pool/GPU availability for this account and resource request. Unclaimed cores or GPU listings do not measure schedulable capacity, eligibility or future queue waits.

### My competing hypotheses

All new explanations below are **HYPOTHESIS**.

1. Apparent ultrathin gap growth is partly a termination/stoichiometry transition: increasingly hydroxylated slabs become chemically different from the measured channel. Compare surface-projected states and alternative electron-count-consistent terminations at fixed interior geometry before interpreting a thickness law.
2. Apparent W delocalization is concentration, periodic-image or filling behaviour rather than a change in disorder. Compare paired pure/W structures from the same host and vary W position or lateral size before varying five thicknesses.
3. Disorder-seed variability exceeds the thickness effect. A second independent host at one thickness is more discriminating than another thickness with one host.
4. The dominant device discrepancy is electrostatic non-identifiability or device provenance, rather than an incorrect crystalline confinement input. Existing threshold failures and fitted charge/mobility do not isolate DFT physics.
5. Deadline risk is dominated by queueing, checkpoint loss or slow ionic convergence, rather than atom count. A pipeline can finish SCF promptly and still fail to deliver a recoverable, analysable result.

### Cheapest discriminating tests

1. **First, offline archive/restart audit:** enumerate checkpoint members and map each continuation stage to its required state. The inspected driver already fails to demonstrate full-state preservation. Require explicit transfer success, a manifest/checksum and a recoverable last geometry; if full QE restart is claimed, require its save files too. Do this before spending a production launch.
2. Analyse the existing 2 nm W projections with the corrected valence-band count, alongside the matching pure reference. Report host CB versus W-derived character and Fermi filling, without translating it into device mobility. This closes an existing evidence gap with no new compute.
3. Audit proposed structures before launch: exact In/W/O/H counts, W/(In+W), density excluding vacuum, thickness definition, minimum distances, periodic W separation, dipole and surface fraction. Require a paired host/W comparison. Retain the 2 nm concentration exception explicitly or redesign it.
4. If humans approve new computation, run one representative pilot through two forced segments on fresh scratch: verify continuation, delivery and agreement against an uninterrupted small reference. Record queue delay separately, per-SCF and per-ionic-step time, peak RAM/disk and restart overhead. This is a proposed test, not authorisation to run CERN now.
5. Before any amorphous thickness campaign, test DFT energies/forces on several representative bulk and surface snapshots, including W local environments; then compare two independent seeds at one thickness. Define observable tolerances before inspecting outcomes. Stop expansion if seed/termination sensitivity exceeds the proposed trend.
6. With no new measurements, prioritise a bounded model-identifiability audit of existing curves and outputs. Additional fits are calibration/sensitivity studies; the known 31.8 nm curve is not a holdout. Preserve registered failures rather than fitting them away.

### Numbers and assertions not independently reproduced

- **A1:** No new measurements; access ends 21 Oct; completion desired 15 Oct. These are stated human constraints, accepted for this review, not independently measured facts.
- **A2, all live-probe values:** timestamp 10 Oct 09:26 UTC; credentials until 11 Oct 12:26; tools installed and empty acrontab; zero running project jobs; 10,427 pool jobs, 2,100 running, 5,539 unclaimed cores; GPU counts 74 A100, 56 H100 NVL, 63 V100/V100S, 19 H200; AFS 86% to 18%; current EOS artifacts and current SSH reachability on ports 22/443. Part A cites no archived raw probe transcript. They cannot be rechecked under the no-network/no-CERN instruction. Historical driver paths support intended artifact locations, not their current presence.
- **A4 thickness labels 0.51/0.75/1/2 nm:** atom counts and compositions reproduced; thicknesses were not independently remeasured from relaxed coordinates in this pass. Bulk inventory follows the protocol/results log; no exhaustive external inventory is possible.
- **A6 approximately 25h lifetime:** supported by the dated results-log account, not independently measured here. The precise lost-job state and every earlier symmetry failure were not reconstructed. Importantly, two symmetry operations are expected for some doped cells per the protocol and are not intrinsically evidence of a faulty structure; the 24-operation criterion applies to the appropriate undoped host reference.
- **A6 stall near 1e-8 Ry:** the historical log reports it; the final input independently confirms conv_thr 1e-8 and mixing_beta 0.1, and the output confirms 91 iterations. I did not reconstruct the lost SCF's complete iteration trajectory.
- No A3 wall time, atom count, k-point count or stated 26/91 iteration count failed reproduction. A5 arithmetic reproduces to its stated precision, conditional on density and stoichiometric-host assumptions.
- Other project-context gap, mass, mobility, SS, fitted-charge and prediction-error numbers were not all recalculated in this timing/structure assessment. They remain the labelled ledger context, not new independent confirmations. In particular, gap shifts must use matched bulk/slab settings: the results log uses a bulk gap 0.8887 eV for the 0.335 eV slab increment, not every bulk gap quoted elsewhere.

Strongest finding: DERIVED — A3 timings reproduce, but the existing archive omits QE save state and does not establish restartable segmentation.
Strongest doubt: UNRESOLVED — Small, differently terminated/composed cells may confound the thickness effect, and delivery by 15 Oct has no measured bound.
Test I would run first: Offline checkpoint completeness audit, followed only after human approval by a forced two-segment restart on fresh scratch.
