# 06 Verify: completeness review of `PLAN_C10_S2_S5_2026-10-14.md` (referee view, 2026-10-14)

**Status.** Review only. Nothing was launched, edited (apart from this file), committed or pushed, and CERN was not contacted.

**Read:** the plan in full (four line-range reads); `00_user_request_tunnelling_mesh.md`; `CAMPAIGN_DESIGN.md` §1, §3, §5–§7; `DFT_TO_TCAD.md` l.85–130; register l.12–42, l.95–178 and l.286–303; `CODEX_WORK_CHAT.md` l.282–303 and l.5480–5503; `01_CURRENT_STATE.md` l.77 and l.210–222; `config/solver.yaml`; the mesh lines of `build_iwo_decks.py`; `proc_guard.py` (grep); manual 5.28 lines as cited. Allowed scored JSONs: `hc_mesh_run_0076_run_0067.json`, `smoke_resolution_pair_run_0070_run_0069.json`, `smoke_resolution_pair_run_0071_run_0061.json` and `smoke_resolution_pair_run_0077_run_0067.json`.

**Not opened:** any output of run_0075, run_0076 or run_0077; anything under `sealed/`; AFF-6p3 or STRIP-6p3; any amorphous DFT quantity. I grepped the boundary-node lines of the run_0061/0067/0069/0070 logs (allowed). They were not informative and are not used.

**Tags.**
- **MUST-FIX**: blocks the named launch, or the named claim, until fixed.
- **SHOULD-FIX**: fix before the stage report.
- **REPORT**: disclose as a limitation.

Labels follow the plan's convention.

**Verdict.** The plan meets the user's tunnelling-mesh request: §7 has automatic-slice and QT-mesh series, cost, memory, the amendment, the checks and an outcome table. For a Nature/Science predictive claim it is not yet complete. Four items block specific launches (D1–D4). The others limit what can be claimed.

---

## A. Numerical convergence

### D1 — MUST-FIX (before the DIAG gate audits and any S2 statement; 0 launches). The numerics evidence is misstated.

**The problem.** Plan §3.5 says "DOS ×2 moved I_D by ≤ 0.0005 dec", and U8 says "mesh and DOS ≤ 0.0005 dec". These numbers are changes in *active RMSE*, not pointwise changes in I_D:
- S1-03: Δ = −0.0005 dec; S1-04: Δ = −0.00002 dec (register l.27–28; work chat l.303).

**What the pointwise data show** (COMPUTED (ATLAS), allowed JSONs):

| Pair | Points changing by > 0.1 dec | Candidate resolution |
|---|---|---|
| S1-03, mesh ×0.7 at 13.2 nm (`…0070_run_0069.json`) | 19 of 76 | 2.85e-18 A/µm |
| S1-04, DOS ×2 at 2.0 nm (`…0071_run_0061.json`) | 28 of 76 | 3.29e-18 A/µm |

**What is missing.** No channel-mesh refinement exists at 2.0 nm or 6.3 nm, and the 13.2 nm one is ×0.7, not ×0.5. H-A requires "numerical resolution … shown to be below that bound" (register l.115).

**Fix.**
1. Report the maximum |Δlog₁₀ I_D| over the J-window points, and the two resolution floors. The runs involved (0061/0069/0070/0071) may be read.
2. State that there is no channel-mesh evidence at 2.0 or 6.3 nm.
3. Optional: one 2.0 nm mesh ×0.7 run from the design's reserve item (2).

### D2 — MUST-FIX (before T1a / D1). S2-11 is not a clean discretisation signal.

**Non-monotonic I_G.** From `hc_mesh_run_0076_run_0067.json` (COMPUTED (ATLAS)), |I_G(V_G)| is non-monotonic for V_G ≤ −0.5 V:
- ×1 mesh: 1 inverted step (−2.8 → −2.6 V: 4.26e-13 → 1.13e-12 A/µm).
- ×0.5 mesh: 6 inverted steps.
  - An isolated spike at −0.70 V (9.43e-20 A/µm, against neighbours of 2.02e-21 and 2.69e-22) *is* the 2.86 dec maximum.
  - The §1.3 reading "+0.70 dec above the floor at −1.8 V" sits on an inverted segment: 2.34e-14 > 1.45e-14 (−2.0 V) > 8.71e-15 (−2.2 V).
- A single-barrier tunnel current should rise monotonically with |V_G| at fixed V_D, because the oxide field is monotonic in V_G (ASSUMED standard MOS argument). Inversions therefore point to non-mesh noise from nonlinear convergence, energy-window or slice handling, which the manual flags (5.28 l.13637–13642).

**I_G below the solver's own current criterion.**
- `ir.tol=1e-19` (solver.yaml l.4) is the absolute terminal-current criterion E2 (manual l.56202; criteria 20-4/20-5 at l.45780–45790). The weak-tolerance acceptance (l.45837–45838) can terminate once those current criteria hold.
- 42 of 75 resolved points are below 1e-19 A/µm on at least one mesh (CALCULATED). The DOS2 resolution R = 2.2e-31 A/µm is about 12 decades below IR.TOL. Codex 03:36Z already asked for this to be disclosed.
- **The FAIL is robust to this:** all 33 points with both |I_G| ≥ 1e-19 change by > 0.1 dec (maximum 1.65 dec at −1.4 V; CALCULATED).

**Fix, in PA-4 before T1a:**
1. An I_G resolution floor of at least IR.TOL.
2. A monotonicity QA: count the inverted steps for V_G ≤ 0, and class inverted points as "unconverged", not "resolved".
3. Log Newton iterations and residual norms per bias (Codex: "monitor … solver residuals").
4. One tolerance-axis replay of the run_0067 deck (IR.TOL and CR.TOLER ×0.01, or finer V_G steps over −2.8…−0.6 V), before or instead of T1b.
5. Drop the −1.8 V reading as a decision argument.

### D3 — MUST-FIX (before T1a; 0 launches). The T1a go-rule rests on a one-point linear memory model.

From 1.69 GB at 9,594 nodes (CALCULATED):

| Memory scaling | Prediction for T1a (21.3–21.5k nodes) |
|---|---|
| Linear | 3.75–3.79 GB |
| N·lnN | 4.08–4.12 GB |
| N^1.5 | 5.59–5.67 GB |

- run_0062 (13,689 nodes, out of memory at 2 GB) cannot tell these apart: it predicts 2.41 / 2.50 / 2.88 GB.
- Any superlinear scaling breaks the 3.9 GB rule.
- `proc_guard.py` defines `PeakProcessMemoryUsed` (l.113) but never logs it.

**Fix.**
1. Sample the peak working set of the DIAG QTNLSC runs (B1, B2, B6) with an external sampler. Leave the runner untouched, so the 1375164 runner-hash gate holds.
2. Fit the scaling exponent before T1a.

### D4 — MUST-FIX (before T1a; 0 launches). Predict T1a offline first.

**Reasoning.** The oxide holds no charge in these decks (Q_f sits at y = 0, and the trap charge is out of Poisson), so φ is linear in each layer (READING). An oxide refinement therefore changes only the staircase and slice sampling, not the electrostatics.

**Fix.**
1. Extend the Z9 script into an offline transfer-matrix study: exact Airy solution against the node-value and mid-point staircases. The ATLAS convention is UNVERIFIED, so do both.
2. Use the T0 node sets for ×1, ×0.5 and ×0.25.
3. If the predicted ×0.5 → ×0.25 change is > 0.1 dec, pre-register T1a as a Richardson level, not a pass test.

The plan already expects 0.1–0.2 dec (§7.2).

### D5 — SHOULD-FIX. PA-4 goes beyond Codex's bound, and T2 cannot certify the registered form.

- Codex 03:36Z allowed "one further refinement, then one conditional refinement" (2 launches). The plan proposes 3 planned and 5 at most. This needs Codex's explicit acceptance.
- The QT mesh is described for Athena/DevEdit meshes (l.13661–13667). run_0066 failed KCL.
- Suggestion: make T2a and T2b conditional on "T1a FAIL, erratic".

### D6 — REPORT, or MUST-FIX if PA-16 is adopted. The DOS quadrature was checked at W_T = 0.040 eV only.

- Level spacing E_g/NUMA = 3.37725/384 = 8.79 meV (CALCULATED). That gives 2.8 levels per W_T at the S4 lower bound of 0.025 eV, and 1.1 at 0.010 eV.
- At 0.025 eV the error is about (Δ/W_T)²/24 ≈ 0.5 % of the trapped charge (CALCULATED; smooth integrand ASSUMED).
- At 0.010 eV, add a DOS ×2 check before S4a.

---

## B. Uncertainty, identifiability, out-of-sample

### D7 — MUST-FIX (before the first S5 launch, in PA-13). S5 folds reuse inputs fitted with the held-out film.

**Inputs affected.**
- N_D 2.5e17: a V1 law fitted to the per-film values of all films (`02` D13).
- Δ_sr 0.287 nm: fitted by Januar on the same devices (`02` F7).
- The V1 start values N_s and W_T.

**Size of the N_D term.** N_D alone gives q·N_D·t/C_ox = 9 / 28 / 59 mV at 2.0 / 6.3 / 13.2 nm (CALCULATED).

**Fix.**
1. Add a fold-wise provenance table.
2. Re-profile Δ_sr inside each fold (U5b, exact, 0 launches).
3. State that the S5 results are conditional on an N_D fitted with all films, bracketed by S6-13/15.

### D8 — SHOULD-FIX (in the S4 report). The design §5.4 identifiability rule was dropped.

The rule is: condition number > 100 or |corr| > 0.95 means a parameter *combination* is reported. The plan mentions the Jacobian only in U2.

Degeneracies to pre-register:
- **On-current law.** μ∞, ℓ (and Δ_sr, fitted on the same devices) against three I_on values leave ≤ 0 effective dof. "ℓ is a fit, not a test" (register l.168).
- **V_th(t).** ΔE_c(t), the NC convention, N_D·t, N_s/t and Q_f all act on it.
- **R_c against μ.** There is one channel length and no TLM. R_c is not modelled because lumped and distributed elements need METHOD NEWTON CARRIERS=2 (l.2843–2846), and two-carrier runs stall (run_0073).

Add a 0-launch analytic series-R sensitivity on μ∞ and ℓ, with the ρ_c range ASSUMED.

### D9 — SHOULD-FIX (before S4a). The NC convention is the largest 2.0 nm systematic, yet its branch is unbudgeted.

- S1-05 FAILED its registered prediction: ΔV_th,cc was +142 mV against +40…+70 mV, and active RMSE went from 0.367 to 0.053 dec (register l.29).
- That exceeds the ±0.10 V acceptance.
- Budget PA-11 ahead of the exploratory items F13–F15 and Schottky B.
- The BQP decks use `nc_mode 3d` (matrix S3-24/25). Read BQP against S3-01 only, since against S0-01 it is confounded by the NC convention.

### D10 — REPORT. There is no secured prospective data source.

- P1–P3 need new fab measurements. The fab meeting and data custody are still open (`01_CURRENT_STATE` l.27–29, l.275).
- S5 has n = 3 with one anomalous film.
- Without P-data, the paper can claim "calibrated, with retrospective LOO" only, never "predictive".

---

## C. Off-current floor: alternatives and data

### D11 — SHOULD-FIX (0 launches). H-A and the extrinsic explanations are absent from the plan.

**What the plan leaves out.**
- The plan never cites H-A (register l.114–119) or the design's asymmetric rule (§7.2): the 2.0 nm floor "may be instrument-limited", so an underprediction there does not falsify.
- The state file says that floor "is at the level of the measurement setup" (`01` l.215).
- The 2.0 nm floor is 4.61e-15 A/µm × 290 µm = 1.34e-12 A in total (CALCULATED).

**Alternatives to list.**
- **Displacement current.** C_ox·A_ov·dV/dt = 8.95537e-7 F/cm² × 5.8e-6 cm² × (0.01–1 V/s, ASSUMED sweep rate) = 1.8e-16 to 1.8e-14 A/µm. That is −1.41 to +0.59 dec against the floor, and flat in V_G (CALCULATED).
- **Setup leakage.**
- **Pad-area oxide leakage under a global gate** (D12).
- **Ambient or photo conduction.** The back channel is air-exposed (generator stack comment).
- **A single-device outlier.**

**The scaling is not one power law.** It is t^3.05 for 2.0 → 6.3 nm and t^5.09 for 6.3 → 13.2 nm (CALCULATED from MEASURED floors). "t^3.851" is a two-point summary anchored on the possibly instrument-limited 2.0 nm floor.

**Fix.**
1. Add an H-A row to §1.4.
2. Carry the asymmetric rule into §1.3, §2.5, §7.5 and P1.
3. Extend Z10 to ask for: sweep rate, delay and integration time; SMU model and range; gate patterning and pad size; ambient and light.

### D12 — SHOULD-FIX (before any T1/T2 magnitude claim). The I_G area normalisation is ASSUMED.

- The gate spans the whole simulated width, including the 2 µm overlaps, which are ASSUMED and not reported.
- A global TiN gate under a 100 × 100 µm² pad (ASSUMED) would add log₁₀(1e4/580) = +1.24 dec of gate–drain leakage (CALCULATED).
- That exceeds the 0.5 dec windows in §1.3 and §7.5.

### D13 — REPORT. Data limitations.

- One device per film (register l.33). No reverse sweep, no I_G, V_D = 0.7 V only (`01` l.77). T is not recorded.
- The acceptance limits are not confidence intervals.
- The 6.3 nm on-current anomaly (I_on ×0.79 against 2.0 nm; design §1 item 5) may be device variation rather than a model failure. State this beside every "fails at 6.3 nm".
- μ_FE at V_D = 0.7 V is not deep-linear.
- Strip and diffusion (×7 against ×1.02) are not distinguishable with these data.

### D14 — REPORT. Physics omitted.

- **Charge centroid.** The model places the charge classically. A 1 nm centroid (ASSUMED, about t/2) gives C_eff/C_ox = 0.902 at 2.0 nm (CALCULATED: C_dark = ε₀·9.3/1 nm = 8.23e-6 F/cm²). It depends on V_G, so the shift and scale profiling cannot absorb it. Only BQP probes it, and BQP is third in the cut order.
- **DFT boundary conditions.** The DFT slabs have vacuum and H/OH surfaces; the device has Al2O3 below and air above. A finite barrier lowers ΔE_c. Check that the box-MODEL low end (0.2344 eV at 2.0 nm, `05` l.110) covers this.
- **Kane α.** PBE overestimates it (DFT_TO_TCAD l.127), so Δm* is biased high.
- **Amorphous transfer.** Crystalline-to-amorphous transfer (H-K) is out of scope. Write "DFT-informed", never "DFT-predicted".
- **Temperature.** T = 300 K is ASSUMED. P3 needs `nc.f` (l.3826–3829).
