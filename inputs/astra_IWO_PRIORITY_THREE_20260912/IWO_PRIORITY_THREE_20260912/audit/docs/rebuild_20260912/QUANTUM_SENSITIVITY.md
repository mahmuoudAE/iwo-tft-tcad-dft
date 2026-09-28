# 2 nm electron-confinement sensitivity

Read-only audit, 2026-09-12. No quantum simulation, simulator launch, or generator modification was performed. This is an optional diagnostic design, not an enabled or calibrated model.

## Appropriate first option

The installed ATLAS 5.28.1.R supports electron Bohm quantum potential through `BQP.N`. It adds a density-gradient-dependent quantum potential to carrier potential energy and the current equations. It is a confinement correction to semiclassical transport, not an atomistic IWO calculation, a sputtering model, an extra trap species, or a direct tunneling model.

The native BQP model is a better first transport sensitivity than enabling the full Schrodinger solver or several quantum corrections at once. The manual recommends calibrating BQP charge control against Schrodinger-Poisson at negligible current. It does not support calling an arbitrary BQP coefficient a measured material parameter.

The basic documented command structure for the present three-terminal electrical model is:

```text
# Add to a separately copied and fully parameter-audited sensitivity deck.
# Preserve the classical control, contacts and DOS unchanged.
material material=IWO mc=0.34 ml=0.34 mt1=0.34 mt2=0.34
models srh fermi temp=300 bqp.n bqp.nalpha=0.5 bqp.ngamma=1.0 bqp.qdir=2 print
method block carriers=1 electrons trap maxtrap=10 itlimit=60
output con.band val.band e.mobility p.quantum
solve init
solve vgate=0 vsource=0 vdrain=0 nocurrent
# Continue with small, explicit biases only after this state converges.
```

This fragment is **not sufficient by itself** to establish a physically parameterized quantum run: the insulator and ambient boundary data below must also be explicitly resolved. The example mass 0.34 m0 and alpha/gamma pair are declared sensitivity assumptions, not measured IWO constants. Preserve the accepted current tolerances and other required solver controls when merging the METHOD statement; the short fragment does not authorize replacing them with loose defaults.

`BQP.NALPHA=0.5` and `BQP.NGAMMA=1.0` select the simplest square-root-density, order-unity Bohm-potential form for a diagnostic. The installed default gamma is 1.2, not 1.0. Neither value is an IWO calibration. Alpha and gamma should eventually reproduce a defensible zero-current charge profile/C-V reference, not be varied to fit Id while DOS and gate work function also move.

`BQP.QDIR=2` declares y as the principal confinement direction. The manual notes that this parameter has no effect for spherical bands; it is not a switch that confines the entire BQP calculation to a set of one-dimensional slices. The underlying model still uses the device's density gradients and effective-mass tensor.

## Mass and material assumptions

The target unified-framework paper discusses qualitative band-curvature/effective-mass trends but the inspected text does not supply a measured numerical confinement mass for this particular 2 nm sputtered IWO film. Do not silently retain silicon ML=0.916 and MT1=MT2=0.191 from the custom-material bootstrap.

For a diagnostic isotropic band, explicitly specifying MC, ML, MT1 and MT2 to the same chosen value avoids unintended silicon anisotropy. The 0.34 m0 value in the fragment is approximately consistent with the existing Nc300=5e18 cm^-3 seed under a single isotropic parabolic band with spin degeneracy two. This is a consistency calculation, not evidence that the actual transport/confinement mass is 0.34 m0. Mass, DOS mass, valley degeneracy and nonparabolicity need not agree with that simplified assumption in a real amorphous oxide.

As a scale calculation only, an ideal infinite 2 nm well with mass 0.34 m0 has first confinement energy approximately 0.28 eV. Real asymmetric finite barriers, electrostatics, disorder and multiple occupied states alter this. This number is not an ATLAS result or a prescribed threshold shift. It explains why a confinement sensitivity may matter at 2 nm and why simply adjusting the gate work function to erase it would defeat the test.

The BQP equation is applied globally and is also calculated in insulators (manual printed page 839). Consequently the Al2O3, HfO2 and Air definitions require an explicit audit of bandgap, electron affinity/barrier, Nc/Nv and masses. Relative permittivity alone, which sufficed for ideal classical insulating regions, is not a complete quantum barrier definition. Built-in silicon/SiO2 defaults are not validated IWO/Al2O3/HfO2 band offsets. The schematic's Air region is an electrostatic ambient; it is not a measured electronic barrier or semiconductor reservoir. A BQP result using unchecked ambient band defaults should remain an implementation diagnostic only.

The manual recommends setting insulator Nc/Nv consistently with the adjoining semiconductor for its BQP treatment. That is a numerical/model convention, not a measurement of the oxide's electronic DOS. Keep insulators classified as insulators: setting `MATERIAL ... SEMICONDUCTOR` would additionally solve drift-diffusion inside them and changes the physical model. Do not do that to obtain apparent leakage.

`REGION ... ZEROBQP` is documented: it assigns Q=0 and skips the BQP equation in that region. This is an available boundary/model approximation, not a generic solution to missing barrier data. It is not equivalent to imposing a physical infinite-wall wavefunction condition. Do not use it on all insulators without documenting and checking the resulting confinement boundary behavior.

## Statistics, transport, contacts and defects

| Combination | Installed evidence and required qualification |
|---|---|
| Electron-only current equations | The BQP chapter allows usual semiclassical equation combinations and independently enables BQP.N/BQP.P. `METHOD ... CARRIERS=1 ELECTRONS` is a reasonable first electron transport sensitivity; no hole quantum equation is needed for that branch. The exact custom IWO run remains untested. |
| FERMI | Explicitly supported and used in installed quantum examples. By default BQP follows the statistics selected for the other equations. High-density Fermi convergence can be difficult. |
| BQP.NOFERMI | Forces only the BQP equation to use its Boltzmann form; the manual requires recalibration after this change. It is not an innocuous convergence toggle and should remain off in the initial comparison. |
| Default BLOCK iteration | The documented standard BQP solver uses a modified BLOCK procedure. Ordinary NEWTON/GUMMEL selection does not mean the original classical algorithm remains unchanged. Record the actual equation/iteration output. |
| BQP.NEWTON | A separate fully coupled alternative, limited to BQP.N or BQP.P individually. It modifies equilibrium intrinsic density and requires `FREEZEBQPNI` on subsequent solves. Do not combine it with the minimal BLOCK test automatically. |
| Schottky contact | Installed quantumex09 combines BQP with a work-function-defined semiconductor contact. This supports general Schottky coexistence; it does not verify the exact Pd/IWO finite-emission source/drain boundary. Preserve its work function, SURF.REC, emission coefficients and tunneling flags and inspect contact-adjacent Q and current conservation. |
| Bulk DEFECTS | Installed solarex18_aux combines BQP.N with continuous DEFECTS in a different silicon/amorphous-silicon structure. Thus the feature families are not inherently mutually exclusive. That example does not validate IWO trap energy/occupation semantics under quantum corrections. |
| Native interface Gaussian | No specific installed example was found proving the exact BQP.N + custom IWO/Al2O3 INTDEFECTS + finite Pd-emission combination. First establish a trap-free quantum control, then restore the unchanged native DOS and compare its exports and occupied charge. |
| Tokyo/field mobility | Keep the selected classical mobility fixed for the initial quantum test. Quantum changes free density and thus can indirectly change any density-dependent mobility. Adding a new mobility law simultaneously would prevent attribution. |

Keep DOS centers tied to the intended material band edges and investigate how the simulator's quantum potential affects occupation; do not manually shift Gaussian energies by the calculated Q without a model derivation. Quantum-modified charge should not be multiplied by a second empirical free/total carrier-partition correction. Do not simultaneously enable density gradient (`QUANTUM`), Van Dort, Hansch, or full Schrodinger confinement and BQP to count the same effect twice.

`OUTPUT P.QUANTUM` is the documented output switch for electron and hole Bohm quantum potentials. Here it is an output request, not the `MODELS P.QUANTUM` hole density-gradient model. This naming distinction matters.

## Bounded validation sequence

1. Preserve the classical mesh/material/contact control and its hashes. Resolve and record the missing quantum mass/barrier assumptions before calling a result physically meaningful.
2. Use the same geometry with a refined vertical IWO mesh. Eight intervals through 2 nm are a starting point, not evidence of quantum convergence. Compare at least 16 and 32 intervals at selected bias states; resolve the wavefunction/charge centroid and interface density gradient rather than only terminal Id.
3. At Vd=Vs=0, solve the initial BQP state and a short gate-charge sequence using `CARRIERS=0` when comparing BQP to Schrodinger-Poisson. The manual's `QSCV` procedure is suitable for a charge-control reference; it is separate from an Id transfer curve.
4. Save Q, conduction-band energy, free density and charge-centroid profiles at the same gate biases in the classical and quantum cases. Check expected localization away from confining boundaries and sensitivity to the explicit masses/barriers. A screenshot alone is insufficient.
5. Only after the zero-current state is sound, resume the electron continuity solve with small drain steps and the unchanged contact law. Retain achieved bias tuples, all signed terminal currents, recovered-step diagnostics and the existing KCL/finite-value checks.
6. If DOS is restored, compare free and occupied sheet charge separately, plus native DOS export energies/amplitudes. Report which changes come from confinement and which from trap filling. Do not tune gamma, mass, band offsets, DOS and gate work function simultaneously.

BQP may shift the onset and charge distribution but does not automatically generate a positive off-current plateau or fix double-precision current cancellation. A completed quantum run still needs the same numerical-resolution and residual reporting as the classical model. Its use at 2 nm increases model scope; it does not establish a nearly exact atomistic device reconstruction.

Primary local references: `C:\sedatools\lib\atlas\5.28.1.R\docs\atlas_users1.pdf`, BQP printed pages 835-840 (PDF 839-844), Schrodinger mass definitions printed pages 828-830 (PDF 832-834), REGION ZEROBQP at PDF page 1563; `common/atlas.key`; installed examples quantumex05, quantumex07, quantumex08, quantumex09 and solar/solarex18/solarex18_aux.in. No proprietary example implementation is copied here.

## Follow-up: bounded zero-current comparison and actual loaded defaults

The actual completed run `20260912T071113_885520_class_bulk_tail_2nm/deckbuild.out` prints a regional material table. It demonstrates the following loaded values, before any quantum model was enabled:

| Region | Material | Eg (eV) | Affinity (eV) | Provenance |
|---|---|---:|---:|---|
| 1 | Air | 9.0 | 0.9 | Installed runtime defaults; artificial electronic ambient representation |
| 2 | IWO | 3.05 | 4.3 | Explicit classical model inputs |
| 3 | Al2O3 | 9.0 | 0.9 | Installed runtime defaults; not measured for this stack |
| 4 | HfO2 | 5.7 | 0.0 | Installed runtime defaults; not measured for this stack |

The corresponding affinity-rule conduction offsets from IWO are 3.4 eV to the Al2O3/Air definitions and 4.3 eV to the HfO2 definition. These are consequences of the loaded values, not experimentally established band offsets. The printed table does not establish insulator electron masses or Nc/Nv. The manual's insulator appendix, printed p.1698/PDF1707, supplies dielectric constants but does not supply the required electronic-barrier masses. No inspected installed example establishes those values for this IWO/Al2O3/HfO2 stack. The parser's generic ML=0.916/MT1=MT2=0.191 defaults are not oxide mass evidence.

A global BQP trial could freeze those actual loaded band defaults and explicitly set oxide Nc/Nv equal to IWO under the documented BQP convention. It would still require a declared insulator mass assumption rather than a falsely attributed installed physical mass. Such a run would be an **installed-default-boundary model sensitivity**, not finite-barrier quantum calibration. The candidate below instead uses the documented non-penetrating Schrodinger limit to avoid selecting unverified oxide masses.

The relevant documented region exclusion is `ZEROBQP` on the original non-IWO REGION definitions. It assigns Q=0 and omits that region's BQP equation. It does not turn `MODELS BQP.N` into a region-local model switch, and it does not specify a hard-wall electron wavefunction. Do not present a `ZEROBQP`-outside-IWO result as proof of correctly modeled physical barrier penetration.

Once quantum boundary assumptions are explicitly chosen, the shortest same-engine comparison design is:

1. Define the complete unchanged geometry, material/barrier/mass inputs, contacts, doping, DOS and native charge probes once. Put all mass and oxide-DOS conventions in place before both comparisons. Preserve the same vertical mesh and all physical parameters.
2. Use the classical model with `METHOD CARRIERS=0`, solve the initial state with Vd=Vs=0 and ramp Vg from 0 to 1 V in bounded steps. Save its native charge/centroid diagnostics, log and structure under unique classical filenames.
3. Close the classical LOG. Enable `BQP.N BQP.NALPHA=0.5 BQP.NGAMMA=1 BQP.QDIR=2`, use `METHOD BLOCK CARRIERS=0`, retain FERMI and the existing controls, and reinitialize. The first post-INIT solve should use `NOCURRENT`; repeat the same Vg ramp to 1 V at Vd=Vs=0. Save distinct BQP outputs including `P.QUANTUM`.
4. Compare free and ionized-trap charge in the same region plus the vertical carrier centroid/profile. Do not compare a Vd=0 charge state against the Vd=0.7 transfer curve as if it were a transfer-fit residual. A single mesh/parameter comparison can demonstrate a sensitivity, not quantum convergence or quantum calibration.

The native statements and zero-current BQP procedure are documented in section14.4. The exact proposed same-engine model-switch sequence has not been tested here; installed `quantumex05` isolates its comparisons with separate `go atlas` stages. Budget accounting must therefore follow the actual wrapper and engine launches selected by the caller rather than assuming this audit proved one-stage execution.

An alternative when oxide electronic parameters would otherwise be guessed is a **hard-wall Schrodinger-Poisson charge sensitivity**. The installed manual, printed p.831/PDF835, documents no electron penetration into insulators by default; `OX.SCHRO` enables penetration. A candidate electron model is `SCHRODINGER NUM.DIRECT=1 SP.GEOMETRY=1DY ^OX.SCHRO`, with explicit IWO isotropic MC=0.34 and CARRIERS=0. It excludes finite penetration by a stated boundary approximation instead of relying on unverified oxide masses. The direct aligned rectangular mesh satisfies the documented slicing requirement. Keep BQP disabled for this alternative and validate the solver's actual self-consistent charge outputs. This is a limiting confinement calculation, not the calibrated BQP transport model and not evidence of realistic finite barriers. No Schrodinger launch was performed by this audit.

## Concrete candidate for caller review

[`quantum_charge_bound.in`](../../decks_rebuild/diagnostics/quantum_charge_bound.in) is a complete one-engine, two-phase classical/hard-wall Schrodinger-Poisson charge comparison. Its companion JSON records the seed configuration, actual zero-drain/no-current-equation diagnostic settings, source/config/deck hashes, explicit assumptions and required acceptance checks. It is suitable as the provenance argument to `local_probe.run`; it is not a transfer-renderer input because the transfer renderer intentionally requires a positive drain bias and current equations.

The candidate uses the direct geometry and trap-free `rebuild_contact_electron.json` seed, a common 32-interval vertical IWO mesh, eight requested eigenstates and explicit MC=ML=MT1=MT2=0.34. Both source and drain remain at zero. Each phase independently initializes and requests Vg=0, 0.5, 1, 2 and 3 V. It saves five structures per phase, native average and interior electron-density log probes, source/drain voltage confirmations, and ten native `Electron Conc` cutline exports at x=12.037 um. The native EXTRACT label and `material="All"` curve form are demonstrated by installed `ledex01`; no numeric STR field identifiers are assumed. The cutlines retain all materials and the known IWO interval must be selected explicitly during analysis.

Static verification confirms one `go atlas`, two initializations, unique phase-specific output names, and zero source/drain biases. This is not an execution test. The caller must inspect the Schrodinger-Poisson potential/residual convergence, including its bounded-iteration and oscillation stopping behavior described on printed p.832/PDF836. Complete bias coverage alone does not prove a converged quantum solution. A single 32-interval/eight-state run also does not establish mesh or eigenstate convergence.

The caller subsequently executed this candidate in run `20260912T074348_745974_quantum_charge_bound_2nm`. The [actual charge verification](QUANTUM_CHARGE_VERIFICATION.md) reports all five native states, strict IWO charge integration, saved plots and the retained Poisson RHS qualification. It supersedes the candidate's unexecuted status while preserving the unvalidated mass, hard-wall boundary and mesh/eigenstate assumptions.
