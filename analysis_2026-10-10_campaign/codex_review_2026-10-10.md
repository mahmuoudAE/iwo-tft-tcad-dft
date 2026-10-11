1. **Exact profiling — FIX.**

   **(a) QF shift:** The charge is correctly placed at **IWO/Al₂O₃, y=0**. However, full-width QF and gate coverage do **not** make the transformation mathematically exact. Changing gate voltage while holding the semiconductor solution fixed would require an oxide-potential perturbation with zero potential and uniform normal displacement at the channel interface. In this 2-D deck, lateral variations, pinned S/D potentials, and contact-edge fields generally prevent that construction. Pd volumes and air preserve these boundary effects. Treat the shift as an **empirically accurate approximation**, with an error bound over the proposed QF range and all three films.

   **(b) MUN scaling:** Exact for source-free, steady, electron-only DD with ideal Ohmic contacts, when every electron mobility is multiplied by the same constant. This includes μ=MUN·f(n): dividing the homogeneous continuity equation by MUN leaves the same solution. **Continuous DEFECTS alone do not make occupancy mobility-dependent**; occupancy depends on local carriers and capture/emission rates.

   But nonzero SRH/DEFECTS generation–recombination breaks that symmetry: ∇·J=qR does not scale uniformly. Electron-only operation does not itself prove R=0. Gate injection, contact tunnelling/thermionic injection, finite resistance, and two-carrier coupling also break it. Call scaling approximate unless the installed formulation suppresses those sources identically.

   Move native transformation checks **before S3 selection/S4**, including IGZO. Earlier evidence is limited: [T2 results](/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff%20(1)/IWO_PHYSICS_CONSTRAINED_MODEL_V1/analysis_2026-10-06_V2/T2_T3_RESULTS.md) record a **2 nm FAIL** against the registered RMSE tolerance.

2. **Model choices/disagreements — mostly OK; FIX specific claims.**

   - D1 is correct. Constant shared donors, Fermi statistics, silicon mobility exclusions, BBT exclusion, and testing IGZO activation are reasonable.
   - **D14:** NC substitution is a calibrated DOS approximation, not actual quasi-2D Fermi statistics. A single subband requires checking **E_F−E₁ as well as kT** against E₂−E₁. The acknowledged on-state DOS error deserves a model sensitivity, not only an override audit.
   - **D4:** “Schottky is on-state only” is too categorical. Reverse injection, barrier lowering, and tunnelling can affect off-state current if a collection path exists. This does not establish a flat-floor mechanism, but excludes calling the branch exclusively on-state.
   - **BQP comparison:** S0 versus BQP changes affinity, gap, mass, DOS and mobility together. Use the matching **no-confinement/no-BQP deck** to isolate BQP’s incremental effect.
   - **FLDMOB OFF:** Reasonable, but 350 V/cm is the average field; watch local contact-edge fields.
   - D11’s common mass convention is bookkeeping, not physical equivalence: in-plane DOS mass and perpendicular tunnelling mass need not match.
   - Retaining assumed deep/interface traps is defensible with sensitivity checks. Removing both together cannot identify which matters.

3. **Labels/validation — FIX.**

   Most labels correctly distinguish DFT calculations, extrapolations and device fitting. However:

   - Label quasi-2D NC and the mass factor **CALCULATED from hybrid LITERATURE + DFT-law inputs**, rather than “from COMPUTED m*.”
   - Numerical FN/SRH/WKB estimates are **CALCULATED conditional bounds**, not direct COMPUTED DFT evidence.
   - The Gaussian-sheet **peak** is 3e11 cm⁻²eV⁻¹; it is not an integrated trap count.
   - Selected tail placement, contact barrier and mobility branch are data-selected model choices and must be reported accordingly.
   - S5 inherits branches selected using **all three films**. Sharing a data-independent S4a grid is legitimate; sharing full-data branch selection contaminates held-out evaluation. Select branches within each fold, or label S5 **conditional LOO after full-data model selection**.
   - Do not inherit `run_extraction.py`’s old “not fitted” status labels for quantities now constrained by whole-curve fitting.

4. **Arithmetic — OK.**

   Independently obtained:

   - μ∞=**100.005323**, ℓ=**7.248408 nm**.
   - MUN=**12.977027 / 40.260652 / 60.538766** cm²/Vs.
   - NC₂nm=**1.373063e19 cm⁻³**, under the stated formula.
   - FN nominal: **3.500e−6 A/V²**, **9.967121e7 V/cm**.
   - FN worst: **1.026667e−5 A/V²**, **3.967871e7 V/cm**.
   - Counts: **2+6+15+26+45+18+3+3+30+27+2=177**; reserve **23**.

   These starts pass through the stated YAML anchors, which differ slightly from the final anchor rescalings reported in T2.

5. **Gate leakage — FIX / RISK.**

   The verdict is quantitative, but improve fairness:

   - Use **2×|measured slope|**.
   - Require sufficient valid points and report sign reversals; positive-only selection must not manufacture a passing median.
   - Score both total I_D and **mechanism-induced ΔI_D** against a matched control. Total-current agreement alone does not establish attribution.
   - Define `drain_share` pointwise and suppress it when I_G is unresolved.
   - Remove the rule that floor-scale current automatically contradicts the bounds: the worst-case set explicitly permits floor-scale leakage.
   - Treat 2 nm as potentially setup/transient limited; underprediction there need not falsify a physical floor mechanism.

   The worst set is a sensible **optimistic scenario**, not a rigorous upper bound covering defects, thinning or pinholes.

   **Conductor gate:** The local manual supports electrode/contact injection for QTNLSC and electrode–insulator coupling for FNORD; a Conductor gate is not inherently excluded. Actual injection remains unverified here. Confirm path selection and nonzero signed terminal transfer with a resolvable diagnostic. **FNORD uses the semiconductor-interface field**, so HfO₂ gate-barrier constants applied at the Al₂O₃/IWO interface are an approximate, potentially inflated bilayer estimate.

6. **10-run minimum — FIX.**

   Replace **S3-02 no confinement**, whose dominant shift/scale effects are subsequently profiled away, with an early **native QF/MUN transformation check**.

   After verifying tunnelling activation at 2 nm, consider replacing **S2-08** with **2 nm 3-D NC sensitivity**: it addresses a new primary-model approximation. Keep the 13.2 nm leakage run if thickness-dependent collection is a priority.

7. **Launch waste / interpretability — FIX.**

   - S4a candidate 1 repeats existing baselines when no branch changes; reuse those curves.
   - Schottky adoption invalidates offline mobility scaling, yet S4 still budgets only DOS launches. Allocate native QF/mobility fitting or exclude Schottky from that fitting workflow.
   - The strip includes shared QF, whereas the earlier successful variant **D excluded QF**; variant Q predicted very different scaling. Add an explicit QF-off strip control.
   - `analyse()` assumes crossings and successful power-law fits; failed/off-only branches need guarded extraction and invalidity flags.
   - S6 changes C_ox, but registered extraction hardcodes it. Report registered-normalisation μ_FE separately from mobility calculated using each perturbed stack.
   - Profile interpolation needs an explicit no-extrapolation rule and adequate voltage coverage.