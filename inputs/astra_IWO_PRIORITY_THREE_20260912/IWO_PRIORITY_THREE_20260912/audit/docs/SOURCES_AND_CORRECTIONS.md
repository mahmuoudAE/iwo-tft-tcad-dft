# Sources and what was taken from each

## A. Primary target measurements

User attachment `IWO-TFT (1).xlsx`, Sheet1. Original numerical samples were read with `artifact_tool`, not OCR. CSVs preserve source rows. SHA256 and original columns are in `data/provenance.json`. The user-provided screenshot supplies dimensions, drain bias, thickness names and the A/um unit interpretation. No assumption is made that every chart in the paper uses precisely this device/bias dataset.

## B. Main2026 paper

M. Januar, Z.-F. Luo, K.-C. Liu and M.-H. Lee, “Unified Analytic Framework for Thickness-Dependent Transport and Trap-State Modulation in Ultrathin W:In2O3 Field-Effect Transistors,” Small Structures7, e202500807 (2026).

https://doi.org/10.1002/sstr.202500807

Used for the fabrication stack and process type (Section2.1), physical interpretation, analytical-model motivation, and qualitative thickness trends. It is an analytical/experimental paper, not a published complete ATLAS deck. It does not supply a complete verified set of band, contact and distributed-DOS parameters for our four ATLAS structures.

## C. Official Supporting Information — newly consulted for this package

https://onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1002/sstr.202500807&file=sstr70281-sup-0001-SuppData-S1.pdf

The14-page supplement was inspected through web text and rendered-page views. It is linked, not falsely supplied as a locally downloaded file.

FigureS1 reports relative permittivities HfO2=19.57+/-0.06, IWO=9.30+/-0.04, In2O3=9.03+/-0.08. Only the appropriate two measured values are used here; epsilon_Al2O3=9 remains a declared assumption.

The preliminary Python model follows the **supplementary** blended-current convention, not three problematic printed forms in the main paper:

1. SupplementS15 adds `Ileak`, not a second copy of the diffusion Ioff.
2. SupplementS16 has the generalized inverse-current blend without the extra leading `m` shown in main Equation1b. We fix m=1, making that particular factor immaterial numerically here.
3. SupplementS18 uses exponential scale S=SS/ln10, consistent with the conventional subthreshold-swing definition. This differs from the main-text printed denominator SS*ln10.

No silent correction is made: the implemented convention is specified in code. A close fit of this algebraic form is not equivalent to2-D TCAD solving the same microscopic mechanisms. The preliminary fit uses broader practical search bounds and does not claim to recover the authors' exact fitted parameters.

The source's effective roughness units remain internally ambiguous (main prose in angstroms versus plot axis in nm); our ATLAS defaults do not silently select one and then claim a universal roughness law. Likewise, model-derived Nt in the paper is not simply copied to ATLAS NTA: peak DOS units and integrated concentration are not interchangeable.

## D. Separate IWO TCAD research — only prior estimates

W.-T. Fan et al., “Numerical Analysis of Oxygen-Related Defects in Amorphous In-W-O Nanosheet Thin-Film Transistor,” Nanomaterials11,3070 (2021).

https://doi.org/10.3390/nano11113070

Section3 gives Eg_IWO=3.05eV and estimates affinity=4.30eV for its own sample. We use those as explicitly labelled **starting priors**, not as measurements on the2026 sample. Its different metal contacts, thickness, donor concentrations, gate structure, and fitted defect distributions are NOT transplanted into this calibration.

## E. Vendor method reference

Silvaco, “ATLAS Device Simulation of Amorphous Oxide Semiconductor Thin-Film Transistors.”

https://silvaco.com/simulation-standard/atlas-device-simulation-of-amorphous-oxide-semiconductor-thin-film-transistors/

This primary vendor note supports the basic approach of2-D ATLAS drift-diffusion with oxide-semiconductor DOS and material calibration. It does not establish our IWO parameters or validate generated syntax against the user's unknown installed version.

General tool-scope references:
https://silvaco.com/tcad/
https://silvaco.com/tcad/victory-device-3d/
https://silvaco.com/tcad/victory-process-3d/

The supplied files target ATLAS/DeckBuild, not an asserted completed migration to Victory. Relevant command patterns are also consistent with the user's previously reviewed TFT example archive, especially direct construction, per-width scaling and region-specific DEFECTS. That archive's numerical IGZO/a-Si values are not treated as IWO measurements.

## Evidence labels used throughout the package

- **Measured input**: original workbook numerical pairs.
- **Paper/supplement value**: explicitly source-labelled structural/dielectric quantity.
- **Other-study prior**: starting estimate from a different IWO device.
- **Assumed seed**: not measured and not calibrated in ATLAS.
- **Preliminary fit**: executed Python algebraic optimization, NOT TCAD.
- **Generated deck**: authored ATLAS instructions, not proof of solver success.
- **Local ATLAS result**: reserved for future outputs created by successful real simulator execution on the user's computer.
