**Task: blind review of the frozen hypothesis register and the first simulation results.**

Attached:
- the frozen hypothesis register (revision 2, frozen 2026-10-10T18:33Z, plus post-freeze amendments A17 and A18);
- the campaign design for the ATLAS runs;
- the DFT-to-TCAD input mapping;
- the raw results of the first ATLAS stages (S0 smoke tests, S1 baselines) as JSON;
- the measured transfer-curve data (clean CSV and data summary).

Please answer, in the reply format of your role:
1. Which registered predictions are **weak**? That is, predictions that are trivially satisfied, unfalsifiable in practice, or whose pass band is wider than the effect they claim to test. Give the hypothesis ID and the line.
2. Which **alternative mechanisms** for the three central observations are missing, and which existing or planned run would discriminate each from the favoured one? The three observations are:
   - the off-current floor at 2.0 nm (about 4.6e-15 A/µm) and how it scales with thickness;
   - the threshold-voltage shift with thickness;
   - the mobility drop with thinning.
3. Are there **errors**? Check the definitions (host edge, localisation PR_n, excess-electron accounting, the censoring rule), the arithmetic (bands, launch counts), the units and the signs (e.g. ΔV_th = +Δ(ΔE_c) = −Δχ).
4. In S1, the 3-D density-of-states run (S1-05) shifted V_th,cc by +142 mV against a registered +40 to +70 mV. The register attributes this to trapped charge in the acceptor tail amplifying a 37.5 meV statistics shift. **From the numbers alone**, is that plausible? What else could produce it?
5. The DFT part uses neutral, spin-unpolarised PBE slabs (0.7–2.0 nm, amorphous, ML-generated structures, OH-terminated, about 2 % W). Which DFT conclusions in the register **cannot** be supported by such cells, whatever the outcome?

Constraints: no new measurements; CERN compute until 21 Oct; 186 ATLAS launches left.
