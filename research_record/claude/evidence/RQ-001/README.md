# RQ-001 evidence: mobility and SS reconciled with Januar et al. (2026)

Task: `04_TASK_QUEUE.yaml` RQ-001. Handoff: HO-002 in `handoffs/CLAUDE_TO_CODEX.md`.

## Reproduce

```
PY="..\IWO_ATLAS_Model_claude\.venv\Scripts\python.exe"
$PY claude/evidence/RQ-001/digitise_fig1b.py sources/Januar2026_SmallStructures.pdf      # -> paper_fig1b_digitised.csv
$PY claude/evidence/RQ-001/rq001_reconcile.py ..\IWO_PHYSICS_CONSTRAINED_MODEL_V1          # -> everything else
```

- **Inputs.**
  - Public repo at `f315b78`: `data/experimental_raw_preserved_IWO-TFT.xlsx`, rows 2–122. The script checks it against `data/experimental_clean.csv`; the two are identical, with a largest difference of 0.
  - The protocol code `analysis_2026-10-06_extraction/extraction.py`, imported and not copied.
  - The paper in `private:sources/`.
- **Run time.** About 50 s. Most of it is the 2000-draw noise Monte Carlo per film.
- **Determinism.** The outputs are deterministic (seed 1). Two runs gave identical CSV hashes.

## Files

| File | Content |
|---|---|
| `rq001_reconcile.py` | Re-extraction: six mobility definitions, six C_ox variants, 31 SS method variants, noise Monte Carlo, figures |
| `digitise_fig1b.py` | Pixel digitisation of the IWO markers in paper Fig. 1b (μ_max, SS, I_off) |
| `paper_fig1b_digitised.csv` | Digitised paper values, with ±1.5 px read uncertainty |
| `mobility_definitions.csv` | Peak, V_G of the peak, and value at 3 V, for each film and definition (protocol C_ox) |
| `mobility_scale_test.csv` | Ratio paper/ours per film. A constant-factor explanation (C_ox, V_D, W/L) needs the same ratio in every film. |
| `ss_methods.csv` | SS for each method, film and floor margin (`kfloor` = how many times the floor the lowest current used must be) |
| `ss_method_scoring.csv` | Every method that gives a value in all three films, ranked by its largest deviation from the digitised paper SS |
| `ss_sliding_window.csv` | One-decade SS against window position, raw and floor-corrected |
| `ss_noise_mc.csv` | Bias of the minimum-SS estimators on a smoothed curve plus measured-level noise |
| `rq001_results.json` | All of the above, plus the C_ox variants, Y-function fits, μ_sat derivative sensitivity and validity at the peak |
| `figures/` | Three figures (captions below) |

## Figure captions

**Fig. 1 (`fig1_mobility_definitions.png`).** Mobility against gate voltage for the measured IWO transfer curves at V_D = 0.7 V.
- **Panels.** (a) 2.0 nm, (b) 6.3 nm, (c) 13.2 nm.
- **Settings.** All curves use C_ox = 8.955e-7 F/cm² and W/L = 290/20.
- **Curves.**
  - Black: linear field-effect mobility L·g_m/(W·C_ox·V_D), protocol M1.
  - Red: saturation-formula mobility 2L/(W·C_ox)·(d√I_D/dV_G)².
  - Blue dashed: effective mobility L·I_D/[W·C_ox·(V_G − V_T − V_D/2)·V_D], with V_T = V_th,cc (I_D = 1e-9 A/µm).
  - Green dashed: the same with V_T = V_th,ELR.
  - Purple dotted: the same with V_T from the power-law fit of protocol M2.
  - Orange bar: Y-function low-field mobility μ0, drawn over its fit range.
  - Grey dash-dot: the paper's μ_max (text value at 2.0 and 13.2 nm; digitised from Fig. 1b at 6.3 nm).
- **Restrictions.** The effective mobilities are drawn only where V_G − V_T ≥ V_D.

**Fig. 2 (`fig2_ss_sliding_window.png`).** Two-point SS over a one-decade current window, against the window's lower edge divided by the off-state floor (median I_D over V_G = −2 to −0.5 V).
- **Panels.** (a) Raw current. (b) Current minus the floor, drawn only for windows starting at or above 1× floor.
- **Colours.** Black 2.0 nm, red 6.3 nm, blue 13.2 nm.
- **Error bars.** Protocol §3.4: noise at both crossings and the interpolation-method difference.
- **Reference lines.**
  - Dashed lines in film colours: the paper's SS digitised from Fig. 1b (61.8, 87.4 and 119.3 mV/dec).
  - Grey dotted: thermionic limit, 59.5 mV/dec at 300 K.

**Fig. 3 (`fig3_local_ss.png`).** Local SS = dV_G/dlog10 I_D (central differences on the 50 mV grid), against current.
- **Panels.** (a) Raw I_D. (b) I_D − floor, drawn only for points above the last V_G where I_D ≤ 2× floor.
- **Colours and lines.** As in Fig. 2.

## Questions only the fab can answer (for HUM-001)

1. **Mobility formula.** Which formula gave μ_max in Fig. 1b, Fig. 5a and SI Fig. S8? If it is the saturation formula, why was it applied to V_D = 0.7 V curves? Is the Fig. 5d mobility measured or modelled?
   - Please send the original extraction script or spreadsheet, not just the formula name. We will apply it unchanged to our workbook.
   - Please also send the data behind Fig. 5d. [added 2026-10-09, R-RQ-001]
2. **Capacitance and geometry.** Which C_ox (and from which C–V, SI Fig. S1) and which W/L were used? Is it the geometric 15 nm HfO2 + 2 nm Al2O3 stack (8.955e-7 F/cm²)?
3. **SS method.** How was SS in Fig. 1b, Fig. 4d and Fig. 6e obtained? Options:
   - the fitted parameter "SS" of Eq. 1e;
   - the minimum local slope;
   - a fixed or steepest window.

   Over how many points or decades, and with or without subtracting I_off?

   If a floor margin or I_off subtraction was used, was the margin applied to the total current or to the current after subtraction? Was a minimum taken over several windows? [added 2026-10-09, R-RQ-001]
4. **Same device?** Is the 2 nm device of Fig. 1b, Fig. 4d and Fig. 6e (SS 62 before stress) the same device and sweep as our 2 nm curve?
5. **Drain bias and sweep.**
   - Was every curve in Fig. 1 and Fig. 5 measured at V_D = 0.7 V?
   - Does an output curve or a second V_D exist? (SI Fig. S7b shows output curves for at least one device.)
   - What were the sweep direction, step, integration time and instrument range? This matters for SS at the pA level near the 2 nm floor.
6. **Current normalisation.** Were the workbook currents divided by W = 290 µm? The I_off axis of Fig. 1b is labelled "A", but its values match our per-µm floors.

## Change log

- **2026-10-09, R-RQ-001** (owner response to the Codex review; `claude/responses_to_codex/RQ-001_response.md`).
  - Question 1 now asks for the original script or spreadsheet and the Fig. 5d data (objections O1, O3).
  - Question 3 now asks how the floor margin and minimum selection were applied (O4, O7).
  - Scripts and outputs are unchanged.
