# Scope of the three-film IWO model

Snapshot: 2026-09-12, after the completed native 6.3 nm mobility and 13.2 nm donor trials. This note describes the actual commands produced by `scripts/rebuild_model.py` for the three configuration/key pairs below. The 2 nm configuration corresponds to the retained completed reference. Both newer candidates pass strict native checks and meet the working active-region targets of log RMSE below 0.05 decades and absolute +3 V current error below 5%: **6.3 nm 0.04920549 decades / +1.96668%**, run `20260912T124657_803129_priority3_fit6_mu12_retry2`; **13.2 nm 0.04902804 decades / +2.45230%**, run `20260912T122359_458630_priority3_fit13_nd89`. **Their candidate-specific numerical controls, final retention and fit acceptance remain pending.** These active metrics exclude the documented low-current scoring regions; the full curves still contain 54 and 46 native zero-current samples respectively. Subsequent delivery manifests must identify the actual selected runs and certificate scope. The 31.8 nm branch is deferred. See [actual calibration tradeoffs](PRIORITY_THREE_ACTUAL_CALIBRATION_TRADEOFFS.md).

| Film | Configuration | Generator key |
|---|---|---|
| 2 nm | `config/rebuild_fit_bulk_width04.json` | `2p0` |
| 6.3 nm candidate | `config/priority3_fit6_mu12.json` | `6p3` |
| 13.2 nm candidate | `config/priority3_fit13_nd89.json` | `13p2` |

Each JSON retains other thickness entries for provenance. **Only its named key is evaluated here.** Using a different key from the same file can select older, unevaluated parameters. Generic `UNVALIDATED`/historical provenance text is preserved; acceptance comes from the exact run and certificate, not that text.

## Shared electrical model

All three use native ATLAS classical drift-diffusion/Poisson, Fermi statistics, 300 K, background SRH, and one electron continuity equation: `models srh fermi temp=300 print` and `method newton carriers=1 electrons ...`. The hole mobility and lifetime are defined material inputs; an independent hole-current solution is not established by this configuration. The full-model uncertainty at 2 nm includes quantum confinement. The separate completed hard-wall charge diagnostic is not a quantum correction applied to these transfer curves.

| Shared input | Value and interpretation |
|---|---|
| IWO bandgap / electron affinity | 3.05 / 4.30 eV; priors from a different IWO study, not measurements of these films |
| IWO Nc / Nv at 300 K | 5e18 / 1e19 cm^-3; explicit electronic assumptions |
| Relative permittivity | IWO 9.3; HfO2 19.57; Al2O3 9.0; Air 1. The Al2O3 value is provisional. |
| Gate work function | 4.7 + 0.065 = **4.765 eV** in the actual CONTACT command. The fitted shared shift is an effective contact/electrostatic parameter, not a postprocessed voltage shift. |
| Source/drain boundary | `workfunction=4.45 surf.rec`; effective electron barrier 4.45 - 4.30 = 0.15 eV at each Pd/IWO contact |
| Contact emission | No explicit velocity or Richardson override in these three files; the installed custom-material defaults give electron/hole Richardson constants 110/30 A cm^-2 K^-2. These are disclosed assumptions, not measured Pd/IWO values. |
| Background lifetimes / hole mobility | taun0=taup0=1e-6 s; mup=0.01 cm^2 V^-1 s^-1 |
| Trap capture cross sections | All specified electron/hole tail/Gaussian capture inputs are 1e-15 cm^2; only populated, enabled families contribute. |
| Drain/source bias | Vd=0.7 V, Vs=0; the transfer sweep contains the original 121 gate targets from -3 to +3 V in 0.05 V steps. |

`user.default=silicon` supplies a software bootstrap for the custom IWO material; it does not make the channel silicon or establish a complete IWO material database. The band/DOS/permittivity/mobility/lifetime values above are explicitly overridden. Active inherited emission/thermal-velocity assumptions remain documented in [CONTACT_EMISSION_DEFAULTS.md](CONTACT_EMISSION_DEFAULTS.md). No source/drain series resistance, contact tunneling, image-force barrier lowering, Poole-Frenkel/TAT correction, dielectric conduction, illumination, ferroelectricity, or stress-driven defect creation is enabled in these three configurations.

## Thickness-dependent fit parameters and active traps

The chosen transport mode is **constant band mobility**, with a uniform shallow donor background and one continuous bulk acceptor tail. Its native energy distribution is

```text
gTA(E) = NTA * exp[(E - Ec)/WTA],  Ev <= E <= Ec.
Nbulk = NTA * WTA * [1 - exp(-Eg/WTA)].
```

NTA is a volumetric DOS at the conduction-band edge, in cm^-3 eV^-1; WTA is an energy scale in eV. Multiplying Nbulk by thickness in cm gives a sheet-equivalent **capacity**, not the occupied trap density. Occupancy and its electrostatic effect are solved natively and inspected separately from the exported DOS. Filled acceptors carry negative charge. The uniform positive donor input is not a measured oxygen-vacancy concentration or a resolved donor Gaussian.

| Film / status | Uniform ND, cm^-3 | Band mobility, cm^2 V^-1 s^-1 | NTA, cm^-3 eV^-1 | WTA, eV | Tail sheet-equivalent capacity, cm^-2 |
|---|---:|---:|---:|---:|---:|
| 2 nm reference | 2.0e17 | 13.3 | 5.5e20 | 0.040 | 4.4e12 |
| 6.3 nm candidate | 1.0e17 | 12.0 | 3.714285714e20 | 0.040 | 9.36e12 |
| 13.2 nm candidate | 8.9e17 | 55.0 | 7.142857143e19 | 0.035 | 3.3e12 |

These are per-film effective fit parameters, not a validated universal thickness law. The 6.3 nm candidate changes band mobility from 13 to 12 relative to its preceding charge-refined trial; the 13.2 nm candidate changes ND from 8.6e17 to 8.9e17 cm^-3. Both changes have now been evaluated by completed native simulations; candidate-specific numerical checks remain pending. They do not authorize rescaling old current exports or transferring old physical-candidate certificates.

| Family or configuration fields | Actual state for these selected keys |
|---|---|
| Bulk acceptor tail | Enabled: `defects ... continuous`, positive NTA/WTA |
| Bulk donor tail | Disabled by emitted `NTD=0` |
| Bulk acceptor Gaussian | Zero capacity: selected `NGA=0`; its stored center/width do not create traps |
| Bulk donor Gaussian | Zero capacity: selected `NGD=0`; its stored center/width do not create traps |
| Interface Gaussian/tails | **Disabled:** `defects.interface=false`, so no `INTDEFECTS` command is emitted. The dormant 2 nm `interface_peak_cm2_eV=2e11` is not an active sheet-trap population. |
| Tokyo density-mobility fields | Dormant: gamma0, tgamma and ncrit remain in JSON, but `transport.mode=constant` emits no Tokyo model |
| PRPMOB/field-mobility branches | Not selected |

The generator supports other families for controlled hypotheses, but their existence in code or JSON must not be described as their inclusion in the selected physical model. Adding every possible Gaussian would introduce populations the present data cannot uniquely constrain. The effective acceptor tail can represent disorder-related localized states; its fitted capacity does not identify a unique oxygen, hydrogen, or metal-vacancy chemical species. No extra free/trapped fraction is multiplied into the band mobility: the native trap charge and free carriers already affect the self-consistent solution.

## Geometry and numerical representation

The mesh is constructed directly in ATLAS, with no external structure dependency. The physical stack represented is n+Si support / TiN 50 nm / HfO2 15 nm / Al2O3 2 nm / IWO / Pd 70 nm. In the electrical solve the continuous ideal TiN gate screens the support, so the domain ends at that gate and omits the Si carrier equations. The gate metal is represented as `Conductor` with its explicit work function; Pd occupies the source/drain electrode volumes.

For film thickness t in micrometres, IWO occupies y=-t..0, Al2O3 y=0..0.002, HfO2 y=0.002..0.017 and the ideal gate y=0.017..0.067. The Pd contacts extend 0.070 um above the IWO surface. Air fills the exposed space; **no SiO2 overlayer is added**. Source overlap is x=0..2 um, channel x=2..22 um and drain overlap x=22..24 um. The 20 um channel length is fixed; each 2 um overlap is an explicit unmeasured assumption.

The 2D cross-section is uniform across width. Simulation width is 1 um; its raw current therefore has the numerical value used for A/um. The physical W=290 um total is 290 times the normalized current. This approximation omits finite-width edges, roughness topography, grain-resolved transport, finite TiN/substrate transport, and contact microstructure. Their omission is not evidence that they are absent in the device.

The source configurations start with 8 IWO intervals, 4 Al2O3 intervals and 10 HfO2 intervals; the 6.3/13.2 nm meshes additionally refine near the IWO boundaries through the generator's graded-mesh option. These requested settings are not substitutes for the realized native mesh or its controls. The 2 nm source uses NUMA/NUMD=384/192; the two candidates start at 192/96. Donor energy counts do not create a donor population when its DOS amplitude is zero. Candidate-specific x/y/DOS evidence must establish resolution; the 2 nm certificate does not certify the others' mesh or DOS.

The solver uses 64-bit arithmetic and bounded Newton/bias-cutback controls. `METHOD TRAP` cuts failed bias steps; it is unrelated to physical defect populations. Geometry/equilibrium/off/final structures, signed gate/source/drain currents, mobility/electron probes, and bulk free/ionized-trap averages are saved. The two thicker candidates also request front/back electron-density probes. These probes diagnose the native solution; they add no transport mechanism. The `gate_step_V=0.1` setting controls initial bias preparation; the recorded transfer sweep still uses all original 0.05 V measurement targets.

## Process and fit limits

The reported pulsed-DC sputter recipe motivates the material and dimensions. Earlier licensed ATHENA work established a geometric deposition/patterning representation. It did not establish calibrated IWO sputter yield, oxygen incorporation, vacancy creation/annealing kinetics, or predictive chemistry. The selected direct-ATLAS inputs therefore make no claim that ATHENA predicted their ND, mobility or DOS from sputter power and gas settings.

The generator reads measured **gate voltages only**. Calibration compares genuine native currents with the preserved measurement currents; no analytical Python fit, interpolated measurement, voltage-remapped curve or added leakage current enters the generated device. All signed samples remain in linear residuals; zero/negative native currents have no logarithmic residual and must retain their counts and visible gaps. The measured low-current plateaus remain unresolved, and there is no arbitrary current floor. See [PRIORITY_THREE_OFF_CURRENT_AUDIT.md](PRIORITY_THREE_OFF_CURRENT_AUDIT.md).

An accepted active-region residual and passed numerical controls establish a useful, bounded electrical fit for that exact candidate. They do not establish a nearly 100% realistic reconstruction, unique trap chemistry, validated quantum transport, or predictive behavior outside the measured conditions. Final delivery must report its actual selected run IDs, residuals, certificate scope and remaining limitations independently of this configuration snapshot.

## Snapshot fingerprints

Software-only rendering was checked for the named keys; this audit launched no simulator and changed no scripts/configurations.

| Source | SHA256 |
|---|---|
| `scripts/rebuild_model.py` | `151bb0c0f3d458d2b082e34d2ecb91e5a617b17558c0d6ce873626403738c2e9` |
| `config/rebuild_fit_bulk_width04.json` | `e2068f83f2f207eb28a442848c0aa37e75cf6abdaea9728743628144e1982b6b` |
| `config/priority3_fit6_mu12.json` | `7411cf29426cd8048dd88586359c8f6b7f22ae995cf521ca7a2ec13d71cf73d4` |
| `config/priority3_fit13_nd89.json` | `b0a9c76c0969de035ae75baa89c42622f3b685c8b5d7a08bb54248cba634b3ec` |
