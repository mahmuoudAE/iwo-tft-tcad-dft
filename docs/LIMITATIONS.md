# Limitations (V1)

Stated plainly, in decreasing order of importance for interpreting the results.

1. **No target-IWO DFT.** All confinement laws (dEg_QC, dEc, m*(t)) are pure-In2O3 PBE proxies (Lin 2022, Si 2021) transferred to ~2 % W:In2O3. W raises m* and flattens the CBM (Januar 2026, qualitative), so the true IWO confinement shifts are probably somewhat smaller. Quantum ESPRESSO is not installed on this machine (and cannot be installed without an interactive sudo password); the workflow is prepared in `qe_workflow/` but unexecuted. Uncertainty on dEg_QC(2 nm) is taken as +/-50 % (0.18-0.53 eV).

2. **Absolute band alignment is not measured.** Eg_bulk 3.05 eV and chi_bulk 4.30 eV are priors from a different IWO study; the gate work function (4.70 eV) is assumed; Qf is a fitted effective electrostatic correction. Only thickness DIFFERENCES of chi are used as physics; the absolute flat-band position remains a fitted quantity. A Kelvin-probe/UPS measurement of the IWO film and of the TiN gate, or C-V of each thickness, would remove this degeneracy.

3. **Composition of "2 % W" is undefined** in the source (atomic, cation or mol% WO3, target vs film). xW enters only as the material identity; no W-concentration law is used and the effective donor density is NOT derived from it.

4. **Off-state floors are not modelled.** The measured plateaus (5e-15, 1.5e-13, 6.6e-12 A/um for 2, 6.3, 13.2 nm) cannot come from thermal generation in this stack (bound 13-17 decades lower); their origin (gate leakage through the 17 nm high-k stack, contact injection, surface conduction, instrument) is NOT DETERMINED FROM AVAILABLE DATA (no IG/IS, no instrument-floor record). Native ATLAS zeros are reported as such; low-current metrics are excluded from the active-region scores and Ioff comparisons are flagged.

5. **Mobility.** The gate-bias roll-off of the paper (mu0/(1 + theta_r Vov)) is not natively insertable: ATLAS 5.28.1.R ignores MOBILITY updates between SOLVE statements, and the installed field-dependent surface models (CVT/Lombardi/PRPMOB) are silicon roughness models with no IWO calibration. V1 uses a constant band mobility per thickness times the roughness factor (1 - Dsr/t)^2; the gate dependence of the effective mobility comes only from the DOS free/trapped partition. The 6.3 -> 13.2 nm step in mu_band (~12 -> ~57 cm^2/Vs) has no defensible law and is a fitted, per-thickness quantity.

6. **6.3 nm device (validation miss).** Its measured threshold coincides with the 2 nm device's (0.64 vs 0.66 V at 1e-9 A/um) although the confinement law predicts it ~0.29 V lower; both Astra and Claude V0 needed device-specific parameters for it as well. The shared model run (run_0014) reproduces the subthreshold shape (SS_min 108 vs 115 mV/dec) but misses Vth by -0.29 V and Ion by +27 % (overdrive); one device-specific flat-band offset plus its own band mobility (run_0015, 0.063 dec) removes the miss. The offset is reported as device-specific, not absorbed into the laws.

7. **31.8 nm device: excluded from the final set** (user directive). It is outside the paper's 2-13 nm series and always-on. Laws + shared Qf + series resistance (run_0006) give Ion within 6 % but the bulk depletes below Vg = -1 V while the measured current stays flat at 2.7e-7 A/um; the back-surface donor-sheet hypothesis run (run_0010) aborted in SOLVE INIT without error text and was not investigated. The V0 evidence (back sheet + Rs, 0.09 dec) remains a hypothesis whose parameters are not separately identifiable.

15. **Sensitivity and convergence launches (executed 2026-09-22, runs 0016-0029).** The no-confinement counterfactual was run at both calibrated thicknesses: removing dEg and the m* increment shifts Vth by -0.316 V at 2 nm but only -0.023 V at 13.2 nm, so without the confinement law the two films would need fixed charges differing by 1.6e12 cm^-2; the shared-Qf result depends on the law. Eight one-at-a-time cases at 2 nm are in tables/SENSITIVITY_RESULTS.md: Vth is set by chi (0.1 eV = 0.10 V) and weakly by Nt (x1.5 -> +0.08 V); SS by WTA (+5 meV -> +12 mV/dec) and Dit (x3 -> +9 mV/dec); Ion by Nt (x1.5 -> -25 %) and chi through the overdrive (+/-7 %); Nd x2, eps 10.55 and a 4 um overlap change nothing beyond 2 %. Not run: gate work function (degenerate with Qf), m* alone, and any case at 6.3 nm. The DOS-level check (96/48 -> 192/96) changes Ion by +2.0 % (max 0.0125 dec), above the 1 % criterion; a 384/192 run was added to establish the direction (docs/NUMERICAL_CONVERGENCE.md).

8. **Interface Dit** is an assumed shared value (3e11 cm^-2 eV^-1 Gaussian) constrained only by literature proxies for HfO2/In2O3; the IWO/Al2O3 interface of the target stack has no direct measurement. C-V/conductance on the target stack would fix it.

9. **Quasi-2D DOS at 2 nm.** Nc(t) is a 3-D continuum value with a confinement-corrected m*; sub-band quantization of the in-plane DOS is not represented (Approach A). A Schrodinger-Poisson charge check (Astra's hard-wall diagnostic) exists only as a sensitivity, not a calibration.

10. **Calibration, not validation.** One ID-VG curve per thickness at one VD and one temperature is fitted. No independent condition (ID-VD, other VD, temperature, C-V, held-out device) is available in the supplied data, so the model is calibrated, not predictive. The cross-thickness structure (shared Eg/chi/m* laws, shared WTA, Nt(t) and Nd(t) laws, one Qf) is the only form of partial validation: a parameter set fitted on 2 and 13.2 nm is applied to 6.3 nm (docs/EXPERIMENTAL_VS_SIMULATION.md).

11. **Contacts** are ideal Ohmic (underconstrained: no TLM); the 2 um overlap is a numerical assumption (long-channel device, insensitive); the 31.8 nm series resistance is fitted.

12. **Capture cross sections, SRH lifetimes, Nv, deep-Gaussian amplitude** are assumed and not identifiable from DC transfer curves; the transfer curves are insensitive to them within the tested ranges.

13. **Numerics.** 32-bit ATLAS limits meshes to ~30k nodes; the 31.8 nm mesh was not refined; DOS-level doubling changes Ion by 1.1 % (at the criterion). See docs/NUMERICAL_CONVERGENCE.md.

14. **Data provenance.** Current units (A/um), VD = 0.7 V and the geometry come from the schematic, not from workbook headers; sweep direction, dwell and temperature are unrecorded.
