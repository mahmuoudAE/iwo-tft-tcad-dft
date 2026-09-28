# Off-current audit for the 2, 6.3 and 13.2 nm models

Read-only audit, 2026-09-12. No simulator was launched, physical parameter changed, saved current corrected, or raw run edited. The new work priority is the three thinner films. This note uses named completed snapshots; it does not label subsequent running calibration or mesh controls complete.

**Recommendation: preserve the remaining simulator starts for the active-region fit and its x/y/DOS checks. Do not spend a reserve start merely changing the retained model to two carrier equations.** Ordinary thermal SRH generation, even with an intentionally generous bound on all currently configured continuous traps, is 13–17 orders below the measured plateaus. A new generation or leakage mechanism is not identified by the available transfer curves. The off-current mismatch remains an explicit limitation of the present model.

## What the actual currents establish

The following three snapshots pass the current strict `rebuild_check.load_run` checks, including all 121 original gate targets, execution/output hashes, signed terminal currents and the existing numerical acceptance checks. This statement concerns native run evidence; it is not a claim that the measured plateau is fitted.

| Thickness | Completed snapshot | Positive / zero / negative native Id samples | Measured median Id, -2 <= Vg <= -0.5 V | Native Id in that same gate interval |
|---|---|---:|---:|---:|
| 2 nm | `20260912T074527_865393_fit_bulk_width04_2nm` | 67 / 54 / 0 | 4.60552e-15 A/um | Exactly zero in exported native LOG |
| 6.3 nm | `20260912T091742_999942_extension02_charge_6p3nm` | 67 / 54 / 0 | 1.52759e-13 A/um | Exactly zero in exported native LOG |
| 13.2 nm | `20260912T090754_224585_extension02_charge_13p2nm` | 75 / 46 / 0 | 6.59655e-12 A/um | 0 to 1.270269381e-18 A/um |

Measured minimum/maximum currents within that reporting interval are 2.41379e-15/5.51414e-15, 7.10345e-14/2.12759e-13, and 6.42069e-12/6.80345e-12 A/um, respectively. This interval summarizes the plateau; it does not replace the pre-existing measurement masks or exclude any original sample from the linear residual report.

All current values above come from the original CSV or native terminal LOG, with the actual simulated width normalization. No current interpolation, absolute-value replacement, or positive floor was applied. All 121 signed points must remain in linear residuals. A logarithmic residual is undefined where simulated Id is nonpositive; its missing-point count must remain visible. Passing an absolute-plus-relative KCL bound cannot establish that a sub-bound current, or an exact zero, is physically resolved.

## Existing two-carrier and precision controls

The three earlier trap-free 2 nm controls were read directly. Every execution-recorded output hash was recomputed and matched; each output contains the actual ATLAS 5.28.1.R completion banner. All 121 target biases are present. These are completed diagnostics, not new or calibrated trapped-model runs.

| Run | Electrical boundary / equations | Native result and acceptance limit |
|---|---|---|
| `20260912T064920_755417_rebuild_trapfree_both_2nm` | Ohmic, electrons and holes | 35 negative drain samples; KCL failed at 17 targets. The deep-off signed current is about 1e-19–1e-18 A/um. This rejected numerical result is not a leakage prediction. |
| `20260912T065050_238465_rebuild_contact_both_2nm` | Schottky, electrons and holes | 137 native rows including recovered cutbacks; all 121 requested targets present; KCL passes the stated absolute-plus-relative test. There are 89 positive and 32 negative target Id values. Tiny signed depletion values do not reproduce the measured plateau. |
| `20260912T065744_067791_rebuild_contact_electron_2nm` | Same Schottky model, electrons only | 121 native rows, 68 positive and 53 exact-zero target Id values. Accumulated Id matches the two-carrier counterpart to the saved precision at Vg=0, 0.5, 1 and 3 V. |

Examples from the Schottky two-carrier native LOG: Id(-3 V)=2.106118614e-53, Id(-2 V)=-6.679570136e-48, Id(-1 V)=-2.464524075e-34 and Id(-0.5 V)=2.343074467e-54 A/um. The electron-only counterpart exports zero at those same biases. These tiny two-carrier values are not evidence of a resolved physical floor: signs and source/drain balance at that scale remain below the absolute numerical acceptance limit. The earlier control also lacks the retained bulk DOS, so it cannot by itself certify the retained model's generation response. The analytical upper bound below addresses whether that missing test is worth a scarce launch.

The documented `go atlas simflags="-128"` and `-80` alternatives were actually attempted in this Windows installation. Runs `20260911T145925_836281_paper_active_128_2nm_01` and `20260911T150155_078376_paper_active_80_2nm_01` did not complete a device simulation. They provide no working extended-precision comparison. Increasing printed digits or tightening CR/IR/CX tolerances does not increase arithmetic precision. See [the precision audit](../paper_revision_20260911/atlas_precision_audit.md) and [numerical design](NUMERICAL_DESIGN.md).

## A generous thermal-generation bound

This calculation is a physical scale check using the configured inputs and documented SRH equations. **It is not an ATLAS current curve, measured leakage estimate, or correction to any native current.**

At 300 K, the common Eg=3.05 eV, Nc=5e18 cm^-3 and Nv=1e19 cm^-3 imply the nondegenerate intrinsic concentration

```text
ni = sqrt(Nc*Nv) * exp[-Eg/(2*kB*T)] = 1.70064067e-7 cm^-3.
```

The installed manual's steady-state continuous-trap equation (15-16, printed p.877 / PDF p.883) gives, in the generation limit n=p=0, a contribution per trap proportional to

```text
ni * cn*cp / [cn*exp(u) + cp*exp(-u)],
cn = sigma_n * vn, cp = sigma_p * vp, u = (Et-Ei)/(kB*T).
```

The denominator is at least `2*sqrt(cn*cp)`. Consequently, even putting every trap at its optimum generation energy gives

```text
G_thermal <= ni * sqrt(cn*cp) * N_total / 2   [cm^-3 s^-1].
```

Finite nonnegative free-carrier populations further increase the denominator or reduce net generation. This is a bound on the ordinary thermal model under the stated band/statistics assumptions; it is not a bound on field-assisted tunneling, external illumination, contact injection or current arriving from another physical path.

The actual inputs use sigma_n=sigma_p=1e-15 cm^2, and the native material table prints vn=1.08e7 and vp=1.3e7 cm/s. Thus `cn=1.08e-8` and `cp=1.3e-8 cm^3/s`. The energy-integrated bulk-tail capacities of the selected configurations are `NTA*WTA*(1-exp(-Eg/WTA))`; their active Gaussian and donor capacities are zero and their interface DOS is disabled. Multiplying by the film thickness gives:

| Film | Bulk capacity, cm^-3 | Sheet-equivalent capacity, cm^-2 | Upper current scale from complete collection over the full 24 um IWO length and 1 um width | Measured plateau / bound |
|---|---:|---:|---:|---:|
| 2 nm | 2.2e19 | 4.4e12 | 1.70467044e-28 A/um | 2.70e13 |
| 6.3 nm | 1.48571429e19 | 9.36e12 | 3.62629894e-28 A/um | 4.21e14 |
| 13.2 nm | 2.5e18 | 3.3e12 | 1.27850283e-28 A/um | 5.16e16 |

The full 24 um length deliberately includes both assumed 2 um contact overlaps. Treating that entire volume as depleted and collecting every generated pair overestimates a depletion-generation current. The actual shallow acceptor tails are far from the generation-optimal energy, so the ordinary thermal contribution would be smaller. Even multiplying both capture cross sections by 1000 increases these bounds by only 1000; that sensitivity is a calculation, not an authorized parameter change or physical calibration.

The separate background `SRH` lifetime pair, taun0=taup0=1e-6 s and ETRAP=0, has `G <= ni/(2*tau)=0.0850320 cm^-3 s^-1`. Its corresponding full-length current scales are below 4.32e-33 A/um even for 13.2 nm. Shortening this lifetime to manufacture the measured plateau would not be defensible. Fitting background lifetimes and the capture rates of the same continuous defect population independently also risks counting the same recombination centers twice.

These estimates do not establish an experimental Eg, capture cross section or thermal velocity for the 2026 films. They show that enabling the missing hole equation for the **current chosen physical model** has negligible expected value as a plateau-recovery experiment. A materially different generation model would require additional evidence.

## What the supplied papers do and do not support

The target 2026 paper's Section 2.4, equations (1a)–(1f), adds an analytic Ioff component and interprets it using flat-band carriers and diffusion. Section 2.7 relates Ioff to thickness and nFB. This motivates investigating equilibrium free-carrier availability and interface-related transport. It does not supply a spatial, microscopic tunneling or leakage law for the actual HfO2/Al2O3/Pd structure. Its compact interface-diffusion component is not automatically created as a separate lateral current channel by native `INTDEFECTS`: those states contribute prescribed charge, occupancy and capture/emission within the selected transport equations. Copying the fitted Ioff into a parallel current source, forcing nFB to be a gate-independent carrier floor, or assigning mobility to trapped charge without a supported transport model would substitute the compact fit for the requested self-consistent TCAD result. The sign convention in printed equation (1f) also needs explicit treatment before any use as a current magnitude.

Fan et al., *Nanomaterials* 2021, 11, 3070, Section 3 / p.4, does use SRH, continuous oxygen-related DOS and a Schottky tunneling model in a different IWO transistor. It supports considering these mechanisms as hypotheses. Its different deposition, contacts, passivation and dielectric do not identify the 2026 Pd/IWO barrier, tunneling mass, contact field or trap population. The completed contact-emission coefficient sensitivity changes the retained 2 nm on-current by only about 0.381% and leaves all 54 zero samples unchanged; it is not evidence that contact tunneling is unnecessary, but it provides no plateau recovery. See [contact emission evidence](CONTACT_EMISSION_DEFAULTS.md).

The supplied Scientific Reports 2018 paper, DOI 10.1038/s41598-018-32233-4, reports area/process-dependent and polarity-dependent leakage in different IGZO/insulator structures. It specifically distinguishes gate currents and compares dielectric quality and geometry. Its dark-measurement instrumentation and leakage behavior are not measurements of the present IWO device. Likewise, the supplied ALD IWO paper documents measurements in dark flowing nitrogen, but that does not establish illumination, guarding, instrument floor or gate leakage for the target workbook. These sources justify retaining gate-current, environmental and measurement-path uncertainty; they do not justify borrowing a leakage amplitude.

Ga/Zn-specific defect species, light-induced metastability from the supplied NBIS paper, ferroelectric HZO switching, and sputtering-defect kinetics remain unsupported additions for this unstressed nonferroelectric transfer dataset. The actual n+Si support is screened by the modeled continuous ideal TiN gate; reintroducing its previously numerical current is not a physical plateau model.

Only Id versus Vg at one drain voltage is supplied as an electrical calibration target. The original workbook does not supply simultaneous Ig/Is, a dark/illuminated pair, temperature-dependent off-current for these exact devices, sweep timing/settling or instrument floor/guarding records. None of instrument offset, dielectric leakage, surface conduction, contact injection and microscopic localized-state conduction is uniquely selected by these curves.

## Native model audit and contingent diagnostics

The installed primary source is `C:/sedatools/lib/atlas/5.28.1.R/docs/atlas_users1.pdf`; parser names were cross-checked in the same version's `common/atlas.key`. Documentation establishes support and meaning, not successful activation in an unrun candidate.

| Native option | Supported meaning | Decision for the present three-film priority |
|---|---|---|
| `MODELS SRH`; `METHOD ... CARRIERS=2` | Background thermal SRH and both carrier continuity equations. METHOD printed p.1386 / PDF p.1392; SRH pp.228–229. | No reserve launch merely for this switch: the above thermal upper bound is negligible. Revisit only if a new mechanism requires both carriers. |
| `MODELS TRAP.TUNNEL MASS.TUNNEL=<relative mass>` | Field-enhanced trap-to-band tunneling for continuous DEFECTS, modifying capture terms; printed pp.878–879 / PDF pp.884–885. | Physically different from adding holes or ordinary SRH. The actual trap spectrum, tunneling mass and local field must be justified; do not turn it on to fit a floor. The existing mass=0.34 quantum assumption is not an experimentally validated tunneling mass. |
| `MODELS TRAP.COULOMBIC` | Coulombic/Poole-Frenkel emission enhancement, including the documented tunneling contribution; printed pp.879–880. | Requires an appropriate charge-state/potential model and field evidence. An effective acceptor-tail fit is not proof of the required Coulombic centers. Do not stack it with every tunneling option. |
| `CONTACT ... SURF.REC E.TUNNEL ME.TUNNEL=<relative mass>` | Contact thermionic emission plus WKB barrier tunneling, with contact mass distinct from the bulk `MASS.TUNNEL`; pp.158–161. | A later isolated contact hypothesis, not a currently warranted floor correction. Preserve explicit barrier and test native activation before fitting. Image-force `BARRIER` is a separate change. |
| Dielectric direct/Fowler–Nordheim/TAT models | Transport across a dielectric or quantum barrier, requiring the corresponding path and barrier/trap inputs. | The current ideal-insulator Ig=0 is a modeling assumption. No measured Ig or validated IWO/Al2O3/HfO2 offsets/masses/oxide defect distribution are available to select a leakage model. Do not copy silicon/SiO2 defaults into this bilayer. |

VD=0.7 V and L=20 um imply a modest average lateral field, but do **not** bound the vertical gate field or the local field near a contact. Thus the thermal bound cannot be used to assert all tunneling is negligible. Equally, a high local electrostatic field alone does not provide the missing tunneling parameters or prove a leakage path.

If a future supported mechanism warrants a short diagnostic, the following documented additions can expose its native quantities without changing its physical coefficients. This is a **2 nm diagnostic fragment**, not a replacement deck or a request to run. Keep the selected deck's other method settings and remove the single-carrier `ELECTRONS` flag when changing to `CARRIERS=2`.

```text
# Retain all other chosen METHOD tolerances and iteration controls.
method newton carriers=2 trap maxtrap=10 itlimit=60 climit=1e-6 cr.toler=1e-20 ir.tol=1e-20 cx.toler=1e-6

# Native structure diagnostics. Existing output selections can be retained.
output band.param con.band val.band e.field jx.electron jx.hole jy.electron jy.hole recomb u.srh

# Exposed-channel IWO box, x=2..22 um, y=-0.002..0 um.
probe name="off_holes_avg" p.conc average region=2 x.min=2 x.max=22 y.min=-0.002 y.max=0
probe name="off_srh_avg" srh average region=2 x.min=2 x.max=22 y.min=-0.002 y.max=0
probe name="off_rnet_avg" recombin average region=2 x.min=2 x.max=22 y.min=-0.002 y.max=0
probe name="off_rtrap_avg" r.trap average region=2 x.min=2 x.max=22 y.min=-0.002 y.max=0
```

Use y.min=-0.0063 or -0.0132 for the other films. Native `P.CONC` is cm^-3; volumetric recombination/generation rates are cm^-3 s^-1. Preserve their sign: positive net recombination consumes pairs; negative means generation under the documented convention. Multiplying a box average by its physical volume and q is an equivalent local generation/recombination current scale, not a terminal current fraction. Inspect the saved native spatial rates and electron/hole current densities before interpreting contact versus channel contributions.

PROBE printed pp.1536–1538 / PDF pp.1542–1544 documents P.CONC, RECOMBIN, R.TRAP and SRH. `R.TRAP` is described generically as trap recombination; its precise inclusion of continuous bulk versus interface populations must be verified from native output before claiming a decomposition. `OUTPUT U.TRAP` is not used here: the installed description refers to REACTION rates and does not establish the requested continuous-DOS separation. `PROBE GENERATION` is also not a general thermal-generation probe: its documented meaning is impact-ionization generation. OUTPUT printed pp.1508–1513 documents the requested fields. None of these diagnostic additions has been runtime-tested by this audit.

The highest-value future discriminating evidence is simultaneous signed Ig/Is/Id over the same off-state gate range, plus a controlled drain-bias or temperature comparison and instrument/background information for the same device. Available computation should first finish the actual active-region calibration and its numerical controls. Report the unresolved plateau and quantum/parameter uncertainty alongside the retained native curves; neither can be repaired by relabeling zero currents or adding unconstrained defect families.

## Evidence fingerprints

All paths below are relative to `results/local_session_20260910/runs/`. The read-only audit recomputed every execution-recorded output hash for the three earlier carrier controls and used strict native loading for the three retained snapshots.

| Run suffix | Native transfer.log SHA256 |
|---|---|
| `20260912T064920_755417_rebuild_trapfree_both_2nm` | `ce43fc9cdb7f3fa76f07fc43d3cd6416c742cbf8b3d8737dade8da454a3b8b38` |
| `20260912T065050_238465_rebuild_contact_both_2nm` | `0583a908740789c61f6585f1104d96dd0a653eebdff3d1960ff2a71e14c61796` |
| `20260912T065744_067791_rebuild_contact_electron_2nm` | `57639fbb3ca8867099c39eff8e08fa14484ab054eed0e917953663974267d1e3` |
| `20260912T074527_865393_fit_bulk_width04_2nm` | `61aa4fe3ad6aca4fe5b50ff54be2eb298a28c3a39491700e35b2f965168d3eda` |
| `20260912T091742_999942_extension02_charge_6p3nm` | `83e455aa360fce068b5459b6f410621d17ef44f40827e5391dd832538dd437e1` |
| `20260912T090754_224585_extension02_charge_13p2nm` | `14c9c6f1b6ba8007fa79c707530b6e45b91eaaf7b449a3471f998492ffedcb08` |

Original CSV SHA256 values: 2 nm `cd24cd4519d64cb010c45c9cba1e6025b2d97176a8dbdcd81b33c8a6134f708b`; 6.3 nm `1d1414542f7ee53ff34116bcbcd1c358f07b4b5ad1f5e8e302e00c62c0415042`; 13.2 nm `f6cc420b775c289b1723b46ff36c5452813757332f18d189aa540519e835f9c3`. Paper paths and original PDF hashes are retained in [the source manifest](../../results/combined_revision_20260911/source_manifest.json) and [the initial paper manifest](../../results/paper_revision_20260911/source_manifest.json).
