# Contact emission and inherited material defaults

Read-only audit, 2026-09-12. No simulator was launched, calibrated configuration changed, retained result relabelled, or current correction applied. The running 31.8 nm PRPMOB experiment is used only for its already printed input/material/model tables; this note does not claim that its transfer sweep completed.

## The Richardson constants affect the requested contact boundary

Native `deckbuild.out` from `20260912T100732_374668_extension03_prpmob_31p8nm` echoes both source/drain contacts as `workfunction=4.45 surf.rec`, prints custom IWO `An*=110` and `Ap*=30`, and shows zero explicit contact resistance. There is no `VSURFN` or `VSURFP` override. These values are inherited from the custom material's `user.default=silicon` bootstrap.

The installed ATLAS 5.28.1.R manual explicitly connects these constants to finite thermionic emission. Section 3.5.2, printed/PDF pp.158–160, equations 3-177–3-180, defines the electron/hole current boundary through surface carrier concentration minus its equilibrium contact value. With barrier lowering disabled, its electron coefficient is `q*Vsn`. The default velocities are:

```text
Vsn = ARICHN * T^2 / (q * Nc)
Vsp = ARICHP * T^2 / (q * Nv)
```

CONTACT printed p.1153/PDF p.1159, equations 22-1–22-2, repeats that `SURF.REC` uses these defaults when velocities are unspecified. Thus ARICHN is an active input to the requested finite electron-emission boundary, not merely an irrelevant printed silicon constant. ARICHP defines the analogous hole boundary; the retained electron-only solves do not establish a validated independent hole-current response.

This establishes the documented parameter dependency. It does not quantify contact limitation in the operating transistor or prove that all contact-adjacent mesh elements behave identically. In particular, the material/contact table does not directly print the resulting surface velocities. Total Id also depends on the self-consistent surface density, channel transport and electrostatics; multiplying or dividing a saved transfer curve by a Richardson ratio would be invalid.

At the saved 300 K, Nc=5e18 cm^-3 and Nv=1e19 cm^-3:

| Assumed Richardson pair, A cm^-2 K^-2 | Derived Vsn, cm/s | Derived Vsp, cm/s | Status |
|---|---:|---:|---|
| 110 / 30 | 1.235818e7 | 1.685207e6 | Documented default-velocity calculation for the present inputs |
| 41 / 30 | 4.606234e6 | 1.685207e6 | Possible isolated electron-emission sensitivity; not executed |
| 41 / 41 | 4.606234e6 | 2.303117e6 | Different-study paired assumption; not executed here |

These are unit-consistency calculations, not native measured/printed velocities or new ATLAS simulation results.

## Supported override syntax

MATERIAL printed p.1307/PDF p.1313 documents material localization, and p.1308/PDF p.1314 lists `ARICHN` and `ARICHP` in A/cm^2/K^2. The accepted custom-material localization used by the existing deck is `material=IWO`. A documented way to make the current assumptions explicit, without changing their values, is:

```text
material material=IWO arichn=110 arichp=30
```

An isolated future electron-emission hypothesis could instead use:

```text
# Hypothesis only: not applied to a retained/calibrated configuration.
material material=IWO arichn=41 arichp=30
```

Place an override after the complete custom IWO definition and before contact initialization/`SOLVE INIT`. Alternatively CONTACT supports `surf.rec vsurfn=<cm/s> vsurfp=<cm/s>`; explicitly supplied velocities replace the Richardson-derived defaults for that contact. Do not vary both representations as independent fit parameters. This is installed-manual syntax evidence, not a new runtime parser or sensitivity validation of the override.

## Consistency with the assumed electron mass

For a single isotropic parabolic band with spin degeneracy two, the standard nondegenerate DOS and ideal Richardson expressions are:

```text
Nc = 2 * (2*pi*m*k*T/h^2)^(3/2)
A* = 4*pi*q*m*k^2/h^3
```

SI-to-centimetre conversions are required: divide Nc in m^-3 by 1e6 and A* in A m^-2 K^-2 by 1e4. Using the same physical constants in both expressions gives:

- m=0.34m0: Nc(300 K)=4.974969e18 cm^-3 and A*=40.858898 A cm^-2 K^-2.
- Nc=5e18 cm^-3: inferred DOS mass=0.34113949m0 and ideal A*=40.995834 A cm^-2 K^-2.

The quantum diagnostic's assumed 0.34m0 and classical Nc seed are therefore mutually consistent under that simplified band assumption. The inherited electron Richardson value 110 is approximately 2.68 times the 41 hypothesis and is not derived from the same isotropic-mass assumption. DOS mass and emission mass need not coincide for anisotropic/multivalley bands or a nonideal interface; effective Richardson coefficients also represent interface transmission. Consequently this inconsistency is a declared physical uncertainty, not evidence that 41 is the measured correct IWO/Pd value or that the existing fit must be discarded.

The different IWO study by Fan et al., Nanomaterials 2021, 11, 3070, printed p.4, explicitly assumes An=Ap=41 with Nc=Nv=2e18 cm^-3 in its modelling discussion. That is a prior from different devices and different electronic inputs. It does not justify silently assigning the same electron and hole mass, copying all of that study's DOS/mobility/contact parameters, or claiming a measured Richardson coefficient for the 2026 film. The retained model uses different Nc/Nv and does not inherit the 2021 result as validation.

## Separate relevant and inactive defaults

| Native printed quantity / requested model | Demonstrated relevance in this run |
|---|---|
| ARICHN=110, ARICHP=30; S/D `SURF.REC` | Default finite contact-emission coefficients as documented above. An explicit velocity override would supersede their use in this boundary. |
| Bulk thermal velocities vn=1.08e7, vp=1.3e7 cm/s; continuous bulk DEFECTS enabled | Separate material velocities enter native trap capture/occupation equations. TFT printed pp.875–876/PDF pp.881–882, equations 15-12–15-15, use vn/vp with the SIG capture cross sections. These thermal velocities are not the same quantities as contact Vsn/Vsp; overriding ARICHN is not demonstrated to replace them. Their physical calibration remains separate. |
| SRH flag true; taun0=taup0=1e-6 s | Background recombination channel is requested, with explicit lifetime assumptions. This should not be fitted as the same defect population a second time alongside continuous DOS. |
| Printed silicon BGN coefficients; native BGN/UBGN variants false | Their appearance in the material table does not mean bandgap narrowing is enabled. No active BGN correction is established. |
| Printed Auger coefficients; native Auger variants false | Not an active Auger model in the displayed regional flags. |
| Printed band-tunnelling masses; native BBT/TAT flags false, no S/D `E.TUNNEL`, `H.TUNNEL`, `PARABOLIC` or `UST` request | No corresponding tunnelling current model is established by these defaults. `SURF.REC` alone enables the thermionic boundary, not every tunnelling option. |
| Printed saturation velocities; no FLDMOB request | The table alone does not demonstrate velocity-saturation transport. The new PRPMOB request is a separate surface-field mobility hypothesis; its actual behaviour requires its own native evidence. |
| Incomplete-ionization flags false | The active uniform donor input must not be reinterpreted as a separately modelled oxygen-vacancy ionization spectrum. |

The retained 2/6.3/13.2 nm inputs use the same explicit band/DOS constants and Schottky `SURF.REC` contact form without a Richardson override. Their existing fits therefore retain this contact-emission assumption. The isolated test subsequently completed below preserves those selected inputs and certificates.

## Subsequent actual 2 nm sensitivity, completed 10:38 UTC

Run `20260912T103227_998562_contact_emission01_2nm` changes only electron ARICHN to40.9958341 in the retained2nm physical command sequence. All121 native targets, signed currents, KCL, bias and probe checks pass. Native material output prints An*=41 (rounded) and Ap*=30. The precise requested electron coefficient is preserved in the actual input and echoed command.

Compared with the retained110 reference, the maximum active relative current change is0.3809675%, occurring at+3V; the endpoint decreases by0.3809675%. Maximum active log difference is0.00165768decade. Its measured active logRMSE is approximately0.0331307decade and endpoint error+0.306769%. The54 native zero currents remain. This sensitivity is small for the tested2nm curve, but does not determine the real contact emission coefficient or remove uncertainty in other thicknesses, temperatures or interface transmission.

See `results/rebuild_20260912/contact_emission01_comparison.json` and its all121-point signed CSV, plus `report_contact_emission01/`. The alternative has a separately delivered `.in` under `deliveries/rebuild_selected_20260912/diagnostics/contact_emission_2nm/`. Its underlying parameters have not received their own x/y/DOS refinements, and the existing110 numerical certificate is not silently transferred. The primary retained2nm deck remains unchanged.
