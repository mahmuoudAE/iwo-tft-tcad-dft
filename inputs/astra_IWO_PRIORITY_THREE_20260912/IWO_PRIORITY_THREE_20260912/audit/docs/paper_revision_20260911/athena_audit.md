# ATHENA process representation audit

Prepared 2026-09-11 from the relevant installed Silvaco manual and parser grammar. This audit made no simulator launch and did not read or modify license files, services, or installation configuration. Runtime verification belongs to the parent task's fresh run records.

## Installed software and evidence

- Launcher: `C:\sedatools\exe\athena.exe`.
- Implementation: `C:\sedatools\lib\athena\5.22.3.R\x86-nt\athena.exe` (5,124,096 bytes).
- Version directory: `5.22.3.R`; this alone does not prove that version was executed or licensed.
- Primary reference: `C:\sedatools\lib\athena\5.22.3.R\docs\athena_users1.pdf`.
- Parser cross-check: `C:\sedatools\lib\athena\5.22.3.R\common\athenakey`.

Only summaries and brief syntax references are provided here. No vendor manual or substantial excerpts are included in the delivery.

## What can be represented defensibly

Ordinary `DEPOSIT MATERIAL=<name> THICK=<micrometres> DIVISIONS=<count>` makes a conformal layer with the requested thickness. On a planar stack, this is a useful way to reconstruct the measured final geometry. It is not a simulation of plasma chemistry, incident DC power, reactive oxygen incorporation, or W/In/O stoichiometry. See manual printed pages 303-305 (PDF pages 307-309).

Elite's `RATE.DEPO` offers geometric incident-flux models including unidirectional, hemispheric, and Monte Carlo deposition. The hemispheric model is described in the context of planar sputtering, but it requires deposition rates and incident-angle/surface-diffusion inputs. No calibrated mapping from the supplied DC-sputtering process conditions to IWO composition, vacancy densities, or electronic Gaussian DOS was found in the audited installed references. See printed page 241 (PDF page 245) and printed pages 376-377 (PDF pages 380-381).

Therefore the supplied ATHENA deck uses thickness-driven conformal deposition and geometrical contact opening. It does not invent a deposition rate or claim a predictive DC-sputtering process. A later calibrated Elite model would require experimentally measured thickness versus time, flux direction distribution, sticking/surface diffusion parameters, and independent chemistry/defect calibration. Those quantities cannot be uniquely extracted from four DC transfer curves.

## Material syntax and name limitations

Arbitrary user-defined names are supported with `MATERIAL=<name>`. Several names not present among the simple built-in ATHENA keywords are recognized as standard materials when saved, including `HfO2`, `Al2O3`, `Palladium`, `Conductor`, `In2O3`, `IGZO`, and `Air`. See printed pages 288-289 (PDF pages 292-293).

The IWO layer is deposited using `material=IWO`. This specifies the geometry label; it does not supply IWO transport, band structure, DOS, trap capture, or sputtering models. Those must be assigned and verified in ATLAS.

`Tin` denotes elemental tin, not titanium nitride. Using `TiN` risks the same case-insensitive name match. `TiN_gate` is an unambiguous custom geometry name, but the documented ATHENA `ELECTRODE` command only recognizes specific metal/polysilicon material identities. An arbitrary `TiN_gate` is not in that list. The runnable deck therefore uses `material=Conductor`, explicitly documented as an ideal electrical/geometrical surrogate for the 50 nm TiN layer. Gate work function must be set in ATLAS; it cannot be inferred from the generic material label. See printed page 312 (PDF page 316).

Palladium is a recognized electrode material. Naming a Pd electrode does not establish its IWO Schottky barrier, contact resistivity, or interface chemistry. These remain electrical-model assumptions/parameters.

## Defects are not interchangeable across ATHENA and ATLAS

ATHENA `VACANCY` and `INTERSTITIAL` commands describe process defect diffusion/generation/recombination. The manual explicitly limits calibrated default data to silicon and some silicon interfaces. These cannot be reused as calibrated oxygen-vacancy transport data for IWO. See printed pages 342-343 (PDF pages 346-347).

ATHENA `TRAP` describes interstitial trapping in a process model, with defaults for silicon. It does not define the ATLAS electron/hole Gaussian energy distributions requested for this transistor. See printed page 403 (PDF page 407).

Similarly, `C.VACANCY` on `DEPOSIT` inserts a prescribed process vacancy concentration; it does not calculate an IWO oxygen-related energy spectrum or supply validated charge-state transitions. No such field is assigned in the delivered process deck. Gaussian/tail bulk and interface DOS should be assigned separately in ATLAS with the documented energy reference, units, capture cross sections, and donor/acceptor charge conventions, then calibrated against independent evidence where available.

## Geometry provided

Executable candidate: `decks_paper_revision/athena/iwo_2p0nm_process.in`.

The initialized support is an assumed 200 nm displayed silicon slice with assumed phosphorus concentration `1e19 cm^-3`. Original wafer thickness and doping are not inferred from the schematic. The source/drain overlap is assumed 2 micrometres per side; inner edges are separated by the specified 20 micrometre channel length. Physical width is 290 micrometres, to be represented consistently during subsequent ATLAS normalization; ATHENA's 2-D geometry has no independent finite physical width.

Coordinates are referenced to the initial Si surface at y=0 and grow toward negative y:

| Layer | y bottom (um) | y top (um) | Thickness |
|---|---:|---:|---:|
| n+Si displayed slice | 0.2 | 0 | 200 nm assumed |
| TiN represented by Conductor | 0 | -0.050 | 50 nm |
| HfO2 | -0.050 | -0.065 | 15 nm |
| Al2O3 | -0.065 | -0.067 | 2 nm |
| IWO | -0.067 | -0.067 - t | t |
| Pd source/drain | -0.067 - t | -0.137 - t | 70 nm |

Use t = 0.002, 0.0063, 0.0132, or 0.0318 micrometres for the four measured channel thicknesses. The 2 nm file contains explicit resolved coordinates. A changed t also requires updating the contact opening and electrode y coordinates.

The Pd centre is removed geometrically over x=2..22 micrometres. This represents the final contact pattern. It does not claim a physical Pd etchant, lift-off kinetics, or process damage prediction. Geometrical polygon etching is documented on printed pages 315-316 (PDF pages 319-320).

For 2 nm IWO and Al2O3, `DIVISIONS=8 MIN.DY=0.00025` requests 0.25 nm vertical subdivisions. The ordinary minimum-spacing default is 1 nm, which is too coarse for this intended subdivision. An ATLAS solver mesh still needs an independent electrical convergence check; a small geometric spacing by itself is not proof of quantum or continuum-model validity.

## Current validation boundary

The parent task subsequently executed the 2 nm deck successfully in genuine local ATHENA. Evidence is in `results/local_session_20260910/runs/20260911T144631_108956_paper_athena_2nm/`. The fresh output identifies ATHENA **5.21.2 (aka 5.22.3.R)**, reports ATHENA/SSUPREM4/ELITE enabled, accepts all three electrode assignments, and writes both requested structures. This is stronger than the installation-directory evidence above. The template and executed input compare identically after newline normalization; their raw byte hashes differ only because of newline representation.

Fresh `iwo_2p0nm_athena_device.str` SHA256: `b5918afb887addc866a566f7c1355b3a63a7d9fef3dd99fdaf2d96f9008b97da`.

The exported structure carries the following region/material/electrode mapping, verified from its own records:

| Region | Material identity | Named electrode |
|---:|---|---|
| 1 | Silicon | none |
| 2 | Conductor (ideal TiN surrogate) | gate, electrode 1 |
| 3 | HfO2 | none |
| 4 | Al2O3 | none |
| 5 | custom IWO | none |
| 6 | Palladium | source, electrode 2 |
| 7 | Palladium | drain, electrode 3 |

The direct ATLAS import candidate is `mesh infile=iwo_2p0nm_athena_device.str width=1`, followed by the IWO donor profile on **region 5** and explicit custom-IWO electronic parameters using `material material=IWO user.group=semiconductor user.default=silicon ...`. The saved IWO name is present, so rectangular reconstruction or an IGZO relabel is not necessary merely to identify it. This is an import proposal, not a claim that import/electrical solution succeeded. ATLAS manual Appendix B.2.5, printed page 1668 (PDF page 1677), documents custom-material classification; the same installation has already executed custom-IWO direct ATLAS decks in the original task. The manual's older Appendix B.14 text contradicts that newer explicit syntax and should not override actual version-tested behavior.

Three additional thickness decks were generated without changing the 2 nm template. Files and hashes are in `decks_paper_revision/athena/thickness_variants.json`. Reproduce them using `scripts/generate_athena_thickness_variants.py`; this is generation only and does not launch the simulator. Their IWO thickness, Pd opening coordinates, contact-centre coordinates, and output names all change together. Vertical IWO subdivisions increase to 13, 27, and 64, respectively, for 6.3, 13.2, and 31.8 nm. These three variants remain **unrun** until their own fresh logs exist.

Successful ATHENA construction does not establish ATLAS import, sufficient mesh quality for a nonlinear electrical solve, current conservation, or a fitted transfer curve. Those checks remain separate and must use actual new simulator output.
