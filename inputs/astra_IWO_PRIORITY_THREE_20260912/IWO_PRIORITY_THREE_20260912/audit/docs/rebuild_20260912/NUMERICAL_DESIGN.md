# Native ATLAS electrical rebuild: numerical design

Read-only design audit, 2026-09-12. No simulator was launched for this audit. The deck fragments below are proposed construction syntax, not a newly verified simulation or calibrated result. They use the installed ATLAS 5.28.1.R manual and the project's genuine run evidence.

## Design decision and physical boundary

Construct the electrical mesh directly with native `MESH`, `X.MESH`, `Y.MESH`, `REGION`, and `ELECTRODE` statements. This removes the ATHENA import and region-remapping dependency from the electrical diagnostic. It does not establish that ATHENA generated an invalid mesh: that cause has not been demonstrated.

Keep the separate, genuine ATHENA structure as process/geometry evidence. Its measured-thickness depositions reproduce geometry; they do not predict pulsed-DC sputtering stoichiometry, oxygen-vacancy formation, or annealing kinetics. The target's process recipe and its limits remain documented in [PROCESS_EVIDENCE.md](../combined_revision_20260911/PROCESS_EVIDENCE.md).

Use a three-terminal electrical domain ending at the continuous ideal TiN gate. The n+Si support underneath that metal is screened in this approximation and contributes no separate carrier-continuity equation. The physical support is retained in the process structure. This choice omits finite TiN resistance, substrate depletion/resistance, and TiN/Si transport; it is appropriate only for the present quasi-static ideal-gate baseline.

| Feature | Native electrical coordinates, micrometres | Status |
|---|---|---|
| Width | `mesh width=1`; physical W=290 | Unit-width slice; width scaling must be tested |
| Source overlap | x=0 to 2 | 2 micrometres is an explicit assumption |
| Exposed channel | x=2 to 22 | Reported L=20 micrometres |
| Drain overlap | x=22 to 24 | Same assumed overlap |
| IWO, 2 nm | y=-0.002 to 0 | Reported thickness |
| Al2O3, 2 nm | y=0 to 0.002 | Reported stack |
| HfO2, 15 nm | y=0.002 to 0.017 | Reported stack |
| TiN, 50 nm | y=0.017 to 0.067 | Explicit ideal metal volume |
| Pd, 70 nm | y=-0.072 to -0.002 at source/drain | Explicit electrode volumes |
| Ambient | Same y range as Pd, between electrodes | Air, relative permittivity 1; no added SiO2 cap |

For thickness t in micrometres, only the IWO top and Pd vertical positions change: IWO is -t to 0 and Pd is -(t+0.070) to -t. Preserve the 2 nm Al2O3 and 15 nm HfO2 coordinates. Do not introduce a fictitious interface slab.

## Native geometry fragment

The following is a 2 nm construction candidate. Region numbers are deliberate: IWO=2 and Al2O3=3, so the front interface is `intnumber="2/3"`. All electrode boundaries coincide with specified mesh lines. `Palladium` controls the display material; electrical contact behavior is specified separately.

```text
go atlas
mesh width=1
x.mesh loc=0    spac=0.20
x.mesh loc=1.8  spac=0.05
x.mesh loc=2    spac=0.02
x.mesh loc=2.2  spac=0.05
x.mesh loc=12   spac=0.50
x.mesh loc=21.8 spac=0.05
x.mesh loc=22   spac=0.02
x.mesh loc=22.2 spac=0.05
x.mesh loc=24   spac=0.20

y.mesh loc=-0.072  spac=0.010
y.mesh loc=-0.012  spac=0.002
y.mesh loc=-0.002  spac=0.00025
y.mesh loc=-0.0015 spac=0.00025
y.mesh loc=-0.001  spac=0.00025
y.mesh loc=-0.0005 spac=0.00025
y.mesh loc=0       spac=0.00025
y.mesh loc=0.001   spac=0.00025
y.mesh loc=0.002   spac=0.00025
y.mesh loc=0.0095  spac=0.001
y.mesh loc=0.017   spac=0.001
y.mesh loc=0.042   spac=0.005
y.mesh loc=0.067   spac=0.005

region num=1 material=Air x.min=0 x.max=24 y.min=-0.072 y.max=-0.002
region num=2 user.material=IWO x.min=0 x.max=24 y.min=-0.002 y.max=0
region num=3 material=Al2O3 x.min=0 x.max=24 y.min=0 y.max=0.002
region num=4 material=HfO2 x.min=0 x.max=24 y.min=0.002 y.max=0.017
region num=5 material=Conductor x.min=0 x.max=24 y.min=0.017 y.max=0.067

electrode num=1 name=gate material=Conductor x.min=0 x.max=24 y.min=0.017 y.max=0.067
electrode num=2 name=source material=Palladium x.min=0 x.max=2 y.min=-0.072 y.max=-0.002
electrode num=3 name=drain material=Palladium x.min=22 x.max=24 y.min=-0.072 y.max=-0.002

# Explicit, unfitted electrical seeds; not measured IWO material constants.
doping uniform n.type conc=2e17 region=2
material material=IWO user.group=semiconductor user.default=silicon \
 eg300=3.05 affinity=4.30 permittivity=9.3 \
 nc300=5e18 nv300=1e19 mun=14 mup=0.01 taun0=1e-6 taup0=1e-6
material material=Al2O3 permittivity=9
material material=HfO2 permittivity=19.57
material material=Air permittivity=1
contact name=gate workfunction=4.7
models srh fermi temp=300 print
output con.band val.band e.mobility
```

Add the chosen source/drain contact branch, audited solver settings, and a short bias/output sequence after this fragment. First run this geometry with constant mobility and without continuous bulk/interface DOS. The purpose is to establish material classification, contacts, dimensions, unit normalization, and observable fields. Its transfer curve is not expected to fit the experiment.

The native grid is still triangulated internally and is strongly anisotropic because a 20 micrometre channel is only 2 nm thick. A large aspect ratio alone does not prove an error. Refine x and y separately to determine which direction changes the electrical result. Do not require nanometre lateral spacing across 20 micrometres without evidence that this expense improves convergence.

## Contact branches and inherited-default audit

The Ohmic branch omits a source/drain work function. This is a named contact assumption, not evidence that Pd/IWO is experimentally Ohmic. Use it first if the objective is the simplest continuity-equation diagnostic.

A finite-emission alternative is documented as:

```text
# Sensitivity only: affinity 4.30 eV + assumed electron barrier 0.15 eV.
contact name=source workfunction=4.45 surf.rec
contact name=drain  workfunction=4.45 surf.rec
```

`WORKFUNCTION` is an absolute energy input here: affinity plus electron barrier. Recompute it if affinity changes. `SURF.REC` selects finite thermionic emission velocities; a work-function-only branch is not the same boundary. The effective 0.15 eV barrier is not the measured vacuum work function of Pd.

Do not activate tunneling, image-force barrier lowering, hopping injection, impact ionization, illumination, or ferroelectricity merely to remove a numerical zero. In the isolated contact comparison, leave `E.TUNNEL`, `H.TUNNEL`, `PARABOLIC`, `BARRIER`, `ALT.BARRIER`, `PIPINYS`, `SCOTT.MALLIARAS`, and `UST` disabled. A later physical leakage model needs mechanism-specific evidence and parameters.

The thermionic branch otherwise inherits silicon Richardson values: ARICHN=110 and ARICHP=30 A/(cm^2 K^2). At 300 K with the stated Nc/Nv, the manual's default velocity formula gives approximately 1.24e7 and 1.69e6 cm/s. These are unvalidated IWO assumptions. Record them explicitly in the run manifest; fitting a barrier while silently varying emission velocities is not a one-parameter comparison.

The `INS.OHMIC` default is true. Inspect actual contact adjacency and the runtime contact summary: a contact shared with semiconductor and insulator may be treated as Ohmic. If a finite Schottky boundary needs `^ins.ohmic`, treat that as an explicit physical boundary choice and confirm it in a new log. Do not assume the material name `Palladium` sets the barrier or that an accepted keyword proves the intended boundary was applied.

| Field | Units / meaning | Rebuild requirement |
|---|---|---|
| Geometry and mesh width | micrometres | Convert nm once: 2 nm = 0.002 micrometres |
| `eg300`, `affinity`, work functions | eV | Set explicitly; do not inherit silicon bandgap or use a barrier as a work function |
| `permittivity` | Relative dielectric constant | No vacuum-permittivity multiplication in input |
| `nc300`, `nv300`, donor concentration | cm^-3 | State seeds and distinguish chemical W fraction from ionized donors |
| `mun`, `mup` | cm^2/(V s) | Constant-mobility control before any density/field-dependent law |
| `taun0`, `taup0` | seconds | Bulk SRH background assumption; not a Gaussian DOS or capture cross section |
| Gaussian `NGA/NGD`, bulk | cm^-3/eV peak DOS | Do not label as integrated defect concentration |
| Gaussian `NGA/NGD`, interface | With `MAX.GAUSSIAN`: cm^-2/eV peak DOS | Explicitly select peak convention; do not silently change to integrated Gaussian convention |
| `EGA` | eV below Ec | Same convention in bulk and interface statements |
| `EGD` | eV above Ev | A donor Ec-0.20 eV at Eg=3.05 requires EGD=2.85 eV |
| `WGA/WGD` | eV in exp[-((E-E0)/W)^2] | W is sqrt(2) times the statistical Gaussian standard deviation |
| `NTA/NTD`, bulk/interface | cm^-3/eV or cm^-2/eV at band edge | Explicitly zero any inactive band; do not inherit defaults |
| `WTA/WTD` | eV characteristic tail energy | Not a Gaussian width or temperature input |
| `SIG*` capture cross sections | cm^2 | Set each active band's electron and hole values explicitly |
| `NUMA/NUMD` | Energy integration/discretization counts | Resolution controls; not physical trap parameters |
| `INTERFACE QF` | Elementary charges per cm^2 | Signed sheet number, not C/cm^2 and not an independent Gaussian DOS |
| `CLIMIT` | Carrier-normalization threshold | Not an output-current floor or an arithmetic-precision setting |

Declare all four DOS amplitudes explicitly whenever enabling `DEFECTS` or `INTDEFECTS`; the installed defaults contain substantial amorphous-silicon-like trap populations. Native interface traps at `intnumber="2/3"` avoid converting a sheet DOS into a made-up interfacial volume. Save AFILE/DFILE/TFILE and check peak positions, peak amplitudes, and integrated density independently. For a Gaussian well away from the band edges, the integral is peak*W*sqrt(pi); use the band-truncated integral for a near-edge Gaussian. A fixed Ec-relative donor depth requires updating EGD if Eg changes.

`user.default=silicon` is a bootstrap for a custom semiconductor, not a complete IWO database. Print and archive the active material values. At fixed 300 K the stated band/DOS overrides control the intended baseline, but temperature laws, thermal velocities, Richardson constants, and any subsequently enabled model coefficients need separate review. Do not claim a validated temperature-dependent model from a single 300 K run. Background SRH and explicit defect recombination are separate channels and can double-count the same physical centers if both are fitted without a decomposition.

## What the existing runs actually establish

The older imported full-substrate run had a shielded-Si numerical current branch. That is different from the following later three-terminal contact tests:

| Genuine run | KCL result in its validation.json | Outstanding issue |
|---|---|---|
| `20260911T154221_075249_combined_schottky_full_2nm` | Passed; maximum absolute residual 7.4e-21 A | 55 nonpositive drain samples; no accepted calibration |
| `20260911T154437_705885_combined_mesh_full_2nm` | Passed; maximum absolute residual 2.0e-22 A | 55 nonpositive drain samples; mobility/electron point probes zero |

Both contain 121 requested gate samples. A passed KCL condition does not prove a resolved off-current: two terminal currents can both underflow or become zero while their sum remains zero.

Read-only inspection of these final STR files establishes that the existing probe coordinate (12,-0.068) is exactly an IWO region-5 vertex in both meshes. It is node 428 of 3878 coarse nodes and node 1397 of 13594 refined nodes; six IWO triangles meet at that point in each case. It is not outside IWO or in the gate dielectric. This observation does not establish why one run's probes are zero. Being on a vertex is not sufficient evidence of the cause because the coarse run used the same type of location successfully.

## Observable-field checks before calibration

The installed PROBE algorithm locates a containing triangle and, for directional quantities, selects the edge nearest `DIR`. For a new point probe, choose a coordinate strictly inside a known IWO triangle in the saved mesh, with a margin from its edges. Do not choose the channel midpoint solely because it is geometrically convenient; explicit midpoint mesh lines make it a vertex again. Repeat at a second interior triangle.

Add an independent interior-box average rather than relying on one point. Documented syntax for the proposed coordinates is:

```text
probe name=n_core_avg average n.conc \
 x.min=8 x.max=16 y.min=-0.00175 y.max=-0.00025
probe name=mu_core_avg average n.mob dir=0 \
 x.min=8 x.max=16 y.min=-0.00175 y.max=-0.00025
```

This combination is a proposed runtime check, not yet verified for the rebuilt deck. The box excludes dielectric and contacts and contains multiple IWO nodes. Compare its outputs with the point probes and `e.mobility`/electron-concentration structure fields at an accumulated bias. In the constant-mobility control, the lateral mobility should be consistent with the explicit 14 cm^2/(V s) input. A zero single-point probe with nonzero box and structure values supports a probe-location/selection problem; all three failing requires checking model classification, output availability, and the solution itself.

Saved structure fields can be interpolated/noisy according to the manual, so use them as a cross-check rather than silently replacing native terminal currents. The installed CCD example also demonstrates native concentration cutline extraction with `curve(depth,n.conc material="Silicon" mat.occno=1 x.val=...)`; adapting its material string to IWO is a useful optional check requiring a real runtime test. Do not guess numeric STR field identifiers and label them as electron concentration or mobility without a verified mapping.

## Bounded numerical plan and interpretation

1. **Trap-free constant-mobility control.** Confirm startup/version/features, region dimensions, three named terminals, interface adjacency, and active material values. Save equilibrium plus one accumulated state and native probes. Reject truncated electrode warnings or incomplete region coverage.
2. **Bias and sign control.** At selected gate biases, test Vd=0 and small positive/negative Vd from fresh saved states. With a symmetric device, source/drain exchange should produce the corresponding symmetric response; compare gate bias relative to source consistently. A zero-bias residual or sign-changing current of the same scale as the claimed off-current indicates an unresolved numerical floor. Compare full signed terminal currents rather than absolute values.
3. **Single-change mesh comparisons.** Refine lateral spacing with identical y lines, then refine IWO/dielectric y spacing with identical x lines. Preserve all physical and contact parameters. Compare terminal currents, core carrier density, mobility, and geometry; a changed point probe by itself is not evidence of changed transport.
4. **Width comparison.** Repeat selected states at width=2 or 290. Compare Iraw/width in A/micrometre, including numerical zero/sign behavior. Unit-width output already has the numerical value of A/micrometre; never divide it by 290 a second time. Width scaling may improve a numerical signal but does not create a physical leakage mechanism.
5. **Contact comparison.** Compare Ohmic and explicitly finite-emission branches only after the same mesh/probes are checked. A better KCL residual alone is insufficient to choose a physical contact model. Check on-current, subthreshold shape, symmetry, and consistency with the absence of measured contact-barrier data.
6. **Restore paper-based DOS in stages.** Add the conduction-band tail, native interface Gaussian, then oxygen-related/deep bulk bands. Change one group at a time. Double NUMA/NUMD at selected biases while holding amplitudes and energies fixed. Add a density/field-dependent mobility law only when native probes demonstrate its expected response; do not reintroduce a bias-indexed mobility update that only affected initialization.
7. **Calibrate only resolved observables.** Maintain the predetermined absolute-plus-relative KCL check, signed-current audit, coverage, convergence, and mesh/DOS acceptance conditions. Report linear residuals for all finite signed samples. Log residuals are undefined for nonpositive simulated currents; count and disclose these samples. A plotting magnitude, clipping constant, or measurement-floor overlay must never replace the real simulated current in a claim of fit.

Use bias continuation and bounded step reductions, recording each accepted target voltage. Keep `MAXTRAP` within the installed documented range (up to 10); `METHOD TRAP` means automatic bias-step cutting, not physical trap states. Tighter CR/IR/CX tolerances do not add arithmetic bits. The documented `-80` and `-128` launch alternatives previously failed to complete a simulation on this installed Windows system, so they are not an established remedy. See [atlas_precision_audit.md](../paper_revision_20260911/atlas_precision_audit.md).

A model-limited off-current is plausible if signed currents, mesh, width, contact boundary, carrier fields, and DOS integration are stable but the chosen dark drift-diffusion mechanisms predict negligible conduction. It must be distinguished from a verified numerical zero before adding physics. The workbook's low-current plateaus alone cannot identify instrument offset, parallel leakage, surface conduction, contact leakage, or tunneling uniquely. Preserve that identifiability limit instead of forcing agreement by arbitrary Gaussian changes or invented parallel currents.

## Installed primary references

- `C:\sedatools\lib\atlas\5.28.1.R\docs\atlas_users1.pdf`: ELECTRODE printed pages 1207-1210 (PDF 1213-1216), including explicit volume bounds, mesh-node placement, and separation of display material from electrical properties.
- Same manual: MESH printed pages 1373-1375 (PDF 1379-1381); REGION printed page 1548 (PDF 1554); custom materials appendix B.2.5 printed page 1668 (PDF 1677).
- Same manual: Schottky boundary section 3.5.2, pages 158-164, and CONTACT reference printed pages 1145-1153.
- Same manual: TFT DOS equations printed pages 873-877 (PDF 879-883); DEFECTS printed pages 1167-1170 (PDF 1173-1176); INTDEFECTS printed pages 1244-1249 (PDF 1250-1255).
- Same manual: PROBE printed pages 1524-1535 (PDF 1530-1541), especially the box average/integration and triangle-edge direction descriptions.
- Installed parser `C:\sedatools\lib\atlas\5.28.1.R\common\atlas.key` confirms the PROBE `AVERAGE`, `N.CONC`, and interface `MAX.GAUSSIAN` keywords.

This document summarizes the licensed local manuals without reproducing their proprietary text. The new geometry and diagnostic branches require fresh, authorized simulator runs before they can be called tested.

## Addendum: recovered bias-step warnings and acceptance

Read-only follow-up on 2026-09-12. A warning containing `Convergence problem. Taking smaller bias` describes a failed **attempt**, not necessarily a failed requested bias. The installed manual, section 2.9.2, pages 90-91, explicitly describes `METHOD TRAP`: a failed step is reduced, a convergent intermediate solution is found, and the original target is retried before the ramp continues. Rejecting every occurrence of this warning incorrectly rejects a normally recovered continuation sequence.

The standard DC output semantics support using native logged achieved biases as evidence. Manual page 97 states that the electrode results table follows convergence. Pages 97-98 and the LOG reference (printed pages 1299-1301, PDF 1305-1307) describe logging the calculated terminal characteristics. In particular, `LOG NO.TRAP` suppresses the additional DC cutback-step records; its default is false. Thus a normal LOG file may contain more solved rows than the requested measurement grid. A LOG row is not merely an echoed `SOLVE` request. However, the manual does not provide a universal per-row success flag for every operating mode, and a present row alone does not prove numerical accuracy. For this DC workflow, pair achieved rows with completion, diagnostics, and the existing current/voltage checks.

Fresh read-only evidence from existing output files agrees with this behavior:

- In `20260911T144832_495009_paper_native_DOS_2nm_01`, the first -0.70 V attempt diverged, the run printed the cutback warning, and a results table was produced at -0.725 V, then at -0.70 V. The native transfer LOG contains the corresponding -0.75, -0.725, and -0.70 V rows. This demonstrates recovery of that target only; that older run itself stopped before the full +3 V endpoint.
- In the still-running `20260912T065050_238465_rebuild_contact_both_2nm` snapshot inspected for this addendum, the first -1.45 V attempt exceeded its iteration limit. The LOG subsequently contained -1.475, -1.4625, several smaller intermediate steps, and finally an actual -1.45 V result. This demonstrates recovery of that requested target. It does not establish completion or acceptance of the entire run.

Retain the following distinctions in validation:

| Diagnostic | Interpretation |
|---|---|
| `Newton algorithm did not converge ... iterations` | The indicated attempt exhausted its iteration limit; subsequent TRAP recovery may still succeed |
| `Solution diverging. Potential update too large` | The indicated attempt diverged; assess whether the requested target was later recovered |
| `Convergence problem. Taking smaller bias` / `Bias step reduced ... times` | Automatic continuation recovery is being attempted |
| `Bias step cut back more than ... times. Cannot trap.` | Automatic recovery limit exhausted; do not classify as recovered solely because earlier intermediate rows exist |
| `Cannot trap. Cannot reduce bias` or `Could not trap, cannot reduce bias` | No further recovery available for that attempt/command |
| `Cannot trap. Trapping not enabled` | Recovery was unavailable; the failed target needs separate explicit successful evidence |

The last three message families were verified as embedded messages in the installed `atlas2.exe` read-only; they were not generated by a new simulator launch in this audit. Some are warning-prefixed and some error-prefixed, so checking only `Error:` is inadequate. In this simple sweep workflow, keep those exhaustion diagnostics as rejecting conditions. If a future deck intentionally retries an exhausted target with a new explicit strategy, it needs a separate, ordered recovery record rather than a global exception.

Recommended acceptance logic:

1. Require successful process completion, the actual ATLAS finished banner, expected fresh outputs, and their recorded hashes. A return code of zero alone is insufficient. Preserve parser, license, fatal, extraction, and exhausted-recovery errors as rejecting evidence.
2. Parse the native transfer LOG's actual voltage tuples, not only echoed `ATLAS> solve` commands. Match every requested gate voltage together with its source/drain biases within the declared numerical voltage tolerance. Require both endpoints and all interior targets. Do not replace a missing requested target with the nearest cutback point or an interpolated value.
3. Allow additional solved cutback rows. Keep them in the immutable raw LOG. Build a separate requested-grid view for measurement comparison, and record which raw row supplies each target. If a target occurs more than once, preserve all occurrences and use a documented branch/order rule; do not average away path dependence.
4. Record warning counts, warning line numbers, the requested target active at each warning, the intermediate achieved biases, and whether that target subsequently has an accepted results table/LOG row. A run with fully recovered warnings may pass the sweep-completion gate while retaining a `recovered_bias_steps` warning status.
5. Apply the existing finite-value, signed-current, KCL, terminal-voltage, mesh/DOS, and physical-model checks independently. Recovery of a solver target does not establish that its tiny current is physically resolved or fitted.

The existing `atlas_workflow.check_coverage` already permits extra adaptive rows and requires each requested gate within 1e-6 V. Retain that behavior. At the time of this audit, both `paper_trial.inspect` and `atlas_workflow.validate_run` instead included the generic `convergence problem` phrase in a rejecting regular expression. Replace that global rejection with the evidence-based recovery classification above; do not erase the phrase or warnings from saved logs. Also retain checks of source/drain voltage at each selected gate target and add native-LOG provenance if relying on extracted XY files.

Leave `LOG NO.TRAP` disabled in diagnostic runs so successful intermediate steps remain inspectable. Suppressing intermediate records is unnecessary for comparison because the requested-grid view can select the verified targets without modifying raw evidence.
