# Plan: from the published IWO data to a Nature paper

> **STATUS: PROPOSED.** This is a hypothesis for the next research programme, not an approved plan (decision D-09).
> It is under independent review (RQ-005). Do not expand it until the review is answered (`prompts/04_CLAUDE_RESPONSE_TO_REVIEW.md`).
>
> Wording note: "no per-device fitting" in this plan means **no target-device-specific post-hoc fitting** (charter §4). Global parameters may be calibrated on declared training data and independent measurements, then frozen.

Draft, 7 October 2026. Kept out of the public repository because it discusses unpublished plans and our collaborators' paper.

**Change log**
- 2026-10-07: The "31.8 nm blind test" is withdrawn. That curve has been in our data since September (`01_CURRENT_STATE.md` §H.5).

## 1. Where we stand

### 1.1 What the fab group has already published

Januar, Luo, Liu and Lee, *Small Structures* 7, e202500807 (2026):

- bottom-gate IWO (~2 % W) and In2O3 TFTs, 2–13 nm (plus a 31.8 nm IWO device in Figs. 4a and 5e; its curve is already in our data file and it never turns off: I_D(−3 V) = 3.0e-7 A/µm); sputtered channels, ALD at 250 °C, RTA at 150 °C;
- an analytic "blended-current" model with eight fitted parameters per device;
- crystalline DFT (bulk In2O3, W:In2O3 with 5.3 % W) and IWO/HfO2 interface slabs;
- DOS reconstruction, roughness-limited mobility, positive and negative bias stress, 65 and 85 °C data.

**Consequence.** A new paper cannot be built on re-analysing these curves. The Nature paper needs new devices and new measurements; the published data and our analysis of them become its starting point (cited, and in Methods).

### 1.2 What we bring

- Physics TCAD (V1 calibrated per film; V2 with DFT thickness laws) and a written extraction protocol with uncertainties.
- DFT of thin slabs: band-gap increase +0.335 eV and m* = 0.206 m0 at 2 nm; 0.75 and 0.51 nm slabs (PBE gaps 2.20 and 3.14 eV; the 0.51 nm layer relaxed into an In(OH)3-like structure).
- Registered tests (the 6.3 nm blind test failed, as registered).
- Findings:
  - SS collapses onto one curve against I_D/I_on, in measurement and TCAD;
  - the 13.2 nm SS mismatch;
  - the off-current floor scales as t^3.85 (ungated-strip hypothesis).

### 1.3 What would stop a Nature paper today

| # | Gap | Why it matters |
|---|---|---|
| 1 | One device per thickness; one drain bias; no gate current; no reverse sweep | No statistics; device physics cannot be separated from device-to-device scatter |
| 2 | Model calibrated per film; the one blind test (6.3 nm) failed | The model describes; it does not yet predict |
| 3 | Published values and ours differ for the same devices | See the two rows below |
| 3a | Mobility | Paper: μ_max 27.4 / ≈4 / 5.1 cm²/Vs (13.2 / 6.3 / 2.0 nm), falling with V_G (Fig. 5d). Ours: peak 50 / 11 / 12, rising up to ~3 V (g_m-based, geometric C_ox, W/L = 290/20, V_D = 0.7 V) |
| 3b | SS at 2 nm | Paper: 60–70 mV/dec (≈62 in Figs. 4d and 6e). Ours: 89.1 ± 0.5 over 3.3 decades (5.6e-14 to 1e-10 A/µm); 123.6 in the normalised window |
| 4 | Off-current origin open | The paper's diffusion formula (Eq. 1f) and our ohmic strip predict different V_D dependences; this is easy to test |
| 5 | DFT is crystalline; the films are amorphous or nanocrystalline (paper's HRTEM) | Trap states are not derived from the real structure |
| 6 | No headline result yet | Nature needs a result of broad interest |
| 7 | The fab's raw curves are in our public GitHub repo (`data/experimental_raw_preserved_IWO-TFT.xlsx`, `data/experimental_clean.csv`, `inputs/.../IWO-TFT (1).xlsx`); their paper releases data only on request | Settle with them before anything else |

## 2. The paper we aim for

**Question.** What limits oxide-semiconductor transistors at the atomic scale, and can physics predict such a device before it is made?

**Headline claim (to be earned).**
- A model with no per-device fitting passes a registered blind test for W:In2O3 transistors down to sub-nanometre thickness. Its inputs come from DFT and from independent measurements.
- Guided by it, we make BEOL-compatible transistors (process ≤ 250 °C) with a record combination of normally-off operation, mobility, swing, off-current and stability, and show them in an application.

**Why this can be Nature.**
1. Predictive, pre-registered device physics is rare. Most oxide-TFT models, including the published one, are fits.
2. The atomic-thickness limit of oxide channels is central to monolithic 3D integration, a broad topic.
3. A record device plus an application gives the broad-interest result.

**Venue.**
- Nature first, after a presubmission enquiry.
- If the editors decline, the Nature transfer service offers Nature Electronics.
- Gate G3 decides, on the device results.

**Main figures (we work backwards from these).**

1. **Atomic structure.**
   - STEM cross-sections from 0.5 to 13 nm.
   - Amorphous-IWO DFT: does W suppress oxygen vacancies and narrow the tail?
   - XPS and EXAFS as checks.
2. **Every model input measured independently.**
   - Thickness and roughness (XRR, TEM).
   - Band gap against thickness, compared with DFT.
   - Free-carrier density and mobility against V_G (gated Hall).
   - Fixed charge and D_it (C–V).
   - Trap DOS (temperature dependence).
3. **Prediction without fitting.** Model against at least 20 devices per thickness: transfer curves, SS collapse, mobility against V_G, and off-current on mesa and blanket films.
4. **Registered blind test.**
   - Predictions are deposited with a DOI before fabrication.
   - Devices: sub-1 nm thicknesses and the W-content splits.
   - Shown: measured against predicted, the design map and a benchmark against the literature.
5. **Application and stability.**
   - Application: 2T0C memory retention predicted from the off-current physics, or a two-tier BEOL stack.
   - Bias-stress shifts predicted by the model.

## 3. Work packages

### WP0 Agreements and consistency (weeks 1–2, before anything else)

- **Meeting.** Prof. Min-Hung Lee and Dr. Mochamad Januar (fab), Mukul and Prof. Wu. Agree on:
  - scope and authorship;
  - who holds new data until our predictions are registered (the "data custodian");
  - fab capacity;
  - budget: device runs, Hall, XPS and synchrotron time (e.g. NSRRC, Hsinchu, for EXAFS).
- **Data.** Get written permission for the raw curves in the public repository, or switch the repository to private until publication. This is your action, in the GitHub settings.
- **Definitions.**
  - Agree one V_D, one W/L and one C_ox (geometric 8.955e-7 F/cm², or from C–V).
  - Agree one mobility definition and one SS definition for both groups.
  - Follow Cheng et al., "How to report and benchmark emerging field-effect transistors" (Nat. Electron., 2022), and Choi et al., "Critical assessment of charge mobility extraction in FETs" (Nat. Mater., 2018).
  - Reconcile items 3a and 3b of Section 1.3 before any joint figure.
- **Existing data we do not have.**
  - Request: In2O3 3/10/11 nm; the bias-stress series; the 65/85 °C curves; C–V (Fig. S1); the annealing series (RT, 150, 200 °C); raw AFM and TEM.
  - Register predictions first for any data nobody on our side has seen (the 65/85 °C curves, if SI Fig. S12 has not been looked at). Correction (7 Oct): the 31.8 nm IWO curve is already in `data/experimental_clean.csv` and V1 fails on it, so it is not a blind test.

### WP1 Existing chips: diagnostics (fab, weeks 2–8)

| Measurement | Conditions | What it decides |
|---|---|---|
| Transfer statistics | ≥ 10 devices per thickness; V_D = 0.05, 0.1, 0.7, 1.0 V; forward and reverse; V_G step ≤ 10 mV; I_D, I_S and I_G recorded | variability, hysteresis, gate leakage; SS over ≥ 2 decades |
| Floor against V_D | V_D = 0.05–1 V | Ohmic strip: floor ∝ V_D (×7 from 0.1 to 0.7 V). Paper Eq. 1f: saturates above ~0.1 V (changes by ~2 %) |
| Floor against layout | probes lifted; different W and L; does IWO extend beyond the gate? | instrument baseline; strip geometry |
| Temperature | as wide as the probe station allows (e.g. 250–400 K) | activation energy, which gives the trap DOS(E); SS(T); floor activation |
| TLM | L series, if on the chip | contact resistance; intrinsic mobility |
| C–V and G–V on MOS capacitors | several frequencies | D_it(E), V_FB, fixed charge |
| Materials on the same films | XRR; XPS (W 4f, O 1s); ellipsometry or UV–Vis | true thickness, density and roughness; O-vacancy fraction; band gap against thickness (DFT predicts +0.335 eV at 2 nm) |

### WP2 Computation (us; can start now)

**2a Amorphous DFT (CERN)**
- a-In2O3 and a-IWO (0, 2, 4, 6 at.% W), with at least 5 independent melt-quench structures each. Use ab initio MD, or a machine-learned potential trained on DFT.
- DOS and inverse participation ratio, to get the tail width and the deep states.
- Formation energies of O vacancies and H near and far from W. This tests "W suppresses vacancies" directly.
- Hybrid-functional check on a subset.
- The interface between the channel and the gate oxide. Ask the fab which oxide touches the channel (Al2O3 or HfO2).
- Check the density against XRR.

**2b Atomic-thickness limit**
- Finish the 0.5–2 nm slab series with and without W, including surface hydroxylation and an Al2O3 cap.
- The 0.51 nm result suggests that surface chemistry, not only confinement, decides whether sub-1 nm channels conduct.

**2c Model V3, with no per-device fitting**
- Band gap, affinity and m* against thickness from DFT, checked by optics.
- Fixed charge and D_it from C–V; donor density from Hall and XPS; tail DOS from temperature data and DFT.
- Surface and bulk traps, separated using the thickness series.
- Mobility: trap-limited transport, plus thickness-fluctuation roughness scattering (∝ t^6 in ultrathin films; Sakaki 1987, Uchida and Takagi 2003) with the measured roughness, plus Coulomb scattering.
- Quantum confinement in the solver.
- The off-current path from the real layout.
- A few global parameters, calibrated once on a training set and then frozen. Use Bayesian calibration through a fast surrogate of ATLAS, so every prediction carries credible intervals.
- Mesh and solver verification.
- Needs a new ATLAS launch budget (60 of 71 used; your decision).

**2d Registration**
- Deposit predictions and evaluation scripts with a timestamped DOI (Zenodo or OSF) before the data exist.
- The fab holds the data until then.

**2e Design maps**
- Map thickness × W content × EOT to V_th, SS, μ and I_off.
- Pick the splits that best separate the hypotheses, and predict the best device.

**2f Literature test**
- Check the SS collapse and the thickness laws on published In2O3-family devices.

### WP3 New devices (fab, months 2–8)

**Run 1: training and diagnostics**
- Thickness 0.5, 0.7, 1.0, 1.5, 2, 3, 4.5, 6.3, 9 and 13.2 nm, for IWO and In2O3.
- W content 0, 1, 2 and 4 at.% at 2 and 6.3 nm.
- Structures:
  - mesa-isolated channels (IWO only inside the gate) next to the current layout;
  - TLM (L = 2–50 µm);
  - gated Hall bars;
  - large MOS and MIM capacitors.
- Passivation split: none, or an ALD Al2O3 cap.
- At least 20 devices per split, on at least 2 dies.

**Run 2: blind test and best device**
- Splits chosen by the model; predictions registered before fabrication.
- The best Run-1 device repeated (run-to-run reproducibility).
- Short channels (L ≤ 1 µm) for on-current benchmarks.

### WP4 Stability and application (months 6–10)

- PBS, NBS, PBTS at 85 °C and NBIS: 10^4 s plus recovery. ΔV_th is predicted from the model's trap changes.
- One application, chosen with the fab:
  - a 2T0C memory cell; its retention is set by I_off, which the off-current physics predicts (Belmonte et al., IEDM 2020, for the cell concept);
  - or a two-tier BEOL stack with inverters and ring oscillators.

### WP5 Paper (months 9–12)

- Presubmission enquiry to Nature (abstract and key figure).
- Methods: the extraction protocol, registration DOIs, reporting checklist and uncertainty budget.
- Data and code: GitHub and a Zenodo DOI, with the fab's agreement.
- Our analysis of the published curves goes into Methods and Extended Data.

## 4. Decision gates

| Gate | When | Pass condition | If it fails |
|---|---|---|---|
| G0 | week 2 | The fab commits to WP1 and Run 1; data and authorship are agreed | No new devices, so no Nature path |
| G1 | month 3 | The off-current origin is decided, and V3 reproduces all existing devices from measured inputs within registered tolerances (e.g. V_th,cc ± 0.1 V, SS ± 10 mV/dec, I_on ± 20 %, μ_FE(V_G) ± 15 %) | Revise the physics before Run 2 |
| G2 | months 6–7 | The registered blind predictions for Run 1 pass | Report it, find the missing physics, and repeat on Run 2 |
| G3 | month 9 | The best device and the application are ready | Decides Nature or Nature Electronics |
| Submit | ~ month 12 | | |

## 5. Risks

- **Discontinuous sub-1 nm films.** Sputtered films below ~1 nm may not be continuous. Check by XRR and TEM in Run 1; if they are not, ~1 nm becomes the limit studied.
- **Limited fab capacity.** Priority: WP1, mesa devices, temperature, C–V, XRR/XPS and the Run-1 thickness splits.
- **Failed blind test.** It would still be informative, but it would not be a Nature headline.
- **Changed published values.** Harmonised definitions may change the published SS and mobility. Settle this privately with the fab first.
- **Cost of the amorphous DFT.** Use machine-learned potentials and the CERN GPU nodes, and start now.

## 6. What I can start now (your go needed)

| # | Task | Cost |
|---|---|---|
| 1 | Register the off-current predictions for the V_D and mesa tests (our strip against the paper's Eq. 1f) | 1 day; no ATLAS runs |
| 2 | Consistency memo for the fab: mobility and SS side by side, with definitions | 1 day |
| 3 | Measurement request sheet for WP1 (conditions, file format) | 1 day |
| 4 | Registered predictions for the 65/85 °C curves (if unseen) and for new multi-V_D measurements of the existing chips | 2–3 days; ~4–6 ATLAS runs |
| 5 | Model V3 specification | 2–3 days |
| 6 | Amorphous DFT on CERN (needs your lxplus login) | set-up ~1 week, then weeks of runs |
| 7 | T4 sub-1 nm registered predictions | on hold until you say go |
