# ALD IWO paper: evidence and limits for the sputtered-device model

Source: Chanyoung Yoo et al., *Atomic Layer Deposition of WO3-Doped In2O3 for Reliable and Scalable BEOL-Compatible Transistors*, Nano Letters **24** (2024), 5737-5745. DOI: [10.1021/acs.nanolett.4c00746](https://doi.org/10.1021/acs.nanolett.4c00746). User-supplied PDF has nine pages; PDF page 1 is journal page 5737. The complete text was read, and PDF pages 2, 4, 5, 6, and 7 were rendered and visually checked. Supporting Information was referenced by the article but was not part of this supplied PDF and was not inspected.

## Process and physical device

| Quantity | Reported value and location |
|---|---|
| Channel process | Remote O2-plasma ALD at 225 C; cyclopentadienyl-indium (CpIn) and bis(t-butylimido)-bis(dimethylamido)-tungsten precursors. PDF p. 2 / journal p. 5738. |
| Growth on native-oxide Si | In2O3 0.58 angstrom/cycle; WO3 0.49 angstrom/cycle. WO3 initially grows more than five times more slowly on In2O3 for fewer than 20 cycles; after 30 cycles its rate approaches 0.48 angstrom/cycle. These are ALD surface-chemistry results, not sputtering rates. PDF p. 2. |
| Composition control | In2O3:WO3 cycle ratios 20:1, 10:1, 5:1 give approximately 1, 2, 4 atomic percent W; corresponding WO3 mole fractions reported as 5, 10, 20 percent. Atomic percent W is not automatically the W/(In+W) cation percentage. PDF pp. 2-3. |
| Substrate and gate | P-type Si with 70 nm thermal SiO2, patterned 40 nm sputtered Ni gate. PDF p. 7 / journal p. 5743. |
| Gate dielectric | Nominal 5 nm remote-plasma ALD HfO2 at 250 C, TDMAHf and O2 plasma. The bias-field calculation uses measured 4.8 nm. PDF pp. 5, 7. |
| Channel | 3 nm ALD IWO; largely amorphous by TEM and broad XRD peak; ordering decreases with W addition. PDF p. 4. |
| Source/drain | 40 nm Ni; described as Ohmic contacts. Channel isolated with 2 percent HCl. No postfabrication anneal. PDF pp. 4, 7. |
| Main device dimensions | W = 10 micrometres, L = 1.5 micrometres. Additional L = 110 and 60 nm devices. PDF pp. 4, 6-7. |
| Measurement conditions | Dark, flowing N2, room temperature, HP 4156C and Keithley 4200-SCS. PDF p. 7. |

## Defect evidence

1. XPS indicates undoped ALD In2O3 has approximately In:O = 2:2.5; just over 1 atomic percent W changes the inferred indium-oxide stoichiometry to approximately 2:3, retained up to 4 atomic percent W. A 2 atomic percent film is reported as 36.5 percent In, 2.1 percent W, and 61.5 percent O. The authors explicitly account for WO3 when interpreting oxygen content. PDF p. 4.
2. The paper does **not** establish that stronger W-O bonds alone cause this change. It argues that the low W population is insufficient for a simple local chemical explanation and proposes Fermi-energy control of oxygen-vacancy formation during growth as a hypothesis requiring further investigation. PDF p. 4.
3. Pre-existing interface and channel traps are discussed as causes of bias-induced threshold shifts. Remote-plasma ALD avoids energetic surface bombardment, whereas sputtering can generate growth defects. The authors identify this as a process-dependent distinction, not a quantitative law converting sputtering power or oxygen flow into trap concentration. PDF pp. 5-7.
4. At 4 atomic percent W, modest instability is tentatively associated with defects from insoluble W atoms; this attribution is speculative. PDF p. 6.
5. No ATLAS-ready values are provided for Gaussian trap peak density, energy center, width, exponential-tail energy, capture cross section, volumetric donor concentration, electron affinity, bandgap, permittivity, or effective mass. No mathematical sputtering-to-DOS model is supplied. XPS stoichiometry is not a measurement of electrically active trap density or charge-state occupancy.

## Electrical numbers: process-specific comparison, not target parameters

- Extracted field-effect mobilities are 76, 41, 12, and 3 cm2/(V s) for 0, 1, 2, and 4 atomic percent W. These are device-extracted mobilities, not independently measured low-field ATLAS material mobilities. PDF p. 4.
- The 2 atomic percent device gives approximately 70 microampere/micrometre at VD = 1 V and VG = 2 V. Minimum reported subthreshold swing is 67 mV/decade, with negligible sweep hysteresis. PDF p. 4.
- Bias stress is VG = +/-2 V, approximately +/-4.2 MV/cm across 4.8 nm HfO2, for 10, 100, and 1000 seconds. Temperature-stress measurements are at 80 C. The 2 atomic percent device exhibits +0.07 V PBS and -0.03 V NBS shifts; 1 and 2 atomic percent devices show small changes after 1000 seconds. PDF pp. 5-6.
- Neither these threshold shifts nor the subthreshold slope uniquely separate interface DOS, bulk DOS, dielectric trapping, free-carrier electrostatics, and contact effects. Do not invert them into a claimed unique Gaussian population.

## Use in the present DC-sputtered model

Use this paper as evidence that W concentration, oxygen stoichiometry, and deposition damage influence carrier supply and traps. It motivates separating oxygen-related donor states, disorder tails, and interface states, with explicit uncertainty and sensitivity checks.

Do not replace the user's Pd/TiN/Al2O3-HfO2 stack with this paper's Ni/HfO2 stack. Do not import its ALD growth rates, mobilities, trap-free behavior, or bias-stability metrics as properties of the 2026 sputtered films. It provides no basis to claim that an ATHENA deposition command predicts actual DC-sputtering chemistry or a complete trap spectrum. Adding every imaginable defect would introduce unsupported, non-identifiable parameters; additional populations require evidence and a measurable improvement beyond numerical error.

Review performed 2026-09-11. Only the supplied source was read; it was not modified. No simulator launch or shared model-code edit was made by this review.
