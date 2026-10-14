The paper's mobility numbers turn out to be a difference of definition, not of data. Its SS numbers come from the very bottom of the subthreshold curve, but I could not pin down the exact SS method. No commit, push, ATLAS launch, CERN contact or network use.

**Mobility.** The paper's μ_max appears to be the peak of the saturation-formula mobility, μ_sat = 2L/(W·C_ox)·(d√I_D/dV_G)², applied to our same V_D = 0.7 V curves. With our fixed protocol C_ox (8.955e-7 F/cm²) and no adjustable factor:

| | 2.0 nm | 6.3 nm | 13.2 nm |
|---|---|---|---|
| μ_sat peak, ours (cm²/Vs) | 5.09 | 3.86 | 27.40 |
| Paper μ_max (cm²/Vs) | 5.1 (text) | 3.73 (digitised from its Fig. 1b) | 27.4 (text) |

- Our earlier g_m-based values (12.1 / 10.9 / 50.2) cannot be brought into line by any single C_ox or V_D, because the paper/ours ratio differs by film (0.42 / 0.34 / 0.55).
- At its peak, the saturation formula is outside its validity range at 6.3 nm at least. It also falls with V_G by construction, which may explain why the paper's mobility falls with V_G (its Fig. 5d).

**SS.** The paper's own Fig. 1b gives SS = 62 / 87 / 119 mV/dec, so "60–70 mV/dec" holds only at 2 nm. Steep-slope estimates taken just above the off-state floor (from 1 to 12 times the floor current) reproduce these within 5–15 %. Our registered windows sit 3–4 decades higher and give up to 168 % more.

**Which values are right.** For these V_D = 0.7 V curves I would report the g_m-based mobility, with its overdrive dependence from the protocol's power-law fit. SS should always be quoted with its current window, because the near-floor and normalised-window values describe different parts of the curve.

- **What I did:** re-extracted mobility (6 definitions, 6 C_ox variants) and SS (31 method variants, plus a noise Monte Carlo) from the raw workbook using the protocol's `extraction.py`, and digitised the paper's Fig. 1b. I wrote handoff HO-002 and updated the claims ledger (C024/C025 history; new claims C030–C033), the task queue (RQ-001 → IN_REVIEW) and `01_CURRENT_STATE.md` §H.
- **Main result:** the paper's μ_max equals the saturation-formula peak on our curves to within 0.3 % (2.0, 13.2 nm) and 3.4 % (6.3 nm). Its SS is a near-floor steepest slope.
- **Main uncertainty:**
  - Which formulas the paper used is inferred, not confirmed.
  - The best SS match is the best of 31 variants, so it flatters the agreement.
  - Some near-floor estimates fall below the 59.5 mV/dec thermal limit.
  - There is one device per film, and the C_ox uncertainty is not included.
- **Open problems:**
  - Six questions only the fab can answer: mobility formula, C_ox and W/L, SS method, whether the paper's devices are ours, sweep settings and V_D, and the current normalisation. They are listed in `claude/evidence/RQ-001/README.md` for the fab meeting (HUM-001).
  - Codex's review is pending.
  - C024 and C025 stay UNRESOLVED.
- **Files created:**
  - In `claude/evidence/RQ-001/`:
    - scripts and notes: `README.md`, `rq001_reconcile.py`, `digitise_fig1b.py`;
    - tables: `paper_fig1b_digitised.csv`, `mobility_definitions.csv`, `mobility_scale_test.csv`, `ss_methods.csv`, `ss_method_scoring.csv`, `ss_sliding_window.csv`, `ss_noise_mc.csv`, `rq001_results.json`;
    - figures: `figures/fig1_mobility_definitions.png`, `figures/fig2_ss_sliding_window.png`, `figures/fig3_local_ss.png`.
  - Edited: `handoffs/CLAUDE_TO_CODEX.md`, `03_CLAIMS_LEDGER.yaml`, `04_TASK_QUEUE.yaml`, `01_CURRENT_STATE.md`.
